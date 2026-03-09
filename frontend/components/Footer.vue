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
            <li><NuxtLink :to="localePath('/legal/gdpr')" class="text-stone-400 hover:text-stone-100">{{ $t('footer.gdpr') }}</NuxtLink></li>
          </ul>
        </div>

        <div>
          <h3 class="mb-4 text-sm font-semibold text-white">{{ $t('footer.newsletterTitle') }}</h3>
          <form class="flex items-center gap-2" @submit.prevent>
            <input
              type="email"
              :placeholder="$t('footer.newsletterPlaceholder')"
              class="w-full rounded-md border border-stone-700 bg-[#151519] px-3 py-2 text-sm text-stone-100 placeholder:text-stone-500"
            />
            <button type="submit" class="rounded-md bg-amber-500 px-3 py-2 text-sm font-medium text-black hover:bg-amber-400">
              {{ $t('footer.subscribe') }}
            </button>
          </form>
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
import { useLocalePath } from '#imports'

const localePath = useLocalePath()
</script>
