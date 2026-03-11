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
}

const text = computed(() => copy[localeCode.value] || copy.en)
const seoTitle = computed(() => text.value.seoTitle)
const seoDescription = computed(() => text.value.seoDescription)

usePublicSeo({
  title: seoTitle,
  description: seoDescription,
})
</script>