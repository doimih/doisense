<template>
  <div class="space-y-12 py-8">
    <section class="relative overflow-hidden rounded-2xl border border-stone-200 bg-gradient-to-br from-amber-50 via-white to-stone-50 p-8 md:p-12">
      <div class="absolute -top-10 -right-10 h-48 w-48 rounded-full bg-amber-200/40 blur-2xl" />
      <div class="absolute -bottom-16 -left-10 h-56 w-56 rounded-full bg-stone-300/30 blur-2xl" />
      <div class="relative max-w-3xl">
        <p class="inline-block rounded-full bg-stone-900 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
          {{ text.heroBadge }}
        </p>
        <h1 class="mt-4 text-4xl md:text-5xl font-bold text-stone-900 leading-tight">{{ text.heroTitle }}</h1>
        <p class="mt-4 text-stone-700 text-lg">{{ text.heroSubtitle }}</p>
        <div class="mt-6 flex flex-wrap gap-3">
          <NuxtLink
            v-if="!authStore.isLoggedIn"
            :to="localePath('/auth/register')"
            class="px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700"
          >
            {{ text.primaryCta }}
          </NuxtLink>
          <NuxtLink
            v-if="!authStore.isLoggedIn"
            :to="localePath('/auth/login')"
            class="px-6 py-3 border border-stone-300 rounded-lg hover:bg-stone-100"
          >
            {{ $t('auth.login') }}
          </NuxtLink>
          <NuxtLink
            v-if="authStore.isLoggedIn"
            :to="localePath('/chat')"
            class="px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700"
          >
            {{ $t('nav.chat') }}
          </NuxtLink>
          <NuxtLink
            :to="localePath('/features')"
            class="px-6 py-3 border border-stone-300 rounded-lg hover:bg-stone-100"
          >
            {{ text.secondaryCta }}
          </NuxtLink>
        </div>
      </div>
    </section>

    <section class="grid gap-4 md:grid-cols-3">
      <article v-for="card in homeCards" :key="card.title" class="bg-white border border-stone-200 rounded-xl px-5 py-[70px]">
        <h2 class="mb-2 text-[19px] font-semibold text-stone-900">{{ card.title }}</h2>
        <p class="text-[15px] text-stone-600">{{ card.description }}</p>
      </article>
    </section>

    <section class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <NuxtLink
        v-for="link in text.quickLinks"
        :key="link.to"
        :to="localePath(link.to)"
        class="bg-white border border-stone-200 rounded-xl px-4 py-[66px] transition hover:bg-stone-50"
      >
        <h3 class="text-[19px] font-semibold text-stone-900">{{ link.title }}</h3>
        <p class="mt-1 text-[15px] text-stone-600">{{ link.description }}</p>
      </NuxtLink>
    </section>

  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const authStore = useAuthStore()
const { locale } = useI18n()
const { cmsPage } = useCmsStaticPage('home')
const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

