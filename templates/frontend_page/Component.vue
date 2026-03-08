<template>
  <div class="border rounded-lg p-4">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
}>()
const emit = defineEmits<{
  submit: [value: string]
}>()
</script>
