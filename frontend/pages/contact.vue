<template>
  <section class="max-w-3xl mx-auto py-10 space-y-6">
    <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
    <p class="text-stone-600">{{ text.subtitle }}</p>

    <div class="bg-white border border-stone-200 rounded-xl p-6 space-y-4">
      <div>
        <h2 class="text-sm font-semibold text-stone-900">{{ text.supportTitle }}</h2>
        <p class="text-sm text-stone-700">{{ text.supportText }}</p>
      </div>
      <div>
        <h2 class="text-sm font-semibold text-stone-900">{{ text.gdprTitle }}</h2>
        <p class="text-sm text-stone-700">{{ text.gdprText }}</p>
      </div>
      <div>
        <h2 class="text-sm font-semibold text-stone-900">{{ text.responseTitle }}</h2>
        <p class="text-sm text-stone-700">{{ text.responseText }}</p>
      </div>
    </div>

    <p class="text-xs text-stone-500">
      {{ text.note }}
      <NuxtLink :to="localePath('/legal/gdpr')" class="underline">{{ text.gdprLink }}</NuxtLink>
    </p>
  </section>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const { locale } = useI18n()
const isRo = computed(() => locale.value.startsWith('ro'))

const text = computed(() => {
  if (isRo.value) {
    return {
      title: 'Contact',
      subtitle: 'Pentru suport tehnic, întrebări comerciale sau solicitări de protecția datelor, ne poți scrie oricând.',
      supportTitle: 'Suport general',
      supportText: 'Email: support@doisense.app',
      gdprTitle: 'Solicitări GDPR',
      gdprText: 'Email: privacy@doisense.app',
      responseTitle: 'Timp de răspuns',
      responseText: 'Încercăm să răspundem în 1-3 zile lucrătoare, în funcție de complexitatea cererii.',
      note: 'Pentru drepturile tale asupra datelor personale, vezi ',
      gdprLink: 'pagina GDPR.',
    }
  }

  return {
    title: 'Contact',
    subtitle: 'For technical support, commercial questions, or data protection requests, you can contact us anytime.',
    supportTitle: 'General support',
    supportText: 'Email: support@doisense.app',
    gdprTitle: 'GDPR requests',
    gdprText: 'Email: privacy@doisense.app',
    responseTitle: 'Response time',
    responseText: 'We aim to respond in 1-3 business days depending on request complexity.',
    note: 'For your personal data rights, see the ',
    gdprLink: 'GDPR page.',
  }
})
</script>
