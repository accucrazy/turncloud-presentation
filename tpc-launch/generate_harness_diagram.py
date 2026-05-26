"""
Generate the "Harness as LLM Input" architecture diagram.

Thesis: Harness Skill 變成 LLM 的 Input — Agent 不再只是 call tool,
而是 LLM 看完一整捆 Harness (skill + tools + examples + context),
然後自己決定怎麼組合。

Style: Same Pixar-meets-modern-product-page DNA as the existing
aios_infographic — warm off-white, cyan/orange/violet, clean glassmorphism.

Outputs: img/harness_as_llm_input.jpg
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

# ─── Reference library: 5 Agent characters + style anchors ────────────────
REFS = {
    "pandora":  OUT_DIR / "08_pandora.jpg",
    "moana":    OUT_DIR / "09_moana.jpg",
    "banana":   OUT_DIR / "10_banana.jpg",
    "adriana":  OUT_DIR / "11_adriana.jpg",
    "stacey":   OUT_DIR / "12_stacey.jpg",
    "aios_anchor": OUT_DIR / "aios_infographic_v3.jpg",  # palette discipline
    "anim_ring":   OUT_DIR / "anim_agents_ring.jpg",     # flow language reference
}


def load_ref(name: str, label: str) -> list:
    path = REFS[name]
    if not path.exists():
        print(f"  ⚠ ref missing: {path.name} (skipping)")
        return []
    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "image/jpeg"
    if path.suffix.lower() == ".png":
        mime = "image/png"
    return [
        {"text": f"Reference — {label}: keep this visual identity / style / quality."},
        {
            "inline_data": {
                "mime_type": mime,
                "data": base64.b64encode(path.read_bytes()).decode(),
            }
        },
    ]


# ─── Brand-aware style brief (matches generate_aios_infographic.py) ─────────
STYLE = (
    "STYLE: Premium enterprise-keynote infographic with a warm, optimistic feel — "
    "marries clean product-page typography (Linear / Stripe / Vercel landing pages) "
    "with the bright Pixar-style 3D character DNA from the references. "
    "PALETTE: warm off-white background #faf7f2, cyan #0891b2 as primary accent, "
    "orange #f59e0b for the 'Skill Bundle' axis, violet #a855f7 for the "
    "'LLM' axis, emerald #10b981 for the result strip, "
    "deep slate #0f172a for headings. "
    "CARDS: large rounded rectangles (24px radius), very soft elevation shadow, "
    "thin coloured top border, abundant interior padding. "
    "TYPOGRAPHY: confident sans-serif (Inter / Noto Sans CJK), tight letter "
    "spacing on headings, JetBrains-Mono small caps for the section labels. "
    "ALL text crisp and CORRECTLY SPELLED — verify every character. "
    "ARROWS / CONNECTORS: thin slate lines with rounded chevrons, NOT neon glowing. "
    "FORBID: photorealistic photography, neon cyberpunk glow, dark backgrounds, "
    "AI-slop fluorescent gradients, stock-icon-pack iconography, watermarks."
)

# ─── Diagram prompt: Harness Skill → LLM Input ──────────────────────────────
PROMPT = """
Design a single 16:9 hero infographic for an enterprise AI keynote slide.

═══════════════════════════════════════════════════════════════════════════
HEADLINE THESIS (the entire point of this diagram):

  HARNESS AS LLM INPUT
  把 Skill 變成模型的「輸入」 ──
  Agent 不再只是 call tool,
  而是 LLM 看完整捆 Harness (skill + tools + examples + context),
  自己決定怎麼組合。

The audience must see in one glance THREE THINGS flowing left → right:
  ZONE 1  Skill Bundle (a folder of files, orange)
  ZONE 2  Harness — compiles Skill Bundle into prompt context (cyan)
  ZONE 3  LLM — receives the harness as its input, decides Agent action (violet)
And at the bottom: the AGENT ACTION result strip (emerald).
═══════════════════════════════════════════════════════════════════════════

LAYOUT (top-to-bottom):

