"""Management command: send daily planning reminders."""

from django.core.management.base import BaseCommand

from users.models import User
from core.notifications import (
    record_notification_delivery,
    send_daily_plan_reminder,
    was_notification_sent,
)


class Command(BaseCommand):
    help = (
        "Send daily planning prompt reminders to active users. "
        "Run once daily at ~7 AM via cron or celery scheduler."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-free',
            action='store_true',
            help='Skip free tier users',
        )
        parser.add_argument(
            '--min-conversations',
            type=int,
            default=1,
            help='Minimum past conversations to trigger reminder (default: 1)',
        )

    def handle(self, *args, **options):
        skip_free = options['skip_free']
        min_conversations = options['min_conversations']
        
        # Filter active paid users
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
        
        from ai.models import Conversation
        
        sent_count = 0
        for user in query:
            # Only remind users who have already used the platform
            conversation_count = Conversation.objects.filter(user=user).count()
            if conversation_count < min_conversations:
                continue

            if was_notification_sent(user, "daily_plan_reminder"):
                continue
            
            try:
                send_daily_plan_reminder(user)
                record_notification_delivery(user, "daily_plan_reminder")
                sent_count += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to send planning reminder to {user.email}: {str(e)}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"Sent {sent_count} daily planning reminder(s).")
        )
