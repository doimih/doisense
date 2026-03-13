<template>
  <section class="mx-auto max-w-lg px-4 py-10">
    <div class="rounded-3xl border border-stone-200 bg-white px-6 py-8 shadow-sm md:px-9 md:py-10">
      <div class="mb-8 text-center">
        <BrandLogo class="mx-auto mb-6" size="md" centered show-tagline />
        <h1 class="text-5xl font-bold tracking-tight text-stone-900">{{ $t('auth.register') }}</h1>
        <p class="mt-4 text-lg text-stone-600">
          {{ text.hasAccountPrefix }}
          <NuxtLink :to="localePath('/auth/login')" class="font-semibold text-blue-600 hover:underline">
            {{ text.hasAccountAction }}
          </NuxtLink>
        </p>
      </div>

      <div class="space-y-3">
        <button
          type="button"
          class="flex w-full items-center justify-center gap-3 rounded-2xl border border-stone-300 bg-white px-4 py-3.5 text-xl font-semibold text-stone-700 transition hover:bg-stone-50"
          :disabled="socialLoading === 'google'"
          :aria-label="uiText.googleAria"
          @click="registerWithGoogle"
        >
          <span v-if="socialLoading === 'google'">...</span>
          <template v-else>
            <svg viewBox="0 0 24 24" class="h-7 w-7" aria-hidden="true">
              <path fill="#EA4335" d="M12 10.2v3.9h5.5c-.2 1.3-1.5 3.8-5.5 3.8-3.3 0-6-2.7-6-6s2.7-6 6-6c1.9 0 3.2.8 3.9 1.5l2.7-2.6C16.9 3.1 14.6 2 12 2 6.5 2 2 6.5 2 12s4.5 10 10 10c5.8 0 9.6-4.1 9.6-9.8 0-.7-.1-1.2-.2-2H12z"/>
            </svg>
            <span>{{ text.continueGoogle }}</span>
          </template>
        </button>

        <button
          type="button"
          class="flex w-full items-center justify-center gap-3 rounded-2xl border border-stone-300 bg-white px-4 py-3.5 text-xl font-semibold text-stone-700 transition hover:bg-stone-50"
          :disabled="socialLoading === 'apple'"
          :aria-label="uiText.appleAria"
          @click="registerWithApple"
        >
          <span v-if="socialLoading === 'apple'">...</span>
          <template v-else>
            <svg viewBox="0 0 24 24" class="h-7 w-7 fill-current" aria-hidden="true">
              <path d="M16.9 12.6c0-2.3 1.9-3.4 2-3.5-1.1-1.6-2.8-1.8-3.4-1.8-1.4-.1-2.8.8-3.5.8-.7 0-1.8-.8-3-.8-1.5 0-2.9.9-3.7 2.2-1.6 2.8-.4 6.9 1.1 9.1.8 1.1 1.6 2.3 2.8 2.3 1.1 0 1.6-.7 3-.7s1.8.7 3 .7c1.2 0 2-1.1 2.7-2.2.9-1.3 1.2-2.6 1.2-2.7 0 0-2.3-.9-2.3-3.4zM14.6 5.8c.6-.8 1-1.9.9-3-.9.1-2 .6-2.6 1.4-.6.7-1.1 1.9-1 3 .9.1 2-.5 2.7-1.4z"/>
            </svg>
            <span>{{ text.continueApple }}</span>
          </template>
        </button>
      </div>

      <div class="my-7 flex items-center gap-4">
        <span class="h-px flex-1 bg-stone-300" />
        <span class="text-2xl font-semibold text-stone-700">{{ uiText.orSeparator }}</span>
        <span class="h-px flex-1 bg-stone-300" />
      </div>

      <form @submit.prevent="register" class="space-y-4">

        <input
          v-model="email"
          type="email"
          required
          :placeholder="$t('auth.email')"
          class="w-full rounded-2xl border border-stone-300 px-4 py-3 text-base text-stone-900 placeholder:text-stone-400 focus:border-stone-500 focus:outline-none"
        />

        <input
          v-model="password"
          type="password"
          required
          minlength="8"
          :placeholder="$t('auth.password')"
          class="w-full rounded-2xl border border-stone-300 px-4 py-3 text-base text-stone-900 placeholder:text-stone-400 focus:border-stone-500 focus:outline-none"
        />

        <select
          v-model="language"
          class="w-full rounded-2xl border border-stone-300 px-4 py-3 text-base text-stone-900 focus:border-stone-500 focus:outline-none"
        >
          <option value="ro">Română</option>
          <option value="en">English</option>
          <option value="de">Deutsch</option>
          <option value="fr">Français</option>
          <option value="it">Italiano</option>
          <option value="es">Español</option>
          <option value="pl">Polski</option>
        </select>

        <label class="block rounded-xl border border-stone-200 bg-stone-50 px-4 py-3 text-sm text-stone-700">
          <input v-model="acceptedLegal" type="checkbox" class="mr-2 align-middle" />
          <span class="align-middle">
            {{ legalText.prefix }}
            <NuxtLink :to="localePath('/legal/terms')" class="font-medium text-blue-600 hover:underline">{{ legalText.terms }}</NuxtLink>
            {{ legalText.and }}
            <NuxtLink :to="localePath('/legal/privacy')" class="font-medium text-blue-600 hover:underline">{{ legalText.privacy }}</NuxtLink>
            {{ legalText.and }}
            <NuxtLink :to="localePath('/legal/ai-consent')" class="font-medium text-blue-600 hover:underline">{{ legalText.ai }}</NuxtLink>
            {{ legalText.suffix }}
          </span>
        </label>

        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
        <p v-if="success" class="text-sm text-emerald-700">{{ success }}</p>

        <button
          type="submit"
          :disabled="loading || !!success"
          class="w-full rounded-2xl bg-black py-4 text-2xl font-semibold text-white transition hover:bg-stone-900 disabled:opacity-50"
        >
          {{ loading ? $t('common.loading') : text.continueLabel }}
        </button>
      </form>
    </div>
  </section>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const authStore = useAuthStore()
