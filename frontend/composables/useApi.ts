export function useApi() {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()
  const nuxtApp = useNuxtApp()
  const selectedLanguageCookie = useCookie<string | null>('i18n_redirect', { default: () => null })
  const rawBase = config.public.apiBase as string
  const appBase = (config.public.appBaseUrl as string) || '/'

  function normalizeBase(base: string): string {
    const appPrefix = appBase.endsWith('/') ? appBase.slice(0, -1) : appBase
    if (!appPrefix || appPrefix === '/') return base

    // If env accidentally points to /api, align it with mounted app prefix (ex: /doisense/api).
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

  const base = normalizeBase(rawBase)

  function getCookieLang(): string {
    const cookieRef = selectedLanguageCookie as unknown as { value?: string | null }
    return (cookieRef.value || '').slice(0, 2).toLowerCase()
  }

  function resolveRequestLanguage(): string {
    const cookieLang = getCookieLang()
    if (cookieLang) return cookieLang

    const i18nLocale = (nuxtApp as { $i18n?: { locale?: string | { value?: string } } }).$i18n?.locale
    const localeValue = typeof i18nLocale === 'string'
      ? i18nLocale
      : (i18nLocale as { value?: string } | undefined)?.value

    const localeLang = (localeValue || 'en').slice(0, 2).toLowerCase()
    return localeLang || 'en'
  }

  function isUnauthorized(error: unknown): boolean {
    const status = (error as { statusCode?: number; response?: { status?: number } })?.statusCode
      ?? (error as { response?: { status?: number } })?.response?.status
    return status === 401
  }

  async function getAccessToken(): Promise<string | null> {
    await authStore.hydrate()
    return authStore.accessToken
  }

  async function refreshAccessToken(): Promise<string | null> {
    await authStore.hydrate()
    const refresh = authStore.refreshToken
    if (!refresh) {
      return null
    }

    try {
      const res = await $fetch<{ access: string }>('/auth/refresh', {
        baseURL: base,
        method: 'POST',
        body: { refresh },
      })
      if (res?.access) {
        authStore.accessToken = res.access
        if (import.meta.client) {
          localStorage.setItem('doisense_access', res.access)
        }
        return res.access
      }
    } catch (error) {
      // Keep local auth state on transient errors; logout only on explicit unauthorized refresh.
      if (isUnauthorized(error)) {
        authStore.logout()
      }
    }

    return null
  }

  async function fetchApi<T>(
    path: string,
    options: Omit<RequestInit, 'body'> & { body?: unknown } = {}
  ): Promise<T> {
    const initialToken = await getAccessToken()

    const requestWithToken = async (token: string | null): Promise<T> => {
      const isFormData = options.body instanceof FormData
      const headers: Record<string, string> = {
        ...(options.headers as Record<string, string>),
      }
      if (!isFormData) {
        headers['Content-Type'] = 'application/json'
      }
      headers['X-Language'] = resolveRequestLanguage()
      if (token) headers.Authorization = `Bearer ${token}`

      const requestConfig = {
        baseURL: base,
        ...(options as Record<string, unknown>),
        headers: { ...headers, ...options.headers },
        body: isFormData
          ? (options.body as BodyInit)
          : (options.body ? (JSON.stringify(options.body) as BodyInit) : undefined),
      }

      const res = await $fetch(path, requestConfig as Parameters<typeof $fetch>[1])
      return res as T
    }

    try {
      return await requestWithToken(initialToken)
    } catch (error) {
      if (!isUnauthorized(error) || !initialToken) {
        throw error
      }

      const freshToken = await refreshAccessToken()
      if (freshToken) {
        return requestWithToken(freshToken)
      }

      // If auth refresh fails, retry once without auth for public endpoints.
      return requestWithToken(null)
    }
  }

  return { fetchApi, getAccessToken, base }
}
