from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from .validators import validate_language


class CMSPage(models.Model):
    slug = models.SlugField(max_length=120)
    title = models.CharField(max_length=200)
    language = models.CharField(max_length=2, default="ro", validators=[validate_language])
    content = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    show_in_header = models.BooleanField(default=False)
    show_in_footer = models.BooleanField(default=False)
    menu_order = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_cmspage"
        ordering = ["menu_order", "slug", "language"]
        constraints = [
            models.UniqueConstraint(fields=["slug", "language"], name="core_cmspage_slug_language_uniq"),
        ]

    def __str__(self):
        return self.slug


class SystemConfig(models.Model):
    """Singleton system-wide runtime configuration editable from Django admin."""

    # Site language settings
    default_site_language = models.CharField(
        max_length=2,
        default="ro",
        validators=[validate_language],
    )
    enabled_languages = models.JSONField(default=list)

    # Contact/email delivery settings
    contact_notification_email = models.EmailField(blank=True)
    contact_from_email = models.EmailField(blank=True)
    email_host = models.CharField(max_length=255, blank=True)
    email_port = models.PositiveIntegerField(default=587)
    email_host_user = models.CharField(max_length=255, blank=True)
    email_host_password = models.CharField(max_length=255, blank=True)
    email_use_tls = models.BooleanField(default=True)
    email_use_ssl = models.BooleanField(default=False)

    # OAuth settings
    google_client_id = models.CharField(max_length=255, blank=True)
    apple_client_id = models.CharField(max_length=255, blank=True)

    # Stripe settings
    stripe_secret_key = models.CharField(max_length=255, blank=True)
    stripe_webhook_secret = models.CharField(max_length=255, blank=True)
    stripe_price_id_basic = models.CharField(max_length=255, blank=True)
    stripe_price_id_premium = models.CharField(max_length=255, blank=True)
    stripe_price_id_vip = models.CharField(max_length=255, blank=True)

    # WAL-G / PostgreSQL backup settings (Hetzner S3 compatible)
    backup_enabled = models.BooleanField(default=False)
    backup_s3_endpoint = models.CharField(max_length=255, blank=True)
    backup_s3_bucket = models.CharField(max_length=255, blank=True)
    backup_s3_path_prefix = models.CharField(max_length=255, blank=True, default="postgresql")
    backup_access_key_id = models.CharField(max_length=255, blank=True)
    backup_secret_access_key = models.CharField(max_length=255, blank=True)
    backup_region = models.CharField(max_length=64, blank=True, default="eu-central")
    backup_force_path_style = models.BooleanField(default=True)
    backup_schedule_minutes = models.PositiveSmallIntegerField(default=10)
    backup_delta_max_steps = models.PositiveSmallIntegerField(default=6)
    backup_retention_full_count = models.PositiveSmallIntegerField(default=14)

    # AI settings
    ai_provider = models.CharField(
        max_length=20,
        choices=[("auto", "Auto"), ("openai", "OpenAI"), ("anthropic", "Anthropic")],
        default="auto",
    )
    ai_openai_api_key = models.CharField(max_length=255, blank=True)
    ai_anthropic_api_key = models.CharField(max_length=255, blank=True)
    ai_openai_model = models.CharField(max_length=100, blank=True, default="gpt-4o-mini")
    ai_anthropic_model = models.CharField(
        max_length=100,
        blank=True,
        default="claude-3-5-haiku-20241022",
    )
    ai_chat_rate_limit = models.PositiveIntegerField(default=20)
    ai_temperature = models.DecimalField(max_digits=3, decimal_places=2, default=0.70)
    ai_max_tokens = models.PositiveIntegerField(default=1024)
    ai_request_timeout_seconds = models.PositiveIntegerField(default=45)
    ai_system_prompt_base = models.TextField(
        blank=True,
        default=(
            "You are the AI ORCHESTRATOR for a wellness platform. "
            "Manage logic, analysis, and personalized wellness content by package tier (BASIC, PREMIUM, VIP). "
            "Use only anonymized data and user_id. Do not invent data. "
            "Do not provide medical diagnosis or medical advice. "
            "If data is insufficient, ask clarifying questions. "
            "Keep tone empathetic, calm, and clear. "
            "Adapt behavior strictly by package and requested output type from backend."
        ),
    )

    # reCAPTCHA settings
    recaptcha_enabled = models.BooleanField(default=False)
    recaptcha_site_key = models.CharField(max_length=255, blank=True)
    recaptcha_secret_key = models.CharField(max_length=255, blank=True)
    recaptcha_min_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.50)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_systemconfig"
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configuration"

    def save(self, *args, **kwargs):
        # Keep this as a singleton row for predictable runtime lookups.
        self.pk = 1
        if not self.enabled_languages:
            self.enabled_languages = ["ro", "en", "de", "fr", "it", "es", "pl"]
        super().save(*args, **kwargs)
        cache.delete("core:system_config")

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "System Configuration"


