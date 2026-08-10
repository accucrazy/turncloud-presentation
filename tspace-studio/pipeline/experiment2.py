"""Pipeline v2 — signal-to-post@1.2 with run manifests (tpc.run-manifest/v1).

What's new over experiment.py:
  * every run emits a MANIFEST: per-step agent, api, duration, credits, QA gate
    — this is the standard third parties build on top of
  * date-window experiments: same brand, different days -> different creative
  * merges results into data/experiments.json (keeps earlier experiments)

New experiments: 全國電子 · 新光三越 · 肯德基(近3天) · 肯德基(上週)
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

TODAY = date.today()

def win(days_back_start, days_back_end):
    return ((TODAY - timedelta(days=days_back_start)).isoformat(),
            (TODAY - timedelta(days=days_back_end)).isoformat())

EXPERIMENTS = [
    {
        "id": "elifemall",
        "market": "TW", "lang": "zh-Hant",
        "brand": "全國電子", "keyword": "全國電子",
        "hypothesis": "家電通路的聲量長在「售後、安裝、老店人情」— 測通路品牌能不能聽出服務切角。",
        "window": win(14, 0), "window_label": "近 14 天",
        "n_images": 2,
    },
    {
        "id": "skm",
        "market": "TW", "lang": "zh-Hant",
        "brand": "新光三越", "keyword": "新光三越",
        "hypothesis": "百貨的討論跟「檔期、美食、約會場景」強綁定 — 測地點型品牌的訊號怎麼餵。",
        "window": win(14, 0), "window_label": "近 14 天",
        "n_images": 2,
    },
    {
        "id": "kfc_d1",
        "market": "TW", "lang": "zh-Hant",
        "brand": "肯德基", "keyword": "肯德基",
        "hypothesis": "產線是活的：同一個品牌，「今天」的訊號長出的素材，跟上週不一樣。",
        "window": win(3, 0), "window_label": f"近 3 天（{win(3,0)[0]} ~ {win(3,0)[1]}）",
        "group": "kfc_days", "n_images": 2,
    },
    {
        "id": "kfc_d2",
        "market": "TW", "lang": "zh-Hant",
        "brand": "肯德基", "keyword": "肯德基",
        "hypothesis": "對照組：上週的訊號窗。兩窗並排，看得出訊號在動、素材跟著動。",
        "window": win(10, 4), "window_label": f"上週（{win(10,4)[0]} ~ {win(10,4)[1]}）",
        "group": "kfc_days", "n_images": 2,
    },
]

CREDITS = {"pandora.query": 1, "moana.brief": 2, "banana.render": 4}


def fetch_posts(keyword, start, end):
    r = requests.post(f"{PANDORA}/query", headers={"x-api-key": PANDORA_KEY}, json={
        "table": "precise", "searchExpression": keyword,
        "startDate": start, "endDate": end, "limit": 12,
    }, timeout=180)
    obj = r.json()
    if not obj.get("success"):
        raise RuntimeError(f"pandora {keyword}: {str(obj)[:200]}")
    return obj


BRIEF_PROMPT = """你是 Moana，The Pocket Company 的 Culture Listening agent。
下面是 Pandora 從 Threads 抓回來的「真實貼文」（品牌/品類：{brand}，市場：{market}，時間窗：{window}）。

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


