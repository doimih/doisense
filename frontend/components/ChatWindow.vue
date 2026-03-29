<template>
  <div class="rounded-[28px] border border-sky-100 bg-gradient-to-br from-[#f7fbff] via-[#f5f9fc] to-[#eef4f8] p-3 md:p-4">
    <div class="grid gap-4 lg:grid-cols-[220px,1fr,290px]">
      <aside class="overflow-hidden rounded-2xl border border-slate-200/60 bg-white/90 shadow-sm backdrop-blur">
        <div class="border-b border-slate-100 px-4 py-4">
          <p class="text-[11px] uppercase tracking-[0.2em] text-slate-400">{{ text.moduleLabel }}</p>
        </div>
        <div class="space-y-2 p-3">
          <button
            v-for="mod in modules"
            :key="mod.id"
            type="button"
            class="group flex w-full items-center gap-3 rounded-xl border px-3 py-3 text-left transition"
            :class="
              currentModule.id === mod.id
                ? 'border-teal-200 bg-teal-50 text-teal-800'
                : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:bg-slate-50'
            "
            @click="switchModule(mod.id)"
          >
            <span class="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-base">{{ mod.icon }}</span>
            <span>
              <span class="block text-sm font-semibold">{{ mod.name }}</span>
              <span class="block text-xs text-slate-500">{{ mod.shortName }}</span>
            </span>
          </button>
        </div>

        <div class="border-t border-slate-100 p-3">
          <p class="mb-2 text-[11px] uppercase tracking-[0.18em] text-slate-400">{{ text.mood }}</p>
          <div class="grid grid-cols-4 gap-2">
            <button
              v-for="m in moods"
              :key="m.id"
              type="button"
              class="rounded-lg border px-2 py-2 text-base transition"
              :class="selectedMood === m.id ? 'border-teal-300 bg-teal-50' : 'border-slate-200 bg-white hover:bg-slate-50'"
              @click="saveMood(m.id)"
            >
              {{ m.emoji }}
            </button>
          </div>

          <ClientOnly>
            <TaskCalendarMini />
            <template #fallback>
              <div class="mt-3 rounded-xl border border-slate-200 bg-white p-3">
                <p class="text-[11px] uppercase tracking-[0.18em] text-slate-500">Calendar task-uri</p>
                <p class="mt-2 text-xs text-slate-500">Se incarca...</p>
              </div>
            </template>
          </ClientOnly>
        </div>
      </aside>

      <section class="flex min-h-[680px] flex-col overflow-hidden rounded-2xl border border-slate-200/70 bg-white shadow-sm">
        <header class="border-b border-slate-100 bg-gradient-to-r from-teal-50/70 to-sky-50/70 px-5 py-4">
          <div class="flex flex-wrap items-center gap-2">
            <span class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700">
              <span>{{ currentModule.icon }}</span>
              <span>{{ currentModule.name }}</span>
            </span>
            <span class="rounded-full bg-teal-100 px-3 py-1 text-xs font-semibold text-teal-800">
              {{ text.coachBadge }}
            </span>
          </div>
          <p class="mt-2 text-sm leading-6 text-slate-600">{{ currentModule.description }}</p>
        </header>

        <div v-if="showCrisisBanner" class="mx-5 mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          <p class="font-semibold">{{ text.crisisTitle }}</p>
          <p>{{ text.crisisSubtitle }}</p>
        </div>

        <div ref="messagesEl" class="flex-1 space-y-4 overflow-y-auto bg-[linear-gradient(180deg,rgba(240,249,255,0.45),rgba(255,255,255,0))] px-5 py-5">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            class="max-w-[95%]"
            :class="msg.isUser ? 'ml-auto' : 'mr-auto'"
          >
            <div
                class="whitespace-pre-line rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm"
              :class="msg.isUser ? 'rounded-br-md border border-teal-200 bg-[#e9f7f5] text-slate-800' : 'rounded-bl-md border border-slate-200 bg-slate-50 text-slate-800'"
            >
              {{ msg.message }}
            </div>
          </div>
          <div v-if="loading" class="text-sm text-slate-500">{{ t('common.loading') }}...</div>
        </div>

        <div class="border-t border-slate-100 bg-white px-5 py-3">
          <p class="mb-2 text-xs font-semibold uppercase tracking-[0.15em] text-slate-500">{{ text.quickActions }}</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="prompt in currentModule.prompts"
              :key="prompt"
              type="button"
              class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-teal-200 hover:bg-teal-50 hover:text-teal-800"
              @click="send(prompt)"
            >
              {{ prompt }}
            </button>
          </div>
        </div>

        <form @submit.prevent="send()" class="border-t border-slate-100 bg-white p-4">
          <div class="flex items-end gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2">
            <textarea
              v-model="input"
              rows="1"
              :placeholder="t('chat.placeholder')"
              class="max-h-40 min-h-[42px] flex-1 resize-y rounded-xl border border-transparent bg-white px-3 py-2 text-sm text-slate-800 outline-none transition focus:border-teal-300 focus:ring-2 focus:ring-teal-100"
              @keydown.enter.exact.prevent="send()"
            />
            <button
              type="submit"
              :disabled="loading || !input.trim()"
              class="rounded-xl bg-teal-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {{ t('chat.send') }}
            </button>
          </div>
        </form>
      </section>

      <aside class="space-y-4 rounded-2xl border border-slate-200/70 bg-white p-4 shadow-sm">
        <div class="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
          <p class="text-xs uppercase tracking-[0.18em] text-slate-500">{{ text.streak }}</p>
          <p class="mt-1 text-3xl font-semibold text-slate-800">{{ streakDays }}</p>
          <p class="text-sm text-slate-500">{{ text.streakDays }} ({{ streakDays }}/{{ planDays }})</p>
          <div class="mt-3 grid grid-cols-7 gap-1">
            <div
              v-for="i in 7"
              :key="i"
              class="h-2 rounded"
              :class="i <= streakProgressSegments ? 'bg-teal-500' : 'bg-slate-200'"
            />
          </div>
        </div>

        <div class="rounded-xl border border-slate-200 bg-white p-4">
          <p class="text-xs uppercase tracking-[0.18em] text-slate-500">{{ text.mood }}</p>
          <svg class="mt-3 h-10 w-full" viewBox="0 0 120 32" preserveAspectRatio="none" aria-hidden="true">
            <polyline
              :points="moodChartPoints"
              fill="none"
              stroke="#0d9488"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>

        <div class="rounded-xl border border-slate-200 bg-white p-4">
          <p class="text-xs uppercase tracking-[0.18em] text-slate-500">{{ text.energyCheckin }}</p>
          <p class="mb-3 mt-1 text-sm text-slate-600">{{ text.energyToday }}</p>
          <div class="grid grid-cols-5 gap-2">
            <button
              v-for="n in 5"
              :key="n"
              type="button"
              class="rounded border py-1 text-xs font-medium transition"
              :class="
                energyLevel === n
                  ? 'border-teal-600 bg-teal-600 text-white'
                  : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
              "
              @click="saveEnergy(n)"
            >
              {{ n }}
            </button>
          </div>
          <svg class="mt-3 h-10 w-full" viewBox="0 0 120 32" preserveAspectRatio="none" aria-hidden="true">
            <polyline
              :points="energyChartPoints"
              fill="none"
              stroke="#334155"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>

        <div class="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
          {{ text.disclaimer }}
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import TaskCalendarMini from '~/components/calendar/TaskCalendarMini.vue'

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

