import re
from collections.abc import Iterable

from django.conf import settings
from django.core.cache import cache

from .models import Prompt


PROMPT_ORDER = [
    Prompt.TYPE_SYSTEM,
    Prompt.TYPE_PERSONALITY,
    Prompt.TYPE_RULES,
    Prompt.TYPE_CONTEXT,
]

_STATIC_PROMPT_TYPES = [Prompt.TYPE_SYSTEM, Prompt.TYPE_PERSONALITY, Prompt.TYPE_RULES]

_CACHE_VERSION_KEY = "ai_core:orchestrator:version"
_CACHE_KEY_PREFIX = "ai_core:orchestrator"


def _cache_ttl_seconds() -> int:
    return int(getattr(settings, "AI_ORCHESTRATOR_CACHE_TTL_SECONDS", 300))


def _max_history_turns() -> int:
    return int(getattr(settings, "AI_PROMPT_MAX_HISTORY_TURNS", 4))


def _max_context_chars() -> int:
    return int(getattr(settings, "AI_PROMPT_MAX_CONTEXT_CHARS", 1600))


def _max_message_chars() -> int:
    return int(getattr(settings, "AI_PROMPT_MAX_MESSAGE_CHARS", 2000))


def _get_cache_version() -> int:
    version = cache.get(_CACHE_VERSION_KEY)
    if version is None:
        cache.set(_CACHE_VERSION_KEY, 1, timeout=None)
        return 1
    return int(version)


def _cache_key(suffix: str) -> str:
    return f"{_CACHE_KEY_PREFIX}:v{_get_cache_version()}:{suffix}"


def invalidate_orchestrator_cache() -> None:
    """Bump orchestrator cache version after prompt changes."""
    try:
        cache.incr(_CACHE_VERSION_KEY)
    except ValueError:
        cache.set(_CACHE_VERSION_KEY, 2, timeout=None)


def _normalize_whitespace(text: str) -> str:
    if not text:
        return ""
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _dedupe_lines(text: str) -> str:
    if not text:
        return ""
    seen: set[str] = set()
    output: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        fingerprint = line.lower()
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        output.append(line)
    return "\n".join(output)


def trim_prompt_text(text: str, max_chars: int) -> str:
    """Compact prompt text by normalizing whitespace and removing repeated lines."""
    if not text:
        return ""
    compact = _normalize_whitespace(text)
    compact = _dedupe_lines(compact)
    if len(compact) <= max_chars:
        return compact
    clipped = compact[:max_chars].rsplit(" ", 1)[0].strip()
    return f"{clipped}\n[...trimmed for performance]"


def _trim_history(history_turns: Iterable[tuple[str, str]] | None) -> str:
    if not history_turns:
        return ""
    turns = list(history_turns)[-_max_history_turns():]
    lines: list[str] = []
    for user_text, assistant_text in turns:
        user_line = trim_prompt_text(user_text or "", _max_context_chars() // 2)
        assistant_line = trim_prompt_text(assistant_text or "", _max_context_chars() // 2)
        if user_line:
            lines.append(f"User: {user_line}")
        if assistant_line:
            lines.append(f"Assistant: {assistant_line}")
    return trim_prompt_text("\n".join(lines), _max_context_chars())


def _load_prompt_contents(prompt_type: str) -> list[str]:
    cache_key = _cache_key(f"prompt_type:{prompt_type}")
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    values = list(
        Prompt.objects.filter(type=prompt_type, language="en")
        .order_by("name")
        .values_list("content", flat=True)
    )
    cache.set(cache_key, values, timeout=_cache_ttl_seconds())
    return values


def _load_skill_prompt(skill_name: str | None) -> list[str]:
    if not skill_name:
        return []

    cache_key = _cache_key(f"skill:{skill_name}")
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    values = list(
        Prompt.objects.filter(type=Prompt.TYPE_SKILL, name=skill_name, language="en")
        .values_list("content", flat=True)
    )
    cache.set(cache_key, values, timeout=_cache_ttl_seconds())
    return values


def _build_static_prompt(include_greeting: bool = False) -> str:
    """Build and cache mostly static prompt prefix for fast runtime assembly."""
    cache_key = _cache_key(f"static:greet:{1 if include_greeting else 0}")
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    sections: list[str] = []
    for prompt_type in _STATIC_PROMPT_TYPES:
        sections.extend(_load_prompt_contents(prompt_type))
    if include_greeting:
        sections.extend(_load_prompt_contents(Prompt.TYPE_GREETING))

    static_prompt = "\n\n".join(
        trim_prompt_text(section, _max_context_chars())
        for section in sections
        if section and section.strip()
    )
    cache.set(cache_key, static_prompt, timeout=_cache_ttl_seconds())
    return static_prompt


def build_final_prompt(
    user_message: str,
    skill_name: str | None = None,
    include_greeting: bool = False,
    dynamic_context: str | None = None,
    conversation_history: Iterable[tuple[str, str]] | None = None,
) -> str:
    sections: list[str] = []

    static_prompt = _build_static_prompt(include_greeting=include_greeting)
    if static_prompt:
        sections.append(static_prompt)

    # Context can change often, so keep it dynamic and trimmed at runtime.
    context_sections = _load_prompt_contents(Prompt.TYPE_CONTEXT)
    if context_sections:
        sections.append(
            "\n\n".join(
                trim_prompt_text(section, _max_context_chars())
                for section in context_sections
                if section and section.strip()
            )
        )

    if dynamic_context:
        sections.append(f"Runtime context:\n{trim_prompt_text(dynamic_context, _max_context_chars())}")

    history_block = _trim_history(conversation_history)
    if history_block:
        sections.append(f"Recent conversation history:\n{history_block}")

    skill_sections = _load_skill_prompt(skill_name)
    if skill_sections:
        sections.append(
            "\n\n".join(
                trim_prompt_text(section, _max_context_chars())
                for section in skill_sections
                if section and section.strip()
            )
        )

    cleaned_message = trim_prompt_text((user_message or "").strip(), _max_message_chars())
    sections.append(f"User message:\n{cleaned_message}")

    return "\n\n".join(section for section in sections if section and section.strip())


def get_prompt_for_existing_ai(
    user_message: str,
    skill_name: str | None = None,
    include_greeting: bool = False,
) -> str:
    return build_final_prompt(
        user_message=user_message,
        skill_name=skill_name,
        include_greeting=include_greeting,
    )
