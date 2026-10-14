"""Pandora -> Culture Listening -> Banana : the real experiment pipeline.

For each brand/market:
  1. SIGNAL   pull real posts from Pandora (/api/public/query)
  2. CULTURE  Gemini text model reads the actual posts and extracts a culture
              brief: verbatim consumer phrases, pain points, hooks in the
              local language, and visual directions
  3. CREATIVE nano-banana renders the visuals from those directions
  4. RECORD   everything (evidence chain) lands in data/experiments.json

The point is not "AI can make pretty pictures" — it is that the copy and the
angle come from what people actually said this week. That is the moat.
"""
import base64
import json
import os
import re
import time
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT.parent / "turncloud-presentation" / "tpc-launch" / ".env")

PANDORA_KEY = os.environ.get("PANDORA_API_KEY") or exit("set PANDORA_API_KEY env var")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
PANDORA = "https://pandora.thepocket.company/api/public"
TEXT_MODEL = "gemini-2.5-pro"
IMG_MODEL = "nano-banana-pro-preview"

DATA = ROOT / "data"
ASSETS = ROOT / "assets"
DATA.mkdir(exist_ok=True)
ASSETS.mkdir(exist_ok=True)

EXPERIMENTS = [
    {
        "id": "cvs_coffee",
        "market": "TW",
        "lang": "zh-Hant",
        "brand": "超商咖啡（以全家為例）",
        "keyword": "星巴克",
        "hypothesis": "洞察常常藏在競品的討論串裡：搜「星巴克」反而找到超商咖啡的機會點。",
        "reuse": "brand_e6989fe5b7.json",
        "n_images": 2,
    },
    {
        "id": "family_mart",
        "market": "TW",
        "lang": "zh-Hant",
        "brand": "全家 FamilyMart",
        "keyword": "全家",
        "hypothesis": "品牌詞雜訊很高（政治文、生活文都會提到「全家」）— 測試工作流的過濾層。",
        "reuse": "brand_e585a8e5.json",
        "n_images": 2,
    },
    {
        "id": "paragon_th",
        "market": "TH",
        "lang": "th",
        "brand": "Siam Paragon（泰國）",
        "keyword": "พารากอน",
        "hypothesis": "Pandora 已涵蓋泰國 Threads — 測海外市場：泰文貼文能否直出在地素材。",
        "reuse": None,
        "n_images": 2,
    },
    {
        "id": "fitness_tw",
        "market": "TW",
        "lang": "zh-Hant",
        "brand": "健身／蛋白質品類",
        "keyword": "健身",
        "hypothesis": "不給品牌只給品類：測「品類聆聽」能不能自己長出切角（如早餐蛋白質）。",
        "reuse": "brand_e581a5e8.json",
        "n_images": 2,
    },
]


# ── step 1 · signal ──────────────────────────────────────────────

def find_reuse(prefix_hint, keyword):
    """brand_*.json filenames were hex-truncated; match by stored keyword."""
    for f in DATA.glob("brand_*.json"):
        obj = json.loads(f.read_text(encoding="utf-8"))
        if obj.get("brand") == keyword:
            return obj
    return None


def fetch_posts(keyword):
    end = date.today()
    start = end - timedelta(days=14)
    r = requests.post(f"{PANDORA}/query", headers={"x-api-key": PANDORA_KEY}, json={
        "table": "precise", "searchExpression": keyword,
        "startDate": start.isoformat(), "endDate": end.isoformat(), "limit": 12,
    }, timeout=180)
    obj = r.json()
    if not obj.get("success"):
        raise RuntimeError(f"pandora {keyword}: {obj}")
    return obj


# ── step 2 · culture brief ───────────────────────────────────────

BRIEF_PROMPT = """你是 Moana，The Pocket Company 的 Culture Listening agent。
下面是 Pandora 從 Threads 抓回來的「真實貼文」（品牌/品類：{brand}，市場：{market}）。

你的工作不是想像消費者，是「聽」他們：
1. 找出真正有內容價值的貼文（忽略無關雜訊，但要記下雜訊比例）
2. 抄下他們的原話（verbatim，保留原語言的口語感）
3. 從原話裡長出創意切角，寫出 {lang} 的社群文案 hook（要像真人發文，不是廣告腔）
4. 為視覺生成寫兩個英文 visual prompt（乾淨、無文字、社群感、符合在地生活場景）

回傳 JSON（只回 JSON）：
{{
 "noise_ratio": 0.0到1.0之間，多少比例的貼文其實與品牌/品類無關,
 "insight": "一句話說出這批貼文裡最值錢的洞察（{lang}）",
 "consumer_phrases": ["3-5句消費者原話，一字不改"],
 "pain_points": ["2-3個痛點或渴望（{lang}）"],
 "hooks": [
   {{"angle": "切角名（{lang}）", "copy": "一段可直接發的社群文案，用消費者的語感寫（{lang}），60字內"}},
   ...共3個
 ],
 "visual_prompts": ["english prompt 1", "english prompt 2"],
 "workflow_note": "這次實驗學到什麼工作流經驗（繁體中文，給內部看）"
}}

真實貼文：
{posts}
"""


