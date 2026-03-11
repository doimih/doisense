#!/bin/sh
set -eu

WAL_FILE_PATH="${1:-}"
if [ -z "$WAL_FILE_PATH" ]; then
  echo "WAL file path missing" >&2
  exit 1
fi

if ! ENV_EXPORTS=$(/usr/local/bin/walg-env.sh); then
  # Do not block PostgreSQL commits if backup config is missing/disabled.
  exit 0
fi

eval "$ENV_EXPORTS"
exec wal-g wal-push "$WAL_FILE_PATH"