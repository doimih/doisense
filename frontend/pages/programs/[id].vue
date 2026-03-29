<template>
  <div class="program-detail mx-auto max-w-5xl space-y-6">
    <NuxtLink :to="localePath('/programs')" class="inline-flex items-center text-sm font-semibold text-amber-700 hover:underline">
      ← Inapoi la programe
    </NuxtLink>

    <p v-if="loading" class="text-stone-500">{{ $t('common.loading') }}</p>

    <template v-else-if="program">
      <section class="program-header">
        <div class="space-y-4">
          <div class="flex flex-wrap items-center gap-2">
            <span class="program-badge">{{ program.category_meta.title }}</span>
            <span :class="planBadgeClass">{{ planLabel }}</span>
            <span class="program-badge-muted">{{ program.duration_days }} zile</span>
          </div>
          <div>
            <h1 class="program-title">{{ program.title }}</h1>
            <p class="program-copy">{{ program.description }}</p>
          </div>
        </div>

        <div class="program-side-card">
          <p class="program-side-kicker">Disponibilitate</p>
          <p class="program-side-copy">{{ availabilityText }}</p>
          <button
            v-if="program.can_activate"
            type="button"
            class="program-primary-action"
            :disabled="working"
            @click="activateProgram"
          >
            {{ isCurrentProgramActive ? 'Program activ' : 'Activeaza programul' }}
          </button>
          <p v-else class="program-side-note">Acest program poate fi explorat, dar activarea cere un plan superior.</p>
        </div>
      </section>

      <section v-if="activeActivation" class="program-progress-card">
        <div>
          <p class="program-side-kicker">Progres curent</p>
          <h2 class="text-2xl font-semibold text-stone-900">Ziua {{ activeActivation.progress_day }}</h2>
          <p class="mt-1 text-sm text-stone-600">
            {{ completedDays.length }} din {{ program.duration_days }} pasi marcati ca finalizati.
          </p>
        </div>
        <div class="program-progress-actions">
          <button
            v-if="!activeActivation.is_paused"
            type="button"
            class="program-secondary-action"
            :disabled="working"
            @click="pauseProgram"
          >
            Pauza
          </button>
          <button
            v-else
            type="button"
            class="program-secondary-action"
            :disabled="working"
            @click="resumeProgram"
          >
            Reia
          </button>
          <button
            v-if="currentStep && !isCurrentStepCompleted"
            type="button"
            class="program-primary-action"
            :disabled="working"
            @click="completeDay"
          >
            Marcheaza ziua {{ currentStep.day_number }}
          </button>
        </div>
      </section>

      <section v-if="feedbackMessage" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-sm text-emerald-900">
        {{ feedbackMessage }}
      </section>

      <section class="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
        <div class="space-y-4">
          <div v-for="step in program.daily_steps" :key="step.id" class="program-step" :class="step.day_number === currentDayNumber ? 'program-step-active' : ''">
            <div class="program-step-topline">
              <span class="program-step-day">Ziua {{ step.day_number }}</span>
              <span v-if="completedDays.includes(step.day_number)" class="program-step-complete">Completata</span>
            </div>
            <h3 class="program-step-title">{{ step.title }}</h3>
            <p class="program-step-copy">{{ step.content }}</p>
            <div class="program-step-meta">
              <span>{{ step.task_type }}</span>
              <span>{{ step.estimated_time_minutes }} min</span>
            </div>
            <p v-if="step.question" class="program-step-question">{{ step.question }}</p>
          </div>
        </div>

        <div class="space-y-4">
          <section v-if="currentStep" class="program-focus-card">
            <p class="program-side-kicker">Focus acum</p>
            <h2 class="text-xl font-semibold text-stone-900">{{ currentStep.title }}</h2>
            <p class="mt-2 text-sm leading-7 text-stone-600">{{ currentStep.content }}</p>
          </section>

          <section v-if="activeActivation" class="program-focus-card">
            <p class="program-side-kicker">Reflectie</p>
            <textarea
              v-model="reflectionText"
              rows="5"
              class="program-textarea"
              placeholder="Noteaza ce a mers bine, ce ai observat si ce ajustezi maine."
            />
            <div class="mt-3 flex items-center gap-3">
              <button type="button" class="program-secondary-action" :disabled="working || !currentDayNumber" @click="saveReflection">
                Salveaza reflectia
              </button>
              <span v-if="reflectionSaved" class="text-sm text-emerald-700">Reflectie salvata</span>
            </div>
            <div v-if="reflectionFeedback" class="mt-3 rounded-2xl border border-sky-200 bg-sky-50 p-4 text-sm text-sky-900">
              <p class="font-semibold">Feedback AI</p>
              <p class="mt-1">{{ reflectionFeedback }}</p>
            </div>
          </section>
        </div>
      </section>
    </template>

    <p v-else class="text-red-600">{{ $t('programs.notFound') }}</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'subscription'] as any })

