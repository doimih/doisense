"""Management command: send segmented reactivation campaign reminders."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from ai.models import Conversation
from core.analytics import track_event
from core.models import NotificationDelivery
from core.notifications import record_notification_delivery, send_inactivity_reminder
from users.models import User


SEGMENTS = [
    (30, "inactive_30d"),
    (14, "inactive_14d"),
    (7, "inactive_7d"),
]


class Command(BaseCommand):
    help = (
        "Send segmented reactivation reminders to paid/trial users based on inactivity windows "
        "(7d, 14d, 30d), with per-segment deduplication."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=500,
            help="Maximum users to process in one run (default: 500).",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        process_limit = max(1, options["limit"])

        candidates = User.objects.filter(
            is_active=True,
            plan_tier__in=[User.PLAN_TRIAL, User.PLAN_BASIC, User.PLAN_PREMIUM, User.PLAN_VIP],
        )[:process_limit]

        sent = 0
        skipped = 0

        for user in candidates:
            last_conversation = Conversation.objects.filter(user=user).order_by("-created_at").first()
            if not last_conversation:
                skipped += 1
                continue

            days_inactive = (now - last_conversation.created_at).days
            segment = self._resolve_segment(days_inactive)
            if not segment:
                skipped += 1
                continue

            _, segment_key = segment
            context_key = f"reactivation:{segment_key}"

            already_sent = NotificationDelivery.objects.filter(
                user=user,
                notification_type="reactivation_campaign",
                context_key=context_key,
            ).exists()
            if already_sent:
                skipped += 1
                continue

            try:
                send_inactivity_reminder(user, days_inactive)
                record_notification_delivery(
                    user,
                    "reactivation_campaign",
                    date=now.date(),
                    context_key=context_key,
                )
                track_event(
                    "reactivation_campaign_sent",
                    source="system",
                    user=user,
                    properties={"segment": segment_key, "days_inactive": days_inactive},
                )
                sent += 1
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"Failed for {user.email}: {exc}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Reactivation campaign completed. sent={sent}, skipped={skipped}, processed={sent + skipped}."
            )
        )

    @staticmethod
    def _resolve_segment(days_inactive: int):
        for threshold, key in SEGMENTS:
            if days_inactive >= threshold:
                return threshold, key
        return None