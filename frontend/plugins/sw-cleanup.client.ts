export default defineNuxtPlugin(() => {
  if (!('serviceWorker' in navigator)) {
    return
  }

  // Cleanup is opt-in and should only run when explicitly enabled.
  const shouldCleanup = localStorage.getItem('doisense_sw_cleanup') === '1'
    || new URLSearchParams(window.location.search).get('sw_cleanup') === '1'
  if (!shouldCleanup) {
    return
  }

  localStorage.removeItem('doisense_sw_cleanup')

  // Recovery guard for clients stuck on stale Workbox configurations.
  window.addEventListener('load', async () => {
    try {
      const registrations = await navigator.serviceWorker.getRegistrations()
      await Promise.all(registrations.map((registration) => registration.unregister()))

      if ('caches' in window) {
        const keys = await caches.keys()
        await Promise.all(keys.map((key) => caches.delete(key)))
      }
    } catch {
      // Ignore cleanup errors; app navigation should proceed regardless.
    }
  })
})
