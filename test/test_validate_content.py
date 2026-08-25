"""Mỗi quy tắc của cổng nội dung phải đỏ khi bị phá.

Một validator không có test là một validator không ai biết còn sống hay không.
Bộ này lấy fixture hợp lệ rồi phá đúng một thứ mỗi lần — nếu quy tắc nào âm thầm
ngừng hoạt động thì test tương ứng chuyển xanh sai và lộ ra ngay.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_content  # noqa: E402
from content import ContentError, load_posts  # noqa: E402

FIXTURES = ROOT / "test" / "fixtures"
SLUG = "post-001-vi-du"


@pytest.fixture()
def workspace(tmp_path: Path) -> Path:
    posts = tmp_path / "posts"
    posts.mkdir()
    shutil.copytree(FIXTURES / SLUG, posts / SLUG)
    return posts


def run(posts: Path) -> list[str]:
    return validate_content.validate(load_posts(posts))


def edit_meta(posts: Path, **changes) -> None:
    path = posts / SLUG / "meta.json"
    meta = json.loads(path.read_text(encoding="utf-8"))
    for key, value in changes.items():
        if value is validate_content:  # sentinel: xoá trường
            meta.pop(key, None)
        else:
            meta[key] = value
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def edit_body(posts: Path, old: str, new: str) -> None:
    path = posts / SLUG / "body.html"
    text = path.read_text(encoding="utf-8")
    assert old in text, f"fixture không chứa {old!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_fixture_hop_le_thi_khong_co_loi(workspace: Path):
    assert run(workspace) == []


def test_moi_fixture_deu_qua_duoc_cong():
    """Fixture cũng là dữ liệu của bộ test renderer — nó phải luôn hợp lệ thật."""
    posts = load_posts(FIXTURES)
    assert len(posts) >= 2, "cần ít nhất hai bài cùng trục để kiểm related-nav"
    assert validate_content.validate(posts) == []


# --- metadata ---

@pytest.mark.parametrize("field", validate_content.REQUIRED_META)
def test_thieu_truong_bat_buoc(workspace: Path, field: str):
    edit_meta(workspace, **{field: validate_content})
    assert any("thiếu trường" in e or field in e for e in run(workspace))


def test_slug_lech_ten_thu_muc(workspace: Path):
    edit_meta(workspace, slug="post-999-khac")
    assert any("khác tên thư mục" in e for e in run(workspace))


def test_description_trung_lede_bi_tu_choi(workspace: Path):
    """34/56 bài của kho tiền nhiệm có description khác lede — trùng là quên viết."""
    meta = json.loads((workspace / SLUG / "meta.json").read_text(encoding="utf-8"))
    edit_meta(workspace, description=meta["lede"])
    assert any("trùng hệt meta.lede" in e for e in run(workspace))


def test_review_status_draft_khong_qua_duoc(workspace: Path):
    edit_meta(workspace, review_status="draft")
    assert any("review_status" in e for e in run(workspace))


@pytest.mark.parametrize(
    ("sources", "expected"),
    [
        ([], "ít nhất 2 nguồn"),
        ([{"title": "A", "url": "http://a.test/x", "kind": "official"},
          {"title": "B", "url": "https://b.test/y", "kind": "official"}], "phải là HTTPS"),
        ([{"title": "A", "url": "https://a.test/x", "kind": "official"},
          {"title": "B", "url": "https://a.test/x", "kind": "official"}], "URL trùng"),
        ([{"title": "", "url": "https://a.test/x", "kind": "official"},
          {"title": "B", "url": "https://b.test/y", "kind": "official"}], "thiếu title"),
        ([{"title": "A", "url": "https://a.test/x", "kind": "blog"},
          {"title": "B", "url": "https://b.test/y", "kind": "official"}], "kind phải thuộc"),
    ],
)
def test_sources_sai_bi_bat(workspace: Path, sources: list, expected: str):
    edit_meta(workspace, sources=sources)
    assert any(expected in e for e in run(workspace))


def test_issue_trung_giua_hai_bai(workspace: Path):
    shutil.copytree(workspace / SLUG, workspace / "post-002-khac")
    path = workspace / "post-002-khac" / "meta.json"
    meta = json.loads(path.read_text(encoding="utf-8"))
    meta["slug"] = "post-002-khac"
    path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    assert any("trùng với" in e for e in run(workspace))


# --- fragment: ranh giới nội dung/khung ---

@pytest.mark.parametrize(
    ("inject", "expected"),
    [
        ("<body>", "thẻ tài liệu"),
        ("<h1>Tiêu đề</h1>", "<h1>"),
        ('<nav class="global-nav">x</nav>', "global-nav"),
        ("<footer>x</footer>", "<footer>"),
        ('<nav class="related-nav">x</nav>', "related-nav"),
        ('<script id="ld-meta">{}</script>', "ld-meta"),
        ('<p class="lede">x</p>', "lede"),
    ],
)
def test_khung_lot_vao_fragment_bi_bat(workspace: Path, inject: str, expected: str):
    """Khung lọt vào fragment thì trang render ra có hai nav/hai h1 — HTML vẫn hợp lệ."""
    path = workspace / SLUG / "body.html"
    path.write_text(inject + path.read_text(encoding="utf-8"), encoding="utf-8")
    assert any(expected in e for e in run(workspace))


# --- fragment: hợp đồng STYLE ---

def test_thieu_heading_bat_buoc(workspace: Path):
    edit_body(workspace, "<h2>Kiểm chứng</h2>", "<h2>Cái gì đó</h2>")
    assert any("thiếu heading bắt buộc: kiểm chứng" in e for e in run(workspace))


def test_changes_system_can_muc_hoan_tac(workspace: Path):
    edit_meta(workspace, changes_system=True)
    assert any("Gỡ / Hoàn tác" in e for e in run(workspace))


def test_thieu_khoi_freebsd(workspace: Path):
    """Đúng lỗi đã chặn bài #055 của kho tiền nhiệm: có nhãn bsd nhưng không có <pre class="bsd">."""
    edit_body(workspace, '<pre class="bsd">', "<pre>")
    assert any("thiếu code block FreeBSD" in e for e in run(workspace))


