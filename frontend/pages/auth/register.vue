<template>
  <div class="max-w-md mx-auto py-12">
    <h1 class="text-2xl font-bold text-stone-800 mb-6">{{ $t('auth.register') }}</h1>
    <form @submit.prevent="register" class="space-y-4">
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
          <option value="it">Italiano</option>
          <option value="es">Español</option>
          <option value="pl">Polski</option>
        </select>
      </div>
      <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
      <button
        type="submit"
        :disabled="loading"
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
const { localePath } = useLocalePath()
const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const language = ref('en')
const error = ref('')
const loading = ref(false)

async function register() {
  error.value = ''
  loading.value = true
  try {
    await authStore.register(email.value, password.value, language.value)
    await router.push(localePath('/chat'))
  } catch (e: unknown) {
    error.value = (e as { message?: string })?.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
