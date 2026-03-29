import pytest
from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory

from ai_core.admin import SocialMediaPostAdmin
from ai_core.models import SocialMediaPost


@pytest.fixture
def staff_user(db):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create_user(email="admin@example.com", password="testpass123", language="en")
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture
def admin_request(staff_user):
    request = RequestFactory().post("/admin/ai_core/socialmediapost/")
    request.user = staff_user

    session_middleware = SessionMiddleware(lambda req: None)
    session_middleware.process_request(request)
    request.session.save()

    messages = FallbackStorage(request)
    setattr(request, "_messages", messages)
    return request


@pytest.mark.django_db
def test_admin_action_publish_instagram_calls_instagram_publisher(monkeypatch, admin_request):
    post = SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_INSTAGRAM,
        title="Morning Walk",
        body="Take a 10-minute walk.",
        wellness_topic="movement",
    )

    calls = {"count": 0}

    def _fake_publisher(obj):
        calls["count"] += 1
        assert obj.pk == post.pk
        return True, "ok"

    monkeypatch.setattr("ai_core.admin.publish_to_instagram", _fake_publisher)

    model_admin = SocialMediaPostAdmin(SocialMediaPost, admin.site)
    queryset = SocialMediaPost.objects.filter(pk=post.pk)
    model_admin.publish_selected_to_instagram(admin_request, queryset)

    assert calls["count"] == 1


@pytest.mark.django_db
def test_admin_action_publish_tiktok_calls_tiktok_publisher(monkeypatch, admin_request):
    post = SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_TIKTOK,
        title="Posture Break",
        body="Relax your shoulders.",
        wellness_topic="stress",
    )

    calls = {"count": 0}

    def _fake_publisher(obj):
        calls["count"] += 1
        assert obj.pk == post.pk
        return True, "ok"

    monkeypatch.setattr("ai_core.admin.publish_to_tiktok", _fake_publisher)

    model_admin = SocialMediaPostAdmin(SocialMediaPost, admin.site)
    queryset = SocialMediaPost.objects.filter(pk=post.pk)
    model_admin.publish_selected_to_tiktok(admin_request, queryset)

    assert calls["count"] == 1


@pytest.mark.django_db
def test_admin_action_publish_linkedin_calls_linkedin_publisher(monkeypatch, admin_request):
    post = SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_LINKEDIN,
        title="Mindful Leadership",
        body="Model healthy boundaries.",
        wellness_topic="workplace wellbeing",
    )

    calls = {"count": 0}

    def _fake_publisher(obj):
        calls["count"] += 1
        assert obj.pk == post.pk
        return True, "ok"

    monkeypatch.setattr("ai_core.admin.publish_to_linkedin", _fake_publisher)

    model_admin = SocialMediaPostAdmin(SocialMediaPost, admin.site)
    queryset = SocialMediaPost.objects.filter(pk=post.pk)
    model_admin.publish_selected_to_linkedin(admin_request, queryset)

    assert calls["count"] == 1


@pytest.mark.django_db
def test_admin_action_skips_posts_with_different_platform(monkeypatch, admin_request):
    post = SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_LINKEDIN,
        title="Hydration at Desk",
        body="Keep water visible.",
        wellness_topic="hydration",
    )

    calls = {"count": 0}

    def _fake_publisher(obj):
        calls["count"] += 1
        return True, "ok"

    monkeypatch.setattr("ai_core.admin.publish_to_instagram", _fake_publisher)

    model_admin = SocialMediaPostAdmin(SocialMediaPost, admin.site)
    queryset = SocialMediaPost.objects.filter(pk=post.pk)
    model_admin.publish_selected_to_instagram(admin_request, queryset)

    post.refresh_from_db()
    assert calls["count"] == 0
    assert "Skipped publish action" in post.publish_log