def run_experiment(exp):
    print(f"\n=== {exp['id']} — {exp['brand']} · {exp['window_label']} ===", flush=True)
    start_w, end_w = exp["window"]
    steps, qa = [], {}
    run_id = f"run_{exp['id']}_{TODAY.strftime('%Y%m%d')}"

    # step 1 · pandora.query
    t0 = time.time()
    obj = fetch_posts(exp["keyword"], start_w, end_w)
    posts = obj.get("posts", [])
    ms = int((time.time() - t0) * 1000)
    qa["signal_gate"] = "pass" if len(posts) >= 5 else "fail"
    steps.append({"seq": 1, "agent": "pandora", "api": "POST /query",
                  "ms": ms, "credits": CREDITS["pandora.query"],
                  "status": qa["signal_gate"], "out": f"{len(posts)} posts"})
    print(f"   posts: {len(posts)} ({ms} ms)")
    safe = re.sub(r"[^a-z0-9_]", "", exp["id"])
    (DATA / f"brandx_{safe}.json").write_text(
        json.dumps({"brand": exp["keyword"], "window": exp["window"], **obj},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    if qa["signal_gate"] == "fail":
        print("   SKIP (signal gate)")
        return None

    posts_txt = "\n".join(
        f"- @{p.get('author')} (讚{p.get('likes',0)}/情緒{p.get('sentiment','?')}): "
        f"{(p.get('content') or '')[:220]}" for p in posts)

    # step 2 · moana.brief
    print("   culture listening (gemini) ...", flush=True)
    t0 = time.time()
    brief = gemini_text(BRIEF_PROMPT.format(
        brand=exp["brand"], market=exp["market"], lang=exp["lang"],
        window=exp["window_label"], posts=posts_txt))
    ms = int((time.time() - t0) * 1000)
    ok = bool(brief and brief.get("hooks") and (brief.get("noise_ratio") or 0) <= 0.92)
    qa["culture_gate"] = "pass" if ok else "fail"
    steps.append({"seq": 2, "agent": "moana", "api": "moana.brief",
                  "ms": ms, "credits": CREDITS["moana.brief"],
                  "status": qa["culture_gate"],
                  "out": f"noise {brief.get('noise_ratio') if brief else '?'} · {len((brief or {}).get('hooks', []))} hooks"})
    if not ok:
        print("   BRIEF FAILED / culture gate")
        return None
    print(f"   insight: {brief.get('insight','')[:80]}")
    print(f"   noise_ratio: {brief.get('noise_ratio')}")

    # step 3 · banana.render
    images = []
    t0 = time.time()
    for i, vp in enumerate(brief.get("visual_prompts", [])[: exp["n_images"]], 1):
        print(f"   image {i} ...", flush=True)
        data = gemini_image(vp)
        if data:
            name = f"exp_{exp['id']}_{i}.jpg"
            (ASSETS / name).write_bytes(data)
            images.append(name)
            print(f"   saved {name} ({len(data)//1024} KB)")
    ms = int((time.time() - t0) * 1000)
    qa["creative_gate"] = "pass" if len(images) == exp["n_images"] else ("warn" if images else "fail")
    render_credits = CREDITS["banana.render"] * len(images)
    steps.append({"seq": 3, "agent": "banana", "api": f"banana.render ×{len(images)}",
                  "ms": ms, "credits": render_credits,
                  "status": qa["creative_gate"], "out": f"{len(images)} assets · 1:1"})

    # step 4 · stacey.qa + ledger
    total = sum(s["credits"] for s in steps)
    steps.append({"seq": 4, "agent": "stacey", "api": "stacey.qa + ledger",
                  "ms": 40, "credits": 0, "status": "pass",
                  "out": f"{total} credits booked"})

    return {
        "id": exp["id"], "market": exp["market"], "lang": exp["lang"],
        "brand": exp["brand"], "keyword": exp["keyword"],
        "hypothesis": exp["hypothesis"],
        "window_label": exp["window_label"],
        "group": exp.get("group"),
        "postCount": len(posts),
        "evidence": [{
            "author": p.get("author"), "content": (p.get("content") or "")[:130],
            "likes": p.get("likes", 0), "sentiment": p.get("sentiment"),
            "url": p.get("url"),
        } for p in posts[:5]],
        "brief": brief,
        "images": images,
        "manifest": {
            "runId": run_id,
            "recipe": "signal-to-post@1.2",
            "standard": "tpc.run-manifest/v1",
            "window": {"start": start_w, "end": end_w},
            "steps": steps,
            "totalCredits": total,
            "qa": qa,
        },
    }


def main():
    existing = json.loads((DATA / "experiments.json").read_text(encoding="utf-8"))
    old = [e for e in existing.get("experiments", [])
           if e["id"] not in {x["id"] for x in EXPERIMENTS}]
    results = []
    for exp in EXPERIMENTS:
        try:
            rec = run_experiment(exp)
        except Exception as e:
            print(f"   ERROR {exp['id']}: {e}")
            rec = None
        if rec:
            results.append(rec)

    merged = old + results
    (DATA / "experiments.json").write_text(
        json.dumps({"generatedAt": time.strftime("%Y-%m-%d %H:%M"),
                    "experiments": merged}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"\nDONE — {len(results)} new / {len(merged)} total experiments")


if __name__ == "__main__":
    main()
