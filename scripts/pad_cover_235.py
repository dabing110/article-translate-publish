#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把封面 pad 成 2.35:1 (公众号标准封面比例)。

用左右各 20px 边缘条带横向拉伸延展背景, 不裁切任何内容 ——
AI 生成封面的标题通常在顶部, 中心裁切会丢题。

用法:
    python pad_cover_235.py --in cover.png --out cover.jpg [--ratio 2.35] [--quality 86]
"""
import argparse
import os
import sys

from PIL import Image


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="输入图片")
    ap.add_argument("--out", required=True, help="输出图片 (.jpg 走 JPEG 压缩)")
    ap.add_argument("--ratio", type=float, default=2.35, help="目标宽高比")
    ap.add_argument("--quality", type=int, default=86)
    args = ap.parse_args()

    img = Image.open(args.inp).convert("RGB")
    w, h = img.size
    target_w = int(h * args.ratio)

    if target_w <= w:
        canvas = img  # 已经够宽, 直接转换
    else:
        pad_total = target_w - w
        pl = pad_total // 2
        pr = pad_total - pl
        left = img.crop((0, 0, 20, h)).resize((pl, h), Image.LANCZOS)
        right = img.crop((w - 20, 0, w, h)).resize((pr, h), Image.LANCZOS)
        canvas = Image.new("RGB", (target_w, h))
        canvas.paste(left, (0, 0))
        canvas.paste(img, (pl, 0))
        canvas.paste(right, (pl + w, 0))

    if args.out.lower().endswith((".jpg", ".jpeg")):
        canvas.save(args.out, "JPEG", quality=args.quality, optimize=True)
    else:
        canvas.save(args.out)

    kb = os.path.getsize(args.out) / 1024
    print(f"{canvas.size} {kb:.0f}KB -> {args.out}")
    if kb > 2048:
        print("WARN: 超过 2MB 封面上限")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
