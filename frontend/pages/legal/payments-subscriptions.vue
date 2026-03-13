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
const { cmsPage, hasCmsContent } = useLegalCmsPage('payments-subscriptions')

const copy: Record<string, {
  title: string
  updated: string
  sections: Array<{ title: string; body?: string; items?: string[] }>
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    title: 'Politica de plăți și abonamente',
    updated: 'Ultima actualizare: 11 martie 2026',
    sections: [
      {
        title: '1. Procesator de plăți',
        body: 'Stripe.',
      },
      {
        title: '2. Tipuri de abonamente',
        items: ['BASIC', 'PREMIUM', 'VIP'],
      },
      {
        title: '3. Recurență',
        body: 'Abonamentele se reînnoiesc automat.',
      },
      {
        title: '4. Anulare',
        body: 'Utilizatorul poate anula oricând.',
      },
      {
        title: '5. Refund',
        body: 'Refund-urile sunt gestionate conform politicii Stripe.',
      },
      {
        title: '6. Facturare',
        body: 'Stripe emite facturi PDF automat.',
      },
    ],
    seoTitle: 'Politica de plăți și abonamente - Doisense',
    seoDescription: 'Vezi informațiile despre procesarea plăților, abonamente, recurență, anulare și refund în platforma Doisense.',
  },
  en: {
    title: 'Payments and Subscriptions Policy',
    updated: 'Last updated: March 11, 2026',
    sections: [
      {
        title: '1. Payment processor',
        body: 'Stripe.',
      },
      {
        title: '2. Subscription types',
        items: ['BASIC', 'PREMIUM', 'VIP'],
      },
      {
        title: '3. Recurrence',
        body: 'Subscriptions renew automatically.',
      },
      {
        title: '4. Cancellation',
        body: 'The user can cancel at any time.',
      },
      {
        title: '5. Refunds',
        body: 'Refunds are handled according to the Stripe policy.',
      },
      {
        title: '6. Invoicing',
        body: 'Stripe automatically issues PDF invoices.',
      },
    ],
    seoTitle: 'Payments and Subscriptions Policy - Doisense',
    seoDescription: 'Review payment processing, subscriptions, recurrence, cancellation, refunds, and invoicing in Doisense.',
  },
  de: {
    title: 'Richtlinie zu Zahlungen und Abonnements',
    updated: 'Zuletzt aktualisiert: 11. März 2026',
    sections: [
      {
        title: '1. Zahlungsabwickler',
        body: 'Stripe.',
      },
      {
        title: '2. Abonnementarten',
        items: ['BASIC', 'PREMIUM', 'VIP'],
      },
      {
        title: '3. Verlängerung',
        body: 'Abonnements verlängern sich automatisch.',
      },
      {
        title: '4. Kündigung',
        body: 'Der Nutzer kann jederzeit kündigen.',
      },
      {
        title: '5. Rückerstattungen',
        body: 'Rückerstattungen werden gemäß der Stripe-Richtlinie bearbeitet.',
      },
      {
        title: '6. Rechnungsstellung',
        body: 'Stripe stellt PDF-Rechnungen automatisch aus.',
      },
    ],
    seoTitle: 'Richtlinie zu Zahlungen und Abonnements - Doisense',
    seoDescription: 'Informiere dich über Zahlungsabwicklung, Abonnements, Verlängerung, Kündigung, Rückerstattungen und Rechnungsstellung bei Doisense.',
  },
  fr: {
    title: 'Politique de paiements et d’abonnements',
    updated: 'Dernière mise à jour : 11 mars 2026',
    sections: [
      {
        title: '1. Prestataire de paiement',
        body: 'Stripe.',
      },
      {
        title: '2. Types d’abonnements',
        items: ['BASIC', 'PREMIUM', 'VIP'],
      },
      {
        title: '3. Reconduction',
        body: 'Les abonnements sont renouvelés automatiquement.',
      },
      {
        title: '4. Résiliation',
        body: 'L’utilisateur peut résilier à tout moment.',
      },
      {
        title: '5. Remboursements',
        body: 'Les remboursements sont traités conformément à la politique de Stripe.',
      },
      {
        title: '6. Facturation',
        body: 'Stripe émet automatiquement des factures PDF.',
      },
    ],
    seoTitle: 'Politique de paiements et d’abonnements - Doisense',
    seoDescription: 'Consulte les informations sur le traitement des paiements, les abonnements, la reconduction, la résiliation, les remboursements et la facturation dans Doisense.',
  },
  it: {
    title: 'Politica di pagamenti e abbonamenti',
    updated: 'Ultimo aggiornamento: 11 marzo 2026',
    sections: [
      {
        title: '1. Processore di pagamento',
        body: 'Stripe.',
      },
      {
        title: '2. Tipi di abbonamento',
        items: ['BASIC', 'PREMIUM', 'VIP'],
      },
      {
        title: '3. Rinnovo',
        body: 'Gli abbonamenti si rinnovano automaticamente.',
      },
      {
        title: '4. Annullamento',
        body: 'L’utente può annullare in qualsiasi momento.',
      },
      {
        title: '5. Rimborsi',
        body: 'I rimborsi vengono gestiti secondo la politica di Stripe.',
      },
      {
        title: '6. Fatturazione',
        body: 'Stripe emette automaticamente fatture PDF.',
      },
    ],
    seoTitle: 'Politica di pagamenti e abbonamenti - Doisense',
    seoDescription: 'Consulta le informazioni su elaborazione dei pagamenti, abbonamenti, rinnovo, annullamento, rimborsi e fatturazione in Doisense.',
  },
  es: {
    title: 'Política de pagos y suscripciones',
    updated: 'Última actualización: 11 de marzo de 2026',
    sections: [
      {
        title: '1. Procesador de pagos',
        body: 'Stripe.',
      },
      {
        title: '2. Tipos de suscripción',
        items: ['BASIC', 'PREMIUM', 'VIP'],
      },
      {
        title: '3. Renovación',
        body: 'Las suscripciones se renuevan automáticamente.',
      },
      {
        title: '4. Cancelación',
        body: 'El usuario puede cancelar en cualquier momento.',
      },
      {
        title: '5. Reembolsos',
        body: 'Los reembolsos se gestionan según la política de Stripe.',
      },
      {
        title: '6. Facturación',
        body: 'Stripe emite automáticamente facturas en PDF.',
      },
    ],
    seoTitle: 'Política de pagos y suscripciones - Doisense',
    seoDescription: 'Consulta la información sobre procesamiento de pagos, suscripciones, renovación, cancelación, reembolsos y facturación en Doisense.',
  },
  pl: {
    title: 'Polityka płatności i subskrypcji',
    updated: 'Ostatnia aktualizacja: 11 marca 2026',
    sections: [
      {
        title: '1. Operator płatności',
        body: 'Stripe.',
      },
      {
        title: '2. Rodzaje subskrypcji',
        items: ['BASIC', 'PREMIUM', 'VIP'],
      },
      {
        title: '3. Odnawianie',
        body: 'Subskrypcje odnawiają się automatycznie.',
      },
      {
        title: '4. Anulowanie',
        body: 'Użytkownik może anulować w dowolnym momencie.',
      },
      {
        title: '5. Zwroty',
        body: 'Zwroty są obsługiwane zgodnie z polityką Stripe.',
      },
      {
        title: '6. Fakturowanie',
        body: 'Stripe automatycznie wystawia faktury PDF.',
      },
    ],
    seoTitle: 'Polityka płatności i subskrypcji - Doisense',
    seoDescription: 'Sprawdź informacje o przetwarzaniu płatności, subskrypcjach, odnawianiu, anulowaniu, zwrotach i fakturowaniu w Doisense.',
  },
}

const text = computed(() => copy[localeCode.value] || copy.en)
const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>