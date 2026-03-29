from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def seed_calendar_plans(apps, schema_editor):
    CalendarPlan = apps.get_model("calendar_tasks", "CalendarPlan")
    CalendarPlan.objects.get_or_create(
        code="basic",
        defaults={
            "name": "BASIC Start",
            "description": "Manual tasks + simple progress",
            "capabilities": {
                "task_create": True,
                "task_check": True,
                "task_active_view": True,
                "simple_progress": True,
                "chat_month_calendar": True,
                "advanced_stats": False,
                "task_history": False,
                "profile_monthly_view": False,
                "advanced_task_options": False,
                "ai_habit_suggestions": False,
                "ai_routine_builder": False,
                "ai_daily_checkin": False,
                "ai_progress_insights": False,
                "ai_habit_optimization": False,
            },
        },
    )
    CalendarPlan.objects.get_or_create(
        code="premium",
        defaults={
            "name": "PREMIUM Flow",
            "description": "Basic + advanced statistics + history + monthly view",
            "capabilities": {
                "task_create": True,
                "task_check": True,
                "task_active_view": True,
                "simple_progress": True,
                "chat_month_calendar": True,
                "advanced_stats": True,
                "task_history": True,
                "profile_monthly_view": True,
                "advanced_task_options": True,
                "ai_habit_suggestions": False,
                "ai_routine_builder": False,
                "ai_daily_checkin": False,
                "ai_progress_insights": False,
                "ai_habit_optimization": False,
            },
        },
    )
    CalendarPlan.objects.get_or_create(
        code="vip",
        defaults={
            "name": "VIP Executive",
            "description": "Premium + AI suggestions, routines, check-ins and insights",
            "capabilities": {
                "task_create": True,
                "task_check": True,
                "task_active_view": True,
                "simple_progress": True,
                "chat_month_calendar": True,
                "advanced_stats": True,
                "task_history": True,
                "profile_monthly_view": True,
                "advanced_task_options": True,
                "ai_habit_suggestions": True,
                "ai_routine_builder": True,
                "ai_daily_checkin": True,
                "ai_progress_insights": True,
                "ai_habit_optimization": True,
            },
        },
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0007_user_early_discount_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="CalendarPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(choices=[("basic", "BASIC Start"), ("premium", "PREMIUM Flow"), ("vip", "VIP Executive")], max_length=16, unique=True)),
                ("name", models.CharField(max_length=64)),
                ("description", models.TextField(blank=True, default="")),
                ("capabilities", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "calendar_plan", "ordering": ["code"]},
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("description", models.TextField(blank=True, default="")),
                ("duration_minutes", models.PositiveIntegerField(default=15)),
                ("frequency", models.CharField(choices=[("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly"), ("custom", "Custom")], default="daily", max_length=16)),
                ("weekdays", models.JSONField(blank=True, default=list)),
                ("month_days", models.JSONField(blank=True, default=list)),
                ("start_time", models.TimeField(blank=True, null=True)),
                ("reminder_enabled", models.BooleanField(default=False)),
                ("reminder_minutes_before", models.PositiveIntegerField(default=10)),
                ("advanced_options", models.JSONField(blank=True, default=dict)),
                ("ai_generated", models.BooleanField(default=False)),
                ("ai_metadata", models.JSONField(blank=True, default=dict)),
                ("starts_on", models.DateField(default=django.utils.timezone.localdate)),
                ("ends_on", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="calendar_tasks", to="users.user")),
            ],
            options={"db_table": "calendar_task", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="TaskStat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("completed_days", models.PositiveIntegerField(default=0)),
                ("total_days", models.PositiveIntegerField(default=0)),
                ("current_streak", models.PositiveIntegerField(default=0)),
                ("best_streak", models.PositiveIntegerField(default=0)),
                ("completion_rate", models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ("last_completed_at", models.DateTimeField(blank=True, null=True)),
                ("last_calculated_at", models.DateTimeField(auto_now=True)),
                ("task", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="stats", to="calendar_tasks.task")),
            ],
            options={"db_table": "calendar_task_stat"},
        ),
        migrations.CreateModel(
            name="TaskProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("progress_date", models.DateField()),
                ("is_completed", models.BooleanField(default=False)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("note", models.CharField(blank=True, default="", max_length=280)),
                ("mood_score", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("energy_score", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("task", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progress_entries", to="calendar_tasks.task")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="task_progress_entries", to="users.user")),
            ],
            options={"db_table": "calendar_task_progress", "ordering": ["-progress_date", "-created_at"]},
        ),
        migrations.CreateModel(
            name="CalendarUserPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source", models.CharField(choices=[("system", "System"), ("admin", "Admin"), ("payment", "Payment")], default="system", max_length=16)),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="user_links", to="calendar_tasks.calendarplan")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="calendar_user_plans", to="users.user")),
            ],
            options={"db_table": "calendar_user_plan", "ordering": ["-started_at"]},
        ),
        migrations.AddIndex(model_name="task", index=models.Index(fields=["user", "is_active"], name="calendar_task_user_active_idx")),
        migrations.AddIndex(model_name="task", index=models.Index(fields=["user", "starts_on"], name="calendar_task_user_start_idx")),
        migrations.AddIndex(model_name="task", index=models.Index(fields=["user", "created_at"], name="calendar_task_user_created_idx")),
        migrations.AddIndex(model_name="taskprogress", index=models.Index(fields=["user", "progress_date"], name="calendar_tp_user_day_idx")),
        migrations.AddIndex(model_name="taskprogress", index=models.Index(fields=["task", "progress_date"], name="calendar_tp_task_day_idx")),
        migrations.AddConstraint(model_name="taskprogress", constraint=models.UniqueConstraint(fields=("task", "progress_date"), name="calendar_tp_task_day_uq")),
        migrations.AddIndex(model_name="taskstat", index=models.Index(fields=["completion_rate"], name="calendar_ts_rate_idx")),
        migrations.AddIndex(model_name="calendaruserplan", index=models.Index(fields=["user", "is_active"], name="calendar_up_user_active_idx")),
        migrations.AddIndex(model_name="calendaruserplan", index=models.Index(fields=["expires_at"], name="calendar_up_exp_idx")),
        migrations.RunPython(seed_calendar_plans, migrations.RunPython.noop),
    ]
