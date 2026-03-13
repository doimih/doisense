<template>
  <div class="mx-auto max-w-6xl space-y-8">

    <!-- ── User: Create ticket + history ── -->
    <div class="mx-auto max-w-3xl w-full space-y-6">
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
              {{ userStatusLabel(ticket.status) }}
            </span>
          </div>
          <p class="mt-2 text-sm text-stone-700 whitespace-pre-wrap">{{ ticket.message }}</p>
          <div class="mt-3 flex items-center justify-between gap-2">
            <p class="text-xs text-stone-500">{{ formatDate(ticket.created_at) }}</p>
            <button
              type="button"
              class="rounded-full border border-stone-300 px-3 py-1 text-xs font-semibold text-stone-700 hover:bg-stone-50"
              @click="openConversation(ticket.id)"
            >
              {{ text.openConversation }}
            </button>
          </div>
        </article>

        <article v-if="activeTicket" class="rounded-xl border border-stone-200 bg-white p-4">
          <h3 class="text-sm font-semibold text-stone-900">{{ text.conversationTitle }} · #{{ activeTicket.id }}</h3>
          <div class="mt-3 space-y-2 max-h-72 overflow-auto rounded-xl border border-stone-200 bg-stone-50 p-3">
            <div
              v-for="row in activeTicket.messages || []"
              :key="row.id"
              class="rounded-lg border border-stone-200 bg-white p-3"
            >
              <div class="mb-1 flex items-center justify-between gap-2 text-[11px] text-stone-500">
                <span class="font-semibold text-stone-700">{{ messageRoleLabel(row.sender_role) }}</span>
                <span>{{ formatDate(row.created_at) }}</span>
              </div>
              <p class="whitespace-pre-wrap text-sm text-stone-800">{{ row.message }}</p>
            </div>
          </div>

          <div class="mt-3">
            <label class="mb-1 block text-sm font-medium text-stone-700">{{ text.yourReply }}</label>
            <textarea
              v-model="replyMessage"
              rows="4"
              class="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 text-sm text-stone-800 focus:border-stone-500 focus:outline-none"
              :placeholder="text.yourReplyPlaceholder"
            />
          </div>
          <p v-if="replyError" class="mt-2 text-sm text-red-700">{{ replyError }}</p>
          <p v-if="replySuccess" class="mt-2 text-sm text-emerald-700">{{ text.replySent }}</p>
          <button
            type="button"
            :disabled="replySending"
            class="mt-3 rounded-full bg-stone-900 px-5 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
            @click="sendReply"
          >
            {{ replySending ? text.sendingReply : text.sendReply }}
          </button>
        </article>
      </section>
    </div>

    <!-- ── Admin: Support tickets management ── -->
    <template v-if="isAdmin">
      <hr class="border-stone-200" />

      <div class="space-y-5">
        <header class="space-y-2">
          <h2 class="text-xl font-bold text-stone-900">{{ adminText.title }}</h2>
          <p class="text-sm text-stone-600">{{ adminText.subtitle }}</p>
        </header>

        <div class="grid gap-4 lg:grid-cols-[340px,1fr]">
          <section class="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
            <div class="mb-3 flex items-center justify-between gap-3">
              <h3 class="text-sm font-semibold text-stone-900">{{ adminText.ticketList }}</h3>
              <button
                type="button"
                class="rounded-full border border-stone-300 px-3 py-1 text-xs font-semibold text-stone-700 hover:bg-stone-50"
                @click="adminLoadTickets"
              >
                {{ adminText.refresh }}
              </button>
            </div>

            <div class="space-y-2 max-h-[70vh] overflow-auto pr-1">
              <button
                v-for="ticket in adminTickets"
                :key="ticket.id"
                type="button"
                class="w-full rounded-xl border p-3 text-left transition"
                :class="adminActiveTicket?.id === ticket.id ? 'border-stone-900 bg-stone-50' : 'border-stone-200 bg-white hover:border-stone-300'"
                @click="loadAdminTicket(ticket.id)"
              >
                <div class="flex items-center justify-between gap-2">
                  <p class="text-xs font-semibold text-stone-900">#{{ ticket.id }} · {{ ticket.user_email }}</p>
                  <span class="rounded-full border px-2 py-0.5 text-[11px] font-semibold" :class="adminStatusBadgeClass(ticket.status)">
                    {{ adminStatusLabel(ticket.status) }}
                  </span>
                </div>
                <p class="mt-1 line-clamp-2 text-xs text-stone-700">{{ ticket.subject }}</p>
                <p class="mt-1 text-[11px] text-stone-500">{{ formatDate(ticket.updated_at) }}</p>
              </button>
              <p v-if="!adminTickets.length && !adminLoadingTickets" class="text-xs text-stone-500">{{ adminText.empty }}</p>
              <p v-if="adminLoadingTickets" class="text-xs text-stone-500">{{ adminText.loading }}</p>
            </div>
          </section>

          <section class="rounded-2xl border border-stone-200 bg-white p-4 shadow-sm">
            <div v-if="!adminActiveTicket" class="py-10 text-center text-sm text-stone-500">{{ adminText.selectTicket }}</div>

            <div v-else class="space-y-4">
              <div class="border-b border-stone-200 pb-3">
                <h3 class="text-sm font-semibold text-stone-900">#{{ adminActiveTicket.id }} · {{ adminActiveTicket.subject }}</h3>
                <p class="text-xs text-stone-500">{{ adminActiveTicket.user_email }} · {{ formatDate(adminActiveTicket.created_at) }}</p>
              </div>

              <div class="space-y-2 max-h-[52vh] overflow-auto rounded-xl border border-stone-200 bg-stone-50 p-3">
                <article
                  v-for="row in adminActiveTicket.messages || []"
                  :key="row.id"
                  class="rounded-lg border p-3"
                  :class="row.sender_role === 'admin' ? 'border-indigo-200 bg-indigo-50' : row.is_internal ? 'border-amber-200 bg-amber-50' : 'border-stone-200 bg-white'"
                >
                  <div class="mb-1 flex items-center justify-between gap-2 text-[11px]">
                    <span class="font-semibold text-stone-700">{{ adminRoleLabel(row.sender_role, row.is_internal) }}</span>
                    <span class="text-stone-500">{{ formatDate(row.created_at) }}</span>
                  </div>
                  <p class="whitespace-pre-wrap text-sm text-stone-800">{{ row.message }}</p>
                </article>
              </div>

              <div class="grid gap-3 sm:grid-cols-2">
                <div>
                  <label class="mb-1 block text-xs font-semibold text-stone-700">{{ adminText.status }}</label>
                  <select v-model="adminReplyStatus" class="w-full rounded-lg border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800">
                    <option value="open">{{ adminStatusLabel('open') }}</option>
                    <option value="in_progress">{{ adminStatusLabel('in_progress') }}</option>
                    <option value="resolved">{{ adminStatusLabel('resolved') }}</option>
                  </select>
                </div>
                <label class="mt-6 inline-flex items-center gap-2 text-xs text-stone-700">
                  <input v-model="adminReplyInternal" type="checkbox" class="h-4 w-4 rounded border-stone-300" />
                  {{ adminText.internalNote }}
                </label>
              </div>

              <div>
                <label class="mb-1 block text-xs font-semibold text-stone-700">{{ adminText.reply }}</label>
                <textarea
                  v-model="adminReplyMessage"
                  rows="5"
                  class="w-full rounded-xl border border-stone-300 bg-white px-4 py-3 text-sm text-stone-800 focus:border-stone-500 focus:outline-none"
                  :placeholder="adminText.replyPlaceholder"
                />
              </div>

              <p v-if="adminReplyError" class="text-sm text-red-700">{{ adminReplyError }}</p>
              <p v-if="adminReplySuccess" class="text-sm text-emerald-700">{{ adminText.replySent }}</p>

              <button
                type="button"
                :disabled="adminSendingReply"
                class="rounded-full bg-stone-900 px-5 py-2 text-sm font-semibold text-white hover:bg-black disabled:opacity-50"
                @click="sendAdminReply"
              >
                {{ adminSendingReply ? adminText.sending : adminText.send }}
              </button>
            </div>
          </section>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth' })

