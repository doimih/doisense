export function useOnboarding() {
  const authStore = useAuthStore()
  const localePath = useLocalePath()

  const needsOnboarding = computed(() => authStore.user?.onboarding_completed === false)
  const onboardingPath = computed(() => localePath('/onboarding'))
  const chatPath = computed(() => localePath('/chat'))

  function getPostAuthPath() {
    return needsOnboarding.value ? onboardingPath.value : chatPath.value
  }

  return {
    needsOnboarding,
    onboardingPath,
    chatPath,
    getPostAuthPath,
  }
}