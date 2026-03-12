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
const { cmsPage, hasCmsContent } = useLegalCmsPage('terms')

const termsCopy: Record<string, {
  title: string
  updated: string
  sections: Array<{ title: string; body?: string; items?: string[] }>
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    title: 'Termeni și condiții',
    updated: 'Ultima actualizare: 11 martie 2026',
    sections: [
      {
        title: '1. Introducere',
        body: 'Acest document stabilește termenii și condițiile de utilizare ale platformei [Numele Platformei], un serviciu digital de wellness bazat pe inteligență artificială.\nPrin utilizarea platformei, utilizatorul acceptă integral acești termeni.',
      },
      {
        title: '2. Descrierea serviciului',
        body: 'Platforma oferă:',
        items: [
          'suport emoțional general',
          'analiză a stărilor emoționale',
          'generare de întrebări pentru auto-reflecție',
          'rapoarte și planuri de wellness',
          'recomandări non-medicale',
        ],
      },
      {
        title: 'Platforma NU oferă',
        items: [
          'diagnostic medical',
          'tratament psihologic',
          'consiliere psihiatrică',
          'intervenții terapeutice',
          'recomandări medicale',
        ],
      },
      {
        title: 'Clarificare',
        body: 'Platforma este un instrument de auto-reflecție și dezvoltare personală.',
      },
      { title: '3. Eligibilitate', body: 'Utilizatorul trebuie să aibă minimum 18 ani.' },
      {
        title: '4. Contul utilizatorului',
        body: 'Utilizatorul este responsabil pentru:',
        items: [
          'confidențialitatea contului',
          'acuratețea datelor introduse',
          'activitatea desfășurată în cont',
        ],
      },
      {
        title: '5. Abonamente și plăți',
        items: [
          'Platforma oferă planuri BASIC, PREMIUM și VIP.',
          'Plățile sunt procesate prin Stripe.',
          'Abonamentele sunt recurente.',
          'Utilizatorul poate anula oricând.',
          'La anulare, accesul rămâne activ până la finalul perioadei plătite.',
          'Refund-urile sunt gestionate conform politicii de refund Stripe.',
        ],
      },
      {
        title: '6. Trial',
        items: [
          'Utilizatorul beneficiază de 7 zile gratuite.',
          'La finalul trialului, accesul se suspendă dacă nu se activează un abonament.',
        ],
      },
      {
        title: '7. Limitarea răspunderii',
        body: 'Platforma nu este responsabilă pentru:',
        items: [
          'deciziile utilizatorului',
          'interpretarea recomandărilor',
          'consecințele emoționale sau psihologice',
          'pierderi financiare',
          'indisponibilitatea temporară a serviciului',
        ],
      },
      {
        title: 'Platforma este oferită „ca atare”.',
      },
      {
        title: '8. Interdicții',
        body: 'Utilizatorul nu poate:',
        items: [
          'utiliza platforma în scopuri ilegale',
          'încerca acces neautorizat',
          'copia sau redistribui conținutul AI',
          'abuza verbal AI-ul sau echipa',
        ],
      },
      {
        title: '9. Suspendarea contului',
        body: 'Platforma poate suspenda contul în caz de:',
        items: ['abuz', 'fraudă', 'încălcarea termenilor'],
      },
      { title: '10. Modificări', body: 'Termenii pot fi actualizați. Utilizatorul va fi notificat.' },
      { title: '11. Legea aplicabilă', body: 'Acest contract este guvernat de legislația din România și UE.' },
    ],
    seoTitle: 'Termeni si conditii - Doisense',
    seoDescription: 'Citește termenii și condițiile de utilizare a platformei Doisense, inclusiv descrierea serviciului, plăți, limitarea răspunderii și legea aplicabilă.',
  },
  en: {
    title: 'Terms and Conditions',
    updated: 'Last updated: March 11, 2026',
    sections: [
      { title: '1. Introduction', body: 'This document sets out the terms and conditions for using Doisense, an AI-based digital wellness platform.\nBy using the platform, the user fully accepts these terms.' },
      { title: '2. Service description', body: 'The platform provides:\n• general emotional support\n• emotional state analysis\n• self-reflection question generation\n• wellness reports and plans\n• non-medical recommendations\n\nThe platform does NOT provide:\n• medical diagnosis\n• psychological treatment\n• psychiatric counselling\n• therapeutic interventions\n• medical recommendations\n\nThe platform is a self-reflection and personal development tool.' },
      { title: '3. Eligibility', body: 'Users must be at least 18 years of age.' },
      { title: '4. User account', body: 'The user is responsible for:\n• account confidentiality\n• accuracy of data entered\n• all activity conducted in the account' },
      { title: '5. Subscriptions and payments', body: 'The platform offers BASIC, PREMIUM and VIP plans. Payments are processed via Stripe. Subscriptions are recurring. Users may cancel at any time.\nUpon cancellation, access remains active until the end of the paid period. Refunds are handled in accordance with Stripe\'s refund policy.' },
      { title: '6. Trial', body: 'Users receive 7 free trial days. At the end of the trial, access is suspended unless a subscription is activated.' },
      { title: '7. Limitation of liability', body: 'The platform is not responsible for:\n• user decisions\n• interpretation of recommendations\n• emotional or psychological consequences\n• financial losses\n• temporary unavailability of the service\n\nThe platform is provided "as is".' },
      { title: '8. Prohibited uses', body: 'Users may not:\n• use the platform for illegal purposes\n• attempt unauthorised access\n• copy or redistribute AI-generated content\n• verbally abuse the AI or the team' },
      { title: '9. Account suspension', body: 'The platform may suspend an account in the event of:\n• abuse\n• fraud\n• breach of terms' },
      { title: '10. Changes', body: 'Terms may be updated at any time. Users will be notified.' },
      { title: '11. Applicable law', body: 'This agreement is governed by the laws of Romania and the European Union.' },
    ],
    seoTitle: 'Terms and Conditions - Doisense',
    seoDescription: 'Read Doisense terms and conditions, including service description, payments, liability limitations and applicable law.',
  },
  de: {
    title: 'Nutzungsbedingungen',
    updated: 'Letzte Aktualisierung: 11. März 2026',
    sections: [
      { title: '1. Einleitung', body: 'Dieses Dokument legt die Nutzungsbedingungen der Plattform Doisense fest, einem KI-gestützten digitalen Wellness-Dienst.\nDurch die Nutzung der Plattform akzeptiert der Nutzer diese Bedingungen vollständig.' },
      { title: '2. Leistungsbeschreibung', body: 'Die Plattform bietet:\n• allgemeine emotionale Unterstützung\n• Analyse emotionaler Zustände\n• Generierung von Selbstreflexionsfragen\n• Wellness-Berichte und -Pläne\n• nicht-medizinische Empfehlungen\n\nDie Plattform bietet KEINE:\n• medizinische Diagnose\n• psychologische Behandlung\n• psychiatrische Beratung\n• therapeutische Interventionen\n• medizinische Empfehlungen\n\nDie Plattform ist ein Werkzeug zur Selbstreflexion und persönlichen Entwicklung.' },
      { title: '3. Voraussetzungen', body: 'Nutzer müssen mindestens 18 Jahre alt sein.' },
      { title: '4. Benutzerkonto', body: 'Der Nutzer ist verantwortlich für:\n• die Vertraulichkeit des Kontos\n• die Richtigkeit der eingegebenen Daten\n• alle im Konto durchgeführten Aktivitäten' },
      { title: '5. Abonnements und Zahlungen', body: 'Die Plattform bietet BASIC-, PREMIUM- und VIP-Pläne. Zahlungen werden über Stripe abgewickelt. Abonnements verlängern sich automatisch. Nutzer können jederzeit kündigen.\nNach der Kündigung bleibt der Zugang bis zum Ende des bezahlten Zeitraums aktiv. Rückerstattungen werden gemäß der Rückerstattungsrichtlinie von Stripe abgewickelt.' },
      { title: '6. Testphase', body: 'Nutzer erhalten 7 kostenlose Testtage. Nach Ablauf der Testphase wird der Zugang gesperrt, sofern kein Abonnement aktiviert wird.' },
      { title: '7. Haftungsbeschränkung', body: 'Die Plattform haftet nicht für:\n• Entscheidungen des Nutzers\n• Interpretation von Empfehlungen\n• emotionale oder psychologische Folgen\n• finanzielle Verluste\n• vorübergehende Nichtverfügbarkeit des Dienstes\n\nDie Plattform wird „wie besehen" bereitgestellt.' },
      { title: '8. Verbotene Nutzung', body: 'Nutzer dürfen nicht:\n• die Plattform für illegale Zwecke nutzen\n• unbefugten Zugriff versuchen\n• KI-generierten Inhalt kopieren oder weiterverbreiten\n• die KI oder das Team verbal missbrauchen' },
      { title: '9. Kontosperrung', body: 'Die Plattform kann ein Konto sperren bei:\n• Missbrauch\n• Betrug\n• Verstoß gegen die Bedingungen' },
      { title: '10. Änderungen', body: 'Die Bedingungen können jederzeit aktualisiert werden. Nutzer werden benachrichtigt.' },
      { title: '11. Anwendbares Recht', body: 'Dieser Vertrag unterliegt dem Recht Rumäniens und der EU.' },
    ],
    seoTitle: 'Nutzungsbedingungen - Doisense',
    seoDescription: 'Lesen Sie die Nutzungsbedingungen von Doisense, einschließlich Leistungsbeschreibung, Zahlungen, Haftungsbeschränkungen und anwendbarem Recht.',
  },
  fr: {
    title: 'Conditions générales d\'utilisation',
    updated: 'Dernière mise à jour : 11 mars 2026',
    sections: [
      { title: '1. Introduction', body: 'Ce document établit les conditions générales d\'utilisation de la plateforme Doisense, un service numérique de bien-être basé sur l\'intelligence artificielle.\nEn utilisant la plateforme, l\'utilisateur accepte intégralement ces conditions.' },
      { title: '2. Description du service', body: 'La plateforme propose :\n• soutien émotionnel général\n• analyse des états émotionnels\n• génération de questions pour l\'auto-réflexion\n• rapports et plans de bien-être\n• recommandations non médicales\n\nLa plateforme ne propose PAS :\n• diagnostic médical\n• traitement psychologique\n• conseil psychiatrique\n• interventions thérapeutiques\n• recommandations médicales\n\nLa plateforme est un outil d\'auto-réflexion et de développement personnel.' },
      { title: '3. Éligibilité', body: 'L\'utilisateur doit avoir au minimum 18 ans.' },
      { title: '4. Compte utilisateur', body: 'L\'utilisateur est responsable de :\n• la confidentialité de son compte\n• l\'exactitude des données saisies\n• les activités réalisées dans le compte' },
      { title: '5. Abonnements et paiements', body: 'La plateforme propose des plans BASIC, PREMIUM et VIP. Les paiements sont traités via Stripe. Les abonnements sont récurrents. L\'utilisateur peut annuler à tout moment.\nAprès annulation, l\'accès reste actif jusqu\'à la fin de la période payée. Les remboursements sont gérés conformément à la politique de remboursement de Stripe.' },
      { title: '6. Période d\'essai', body: 'L\'utilisateur bénéficie de 7 jours gratuits. À la fin de l\'essai, l\'accès est suspendu si aucun abonnement n\'est activé.' },
      { title: '7. Limitation de responsabilité', body: 'La plateforme n\'est pas responsable de :\n• les décisions de l\'utilisateur\n• l\'interprétation des recommandations\n• les conséquences émotionnelles ou psychologiques\n• les pertes financières\n• l\'indisponibilité temporaire du service\n\nLa plateforme est fournie « telle quelle ».' },
      { title: '8. Interdictions', body: 'L\'utilisateur ne peut pas :\n• utiliser la plateforme à des fins illégales\n• tenter un accès non autorisé\n• copier ou redistribuer le contenu généré par l\'IA\n• abuser verbalement l\'IA ou l\'équipe' },
      { title: '9. Suspension du compte', body: 'La plateforme peut suspendre un compte en cas de :\n• abus\n• fraude\n• violation des conditions' },
      { title: '10. Modifications', body: 'Les conditions peuvent être mises à jour. L\'utilisateur sera notifié.' },
      { title: '11. Droit applicable', body: 'Ce contrat est régi par le droit roumain et européen.' },
    ],
    seoTitle: 'Conditions générales - Doisense',
    seoDescription: 'Lisez les conditions générales de Doisense, incluant la description du service, les paiements, les limitations de responsabilité et le droit applicable.',
  },
  it: {
    title: 'Termini e condizioni',
    updated: 'Ultimo aggiornamento: 11 marzo 2026',
    sections: [
      { title: '1. Introduzione', body: 'Questo documento stabilisce i termini e le condizioni d\'uso della piattaforma Doisense, un servizio digitale di benessere basato sull\'intelligenza artificiale.\nUtilizzando la piattaforma, l\'utente accetta integralmente questi termini.' },
      { title: '2. Descrizione del servizio', body: 'La piattaforma offre:\n• supporto emotivo generale\n• analisi degli stati emotivi\n• generazione di domande per l\'auto-riflessione\n• report e piani per il benessere\n• raccomandazioni non mediche\n\nLa piattaforma NON offre:\n• diagnosi medica\n• trattamento psicologico\n• consulenza psichiatrica\n• interventi terapeutici\n• raccomandazioni mediche\n\nLa piattaforma è uno strumento di auto-riflessione e sviluppo personale.' },
      { title: '3. Requisiti', body: 'L\'utente deve avere almeno 18 anni.' },
      { title: '4. Account utente', body: 'L\'utente è responsabile di:\n• la riservatezza dell\'account\n• l\'accuratezza dei dati inseriti\n• le attività svolte nell\'account' },
      { title: '5. Abbonamenti e pagamenti', body: 'La piattaforma offre piani BASIC, PREMIUM e VIP. I pagamenti sono elaborati tramite Stripe. Gli abbonamenti sono ricorrenti. L\'utente può disdire in qualsiasi momento.\nIn caso di disdetta, l\'accesso rimane attivo fino alla fine del periodo pagato. I rimborsi sono gestiti in conformità con la politica di rimborso di Stripe.' },
      { title: '6. Periodo di prova', body: 'L\'utente usufruisce di 7 giorni gratuiti. Al termine del periodo di prova, l\'accesso viene sospeso se non viene attivato un abbonamento.' },
      { title: '7. Limitazione di responsabilità', body: 'La piattaforma non è responsabile per:\n• le decisioni dell\'utente\n• l\'interpretazione delle raccomandazioni\n• le conseguenze emotive o psicologiche\n• perdite finanziarie\n• indisponibilità temporanea del servizio\n\nLa piattaforma è fornita \"così com\'è\".' },
      { title: '8. Divieti', body: 'L\'utente non può:\n• utilizzare la piattaforma per scopi illegali\n• tentare accessi non autorizzati\n• copiare o ridistribuire contenuti generati dall\'IA\n• abusare verbalmente dell\'IA o del team' },
      { title: '9. Sospensione dell\'account', body: 'La piattaforma può sospendere l\'account in caso di:\n• abuso\n• frode\n• violazione dei termini' },
      { title: '10. Modifiche', body: 'I termini possono essere aggiornati. L\'utente verrà notificato.' },
      { title: '11. Legge applicabile', body: 'Questo contratto è regolato dalla legge rumena e dell\'UE.' },
    ],
    seoTitle: 'Termini e condizioni - Doisense',
    seoDescription: 'Leggi i termini e condizioni di Doisense, inclusa la descrizione del servizio, pagamenti, limitazioni di responsabilità e legge applicabile.',
  },
  es: {
    title: 'Términos y condiciones',
    updated: 'Última actualización: 11 de marzo de 2026',
    sections: [
      { title: '1. Introducción', body: 'Este documento establece los términos y condiciones de uso de la plataforma Doisense, un servicio digital de bienestar basado en inteligencia artificial.\nAl utilizar la plataforma, el usuario acepta íntegramente estos términos.' },
      { title: '2. Descripción del servicio', body: 'La plataforma ofrece:\n• apoyo emocional general\n• análisis de estados emocionales\n• generación de preguntas para la auto-reflexión\n• informes y planes de bienestar\n• recomendaciones no médicas\n\nLa plataforma NO ofrece:\n• diagnóstico médico\n• tratamiento psicológico\n• asesoramiento psiquiátrico\n• intervenciones terapéuticas\n• recomendaciones médicas\n\nLa plataforma es una herramienta de auto-reflexión y desarrollo personal.' },
      { title: '3. Requisitos', body: 'El usuario debe tener al menos 18 años.' },
      { title: '4. Cuenta de usuario', body: 'El usuario es responsable de:\n• la confidencialidad de la cuenta\n• la exactitud de los datos introducidos\n• las actividades realizadas en la cuenta' },
      { title: '5. Suscripciones y pagos', body: 'La plataforma ofrece planes BASIC, PREMIUM y VIP. Los pagos se procesan a través de Stripe. Las suscripciones son recurrentes. El usuario puede cancelar en cualquier momento.\nTras la cancelación, el acceso permanece activo hasta el final del período pagado. Los reembolsos se gestionan según la política de reembolso de Stripe.' },
      { title: '6. Período de prueba', body: 'El usuario dispone de 7 días gratuitos. Al finalizar el período de prueba, el acceso se suspende si no se activa una suscripción.' },
      { title: '7. Limitación de responsabilidad', body: 'La plataforma no es responsable de:\n• las decisiones del usuario\n• la interpretación de las recomendaciones\n• las consecuencias emocionales o psicológicas\n• pérdidas financieras\n• la indisponibilidad temporal del servicio\n\nLa plataforma se proporciona \"tal cual\".' },
      { title: '8. Prohibiciones', body: 'El usuario no puede:\n• utilizar la plataforma con fines ilegales\n• intentar el acceso no autorizado\n• copiar o redistribuir contenido generado por IA\n• abusar verbalmente de la IA o del equipo' },
      { title: '9. Suspensión de cuenta', body: 'La plataforma puede suspender la cuenta en caso de:\n• abuso\n• fraude\n• incumplimiento de los términos' },
      { title: '10. Modificaciones', body: 'Los términos pueden ser actualizados. El usuario será notificado.' },
      { title: '11. Ley aplicable', body: 'Este contrato se rige por la legislación de Rumanía y la UE.' },
    ],
    seoTitle: 'Términos y condiciones - Doisense',
    seoDescription: 'Lee los términos y condiciones de Doisense, incluyendo la descripción del servicio, pagos, limitaciones de responsabilidad y ley aplicable.',
  },
  pl: {
    title: 'Regulamin',
    updated: 'Ostatnia aktualizacja: 11 marca 2026',
    sections: [
      { title: '1. Wprowadzenie', body: 'Niniejszy dokument określa warunki korzystania z platformy Doisense, cyfrowej usługi wellness opartej na sztucznej inteligencji.\nKorzystając z platformy, użytkownik w pełni akceptuje niniejsze warunki.' },
      { title: '2. Opis usługi', body: 'Platforma oferuje:\n• ogólne wsparcie emocjonalne\n• analizę stanów emocjonalnych\n• generowanie pytań do autorefleksji\n• raporty i plany wellness\n• zalecenia niemedyczne\n\nPlatforma NIE oferuje:\n• diagnozy medycznej\n• leczenia psychologicznego\n• doradztwa psychiatrycznego\n• interwencji terapeutycznych\n• zaleceń medycznych\n\nPlatforma jest narzędziem do autorefleksji i rozwoju osobistego.' },
      { title: '3. Wymagania', body: 'Użytkownik musi mieć co najmniej 18 lat.' },
      { title: '4. Konto użytkownika', body: 'Użytkownik jest odpowiedzialny za:\n• poufność konta\n• dokładność wprowadzonych danych\n• działania prowadzone na koncie' },
      { title: '5. Subskrypcje i płatności', body: 'Platforma oferuje plany BASIC, PREMIUM i VIP. Płatności są przetwarzane przez Stripe. Subskrypcje odnawiane są automatycznie. Użytkownik może anulować w dowolnym momencie.\nPo anulowaniu dostęp pozostaje aktywny do końca opłaconego okresu. Zwroty są obsługiwane zgodnie z polityką zwrotów Stripe.' },
      { title: '6. Okres próbny', body: 'Użytkownik otrzymuje 7 bezpłatnych dni próbnych. Po zakończeniu okresu próbnego dostęp zostaje zawieszony, jeśli nie zostanie aktywowana subskrypcja.' },
      { title: '7. Ograniczenie odpowiedzialności', body: 'Platforma nie ponosi odpowiedzialności za:\n• decyzje użytkownika\n• interpretację zaleceń\n• konsekwencje emocjonalne lub psychologiczne\n• straty finansowe\n• tymczasową niedostępność usługi\n\nPlatforma jest dostarczana \"w stanie, w jakim się znajduje\".' },
      { title: '8. Zakazy', body: 'Użytkownik nie może:\n• korzystać z platformy w celach niezgodnych z prawem\n• próbować uzyskać nieautoryzowanego dostępu\n• kopiować ani redystrybuować treści generowanych przez AI\n• werbalnie nadużywać AI ani zespołu' },
      { title: '9. Zawieszenie konta', body: 'Platforma może zawiesić konto w przypadku:\n• nadużycia\n• oszustwa\n• naruszenia warunków' },
      { title: '10. Zmiany', body: 'Warunki mogą być aktualizowane. Użytkownik zostanie powiadomiony.' },
      { title: '11. Prawo właściwe', body: 'Niniejsza umowa podlega prawu Rumunii i UE.' },
    ],
    seoTitle: 'Regulamin - Doisense',
    seoDescription: 'Przeczytaj regulamin Doisense, w tym opis usługi, płatności, ograniczenia odpowiedzialności i prawo właściwe.',
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
