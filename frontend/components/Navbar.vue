<template>
  <nav ref="navRef" :class="navClass">
    <div class="container mx-auto flex items-center justify-between gap-4">
      <NuxtLink :to="localePath('/')" :class="brandClass">Doisense</NuxtLink>

      <button
        type="button"
        :class="mobileToggleClass"
        @click="mobileOpen = !mobileOpen"
        aria-label="Toggle navigation"
      >
        <span v-if="!mobileOpen">☰</span>
        <span v-else>✕</span>
      </button>

      <div class="hidden lg:flex items-center gap-3 flex-wrap justify-end text-sm">
        <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/features')" :class="navLinkClass">
          {{ $t('nav.features') }}
        </NuxtLink>
        <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/pricing')" :class="navLinkClass">
          {{ $t('nav.pricing') }}
        </NuxtLink>
        <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/about')" :class="navLinkClass">
          {{ $t('nav.about') }}
        </NuxtLink>
        <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/contact')" :class="navLinkClass">
          {{ $t('nav.contact') }}
        </NuxtLink>
        <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/faq')" :class="navLinkClass">
          FAQ
        </NuxtLink>

        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/chat')" :class="navLinkClass">
          {{ $t('nav.chat') }}
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/journal')" :class="navLinkClass">
          {{ $t('nav.journal') }}
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/programs')" :class="navLinkClass">
          {{ $t('nav.programs') }}
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/profile')" :class="navLinkClass">
          {{ $t('nav.profile') }}
        </NuxtLink>
        <a v-if="authStore.isLoggedIn && authStore.user?.is_superuser" href="/doisense/ro/admin/" :class="navLinkClass">
          {{ $t('nav.admin') }}
        </a>
        <button
          v-if="!authStore.isLoggedIn"
          type="button"
          :class="accountButtonClass"
          @click="openAuthModal"
          aria-label="Open authentication"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-5 w-5">
            <path d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5Zm0 2c-4.418 0-8 2.239-8 5v1h16v-1c0-2.761-3.582-5-8-5Z" />
          </svg>
        </button>
        <div class="relative">
          <button
            type="button"
            :class="languageButtonClass"
            aria-label="Open language menu"
            @click="desktopLanguageMenuOpen = !desktopLanguageMenuOpen"
          >
            {{ activeLanguageLabel }}
            <span class="text-[10px]">▾</span>
          </button>
          <div
            v-if="desktopLanguageMenuOpen"
            class="absolute right-0 z-20 mt-2 w-36 rounded-lg border border-stone-200 bg-white p-1 shadow-lg"
          >
            <button
              v-for="lang in languageOptions"
              :key="lang.code"
              type="button"
              class="flex w-full items-center justify-between rounded-md px-2 py-1.5 text-left text-xs text-stone-700 hover:bg-stone-100"
              @click="changeLanguage(lang.code)"
            >
              <span>{{ lang.label }}</span>
              <span v-if="locale.startsWith(lang.code)">✓</span>
            </button>
          </div>
        </div>
        <button
          v-if="authStore.isLoggedIn"
          type="button"
          :class="navLinkClass"
          @click="logout"
        >
          {{ $t('auth.logout') }}
        </button>
      </div>
    </div>

    <div v-if="mobileOpen" class="container mx-auto mt-3 space-y-2 border-t border-stone-200 pt-3 text-sm lg:hidden">
      <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/features')" class="block text-stone-700" @click="mobileOpen = false">{{ $t('nav.features') }}</NuxtLink>
      <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/pricing')" class="block text-stone-700" @click="mobileOpen = false">{{ $t('nav.pricing') }}</NuxtLink>
      <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/about')" class="block text-stone-700" @click="mobileOpen = false">{{ $t('nav.about') }}</NuxtLink>
      <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/contact')" class="block text-stone-700" @click="mobileOpen = false">{{ $t('nav.contact') }}</NuxtLink>
      <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/faq')" class="block text-stone-700" @click="mobileOpen = false">FAQ</NuxtLink>
      <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/chat')" class="block text-stone-700" @click="mobileOpen = false">{{ $t('nav.chat') }}</NuxtLink>
      <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/journal')" class="block text-stone-700" @click="mobileOpen = false">{{ $t('nav.journal') }}</NuxtLink>
      <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/programs')" class="block text-stone-700" @click="mobileOpen = false">{{ $t('nav.programs') }}</NuxtLink>
      <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/profile')" class="block text-stone-700" @click="mobileOpen = false">{{ $t('nav.profile') }}</NuxtLink>
      <div class="pt-2">
        <p class="mb-1 text-xs text-stone-500">{{ $t('auth.language') }}</p>
        <div class="relative inline-block">
          <button
            type="button"
            class="inline-flex items-center gap-2 rounded-full border border-stone-300 px-3 py-1.5 text-xs font-medium text-stone-700"
            aria-label="Open language menu"
            @click="mobileLanguageMenuOpen = !mobileLanguageMenuOpen"
          >
            {{ activeLanguageLabel }}
            <span class="text-[10px]">▾</span>
          </button>
          <div
            v-if="mobileLanguageMenuOpen"
            class="absolute left-0 z-20 mt-2 w-40 rounded-lg border border-stone-200 bg-white p-1 shadow-lg"
          >
            <button
              v-for="lang in languageOptions"
              :key="`mobile-lang-${lang.code}`"
              type="button"
              class="flex w-full items-center justify-between rounded-md px-2 py-1.5 text-left text-xs text-stone-700 hover:bg-stone-100"
              @click="changeLanguage(lang.code)"
            >
              <span>{{ lang.label }}</span>
              <span v-if="locale.startsWith(lang.code)">✓</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </nav>

  <Teleport to="body">
    <div
      v-if="showAuthModal"
      class="fixed inset-0 z-[100] overflow-y-auto bg-stone-900/50"
      @click.self="closeAuthModal"
      @keydown.esc="closeAuthModal"
    >
      <div class="flex min-h-full items-center justify-center px-4 py-6">
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl" @click.stop>
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-stone-900">{{ $t('auth.accountTitle') }}</h2>
        <button type="button" class="text-stone-500 hover:text-stone-800" @click="closeAuthModal" aria-label="Close">
          ✕
        </button>
      </div>

      <div class="mb-4 grid grid-cols-2 rounded-lg bg-stone-100 p-1">
        <button
          type="button"
          class="rounded-md px-3 py-2 text-sm"
          :class="authTab === 'login' ? 'bg-white font-medium text-stone-900 shadow-sm' : 'text-stone-600'"
          @click="switchTab('login')"
        >
          {{ $t('auth.login') }}
        </button>
        <button
          type="button"
          class="rounded-md px-3 py-2 text-sm"
          :class="authTab === 'register' ? 'bg-white font-medium text-stone-900 shadow-sm' : 'text-stone-600'"
          @click="switchTab('register')"
        >
          {{ $t('auth.register') }}
        </button>
      </div>

      <div class="mb-4 grid grid-cols-2 gap-2">
        <button
          type="button"
          class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-medium text-stone-700 hover:bg-stone-50 disabled:opacity-50"
          :disabled="authLoading || socialLoading === 'apple'"
          @click="loginWithGoogle"
          aria-label="Continue with Google"
        >
          <span v-if="socialLoading === 'google'">...</span>
          <svg v-else viewBox="0 0 24 24" class="mx-auto h-5 w-5" aria-hidden="true">
            <path fill="#EA4335" d="M12 10.2v3.9h5.5c-.2 1.3-1.5 3.8-5.5 3.8-3.3 0-6-2.7-6-6s2.7-6 6-6c1.9 0 3.2.8 3.9 1.5l2.7-2.6C16.9 3.1 14.6 2 12 2 6.5 2 2 6.5 2 12s4.5 10 10 10c5.8 0 9.6-4.1 9.6-9.8 0-.7-.1-1.2-.2-2H12z"/>
          </svg>
        </button>
        <button
          type="button"
          class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-medium text-stone-700 hover:bg-stone-50 disabled:opacity-50"
          :disabled="authLoading || socialLoading === 'google'"
          @click="loginWithApple"
          aria-label="Continue with Apple"
        >
          <span v-if="socialLoading === 'apple'">...</span>
          <svg v-else viewBox="0 0 24 24" class="mx-auto h-5 w-5 fill-current" aria-hidden="true">
            <path d="M16.9 12.6c0-2.3 1.9-3.4 2-3.5-1.1-1.6-2.8-1.8-3.4-1.8-1.4-.1-2.8.8-3.5.8-.7 0-1.8-.8-3-.8-1.5 0-2.9.9-3.7 2.2-1.6 2.8-.4 6.9 1.1 9.1.8 1.1 1.6 2.3 2.8 2.3 1.1 0 1.6-.7 3-.7s1.8.7 3 .7c1.2 0 2-1.1 2.7-2.2.9-1.3 1.2-2.6 1.2-2.7 0 0-2.3-.9-2.3-3.4zM14.6 5.8c.6-.8 1-1.9.9-3-.9.1-2 .6-2.6 1.4-.6.7-1.1 1.9-1 3 .9.1 2-.5 2.7-1.4z"/>
          </svg>
        </button>
      </div>

      <form v-if="authTab === 'login'" class="space-y-3" @submit.prevent="submitLogin">
        <div>
          <label class="mb-1 block text-sm font-medium text-stone-700">{{ $t('auth.email') }}</label>
          <input v-model="loginEmail" type="email" required class="w-full rounded-lg border border-stone-300 px-3 py-2" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-stone-700">{{ $t('auth.password') }}</label>
          <input v-model="loginPassword" type="password" required class="w-full rounded-lg border border-stone-300 px-3 py-2" />
        </div>
        <div class="text-right">
          <button
            type="button"
            class="text-sm text-amber-700 hover:underline"
            :disabled="authLoading"
            @click="goToRecover"
          >
            {{ $t('auth.recover') }}
          </button>
        </div>
        <p v-if="authError" class="text-sm text-red-600">{{ authError }}</p>
        <button
          type="submit"
          :disabled="authLoading"
          class="w-full rounded-lg bg-amber-600 py-2 text-white hover:bg-amber-700 disabled:opacity-50"
        >
          {{ authLoading ? $t('common.loading') : $t('auth.login') }}
        </button>
      </form>

      <form v-else class="space-y-3" @submit.prevent="submitRegister">
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-sm font-medium text-stone-700">{{ $t('auth.firstName') }}</label>
            <input v-model="registerFirstName" type="text" class="w-full rounded-lg border border-stone-300 px-3 py-2" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-stone-700">{{ $t('auth.lastName') }}</label>
            <input v-model="registerLastName" type="text" class="w-full rounded-lg border border-stone-300 px-3 py-2" />
          </div>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-stone-700">{{ $t('auth.email') }}</label>
          <input v-model="registerEmail" type="email" required class="w-full rounded-lg border border-stone-300 px-3 py-2" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-stone-700">{{ $t('auth.password') }}</label>
          <input v-model="registerPassword" type="password" minlength="8" required class="w-full rounded-lg border border-stone-300 px-3 py-2" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-stone-700">{{ $t('auth.language') }}</label>
          <select v-model="registerLanguage" class="w-full rounded-lg border border-stone-300 px-3 py-2">
            <option value="ro">Romana</option>
            <option value="en">English</option>
            <option value="de">Deutsch</option>
            <option value="fr">Francais</option>
            <option value="it">Italiano</option>
            <option value="es">Espanol</option>
            <option value="pl">Polski</option>
          </select>
        </div>
        <p v-if="authError" class="text-sm text-red-600">{{ authError }}</p>
        <p v-if="authSuccess" class="text-sm text-emerald-700">{{ authSuccess }}</p>
        <button
          type="submit"
          :disabled="authLoading || !!authSuccess"
          class="w-full rounded-lg bg-amber-600 py-2 text-white hover:bg-amber-700 disabled:opacity-50"
        >
          {{ authLoading ? $t('common.loading') : $t('auth.register') }}
        </button>
      </form>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const switchLocalePath = useSwitchLocalePath()
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { locale, setLocale, t } = useI18n()
const runtimeConfig = useRuntimeConfig()
const selectedLanguageCookie = useCookie<string | null>('i18n_redirect', { default: () => null })
const selectedLanguageCookieLegacy = useCookie<string | null>('i18n_redirected', { default: () => null })