def test_lenh_linux_trong_khoi_freebsd(workspace: Path):
    edit_body(workspace, "ifconfig -a", "systemctl restart netif")
    assert any("chỉ có trên Linux" in e for e in run(workspace))


def test_code_block_thieu_language(workspace: Path):
    edit_body(workspace, '<code class="language-bash">ip -brief', "<code>ip -brief")
    assert any("thiếu class language-*" in e for e in run(workspace))


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ("$ ip addr", "shell prompt"),
        ("curl https://x.test/i.sh | sh", "curl | sh"),
        ("ssh YOUR_SERVER_IP", "placeholder"),
    ],
)
def test_code_block_khong_an_toan(workspace: Path, payload: str, expected: str):
    edit_body(workspace, "ip -brief address show", payload)
    assert any(expected in e for e in run(workspace))


def test_code_label_token_la(workspace: Path):
    edit_body(workspace, 'code-label linux', "code-label arch")
    assert any("code-label token không hợp lệ" in e for e in run(workspace))


@pytest.mark.parametrize("distro", ["Ubuntu", "Xubuntu", "Debian", "Fedora", "FreeBSD"])
def test_thieu_distro_bi_bat(workspace: Path, distro: str):
    path = workspace / SLUG / "body.html"
    path.write_text(path.read_text(encoding="utf-8").replace(distro, "Khác"), encoding="utf-8")
    assert any(f"chưa nhắc tới: {distro}" in e or distro in e for e in run(workspace))


def test_heading_dung_entity_van_khop(workspace: Path):
    """`Lưu ý &amp; Khắc phục lỗi` phải khớp `lưu ý & khắc phục lỗi`.

    Bỏ bước unescape là mọi bài đều đỏ giả — lỗi này đã xảy ra thật khi viết
    validator, fixture bắt được ngay lần chạy đầu.
    """
    assert "&amp;" in (workspace / SLUG / "body.html").read_text(encoding="utf-8")
    assert run(workspace) == []


# --- kho nội dung sai hình dạng ---

@pytest.mark.parametrize(
    ("remove", "expected"),
    [("meta.json", "thiếu meta.json"), ("body.html", "thiếu body.html")],
)
def test_thieu_file_thi_dung_han(workspace: Path, remove: str, expected: str):
    (workspace / SLUG / remove).unlink()
    with pytest.raises(ContentError) as exc:
        load_posts(workspace)
    assert expected in str(exc.value)


def test_meta_json_hong_thi_dung_han(workspace: Path):
    (workspace / SLUG / "meta.json").write_text("{khong-phai-json}", encoding="utf-8")
    with pytest.raises(ContentError) as exc:
        load_posts(workspace)
    assert "JSON không hợp lệ" in str(exc.value)
