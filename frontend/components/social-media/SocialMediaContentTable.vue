<template>
  <section class="rounded-2xl border border-[#d4e4e0] bg-[#fafbfa] p-5 shadow-sm">
    <div class="mb-4 flex flex-wrap items-start justify-between gap-3">
      <div>
        <h2 class="text-lg font-semibold text-[#2c3e35]">Content List Panel</h2>
        <p class="text-sm text-[#5a6b63]">Review generated posts, publish by platform, and inspect publish logs.</p>
      </div>
      <button
        type="button"
        class="rounded-lg border border-[#c6d9d2] bg-[#f0f4f1] px-3 py-1.5 text-xs font-semibold text-[#42524b] transition hover:bg-[#e8f1ed]"
        :disabled="loading"
        @click="$emit('refresh')"
      >
        Refresh
      </button>
    </div>

    <div class="mb-4 grid gap-3 md:grid-cols-4">
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-[#6e7d76]">Platform</label>
        <select
          v-model="localFilters.platform"
          class="w-full rounded-lg border border-[#c6d9d2] bg-[#fafbfa] px-3 py-2 text-sm text-[#2c3e35]"
        >
          <option value="">All</option>
          <option value="instagram">Instagram</option>
          <option value="tiktok">TikTok</option>
          <option value="linkedin">LinkedIn</option>
        </select>
      </div>
      <div>
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-[#6e7d76]">Status</label>
        <select
          v-model="localFilters.status"
          class="w-full rounded-lg border border-[#c6d9d2] bg-[#fafbfa] px-3 py-2 text-sm text-[#2c3e35]"
        >
          <option value="">All</option>
          <option value="draft">Draft</option>
          <option value="posted">Posted</option>
        </select>
      </div>
      <div class="md:col-span-2">
        <label class="mb-1 block text-xs font-semibold uppercase tracking-wide text-[#6e7d76]">Search</label>
        <div class="flex gap-2">
          <input
            v-model="localFilters.search"
            type="text"
            placeholder="Search title or topic"
            class="w-full rounded-lg border border-[#c6d9d2] bg-[#fafbfa] px-3 py-2 text-sm text-[#2c3e35] placeholder:text-[#9aa8a2]"
          >
          <button
            type="button"
            class="rounded-lg bg-[#2c3e35] px-3 py-2 text-xs font-semibold text-white hover:bg-[#1f2d26]"
            @click="$emit('apply-filters', { ...localFilters })"
          >
            Apply
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
      {{ error }}
    </div>

    <div class="overflow-x-auto rounded-xl border border-[#d4e4e0]">
      <table class="min-w-full divide-y divide-[#e4ece8] bg-white text-sm">
        <thead class="bg-[#f4f8f6]">
          <tr>
            <th class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-[#6e7d76]">Platform</th>
            <th class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-[#6e7d76]">Title</th>
            <th class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-[#6e7d76]">Topic</th>
            <th class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-[#6e7d76]">Status</th>
            <th class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-[#6e7d76]">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-if="loading">
            <td colspan="5" class="px-3 py-8 text-center text-sm text-[#6e7d76]">Loading posts...</td>
          </tr>

          <tr v-else-if="posts.length === 0">
            <td colspan="5" class="px-3 py-8 text-center text-sm text-[#6e7d76]">No social posts found for current filters.</td>
          </tr>

          <tr v-for="post in posts" :key="post.id" class="border-t border-[#edf3ef]">
            <td class="px-3 py-2 text-[#42524b]">{{ formatPlatform(post.platform) }}</td>
            <td class="px-3 py-2 text-[#2c3e35]">{{ post.title }}</td>
            <td class="px-3 py-2 text-[#42524b]">{{ post.wellness_topic }}</td>
            <td class="px-3 py-2">
              <span
                class="inline-flex rounded-full border px-2 py-0.5 text-xs font-semibold"
                :class="post.status === 'posted' ? 'border-[#bde0ca] bg-[#eef8f2] text-[#2f7d56]' : 'border-[#e8d7b3] bg-[#faf5e8] text-[#8a6a2d]'"
              >
                {{ post.status }}
              </span>
            </td>
            <td class="px-3 py-2">
              <div class="flex flex-wrap items-center gap-1.5">
                <PublishActionButton
                  platform="instagram"
                  :recommended="post.platform === 'instagram'"
                  :loading="isPublishing(post.id, 'instagram')"
                  :disabled="post.status === 'posted'"
                  @click="$emit('publish', { postId: post.id, platform: 'instagram' })"
                />
                <PublishActionButton
                  platform="tiktok"
                  :recommended="post.platform === 'tiktok'"
                  :loading="isPublishing(post.id, 'tiktok')"
                  :disabled="true"
                  @click="$emit('publish', { postId: post.id, platform: 'tiktok' })"
                />
                <PublishActionButton
                  platform="linkedin"
                  :recommended="post.platform === 'linkedin'"
                  :loading="isPublishing(post.id, 'linkedin')"
                  :disabled="post.status === 'posted'"
                  @click="$emit('publish', { postId: post.id, platform: 'linkedin' })"
                />
                <button
                  type="button"
                  class="rounded-lg border border-[#d4e4e0] bg-[#fafbfa] px-2.5 py-1.5 text-xs font-semibold text-[#5a6b63] hover:bg-[#f0f4f1]"
                  @click="openLog(post)"
                >
                  Log
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-if="logModalPost"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      @click.self="closeLog"
    >
      <div class="w-full max-w-2xl rounded-2xl border border-[#d4e4e0] bg-[#fafbfa] p-5 shadow-xl">
        <div class="mb-3 flex items-start justify-between gap-3">
          <div>
            <h3 class="text-base font-semibold text-[#2c3e35]">Publish Log</h3>
            <p class="text-xs text-[#6e7d76]">#{{ logModalPost.id }} · {{ logModalPost.title }}</p>
          </div>
          <button
            type="button"
            class="rounded-full border border-[#d4e4e0] px-2.5 py-1 text-xs font-semibold text-[#5a6b63] hover:bg-[#f0f4f1]"
            @click="closeLog"
          >
            Close
          </button>
        </div>
        <pre class="max-h-[60vh] overflow-auto whitespace-pre-wrap rounded-lg border border-[#d4e4e0] bg-white p-3 text-xs text-[#2c3e35]">{{ logModalPost.publish_log || 'No logs yet.' }}</pre>
      </div>
    </div>
  </section>
</template>

<script setup>
import PublishActionButton from './PublishActionButton.vue'

const props = defineProps({
  posts: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
  filters: {
    type: Object,
    default: () => ({ platform: '', status: '', search: '' }),
  },
  publishLoadingKey: {
    type: String,
    default: '',
  },
})

defineEmits(['refresh', 'apply-filters', 'publish'])

const localFilters = reactive({
  platform: '',
  status: '',
  search: '',
})

const logModalPost = ref(null)

watch(
  () => props.filters,
  (value) => {
    localFilters.platform = value.platform
    localFilters.status = value.status
    localFilters.search = value.search
  },
  { immediate: true, deep: true }
)

function formatPlatform(value) {
  if (value === 'instagram') return 'Instagram'
  if (value === 'tiktok') return 'TikTok'
  if (value === 'linkedin') return 'LinkedIn'
  return value
}

function isPublishing(postId, platform) {
  return props.publishLoadingKey === `${postId}:${platform}`
}

function openLog(post) {
  logModalPost.value = post
}

function closeLog() {
  logModalPost.value = null
}
</script>
