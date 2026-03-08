from django.conf import settings
from django.db import models

from core.validators import validate_language


class ConversationTemplate(models.Model):
    name = models.CharField(max_length=100)
    language = models.CharField(max_length=2, validators=[validate_language])
    prompt = models.TextField()

    class Meta:
        db_table = "ai_conversationtemplate"

    def __str__(self):
        return f"{self.name} ({self.language})"


class AILog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    model = models.CharField(max_length=50)
    prompt_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_ailog"
