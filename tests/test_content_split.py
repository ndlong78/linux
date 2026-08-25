"""Bất biến của phép tách nội dung/khung.

Phép tách này là nền của toàn bộ kiến trúc dynamic: renderer sinh khung, git giữ
nội dung. Nếu nó cắt sai một bài thì nội dung mất đi âm thầm — không gate nào
phía sau bắt được, vì bài "vẫn render ra HTML hợp lệ".
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import content_split  # noqa: E402

FIXTURE = """<!doctype html>
<html lang="vi"><head>
<script type="application/json" id="ld-meta">
{"issue": 42, "title": "T"}
</script>
</head>
<body class="post"><main><div class="wrap">
<nav class="global-nav">khung</nav>
<header class="post"><h1>T</h1></header>
<section><p>thân bài</p></section>
<!-- related-nav:start -->
<nav class="related-nav">khung</nav>
<!-- related-nav:end -->
<footer>khung</footer>
</div></main></body></html>
"""


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "post-042-x.html"
    path.write_text(text, encoding="utf-8")
    return path


def test_split_keeps_only_the_body_and_round_trips(tmp_path: Path):
    item = content_split.split_post(_write(tmp_path, FIXTURE))

    assert item.content.startswith('<header class="post">')
    assert "<section><p>thân bài</p></section>" in item.content
    # Khung không được lọt vào nội dung.
    assert "global-nav" not in item.content
    assert "related-nav" not in item.content
    assert "<footer>" not in item.content
    assert item.meta["issue"] == 42
    assert item.reassemble() == FIXTURE


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda t: t.replace('<header class="post">', "<header>"), "không tìm thấy"),
        (lambda t: t.replace("<!-- related-nav:start -->", ""), "không tìm thấy"),
        (
            lambda t: t.replace('<header class="post">', '<header class="post">', 1)
            + '<header class="post">',
            "nhiều hơn một",
        ),
        (lambda t: t.replace('id="ld-meta">', 'id="other">'), "thiếu khối ld-meta"),
        (lambda t: t.replace('{"issue": 42, "title": "T"}', "{khong-phai-json}"), "không phải JSON"),
    ],
)
def test_malformed_post_is_refused_not_guessed(tmp_path: Path, mutate, expected: str):
    """Bài lệch khuôn phải làm script dừng, không được cắt bừa rồi đi tiếp."""
    with pytest.raises(content_split.SplitError) as exc:
        content_split.split_post(_write(tmp_path, mutate(FIXTURE)))
    assert expected in str(exc.value)


def test_audit_reports_round_trip_mismatch_instead_of_silently_passing(tmp_path: Path, monkeypatch):
    """Nếu ghép lại không ra byte gốc, audit phải coi đó là lỗi.

    Đây là lớp chắn cuối: dù split_post có bug gì thì bất biến byte-exact vẫn
    phải được kiểm lại trên từng bài thật.
    """
    path = _write(tmp_path, FIXTURE)
    monkeypatch.setattr(
        content_split.Split, "reassemble", lambda self: self.prefix + self.suffix
    )
    splits, errors = content_split.audit([path])

    assert splits == []
    assert errors and "không khớp byte gốc" in errors[0]
