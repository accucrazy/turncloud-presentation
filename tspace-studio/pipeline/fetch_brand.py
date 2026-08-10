"""Capture a brand-scenario snapshot so the Studio demo has a concrete,
brand-safe case (trending news topics are not suitable for creative demos)."""
import json
import os
from datetime import date, timedelta
from pathlib import Path

import requests

KEY = os.environ.get("PANDORA_API_KEY") or exit("set PANDORA_API_KEY env var")
BASE = "https://pandora.thepocket.company/api/public"
OUT = Path(__file__).resolve().parent / "data"
OUT.mkdir(exist_ok=True)

BRANDS = ["全家", "星巴克", "健身"]


def main():
    end = date.today()
    start = end - timedelta(days=14)
    for b in BRANDS:
        r = requests.post(
            f"{BASE}/query",
            headers={"x-api-key": KEY, "Content-Type": "application/json"},
            json={
                "table": "precise",
                "searchExpression": b,
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "limit": 12,
            },
            timeout=180,
        )
        try:
            obj = r.json()
        except Exception:
            print(b, r.status_code, r.text[:200])
            continue
        posts = obj.get("posts", [])
        print(f"{b}: {r.status_code} rows={len(posts)} quota={obj.get('meta',{}).get('quota')}")
        for p in posts[:4]:
            print(f"   - @{p.get('author')} · {str(p.get('title'))[:34]} "
                  f"· like {p.get('likes')} · sent {p.get('sentiment')}")
        safe = b.encode("utf-8").hex()[:10]
        (OUT / f"brand_{safe}.json").write_text(
            json.dumps({"brand": b, **obj}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
