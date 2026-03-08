<template>
  <div class="max-w-3xl mx-auto text-center py-16">
    <h1 class="text-4xl font-bold text-stone-800 mb-4">{{ $t('landing.title') }}</h1>
    <p class="text-lg text-stone-600 mb-8">{{ $t('landing.subtitle') }}</p>
    <div class="flex gap-4 justify-center flex-wrap">
      <NuxtLink
        v-if="!authStore.isLoggedIn"
        :to="localePath('/auth/login')"
        class="px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700"
      >
        {{ $t('auth.login') }}
      </NuxtLink>
      <NuxtLink
        v-if="!authStore.isLoggedIn"
        :to="localePath('/auth/register')"
        class="px-6 py-3 border border-stone-300 rounded-lg hover:bg-stone-100"
      >
        {{ $t('auth.register') }}
      </NuxtLink>
      <NuxtLink
        v-if="authStore.isLoggedIn"
        :to="localePath('/chat')"
        class="px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700"
      >
        {{ $t('nav.chat') }}
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const { localePath } = useLocalePath()
const authStore = useAuthStore()
</script>
