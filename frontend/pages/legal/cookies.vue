<template>
  <article class="max-w-4xl mx-auto py-10 space-y-4">
    <template v-if="hasCmsContent && cmsPage">
      <h1 class="text-4xl font-bold text-stone-900">{{ cmsPage.title }}</h1>
      <section class="bg-white border border-stone-200 rounded-xl p-5">
        <p class="text-stone-700 text-sm leading-7 whitespace-pre-line">{{ cmsPage.content }}</p>
      </section>
    </template>

    <template v-else>
      <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
      <p class="text-sm text-stone-500">{{ text.updated }}</p>

      <section
        v-for="section in text.sections"
        :key="section.heading"
        class="bg-white border border-stone-200 rounded-xl p-5 space-y-3"
      >
        <h2 class="text-base font-semibold text-stone-900">{{ section.heading }}</h2>
        <p v-for="(para, i) in section.paragraphs" :key="i" class="text-stone-700 text-sm leading-6 whitespace-pre-line">{{ para }}</p>
        <ul v-if="section.items?.length" class="space-y-1.5 text-sm text-stone-700 pl-1">
          <li v-for="item in section.items" :key="item">• {{ item }}</li>
        </ul>
        <template v-if="section.subsections?.length">
          <div v-for="sub in section.subsections" :key="sub.heading" class="pt-1 space-y-1">
            <h3 class="text-sm font-semibold text-stone-800">{{ sub.heading }}</h3>
            <p class="text-stone-700 text-sm leading-6">{{ sub.content }}</p>
          </div>
        </template>
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
const { cmsPage, hasCmsContent } = useLegalCmsPage('cookies')

type Section = {
  heading: string
  paragraphs?: string[]
  items?: string[]
  subsections?: { heading: string; content: string }[]
}

