<template>
  <section class="max-w-6xl mx-auto py-10 space-y-8">
    <header class="text-center space-y-3">
      <h1 class="text-4xl font-bold text-stone-900">{{ text.title }}</h1>
      <p class="text-stone-600 max-w-2xl mx-auto">{{ text.subtitle }}</p>
    </header>

    <div class="grid gap-4 md:grid-cols-2">
      <article class="bg-white border border-stone-200 rounded-xl p-6">
        <h2 class="text-2xl font-semibold text-stone-900">{{ text.freeTitle }}</h2>
        <p class="text-stone-500 text-sm mb-4">{{ text.freePrice }}</p>
        <ul class="space-y-2 text-sm text-stone-700">
          <li v-for="item in text.freeItems" :key="item">• {{ item }}</li>
        </ul>
      </article>

      <article class="bg-stone-900 text-white rounded-xl p-6">
        <h2 class="text-2xl font-semibold">{{ text.premiumTitle }}</h2>
        <p class="text-stone-200 text-sm mb-4">{{ text.premiumPrice }}</p>
        <ul class="space-y-2 text-sm">
          <li v-for="item in text.premiumItems" :key="item">• {{ item }}</li>
        </ul>
      </article>
    </div>

    <p class="text-xs text-stone-500 bg-stone-100 border border-stone-200 rounded-lg p-3">
      {{ text.notice }}
    </p>
  </section>
</template>

<script setup lang="ts">
const { locale } = useI18n()
const isRo = computed(() => locale.value.startsWith('ro'))

const text = computed(() => {
  if (isRo.value) {
    return {
      title: 'Planuri și prețuri',
      subtitle: 'Începe gratuit și treci la Premium când vrei funcții avansate și programe complete.',
      freeTitle: 'Free',
      freePrice: '0 EUR / lună',
      freeItems: [
        'Acces la jurnal de bază',
        'Chat AI standard',
        'Profil personal de bază',
      ],
      premiumTitle: 'Premium',
      premiumPrice: 'Conform Stripe checkout',
      premiumItems: [
        'Programe ghidate extinse',
        'Personalizare avansată AI',
        'Prioritate la noi funcționalități',
      ],
      notice: 'Plățile sunt procesate prin Stripe. Vei vedea prețul final în checkout înainte de confirmare.',
    }
  }

  return {
    title: 'Plans and pricing',
    subtitle: 'Start for free and upgrade to Premium when you need advanced features and full programs.',
    freeTitle: 'Free',
    freePrice: '0 EUR / month',
    freeItems: ['Basic journaling access', 'Standard AI chat', 'Basic personal profile'],
    premiumTitle: 'Premium',
    premiumPrice: 'As shown in Stripe checkout',
    premiumItems: ['Extended guided programs', 'Advanced AI personalization', 'Priority access to new features'],
    notice: 'Payments are processed via Stripe. You will see final pricing in checkout before confirmation.',
  }
})
</script>
