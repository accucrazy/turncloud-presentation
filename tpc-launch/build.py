"""
build.py — 從 slides.yaml + templates/ 產出 index.html

用法：
    python build.py
    python build.py --watch          # 監看 slides.yaml / templates/ 變動自動重建
    python build.py --out preview.html
"""
from __future__ import annotations

import argparse
import io
import sys
import time
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Undefined

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent
TEMPLATES_DIR = ROOT / "templates"
SLIDES_FILE = ROOT / "slides.yaml"
DEFAULT_OUT = ROOT / "index.html"


class SilentUndefined(Undefined):
    """讓未定義變數渲染為空字串，避免簡報缺欄位時整份炸掉"""

    def _fail_with_undefined_error(self, *args, **kwargs):
        return ""

    __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = (
        __truediv__
    ) = __rtruediv__ = __floordiv__ = __rfloordiv__ = __mod__ = __rmod__ = (
        __pos__
    ) = __neg__ = __call__ = __getitem__ = __lt__ = __le__ = __gt__ = (
        __ge__
    ) = __int__ = __float__ = __complex__ = __pow__ = __rpow__ = (
        _fail_with_undefined_error
    )

    def __str__(self):
        return ""

    def __bool__(self):
        return False


def make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=False,
        trim_blocks=False,
        lstrip_blocks=False,
        undefined=SilentUndefined,
    )
    return env


def render(out_path: Path) -> None:
    data = yaml.safe_load(SLIDES_FILE.read_text(encoding="utf-8"))
    meta = data.get("meta", {})
    slides = data.get("slides", [])
    total = len(slides)

    env = make_env()

    rendered = []
    for i, slide in enumerate(slides):
        template_name = slide.get("template")
        if not template_name:
            raise ValueError(f"Slide #{i + 1} ({slide.get('id', '?')}) 缺少 template 欄位")

        template_path = f"slide_{template_name}.html"
        try:
            template = env.get_template(template_path)
        except Exception as e:
            raise ValueError(
                f"Slide #{i + 1} ({slide.get('id', '?')}) 找不到模板 {template_path}: {e}"
            )

        ctx = {
            **slide,
            "page": f"{i + 1:02d}",
            "total": f"{total:02d}",
            "is_first": (i == 0),
            "index": i,
        }
        slide_html = template.render(**ctx)
        separator = (
            f"<!-- ══════════ SLIDE {i + 1:02d}: "
            f"{slide.get('id', '?')} ({template_name}) ══════════ -->"
        )
        rendered.append(f"{separator}\n{slide_html}")

    auto_gen_notice = (
        "<!--\n"
        "  ⚠ 自動產出 — 請勿直接編輯本檔。\n"
        "  改內容請編輯 slides.yaml；改版型請改 templates/；改完跑 `python build.py`。\n"
        "-->\n"
    )

    base = env.get_template("base.html")
    html = auto_gen_notice + base.render(
        meta=meta,
        slides_html="\n\n".join(rendered),
    )

    out_path.write_text(html, encoding="utf-8")
    print(f"✓ Built {out_path.relative_to(ROOT)} — {total} slides")


def watch(out_path: Path) -> None:
    watched_files: dict[Path, float] = {}

    def collect() -> dict[Path, float]:
        files = [SLIDES_FILE, *TEMPLATES_DIR.glob("*.html")]
        return {f: f.stat().st_mtime for f in files if f.exists()}

    print("👀 監看中… (Ctrl+C 結束)")
    render(out_path)
    watched_files = collect()

    try:
        while True:
            time.sleep(0.5)
            current = collect()
            if current != watched_files:
                try:
                    render(out_path)
                except Exception as e:
                    print(f"✗ 建置失敗：{e}")
                watched_files = current
    except KeyboardInterrupt:
        print("\n👋 結束監看")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build slide deck from slides.yaml")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="輸出 HTML 路徑")
    parser.add_argument("--watch", action="store_true", help="監看檔案變動自動重建")
    args = parser.parse_args()

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path

    if not SLIDES_FILE.exists():
        print(f"✗ 找不到 {SLIDES_FILE}", file=sys.stderr)
        return 1

    if args.watch:
        watch(out_path)
    else:
        render(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
