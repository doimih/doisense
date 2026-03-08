from django.contrib import admin
from .models import GuidedProgram, GuidedProgramDay


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
