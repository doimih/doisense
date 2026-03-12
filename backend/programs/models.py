from django.conf import settings
from django.db import models
from django.utils import timezone

from core.validators import validate_language


class GuidedProgram(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=2, validators=[validate_language])
    active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)

    class Meta:
        db_table = "programs_guidedprogram"

    def __str__(self):
        return self.title


class GuidedProgramDay(models.Model):
    program = models.ForeignKey(
        GuidedProgram, on_delete=models.CASCADE, related_name="days"
    )
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    question = models.TextField(blank=True)
    ai_prompt = models.TextField(blank=True)

    class Meta:
        db_table = "programs_guidedprogramday"
        ordering = ["day_number"]
        unique_together = [("program", "day_number")]

    def __str__(self):
        return f"{self.program.title} - Day {self.day_number}"


class UserProgramProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="program_progress",
    )
    program = models.ForeignKey(
        GuidedProgram, on_delete=models.CASCADE, related_name="progress"
    )
    current_day = models.PositiveIntegerField(default=1)
    completed_days = models.JSONField(default=list)
    is_paused = models.BooleanField(default=False)
    paused_at = models.DateTimeField(null=True, blank=True)
    dropout_marked_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "programs_userprogramprogress"
        unique_together = [("user", "program")]

    def __str__(self):
        return f"{self.user} - {self.program.title} (day {self.current_day})"

    def mark_day_complete(self, day_number: int) -> None:
        if day_number not in self.completed_days:
            self.completed_days.append(day_number)
        if day_number >= self.current_day:
            self.current_day = day_number + 1
        self.is_paused = False
        self.paused_at = None
        self.save(
            update_fields=[
                "completed_days",
                "current_day",
                "is_paused",
                "paused_at",
                "last_active_at",
            ]
        )

    def pause(self) -> None:
        if self.is_paused:
            return
        self.is_paused = True
        self.paused_at = timezone.now()
        self.save(update_fields=["is_paused", "paused_at", "last_active_at"])

    def resume(self) -> None:
        if not self.is_paused:
            return
        self.is_paused = False
        self.paused_at = None
        self.save(update_fields=["is_paused", "paused_at", "last_active_at"])


class ProgramReflection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="program_reflections",
    )
    program = models.ForeignKey(
        GuidedProgram,
        on_delete=models.CASCADE,
        related_name="reflections",
    )
    day_number = models.PositiveIntegerField()
    reflection_text = models.TextField()
    ai_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "programs_programreflection"
        unique_together = [("user", "program", "day_number")]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Reflection: user={self.user_id}, program={self.program_id}, day={self.day_number}"
