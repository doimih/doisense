<template>
  <section v-if="initError" class="profile-card">
    <div class="rounded-lg border border-red-200 bg-red-50 p-3">
      <p class="text-sm text-red-700">{{ initError }}</p>
    </div>
  </section>
  <section v-else class="profile-card" id="profile-habits">
    <div class="profile-section-head">
      <h3>Obiceiurile mele</h3>
      <span class="profile-plan-chip">{{ planLabel }}</span>
    </div>

    <div class="profile-grid-2">
      <div class="habit-panel">
        <p class="habit-kpi-label">Task-uri active</p>
        <p class="habit-kpi-value">{{ stats?.simple.active_tasks ?? 0 }}</p>
      </div>
      <div class="habit-panel">
        <p class="habit-kpi-label">Check-in-uri completate</p>
        <p class="habit-kpi-value">{{ stats?.simple.completed_checkins_total ?? 0 }}</p>
      </div>
    </div>

    <div class="mt-3 rounded-lg border border-slate-200 bg-slate-50 p-3">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-600">Task-uri active</p>
      <div class="space-y-2">
        <div v-for="task in tasks.slice(0, 8)" :key="task.id" class="rounded border border-slate-200 bg-white px-3 py-2">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-slate-800">{{ task.title }}</p>
              <p class="text-xs text-slate-500">{{ task.description || 'Fara descriere' }}</p>
              <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                <span>{{ task.frequency }} · {{ task.duration_minutes }} min</span>
                <span v-if="task.source === 'program'" class="rounded bg-amber-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] text-amber-700">
                  Program · ziua {{ task.program_day }}
                </span>
              </div>
            </div>
            <button type="button" class="profile-tag profile-tag-danger" :disabled="deleteLoadingId === task.id" @click="removeTask(task.id)">
              {{ deleteLoadingId === task.id ? 'Se sterge...' : 'Sterge' }}
            </button>
          </div>
        </div>
        <p v-if="!tasks.length" class="rounded border border-dashed border-slate-300 bg-white px-3 py-3 text-xs text-slate-500">
          Nu exista inca task-uri pe acest cont.
        </p>
      </div>
    </div>

    <div v-if="stats?.advanced" class="mt-3 grid grid-cols-1 gap-3 md:grid-cols-3">
      <div class="habit-panel">
        <p class="habit-kpi-label">Streak curent</p>
        <p class="habit-kpi-value">{{ stats.advanced.current_streak }}</p>
      </div>
      <div class="habit-panel">
        <p class="habit-kpi-label">Best streak</p>
        <p class="habit-kpi-value">{{ stats.advanced.best_streak }}</p>
      </div>
      <div class="habit-panel">
        <p class="habit-kpi-label">Completari luna</p>
        <p class="habit-kpi-value">{{ stats.advanced.completed_month }}</p>
      </div>
    </div>

    <div v-if="capabilities.profile_monthly_view" class="mt-3 rounded-lg border border-slate-200 bg-white p-3">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-600">Calendar monthly view</p>
      <div class="grid grid-cols-7 gap-1 text-center text-[10px] text-slate-400">
        <span v-for="day in dayNames" :key="day">{{ day }}</span>
      </div>
      <div class="mt-1 grid grid-cols-7 gap-1">
        <div v-for="cell in monthCells" :key="cell.key" class="h-7 rounded border text-center text-[11px] leading-7" :class="calendarClass(cell)">
          {{ cell.day || '' }}
        </div>
      </div>
    </div>

    <div v-if="isVip" class="mt-3 rounded-lg border border-violet-200 bg-violet-50 p-3">
      <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-violet-700">VIP Executive AI</p>
      <div class="flex flex-wrap gap-2">
        <button type="button" class="profile-tag" :disabled="aiLoading" @click="runAi('insights')">AI Progress Insights</button>
        <button type="button" class="profile-tag" :disabled="aiLoading" @click="runAi('optimize')">AI Habit Optimization</button>
        <button type="button" class="profile-tag" :disabled="aiLoading" @click="runAi('checkin')">AI Daily Check-in</button>
      </div>
      <p v-if="aiText" class="mt-2 whitespace-pre-line text-xs text-slate-700">{{ aiText }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from '#imports'
import { useCalendarTasks } from '~/composables/calendar/useCalendarTasks'

const {
  capabilities,
  planCode,
  tasks,
  markers,
  stats,
  fetchCapabilities,
  fetchTasks,
  fetchStats,
  deleteTask,
  aiDailyCheckin,
  aiProgressInsights,
  aiHabitOptimization,
} = useCalendarTasks()

const dayNames = ['L', 'M', 'M', 'J', 'V', 'S', 'D']
const aiLoading = ref(false)
const aiText = ref('')
const deleteLoadingId = ref<number | null>(null)
const initError = ref('')

const isVip = computed(() => planCode.value === 'vip')
const planLabel = computed(() => {
  if (planCode.value === 'vip') return 'VIP Executive'
  if (planCode.value === 'premium') return 'PREMIUM Flow'
  return 'BASIC Start'
})

const monthCells = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()
  const first = new Date(year, month, 1)
  const last = new Date(year, month + 1, 0)
  const offset = (first.getDay() + 6) % 7
  const total = last.getDate()
  const arr: Array<{ key: string; day: number | null; iso: string | null }> = []
  for (let i = 0; i < 42; i += 1) {
    const d = i - offset + 1
    if (d < 1 || d > total) {
      arr.push({ key: `o-${i}`, day: null, iso: null })
      continue
    }
    const iso = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    arr.push({ key: iso, day: d, iso })
  }
  return arr
})

