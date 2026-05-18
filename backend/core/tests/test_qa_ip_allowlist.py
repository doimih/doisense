import pytest
from django.urls import reverse

from core.models import SystemConfig


@pytest.fixture(autouse=True)
def _disable_ssl_redirect(settings):
    settings.SECURE_SSL_REDIRECT = False


@pytest.mark.django_db
def test_allowlist_empty_does_not_block_api(api_client):
    config = SystemConfig.get_solo()
    config.qa_allowed_source_ips = ""
    config.save(update_fields=["qa_allowed_source_ips", "updated_at"])

    response = api_client.post(
        reverse("auth-register"),
        {
            "email": "allowlist-empty@example.com",
            "password": "SecurePass123",
            "language": "en",
            "accepted_terms": True,
            "accepted_privacy": True,
            "accepted_ai_usage": True,
        },
        format="json",
        REMOTE_ADDR="198.51.100.9",
    )

    assert response.status_code != 403


@pytest.mark.django_db
def test_allowlisted_ip_can_access_api(api_client):
    config = SystemConfig.get_solo()
    config.qa_allowed_source_ips = "198.51.100.0/24"
    config.save(update_fields=["qa_allowed_source_ips", "updated_at"])

    response = api_client.post(
        reverse("auth-register"),
        {
            "email": "allowlisted-ip@example.com",
            "password": "SecurePass123",
            "language": "en",
            "accepted_terms": True,
            "accepted_privacy": True,
            "accepted_ai_usage": True,
        },
        format="json",
        REMOTE_ADDR="198.51.100.42",
    )

    assert response.status_code != 403


@pytest.mark.django_db
def test_non_allowlisted_ip_is_blocked(api_client):
    config = SystemConfig.get_solo()
    config.qa_allowed_source_ips = "203.0.113.10"
    config.save(update_fields=["qa_allowed_source_ips", "updated_at"])

    response = api_client.post(
        reverse("auth-register"),
        {
            "email": "blocked-ip@example.com",
            "password": "SecurePass123",
            "language": "en",
            "accepted_terms": True,
            "accepted_privacy": True,
            "accepted_ai_usage": True,
        },
        format="json",
        REMOTE_ADDR="198.51.100.44",
    )

    assert response.status_code == 403
    assert response.json().get("code") == "ip_not_allowed"


@pytest.mark.django_db
def test_healthcheck_is_exempt_from_allowlist(api_client):
    config = SystemConfig.get_solo()
    config.qa_allowed_source_ips = "203.0.113.10"
    config.save(update_fields=["qa_allowed_source_ips", "updated_at"])

    response = api_client.get(reverse("health-check"), REMOTE_ADDR="198.51.100.44")

    assert response.status_code == 200
    assert response.data["status"] == "ok"
