<template>
  <div class="space-y-4">
    <h1 class="text-3xl font-bold text-stone-900">{{ $t('nav.chat') }}</h1>
    <ChatWindow />
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

usePublicSeo({
  title: 'Chat - Doisense',
  description: 'Chat AI contextual pentru utilizatori autentificati.',
  noindex: true,
})
</script>
