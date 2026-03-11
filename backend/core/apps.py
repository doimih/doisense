from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core"

    def ready(self):
        from django.contrib import admin

        admin.site.has_permission = lambda request: bool(
            request.user.is_active and request.user.is_superuser
        )
