from django.contrib import admin
from .models import Conversation, ConversationTemplate, AILog


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
