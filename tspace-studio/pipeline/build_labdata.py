"""experiments.json -> data/experiments.js (window.LAB_DATA) for file:// use."""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
obj = json.loads((DATA / "experiments.json").read_text(encoding="utf-8"))
out = DATA / "experiments.js"
out.write_text(
    "// Real experiment results: Pandora -> Culture Listening -> Banana.\n"
    "window.LAB_DATA = " + json.dumps(obj, ensure_ascii=False, indent=1) + ";\n",
    encoding="utf-8",
)
print(f"experiments.js — {out.stat().st_size//1024} KB, {len(obj['experiments'])} experiments")
