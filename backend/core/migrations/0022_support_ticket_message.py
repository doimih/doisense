from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0021_support_sla_and_backup_restore"),
    ]

    operations = [
        migrations.CreateModel(
            name="SupportTicketMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "sender_role",
                    models.CharField(
                        choices=[("user", "User"), ("admin", "Admin"), ("system", "System")],
                        default="user",
                        max_length=16,
                    ),
                ),
                ("message", models.TextField()),
                ("is_internal", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="support_ticket_messages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "ticket",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="messages",
                        to="core.supportticket",
                    ),
                ),
            ],
            options={
                "db_table": "core_supportticketmessage",
                "ordering": ["created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="supportticketmessage",
            index=models.Index(fields=["ticket", "created_at"], name="core_suppor_ticket__45a5b4_idx"),
        ),
        migrations.AddIndex(
            model_name="supportticketmessage",
            index=models.Index(fields=["is_internal", "created_at"], name="core_suppor_is_inte_0ee07f_idx"),
        ),
    ]
