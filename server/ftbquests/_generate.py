#!/usr/bin/env python3
"""Generates the FTB Quests definition for Outlands of Aerie.
Output: ./quests/  (chapter_groups.snbt, data.snbt, chapters/*.snbt)
Deploy: copy ./quests/ -> server/run/config/ftbquests/quests/  then restart.
IDs are deterministic (hash of a stable key) so regenerating keeps dependencies intact.
"""
import hashlib, os, pathlib, textwrap

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "quests"
GROUP_ID = "0AE71E00A11ED000"          # "Outlands of Aerie" group

def hid(key: str) -> str:
    return hashlib.md5(key.encode()).hexdigest()[:16].upper()

# ---------- SNBT writer ----------
def snbt(v, ind=0):
    pad = "\t" * ind
    if isinstance(v, dict):
        if not v:
            return "{ }"
        lines = ["{"]
        for k, val in v.items():
            lines.append(f"{pad}\t{k}: {snbt(val, ind+1)}")
        lines.append(pad + "}")
        return "\n".join(lines)
    if isinstance(v, list):
        if not v:
            return "[ ]"
        lines = ["["]
        for item in v:
            lines.append(f"{pad}\t{snbt(item, ind+1)}")
        lines.append(pad + "]")
        return "\n".join(lines)
    if isinstance(v, Raw):
        return v.s
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        esc = v.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{esc}"'
    return str(v)

class Raw:
    def __init__(self, s): self.s = s

def L(n):  # long literal
    return Raw(f"{n}L")
def D(n):  # double literal
    return Raw(f"{n}d")

# ---------- task / reward helpers ----------
_seq = [0]
def _tid(qkey, n):
    return hid(f"{qkey}/task/{n}")
def _rid(qkey, n):
    return hid(f"{qkey}/reward/{n}")

def t_item(qkey, n, item, count=1):
    d = {"id": _tid(qkey, n), "item": {"count": 1, "id": item}, "type": "item"}
    if count != 1:
        d["count"] = L(count)
    return d

def t_kill(qkey, n, entity, count=1):
    return {"id": _tid(qkey, n), "entity": entity, "type": "kill", "value": L(count)}

def t_adv(qkey, n, adv):
    return {"id": _tid(qkey, n), "type": "advancement", "advancement": adv, "criterion": ""}

def t_check(qkey, n, title):
    return {"id": _tid(qkey, n), "type": "checkmark", "title": title}

def t_dim(qkey, n, dim="minecraft:overworld"):
    return {"id": _tid(qkey, n), "dimension": dim, "type": "dimension"}

def r_item(qkey, n, item, count=1):
    return {"id": _rid(qkey, n), "count": count, "item": {"count": 1, "id": item}, "type": "item"}

def r_xp(qkey, n, xp):
    return {"id": _rid(qkey, n), "type": "xp", "xp": xp}

def r_cmd(qkey, n, cmd, title):
    return {"id": _rid(qkey, n), "type": "command", "command": cmd, "title": title, "player_command": False}

# ---------- Chapter 1 spec ----------
# each quest: key, title, [desc lines], icon, [tasks], [rewards], [dep keys], shape/size opt
Q = []
def quest(key, title, desc, icon, tasks, rewards, deps=(), shape=None, size=None):
    Q.append(dict(key=key, title=title, desc=list(desc), icon=icon,
                  tasks=tasks, rewards=rewards, deps=list(deps),
                  shape=shape, size=size))

V = "come_to"  # chapter key

quest("wake", "Come To",
      ["The world swims into focus. Cold ground. A splitting headache. The smell of pine and smoke.",
       "", "You don't know your name. You don't know this place. You don't know how you got here — only that you fell, and the sky was on fire.",
       "", "&7First things first. Get off the ground and &fpunch a tree&7."],
      "minecraft:oak_log",
      [t_item(V+"/wake", 0, "#minecraft:logs", 1)],
      [r_item(V+"/wake", 0, "minecraft:oak_log", 3), r_xp(V+"/wake", 1, 5)],
      shape="hexagon", size=1.5)

