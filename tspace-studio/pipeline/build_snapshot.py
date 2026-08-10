"""Trim the captured Pandora responses into data/snapshot.js.

Written as a JS assignment (not JSON) so the demo also runs from file://
without a web server — useful for ad-hoc testing before deploy.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def clip(s, n):
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def main():
    top = json.loads((DATA / "trends_top.json").read_text(encoding="utf-8"))
    runs = json.loads((DATA / "trends_runs.json").read_text(encoding="utf-8"))

    trends = []
    for t in top.get("data", []):
        trends.append({
            "rank": t["rank"],
            "query": t["query"],
            "label": t.get("label", ""),
            "postCount": t.get("postCount", 0),
            "totalVolume": t.get("totalVolume", 0),
            "posts": [{
                "author": p.get("author"),
                "url": p.get("url"),
                "source": p.get("source"),
                "excerpt": clip(p.get("excerpt") or p.get("content"), 110),
                "likes": p.get("likes", 0),
                "comments": p.get("comments", 0),
                "shares": p.get("shares", 0),
                "volume": p.get("volume", 0),
                "createdAt": p.get("pageCreatedAt"),
            } for p in t.get("posts", [])[:3]],
        })

    brands = []
    for f in sorted(DATA.glob("brand_*.json")):
        obj = json.loads(f.read_text(encoding="utf-8"))
        posts = [{
            "author": p.get("author"),
            "url": p.get("url"),
            "excerpt": clip(p.get("content") or p.get("title"), 130),
            "likes": p.get("likes", 0),
            "comments": p.get("comments", 0),
            "volume": p.get("volume", 0),
            "sentiment": p.get("sentiment", 0),
            "keyword": p.get("keyword"),
            "lang": p.get("detectedLanguage"),
            "createdAt": p.get("pageCreatedAt"),
        } for p in obj.get("posts", [])]
        brands.append({"brand": obj.get("brand"), "posts": posts})

    snapshot = {
        "capturedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "quota": top.get("meta", {}).get("quota", {}),
        "window": top.get("meta", {}).get("window", {}),
        "trends": trends,
        "runs": [{
            "runId": r.get("runId"),
            "status": r.get("status"),
            "startedAt": r.get("startedAt"),
            "finishedAt": r.get("finishedAt"),
            "entries": r.get("processedEntries"),
            "posts": r.get("totalPosts"),
        } for r in runs.get("data", [])],
        "brands": brands,
    }

    out = DATA / "snapshot.js"
    out.write_text(
        "// Captured from https://pandora.thepocket.company/api/public — real data.\n"
        "window.PANDORA_SNAPSHOT = "
        + json.dumps(snapshot, ensure_ascii=False, indent=1)
        + ";\n",
        encoding="utf-8",
    )
    print(f"snapshot.js — {out.stat().st_size//1024} KB · "
          f"{len(trends)} trends · {len(brands)} brands · {len(snapshot['runs'])} runs")


if __name__ == "__main__":
    main()
