import pytest
from django.urls import reverse

from ai.models import Conversation
from core.models import UserWellbeingCheckin
from journal.models import JournalEntry


@pytest.mark.django_db
def test_delete_account_anonymizes_user_and_preserves_content(authenticated_client, user, journal_question):
    user.vip_manual_override = True
    user.early_discount_eligible = True
    user.plan_tier = "trial"
    user.trial_started_at = user.created_at
    user.trial_ends_at = user.created_at
    user.save(
        update_fields=[
            "vip_manual_override",
            "early_discount_eligible",
            "plan_tier",
            "trial_started_at",
            "trial_ends_at",
        ]
    )

    JournalEntry.objects.create(
        user=user,
        question=journal_question,
        content="Initial journal entry",
        emotions=["ok"],
    )
    UserWellbeingCheckin.objects.create(user=user, mood="ok", energy_level=6)
    Conversation.objects.create(
        user=user,
        module="wellness",
        plan_tier="premium",
        user_message="I feel overwhelmed. My email is test@example.com.",
        ai_response="Let's slow down, test@example.com, and name what feels heavy.",
    )

    response = authenticated_client.delete(reverse("me"))

    assert response.status_code == 204

    user.refresh_from_db()
    conversation = Conversation.objects.get()

    assert user.is_active is False
    assert user.plan_tier == "free"
    assert user.vip_manual_override is False
    assert user.early_discount_eligible is False
    assert user.trial_started_at is None
    assert user.trial_ends_at is None
    assert user.email == f"deleted.user.{user.id}@doisense.local"
    assert user.first_name == ""
    assert user.last_name == ""
    assert user.phone_contact == ""
    assert JournalEntry.objects.count() == 0
    assert UserWellbeingCheckin.objects.count() == 0
    assert conversation.user_id is None
    assert "test@example.com" not in conversation.user_message
    assert "test@example.com" not in conversation.ai_response