"""
Generate the "Harness as LLM Input" diagram — UNIFIED SCENE VERSION.

v2 改動：
- 不再分三欄, 改成「一張連續的場景圖」
- 加入 5 個 Agent 角色 (Pandora/Moana/Banana/Adriana/Stacey)
- 簡化文字, 突出視覺敘事:
    左:  HARNESS Manual (一本發光的厚冊)
    中:  LLM Brain Orb (吸收 manual 內容)
    右:  5 個 Agent 從 orb 召喚出來
- 像一個 Pixar 風格的 keynote hero illustration

Outputs: img/harness_as_llm_input_v2.jpg
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

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise SystemExit("Set GEMINI_API_KEY (or GOOGLE_API_KEY) env var before running.")
MODEL = "nano-banana-pro-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

OUT_DIR = ROOT / "img"
OUT_DIR.mkdir(exist_ok=True)

REFS = {
    "pandora":  OUT_DIR / "08_pandora.jpg",
    "moana":    OUT_DIR / "09_moana.jpg",
    "banana":   OUT_DIR / "10_banana.jpg",
    "adriana":  OUT_DIR / "11_adriana.jpg",
    "stacey":   OUT_DIR / "12_stacey.jpg",
    "anchor":   OUT_DIR / "aios_infographic_v3.jpg",
}


def load_ref(name: str, label: str) -> list:
    path = REFS[name]
    if not path.exists():
        print(f"  missing ref {path.name}, skipping")
        return []
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "image/jpeg"
    if path.suffix.lower() == ".png":
        mime = "image/png"
    return [
        {"text": f"Reference — {label}: keep character identity / face / outfit consistent."},
        {
            "inline_data": {
                "mime_type": mime,
                "data": base64.b64encode(path.read_bytes()).decode(),
            }
        },
    ]


STYLE = (
    "STYLE: Premium Pixar-style 3D keynote hero illustration with a warm, "
    "optimistic mood. Soft subsurface scattering on characters, big "
    "expressive eyes, warm studio rim lighting. Bright clean backdrop, NOT "
    "cyberpunk. Mood: like a Linear / Stripe / Anthropic announcement page. "
    "PALETTE: warm off-white #faf7f2 base, cyan #0891b2 primary accent, "
    "orange #f59e0b for the harness manual, violet #a855f7 for the LLM orb, "
    "emerald #10b981 for the bottom CTA, deep slate #0f172a for headings. "
    "TYPOGRAPHY: confident sans-serif for headings (Inter / Noto Sans CJK), "
    "JetBrains-Mono small caps for technical labels. ALL text crisp and "
    "CORRECTLY SPELLED. NO watermarks. NO photorealism. NO cluttered icons."
)


PROMPT = """
Design ONE 16:9 keynote hero illustration — a SINGLE UNIFIED SCENE,
not a three-column infographic, not a card layout. The whole image is
ONE Pixar-style 3D stage that flows left-to-right and tells the story
in one glance.

THE STORY (in one continuous scene):
  HARNESS AS LLM INPUT —
  寫好的 Skill 整捆塞進 LLM 的眼裡,
  然後 LLM 召喚出 5 個 Agent 自己完成任務。

The viewer sees, left to right, in ONE flowing scene:
  1) An open glowing HARNESS manual on the LEFT,
     its pages streaming as structured text & tags into...
  2) A softly glowing LLM brain orb in the CENTRE (violet+cyan),
     which is "reading" the harness — from the other side of the orb...
  3) The 5 CHARACTER AGENTS emerge on the RIGHT,
     summoned by the harness, each starting their work.

NO column dividers. NO separate cards. ONE continuous illustrated stage.

LAYOUT (single 16:9 frame):

