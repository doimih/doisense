<template>
  <section class="max-w-6xl mx-auto py-8 md:py-12 space-y-10">
    <div class="grid gap-8 lg:grid-cols-2 lg:gap-14 items-start">
      <div class="space-y-7">
        <p class="inline-flex items-center rounded-full border border-stone-300 bg-white/80 px-4 py-2 text-xs font-semibold tracking-wide text-stone-700">
          {{ text.badge }}
        </p>

        <p class="max-w-xl text-lg leading-9 text-stone-600">
          {{ text.subtitle }}
        </p>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <article class="overflow-hidden rounded-2xl border border-stone-200 bg-white">
            <img
              src="https://images.unsplash.com/photo-1493836512294-502baa1986e2?auto=format&fit=crop&w=1200&q=80"
              alt="Wellbeing support session"
              loading="lazy"
              decoding="async"
              width="960"
              height="760"
              class="h-56 w-full object-cover"
            >
          </article>
          <article class="overflow-hidden rounded-2xl border border-stone-200 bg-white">
            <img
              src="https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=1200&q=80"
              alt="Emotional wellbeing moment"
              loading="lazy"
              decoding="async"
              width="960"
              height="760"
              class="h-56 w-full object-cover"
            >
          </article>
        </div>
      </div>

      <div class="space-y-10">
        <h1 class="text-4xl md:text-6xl font-bold leading-tight text-stone-900">
          {{ text.title }}
        </h1>

        <div class="grid gap-8 sm:grid-cols-2">
          <article v-for="(feature, index) in spotlightCards" :key="feature.title" class="space-y-3">
            <div class="flex h-14 w-14 items-center justify-center rounded-full border border-stone-300 bg-white text-2xl">
              {{ featureIcons[index] }}
            </div>
            <h2 class="text-3xl font-semibold text-stone-900 tracking-tight leading-tight">{{ feature.title }}</h2>
            <p class="text-stone-600 text-xl leading-8">{{ feature.description }}</p>
          </article>
        </div>
      </div>
    </div>

  </section>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
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
  fr: {
    badge: 'Plateforme complete',
    title: 'Fonctionnalites pensees pour un bien-etre concret',
    subtitle: 'Doisense combine journal guide, conversations IA et plans de progression dans un flux coherent.',
    featureCards: [
      { title: 'Journal guide quotidien', description: 'Prompts dynamiques et sauvegarde rapide pour des habitudes saines.' },
      { title: 'Chat IA contextuel', description: 'Des reponses plus pertinentes grace a votre contexte.' },
      { title: 'Programmes structures', description: 'Plans jour par jour avec des actions pratiques.' },
      { title: 'Profil adaptatif', description: 'Le ton et les preferences evoluent selon votre activite.' },
      { title: 'Premium simple', description: 'Parcours d\'upgrade transparent vers les fonctions avancees.' },
      { title: 'Architecture evolutive', description: 'Nuxt, Django, PostgreSQL et Redis pour la fiabilite.' },
    ],
    gdprTitle: 'GDPR integre au produit',
    gdprItems: [
      'Transparence: quelles donnees nous collectons et pourquoi.',
      'Controle: acces, rectification ou suppression.',
      'Minimisation: nous stockons seulement les donnees necessaires.',
      'Securite: separation des services et bonnes pratiques.',
    ],
    gdprAction: 'Voir la page GDPR',
    seoTitle: 'Fonctionnalites Doisense - Journal, chat IA, programmes',
    seoDescription: 'Decouvrez les fonctionnalites cle de Doisense: journal guide, chat IA contextuel et conformite GDPR.',
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
const featureIcons = ['🧠', '👥', '🧾', '💬']
const spotlightCards = computed(() => text.value.featureCards.slice(0, 4))
const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
