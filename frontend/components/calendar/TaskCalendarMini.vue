<template>
  <div v-if="initError" class="mt-3 rounded-lg border border-red-200 bg-red-50 p-3">
    <p class="text-xs text-red-700">{{ initError }}</p>
  </div>
  <div v-else class="mt-3 rounded-xl border border-slate-200 bg-white p-3">
    <div class="mb-2 flex items-center justify-between">
      <p class="text-[11px] uppercase tracking-[0.18em] text-slate-500">Calendar task-uri</p>
      <div class="flex items-center gap-1">
        <button type="button" class="rounded border border-slate-200 px-2 py-1 text-[10px]" @click="prevMonth">◀</button>
        <button type="button" class="rounded border border-slate-200 px-2 py-1 text-[10px]" @click="nextMonth">▶</button>
      </div>
    </div>
    <p class="mb-2 text-xs font-semibold text-slate-700">{{ monthLabel }}</p>

    <div class="grid grid-cols-7 gap-1 text-center text-[10px] text-slate-400">
      <span v-for="day in dayNames" :key="day">{{ day }}</span>
    </div>

    <div class="mt-1 grid grid-cols-7 gap-1">
      <button
        v-for="cell in cells"
        :key="cell.key"
        type="button"
        class="relative h-8 rounded border text-[11px]"
        :class="cellClass(cell)"
        @click="selectDate(cell.isoDate)"
      >
        <span>{{ cell.day }}</span>
        <span v-if="cell.marker?.has_tasks" class="absolute bottom-0.5 left-1/2 h-1 w-1 -translate-x-1/2 rounded-full" :class="cell.marker.all_completed ? 'bg-emerald-500' : 'bg-amber-500'" />
      </button>
    </div>

    <div class="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-2">
      <p class="text-xs font-semibold text-slate-700">{{ selectedDate }}</p>
      <p class="mt-1 text-[11px] text-slate-500">Task-uri active: {{ selectedTasks.length }}</p>
      <div class="mt-2 max-h-28 space-y-1 overflow-y-auto">
        <div v-for="task in selectedTasks" :key="task.id" class="flex items-center justify-between rounded border border-slate-200 bg-white px-2 py-1">
          <div class="min-w-0">
            <span class="truncate text-[11px] text-slate-700">{{ task.title }}</span>
            <p v-if="task.source === 'program'" class="text-[10px] uppercase tracking-[0.12em] text-amber-700">
              Program ghidat · ziua {{ task.program_day }}
            </p>
          </div>
          <button type="button" class="rounded bg-teal-600 px-1.5 py-0.5 text-[10px] text-white" @click="toggleDone(task)">✓</button>
        </div>
        <p v-if="!selectedTasks.length" class="text-[11px] text-slate-500">Niciun task pentru ziua selectata.</p>
      </div>
      <button type="button" class="mt-2 w-full rounded bg-slate-900 px-2 py-1.5 text-[11px] font-semibold text-white" @click="modalOpen = true">
        + Adauga task
      </button>
    </div>

    <TaskCreateModal
      :open="modalOpen"
      :selected-date="selectedDate"
      :capabilities="capabilities"
      @close="modalOpen = false"
      @saved="refreshMonth"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import TaskCreateModal from '~/components/calendar/TaskCreateModal.vue'
import { useCalendarTasks } from '~/composables/calendar/useCalendarTasks'

const {
  capabilities,
  tasks,
  markers,
  fetchCapabilities,
  fetchTasks,
  checkTask,
} = useCalendarTasks()

const today = new Date()
const visibleYear = ref(today.getFullYear())
const visibleMonth = ref(today.getMonth() + 1)
const selectedDate = ref(toIso(today))
const modalOpen = ref(false)
const initError = ref('')

const dayNames = ['L', 'M', 'M', 'J', 'V', 'S', 'D']

