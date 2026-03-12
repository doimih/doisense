<template>
  <div class="max-w-2xl mx-auto space-y-6">
    <NuxtLink :to="localePath('/programs')" class="text-amber-600 hover:underline inline-block">
      ← {{ $t('common.back') }}
    </NuxtLink>

    <p v-if="loading" class="text-stone-500">{{ $t('common.loading') }}</p>

    <template v-else-if="day">
      <div v-if="isPaused" class="rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        {{ text.pausedNotice }}
      </div>

      <!-- Progress bar -->
      <div class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
        <div class="mb-2 flex items-center justify-between text-sm text-stone-600">
          <span>{{ $t('programs.day') }} {{ currentDay }} / {{ totalDays }}</span>
          <span class="font-semibold text-amber-600">
            {{ Math.round((completedDays.length / Math.max(totalDays, 1)) * 100) }}% {{ $t('programs.completed') }}
          </span>
        </div>
        <div class="h-2 w-full overflow-hidden rounded-full bg-stone-100">
          <div
            class="h-2 rounded-full bg-amber-500 transition-all"
            :style="{ width: `${Math.round((completedDays.length / Math.max(totalDays, 1)) * 100)}%` }"
          />
        </div>
      </div>

      <!-- Day content -->
      <div class="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm">
        <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-stone-400">{{ $t('programs.day') }} {{ currentDay }}</p>
        <h1 class="text-2xl font-bold text-stone-800">{{ day.title }}</h1>
        <p class="mt-4 text-stone-600 whitespace-pre-wrap leading-relaxed">{{ day.content }}</p>
        <p v-if="day.question" class="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4 font-medium text-stone-700">
          {{ day.question }}
        </p>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-3">
        <button
          v-if="currentDay > 1"
          class="flex-1 rounded-full border border-stone-300 bg-white px-4 py-2.5 text-sm font-semibold text-stone-700 hover:bg-stone-50 transition"
          @click="navigateDay(currentDay - 1)"
        >
          ← {{ $t('programs.prevDay') }}
        </button>
        <button
          v-if="!isDayCompleted(currentDay) && currentDay <= totalDays"
          :disabled="completing"
          class="flex-1 rounded-full bg-amber-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-amber-600 transition disabled:opacity-50"
          @click="completeDay"
        >
          {{ completing ? $t('common.loading') : $t('programs.markComplete') }}
        </button>
        <button
          v-else-if="isDayCompleted(currentDay) && currentDay < totalDays"
          class="flex-1 rounded-full bg-stone-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-black transition"
          @click="navigateDay(currentDay + 1)"
        >
          {{ $t('programs.nextDay') }} →
        </button>
        <span
          v-else-if="isDayCompleted(currentDay) && currentDay >= totalDays"
          class="flex-1 rounded-full bg-emerald-600 px-4 py-2.5 text-center text-sm font-semibold text-white"
        >
          🎉 {{ $t('programs.allComplete') }}
        </span>
      </div>

      <div class="flex items-center gap-3">
        <button
          v-if="!isPaused"
          type="button"
          class="rounded-full border border-stone-300 bg-white px-4 py-2 text-sm font-semibold text-stone-700 hover:bg-stone-50 transition"
          @click="pauseProgram"
        >
          {{ text.pause }}
        </button>
        <button
          v-else
          type="button"
          class="rounded-full bg-stone-900 px-4 py-2 text-sm font-semibold text-white hover:bg-black transition"
          @click="resumeProgram"
        >
          {{ text.resume }}
        </button>
      </div>

      <div class="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm space-y-3">
        <h2 class="text-lg font-semibold text-stone-900">{{ text.reflectionTitle }}</h2>
        <textarea
          v-model="reflectionText"
          rows="4"
          class="w-full rounded-xl border border-stone-200 bg-stone-50 px-4 py-3 text-sm text-stone-800 outline-none focus:border-stone-400"
          :placeholder="text.reflectionPlaceholder"
        />
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="rounded-full bg-amber-500 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-600 disabled:opacity-50"
            :disabled="savingReflection"
            @click="saveReflection"
          >
            {{ savingReflection ? $t('common.loading') : text.saveReflection }}
          </button>
          <span v-if="reflectionSaved" class="text-sm text-emerald-700">{{ text.saved }}</span>
        </div>
        <div v-if="reflectionFeedback" class="rounded-xl border border-sky-200 bg-sky-50 p-4 text-sm text-sky-900">
          <p class="mb-1 font-semibold">{{ text.feedbackTitle }}</p>
          <p>{{ reflectionFeedback }}</p>
        </div>
      </div>
    </template>

    <p v-else class="text-red-600">{{ $t('programs.notFound') }}</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'subscription'] as any })

const route = useRoute()
const { fetchApi } = useApi()
const { t } = useI18n()

