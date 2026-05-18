import os
from pathlib import Path

import environ
from django.urls import reverse

env = environ.Env(DEBUG=(bool, False))


def _normalize_public_path_prefix(raw_value: str) -> str:
    value = (raw_value or "").strip()
    if not value or value == "/":
        return ""
    return f"/{value.strip('/')}"


def _public_path(*segments: str, trailing_slash: bool = True) -> str:
    parts = []
    if PUBLIC_PATH_PREFIX:
        parts.append(PUBLIC_PATH_PREFIX.strip("/"))
    parts.extend(segment.strip("/") for segment in segments if segment.strip("/"))
    if not parts:
        return "/"

    path = "/" + "/".join(parts)
    if trailing_slash:
        path += "/"
    return path


def _perm(permission_codename: str):
    return lambda request: request.user.has_perm(permission_codename)

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(BASE_DIR / ".env")

PUBLIC_PATH_PREFIX = _normalize_public_path_prefix(env("PUBLIC_PATH_PREFIX", default="/doisense"))
DEFAULT_FRONTEND_BASE_URL = env(
    "DEFAULT_FRONTEND_BASE_URL",
    default=f"https://projects.doimih.net{PUBLIC_PATH_PREFIX}" if PUBLIC_PATH_PREFIX else "https://projects.doimih.net",
)
ADMIN_SITE_URL = env("ADMIN_SITE_URL", default=DEFAULT_FRONTEND_BASE_URL)
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", default=DEFAULT_FRONTEND_BASE_URL)
ADMIN_STATIC_URL = env("STATIC_URL", default=_public_path("ro/admin/static"))

SECRET_KEY = env(
    "SECRET_KEY",
    default="dev-secret-change-in-production-please-override-with-32-plus-chars",
)
DEBUG = env("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
AI_BUDGET_ALERT_THRESHOLD_USD = env.float("AI_BUDGET_ALERT_THRESHOLD_USD", default=20.0)

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.forms",
    "django_ckeditor_5",
    "crispy_forms",
    "crispy_tailwind",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "sorl.thumbnail",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "core",
    "users",
    "profiles",
    "journal",
    "programs",
    "calendar_tasks",
    "ai",
    "payments",
    "ai_core",
]

