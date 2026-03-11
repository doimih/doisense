<template>
  <section class="mx-auto max-w-5xl px-4 py-8 md:py-12">
    <div class="mb-8 flex flex-wrap items-center gap-3">
      <div
        v-for="(step, index) in text.steps"
        :key="step.title"
        :class="[
          'flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-medium transition',
          index === currentStep
            ? 'border-sky-300 bg-sky-100 text-sky-900'
            : index < currentStep
            ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
            : 'border-stone-200 bg-white text-stone-500',
        ]"
      >
        <span class="flex h-6 w-6 items-center justify-center rounded-full border border-current text-xs">{{ index + 1 }}</span>
        <span>{{ step.shortTitle }}</span>
      </div>
    </div>

    <div class="overflow-hidden rounded-[2rem] border border-stone-200 bg-white shadow-[0_25px_80px_-40px_rgba(15,23,42,0.28)]">
      <div class="relative bg-stone-950 px-6 py-10 text-white md:px-10">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(56,189,248,0.28),transparent_35%),radial-gradient(circle_at_bottom_left,rgba(251,191,36,0.18),transparent_35%)]" />
        <div class="relative max-w-3xl space-y-4">
          <p class="inline-flex rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-white/75">
            {{ text.progressLabel(currentStep + 1, text.steps.length) }}
          </p>
          <h1 class="text-3xl font-bold leading-tight md:text-5xl">{{ activeStep.title }}</h1>
          <p v-if="activeStep.text" class="max-w-2xl text-base leading-8 text-white/82 md:text-lg">{{ activeStep.text }}</p>
          <p v-if="activeStep.subtext" class="max-w-2xl text-sm leading-7 text-white/68 md:text-base">{{ activeStep.subtext }}</p>
        </div>
      </div>

      <div class="space-y-8 px-6 py-8 md:px-10 md:py-10">
        <template v-if="activeStep.bullets?.length">
          <ul class="grid gap-4 md:grid-cols-2">
            <li
              v-for="bullet in activeStep.bullets"
              :key="bullet"
              class="rounded-2xl border border-stone-200 bg-stone-50 px-5 py-4 text-sm font-medium leading-6 text-stone-700"
            >
              {{ bullet }}
            </li>
          </ul>
        </template>

        <template v-if="currentStep === 3">
          <div class="space-y-5 rounded-2xl border border-stone-200 bg-stone-50 p-5">
            <label class="flex items-start gap-3 text-sm leading-6 text-stone-700">
              <input v-model="consentAccepted" type="checkbox" class="mt-1 h-4 w-4 rounded border-stone-300 text-sky-600" />
              <span>
                {{ text.consentLabel.before }}
                <NuxtLink :to="localePath('/legal/terms')" class="font-semibold text-sky-700 underline-offset-2 hover:underline">{{ text.consentLabel.terms }}</NuxtLink>
                {{ text.consentLabel.middle }}
                <NuxtLink :to="localePath('/legal/privacy')" class="font-semibold text-sky-700 underline-offset-2 hover:underline">{{ text.consentLabel.privacy }}</NuxtLink>
                {{ text.consentLabel.and }}
                <NuxtLink :to="localePath('/legal/ai-consent')" class="font-semibold text-sky-700 underline-offset-2 hover:underline">{{ text.consentLabel.ai }}</NuxtLink>
                {{ text.consentLabel.after }}
              </span>
            </label>

            <div class="flex flex-wrap gap-3 text-sm">
              <NuxtLink :to="localePath('/legal/terms')" class="rounded-full border border-stone-300 bg-white px-4 py-2 text-stone-700 transition hover:border-stone-400 hover:text-stone-900">{{ text.linkLabels.terms }}</NuxtLink>
              <NuxtLink :to="localePath('/legal/gdpr')" class="rounded-full border border-stone-300 bg-white px-4 py-2 text-stone-700 transition hover:border-stone-400 hover:text-stone-900">{{ text.linkLabels.gdpr }}</NuxtLink>
              <NuxtLink :to="localePath('/legal/ai-consent')" class="rounded-full border border-stone-300 bg-white px-4 py-2 text-stone-700 transition hover:border-stone-400 hover:text-stone-900">{{ text.linkLabels.ai }}</NuxtLink>
              <NuxtLink :to="localePath('/legal/cookies')" class="rounded-full border border-stone-300 bg-white px-4 py-2 text-stone-700 transition hover:border-stone-400 hover:text-stone-900">{{ text.linkLabels.cookies }}</NuxtLink>
            </div>
          </div>
        </template>

        <template v-if="currentStep === 4">
          <div class="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
            <div class="rounded-2xl border border-stone-200 bg-stone-50 p-5">
              <h2 class="text-lg font-semibold text-stone-900">{{ text.profile.moodTitle }}</h2>
              <div class="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <button
                  v-for="option in text.profile.moods"
                  :key="option.value"
                  type="button"
                  :class="[
                    'rounded-2xl border px-4 py-4 text-left transition',
                    selectedMood === option.value
                      ? 'border-sky-400 bg-sky-100 text-sky-900'
                      : 'border-stone-200 bg-white text-stone-700 hover:border-stone-300',
                  ]"
                  @click="selectedMood = option.value"
                >
                  <div class="text-2xl">{{ option.icon }}</div>
                  <div class="mt-2 text-sm font-semibold">{{ option.label }}</div>
                </button>
              </div>
            </div>

            <div class="space-y-5 rounded-2xl border border-stone-200 bg-white p-5">
              <div>
                <div class="flex items-center justify-between gap-4">
                  <h2 class="text-lg font-semibold text-stone-900">{{ text.profile.energyTitle }}</h2>
                  <span class="text-sm font-medium text-stone-500">{{ energyLevel }}/5</span>
                </div>
                <input v-model="energyLevel" type="range" min="1" max="5" step="1" class="mt-4 w-full accent-sky-600" />
              </div>

              <label class="block">
                <span class="mb-2 block text-sm font-semibold text-stone-900">{{ text.profile.journalTitle }}</span>
                <textarea
                  v-model="journalEntry"
                  rows="5"
                  class="w-full rounded-2xl border border-stone-300 px-4 py-3 text-sm text-stone-800 outline-none transition focus:border-stone-500"
                  :placeholder="text.profile.journalPlaceholder"
                />
              </label>

              <p class="text-sm leading-6 text-stone-500">{{ text.profile.note }}</p>
            </div>
          </div>
        </template>

        <template v-if="currentStep === 5">
          <div class="grid gap-4 md:grid-cols-2">
            <article
              v-for="item in text.chatAccessSteps"
              :key="item.title"
              class="rounded-2xl border border-stone-200 bg-stone-50 px-5 py-5"
            >
              <p class="text-xs font-semibold uppercase tracking-[0.14em] text-stone-500">{{ item.step }}</p>
              <h2 class="mt-2 text-lg font-semibold text-stone-900">{{ item.title }}</h2>
              <p class="mt-2 text-sm leading-6 text-stone-600">{{ item.body }}</p>
            </article>
          </div>
        </template>

        <p v-if="stepError" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ stepError }}
        </p>

        <div class="flex flex-col-reverse gap-3 border-t border-stone-200 pt-6 sm:flex-row sm:items-center sm:justify-between">
          <button
            v-if="currentStep > 0"
            type="button"
            class="rounded-full border border-stone-300 px-5 py-3 text-sm font-semibold text-stone-700 transition hover:border-stone-400 hover:text-stone-900"
            @click="goBack"
          >
            {{ text.backAction }}
          </button>
          <div class="sm:ml-auto">
            <button
              type="button"
              :disabled="isBusy || isCurrentStepBlocked"
              class="rounded-full bg-stone-950 px-6 py-3 text-sm font-semibold text-white transition hover:bg-stone-800 disabled:cursor-not-allowed disabled:opacity-50"
              @click="goNext"
            >
              {{ currentStep === text.steps.length - 1 ? text.finishAction : activeStep.button }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const localePath = useLocalePath()
const router = useRouter()
const authStore = useAuthStore()
const { fetchApi } = useApi()
const { locale } = useI18n()
const { chatPath } = useOnboarding()

type MoodValue = 'low' | 'ok' | 'good' | 'great'

interface OnboardingCopy {
  steps: Array<{
    shortTitle: string
    title: string
    text?: string
    subtext?: string
    bullets?: string[]
    button: string
  }>
  progressLabel: (current: number, total: number) => string
  consentLabel: {
    before: string
    terms: string
    middle: string
    privacy: string
    and: string
    ai: string
    after: string
  }
  linkLabels: Record<'terms' | 'gdpr' | 'ai' | 'cookies', string>
  profile: {
    moodTitle: string
    moods: Array<{ value: MoodValue; label: string; icon: string }>
    energyTitle: string
    journalTitle: string
    journalPlaceholder: string
    note: string
  }
  chatAccessSteps: Array<{ step: string; title: string; body: string }>
  backAction: string
  finishAction: string
  consentRequired: string
  saveError: string
  seoTitle: string
  seoDescription: string
}

const copy: Record<string, OnboardingCopy> = {
  ro: {
    steps: [
      {
        shortTitle: 'Bun venit',
        title: 'Bine ai venit în spațiul tău de claritate și echilibru',
        text: 'Aici vei lucra cu un AI creat pentru a te ajuta să înțelegi mai bine ce simți, să-ți clarifici obiectivele și să evoluezi în ritmul tău.',
        button: 'Începe',
      },
      {
        shortTitle: 'Platforma',
        title: 'Cum te poate ajuta platforma',
        bullets: [
          'îți analizează stările emoționale',
          'îți pune întrebări inteligente',
          'îți creează planuri zilnice și rapoarte',
          'te ajută să-ți clarifici obiectivele',
          'îți oferă suport emoțional general',
        ],
        button: 'Continuă',
      },
      {
        shortTitle: 'Disclaimer',
        title: 'Ce este important să știi',
        text: 'Platforma oferă suport emoțional general și instrumente de auto-reflecție. Nu oferă sfaturi medicale, psihologice sau terapeutice.',
        subtext: 'Dacă te confrunți cu o situație gravă, este important să cauți ajutor specializat.',
        button: 'Am înțeles',
      },
      {
        shortTitle: 'Confidențialitate',
        title: 'Protejăm confidențialitatea ta',
        text: 'Nu colectăm nume, adresă sau date personale sensibile. Folosim doar un ID anonim. Datele tale sunt criptate și pot fi șterse oricând.',
        button: 'Accept și continui',
      },
      {
        shortTitle: 'Profil emoțional',
        title: 'Setarea profilului emoțional',
        text: 'Înainte de prima conversație, setează rapid starea ta actuală. Asta ne ajută să pornim mai relevant și mai calm.',
        subtext: 'Poți adăuga și câteva rânduri despre ce te preocupă chiar acum.',
        button: 'Continuă către AI',
      },
      {
        shortTitle: 'Prima conversație',
        title: 'Prima conversație cu AI-ul',
        text: 'Totul este pregătit. Mai jos ai pașii prin care intri în chat și începi prima conversație ghidată.',
        button: 'Deschide chat-ul AI',
      },
    ],
    progressLabel: (current, total) => `Pasul ${current} din ${total}`,
    consentLabel: {
      before: 'Sunt de acord cu ',
      terms: 'Termenii și Condițiile',
      middle: ', ',
      privacy: 'Politica de Confidențialitate',
      and: ' și ',
      ai: 'Acordul AI',
      after: '.',
    },
    linkLabels: {
      terms: 'Termeni și Condiții',
      gdpr: 'Politica GDPR',
      ai: 'Acord AI',
      cookies: 'Politica Cookies',
    },
    profile: {
      moodTitle: 'Cum te simți acum?',
      moods: [
        { value: 'low', label: 'Apăsat(ă)', icon: '🌧️' },
        { value: 'ok', label: 'Echilibrat(ă)', icon: '🌿' },
        { value: 'good', label: 'Bine', icon: '🌤️' },
        { value: 'great', label: 'Foarte bine', icon: '☀️' },
      ],
      energyTitle: 'Nivelul de energie',
      journalTitle: 'Jurnal inițial',
      journalPlaceholder: 'Scrie câteva rânduri despre ce simți, ce te apasă sau ce ai vrea să clarifici.',
      note: 'Vom salva starea ta actuală pentru a personaliza experiența din chat. Nota de jurnal este opțională, dar utilă pentru primul context.',
    },
    chatAccessSteps: [
      { step: 'Pasul 1', title: 'Intri în chat-ul AI', body: 'După acest ecran vei fi redirecționat direct în zona de chat a platformei.' },
      { step: 'Pasul 2', title: 'Alegi direcția conversației', body: 'Poți porni cu suport emoțional, clarificare, obiective sau o întrebare punctuală.' },
      { step: 'Pasul 3', title: 'Scrii primul mesaj', body: 'Spune ce simți acum, ce te preocupă sau ce vrei să înțelegi mai bine despre tine.' },
      { step: 'Pasul 4', title: 'Primești răspuns ghidat', body: 'AI-ul îți oferă întrebări, clarificări și recomandări generale, fără diagnostic sau tratament.' },
    ],
    backAction: 'Înapoi',
    finishAction: 'Deschide chat-ul AI',
    consentRequired: 'Trebuie să accepți termenii înainte să continui.',
    saveError: 'Nu am putut salva profilul inițial. Încearcă din nou.',
    seoTitle: 'Onboarding - Doisense',
    seoDescription: 'Flux ghidat de onboarding pentru utilizatorii noi înainte de prima conversație cu AI-ul.',
  },
  en: {
    steps: [
      {
        shortTitle: 'Welcome',
        title: 'Welcome to your space for clarity and balance',
        text: 'Here you will work with an AI designed to help you understand what you feel, clarify your goals, and grow at your own pace.',
        button: 'Start',
      },
      {
        shortTitle: 'Platform',
        title: 'How the platform can help you',
        bullets: [
          'analyzes your emotional states',
          'asks intelligent questions',
          'creates daily plans and reports',
          'helps you clarify your goals',
          'offers general emotional support',
        ],
        button: 'Continue',
      },
      {
        shortTitle: 'Disclaimer',
        title: 'What is important to know',
        text: 'The platform provides general emotional support and self-reflection tools. It does not provide medical, psychological, or therapeutic advice.',
        subtext: 'If you are facing a serious situation, it is important to seek specialized help.',
        button: 'I understand',
      },
      {
        shortTitle: 'Privacy',
        title: 'We protect your privacy',
        text: 'We do not collect names, addresses, or sensitive personal data. We use only an anonymous ID. Your data is encrypted and can be deleted at any time.',
        button: 'Accept and continue',
      },
      {
        shortTitle: 'Emotional profile',
        title: 'Set up your emotional profile',
        text: 'Before your first conversation, quickly set your current state. This helps us start in a more relevant and calmer way.',
        subtext: 'You can also add a few lines about what is on your mind right now.',
        button: 'Continue to AI',
      },
      {
        shortTitle: 'First chat',
        title: 'Your first conversation with AI',
        text: 'Everything is ready. Below are the steps that take you into chat and help you start your first guided conversation.',
        button: 'Open AI chat',
      },
    ],
    progressLabel: (current, total) => `Step ${current} of ${total}`,
    consentLabel: {
      before: 'I agree with the ',
      terms: 'Terms and Conditions',
      middle: ', ',
      privacy: 'Privacy Policy',
      and: ', and the ',
      ai: 'AI Agreement',
      after: '.',
    },
    linkLabels: {
      terms: 'Terms and Conditions',
      gdpr: 'GDPR Policy',
      ai: 'AI Agreement',
      cookies: 'Cookies Policy',
    },
    profile: {
      moodTitle: 'How do you feel right now?',
      moods: [
        { value: 'low', label: 'Low', icon: '🌧️' },
        { value: 'ok', label: 'Steady', icon: '🌿' },
        { value: 'good', label: 'Good', icon: '🌤️' },
        { value: 'great', label: 'Great', icon: '☀️' },
      ],
      energyTitle: 'Energy level',
      journalTitle: 'Initial journal note',
      journalPlaceholder: 'Write a few lines about what you feel, what feels heavy, or what you want to clarify.',
      note: 'We will save your current state to personalize the chat experience. The journal note is optional, but helpful for initial context.',
    },
    chatAccessSteps: [
      { step: 'Step 1', title: 'Open AI chat', body: 'After this screen you will be redirected straight into the chat area.' },
      { step: 'Step 2', title: 'Choose your direction', body: 'You can start with emotional support, clarity, goals, or a direct question.' },
      { step: 'Step 3', title: 'Write your first message', body: 'Say what you feel now, what is on your mind, or what you want to understand better.' },
      { step: 'Step 4', title: 'Receive guided support', body: 'The AI responds with questions, clarifications, and general recommendations without diagnosis or treatment.' },
    ],
    backAction: 'Back',
    finishAction: 'Open AI chat',
    consentRequired: 'You need to accept the terms before continuing.',
    saveError: 'We could not save your initial profile. Please try again.',
    seoTitle: 'Onboarding - Doisense',
    seoDescription: 'Guided onboarding flow for new users before their first AI conversation.',
  },
}

const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en'].includes(code) ? code : 'en'
})

