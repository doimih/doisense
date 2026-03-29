import pytest
from django.utils import timezone

from ai_core.models import SocialMediaPost, SocialMediaSettings


@pytest.mark.django_db
def test_social_media_post_creation_defaults():
    post = SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_INSTAGRAM,
        title="Morning Breathwork",
        body="Try 2 minutes of breathing before work.",
        wellness_topic="breathwork",
    )

    assert post.status == SocialMediaPost.STATUS_DRAFT
    assert post.hashtags == ""
    assert post.image_url == ""
    assert post.owner == SocialMediaPost.OWNER_DOISENSE
    assert post.publish_log == ""
    assert post.created_at is not None
    assert post.posted_at is None


@pytest.mark.django_db
def test_social_media_post_status_transition_to_posted():
    post = SocialMediaPost.objects.create(
        platform=SocialMediaPost.PLATFORM_LINKEDIN,
        title="Workday Reset",
        body="Take a mindful pause between meetings.",
        wellness_topic="mindfulness",
    )

    post.status = SocialMediaPost.STATUS_POSTED
    post.posted_at = timezone.now()
    post.publish_log = "Posted successfully"
    post.save(update_fields=["status", "posted_at", "publish_log"])
    post.refresh_from_db()

    assert post.status == SocialMediaPost.STATUS_POSTED
    assert post.posted_at is not None
    assert "Posted successfully" in post.publish_log


@pytest.mark.django_db
def test_social_media_settings_singleton_save_behavior():
    first = SocialMediaSettings(
        instagram_app_id="app-1",
        instagram_access_token="token-1-very-long",
    )
    first.save()

    second = SocialMediaSettings(
        instagram_app_id="app-2",
        instagram_access_token="token-2-very-long",
    )
    second.save()

    assert SocialMediaSettings.objects.count() == 1
    singleton = SocialMediaSettings.objects.get(pk=1)
    assert singleton.instagram_app_id == "app-2"
    assert singleton.instagram_access_token == "token-2-very-long"


@pytest.mark.django_db
def test_social_media_settings_load_returns_singleton():
    loaded = SocialMediaSettings.load()
    assert loaded.pk == 1
    assert SocialMediaSettings.objects.count() == 1

    loaded.instagram_app_secret = "secret-updated"
    loaded.save()

    loaded_again = SocialMediaSettings.load()
    assert loaded_again.pk == 1
    assert loaded_again.instagram_app_secret == "secret-updated"
