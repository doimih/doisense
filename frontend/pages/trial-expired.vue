<template>
  <div class="mx-auto max-w-2xl space-y-8 px-4 py-16 text-center sm:px-6">
    <div class="space-y-3">
      <div class="inline-flex items-center justify-center rounded-full border border-amber-300 bg-amber-50 p-4 text-amber-600">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h1 class="text-3xl font-bold text-stone-900">{{ text.title }}</h1>
      <p class="mx-auto max-w-md text-base leading-7 text-stone-600">{{ text.subtitle }}</p>
    </div>

    <div class="grid gap-4 sm:grid-cols-3">
      <article
        v-for="plan in text.plans"
        :key="plan.key"
        :class="[
          'rounded-2xl border p-5 text-left shadow-sm',
          plan.key === 'premium'
            ? 'border-sky-300 bg-sky-50/80 shadow-[0_20px_60px_-30px_rgba(2,132,199,0.5)]'
            : plan.key === 'vip'
              ? 'border-amber-300 bg-amber-50/70'
              : 'border-stone-200 bg-white',
        ]"
      >
        <p class="text-xs font-semibold uppercase tracking-wider text-stone-500">{{ plan.tone }}</p>
        <h2 class="mt-1 text-lg font-bold text-stone-900">{{ plan.title }}</h2>
        <p class="mt-2 text-2xl font-bold tracking-tight text-stone-900">{{ plan.price }}<span class="ml-1 text-sm font-medium text-stone-500">{{ plan.period }}</span></p>
        <button
          type="button"
          :disabled="loadingPlan === plan.key"
          :class="[
            'mt-4 inline-flex w-full items-center justify-center rounded-full px-4 py-2.5 text-sm font-semibold transition disabled:opacity-50',
            plan.key === 'premium'
              ? 'bg-sky-600 text-white hover:bg-sky-700'
              : plan.key === 'vip'
                ? 'bg-stone-900 text-white hover:bg-black'
                : 'border border-stone-300 bg-white text-stone-900 hover:bg-stone-50',
          ]"
          @click="startCheckout(plan.key)"
        >
          {{ loadingPlan === plan.key ? text.loading : plan.action }}
        </button>
      </article>
    </div>

    <p class="text-sm text-stone-500">{{ text.footer }}</p>
    <NuxtLink :to="localePath('/pricing')" class="inline-block text-sm font-medium text-sky-600 hover:underline">
      {{ text.compareLink }}
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: ['auth', 'onboarding'] })

const localePath = useLocalePath()
const { locale } = useI18n()
const { fetchApi } = useApi()
const loadingPlan = ref<string | null>(null)

const localeCode = computed(() => {
  const code = (locale.value || 'ro').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'ro'
})

type PlanSummary = { key: string; tone: string; title: string; price: string; period: string; action: string }

