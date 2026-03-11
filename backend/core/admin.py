import imghdr
import os
import re
import time

from django.conf import settings
from django import forms
from django.contrib import admin, messages
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.core.mail import EmailMessage, get_connection
from django.template.response import TemplateResponse
from django.urls import path, reverse
from unfold.admin import ModelAdmin

from .image_utils import convert_uploaded_image_to_webp
from .models import (
    AIConfig,
    NotificationDelivery,
    OAuthConfig,
    RecaptchaConfig,
    StripeConfig,
    SystemConfig,
)

_MEDIA_LIBRARY_FOLDER = "settings-images"
_MEDIA_LIBRARY_ALLOWED_EXT = {"jpg", "jpeg", "png", "webp", "gif"}
_MEDIA_LIBRARY_ALLOWED_TYPES = {"jpeg", "png", "webp", "gif"}
_MEDIA_LIBRARY_MAX_SIZE = 8 * 1024 * 1024


class SystemConfigAdminForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep sensitive values editable but masked in admin UI.
        masked_fields = [
            "email_host_password",
            "google_client_id",
            "apple_client_id",
            "stripe_secret_key",
            "stripe_webhook_secret",
            "stripe_price_id_premium",
            "backup_access_key_id",
            "backup_secret_access_key",
            "ai_openai_api_key",
            "ai_anthropic_api_key",
            "recaptcha_secret_key",
        ]
        for field_name in masked_fields:
            if field_name in self.fields:
                self.fields[field_name].widget = forms.PasswordInput(
                    render_value=True,
                    attrs={"autocomplete": "new-password"},
                )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("email_use_tls") and cleaned_data.get("email_use_ssl"):
            raise forms.ValidationError(
                "EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be enabled. Select only one."
            )
        return cleaned_data