const route = useRoute()
const localePath = useLocalePath()
const { fetchApi } = useApi()

const programId = route.params.id as string

type ProgramActivation = {
  progress_day: number
  status: string
  completed_days: number[]
  is_paused: boolean
}

type ProgramDay = {
  id: number
  day_number: number
  title: string
  content: string
  task_type: string
  estimated_time_minutes: number
  question: string
}

type ProgramDetail = {
  id: number
  category: string
  category_meta: { title: string; icon: string }
  title: string
  description: string
  duration_days: number
  plan_access: 'basic' | 'premium' | 'vip'
  can_activate: boolean
  daily_steps: ProgramDay[]
  activation?: ProgramActivation | null
}

type ActiveProgramPayload = {
  item: null | {
    program: { id: number; title: string; duration_days: number }
    activation: ProgramActivation
    current_step: ProgramDay | null
  }
}

type ReflectionData = { reflection_text: string; ai_feedback: string }

type CompleteDayData = {
  activation: ProgramActivation
  completed_day: number
  daily_message: string
  dynamic_recommendation: { adjustment: string; suggestion: string } | null
}

const program = ref<ProgramDetail | null>(null)
const activeItem = ref<ActiveProgramPayload['item']>(null)
const reflectionText = ref('')
const reflectionFeedback = ref('')
const reflectionSaved = ref(false)
const feedbackMessage = ref('')
const loading = ref(true)
const working = ref(false)

const activeActivation = computed(() => {
  if (activeItem.value?.program.id === Number(programId)) return activeItem.value.activation
  return program.value?.activation || null
})

const currentDayNumber = computed(() => activeActivation.value?.progress_day || 1)
const currentStep = computed(() => program.value?.daily_steps.find(step => step.day_number === currentDayNumber.value) || null)
const completedDays = computed(() => activeActivation.value?.completed_days || [])
const isCurrentStepCompleted = computed(() => completedDays.value.includes(currentDayNumber.value))
const isCurrentProgramActive = computed(() => activeItem.value?.program.id === Number(programId) && activeActivation.value?.status === 'active')

const planLabel = computed(() => {
  if (program.value?.plan_access === 'vip') return 'VIP Executive'
  if (program.value?.plan_access === 'premium') return 'PREMIUM Flow'
  return 'BASIC Start'
})

const planBadgeClass = computed(() => {
  if (program.value?.plan_access === 'vip') return 'program-badge program-badge-vip'
  if (program.value?.plan_access === 'premium') return 'program-badge program-badge-premium'
  return 'program-badge program-badge-basic'
})

const availabilityText = computed(() => {
  if (!program.value) return ''
  if (isCurrentProgramActive.value) return 'Programul este deja activ si sincronizat cu task-urile din calendar.'
  if (program.value.can_activate) return 'Poate fi activat acum. Task-urile zilnice vor fi generate automat in calendar.'
  return 'Acces disponibil doar pentru vizualizare in planul curent.'
})

usePublicSeo({
  title: computed(() => program.value?.title ? `${program.value.title} - Doisense` : 'Program ghidat - Doisense'),
  description: computed(() => program.value?.description || 'Program ghidat integrat cu calendar si task-uri.'),
  noindex: true,
})

async function loadProgram() {
  program.value = await fetchApi<ProgramDetail>(`/programs/${programId}`)
}

async function loadActiveItem() {
  const response = await fetchApi<ActiveProgramPayload>('/programs/active')
  activeItem.value = response.item
}

async function loadReflection() {
  reflectionSaved.value = false
  reflectionFeedback.value = ''
  reflectionText.value = ''
  if (!currentDayNumber.value) return
  try {
    const response = await fetchApi<ReflectionData>(`/programs/${programId}/reflection?day_number=${currentDayNumber.value}`)
    reflectionText.value = response.reflection_text || ''
    reflectionFeedback.value = response.ai_feedback || ''
  } catch {
    reflectionText.value = ''
    reflectionFeedback.value = ''
  }
}

async function refreshAll() {
  await Promise.all([loadProgram(), loadActiveItem()])
  await loadReflection()
}

async function activateProgram() {
  working.value = true
  feedbackMessage.value = ''
  try {
    await fetchApi(`/programs/${programId}/activate`, { method: 'POST', body: {} })
    feedbackMessage.value = 'Programul a fost activat si task-urile au fost adaugate in calendar.'
    await refreshAll()
  } finally {
    working.value = false
  }
}

