"""
generate.py — 用 Google Gemini 根據自然語言描述生成新的投影片條目

用法：
    python generate.py "做一頁談 2026 Q1 商業目標，列三個 KPI"
    python generate.py --template two_col "..."
    python generate.py --insert-at 5 "..."          # 插入到第 5 頁之後（預設追加在最後）
    python generate.py --dry-run "..."              # 只印出不寫入 yaml

需要 .env：
    GOOGLE_API_KEY=AIzaSy...
    GEMINI_MODEL=gemini-2.5-flash       # 可選，預設 gemini-2.5-flash
                                        # 想用更強的可改 gemini-2.5-pro
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).parent
SLIDES_FILE = ROOT / "slides.yaml"
TEMPLATES_DIR = ROOT / "templates"

SYSTEM_PROMPT = """你是一份 16:9 企業簡報的內容生成器，使用者用自然語言描述要新增的一頁，你的工作是生成「一個」對應的 YAML slide 條目，附加到既有的 slides.yaml。

# 嚴格規則
1. 只輸出 YAML，不要有任何說明文字、不要包 markdown code fence。
2. **縮排必須是 YAML 合法格式**：
   - 第一行必須是 `  - id: xxx`（**前面 2 個空格**、dash、space）
   - 該 slide 底下其他 key 必須**前面 4 個空格**對齊（dash 後相當於 2 個空格的視覺對齊）
   - 嵌套陣列每多一層加 2 個空格
   - 範例：`  - id:` 在 col 2，`    template:` 在 col 4，`    boxes:` 在 col 4，`      - color:` 在 col 6
   - 嚴禁：dash 在 col 0、keys 在 col 4 的混亂格式（YAML 解析會失敗）
3. 必填欄位：`id`（小寫英數+底線）、`template`、`title`。
4. `template` 必為以下之一：cover / two_col / layers / workforce / ecosystem / closing
5. 各 template 的必要欄位：
   - two_col: tag, title, subtitle, media, boxes(2-3 個), meta_left
   - layers: tag, title, subtitle, media, layers(2-3 個), meta_left, 可選 footer_box
   - workforce: tag, title, subtitle, media, agents(3-6 個), meta_left
   - ecosystem: tag, title, subtitle, media, header_box, pills(6 個), footer_box, meta_left
   - cover: media, pre, title, lede, signatures
   - closing: media, quote, lede, sig
6. `bg` 欄位（兩欄類）可選 dark / warm / violet / cyan
7. 可用顏色：cyan / violet / orange / green / pink / gold（box.color、tag.color 等）
8. HTML 字串內可用：<br>、<strong>、<span class="c|v|o|g|p">（c=青、v=紫、o=橘、g=綠、p=粉）
9. box 列點用 `bullets:` 欄位（不是 items），純文字段落用 `body:` 欄位。
10. header_box / footer_box 也支援 bullets / body。
11. 媒體路徑放在 `media:` 欄位，如 `img/15_xxx.jpg` 或 `img/15_xxx.mp4`（如果不知道實際檔名，用 `img/{id}.jpg` 佔位）
12. 不要重複現有 slide 的 id。

# 語氣與風格
- 標題短、力道強、可用色彩 span 點綴重點字
- subtitle 一句點題，用 <strong> 強調關鍵詞
- box 標題簡短，items 列點 3-5 條為佳，每條開頭可用 <strong> 強調名詞
- 全份簡報定位：Accucrazy 加入騰雲，發表 Enterprise AI OS 與 5 個 AI Agent

