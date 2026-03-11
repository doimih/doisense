"""
Management command: expire_trials

Scan users whose trial has physically expired (trial_ends_at < now) but whose
DB fields still reflect an active trial. Syncs is_premium=False and
plan_tier='free' so backend state stays consistent with effective_plan_tier().

Run on a cron: e.g. every hour.
    python manage.py expire_trials
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from users.models import User


class Command(BaseCommand):
    help = "Mark expired trial users as free and clear is_premium flag."

    def handle(self, *args, **options):
        now = timezone.now()

        expired_qs = User.objects.filter(
            plan_tier=User.PLAN_TRIAL,
            trial_ends_at__lt=now,
            is_premium=True,
        )

        count = expired_qs.count()
        if count == 0:
            self.stdout.write("No expired trials to process.")
            return

        with transaction.atomic():
            expired_qs.update(
                plan_tier=User.PLAN_FREE,
                is_premium=False,
            )

        self.stdout.write(
            self.style.SUCCESS(f"Expired {count} trial account(s) → plan_tier=free, is_premium=False.")
        )
