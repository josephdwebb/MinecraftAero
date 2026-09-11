#!/usr/bin/env bash
# Deploy quest definitions. MUST run with the server STOPPED.
#
# FTB Quests loads quests into memory at startup and writes them back on
# shutdown. Copying files while the server is up gets silently reverted when it
# next saves, so this script refuses to run against a live server.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/server/run"

if ss -tln | grep -q ":25565 "; then
  echo "!! Server is RUNNING. Stop it first:  sudo systemctl stop aero-server" >&2
  exit 1
fi

echo ">> deploying quest definitions"
rm -rf "$RUN/config/ftbquests/quests"
mkdir -p "$RUN/config/ftbquests"
cp -r "$ROOT/server/ftbquests/quests" "$RUN/config/ftbquests/quests"

echo ">> deploying datapacks"
for d in "$ROOT"/server/datapacks/*/; do
  [ -d "$d" ] && { rm -rf "$RUN/world/datapacks/$(basename "$d")"; cp -r "$d" "$RUN/world/datapacks/"; }
done

if [ "${1:-}" = "--reset-progress" ]; then
  echo ">> wiping all player quest progress"
  rm -f "$RUN"/world/ftbquests/*.snbt
fi

python3 - "$RUN" <<'PY'
import re, collections, pathlib, sys
run = pathlib.Path(sys.argv[1])
ok = True
for f in sorted((run / "config/ftbquests/quests/chapters").glob("*.snbt")):
    t = f.read_text()
    deps = re.findall(r"dependencies: \[([^\]]*)\]", t, re.S)
    ids = re.findall(r'"([0-9A-F]{16})"', "".join(deps))
    forks = [k for k, v in collections.Counter(ids).items() if v > 1]
    titles = t.count("\ttitle:")
    print(f"   {f.name}: {len(deps)} deps, {len(forks)} forks, {titles} inline titles")
    if forks:
        ok = False
print(">> LINEAR OK" if ok else "!! STILL FORKED")
PY
echo ">> done. Now:  sudo systemctl start aero-server"