UNFOLD = {
    "SITE_TITLE": "Doisense Admin",
    "SITE_HEADER": "Doisense",
    "SITE_SYMBOL": "dashboard",
    "SITE_URL": ADMIN_SITE_URL,
    "SHOW_HISTORY": True,
    "STYLES": [
        f"{ADMIN_STATIC_URL}admin/css/unfold_custom_fields.css",
    ],
    "SCRIPTS": [
        f"{ADMIN_STATIC_URL}admin/js/unfold_wysiwyg_toolbar.js",
        f"{ADMIN_STATIC_URL}admin/js/unfold_sidebar_accordion.js",
    ],
    "DASHBOARD_CALLBACK": "core.admin_dashboard.dashboard_callback",
    "SIDEBAR": {
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Overview",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": lambda request: reverse("admin:index"),
                    }
                ],
            },
            {
                "title": "Users",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Accounts",
                        "icon": "person",
                        "link": lambda request: reverse("admin:users_user_changelist"),
                        "permission": _perm("users.view_user"),
                    },
                    {
                        "title": "Profiles",
                        "icon": "badge",
                        "link": lambda request: reverse("admin:profiles_userprofile_changelist"),
                        "permission": _perm("profiles.view_userprofile"),
                    },
                    {
                        "title": "Subscriptions",
                        "icon": "payments",
                        "link": lambda request: reverse("admin:payments_payment_changelist"),
                        "permission": _perm("payments.view_payment"),
                    },
                ],
            },
            {
                "title": "Settings",
                "collapsible": True,
                "items": [
                    {
                        "title": "Journal Questions",
                        "icon": "help",
                        "link": lambda request: reverse("admin:journal_journalquestion_changelist"),
                        "permission": _perm("journal.view_journalquestion"),
                    },
                    {
                        "title": "Guided Programs",
                        "icon": "menu_book",
                        "link": lambda request: reverse("admin:programs_guidedprogram_changelist"),
                        "permission": _perm("programs.view_guidedprogram"),
                    },
                    {
                        "title": "Program Days",
                        "icon": "calendar_month",
                        "link": lambda request: reverse("admin:programs_guidedprogramday_changelist"),
                        "permission": _perm("programs.view_guidedprogramday"),
                    },
                    {
                        "title": "Setari email",
                        "icon": "mail",
                        "link": lambda request: reverse("admin:core_systemconfig_email_settings"),
                        "permission": _perm("core.view_systemconfig"),
                    },
                    {
                        "title": "OAuth Settings",
                        "icon": "vpn_key",
                        "link": lambda request: reverse("admin:core_oauthconfig_changelist"),
                        "permission": _perm("core.view_systemconfig"),
                    },
                    {
                        "title": "Stripe Settings",
                        "icon": "credit_card",
                        "link": lambda request: reverse("admin:core_stripeconfig_changelist"),
                        "permission": _perm("core.view_systemconfig"),
                    },
                    {
                        "title": "reCAPTCHA Settings",
                        "icon": "verified_user",
                        "link": lambda request: reverse("admin:core_recaptchaconfig_changelist"),
                        "permission": _perm("core.view_systemconfig"),
                    },
                    {
                        "title": "Media Library",
                        "icon": "photo_library",
                        "link": lambda request: reverse("admin:core_media_library"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                "title": "Automation",
                "collapsible": True,
                "items": [
                    {
                        "title": "Task Scheduler",
                        "icon": "schedule",
                        "link": lambda request: reverse("admin:core_platformscheduledjob_changelist"),
                        "permission": _perm("core.view_platformscheduledjob"),
                    },
                    {
                        "title": "Backup Scheduler",
                        "icon": "backup",
                        "link": lambda request: reverse("admin:core_backupconfig_changelist"),
                        "permission": _perm("core.view_systemconfig"),
                    },
                ],
            },
            {
                "title": "Storage",
                "collapsible": True,
                "items": [
                    {
                        "title": "Setari",
                        "icon": "settings",
                        "link": lambda request: reverse("admin:core_systemconfig_storage_settings"),
                        "permission": _perm("core.view_systemconfig"),
                    },
                    {
                        "title": "Test",
                        "icon": "cloud_done",
                        "link": lambda request: reverse("admin:core_systemconfig_test_storage"),
                        "permission": _perm("core.view_systemconfig"),
                    },
                    {
                        "title": "Test flux backup",
                        "icon": "published_with_changes",
                        "link": lambda request: reverse("admin:core_systemconfig_test_backup_flow"),
                        "permission": _perm("core.view_systemconfig"),
                    },
                    {
                        "title": "Log backup",
                        "icon": "receipt_long",
                        "link": lambda request: reverse("admin:core_backupverificationlog_changelist"),
                        "permission": _perm("core.view_backupverificationlog"),
                    },
                ],
            },
            {
                "title": "AI",
                "collapsible": True,
                "items": [
                    {
                        "title": "AI Cost Dashboard",
                        "icon": "monitoring",
                        "link": lambda request: reverse("admin:ai_cost_dashboard"),
                        "permission": _perm("ai.view_aibudgetcredit"),
                    },
                    {
                        "title": "Budget Credits",
                        "icon": "account_balance_wallet",
                        "link": lambda request: reverse("admin:ai_aibudgetcredit_changelist"),
                        "permission": _perm("ai.view_aibudgetcredit"),
                    },
                    {
                        "title": "Monthly Targets",
                        "icon": "flag",
                        "link": lambda request: reverse("admin:ai_aibudgetmonthlytarget_changelist"),
                        "permission": _perm("ai.view_aibudgetmonthlytarget"),
                    },
                    {
                        "title": "AI Settings",
                        "icon": "psychology",
                        "link": lambda request: reverse("admin:core_aiconfig_changelist"),
                        "permission": _perm("core.view_systemconfig"),
                    },
                    {
                        "title": "AI Templates",
                        "icon": "smart_toy",
                        "link": lambda request: reverse("admin:ai_conversationtemplate_changelist"),
                        "permission": _perm("ai.view_conversationtemplate"),
                    },
                    {
                        "title": "Conversations",
                        "icon": "forum",
                        "link": lambda request: reverse("admin:ai_conversation_changelist"),
                        "permission": _perm("ai.view_conversation"),
                    },
                    {
                        "title": "AI Logs",
                        "icon": "receipt_long",
                        "link": lambda request: reverse("admin:ai_ailog_changelist"),
                        "permission": _perm("ai.view_ailog"),
                    },
                    {
                        "title": "Emotional Analyses",
                        "icon": "monitor_heart",
                        "link": lambda request: reverse("admin:ai_emotionalanalysis_changelist"),
                        "permission": _perm("ai.view_emotionalanalysis"),
                    },
                    {
                        "title": "Wellness Metrics",
                        "icon": "query_stats",
                        "link": lambda request: reverse("admin:ai_wellnessmetric_changelist"),
                        "permission": _perm("ai.view_wellnessmetric"),
                    },
                    {
                        "title": "Questions",
                        "icon": "quiz",
                        "link": lambda request: reverse("admin:ai_question_changelist"),
                        "permission": _perm("ai.view_question"),
                    },
                    {
                        "title": "Daily Reports",
                        "icon": "today",
                        "link": lambda request: reverse("admin:ai_dailyreport_changelist"),
                        "permission": _perm("ai.view_dailyreport"),
                    },
                    {
                        "title": "Weekly Reports",
                        "icon": "date_range",
                        "link": lambda request: reverse("admin:ai_weeklyreport_changelist"),
                        "permission": _perm("ai.view_weeklyreport"),
                    },
                    {
                        "title": "Monthly Reports",
                        "icon": "calendar_month",
                        "link": lambda request: reverse("admin:ai_monthlyreport_changelist"),
                        "permission": _perm("ai.view_monthlyreport"),
                    },
                ],
            },
            {
                "title": "AI Brain",
                "collapsible": True,
                "items": [
                    {
                        "title": "Prompts",
                        "icon": "psychology_alt",
                        "link": lambda request: reverse("admin:ai_core_prompt_changelist"),
                        "permission": _perm("ai_core.view_prompt"),
                    },
                    {
                        "title": "Prompt Versions",
                        "icon": "history",
                        "link": lambda request: reverse("admin:ai_core_promptversion_changelist"),
                        "permission": _perm("ai_core.view_promptversion"),
                    },
                    {
                        "title": "Audit Prompt",
                        "icon": "fact_check",
                        "link": lambda request: reverse("admin:ai_core_prompt_audit_hub"),
                        "permission": _perm("ai_core.view_prompt"),
                    },
                    {
                        "title": "Improve Prompt",
                        "icon": "auto_fix_high",
                        "link": lambda request: reverse("admin:ai_core_prompt_improve_hub"),
                        "permission": _perm("ai_core.view_prompt"),
                    },
                    {
                        "title": "Orchestrator Preview",
                        "icon": "preview",
                        "link": lambda request: reverse("admin:ai_core_prompt_preview_hub"),
                        "permission": _perm("ai_core.view_prompt"),
                    },
                    {
                        "title": "AI Health Dashboard",
                        "icon": "monitoring",
                        "link": lambda request: reverse("admin:ai_core_dashboard"),
                        "permission": _perm("ai_core.view_prompt"),
                    },
                ],
            },
            {
                "title": "Activity",
                "collapsible": True,
                "items": [
                    {
                        "title": "Journal Entries",
                        "icon": "edit_note",
                        "link": lambda request: reverse("admin:journal_journalentry_changelist"),
                        "permission": _perm("journal.view_journalentry"),
                    },
                ],
            },
            {
                "title": "Support",
                "collapsible": True,
                "items": [
                    {
                        "title": "Support Tickets",
                        "icon": "support_agent",
                        "link": lambda request: reverse("admin:core_supportticket_changelist"),
                        "permission": _perm("core.view_supportticket"),
                    },
                ],
            },
            {
                "title": "LOG-uri",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Analytics Events",
                        "icon": "insights",
                        "link": lambda request: reverse("admin:core_analyticsevent_changelist"),
                        "permission": _perm("core.view_analyticsevent"),
                    },
                    {
                        "title": "Feature Access",
                        "icon": "rule",
                        "link": lambda request: reverse("admin:core_featureaccesslog_changelist"),
                        "permission": _perm("core.view_featureaccesslog"),
                    },
                    {
                        "title": "Stripe Webhooks",
                        "icon": "sync_problem",
                        "link": lambda request: reverse("admin:payments_stripewebhookevent_changelist"),
                        "permission": _perm("payments.view_stripewebhookevent"),
                    },
                    {
                        "title": "Notification Delivery",
                        "icon": "mail",
                        "link": lambda request: reverse("admin:core_notificationdelivery_changelist"),
                        "permission": _perm("core.view_notificationdelivery"),
                    },
                    {
                        "title": "In-App Notifications",
                        "icon": "notifications",
                        "link": lambda request: reverse("admin:core_inappnotification_changelist"),
                        "permission": _perm("core.view_inappnotification"),
                    },
                    {
                        "title": "Quota Usage",
                        "icon": "query_stats",
                        "link": lambda request: reverse("admin:core_userquotausage_changelist"),
                        "permission": _perm("core.view_userquotausage"),
                    },
                    {
                        "title": "System Errors",
                        "icon": "error",
                        "link": lambda request: reverse("admin:core_systemerrorevent_changelist"),
                        "permission": _perm("core.view_systemerrorevent"),
                    },
                    {
                        "title": "Admin Audit",
                        "icon": "admin_panel_settings",
                        "link": lambda request: reverse("admin:core_adminauditlog_changelist"),
                        "permission": _perm("core.view_adminauditlog"),
                    },
                    {
                        "title": "Backup Restore Requests",
                        "icon": "restore",
                        "link": lambda request: reverse("admin:core_backuprestorerequest_changelist"),
                        "permission": _perm("core.view_backuprestorerequest"),
                    },
                ],
            },
        ],
    },
}

