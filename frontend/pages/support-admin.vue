<template>
  <div class="mx-auto max-w-6xl space-y-5">
    <header class="space-y-2">
      <h1 class="text-2xl font-bold text-stone-900">{{ text.title }}</h1>
      <p class="text-sm text-stone-600">{{ text.subtitle }}</p>
    </header>

    <div v-if="!isAdmin" class="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
      {{ text.forbidden }}
    </div>

    <div v-else class="grid gap-4 lg:grid-cols-[340px,1fr]">
      <section class="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
        <div class="mb-3 flex items-center justify-between gap-3">
          <h2 class="text-sm font-semibold text-stone-900">{{ text.ticketList }}</h2>
          <button
            type="button"
            class="rounded-full border border-stone-300 px-3 py-1 text-xs font-semibold text-stone-700 hover:bg-stone-50"
            @click="loadTickets"
          >
            {{ text.refresh }}
          </button>
        </div>

        <div class="space-y-2 max-h-[70vh] overflow-auto pr-1">
          <button
            v-for="ticket in tickets"
            :key="ticket.id"
            type="button"
            class="w-full rounded-xl border p-3 text-left transition"
            :class="activeTicket?.id === ticket.id ? 'border-stone-900 bg-stone-50' : 'border-stone-200 bg-white hover:border-stone-300'"
            @click="loadTicket(ticket.id)"
          >
            <div class="flex items-center justify-between gap-2">
              <p class="text-xs font-semibold text-stone-900">#{{ ticket.id }} · {{ ticket.user_email }}</p>
              <span class="rounded-full border px-2 py-0.5 text-[11px] font-semibold" :class="statusBadgeClass(ticket.status)">
                {{ statusLabel(ticket.status) }}
              </span>
            </div>
            <p class="mt-1 line-clamp-2 text-xs text-stone-700">{{ ticket.subject }}</p>
            <p class="mt-1 text-[11px] text-stone-500">{{ formatDate(ticket.updated_at) }}</p>
          </button>
          <p v-if="!tickets.length && !loadingTickets" class="text-xs text-stone-500">{{ text.empty }}</p>
          <p v-if="loadingTickets" class="text-xs text-stone-500">{{ text.loading }}</p>
        </div>
      </section>

      <section class="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
        <div v-if="!activeTicket" class="py-10 text-center text-sm text-stone-500">{{ text.selectTicket }}</div>

        <div v-else class="space-y-4">
          <div class="border-b border-stone-200 pb-3">
            <h3 class="text-sm font-semibold text-stone-900">#{{ activeTicket.id }} · {{ activeTicket.subject }}</h3>
            <p class="text-xs text-stone-500">{{ activeTicket.user_email }} · {{ formatDate(activeTicket.created_at) }}</p>
          </div>

          <div class="space-y-2 max-h-[52vh] overflow-auto rounded-xl border border-stone-200 bg-stone-50 p-3">
            <article
              v-for="row in activeTicket.messages || []"
              :key="row.id"
              class="rounded-lg border p-3"
              :class="row.sender_role === 'admin' ? 'border-indigo-200 bg-indigo-50' : row.is_internal ? 'border-amber-200 bg-amber-50' : 'border-stone-200 bg-white'"
            >
              <div class="mb-1 flex items-center justify-between gap-2 text-[11px]">
                <span class="font-semibold text-stone-700">{{ roleLabel(row.sender_role, row.is_internal) }}</span>
                <span class="text-stone-500">{{ formatDate(row.created_at) }}</span>
              </div>
              <p class="whitespace-pre-wrap text-sm text-stone-800">{{ row.message }}</p>
            </article>
          </div>

          <div class="grid gap-3 sm:grid-cols-2">
            <div>
              <label class="mb-1 block text-xs font-semibold text-stone-700">{{ text.status }}</label>
              <select v-model="replyStatus" class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800">
                <option value="open">{{ statusLabel('open') }}</option>
                <option value="in_progress">{{ statusLabel('in_progress') }}</option>
                <option value="resolved">{{ statusLabel('resolved') }}</option>
              </select>
            </div>
            <label class="mt-6 inline-flex items-center gap-2 text-xs text-stone-700">
              <input v-model="replyInternal" type="checkbox" class="h-4 w-4 rounded border-stone-300" />
              {{ text.internalNote }}
            </label>
          </div>

          <div>
            <label class="mb-1 block text-xs font-semibold text-stone-700">{{ text.reply }}</label>
            <textarea
              v-model="replyMessage"
              rows="5"
              class="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 text-sm text-stone-800 focus:border-stone-500 focus:outline-none"
              :placeholder="text.replyPlaceholder"
            />
          </div>

          <p v-if="replyError" class="text-sm text-red-700">{{ replyError }}</p>
          <p v-if="replySuccess" class="text-sm text-emerald-700">{{ text.replySent }}</p>

          <button
            type="button"
            :disabled="sendingReply"
            class="rounded-full bg-stone-900 px-5 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
            @click="sendReply"
          >
            {{ sendingReply ? text.sending : text.send }}
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

type TicketStatus = 'open' | 'in_progress' | 'resolved'
type TicketMessage = {
  id: number
  sender_role: 'user' | 'admin' | 'system'
  message: string
  is_internal: boolean
  created_at: string
}

type Ticket = {
  id: number
  subject: string
  message: string
  user_email: string
  status: TicketStatus
  created_at: string
  updated_at: string
  messages?: TicketMessage[]
}

const { fetchApi } = useApi()
const { locale } = useI18n()
const authStore = useAuthStore()

