from django.conf import settings
from django.db import models

from core.validators import validate_language


class JournalQuestion(models.Model):
    text = models.TextField()
    category = models.CharField(max_length=50)
    language = models.CharField(max_length=2, validators=[validate_language])
    tags = models.JSONField(default=list, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "journal_journalquestion"

    def __str__(self):
        return self.text[:50]


class JournalEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journal_entries"
    )
    question = models.ForeignKey(
        JournalQuestion, on_delete=models.CASCADE, related_name="entries"
    )
    content = models.TextField()
    emotions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "journal_journalentry"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Entry by {self.user.email} for Q{self.question_id}"
