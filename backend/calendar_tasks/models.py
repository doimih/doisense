from django.conf import settings
from django.db import models
from django.utils import timezone


class CalendarPlan(models.Model):
    CODE_BASIC = "basic"
    CODE_PREMIUM = "premium"
    CODE_VIP = "vip"

    CODE_CHOICES = [
        (CODE_BASIC, "BASIC Start"),
        (CODE_PREMIUM, "PREMIUM Flow"),
        (CODE_VIP, "VIP Executive"),
    ]

    code = models.CharField(max_length=16, choices=CODE_CHOICES, unique=True)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, default="")
    capabilities = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calendar_plan"
        ordering = ["code"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class CalendarUserPlan(models.Model):
    SOURCE_SYSTEM = "system"
    SOURCE_ADMIN = "admin"
    SOURCE_PAYMENT = "payment"

    SOURCE_CHOICES = [
        (SOURCE_SYSTEM, "System"),
        (SOURCE_ADMIN, "Admin"),
        (SOURCE_PAYMENT, "Payment"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="calendar_user_plans"
    )
    plan = models.ForeignKey(CalendarPlan, on_delete=models.PROTECT, related_name="user_links")
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default=SOURCE_SYSTEM)
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "calendar_user_plan"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "is_active"], name="calendar_up_user_active_idx"),
            models.Index(fields=["expires_at"], name="calendar_up_exp_idx"),
        ]


class Task(models.Model):
    SOURCE_MANUAL = "manual"
    SOURCE_PROGRAM = "program"
    SOURCE_AI = "ai"

    SOURCE_CHOICES = [
        (SOURCE_MANUAL, "Manual"),
        (SOURCE_PROGRAM, "Program"),
        (SOURCE_AI, "AI"),
    ]

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

    FREQ_DAILY = "daily"
    FREQ_WEEKLY = "weekly"
    FREQ_MONTHLY = "monthly"
    FREQ_CUSTOM = "custom"

    FREQUENCY_CHOICES = [
        (FREQ_DAILY, "Daily"),
        (FREQ_WEEKLY, "Weekly"),
        (FREQ_MONTHLY, "Monthly"),
        (FREQ_CUSTOM, "Custom"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="calendar_tasks"
    )
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True, default="")
    duration_minutes = models.PositiveIntegerField(default=15)
    frequency = models.CharField(max_length=16, choices=FREQUENCY_CHOICES, default=FREQ_DAILY)
    weekdays = models.JSONField(default=list, blank=True)
    month_days = models.JSONField(default=list, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    reminder_enabled = models.BooleanField(default=False)
    reminder_minutes_before = models.PositiveIntegerField(default=10)
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    task_type = models.CharField(
        max_length=16, choices=TASK_TYPE_CHOICES, default=TASK_TYPE_CHECKIN
    )
    advanced_options = models.JSONField(default=dict, blank=True)
    ai_generated = models.BooleanField(default=False)
    ai_metadata = models.JSONField(default=dict, blank=True)
    guided_program = models.ForeignKey(
        "programs.GuidedProgram",
        on_delete=models.SET_NULL,
        related_name="generated_tasks",
        null=True,
        blank=True,
    )
    program_day = models.PositiveIntegerField(null=True, blank=True)
    starts_on = models.DateField(default=timezone.localdate)
    ends_on = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calendar_task"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"], name="calendar_task_user_active_idx"),
            models.Index(fields=["user", "starts_on"], name="calendar_task_user_start_idx"),
            models.Index(fields=["user", "created_at"], name="calendar_task_user_created_idx"),
        ]


class TaskProgress(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="progress_entries")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_progress_entries"
    )
    progress_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    note = models.CharField(max_length=280, blank=True, default="")
    mood_score = models.PositiveSmallIntegerField(null=True, blank=True)
    energy_score = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calendar_task_progress"
        ordering = ["-progress_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["task", "progress_date"], name="calendar_tp_task_day_uq"
            ),
        ]
        indexes = [
            models.Index(fields=["user", "progress_date"], name="calendar_tp_user_day_idx"),
            models.Index(fields=["task", "progress_date"], name="calendar_tp_task_day_idx"),
        ]


class TaskStat(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name="stats")
    completed_days = models.PositiveIntegerField(default=0)
    total_days = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    best_streak = models.PositiveIntegerField(default=0)
    completion_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    last_completed_at = models.DateTimeField(null=True, blank=True)
    last_calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calendar_task_stat"
        indexes = [
            models.Index(fields=["completion_rate"], name="calendar_ts_rate_idx"),
        ]