const tickets = ref<Ticket[]>([])
const activeTicket = ref<Ticket | null>(null)
const loadingTickets = ref(false)
const sendingReply = ref(false)
const replyMessage = ref('')
const replyStatus = ref<TicketStatus>('in_progress')
const replyInternal = ref(false)
const replyError = ref('')
const replySuccess = ref(false)

const isAdmin = computed(() => Boolean(authStore.user?.is_superuser))

const text = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return {
    ro: {
      title: 'Administrare suport tickets',
      subtitle: 'Raspunde utilizatorilor direct din platforma.',
      forbidden: 'Ai nevoie de drepturi de administrator pentru aceasta pagina.',
      ticketList: 'Ticket-uri',
      refresh: 'Reincarca',
      empty: 'Nu exista ticket-uri.',
      loading: 'Se incarca...',
      selectTicket: 'Selecteaza un ticket pentru a vedea conversatia.',
      status: 'Status',
      internalNote: 'Nota interna (nu este vizibila utilizatorului)',
      reply: 'Raspuns',
      replyPlaceholder: 'Scrie un raspuns catre utilizator...',
      replySent: 'Raspuns trimis.',
      sending: 'Se trimite...',
      send: 'Trimite raspuns',
      replyRequired: 'Mesajul este obligatoriu.',
      replyError: 'Nu am putut trimite raspunsul.',
      roleUser: 'Utilizator',
      roleAdmin: 'Admin',
      roleInternal: 'Nota interna',
      statusOpen: 'deschis',
      statusProgress: 'in lucru',
      statusResolved: 'rezolvat',
    },
    en: {
      title: 'Support tickets administration',
      subtitle: 'Reply to users directly from the platform.',
      forbidden: 'You need administrator rights for this page.',
      ticketList: 'Tickets',
      refresh: 'Refresh',
      empty: 'No tickets found.',
      loading: 'Loading...',
      selectTicket: 'Select a ticket to view the conversation.',
      status: 'Status',
      internalNote: 'Internal note (not visible to user)',
      reply: 'Reply',
      replyPlaceholder: 'Write a reply to the user...',
      replySent: 'Reply sent.',
      sending: 'Sending...',
      send: 'Send reply',
      replyRequired: 'Message is required.',
      replyError: 'Could not send reply.',
      roleUser: 'User',
      roleAdmin: 'Admin',
      roleInternal: 'Internal note',
      statusOpen: 'open',
      statusProgress: 'in progress',
      statusResolved: 'resolved',
    },
  }[code] || {
    title: 'Support tickets administration',
    subtitle: 'Reply to users directly from the platform.',
    forbidden: 'You need administrator rights for this page.',
    ticketList: 'Tickets',
    refresh: 'Refresh',
    empty: 'No tickets found.',
    loading: 'Loading...',
    selectTicket: 'Select a ticket to view the conversation.',
    status: 'Status',
    internalNote: 'Internal note (not visible to user)',
    reply: 'Reply',
    replyPlaceholder: 'Write a reply to the user...',
    replySent: 'Reply sent.',
    sending: 'Sending...',
    send: 'Send reply',
    replyRequired: 'Message is required.',
    replyError: 'Could not send reply.',
    roleUser: 'User',
    roleAdmin: 'Admin',
    roleInternal: 'Internal note',
    statusOpen: 'open',
    statusProgress: 'in progress',
    statusResolved: 'resolved',
  }
})

function formatDate(value: string) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString(locale.value)
}

function statusLabel(status: TicketStatus) {
  if (status === 'resolved') return text.value.statusResolved
  if (status === 'in_progress') return text.value.statusProgress
  return text.value.statusOpen
}

function statusBadgeClass(status: TicketStatus) {
  if (status === 'resolved') return 'border-emerald-300 bg-emerald-50 text-emerald-700'
  if (status === 'in_progress') return 'border-amber-300 bg-amber-50 text-amber-800'
  return 'border-sky-300 bg-sky-50 text-sky-800'
}

function roleLabel(role: TicketMessage['sender_role'], isInternal: boolean) {
  if (isInternal) return text.value.roleInternal
  if (role === 'admin') return text.value.roleAdmin
  return text.value.roleUser
}

async function loadTickets() {
  if (!isAdmin.value) return
  loadingTickets.value = true
  try {
    const data = await fetchApi<{ items: Ticket[] }>('/support/admin/tickets')
    tickets.value = data.items || []
  } finally {
    loadingTickets.value = false
  }
}

async function loadTicket(ticketId: number) {
  if (!isAdmin.value) return
  const data = await fetchApi<Ticket>(`/support/tickets/${ticketId}`)
  activeTicket.value = data
  replyStatus.value = data.status
  replyError.value = ''
  replySuccess.value = false
}

async function sendReply() {
  if (!activeTicket.value) return
  replyError.value = ''
  replySuccess.value = false

  if (!replyMessage.value.trim()) {
    replyError.value = text.value.replyRequired
    return
  }

  sendingReply.value = true
  try {
    const response = await fetchApi<{ ticket: Ticket }>(`/support/tickets/${activeTicket.value.id}`, {
      method: 'POST',
      body: {
        message: replyMessage.value,
        status: replyStatus.value,
        is_internal: replyInternal.value,
      },
    })
    activeTicket.value = response.ticket
    replyMessage.value = ''
    replyInternal.value = false
    replySuccess.value = true
    await loadTickets()
  } catch {
    replyError.value = text.value.replyError
  } finally {
    sendingReply.value = false
  }
}

onMounted(async () => {
  await authStore.hydrate()
  await loadTickets()
})
</script>
