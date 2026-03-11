#!/bin/sh
set -eu

if ! ENV_EXPORTS=$(/usr/local/bin/walg-env.sh); then
  exit 0
fi

eval "$ENV_EXPORTS"

wal-g backup-push "${PGDATA}"
wal-g delete retain FULL "${WALG_RETENTION_FULL}" --confirm