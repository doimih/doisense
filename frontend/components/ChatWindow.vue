<template>
  <div class="border border-stone-200 rounded-lg bg-white flex flex-col" style="min-height: 400px">
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
      <ChatBubble
        v-for="(msg, i) in messages"
        :key="i"
        :message="msg.message"
        :is-user="msg.isUser"
      />
      <p v-if="loading" class="text-stone-500 text-sm">{{ $t('common.loading') }}...</p>
    </div>
    <form @submit.prevent="send" class="p-4 border-t border-stone-200 flex gap-2">
      <input
        v-model="input"
        type="text"
        :placeholder="$t('chat.placeholder')"
        class="flex-1 px-3 py-2 border border-stone-300 rounded-lg"
      />
      <button
        type="submit"
        :disabled="loading || !input.trim()"
        class="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50"
      >
        {{ $t('chat.send') }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
interface ChatMessage {
  message: string
  isUser: boolean
}

const { $t } = useNuxtApp()
const { fetchApi } = useApi()

const messages = ref<ChatMessage[]>([])
const input = ref('')
const loading = ref(false)

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return
  messages.value.push({ message: text, isUser: true })
  input.value = ''
  loading.value = true
  try {
    const res = await fetchApi<{ reply: string }>('/chat/send', {
      method: 'POST',
      body: { message: text },
    })
    messages.value.push({ message: res.reply, isUser: false })
  } catch (e) {
    messages.value.push({
      message: (e as Error).message || 'Error sending message',
      isUser: false,
    })
  } finally {
    loading.value = false
  }
}
</script>
