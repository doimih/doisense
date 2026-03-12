<template>
  <div class="-mt-6 pb-10">
    <header class="relative left-1/2 right-1/2 -mx-[50vw] w-screen overflow-hidden bg-[linear-gradient(130deg,#f8fafc_0%,#f5f3ff_45%,#f0f9ff_100%)]">
      <div class="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-sky-200/50 blur-3xl" />
      <div class="pointer-events-none absolute -bottom-20 left-10 h-48 w-48 rounded-full bg-amber-200/40 blur-3xl" />
      <div class="relative mx-auto max-w-[1440px] px-4 py-12 sm:px-6 md:py-16 lg:px-8">
        <div class="relative grid gap-7 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
          <div class="space-y-5">
            <p class="inline-flex items-center rounded-full border border-stone-300 bg-white/90 px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-stone-700">
              {{ text.badge }}
            </p>
            <h1 class="text-4xl font-bold leading-tight text-stone-900 md:text-6xl">{{ text.title }}</h1>
          </div>
          <p class="max-w-xl text-lg leading-8 text-stone-700 lg:ml-auto">{{ text.subtitle }}</p>
        </div>
      </div>
    </header>

    <div class="mx-auto max-w-7xl space-y-0 px-4 py-10 sm:px-6 lg:px-8">
    <section class="mt-[100px] mb-[100px] grid gap-6 lg:grid-cols-3">
      <article
        v-for="plan in displayedPlans"
        :key="plan.key"
        :class="[
          'relative rounded-3xl border p-6 shadow-sm transition-transform md:p-7',
          plan.key === 'premium'
            ? 'scale-[1.01] border-sky-300 bg-sky-50/80 shadow-[0_30px_80px_-45px_rgba(2,132,199,0.7)]'
            : plan.key === 'vip'
              ? 'border-amber-300 bg-amber-50/70'
              : 'border-stone-200 bg-white',
        ]"
      >
        <p
          v-if="plan.highlight"
          class="absolute -top-3 left-6 inline-flex rounded-full border border-sky-300 bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-sky-700"
        >
          {{ text.mostChosen }}
        </p>
        <p
          v-if="currentPlanKey === plan.key"
          class="absolute -top-3 right-6 inline-flex rounded-full border border-emerald-300 bg-emerald-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-emerald-700"
        >
          {{ text.currentPlan }}
        </p>

        <p class="text-sm font-semibold uppercase tracking-[0.12em] text-stone-500">{{ plan.tone }}</p>
        <h2 class="mt-2 text-2xl font-bold text-stone-900">{{ plan.title }}</h2>
        <p class="mt-3 text-sm leading-6 text-stone-700">{{ plan.description }}</p>

        <p
          v-if="plan.earlyAccessBadge"
          class="mt-4 inline-flex rounded-full border border-emerald-300 bg-emerald-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.11em] text-emerald-700"
        >
          {{ plan.earlyAccessBadge }}
        </p>

        <div class="mt-5 flex items-end gap-2 border-b border-stone-200 pb-5">
          <p v-if="plan.originalPrice" class="text-base font-semibold text-stone-400 line-through">{{ plan.originalPrice }}</p>
          <p class="text-5xl font-bold tracking-tight text-stone-900">{{ plan.price }}</p>
          <p class="pb-1 text-sm font-medium text-stone-600">{{ plan.period }}</p>
        </div>

        <ul class="mt-5 space-y-2.5 text-sm leading-6 text-stone-700">
          <li v-for="item in plan.items" :key="item" class="flex items-start gap-2">
            <span class="mt-[1px] text-emerald-600">✓</span>
            <span>{{ item }}</span>
          </li>
        </ul>

        <p
          v-if="plan.key === 'premium'"
          class="mt-5 rounded-xl border border-sky-200 bg-white px-4 py-3 text-sm font-medium leading-6 text-sky-900"
        >
          {{ text.premiumArgument }}
        </p>

        <button
          v-if="isLoggedIn"
          type="button"
          :disabled="loadingPlan === plan.key || currentPlanKey === plan.key"
          :class="[
            'mt-6 inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-semibold transition disabled:opacity-60',
            currentPlanKey === plan.key
              ? 'bg-emerald-600 text-white cursor-default'
              : plan.key === 'premium'
                ? 'bg-sky-600 text-white hover:bg-sky-700'
                : plan.key === 'vip'
                  ? 'bg-stone-900 text-white hover:bg-black'
                  : 'bg-white text-stone-900 border border-stone-300 hover:bg-stone-100',
          ]"
          @click="handlePlanAction(plan.key)"
        >
          {{ loadingPlan === plan.key ? loadingText : (currentPlanKey === plan.key ? text.currentPlan : plan.action) }}
        </button>
        <NuxtLink
          v-else
          :to="localePath('/auth/register')"
          :class="[
            'mt-6 inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-sm font-semibold transition',
            plan.key === 'premium'
              ? 'bg-sky-600 text-white hover:bg-sky-700'
              : plan.key === 'vip'
                ? 'bg-stone-900 text-white hover:bg-black'
                : 'bg-white text-stone-900 border border-stone-300 hover:bg-stone-100',
          ]"
        >
          {{ plan.action }}
        </NuxtLink>
      </article>
    </section>

    <section class="mb-10 overflow-hidden rounded-3xl border border-stone-200 bg-white">
      <div class="border-b border-stone-200 bg-stone-50 px-5 py-4">
        <h3 class="text-xl font-semibold text-stone-900">{{ text.comparisonTitle }}</h3>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full text-left text-sm">
          <thead class="bg-stone-50 text-stone-700">
            <tr>
              <th class="px-5 py-3 font-semibold">{{ text.tableFeature }}</th>
              <th class="px-5 py-3 text-center font-semibold">BASIC</th>
              <th class="px-5 py-3 text-center font-semibold text-sky-700">PREMIUM</th>
              <th class="px-5 py-3 text-center font-semibold">VIP</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in text.comparisonRows" :key="row.name" class="border-t border-stone-100">
              <td class="px-5 py-3 font-medium text-stone-800">{{ row.name }}</td>
              <td class="px-5 py-3 text-center" :class="row.basic ? 'text-emerald-600' : 'text-stone-300'">{{ row.basic ? '✓' : '—' }}</td>
              <td class="px-5 py-3 text-center" :class="row.premium ? 'text-emerald-600' : 'text-stone-300'">{{ row.premium ? '✓' : '—' }}</td>
              <td class="px-5 py-3 text-center" :class="row.vip ? 'text-emerald-600' : 'text-stone-300'">{{ row.vip ? '✓' : '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="my-10 grid gap-10 rounded-2xl border border-stone-200 bg-stone-50 p-4 font-semibold text-stone-700 sm:grid-cols-3">
      <p class="rounded-xl border border-stone-200 bg-white px-4 py-[35px] text-center text-[25px] leading-tight">{{ text.trust[0] }}</p>
      <p class="rounded-xl border border-stone-200 bg-white px-4 py-[35px] text-center text-[25px] leading-tight">{{ text.trust[1] }}</p>
      <p class="rounded-xl border border-stone-200 bg-white px-4 py-[35px] text-center text-[25px] leading-tight">{{ text.trust[2] }}</p>
    </section>

    <section class="rounded-3xl border border-stone-200 bg-[linear-gradient(135deg,#0f172a_0%,#1f2937_52%,#0b3b5b_100%)] px-6 py-10 text-white md:px-10">
      <div class="mx-auto max-w-3xl space-y-5 text-center">
        <h3 class="text-3xl font-bold leading-tight md:text-4xl">{{ text.finalTitle }}</h3>
        <p class="text-base leading-8 text-slate-200 md:text-lg">{{ text.finalSubtitle }}</p>
        <button
          v-if="isLoggedIn"
          type="button"
          :disabled="!!loadingPlan"
          class="inline-flex items-center justify-center rounded-full bg-white px-6 py-3 text-sm font-semibold text-stone-900 transition hover:bg-slate-100 disabled:opacity-50"
          @click="handlePlanAction('premium')"
        >
          {{ text.finalCta }}
        </button>
        <NuxtLink
          v-else
          :to="localePath('/auth/register')"
          class="inline-flex items-center justify-center rounded-full bg-white px-6 py-3 text-sm font-semibold text-stone-900 transition hover:bg-slate-100"
        >
          {{ text.finalCta }}
        </NuxtLink>
      </div>
    </section>
    </div>
  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const { locale } = useI18n()
const authStore = useAuthStore()
const { fetchApi } = useApi()

const isLoggedIn = computed(() => authStore.isLoggedIn)
const loadingPlan = ref<string | null>(null)
const loadingText = computed(() => {
  const code = localeCode.value
  const labels: Record<string, string> = { ro: 'Se procesează...', en: 'Processing...', de: 'Verarbeitung...', fr: 'En cours...', it: 'In elaborazione...', es: 'Procesando...', pl: 'Przetwarzanie...' }
  return labels[code] || 'Processing...'
})

const currentPlanKey = computed(() => {
  if (!isLoggedIn.value) return null
  const tier = authStore.user?.plan_tier
  if (!tier || tier === 'free' || tier === 'trial') return null
  if (tier === 'premium_discounted') return 'premium'
  return tier
})

const isEarlyDiscountEligible = computed(() => {
  return Boolean(isLoggedIn.value && authStore.user?.early_discount_eligible)
})

async function startCheckout(planKey: string) {
  loadingPlan.value = planKey
  try {
    const res = await fetchApi<{ url: string }>('/payments/create-checkout-session', {
      method: 'POST',
      body: { plan_tier: planKey },
    })
    if (res?.url) window.location.href = res.url
  } finally {
    loadingPlan.value = null
  }
}

async function upgradeSubscription(planKey: string) {
  loadingPlan.value = planKey
  try {
    await fetchApi('/payments/upgrade', {
      method: 'POST',
      body: { plan_tier: planKey },
    })
    const updated = await fetchApi<Record<string, unknown>>('/me')
    if (updated && authStore.user) {
      authStore.setUser({ ...authStore.user, ...updated } as typeof authStore.user)
    }
  } finally {
    loadingPlan.value = null
  }
}

async function handlePlanAction(planKey: string) {
  if (planKey === currentPlanKey.value) return
  if (currentPlanKey.value) {
    await upgradeSubscription(planKey)
  } else {
    await startCheckout(planKey)
  }
}

const localeCode = computed(() => {
  const code = (locale.value || 'ro').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'ro'
})

type Plan = {
  key: 'basic' | 'premium' | 'vip'
  tone: string
  title: string
  price: string
  period: string
  description: string
  items: string[]
  action: string
  highlight?: boolean
  originalPrice?: string
  earlyAccessBadge?: string
}

type ComparisonRow = {
  name: string
  basic: boolean
  premium: boolean
  vip: boolean
}

const pricingCopy: Record<string, {
  badge: string
  title: string
  subtitle: string
  mostChosen: string
  premiumArgument: string
  plans: Plan[]
  comparisonTitle: string
  tableFeature: string
  comparisonRows: ComparisonRow[]
  trust: string[]
  finalTitle: string
  finalSubtitle: string
  currentPlan: string
  finalCta: string
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    badge: 'Pachete premium pentru progres real',
    title: 'Alege claritatea de care ai nevoie pentru următorul tău nivel',
    subtitle: 'Doisense combină conversații AI, reflecție ghidată și planuri personalizate de wellbeing într-o experiență elegantă, ușor de urmat și orientată spre rezultate sustenabile.',
    mostChosen: 'Cel mai ales',
    premiumArgument: 'PREMIUM este alegerea ideală pentru ritm constant: suficient de profund pentru progres vizibil, fără complexitatea unui program exclusivist.',
    plans: [
      {
        key: 'basic',
        tone: 'Simplu și clar',
        title: 'BASIC Start',
        price: '59 lei',
        period: '/ lună',
        description: 'Un plan echilibrat pentru rutină de bază și claritate zilnică.',
        items: [
          'Conversații nelimitate în chatul AI',
          'Analiză emoțională simplă pentru fiecare interacțiune',
          'Întrebări de auto-reflecție pentru claritate personală',
          'Recomandări scurte pentru pași imediat aplicabili',
          'Jurnal personal pentru continuitate',
        ],
        action: 'Alege BASIC',
      },
      {
        key: 'premium',
        tone: 'Echilibru și consistență',
        title: 'PREMIUM Flow',
        price: '129 lei',
        period: '/ lună',
        description: 'Pentru cei care vor structură, ritm și evoluție clară de la o săptămână la alta.',
        items: [
          'Tot ce include BASIC',
          'Istoric conversațional extins pentru context mai bun',
          'Analiză emoțională avansată',
          'Plan zilnic personalizat',
          'Rapoarte zilnice și săptămânale',
          'Tipologie emoțională parțială',
        ],
        action: 'Alege PREMIUM',
        highlight: true,
      },
      {
        key: 'vip',
        tone: 'Exclusiv și strategic',
        title: 'VIP Executive',
        price: '249 lei',
        period: '/ lună',
        description: 'Un nivel premium complet pentru decizii strategice și progres pe termen lung.',
        items: [
          'Tot ce include PREMIUM',
          'Analiză emoțională profundă',
          'Tipologie emoțională completă',
          'Plan săptămânal și plan lunar',
          'Rapoarte lunare și recomandări strategice',
          'Analiză integrată pe 30 de zile',
        ],
        action: 'Alege VIP',
      },
    ],
    comparisonTitle: 'Compară rapid ce primești în fiecare plan',
    tableFeature: 'Funcționalitate',
    comparisonRows: [
      { name: 'Conversații nelimitate', basic: true, premium: true, vip: true },
      { name: 'Analiză emoțională simplă', basic: true, premium: true, vip: true },
      { name: 'Întrebări de auto-reflecție', basic: true, premium: true, vip: true },
      { name: 'Recomandări scurte', basic: true, premium: true, vip: true },
      { name: 'Jurnal personal', basic: true, premium: true, vip: true },
      { name: 'Istoric conversațional extins', basic: false, premium: true, vip: true },
      { name: 'Analiză emoțională avansată', basic: false, premium: true, vip: true },
      { name: 'Plan zilnic personalizat', basic: false, premium: true, vip: true },
      { name: 'Rapoarte zilnice', basic: false, premium: true, vip: true },
      { name: 'Rapoarte săptămânale', basic: false, premium: true, vip: true },
      { name: 'Tipologie emoțională parțială', basic: false, premium: true, vip: true },
      { name: 'Analiză emoțională profundă', basic: false, premium: false, vip: true },
      { name: 'Tipologie completă', basic: false, premium: false, vip: true },
      { name: 'Plan săptămânal', basic: false, premium: false, vip: true },
      { name: 'Plan lunar', basic: false, premium: false, vip: true },
      { name: 'Rapoarte lunare', basic: false, premium: false, vip: true },
      { name: 'Recomandări strategice', basic: false, premium: false, vip: true },
      { name: 'Analiză pe 30 de zile', basic: false, premium: false, vip: true },
    ],
    trust: ['Fără contracte', 'Poți anula oricând', 'Plăți securizate prin Stripe'],
    finalTitle: 'Wellbeing-ul tău merită un plan pe măsura obiectivelor tale',
    finalSubtitle: 'Începe cu pachetul care ți se potrivește acum și ajustează pe parcurs. Platforma crește odată cu tine, într-un ritm clar și sustenabil.',
    currentPlan: 'Planul tău actual',
    finalCta: 'Începe acum',
    seoTitle: 'Prețuri Doisense - BASIC, PREMIUM, VIP',
    seoDescription: 'Descoperă planurile Doisense pentru wellbeing AI: BASIC, PREMIUM și VIP, cu comparație completă și beneficii clare.',
  },
  en: {
    badge: 'Premium plans for meaningful progress',
    title: 'Choose the level of clarity that fits your next step',
    subtitle: 'Doisense combines AI conversations, guided reflection, and personalized wellbeing plans in a clear, elegant experience built for sustainable progress.',
    mostChosen: 'Most Chosen',
    premiumArgument: 'PREMIUM is the best balance for steady growth: deep enough to deliver visible progress without the complexity of an exclusive plan.',
    plans: [
      {
        key: 'basic',
        tone: 'Simple and practical',
        title: 'BASIC Start',
        price: '59 RON',
        period: '/ month',
        description: 'A clean starting plan for daily structure and emotional clarity.',
        items: [
          'Unlimited AI conversations',
          'Basic emotional analysis',
          'Self-reflection prompts',
          'Short recommendations',
          'Personal journal',
        ],
        action: 'Choose BASIC',
      },
      {
        key: 'premium',
        tone: 'Balanced and consistent',
        title: 'PREMIUM Flow',
        price: '129 RON',
        period: '/ month',
        description: 'Built for people who want rhythm, structure, and measurable weekly progress.',
        items: [
          'Everything in BASIC',
          'Extended conversation history',
          'Advanced emotional analysis',
          'Personalized daily plan',
          'Daily and weekly reports',
          'Partial emotional typology',
        ],
        action: 'Choose PREMIUM',
        highlight: true,
      },
      {
        key: 'vip',
        tone: 'Exclusive and strategic',
        title: 'VIP Executive',
        price: '249 RON',
        period: '/ month',
        description: 'A complete premium level for long-term strategic direction.',
        items: [
          'Everything in PREMIUM',
          'Deep emotional analysis',
          'Full emotional typology',
          'Weekly and monthly plans',
          'Monthly reports and strategic recommendations',
          'Integrated 30-day analysis',
        ],
        action: 'Choose VIP',
      },
    ],
    comparisonTitle: 'Compare what is included in each plan',
    tableFeature: 'Feature',
    comparisonRows: [
      { name: 'Unlimited conversations', basic: true, premium: true, vip: true },
      { name: 'Basic emotional analysis', basic: true, premium: true, vip: true },
      { name: 'Self-reflection prompts', basic: true, premium: true, vip: true },
      { name: 'Short recommendations', basic: true, premium: true, vip: true },
      { name: 'Personal journal', basic: true, premium: true, vip: true },
      { name: 'Extended conversation history', basic: false, premium: true, vip: true },
      { name: 'Advanced emotional analysis', basic: false, premium: true, vip: true },
      { name: 'Personalized daily plan', basic: false, premium: true, vip: true },
      { name: 'Daily reports', basic: false, premium: true, vip: true },
      { name: 'Weekly reports', basic: false, premium: true, vip: true },
      { name: 'Partial emotional typology', basic: false, premium: true, vip: true },
      { name: 'Deep emotional analysis', basic: false, premium: false, vip: true },
      { name: 'Full emotional typology', basic: false, premium: false, vip: true },
      { name: 'Weekly plan', basic: false, premium: false, vip: true },
      { name: 'Monthly plan', basic: false, premium: false, vip: true },
      { name: 'Monthly reports', basic: false, premium: false, vip: true },
      { name: 'Strategic recommendations', basic: false, premium: false, vip: true },
      { name: '30-day analysis', basic: false, premium: false, vip: true },
    ],
    trust: ['No contracts', 'Cancel anytime', 'Secure payments via Stripe'],
    finalTitle: 'Your wellbeing deserves a plan aligned with your goals',
    finalSubtitle: 'Start with the package that fits your current rhythm and upgrade whenever you need more depth.',
    currentPlan: 'Current Plan',
    finalCta: 'Start now',
    seoTitle: 'Doisense Pricing - BASIC, PREMIUM, VIP',
    seoDescription: 'Explore Doisense AI wellbeing plans with full comparison: BASIC, PREMIUM, and VIP.',
  },
  de: {
    badge: 'Premium-Pläne für echten Fortschritt',
    title: 'Wähle die Klarheit, die zu deinem nächsten Schritt passt',
    subtitle: 'Doisense verbindet KI-Gespräche, geführte Selbstreflexion und personalisierte Wellbeing-Pläne in einer eleganten Erfahrung für nachhaltigen Fortschritt.',
    mostChosen: 'Am häufigsten gewählt',
    currentPlan: 'Aktueller Plan',
    premiumArgument: 'PREMIUM ist die beste Balance für stetiges Wachstum: tiefgründig genug für sichtbaren Fortschritt, ohne die Komplexität eines exklusiven Plans.',
    plans: [
      {
        key: 'basic',
        tone: 'Einfach und klar',
        title: 'BASIC Start',
        price: '59 RON',
        period: '/ Monat',
        description: 'Ein ausgewogener Plan für Grundroutine und tägliche Klarheit.',
        items: [
          'Unbegrenzte KI-Gespräche',
          'Einfache emotionale Analyse',
          'Selbstreflexionsfragen',
          'Kurze Empfehlungen',
          'Persönliches Tagebuch',
        ],
        action: 'BASIC wählen',
      },
      {
        key: 'premium',
        tone: 'Balance und Konsistenz',
        title: 'PREMIUM Flow',
        price: '129 RON',
        period: '/ Monat',
        description: 'Für alle, die Struktur, Rhythmus und klaren wöchentlichen Fortschritt wollen.',
        items: [
          'Alles in BASIC',
          'Erweiterte Gesprächshistorie',
          'Erweiterte emotionale Analyse',
          'Personalisierter Tagesplan',
          'Tages- und Wochenberichte',
          'Partielle emotionale Typologie',
        ],
        action: 'PREMIUM wählen',
        highlight: true,
      },
      {
        key: 'vip',
        tone: 'Exklusiv und strategisch',
        title: 'VIP Executive',
        price: '249 RON',
        period: '/ Monat',
        description: 'Ein vollständiges Premium-Niveau für strategische Ausrichtung und langfristiges Wachstum.',
        items: [
          'Alles in PREMIUM',
          'Tiefe emotionale Analyse',
          'Vollständige emotionale Typologie',
          'Wochen- und Monatspläne',
          'Monatsberichte und strategische Empfehlungen',
          'Integrierte 30-Tage-Analyse',
        ],
        action: 'VIP wählen',
      },
    ],
    comparisonTitle: 'Vergleiche, was in jedem Plan enthalten ist',
    tableFeature: 'Funktion',
    comparisonRows: [
      { name: 'Unbegrenzte Gespräche', basic: true, premium: true, vip: true },
      { name: 'Einfache emotionale Analyse', basic: true, premium: true, vip: true },
      { name: 'Selbstreflexionsfragen', basic: true, premium: true, vip: true },
      { name: 'Kurze Empfehlungen', basic: true, premium: true, vip: true },
      { name: 'Persönliches Tagebuch', basic: true, premium: true, vip: true },
      { name: 'Erweiterte Gesprächshistorie', basic: false, premium: true, vip: true },
      { name: 'Erweiterte emotionale Analyse', basic: false, premium: true, vip: true },
      { name: 'Personalisierter Tagesplan', basic: false, premium: true, vip: true },
      { name: 'Tagesberichte', basic: false, premium: true, vip: true },
      { name: 'Wochenberichte', basic: false, premium: true, vip: true },
      { name: 'Partielle emotionale Typologie', basic: false, premium: true, vip: true },
      { name: 'Tiefe emotionale Analyse', basic: false, premium: false, vip: true },
      { name: 'Vollständige emotionale Typologie', basic: false, premium: false, vip: true },
      { name: 'Wochenplan', basic: false, premium: false, vip: true },
      { name: 'Monatsplan', basic: false, premium: false, vip: true },
      { name: 'Monatsberichte', basic: false, premium: false, vip: true },
      { name: 'Strategische Empfehlungen', basic: false, premium: false, vip: true },
      { name: '30-Tage-Analyse', basic: false, premium: false, vip: true },
    ],
    trust: ['Keine Verträge', 'Jederzeit kündbar', 'Sichere Zahlungen über Stripe'],
    finalTitle: 'Dein Wohlbefinden verdient einen Plan, der zu deinen Zielen passt',
    finalSubtitle: 'Starte mit dem Paket, das zu deinem aktuellen Rhythmus passt, und erweitere es jederzeit.',
    finalCta: 'Jetzt starten',
    seoTitle: 'Doisense Preise - BASIC, PREMIUM, VIP',
    seoDescription: 'Entdecke Doisense KI-Wellbeing-Pläne mit vollständigem Vergleich: BASIC, PREMIUM und VIP.',
  },
  fr: {
    badge: 'Des plans premium pour un progrès concret',
    title: 'Choisis le niveau de clarté adapté à ta prochaine étape',
    subtitle: "Doisense combine conversations IA, réflexion guidée et plans de bien-être personnalisés dans une expérience claire et élégante orientée vers des résultats durables.",
    mostChosen: 'Le plus choisi',
    currentPlan: 'Plan actuel',
    premiumArgument: "PREMIUM est le meilleur équilibre pour une croissance constante : suffisamment profond pour des progrès visibles, sans la complexité d'un programme exclusif.",
    plans: [
      {
        key: 'basic',
        tone: 'Simple et pratique',
        title: 'BASIC Start',
        price: '59 RON',
        period: '/ mois',
        description: 'Un plan équilibré pour une routine de base et une clarté quotidienne.',
        items: [
          'Conversations IA illimitées',
          'Analyse émotionnelle simple',
          "Questions d'auto-réflexion",
          'Recommandations courtes',
          'Journal personnel',
        ],
        action: 'Choisir BASIC',
      },
      {
        key: 'premium',
        tone: 'Équilibre et régularité',
        title: 'PREMIUM Flow',
        price: '129 RON',
        period: '/ mois',
        description: 'Pour ceux qui veulent structure, rythme et progression hebdomadaire mesurable.',
        items: [
          'Tout ce que BASIC inclut',
          'Historique de conversations étendu',
          'Analyse émotionnelle avancée',
          'Plan quotidien personnalisé',
          'Rapports quotidiens et hebdomadaires',
          'Typologie émotionnelle partielle',
        ],
        action: 'Choisir PREMIUM',
        highlight: true,
      },
      {
        key: 'vip',
        tone: 'Exclusif et stratégique',
        title: 'VIP Executive',
        price: '249 RON',
        period: '/ mois',
        description: 'Un niveau premium complet pour une orientation stratégique et un progrès à long terme.',
        items: [
          'Tout ce que PREMIUM inclut',
          'Analyse émotionnelle profonde',
          'Typologie émotionnelle complète',
          'Plans hebdomadaires et mensuels',
          'Rapports mensuels et recommandations stratégiques',
          'Analyse intégrée sur 30 jours',
        ],
        action: 'Choisir VIP',
      },
    ],
    comparisonTitle: 'Compare ce qui est inclus dans chaque plan',
    tableFeature: 'Fonctionnalité',
    comparisonRows: [
      { name: 'Conversations illimitées', basic: true, premium: true, vip: true },
      { name: 'Analyse émotionnelle simple', basic: true, premium: true, vip: true },
      { name: "Questions d'auto-réflexion", basic: true, premium: true, vip: true },
      { name: 'Recommandations courtes', basic: true, premium: true, vip: true },
      { name: 'Journal personnel', basic: true, premium: true, vip: true },
      { name: 'Historique de conversations étendu', basic: false, premium: true, vip: true },
      { name: 'Analyse émotionnelle avancée', basic: false, premium: true, vip: true },
      { name: 'Plan quotidien personnalisé', basic: false, premium: true, vip: true },
      { name: 'Rapports quotidiens', basic: false, premium: true, vip: true },
      { name: 'Rapports hebdomadaires', basic: false, premium: true, vip: true },
      { name: 'Typologie émotionnelle partielle', basic: false, premium: true, vip: true },
      { name: 'Analyse émotionnelle profonde', basic: false, premium: false, vip: true },
      { name: 'Typologie émotionnelle complète', basic: false, premium: false, vip: true },
      { name: 'Plan hebdomadaire', basic: false, premium: false, vip: true },
      { name: 'Plan mensuel', basic: false, premium: false, vip: true },
      { name: 'Rapports mensuels', basic: false, premium: false, vip: true },
      { name: 'Recommandations stratégiques', basic: false, premium: false, vip: true },
      { name: 'Analyse sur 30 jours', basic: false, premium: false, vip: true },
    ],
    trust: ['Sans contrats', 'Résiliable à tout moment', 'Paiements sécurisés via Stripe'],
    finalTitle: 'Ton bien-être mérite un plan à la hauteur de tes objectifs',
    finalSubtitle: "Commence avec le forfait qui correspond à ton rythme actuel et adapte-le au fil du temps.",
    finalCta: 'Commencer maintenant',
    seoTitle: 'Prix Doisense - BASIC, PREMIUM, VIP',
    seoDescription: 'Découvre les plans de bien-être IA Doisense avec une comparaison complète : BASIC, PREMIUM et VIP.',
  },
  it: {
    badge: 'Piani premium per un progresso concreto',
    title: 'Scegli il livello di chiarezza adatto al tuo prossimo passo',
    subtitle: 'Doisense combina conversazioni AI, riflessione guidata e piani di benessere personalizzati in un\u2019esperienza elegante orientata a risultati sostenibili.',
    mostChosen: 'Il più scelto',
    currentPlan: 'Piano attuale',
    premiumArgument: 'PREMIUM è il miglior equilibrio per una crescita costante: abbastanza profondo per progressi visibili, senza la complessità di un programma esclusivo.',
    plans: [
      {
        key: 'basic',
        tone: 'Semplice e chiaro',
        title: 'BASIC Start',
        price: '59 RON',
        period: '/ mese',
        description: 'Un piano equilibrato per una routine di base e chiarezza quotidiana.',
        items: [
          'Conversazioni AI illimitate',
          'Analisi emotiva semplice',
          'Domande di auto-riflessione',
          'Raccomandazioni brevi',
          'Diario personale',
        ],
        action: 'Scegli BASIC',
      },
      {
        key: 'premium',
        tone: 'Equilibrio e costanza',
        title: 'PREMIUM Flow',
        price: '129 RON',
        period: '/ mese',
        description: 'Per chi vuole struttura, ritmo e progressi settimanali misurabili.',
        items: [
          'Tutto ciò che include BASIC',
          'Cronologia delle conversazioni estesa',
          'Analisi emotiva avanzata',
          'Piano giornaliero personalizzato',
          'Report giornalieri e settimanali',
          'Tipologia emotiva parziale',
        ],
        action: 'Scegli PREMIUM',
        highlight: true,
      },
      {
        key: 'vip',
        tone: 'Esclusivo e strategico',
        title: 'VIP Executive',
        price: '249 RON',
        period: '/ mese',
        description: 'Un livello premium completo per una direzione strategica e una crescita a lungo termine.',
        items: [
          'Tutto ciò che include PREMIUM',
          'Analisi emotiva profonda',
          'Tipologia emotiva completa',
          'Piani settimanali e mensili',
          'Report mensili e raccomandazioni strategiche',
          'Analisi integrata su 30 giorni',
        ],
        action: 'Scegli VIP',
      },
    ],
    comparisonTitle: 'Confronta cosa è incluso in ogni piano',
    tableFeature: 'Funzionalità',
    comparisonRows: [
      { name: 'Conversazioni illimitate', basic: true, premium: true, vip: true },
      { name: 'Analisi emotiva semplice', basic: true, premium: true, vip: true },
      { name: 'Domande di auto-riflessione', basic: true, premium: true, vip: true },
      { name: 'Raccomandazioni brevi', basic: true, premium: true, vip: true },
      { name: 'Diario personale', basic: true, premium: true, vip: true },
      { name: 'Cronologia conversazioni estesa', basic: false, premium: true, vip: true },
      { name: 'Analisi emotiva avanzata', basic: false, premium: true, vip: true },
      { name: 'Piano giornaliero personalizzato', basic: false, premium: true, vip: true },
      { name: 'Report giornalieri', basic: false, premium: true, vip: true },
      { name: 'Report settimanali', basic: false, premium: true, vip: true },
      { name: 'Tipologia emotiva parziale', basic: false, premium: true, vip: true },
      { name: 'Analisi emotiva profonda', basic: false, premium: false, vip: true },
      { name: 'Tipologia emotiva completa', basic: false, premium: false, vip: true },
      { name: 'Piano settimanale', basic: false, premium: false, vip: true },
      { name: 'Piano mensile', basic: false, premium: false, vip: true },
      { name: 'Report mensili', basic: false, premium: false, vip: true },
      { name: 'Raccomandazioni strategiche', basic: false, premium: false, vip: true },
      { name: 'Analisi su 30 giorni', basic: false, premium: false, vip: true },
    ],
    trust: ['Nessun contratto', 'Annullabile in qualsiasi momento', 'Pagamenti sicuri tramite Stripe'],
    finalTitle: 'Il tuo benessere merita un piano all\u2019altezza dei tuoi obiettivi',
    finalSubtitle: 'Inizia con il pacchetto che si adatta al tuo ritmo attuale e aggiornalo quando vuoi.',
    finalCta: 'Inizia ora',
    seoTitle: 'Prezzi Doisense - BASIC, PREMIUM, VIP',
    seoDescription: 'Scopri i piani di benessere AI Doisense con confronto completo: BASIC, PREMIUM e VIP.',
  },
  es: {
    badge: 'Planes premium para un progreso real',
    title: 'Elige el nivel de claridad que se adapta a tu próximo paso',
    subtitle: 'Doisense combina conversaciones IA, reflexión guiada y planes de bienestar personalizados en una experiencia elegante orientada a resultados sostenibles.',
    mostChosen: 'El más elegido',
    currentPlan: 'Plan actual',
    premiumArgument: 'PREMIUM es el mejor equilibrio para un crecimiento constante: lo suficientemente profundo para un progreso visible, sin la complejidad de un programa exclusivo.',
    plans: [
      {
        key: 'basic',
        tone: 'Simple y claro',
        title: 'BASIC Start',
        price: '59 RON',
        period: '/ mes',
        description: 'Un plan equilibrado para una rutina básica y claridad diaria.',
        items: [
          'Conversaciones IA ilimitadas',
          'Análisis emocional simple',
          'Preguntas de auto-reflexión',
          'Recomendaciones cortas',
          'Diario personal',
        ],
        action: 'Elegir BASIC',
      },
      {
        key: 'premium',
        tone: 'Equilibrio y consistencia',
        title: 'PREMIUM Flow',
        price: '129 RON',
        period: '/ mes',
        description: 'Para quienes quieren estructura, ritmo y progreso semanal medible.',
        items: [
          'Todo lo que incluye BASIC',
          'Historial de conversaciones extendido',
          'Análisis emocional avanzado',
          'Plan diario personalizado',
          'Informes diarios y semanales',
          'Tipología emocional parcial',
        ],
        action: 'Elegir PREMIUM',
        highlight: true,
      },
      {
        key: 'vip',
        tone: 'Exclusivo y estratégico',
        title: 'VIP Executive',
        price: '249 RON',
        period: '/ mes',
        description: 'Un nivel premium completo para una dirección estratégica y un progreso a largo plazo.',
        items: [
          'Todo lo que incluye PREMIUM',
          'Análisis emocional profundo',
          'Tipología emocional completa',
          'Planes semanales y mensuales',
          'Informes mensuales y recomendaciones estratégicas',
          'Análisis integrado de 30 días',
        ],
        action: 'Elegir VIP',
      },
    ],
    comparisonTitle: 'Compara lo que incluye cada plan',
    tableFeature: 'Funcionalidad',
    comparisonRows: [
      { name: 'Conversaciones ilimitadas', basic: true, premium: true, vip: true },
      { name: 'Análisis emocional simple', basic: true, premium: true, vip: true },
      { name: 'Preguntas de auto-reflexión', basic: true, premium: true, vip: true },
      { name: 'Recomendaciones cortas', basic: true, premium: true, vip: true },
      { name: 'Diario personal', basic: true, premium: true, vip: true },
      { name: 'Historial de conversaciones extendido', basic: false, premium: true, vip: true },
      { name: 'Análisis emocional avanzado', basic: false, premium: true, vip: true },
      { name: 'Plan diario personalizado', basic: false, premium: true, vip: true },
      { name: 'Informes diarios', basic: false, premium: true, vip: true },
      { name: 'Informes semanales', basic: false, premium: true, vip: true },
      { name: 'Tipología emocional parcial', basic: false, premium: true, vip: true },
      { name: 'Análisis emocional profundo', basic: false, premium: false, vip: true },
      { name: 'Tipología emocional completa', basic: false, premium: false, vip: true },
      { name: 'Plan semanal', basic: false, premium: false, vip: true },
      { name: 'Plan mensual', basic: false, premium: false, vip: true },
      { name: 'Informes mensuales', basic: false, premium: false, vip: true },
      { name: 'Recomendaciones estratégicas', basic: false, premium: false, vip: true },
      { name: 'Análisis de 30 días', basic: false, premium: false, vip: true },
    ],
    trust: ['Sin contratos', 'Cancela cuando quieras', 'Pagos seguros a través de Stripe'],
    finalTitle: 'Tu bienestar merece un plan a la altura de tus objetivos',
    finalSubtitle: 'Empieza con el paquete que se adapta a tu ritmo actual y actualízalo cuando lo necesites.',
    finalCta: 'Empezar ahora',
    seoTitle: 'Precios Doisense - BASIC, PREMIUM, VIP',
    seoDescription: 'Descubre los planes de bienestar IA de Doisense con comparación completa: BASIC, PREMIUM y VIP.',
  },
  pl: {
    badge: 'Plany premium dla realnego postępu',
    title: 'Wybierz poziom jasności odpowiedni do Twojego kolejnego kroku',
    subtitle: 'Doisense łączy rozmowy z AI, ukierunkowaną refleksję i spersonalizowane plany wellness w eleganckim doświadczeniu zorientowanym na trwałe rezultaty.',
    mostChosen: 'Najczęściej wybierany',
    currentPlan: 'Aktualny plan',
    premiumArgument: 'PREMIUM to najlepsza równowaga dla stałego wzrostu: wystarczająco głęboki, by zapewnić widoczne postępy, bez złożoności ekskluzywnego programu.',
    plans: [
      {
        key: 'basic',
        tone: 'Prosty i przejrzysty',
        title: 'BASIC Start',
        price: '59 RON',
        period: '/ miesiąc',
        description: 'Zrównoważony plan dla podstawowej rutyny i codziennej jasności.',
        items: [
          'Nieograniczone rozmowy z AI',
          'Prosta analiza emocjonalna',
          'Pytania do autorefleksji',
          'Krótkie rekomendacje',
          'Osobisty dziennik',
        ],
        action: 'Wybierz BASIC',
      },
      {
        key: 'premium',
        tone: 'Równowaga i konsekwencja',
        title: 'PREMIUM Flow',
        price: '129 RON',
        period: '/ miesiąc',
        description: 'Dla osób, które chcą struktury, rytmu i mierzalnego tygodniowego postępu.',
        items: [
          'Wszystko z BASIC',
          'Rozszerzona historia rozmów',
          'Zaawansowana analiza emocjonalna',
          'Spersonalizowany plan dzienny',
          'Raporty dzienne i tygodniowe',
          'Częściowa typologia emocjonalna',
        ],
        action: 'Wybierz PREMIUM',
        highlight: true,
      },
      {
        key: 'vip',
        tone: 'Ekskluzywny i strategiczny',
        title: 'VIP Executive',
        price: '249 RON',
        period: '/ miesiąc',
        description: 'Kompletny poziom premium dla strategicznego kierunku i długoterminowego wzrostu.',
        items: [
          'Wszystko z PREMIUM',
          'Głęboka analiza emocjonalna',
          'Kompletna typologia emocjonalna',
          'Plany tygodniowe i miesięczne',
          'Raporty miesięczne i rekomendacje strategiczne',
          'Zintegrowana analiza 30-dniowa',
        ],
        action: 'Wybierz VIP',
      },
    ],
    comparisonTitle: 'Porównaj, co jest zawarte w każdym planie',
    tableFeature: 'Funkcja',
    comparisonRows: [
      { name: 'Nieograniczone rozmowy', basic: true, premium: true, vip: true },
      { name: 'Prosta analiza emocjonalna', basic: true, premium: true, vip: true },
      { name: 'Pytania do autorefleksji', basic: true, premium: true, vip: true },
      { name: 'Krótkie rekomendacje', basic: true, premium: true, vip: true },
      { name: 'Osobisty dziennik', basic: true, premium: true, vip: true },
      { name: 'Rozszerzona historia rozmów', basic: false, premium: true, vip: true },
      { name: 'Zaawansowana analiza emocjonalna', basic: false, premium: true, vip: true },
      { name: 'Spersonalizowany plan dzienny', basic: false, premium: true, vip: true },
      { name: 'Raporty dzienne', basic: false, premium: true, vip: true },
      { name: 'Raporty tygodniowe', basic: false, premium: true, vip: true },
      { name: 'Częściowa typologia emocjonalna', basic: false, premium: true, vip: true },
      { name: 'Głęboka analiza emocjonalna', basic: false, premium: false, vip: true },
      { name: 'Kompletna typologia emocjonalna', basic: false, premium: false, vip: true },
      { name: 'Plan tygodniowy', basic: false, premium: false, vip: true },
      { name: 'Plan miesięczny', basic: false, premium: false, vip: true },
      { name: 'Raporty miesięczne', basic: false, premium: false, vip: true },
      { name: 'Rekomendacje strategiczne', basic: false, premium: false, vip: true },
      { name: 'Analiza 30-dniowa', basic: false, premium: false, vip: true },
    ],
    trust: ['Bez umów', 'Anuluj w dowolnym momencie', 'Bezpieczne płatności przez Stripe'],
    finalTitle: 'Twój dobrostan zasługuje na plan dopasowany do Twoich celów',
    finalSubtitle: 'Zacznij od pakietu odpowiadającego Twojemu obecnemu rytmowi i ulepszaj go w razie potrzeby.',
    finalCta: 'Zacznij teraz',
    seoTitle: 'Cennik Doisense - BASIC, PREMIUM, VIP',
    seoDescription: 'Odkryj plany wellness AI Doisense z pełnym porównaniem: BASIC, PREMIUM i VIP.',
  },
}

const text = computed(() => pricingCopy[localeCode.value] || pricingCopy.ro)
const displayedPlans = computed<Plan[]>(() => {
  const plans = text.value.plans.map((plan) => ({ ...plan }))
  if (!isEarlyDiscountEligible.value) {
    return plans
  }

  return plans.map((plan) => {
    if (plan.key !== 'premium') {
      return plan
    }

    return {
      ...plan,
      originalPrice: plan.price,
      price: localeCode.value === 'ro' ? '116.10 lei' : '116.10 RON',
      earlyAccessBadge: localeCode.value === 'ro'
        ? 'Reducere Early Access -10%'
        : 'Early Access Discount -10%',
    }
  })
})
const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
