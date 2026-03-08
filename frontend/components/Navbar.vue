<template>
  <nav class="bg-white border-b border-stone-200 px-4 py-3">
    <div class="container mx-auto flex items-center justify-between">
      <NuxtLink :to="localePath('/')" class="text-xl font-semibold text-stone-800">Doisense</NuxtLink>
      <div class="flex items-center gap-4">
        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/chat')" class="text-stone-600 hover:text-stone-900">
          {{ $t('nav.chat') }}
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/journal')" class="text-stone-600 hover:text-stone-900">
          {{ $t('nav.journal') }}
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/programs')" class="text-stone-600 hover:text-stone-900">
          {{ $t('nav.programs') }}
        </NuxtLink>
        <NuxtLink v-if="authStore.isLoggedIn" :to="localePath('/profile')" class="text-stone-600 hover:text-stone-900">
          {{ $t('nav.profile') }}
        </NuxtLink>
        <NuxtLink v-if="!authStore.isLoggedIn" :to="localePath('/auth/login')" class="text-stone-600 hover:text-stone-900">
          {{ $t('auth.login') }}
        </NuxtLink>
        <button
          v-if="authStore.isLoggedIn"
          type="button"
          class="text-stone-600 hover:text-stone-900"
          @click="logout"
        >
          {{ $t('auth.logout') }}
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
const { localePath } = useLocalePath()
const authStore = useAuthStore()
const router = useRouter()

function logout() {
  authStore.logout()
  router.push(localePath('/'))
}
</script>
