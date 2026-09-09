#!/usr/bin/env bash
# Starts the server in the foreground (systemd uses this too).
set -euo pipefail
RUN="$(cd "$(dirname "$0")/.." && pwd)/server/run"
export PATH="$RUN/jdk/bin:$PATH"
cd "$RUN"
exec ./run.sh nogui
