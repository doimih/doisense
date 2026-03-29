<template>
  <div class="mx-auto max-w-7xl space-y-6">
    <header class="rounded-2xl border border-[#d4e4e0] bg-[linear-gradient(135deg,#fafbfa_0%,#f4f8f6_48%,#eef4f1_100%)] p-6">
      <p class="inline-flex rounded-full border border-[#c6d9d2] bg-[#fafbfa] px-3 py-1 text-xs font-semibold uppercase tracking-wide text-[#42524b]">
        AI Brain
      </p>
      <h1 class="mt-3 text-2xl font-bold text-[#2c3e35] md:text-3xl">Social Media Dashboard</h1>
      <p class="mt-2 max-w-3xl text-sm text-[#5a6b63]">
        Generate wellness-focused social posts, review draft content, publish to platforms, and inspect operational logs.
      </p>
    </header>

    <div v-if="notification.message" class="rounded-xl border px-4 py-3 text-sm" :class="notificationClass">
      {{ notification.message }}
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.05fr_1.4fr]">
      <SocialMediaGeneratorPanel
        :loading="generatorLoading"
        :error="generatorError"
        :preview="previewPost"
        @generate="handleGenerate"
      />

      <SocialMediaContentTable
        :posts="posts"
        :loading="postsLoading"
        :error="postsError"
        :filters="filters"
        :publish-loading-key="publishLoadingKey"
        @refresh="loadPosts"
        @apply-filters="applyFilters"
        @publish="handlePublish"
      />
    </div>
  </div>
</template>

<script setup>
import SocialMediaContentTable from './SocialMediaContentTable.vue'
import SocialMediaGeneratorPanel from './SocialMediaGeneratorPanel.vue'

const { fetchApi } = useApi()

const posts = ref([])
const previewPost = ref(null)

const generatorLoading = ref(false)
const generatorError = ref('')

const postsLoading = ref(false)
const postsError = ref('')

const publishLoadingKey = ref('')

const filters = reactive({
  platform: '',
  status: '',
  search: '',
})

const notification = reactive({
  type: '',
  message: '',
})

const notificationClass = computed(() => {
  if (notification.type === 'success') return 'border-[#bde0ca] bg-[#eef8f2] text-[#2f7d56]'
  if (notification.type === 'error') return 'border-red-200 bg-red-50 text-red-700'
  return 'border-[#d4e4e0] bg-white text-[#42524b]'
})

function showNotification(type, message) {
  notification.type = type
  notification.message = message
  window.setTimeout(() => {
    notification.type = ''
    notification.message = ''
  }, 4500)
}

function normalizePostsResponse(payload) {
  if (Array.isArray(payload)) return payload
  return payload.items || payload.results || payload.posts || []
}

function normalizeGenerateResponse(payload) {
  if ('post' in payload && payload.post) return payload.post
  return payload
}

async function loadPosts() {
  postsLoading.value = true
  postsError.value = ''

  try {
    const params = new URLSearchParams()
    if (filters.platform) params.set('platform', filters.platform)
    if (filters.status) params.set('status', filters.status)
    if (filters.search.trim()) params.set('search', filters.search.trim())

    const query = params.toString()
    const endpoint = query ? `/social/posts/?${query}` : '/social/posts/'
    const data = await fetchApi(endpoint)
    posts.value = normalizePostsResponse(data)
  } catch (error) {
    postsError.value = parseErrorMessage(error, 'Could not load social media posts.')
    showNotification('error', postsError.value)
  } finally {
    postsLoading.value = false
  }
}

async function handleGenerate(payload) {
  generatorError.value = ''

  if (!payload.topic.trim()) {
    generatorError.value = 'Topic is required before generating content.'
    return
  }

  generatorLoading.value = true
  try {
    const data = await fetchApi('/social/generate/', {
      method: 'POST',
      body: {
        platform: payload.platform,
        topic: payload.topic.trim(),
      },
    })

    previewPost.value = normalizeGenerateResponse(data)
    showNotification('success', 'Post generated and saved as draft successfully.')
    await loadPosts()
  } catch (error) {
    generatorError.value = parseErrorMessage(error, 'Could not generate social post.')
    showNotification('error', generatorError.value)
  } finally {
    generatorLoading.value = false
  }
}

async function handlePublish(payload) {
  publishLoadingKey.value = `${payload.postId}:${payload.platform}`

  try {
    const response = await fetchApi('/social/publish/', {
      method: 'POST',
      body: {
        post_id: payload.postId,
        platform: payload.platform,
      },
    })

    const message = response.detail || response.message || 'Post published successfully.'
    showNotification('success', message)
    await loadPosts()
  } catch (error) {
    showNotification('error', parseErrorMessage(error, 'Could not publish post.'))
  } finally {
    publishLoadingKey.value = ''
  }
}

function applyFilters(next) {
  filters.platform = next.platform
  filters.status = next.status
  filters.search = next.search
  loadPosts()
}

function parseErrorMessage(error, fallback) {
  const candidate = error || {}

  return (
    candidate?.data?.detail
    || candidate?.data?.message
    || candidate?.statusMessage
    || candidate?.message
    || fallback
  )
}

onMounted(() => {
  loadPosts()
})
</script>