const text = computed(() => copy[localeCode.value] || copy.en)
const currentStep = ref(0)
const consentAccepted = ref(false)
const selectedMood = ref<MoodValue>('ok')
const energyLevel = ref(3)
const journalEntry = ref('')
const stepError = ref('')
const profileSaved = ref(false)
const isBusy = ref(false)

const activeStep = computed(() => text.value.steps[currentStep.value])
const isCurrentStepBlocked = computed(() => currentStep.value === 3 && !consentAccepted.value)

usePublicSeo({
  title: computed(() => text.value.seoTitle),
  description: computed(() => text.value.seoDescription),
  noindex: true,
})

onMounted(async () => {
  authStore.hydrate()
  if (authStore.user?.onboarding_completed !== false) {
    await router.replace(chatPath.value)
  }
})

function goBack() {
  stepError.value = ''
  currentStep.value = Math.max(0, currentStep.value - 1)
}

async function saveInitialProfile() {
  if (profileSaved.value) {
    return
  }

  const tasks: Promise<unknown>[] = [
    fetchApi('/wellbeing/checkins', {
      method: 'POST',
      body: { mood: selectedMood.value, energy_level: energyLevel.value },
    }),
  ]

  if (journalEntry.value.trim()) {
    const questions = await fetchApi<Array<{ id: number }>>(`/journal/questions?language=${localeCode.value}`)
    if (questions[0]?.id) {
      tasks.push(
        fetchApi('/journal/entries', {
          method: 'POST',
          body: {
            question: questions[0].id,
            content: journalEntry.value.trim(),
            emotions: [selectedMood.value],
          },
        }),
      )
    }
  }

  await Promise.all(tasks)
  profileSaved.value = true
}

async function completeOnboarding() {
  const user = await fetchApi<typeof authStore.user>('/me', {
    method: 'PATCH',
    body: { onboarding_completed: true },
  })
  if (user) {
    authStore.setUser(user)
  }
}

async function goNext() {
  stepError.value = ''

  if (currentStep.value === 3 && !consentAccepted.value) {
    stepError.value = text.value.consentRequired
    return
  }

  isBusy.value = true
  try {
    if (currentStep.value === 4) {
      await saveInitialProfile()
    }

    if (currentStep.value === text.value.steps.length - 1) {
      await completeOnboarding()
      await router.push(chatPath.value)
      return
    }

    currentStep.value += 1
  } catch {
    stepError.value = text.value.saveError
  } finally {
    isBusy.value = false
  }
}
</script>