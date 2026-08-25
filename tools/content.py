#!/usr/bin/env python3
"""Đọc kho nội dung. Dùng chung cho validator và bước dựng manifest.

Một bài = một thư mục:

    content/posts/<slug>/meta.json   metadata (nguồn sự thật)
    content/posts/<slug>/body.html   fragment thân bài

Tách hai file là có chủ đích. Ở bản static, metadata nằm trong `<script id="ld-meta">`
NGAY TRONG trang, còn eyebrow/title/lede lại được viết lại lần nữa ở phần hiển thị
— hai bản của cùng một dữ liệu, và chúng lệch nhau thật (bài #055 của linux-daily
lệch cả lede lẫn tiêu đề nguồn). Ở đây metadata chỉ tồn tại một chỗ và renderer
sinh phần hiển thị từ nó, nên lớp lỗi đó không còn cửa xảy ra.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "content" / "posts"
META_NAME = "meta.json"
BODY_NAME = "body.html"


class ContentError(Exception):
    """Kho nội dung sai hình dạng — dừng, không đoán."""


@dataclass(frozen=True)
class Post:
    slug: str
    meta: dict
    body: str
    directory: Path


def _load_one(directory: Path) -> Post:
    meta_path = directory / META_NAME
    body_path = directory / BODY_NAME
    if not meta_path.is_file():
        raise ContentError(f"{directory.name}/: thiếu {META_NAME}")
    if not body_path.is_file():
        raise ContentError(f"{directory.name}/: thiếu {BODY_NAME}")
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContentError(f"{directory.name}/{META_NAME}: JSON không hợp lệ ({exc})") from exc
    if not isinstance(meta, dict):
        raise ContentError(f"{directory.name}/{META_NAME}: phải là một object JSON")
    return Post(
        slug=directory.name,
        meta=meta,
        body=body_path.read_text(encoding="utf-8"),
        directory=directory,
    )


def load_posts(posts_dir: Path | None = None) -> list[Post]:
    """Mọi bài, sắp theo issue tăng dần."""
    base = posts_dir or POSTS_DIR
    if not base.is_dir():
        return []
    posts = [_load_one(child) for child in sorted(base.iterdir()) if child.is_dir()]
    return sorted(posts, key=lambda post: post.meta.get("issue", 0))
