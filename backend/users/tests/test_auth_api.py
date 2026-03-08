import pytest
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
