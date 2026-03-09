from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django import forms
from django.contrib import admin, messages
from django.core.mail import EmailMessage, get_connection
from django.core.files.storage import default_storage
from django.db.models import Min
from django.http import HttpResponseForbidden, JsonResponse
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_exempt
from django_ckeditor_5.widgets import CKEditor5Widget
from unfold.admin import ModelAdmin

from .models import CMSPage, SystemConfig


CMS_TEMPLATE_PRESETS = {
    "legal": """<h2>Scope</h2>\n<p>Describe what this legal page covers.</p>\n\n<h2>Data We Collect</h2>\n<p>List data categories and purpose.</p>\n\n<h2>Your Rights</h2>\n<p>Explain user rights and contact channel.</p>\n\n<h2>Contact</h2>\n<p>Add support/legal contact details.</p>""",
    "marketing": """<h2>Why Doisense</h2>\n<p>Short value proposition for this page.</p>\n\n<h3>Key Benefits</h3>\n<ul><li>Benefit one</li><li>Benefit two</li><li>Benefit three</li></ul>\n\n<h3>How It Works</h3>\n<p>Explain your flow in 2-3 short paragraphs.</p>\n\n<h3>Call to Action</h3>\n<p>Invite users to sign up, start trial, or contact you.</p>""",
}

CMS_FRONTEND_PAGE_CHOICES = [
    ("home", "Home"),
    ("features", "Features"),
    ("pricing", "Pricing"),
    ("about", "About"),
    ("contact", "Contact"),
    ("legal-privacy", "Legal - Privacy"),
    ("legal-terms", "Legal - Terms"),
    ("legal-cookies", "Legal - Cookies"),
    ("legal-gdpr", "Legal - GDPR"),
    ("journal", "Journal"),
    ("programs", "Programs"),
]

LANGUAGE_LABELS = {
    "ro": "Romanian",
    "en": "English",
    "de": "German",
    "it": "Italian",
    "es": "Spanish",
    "pl": "Polish",
}


def get_cms_languages():
    configured = list(getattr(settings, "SUPPORTED_LANGUAGES", ["ro", "en", "de", "it", "es", "pl"]))
    allowed = [language for language in configured if language in LANGUAGE_LABELS]
    return allowed or ["ro", "en", "de", "it", "es", "pl"]


