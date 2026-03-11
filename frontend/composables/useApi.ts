export function useApi() {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()
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
    } catch {
      authStore.logout()
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
      if (token) headers.Authorization = `Bearer ${token}`

      const res = await $fetch(path, {
        baseURL: base,
        ...options,
        headers: { ...headers, ...options.headers },
        body: isFormData ? options.body : (options.body ? JSON.stringify(options.body) : options.body),
      })
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
