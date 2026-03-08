from django.contrib import admin
from .models import JournalQuestion, JournalEntry


@admin.register(JournalQuestion)
class JournalQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "category", "language", "active")
    list_filter = ("language", "active")


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "created_at")
    list_filter = ("created_at",)