const mobileOpen = ref(false)
const hasScrolled = ref(false)
const isOverDarkZone = ref(false)
const navRef = ref<HTMLElement | null>(null)
const navHidden = ref(false)
const lastScrollY = ref(0)
const desktopLanguageMenuOpen = ref(false)
const mobileLanguageMenuOpen = ref(false)
const languageOptions = [
  { code: 'ro', label: 'Romana' },
  { code: 'en', label: 'English' },
  { code: 'de', label: 'Deutsch' },
  { code: 'fr', label: 'Francais' },
  { code: 'it', label: 'Italiano' },
  { code: 'es', label: 'Espanol' },
  { code: 'pl', label: 'Polski' },
]
const activeLanguageLabel = computed(() => {
  const current = languageOptions.find((lang) => locale.value.startsWith(lang.code))
  return current?.label ?? 'en'
})

const navClass = computed(() => {
  const scrolled = hasScrolled.value
  const darkZone = isOverDarkZone.value
  const hidden = navHidden.value && !mobileOpen.value
  return [
    'sticky top-0 z-40 px-4 py-3 transition-all duration-300',
    scrolled && darkZone
      ? 'border-b border-white/25 bg-stone-900/55 text-white shadow-[0_8px_30px_-20px_rgba(2,6,23,0.7)] backdrop-blur-xl'
      : scrolled
      ? 'border-b border-white/35 bg-white/72 shadow-[0_8px_30px_-20px_rgba(15,23,42,0.45)] backdrop-blur-xl'
      : 'border-b border-stone-200 bg-white/98',
    hidden ? '-translate-y-full' : 'translate-y-0',
  ]
})

