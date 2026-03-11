import pytest
from django.contrib import admin
from django.test import RequestFactory

from users.models import User


@pytest.mark.django_db
def test_staff_user_has_unlimited_platform_access():
    user = User.objects.create_user(
        email="staff@example.com",
        password="testpass123",
        language="en",
        is_staff=True,
        plan_tier=User.PLAN_FREE,
        is_premium=False,
    )

    assert user.has_unlimited_platform_access() is True
    assert user.has_paid_access() is True
    assert user.effective_plan_tier() == User.PLAN_VIP


@pytest.mark.django_db
def test_superuser_has_unlimited_platform_access():
    user = User.objects.create_superuser(
        email="super@example.com",
        password="testpass123",
        language="en",
    )

    assert user.has_unlimited_platform_access() is True
    assert user.has_paid_access() is True
    assert user.effective_plan_tier() == User.PLAN_VIP


@pytest.mark.django_db
def test_admin_site_rejects_staff_non_superuser():
    user = User.objects.create_user(
        email="staff-no-admin@example.com",
        password="testpass123",
        language="en",
        is_staff=True,
        is_active=True,
    )
    request = RequestFactory().get("/doisense/ro/admin/")
    request.user = user

    assert admin.site.has_permission(request) is False


@pytest.mark.django_db
def test_admin_site_allows_superuser():
    user = User.objects.create_superuser(
        email="super-admin@example.com",
        password="testpass123",
        language="en",
    )
    request = RequestFactory().get("/doisense/ro/admin/")
    request.user = user

    assert admin.site.has_permission(request) is True