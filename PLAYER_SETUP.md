# Joining the Aero Server (one-time setup, ~3 minutes)

You'll use **Prism Launcher** instead of the normal Minecraft launcher for this server.
It logs in with your same Microsoft/Mojang account and keeps the mods up to date for
you automatically — you never download or manage mods yourself.

## Steps

1. **Install Prism Launcher** — https://prismlauncher.org (Windows/Mac/Linux). Open it
   and add your Microsoft account when prompted.
2. **Import the pack** — download `AeroServer-Prism.zip` (from our Discord), then in
   Prism: **Add Instance → Import from zip →** pick that file → **OK**.
3. **First launch** — select the "Aero Server" instance and click **Play**. The first
   launch downloads Minecraft, NeoForge, and the mods (a minute or two). Later launches
   are fast, and mods re-sync automatically whenever the server's list changes.
4. **Connect** — Multiplayer → **Losertown** is already in the list. Join it.

Tell Joe your exact Minecraft username so he can whitelist you (the server is
whitelist-only — you'll get "not white-listed" until he adds you).

## In-game basics

- **L** — advancements screen. There's a full Create → Aeronautics guide tree; follow it.
- **Xaero's minimap** (top-left) — press **U** for the fullscreen map, **B** to drop a
  waypoint. Death markers appear automatically so you can walk back to your stuff.
- Keep-inventory is ON — falling off an airship won't cost you your gear.

## Distant Horizons quirks

- **Nearby water invisible while far water shows?** DH is over-culling. Options → Distant
  Horizons → Advanced → Graphics → **Overdraw Prevention → 0 / Disabled**. Also try
  **Transparency → Fast**.
- **Grainy mid-distance ground?** Same menu → **Noise Texture → Off**.

## If the game runs badly

Your laptop is probably struggling with **Distant Horizons** (the far-terrain view).
It's optional — the server doesn't need it. Press **Options → Distant Horizons**:

- **LOD Render Distance → 32–48** (down from default)
- **Quality preset → Minimum**
- or just **disable Distant Horizons** entirely — everything else still works.

Also in normal Video Settings: Render Distance 6–8, Graphics "Fast".

## Notes

- Always launch from **Prism** for this server. Your normal launcher still works for
  everything else.
- If a launch ever fails right after an update, click Play again — the sync finishes
  and the second launch works.
- Requires Java? No — Prism handles it.
