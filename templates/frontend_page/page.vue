<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-stone-800 mb-4">{{ $t('section.key') }}</h1>
    <p class="text-stone-600">{{ $t('section.description') }}</p>
    <!-- fetch API, layout standard -->
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' }) // optional
const { fetchApi } = useApi()
const data = ref<unknown>(null)
onMounted(async () => {
  // data.value = await fetchApi('/your-endpoint')
})
</script>
