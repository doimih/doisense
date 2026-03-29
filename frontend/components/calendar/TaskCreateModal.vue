<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-[130] flex items-center justify-center bg-black/30 p-3" @click.self="emit('close')">
      <div class="w-full max-w-2xl rounded-2xl border border-slate-200 bg-white p-5 shadow-2xl max-h-[90vh] overflow-y-auto">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="text-base font-semibold text-slate-800">{{ copy.title }}</h3>
        <button type="button" class="rounded px-2 py-1 text-xs text-slate-500 hover:bg-slate-100" @click="emit('close')">✕</button>
      </div>

      <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
        <label class="text-xs text-slate-600">
          {{ copy.taskTitle }}
          <input v-model="form.title" type="text" class="mt-1 w-full rounded border border-slate-300 px-2 py-2 text-sm" />
        </label>

        <label class="text-xs text-slate-600">
          {{ copy.duration }}
          <input v-model.number="form.duration_minutes" type="number" min="5" max="600" class="mt-1 w-full rounded border border-slate-300 px-2 py-2 text-sm" />
        </label>

        <label class="md:col-span-2 text-xs text-slate-600">
          {{ copy.description }}
          <textarea v-model="form.description" rows="2" class="mt-1 w-full rounded border border-slate-300 px-2 py-2 text-sm" />
        </label>

        <label class="text-xs text-slate-600">
          {{ copy.frequency }}
          <select v-model="form.frequency" class="mt-1 w-full rounded border border-slate-300 px-2 py-2 text-sm">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly" :disabled="!capabilities.advanced_task_options">Monthly</option>
            <option value="custom" :disabled="!capabilities.advanced_task_options">Custom</option>
          </select>
        </label>

        <label class="text-xs text-slate-600">
          {{ copy.time }}
          <input v-model="form.start_time" type="time" class="mt-1 w-full rounded border border-slate-300 px-2 py-2 text-sm" />
        </label>

        <label class="text-xs text-slate-600">
          {{ copy.reminder }}
          <select v-model="form.reminder_enabled" class="mt-1 w-full rounded border border-slate-300 px-2 py-2 text-sm">
            <option :value="false">Off</option>
            <option :value="true">On</option>
          </select>
        </label>

        <label class="text-xs text-slate-600">
          {{ copy.reminderBefore }}
          <input v-model.number="form.reminder_minutes_before" type="number" min="0" max="1440" class="mt-1 w-full rounded border border-slate-300 px-2 py-2 text-sm" />
        </label>

        <label v-if="capabilities.advanced_task_options" class="md:col-span-2 text-xs text-slate-600">
          {{ copy.advanced }}
          <input v-model="advancedText" type="text" class="mt-1 w-full rounded border border-slate-300 px-2 py-2 text-sm" placeholder="window=07:00-09:00; priority=high" />
          <p class="mt-1 text-[11px] text-slate-500">
            Optional: reguli extra pentru task (de ex. interval orar preferat, prioritate). Daca nu ai nevoie, lasa gol.
          </p>
        </label>
      </div>

      <div v-if="isVip" class="mt-4 rounded-lg border border-violet-200 bg-violet-50 p-3">
        <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-violet-700">VIP AI</p>
        <div class="flex flex-wrap gap-2">
          <button type="button" class="rounded border border-violet-300 bg-white px-2 py-1 text-xs text-violet-700" :disabled="aiLoading" @click="runAi('suggestions')">Sugereaza AI</button>
          <button type="button" class="rounded border border-violet-300 bg-white px-2 py-1 text-xs text-violet-700" :disabled="aiLoading" @click="runAi('routine')">Creeaza rutina cu AI</button>
        </div>
        <p v-if="aiText" class="mt-2 whitespace-pre-line text-xs text-slate-700">{{ aiText }}</p>
      </div>

      <p v-if="error" class="mt-3 text-xs text-red-600">{{ error }}</p>

      <div class="mt-4 flex justify-end gap-2">
        <button type="button" class="rounded border border-slate-300 px-3 py-2 text-xs" @click="emit('close')">{{ copy.cancel }}</button>
        <button type="button" class="rounded bg-teal-600 px-3 py-2 text-xs font-semibold text-white" :disabled="saving" @click="save">
          {{ saving ? copy.saving : copy.save }}
        </button>
      </div>
    </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from '#imports'
