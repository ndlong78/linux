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


def test_tieu_de_qua_dai_bi_bat(workspace: Path):
    """Quá ngưỡng một ký tự cũng đỏ — ngưỡng mềm là ngưỡng không ai giữ."""
    edit_meta(workspace, title="X" * (validate_content.TITLE_MAX + 1))
    assert any("meta.title dài" in e for e in run(workspace))


def test_tieu_de_dung_bang_nguong_van_qua(workspace: Path):
    edit_meta(workspace, title="X" * validate_content.TITLE_MAX)
    assert run(workspace) == []


def test_description_qua_dai_bi_bat(workspace: Path):
    edit_meta(workspace, description="X" * (validate_content.DESCRIPTION_MAX + 1))
    assert any("meta.description dài" in e for e in run(workspace))


def test_description_dung_bang_nguong_van_qua(workspace: Path):
    edit_meta(workspace, description="X" * validate_content.DESCRIPTION_MAX)
    assert run(workspace) == []


def test_tested_on_go_sai_ten_he_bi_bat(workspace: Path):
    """Bắt lỗi gõ sai và bắt trường bị điền cho có."""
    edit_meta(workspace, tested_on=["Ubunut 26.04"])
    assert any("không nhắc tới hệ nào" in e for e in run(workspace))


def test_tested_on_chi_can_mot_he_trong_ma_tran(workspace: Path):
    """Chạy được trên đâu thì ghi đúng chỗ đó — không đòi phải đủ mọi hệ."""
    edit_meta(workspace, tested_on=["Ubuntu 26.04 LTS"])
    assert run(workspace) == []


def test_ma_tran_nen_tang_doc_tu_file(workspace: Path):
    """content/platforms.json là bản duy nhất của danh sách hệ, không chép vào code."""
    names = set(validate_content.DISTRO_PATTERNS)
    assert names == {p["name"] for p in validate_content.PLATFORMS}
    assert "Ubuntu" in names and "FreeBSD" in names


def test_review_status_draft_khong_qua_duoc(workspace: Path):
    edit_meta(workspace, review_status="draft")
    assert any("review_status" in e for e in run(workspace))


def test_che_do_nhap_nhan_draft_nhung_khong_nhan_gi_khac(workspace: Path):
    """`--allow-draft` chỉ nới đúng một quy tắc, không nới bộ quy tắc."""
    edit_meta(workspace, review_status="draft")
    assert validate_content.validate(load_posts(workspace), allow_draft=True) == []

    edit_meta(workspace, review_status="dang-viet")
    assert any(
        "review_status" in e
        for e in validate_content.validate(load_posts(workspace), allow_draft=True)
    )


def test_che_do_nhap_van_bat_moi_loi_con_lai(workspace: Path):
    """Bài nháp sai heading vẫn phải đỏ — biết lúc còn nháp rẻ hơn biết lúc merge."""
    edit_meta(workspace, review_status="draft")
    edit_body(workspace, "<h2>Kiểm chứng</h2>", "<h2>Cái gì đó</h2>")
    assert any(
        "thiếu heading bắt buộc" in e
        for e in validate_content.validate(load_posts(workspace), allow_draft=True)
    )


def test_ban_nhap_dang_co_qua_duoc_cong_nhap():
    """Bài trong content/drafts/ phải luôn hợp lệ, chỉ thiếu mỗi chữ ký review."""
    drafts = load_posts(ROOT / "content" / "drafts")
    if not drafts:
        pytest.skip("chưa có bản nháp nào")
    assert validate_content.validate(drafts, allow_draft=True) == []


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


# --- scope: chủ đề không có đối ứng FreeBSD ---

LINUX_ONLY = "post-003-linux-only"


@pytest.fixture()
def linux_only(tmp_path: Path) -> Path:
    posts = tmp_path / "posts"
    posts.mkdir()
    shutil.copytree(FIXTURES / LINUX_ONLY, posts / LINUX_ONLY)
    return posts


def edit(posts: Path, slug: str, **changes) -> None:
    path = posts / slug / "meta.json"
    meta = json.loads(path.read_text(encoding="utf-8"))
    meta.update(changes)
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def test_linux_only_khong_can_khoi_freebsd(linux_only: Path):
    assert run(linux_only) == []


def test_vang_scope_thi_van_bi_kiem_theo_luat_chat(linux_only: Path):
    """Bỏ sót khai báo không bao giờ được trở thành cách lách."""
    path = linux_only / LINUX_ONLY / "meta.json"
    meta = json.loads(path.read_text(encoding="utf-8"))
    del meta["scope"]
    path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    errors = run(linux_only)
    assert any("thiếu code block FreeBSD" in e for e in errors)
    assert any("chưa nhắc tới: FreeBSD" in e or "FreeBSD" in e for e in errors)


def test_scope_la_bi_tu_choi(linux_only: Path):
    edit(linux_only, LINUX_ONLY, scope="chi-freebsd")
    assert any("meta.scope phải thuộc" in e for e in run(linux_only))


def test_linux_only_ma_van_co_khoi_bsd_la_mau_thuan(linux_only: Path):
    """Khai báo phải đúng cả hai chiều, nếu không không ai biết bên nào sai."""
    path = linux_only / LINUX_ONLY / "body.html"
    path.write_text(
        path.read_text(encoding="utf-8")
        + '<pre class="bsd"><code class="language-bash">ifconfig -a</code></pre>',
        encoding="utf-8",
    )
    assert any("vẫn có <pre class=\"bsd\">" in e for e in run(linux_only))


def test_linux_only_ma_van_co_nhan_bsd_la_mau_thuan(linux_only: Path):
    path = linux_only / LINUX_ONLY / "body.html"
    path.write_text(
        path.read_text(encoding="utf-8") + '<p class="code-label bsd">FreeBSD</p>',
        encoding="utf-8",
    )
    assert any("nhãn code-label bsd" in e for e in run(linux_only))


@pytest.mark.parametrize("distro", ["Ubuntu", "Xubuntu", "Debian", "Fedora"])
def test_linux_only_van_phai_du_bon_distro_linux(linux_only: Path, distro: str):
    """Nới đúng hai quy tắc FreeBSD, không nới gì khác."""
    path = linux_only / LINUX_ONLY / "body.html"
    path.write_text(path.read_text(encoding="utf-8").replace(distro, "Khác"), encoding="utf-8")
    assert any(f"chưa nhắc tới: {distro}" in e for e in run(linux_only))


def test_linux_only_van_phai_du_heading(linux_only: Path):
    path = linux_only / LINUX_ONLY / "body.html"
    path.write_text(
        path.read_text(encoding="utf-8").replace("<h2>Kiểm chứng</h2>", "<h2>Gì đó</h2>"),
        encoding="utf-8",
    )
    assert any("thiếu heading bắt buộc" in e for e in run(linux_only))


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
