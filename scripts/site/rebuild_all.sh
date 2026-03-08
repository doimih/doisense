#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

echo "[1/5] Building backend image..."
docker compose build backend

echo "[2/5] Building frontend image..."
docker compose build frontend

echo "[3/5] Restarting backend + frontend services..."
docker compose up -d backend frontend

echo "[4/5] Checking services status..."
docker compose ps backend frontend

echo "[5/5] Done. Full rebuild + restart completed."
