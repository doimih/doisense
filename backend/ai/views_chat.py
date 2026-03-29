from django.conf import settings
from django.core.cache import cache
from django.http import StreamingHttpResponse
import json
import re
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation
from .router import complete, complete_stream
from .prompt_builder import get_chat_system_prompt
from core.analytics import track_event
from core.feature_access import require_feature
from core.i18n import get_user_language, normalize_language, translate
from core.quota import check_and_consume
from core.system_config import get_ai_chat_rate_limit, get_ai_max_tokens
from ai_core.orchestrator import build_final_prompt


_CHAT_COPY = {
    "ro": {
        "message_required": "Campul message este obligatoriu si nu poate fi gol.",
        "quota_exceeded": "Cota zilnica de chat a fost depasita pentru planul tau.",
        "rate_limit": "Limita de solicitari depasita. Incearca din nou mai tarziu.",
        "stream_timeout": "Generarea a esuat din cauza unui timeout. Incearca din nou.",
        "stream_failed": "Generarea a esuat. Te rugam sa incerci din nou.",
        "text_too_long": "Textul este prea lung (maxim 1200 de caractere).",
        "reply_empty": "Momentan nu am putut genera un raspuns. Incearca din nou.",
        "reply_unavailable": "Momentan serviciul AI este indisponibil. Incearca din nou in cateva momente.",
        "stream_processing": "Procesez raspunsul...",
    },
    "en": {
        "message_required": "message is required and cannot be empty",
        "quota_exceeded": "Daily chat quota exceeded for your tier.",
        "rate_limit": "Rate limit exceeded. Try again later.",
        "stream_timeout": "Streaming failed due to upstream timeout.",
        "stream_failed": "Streaming failed. Please try again.",
        "text_too_long": "text is too long (max 1200 chars)",
        "reply_empty": "We could not generate a response at this time. Please try again.",
        "reply_unavailable": "The AI service is currently unavailable. Please try again in a few moments.",
        "stream_processing": "Processing your response...",
    },
    "de": {
        "message_required": "Das Feld message ist erforderlich und darf nicht leer sein.",
        "quota_exceeded": "Taeglich Chat-Kontingent fuer Ihr Abonnement ueberschritten.",
        "rate_limit": "Anfragelimit ueberschritten. Bitte versuche es spaeter erneut.",
        "stream_timeout": "Streaming fehlgeschlagen aufgrund eines Timeouts.",
        "stream_failed": "Streaming fehlgeschlagen. Bitte versuche es erneut.",
        "text_too_long": "Text ist zu lang (maximal 1200 Zeichen).",
        "reply_empty": "Im Moment konnte keine Antwort generiert werden. Bitte versuche es erneut.",
        "reply_unavailable": "Der KI-Dienst ist momentan nicht verfuegbar. Bitte versuche es in einigen Momenten erneut.",
        "stream_processing": "Antwort wird verarbeitet...",
    },
    "fr": {
        "message_required": "Le champ message est obligatoire et ne peut pas etre vide.",
        "quota_exceeded": "Quota quotidien de chat depasse pour votre abonnement.",
        "rate_limit": "Limite de requetes depassee. Veuillez reessayer plus tard.",
        "stream_timeout": "Le streaming a echoue en raison d un delai d attente.",
        "stream_failed": "Le streaming a echoue. Veuillez reessayer.",
        "text_too_long": "Le texte est trop long (maximum 1200 caracteres).",
        "reply_empty": "Nous n avons pas pu generer une reponse pour le moment. Veuillez reessayer.",
        "reply_unavailable": "Le service IA est actuellement indisponible. Veuillez reessayer dans quelques instants.",
        "stream_processing": "Traitement de votre reponse...",
    },
    "it": {
        "message_required": "Il campo message e obbligatorio e non puo essere vuoto.",
        "quota_exceeded": "Quota giornaliera di chat superata per il tuo piano.",
        "rate_limit": "Limite di richieste superato. Riprova piu tardi.",
        "stream_timeout": "Streaming fallito a causa di un timeout.",
        "stream_failed": "Streaming fallito. Riprova.",
        "text_too_long": "Il testo e troppo lungo (massimo 1200 caratteri).",
        "reply_empty": "Al momento non siamo riusciti a generare una risposta. Riprova.",
        "reply_unavailable": "Il servizio AI e momentaneamente non disponibile. Riprova tra qualche istante.",
        "stream_processing": "Elaborazione della risposta...",
    },
    "es": {
        "message_required": "El campo message es obligatorio y no puede estar vacio.",
        "quota_exceeded": "Cuota diaria de chat superada para tu plan.",
        "rate_limit": "Limite de solicitudes superado. Intenta de nuevo mas tarde.",
        "stream_timeout": "El streaming fallo debido a un tiempo de espera agotado.",
        "stream_failed": "El streaming fallo. Por favor, intenta de nuevo.",
        "text_too_long": "El texto es demasiado largo (maximo 1200 caracteres).",
        "reply_empty": "No pudimos generar una respuesta en este momento. Intenta de nuevo.",
        "reply_unavailable": "El servicio de IA no esta disponible en este momento. Intenta de nuevo en unos momentos.",
        "stream_processing": "Procesando tu respuesta...",
    },
    "pl": {
        "message_required": "Pole message jest wymagane i nie moze byc puste.",
        "quota_exceeded": "Dzienny limit czatu zostal przekroczony dla Twojego planu.",
        "rate_limit": "Limit zapytan przekroczony. Sprobuj ponownie pozniej.",
        "stream_timeout": "Przesylanie strumieniowe nie powiodlo sie z powodu przekroczenia czasu.",
        "stream_failed": "Przesylanie strumieniowe nie powiodlo sie. Sprobuj ponownie.",
        "text_too_long": "Tekst jest za dlugi (maksymalnie 1200 znakow).",
        "reply_empty": "Nie mogligmy wygenerowac odpowiedzi w tej chwili. Sprobuj ponownie.",
        "reply_unavailable": "Usluga AI jest chwilowo niedostepna. Sprobuj ponownie za chwile.",
        "stream_processing": "Przetwarzanie odpowiedzi...",
    },
}


