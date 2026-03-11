"""Management command: expire trials that have passed their end date."""

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User


class Command(BaseCommand):
    help = "Expire free trials that have passed their trial_ends_at date."

    def handle(self, *args, **options):
        now = timezone.now()
        expired = User.objects.filter(
            plan_tier=User.PLAN_TRIAL,
            trial_ends_at__lt=now,
        )
        count = expired.count()
        expired.update(plan_tier=User.PLAN_FREE, is_premium=False)
        self.stdout.write(self.style.SUCCESS(f"Expired {count} trial(s)."))
