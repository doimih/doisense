from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ai", "0003_ai_reports_and_analysis_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="ailog",
            name="estimated_cost_usd",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name="ailog",
            name="input_tokens",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ailog",
            name="output_tokens",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ailog",
            name="provider",
            field=models.CharField(
                choices=[("openai", "OpenAI"), ("anthropic", "Anthropic"), ("unknown", "Unknown")],
                default="unknown",
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="AIBudgetCredit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(choices=[("openai", "OpenAI"), ("anthropic", "Anthropic")], max_length=20)),
                ("amount_usd", models.DecimalField(decimal_places=2, max_digits=12)),
                ("credited_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("source_reference", models.CharField(blank=True, default="", max_length=120)),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="ai_budget_credits",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "ai_aibudgetcredit",
                "ordering": ["-credited_at", "-created_at"],
            },
        ),
    ]
