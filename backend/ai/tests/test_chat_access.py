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