<template>
  <div class="min-h-screen bg-[#f3f5f8] flex flex-col">
    <Navbar />
    <main class="flex-1 min-h-0 p-3 md:p-4">
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
