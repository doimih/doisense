<template>
  <div class="max-w-md mx-auto py-12">
    <h1 class="text-2xl font-bold text-stone-800 mb-6">{{ $t('auth.login') }}</h1>

    <div v-if="authNotice" class="mb-4 rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ authNotice }}
    </div>

    <div class="mb-5">
      <button
        type="button"
        class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-stone-700 hover:bg-stone-50"
        :disabled="socialLoading === 'google'"
        :aria-label="socialLabels.google"
        @click="loginWithGoogle"
      >
        <span v-if="socialLoading === 'google'">...</span>
        <svg v-else viewBox="0 0 24 24" class="mx-auto h-5 w-5" aria-hidden="true">
          <path fill="#EA4335" d="M12 10.2v3.9h5.5c-.2 1.3-1.5 3.8-5.5 3.8-3.3 0-6-2.7-6-6s2.7-6 6-6c1.9 0 3.2.8 3.9 1.5l2.7-2.6C16.9 3.1 14.6 2 12 2 6.5 2 2 6.5 2 12s4.5 10 10 10c5.8 0 9.6-4.1 9.6-9.8 0-.7-.1-1.2-.2-2H12z"/>
        </svg>
      </button>
    </div>

    <form @submit.prevent="login" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-stone-700 mb-1">{{ $t('auth.email') }}</label>
        <input
          v-model="email"
          type="email"
          required
          class="w-full px-3 py-2 border border-stone-300 rounded-lg"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-stone-700 mb-1">{{ $t('auth.password') }}</label>
        <input
          v-model="password"
          type="password"
          required
          class="w-full px-3 py-2 border border-stone-300 rounded-lg"
        />
      </div>
      <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
      <button
        type="submit"
        :disabled="loading"
        class="w-full py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50"
      >
        {{ loading ? $t('common.loading') : $t('auth.login') }}
      </button>
    </form>
    <p class="mt-3 text-center text-stone-600 text-sm">
      <NuxtLink :to="localePath('/auth/recover')" class="text-amber-600 hover:underline">
        {{ $t('auth.recover') }}
      </NuxtLink>
    </p>
    <p class="mt-4 text-center text-stone-600">
      <NuxtLink :to="localePath('/auth/register')" class="text-amber-600 hover:underline">
        {{ $t('auth.noAccount') }}
      </NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { locale, t } = useI18n()
const runtimeConfig = useRuntimeConfig()
const { getPostAuthPath } = useOnboarding()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const socialLoading = ref<'' | 'google'>('')

const authNotice = computed(() => {
  const reason = String(route.query.reason || '')
  if (!reason) return ''

  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  const messages = {
    ro: 'Sesiunea ta a expirat sau necesita autentificare. Te rugam sa te conectezi din nou.',
    en: 'Your session expired or requires authentication. Please sign in again.',
    de: 'Deine Sitzung ist abgelaufen oder erfordert eine Anmeldung. Bitte melde dich erneut an.',
    fr: 'Votre session a expire ou necessite une authentification. Veuillez vous reconnecter.',
    it: 'La tua sessione e scaduta o richiede autenticazione. Effettua nuovamente il login.',
    es: 'Tu sesion expiro o requiere autenticacion. Inicia sesion nuevamente.',
    pl: 'Twoja sesja wygasla lub wymaga uwierzytelnienia. Zaloguj sie ponownie.',
  } as const

  return messages[code as keyof typeof messages] || messages.en
})

const nextAfterLogin = computed(() => {
  const raw = String(route.query.next || '').trim()
  if (!raw.startsWith('/')) return ''
  return raw
})

const socialLabels = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return {
    google: {
      ro: 'Continua cu Google',
      en: 'Continue with Google',
      de: 'Mit Google fortfahren',
      fr: 'Continuer avec Google',
      it: 'Continua con Google',
      es: 'Continuar con Google',
      pl: 'Kontynuuj z Google',
    }[code] || 'Continue with Google',
  }
})

usePublicSeo({
  title: computed(() => `${t('auth.login')} - Doisense`),
  description: computed(() => t('auth.loginSeoDescription')),
  noindex: true,
})

function preferredLanguage() {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
}

function loadScript(src: string, id: string) {
  if (!import.meta.client) return Promise.resolve()
  const existing = document.getElementById(id) as HTMLScriptElement | null
  if (existing) return Promise.resolve()
  return new Promise<void>((resolve, reject) => {
    const script = document.createElement('script')
    script.id = id
    script.src = src
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error(`Failed to load script: ${src}`))
    document.head.appendChild(script)
  })
}

async function loginWithGoogle() {
  const clientId = (runtimeConfig.public.googleClientId as string) || ''
  if (!clientId) {
    error.value = t('auth.googleNotConfigured')
    return
  }

  socialLoading.value = 'google'
  error.value = ''
  try {
    await loadScript('https://accounts.google.com/gsi/client', 'google-gsi-script-page')

    const credential = await new Promise<string>((resolve, reject) => {
      const w = window as unknown as Record<string, any>
      const google = w.google
      if (!google?.accounts?.id) {
        reject(new Error('Google SDK unavailable'))
        return
      }

      google.accounts.id.initialize({
        client_id: clientId,
        callback: (response: { credential?: string }) => {
          if (response?.credential) resolve(response.credential)
          else reject(new Error('Missing Google credential'))
        },
      })
      google.accounts.id.prompt()
    })

    await authStore.loginWithSocial('google', credential, preferredLanguage())
    await router.push(nextAfterLogin.value || getPostAuthPath())
  } catch {
    error.value = t('auth.googleLoginFailed')
  } finally {
    socialLoading.value = ''
  }
}

async function login() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    await router.push(nextAfterLogin.value || getPostAuthPath())
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail || t('auth.loginFailed')
  } finally {
    loading.value = false
  }
}
</script>
