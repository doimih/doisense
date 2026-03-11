from django.db import migrations, models
import django.db.models.deletion
import core.validators


class Migration(migrations.Migration):
    """Initial state migration — tables already exist via syncdb. Fake-apply this."""

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GuidedProgram",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("language", models.CharField(max_length=2, validators=[core.validators.validate_language])),
                ("active", models.BooleanField(default=True)),
                ("is_premium", models.BooleanField(default=False)),
            ],
            options={"db_table": "programs_guidedprogram"},
        ),
        migrations.CreateModel(
            name="GuidedProgramDay",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("day_number", models.PositiveIntegerField()),
                ("title", models.CharField(max_length=200)),
                ("content", models.TextField()),
                ("question", models.TextField(blank=True)),
                ("ai_prompt", models.TextField(blank=True)),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="days",
                        to="programs.guidedprogram",
                    ),
                ),
            ],
            options={
                "db_table": "programs_guidedprogramday",
                "ordering": ["day_number"],
                "unique_together": {("program", "day_number")},
            },
        ),
    ]
