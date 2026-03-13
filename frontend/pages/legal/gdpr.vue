<template>
  <article class="max-w-4xl mx-auto py-10 space-y-6">
    <template v-if="hasCmsContent && cmsContent">
      <h1 class="text-4xl font-bold text-stone-900">{{ cmsContent.title }}</h1>
      <section class="bg-white border border-stone-200 rounded-xl p-5">
        <p class="text-stone-700 text-sm leading-7 whitespace-pre-line">{{ cmsContent.content }}</p>
      </section>
    </template>

    <template v-else>
      <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
      <p class="text-stone-600">{{ text.subtitle }}</p>

      <section class="bg-white border border-stone-200 rounded-xl p-5">
        <h2 class="text-xl font-semibold text-stone-900 mb-3">{{ text.rightsTitle }}</h2>
        <ul class="space-y-2 text-sm text-stone-700">
          <li v-for="right in text.rights" :key="right">• {{ right }}</li>
        </ul>
      </section>

      <section class="bg-stone-900 text-white rounded-xl p-5 space-y-2">
        <h2 class="text-xl font-semibold">{{ text.requestTitle }}</h2>
        <p class="text-sm text-stone-100">{{ text.requestText }}</p>
        <p class="text-sm">privacy@doisense.eu</p>
        <p class="text-xs text-stone-200">{{ text.requestNote }}</p>
      </section>
    </template>
  </article>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})
const { cmsPage, hasCmsContent } = useLegalCmsPage('gdpr')
const cmsContent = computed(() => cmsPage.value as { title: string; content: string } | null)

