import pytest
from django.urls import reverse
from django.utils import timezone

from ai.models import Conversation
from users.models import User


@pytest.mark.django_db
def test_chat_requires_active_subscription(authenticated_client, user):
    user.plan_tier = User.PLAN_FREE
    user.is_premium = False
    user.save(update_fields=["plan_tier", "is_premium"])

    response = authenticated_client.post(
        reverse("chat-send"),
        {"message": "Hello"},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_chat_saves_conversation_for_paid_user(authenticated_client, user, monkeypatch):
    user.plan_tier = User.PLAN_PREMIUM
    user.is_premium = True
    user.save(update_fields=["plan_tier", "is_premium"])

    monkeypatch.setattr("ai.views_chat.complete", lambda *args, **kwargs: "AI reply")

    response = authenticated_client.post(
        reverse("chat-send"),
        {"message": "[Wellness|mood:ok|energy:3] Hello"},
        format="json",
    )

    assert response.status_code == 200
    conversation = Conversation.objects.get()
    assert conversation.plan_tier == "premium"
    assert conversation.module == "wellness"
    assert conversation.ai_response == "AI reply"


@pytest.mark.django_db
def test_chat_keeps_trial_tier_distinct(authenticated_client, user, monkeypatch):
    user.plan_tier = User.PLAN_TRIAL
    user.is_premium = True
    user.trial_started_at = timezone.now()
    user.trial_ends_at = timezone.now() + timezone.timedelta(days=1)
    user.save(update_fields=["plan_tier", "is_premium", "trial_started_at", "trial_ends_at"])

    captured = {}

    def fake_complete(prompt, system=None, user_id=None, max_tokens=None):
        captured["prompt"] = prompt
        captured["system"] = system
        captured["user_id"] = user_id
        captured["max_tokens"] = max_tokens
        return "Trial reply"

    monkeypatch.setattr("ai.views_chat.complete", fake_complete)

    response = authenticated_client.post(
        reverse("chat-send"),
        {"message": "Can you diagnose me?"},
        format="json",
    )

    assert response.status_code == 200
    conversation = Conversation.objects.get()
    assert conversation.plan_tier == "trial"
    assert captured["max_tokens"] == 640
    assert "User tier: TRIAL." in captured["system"]
    assert "Iti sunt alaturi cu suport emotional" in captured["system"]


@pytest.mark.django_db
def test_translate_draft_returns_translated_text(authenticated_client, user, monkeypatch):
    user.plan_tier = User.PLAN_PREMIUM
    user.is_premium = True
    user.save(update_fields=["plan_tier", "is_premium"])

    def fake_complete(prompt, system=None, user_id=None, max_tokens=None):
        assert "language code 'en'" in prompt
        return "I feel stressed today"

    monkeypatch.setattr("ai.views_chat.complete", fake_complete)

    response = authenticated_client.post(
        reverse("chat-translate-draft"),
        {"text": "Ma simt stresat azi", "source_language": "ro", "target_language": "en"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["translated_text"] == "I feel stressed today"
    assert response.data["status"] == "translated"


@pytest.mark.django_db
def test_translate_draft_falls_back_to_original_text_on_provider_error(
    authenticated_client, user, monkeypatch
):
    user.plan_tier = User.PLAN_PREMIUM
    user.is_premium = True
    user.save(update_fields=["plan_tier", "is_premium"])

    monkeypatch.setattr("ai.views_chat.complete", lambda *args, **kwargs: "[AI not configured]")

    response = authenticated_client.post(
        reverse("chat-translate-draft"),
        {"text": "Ma simt stresat azi", "source_language": "ro", "target_language": "en"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["translated_text"] == "Ma simt stresat azi"
    assert response.data["status"] == "fallback"


@pytest.mark.django_db
@pytest.mark.parametrize("target_language", ["ro", "en", "de", "fr", "it", "es", "pl"])
def test_translate_draft_supports_all_site_languages(
    authenticated_client, user, monkeypatch, target_language
):
    user.plan_tier = User.PLAN_PREMIUM
    user.is_premium = True
    user.save(update_fields=["plan_tier", "is_premium"])

    def fake_complete(prompt, system=None, user_id=None, max_tokens=None):
        assert f"language code '{target_language}'" in prompt
        return f"translated-{target_language}"

    monkeypatch.setattr("ai.views_chat.complete", fake_complete)

    source_language = "ro" if target_language == "en" else "en"
    source_text = "Ma simt stresat azi" if source_language == "ro" else "I feel stressed today"

    response = authenticated_client.post(
        reverse("chat-translate-draft"),
        {
            "text": source_text,
            "source_language": source_language,
            "target_language": target_language,
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["translated_text"] == f"translated-{target_language}"
    assert response.data["status"] == "translated"
