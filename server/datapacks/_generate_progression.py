#!/usr/bin/env python3
"""Generates the 'losertown_progression' advancement datapack.
Run:  python server/datapacks/_generate_progression.py
Output: server/datapacks/losertown_progression/
"""
import json, os, pathlib

NS = "losertown"
ROOT = pathlib.Path(__file__).parent / "losertown_progression"
ADV = ROOT / "data" / NS / "advancement"

# (key, parent, title, description, icon_item, [item_ids that satisfy it], frame)
NODES = [
    ("root", None, "Aesthetic Technology",
     "Craft Andesite Alloy — the backbone of every Create machine.",
     "create:andesite_alloy", ["create:andesite_alloy"], "task"),

    ("cogwheel", "root", "Turn, Turn, Turn",
     "Craft a Cogwheel. Rotation is power in Create.",
     "create:cogwheel", ["create:cogwheel", "create:large_cogwheel"], "task"),

    ("power", "cogwheel", "First Rotation",
     "Build a source of rotational force: a Water Wheel or a Windmill Bearing.",
     "create:water_wheel",
     ["create:water_wheel", "create:large_water_wheel", "create:windmill_bearing"], "task"),

    ("casing", "power", "Encased",
     "Craft Andesite Casing. Most machines need it.",
     "create:andesite_casing", ["create:andesite_casing"], "task"),

    ("press", "casing", "Under Pressure",
     "Craft a Mechanical Press — sheet metal, plates and pressing recipes.",
     "create:mechanical_press", ["create:mechanical_press"], "task"),

    ("crushing", "casing", "Grind It Out",
     "Craft a Millstone or Crushing Wheels and start processing ore.",
     "create:millstone", ["create:millstone", "create:crushing_wheel"], "task"),

    ("mixer", "press", "Well Mixed",
     "Craft a Mechanical Mixer for multi-ingredient and washing recipes.",
     "create:mechanical_mixer", ["create:mechanical_mixer"], "task"),

    ("brass", "mixer", "Going for Brass",
     "Produce your first Brass Ingot. Tier two begins.",
     "create:brass_ingot", ["create:brass_ingot"], "goal"),

    ("precision", "brass", "Precision Engineering",
     "Craft a Precision Mechanism — the heart of advanced Create devices.",
     "create:precision_mechanism", ["create:precision_mechanism"], "task"),

    ("deployer", "precision", "Automation Station",
     "Craft a Deployer. It uses tools and items on the world for you.",
     "create:deployer", ["create:deployer"], "task"),

    ("arm", "precision", "Give 'em a Hand",
     "Craft a Mechanical Arm to sort and move items between points.",
     "create:mechanical_arm", ["create:mechanical_arm"], "task"),

    ("crafter", "precision", "Assembly Line",
     "Craft a Mechanical Crafter and automate crafting recipes.",
     "create:mechanical_crafter", ["create:mechanical_crafter"], "task"),

    ("contraption", "power", "It Moves!",
     "Craft a Mechanical Bearing, Clutch or Gantry — assemble a moving contraption.",
     "create:mechanical_bearing",
     ["create:mechanical_bearing", "create:clutch", "create:gantry_carriage", "create:rope_pulley"], "goal"),

    ("train", "contraption", "All Aboard",
     "Craft Railway Casing and lay Train Tracks. Build a working train.",
     "create:railway_casing", ["create:railway_casing"], "challenge"),

    ("goggles", "cogwheel", "Engineer's Eyes",
     "Craft Engineer's Goggles to read stress, speed and fluid levels.",
     "create:goggles", ["create:goggles"], "task"),

    ("schematic_table", "casing", "Blueprints",
     "Craft a Schematic Table. Load a .nbt schematic from your client's "
     "'schematics' folder to deploy a hologram.",
     "create:schematic_table", ["create:schematic_table"], "task"),

    ("schematicannon", "schematic_table", "Automated Architect",
     "Craft a Schematicannon. Feed it the real materials + gunpowder and it "
     "prints your schematic block by block.",
     "create:schematicannon", ["create:schematicannon"], "challenge"),

    # ── Aeronautics branch ──
    ("propeller", "contraption", "Take to the Skies",
     "Craft a Wooden Propeller — your first piece of flight hardware.",
     "aeronautics:wooden_propeller",
     ["aeronautics:wooden_propeller", "aeronautics:andesite_propeller"], "goal"),

    ("prop_bearing", "propeller", "Spin Up",
     "Craft a Propeller Bearing. Mount it to make a contraption that flies.",
     "aeronautics:propeller_bearing",
     ["aeronautics:propeller_bearing", "aeronautics:gyroscopic_propeller_bearing"], "task"),

    ("envelope", "propeller", "Hot Air",
     "Craft Envelope blocks — the skin of a blimp or airship balloon.",
     "aeronautics:white_envelope",
     ["aeronautics:white_envelope", "aeronautics:blue_envelope", "aeronautics:red_envelope",
      "aeronautics:black_envelope", "aeronautics:gray_envelope", "aeronautics:yellow_envelope",
      "aeronautics:green_envelope", "aeronautics:orange_envelope"], "task"),

    ("levitite", "prop_bearing", "Anti-Gravity",
     "Obtain Levitite Blend or Levitite — passive lift for heavy airships.",
     "aeronautics:levitite_blend",
     ["aeronautics:levitite_blend", "aeronautics:levitite", "aeronautics:pearlescent_levitite"], "task"),

    ("smart_prop", "levitite", "Fly-by-Wire",
     "Craft a Smart Propeller for controllable, variable-pitch thrust.",
     "aeronautics:smart_propeller", ["aeronautics:smart_propeller"], "challenge"),

    ("aviator", "envelope", "Aviator",
     "Craft Aviator's Goggles and take the wheel.",
     "aeronautics:aviators_goggles", ["aeronautics:aviators_goggles"], "task"),
]


def build(key, parent, title, desc, icon, items, frame):
    disp = {
        "icon": {"id": icon},
        "title": title,
        "description": desc,
        "frame": frame,
        "show_toast": True,
        "announce_to_chat": True,
        "hidden": False,
    }
    if parent is None:
        disp["background"] = "minecraft:textures/block/andesite.png"
    adv = {
        "display": disp,
        "criteria": {
            "have": {
                "trigger": "minecraft:inventory_changed",
                "conditions": {"items": [{"items": items}]},
            }
        },
        "requirements": [["have"]],
    }
    if parent is not None:
        adv["parent"] = f"{NS}:{parent}"
    return adv


def main():
    ADV.mkdir(parents=True, exist_ok=True)
    (ROOT / "pack.mcmeta").write_text(json.dumps({
        "pack": {
            "pack_format": 48,
            "description": "Losertown — Create & Aeronautics guided progression",
        }
    }, indent=2))
    for node in NODES:
        (ADV / f"{node[0]}.json").write_text(json.dumps(build(*node), indent=2))
    print(f"wrote {len(NODES)} advancements to {ADV}")


if __name__ == "__main__":
    main()
