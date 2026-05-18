type SessionBridgeResponse = {
  user: import('~/stores/User').User
  access: string
  refresh: string
}

export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) {
    return
  }

  const authStore = useAuthStore()
  authStore.hydrate()
  const { fetchApi } = useApi()

  if (authStore.accessToken && !authStore.user) {
    // Prefer JWT-based recovery when token pair exists.
    try {
      const me = await fetchApi<import('~/stores/User').User>('/users/me/')
      authStore.setUser(me)
    } catch {
      // Ignore and continue with bridge fallback.
    }
  }

  if (authStore.isLoggedIn) {
    return
  }

  try {
    const bridged = await fetchApi<SessionBridgeResponse>('/auth/session-bridge')
    if (bridged?.access && bridged?.refresh && bridged?.user) {
      authStore.setUser(bridged.user)
      authStore.setTokens(bridged.access)
      return
    }
  } catch {
    // Fall through to login redirect.
  }

  const localePath = useLocalePath()
  return navigateTo({
    path: localePath('/auth/login'),
    query: {
      reason: 'session_required',
      next: to.fullPath,
    },
  })
})