interface WellbeingSummary {
  plan: 'free' | 'premium'
  plan_days: number
  streak_days: number
  current_mood: 'low' | 'ok' | 'good' | 'great'
  current_energy: number
  mood_history: Array<{ at: string; mood: 'low' | 'ok' | 'good' | 'great' }>
  energy_history: Array<{ at: string; energy_level: number }>
}

const { t } = useI18n()
const { locale } = useI18n()
const { fetchApi, getAccessToken, base } = useApi()

const localeCode = computed(() => {
  const code = (locale.value || 'en').slice(0, 2).toLowerCase()
  return ['ro', 'en', 'de', 'fr', 'it', 'es', 'pl'].includes(code) ? code : 'en'
})

type ChatUiText = {
  moduleLabel: string
  coachBadge: string
  quickActions: string
  crisisTitle: string
  crisisSubtitle: string
  streak: string
  streakDays: string
  mood: string
  energyCheckin: string
  energyToday: string
  disclaimer: string
  sendError: string
  quotaExceededError: string
  tierRestrictedError: string
  loginRequiredError: string
}

const chatCopy: Record<string, { modules: ChatModule[]; ui: ChatUiText }> = {
  ro: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Bine', name: 'Wellness', description: 'Mindfulness, somn, stres si echilibru emotional.', welcome: 'Buna! Sunt aici pentru wellness mental. Cum te pot ajuta astazi?', prompts: ['Ma simt stresat/a', 'Exercitiu de respiratie', 'Nu pot dormi', '5 minute de calm'] },
      { id: 'coaching', icon: '🎯', shortName: 'Ghid', name: 'Coaching', description: 'Obiective, claritate si planuri concrete.', welcome: 'Salut! Putem lucra pe un obiectiv clar pentru ziua asta.', prompts: ['Setare obiectiv saptamana', 'Cum evit procrastinarea?', 'Plan pe 3 pasi'] },
      { id: 'education', icon: '📚', shortName: 'Invata', name: 'Educatie', description: 'Concepte psihologice explicate simplu.', welcome: 'Buna! Pot explica pe scurt concepte de psihologie aplicata.', prompts: ['Ce este burnout-ul?', 'Cum functioneaza anxietatea?', 'Ce inseamna CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Suport', name: 'Suport', description: 'Spatiu sigur pentru descarcare emotionala.', welcome: 'Sunt aici sa te ascult, fara judecata. Ce apasa azi pe tine?', prompts: ['Am o zi grea', 'Ma simt coplesit/a', 'Nu stiu ce simt'] },
    ],
    ui: { moduleLabel: 'Module AI', coachBadge: 'Coach AI', quickActions: 'Actiuni rapide', crisisTitle: 'Este posibil sa ai nevoie de ajutor imediat.', crisisSubtitle: 'Daca e urgenta, suna la 112 sau contacteaza o linie locala de suport.', streak: 'Serie', streakDays: 'zile consecutive', mood: 'Stare', energyCheckin: 'Energie zilnica', energyToday: 'Nivel energie azi', disclaimer: 'Asistentul AI ofera suport complementar, nu inlocuieste un specialist licentiat.', sendError: 'Eroare la trimiterea mesajului.', quotaExceededError: 'Ai depasit cota zilnica de mesaje chat pentru planul tau.', tierRestrictedError: 'Chat-ul AI nu este disponibil pentru planul tau curent.', loginRequiredError: 'Trebuie sa te autentifici pentru a folosi chat-ul.' },
  },
  en: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Well', name: 'Wellness', description: 'Mindfulness, sleep, stress and emotional balance.', welcome: 'Hi! I am here for mental wellness. How can I help today?', prompts: ['I feel stressed', 'Breathing exercise', 'I cannot sleep', '5 minutes of calm'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Goals, clarity and practical plans.', welcome: 'Hi! We can work on one clear goal for today.', prompts: ['Set weekly goal', 'How do I avoid procrastination?', '3-step plan'] },
      { id: 'education', icon: '📚', shortName: 'Learn', name: 'Education', description: 'Psychology concepts explained simply.', welcome: 'Hi! I can explain practical psychology concepts in a short way.', prompts: ['What is burnout?', 'How does anxiety work?', 'What is CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Care', name: 'Support', description: 'Safe space for emotional release.', welcome: 'I am here to listen without judgment. What feels heavy today?', prompts: ['I am having a hard day', 'I feel overwhelmed', 'I do not know what I feel'] },
    ],
    ui: { moduleLabel: 'AI modules', coachBadge: 'AI Coach', quickActions: 'Quick actions', crisisTitle: 'You may need immediate help.', crisisSubtitle: 'If this is an emergency, call your local emergency number now.', streak: 'Streak', streakDays: 'days in a row', mood: 'Mood', energyCheckin: 'Energy check-in', energyToday: 'Energy level today', disclaimer: 'AI assistant support is complementary and does not replace licensed care.', sendError: 'Failed to send message.', quotaExceededError: 'Daily chat quota exceeded for your tier.', tierRestrictedError: 'AI chat is not available for your current plan.', loginRequiredError: 'Please sign in to use chat.' },
  },
  de: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Wohl', name: 'Wellness', description: 'Achtsamkeit, Schlaf, Stress und emotionale Balance.', welcome: 'Hallo! Ich bin fur mentales Wohlbefinden da. Wie kann ich helfen?', prompts: ['Ich fuhle mich gestresst', 'Atemubung', 'Ich kann nicht schlafen', '5 Minuten Ruhe'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Ziele, Klarheit und konkrete Plane.', welcome: 'Hallo! Wir konnen heute an einem klaren Ziel arbeiten.', prompts: ['Wochenziel setzen', 'Wie vermeide ich Prokrastination?', '3-Schritte-Plan'] },
      { id: 'education', icon: '📚', shortName: 'Lern', name: 'Bildung', description: 'Psychologische Konzepte einfach erklart.', welcome: 'Hallo! Ich kann psychologische Konzepte kurz und klar erklaren.', prompts: ['Was ist Burnout?', 'Wie funktioniert Angst?', 'Was bedeutet CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Hilfe', name: 'Support', description: 'Sicherer Raum fur emotionale Entlastung.', welcome: 'Ich hore dir ohne Bewertung zu. Was belastet dich heute?', prompts: ['Ich habe einen schweren Tag', 'Ich fuhle mich uberfordert', 'Ich weiss nicht, was ich fuhle'] },
    ],
    ui: { moduleLabel: 'KI-Module', coachBadge: 'KI Coach', quickActions: 'Schnellaktionen', crisisTitle: 'Du brauchst moglicherweise sofort Hilfe.', crisisSubtitle: 'Bei einem Notfall rufe sofort die lokale Notrufnummer an.', streak: 'Serie', streakDays: 'Tage in Folge', mood: 'Stimmung', energyCheckin: 'Energie-Check-in', energyToday: 'Energie heute', disclaimer: 'Die KI-Unterstutzung ist erganzend und ersetzt keine fachliche Behandlung.', sendError: 'Nachricht konnte nicht gesendet werden.', quotaExceededError: 'Dein tagliches Chat-Kontingent fur dein Abo ist aufgebraucht.', tierRestrictedError: 'KI-Chat ist fur deinen aktuellen Tarif nicht verfugbar.', loginRequiredError: 'Bitte melde dich an, um den Chat zu nutzen.' },
  },
  fr: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Bien', name: 'Bien-etre', description: 'Pleine conscience, sommeil, stress et equilibre emotionnel.', welcome: 'Bonjour ! Je suis la pour le bien-etre mental. Comment puis-je aider aujourd\'hui ?', prompts: ['Je me sens stresse(e)', 'Exercice de respiration', 'Je n\'arrive pas a dormir', '5 minutes de calme'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Objectifs, clarte et plans concrets.', welcome: 'Bonjour ! Nous pouvons travailler sur un objectif clair pour aujourd\'hui.', prompts: ['Definir un objectif hebdo', 'Comment eviter la procrastination ?', 'Plan en 3 etapes'] },
      { id: 'education', icon: '📚', shortName: 'Appr', name: 'Education', description: 'Concepts psychologiques expliques simplement.', welcome: 'Bonjour ! Je peux expliquer des concepts de psychologie de facon simple.', prompts: ['Qu\'est-ce que le burnout ?', 'Comment fonctionne l\'anxiete ?', 'Que signifie CBT ?'] },
      { id: 'support', icon: '🤝', shortName: 'Soin', name: 'Soutien', description: 'Espace sur pour relacher les emotions.', welcome: 'Je suis la pour t\'ecouter sans jugement. Qu\'est-ce qui te pese aujourd\'hui ?', prompts: ['Je passe une journee difficile', 'Je me sens depasse(e)', 'Je ne sais pas ce que je ressens'] },
    ],
    ui: { moduleLabel: 'Modules IA', coachBadge: 'Coach IA', quickActions: 'Actions rapides', crisisTitle: 'Tu pourrais avoir besoin d\'aide immediate.', crisisSubtitle: 'En cas d\'urgence, appelle immediatement le numero d\'urgence local.', streak: 'Serie', streakDays: 'jours d\'affilee', mood: 'Humeur', energyCheckin: 'Check-in energie', energyToday: 'Niveau d\'energie aujourd\'hui', disclaimer: 'L\'assistant IA offre un soutien complementaire et ne remplace pas un professionnel de sante.', sendError: 'Impossible d\'envoyer le message.', quotaExceededError: 'Quota quotidien de messages chat depasse pour ton forfait.', tierRestrictedError: 'Le chat IA n\'est pas disponible pour ton forfait actuel.', loginRequiredError: 'Connecte-toi pour utiliser le chat.' },
  },
  it: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Bene', name: 'Wellness', description: 'Mindfulness, sonno, stress ed equilibrio emotivo.', welcome: 'Ciao! Sono qui per il benessere mentale. Come posso aiutarti?', prompts: ['Mi sento stressato/a', 'Esercizio di respirazione', 'Non riesco a dormire', '5 minuti di calma'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Obiettivi, chiarezza e piani concreti.', welcome: 'Ciao! Possiamo lavorare su un obiettivo chiaro per oggi.', prompts: ['Definisci obiettivo settimanale', 'Come evitare la procrastinazione?', 'Piano in 3 passi'] },
      { id: 'education', icon: '📚', shortName: 'Impara', name: 'Educazione', description: 'Concetti psicologici spiegati in modo semplice.', welcome: 'Ciao! Posso spiegare in breve concetti utili di psicologia.', prompts: ['Cos\'e il burnout?', 'Come funziona l\'ansia?', 'Che cos\'e la CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Cura', name: 'Supporto', description: 'Spazio sicuro per il rilascio emotivo.', welcome: 'Sono qui per ascoltarti senza giudicare. Cosa ti pesa oggi?', prompts: ['Sto vivendo una giornata difficile', 'Mi sento sopraffatto/a', 'Non so cosa provo'] },
    ],
    ui: { moduleLabel: 'Moduli AI', coachBadge: 'Coach AI', quickActions: 'Azioni rapide', crisisTitle: 'Potresti aver bisogno di aiuto immediato.', crisisSubtitle: 'In caso di emergenza chiama subito il numero locale di emergenza.', streak: 'Serie', streakDays: 'giorni consecutivi', mood: 'Umore', energyCheckin: 'Check energia', energyToday: 'Livello energia oggi', disclaimer: 'L\'assistente AI offre supporto complementare e non sostituisce specialisti abilitati.', sendError: 'Invio del messaggio non riuscito.', quotaExceededError: 'Hai superato la quota giornaliera di messaggi chat per il tuo piano.', tierRestrictedError: 'La chat AI non e disponibile per il tuo piano attuale.', loginRequiredError: 'Accedi per usare la chat.' },
  },
  es: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Bien', name: 'Wellness', description: 'Mindfulness, sueno, estres y equilibrio emocional.', welcome: 'Hola, estoy aqui para bienestar mental. Como puedo ayudarte hoy?', prompts: ['Me siento estresado/a', 'Ejercicio de respiracion', 'No puedo dormir', '5 minutos de calma'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Objetivos, claridad y planes concretos.', welcome: 'Hola, podemos trabajar en un objetivo claro para hoy.', prompts: ['Definir objetivo semanal', 'Como evito procrastinar?', 'Plan de 3 pasos'] },
      { id: 'education', icon: '📚', shortName: 'Aprende', name: 'Educacion', description: 'Conceptos de psicologia explicados de forma simple.', welcome: 'Hola, puedo explicar conceptos de psicologia de forma practica.', prompts: ['Que es el burnout?', 'Como funciona la ansiedad?', 'Que significa CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Apoyo', name: 'Apoyo', description: 'Espacio seguro para descarga emocional.', welcome: 'Estoy aqui para escucharte sin juicio. Que te pesa hoy?', prompts: ['Tengo un dia dificil', 'Me siento abrumado/a', 'No se que siento'] },
    ],
    ui: { moduleLabel: 'Modulos IA', coachBadge: 'Coach IA', quickActions: 'Acciones rapidas', crisisTitle: 'Podrias necesitar ayuda inmediata.', crisisSubtitle: 'Si es una emergencia, llama ahora al numero local de emergencias.', streak: 'Racha', streakDays: 'dias seguidos', mood: 'Estado de animo', energyCheckin: 'Chequeo de energia', energyToday: 'Nivel de energia hoy', disclaimer: 'El asistente AI brinda apoyo complementario y no sustituye atencion profesional.', sendError: 'No se pudo enviar el mensaje.', quotaExceededError: 'Has superado la cuota diaria de mensajes de chat para tu plan.', tierRestrictedError: 'El chat AI no esta disponible para tu plan actual.', loginRequiredError: 'Inicia sesion para usar el chat.' },
  },
  pl: {
    modules: [
      { id: 'wellness', icon: '🌿', shortName: 'Dobro', name: 'Wellness', description: 'Mindfulness, sen, stres i rownowaga emocjonalna.', welcome: 'Czesc! Jestem tu dla dobrostanu psychicznego. Jak moge pomoc?', prompts: ['Czuje stres', 'Cwiczenie oddechowe', 'Nie moge spac', '5 minut spokoju'] },
      { id: 'coaching', icon: '🎯', shortName: 'Coach', name: 'Coaching', description: 'Cele, jasnosc i konkretne plany.', welcome: 'Czesc! Mozemy popracowac nad jednym jasnym celem na dzis.', prompts: ['Ustal cel tygodnia', 'Jak unikac prokrastynacji?', 'Plan na 3 kroki'] },
      { id: 'education', icon: '📚', shortName: 'Nauka', name: 'Edukacja', description: 'Pojecia psychologiczne wyjasnione prosto.', welcome: 'Czesc! Moge krotko wyjasnic praktyczne pojecia psychologiczne.', prompts: ['Co to jest wypalenie?', 'Jak dziala lek?', 'Co oznacza CBT?'] },
      { id: 'support', icon: '🤝', shortName: 'Pomoc', name: 'Wsparcie', description: 'Bezpieczna przestrzen na emocje.', welcome: 'Jestem tutaj, by wysluchac bez oceniania. Co cie dzis obciaza?', prompts: ['Mam trudny dzien', 'Czuje przytloczenie', 'Nie wiem, co czuje'] },
    ],
    ui: { moduleLabel: 'Moduly AI', coachBadge: 'AI Coach', quickActions: 'Szybkie akcje', crisisTitle: 'Mozesz potrzebowac natychmiastowej pomocy.', crisisSubtitle: 'Jesli to nagla sytuacja, zadzwon pod lokalny numer alarmowy.', streak: 'Seria', streakDays: 'dni z rzedu', mood: 'Nastroj', energyCheckin: 'Dzienna energia', energyToday: 'Poziom energii dzis', disclaimer: 'Asystent AI wspiera dodatkowo i nie zastepuje specjalisty.', sendError: 'Nie udalo sie wyslac wiadomosci.', quotaExceededError: 'Przekroczono dzienny limit wiadomosci czatu dla Twojego planu.', tierRestrictedError: 'Czat AI nie jest dostepny w Twoim obecnym planie.', loginRequiredError: 'Zaloguj sie, aby korzystac z czatu.' },
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
const streakDays = ref(0)
const planDays = ref(7)
const moodHistory = ref<Array<{ at: string; mood: 'low' | 'ok' | 'good' | 'great' }>>([])
const energyHistory = ref<Array<{ at: string; energy_level: number }>>([])
const currentModuleId = ref<ChatModule['id']>('wellness')
const moduleMessages = reactive<Record<ChatModule['id'], ChatMessage[]>>({
  wellness: [],
  coaching: [],
  education: [],
  support: [],
})
const messages = computed(() => moduleMessages[currentModuleId.value])
const moduleHistory = ref<Record<string, ChatMessage[]>>({})
const input = ref('')
const loading = ref(false)
const translatingDraft = ref(false)
const showCrisisBanner = ref(false)
const messagesEl = ref<HTMLElement | null>(null)

const currentModule = computed(() => modules.value.find((m) => m.id === currentModuleId.value) || modules.value[0])

const moodValueMap: Record<'low' | 'ok' | 'good' | 'great', number> = {
  low: 1,
  ok: 2,
  good: 3,
  great: 4,
}

const streakProgressSegments = computed(() => {
  if (!planDays.value) return 0
  const ratio = Math.min(1, streakDays.value / planDays.value)
  return Math.max(0, Math.round(ratio * 7))
})

function buildSparklinePoints(values: number[], max: number): string {
  if (!values.length) return '0,16 120,16'
  if (values.length === 1) {
    const y = 30 - ((values[0] - 1) / Math.max(1, max - 1)) * 26
    return `0,${y} 120,${y}`
  }

  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * 120
      const y = 30 - ((value - 1) / Math.max(1, max - 1)) * 26
      return `${x},${y}`
    })
    .join(' ')
}

