from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count
from django.utils import timezone

from .models import Task, TaskProgress, TaskStat


def parse_iso_date(raw: str | None, *, fallback: date | None = None) -> date:
    if not raw:
        if fallback:
            return fallback
        return timezone.localdate()
    return date.fromisoformat(raw)


def month_range(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    return start, end


def task_is_scheduled_for_day(task: Task, day: date) -> bool:
    if day < task.starts_on:
        return False
    if task.ends_on and day > task.ends_on:
        return False

    if task.frequency == Task.FREQ_DAILY:
        return True
    if task.frequency == Task.FREQ_WEEKLY:
        weekdays = set(int(item) for item in (task.weekdays or []) if str(item).isdigit())
        if not weekdays:
            weekdays = {task.starts_on.weekday()}
        return day.weekday() in weekdays
    if task.frequency == Task.FREQ_MONTHLY:
        month_days = set(int(item) for item in (task.month_days or []) if str(item).isdigit())
        if not month_days:
            month_days = {task.starts_on.day}
        return day.day in month_days
    if task.frequency == Task.FREQ_CUSTOM:
        weekdays = set(int(item) for item in (task.weekdays or []) if str(item).isdigit())
        month_days = set(int(item) for item in (task.month_days or []) if str(item).isdigit())
        return day.weekday() in weekdays or day.day in month_days
    return False


def update_task_stats(task: Task) -> TaskStat:
    rows = list(TaskProgress.objects.filter(task=task).order_by("progress_date"))
    total_days = len(rows)
    completed_days = sum(1 for row in rows if row.is_completed)

    current_streak = 0
    best_streak = 0
    running = 0

    for row in rows:
        if row.is_completed:
            running += 1
            best_streak = max(best_streak, running)
        else:
            running = 0

    for row in reversed(rows):
        if row.is_completed:
            current_streak += 1
        else:
            break

    if total_days:
        rate = (Decimal(completed_days) / Decimal(total_days)) * Decimal("100")
        completion_rate = rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    else:
        completion_rate = Decimal("0.00")

    last_completed_at = None
    for row in reversed(rows):
        if row.is_completed:
            last_completed_at = row.completed_at
            break

    stat, _ = TaskStat.objects.get_or_create(task=task)
    stat.completed_days = completed_days
    stat.total_days = total_days
    stat.current_streak = current_streak
    stat.best_streak = best_streak
    stat.completion_rate = completion_rate
    stat.last_completed_at = last_completed_at
    stat.save(update_fields=[
        "completed_days",
        "total_days",
        "current_streak",
        "best_streak",
        "completion_rate",
        "last_completed_at",
        "last_calculated_at",
    ])
    return stat


def build_month_markers(user, start_day: date, end_day: date) -> dict[str, dict[str, int | bool]]:
    tasks = list(Task.objects.filter(user=user, is_active=True))
    progress_rows = list(
        TaskProgress.objects.filter(
            user=user,
            progress_date__gte=start_day,
            progress_date__lte=end_day,
        )
    )

    completed_by_day: dict[date, int] = defaultdict(int)
    planned_by_day: dict[date, int] = defaultdict(int)

    day = start_day
    while day <= end_day:
        for task in tasks:
            if task_is_scheduled_for_day(task, day):
                planned_by_day[day] += 1
        day += timedelta(days=1)

    for row in progress_rows:
        if row.is_completed:
            completed_by_day[row.progress_date] += 1

    markers: dict[str, dict[str, int | bool]] = {}
    day = start_day
    while day <= end_day:
        planned = planned_by_day.get(day, 0)
        completed = completed_by_day.get(day, 0)
        markers[day.isoformat()] = {
            "planned": planned,
            "completed": completed,
            "has_tasks": planned > 0,
            "all_completed": planned > 0 and completed >= planned,
        }
        day += timedelta(days=1)

    return markers


def build_task_payload(task: Task, *, include_stats: bool = False) -> dict:
    payload = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "duration_minutes": task.duration_minutes,
        "frequency": task.frequency,
        "weekdays": task.weekdays,
        "month_days": task.month_days,
        "start_time": task.start_time.isoformat() if task.start_time else None,
        "reminder_enabled": task.reminder_enabled,
        "reminder_minutes_before": task.reminder_minutes_before,
        "source": task.source,
        "task_type": task.task_type,
        "advanced_options": task.advanced_options,
        "ai_generated": task.ai_generated,
        "guided_program_id": task.guided_program_id,
        "program_day": task.program_day,
        "starts_on": task.starts_on.isoformat(),
        "ends_on": task.ends_on.isoformat() if task.ends_on else None,
        "is_active": task.is_active,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
    if include_stats:
        stat = getattr(task, "stats", None)
        if not stat:
            stat = update_task_stats(task)
        payload["stats"] = {
            "completed_days": stat.completed_days,
            "total_days": stat.total_days,
            "current_streak": stat.current_streak,
            "best_streak": stat.best_streak,
            "completion_rate": float(stat.completion_rate),
            "last_completed_at": stat.last_completed_at,
        }
    return payload


def build_stats_response(user, *, advanced: bool) -> dict:
    tasks = list(Task.objects.filter(user=user))
    active_tasks = [task for task in tasks if task.is_active]
    total_tasks = len(tasks)
    active_count = len(active_tasks)

    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    progress_rows = TaskProgress.objects.filter(user=user)
    completed_total = progress_rows.filter(is_completed=True).count()
    completed_week = progress_rows.filter(is_completed=True, progress_date__gte=week_start).count()
    completed_month = progress_rows.filter(is_completed=True, progress_date__gte=month_start).count()

    simple = {
        "total_tasks": total_tasks,
        "active_tasks": active_count,
        "completed_checkins_total": completed_total,
    }

    if not advanced:
        return {"simple": simple, "advanced": None}

    stats = [update_task_stats(task) for task in tasks]
    best_streak = max((stat.best_streak for stat in stats), default=0)
    current_streak = max((stat.current_streak for stat in stats), default=0)

    weekly_distribution = list(
        progress_rows.filter(progress_date__gte=week_start)
        .values("progress_date")
        .annotate(completed=Count("id"))
        .order_by("progress_date")
    )

    monthly_distribution = list(
        progress_rows.filter(progress_date__gte=month_start)
        .values("progress_date")
        .annotate(completed=Count("id"))
        .order_by("progress_date")
    )

    return {
        "simple": simple,
        "advanced": {
            "current_streak": current_streak,
            "best_streak": best_streak,
            "completed_week": completed_week,
            "completed_month": completed_month,
            "weekly_distribution": weekly_distribution,
            "monthly_distribution": monthly_distribution,
        },
    }


def upsert_progress(task: Task, user, progress_day: date, completed: bool, note: str = "") -> TaskProgress:
    row, _ = TaskProgress.objects.get_or_create(task=task, progress_date=progress_day, defaults={"user": user})
    row.user = user
    row.is_completed = completed
    row.completed_at = timezone.now() if completed else None
    row.note = (note or "").strip()[:280]
    row.save(update_fields=["user", "is_completed", "completed_at", "note", "updated_at"])
    update_task_stats(task)
    return row
