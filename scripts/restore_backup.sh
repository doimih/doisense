#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT_DIR"

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE="docker-compose"
else
  echo "Error: docker compose is not available." >&2
  exit 1
fi

TARGET_BACKUP="${1:-LATEST}"

if [ "${CONFIRM_RESTORE:-}" != "yes" ]; then
  echo "Refusing to restore without confirmation."
  echo "Run with: CONFIRM_RESTORE=yes ./scripts/restore_backup.sh ${TARGET_BACKUP}" >&2
  exit 1
fi

echo "[restore] Stopping backend and db services..."
$COMPOSE stop backend db

echo "[restore] Restoring backup '${TARGET_BACKUP}' into PostgreSQL data volume..."
$COMPOSE run --rm --no-deps --entrypoint sh db -lc "
  set -eu
  rm -rf /var/lib/postgresql/data/*
  eval \"\$(/usr/local/bin/walg-env.sh)\"
  wal-g backup-fetch /var/lib/postgresql/data '${TARGET_BACKUP}'
  chown -R postgres:postgres /var/lib/postgresql/data
"

echo "[restore] Starting db and backend services..."
$COMPOSE up -d db backend

echo "[restore] Restore completed. Run migration/status checks before opening traffic."
