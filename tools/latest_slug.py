#!/usr/bin/env python3
"""In ra slug của bài mới nhất ĐÃ xuất bản.

Dùng cho bước kiểm tra site thật sau khi deploy. Phải lọc theo ngày chứ không
chỉ lấy số hiệu lớn nhất: bài viết trước cho tuần sau đã nằm sẵn trong bundle
nhưng URL của nó chưa tồn tại, nên hỏi nó sẽ ra 404 và làm đỏ một phép kiểm tra
lẽ ra phải xanh.

Ngày trong `meta.date` là ngày theo giờ Việt Nam — cùng quy ước với
`PUBLISH_OFFSET` trong src/content.js.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content import ContentError, load_posts  # noqa: E402

PUBLISH_TZ = timezone(timedelta(hours=7))


def published_at(post) -> datetime | None:
    raw = post.meta.get("date")
    try:
        return datetime.strptime(str(raw), "%Y-%m-%d").replace(tzinfo=PUBLISH_TZ)
    except (TypeError, ValueError):
        # Ngày hỏng thì coi như đã xuất bản — cùng lối xử lý với isPublished()
        # trong src/content.js: giấu mất một bài là hỏng theo cách khó thấy hơn.
        return None


def latest_slug(posts_dir: Path | None = None, now: datetime | None = None) -> str | None:
    now = now or datetime.now(PUBLISH_TZ)
    published = [
        post
        for post in load_posts(posts_dir)
        if (at := published_at(post)) is None or at <= now
    ]
    if not published:
        return None
    return max(published, key=lambda post: post.meta.get("issue", 0)).slug


def main(argv=None) -> int:
    try:
        slug = latest_slug()
    except ContentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1
    if slug is None:
        print("✗ không có bài nào đã xuất bản", file=sys.stderr)
        return 1
    print(slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
