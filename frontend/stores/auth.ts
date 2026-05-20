import { defineStore } from 'pinia'
import type { User } from './User'

function normalizeApiBase(base: string): string {
  const cleaned = (base || '').trim().replace(/^['\"]+|['\"]+$/g, '')
  if (!cleaned) return '/api'
  return cleaned.replace(/\/+$/, '')
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    accessToken: null as string | null,
  }),
  getters: {
    isLoggedIn(state): boolean {
      return !!state.accessToken && !!state.user
    },
  },
  actions: {
    async trackFrontendEvent(eventName: string, properties: Record<string, unknown> = {}) {
      try {
        const config = useRuntimeConfig()
        const base = normalizeApiBase(config.public.apiBase as string)
        await $fetch(`${base}/analytics/track`, {
          method: 'POST',
          body: {
            event_name: eventName,
            source: 'frontend',
            properties,
          },
        })
      } catch {
        // Analytics tracking is best-effort and should not block auth UX.
      }
    },

    setTokens(access: string) {
      this.accessToken = access
    },
    setUser(user: User) {
      this.user = user
      if (import.meta.client) {
        localStorage.setItem('doisense_user', JSON.stringify(user))
      }
    },
    async register(
      email: string,
      password: string,
      language: string,
      firstName = '',
      lastName = '',
      legalConsent = { acceptedTerms: true, acceptedPrivacy: true, acceptedAiUsage: true },
    ) {
      const config = useRuntimeConfig()
      const base = normalizeApiBase(config.public.apiBase as string)
      return $fetch<{ detail: string }>(`${base}/auth/register`, {
        method: 'POST',
        body: {
          email,
          password,
          language,
          first_name: firstName,
          last_name: lastName,
          accepted_terms: legalConsent.acceptedTerms,
          accepted_privacy: legalConsent.acceptedPrivacy,
          accepted_ai_usage: legalConsent.acceptedAiUsage,
        },
      })
        .then(async (res) => {
          await this.trackFrontendEvent('user_registered', { auth_method: 'email' })
          return res
        })
    },
    async login(email: string, password: string) {
      const config = useRuntimeConfig()
      const base = normalizeApiBase(config.public.apiBase as string)
      const res = await $fetch<{ user: User; access: string }>(`${base}/auth/login`, {
        method: 'POST',
        body: { email, password },
        credentials: 'include',
      })
      this.setUser(res.user)
      this.setTokens(res.access)
      await this.trackFrontendEvent('user_activated', { auth_method: 'email' })
    },
    async loginWithSocial(
      provider: 'google',
      idToken: string,
      language: string,
      legalConsent = { acceptedTerms: false, acceptedPrivacy: false, acceptedAiUsage: false },
    ) {
      const config = useRuntimeConfig()
      const base = normalizeApiBase(config.public.apiBase as string)
      const res = await $fetch<{ user: User; access: string }>(`${base}/auth/social`, {
        method: 'POST',
        body: {
          provider,
          id_token: idToken,
          language,
          accepted_terms: legalConsent.acceptedTerms,
          accepted_privacy: legalConsent.acceptedPrivacy,
          accepted_ai_usage: legalConsent.acceptedAiUsage,
        },
        credentials: 'include',
      })
      this.setUser(res.user)
      this.setTokens(res.access)
      await this.trackFrontendEvent('user_activated', { auth_method: provider })
    },
    async logout() {
      try {
        const config = useRuntimeConfig()
        const base = normalizeApiBase(config.public.apiBase as string)
        await $fetch(`${base}/auth/logout`, { method: 'POST', credentials: 'include' })
      } catch {
        // Local cleanup should still run even if logout API is unavailable.
      }

      this.user = null
      this.accessToken = null
      if (import.meta.client) {
        localStorage.removeItem('doisense_user')
      }
    },
    hydrate() {
      if (import.meta.client) {
        const userStr = localStorage.getItem('doisense_user')
        if (userStr) {
          try {
            this.user = JSON.parse(userStr) as User
          } catch {
            this.user = null
            localStorage.removeItem('doisense_user')
          }
        }
      }
    },
    async getAccessToken(): Promise<string | null> {
      if (this.accessToken) return this.accessToken
      this.hydrate()
      return this.accessToken
    },
  },
})
