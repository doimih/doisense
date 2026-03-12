from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_user_legal_consent_fields"),
        ("core", "0015_featureaccesslog_analyticsevent"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserQuotaUsage",
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
                ("metric_key", models.CharField(max_length=64)),
                (
                    "period_type",
                    models.CharField(
                        choices=[("day", "Day"), ("month", "Month")],
                        max_length=8,
                    ),
                ),
                ("period_start", models.DateField()),
                ("used_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="quota_usage",
                        to="users.user",
                    ),
                ),
            ],
            options={
                "db_table": "core_userquotausage",
                "ordering": ["-updated_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="userquotausage",
            constraint=models.UniqueConstraint(
                fields=("user", "metric_key", "period_type", "period_start"),
                name="core_userquotausage_unique_period",
            ),
        ),
        migrations.AddIndex(
            model_name="userquotausage",
            index=models.Index(
                fields=["metric_key", "period_start"],
                name="core_userqu_metric__2cb145_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="userquotausage",
            index=models.Index(
                fields=["user", "updated_at"],
                name="core_userqu_user_id_47272c_idx",
            ),
        ),
    ]