const copy: Record<string, {
  title: string
  subtitle: string
  rightsTitle: string
  rights: string[]
  requestTitle: string
  requestText: string
  requestNote: string
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    title: 'Drepturile tale GDPR',
    subtitle: 'Ai control asupra datelor tale personale. Poți trimite solicitări în orice moment.',
    rightsTitle: 'Drepturi principale',
    rights: [
      'Drept de acces la datele personale prelucrate.',
      'Drept la rectificarea datelor inexacte.',
      'Drept la ștergere („dreptul de a fi uitat”), când se aplică.',
      'Drept la restricționarea prelucrării.',
      'Drept la portabilitatea datelor într-un format utilizabil.',
      'Drept de opoziție la anumite tipuri de prelucrare.',
    ],
    requestTitle: 'Cum trimiți o solicitare',
    requestText: 'Pentru exportul datelor și ștergerea contului poți folosi direct pagina Profil. Pentru rectificare, opoziție sau cereri speciale, trimite un email cu subiectul "GDPR Request" și detalii despre cererea ta.',
    requestNote: 'Putem solicita verificare suplimentară a identității pentru a proteja datele contului tău.',
    seoTitle: 'Drepturi GDPR - Doisense',
    seoDescription: 'Consultă drepturile tale GDPR în platforma Doisense și pașii pentru a trimite cereri privind datele personale.',
  },
  en: {
    title: 'Your GDPR Rights',
    subtitle: 'You remain in control of your personal data and can submit requests at any time.',
    rightsTitle: 'Core rights',
    rights: [
      'Right of access to your personal data.',
      'Right to rectification of inaccurate data.',
      'Right to erasure (right to be forgotten), where applicable.',
      'Right to restriction of processing.',
      'Right to data portability in a usable format.',
      'Right to object to certain processing activities.',
    ],
    requestTitle: 'How to submit a request',
    requestText: 'For data export and account deletion you can use your Profile page directly. For rectification, objection, or special requests, send an email with subject "GDPR Request" and details of your request.',
    requestNote: 'We may request additional identity verification to protect your account data.',
    seoTitle: 'GDPR Rights - Doisense',
    seoDescription: 'Review your GDPR rights in Doisense and how to submit personal data requests.',
  },
  de: {
    title: 'Deine DSGVO-Rechte',
    subtitle: 'Du behältst die Kontrolle über deine personenbezogenen Daten und kannst jederzeit Anfragen stellen.',
    rightsTitle: 'Wesentliche Rechte',
    rights: [
      'Recht auf Auskunft über deine personenbezogenen Daten.',
      'Recht auf Berichtigung unrichtiger Daten.',
      'Recht auf Löschung (Recht auf Vergessenwerden), soweit anwendbar.',
      'Recht auf Einschränkung der Verarbeitung.',
      'Recht auf Datenübertragbarkeit in einem nutzbaren Format.',
      'Recht auf Widerspruch gegen bestimmte Verarbeitungen.',
    ],
    requestTitle: 'So stellst du eine Anfrage',
    requestText: 'Sende eine E-Mail mit dem Betreff "GDPR Request" und Details zu deiner Anfrage.',
    requestNote: 'Zum Schutz deiner Kontodaten können wir eine zusätzliche Identitätsprüfung verlangen.',
    seoTitle: 'DSGVO-Rechte - Doisense',
    seoDescription: 'Sieh dir deine DSGVO-Rechte in Doisense an und erfahre, wie du Anfragen zu personenbezogenen Daten einreichst.',
  },
  fr: {
    title: 'Vos droits GDPR',
    subtitle: 'Vous gardez le controle de vos donnees personnelles et pouvez envoyer des demandes a tout moment.',
    rightsTitle: 'Droits principaux',
    rights: [
      'Droit d\'acces a vos donnees personnelles.',
      'Droit de rectification des donnees inexactes.',
      'Droit a l\'effacement (droit a l\'oubli), lorsque applicable.',
      'Droit a la limitation du traitement.',
      'Droit a la portabilite des donnees dans un format exploitable.',
      'Droit d\'opposition a certains traitements.',
    ],
    requestTitle: 'Comment envoyer une demande',
    requestText: 'Envoyez un email avec l\'objet "GDPR Request" et les details de votre demande.',
    requestNote: 'Nous pouvons demander une verification d\'identite supplementaire pour proteger les donnees de votre compte.',
    seoTitle: 'Droits GDPR - Doisense',
    seoDescription: 'Consultez vos droits GDPR dans Doisense et la procedure pour envoyer des demandes sur vos donnees personnelles.',
  },
  it: {
    title: 'I tuoi diritti GDPR',
    subtitle: 'Hai il controllo dei tuoi dati personali e puoi inviare richieste in qualsiasi momento.',
    rightsTitle: 'Diritti principali',
    rights: [
      'Diritto di accesso ai tuoi dati personali.',
      'Diritto di rettifica dei dati inesatti.',
      'Diritto alla cancellazione (diritto all’oblio), ove applicabile.',
      'Diritto alla limitazione del trattamento.',
      'Diritto alla portabilità dei dati in formato utilizzabile.',
      'Diritto di opposizione ad alcuni trattamenti.',
    ],
    requestTitle: 'Come inviare una richiesta',
    requestText: 'Invia un’email con oggetto "GDPR Request" e i dettagli della tua richiesta.',
    requestNote: 'Potremmo richiedere una verifica aggiuntiva dell’identità per proteggere i dati del tuo account.',
    seoTitle: 'Diritti GDPR - Doisense',
    seoDescription: 'Consulta i tuoi diritti GDPR in Doisense e come inviare richieste sui dati personali.',
  },
  es: {
    title: 'Tus derechos GDPR',
    subtitle: 'Mantienes el control de tus datos personales y puedes enviar solicitudes en cualquier momento.',
    rightsTitle: 'Derechos principales',
    rights: [
      'Derecho de acceso a tus datos personales.',
      'Derecho de rectificación de datos inexactos.',
      'Derecho de supresión (derecho al olvido), cuando aplique.',
      'Derecho a la limitación del tratamiento.',
      'Derecho a la portabilidad de datos en formato utilizable.',
      'Derecho de oposición a determinados tratamientos.',
    ],
    requestTitle: 'Cómo enviar una solicitud',
    requestText: 'Envía un email con asunto "GDPR Request" y detalles de tu solicitud.',
    requestNote: 'Podemos solicitar verificación adicional de identidad para proteger los datos de tu cuenta.',
    seoTitle: 'Derechos GDPR - Doisense',
    seoDescription: 'Revisa tus derechos GDPR en Doisense y cómo enviar solicitudes sobre datos personales.',
  },
  pl: {
    title: 'Twoje prawa GDPR',
    subtitle: 'Masz kontrolę nad swoimi danymi osobowymi i możesz składać wnioski w dowolnym momencie.',
    rightsTitle: 'Główne prawa',
    rights: [
      'Prawo dostępu do swoich danych osobowych.',
      'Prawo do sprostowania nieprawidłowych danych.',
      'Prawo do usunięcia danych (prawo do bycia zapomnianym), gdy ma zastosowanie.',
      'Prawo do ograniczenia przetwarzania.',
      'Prawo do przenoszenia danych w użytecznym formacie.',
      'Prawo sprzeciwu wobec określonych form przetwarzania.',
    ],
    requestTitle: 'Jak złożyć wniosek',
    requestText: 'Wyślij email z tematem "GDPR Request" i szczegółami wniosku.',
    requestNote: 'Możemy poprosić o dodatkową weryfikację tożsamości, aby chronić dane konta.',
    seoTitle: 'Prawa GDPR - Doisense',
    seoDescription: 'Sprawdź swoje prawa GDPR w Doisense i dowiedz się, jak składać wnioski dotyczące danych osobowych.',
  },
}

const text = computed(() => {
  return copy[localeCode.value] || copy.en
})

const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
