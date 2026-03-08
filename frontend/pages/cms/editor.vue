<template>
  <section class="max-w-6xl mx-auto py-8 space-y-4">
    <header class="flex items-center justify-between gap-3 flex-wrap">
      <div>
        <h1 class="text-3xl font-bold text-stone-900">CMS Editor</h1>
        <p class="text-stone-600 text-sm">Edit pages saved in backend database (`core_cmspage`).</p>
      </div>
      <button
        type="button"
        class="px-4 py-2 rounded-lg bg-stone-900 text-white hover:bg-black"
        @click="createPage"
      >
        New Page
      </button>
    </header>

    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

    <div v-if="!isSuperAdmin" class="bg-amber-50 border border-amber-200 rounded-lg p-4 text-amber-900 text-sm">
      Access denied. Superadmin only.
    </div>

    <div v-else class="grid gap-4 lg:grid-cols-[260px,1fr]">
      <aside class="bg-white border border-stone-200 rounded-xl p-3 max-h-[70vh] overflow-y-auto">
        <button
          v-for="page in pages"
          :key="page.slug"
          type="button"
          class="w-full text-left px-3 py-2 rounded-lg mb-2"
          :class="selected?.slug === page.slug ? 'bg-stone-900 text-white' : 'hover:bg-stone-100 text-stone-800'"
          @click="selectPage(page.slug)"
        >
          <p class="font-medium">{{ page.title || page.slug }}</p>
          <p class="text-xs opacity-80">/{{ page.slug }}</p>
        </button>
      </aside>

      <main class="bg-white border border-stone-200 rounded-xl p-4 space-y-3">
        <div class="grid gap-3 md:grid-cols-2">
          <label class="text-sm text-stone-700">
            <span class="block mb-1">Slug</span>
            <input v-model="form.slug" type="text" class="w-full px-3 py-2 border border-stone-300 rounded-lg" disabled />
          </label>
          <label class="text-sm text-stone-700">
            <span class="block mb-1">Title</span>
            <input v-model="form.title" type="text" class="w-full px-3 py-2 border border-stone-300 rounded-lg" />
          </label>
        </div>

        <label class="text-sm text-stone-700 block">
          <span class="block mb-1">Content (Markdown)</span>
          <textarea
            v-model="form.content"
            rows="18"
            class="w-full px-3 py-2 border border-stone-300 rounded-lg font-mono text-sm"
          />
        </label>

        <label class="inline-flex items-center gap-2 text-sm text-stone-700">
          <input v-model="form.is_published" type="checkbox" />
          Published
        </label>

        <div class="flex items-center gap-3">
          <button
            type="button"
            class="px-4 py-2 rounded-lg bg-amber-600 text-white hover:bg-amber-700"
            :disabled="saving || !form.slug"
            @click="save"
          >
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
          <NuxtLink v-if="form.slug" :to="localePath(`/cms/${form.slug}`)" class="text-sm text-stone-700 underline">
            Open page
          </NuxtLink>
        </div>
      </main>
    </div>
  </section>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

interface CmsPage {
  slug: string
  title: string
  content: string
  is_published: boolean
}

const { fetchApi } = useApi()
const authStore = useAuthStore()
const localePath = useLocalePath()

const pages = ref<CmsPage[]>([])
const selected = ref<CmsPage | null>(null)
const saving = ref(false)
const error = ref('')

const form = reactive<CmsPage>({ slug: '', title: '', content: '', is_published: true })

const isSuperAdmin = computed(() => !!authStore.user?.is_superuser)

function loadIntoForm(page: CmsPage) {
  form.slug = page.slug
  form.title = page.title
  form.content = page.content
  form.is_published = page.is_published
}

async function loadPages() {
  error.value = ''
  try {
    pages.value = await fetchApi<CmsPage[]>('/cms/pages')
    if (pages.value.length) {
      await selectPage(pages.value[0].slug)
    }
  } catch (e: unknown) {
    error.value = (e as { message?: string })?.message || 'Failed loading CMS pages.'
  }
}

async function selectPage(slug: string) {
  error.value = ''
  try {
    const page = await fetchApi<CmsPage>(`/cms/pages/${slug}`)
    selected.value = page
    loadIntoForm(page)
  } catch (e: unknown) {
    error.value = (e as { message?: string })?.message || 'Failed loading selected page.'
  }
}

async function save() {
  if (!form.slug) return
  error.value = ''
  saving.value = true
  try {
    const saved = await fetchApi<CmsPage>(`/cms/pages/${form.slug}`, {
      method: 'PUT',
      body: {
        title: form.title,
        content: form.content,
        is_published: form.is_published,
      },
    })
    selected.value = saved
    const idx = pages.value.findIndex((p) => p.slug === saved.slug)
    if (idx >= 0) {
      pages.value[idx] = saved
    } else {
      pages.value.push(saved)
    }
  } catch (e: unknown) {
    error.value = (e as { message?: string })?.message || 'Save failed.'
  } finally {
    saving.value = false
  }
}

async function createPage() {
  const slug = prompt('New page slug (example: faq)')?.trim().toLowerCase()
  if (!slug) return
  form.slug = slug
  form.title = slug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
  form.content = '# New page\n\nStart editing...'
  form.is_published = true
  await save()
  await selectPage(slug)
}

onMounted(async () => {
  authStore.hydrate()
  if (isSuperAdmin.value) {
    await loadPages()
  }
})
</script>