const moodChartPoints = computed(() => {
  const values = moodHistory.value.slice(-24).map((item) => moodValueMap[item.mood])
  return buildSparklinePoints(values, 4)
})

const energyChartPoints = computed(() => {
  const values = energyHistory.value.slice(-24).map((item) => item.energy_level)
  return buildSparklinePoints(values, 5)
})

async function loadWellbeingSummary() {
  try {
    const summary = await fetchApi<WellbeingSummary>('/wellbeing/summary')
    streakDays.value = summary.streak_days || 0
    planDays.value = summary.plan_days || 7
    selectedMood.value = summary.current_mood || 'ok'
    energyLevel.value = summary.current_energy || 3
    moodHistory.value = summary.mood_history || []
    energyHistory.value = summary.energy_history || []
  } catch {
    // Keep local defaults if summary is unavailable.
  }
}

function stripMessagePrefix(msg: string): string {
  if (!msg.startsWith('[') || !msg.includes(']')) return msg
  return msg.slice(msg.indexOf(']') + 1).trim()
}

async function loadChatHistory() {
  try {
    const data = await fetchApi<{
      history: Record<string, Array<{ user_message: string; ai_response: string; created_at: string }>>
      last_module: string | null
    }>('/chat/history')
    const result: Record<string, ChatMessage[]> = {}
    for (const [mod, items] of Object.entries(data.history || {})) {
      result[mod] = items.flatMap((item) => [
        { message: stripMessagePrefix(item.user_message), isUser: true },
        { message: item.ai_response, isUser: false },
      ])
    }
    moduleHistory.value = result
    if (data.last_module && ['wellness', 'coaching', 'education', 'support'].includes(data.last_module)) {
      currentModuleId.value = data.last_module as ChatModule['id']
    }
  } catch {
    // Keep defaults if history unavailable.
  }
}

