from django.utils import timezone

from ai.prompt_builder import get_chat_system_prompt, get_user_package_tier, validate_save_to_db
from users.models import User


def test_get_user_package_tier_distinguishes_trial(user):
    user.plan_tier = User.PLAN_TRIAL
    user.is_premium = True
    user.trial_started_at = timezone.now()
    user.trial_ends_at = timezone.now() + timezone.timedelta(days=1)

    assert get_user_package_tier(user) == "TRIAL"


def test_chat_prompt_for_trial_mentions_preview_limits(user):
    user.plan_tier = User.PLAN_TRIAL
    user.is_premium = True
    user.trial_started_at = timezone.now()
    user.trial_ends_at = timezone.now() + timezone.timedelta(days=1)
    user.save(update_fields=["plan_tier", "is_premium", "trial_started_at", "trial_ends_at"])

    prompt = get_chat_system_prompt(user, "en", current_message="Can you diagnose me?", conversation_count=9)

    assert "User tier: TRIAL." in prompt
    assert "weekly or monthly reports" in prompt
    assert "paid plans after the trial" in prompt
    assert "Iti sunt alaturi cu suport emotional" in prompt


def test_chat_prompt_for_basic_contains_light_upsell(user):
    user.plan_tier = User.PLAN_BASIC
    user.is_premium = True
    user.save(update_fields=["plan_tier", "is_premium"])

    prompt = get_chat_system_prompt(user, "en", current_message="Can you build a long-term report?", conversation_count=1)

    assert "User tier: BASIC." in prompt
    assert "avoid formal plans, reports, or typology updates" in prompt
    assert "paid tiers unlock richer ongoing guidance" in prompt


def test_chat_prompt_for_premium_allows_weekly_but_not_typology(user):
    user.plan_tier = User.PLAN_PREMIUM
    user.is_premium = True
    user.save(update_fields=["plan_tier", "is_premium"])

    prompt = get_chat_system_prompt(user, "en", current_message="Give me a summary.", conversation_count=2)

    assert "User tier: PREMIUM." in prompt
    assert "daily or weekly-style summaries" in prompt
    assert "Do not produce monthly reports or formal typology updates" in prompt


def test_chat_prompt_for_vip_enables_typology_without_upsell(user):
    user.plan_tier = User.PLAN_VIP
    user.is_premium = True
    user.save(update_fields=["plan_tier", "is_premium"])

    prompt = get_chat_system_prompt(user, "en", current_message="Map my longer-term patterns.", conversation_count=5)

    assert "User tier: VIP." in prompt
    assert "monthly-style reflections" in prompt
    assert "typology as a working hypothesis" in prompt
    assert "Do not upsell" in prompt


def test_validate_save_to_db_blocks_reports_for_trial(user):
    user.plan_tier = User.PLAN_TRIAL
    user.is_premium = True
    user.trial_started_at = timezone.now()
    user.trial_ends_at = timezone.now() + timezone.timedelta(days=1)
    user.save(update_fields=["plan_tier", "is_premium", "trial_started_at", "trial_ends_at"])

    result = validate_save_to_db(
        user,
        {
            "save_to_db": {
                "daily_reports": True,
                "weekly_reports": True,
                "monthly_reports": True,
                "typology_update": True,
            }
        },
    )

    assert result["save_to_db"] == {
        "daily_reports": False,
        "weekly_reports": False,
        "monthly_reports": False,
        "typology_update": False,
    }