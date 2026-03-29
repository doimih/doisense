import pytest

from ai_core.models import Prompt, SocialMediaPost
from ai_core.social_media import generate_social_post, save_generated_post


@pytest.mark.django_db
def test_generate_social_post_enforces_wellness_only_for_non_wellness_topic():
    post = generate_social_post(topic="football tactics", platform=SocialMediaPost.PLATFORM_INSTAGRAM)

    assert post["wellness_topic"].lower().startswith("wellness practice:")
    assert "instagram" in post["closing_line"].lower()
    assert post["body"].endswith(post["closing_line"])


@pytest.mark.django_db
def test_generate_social_post_platform_adapted_tone_and_closing_line():
    insta = generate_social_post("mindfulness", SocialMediaPost.PLATFORM_INSTAGRAM)
    tiktok = generate_social_post("mindfulness", SocialMediaPost.PLATFORM_TIKTOK)
    linkedin = generate_social_post("mindfulness", SocialMediaPost.PLATFORM_LINKEDIN)

    assert "visual-first" in insta["body"]
    assert "Instagram" in insta["closing_line"]

    assert "trend-aware" in tiktok["body"]
    assert "TikTok" in tiktok["closing_line"]

    assert "professional" in linkedin["body"]
    assert "LinkedIn" in linkedin["closing_line"]


@pytest.mark.django_db
def test_generate_social_post_uses_rules_prompt_from_db_when_present():
    Prompt.objects.create(
        name="social_media_global_wellness_rules_test",
        type=Prompt.TYPE_RULES,
        content="Wellness content only. Always mention platform in closing.",
        language="en",
    )

    post = generate_social_post("sleep hygiene", SocialMediaPost.PLATFORM_LINKEDIN)

    assert "Wellness content only" in post["rules_applied"]


@pytest.mark.django_db
def test_save_generated_post_creates_social_media_post_record():
    data = {
        "platform": SocialMediaPost.PLATFORM_TIKTOK,
        "title": "Evening Wind Down",
        "body": "Lower stimulation 30 minutes before bed.",
        "hashtags": "#Wellness #Sleep",
        "image_url": "https://example.com/image.png",
        "wellness_topic": "sleep",
        "status": SocialMediaPost.STATUS_DRAFT,
        "publish_log": "Saved from generator.",
    }

    created = save_generated_post(data)

    assert SocialMediaPost.objects.count() == 1
    assert created.platform == SocialMediaPost.PLATFORM_TIKTOK
    assert created.title == "Evening Wind Down"
    assert created.hashtags == "#Wellness #Sleep"
    assert created.image_url == "https://example.com/image.png"
    assert created.publish_log == "Saved from generator."
