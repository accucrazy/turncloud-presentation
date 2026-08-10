"""Generate the TPC agent shopping-street hero (replaces the grid-floor space hero).

Uses all five official agent portraits as references for character consistency.
"""
import base64
import mimetypes
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

IMG = ROOT.parent / "turncloud-presentation" / "img"
OUT = ROOT / "assets"

REFS = [
    ("08_pandora.jpg", "Pandora — silver-haired woman in a grey suit (cyan accent)"),
    ("09_moana.jpg", "Moana — woman with curly afro hair, orange tee, pink megaphone (orange accent)"),
    ("10_banana.jpg", "Banana — yellow banana mascot with round glasses and bow tie (gold accent)"),
    ("11_adriana.jpg", "Adriana — brunette woman, round glasses, sage blazer, glowing tablet (violet accent)"),
    ("12_stacey.jpg", "Stacey — woman with dark-brown high ponytail, navy blazer, holographic stylus (green accent)"),
]

PROMPT = """
A wide 16:9 keynote hero: a charming Pixar-3D SHOPPING STREET at dusk — the
business district of an AI world where companies come to make money together.

Five cozy storefronts line the street side by side, each run by one of the five
reference characters standing proudly at their own shop door (match each
character's face, hair, outfit and colour EXACTLY to the reference photos):

1. Pandora's observatory-style data shop — cyan glow, holographic charts in the window
2. Moana's content studio — orange glow, speaker/megaphone motif on the facade
3. Banana's art & creative boutique — warm gold glow, easels and picture frames in the window
4. Adriana's media & delivery office — violet glow, floating parcel-drones above
5. Stacey's command tower at the end of the street — green glow, taller, orchestrating

Atmosphere: warm golden-hour light mixed with soft neon shop glows, glowing shop
windows, a few small cute robot customers walking with shopping bags, gentle
floating holograms (coins, charts, sparkles) above the street suggesting
prosperity and commerce. Optimistic, inviting, "let's build a business here".

Camera: slightly elevated 3/4 view down the street so all five shops are visible.
Style: premium Pixar-quality 3D render, soft global illumination, crisp details.

STRICT RULES:
- NO grid floor, NO wireframe, NO tron-style lines. The street is warm paved stone.
- Signboards use ABSTRACT ICONS ONLY — absolutely NO text, NO letters, NO numbers,
  NO logos, NO watermarks anywhere in the image.
- Keep the upper-left area relatively calm (sky/bokeh) so UI copy can overlay.
"""


def part(path):
    mime, _ = mimetypes.guess_type(str(path))
    return {"inline_data": {"mime_type": mime or "image/jpeg",
                            "data": base64.b64encode(path.read_bytes()).decode()}}


def main():
    parts = []
    for fname, label in REFS:
        p = IMG / fname
        if p.exists():
            parts.append({"text": f"Character reference — {label}:"})
            parts.append(part(p))
    parts.append({"text": PROMPT})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"],
                             "imageConfig": {"aspectRatio": "16:9"}},
    }
    for attempt in range(1, 4):
        print(f"generating street hero (attempt {attempt}) ...", flush=True)
        t0 = time.time()
        try:
            r = requests.post(URL, json=payload, timeout=300)
        except requests.RequestException as e:
            print("  req err", e)
            time.sleep(10 * attempt)
            continue
        if r.status_code != 200:
            print(f"  http {r.status_code}: {r.text[:200]}")
            time.sleep(12 * attempt)
            continue
        for c in r.json().get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                inline = p.get("inlineData") or p.get("inline_data")
                if inline and inline.get("data"):
                    data = base64.b64decode(inline["data"])
                    out = OUT / "street_hero.jpg"
                    out.write_bytes(data)
                    print(f"  saved {out.name} ({len(data)//1024} KB, {time.time()-t0:.0f}s)")
                    return 0
        print("  no image in response")
        time.sleep(8 * attempt)
    return 1


if __name__ == "__main__":
    sys.exit(main())
