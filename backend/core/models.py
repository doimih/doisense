from django.core.cache import cache
from django.db import models

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
    stripe_price_id_premium = models.CharField(max_length=255, blank=True)

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
        default="You are a supportive wellbeing assistant. Respond in the user's language. Be empathetic and concise.",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_systemconfig"
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configuration"

    def save(self, *args, **kwargs):
        # Keep this as a singleton row for predictable runtime lookups.
        self.pk = 1
        if not self.enabled_languages:
            self.enabled_languages = ["ro", "en", "de", "it", "es", "pl"]
        super().save(*args, **kwargs)
        cache.delete("core:system_config")

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "System Configuration"
