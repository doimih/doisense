"""
Management command: scanează DB cu textele clienților, AI structurează informația
și actualizează automat profilele (indiferent de limbă/țară).

Usage:
  python manage.py ai_update_profiles
  python manage.py ai_update_profiles --dry-run
  python manage.py ai_update_profiles --user-id=42
  python manage.py ai_update_profiles --limit=10
"""
from django.core.management.base import BaseCommand

from ai.profile_updater import run_profile_updates_for_all_users, update_profile_from_ai


class Command(BaseCommand):
    help = "Scan user texts in DB, run AI to structure info and update user profiles (any language)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not save profile changes, only log what would be done.",
        )
        parser.add_argument(
            "--user-id",
            type=int,
            default=None,
            help="Update only this user ID.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Max number of users to process (when not using --user-id).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        user_id = options["user_id"]
        limit = options["limit"]

        if dry_run:
            self.stdout.write("DRY RUN – no profile changes will be saved.")

        if user_id is not None:
            ok = update_profile_from_ai(user_id, dry_run=dry_run)
            if ok:
                self.stdout.write(self.style.SUCCESS(f"Profile update done for user {user_id}."))
            else:
                self.stdout.write(self.style.WARNING(f"Profile update skipped or failed for user {user_id}."))
            return

        stats = run_profile_updates_for_all_users(dry_run=dry_run, limit=limit)
        self.stdout.write(
            f"Processed: {stats['processed']}, updated: {stats['updated']}, "
            f"skipped: {stats['skipped']}, errors: {stats['errors']}"
        )
        if dry_run:
            self.stdout.write("DRY RUN – no changes were saved.")