const copy: Record<string, {
  title: string; subtitle: string; loading: string; footer: string; compareLink: string; plans: PlanSummary[]
}> = {
  ro: {
    title: 'Perioada ta de trial a expirat',
    subtitle: 'Accesul tău gratuit de 7 zile s-a încheiat. Alege un plan pentru a continua să folosești platforma.',
    loading: 'Se procesează...',
    footer: 'Plăți securizate prin Stripe. Poți anula oricând.',
    compareLink: 'Compară toate planurile →',
    plans: [
      { key: 'basic', tone: 'Simplu și clar', title: 'BASIC Start', price: '€12', period: '/ lună', action: 'Alege BASIC' },
      { key: 'premium', tone: 'Echilibru și consistență', title: 'PREMIUM Flow', price: '€25', period: '/ lună', action: 'Alege PREMIUM' },
      { key: 'vip', tone: 'Exclusiv și strategic', title: 'VIP Executive', price: '€49', period: '/ lună', action: 'Alege VIP' },
    ],
  },
  en: {
    title: 'Your trial has ended',
    subtitle: 'Your 7-day free trial is over. Choose a plan to keep using the platform.',
    loading: 'Processing...',
    footer: 'Secure payments via Stripe. Cancel anytime.',
    compareLink: 'Compare all plans →',
    plans: [
      { key: 'basic', tone: 'Simple & practical', title: 'BASIC Start', price: '€12', period: '/ month', action: 'Choose BASIC' },
      { key: 'premium', tone: 'Balanced & consistent', title: 'PREMIUM Flow', price: '€25', period: '/ month', action: 'Choose PREMIUM' },
      { key: 'vip', tone: 'Exclusive & strategic', title: 'VIP Executive', price: '€49', period: '/ month', action: 'Choose VIP' },
    ],
  },
  de: {
    title: 'Dein Testzeitraum ist abgelaufen',
    subtitle: 'Dein kostenloser 7-Tage-Test ist vorbei. Wähle einen Plan, um weiterzumachen.',
    loading: 'Verarbeitung...',
    footer: 'Sichere Zahlung über Stripe. Jederzeit kündbar.',
    compareLink: 'Alle Pläne vergleichen →',
    plans: [
      { key: 'basic', tone: 'Einfach & klar', title: 'BASIC Start', price: '€12', period: '/ Monat', action: 'BASIC wählen' },
      { key: 'premium', tone: 'Ausgewogen & konsistent', title: 'PREMIUM Flow', price: '€25', period: '/ Monat', action: 'PREMIUM wählen' },
      { key: 'vip', tone: 'Exklusiv & strategisch', title: 'VIP Executive', price: '€49', period: '/ Monat', action: 'VIP wählen' },
    ],
  },
  fr: {
    title: 'Votre essai a expiré',
    subtitle: 'Votre essai gratuit de 7 jours est terminé. Choisissez un plan pour continuer.',
    loading: 'En cours...',
    footer: 'Paiements sécurisés via Stripe. Annulation à tout moment.',
    compareLink: 'Comparer tous les plans →',
    plans: [
      { key: 'basic', tone: 'Simple et clair', title: 'BASIC Start', price: '€12', period: '/ mois', action: 'Choisir BASIC' },
      { key: 'premium', tone: 'Équilibré et cohérent', title: 'PREMIUM Flow', price: '€25', period: '/ mois', action: 'Choisir PREMIUM' },
      { key: 'vip', tone: 'Exclusif et stratégique', title: 'VIP Executive', price: '€49', period: '/ mois', action: 'Choisir VIP' },
    ],
  },
  it: {
    title: 'Il tuo periodo di prova è scaduto',
    subtitle: 'I tuoi 7 giorni di prova gratuita sono terminati. Scegli un piano per continuare.',
    loading: 'In elaborazione...',
    footer: 'Pagamenti sicuri tramite Stripe. Cancella quando vuoi.',
    compareLink: 'Confronta tutti i piani →',
    plans: [
      { key: 'basic', tone: 'Semplice e chiaro', title: 'BASIC Start', price: '€12', period: '/ mese', action: 'Scegli BASIC' },
      { key: 'premium', tone: 'Equilibrato e costante', title: 'PREMIUM Flow', price: '€25', period: '/ mese', action: 'Scegli PREMIUM' },
      { key: 'vip', tone: 'Esclusivo e strategico', title: 'VIP Executive', price: '€49', period: '/ mese', action: 'Scegli VIP' },
    ],
  },
  es: {
    title: 'Tu período de prueba ha expirado',
    subtitle: 'Tu prueba gratuita de 7 días ha terminado. Elige un plan para continuar.',
    loading: 'Procesando...',
    footer: 'Pagos seguros a través de Stripe. Cancela cuando quieras.',
    compareLink: 'Comparar todos los planes →',
    plans: [
      { key: 'basic', tone: 'Simple y claro', title: 'BASIC Start', price: '€12', period: '/ mes', action: 'Elegir BASIC' },
      { key: 'premium', tone: 'Equilibrado y constante', title: 'PREMIUM Flow', price: '€25', period: '/ mes', action: 'Elegir PREMIUM' },
      { key: 'vip', tone: 'Exclusivo y estratégico', title: 'VIP Executive', price: '€49', period: '/ mes', action: 'Elegir VIP' },
    ],
  },
  pl: {
    title: 'Twój okres próbny wygasł',
    subtitle: 'Twój bezpłatny 7-dniowy okres próbny dobiegł końca. Wybierz plan, aby kontynuować.',
    loading: 'Przetwarzanie...',
    footer: 'Bezpieczne płatności przez Stripe. Anuluj w dowolnym momencie.',
    compareLink: 'Porównaj wszystkie plany →',
    plans: [
      { key: 'basic', tone: 'Prosty i przejrzysty', title: 'BASIC Start', price: '€12', period: '/ miesiąc', action: 'Wybierz BASIC' },
      { key: 'premium', tone: 'Zrównoważony i stały', title: 'PREMIUM Flow', price: '€25', period: '/ miesiąc', action: 'Wybierz PREMIUM' },
      { key: 'vip', tone: 'Ekskluzywny i strategiczny', title: 'VIP Executive', price: '€49', period: '/ miesiąc', action: 'Wybierz VIP' },
    ],
  },
}

const text = computed(() => copy[localeCode.value] || copy.ro)

usePublicSeo({
  title: computed(() => text.value.title + ' - Doisense'),
  description: computed(() => text.value.subtitle),
  noindex: true,
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
</script>
