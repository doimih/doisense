<template>
  <section class="py-16 px-4">
    <template v-if="hasCmsContent && cmsPage">
      <!-- CMS Version -->
      <div class="max-w-6xl mx-auto">
        <h1 class="text-4xl font-bold text-slate-900 mb-4">{{ cmsPage.title }}</h1>
        <section class="bg-white border border-slate-200 rounded-xl p-6">
          <p class="text-slate-700 text-base leading-7 whitespace-pre-line">{{ cmsPage.content }}</p>
        </section>
      </div>
    </template>

    <template v-else>
      <!-- Custom Layout -->
      <div class="max-w-7xl mx-auto">
        <!-- Header with Badge -->
        <div class="mb-16">
          <div class="inline-block bg-rose-100 text-rose-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
            {{ text.badge }}
          </div>
        </div>

        <!-- Main Grid Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          <!-- Left Side: Content + Images -->
          <div class="space-y-8">
            <!-- First Paragraph -->
            <p class="text-slate-700 text-base leading-7 max-w-sm">{{ text.p1 }}</p>

            <!-- Images Grid -->
            <div class="grid grid-cols-2 gap-4">
              <div class="h-64 rounded-2xl overflow-hidden border border-slate-200 bg-slate-100">
                <img
                  :src="aboutVisuals[0]"
                  alt="Wellbeing session"
                  class="w-full h-full object-cover"
                  loading="lazy"
                  decoding="async"
                />
              </div>
              <div class="h-64 rounded-2xl overflow-hidden border border-slate-200 bg-slate-100">
                <img
                  :src="aboutVisuals[1]"
                  alt="Guided emotional support"
                  class="w-full h-full object-cover"
                  loading="lazy"
                  decoding="async"
                />
              </div>
            </div>
          </div>

          <!-- Right Side: Title + Features -->
          <div class="space-y-12">
            <!-- Main Title -->
            <div>
              <h2 class="text-4xl lg:text-5xl font-bold text-slate-900 leading-tight">{{ text.mainTitle }}</h2>
            </div>

            <!-- Features Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <article
                v-for="(item, index) in text.values"
                :key="item.title"
                class="bg-white border border-slate-200 rounded-xl p-6 hover:shadow-lg transition-shadow"
              >
                <div class="mb-4 h-28 rounded-lg overflow-hidden border border-slate-200">
                  <img
                    :src="valueCardImages[index % valueCardImages.length]"
                    :alt="item.title"
                    class="h-full w-full object-cover"
                    loading="lazy"
                    decoding="async"
                  />
                </div>

                <!-- Content -->
                <h3 class="font-semibold text-slate-900 mb-2 text-lg">{{ item.title }}</h3>
                <p class="text-slate-600 text-sm leading-6">{{ item.description }}</p>
              </article>
            </div>

            <!-- Additional Paragraphs -->
            <div class="space-y-4 pt-6 border-t border-slate-200">
              <p class="text-slate-700 text-base leading-7">{{ text.p2 }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})
const { cmsPage, hasCmsContent } = useCmsStaticPage('about')

const aboutVisuals = [
  'https://images.unsplash.com/photo-1493836512294-502baa1986e2?auto=format&fit=crop&w=1200&q=80',
  'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=1200&q=80',
]

const valueCardImages = [
  'https://images.unsplash.com/photo-1493836512294-502baa1986e2?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1512428559087-560fa5ceab42?auto=format&fit=crop&w=900&q=80',
  'https://images.unsplash.com/photo-1485727749690-d091e8284ef3?auto=format&fit=crop&w=900&q=80',
]

