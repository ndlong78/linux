"""Manifest là mặt tiếp giáp duy nhất giữa kho nội dung và Worker.

Trường nào renderer đọc mà manifest không mang theo thì trang render ra sẽ thiếu
im lặng — HTML vẫn hợp lệ, test vẫn xanh, chỉ có nội dung là mất. Bộ này khoá
đúng chỗ đó lại.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_manifest  # noqa: E402

FIXTURES = ROOT / "test" / "fixtures"


@pytest.fixture()
def manifest() -> dict:
    return build_manifest.build(FIXTURES)


def test_moi_bai_mang_du_truong(manifest: dict):
    assert [post["slug"] for post in manifest["posts"]] == [
        "post-001-vi-du",
        "post-002-vi-du",
        "post-003-linux-only",
    ]
    optional = {"scope"}  # vắng scope nghĩa là cross-platform, không phải thiếu dữ liệu
    for post in manifest["posts"]:
        assert set(post) == set(build_manifest.FIELDS)
        assert all(post[field] is not None for field in set(build_manifest.FIELDS) - optional)


def test_hop_dong_xuat_xu_di_theo_manifest(manifest: dict):
    """`sources`/`tested_on`/`last_verified` là thứ trang bài render ra."""
    post = manifest["posts"][0]
    assert len(post["sources"]) == 2
    assert post["sources"][0]["kind"] in {"official", "upstream"}
    assert post["tested_on"] == ["Ubuntu 26.04 LTS", "FreeBSD 15.0-RELEASE"]
    assert post["last_verified"] == "2026-06-01"
    assert post["changes_system"] is False


def test_body_vao_nguyen_ven(manifest: dict):
    body = (FIXTURES / "post-001-vi-du" / "body.html").read_text(encoding="utf-8")
    assert manifest["bodies"]["post-001-vi-du"] == body


def test_tao_ca_thu_muc_khi_chua_co(tmp_path: Path):
    """content/ nằm trong .gitignore: bản clone mới không có sẵn thư mục này."""
    out = tmp_path / "content" / "manifest.json"
    assert build_manifest.main(["--posts", str(FIXTURES), "--out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["posts"]


def test_kho_rong_van_dung_duoc_manifest(tmp_path: Path):
    out = tmp_path / "manifest.json"
    assert build_manifest.main(["--posts", str(tmp_path / "trong"), "--out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8")) == {"posts": [], "bodies": {}}


# Renderer truy cập metadata bằng `post.<field>` / `item.<field>`. Quét thẳng mã
# nguồn rẻ hơn nhiều so với phát hiện thiếu trường lúc deploy.
PROPERTY_RE = re.compile(r"\b(?:post|item)\.([a-z_]+)\b")
NON_META = frozenset({"body"})  # thuộc tính không đến từ meta.json


def test_moi_truong_renderer_doc_deu_co_trong_manifest():
    sources = [ROOT / "src" / "content.js", *sorted((ROOT / "src" / "render").glob("*.js"))]
    used: set[str] = set()
    for path in sources:
        used |= set(PROPERTY_RE.findall(path.read_text(encoding="utf-8")))
    missing = sorted(used - NON_META - set(build_manifest.FIELDS))
    assert not missing, f"renderer đọc trường không có trong manifest: {missing}"


def test_bien_moi_truong_chon_thu_muc_bai(tmp_path, monkeypatch):
    """NIX_POSTS_DIR thay cho cờ --posts khi không truyền cờ vào được.

    `wrangler dev` và `wrangler deploy` tự chạy build_manifest.py qua
    build.command trong wrangler.jsonc, và không có chỗ nào truyền cờ. Trước khi
    có biến này, bước dựng của wrangler luôn đọc content/posts/ và ghi đè
    manifest mà `npm run dev:draft` vừa sinh — nên xem thử bản nháp trong trình
    duyệt luôn ra 404, dù script chạy không báo lỗi gì.
    """
    src = Path(__file__).parent / "fixtures" / "post-001-vi-du"
    posts = tmp_path / "nhap"
    (posts / src.name).mkdir(parents=True)
    for name in ("meta.json", "body.html"):
        (posts / src.name / name).write_text(
            (src / name).read_text(encoding="utf-8"), encoding="utf-8"
        )

    out = tmp_path / "manifest.json"
    monkeypatch.setenv("NIX_POSTS_DIR", str(posts))
    assert build_manifest.main(["--out", str(out)]) == 0
    assert [p["slug"] for p in json.loads(out.read_text(encoding="utf-8"))["posts"]] == [src.name]


def test_co_posts_thang_bien_moi_truong(tmp_path, monkeypatch):
    """Cờ --posts truyền tay phải thắng biến môi trường."""
    src = Path(__file__).parent / "fixtures"
    monkeypatch.setenv("NIX_POSTS_DIR", str(tmp_path / "khong-ton-tai"))
    out = tmp_path / "m.json"
    assert build_manifest.main(["--posts", str(src), "--out", str(out)]) == 0
    assert len(json.loads(out.read_text(encoding="utf-8"))["posts"]) == 3
