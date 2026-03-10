<template>
  <div class="max-w-md mx-auto py-12">
    <h1 class="text-2xl font-bold text-stone-800 mb-6">{{ $t('auth.register') }}</h1>
    <form @submit.prevent="register" class="space-y-4">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label class="block text-sm font-medium text-stone-700 mb-1">{{ $t('auth.firstName') }}</label>
          <input
            v-model="firstName"
            type="text"
            class="w-full px-3 py-2 border border-stone-300 rounded-lg"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-stone-700 mb-1">{{ $t('auth.lastName') }}</label>
          <input
            v-model="lastName"
            type="text"
            class="w-full px-3 py-2 border border-stone-300 rounded-lg"
          />
        </div>
      </div>
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
          minlength="8"
          class="w-full px-3 py-2 border border-stone-300 rounded-lg"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-stone-700 mb-1">{{ $t('auth.language') }}</label>
        <select v-model="language" class="w-full px-3 py-2 border border-stone-300 rounded-lg">
          <option value="ro">Română</option>
          <option value="en">English</option>
          <option value="de">Deutsch</option>
          <option value="fr">Français</option>
          <option value="it">Italiano</option>
          <option value="es">Español</option>
          <option value="pl">Polski</option>
        </select>
      </div>
      <label class="block text-sm text-stone-700">
        <input v-model="acceptedLegal" type="checkbox" class="mr-2 align-middle" />
        <span class="align-middle">
          {{ legalText.prefix }}
          <NuxtLink :to="localePath('/legal/terms')" class="text-amber-600 hover:underline">{{ legalText.terms }}</NuxtLink>
          {{ legalText.and }}
          <NuxtLink :to="localePath('/legal/privacy')" class="text-amber-600 hover:underline">{{ legalText.privacy }}</NuxtLink>
          {{ legalText.suffix }}
        </span>
      </label>
      <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
      <p v-if="success" class="text-emerald-700 text-sm">{{ success }}</p>
      <button
        type="submit"
        :disabled="loading || success"
        class="w-full py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50"
      >
        {{ loading ? $t('common.loading') : $t('auth.register') }}
      </button>
    </form>
    <p class="mt-4 text-center text-stone-600">
      <NuxtLink :to="localePath('/auth/login')" class="text-amber-600 hover:underline">
        {{ $t('auth.hasAccount') }}
      </NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const authStore = useAuthStore()
const { t } = useI18n()

const email = ref('')
const password = ref('')
const language = ref('en')
const firstName = ref('')
const lastName = ref('')
const acceptedLegal = ref(false)
const error = ref('')
const loading = ref(false)
const success = ref('')

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
  suffix: '.',
  validation: t('auth.mustAcceptLegal'),
}))

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
      firstName.value,
      lastName.value,
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
</script>
