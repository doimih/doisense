from datetime import date

from django.core.management.base import BaseCommand

from ai.report_generator import run_daily_reports_for_all_users


class Command(BaseCommand):
    help = "Generate daily AI reports automatically for eligible users."

    def add_arguments(self, parser):
        parser.add_argument("--date", dest="target_date", help="Target date in YYYY-MM-DD format.")
        parser.add_argument(
            "--user-id", dest="user_id", type=int, default=None, help="Run only for one user."
        )

    def handle(self, *args, **options):
        target_date_raw = options.get("target_date")
        target_date = date.fromisoformat(target_date_raw) if target_date_raw else None
        stats = run_daily_reports_for_all_users(
            target_day=target_date, user_id=options.get("user_id")
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Daily reports: processed={stats.processed}, updated={stats.updated}, errors={stats.errors}"
            )
        )