async function saveMood(mood: 'low' | 'ok' | 'good' | 'great') {
  selectedMood.value = mood
  try {
    await fetchApi('/wellbeing/checkins', {
      method: 'POST',
      body: { mood },
    })
    await loadWellbeingSummary()
  } catch {
    // UI remains responsive even if persistence fails.
  }
}

async function saveEnergy(level: number) {
  energyLevel.value = level
  try {
    await fetchApi('/wellbeing/checkins', {
      method: 'POST',
      body: { energy_level: level },
    })
    await loadWellbeingSummary()
  } catch {
    // UI remains responsive even if persistence fails.
  }
}

function resetConversation(moduleId?: ChatModule['id']) {
  const id = moduleId ?? currentModuleId.value
  const mod = modules.value.find((m) => m.id === id) || modules.value[0]
  if (moduleId === undefined) showCrisisBanner.value = false
  const hist = moduleHistory.value[id]
  if (hist && hist.length > 0) {
    moduleMessages[id] = [...hist]
  } else {
    moduleMessages[id] = [{ message: mod.welcome, isUser: false }]
  }
}

function switchModule(id: ChatModule['id']) {
  showCrisisBanner.value = false
  currentModuleId.value = id
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

function resolveApiErrorMessage(error: unknown, ui: ChatUiText): string {
  const err = error as {
    data?: { detail?: string; code?: string }
    statusCode?: number
    message?: string
  }

  if (err?.data?.code === 'quota_exceeded') {
    return ui.quotaExceededError
  }

  const detail = err?.data?.detail?.trim()
  if (detail) {
    const normalized = detail.toLowerCase()
    if (normalized.includes('daily chat quota exceeded')) {
      return ui.quotaExceededError
    }
    if (normalized.includes('not available for your current tier') || normalized.includes('current tier')) {
      return ui.tierRestrictedError
    }
    if (normalized.includes('authentication credentials were not provided')) {
      return ui.loginRequiredError
    }
    return detail
  }

  if (err?.statusCode === 403) {
    return ui.tierRestrictedError
  }

  if (err?.statusCode === 401) {
    return ui.loginRequiredError
  }

  const generic = err?.message?.trim()
  if (generic && !generic.startsWith('[POST]')) {
    return generic
  }

  return ui.sendError
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  })
}

