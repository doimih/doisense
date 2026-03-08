<template>
  <div :class="isUser ? 'text-right' : 'text-left'">
    <span
      :class="[
        'inline-block max-w-[85%] px-4 py-2 rounded-lg',
        isUser ? 'bg-amber-600 text-white' : 'bg-stone-200 text-stone-800'
      ]"
    >
      {{ message }}
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  message: string
  isUser: boolean
}>()
</script>
