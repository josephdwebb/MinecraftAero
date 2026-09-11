"""Inspect structure NBT with the standard library; does not edit the world."""
import gzip
import io
import struct
from pathlib import Path

def read_nbt(path):
    stream = io.BytesIO(gzip.decompress(path.read_bytes()))
    def number(fmt):
        return struct.unpack(">" + fmt, stream.read(struct.calcsize(fmt)))[0]
    def string():
        return stream.read(number("H")).decode("utf-8")
    def payload(kind):
        if kind in range(1, 7):
            return number({1: "b", 2: "h", 3: "i", 4: "q", 5: "f", 6: "d"}[kind])
        if kind == 8:
            return string()
        if kind == 9:
            subtype, length = number("B"), number("i")
            return [payload(subtype) for _ in range(length)]
        if kind == 10:
            value = {}
            while (subtype := number("B")):
                key = string()
                value[key] = payload(subtype)
            return value
        if kind in (7, 11, 12):
            return [number({7: "b", 11: "i", 12: "q"}[kind]) for _ in range(number("i"))]
        raise ValueError(kind)
    kind = number("B")
    string()
    return payload(kind)

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    data = read_nbt(root / "server/datapacks/aerie_intro/data/aerie/structure/big_airship_1.nbt")
    palette = data["palette"]
    blocks = {tuple(b["pos"]): palette[b["state"]]["Name"] for b in data["blocks"]}
    print("Structure size:", data["size"])
    for y in (5, 6, 7, 10, 14, 15, 16):
        print(f"\nFloor slice world Y={270 + y}; # solid, . air, ? absent mod")
        for z in range(30, 51):
            row = []
            for x in range(7, 29):
                block = blocks.get((x, y, z), "minecraft:air")
                row.append("." if block.endswith(":air") else "?" if block.startswith("enchanted") else "#")
            print(f"{z - 172:4}: " + "".join(row))
    print("\nOriginal cabin feet/head:", blocks.get((17, 15, 40)), blocks.get((17, 16, 40)))
