<template>
  <div class="min-h-screen flex flex-col bg-stone-50">
    <Navbar />
    <main class="flex-1 container mx-auto px-4 py-6">
      <slot />
    </main>
    <Footer />
    <GdprConsentModal />
  </div>
</template>

<script setup lang="ts">
</script>
