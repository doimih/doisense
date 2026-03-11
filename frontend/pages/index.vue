<template>
  <div class="-mt-6 pb-8">
    <section data-nav-theme="dark" class="relative left-1/2 right-1/2 -mx-[50vw] w-screen overflow-hidden bg-stone-900 text-white">
      <img
        src="/hero-zen.jpg"
        alt="Doisense wellbeing support"
        loading="eager"
        decoding="async"
        width="2200"
        height="1400"
        class="absolute inset-0 h-full w-full object-cover object-[50%_18%]"
      >
      <div class="absolute inset-0 bg-stone-950/62" />
      <div class="absolute inset-0 bg-gradient-to-r from-stone-950/94 via-stone-900/74 to-stone-900/48" />
      <div class="pointer-events-none absolute inset-0">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_12%_18%,rgba(125,211,252,0.35),transparent_42%),radial-gradient(circle_at_86%_82%,rgba(56,189,248,0.32),transparent_45%)]" />
      </div>

      <div class="relative mx-auto max-w-[1440px] px-4 py-10 sm:px-6 md:py-14 lg:px-8">
        <div class="relative overflow-hidden rounded-[2.4rem] border border-white/20 bg-black/28 p-5 shadow-[0_32px_90px_-35px_rgba(14,116,144,0.65)] backdrop-blur-[1px] md:p-8 lg:p-10">

          <div class="relative grid gap-8 lg:grid-cols-[1.18fr_0.82fr] lg:items-end">
            <div class="space-y-7">
              <p class="inline-flex items-center rounded-full border border-white/30 bg-white/10 px-4 py-2 text-xs font-semibold text-white/95 md:text-sm">
                {{ text.heroBadge }}
              </p>

              <h1 class="max-w-4xl text-4xl font-bold leading-[1.05] tracking-tight text-white md:text-6xl lg:text-7xl">
                {{ text.heroTitle }}
              </h1>

              <p class="max-w-2xl text-base leading-8 text-white/85 md:text-lg">
                {{ text.heroSubtitle }}
              </p>

              <div class="flex flex-wrap gap-3">
                <NuxtLink
                  v-if="!authStore.isLoggedIn"
                  :to="localePath('/auth/register')"
                  class="rounded-full bg-sky-300 px-6 py-3 text-sm font-semibold text-stone-900 transition hover:bg-sky-200"
                >
                  {{ text.primaryCta }}
                </NuxtLink>
                <NuxtLink
                  v-if="!authStore.isLoggedIn"
                  :to="localePath('/auth/login')"
                  class="rounded-full border border-white/35 bg-white/10 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/20"
                >
                  {{ $t('auth.login') }}
                </NuxtLink>
                <NuxtLink
                  v-if="authStore.isLoggedIn"
                  :to="localePath('/chat')"
                  class="rounded-full bg-sky-300 px-6 py-3 text-sm font-semibold text-stone-900 transition hover:bg-sky-200"
                >
                  {{ $t('nav.chat') }}
                </NuxtLink>
                <NuxtLink
                  :to="localePath('/features')"
                  class="rounded-full border border-white/35 bg-white/10 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/20"
                >
                  {{ text.secondaryCta }}
                </NuxtLink>
              </div>
            </div>

            <div class="space-y-4 lg:justify-self-end lg:max-w-md">
              <article class="rounded-2xl border border-white/20 bg-white/10 p-5 backdrop-blur">
                <h2 class="text-2xl font-semibold tracking-tight text-white md:text-3xl">{{ heroCard.title }}</h2>
                <p class="mt-2 text-base leading-7 text-white/85 md:text-lg">{{ heroCard.description }}</p>
              </article>

              <div class="flex flex-wrap gap-3">
                <p class="rounded-full border border-white/25 bg-white/10 px-5 py-2 text-sm font-semibold text-white/90 shadow-sm md:text-base">
                  {{ heroPillLeft }}
                </p>
                <p class="rounded-full border border-white/25 bg-white/10 px-5 py-2 text-sm font-semibold text-white/90 shadow-sm md:text-base">
                  {{ heroPillRight }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="mt-[120px] rounded-3xl border border-stone-200 bg-stone-100/70 px-5 py-8 md:px-8 md:py-10">
      <div class="grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-start">
        <div class="space-y-6">
          <p class="inline-flex items-center rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold text-stone-700 md:text-sm">
            {{ text.heroBadge }}
          </p>
          <h2 class="max-w-4xl text-4xl font-bold leading-tight text-stone-900 md:text-6xl">
            {{ sectionTwoTitle }}
          </h2>
        </div>

        <div class="space-y-6 lg:pt-4">
          <p class="max-w-lg text-lg leading-8 text-stone-600">
            {{ sectionTwoDescription }}
          </p>
          <NuxtLink
            :to="sectionTwoCta.to"
            class="inline-flex items-center rounded-full bg-black px-6 py-3 text-sm font-semibold text-white transition hover:bg-stone-900"
          >
            {{ sectionTwoCta.label }}
          </NuxtLink>
        </div>
      </div>

      <div class="mt-8 flex flex-wrap gap-3">
        <NuxtLink
          v-for="link in text.quickLinks"
          :key="link.to"
          :to="localePath(link.to)"
          class="rounded-full border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-700 transition hover:bg-stone-50"
        >
          {{ link.title }}
        </NuxtLink>
      </div>
    </section>

    <section class="mt-[120px] rounded-3xl border border-stone-200 bg-stone-100/70 px-5 py-8 md:px-8 md:py-10">
      <div class="grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
        <p class="inline-flex h-fit w-fit justify-self-start items-center rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold text-stone-700 md:text-sm">
          {{ impactText.badge }}
        </p>
        <h2 class="max-w-4xl text-4xl font-bold leading-tight text-stone-900 md:text-6xl">
          {{ impactText.title }}
        </h2>
      </div>

      <div class="mt-8 grid gap-4 lg:grid-cols-4">
        <article
          v-for="(item, index) in impactCards"
          :key="item.label"
          :class="[
            'rounded-2xl border p-5 md:p-6',
            index === 1 ? 'border-sky-200 bg-sky-100/70' : 'border-stone-200 bg-white',
          ]"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-full border border-stone-200 bg-stone-50 text-[1.95rem] leading-none">
            ✹
          </div>
          <p class="mt-5 text-5xl font-bold tracking-tight text-stone-900">{{ item.value }}</p>
          <h3 class="mt-2 text-3xl font-semibold leading-tight text-stone-900">{{ item.label }}</h3>
          <p class="mt-4 text-xl leading-8 text-stone-600">{{ item.description }}</p>
        </article>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const authStore = useAuthStore()
