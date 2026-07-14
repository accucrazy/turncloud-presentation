#!/usr/bin/env python3
"""Translate the standalone English keynote deck (tpc-launch-en/index.html)
into another language, preserving all HTML structure, CSS, JS and asset paths.

Strategy: parse the HTML, find "leaf block" elements (elements that contain
visible text but have no block-level descendant), and translate the *inner
HTML* of each such block as one unit so sentences stay whole (including their
inline <span>/<strong>/<br> tags). Brand / product names are protected.

Usage:
    python translate_deck.py --lang th --name "Thai"   --out tpc-launch-th/index.html
    python translate_deck.py --lang ja --name "Japanese" --out tpc-launch-ja/index.html
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "tpc-launch-en" / "index.html"

# elements that establish a block / section: if one of these is a descendant,
# the element is NOT a leaf translation unit.
BLOCK_TAGS = {
    "html", "body", "head", "div", "section", "header", "footer", "main",
    "article", "aside", "nav", "ul", "ol", "li", "table", "thead", "tbody",
    "tfoot", "tr", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "p",
    "figure", "figcaption", "blockquote", "pre", "form", "fieldset", "hr",
    "dl", "dt", "dd", "svg",
}
SKIP_TAGS = {"script", "style", "head", "svg", "path", "defs", "lineargradient",
             "radialgradient", "stop", "filter", "meta", "link"}

DO_NOT_TRANSLATE = [
    "TurnCloud", "Accucrazy", "Pandora", "Moana", "Banana Split", "Banana",
    "Adriana", "Stacey", "Luna", "Rytho", "TSpace", "The Pocket Company",
    "Pocket Company", "NVIDIA", "OpenClaw", "MCP", "WebMCP", "A2A", "CAPI",
    "TCRM", "TCDP", "TCMS", "CRM", "CDP", "TPOS", "HOYABOX", "POS",
    "Reels Studio", "AI OS", "AIOS", "Nemotron", "Coeus", "claw3d.ai",
    "DR.WU", "Dr.Wu", "7-ELEVEN", "SQL", "EDM", "KOL", "IoT", "SaaS",
    "Meta", "Google", "TikTok", "LINE", "IG", "FB", "Threads", "ROAS", "CTR",
]

ALPHA = re.compile(r"[A-Za-z]")


def has_block_descendant(el) -> bool:
    for d in el.find_all(True):
        if d.name in BLOCK_TAGS:
            return True
    return False


def is_leaf_unit(el) -> bool:
    if el.name in SKIP_TAGS:
        return False
    if not el.get_text(strip=True):
        return False
    if not ALPHA.search(el.get_text()):
        return False
    return not has_block_descendant(el)


def collect_units(soup):
    units = []
    for el in soup.find_all(True):
        if not is_leaf_unit(el):
            continue
        # only the OUTERMOST leaf (skip if an ancestor is also a leaf unit)
        anc = el.parent
        skip = False
        while anc is not None and anc.name is not None:
            if is_leaf_unit(anc):
                skip = True
                break
            anc = anc.parent
        if not skip:
            units.append(el)
    return units


def build_client():
    load_dotenv(ROOT / "tpc-launch" / ".env")
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY not found in tpc-launch/.env")
    from google import genai
    return genai.Client(api_key=api_key)


def translate_batch(client, model, lang_name, snippets):
    protect = ", ".join(DO_NOT_TRANSLATE)
    prompt = f"""You are a professional localizer translating an enterprise AI product keynote from English into {lang_name}.

You are given a JSON array of HTML snippets. Translate ONLY the human-visible text into natural, fluent, professional {lang_name} suitable for a corporate keynote for business executives.

STRICT RULES:
- Keep every HTML tag and attribute EXACTLY as-is (e.g. <span class="c">, <strong>, <br>). Only change the text between/around tags.
- Preserve the same number of snippets and their order.
- Do NOT translate these brand / product / technical names, keep them verbatim: {protect}
- Keep numbers, %, ×, ·, arrows and acronyms unchanged.
- Keep it concise; keynote slides are short. Do not add explanations.
- Return ONLY a JSON array of strings, same length and order as the input.

INPUT:
{json.dumps(snippets, ensure_ascii=False)}
"""
    from google.genai import types
    for attempt in range(4):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    response_mime_type="application/json",
                ),
            )
            text = resp.text.strip()
            out = json.loads(text)
            if isinstance(out, list) and len(out) == len(snippets):
                return [str(x) for x in out]
            print(f"    ! length mismatch ({len(out)} vs {len(snippets)}), retry {attempt+1}")
        except Exception as e:  # noqa
            print(f"    ! error: {e} (retry {attempt+1})")
            time.sleep(2 * (attempt + 1))
    return None


def set_inner_html(el, html):
    new = BeautifulSoup(html, "html.parser")
    el.clear()
    for c in list(new.contents):
        el.append(c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True, help="html lang code, e.g. th, ja")
    ap.add_argument("--name", required=True, help="language name for the prompt")
    ap.add_argument("--out", required=True, help="output path relative to repo root")
    ap.add_argument("--model", default="gemini-2.5-pro")
    ap.add_argument("--batch", type=int, default=30)
    args = ap.parse_args()

    html = SRC.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # strip HTML comments
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()

    units = collect_units(soup)
    snippets = [u.decode_contents() for u in units]
    print(f"[{args.lang}] {len(units)} translation units")

    client = build_client()

    translated = [None] * len(snippets)
    for i in range(0, len(snippets), args.batch):
        chunk = snippets[i:i + args.batch]
        print(f"  translating {i+1}-{i+len(chunk)} / {len(snippets)} ...")
        out = translate_batch(client, args.model, args.name, chunk)
        if out is None:
            print("    !! batch failed, keeping English for this chunk")
            out = chunk
        for j, t in enumerate(out):
            translated[i + j] = t

    for u, t in zip(units, translated):
        if t is None:
            continue
        try:
            set_inner_html(u, t)
        except Exception as e:  # noqa
            print(f"    ! could not set unit: {e}")

    # set <html lang="...">
    if soup.html is not None:
        soup.html["lang"] = args.lang

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(str(soup), encoding="utf-8")
    print(f"[{args.lang}] wrote {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
