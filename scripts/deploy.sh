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

# The backend container runs as root with a bind mount on $REPO_DIR, so it
# leaves root-owned __pycache__ (and sometimes package dirs) that block rsync.
reset_bind_mount_ownership() {
  local uid gid cmd
  uid="$(id -u)"
  gid="$(id -g)"
  cmd="find /app -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true; chown -R ${uid}:${gid} /app"
  echo "Resetting bind-mount ownership to ${uid}:${gid}"

  if docker_compose exec -T backend sh -c "$cmd"; then
    return 0
  fi

  if docker info >/dev/null 2>&1; then
    docker run --rm -v "$REPO_DIR":/app alpine sh -c "$cmd"
    return 0
  fi

  if command -v sudo >/dev/null && sudo -n docker info >/dev/null 2>&1; then
    sudo docker run --rm -v "$REPO_DIR":/app alpine sh -c "$cmd"
    return 0
  fi

  if command -v sudo >/dev/null && sudo -n true >/dev/null 2>&1; then
    sudo find "$REPO_DIR" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
    sudo chown -R "${uid}:${gid}" "$REPO_DIR"
    return 0
  fi

  echo "Could not reset bind-mount ownership; rsync may fail on root-owned files." >&2
}

install_from_archive() {
  local archive="$1"
  local tmpdir
  tmpdir="$(mktemp -d)"
  tar -xzf "$archive" -C "$tmpdir"

  if command -v rsync >/dev/null 2>&1; then
    # Do not preserve owner/group from the GitHub runner tarball — that
    # causes chgrp "Operation not permitted" and aborts the release.
    rsync -rltD --delete \
      --exclude '.env' \
      --exclude '.git/' \
      --exclude 'venv/' \
      --exclude '.venv/' \
      --exclude '__pycache__/' \
      --exclude '*.pyc' \
      "$tmpdir"/ "$REPO_DIR"/
  else
    tar -xzf "$archive" -C "$REPO_DIR"
  fi

  rm -rf "$tmpdir"
}

mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

reset_bind_mount_ownership || true

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
