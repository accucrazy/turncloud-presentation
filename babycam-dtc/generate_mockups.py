"""
Generate all hero mockups for the Guardian Halo DTC deck.

Usage:
    python generate_mockups.py              # generate ALL 5 mockups
    python generate_mockups.py brand_hero   # generate only one
    python generate_mockups.py website
    python generate_mockups.py shopify
    python generate_mockups.py app
    python generate_mockups.py brand_identity

Outputs to assets/<name>.jpg
"""
import base64
import io
import json
import mimetypes
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise SystemExit("Set GEMINI_API_KEY in .env")

MODEL = "nano-banana-pro-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

OUT_DIR = ROOT / "assets"
OUT_DIR.mkdir(exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
#  SHARED STYLE
# ═══════════════════════════════════════════════════════════════════

STYLE = (
    "STYLE: Premium DTC e-commerce / Apple-keynote-grade product "
    "mockup. Photorealistic where required (product, device screens, "
    "lifestyle shots), clean flat-vector where required (logo, "
    "packaging, brand identity sheets). Warm, optimistic, parent-safe "
    "mood — NOT cyberpunk, NOT cluttered. "
    "Think: Apple product page × Allbirds DTC × Owlet baby monitor × "
    "Tesla aesthetic. "
    "PALETTE: warm off-white #faf7f2 main background; soft mint-cream "
    "#eef7f1; sage green #84a98c (primary brand accent for Guardian "
    "Halo); deep slate #0f172a for headings; warm peach #fbbf80 for "
    "playful accents; soft sky blue #cfe8f5 for trust/tech moments. "
    "Avoid neon, avoid generic stock-photo cliches. "
    "TYPOGRAPHY: confident sans-serif (Inter / SF Pro / Manrope). "
    "All text must be ENGLISH and CORRECTLY SPELLED. "
    "Product name is 'Guardian Halo' — render it EXACTLY. "
    "NO watermarks, NO photographer credits, NO clip-art icon packs."
)


# ═══════════════════════════════════════════════════════════════════
#  MOCKUP CATALOG
# ═══════════════════════════════════════════════════════════════════

MOCKUPS = {
    # ─────────────────────────────────────────────────────────────
    "brand_hero": dict(
        name="Brand Lifestyle Hero",
        aspect="16:9",
        prompt="""
A single photorealistic 16:9 lifestyle hero image for a DTC baby-camera
brand called "Guardian Halo".

SCENE:
Interior of a modern Toyota RAV4 (2024+), seen from a 3/4 rear-angle
inside the cabin. Late-afternoon golden-hour light spills through the
side windows.

FOREGROUND (right): A baby (~9 months) in a rear-facing car seat,
peacefully looking up. The baby's expression is calm/curious — NOT
crying. The car seat is a modern grey/charcoal model.

CEILING (above the baby, where the rear reading-light would be): A
small, beautifully designed circular device — the "Guardian Halo" —
mounted flush into the roof panel. It has a soft warm halo of light
ringing its perimeter (suggesting an active LED ring). At its centre,
a small camera lens. The device looks premium, like an Apple HomePod
mini or Owlet sock — soft white shell, brushed-aluminium rim.

MIDGROUND (left, front seat): A mother (modern, 30s, slightly out of
focus) sits in the passenger seat looking at her iPhone, which clearly
displays a clean app interface showing a live camera feed of the
baby. The screen shows a small status badge "Calm · Sleeping in 2 min"
in soft sage-green type.

OVERALL FEELING: warmth, safety, peace of mind, "I can finally relax
while driving". Soft depth of field. No harsh shadows.

TEXT ON IMAGE: none, except the phone-screen UI elements
which can show "Guardian Halo" wordmark very subtly and the status
line "Calm · Sleeping in 2 min".

NO logos of Toyota or any other real brand visible.
NO stock-photo "happy family" cliches.
""",
    ),

    # ─────────────────────────────────────────────────────────────
    "website": dict(
        name="Website Landing Page Mockup",
        aspect="16:9",
        prompt="""
A single 16:9 product-page mockup hero image for the DTC website
"guardianhalo.com".

LAYOUT: a stunning, premium 16-inch MacBook Pro floating in 3/4 view
on a warm off-white #faf7f2 background. Soft shadow beneath.
The MacBook screen displays the landing page of guardianhalo.com in
high fidelity.

THE LANDING PAGE ON THE SCREEN:
   TOP NAV (left): a small sage-green wordmark "Guardian Halo"
                   followed by a tiny halo glyph (◯).
                   Nav links (right): "How it works", "RAV4 fit",
                   "Reviews", "Shop". Far right, a "Cart (0)" pill.

   HERO SECTION:
     Big slate-#0f172a headline:
        "See your baby. Drive in peace."
     Sub-headline (slate-600, medium):
        "Guardian Halo — the AI baby camera built into your
         car's reading light. No cabling. No drilling. Just calm."
     Two CTAs side by side:
        [ Shop Guardian Halo — $349 ]  (filled sage-green button)
        [ Watch the 60-sec demo  → ]   (text link with arrow)
     A small trust line under the CTAs:
        ★★★★★ "4.9 from 1,247 RAV4 parents" · NHTSA-aligned
                                                presence detection

   HERO IMAGE (right half of the hero): a beautifully composed photo
   of the Guardian Halo device installed in the car ceiling, soft
   light glowing around it.

   BELOW THE HERO (visible only the top edge, suggesting more
   content): a row of 3 small icons with mini-captions:
     [icon] AI Presence Detection
     [icon] 3-Way Live View
     [icon] Memorable Moments

NEXT TO THE MACBOOK (foreground right, slightly lower): an iPhone 16
Pro held at a soft angle, showing the Guardian Halo companion app
with a live baby-cam feed. The phone screen shows:
   – top bar: "Guardian Halo"
   – live camera tile (sleeping baby)
   – status pills: "Calm" "Cabin 72°F" "Wi-Fi 5G"
   – bottom tab bar: "Live · History · Moments · Settings"

OVERALL MOOD: clean, premium, calm, trustworthy. Reminds the viewer
of Apple's product pages or Allbirds' homepage. Soft shadows. No
clutter.

TEXT MUST RENDER ACCURATELY:
   "Guardian Halo"  "See your baby. Drive in peace."
   "guardianhalo.com" (in the browser URL bar, faintly)
   "Shop Guardian Halo — $349"  "Watch the 60-sec demo"
   "4.9 from 1,247 RAV4 parents"
""",
    ),

    # ─────────────────────────────────────────────────────────────
    "shopify": dict(
        name="Shopify Product Detail Page Mockup",
        aspect="16:9",
        prompt="""
A single 16:9 e-commerce product page mockup for Guardian Halo, shown
inside a desktop browser window.

FRAME: A clean browser window chrome (Chrome-style address bar at top
showing "guardianhalo.com/products/guardian-halo-for-rav4"). The
window floats on a warm off-white #faf7f2 background with a very
gentle drop-shadow.

INSIDE THE BROWSER:

   TOP NAV: small sage-green "Guardian Halo" wordmark left.
             Right: links "How it works", "RAV4 fit", "Reviews",
             "Shop", and "Cart (1)" pill.

   PAGE BODY · 2-COLUMN LAYOUT:

   LEFT (gallery, ~55%):
      Large primary product photo of Guardian Halo device on a clean
      sage-cream backdrop, the device shown in 3/4 angle with its halo
      LED softly glowing.
      Beneath the primary, a row of 4 small thumbnails:
        thumb 1: device front
        thumb 2: device in-ceiling (installed view)
        thumb 3: companion app screen
        thumb 4: packaging shot

   RIGHT (info, ~45%):
      Breadcrumb (slate-500): "Home / RAV4 / Guardian Halo"
      Product title (slate-900, bold, large):
         "Guardian Halo — AI Baby Camera"
      Sub-title (slate-600):
         "For Toyota RAV4 (2019–2026+). Installs in 5 minutes,
          no cabling required."

      Price block:
         "$299"  (large, sage-green, bold)
         strikethrough "$349"  (slate-400)
         pill "Launch price · save $50"  (peach background)

      Star rating row: "★★★★★ 4.9 (1,247 reviews)"

      Variant selector:
         "Choose your RAV4 generation:"
         [ 5th Gen 2019–2025 ] (selected, sage outline)
         [ 6th Gen 2026+      ] (un-selected, slate outline)

      Quantity stepper:  - 1 +

      Primary CTA:
         [ Add to Cart — $299 ]   (full-width sage-green button)
      Secondary CTA below:
         [ Buy now with Shop Pay ]  (purple Shop Pay button)

      Trust strip (3 small icons + labels):
         ✓ Free US shipping
         ✓ 30-day returns
         ✓ 2-year warranty

      "What's in the box" mini-list:
         · Guardian Halo device
         · OEM-compatible wire harness for RAV4
         · Quick-install guide
         · Companion app (iOS + Android)

   BOTTOM EDGE just visible: a "Customer Reviews" section header
   and the start of a 5-star review tile.

OVERALL: Apple-grade product page polish. Lots of breathing room.
Sage green is the primary accent, peach is the secondary highlight.
NO clutter. NO neon. NO generic stock photos.

TEXT MUST RENDER ACCURATELY:
   "Guardian Halo — AI Baby Camera"
   "For Toyota RAV4 (2019–2026+)"
   "$299"  "$349"  "Launch price · save $50"
   "4.9 (1,247 reviews)"
   "Add to Cart — $299"  "Buy now with Shop Pay"
   "Free US shipping"  "30-day returns"  "2-year warranty"
""",
    ),

    # ─────────────────────────────────────────────────────────────
    "app": dict(
        name="Companion App + Social Ad Mockup",
        aspect="16:9",
        prompt="""
A single 16:9 split mockup image: LEFT half shows the Guardian Halo
companion smartphone app; RIGHT half shows a beautiful Instagram
sponsored-post ad for the same product. Both on a warm off-white
#faf7f2 background.

═══ LEFT HALF (50%) — APP MOCKUP ═══

A photorealistic iPhone 16 Pro held at a slight 3/4 angle, screen
facing the viewer. The screen shows the Guardian Halo app:

STATUS BAR: 9:41, full bars, full battery (standard iOS).

APP TOP: large sage-green wordmark "Guardian Halo"
          right side: a small profile avatar circle

LIVE FEED TILE (taking ~50% of screen height):
   A photorealistic still of a baby (~9mo) sleeping in a car seat,
   shot from the ceiling-camera angle (top-down 3/4). A small "● LIVE"
   indicator top-left. Bottom-left timecode: "Today · 3:42 PM".

STATUS BADGES (row of pills below the live feed):
   "Calm 😌"  (sage background)
   "Sleeping · 18 min"  (cream background)
   "Cabin 72°F"  (sky-blue background)
   "Wi-Fi 5G"   (slate background)

AI INSIGHTS CARD:
   Header: "AI Insights"
   Body: "Your baby has been sleeping 18 min — typical naps last
          25–35 min."
   Small CTA pill: "Tap for nap history"

BOTTOM TAB BAR (4 tabs with icons):
   ● Live   ○ History   ○ Moments   ○ Settings

═══ RIGHT HALF (50%) — INSTAGRAM SPONSORED AD ═══

A photorealistic iPhone 16 Pro held in portrait, showing an Instagram
feed sponsored post.

POST HEADER:
   Tiny circular avatar with halo glyph, username "guardianhalo"
   small "Sponsored" label.
   Three-dot menu icon top-right.

POST IMAGE (square, takes most of phone screen):
   A beautiful lifestyle photo: a young dad in the driver seat of a
   Toyota RAV4, holding his phone showing the baby-cam feed, with a
   peaceful smile. Soft daylight. Caption overlay in bottom-right
   corner of the image (large, white, sans-serif):
      "Eyes on the road.
       Heart on your baby."
   Below that, smaller text:
      "Guardian Halo — installs in 5 minutes. Built for RAV4 parents."

POST FOOTER:
   Row of action icons (heart, comment, share, bookmark).
   Like count: "♥ 8,247 likes"
   Caption snippet under: "guardianhalo The AI baby cam built into
   your RAV4's reading light. No cabling. Just calm. Shop with code
   PEACEFUL10 — link in bio."
   "View all 312 comments..."

CTA STRIP across the bottom of the post (Instagram's standard
sponsored CTA):  "Shop Now  ›"  (sage-green Instagram CTA button)

═══ COMPOSITION ═══

Both phones are in front of the off-white background, slightly tilted
toward the viewer. A subtle vertical divider line between the halves,
labelled top-centre:
   left side:  "1 · Product · App"
   right side: "2 · Marketing · Social Ad"

Both labels small mono uppercase slate-600.

OVERALL FEELING: Polished, premium, like a slide from an Apple or
Allbirds brand deck. NO clutter.

TEXT MUST RENDER ACCURATELY:
   "Guardian Halo"  "AI Insights"  "Live · History · Moments · Settings"
   "Calm 😌"  "Sleeping · 18 min"  "Cabin 72°F"  "Wi-Fi 5G"
   "Eyes on the road. Heart on your baby."
   "Guardian Halo — installs in 5 minutes. Built for RAV4 parents."
   "guardianhalo"  "Sponsored"  "Shop Now  ›"
   "PEACEFUL10"
""",
    ),

    # ─────────────────────────────────────────────────────────────
    "brand_identity": dict(
        name="Brand Identity Sheet",
        aspect="16:9",
        prompt="""
A single 16:9 brand identity sheet for "Guardian Halo", styled like
a designer's brand-system board. Flat / clean / editorial layout on
a warm off-white #faf7f2 background.

TITLE STRIP at the top:
   Small mono label (slate-500, uppercase): "BRAND IDENTITY · 2026"
   Big slate-900 bold headline:
      "Guardian Halo — Brand System"
   Sub-line (slate-600):
      "Calm tech for parents on the move."

MAIN GRID — 4 quadrants below the title strip:

═══ QUADRANT 1 (top-left) · LOGO ═══
On a soft mint-cream #eef7f1 panel:
   Centred, a custom wordmark "Guardian Halo" in a confident
   geometric sans-serif (think Inter ExtraBold). To the LEFT of
   the wordmark, a circular halo icon: a soft sage-green ring
   with a small dot at its centre (representing the camera).
   Below the wordmark, smaller mono caption: "Primary lockup".
   Below that, two stacked variants:
     · Wordmark only (horizontal)
     · Halo icon only (the ring symbol)

═══ QUADRANT 2 (top-right) · COLOR PALETTE ═══
A 2 × 3 grid of color swatches, each a rounded-rect:
   1. "Halo Sage"    #84a98c  (primary brand)
   2. "Peace Cream"  #faf7f2  (background)
   3. "Cabin Slate"  #0f172a  (heading)
   4. "Mint Wash"    #eef7f1  (panel)
   5. "Dawn Peach"   #fbbf80  (accent)
   6. "Sky Calm"     #cfe8f5  (highlight)

═══ QUADRANT 3 (bottom-left) · TYPOGRAPHY ═══
A typography specimen panel:
   "Aa" — big serif-like display (representing Inter Black 96pt)
   Sub-label: "Inter — Headings"
   Below, a smaller "Aa Bb Cc" specimen for body
   Sub-label: "Inter — Body 16/24"
   Smallest: "Aa Bb 123" mono
   Sub-label: "JetBrains Mono — Labels"

═══ QUADRANT 4 (bottom-right) · TONE OF VOICE ═══
A clean text panel:
   Header: "How we speak"
   3 short pillars:
     1. CALM, NOT ALARMING
        "Your baby is sleeping peacefully." — NOT
        "Emergency! Check now!"
     2. PARENT-TO-PARENT
        We write like a friend who's been there.
        No jargon, no scary stats.
     3. SAFETY AS PEACE
        Safety isn't fear — it's the freedom to enjoy
        the drive.

PACKAGING TEASER (small strip across the very bottom of the sheet,
spanning width):
   A small photorealistic render of the product packaging box —
   sage-green box with white "Guardian Halo" wordmark + halo icon,
   sat next to a small inner-tray showing the device.
   Mono caption beneath: "Unboxing · designed to delight"

OVERALL: Like a single page out of a design-system PDF (think
Stripe's brand book, or Linear's brand assets page). Very clean, lots
of white space, careful alignment.

TEXT MUST RENDER ACCURATELY:
   "BRAND IDENTITY · 2026"
   "Guardian Halo — Brand System"
   "Calm tech for parents on the move."
   "Primary lockup"  "Wordmark only"  "Halo icon only"
   "Halo Sage" "Peace Cream" "Cabin Slate" "Mint Wash"
        "Dawn Peach" "Sky Calm"
   "#84a98c" "#faf7f2" "#0f172a" "#eef7f1" "#fbbf80" "#cfe8f5"
   "Inter — Headings"  "Inter — Body 16/24"  "JetBrains Mono — Labels"
   "How we speak"  "CALM, NOT ALARMING"  "PARENT-TO-PARENT"
        "SAFETY AS PEACE"
   "Unboxing · designed to delight"
""",
    ),

    # ─────────────────────────────────────────────────────────────
    "packaging": dict(
        name="Packaging & Unboxing Suite",
        aspect="16:9",
        prompt="""
A single 16:9 premium flat-lay / hero render of the full "Guardian
Halo" PHYSICAL BRAND SUITE — the kind of unboxing photo a top DTC
brand pins to its press kit. Shot slightly top-down on a warm
off-white #faf7f2 surface with soft natural shadows.

ARRANGE these branded items in a tasteful, editorial composition:

1. THE MAIN BOX (hero, centre-left): a square sage-green #84a98c rigid
   gift box, matte finish, with a clean white embossed "Guardian Halo"
   wordmark + halo ring icon (◯ with a centre dot) on the lid. Premium,
   like an Apple or Aesop box.

2. THE OPEN BOX / INNER TRAY (centre): lid lifted, revealing the
   Guardian Halo device nestled in a soft moulded cream tray, with a
   small fabric pull-ribbon. The device shows its sage rim + camera lens.

3. WELCOME CARD (foreground): a thick cream card, top edge visible,
   printed in slate: "Welcome, parent." and below in smaller type:
   "Eyes on the road. Heart on your baby."

4. QUICK-INSTALL CARD: a folded card showing 3 tiny step icons:
   "1 · Unplug   2 · Click in   3 · App on" with "5-minute install"
   in sage.

5. STICKER SHEET: a small sheet of die-cut stickers — halo rings,
   a tiny car, a moon, "Guardian Halo" wordmark — in sage / peach.

6. WIRE HARNESS: a neatly coiled OEM-style wire harness adapter with
   a small "for RAV4" tag.

7. A COTTON DRAWSTRING POUCH in sage with a small white halo icon.

8. A WARRANTY CARD: small, reading "2-Year Warranty" + "30-Day Returns".

OVERALL FEELING: tactile, premium, calm, parent-safe. Like the
unboxing hero of Owlet × Aesop × Apple. Lots of breathing room.
Soft shadows. Consistent sage-green + cream + peach palette.

TEXT MUST RENDER ACCURATELY (English):
   "Guardian Halo"  "Welcome, parent."
   "Eyes on the road. Heart on your baby."
   "5-minute install"  "1 · Unplug"  "2 · Click in"  "3 · App on"
   "for RAV4"  "2-Year Warranty"  "30-Day Returns"
NO real-brand logos. NO clutter.
""",
    ),

    # ─────────────────────────────────────────────────────────────
    "email": dict(
        name="Email + SMS Lifecycle Mockup",
        aspect="16:9",
        prompt="""
A single 16:9 mockup showing the Guardian Halo CRM / lifecycle
messaging suite — the automated email + SMS flow a parent receives.
Clean editorial layout on a warm off-white #faf7f2 background.

Show THREE branded email cards floating at slight angles (like a
designer's email-system board) PLUS one phone showing an SMS.

═══ EMAIL CARD 1 — WELCOME (largest, left) ═══
A rendered email in a soft white rounded card:
   Header strip: sage-green band with white "Guardian Halo" wordmark
                 + halo icon.
   Hero line (slate, bold): "Welcome to calmer drives."
   Sub: "Eyes on the road. Heart on your baby."
   A warm photo block: baby sleeping peacefully in a car seat.
   Body snippet: "Your Guardian Halo ships in 2 days. Here's how the
                  5-minute install works."
   Sage CTA button: "Watch the install video"

═══ EMAIL CARD 2 — REVIEW REQUEST (centre, behind) ═══
   Header: "How are the drives going?"
   5 sage stars row.
   Body: "Leave a review, help another RAV4 parent."
   Sage CTA: "Share your experience"

═══ EMAIL CARD 3 — REFERRAL (right) ═══
   Header (peach accent): "Give $30, get $30."
   Body: "Know another parent who'd love calmer drives?"
   A dashed code box: "PEACEFUL30"
   Sage CTA: "Refer a parent"

═══ PHONE (foreground right) — SMS ═══
An iPhone showing an iMessage-style SMS thread from "Guardian Halo":
   Bubble 1: "Hi Sarah! Your Halo just shipped 📦 Track: ghalo.co/t/8842"
   Bubble 2: "Installed? Reply HELP for a 60-sec video walkthrough."
   A small "Klaviyo · automated" tag at the bottom (tiny, slate-400).

LABEL STRIP across the top (small mono uppercase slate-500):
   "LIFECYCLE · WELCOME → INSTALL → REVIEW → REFER"

OVERALL: polished CRM system board, sage + cream + peach, consistent
with the Guardian Halo brand. Clean, lots of white space.

TEXT MUST RENDER ACCURATELY (English):
   "Guardian Halo"  "Welcome to calmer drives."
   "Eyes on the road. Heart on your baby."
   "Watch the install video"
   "How are the drives going?"  "Share your experience"
   "Give $30, get $30."  "PEACEFUL30"  "Refer a parent"
   "LIFECYCLE · WELCOME → INSTALL → REVIEW → REFER"
""",
    ),
}


def call_api(prompt, aspect, attempt=1, max_attempts=3):
    parts = [{"text": prompt}, {"text": STYLE}]
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect},
        },
    }
    try:
        r = requests.post(URL, json=payload, timeout=300)
    except requests.RequestException as e:
        print(f"  request error: {e}")
        if attempt < max_attempts:
            time.sleep(5 * attempt)
            return call_api(prompt, aspect, attempt + 1, max_attempts)
        return None
    if r.status_code != 200:
        print(f"  http {r.status_code}: {r.text[:600]}")
        if r.status_code in (429, 500, 502, 503, 504) and attempt < max_attempts:
            time.sleep(10 * attempt)
            return call_api(prompt, aspect, attempt + 1, max_attempts)
        return None
    data = r.json()
    for c in data.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            inline = p.get("inlineData") or p.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])
    print("  no image in response; preview:", json.dumps(data, ensure_ascii=False)[:500])
    return None


