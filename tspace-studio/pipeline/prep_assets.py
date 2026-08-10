"""Copy + downscale the shared brand assets into the demo folder so the demo
deploys standalone without pulling 700KB portraits over the wire."""
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent / "turncloud-presentation" / "img"
OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

PORTRAITS = {
    "08_pandora.jpg": "agent_pandora.jpg",
    "09_moana.jpg": "agent_moana.jpg",
    "10_banana.jpg": "agent_banana.jpg",
    "11_adriana.jpg": "agent_adriana.jpg",
    "12_stacey.jpg": "agent_stacey.jpg",
}
COPY = ["tspace_logo.png", "turncloud-logo.png", "accucrazy-logo.webp"]


def main():
    for src, dst in PORTRAITS.items():
        p = SRC / src
        im = Image.open(p).convert("RGB")
        im.thumbnail((520, 520), Image.LANCZOS)
        im.save(OUT / dst, quality=86, optimize=True)
        print(f"{dst}: {im.size} {(OUT/dst).stat().st_size//1024} KB")
    for f in COPY:
        if (SRC / f).exists():
            shutil.copy2(SRC / f, OUT / f)
            print(f"copied {f}")


if __name__ == "__main__":
    main()