function calendarClass(cell: { iso: string | null }) {
  if (!cell.iso) return 'border-transparent bg-transparent'
  const marker = markers.value[cell.iso]
  if (marker?.all_completed) return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  if (marker?.has_tasks) return 'border-amber-200 bg-amber-50 text-amber-700'
  return 'border-slate-200 bg-white text-slate-600'
}

async function runAi(mode: 'insights' | 'optimize' | 'checkin') {
  aiLoading.value = true
  aiText.value = ''
  try {
    const context = `Plan: ${planLabel.value}\nTask-uri active: ${stats.value?.simple.active_tasks ?? 0}\nCompletari totale: ${stats.value?.simple.completed_checkins_total ?? 0}`
    const res = mode === 'insights'
      ? await aiProgressInsights(context)
      : mode === 'optimize'
        ? await aiHabitOptimization(context)
        : await aiDailyCheckin(context)
    aiText.value = res.result
  } catch {
    aiText.value = 'Nu am putut obtine un raspuns AI in acest moment.'
  } finally {
    aiLoading.value = false
  }
}

async function refreshDashboard() {
  const monthKey = new Date().toISOString().slice(0, 7)
  await fetchTasks(monthKey)
  await fetchStats()
}

async function removeTask(taskId: number) {
  deleteLoadingId.value = taskId
  try {
    await deleteTask(taskId)
    await refreshDashboard()
  } finally {
    deleteLoadingId.value = null
  }
}

onMounted(async () => {
  try {
    await fetchCapabilities()
    await refreshDashboard()
  } catch (err) {
    console.error('[HabitsDashboard] Init error:', err)
    initError.value = 'Eroare la incarcarea obiceiurilor'
  }
})
</script>

<style scoped>
.profile-card {
  background: #fafbfa;
  border: 1px solid #d4e4e0;
  border-radius: 6px;
  padding: 20px;
}

.profile-section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.profile-section-head h3 {
  font-size: 10px;
  font-weight: 400;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: #8a9b94;
}

.profile-tag {
  border: 1px solid #d4e4e0;
  background: #fff;
  border-radius: 3px;
  color: #6b7f76;
  padding: 8px 12px;
  font-size: 11px;
  cursor: pointer;
}

.profile-tag-danger {
  border-color: #efc3bc;
  color: #b25a49;
  background: #fff7f5;
}

.profile-grid-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.habit-panel {
  border: 1px solid #d4e4e0;
  border-radius: 6px;
  padding: 12px;
  background: #f7faf8;
}

.habit-kpi-label {
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #7b8b85;
}

.habit-kpi-value {
  margin-top: 4px;
  font-size: 22px;
  color: #2c3e35;
}

.profile-plan-chip {
  padding: 4px 8px;
  border: 1px solid #bfd5cd;
  border-radius: 4px;
  background: #eff7f3;
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #537767;
}

@media (max-width: 980px) {
  .profile-grid-2 {
    grid-template-columns: 1fr;
  }
}
</style>
