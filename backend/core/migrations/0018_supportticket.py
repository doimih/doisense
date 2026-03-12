from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_inapp_notifications"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SupportTicket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(max_length=180)),
                ("message", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("in_progress", "In Progress"), ("resolved", "Resolved")],
                        default="open",
                        max_length=16,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="support_tickets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "core_supportticket",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="supportticket",
            index=models.Index(fields=["user", "status", "created_at"], name="core_suppor_user_id_4dca98_idx"),
        ),
    ]
