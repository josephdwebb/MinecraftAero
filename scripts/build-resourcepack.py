"""Build the downloadable pack and matching server properties (stdlib only)."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "resourcepack"
OUTPUT = ROOT / "releases" / "aerie-resources.zip"

def build():
    OUTPUT.parent.mkdir(exist_ok=True)
    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        for path in sorted(SOURCE.rglob("*")):
            if path.is_file() and "_src" not in path.parts:
                info = ZipInfo(path.relative_to(SOURCE).as_posix(), (2026, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                archive.writestr(info, path.read_bytes())
    digest = hashlib.sha1(OUTPUT.read_bytes()).hexdigest()
    values = {
        "resource-pack": f"https://raw.githubusercontent.com/josephdwebb/MinecraftAero/main/releases/aerie-resources.zip?v={digest}",
        "resource-pack-sha1": digest,
        "require-resource-pack": "true",
        "resource-pack-prompt": json.dumps({"text": "Install the Outlands of Aerie soundtrack for your arrival."}),
    }
    (ROOT / "server/resourcepack.properties").write_text(
        "\n".join(f"{k}={v}" for k, v in values.items()) + "\n", encoding="utf-8")
    print(f"Built {OUTPUT.name}: {OUTPUT.stat().st_size} bytes, SHA-1 {digest}")

if __name__ == "__main__":
    build()
