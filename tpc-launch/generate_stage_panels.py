"""
Generate per-panel iconic illustrations for the new stage-style deck.

Each icon is a SQUARE flat-vector illustration that sits inside a panel card
with a coloured halo glow. Matches the bright Pixar-meets-product-page
aesthetic established by anim_runtime_iso / anim_aios_orb / anim_agents_ring.
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
        {"text": f"Reference — {label}: keep this aesthetic and quality."},
        {
            "inline_data": {
                "mime_type": mime,
                "data": base64.b64encode(path.read_bytes()).decode(),
            }
        },
    ]


STYLE = (
    "STYLE: clean flat-vector icon illustration in the bright, warm "
    "Pixar-meets-product-page aesthetic. Soft global illumination, rounded "
    "shapes, abundant whitespace, premium SaaS landing-page energy. NO neon "
    "glow, NO cyberpunk. The image is a single focused icon that sits inside "
    "a rounded card. STRICTLY NO TEXT, NO LETTERS, NO LABELS, NO WATERMARKS, "
    "NO READABLE SIGNAGE. Soft drop shadow."
)


JOBS = [
    # ─── SLIDE 2: MERGER (3 panels) ───
    ("icon_legacy_infra", "4:3", ["anim_runtime_iso.jpg"],
     "ORANGE/AMBER PALETTE (#f59e0b, #fbbf24, #fed7aa). Isometric 3/4 view of "
     "a small store with: a sleek POS counter (no readable text), a smart "
     "phone scanner on the counter, an IoT camera with WiFi waves on the "
     "wall, and in the background a small office building and a small "
     "factory rooftop. Friendly architectural icon scene, no people, soft "
     "white floor. Conveys '20 years of business infrastructure'."),

    ("icon_agent_team", "4:3", ["anim_agents_ring.jpg"],
     "VIOLET PALETTE (#a855f7, #c084fc with cyan accents #06b6d4). A circular "
     "ring of FIVE small abstract head-silhouette character avatars in soft "
     "Pixar style, evenly spaced around a glowing central spark of light. "
     "The silhouettes have simple coloured fills: silver-grey, brown-curly, "
     "banana-yellow, brunette, dark-ponytail. Thin violet A2A protocol lines "
     "connect adjacent avatars. Conveys 'a team of 5 AI agents'."),

    ("icon_fusion", "4:3", ["anim_aios_orb.jpg"],
     "CYAN PALETTE with subtle violet+orange accents. Centre: two rounded "
     "interlocking puzzle pieces or two overlapping rings — one tinted "
     "warm-orange (representing legacy enterprise), one tinted cool-violet "
     "(representing AI agents) — fusing into a single bright cyan hexagonal "
     "core in the middle, with very soft outer glow rings. The fusion point "
     "is the visual focus. Conveys 'two worlds merging into one'."),

    # ─── SLIDE 3: RUNTIME (3 panels) ───
    ("icon_runtime_engine", "4:3", ["anim_runtime_iso.jpg"],
     "ORANGE PALETTE (#f59e0b base). A clean isometric depiction of a small "
     "glowing engine / core processor sitting on a slab platform, with three "
     "or four softly glowing energy lines flowing outward to small floating "
     "device icons (a phone, a sensor, a tablet — minimal silhouettes). "
     "Conveys 'the runtime that powers everything'."),

    ("icon_four_abilities", "1:1", ["anim_aios_orb.jpg"],
     "ORANGE-TO-AMBER palette. A clean 2x2 quadrant tile arrangement, "
     "each quadrant containing ONE simple flat-vector glyph (NO TEXT). The "
     "four glyphs are: an EYE (sense), a BRAIN SHAPE (reason), a CHOICE "
     "FORK/COMPASS (decide), and a LIGHTNING BOLT or HAND (act). Each "
     "quadrant has its own subtle tint variation but stays in the warm "
     "palette. Centre connector dot. Conveys 'four capabilities of "
     "physical-space runtime'."),

    ("icon_challenge", "4:3", ["anim_aios_orb.jpg"],
     "CYAN-VIOLET palette transitioning. A small isometric runway/road with "
     "a glowing question-mark hovering above an open doorway at the far end. "
     "The road is paved with hexagonal tiles in alternating cyan tones. "
     "Conveys 'the challenge ahead — how do we make AI a working system?'. "
     "Light, hopeful, NOT ominous."),

    # ─── SLIDE 4: PROBLEM (3 panels) ───
    ("icon_scattered_tools", "4:3", ["anim_aios_orb.jpg"],
     "PINK/ROSE PALETTE (#ec4899 with soft pastel pink #fbcfe8 background). "
     "A scene showing 4-6 disconnected small AI tool icons floating "
     "AWAY from each other in different directions — each a different "
     "shape (a magnifying glass, a speech bubble, a chart bar, a brush, a "
     "robot face). No connecting lines between them. Conveys 'each "
     "department uses AI alone, fragmented'."),

    ("icon_disconnected", "4:3", ["anim_aios_orb.jpg"],
     "MUTED CYAN-GREY palette. Three or four broken chain links lying on a "
     "soft surface, slightly offset from each other, with very subtle red "
     "warning dots near the breaks. Minimalist composition. Conveys "
     "'fragmented data / agents not collaborating / governance scattered'."),

    ("icon_unify_os", "4:3", ["anim_aios_orb.jpg"],
     "CYAN PALETTE (#06b6d4). A clean funnel shape — wide at top with "
     "many small scattered icons flowing INTO it, narrow at bottom emitting "
     "ONE bright cyan hexagonal core. Above the funnel, the chaos of "
     "many tools; below, the order of one unified system. Conveys 'unifying "
     "all AI into one enterprise OS'."),

    # ─── SLIDE 7: AI OS (2 panels) ───
    ("icon_eight_modules", "4:3", ["anim_aios_orb.jpg"],
     "CYAN PALETTE. A clean 2x4 (or 3x3-with-centre) grid of EIGHT rounded "
     "hex tiles, each tile containing ONE simple symbolic flat-vector glyph "
     "(NO TEXT). The eight glyphs represent: database, brain (memory), "
     "flowchart (workflow), robot (agents), shield (permission), eye "
     "(observability), checkmark (governance), and decision tree. All in "
     "soft cyan tints. Conveys 'AI OS manages 8 things in one place'."),

    ("icon_user_memory", "4:3", ["anim_agents_ring.jpg"],
     "VIOLET PALETTE (#a855f7). A simple cute character head-silhouette in "
     "the centre with a soft glowing brain shape rendered above it, and 3-4 "
     "memory orbs orbiting at different depths. Below the head, a small "
     "padlock icon indicating private memory. Conveys 'each user has their "
     "own private long-term memory — their personal AI'."),
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