const { locale, t } = useI18n()
const runtimeConfig = useRuntimeConfig()
const router = useRouter()
const { getPostAuthPath } = useOnboarding()

const email = ref('')
const password = ref('')
const language = ref('en')
const acceptedLegal = ref(false)
const error = ref('')
const loading = ref(false)
const success = ref('')
const socialLoading = ref<'' | 'google' | 'apple'>('')

const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

const text = computed(() => {
  return {
    ro: {
      hasAccountPrefix: 'Ai deja cont?',
      hasAccountAction: 'Autentifica-te',
      continueGoogle: 'Continua cu Google',
      continueApple: 'Continua cu Apple',
      continueLabel: 'Continua',
    },
    en: {
      hasAccountPrefix: 'Already have an account?',
      hasAccountAction: 'Sign in',
      continueGoogle: 'Continue with Google',
      continueApple: 'Continue with Apple',
      continueLabel: 'Continue',
    },
    de: {
      hasAccountPrefix: 'Hast du bereits ein Konto?',
      hasAccountAction: 'Anmelden',
      continueGoogle: 'Mit Google fortfahren',
      continueApple: 'Mit Apple fortfahren',
      continueLabel: 'Fortfahren',
    },
    fr: {
      hasAccountPrefix: 'Vous avez deja un compte ?',
      hasAccountAction: 'Se connecter',
      continueGoogle: 'Continuer avec Google',
      continueApple: 'Continuer avec Apple',
      continueLabel: 'Continuer',
    },
    it: {
      hasAccountPrefix: 'Hai gia un account?',
      hasAccountAction: 'Accedi',
      continueGoogle: 'Continua con Google',
      continueApple: 'Continua con Apple',
      continueLabel: 'Continua',
    },
    es: {
      hasAccountPrefix: 'Ya tienes una cuenta?',
      hasAccountAction: 'Iniciar sesion',
      continueGoogle: 'Continuar con Google',
      continueApple: 'Continuar con Apple',
      continueLabel: 'Continuar',
    },
    pl: {
      hasAccountPrefix: 'Masz juz konto?',
      hasAccountAction: 'Zaloguj sie',
      continueGoogle: 'Kontynuuj z Google',
      continueApple: 'Kontynuuj z Apple',
      continueLabel: 'Kontynuuj',
    },
  }[localeCode.value] || {
    hasAccountPrefix: 'Already have an account?',
    hasAccountAction: 'Sign in',
    continueGoogle: 'Continue with Google',
    continueApple: 'Continue with Apple',
    continueLabel: 'Continue',
  }
})

usePublicSeo({
  title: computed(() => `${t('auth.register')} - Doisense`),
  description: computed(() => t('auth.registerSeoDescription')),
  noindex: true,
})

