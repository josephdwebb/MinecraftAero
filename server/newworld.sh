#!/usr/bin/env bash
# Wipe the world and regenerate it from the seed in server/server.properties.
# Backs the old world up first. Datapacks are re-installed automatically.
#
#   bash server/newworld.sh          (you'll be asked for your sudo password)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/server/run"
BK="$HOME/aero-backups"
SEED="$(grep -oP 'level-seed=\K.*' "$ROOT/server/server.properties" || true)"

echo ">> New world from seed: ${SEED:-(random)}"
read -rp ">> This DELETES the current world. Type 'yes' to continue: " ok
[[ "$ok" == "yes" ]] || { echo "aborted"; exit 1; }

sudo systemctl stop aero-server || true

if [[ -d "$RUN/world" ]]; then
  mkdir -p "$BK"
  ts="$(date +%Y%m%d-%H%M%S)"
  echo ">> Backing up old world -> $BK/world-$ts.tar.gz"
  tar -C "$RUN" -czf "$BK/world-$ts.tar.gz" world
  rm -rf "$RUN/world"
fi

# fresh server.properties (carries the new seed + any committed setting changes)
cp "$ROOT/server/server.properties" "$RUN/server.properties"

# re-install datapacks into the (about-to-be-generated) world
mkdir -p "$RUN/world/datapacks"
for d in "$ROOT"/server/datapacks/*/; do
  [[ -d "$d" ]] && cp -r "$d" "$RUN/world/datapacks/"
done
echo ">> Datapacks: $(ls "$RUN/world/datapacks")"

sudo systemctl start aero-server
echo ">> Server starting. Watch:  journalctl -u aero-server -f"
echo ">> Tell everyone to clear their Distant Horizons data for this world"
echo "   (DH menu -> Advanced -> 'Delete Distant Horizons data' -> This World)."
