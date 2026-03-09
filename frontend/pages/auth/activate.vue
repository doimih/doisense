<template>
  <div class="max-w-md mx-auto py-12">
    <h1 class="text-2xl font-bold text-stone-800 mb-4">Activare cont</h1>
    <p class="text-stone-600 mb-6">
      Confirmam contul tau folosind linkul din email.
    </p>

    <p v-if="loading" class="text-stone-700">{{ $t('common.loading') }}...</p>
    <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>
    <p v-if="success" class="text-emerald-700 text-sm">{{ success }}</p>

    <NuxtLink :to="localePath('/auth/login')" class="mt-6 inline-block text-amber-600 hover:underline">
      Mergi la autentificare
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const route = useRoute()
const config = useRuntimeConfig()

const loading = ref(true)
const error = ref('')
const success = ref('')

onMounted(async () => {
  const uid = (route.query.uid as string) || ''
  const token = (route.query.token as string) || ''

  if (!uid || !token) {
    error.value = 'Link de activare invalid.'
    loading.value = false
    return
  }

  try {
    const base = config.public.apiBase as string
    const res = await $fetch<{ detail: string }>(`${base}/auth/activate`, {
      method: 'POST',
      body: { uid, token },
    })
    success.value = res.detail || 'Cont activat cu succes.'
  } catch (e: unknown) {
    error.value = (e as { data?: { detail?: string } })?.data?.detail || 'Nu am putut activa contul.'
  } finally {
    loading.value = false
  }
})
</script>