const homeCopy: Record<string, {
  heroBadge: string
  heroTitle: string
  heroSubtitle: string
  primaryCta: string
  secondaryCta: string
  cards: Array<{ title: string; description: string }>
  quickLinks: Array<{ to: '/features' | '/pricing' | '/about' | '/contact'; title: string; description: string }>
  gdprTitle: string
  gdprSubtitle: string
  privacy: string
  terms: string
  cookies: string
  gdprRights: string
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    heroBadge: 'Wellbeing + AI + GDPR',
    heroTitle: 'Platformă de wellbeing digital, construită responsabil',
    heroSubtitle: 'Doisense îți oferă jurnal ghidat, chat AI contextual și programe structurate, cu pagini legale complete și control asupra datelor.',
    primaryCta: 'Creează cont',
    secondaryCta: 'Vezi funcționalitățile',
    cards: [
      { title: 'Experiență ghidată', description: 'Flux clar de la onboarding la progres zilnic.' },
      { title: 'Design pentru încredere', description: 'Informații explicite despre date, securitate și drepturi.' },
      { title: 'Scalabil pentru produs', description: 'Pagini publice importante gata pentru creștere.' },
    ],
    quickLinks: [
      { to: '/features', title: 'Funcționalități', description: 'Tot ce poate face platforma.' },
      { to: '/pricing', title: 'Prețuri', description: 'Planuri free și premium.' },
      { to: '/about', title: 'Despre', description: 'Misiune, valori și context produs.' },
      { to: '/contact', title: 'Contact', description: 'Suport și canale de comunicare.' },
    ],
    gdprTitle: 'GDPR în tot sistemul',
    gdprSubtitle: 'Pagini dedicate pentru confidențialitate, termeni, cookie-uri și drepturile utilizatorului.',
    privacy: 'Politica de confidențialitate',
    terms: 'Termeni',
    cookies: 'Cookie-uri',
    gdprRights: 'Drepturi GDPR',
    seoTitle: 'Doisense - Wellbeing digital cu AI si jurnal ghidat',
    seoDescription: 'Platforma Doisense ofera jurnal ghidat, chat AI contextual, programe structurate si pagini legale complete pentru transparenta si conformitate.',
  },
  en: {
    heroBadge: 'Wellbeing + AI + GDPR',
    heroTitle: 'Your digital wellbeing platform, built responsibly',
    heroSubtitle: 'Doisense provides guided journaling, contextual AI chat, and structured programs with complete legal pages and user data control.',
    primaryCta: 'Create account',
    secondaryCta: 'Explore features',
    cards: [
      { title: 'Guided experience', description: 'Clear flow from onboarding to daily progress.' },
      { title: 'Trust-focused design', description: 'Explicit data, security, and rights information.' },
      { title: 'Product-ready scale', description: 'Public key pages ready for growth.' },
    ],
    quickLinks: [
      { to: '/features', title: 'Features', description: 'What the platform can do.' },
      { to: '/pricing', title: 'Pricing', description: 'Free and premium plans.' },
      { to: '/about', title: 'About', description: 'Mission, values, and product context.' },
      { to: '/contact', title: 'Contact', description: 'Support and communication channels.' },
    ],
    gdprTitle: 'GDPR across the system',
    gdprSubtitle: 'Dedicated pages for privacy, terms, cookies, and user rights are now included.',
    privacy: 'Privacy Policy',
    terms: 'Terms',
    cookies: 'Cookies',
    gdprRights: 'GDPR Rights',
    seoTitle: 'Doisense - Digital wellbeing with AI and guided journaling',
    seoDescription: 'Doisense provides guided journaling, contextual AI chat, structured programs, and complete legal pages for transparent compliance.',
  },
  de: {
    heroBadge: 'Wellbeing + AI + DSGVO',
    heroTitle: 'Digitale Wellbeing-Plattform, verantwortungsvoll gebaut',
    heroSubtitle: 'Doisense bietet geführtes Tagebuch, kontextbezogenen KI-Chat und strukturierte Programme mit klaren rechtlichen Seiten.',
    primaryCta: 'Konto erstellen',
    secondaryCta: 'Funktionen ansehen',
    cards: [
      { title: 'Geführte Erfahrung', description: 'Klarer Ablauf von Onboarding bis täglichem Fortschritt.' },
      { title: 'Vertrauensdesign', description: 'Klare Infos zu Daten, Sicherheit und Rechten.' },
      { title: 'Skalierbar', description: 'Wichtige öffentliche Seiten für Wachstum bereit.' },
    ],
    quickLinks: [
      { to: '/features', title: 'Funktionen', description: 'Was die Plattform leisten kann.' },
      { to: '/pricing', title: 'Preise', description: 'Free- und Premium-Pläne.' },
      { to: '/about', title: 'Über uns', description: 'Mission, Werte und Produktkontext.' },
      { to: '/contact', title: 'Kontakt', description: 'Support und Kommunikationskanäle.' },
    ],
    gdprTitle: 'DSGVO im gesamten System',
    gdprSubtitle: 'Dedizierte Seiten für Datenschutz, Bedingungen, Cookies und Nutzerrechte.',
    privacy: 'Datenschutz',
    terms: 'Bedingungen',
    cookies: 'Cookies',
    gdprRights: 'DSGVO-Rechte',
    seoTitle: 'Doisense - Digitales Wellbeing mit KI und Tagebuch',
    seoDescription: 'Doisense bietet geführtes Tagebuch, KI-Chat, strukturierte Programme und vollständige rechtliche Seiten.',
  },
  it: {
    heroBadge: 'Wellbeing + AI + GDPR',
    heroTitle: 'Piattaforma di benessere digitale costruita con responsabilità',
    heroSubtitle: 'Doisense offre diario guidato, chat AI contestuale e programmi strutturati con pagine legali complete.',
    primaryCta: 'Crea account',
    secondaryCta: 'Scopri le funzionalità',
    cards: [
      { title: 'Esperienza guidata', description: 'Flusso chiaro dall’onboarding al progresso quotidiano.' },
      { title: 'Design affidabile', description: 'Informazioni chiare su dati, sicurezza e diritti.' },
      { title: 'Scalabilità prodotto', description: 'Pagine pubbliche chiave pronte per crescere.' },
    ],
    quickLinks: [
      { to: '/features', title: 'Funzionalità', description: 'Cosa può fare la piattaforma.' },
      { to: '/pricing', title: 'Prezzi', description: 'Piani free e premium.' },
      { to: '/about', title: 'Chi siamo', description: 'Missione, valori e contesto prodotto.' },
      { to: '/contact', title: 'Contatto', description: 'Supporto e canali di comunicazione.' },
    ],
    gdprTitle: 'GDPR in tutto il sistema',
    gdprSubtitle: 'Pagine dedicate per privacy, termini, cookie e diritti utente.',
    privacy: 'Privacy',
    terms: 'Termini',
    cookies: 'Cookie',
    gdprRights: 'Diritti GDPR',
    seoTitle: 'Doisense - Benessere digitale con AI e diario guidato',
    seoDescription: 'Doisense offre diario guidato, chat AI contestuale, programmi strutturati e pagine legali complete.',
  },
  es: {
    heroBadge: 'Wellbeing + AI + GDPR',
    heroTitle: 'Tu plataforma de bienestar digital, construida con responsabilidad',
    heroSubtitle: 'Doisense ofrece diario guiado, chat AI contextual y programas estructurados con páginas legales completas.',
    primaryCta: 'Crear cuenta',
    secondaryCta: 'Ver funciones',
    cards: [
      { title: 'Experiencia guiada', description: 'Flujo claro desde onboarding hasta progreso diario.' },
      { title: 'Diseño de confianza', description: 'Información clara sobre datos, seguridad y derechos.' },
      { title: 'Escalabilidad', description: 'Páginas públicas clave preparadas para crecer.' },
    ],
    quickLinks: [
      { to: '/features', title: 'Funciones', description: 'Todo lo que la plataforma puede hacer.' },
      { to: '/pricing', title: 'Precios', description: 'Planes free y premium.' },
      { to: '/about', title: 'Acerca de', description: 'Misión, valores y contexto del producto.' },
      { to: '/contact', title: 'Contacto', description: 'Soporte y canales de comunicación.' },
    ],
    gdprTitle: 'GDPR en todo el sistema',
    gdprSubtitle: 'Páginas dedicadas para privacidad, términos, cookies y derechos del usuario.',
    privacy: 'Política de privacidad',
    terms: 'Términos',
    cookies: 'Cookies',
    gdprRights: 'Derechos GDPR',
    seoTitle: 'Doisense - Bienestar digital con AI y diario guiado',
    seoDescription: 'Doisense ofrece diario guiado, chat AI contextual, programas estructurados y páginas legales completas.',
  },
  pl: {
    heroBadge: 'Wellbeing + AI + GDPR',
    heroTitle: 'Twoja platforma wellbeing, zbudowana odpowiedzialnie',
    heroSubtitle: 'Doisense oferuje dziennik prowadzony, kontekstowy chat AI i programy strukturalne z kompletnymi stronami prawnymi.',
    primaryCta: 'Utwórz konto',
    secondaryCta: 'Zobacz funkcje',
    cards: [
      { title: 'Prowadzone doświadczenie', description: 'Jasny przepływ od onboardingu do codziennego postępu.' },
      { title: 'Projekt oparty na zaufaniu', description: 'Czytelne informacje o danych, bezpieczeństwie i prawach.' },
      { title: 'Gotowość na skalę', description: 'Kluczowe strony publiczne gotowe na rozwój.' },
    ],
    quickLinks: [
      { to: '/features', title: 'Funkcje', description: 'Co potrafi platforma.' },
      { to: '/pricing', title: 'Cennik', description: 'Plany free i premium.' },
      { to: '/about', title: 'O nas', description: 'Misja, wartości i kontekst produktu.' },
      { to: '/contact', title: 'Kontakt', description: 'Wsparcie i kanały komunikacji.' },
    ],
    gdprTitle: 'GDPR w całym systemie',
    gdprSubtitle: 'Dedykowane strony dotyczące prywatności, regulaminu, cookies i praw użytkownika.',
    privacy: 'Polityka prywatności',
    terms: 'Regulamin',
    cookies: 'Cookies',
    gdprRights: 'Prawa GDPR',
    seoTitle: 'Doisense - Cyfrowy wellbeing z AI i dziennikiem',
    seoDescription: 'Doisense zapewnia dziennik prowadzony, chat AI, programy strukturalne i kompletne strony prawne.',
  },
}

