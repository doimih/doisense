import { computed, ref } from '#imports'

type PlanCode = 'basic' | 'premium' | 'vip'

type Capabilities = {
  task_create: boolean
  task_check: boolean
  task_active_view: boolean
  simple_progress: boolean
  chat_month_calendar: boolean
  advanced_stats: boolean
  task_history: boolean
  profile_monthly_view: boolean
  advanced_task_options: boolean
  ai_habit_suggestions: boolean
  ai_routine_builder: boolean
  ai_daily_checkin: boolean
  ai_progress_insights: boolean
  ai_habit_optimization: boolean
}

type TaskItem = {
  id: number
  title: string
  description: string
  duration_minutes: number
  source: 'manual' | 'program' | 'ai'
  task_type: 'check-in' | 'exercise' | 'reflection' | 'reminder' | 'journaling'
  guided_program_id: number | null
  program_day: number | null
  frequency: 'daily' | 'weekly' | 'monthly' | 'custom'
  weekdays: number[]
  month_days: number[]
  start_time: string | null
  reminder_enabled: boolean
  reminder_minutes_before: number
  advanced_options: Record<string, unknown>
  ai_generated: boolean
  starts_on: string
  ends_on: string | null
  is_active: boolean
  stats?: {
    completed_days: number
    total_days: number
    current_streak: number
    best_streak: number
    completion_rate: number
    last_completed_at: string | null
  }
}

type MarkerItem = {
  planned: number
  completed: number
  has_tasks: boolean
  all_completed: boolean
}

type StatsPayload = {
  simple: {
    total_tasks: number
    active_tasks: number
    completed_checkins_total: number
  }
  advanced: null | {
    current_streak: number
    best_streak: number
    completed_week: number
    completed_month: number
    weekly_distribution: Array<{ progress_date: string; completed: number }>
    monthly_distribution: Array<{ progress_date: string; completed: number }>
  }
  plan: { code: PlanCode; capabilities: Capabilities }
}

type TaskPayload = {
  title: string
  description?: string
  duration_minutes?: number
  frequency?: 'daily' | 'weekly' | 'monthly' | 'custom'
  weekdays?: number[]
  month_days?: number[]
  start_time?: string | null
  reminder_enabled?: boolean
  reminder_minutes_before?: number
  advanced_options?: Record<string, unknown>
  starts_on?: string
  ends_on?: string | null
}

const defaultCaps: Capabilities = {
  task_create: false,
  task_check: false,
  task_active_view: false,
  simple_progress: false,
  chat_month_calendar: false,
  advanced_stats: false,
  task_history: false,
  profile_monthly_view: false,
  advanced_task_options: false,
  ai_habit_suggestions: false,
  ai_routine_builder: false,
  ai_daily_checkin: false,
  ai_progress_insights: false,
  ai_habit_optimization: false,
}

export function useCalendarTasks() {
  const { fetchApi } = useApi()

  const loading = ref(false)
  const capabilities = ref<Capabilities>({ ...defaultCaps })
  const planCode = ref<PlanCode>('basic')
  const tasks = ref<TaskItem[]>([])
  const markers = ref<Record<string, MarkerItem>>({})
  const stats = ref<StatsPayload | null>(null)

  const hasAdvanced = computed(() => capabilities.value.advanced_stats)
  const isVip = computed(() => planCode.value === 'vip')

  async function fetchCapabilities() {
    const res = await fetchApi<{ plan: { code: PlanCode; capabilities: Capabilities } }>('/calendar/plan-capabilities')
    planCode.value = res.plan.code
    capabilities.value = { ...defaultCaps, ...res.plan.capabilities }
    return res.plan
  }

  async function fetchTasks(month: string) {
    loading.value = true
    try {
      const res = await fetchApi<{
        items: TaskItem[]
        markers: Record<string, MarkerItem>
      }>(`/calendar/tasks?month=${encodeURIComponent(month)}`)
      tasks.value = res.items
      markers.value = res.markers || {}
      return res
    } finally {
      loading.value = false
    }
  }

  async function createTask(payload: TaskPayload) {
    const row = await fetchApi<TaskItem>('/calendar/task', {
      method: 'POST',
      body: payload,
    })
    return row
  }

  async function updateTask(taskId: number, payload: TaskPayload) {
    return fetchApi<TaskItem>(`/calendar/task/${taskId}`, {
      method: 'PUT',
      body: payload,
    })
  }

  async function deleteTask(taskId: number) {
    return fetchApi<void>(`/calendar/task/${taskId}`, {
      method: 'DELETE',
    })
  }

  async function checkTask(taskId: number, progressDate: string, completed: boolean) {
    return fetchApi(`/calendar/task/${taskId}/check`, {
      method: 'POST',
      body: { progress_date: progressDate, completed },
    })
  }

  async function fetchTaskProgress(taskId: number, from: string, to: string) {
    return fetchApi<{ items: Array<{ progress_date: string; is_completed: boolean }> }>(
      `/calendar/task/${taskId}/progress?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`
    )
  }

  async function fetchStats() {
    const res = await fetchApi<StatsPayload>('/calendar/stats')
    stats.value = res
    return res
  }

  async function aiHabitSuggestions(context: string) {
    return fetchApi<{ result: string }>('/calendar/ai/habit-suggestions', {
      method: 'POST',
      body: { context },
    })
  }

  async function aiRoutineBuilder(context: string) {
    return fetchApi<{ result: string }>('/calendar/ai/routine-builder', {
      method: 'POST',
      body: { context },
    })
  }

  async function aiDailyCheckin(context: string) {
    return fetchApi<{ result: string }>('/calendar/ai/daily-checkin', {
      method: 'POST',
      body: { context },
    })
  }

  async function aiProgressInsights(context: string) {
    return fetchApi<{ result: string }>('/calendar/ai/progress-insights', {
      method: 'POST',
      body: { context },
    })
  }

  async function aiHabitOptimization(context: string) {
    return fetchApi<{ result: string }>('/calendar/ai/habit-optimization', {
      method: 'POST',
      body: { context },
    })
  }

  return {
    loading,
    capabilities,
    planCode,
    tasks,
    markers,
    stats,
    hasAdvanced,
    isVip,
    fetchCapabilities,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    checkTask,
    fetchTaskProgress,
    fetchStats,
    aiHabitSuggestions,
    aiRoutineBuilder,
    aiDailyCheckin,
    aiProgressInsights,
    aiHabitOptimization,
  }
}
