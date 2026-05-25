"""
compress_videos.py — 用 ffmpeg 把 img/ 內的 .mov 壓成 .mp4，並自動更新 slides.yaml 路徑

用法：
    python compress_videos.py                  # 壓縮所有 .mov + 更新 yaml
    python compress_videos.py --dry-run        # 只列出會做什麼，不實際執行
    python compress_videos.py --crf 23         # 自訂品質（預設 28；越低越精細越大）
    python compress_videos.py --no-yaml        # 只壓縮、不動 yaml
    python compress_videos.py --no-compress    # 只更新 yaml（假設 .mp4 已存在）
    python compress_videos.py --keep-mov       # 完成後不提示刪除原始檔

需要先安裝 ffmpeg：
    brew install ffmpeg
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
IMG_DIR = ROOT / "img"
SLIDES_FILE = ROOT / "slides.yaml"


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        print("✗ 找不到 ffmpeg。請先安裝：brew install ffmpeg", file=sys.stderr)
        sys.exit(1)


def fmt_mb(size_bytes: int) -> str:
    return f"{size_bytes / 1_000_000:.1f} MB"


def compress_one(src: Path, crf: int, dry_run: bool) -> bool:
    dst = src.with_suffix(".mp4")
    src_size = src.stat().st_size

    if dst.exists():
        dst_size = dst.stat().st_size
        print(f"⊘ 已存在 {dst.name}（原始 {fmt_mb(src_size)} → 已壓 {fmt_mb(dst_size)}），跳過")
        return True

    if dry_run:
        print(f"→ 會壓縮：{src.name}（{fmt_mb(src_size)}） → {dst.name} (crf={crf})")
        return True

    print(f"⌛ 壓縮中：{src.name}（{fmt_mb(src_size)}）→ {dst.name}", flush=True)
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(src),
                "-vcodec", "libx264", "-crf", str(crf), "-preset", "slow",
                "-acodec", "aac",
                "-movflags", "+faststart",
                str(dst),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        print(f"✗ 壓縮失敗：{src.name}: {e}", file=sys.stderr)
        if dst.exists():
            dst.unlink()
        return False

    dst_size = dst.stat().st_size
    saved_pct = (1 - dst_size / src_size) * 100
    print(f"✓ 完成：{dst.name}（{fmt_mb(src_size)} → {fmt_mb(dst_size)}，省 {saved_pct:.0f}%）")
    return True


def update_yaml(mov_names: list[str], dry_run: bool) -> int:
    if not SLIDES_FILE.exists():
        print(f"ℹ 找不到 {SLIDES_FILE}，跳過 yaml 更新")
        return 0

    text = SLIDES_FILE.read_text(encoding="utf-8")
    changed = 0

    for name in mov_names:
        mov_ref = f"media: img/{name}"
        mp4_ref = f"media: img/{name[:-4]}.mp4"
        if mov_ref in text:
            text = text.replace(mov_ref, mp4_ref)
            changed += 1
            print(f"→ 更新 yaml：{mov_ref}  →  {mp4_ref}")

    if changed == 0:
        print("ℹ slides.yaml 沒有需要更新的 .mov 引用")
        return 0

    if dry_run:
        print(f"(dry-run：未實際寫入，但會更新 {changed} 處)")
        return changed

    SLIDES_FILE.write_text(text, encoding="utf-8")
    print(f"✓ slides.yaml 已更新 {changed} 處")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="壓縮 .mov 並更新 slides.yaml 路徑")
    parser.add_argument("--crf", type=int, default=28, help="壓縮品質，越低越精細（預設 28；常用範圍 23-30）")
    parser.add_argument("--dry-run", action="store_true", help="只顯示會做什麼，不實際執行")
    parser.add_argument("--no-yaml", action="store_true", help="只壓縮，不動 slides.yaml")
    parser.add_argument("--no-compress", action="store_true", help="只更新 yaml（假設 .mp4 已存在）")
    parser.add_argument("--keep-mov", action="store_true", help="不提示刪除原始 .mov 檔")
    args = parser.parse_args()

    mov_files = sorted(IMG_DIR.glob("*.mov"))
    if not mov_files:
        print("沒有找到任何 .mov 檔案")
        return 0

    total_src = sum(f.stat().st_size for f in mov_files)
    print(f"找到 {len(mov_files)} 個 .mov 檔案，合計 {fmt_mb(total_src)}\n")

    if not args.no_compress:
        check_ffmpeg()
        for src in mov_files:
            if not compress_one(src, args.crf, args.dry_run):
                return 1
        print()

    if not args.no_yaml:
        update_yaml([f.name for f in mov_files], args.dry_run)

    if args.dry_run:
        print("\n（dry-run 結束。確認 OK 後拿掉 --dry-run 重跑）")
        return 0

    print("\n下一步：python build.py 重新建置")

    if not args.keep_mov:
        existing_mov = [f for f in mov_files if f.with_suffix(".mp4").exists()]
        if existing_mov:
            total_mov_size = sum(f.stat().st_size for f in existing_mov)
            print(f"\n💡 你現在可以手動刪除以下 {len(existing_mov)} 個 .mov 原始檔（共 {fmt_mb(total_mov_size)}）：")
            for f in existing_mov:
                print(f"   rm {f.relative_to(ROOT)}")
            print("   ── 確認簡報播放正常後再刪，git 也還可以還原")
    return 0


if __name__ == "__main__":
    sys.exit(main())
