#!/usr/bin/env python3
"""Generates the FTB Quests definition for Outlands of Aerie.
Output: ./quests/  (chapter_groups.snbt, data.snbt, chapters/*.snbt)
Deploy: copy ./quests/ -> server/run/config/ftbquests/quests/  then restart.
IDs are deterministic (hash of a stable key) so regenerating keeps dependencies intact.
"""
import hashlib, json, pathlib

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "quests"
ADV = ROOT.parent / "datapacks/aerie_intro/data/aerie/advancement/quests"
TAG_TASKS = {}
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
    # A tag is not a valid ItemStack id. Vanilla advancement predicates support
    # tags without requiring another client/server filtering mod.
    if item.startswith("#"):
        key = f"{qkey}/{n}"
        TAG_TASKS[key] = {"criteria": {"have": {
            "trigger": "minecraft:inventory_changed",
            "conditions": {"items": [{"items": item, "count": {"min": count}}]}
        }}}
        task = t_adv(qkey, n, "aerie:quests/" + key)
        task["title"] = f"Collect {count} {item.split(':')[1].replace('_', ' ')} (any type)"
        return task
    d = {"id": _tid(qkey, n), "item": {"count": 1, "id": item}, "type": "item", "consume_items": False}
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
    return {"id": _rid(qkey, n), "type": "command", "command": cmd, "title": title, "permission_level": 2, "silent": True}

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
      ["Make a stone pickaxe to open the mining route. The rest of the set is your choice."],
      "minecraft:stone_pickaxe",
      [t_item(V+"/stonetools", 0, "minecraft:stone_pickaxe", 1)],
      [r_item(V+"/stonetools", 0, "minecraft:coal", 4), r_xp(V+"/stonetools", 1, 15)],
      deps=["cobble"], shape="square")

quest("furnace", "The Hearth", ["Eight cobblestone. A furnace smelts ore, cooks food, and bakes charcoal."],
      "minecraft:furnace", [t_item(V+"/furnace", 0, "minecraft:furnace", 1)],
      [r_xp(V+"/furnace", 0, 5)], deps=["stonetools"])

quest("light", "First Light",
      ["Mine coal (black flecks in stone) &7or&f smelt a log into charcoal. Either makes torches.",
       "", "Coal or charcoal above a stick makes four torches. Light the ground around camp."],
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
      [t_adv(V+"/sleep", 0, "minecraft:adventure/sleep_in_bed")],
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
      [t_item(V+"/hoe", 0, "#minecraft:hoes", 1)],
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
       r_cmd(V+"/ruins", 1, "title @s title {\"text\":\"You remember something...\",\"color\":\"gold\"}", "A flicker of memory"),
       r_xp(V+"/ruins", 2, 50)],
      deps=["explore", "sapling", "breed"], shape="gear", size=2.0)

# ---------- parallel survival routes, retaining all existing quest IDs ----------
by_key = {q["key"]: q for q in Q}
for key, deps in {
    "furnace": ["cobble"], "door": ["table"], "wool": ["table"],
    "chest": ["table"], "digdeep": ["stonetools", "furnace"],
    "hoe": ["cobble"], "bucket": ["smelt"], "shears": ["smelt"],
    "shield": ["smelt"], "meal": ["furnace"],
    "stockpile": ["bread", "ironpick"], "explore": ["sleep"],
    "ruins": ["ironpick", "sleep", "bread"],
}.items():
    by_key[key]["deps"] = deps
