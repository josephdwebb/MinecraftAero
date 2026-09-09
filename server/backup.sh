#!/usr/bin/env bash
# Snapshot the world to ~/aero-backups, keep the last 7. Safe to run while the
# server is up (uses RCON save-off/save-on around the copy).
# Add to cron for a daily backup:
#   (crontab -l 2>/dev/null; echo '30 5 * * * bash ~/MinecraftAero/server/backup.sh') | crontab -
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/server/run"
BK="$HOME/aero-backups"
KEEP=7
mkdir -p "$BK"
ts="$(date +%Y%m%d-%H%M%S)"

rcon() {
  python3 - "$1" <<'PY' 2>/dev/null || true
import socket,struct,sys,time
c=sys.argv[1]
def pkt(i,t,b):
    p=struct.pack("<ii",i,t)+b.encode()+b"\x00\x00"; return struct.pack("<i",len(p))+p
try:
    s=socket.create_connection(("127.0.0.1",25575),3)
    s.sendall(pkt(1,3,"ilovegian")); s.recv(4096)
    s.sendall(pkt(2,2,c)); time.sleep(0.3); s.recv(4096); s.close()
except Exception:
    pass
PY
}

rcon "save-off"; rcon "save-all flush"; sleep 2
tar -C "$RUN" -czf "$BK/world-$ts.tar.gz" world
rcon "save-on"

# prune
ls -1t "$BK"/world-*.tar.gz | tail -n +$((KEEP+1)) | xargs -r rm -f
echo "backup: $BK/world-$ts.tar.gz ($(du -h "$BK/world-$ts.tar.gz" | cut -f1)); kept $(ls "$BK"/world-*.tar.gz | wc -l)"
