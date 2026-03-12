from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_supportticket"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminAuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=64)),
                ("target_model", models.CharField(max_length=128)),
                ("target_object_id", models.CharField(max_length=64)),
                ("before_data", models.JSONField(blank=True, default=dict)),
                ("after_data", models.JSONField(blank=True, default=dict)),
                ("reason", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="admin_audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "core_adminauditlog",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="BackupVerificationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("success", "Success"), ("failed", "Failed")], max_length=16)),
                ("source", models.CharField(blank=True, default="backup_job", max_length=64)),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "core_backupverificationlog",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="SystemErrorEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "severity",
                    models.CharField(
                        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
                        default="high",
                        max_length=16,
                    ),
                ),
                ("component", models.CharField(default="backend", max_length=64)),
                ("endpoint", models.CharField(blank=True, default="", max_length=255)),
                ("http_method", models.CharField(blank=True, default="", max_length=12)),
                ("status_code", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("error_type", models.CharField(blank=True, default="", max_length=128)),
                ("message", models.TextField(blank=True, default="")),
                ("context", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="system_error_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "core_systemerrorevent",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="adminauditlog",
            index=models.Index(fields=["action", "created_at"], name="core_admina_action_922ba4_idx"),
        ),
        migrations.AddIndex(
            model_name="adminauditlog",
            index=models.Index(fields=["target_model", "created_at"], name="core_admina_target__2c0f2e_idx"),
        ),
        migrations.AddIndex(
            model_name="adminauditlog",
            index=models.Index(fields=["actor", "created_at"], name="core_admina_actor_i_28f049_idx"),
        ),
        migrations.AddIndex(
            model_name="backupverificationlog",
            index=models.Index(fields=["status", "created_at"], name="core_backupv_status_859a75_idx"),
        ),
        migrations.AddIndex(
            model_name="systemerrorevent",
            index=models.Index(fields=["severity", "created_at"], name="core_systeme_severit_13616a_idx"),
        ),
        migrations.AddIndex(
            model_name="systemerrorevent",
            index=models.Index(fields=["component", "created_at"], name="core_systeme_compone_7f5dd4_idx"),
        ),
        migrations.AddIndex(
            model_name="systemerrorevent",
            index=models.Index(fields=["status_code", "created_at"], name="core_systeme_status__8fcb82_idx"),
        ),
    ]