const brandClass = computed(() => [
  'text-xl font-semibold transition-colors',
  isOverDarkZone.value ? 'text-white' : 'text-stone-800',
])

const navLinkClass = computed(() =>
  isOverDarkZone.value ? 'text-white/85 hover:text-white transition-colors' : 'text-stone-600 hover:text-stone-900 transition-colors',
)

const mobileToggleClass = computed(() => [
  'lg:hidden inline-flex h-9 w-9 items-center justify-center rounded-md border transition-colors',
  isOverDarkZone.value ? 'border-white/40 text-white' : 'border-stone-300 text-stone-700',
])

const accountButtonClass = computed(() => [
  'inline-flex h-9 w-9 items-center justify-center rounded-full border transition-colors',
  isOverDarkZone.value ? 'border-white/40 text-white hover:border-white/70 hover:text-white' : 'border-stone-300 text-stone-600 hover:border-stone-400 hover:text-stone-900',
])

const languageButtonClass = computed(() => [
  'inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors',
  isOverDarkZone.value ? 'border-white/40 text-white hover:border-white/70' : 'border-stone-300 text-stone-700 hover:border-stone-400',
])

const showAuthModal = ref(false)
const authTab = ref<'login' | 'register'>('login')
const authLoading = ref(false)
const socialLoading = ref<'' | 'google' | 'apple'>('')
const authError = ref('')
const authSuccess = ref('')

