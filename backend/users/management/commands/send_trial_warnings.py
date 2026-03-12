"""Management command: send trial expiration warnings."""

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User
from core.notifications import (
    record_notification_delivery,
    send_trial_expiration_warning,
    was_notification_sent,
)


class Command(BaseCommand):
    help = (
        "Send trial expiration warnings to users on days 5, 6, and 7 of trial. "
        "Run daily via cron or celery scheduler."
    )

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find users in trial who still have access
        trial_users = User.objects.filter(
            plan_tier=User.PLAN_TRIAL,
            trial_ends_at__isnull=False,
            vip_manual_override=False,
        )
        
        sent_count = 0
        for user in trial_users:
            if user.trial_ends_at <= now:
                # Trial already expired
                continue
            
            days_left = (user.trial_ends_at.date() - now.date()).days
            
            # Send warnings on days 5, 6, and 7
            if days_left in (5, 6, 7):
                context_key = f"day_{days_left}"
                if was_notification_sent(
                    user,
                    "trial_expiration_warning",
                    date=now.date(),
                    context_key=context_key,
                ):
                    continue
                try:
                    send_trial_expiration_warning(user, days_left)
                    record_notification_delivery(
                        user,
                        "trial_expiration_warning",
                        date=now.date(),
                        context_key=context_key,
                    )
                    sent_count += 1
                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Failed to send trial warning to {user.email}: {str(e)}"
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f"Sent {sent_count} trial expiration warning(s).")
        )
