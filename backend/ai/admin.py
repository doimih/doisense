from django.contrib import admin
from .models import (
    AILog,
    Conversation,
    ConversationTemplate,
    DailyReport,
    EmotionalAnalysis,
    MonthlyReport,
    Question,
    WeeklyReport,
    WellnessMetric,
)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "module", "plan_tier", "created_at")
    list_filter = ("module", "plan_tier", "created_at")
    search_fields = ("user__email", "user_message", "ai_response")
    readonly_fields = ("user", "module", "plan_tier", "user_message", "ai_response", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConversationTemplate)
class ConversationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "language")


@admin.register(AILog)
class AILogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "model", "created_at")
    list_filter = ("model",)
    readonly_fields = ("user", "model", "prompt_hash", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "updated_at")
    list_filter = ("date",)
    search_fields = ("user__email", "summary")


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "week_start", "updated_at")
    list_filter = ("week_start",)
    search_fields = ("user__email", "summary")


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "year", "month", "updated_at")
    list_filter = ("year", "month")
    search_fields = ("user__email", "summary")


@admin.register(EmotionalAnalysis)
class EmotionalAnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "dominant_emotion", "created_at")
    list_filter = ("dominant_emotion",)
    search_fields = ("user__email", "dominant_emotion", "observations")


@admin.register(WellnessMetric)
class WellnessMetricAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "stress_score", "energy_score", "motivation_score", "created_at")
    search_fields = ("user__email",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question_type", "priority", "created_at")
    list_filter = ("question_type", "priority")
    search_fields = ("user__email", "text", "reason")