quest("planks", "Splinters", ["Break the logs down into planks. It's the start of everything."],
      "minecraft:oak_planks", [t_item(V+"/planks", 0, "#minecraft:planks", 4)],
      [r_xp(V+"/planks", 0, 3)], deps=["wake"])

quest("table", "A Place to Work", ["Four planks in a square. A crafting table lets you make everything else."],
      "minecraft:crafting_table", [t_item(V+"/table", 0, "minecraft:crafting_table", 1)],
      [r_item(V+"/table", 0, "minecraft:oak_planks", 4), r_xp(V+"/table", 1, 5)], deps=["planks"])

quest("sticks", "Sticks", ["Two planks stacked. You'll need a pile of these for tools and torches."],
      "minecraft:stick", [t_item(V+"/sticks", 0, "minecraft:stick", 8)],
      [r_xp(V+"/sticks", 0, 3)], deps=["table"])

quest("wpick", "Wooden Pickaxe", ["Three planks, two sticks. It won't last, but it'll get you stone."],
      "minecraft:wooden_pickaxe", [t_item(V+"/wpick", 0, "minecraft:wooden_pickaxe", 1)],
      [r_xp(V+"/wpick", 0, 5)], deps=["sticks"])

quest("waxe", "Wooden Axe", ["Chops wood faster than your fists. Your knuckles will thank you."],
      "minecraft:wooden_axe", [t_item(V+"/waxe", 0, "minecraft:wooden_axe", 1)],
      [r_xp(V+"/waxe", 0, 5)], deps=["sticks"])

quest("wsword", "Wooden Sword", ["Something moved in the trees. Arm yourself."],
      "minecraft:wooden_sword", [t_item(V+"/wsword", 0, "minecraft:wooden_sword", 1)],
      [r_xp(V+"/wsword", 0, 5)], deps=["sticks"])

quest("cobble", "Break Stone", ["Take the wooden pickaxe underground, or into the mountain. Bring back a stack of cobblestone."],
      "minecraft:cobblestone", [t_item(V+"/cobble", 0, "minecraft:cobblestone", 20)],
      [r_item(V+"/cobble", 0, "minecraft:bread", 1), r_xp(V+"/cobble", 1, 10)],
      deps=["wpick"])

quest("stonetools", "Stone Age",
      ["Cobblestone tools are the real starting kit. Make the set."],
      "minecraft:stone_pickaxe",
      [t_item(V+"/stonetools", 0, "minecraft:stone_pickaxe", 1),
       t_item(V+"/stonetools", 1, "minecraft:stone_axe", 1),
       t_item(V+"/stonetools", 2, "minecraft:stone_sword", 1),
       t_item(V+"/stonetools", 3, "minecraft:stone_shovel", 1)],
      [r_item(V+"/stonetools", 0, "minecraft:coal", 4), r_xp(V+"/stonetools", 1, 15)],
      deps=["cobble"], shape="square")

quest("furnace", "The Hearth", ["Eight cobblestone. A furnace smelts ore, cooks food, and bakes charcoal."],
      "minecraft:furnace", [t_item(V+"/furnace", 0, "minecraft:furnace", 1)],
      [r_xp(V+"/furnace", 0, 5)], deps=["stonetools"])

quest("light", "First Light",
      ["Mine coal (black flecks in stone) &7or&f smelt a log into charcoal. Either makes torches.",
       "", "Torch + stick. Never sleep in the dark again."],
      "minecraft:torch", [t_item(V+"/light", 0, "minecraft:torch", 8)],
      [r_item(V+"/light", 0, "minecraft:torch", 24), r_xp(V+"/light", 1, 10)],
      deps=["furnace"], shape="square")

# --- Act II ---
quest("door", "Seal It Off", ["Six planks. A door keeps the night where it belongs."],
      "minecraft:oak_door", [t_item(V+"/door", 0, "#minecraft:wooden_doors", 1)],
      [r_xp(V+"/door", 0, 5)], deps=["light"])

