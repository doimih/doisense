import json
from io import StringIO

import pytest
from django.core.management import call_command

from core.models import NotificationDelivery
from payments.models import Payment
from users.models import User


@pytest.mark.django_db
def test_manual_vip_audit_reports_conflicts_and_possible_wrong_marks():
    user = User.objects.create_user(
        email="manual-vip-audit@example.com",
        password="StrongPass123",
        vip_manual_override=True,
        is_active=False,
        is_premium=True,
        plan_tier=User.PLAN_TRIAL,
    )
    User.objects.filter(pk=user.pk).update(early_discount_eligible=True)
    Payment.objects.create(
        user=user,
        status="past_due",
        plan_tier="premium_discounted",
        cancel_at_period_end=True,
    )
    NotificationDelivery.objects.create(
        user=user,
        notification_type="trial_expiration_warning",
        sent_for_date=user.created_at.date(),
        context_key="day_5",
    )
    NotificationDelivery.objects.create(
        user=user,
        notification_type="upgrade_recommendation",
        sent_for_date=user.created_at.date(),
        context_key="report_limit",
    )

    out = StringIO()
    call_command("audit_manual_vip", "--json", stdout=out)
    payload = json.loads(out.getvalue())

    assert payload["manual_vip_count"] == 1
    assert payload["validated_manual_vip_users"][0]["effective_tier"] == "vip"
    assert {item["conflict"] for item in payload["detected_conflicts"]} >= {
        "early_discount_flag_active",
        "trial_notifications_sent",
        "upsell_notifications_sent",
        "discounted_subscription_attached",
        "subscription_cancel_state_present",
        "subscription_past_due_state_present",
    }
    assert payload["wrongly_marked_users"][0]["reason"] == "inactive_or_deleted_account"


@pytest.mark.django_db
def test_manual_vip_audit_can_fix_discount_flags():
    user = User.objects.create_user(
        email="manual-vip-fix@example.com",
        password="StrongPass123",
        vip_manual_override=True,
    )
    User.objects.filter(pk=user.pk).update(early_discount_eligible=True)

    out = StringIO()
    call_command("audit_manual_vip", "--fix-discount-flags", "--json", stdout=out)

    user.refresh_from_db()
    assert user.early_discount_eligible is False