"""
Generate Harness diagram v4

v4 改動 (基於 v3):
- 標題改為「MULTI-AGENT × HARNESS ENGINEERING 打造的協作架構」
  副標「The Pocket Company framework · by TSpace」
- 中間 LLM orb 拿掉 Claude/GPT/Gemini, 改成「SOTA 模型 or 地端模型」
- 左邊 Harness manual 改成明確雙欄: SKILL + TOOL (兩個核心元件)
- Tool Universe 多畫 fan-up 線: Tool 不只被 Agent 用,
  也可以被「打包」進 Harness ── 這是 Harness Engineering 的精髓
- 保留 v3 的 A2A mesh + Tool Universe

Outputs: img/harness_as_llm_input_v4.jpg
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
    "pandora":   OUT_DIR / "08_pandora.jpg",
    "moana":     OUT_DIR / "09_moana.jpg",
    "banana":    OUT_DIR / "10_banana.jpg",
    "adriana":   OUT_DIR / "11_adriana.jpg",
    "stacey":    OUT_DIR / "12_stacey.jpg",
    "v3_anchor": OUT_DIR / "harness_as_llm_input_v3.jpg",   # v3 layout as base
    "anchor":    OUT_DIR / "aios_infographic_v3.jpg",        # palette discipline
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
    "isometric 3D illustrations consistent with the scene. "
    "NO stray typography style notes like 'JetBrains Mono' as visible text."
)


PROMPT = """
Design ONE 16:9 keynote hero illustration — a SINGLE UNIFIED SCENE,
not a multi-column infographic. The whole image is ONE Pixar-style 3D
stage that flows TOP → MIDDLE → BOTTOM, telling the story in one glance.

THE STORY THIS IMAGE TELLS:

  Harness Engineering ──
  把 SKILL + TOOL 整捆塞進一個 LLM (SOTA 或地端) 的眼裡,
  LLM 召喚出 5 個 Agent, Agent 之間用 A2A 協作,
  Agent 再從 Tool 通往各種真實資料源 (虛擬 + 實體世界)。
  下面的 Tool Universe 不只被 Agent 用 ── 也會被「打包」回左邊的
  Harness 裡, 形成一個自我演進的協作架構。

ONE CONTINUOUS scene. NO column dividers. NO separate cards.

LAYOUT (single 16:9 frame):

