import pytest
from users.views import SocialLoginView
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_register_success(api_client):
    url = reverse("auth-register")
    data = {"email": "new@example.com", "password": "SecurePass123", "language": "ro"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert "access" in response.data
    assert "refresh" in response.data
    assert response.data["user"]["email"] == "new@example.com"


@pytest.mark.django_db
def test_register_duplicate_email(api_client, user):
    url = reverse("auth-register")
    data = {"email": user.email, "password": "SecurePass123"}
    response = api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_success(api_client, user):
    url = reverse("auth-login")
    response = api_client.post(
        url, {"email": user.email, "password": "testpass123"}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert response.data["user"]["email"] == user.email


@pytest.mark.django_db
def test_login_invalid_password(api_client, user):
    url = reverse("auth-login")
    response = api_client.post(
        url, {"email": user.email, "password": "wrong"}, format="json"
    )
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
def test_social_login_google_creates_user(api_client, monkeypatch):
    url = reverse("auth-social-login")

    def _mock_verify(_token):
        return {"email": "google.user@example.com"}

    monkeypatch.setattr(SocialLoginView, "_verify_google_token", staticmethod(_mock_verify))
    response = api_client.post(
        url,
        {"provider": "google", "id_token": "dummy", "language": "ro"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["user"]["email"] == "google.user@example.com"
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_social_login_apple_existing_user(api_client, user, monkeypatch):
    url = reverse("auth-social-login")

    def _mock_verify(_token):
        return {"email": user.email}

    monkeypatch.setattr(SocialLoginView, "_verify_apple_token", staticmethod(_mock_verify))
    response = api_client.post(
        url,
        {"provider": "apple", "id_token": "dummy", "language": "en"},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["user"]["email"] == user.email


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
