from django.contrib import admin

from .models import CalendarPlan, CalendarUserPlan, Task, TaskProgress, TaskStat


@admin.register(CalendarPlan)
class CalendarPlanAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "updated_at")
    search_fields = ("code", "name")


@admin.register(CalendarUserPlan)
class CalendarUserPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "is_active", "started_at", "expires_at", "source")
    list_filter = ("plan", "is_active", "source")
    search_fields = ("user__email",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "frequency", "is_active", "starts_on", "ends_on")
    list_filter = ("frequency", "is_active")
    search_fields = ("title", "user__email")


@admin.register(TaskProgress)
class TaskProgressAdmin(admin.ModelAdmin):
    list_display = ("task", "user", "progress_date", "is_completed", "completed_at")
    list_filter = ("is_completed", "progress_date")
    search_fields = ("task__title", "user__email")


@admin.register(TaskStat)
class TaskStatAdmin(admin.ModelAdmin):
    list_display = ("task", "completion_rate", "current_streak", "best_streak", "last_completed_at")
