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

      <section class="bg-white border border-stone-200 rounded-xl p-5 space-y-3">
        <p class="text-stone-700 text-sm leading-6">{{ text.intro }}</p>
        <ul class="space-y-2 text-sm text-stone-700">
          <li v-for="item in text.items" :key="item">• {{ item }}</li>
        </ul>
        <p class="text-xs text-stone-500">{{ text.note }}</p>
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

const cookiesCopy: Record<string, {
  title: string
  updated: string
  intro: string
  items: string[]
  note: string
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    title: 'Politica de cookie-uri',
    updated: 'Ultima actualizare: 08 martie 2026',
    intro: 'Folosim cookie-uri și tehnologii similare pentru autentificare, păstrarea limbii selectate și funcționarea corectă a interfeței.',
    items: [
      'Cookie-uri esențiale: necesare autentificării și securității sesiunii.',
      'Cookie-uri de preferințe: memorarea limbii și setărilor de interfață.',
      'Cookie-uri tehnice: diagnostic minim pentru stabilitate și performanță.',
    ],
    note: 'Poți controla cookie-urile din setările browserului. Dezactivarea celor esențiale poate afecta funcționarea aplicației.',
    seoTitle: 'Politica de cookie-uri - Doisense',
    seoDescription: 'Află ce tipuri de cookie-uri folosește Doisense și cum poți controla setările din browser.',
  },
  en: {
    title: 'Cookie Policy',
    updated: 'Last updated: March 8, 2026',
    intro: 'We use cookies and similar technologies for authentication, selected-language persistence, and proper UI operation.',
    items: [
      'Essential cookies: required for authentication and session security.',
      'Preference cookies: remember language and interface settings.',
      'Technical cookies: minimal diagnostics for stability and performance.',
    ],
    note: 'You can control cookies in your browser settings. Disabling essential cookies may impact platform functionality.',
    seoTitle: 'Cookie Policy - Doisense',
    seoDescription: 'Find out what cookie types Doisense uses and how you can control browser settings.',
  },
  de: {
    title: 'Cookie-Richtlinie',
    updated: 'Letzte Aktualisierung: 08. März 2026',
    intro: 'Wir verwenden Cookies und ähnliche Technologien für Authentifizierung, Sprachauswahl und eine stabile Oberfläche.',
    items: [
      'Essenzielle Cookies: erforderlich für Authentifizierung und Sitzungssicherheit.',
      'Präferenz-Cookies: speichern Sprache und Oberflächeinstellungen.',
      'Technische Cookies: minimale Diagnostik für Stabilität und Leistung.',
    ],
    note: 'Du kannst Cookies in den Browsereinstellungen verwalten. Das Deaktivieren essenzieller Cookies kann Funktionen einschränken.',
    seoTitle: 'Cookie-Richtlinie - Doisense',
    seoDescription: 'Erfahre, welche Cookie-Typen Doisense nutzt und wie du Browser-Einstellungen steuern kannst.',
  },
  fr: {
    title: 'Politique de cookies',
    updated: 'Derniere mise a jour: 08 mars 2026',
    intro: 'Nous utilisons des cookies et technologies similaires pour l\'authentification, la langue choisie et le bon fonctionnement de l\'interface.',
    items: [
      'Cookies essentiels: necessaires a l\'authentification et a la securite de session.',
      'Cookies de preference: memorisent la langue et les parametres d\'interface.',
      'Cookies techniques: diagnostic minimal pour la stabilite et les performances.',
    ],
    note: 'Vous pouvez gerer les cookies dans les parametres du navigateur. Desactiver les cookies essentiels peut limiter certaines fonctions.',
    seoTitle: 'Politique de cookies - Doisense',
    seoDescription: 'Decouvrez les types de cookies utilises par Doisense et comment gerer vos parametres navigateur.',
  },
  it: {
    title: 'Politica sui cookie',
    updated: 'Ultimo aggiornamento: 08 marzo 2026',
    intro: 'Usiamo cookie e tecnologie simili per autenticazione, lingua selezionata e corretto funzionamento dell’interfaccia.',
    items: [
      'Cookie essenziali: necessari per autenticazione e sicurezza della sessione.',
      'Cookie preferenze: memorizzano lingua e impostazioni interfaccia.',
      'Cookie tecnici: diagnostica minima per stabilità e performance.',
    ],
    note: 'Puoi gestire i cookie nelle impostazioni del browser. Disabilitare quelli essenziali può limitare alcune funzioni.',
    seoTitle: 'Politica sui cookie - Doisense',
    seoDescription: 'Scopri quali tipi di cookie usa Doisense e come controllare le impostazioni del browser.',
  },
  es: {
    title: 'Política de cookies',
    updated: 'Última actualización: 08 de marzo de 2026',
    intro: 'Usamos cookies y tecnologías similares para autenticación, idioma seleccionado y correcto funcionamiento de la interfaz.',
    items: [
      'Cookies esenciales: necesarias para autenticación y seguridad de sesión.',
      'Cookies de preferencias: recuerdan idioma y ajustes de interfaz.',
      'Cookies técnicas: diagnóstico mínimo para estabilidad y rendimiento.',
    ],
    note: 'Puedes gestionar las cookies en tu navegador. Desactivar las esenciales puede afectar el funcionamiento.',
    seoTitle: 'Política de cookies - Doisense',
    seoDescription: 'Descubre qué tipos de cookies usa Doisense y cómo controlar la configuración del navegador.',
  },
  pl: {
    title: 'Polityka cookies',
    updated: 'Ostatnia aktualizacja: 08 marca 2026',
    intro: 'Używamy cookies i podobnych technologii do uwierzytelniania, zapamiętywania języka i poprawnego działania interfejsu.',
    items: [
      'Cookies niezbędne: wymagane do uwierzytelniania i bezpieczeństwa sesji.',
      'Cookies preferencji: zapamiętują język i ustawienia interfejsu.',
      'Cookies techniczne: minimalna diagnostyka dla stabilności i wydajności.',
    ],
    note: 'Możesz zarządzać cookies w ustawieniach przeglądarki. Wyłączenie niezbędnych cookies może ograniczyć działanie.',
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
