// @ts-nocheck
import { defineNuxtPlugin, useCookie, useRuntimeConfig } from "nuxt/app"

export default defineNuxtPlugin((nuxtApp) => {
  const runtimeConfig = useRuntimeConfig()
  const appBase = typeof runtimeConfig.public.appBaseUrl === 'string' ? runtimeConfig.public.appBaseUrl : '/'
  const apiBaseRaw = typeof runtimeConfig.public.apiBase === 'string' ? runtimeConfig.public.apiBase : '/api'

  const selectedLanguageCookie = useCookie('i18n_redirect', {
    default: () => null,
  })
  const selectedLanguageCookieLegacy = useCookie('i18n_redirected', {
    default: () => null,
  })

  // Respect explicit user selection stored by nuxt-i18n.
  if (selectedLanguageCookie.value || selectedLanguageCookieLegacy.value) return

  const i18n = nuxtApp.$i18n
  const locales = Array.isArray(i18n?.locales) ? i18n.locales : []
  const supported = new Set(locales.map((item) => item.code))

  // Respect locale present in route path (for prefix strategies like /ro, /de).
  const router = nuxtApp.$router
  const currentPath = router?.currentRoute?.value?.path || ''
  const normalizedBase = appBase.startsWith('/') ? appBase : `/${appBase}`
  const appPrefix = normalizedBase.replace(/\/+$/, '')
  const pathWithoutBase = appPrefix && currentPath.startsWith(appPrefix)
    ? currentPath.slice(appPrefix.length)
    : currentPath
  const firstSegment = pathWithoutBase.split('/').filter(Boolean)[0] || ''
  if (supported.has(firstSegment)) {
    selectedLanguageCookie.value = firstSegment
    selectedLanguageCookieLegacy.value = firstSegment
    return
  }

  function normalizeApiBase(base) {
    const appPrefix = appBase.endsWith('/') ? appBase.slice(0, -1) : appBase
    if (!appPrefix || appPrefix === '/') return base

    if (base === '/api') return `${appPrefix}/api`

    try {
      const parsed = new URL(base)
      if (parsed.pathname === '/api') {
        parsed.pathname = `${appPrefix}/api`
        return parsed.toString().replace(/\/$/, '')
      }
    } catch {
      return base
    }

    return base
  }

  // Keep startup fast: run geolocation lookup without blocking plugin resolution.
  void (async () => {
    try {
      const payload = await $fetch('/geo/language', {
        baseURL: normalizeApiBase(apiBaseRaw),
        timeout: 1500,
      })

      const language = (payload?.language || 'en').toLowerCase()
      const target = supported.has(language) ? language : 'en'

      if (i18n.locale.value !== target) {
        await i18n.setLocale(target)
      }
      selectedLanguageCookie.value = target
      selectedLanguageCookieLegacy.value = target
    } catch {
      // Silent fallback: keep default locale if geolocation is unavailable.
    }
  })()
})
