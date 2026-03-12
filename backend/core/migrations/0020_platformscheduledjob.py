from django.db import migrations, models
import django.core.validators


def seed_platform_scheduler_jobs(apps, schema_editor):
    PlatformScheduledJob = apps.get_model("core", "PlatformScheduledJob")
    defaults = [
        {
            "code": "expire_trials",
            "label": "Expire Trials",
            "command_name": "expire_trials",
            "schedule_type": "hourly",
            "minute_of_hour": 0,
            "hour_of_day": None,
            "weekday": None,
        },
        {
            "code": "send_trial_warnings",
            "label": "Send Trial Warnings",
            "command_name": "send_trial_warnings",
            "schedule_type": "daily",
            "minute_of_hour": 0,
            "hour_of_day": 5,
            "weekday": None,
        },
        {
            "code": "send_daily_plan_reminders",
            "label": "Send Daily Plan Reminders",
            "command_name": "send_daily_plan_reminders",
            "schedule_type": "daily",
            "minute_of_hour": 0,
            "hour_of_day": 7,
            "weekday": None,
        },
        {
            "code": "send_journal_reminders",
            "label": "Send Journal Reminders",
            "command_name": "send_journal_reminders",
            "schedule_type": "daily",
            "minute_of_hour": 0,
            "hour_of_day": 8,
            "weekday": None,
        },
        {
            "code": "send_goal_reminders",
            "label": "Send Goal Reminders",
            "command_name": "send_goal_reminders",
            "schedule_type": "daily",
            "minute_of_hour": 0,
            "hour_of_day": 18,
            "weekday": None,
        },
        {
            "code": "send_wellbeing_reminders",
            "label": "Send Wellbeing Reminders",
            "command_name": "send_wellbeing_reminders",
            "schedule_type": "daily",
            "minute_of_hour": 0,
            "hour_of_day": 10,
            "weekday": None,
        },
        {
            "code": "send_upgrade_recommendations",
            "label": "Send Upgrade Recommendations",
            "command_name": "send_upgrade_recommendations",
            "schedule_type": "daily",
            "minute_of_hour": 0,
            "hour_of_day": 14,
            "weekday": None,
        },
        {
            "code": "audit_manual_vip",
            "label": "Audit Manual VIP",
            "command_name": "audit_manual_vip",
            "schedule_type": "weekly",
            "minute_of_hour": 0,
            "hour_of_day": 6,
            "weekday": 0,
        },
        {
            "code": "send_inactivity_reminders",
            "label": "Send Inactivity Reminders",
            "command_name": "send_inactivity_reminders",
            "schedule_type": "daily",
            "minute_of_hour": 0,
            "hour_of_day": 9,
            "weekday": None,
        },
        {
            "code": "ai_update_profiles",
            "label": "Refresh AI Profiles",
            "command_name": "ai_update_profiles",
            "schedule_type": "daily",
            "minute_of_hour": 0,
            "hour_of_day": 2,
            "weekday": None,
        },
    ]

    for item in defaults:
        PlatformScheduledJob.objects.update_or_create(code=item["code"], defaults=item)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0019_observability_logs"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlatformScheduledJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=64, unique=True)),
                ("label", models.CharField(max_length=120)),
                ("command_name", models.CharField(max_length=120)),
                ("schedule_type", models.CharField(choices=[("hourly", "Hourly"), ("daily", "Daily"), ("weekly", "Weekly")], default="daily", max_length=16)),
                ("minute_of_hour", models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(59)])),
                ("hour_of_day", models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(23)])),
                ("weekday", models.PositiveSmallIntegerField(blank=True, choices=[(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday")], null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)])),
                ("enabled", models.BooleanField(default=True)),
                ("last_run_at", models.DateTimeField(blank=True, null=True)),
                ("last_run_status", models.CharField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], default="pending", max_length=16)),
                ("last_error", models.TextField(blank=True, default="")),
                ("last_duration_ms", models.PositiveIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "core_platformscheduledjob",
                "ordering": ["label"],
            },
        ),
        migrations.RunPython(seed_platform_scheduler_jobs, migrations.RunPython.noop),
    ]