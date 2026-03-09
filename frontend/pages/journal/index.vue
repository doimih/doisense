<template>
  <div class="max-w-2xl mx-auto">
    <section v-if="hasCmsContent && cmsPage" class="mb-6 space-y-3">
      <h1 class="text-2xl font-bold text-stone-800">{{ cmsPage.title }}</h1>
      <div class="bg-white border border-stone-200 rounded-xl p-4">
        <p class="text-sm text-stone-700 leading-7 whitespace-pre-line">{{ cmsPage.content }}</p>
      </div>
    </section>
    <h1 v-else class="text-2xl font-bold text-stone-800 mb-4">{{ $t('nav.journal') }}</h1>
    <p v-if="loadingQuestions" class="text-stone-500">{{ $t('common.loading') }}</p>
    <div v-else class="space-y-4">
      <JournalCard
        v-for="q in questions"
        :key="q.id"
        :question="q"
        @submitted="onSubmitted"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const { fetchApi } = useApi()
const { locale } = useI18n()
const { cmsPage, hasCmsContent } = useCmsStaticPage('journal')

const questions = ref<{ id: number; text: string; category: string }[]>([])
const loadingQuestions = ref(true)

usePublicSeo({
  title: 'Jurnal - Doisense',
  description: 'Jurnalul personal pentru utilizatori autentificati.',
  noindex: true,
})

onMounted(async () => {
  try {
    const lang = locale.value || 'en'
    questions.value = await fetchApi<typeof questions.value>(`/journal/questions?language=${lang}`)
  } catch {
    questions.value = []
  } finally {
    loadingQuestions.value = false
  }
})

function onSubmitted() {
  // Optional: refresh or show success
}
</script>
