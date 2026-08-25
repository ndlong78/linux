"""Bộ test cho check_links chạy hoàn toàn offline.

Một công cụ kiểm mạng mà bộ test của nó cũng cần mạng thì không ai chạy được nó
trong CI, và nó sẽ đỏ vì lý do chẳng liên quan gì tới link. Toàn bộ phần đáng
test ở đây — phân loại status, chờ lại khi 429, mã thoát — đều là hàm thuần nhận
một fetcher, nên test chỉ việc đưa vào một fetcher giả.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_links  # noqa: E402
from check_links import Outcome, Response  # noqa: E402

FIXTURES = ROOT / "test" / "fixtures"
SLUG = "post-001-vi-du"


class FakeFetch:
    """Trả lời theo kịch bản dựng sẵn và ghi lại từng lần được gọi."""

    def __init__(self, script: dict[str, list[Response]] | Response):
        self.script = script
        self.calls: list[tuple[str, str]] = []

    def __call__(self, url: str, method: str) -> Response:
        self.calls.append((url, method))
        if isinstance(self.script, Response):
            return self.script
        queue = self.script[url]
        return queue.pop(0) if len(queue) > 1 else queue[0]


# --- phân loại: một status code, một kết luận ---

@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (Response(200), Outcome.OK),
        (Response(204), Outcome.OK),
        (Response(302, "https://x.test/tam"), Outcome.OK),
        (Response(301, "https://x.test/moi"), Outcome.MOVED),
        (Response(308, "https://x.test/moi"), Outcome.MOVED),
        (Response(404), Outcome.DEAD),
        (Response(410), Outcome.DEAD),
        (Response(429), Outcome.RATE_LIMITED),
        (Response(403), Outcome.UNREACHABLE),
        (Response(500), Outcome.UNREACHABLE),
        (Response(-1, error="timed out"), Outcome.UNREACHABLE),
    ],
)
def test_phan_loai(response: Response, expected: Outcome):
    assert check_links.classify(response)[0] is expected


def test_429_khong_bi_coi_la_chet():
    """Lý do công cụ này được tách khỏi cổng nội dung: 429 khác 404."""
    assert check_links.classify(Response(429))[0] is not Outcome.DEAD
    assert check_links.classify(Response(404))[0] is Outcome.DEAD


def test_301_phai_sua_du_link_van_mo_duoc():
    """URL còn chạy hôm nay nhờ redirect, và hỏng vào ngày người ta gỡ redirect."""
    outcome, detail = check_links.classify(Response(301, "https://x.test/moi"))
    assert outcome is Outcome.MOVED
    assert "https://x.test/moi" in detail


# --- chờ lại khi bị rate limit ---

def test_429_roi_200_thi_ket_luan_la_song():
    fetch = FakeFetch({"https://x.test/a": [Response(429, retry_after="1"), Response(200)]})
    slept: list[float] = []
    result = check_links.check_url("https://x.test/a", fetch, retries=2, sleep=slept.append)
    assert result.outcome is Outcome.OK
    assert slept == [1.0], "phải tôn trọng Retry-After của server"


def test_429_mai_thi_bao_khong_ket_luan_duoc():
    fetch = FakeFetch(Response(429))
    result = check_links.check_url("https://x.test/a", fetch, retries=2, sleep=lambda _: None)
    assert result.outcome is Outcome.RATE_LIMITED
    assert len([c for c in fetch.calls if c[1] == "HEAD"]) == 3


def test_retry_after_vo_nghia_thi_lui_theo_cap_so_nhan():
    fetch = FakeFetch(Response(429, retry_after="lúc nào đó"))
    slept: list[float] = []
    check_links.check_url("https://x.test/a", fetch, retries=2, sleep=slept.append)
    assert slept == [1.0, 2.0]


def test_retry_after_khong_cho_qua_tran():
    delay = check_links._retry_delay(Response(429, retry_after="999999"), 0)
    assert delay == check_links.MAX_BACKOFF


# --- HEAD không phải lúc nào cũng được nhận ---

@pytest.mark.parametrize("status", [403, 405, 501])
def test_head_bi_tu_choi_thi_thu_lai_bang_get(status: int):
    fetch = FakeFetch({"https://x.test/a": [Response(status), Response(200)]})
    result = check_links.check_url("https://x.test/a", fetch, retries=0, sleep=lambda _: None)
    assert result.outcome is Outcome.OK
    assert [method for _, method in fetch.calls] == ["HEAD", "GET"]


# --- gom URL từ kho nội dung ---

def test_gom_ca_nguon_lan_link_trong_than_bai(tmp_path: Path):
    posts = tmp_path / "posts"
    posts.mkdir()
    shutil.copytree(FIXTURES / SLUG, posts / SLUG)
    body = posts / SLUG / "body.html"
    body.write_text(
        body.read_text(encoding="utf-8")
        + '<p><a href="https://than-bai.test/x?a=1&amp;b=2">x</a></p>',
        encoding="utf-8",
    )

    from content import load_posts

    found = check_links.collect_urls(load_posts(posts))
    assert "https://man7.org/linux/man-pages/man8/ip.8.html" in found
    # `&amp;` trong HTML phải được giải mã trước khi gọi, nếu không mọi URL có
    # query string đều bị hỏi sai địa chỉ.
    assert "https://than-bai.test/x?a=1&b=2" in found
    assert found["https://than-bai.test/x?a=1&b=2"] == [f"{SLUG} thân bài"]


def test_mot_url_bi_nhieu_bai_trich_dan_chi_goi_mot_lan(tmp_path: Path):
    posts = tmp_path / "posts"
    posts.mkdir()
    for slug in (SLUG, "post-002-vi-du"):
        shutil.copytree(FIXTURES / SLUG, posts / slug)
        meta = posts / slug / "meta.json"
        data = json.loads(meta.read_text(encoding="utf-8"))
        data["slug"] = slug
        meta.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    from content import load_posts

    found = check_links.collect_urls(load_posts(posts))
    shared = found["https://man7.org/linux/man-pages/man8/ip.8.html"]
    assert len(shared) == 2, "phải nhớ đủ mọi chỗ trích dẫn"
    assert len(found) == 2, "nhưng chỉ còn hai URL để gọi mạng"


# --- mã thoát: sai khác không biết ---

def run_main(response_by_url, *extra: str):
    fetch = FakeFetch(response_by_url)
    return check_links.main(
        ["--posts", str(FIXTURES), "--retries", "0", *extra], fetch=fetch, sleep=lambda _: None
    )


def test_moi_url_song_thi_thoat_0():
    assert run_main(Response(200)) == 0


def test_co_url_chet_thi_thoat_1():
    assert run_main(Response(404)) == 1


def test_chi_toan_429_thi_thoat_2_chu_khong_phai_1():
    """Mã thoát phải phân biệt 'link của bạn sai' với 'tôi không kiểm được'."""
    assert run_main(Response(429)) == 2


def test_khong_toi_duoc_cung_la_2():
    assert run_main(Response(-1, error="Name or service not known")) == 2


# --- gắn vào gate: gate phải chạy được ở máy không có mạng ---

def test_allow_unknown_khong_chan_merge_khi_chua_kiem_duoc():
    """Container không egress vẫn phải chạy được gate — không kiểm được ≠ sai."""
    assert run_main(Response(429), "--allow-unknown") == 0
    assert run_main(Response(-1, error="mất mạng"), "--allow-unknown") == 0


def test_allow_unknown_van_chan_link_chet():
    """Cờ này nới đúng một thứ: nó không biến 404 thành chuyện nhỏ."""
    assert run_main(Response(404), "--allow-unknown") == 1
    assert run_main(Response(301, "https://x.test/moi"), "--allow-unknown") == 1


def test_allow_unknown_bao_to_chu_khong_im_lang(capsys):
    run_main(Response(429), "--allow-unknown")
    assert "chưa kiểm được" in capsys.readouterr().err


# --- cache: hỏi lại cái cần hỏi, bỏ qua cái vừa hỏi ---

# Sau `last_verified` của fixture (2026-09-01 và 2026-09-02): một lần kiểm diễn
# ra trước ngày bài được rà lại thì đằng nào cũng phải hỏi lại, nên lấy mốc đó
# làm "hôm nay" thì mọi test dưới đây mới nói đúng thứ nó định nói.
TODAY = date(2026, 9, 10)


def stamp(days_ago: int) -> str:
    return (TODAY - timedelta(days=days_ago)).isoformat()


def entry(days_ago: int) -> dict:
    return {"checked_at": stamp(days_ago), "status": "ok"}


def test_cache_con_han_thi_bo_qua():
    assert check_links.is_fresh(entry(1), today=TODAY, max_age_days=14, last_verified=stamp(30))


def test_cache_qua_han_thi_hoi_lai():
    """Link chết mà không ai đụng vào bài thì vẫn phải bị phát hiện."""
    assert not check_links.is_fresh(
        entry(15), today=TODAY, max_age_days=14, last_verified=stamp(30)
    )


def test_last_verified_moi_hon_lan_kiem_thi_hoi_lai():
    """Đẩy last_verified lên nghĩa là tác giả vừa rà lại bài — nguồn phải hỏi lại."""
    assert not check_links.is_fresh(entry(3), today=TODAY, max_age_days=14, last_verified=stamp(2))
    assert check_links.is_fresh(entry(3), today=TODAY, max_age_days=14, last_verified=stamp(4))


@pytest.mark.parametrize(
    "entry", [None, {}, {"checked_at": "hôm qua"}, {"checked_at": "2027-12-31"}]
)
def test_cache_hong_hoac_o_tuong_lai_thi_khong_tin(entry):
    assert not check_links.is_fresh(entry, today=TODAY, max_age_days=14, last_verified="")


def test_lan_hai_khong_goi_mang_nua(tmp_path: Path):
    cache = tmp_path / "cache.json"
    fetch = FakeFetch(Response(200))
    args = ["--posts", str(FIXTURES), "--retries", "0", "--cache", str(cache)]

    assert check_links.main(args, fetch=fetch, sleep=lambda _: None, today=TODAY) == 0
    goi_lan_dau = len(fetch.calls)
    assert goi_lan_dau > 0

    fetch_lan_hai = FakeFetch(Response(200))
    assert check_links.main(args, fetch=fetch_lan_hai, sleep=lambda _: None, today=TODAY) == 0
    assert fetch_lan_hai.calls == [], "lần hai phải lấy hết từ cache"


def test_no_cache_thi_hoi_lai_bang_het(tmp_path: Path):
    cache = tmp_path / "cache.json"
    args = ["--posts", str(FIXTURES), "--retries", "0", "--cache", str(cache)]
    check_links.main(args, fetch=FakeFetch(Response(200)), sleep=lambda _: None, today=TODAY)

    fetch = FakeFetch(Response(200))
    check_links.main(
        [*args, "--no-cache"], fetch=fetch, sleep=lambda _: None, today=TODAY
    )
    assert fetch.calls, "--no-cache phải bỏ qua cache"


def test_khong_bao_gio_cache_mot_that_bai(tmp_path: Path):
    """Cache một 404 là để nó tự khỏi sau vài ngày — đúng thứ công cụ này chặn."""
    cache = tmp_path / "cache.json"
    args = ["--posts", str(FIXTURES), "--retries", "0", "--cache", str(cache)]

    assert check_links.main(args, fetch=FakeFetch(Response(404)), sleep=lambda _: None, today=TODAY) == 1
    assert check_links.load_cache(cache) == {}

    fetch = FakeFetch(Response(404))
    assert check_links.main(args, fetch=fetch, sleep=lambda _: None, today=TODAY) == 1
    assert fetch.calls, "vẫn phải hỏi lại, không được im lặng nhờ cache"


def test_429_cung_khong_duoc_cache(tmp_path: Path):
    cache = tmp_path / "cache.json"
    args = ["--posts", str(FIXTURES), "--retries", "0", "--cache", str(cache)]
    check_links.main(args, fetch=FakeFetch(Response(429)), sleep=lambda _: None, today=TODAY)
    assert check_links.load_cache(cache) == {}


def test_url_khong_con_duoc_trich_dan_thi_roi_khoi_cache(tmp_path: Path):
    cache = tmp_path / "cache.json"
    check_links.save_cache(cache, {"https://khong-ai-dung.test/x": entry(0)})
    args = ["--posts", str(FIXTURES), "--retries", "0", "--cache", str(cache)]
    check_links.main(args, fetch=FakeFetch(Response(200)), sleep=lambda _: None, today=TODAY)
    assert "https://khong-ai-dung.test/x" not in check_links.load_cache(cache)


def test_cache_hong_thi_coi_nhu_khong_co(tmp_path: Path):
    cache = tmp_path / "cache.json"
    cache.write_text("{khong-phai-json}", encoding="utf-8")
    assert check_links.load_cache(cache) == {}


def test_cache_khac_version_thi_bo(tmp_path: Path):
    cache = tmp_path / "cache.json"
    cache.write_text(json.dumps({"version": 999, "urls": {"a": {}}}), encoding="utf-8")
    assert check_links.load_cache(cache) == {}


def test_latest_verified_lay_ngay_moi_nhat(tmp_path: Path):
    posts = tmp_path / "posts"
    posts.mkdir()
    for slug, stamp in (("post-001-vi-du", "2026-01-01"), ("post-002-khac", "2026-07-07")):
        shutil.copytree(FIXTURES / "post-001-vi-du", posts / slug)
        meta = posts / slug / "meta.json"
        data = json.loads(meta.read_text(encoding="utf-8"))
        data["slug"], data["last_verified"] = slug, stamp
        meta.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    from content import load_posts

    newest = check_links.latest_verified(load_posts(posts))
    assert newest["https://man7.org/linux/man-pages/man8/ip.8.html"] == "2026-07-07"
