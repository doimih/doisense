#!/bin/sh
set -eu

escape_single_quotes() {
  printf "%s" "$1" | sed "s/'/'\\''/g"
}

status=${1:-failed}
source_name=${2:-backup_daemon}
notes=${3:-}

if [ -z "${POSTGRES_USER:-}" ] || [ -z "${POSTGRES_DB:-}" ]; then
  exit 0
fi

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
INSERT INTO core_backupverificationlog (status, source, notes, created_at)
VALUES (
  '$(escape_single_quotes "$status")',
  '$(escape_single_quotes "$source_name")',
  '$(escape_single_quotes "$notes")',
  NOW()
);
" >/dev/null 2>&1 || true