function buildChatMessagePayload(userText: string) {
  return {
    message: `[${currentModule.value.id}|mood:${selectedMood.value}|energy:${energyLevel.value}] ${userText}`,
  }
}

function applyAssistantMessage(index: number, message: string) {
  if (!moduleMessages[currentModuleId.value][index]) return
  moduleMessages[currentModuleId.value][index].message = message
  if (detectCrisis(message)) {
    showCrisisBanner.value = true
  }
}

async function streamChatReply(userText: string, assistantIndex: number): Promise<void> {
  const token = await getAccessToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Language': localeCode.value,
  }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${base}/chat/send-stream`, {
    method: 'POST',
    headers,
    body: JSON.stringify(buildChatMessagePayload(userText)),
  })

  if (!response.ok || !response.body) {
    throw new Error(`stream_unavailable_${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''
  let assistantText = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    let marker = buffer.indexOf('\n\n')
    while (marker !== -1) {
      const rawEvent = buffer.slice(0, marker)
      buffer = buffer.slice(marker + 2)

      const lines = rawEvent.split('\n')
      let eventType = 'message'
      let dataRaw = ''
      for (const line of lines) {
        if (line.startsWith('event:')) {
          eventType = line.slice(6).trim()
        } else if (line.startsWith('data:')) {
          dataRaw += line.slice(5).trim()
        }
      }

      if (!dataRaw) {
        marker = buffer.indexOf('\n\n')
        continue
      }

      let payload: { token?: string; reply?: string; message?: string; detail?: string } = {}
      try {
        payload = JSON.parse(dataRaw)
      } catch {
        marker = buffer.indexOf('\n\n')
        continue
      }

      if (eventType === 'ack' && payload.message) {
        applyAssistantMessage(assistantIndex, payload.message)
        scrollToBottom()
      } else if (eventType === 'token' && payload.token) {
        assistantText += payload.token
        applyAssistantMessage(assistantIndex, assistantText)
        scrollToBottom()
      } else if (eventType === 'done') {
        applyAssistantMessage(assistantIndex, payload.reply || assistantText)
        return
      } else if (eventType === 'error') {
        throw new Error(payload.detail || text.value.sendError)
      }

      marker = buffer.indexOf('\n\n')
    }
  }

  if (!assistantText) {
    throw new Error('empty_stream_reply')
  }
  applyAssistantMessage(assistantIndex, assistantText)
}