async function completeDay() {
  working.value = true
  try {
    const response = await fetchApi<CompleteDayData>(`/programs/${programId}/complete-day`, {
      method: 'POST',
      body: { day_number: currentDayNumber.value },
    })
    const adaptiveText = response.dynamic_recommendation
      ? ` ${response.dynamic_recommendation.adjustment} ${response.dynamic_recommendation.suggestion}`
      : ''
    feedbackMessage.value = `${response.daily_message || 'Ziua a fost marcata ca finalizata.'}${adaptiveText}`.trim()
    await refreshAll()
  } finally {
    working.value = false
  }
}

async function pauseProgram() {
  working.value = true
  try {
    await fetchApi(`/programs/${programId}/pause`, { method: 'POST', body: {} })
    await refreshAll()
  } finally {
    working.value = false
  }
}

async function resumeProgram() {
  working.value = true
  try {
    await fetchApi(`/programs/${programId}/resume`, { method: 'POST', body: {} })
    await refreshAll()
  } finally {
    working.value = false
  }
}

async function saveReflection() {
  if (!reflectionText.value.trim()) return
  working.value = true
  reflectionSaved.value = false
  try {
    const response = await fetchApi<ReflectionData>(`/programs/${programId}/reflection`, {
      method: 'POST',
      body: {
        day_number: currentDayNumber.value,
        reflection_text: reflectionText.value,
      },
    })
    reflectionFeedback.value = response.ai_feedback || ''
    reflectionSaved.value = true
  } finally {
    working.value = false
  }
}

onMounted(async () => {
  try {
    await refreshAll()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.program-header {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
  gap: 24px;
  padding: 28px;
  border-radius: 28px;
  border: 1px solid #dde5de;
  background:
    radial-gradient(circle at top right, rgba(245, 200, 111, 0.2), transparent 34%),
    linear-gradient(180deg, #fffdf6 0%, #ffffff 70%);
}

.program-badge,
.program-badge-muted {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 7px 10px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.program-badge-basic {
  background: #eef5f0;
  color: #577566;
}

.program-badge-premium {
  background: #fff0d6;
  color: #986120;
}

.program-badge-vip {
  background: #e7f3eb;
  color: #2b6b4b;
}

.program-badge-muted {
  background: #f4f5f3;
  color: #748278;
}

.program-title {
  font-size: clamp(30px, 5vw, 48px);
  line-height: 0.96;
  font-weight: 700;
  color: #1f352c;
}

.program-copy {
  margin-top: 14px;
  max-width: 760px;
  font-size: 15px;
  line-height: 1.8;
  color: #607166;
}

.program-side-card,
.program-progress-card,
.program-focus-card {
  border-radius: 24px;
  border: 1px solid #dde4de;
  background: white;
  padding: 20px;
}

.program-side-kicker {
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #7a8a81;
}

.program-side-copy,
.program-side-note {
  margin-top: 10px;
  font-size: 14px;
  line-height: 1.7;
  color: #617369;
}

.program-primary-action,
.program-secondary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  border-radius: 999px;
  padding: 0 18px;
  font-size: 13px;
  font-weight: 700;
}

.program-primary-action {
  margin-top: 16px;
  background: #22372e;
  color: white;
}

.program-secondary-action {
  border: 1px solid #d5ddd7;
  background: white;
  color: #31473c;
}

.program-progress-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.program-progress-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.program-step {
  border: 1px solid #e0e6e1;
  border-radius: 22px;
  padding: 18px;
  background: white;
}

.program-step-active {
  border-color: #e5c27b;
  background: linear-gradient(180deg, #fff7e7, #ffffff);
}

.program-step-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.program-step-day,
.program-step-complete {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.program-step-day {
  color: #7c8a82;
}

.program-step-complete {
  color: #2f7751;
}

.program-step-title {
  margin-top: 10px;
  font-size: 20px;
  font-weight: 700;
  color: #22362d;
}

.program-step-copy {
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.8;
  color: #637369;
}

.program-step-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
  font-size: 12px;
  color: #869288;
}

.program-step-question {
  margin-top: 14px;
  border-radius: 18px;
  background: #f6f8f6;
  padding: 12px 14px;
  font-size: 13px;
  color: #50645a;
}

.program-textarea {
  width: 100%;
  margin-top: 12px;
  border-radius: 18px;
  border: 1px solid #d9e1db;
  background: #f8faf8;
  padding: 14px 16px;
  font-size: 14px;
  color: #24372e;
  outline: none;
}

@media (max-width: 920px) {
  .program-header,
  .program-progress-card {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
