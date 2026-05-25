"""
Generate the cinematic backdrop + per-layer icon illustrations for the new
animated "overview" slide that orchestrates the concepts of slides 1-4.

Outputs:
  img/anim_backdrop.jpg          — wide ambient cyan/violet aurora backdrop
  img/anim_runtime_iso.png       — orange isometric foundation card
  img/anim_aios_orb.png          — cyan AI OS core orb with floating chips
  img/anim_agents_ring.png       — violet ring of 5 collaborating agents
"""
import base64
import json
import mimetypes
import os
import sys
import time
from pathlib import Path

import requests

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise SystemExit("Set GEMINI_API_KEY (or GOOGLE_API_KEY) env var before running.")
MODEL = "nano-banana-pro-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

ROOT = Path(__file__).parent
OUT = ROOT / "img"
OUT.mkdir(exist_ok=True)


def load_ref(path: Path, label: str) -> list:
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "image/jpeg"
    if path.suffix.lower() == ".png":
        mime = "image/png"
    return [
        {"text": f"Reference — {label}: keep this visual language and quality."},
        {
            "inline_data": {
                "mime_type": mime,
                "data": base64.b64encode(path.read_bytes()).decode(),
            }
        },
    ]


STYLE_BACKDROP = (
    "STYLE: cinematic ambient backdrop for a premium tech keynote slide. "
    "Mood: warm-bright, hopeful, slightly futuristic, NOT cyberpunk. "
    "PALETTE: predominantly soft off-white, with gentle cyan #06b6d4 "
    "and violet #a855f7 radial auroras blooming at the edges, faint orange "
    "#f59e0b warm glow at the bottom. Very subtle floating particle dots, "
    "soft bokeh, faint geometric lattice barely visible. NO TEXT, no logos, "
    "no watermarks. Just an ambient stage where other elements will sit on top."
)

STYLE_ICON = (
    "STYLE: clean modern flat vector illustration on transparent / very pale "
    "off-white background. Bright, optimistic, premium product-page aesthetic "
    "(Linear / Stripe / Vercel). Soft drop shadow. NO TEXT, no labels, no "
    "watermarks. The image must work as a standalone decorative icon at "
    "small or medium size."
)


JOBS = [
    # 1) Ambient backdrop — used as bg for the animated overview slide
    ("anim_backdrop", "16:9", STYLE_BACKDROP, None,
     "Cinematic ambient backdrop: a soft, almost-white stage with two large "
     "diffuse radial auroras — cyan glow at the upper-right and violet glow "
     "at the upper-left — blooming softly inward. A faint warm orange wash "
     "rises from the bottom. Very fine floating particle dots scattered "
     "across the scene, plus a barely-visible geometric grid lattice. "
     "Empty stage feeling — the centre is calm and ready to hold UI/text "
     "elements on top of it."),

    # 2) Runtime isometric foundation slab — orange
    ("anim_runtime_iso", "4:3", STYLE_ICON, None,
     "A wide isometric foundation slab seen from a low 3/4 angle, warm "
     "amber-orange palette (#f59e0b, #fbbf24, #fed7aa). On top of the slab "
     "sit small, friendly flat-vector icons (no text), evenly spaced: "
     "a retail store building, a POS terminal, an IoT sensor with WiFi "
     "waves, a small factory, and a tiny customer-and-staff figure pair. "
     "Soft shadow underneath the slab. Premium illustration, like a hero "
     "graphic on a SaaS landing page."),

    # 3) AI OS core orb — cyan, with floating chip tags
    ("anim_aios_orb", "1:1", STYLE_ICON, None,
     "A clean cyan glowing hexagonal core (#06b6d4) in the centre, drawn "
     "as a flat-vector emblem with very soft outer glow rings. Around the "
     "hex, six small pill-shaped tags float on invisible orbits, each with "
     "a subtle cyan background tint — but DO NOT write any letters in the "
     "tags (the chips appear empty / decorative). Faint connection lines "
     "between the hex and the tags. Premium product-page aesthetic."),

    # 4) Agents collaboration ring — violet
    ("anim_agents_ring", "1:1", STYLE_ICON, None,
     "A soft violet (#a855f7) circular ring layout. Five small Pixar-style "
     "circular character avatar PLACEHOLDERS (just abstract head silhouettes "
     "with simple colour fills — silver/grey, brown-curly, banana-yellow, "
     "brunette, dark-ponytail) arranged evenly around the ring. Connecting "
     "each pair: thin glowing violet A2A protocol lines that softly pulse. "
     "The ring sits on a very pale lavender background patch with soft "
     "shadow."),
]


def call_api(prompt: str, style: str, refs: list, aspect: str,
             attempt: int = 1, max_attempts: int = 3) -> bytes | None:
    parts = []
    for r in refs or []:
        parts.extend(r)
    parts.append({"text": prompt})
    parts.append({"text": style})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect},
        },
    }

    try:
        r = requests.post(URL, json=payload, timeout=300)
    except requests.RequestException as e:
        print(f"  request error: {e}")
        if attempt < max_attempts:
            time.sleep(5 * attempt)
            return call_api(prompt, style, refs, aspect, attempt + 1, max_attempts)
        return None

    if r.status_code != 200:
        print(f"  http {r.status_code}: {r.text[:500]}")
        if r.status_code in (429, 500, 502, 503, 504) and attempt < max_attempts:
            time.sleep(10 * attempt)
            return call_api(prompt, style, refs, aspect, attempt + 1, max_attempts)
        return None

    data = r.json()
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])
    print("  no image in response; preview:", json.dumps(data, ensure_ascii=False)[:400])
    return None


def main():
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    total = len(JOBS)
    for i, (name, aspect, style, refs, prompt) in enumerate(JOBS, 1):
        if only and name not in only:
            continue
        existing = list(OUT.glob(f"{name}.*"))
        if existing:
            print(f"[{i}/{total}] {name}: SKIP (exists)")
            continue
        t0 = time.time()
        print(f"[{i}/{total}] {name}: generating ({aspect})...", flush=True)
        data = call_api(prompt, style, refs, aspect)
        if data is None:
            print(f"[{i}/{total}] {name}: FAILED")
            continue
        ext = "png" if data[:8] == b"\x89PNG\r\n\x1a\n" else "jpg"
        out = OUT / f"{name}.{ext}"
        out.write_bytes(data)
        print(f"[{i}/{total}] {name}: saved {out.name} ({len(data)//1024} KB, {time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
