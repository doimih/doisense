"""Management command: send inactivity reminders."""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from users.models import User
from ai.models import Conversation
from core.notifications import (
    record_notification_delivery,
    send_inactivity_reminder,
    was_notification_sent,
)


class Command(BaseCommand):
    help = (
        "Send inactivity reminders to users with no chat activity in 7+ days. "
        "Run daily via cron or celery scheduler."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Days of inactivity threshold (default: 7)',
        )
        parser.add_argument(
            '--min-conversations',
            type=int,
            default=1,
            help='Minimum conversations to trigger reminder (default: 1)',
        )

    def handle(self, *args, **options):
        days_threshold = options['days']
        min_conversations = options['min_conversations']
        now = timezone.now()
        cutoff_date = now - timedelta(days=days_threshold)
        
        # Find users with paid access (not free tier)
        active_users = User.objects.filter(
            is_active=True,
            plan_tier__in=[User.PLAN_TRIAL, User.PLAN_BASIC, User.PLAN_PREMIUM, User.PLAN_VIP],
        )
        
        sent_count = 0
        for user in active_users:
            # Check if user has at least min_conversations
            conversation_count = Conversation.objects.filter(user=user).count()
            if conversation_count < min_conversations:
                continue
            
            # Check last conversation date
            last_conversation = Conversation.objects.filter(user=user).order_by('-created_at').first()
            if not last_conversation or last_conversation.created_at > cutoff_date:
                continue
            
            # Calculate days inactive
            days_inactive = (now - last_conversation.created_at).days

            if was_notification_sent(user, "inactivity_reminder"):
                continue
            
            try:
                send_inactivity_reminder(user, days_inactive)
                record_notification_delivery(user, "inactivity_reminder")
                sent_count += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to send inactivity reminder to {user.email}: {str(e)}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Sent {sent_count} inactivity reminder(s) to users inactive for {days_threshold}+ days."
            )
        )
