from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_alter_cmspage_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationDelivery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("notification_type", models.CharField(max_length=64)),
                ("sent_for_date", models.DateField()),
                ("context_key", models.CharField(blank=True, default="", max_length=64)),
                ("sent_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_deliveries",
                        to="users.user",
                    ),
                ),
            ],
            options={
                "db_table": "core_notificationdelivery",
                "ordering": ["-sent_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="notificationdelivery",
            constraint=models.UniqueConstraint(
                fields=("user", "notification_type", "sent_for_date", "context_key"),
                name="core_notificationdelivery_unique_send",
            ),
        ),
        migrations.AddIndex(
            model_name="notificationdelivery",
            index=models.Index(
                fields=["notification_type", "sent_for_date"],
                name="core_notifi_notific_e5c13f_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="notificationdelivery",
            index=models.Index(
                fields=["user", "sent_at"],
                name="core_notifi_user_id_b4b702_idx",
            ),
        ),
    ]