const { locale } = useI18n()
const { cmsPage } = useCmsStaticPage('home')
const SUPPORTED_LOCALES = ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'] as const
const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return SUPPORTED_LOCALES.includes(code as (typeof SUPPORTED_LOCALES)[number]) ? code : 'en'
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
  fr: {
    heroBadge: 'Wellbeing + AI + GDPR',
    heroTitle: 'Votre plateforme de bien-etre numerique, construite de facon responsable',
    heroSubtitle: 'Doisense propose un journal guide, un chat IA contextuel et des programmes structures avec des pages legales completes.',
    primaryCta: 'Creer un compte',
    secondaryCta: 'Voir les fonctionnalites',
    cards: [
      { title: 'Experience guidee', description: 'Un parcours clair de l\'onboarding au progres quotidien.' },
      { title: 'Design de confiance', description: 'Informations claires sur les donnees, la securite et les droits.' },
      { title: 'Pret pour evoluer', description: 'Pages publiques essentielles pretes pour la croissance.' },
    ],
    quickLinks: [
      { to: '/features', title: 'Fonctionnalites', description: 'Tout ce que la plateforme peut faire.' },
      { to: '/pricing', title: 'Tarifs', description: 'Plans free et premium.' },
      { to: '/about', title: 'A propos', description: 'Mission, valeurs et contexte produit.' },
      { to: '/contact', title: 'Contact', description: 'Support et canaux de communication.' },
    ],
    gdprTitle: 'GDPR dans tout le systeme',
    gdprSubtitle: 'Pages dediees a la confidentialite, aux conditions, aux cookies et aux droits des utilisateurs.',
    privacy: 'Politique de confidentialite',
    terms: 'Conditions',
    cookies: 'Cookies',
    gdprRights: 'Droits GDPR',
    seoTitle: 'Doisense - Bien-etre numerique avec IA et journal guide',
    seoDescription: 'Doisense offre un journal guide, un chat IA contextuel, des programmes structures et des pages legales completes.',
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

const heroCard = computed(() => homeCards.value[0] || text.value.cards[0])
const heroPillLeft = computed(() => `${homeCards.value.length}+ ${text.value.cards[0]?.title || 'Highlights'}`)
const heroPillRight = computed(() => text.value.quickLinks[0]?.title || 'Features')
const sectionTwoTitle = computed(() => {
  const titles: Record<string, string> = {
    ro: 'Sprijin ghidat pentru wellbeing mental, zi de zi',
    en: 'Guided support for everyday mental wellbeing',
    de: 'Gefuhrte Unterstutzung fur mentales Wohlbefinden im Alltag',
    fr: 'Un accompagnement guide pour le bien-etre mental au quotidien',
    it: 'Supporto guidato per il benessere mentale di ogni giorno',
    es: 'Apoyo guiado para el bienestar mental de cada dia',
    pl: 'Prowadzone wsparcie dla codziennego dobrostanu psychicznego',
  }
  return titles[localeCode.value] || titles.en
})
const sectionTwoDescription = computed(() => {
  const descriptions: Record<string, string> = {
    ro: 'Platforma Doisense combină jurnalul ghidat, conversațiile AI și programele structurate pentru progres real și consecvent.',
    en: 'Doisense combines guided journaling, AI conversations, and structured programs for real and sustainable progress.',
    de: 'Doisense verbindet gefuhrtes Journaling, KI-Gesprach und strukturierte Programme fur echten, nachhaltigen Fortschritt.',
    fr: 'Doisense combine journal guide, conversations IA et programmes structures pour un progres reel et durable.',
    it: 'Doisense unisce diario guidato, conversazioni AI e programmi strutturati per un progresso reale e costante.',
    es: 'Doisense combina diario guiado, conversaciones AI y programas estructurados para un progreso real y sostenible.',
    pl: 'Doisense laczy dziennik prowadzony, rozmowy AI i programy strukturalne, aby wspierac realny i trwaly progres.',
  }
  return descriptions[localeCode.value] || descriptions.en
})
const sectionTwoCta = computed(() => {
  const first = text.value.quickLinks[0]
  return {
    to: first ? localePath(first.to) : localePath('/features'),
    label: first?.title || text.value.secondaryCta,
  }
})

const impactCopy: Record<string, { badge: string; title: string }> = {
  ro: {
    badge: 'Impactul nostru în cifre',
    title: 'Vezi acoperirea, rezultatele și progresul construit cu utilizatorii noștri',
  },
  en: {
    badge: 'Our Impact In Numbers',
    title: "See The Reach, Results, And Growth We've Helped Facilitate",
  },
  de: {
    badge: 'Unser Impact in Zahlen',
    title: 'Sieh Reichweite, Ergebnisse und Wachstum, pe care le susținem împreună',
  },
  fr: {
    badge: 'Notre impact en chiffres',
    title: 'Decouvrez la portee, les resultats et la progression que nous facilitons',
  },
  it: {
    badge: 'Il nostro impatto in numeri',
    title: 'Scopri portata, risultati e crescita che aiutiamo a costruire',
  },
  es: {
    badge: 'Nuestro impacto en cifras',
    title: 'Mira el alcance, los resultados y el crecimiento que facilitamos',
  },
  pl: {
    badge: 'Nasz wpływ w liczbach',
    title: 'Zobacz zasięg, rezultaty i rozwój, które wspieramy',
  },
}

const impactText = computed(() => impactCopy[localeCode.value] || impactCopy.en)
const impactCards = computed(() => {
  const cards = homeCards.value.length ? homeCards.value : text.value.cards
  const links = text.value.quickLinks
  return [
    {
      value: `${cards.length}+`,
      label: cards[0]?.title || 'Guided experience',
      description: cards[0]?.description || text.value.heroSubtitle,
    },
    {
      value: `${links.length}+`,
      label: cards[1]?.title || 'Trust-focused design',
      description: cards[1]?.description || text.value.heroSubtitle,
    },
    {
      value: `${SUPPORTED_LOCALES.length}+`,
      label: cards[2]?.title || 'Product-ready scale',
      description: cards[2]?.description || text.value.heroSubtitle,
    },
    {
      value: `${links.length * 15}+`,
      label: links[0]?.title || 'Features',
      description: links[0]?.description || text.value.secondaryCta,
    },
  ]
})

const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
