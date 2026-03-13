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

echo "[backup] Triggering WAL-G backup inside db container..."
$COMPOSE exec -T -e BACKUP_LOG_SOURCE=manual_backup_script db /usr/local/bin/walg-backup.sh

echo "[backup] Verifying latest backup is visible..."
$COMPOSE exec -T db sh -lc '
  set -eu
  eval "$(/usr/local/bin/walg-env.sh)"
  wal-g backup-list | sed -n "1,8p"
'

echo "[backup] Done."
