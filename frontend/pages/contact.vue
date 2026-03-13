<template>
  <div class="-mt-6 pb-8">
    <section class="relative left-1/2 right-1/2 -mx-[50vw] w-screen overflow-hidden bg-stone-100 text-stone-900">
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(125deg,#f8fafc_0%,#f1f5f9_42%,#e0f2fe_100%)]" />
      <div class="pointer-events-none absolute -right-20 -top-16 h-52 w-52 rounded-full bg-sky-200/50 blur-3xl" />
      <div class="pointer-events-none absolute -left-16 bottom-0 h-44 w-44 rounded-full bg-amber-100/60 blur-3xl" />
      <div class="relative mx-auto max-w-5xl px-4 py-12 sm:px-6 md:py-16 lg:px-8">
        <div class="w-full space-y-6 rounded-[2rem] border border-stone-200 bg-white/86 p-6 shadow-[0_30px_90px_-40px_rgba(12,74,110,0.35)] backdrop-blur-[1px] md:p-9">
          <p class="inline-flex items-center rounded-full border border-stone-300 bg-white px-4 py-2 text-sm font-semibold text-stone-900">
            {{ text.badge }}
          </p>
          <h1 class="text-4xl font-bold leading-[1.05] tracking-tight text-stone-900 md:text-6xl lg:text-7xl">{{ text.title }}</h1>
          <p class="max-w-2xl text-base leading-8 text-stone-800 md:text-lg">{{ text.subtitle }}</p>
        </div>
      </div>
    </section>

    <section class="max-w-5xl mx-auto py-8 md:py-12">
      <div class="rounded-3xl border border-stone-300 bg-stone-100/70 p-6 md:p-10 lg:p-14 space-y-8">

        <form class="space-y-6" @submit.prevent="submitForm">
        <div class="grid gap-5 md:grid-cols-2">
          <label class="space-y-2">
            <span class="text-base font-semibold text-stone-900">{{ text.fullNameLabel }}</span>
            <input
              v-model="form.fullName"
              type="text"
              class="w-full rounded-xl border border-stone-300 bg-white px-4 py-4 text-stone-900 outline-none transition focus:border-stone-500"
              :placeholder="text.fullNamePlaceholder"
              autocomplete="name"
              required
            >
          </label>

          <label class="space-y-2">
            <span class="text-base font-semibold text-stone-900">{{ text.emailLabel }}</span>
            <input
              v-model="form.email"
              type="email"
              class="w-full rounded-xl border border-stone-300 bg-white px-4 py-4 text-stone-900 outline-none transition focus:border-stone-500"
              :placeholder="text.emailPlaceholder"
              autocomplete="email"
              required
            >
          </label>
        </div>

        <label class="space-y-2 block">
          <span class="text-base font-semibold text-stone-900">{{ text.subjectLabel }}</span>
          <input
            v-model="form.subject"
            type="text"
            class="w-full rounded-xl border border-stone-300 bg-white px-4 py-4 text-stone-900 outline-none transition focus:border-stone-500"
            :placeholder="text.subjectPlaceholder"
            required
          >
        </label>

        <label class="space-y-2 block">
          <span class="text-base font-semibold text-stone-900">{{ text.messageLabel }}</span>
          <textarea
            v-model="form.message"
            rows="5"
            class="w-full rounded-xl border border-stone-300 bg-white px-4 py-4 text-stone-900 outline-none transition focus:border-stone-500"
            :placeholder="text.messagePlaceholder"
            required
          />
        </label>

        <p v-if="errorMessage" class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ errorMessage }}
        </p>
        <p v-if="successMessage" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {{ successMessage }}
        </p>

        <button
          type="submit"
          :disabled="submitting"
          class="inline-flex min-w-[220px] items-center justify-center rounded-xl bg-black px-5 py-3 text-sm font-semibold text-white transition hover:bg-stone-900 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ submitting ? text.sendingAction : text.sendAction }}
        </button>
        </form>

        <div class="grid gap-4 md:grid-cols-3 pt-2">
        <article class="rounded-xl border border-stone-300 bg-white px-4 py-4">
          <h2 class="text-sm font-semibold text-stone-900">{{ text.supportTitle }}</h2>
          <p class="text-sm text-stone-700 mt-1">{{ text.supportText }}</p>
        </article>
        <article class="rounded-xl border border-stone-300 bg-white px-4 py-4">
          <h2 class="text-sm font-semibold text-stone-900">{{ text.gdprTitle }}</h2>
          <p class="text-sm text-stone-700 mt-1">{{ text.gdprText }}</p>
        </article>
        <article class="rounded-xl border border-stone-300 bg-white px-4 py-4">
          <h2 class="text-sm font-semibold text-stone-900">{{ text.responseTitle }}</h2>
          <p class="text-sm text-stone-700 mt-1">{{ text.responseText }}</p>
        </article>
        </div>

        <p class="text-xs text-stone-500">
          {{ text.note }}
          <NuxtLink :to="localePath('/legal/gdpr')" class="underline">{{ text.gdprLink }}</NuxtLink>
        </p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const { fetchApi } = useApi()
