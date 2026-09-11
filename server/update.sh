#!/usr/bin/env bash
# Pull the latest mod list from GitHub and re-sync the server, then restart.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/server/run"
# shellcheck disable=SC1091
source "$ROOT/aero.config"
PACK_URL="https://raw.githubusercontent.com/${GITHUB_REPO}/${GITHUB_BRANCH}/pack/pack.toml"

git -C "$ROOT" pull --ff-only
( cd "$RUN" && ./jdk/bin/java -jar packwiz-installer-bootstrap.jar -g -s server "$PACK_URL" )

# refresh datapacks in the existing world (no world wipe)
if [[ -d "$RUN/world" ]]; then
  for d in "$ROOT"/server/datapacks/*/; do
    [[ -d "$d" ]] && { rm -rf "$RUN/world/datapacks/$(basename "$d")"; cp -r "$d" "$RUN/world/datapacks/"; }
  done
fi

# deploy FTB Quests definitions (server-authoritative; clients sync over network)
if [[ -d "$ROOT/server/ftbquests/quests" ]]; then
  mkdir -p "$RUN/config/ftbquests"
  rm -rf "$RUN/config/ftbquests/quests"
  cp -r "$ROOT/server/ftbquests/quests" "$RUN/config/ftbquests/quests"
  echo ">> FTB Quests definitions deployed"
fi

if systemctl list-units --full -all | grep -q aero-server.service; then
  sudo systemctl restart aero-server
  echo ">> aero-server restarted."
else
  echo ">> Mods synced. Restart the server to apply."
fi
