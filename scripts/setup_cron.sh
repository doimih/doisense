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

# Every minute: run the admin-configurable platform scheduler
* * * * *   $CMD run_platform_scheduler >> $LOG 2>&1  $CRON_TAG

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
