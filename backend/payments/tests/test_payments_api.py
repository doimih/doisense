import pytest
from django.urls import reverse
from django.core.cache import cache

from payments.models import Payment


@pytest.fixture(autouse=True)
def _clear_throttle_cache():
    cache.clear()


@pytest.mark.django_db
def test_checkout_session_falls_back_to_internal_activation(authenticated_client, user):
    response = authenticated_client.post(
        reverse("create-checkout-session"),
        {"plan_tier": "basic"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["internal_activation"] is True
    assert response.data["plan_tier"] == "basic"

    user.refresh_from_db()
    payment = Payment.objects.get(user=user)
    assert user.plan_tier == "basic"
    assert user.is_premium is True
    assert payment.plan_tier == "basic"
    assert payment.status == "active"


@pytest.mark.django_db
def test_checkout_session_applies_early_discount_for_premium(authenticated_client, user):
    user.early_discount_eligible = True
    user.vip_manual_override = False
    user.save(update_fields=["early_discount_eligible", "vip_manual_override"])

    response = authenticated_client.post(
        reverse("create-checkout-session"),
        {"plan_tier": "premium"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["internal_activation"] is True
    assert response.data["applied_plan_tier"] == "premium_discounted"
    assert response.data["early_discount_applied"] is True
    assert response.data["early_discount_percent"] == 10

    user.refresh_from_db()
    payment = Payment.objects.get(user=user)
    assert user.plan_tier == "premium"
    assert payment.plan_tier == "premium_discounted"


@pytest.mark.django_db
def test_checkout_session_skips_early_discount_for_manual_vip(authenticated_client, user):
    user.early_discount_eligible = True
    user.vip_manual_override = True
    user.save(update_fields=["early_discount_eligible", "vip_manual_override"])

    response = authenticated_client.post(
        reverse("create-checkout-session"),
        {"plan_tier": "premium"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["manual_vip"] is True
    assert response.data["effective_tier"] == "vip"
    assert Payment.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_early_discount_eligibility_persists_after_vip_toggle(authenticated_client, user):
    user.early_discount_eligible = True
    user.vip_manual_override = True
    user.save(update_fields=["early_discount_eligible", "vip_manual_override"])

    first_response = authenticated_client.post(
        reverse("create-checkout-session"),
        {"plan_tier": "premium"},
        format="json",
    )
    assert first_response.status_code == 200
    assert first_response.data["manual_vip"] is True

    user.refresh_from_db()
    assert user.early_discount_eligible is True

    user.vip_manual_override = False
    user.save(update_fields=["vip_manual_override"])

    user.refresh_from_db()
    assert user.early_discount_eligible is True

    second_response = authenticated_client.post(
        reverse("create-checkout-session"),
        {"plan_tier": "premium"},
        format="json",
    )
    assert second_response.status_code == 200
    assert second_response.data["early_discount_applied"] is True
    assert second_response.data["applied_plan_tier"] == "premium_discounted"


@pytest.mark.django_db
def test_cancel_subscription_marks_cancel_at_period_end(authenticated_client, user):
    payment = Payment.objects.create(
        user=user,
        stripe_customer_id="cus_test",
        stripe_subscription_id="sub_test",
        status="active",
        plan_tier="premium",
    )

    response = authenticated_client.post(
        reverse("cancel-subscription"),
        {},
        format="json",
    )

    assert response.status_code == 200

    payment.refresh_from_db()
    assert payment.cancel_at_period_end is True


@pytest.mark.django_db
def test_manual_vip_checkout_bypasses_subscription_logic(authenticated_client, user):
    user.vip_manual_override = True
    user.save(update_fields=["vip_manual_override"])

    response = authenticated_client.post(
        reverse("create-checkout-session"),
        {"plan_tier": "premium"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["manual_vip"] is True
    assert response.data["effective_tier"] == "vip"
    assert Payment.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_manual_vip_upgrade_bypasses_subscription_logic(authenticated_client, user):
    user.vip_manual_override = True
    user.save(update_fields=["vip_manual_override"])

    response = authenticated_client.post(
        reverse("upgrade-subscription"),
        {"plan_tier": "vip"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["manual_vip"] is True
    assert response.data["upgraded"] is False


@pytest.mark.django_db
def test_manual_vip_cancel_bypasses_subscription_logic(authenticated_client, user):
    user.vip_manual_override = True
    user.save(update_fields=["vip_manual_override"])

    response = authenticated_client.post(
        reverse("cancel-subscription"),
        {},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["manual_vip"] is True
    assert response.data["cancel_at_period_end"] is False


@pytest.mark.django_db
def test_manual_vip_subscription_status_is_vip(authenticated_client, user):
    user.vip_manual_override = True
    user.save(update_fields=["vip_manual_override"])

    response = authenticated_client.get(reverse("subscription-status"))

    assert response.status_code == 200
    assert response.data["manual_vip"] is True
    assert response.data["effective_tier"] == "vip"
    assert response.data["status"] == "manual_vip"


@pytest.mark.django_db
def test_promo_state_active_for_eligible_user(authenticated_client, user):
    user.early_discount_eligible = True
    user.vip_manual_override = False
    user.save(update_fields=["early_discount_eligible", "vip_manual_override"])

    response = authenticated_client.get(reverse("promo-state"))

    assert response.status_code == 200
    assert response.data["promo_key"] == "premium_early_discount"
    assert response.data["is_active"] is True
    assert response.data["discount_percent"] == 10
    assert response.data["target_plan"] == "premium"


@pytest.mark.django_db
def test_promo_state_inactive_for_manual_vip(authenticated_client, user):
    user.early_discount_eligible = True
    user.vip_manual_override = True
    user.save(update_fields=["early_discount_eligible", "vip_manual_override"])

    response = authenticated_client.get(reverse("promo-state"))

    assert response.status_code == 200
    assert response.data["is_active"] is False
    assert response.data["discount_percent"] == 0
    assert response.data["manual_vip"] is True