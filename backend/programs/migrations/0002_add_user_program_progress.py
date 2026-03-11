import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Add UserProgramProgress to track which days each user has completed."""

    dependencies = [
        ("programs", "0001_add_user_program_progress"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProgramProgress",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("current_day", models.PositiveIntegerField(default=1)),
                ("completed_days", models.JSONField(default=list)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("last_active_at", models.DateTimeField(auto_now=True)),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="progress",
                        to="programs.guidedprogram",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="program_progress",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "programs_userprogramprogress",
                "unique_together": {("user", "program")},
            },
        ),
    ]
