from django.urls import path

from . import views

urlpatterns = [
    path("plan-capabilities", views.CalendarPlanCapabilitiesView.as_view(), name="calendar-plan-capabilities"),
    path("task", views.CalendarTaskCreateView.as_view(), name="calendar-task-create"),
    path("tasks", views.CalendarTasksListView.as_view(), name="calendar-tasks-list"),
    path("task/<int:task_id>", views.CalendarTaskDetailView.as_view(), name="calendar-task-detail"),
    path("task/<int:task_id>/check", views.CalendarTaskCheckView.as_view(), name="calendar-task-check"),
    path("task/<int:task_id>/progress", views.CalendarTaskProgressView.as_view(), name="calendar-task-progress"),
    path("stats", views.CalendarStatsView.as_view(), name="calendar-stats"),
    path("ai/habit-suggestions", views.VipAiHabitSuggestionsView.as_view(), name="calendar-ai-habit-suggestions"),
    path("ai/routine-builder", views.VipAiRoutineBuilderView.as_view(), name="calendar-ai-routine-builder"),
    path("ai/daily-checkin", views.VipAiDailyCheckinView.as_view(), name="calendar-ai-daily-checkin"),
    path("ai/progress-insights", views.VipAiProgressInsightsView.as_view(), name="calendar-ai-progress-insights"),
    path("ai/habit-optimization", views.VipAiHabitOptimizationView.as_view(), name="calendar-ai-habit-optimization"),
]
