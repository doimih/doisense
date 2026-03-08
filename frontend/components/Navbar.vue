<template>
  <nav class="bg-white border-b border-stone-200 px-4 py-3">
    <div class="container mx-auto flex items-center justify-between gap-4">
      <NuxtLink :to="localePath('/')" class="text-xl font-semibold text-stone-800">Doisense</NuxtLink>
      <div class="flex items-center gap-3 flex-wrap justify-end text-sm">
        <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/features')" class="text-stone-600 hover:text-stone-900">
          Features
        </NuxtLink>
        <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/pricing')" class="text-stone-600 hover:text-stone-900">
          Pricing
        </NuxtLink>
        <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/about')" class="text-stone-600 hover:text-stone-900">
          About
        </NuxtLink>
        <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/contact')" class="text-stone-600 hover:text-stone-900">
          Contact
        </NuxtLink>
        <NuxtLink :to="localePath('/search')" class="text-stone-600 hover:text-stone-900">
          Search
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/chat')" class="text-stone-600 hover:text-stone-900">
          {{ $t('nav.chat') }}
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/journal')" class="text-stone-600 hover:text-stone-900">
          {{ $t('nav.journal') }}
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/programs')" class="text-stone-600 hover:text-stone-900">
          {{ $t('nav.programs') }}
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/profile')" class="text-stone-600 hover:text-stone-900">
          {{ $t('nav.profile') }}
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn && authStore.user?.is_superuser" :to="localePath('/cms/home')" class="text-stone-600 hover:text-stone-900">
          CMS
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn && authStore.user?.is_superuser" :to="localePath('/cms/editor')" class="text-stone-600 hover:text-stone-900">
          CMS Editor
        </NuxtLink>
        <a v-if="authStore.isLoggedIn && authStore.user?.is_superuser" href="/doisense/ro/admin/" class="text-stone-600 hover:text-stone-900">
          Admin
        </a>
        <button
          v-if="!authStore.isLoggedIn"
          type="button"
          class="inline-flex h-9 w-9 items-center justify-center rounded-full border border-stone-300 text-stone-600 hover:border-stone-400 hover:text-stone-900"
          @click="openAuthModal"
          aria-label="Open authentication"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="h-5 w-5">
            <path d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5Zm0 2c-4.418 0-8 2.239-8 5v1h16v-1c0-2.761-3.582-5-8-5Z" />
          </svg>
        </button>
        <NuxtLink :to="localePath('/legal/gdpr')" class="text-stone-600 hover:text-stone-900">
          GDPR
        </NuxtLink>
        <button
          v-if="authStore.isLoggedIn"
          type="button"
          class="text-stone-600 hover:text-stone-900"
          @click="logout"
        >
          {{ $t('auth.logout') }}
        </button>
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
        <h2 class="text-lg font-semibold text-stone-900">Contul tău</h2>
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

      <div class="mb-4 space-y-2">
        <button
          type="button"
          class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-medium text-stone-700 hover:bg-stone-50 disabled:opacity-50"
          :disabled="authLoading || socialLoading === 'apple'"
          @click="loginWithGoogle"
        >
          {{ socialLoading === 'google' ? 'Google...' : 'Continua cu Google' }}
        </button>
        <button
          type="button"
          class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm font-medium text-stone-700 hover:bg-stone-50 disabled:opacity-50"
          :disabled="authLoading || socialLoading === 'google'"
          @click="loginWithApple"
        >
          {{ socialLoading === 'apple' ? 'Apple...' : 'Continua cu Apple' }}
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
            <option value="it">Italiano</option>
            <option value="es">Espanol</option>
            <option value="pl">Polski</option>
          </select>
        </div>
        <p v-if="authError" class="text-sm text-red-600">{{ authError }}</p>
        <button
          type="submit"
          :disabled="authLoading"
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
const authStore = useAuthStore()
const router = useRouter()
const { locale } = useI18n()
const runtimeConfig = useRuntimeConfig()

const showAuthModal = ref(false)
const authTab = ref<'login' | 'register'>('login')
const authLoading = ref(false)
const socialLoading = ref<'' | 'google' | 'apple'>('')
const authError = ref('')

const loginEmail = ref('')
const loginPassword = ref('')

const registerEmail = ref('')
const registerPassword = ref('')
const registerLanguage = ref('en')

function openAuthModal() {
  showAuthModal.value = true
  authError.value = ''
  registerLanguage.value = locale.value?.startsWith('ro') ? 'ro' : 'en'
}

function closeAuthModal() {
  showAuthModal.value = false
  authError.value = ''
}

function switchTab(tab: 'login' | 'register') {
  authTab.value = tab
  authError.value = ''
}

function preferredLanguage() {
  return locale.value?.startsWith('ro') ? 'ro' : 'en'
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
    authError.value = 'Google login nu este configurat.'
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
    authError.value = 'Nu am putut finaliza login cu Google.'
  } finally {
    socialLoading.value = ''
  }
}

async function loginWithApple() {
  const clientId = (runtimeConfig.public.appleClientId as string) || ''
  if (!clientId) {
    authError.value = 'Apple login nu este configurat.'
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
    authError.value = 'Nu am putut finaliza login cu Apple.'
  } finally {
    socialLoading.value = ''
  }
}

async function submitLogin() {
  authError.value = ''
  authLoading.value = true
  try {
    await authStore.login(loginEmail.value, loginPassword.value)
    closeAuthModal()
    await router.push(localePath('/chat'))
  } catch {
    authError.value = 'Datele de logare sunt eronate.'
  } finally {
    authLoading.value = false
  }
}

async function submitRegister() {
  authError.value = ''
  authLoading.value = true
  try {
    await authStore.register(registerEmail.value, registerPassword.value, registerLanguage.value)
    closeAuthModal()
    await router.push(localePath('/chat'))
  } catch {
    authError.value = 'Nu am putut crea contul. Verifica datele si incearca din nou.'
  } finally {
    authLoading.value = false
  }
}

function logout() {
  authStore.logout()
  router.push(localePath('/'))
}
</script>