class CMSPageAdminForm(forms.ModelForm):
    template_preset = forms.ChoiceField(
        required=False,
        choices=[
            ("", "No preset"),
            ("legal", "Legal page preset"),
            ("marketing", "Marketing page preset"),
        ],
        help_text="Optional: select a preset to prefill content on save.",
    )
    slug = forms.ChoiceField(
        choices=CMS_FRONTEND_PAGE_CHOICES,
        required=True,
        help_text="Only public frontend pages can be managed from CMS.",
    )
    title_ro = forms.CharField(required=False, label="Title (RO)")
    content_ro = forms.CharField(required=False, label="Content (RO)", widget=CKEditor5Widget(config_name="complete"))
    title_en = forms.CharField(required=False, label="Title (EN)")
    content_en = forms.CharField(required=False, label="Content (EN)", widget=CKEditor5Widget(config_name="complete"))
    title_de = forms.CharField(required=False, label="Title (DE)")
    content_de = forms.CharField(required=False, label="Content (DE)", widget=CKEditor5Widget(config_name="complete"))
    title_it = forms.CharField(required=False, label="Title (IT)")
    content_it = forms.CharField(required=False, label="Content (IT)", widget=CKEditor5Widget(config_name="complete"))
    title_es = forms.CharField(required=False, label="Title (ES)")
    content_es = forms.CharField(required=False, label="Content (ES)", widget=CKEditor5Widget(config_name="complete"))
    title_pl = forms.CharField(required=False, label="Title (PL)")
    content_pl = forms.CharField(required=False, label="Content (PL)", widget=CKEditor5Widget(config_name="complete"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        toolbar_mode = getattr(settings, "ADMIN_WYSIWYG_TOOLBAR_MODE", "complete")
        editor_height = getattr(settings, "ADMIN_WYSIWYG_HEIGHT", 420)

        config_name = "simple" if toolbar_mode == "simple" else "complete"
        self.languages = get_cms_languages()

        for language in self.languages:
            self.fields[f"title_{language}"].label = f"Title ({language.upper()})"
            self.fields[f"content_{language}"].label = f"Content ({language.upper()})"
            self.fields[f"content_{language}"].widget = CKEditor5Widget(
                config_name=config_name,
                attrs={"style": f"min-height: {editor_height}px;"},
            )

        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            pages = {
                page.language: page
                for page in CMSPage.objects.filter(slug=instance.slug)
            }
            default_page = pages.get("ro") or next(iter(pages.values()), None)
            if default_page:
                self.fields["slug"].initial = default_page.slug
                self.fields["is_published"].initial = default_page.is_published
                self.fields["show_in_header"].initial = default_page.show_in_header
                self.fields["show_in_footer"].initial = default_page.show_in_footer
                self.fields["menu_order"].initial = default_page.menu_order

            for language in self.languages:
                variant = pages.get(language)
                if variant:
                    self.fields[f"title_{language}"].initial = variant.title
                    self.fields[f"content_{language}"].initial = variant.content

        # Keep slug dropdown stable even for existing historic slugs.
        current_slug = (self.initial.get("slug") or self.fields["slug"].initial or "").strip()
        if current_slug and current_slug not in dict(CMS_FRONTEND_PAGE_CHOICES):
            self.fields["slug"].choices = [
                (current_slug, f"{current_slug} (legacy)"),
                *CMS_FRONTEND_PAGE_CHOICES,
            ]

    def clean(self):
        cleaned_data = super().clean()
        has_any_title = False
        for language in getattr(self, "languages", ["ro", "en", "de", "it", "es", "pl"]):
            if (cleaned_data.get(f"title_{language}") or "").strip():
                has_any_title = True
                break

        if not has_any_title:
            raise forms.ValidationError("Provide at least one title in any language tab.")

        return cleaned_data

    class Meta:
        model = CMSPage
        fields = (
            "slug",
            "is_published",
            "show_in_header",
            "show_in_footer",
            "menu_order",
        )

    class Media:
        css = {
            "all": ("core/admin/cms-tabs.css",),
        }
        js = ("core/admin/cms-tabs.js",)


class SystemConfigAdminForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("email_use_tls") and cleaned_data.get("email_use_ssl"):
            raise forms.ValidationError(
                "EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be enabled. Select only one."
            )
        return cleaned_data


@admin.register(CMSPage)
class CMSPageAdmin(ModelAdmin):
    form = CMSPageAdminForm
    list_display = (
        "slug",
        "display_title",
        "is_published",
        "show_in_header",
        "show_in_footer",
        "menu_order",
        "updated_at",
    )
    list_filter = ("is_published", "show_in_header", "show_in_footer")
    search_fields = ("slug", "title", "content")

    base_fieldsets = (
        (
            "Content",
            {
                "fields": ("slug", "template_preset"),
            },
        ),
        (
            "Visibility",
            {
                "fields": (
                    "is_published",
                    "show_in_header",
                    "show_in_footer",
                    "menu_order",
                    "preview_link",
                ),
            },
        ),
    )

    readonly_fields = ("preview_link",)

    def get_fieldsets(self, request, obj=None):
        languages = get_cms_languages()
        language_fieldsets = []
        for language in languages:
            language_label = LANGUAGE_LABELS.get(language, language.upper())
            language_fieldsets.append(
                (
                    language_label,
                    {
                        "fields": (f"title_{language}", f"content_{language}"),
                        "classes": ("cms-lang-pane", f"cms-lang-pane-{language}"),
                    },
                )
            )

        return (
            self.base_fieldsets[0],
            *language_fieldsets,
            self.base_fieldsets[1],
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        min_ids = qs.values("slug").annotate(min_id=Min("id")).values_list("min_id", flat=True)
        return qs.filter(id__in=min_ids)

    def display_title(self, obj):
        ro_title = (
            CMSPage.objects.filter(slug=obj.slug, language="ro")
            .values_list("title", flat=True)
            .first()
        )
        en_title = (
            CMSPage.objects.filter(slug=obj.slug, language="en")
            .values_list("title", flat=True)
            .first()
        )
        if ro_title or en_title:
            return ro_title or en_title

        first_title = (
            CMSPage.objects.filter(slug=obj.slug)
            .exclude(title="")
            .values_list("title", flat=True)
            .first()
        )
        return first_title or obj.title

    display_title.short_description = "Title"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "upload-image/",
                csrf_exempt(self.cms_image_upload),
                name="core_cmspage_upload_image",
            ),
        ]
        return custom_urls + urls

    def save_model(self, request, obj, form, change):
        preset = form.cleaned_data.get("template_preset")
        preset_content = CMS_TEMPLATE_PRESETS.get(preset, "")

        languages = get_cms_languages()
        title_by_language = {}
        content_by_language = {}

        for language in languages:
            title = (form.cleaned_data.get(f"title_{language}") or "").strip()
            content = form.cleaned_data.get(f"content_{language}") or ""
            if preset_content and not content:
                content = preset_content
            title_by_language[language] = title
            content_by_language[language] = content

        slug = form.cleaned_data["slug"]
        is_published = form.cleaned_data["is_published"]
        show_in_header = form.cleaned_data["show_in_header"]
        show_in_footer = form.cleaned_data["show_in_footer"]
        menu_order = form.cleaned_data["menu_order"]

        representative_language = "ro" if "ro" in languages else languages[0]
        for language in languages:
            if title_by_language[language] or content_by_language[language]:
                representative_language = language
                break

        # Keep current object as representative row so admin change URL remains stable.
        obj.slug = slug
        obj.language = representative_language
        obj.title = title_by_language[representative_language] or slug.replace("-", " ").title()
        obj.content = content_by_language[representative_language] or ""
        obj.is_published = is_published
        obj.show_in_header = show_in_header
        obj.show_in_footer = show_in_footer
        obj.menu_order = menu_order
        super().save_model(request, obj, form, change)

        for language in languages:
            if language == representative_language:
                continue

            title = title_by_language[language]
            content = content_by_language[language]
            has_variant = bool(title or content)

            if has_variant:
                CMSPage.objects.update_or_create(
                    slug=slug,
                    language=language,
                    defaults={
                        "title": title or obj.title,
                        "content": content,
                        "is_published": is_published,
                        "show_in_header": show_in_header,
                        "show_in_footer": show_in_footer,
                        "menu_order": menu_order,
                    },
                )
            else:
                CMSPage.objects.filter(slug=slug, language=language).delete()

    def preview_link(self, obj):
        if not obj.pk:
            return "Save page first to enable preview."

        url = reverse("cms-page-preview", args=[obj.slug])
        links = []
        for language in get_cms_languages():
            links.append(
                format_html(
                    '<a href="{}?language={}" target="_blank" rel="noopener">{}</a>',
                    url,
                    language,
                    language.upper(),
                )
            )
        return format_html("{}", format_html(" | ").join(links))

    preview_link.short_description = "Preview"

    def cms_image_upload(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseForbidden("Forbidden")

        upload = request.FILES.get("upload")
        if not upload:
            return JsonResponse({"error": {"message": "No file uploaded."}}, status=400)

        allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
        if upload.content_type not in allowed_types:
            return JsonResponse(
                {"error": {"message": "Only JPG, PNG, WEBP, GIF images are allowed."}},
                status=400,
            )

        max_size = 3 * 1024 * 1024
        if upload.size > max_size:
            return JsonResponse(
                {"error": {"message": "Image is too large. Max size is 3MB."}},
                status=400,
            )

        ext = Path(upload.name).suffix.lower() or ".bin"
        filename = f"cms/{uuid4().hex}{ext}"
        saved_path = default_storage.save(filename, upload)

        file_url = request.build_absolute_uri(default_storage.url(saved_path))
        return JsonResponse({"url": file_url})
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
            "OAuth",
            {
                "fields": (
                    "google_client_id",
                    "apple_client_id",
                )
            },
        ),
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "test-email/",
                self.admin_site.admin_view(self.send_test_email),
                name="core_systemconfig_test_email",
            ),
        ]
        return custom_urls + urls

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
