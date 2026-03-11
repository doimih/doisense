<template>
  <section class="rounded-3xl bg-sky-100/70 px-5 py-10 md:px-10 md:py-14">
    <div class="mx-auto max-w-5xl space-y-10">
      <header class="space-y-4 text-center">
        <p class="inline-flex items-center rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold text-stone-700">
          {{ text.badge }}
        </p>
        <h1 class="text-4xl md:text-6xl font-bold text-stone-900">{{ text.title }}</h1>
        <p class="mx-auto max-w-3xl text-lg leading-8 text-stone-600">{{ text.subtitle }}</p>
      </header>

      <section class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        <article
          v-for="item in text.items"
          :key="item.title"
          class="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-full border border-stone-200 bg-stone-50 text-xl">
            {{ item.icon }}
          </div>
          <h2 class="mt-4 text-3xl font-semibold leading-tight text-stone-900">{{ item.title }}</h2>
          <p class="mt-3 text-xl leading-8 text-stone-600">{{ item.description }}</p>
          <NuxtLink
            :to="localePath(item.to)"
            class="mt-6 inline-flex items-center gap-2 text-xl font-semibold text-stone-900"
          >
            {{ item.action }}
            <span class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-sky-100 text-stone-800">→</span>
          </NuxtLink>
        </article>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const { locale } = useI18n()

const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

type FaqItem = {
  icon: string
  title: string
  description: string
  action: string
  to: '/programs' | '/journal' | '/pricing' | '/profile' | '/legal/privacy' | '/contact'
}