def generate_one(key):
    if key not in MOCKUPS:
        print(f"✗ unknown mockup '{key}'. Available: {', '.join(MOCKUPS.keys())}")
        return False
    m = MOCKUPS[key]
    print(f"\n[*] {key} -- {m['name']}")
    t0 = time.time()
    data = call_api(m["prompt"], m["aspect"])
    if data is None:
        print(f"  [x] FAILED")
        return False
    ext = "png" if data[:8] == b"\x89PNG\r\n\x1a\n" else "jpg"
    out = OUT_DIR / f"{key}.{ext}"
    out.write_bytes(data)
    print(f"  [ok] saved {out.relative_to(ROOT)} ({len(data) // 1024} KB / {time.time() - t0:.1f}s)")
    return True


def main():
    args = sys.argv[1:]
    force = "--force" in args
    args = [a for a in args if a != "--force"]
    if args:
        keys = args
    else:
        keys = list(MOCKUPS.keys())

    print(f"Generating {len(keys)} mockup(s): {', '.join(keys)}  (force={force})")
    ok = 0
    skipped = 0
    for k in keys:
        if not force:
            existing = list(OUT_DIR.glob(f"{k}.*"))
            if existing:
                print(f"\n[skip] {k} -- already exists: {existing[0].name}")
                skipped += 1
                continue
        if generate_one(k):
            ok += 1
    total_done = ok + skipped
    print(f"\n[*] DONE -- {ok} generated, {skipped} skipped, {len(keys) - total_done} failed")
    return 0 if total_done == len(keys) else 1


if __name__ == "__main__":
    sys.exit(main())