// ── Shared types ──────────────────────────────────────────────
type TicketStatus = 'open' | 'in_progress' | 'resolved'

type TicketMessage = {
  id: number
  sender_role: 'user' | 'admin' | 'system'
  message: string
  is_internal: boolean
  created_at: string
}

type UserTicket = {
  id: number
  subject: string
  message: string
  status: TicketStatus
  created_at: string
  updated_at?: string
  messages?: TicketMessage[]
}

type AdminTicket = {
  id: number
  subject: string
  message: string
  user_email: string
  status: TicketStatus
  created_at: string
  updated_at: string
  messages?: TicketMessage[]
}

// ── Composables ───────────────────────────────────────────────
const { fetchApi } = useApi()
const { locale } = useI18n()
const authStore = useAuthStore()

const isAdmin = computed(() => Boolean(authStore.user?.is_superuser))

// ── Shared helpers ────────────────────────────────────────────
function formatDate(value: string) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString(locale.value)
}

// ── User section state ────────────────────────────────────────
const subject = ref('')
const message = ref('')
const error = ref('')
const success = ref(false)
const sending = ref(false)
const loading = ref(true)
const tickets = ref<UserTicket[]>([])
const activeTicket = ref<UserTicket | null>(null)
const replyMessage = ref('')
const replySending = ref(false)
const replyError = ref('')
const replySuccess = ref(false)

