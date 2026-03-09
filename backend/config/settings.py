import os
from pathlib import Path

import environ
from django.urls import reverse

env = environ.Env(DEBUG=(bool, False))


def _perm(permission_codename: str):
    return lambda request: request.user.has_perm(permission_codename)

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(BASE_DIR / ".env")

ADMIN_STATIC_URL = env("STATIC_URL", default="/doisense/ro/admin/static/")

SECRET_KEY = env("SECRET_KEY", default="dev-secret-change-in-production")
DEBUG = env("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

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
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "core",
    "users",
    "profiles",
    "journal",
    "programs",
    "ai",
    "payments",
]

UNFOLD = {
    "SITE_TITLE": "Doisense Admin",
    "SITE_HEADER": "Doisense",
    "SITE_SYMBOL": "dashboard",
    "SHOW_HISTORY": True,
    "STYLES": [
        f"{ADMIN_STATIC_URL}admin/css/unfold_custom_fields.css",
    ],
    "SCRIPTS": [
        f"{ADMIN_STATIC_URL}admin/js/unfold_wysiwyg_toolbar.js",
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
                        "title": "AI Templates",
                        "icon": "smart_toy",
                        "link": lambda request: reverse("admin:ai_conversationtemplate_changelist"),
                        "permission": _perm("ai.view_conversationtemplate"),
                    },
                    {
                        "title": "CMS Pages",
                        "icon": "article",
                        "link": lambda request: reverse("admin:core_cmspage_changelist"),
                        "permission": _perm("core.view_cmspage"),
                    },
                ],
            },
            {
                "title": "Activity",
                "items": [
                    {
                        "title": "Journal Entries",
                        "icon": "edit_note",
                        "link": lambda request: reverse("admin:journal_journalentry_changelist"),
                        "permission": _perm("journal.view_journalentry"),
                    },
                    {
                        "title": "AI Logs",
                        "icon": "receipt_long",
                        "link": lambda request: reverse("admin:ai_ailog_changelist"),
                        "permission": _perm("ai.view_ailog"),
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
        "toolbar": ["bold", "italic", "link", "bulletedList", "numberedList", "undo", "redo"],
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
            "insertTable",
            "|",
            "undo",
            "redo",
        ],
        "simpleUpload": {
            "uploadUrl": CMS_EDITOR_UPLOAD_URL,
        },
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
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

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

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

FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", default="https://projects.doimih.net/doisense")

# Stripe
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_PRICE_ID_PREMIUM = env("STRIPE_PRICE_ID_PREMIUM", default="")

# AI
OPENAI_API_KEY = env("OPENAI_API_KEY", default="")
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY", default="")
AI_CHAT_RATE_LIMIT = env.int("AI_CHAT_RATE_LIMIT", default=20)  # per minute

# Supported languages (must match frontend i18n)
SUPPORTED_LANGUAGES = ["ro", "en", "de", "it", "es", "pl"]

# Social login
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="")
APPLE_CLIENT_ID = env("APPLE_CLIENT_ID", default="")
