<template>
  <section class="min-h-screen bg-[radial-gradient(circle_at_top_right,_#d8f3f0_0%,_#f3f5f8_42%,_#edf1f6_100%)] px-4 py-16 text-slate-800">
    <div class="mx-auto w-full max-w-xl rounded-[20px] border border-slate-300 bg-white/90 p-8 shadow-[0_18px_40px_rgba(15,23,42,0.08)] backdrop-blur-sm">
      <BrandLogo size="md" centered class="mb-6" />
      <h1 class="mb-3 text-2xl font-semibold text-slate-900">{{ text.title }}</h1>
      <p class="mb-6 leading-7 text-slate-700">
        {{ text.subtitle }}
      </p>
      <div class="flex flex-wrap gap-3">
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-xl bg-slate-200 px-4 py-3 font-semibold text-slate-800 transition hover:bg-slate-300"
          @click="retryNow"
        >
          {{ text.retryNow }}
        </button>
        <NuxtLink
          :to="localePath('/')"
          class="inline-flex items-center justify-center rounded-xl bg-teal-700 px-4 py-3 font-semibold text-white transition hover:bg-teal-800"
        >
          {{ text.returnHome }}
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const router = useRouter()
const localePath = useLocalePath()
const { locale } = useI18n()

const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

const copy: Record<string, { title: string; subtitle: string; retryNow: string; returnHome: string; seoTitle: string; seoDescription: string }> = {
  ro: {
    title: 'Esti offline',
    subtitle: 'Doisense nu poate accesa reteaua acum. Poti reincerca atunci cand conexiunea revine.',
    retryNow: 'Reincearca acum',
    returnHome: 'Inapoi la Doisense',
    seoTitle: 'Offline - Doisense',
    seoDescription: 'Pagina offline pentru Doisense.',
  },
  en: {
    title: 'You are offline',
    subtitle: 'Doisense cannot reach the network right now. You can retry when your connection is restored.',
    retryNow: 'Retry now',
    returnHome: 'Return to Doisense',
    seoTitle: 'Offline - Doisense',
    seoDescription: 'Offline fallback page for Doisense.',
  },
  de: {
    title: 'Du bist offline',
    subtitle: 'Doisense kann das Netzwerk derzeit nicht erreichen. Du kannst es erneut versuchen, sobald die Verbindung wiederhergestellt ist.',
    retryNow: 'Jetzt erneut versuchen',
    returnHome: 'Zurueck zu Doisense',
    seoTitle: 'Offline - Doisense',
    seoDescription: 'Offline-Seite fuer Doisense.',
  },
  fr: {
    title: 'Vous etes hors ligne',
    subtitle: 'Doisense ne peut pas atteindre le reseau pour le moment. Vous pouvez reessayer lorsque la connexion est retablie.',
    retryNow: 'Reessayer maintenant',
    returnHome: 'Retour a Doisense',
    seoTitle: 'Hors ligne - Doisense',
    seoDescription: 'Page hors ligne pour Doisense.',
  },
  it: {
    title: 'Sei offline',
    subtitle: 'Doisense non riesce a raggiungere la rete in questo momento. Riprova quando la connessione torna disponibile.',
    retryNow: 'Riprova ora',
    returnHome: 'Torna a Doisense',
    seoTitle: 'Offline - Doisense',
    seoDescription: 'Pagina offline per Doisense.',
  },
  es: {
    title: 'Estas sin conexion',
    subtitle: 'Doisense no puede acceder a la red en este momento. Puedes volver a intentarlo cuando se restablezca la conexion.',
    retryNow: 'Reintentar ahora',
    returnHome: 'Volver a Doisense',
    seoTitle: 'Sin conexion - Doisense',
    seoDescription: 'Pagina offline para Doisense.',
  },
  pl: {
    title: 'Jestes offline',
    subtitle: 'Doisense nie moze teraz polaczyc sie z siecia. Sprobuj ponownie, gdy polaczenie zostanie przywrocone.',
    retryNow: 'Sprobuj ponownie',
    returnHome: 'Powrot do Doisense',
    seoTitle: 'Offline - Doisense',
    seoDescription: 'Strona offline dla Doisense.',
  },
}

const text = computed(() => copy[localeCode.value] || copy.en)

async function clearServiceWorkers() {
  if (!import.meta.client || !('serviceWorker' in navigator)) {
    return
  }

  const registrations = await navigator.serviceWorker.getRegistrations()
  await Promise.all(registrations.map((registration) => registration.unregister()))

  if ('caches' in window) {
    const cacheKeys = await caches.keys()
    await Promise.all(cacheKeys.map((key) => caches.delete(key)))
  }
}

async function retryNow() {
  if (!import.meta.client) {
    return
  }

  if (!navigator.onLine) {
    window.location.reload()
    return
  }

  await clearServiceWorkers()
  await router.replace('/')
  window.location.reload()
}

onMounted(async () => {
  if (!import.meta.client || !navigator.onLine) {
    return
  }

  await clearServiceWorkers()
  await router.replace('/')
})

usePublicSeo({
  title: computed(() => text.value.seoTitle),
  description: computed(() => text.value.seoDescription),
  noindex: true,
})
</script>