from dataclasses import dataclass
from typing import Any

from django.utils import timezone

from .models import CalendarPlan, CalendarUserPlan


BASIC_CAPABILITIES = {
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
}

PREMIUM_CAPABILITIES = {
    **BASIC_CAPABILITIES,
    "advanced_stats": True,
    "task_history": True,
    "profile_monthly_view": True,
    "advanced_task_options": True,
}

VIP_CAPABILITIES = {
    **PREMIUM_CAPABILITIES,
    "ai_habit_suggestions": True,
    "ai_routine_builder": True,
    "ai_daily_checkin": True,
    "ai_progress_insights": True,
    "ai_habit_optimization": True,
}


@dataclass
class CalendarPlanContext:
    code: str
    name: str
    capabilities: dict[str, Any]

    def has(self, capability: str) -> bool:
        return bool(self.capabilities.get(capability, False))


PLAN_CODE_TO_LABEL = {
    "basic": "BASIC Start",
    "premium": "PREMIUM Flow",
    "vip": "VIP Executive",
}

PLAN_CODE_TO_CAPABILITIES = {
    "basic": BASIC_CAPABILITIES,
    "premium": PREMIUM_CAPABILITIES,
    "vip": VIP_CAPABILITIES,
}


def _map_user_tier_to_calendar_code(user_tier: str) -> str | None:
    if user_tier in ("vip",):
        return "vip"
    if user_tier in ("premium",):
        return "premium"
    if user_tier in ("trial", "basic"):
        return "basic"
    return None


def _resolve_from_calendar_user_plan(user) -> str | None:
    now = timezone.now()
    row = (
        CalendarUserPlan.objects.select_related("plan")
        .filter(user=user, is_active=True)
        .order_by("-started_at")
        .first()
    )
    if not row:
        return None
    if row.expires_at and row.expires_at <= now:
        return None
    return row.plan.code


def resolve_calendar_plan_for_user(user) -> CalendarPlanContext | None:
    if not user or not getattr(user, "is_authenticated", False):
        return None

    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        code = "vip"
    else:
        code = _resolve_from_calendar_user_plan(user)
        if not code:
            tier = user.effective_plan_tier() if hasattr(user, "effective_plan_tier") else "free"
            code = _map_user_tier_to_calendar_code(tier)

    if not code:
        return None

    capabilities = PLAN_CODE_TO_CAPABILITIES[code]
    name = PLAN_CODE_TO_LABEL[code]
    return CalendarPlanContext(code=code, name=name, capabilities=capabilities)


def ensure_seed_plans() -> None:
    for code, label in PLAN_CODE_TO_LABEL.items():
        CalendarPlan.objects.get_or_create(
            code=code,
            defaults={
                "name": label,
                "description": f"Plan {label} for Calendar & Task module",
                "capabilities": PLAN_CODE_TO_CAPABILITIES[code],
            },
        )