def _chat_text(user, key: str) -> str:
    return translate(_CHAT_COPY, get_user_language(user)).get(key, _CHAT_COPY["en"][key])


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


def _build_recent_history_turns(user, plan_tier: str) -> list[tuple[str, str]]:
    history_window = _get_history_window(plan_tier)
    if history_window <= 0:
        return []

    items = list(
        Conversation.objects.filter(user=user)
        .order_by("-created_at")[:history_window]
    )
    return [(item.user_message or "", item.ai_response or "") for item in reversed(items)]


def _stream_processing_message(user) -> str:
    return _chat_text(user, "stream_processing")


def _sse(event: str, payload: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _prepare_chat_message(request):
    message = (request.data.get("message") or "").strip()
    if not message:
        return None, Response(
            {"detail": _chat_text(request.user, "message_required")},
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
    history_turns = _build_recent_history_turns(request.user, plan_tier)
    try:
        # Use orchestrator to build final runtime prompt while chat AI remains the responder.
        full_prompt = build_final_prompt(
            user_message=message,
            dynamic_context=recent_context or None,
            conversation_history=history_turns or None,
        )
    except Exception:
        full_prompt = message if not recent_context else f"{recent_context}\n\nCurrent user message:\n{message}"
    return {
        "message": message,
        "plan_tier": plan_tier,
        "system": system,
        "full_prompt": full_prompt,
        "max_tokens": _get_max_response_tokens(plan_tier),
    }, None


def _normalize_chat_reply(reply: str) -> str:
    """Remove markdown-like formatting so the UI gets clean plain text."""
    if not reply:
        return ""

    text = reply.replace("**", "").replace("__", "").replace("`", "")
    # Force inline numbered points into separate lines: "... 1. ... 2. ..." -> new line per point.
    text = re.sub(r"(?<!\n)\s+(\d+\.)\s+", r"\n\1 ", text)
    # Also force dashed bullets to start on new lines when returned inline.
    text = re.sub(r"(?<!\n)\s+-\s+", r"\n- ", text)
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = re.sub(r"^\s*#{1,6}\s*", "", raw_line).rstrip()
        if line.startswith("* "):
            line = "- " + line[2:]
        lines.append(line)

    return "\n".join(lines).strip()


def _public_chat_reply(reply: str, user=None) -> str:
    """Ensure frontend users never see backend/provider diagnostic payloads."""
    normalized = _normalize_chat_reply(reply)
    if not normalized:
        return _chat_text(user, "reply_empty")
    if normalized.startswith("["):
        return _chat_text(user, "reply_unavailable")
    return normalized


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
                    "detail": _chat_text(request.user, "quota_exceeded"),
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
                {"detail": _chat_text(request.user, "rate_limit")},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        payload, error = _prepare_chat_message(request)
        if error is not None:
            return error

        reply = complete(
            payload["full_prompt"],
            system=payload["system"],
            user_id=request.user.id,
            max_tokens=payload["max_tokens"],
        )
        reply = _public_chat_reply(reply, request.user)
        Conversation.objects.create(
            user=request.user,
            module=_extract_module(payload["message"]),
            plan_tier=payload["plan_tier"],
            user_message=payload["message"],
            ai_response=reply,
        )
        track_event(
            "chat_message_sent",
            source="backend",
            user=request.user,
            properties={"module": _extract_module(payload["message"]) or "general"},
        )
        return Response({"reply": reply})


class SendChatStreamView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("chat_ai")
    def post(self, request):
        allowed, remaining, limit = check_and_consume(request.user, "chat_messages", amount=1)
        if not allowed:
            base_url = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
            language = request.user.language or "en"
            return Response(
                {
                    "detail": _chat_text(request.user, "quota_exceeded"),
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
                {"detail": _chat_text(request.user, "rate_limit")},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        payload, error = _prepare_chat_message(request)
        if error is not None:
            return error

        def event_stream():
            chunks: list[str] = []
            try:
                # Quick-response fallback: notify UI immediately while generation continues.
                yield _sse("ack", {"message": _stream_processing_message(request.user)})
                for token in complete_stream(
                    payload["full_prompt"],
                    system=payload["system"],
                    user_id=request.user.id,
                    max_tokens=payload["max_tokens"],
                ):
                    if token:
                        chunks.append(token)
                        yield _sse("token", {"token": token})

                if not chunks:
                    # Stream produced nothing — fall back to synchronous completion.
                    sync_reply = complete(
                        payload["full_prompt"],
                        system=payload["system"],
                        user_id=request.user.id,
                        max_tokens=payload["max_tokens"],
                    )
                    reply = _public_chat_reply(sync_reply, request.user)
                else:
                    reply = _public_chat_reply("".join(chunks), request.user)
                Conversation.objects.create(
                    user=request.user,
                    module=_extract_module(payload["message"]),
                    plan_tier=payload["plan_tier"],
                    user_message=payload["message"],
                    ai_response=reply,
                )
                track_event(
                    "chat_message_sent",
                    source="backend",
                    user=request.user,
                    properties={"module": _extract_module(payload["message"]) or "general", "streaming": True},
                )
                yield _sse("done", {"reply": reply})
            except Exception as exc:
                detail = _chat_text(request.user, "stream_timeout") if "timeout" in str(exc).lower() else _chat_text(request.user, "stream_failed")
                yield _sse("error", {"detail": detail})

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


class TranslateDraftView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("chat_ai")
    def post(self, request):
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"translated_text": "", "status": "translated"})

        if len(text) > 1200:
            return Response(
                {"detail": _chat_text(request.user, "text_too_long")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_language = normalize_language(
            request.data.get("target_language") or getattr(request.user, "language", None) or "en"
        )
        source_raw = (request.data.get("source_language") or "").strip()
        source_language = normalize_language(source_raw) if source_raw else ""

        if source_language and source_language == target_language:
            return Response({"translated_text": text, "status": "translated"})

        source_line = f"Source language: {source_language}.\n" if source_language else ""
        prompt = (
            f"Translate the user text to language code '{target_language}'.\n"
            f"{source_line}"
            "Return only the translated text. No quotes. No explanation.\n"
            "Keep the same meaning, emotional tone, and brevity.\n"
            f"Text:\n{text}"
        )
        system = (
            "You are a precise translator for a wellbeing chat input field. "
            "Preserve first-person voice and intent. Do not add advice or extra content."
        )

        try:
            translated = complete(
                prompt,
                system=system,
                user_id=request.user.id,
                max_tokens=min(700, max(180, len(text) * 2)),
            ).strip()
        except Exception:
            translated = text
            track_event(
                "translator_result",
                source="backend",
                user=request.user,
                properties={"status": "error", "target_language": target_language},
            )
            return Response(
                {
                    "translated_text": translated,
                    "status": "error",
                    "error_code": "provider_unavailable",
                }
            )

        if not translated or translated.startswith("["):
            translated = text
            track_event(
                "translator_result",
                source="backend",
                user=request.user,
                properties={"status": "fallback", "target_language": target_language},
            )
            return Response({"translated_text": translated, "status": "fallback"})

        track_event(
            "translator_result",
            source="backend",
            user=request.user,
            properties={"status": "translated", "target_language": target_language},
        )
        return Response({"translated_text": translated, "status": "translated"})


HISTORY_DISPLAY_PER_MODULE = 5
_CHAT_MODULE_IDS = ["wellness", "coaching", "education", "support"]


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_tier = _get_effective_chat_tier(request.user)
        if _get_history_window(plan_tier) <= 0:
            return Response({"history": {}, "last_module": None})

        history = {}
        for mod in _CHAT_MODULE_IDS:
            items = list(
                Conversation.objects.filter(user=request.user, module=mod)
                .order_by("-created_at")[:HISTORY_DISPLAY_PER_MODULE]
            )
            if items:
                history[mod] = [
                    {
                        "user_message": item.user_message,
                        "ai_response": item.ai_response,
                        "created_at": item.created_at.isoformat(),
                    }
                    for item in reversed(items)
                ]

        last = (
            Conversation.objects.filter(user=request.user, module__in=_CHAT_MODULE_IDS)
            .order_by("-created_at")
            .values("module")
            .first()
        )
        last_module = last["module"] if last else None

        return Response({"history": history, "last_module": last_module})
