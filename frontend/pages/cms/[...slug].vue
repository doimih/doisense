<template>
  <section class="max-w-4xl mx-auto py-10 space-y-6">
    <header class="space-y-2">
      <h1 class="text-3xl font-bold text-stone-900">CMS</h1>
      <p class="text-stone-600 text-sm">
        Editable content source:
        <code class="bg-stone-100 px-2 py-1 rounded">frontend/content/cms/*.md</code>
      </p>
    </header>

    <article class="prose prose-stone max-w-none bg-white border border-stone-200 rounded-xl p-6">
      <ContentDoc :path="contentPath" />
    </article>
  </section>
</template>

<script setup lang="ts">
const route = useRoute()

const contentPath = computed(() => {
  const slug = route.params.slug
  if (Array.isArray(slug) && slug.length) {
    return `/cms/${slug.join('/')}`
  }
  if (typeof slug === 'string' && slug.length) {
    return `/cms/${slug}`
  }
  return '/cms/home'
})
</script>