import { useCalendarTasks } from '~/composables/calendar/useCalendarTasks'

type Capabilities = {
  advanced_task_options: boolean
  ai_habit_suggestions: boolean
  ai_routine_builder: boolean
}

const props = defineProps<{
  open: boolean
  selectedDate: string
  capabilities: Capabilities
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const {
  createTask,
  aiHabitSuggestions,
  aiRoutineBuilder,
} = useCalendarTasks()

const copy = {
  title: 'Adauga task',
  taskTitle: 'Titlu',
  description: 'Descriere',
  duration: 'Durata (minute)',
  frequency: 'Frecventa',
  time: 'Ora',
  reminder: 'Reminder',
  reminderBefore: 'Minute inainte',
  advanced: 'Optiuni avansate (PREMIUM)',
  save: 'Salveaza task',
  saving: 'Se salveaza...',
  cancel: 'Anuleaza',
}

const form = reactive({
  title: '',
  description: '',
  duration_minutes: 15,
  frequency: 'daily',
  start_time: '',
  reminder_enabled: false,
  reminder_minutes_before: 10,
})

const advancedText = ref('')
const saving = ref(false)
const error = ref('')
const aiLoading = ref(false)
const aiText = ref('')

const isVip = computed(() => props.capabilities.ai_habit_suggestions || props.capabilities.ai_routine_builder)

watch(
  () => props.open,
  (open: boolean) => {
    if (!open) return
    error.value = ''
    aiText.value = ''
    form.title = ''
    form.description = ''
    form.duration_minutes = 15
    form.frequency = props.capabilities.advanced_task_options ? 'daily' : 'weekly'
    form.start_time = ''
    form.reminder_enabled = false
    form.reminder_minutes_before = 10
    advancedText.value = ''
  }
)

function parseAdvancedOptions(raw: string): Record<string, string> {
  const pairs = raw.split(';').map((item) => item.trim()).filter(Boolean)
  const out: Record<string, string> = {}
  for (const pair of pairs) {
    const [key, ...rest] = pair.split('=')
    const value = rest.join('=').trim()
    if (key && value) out[key.trim()] = value
  }
  return out
}

async function runAi(mode: 'suggestions' | 'routine') {
  aiLoading.value = true
  error.value = ''
  try {
    const context = `Data selectata: ${props.selectedDate}\nTask curent: ${form.title || '(fara titlu)'}\nDescriere: ${form.description || '(fara descriere)'}`
    const res = mode === 'suggestions'
      ? await aiHabitSuggestions(context)
      : await aiRoutineBuilder(context)
    aiText.value = res.result
    if (!form.description) {
      form.description = res.result.slice(0, 450)
    }
  } catch {
    error.value = 'Nu am putut obtine un raspuns AI acum.'
  } finally {
    aiLoading.value = false
  }
}

async function save() {
  if (!form.title.trim()) {
    error.value = 'Titlul este obligatoriu.'
    return
  }
  saving.value = true
  error.value = ''
  try {
    await createTask({
      title: form.title.trim(),
      description: form.description.trim(),
      duration_minutes: form.duration_minutes,
      frequency: form.frequency as 'daily' | 'weekly' | 'monthly' | 'custom',
      start_time: form.start_time || null,
      reminder_enabled: !!form.reminder_enabled,
      reminder_minutes_before: form.reminder_minutes_before,
      advanced_options: props.capabilities.advanced_task_options ? parseAdvancedOptions(advancedText.value) : {},
      starts_on: props.selectedDate,
    })
    emit('saved')
    emit('close')
  } catch {
    error.value = 'Nu am putut salva task-ul.'
  } finally {
    saving.value = false
  }
}
</script>
