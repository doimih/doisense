<template>
  <div class="max-w-md mx-auto">
    <h1 class="text-2xl font-bold text-stone-800 mb-4">{{ $t('nav.profile') }}</h1>
    <div v-if="authStore.user" class="space-y-4">
      <p><span class="font-medium">{{ $t('auth.email') }}:</span> {{ authStore.user.email }}</p>
      <p><span class="font-medium">{{ $t('profile.premium') }}:</span> {{ authStore.user.is_premium ? $t('common.yes') : $t('common.no') }}</p>
      <button
        v-if="!authStore.user.is_premium"
        :disabled="checkoutLoading"
        class="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50"
        @click="createCheckout"
      >
        {{ checkoutLoading ? $t('common.loading') : $t('profile.upgrade') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const authStore = useAuthStore()
const { fetchApi } = useApi()
const checkoutLoading = ref(false)

async function createCheckout() {
  checkoutLoading.value = true
  try {
    const res = await fetchApi<{ url: string }>('/payments/create-checkout-session', { method: 'POST' })
    if (res?.url) window.location.href = res.url
  } finally {
    checkoutLoading.value = false
  }
}
</script>
