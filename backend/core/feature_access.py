from functools import wraps

from django.http import JsonResponse

from .analytics import track_event
from .models import FeatureAccessLog


TIER_ORDER = {
    "free": 0,
    "normal": 0,
    "trial": 1,
    "basic": 2,
    "premium": 3,
    "vip": 4,
}

FEATURE_MATRIX = {
    "analytics_track": ["free", "trial", "basic", "premium", "vip"],
    "chat_ai": ["trial", "basic", "premium", "vip"],
    "journal_access": ["trial", "basic", "premium", "vip"],
    "programs_access": ["trial", "basic", "premium", "vip"],
    "premium_programs": ["premium", "vip"],
    "payment_checkout": ["free", "trial", "basic", "premium", "vip"],
    "payment_upgrade": ["trial", "basic", "premium", "vip"],
}


def resolve_user_tier(user) -> str:
    if not user or not getattr(user, "is_authenticated", False):
        return "anonymous"
    if hasattr(user, "effective_plan_tier"):
        tier = user.effective_plan_tier()
    else:
        tier = "premium" if getattr(user, "is_premium", False) else "free"
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return "vip"
    return tier


def is_feature_allowed(user, feature_key: str):
    required = FEATURE_MATRIX.get(feature_key, ["vip"])
    tier = resolve_user_tier(user)

    if tier == "anonymous":
        return False, tier, required, "authentication_required"

    if tier in required:
        return True, tier, required, "tier_allowed"

    current_weight = TIER_ORDER.get(tier, 0)
    required_weight = min(TIER_ORDER.get(item, 999) for item in required)
    allowed = current_weight >= required_weight
    return allowed, tier, required, "tier_allowed" if allowed else "tier_blocked"


def log_feature_access(user, feature_key: str, granted: bool, required_tiers, user_tier: str, reason: str, context=None):
    FeatureAccessLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        feature_key=feature_key,
        required_tiers=list(required_tiers),
        user_tier=user_tier,
        granted=bool(granted),
        reason=reason,
        context=context or {},
    )
    track_event(
        "feature_access_checked",
        source="system",
        user=user if getattr(user, "is_authenticated", False) else None,
        properties={
            "feature_key": feature_key,
            "granted": bool(granted),
        },
    )


def require_feature(feature_key: str):
    def decorator(method):
        @wraps(method)
        def wrapper(self, request, *args, **kwargs):
            allowed, user_tier, required, reason = is_feature_allowed(request.user, feature_key)
            log_feature_access(
                request.user,
                feature_key,
                allowed,
                required,
                user_tier,
                reason,
                context={"path": request.path, "method": request.method},
            )
            if not allowed:
                return JsonResponse(
                    {
                        "detail": "This feature is not available for your current tier.",
                        "feature": feature_key,
                        "required_tiers": required,
                        "current_tier": user_tier,
                    },
                    status=403,
                )
            return method(self, request, *args, **kwargs)

        return wrapper

    return decorator