const text = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return {
    ro: {
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
      requiredError: 'Subiectul si mesajul sunt obligatorii.',
      createError: 'Nu am putut crea ticket-ul acum.',
      openConversation: 'Deschide conversatia',
      conversationTitle: 'Conversatie ticket',
      yourReply: 'Mesajul tau',
      yourReplyPlaceholder: 'Scrie un update pentru echipa de suport...',
      sendReply: 'Trimite raspuns',
      sendingReply: 'Se trimite raspunsul...',
      replySent: 'Raspuns trimis.',
      replyRequired: 'Mesajul este obligatoriu.',
      replyError: 'Nu am putut trimite raspunsul.',
      roleUser: 'Tu',
      roleAdmin: 'Suport',
    },
    en: {
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
      requiredError: 'Subject and message are required.',
      createError: 'Unable to create ticket right now.',
      openConversation: 'Open conversation',
      conversationTitle: 'Ticket conversation',
      yourReply: 'Your message',
      yourReplyPlaceholder: 'Write an update for the support team...',
      sendReply: 'Send reply',
      sendingReply: 'Sending reply...',
      replySent: 'Reply sent.',
      replyRequired: 'Message is required.',
      replyError: 'Unable to send reply right now.',
      roleUser: 'You',
      roleAdmin: 'Support',
    },
    de: {
      title: 'Support-Tickets',
      subtitle: 'Erstelle direkt in deinem Konto ein Ticket fuer technische oder Abrechnungsprobleme.',
      subject: 'Betreff',
      subjectPlaceholder: 'Beispiel: Ich kann den Checkout nicht abschliessen',
      message: 'Nachricht',
      messagePlaceholder: 'Beschreibe das Problem, die Schritte zur Reproduktion und was du bereits versucht hast.',
      submit: 'Ticket senden',
      sending: 'Wird gesendet...',
      success: 'Ticket erfolgreich erstellt.',
      history: 'Ticketverlauf',
      loading: 'Verlauf wird geladen...',
      empty: 'Noch keine Tickets vorhanden.',
      requiredError: 'Betreff und Nachricht sind erforderlich.',
      createError: 'Ticket konnte derzeit nicht erstellt werden.',
      openConversation: 'Konversation oeffnen',
      conversationTitle: 'Ticket-Konversation',
      yourReply: 'Deine Nachricht',
      yourReplyPlaceholder: 'Schreibe ein Update fuer das Support-Team...',
      sendReply: 'Antwort senden',
      sendingReply: 'Antwort wird gesendet...',
      replySent: 'Antwort gesendet.',
      replyRequired: 'Nachricht ist erforderlich.',
      replyError: 'Antwort konnte nicht gesendet werden.',
      roleUser: 'Du',
      roleAdmin: 'Support',
    },
    fr: {
      title: 'Tickets de support',
      subtitle: 'Ouvrez un ticket depuis votre compte pour des problemes techniques ou de facturation.',
      subject: 'Sujet',
      subjectPlaceholder: 'Exemple : impossible de terminer le paiement',
      message: 'Message',
      messagePlaceholder: 'Decrivez le probleme, les etapes de reproduction et ce que vous avez deja essaye.',
      submit: 'Envoyer le ticket',
      sending: 'Envoi en cours...',
      success: 'Ticket cree avec succes.',
      history: 'Historique des tickets',
      loading: 'Chargement de l\'historique...',
      empty: 'Vous n\'avez pas encore de tickets.',
      requiredError: 'Le sujet et le message sont obligatoires.',
      createError: 'Impossible de creer un ticket pour le moment.',
      openConversation: 'Ouvrir la conversation',
      conversationTitle: 'Conversation du ticket',
      yourReply: 'Votre message',
      yourReplyPlaceholder: 'Ecrivez une mise a jour pour le support...',
      sendReply: 'Envoyer la reponse',
      sendingReply: 'Envoi de la reponse...',
      replySent: 'Reponse envoyee.',
      replyRequired: 'Le message est obligatoire.',
      replyError: 'Impossible d envoyer la reponse.',
      roleUser: 'Vous',
      roleAdmin: 'Support',
    },
    it: {
      title: 'Ticket di supporto',
      subtitle: 'Apri un ticket dal tuo account per problemi tecnici o di pagamento.',
      subject: 'Oggetto',
      subjectPlaceholder: 'Esempio: non riesco a completare il checkout',
      message: 'Messaggio',
      messagePlaceholder: 'Descrivi il problema, i passaggi per riprodurlo e cosa hai gia provato.',
      submit: 'Invia ticket',
      sending: 'Invio in corso...',
      success: 'Ticket creato con successo.',
      history: 'Storico ticket',
      loading: 'Caricamento storico...',
      empty: 'Non hai ancora ticket di supporto.',
      requiredError: 'Oggetto e messaggio sono obbligatori.',
      createError: 'Impossibile creare il ticket in questo momento.',
      openConversation: 'Apri conversazione',
      conversationTitle: 'Conversazione ticket',
      yourReply: 'Il tuo messaggio',
      yourReplyPlaceholder: 'Scrivi un aggiornamento per il supporto...',
      sendReply: 'Invia risposta',
      sendingReply: 'Invio risposta...',
      replySent: 'Risposta inviata.',
      replyRequired: 'Il messaggio e obbligatorio.',
      replyError: 'Impossibile inviare la risposta.',
      roleUser: 'Tu',
      roleAdmin: 'Supporto',
    },
    es: {
      title: 'Tickets de soporte',
      subtitle: 'Abre un ticket desde tu cuenta para problemas tecnicos o de facturacion.',
      subject: 'Asunto',
      subjectPlaceholder: 'Ejemplo: no puedo finalizar el checkout',
      message: 'Mensaje',
      messagePlaceholder: 'Describe el problema, los pasos para reproducirlo y lo que ya intentaste.',
      submit: 'Enviar ticket',
      sending: 'Enviando...',
      success: 'Ticket creado correctamente.',
      history: 'Historial de tickets',
      loading: 'Cargando historial...',
      empty: 'Aun no tienes tickets de soporte.',
      requiredError: 'El asunto y el mensaje son obligatorios.',
      createError: 'No se pudo crear el ticket ahora.',
      openConversation: 'Abrir conversacion',
      conversationTitle: 'Conversacion del ticket',
      yourReply: 'Tu mensaje',
      yourReplyPlaceholder: 'Escribe una actualizacion para soporte...',
      sendReply: 'Enviar respuesta',
      sendingReply: 'Enviando respuesta...',
      replySent: 'Respuesta enviada.',
      replyRequired: 'El mensaje es obligatorio.',
      replyError: 'No se pudo enviar la respuesta.',
      roleUser: 'Tu',
      roleAdmin: 'Soporte',
    },
    pl: {
      title: 'Zgloszenia wsparcia',
      subtitle: 'Utworz zgloszenie z konta w sprawach technicznych lub rozliczeniowych.',
      subject: 'Temat',
      subjectPlaceholder: 'Przyklad: nie moge dokonczyc checkoutu',
      message: 'Wiadomosc',
      messagePlaceholder: 'Opisz problem, kroki odtworzenia i to, co juz zostalo sprawdzone.',
      submit: 'Wyslij zgloszenie',
      sending: 'Wysylanie...',
      success: 'Zgloszenie utworzone pomyslnie.',
      history: 'Historia zgloszen',
      loading: 'Ladowanie historii...',
      empty: 'Nie masz jeszcze zgloszen.',
      requiredError: 'Temat i wiadomosc sa wymagane.',
      createError: 'Nie mozna teraz utworzyc zgloszenia.',
      openConversation: 'Otworz rozmowe',
      conversationTitle: 'Rozmowa w zgloszeniu',
      yourReply: 'Twoja wiadomosc',
      yourReplyPlaceholder: 'Napisz aktualizacje dla zespolu wsparcia...',
      sendReply: 'Wyslij odpowiedz',
      sendingReply: 'Wysylanie odpowiedzi...',
      replySent: 'Odpowiedz wyslana.',
      replyRequired: 'Wiadomosc jest wymagana.',
      replyError: 'Nie mozna wyslac odpowiedzi.',
      roleUser: 'Ty',
      roleAdmin: 'Wsparcie',
    },
  }[code] || {
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
    requiredError: 'Subject and message are required.',
    createError: 'Unable to create ticket right now.',
    openConversation: 'Open conversation',
    conversationTitle: 'Ticket conversation',
    yourReply: 'Your message',
    yourReplyPlaceholder: 'Write an update for the support team...',
    sendReply: 'Send reply',
    sendingReply: 'Sending reply...',
    replySent: 'Reply sent.',
    replyRequired: 'Message is required.',
    replyError: 'Unable to send reply right now.',
    roleUser: 'You',
    roleAdmin: 'Support',
  }
})

