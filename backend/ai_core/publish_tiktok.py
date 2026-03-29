from __future__ import annotations

import json
from urllib import error, request

from django.utils import timezone

from .models import SocialMediaPost, SocialMediaSettings


def _append_log(post: SocialMediaPost, message: str) -> None:
    timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    post.publish_log = f"{post.publish_log}\n[{timestamp}] {message}".strip()


def _decode_json(payload: str) -> dict:
    try:
        return json.loads(payload or "{}")
    except (TypeError, json.JSONDecodeError):
        return {}


def _looks_like_video_url(url: str) -> bool:
    lowered = (url or "").lower()
    return lowered.startswith(("http://", "https://")) and any(
        ext in lowered for ext in (".mp4", ".mov", ".webm", ".m4v")
    )


def publish_to_tiktok(post: SocialMediaPost) -> tuple[bool, str]:
    settings_obj = SocialMediaSettings.load()

    if not settings_obj.tiktok_access_token or not settings_obj.tiktok_app_id:
        message = "TikTok settings are incomplete: missing app id or access token."
        _append_log(post, message)
        post.save(update_fields=["publish_log"])
        return False, message

    if len(settings_obj.tiktok_access_token.strip()) < 10:
        message = "TikTok access token appears invalid (too short)."
        _append_log(post, message)
        post.save(update_fields=["publish_log"])
        return False, message

    video_source = (post.video_url or post.image_url or "").strip()

    if not _looks_like_video_url(video_source):
        message = "TikTok publish requires a valid public video URL (mp4/mov/webm/m4v)."
        _append_log(post, message)
        post.save(update_fields=["publish_log"])
        return False, message

    endpoint = "https://open.tiktokapis.com/v2/post/publish/content/init/"
    payload = {
        "post_info": {
            "title": post.title,
            "description": f"{post.body}\n\n{post.hashtags}".strip(),
            "privacy_level": "PUBLIC_TO_EVERYONE",
        },
        "source_info": {
            "source": "PULL_FROM_URL",
            "video_url": video_source,
        },
    }

    try:
        req = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings_obj.tiktok_access_token}",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")

        parsed = _decode_json(body)
        publish_id = str(parsed.get("data", {}).get("publish_id") or "").strip()
        if not publish_id:
            message = f"TikTok publish response missing publish_id. Response: {body[:500]}"
            _append_log(post, message)
            post.save(update_fields=["publish_log"])
            return False, message

        _append_log(post, f"TikTok publish request accepted. publish_id={publish_id}")
        post.status = SocialMediaPost.STATUS_POSTED
        post.posted_at = timezone.now()
        post.save(update_fields=["status", "posted_at", "publish_log"])
        return True, "Published to TikTok successfully."
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
        message = f"TikTok API error {exc.code}: {body[:500]}"
    except Exception as exc:  # pragma: no cover
        message = f"TikTok publish failed: {exc}"

    _append_log(post, message)
    post.save(update_fields=["publish_log"])
    return False, message