quest("nightfall", "Something Out There",
      ["It came with the dark. Put it down — kill two of whatever's clawing at your walls."],
      "minecraft:rotten_flesh",
      [t_kill(V+"/nightfall", 0, "minecraft:zombie", 2)],
      [r_item(V+"/nightfall", 0, "minecraft:arrow", 8), r_xp(V+"/nightfall", 1, 15)],
      deps=["door"], shape="square")

quest("wool", "Fleece", ["Find sheep. Shear them or cut them down — you need wool for a bed."],
      "minecraft:white_wool", [t_item(V+"/wool", 0, "#minecraft:wool", 3)],
      [r_xp(V+"/wool", 0, 5)], deps=["door"])

quest("bed", "Somewhere to Fall", ["Three wool, three planks. It's not much. It's yours."],
      "minecraft:red_bed", [t_item(V+"/bed", 0, "#minecraft:beds", 1)],
      [r_xp(V+"/bed", 0, 10)], deps=["wool"])

quest("sleep", "Rest",
      ["Place the bed. Right-click it after dark to sleep.",
       "", "&7When you wake, this is home — the world will bring you back here."],
      "minecraft:white_bed",
      [t_check(V+"/sleep", 0, "I slept in my bed and set my spawn")],
      [r_item(V+"/sleep", 0, "minecraft:cooked_beef", 3), r_xp(V+"/sleep", 1, 15)],
      deps=["bed"], shape="square")

quest("chest", "Somewhere to Keep It", ["Eight planks. Stop carrying your whole life in your pockets."],
      "minecraft:chest", [t_item(V+"/chest", 0, "minecraft:chest", 1)],
      [r_item(V+"/chest", 0, "minecraft:chest", 1)], deps=["sleep"])

# --- Act III: iron ---
quest("digdeep", "Dig Deeper",
      ["Iron hides as pale specks in stone, lower down. A stone pickaxe will break it.",
       "Bring back raw iron — half a dozen."],
      "minecraft:raw_iron", [t_item(V+"/digdeep", 0, "minecraft:raw_iron", 6)],
      [r_item(V+"/digdeep", 0, "minecraft:torch", 16), r_xp(V+"/digdeep", 1, 15)],
      deps=["chest"], shape="square")

quest("smelt", "Smelt It Down", ["Raw iron + fuel in the furnace. Out comes something you can actually use."],
      "minecraft:iron_ingot", [t_item(V+"/smelt", 0, "minecraft:iron_ingot", 5)],
      [r_item(V+"/smelt", 0, "minecraft:iron_ingot", 2), r_xp(V+"/smelt", 1, 10)],
      deps=["digdeep"])

quest("ironpick", "Iron Pickaxe", ["The tool that opens up the deep world. Diamond, redstone, gold — all behind this."],
      "minecraft:iron_pickaxe", [t_item(V+"/ironpick", 0, "minecraft:iron_pickaxe", 1)],
      [r_xp(V+"/ironpick", 0, 10)], deps=["smelt"])

quest("irontools", "Iron Age", ["Round out the set."],
      "minecraft:iron_axe",
      [t_item(V+"/irontools", 0, "minecraft:iron_axe", 1),
       t_item(V+"/irontools", 1, "minecraft:iron_sword", 1),
       t_item(V+"/irontools", 2, "minecraft:iron_shovel", 1)],
      [r_item(V+"/irontools", 0, "minecraft:coal", 8), r_xp(V+"/irontools", 1, 15)],
      deps=["ironpick"], shape="square")

quest("armor", "Ironclad", ["Full iron. The night gets a lot less frightening."],
      "minecraft:iron_chestplate",
      [t_item(V+"/armor", 0, "minecraft:iron_helmet", 1),
       t_item(V+"/armor", 1, "minecraft:iron_chestplate", 1),
       t_item(V+"/armor", 2, "minecraft:iron_leggings", 1),
       t_item(V+"/armor", 3, "minecraft:iron_boots", 1)],
      [r_xp(V+"/armor", 0, 30)], deps=["irontools"], shape="square")