class OAuthConfig(SystemConfig):
    class Meta:
        proxy = True
        verbose_name = "OAuth Configuration"
        verbose_name_plural = "OAuth Configuration"


class StripeConfig(SystemConfig):
    class Meta:
        proxy = True
        verbose_name = "Stripe Configuration"
        verbose_name_plural = "Stripe Configuration"


class AIConfig(SystemConfig):
    class Meta:
        proxy = True
        verbose_name = "AI Configuration"
        verbose_name_plural = "AI Configuration"


class RecaptchaConfig(SystemConfig):
    class Meta:
        proxy = True
        verbose_name = "reCAPTCHA Configuration"
        verbose_name_plural = "reCAPTCHA Configuration"


class BackupConfig(SystemConfig):
    class Meta:
        proxy = True
        verbose_name = "Backup Configuration"
        verbose_name_plural = "Backup Configuration"


class PlatformScheduledJob(models.Model):
    SCHEDULE_HOURLY = "hourly"
    SCHEDULE_DAILY = "daily"
    SCHEDULE_WEEKLY = "weekly"
    SCHEDULE_CHOICES = [
        (SCHEDULE_HOURLY, "Hourly"),
        (SCHEDULE_DAILY, "Daily"),
        (SCHEDULE_WEEKLY, "Weekly"),
    ]

    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    WEEKDAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    code = models.CharField(max_length=64, unique=True)
    label = models.CharField(max_length=120)
    command_name = models.CharField(max_length=120)
    schedule_type = models.CharField(max_length=16, choices=SCHEDULE_CHOICES, default=SCHEDULE_DAILY)
    minute_of_hour = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(59)],
    )
    hour_of_day = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(23)],
    )
    weekday = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=WEEKDAY_CHOICES,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
    )
    enabled = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_run_status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    last_error = models.TextField(blank=True, default="")
    last_duration_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_platformscheduledjob"
        ordering = ["label"]
        verbose_name = "Scheduler Job"
        verbose_name_plural = "Scheduler Jobs"

    def __str__(self):
        return self.label

    def schedule_summary(self) -> str:
        if self.schedule_type == self.SCHEDULE_HOURLY:
            return f"Every hour at minute {self.minute_of_hour:02d}"
        if self.schedule_type == self.SCHEDULE_WEEKLY:
            weekday_label = dict(self.WEEKDAY_CHOICES).get(self.weekday, "Unknown")
            return f"Every {weekday_label} at {self.hour_of_day:02d}:{self.minute_of_hour:02d}"
        return f"Every day at {self.hour_of_day:02d}:{self.minute_of_hour:02d}"

    def is_due(self, now=None) -> bool:
        if not self.enabled:
            return False

        current = timezone.localtime(now or timezone.now())
        last_run = timezone.localtime(self.last_run_at) if self.last_run_at else None

        if self.schedule_type == self.SCHEDULE_HOURLY:
            if current.minute != self.minute_of_hour:
                return False
            return not last_run or (
                last_run.year,
                last_run.month,
                last_run.day,
                last_run.hour,
            ) != (
                current.year,
                current.month,
                current.day,
                current.hour,
            )

        if self.hour_of_day is None or current.hour != self.hour_of_day or current.minute != self.minute_of_hour:
            return False

        if self.schedule_type == self.SCHEDULE_WEEKLY:
            if self.weekday is None or current.weekday() != self.weekday:
                return False

        return not last_run or last_run.date() != current.date()


