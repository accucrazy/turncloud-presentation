"""Build contact-sheet montages of the AI-talk slides so they can be reviewed at a glance."""
import os, math
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
TALK_DIR = os.path.join(ROOT, "img", "talk")

# order = the TALK array used by index.html
ORDER = ["t02","bio","t03","t05","t07","t08","t10","t12","t13","t14","t15","t16","t17","t18","t19","t20",
         "t23","t24","t25","t26","t27","t28","t32","t33","t34","cot-training","t35","t36","t37",
         "ad-case","ad-results","ad-results2","t39","t45","t46","t47","t48","t49","t50",
         "t55","t56","t57","t58","t65","t66","t67","t68","t69","t71","t72","t73","t74",
         "market-tam","funnel","t75","t76"]

COLS = 3
THUMB_W = 600
LABEL_H = 34
PAD = 10
PER_SHEET = 15  # 5 rows

try:
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 22)
except Exception:
    font = ImageFont.load_default()

def make_sheet(items, idx):
    rows = math.ceil(len(items) / COLS)
    thumb_h = int(THUMB_W * 9 / 16)
    cell_w = THUMB_W + PAD
    cell_h = thumb_h + LABEL_H + PAD
    W = COLS * cell_w + PAD
    H = rows * cell_h + PAD
    sheet = Image.new("RGB", (W, H), (15, 18, 28))
    d = ImageDraw.Draw(sheet)
    for i, name in enumerate(items):
        r, c = divmod(i, COLS)
        x = PAD + c * cell_w
        y = PAD + r * cell_h
        gi = idx * PER_SHEET + i + 1  # global slide # in talk section (1-based)
        d.rectangle([x, y, x + THUMB_W, y + LABEL_H], fill=(30, 38, 56))
        d.text((x + 8, y + 6), f"#{gi:>2}  {name}", font=font, fill=(120, 230, 210))
        p = os.path.join(TALK_DIR, name + ".png")
        try:
            im = Image.open(p).convert("RGB")
            im.thumbnail((THUMB_W, thumb_h))
            ox = x + (THUMB_W - im.width) // 2
            oy = y + LABEL_H + (thumb_h - im.height) // 2
            sheet.paste(im, (ox, oy))
        except Exception as e:
            d.text((x + 8, y + LABEL_H + 8), f"MISSING {e}", font=font, fill=(255, 120, 120))
    out = os.path.join(ROOT, f"_montage_{idx+1}.png")
    sheet.save(out, quality=85)
    print("saved", out, sheet.size)

chunks = [ORDER[i:i+PER_SHEET] for i in range(0, len(ORDER), PER_SHEET)]
for i, ch in enumerate(chunks):
    make_sheet(ch, i)
print("total slides:", len(ORDER), "sheets:", len(chunks))
