import pytest
from django.urls import reverse

from payments.models import Payment


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