class UserWellbeingCheckin(models.Model):
    MOOD_LOW = "low"
    MOOD_OK = "ok"
    MOOD_GOOD = "good"
    MOOD_GREAT = "great"
    MOOD_CHOICES = [
        (MOOD_LOW, "Low"),
        (MOOD_OK, "OK"),
        (MOOD_GOOD, "Good"),
        (MOOD_GREAT, "Great"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="wellbeing_checkins",
    )
    mood = models.CharField(max_length=16, choices=MOOD_CHOICES, blank=True)
    energy_level = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_userwellbeingcheckin"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"Wellbeing checkin for {self.user_id} at {self.created_at}"


class NotificationDelivery(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="notification_deliveries",
    )
    notification_type = models.CharField(max_length=64)
    sent_for_date = models.DateField()
    context_key = models.CharField(max_length=64, blank=True, default="")
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_notificationdelivery"
        ordering = ["-sent_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "notification_type", "sent_for_date", "context_key"],
                name="core_notificationdelivery_unique_send",
            ),
        ]
        indexes = [
            models.Index(
                fields=["notification_type", "sent_for_date"],
                name="core_notifi_notific_e5c13f_idx",
            ),
            models.Index(
                fields=["user", "sent_at"],
                name="core_notifi_user_id_b4b702_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.notification_type} for {self.user_id} on "
            f"{self.sent_for_date} ({self.context_key or 'default'})"
        )


class InAppNotification(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="in_app_notifications",
    )
    notification_type = models.CharField(max_length=64)
    title = models.CharField(max_length=160)
    body = models.TextField(blank=True)
    context_key = models.CharField(max_length=64, blank=True, default="")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_inappnotification"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "created_at"]),
            models.Index(fields=["notification_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.notification_type} -> {self.user_id}"


class UserNotificationPreference(models.Model):
    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    push_enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_usernotificationpreference"

    def __str__(self):
        return f"Notification preferences for {self.user_id}"


class SupportTicket(models.Model):
    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
        (PRIORITY_URGENT, "Urgent"),
    ]

    STATUS_OPEN = "open"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_RESOLVED = "resolved"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_RESOLVED, "Resolved"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="support_tickets",
    )
    subject = models.CharField(max_length=180)
    message = models.TextField()
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN)
    assigned_to = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_support_tickets",
    )
    first_response_due_at = models.DateTimeField(null=True, blank=True)
    resolution_due_at = models.DateTimeField(null=True, blank=True)
    first_responded_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    internal_notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_supportticket"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status", "created_at"]),
        ]

    def __str__(self):
        return f"Ticket #{self.id} ({self.status})"


class BackupRestoreRequest(models.Model):
    STATUS_REQUESTED = "requested"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_EXECUTED = "executed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_EXECUTED, "Executed"),
        (STATUS_FAILED, "Failed"),
    ]

    requested_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="backup_restore_requests",
    )
    approved_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_backup_restore_requests",
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    restore_point = models.CharField(max_length=255)
    reason = models.TextField(blank=True, default="")
    confirmation_token = models.CharField(max_length=64, default="CONFIRM_RESTORE")
    execution_notes = models.TextField(blank=True, default="")
    approved_at = models.DateTimeField(null=True, blank=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_backuprestorerequest"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"Restore {self.restore_point} ({self.status})"


class FeatureAccessLog(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="feature_access_logs",
        null=True,
        blank=True,
    )
    feature_key = models.CharField(max_length=64)
    required_tiers = models.JSONField(default=list)
    user_tier = models.CharField(max_length=16, default="anonymous")
    granted = models.BooleanField(default=False)
    reason = models.CharField(max_length=128, blank=True, default="")
    context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_featureaccesslog"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["feature_key", "created_at"]),
            models.Index(fields=["granted", "created_at"]),
        ]

    def __str__(self):
        return f"{self.feature_key} ({'granted' if self.granted else 'denied'})"


