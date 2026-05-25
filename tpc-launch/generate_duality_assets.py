"""
Generate clean illustration assets for the new animated AI OS Duality slide
(slide 6 — One OS, Two Spaces).

Outputs:
  img/space_physical.jpg  — clean retail/factory scene, warm orange
  img/space_virtual.jpg   — clean 5-agent collaboration scene, cool violet
  img/aios_hex_card.jpg   — clean AI OS · Agent Orchestrated Space top card
                            (hex orb + 6 chip tags, with crisp small caption)
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


REFS = {
    "pandora":  OUT / "08_pandora.jpg",
    "moana":    OUT / "09_moana.jpg",
    "banana":   OUT / "10_banana.jpg",
    "adriana":  OUT / "11_adriana.jpg",
    "stacey":   OUT / "12_stacey.jpg",
    "v4":       OUT / "aios_infographic_v4.jpg",
}


def load_ref(name: str, label: str) -> list:
    path = REFS[name]
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "image/jpeg"
    if path.suffix.lower() == ".png":
        mime = "image/png"
    return [
        {"text": f"Reference — {label}: keep this style and visual identity."},
        {
            "inline_data": {
                "mime_type": mime,
                "data": base64.b64encode(path.read_bytes()).decode(),
            }
        },
    ]


STYLE = (
    "STYLE: premium enterprise-keynote illustration in the bright, warm "
    "Pixar-meets-product-page aesthetic of the references. Clean composition, "
    "soft global illumination, abundant whitespace around the subject, "
    "rounded shapes, NO neon glow, NO cyberpunk. The image is one focused "
    "scene that will sit inside a rounded card. STRICTLY NO TEXT, NO LETTERS, "
    "NO LABELS, NO LOGOS, NO WATERMARKS, NO READABLE SIGNAGE anywhere in the "
    "image. Decorative coloured chips/badges are OK only if they remain empty "
    "(no glyphs inside)."
)


JOBS = [
    # 1) Physical Space — retail/factory scene (orange tones)
    ("space_physical", "4:3", ["pandora"],
     "A bright, friendly real-world retail interior scene rendered in soft "
     "3D Pixar style with WARM AMBER-ORANGE palette (#f59e0b, #fbbf24, "
     "#fed7aa as the dominant tones, with creamy off-white walls). "
     "Composition shows: a clean modern small store with a counter that has "
     "a sleek POS / HOYABOX-like terminal on it, a couple of happy customers "
     "browsing shelves, a small handheld scanner, a tiny IoT ceiling camera "
     "with subtle WiFi signal indicator, and through a large window in the "
     "background a sunlit city street with a small factory rooftop visible. "
     "Three-quarter low isometric camera angle. Soft drop shadow under the "
     "whole scene. The store feels warm and humanly busy — populated by "
     "real people doing real things. ABSOLUTELY NO text on signs, "
     "no readable labels, no logos."),

    # 2) Virtual Space — agent collaboration scene (violet tones)
    ("space_virtual", "4:3", ["pandora", "moana", "banana", "adriana", "stacey"],
     "A bright digital collaboration workspace rendered in the same 3D "
     "Pixar style. COOL VIOLET + CYAN palette (#a855f7, #c084fc, #06b6d4, "
     "with soft lavender-white background). Composition shows FIVE 3D "
     "character agents gathered around a circular holographic table in a "
     "modern bright glass-walled meeting pod: Pandora (silver-hair grey "
     "suit), Moana (curly afro pink megaphone orange tee), Banana mascot "
     "(yellow banana with glasses and bow tie), Adriana (brunette round "
     "glasses sage-green blazer with tablet), and Stacey (dark high "
     "ponytail dark-navy blazer with thin gold buttons, holding a small "
     "holographic stylus). They are looking at each other and gesturing — "
     "clearly collaborating. Thin glowing violet/cyan A2A protocol lines "
     "connect them through the table. Around the room, small floating "
     "decorative chips/badges hover (kept EMPTY — no letters inside them). "
     "Soft drop shadow. NO TEXT, no labels, no readable signage."),

    # 3) AI OS hex card — orchestrator centrepiece
    ("aios_hex_card", "3:1", ["v4"],
     "A clean, wide horizontal hero card layout with a soft cyan-tinted "
     "off-white interior and a 4-pixel cyan top accent border. In the "
     "centre-left of the card sits a large prominent cyan hexagonal core "
     "emblem (#06b6d4) drawn as a flat-vector mark with a few soft outer "
     "glow rings. To the right of the hex, six rounded-pill chip badges "
     "are arranged in a clean horizontal row, all in soft cyan tint, "
     "EMPTY (no glyphs inside — they are decorative). Thin connection "
     "lines link the hex to the chips. The card has soft shadow. "
     "NO TEXT inside the card."),
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
        if existing:
            print(f"[{i}/{total}] {name}: SKIP (exists)")
            continue
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
