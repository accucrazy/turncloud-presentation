"""Generate the visual assets for the TSpace Studio demo.

  space_hero.jpg   16:9  — the "digital space" backdrop (metaverse vibe)
  gen_out_1..3.jpg  1:1  — sample Banana Split creative outputs for the demo run
"""
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT.parent / "turncloud-presentation" / "tpc-launch" / ".env")

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise SystemExit("GEMINI_API_KEY missing")
MODEL = "nano-banana-pro-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

OUT = ROOT / "assets"
OUT.mkdir(exist_ok=True)

SPACE_HERO = """
A wide 16:9 keynote backdrop of a DIGITAL SPACE — the virtual headquarters where AI
agents work. Dark deep-space navy (#050810 → #0b1024) with a luminous perspective
GRID FLOOR receding to a horizon, soft volumetric light, drifting particles and a few
translucent glass panels floating in the void showing faint dashboards and charts.
A large translucent cyan-violet ORB glows at the centre-right, softly lighting the grid.
Subtle neon rim light in cyan #22d3ee, violet #a855f7 and a touch of amber #f59e0b.
Elegant, calm, premium — like an Apple/Linear product film still. Slight metaverse feel
but NOT cheesy, NOT cyberpunk clutter, NOT neon signage.
ABSOLUTELY NO TEXT, NO letters, NO numbers, NO logos, NO watermarks anywhere.
Empty negative space in the upper-left third so UI text can be overlaid later.
"""

CREATIVE_BASE = """
A polished 1:1 SOCIAL MEDIA CREATIVE for a Taiwanese convenience-store coffee brand's
iced americano ("cold brew"). Premium product photography look, clean modern layout,
generous negative space, soft natural light, shallow depth of field.
The composition must look like a real, ready-to-publish Instagram post from a brand.
Include a tall clear plastic cup of iced black coffee with condensation and ice cubes.
NO text, NO letters, NO logos, NO watermarks — the copy will be overlaid by the app.
"""

VARIANTS = [
    ("gen_out_1", CREATIVE_BASE + "Variant A — warm morning: wooden desk by a sunlit window, "
                                  "soft amber highlights, cozy office-morning mood."),
    ("gen_out_2", CREATIVE_BASE + "Variant B — clean studio: seamless pastel mint background, "
                                  "centred hero product, crisp editorial minimalism, soft shadow."),
    ("gen_out_3", CREATIVE_BASE + "Variant C — lifestyle: coffee held in hand on a city street at "
                                  "golden hour, blurred urban bokeh behind, energetic commute mood."),
]


def call(prompt, ratio):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": ratio},
        },
    }
    for attempt in range(1, 4):
        try:
            r = requests.post(URL, json=payload, timeout=300)
        except requests.RequestException as e:
            print(f"   request error {e} (retry {attempt})")
            time.sleep(5 * attempt)
            continue
        if r.status_code != 200:
            print(f"   http {r.status_code}: {r.text[:250]}")
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(10 * attempt)
                continue
            return None
        for c in r.json().get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                inline = p.get("inlineData") or p.get("inline_data")
                if inline and inline.get("data"):
                    return base64.b64decode(inline["data"])
        time.sleep(4 * attempt)
    return None


def main():
    jobs = [("space_hero", SPACE_HERO, "16:9")] + [(n, p, "1:1") for n, p in VARIANTS]
    only = sys.argv[1:] 
    for name, prompt, ratio in jobs:
        if only and name not in only:
            continue
        print(f"generating {name} ({ratio}) ...", flush=True)
        t0 = time.time()
        data = call(prompt, ratio)
        if not data:
            print(f"   FAILED {name}")
            continue
        ext = "png" if data[:8] == b"\x89PNG\r\n\x1a\n" else "jpg"
        p = OUT / f"{name}.{ext}"
        p.write_bytes(data)
        print(f"   saved {p.name} ({len(data)//1024} KB, {time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
