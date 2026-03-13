# Scheduler Command Map

This document maps platform scheduler job codes to Django management commands.

- `expire_trials` -> `expire_trials`
- `send_trial_warnings` -> `send_trial_warnings`
- `send_daily_plan_reminders` -> `send_daily_plan_reminders`
- `send_journal_reminders` -> `send_journal_reminders`
- `send_goal_reminders` -> `send_goal_reminders`
- `send_wellbeing_reminders` -> `send_wellbeing_reminders`
- `send_upgrade_recommendations` -> `send_upgrade_recommendations`
- `audit_manual_vip` -> `audit_manual_vip`
- `send_inactivity_reminders` -> `send_inactivity_reminders`
- `send_reactivation_campaign` -> `send_reactivation_campaign`
- `ai_update_profiles` -> `ai_update_profiles`
- `verify_backup_flow` -> `verify_backup_flow`

Execution entrypoint used by cron:

- `run_platform_scheduler` executes enabled jobs that are due.
