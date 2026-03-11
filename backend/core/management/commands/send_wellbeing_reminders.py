"""Management command: send wellbeing check-in reminders."""

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User
from core.models import UserWellbeingCheckin
from core.notifications import (
    record_notification_delivery,
    send_wellbeing_checkin_reminder,
    was_notification_sent,
)


class Command(BaseCommand):
    help = (
        "Send daily wellbeing check-in reminders to active users who haven't checked in today. "
        "Run once daily at ~10 AM via cron or celery scheduler."
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
        
        sent_count = 0
        for user in query:
            # Check if user already has check-in for today
            has_checkin_today = UserWellbeingCheckin.objects.filter(
                user=user,
                created_at__date=today,
            ).exists()
            
            if has_checkin_today:
                continue

            if was_notification_sent(user, "wellbeing_checkin_reminder", date=today):
                continue
            
            try:
                send_wellbeing_checkin_reminder(user)
                record_notification_delivery(user, "wellbeing_checkin_reminder", date=today)
                sent_count += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"Failed to send wellbeing reminder to {user.email}: {str(e)}"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"Sent {sent_count} wellbeing check-in reminder(s).")
        )
