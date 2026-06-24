import os, re, shutil, glob, json

SRC = r"d:\DEV\Turncloud Launch\ai talk"
DST = r"d:\DEV\Turncloud Launch\ai-talk-deck\img\talk"
if os.path.isdir(DST):
    shutil.rmtree(DST)
os.makedirs(DST, exist_ok=True)

manifest = []  # (sort_key, dst_name, original)

named_map = {
    "(英文).png":     ("bio.png", 2.5),           # Ian Wu founder/CEO bio
    "(英文) (2).png": ("cot-training.png", 34.5), # 獨家思維鏈模型訓練技術
    "英文 (2).png":   ("ad-case.png", 37.3),       # 口碑文 ad case
    "英文.png":       ("ad-results.png", 38.5),    # 不只引發討論 縮短消費決策期
    "英文 (3).png":   ("ad-results2.png", 38.6),   # (dup) ad results
    "英文 (4).png":   ("funnel.png", 74.6),        # 硬廣＋軟廣行銷漏斗 3.0
    "✅.png":         ("market-tam.png", 74.5),    # 輿情操作市場潛力 TAM/SAM
}

for f in os.listdir(SRC):
    full = os.path.join(SRC, f)
    if not os.path.isfile(full):
        continue
    if not f.lower().endswith(".png"):
        continue
    m = re.match(r"^(\d+)\.png$", f)
    if m:
        n = int(m.group(1))
        dst = f"t{n:02d}.png"
        shutil.copy2(full, os.path.join(DST, dst))
        manifest.append((float(n), dst, f))
    elif f in named_map:
        dst, key = named_map[f]
        shutil.copy2(full, os.path.join(DST, dst))
        manifest.append((key, dst, f))

manifest.sort(key=lambda x: x[0])
with open(os.path.join(os.path.dirname(DST), "..", "_talk_manifest.json"), "w", encoding="utf-8") as fp:
    json.dump([{"order": k, "file": d, "orig": o} for k, d, o in manifest], fp, ensure_ascii=False, indent=2)

print(f"Copied {len(manifest)} images to {DST}")
for k, d, o in manifest:
    line = f"  {k:>6}  {d:<16}  <- {o}"
    print(line.encode('ascii', 'replace').decode('ascii'))