by_key["wake"]["desc"] += ["", "&6Your field journal", "Open quests from the inventory quest-book button, or bind Open Quests in Controls > FTB Quests.", "Item tasks keep your supplies. Claim rewards by clicking them. Shelter, mining and farming can be tackled in parallel."]
by_key["cobble"]["desc"] = ["Mine 20 cobblestone with your wooden pickaxe. Enough for a furnace and your first stone tools."]
by_key["nightfall"]["desc"] = ["Optional patrol: defeat two zombies. Stay near lit ground and keep a retreat open."]
by_key["sapling"]["desc"] = ["Collect two saplings of one type. Plant a few near camp to keep wood close at hand."]
by_key["ruins"]["desc"] = ["A bed. Bread. An iron pickaxe. You have enough to build a life here.", "", "The airship ran on wheels and shafts. If you can learn how they worked, the sky might not be lost to you.", "", "&6Continue in Chapter II: First Rotation.&r Optional survival jobs remain available whenever you want them."]

# Read left-to-right by route; avoid a serpentine line crossing unrelated branches.
routes = [
    (0, ["wake", "planks", "table", "sticks", "wpick", "cobble"]),
    (2, ["door", "wool", "bed", "sleep", "chest", "explore"]),
    (4, ["stonetools", "furnace", "digdeep", "smelt", "ironpick", "stockpile", "ruins"]),
    (6, ["hoe", "seeds", "farm", "bread", "breed", "sapling"]),
    (8, ["waxe", "wsword", "light", "nightfall", "meal"]),
    (10, ["shield", "bucket", "shears", "irontools", "armor"]),
]
for y, keys in routes:
    for x, key in enumerate(keys):
        by_key[key]["x"], by_key[key]["y"] = x * 2.25, y

# ---------- layout ----------
PER_ROW = 7
SPACING = 1.75
for i, q in enumerate(Q):
    row = i // PER_ROW
    col = i % PER_ROW
    if row % 2 == 1:
        col = PER_ROW - 1 - col
    q.setdefault("x", round(col * SPACING, 2))
    q.setdefault("y", round(row * SPACING, 2))

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

def linearize(quests):
    """Force a strictly linear chain: quest N depends only on quest N-1.

    The tracker should ever show one objective, so the dependency graph must be
    a single path. Authoring order above defines the path.
    """
    for i, q in enumerate(quests):
        q["deps"] = [quests[i - 1]["key"]] if i else []


chapter = {
    "default_hide_dependency_lines": False,
    "default_quest_shape": "circle",
    "filename": V,
    "group": GROUP_ID,
    "icon": {"id": "minecraft:oak_sapling"},
    "id": hid("chapter/" + V),
    "order_index": 0,
    "quest_links": [],
    "quests": (linearize(Q), [build_quest(q) for q in Q])[1],
    "title": "I · Come To",
}

def wr(path, text):
    path.write_text(text, encoding="utf-8", newline="\n")

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "chapters").mkdir(exist_ok=True)
wr(OUT / "chapter_groups.snbt", snbt({"chapter_groups": [{"id": GROUP_ID, "title": "Outlands of Aerie"}]}) + "\n")
wr(OUT / "data.snbt", snbt({
    "default_autoclaim_rewards": "enabled",
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
    "progression_mode": "linear",
    "title": "Outlands of Aerie",
    "version": 13,
}) + "\n")
wr(OUT / "chapters" / f"{V}.snbt", snbt(chapter) + "\n")
print(f"wrote {len(Q)} quests -> {OUT}")

