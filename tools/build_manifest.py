#!/usr/bin/env python3
"""Gộp content/posts/*/ thành một manifest để Worker import lúc bundle.

Worker không đọc được filesystem lúc chạy, nên nội dung phải nằm trong bundle.
Manifest là artifact dẫn xuất — **không commit**. Sinh trước khi test/dev/deploy.

Đây là artifact duy nhất của kiến trúc này, và nó không có gate byte-exact: sai
thì test đỏ ngay, không cần so hash.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from content import POSTS_DIR, ContentError, load_posts

ROOT = Path(__file__).resolve().parents[1]
# Trường nào renderer đọc thì trường đó phải vào manifest. `sources`,
# `tested_on`, `last_verified`, `changes_system` là phần hợp đồng mà cổng nội
# dung bắt buộc phải có — bỏ chúng khỏi manifest là bắt tác giả viết dữ liệu mà
# không ai đọc.
FIELDS = (
    "issue", "date", "level", "axis", "scope", "slug", "eyebrow", "title", "lede", "description",
    "tested_on", "last_verified", "changes_system", "sources",
)


def build(posts_dir: Path | None = None) -> dict:
    posts = load_posts(posts_dir)
    return {
        "posts": [{field: post.meta.get(field) for field in FIELDS} for post in posts],
        "bodies": {post.slug: post.body for post in posts},
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    # `wrangler dev` và `wrangler deploy` tự chạy script này qua build.command
    # trong wrangler.jsonc, và không có chỗ nào truyền cờ vào được. Không có biến
    # môi trường này thì bước dựng của wrangler luôn đọc content/posts/ và ghi đè
    # manifest mà `npm run dev:draft` vừa sinh ra — xem bản nháp thành ra không thể.
    parser.add_argument("--posts", default=os.environ.get("NIX_POSTS_DIR") or None)
    parser.add_argument("--out", default=str(ROOT / "content" / "manifest.json"))
    args = parser.parse_args(argv)

    try:
        manifest = build(Path(args.posts) if args.posts else POSTS_DIR)
    except ContentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    out = Path(args.out)
    # content/ nằm trong .gitignore nên bản clone mới không có thư mục này; thiếu
    # dòng dưới thì `npm test` đỏ ngay ở lần chạy đầu.
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"✓ manifest: {len(manifest['posts'])} bài → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
