import type { User } from '~/stores/User'

export default defineNuxtRouteMiddleware(async (to) => {
  const authStore = useAuthStore()
  authStore.hydrate()

  if (!authStore.isLoggedIn) {
    return
  }

  const { fetchApi } = useApi()
  const localePath = useLocalePath()

  const isUnauthorized = (error: unknown): boolean => {
    const status = (error as { statusCode?: number; response?: { status?: number } })?.statusCode
      ?? (error as { response?: { status?: number } })?.response?.status
    return status === 401
  }

  try {
    const refreshedUser = await fetchApi<User>('/me')
    authStore.setUser(refreshedUser)
  } catch (error) {
    if (isUnauthorized(error)) {
      authStore.logout()
      return navigateTo({
        path: localePath('/auth/login'),
        query: {
          reason: 'session_expired',
          next: to.fullPath,
        },
      })
    }
    return
  }

  const user = authStore.user
  if (!user) {
    return
  }

  if (!user.is_superuser && !user.is_staff) {
    return navigateTo(localePath('/chat'))
  }
})