const { locale } = useI18n()
const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

const copy: Record<string, {
  title: string
  badge: string
  subtitle: string
  fullNameLabel: string
  fullNamePlaceholder: string
  emailLabel: string
  emailPlaceholder: string
  subjectLabel: string
  subjectPlaceholder: string
  messageLabel: string
  messagePlaceholder: string
  sendAction: string
  sendingAction: string
  successMessage: string
  sendFailedMessage: string
  recaptchaNotReady: string
  recaptchaFailed: string
  supportTitle: string
  supportText: string
  gdprTitle: string
  gdprText: string
  responseTitle: string
  responseText: string
  note: string
  gdprLink: string
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    title: 'Contact',
    badge: 'Contactează-ne',
    subtitle: 'Pentru suport tehnic, întrebări comerciale sau solicitări de protecția datelor, ne poți scrie oricând.',
    fullNameLabel: 'Nume complet',
    fullNamePlaceholder: 'Introdu numele tău complet',
    emailLabel: 'Adresă de email',
    emailPlaceholder: 'Introdu adresa ta de email',
    subjectLabel: 'Subiect',
    subjectPlaceholder: 'Despre ce este mesajul?',
    messageLabel: 'Mesaj',
    messagePlaceholder: 'Scrie mesajul tău aici',
    sendAction: 'Trimite mesajul',
    sendingAction: 'Se trimite...',
    successMessage: 'Mesaj trimis cu succes. Revenim către tine cât mai curând.',
    sendFailedMessage: 'Nu am putut trimite mesajul acum.',
    recaptchaNotReady: 'Verificarea reCAPTCHA nu este gata.',
    recaptchaFailed: 'Verificarea reCAPTCHA a esuat.',
    supportTitle: 'Suport general',
    supportText: 'Email: support@doisense.eu',
    gdprTitle: 'Solicitări GDPR',
    gdprText: 'Email: privacy@doisense.eu',
    responseTitle: 'Timp de răspuns',
    responseText: 'Încercăm să răspundem în 1-3 zile lucrătoare, în funcție de complexitatea cererii.',
    note: 'Pentru drepturile tale asupra datelor personale, vezi ',
    gdprLink: 'pagina GDPR.',
    seoTitle: 'Contact Doisense - Suport si solicitari GDPR',
    seoDescription: 'Contactează echipa Doisense pentru suport tehnic, întrebări comerciale sau solicitări privind datele personale.',
  },
  en: {
    title: 'Contact',
    badge: 'Contact Us',
    subtitle: 'For technical support, commercial questions, or data protection requests, you can contact us anytime.',
    fullNameLabel: 'Full Name',
    fullNamePlaceholder: 'Enter your full name',
    emailLabel: 'Email Address',
    emailPlaceholder: 'Enter your email address',
    subjectLabel: 'Subject',
    subjectPlaceholder: 'What is this message about?',
    messageLabel: 'Message',
    messagePlaceholder: 'Type your message here',
    sendAction: 'Send Message',
    sendingAction: 'Sending...',
    successMessage: 'Message sent successfully. We will get back to you soon.',
    sendFailedMessage: 'Unable to send message right now.',
    recaptchaNotReady: 'reCAPTCHA is not ready.',
    recaptchaFailed: 'reCAPTCHA execution failed.',
    supportTitle: 'General support',
    supportText: 'Email: support@doisense.eu',
    gdprTitle: 'GDPR requests',
    gdprText: 'Email: privacy@doisense.eu',
    responseTitle: 'Response time',
    responseText: 'We aim to respond in 1-3 business days depending on request complexity.',
    note: 'For your personal data rights, see the ',
    gdprLink: 'GDPR page.',
    seoTitle: 'Contact Doisense - Support and GDPR requests',
    seoDescription: 'Contact the Doisense team for technical support, commercial questions, or personal data requests.',
  },
  de: {
    title: 'Kontakt',
    badge: 'Kontakt',
    subtitle: 'Für technischen Support, geschäftliche Fragen oder Datenschutzanfragen kannst du uns jederzeit kontaktieren.',
    fullNameLabel: 'Vollständiger Name',
    fullNamePlaceholder: 'Gib deinen vollständigen Namen ein',
    emailLabel: 'E-Mail-Adresse',
    emailPlaceholder: 'Gib deine E-Mail-Adresse ein',
    subjectLabel: 'Betreff',
    subjectPlaceholder: 'Worum geht es in deiner Nachricht?',
    messageLabel: 'Nachricht',
    messagePlaceholder: 'Schreibe hier deine Nachricht',
    sendAction: 'Nachricht senden',
    sendingAction: 'Wird gesendet...',
    successMessage: 'Nachricht erfolgreich gesendet. Wir melden uns bald bei dir.',
    sendFailedMessage: 'Nachricht konnte gerade nicht gesendet werden.',
    recaptchaNotReady: 'reCAPTCHA ist noch nicht bereit.',
    recaptchaFailed: 'reCAPTCHA-Pruefung ist fehlgeschlagen.',
    supportTitle: 'Allgemeiner Support',
    supportText: 'E-Mail: support@doisense.eu',
    gdprTitle: 'DSGVO-Anfragen',
    gdprText: 'E-Mail: privacy@doisense.eu',
    responseTitle: 'Antwortzeit',
    responseText: 'Wir antworten in der Regel innerhalb von 1-3 Werktagen, je nach Komplexität der Anfrage.',
    note: 'Für deine Datenschutzrechte siehe die ',
    gdprLink: 'DSGVO-Seite.',
    seoTitle: 'Doisense Kontakt - Support und DSGVO-Anfragen',
    seoDescription: 'Kontaktiere das Doisense-Team für technischen Support, geschäftliche Fragen oder Datenschutzanfragen.',
  },
  fr: {
    title: 'Contact',
    badge: 'Contact',
    subtitle: 'Pour le support technique, les questions commerciales ou les demandes sur les donnees personnelles, vous pouvez nous contacter a tout moment.',
    fullNameLabel: 'Nom complet',
    fullNamePlaceholder: 'Entrez votre nom complet',
    emailLabel: 'Adresse email',
    emailPlaceholder: 'Entrez votre adresse email',
    subjectLabel: 'Sujet',
    subjectPlaceholder: 'Quel est le sujet de votre message ?',
    messageLabel: 'Message',
    messagePlaceholder: 'Ecrivez votre message ici',
    sendAction: 'Envoyer le message',
    sendingAction: 'Envoi en cours...',
    successMessage: 'Message envoye avec succes. Nous revenons vers vous rapidement.',
    sendFailedMessage: 'Impossible d\'envoyer le message pour le moment.',
    recaptchaNotReady: 'reCAPTCHA n\'est pas pret.',
    recaptchaFailed: 'L\'execution de reCAPTCHA a echoue.',
    supportTitle: 'Support general',
    supportText: 'Email: support@doisense.eu',
    gdprTitle: 'Demandes GDPR',
    gdprText: 'Email: privacy@doisense.eu',
    responseTitle: 'Delai de reponse',
    responseText: 'Nous essayons de repondre sous 1 a 3 jours ouvrables selon la complexite de la demande.',
    note: 'Pour vos droits sur les donnees personnelles, consultez la ',
    gdprLink: 'page GDPR.',
    seoTitle: 'Contact Doisense - Support et demandes GDPR',
    seoDescription: 'Contactez l\'equipe Doisense pour le support technique, les questions commerciales ou les demandes de donnees personnelles.',
  },
  it: {
    title: 'Contatto',
    badge: 'Contattaci',
    subtitle: 'Per supporto tecnico, domande commerciali o richieste sulla protezione dei dati, puoi contattarci in qualsiasi momento.',
    fullNameLabel: 'Nome completo',
    fullNamePlaceholder: 'Inserisci il tuo nome completo',
    emailLabel: 'Indirizzo email',
    emailPlaceholder: 'Inserisci il tuo indirizzo email',
    subjectLabel: 'Oggetto',
    subjectPlaceholder: 'Di cosa tratta il messaggio?',
    messageLabel: 'Messaggio',
    messagePlaceholder: 'Scrivi qui il tuo messaggio',
    sendAction: 'Invia messaggio',
    sendingAction: 'Invio in corso...',
    successMessage: 'Messaggio inviato con successo. Ti risponderemo presto.',
    sendFailedMessage: 'Impossibile inviare il messaggio in questo momento.',
    recaptchaNotReady: 'reCAPTCHA non e pronto.',
    recaptchaFailed: 'Esecuzione reCAPTCHA non riuscita.',
    supportTitle: 'Supporto generale',
    supportText: 'Email: support@doisense.eu',
    gdprTitle: 'Richieste GDPR',
    gdprText: 'Email: privacy@doisense.eu',
    responseTitle: 'Tempi di risposta',
    responseText: 'Cerchiamo di rispondere entro 1-3 giorni lavorativi, in base alla complessità della richiesta.',
    note: 'Per i tuoi diritti sui dati personali, consulta la ',
    gdprLink: 'pagina GDPR.',
    seoTitle: 'Contatto Doisense - Supporto e richieste GDPR',
    seoDescription: 'Contatta il team Doisense per supporto tecnico, domande commerciali o richieste sui dati personali.',
  },
  es: {
    title: 'Contacto',
    badge: 'Contáctanos',
    subtitle: 'Para soporte técnico, preguntas comerciales o solicitudes de protección de datos, puedes escribirnos en cualquier momento.',
    fullNameLabel: 'Nombre completo',
    fullNamePlaceholder: 'Introduce tu nombre completo',
    emailLabel: 'Correo electrónico',
    emailPlaceholder: 'Introduce tu correo electrónico',
    subjectLabel: 'Asunto',
    subjectPlaceholder: '¿De qué trata este mensaje?',
    messageLabel: 'Mensaje',
    messagePlaceholder: 'Escribe tu mensaje aquí',
    sendAction: 'Enviar mensaje',
    sendingAction: 'Enviando...',
    successMessage: 'Mensaje enviado correctamente. Te responderemos pronto.',
    sendFailedMessage: 'No se pudo enviar el mensaje en este momento.',
    recaptchaNotReady: 'reCAPTCHA no esta listo.',
    recaptchaFailed: 'La ejecucion de reCAPTCHA ha fallado.',
    supportTitle: 'Soporte general',
    supportText: 'Email: support@doisense.eu',
    gdprTitle: 'Solicitudes GDPR',
    gdprText: 'Email: privacy@doisense.eu',
    responseTitle: 'Tiempo de respuesta',
    responseText: 'Intentamos responder en 1-3 días hábiles, según la complejidad de la solicitud.',
    note: 'Para tus derechos sobre datos personales, consulta la ',
    gdprLink: 'página GDPR.',
    seoTitle: 'Contacto Doisense - Soporte y solicitudes GDPR',
    seoDescription: 'Contacta al equipo de Doisense para soporte técnico, preguntas comerciales o solicitudes de datos personales.',
  },
  pl: {
    title: 'Kontakt',
    badge: 'Skontaktuj się z nami',
    subtitle: 'W sprawie wsparcia technicznego, pytań handlowych lub wniosków dotyczących ochrony danych możesz skontaktować się z nami w dowolnym momencie.',
    fullNameLabel: 'Imię i nazwisko',
    fullNamePlaceholder: 'Wpisz swoje imię i nazwisko',
    emailLabel: 'Adres email',
    emailPlaceholder: 'Wpisz swój adres email',
    subjectLabel: 'Temat',
    subjectPlaceholder: 'Czego dotyczy wiadomość?',
    messageLabel: 'Wiadomość',
    messagePlaceholder: 'Wpisz treść wiadomości',
    sendAction: 'Wyślij wiadomość',
    sendingAction: 'Wysyłanie...',
    successMessage: 'Wiadomość została wysłana. Odpowiemy wkrótce.',
    sendFailedMessage: 'Nie mozna teraz wyslac wiadomosci.',
    recaptchaNotReady: 'reCAPTCHA nie jest jeszcze gotowe.',
    recaptchaFailed: 'Wykonanie reCAPTCHA nie powiodlo sie.',
    supportTitle: 'Wsparcie ogólne',
    supportText: 'Email: support@doisense.eu',
    gdprTitle: 'Wnioski GDPR',
    gdprText: 'Email: privacy@doisense.eu',
    responseTitle: 'Czas odpowiedzi',
    responseText: 'Staramy się odpowiadać w ciągu 1-3 dni roboczych, zależnie od złożoności sprawy.',
    note: 'Aby poznać prawa dotyczące danych osobowych, zobacz ',
    gdprLink: 'stronę GDPR.',
    seoTitle: 'Kontakt Doisense - Wsparcie i wnioski GDPR',
    seoDescription: 'Skontaktuj się z zespołem Doisense w sprawie wsparcia technicznego, pytań handlowych lub danych osobowych.',
  },
}

