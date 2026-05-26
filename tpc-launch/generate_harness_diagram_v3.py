"""
Generate Harness diagram v3 — adds A2A multi-agent collaboration mesh
and TOOL UNIVERSE (data sources + physical-world data).

v3 改動 (基於 v2):
- 5 個 Agent 之間用 A2A 線互相連 (不是 hub-spoke, 是 agent-to-agent mesh)
- 底部新增 TOOL UNIVERSE: Database / Data Lake / CDP / MDP / BigQuery
  + 實體世界資料 (POS / 刷卡機 / IoT)
- 整張圖仍是一個連貫場景, 不分欄

Outputs: img/harness_as_llm_input_v3.jpg
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
    "v2_anchor": OUT_DIR / "harness_as_llm_input_v2.jpg",  # v2 layout 作為構圖基準
    "anchor":    OUT_DIR / "aios_infographic_v3.jpg",       # palette discipline
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
        {"text": f"Reference — {label}: keep character identity / face / outfit / palette consistent."},
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
    "cyberpunk. Mood: Linear / Stripe / Anthropic announcement page. "
    "PALETTE: warm off-white #faf7f2 base, cyan #0891b2 primary accent, "
    "orange #f59e0b for the harness manual, violet #a855f7 for the LLM orb, "
    "emerald #10b981 for the bottom CTA, deep slate #0f172a for headings. "
    "TYPOGRAPHY: confident sans-serif for headings (Inter / Noto Sans CJK), "
    "JetBrains-Mono small caps for technical labels. ALL text crisp and "
    "CORRECTLY SPELLED. NO watermarks. NO photorealism. NO cluttered icons. "
    "NO stock-icon-pack iconography — render data source icons as small "
    "isometric 3D illustrations consistent with the scene."
)


PROMPT = """
Design ONE 16:9 keynote hero illustration — a SINGLE UNIFIED SCENE,
not a multi-column infographic. The whole image is ONE Pixar-style 3D
stage that flows TOP-to-BOTTOM and LEFT-to-RIGHT, telling the story
in one glance.

THE STORY THIS IMAGE TELLS:

  HARNESS AS LLM INPUT —
  寫好的 Skill 整捆塞進 LLM 的眼裡,
  LLM 召喚出 5 個 Agent 互相 A2A 協作,
  Agent 們再從 Tool 接到各種資料源 ── 包含實體世界的 POS、刷卡機、IoT。

The viewer must see in one glance:
  1) LEFT  : a glowing open HARNESS manual streaming pages.
  2) CENTRE: a softly-glowing LLM brain orb reading the harness.
  3) RIGHT : the 5 CHARACTER AGENTS emerging from the orb,
             linked by A2A lines into a MESH (agent-to-agent, not just
             agent-to-orb) — it must read as a TEAM collaborating.
  4) BOTTOM (full-width band): the TOOL UNIVERSE — small icons for
     databases, data lake, CDP, MDP, BigQuery, and PHYSICAL-WORLD
     icons (POS terminal, credit-card reader, IoT sensor). Each
     Agent has a thin slate line fanning down into the tool universe,
     showing the Agents reach into real data — both digital and physical.

ONE CONTINUOUS SCENE. NO column dividers. NO separate cards.

LAYOUT (single 16:9 frame):

