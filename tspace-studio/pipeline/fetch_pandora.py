"""Capture real Pandora API responses as JSON snapshots for the demo.

The demo runs in hybrid mode:
  - LIVE  : same-origin BFF proxy (key stays server-side)
  - CACHED: these snapshots, so the demo never fails on stage
"""
import json
import os
from datetime import date, timedelta
from pathlib import Path

import requests

KEY = os.environ.get("PANDORA_API_KEY") or exit("set PANDORA_API_KEY env var")
BASE = "https://pandora.thepocket.company/api/public"
OUT = Path(__file__).resolve().parent / "data"
OUT.mkdir(exist_ok=True)


def call(path, body):
    r = requests.post(
        f"{BASE}/{path}",
        headers={"x-api-key": KEY, "Content-Type": "application/json"},
        json=body,
        timeout=180,
    )
    print(f"{path} {r.status_code} ({len(r.content)} bytes)")
    try:
        return r.json()
    except Exception:
        print("  raw:", r.text[:300])
        return {"success": False, "error": r.text[:300]}


def save(name, obj):
    p = OUT / f"{name}.json"
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  -> {p.name} ({p.stat().st_size // 1024} KB)")


def main():
    top = call("trends", {"type": "top", "topN": 8, "postsPerTrend": 3})
    save("trends_top", top)
    if top.get("success"):
        for t in top.get("data", [])[:8]:
            print(f"   #{t['rank']} {t['query']} — {t.get('label','')} "
                  f"(posts={t.get('postCount')}, volume={t.get('totalVolume')})")

    save("trends_runs", call("trends", {"type": "runs", "limit": 8}))

    end = date.today()
    start = end - timedelta(days=14)
    save("query_ai", call("query", {
        "table": "precise",
        "searchExpression": "AI",
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "limit": 10,
    }))


if __name__ == "__main__":
    main()
