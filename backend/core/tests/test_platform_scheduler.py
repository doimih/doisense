import pytest
from django.core.management import call_command
from django.utils import timezone

from core.models import PlatformScheduledJob


@pytest.mark.django_db
def test_platform_scheduler_runs_due_job_once(monkeypatch):
    job = PlatformScheduledJob.objects.create(
        code="send-trial-test",
        label="Send Trial Test",
        command_name="send_trial_warnings",
        schedule_type=PlatformScheduledJob.SCHEDULE_HOURLY,
        minute_of_hour=15,
    )
    fixed_now = timezone.now().replace(second=0, microsecond=0, minute=15)
    executed = []

    monkeypatch.setattr("core.management.commands.run_platform_scheduler.timezone.now", lambda: fixed_now)
    monkeypatch.setattr(
        "core.scheduler.call_command",
        lambda command_name, stdout=None, stderr=None: executed.append(command_name),
    )

    call_command("run_platform_scheduler")
    job.refresh_from_db()

    assert executed == ["send_trial_warnings"]
    assert job.last_run_status == PlatformScheduledJob.STATUS_SUCCESS
    assert job.last_run_at == fixed_now

    call_command("run_platform_scheduler")
    assert executed == ["send_trial_warnings"]


@pytest.mark.django_db
def test_platform_scheduler_marks_failed_job(monkeypatch):
    job = PlatformScheduledJob.objects.create(
        code="audit-vip-test",
        label="Audit VIP Test",
        command_name="audit_manual_vip",
        schedule_type=PlatformScheduledJob.SCHEDULE_DAILY,
        minute_of_hour=30,
        hour_of_day=11,
    )
    fixed_now = timezone.now().replace(second=0, microsecond=0, minute=30, hour=11)

    monkeypatch.setattr("core.management.commands.run_platform_scheduler.timezone.now", lambda: fixed_now)

    def _raise(*args, **kwargs):
        raise RuntimeError("scheduler failure")

    monkeypatch.setattr("core.scheduler.call_command", _raise)

    call_command("run_platform_scheduler")
    job.refresh_from_db()

    assert job.last_run_status == PlatformScheduledJob.STATUS_FAILED
    assert "scheduler failure" in job.last_error