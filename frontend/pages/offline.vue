<template>
  <section class="min-h-screen bg-[radial-gradient(circle_at_top_right,_#d8f3f0_0%,_#f3f5f8_42%,_#edf1f6_100%)] px-4 py-16 text-slate-800">
    <div class="mx-auto w-full max-w-xl rounded-[20px] border border-slate-300 bg-white/90 p-8 shadow-[0_18px_40px_rgba(15,23,42,0.08)] backdrop-blur-sm">
      <BrandLogo size="md" centered class="mb-6" />
      <h1 class="mb-3 text-2xl font-semibold text-slate-900">You are offline</h1>
      <p class="mb-6 leading-7 text-slate-700">
        Doisense cannot reach the network right now. You can retry when your connection is restored.
      </p>
      <div class="flex flex-wrap gap-3">
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-xl bg-slate-200 px-4 py-3 font-semibold text-slate-800 transition hover:bg-slate-300"
          @click="retryNow"
        >
          Retry now
        </button>
        <NuxtLink
          to="/"
          class="inline-flex items-center justify-center rounded-xl bg-teal-700 px-4 py-3 font-semibold text-white transition hover:bg-teal-800"
        >
          Return to Doisense
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const router = useRouter()

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
  title: 'Offline - Doisense',
  description: 'Offline fallback page for Doisense.',
  noindex: true,
})
</script>