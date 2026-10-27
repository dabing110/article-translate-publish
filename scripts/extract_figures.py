#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取文章页面的配图清单：url + alt + 上下文（按出现顺序）。

用法:
    python extract_figures.py --url <文章URL> --out figs_manifest.json [--download figs/]

输出 JSON 数组, 元素: {"url": ..., "alt": ..., "context": ...}
--download 给定目录时同时下载图片为 figN.<ext> (顺序下载, 不用并行)
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from urllib.parse import urljoin

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="文章页面 URL")
    ap.add_argument("--out", required=True, help="清单输出 JSON 路径")
    ap.add_argument("--download", help="可选: 下载目录 (顺序下载)")
    args = ap.parse_args()

    html = fetch(args.url)
    figures = []
    for m in re.finditer(r"<img[^>]*>", html):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        if not src:
            continue
        url = src.group(1)
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = urljoin(args.url, url)
        if not url.startswith("http"):
            continue
        alt_m = re.search(r'alt="([^"]*)"', tag)
        ctx = re.sub(r"\s+", " ", re.sub(
            r"<[^>]+>", " ", html[max(0, m.start() - 200):m.end() + 200])).strip()
        figures.append({
            "url": url,
            "alt": alt_m.group(1) if alt_m else "",
            "context": ctx[-160:],
        })

    if not figures:
        print("未提取到任何 <img> 标签")
        return 1

    if args.download:
        os.makedirs(args.download, exist_ok=True)
        for i, fig in enumerate(figures, 1):
            ext = os.path.splitext(fig["url"].split("?")[0])[1] or ".png"
            dest = os.path.join(args.download, f"fig{i}{ext}")
            try:
                req = urllib.request.Request(fig["url"], headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
                    f.write(resp.read())
                fig["local"] = dest
                print(f"OK   fig{i} {os.path.getsize(dest)//1024}KB {fig['alt'][:40]}")
            except Exception as e:  # 单张失败不阻塞
                fig["local"] = None
                print(f"FAIL fig{i} {e} {fig['url']}")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(figures, f, ensure_ascii=False, indent=2)
    print(f"共 {len(figures)} 张, 清单写入 {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
