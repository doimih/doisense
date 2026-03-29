<template>
  <div class="site-shell min-h-screen flex flex-col">
    <Navbar />
    <main class="site-main flex-1 container mx-auto px-4 py-6">
      <slot />
    </main>
    <Footer />
    <ClientOnly>
      <LazyGdprFloatingButton />
      <LazyGdprConsentModal />
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.site-shell {
  background:
    radial-gradient(ellipse 65% 50% at 8% 14%, rgba(168, 213, 186, 0.16) 0%, transparent 62%),
    radial-gradient(ellipse 54% 44% at 92% 86%, rgba(212, 228, 224, 0.22) 0%, transparent 65%),
    linear-gradient(135deg, #fafbfa 0%, #f4f8f6 48%, #eef4f1 100%);
}

.site-main {
  max-width: 1400px;
  width: 100%;
}
</style>
