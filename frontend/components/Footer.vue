<template>
  <footer class="border-t border-stone-200 py-8 mt-auto bg-white">
    <div class="container mx-auto px-4 space-y-6">
      <div class="grid gap-6 md:grid-cols-3 text-sm">
        <div>
          <h3 class="font-semibold text-stone-900 mb-2">Doisense</h3>
          <p class="text-stone-600">{{ text.summary }}</p>
        </div>
        <div>
          <h3 class="font-semibold text-stone-900 mb-2">{{ text.product }}</h3>
          <ul class="space-y-1">
            <li><NuxtLink :to="localePath('/features')" class="text-stone-600 hover:text-stone-900">Features</NuxtLink></li>
            <li><NuxtLink :to="localePath('/pricing')" class="text-stone-600 hover:text-stone-900">Pricing</NuxtLink></li>
            <li><NuxtLink :to="localePath('/about')" class="text-stone-600 hover:text-stone-900">About</NuxtLink></li>
            <li><NuxtLink :to="localePath('/contact')" class="text-stone-600 hover:text-stone-900">Contact</NuxtLink></li>
          </ul>
        </div>
        <div>
          <h3 class="font-semibold text-stone-900 mb-2">{{ text.legal }}</h3>
          <ul class="space-y-1">
            <li><NuxtLink :to="localePath('/legal/privacy')" class="text-stone-600 hover:text-stone-900">Privacy Policy</NuxtLink></li>
            <li><NuxtLink :to="localePath('/legal/terms')" class="text-stone-600 hover:text-stone-900">Terms</NuxtLink></li>
            <li><NuxtLink :to="localePath('/legal/cookies')" class="text-stone-600 hover:text-stone-900">Cookies</NuxtLink></li>
            <li><NuxtLink :to="localePath('/legal/gdpr')" class="text-stone-600 hover:text-stone-900">GDPR Rights</NuxtLink></li>
          </ul>
        </div>
      </div>
      <div class="text-center text-stone-500 text-sm">
        {{ $t('footer.copyright') }}
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const { locale } = useI18n()

const isRo = computed(() => locale.value.startsWith('ro'))

const text = computed(() => {
  if (isRo.value) {
    return {
      summary: 'Platformă de wellbeing cu jurnal, chat AI, programe și conformitate GDPR.',
      product: 'Produs',
      legal: 'Legal',
    }
  }

  return {
    summary: 'Wellbeing platform with journaling, AI chat, programs, and GDPR compliance.',
    product: 'Product',
    legal: 'Legal',
  }
})
</script>
