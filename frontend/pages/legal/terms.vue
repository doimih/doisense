<template>
  <article class="max-w-4xl mx-auto py-10 space-y-6">
    <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
    <p class="text-sm text-stone-500">{{ text.updated }}</p>

    <section v-for="section in text.sections" :key="section.title" class="bg-white border border-stone-200 rounded-xl p-5">
      <h2 class="text-xl font-semibold text-stone-900 mb-2">{{ section.title }}</h2>
      <p class="text-stone-700 text-sm leading-6">{{ section.body }}</p>
    </section>
  </article>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const isRo = computed(() => locale.value.startsWith('ro'))

const text = computed(() => {
  if (isRo.value) {
    return {
      title: 'Termeni și condiții',
      updated: 'Ultima actualizare: 08 martie 2026',
      sections: [
        { title: '1. Acceptarea termenilor', body: 'Prin utilizarea platformei accepți acești termeni. Dacă nu ești de acord, nu utiliza serviciul.' },
        { title: '2. Contul tău', body: 'Ești responsabil pentru confidențialitatea credentialelor și pentru activitatea din contul tău.' },
        { title: '3. Utilizare permisă', body: 'Nu utiliza serviciul pentru activități ilegale, abuzive sau care încalcă drepturile altor persoane.' },
        { title: '4. Plăți și premium', body: 'Funcțiile premium sunt gestionate prin Stripe. Condițiile comerciale sunt afișate înainte de plată.' },
        { title: '5. Limitarea răspunderii', body: 'Serviciul este oferit ca instrument digital de suport și nu înlocuiește consultanța medicală/psihologică specializată.' },
      ],
    }
  }

  return {
    title: 'Terms and Conditions',
    updated: 'Last updated: March 8, 2026',
    sections: [
      { title: '1. Acceptance', body: 'By using the platform you agree to these terms. If you disagree, do not use the service.' },
      { title: '2. Your account', body: 'You are responsible for credential confidentiality and all activity under your account.' },
      { title: '3. Allowed use', body: 'Do not use the service for unlawful, abusive, or rights-infringing activities.' },
      { title: '4. Payments and premium', body: 'Premium features are handled via Stripe. Commercial terms are shown before payment confirmation.' },
      { title: '5. Liability limitation', body: 'The service is a digital support tool and does not replace professional medical or psychological care.' },
    ],
  }
})
</script>
