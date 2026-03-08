<template>
  <div class="border border-stone-200 rounded-lg bg-white p-4">
    <p class="font-medium text-stone-800 mb-2">{{ question.text }}</p>
    <form v-if="!submitted" @submit.prevent="submit" class="space-y-2">
      <textarea
        v-model="content"
        :placeholder="$t('journal.contentPlaceholder')"
        rows="3"
        class="w-full px-3 py-2 border border-stone-300 rounded-lg"
      />
      <button
        type="submit"
        :disabled="!content.trim() || loading"
        class="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50"
      >
        {{ $t('journal.save') }}
      </button>
    </form>
    <p v-else class="text-green-600 text-sm">{{ $t('journal.saved') }}</p>
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
