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


LUNA = """
TEXT MAPPING (Traditional Chinese -> English), keep each in the SAME position,
same orange colour, same fonts and sizes:

TOP-LEFT heading (orange bold): "爆文機器人"  ->  "Viral-Post Bot"
TOP-LEFT sub (slate): "AI 內容生成引擎"  ->  "AI Content Engine"

Four orange pills (centre, top to bottom):
  "品牌痛點"    ->  "Brand pain points"
  "粉絲偏好"    ->  "Fan preferences"
  "客製化主題"  ->  "Custom topics"
  "爆文公式"    ->  "Viral formula"

Orange circle badge (two lines):
  "AI 處理"  ->  "AI in"
  "/ 60 秒"  ->  "/ 60 sec"

Bottom orange pill (centred):
  "30 秒產出 · 客製化 · 即買即用"  ->  "30-sec output · customized · ready to use"

Keep the 3D woman mascot (Luna) holding a coffee cup with the "CREATOR SUMMIT 2025 / LUNA"
lanyard EXACTLY the same. Keep the phone mockup on the right (its "Threads post / Preview"
UI stays as-is). Keep the confetti, background and all colours identical. Only the
Chinese text becomes English.
"""


RACCOON = """
TEXT MAPPING (Traditional Chinese -> English), keep each in the SAME position,
same colours, same layout, same fonts/sizes. Keep it concise so text fits.

RIGHT SIDE:
  Pill tag: "AI 智能客服解決方案"  ->  "AI CUSTOMER-SERVICE SOLUTION"
  Big heading (two lines):
     "把 AI 客服嵌入"   ->  "Embed AI customer service"
     "你的品牌 App"     ->  "into your brand App"
  Sub (two lines, grey):
     "消費者問什麼，AI 都答得出來──"    ->  "Whatever shoppers ask, the AI answers ──"
     "精品推薦、樓層導覽、促銷活動，一次搞定。" -> "product picks, floor guide, promos — all in one."
  Three bullets (bold title + grey caption):
     "自然語言理解" / "懂中文語境，能理解模糊問法與意圖"
        -> "Natural-language understanding" / "Grasps context, handles vague questions & intent"
     "即時商品與樓層查詢" / "連結後台資料，推薦精準且即時更新"
        -> "Real-time product & floor lookup" / "Linked to backend data, accurate & always current"
     "串接任何 App 或平台" / "透過 API 快速整合，一週即可上線"
        -> "Connects to any App or platform" / "Fast API integration, live in a week"
  "Powered by  Raccoon AI"  -> keep as-is (Raccoon AI is a brand name)

LEFT PHONE CHAT MOCKUP (translate every bubble, keep the same bubble layout/colours):
  Header title: "精品百貨 AI 客服"  ->  "Department Store AI Concierge"
  Header status (green): "線上服務中"  ->  "Online now"
  Date divider: "今天"  ->  "Today"
  User bubble 1 (blue): "媽媽節快到了，想送禮給媽媽，有推薦嗎？"
     -> "Mother's Day is near — any gift ideas for mom?"
  AI label: "AI 客服助理"  ->  "AI Assistant"
  AI bubble 1 (grey): "您好！幫您精選母親節熱門禮品，以下是本週百貨推薦 🎁"
     -> "Hi! Here are this week's top Mother's Day picks 🎁"
  (keep the two small product image thumbnails)
  User bubble 2 (blue): "SK-II 的禮盒在哪？現在有優惠嗎？"
     -> "Where are the SK-II gift sets? Any deals now?"
  AI bubble 2 (grey): "SK-II 專櫃位於 B2 美妝區，今日營業至 21:30"
     -> "SK-II counter is on B2 (Beauty), open till 21:30 today"
  Promo card (orange): "母親節限定優惠" / "滿 $3,000 樓層量販券，並累積點數回饋 5%"
     -> "Mother's Day special" / "Spend $3,000 for a floor voucher + 5% points back"
  Input placeholder: "輸入您的問題..."  ->  "Type your question..."
  Bottom brand label "Raccoon AI" stays as-is.

Keep the raccoon mascot, the phone frame ("9:41" time, signal/wifi icons), the blue
gradient background and ALL colours EXACTLY the same. Only the text becomes English.
Every English word must be spelled correctly.
"""


JOBS = {
    "culture": ("moana_culture_flow_v2.jpg", "moana_culture_flow_v2_en", CULTURE),
    "harness": ("harness_as_llm_input_v11b_final.jpg", "harness_as_llm_input_v11b_final_en", HARNESS),
    "luna": ("luna_hero_composite.jpg", "luna_hero_composite_en", LUNA),
    "raccoon": ("partner_raccoon_hero.png", "partner_raccoon_hero_en", RACCOON),
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
