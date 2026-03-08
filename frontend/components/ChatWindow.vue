<template>
  <div class="grid gap-4 lg:grid-cols-[84px,1fr,280px]">
    <aside class="rounded-2xl bg-stone-900 p-3 text-stone-100">
      <div class="flex h-full flex-row gap-2 overflow-x-auto lg:flex-col lg:overflow-visible">
        <button
          v-for="mod in modules"
          :key="mod.id"
          type="button"
          class="group flex min-w-[64px] flex-col items-center justify-center rounded-xl px-2 py-3 text-center transition lg:min-w-0"
          :class="
            currentModule.id === mod.id
              ? 'bg-stone-700 text-white'
              : 'bg-stone-800/70 text-stone-300 hover:bg-stone-700 hover:text-white'
          "
          @click="switchModule(mod.id)"
        >
          <span class="text-lg">{{ mod.icon }}</span>
          <span class="mt-1 text-[11px] font-medium leading-tight">{{ mod.shortName }}</span>
        </button>
      </div>
    </aside>

    <section class="flex min-h-[650px] flex-col overflow-hidden rounded-2xl border border-stone-200 bg-white">
      <header class="border-b border-stone-200 bg-stone-50 px-5 py-4">
        <div class="flex flex-wrap items-center gap-2">
          <span class="inline-flex items-center gap-2 rounded-full border border-stone-300 bg-white px-3 py-1 text-xs font-semibold text-stone-700">
            <span>{{ currentModule.icon }}</span>
            <span>{{ currentModule.name }}</span>
          </span>
          <span class="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800">
            AI Coach
          </span>
        </div>
        <p class="mt-2 text-sm text-stone-600">{{ currentModule.description }}</p>
      </header>

      <div v-if="showCrisisBanner" class="mx-5 mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        <p class="font-semibold">Este posibil să ai nevoie de ajutor imediat.</p>
        <p>Dacă e urgență, sună la 112 sau contactează o linie de suport locală.</p>
      </div>

      <div ref="messagesEl" class="flex-1 space-y-4 overflow-y-auto px-5 py-5">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="max-w-[95%]"
          :class="msg.isUser ? 'ml-auto' : 'mr-auto'"
        >
          <div
            class="rounded-2xl px-4 py-3 text-sm leading-6"
            :class="msg.isUser ? 'rounded-br-md bg-stone-800 text-white' : 'rounded-bl-md bg-stone-100 text-stone-800'"
          >
            {{ msg.message }}
          </div>
        </div>
        <div v-if="loading" class="text-sm text-stone-500">{{ t('common.loading') }}...</div>
      </div>

      <div class="border-t border-stone-200 px-5 py-3">
        <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-stone-500">Quick Actions</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="prompt in currentModule.prompts"
            :key="prompt"
            type="button"
            class="rounded-full border border-stone-300 bg-stone-50 px-3 py-1 text-xs transition hover:bg-stone-100"
            @click="send(prompt)"
          >
            {{ prompt }}
          </button>
        </div>
      </div>

      <form @submit.prevent="send()" class="border-t border-stone-200 bg-white p-4">
        <div class="flex items-end gap-2">
          <textarea
            v-model="input"
            rows="1"
            :placeholder="t('chat.placeholder')"
            class="max-h-40 min-h-[42px] flex-1 resize-y rounded-xl border border-stone-300 px-3 py-2 text-sm outline-none transition focus:border-amber-500 focus:ring-2 focus:ring-amber-200"
          />
          <button
            type="submit"
            :disabled="loading || !input.trim()"
            class="rounded-xl bg-amber-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-amber-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {{ t('chat.send') }}
          </button>
        </div>
      </form>
    </section>

    <aside class="space-y-4 rounded-2xl border border-stone-200 bg-stone-50 p-4">
      <div class="rounded-xl border border-stone-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wider text-stone-500">Streak</p>
        <p class="mt-1 text-3xl font-semibold text-stone-800">7</p>
        <p class="text-sm text-stone-500">zile consecutive</p>
        <div class="mt-3 grid grid-cols-7 gap-1">
          <div
            v-for="i in 7"
            :key="i"
            class="h-2 rounded"
            :class="i <= 6 ? 'bg-emerald-500' : 'bg-amber-500'"
          />
        </div>
      </div>

      <div class="rounded-xl border border-stone-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wider text-stone-500">Mood</p>
        <div class="mt-2 grid grid-cols-4 gap-2">
          <button
            v-for="m in moods"
            :key="m.id"
            type="button"
            class="rounded-md px-2 py-2 text-lg transition"
            :class="selectedMood === m.id ? 'bg-amber-600 text-white' : 'bg-stone-100 hover:bg-stone-200'"
            @click="selectedMood = m.id"
          >
            {{ m.emoji }}
          </button>
        </div>
      </div>

      <div class="rounded-xl border border-stone-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wider text-stone-500">Energy Check-in</p>
        <p class="mb-3 mt-1 text-sm text-stone-600">Nivel energie azi</p>
        <div class="grid grid-cols-5 gap-2">
          <button
            v-for="n in 5"
            :key="n"
            type="button"
            class="rounded border py-1 text-xs"
            :class="
              energyLevel === n
                ? 'border-stone-800 bg-stone-800 text-white'
                : 'border-stone-300 bg-white text-stone-700'
            "
            @click="energyLevel = n"
          >
            {{ n }}
          </button>
        </div>
      </div>

      <div class="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
        Asistentul AI oferă suport complementar, nu înlocuiește un specialist licențiat.
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
interface ChatMessage {
  message: string
  isUser: boolean
}

