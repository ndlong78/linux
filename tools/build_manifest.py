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
import sys
from pathlib import Path

from content import POSTS_DIR, ContentError, load_posts

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("issue", "date", "axis", "slug", "eyebrow", "title", "lede", "description")


def build(posts_dir: Path | None = None) -> dict:
    posts = load_posts(posts_dir)
    return {
        "posts": [{field: post.meta.get(field) for field in FIELDS} for post in posts],
        "bodies": {post.slug: post.body for post in posts},
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--posts", default=None)
    parser.add_argument("--out", default=str(ROOT / "content" / "manifest.json"))
    args = parser.parse_args(argv)

    try:
        manifest = build(Path(args.posts) if args.posts else POSTS_DIR)
    except ContentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    Path(args.out).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"✓ manifest: {len(manifest['posts'])} bài → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
