import pytest
from django.core.management import call_command
from django.utils import timezone

from ai.models import Conversation
from core.models import NotificationDelivery


@pytest.mark.django_db
def test_reactivation_campaign_sends_once_per_segment(user):
    user.plan_tier = "premium"
    user.is_premium = True
    user.save(update_fields=["plan_tier", "is_premium"])

    conversation = Conversation.objects.create(
        user=user,
        module="general",
        plan_tier="premium",
        user_message="hello",
        ai_response="hi",
    )
    Conversation.objects.filter(pk=conversation.pk).update(
        created_at=timezone.now() - timezone.timedelta(days=15)
    )

    call_command("send_reactivation_campaign")
    assert NotificationDelivery.objects.filter(
        user=user,
        notification_type="reactivation_campaign",
        context_key="reactivation:inactive_14d",
    ).count() == 1

    # Running again should keep dedupe for the same segment.
    call_command("send_reactivation_campaign")
    assert NotificationDelivery.objects.filter(
        user=user,
        notification_type="reactivation_campaign",
        context_key="reactivation:inactive_14d",
    ).count() == 1
