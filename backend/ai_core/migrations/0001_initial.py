from django.db import migrations, models

import ai_core.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Prompt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("system", "System"),
                            ("personality", "Personality"),
                            ("rules", "Rules"),
                            ("context", "Context"),
                            ("greeting", "Greeting"),
                            ("fallback", "Fallback"),
                            ("skill", "Skill"),
                        ],
                        max_length=32,
                    ),
                ),
                ("content", models.TextField(validators=[ai_core.validators.validate_english_prompt_content])),
                ("language", models.CharField(default="en", max_length=8)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "ai_core_prompt",
                "ordering": ["type", "name"],
                "verbose_name": "Prompt",
                "verbose_name_plural": "Prompts",
            },
        ),
        migrations.CreateModel(
            name="PromptVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version_number", models.IntegerField()),
                ("content_snapshot", models.TextField()),
                (
                    "type_snapshot",
                    models.CharField(
                        choices=[
                            ("system", "System"),
                            ("personality", "Personality"),
                            ("rules", "Rules"),
                            ("context", "Context"),
                            ("greeting", "Greeting"),
                            ("fallback", "Fallback"),
                            ("skill", "Skill"),
                        ],
                        max_length=32,
                    ),
                ),
                ("language_snapshot", models.CharField(max_length=8)),
                ("updated_at", models.DateTimeField(auto_now_add=True)),
                ("updated_by", models.CharField(blank=True, default="", max_length=255)),
                ("change_reason", models.TextField(blank=True, default="")),
                (
                    "prompt",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="versions", to="ai_core.prompt"),
                ),
            ],
            options={
                "db_table": "ai_core_promptversion",
                "ordering": ["-updated_at", "-version_number"],
                "verbose_name": "Prompt Version",
                "verbose_name_plural": "Prompt Versions",
            },
        ),
        migrations.AddConstraint(
            model_name="promptversion",
            constraint=models.UniqueConstraint(
                fields=("prompt", "version_number"),
                name="ai_core_promptversion_prompt_version_uniq",
            ),
        ),
    ]