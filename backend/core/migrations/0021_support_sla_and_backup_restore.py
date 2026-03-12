from django.conf import settings
from django.db import migrations, models


def seed_reactivation_scheduler_job(apps, schema_editor):
    PlatformScheduledJob = apps.get_model("core", "PlatformScheduledJob")
    PlatformScheduledJob.objects.update_or_create(
        code="send_reactivation_campaign",
        defaults={
            "label": "Send Reactivation Campaign",
            "command_name": "send_reactivation_campaign",
            "schedule_type": "daily",
            "minute_of_hour": 0,
            "hour_of_day": 11,
            "weekday": None,
            "enabled": True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0020_platformscheduledjob"),
    ]

    operations = [
        migrations.AddField(
            model_name="supportticket",
            name="assigned_to",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="assigned_support_tickets", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="supportticket",
            name="first_responded_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="supportticket",
            name="first_response_due_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="supportticket",
            name="internal_notes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="supportticket",
            name="priority",
            field=models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")], default="medium", max_length=16),
        ),
        migrations.AddField(
            model_name="supportticket",
            name="resolution_due_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="supportticket",
            name="resolved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="BackupRestoreRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("requested", "Requested"), ("approved", "Approved"), ("rejected", "Rejected"), ("executed", "Executed"), ("failed", "Failed")], default="requested", max_length=16)),
                ("restore_point", models.CharField(max_length=255)),
                ("reason", models.TextField(blank=True, default="")),
                ("confirmation_token", models.CharField(default="CONFIRM_RESTORE", max_length=64)),
                ("execution_notes", models.TextField(blank=True, default="")),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("executed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="approved_backup_restore_requests", to=settings.AUTH_USER_MODEL)),
                ("requested_by", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="backup_restore_requests", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "core_backuprestorerequest",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="backuprestorerequest",
            index=models.Index(fields=["status", "created_at"], name="core_backup_status_ff341b_idx"),
        ),
        migrations.RunPython(seed_reactivation_scheduler_job, migrations.RunPython.noop),
    ]