# 輸出範例（two_col）
```
  - id: q1_goals
    template: two_col
    bg: dark
    media: img/q1_goals.jpg
    tag: { color: cyan, text: "CHAPTER 08 · Q1 商業目標" }
    title: '2026 Q1 — <span class="c">三個關鍵 KPI</span>'
    subtitle: "把 AI OS 從 demo 推向營收的第一個 90 天。"
    meta_left: "Q1 OKR — The Pocket Company"
    boxes:
      - color: cyan
        title: "三大目標"
        bullets:
          - "簽下 5 家企業客戶"
          - "MRR 達到 200 萬"
          - "Agent 每月執行任務破百萬次"
```
（注意：實際輸出不要包 ``` code fence）
"""


def load_existing_yaml() -> str:
    if not SLIDES_FILE.exists():
        return ""
    return SLIDES_FILE.read_text(encoding="utf-8")


def list_available_templates() -> list[str]:
    return sorted(
        p.stem.replace("slide_", "")
        for p in TEMPLATES_DIR.glob("slide_*.html")
    )


def call_llm(description: str, template_hint: str | None) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print(
            "✗ 缺少 google-genai 套件，請先：pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(
            "✗ 缺少 GOOGLE_API_KEY，請複製 .env.example 為 .env 並填入",
            file=sys.stderr,
        )
        sys.exit(1)

    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)

    user_msg_parts = [
        "以下是目前的 slides.yaml（僅作風格參考）：",
        "```yaml",
        load_existing_yaml(),
        "```",
        "",
        f"請新增一頁：{description}",
    ]
    if template_hint:
        user_msg_parts.append(f"\n要求使用 template：{template_hint}")
    user_msg_parts.append(
        "\n請直接輸出新的 YAML 條目（以 `  - id:` 開頭，2 空格縮排），不要有任何其他文字。"
    )

    print(f"⌛ 呼叫 {model}…")
    response = client.models.generate_content(
        model=model,
        contents="\n".join(user_msg_parts),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=4000,
            temperature=0.5,
        ),
    )

    text = (response.text or "").strip()
    text = re.sub(r"^```ya?ml\s*\n", "", text)
    text = re.sub(r"\n```\s*$", "", text)
    return text.strip()


def normalize_indent(snippet: str) -> str:
    """
    修正 LLM 常見的縮排問題：
    - 原始：`- id` 在 col 0、`    template` 在 col 4（YAML 不合法，dash + key 應該差 2）
    - 修正：只保留「最上層 dash」原位，其餘所有行都 dedent 抵銷 offset
    """
    lines = snippet.split("\n")
    start = 0
    while start < len(lines) and not lines[start].strip():
        start += 1
    if start >= len(lines):
        return snippet

    first = lines[start]
    stripped = first.lstrip(" ")
    if not stripped.startswith("- "):
        return snippet

    dash_col = len(first) - len(stripped)

    key_col = None
    for line in lines[start + 1 :]:
        if not line.strip():
            continue
        ls = line.lstrip(" ")
        if ls.startswith("- "):
            continue
        key_col = len(line) - len(ls)
        break

    if key_col is None:
        return snippet

    correct_key_col = dash_col + 2
    offset = key_col - correct_key_col
    if offset <= 0:
        return snippet

    fixed = []
    seen_top_dash = False
    for line in lines:
        if not line.strip():
            fixed.append(line)
            continue
        ls = line.lstrip(" ")
        col = len(line) - len(ls)
        if not seen_top_dash and ls.startswith("- ") and col == dash_col:
            seen_top_dash = True
            fixed.append(line)
        else:
            new_col = max(col - offset, 0)
            fixed.append(" " * new_col + ls)
    return "\n".join(fixed)


def ensure_top_level_indent(snippet: str) -> str:
    """
    確保最外層 dash 在 col 2（追加到 slides.yaml 的 slides: list 下時所需）
    """
    lines = snippet.split("\n")
    start = 0
    while start < len(lines) and not lines[start].strip():
        start += 1
    if start >= len(lines):
        return snippet

    first = lines[start]
    stripped = first.lstrip(" ")
    if not stripped.startswith("- "):
        return snippet

    dash_col = len(first) - len(stripped)
    if dash_col == 2:
        return snippet

    shift = 2 - dash_col
    if shift > 0:
        return "\n".join(
            (" " * shift + line) if line.strip() else line for line in lines
        )
    return "\n".join(line[abs(shift) :] if line.startswith(" " * abs(shift)) else line for line in lines)


