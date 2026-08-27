#!/usr/bin/env python3
"""Dựng khung một bài mới trong content/drafts/.

Khung này qua được `npm run gate:draft` ngay khi vừa sinh ra. Đó là chủ đích:
lần chạy cổng đầu tiên của bạn phải xanh, để mọi lần đỏ sau đó đều là một điều
bạn vừa làm — chứ không phải mười lỗi có sẵn từ trước mà bạn phải lội qua.

Đổi lại, mọi chỗ cần bạn viết đều mang chữ TODO. Chúng nằm trong bản nháp, và
`review_status: "draft"` giữ bài ngoài production cho tới khi bạn tự tay đổi.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

from content import POSTS_DIR, load_posts
from validate_content import CURRICULUM, PLATFORMS

ROOT = Path(__file__).resolve().parents[1]
DRAFTS_DIR = ROOT / "content" / "drafts"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

FREEBSD_STEP = """<p class="code-label bsd"><span class="dot"></span>FreeBSD</p>
<p class="run-context" data-run-as="user"><strong>Run as:</strong> user</p>
<pre class="bsd"><code class="language-bash">uname -srm</code></pre>
"""

BODY = """<section class="objective"><h2>Mục tiêu</h2>
<p>TODO: sau bài này người đọc làm được gì. Một đoạn, nói thẳng.</p>
</section>

<section class="prerequisites"><h2>Yêu cầu tiên quyết</h2>
<ul>
<li>TODO: cần gì trước khi bắt đầu.</li>
<li>Chạy được trên Ubuntu, Xubuntu, Debian, Fedora{freebsd_prereq}.</li>
</ul>
</section>

<section><h2>Các bước thực hiện</h2>
<ol class="steps">
<li>
<p><strong>TODO: tên bước.</strong> TODO: vì sao bước này tồn tại.</p>
<p class="code-label linux"><span class="dot"></span>Linux</p>
<p class="run-context" data-run-as="user"><strong>Run as:</strong> user</p>
<pre><code class="language-bash">uname -srm</code></pre>
{freebsd_step}</li>
</ol>
</section>

<section><h2>Kiểm chứng</h2>
<p><strong>Expected Output:</strong> TODO: dán output thật, đừng viết lại từ trí nhớ.</p>
<pre><code class="language-text">TODO</code></pre>
</section>

