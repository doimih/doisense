<template>
  <button
    type="button"
    class="inline-flex items-center justify-center rounded-lg border px-2.5 py-1.5 text-xs font-semibold transition disabled:cursor-not-allowed disabled:opacity-50"
    :class="buttonClass"
    :disabled="disabled || loading"
    @click="$emit('click')"
  >
    <span v-if="loading" class="mr-1.5 inline-block h-3 w-3 animate-spin rounded-full border-2 border-current border-r-transparent" />
    {{ loading ? loadingLabel : label }}
  </button>
</template>

<script setup>
const props = defineProps({
  platform: {
    type: String,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  recommended: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['click'])

const label = computed(() => {
  if (props.platform === 'instagram') return 'Instagram'
  if (props.platform === 'tiktok') return 'TikTok'
  return 'LinkedIn'
})

const loadingLabel = 'Publishing...'

const buttonClass = computed(() => {
  const baseByPlatform = {
    instagram: 'border-[#f3b4c7] bg-[#fff5f8] text-[#a63e63] hover:bg-[#ffe7ef]',
    tiktok: 'border-[#c8d6ff] bg-[#f5f7ff] text-[#334f9d] hover:bg-[#e9eeff]',
    linkedin: 'border-[#b6d8f5] bg-[#f2f9ff] text-[#1d5f94] hover:bg-[#e6f3ff]',
  }

  const highlight = props.recommended ? 'ring-2 ring-offset-1 ring-[#7bb8a0]/45' : ''
  return `${baseByPlatform[props.platform]} ${highlight}`.trim()
})
</script>
