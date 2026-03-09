from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .router import complete
from .prompt_builder import get_chat_system_prompt
from core.system_config import get_ai_chat_rate_limit


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


class SendChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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
        system = get_chat_system_prompt(request.user, language)
        reply = complete(message, system=system, user_id=request.user.id)
        return Response({"reply": reply})
