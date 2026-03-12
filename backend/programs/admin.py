from django.contrib import admin
from .models import GuidedProgram, GuidedProgramDay, ProgramReflection, UserProgramProgress


class GuidedProgramDayInline(admin.TabularInline):
    model = GuidedProgramDay
    extra = 0


@admin.register(GuidedProgram)
class GuidedProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "language", "is_premium", "active")
    list_filter = ("language", "is_premium")
    inlines = [GuidedProgramDayInline]


@admin.register(GuidedProgramDay)
class GuidedProgramDayAdmin(admin.ModelAdmin):
    list_display = ("program", "day_number", "title")


@admin.register(UserProgramProgress)
class UserProgramProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "program", "current_day", "is_paused", "dropout_marked_at", "last_active_at")
    list_filter = ("program", "is_paused")
    search_fields = ("user__email", "program__title")
    readonly_fields = ("started_at", "last_active_at", "dropout_marked_at")


@admin.register(ProgramReflection)
class ProgramReflectionAdmin(admin.ModelAdmin):
    list_display = ("user", "program", "day_number", "updated_at")
    list_filter = ("program",)
    search_fields = ("user__email", "program__title", "reflection_text")
    readonly_fields = ("created_at", "updated_at")
