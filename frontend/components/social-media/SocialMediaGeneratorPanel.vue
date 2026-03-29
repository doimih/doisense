<template>
  <section class="rounded-2xl border border-[#d4e4e0] bg-[#fafbfa] p-5 shadow-sm">
    <div class="mb-4 flex items-start justify-between gap-4">
      <div>
        <h2 class="text-lg font-semibold text-[#2c3e35]">Generator Panel</h2>
        <p class="text-sm text-[#5a6b63]">Generate wellness social content and preview it before publishing.</p>
      </div>
      <span class="rounded-full border border-[#c6d9d2] bg-[#f0f4f1] px-3 py-1 text-xs font-semibold text-[#42524b]">
        Wellness-Only
      </span>
    </div>

    <form class="grid gap-3 md:grid-cols-[220px_1fr_auto]" @submit.prevent="onSubmit">
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-[#6e7d76]">Platform</label>
        <select
          v-model="platform"
          class="w-full rounded-lg border border-[#c6d9d2] bg-[#fafbfa] px-3 py-2 text-sm text-[#2c3e35] focus:border-[#7bb8a0] focus:outline-none"
        >
          <option value="instagram">Instagram</option>
          <option value="tiktok" disabled>TikTok (temporarily unavailable)</option>
          <option value="linkedin">LinkedIn</option>
        </select>
      </div>

      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-[#6e7d76]">Topic</label>
        <input
          v-model="topic"
          type="text"
          class="w-full rounded-lg border border-[#c6d9d2] bg-[#fafbfa] px-3 py-2 text-sm text-[#2c3e35] placeholder:text-[#9aa8a2] focus:border-[#7bb8a0] focus:outline-none"
          placeholder="Example: mindful breathing for stress"
        >
      </div>

      <div class="self-end">
        <button
          type="submit"
          class="inline-flex w-full items-center justify-center rounded-lg bg-[#7bb8a0] px-4 py-2 text-sm font-semibold text-white transition hover:bg-[#6aa58d] disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="loading"
        >
          <span v-if="loading" class="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-r-transparent" />
          {{ loading ? 'Generating...' : 'Generate' }}
        </button>
      </div>
    </form>

    <p class="mt-2 text-xs text-[#8a6a2d]">
      TikTok publishing is disabled in UI until a valid video pipeline is available.
    </p>

    <p v-if="error" class="mt-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
      {{ error }}
    </p>

    <div v-if="preview" class="mt-5 rounded-xl border border-[#d4e4e0] bg-[#f9fbfa] p-4">
      <div class="mb-2 flex items-center justify-between gap-2">
        <h3 class="text-base font-semibold text-[#2c3e35]">Preview</h3>
        <span class="rounded-full border border-[#d4e4e0] bg-[#e8f1ed] px-2.5 py-1 text-xs font-semibold text-[#42524b]">
          {{ formatPlatform(preview.platform) }}
        </span>
      </div>

      <div class="space-y-2 text-sm">
        <p><span class="font-semibold text-[#42524b]">Title:</span> <span class="text-[#2c3e35]">{{ preview.title }}</span></p>
        <p class="whitespace-pre-wrap"><span class="font-semibold text-[#42524b]">Body:</span> <span class="text-[#2c3e35]">{{ preview.body }}</span></p>
        <p><span class="font-semibold text-[#42524b]">Hashtags:</span> <span class="text-[#2c3e35]">{{ preview.hashtags }}</span></p>
      </div>

      <div v-if="preview.image_url" class="mt-3">
        <img
          :src="preview.image_url"
          alt="Generated social media visual"
          class="max-h-72 w-full rounded-lg border border-[#d4e4e0] object-cover"
        >
      </div>
    </div>
  </section>
</template>

<script setup>
const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
  preview: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['generate'])

const platform = ref('instagram')
const topic = ref('')

watch(
  () => props.preview,
  (value) => {
    if (!value) return
    platform.value = value.platform
    topic.value = value.wellness_topic || topic.value
  }
)

function onSubmit() {
  emit('generate', { platform: platform.value, topic: topic.value.trim() })
}

function formatPlatform(value) {
  if (value === 'instagram') return 'Instagram'
  if (value === 'tiktok') return 'TikTok'
  if (value === 'linkedin') return 'LinkedIn'
  return value
}
</script>
