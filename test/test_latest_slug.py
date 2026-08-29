"""Bài mới nhất ĐÃ xuất bản — đầu vào của bước kiểm tra site thật sau deploy."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import latest_slug  # noqa: E402

TZ = timezone(timedelta(hours=7))
FIXTURES = Path(__file__).parent / "fixtures"


def _post(directory: Path, slug: str, issue: int, date: str) -> None:
    d = directory / slug
    d.mkdir(parents=True)
    meta = json.loads((FIXTURES / "post-001-vi-du" / "meta.json").read_text(encoding="utf-8"))
    meta.update(slug=slug, issue=issue, date=date)
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    (d / "body.html").write_text(
        (FIXTURES / "post-001-vi-du" / "body.html").read_text(encoding="utf-8"), encoding="utf-8"
    )


def test_lay_bai_co_so_hieu_lon_nhat(tmp_path):
    _post(tmp_path, "post-001-a", 1, "2026-01-01")
    _post(tmp_path, "post-002-b", 2, "2026-01-02")
    assert latest_slug.latest_slug(tmp_path, datetime(2026, 6, 1, tzinfo=TZ)) == "post-002-b"


def test_bo_qua_bai_chua_toi_ngay(tmp_path):
    """Bài hẹn ngày mai đã nằm trong bundle nhưng URL của nó chưa tồn tại.

    Lấy nó ra để kiểm tra là tự làm đỏ một phép kiểm tra lẽ ra phải xanh —
    trang sẽ trả 404 vì router lọc bài chưa tới ngày.
    """
    _post(tmp_path, "post-001-da-len", 1, "2026-01-01")
    _post(tmp_path, "post-002-tuan-sau", 2, "2026-12-31")
    assert latest_slug.latest_slug(tmp_path, datetime(2026, 6, 1, tzinfo=TZ)) == "post-001-da-len"


def test_moc_gio_viet_nam(tmp_path):
    """Bài của ngày hôm nay lên lúc 00:00 giờ Việt Nam, không phải 00:00 UTC."""
    _post(tmp_path, "post-001-hom-nay", 1, "2026-06-01")
    truoc = datetime(2026, 5, 31, 23, 0, tzinfo=TZ)
    sau = datetime(2026, 6, 1, 0, 30, tzinfo=TZ)
    assert latest_slug.latest_slug(tmp_path, truoc) is None
    assert latest_slug.latest_slug(tmp_path, sau) == "post-001-hom-nay"


def test_khong_co_bai_nao(tmp_path):
    assert latest_slug.latest_slug(tmp_path, datetime(2026, 6, 1, tzinfo=TZ)) is None


def test_ngay_hong_van_tinh_la_da_xuat_ban(tmp_path):
    """Cùng lối xử lý với isPublished() trong src/content.js."""
    _post(tmp_path, "post-001-ngay-hong", 1, "khong-phai-ngay")
    assert latest_slug.latest_slug(tmp_path, datetime(2026, 6, 1, tzinfo=TZ)) == "post-001-ngay-hong"
