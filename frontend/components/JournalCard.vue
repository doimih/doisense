<template>
  <div class="border border-slate-200 rounded-lg bg-white p-5 shadow-sm hover:shadow-md transition-shadow h-full flex flex-col">
    <!-- Question Text -->
    <p class="font-medium text-slate-900 mb-4 text-sm leading-relaxed flex-shrink-0">{{ question.text }}</p>

    <!-- Form or Success Message -->
    <form v-if="!submitted" @submit.prevent="submit" class="space-y-3 flex flex-col flex-grow">
      <textarea
        v-model="content"
        :placeholder="$t('journal.contentPlaceholder') || 'Your thoughts...'"
        rows="4"
        class="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent resize-none flex-grow"
      />
      <button
        type="submit"
        :disabled="!content.trim() || loading"
        class="w-full px-4 py-2 bg-teal-600 text-white font-medium rounded-lg hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
      >
        <span v-if="loading">{{ $t('journal.saving') || 'Saving...' }}</span>
        <span v-else>{{ $t('journal.save') || 'Save' }}</span>
      </button>
    </form>

    <!-- Success State -->
    <div v-else class="bg-teal-50 border border-teal-200 rounded-lg p-3 flex items-center gap-2 flex-shrink-0">
      <svg class="w-5 h-5 text-teal-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      <span class="text-teal-700 text-sm font-medium">{{ $t('journal.saved') || 'Saved!' }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  question: { id: number; text: string; category: string }
}>()

const emit = defineEmits<{ submitted: [] }>()

const { fetchApi } = useApi()
const content = ref('')
const submitted = ref(false)
const loading = ref(false)

async function submit() {
  if (!content.value.trim() || loading.value) return
  loading.value = true
  try {
    await fetchApi('/journal/entries', {
      method: 'POST',
      body: { question: props.question.id, content: content.value.trim(), emotions: [] },
    })
    submitted.value = true
    emit('submitted')
  } finally {
    loading.value = false
  }
}
</script>
