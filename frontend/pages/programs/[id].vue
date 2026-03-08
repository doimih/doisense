<template>
  <div class="max-w-2xl mx-auto">
    <NuxtLink :to="localePath('/programs')" class="text-amber-600 hover:underline mb-4 inline-block">
      {{ $t('common.back') }}
    </NuxtLink>
    <p v-if="loading" class="text-stone-500">{{ $t('common.loading') }}</p>
    <div v-else-if="day">
      <h1 class="text-2xl font-bold text-stone-800">{{ day.title }}</h1>
      <p class="text-stone-600 mt-2 whitespace-pre-wrap">{{ day.content }}</p>
      <p v-if="day.question" class="mt-4 font-medium text-stone-700">{{ day.question }}</p>
    </div>
    <p v-else class="text-red-600">{{ $t('programs.notFound') }}</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const route = useRoute()
const { fetchApi } = useApi()

const day = ref<{ title: string; content: string; question: string } | null>(null)
const loading = ref(true)

onMounted(async () => {
  const id = route.params.id as string
  try {
    day.value = await fetchApi<typeof day.value>(`/programs/${id}/days/1`)
  } catch {
    day.value = null
  } finally {
    loading.value = false
  }
})
</script>
