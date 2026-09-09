#!/usr/bin/env bash
# One-time server setup for Raspberry Pi 5 (Raspberry Pi OS 64-bit / any arm64 Linux).
#   git clone https://github.com/<you>/aero-server && cd aero-server
#   bash server/setup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUN="$ROOT/server/run"
cd "$ROOT"

# shellcheck disable=SC1091
source "$ROOT/aero.config"
[[ "$GITHUB_REPO" == REPLACE_ME* ]] && { echo "Edit aero.config first."; exit 1; }

NEOFORGE_VER="$(grep -oP 'neoforge\s*=\s*"\K[^"]+' pack/pack.toml)"
PACK_URL="https://raw.githubusercontent.com/${GITHUB_REPO}/${GITHUB_BRANCH}/pack/pack.toml"
mkdir -p "$RUN"

# --- Java 21 (arm64) ---
JAVA="$RUN/jdk/bin/java"
if [[ ! -x "$JAVA" ]]; then
  echo ">> Downloading Temurin JDK 21 (arm64)..."
  curl -fL "https://api.adoptium.net/v3/binary/latest/21/ga/linux/aarch64/jdk/hotspot/normal/eclipse" -o /tmp/jdk21.tar.gz
  mkdir -p "$RUN/jdk"
  tar -xzf /tmp/jdk21.tar.gz -C "$RUN/jdk" --strip-components=1
  rm /tmp/jdk21.tar.gz
fi
"$JAVA" -version

# --- NeoForge server ---
if [[ ! -f "$RUN/run.sh" ]]; then
  echo ">> Installing NeoForge $NEOFORGE_VER server..."
  curl -fL "https://maven.neoforged.net/releases/net/neoforged/neoforge/${NEOFORGE_VER}/neoforge-${NEOFORGE_VER}-installer.jar" -o /tmp/neoforge-installer.jar
  ( cd "$RUN" && "$JAVA" -jar /tmp/neoforge-installer.jar --installServer )
  rm /tmp/neoforge-installer.jar
fi

# --- mods, synced from the pack ---
echo ">> Syncing mods from pack..."
curl -fL "https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar" -o "$RUN/packwiz-installer-bootstrap.jar"
( cd "$RUN" && "$JAVA" -jar packwiz-installer-bootstrap.jar -g -s server "$PACK_URL" )

# --- config files ---
echo "eula=true" > "$RUN/eula.txt"
[[ -f "$RUN/server.properties" ]] || cp "$ROOT/server/server.properties" "$RUN/server.properties"

# datapacks (guided progression, etc.) into the world dir
mkdir -p "$RUN/world/datapacks"
for d in "$ROOT"/server/datapacks/*/; do
  [[ -d "$d" ]] && cp -r "$d" "$RUN/world/datapacks/"
done
cat > "$RUN/user_jvm_args.txt" <<EOF
-Xms${SERVER_XMS}
-Xmx${SERVER_XMX}
-XX:+UseG1GC
-XX:+ParallelRefProcEnabled
-XX:MaxGCPauseMillis=200
-XX:+UnlockExperimentalVMOptions
-XX:G1NewSizePercent=30
-XX:G1MaxNewSizePercent=40
-XX:G1HeapRegionSize=8M
-XX:G1ReservePercent=20
-XX:InitiatingHeapOccupancyPercent=15
EOF

echo ""
echo ">> Done. Start manually with:   bash server/start.sh"
echo ">> Or install the service:      bash server/install-service.sh"
