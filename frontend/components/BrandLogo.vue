<template>
  <span
    class="brand-logo inline-flex flex-col"
    :class="[
      centered ? 'items-center text-center' : 'items-start',
      sizeClasses.wrapper,
    ]"
    aria-label="doisense"
  >
    <span class="brand-word inline-flex items-baseline" :class="sizeClasses.word">
      <span :class="isDark ? 'text-white' : 'text-stone-900'">doi</span>
      <span style="color: #c4a882;">sense</span>
    </span>
    <span
      v-if="showTagline"
      class="brand-tagline mt-1 uppercase"
      :class="[sizeClasses.tagline, isDark ? 'text-white/80' : 'text-stone-500']"
    >
      wellbeing
    </span>
  </span>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  isDark?: boolean
  showTagline?: boolean
  centered?: boolean
  size?: 'sm' | 'md' | 'lg'
}>(), {
  isDark: false,
  showTagline: false,
  centered: false,
  size: 'md',
})

const sizeClasses = computed(() => {
  if (props.size === 'sm') {
    return {
      wrapper: 'leading-none',
      word: 'text-[1.95rem]',
      tagline: 'text-[0.42rem] tracking-[0.42em]',
    }
  }
  if (props.size === 'lg') {
    return {
      wrapper: 'leading-none',
      word: 'text-[3.2rem]',
      tagline: 'text-[0.64rem] tracking-[0.6em]',
    }
  }
  return {
    wrapper: 'leading-none',
    word: 'text-[2.55rem]',
    tagline: 'text-[0.55rem] tracking-[0.52em]',
  }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,500&display=swap');

.brand-logo {
  font-family: 'Cormorant Garamond', serif;
}

.brand-word {
  letter-spacing: 0.2em;
  text-transform: lowercase;
  line-height: 0.92;
}

.brand-word span:last-child {
  font-style: italic;
  margin-left: 0.22em;
}

.brand-tagline {
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif;
  letter-spacing: 0.52em;
}
</style>