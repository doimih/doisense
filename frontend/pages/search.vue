<template>
  <section class="max-w-5xl mx-auto py-8 space-y-6">
    <header class="space-y-2">
      <h1 class="text-3xl font-bold text-stone-900">{{ $t('search.title') }}</h1>
      <p class="text-stone-600 text-sm">{{ $t('search.subtitle') }}</p>
    </header>

    <form class="flex gap-2" @submit.prevent="runSearch">
      <input
        v-model="query"
        type="text"
        :placeholder="$t('search.placeholder')"
        class="flex-1 px-3 py-2 border border-stone-300 rounded-lg"
      />
      <button type="submit" class="px-4 py-2 rounded-lg bg-stone-900 text-white hover:bg-black">{{ $t('search.action') }}</button>
    </form>

    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

    <div class="grid gap-4 md:grid-cols-3">
      <article class="bg-white border border-stone-200 rounded-xl p-4">
        <h2 class="font-semibold text-stone-900 mb-2">{{ $t('search.programs') }} ({{ results.programs.length }})</h2>
        <ul class="space-y-2 text-sm">
          <li v-for="item in results.programs" :key="`p-${item.id}`">
            <NuxtLink :to="localePath(item.path)" class="underline text-stone-800">{{ item.title }}</NuxtLink>
          </li>
        </ul>
      </article>

      <article class="bg-white border border-stone-200 rounded-xl p-4">
        <h2 class="font-semibold text-stone-900 mb-2">{{ $t('search.journalQuestions') }} ({{ results.journal_questions.length }})</h2>
        <ul class="space-y-2 text-sm">
          <li v-for="item in results.journal_questions" :key="`j-${item.id}`">
            <NuxtLink :to="localePath(item.path)" class="underline text-stone-800">{{ item.text }}</NuxtLink>
          </li>
        </ul>
      </article>

      <article class="bg-white border border-stone-200 rounded-xl p-4">
        <h2 class="font-semibold text-stone-900 mb-2">{{ $t('search.cmsPages') }} ({{ results.cms_pages.length }})</h2>
        <ul class="space-y-2 text-sm">
          <li v-for="item in results.cms_pages" :key="`c-${item.slug}`">
            <NuxtLink :to="localePath(item.path)" class="underline text-stone-800">{{ item.title }}</NuxtLink>
          </li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n, useLocalePath } from '#imports'
import { useApi } from '~/composables/useApi'

interface SearchResponse {
  query: string
  results: {
    programs: Array<{ id: number; title: string; path: string }>
    journal_questions: Array<{ id: number; text: string; path: string }>
    cms_pages: Array<{ slug: string; title: string; path: string }>
  }
}

const { fetchApi } = useApi()
const localePath = useLocalePath()
const { locale, t } = useI18n()

const query = ref('')
const error = ref('')
const results = ref<SearchResponse['results']>({ programs: [], journal_questions: [], cms_pages: [] })

usePublicSeo({
  title: computed(() => t('search.seoTitle')),
  description: computed(() => t('search.seoDescription')),
  noindex: true,
})

async function runSearch() {
  error.value = ''
  if (query.value.trim().length < 2) {
    results.value = { programs: [], journal_questions: [], cms_pages: [] }
    return
  }

  try {
    const lang = (locale.value || 'en').split('-')[0]
    const data = await fetchApi<SearchResponse>(`/search?q=${encodeURIComponent(query.value.trim())}&language=${lang}`)
    results.value = data.results
  } catch (e: unknown) {
    error.value = (e as { message?: string })?.message || t('search.failed')
  }
}
</script>