@admin.register(SystemConfig)
class SystemConfigAdmin(ModelAdmin):
    form = SystemConfigAdminForm
    change_form_template = "admin/core/systemconfig/change_form.html"

    fieldsets = (
        (
            "Localization",
            {
                "fields": (
                    "default_site_language",
                    "enabled_languages",
                )
            },
        ),
        (
            "Contact & Email",
            {
                "fields": (
                    "contact_notification_email",
                    "contact_from_email",
                    "email_host",
                    "email_port",
                    "email_host_user",
                    "email_host_password",
                    "email_use_tls",
                    "email_use_ssl",
                )
            },
        ),
        (
            "WAL-G Backup (Hetzner Object Storage)",
            {
                "fields": (
                    "backup_enabled",
                    "backup_s3_endpoint",
                    "backup_s3_bucket",
                    "backup_s3_path_prefix",
                    "backup_access_key_id",
                    "backup_secret_access_key",
                    "backup_region",
                    "backup_force_path_style",
                    "backup_schedule_minutes",
                    "backup_delta_max_steps",
                    "backup_retention_full_count",
                )
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "test-email/",
                self.admin_site.admin_view(self.send_test_email),
                name="core_systemconfig_test_email",
            ),
            path(
                "media-library/",
                self.admin_site.admin_view(self.media_library_view),
                name="core_media_library",
            ),
        ]
        return custom_urls + urls

    def media_library_view(self, request):
        if not request.user.is_superuser:
            self.message_user(request, "Access denied.", level=messages.ERROR)
            return HttpResponseRedirect(reverse("admin:index"))

        errors = []
        success = None
        uploaded_names = []

        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

        if request.method == "POST":
            uploads = request.FILES.getlist("image")
            if not uploads:
                single_file = request.FILES.get("image")
                if single_file:
                    uploads = [single_file]

            if not uploads:
                errors.append("No file selected.")
            else:
                for uploaded in uploads:
                    if uploaded.size > _MEDIA_LIBRARY_MAX_SIZE:
                        errors.append(f"{uploaded.name}: file exceeds 8 MB limit.")
                        continue

                    ext = uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else ""
                    if ext not in _MEDIA_LIBRARY_ALLOWED_EXT:
                        errors.append(f"{uploaded.name}: unsupported file extension.")
                        continue

                    detected = imghdr.what(uploaded)
                    if detected not in _MEDIA_LIBRARY_ALLOWED_TYPES:
                        errors.append(f"{uploaded.name}: file content does not match an allowed image type.")
                        continue

                    uploaded.seek(0)
                    try:
                        webp_file, stem = convert_uploaded_image_to_webp(uploaded)
                    except ValueError:
                        errors.append(f"{uploaded.name}: failed to process image.")
                        continue

                    dest = f"{_MEDIA_LIBRARY_FOLDER}/{stem}.webp"
                    if default_storage.exists(dest):
                        dest = f"{_MEDIA_LIBRARY_FOLDER}/{stem}_{int(time.time())}.webp"

                    default_storage.save(dest, webp_file)
                    uploaded_names.append(os.path.basename(dest))

                if uploaded_names:
                    success = f"Uploaded {len(uploaded_names)} image(s): {', '.join(uploaded_names)}"

            if is_ajax:
                status_code = 201 if uploaded_names and not errors else (207 if uploaded_names else 400)
                return JsonResponse(
                    {
                        "uploaded": uploaded_names,
                        "errors": errors,
                        "success": success,
                    },
                    status=status_code,
                )

        # Build image list
        folder = os.path.join(settings.MEDIA_ROOT, _MEDIA_LIBRARY_FOLDER)
        items = []
        if os.path.isdir(folder):
            for fname in sorted(os.listdir(folder)):
                fpath = os.path.join(folder, fname)
                if os.path.isfile(fpath):
                    url = request.build_absolute_uri(
                        f"{settings.MEDIA_URL}{_MEDIA_LIBRARY_FOLDER}/{fname}"
                    )
                    size_kb = round(os.path.getsize(fpath) / 1024, 1)
                    items.append({"name": fname, "url": url, "size_kb": size_kb})

        context = {
            **self.admin_site.each_context(request),
            "title": "Media Library",
            "items": items,
            "errors": errors,
            "success": success,
            "upload_url": reverse("admin:core_media_library"),
        }
        return TemplateResponse(request, "admin/core/media_library.html", context)

    def changelist_view(self, request, extra_context=None):
        config = SystemConfig.get_solo()
        url = reverse("admin:core_systemconfig_change", args=[config.pk])
        return HttpResponseRedirect(url)

    def send_test_email(self, request):
        config = SystemConfig.get_solo()
        target = request.user.email

        if config.email_use_tls and config.email_use_ssl:
            self.message_user(
                request,
                "Invalid SMTP settings: TLS and SSL cannot both be enabled. Disable one in Contact & Email tab.",
                level=messages.ERROR,
            )
            return HttpResponseRedirect(reverse("admin:core_systemconfig_changelist"))

        if not target:
            self.message_user(
                request,
                "Current admin user has no email address set.",
                level=messages.ERROR,
            )
            return HttpResponseRedirect(reverse("admin:core_systemconfig_changelist"))

        try:
            connection = get_connection(
                host=config.email_host,
                port=config.email_port,
                username=config.email_host_user,
                password=config.email_host_password,
                use_tls=config.email_use_tls,
                use_ssl=config.email_use_ssl,
                fail_silently=False,
            )

            from_email = (
                config.contact_from_email
                or config.email_host_user
                or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@doisense.app")
            )
            message = EmailMessage(
                subject="Doisense SMTP test",
                body="This is a test email sent from Django Admin System Configuration.",
                from_email=from_email,
                to=[target],
                connection=connection,
            )
            message.send()
            self.message_user(
                request,
                f"Test email sent successfully to {target}.",
                level=messages.SUCCESS,
            )
        except Exception as exc:
            self.message_user(
                request,
                f"Failed to send test email: {exc}",
                level=messages.ERROR,
            )

        return HttpResponseRedirect(reverse("admin:core_systemconfig_changelist"))

    def has_add_permission(self, request):
        # Only one configuration row should exist.
        return not SystemConfig.objects.exists()


@admin.register(NotificationDelivery)
class NotificationDeliveryAdmin(ModelAdmin):
    list_display = ("notification_type", "user", "sent_for_date", "context_key", "sent_at")
    list_filter = ("notification_type", "sent_for_date")
    search_fields = ("user__email", "context_key")
    ordering = ("-sent_at",)


class SingletonProxyConfigAdmin(ModelAdmin):
    form = SystemConfigAdminForm
    change_form_template = "admin/core/systemconfig/change_form.html"

    def changelist_view(self, request, extra_context=None):
        config = SystemConfig.get_solo()
        meta = self.model._meta
        url = reverse(f"admin:{meta.app_label}_{meta.model_name}_change", args=[config.pk])
        return HttpResponseRedirect(url)

    def has_add_permission(self, request):
        return False


@admin.register(OAuthConfig)
class OAuthConfigAdmin(SingletonProxyConfigAdmin):
    fieldsets = (
        (
            "OAuth",
            {
                "fields": (
                    "google_client_id",
                    "apple_client_id",
                )
            },
        ),
    )


@admin.register(StripeConfig)
class StripeConfigAdmin(SingletonProxyConfigAdmin):
    fieldsets = (
        (
            "Stripe",
            {
                "fields": (
                    "stripe_secret_key",
                    "stripe_webhook_secret",
                    "stripe_price_id_premium",
                )
            },
        ),
    )


@admin.register(AIConfig)
class AIConfigAdmin(SingletonProxyConfigAdmin):
    fieldsets = (
        (
            "AI",
            {
                "fields": (
                    "ai_provider",
                    "ai_openai_api_key",
                    "ai_anthropic_api_key",
                    "ai_openai_model",
                    "ai_anthropic_model",
                    "ai_chat_rate_limit",
                    "ai_temperature",
                    "ai_max_tokens",
                    "ai_request_timeout_seconds",
                    "ai_system_prompt_base",
                )
            },
        ),
    )


@admin.register(RecaptchaConfig)
class RecaptchaConfigAdmin(SingletonProxyConfigAdmin):
    fieldsets = (
        (
            "reCAPTCHA",
            {
                "fields": (
                    "recaptcha_enabled",
                    "recaptcha_site_key",
                    "recaptcha_secret_key",
                    "recaptcha_min_score",
                )
            },
        ),
    )

