"""Probe Pandora's multi-country / multi-language coverage.

Questions:
  1. Does /query accept a geoCountry filter?
  2. Does the corpus contain non-TW posts (en / th / ja keywords)?
"""
import json
import os
from datetime import date, timedelta
from pathlib import Path

import requests

KEY = os.environ.get("PANDORA_API_KEY") or exit("set PANDORA_API_KEY env var")
BASE = "https://pandora.thepocket.company/api/public"

end = date.today()
start = end - timedelta(days=14)
COMMON = {"table": "precise", "startDate": start.isoformat(), "endDate": end.isoformat(), "limit": 8}


def q(label, extra):
    body = {**COMMON, **extra}
    r = requests.post(f"{BASE}/query", headers={"x-api-key": KEY}, json=body, timeout=180)
    try:
        obj = r.json()
    except Exception:
        print(f"[{label}] {r.status_code} {r.text[:150]}")
        return None
    if not obj.get("success"):
        print(f"[{label}] ERR {r.status_code}: {obj.get('error')}")
        return obj
    posts = obj.get("posts", [])
    geos = {}
    langs = {}
    for p in posts:
        geos[p.get("geoCountry")] = geos.get(p.get("geoCountry"), 0) + 1
        langs[p.get("detectedLanguage")] = langs.get(p.get("detectedLanguage"), 0) + 1
    print(f"[{label}] rows={len(posts)} geo={geos} lang={langs} quota_used={obj['meta']['quota']['used']}")
    for p in posts[:2]:
        print(f"    @{p.get('author')} [{p.get('geoCountry')}/{p.get('detectedLanguage')}] {str(p.get('content'))[:60]}")
    return obj


print("== 1. english keyword ==")
q("Starbucks(en)", {"searchExpression": "Starbucks"})
print("== 2. thai keyword ==")
q("Paragon(th)", {"searchExpression": "พารากอน"})
print("== 3. japanese keyword ==")
q("Sutaba(ja)", {"searchExpression": "スタバ"})
print("== 4. geoCountry param? ==")
q("geo=th", {"searchExpression": "coffee", "geoCountry": "th"})
q("geo=us", {"searchExpression": "coffee", "geoCountry": "us"})
print("== 5. plain english ==")
q("Nike(en)", {"searchExpression": "Nike"})
