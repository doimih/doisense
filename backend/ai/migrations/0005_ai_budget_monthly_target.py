from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ai", "0004_ai_budget_and_usage_costs"),
    ]

    operations = [
        migrations.CreateModel(
            name="AIBudgetMonthlyTarget",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        choices=[("openai", "OpenAI"), ("anthropic", "Anthropic")],
                        max_length=20,
                    ),
                ),
                ("year", models.PositiveSmallIntegerField()),
                ("month", models.PositiveSmallIntegerField()),
                ("target_usd", models.DecimalField(decimal_places=2, max_digits=12)),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "ai_aibudgetmonthlytarget",
                "ordering": ["-year", "-month", "provider"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("provider", "year", "month"),
                        name="ai_budget_monthly_target_provider_month_uniq",
                    )
                ],
            },
        ),
    ]
