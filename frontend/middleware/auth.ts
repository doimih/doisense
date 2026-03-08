export default defineNuxtRouteMiddleware(() => {
  const authStore = useAuthStore()
  authStore.hydrate()
  if (!authStore.isLoggedIn) {
    const localePath = useLocalePath()
    return navigateTo(localePath('/auth/login'))
  }
})
