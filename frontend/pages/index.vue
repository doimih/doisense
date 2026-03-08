<template>
  <div class="space-y-12 py-8">
    <section class="relative overflow-hidden rounded-2xl border border-stone-200 bg-gradient-to-br from-amber-50 via-white to-stone-50 p-8 md:p-12">
      <div class="absolute -top-10 -right-10 h-48 w-48 rounded-full bg-amber-200/40 blur-2xl" />
      <div class="absolute -bottom-16 -left-10 h-56 w-56 rounded-full bg-stone-300/30 blur-2xl" />
      <div class="relative max-w-3xl">
        <p class="inline-block rounded-full bg-stone-900 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
          {{ text.heroBadge }}
        </p>
        <h1 class="mt-4 text-4xl md:text-5xl font-bold text-stone-900 leading-tight">{{ text.heroTitle }}</h1>
        <p class="mt-4 text-stone-700 text-lg">{{ text.heroSubtitle }}</p>
        <div class="mt-6 flex flex-wrap gap-3">
          <NuxtLink
            v-if="!authStore.isLoggedIn"
            :to="localePath('/auth/register')"
            class="px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700"
          >
            {{ text.primaryCta }}
          </NuxtLink>
          <NuxtLink
            v-if="!authStore.isLoggedIn"
            :to="localePath('/auth/login')"
            class="px-6 py-3 border border-stone-300 rounded-lg hover:bg-stone-100"
          >
            {{ $t('auth.login') }}
          </NuxtLink>
          <NuxtLink
            v-if="authStore.isLoggedIn"
            :to="localePath('/chat')"
            class="px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700"
          >
            {{ $t('nav.chat') }}
          </NuxtLink>
          <NuxtLink
            :to="localePath('/features')"
            class="px-6 py-3 border border-stone-300 rounded-lg hover:bg-stone-100"
          >
            {{ text.secondaryCta }}
          </NuxtLink>
        </div>
      </div>
    </section>

    <section class="grid gap-4 md:grid-cols-3">
      <article v-for="card in text.cards" :key="card.title" class="bg-white border border-stone-200 rounded-xl p-5">
        <h2 class="font-semibold text-stone-900 mb-2">{{ card.title }}</h2>
        <p class="text-sm text-stone-600">{{ card.description }}</p>
      </article>
    </section>

    <section class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <NuxtLink
        v-for="link in text.quickLinks"
        :key="link.to"
        :to="localePath(link.to)"
        class="bg-white border border-stone-200 rounded-xl p-4 hover:bg-stone-50 transition"
      >
        <h3 class="font-semibold text-stone-900">{{ link.title }}</h3>
        <p class="text-sm text-stone-600 mt-1">{{ link.description }}</p>
      </NuxtLink>
    </section>

    <section class="bg-stone-900 text-white rounded-2xl p-6 md:p-8">
      <h2 class="text-2xl font-semibold">{{ text.gdprTitle }}</h2>
      <p class="text-stone-200 mt-2">{{ text.gdprSubtitle }}</p>
      <div class="mt-5 flex flex-wrap gap-3">
        <NuxtLink :to="localePath('/legal/privacy')" class="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20">{{ text.privacy }}</NuxtLink>
        <NuxtLink :to="localePath('/legal/terms')" class="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20">{{ text.terms }}</NuxtLink>
        <NuxtLink :to="localePath('/legal/cookies')" class="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20">{{ text.cookies }}</NuxtLink>
        <NuxtLink :to="localePath('/legal/gdpr')" class="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-700">{{ text.gdprRights }}</NuxtLink>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const authStore = useAuthStore()
const { locale } = useI18n()

const isRo = computed(() => locale.value.startsWith('ro'))

const text = computed(() => {
  if (isRo.value) {
    return {
      heroBadge: 'Wellbeing + AI + GDPR',
      heroTitle: 'Prima platformă ta pentru wellbeing digital, construită responsabil',
      heroSubtitle: 'Doisense îți oferă jurnal ghidat, chat AI contextual și programe structurate, cu pagini legale complete și control asupra datelor.',
      primaryCta: 'Creează cont',
      secondaryCta: 'Vezi funcționalitățile',
      cards: [
        { title: 'Experiență ghidată', description: 'Flux clar de la onboarding la progres zilnic.' },
        { title: 'Design pentru încredere', description: 'Informații explicite despre date, securitate și drepturi.' },
        { title: 'Scalabil pentru produs', description: 'Pagini publice importante gata pentru creștere.' },
      ],
      quickLinks: [
        { to: '/features', title: 'Features', description: 'Tot ce poate face platforma.' },
        { to: '/pricing', title: 'Pricing', description: 'Planuri free și premium.' },
        { to: '/about', title: 'About', description: 'Misiune, valori și context produs.' },
        { to: '/contact', title: 'Contact', description: 'Suport și canale de comunicare.' },
      ],
      gdprTitle: 'GDPR în tot sistemul',
      gdprSubtitle: 'Am inclus pagini dedicate pentru confidențialitate, termeni, cookie-uri și drepturile utilizatorului.',
      privacy: 'Privacy Policy',
      terms: 'Terms',
      cookies: 'Cookies',
      gdprRights: 'GDPR Rights',
    }
  }

  return {
    heroBadge: 'Wellbeing + AI + GDPR',
    heroTitle: 'Your digital wellbeing platform, built responsibly',
    heroSubtitle: 'Doisense provides guided journaling, contextual AI chat, and structured programs with complete legal pages and user data control.',
    primaryCta: 'Create account',
    secondaryCta: 'Explore features',
    cards: [
      { title: 'Guided experience', description: 'Clear flow from onboarding to daily progress.' },
      { title: 'Trust-focused design', description: 'Explicit data, security, and rights information.' },
      { title: 'Product-ready scale', description: 'Public key pages ready for growth.' },
    ],
    quickLinks: [
      { to: '/features', title: 'Features', description: 'What the platform can do.' },
      { to: '/pricing', title: 'Pricing', description: 'Free and premium plans.' },
      { to: '/about', title: 'About', description: 'Mission, values, and product context.' },
      { to: '/contact', title: 'Contact', description: 'Support and communication channels.' },
    ],
    gdprTitle: 'GDPR across the system',
    gdprSubtitle: 'Dedicated pages for privacy, terms, cookies, and user rights are now included.',
    privacy: 'Privacy Policy',
    terms: 'Terms',
    cookies: 'Cookies',
    gdprRights: 'GDPR Rights',
  }
})
</script>
