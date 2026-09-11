# Outlands of Aerie — Server Handoff / Context Dump

> **2026-09-11 update:** Intro and quests were revised after this snapshot.
> Read [server/CONTENT_UPDATE.md](server/CONTENT_UPDATE.md) first for current
> timings, coordinates, quest changes, resource-pack delivery and deployment.
> The historical cutscene implementation below has been replaced.

A Minecraft Java survival server for ~5 friends, self-hosted on a Raspberry Pi 5,
built around Create + Create: Aeronautics. This doc is a complete state snapshot
for another assistant to pick up work — especially the broken arrival cutscene.

## Infrastructure

- **Host:** Raspberry Pi 5, 8 GB RAM, Debian 13 (trixie), aarch64, hostname `RaspberryPi5`.
  Also runs (on the same box, competing for RAM/CPU): a Docker media stack
  (Jellyfin, Sonarr, Radarr, Prowlarr, Jellyseerr, flaresolverr, gluetun VPN —
  qBittorrent is permanently stopped), a Node "ymerra" site, a cloudflared tunnel,
  and a Discord bot called **Sinerva** (Python, `~/sinerva/venv`, not yet integrated
  with the MC server).
- **Repo:** `github.com/josephdwebb/MinecraftAero` (public). Cloned at
  `~/MinecraftAero` on the Pi and `C:\Users\Joe\Desktop\Minecraft Aero Server` on
  the owner's Windows PC. All server config, scripts, and datapacks live here —
  treat it as the source of truth; the `server/run/` directory on the Pi is the
  live, gitignored server instance.
- **Server process:** systemd service `aero-server`
  (`ssh ymerra 'sudo systemctl restart aero-server'` — sudo needs a password,
  cannot be run non-interactively). Working dir `~/MinecraftAero/server/run/`.
  JVM: `-Xms2G -Xmx5G -XX:+UseZGC -XX:+ZGenerational` (ZGC chosen over G1 —
  Distant Horizons, when it was installed, warned against G1's pause times;
  kept ZGC after removing DH too).
- **RCON:** `127.0.0.1:25575`, password `ilovegian` (yes, it's in the public
  repo's `server/server.properties` — accepted risk since RCON isn't
  port-forwarded, LAN/localhost only).
