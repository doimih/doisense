export function useApi() {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()
  const base = config.public.apiBase as string

  async function getAccessToken(): Promise<string | null> {
    await authStore.hydrate()
    return authStore.accessToken
  }

  async function fetchApi<T>(
    path: string,
    options: RequestInit & { body?: object } = {}
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
