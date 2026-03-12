from django.conf import settings
from django.db import models

from core.validators import validate_language


class Conversation(models.Model):
    PLAN_CHOICES = [
        ("free", "Free"),
        ("trial", "Trial"),
        ("basic", "Basic"),
        ("premium", "Premium"),
        ("vip", "VIP"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations",
    )
    module = models.CharField(max_length=32, blank=True)
    plan_tier = models.CharField(max_length=10, choices=PLAN_CHOICES, default="free")
    response_type = models.CharField(max_length=32, blank=True, default="response")
    user_message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_conversation"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]

    def __str__(self):
        return f"Conversation #{self.pk}"


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


class EmotionalAnalysis(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emotional_analyses",
    )
    dominant_emotion = models.CharField(max_length=64, blank=True, default="")
    secondary_emotions = models.JSONField(default=list, blank=True)
    triggers = models.JSONField(default=list, blank=True)
    stress_score = models.FloatField(null=True, blank=True)
    energy_score = models.FloatField(null=True, blank=True)
    motivation_score = models.FloatField(null=True, blank=True)
    observations = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_emotionalanalysis"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]


class WellnessMetric(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wellness_metrics",
    )
    stress_score = models.FloatField(null=True, blank=True)
    energy_score = models.FloatField(null=True, blank=True)
    motivation_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_wellnessmetric"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]


class Question(models.Model):
    TYPE_CHOICES = [
        ("open", "Open"),
        ("multiple_choice", "Multiple Choice"),
        ("rating", "Rating"),
        ("yes_no", "Yes / No"),
    ]
    PRIORITY_CHOICES = [
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generated_questions",
    )
    text = models.TextField()
    question_type = models.CharField(max_length=24, choices=TYPE_CHOICES, default="open")
    reason = models.TextField(blank=True, default="")
    priority = models.CharField(max_length=8, choices=PRIORITY_CHOICES, default="medium")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_question"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]


class DailyReport(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_reports",
    )
    date = models.DateField()
    summary = models.TextField(blank=True, default="")
    highlights = models.JSONField(default=list, blank=True)
    challenges = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_dailyreport"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["user", "date"], name="ai_dailyreport_user_date_uniq"),
        ]


class WeeklyReport(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="weekly_reports",
    )
    week_start = models.DateField()
    summary = models.TextField(blank=True, default="")
    trends = models.JSONField(default=list, blank=True)
    progress = models.TextField(blank=True, default="")
    recommendations = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_weeklyreport"
        ordering = ["-week_start"]
        constraints = [
            models.UniqueConstraint(fields=["user", "week_start"], name="ai_weeklyreport_user_week_uniq"),
        ]


class MonthlyReport(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="monthly_reports",
    )
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    summary = models.TextField(blank=True, default="")
    trends = models.JSONField(default=list, blank=True)
    insights = models.TextField(blank=True, default="")
    recommendations = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_monthlyreport"
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(fields=["user", "year", "month"], name="ai_monthlyreport_user_month_uniq"),
        ]
