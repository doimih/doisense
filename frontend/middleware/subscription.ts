import type { User } from '~/stores/User'

export default defineNuxtRouteMiddleware(async () => {
  const authStore = useAuthStore()
  authStore.hydrate()

  if (!authStore.isLoggedIn) {
    return
  }

  const { fetchApi } = useApi()
  const localePath = useLocalePath()

  try {
    const refreshedUser = await fetchApi<User>('/me')
    authStore.setUser(refreshedUser)
  } catch {
    return
  }

  if (authStore.user?.membership_tier === 'free') {
    return navigateTo(localePath('/trial-expired'))
  }
})