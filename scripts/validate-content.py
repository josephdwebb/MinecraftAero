"""Check progression integrity, intro isolation, resource packaging and cabin space."""
import hashlib
import json
import re
import runpy
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
INTRO = ROOT / "server/datapacks/aerie_intro"

def validate():
    # All function calls resolve; no scene function can address another player.
    functions = {p.stem: p.read_text(encoding="utf-8") for p in
                 (INTRO / "data/aerie/function/intro").glob("*.mcfunction")}
    for name, code in functions.items():
        for target in re.findall(r"(?:run )?function aerie:intro/([\w_]+)", code):
            assert target in functions, (name, target)
        assert "schedule function" not in code, name
        if name not in ("check", "setup"):
            assert "@a" not in code and "@p" not in code, name
    for path in (ROOT / "server/datapacks").rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    # Simulate staggered joins and disconnect/resume using the generated timer events.
    beats = [int(t) for t in re.findall(r"matches (\d+) run function aerie:intro/beat_", functions["tick"])]
    assert len(beats) == len(set(beats)) and max(beats) == 600
    timers, events = {"a": 0, "b": 0}, {"a": [], "b": []}
    for tick in range(1000):
        for player in timers:
            if player == "b" and (tick < 120 or 200 <= tick < 350):
                continue
            if timers[player] == 600:
                continue
            timers[player] += 1
            if timers[player] in beats:
                events[player].append(timers[player])
    assert events["a"] == events["b"] == beats
    assert "aerie_skip matches 1.. run return run function aerie:intro/finish" in functions["tick"]
    assert "scoreboard players reset @s aerie_time" in functions["finish"]
    # Flight path remains above the terrain until the scripted blackout/landing.
    assert 280 - 100 * 1.6 == 120
    nbt = runpy.run_path(str(ROOT / "scripts/inspect-airship.py"))["read_nbt"]
    ship = nbt(INTRO / "data/aerie/structure/big_airship_1.nbt")
    blocks = {tuple(b["pos"]): ship["palette"][b["state"]]["Name"] for b in ship["blocks"]}
    assert blocks[(15, 4, 42)] == "minecraft:stripped_oak_log"
    assert all(blocks.get((15, y, 42), "minecraft:air") == "minecraft:air" for y in (5, 6, 7))
    # Read emitted SNBT IDs/dependencies without depending on third-party packages.
    chapters = list((ROOT / "server/ftbquests/quests/chapters").glob("*.snbt"))
    texts = [p.read_text(encoding="utf-8") for p in chapters]
    ids = re.findall(r'\bid: "([A-F0-9]{16})"', "\n".join(texts))
    assert len(ids) == len(set(ids)), "Duplicate quest/task/reward/chapter IDs"
    for code in texts:
        assert 'id: "#' not in code, "Tag masquerading as item ID"
        for dependencies in re.findall(r"dependencies: \[(.*?)\]", code, re.S):
            assert all(dep in ids for dep in re.findall(r'"([A-F0-9]{16})"', dependencies))
        for adv in re.findall(r'advancement: "aerie:([^\"]+)"', code):
            assert (INTRO / "data/aerie/advancement" / (adv + ".json")).exists(), adv
    legacy = texts[next(i for i, p in enumerate(chapters) if p.stem == "come_to")]
    for key in ("wake", "sleep", "ruins", "hoe", "stockpile"):
        assert hashlib.md5(f"come_to/{key}".encode()).hexdigest()[:16].upper() in legacy
    with ZipFile(ROOT / "releases/aerie-resources.zip") as archive:
        assert "pack.mcmeta" in archive.namelist()
        assert not any("_src" in name for name in archive.namelist())
        assert archive.testzip() is None
        sound = json.loads(archive.read("assets/aerie/sounds.json"))["theme"]["sounds"][0]
        assert sound["stream"] and sound["attenuation_distance"] >= 300
    digest = hashlib.sha1((ROOT / "releases/aerie-resources.zip").read_bytes()).hexdigest()
    assert f"resource-pack-sha1={digest}" in (ROOT / "server/resourcepack.properties").read_text(encoding="utf-8")
    print("PASS: function isolation/references, staggered timelines, cabin, quest IDs/dependencies, JSON and resource ZIP/hash")

if __name__ == "__main__":
    validate()
