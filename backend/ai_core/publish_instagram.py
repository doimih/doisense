from __future__ import annotations

import json
from urllib import error, request
from urllib.parse import urlencode

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


def publish_to_instagram(post: SocialMediaPost) -> tuple[bool, str]:
    settings_obj = SocialMediaSettings.load()

    if not settings_obj.instagram_access_token or not settings_obj.instagram_business_account_id:
        message = "Instagram settings are incomplete: missing access token or business account id."
        _append_log(post, message)
        post.save(update_fields=["publish_log"])
        return False, message

    if len(settings_obj.instagram_access_token.strip()) < 10:
        message = "Instagram access token appears invalid (too short)."
        _append_log(post, message)
        post.save(update_fields=["publish_log"])
        return False, message

    if not (post.image_url or "").strip().lower().startswith(("http://", "https://")):
        message = "Instagram publish requires a valid public image URL."
        _append_log(post, message)
        post.save(update_fields=["publish_log"])
        return False, message

    endpoint = (
        f"https://graph.facebook.com/v20.0/"
        f"{settings_obj.instagram_business_account_id}/media"
    )
    payload = {
        "caption": f"{post.title}\n\n{post.body}\n\n{post.hashtags}".strip(),
        "image_url": post.image_url,
        "access_token": settings_obj.instagram_access_token,
    }

    try:
        # Step 1: create media container.
        req = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")

        create_payload = _decode_json(body)
        creation_id = str(create_payload.get("id") or "").strip()
        if not creation_id:
            message = f"Instagram media creation did not return an id. Response: {body[:500]}"
            _append_log(post, message)
            post.save(update_fields=["publish_log"])
            return False, message

        # Step 2: publish media container.
        publish_endpoint = (
            f"https://graph.facebook.com/v20.0/"
            f"{settings_obj.instagram_business_account_id}/media_publish"
        )
        publish_data = urlencode(
            {
                "creation_id": creation_id,
                "access_token": settings_obj.instagram_access_token,
            }
        ).encode("utf-8")
        publish_req = request.Request(
            publish_endpoint,
            data=publish_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with request.urlopen(publish_req, timeout=15) as publish_resp:
            publish_body = publish_resp.read().decode("utf-8")

        _append_log(post, f"Instagram media published. Response: {publish_body[:500]}")
        post.status = SocialMediaPost.STATUS_POSTED
        post.posted_at = timezone.now()
        post.save(update_fields=["status", "posted_at", "publish_log"])
        return True, "Published to Instagram successfully."
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
        message = f"Instagram API error {exc.code}: {body[:500]}"
    except Exception as exc:  # pragma: no cover
        message = f"Instagram publish failed: {exc}"

    _append_log(post, message)
    post.save(update_fields=["publish_log"])
    return False, message
