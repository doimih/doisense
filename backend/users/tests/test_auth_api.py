import pytest
from django.core.cache import cache
from users.views import SocialLoginView
from django.urls import reverse
from rest_framework import status


@pytest.fixture(autouse=True)
def _disable_ssl_redirect_for_api_client(settings):
    settings.SECURE_SSL_REDIRECT = False


@pytest.fixture(autouse=True)
def _clear_cache_between_tests():
    cache.clear()


@pytest.mark.django_db
def test_register_success(api_client):
    url = reverse("auth-register")
    data = {
        "email": "new@example.com",
        "password": "SecurePass123",
        "language": "ro",
        "accepted_terms": True,
        "accepted_privacy": True,
        "accepted_ai_usage": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "detail" in response.data


@pytest.mark.django_db
def test_register_requires_legal_acceptance(api_client):
    url = reverse("auth-register")
    data = {
        "email": "new@example.com",
        "password": "SecurePass123",
        "language": "ro",
        "accepted_terms": True,
        "accepted_privacy": False,
        "accepted_ai_usage": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_duplicate_email(api_client, user):
    url = reverse("auth-register")
    data = {
        "email": user.email,
        "password": "SecurePass123",
        "accepted_terms": True,
        "accepted_privacy": True,
        "accepted_ai_usage": True,
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_success(api_client, user):
    url = reverse("auth-login")
    response = api_client.post(url, {"email": user.email, "password": "testpass123"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert response.data["user"]["email"] == user.email
    assert "refresh" not in response.data

    access_cookie = response.cookies.get("doisense_access")
    refresh_cookie = response.cookies.get("doisense_refresh")
    assert access_cookie is not None
    assert refresh_cookie is not None
    assert access_cookie["httponly"]
    assert refresh_cookie["httponly"]


@pytest.mark.django_db
def test_login_invalid_password(api_client, user):
    url = reverse("auth-login")
    response = api_client.post(url, {"email": user.email, "password": "wrong"}, format="json")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    url = reverse("me")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_success(authenticated_client, user):
    url = reverse("me")
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["email"] == user.email


@pytest.mark.django_db
def test_me_patch_updates_onboarding_completed(authenticated_client, user):
    user.onboarding_completed = False
    user.save(update_fields=["onboarding_completed"])

    response = authenticated_client.patch(
        reverse("me"),
        {"onboarding_completed": True},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.onboarding_completed is True
    assert response.data["onboarding_completed"] is True


@pytest.mark.django_db
def test_social_login_google_creates_user(api_client, monkeypatch):
    url = reverse("auth-social-login")

    def _mock_verify(_token):
        return {"email": "google.user@example.com"}

    monkeypatch.setattr(SocialLoginView, "_verify_google_token", staticmethod(_mock_verify))
    response = api_client.post(
        url,
        {
            "provider": "google",
            "id_token": "dummy",
            "language": "ro",
            "accepted_terms": True,
            "accepted_privacy": True,
            "accepted_ai_usage": True,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["user"]["email"] == "google.user@example.com"
    assert "access" in response.data
    assert "refresh" not in response.data
    assert response.cookies.get("doisense_access") is not None
    assert response.cookies.get("doisense_refresh") is not None


@pytest.mark.django_db
def test_refresh_uses_cookie_without_request_body(api_client, user):
    login_response = api_client.post(
        reverse("auth-login"),
        {"email": user.email, "password": "testpass123"},
        format="json",
    )
    assert login_response.status_code == status.HTTP_200_OK

    refresh_response = api_client.post(reverse("auth-refresh"), {}, format="json")
    assert refresh_response.status_code == status.HTTP_200_OK
    assert "access" in refresh_response.data
    assert refresh_response.cookies.get("doisense_access") is not None


@pytest.mark.django_db
def test_logout_clears_auth_cookies(api_client, user):
    login_response = api_client.post(
        reverse("auth-login"),
        {"email": user.email, "password": "testpass123"},
        format="json",
    )
    assert login_response.status_code == status.HTTP_200_OK

    response = api_client.post(reverse("auth-logout"), {}, format="json")
    assert response.status_code == status.HTTP_200_OK

    access_cookie = response.cookies.get("doisense_access")
    refresh_cookie = response.cookies.get("doisense_refresh")
    assert access_cookie is not None
    assert refresh_cookie is not None
    assert access_cookie["max-age"] == 0
    assert refresh_cookie["max-age"] == 0


@pytest.mark.django_db
def test_login_uses_configured_cookie_names_and_attributes(api_client, user, settings):
    settings.JWT_ACCESS_COOKIE_NAME = "custom_access_cookie"
    settings.JWT_REFRESH_COOKIE_NAME = "custom_refresh_cookie"
    settings.JWT_COOKIE_SAMESITE = "Strict"
    settings.SESSION_COOKIE_SECURE = True

    response = api_client.post(
        reverse("auth-login"),
        {"email": user.email, "password": "testpass123"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK

    access_cookie = response.cookies.get("custom_access_cookie")
    refresh_cookie = response.cookies.get("custom_refresh_cookie")
    assert access_cookie is not None
    assert refresh_cookie is not None
    assert access_cookie["samesite"] == "Strict"
    assert refresh_cookie["samesite"] == "Strict"
    assert access_cookie["secure"]
    assert refresh_cookie["secure"]


@pytest.mark.django_db
def test_refresh_invalid_cookie_clears_auth_cookies(api_client, settings):
    settings.JWT_ACCESS_COOKIE_NAME = "doisense_access"
    settings.JWT_REFRESH_COOKIE_NAME = "doisense_refresh"

    api_client.cookies["doisense_refresh"] = "invalid-token"
    response = api_client.post(reverse("auth-refresh"), {}, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    access_cookie = response.cookies.get("doisense_access")
    refresh_cookie = response.cookies.get("doisense_refresh")
    assert access_cookie is not None
    assert refresh_cookie is not None
    assert access_cookie["max-age"] == 0
    assert refresh_cookie["max-age"] == 0


@pytest.mark.django_db
def test_social_login_requires_legal_acceptance_for_new_accounts(api_client, monkeypatch):
    url = reverse("auth-social-login")

    def _mock_verify(_token):
        return {"email": "missing.consent@example.com"}

    monkeypatch.setattr(SocialLoginView, "_verify_google_token", staticmethod(_mock_verify))
    response = api_client.post(
        url,
        {"provider": "google", "id_token": "dummy", "language": "ro"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_social_login_invalid_token(api_client, monkeypatch):
    url = reverse("auth-social-login")

    def _mock_verify(_token):
        raise ValueError("invalid")

    monkeypatch.setattr(SocialLoginView, "_verify_google_token", staticmethod(_mock_verify))
    response = api_client.post(
        url,
        {"provider": "google", "id_token": "dummy", "language": "en"},
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_export_returns_personal_data(authenticated_client, user, journal_question):
    from ai.models import Conversation
    from core.models import UserWellbeingCheckin
    from journal.models import JournalEntry

    JournalEntry.objects.create(
        user=user,
        question=journal_question,
        content="Journal export content",
        emotions=["steady"],
    )
    Conversation.objects.create(
        user=user,
        module="wellness",
        plan_tier="trial",
        user_message="Export my data",
        ai_response="Here is a summary.",
    )
    UserWellbeingCheckin.objects.create(user=user, mood="good", energy_level=8)

    response = authenticated_client.get(reverse("me-export"))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user"]["email"] == user.email
    assert len(response.json()["journal_entries"]) == 1
    assert len(response.json()["conversations"]) == 1
    assert len(response.json()["wellbeing_checkins"]) == 1