TOP STRIP (very thin, about 10% of frame height):
  Centre, big bold heading (deep slate #0f172a):
     HARNESS AS LLM INPUT
  Below it, smaller subtitle (slate-700, centred):
     把 Skill 變成模型今天的「輸入」 — LLM 看完整捆 Harness, 召喚 5 個 Agent

MAIN STAGE (about 80% of frame height, warm off-white background):

  LEFT THIRD of the stage:
    A large 3D open book / manual standing upright at a slight angle.
    Cover spine reads "HARNESS" in JetBrains Mono uppercase, orange.
    Open pages show structured prompt markers in mono text:
       <skill>
       <tools>
       <examples>
       <context>
    Small file icons drift up off the pages (skill.md, tools/,
    examples/, scripts/) and float diagonally towards the centre,
    like soft glowing motes. A subtle orange-cyan rim glow on the book.

  CENTRE of the stage:
    A translucent 3D brain / orb in violet-cyan gradient, floating
    mid-air, soft subsurface scattering — same Pixar quality as the
    reference characters. The orb is RECEIVING the stream of harness
    pages from the left into its left side.
    Around the orb, three small floating mono labels (small, not noisy):
       "Claude"   "GPT"   "Gemini"
    Below the orb, a small cyan mono label:
       LLM · CONTEXT WINDOW
    And a sub-label (slate-500, smaller):
       Harness 就是這個模型今天的 input

  RIGHT THIRD of the stage:
    The FIVE CHARACTER AGENTS emerge from the RIGHT side of the orb,
    as if summoned by what the LLM just read. Render each one in
    Pixar 3D, FAITHFUL to the provided character references:
      • Pandora — silver-haired woman in grey suit
      • Moana   — curly-afro woman with pink megaphone in orange tee
      • Banana  — yellow banana mascot with round glasses, bow tie
      • Adriana — brunette woman with round glasses, sage-green
                  blazer, holding a glowing tablet
      • Stacey  — sleek dark-brown high-ponytail woman in dark-navy
                  blazer with thin gold buttons, small holographic stylus
    Arrange the 5 agents in a slight diagonal arc emerging from the
    orb — each mid-action, gestures suggesting they're starting work.
    Thin glowing cyan A2A connection lines link each agent back to
    the orb (not noisy — calm and clean).
    A tiny mono name label sits below each character:
       Pandora    Moana    Banana    Adriana    Stacey

  FLOW VISUALS connecting everything:
    Soft glowing motes / light particles streaming left → centre → right.
    NO arrows, NO column dividers, NO card outlines — just light flow.

BOTTOM STRIP (about 10% of frame height):
  A single slate-thin horizontal line spans the scene.
  Centre label (emerald #10b981 mono uppercase, BOLD):
     AGENT ACTION — 自己決定怎麼做
  Below it (slate-500, smaller, centred):
     傳統 Tool Calling 受限於 schema · 新方式 Harness 是 Input · LLM 召喚 Agent 團隊

DESIGN GUIDANCE:
- ONE CONTINUOUS scene. The viewer should feel "left flows into centre
  flows into right" without any visible boundary.
- The 5 agents MUST be clearly recognisable and match the references
  (faces, outfits, hair, props). Same Pixar 3D quality.
- Calm, premium, optimistic. NOT cyberpunk. NOT cluttered.
- Generous breathing room around the orb.
- Soft glow, not neon. Slate / cream is the base, colour is for accent.

TEXT ACCURACY — verify every character renders correctly:
- English: "HARNESS AS LLM INPUT",
  "LLM · CONTEXT WINDOW",
  "AGENT ACTION — 自己決定怎麼做",
  "Claude", "GPT", "Gemini" (floating around orb),
  "Pandora", "Moana", "Banana", "Adriana", "Stacey" (agent labels),
  on the manual spine: "HARNESS",
  on the manual pages: <skill>, <tools>, <examples>, <context>,
  file names floating: skill.md, tools/, examples/, scripts/.
- Traditional Chinese (exact forms — do not paraphrase):
  把 Skill 變成模型今天的「輸入」
  LLM 看完整捆 Harness, 召喚 5 個 Agent
  Harness 就是這個模型今天的 input
  自己決定怎麼做
  傳統 Tool Calling 受限於 schema
  新方式 Harness 是 Input · LLM 召喚 Agent 團隊

NO watermarks. NO signatures. NO decorative extra noise.
The image should look like a single Pixar + Stripe / Anthropic-tier
hero illustration that could be the cover of an AI keynote video.
"""


def call_api(prompt, refs, attempt=1, max_attempts=3):
    parts = []
    for ref_parts in refs:
        parts.extend(ref_parts)
    parts.append({"text": prompt})
    parts.append({"text": STYLE})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "16:9"},
        },
    }

    try:
        r = requests.post(URL, json=payload, timeout=300)
    except requests.RequestException as e:
        print(f"  request error: {e}")
        if attempt < max_attempts:
            time.sleep(5 * attempt)
            return call_api(prompt, refs, attempt + 1, max_attempts)
        return None

    if r.status_code != 200:
        print(f"  http {r.status_code}: {r.text[:600]}")
        if r.status_code in (429, 500, 502, 503, 504) and attempt < max_attempts:
            time.sleep(10 * attempt)
            return call_api(prompt, refs, attempt + 1, max_attempts)
        return None

    data = r.json()
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])
    print("  no image in response; preview:", json.dumps(data, ensure_ascii=False)[:500])
    return None


def main():
    out_name = sys.argv[1] if len(sys.argv) > 1 else "harness_as_llm_input_v2"

    refs = [
        load_ref("pandora", "Pandora — silver-hair Agent"),
        load_ref("moana",   "Moana — curly-afro content Agent"),
        load_ref("banana",  "Banana — yellow mascot Agent"),
        load_ref("adriana", "Adriana — brunette analyst Agent"),
        load_ref("stacey",  "Stacey — orchestrator Agent"),
        load_ref("anchor",  "AIOS infographic — keep palette/typography style"),
    ]
    refs = [r for r in refs if r]

    print(f"generating {out_name} ... ({len(refs)} refs)", flush=True)
    t0 = time.time()
    data = call_api(PROMPT, refs)
    if data is None:
        print("FAILED")
        return 1
    ext = "png" if data[:8] == b"\x89PNG\r\n\x1a\n" else "jpg"
    out = OUT_DIR / f"{out_name}.{ext}"
    out.write_bytes(data)
    print(f"saved {out.name} ({len(data) // 1024} KB, {time.time() - t0:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
