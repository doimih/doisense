<template>
  <button
    type="button"
    class="fixed bottom-4 right-4 z-[110] inline-flex items-center gap-2 rounded-full border border-amber-300 bg-amber-500 px-4 py-2 text-xs font-semibold text-black shadow-lg transition hover:bg-amber-400"
    @click="openModal"
  >
    <span class="text-sm">⚙</span>
    <span>{{ $t('footer.gdpr') }}</span>
  </button>
</template>

<script setup lang="ts">
const { openModal } = useGdprConsent()
</script>