TOP STRIP (about 10% of frame height):
  Centre, big bold heading (deep slate #0f172a):
     HARNESS AS LLM INPUT
  Below it, smaller subtitle (slate-700, centred):
     Skill 是 LLM 的 Input · Agent 用 A2A 協作 · Tool 通向虛擬與實體世界

MAIN STAGE (about 70% of frame height, warm off-white background):

  LEFT FOURTH of the stage — HARNESS MANUAL:
    A 3D open book / manual standing upright at a slight angle.
    Spine reads "HARNESS" in JetBrains Mono uppercase, orange.
    Open pages show structured prompt markers in mono text:
       <skill>
       <tools>
       <examples>
       <context>
    Small file icons drift up off the pages (skill.md, tools/,
    examples/, scripts/) and float diagonally towards the centre,
    like soft glowing motes. Subtle orange-cyan rim glow.

  CENTRE of the stage — LLM ORB:
    A translucent 3D brain / orb in violet-cyan gradient, floating
    mid-air, soft subsurface scattering — same Pixar quality as the
    reference characters. The orb is RECEIVING the harness stream
    from the left into its left side.
    Around the orb, three small floating mono labels:
       "Claude"   "GPT"   "Gemini"
    Below the orb, a small cyan mono label:
       LLM · CONTEXT WINDOW
    And a sub-label (slate-500, smaller):
       Harness 就是這個模型今天的 input

  RIGHT HALF of the stage — A2A AGENT MESH:
    The FIVE CHARACTER AGENTS emerge from the RIGHT side of the orb
    and form a SMALL COLLABORATING TEAM. Render each one in Pixar 3D,
    FAITHFUL to the provided character references:
      • Pandora — silver-haired woman in grey suit
      • Moana   — curly-afro woman with pink megaphone in orange tee
      • Banana  — yellow banana mascot with round glasses, bow tie
      • Adriana — brunette woman with round glasses, sage-green
                  blazer, holding a glowing tablet
      • Stacey  — sleek dark-brown high-ponytail woman in dark-navy
                  blazer with thin gold buttons, small holographic stylus
    Arrange them in a loose huddle / arc — clearly turned towards
    each other (NOT facing outwards). Each one mid-action.

    CRITICAL — A2A MESH (this is the new emphasis):
    Draw thin glowing CYAN A2A connection lines forming a MESH between
    the 5 agents themselves — Pandora↔Moana, Moana↔Banana, Banana↔
    Adriana, Adriana↔Stacey, plus diagonal cross-links — so it reads
    like a TEAM of agents talking to each other, NOT a hub-and-spoke
    diagram. Faint chat-bubble glyphs or small <A2A> tags floating
    between the agents reinforce the collaboration vibe.
    A single thin cyan line connects the WHOLE huddle back to the orb
    on its left (not five separate lines from the orb).

    A small cyan mono label floats above the huddle:
       A2A PROTOCOL · MULTI-AGENT COLLABORATION
    Below the huddle, agent name labels (small mono):
       Pandora   Moana   Banana   Adriana   Stacey

  FLOW VISUALS:
    Soft glowing motes / light particles streaming left → centre →
    right. NO arrows, NO column dividers — just light flow.

BOTTOM BAND (about 20% of frame height) — TOOL UNIVERSE:
  A subtle horizontal band that spans the full width of the frame,
  slightly recessed (very soft slate gradient). Centred small label
  at the very top of this band (cyan mono uppercase):
     TOOLS — VIRTUAL & PHYSICAL WORLD
  A short sub-caption (slate-500, centred):
     Tool 的豐富性 ── 從資料倉到 POS 機,從雲端到收銀台

  Below the labels, draw EIGHT small isometric 3D data-source icons
  spread across the width, each with a tiny mono label below it.
  LEFT GROUP (virtual / data, cyan-tinted):
     • Database     — small 3D cylinder (database stack)
     • Data Lake    — flat circular lake icon with data ripples
     • CDP          — customer data platform icon (people + data)
     • MDP          — marketing data platform icon (chart + audience)
     • BigQuery     — 3D table grid icon
  RIGHT GROUP (physical / real world, orange-tinted):
     • POS 機       — 3D point-of-sale terminal (small isometric)
     • 刷卡機       — 3D credit-card reader
     • IoT 感測     — small isometric sensor / camera icon

  Thin slate lines fan down from EACH of the 5 agents above into
  this tool universe band — every agent reaches into multiple tools.
  The lines are subtle, NOT noisy.

  At the very bottom of this band, a single emerald mono uppercase
  label, BOLD:
     AGENT ACTION — 自己選工具 · 召喚 Multi-Agent · 自己決定怎麼做

DESIGN GUIDANCE:
- ONE CONTINUOUS scene. The viewer should feel everything flows:
  HARNESS → LLM → AGENT MESH → TOOLS.
- The 5 agents MUST be clearly recognisable and match the references
  (faces, outfits, hair, props). Same Pixar 3D quality.
- The A2A mesh between agents is the KEY new visual — make it the
  most readable detail after the orb.
- TOOL UNIVERSE band must NOT use generic stock clip-art icons — use
  the same warm Pixar 3D illustration style as the rest of the scene.
- The split between LEFT GROUP (virtual) and RIGHT GROUP (physical)
  in the tool universe should be subtle — same band, but the right
  group has slight orange tint to suggest "real-world physical".
- Calm, premium, optimistic. NOT cyberpunk. NOT cluttered.

TEXT ACCURACY — verify every character renders correctly:
- English: "HARNESS AS LLM INPUT",
  "LLM · CONTEXT WINDOW",
  "A2A PROTOCOL · MULTI-AGENT COLLABORATION",
  "TOOLS — VIRTUAL & PHYSICAL WORLD",
  "AGENT ACTION — 自己選工具 · 召喚 Multi-Agent · 自己決定怎麼做",
  "Claude", "GPT", "Gemini" (floating around orb),
  "Pandora", "Moana", "Banana", "Adriana", "Stacey" (agent labels),
  "HARNESS" (manual spine),
  manual pages: <skill>, <tools>, <examples>, <context>,
  file motes: skill.md, tools/, examples/, scripts/,
  tool labels: Database, Data Lake, CDP, MDP, BigQuery, POS 機,
              刷卡機, IoT 感測.
- Traditional Chinese (exact forms):
  Skill 是 LLM 的 Input · Agent 用 A2A 協作 · Tool 通向虛擬與實體世界
  Harness 就是這個模型今天的 input
  Tool 的豐富性 ── 從資料倉到 POS 機,從雲端到收銀台
  自己選工具 · 召喚 Multi-Agent · 自己決定怎麼做
  POS 機 · 刷卡機 · IoT 感測

NO watermarks. NO signatures. NO decorative extra noise.
The image should look like a single Pixar + Stripe / Anthropic-tier
hero illustration that could be the cover of a 2026 AI keynote.
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
    out_name = sys.argv[1] if len(sys.argv) > 1 else "harness_as_llm_input_v3"

    refs = [
        load_ref("v2_anchor", "Previous v2 layout — keep the LEFT manual / CENTRE orb / RIGHT agents structure"),
        load_ref("pandora",   "Pandora — silver-hair Agent"),
        load_ref("moana",     "Moana — curly-afro content Agent"),
        load_ref("banana",    "Banana — yellow mascot Agent"),
        load_ref("adriana",   "Adriana — brunette analyst Agent"),
        load_ref("stacey",    "Stacey — orchestrator Agent"),
        load_ref("anchor",    "AIOS infographic — palette/typography discipline"),
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
