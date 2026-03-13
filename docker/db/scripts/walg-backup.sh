#!/bin/sh
set -eu

LOG_SOURCE=${BACKUP_LOG_SOURCE:-backup_daemon}
OUTPUT_FILE=$(mktemp)
cleanup() {
  rm -f "$OUTPUT_FILE"
}
trap cleanup EXIT

if ! ENV_EXPORTS=$(/usr/local/bin/walg-env.sh); then
  exit 0
fi

eval "$ENV_EXPORTS"

if wal-g backup-push "${PGDATA}" >"$OUTPUT_FILE" 2>&1 \
  && wal-g delete retain FULL "${WALG_RETENTION_FULL}" --confirm >>"$OUTPUT_FILE" 2>&1; then
  NOTES="Automatic backup completed successfully. Prefix: ${WALG_S3_PREFIX}"
  /usr/local/bin/walg-log.sh success "$LOG_SOURCE" "$NOTES"
  cat "$OUTPUT_FILE"
else
  OUTPUT=$(tail -c 3500 "$OUTPUT_FILE" 2>/dev/null || cat "$OUTPUT_FILE")
  NOTES="Automatic backup failed. Prefix: ${WALG_S3_PREFIX}. Details: ${OUTPUT}"
  /usr/local/bin/walg-log.sh failed "$LOG_SOURCE" "$NOTES"
  cat "$OUTPUT_FILE" >&2
  exit 1
fi