quest("shield", "Guard", ["Six planks, one iron. Raise it and most things bounce off."],
      "minecraft:shield", [t_item(V+"/shield", 0, "minecraft:shield", 1)],
      [r_xp(V+"/shield", 0, 10)], deps=["ironpick"])

quest("bucket", "The Bucket", ["Three iron. Carries water, lava, milk, fish. You'll want water soon — trust me."],
      "minecraft:bucket", [t_item(V+"/bucket", 0, "minecraft:bucket", 1)],
      [r_item(V+"/bucket", 0, "minecraft:water_bucket", 1)], deps=["ironpick"])

quest("shears", "Shears", ["Two iron. Wool without the wet work, plus leaves and string."],
      "minecraft:shears", [t_item(V+"/shears", 0, "minecraft:shears", 1)],
      [r_item(V+"/shears", 0, "minecraft:white_wool", 6)], deps=["ironpick"])

# --- Act IV: farming ---
quest("hoe", "Break Ground", ["A hoe turns dirt into farmland. Any hoe will do."],
      "minecraft:iron_hoe",
      [t_item(V+"/hoe", 0, "minecraft:stone_hoe", 1)],
      [r_xp(V+"/hoe", 0, 5)], deps=["shears"])

quest("seeds", "Seed", ["Punch tall grass until seeds drop. Plant them on tilled soil next to water."],
      "minecraft:wheat_seeds", [t_item(V+"/seeds", 0, "minecraft:wheat_seeds", 3)],
      [r_xp(V+"/seeds", 0, 3)], deps=["hoe"])

quest("farm", "The Field",
      ["Till soil, plant your seeds, wait for the stalks to go gold.",
       "Then harvest — bring back wheat."],
      "minecraft:wheat",
      [t_check(V+"/farm", 0, "I tilled soil and planted a crop"),
       t_item(V+"/farm", 1, "minecraft:wheat", 3)],
      [r_item(V+"/farm", 0, "minecraft:wheat_seeds", 6), r_xp(V+"/farm", 1, 15)],
      deps=["seeds"], shape="square")

quest("bread", "Bread",
      ["Three wheat in a row. You will not go hungry in the Outlands again."],
      "minecraft:bread", [t_item(V+"/bread", 0, "minecraft:bread", 1)],
      [r_item(V+"/bread", 0, "minecraft:bread", 8), r_xp(V+"/bread", 1, 15)],
      deps=["farm"], shape="square")

quest("breed", "Livestock",
      ["Feed two of the same animal (wheat, seeds, carrots — depends on the animal). They'll make a third.",
       "A herd is a food supply that walks itself home."],
      "minecraft:wheat",
      [t_adv(V+"/breed", 0, "minecraft:husbandry/breed_an_animal")],
      [r_item(V+"/breed", 0, "minecraft:hay_block", 2), r_xp(V+"/breed", 1, 15)],
      deps=["bread"])

quest("meal", "A Proper Meal", ["Cook and stockpile real food. Rotten flesh doesn't count."],
      "minecraft:cooked_beef", [t_item(V+"/meal", 0, "minecraft:cooked_beef", 5)],
      [r_xp(V+"/meal", 0, 10)], deps=["bread"])

quest("sapling", "Replant", ["Take what you need, leave the forest standing. Grow a tree."],
      "minecraft:oak_sapling", [t_item(V+"/sapling", 0, "#minecraft:saplings", 2)],
      [r_xp(V+"/sapling", 0, 5)], deps=["farm"])

# --- Act V: ready ---
quest("stockpile", "Provisions",
      ["You don't leave a safe camp without supplies. Stock up."],
      "minecraft:bundle",
      [t_item(V+"/stockpile", 0, "minecraft:torch", 16),
       t_item(V+"/stockpile", 1, "minecraft:bread", 8),
       t_item(V+"/stockpile", 2, "minecraft:iron_ingot", 8)],
      [r_item(V+"/stockpile", 0, "minecraft:iron_block", 1), r_xp(V+"/stockpile", 1, 20)],
      deps=["meal", "bread"], shape="square")