┌─────────────────────────────────────────────────────────────────────┐
│  ZONE 0 · HEADER (full width, cyan rounded card, ~13% of height)    │
│                                                                       │
│  Big bold heading (left-aligned, dark slate #0f172a):                 │
│     HARNESS AS LLM INPUT                                              │
│  Smaller subtitle directly below (slate-700):                         │
│     把 Skill 變成模型的「輸入」 ── Agent 不再只是 call tool             │
│  On the right side of the same header, in JetBrains Mono uppercase:   │
│     SKILL ▸ HARNESS ▸ LLM ▸ AGENT                                     │
│  Tiny pill row at the very bottom of the header (cyan tags):          │
│     skill.md · tools · examples · scripts · context · A2A             │
└─────────────────────────────────────────────────────────────────────┘

ZONE 1 · LEFT CARD (~32% width) — SKILL BUNDLE 一捆能力
──────────────────────────────────────────────────────
Visual mood: warm orange top accent, structured folder feel.
Caption strip (orange #f59e0b mono): SKILL BUNDLE — 一捆能力
Heading: Skill Bundle
Subheading: 寫一次, 帶得走的能力包

Inside the card, render an illustrated "folder" containing FOUR file-card rows
stacked vertically, each with a small icon + filename + one-line caption:
   📄  skill.md       自然語言能力描述
   🛠   tools/         可呼叫的工具集
   📚  examples/      範例與案例
   ⚙   scripts/       子流程腳本

Below the stack, a tidy bullet list (slate text):
   • 不是 API, 而是一捆檔案
   • Skill 可以熱抽換 · 版本控管
   • 任何 LLM 都能讀懂

Card footer (mono, slate-500):
   A bundle of files, not an API.

ZONE 2 · CENTER CARD (~22% width) — HARNESS · COMPILER
──────────────────────────────────────────────────────
Visual mood: cyan top accent, "pipeline" feel.
Caption strip (cyan #0891b2 mono): HARNESS · COMPILER
Heading: Harness
Subheading: 把整捆 Skill 序列化成 prompt context

Inside the card, render a stylised pipeline / funnel:
   Multiple file icons (flowing from the left zone) converge into ONE
   structured prompt document with visible section markers labelled:
     <skill>...</skill>
     <tools>...</tools>
     <examples>...</examples>
     <context>...</context>

Bullet list (slate text):
   • 不再受 schema 限制
   • 整捆 Skill 變成 LLM 的眼睛能看到的脈絡
   • Harness = 新的 system prompt

Card footer (mono, slate-500):
   Harness = the new system prompt.

ZONE 3 · RIGHT CARD (~32% width) — LLM · CONTEXT WINDOW
───────────────────────────────────────────────────────
Visual mood: violet top accent, bright optimistic — NOT cyberpunk.
Caption strip (violet #a855f7 mono): LLM · CONTEXT WINDOW
Heading: LLM
Subheading: Harness 就是這個模型今天的 input

Inside the card, render a stylised brain / orb glowing softly violet —
visualise the harness document being absorbed into it as a stream of
structured content (file icons / tag blocks) entering the model. The
brain should NOT be sci-fi cyberpunk; treat it like a 3D illustration
in the style of the reference characters.

Floating around the brain (small holographic glyphs, NOT noisy):
   "Claude"  "GPT"  "Gemini"  "Stacey"
showing the model is interchangeable.

Bullet list (slate text):
   • 看完整捆 Harness 才開始推理
   • 自己選工具 · 自己排順序 · 自己處理錯誤
   • 不用重新部署 Agent — 換 Skill 就好

Card footer (mono, slate-500):
   The model reads the harness like a person reads a manual.

ZONE 4 · BOTTOM RESULT STRIP (full width, emerald accent, ~12% height)
──────────────────────────────────────────────────────────────────────
A thin horizontal band connecting all three zones.
Centre label (emerald #10b981 mono uppercase, BOLD):
   AGENT ACTION — 自己決定怎麼做
Below it a tiny slate caption:
   傳統 Tool Calling 受限於 schema · 新方式 Harness 是 Input · LLM 自由組合 Skill

═══════════════════════════════════════════════════════════════════════════
FLOW ARROWS
───────────
Three slate arrows (thin lines with rounded chevrons, NOT neon glowing),
connecting the cards horizontally:
   ZONE 1 ─►  ZONE 2  ─►  ZONE 3  ─▼  ZONE 4

DESIGN GUIDANCE
- The THREE upper cards must feel visually parallel — same card shape,
  same heading hierarchy, same footer position — but their interiors
  should clearly differ in mood (orange folder / cyan pipeline / violet brain).
- ZONE 3 is the diagram's hero — it embodies "Harness AS LLM input".
- Generous breathing room; calm, premium feel.

TEXT ACCURACY — VERIFY EVERY CHARACTER:
- English: "HARNESS AS LLM INPUT",
  "SKILL ▸ HARNESS ▸ LLM ▸ AGENT",
  "SKILL BUNDLE — 一捆能力",
  "HARNESS · COMPILER",
  "LLM · CONTEXT WINDOW",
  "AGENT ACTION — 自己決定怎麼做",
  "A bundle of files, not an API.",
  "Harness = the new system prompt.",
  "The model reads the harness like a person reads a manual.".
- Traditional Chinese (use these exact forms):
  把 Skill 變成模型的「輸入」
  寫一次, 帶得走的能力包
  把整捆 Skill 序列化成 prompt context
  Harness 就是這個模型今天的 input
  不再受 schema 限制
  整捆 Skill 變成 LLM 的眼睛能看到的脈絡
  看完整捆 Harness 才開始推理
  自己選工具 · 自己排順序 · 自己處理錯誤
  不用重新部署 Agent — 換 Skill 就好
  傳統 Tool Calling 受限於 schema
  新方式 Harness 是 Input · LLM 自由組合 Skill
  自己決定怎麼做
- File names spelled exactly: skill.md, tools/, examples/, scripts/.

No watermarks, no signatures, no extra decorative noise.
The image should look like a Series-B announcement page hero diagram
that a Linear / Stripe / Anthropic-tier designer would ship.
"""


def call_api(prompt: str, refs: list, attempt: int = 1, max_attempts: int = 3) -> bytes | None:
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
    out_name = sys.argv[1] if len(sys.argv) > 1 else "harness_as_llm_input"

    refs = [
        load_ref("aios_anchor", "AIOS infographic — keep palette/layout/typography"),
        load_ref("anim_ring",   "agents-ring composition — flow language reference"),
        load_ref("stacey",      "Stacey — orchestrator portrait, for any character cameo"),
    ]
    refs = [r for r in refs if r]  # drop missing ones

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