const loginEmail = ref('')
const loginPassword = ref('')

const registerEmail = ref('')
const registerPassword = ref('')
const registerLanguage = ref('en')
const registerFirstName = ref('')
const registerLastName = ref('')

function openAuthModal() {
  showAuthModal.value = true
  authError.value = ''
  authSuccess.value = ''
  registerLanguage.value = preferredLanguage()
}

function closeAuthModal() {
  showAuthModal.value = false
  authError.value = ''
  authSuccess.value = ''
}

function switchTab(tab: 'login' | 'register') {
  authTab.value = tab
  authError.value = ''
  authSuccess.value = ''
}

async function goToRecover() {
  closeAuthModal()
  await router.push(localePath('/auth/recover'))
}

function preferredLanguage() {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return languageOptions.some((lang) => lang.code === code) ? code : 'en'
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
    authError.value = t('auth.googleNotConfigured')
    return
  }

  socialLoading.value = 'google'
  authError.value = ''
  try {
    await loadScript('https://accounts.google.com/gsi/client', 'google-gsi-script')

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
    closeAuthModal()
    await router.push(localePath('/chat'))
  } catch {
    authError.value = t('auth.googleLoginFailed')
  } finally {
    socialLoading.value = ''
  }
}

async function loginWithApple() {
  const clientId = (runtimeConfig.public.appleClientId as string) || ''
  if (!clientId) {
    authError.value = t('auth.appleNotConfigured')
    return
  }

  socialLoading.value = 'apple'
  authError.value = ''
  try {
    await loadScript(
      'https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/1/en_US/appleid.auth.js',
      'appleid-auth-script',
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

    await authStore.loginWithSocial('apple', credential, preferredLanguage())
    closeAuthModal()
    await router.push(localePath('/chat'))
  } catch {
    authError.value = t('auth.appleLoginFailed')
  } finally {
    socialLoading.value = ''
  }
}

async function submitLogin() {
  authError.value = ''
  authSuccess.value = ''
  authLoading.value = true
  try {
    await authStore.login(loginEmail.value, loginPassword.value)
    closeAuthModal()
    await router.push(localePath('/chat'))
  } catch (e: unknown) {
    authError.value = (e as { data?: { detail?: string } })?.data?.detail || t('auth.loginFailed')
  } finally {
    authLoading.value = false
  }
}

async function submitRegister() {
  authError.value = ''
  authSuccess.value = ''
  authLoading.value = true
  try {
    const res = await authStore.register(
      registerEmail.value,
      registerPassword.value,
      registerLanguage.value,
      registerFirstName.value,
      registerLastName.value,
    )
    authSuccess.value = res.detail || t('auth.registerSuccess')
  } catch (e: unknown) {
    authError.value = (e as { data?: { detail?: string } })?.data?.detail || t('auth.registerFailed')
  } finally {
    authLoading.value = false
  }
}

function logout() {
  authStore.logout()
  router.push(localePath('/'))
}

async function changeLanguage(code: string) {
  try {
    selectedLanguageCookie.value = code
    selectedLanguageCookieLegacy.value = code
    const targetPath = switchLocalePath(code)
    if (targetPath && targetPath !== route.fullPath) {
      await router.push(targetPath)
      return
    }
    await setLocale(code)
  } finally {
    desktopLanguageMenuOpen.value = false
    mobileLanguageMenuOpen.value = false
    mobileOpen.value = false
  }
}

watch(
  () => route.fullPath,
  async () => {
    mobileOpen.value = false
    navHidden.value = false
    desktopLanguageMenuOpen.value = false
    mobileLanguageMenuOpen.value = false
    await nextTick()
    updateNavTone()
  },
)

function onScroll() {
  if (!import.meta.client) return
  const currentY = Math.max(0, window.scrollY)
  hasScrolled.value = currentY > 8

  if (mobileOpen.value) {
    navHidden.value = false
  } else {
    const scrollingDown = currentY > lastScrollY.value
    const delta = Math.abs(currentY - lastScrollY.value)
    if (currentY <= 16) {
      navHidden.value = false
    } else if (delta > 6) {
      navHidden.value = scrollingDown
    }
  }

  lastScrollY.value = currentY
  updateNavTone()
}

function updateNavTone() {
  if (!import.meta.client) return
  const nav = navRef.value
  if (!nav) return

  const x = Math.max(1, Math.floor(window.innerWidth / 2))
  const y = Math.max(1, Math.floor(nav.offsetHeight / 2))
  const stack = document.elementsFromPoint(x, y)
  const underNav = stack.find((el) => !nav.contains(el))
  isOverDarkZone.value = Boolean(underNav?.closest('[data-nav-theme="dark"]'))
}

onMounted(() => {
  if (!import.meta.client) return
  lastScrollY.value = Math.max(0, window.scrollY)
  hasScrolled.value = lastScrollY.value > 8
  navHidden.value = false
  updateNavTone()
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', updateNavTone, { passive: true })
})

onBeforeUnmount(() => {
  if (!import.meta.client) return
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('resize', updateNavTone)
})
</script>
