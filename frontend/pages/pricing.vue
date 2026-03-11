<template>
  <section class="max-w-6xl mx-auto py-10 space-y-10">
    <header class="grid gap-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
      <div class="space-y-5">
        <p class="inline-flex items-center rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold text-stone-700">
          {{ text.badge }}
        </p>
        <h1 class="text-4xl md:text-6xl font-bold leading-tight text-stone-900">{{ text.title }}</h1>
      </div>
      <p class="max-w-md text-lg leading-8 text-stone-600 lg:ml-auto">{{ text.subtitle }}</p>
    </header>

    <section class="grid gap-5 lg:grid-cols-3">
      <article
        v-for="(plan, index) in text.plans"
        :key="plan.title"
        :class="[
          'rounded-2xl border p-7 shadow-sm',
          index === 1 ? 'border-sky-200 bg-sky-100/70' : 'border-stone-200 bg-white',
        ]"
      >
        <p class="text-2xl font-semibold text-stone-900">{{ plan.title }}</p>
        <p class="mt-3 text-6xl font-bold tracking-tight text-stone-900">{{ plan.price }}</p>
        <p class="mt-1 text-sm font-medium text-stone-600">{{ plan.period }}</p>
        <p class="mt-4 border-t border-stone-200 pt-4 text-lg leading-8 text-stone-600">{{ plan.description }}</p>

        <ul class="mt-6 space-y-2 text-lg text-stone-700">
          <li v-for="item in plan.items" :key="item" class="flex items-start gap-2">
            <span class="text-emerald-500">✓</span>
            <span>{{ item }}</span>
          </li>
        </ul>

        <NuxtLink
          :to="localePath('/auth/register')"
          class="mt-7 inline-flex w-full items-center justify-center rounded-full bg-black px-5 py-3 text-base font-semibold text-white transition hover:bg-stone-900"
        >
          {{ plan.action }}
        </NuxtLink>
      </article>
    </section>

    <p class="rounded-xl border border-stone-200 bg-stone-50 px-4 py-3 text-sm text-stone-600">
      {{ text.notice }}
    </p>
  </section>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const { locale } = useI18n()

const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

type PricingPlan = {
  title: string
  price: string
  period: string
  description: string
  items: string[]
  action: string
}

