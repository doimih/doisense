<template>
  <div class="max-w-md mx-auto py-12">
    <h1 class="text-2xl font-bold text-stone-800 mb-6">{{ title }}</h1>

    <form v-if="!isResetMode" @submit.prevent="requestRecovery" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-stone-700 mb-1">{{ t('auth.email') }}</label>
        <input
          v-model="email"
          type="email"
          required
          class="w-full px-3 py-2 border border-stone-300 rounded-lg"
        />
      </div>
      <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
      <p v-if="success" class="text-emerald-700 text-sm">{{ success }}</p>
      <button
        type="submit"
        :disabled="loading"
        class="w-full py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50"
      >
        {{ loading ? t('common.loading') : actionLabel }}
      </button>
    </form>

    <form v-else @submit.prevent="confirmReset" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-stone-700 mb-1">{{ t('auth.password') }}</label>
        <input
          v-model="newPassword"
          type="password"
          minlength="8"
          required
          class="w-full px-3 py-2 border border-stone-300 rounded-lg"
        />
      </div>
      <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
      <p v-if="success" class="text-emerald-700 text-sm">{{ success }}</p>
      <button
        type="submit"
        :disabled="loading"
        class="w-full py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50"
      >
        {{ loading ? t('common.loading') : resetLabel }}
      </button>
    </form>

    <p class="mt-4 text-center text-stone-600">
      <NuxtLink :to="localePath('/auth/login')" class="text-amber-600 hover:underline">
        {{ backLabel }}
      </NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n, useLocalePath, useRoute, useRuntimeConfig } from '#imports'

const localePath = useLocalePath()
const route = useRoute()
const { t } = useI18n()

const email = ref('')
const newPassword = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

const uid = computed(() => (route.query.uid as string) || '')
const token = computed(() => (route.query.token as string) || '')
const isResetMode = computed(() => !!uid.value && !!token.value)

const title = computed(() => (isResetMode.value ? t('auth.recoverSetTitle') : t('auth.recover')))
const actionLabel = computed(() => t('auth.recoverAction'))
const resetLabel = computed(() => t('auth.recoverSetAction'))
const backLabel = computed(() => t('auth.recoverBack'))

usePublicSeo({
  title: 'Recover account - Doisense',
  description: 'Account recovery and password reset for Doisense users.',
  noindex: true,
})

async function requestRecovery() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const config = useRuntimeConfig()
    const base = config.public.apiBase as string
    await $fetch(`${base}/auth/recover`, {
      method: 'POST',
      body: { email: email.value },
    })
    success.value = t('auth.recoverSent')
  } catch {
    error.value = t('auth.recoverError')
  } finally {
    loading.value = false
  }
}

async function confirmReset() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const config = useRuntimeConfig()
    const base = config.public.apiBase as string
    await $fetch(`${base}/auth/recover/confirm`, {
      method: 'POST',
      body: {
        uid: uid.value,
        token: token.value,
        new_password: newPassword.value,
      },
    })
    success.value = t('auth.recoverDone')
  } catch {
    error.value = t('auth.recoverInvalid')
  } finally {
    loading.value = false
  }
}
</script>
