#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "[1/4] Building frontend image..."
docker compose build frontend

echo "[2/4] Restarting frontend service..."
docker compose up -d frontend

echo "[3/4] Checking service status..."
docker compose ps frontend

echo "[4/4] Done. Frontend rebuild + restart completed."
