<template>
  <footer class="mt-auto bg-slate-900 text-slate-300 border-t border-slate-800">
    <!-- Main Footer Content -->
    <div class="container mx-auto px-4 py-16">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-12">
        <!-- Brand Section -->
        <div class="lg:col-span-1">
          <NuxtLink :to="localePath('/')" class="mb-5 block">
            <BrandLogo size="md" :is-dark="true" show-tagline />
          </NuxtLink>
          <p class="text-sm leading-6 text-slate-400 mb-6 max-w-xs">
            {{ $t('footer.brandDescription') }}
          </p>

          <!-- Contact Info -->
          <div class="space-y-3 text-sm">
            <div v-if="$t('footer.whatsapp')" class="flex flex-col">
              <span class="text-slate-500 text-xs uppercase tracking-wide">WhatsApp</span>
              <a href="tel:+40749000000" class="text-white hover:text-slate-200">+40 749 000 000</a>
            </div>
            <div v-if="$t('footer.email')" class="flex flex-col">
              <span class="text-slate-500 text-xs uppercase tracking-wide">Email</span>
              <a href="mailto:hello@doisense.com" class="text-white hover:text-slate-200">hello@doisense.com</a>
            </div>
          </div>
        </div>

        <!-- About Us -->
        <div>
          <h3 class="mb-4 text-sm font-semibold text-white uppercase tracking-wide">{{ $t('footer.aboutUs') || 'About Us' }}</h3>
          <ul class="space-y-2 text-sm">
            <li><NuxtLink :to="localePath('/about')" class="text-slate-400 hover:text-white transition">{{ $t('nav.about') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/features')" class="text-slate-400 hover:text-white transition">{{ $t('nav.features') }}</NuxtLink></li>
            <li v-if="false"><a href="#" class="text-slate-400 hover:text-white transition">{{ $t('footer.team') || 'Team' }}</a></li>
            <li v-if="false"><a href="#" class="text-slate-400 hover:text-white transition">{{ $t('footer.mission') || 'Mission & Values' }}</a></li>
            <li v-if="false"><a href="#" class="text-slate-400 hover:text-white transition">{{ $t('footer.careers') || 'Careers' }}</a></li>
          </ul>
        </div>

        <!-- Services -->
        <div>
          <h3 class="mb-4 text-sm font-semibold text-white uppercase tracking-wide">{{ $t('footer.services') || 'Services' }}</h3>
          <ul class="space-y-2 text-sm">
            <li><NuxtLink :to="localePath('/chat')" class="text-slate-400 hover:text-white transition">{{ $t('nav.chat') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/journal')" class="text-slate-400 hover:text-white transition">{{ $t('nav.journal') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/programs')" class="text-slate-400 hover:text-white transition">{{ $t('nav.programs') }}</NuxtLink></li>
            <li v-if="false"><a href="#" class="text-slate-400 hover:text-white transition">{{ $t('footer.coaching') || 'Coaching' }}</a></li>
            <li v-if="false"><a href="#" class="text-slate-400 hover:text-white transition">{{ $t('footer.wellness') || 'Wellness Programs' }}</a></li>
          </ul>
        </div>

        <!-- Resources -->
        <div>
          <h3 class="mb-4 text-sm font-semibold text-white uppercase tracking-wide">{{ $t('footer.resources') || 'Resources' }}</h3>
          <ul class="space-y-2 text-sm">
            <li><NuxtLink :to="localePath('/contact')" class="text-slate-400 hover:text-white transition">{{ $t('footer.helpCenter') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/faq')" class="text-slate-400 hover:text-white transition">FAQ</NuxtLink></li>
            <li v-if="false"><a href="#" class="text-slate-400 hover:text-white transition">{{ $t('footer.blog') || 'Blog' }}</a></li>
            <li v-if="false"><a href="#" class="text-slate-400 hover:text-white transition">{{ $t('footer.documentation') || 'Documentation' }}</a></li>
          </ul>
        </div>

        <!-- Company -->
        <div>
          <h3 class="mb-4 text-sm font-semibold text-white uppercase tracking-wide">{{ $t('footer.company') || 'Company' }}</h3>
          <ul class="space-y-2 text-sm">
            <li><NuxtLink :to="localePath('/legal/privacy')" class="text-slate-400 hover:text-white transition">{{ $t('footer.privacy') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/legal/terms')" class="text-slate-400 hover:text-white transition">{{ $t('footer.terms') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/legal/cookies')" class="text-slate-400 hover:text-white transition">{{ $t('footer.cookies') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/legal/ai-consent')" class="text-slate-400 hover:text-white transition">{{ aiConsentLabel }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/legal/payments-subscriptions')" class="text-slate-400 hover:text-white transition">{{ paymentsPolicyLabel }}</NuxtLink></li>
            <li>
              <button type="button" class="text-slate-400 hover:text-white transition" @click="openModal">
                {{ $t('footer.gdpr') }}
              </button>
            </li>
          </ul>
        </div>
      </div>

      <!-- Bottom Footer -->
      <div class="border-t border-slate-800 pt-8">
        <p class="mb-6 rounded-lg border border-slate-800 bg-slate-950/50 px-4 py-3 text-sm leading-6 text-slate-300 text-center">
          Platforma oferă suport emoțional general și instrumente de auto-reflecție. Nu oferă sfaturi medicale, psihologice sau terapeutice. Dacă te confrunți cu o situație gravă, caută ajutor specializat.
        </p>
        <div class="flex flex-col md:flex-row justify-between items-center gap-4">
          <p class="text-sm text-slate-500">
            {{ $t('footer.copyright') || 'Mental Health & Wellness Platform' }} · © 2026 Doisense
          </p>

          <!-- Social Links -->
          <div class="flex items-center gap-4">
            <a
              href="https://discord.com"
              target="_blank"
              rel="noopener noreferrer"
              class="w-10 h-10 flex items-center justify-center rounded-full bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white transition"
              aria-label="Discord"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.211.375-.444.864-.607 1.25a18.27 18.27 0 00-5.487 0c-.163-.386-.395-.875-.607-1.25a.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.873-1.295 1.226-1.994a.076.076 0 00-.042-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.294.075.075 0 01.078-.01c3.928 1.793 8.18 1.793 12.062 0a.075.075 0 01.079.009c.125.098.246.198.373.295a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.076.076 0 00-.041.107c.359.698.77 1.364 1.225 1.994a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-4.467.151-8.343-.88-12.467a.056.056 0 00-.021-.037zM8.02 15.33c-1.183 0-2.157-.965-2.157-2.156 0-1.193.964-2.157 2.157-2.157 1.193 0 2.156.964 2.156 2.157 0 1.19-.963 2.156-2.156 2.156zm7.975 0c-1.183 0-2.157-.965-2.157-2.156 0-1.193.965-2.157 2.157-2.157 1.192 0 2.157.964 2.157 2.157 0 1.19-.965 2.156-2.157 2.156z" />
              </svg>
            </a>
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
              class="w-10 h-10 flex items-center justify-center rounded-full bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white transition"
              aria-label="X"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24h-6.654l-5.207-6.807-5.974 6.807H2.882l7.73-8.835L1.077 2.25h6.82l4.713 6.231 5.612-6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
              </svg>
            </a>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              class="w-10 h-10 flex items-center justify-center rounded-full bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white transition"
              aria-label="GitHub"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v 3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
              </svg>
            </a>
            <a
              href="https://instagram.com"
              target="_blank"
              rel="noopener noreferrer"
              class="w-10 h-10 flex items-center justify-center rounded-full bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white transition"
              aria-label="Instagram"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12m0 2.25c5.385 0 9.75 4.365 9.75 9.75s-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12 6.615 2.25 12 2.25m3.75 9.75c0 2.071-1.679 3.75-3.75 3.75s-3.75-1.679-3.75-3.75 1.679-3.75 3.75-3.75 3.75 1.679 3.75 3.75M16.875 6.75a0.75 0.75 0 1 0 1.5 0 0.75 0.75 0 0 0-1.5 0" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useLocalePath } from '#imports'
import { useGdprConsent } from '~/composables/useGdprConsent'

const localePath = useLocalePath()
const { locale } = useI18n()
const { openModal } = useGdprConsent()

const aiConsentLabel = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return {
    ro: 'Acord de utilizare a AI-ului',
    en: 'AI Usage Agreement',
    de: 'Vereinbarung zur KI-Nutzung',
    fr: 'Accord d\'utilisation de l\'IA',
    it: 'Accordo di utilizzo dell\'IA',
    es: 'Acuerdo de uso de la IA',
    pl: 'Zgoda na korzystanie z AI',
  }[code] || 'AI Usage Agreement'
})

const paymentsPolicyLabel = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return {
    ro: 'Politica de plăți și abonamente',
    en: 'Payments and Subscriptions Policy',
    de: 'Zahlungs- und Abonnementrichtlinie',
    fr: 'Politique de paiements et abonnements',
    it: 'Politica pagamenti e abbonamenti',
    es: 'Política de pagos y suscripciones',
    pl: 'Polityka płatności i subskrypcji',
  }[code] || 'Payments and Subscriptions Policy'
})
</script>
