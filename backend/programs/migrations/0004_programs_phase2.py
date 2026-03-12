from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("programs", "0003_alter_guidedprogram_id_alter_guidedprogramday_id_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="userprogramprogress",
            name="dropout_marked_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userprogramprogress",
            name="is_paused",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="userprogramprogress",
            name="paused_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="ProgramReflection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("day_number", models.PositiveIntegerField()),
                ("reflection_text", models.TextField()),
                ("ai_feedback", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reflections",
                        to="programs.guidedprogram",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="program_reflections",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "programs_programreflection",
                "ordering": ["-updated_at"],
                "unique_together": {("user", "program", "day_number")},
            },
        ),
    ]
