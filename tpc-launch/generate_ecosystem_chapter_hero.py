"""
Generate the hero illustration for the OPEN ECOSYSTEM chapter slide.
Scene: Pandora (Accucrazy's market-intelligence AI) jamming together with the
ecosystem partners — Luna (viral content creator AI), Raccoon (Raccoon AI
customer-service robot) and a Daft-Punk-style helmet robot that stands in for
Rytho (the music agent OS). Friendly, premium, Pixar-meets-product-page energy
that says "we're playing together, the ecosystem is open."
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


def load_ref(name: str, label: str) -> list:
    path = OUT / name
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "image/jpeg"
    if path.suffix.lower() == ".png":
        mime = "image/png"
    return [
        {"text": f"Reference — {label}: keep the same character design, palette and Pixar-style quality."},
        {
            "inline_data": {
                "mime_type": mime,
                "data": base64.b64encode(path.read_bytes()).decode(),
            }
        },
    ]


STYLE = (
    "STYLE: cinematic Pixar / Disney 3D illustration. Soft global illumination, "
    "warm rim lights, gentle bokeh background, premium SaaS keynote energy. "
    "Bright, joyful, NOT cyberpunk, NOT neon-soaked. Soft glow accents only. "
    "STRICTLY NO TEXT, NO LETTERS, NO LABELS, NO WATERMARKS, NO READABLE "
    "SIGNAGE anywhere — pure visual storytelling only. Composition leaves "
    "comfortable empty negative space on the upper-left for typography to be "
    "added later."
)


JOBS = [
    (
        "ecosystem_chapter_hero",
        "16:9",
        [
            "08_pandora.jpg",          # Pandora — silver-haired pixar woman in suit
            "luna_character.png",       # Luna — long-ponytail Asian woman, black blazer, coffee cup
            "partner_raccoon_hero.png", # Raccoon — friendly cyber-raccoon mascot
            "ref_rytho_robot.png",      # Rytho — Daft-Punk-style black-helmet music mannequin
        ],
        "GROUP SCENE — 4 hero characters hanging out together in a friendly "
        "Pixar / Disney concert-stage jam session, like a cute keynote band. "
        "Re-imagine the same characters from the references in the same "
        "warm Pixar 3D aesthetic, all standing on a soft pastel stage with "
        "abundant negative space.\n\n"
        "PANDORA on the right side: same silver-bobbed Pixar Asian "
        "businesswoman from the reference (light grey blazer, white shirt, "
        "warm smile), holding a translucent glowing data-orb in her hand "
        "like a microphone, mid-song.\n\n"
        "LUNA on the left side: same young Asian woman from the reference "
        "with the long dark-brown ponytail, sharp black blazer suit, large "
        "expressive eyes — she is dancing playfully and holding her "
        "smartphone, with a soft trail of glowing pastel social-media post "
        "bubbles spilling out of the phone (no readable text on them, just "
        "soft glyphs and emoji-like dots).\n\n"
        "RACCOON AI in the front-left: a small adorable cyber-raccoon "
        "mascot identical to the reference design — soft grey fur with "
        "darker striped tail and eye-mask, cyan glowing chest-gem accents, "
        "big friendly cartoon eyes — playing a small floating futuristic "
        "synth keytar that emits little cyan music notes.\n\n"
        "RYTHO MUSIC ROBOT in the front-right: faithfully use the same "
        "design as the Rytho reference — a tall slim mannequin-style 3D "
        "music agent, body and torso jet-black with smooth matte finish "
        "and subtle cyan/blue edge lighting, with a perfectly spherical "
        "JET-BLACK glossy DAFT-PUNK-style helmet head featuring a thin "
        "horizontal glowing cyan audio-waveform ring across the face, "
        "standing on a small circular pedestal that glows cyan-blue at "
        "the base, one arm raised mid-dance and the other hand holding a "
        "small chrome-tipped microphone wand. Translucent pastel-purple "
        "sound waves rise behind it. Make this character read clearly as "
        "a friendly Daft-Punk-style DJ helmet figure but keep it cute and "
        "premium, not menacing.\n\n"
        "A soft glowing rainbow data ribbon (pastel cyan → orange → "
        "violet → amber) flows BETWEEN the four characters like floating "
        "stage spotlights — implying the open A2A ecosystem linking them, "
        "the music itself made visible. The background is a soft daylight "
        "concert stage with cumulus clouds and a pastel cyan-to-amber "
        "gradient sky, plenty of breathing room. Camera: slight low "
        "angle, wide cinematic 16:9, the four characters arranged across "
        "the lower-right two-thirds of the frame so the UPPER-LEFT "
        "quadrant stays as clean empty sky for typography to be added "
        "later. Mood: optimistic, joyful, premium, friendly. NO text, "
        "NO letters, NO logos, NO readable signage anywhere."
    ),
]


def call_api(prompt: str, refs: list, aspect: str,
             attempt: int = 1, max_attempts: int = 3) -> bytes | None:
    parts = []
    for r in refs:
        parts.extend(load_ref(r, r))
    parts.append({"text": prompt})
    parts.append({"text": STYLE})

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
            return call_api(prompt, refs, aspect, attempt + 1, max_attempts)
        return None

    if r.status_code != 200:
        print(f"  http {r.status_code}: {r.text[:500]}")
        if r.status_code in (429, 500, 502, 503, 504) and attempt < max_attempts:
            time.sleep(10 * attempt)
            return call_api(prompt, refs, aspect, attempt + 1, max_attempts)
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
    for i, (name, aspect, refs, prompt) in enumerate(JOBS, 1):
        if only and name not in only:
            continue
        existing = list(OUT.glob(f"{name}.*"))
        if existing and not only:
            print(f"[{i}/{total}] {name}: SKIP (exists)")
            continue
        if existing and only:
            for e in existing:
                e.unlink()
            print(f"[{i}/{total}] {name}: regenerating (forced)...")
        t0 = time.time()
        print(f"[{i}/{total}] {name}: generating ({aspect}, {len(refs)} refs)...", flush=True)
        data = call_api(prompt, refs, aspect)
        if data is None:
            print(f"[{i}/{total}] {name}: FAILED")
            continue
        ext = "png" if data[:8] == b"\x89PNG\r\n\x1a\n" else "jpg"
        out = OUT / f"{name}.{ext}"
        out.write_bytes(data)
        print(f"[{i}/{total}] {name}: saved {out.name} ({len(data)//1024} KB, {time.time()-t0:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
