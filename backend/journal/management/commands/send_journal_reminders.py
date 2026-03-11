"""Management command: send daily journal reminders."""

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User
from journal.models import JournalEntry
from core.notifications import (
    record_notification_delivery,
    send_journal_reminder,
    was_notification_sent,
)


class Command(BaseCommand):
    help = (
        "Send journal reminder emails to users who haven't made an entry today. "
        "Run daily at ~8 AM via cron or celery scheduler."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-free',
            action='store_true',
            help='Skip free tier users',
        )

    def handle(self, *args, **options):
        skip_free = options['skip_free']
        now = timezone.now()
        today = now.date()
        
        # Filter users based on options
        query = User.objects.filter(is_active=True)
        if skip_free:
            query = query.exclude(plan_tier=User.PLAN_FREE)
        else:
            query = query.filter(
                plan_tier__in=[
                    User.PLAN_TRIAL,
                    User.PLAN_BASIC,
                    User.PLAN_PREMIUM,
                    User.PLAN_VIP,
                ]
            )
        
        sent_count = 0
        for user in query:
            # Check if user has made an entry today
            has_entry_today = JournalEntry.objects.filter(
                user=user,
                created_at__date=today,
            ).exists()
            
            if has_entry_today:
                continue

            if was_notification_sent(user, "journal_reminder", date=today):
                continue
            
            try:
                send_journal_reminder(user)
                record_notification_delivery(user, "journal_reminder", date=today)
                sent_count += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to send journal reminder to {user.email}: {str(e)}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"Sent {sent_count} journal reminder(s).")
        )
