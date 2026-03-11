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
        <p v-if="section.body" class="text-stone-700 text-sm leading-6 whitespace-pre-line">{{ section.body }}</p>
        <ul v-if="section.items?.length" class="mt-3 space-y-2 pl-5 text-sm leading-6 text-stone-700 list-disc">
          <li v-for="item in section.items" :key="item">{{ item }}</li>
        </ul>
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
const { cmsPage, hasCmsContent } = useLegalCmsPage('privacy')

const privacyCopy: Record<string, {
  title: string
  updated: string
  sections: Array<{ title: string; body?: string; items?: string[] }>
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    title: 'Politica de confidențialitate',
    updated: 'Ultima actualizare: 11 martie 2026',
    sections: [
      {
        title: '1. Ce date colectăm',
        body: 'Colectăm doar datele necesare pentru funcționarea contului și a serviciilor contractate:',
        items: [
          'date de cont: email, limbă, prenume, nume, telefon și regiune fiscală, dacă le completezi',
          'conținut introdus de tine în jurnal, chat și check-in-uri de wellbeing',
          'date de profil folosite pentru personalizare: ton preferat, sensibilități, stil de comunicare și cuvinte-cheie',
          'date de abonament și facturare procesate prin Stripe',
          'metadate tehnice minime pentru autentificare, securitate și funcționarea sesiunii',
        ],
      },
      {
        title: '2. Ce nu colectăm intenționat',
        items: [
          'nu solicităm CNP sau date oficiale de identitate',
          'nu vindem datele tale personale către terți',
          'nu folosim conținutul tău pentru publicitate personalizată externă',
        ],
      },
      {
        title: '3. Scopul prelucrării',
        items: [
          'crearea și administrarea contului tău',
          'livrarea funcțiilor de jurnal, chat AI, programe și plăți',
          'personalizarea răspunsurilor și a experienței în produs',
          'securitate, prevenirea fraudei și suport tehnic',
        ],
      },
      {
        title: '4. Temeiul legal',
        items: [
          'executarea contractului pentru funcțiile contului și abonamentelor',
          'consimțământul tău pentru acceptarea documentelor legale și preferințele opționale',
          'interes legitim pentru securitate, operare și apărarea drepturilor noastre',
        ],
      },
      {
        title: '5. Stocare și retenție',
        items: [
          'datele sunt stocate în infrastructură securizată și accesate doar după necesitate',
          'datele de cont sunt păstrate cât timp contul rămâne activ sau cât timp există obligații legale minime',
          'la ștergerea contului, datele personale de cont sunt eliminate sau anonimizate; conversațiile sunt păstrate doar în formă anonimizată',
        ],
      },
      {
        title: '6. Drepturile tale',
        items: [
          'dreptul la acces',
          'dreptul la rectificare',
          'dreptul la ștergere',
          'dreptul la portabilitate',
          'dreptul la restricționare',
          'dreptul la opoziție',
        ],
      },
      {
        title: '7. Export și ștergere',
        body: 'Poți exporta direct datele personale din pagina Profil. Poți șterge contul din aceeași zonă; jurnalul și check-in-urile se șterg, iar conversațiile se anonimizează și rămân fără legătură directă cu identitatea ta.',
      },
      {
        title: '8. Furnizori și transferuri',
        body: 'Putem folosi furnizori tehnici pentru hosting, procesare plăți și modele AI. Datele pot fi procesate în UE sau în alte jurisdicții numai în condiții contractuale și garanții adecvate.',
      },
      {
        title: '9. Contact pentru confidențialitate',
        body: 'Pentru cereri legate de confidențialitate, rectificare sau opoziție: privacy@doisense.app',
      },
    ],
    seoTitle: 'Politica de confidentialitate - Doisense',
    seoDescription: 'Vezi cum prelucrăm datele personale în Doisense: ce colectăm, de ce, cât stocăm și cu cine partajăm.',
  },
  en: {
    title: 'Privacy Policy',
    updated: 'Last updated: March 11, 2026',
    sections: [
      { title: '1. Data we collect', body: 'We collect account data you provide, profile preferences used for personalization, journal and chat content, wellbeing check-ins, subscription records, and the minimum technical metadata needed for authentication and security.' },
      { title: '2. Why we process data', body: 'We process data to operate your account, deliver paid features, personalize AI responses, secure the service, and support billing and fraud prevention.' },
      { title: '3. Legal basis', body: 'Contract performance, legitimate interest for security and operations, and consent where required for legal acceptance or optional processing.' },
      { title: '4. Storage and retention', body: 'We retain account data while your account is active and longer only when necessary for legal obligations or minimum security auditing. When you delete your account, personal account data is removed or anonymized, while conversations are retained only in anonymized form.' },
      { title: '5. Export and deletion', body: 'You can export your personal data directly from your profile page in JSON format. You can also delete your account from the profile page; journal entries and wellbeing check-ins are deleted, and conversations are detached and anonymized.' },
      { title: '6. Sharing', body: 'We do not sell personal data. Technical providers such as hosting, payment, and AI vendors may process data only to deliver the service under contractual safeguards.' },
    ],
    seoTitle: 'Privacy Policy - Doisense',
    seoDescription: 'Learn how Doisense processes personal data: what we collect, why, retention periods, and controlled sharing.',
  },
  de: {
    title: 'Datenschutzerklärung',
    updated: 'Letzte Aktualisierung: 08. März 2026',
    sections: [
      { title: '1. Welche Daten wir erheben', body: 'Kontodaten (E-Mail), Inhalte aus Tagebuch/Chat sowie technische Metadaten für Sicherheit und Betrieb.' },
      { title: '2. Zweck der Verarbeitung', body: 'Wir verarbeiten Daten für Authentifizierung, Bereitstellung von Funktionen, Personalisierung der KI-Antworten und Qualitätsverbesserung.' },
      { title: '3. Rechtsgrundlage', body: 'Vertragserfüllung, berechtigtes Interesse für Sicherheit/Betrieb und Einwilligung, wo erforderlich.' },
      { title: '4. Speicherung und Aufbewahrung', body: 'Daten werden gespeichert, solange dein Konto aktiv ist oder gesetzliche Pflichten und Sicherheitsprotokolle dies erfordern.' },
      { title: '5. Weitergabe', body: 'Wir verkaufen keine personenbezogenen Daten. Technische Dienstleister (Hosting, Zahlungen, KI) verarbeiten Daten nur zur Bereitstellung des Dienstes.' },
    ],
    seoTitle: 'Datenschutz - Doisense',
    seoDescription: 'Erfahre, wie Doisense personenbezogene Daten verarbeitet: Erhebung, Zweck, Speicherdauer und kontrollierte Weitergabe.',
  },
  fr: {
    title: 'Politique de confidentialite',
    updated: 'Derniere mise a jour: 08 mars 2026',
    sections: [
      { title: '1. Donnees que nous collectons', body: 'Donnees de compte (email), contenu de journal/chat fourni par vous et metadonnees techniques necessaires a la securite et au fonctionnement.' },
      { title: '2. Finalite du traitement', body: 'Nous traitons les donnees pour l\'authentification, la fourniture des fonctionnalites, la personnalisation des reponses IA et l\'amelioration du service.' },
      { title: '3. Base legale', body: 'Execution du contrat, interet legitime pour la securite/l\'exploitation et consentement lorsque requis.' },
      { title: '4. Stockage et retention', body: 'Les donnees sont conservees tant que le compte est actif ou selon les obligations legales et l\'audit minimum de securite.' },
      { title: '5. Partage', body: 'Nous ne vendons pas de donnees personnelles. Des prestataires techniques (hebergement, paiements, IA) peuvent traiter les donnees uniquement pour fournir le service.' },
    ],
    seoTitle: 'Politique de confidentialite - Doisense',
    seoDescription: 'Consultez comment Doisense traite les donnees personnelles: collecte, finalite, retention et partage controle.',
  },
  it: {
    title: 'Informativa sulla privacy',
    updated: 'Ultimo aggiornamento: 08 marzo 2026',
    sections: [
      { title: '1. Dati raccolti', body: 'Dati account (email), contenuti di diario/chat e metadati tecnici necessari a sicurezza e funzionamento.' },
      { title: '2. Finalità del trattamento', body: 'Usiamo i dati per autenticazione, erogazione funzionalità, personalizzazione AI e miglioramento del servizio.' },
      { title: '3. Base giuridica', body: 'Esecuzione del contratto, legittimo interesse per sicurezza/operatività e consenso ove richiesto.' },
      { title: '4. Conservazione', body: 'I dati sono conservati finché l’account è attivo o per obblighi legali e audit minimi di sicurezza.' },
      { title: '5. Condivisione', body: 'Non vendiamo dati personali. Fornitori tecnici (hosting, pagamenti, AI) trattano dati solo per erogare il servizio.' },
    ],
    seoTitle: 'Privacy - Doisense',
    seoDescription: 'Scopri come Doisense tratta i dati personali: raccolta, finalità, conservazione e condivisione controllata.',
  },
  es: {
    title: 'Política de privacidad',
    updated: 'Última actualización: 08 de marzo de 2026',
    sections: [
      { title: '1. Datos que recopilamos', body: 'Datos de cuenta (correo), contenido de diario/chat y metadatos técnicos necesarios para seguridad y operación.' },
      { title: '2. Finalidad del tratamiento', body: 'Procesamos datos para autenticación, entrega de funciones, personalización de respuestas AI y mejora del servicio.' },
      { title: '3. Base legal', body: 'Ejecución del contrato, interés legítimo para seguridad/operación y consentimiento cuando corresponda.' },
      { title: '4. Almacenamiento y retención', body: 'Los datos se conservan mientras la cuenta esté activa o sea necesario por obligaciones legales y auditoría mínima de seguridad.' },
      { title: '5. Compartición', body: 'No vendemos datos personales. Proveedores técnicos (hosting, pagos, AI) procesan datos solo para prestar el servicio.' },
    ],
    seoTitle: 'Política de privacidad - Doisense',
    seoDescription: 'Consulta cómo Doisense procesa datos personales: qué recopilamos, por qué, cuánto tiempo y con quién se comparte.',
  },
  pl: {
    title: 'Polityka prywatności',
    updated: 'Ostatnia aktualizacja: 08 marca 2026',
    sections: [
      { title: '1. Jakie dane zbieramy', body: 'Dane konta (email), treści dziennika/czatu oraz metadane techniczne wymagane dla bezpieczeństwa i działania aplikacji.' },
      { title: '2. Cel przetwarzania', body: 'Przetwarzamy dane do uwierzytelniania, dostarczania funkcji, personalizacji odpowiedzi AI i poprawy jakości usługi.' },
      { title: '3. Podstawa prawna', body: 'Wykonanie umowy, uzasadniony interes dla bezpieczeństwa/operacji oraz zgoda tam, gdzie wymagana.' },
      { title: '4. Przechowywanie i retencja', body: 'Dane przechowujemy, gdy konto jest aktywne lub gdy wymagają tego obowiązki prawne i minimalny audyt bezpieczeństwa.' },
      { title: '5. Udostępnianie', body: 'Nie sprzedajemy danych osobowych. Dostawcy techniczni (hosting, płatności, AI) przetwarzają dane wyłącznie w celu świadczenia usługi.' },
    ],
    seoTitle: 'Polityka prywatności - Doisense',
    seoDescription: 'Sprawdź, jak Doisense przetwarza dane osobowe: co zbieramy, dlaczego, jak długo i z kim udostępniamy.',
  },
}

const text = computed(() => {
  return privacyCopy[localeCode.value] || privacyCopy.en
})

const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
