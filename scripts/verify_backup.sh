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

echo "[verify] Fetching latest backup and validating restore metadata..."
$COMPOSE exec -T -e BACKUP_LOG_SOURCE=manual_verify_script db /usr/local/bin/walg-verify.sh

echo "[verify] Backup restore validation passed."