const aboutCopy: Record<string, {
  badge: string
  title: string
  mainTitle: string
  p1: string
  p2: string
  values: Array<{ title: string; description: string }>
  images?: string[]
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    badge: 'Doisense - Despre noi',
    title: 'Despre Doisense',
    mainTitle: 'Construind spații sigure pentru creștere emoțională',
    p1: 'Doisense este o platformă digitală pentru wellbeing care combină reflecția personală, suportul conversațional AI și programe ghidate într-o experiență simplă.',
    p2: 'Scopul produsului este să ajute oamenii să își construiască rutine emoționale sănătoase și să observe progresul în timp, fără fricțiune tehnică.',
    values: [
      { title: 'Empatie', description: 'Interacțiuni prietenoase și suportive, fără ton rigid.' },
      { title: 'Claritate', description: 'Interfață simplă, pași expliciți și informații ușor de înțeles.' },
      { title: 'Responsabilitate', description: 'Respect pentru confidențialitate, securitate și conformitate GDPR.' },
      { title: 'Inovație', description: 'Evoluție continuă, adaptată nevoilor utilizatorilor.' },
    ],
    seoTitle: 'Despre Doisense - Misiune, valori, context',
    seoDescription: 'Află misiunea Doisense, valorile produsului și cum construim o platformă de wellbeing digital responsabilă.',
  },
  en: {
    badge: 'Doisense - About',
    title: 'About Doisense',
    mainTitle: 'Building Safe Spaces For Emotional Growth',
    p1: 'Doisense is a digital wellbeing platform combining personal reflection, AI conversational support, and guided programs into one simple experience.',
    p2: 'The product helps people build healthier emotional routines and track progress over time without technical friction.',
    values: [
      { title: 'Empathy', description: 'Supportive interactions without a robotic tone.' },
      { title: 'Clarity', description: 'Simple interface, explicit steps, and understandable information.' },
      { title: 'Responsibility', description: 'Respect for privacy, security, and GDPR compliance.' },
      { title: 'Innovation', description: 'Continuous evolution, responsive to user needs.' },
    ],
    seoTitle: 'About Doisense - Mission, values, context',
    seoDescription: 'Learn the Doisense mission, product values, and how we build a responsible digital wellbeing platform.',
  },
  de: {
    badge: 'Doisense - Über uns',
    title: 'Über Doisense',
    mainTitle: 'Sichere Räume für emotionales Wachstum schaffen',
    p1: 'Doisense ist eine digitale Wellbeing-Plattform, die persönliche Reflexion, KI-Konversationen und geführte Programme verbindet.',
    p2: 'Unser Ziel ist es, gesunde emotionale Routinen aufzubauen und Fortschritt ohne technische Hürden sichtbar zu machen.',
    values: [
      { title: 'Empathie', description: 'Unterstützende und freundliche Interaktionen ohne starre Sprache.' },
      { title: 'Klarheit', description: 'Einfache Oberfläche, klare Schritte und verständliche Informationen.' },
      { title: 'Verantwortung', description: 'Respekt für Datenschutz, Sicherheit und DSGVO-Konformität.' },
      { title: 'Innovation', description: 'Kontinuierliche Weiterentwicklung, responsiv auf Nutzerbedürfnisse.' },
    ],
    seoTitle: 'Über Doisense - Mission, Werte, Kontext',
    seoDescription: 'Erfahre mehr über die Doisense-Mission, Produktwerte und den verantwortungsvollen Aufbau der Plattform.',
  },
  fr: {
    badge: 'Doisense - A propos',
    title: 'A propos de Doisense',
    mainTitle: 'Créer des espaces sûrs pour la croissance émotionnelle',
    p1: 'Doisense est une plateforme numérique de bien-être qui combine réflexion personnelle, support conversationnel IA et programmes guidés.',
    p2: 'Le produit aide à construire des routines émotionnelles saines et à suivre les progrès sans friction technique.',
    values: [
      { title: 'Empathie', description: 'Interactions bienveillantes et utiles, sans ton robotique.' },
      { title: 'Clarté', description: 'Interface simple, étapes explicites et informations faciles à comprendre.' },
      { title: 'Responsabilité', description: 'Respect de la confidentialité, de la sécurité et de la conformité RGPD.' },
      { title: 'Innovation', description: 'Évolution continue, responsive aux besoins des utilisateurs.' },
    ],
    seoTitle: 'A propos de Doisense - Mission, valeurs, contexte',
    seoDescription: 'Découvrez la mission de Doisense, les valeurs du produit et notre approche responsable du bien-être numérique.',
  },
  it: {
    badge: 'Doisense - Chi siamo',
    title: 'Chi è Doisense',
    mainTitle: 'Creare spazi sicuri per la crescita emotiva',
    p1: 'Doisense è una piattaforma digitale di benessere che unisce riflessione personale, supporto AI conversazionale e programmi guidati.',
    p2: 'Il prodotto aiuta a costruire routine emotive sane e a monitorare i progressi senza attrito tecnico.',
    values: [
      { title: 'Empatia', description: 'Interazioni di supporto, con tono naturale e umano.' },
      { title: 'Chiarezza', description: 'Interfaccia semplice, passi espliciti e informazioni comprensibili.' },
      { title: 'Responsabilità', description: 'Rispetto per privacy, sicurezza e conformità GDPR.' },
      { title: 'Innovazione', description: 'Evoluzione continua, responsive alle esigenze degli utenti.' },
    ],
    seoTitle: 'Doisense - Missione, valori e contesto',
    seoDescription: 'Scopri la missione di Doisense, i valori del prodotto e come costruiamo una piattaforma digitale responsabile.',
  },
  es: {
    badge: 'Doisense - Sobre nosotros',
    title: 'Sobre Doisense',
    mainTitle: 'Crear espacios seguros para el crecimiento emocional',
    p1: 'Doisense es una plataforma digital de bienestar que combina reflexión personal, soporte conversacional AI y programas guiados.',
    p2: 'El producto ayuda a construir rutinas emocionales saludables y seguir el progreso sin fricción técnica.',
    values: [
      { title: 'Empatía', description: 'Interacciones cercanas y de apoyo, sin tono robótico.' },
      { title: 'Claridad', description: 'Interfaz simple, pasos claros e información fácil de entender.' },
      { title: 'Responsabilidad', description: 'Respeto por privacidad, seguridad y cumplimiento GDPR.' },
      { title: 'Innovación', description: 'Evolución continua, responsive a las necesidades de los usuarios.' },
    ],
    seoTitle: 'Sobre Doisense - Misión, valores y contexto',
    seoDescription: 'Conoce la misión de Doisense, los valores del producto y cómo construimos una plataforma digital responsable.',
  },
  pl: {
    badge: 'Doisense - O nas',
    title: 'O Doisense',
    mainTitle: 'Tworzenie bezpiecznych przestrzeni dla rozwoju emocjonalnego',
    p1: 'Doisense to cyfrowa platforma wellbeing łącząca refleksję osobistą, wsparcie konwersacyjne AI i programy prowadzone.',
    p2: 'Produkt pomaga budować zdrowe nawyki emocjonalne i śledzić postępy bez technicznych barier.',
    values: [
      { title: 'Empatia', description: 'Wspierające interakcje bez sztywnego, technicznego tonu.' },
      { title: 'Przejrzystość', description: 'Prosty interfejs, jasne kroki i zrozumiałe informacje.' },
      { title: 'Odpowiedzialność', description: 'Szacunek dla prywatności, bezpieczeństwa i zgodności GDPR.' },
      { title: 'Innowacja', description: 'Ciągły rozwój, responsywny na potrzeby użytkowników.' },
    ],
    seoTitle: 'O Doisense - Misja, wartości, kontekst',
    seoDescription: 'Poznaj misję Doisense, wartości produktu i sposób budowania odpowiedzialnej platformy cyfrowej.',
  },
}

const text = computed(() => aboutCopy[localeCode.value] || aboutCopy.en)
const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
