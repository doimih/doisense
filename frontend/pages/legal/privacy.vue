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
      title: 'Politica de confidențialitate',
      updated: 'Ultima actualizare: 08 martie 2026',
      sections: [
        { title: '1. Ce date colectăm', body: 'Date de cont (email), conținut introdus în jurnal/chat, metadate tehnice necesare securității și funcționării aplicației.' },
        { title: '2. Scopul prelucrării', body: 'Folosim datele pentru autentificare, furnizarea funcționalităților, personalizarea răspunsurilor AI și îmbunătățirea calității serviciului.' },
        { title: '3. Temei legal', body: 'Executarea contractului (serviciul oferit), interes legitim pentru securitate/operare și consimțământ unde este necesar.' },
        { title: '4. Stocare și retenție', body: 'Datele sunt păstrate atât timp cât contul este activ sau cât este necesar pentru obligații legale și audit minim de securitate.' },
        { title: '5. Partajare', body: 'Nu vindem date personale. Putem folosi furnizori tehnici (hosting, plăți, AI) strict pentru furnizarea serviciului, cu măsuri contractuale adecvate.' },
      ],
    }
  }

  return {
    title: 'Privacy Policy',
    updated: 'Last updated: March 8, 2026',
    sections: [
      { title: '1. Data we collect', body: 'Account data (email), journal/chat content you provide, and technical metadata required for security and platform operation.' },
      { title: '2. Why we process data', body: 'We process data for authentication, feature delivery, AI response personalization, and service quality improvements.' },
      { title: '3. Legal basis', body: 'Contract performance, legitimate interest for security/operations, and consent where required.' },
      { title: '4. Storage and retention', body: 'Data is retained while your account is active or as needed for legal obligations and minimum security auditing.' },
      { title: '5. Sharing', body: 'We do not sell personal data. Technical providers (hosting, payments, AI) may process data only to deliver the service under proper safeguards.' },
    ],
  }
})
</script>