TOP STRIP (about 12% of frame height):
  Centred big bold heading (deep slate #0f172a), TWO LINES:
     Line 1 (English, larger):
        MULTI-AGENT × HARNESS ENGINEERING
     Line 2 (Traditional Chinese, slightly smaller, slate-700):
        打造的協作架構
  Directly below, a small mono uppercase tag (cyan):
        THE POCKET COMPANY FRAMEWORK · by TSpace

MAIN STAGE (about 68% of frame height, warm off-white background):

  LEFT FOURTH — HARNESS MANUAL (SKILL + TOOL):
    A 3D open book / manual standing upright at a slight angle, with
    a clear divider down the middle of the open spread, showing TWO
    distinct sections side-by-side ON the open pages:
       LEFT page  — header "SKILL" (orange, JetBrains Mono uppercase)
                    listing in mono text:
                       skill.md
                       examples/
                       scripts/
                       prompts/
       RIGHT page — header "TOOL" (cyan, JetBrains Mono uppercase)
                    listing in mono text:
                       tools/
                       schemas
                       MCP defs
                       APIs
    Below the pages, a small slate band reads:
       HARNESS  =  SKILL  +  TOOL
    Spine of the book reads "HARNESS" in orange uppercase mono.
    Small file motes / glyphs drift up off both pages and float
    diagonally rightwards towards the central LLM orb, with subtle
    orange-cyan rim glow.

  CENTRE — LLM RUNTIME ORB:
    A translucent 3D brain / orb in violet-cyan gradient, floating
    mid-air, soft subsurface scattering — same Pixar quality as the
    reference characters. The orb is RECEIVING the harness stream
    from the LEFT.
    Around the orb, three small floating mono labels (NOT brand
    names, ONLY generic capability tags):
       "SOTA MODEL"   "ON-PREM MODEL"   "地端模型"
    Directly under the orb, a small cyan mono label:
       LLM RUNTIME · MODEL-AGNOSTIC
    And a Traditional Chinese sub-label (slate-500, smaller):
       SOTA 模型 or 地端模型 ── 模型可換, Harness 不變
    Do NOT include brand names like Claude / GPT / Gemini anywhere
    in this scene.

  RIGHT HALF — A2A AGENT MESH:
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

    A2A MESH — draw thin glowing CYAN A2A connection lines forming
    a MESH between the 5 agents themselves (Pandora↔Moana, Moana↔
    Banana, Banana↔Adriana, Adriana↔Stacey, plus diagonal cross-
    links). Faint chat-bubble glyphs or small <A2A> tags floating
    between the agents reinforce the collaboration vibe.
    A single thin cyan line connects the WHOLE huddle back to the
    orb on its left (not five separate lines from the orb).

    A small cyan mono label floats above the huddle:
       A2A PROTOCOL · MULTI-AGENT COLLABORATION
    Below the huddle, agent name labels (small mono):
       Pandora   Moana   Banana   Adriana   Stacey

  FLOW VISUALS:
    Soft glowing motes / light particles streaming LEFT → CENTRE →
    RIGHT. NO arrows, NO column dividers — just light flow.

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

  TWO sets of subtle lines emerge from this Tool Universe band:
    (1) Thin slate lines fan UP-RIGHT from the tools into the
        5 agents above — agents reach into tools at runtime.
    (2) Thin DASHED orange lines fan UP-LEFT from the tools into
        the HARNESS manual's TOOL page on the far left — meaning
        these same tools can also be PACKAGED into the Harness
        itself. This is the key idea of "Harness Engineering":
        tools flow IN both directions.
  Keep both line sets subtle, not noisy. A tiny mono caption near
  the leftward dashed lines reads:
        "tools 也可以被打包進 Harness"

  At the very bottom of this band, a single emerald mono uppercase
  label, BOLD:
     AGENT ACTION — 自己選工具 · 召喚 Multi-Agent · 自己決定怎麼做

DESIGN GUIDANCE:
- ONE CONTINUOUS scene. Everything flows:
  HARNESS (Skill + Tool) → LLM Runtime → A2A Agent Mesh → Tool
  Universe → back UP into Harness.
- The 5 agents MUST clearly match the references (faces, outfits,
  hair, props). Same Pixar 3D quality.
- The A2A mesh between agents and the Skill + Tool split inside
  the Harness manual are the TWO key new visuals — make them
  the most readable details after the orb.
- TOOL UNIVERSE band must NOT use generic stock clip-art icons.
- The split between LEFT GROUP (virtual) and RIGHT GROUP (physical)
  in the tool universe should be subtle — same band, but the right
  group has slight orange tint.
- Calm, premium, optimistic. NOT cyberpunk. NOT cluttered.
- DO NOT print any style notes like "JetBrains Mono" as standalone
  visible labels in the scene.
- DO NOT show brand names Claude / GPT / Gemini.

TEXT ACCURACY — verify every character renders correctly:
- English:
   "MULTI-AGENT × HARNESS ENGINEERING"
   "THE POCKET COMPANY FRAMEWORK · by TSpace"
   "LLM RUNTIME · MODEL-AGNOSTIC"
   "SOTA MODEL"   "ON-PREM MODEL"
   "A2A PROTOCOL · MULTI-AGENT COLLABORATION"
   "HARNESS  =  SKILL  +  TOOL"
   "TOOLS — VIRTUAL & PHYSICAL WORLD"
   "AGENT ACTION — 自己選工具 · 召喚 Multi-Agent · 自己決定怎麼做"
   "HARNESS", "SKILL", "TOOL" (manual headers)
   "Pandora", "Moana", "Banana", "Adriana", "Stacey"
   manual SKILL page: skill.md, examples/, scripts/, prompts/
   manual TOOL  page: tools/, schemas, MCP defs, APIs
   tool labels: Database, Data Lake, CDP, MDP, BigQuery,
                POS 機, 刷卡機, IoT 感測.
- Traditional Chinese (exact forms):
   "打造的協作架構"
   "地端模型"
   "SOTA 模型 or 地端模型 ── 模型可換, Harness 不變"
   "Tool 的豐富性 ── 從資料倉到 POS 機,從雲端到收銀台"
   "tools 也可以被打包進 Harness"
   "自己選工具 · 召喚 Multi-Agent · 自己決定怎麼做"

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
    out_name = sys.argv[1] if len(sys.argv) > 1 else "harness_as_llm_input_v4"

    refs = [
        load_ref("v3_anchor", "Previous v3 layout — keep LEFT manual / CENTRE orb / RIGHT agents / BOTTOM tools structure"),
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
