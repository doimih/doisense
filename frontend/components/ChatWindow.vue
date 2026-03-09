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
        <p class="font-semibold">{{ text.crisisTitle }}</p>
        <p>{{ text.crisisSubtitle }}</p>
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
        <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-stone-500">{{ text.quickActions }}</p>
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
        <p class="text-xs uppercase tracking-wider text-stone-500">{{ text.streak }}</p>
        <p class="mt-1 text-3xl font-semibold text-stone-800">7</p>
        <p class="text-sm text-stone-500">{{ text.streakDays }}</p>
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
        <p class="text-xs uppercase tracking-wider text-stone-500">{{ text.mood }}</p>
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
        <p class="text-xs uppercase tracking-wider text-stone-500">{{ text.energyCheckin }}</p>
        <p class="mb-3 mt-1 text-sm text-stone-600">{{ text.energyToday }}</p>
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
        {{ text.disclaimer }}
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
const { locale } = useI18n()
const { fetchApi } = useApi()

const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

type ChatUiText = {
  quickActions: string
  crisisTitle: string
  crisisSubtitle: string
  streak: string
  streakDays: string
  mood: string
  energyCheckin: string
  energyToday: string
  disclaimer: string
}

const chatCopy: Record<string, { modules: ChatModule[]; ui: ChatUiText }> = {
  ro: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Well', name: 'Wellness', description: 'Mindfulness, somn, stres si echilibru emotional.', welcome: 'Buna! Sunt aici pentru wellness mental. Cum te pot ajuta astazi?', prompts: ['Ma simt stresat/a', 'Exercitiu de respiratie', 'Nu pot dormi', '5 minute de calm'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Obiective, claritate si planuri concrete.', welcome: 'Salut! Putem lucra pe un obiectiv clar pentru ziua asta.', prompts: ['Setare obiectiv saptamana', 'Cum evit procrastinarea?', 'Plan pe 3 pasi'] },
      { id: 'education', icon: '📚', shortName: 'Learn', name: 'Educatie', description: 'Concepte psihologice explicate simplu.', welcome: 'Buna! Pot explica pe scurt concepte de psihologie aplicata.', prompts: ['Ce este burnout-ul?', 'Cum functioneaza anxietatea?', 'Ce inseamna CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Care', name: 'Suport', description: 'Spatiu sigur pentru descarcare emotionala.', welcome: 'Sunt aici sa te ascult, fara judecata. Ce apasa azi pe tine?', prompts: ['Am o zi grea', 'Ma simt coplesit/a', 'Nu stiu ce simt'] },
    ],
    ui: { quickActions: 'Actiuni rapide', crisisTitle: 'Este posibil sa ai nevoie de ajutor imediat.', crisisSubtitle: 'Daca e urgenta, suna la 112 sau contacteaza o linie locala de suport.', streak: 'Streak', streakDays: 'zile consecutive', mood: 'Stare', energyCheckin: 'Energie zilnica', energyToday: 'Nivel energie azi', disclaimer: 'Asistentul AI ofera suport complementar, nu inlocuieste un specialist licentiat.' },
  },
  en: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Well', name: 'Wellness', description: 'Mindfulness, sleep, stress and emotional balance.', welcome: 'Hi! I am here for mental wellness. How can I help today?', prompts: ['I feel stressed', 'Breathing exercise', 'I cannot sleep', '5 minutes of calm'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Goals, clarity and practical plans.', welcome: 'Hi! We can work on one clear goal for today.', prompts: ['Set weekly goal', 'How do I avoid procrastination?', '3-step plan'] },
      { id: 'education', icon: '📚', shortName: 'Learn', name: 'Education', description: 'Psychology concepts explained simply.', welcome: 'Hi! I can explain practical psychology concepts in a short way.', prompts: ['What is burnout?', 'How does anxiety work?', 'What is CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Care', name: 'Support', description: 'Safe space for emotional release.', welcome: 'I am here to listen without judgment. What feels heavy today?', prompts: ['I am having a hard day', 'I feel overwhelmed', 'I do not know what I feel'] },
    ],
    ui: { quickActions: 'Quick actions', crisisTitle: 'You may need immediate help.', crisisSubtitle: 'If this is an emergency, call your local emergency number now.', streak: 'Streak', streakDays: 'days in a row', mood: 'Mood', energyCheckin: 'Energy check-in', energyToday: 'Energy level today', disclaimer: 'AI assistant support is complementary and does not replace licensed care.' },
  },
  de: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Well', name: 'Wellness', description: 'Achtsamkeit, Schlaf, Stress und emotionale Balance.', welcome: 'Hallo! Ich bin fur mentales Wohlbefinden da. Wie kann ich helfen?', prompts: ['Ich fuhle mich gestresst', 'Atemubung', 'Ich kann nicht schlafen', '5 Minuten Ruhe'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Ziele, Klarheit und konkrete Plane.', welcome: 'Hallo! Wir konnen heute an einem klaren Ziel arbeiten.', prompts: ['Wochenziel setzen', 'Wie vermeide ich Prokrastination?', '3-Schritte-Plan'] },
      { id: 'education', icon: '📚', shortName: 'Learn', name: 'Bildung', description: 'Psychologische Konzepte einfach erklart.', welcome: 'Hallo! Ich kann psychologische Konzepte kurz und klar erklaren.', prompts: ['Was ist Burnout?', 'Wie funktioniert Angst?', 'Was bedeutet CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Care', name: 'Support', description: 'Sicherer Raum fur emotionale Entlastung.', welcome: 'Ich hore dir ohne Bewertung zu. Was belastet dich heute?', prompts: ['Ich habe einen schweren Tag', 'Ich fuhle mich uberfordert', 'Ich weiss nicht, was ich fuhle'] },
    ],
    ui: { quickActions: 'Schnellaktionen', crisisTitle: 'Du brauchst moglicherweise sofort Hilfe.', crisisSubtitle: 'Bei einem Notfall rufe sofort die lokale Notrufnummer an.', streak: 'Serie', streakDays: 'Tage in Folge', mood: 'Stimmung', energyCheckin: 'Energie-Check-in', energyToday: 'Energie heute', disclaimer: 'Die KI-Unterstutzung ist erganzend und ersetzt keine fachliche Behandlung.' },
  },
  it: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Well', name: 'Wellness', description: 'Mindfulness, sonno, stress ed equilibrio emotivo.', welcome: 'Ciao! Sono qui per il benessere mentale. Come posso aiutarti?', prompts: ['Mi sento stressato/a', 'Esercizio di respirazione', 'Non riesco a dormire', '5 minuti di calma'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Obiettivi, chiarezza e piani concreti.', welcome: 'Ciao! Possiamo lavorare su un obiettivo chiaro per oggi.', prompts: ['Definisci obiettivo settimanale', 'Come evitare la procrastinazione?', 'Piano in 3 passi'] },
      { id: 'education', icon: '📚', shortName: 'Learn', name: 'Educazione', description: 'Concetti psicologici spiegati in modo semplice.', welcome: 'Ciao! Posso spiegare in breve concetti utili di psicologia.', prompts: ['Cos\'e il burnout?', 'Come funziona l\'ansia?', 'Che cos\'e la CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Care', name: 'Supporto', description: 'Spazio sicuro per il rilascio emotivo.', welcome: 'Sono qui per ascoltarti senza giudicare. Cosa ti pesa oggi?', prompts: ['Sto vivendo una giornata difficile', 'Mi sento sopraffatto/a', 'Non so cosa provo'] },
    ],
    ui: { quickActions: 'Azioni rapide', crisisTitle: 'Potresti aver bisogno di aiuto immediato.', crisisSubtitle: 'In caso di emergenza chiama subito il numero locale di emergenza.', streak: 'Serie', streakDays: 'giorni consecutivi', mood: 'Umore', energyCheckin: 'Check energia', energyToday: 'Livello energia oggi', disclaimer: 'L\'assistente AI offre supporto complementare e non sostituisce specialisti abilitati.' },
  },
  es: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Well', name: 'Wellness', description: 'Mindfulness, sueno, estres y equilibrio emocional.', welcome: 'Hola, estoy aqui para bienestar mental. Como puedo ayudarte hoy?', prompts: ['Me siento estresado/a', 'Ejercicio de respiracion', 'No puedo dormir', '5 minutos de calma'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Objetivos, claridad y planes concretos.', welcome: 'Hola, podemos trabajar en un objetivo claro para hoy.', prompts: ['Definir objetivo semanal', 'Como evito procrastinar?', 'Plan de 3 pasos'] },
      { id: 'education', icon: '📚', shortName: 'Learn', name: 'Educacion', description: 'Conceptos de psicologia explicados de forma simple.', welcome: 'Hola, puedo explicar conceptos de psicologia de forma practica.', prompts: ['Que es el burnout?', 'Como funciona la ansiedad?', 'Que significa CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Care', name: 'Apoyo', description: 'Espacio seguro para descarga emocional.', welcome: 'Estoy aqui para escucharte sin juicio. Que te pesa hoy?', prompts: ['Tengo un dia dificil', 'Me siento abrumado/a', 'No se que siento'] },
    ],
    ui: { quickActions: 'Acciones rapidas', crisisTitle: 'Podrias necesitar ayuda inmediata.', crisisSubtitle: 'Si es una emergencia, llama ahora al numero local de emergencias.', streak: 'Racha', streakDays: 'dias seguidos', mood: 'Estado de animo', energyCheckin: 'Chequeo de energia', energyToday: 'Nivel de energia hoy', disclaimer: 'El asistente AI brinda apoyo complementario y no sustituye atencion profesional.' },
  },
  pl: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Well', name: 'Wellness', description: 'Mindfulness, sen, stres i rownowaga emocjonalna.', welcome: 'Czesc! Jestem tu dla dobrostanu psychicznego. Jak moge pomoc?', prompts: ['Czuje stres', 'Cwiczenie oddechowe', 'Nie moge spac', '5 minut spokoju'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Cele, jasnosc i konkretne plany.', welcome: 'Czesc! Mozemy popracowac nad jednym jasnym celem na dzis.', prompts: ['Ustal cel tygodnia', 'Jak unikac prokrastynacji?', 'Plan na 3 kroki'] },
      { id: 'education', icon: '📚', shortName: 'Learn', name: 'Edukacja', description: 'Pojecia psychologiczne wyjasnione prosto.', welcome: 'Czesc! Moge krotko wyjasnic praktyczne pojecia psychologiczne.', prompts: ['Co to jest wypalenie?', 'Jak dziala lek?', 'Co oznacza CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Care', name: 'Wsparcie', description: 'Bezpieczna przestrzen na emocje.', welcome: 'Jestem tutaj, by wysluchac bez oceniania. Co cie dzis obciaza?', prompts: ['Mam trudny dzien', 'Czuje przytloczenie', 'Nie wiem, co czuje'] },
    ],
    ui: { quickActions: 'Szybkie akcje', crisisTitle: 'Mozesz potrzebowac natychmiastowej pomocy.', crisisSubtitle: 'Jesli to nagla sytuacja, zadzwon pod lokalny numer alarmowy.', streak: 'Seria', streakDays: 'dni z rzedu', mood: 'Nastroj', energyCheckin: 'Dzienna energia', energyToday: 'Poziom energii dzis', disclaimer: 'Asystent AI wspiera dodatkowo i nie zastepuje specjalisty.' },
  },
}

const modules = computed(() => (chatCopy[localeCode.value] || chatCopy.en).modules)
const text = computed(() => (chatCopy[localeCode.value] || chatCopy.en).ui)

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

const currentModule = computed(() => modules.value.find((m) => m.id === currentModuleId.value) || modules.value[0])

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

watch(localeCode, () => {
  resetConversation()
})
</script>
