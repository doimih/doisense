import types
from urllib import error

import pytest

from ai_core.models import SocialMediaPost, SocialMediaSettings
from ai_core.publish_instagram import publish_to_instagram
from ai_core.publish_linkedin import publish_to_linkedin
from ai_core.publish_tiktok import publish_to_tiktok


class _DummyResponse:
    def __init__(self, payload: str):
        self._payload = payload.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._payload


class _DummyErrorBody:
    def __init__(self, payload: str):
        self._payload = payload.encode("utf-8")

    def read(self):
        return self._payload

    def close(self):
        return None


@pytest.fixture
def base_post(db):
    return SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_INSTAGRAM,
        title="Hydration Habit",
        body="Drink water after waking up.",
        hashtags="#Wellness",
        image_url="https://example.com/media.png",
        wellness_topic="hydration",
    )


@pytest.mark.django_db
def test_publish_instagram_success_updates_status_and_log(monkeypatch, base_post):
    SocialMediaSettings.load()
    settings_obj = SocialMediaSettings.load()
    settings_obj.instagram_access_token = "instagram-token-very-long"
    settings_obj.instagram_business_account_id = "business-id"
    settings_obj.save()

    monkeypatch.setattr(
        "ai_core.publish_instagram.request.urlopen",
        lambda req, timeout=0: _DummyResponse('{"id":"media-123"}'),
    )

    ok, message = publish_to_instagram(base_post)
    base_post.refresh_from_db()

    assert ok is True
    assert "Published to Instagram successfully" in message
    assert base_post.status == SocialMediaPost.STATUS_POSTED
    assert base_post.posted_at is not None
    assert "accepted" in base_post.publish_log.lower()


@pytest.mark.django_db
def test_publish_tiktok_success_updates_status_and_log(monkeypatch):
    settings_obj = SocialMediaSettings.load()
    settings_obj.tiktok_app_id = "tt-app"
    settings_obj.tiktok_access_token = "tiktok-token-very-long"
    settings_obj.save()

    post = SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_TIKTOK,
        title="Desk Stretch",
        body="Stretch your neck every hour.",
        hashtags="#Wellness",
        image_url="https://example.com/video.mp4",
        wellness_topic="movement",
    )

    monkeypatch.setattr(
        "ai_core.publish_tiktok.request.urlopen",
        lambda req, timeout=0: _DummyResponse('{"data":{"publish_id":"p-1"}}'),
    )

    ok, message = publish_to_tiktok(post)
    post.refresh_from_db()

    assert ok is True
    assert "Published to TikTok successfully" in message
    assert post.status == SocialMediaPost.STATUS_POSTED
    assert post.posted_at is not None
    assert "accepted" in post.publish_log.lower()


@pytest.mark.django_db
def test_publish_linkedin_success_updates_status_and_log(monkeypatch):
    settings_obj = SocialMediaSettings.load()
    settings_obj.linkedin_access_token = "linkedin-token-very-long"
    settings_obj.linkedin_organization_id = "123456"
    settings_obj.save()

    post = SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_LINKEDIN,
        title="Boundary Setting",
        body="Protect focus with clear calendar boundaries.",
        hashtags="#WorkplaceWellness",
        image_url="https://example.com/image.png",
        wellness_topic="stress management",
    )

    monkeypatch.setattr(
        "ai_core.publish_linkedin.request.urlopen",
        lambda req, timeout=0: _DummyResponse('{"id":"ugc-1"}'),
    )

    ok, message = publish_to_linkedin(post)
    post.refresh_from_db()

    assert ok is True
    assert "Published to LinkedIn successfully" in message
    assert post.status == SocialMediaPost.STATUS_POSTED
    assert post.posted_at is not None
    assert "accepted" in post.publish_log.lower()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "publisher_path,platform,settings_updates,expected_fragment",
    [
        (
            "ai_core.publish_instagram.publish_to_instagram",
            SocialMediaPost.PLATFORM_INSTAGRAM,
            {},
            "instagram settings are incomplete",
        ),
        (
            "ai_core.publish_tiktok.publish_to_tiktok",
            SocialMediaPost.PLATFORM_TIKTOK,
            {"tiktok_app_id": "tt-app"},
            "tiktok settings are incomplete",
        ),
        (
            "ai_core.publish_linkedin.publish_to_linkedin",
            SocialMediaPost.PLATFORM_LINKEDIN,
            {},
            "linkedin settings are incomplete",
        ),
    ],
)
def test_publish_fails_when_required_settings_missing(publisher_path, platform, settings_updates, expected_fragment):
    settings_obj = SocialMediaSettings.load()
    for key, value in settings_updates.items():
        setattr(settings_obj, key, value)
    settings_obj.save()

    post = SocialMediaPost.objects.create(
        platform=platform,
        title="Test",
        body="Body",
        hashtags="#x",
        image_url="https://example.com/img.png",
        wellness_topic="wellness",
    )

    module_name, fn_name = publisher_path.rsplit(".", 1)
    module = __import__(module_name, fromlist=[fn_name])
    publisher = getattr(module, fn_name)

    ok, message = publisher(post)
    post.refresh_from_db()

    assert ok is False
    assert expected_fragment in message.lower()
    assert post.status == SocialMediaPost.STATUS_DRAFT


@pytest.mark.django_db
def test_publish_fails_with_invalid_token_instagram(base_post):
    settings_obj = SocialMediaSettings.load()
    settings_obj.instagram_access_token = "short"
    settings_obj.instagram_business_account_id = "business-id"
    settings_obj.save()

    ok, message = publish_to_instagram(base_post)
    base_post.refresh_from_db()

    assert ok is False
    assert "invalid" in message.lower()
    assert base_post.status == SocialMediaPost.STATUS_DRAFT


@pytest.mark.django_db
def test_publish_fails_on_instagram_http_error(monkeypatch, base_post):
    settings_obj = SocialMediaSettings.load()
    settings_obj.instagram_access_token = "instagram-token-very-long"
    settings_obj.instagram_business_account_id = "business-id"
    settings_obj.save()

    class _HTTPErrorWithBody(error.HTTPError):
        def __init__(self):
            super().__init__(
                url="https://graph.facebook.com",
                code=400,
                msg="Bad Request",
                hdrs=None,
                fp=_DummyErrorBody('{"error":"invalid"}'),
            )

    def _raise_http_error(req, timeout=0):
        raise _HTTPErrorWithBody()

    monkeypatch.setattr("ai_core.publish_instagram.request.urlopen", _raise_http_error)

    ok, message = publish_to_instagram(base_post)
    base_post.refresh_from_db()

    assert ok is False
    assert "api error" in message.lower()
    assert base_post.status == SocialMediaPost.STATUS_DRAFT
    assert "api error" in base_post.publish_log.lower()