const text = computed(() => {
  return copy[localeCode.value] || copy.en
})

const form = reactive({
  fullName: '',
  email: '',
  subject: '',
  message: '',
})

const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const recaptchaEnabled = ref(false)
const recaptchaSiteKey = ref('')

declare global {
  interface Window {
    grecaptcha?: {
      ready: (cb: () => void) => void
      execute: (siteKey: string, options: { action: string }) => Promise<string>
    }
  }
}

function loadRecaptchaScript(siteKey: string) {
  if (!import.meta.client || !siteKey) return
  if (document.querySelector('script[data-recaptcha="doisense"]')) return

  const script = document.createElement('script')
  script.src = `https://www.google.com/recaptcha/api.js?render=${encodeURIComponent(siteKey)}`
  script.async = true
  script.defer = true
  script.setAttribute('data-recaptcha', 'doisense')
  document.head.appendChild(script)
}

async function getRecaptchaToken() {
  if (!recaptchaEnabled.value || !recaptchaSiteKey.value || !import.meta.client) {
    return ''
  }

  const instance = window.grecaptcha
  if (!instance) {
    throw new Error(text.value.recaptchaNotReady)
  }

  return new Promise<string>((resolve, reject) => {
    instance.ready(async () => {
      try {
        const token = await instance.execute(recaptchaSiteKey.value, { action: 'contact_form' })
        resolve(token)
      } catch {
        reject(new Error(text.value.recaptchaFailed))
      }
    })
  })
}

async function submitForm() {
  if (submitting.value) return

  errorMessage.value = ''
  successMessage.value = ''
  submitting.value = true
  try {
    const recaptchaToken = await getRecaptchaToken()
    await fetchApi('/contact/submit', {
      method: 'POST',
      body: {
        full_name: form.fullName,
        email: form.email,
        subject: form.subject,
        message: form.message,
        recaptcha_token: recaptchaToken,
      },
    })

    successMessage.value = text.value.successMessage
    form.fullName = ''
    form.email = ''
    form.subject = ''
    form.message = ''
  } catch (error: any) {
    errorMessage.value = error?.data?.detail || error?.message || text.value.sendFailedMessage
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const config = await fetchApi<{ recaptcha_enabled?: boolean; recaptcha_site_key?: string }>('/contact/config')
    recaptchaEnabled.value = Boolean(config?.recaptcha_enabled)
    recaptchaSiteKey.value = config?.recaptcha_site_key || ''
    if (recaptchaEnabled.value && recaptchaSiteKey.value) {
      loadRecaptchaScript(recaptchaSiteKey.value)
    }
  } catch {
    recaptchaEnabled.value = false
    recaptchaSiteKey.value = ''
  }
})

const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
