from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve
from django.views.generic import RedirectView

admin.site.site_url = settings.ADMIN_SITE_URL


PUBLIC_PATH_PREFIX = settings.PUBLIC_PATH_PREFIX.strip("/")


def prefixed_path(*segments: str) -> str:
    parts = []
    if PUBLIC_PATH_PREFIX:
        parts.append(PUBLIC_PATH_PREFIX)
    parts.extend(segment.strip("/") for segment in segments if segment.strip("/"))
    return "/".join(parts) + "/"


def prefixed_absolute_path(*segments: str) -> str:
    return "/" + prefixed_path(*segments)

urlpatterns = [
    path(
        prefixed_path("admin"),
        RedirectView.as_view(url=prefixed_absolute_path("ro/admin"), permanent=False),
    ),
    path(
        prefixed_path("ro/admin/static") + "<path:path>",
        serve,
        {"document_root": settings.STATIC_ROOT},
    ),
    path(
        prefixed_path("media") + "<path:path>",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
    path(prefixed_path("ro/admin/ckeditor5"), include("django_ckeditor_5.urls")),
    path(prefixed_path("ro/admin"), admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/", include("users.urls_me")),
    path("api/", include("core.urls")),
    path("api/profile/", include("profiles.urls")),
    path("api/chat/", include("ai.urls_chat")),
    path("api/support/", include("ai.urls_support")),
    path("api/journal/", include("journal.urls")),
    path("api/programs/", include("programs.urls")),
    path("api/calendar/", include("calendar_tasks.urls")),
    path("api/payments/", include("payments.urls")),
]