const faqCopy: Record<string, {
  badge: string
  title: string
  subtitle: string
  items: FaqItem[]
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    badge: 'Centru de ajutor',
    title: 'Suport la fiecare pas',
    subtitle: 'Găsești răspunsuri pentru programe, cont, plăți și confidențialitate, plus contact direct când ai nevoie.',
    items: [
      { icon: '❓', title: 'Întrebări generale', description: 'Răspunsuri rapide despre funcționalități, jurnal, AI chat și start în platformă.', action: 'Vezi răspunsuri', to: '/programs' },
      { icon: '📅', title: 'Ajutor programe', description: 'Cum începi un program, cum urmărești pașii și cum îți menții progresul.', action: 'Vezi ghid', to: '/programs' },
      { icon: '💳', title: 'Informații plăți', description: 'Detalii despre planuri, upgrade Premium și procesarea sigură prin Stripe.', action: 'Află mai mult', to: '/pricing' },
      { icon: '👤', title: 'Acces cont', description: 'Recuperare acces, actualizare profil și setări personale.', action: 'Primește suport', to: '/profile' },
      { icon: '🔒', title: 'Politica de confidențialitate', description: 'Cum protejăm datele tale și ce drepturi ai în platformă.', action: 'Vezi politica', to: '/legal/privacy' },
      { icon: '💬', title: 'Vorbește cu noi', description: 'Dacă nu găsești ce cauți, echipa noastră îți răspunde direct.', action: 'Trimite mesaj', to: '/contact' },
    ],
    seoTitle: 'FAQ Doisense - Suport, plăți, cont și GDPR',
    seoDescription: 'Pagina FAQ Doisense cu răspunsuri despre programe, cont, plăți și confidențialitate.',
  },
  en: {
    badge: 'Help Center',
    title: 'Support At Every Step',
    subtitle: 'Find answers about programs, account, payments, and privacy, plus direct contact when needed.',
    items: [
      { icon: '❓', title: 'General Questions', description: 'Quick answers about features, journaling, AI chat, and getting started.', action: 'View Answers', to: '/programs' },
      { icon: '📅', title: 'Program Help', description: 'How to start a program, follow daily steps, and keep progress consistent.', action: 'See Guide', to: '/programs' },
      { icon: '💳', title: 'Payment Info', description: 'Details about plans, Premium upgrade, and secure Stripe payment flow.', action: 'Learn More', to: '/pricing' },
      { icon: '👤', title: 'Account Access', description: 'Password recovery, profile updates, and personal account settings.', action: 'Get Support', to: '/profile' },
      { icon: '🔒', title: 'Privacy Policy', description: 'How we protect your data and what rights you have as a user.', action: 'View Policy', to: '/legal/privacy' },
      { icon: '💬', title: 'Talk To Us', description: 'If you cannot find what you need, contact our support team directly.', action: 'Send Message', to: '/contact' },
    ],
    seoTitle: 'Doisense FAQ - Support, billing, account, privacy',
    seoDescription: 'FAQ page with support resources for programs, payments, account access, and privacy.',
  },
  de: { badge: 'Help Center', title: 'Support in jedem Schritt', subtitle: 'Antworten zu Programmen, Konto, Zahlungen und Datenschutz plus direkter Kontakt.', items: [ { icon: '❓', title: 'Allgemeine Fragen', description: 'Schnelle Antworten zu Funktionen, Tagebuch und KI-Chat.', action: 'Antworten ansehen', to: '/programs' }, { icon: '📅', title: 'Programm-Hilfe', description: 'So startest du Programme und verfolgst deinen Fortschritt.', action: 'Leitfaden', to: '/programs' }, { icon: '💳', title: 'Zahlungsinfos', description: 'Pläne, Premium-Upgrade und sichere Stripe-Zahlung.', action: 'Mehr erfahren', to: '/pricing' }, { icon: '👤', title: 'Kontozugang', description: 'Zugang wiederherstellen und Profil aktualisieren.', action: 'Support', to: '/profile' }, { icon: '🔒', title: 'Datenschutz', description: 'Wie wir Daten schützen und welche Rechte du hast.', action: 'Richtlinie', to: '/legal/privacy' }, { icon: '💬', title: 'Mit uns sprechen', description: 'Unser Team hilft dir direkt weiter.', action: 'Nachricht senden', to: '/contact' } ], seoTitle: 'Doisense FAQ', seoDescription: 'FAQ mit Hilfe zu Programmen, Zahlungen und Datenschutz.' },
  fr: { badge: 'Centre d aide', title: 'Support a chaque etape', subtitle: 'Reponses sur les programmes, le compte, les paiements et la confidentialite.', items: [ { icon: '❓', title: 'Questions generales', description: 'Reponses rapides sur les fonctionnalites et le journal guide.', action: 'Voir', to: '/programs' }, { icon: '📅', title: 'Aide programmes', description: 'Commencer un programme et suivre vos etapes.', action: 'Voir guide', to: '/programs' }, { icon: '💳', title: 'Infos paiement', description: 'Plans, upgrade Premium et Stripe securise.', action: 'En savoir plus', to: '/pricing' }, { icon: '👤', title: 'Acces compte', description: 'Recuperation d acces et mise a jour profil.', action: 'Support', to: '/profile' }, { icon: '🔒', title: 'Confidentialite', description: 'Protection des donnees et droits utilisateur.', action: 'Voir politique', to: '/legal/privacy' }, { icon: '💬', title: 'Parlez-nous', description: 'Contact direct avec notre equipe support.', action: 'Envoyer message', to: '/contact' } ], seoTitle: 'FAQ Doisense', seoDescription: 'Aide sur programmes, paiements, compte et confidentialite.' },
  it: { badge: 'Help Center', title: 'Supporto in ogni passo', subtitle: 'Risposte su programmi, account, pagamenti e privacy.', items: [ { icon: '❓', title: 'Domande generali', description: 'Risposte rapide su funzionalita, diario e chat AI.', action: 'Vedi risposte', to: '/programs' }, { icon: '📅', title: 'Aiuto programmi', description: 'Come iniziare e seguire i programmi guidati.', action: 'Guida', to: '/programs' }, { icon: '💳', title: 'Info pagamenti', description: 'Piani, upgrade Premium e Stripe sicuro.', action: 'Scopri', to: '/pricing' }, { icon: '👤', title: 'Accesso account', description: 'Recupero accesso e aggiornamento profilo.', action: 'Supporto', to: '/profile' }, { icon: '🔒', title: 'Privacy policy', description: 'Come proteggiamo i dati personali.', action: 'Vedi policy', to: '/legal/privacy' }, { icon: '💬', title: 'Parla con noi', description: 'Contatto diretto con il team supporto.', action: 'Invia messaggio', to: '/contact' } ], seoTitle: 'FAQ Doisense', seoDescription: 'Supporto su programmi, pagamenti, account e privacy.' },
  es: { badge: 'Centro de ayuda', title: 'Soporte en cada paso', subtitle: 'Respuestas sobre programas, cuenta, pagos y privacidad.', items: [ { icon: '❓', title: 'Preguntas generales', description: 'Respuestas rápidas sobre funciones, diario y chat AI.', action: 'Ver respuestas', to: '/programs' }, { icon: '📅', title: 'Ayuda programas', description: 'Cómo empezar y seguir programas guiados.', action: 'Ver guía', to: '/programs' }, { icon: '💳', title: 'Info pagos', description: 'Planes, upgrade Premium y Stripe seguro.', action: 'Más info', to: '/pricing' }, { icon: '👤', title: 'Acceso cuenta', description: 'Recuperación de acceso y actualización de perfil.', action: 'Obtener soporte', to: '/profile' }, { icon: '🔒', title: 'Política privacidad', description: 'Cómo protegemos tus datos personales.', action: 'Ver política', to: '/legal/privacy' }, { icon: '💬', title: 'Habla con nosotros', description: 'Contacto directo con nuestro equipo.', action: 'Enviar mensaje', to: '/contact' } ], seoTitle: 'FAQ Doisense', seoDescription: 'Ayuda sobre programas, pagos, cuenta y privacidad.' },
  pl: { badge: 'Centrum pomocy', title: 'Wsparcie na kazdym kroku', subtitle: 'Odpowiedzi o programach, koncie, platnosciach i prywatnosci.', items: [ { icon: '❓', title: 'Pytania ogolne', description: 'Szybkie odpowiedzi o funkcjach, dzienniku i chat AI.', action: 'Zobacz', to: '/programs' }, { icon: '📅', title: 'Pomoc programy', description: 'Jak zaczac i realizowac programy krok po kroku.', action: 'Przewodnik', to: '/programs' }, { icon: '💳', title: 'Informacje platnosci', description: 'Plany, Premium i bezpieczny Stripe.', action: 'Dowiedz sie', to: '/pricing' }, { icon: '👤', title: 'Dostep do konta', description: 'Odzyskanie dostepu i aktualizacja profilu.', action: 'Wsparcie', to: '/profile' }, { icon: '🔒', title: 'Polityka prywatnosci', description: 'Jak chronimy dane osobowe.', action: 'Zobacz polityke', to: '/legal/privacy' }, { icon: '💬', title: 'Napisz do nas', description: 'Bezposredni kontakt z zespolem wsparcia.', action: 'Wyslij wiadomosc', to: '/contact' } ], seoTitle: 'FAQ Doisense', seoDescription: 'Pomoc dot. programow, platnosci, konta i prywatnosci.' },
}

const text = computed(() => faqCopy[localeCode.value] || faqCopy.en)

usePublicSeo({
  title: computed(() => text.value.seoTitle),
  description: computed(() => text.value.seoDescription),
})
</script>
