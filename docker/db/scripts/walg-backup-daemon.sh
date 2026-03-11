#!/bin/sh
set -eu

while ! pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; do
  sleep 5
done

while true; do
  /usr/local/bin/walg-backup.sh || true

  SCHEDULE_MINUTES=$(psql -tA -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
    SELECT COALESCE(NULLIF(backup_schedule_minutes, 0), 10)
    FROM core_systemconfig
    WHERE id = 1;
  " 2>/dev/null || echo "10")

  if [ -z "$SCHEDULE_MINUTES" ]; then
    SCHEDULE_MINUTES=10
  fi

  SLEEP_SECONDS=$((SCHEDULE_MINUTES * 60))
  if [ "$SLEEP_SECONDS" -lt 60 ]; then
    SLEEP_SECONDS=600
  fi

  sleep "$SLEEP_SECONDS"
done