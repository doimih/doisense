<template>
  <div class="mx-auto max-w-lg space-y-6 px-4 py-20 text-center sm:px-6">
    <div class="inline-flex items-center justify-center rounded-full border border-emerald-300 bg-emerald-50 p-5 text-emerald-600">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
    <h1 class="text-3xl font-bold text-stone-900">{{ text.title }}</h1>
    <p class="text-base leading-7 text-stone-600">{{ text.subtitle }}</p>
    <p v-if="planLabel" class="inline-flex rounded-full border border-sky-200 bg-sky-50 px-4 py-1.5 text-sm font-semibold text-sky-800">
      {{ text.activatedPlan }}: {{ planLabel }}
    </p>
    <div class="flex flex-col items-center gap-3 pt-2">
      <NuxtLink
        :to="localePath('/chat')"
        class="inline-flex items-center justify-center rounded-full bg-sky-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-sky-700"
      >
        {{ text.ctaChat }}
      </NuxtLink>
      <NuxtLink
        :to="localePath('/profile')"
        class="text-sm font-medium text-stone-600 hover:text-stone-900 hover:underline"
      >
        {{ text.ctaProfile }}
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: ['auth'] })

const localePath = useLocalePath()
const { locale } = useI18n()
const route = useRoute()
const authStore = useAuthStore()
const { fetchApi } = useApi()

const localeCode = computed(() => {
  const code = (locale.value || 'ro').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'ro'
})

const planParam = computed(() => (route.query.plan as string) || '')

const planLabels: Record<string, Record<string, string>> = {
  ro: { basic: 'BASIC Start', premium: 'PREMIUM Flow', vip: 'VIP Executive' },
  en: { basic: 'BASIC Start', premium: 'PREMIUM Flow', vip: 'VIP Executive' },
  de: { basic: 'BASIC Start', premium: 'PREMIUM Flow', vip: 'VIP Executive' },
  fr: { basic: 'BASIC Start', premium: 'PREMIUM Flow', vip: 'VIP Executive' },
  it: { basic: 'BASIC Start', premium: 'PREMIUM Flow', vip: 'VIP Executive' },
  es: { basic: 'BASIC Start', premium: 'PREMIUM Flow', vip: 'VIP Executive' },
  pl: { basic: 'BASIC Start', premium: 'PREMIUM Flow', vip: 'VIP Executive' },
}

const planLabel = computed(() => planLabels[localeCode.value]?.[planParam.value] || '')

const copy: Record<string, { title: string; subtitle: string; activatedPlan: string; ctaChat: string; ctaProfile: string }> = {
  ro: {
    title: 'Abonamentul tău este activ!',
    subtitle: 'Mulțumim pentru abonare. Platforma Doisense este acum complet disponibilă pentru tine.',
    activatedPlan: 'Plan activat',
    ctaChat: 'Deschide chat-ul AI',
    ctaProfile: 'Înapoi la profil',
  },
  en: {
    title: 'Your subscription is active!',
    subtitle: 'Thank you for subscribing. The full Doisense platform is now available to you.',
    activatedPlan: 'Activated plan',
    ctaChat: 'Open AI chat',
    ctaProfile: 'Back to profile',
  },
  de: {
    title: 'Dein Abonnement ist aktiv!',
    subtitle: 'Vielen Dank für dein Abonnement. Die vollständige Doisense-Plattform steht dir jetzt zur Verfügung.',
    activatedPlan: 'Aktivierter Plan',
    ctaChat: 'KI-Chat öffnen',
    ctaProfile: 'Zurück zum Profil',
  },
  fr: {
    title: 'Votre abonnement est actif !',
    subtitle: 'Merci pour votre abonnement. La plateforme Doisense est maintenant entièrement disponible.',
    activatedPlan: 'Plan activé',
    ctaChat: 'Ouvrir le chat IA',
    ctaProfile: 'Retour au profil',
  },
  it: {
    title: 'Il tuo abbonamento è attivo!',
    subtitle: 'Grazie per l\'abbonamento. La piattaforma Doisense è ora completamente disponibile per te.',
    activatedPlan: 'Piano attivato',
    ctaChat: 'Apri la chat AI',
    ctaProfile: 'Torna al profilo',
  },
  es: {
    title: '¡Tu suscripción está activa!',
    subtitle: 'Gracias por suscribirte. La plataforma Doisense está ahora completamente disponible para ti.',
    activatedPlan: 'Plan activado',
    ctaChat: 'Abrir chat IA',
    ctaProfile: 'Volver al perfil',
  },
  pl: {
    title: 'Twoja subskrypcja jest aktywna!',
    subtitle: 'Dziękujemy za subskrypcję. Pełna platforma Doisense jest teraz dostępna dla Ciebie.',
    activatedPlan: 'Aktywowany plan',
    ctaChat: 'Otwórz czat AI',
    ctaProfile: 'Wróć do profilu',
  },
}

const text = computed(() => copy[localeCode.value] || copy.ro)

usePublicSeo({
  title: computed(() => text.value.title + ' - Doisense'),
  description: computed(() => text.value.subtitle),
  noindex: true,
})

// Refresh user data so the updated plan_tier is reflected immediately
onMounted(async () => {
  try {
    const updated = await fetchApi<{ plan_tier: string; is_premium: boolean; membership_tier: string }>('/me')
    if (updated && authStore.user) {
      authStore.setUser({ ...authStore.user, ...updated })
    }
  } catch {
    // Non-critical: user is redirected after login anyway
  }
})
</script>
