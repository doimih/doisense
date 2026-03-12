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
