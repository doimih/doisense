from django.contrib import admin
from .models import ConversationTemplate, AILog


@admin.register(ConversationTemplate)
class ConversationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "language")


@admin.register(AILog)
class AILogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "model", "created_at")
    list_filter = ("model",)
