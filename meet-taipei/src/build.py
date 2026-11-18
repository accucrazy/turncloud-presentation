"""Assemble the MEET TAIPEI 2026 deck from the canonical deck's CSS/JS + deck-body.html.
Run from anywhere: python meet-taipei/src/build.py  ->  meet-taipei/index.html (GitHub Pages) + src/artifact.html (claude.ai preview). CSS/JS come from the repo root index.html (the canonical deck), so the look stays in sync."""
import re, shutil
from pathlib import Path
HERE = Path(__file__).parent; ROOT = HERE.parent.parent
REPO = HERE.parent
B = "https://accucrazy.github.io/turncloud-presentation/img/"
try:
    canon = (ROOT / "index.html").read_text(encoding="utf-8")
except FileNotFoundError:  # sparse checkout without the root deck: read it from git
    import subprocess
    canon = subprocess.run(["git", "-C", str(ROOT), "show", "HEAD:index.html"], check=True, capture_output=True).stdout.decode("utf-8")
css = re.search(r"<style>(.*?)</style>", canon, re.S).group(1) + "\n" + (HERE / "mt.css").read_text()
js = re.findall(r"<script[^>]*>(.*?)</script>", canon, re.S)[-1]
body = (HERE / "deck-body.html").read_text().replace("{B}", B)
# page numbers: renumber every <span class="pg"> sequentially so slides can be added/removed freely
_total = len(re.findall(r'<div class="slide[ "]', body)); _n = [0]
def _pg(m):
    _n[0] += 1; return f'<span class="pg">{_n[0] + 1:02d} / {_total}</span>'  # cover has no pg; numbering starts at 02
body = re.sub(r'<span class="pg">[^<]*</span>', _pg, body).replace("THE POCKET COMPANY × TURNCLOUD · 2026", "THE POCKET COMPANY × TURNCLOUD · MEET TAIPEI 2026")
pre = canon[canon.index("<body") + len("<body>"):]
pre = pre[:pre.index('<div class="slide')]  # rotate-prompt + <div class="deck">
pre = pre.replace("THE POCKET COMPANY × TURNCLOUD · 2026", "THE POCKET COMPANY × TURNCLOUD · MEET TAIPEI 2026")
tail = canon[canon.index("</template>") + len("</template>"):canon.index("</body>")]
tail = re.sub(r"<script.*?</script>", "", tail, flags=re.S)
tail = tail.replace("<strong>TPC × TURNCLOUD</strong> · KEYNOTE · 2026", "<strong>TPC × TURNCLOUD</strong> · MEET TAIPEI · 2026")
hashnav = """
/* MEET TAIPEI: deep link #s12 -> slide 12; keep the hash in sync */
(function(){
  function fromHash(){ var m = location.hash.match(/^#s(\\d+)$/); if (m && typeof go === 'function') go(Math.max(0, Math.min(slides.length - 1, parseInt(m[1], 10) - 1))); }
  window.addEventListener('hashchange', fromHash); fromHash();
  if (typeof go === 'function') { var _go = go; go = function(i){ _go(i); try { history.replaceState(null, '', '#s' + (i + 1)); } catch (e) {} }; }
})();
"""
TITLE = "MEET TAIPEI 2026 — The Pocket Company · 內容飛輪六週之後 · TurnCloud"
head = f"""<!--
  MEET TAIPEI 2026 deck — assembled by build_meet.py from deck-body.html + the canonical deck's CSS/JS.
  Canonical image assets are referenced by absolute GitHub Pages URL; new assets live in ./img/.
-->
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
"""
full = head + pre + body + "\n" + tail + "<script>\n" + js + "\n" + hashnav + "</script>\n</body>\n</html>\n"
REPO.mkdir(parents=True, exist_ok=True); (REPO / "img").mkdir(exist_ok=True)
(REPO / "index.html").write_text(full, encoding="utf-8")
# artifact preview: no doctype/html/head/body wrappers; title + style first
art = f"<title>The Pocket Company · MEET TAIPEI</title>\n<link href=\"https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap\" rel=\"stylesheet\">\n<style>\nhtml,body{{margin:0;padding:0}}\n{css}\n</style>\n" + pre + body + "\n" + tail + "<script>\n" + js + "\n" + hashnav + "</script>\n"
(HERE / "artifact.html").write_text(art, encoding="utf-8")  # preview page for claude.ai artifact (no html/head/body wrapper)
n = len(re.findall(r'<div class="slide', body))
print("slides", n, "| repo index.html", len(full), "bytes | artifact.html", len(art), "bytes | assets", sorted(p.name for p in (REPO / "img").iterdir()))
