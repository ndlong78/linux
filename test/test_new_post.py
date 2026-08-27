"""Khung bài mới phải qua được cổng nội dung ngay lúc vừa sinh ra.

Đây là test quan trọng nhất của file này, và nó có tác dụng theo cả chiều ngược
lại: thêm một quy tắc vào validator mà quên cập nhật khung thì test này đỏ —
chứ không phải người viết bài tiếp theo phát hiện hộ.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import new_post  # noqa: E402
import validate_content  # noqa: E402
from content import load_posts  # noqa: E402


def make(tmp_path: Path, *args: str) -> Path:
    drafts = tmp_path / "drafts"
    base = ["post-042-thu-nghiem", "--issue", "42", "--drafts", str(drafts)]
    if "--axis" not in args:
        base += ["--level", "1", "--axis", "Tập tin"]
    assert new_post.main([*base, *args]) == 0
    return drafts


@pytest.mark.parametrize(
    "args",
    [
        (),
        ("--scope", "linux-only"),
        ("--changes-system",),
        ("--scope", "linux-only", "--changes-system"),
    ],
    ids=["mặc-định", "linux-only", "đổi-hệ-thống", "cả-hai"],
)
def test_khung_moi_qua_duoc_cong_ngay(tmp_path: Path, args: tuple[str, ...]):
    drafts = make(tmp_path, *args)
    assert validate_content.validate(load_posts(drafts), allow_draft=True) == []


def test_khung_mac_dinh_khong_qua_duoc_cong_that(tmp_path: Path):
    """Vẫn là bản nháp: nó không được tự lọt vào production."""
    drafts = make(tmp_path)
    assert any("review_status" in e for e in validate_content.validate(load_posts(drafts)))


def test_vang_scope_khi_la_cross_platform(tmp_path: Path):
    """Mặc định không ghi trường scope ra — luật chặt nhất là thứ nên xảy ra khi không ai nghĩ tới."""
    meta = json.loads((make(tmp_path) / "post-042-thu-nghiem" / "meta.json").read_text(encoding="utf-8"))
    assert "scope" not in meta


def test_linux_only_ghi_scope_va_bo_khoi_bsd(tmp_path: Path):
    drafts = make(tmp_path, "--scope", "linux-only")
    meta = json.loads((drafts / "post-042-thu-nghiem" / "meta.json").read_text(encoding="utf-8"))
    body = (drafts / "post-042-thu-nghiem" / "body.html").read_text(encoding="utf-8")
    assert meta["scope"] == "linux-only"
    assert "bsd" not in body
    assert "FreeBSD" not in body


def test_changes_system_kem_san_muc_hoan_tac(tmp_path: Path):
    body = (make(tmp_path, "--changes-system") / "post-042-thu-nghiem" / "body.html").read_text(
        encoding="utf-8"
    )
    assert "Gỡ / Hoàn tác" in body


def test_moi_cho_can_viet_deu_mang_chu_todo(tmp_path: Path):
    directory = make(tmp_path) / "post-042-thu-nghiem"
    assert "TODO" in (directory / "body.html").read_text(encoding="utf-8")
    meta = json.loads((directory / "meta.json").read_text(encoding="utf-8"))
    assert meta["tested_on"] and "TODO" in meta["tested_on"][0]


def test_khong_ghi_de_thu_muc_da_co(tmp_path: Path):
    drafts = make(tmp_path)
    truoc = (drafts / "post-042-thu-nghiem" / "meta.json").read_text(encoding="utf-8")
    assert new_post.main(["post-042-thu-nghiem", "--drafts", str(drafts)]) == 1
    assert (drafts / "post-042-thu-nghiem" / "meta.json").read_text(encoding="utf-8") == truoc


@pytest.mark.parametrize("slug", ["Post-001", "post 001", "post_001", "post-001-", ""])
def test_slug_sai_dinh_dang_bi_tu_choi(tmp_path: Path, slug: str):
    assert new_post.main([slug, "--drafts", str(tmp_path / "drafts")]) == 1


def test_so_hieu_ke_tiep_tinh_ca_bai_dang_va_bai_nhap(tmp_path: Path, monkeypatch):
    posts, drafts = tmp_path / "posts", tmp_path / "drafts"
    for directory, issue in ((posts, 7), (drafts, 12)):
        import shutil

        shutil.copytree(ROOT / "test" / "fixtures" / "post-001-vi-du", directory / "bai")
        meta = directory / "bai" / "meta.json"
        data = json.loads(meta.read_text(encoding="utf-8"))
        data["issue"], data["slug"] = issue, "bai"
        meta.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(new_post, "POSTS_DIR", posts)
    monkeypatch.setattr(new_post, "DRAFTS_DIR", drafts)
    assert new_post.next_issue() == 13


# --- lên lịch ---

def test_dat_duoc_ngay_len(tmp_path: Path):
    """Ngày tương lai là hợp lệ: bài nằm trong bundle nhưng chưa được trả ra."""
    drafts = make(tmp_path, "--date", "2099-01-31")
    meta = json.loads((drafts / "post-042-thu-nghiem" / "meta.json").read_text(encoding="utf-8"))
    assert meta["date"] == "2099-01-31"
    # last_verified là ngày kiểm, không phải ngày lên.
    assert meta["last_verified"] != meta["date"]
    assert validate_content.validate(load_posts(drafts), allow_draft=True) == []


def test_ngay_sai_dinh_dang_bi_tu_choi(tmp_path: Path):
    assert new_post.main(["post-042-x", "--date", "31/01/2099", "--drafts", str(tmp_path)]) == 1
    assert not (tmp_path / "post-042-x").exists()


# --- lộ trình 4 cấp ---

def test_thieu_axis_thi_tu_choi_va_liet_ke_nhanh_hop_le(tmp_path: Path, capsys):
    """Người viết không phải mở curriculum.json mới biết cấp đó có nhánh nào."""
    assert new_post.main(["post-042-x", "--level", "2", "--drafts", str(tmp_path)]) == 1
    err = capsys.readouterr().err
    assert "Lưu trữ" in err and "systemd" in err


def test_axis_khong_thuoc_cap_thi_tu_choi(tmp_path: Path, capsys):
    """Nhánh có thật nhưng sai cấp cũng là sai — lộ trình mới là thứ quyết định."""
    code = new_post.main(
        ["post-042-x", "--level", "2", "--axis", "Tập tin", "--drafts", str(tmp_path)]
    )
    assert code == 1
    assert "không phải nhánh của cấp 2" in capsys.readouterr().err
    assert not (tmp_path / "post-042-x").exists()


def test_eyebrow_sinh_tu_cap_va_nhanh(tmp_path: Path):
    drafts = make(tmp_path, "--level", "3", "--axis", "Hiệu năng")
    meta = json.loads((drafts / "post-042-thu-nghiem" / "meta.json").read_text(encoding="utf-8"))
    assert meta["level"] == 3
    assert meta["axis"] == "Hiệu năng"
    assert meta["eyebrow"] == "Quản trị cấp cao · Hiệu năng"


def test_tu_danh_so_khi_drafts_da_co_bai(tmp_path, monkeypatch):
    """Số hiệu phải được tính trước khi tạo thư mục.

    Lỗi thật đã gặp: main() gọi mkdir rồi mới gọi next_issue(), mà next_issue()
    quét chính thư mục drafts đó — thư mục vừa tạo còn rỗng nên load_posts()
    dừng vì thiếu meta.json. Công cụ chết, và để lại một thư mục rỗng khiến lần
    chạy sau báo "đã tồn tại". Không cờ --issue thì lần nào cũng vỡ, tức là lịch
    soạn nháp tự động không bao giờ chạy được.
    """
    drafts = tmp_path / "drafts"
    assert (
        new_post.main([
            "post-002-bai-dau", "--level", "1", "--axis", "Tập tin",
            "--drafts", str(drafts),
        ])
        == 0
    )
    # Lần thứ hai là lần từng vỡ: giờ drafts/ đã có một bài để quét qua.
    assert (
        new_post.main([
            "post-003-bai-sau", "--level", "1", "--axis", "Tập tin",
            "--drafts", str(drafts),
        ])
        == 0
    )
    second = json.loads((drafts / "post-003-bai-sau" / "meta.json").read_text(encoding="utf-8"))
    first = json.loads((drafts / "post-002-bai-dau" / "meta.json").read_text(encoding="utf-8"))
    assert second["issue"] == first["issue"] + 1
