# Arrival and field journal update

The intro now runs for 600 ticks (30 seconds at 20 TPS), with an independent
`aerie_time` for each player. Joining midway cannot restart another player's
scene. Disconnecting pauses that player's timer; rejoining resumes it. Music
cannot seek to a saved position after reconnecting, so that case may be silent.
There is no rotation jitter, nausea or accumulated spin. A spectator camera
holds the cabin position, follows a five-second descent outside the hull, then
holds at the landing while the player recovers. Darkness is a vignette, not a
fully black screen. The previous gamemode is restored at the end or on skip.

- Cabin: `-69.5 275 -129.5`, facing north. Structure NBT has a stripped-oak floor
  at `-70 274 -130` and air at feet/head height.
- Fall starts at `-48 280 -108`, outside the ship's east edge. It ends at Y=120.
- Landing: `-70 76 -108` (existing handoff location; no terrain edits).
- Player skip: `/trigger aerie_skip`, also offered as clickable chat text.
- Operator replay: `/scoreboard players set PLAYER aerie_intro 0`.
- Operator recovery: `/execute as PLAYER run function aerie:intro/finish`.
- Existing completed players (score 3) are not replayed automatically.
- A fresh world needs an operator to run `/function aerie:intro/place_airship`.
  Reload no longer automatically pastes a structure over existing builds.

Chapter I retains its 35 quest IDs. Shelter, farming and mining now branch
early, stone-tool progression only requires a pickaxe, and the Create bridge
requires a bed/sleep, bread and an iron pickaxe. Optional combat, livestock,
armour and exploration remain available. Chapter II adds 15 quests leading
through Ponder, water power, shafts/cogs, casings, pressing, milling, mixing,
a practical workshop check and planning a hangar. Rewards stay modest.

Tag tasks use hidden vanilla inventory advancements, preserving the original
task IDs. Any matching type works, but the requested count must be in one
stack (e.g. three wool of one colour); supplies are not consumed. The sleep
task uses the vanilla sleep advancement. Previously completed quests remain
completed even where requirements have changed. FTB Teams sharing still
applies. Claiming the Chapter I title reward targets the claiming player and
uses the installed version's `permission_level` field.

## Build and verify

```text
python scripts/build-intro.py
python server/ftbquests/_generate.py
python scripts/build-resourcepack.py
python scripts/validate-content.py
```

The downloadable ZIP is `releases/aerie-resources.zip`, with `pack.mcmeta` at
its root. Music streams with an extended attenuation distance. The build
updates the SHA-1 and public URL in the separate, credential-free
`server/resourcepack.properties`. Rebuild whenever assets
change, and publish the ZIP before deploying its new settings.

## Deploy on the Pi

After pushing the source and resource ZIP, pull the repo on the Pi. With no
players online:

```bash
python3 server/deploy-content.py
sudo systemctl restart aero-server
```

Deployment checks the hosted ZIP hash before changing anything, backs up
definitions, progress directories and current properties under
`server/run/content-backups/TIMESTAMP`, and changes only the four resource-pack
properties. It never replaces the full live properties file. Player/world
progress stays in place. The datapack reloads immediately; this server rejects
FTB administrative reloads over RCON, so the restart loads quests as well as
activating required resource-pack delivery. The sudo password must be entered
in the owner's terminal. Never put it in a script or chat.

The pack URL is GitHub raw with a content hash query string. After restart,
join, accept/download the required pack, and keep Music & Sounds >
Jukebox/Note Blocks audible. Server commands cannot override a muted slider.

## Acceptance pass

1. Check `latest.log` after restart for failed functions/advancements, missing
   items or FTB quest import errors. Expect 50 quests across two chapters.
2. Replay on a test account. Check cabin framing, the east-side exit, landing
   clearance, readable title timing, music and a safe return to survival.
3. Repeat with two players joining five seconds apart. Each should have their
   own attack/fall/wake timing. Skip on one must not affect the other.
4. Disconnect during the fall and reconnect. Verify completion and no stuck
   spectator state. Test skip during the cabin, fall and wake sections.
5. On an unfinished quest, collect spruce logs/planks, a non-white bed and any
   hoe; confirm completion without consumption. Check the journal's branches,
   reward quantities and Create chapter visibility.

Static validation covers references, JSON, IDs, dependencies, staggered timer
simulation, structure clearance and ZIP/hash integrity. A live datapack reload
checks Minecraft's parser. Client visuals/audio and FTB acceptance still need
the restart and in-game acceptance pass above.

## Rollback

Stop the service, choose the pre-update timestamp in `content-backups`, move
the current intro/quest definition directories aside, and copy that backup's
`aerie_intro`, `quests`, and `server.properties` to their original locations.
Restart. Progress backups are for recovery only; do not overwrite newer player
progress as part of a routine content rollback.

Format reference: [FTB Quests upstream](https://github.com/FTBTeam/FTB-Quests).
The installed 2101.1.35 jar serializers were also inspected for reward fields.
