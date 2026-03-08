from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("doisense/ro/admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/", include("users.urls_me")),
    path("api/", include("core.urls")),
    path("api/profile/", include("profiles.urls")),
    path("api/chat/", include("ai.urls_chat")),
    path("api/journal/", include("journal.urls")),
    path("api/programs/", include("programs.urls")),
    path("api/payments/", include("payments.urls")),
]
