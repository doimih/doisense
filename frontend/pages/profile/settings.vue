<template>
  <section class="mx-auto max-w-5xl space-y-6 rounded-2xl border border-sky-100 bg-gradient-to-br from-[#f7fbff] via-[#f5f9fc] to-[#eef4f8] p-4 md:p-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">Image Settings</h1>
        <p class="mt-1 text-sm text-slate-600">
          Upload project images and copy links quickly for Hero or CMS content.
        </p>
      </div>
      <NuxtLink
        :to="localePath('/profile')"
        class="rounded-lg border border-sky-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-sky-50"
      >
        Back to profile
      </NuxtLink>
    </div>

    <div v-if="!authStore.user?.is_superuser" class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
      This section is available only for admin accounts.
    </div>

    <template v-else>
      <div class="rounded-xl border border-sky-200 bg-white p-4 shadow-sm">
        <form class="space-y-3" @submit.prevent="uploadImage">
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-700">Choose image</label>
            <input
              ref="fileInput"
              type="file"
              accept="image/png,image/jpeg,image/webp,image/gif"
              class="block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 file:mr-3 file:rounded-md file:border-0 file:bg-sky-100 file:px-3 file:py-1.5 file:font-medium file:text-slate-800"
              @change="onFileChange"
            >
          </div>
          <div class="flex flex-wrap gap-2">
            <button
              type="submit"
              :disabled="uploading || !selectedFile"
              class="rounded-lg bg-sky-300 px-4 py-2 text-sm font-semibold text-stone-900 transition hover:bg-sky-200 disabled:opacity-50"
            >
              {{ uploading ? 'Uploading...' : 'Upload image' }}
            </button>
            <button
              type="button"
              :disabled="loading"
              class="rounded-lg border border-sky-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-sky-50 disabled:opacity-50"
              @click="loadImages"
            >
              Refresh list
            </button>
          </div>
          <p v-if="uploadError" class="text-sm text-red-600">{{ uploadError }}</p>
          <p v-if="uploadSuccess" class="text-sm text-emerald-700">{{ uploadSuccess }}</p>
        </form>
      </div>

      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-900">Uploaded images</h2>
          <p class="text-xs text-slate-500">{{ images.length }} item(s)</p>
        </div>

        <div v-if="loading" class="rounded-xl border border-sky-200 bg-white p-4 text-sm text-slate-600">Loading...</div>

        <div v-else-if="!images.length" class="rounded-xl border border-sky-200 bg-white p-4 text-sm text-slate-600">
          No images uploaded yet.
        </div>

        <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <article
            v-for="item in images"
            :key="item.url"
            class="overflow-hidden rounded-xl border border-sky-200 bg-white shadow-sm"
          >
            <img :src="item.url" :alt="item.name" class="h-40 w-full bg-slate-100 object-cover" loading="lazy" decoding="async">
            <div class="space-y-2 p-3">
              <p class="truncate text-sm font-medium text-slate-800" :title="item.name">{{ item.name }}</p>
              <p class="text-xs text-slate-500">{{ formatSize(item.size) }}</p>
              <button
                type="button"
                class="w-full rounded-md border border-sky-200 bg-sky-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-sky-100"
                @click="copyUrl(item.url)"
              >
                Copy URL
              </button>
            </div>
          </article>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

const { fetchApi } = useApi()
const authStore = useAuthStore()
const localePath = useLocalePath()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const loading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref('')

type ImageItem = {
  name: string
  url: string
  size: number
  updated_at: string
}

const images = ref<ImageItem[]>([])

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  selectedFile.value = input.files?.[0] || null
  uploadError.value = ''
  uploadSuccess.value = ''
}

async function loadImages() {
  if (!authStore.user?.is_superuser) return
  loading.value = true
  try {
    const res = await fetchApi<{ items: ImageItem[] }>('/settings/images', { method: 'GET' })
    images.value = res.items || []
  } catch {
    uploadError.value = 'Could not load images list.'
  } finally {
    loading.value = false
  }
}

async function uploadImage() {
  if (!selectedFile.value) return

  uploadError.value = ''
  uploadSuccess.value = ''
  uploading.value = true

  try {
    const data = new FormData()
    data.append('image', selectedFile.value)

    const uploaded = await fetchApi<{ name: string; url: string }>('/settings/images', {
      method: 'POST',
      body: data,
    })

    uploadSuccess.value = `Uploaded: ${uploaded.name}`
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
    await loadImages()
  } catch (error: any) {
    uploadError.value = error?.data?.detail || 'Upload failed.'
  } finally {
    uploading.value = false
  }
}

async function copyUrl(url: string) {
  try {
    await navigator.clipboard.writeText(url)
    uploadSuccess.value = 'URL copied to clipboard.'
    uploadError.value = ''
  } catch {
    uploadError.value = 'Could not copy URL. Copy manually from browser.'
  }
}

function formatSize(size: number): string {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

onMounted(async () => {
  await loadImages()
})
</script>
