<template>
  <div class="max-w-3xl mx-auto">
    <section v-if="hasCmsContent && cmsPage" class="mb-6 space-y-3">
      <h1 class="text-2xl font-bold text-stone-800">{{ cmsPage.title }}</h1>
      <div class="bg-white border border-stone-200 rounded-xl p-4">
        <p class="text-sm text-stone-700 leading-7 whitespace-pre-line">{{ cmsPage.content }}</p>
      </div>
    </section>
    <h1 v-else class="text-2xl font-bold text-stone-800 mb-4">{{ $t('nav.programs') }}</h1>
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
const { cmsPage, hasCmsContent } = useCmsStaticPage('programs')

const programs = ref<{ id: number; title: string; description: string; is_premium: boolean }[]>([])
const loading = ref(true)

usePublicSeo({
  title: 'Programe ghidate - Doisense',
  description: 'Lista programelor ghidate disponibile pentru utilizatorii autentificati.',
  noindex: true,
})

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
