<template>
  <div class="max-w-6xl mx-auto px-4">
    <!-- CMS Content Section -->
    <section v-if="hasCmsContent && cmsPage" class="mb-8 space-y-3">
      <h1 class="text-3xl font-bold text-slate-900">{{ cmsPage.title }}</h1>
      <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <p class="text-base text-slate-700 leading-7 whitespace-pre-line">{{ cmsPage.content }}</p>
      </div>
    </section>

    <!-- Page Header -->
    <div v-else class="mb-8">
      <h1 class="text-3xl font-bold text-slate-900 mb-2">{{ $t('nav.journal') }}</h1>
      <p class="text-slate-600">{{ $t('journal.description') || 'Reflect on your daily experiences with guided questions.' }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loadingQuestions" class="flex items-center justify-center py-12">
      <div class="text-slate-500">{{ $t('common.loading') }}</div>
    </div>

    <!-- Questions by Category -->
    <div v-else-if="groupedQuestions.length > 0" class="space-y-8">
      <!-- Category Section -->
      <div v-for="category in groupedQuestions" :key="category.name" class="space-y-4">
        <!-- Category Header -->
        <div class="flex items-center gap-3 mb-4">
          <div class="h-1 w-12 bg-teal-500 rounded"></div>
          <h2 class="text-xl font-semibold text-slate-900">{{ getCategoryLabel(category.name) }}</h2>
          <span class="ml-auto text-sm text-slate-500 bg-slate-100 px-3 py-1 rounded-full">
            {{ category.questions.length }}
          </span>
        </div>

        <!-- Questions Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <JournalCard
            v-for="q in category.questions"
            :key="q.id"
            :question="q"
            @submitted="onSubmitted"
          />
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-col items-center justify-center py-12">
      <svg class="w-12 h-12 text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7 20H5a2 2 0 01-2-2V7a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2h-5.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-1.414 0l-2.414-2.414a1 1 0 00-.707-.293z" />
      </svg>
      <p class="text-slate-600 text-lg">{{ $t('journal.noQuestions') || 'No questions available' }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const { fetchApi } = useApi()
const { locale, t } = useI18n()
const { cmsPage, hasCmsContent } = useCmsStaticPage('journal')

interface Question {
  id: number
  text: string
  category: string
}

interface CategoryGroup {
  name: string
  questions: Question[]
}

const questions = ref<Question[]>([])
const loadingQuestions = ref(true)

// Dynamic SEO based on language
const seoTitles: Record<string, string> = {
  ro: 'Jurnal - Doisense',
  en: 'Journal - Doisense',
  de: 'Tagebuch - Doisense',
  it: 'Diario - Doisense',
  pl: 'Dziennik - Doisense',
  es: 'Diario - Doisense',
  fr: 'Journal - Doisense',
}

const seoDescriptions: Record<string, string> = {
  ro: 'Reflectează asupra experienţelor tale zilnice cu întrebări ghidate.',
  en: 'Reflect on your daily experiences with guided questions.',
  de: 'Reflektiere über deine täglichen Erfahrungen mit geführten Fragen.',
  it: 'Rifletti sulle tue esperienze quotidiane con domande guidate.',
  pl: 'Zastanów się nad swoimi codziennymi doświadczeniami za pomocą pytań przewodnika.',
  es: 'Reflexiona sobre tus experiencias diarias con preguntas guiadas.',
  fr: 'Réfléchissez à vos expériences quotidiennes avec des questions guidées.',
}

const currentLang = computed(() => locale.value || 'en')

usePublicSeo({
  title: computed(() => seoTitles[currentLang.value]),
  description: computed(() => seoDescriptions[currentLang.value]),
  noindex: true,
})

// Computed property to group questions by category
const groupedQuestions = computed(() => {
  const groups = new Map<string, Question[]>()

  questions.value.forEach((q) => {
    const category = q.category || 'general'
    if (!groups.has(category)) {
      groups.set(category, [])
    }
    groups.get(category)!.push(q)
  })

  // Convert to array and sort by category name
  const sorted = Array.from(groups.entries())
    .map(([name, qs]) => ({ name, questions: qs }))
    .sort((a, b) => a.name.localeCompare(b.name))

  return sorted as CategoryGroup[]
})

// Category label mapping (translatable)
const categoryLabels: Record<string, string> = {
  'emotions': 'Emotions',
  'daily': 'Daily Reflections',
  'goals': 'Goals & Progress',
  'wellness': 'Wellness',
  'relationships': 'Relationships',
  'health': 'Health',
  'work': 'Work & Career',
  'general': 'General',
  // Romanian
  'emotii': 'Emoții',
  'zilnic': 'Reflecții Zilnice',
  'obiective': 'Obiective și Progres',
  'binestare': 'Bine-ființă',
  'relatii': 'Relații',
  'sanatate': 'Sănătate',
  'munca': 'Muncă și Carieră',
  // German
  'gefühle': 'Gefühle',
  'täglich': 'Tägliche Überlegungen',
  'ziele': 'Ziele & Fortschritt',
  'wohlbefinden': 'Wohlbefinden',
  'beziehungen': 'Beziehungen',
  'gesundheit': 'Gesundheit',
  'arbeit': 'Arbeit & Karriere',
  // Italian
  'emozioni': 'Emozioni',
  'quotidiano': 'Riflessioni Quotidiane',
  'obiettivi': 'Obiettivi e Progresso',
  'benessere': 'Benessere',
  'relazioni': 'Relazioni',
  'salute': 'Salute',
  'lavoro': 'Lavoro e Carriera',
}

function getCategoryLabel(category: string): string {
  return categoryLabels[category.toLowerCase()] || category
}

onMounted(async () => {
  try {
    const lang = locale.value || 'en'
    questions.value = await fetchApi<Question[]>(`/journal/questions?language=${lang}`)
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
