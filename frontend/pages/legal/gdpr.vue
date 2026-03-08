<template>
  <article class="max-w-4xl mx-auto py-10 space-y-6">
    <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
    <p class="text-stone-600">{{ text.subtitle }}</p>

    <section class="bg-white border border-stone-200 rounded-xl p-5">
      <h2 class="text-xl font-semibold text-stone-900 mb-3">{{ text.rightsTitle }}</h2>
      <ul class="space-y-2 text-sm text-stone-700">
        <li v-for="right in text.rights" :key="right">• {{ right }}</li>
      </ul>
    </section>

    <section class="bg-stone-900 text-white rounded-xl p-5 space-y-2">
      <h2 class="text-xl font-semibold">{{ text.requestTitle }}</h2>
      <p class="text-sm text-stone-100">{{ text.requestText }}</p>
      <p class="text-sm">privacy@doisense.app</p>
      <p class="text-xs text-stone-200">{{ text.requestNote }}</p>
    </section>
  </article>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const isRo = computed(() => locale.value.startsWith('ro'))

const text = computed(() => {
  if (isRo.value) {
    return {
      title: 'Drepturile tale GDPR',
      subtitle: 'Ai control asupra datelor tale personale. Poți trimite solicitări în orice moment.',
      rightsTitle: 'Drepturi principale',
      rights: [
        'Drept de acces la datele personale prelucrate.',
        'Drept la rectificarea datelor inexacte.',
        'Drept la ștergere („dreptul de a fi uitat”), când se aplică.',
        'Drept la restricționarea prelucrării.',
        'Drept la portabilitatea datelor într-un format utilizabil.',
        'Drept de opoziție la anumite tipuri de prelucrare.',
      ],
      requestTitle: 'Cum trimiți o solicitare',
      requestText: 'Trimite un email cu subiectul "GDPR Request" și detalii despre cererea ta.',
      requestNote: 'Putem solicita verificare suplimentară a identității pentru a proteja datele contului tău.',
    }
  }

  return {
    title: 'Your GDPR Rights',
    subtitle: 'You remain in control of your personal data and can submit requests at any time.',
    rightsTitle: 'Core rights',
    rights: [
      'Right of access to your personal data.',
      'Right to rectification of inaccurate data.',
      'Right to erasure (right to be forgotten), where applicable.',
      'Right to restriction of processing.',
      'Right to data portability in a usable format.',
      'Right to object to certain processing activities.',
    ],
    requestTitle: 'How to submit a request',
    requestText: 'Send an email with subject "GDPR Request" and details of your request.',
    requestNote: 'We may request additional identity verification to protect your account data.',
  }
})
</script>
