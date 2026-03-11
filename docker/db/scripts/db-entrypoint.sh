#!/bin/sh
set -eu

/usr/local/bin/walg-backup-daemon.sh &

exec docker-entrypoint.sh postgres \
  -c wal_level=replica \
  -c archive_mode=on \
  -c archive_timeout=60 \
  -c archive_command='/usr/local/bin/walg-archive.sh %p'