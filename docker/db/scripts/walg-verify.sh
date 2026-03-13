#!/bin/sh
set -eu

LOG_SOURCE=${BACKUP_LOG_SOURCE:-manual_verify_script}
OUTPUT_FILE=$(mktemp)
VERIFY_DIR="/tmp/walg-verify-$(date +%s)"

cleanup() {
  rm -f "$OUTPUT_FILE"
  rm -rf "$VERIFY_DIR"
}
trap cleanup EXIT

if ! ENV_EXPORTS=$(/usr/local/bin/walg-env.sh); then
  exit 0
fi

eval "$ENV_EXPORTS"

PG_CONTROLDATA_BIN=${PG_CONTROLDATA_BIN:-$(command -v pg_controldata || true)}
if [ -z "$PG_CONTROLDATA_BIN" ] && [ -x "/usr/lib/postgresql/16/bin/pg_controldata" ]; then
  PG_CONTROLDATA_BIN="/usr/lib/postgresql/16/bin/pg_controldata"
fi

if [ -z "$PG_CONTROLDATA_BIN" ]; then
  NOTES="Backup restore validation failed. Prefix: ${WALG_S3_PREFIX}. Details: pg_controldata binary not found in container."
  /usr/local/bin/walg-log.sh failed "$LOG_SOURCE" "$NOTES"
  echo "pg_controldata binary not found in container" >&2
  exit 1
fi

if mkdir -p "$VERIFY_DIR" \
  && wal-g backup-fetch "$VERIFY_DIR" LATEST >"$OUTPUT_FILE" 2>&1 \
  && "$PG_CONTROLDATA_BIN" "$VERIFY_DIR" >>"$OUTPUT_FILE" 2>&1; then
  NOTES="Backup restore validation passed. Prefix: ${WALG_S3_PREFIX}"
  /usr/local/bin/walg-log.sh success "$LOG_SOURCE" "$NOTES"
  cat "$OUTPUT_FILE"
else
  OUTPUT=$(tail -c 3500 "$OUTPUT_FILE" 2>/dev/null || cat "$OUTPUT_FILE")
  NOTES="Backup restore validation failed. Prefix: ${WALG_S3_PREFIX}. Details: ${OUTPUT}"
  /usr/local/bin/walg-log.sh failed "$LOG_SOURCE" "$NOTES"
  cat "$OUTPUT_FILE" >&2
  exit 1
fi