interface ChatModule {
  id: 'wellness' | 'coaching' | 'education' | 'support'
  icon: string
  shortName: string
  name: string
  description: string
  welcome: string
  prompts: string[]
}

const { t } = useI18n()
const { fetchApi } = useApi()

const modules: ChatModule[] = [
  {
    id: 'wellness',
    icon: '🌿',
    shortName: 'Well',
    name: 'Wellness',
    description: 'Mindfulness, somn, stres si echilibru emotional.',
    welcome: 'Buna! Sunt aici pentru wellness mental. Cum te pot ajuta astazi?',
    prompts: ['Mă simt stresat/ă', 'Exercițiu de respirație', 'Nu pot dormi', '5 minute de calm'],
  },
  {
    id: 'coaching',
    icon: '🎯',
    shortName: 'Coach',
    name: 'Coaching',
    description: 'Obiective, claritate si planuri concrete.',
    welcome: 'Salut! Putem lucra pe un obiectiv clar pentru ziua asta.',
    prompts: ['Setare obiectiv săptămână', 'Cum evit procrastinarea?', 'Plan pe 3 pași'],
  },
  {
    id: 'education',
    icon: '📚',
    shortName: 'Learn',
    name: 'Educatie',
    description: 'Concepte psihologice explicate simplu.',
    welcome: 'Buna! Pot explica pe scurt concepte de psihologie aplicata.',
    prompts: ['Ce este burnout-ul?', 'Cum funcționează anxietatea?', 'Ce inseamna CBT?'],
  },
  {
    id: 'support',
    icon: '🤝',
    shortName: 'Care',
    name: 'Suport',
    description: 'Spatiu sigur pentru descarcare emotionala.',
    welcome: 'Sunt aici sa te ascult, fara judecata. Ce apasa azi pe tine?',
    prompts: ['Am o zi grea', 'Mă simt copleșit/ă', 'Nu stiu ce simt'],
  },
]

const moods = [
  { id: 'low', emoji: '😔' },
  { id: 'ok', emoji: '😐' },
  { id: 'good', emoji: '🙂' },
  { id: 'great', emoji: '😊' },
]

const selectedMood = ref('ok')
const energyLevel = ref(3)
const currentModuleId = ref<ChatModule['id']>('wellness')
const messages = ref<ChatMessage[]>([])
const input = ref('')
const loading = ref(false)
const showCrisisBanner = ref(false)
const messagesEl = ref<HTMLElement | null>(null)

const currentModule = computed(() => modules.find((m) => m.id === currentModuleId.value) || modules[0])

function resetConversation() {
  showCrisisBanner.value = false
  messages.value = [{ message: currentModule.value.welcome, isUser: false }]
}

function switchModule(id: ChatModule['id']) {
  currentModuleId.value = id
  resetConversation()
}

function detectCrisis(text: string): boolean {
  const t = text.toLowerCase()
  return (
    t.includes('suicid') ||
    t.includes('sinucid') ||
    t.includes('self-harm') ||
    t.includes('kill myself')
  )
}

async function send(quickPrompt?: string) {
  const text = (quickPrompt || input.value).trim()
  if (!text || loading.value) return

  messages.value.push({ message: text, isUser: true })
  input.value = ''
  loading.value = true
  try {
    const res = await fetchApi<{ reply: string }>('/chat/send', {
      method: 'POST',
      body: {
        message: `[${currentModule.value.name}|mood:${selectedMood.value}|energy:${energyLevel.value}] ${text}`,
      },
    })
    messages.value.push({ message: res.reply, isUser: false })
    if (detectCrisis(res.reply)) {
      showCrisisBanner.value = true
    }
  } catch (e) {
    messages.value.push({
      message: (e as Error).message || 'Error sending message',
      isUser: false,
    })
  } finally {
    loading.value = false
    nextTick(() => {
      if (messagesEl.value) {
        messagesEl.value.scrollTop = messagesEl.value.scrollHeight
      }
    })
  }
}

onMounted(() => {
  resetConversation()
})
</script>
