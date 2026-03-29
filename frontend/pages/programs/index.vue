<template>
  <div class="programs-page mx-auto max-w-6xl">
    <div v-if="authNotice" class="mb-6 rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ authNotice }}
    </div>

    <section class="programs-hero">
      <div>
        <p class="programs-eyebrow">Programe ghidate</p>
        <h1 class="programs-title">Planuri scurte, clare si compatibile cu calendarul tau zilnic.</h1>
        <p class="programs-subtitle">
          BASIC poate explora programele de baza. PREMIUM activeaza programe si genereaza task-uri in calendar. VIP primeste
          si recomandari adaptive zilnice.
        </p>
      </div>
      <div class="programs-hero-chip">
        <span>Plan activ</span>
        <strong>{{ userPlanLabel }}</strong>
      </div>
    </section>

    <section v-if="activeProgram" class="active-program-panel">
      <div>
        <p class="active-program-label">Program activ</p>
        <h2 class="active-program-title">{{ activeProgram.program.title }}</h2>
        <p class="active-program-copy">
          Ziua {{ activeProgram.activation.progress_day }} din {{ activeProgram.program.duration_days }}
          <span v-if="activeProgram.current_step">· {{ activeProgram.current_step.title }}</span>
        </p>
      </div>
      <NuxtLink :to="localePath(`/programs/${activeProgram.program.id}`)" class="active-program-link">
        Continua programul
      </NuxtLink>
    </section>

    <section v-if="hasCmsContent && cmsPage" class="mb-8 rounded-2xl border border-stone-200 bg-white/80 p-5">
      <h2 class="text-lg font-semibold text-stone-900">{{ cmsPage.title }}</h2>
      <p class="mt-2 whitespace-pre-line text-sm leading-7 text-stone-600">{{ cmsPage.content }}</p>
    </section>

    <div class="programs-filter-bar">
      <button
        v-for="item in categories"
        :key="item.value"
        type="button"
        class="programs-filter-chip"
        :class="item.value === selectedCategory ? 'programs-filter-chip-active' : ''"
        @click="selectedCategory = item.value"
      >
        {{ item.label }}
      </button>
    </div>

    <p v-if="loading" class="text-stone-500">{{ $t('common.loading') }}</p>

    <div v-else class="space-y-10">
      <section v-for="group in groupedPrograms" :key="group.category" class="space-y-4">
        <div class="flex items-end justify-between gap-4">
          <div>
            <p class="programs-section-kicker">Categorie</p>
            <h2 class="programs-section-title">{{ group.meta.title }}</h2>
          </div>
          <p class="text-sm text-stone-500">{{ group.items.length }} programe</p>
        </div>
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <ProgramCard v-for="program in group.items" :key="program.id" :program="program" />
        </div>
      </section>

      <section v-if="!groupedPrograms.length" class="rounded-2xl border border-dashed border-stone-300 bg-white px-6 py-10 text-center text-sm text-stone-500">
        Nu exista programe disponibile pentru filtrul selectat.
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'subscription'] as any })

const { fetchApi } = useApi()
const { locale } = useI18n()
const route = useRoute()
const localePath = useLocalePath()
const auth = useAuthStore()
const { cmsPage, hasCmsContent } = useCmsStaticPage('programs')

type ProgramActivation = {
  progress_day: number
  status: string
}

type ProgramItem = {
  id: number
  category: string
  category_meta: { title: string; icon: string }
  title: string
  description: string
  duration_days: number
  plan_access: 'basic' | 'premium' | 'vip'
  can_activate: boolean
  activation?: ProgramActivation | null
}

type ActiveProgramPayload = {
  item: null | {
    program: ProgramItem
    activation: ProgramActivation
    current_step: { day_number: number; title: string } | null
  }
}

const programs = ref<ProgramItem[]>([])
const activeProgram = ref<ActiveProgramPayload['item']>(null)
const loading = ref(true)
const authNotice = ref('')
const selectedCategory = ref<'all' | 'wellness' | 'coaching' | 'educatie' | 'suport'>('all')

const categories = [
  { value: 'all', label: 'Toate' },
  { value: 'wellness', label: 'Wellness' },
  { value: 'coaching', label: 'Coaching' },
  { value: 'educatie', label: 'Educatie' },
  { value: 'suport', label: 'Suport' },
] as const

const sessionExpiredMessage = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return {
    ro: 'Sesiunea ta a expirat. Te rugam sa te autentifici din nou.',
    en: 'Your session expired. Please sign in again.',
    de: 'Deine Sitzung ist abgelaufen. Bitte melde dich erneut an.',
    fr: 'Votre session a expire. Veuillez vous reconnecter.',
    it: 'La tua sessione e scaduta. Effettua nuovamente il login.',
    es: 'Tu sesion expiro. Inicia sesion nuevamente.',
    pl: 'Twoja sesja wygasla. Zaloguj sie ponownie.',
  }[code] || 'Your session expired. Please sign in again.'
})

