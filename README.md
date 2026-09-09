# Aero Server

A small survival Minecraft server for ~5 friends, built around **Create** and
**Create: Aeronautics**, with schematics enabled (Create's built-in Schematic Table /
Schematicannon — survival-balanced, materials still required).

- **Minecraft 1.21.1 · NeoForge** (dictated by Create: Aeronautics, which is 1.21.1-only)
- One mod list, in `scripts/modlist.txt`, published via **packwiz** to this repo.
- Players use **Prism Launcher**; mods sync to match the server on every launch.
- Server runs on a Raspberry Pi 5 (arm64).

## Layout

| Path | What |
|---|---|
| `aero.config` | Your settings — **edit this first** (GitHub repo, memory). |
| `scripts/modlist.txt` | The mod list. Edit here, then rebuild. |
| `scripts/build-pack.ps1` | Builds/updates `pack/` from the mod list (run on Windows). |
| `scripts/build-prism-instance.ps1` | Builds `dist/AeroServer-Prism.zip` for friends. |
| `pack/` | Generated packwiz files — committed, served to clients + server. |
| `server/setup.sh` | One-time Pi setup (JDK 21, NeoForge, mods, configs). |
| `server/start.sh` | Run the server. |
| `server/install-service.sh` | systemd unit (boot start + crash restart). |
| `server/update.sh` | Pull latest mod list + re-sync + restart. |
| `PLAYER_SETUP.md` | Send this to friends with the zip. |

## First-time build (on your Windows PC)

1. Create a **public** GitHub repo, e.g. `you/aero-server`. Set `GITHUB_REPO` in `aero.config`.
2. `powershell -ExecutionPolicy Bypass -File scripts\build-pack.ps1`
3. `git add -A && git commit -m "initial pack" && git push`
4. `powershell -ExecutionPolicy Bypass -File scripts\build-prism-instance.ps1`
5. Upload `dist/AeroServer-Prism.zip` + `PLAYER_SETUP.md` to Discord.

## First-time server setup (on the Pi)

```bash
sudo apt update && sudo apt install -y git curl
git clone https://github.com/you/aero-server && cd aero-server
nano aero.config                 # match GITHUB_REPO; tune SERVER_XMX if needed
nano server/server.properties    # set a real rcon.password  (copied on first setup)
bash server/setup.sh
bash server/install-service.sh
```

### Making it reachable over the internet

The Prism instance connects to `SERVER_ADDRESS` from `aero.config`. That hostname must
resolve to your home's public IP. Pick one:

**A. DuckDNS + port forward (recommended, lowest latency)**
1. Sign in at https://www.duckdns.org with a Google/GitHub account, create a subdomain
   (e.g. `joe-losertown`). Put `joe-losertown.duckdns.org` in `aero.config` → `SERVER_ADDRESS`.
2. On the Pi, add a cron job to keep the record pointed at your IP:
   ```
   ( crontab -l 2>/dev/null; echo '*/5 * * * * curl -sk "https://www.duckdns.org/update?domains=joe-losertown&token=YOUR_DUCKDNS_TOKEN&ip=" >/dev/null' ) | crontab -
   ```
3. Forward **TCP 25565** on your router to the Pi's LAN IP. Keep **25575** (RCON) LAN-only.

**B. playit.gg (no router config; adds a small latency hop)**
Install the playit agent on the Pi, create a Minecraft tunnel, use the address it gives
you as `SERVER_ADDRESS`. No port forwarding needed.

After changing `SERVER_ADDRESS`, re-run `build-prism-instance.ps1` and re-share the zip.
Whitelist friends: `journalctl` won't take input — use RCON, or temporarily run
`bash server/start.sh` in a terminal and type `whitelist add <name>`.

## Updating mods later

```
# Windows:
scripts\build-pack.ps1  ->  git commit -am "update" && git push
# Pi:
bash server/update.sh
```
Players get the new mods automatically on their next launch. No new zip needed unless
the Minecraft or NeoForge version changes.

## Tuning for the Pi

- `aero.config` → `SERVER_XMX` (5G ceiling on a 8GB Pi; drop to 4G if the OS gets tight).
- After first run, edit `server/run/config/create-server.toml` to cap contraption size
  and set schematic limits (`maxSchematics`, `maxTotalBytes`) if players get carried away.
- `chunky` isn't bundled; if exploration lags, add `modrinth chunky` to the mod list and
  pre-generate spawn.
