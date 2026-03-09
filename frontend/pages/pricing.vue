<template>
  <section class="max-w-6xl mx-auto py-10 space-y-8">
    <template v-if="hasCmsContent && cmsPage">
      <h1 class="text-4xl font-bold text-stone-900 text-center">{{ cmsPage.title }}</h1>
      <section class="bg-white border border-stone-200 rounded-xl p-5 max-w-4xl mx-auto">
        <p class="text-stone-700 text-sm leading-7 whitespace-pre-line">{{ cmsPage.content }}</p>
      </section>
    </template>

    <template v-else>
      <header class="text-center space-y-3">
        <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
        <p class="text-stone-600 max-w-2xl mx-auto">{{ text.subtitle }}</p>
      </header>

      <div class="grid gap-4 md:grid-cols-2">
        <article class="bg-white border border-stone-200 rounded-xl p-6">
          <h2 class="text-2xl font-semibold text-stone-900">{{ text.freeTitle }}</h2>
          <p class="text-stone-500 text-sm mb-4">{{ text.freePrice }}</p>
          <ul class="space-y-2 text-sm text-stone-700">
            <li v-for="item in text.freeItems" :key="item">• {{ item }}</li>
          </ul>
        </article>

        <article class="bg-stone-900 text-white rounded-xl p-6">
          <h2 class="text-2xl font-semibold">{{ text.premiumTitle }}</h2>
          <p class="text-stone-200 text-sm mb-4">{{ text.premiumPrice }}</p>
          <ul class="space-y-2 text-sm">
            <li v-for="item in text.premiumItems" :key="item">• {{ item }}</li>
          </ul>
        </article>
      </div>

      <p class="text-xs text-stone-500 bg-stone-100 border border-stone-200 rounded-lg p-3">
        {{ text.notice }}
      </p>
    </template>
  </section>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})
const { cmsPage, hasCmsContent } = useCmsStaticPage('pricing')

const pricingCopy: Record<string, {
  title: string
  subtitle: string
  freeTitle: string
  freePrice: string
  freeItems: string[]
  premiumTitle: string
  premiumPrice: string
  premiumItems: string[]
  notice: string
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    title: 'Planuri și prețuri',
    subtitle: 'Începe gratuit și treci la Premium când vrei funcții avansate și programe complete.',
    freeTitle: 'Free',
    freePrice: '0 EUR / lună',
    freeItems: ['Acces la jurnal de bază', 'Chat AI standard', 'Profil personal de bază'],
    premiumTitle: 'Premium',
    premiumPrice: 'Conform Stripe checkout',
    premiumItems: ['Programe ghidate extinse', 'Personalizare avansată AI', 'Prioritate la noi funcționalități'],
    notice: 'Plățile sunt procesate prin Stripe. Vei vedea prețul final în checkout înainte de confirmare.',
    seoTitle: 'Preturi Doisense - Planuri Free si Premium',
    seoDescription: 'Vezi planurile Doisense, diferențele dintre Free și Premium și detalii despre plata securizată prin Stripe.',
  },
  en: {
    title: 'Plans and pricing',
    subtitle: 'Start for free and upgrade to Premium when you need advanced features and full programs.',
    freeTitle: 'Free',
    freePrice: '0 EUR / month',
    freeItems: ['Basic journaling access', 'Standard AI chat', 'Basic personal profile'],
    premiumTitle: 'Premium',
    premiumPrice: 'As shown in Stripe checkout',
    premiumItems: ['Extended guided programs', 'Advanced AI personalization', 'Priority access to new features'],
    notice: 'Payments are processed via Stripe. You will see final pricing in checkout before confirmation.',
    seoTitle: 'Doisense Pricing - Free and Premium plans',
    seoDescription: 'Check Doisense plans, Free vs Premium differences, and secure Stripe payment details.',
  },
  de: {
    title: 'Pläne und Preise',
    subtitle: 'Starte kostenlos und wechsle zu Premium, wenn du erweiterte Funktionen brauchst.',
    freeTitle: 'Free',
    freePrice: '0 EUR / Monat',
    freeItems: ['Basiszugang zum Tagebuch', 'Standard-KI-Chat', 'Basisprofil'],
    premiumTitle: 'Premium',
    premiumPrice: 'Wie im Stripe-Checkout angezeigt',
    premiumItems: ['Erweiterte Programme', 'Fortgeschrittene KI-Personalisierung', 'Priorität bei neuen Funktionen'],
    notice: 'Zahlungen werden über Stripe verarbeitet. Den Endpreis siehst du vor der Bestätigung im Checkout.',
    seoTitle: 'Doisense Preise - Free und Premium',
    seoDescription: 'Sieh dir Doisense-Pläne, Unterschiede zwischen Free und Premium und sichere Stripe-Zahlung an.',
  },
  it: {
    title: 'Piani e prezzi',
    subtitle: 'Inizia gratis e passa a Premium quando vuoi funzionalità avanzate e programmi completi.',
    freeTitle: 'Free',
    freePrice: '0 EUR / mese',
    freeItems: ['Accesso base al diario', 'Chat AI standard', 'Profilo personale base'],
    premiumTitle: 'Premium',
    premiumPrice: 'Come mostrato nel checkout Stripe',
    premiumItems: ['Programmi guidati estesi', 'Personalizzazione AI avanzata', 'Priorità sulle nuove funzionalità'],
    notice: 'I pagamenti sono elaborati tramite Stripe. Vedrai il prezzo finale prima della conferma.',
    seoTitle: 'Prezzi Doisense - Piani Free e Premium',
    seoDescription: 'Scopri i piani Doisense, differenze tra Free e Premium e dettagli sul pagamento sicuro con Stripe.',
  },
  es: {
    title: 'Planes y precios',
    subtitle: 'Empieza gratis y pasa a Premium cuando necesites funciones avanzadas y programas completos.',
    freeTitle: 'Free',
    freePrice: '0 EUR / mes',
    freeItems: ['Acceso básico al diario', 'Chat AI estándar', 'Perfil personal básico'],
    premiumTitle: 'Premium',
    premiumPrice: 'Como se muestra en Stripe checkout',
    premiumItems: ['Programas guiados ampliados', 'Personalización AI avanzada', 'Prioridad en nuevas funciones'],
    notice: 'Los pagos se procesan con Stripe. Verás el precio final antes de confirmar.',
    seoTitle: 'Precios Doisense - Planes Free y Premium',
    seoDescription: 'Consulta los planes de Doisense, diferencias entre Free y Premium y pago seguro con Stripe.',
  },
  pl: {
    title: 'Plany i ceny',
    subtitle: 'Zacznij za darmo i przejdź na Premium, gdy potrzebujesz zaawansowanych funkcji i pełnych programów.',
    freeTitle: 'Free',
    freePrice: '0 EUR / miesiąc',
    freeItems: ['Podstawowy dostęp do dziennika', 'Standardowy chat AI', 'Podstawowy profil'],
    premiumTitle: 'Premium',
    premiumPrice: 'Jak pokazano w Stripe checkout',
    premiumItems: ['Rozszerzone programy prowadzone', 'Zaawansowana personalizacja AI', 'Priorytet dla nowych funkcji'],
    notice: 'Płatności są realizowane przez Stripe. Ostateczną cenę zobaczysz przed potwierdzeniem.',
    seoTitle: 'Cennik Doisense - Free i Premium',
    seoDescription: 'Sprawdź plany Doisense, różnice między Free i Premium oraz bezpieczne płatności Stripe.',
  },
}

const text = computed(() => pricingCopy[localeCode.value] || pricingCopy.en)
const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
