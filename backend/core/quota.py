from datetime import date

from django.db import transaction

from .analytics import track_event
from .models import UserQuotaUsage


PERIOD_BY_METRIC = {
    "chat_messages": UserQuotaUsage.PERIOD_DAY,
    "journal_entries": UserQuotaUsage.PERIOD_MONTH,
    "program_days_completed": UserQuotaUsage.PERIOD_MONTH,
}


QUOTA_LIMITS = {
    "chat_messages": {
        "trial": 40,
        "basic": 80,
        "premium": 300,
        "vip": 1000,
    },
    "journal_entries": {
        "trial": 30,
        "basic": 80,
        "premium": 300,
        "vip": 1000,
    },
    "program_days_completed": {
        "trial": 20,
        "basic": 60,
        "premium": 200,
        "vip": 1000,
    },
}


def _period_start(period_type: str) -> date:
    today = date.today()
    if period_type == UserQuotaUsage.PERIOD_DAY:
        return today
    return today.replace(day=1)


def _resolve_user_tier(user) -> str:
    if hasattr(user, "effective_plan_tier"):
        return user.effective_plan_tier()
    return "premium" if getattr(user, "is_premium", False) else "free"


def quota_limit_for(user, metric_key: str) -> int:
    tier = _resolve_user_tier(user)
    return QUOTA_LIMITS.get(metric_key, {}).get(tier, 0)


def check_and_consume(user, metric_key: str, amount: int = 1):
    period_type = PERIOD_BY_METRIC.get(metric_key)
    if not period_type:
        return True, 999999, 999999

    limit = quota_limit_for(user, metric_key)
    if limit <= 0:
        track_event(
            "quota_exceeded",
            source="backend",
            user=user,
            properties={"metric_key": metric_key},
        )
        return False, 0, 0

    start = _period_start(period_type)

    with transaction.atomic():
        usage, _ = UserQuotaUsage.objects.select_for_update().get_or_create(
            user=user,
            metric_key=metric_key,
            period_type=period_type,
            period_start=start,
            defaults={"used_count": 0},
        )
        if usage.used_count + amount > limit:
            track_event(
                "quota_exceeded",
                source="backend",
                user=user,
                properties={"metric_key": metric_key},
            )
            remaining = max(0, limit - usage.used_count)
            return False, remaining, limit

        usage.used_count += amount
        usage.save(update_fields=["used_count", "updated_at"])

    remaining = max(0, limit - usage.used_count)
    return True, remaining, limit
