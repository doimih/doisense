import pytest
from django.urls import reverse

from core.models import InAppNotification, SupportTicket


@pytest.mark.django_db
def test_support_chat_creates_ticket_for_technical_issue(authenticated_client, user, monkeypatch):
    monkeypatch.setattr("ai.views_support.complete", lambda **kwargs: "Please try a hard refresh.")

    response = authenticated_client.post(
        reverse("support-ask"),
        {"message": "I have a technical error and need human support urgently."},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["intent"] == "tech"
    assert response.data["ticket"]["created"] is True
    assert "ticket" in response.data

    ticket = SupportTicket.objects.get(user=user)
    assert ticket.status == SupportTicket.STATUS_OPEN
    assert "Technical support" in ticket.subject
    notification = InAppNotification.objects.get(user=user, notification_type="support_ticket_created")
    assert str(ticket.id) in notification.body


@pytest.mark.django_db
def test_support_chat_reuses_open_ticket_for_same_issue(authenticated_client, user, monkeypatch):
    monkeypatch.setattr("ai.views_support.complete", lambda **kwargs: "We are checking this.")

    message = "I have a technical error and need human support urgently."
    first = authenticated_client.post(reverse("support-ask"), {"message": message}, format="json")
    second = authenticated_client.post(reverse("support-ask"), {"message": message}, format="json")

    assert first.status_code == 200
    assert second.status_code == 200
    assert SupportTicket.objects.filter(user=user).count() == 1
    assert second.data["ticket"]["created"] is False
    assert second.data["ticket"]["id"] == first.data["ticket"]["id"]


@pytest.mark.django_db
def test_support_chat_does_not_create_ticket_for_general_question(authenticated_client, user, monkeypatch):
    monkeypatch.setattr("ai.views_support.complete", lambda **kwargs: "Here is how the platform works.")

    response = authenticated_client.post(
        reverse("support-ask"),
        {"message": "How does the platform work?"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["intent"] == "general"
    assert "ticket" not in response.data
    assert SupportTicket.objects.filter(user=user).count() == 0