quest("explore", "See the Outlands",
      ["Climb something high. Look out over the frontier. Get a feel for where you woke up.",
       "&7(Walk about a thousand blocks — anywhere.)"],
      "minecraft:spyglass",
      [t_check(V+"/explore", 0, "I've walked the land and seen the Outlands")],
      [r_item(V+"/explore", 0, "minecraft:map", 1), r_xp(V+"/explore", 1, 15)],
      deps=["stockpile"])

quest("ruins", "What the Old World Left",
      ["You've survived. Iron on your back, bread in your pack, a roof and a bed.",
       "", "But you've seen the machines in the ruins — the wheels, the gears, the great brass spines half-buried in the hills. Nobody grew those. Somebody &obuilt&r them, on purpose, and then they left.",
       "", "&fTime to learn how.&7 The next chapter opens the moment you're ready."],
      "create:brass_ingot",
      [t_check(V+"/ruins", 0, "I'm ready to look at the machines")],
      [r_item(V+"/ruins", 0, "create:andesite_alloy", 4),
       r_cmd(V+"/ruins", 1, "title @p title {\"text\":\"You remember something...\",\"color\":\"gold\"}", "A flicker of memory"),
       r_xp(V+"/ruins", 2, 50)],
      deps=["explore", "sapling", "breed"], shape="gear", size=2.0)

# ---------- layout: serpentine ----------
PER_ROW = 7
SPACING = 1.75
for i, q in enumerate(Q):
    row = i // PER_ROW
    col = i % PER_ROW
    if row % 2 == 1:
        col = PER_ROW - 1 - col
    q["x"] = round(col * SPACING, 2)
    q["y"] = round(row * SPACING, 2)

# ---------- emit ----------
def build_quest(q):
    d = {"id": hid(V + "/" + q["key"])}
    if q["deps"]:
        d["dependencies"] = [hid(V + "/" + k) for k in q["deps"]]
    d["description"] = q["desc"]
    if q["icon"]:
        d["icon"] = {"id": q["icon"]}
    if q["shape"]:
        d["shape"] = q["shape"]
    if q["size"]:
        d["size"] = D(q["size"])
    d["tasks"] = q["tasks"]
    d["rewards"] = q["rewards"]
    d["title"] = q["title"]
    d["x"] = D(q["x"])
    d["y"] = D(q["y"])
    return d

chapter = {
    "default_hide_dependency_lines": False,
    "default_quest_shape": "circle",
    "filename": V,
    "group": GROUP_ID,
    "icon": {"id": "minecraft:oak_sapling"},
    "id": hid("chapter/" + V),
    "order_index": 0,
    "quest_links": [],
    "quests": [build_quest(q) for q in Q],
    "title": "I · Come To",
}

def wr(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "chapters").mkdir(exist_ok=True)
wr(OUT / "chapter_groups.snbt", snbt({"chapter_groups": [{"id": GROUP_ID, "title": "Outlands of Aerie"}]}) + "\n")
wr(OUT / "data.snbt", snbt({
    "default_autoclaim_rewards": "disabled",
    "default_consume_items": False,
    "default_quest_disable_jei": False,
    "default_quest_shape": "circle",
    "default_reward_team": False,
    "detection_delay": 20,
    "disable_gui": False,
    "drop_loot_crates": False,
    "emergency_items_cooldown": 300,
    "grid_scale": D(0.5),
    "lock_message": "",
    "pause_game": False,
    "progression_mode": "flexible",
    "title": "Outlands of Aerie",
    "version": 13,
}) + "\n")
wr(OUT / "chapters" / f"{V}.snbt", snbt(chapter) + "\n")
print(f"wrote {len(Q)} quests -> {OUT}")