<section><h2>Lưu ý &amp; Khắc phục lỗi</h2>
<p><strong>TODO: triệu chứng.</strong> TODO: nguyên nhân và cách xử lý.</p>
</section>
{undo}
<section class="exercise"><h2>Bài tập tự luyện</h2>
<ol><li>TODO.</li></ol>
</section>
"""

UNDO = """
<section><h2>Gỡ / Hoàn tác</h2>
<p class="code-label linux"><span class="dot"></span>Linux</p>
<p class="run-context" data-run-as="sudo"><strong>Run as:</strong> sudo</p>
<pre><code class="language-bash">TODO</code></pre>
</section>
"""


def next_issue(drafts: Path | None = None) -> int:
    """Số hiệu kế tiếp, tính trên cả bài đã đăng lẫn bài còn nháp.

    `drafts` phải đi theo cờ --drafts. Bỏ tham số này và luôn đọc DRAFTS_DIR thì
    một lần chạy trỏ vào thư mục nháp khác vẫn đánh số theo thư mục mặc định —
    và hai bản nháp trong cùng thư mục đó lĩnh cùng một số hiệu, lỗi chỉ lộ ra
    ở cổng nội dung với thông báo "issue trùng".
    """
    issues = [
        post.meta.get("issue", 0)
        for directory in (POSTS_DIR, drafts or DRAFTS_DIR)
        for post in load_posts(directory)
        if isinstance(post.meta.get("issue"), int)
    ]
    return max(issues, default=0) + 1


def build_meta(
    slug: str,
    issue: int,
    level: int,
    axis: str,
    scope: str,
    changes_system: bool,
    publish_on: date,
) -> dict:
    meta = {
        "issue": issue,
        # Ngày lên, theo 00:00 giờ Việt Nam. Ngày tương lai là hợp lệ và có
        # nghĩa: bài nằm trong bundle nhưng chưa được trả ra cho tới ngày đó.
        "date": publish_on.isoformat(),
        "level": level,
        "axis": axis,
        "slug": slug,
        "eyebrow": f"{CURRICULUM[level]['vi']} · {axis}",
        "title": "TODO: tiêu đề, tối đa 52 ký tự",
        "lede": "TODO: câu dẫn — một hai câu nói vì sao bài này đáng đọc.",
        "description": "TODO: SEO copy riêng, tối đa 160 ký tự và phải khác lede.",
        "review_status": "draft",
        # Nêu sẵn phiên bản mục tiêu để tác giả biết cần chạy ở đâu — nhưng vẫn
        # là TODO, vì trường này ghi nơi đã chạy THẬT chứ không phải nơi định chạy.
        "tested_on": [
            "TODO — thay bằng hệ đã chạy thật. Mục tiêu của series: "
            + ", ".join(f"{p['name']} {p['version']}" for p in PLATFORMS)
        ],
        # Ngày kiểm, không phải ngày lên: bài viết hôm nay cho tuần sau vẫn được
        # kiểm hôm nay.
        "last_verified": date.today().isoformat(),
        "changes_system": changes_system,
        "sources": [
            {
                "title": "TODO: tên trang nguồn",
                "url": "https://man7.org/linux/man-pages/man1/uname.1.html",
                "kind": "official",
            },
            {
                "title": "TODO: nguồn thứ hai",
                "url": "https://docs.freebsd.org/en/books/handbook/basics/",
                "kind": "upstream",
            },
        ],
    }
    if scope != "cross-platform":
        # Chỉ ghi ra khi khác mặc định: vắng trường này nghĩa là bài bị kiểm theo
        # luật chặt nhất, và đó là thứ nên xảy ra khi không ai nghĩ tới nó.
        meta["scope"] = scope
    return meta


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Thư mục bài, dạng post-002-ten-bai")
    parser.add_argument(
        "--level", type=int, default=1, choices=sorted(CURRICULUM), help="Cấp trong lộ trình"
    )
    parser.add_argument("--axis", default=None, help="Nhánh trong cấp đó (xem curriculum.json)")
    parser.add_argument("--issue", type=int, default=None, help="Mặc định: số hiệu lớn nhất + 1")
    parser.add_argument(
        "--scope",
        choices=("cross-platform", "linux-only"),
        default="cross-platform",
        help="linux-only cho chủ đề không có đối ứng FreeBSD",
    )
    parser.add_argument(
        "--changes-system",
        action="store_true",
        help="Bài có sửa hệ thống — thêm sẵn mục Gỡ / Hoàn tác mà cổng nội dung sẽ đòi",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Ngày lên (YYYY-MM-DD), mặc định hôm nay. Ngày tương lai = bài tự lên đúng ngày đó.",
    )
    parser.add_argument("--drafts", default=str(DRAFTS_DIR))
    args = parser.parse_args(argv)

    try:
        publish_on = date.fromisoformat(args.date) if args.date else date.today()
    except ValueError:
        print(f"✗ --date phải là YYYY-MM-DD: {args.date!r}", file=sys.stderr)
        return 1

    axes = sorted(CURRICULUM[args.level]["axes"])
    if args.axis is None:
        print(f"✗ thiếu --axis. Nhánh của cấp {args.level}: {axes}", file=sys.stderr)
        return 1
    if args.axis not in axes:
        print(
            f"✗ '{args.axis}' không phải nhánh của cấp {args.level} "
            f"({CURRICULUM[args.level]['name']}). Hợp lệ: {axes}",
            file=sys.stderr,
        )
        return 1

    if not SLUG_RE.match(args.slug):
        print(f"✗ slug phải là chữ thường và gạch nối: {args.slug!r}", file=sys.stderr)
        return 1

    directory = Path(args.drafts) / args.slug
    if directory.exists():
        print(f"✗ {directory} đã tồn tại — không ghi đè", file=sys.stderr)
        return 1

    linux_only = args.scope == "linux-only"
    # Số hiệu phải tính TRƯỚC khi tạo thư mục. next_issue() quét content/drafts/,
    # và một thư mục vừa mkdir còn rỗng sẽ làm load_posts() dừng vì thiếu
    # meta.json — tức là công cụ tự làm hỏng đầu vào của chính nó, rồi bỏ lại
    # một thư mục rỗng khiến lần chạy sau báo "đã tồn tại".
    issue = args.issue or next_issue(Path(args.drafts))

    directory.mkdir(parents=True)
    (directory / "meta.json").write_text(
        json.dumps(
            build_meta(
                args.slug,
                issue,
                args.level,
                args.axis,
                args.scope,
                args.changes_system,
                publish_on,
            ),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (directory / "body.html").write_text(
        BODY.format(
            freebsd_prereq="" if linux_only else " và FreeBSD",
            freebsd_step="" if linux_only else FREEBSD_STEP,
            undo=UNDO if args.changes_system else "",
        ),
        encoding="utf-8",
    )

    print(f"✓ {directory}")
    print("  Sửa hai file rồi chạy: npm run gate:draft && npm run dev:draft")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
