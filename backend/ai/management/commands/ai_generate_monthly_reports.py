from datetime import date

from django.core.management.base import BaseCommand
from django.utils import timezone

from ai.report_generator import run_monthly_reports_for_all_users


class Command(BaseCommand):
    help = "Generate monthly AI reports automatically for eligible users (VIP)."

    def add_arguments(self, parser):
        parser.add_argument("--date", dest="target_date", help="Target day in YYYY-MM-DD format (month inferred).")
        parser.add_argument("--user-id", dest="user_id", type=int, default=None, help="Run only for one user.")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Run even if today is not the first day of month.",
        )

    def handle(self, *args, **options):
        target_date_raw = options.get("target_date")
        target_date = date.fromisoformat(target_date_raw) if target_date_raw else None

        if target_date is None and not options.get("force"):
            today = timezone.localdate()
            if today.day != 1:
                self.stdout.write("Skip monthly reports: today is not first day of month. Use --force to run now.")
                return

        stats = run_monthly_reports_for_all_users(target_day=target_date, user_id=options.get("user_id"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Monthly reports: processed={stats.processed}, updated={stats.updated}, errors={stats.errors}"
            )
        )
