from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import PlatformScheduledJob
from core.scheduler import execute_scheduled_job, sync_default_scheduler_tasks


class Command(BaseCommand):
    help = "Run due platform scheduler jobs configured in Django Admin."

    def add_arguments(self, parser):
        parser.add_argument(
            "--job-code",
            dest="job_code",
            help="Run a single job by code, ignoring due-time checks.",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        job_code = options.get("job_code")

        sync_default_scheduler_tasks()

        jobs = PlatformScheduledJob.objects.filter(enabled=True)
        if job_code:
            jobs = jobs.filter(code=job_code)

        executed = 0
        for job in jobs.order_by("label"):
            if job_code or job.is_due(now):
                executed += 1
                success, message = execute_scheduled_job(job, now=now)
                if success:
                    self.stdout.write(self.style.SUCCESS(f"Executed {job.code}"))
                else:
                    self.stderr.write(self.style.ERROR(f"Failed {job.code}: {message}"))

        if executed == 0:
            self.stdout.write("No scheduled jobs were due.")