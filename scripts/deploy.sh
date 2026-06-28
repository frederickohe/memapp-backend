#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/var/www/memapp-backend"

cd "$REPO_DIR"
git fetch origin main
git reset --hard origin/main

docker compose up --build -d

echo "memapp-backend deploy complete"
