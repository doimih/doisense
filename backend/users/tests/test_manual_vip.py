import pytest
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from users.models import User


@pytest.mark.django_db
def test_manual_vip_forces_effective_vip_and_bypasses_trial_state(user):
    user.plan_tier = User.PLAN_TRIAL
    user.is_premium = False
    user.trial_started_at = timezone.now() - timedelta(days=10)
    user.trial_ends_at = timezone.now() - timedelta(days=3)
    user.vip_manual_override = True
    user.save(
        update_fields=[
            "plan_tier",
            "is_premium",
            "trial_started_at",
            "trial_ends_at",
            "vip_manual_override",
        ]
    )

    assert user.manual_vip is True
    assert user.is_in_trial() is False
    assert user.effective_plan_tier() == User.PLAN_VIP
    assert user.has_paid_access() is True


@pytest.mark.django_db
def test_send_trial_warnings_skips_manual_vip_users():
    user = User.objects.create_user(
        email="manual-vip-trial@example.com",
        password="testpass123",
        plan_tier=User.PLAN_TRIAL,
        is_premium=True,
        trial_started_at=timezone.now() - timedelta(days=1),
        trial_ends_at=timezone.now() + timedelta(days=6),
        vip_manual_override=True,
    )

    out = StringIO()
    with patch("core.notifications.send_trial_expiration_warning") as mock_send:
        call_command("send_trial_warnings", stdout=out)

    assert user not in [call[0][0] for call in mock_send.call_args_list] if mock_send.call_args_list else True


@pytest.mark.django_db
def test_expire_trials_does_not_downgrade_manual_vip_users():
    user = User.objects.create_user(
        email="manual-vip-expired@example.com",
        password="testpass123",
        plan_tier=User.PLAN_TRIAL,
        is_premium=True,
        trial_started_at=timezone.now() - timedelta(days=8),
        trial_ends_at=timezone.now() - timedelta(days=1),
        vip_manual_override=True,
    )

    out = StringIO()
    call_command("expire_trials", stdout=out)

    user.refresh_from_db()
    assert user.plan_tier == User.PLAN_TRIAL
    assert user.is_premium is True
    assert user.vip_manual_override is True
