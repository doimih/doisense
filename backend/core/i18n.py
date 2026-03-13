"""User-facing localization helpers for backend flows."""

from __future__ import annotations

from typing import Mapping, TypeVar


SUPPORTED_LANGUAGES = ("ro", "en", "de", "fr", "it", "es", "pl")

T = TypeVar("T")


def normalize_language(value: str | None, default: str = "en") -> str:
    fallback = default if default in SUPPORTED_LANGUAGES else "en"
    if not value:
        return fallback

    candidate = value.strip().lower().replace("_", "-")
    if not candidate:
        return fallback

    candidate = candidate.split(",", 1)[0].split(";", 1)[0].strip()
    base = candidate.split("-", 1)[0]
    return base if base in SUPPORTED_LANGUAGES else fallback


def get_user_language(user=None, default: str = "en") -> str:
    return normalize_language(getattr(user, "language", None), default)


def get_request_language(request, *, user=None, default: str = "en") -> str:
    candidates: list[str | None] = []

    if hasattr(request, "data"):
        try:
            candidates.append(request.data.get("language"))
        except Exception:
            pass

    if hasattr(request, "query_params"):
        candidates.append(request.query_params.get("language"))

    if hasattr(request, "headers"):
        candidates.append(request.headers.get("X-Language"))
        candidates.append(request.headers.get("Accept-Language"))

    if hasattr(request, "COOKIES"):
        candidates.append(request.COOKIES.get("i18n_redirect"))

    candidates.append(getattr(user, "language", None))

    for candidate in candidates:
        normalized = normalize_language(candidate, default)
        if candidate and normalized:
            return normalized

    return normalize_language(None, default)


def translate(messages: Mapping[str, T], language: str, default: str = "en") -> T:
    normalized = normalize_language(language, default)
    fallback = normalize_language(default, "en")
    if normalized in messages:
        return messages[normalized]
    if fallback in messages:
        return messages[fallback]
    return next(iter(messages.values()))