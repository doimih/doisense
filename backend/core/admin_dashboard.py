import json
from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.urls import reverse
from django.utils import timezone

from ai.models import AILog, Conversation
from core.models import (
    AdminAuditLog,
    AnalyticsEvent,
    BackupVerificationLog,
    InAppNotification,
    SupportTicket,
    SystemErrorEvent,
    UserQuotaUsage,
)
from journal.models import JournalEntry
from payments.models import Payment, StripeWebhookEvent
from programs.models import GuidedProgram, UserProgramProgress
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


def _tier_distribution():
    rows = (
        User.objects.values("plan_tier")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    tier_order = ["vip", "premium", "basic", "trial", "free"]
    tier_colors = {
        "vip": "rgba(217, 119, 6, 0.85)",
        "premium": "rgba(2, 132, 199, 0.85)",
        "basic": "rgba(22, 163, 74, 0.85)",
        "trial": "rgba(124, 58, 237, 0.72)",
        "free": "rgba(120, 113, 108, 0.55)",
    }
    total = sum(r["total"] for r in rows)
    result = []
    counts_by_tier = {r["plan_tier"]: r["total"] for r in rows}
    for tier in tier_order:
        n = counts_by_tier.get(tier, 0)
        pct = round((n / total) * 100) if total else 0
        result.append({
            "tier": tier.upper(),
            "count": n,
            "pct": pct,
            "color": tier_colors.get(tier, "rgba(100,100,100,0.5)"),
        })
    return result, total


def _mrr_estimate():
    """Return estimated MRR in RON based on active subscriptions by tier."""
    prices = {"basic": 59, "premium": 129, "premium_discounted": 116.1, "vip": 249}
    active = Payment.objects.filter(status__in=["active", "trialing"])
    mrr = 0
    for payment in active.iterator():
        mrr += prices.get(payment.plan_tier, 0)
    return round(mrr, 1)


def _churn_rate_30d():
    """Users whose subscription moved to cancelled/past_due in last 30 days."""
    start_30d = timezone.now() - timedelta(days=30)
    churned = Payment.objects.filter(
        status__in=["cancelled", "past_due"],
        updated_at__gte=start_30d,
    ).count()
    active_start = Payment.objects.filter(
        status__in=["active", "trialing"],
        created_at__lt=start_30d,
    ).count()
    if active_start <= 0:
        return 0.0
    return round((churned / active_start) * 100, 1)


def _ai_usage_by_tier(days: int):
    """Return AI conversation counts broken down by user plan_tier, over last N days."""
    start = timezone.now() - timedelta(days=days)
    rows = (
        Conversation.objects.filter(created_at__gte=start)
        .values("plan_tier")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    return list(rows)


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

    tier_distribution, _ = _tier_distribution()
    mrr = _mrr_estimate()
    churn_rate_30d = _churn_rate_30d()
    ai_by_tier = _ai_usage_by_tier(selected_period)
    month_start = today.replace(day=1)
    quota_usage_rows = list(
        UserQuotaUsage.objects.filter(
            period_type=UserQuotaUsage.PERIOD_MONTH,
            period_start=month_start,
        )
        .values("metric_key")
        .annotate(total_used=Sum("used_count"), users=Count("user", distinct=True))
        .order_by("metric_key")
    )
    quota_exceeded_30d = AnalyticsEvent.objects.filter(
        event_name="quota_exceeded",
        created_at__gte=start_30d,
    ).count()
    quota_exceeded_period = AnalyticsEvent.objects.filter(
        event_name="quota_exceeded",
        created_at__gte=start_period,
    ).count()
    onboarding_started_period = AnalyticsEvent.objects.filter(
        event_name="onboarding_started",
        created_at__gte=start_period,
    ).count()
    onboarding_completed_period = AnalyticsEvent.objects.filter(
        event_name="onboarding_completed",
        created_at__gte=start_period,
    ).count()
    onboarding_restarted_period = AnalyticsEvent.objects.filter(
        event_name="onboarding_restarted",
        created_at__gte=start_period,
    ).count()
    program_completed_period = AnalyticsEvent.objects.filter(
        event_name="program_completed",
        created_at__gte=start_period,
    ).count()
    program_dropout_period = AnalyticsEvent.objects.filter(
        event_name="program_dropout_detected",
        created_at__gte=start_period,
    ).count()
    program_reflection_period = AnalyticsEvent.objects.filter(
        event_name="program_reflection_submitted",
        created_at__gte=start_period,
    ).count()
    support_ticket_created_period = SupportTicket.objects.filter(created_at__gte=start_period).count()
    support_ticket_open_total = SupportTicket.objects.filter(
        status__in=[SupportTicket.STATUS_OPEN, SupportTicket.STATUS_IN_PROGRESS]
    ).count()
    in_app_unread_total = InAppNotification.objects.filter(is_read=False).count()
    subscription_cancel_requested_period = AnalyticsEvent.objects.filter(
        event_name="subscription_cancel_requested",
        created_at__gte=start_period,
    ).count()
    subscription_refunded_period = AnalyticsEvent.objects.filter(
        event_name="subscription_refunded",
        created_at__gte=start_period,
    ).count()
    webhook_events_30d = StripeWebhookEvent.objects.filter(first_received_at__gte=start_30d).count()
    webhook_failed_30d = StripeWebhookEvent.objects.filter(
        first_received_at__gte=start_30d,
        last_status=StripeWebhookEvent.STATUS_FAILED,
    ).count()
    webhook_ignored_30d = StripeWebhookEvent.objects.filter(
        first_received_at__gte=start_30d,
        last_status=StripeWebhookEvent.STATUS_IGNORED,
    ).count()
    system_errors_24h = SystemErrorEvent.objects.filter(created_at__gte=now - timedelta(hours=24)).count()
    system_errors_7d = SystemErrorEvent.objects.filter(created_at__gte=start_7d).count()
    critical_errors_7d = SystemErrorEvent.objects.filter(
        created_at__gte=start_7d,
        severity__in=[SystemErrorEvent.SEVERITY_HIGH, SystemErrorEvent.SEVERITY_CRITICAL],
    ).count()
    latest_system_error = SystemErrorEvent.objects.order_by("-created_at").values_list("created_at", flat=True).first()
    admin_audit_7d = AdminAuditLog.objects.filter(created_at__gte=start_7d).count()
    latest_backup = BackupVerificationLog.objects.order_by("-created_at").first()
    gdpr_delete_count = User.objects.filter(
        email__startswith="deleted.user.",
        is_active=False,
    ).count()
    upgrade_count_30d = Payment.objects.filter(
        created_at__gte=start_30d,
        status__in=["active", "trialing"],
    ).count()
    program_insights = []
    for program in GuidedProgram.objects.filter(active=True).order_by("title")[:25]:
        progress_qs = UserProgramProgress.objects.filter(program=program)
        started = progress_qs.count()
        total_days = max(program.days.count(), 1)
        completed = progress_qs.filter(current_day__gt=total_days).count()
        paused = progress_qs.filter(is_paused=True).count()
        dropped = progress_qs.filter(dropout_marked_at__isnull=False).count()
        completion_rate = round((completed / started) * 100, 1) if started else 0.0
        dropout_rate = round((dropped / started) * 100, 1) if started else 0.0
        program_insights.append(
            {
                "program_id": program.id,
                "title": program.title,
                "started": started,
                "completed": completed,
                "paused": paused,
                "dropped": dropped,
                "completion_rate": completion_rate,
                "dropout_rate": dropout_rate,
            }
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

    log_shortcuts = [
        {
            "title": "System Errors",
            "url": reverse("admin:core_systemerrorevent_changelist"),
        },
        {
            "title": "Admin Audit Logs",
            "url": reverse("admin:core_adminauditlog_changelist"),
        },
        {
            "title": "Stripe Webhooks",
            "url": reverse("admin:payments_stripewebhookevent_changelist"),
        },
        {
            "title": "Feature Access Logs",
            "url": reverse("admin:core_featureaccesslog_changelist"),
        },
        {
            "title": "Support Tickets",
            "url": reverse("admin:core_supportticket_changelist"),
        },
        {
            "title": "Backup Verification",
            "url": reverse("admin:core_backupverificationlog_changelist"),
        },
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
                "mrr": mrr,
                "churn_rate_30d": churn_rate_30d,
                "gdpr_delete_count": gdpr_delete_count,
                "upgrade_count_30d": upgrade_count_30d,
                "ai_by_tier": ai_by_tier,
                "quota_usage_rows": quota_usage_rows,
                "quota_exceeded_30d": quota_exceeded_30d,
                "quota_exceeded_period": quota_exceeded_period,
                "onboarding_started_period": onboarding_started_period,
                "onboarding_completed_period": onboarding_completed_period,
                "onboarding_restarted_period": onboarding_restarted_period,
                "program_completed_period": program_completed_period,
                "program_dropout_period": program_dropout_period,
                "program_reflection_period": program_reflection_period,
                "support_ticket_created_period": support_ticket_created_period,
                "support_ticket_open_total": support_ticket_open_total,
                "in_app_unread_total": in_app_unread_total,
                "subscription_cancel_requested_period": subscription_cancel_requested_period,
                "subscription_refunded_period": subscription_refunded_period,
                "webhook_events_30d": webhook_events_30d,
                "webhook_failed_30d": webhook_failed_30d,
                "webhook_ignored_30d": webhook_ignored_30d,
                "system_errors_24h": system_errors_24h,
                "system_errors_7d": system_errors_7d,
                "critical_errors_7d": critical_errors_7d,
                "latest_system_error": latest_system_error,
                "admin_audit_7d": admin_audit_7d,
                "latest_backup_status": getattr(latest_backup, "status", "n/a"),
                "latest_backup_at": getattr(latest_backup, "created_at", None),
                "program_insights": program_insights,
            },
            "tier_distribution": tier_distribution,
            "period_filters": period_filters,
            "log_shortcuts": log_shortcuts,
            "user_chart_data": user_chart_data,
            "journal_chart_data": journal_chart_data,
            "conversion_chart_data": conversion_chart_data,
            "chart_options": chart_options,
            "conversion_chart_options": conversion_chart_options,
            "language_progress": language_progress,
        }
    )

    return context
