from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_userquotausage"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InAppNotification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("notification_type", models.CharField(max_length=64)),
                ("title", models.CharField(max_length=160)),
                ("body", models.TextField(blank=True)),
                ("context_key", models.CharField(blank=True, default="", max_length=64)),
                ("is_read", models.BooleanField(default=False)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="in_app_notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "core_inappnotification",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="UserNotificationPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("push_enabled", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_preferences",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "core_usernotificationpreference",
            },
        ),
        migrations.AddIndex(
            model_name="inappnotification",
            index=models.Index(fields=["user", "is_read", "created_at"], name="core_inapp_user_id_ea6f9f_idx"),
        ),
        migrations.AddIndex(
            model_name="inappnotification",
            index=models.Index(fields=["notification_type", "created_at"], name="core_inapp_notific_32e559_idx"),
        ),
    ]
