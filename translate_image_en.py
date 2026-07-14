"""Re-render text-bearing diagram images into English, keeping the exact
layout / colours / characters. Uses nano-banana-pro (Gemini image) with the
original image as the primary reference and an explicit EN text mapping.

Outputs English-named variants so the Chinese deck keeps the originals:
  img/moana_culture_flow_v2_en.jpg
  img/harness_as_llm_input_v11b_final_en.jpg
"""
import base64
import json
import mimetypes
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / "tpc-launch" / ".env")

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise SystemExit("Set GEMINI_API_KEY in tpc-launch/.env")
MODEL = "nano-banana-pro-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
IMG = ROOT / "img"


def img_part(path: Path):
    mime, _ = mimetypes.guess_type(str(path))
    if path.suffix.lower() == ".png":
        mime = "image/png"
    mime = mime or "image/jpeg"
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(path.read_bytes()).decode()}}


def generate(src: Path, out_name: str, instruction: str):
    parts = [
        {"text": "This is the SOURCE infographic. Recreate it EXACTLY — same layout, "
                 "same composition, same colours, same icons, same characters/mascots, "
                 "same fonts and text positions/sizes — but TRANSLATE ALL TEXT TO ENGLISH "
                 "using the mapping below. Do not move, add or remove any element. "
                 "Every English word must be spelled correctly and fit its box. "
                 "Output a single crisp 16:9 image."},
        img_part(src),
        {"text": instruction},
    ]
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9"},
        },
    }
    for attempt in range(1, 4):
        try:
            r = requests.post(URL, json=payload, timeout=300)
        except requests.RequestException as e:
            print(f"  request error: {e} (retry {attempt})")
            time.sleep(5 * attempt)
            continue
        if r.status_code != 200:
            print(f"  http {r.status_code}: {r.text[:400]}")
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(10 * attempt)
                continue
            return False
        data = r.json()
        for cand in data.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    raw = base64.b64decode(inline["data"])
                    ext = "png" if raw[:8] == b"\x89PNG\r\n\x1a\n" else "jpg"
                    out = IMG / f"{out_name}.{ext}"
                    out.write_bytes(raw)
                    print(f"  saved {out.name} ({len(raw)//1024} KB)")
                    return True
        print("  no image in response:", json.dumps(data, ensure_ascii=False)[:400])
        time.sleep(4 * attempt)
    return False


CULTURE = """
TEXT MAPPING (Traditional Chinese -> English), keep each in the SAME position:

TITLE (top, bold black): "Culture Listening — Integrated Insight"
TITLE PILL (orange, under title): "Culture-Signal Integration Engine"

LEFT column tag: "INPUT"
LEFT five cards (bold word + small caption):
  1. "Industry"     / "Market dynamics · Industry trends"
  2. "Brand"        / "Brand voice · Consumer sentiment"
  3. "Competitors"  / "Competitor moves · Content strategy"
  4. "Creators"     / "KOL views · Creator content"
  5. "Culture"      / "Social issues · Pop culture"

CENTRE orb tag: "ENGINE"
CENTRE orb text (stacked):
  big: "Culture Listening"
  under it: "Culture-Signal Integration Engine"
  small two lines: "Context understanding · Sentiment detection"
                   "Trend detection · Meaning extraction"

RIGHT three items (with icons):
  "Content inspiration"
  "Communication strategy"
  "Actionable playbooks"

RIGHT green OUTPUT box tag: "OUTPUT"
  bold: "Actionable Application"
  small: "Content × Communication × Growth"

BOTTOM three pills:
  "Grasp real context & sentiment"
  "See trends, memes & community pulse"
  "Turn culture insight into content inspiration"

BOTTOM italic line (orange, centred):
  "With culture at the core — content with more meaning, brands with more resonance"

Keep the orange gradient, the curly-hair woman mascot with pink megaphone, the orb,
the arrows and all icons EXACTLY as in the source. Only the text changes to English.
"""

HARNESS = """
The source is ALREADY mostly English. Change ONLY the Traditional Chinese
subtitle under the main title from "打造的協作架構" to the English:
   "The Collaboration Architecture We Build"
Keep the top title "THE POCKET COMPANY FRAMEWORK powered by [TSpace logo]" and
the pill "MULTI-AGENT × HARNESS ENGINEERING ·" — replace the trailing Chinese
"打造的協作架構" so the pill reads:
   "MULTI-AGENT × HARNESS ENGINEERING · THE COLLABORATION ARCHITECTURE WE BUILD"
Everything else (SKILL/TOOL manual, Gemini Pro / Claude Opus / Turncloud VIN
cards, the 5 character agents, A2A arrows,
the bottom "Tools — Digital & Physical World" band with Database/Data Lake/CDP/
MDP/BigQuery/POS/Card Reader/IoT Sensor, and "AGENT ACTION") stays EXACTLY the
same, all English, same layout and colours.

CRITICAL: the five agent name labels under the characters on the right MUST be
spelled EXACTLY and correctly, left to right:
   "Pandora"  "Moana"  "Banana"  "Adriana"  "Stacey"
Do NOT misspell "Moana" (it is NOT "Mcana"). Double-check every label.
"""


JOBS = {
    "culture": ("moana_culture_flow_v2.jpg", "moana_culture_flow_v2_en", CULTURE),
    "harness": ("harness_as_llm_input_v11b_final.jpg", "harness_as_llm_input_v11b_final_en", HARNESS),
}


def main():
    which = sys.argv[1:] or list(JOBS.keys())
    rc = 0
    for key in which:
        src_name, out_name, instr = JOBS[key]
        src = IMG / src_name
        print(f"[{key}] {src_name} -> {out_name}")
        if not generate(src, out_name, instr):
            print(f"[{key}] FAILED")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
