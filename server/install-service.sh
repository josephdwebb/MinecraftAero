#!/usr/bin/env bash
# Installs a systemd service so the server starts on boot and restarts on crash.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
USER_NAME="$(id -un)"

sudo tee /etc/systemd/system/aero-server.service > /dev/null <<EOF
[Unit]
Description=Aero Minecraft Server (Create + Aeronautics)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${USER_NAME}
WorkingDirectory=${ROOT}
ExecStart=/usr/bin/env bash ${ROOT}/server/start.sh
Restart=on-failure
RestartSec=10
SuccessExitStatus=0 143

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now aero-server
echo ">> Running. Logs:  journalctl -u aero-server -f"
echo ">> Console:      (install 'tmux'/rcon, or use: journalctl for read-only)"
