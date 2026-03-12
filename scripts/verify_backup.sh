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

VERIFY_DIR="/tmp/walg-verify-$(date +%s)"

echo "[verify] Fetching latest backup to ${VERIFY_DIR}..."
$COMPOSE exec -T db sh -lc "
  set -eu
  eval \"\$(/usr/local/bin/walg-env.sh)\"
  mkdir -p '${VERIFY_DIR}'
  wal-g backup-fetch '${VERIFY_DIR}' LATEST
  pg_controldata '${VERIFY_DIR}' >/dev/null
  rm -rf '${VERIFY_DIR}'
"

echo "[verify] Backup restore validation passed."
