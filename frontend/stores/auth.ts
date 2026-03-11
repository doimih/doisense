import { defineStore } from 'pinia'
import type { User } from './User'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    accessToken: null as string | null,
    refreshToken: null as string | null,
  }),
  getters: {
    isLoggedIn(state): boolean {
      return !!state.accessToken && !!state.user
    },
  },
  actions: {
    setTokens(access: string, refresh: string) {
      this.accessToken = access
      this.refreshToken = refresh
      if (import.meta.client) {
        localStorage.setItem('doisense_access', access)
        localStorage.setItem('doisense_refresh', refresh)
      }
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
      const base = config.public.apiBase as string
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
    },
    async login(email: string, password: string) {
      const config = useRuntimeConfig()
      const base = config.public.apiBase as string
      const res = await $fetch<{ user: User; access: string; refresh: string }>(`${base}/auth/login`, {
        method: 'POST',
        body: { email, password },
      })
      this.setUser(res.user)
      this.setTokens(res.access, res.refresh)
    },
    async loginWithSocial(
      provider: 'google' | 'apple',
      idToken: string,
      language: string,
      legalConsent = { acceptedTerms: false, acceptedPrivacy: false, acceptedAiUsage: false },
    ) {
      const config = useRuntimeConfig()
      const base = config.public.apiBase as string
      const res = await $fetch<{ user: User; access: string; refresh: string }>(`${base}/auth/social`, {
        method: 'POST',
        body: {
          provider,
          id_token: idToken,
          language,
          accepted_terms: legalConsent.acceptedTerms,
          accepted_privacy: legalConsent.acceptedPrivacy,
          accepted_ai_usage: legalConsent.acceptedAiUsage,
        },
      })
      this.setUser(res.user)
      this.setTokens(res.access, res.refresh)
    },
    logout() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      if (import.meta.client) {
        localStorage.removeItem('doisense_access')
        localStorage.removeItem('doisense_refresh')
        localStorage.removeItem('doisense_user')
      }
    },
    hydrate() {
      if (import.meta.client) {
        const access = localStorage.getItem('doisense_access')
        const refresh = localStorage.getItem('doisense_refresh')
        const userStr = localStorage.getItem('doisense_user')
        if (access && refresh && userStr) {
          this.accessToken = access
          this.refreshToken = refresh
          try {
            this.user = JSON.parse(userStr) as User
          } catch {
            this.logout()
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
