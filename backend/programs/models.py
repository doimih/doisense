from django.conf import settings
from django.db import models
from django.utils import timezone

from core.validators import validate_language


class GuidedProgram(models.Model):
    CATEGORY_WELLNESS = "wellness"
    CATEGORY_COACHING = "coaching"
    CATEGORY_EDUCATIE = "educatie"
    CATEGORY_SUPORT = "suport"

    PLAN_ACCESS_BASIC = "basic"
    PLAN_ACCESS_PREMIUM = "premium"
    PLAN_ACCESS_VIP = "vip"

    CATEGORY_CHOICES = [
        (CATEGORY_WELLNESS, "Wellness"),
        (CATEGORY_COACHING, "Coaching"),
        (CATEGORY_EDUCATIE, "Educatie"),
        (CATEGORY_SUPORT, "Suport"),
    ]

    PLAN_ACCESS_CHOICES = [
        (PLAN_ACCESS_BASIC, "BASIC Start"),
        (PLAN_ACCESS_PREMIUM, "PREMIUM Flow"),
        (PLAN_ACCESS_VIP, "VIP Executive"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES, default=CATEGORY_WELLNESS)
    duration_days = models.PositiveIntegerField(default=7)
    plan_access = models.CharField(max_length=16, choices=PLAN_ACCESS_CHOICES, default=PLAN_ACCESS_BASIC)
    language = models.CharField(max_length=2, validators=[validate_language])
    active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)

    class Meta:
        db_table = "programs_guidedprogram"
        ordering = ["category", "plan_access", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.is_premium = self.plan_access in {self.PLAN_ACCESS_PREMIUM, self.PLAN_ACCESS_VIP}
        super().save(*args, **kwargs)

    @property
    def is_vip_exclusive(self) -> bool:
        return self.plan_access == self.PLAN_ACCESS_VIP


class GuidedProgramDay(models.Model):
    TASK_TYPE_CHECKIN = "check-in"
    TASK_TYPE_EXERCISE = "exercise"
    TASK_TYPE_REFLECTION = "reflection"
    TASK_TYPE_REMINDER = "reminder"
    TASK_TYPE_JOURNALING = "journaling"

    TASK_TYPE_CHOICES = [
        (TASK_TYPE_CHECKIN, "Check-in"),
        (TASK_TYPE_EXERCISE, "Exercise"),
        (TASK_TYPE_REFLECTION, "Reflection"),
        (TASK_TYPE_REMINDER, "Reminder"),
        (TASK_TYPE_JOURNALING, "Journaling"),
    ]

    program = models.ForeignKey(
        GuidedProgram, on_delete=models.CASCADE, related_name="days"
    )
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    task_type = models.CharField(max_length=16, choices=TASK_TYPE_CHOICES, default=TASK_TYPE_CHECKIN)
    estimated_time_minutes = models.PositiveIntegerField(default=10)
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
    start_date = models.DateField(default=timezone.localdate)
    completed_days = models.JSONField(default=list)
    is_paused = models.BooleanField(default=False)
    paused_at = models.DateTimeField(null=True, blank=True)
    dropout_marked_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "programs_userprogramprogress"
        unique_together = [("user", "program")]

    def __str__(self):
        return f"{self.user} - {self.program.title} (day {self.current_day})"

    @property
    def status(self) -> str:
        if self.completed_at is not None:
            return "completed"
        if self.dropout_marked_at is not None:
            return "dropout"
        if self.is_paused:
            return "paused"
        return "active"

    @property
    def progress_day(self) -> int:
        return self.current_day

    def reset_activation(self, start_date=None) -> None:
        self.current_day = 1
        self.completed_days = []
        self.is_paused = False
        self.paused_at = None
        self.dropout_marked_at = None
        self.completed_at = None
        self.start_date = start_date or timezone.localdate()
        self.save(
            update_fields=[
                "current_day",
                "completed_days",
                "is_paused",
                "paused_at",
                "dropout_marked_at",
                "completed_at",
                "start_date",
                "last_active_at",
            ]
        )

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

    def complete_program(self) -> None:
        """Mark the entire program as finished."""
        if self.completed_at is not None:
            return
        self.completed_at = timezone.now()
        self.current_day = max(self.current_day, self.program.duration_days)
        self.is_paused = False
        self.paused_at = None
        self.save(update_fields=["completed_at", "current_day", "is_paused", "paused_at", "last_active_at"])

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