- **Public access:** DuckDNS `joe-losertown.duckdns.org` (cron refreshes every
  5 min with the account's token), router port-forward TCP 25565 → the Pi.
  Legacy name "joe-losertown" predates the "Outlands of Aerie" rebrand — cosmetic
  only, never renamed.
- **Distribution to players:** packwiz pack (`pack/` in repo) served via GitHub
  raw URLs; players use **Prism Launcher** with `packwiz-installer-bootstrap.jar`
  as a pre-launch command, so mods auto-sync on every launch. `scripts/build-pack.ps1`
  (Windows) adds/updates mods from `scripts/modlist.txt`.
- **Backups:** `server/backup.sh`, daily 5:30am cron, keeps 7, in `~/aero-backups/`
  on the Pi. RCON save-off/save-all/save-on wrapped around a tar.
- **World edits often need going around the live server** because WorldEdit ops
  large enough to matter (tens of millions of blocks) reliably **OOM the 5 GB
  heap** — see "Known landmines" below.

## Minecraft version & full mod list

**Minecraft 1.21.1, NeoForge 21.1.250.** Pinned there because Create: Aeronautics
only exists for 1.21.1 — this dictates everything else. World seed:
`-7833842402223417925`.

| Mod | Notes |
|---|---|
| Create 6.0.10 | core |
| Create: Aeronautics 1.3.2 (+ Sable 2.0.5) | core; Sable is Aeronautics' physics engine (Rapier), jarjar'd |
| Lithium, FerriteCore, ModernFix | server perf |
| Chunky | server-side, spawn pregen |
| Sodium, ImmediatelyFast, Dynamic FPS | client perf |
| Xaero's Minimap + World Map | client QoL |
| Doggy Talents Next 1.19.1 | wolf taming/leveling system |
| Critters and Companions 2.7.0 (+ GeckoLib, Architectury, YACL, CreativeCore) | small tameable critters (ferrets etc.) |
| AmbientSounds | client, dynamic ambience |
| Simple Economy 1.0.0 | currency backend (no shop UI yet — planned: villager traders) |
| FTB Quests + FTB Library + FTB Teams + Architectury | quest system |
| WorldEdit 7.3.8 | server-side, op-only, used for terrain/hub work |

**Removed/rejected, do not re-add without reason:**
- **Distant Horizons** + **EntityCulling** — caused water-invisible bugs, mob
  pop-in, blocky-flower artifacts, stutter, huge LOD-gen queue on the Pi. Pulled entirely.
- **Jade** — block-info tooltip the owner found annoying; removed in favor of
  vanilla Engineer's Goggles + Ponder for learning Create.
- **"Companions!" (`companions-mod`)** — turned out to be a magic-summon combat
  mod (Soul Mage, Shadow Sword, Croissant Dragon, Imps, a boss) misleadingly
  named; wrong tone entirely. Swapped for Critters and Companions.
- **SDM Shop** — crashed server boot (`ClassNotFoundException:
  net.sixik.sdmcore...`, a missing dependency not resolvable via
  Modrinth/packwiz). Dropped; the plan is a shop via locked villager traders
  instead (not yet built).

## World state

- **Hub build:** a PlanetMinecraft "Spawn Village & Palace 400×368" schematic
  (`server/hub/HubBlaze.schem`, Sponge v2, DataVersion 3465 = native 1.21.1, all
  vanilla blocks, no license/attribution required per the listing).
  - **It was NOT pasted with WorldEdit** — a live `//paste` of ~27M blocks OOM'd
    the server. Instead it was placed with a **custom offline Python script**
    (`server/hub_paste.py` — reference it if it still exists, otherwise it was
    ephemeral/scratchpad; the logic: parse the Sponge schematic, for every
    column in its footprint write the schematic block if solid, else seal with
    stone up to a floor height, else air) that edits the Anvil `region/*.mca`
    files directly while the server is stopped. Placed centered near
    (-46, -64) with **floor/base at Y=62**.
  - Left ugly seams (flat stone walls, popcorn-smooth terrain) where the paste
    met existing hills — the owner used **WorldPainter** (external tool) to
    merge/reshape terrain after the fact, uploading the edited `region/` +
    `entities/` files back over SCP, then also did manual **in-game WorldEdit
    brush work** (`//br smooth`, `//br sphere <pattern>`, `//br overlay`) to
    texture and blend the mountainside. `max-brush-radius` was raised from the
    default 6 to 25 in `config/worldedit/worldedit.properties` for this.
  - **Terrain is real, generated, and quite mountainous/hilly** near spawn —
    no large flat areas exist within a few hundred blocks. This matters for
    any future structure placement.
- **Airship structure** (`server/datapacks/aerie_intro/data/aerie/structure/big_airship_1.nbt`):
  a second, separate build used only for the arrival cutscene. DataVersion 3955
  (built in MC **1.21.4**, one version newer than this server — some
  block-state drift is possible but wasn't observed as a problem). Uses
  namespaces `create`, `aeronautics`, `simulated` (all present) and
  `enchanted-vertical-slabs` (**not installed** — those specific blocks silently
  become air on placement; cosmetic gaps only, not investigated further).
  Placed via `/place template aerie:big_airship_1 -85 270 -172` — size
  `[35, 40, 80]` (X, Y, Z), so it spans roughly X -85..-50, Y 270..310,
  Z -172..-92. World build-height ceiling is **Y 320** — this is why it's not
  higher up despite an earlier ask for Y=700 (invalid, above the ceiling).
- Real ground surface at (-70, -108) — the intro's landing spot — was probed
  and found to be **Y=75** (walkable at Y=76). An earlier requested Y=-76 was
  invalid (below the world floor of Y=-64) and was corrected.

## Datapacks (`server/datapacks/` in repo → deployed to `world/datapacks/` on the live server)

1. **`losertown_progression`** — 23 vanilla advancements forming a Create/Aeronautics
   tech-tree (namespace `losertown`, a legacy name from before the "Outlands of
   Aerie" rename — never renamed, harmless since it's an internal ID). Uses
   `minecraft:inventory_changed` triggers on items like `create:andesite_alloy`,
   `aeronautics:propeller_bearing`, etc.
2. **`losertown_rules`** — sets gamerules on load: `keepInventory true`,
   `playersSleepingPercentage 50`, `announceAdvancements true`.
3. **`aerie_intro`** — **the arrival cutscene. Currently broken/unsatisfying — see below.**

Also: **FTB Quests Chapter 1 "Come To"** (35 quests, `server/ftbquests/quests/`,
generated by `server/ftbquests/_generate.py`, deployed to
`config/ftbquests/quests/` — NOT the `world/` dir, that's just per-player
progress) — a full vanilla-survival arc (wood → tools → shelter → iron →
farming → bread → "What the Old World Left" which is meant to bridge into a
not-yet-built Create-focused Chapter 2). IDs are deterministic hashes of a
string key so regenerating the script preserves quest dependency chains.
Untested for whether FTB Quests accepted the `#minecraft:logs`-style tag
syntax in item tasks — worth checking the log for quest-load warnings.

## The broken piece: `aerie_intro` cutscene

**Intent:** first-ever join → player wakes in a dark airship cabin high above
the world → engine-hum ambience + title cards ("The engines strain against the
wind." / "Outlands of Aerie" / "the frontier at the top of the world") →
"under attack": explosion sounds, particles, camera shake, "WE'RE HIT" →
"HULL BREACH" → a **scripted 9-second fall** (not real gravity — the player is
put in spectator and moved down by script so the timing is exact regardless of
real physics/height) → **blackout** (blindness + darkness effects
approximating a black screen, since vanilla has no true screen-black command)
→ teleport to the real landing spot while still "blacked out" → amnesia lines
fade in ("Where... am I?" / "Nothing looks familiar." / "Whatever happened,
you're on your own now.") → vision clears, gamemode set to survival, Chapter 1
quest is live.

**Mechanism:** a scoreboard `aerie_intro` (per player) drives a linear state
machine: 0 = never started, 1 = mid-cutscene, 3 = done (2 is unused/skipped).
`data/minecraft/tags/function/tick.json` runs `aerie:intro/check` every tick,
which does `scoreboard players add @a aerie_intro 0` (idempotent init) then
triggers `aerie:intro/start` for anyone still at 0. `start` sets the score to 1
and does the first teleport/effects directly (this part works, since it's
invoked via `execute as <player> at @s run function`, so `@s` is bound).
Everything after that is chained via `schedule function aerie:intro/<next> <ticks>`.

**Bug #1 (found and fixed):** `/schedule function` runs the target function
with **no entity/position context at all** — inside a scheduled function,
`@s` matches nothing. So every subsequent step's `title @s ...`,
`effect give @s ...`, `tp @s ...` etc. were silently no-ops (no error is
logged when a targeted command matches zero entities — it just does nothing).
Symptom matched exactly: player teleported into the airship (from `start`,
which worked) and then **nothing else ever happened** — no titles, no sounds,
no scripted fall — so the player jumped out under their own power and took
fall damage / respawned normally.

**Fix applied:** every line in `title1`, `title2`, `attack1`, `shake_a`,
`shake_b`, `fall_start`, `fall_tick`, `blackout`, `wake1`–`wake4`
that needs `@s` now wraps it: `execute as @a[scores={aerie_intro=1}] at @s run
<original command>`. Commands that accept a selector natively (`tp`,
`gamemode`, `scoreboard players set/remove`) target
`@a[scores={aerie_intro=1}]` directly instead of `@s`. This is a standard
datapack gotcha (scheduled/tick-tag functions lose context) — if debugging
further broken behavior, **assume every `@s` in a function reached via
`schedule` or a bare tag is suspect unless it's wrapped in `execute as/at`.**

**Current status:** after the fix + `/reload` + clearing any stale
`schedule` entries (`schedule clear aerie:intro/<name>` for all 12 step
functions — none were found pending, for what that's worth) + resetting the
test account's `aerie_intro` score to 0, the owner ran it again and reported
**"still really bad"** without specifics. One data point: right before writing
this doc, the account's score read **3** (= completed), meaning the full
chain now runs end-to-end — so the remaining problem is likely about *feel*
(pacing, camera-shake quality, sound choices, timing gaps, jarring transitions)
rather than a hard failure, but this has not been confirmed with the owner.

**Suspects worth checking next, roughly in order of likelihood:**
1. **The camera-shake implementation is crude and may feel bad, not "shaky."**
   It works by teleporting the player with a large *relative* rotation delta
   (`tp @s ~ ~ ~ ~20 ~-10`) alternating direction every 3 ticks, 8 times. This
   is a hard snap-to-new-angle each time, not a smooth oscillation — it may
   read as disorienting teleport-snaps rather than a shake, or (worse) as
   nauseating in a bad way. Vanilla Minecraft has **no real camera-shake
   primitive**; consider smaller deltas, more frequent smaller ticks, or
   accepting a different effect (e.g., just particles + sound + the nausea
   effect, no rotation jitter).
2. **Timing may be off / feel too slow or too fast.** All step delays are
   hardcoded tick counts across ~12 files — e.g. title1 fires 60 ticks (3s)
   after start, title2 70 ticks (3.5s) after that, attack1 70 ticks after
   that, etc. The 9-second fall is `aerie_fall` counting down from 180 with
   one `tp @s ~ ~-1.1 ~ ~1 ~` per tick (also spins the player slowly via the
   `~1` yaw delta each tick — over 180 ticks that's a full 180° of accumulated
   spin, which may feel wrong/nauseating on its own).
3. **The "blackout" is blindness+darkness effects, not a true black screen** —
   vanilla can't fully black the screen. If the owner expected literal black
   and is instead seeing a dark vignette with the world still dimly visible,
   that will read as "not working" even though it's functioning as coded.
4. **`gamemode spectator` during the fall** removes the player's own body/
   collision — check whether this looks/feels right (no player model, can the
   camera clip through the airship hull on the way out, etc.).
5. Confirm the **airship's interior** actually has a sensible room at
   (-68, 285, -132) — this point was chosen by *centering* the 35×40×80
   structure under the originally-requested coordinate, without knowing the
   structure's actual interior layout. It's plausible the player spawns in a
   wall, a service corridor, or an oddly-shaped space rather than a proper cabin.
6. Sound choices are placeholders (`minecraft:entity.generic.explode`,
   `minecraft:entity.enderdragon.flap` for wind, `minecraft:entity.player.big_fall`
   for the landing thud) — may not sell the intended mood.
7. Custom music (`aerie:theme`, from `resourcepack/assets/aerie/sounds/theme.ogg`
   + `resourcepack/assets/aerie/sounds.json`) **requires the resource pack to
   be active on the client to play at all** — and the resource pack is **not
   yet hosted/required** via `server.properties` (`resource-pack` /
   `resource-pack-sha1` / `require-resource-pack` are unset). If the pack isn't
   being served, `playsound aerie:theme ...` calls fail silently (unknown
   sound event) — this alone could make the whole thing feel broken/empty,
   since the music is a big part of the intended atmosphere. **Check this
   first** — it's an easy, high-impact miss.

**Files:** `server/datapacks/aerie_intro/data/aerie/function/intro/*.mcfunction`
(one file per step, named `setup`, `check`, `place_airship`, `start`, `title1`,
`title2`, `attack1`, `shake_a`, `shake_b`, `fall_start`, `fall_tick`,
`blackout`, `wake1`-`wake4`). Deploy flow: edit locally → commit/push → on the
Pi, `rm -rf server/run/world/datapacks/aerie_intro && cp -r
server/datapacks/aerie_intro server/run/world/datapacks/` → RCON `reload`
(no server restart needed for datapack-only changes) → RCON
`scoreboard players set <name> aerie_intro 0` to re-arm a test.

## Branding

- **Name:** "Outlands of Aerie". Tagline: "Nowhere to go but up."
- **MOTD** (`server.properties`): `§6§lOutlands of Aerie§r §8§l|§r §7Nowhere to go but up`
- **Palette:** brass `#C9A227`, weathered copper `#4E8D7C`, twilight indigo
  `#1B2A4A`, ember `#E8763A`, canvas `#EFE6D2`, iron `#3A3F44`.
- **Voice:** weathered/practical frontier-aviation tone, not high fantasy.
- **Resource pack** (`resourcepack/` in repo) exists but is **not yet hosted or
  required by the server** — this is the single biggest unfinished piece
  blocking both the music and any visual branding (loading screen, title
  panorama) from actually reaching players. Contains: `assets/aerie/sounds.json`
  + `theme.ogg` (the custom music, converted from an mp3 with ffmpeg), and
  `_src/*.png` (5 promo screenshots of the hub build, converted from webp,
  intended for the join/loading-screen background — not yet wired in, and
  they carry a faint "Activate Windows" watermark that needs cropping).
- Player-facing docs (`PLAYER_SETUP.md`) still reference the old "Losertown"
  branding in places — not fully updated.

## Known landmines / hard constraints

- **The Pi cannot handle large live WorldEdit operations.** Anything
  approaching tens of millions of blocks (a `//set` over a big cuboid, a
  `//paste` of a large schematic) will OOM the 5 GB heap and crash the server.
  Prefer: small brush operations (radius ≤ ~12), or offline region-file editing
  with the server stopped, or breaking large operations into chunks with the
  server otherwise idle.
- **`sudo` on the Pi requires an interactive password** — no automation can
  start/stop/restart the systemd service or run other root commands
  unattended; a human has to run those specific commands.
- **NeoForge enforces exact mod-list matching** between client and server —
  any mod add/remove/version bump must be synced to *both* (packwiz handles
  this for players automatically on next launch; the server needs an explicit
  `packwiz-installer-bootstrap.jar -s server` run + restart).
- **GitHub raw URLs can serve briefly stale content** (CDN edge caching) —
  if a `packwiz-installer` sync errors on a 404 for a file you just removed
  from the repo, it's likely edge-cache staleness; retry after a minute or
  cache-bust the URL.
- **World build height is Y -64 to Y 320** in this version — don't place
  structures or teleport players outside that range.
- **Only vanilla WorldEdit is available** — FastAsyncWorldEdit, GoBrush, and
  GoPaint are all Paper/Spigot-only and do not have NeoForge builds. No true
  terrain-erosion brush exists here; `//smooth` / `//br smooth` (Gaussian
  blur on the heightmap) is the only smoothing tool, and it tends to produce
  a "blobby" look with too many iterations.