const userPlanLabel = computed(() => {
  const tier = auth.user?.plan_tier || 'free'
  if (auth.user?.is_staff || auth.user?.is_superuser || tier === 'vip') return 'VIP Executive'
  if (tier === 'premium' || tier === 'premium_discounted') return 'PREMIUM Flow'
  if (tier === 'basic' || tier === 'trial') return 'BASIC Start'
  return 'Fara plan activ'
})

const groupedPrograms = computed(() => {
  const filtered = selectedCategory.value === 'all'
    ? programs.value
    : programs.value.filter(program => program.category === selectedCategory.value)

  const grouped = new Map<string, { category: string; meta: { title: string; icon: string }; items: ProgramItem[] }>()
  for (const program of filtered) {
    if (!grouped.has(program.category)) {
      grouped.set(program.category, {
        category: program.category,
        meta: program.category_meta,
        items: [],
      })
    }
    grouped.get(program.category)?.items.push(program)
  }
  return Array.from(grouped.values())
})

function isUnauthorized(error: unknown): boolean {
  const status = (error as { statusCode?: number; response?: { status?: number } })?.statusCode
    ?? (error as { response?: { status?: number } })?.response?.status
  return status === 401
}

usePublicSeo({
  title: 'Programe ghidate - Doisense',
  description: 'Catalogul programelor ghidate conectate la calendar si task-uri.',
  noindex: true,
})

async function loadPrograms() {
  const lang = locale.value || auth.user?.language || 'ro'
  const response = await fetchApi<{ items: ProgramItem[] }>(`/programs?language=${lang}`)
  programs.value = response.items || []
}

async function loadActiveProgram() {
  const response = await fetchApi<ActiveProgramPayload>('/programs/active')
  activeProgram.value = response.item
}

onMounted(async () => {
  try {
    await Promise.all([loadPrograms(), loadActiveProgram()])
  } catch (error) {
    if (isUnauthorized(error)) {
      authNotice.value = sessionExpiredMessage.value
      await navigateTo({
        path: localePath('/auth/login'),
        query: {
          reason: 'session_expired',
          next: route.fullPath,
        },
      })
      return
    }
    programs.value = []
    activeProgram.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.programs-page {
  padding-bottom: 40px;
}

.programs-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 24px;
  align-items: end;
  margin-bottom: 24px;
  padding: 28px;
  border-radius: 28px;
  background:
    linear-gradient(135deg, rgba(247, 242, 225, 0.95), rgba(235, 245, 238, 0.96)),
    linear-gradient(180deg, #ffffff, #ffffff);
  border: 1px solid #dbe5de;
}

.programs-eyebrow {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.24em;
  color: #728379;
}

.programs-title {
  margin-top: 8px;
  max-width: 760px;
  font-size: clamp(30px, 5vw, 52px);
  line-height: 0.96;
  font-weight: 700;
  color: #21362d;
}

.programs-subtitle {
  margin-top: 14px;
  max-width: 720px;
  font-size: 15px;
  line-height: 1.7;
  color: #5d7065;
}

.programs-hero-chip {
  display: grid;
  gap: 6px;
  min-width: 180px;
  border-radius: 18px;
  padding: 16px 18px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #d6e1d9;
  color: #61746a;
}

.programs-hero-chip span {
  font-size: 10px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.programs-hero-chip strong {
  font-size: 16px;
  color: #20352c;
}

.active-program-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
  border-radius: 24px;
  padding: 20px 22px;
  background: #1f352b;
  color: white;
}

.active-program-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: rgba(255, 255, 255, 0.62);
}

.active-program-title {
  margin-top: 4px;
  font-size: 24px;
  font-weight: 700;
}

.active-program-copy {
  margin-top: 6px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.78);
}

.active-program-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  border-radius: 999px;
  background: #f5c86f;
  padding: 0 18px;
  font-size: 13px;
  font-weight: 700;
  color: #2e2410;
}

.programs-filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
}

.programs-filter-chip {
  border: 1px solid #d5ded8;
  border-radius: 999px;
  background: white;
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #607167;
}

.programs-filter-chip-active {
  background: #22372e;
  border-color: #22372e;
  color: white;
}

.programs-section-kicker {
  font-size: 10px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #7c8b83;
}

.programs-section-title {
  margin-top: 6px;
  font-size: 26px;
  font-weight: 700;
  color: #23372d;
}

@media (max-width: 900px) {
  .programs-hero,
  .active-program-panel {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
