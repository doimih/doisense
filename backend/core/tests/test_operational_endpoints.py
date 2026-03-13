import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import BackupRestoreRequest, SupportTicket


@pytest.mark.django_db
def test_support_ticket_sets_default_sla(authenticated_client):
    response = authenticated_client.post(
        reverse("support-tickets"),
        {"subject": "Need help", "message": "Issue details"},
        format="json",
    )

    assert response.status_code == 201
    ticket = SupportTicket.objects.get(id=response.data["id"])
    assert ticket.first_response_due_at is not None
    assert ticket.resolution_due_at is not None


@pytest.mark.django_db
def test_support_ticket_thread_allows_user_reply(authenticated_client):
    created = authenticated_client.post(
        reverse("support-tickets"),
        {"subject": "Need update", "message": "Initial issue"},
        format="json",
    )
    assert created.status_code == 201

    ticket_id = created.data["id"]
    detail = authenticated_client.get(reverse("support-ticket-detail", args=[ticket_id]))
    assert detail.status_code == 200
    assert len(detail.data["messages"]) == 1

    reply = authenticated_client.post(
        reverse("support-ticket-detail", args=[ticket_id]),
        {"message": "Additional context"},
        format="json",
    )
    assert reply.status_code == 201
    assert reply.data["ticket"]["id"] == ticket_id
    assert len(reply.data["ticket"]["messages"]) == 2


@pytest.mark.django_db
def test_support_admin_can_reply_to_ticket(user):
    from users.models import User

    ticket_owner = user
    ticket = SupportTicket.objects.create(
        user=ticket_owner,
        subject="Billing issue",
        message="Please help",
    )

    admin_user = User.objects.create_user(
        email="support-admin@example.com",
        password="StrongPass123",
        language="en",
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )

    client = APIClient()
    token = RefreshToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

    listing = client.get(reverse("support-admin-tickets"))
    assert listing.status_code == 200
    assert any(item["id"] == ticket.id for item in listing.data["items"])

    reply = client.post(
        reverse("support-ticket-detail", args=[ticket.id]),
        {"message": "We are checking this now.", "status": "in_progress"},
        format="json",
    )
    assert reply.status_code == 201
    assert reply.data["ticket"]["status"] == "in_progress"


@pytest.mark.django_db
def test_backup_restore_request_requires_confirmation(user):
    user.is_staff = True
    user.save(update_fields=["is_staff"])

    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")

    bad = client.post(
        reverse("backup-restore-requests"),
        {"restore_point": "base_0001", "reason": "test", "confirmation": "WRONG"},
        format="json",
    )
    assert bad.status_code == 400

    good = client.post(
        reverse("backup-restore-requests"),
        {"restore_point": "base_0001", "reason": "test", "confirmation": "CONFIRM_RESTORE"},
        format="json",
    )
    assert good.status_code == 201
    assert BackupRestoreRequest.objects.count() == 1
