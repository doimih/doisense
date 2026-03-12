import pytest
from django.urls import reverse

from ai.models import DailyReport, MonthlyReport


@pytest.mark.django_db
def test_reports_daily_available_for_premium(authenticated_client, user):
    user.plan_tier = "premium"
    user.is_premium = True
    user.save(update_fields=["plan_tier", "is_premium"])

    DailyReport.objects.create(
        user=user,
        date="2026-03-10",
        summary="Daily summary",
        highlights=["h1"],
        challenges=["c1"],
        recommendations=["r1"],
    )

    response = authenticated_client.get(reverse("chat-reports"), {"type": "daily"})

    assert response.status_code == 200
    assert response.data["type"] == "daily"
    assert len(response.data["items"]) == 1


@pytest.mark.django_db
def test_reports_monthly_requires_vip(authenticated_client, user):
    user.plan_tier = "premium"
    user.is_premium = True
    user.save(update_fields=["plan_tier", "is_premium"])

    MonthlyReport.objects.create(
        user=user,
        year=2026,
        month=3,
        summary="Monthly summary",
        trends=["trend"],
        insights="Insight",
        recommendations=["rec"],
    )

    response = authenticated_client.get(reverse("chat-reports"), {"type": "monthly"})
    assert response.status_code == 403
