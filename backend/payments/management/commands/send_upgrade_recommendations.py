"""Management command: send upgrade recommendations."""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from users.models import User
from journal.models import JournalEntry
from ai.models import Conversation
from core.notifications import (
    record_notification_delivery,
    send_upgrade_recommendation,
    was_notification_sent,
)


class Command(BaseCommand):
    help = (
        "Send upgrade recommendations to BASIC and TRIAL users based on behavior. "
        "Run daily via cron or celery scheduler."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-journal-entries',
            type=int,
            default=5,
            help='Min journal entries to suggest premium (default: 5)',
        )
        parser.add_argument(
            '--min-conversations',
            type=int,
            default=3,
            help='Min conversations to suggest premium (default: 3)',
        )
        parser.add_argument(
            '--days-active',
            type=int,
            default=3,
            help='Days of activity to qualify (default: 3)',
        )

    def handle(self, *args, **options):
        min_journal = options['min_journal_entries']
        min_conv = options['min_conversations']
        days_active = options['days_active']
        now = timezone.now()
        cutoff_date = now - timedelta(days=days_active)
        
        # Find BASIC/TRIAL users with good engagement
        trial_basic_users = User.objects.filter(
            plan_tier__in=[User.PLAN_TRIAL, User.PLAN_BASIC],
            is_active=True,
        )
        
        sent_count = 0
        for user in trial_basic_users:
            journal_count = JournalEntry.objects.filter(user=user).count()
            conv_count = Conversation.objects.filter(user=user).count()
            
            # Check recent activity
            recent_activity = Conversation.objects.filter(
                user=user,
                created_at__gte=cutoff_date,
            ).exists()
            
            if not recent_activity:
                continue
            
            reason = None
            if journal_count >= min_journal:
                reason = "journal_limit"
            elif conv_count >= min_conv:
                reason = "report_limit"
            else:
                continue

            if was_notification_sent(
                user,
                "upgrade_recommendation",
                date=now.date(),
                context_key=reason,
            ):
                continue
            
            try:
                send_upgrade_recommendation(user, reason)
                record_notification_delivery(
                    user,
                    "upgrade_recommendation",
                    date=now.date(),
                    context_key=reason,
                )
                sent_count += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to send upgrade recommendation to {user.email}: {str(e)}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"Sent {sent_count} upgrade recommendation(s).")
        )
