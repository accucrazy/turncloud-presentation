"""
Generate the AI OS · Agent Orchestrated Space hero infographic.

Thesis: Data × Agent = Business Value.
Style: bright Pixar-meets-modern-product-page — keeps the deck's character
DNA (cyan/orange/violet, soft glassmorphism, 3D character portraits as
agent badges) while staying infographic-clean and high-information-density.

Outputs: img/aios_infographic_v3.jpg
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
OUT_DIR = ROOT / "img"
OUT_DIR.mkdir(exist_ok=True)

# ─── Reference library: characters + visual anchors ────────────────────────
REFS = {
    "pandora":  OUT_DIR / "08_pandora.jpg",
    "moana":    OUT_DIR / "09_moana.jpg",
    "banana":   OUT_DIR / "10_banana.jpg",
    "adriana":  OUT_DIR / "11_adriana.jpg",
    "stacey":   OUT_DIR / "12_stacey.jpg",
    "all_hands": OUT_DIR / "07_workforce.jpg",
    "infographic_anchor": OUT_DIR / "aios_infographic_v2.jpg",  # for layout discipline
}


def load_ref(name: str, label: str) -> list:
    path = REFS[name]
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


# ─── Brand-aware style brief ───────────────────────────────────────────────
STYLE = (
    "STYLE: Premium enterprise-keynote infographic with a warm, optimistic feel — "
    "marries clean product-page typography (Linear / Stripe / Vercel landing pages) "
    "with the bright Pixar-style 3D character DNA from the references. "
    "PALETTE: warm off-white background #faf7f2, cyan #0891b2 as primary accent, "
    "orange #f59e0b for the 'physical / real-world' axis, violet #a855f7 for the "
    "'virtual / digital' axis, emerald #10b981 for the value KPI numbers, "
    "deep slate #0f172a for headings. "
    "CARDS: large rounded rectangles (24px radius), very soft elevation shadow, "
    "thin coloured top border, abundant interior padding. "
    "TYPOGRAPHY: confident sans-serif (Inter / Noto Sans CJK), tight letter "
    "spacing on headings, JetBrains-Mono small caps for the section labels and KPI "
    "captions. ALL text crisp and CORRECTLY SPELLED — verify every character. "
    "AGENT AVATARS: render each as a small circular portrait (~120px), 3D Pixar "
    "style consistent with the reference character renders — soft subsurface "
    "scattering, big expressive eyes, warm studio lighting. "
    "ARROWS / CONNECTORS: thin slate lines with rounded chevrons, NOT neon glowing. "
    "FORBID: photorealistic photography, neon cyberpunk glow, dark backgrounds, "
    "AI-slop fluorescent gradients, stock-icon-pack iconography, watermarks."
)

# ─── The duality-focused infographic prompt ────────────────────────────────
PROMPT = """
Design a single 16:9 hero infographic for an enterprise AI keynote slide.

═══════════════════════════════════════════════════════════════════════════
HEADLINE THESIS (the entire point of this diagram):

  AI OS · Agent Orchestrated Space
  「Space」既可以是【實體】也可以是【虛擬】 ──
   • 實體空間 = AI 走進真實人、場、貨的場域
   • 虛擬空間 = Agent 之間互相協作、分工、編排的場域

The audience must see in one glance that "Space" is NOT just one thing —
it has a dual nature. The LEFT card shows AI reaching into the physical
world. The RIGHT card IS the digital space WHERE THE 5 AGENTS LIVE AND
COLLABORATE with each other through A2A protocol.
═══════════════════════════════════════════════════════════════════════════

LAYOUT (top-to-bottom):

┌─────────────────────────────────────────────────────────────────────┐
│  ZONE 0 · HEADER (full width, cyan rounded card, ~14% of height)    │
│                                                                       │
│  Big bold heading (left-aligned, dark slate):                         │
│     AI OS · Agent Orchestrated Space                                  │
│  Smaller subtitle directly below (slate-700):                         │
│     「Space」可以是實體，也可以是虛擬 ── 同一套 AI OS 編排兩種空間      │
│  On the right side of the same header, in JetBrains Mono uppercase:   │
│     PHYSICAL  ／  VIRTUAL  ── ONE OS, TWO SPACES                      │
│  Tiny pill row at the very bottom of the header (cyan tags):          │
│     Orchestrator · A2A · MCP · Memory · Policy · Governance            │
└─────────────────────────────────────────────────────────────────────┘

ZONE 1 · LEFT (50%) — PHYSICAL SPACE 實體空間
─────────────────────────────────────────────
Visual mood: warm, sunlit, real-world. Orange top accent.
Caption strip at the top of the card (orange mono):
   PHYSICAL SPACE — where AI serves the real world
Heading: 實體空間
Subheading: AI 走進真實的人、場、貨
A clean illustrated stage inside the card — show a small isometric or
flat-vector scene of a real-world business environment, with iconic
elements (you may freely choose composition):
   🏪  零售店 / 商場 / 飯店 / 工廠 with people walking through it
   🧾  POS / HOYABOX terminal on a counter
   📡  IoT sensors / cameras tracking 動線
   👥  real customers and staff