ADMIN_WYSIWYG_TOOLBAR_MODE = env(
    "ADMIN_WYSIWYG_TOOLBAR_MODE", default="complete"
).strip().lower()
if ADMIN_WYSIWYG_TOOLBAR_MODE not in {"simple", "complete"}:
    ADMIN_WYSIWYG_TOOLBAR_MODE = "complete"

ADMIN_WYSIWYG_HEIGHT = env.int("ADMIN_WYSIWYG_HEIGHT", default=420)
CMS_EDITOR_UPLOAD_URL = "/doisense/ro/admin/core/cmspage/upload-image/"

CKEDITOR_5_CONFIGS = {
    "simple": {
        "toolbar": [
            "bold",
            "italic",
            "link",
            "bulletedList",
            "numberedList",
            "imageUpload",
            "undo",
            "redo",
        ],
        "image": {
            "toolbar": ["imageTextAlternative"],
        },
        "simpleUpload": {
            "uploadUrl": CMS_EDITOR_UPLOAD_URL,
        },
    },
    "complete": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "|",
            "link",
            "blockQuote",
            "bulletedList",
            "numberedList",
            "|",
            "imageUpload",
            "|",
            "insertTable",
            "|",
            "undo",
            "redo",
        ],
        "image": {
            "toolbar": ["imageTextAlternative"],
        },
        "simpleUpload": {
            "uploadUrl": CMS_EDITOR_UPLOAD_URL,
        },
    },
    "programs_content": {
        "toolbar": [
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "|",
            "link",
            "bulletedList",
            "numberedList",
            "indent",
            "outdent",
            "|",
            "alignment",
            "|",
            "fontSize",
            "fontColor",
            "fontBackgroundColor",
            "|",
            "imageUpload",
            "insertTable",
            "code",
            "|",
            "undo",
            "redo",
        ],
        "image": {
            "toolbar": ["imageTextAlternative"],
        },
        "simpleUpload": {
            "uploadUrl": CMS_EDITOR_UPLOAD_URL,
        },
        "fontSize": {
            "options": [10, 12, 14, "default", 18, 20, 24, 28, 36],
        },
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "core.middleware.QAIPAllowlistMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "core.middleware.SystemErrorLoggingMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://doisense:doisense@db:5432/doisense",
    )
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://redis:6379/0"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = ADMIN_STATIC_URL
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = env("MEDIA_URL", default="/doisense/media/")
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SITE_ID = 1

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "users.authentication.CookieJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_THROTTLE_RATES": {
        "auth_register": "20/hour",
        "auth_activate": "60/hour",
        "auth_login": "30/hour",
        "auth_refresh": "120/hour",
        "auth_social": "30/hour",
        "auth_recover": "15/hour",
        "auth_reset_confirm": "30/hour",
    },
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

