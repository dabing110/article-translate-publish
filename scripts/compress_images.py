#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""压缩图片: 转 JPEG、长边限 1200px、单张体积 < --max-kb (言序正文图硬限 1MB)。

用法:
    python compress_images.py --dir figs/ [--max-kb 1000] [--max-edge 1200] [--quality 86]

对目录内 png/jpg/jpeg/webp 逐张处理, 输出同名 .jpg。
退出码 0=全部达标, 2=存在超限文件。
"""
import argparse
import os
import sys

from PIL import Image


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="图片目录")
    ap.add_argument("--max-kb", type=int, default=1000, help="单张体积上限 KB")
    ap.add_argument("--max-edge", type=int, default=1200, help="长边上限 px")
    ap.add_argument("--quality", type=int, default=86, help="JPEG 质量")
    args = ap.parse_args()

    exts = (".png", ".jpg", ".jpeg", ".webp")
    files = [f for f in sorted(os.listdir(args.dir)) if f.lower().endswith(exts)]
    if not files:
        print(f"目录无图片: {args.dir}")
        return 1

    ok = True
    for f in files:
        p = os.path.join(args.dir, f)
        try:
            img = Image.open(p).convert("RGB")
        except Exception as e:
            print(f"SKIP {f}: {e}")
            continue
        w, h = img.size
        if max(w, h) > args.max_edge:
            r = args.max_edge / max(w, h)
            img = img.resize((int(w * r), int(h * r)), Image.LANCZOS)
        out = os.path.splitext(p)[0] + ".jpg"
        img.save(out, "JPEG", quality=args.quality, optimize=True)
        kb = os.path.getsize(out) / 1024
        flag = "OK  " if kb <= args.max_kb else "OVER"
        if kb > args.max_kb:
            ok = False
        print(f"{flag} {f} -> {os.path.basename(out)} {img.size} {kb:.0f}KB")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    sys.exit(main())
