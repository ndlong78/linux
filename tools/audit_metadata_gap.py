#!/usr/bin/env python3
"""Tìm trường trong <head> mà renderer KHÔNG sinh lại được từ ld-meta.

Kiến trúc dynamic dựa trên một giả định: khung trang sinh được từ metadata cộng
cấu hình site. Giả định đó đúng tới đâu là chuyện phải đo, không phải chuyện tin.

Trường nào có trong <head> của bài nhưng không suy được từ `ld-meta` + `site.json`
thì phải đưa vào schema metadata trước khi bỏ HTML tĩnh — nếu không, chuyển kiến
trúc xong là mất trường đó, âm thầm, trên mọi bài cùng lúc.

Chạy:
    python3 tools/audit_metadata_gap.py --posts ../linux-daily/posts
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

META_OPEN = '<script type="application/json" id="ld-meta">'
META_CLOSE = "</script>"

# Các trường head cần đối chiếu: (nhãn, regex lấy content, khoá ld-meta tương ứng)
FIELDS = (
    ("meta name=description", r'<meta name="description" content="([^"]*)"', "lede"),
    ("og:description", r'<meta property="og:description" content="([^"]*)"', "lede"),
    ("og:title", r'<meta property="og:title" content="([^"]*)"', "title"),
    ("twitter:description", r'<meta name="twitter:description" content="([^"]*)"', "lede"),
)


def read_meta(text: str) -> dict:
    start = text.find(META_OPEN)
    end = text.find(META_CLOSE, start + len(META_OPEN))
    return json.loads(text[start + len(META_OPEN) : end])


def audit(posts: list[Path]) -> dict:
    result: dict[str, dict] = {
        label: {"derivable": 0, "divergent": 0, "missing": 0, "examples": []}
        for label, _, _ in FIELDS
    }
    for path in posts:
        text = path.read_text(encoding="utf-8")
        meta = read_meta(text)
        for label, pattern, key in FIELDS:
            found = re.search(pattern, text)
            bucket = result[label]
            if not found:
                bucket["missing"] += 1
                continue
            actual = html.unescape(found.group(1))
            if actual == str(meta.get(key, "")):
                bucket["derivable"] += 1
            else:
                bucket["divergent"] += 1
                if len(bucket["examples"]) < 2:
                    bucket["examples"].append(
                        {"post": path.name, "head": actual[:90], f"ld-meta.{key}": str(meta.get(key, ""))[:90]}
                    )
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--posts", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    posts = sorted(Path(args.posts).glob("post-*.html"))
    if not posts:
        print(f"Không tìm thấy bài nào trong {args.posts}", file=sys.stderr)
        return 1

    result = audit(posts)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Đối chiếu {len(posts)} bài\n")
        print(f"{'trường head':<24} {'suy được':>9} {'lệch':>6} {'thiếu':>6}")
        for label, _, _ in FIELDS:
            b = result[label]
            print(f"{label:<24} {b['derivable']:>9} {b['divergent']:>6} {b['missing']:>6}")

    gaps = [label for label, _, _ in FIELDS if result[label]["divergent"]]
    if gaps:
        print(
            "\n✗ Không sinh lại được từ ld-meta: " + ", ".join(gaps),
            file=sys.stderr,
        )
        print(
            "  → phải thêm vào schema metadata trước khi bỏ HTML tĩnh.",
            file=sys.stderr,
        )
        for label in gaps:
            for ex in result[label]["examples"]:
                print(f"  {label} · {ex['post']}", file=sys.stderr)
                for k, v in ex.items():
                    if k != "post":
                        print(f"      {k:<16} {v}", file=sys.stderr)
        return 1

    print("\n✓ Mọi trường head đối chiếu đều suy được từ ld-meta.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
