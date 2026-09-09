#!/usr/bin/env bash
# Pull the latest mod list from GitHub and re-sync the server, then restart.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/server/run"
# shellcheck disable=SC1091
source "$ROOT/aero.config"
PACK_URL="https://raw.githubusercontent.com/${GITHUB_REPO}/${GITHUB_BRANCH}/pack/pack.toml"

git -C "$ROOT" pull --ff-only
( cd "$RUN" && ./jdk/bin/java -jar packwiz-installer.jar -g -s server "$PACK_URL" )

if systemctl list-units --full -all | grep -q aero-server.service; then
  sudo systemctl restart aero-server
  echo ">> aero-server restarted."
else
  echo ">> Mods synced. Restart the server to apply."
fi