function toIso(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const monthLabel = computed(() => {
  return new Date(visibleYear.value, visibleMonth.value - 1, 1).toLocaleDateString('ro-RO', {
    month: 'long',
    year: 'numeric',
  })
})

const monthKey = computed(() => `${visibleYear.value}-${String(visibleMonth.value).padStart(2, '0')}`)

const cells = computed(() => {
  const start = new Date(visibleYear.value, visibleMonth.value - 1, 1)
  const end = new Date(visibleYear.value, visibleMonth.value, 0)
  const offset = (start.getDay() + 6) % 7
  const totalDays = end.getDate()
  const out: Array<{ key: string; day: number; isoDate: string; inMonth: boolean; marker?: { has_tasks: boolean; all_completed: boolean } }> = []

  for (let i = 0; i < 42; i += 1) {
    const dayNum = i - offset + 1
    const inMonth = dayNum >= 1 && dayNum <= totalDays
    const d = inMonth
      ? new Date(visibleYear.value, visibleMonth.value - 1, dayNum)
      : new Date(visibleYear.value, visibleMonth.value - 1, 1)
    const isoDate = inMonth ? toIso(d) : `outside-${i}`
    const marker = inMonth ? markers.value[isoDate] : undefined

    out.push({
      key: `${isoDate}-${i}`,
      day: inMonth ? dayNum : 0,
      isoDate,
      inMonth,
      marker: marker ? { has_tasks: marker.has_tasks, all_completed: marker.all_completed } : undefined,
    })
  }

  return out
})

const selectedTasks = computed(() => {
  const day = new Date(selectedDate.value)
  const weekday = (day.getDay() + 6) % 7
  const monthDay = day.getDate()
  return tasks.value.filter((task: { is_active: boolean; frequency: string; weekdays?: number[]; month_days?: number[] }) => {
    if (!task.is_active) return false
    if (task.frequency === 'daily') return true
    if (task.frequency === 'weekly') {
      const weekdays = task.weekdays?.length ? task.weekdays : [weekday]
      return weekdays.includes(weekday)
    }
    if (task.frequency === 'monthly') {
      const monthDays = task.month_days?.length ? task.month_days : [monthDay]
      return monthDays.includes(monthDay)
    }
    if (task.frequency === 'custom') {
      return (task.weekdays || []).includes(weekday) || (task.month_days || []).includes(monthDay)
    }
    return false
  })
})

function cellClass(cell: { isoDate: string; inMonth: boolean; marker?: { has_tasks: boolean; all_completed: boolean } }) {
  if (!cell.inMonth) return 'border-transparent bg-transparent text-transparent'
  if (selectedDate.value === cell.isoDate) return 'border-teal-400 bg-teal-50 text-teal-800'
  if (cell.marker?.all_completed) return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  if (cell.marker?.has_tasks) return 'border-amber-200 bg-amber-50 text-amber-700'
  return 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
}

function selectDate(isoDate: string) {
  if (isoDate.startsWith('outside-')) return
  selectedDate.value = isoDate
}

function prevMonth() {
  if (visibleMonth.value === 1) {
    visibleMonth.value = 12
    visibleYear.value -= 1
  } else {
    visibleMonth.value -= 1
  }
  void refreshMonth()
}

function nextMonth() {
  if (visibleMonth.value === 12) {
    visibleMonth.value = 1
    visibleYear.value += 1
  } else {
    visibleMonth.value += 1
  }
  void refreshMonth()
}

async function refreshMonth() {
  await fetchTasks(monthKey.value)
}

async function toggleDone(task: { id: number }) {
  await checkTask(task.id, selectedDate.value, true)
  await refreshMonth()
}

onMounted(async () => {
  try {
    await fetchCapabilities()
    await refreshMonth()
  } catch (err) {
    console.error('[TaskCalendarMini] Init error:', err)
    initError.value = 'Eroare la incarcarea calendarului'
  }
})
</script>
