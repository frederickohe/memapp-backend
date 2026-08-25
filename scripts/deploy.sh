#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/var/www/memapp-backend"
ARCHIVE="${1:-}"

docker_compose() {
  if docker info >/dev/null 2>&1; then
    docker compose "$@"
  elif command -v sudo >/dev/null && sudo -n docker info >/dev/null 2>&1; then
    sudo docker compose "$@"
  else
    echo "Cannot talk to Docker. Add this user to the docker group, or allow passwordless sudo for docker." >&2
    exit 1
  fi
}

install_from_archive() {
  local archive="$1"
  local tmpdir
  tmpdir="$(mktemp -d)"
  tar -xzf "$archive" -C "$tmpdir"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete \
      --exclude '.env' \
      --exclude '.git/' \
      --exclude 'venv/' \
      --exclude '.venv/' \
      "$tmpdir"/ "$REPO_DIR"/
  else
    tar -xzf "$archive" -C "$REPO_DIR"
  fi

  rm -rf "$tmpdir"
}

mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

if [[ -n "$ARCHIVE" ]]; then
  if [[ ! -f "$ARCHIVE" ]]; then
    echo "Release archive not found: $ARCHIVE" >&2
    exit 1
  fi
  echo "Installing release from $ARCHIVE"
  install_from_archive "$ARCHIVE"
else
  echo "Pulling origin/main"
  git fetch origin main
  git reset --hard origin/main
fi

chmod +x "$REPO_DIR/scripts/"*.sh "$REPO_DIR/startup.sh" 2>/dev/null || true

docker_compose up --build -d

echo "memapp-backend deploy complete"
