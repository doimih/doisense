<template>
  <section class="max-w-6xl mx-auto py-10 space-y-10">
    <header class="space-y-4 text-center">
      <p class="inline-block px-3 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-semibold tracking-wide">
        {{ text.badge }}
      </p>
      <h1 class="text-4xl md:text-5xl font-bold text-stone-900">{{ text.title }}</h1>
      <p class="text-stone-600 max-w-3xl mx-auto">{{ text.subtitle }}</p>
    </header>

    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="feature in text.featureCards"
        :key="feature.title"
        class="bg-white border border-stone-200 rounded-xl p-5 shadow-sm"
      >
        <h2 class="text-lg font-semibold text-stone-900 mb-2">{{ feature.title }}</h2>
        <p class="text-stone-600 text-sm">{{ feature.description }}</p>
      </article>
    </div>

    <section class="bg-white border border-stone-200 rounded-xl p-6">
      <h2 class="text-2xl font-semibold text-stone-900 mb-4">{{ text.gdprTitle }}</h2>
      <ul class="grid gap-3 md:grid-cols-2">
        <li
          v-for="item in text.gdprItems"
          :key="item"
          class="text-stone-700 text-sm bg-stone-50 border border-stone-200 rounded-lg px-4 py-3"
        >
          {{ item }}
        </li>
      </ul>
      <div class="mt-5">
        <NuxtLink
          :to="localePath('/legal/gdpr')"
          class="inline-block px-4 py-2 rounded-lg bg-stone-900 text-white hover:bg-black"
        >
          {{ text.gdprAction }}
        </NuxtLink>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const { locale } = useI18n()
const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

