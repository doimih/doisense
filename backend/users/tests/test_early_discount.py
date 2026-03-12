import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_early_discount_enabled_for_first_500_non_vip_users():
    user = User.objects.create_user(
        email="early-discount@example.com",
        password="StrongPass123",
        vip_manual_override=False,
    )

    user.refresh_from_db()
    assert user.id <= 500
    assert user.early_discount_eligible is True


@pytest.mark.django_db
def test_early_discount_disabled_when_user_id_exceeds_limit():
    user = User.objects.create_user(
        id=501,
        email="no-early-discount@example.com",
        password="StrongPass123",
        vip_manual_override=False,
    )

    user.refresh_from_db()
    assert user.id == 501
    assert user.early_discount_eligible is False


@pytest.mark.django_db
def test_early_discount_disabled_for_manual_vip():
    user = User.objects.create_user(
        email="vip-manual@example.com",
        password="StrongPass123",
        vip_manual_override=True,
    )

    user.refresh_from_db()
    assert user.vip_manual_override is True
    assert user.early_discount_eligible is False
