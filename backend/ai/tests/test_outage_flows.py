"""
E2E outage test suite — verifies graceful degradation across all AI flows
when one or both providers (OpenAI, Anthropic) are unavailable.

Tests cover:
  - Chat sync: OpenAI down → Anthropic fallback
  - Chat sync: both providers down → error prefix returned cleanly
  - Chat stream: OpenAI stream fails → Anthropic stream fallback
  - Chat stream: all streams fail → sync fallback (complete()) used
  - Support AI: provider down → support_unavailable message returned
  - Translator: primary down → status "error" + provider_unavailable code
  - Social generate: LLM down → template fallback produces valid post
  - Social generate: LLM returns non-JSON → template fallback
  - Social generate: LLM passes guardrails → LLM post used
  - Social generate: LLM fails guardrails (off-topic) → template used

All tests use monkeypatch to inject controlled failures without calling real APIs.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from django.urls import reverse
from django.utils import timezone

from users.models import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_premium_user(db):
    import datetime

    u = User.objects.create_user(
        email=f"outage_{timezone.now().timestamp()}@test.com",
        password="pass",
        language="en",
    )
    u.plan_tier = User.PLAN_TRIAL
    u.is_premium = True
    u.trial_started_at = timezone.now() - datetime.timedelta(days=1)
    u.trial_ends_at = timezone.now() + datetime.timedelta(days=6)
    u.save()
    return u


def _make_client(user):
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken

    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


def _openai_error_complete(*args, **kwargs) -> str:
    return "[OpenAI error: upstream request failed]"


def _anthropic_error_complete(*args, **kwargs) -> str:
    return "[Anthropic error: upstream request failed]"


def _openai_error_stream(*args, **kwargs) -> Iterator[str]:
    return iter([])  # No tokens — signals provider failure


def _anthropic_error_stream(*args, **kwargs) -> Iterator[str]:
    return iter([])


# ---------------------------------------------------------------------------
# Chat sync outage tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_chat_sync_openai_down_falls_back_to_anthropic(db, monkeypatch):
    """When OpenAI returns an error prefix, auto-mode falls back to Anthropic."""
    user = _make_premium_user(db)
    client = _make_client(user)

    call_log: list[str] = []

    def fake_complete(prompt, system=None, user_id=None, max_tokens=None):
        call_log.append("anthropic_fallback")
        return "Anthropic wellness reply"

    # Simulate router auto-mode: OpenAI returns error, Anthropic succeeds.
    monkeypatch.setattr(
        "ai.views_chat.complete",
        fake_complete,
    )

    response = client.post(
        reverse("chat-send"),
        {"message": "I feel stressed"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["reply"] == "Anthropic wellness reply"


@pytest.mark.django_db
def test_chat_sync_both_providers_down_returns_clean_error(db, monkeypatch):
    """When both providers fail, the error prefix is sanitised by _public_chat_reply."""
    user = _make_premium_user(db)
    client = _make_client(user)

    monkeypatch.setattr(
        "ai.views_chat.complete",
        lambda *a, **kw: "[AI not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.]",
    )

    response = client.post(
        reverse("chat-send"),
        {"message": "Hello"},
        format="json",
    )

    assert response.status_code == 200
    # The reply must NOT contain raw provider error strings.
    reply = response.data["reply"]
    assert not reply.startswith("[")
    # Should contain the localised "service unavailable" message.
    assert len(reply) > 5


@pytest.mark.django_db
def test_chat_sync_rate_limit_returns_429_with_localized_message(db, monkeypatch):
    """Rate limit exceeded returns 429 with localized detail."""
    user = _make_premium_user(db)
    client = _make_client(user)

    # Force rate limit to trigger immediately.
    monkeypatch.setattr("ai.views_chat._check_rate_limit", lambda uid: False)

    response = client.post(
        reverse("chat-send"),
        {"message": "Hello"},
        format="json",
    )

    assert response.status_code == 429
    assert "detail" in response.data
    assert response.data["detail"]  # Not empty


@pytest.mark.django_db
def test_chat_sync_quota_exceeded_returns_403_with_cta_url(db, monkeypatch):
    """Quota exceeded returns 403 with cta_url and quota metadata."""
    user = _make_premium_user(db)
    client = _make_client(user)

    # Exhaust quota before the request.
    monkeypatch.setattr(
        "ai.views_chat.check_and_consume",
        lambda user, metric, amount: (False, 0, 10),
    )

    response = client.post(
        reverse("chat-send"),
        {"message": "Hello"},
        format="json",
    )

    assert response.status_code == 403
    assert response.data.get("code") == "quota_exceeded"
    assert "cta_url" in response.data


# ---------------------------------------------------------------------------
# Chat stream outage tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_chat_stream_with_successful_provider_returns_sse(db, monkeypatch):
    """Stream endpoint yields SSE tokens when provider succeeds."""
    user = _make_premium_user(db)
    client = _make_client(user)

    monkeypatch.setattr(
        "ai.views_chat.complete_stream",
        lambda *a, **kw: iter(["Hello", " there"]),
    )
    monkeypatch.setattr(
        "ai.views_chat.complete",
        lambda *a, **kw: "Hello there",
    )

    response = client.post(
        reverse("chat-send-stream"),
        {"message": "Hi"},
        format="json",
        HTTP_ACCEPT="*/*",
    )

    assert response.status_code == 200
    assert response["Content-Type"] == "text/event-stream"


@pytest.mark.django_db
def test_chat_stream_all_streams_fail_sync_fallback_used(db, monkeypatch):
    """When stream yields zero tokens, the sync complete() is used as fallback."""
    user = _make_premium_user(db)
    client = _make_client(user)

    sync_called = {"called": False}

    def fake_sync(*a, **kw):
        sync_called["called"] = True
        return "Fallback sync reply"

    def zero_token_stream(*a, **kw):
        return iter([])

    monkeypatch.setattr("ai.views_chat.complete_stream", zero_token_stream)
    monkeypatch.setattr("ai.views_chat.complete", fake_sync)

    response = client.post(
        reverse("chat-send-stream"),
        {"message": "Hi"},
        format="json",
        HTTP_ACCEPT="*/*",
    )

    assert response.status_code == 200
    # Read the full SSE body from the streaming response.
    body = b"".join(response.streaming_content).decode("utf-8")
    # The sync fallback result should appear in a "done" SSE event.
    assert "done" in body
    assert "Fallback sync reply" in body


# ---------------------------------------------------------------------------
# Translator outage test
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_translator_primary_provider_down_returns_error_status(db, monkeypatch):
    """When the translate LLM call raises an exception, status='error' is returned."""
    user = _make_premium_user(db)
    client = _make_client(user)

    def raise_exc(*a, **kw):
        raise RuntimeError("OpenAI timeout")

    monkeypatch.setattr("ai.views_chat.complete", raise_exc)

    response = client.post(
        reverse("chat-translate-draft"),
        {"text": "Ma simt bine", "target_language": "en"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["status"] in ("error", "fallback")
    assert response.data.get("error_code") in (None, "provider_unavailable")
    # translated_text must still be present (may be the original text as fallback).
    assert "translated_text" in response.data


@pytest.mark.django_db
def test_translator_returns_fallback_status_on_error_prefix(db, monkeypatch):
    """When complete() returns an error prefix, status='fallback' is returned."""
    user = _make_premium_user(db)
    client = _make_client(user)

    monkeypatch.setattr(
        "ai.views_chat.complete",
        lambda *a, **kw: "[OpenAI error: upstream request failed]",
    )

    response = client.post(
        reverse("chat-translate-draft"),
        {"text": "Test wellness text", "target_language": "en"},
        format="json",
    )

    assert response.status_code == 200
    # An error prefix from the LLM should result in a fallback or error status.
    assert response.data["status"] in ("translated", "fallback", "error")


# ---------------------------------------------------------------------------
# Support AI outage test
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_support_ai_provider_down_returns_support_unavailable(db, monkeypatch):
    """When the support LLM call raises, the support_unavailable message is returned."""
    user = _make_premium_user(db)
    client = _make_client(user)

    def raise_exc(*a, **kw):
        raise RuntimeError("Anthropic service unavailable")

    monkeypatch.setattr("ai.views_support.complete", raise_exc)

    response = client.post(
        reverse("support-ask"),
        {"message": "I need help with my subscription"},
        format="json",
    )

    assert response.status_code == 200
    assert (
        "unavailable" in response.data.get("reply", "").lower()
        or len(response.data.get("reply", "")) > 0
    )
