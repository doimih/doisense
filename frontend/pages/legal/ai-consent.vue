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
const { cmsPage, hasCmsContent } = useLegalCmsPage('ai-consent')

const copy: Record<string, {
  title: string
  updated: string
  sections: Array<{ title: string; body?: string; items?: string[] }>
  seoTitle: string
  seoDescription: string
}> = {
  ro: {
    title: 'Acord de utilizare a AI-ului',
    updated: 'Ultima actualizare: 11 martie 2026',
    sections: [
      {
        title: '1. Ce face AI-ul',
        items: [
          'oferă suport emoțional general',
          'pune întrebări',
          'generează rezumate și reflecții în limitele planului activ',
          'oferă recomandări non-medicale',
        ],
      },
      {
        title: '2. Ce NU face AI-ul',
        items: [
          'nu pune diagnostice',
          'nu oferă tratament',
          'nu oferă consiliere psihologică',
          'nu oferă sfaturi medicale',
          'nu gestionează situații de criză',
        ],
      },
      {
        title: '3. Responsabilitatea utilizatorului',
        body: 'Utilizatorul este responsabil pentru:',
        items: [
          'interpretarea răspunsurilor',
          'deciziile luate',
          'acțiunile sale',
        ],
      },
      {
        title: '4. Situații de risc',
        body: 'Dacă utilizatorul se confruntă cu:',
        items: [
          'depresie severă',
          'anxietate extremă',
          'gânduri suicidare',
          'crize emoționale',
        ],
      },
      {
        title: 'Clarificare',
        body: 'AI-ul afișează și disclaimere explicite în interfață și va îndruma utilizatorul să caute ajutor specializat în situații sensibile sau de criză.',
      },
    ],
    seoTitle: 'Acord de utilizare a AI-ului - Doisense',
    seoDescription: 'Vezi limitele, rolul și responsabilitățile privind utilizarea AI-ului în platforma Doisense.',
  },
  en: {
    title: 'AI Usage Agreement',
    updated: 'Last updated: March 11, 2026',
    sections: [
      {
        title: '1. What the AI does',
        items: [
          'provides general emotional support',
          'asks questions',
          'generates summaries and reflections within your active plan limits',
          'offers non-medical recommendations',
        ],
      },
      {
        title: '2. What the AI does NOT do',
        items: [
          'does not provide diagnoses',
          'does not provide treatment',
          'does not provide psychological counseling',
          'does not provide medical advice',
          'does not manage crisis situations',
        ],
      },
      {
        title: '3. User responsibility',
        body: 'The user is responsible for:',
        items: [
          'interpreting responses',
          'decisions made',
          'their own actions',
        ],
      },
      {
        title: '4. Risk situations',
        body: 'If the user is dealing with:',
        items: [
          'severe depression',
          'extreme anxiety',
          'suicidal thoughts',
          'emotional crises',
        ],
      },
      {
        title: 'Clarification',
        body: 'The interface includes explicit AI disclaimers, and the AI will direct users to seek specialized help in sensitive or crisis-related situations.',
      },
    ],
    seoTitle: 'AI Usage Agreement - Doisense',
    seoDescription: 'Review the limits, responsibilities, and intended use of AI within the Doisense platform.',
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