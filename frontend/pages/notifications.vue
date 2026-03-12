<template>
  <div class="mx-auto max-w-3xl space-y-6">
    <div class="flex items-center justify-between gap-3">
      <h1 class="text-2xl font-bold text-stone-900">{{ text.title }}</h1>
      <span class="rounded-full border border-stone-300 bg-white px-3 py-1 text-xs font-semibold text-stone-700">
        {{ text.unread }}: {{ unreadCount }}
      </span>
    </div>

    <div class="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="text-sm font-semibold text-stone-900">{{ text.pushTitle }}</p>
          <p class="text-xs text-stone-600">{{ text.pushSubtitle }}</p>
        </div>
        <button
          type="button"
          class="rounded-full px-4 py-2 text-xs font-semibold transition"
          :class="pushEnabled ? 'bg-emerald-600 text-white hover:bg-emerald-700' : 'bg-stone-200 text-stone-800 hover:bg-stone-300'"
          @click="togglePush"
        >
          {{ pushEnabled ? text.pushOn : text.pushOff }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-sm text-stone-500">{{ text.loading }}</div>
    <div v-else-if="items.length === 0" class="rounded-xl border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
      {{ text.empty }}
    </div>

    <div v-else class="space-y-3">
      <article
        v-for="item in items"
        :key="item.id"
        class="rounded-xl border p-4 transition"
        :class="item.is_read ? 'border-stone-200 bg-white' : 'border-sky-200 bg-sky-50'"
      >
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-sm font-semibold text-stone-900">{{ item.title }}</h2>
            <p class="mt-1 text-sm text-stone-700">{{ item.body }}</p>
            <p class="mt-2 text-xs text-stone-500">{{ formatDate(item.created_at) }}</p>
          </div>
          <button
            v-if="!item.is_read"
            type="button"
            class="rounded-full border border-stone-300 bg-white px-3 py-1 text-xs font-semibold text-stone-700 hover:bg-stone-50"
            @click="markRead(item.id)"
          >
            {{ text.markRead }}
          </button>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

type NotificationItem = {
  id: number
  title: string
  body: string
  is_read: boolean
  created_at: string
}

const { fetchApi } = useApi()
const { locale } = useI18n()

const items = ref<NotificationItem[]>([])
const unreadCount = ref(0)
const loading = ref(true)
const pushEnabled = ref(false)

const text = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  if (code === 'ro') {
    return {
      title: 'Notificari',
      unread: 'Necitite',
      pushTitle: 'Notificari push in browser',
      pushSubtitle: 'Activeaza/dezactiveaza notificarile rapide pentru update-uri importante.',
      pushOn: 'Push activ',
      pushOff: 'Push inactiv',
      loading: 'Se incarca notificarile...',
      empty: 'Nu ai notificari momentan.',
      markRead: 'Marcheaza citit',
    }
  }
  return {
    title: 'Notifications',
    unread: 'Unread',
    pushTitle: 'Browser push notifications',
    pushSubtitle: 'Enable or disable quick notifications for important updates.',
    pushOn: 'Push enabled',
    pushOff: 'Push disabled',
    loading: 'Loading notifications...',
    empty: 'No notifications yet.',
    markRead: 'Mark read',
  }
})

function formatDate(value: string) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

async function loadNotifications() {
  loading.value = true
  try {
    const data = await fetchApi<{ unread_count: number; items: NotificationItem[] }>('/notifications')
    unreadCount.value = data.unread_count || 0
    items.value = data.items || []
  } finally {
    loading.value = false
  }
}

async function loadPushPreference() {
  try {
    const data = await fetchApi<{ push_enabled: boolean }>('/notifications/preferences')
    pushEnabled.value = Boolean(data.push_enabled)
  } catch {
    pushEnabled.value = false
  }
}

async function togglePush() {
  const nextValue = !pushEnabled.value

  if (nextValue && import.meta.client && 'Notification' in window) {
    const permission = await Notification.requestPermission()
    if (permission !== 'granted') {
      return
    }
  }

  const data = await fetchApi<{ push_enabled: boolean }>('/notifications/preferences', {
    method: 'POST',
    body: { push_enabled: nextValue },
  })
  pushEnabled.value = Boolean(data.push_enabled)
}

async function markRead(notificationId: number) {
  await fetchApi(`/notifications/${notificationId}/read`, { method: 'POST' })
  await loadNotifications()
}

onMounted(async () => {
  await Promise.all([loadNotifications(), loadPushPreference()])
})
</script>