const text = computed(() => homeCopy[localeCode.value] || homeCopy.en)

type HomeCard = { title: string; description: string }

function stripHtml(value: string) {
  return value
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim()
}

function extractCardsFromCms(html: string): HomeCard[] {
  if (!html?.trim()) return []

  const cards: HomeCard[] = []

  // Recommended format in CMS: table rows => Title | Description
  const rowMatches = [...html.matchAll(/<tr[^>]*>([\s\S]*?)<\/tr>/gi)]
  for (const row of rowMatches) {
    const columns = [...row[1].matchAll(/<t[dh][^>]*>([\s\S]*?)<\/t[dh]>/gi)].map((col) => stripHtml(col[1]))
    if (columns.length >= 2 && columns[0] && columns[1]) {
      cards.push({ title: columns[0], description: columns[1] })
    }
  }

  if (cards.length) return cards

  // Fallback format: heading + first paragraph after heading.
  const headingMatches = [...html.matchAll(/<h[1-6][^>]*>([\s\S]*?)<\/h[1-6]>/gi)]
  for (let i = 0; i < headingMatches.length; i += 1) {
    const heading = stripHtml(headingMatches[i][1])
    const start = headingMatches[i].index ?? 0
    const end = i + 1 < headingMatches.length ? (headingMatches[i + 1].index ?? html.length) : html.length
    const chunk = html.slice(start, end)
    const paragraphMatch = chunk.match(/<p[^>]*>([\s\S]*?)<\/p>/i)
    const paragraph = paragraphMatch ? stripHtml(paragraphMatch[1]) : ""

    if (heading && paragraph) {
      cards.push({ title: heading, description: paragraph })
    }
  }

  return cards
}

const homeCards = computed(() => {
  const parsed = extractCardsFromCms(cmsPage.value?.content || "")
  return parsed.length ? parsed : text.value.cards
})

const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
