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

  async function getAccessToken(): Promise<string | null> {
    await authStore.hydrate()
    return authStore.accessToken
  }

  async function fetchApi<T>(
    path: string,
    options: Omit<RequestInit, 'body'> & { body?: unknown } = {}
  ): Promise<T> {
    const token = await getAccessToken()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }
    if (token) headers['Authorization'] = `Bearer ${token}`

    const res = await $fetch(path, {
      baseURL: base,
      ...options,
      headers: { ...headers, ...options.headers },
      body: options.body ? JSON.stringify(options.body) : options.body,
    })
    return res as T
  }

  return { fetchApi, getAccessToken, base }
}
