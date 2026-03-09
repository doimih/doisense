import json
from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.urls import reverse
from django.utils import timezone

from ai.models import AILog
from journal.models import JournalEntry
from payments.models import Payment
from users.models import User


def _daily_counts(queryset, date_field, days):
    today = timezone.localdate()
    start_date = today - timedelta(days=days - 1)

    rows = (
        queryset.filter(**{f"{date_field}__date__gte": start_date})
        .annotate(day=TruncDate(date_field))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    values_by_day = {row["day"]: row["total"] for row in rows}
    labels = []
    values = []

    for index in range(days):
        day = start_date + timedelta(days=index)
        labels.append(day.strftime("%d %b"))
        values.append(values_by_day.get(day, 0))

    return labels, values


def _daily_user_conversion(days):
    today = timezone.localdate()
    start_date = today - timedelta(days=days - 1)

    rows = (
        User.objects.filter(created_at__date__gte=start_date)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(
            total=Count("id"),
            premium=Count("id", filter=Q(is_premium=True)),
        )
        .order_by("day")
    )

    values_by_day = {
        row["day"]: {"total": row["total"], "premium": row["premium"]} for row in rows
    }

    labels = []
    rates = []
    cumulative_total = 0
    cumulative_premium = 0

    for index in range(days):
        day = start_date + timedelta(days=index)
        daily = values_by_day.get(day, {"total": 0, "premium": 0})
        cumulative_total += daily["total"]
        cumulative_premium += daily["premium"]
        rate = round((cumulative_premium / cumulative_total) * 100, 2) if cumulative_total else 0

        labels.append(day.strftime("%d %b"))
        rates.append(rate)

    return labels, rates


def dashboard_callback(request, context):
    allowed_periods = [7, 30, 90]
    raw_period = request.GET.get("period", "30")
    try:
        selected_period = int(raw_period)
    except (TypeError, ValueError):
        selected_period = 30
    if selected_period not in allowed_periods:
        selected_period = 30

    now = timezone.now()
    today = timezone.localdate()
    start_7d = now - timedelta(days=7)
    start_30d = now - timedelta(days=30)
    start_period = now - timedelta(days=selected_period)

    total_users = User.objects.count()
    premium_users = User.objects.filter(is_premium=True).count()
    new_users_30d = User.objects.filter(created_at__gte=start_30d).count()

    active_subscriptions = Payment.objects.filter(status__in=["active", "trialing"]).count()
    journal_entries = JournalEntry.objects.count()
    ai_logs = AILog.objects.count()

    active_users_7d = (
        User.objects.filter(
            Q(journal_entries__created_at__gte=start_7d) | Q(ailog__created_at__gte=start_7d)
        )
        .distinct()
        .count()
    )

    user_labels, user_values = _daily_counts(User.objects.all(), "created_at", selected_period)
    journal_labels, journal_values = _daily_counts(
        JournalEntry.objects.all(), "created_at", selected_period
    )
    conversion_labels, conversion_values = _daily_user_conversion(selected_period)

    premium_users_period = User.objects.filter(
        is_premium=True,
        created_at__gte=start_period,
    ).count()
    users_period = User.objects.filter(created_at__gte=start_period).count()
    premium_conversion_period = (
        round((premium_users_period / users_period) * 100, 2) if users_period else 0
    )

    language_counts = (
        User.objects.values("language").annotate(total=Count("id")).order_by("-total")[:5]
    )
    language_progress = []
    for row in language_counts:
        pct = round((row["total"] / total_users) * 100) if total_users else 0
        language_progress.append(
            {
                "title": (row["language"] or "?").upper(),
                "value": pct,
                "description": f"{pct}%",
                "progress_class": "",
            }
        )

    user_chart_data = json.dumps(
        {
            "labels": user_labels,
            "datasets": [
                {
                    "label": "Utilizatori noi",
                    "data": user_values,
                    "borderColor": "rgb(192, 132, 44)",
                    "backgroundColor": "rgba(192, 132, 44, 0.22)",
                    "pointBackgroundColor": "rgb(148, 87, 12)",
                    "fill": True,
                    "tension": 0.35,
                }
            ],
        }
    )

    journal_chart_data = json.dumps(
        {
            "labels": journal_labels,
            "datasets": [
                {
                    "label": "Jurnale create",
                    "data": journal_values,
                    "backgroundColor": "rgba(112, 56, 202, 0.72)",
                    "borderColor": "rgb(86, 32, 168)",
                    "borderRadius": 6,
                }
            ],
        }
    )

    conversion_chart_data = json.dumps(
        {
            "labels": conversion_labels,
            "datasets": [
                {
                    "label": "Conversie premium (%)",
                    "data": conversion_values,
                    "borderColor": "rgb(185, 28, 28)",
                    "backgroundColor": "rgba(185, 28, 28, 0.15)",
                    "pointBackgroundColor": "rgb(185, 28, 28)",
                    "fill": True,
                    "tension": 0.3,
                }
            ],
        }
    )

    chart_options = json.dumps(
        {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "legend": {
                    "display": True,
                    "labels": {
                        "color": "#44403c",
                    },
                },
            },
            "scales": {
                "x": {
                    "grid": {"color": "rgba(120, 113, 108, 0.12)"},
                    "ticks": {"color": "#57534e"},
                },
                "y": {
                    "beginAtZero": True,
                    "grid": {"color": "rgba(120, 113, 108, 0.14)"},
                    "ticks": {"precision": 0, "color": "#57534e"},
                }
            },
        }
    )

    conversion_chart_options = json.dumps(
        {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "legend": {
                    "display": True,
                    "labels": {
                        "color": "#44403c",
                    },
                },
            },
            "scales": {
                "x": {
                    "grid": {"color": "rgba(120, 113, 108, 0.12)"},
                    "ticks": {"color": "#57534e"},
                },
                "y": {
                    "beginAtZero": True,
                    "max": 100,
                    "grid": {"color": "rgba(120, 113, 108, 0.14)"},
                    "ticks": {"precision": 0},
                },
            },
        }
    )

    period_filters = [
        {
            "value": period,
            "label": f"{period}d",
            "active": selected_period == period,
            "url": f"{reverse('admin:index')}?period={period}",
        }
        for period in allowed_periods
    ]

    context.update(
        {
            "analytics": {
                "generated_at": today.strftime("%d %b %Y"),
                "selected_period": selected_period,
                "total_users": total_users,
                "premium_users": premium_users,
                "new_users_30d": new_users_30d,
                "active_subscriptions": active_subscriptions,
                "journal_entries": journal_entries,
                "ai_logs": ai_logs,
                "active_users_7d": active_users_7d,
                "premium_rate": round((premium_users / total_users) * 100) if total_users else 0,
                "premium_conversion_period": premium_conversion_period,
            },
            "period_filters": period_filters,
            "user_chart_data": user_chart_data,
            "journal_chart_data": journal_chart_data,
            "conversion_chart_data": conversion_chart_data,
            "chart_options": chart_options,
            "conversion_chart_options": conversion_chart_options,
            "language_progress": language_progress,
        }
    )

    return context
