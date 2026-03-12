from dataclasses import dataclass
from io import StringIO
import time

from django.core.management import call_command
from django.utils import timezone

from .models import PlatformScheduledJob


@dataclass(frozen=True)
class SchedulerTaskDefinition:
    code: str
    label: str
    command_name: str
    schedule_type: str
    minute_of_hour: int
    hour_of_day: int | None = None
    weekday: int | None = None


DEFAULT_SCHEDULER_TASKS = [
    SchedulerTaskDefinition("expire_trials", "Expire Trials", "expire_trials", PlatformScheduledJob.SCHEDULE_HOURLY, 0),
    SchedulerTaskDefinition("send_trial_warnings", "Send Trial Warnings", "send_trial_warnings", PlatformScheduledJob.SCHEDULE_DAILY, 0, 5),
    SchedulerTaskDefinition("send_daily_plan_reminders", "Send Daily Plan Reminders", "send_daily_plan_reminders", PlatformScheduledJob.SCHEDULE_DAILY, 0, 7),
    SchedulerTaskDefinition("send_journal_reminders", "Send Journal Reminders", "send_journal_reminders", PlatformScheduledJob.SCHEDULE_DAILY, 0, 8),
    SchedulerTaskDefinition("send_goal_reminders", "Send Goal Reminders", "send_goal_reminders", PlatformScheduledJob.SCHEDULE_DAILY, 0, 18),
    SchedulerTaskDefinition("send_wellbeing_reminders", "Send Wellbeing Reminders", "send_wellbeing_reminders", PlatformScheduledJob.SCHEDULE_DAILY, 0, 10),
    SchedulerTaskDefinition("send_upgrade_recommendations", "Send Upgrade Recommendations", "send_upgrade_recommendations", PlatformScheduledJob.SCHEDULE_DAILY, 0, 14),
    SchedulerTaskDefinition("audit_manual_vip", "Audit Manual VIP", "audit_manual_vip", PlatformScheduledJob.SCHEDULE_WEEKLY, 0, 6, 0),
    SchedulerTaskDefinition("send_inactivity_reminders", "Send Inactivity Reminders", "send_inactivity_reminders", PlatformScheduledJob.SCHEDULE_DAILY, 0, 9),
    SchedulerTaskDefinition("ai_update_profiles", "Refresh AI Profiles", "ai_update_profiles", PlatformScheduledJob.SCHEDULE_DAILY, 0, 2),
]


def execute_scheduled_job(job: PlatformScheduledJob, *, now=None) -> tuple[bool, str]:
    started_at = time.monotonic()
    stdout = StringIO()
    stderr = StringIO()
    executed_at = now or timezone.now()

    try:
        call_command(job.command_name, stdout=stdout, stderr=stderr)
        status = PlatformScheduledJob.STATUS_SUCCESS
        combined_output = "\n".join(part for part in [stdout.getvalue().strip(), stderr.getvalue().strip()] if part).strip()
        job.last_error = combined_output[:5000]
        success = True
    except Exception as exc:
        status = PlatformScheduledJob.STATUS_FAILED
        error_output = stderr.getvalue().strip()
        job.last_error = (error_output or str(exc))[:5000]
        success = False

    duration_ms = int((time.monotonic() - started_at) * 1000)
    job.last_run_at = executed_at
    job.last_run_status = status
    job.last_duration_ms = duration_ms
    job.save(update_fields=["last_run_at", "last_run_status", "last_error", "last_duration_ms", "updated_at"])
    return success, job.last_error