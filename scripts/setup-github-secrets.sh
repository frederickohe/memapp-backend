#!/usr/bin/env bash
# Configure GitHub Actions deploy secrets for the backend and admin portal.
#
# Prerequisites:
#   1. GitHub CLI: https://cli.github.com/  then  gh auth login
#   2. A Linux user on the VPS that can write /var/www and run Docker
#      (default: deploy). Run memappcaddy/scripts/setup-server-for-cicd.sh as root.
#
# Usage:
#   bash scripts/setup-github-secrets.sh
#
# Environment overrides:
#   GITHUB_OWNER      default frederickohe
#   DEPLOY_HOST       default 62.171.136.252
#   DEPLOY_USER       default deploy
#   DEPLOY_KEY_PATH   default ~/.memapp-deploy/github_actions_deploy

set -euo pipefail

OWNER="${GITHUB_OWNER:-frederickohe}"
DEPLOY_HOST="${DEPLOY_HOST:-62.171.136.252}"
DEPLOY_USER="${DEPLOY_USER:-deploy}"
KEY_PATH="${DEPLOY_KEY_PATH:-$HOME/.memapp-deploy/github_actions_deploy}"
REPOS=(memapp-backend memapp-web)

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not installed. See https://cli.github.com/" >&2
  exit 1
fi

gh auth status

mkdir -p "$(dirname "$KEY_PATH")"
if [[ ! -f "$KEY_PATH" ]]; then
  ssh-keygen -t ed25519 -f "$KEY_PATH" -N "" -C "github-actions-memapp-deploy"
  echo
  echo "Add this public key to ${DEPLOY_USER}@${DEPLOY_HOST}:~/.ssh/authorized_keys"
  echo "------------------------------------------------------------------------"
  cat "${KEY_PATH}.pub"
  echo "------------------------------------------------------------------------"
  echo "On the server as root:"
  echo "  mkdir -p /home/${DEPLOY_USER}/.ssh"
  echo "  echo '$(cat "${KEY_PATH}.pub")' >> /home/${DEPLOY_USER}/.ssh/authorized_keys"
  echo "  chown -R ${DEPLOY_USER}:${DEPLOY_USER} /home/${DEPLOY_USER}/.ssh"
  echo "  chmod 700 /home/${DEPLOY_USER}/.ssh && chmod 600 /home/${DEPLOY_USER}/.ssh/authorized_keys"
  echo
  read -r -p "Press Enter after the public key is installed on the server..."
fi

echo "Testing SSH ${DEPLOY_USER}@${DEPLOY_HOST} ..."
ssh -i "$KEY_PATH" -o StrictHostKeyChecking=accept-new -o BatchMode=yes \
  "${DEPLOY_USER}@${DEPLOY_HOST}" 'echo ssh-ok && test -d /var/www/memapp-backend && test -d /var/www/memapp-web'

for repo in "${REPOS[@]}"; do
  full="$OWNER/$repo"
  echo "Setting secrets on $full"
  gh secret set DEPLOY_HOST --repo "$full" --body "$DEPLOY_HOST"
  gh secret set DEPLOY_USER --repo "$full" --body "$DEPLOY_USER"
  gh secret set DEPLOY_SSH_KEY --repo "$full" < "$KEY_PATH"
done

echo
echo "Done. Push to main (or run the workflow from the Actions tab) to deploy."
echo "  Backend:  https://github.com/${OWNER}/memapp-backend/actions"
echo "  Admin:    https://github.com/${OWNER}/memapp-web/actions"
