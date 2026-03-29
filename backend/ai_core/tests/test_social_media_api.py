import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from ai_core.models import SocialMediaPost


User = get_user_model()


@pytest.fixture
def staff_client(db):
    user = User.objects.create_user(
        email="staff@example.com",
        password="testpass123",
        language="en",
        is_staff=True,
    )
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        email="staff-owner@example.com",
        password="testpass123",
        language="en",
        is_staff=True,
    )


@pytest.fixture
def other_staff_user(db):
    return User.objects.create_user(
        email="staff-other@example.com",
        password="testpass123",
        language="en",
        is_staff=True,
    )


@pytest.mark.django_db
def test_social_posts_list_returns_items(staff_user):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_INSTAGRAM,
        title="Morning reset",
        body="Take a slow breath.",
        owner_user=staff_user,
        wellness_topic="mindfulness",
    )

    SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_INSTAGRAM,
        title="Other owner post",
        body="Hidden due to ownership.",
        wellness_topic="mindfulness",
    )

    response = client.get("/api/social/posts/")

    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
    assert len(payload["items"]) == 1
    assert payload["items"][0]["title"] == "Morning reset"


@pytest.mark.django_db
def test_social_generate_creates_draft(staff_client):
    response = staff_client.post(
        "/api/social/generate/",
        {"platform": "instagram", "topic": "stress relief"},
        format="json",
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["post"]["status"] == SocialMediaPost.STATUS_DRAFT
    assert payload["post"]["platform"] == SocialMediaPost.PLATFORM_INSTAGRAM
    assert payload["post"]["owner"] == SocialMediaPost.OWNER_DOISENSE
    assert payload["post"]["owner_user_id"] is not None
    assert SocialMediaPost.objects.count() == 1


@pytest.mark.django_db
def test_social_publish_rejects_platform_mismatch(staff_user):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    post = SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_LINKEDIN,
        title="Focus block",
        body="Protect deep work.",
        owner_user=staff_user,
        wellness_topic="focus",
    )

    response = client.post(
        "/api/social/publish/",
        {"post_id": post.pk, "platform": "instagram"},
        format="json",
    )

    assert response.status_code == 409
    payload = response.json()
    assert "does not match" in payload["detail"].lower()


@pytest.mark.django_db
def test_social_publish_calls_platform_publisher(monkeypatch, staff_user):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    post = SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_LINKEDIN,
        title="Boundaries",
        body="Set realistic meeting limits.",
        owner_user=staff_user,
        wellness_topic="workplace wellbeing",
    )

    calls = {"count": 0}

    def _fake_publisher(obj):
        calls["count"] += 1
        obj.status = SocialMediaPost.STATUS_POSTED
        obj.save(update_fields=["status"])
        return True, "Published"

    monkeypatch.setattr("ai_core.api_views.publish_to_linkedin", _fake_publisher)

    response = client.post(
        "/api/social/publish/",
        {"post_id": post.pk, "platform": "linkedin"},
        format="json",
    )

    assert response.status_code == 200
    assert calls["count"] == 1
    post.refresh_from_db()
    assert post.status == SocialMediaPost.STATUS_POSTED


@pytest.mark.django_db
def test_social_endpoints_forbidden_for_non_staff(authenticated_client):
    response = authenticated_client.get("/api/social/posts/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_social_publish_forbidden_for_foreign_owner(staff_user, other_staff_user):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    foreign_post = SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_LINKEDIN,
        title="Foreign post",
        body="This post is owned by another staff user.",
        owner_user=other_staff_user,
        wellness_topic="boundaries",
    )

    response = client.post(
        "/api/social/publish/",
        {"post_id": foreign_post.pk, "platform": "linkedin"},
        format="json",
    )

    assert response.status_code == 403
