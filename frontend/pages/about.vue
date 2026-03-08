<template>
  <section class="max-w-4xl mx-auto py-10 space-y-6">
    <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
    <p class="text-stone-700 leading-7">{{ text.p1 }}</p>
    <p class="text-stone-700 leading-7">{{ text.p2 }}</p>
    <p class="text-stone-700 leading-7">{{ text.p3 }}</p>

    <div class="grid gap-4 md:grid-cols-3">
      <article v-for="item in text.values" :key="item.title" class="bg-white border border-stone-200 rounded-xl p-4">
        <h2 class="font-semibold text-stone-900 mb-2">{{ item.title }}</h2>
        <p class="text-sm text-stone-600">{{ item.description }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const isRo = computed(() => locale.value.startsWith('ro'))

const text = computed(() => {
  if (isRo.value) {
    return {
      title: 'Despre Doisense',
      p1: 'Doisense este o platformă digitală pentru wellbeing care combină reflecția personală, suportul conversațional AI și programe ghidate într-o experiență simplă.',
      p2: 'Scopul produsului este să ajute oamenii să își construiască rutine emoționale sănătoase și să observe progresul în timp, fără fricțiune tehnică.',
      p3: 'Construim responsabil: transparență pe date, control pentru utilizator și o arhitectură care poate evolua în siguranță.',
      values: [
        { title: 'Empatie', description: 'Interacțiuni prietenoase și suportive, fără ton rigid.' },
        { title: 'Claritate', description: 'Interfață simplă, pași expliciți și informații ușor de înțeles.' },
        { title: 'Responsabilitate', description: 'Respect pentru confidențialitate, securitate și conformitate GDPR.' },
      ],
    }
  }

  return {
    title: 'About Doisense',
    p1: 'Doisense is a digital wellbeing platform combining personal reflection, AI conversational support, and guided programs into one simple experience.',
    p2: 'The product helps people build healthier emotional routines and track progress over time without technical friction.',
    p3: 'We build responsibly: data transparency, user control, and architecture designed for safe evolution.',
    values: [
      { title: 'Empathy', description: 'Supportive interactions without a robotic tone.' },
      { title: 'Clarity', description: 'Simple interface, explicit steps, and understandable information.' },
      { title: 'Responsibility', description: 'Respect for privacy, security, and GDPR compliance.' },
    ],
  }
})
</script>