def gemini_text(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TEXT_MODEL}:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
    }
    for attempt in range(1, 4):
        r = requests.post(url, json=payload, timeout=300)
        if r.status_code != 200:
            print(f"   text http {r.status_code}: {r.text[:200]}")
            time.sleep(10 * attempt)
            continue
        try:
            txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(txt)
        except Exception as e:
            print(f"   text parse err {e}")
            time.sleep(5 * attempt)
    return None


# ── step 3 · creative ────────────────────────────────────────────

IMG_STYLE = (" Premium social-media creative, authentic local lifestyle, natural light,"
             " shallow depth of field, editorial minimalism, generous negative space."
             " Looks like a real Instagram post, NOT a stock photo."
             " ABSOLUTELY NO text, NO letters, NO logos, NO watermarks.")


def gemini_image(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{IMG_MODEL}:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt + IMG_STYLE}]}],
        "generationConfig": {"responseModalities": ["IMAGE"],
                             "imageConfig": {"aspectRatio": "1:1"}},
    }
    for attempt in range(1, 4):
        try:
            r = requests.post(url, json=payload, timeout=300)
        except requests.RequestException:
            time.sleep(8 * attempt)
            continue
        if r.status_code != 200:
            print(f"   img http {r.status_code}: {r.text[:150]}")
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(12 * attempt)
                continue
            return None
        for c in r.json().get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                inline = p.get("inlineData") or p.get("inline_data")
                if inline and inline.get("data"):
                    return base64.b64decode(inline["data"])
        time.sleep(6 * attempt)
    return None


# ── main ─────────────────────────────────────────────────────────

def main():
    results = []
    for exp in EXPERIMENTS:
        print(f"\n=== {exp['id']} ({exp['market']}) — {exp['brand']} ===", flush=True)

        # 1 · signal
        obj = find_reuse(exp.get("reuse"), exp["keyword"])
        if obj is None:
            print("   fetching fresh from Pandora ...")
            obj = fetch_posts(exp["keyword"])
            safe = re.sub(r"[^a-z0-9]", "", exp["id"])
            (DATA / f"brandx_{safe}.json").write_text(
                json.dumps({"brand": exp["keyword"], **obj}, ensure_ascii=False, indent=1),
                encoding="utf-8")
        posts = obj.get("posts", [])
        print(f"   posts: {len(posts)}")
        if not posts:
            print("   SKIP (no data)")
            continue

        posts_txt = "\n".join(
            f"- @{p.get('author')} (讚{p.get('likes',0)}/情緒{p.get('sentiment','?')}): "
            f"{(p.get('content') or '')[:220]}"
            for p in posts)

        # 2 · culture brief
        print("   culture listening (gemini) ...", flush=True)
        brief = gemini_text(BRIEF_PROMPT.format(
            brand=exp["brand"], market=exp["market"], lang=exp["lang"], posts=posts_txt))
        if not brief:
            print("   BRIEF FAILED")
            continue
        print(f"   insight: {brief.get('insight','')[:80]}")
        print(f"   noise_ratio: {brief.get('noise_ratio')}")

        # 3 · creative
        images = []
        for i, vp in enumerate(brief.get("visual_prompts", [])[: exp["n_images"]], 1):
            print(f"   image {i} ...", flush=True)
            data = gemini_image(vp)
            if data:
                name = f"exp_{exp['id']}_{i}.jpg"
                (ASSETS / name).write_bytes(data)
                images.append(name)
                print(f"   saved {name} ({len(data)//1024} KB)")

        results.append({
            "id": exp["id"], "market": exp["market"], "lang": exp["lang"],
            "brand": exp["brand"], "keyword": exp["keyword"],
            "hypothesis": exp["hypothesis"],
            "postCount": len(posts),
            "evidence": [{
                "author": p.get("author"), "content": (p.get("content") or "")[:130],
                "likes": p.get("likes", 0), "sentiment": p.get("sentiment"),
                "url": p.get("url"),
            } for p in posts[:5]],
            "brief": brief,
            "images": images,
        })

    out = DATA / "experiments.json"
    out.write_text(json.dumps({"generatedAt": time.strftime("%Y-%m-%d %H:%M"),
                               "experiments": results}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"\nDONE — {len(results)} experiments -> {out.name} ({out.stat().st_size//1024} KB)")


if __name__ == "__main__":
    main()
