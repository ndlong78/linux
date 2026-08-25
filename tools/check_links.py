#!/usr/bin/env python3
"""Kiểm URL trong kho nội dung còn sống hay đã chết.

Tách khỏi `validate_content.py` vì hai lý do, và cả hai đều nằm trong thiết kế
của công cụ này:

1. Nó cần mạng. Cổng nội dung phải chạy được offline, trong container không có
   egress, ở máy đang mất mạng — nên nó không được phép gọi ra ngoài.
2. **429 phải xử lý khác 404.** Một link bị rate limit không phải link chết;
   coi hai thứ đó như nhau là dạy người dùng bỏ qua kết quả của công cụ.

Vì vậy công cụ này phân biệt "sai" với "không biết", và mã thoát nói rõ điều đó:

    0  mọi URL đều sống
    1  có URL chết hoặc redirect vĩnh viễn — phải sửa
    2  không có URL chết, nhưng có URL không kết luận được (429, timeout, 5xx)

CI nên coi mã 1 là đỏ. Coi mã 2 là đỏ hay không là lựa chọn của bạn — nhưng đừng
coi nó là xanh im lặng.

`--allow-unknown` biến mã 2 thành 0 và vẫn in đủ danh sách. Nó tồn tại để công cụ
này gắn được vào `npm run gate`: gate phải chạy được ở máy không có mạng, nên
"không kiểm được" không được chặn merge — nhưng "link chết" thì có.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from content import ContentError, Post, load_posts

USER_AGENT = "nix-daily-link-check/1.0 (+https://github.com/ndlong78/nix)"
HREF_RE = re.compile(r'href=["\'](https?://[^"\'\s]+)["\']', re.IGNORECASE)

# Khoảng cách tối thiểu giữa hai request tới cùng một host. Kho bài trích dẫn
# man7.org và docs.freebsd.org rất dày; bắn song song vào một host là cách nhanh
# nhất để tự chuốc lấy 429 rồi kết luận sai về chính link của mình.
HOST_INTERVAL = 1.0
MAX_BACKOFF = 60.0


class Outcome(Enum):
    OK = "ok"
    MOVED = "moved"          # redirect vĩnh viễn: URL trong kho đã cũ
    DEAD = "dead"            # 404/410 và các lỗi client khác
    RATE_LIMITED = "429"     # không kết luận được
    UNREACHABLE = "unreachable"  # 5xx, timeout, DNS — cũng không kết luận được


INCONCLUSIVE = (Outcome.RATE_LIMITED, Outcome.UNREACHABLE)
MUST_FIX = (Outcome.DEAD, Outcome.MOVED)


@dataclass(frozen=True)
class Response:
    """Chỉ những gì cần để kết luận. `status = -1` là lỗi mạng, chưa tới được HTTP."""

    status: int
    location: str | None = None
    retry_after: str | None = None
    error: str | None = None


@dataclass
class Result:
    url: str
    outcome: Outcome
    detail: str


def classify(response: Response) -> tuple[Outcome, str]:
    """Một status code → một kết luận. Đây là toàn bộ phần cần test kỹ."""
    status = response.status
    if status < 0:
        return Outcome.UNREACHABLE, response.error or "lỗi mạng"
    if 200 <= status < 300:
        return Outcome.OK, f"{status}"
    # 301/308 nghĩa là URL trong meta.json đã cũ: nó còn chạy hôm nay nhờ
    # redirect, và sẽ hỏng vào ngày người ta gỡ redirect đi. Sửa ngay.
    if status in (301, 308):
        return Outcome.MOVED, f"{status} → {response.location or '?'}"
    if 300 <= status < 400:
        return Outcome.OK, f"{status} (redirect tạm) → {response.location or '?'}"
    if status == 429:
        return Outcome.RATE_LIMITED, "429 — bị rate limit, không kết luận được"
    if status in (401, 403):
        # Nhiều site chặn client không phải trình duyệt. Link có thể vẫn sống với
        # người đọc thật, nên đây không phải bằng chứng link chết.
        return Outcome.UNREACHABLE, f"{status} — bị từ chối, cần mở bằng trình duyệt để xác nhận"
    if 400 <= status < 500:
        return Outcome.DEAD, f"{status}"
    return Outcome.UNREACHABLE, f"{status}"


def _retry_delay(response: Response, attempt: int) -> float:
    """Tôn trọng Retry-After nếu server có gửi; không thì lùi theo cấp số nhân."""
    raw = (response.retry_after or "").strip()
    if raw.isdigit():
        return min(float(raw), MAX_BACKOFF)
    if raw:
        try:
            when = parsedate_to_datetime(raw)
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            return max(0.0, min((when - datetime.now(timezone.utc)).total_seconds(), MAX_BACKOFF))
        except (TypeError, ValueError):
            pass
    return min(2.0**attempt, MAX_BACKOFF)


def check_url(url: str, fetch, *, retries: int = 2, sleep=time.sleep) -> Result:
    """HEAD trước, GET khi server không chịu HEAD, và chờ lại khi bị 429."""
    for attempt in range(retries + 1):
        response = fetch(url, "HEAD")
        # 405/501 là server không cài HEAD; 403 với HEAD nhưng mở với GET cũng
        # gặp thường xuyên. Thử lại bằng GET trước khi kết luận bất cứ điều gì.
        if response.status in (403, 405, 501):
            response = fetch(url, "GET")
        outcome, detail = classify(response)
        if outcome is not Outcome.RATE_LIMITED or attempt == retries:
            return Result(url, outcome, detail)
        sleep(_retry_delay(response, attempt))
    raise AssertionError("không tới được")  # pragma: no cover


def _urllib_fetch(url: str, method: str, timeout: float) -> Response:
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):  # noqa: D401
            return None  # tự phân loại redirect thay vì đi theo nó

    opener = urllib.request.build_opener(NoRedirect)
    request = urllib.request.Request(
        url, method=method, headers={"User-Agent": USER_AGENT, "Accept": "*/*"}
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            return Response(response.status)
    except urllib.error.HTTPError as exc:
        return Response(exc.status, exc.headers.get("Location"), exc.headers.get("Retry-After"))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        # DNS hỏng, timeout, TLS từ chối — chưa từng tới được HTTP, nên không có
        # status nào để phân loại. Đây là "không biết", không phải "link chết".
        reason = getattr(exc, "reason", exc)
        return Response(-1, error=str(reason))


def collect_urls(posts: list[Post]) -> dict[str, list[str]]:
    """URL → những chỗ nó xuất hiện. Một URL bị ba bài trích dẫn vẫn chỉ gọi mạng một lần."""
    found: dict[str, list[str]] = defaultdict(list)
    for post in posts:
        sources = post.meta.get("sources")
        if isinstance(sources, list):
            for index, source in enumerate(sources, start=1):
                if isinstance(source, dict) and isinstance(source.get("url"), str):
                    found[source["url"]].append(f"{post.slug} sources[{index}]")
        for match in HREF_RE.findall(post.body):
            found[html.unescape(match)].append(f"{post.slug} thân bài")
    return dict(found)


def _polite_fetch(timeout: float):
    """Nối tiếp theo từng host, song song giữa các host."""
    locks: dict[str, Lock] = defaultdict(Lock)
    last: dict[str, float] = {}
    guard = Lock()

    def fetch(url: str, method: str) -> Response:
        host = urllib.parse.urlparse(url).hostname or ""
        with guard:
            lock = locks[host]
        with lock:
            wait = HOST_INTERVAL - (time.monotonic() - last.get(host, -HOST_INTERVAL))
            if wait > 0:
                time.sleep(wait)
            try:
                return _urllib_fetch(url, method, timeout)
            finally:
                last[host] = time.monotonic()

    return fetch


def report(
    results: dict[str, Result], origins: dict[str, list[str]], allow_unknown: bool = False
) -> int:
    by_outcome: dict[Outcome, list[Result]] = defaultdict(list)
    for result in results.values():
        by_outcome[result.outcome].append(result)

    for outcome, label in (
        (Outcome.DEAD, "✗ Chết"),
        (Outcome.MOVED, "✗ Đã chuyển vĩnh viễn"),
        (Outcome.RATE_LIMITED, "? Bị rate limit"),
        (Outcome.UNREACHABLE, "? Không tới được"),
    ):
        for result in by_outcome.get(outcome, []):
            print(f"{label}: {result.url}", file=sys.stderr)
            print(f"    {result.detail}", file=sys.stderr)
            for origin in origins.get(result.url, []):
                print(f"    ← {origin}", file=sys.stderr)

    ok = len(by_outcome.get(Outcome.OK, []))
    must_fix = sum(len(by_outcome.get(outcome, [])) for outcome in MUST_FIX)
    unknown = sum(len(by_outcome.get(outcome, [])) for outcome in INCONCLUSIVE)
    print(f"{ok} sống · {must_fix} phải sửa · {unknown} không kết luận được")

    if must_fix:
        return 1
    if not unknown:
        return 0
    if allow_unknown:
        # Gate gọi công cụ này với cờ đó. Không kiểm được thì nói to là không
        # kiểm được, chứ không âm thầm báo xanh.
        print(
            f"⚠ {unknown} URL chưa kiểm được (mạng?). Chạy `npm run links` ở máy có mạng.",
            file=sys.stderr,
        )
        return 0
    return 2


def main(argv=None, fetch=None, sleep=time.sleep) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--posts", default=None, help="Thư mục bài (mặc định content/posts)")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--retries", type=int, default=2, help="Số lần chờ lại khi gặp 429")
    parser.add_argument("--jobs", type=int, default=4, help="Số host kiểm song song")
    parser.add_argument(
        "--allow-unknown",
        action="store_true",
        help="Mã 2 (không kết luận được) thành 0 — dùng khi gắn vào gate offline",
    )
    args = parser.parse_args(argv)

    try:
        posts = load_posts(Path(args.posts) if args.posts else None)
    except ContentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    origins = collect_urls(posts)
    if not origins:
        print("Không có URL nào để kiểm.")
        return 0

    fetch = fetch or _polite_fetch(args.timeout)
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        checked = list(
            pool.map(lambda url: check_url(url, fetch, retries=args.retries, sleep=sleep), origins)
        )
    return report({result.url: result for result in checked}, origins, args.allow_unknown)


if __name__ == "__main__":
    raise SystemExit(main())
