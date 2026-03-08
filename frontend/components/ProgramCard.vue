<template>
  <div class="border border-stone-200 rounded-lg bg-white p-4">
    <h2 class="font-semibold text-stone-800">{{ program.title }}</h2>
    <p class="text-sm text-stone-600 mt-1">{{ program.description || $t('programs.noDescription') }}</p>
    <span v-if="program.is_premium" class="inline-block mt-2 text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded">
      {{ $t('programs.premium') }}
    </span>
    <NuxtLink
      :to="localePath(`/programs/${program.id}`)"
      class="mt-3 inline-block text-amber-600 hover:underline text-sm"
    >
      {{ $t('programs.view') }}
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
const { localePath } = useLocalePath()
defineProps<{
  program: { id: number; title: string; description: string; is_premium: boolean }
}>()
</script>
