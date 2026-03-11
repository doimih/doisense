from django.core.cache import cache
from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from .validators import validate_language


class BaseWagtailLandingPage(Page):
    subtitle = models.CharField(max_length=255, blank=True)
    intro = RichTextField(blank=True)
    content = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title", icon="title")),
            ("paragraph", blocks.RichTextBlock(icon="doc-full")),
            (
                "cta",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(required=True)),
                        ("text", blocks.TextBlock(required=False)),
                        ("button_text", blocks.CharBlock(required=False)),
                        ("button_url", blocks.URLBlock(required=False)),
                    ],
                    icon="placeholder",
                ),
            ),
            (
                "faq",
                blocks.StructBlock(
                    [
                        ("question", blocks.CharBlock(required=True)),
                        ("answer", blocks.RichTextBlock(required=True)),
                    ],
                    icon="help",
                ),
            ),
        ],
        blank=True,
        use_json_field=True,
    )
    seo_title_override = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("intro"),
        FieldPanel("content"),
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel("seo_title_override"),
                FieldPanel("seo_description"),
            ],
            heading="SEO",
        )
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []

    class Meta:
        abstract = True


class WagtailHomePage(BaseWagtailLandingPage):
    template = "core/wagtail_landing_page.html"
    max_count = 1

    class Meta:
        verbose_name = "Wagtail Home Page"


class WagtailFeaturesPage(BaseWagtailLandingPage):
    template = "core/wagtail_landing_page.html"
    max_count = 1

    class Meta:
        verbose_name = "Wagtail Features Page"


class WagtailPricingPage(BaseWagtailLandingPage):
    template = "core/wagtail_landing_page.html"
    max_count = 1

    class Meta:
        verbose_name = "Wagtail Pricing Page"


class WagtailAboutPage(BaseWagtailLandingPage):
    template = "core/wagtail_landing_page.html"
    max_count = 1

    class Meta:
        verbose_name = "Wagtail About Page"


class WagtailContactPage(BaseWagtailLandingPage):
    template = "core/wagtail_landing_page.html"
    max_count = 1

    class Meta:
        verbose_name = "Wagtail Contact Page"


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
