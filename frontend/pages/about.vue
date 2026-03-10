<template>
  <section class="max-w-4xl mx-auto py-10 space-y-6">
    <template v-if="hasCmsContent && cmsPage">
      <h1 class="text-4xl font-bold text-stone-900">{{ cmsPage.title }}</h1>
      <section class="bg-white border border-stone-200 rounded-xl p-5">
        <p class="text-stone-700 text-sm leading-7 whitespace-pre-line">{{ cmsPage.content }}</p>
      </section>
    </template>

    <template v-else>
      <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
      <p class="text-stone-700 leading-7">{{ text.p1 }}</p>
      <p class="text-stone-700 leading-7">{{ text.p2 }}</p>
      <p class="text-stone-700 leading-7">{{ text.p3 }}</p>

      <div class="grid gap-4 md:grid-cols-3">
        <article v-for="item in text.values" :key="item.title" class="bg-white border border-stone-200 rounded-xl p-4">
          <h2 class="font-semibold text-stone-900 mb-2">{{ item.title }}</h2>
          <p class="text-sm text-stone-600">{{ item.description }}</p>
        </article>
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

const aboutCopy: Record<string, {
  title: string
  p1: string
  p2: string
  p3: string
  values: Array<{ title: string; description: string }>
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    title: 'Despre Doisense',
    p1: 'Doisense este o platformă digitală pentru wellbeing care combină reflecția personală, suportul conversațional AI și programe ghidate într-o experiență simplă.',
    p2: 'Scopul produsului este să ajute oamenii să își construiască rutine emoționale sănătoase și să observe progresul în timp, fără fricțiune tehnică.',
    p3: 'Construim responsabil: transparență pe date, control pentru utilizator și o arhitectură care poate evolua în siguranță.',
    values: [
      { title: 'Empatie', description: 'Interacțiuni prietenoase și suportive, fără ton rigid.' },
      { title: 'Claritate', description: 'Interfață simplă, pași expliciți și informații ușor de înțeles.' },
      { title: 'Responsabilitate', description: 'Respect pentru confidențialitate, securitate și conformitate GDPR.' },
    ],
    seoTitle: 'Despre Doisense - Misiune, valori, context',
    seoDescription: 'Află misiunea Doisense, valorile produsului și cum construim o platformă de wellbeing digital responsabilă.',
  },
  en: {
    title: 'About Doisense',
    p1: 'Doisense is a digital wellbeing platform combining personal reflection, AI conversational support, and guided programs into one simple experience.',
    p2: 'The product helps people build healthier emotional routines and track progress over time without technical friction.',
    p3: 'We build responsibly: data transparency, user control, and architecture designed for safe evolution.',
    values: [
      { title: 'Empathy', description: 'Supportive interactions without a robotic tone.' },
      { title: 'Clarity', description: 'Simple interface, explicit steps, and understandable information.' },
      { title: 'Responsibility', description: 'Respect for privacy, security, and GDPR compliance.' },
    ],
    seoTitle: 'About Doisense - Mission, values, context',
    seoDescription: 'Learn the Doisense mission, product values, and how we build a responsible digital wellbeing platform.',
  },
  de: {
    title: 'Über Doisense',
    p1: 'Doisense ist eine digitale Wellbeing-Plattform, die persönliche Reflexion, KI-Konversationen und geführte Programme verbindet.',
    p2: 'Unser Ziel ist es, gesunde emotionale Routinen aufzubauen und Fortschritt ohne technische Hürden sichtbar zu machen.',
    p3: 'Wir bauen verantwortungsvoll: Datentransparenz, Nutzerkontrolle und sichere, skalierbare Architektur.',
    values: [
      { title: 'Empathie', description: 'Unterstützende und freundliche Interaktionen ohne starre Sprache.' },
      { title: 'Klarheit', description: 'Einfache Oberfläche, klare Schritte und verständliche Informationen.' },
      { title: 'Verantwortung', description: 'Respekt für Datenschutz, Sicherheit und DSGVO-Konformität.' },
    ],
    seoTitle: 'Über Doisense - Mission, Werte, Kontext',
    seoDescription: 'Erfahre mehr über die Doisense-Mission, Produktwerte und den verantwortungsvollen Aufbau der Plattform.',
  },
  fr: {
    title: 'A propos de Doisense',
    p1: 'Doisense est une plateforme numerique de bien-etre qui combine reflexion personnelle, support conversationnel IA et programmes guides.',
    p2: 'Le produit aide a construire des routines emotionnelles saines et a suivre les progres sans friction technique.',
    p3: 'Nous construisons de facon responsable: transparence des donnees, controle utilisateur et architecture securisee.',
    values: [
      { title: 'Empathie', description: 'Interactions bienveillantes et utiles, sans ton robotique.' },
      { title: 'Clarte', description: 'Interface simple, etapes explicites et informations faciles a comprendre.' },
      { title: 'Responsabilite', description: 'Respect de la confidentialite, de la securite et de la conformite GDPR.' },
    ],
    seoTitle: 'A propos de Doisense - Mission, valeurs, contexte',
    seoDescription: 'Decouvrez la mission de Doisense, les valeurs du produit et notre approche responsable du bien-etre numerique.',
  },
  it: {
    title: 'Chi è Doisense',
    p1: 'Doisense è una piattaforma digitale di benessere che unisce riflessione personale, supporto AI conversazionale e programmi guidati.',
    p2: 'Il prodotto aiuta a costruire routine emotive sane e a monitorare i progressi senza attrito tecnico.',
    p3: 'Costruiamo in modo responsabile: trasparenza sui dati, controllo utente e architettura sicura.',
    values: [
      { title: 'Empatia', description: 'Interazioni di supporto, con tono naturale e umano.' },
      { title: 'Chiarezza', description: 'Interfaccia semplice, passi espliciti e informazioni comprensibili.' },
      { title: 'Responsabilità', description: 'Rispetto per privacy, sicurezza e conformità GDPR.' },
    ],
    seoTitle: 'Doisense - Missione, valori e contesto',
    seoDescription: 'Scopri la missione di Doisense, i valori del prodotto e come costruiamo una piattaforma digitale responsabile.',
  },
  es: {
    title: 'Sobre Doisense',
    p1: 'Doisense es una plataforma digital de bienestar que combina reflexión personal, soporte conversacional AI y programas guiados.',
    p2: 'El producto ayuda a construir rutinas emocionales saludables y seguir el progreso sin fricción técnica.',
    p3: 'Construimos con responsabilidad: transparencia de datos, control del usuario y arquitectura segura.',
    values: [
      { title: 'Empatía', description: 'Interacciones cercanas y de apoyo, sin tono robótico.' },
      { title: 'Claridad', description: 'Interfaz simple, pasos claros e información fácil de entender.' },
      { title: 'Responsabilidad', description: 'Respeto por privacidad, seguridad y cumplimiento GDPR.' },
    ],
    seoTitle: 'Sobre Doisense - Misión, valores y contexto',
    seoDescription: 'Conoce la misión de Doisense, los valores del producto y cómo construimos una plataforma digital responsable.',
  },
  pl: {
    title: 'O Doisense',
    p1: 'Doisense to cyfrowa platforma wellbeing łącząca refleksję osobistą, wsparcie konwersacyjne AI i programy prowadzone.',
    p2: 'Produkt pomaga budować zdrowe nawyki emocjonalne i śledzić postępy bez technicznych barier.',
    p3: 'Tworzymy odpowiedzialnie: przejrzystość danych, kontrola użytkownika i bezpieczna architektura.',
    values: [
      { title: 'Empatia', description: 'Wspierające interakcje bez sztywnego, technicznego tonu.' },
      { title: 'Przejrzystość', description: 'Prosty interfejs, jasne kroki i zrozumiałe informacje.' },
      { title: 'Odpowiedzialność', description: 'Szacunek dla prywatności, bezpieczeństwa i zgodności GDPR.' },
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
