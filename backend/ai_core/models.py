from django.core.exceptions import ValidationError
from django.db import models

from .validators import ENGLISH_ONLY_ERROR, validate_english_prompt_content


class Prompt(models.Model):
    TYPE_SYSTEM = "system"
    TYPE_PERSONALITY = "personality"
    TYPE_RULES = "rules"
    TYPE_CONTEXT = "context"
    TYPE_GREETING = "greeting"
    TYPE_FALLBACK = "fallback"
    TYPE_SKILL = "skill"

    TYPE_CHOICES = [
        (TYPE_SYSTEM, "System"),
        (TYPE_PERSONALITY, "Personality"),
        (TYPE_RULES, "Rules"),
        (TYPE_CONTEXT, "Context"),
        (TYPE_GREETING, "Greeting"),
        (TYPE_FALLBACK, "Fallback"),
        (TYPE_SKILL, "Skill"),
    ]

    name = models.CharField(max_length=120, unique=True)
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    content = models.TextField(validators=[validate_english_prompt_content])
    language = models.CharField(max_length=8, default="en")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_core_prompt"
        ordering = ["type", "name"]
        verbose_name = "Prompt"
        verbose_name_plural = "Prompts"

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        validate_english_prompt_content(self.content)
        if (self.language or "en").lower() != "en":
            raise ValidationError({"language": ENGLISH_ONLY_ERROR})

    def save(self, *args, **kwargs):
        self.full_clean()
        previous_state = None
        created = self.pk is None
        if self.pk:
            previous_state = (
                Prompt.objects.filter(pk=self.pk).values("content", "type", "language").first()
            )

        changed = bool(
            previous_state
            and (
                previous_state["content"] != self.content
                or previous_state["type"] != self.type
                or previous_state["language"] != self.language
            )
        )

        super().save(*args, **kwargs)

        try:
            from .orchestrator import invalidate_orchestrator_cache

            invalidate_orchestrator_cache()
        except Exception:
            # Cache invalidation must never block prompt persistence.
            pass

        if (created or changed) and not getattr(self, "_skip_versioning", False):
            from .versioning import create_prompt_version

            create_prompt_version(
                prompt=self,
                updated_by=getattr(self, "_updated_by", ""),
                change_reason=getattr(
                    self,
                    "_change_reason",
                    "Initial version" if created else "Automatic version snapshot",
                ),
            )


class PromptVersion(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name="versions")
    version_number = models.IntegerField()
    content_snapshot = models.TextField()
    type_snapshot = models.CharField(max_length=32, choices=Prompt.TYPE_CHOICES)
    language_snapshot = models.CharField(max_length=8)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=255, blank=True, default="")
    change_reason = models.TextField(blank=True, default="")

    class Meta:
        db_table = "ai_core_promptversion"
        ordering = ["-updated_at", "-version_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["prompt", "version_number"],
                name="ai_core_promptversion_prompt_version_uniq",
            )
        ]
        verbose_name = "Prompt Version"
        verbose_name_plural = "Prompt Versions"

    def __str__(self):
        return f"{self.prompt.name} v{self.version_number}"
