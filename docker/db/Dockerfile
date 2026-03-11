FROM postgres:16

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash ca-certificates wget tzdata \
    && rm -rf /var/lib/apt/lists/*

ARG WALG_VERSION=v3.0.8
ARG WALG_ASSET=wal-g-pg-22.04-amd64.tar.gz

RUN wget -qO /tmp/wal-g.tar.gz "https://github.com/wal-g/wal-g/releases/download/${WALG_VERSION}/${WALG_ASSET}" \
    && tar -xzf /tmp/wal-g.tar.gz -C /tmp \
    && install -m 0755 /tmp/wal-g-pg-22.04-amd64 /usr/local/bin/wal-g \
    && rm -f /tmp/wal-g.tar.gz \
    && rm -f /tmp/wal-g-pg-22.04-amd64

COPY scripts/walg-env.sh /usr/local/bin/walg-env.sh
COPY scripts/walg-archive.sh /usr/local/bin/walg-archive.sh
COPY scripts/walg-backup.sh /usr/local/bin/walg-backup.sh
COPY scripts/walg-backup-daemon.sh /usr/local/bin/walg-backup-daemon.sh
COPY scripts/db-entrypoint.sh /usr/local/bin/db-entrypoint.sh

RUN chmod +x /usr/local/bin/walg-env.sh \
    /usr/local/bin/walg-archive.sh \
    /usr/local/bin/walg-backup.sh \
    /usr/local/bin/walg-backup-daemon.sh \
    /usr/local/bin/db-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/db-entrypoint.sh"]