def validate_yaml(snippet: str) -> dict:
    """驗證生成的 YAML 可以被解析、且符合 slide 結構"""
    try:
        parsed = yaml.safe_load(snippet)
    except yaml.YAMLError as e:
        raise ValueError(f"生成的 YAML 無法解析：{e}")

    if not isinstance(parsed, list) or len(parsed) != 1:
        raise ValueError("生成的內容必須是「一個」YAML list 條目")

    slide = parsed[0]
    if not isinstance(slide, dict):
        raise ValueError("生成的條目必須是 dict")

    required = {"id", "template", "title"}
    missing = required - slide.keys()
    if missing:
        raise ValueError(f"生成的 slide 缺少必填欄位：{missing}")

    available = list_available_templates()
    if slide["template"] not in available:
        raise ValueError(
            f"template '{slide['template']}' 不存在，可選：{available}"
        )

    return slide


def insert_into_yaml(snippet: str, insert_at: int | None) -> None:
    """
    在 slides.yaml 的 slides: list 裡插入新條目。
    insert_at = None 表示追加在最後。
    insert_at = 5 表示插入到第 5 頁之後（變成第 6 頁）。
    """
    existing_data = yaml.safe_load(load_existing_yaml())
    new_slide = yaml.safe_load(snippet)[0]
    slides = existing_data.get("slides", [])

    if insert_at is None:
        slides.append(new_slide)
        pos_msg = f"末尾（第 {len(slides)} 頁）"
    else:
        idx = max(0, min(insert_at, len(slides)))
        slides.insert(idx, new_slide)
        pos_msg = f"第 {idx + 1} 頁"

    existing_data["slides"] = slides

    # 直接 append snippet 到檔案，保留現有 YAML 的註解與排版
    # 只有 insert 中間時才需要重寫整個檔案（會失去註解）
    if insert_at is None:
        with SLIDES_FILE.open("a", encoding="utf-8") as f:
            f.write("\n" + snippet.rstrip() + "\n")
        print(f"✓ 已追加到 slides.yaml {pos_msg}")
    else:
        SLIDES_FILE.write_text(
            yaml.safe_dump(
                existing_data,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                width=200,
            ),
            encoding="utf-8",
        )
        print(f"✓ 已插入到 slides.yaml {pos_msg}")
        print("⚠ 中間插入會重寫整個 slides.yaml，註解會遺失（用 git 還原即可）")


def main() -> int:
    load_dotenv(ROOT / ".env")

    parser = argparse.ArgumentParser(description="用 Gemini 生成新的投影片條目")
    parser.add_argument("description", help="這一頁要講什麼（自然語言）")
    parser.add_argument(
        "--template",
        choices=list_available_templates(),
        help="指定 template 類型（不指定的話讓 Gemini 自己決定）",
    )
    parser.add_argument(
        "--insert-at",
        type=int,
        default=None,
        help="插入到第 N 頁之後（不指定的話追加在最後）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只印出 YAML，不寫入 slides.yaml",
    )
    args = parser.parse_args()

    raw_snippet = call_llm(args.description, args.template)

    snippet = normalize_indent(raw_snippet)
    snippet = ensure_top_level_indent(snippet)

    if snippet != raw_snippet:
        print("ℹ 自動修正了縮排")

    print("\n──── 生成的 YAML ────")
    print(snippet)
    print("─────────────────────\n")

    try:
        slide = validate_yaml(snippet)
    except ValueError as e:
        print(f"✗ 驗證失敗：{e}", file=sys.stderr)
        print("\n原始 LLM 輸出：")
        print(raw_snippet)
        return 1

    print(f"✓ 驗證通過：id={slide['id']}, template={slide['template']}")

    if args.dry_run:
        print("（dry-run：未寫入 slides.yaml）")
        return 0

    insert_into_yaml(snippet, args.insert_at)
    print("\n下一步：python build.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
