<template>
  <div class="max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold text-stone-800 mb-4">{{ $t('nav.chat') }}</h1>
    <ChatWindow />
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })
</script>