const pricingCopy: Record<string, {
  badge: string
  title: string
  subtitle: string
  plans: PricingPlan[]
  notice: string
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    badge: 'Prețuri simple și transparente',
    title: 'Investește în wellbeing-ul tău fără confuzie',
    subtitle: 'Planurile sunt gândite pentru ritmul tău: clar, flexibil și orientat spre progres real.',
    plans: [
      {
        title: 'Basic Support',
        price: '49EUR',
        period: '/ sesiune',
        description: 'Un punct bun de pornire pentru suport punctual și claritate emoțională.',
        items: ['1 sesiune/săptămână', 'Suport pe email', 'Coach alocat', 'Reprogramare flexibilă', 'Acces tracker wellbeing'],
        action: 'Începe cu Basic',
      },
      {
        title: 'Growth Plan',
        price: '129EUR',
        period: '/ lună',
        description: 'Pentru cei care vor ritm constant, structură și rezultate măsurabile.',
        items: ['2 sesiuni/săptămână', 'Acces chat direct', 'Fișe personalizate', 'Review lunar progres', 'Programări prioritare'],
        action: 'Alege Growth Plan',
      },
      {
        title: 'Premium Care',
        price: '289EUR',
        period: '/ lună',
        description: 'Pachet complet pentru transformare pe termen lung și suport extins.',
        items: ['Sesiuni nelimitate', 'Specialist dedicat', 'Acces complet programe', 'Rapoarte wellbeing', 'Beneficii VIP'],
        action: 'Pornește Premium',
      },
    ],
    notice: 'Plățile sunt procesate prin Stripe. În checkout vezi prețul final înainte de confirmare.',
    seoTitle: 'Prețuri Doisense - 3 pachete pentru wellbeing',
    seoDescription: 'Compară pachetele Basic Support, Growth Plan și Premium Care pe platforma Doisense.',
  },
  en: {
    badge: 'Simple, Transparent Pricing',
    title: 'Invest In Your Mental Wellbeing Without Confusion',
    subtitle: 'Our plans are designed to meet you where you are: clear, flexible, and value-driven.',
    plans: [
      {
        title: 'Basic Support',
        price: '49EUR',
        period: '/ session',
        description: 'A practical starting point for short-term guidance and emotional support.',
        items: ['1x weekly session', 'Email support', 'Assigned coach', 'Flexible rescheduling', 'Wellbeing tracker access'],
        action: 'Start With Basic',
      },
      {
        title: 'Growth Plan',
        price: '129EUR',
        period: '/ month',
        description: 'For people ready to build consistent clarity, structure, and momentum.',
        items: ['2x weekly sessions', 'Direct chat access', 'Personalized worksheets', 'Monthly progress review', 'Priority booking'],
        action: 'Choose Growth Plan',
      },
      {
        title: 'Premium Care',
        price: '289EUR',
        period: '/ month',
        description: 'Designed for long-term transformation with deeper guidance and access.',
        items: ['Unlimited sessions', 'Dedicated specialist', 'Full program access', 'Mental wellbeing reports', 'VIP member perks'],
        action: 'Start Premium',
      },
    ],
    notice: 'Payments are securely processed via Stripe. Final price is visible before confirmation.',
    seoTitle: 'Doisense Pricing - 3 wellbeing packages',
    seoDescription: 'Compare Basic Support, Growth Plan, and Premium Care on Doisense.',
  },
  de: {
    badge: 'Einfache, transparente Preise',
    title: 'Investiere in dein Wohlbefinden ohne Verwirrung',
    subtitle: 'Unsere Pakete sind klar, flexibel und auf echten Fortschritt ausgerichtet.',
    plans: [
      { title: 'Basic Support', price: '49EUR', period: '/ Sitzung', description: 'Guter Einstieg für kurze Begleitung und emotionale Stabilität.', items: ['1 Sitzung/Woche', 'E-Mail Support', 'Fester Coach', 'Flexible Umbuchung', 'Wellbeing Tracker'], action: 'Mit Basic starten' },
      { title: 'Growth Plan', price: '129EUR', period: '/ Monat', description: 'Für Menschen, die Struktur, Kontinuität und messbaren Fortschritt wollen.', items: ['2 Sitzungen/Woche', 'Direkter Chat-Zugang', 'Personalisierte Arbeitsblätter', 'Monatlicher Review', 'Priorisierte Buchung'], action: 'Growth Plan wählen' },
      { title: 'Premium Care', price: '289EUR', period: '/ Monat', description: 'Umfassendes Paket für langfristige Transformation und tiefe Betreuung.', items: ['Unbegrenzte Sitzungen', 'Dedizierter Spezialist', 'Voller Programmzugang', 'Wellbeing-Berichte', 'VIP Vorteile'], action: 'Premium starten' },
    ],
    notice: 'Zahlungen laufen sicher über Stripe. Der Endpreis ist vor Bestätigung sichtbar.',
    seoTitle: 'Doisense Preise - 3 Pakete',
    seoDescription: 'Vergleiche Basic Support, Growth Plan und Premium Care bei Doisense.',
  },
  fr: {
    badge: 'Tarification simple et transparente',
    title: 'Investissez dans votre bien-etre sans confusion',
    subtitle: 'Des plans clairs et flexibles, adaptes a votre rythme de progression.',
    plans: [
      { title: 'Basic Support', price: '49EUR', period: '/ session', description: 'Un bon point de depart pour un accompagnement court et rassurant.', items: ['1 session/semaine', 'Support email', 'Coach attribue', 'Reprogrammation flexible', 'Acces tracker wellbeing'], action: 'Commencer Basic' },
      { title: 'Growth Plan', price: '129EUR', period: '/ mois', description: 'Pour celles et ceux qui veulent une progression reguliere et structuree.', items: ['2 sessions/semaine', 'Acces chat direct', 'Fiches personnalisees', 'Revue mensuelle', 'Priorite de reservation'], action: 'Choisir Growth' },
      { title: 'Premium Care', price: '289EUR', period: '/ mois', description: 'Un pack complet pour une transformation durable.', items: ['Sessions illimitees', 'Specialiste dedie', 'Acces complet aux programmes', 'Rapports wellbeing', 'Avantages VIP'], action: 'Commencer Premium' },
    ],
    notice: 'Paiements securises via Stripe. Le prix final est visible avant validation.',
    seoTitle: 'Tarifs Doisense - 3 offres wellbeing',
    seoDescription: 'Comparez Basic Support, Growth Plan et Premium Care sur Doisense.',
  },
  it: {
    badge: 'Prezzi semplici e trasparenti',
    title: 'Investi nel tuo benessere mentale senza confusione',
    subtitle: 'Piani chiari e flessibili, costruiti sul tuo ritmo personale.',
    plans: [
      { title: 'Basic Support', price: '49EUR', period: '/ sessione', description: 'Ottimo punto di partenza per supporto mirato e chiarezza emotiva.', items: ['1 sessione/settimana', 'Supporto email', 'Coach assegnato', 'Ripianificazione flessibile', 'Accesso tracker wellbeing'], action: 'Inizia con Basic' },
      { title: 'Growth Plan', price: '129EUR', period: '/ mese', description: 'Per chi vuole continuita, struttura e risultati concreti.', items: ['2 sessioni/settimana', 'Accesso chat diretto', 'Schede personalizzate', 'Review mensile', 'Prenotazione prioritaria'], action: 'Scegli Growth' },
      { title: 'Premium Care', price: '289EUR', period: '/ mese', description: 'Pacchetto completo per trasformazione a lungo termine.', items: ['Sessioni illimitate', 'Specialista dedicato', 'Accesso completo programmi', 'Report wellbeing', 'Vantaggi VIP'], action: 'Avvia Premium' },
    ],
    notice: 'Pagamenti gestiti in sicurezza con Stripe. Prezzo finale visibile prima della conferma.',
    seoTitle: 'Prezzi Doisense - 3 pacchetti wellbeing',
    seoDescription: 'Confronta Basic Support, Growth Plan e Premium Care su Doisense.',
  },
  es: {
    badge: 'Precios simples y transparentes',
    title: 'Invierte en tu bienestar mental sin confusión',
    subtitle: 'Planes claros, flexibles y adaptados a tu momento personal.',
    plans: [
      { title: 'Basic Support', price: '49EUR', period: '/ sesión', description: 'Buen punto de partida para apoyo puntual y claridad emocional.', items: ['1 sesión semanal', 'Soporte por email', 'Coach asignado', 'Reprogramación flexible', 'Acceso a tracker wellbeing'], action: 'Empezar Basic' },
      { title: 'Growth Plan', price: '129EUR', period: '/ mes', description: 'Para quienes buscan estructura continua y avances medibles.', items: ['2 sesiones semanales', 'Acceso chat directo', 'Fichas personalizadas', 'Revisión mensual', 'Reserva prioritaria'], action: 'Elegir Growth' },
      { title: 'Premium Care', price: '289EUR', period: '/ mes', description: 'Diseñado para transformación profunda y apoyo continuo.', items: ['Sesiones ilimitadas', 'Especialista dedicado', 'Acceso total a programas', 'Reportes wellbeing', 'Beneficios VIP'], action: 'Iniciar Premium' },
    ],
    notice: 'Pagos procesados de forma segura con Stripe. Precio final visible antes de confirmar.',
    seoTitle: 'Precios Doisense - 3 paquetes wellbeing',
    seoDescription: 'Compara Basic Support, Growth Plan y Premium Care en Doisense.',
  },
  pl: {
    badge: 'Prosty i transparentny cennik',
    title: 'Zainwestuj w wellbeing bez niejasnosci',
    subtitle: 'Pakiety sa jasne, elastyczne i dopasowane do Twojego etapu.',
    plans: [
      { title: 'Basic Support', price: '49EUR', period: '/ sesja', description: 'Dobry start dla wsparcia krok po kroku i emocjonalnej równowagi.', items: ['1 sesja tygodniowo', 'Wsparcie email', 'Przypisany coach', 'Elastyczna zmiana terminu', 'Dostęp do trackera wellbeing'], action: 'Start z Basic' },
      { title: 'Growth Plan', price: '129EUR', period: '/ miesiąc', description: 'Dla osób, które chcą regularności i mierzalnego progresu.', items: ['2 sesje tygodniowo', 'Bezpośredni chat', 'Spersonalizowane materiały', 'Miesięczny przegląd postępów', 'Priorytetowe rezerwacje'], action: 'Wybierz Growth' },
      { title: 'Premium Care', price: '289EUR', period: '/ miesiąc', description: 'Kompletny pakiet dla długoterminowej transformacji.', items: ['Nielimitowane sesje', 'Dedykowany specjalista', 'Pełny dostęp do programów', 'Raporty wellbeing', 'Korzyści VIP'], action: 'Start Premium' },
    ],
    notice: 'Płatności są bezpiecznie realizowane przez Stripe. Cenę końcową zobaczysz przed potwierdzeniem.',
    seoTitle: 'Cennik Doisense - 3 pakiety wellbeing',
    seoDescription: 'Porównaj Basic Support, Growth Plan i Premium Care w Doisense.',
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
