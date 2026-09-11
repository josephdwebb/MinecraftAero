"""Back up and deploy intro/quests; update resource settings after verifying hosting.

Run on the Pi: python3 server/deploy-content.py
The resource settings take effect after a service restart. No world blocks are edited.
"""
import argparse
import hashlib
import shutil
import time
import urllib.request
from pathlib import Path
from rcon import command, properties

def deploy(run, content_only=False):
    root = Path(__file__).resolve().parents[1]
    run = run.resolve(strict=True)
    online = command("list", run)
    if not online.startswith("There are 0 of"):
        raise RuntimeError("Wait until the server is empty before replacing quest definitions: " + online)
    source_props = properties(root / "server/resourcepack.properties")
    if not content_only:
        with urllib.request.urlopen(source_props["resource-pack"], timeout=30) as response:
            digest = hashlib.sha1(response.read()).hexdigest()
        if digest != source_props["resource-pack-sha1"]:
            raise RuntimeError("Hosted resource pack does not match the configured SHA-1")
    backup = run / "content-backups" / time.strftime("%Y%m%d-%H%M%S")
    backup.mkdir(parents=True, exist_ok=False)
    targets = [(root / "server/datapacks/aerie_intro", run / "world/datapacks/aerie_intro"),
               (root / "server/ftbquests/quests", run / "config/ftbquests/quests")]
    # Back up definitions AND progress. Keep world/ftbquests in place throughout.
    shutil.copy2(run / "server.properties", backup / "server.properties")
    for name in ("ftbquests", "ftbteams", "advancements"):
        path = run / "world" / name
        if path.exists():
            shutil.copytree(path, backup / ("world-" + name))
    for source, target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.rename(backup / target.name)
        shutil.copytree(source, target)
    if not content_only:
        keys = ("resource-pack", "resource-pack-sha1", "require-resource-pack", "resource-pack-prompt")
        path = run / "server.properties"
        lines = [line for line in path.read_text().splitlines() if line.split("=", 1)[0] not in keys]
        path.write_text("\n".join(lines + [f"{key}={source_props[key]}" for key in keys]) + "\n")
    print("Backup:", backup)
    print(command("reload", run))
    quest_result = command("ftbquests reload quests", run)
    print(quest_result)
    if "Incorrect argument" in quest_result or "Unknown" in quest_result:
        print("Quest definitions are staged; this server rejects FTB administrative commands over RCON. Restart to load them.")
    print("Datapack reload requested. Check latest.log for reload errors.")
    if not content_only:
        print("Restart aero-server to activate required resource-pack delivery.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=Path(__file__).resolve().parent / "run")
    parser.add_argument("--content-only", action="store_true", help="Leave resource-pack properties unchanged")
    args = parser.parse_args()
    deploy(args.run, args.content_only)
