from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from django.views.generic import RedirectView

admin.site.site_url = "https://projects.doimih.net/doisense"
admin.site.has_permission = lambda request: bool(
    request.user.is_active and request.user.is_superuser
)

urlpatterns = [
    path("doisense/admin/", RedirectView.as_view(url="/doisense/ro/admin/", permanent=False)),
    re_path(r"^doisense/ro/admin/static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    re_path(r"^doisense/media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    path("doisense/ro/admin/ckeditor5/", include("django_ckeditor_5.urls")),
    path("doisense/ro/admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/", include("users.urls_me")),
    path("api/", include("core.urls")),
    path("api/profile/", include("profiles.urls")),
    path("api/chat/", include("ai.urls_chat")),
    path("api/support/", include("ai.urls_support")),
    path("api/journal/", include("journal.urls")),
    path("api/programs/", include("programs.urls")),
    path("api/payments/", include("payments.urls")),
]