const featuresCopy: Record<string, {
  badge: string
  title: string
  subtitle: string
  featureCards: Array<{ title: string; description: string }>
  gdprTitle: string
  gdprItems: string[]
  gdprAction: string
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    badge: 'Platformă completă',
    title: 'Funcționalități gândite pentru wellbeing real',
    subtitle: 'Doisense combină jurnalul ghidat, conversațiile AI și planurile de progres într-o singură experiență.',
    featureCards: [
      { title: 'Jurnal ghidat zilnic', description: 'Întrebări dinamice și salvare rapidă pentru obiceiuri sănătoase de reflecție.' },
      { title: 'Chat AI contextual', description: 'Asistentul folosește istoricul tău pentru răspunsuri mai relevante și mai empatice.' },
      { title: 'Programe structurate', description: 'Planuri pe zile și pași mici, urmărite direct în contul tău.' },
      { title: 'Profil personal adaptiv', description: 'Preferințele și tonul conversației se ajustează pe baza datelor tale.' },
      { title: 'Flux premium simplu', description: 'Upgrade rapid și transparent pentru funcțiile avansate.' },
      { title: 'Arhitectură scalabilă', description: 'Frontend Nuxt, backend Django, PostgreSQL și Redis pentru stabilitate.' },
    ],
    gdprTitle: 'Conformitate GDPR în produs',
    gdprItems: [
      'Transparență: vezi ce date colectăm și de ce.',
      'Control: poți solicita acces, rectificare sau ștergere.',
      'Minimizare: păstrăm doar datele necesare funcționalităților.',
      'Securitate: separare pe servicii și bune practici de deployment.',
    ],
    gdprAction: 'Vezi pagina GDPR',
    seoTitle: 'Functionalitati Doisense - Jurnal, AI chat, programe',
    seoDescription: 'Explorează funcționalitățile principale Doisense: jurnal ghidat, chat AI contextual, programe structurate și conformitate GDPR.',
  },
  en: {
    badge: 'All-in-one platform',
    title: 'Features designed for practical wellbeing',
    subtitle: 'Doisense combines guided journaling, AI conversations, and progress plans in one coherent flow.',
    featureCards: [
      { title: 'Daily guided journal', description: 'Dynamic prompts and fast saving for consistent reflection habits.' },
      { title: 'Context-aware AI chat', description: 'The assistant uses your context for more relevant and empathetic responses.' },
      { title: 'Structured programs', description: 'Day-by-day plans with practical actions tracked in your account.' },
      { title: 'Adaptive personal profile', description: 'Tone and preferences evolve based on your activity and feedback.' },
      { title: 'Simple premium flow', description: 'Transparent upgrade path for advanced features.' },
      { title: 'Scalable architecture', description: 'Nuxt frontend, Django backend, PostgreSQL and Redis for reliability.' },
    ],
    gdprTitle: 'GDPR built into the product',
    gdprItems: [
      'Transparency: clearly understand what data we collect and why.',
      'Control: request access, rectification, or deletion.',
      'Minimization: we store only data needed for core features.',
      'Security: service separation and deployment best practices.',
    ],
    gdprAction: 'Read the GDPR page',
    seoTitle: 'Doisense Features - Journaling, AI chat, programs',
    seoDescription: 'Explore key Doisense features: guided journaling, contextual AI chat, structured programs, and GDPR compliance.',
  },
  de: {
    badge: 'Alles-in-einem',
    title: 'Funktionen für echtes Wellbeing',
    subtitle: 'Doisense verbindet geführtes Tagebuch, KI-Dialoge und Fortschrittspläne in einem klaren Ablauf.',
    featureCards: [
      { title: 'Tägliches Tagebuch', description: 'Dynamische Fragen und schnelles Speichern für gesunde Routinen.' },
      { title: 'Kontextbezogener KI-Chat', description: 'Antworten werden auf deinen Verlauf und Kontext abgestimmt.' },
      { title: 'Strukturierte Programme', description: 'Tagespläne mit kleinen Schritten direkt im Konto.' },
      { title: 'Adaptives Profil', description: 'Ton und Präferenzen passen sich deiner Nutzung an.' },
      { title: 'Einfaches Premium', description: 'Transparenter Upgrade-Pfad für erweiterte Funktionen.' },
      { title: 'Skalierbare Architektur', description: 'Nuxt, Django, PostgreSQL und Redis für Stabilität.' },
    ],
    gdprTitle: 'DSGVO im Produkt',
    gdprItems: [
      'Transparenz: welche Daten wir sammeln und warum.',
      'Kontrolle: Auskunft, Berichtigung und Löschung.',
      'Datenminimierung: nur notwendige Daten für Kernfunktionen.',
      'Sicherheit: Service-Trennung und Best Practices.',
    ],
    gdprAction: 'DSGVO-Seite ansehen',
    seoTitle: 'Doisense Funktionen - Tagebuch, KI-Chat, Programme',
    seoDescription: 'Entdecke die wichtigsten Doisense-Funktionen mit geführtem Tagebuch, KI-Chat und DSGVO-Konformität.',
  },
  it: {
    badge: 'Piattaforma completa',
    title: 'Funzionalità pensate per il benessere reale',
    subtitle: 'Doisense unisce diario guidato, conversazioni AI e piani di progresso in un unico flusso.',
    featureCards: [
      { title: 'Diario guidato quotidiano', description: 'Prompt dinamici e salvataggio rapido per creare routine sane.' },
      { title: 'Chat AI contestuale', description: 'Risposte più pertinenti grazie al tuo contesto personale.' },
      { title: 'Programmi strutturati', description: 'Piani giorno per giorno con azioni pratiche.' },
      { title: 'Profilo adattivo', description: 'Tono e preferenze evolvono in base al tuo utilizzo.' },
      { title: 'Premium semplice', description: 'Upgrade trasparente alle funzioni avanzate.' },
      { title: 'Architettura scalabile', description: 'Nuxt, Django, PostgreSQL e Redis per affidabilità.' },
    ],
    gdprTitle: 'GDPR integrato nel prodotto',
    gdprItems: [
      'Trasparenza: cosa raccogliamo e perché.',
      'Controllo: accesso, rettifica o cancellazione.',
      'Minimizzazione: salviamo solo i dati necessari.',
      'Sicurezza: separazione servizi e best practice.',
    ],
    gdprAction: 'Vai alla pagina GDPR',
    seoTitle: 'Funzionalità Doisense - Diario, chat AI, programmi',
    seoDescription: 'Scopri le funzionalità principali di Doisense: diario guidato, chat AI e conformità GDPR.',
  },
  es: {
    badge: 'Plataforma integral',
    title: 'Funciones pensadas para bienestar real',
    subtitle: 'Doisense combina diario guiado, conversaciones AI y planes de progreso en un flujo coherente.',
    featureCards: [
      { title: 'Diario guiado diario', description: 'Preguntas dinámicas y guardado rápido para crear hábitos saludables.' },
      { title: 'Chat AI contextual', description: 'Respuestas más relevantes según tu contexto.' },
      { title: 'Programas estructurados', description: 'Planes por día con pasos prácticos en tu cuenta.' },
      { title: 'Perfil adaptativo', description: 'El tono y preferencias evolucionan según tu actividad.' },
      { title: 'Premium simple', description: 'Ruta de upgrade transparente para funciones avanzadas.' },
      { title: 'Arquitectura escalable', description: 'Nuxt, Django, PostgreSQL y Redis para estabilidad.' },
    ],
    gdprTitle: 'GDPR dentro del producto',
    gdprItems: [
      'Transparencia: qué datos recopilamos y por qué.',
      'Control: acceso, rectificación o eliminación.',
      'Minimización: guardamos solo datos necesarios.',
      'Seguridad: separación de servicios y buenas prácticas.',
    ],
    gdprAction: 'Ver página GDPR',
    seoTitle: 'Funciones Doisense - Diario, chat AI, programas',
    seoDescription: 'Explora las funciones clave de Doisense: diario guiado, chat AI contextual y cumplimiento GDPR.',
  },
  pl: {
    badge: 'Platforma all-in-one',
    title: 'Funkcje dla realnego wellbeing',
    subtitle: 'Doisense łączy dziennik prowadzony, rozmowy AI i plany postępu w jednym spójnym doświadczeniu.',
    featureCards: [
      { title: 'Codzienny dziennik', description: 'Dynamiczne pytania i szybkie zapisywanie dla zdrowych nawyków.' },
      { title: 'Kontekstowy chat AI', description: 'Bardziej trafne odpowiedzi dzięki Twojemu kontekstowi.' },
      { title: 'Programy strukturalne', description: 'Plan dnia po dniu z praktycznymi krokami.' },
      { title: 'Profil adaptacyjny', description: 'Ton i preferencje dopasowują się do Twojej aktywności.' },
      { title: 'Prosty Premium', description: 'Przejrzysty upgrade do funkcji zaawansowanych.' },
      { title: 'Skalowalna architektura', description: 'Nuxt, Django, PostgreSQL i Redis dla niezawodności.' },
    ],
    gdprTitle: 'GDPR w produkcie',
    gdprItems: [
      'Transparentność: co zbieramy i dlaczego.',
      'Kontrola: dostęp, poprawienie i usunięcie danych.',
      'Minimalizacja: przechowujemy tylko potrzebne dane.',
      'Bezpieczeństwo: separacja usług i dobre praktyki.',
    ],
    gdprAction: 'Zobacz stronę GDPR',
    seoTitle: 'Funkcje Doisense - Dziennik, chat AI, programy',
    seoDescription: 'Poznaj kluczowe funkcje Doisense: dziennik prowadzony, kontekstowy chat AI i zgodność GDPR.',
  },
}

const text = computed(() => featuresCopy[localeCode.value] || featuresCopy.en)
const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
