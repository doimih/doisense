<template>
  <article class="max-w-4xl mx-auto py-10 space-y-6">
    <template v-if="hasCmsContent && cmsPage">
      <h1 class="text-4xl font-bold text-stone-900">{{ cmsPage.title }}</h1>
      <section class="bg-white border border-stone-200 rounded-xl p-5">
        <p class="text-stone-700 text-sm leading-7 whitespace-pre-line">{{ cmsPage.content }}</p>
      </section>
    </template>

    <template v-else>
      <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
      <p class="text-sm text-stone-500">{{ text.updated }}</p>

      <section v-for="section in text.sections" :key="section.title" class="bg-white border border-stone-200 rounded-xl p-5">
        <h2 class="text-xl font-semibold text-stone-900 mb-2">{{ section.title }}</h2>
        <p class="text-stone-700 text-sm leading-6">{{ section.body }}</p>
      </section>
    </template>
  </article>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})
const { cmsPage, hasCmsContent } = useLegalCmsPage('terms')

const termsCopy: Record<string, {
  title: string
  updated: string
  sections: Array<{ title: string; body: string }>
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    title: 'Termeni și condiții',
    updated: 'Ultima actualizare: 08 martie 2026',
    sections: [
      { title: '1. Acceptarea termenilor', body: 'Prin utilizarea platformei accepți acești termeni. Dacă nu ești de acord, nu utiliza serviciul.' },
      { title: '2. Contul tău', body: 'Ești responsabil pentru confidențialitatea credentialelor și pentru activitatea din contul tău.' },
      { title: '3. Utilizare permisă', body: 'Nu utiliza serviciul pentru activități ilegale, abuzive sau care încalcă drepturile altor persoane.' },
      { title: '4. Plăți și premium', body: 'Funcțiile premium sunt gestionate prin Stripe. Condițiile comerciale sunt afișate înainte de plată.' },
      { title: '5. Limitarea răspunderii', body: 'Serviciul este oferit ca instrument digital de suport și nu înlocuiește consultanța medicală/psihologică specializată.' },
    ],
    seoTitle: 'Termeni si conditii - Doisense',
    seoDescription: 'Citește termenii și condițiile de utilizare a platformei Doisense, inclusiv utilizare permisă, premium și limitarea răspunderii.',
  },
  en: {
    title: 'Terms and Conditions',
    updated: 'Last updated: March 8, 2026',
    sections: [
      { title: '1. Acceptance', body: 'By using the platform you agree to these terms. If you disagree, do not use the service.' },
      { title: '2. Your account', body: 'You are responsible for credential confidentiality and all activity under your account.' },
      { title: '3. Allowed use', body: 'Do not use the service for unlawful, abusive, or rights-infringing activities.' },
      { title: '4. Payments and premium', body: 'Premium features are handled via Stripe. Commercial terms are shown before payment confirmation.' },
      { title: '5. Liability limitation', body: 'The service is a digital support tool and does not replace professional medical or psychological care.' },
    ],
    seoTitle: 'Terms and Conditions - Doisense',
    seoDescription: 'Read Doisense terms and conditions, including allowed usage, premium access, and liability limitations.',
  },
  de: {
    title: 'Nutzungsbedingungen',
    updated: 'Letzte Aktualisierung: 08. März 2026',
    sections: [
      { title: '1. Annahme', body: 'Durch die Nutzung der Plattform stimmst du diesen Bedingungen zu. Wenn nicht, nutze den Dienst nicht.' },
      { title: '2. Dein Konto', body: 'Du bist für die Vertraulichkeit deiner Zugangsdaten und Aktivitäten in deinem Konto verantwortlich.' },
      { title: '3. Zulässige Nutzung', body: 'Nutze den Dienst nicht für rechtswidrige, missbräuchliche oder rechtsverletzende Aktivitäten.' },
      { title: '4. Zahlungen und Premium', body: 'Premium-Funktionen werden über Stripe verwaltet. Kommerzielle Bedingungen werden vor der Zahlung angezeigt.' },
      { title: '5. Haftungsbeschränkung', body: 'Der Dienst ist ein digitales Hilfsmittel und ersetzt keine professionelle medizinische oder psychologische Betreuung.' },
    ],
    seoTitle: 'Nutzungsbedingungen - Doisense',
    seoDescription: 'Lies die Doisense-Nutzungsbedingungen, einschließlich zulässiger Nutzung, Premiumzugang und Haftungsbeschränkungen.',
  },
  it: {
    title: 'Termini e condizioni',
    updated: 'Ultimo aggiornamento: 08 marzo 2026',
    sections: [
      { title: '1. Accettazione', body: 'Utilizzando la piattaforma accetti questi termini. Se non sei d’accordo, non usare il servizio.' },
      { title: '2. Il tuo account', body: 'Sei responsabile della riservatezza delle credenziali e delle attività del tuo account.' },
      { title: '3. Uso consentito', body: 'Non usare il servizio per attività illegali, abusive o che violano diritti altrui.' },
      { title: '4. Pagamenti e premium', body: 'Le funzionalità premium sono gestite tramite Stripe. Le condizioni sono mostrate prima del pagamento.' },
      { title: '5. Limitazione di responsabilità', body: 'Il servizio è uno strumento digitale di supporto e non sostituisce assistenza medica o psicologica professionale.' },
    ],
    seoTitle: 'Termini e condizioni - Doisense',
    seoDescription: 'Leggi i termini e condizioni di Doisense, inclusi uso consentito, accesso premium e limiti di responsabilità.',
  },
  es: {
    title: 'Términos y condiciones',
    updated: 'Última actualización: 08 de marzo de 2026',
    sections: [
      { title: '1. Aceptación', body: 'Al usar la plataforma aceptas estos términos. Si no estás de acuerdo, no uses el servicio.' },
      { title: '2. Tu cuenta', body: 'Eres responsable de la confidencialidad de tus credenciales y de la actividad en tu cuenta.' },
      { title: '3. Uso permitido', body: 'No uses el servicio para actividades ilegales, abusivas o que vulneren derechos de terceros.' },
      { title: '4. Pagos y premium', body: 'Las funciones premium se gestionan con Stripe. Las condiciones comerciales se muestran antes del pago.' },
      { title: '5. Limitación de responsabilidad', body: 'El servicio es una herramienta digital de apoyo y no reemplaza atención médica o psicológica profesional.' },
    ],
    seoTitle: 'Términos y condiciones - Doisense',
    seoDescription: 'Lee los términos y condiciones de Doisense, incluyendo uso permitido, acceso premium y limitaciones de responsabilidad.',
  },
  pl: {
    title: 'Regulamin',
    updated: 'Ostatnia aktualizacja: 08 marca 2026',
    sections: [
      { title: '1. Akceptacja', body: 'Korzystając z platformy akceptujesz te warunki. Jeśli się nie zgadzasz, nie korzystaj z usługi.' },
      { title: '2. Twoje konto', body: 'Odpowiadasz za poufność danych logowania i aktywność na swoim koncie.' },
      { title: '3. Dozwolone użycie', body: 'Nie używaj usługi do działań niezgodnych z prawem, nadużyć lub naruszania praw innych osób.' },
      { title: '4. Płatności i premium', body: 'Funkcje premium są obsługiwane przez Stripe. Warunki handlowe są widoczne przed płatnością.' },
      { title: '5. Ograniczenie odpowiedzialności', body: 'Usługa jest narzędziem wsparcia cyfrowego i nie zastępuje profesjonalnej opieki medycznej ani psychologicznej.' },
    ],
    seoTitle: 'Regulamin - Doisense',
    seoDescription: 'Przeczytaj regulamin Doisense, w tym zasady dozwolonego użycia, dostęp premium i ograniczenia odpowiedzialności.',
  },
}

const text = computed(() => {
  return termsCopy[localeCode.value] || termsCopy.en
})

const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
