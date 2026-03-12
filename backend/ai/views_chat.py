from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation
from .router import complete
from .prompt_builder import get_chat_system_prompt
from core.analytics import track_event
from core.feature_access import require_feature
from core.quota import check_and_consume
from core.system_config import get_ai_chat_rate_limit, get_ai_max_tokens


def _rate_limit_key(user_id):
    return f"chat_rate:{user_id}"


def _check_rate_limit(user_id) -> bool:
    key = _rate_limit_key(user_id)
    count = cache.get(key, 0)
    limit = get_ai_chat_rate_limit()
    if count >= limit:
        return False
    cache.set(key, count + 1, timeout=60)
    return True


def _get_effective_chat_tier(user) -> str:
    return user.effective_plan_tier()


def _get_history_window(plan_tier: str) -> int:
    return {"trial": 4, "basic": 2, "premium": 6, "vip": 12}.get(plan_tier, 0)


def _get_max_response_tokens(plan_tier: str) -> int:
    configured_limit = get_ai_max_tokens()
    tier_limit = {"trial": 640, "basic": 420, "premium": 800, "vip": 1200}.get(plan_tier, 420)
    return max(256, min(configured_limit, tier_limit))


def _extract_module(message: str) -> str:
    if not message.startswith("[") or "]" not in message:
        return ""
    prefix = message.split("]", 1)[0].lstrip("[")
    return (prefix.split("|", 1)[0] or "").strip().lower()


def _build_recent_context(user, plan_tier: str) -> str:
    history_window = _get_history_window(plan_tier)
    if history_window <= 0:
        return ""

    items = list(
        Conversation.objects.filter(user=user)
        .order_by("-created_at")[:history_window]
    )
    if not items:
        return ""

    parts = ["Recent conversation context:"]
    for item in reversed(items):
        parts.append(f"User: {item.user_message}")
        parts.append(f"Assistant: {item.ai_response}")
    return "\n".join(parts)


class SendChatView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("chat_ai")
    def post(self, request):
        allowed, remaining, limit = check_and_consume(request.user, "chat_messages", amount=1)
        if not allowed:
            base_url = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
            language = request.user.language or "en"
            return Response(
                {
                    "detail": "Daily chat quota exceeded for your tier.",
                    "code": "quota_exceeded",
                    "metric": "chat_messages",
                    "limit": limit,
                    "remaining": remaining,
                    "cta_url": f"{base_url}/{language}/pricing",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not _check_rate_limit(request.user.id):
            return Response(
                {"detail": "Rate limit exceeded. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        message = (request.data.get("message") or "").strip()
        if not message:
            return Response(
                {"detail": "message is required and cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        language = getattr(request.user, "language", "en") or "en"
        plan_tier = _get_effective_chat_tier(request.user)
        conversation_count = Conversation.objects.filter(user=request.user).count()
        system = get_chat_system_prompt(
            request.user,
            language,
            current_message=message,
            conversation_count=conversation_count,
        )
        recent_context = _build_recent_context(request.user, plan_tier)
        full_prompt = message if not recent_context else f"{recent_context}\n\nCurrent user message:\n{message}"
        reply = complete(
            full_prompt,
            system=system,
            user_id=request.user.id,
            max_tokens=_get_max_response_tokens(plan_tier),
        )
        Conversation.objects.create(
            user=request.user,
            module=_extract_module(message),
            plan_tier=plan_tier,
            user_message=message,
            ai_response=reply,
        )
        track_event(
            "chat_message_sent",
            source="backend",
            user=request.user,
            properties={"module": _extract_module(message) or "general"},
        )
        return Response({"reply": reply})
