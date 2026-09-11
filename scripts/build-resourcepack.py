#!/usr/bin/env python3
"""Zip resourcepack/ into releases/aerie-resources.zip and print its SHA-1.

Uses zipfile (not tar) so entries are real zip records with forward slashes --
GNU tar's -a does NOT produce zip format and Minecraft will reject the pack,
which with require-resource-pack=true kicks players on join.
"""
import hashlib, pathlib, zipfile

root = pathlib.Path(__file__).resolve().parent.parent
src = root / "resourcepack"
out = root / "releases" / "aerie-resources.zip"
out.parent.mkdir(exist_ok=True)

files = sorted(p for p in src.rglob("*") if p.is_file() and "_src" not in p.parts)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in files:
        arc = p.relative_to(src).as_posix()   # forward slashes, pack.mcmeta at root
        z.write(p, arc)

data = out.read_bytes()
sha = hashlib.sha1(data).hexdigest()
with zipfile.ZipFile(out) as z:
    assert "pack.mcmeta" in z.namelist(), "pack.mcmeta must be at zip root"
    names = z.namelist()
print(f"{out.name}  {len(data)} bytes")
print("entries:", names)
print("sha1:", sha)
