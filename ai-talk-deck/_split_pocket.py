import os, re, json, shutil

SRC = r"d:\DEV\Turncloud Launch\turncloud-presentation\index.html"
OUT = r"d:\DEV\Turncloud Launch\ai-talk-deck\pocket"
os.makedirs(OUT, exist_ok=True)

html = open(SRC, encoding="utf-8").read()

# 1) grab the <head> (fonts + inline CSS)
head = html[html.index("<head>"): html.index("</head>") + len("</head>")]

# 2) find each top-level slide div: <div class="slide ..."> ... </div>  (balanced)
slide_open = re.compile(r'<div class="slide[ "]')
DIV = re.compile(r'</?div\b', re.I)

slides = []
for m in slide_open.finditer(html):
    start = m.start()
    depth = 0
    i = start
    end = None
    for d in DIV.finditer(html, start):
        if d.group().lower().startswith("</"):
            depth -= 1
        else:
            depth += 1
        if depth == 0:
            end = d.end() + html[d.end():].index(">") + 1
            break
    if end:
        block = html[start:end]
        ds = re.search(r'data-slide="([^"]+)"', block)
        slides.append((ds.group(1) if ds else f"s{len(slides)}", block))

print("Found slides:", len(slides))

PAGE = """<!DOCTYPE html>
<html lang="zh-Hant">
{head}
<body>
<div class="deck">
{slide}
</div>
<script>
// single-slide embed: force active + best-effort autoplay
(function(){{
  var s=document.querySelector('.slide'); if(s) s.classList.add('active');
  document.querySelectorAll('video').forEach(function(v){{
    v.muted = v.muted || !v.hasAttribute('controls');
    if(!v.hasAttribute('controls')){{ v.loop=true; }}
    var p=v.play(); if(p&&p.catch) p.catch(function(){{}});
  }});
}})();
</script>
</body>
</html>
"""

manifest = []
for idx, (name, block) in enumerate(slides):
    # ensure the slide carries the active class statically too
    fn = f"p{idx:02d}_{name}.html"
    with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
        f.write(PAGE.format(head=head, slide=block))
    manifest.append({"idx": idx, "slide": name, "file": fn})

with open(os.path.join(OUT, "_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

for m in manifest:
    print(f"  {m['idx']:>2}  {m['slide']:<22}  {m['file']}")
