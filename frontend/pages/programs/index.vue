<template>
  <div class="max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold text-stone-800 mb-4">{{ $t('nav.programs') }}</h1>
    <p v-if="loading" class="text-stone-500">{{ $t('common.loading') }}</p>
    <div v-else class="grid gap-4 sm:grid-cols-2">
      <ProgramCard
        v-for="p in programs"
        :key="p.id"
        :program="p"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const { fetchApi } = useApi()
const { locale } = useI18n()

const programs = ref<{ id: number; title: string; description: string; is_premium: boolean }[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const lang = locale.value || 'en'
    programs.value = await fetchApi<typeof programs.value>(`/programs?language=${lang}`)
  } catch {
    programs.value = []
  } finally {
    loading.value = false
  }
})
</script>
