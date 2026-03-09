import { defineNuxtPlugin, useCookie, useRuntimeConfig } from "nuxt/app"

export default defineNuxtPlugin(async (nuxtApp) => {
  const runtimeConfig = useRuntimeConfig()
  const appBase = (runtimeConfig.public.appBaseUrl as string) || '/'
  const apiBaseRaw = (runtimeConfig.public.apiBase as string) || '/api'

  const selectedLanguageCookie = useCookie<string | null>('i18n_redirect', {
    default: () => null,
  })

  // Respect explicit user selection stored by nuxt-i18n.
  if (selectedLanguageCookie.value) return

  function normalizeApiBase(base: string): string {
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

  try {
    const payload = await $fetch<{ country?: string; language?: string }>('/geo/language', {
      baseURL: normalizeApiBase(apiBaseRaw),
    })

    const language = (payload?.language || 'en').toLowerCase()
    const i18n = nuxtApp.$i18n as {
      locale: { value: string }
      setLocale: (locale: string) => Promise<void>
      locales: Array<{ code: string }>
    }

    const supported = new Set((i18n.locales || []).map((item) => item.code))
    const target = supported.has(language) ? language : 'en'

    if (i18n.locale.value !== target) {
      await i18n.setLocale(target)
    }
  } catch {
    // Silent fallback: keep default locale if geolocation is unavailable.
  }
})