JWT_ACCESS_COOKIE_NAME = env("JWT_ACCESS_COOKIE_NAME", default="doisense_access")
JWT_REFRESH_COOKIE_NAME = env("JWT_REFRESH_COOKIE_NAME", default="doisense_refresh")
JWT_COOKIE_SAMESITE = env("JWT_COOKIE_SAMESITE", default="Lax")

CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["https://projects.doimih.net", "http://localhost:3000"],
)
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["https://projects.doimih.net", "http://localhost:3000"],
)

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=not DEBUG)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000 if not DEBUG else 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=not DEBUG
)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=not DEBUG)

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=not DEBUG)

# Stripe
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_PRODUCT_ID_BASIC = env("STRIPE_PRODUCT_ID_BASIC", default="")
STRIPE_PRODUCT_ID_PREMIUM = env("STRIPE_PRODUCT_ID_PREMIUM", default="")
STRIPE_PRODUCT_ID_VIP = env("STRIPE_PRODUCT_ID_VIP", default="")
# Deprecated: kept for backward compatibility
STRIPE_PRICE_ID_PREMIUM = env("STRIPE_PRICE_ID_PREMIUM", default="")

# AI
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")
AI_CHAT_RATE_LIMIT = env.int("AI_CHAT_RATE_LIMIT", default=20)  # per minute

# Analytics
POSTHOG_API_KEY = env("POSTHOG_API_KEY", default="")
POSTHOG_HOST = env("POSTHOG_HOST", default="https://app.posthog.com")

# Supported languages (must match frontend i18n)
SUPPORTED_LANGUAGES = ["ro", "en", "de", "fr", "it", "es", "pl"]

# Social login
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="")
APPLE_CLIENT_ID = env("APPLE_CLIENT_ID", default="")
