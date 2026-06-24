"""
Generate: The Pocket Company chapter-divider BACKGROUND image (sits behind title text).
Outputs: img/pocket_chapter_bg.(png|jpg)

Uses the documented Banana pipeline (Gemini nano-banana-pro-preview).
API key resolution order: env GEMINI_API_KEY / GOOGLE_API_KEY → local _tpcai_ref config fallback
(so the key never has to be typed into a shell command or committed to a new file).
"""
import base64, json, mimetypes, os, re, sys, time
from pathlib import Path
import requests

ROOT = Path(__file__).parent
PORTRAITS = Path(r"d:/DEV/Turncloud Launch/turncloud-presentation/img")

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    for p in [
        Path(r"d:/DEV/Turncloud Launch/_tpcai_ref/tools/google-search/config.ts"),
        Path(r"d:/DEV/Turncloud Launch/_tpcai_ref/config.ts"),
    ]:
        if p.exists():
            m = re.search(r"AIzaSy[A-Za-z0-9_\-]{20,}", p.read_text(encoding="utf-8", errors="ignore"))
            if m:
                API_KEY = m.group(0)
                break
if not API_KEY:
    raise SystemExit("No Gemini API key found (env or _tpcai_ref).")

MODEL = "nano-banana-pro-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

OUT_DIR = ROOT / "img"
OUT_DIR.mkdir(exist_ok=True)

REFS = {
    "pandora": PORTRAITS / "08_pandora.jpg",
    "moana":   PORTRAITS / "09_moana.jpg",
    "banana":  PORTRAITS / "10_banana.jpg",
    "adriana": PORTRAITS / "11_adriana.jpg",
    "stacey":  PORTRAITS / "12_stacey.jpg",
    "workforce": PORTRAITS / "07_workforce.jpg",
}


def load_ref(name, label):
    path = REFS[name]
    if not path.exists():
        print(f"  missing ref {path.name}, skipping")
        return []
    mime, _ = mimetypes.guess_type(str(path))
    if path.suffix.lower() == ".png":
        mime = "image/png"
    return [
        {"text": f"Reference — {label}: keep character identity / face / outfit / palette consistent."},
        {"inline_data": {"mime_type": mime or "image/jpeg",
                         "data": base64.b64encode(path.read_bytes()).decode()}},
    ]


STYLE = (
    "STYLE: Premium cinematic Pixar-style 3D illustration used as a SLIDE BACKGROUND. "
    "Deep dark-navy stage (#0a1633 / #070d1c), with subtle cyan (#22d3ee) and violet (#a855f7) "
    "rim lighting and soft volumetric glow. Gentle depth-of-field bokeh. Soft subsurface "
    "scattering on characters, big expressive eyes. Mood: confident, premium, calm keynote "
    "chapter title — NOT busy, NOT cyberpunk neon overload. Intentionally LOW overall brightness "
    "so white title text overlays cleanly. NO text, NO letters, NO numbers, NO logos, NO watermarks."
)

PROMPT = """
Design ONE 16:9 cinematic BACKGROUND image for a keynote CHAPTER-DIVIDER slide
(the slide title 'The Pocket Company' will be overlaid in white text by the deck,
so DO NOT render any text yourself).

COMPOSITION:
- The RIGHT ~55% of the frame: a small confident TEAM of five Pixar-style 3D
  AI-agent characters standing together in a sleek, dark, modern AI operations
  studio, with soft glowing holographic dashboards / data ribbons floating gently
  behind and around them. Render each FAITHFUL to the provided references:
    • Pandora — silver-haired woman in grey suit
    • Moana   — woman with a curly afro, orange tee (pink megaphone optional)
    • Banana  — friendly tall yellow banana mascot with round glasses and bow tie
    • Adriana — brunette woman with round glasses, sage-green blazer, glowing tablet
    • Stacey  — woman with sleek dark high-ponytail, dark-navy blazer
  Arrange them as a relaxed hero group, softly lit, slightly turned toward camera.
- The LEFT ~45% of the frame: deep, almost-solid dark navy emptiness (a smooth
  gradient fading to near-black #070d1c at the far left edge), with only faint
  floating light motes / soft bokeh. This negative space is RESERVED for title text.
- A soft horizontal floor reflection and gentle vignette keep focus centered.

MOOD: premium, dark, cinematic, optimistic. Low brightness overall. The five
characters should read as a single elegant team silhouette, not a busy crowd.

ABSOLUTELY NO text, letters, numbers, logos, UI labels, or watermarks anywhere.
"""


def call_api(prompt, refs, attempt=1, max_attempts=3):
    parts = []
    for rp in refs:
        parts.extend(rp)
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
    out_name = sys.argv[1] if len(sys.argv) > 1 else "pocket_chapter_bg"
    refs = [
        load_ref("workforce", "team composition / overall vibe"),
        load_ref("pandora", "Pandora"),
        load_ref("moana", "Moana"),
        load_ref("banana", "Banana"),
        load_ref("adriana", "Adriana"),
        load_ref("stacey", "Stacey"),
    ]
    refs = [r for r in refs if r]
    print(f"generating {out_name} ... ({len(refs)} refs)", flush=True)
    t0 = time.time()
    data = call_api(PROMPT, refs)
    if data is None:
        print("FAILED")
        return 1
    ext = "png" if data[:8] == b"\x89PNG\r\n\x1a\n" else "jpg"
    out = OUT_DIR / f"{out_name}.{ext}"
    out.write_bytes(data)
    print(f"saved {out.name} ({len(data)//1024} KB, {time.time()-t0:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
