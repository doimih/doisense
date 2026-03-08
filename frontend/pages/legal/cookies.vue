<template>
  <article class="max-w-4xl mx-auto py-10 space-y-6">
    <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
    <p class="text-sm text-stone-500">{{ text.updated }}</p>

    <section class="bg-white border border-stone-200 rounded-xl p-5 space-y-3">
      <p class="text-stone-700 text-sm leading-6">{{ text.intro }}</p>
      <ul class="space-y-2 text-sm text-stone-700">
        <li v-for="item in text.items" :key="item">• {{ item }}</li>
      </ul>
      <p class="text-xs text-stone-500">{{ text.note }}</p>
    </section>
  </article>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const isRo = computed(() => locale.value.startsWith('ro'))

const text = computed(() => {
  if (isRo.value) {
    return {
      title: 'Politica de cookie-uri',
      updated: 'Ultima actualizare: 08 martie 2026',
      intro: 'Folosim cookie-uri și tehnologii similare pentru autentificare, păstrarea limbii selectate și funcționarea corectă a interfeței.',
      items: [
        'Cookie-uri esențiale: necesare autentificării și securității sesiunii.',
        'Cookie-uri de preferințe: memorarea limbii și setărilor de interfață.',
        'Cookie-uri tehnice: diagnostic minim pentru stabilitate și performanță.',
      ],
      note: 'Poți controla cookie-urile din setările browserului. Dezactivarea celor esențiale poate afecta funcționarea aplicației.',
    }
  }

  return {
    title: 'Cookie Policy',
    updated: 'Last updated: March 8, 2026',
    intro: 'We use cookies and similar technologies for authentication, selected-language persistence, and proper UI operation.',
    items: [
      'Essential cookies: required for authentication and session security.',
      'Preference cookies: remember language and interface settings.',
      'Technical cookies: minimal diagnostics for stability and performance.',
    ],
    note: 'You can control cookies in your browser settings. Disabling essential cookies may impact platform functionality.',
  }
})
</script>