async function send(quickPrompt?: string) {
  const userText = (quickPrompt || input.value).trim()
  if (!userText || loading.value) return

  moduleMessages[currentModuleId.value].push({ message: userText, isUser: true })
  const assistantIndex = moduleMessages[currentModuleId.value].push({ message: '...', isUser: false }) - 1
  input.value = ''
  loading.value = true
  try {
    try {
      await streamChatReply(userText, assistantIndex)
    } catch {
      // Backward compatible fallback to existing sync endpoint.
      const res = await fetchApi<{ reply: string }>('/chat/send', {
        method: 'POST',
        body: buildChatMessagePayload(userText),
      })
      applyAssistantMessage(assistantIndex, res.reply)
    }
  } catch (e) {
    applyAssistantMessage(assistantIndex, resolveApiErrorMessage(e, text.value))
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

async function translateDraftToLocale(targetLocale: string, previousLocale?: string) {
  const sourceLocale = (previousLocale || '').slice(0, 2).toLowerCase()
  const targetLanguage = (targetLocale || '').slice(0, 2).toLowerCase()
  const originalText = input.value

  if (!originalText.trim() || sourceLocale === targetLanguage || translatingDraft.value) return

  translatingDraft.value = true
  try {
    const res = await fetchApi<{ translated_text: string }>('/chat/translate-draft', {
      method: 'POST',
      body: {
        text: originalText,
        source_language: sourceLocale,
        target_language: targetLanguage,
      },
    })
    if (input.value === originalText && (res.translated_text || '').trim()) {
      input.value = res.translated_text
    }
  } catch {
    // Keep user's original draft if translation is unavailable.
  } finally {
    translatingDraft.value = false
  }
}

onMounted(async () => {
  await loadWellbeingSummary()
  await loadChatHistory()
  const moduleIds: ChatModule['id'][] = ['wellness', 'coaching', 'education', 'support']
  for (const id of moduleIds) {
    resetConversation(id)
  }
  nextTick(() => {
    scrollToBottom()
  })
})

watch(localeCode, async (nextLocale, previousLocale) => {
  const moduleIds: ChatModule['id'][] = ['wellness', 'coaching', 'education', 'support']
  for (const id of moduleIds) {
    if (moduleMessages[id].length === 1 && !moduleMessages[id][0].isUser) {
      const mod = modules.value.find((m) => m.id === id) || modules.value[0]
      moduleMessages[id] = [{ message: mod.welcome, isUser: false }]
    }
  }

  await translateDraftToLocale(nextLocale, previousLocale)
})
</script>