class AnalyticsEvent(models.Model):
    EVENT_SOURCE_CHOICES = [
        ("backend", "Backend"),
        ("frontend", "Frontend"),
        ("system", "System"),
    ]

    event_name = models.CharField(max_length=96)
    source = models.CharField(max_length=16, choices=EVENT_SOURCE_CHOICES, default="backend")
    schema_version = models.CharField(max_length=16, default="v1")
    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="analytics_events",
        null=True,
        blank=True,
    )
    session_id = models.CharField(max_length=128, blank=True, default="")
    properties = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_analyticsevent"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_name", "created_at"]),
            models.Index(fields=["source", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_name} ({self.source})"


class UserQuotaUsage(models.Model):
    PERIOD_DAY = "day"
    PERIOD_MONTH = "month"
    PERIOD_CHOICES = [
        (PERIOD_DAY, "Day"),
        (PERIOD_MONTH, "Month"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="quota_usage",
    )
    metric_key = models.CharField(max_length=64)
    period_type = models.CharField(max_length=8, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_userquotausage"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "metric_key", "period_type", "period_start"],
                name="core_userquotausage_unique_period",
            ),
        ]
        indexes = [
            models.Index(fields=["metric_key", "period_start"]),
            models.Index(fields=["user", "updated_at"]),
        ]

    def __str__(self):
        return f"{self.user_id} {self.metric_key} {self.used_count}"


class SystemErrorEvent(models.Model):
    SEVERITY_LOW = "low"
    SEVERITY_MEDIUM = "medium"
    SEVERITY_HIGH = "high"
    SEVERITY_CRITICAL = "critical"
    SEVERITY_CHOICES = [
        (SEVERITY_LOW, "Low"),
        (SEVERITY_MEDIUM, "Medium"),
        (SEVERITY_HIGH, "High"),
        (SEVERITY_CRITICAL, "Critical"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="system_error_events",
        null=True,
        blank=True,
    )
    severity = models.CharField(max_length=16, choices=SEVERITY_CHOICES, default=SEVERITY_HIGH)
    component = models.CharField(max_length=64, default="backend")
    endpoint = models.CharField(max_length=255, blank=True, default="")
    http_method = models.CharField(max_length=12, blank=True, default="")
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    error_type = models.CharField(max_length=128, blank=True, default="")
    message = models.TextField(blank=True, default="")
    context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_systemerrorevent"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["severity", "created_at"]),
            models.Index(fields=["component", "created_at"]),
            models.Index(fields=["status_code", "created_at"]),
        ]

    def __str__(self):
        return f"{self.severity.upper()} {self.error_type or 'Error'}"


class AdminAuditLog(models.Model):
    actor = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="admin_audit_logs",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=64)
    target_model = models.CharField(max_length=128)
    target_object_id = models.CharField(max_length=64)
    before_data = models.JSONField(default=dict, blank=True)
    after_data = models.JSONField(default=dict, blank=True)
    reason = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_adminauditlog"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["target_model", "created_at"]),
            models.Index(fields=["actor", "created_at"]),
        ]

    def __str__(self):
        return f"{self.action} on {self.target_model}:{self.target_object_id}"


class BackupVerificationLog(models.Model):
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    source = models.CharField(max_length=64, blank=True, default="backup_job")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_backupverificationlog"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.status} ({self.created_at})"
