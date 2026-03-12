from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ai", "0002_rename_ai_conversation_user_created_idx_ai_conversa_user_id_220de8_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="response_type",
            field=models.CharField(blank=True, default="response", max_length=32),
        ),
        migrations.CreateModel(
            name="DailyReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("summary", models.TextField(blank=True, default="")),
                ("highlights", models.JSONField(blank=True, default=list)),
                ("challenges", models.JSONField(blank=True, default=list)),
                ("recommendations", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="daily_reports", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "db_table": "ai_dailyreport",
                "ordering": ["-date"],
            },
        ),
        migrations.CreateModel(
            name="EmotionalAnalysis",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("dominant_emotion", models.CharField(blank=True, default="", max_length=64)),
                ("secondary_emotions", models.JSONField(blank=True, default=list)),
                ("triggers", models.JSONField(blank=True, default=list)),
                ("stress_score", models.FloatField(blank=True, null=True)),
                ("energy_score", models.FloatField(blank=True, null=True)),
                ("motivation_score", models.FloatField(blank=True, null=True)),
                ("observations", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="emotional_analyses", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "db_table": "ai_emotionalanalysis",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="MonthlyReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("year", models.PositiveSmallIntegerField()),
                ("month", models.PositiveSmallIntegerField()),
                ("summary", models.TextField(blank=True, default="")),
                ("trends", models.JSONField(blank=True, default=list)),
                ("insights", models.TextField(blank=True, default="")),
                ("recommendations", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="monthly_reports", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "db_table": "ai_monthlyreport",
                "ordering": ["-year", "-month"],
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField()),
                (
                    "question_type",
                    models.CharField(
                        choices=[("open", "Open"), ("multiple_choice", "Multiple Choice"), ("rating", "Rating"), ("yes_no", "Yes / No")],
                        default="open",
                        max_length=24,
                    ),
                ),
                ("reason", models.TextField(blank=True, default="")),
                (
                    "priority",
                    models.CharField(choices=[("high", "High"), ("medium", "Medium"), ("low", "Low")], default="medium", max_length=8),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="generated_questions", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "db_table": "ai_question",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="WeeklyReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("week_start", models.DateField()),
                ("summary", models.TextField(blank=True, default="")),
                ("trends", models.JSONField(blank=True, default=list)),
                ("progress", models.TextField(blank=True, default="")),
                ("recommendations", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="weekly_reports", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "db_table": "ai_weeklyreport",
                "ordering": ["-week_start"],
            },
        ),
        migrations.CreateModel(
            name="WellnessMetric",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stress_score", models.FloatField(blank=True, null=True)),
                ("energy_score", models.FloatField(blank=True, null=True)),
                ("motivation_score", models.FloatField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="wellness_metrics", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                "db_table": "ai_wellnessmetric",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="dailyreport",
            constraint=models.UniqueConstraint(fields=("user", "date"), name="ai_dailyreport_user_date_uniq"),
        ),
        migrations.AddConstraint(
            model_name="monthlyreport",
            constraint=models.UniqueConstraint(fields=("user", "year", "month"), name="ai_monthlyreport_user_month_uniq"),
        ),
        migrations.AddConstraint(
            model_name="weeklyreport",
            constraint=models.UniqueConstraint(fields=("user", "week_start"), name="ai_weeklyreport_user_week_uniq"),
        ),
        migrations.AddIndex(
            model_name="emotionalanalysis",
            index=models.Index(fields=["user", "created_at"], name="ai_emotiona_user_id_665a10_idx"),
        ),
        migrations.AddIndex(
            model_name="question",
            index=models.Index(fields=["user", "created_at"], name="ai_question_user_id_688110_idx"),
        ),
        migrations.AddIndex(
            model_name="wellnessmetric",
            index=models.Index(fields=["user", "created_at"], name="ai_wellness_user_id_8087a4_idx"),
        ),
    ]