const legalText = computed(() => ({
  prefix: t('auth.legalAcceptPrefix'),
  terms: t('auth.termsAndConditions'),
  and: t('auth.and'),
  privacy: t('auth.privacyPolicy'),
  ai: {
    ro: 'Acordul de utilizare AI',
    en: 'AI Usage Agreement',
    de: 'Vereinbarung zur KI-Nutzung',
    fr: 'Accord d\'utilisation de l\'IA',
    it: 'Accordo di utilizzo dell\'IA',
    es: 'Acuerdo de uso de la IA',
    pl: 'Umowa korzystania z AI',
  }[localeCode.value] || 'AI Usage Agreement',
  suffix: '.',
  validation: {
    ro: 'Trebuie sa accepti Termenii, Politica de confidentialitate si Acordul de utilizare AI.',
    en: 'You must accept the Terms, Privacy Policy, and AI Usage Agreement.',
    de: 'Du musst den Bedingungen, der Datenschutzrichtlinie und der KI-Nutzungsvereinbarung zustimmen.',
    fr: 'Vous devez accepter les Conditions, la Politique de confidentialite et l\'accord d\'utilisation de l\'IA.',
    it: 'Devi accettare i Termini, l\'Informativa sulla privacy e l\'accordo di utilizzo AI.',
    es: 'Debes aceptar los Terminos, la Politica de privacidad y el Acuerdo de uso de IA.',
    pl: 'Musisz zaakceptowac Regulamin, Polityke prywatnosci i Umowe korzystania z AI.',
  }[localeCode.value] || 'You must accept the Terms, Privacy Policy, and AI Usage Agreement.',
}))

const uiText = computed(() => {
  return {
    ro: { googleAria: 'Continua cu Google', appleAria: 'Continua cu Apple', orSeparator: 'SAU' },
    en: { googleAria: 'Continue with Google', appleAria: 'Continue with Apple', orSeparator: 'OR' },
    de: { googleAria: 'Mit Google fortfahren', appleAria: 'Mit Apple fortfahren', orSeparator: 'ODER' },
    fr: { googleAria: 'Continuer avec Google', appleAria: 'Continuer avec Apple', orSeparator: 'OU' },
    it: { googleAria: 'Continua con Google', appleAria: 'Continua con Apple', orSeparator: 'OPPURE' },
    es: { googleAria: 'Continuar con Google', appleAria: 'Continuar con Apple', orSeparator: 'O' },
    pl: { googleAria: 'Kontynuuj z Google', appleAria: 'Kontynuuj z Apple', orSeparator: 'LUB' },
  }[localeCode.value] || { googleAria: 'Continue with Google', appleAria: 'Continue with Apple', orSeparator: 'OR' }
})

async function register() {
  error.value = ''
  if (!acceptedLegal.value) {
    error.value = legalText.value.validation
    return
  }
  loading.value = true
  try {
    const res = await authStore.register(
      email.value,
      password.value,
      language.value,
      '',
      '',
      { acceptedTerms: true, acceptedPrivacy: true, acceptedAiUsage: true },
    )
    success.value = res.detail || t('auth.registerSuccess')
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string }; message?: string })?.data?.detail
      || (e as { message?: string })?.message
      || t('auth.registerFailed')
  } finally {
    loading.value = false
  }
}

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

async function registerWithGoogle() {
  const clientId = (runtimeConfig.public.googleClientId as string) || ''
  if (!clientId) {
    error.value = t('auth.googleNotConfigured')
    return
  }

  socialLoading.value = 'google'
  error.value = ''
  try {
    await loadScript('https://accounts.google.com/gsi/client', 'google-gsi-script-page-register')

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

    if (!acceptedLegal.value) {
      error.value = legalText.value.validation
      return
    }

    await authStore.loginWithSocial('google', credential, preferredLanguage(), {
      acceptedTerms: true,
      acceptedPrivacy: true,
      acceptedAiUsage: true,
    })
    await router.push(getPostAuthPath())
  } catch {
    error.value = t('auth.googleLoginFailed')
  } finally {
    socialLoading.value = ''
  }
}

async function registerWithApple() {
  const clientId = (runtimeConfig.public.appleClientId as string) || ''
  if (!clientId) {
    error.value = t('auth.appleNotConfigured')
    return
  }

  socialLoading.value = 'apple'
  error.value = ''
  try {
    await loadScript(
      'https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/1/en_US/appleid.auth.js',
      'appleid-auth-script-page-register',
    )

    const w = window as unknown as Record<string, any>
    const AppleID = w.AppleID
    if (!AppleID?.auth) throw new Error('Apple SDK unavailable')

    const redirectURI = (runtimeConfig.public.appleRedirectUri as string) || window.location.href
    AppleID.auth.init({
      clientId,
      scope: 'name email',
      redirectURI,
      usePopup: true,
    })

    const response = await AppleID.auth.signIn()
    const credential = response?.authorization?.id_token as string | undefined
    if (!credential) throw new Error('Missing Apple credential')

    if (!acceptedLegal.value) {
      error.value = legalText.value.validation
      return
    }

    await authStore.loginWithSocial('apple', credential, preferredLanguage(), {
      acceptedTerms: true,
      acceptedPrivacy: true,
      acceptedAiUsage: true,
    })
    await router.push(getPostAuthPath())
  } catch {
    error.value = t('auth.appleLoginFailed')
  } finally {
    socialLoading.value = ''
  }
}
</script>