function userStatusLabel(status: TicketStatus) {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  const byLanguage: Record<string, Record<TicketStatus, string>> = {
    ro: { open: 'deschis', in_progress: 'in lucru', resolved: 'rezolvat' },
    en: { open: 'open', in_progress: 'in progress', resolved: 'resolved' },
    de: { open: 'offen', in_progress: 'in bearbeitung', resolved: 'geloest' },
    fr: { open: 'ouvert', in_progress: 'en cours', resolved: 'resolu' },
    it: { open: 'aperto', in_progress: 'in lavorazione', resolved: 'risolto' },
    es: { open: 'abierto', in_progress: 'en progreso', resolved: 'resuelto' },
    pl: { open: 'otwarte', in_progress: 'w toku', resolved: 'rozwiazane' },
  }
  return (byLanguage[code] || byLanguage.en)[status]
}

function messageRoleLabel(role: TicketMessage['sender_role']) {
  return role === 'admin' ? text.value.roleAdmin : text.value.roleUser
}

async function loadTickets() {
  loading.value = true
  try {
    const data = await fetchApi<{ items: UserTicket[] }>('/support/tickets')
    tickets.value = data.items || []
  } finally {
    loading.value = false
  }
}

async function openConversation(ticketId: number) {
  const data = await fetchApi<UserTicket>(`/support/tickets/${ticketId}`)
  activeTicket.value = data
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
  replySending.value = true
  try {
    const response = await fetchApi<{ ticket: UserTicket }>(`/support/tickets/${activeTicket.value.id}`, {
      method: 'POST',
      body: { message: replyMessage.value },
    })
    activeTicket.value = response.ticket
    replyMessage.value = ''
    replySuccess.value = true
    await loadTickets()
  } catch {
    replyError.value = text.value.replyError
  } finally {
    replySending.value = false
  }
}

