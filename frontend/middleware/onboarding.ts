export default defineNuxtRouteMiddleware(() => {
  const authStore = useAuthStore()
  authStore.hydrate()

  if (!authStore.isLoggedIn || authStore.user?.onboarding_completed !== false) {
    return
  }

  const localePath = useLocalePath()
  return navigateTo(localePath('/onboarding'))
})