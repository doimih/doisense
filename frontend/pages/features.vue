<template>
  <section class="max-w-6xl mx-auto py-10 space-y-10">
    <header class="space-y-4 text-center">
      <p class="inline-block px-3 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-semibold tracking-wide">
        {{ text.badge }}
      </p>
      <h1 class="text-4xl md:text-5xl font-bold text-stone-900">{{ text.title }}</h1>
      <p class="text-stone-600 max-w-3xl mx-auto">{{ text.subtitle }}</p>
    </header>

    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="feature in text.featureCards"
        :key="feature.title"
        class="bg-white border border-stone-200 rounded-xl p-5 shadow-sm"
      >
        <h2 class="text-lg font-semibold text-stone-900 mb-2">{{ feature.title }}</h2>
        <p class="text-stone-600 text-sm">{{ feature.description }}</p>
      </article>
    </div>

    <section class="bg-white border border-stone-200 rounded-xl p-6">
      <h2 class="text-2xl font-semibold text-stone-900 mb-4">{{ text.gdprTitle }}</h2>
      <ul class="grid gap-3 md:grid-cols-2">
        <li
          v-for="item in text.gdprItems"
          :key="item"
          class="text-stone-700 text-sm bg-stone-50 border border-stone-200 rounded-lg px-4 py-3"
        >
          {{ item }}
        </li>
      </ul>
      <div class="mt-5">
        <NuxtLink
          :to="localePath('/legal/gdpr')"
          class="inline-block px-4 py-2 rounded-lg bg-stone-900 text-white hover:bg-black"
        >
          {{ text.gdprAction }}
        </NuxtLink>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const { locale } = useI18n()

const isRo = computed(() => locale.value.startsWith('ro'))

const text = computed(() => {
  if (isRo.value) {
    return {
      badge: 'Platformă completă',
      title: 'Funcționalități gândite pentru wellbeing real',
      subtitle: 'Doisense combină jurnalul ghidat, conversațiile AI și planurile de progres într-o singură experiență.',
      featureCards: [
        { title: 'Jurnal ghidat zilnic', description: 'Întrebări dinamice și salvare rapidă pentru obiceiuri sănătoase de reflecție.' },
        { title: 'Chat AI contextual', description: 'Asistentul folosește istoricul tău pentru răspunsuri mai relevante și mai empatice.' },
        { title: 'Programe structurate', description: 'Planuri pe zile și pași mici, urmărite direct în contul tău.' },
        { title: 'Profil personal adaptiv', description: 'Preferințele și tonul conversației se ajustează pe baza datelor tale.' },
        { title: 'Flux premium simplu', description: 'Upgrade rapid și transparent pentru funcțiile avansate.' },
        { title: 'Arhitectură scalabilă', description: 'Frontend Nuxt, backend Django, PostgreSQL și Redis pentru stabilitate.' },
      ],
      gdprTitle: 'Conformitate GDPR în produs',
      gdprItems: [
        'Transparență: vezi ce date colectăm și de ce.',
        'Control: poți solicita acces, rectificare sau ștergere.',
        'Minimizare: păstrăm doar datele necesare funcționalităților.',
        'Securitate: separare pe servicii și bune practici de deployment.',
      ],
      gdprAction: 'Vezi pagina GDPR',
    }
  }

  return {
    badge: 'All-in-one platform',
    title: 'Features designed for practical wellbeing',
    subtitle: 'Doisense combines guided journaling, AI conversations, and progress plans in one coherent flow.',
    featureCards: [
      { title: 'Daily guided journal', description: 'Dynamic prompts and fast saving for consistent reflection habits.' },
      { title: 'Context-aware AI chat', description: 'The assistant uses your context for more relevant and empathetic responses.' },
      { title: 'Structured programs', description: 'Day-by-day plans with practical actions tracked in your account.' },
      { title: 'Adaptive personal profile', description: 'Tone and preferences evolve based on your activity and feedback.' },
      { title: 'Simple premium flow', description: 'Transparent upgrade path for advanced features.' },
      { title: 'Scalable architecture', description: 'Nuxt frontend, Django backend, PostgreSQL and Redis for reliability.' },
    ],
    gdprTitle: 'GDPR built into the product',
    gdprItems: [
      'Transparency: clearly understand what data we collect and why.',
      'Control: request access, rectification, or deletion.',
      'Minimization: we store only data needed for core features.',
      'Security: service separation and deployment best practices.',
    ],
    gdprAction: 'Read the GDPR page',
  }
})
</script>