# Chapter II teaches a working workshop rather than rewarding a shopping list.
# New keys use their own namespace; Chapter I hashes above remain untouched.
V = "first_rotation"
Q = []
spec = [
    ("ponder", "A Mechanic's Memory", "create:andesite_alloy", None,
     ["Find a Create item in your inventory and hold the Ponder key shown in its tooltip.", "Ponder demonstrates placement, power and moving parts. Use it whenever a machine is unfamiliar.", "This field journal is a guide, not a recipe browser: use the crafting recipe book and Ponder."], []),
    ("alloy", "The First Alloy", "create:andesite_alloy", 8,
     ["Gather andesite and iron nuggets to make eight andesite alloy. Keep some iron for tools."], ["ponder"]),
    ("wheel", "Borrow the River", "create:water_wheel", 1,
     ["Craft a water wheel. Ponder it, then set it in flowing water near your workshop."], ["alloy"]),
    ("shaft", "Carry the Motion", "create:shaft", 8,
     ["Shafts carry rotation in a straight line. Connect them to the wheel's axle."], ["wheel"]),
    ("cog", "Around the Corner", "create:cogwheel", 4,
     ["Meshing cogwheels transfer rotation. Ponder small and large cogs before changing speed."], ["shaft"]),
    ("casing", "A Machine's Frame", "create:andesite_casing", 4,
     ["Strip a log with an axe, then apply andesite alloy to it. Make four casings."], ["alloy"]),
    ("press", "Under Pressure", "create:mechanical_press", 1,
     ["Craft a mechanical press. Supply rotation from the wheel and leave room below its head."], ["cog", "casing"]),
    ("depot", "On the Workbench", "create:depot", 1,
     ["Put a depot beneath the press. Use Ponder to check the spacing, then place an iron ingot on it."], ["press"]),
    ("sheet", "Proof of Power", "create:iron_sheet", 4,
     ["Press four iron ingots into sheets. If it stalls, check connections and the wheel's stress capacity."], ["depot"]),
    ("goggles", "Read the Machine", "create:goggles", 1,
     ["Optional instrument: Engineer's Goggles show machine information when worn. Check the recipe book; these need gold."], ["sheet"]),
    ("mill", "The Daily Grind", "create:millstone", 1,
     ["Add a powered millstone. Try milling wheat and inspect the output; keep the farm feeding the workshop."], ["cog", "casing"]),
    ("basin", "Leave Room to Grow", "create:basin", 1,
     ["A basin holds ingredients for mixing and pressing. Set one aside for the next machine."], ["sheet"]),
    ("mixer", "Mixing Business", "create:mechanical_mixer", 1,
     ["Craft a mixer and Ponder it above a basin. It needs sufficient speed; a spinning shaft alone may not be enough."], ["basin", "cog"]),
    ("workshop", "A Workshop That Works", "create:mechanical_press", None,
     ["Practical check: one water-powered workshop, a press that makes sheets, and a millstone that processes wheat.", "Mark this complete after you have run both machines. Keep a clear walkway and room to expand."], ["sheet", "mill"]),
    ("flight_plan", "A Reason to Build", "aeronautics:wooden_propeller", None,
     ["Pick a place outside the village for your future hangar. Leave space around the hull and overhead.", "Your next project is flight. Use the Aeronautics Ponder scenes and the advancements tab for flight hardware milestones.", "Sketch a small first ship, decide where it will dock, and mark this planning job complete. Building it remains your next expedition."], ["workshop"]),
]
for i, (key, name, icon, count, desc, deps) in enumerate(spec):
    qkey = V + "/" + key
    tasks = [t_item(qkey, 0, icon, count)] if count else [t_check(qkey, 0, {
        "ponder": "I watched a Create Ponder scene", "workshop": "My press and millstone run on water power",
        "flight_plan": "I chose a hangar site and planned my first ship"}[key])]
    quest(key, name, desc, icon, tasks, [r_xp(qkey, 0, 10 if count else 20)], deps,
          shape="hexagon" if key in ("ponder", "workshop", "flight_plan") else None)
    Q[-1]["x"], Q[-1]["y"] = (i % 5) * 2.5, (i // 5) * 2.5
linearize(Q)
second = dict(chapter, filename=V, id=hid("chapter/" + V), title="II · First Rotation",
              icon={"id": "create:water_wheel"}, order_index=1, quests=[build_quest(q) for q in Q])
second["quests"][0]["dependencies"] = [hid("come_to/ruins")]
wr(OUT / "chapters" / f"{V}.snbt", snbt(second) + "\n")
for key, data in TAG_TASKS.items():
    path = ADV / f"{key}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    wr(path, json.dumps(data, indent=2) + "\n")
print(f"wrote {len(Q)} Create quests and {len(TAG_TASKS)} tag predicates")
