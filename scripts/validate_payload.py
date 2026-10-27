#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 create_article payload: title/abstract 字数、chapters 结构与块类型。

用法:
    python validate_payload.py --payload article.json

校验项:
  - title <= 30 字, abstract <= 100 字 (言序硬限, 超限被拒不报长度)
  - chapters 可为 JSON 数组或 JSON 数组字符串 (字符串会先 json.loads)
  - 每章有 title 且 blocks 非空; 块类型仅 paragraph/image/list/table
  - paragraph 有 content, image 有 url, list 有 items
  - cover_img 必须是 http(s) 公网 URL (本地路径会在 publish 阶段报 invalid media_id)

退出码 0=通过, 2=校验失败 (不写任何文件, 不会静默截断)。
"""
import argparse
import json
import sys

VALID_BLOCKS = {"paragraph", "image", "list", "table"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload", required=True, help="payload JSON 文件路径")
    args = ap.parse_args()

    try:
        with open(args.payload, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"payload 文件读取/解析失败: {e}")
        return 2

    errors = []
    title = data.get("title", "")
    abstract = data.get("abstract", "")
    if not title:
        errors.append("title 为空")
    elif len(title) > 30:
        errors.append(f"title {len(title)} 字 > 30")
    if not abstract:
        errors.append("abstract 为空")
    elif len(abstract) > 100:
        errors.append(f"abstract {len(abstract)} 字 > 100")

    cover = data.get("cover_img") or ""
    if cover and not cover.startswith("http"):
        errors.append(f"cover_img 不是公网 URL: {cover[:60]}")

    chapters = data.get("chapters")
    if isinstance(chapters, str):
        try:
            chapters = json.loads(chapters)
        except json.JSONDecodeError as e:
            errors.append(f"chapters JSON 字符串解析失败: {e}")
            chapters = None
    if chapters is not None:
        if not isinstance(chapters, list) or not chapters:
            errors.append("chapters 为空或不是数组")
        else:
            for i, ch in enumerate(chapters):
                label = ch.get("title") or f"第{i + 1}章"
                if not ch.get("title"):
                    errors.append(f"第{i + 1}章缺 title")
                blocks = ch.get("blocks")
                if not blocks:
                    errors.append(f"「{label}」blocks 为空")
                    continue
                for j, b in enumerate(blocks):
                    t = b.get("type")
                    if t not in VALID_BLOCKS:
                        errors.append(f"「{label}」block{j + 1} 非法类型: {t}")
                        continue
                    if t == "paragraph" and not b.get("content"):
                        errors.append(f"「{label}」block{j + 1} paragraph 缺 content")
                    if t == "image" and not b.get("url"):
                        errors.append(f"「{label}」block{j + 1} image 缺 url")
                    if t == "list" and not b.get("items"):
                        errors.append(f"「{label}」block{j + 1} list 缺 items")

    if errors:
        print("校验失败:")
        for e in errors:
            print("  -", e)
        return 2
    n = len(chapters) if isinstance(chapters, list) else 0
    print(f"校验通过: title {len(title)} 字 / abstract {len(abstract)} 字 / {n} 章")
    return 0


if __name__ == "__main__":
    sys.exit(main())