async function createTicket() {
  error.value = ''
  success.value = false
  if (!subject.value.trim() || !message.value.trim()) {
    error.value = text.value.requiredError
    return
  }
  sending.value = true
  try {
    await fetchApi('/support/tickets', {
      method: 'POST',
      body: { subject: subject.value, message: message.value },
    })
    subject.value = ''
    message.value = ''
    success.value = true
    await loadTickets()
  } catch {
    error.value = text.value.createError
  } finally {
    sending.value = false
  }
}

// ── Admin section state ────────────────────────────────────────
const adminTickets = ref<AdminTicket[]>([])
const adminActiveTicket = ref<AdminTicket | null>(null)
const adminLoadingTickets = ref(false)
const adminSendingReply = ref(false)
const adminReplyMessage = ref('')
const adminReplyStatus = ref<TicketStatus>('in_progress')
const adminReplyInternal = ref(false)
const adminReplyError = ref('')
const adminReplySuccess = ref(false)

const adminText = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return {
    ro: {
      title: 'Administrare suport tickets',
      subtitle: 'Raspunde utilizatorilor direct din platforma.',
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

function adminStatusLabel(status: TicketStatus) {
  if (status === 'resolved') return adminText.value.statusResolved
  if (status === 'in_progress') return adminText.value.statusProgress
  return adminText.value.statusOpen
}

function adminStatusBadgeClass(status: TicketStatus) {
  if (status === 'resolved') return 'border-emerald-300 bg-emerald-50 text-emerald-700'
  if (status === 'in_progress') return 'border-amber-300 bg-amber-50 text-amber-800'
  return 'border-sky-300 bg-sky-50 text-sky-800'
}

function adminRoleLabel(role: TicketMessage['sender_role'], isInternal: boolean) {
  if (isInternal) return adminText.value.roleInternal
  if (role === 'admin') return adminText.value.roleAdmin
  return adminText.value.roleUser
}

async function adminLoadTickets() {
  if (!isAdmin.value) return
  adminLoadingTickets.value = true
  try {
    const data = await fetchApi<{ items: AdminTicket[] }>('/support/admin/tickets')
    adminTickets.value = data.items || []
  } finally {
    adminLoadingTickets.value = false
  }
}

async function loadAdminTicket(ticketId: number) {
  if (!isAdmin.value) return
  const data = await fetchApi<AdminTicket>(`/support/tickets/${ticketId}`)
  adminActiveTicket.value = data
  adminReplyStatus.value = data.status
  adminReplyError.value = ''
  adminReplySuccess.value = false
}

async function sendAdminReply() {
  if (!adminActiveTicket.value) return
  adminReplyError.value = ''
  adminReplySuccess.value = false
  if (!adminReplyMessage.value.trim()) {
    adminReplyError.value = adminText.value.replyRequired
    return
  }
  adminSendingReply.value = true
  try {
    const response = await fetchApi<{ ticket: AdminTicket }>(`/support/tickets/${adminActiveTicket.value.id}`, {
      method: 'POST',
      body: {
        message: adminReplyMessage.value,
        status: adminReplyStatus.value,
        is_internal: adminReplyInternal.value,
      },
    })
    adminActiveTicket.value = response.ticket
    adminReplyMessage.value = ''
    adminReplyInternal.value = false
    adminReplySuccess.value = true
    await adminLoadTickets()
  } catch {
    adminReplyError.value = adminText.value.replyError
  } finally {
    adminSendingReply.value = false
  }
}

onMounted(async () => {
  await authStore.hydrate()
  await loadTickets()
  if (isAdmin.value) {
    await adminLoadTickets()
  }
})
</script>
