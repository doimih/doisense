<template>
  <main class="min-h-screen bg-[radial-gradient(circle_at_20%_15%,#ecf4ef_0%,#f7faf8_35%,#f5f8f6_100%)] px-4 py-6 md:px-8 md:py-8">
    <SocialMediaDashboard />
  </main>
</template>

<script setup lang="ts">
import SocialMediaDashboard from '~/components/social-media/SocialMediaDashboard.vue'

definePageMeta({
  middleware: ['auth', 'admin'],
})
</script>