const programId = route.params.id as string

type DayData = { title: string; content: string; question: string }
type ProgressData = { current_day: number; completed_days: number[]; total_days: number; is_paused?: boolean }
type ReflectionData = { reflection_text: string; ai_feedback: string }

const day = ref<DayData | null>(null)
const loading = ref(true)
const completing = ref(false)
const currentDay = ref(1)
const completedDays = ref<number[]>([])
const totalDays = ref(0)
const isPaused = ref(false)
const reflectionText = ref('')
const reflectionFeedback = ref('')
const savingReflection = ref(false)
const reflectionSaved = ref(false)

const { locale } = useI18n()

const text = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  if (code === 'ro') {
    return {
      pause: 'Pauză program',
      resume: 'Reia programul',
      pausedNotice: 'Programul este pus pe pauză. Îl poți relua când ești gata.',
      reflectionTitle: 'Reflecție ziua curentă',
      reflectionPlaceholder: 'Scrie aici ce ai observat azi, ce a mers bine și ce vrei să ajustezi.',
      saveReflection: 'Salvează reflecția',
      saved: 'Reflecție salvată',
      feedbackTitle: 'Feedback AI',
    }
  }
  return {
    pause: 'Pause program',
    resume: 'Resume program',
    pausedNotice: 'This program is currently paused. Resume when you are ready.',
    reflectionTitle: 'Current day reflection',
    reflectionPlaceholder: 'Write what you noticed today, what worked, and what you want to adjust next.',
    saveReflection: 'Save reflection',
    saved: 'Reflection saved',
    feedbackTitle: 'AI feedback',
  }
})

usePublicSeo({
  title: computed(() => day.value ? `${day.value.title} - Doisense` : 'Program ghidat - Doisense'),
  description: 'Progres program ghidat.',
  noindex: true,
})

async function loadProgress() {
  try {
    const progress = await fetchApi<ProgressData>(`/programs/${programId}/progress`)
    if (progress) {
      currentDay.value = progress.current_day
      completedDays.value = progress.completed_days
      totalDays.value = progress.total_days
      isPaused.value = Boolean(progress.is_paused)
    }
  } catch {
    // fallback: start from day 1
  }
}

async function loadReflection(dayNum: number) {
  reflectionSaved.value = false
  try {
    const item = await fetchApi<ReflectionData>(`/programs/${programId}/reflection?day_number=${dayNum}`)
    reflectionText.value = item.reflection_text || ''
    reflectionFeedback.value = item.ai_feedback || ''
  } catch {
    reflectionText.value = ''
    reflectionFeedback.value = ''
  }
}

async function loadDay(dayNum: number) {
  loading.value = true
  try {
    day.value = await fetchApi<DayData>(`/programs/${programId}/days/${dayNum}`)
  } catch {
    day.value = null
  } finally {
    loading.value = false
  }
}

function isDayCompleted(dayNum: number) {
  return completedDays.value.includes(dayNum)
}

async function navigateDay(dayNum: number) {
  currentDay.value = dayNum
  await loadDay(dayNum)
  await loadReflection(dayNum)
}

async function completeDay() {
  completing.value = true
  try {
    const progress = await fetchApi<ProgressData>(`/programs/${programId}/progress`, {
      method: 'POST',
      body: { day_number: currentDay.value },
    })
    if (progress) {
      completedDays.value = progress.completed_days
      totalDays.value = progress.total_days
      isPaused.value = Boolean(progress.is_paused)
      // Auto-advance if there are more days
      if (currentDay.value < progress.total_days) {
        await navigateDay(currentDay.value + 1)
        currentDay.value = progress.current_day
      }
    }
  } finally {
    completing.value = false
  }
}

async function pauseProgram() {
  const progress = await fetchApi<ProgressData>(`/programs/${programId}/pause`, { method: 'POST' })
  isPaused.value = Boolean(progress.is_paused)
}

async function resumeProgram() {
  const progress = await fetchApi<ProgressData>(`/programs/${programId}/resume`, { method: 'POST' })
  isPaused.value = Boolean(progress.is_paused)
}

async function saveReflection() {
  if (!reflectionText.value.trim()) {
    return
  }
  savingReflection.value = true
  reflectionSaved.value = false
  try {
    const item = await fetchApi<ReflectionData>(`/programs/${programId}/reflection`, {
      method: 'POST',
      body: {
        day_number: currentDay.value,
        reflection_text: reflectionText.value,
      },
    })
    reflectionFeedback.value = item.ai_feedback || ''
    reflectionSaved.value = true
  } finally {
    savingReflection.value = false
  }
}

onMounted(async () => {
  await loadProgress()
  await loadDay(currentDay.value)
  await loadReflection(currentDay.value)
})
</script>
