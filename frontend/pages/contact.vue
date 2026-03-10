<template>
  <section class="max-w-3xl mx-auto py-10 space-y-6">
    <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
    <p class="text-stone-600">{{ text.subtitle }}</p>

    <div class="bg-white border border-stone-200 rounded-xl p-6 space-y-4">
      <div>
        <h2 class="text-sm font-semibold text-stone-900">{{ text.supportTitle }}</h2>
        <p class="text-sm text-stone-700">{{ text.supportText }}</p>
      </div>
      <div>
        <h2 class="text-sm font-semibold text-stone-900">{{ text.gdprTitle }}</h2>
        <p class="text-sm text-stone-700">{{ text.gdprText }}</p>
      </div>
      <div>
        <h2 class="text-sm font-semibold text-stone-900">{{ text.responseTitle }}</h2>
        <p class="text-sm text-stone-700">{{ text.responseText }}</p>
      </div>
    </div>

    <p class="text-xs text-stone-500">
      {{ text.note }}
      <NuxtLink :to="localePath('/legal/gdpr')" class="underline">{{ text.gdprLink }}</NuxtLink>
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

const copy: Record<string, {
  title: string
  subtitle: string
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
    subtitle: 'Pentru suport tehnic, întrebări comerciale sau solicitări de protecția datelor, ne poți scrie oricând.',
    supportTitle: 'Suport general',
    supportText: 'Email: support@doisense.app',
    gdprTitle: 'Solicitări GDPR',
    gdprText: 'Email: privacy@doisense.app',
    responseTitle: 'Timp de răspuns',
    responseText: 'Încercăm să răspundem în 1-3 zile lucrătoare, în funcție de complexitatea cererii.',
    note: 'Pentru drepturile tale asupra datelor personale, vezi ',
    gdprLink: 'pagina GDPR.',
    seoTitle: 'Contact Doisense - Suport si solicitari GDPR',
    seoDescription: 'Contactează echipa Doisense pentru suport tehnic, întrebări comerciale sau solicitări privind datele personale.',
  },
  en: {
    title: 'Contact',
    subtitle: 'For technical support, commercial questions, or data protection requests, you can contact us anytime.',
    supportTitle: 'General support',
    supportText: 'Email: support@doisense.app',
    gdprTitle: 'GDPR requests',
    gdprText: 'Email: privacy@doisense.app',
    responseTitle: 'Response time',
    responseText: 'We aim to respond in 1-3 business days depending on request complexity.',
    note: 'For your personal data rights, see the ',
    gdprLink: 'GDPR page.',
    seoTitle: 'Contact Doisense - Support and GDPR requests',
    seoDescription: 'Contact the Doisense team for technical support, commercial questions, or personal data requests.',
  },
  de: {
    title: 'Kontakt',
    subtitle: 'Für technischen Support, geschäftliche Fragen oder Datenschutzanfragen kannst du uns jederzeit kontaktieren.',
    supportTitle: 'Allgemeiner Support',
    supportText: 'E-Mail: support@doisense.app',
    gdprTitle: 'DSGVO-Anfragen',
    gdprText: 'E-Mail: privacy@doisense.app',
    responseTitle: 'Antwortzeit',
    responseText: 'Wir antworten in der Regel innerhalb von 1-3 Werktagen, je nach Komplexität der Anfrage.',
    note: 'Für deine Datenschutzrechte siehe die ',
    gdprLink: 'DSGVO-Seite.',
    seoTitle: 'Doisense Kontakt - Support und DSGVO-Anfragen',
    seoDescription: 'Kontaktiere das Doisense-Team für technischen Support, geschäftliche Fragen oder Datenschutzanfragen.',
  },
  fr: {
    title: 'Contact',
    subtitle: 'Pour le support technique, les questions commerciales ou les demandes sur les donnees personnelles, vous pouvez nous contacter a tout moment.',
    supportTitle: 'Support general',
    supportText: 'Email: support@doisense.app',
    gdprTitle: 'Demandes GDPR',
    gdprText: 'Email: privacy@doisense.app',
    responseTitle: 'Delai de reponse',
    responseText: 'Nous essayons de repondre sous 1 a 3 jours ouvrables selon la complexite de la demande.',
    note: 'Pour vos droits sur les donnees personnelles, consultez la ',
    gdprLink: 'page GDPR.',
    seoTitle: 'Contact Doisense - Support et demandes GDPR',
    seoDescription: 'Contactez l\'equipe Doisense pour le support technique, les questions commerciales ou les demandes de donnees personnelles.',
  },
  it: {
    title: 'Contatto',
    subtitle: 'Per supporto tecnico, domande commerciali o richieste sulla protezione dei dati, puoi contattarci in qualsiasi momento.',
    supportTitle: 'Supporto generale',
    supportText: 'Email: support@doisense.app',
    gdprTitle: 'Richieste GDPR',
    gdprText: 'Email: privacy@doisense.app',
    responseTitle: 'Tempi di risposta',
    responseText: 'Cerchiamo di rispondere entro 1-3 giorni lavorativi, in base alla complessità della richiesta.',
    note: 'Per i tuoi diritti sui dati personali, consulta la ',
    gdprLink: 'pagina GDPR.',
    seoTitle: 'Contatto Doisense - Supporto e richieste GDPR',
    seoDescription: 'Contatta il team Doisense per supporto tecnico, domande commerciali o richieste sui dati personali.',
  },
  es: {
    title: 'Contacto',
    subtitle: 'Para soporte técnico, preguntas comerciales o solicitudes de protección de datos, puedes escribirnos en cualquier momento.',
    supportTitle: 'Soporte general',
    supportText: 'Email: support@doisense.app',
    gdprTitle: 'Solicitudes GDPR',
    gdprText: 'Email: privacy@doisense.app',
    responseTitle: 'Tiempo de respuesta',
    responseText: 'Intentamos responder en 1-3 días hábiles, según la complejidad de la solicitud.',
    note: 'Para tus derechos sobre datos personales, consulta la ',
    gdprLink: 'página GDPR.',
    seoTitle: 'Contacto Doisense - Soporte y solicitudes GDPR',
    seoDescription: 'Contacta al equipo de Doisense para soporte técnico, preguntas comerciales o solicitudes de datos personales.',
  },
  pl: {
    title: 'Kontakt',
    subtitle: 'W sprawie wsparcia technicznego, pytań handlowych lub wniosków dotyczących ochrony danych możesz skontaktować się z nami w dowolnym momencie.',
    supportTitle: 'Wsparcie ogólne',
    supportText: 'Email: support@doisense.app',
    gdprTitle: 'Wnioski GDPR',
    gdprText: 'Email: privacy@doisense.app',
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

const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
