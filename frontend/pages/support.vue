<template>
  <div class="mx-auto max-w-3xl space-y-6">
    <header class="space-y-2">
      <h1 class="text-2xl font-bold text-stone-900">{{ text.title }}</h1>
      <p class="text-sm text-stone-600">{{ text.subtitle }}</p>
    </header>

    <section class="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm space-y-4">
      <div>
        <label class="mb-1 block text-sm font-medium text-stone-700">{{ text.subject }}</label>
        <input
          v-model="subject"
          type="text"
          class="w-full rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm text-stone-800 focus:border-stone-500 focus:outline-none"
          :placeholder="text.subjectPlaceholder"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium text-stone-700">{{ text.message }}</label>
        <textarea
          v-model="message"
          rows="5"
          class="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 text-sm text-stone-800 focus:border-stone-500 focus:outline-none"
          :placeholder="text.messagePlaceholder"
        />
      </div>
      <p v-if="error" class="text-sm text-red-700">{{ error }}</p>
      <p v-if="success" class="text-sm text-emerald-700">{{ text.success }}</p>
      <button
        type="button"
        :disabled="sending"
        class="rounded-full bg-stone-900 px-5 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
        @click="createTicket"
      >
        {{ sending ? text.sending : text.submit }}
      </button>
    </section>

    <section class="space-y-3">
      <h2 class="text-lg font-semibold text-stone-900">{{ text.history }}</h2>
      <div v-if="loading" class="text-sm text-stone-500">{{ text.loading }}</div>
      <div v-else-if="tickets.length === 0" class="rounded-xl border border-stone-200 bg-stone-50 p-4 text-sm text-stone-600">
        {{ text.empty }}
      </div>
      <article
        v-for="ticket in tickets"
        :key="ticket.id"
        class="rounded-xl border border-stone-200 bg-white p-4"
      >
        <div class="flex items-center justify-between gap-3">
          <h3 class="text-sm font-semibold text-stone-900">#{{ ticket.id }} · {{ ticket.subject }}</h3>
          <span class="rounded-full border px-2 py-0.5 text-xs font-semibold"
            :class="ticket.status === 'resolved' ? 'border-emerald-300 bg-emerald-50 text-emerald-700' : ticket.status === 'in_progress' ? 'border-amber-300 bg-amber-50 text-amber-800' : 'border-sky-300 bg-sky-50 text-sky-800'"
          >
            {{ statusLabel(ticket.status) }}
          </span>
        </div>
        <p class="mt-2 text-sm text-stone-700 whitespace-pre-wrap">{{ ticket.message }}</p>
        <p class="mt-2 text-xs text-stone-500">{{ formatDate(ticket.created_at) }}</p>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

type Ticket = {
  id: number
  subject: string
  message: string
  status: 'open' | 'in_progress' | 'resolved'
  created_at: string
}

const { fetchApi } = useApi()
const { locale } = useI18n()

const subject = ref('')
const message = ref('')
const error = ref('')
const success = ref(false)
const sending = ref(false)
const loading = ref(true)
const tickets = ref<Ticket[]>([])

const text = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  if (code === 'ro') {
    return {
      title: 'Support tickets',
      subtitle: 'Deschide un ticket direct din contul tau pentru probleme tehnice sau comerciale.',
      subject: 'Subiect',
      subjectPlaceholder: 'Ex: Nu pot finaliza checkout-ul',
      message: 'Mesaj',
      messagePlaceholder: 'Descrie problema, pasi de reproducere si ce ai incercat deja.',
      submit: 'Trimite ticket',
      sending: 'Se trimite...',
      success: 'Ticket creat cu succes.',
      history: 'Istoric ticket-uri',
      loading: 'Se incarca istoricul...',
      empty: 'Nu ai inca ticket-uri deschise.',
    }
  }
  return {
    title: 'Support tickets',
    subtitle: 'Open a ticket from your account for technical or billing issues.',
    subject: 'Subject',
    subjectPlaceholder: 'Example: I cannot complete checkout',
    message: 'Message',
    messagePlaceholder: 'Describe the issue, steps to reproduce, and what you already tried.',
    submit: 'Submit ticket',
    sending: 'Submitting...',
    success: 'Ticket created successfully.',
    history: 'Ticket history',
    loading: 'Loading history...',
    empty: 'You do not have support tickets yet.',
  }
})

function formatDate(value: string) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

function statusLabel(status: Ticket['status']) {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  const ro = { open: 'deschis', in_progress: 'in lucru', resolved: 'rezolvat' }
  const en = { open: 'open', in_progress: 'in progress', resolved: 'resolved' }
  return (code === 'ro' ? ro : en)[status]
}

async function loadTickets() {
  loading.value = true
  try {
    const data = await fetchApi<{ items: Ticket[] }>('/support/tickets')
    tickets.value = data.items || []
  } finally {
    loading.value = false
  }
}

async function createTicket() {
  error.value = ''
  success.value = false
  if (!subject.value.trim() || !message.value.trim()) {
    error.value = 'Subject and message are required.'
    return
  }

  sending.value = true
  try {
    await fetchApi('/support/tickets', {
      method: 'POST',
      body: {
        subject: subject.value,
        message: message.value,
      },
    })
    subject.value = ''
    message.value = ''
    success.value = true
    await loadTickets()
  } catch {
    error.value = 'Unable to create ticket right now.'
  } finally {
    sending.value = false
  }
}

onMounted(loadTickets)
</script>