Below the scene, a tidy bullet list (slate text):
   • POS · HOYABOX · 收銀終端
   • 店流 · 動線 · IoT 感測
   • 工廠 · 商場 · 飯店
   • 真實的人 · 場 · 貨
Card footer (mono, slate-500):
   via Physical Space Runtime

ZONE 2 · RIGHT (50%) — VIRTUAL SPACE 虛擬空間 (= AGENT ORCHESTRATED SPACE)
─────────────────────────────────────────────────────────────────────────
Visual mood: bright digital workspace with subtle violet glow on edges,
NOT cyberpunk — clean, optimistic, like a holographic team meeting room.
Violet top accent.
Caption strip at the top of the card (violet mono):
   VIRTUAL SPACE — where Agents collaborate
Heading: 虛擬空間
Subheading: Agent 之間互相溝通、分工、協作的工作空間

Inside the card, render a small "agent collaboration room" scene where
the FIVE CHARACTER AGENTS are working together. Render each as a 3D
Pixar-style character portrait CONSISTENT with the provided references:
   • Pandora — silver-haired woman in grey suit (top centre)
   • Moana — curly-afro woman with pink megaphone in orange tee
   • Banana — yellow banana mascot with round glasses and bow tie
   • Adriana — brunette woman with round glasses in sage-green blazer,
     holding a glowing tablet
   • Stacey — sleek dark-brown high-ponytail woman in dark-navy blazer
     with thin gold buttons, holding a small holographic stylus
The five characters should be arranged in a compact collaborative
formation (like a team huddle around a holographic table or facing each
other in a circle), connected to each other by thin glowing cyan A2A
protocol lines that visualise inter-agent messages.
Floating around them (small holographic data tags): "TCRM" "TCDP"
"BigQuery" "Meta Ads" "MCP" — showing the data they pull from.

Next to / under the scene, a small label row:
   ⦿ Pandora 輿情 · Moana 內容 · Banana 視覺 · Adriana 廣告 · Stacey 編排
Bullet list (slate text):
   • Agent 與 Agent 即時對話與分工
   • 一句指令啟動跨 Agent 工作流
   • 共享 Memory · Policy · Governance
   • 動態接 TCRM / BigQuery / Ads / SaaS 資料
Card footer (mono, slate-500):
   via A2A Protocol · MCP · Connectors

ZONE 3 · BOTTOM UNIFIER (full width, thin slate band)
──────────────────────────────────────────────────────
A single clean horizontal line connecting both cards back up to the
top header, with a label in JetBrains-Mono uppercase centred:
   ─── 同一套 AI OS · 把 AGENT 編排到任一空間執行任務 ───
Below it a tiny mono caption (slate-500):
   PHYSICAL = AI serves real people · VIRTUAL = Agents collaborate with each other

═══════════════════════════════════════════════════════════════════════════
DESIGN GUIDANCE
- The LEFT and RIGHT cards must feel visually parallel — same card shape,
  same heading hierarchy, same footer position — but their interiors
  should clearly differ in mood (warm physical world vs. bright digital
  collaboration room).
- The RIGHT card is the diagram's hero — it's the literal embodiment of
  "Agent Orchestrated Space". Spend visual weight on the 5-agent
  collaboration scene.
- Subtle A2A connection lines between the agents should be visible but
  not noisy.
- Generous breathing room; the whole image should feel calm, premium.

TEXT ACCURACY — VERIFY EVERY CHARACTER:
- English: "AI OS · Agent Orchestrated Space",
  "PHYSICAL  ／  VIRTUAL  ── ONE OS, TWO SPACES",
  "PHYSICAL SPACE — where AI serves the real world",
  "VIRTUAL SPACE — where Agents collaborate",
  "via Physical Space Runtime",
  "via A2A Protocol · MCP · Connectors".
- Traditional Chinese (use these exact forms):
  「Space」可以是實體，也可以是虛擬 ── 同一套 AI OS 編排兩種空間
  實體空間  ·  虛擬空間
  AI 走進真實的人、場、貨
  Agent 之間互相溝通、分工、協作的工作空間
  Agent 與 Agent 即時對話與分工
  一句指令啟動跨 Agent 工作流
  共享 Memory · Policy · Governance
  動態接 TCRM / BigQuery / Ads / SaaS 資料
  同一套 AI OS · 把 AGENT 編排到任一空間執行任務
- Agent names spelled exactly: Pandora, Moana, Banana, Adriana, Stacey.

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
    out_name = sys.argv[1] if len(sys.argv) > 1 else "aios_infographic_v3"

    refs = [
        load_ref("pandora",            "Pandora — silver-hair Agent"),
        load_ref("moana",              "Moana — curly-afro content Agent"),
        load_ref("banana",             "Banana — yellow mascot"),
        load_ref("adriana",            "Adriana — brunette analyst Agent"),
        load_ref("stacey",             "Stacey — orchestrator Agent"),
        load_ref("infographic_anchor", "previous infographic — for layout discipline"),
    ]

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
