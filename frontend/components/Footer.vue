<template>
  <footer class="mt-auto border-t border-stone-800 bg-[#111113] text-stone-200">
    <div class="container mx-auto px-4 py-10">
      <div class="grid gap-8 md:grid-cols-4">
        <div>
          <h3 class="mb-4 text-sm font-semibold text-white">{{ $t('footer.resources') }}</h3>
          <ul class="space-y-2 text-sm">
            <li><NuxtLink :to="localePath('/contact')" class="text-stone-400 hover:text-stone-100">{{ $t('footer.helpCenter') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/about')" class="text-stone-400 hover:text-stone-100">{{ $t('footer.docs') }}</NuxtLink></li>
          </ul>
        </div>

        <div>
          <h3 class="mb-4 text-sm font-semibold text-white">{{ $t('footer.features') }}</h3>
          <ul class="space-y-2 text-sm">
            <li><NuxtLink :to="localePath('/pricing')" class="text-stone-400 hover:text-stone-100">{{ $t('nav.pricing') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/programs')" class="text-stone-400 hover:text-stone-100">{{ $t('nav.programs') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/journal')" class="text-stone-400 hover:text-stone-100">{{ $t('nav.journal') }}</NuxtLink></li>
          </ul>
        </div>

        <div>
          <h3 class="mb-4 text-sm font-semibold text-white">{{ $t('footer.company') }}</h3>
          <ul class="space-y-2 text-sm">
            <li><NuxtLink :to="localePath('/about')" class="text-stone-400 hover:text-stone-100">{{ $t('nav.about') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/legal/privacy')" class="text-stone-400 hover:text-stone-100">{{ $t('footer.privacy') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/legal/terms')" class="text-stone-400 hover:text-stone-100">{{ $t('footer.terms') }}</NuxtLink></li>
            <li><NuxtLink :to="localePath('/legal/cookies')" class="text-stone-400 hover:text-stone-100">{{ $t('footer.cookies') }}</NuxtLink></li>
            <li>
              <button type="button" class="text-stone-400 hover:text-stone-100" @click="openModal">
                {{ $t('footer.gdpr') }}
              </button>
            </li>
          </ul>
        </div>

        <div>
          <h3 class="mb-4 text-sm font-semibold text-white">{{ $t('footer.newsletterTitle') }}</h3>
          <form class="flex items-center gap-2" @submit.prevent="subscribeToNewsletter">
            <input
              v-model="newsletterEmail"
              type="email"
              :placeholder="$t('footer.newsletterPlaceholder')"
              required
              class="w-full rounded-md border border-stone-700 bg-[#151519] px-3 py-2 text-sm text-stone-100 placeholder:text-stone-500"
            />
            <button type="submit" :disabled="newsletterLoading" class="rounded-md bg-amber-500 px-3 py-2 text-sm font-medium text-black hover:bg-amber-400 disabled:opacity-60">
              {{ $t('footer.subscribe') }}
            </button>
          </form>
          <p v-if="newsletterStatus" class="mt-2 text-xs" :class="newsletterError ? 'text-red-300' : 'text-emerald-300'">
            {{ newsletterStatus }}
          </p>
        </div>
      </div>

      <div class="mt-8 flex flex-col items-start justify-between gap-3 border-t border-stone-800 pt-5 text-sm text-stone-400 md:flex-row md:items-center">
        <p>{{ $t('footer.builtWithNuxt') }} · © 2026</p>
        <div class="flex items-center gap-4">
          <a href="#" class="hover:text-white" aria-label="Discord">Discord</a>
          <a href="#" class="hover:text-white" aria-label="X">X</a>
          <a href="#" class="hover:text-white" aria-label="GitHub">GitHub</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useI18n, useLocalePath } from '#imports'
import { useApi } from '~/composables/useApi'
import { useGdprConsent } from '~/composables/useGdprConsent'

const localePath = useLocalePath()
const { openModal } = useGdprConsent()
const { fetchApi } = useApi()
const { t } = useI18n()

const newsletterEmail = ref('')
const newsletterStatus = ref('')
const newsletterError = ref(false)
const newsletterLoading = ref(false)

async function subscribeToNewsletter() {
  newsletterStatus.value = ''
  newsletterError.value = false

  const email = newsletterEmail.value.trim().toLowerCase()
  if (!email) {
    newsletterError.value = true
    newsletterStatus.value = t('footer.newsletterInvalidEmail')
    return
  }

  newsletterLoading.value = true
  try {
    await fetchApi('/newsletter/subscribe', {
      method: 'POST',
      body: { email },
    })
    newsletterEmail.value = ''
    newsletterStatus.value = t('footer.newsletterSubscribed')
  } catch {
    newsletterError.value = true
    newsletterStatus.value = t('footer.newsletterSubscribeError')
  } finally {
    newsletterLoading.value = false
  }
}
</script>
