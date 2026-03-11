"""Management command: send goal-focused reminders based on stored profile goals."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from ai.models import Conversation
from core.notifications import (
    record_notification_delivery,
    send_goal_reminder,
    was_notification_sent,
)
from journal.models import JournalEntry
from profiles.models import UserProfile
from users.models import User


class Command(BaseCommand):
    help = (
        "Send goal reminders to active users who have goals in their profile and "
        "have not engaged recently. Run daily via cron or celery scheduler."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days-since-activity",
            type=int,
            default=2,
            help="Days since last journal/chat activity to qualify (default: 2)",
        )
        parser.add_argument(
            "--skip-free",
            action="store_true",
            help="Skip free tier users",
        )

    def handle(self, *args, **options):
        days_since_activity = options["days_since_activity"]
        skip_free = options["skip_free"]
        now = timezone.now()
        today = now.date()
        cutoff_date = now - timedelta(days=days_since_activity)

        profiles = UserProfile.objects.select_related("user").filter(user__is_active=True)
        if skip_free:
            profiles = profiles.exclude(user__plan_tier=User.PLAN_FREE)
        else:
            profiles = profiles.filter(
                user__plan_tier__in=[
                    User.PLAN_TRIAL,
                    User.PLAN_BASIC,
                    User.PLAN_PREMIUM,
                    User.PLAN_VIP,
                ]
            )

        sent_count = 0
        for profile in profiles:
            user = profile.user
            goals = self._extract_goals(profile.keywords)
            if not goals:
                continue

            if was_notification_sent(user, "goal_reminder", date=today):
                continue

            last_conversation = (
                Conversation.objects.filter(user=user)
                .order_by("-created_at")
                .values_list("created_at", flat=True)
                .first()
            )
            last_journal = (
                JournalEntry.objects.filter(user=user)
                .order_by("-created_at")
                .values_list("created_at", flat=True)
                .first()
            )

            last_focus_at = max(
                [timestamp for timestamp in [last_conversation, last_journal] if timestamp is not None],
                default=None,
            )
            if last_focus_at is None or last_focus_at > cutoff_date:
                continue

            days_without_focus = max(1, (now - last_focus_at).days)

            try:
                send_goal_reminder(user, goals, days_without_focus)
                record_notification_delivery(user, "goal_reminder", date=today)
                sent_count += 1
            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to send goal reminder to {user.email}: {str(exc)}"
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"Sent {sent_count} goal reminder(s)."))

    @staticmethod
    def _extract_goals(keywords) -> list[str]:
        if not isinstance(keywords, dict):
            return []
        raw_goals = keywords.get("goals") or []
        if not isinstance(raw_goals, list):
            return []
        return [goal.strip() for goal in raw_goals if isinstance(goal, str) and goal.strip()]