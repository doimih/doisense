#!/bin/bash
# =============================================================================
# scripts/setup_cron.sh
# Doisense — Autonomous Scheduler Setup
# Run once on the host server to configure all recurring jobs.
# Usage: bash scripts/setup_cron.sh
# =============================================================================

set -e

COMPOSE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CMD="docker compose -f $COMPOSE_DIR/docker-compose.yml exec -T backend python manage.py"
LOG="$COMPOSE_DIR/logs/cron.log"
CRON_TAG="# doisense-auto"

# Ensure logs directory exists
mkdir -p "$COMPOSE_DIR/logs"

echo "Setting up Doisense autonomous scheduler..."
echo "Project root: $COMPOSE_DIR"
echo "Log file: $LOG"

# Remove existing doisense entries to avoid duplicates
(crontab -l 2>/dev/null | grep -v "$CRON_TAG") | crontab - 2>/dev/null || true

# Add all scheduled jobs
(
  crontab -l 2>/dev/null || true
  cat <<CRON
# ── Doisense Autonomous Scheduler ──────────────────────────────────── #

# Hourly: expire trials whose trial_ends_at has passed
0 * * * *   $CMD expire_trials >> $LOG 2>&1  $CRON_TAG

# 05:00 daily: send trial expiration warnings (days 5, 6, 7)
0 5 * * *   $CMD send_trial_warnings >> $LOG 2>&1  $CRON_TAG

# 07:00 daily: send daily plan reminders to premium+ users
0 7 * * *   $CMD send_daily_plan_reminders >> $LOG 2>&1  $CRON_TAG

# 08:00 daily: send journal reminders to users with no entry today
0 8 * * *   $CMD send_journal_reminders >> $LOG 2>&1  $CRON_TAG

# 18:00 daily: send goal reminders to users with saved goals and low recent engagement
0 18 * * *  $CMD send_goal_reminders >> $LOG 2>&1  $CRON_TAG

# 10:00 daily: send wellbeing check-in reminders to premium+ users
0 10 * * *  $CMD send_wellbeing_reminders >> $LOG 2>&1  $CRON_TAG

# 14:00 daily: send upgrade recommendations to engaged trial/basic users
0 14 * * *  $CMD send_upgrade_recommendations >> $LOG 2>&1  $CRON_TAG

# 09:00 daily: send inactivity reminders (users inactive 7+ days)
0 9 * * *   $CMD send_inactivity_reminders >> $LOG 2>&1  $CRON_TAG

# 02:00 daily: refresh AI user profiles from journal entries
0 2 * * *   $CMD ai_update_profiles >> $LOG 2>&1  $CRON_TAG

# 03:00 daily (Sunday): PostgreSQL backup to /opt/backups/doisense/
0 3 * * 0   docker compose -f $COMPOSE_DIR/docker-compose.yml exec -T db \
  pg_dump -Fc doisense > /opt/backups/doisense/doisense_\$(date +\%Y\%m\%d_\%H\%M).dump \
  >> $LOG 2>&1  $CRON_TAG

# ───────────────────────────────────────────────────────────────────── #
CRON
) | crontab -

echo "✓ Crontab installed. Verify with: crontab -l"

# Create backup directory if it doesn't exist
mkdir -p /opt/backups/doisense
echo "✓ Backup directory ensured: /opt/backups/doisense"

echo ""
echo "==== Active Doisense cron jobs ===="
crontab -l | grep "$CRON_TAG" || echo "(none found)"
echo ""
echo "Done."
