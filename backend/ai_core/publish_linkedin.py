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


def publish_to_linkedin(post: SocialMediaPost) -> tuple[bool, str]:
    settings_obj = SocialMediaSettings.load()

    if not settings_obj.linkedin_access_token or not settings_obj.linkedin_organization_id:
        message = "LinkedIn settings are incomplete: missing access token or organization id."
        _append_log(post, message)
        post.save(update_fields=["publish_log"])
        return False, message

    if len(settings_obj.linkedin_access_token.strip()) < 10:
        message = "LinkedIn access token appears invalid (too short)."
        _append_log(post, message)
        post.save(update_fields=["publish_log"])
        return False, message

    endpoint = "https://api.linkedin.com/v2/ugcPosts"
    payload = {
        "author": f"urn:li:organization:{settings_obj.linkedin_organization_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": f"{post.title}\n\n{post.body}\n\n{post.hashtags}".strip()
                },
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    try:
        req = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings_obj.linkedin_access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")

            status_code = int(getattr(resp, "status", 0) or resp.getcode() or 0)
            restli_id = (resp.headers.get("x-restli-id") or "").strip()

        parsed = _decode_json(body)
        ugc_id = str(parsed.get("id") or restli_id).strip()
        if status_code not in {200, 201} or not ugc_id:
            message = (
                f"LinkedIn publish response could not be confirmed "
                f"(status={status_code}, id={ugc_id or 'missing'}). Response: {body[:500]}"
            )
            _append_log(post, message)
            post.save(update_fields=["publish_log"])
            return False, message

        _append_log(post, f"LinkedIn publish request accepted. ugc_id={ugc_id}")
        post.status = SocialMediaPost.STATUS_POSTED
        post.posted_at = timezone.now()
        post.save(update_fields=["status", "posted_at", "publish_log"])
        return True, "Published to LinkedIn successfully."
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
        message = f"LinkedIn API error {exc.code}: {body[:500]}"
    except Exception as exc:  # pragma: no cover
        message = f"LinkedIn publish failed: {exc}"

    _append_log(post, message)
    post.save(update_fields=["publish_log"])
    return False, message
