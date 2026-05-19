from django import forms
from django.contrib import admin
from django_ckeditor_5.widgets import CKEditor5Widget
from unfold.admin import ModelAdmin

from .models import GuidedProgram, GuidedProgramDay, ProgramReflection, UserProgramProgress


class GuidedProgramDayAdminForm(forms.ModelForm):
    class Meta:
        model = GuidedProgramDay
        fields = "__all__"
        widgets = {
            "content": CKEditor5Widget(config_name="programs_content"),
        }


class GuidedProgramDayInline(admin.TabularInline):
    model = GuidedProgramDay
    extra = 0


@admin.register(GuidedProgram)
class GuidedProgramAdmin(ModelAdmin):
    list_display = (
        "title",
        "category",
        "plan_access",
        "duration_days",
        "language",
        "is_premium",
        "active",
    )
    list_filter = ("category", "plan_access", "language", "is_premium", "active")
    search_fields = ("title", "description")
    inlines = [GuidedProgramDayInline]


@admin.register(GuidedProgramDay)
class GuidedProgramDayAdmin(ModelAdmin):
    form = GuidedProgramDayAdminForm
    change_form_template = "admin/programs/guidedprogramday/change_form.html"
    list_display = ("program", "day_number", "title", "task_type", "estimated_time_minutes")
    list_filter = ("program", "task_type")
    search_fields = ("title", "program__title")
    fieldsets = (
        (
            "Detalii program",
            {
                "fields": ("program", "day_number", "title", "task_type", "estimated_time_minutes"),
            },
        ),
        (
            "Conținut zi",
            {
                "fields": ("content", "question", "ai_prompt"),
            },
        ),
    )


@admin.register(UserProgramProgress)
class UserProgramProgressAdmin(ModelAdmin):
    list_display = (
        "user",
        "program",
        "current_day",
        "start_date",
        "is_paused",
        "completed_at",
        "dropout_marked_at",
        "last_active_at",
    )
    list_filter = ("program", "is_paused", "completed_at")
    search_fields = ("user__email", "program__title")
    readonly_fields = ("started_at", "last_active_at", "dropout_marked_at", "completed_at")


@admin.register(ProgramReflection)
class ProgramReflectionAdmin(ModelAdmin):
    list_display = ("user", "program", "day_number", "updated_at")
    list_filter = ("program",)
    search_fields = ("user__email", "program__title", "reflection_text")
    readonly_fields = ("created_at", "updated_at")
