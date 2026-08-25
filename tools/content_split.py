#!/usr/bin/env python3
"""Tách bài Linux Daily thành (nội dung, metadata) và kiểm chứng ranh giới.

Bài trong linux-daily là trang HTML đầy đủ: head/meta/og, global nav, masthead,
back-to-top, related-nav, footer. Ở kiến trúc dynamic, tất cả những thứ đó do
renderer sinh ra tại request; chỉ phần thân bài là nội dung thật cần giữ trong git.

Script này KHÔNG chuyển đổi gì. Nó chỉ trả lời một câu hỏi trước khi ai đó xây
tiếp lên trên: **ranh giới nội dung/khung có xác định được một cách máy móc, cho
mọi bài, không cần đoán?**

Ranh giới:
    bắt đầu  <header class="post">
    kết thúc dòng ngay trước <!-- related-nav:start -->

Mọi thứ ngoài khoảng đó là khung. Nếu một bài không khớp khuôn này thì script
báo lỗi thay vì cắt bừa — cắt sai một bài là mất nội dung im lặng.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

CONTENT_START = '<header class="post">'
CONTENT_END = "<!-- related-nav:start -->"
META_OPEN = '<script type="application/json" id="ld-meta">'
META_CLOSE = "</script>"


class SplitError(Exception):
    """Bài không khớp khuôn — không cắt, để người xử lý."""


@dataclass(frozen=True)
class Split:
    path: str
    prefix: str   # khung phía trên nội dung
    content: str  # thân bài
    suffix: str   # related-nav + footer + đóng thẻ
    meta: dict

    def reassemble(self) -> str:
        return self.prefix + self.content + self.suffix


def _read_meta(text: str, path: str) -> dict:
    start = text.find(META_OPEN)
    if start < 0:
        raise SplitError(f"{path}: thiếu khối ld-meta")
    body_start = start + len(META_OPEN)
    end = text.find(META_CLOSE, body_start)
    if end < 0:
        raise SplitError(f"{path}: khối ld-meta không đóng")
    try:
        return json.loads(text[body_start:end])
    except json.JSONDecodeError as exc:
        raise SplitError(f"{path}: ld-meta không phải JSON hợp lệ ({exc})") from exc


def split_post(path: Path) -> Split:
    text = path.read_text(encoding="utf-8")
    name = path.name

    start = text.find(CONTENT_START)
    if start < 0:
        raise SplitError(f"{name}: không tìm thấy {CONTENT_START}")
    if text.find(CONTENT_START, start + 1) >= 0:
        raise SplitError(f"{name}: có nhiều hơn một {CONTENT_START}")

    end = text.find(CONTENT_END, start)
    if end < 0:
        raise SplitError(f"{name}: không tìm thấy {CONTENT_END} sau nội dung")

    return Split(
        path=name,
        prefix=text[:start],
        content=text[start:end],
        suffix=text[end:],
        meta=_read_meta(text, name),
    )


def audit(posts: list[Path]) -> tuple[list[Split], list[str]]:
    splits: list[Split] = []
    errors: list[str] = []
    for path in posts:
        try:
            item = split_post(path)
        except SplitError as exc:
            errors.append(str(exc))
            continue
        # Ghép lại phải ra đúng byte gốc. Đây là bất biến của phép tách: nếu sai
        # thì mọi thứ xây bên trên đều dựa trên nội dung đã bị biến dạng.
        if item.reassemble() != path.read_text(encoding="utf-8"):
            errors.append(f"{path.name}: ghép lại không khớp byte gốc")
            continue
        splits.append(item)
    return splits, errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--posts", required=True, help="Thư mục chứa posts/*.html")
    parser.add_argument("--json", action="store_true", help="In báo cáo dạng JSON")
    args = parser.parse_args(argv)

    posts = sorted(Path(args.posts).glob("post-*.html"))
    if not posts:
        print(f"Không tìm thấy bài nào trong {args.posts}", file=sys.stderr)
        return 1

    splits, errors = audit(posts)

    if args.json:
        print(json.dumps(
            {
                "total": len(posts),
                "clean": len(splits),
                "errors": errors,
                "posts": [
                    {
                        "path": s.path,
                        "issue": s.meta.get("issue"),
                        "content_bytes": len(s.content.encode("utf-8")),
                        "chrome_bytes": len((s.prefix + s.suffix).encode("utf-8")),
                    }
                    for s in splits
                ],
            },
            ensure_ascii=False,
            indent=2,
        ))
        return 1 if errors else 0

    content_bytes = sum(len(s.content.encode("utf-8")) for s in splits)
    chrome_bytes = sum(len((s.prefix + s.suffix).encode("utf-8")) for s in splits)
    total = content_bytes + chrome_bytes

    print(f"Bài kiểm tra      : {len(posts)}")
    print(f"Tách sạch         : {len(splits)}")
    print(f"Nội dung thật     : {content_bytes:,} bytes ({content_bytes / total:.1%})")
    print(f"Khung sinh lại được: {chrome_bytes:,} bytes ({chrome_bytes / total:.1%})")

    if errors:
        print(f"\n✗ {len(errors)} bài không khớp khuôn:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("\n✓ Mọi bài tách được bằng quy tắc cố định và ghép lại khớp byte gốc.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
