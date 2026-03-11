from django.contrib import admin
from .models import GuidedProgram, GuidedProgramDay, UserProgramProgress


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
    list_display = ("user", "program", "current_day", "last_active_at")
    list_filter = ("program",)
    search_fields = ("user__email", "program__title")
    readonly_fields = ("started_at", "last_active_at")
