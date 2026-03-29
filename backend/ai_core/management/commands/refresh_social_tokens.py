"""
Management command: refresh_social_tokens

Checks Instagram and LinkedIn OAuth token expiry and refreshes tokens
that are within the warning window. Sends in-app notifications to admin
users when tokens are expiring or have been refreshed.

Usage:
    python manage.py refresh_social_tokens [--dry-run] [--warn-days N]
"""
from __future__ import annotations

import json
import logging
from datetime import timedelta
from urllib import error, request as urllib_request
from urllib.parse import urlencode

from django.core.management.base import BaseCommand
from django.utils import timezone

from ai_core.models import SocialMediaSettings

logger = logging.getLogger(__name__)

_WARN_DAYS_DEFAULT = 7  # Notify/refresh when token expires within this many days


class Command(BaseCommand):
    help = "Refresh expiring Instagram and LinkedIn OAuth tokens."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Check token expiry and log results without making API calls or saving changes.",
        )
        parser.add_argument(
            "--warn-days",
            type=int,
            default=_WARN_DAYS_DEFAULT,
            help=f"Number of days before expiry to trigger a refresh (default: {_WARN_DAYS_DEFAULT}).",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        warn_days: int = options["warn_days"]
        now = timezone.now()
        warn_threshold = now + timedelta(days=warn_days)

        settings_obj = SocialMediaSettings.load()
        changed = False

        # --- Instagram ---
        ig_expires = settings_obj.instagram_token_expires_at
        ig_token = (settings_obj.instagram_access_token or "").strip()
        ig_app_id = (settings_obj.instagram_app_id or "").strip()
        ig_app_secret = (settings_obj.instagram_app_secret or "").strip()

        if not ig_token:
            self.stdout.write("Instagram: no access token configured — skipping.")
        elif ig_expires and ig_expires <= now:
            self._notify_admin("instagram", "expired", ig_expires)
            self.stdout.write(self.style.WARNING(
                f"Instagram token EXPIRED at {ig_expires}. Manual re-authentication required."
            ))
        elif ig_expires and ig_expires <= warn_threshold:
            self.stdout.write(self.style.WARNING(
                f"Instagram token expires at {ig_expires} (within {warn_days} days). Attempting refresh..."
            ))
            if not dry_run and ig_app_id and ig_app_secret:
                new_token, new_expiry = _refresh_instagram_token(ig_token, ig_app_id, ig_app_secret)
                if new_token:
                    settings_obj.instagram_access_token = new_token
                    settings_obj.instagram_token_expires_at = new_expiry
                    changed = True
                    self._notify_admin("instagram", "refreshed", new_expiry)
                    self.stdout.write(self.style.SUCCESS(
                        f"Instagram token refreshed. New expiry: {new_expiry}"
                    ))
                else:
                    self._notify_admin("instagram", "refresh_failed", ig_expires)
                    self.stdout.write(self.style.ERROR(
                        "Instagram token refresh FAILED. Manual re-authentication required."
                    ))
            elif dry_run:
                self.stdout.write("[dry-run] Would attempt Instagram token refresh.")
            else:
                self.stdout.write(self.style.WARNING(
                    "Instagram app_id or app_secret not configured — cannot refresh automatically."
                ))
        elif ig_expires:
            self.stdout.write(f"Instagram token valid until {ig_expires}.")
        else:
            self.stdout.write("Instagram: token_expires_at not set. Set it after first authentication.")

        # --- LinkedIn ---
        li_expires = settings_obj.linkedin_token_expires_at
        li_token = (settings_obj.linkedin_access_token or "").strip()
        li_refresh = (settings_obj.linkedin_refresh_token or "").strip()
        li_client_id = (settings_obj.linkedin_client_id or "").strip()
        li_client_secret = (settings_obj.linkedin_client_secret or "").strip()

        if not li_token:
            self.stdout.write("LinkedIn: no access token configured — skipping.")
        elif li_expires and li_expires <= now:
            self._notify_admin("linkedin", "expired", li_expires)
            self.stdout.write(self.style.WARNING(
                f"LinkedIn token EXPIRED at {li_expires}. Manual re-authentication required."
            ))
        elif li_expires and li_expires <= warn_threshold:
            self.stdout.write(self.style.WARNING(
                f"LinkedIn token expires at {li_expires} (within {warn_days} days). Attempting refresh..."
            ))
            if not dry_run and li_refresh and li_client_id and li_client_secret:
                new_token, new_refresh, new_expiry = _refresh_linkedin_token(
                    li_refresh, li_client_id, li_client_secret
                )
                if new_token:
                    settings_obj.linkedin_access_token = new_token
                    if new_refresh:
                        settings_obj.linkedin_refresh_token = new_refresh
                    settings_obj.linkedin_token_expires_at = new_expiry
                    changed = True
                    self._notify_admin("linkedin", "refreshed", new_expiry)
                    self.stdout.write(self.style.SUCCESS(
                        f"LinkedIn token refreshed. New expiry: {new_expiry}"
                    ))
                else:
                    self._notify_admin("linkedin", "refresh_failed", li_expires)
                    self.stdout.write(self.style.ERROR(
                        "LinkedIn token refresh FAILED. Manual re-authentication required."
                    ))
            elif dry_run:
                self.stdout.write("[dry-run] Would attempt LinkedIn token refresh.")
            else:
                self.stdout.write(self.style.WARNING(
                    "LinkedIn refresh_token, client_id, or client_secret not configured."
                ))
        elif li_expires:
            self.stdout.write(f"LinkedIn token valid until {li_expires}.")
        else:
            self.stdout.write("LinkedIn: token_expires_at not set. Set it after first authentication.")

        if changed and not dry_run:
            settings_obj.save()
            self.stdout.write(self.style.SUCCESS("SocialMediaSettings saved."))

    def _notify_admin(self, platform: str, event: str, expiry) -> None:
        """
        Send an in-app notification to all admin/staff users about a token lifecycle event.
        Silently skips if the notification system is unavailable.
        """
        try:
            from django.contrib.auth import get_user_model
            from core.notifications import create_in_app_notification

            User = get_user_model()
            admins = User.objects.filter(is_staff=True, is_active=True)

            title_map = {
                "refreshed": f"{platform.title()} token refreshed",
                "expired": f"{platform.title()} token EXPIRED",
                "refresh_failed": f"{platform.title()} token refresh failed",
            }
            body_map = {
                "refreshed": f"The {platform.title()} OAuth token was automatically refreshed. New expiry: {expiry}.",
                "expired": f"The {platform.title()} OAuth token has expired. Manual re-authentication is required to restore publishing.",
                "refresh_failed": f"Automatic refresh of the {platform.title()} OAuth token FAILED. Please re-authenticate manually before {expiry}.",
            }
            title = title_map.get(event, f"{platform.title()} token event: {event}")
            body = body_map.get(event, f"Token event: {event}. Expiry: {expiry}.")

            for admin in admins:
                create_in_app_notification(
                    admin,
                    f"social_token_{platform}_{event}",
                    title,
                    body,
                    context_key=f"{platform}:{event}:{expiry}",
                )
        except Exception as exc:
            logger.warning("Failed to send social token notification: %s", exc)


# ---------------------------------------------------------------------------
# Platform-specific refresh helpers
# ---------------------------------------------------------------------------

def _refresh_instagram_token(
    access_token: str, app_id: str, app_secret: str
) -> tuple[str | None, object | None]:
    """
    Refresh a long-lived Instagram/Facebook Graph API token.
    See: https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived/

    Returns (new_access_token, new_expiry_datetime) or (None, None) on failure.
    """
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": access_token,
    }
    url = f"https://graph.facebook.com/v20.0/oauth/access_token?{urlencode(params)}"
    try:
        with urllib_request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        new_token = data.get("access_token")
        expires_in = data.get("expires_in")  # seconds
        if not new_token:
            logger.warning("Instagram refresh response missing access_token: %s", data)
            return None, None
        new_expiry = timezone.now() + timedelta(seconds=int(expires_in)) if expires_in else None
        return new_token, new_expiry
    except (error.URLError, error.HTTPError, json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.warning("Instagram token refresh request failed: %s", exc)
        return None, None


def _refresh_linkedin_token(
    refresh_token: str, client_id: str, client_secret: str
) -> tuple[str | None, str | None, object | None]:
    """
    Refresh a LinkedIn OAuth2 access token using the refresh_token grant.
    See: https://learn.microsoft.com/en-us/linkedin/shared/authentication/programmatic-refresh-tokens

    Returns (new_access_token, new_refresh_token_or_None, new_expiry_datetime) on success,
    or (None, None, None) on failure.
    """
    payload = urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode("utf-8")
    req = urllib_request.Request(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib_request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        new_token = data.get("access_token")
        new_refresh = data.get("refresh_token")  # may or may not be rotated
        expires_in = data.get("expires_in")  # seconds
        if not new_token:
            logger.warning("LinkedIn refresh response missing access_token: %s", data)
            return None, None, None
        new_expiry = timezone.now() + timedelta(seconds=int(expires_in)) if expires_in else None
        return new_token, new_refresh, new_expiry
    except (error.URLError, error.HTTPError, json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.warning("LinkedIn token refresh request failed: %s", exc)
        return None, None, None