const cookiesCopy: Record<string, {
  title: string
  updated: string
  sections: Section[]
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    title: 'Politică cookie-uri (UE)',
    updated: 'Această Politică cookie-uri a fost actualizată ultima dată pe 11 martie 2026 și se aplică cetățenilor și rezidenților permanenți din Spațiul Economic European și Elveția.',
    sections: [
      { heading: '1. Introducere', paragraphs: ['Site-ul nostru, https://doisense.eu (denumit în continuare „site-ul"), folosește cookie-uri și alte tehnologii similare (pentru comoditate, toate tehnologiile sunt numite în continuare „cookie-uri"). Cookie-urile sunt plasate și de terții cu care colaborăm. În documentul de mai jos te informăm despre modul cum folosim cookie-uri pe site-ul nostru.'] },
      { heading: '2. Ce sunt cookie-urile?', paragraphs: ['Un cookie este un fișier simplu, de mici dimensiuni, care este trimis împreună cu paginile acestui site web și stocat de navigatorul tău pe hard diskul computerului sau al altui dispozitiv. Informațiile stocate acolo pot fi trimise înapoi către serverele noastre sau serverele terților relevanți, în timpul unei vizite ulterioare.'] },
      { heading: '3. Ce sunt scripturile?', paragraphs: ['Un script este un fragment de cod (de program), utilizat pentru ca site-ul nostru să funcționeze corect și interactiv. Acest cod este executat pe serverul nostru sau pe dispozitivul tău.'] },
      { heading: '4. Ce este un web beacon?', paragraphs: ['Un „web beacon" (sau un „pixel tag") este un mic fragment invizibil de text sau o imagine plasată pe un site web pentru a monitoriza traficul. Web beacon-urile pot stoca diverse date despre tine în scopul monitorizării.'] },
      {
        heading: '5. Cookie-uri',
        subsections: [
          { heading: '5.1 Cookie-uri tehnice sau funcționale', content: 'Unele cookie-uri se asigură că anumite părți ale site-ului funcționează corect și că preferințele tale de utilizator rămân cunoscute. Prin plasarea cookie-urilor funcționale, nu trebuie să introduci în mod repetat aceleași informații la fiecare vizită. Putem plasa aceste cookie-uri fără consimțământul tău.' },
          { heading: '5.2 Cookie-uri statistice', content: 'Folosim cookie-uri statistice pentru a optimiza experiența de utilizare a platformei. Cu aceste cookie-uri obținem informații despre utilizarea site-ului nostru. Îți cerem permisiunea de a plasa cookie-uri statistice.' },
          { heading: '5.3 Cookie-uri pentru marketing/urmărire', content: 'Cookie-urile de marketing sunt utilizate pentru a înțelege comportamentul de navigare și pentru a îmbunătăți serviciul. Doisense utilizează cookie-uri de marketing limitate, fără a vinde datele tale terților.' },
          { heading: '5.4 Servicii terțe', content: 'Doisense integrează servicii terțe precum Google OAuth pentru autentificare și Stripe pentru plăți. Dacă în viitor activăm analytics opțional, acesta va fi condiționat de consimțământul din bannerul GDPR.' },
        ],
      },
      {
        heading: '6. Cookie-uri plasate',
        subsections: [
          { heading: 'Google Analytics — Statistici', content: 'Nu este activ implicit în versiunea curentă. Dacă va fi activat ulterior, va folosi doar consimțământul explicit pentru categoria Statistics.' },
          { heading: 'Google OAuth — Funcțional', content: 'Permite autentificarea cu contul Google, stocând token-uri de sesiune necesare menținerii stării de autentificare.' },
          { heading: 'Stripe — Funcțional', content: 'Procesarea securizată a plăților. Stripe plasează cookie-uri pentru prevenirea fraudei și gestionarea sesiunilor de plată.' },
          { heading: 'JWT Auth (intern) — Funcțional', content: 'Token-uri de autentificare folosite intern pentru menținerea sesiunii utilizatorului pe platformă. Șterse la expirarea sesiunii.' },
        ],
      },
      { heading: '7. Consimțământ', paragraphs: ['Când vizitezi pentru prima dată site-ul nostru, îți vom arăta o fereastră pop-up cu o explicație despre cookie-uri. Apăsând pe „Salvează preferințele", îți exprimi consimțământul pentru utilizarea categoriilor de cookie-uri selectate, conform acestei politici.', 'Poți bloca folosirea cookie-urilor din navigatorul pe care îl folosești, dar te rugăm să ții cont că anumite funcții ale platformei (autentificare, menținerea sesiunii) pot să nu funcționeze corespunzător.'] },
      { heading: '8. Activarea/dezactivarea și ștergerea cookie-urilor', paragraphs: ['Poți utiliza navigatorul de internet pentru a șterge automat sau manual cookie-urile. De asemenea, poți specifica că anumite cookie-uri nu pot fi plasate sau poți configura browserul să îți trimită o notificare la fiecare plasare a unui cookie.', 'Te rog să reții că site-ul nostru s-ar putea să nu funcționeze corect dacă sunt dezactivate toate cookie-urile. Dacă ștergi cookie-urile, ele vor fi plasate din nou după ce vizitezi site-ul și îți exprimi din nou consimțământul.'] },
      { heading: '9. Drepturile tale asupra datelor cu caracter personal', paragraphs: ['Conform GDPR, ai următoarele drepturi privind datele cu caracter personal:'], items: ['Dreptul la informare: ai dreptul să știi de ce sunt necesare datele tale, ce se va face cu ele și cât timp vor fi păstrate.', 'Dreptul de acces: ai dreptul de a-ți accesa datele cu caracter personal colectate.', 'Dreptul la rectificare: ai dreptul de a completa, corecta, șterge sau bloca datele tale cu caracter personal oricând.', 'Dreptul la ștergere: dacă ne-ai dat consimțământul, îl poți revoca și cere ștergerea datelor tale cu caracter personal.', 'Dreptul la portabilitate: ai dreptul să ceri toate datele tale și să le transferi la un alt operator.', 'Dreptul de a obiecta: te poți opune prelucrării datelor tale. Respectăm acest lucru, cu excepția cazului în care există motive justificate pentru prelucrare.', 'Pentru exercitarea acestor drepturi sau pentru reclamații, poți contacta și Autoritatea Națională de Supraveghere a Prelucrării Datelor cu Caracter Personal (ANSPDCP).'] },
      { heading: '10. Date de contact', paragraphs: ['Pentru întrebări și/sau comentarii în legătură cu Politica noastră privind cookie-urile, te rugăm să ne contactezi:', 'Doisense\nEmail: privacy@doisense.eu\nSite web: https://doisense.eu'] },
    ],
    seoTitle: 'Politica de cookie-uri - Doisense',
    seoDescription: 'Află ce tipuri de cookie-uri folosește Doisense și cum poți controla setările din browser.',
  },
  en: {
    title: 'Cookie Policy (EU)',
    updated: 'This Cookie Policy was last updated on March 11, 2026, and applies to citizens and permanent residents of the European Economic Area and Switzerland.',
    sections: [
      { heading: '1. Introduction', paragraphs: ['Our website, https://doisense.eu (hereinafter "the website"), uses cookies and other similar technologies (for convenience, all technologies are referred to hereinafter as "cookies"). Cookies are also placed by third parties with whom we work. In the document below we inform you about the use of cookies on our website.'] },
      { heading: '2. What are cookies?', paragraphs: ['A cookie is a small simple file that is sent along with pages of this website and stored by your browser on the hard drive of your computer or another device. The information stored therein may be returned to our servers or to the servers of the relevant third parties during a subsequent visit.'] },
      { heading: '3. What are scripts?', paragraphs: ['A script is a piece of program code that is used to make our website function properly and interactively. This code is executed on our server or on your device.'] },
      { heading: '4. What is a web beacon?', paragraphs: ['A web beacon (or a pixel tag) is a small, invisible piece of text or image on a website, used to monitor traffic on a website. In order to do this, various data about you is stored using web beacons.'] },
      {
        heading: '5. Cookies',
        subsections: [
          { heading: '5.1 Technical or functional cookies', content: 'Some cookies ensure that certain parts of the website work properly and that your user preferences remain known. By placing functional cookies, we make it easier for you to visit our website. You do not need to repeatedly enter the same information. We can place these cookies without your consent.' },
          { heading: '5.2 Statistics cookies', content: 'We use statistics cookies to optimize the website experience for our users. With these statistics cookies we get insights about the usage of our website. We ask your permission to place statistics cookies.' },
          { heading: '5.3 Marketing/Tracking cookies', content: 'Marketing/tracking cookies are used to create user profiles and understand browsing behaviour to improve the service. Doisense uses limited marketing cookies, without selling your data to third parties.' },
          { heading: '5.4 Third-party services', content: 'Doisense integrates third-party services such as Google OAuth for authentication and Stripe for payments. If optional analytics is enabled in the future, it will remain gated behind consent from the GDPR banner.' },
        ],
      },
      {
        heading: '6. Placed cookies',
        subsections: [
          { heading: 'Google Analytics — Statistics', content: 'Not active by default in the current version. If enabled later, it will only run after explicit consent for the Statistics category.' },
          { heading: 'Google OAuth — Functional', content: 'Enables sign-in with Google, storing session tokens needed to maintain authentication state.' },
          { heading: 'Stripe — Functional', content: 'Secure payment processing. Stripe places cookies to prevent fraud and manage payment sessions.' },
          { heading: 'JWT Auth (internal) — Functional', content: 'Authentication tokens used internally to maintain the user session on the platform. Removed after session expiry.' },
        ],
      },
      { heading: '7. Consent', paragraphs: ['When you visit our website for the first time, we will show you a pop-up with an explanation about cookies. As soon as you click on "Save preferences", you consent to us using the categories of cookies you have selected in accordance with this Cookie Policy.', 'You can disable the use of cookies via your browser, but please note that our website may no longer work properly if you do so.'] },
      { heading: '8. Enabling/disabling and deleting cookies', paragraphs: ['You can use your internet browser to automatically or manually delete cookies. You can also specify that certain cookies may not be placed. Another option is to change the settings of your internet browser so that you receive a message each time a cookie is placed. For more information about these options, please refer to the instructions in the Help section of your browser.', 'Please note that our website may not work properly if all cookies are disabled. If you delete cookies in your browser, they will be placed again after your consent when you visit our website again.'] },
      { heading: '9. Your rights with respect to personal data', paragraphs: ['Under GDPR, you have the following rights regarding personal data:'], items: ['You have the right to know why your personal data is needed, what will happen to it, and how long it will be retained.', 'Right of access: you have the right to access your personal data that we have collected.', 'Right to rectification: you have the right to supplement, correct, delete or block your personal data at any time.', 'If you give us your consent to process your data, you have the right to revoke that consent and to have your personal data deleted.', 'Right to data portability: you have the right to request all your personal data from the controller and transfer it in its entirety to another controller.', 'Right to object: you may object against the processing of your personal data. We comply with this, unless there are justified grounds for processing.', 'To exercise these rights or to file a complaint, you may also contact your national data protection authority.'] },
      { heading: '10. Contact details', paragraphs: ['If you have any questions and/or comments about our Cookie Policy, please contact us:', 'Doisense\nEmail: privacy@doisense.eu\nWebsite: https://doisense.eu'] },
    ],
    seoTitle: 'Cookie Policy - Doisense',
    seoDescription: 'Find out what cookie types Doisense uses and how you can control browser settings.',
  },
  de: {
    title: 'Cookie-Richtlinie (EU)',
    updated: 'Diese Cookie-Richtlinie wurde zuletzt am 11. März 2026 aktualisiert und gilt für Bürger und Dauereinwohner des Europäischen Wirtschaftsraums und der Schweiz.',
    sections: [
      { heading: '1. Einleitung', paragraphs: ['Unsere Website, https://doisense.eu (nachfolgend „die Website"), verwendet Cookies und ähnliche Technologien (alle Technologien werden nachfolgend als „Cookies" bezeichnet). Cookies werden auch von Dritten gesetzt, mit denen wir zusammenarbeiten. Im folgenden Dokument informieren wir Sie darüber, wie wir Cookies auf unserer Website verwenden.'] },
      { heading: '2. Was sind Cookies?', paragraphs: ['Ein Cookie ist eine einfache kleine Datei, die zusammen mit den Seiten dieser Website versendet und vom Browser auf der Festplatte Ihres Computers oder eines anderen Geräts gespeichert wird. Die darin gespeicherten Informationen können bei einem späteren Besuch an unsere Server oder an die Server relevanter Dritter zurückgesendet werden.'] },
      { heading: '3. Was sind Skripte?', paragraphs: ['Ein Skript ist ein Stück Programmcode, das verwendet wird, damit unsere Website korrekt und interaktiv funktioniert. Dieser Code wird auf unserem Server oder auf Ihrem Gerät ausgeführt.'] },
      { heading: '4. Was ist ein Web-Beacon?', paragraphs: ['Ein Web-Beacon (oder ein Pixel-Tag) ist ein kleines, unsichtbares Stück Text oder Bild auf einer Website, das verwendet wird, um den Datenverkehr zu überwachen. Dabei werden mithilfe von Web-Beacons verschiedene Daten über Sie gespeichert.'] },
      {
        heading: '5. Cookies',
        subsections: [
          { heading: '5.1 Technische oder funktionale Cookies', content: 'Einige Cookies stellen sicher, dass bestimmte Teile der Website ordnungsgemäß funktionieren und Ihre Benutzerpräferenzen bekannt bleiben. Durch das Setzen funktionaler Cookies erleichtern wir Ihnen den Besuch unserer Website. Diese Cookies können wir ohne Ihre Einwilligung setzen.' },
          { heading: '5.2 Statistik-Cookies', content: 'Wir verwenden Statistik-Cookies, um die Website-Erfahrung für unsere Benutzer zu optimieren. Mit diesen Cookies erhalten wir Einblicke in die Nutzung unserer Website. Wir bitten Sie um Erlaubnis, Statistik-Cookies zu setzen.' },
          { heading: '5.3 Marketing-/Tracking-Cookies', content: 'Marketing-Cookies werden verwendet, um das Nutzungsverhalten zu verstehen und den Dienst zu verbessern. Doisense verwendet begrenzte Marketing-Cookies, ohne Ihre Daten an Dritte zu verkaufen.' },
          { heading: '5.4 Drittanbieter-Dienste', content: 'Doisense integriert Drittanbieter-Dienste — Google (OAuth-Authentifizierung und Analytics) und Stripe (Zahlungsabwicklung) — die eigene Cookies setzen können. Bitte lesen Sie die Datenschutzrichtlinien dieser Anbieter für vollständige Informationen.' },
        ],
      },
      {
        heading: '6. Platzierte Cookies',
        subsections: [
          { heading: 'Google Analytics — Statistiken', content: 'Wird zur Analyse des Plattformverkehrs und des Nutzerverhaltens verwendet. Daten werden anonymisiert.' },
          { heading: 'Google OAuth — Funktional', content: 'Ermöglicht die Anmeldung mit Google und speichert Sitzungstoken zur Authentifizierung.' },
          { heading: 'Stripe — Funktional', content: 'Sichere Zahlungsabwicklung. Stripe setzt Cookies zur Betrugsprävention und Verwaltung von Zahlungssitzungen.' },
          { heading: 'JWT Auth (intern) — Funktional', content: 'Intern verwendete Authentifizierungstoken zur Aufrechterhaltung der Benutzersitzung. Nach Sitzungsablauf gelöscht.' },
        ],
      },
      { heading: '7. Einwilligung', paragraphs: ['Wenn Sie unsere Website zum ersten Mal besuchen, zeigen wir Ihnen ein Pop-up-Fenster mit einer Erklärung zu Cookies. Sobald Sie auf „Einstellungen speichern" klicken, stimmen Sie der Verwendung der ausgewählten Cookie-Kategorien gemäß dieser Richtlinie zu.', 'Sie können die Verwendung von Cookies über Ihren Browser deaktivieren, aber bitte beachten Sie, dass unsere Website möglicherweise nicht mehr ordnungsgemäß funktioniert.'] },
      { heading: '8. Aktivieren/Deaktivieren und Löschen von Cookies', paragraphs: ['Sie können Ihren Internetbrowser verwenden, um Cookies automatisch oder manuell zu löschen. Sie können auch angeben, dass bestimmte Cookies nicht gesetzt werden dürfen, oder den Browser so konfigurieren, dass Sie bei jedem Cookie eine Benachrichtigung erhalten.', 'Bitte beachten Sie, dass unsere Website möglicherweise nicht ordnungsgemäß funktioniert, wenn alle Cookies deaktiviert sind. Wenn Sie Cookies löschen, werden sie erneut gesetzt, wenn Sie bei Ihrem nächsten Besuch Ihre Einwilligung geben.'] },
      { heading: '9. Ihre Rechte in Bezug auf personenbezogene Daten', paragraphs: ['Gemäß DSGVO haben Sie folgende Rechte bezüglich personenbezogener Daten:'], items: ['Sie haben das Recht zu erfahren, warum Ihre personenbezogenen Daten benötigt werden, was damit geschieht und wie lange sie aufbewahrt werden.', 'Auskunftsrecht: Sie haben das Recht, auf Ihre personenbezogenen Daten zuzugreifen.', 'Berichtigungsrecht: Sie haben das Recht, Ihre personenbezogenen Daten jederzeit zu ergänzen, zu korrigieren, zu löschen oder zu sperren.', 'Wenn Sie Ihre Einwilligung zur Verarbeitung erteilt haben, haben Sie das Recht, diese zu widerrufen und die Löschung Ihrer Daten zu verlangen.', 'Recht auf Datenübertragbarkeit: Sie haben das Recht, alle Ihre personenbezogenen Daten vollständig an einen anderen Verantwortlichen zu übertragen.', 'Widerspruchsrecht: Sie können der Verarbeitung Ihrer Daten widersprechen, es sei denn, es gibt berechtigte Gründe.', 'Zur Ausübung dieser Rechte oder zur Beschwerde können Sie sich auch an Ihre nationale Datenschutzbehörde wenden.'] },
      { heading: '10. Kontaktdaten', paragraphs: ['Wenn Sie Fragen oder Kommentare zu unserer Cookie-Richtlinie haben, kontaktieren Sie uns bitte:', 'Doisense\nE-Mail: privacy@doisense.eu\nWebsite: https://doisense.eu'] },
    ],
    seoTitle: 'Cookie-Richtlinie - Doisense',
    seoDescription: 'Erfahre, welche Cookie-Typen Doisense nutzt und wie du Browser-Einstellungen steuern kannst.',
  },
  fr: {
    title: 'Politique de cookies (UE)',
    updated: 'Cette Politique de cookies a été mise à jour pour la dernière fois le 11 mars 2026 et s\'applique aux citoyens et résidents permanents de l\'Espace économique européen et de la Suisse.',
    sections: [
      { heading: '1. Introduction', paragraphs: ['Notre site web, https://doisense.eu (ci-après « le site »), utilise des cookies et d\'autres technologies similaires (toutes les technologies sont appelées ci-après « cookies »). Des cookies sont également placés par des tiers avec lesquels nous collaborons. Dans le document ci-dessous, nous vous informons de la manière dont nous utilisons les cookies sur notre site.'] },
      { heading: '2. Que sont les cookies ?', paragraphs: ['Un cookie est un petit fichier simple envoyé avec les pages de ce site web et stocké par votre navigateur sur le disque dur de votre ordinateur ou d\'un autre appareil. Les informations qui y sont stockées peuvent être renvoyées à nos serveurs ou aux serveurs de tiers concernés lors d\'une visite ultérieure.'] },
      { heading: '3. Que sont les scripts ?', paragraphs: ['Un script est un morceau de code de programme utilisé pour que notre site web fonctionne correctement et de manière interactive. Ce code est exécuté sur notre serveur ou sur votre appareil.'] },
      { heading: '4. Qu\'est-ce qu\'un web beacon ?', paragraphs: ['Un web beacon (ou balise pixel) est un petit morceau invisible de texte ou d\'image sur un site web, utilisé pour surveiller le trafic. À cette fin, diverses données vous concernant sont stockées via des web beacons.'] },
      {
        heading: '5. Cookies',
        subsections: [
          { heading: '5.1 Cookies techniques ou fonctionnels', content: 'Certains cookies s\'assurent que certaines parties du site fonctionnent correctement et que vos préférences d\'utilisateur sont mémorisées. Grâce aux cookies fonctionnels, vous n\'avez pas besoin de saisir à plusieurs reprises les mêmes informations. Nous pouvons placer ces cookies sans votre consentement.' },
          { heading: '5.2 Cookies statistiques', content: 'Nous utilisons des cookies statistiques pour optimiser l\'expérience du site pour nos utilisateurs. Nous vous demandons la permission de placer des cookies statistiques.' },
          { heading: '5.3 Cookies de marketing/suivi', content: 'Les cookies de marketing sont utilisés pour comprendre le comportement de navigation et améliorer le service. Doisense utilise des cookies de marketing limités, sans vendre vos données à des tiers.' },
          { heading: '5.4 Services tiers', content: 'Doisense intègre des services tiers — Google (authentification OAuth et Analytics) et Stripe (traitement des paiements) — qui peuvent placer leurs propres cookies. Veuillez consulter les politiques de confidentialité de ces fournisseurs pour plus d\'informations.' },
        ],
      },
      {
        heading: '6. Cookies placés',
        subsections: [
          { heading: 'Google Analytics — Statistiques', content: 'Utilisé pour analyser le trafic et le comportement des utilisateurs sur la plateforme. Données anonymisées.' },
          { heading: 'Google OAuth — Fonctionnel', content: 'Permet la connexion avec Google, en stockant des jetons de session nécessaires au maintien de l\'état d\'authentification.' },
          { heading: 'Stripe — Fonctionnel', content: 'Traitement sécurisé des paiements. Stripe place des cookies pour prévenir la fraude et gérer les sessions de paiement.' },
          { heading: 'JWT Auth (interne) — Fonctionnel', content: 'Jetons d\'authentification utilisés en interne pour maintenir la session utilisateur sur la plateforme. Supprimés à l\'expiration de la session.' },
        ],
      },
      { heading: '7. Consentement', paragraphs: ['Lors de votre première visite sur notre site, nous vous afficherons une fenêtre contextuelle expliquant les cookies. En cliquant sur « Enregistrer les préférences », vous consentez à notre utilisation des catégories de cookies sélectionnées, conformément à cette politique.', 'Vous pouvez désactiver l\'utilisation des cookies via votre navigateur, mais notez que notre site pourrait ne plus fonctionner correctement.'] },
      { heading: '8. Activation/désactivation et suppression des cookies', paragraphs: ['Vous pouvez utiliser votre navigateur Internet pour supprimer automatiquement ou manuellement les cookies. Vous pouvez également spécifier que certains cookies ne peuvent pas être placés, ou configurer votre navigateur pour recevoir un message à chaque placement de cookie.', 'Veuillez noter que notre site pourrait ne pas fonctionner correctement si tous les cookies sont désactivés. Si vous supprimez les cookies, ils seront replacés après votre consentement lors de votre prochaine visite.'] },
      { heading: '9. Vos droits concernant les données personnelles', paragraphs: ['En vertu du RGPD, vous disposez des droits suivants :'], items: ['Vous avez le droit de savoir pourquoi vos données personnelles sont nécessaires, ce qui en sera fait et combien de temps elles seront conservées.', 'Droit d\'accès : vous avez le droit d\'accéder à vos données personnelles que nous avons collectées.', 'Droit de rectification : vous avez le droit de compléter, corriger, supprimer ou bloquer vos données personnelles à tout moment.', 'Si vous nous avez donné votre consentement, vous avez le droit de le révoquer et de demander la suppression de vos données.', 'Droit à la portabilité : vous avez le droit de demander toutes vos données et de les transférer à un autre responsable.', 'Droit d\'opposition : vous pouvez vous opposer au traitement de vos données, sauf s\'il existe des raisons justifiées.', 'Pour exercer ces droits ou déposer une plainte, vous pouvez également contacter votre autorité nationale de protection des données.'] },
      { heading: '10. Coordonnées', paragraphs: ['Pour toute question concernant notre Politique de cookies, veuillez nous contacter :', 'Doisense\nEmail : privacy@doisense.eu\nSite web : https://doisense.eu'] },
    ],
    seoTitle: 'Politique de cookies - Doisense',
    seoDescription: 'Découvrez les types de cookies utilisés par Doisense et comment gérer vos paramètres de navigateur.',
  },
  it: {
    title: 'Informativa sui cookie (UE)',
    updated: 'Questa Informativa sui cookie è stata aggiornata l\'ultima volta l\'11 marzo 2026 e si applica ai cittadini e residenti permanenti dello Spazio Economico Europeo e della Svizzera.',
    sections: [
      { heading: '1. Introduzione', paragraphs: ['Il nostro sito web, https://doisense.eu (di seguito "il sito"), utilizza cookie e altre tecnologie simili (tutte le tecnologie sono denominate di seguito "cookie"). I cookie vengono inoltre inseriti da terze parti con cui collaboriamo. Nel documento seguente vi informiamo sull\'utilizzo dei cookie sul nostro sito.'] },
      { heading: '2. Cosa sono i cookie?', paragraphs: ['Un cookie è un piccolo file semplice inviato insieme alle pagine di questo sito web e memorizzato dal browser sul disco rigido del computer o di un altro dispositivo. Le informazioni ivi memorizzate possono essere reinviate ai nostri server o ai server di terze parti rilevanti durante una visita successiva.'] },
      { heading: '3. Cosa sono gli script?', paragraphs: ['Uno script è un frammento di codice di programma utilizzato per il corretto funzionamento interattivo del nostro sito web. Questo codice viene eseguito sul nostro server o sul vostro dispositivo.'] },
      { heading: '4. Cos\'è un web beacon?', paragraphs: ['Un web beacon (o pixel tag) è un piccolo frammento invisibile di testo o immagine su un sito web, utilizzato per monitorare il traffico. A tal fine, i web beacon possono memorizzare vari dati su di voi.'] },
      {
        heading: '5. Cookie',
        subsections: [
          { heading: '5.1 Cookie tecnici o funzionali', content: 'Alcuni cookie garantiscono il corretto funzionamento di determinate parti del sito e che le preferenze dell\'utente rimangano memorizzate. Grazie ai cookie funzionali, non è necessario inserire ripetutamente le stesse informazioni. Possiamo inserire questi cookie senza il vostro consenso.' },
          { heading: '5.2 Cookie statistici', content: 'Utilizziamo cookie statistici per ottimizzare l\'esperienza del sito per i nostri utenti. Vi chiediamo il permesso di inserire cookie statistici.' },
          { heading: '5.3 Cookie di marketing/tracciamento', content: 'I cookie di marketing vengono utilizzati per comprendere il comportamento di navigazione e migliorare il servizio. Doisense utilizza cookie di marketing limitati, senza vendere i vostri dati a terzi.' },
          { heading: '5.4 Servizi di terze parti', content: 'Doisense integra servizi di terze parti — Google (autenticazione OAuth e Analytics) e Stripe (elaborazione pagamenti) — che potrebbero inserire i propri cookie. Consultate le informative sulla privacy di questi fornitori per informazioni complete.' },
        ],
      },
      {
        heading: '6. Cookie inseriti',
        subsections: [
          { heading: 'Google Analytics — Statistiche', content: 'Utilizzato per analizzare il traffico e il comportamento degli utenti sulla piattaforma. Dati anonimizzati.' },
          { heading: 'Google OAuth — Funzionale', content: 'Consente l\'accesso con Google, memorizzando token di sessione necessari per mantenere lo stato di autenticazione.' },
          { heading: 'Stripe — Funzionale', content: 'Elaborazione sicura dei pagamenti. Stripe inserisce cookie per prevenire le frodi e gestire le sessioni di pagamento.' },
          { heading: 'JWT Auth (interno) — Funzionale', content: 'Token di autenticazione utilizzati internamente per mantenere la sessione utente sulla piattaforma. Eliminati alla scadenza della sessione.' },
        ],
      },
      { heading: '7. Consenso', paragraphs: ['Alla prima visita del nostro sito, mostreremo un pop-up con una spiegazione sui cookie. Facendo clic su "Salva preferenze", acconsentite all\'utilizzo delle categorie di cookie selezionate in conformità con questa informativa.', 'Potete disabilitare l\'uso dei cookie tramite il browser, ma tenete presente che il nostro sito potrebbe non funzionare correttamente.'] },
      { heading: '8. Attivazione/disattivazione ed eliminazione dei cookie', paragraphs: ['Potete utilizzare il vostro browser Internet per eliminare automaticamente o manualmente i cookie. Potete anche specificare che determinati cookie non possono essere inseriti o configurare il browser per ricevere una notifica ad ogni inserimento.', 'Tenete presente che il nostro sito potrebbe non funzionare correttamente se tutti i cookie sono disabilitati. Se eliminate i cookie, verranno reinseriti dopo il vostro consenso alla visita successiva.'] },
      { heading: '9. I vostri diritti riguardo ai dati personali', paragraphs: ['Ai sensi del GDPR, avete i seguenti diritti riguardo ai dati personali:'], items: ['Avete il diritto di sapere perché i vostri dati personali sono necessari, cosa ne verrà fatto e per quanto tempo saranno conservati.', 'Diritto di accesso: avete il diritto di accedere ai vostri dati personali che abbiamo raccolto.', 'Diritto di rettifica: avete il diritto di integrare, correggere, eliminare o bloccare i vostri dati personali in qualsiasi momento.', 'Se avete dato il consenso al trattamento, avete il diritto di revocarlo e richiedere la cancellazione dei dati.', 'Diritto alla portabilità: avete il diritto di richiedere tutti i vostri dati e trasferirli a un altro titolare.', 'Diritto di opposizione: potete opporvi al trattamento dei vostri dati, salvo che esistano motivi giustificati.', 'Per esercitare questi diritti o presentare un reclamo, potete anche contattare la vostra autorità nazionale per la protezione dei dati.'] },
      { heading: '10. Dati di contatto', paragraphs: ['Per domande e/o commenti sulla nostra Informativa sui cookie, vi preghiamo di contattarci:', 'Doisense\nEmail: privacy@doisense.eu\nSito web: https://doisense.eu'] },
    ],
    seoTitle: 'Informativa sui cookie - Doisense',
    seoDescription: 'Scopri quali tipi di cookie usa Doisense e come controllare le impostazioni del browser.',
  },
  es: {
    title: 'Política de cookies (UE)',
    updated: 'Esta Política de cookies fue actualizada por última vez el 11 de marzo de 2026 y se aplica a ciudadanos y residentes permanentes del Espacio Económico Europeo y Suiza.',
    sections: [
      { heading: '1. Introducción', paragraphs: ['Nuestro sitio web, https://doisense.eu (en adelante "el sitio"), utiliza cookies y otras tecnologías similares (todas las tecnologías se denominan en adelante "cookies"). Las cookies también son colocadas por terceros con quienes colaboramos. En el documento a continuación le informamos sobre cómo utilizamos cookies en nuestro sitio.'] },
      { heading: '2. ¿Qué son las cookies?', paragraphs: ['Una cookie es un pequeño archivo simple que se envía junto con las páginas de este sitio web y que su navegador almacena en el disco duro de su computadora u otro dispositivo. La información almacenada puede ser devuelta a nuestros servidores o a los servidores de terceros relevantes durante una visita posterior.'] },
      { heading: '3. ¿Qué son los scripts?', paragraphs: ['Un script es un fragmento de código de programa que se utiliza para que nuestro sitio web funcione correctamente e interactivamente. Este código se ejecuta en nuestro servidor o en su dispositivo.'] },
      { heading: '4. ¿Qué es una web beacon?', paragraphs: ['Una web beacon (o etiqueta de píxel) es un pequeño fragmento invisible de texto o imagen en un sitio web, utilizado para monitorizar el tráfico. Para ello, las web beacons pueden almacenar varios datos sobre usted.'] },
      {
        heading: '5. Cookies',
        subsections: [
          { heading: '5.1 Cookies técnicas o funcionales', content: 'Algunas cookies garantizan que ciertas partes del sitio funcionen correctamente y que sus preferencias de usuario permanezcan guardadas. Mediante cookies funcionales, no necesita introducir repetidamente la misma información. Podemos colocar estas cookies sin su consentimiento.' },
          { heading: '5.2 Cookies estadísticas', content: 'Utilizamos cookies estadísticas para optimizar la experiencia del sitio para nuestros usuarios. Le pedimos permiso para colocar cookies estadísticas.' },
          { heading: '5.3 Cookies de marketing/rastreo', content: 'Las cookies de marketing se utilizan para comprender el comportamiento de navegación y mejorar el servicio. Doisense utiliza cookies de marketing limitadas, sin vender sus datos a terceros.' },
          { heading: '5.4 Servicios de terceros', content: 'Doisense integra servicios de terceros — Google (autenticación OAuth y Analytics) y Stripe (procesamiento de pagos) — que pueden colocar sus propias cookies. Consulte las políticas de privacidad de estos proveedores para obtener información completa.' },
        ],
      },
      {
        heading: '6. Cookies colocadas',
        subsections: [
          { heading: 'Google Analytics — Estadísticas', content: 'Utilizado para analizar el tráfico y el comportamiento de los usuarios en la plataforma. Datos anonimizados.' },
          { heading: 'Google OAuth — Funcional', content: 'Permite el inicio de sesión con Google, almacenando tokens de sesión necesarios para mantener el estado de autenticación.' },
          { heading: 'Stripe — Funcional', content: 'Procesamiento seguro de pagos. Stripe coloca cookies para prevenir fraudes y gestionar sesiones de pago.' },
          { heading: 'JWT Auth (interno) — Funcional', content: 'Tokens de autenticación utilizados internamente para mantener la sesión del usuario en la plataforma. Eliminados al expirar la sesión.' },
        ],
      },
      { heading: '7. Consentimiento', paragraphs: ['Cuando visita nuestro sitio por primera vez, le mostraremos una ventana emergente con una explicación sobre las cookies. Al hacer clic en "Guardar preferencias", acepta el uso de las categorías de cookies seleccionadas de acuerdo con esta Política de cookies.', 'Puede deshabilitar el uso de cookies a través de su navegador, pero tenga en cuenta que nuestro sitio puede dejar de funcionar correctamente.'] },
      { heading: '8. Activación/desactivación y eliminación de cookies', paragraphs: ['Puede utilizar su navegador de Internet para eliminar automática o manualmente las cookies. También puede especificar que ciertas cookies no puedan colocarse o configurar el navegador para recibir una notificación cada vez que se coloque una cookie.', 'Tenga en cuenta que nuestro sitio puede no funcionar correctamente si se deshabilitan todas las cookies. Si elimina las cookies, se volverán a colocar después de su consentimiento en su próxima visita.'] },
      { heading: '9. Sus derechos sobre los datos personales', paragraphs: ['En virtud del RGPD, tiene los siguientes derechos con respecto a los datos personales:'], items: ['Tiene derecho a saber por qué son necesarios sus datos personales, qué se hará con ellos y cuánto tiempo se conservarán.', 'Derecho de acceso: tiene derecho a acceder a sus datos personales que hemos recopilado.', 'Derecho de rectificación: tiene derecho a complementar, corregir, eliminar o bloquear sus datos personales en cualquier momento.', 'Si nos ha dado su consentimiento, tiene derecho a revocarlo y solicitar la eliminación de sus datos.', 'Derecho a la portabilidad: tiene derecho a solicitar todos sus datos y transferirlos a otro responsable.', 'Derecho a oponerse: puede oponerse al tratamiento de sus datos, salvo que existan motivos justificados.', 'Para ejercer estos derechos o presentar una queja, también puede contactar con su autoridad nacional de protección de datos.'] },
      { heading: '10. Datos de contacto', paragraphs: ['Si tiene preguntas y/o comentarios sobre nuestra Política de cookies, contáctenos:', 'Doisense\nEmail: privacy@doisense.eu\nSitio web: https://doisense.eu'] },
    ],
    seoTitle: 'Política de cookies - Doisense',
    seoDescription: 'Descubre qué tipos de cookies usa Doisense y cómo controlar la configuración del navegador.',
  },
  pl: {
    title: 'Polityka cookies (UE)',
    updated: 'Niniejsza Polityka cookies została ostatnio zaktualizowana 11 marca 2026 r. i ma zastosowanie do obywateli i stałych rezydentów Europejskiego Obszaru Gospodarczego oraz Szwajcarii.',
    sections: [
      { heading: '1. Wprowadzenie', paragraphs: ['Nasza strona internetowa, https://doisense.eu (zwana dalej „stroną"), używa plików cookie i innych podobnych technologii (wszystkie technologie są dalej nazywane „plikami cookie"). Pliki cookie są też umieszczane przez strony trzecie, z którymi współpracujemy. W poniższym dokumencie informujemy o sposobie, w jaki używamy plików cookie na naszej stronie.'] },
      { heading: '2. Czym są pliki cookie?', paragraphs: ['Plik cookie to mały prosty plik wysyłany wraz ze stronami tej witryny i przechowywany przez przeglądarkę na dysku twardym komputera lub innego urządzenia. Przechowywane tam informacje mogą być przesyłane z powrotem na nasze serwery lub serwery odpowiednich stron trzecich podczas kolejnej wizyty.'] },
      { heading: '3. Czym są skrypty?', paragraphs: ['Skrypt to fragment kodu programu służący do prawidłowego i interaktywnego działania naszej strony. Kod ten jest wykonywany na naszym serwerze lub na Twoim urządzeniu.'] },
      { heading: '4. Czym jest web beacon?', paragraphs: ['Web beacon (lub znacznik pikselowy) to mały, niewidoczny fragment tekstu lub obrazu na stronie internetowej, służący do monitorowania ruchu. W tym celu web beacony mogą przechowywać różne dane o Tobie.'] },
      {
        heading: '5. Pliki cookie',
        subsections: [
          { heading: '5.1 Techniczne lub funkcjonalne pliki cookie', content: 'Niektóre pliki cookie zapewniają prawidłowe działanie określonych części strony oraz zachowanie Twoich preferencji. Dzięki funkcjonalnym plikom cookie nie musisz wielokrotnie wprowadzać tych samych informacji. Możemy umieszczać te pliki cookie bez Twojej zgody.' },
          { heading: '5.2 Statystyczne pliki cookie', content: 'Używamy statystycznych plików cookie do optymalizacji doświadczenia użytkownika na stronie. Prosimy o zgodę na umieszczanie statystycznych plików cookie.' },
          { heading: '5.3 Marketingowe/śledzące pliki cookie', content: 'Pliki cookie do celów marketingowych służą do rozumienia zachowania użytkowników i ulepszania usługi. Doisense używa ograniczonych plików cookie marketingowych, nie sprzedając Twoich danych stronom trzecim.' },
          { heading: '5.4 Usługi stron trzecich', content: 'Doisense integruje usługi stron trzecich — Google (uwierzytelnianie OAuth i Analytics) oraz Stripe (przetwarzanie płatności) — które mogą umieszczać własne pliki cookie. Zapoznaj się z politykami prywatności tych dostawców, aby uzyskać pełne informacje.' },
        ],
      },
      {
        heading: '6. Umieszczane pliki cookie',
        subsections: [
          { heading: 'Google Analytics — Statystyki', content: 'Używany do analizy ruchu i zachowania użytkowników na platformie. Dane są anonimizowane.' },
          { heading: 'Google OAuth — Funkcjonalne', content: 'Umożliwia logowanie przez Google, przechowując tokeny sesji niezbędne do utrzymania stanu uwierzytelnienia.' },
          { heading: 'Stripe — Funkcjonalne', content: 'Bezpieczne przetwarzanie płatności. Stripe umieszcza pliki cookie w celu zapobiegania oszustwom i zarządzania sesjami płatności.' },
          { heading: 'JWT Auth (wewnętrzne) — Funkcjonalne', content: 'Tokeny uwierzytelniające używane wewnętrznie do utrzymania sesji użytkownika na platformie. Usuwane po wygaśnięciu sesji.' },
        ],
      },
      { heading: '7. Zgoda', paragraphs: ['Przy pierwszej wizycie na naszej stronie wyświetlimy wyskakujące okno z wyjaśnieniem dotyczącym plików cookie. Klikając „Zapisz preferencje", wyrażasz zgodę na używanie wybranych kategorii plików cookie zgodnie z niniejszą Polityką.', 'Możesz zablokować używanie plików cookie w przeglądarce, ale pamiętaj, że nasza strona może wtedy nie działać prawidłowo.'] },
      { heading: '8. Włączanie/wyłączanie i usuwanie plików cookie', paragraphs: ['Możesz użyć przeglądarki internetowej, aby automatycznie lub ręcznie usuwać pliki cookie. Możesz też określić, że pewne pliki cookie nie mogą być umieszczane, lub skonfigurować przeglądarkę, aby powiadamiała Cię przy każdym umieszczeniu pliku cookie.', 'Pamiętaj, że nasza strona może nie działać prawidłowo, jeśli wszystkie pliki cookie są wyłączone. Jeśli usuniesz pliki cookie, zostaną one ponownie umieszczone po wyrażeniu zgody podczas kolejnej wizyty.'] },
      { heading: '9. Twoje prawa dotyczące danych osobowych', paragraphs: ['Zgodnie z RODO masz następujące prawa dotyczące danych osobowych:'], items: ['Masz prawo wiedzieć, dlaczego Twoje dane osobowe są potrzebne, co z nimi zrobimy i jak długo będą przechowywane.', 'Prawo dostępu: masz prawo dostępu do zebranych danych osobowych.', 'Prawo do sprostowania: masz prawo do uzupełnienia, poprawienia, usunięcia lub zablokowania swoich danych osobowych w dowolnym momencie.', 'Jeśli wyraziłeś zgodę na przetwarzanie danych, masz prawo ją cofnąć i zażądać usunięcia danych.', 'Prawo do przenoszenia danych: masz prawo zażądać wszystkich swoich danych i przenieść je do innego administratora.', 'Prawo do sprzeciwu: możesz sprzeciwić się przetwarzaniu swoich danych, chyba że istnieją uzasadnione podstawy do ich przetwarzania.', 'Aby skorzystać z tych praw lub złożyć skargę, możesz również skontaktować się z krajowym organem ochrony danych.'] },
      { heading: '10. Dane kontaktowe', paragraphs: ['W przypadku pytań dotyczących naszej Polityki cookies prosimy o kontakt:', 'Doisense\nEmail: privacy@doisense.eu\nStrona internetowa: https://doisense.eu'] },
    ],
    seoTitle: 'Polityka cookies - Doisense',
    seoDescription: 'Sprawdź, jakie typy cookies wykorzystuje Doisense i jak kontrolować ustawienia przeglądarki.',
  },
}

const text = computed(() => cookiesCopy[localeCode.value] || cookiesCopy.en)
const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>
