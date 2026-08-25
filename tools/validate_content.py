#!/usr/bin/env python3
"""Cổng nội dung: kiểm metadata và fragment trước khi bài được merge.

Đây là lớp duy nhất đứng giữa "agent viết ra một thứ trông hợp lý" và production.
Ở repo tiền nhiệm, chính lớp này bắt được: lede lệch metadata, tiêu đề nguồn lệch
`sources`, thiếu khối FreeBSD, và nguồn trỏ tới URL không tồn tại. Mỗi lần nó bắt
được là một ngày không phải đăng bài sai.

Kiểm offline. Kiểm URL sống hay chết là việc của `check_links.py` — tách ra vì
nó cần mạng và vì 429 phải xử lý khác 404.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

from content import ContentError, Post, load_posts

REQUIRED_META = (
    "issue", "date", "axis", "slug", "eyebrow", "title", "lede", "description",
    "review_status", "tested_on", "last_verified", "changes_system", "sources",
)
REQUIRED_HEADINGS = (
    "mục tiêu", "yêu cầu tiên quyết", "các bước thực hiện",
    "kiểm chứng", "lưu ý & khắc phục lỗi", "bài tập",
)
CODE_LABEL_TOKENS = frozenset({"bsd", "ubuntu", "debian", "fedora", "linux", "same"})
SOURCE_KINDS = frozenset({"official", "upstream"})
REVIEW_STATUSES = ("draft", "reviewed")

# Trang kết quả tìm kiếm cắt tiêu đề quanh mốc 60 ký tự, và renderer nối thêm
# tiền tố số hiệu `#001 · ` (7 ký tự) vào trước meta.title — xem src/render/post.js.
# 52 + 7 = 59, vừa đủ nằm dưới mốc đó. Phần bị cắt luôn là phần đuôi, tức là phần
# tác giả viết cẩn thận nhất.
TITLE_PREFIX_LEN = len("#001 · ")
TITLE_RENDERED_MAX = 60
TITLE_MAX = TITLE_RENDERED_MAX - TITLE_PREFIX_LEN - 1
DISTRO_PATTERNS = {
    "Ubuntu": r"\bUbuntu\b",
    "Xubuntu": r"\bXubuntu\b",
    "Debian": r"\bDebian\b",
    "Fedora": r"\bFedora\b",
    "FreeBSD": r"\bFreeBSD\b",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEADING_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.IGNORECASE | re.DOTALL)
PRE_RE = re.compile(r"<pre(?P<attrs>[^>]*)>(?P<body>.*?)</pre>", re.IGNORECASE | re.DOTALL)
CLASS_RE = re.compile(r'class=["\'](?P<value>[^"\']*)["\']', re.IGNORECASE)
CODE_LABEL_RE = re.compile(r'class=["\'][^"\']*\bcode-label\s+([a-z0-9_-]+)', re.IGNORECASE)
LANGUAGE_RE = re.compile(r'class=["\'][^"\']*\blanguage-[a-z0-9_-]+\b', re.IGNORECASE)
RUN_AS_RE = re.compile(r'data-run-as=["\'](?:user|sudo|root)["\']', re.IGNORECASE)
PROMPT_RE = re.compile(r"^\s*[$#]\s+\S", re.MULTILINE)
CURL_PIPE_SHELL_RE = re.compile(r"curl\b[^\n|]*\|\s*(?:sudo\s+)?(?:ba)?sh\b", re.IGNORECASE)
LEGACY_PLACEHOLDER_RE = re.compile(r"\bYOUR_[A-Z0-9_]+\b|\[username\]|\[server-ip\]", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")

# Fragment là THÂN bài. Khung do renderer sinh; nếu khung lọt vào fragment thì
# trang render ra sẽ có hai nav, hai footer, hoặc hai <h1> — và không gate nào
# khác bắt được vì HTML vẫn hợp lệ.
FORBIDDEN_IN_BODY = (
    (re.compile(r"<html\b|<head\b|<body\b", re.IGNORECASE), "thẻ tài liệu (html/head/body)"),
    (re.compile(r"<h1\b", re.IGNORECASE), "<h1> — tiêu đề do renderer sinh từ meta.title"),
    (re.compile(r'class=["\'][^"\']*\bglobal-nav\b', re.IGNORECASE), "global-nav"),
    (re.compile(r"<footer\b", re.IGNORECASE), "<footer>"),
    (re.compile(r'class=["\'][^"\']*\brelated-nav\b', re.IGNORECASE), "related-nav"),
    (re.compile(r'id=["\']ld-meta["\']', re.IGNORECASE), "khối ld-meta — metadata nằm ở meta.json"),
    (re.compile(r'class=["\'][^"\']*\blede\b', re.IGNORECASE), "lede — renderer sinh từ meta.lede"),
)

# Lệnh chỉ có trên Linux, không được xuất hiện trong khối đánh dấu FreeBSD.
LINUX_ONLY_RE = re.compile(
    r"^\s*(?:sudo\s+)?(?:apt|apt-get|dnf|yum|systemctl|journalctl|timedatectl|ufw|firewall-cmd|nmcli|netplan)\b"
)


def _visible_text(markup: str) -> str:
    """Text người đọc thấy: bỏ thẻ và giải mã entity.

    Bỏ qua bước unescape là so `Lưu ý &amp; Khắc phục lỗi` với `lưu ý & khắc phục
    lỗi` và không bao giờ khớp — heading đó viết bằng `&amp;` ở mọi bài.
    """
    return html.unescape(TAG_RE.sub(" ", markup))


def _check_meta(post: Post, errors: list[str], allow_draft: bool) -> None:
    say = lambda msg: errors.append(f"{post.slug}: {msg}")  # noqa: E731
    meta = post.meta

    for field in REQUIRED_META:
        if field not in meta:
            say(f"meta thiếu trường `{field}`")

    if meta.get("slug") != post.slug:
        say(f"meta.slug ('{meta.get('slug')}') khác tên thư mục")
    if not isinstance(meta.get("issue"), int):
        say("meta.issue phải là số nguyên")
    if not DATE_RE.match(str(meta.get("date", ""))):
        say("meta.date phải là ISO YYYY-MM-DD")
    if not DATE_RE.match(str(meta.get("last_verified", ""))):
        say("meta.last_verified phải là ISO YYYY-MM-DD")
    if not isinstance(meta.get("changes_system"), bool):
        say("meta.changes_system phải là boolean")
    if not isinstance(meta.get("tested_on"), list) or not meta.get("tested_on"):
        say("meta.tested_on phải là danh sách OS/version đã test")
    # Bản nháp được kiểm bằng đúng bộ quy tắc này, chỉ trừ một điều: nó chưa
    # tự nhận là đã review. Mọi lỗi khác vẫn phải đỏ ngay lúc còn nháp — biết
    # sớm rẻ hơn biết lúc sắp merge.
    if allow_draft:
        if meta.get("review_status") not in REVIEW_STATUSES:
            say(f"meta.review_status phải thuộc {list(REVIEW_STATUSES)}")
    elif meta.get("review_status") != "reviewed":
        say("meta.review_status phải là 'reviewed' mới được merge")

    # description tách khỏi lede là có lý do đo được: ở kho tiền nhiệm 34/56 bài
    # có description khác lede. Để chúng bằng nhau là dấu hiệu quên viết SEO copy.
    if meta.get("description") and meta.get("description") == meta.get("lede"):
        say("meta.description trùng hệt meta.lede — description là SEO copy riêng")

    title = str(meta.get("title", ""))
    if len(title) > TITLE_MAX:
        say(
            f"meta.title dài {len(title)} ký tự, tối đa {TITLE_MAX} — "
            f"<title> render ra {len(title) + TITLE_PREFIX_LEN} ký tự sẽ bị cắt"
        )

    sources = meta.get("sources")
    if not isinstance(sources, list) or len(sources) < 2:
        say("meta.sources cần ít nhất 2 nguồn official/upstream")
        return
    seen: set[str] = set()
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            say(f"sources[{index}] phải là object")
            continue
        url = str(source.get("url", ""))
        if not url.startswith("https://"):
            say(f"sources[{index}] URL phải là HTTPS: {url!r}")
        if url in seen:
            say(f"sources[{index}] URL trùng: {url}")
        seen.add(url)
        if not str(source.get("title", "")).strip():
            say(f"sources[{index}] thiếu title")
        if source.get("kind") not in SOURCE_KINDS:
            say(f"sources[{index}].kind phải thuộc {sorted(SOURCE_KINDS)}")


def _check_body(post: Post, errors: list[str]) -> None:
    say = lambda msg: errors.append(f"{post.slug}: {msg}")  # noqa: E731
    body = post.body

    for pattern, label in FORBIDDEN_IN_BODY:
        if pattern.search(body):
            say(f"fragment chứa {label} — phần khung do renderer sinh")

    headings = {_visible_text(h).strip().lower() for h in HEADING_RE.findall(body)}
    for required in REQUIRED_HEADINGS:
        if not any(required in heading for heading in headings):
            say(f"thiếu heading bắt buộc: {required}")

    if post.meta.get("changes_system") is True:
        if not any("hoàn tác" in heading or "gỡ" in heading for heading in headings):
            say("changes_system=true nhưng thiếu mục Gỡ / Hoàn tác")

    for token in CODE_LABEL_RE.findall(body):
        if token.lower() not in CODE_LABEL_TOKENS:
            say(f"code-label token không hợp lệ: {token}")

    blocks = list(PRE_RE.finditer(body))
    if not blocks:
        say("bài không có code block nào")

    freebsd_blocks = 0
    for index, block in enumerate(blocks, start=1):
        attrs, inner = block.group("attrs"), block.group("body")
        classes = CLASS_RE.search(attrs)
        is_bsd = bool(classes) and "bsd" in classes.group("value").split()
        if is_bsd:
            freebsd_blocks += 1

        if not LANGUAGE_RE.search(inner):
            say(f"code block #{index} thiếu class language-*")
        text = _visible_text(inner)
        if PROMPT_RE.search(text):
            say(f"code block #{index} chứa shell prompt $/#")
        if CURL_PIPE_SHELL_RE.search(text):
            say(f"code block #{index} chứa curl | sh chạy trực tiếp")
        if LEGACY_PLACEHOLDER_RE.search(text):
            say(f"code block #{index} dùng placeholder không theo chuẩn <...>")
        if "language-bash" in inner and not RUN_AS_RE.search(body[: block.start()][-400:]):
            say(f"code block #{index} thiếu data-run-as=user|sudo|root")
        if is_bsd:
            for line in text.splitlines():
                if LINUX_ONLY_RE.match(line):
                    say(f"khối FreeBSD #{index} dùng lệnh chỉ có trên Linux: {line.strip()[:60]}")

    # Đây là quy tắc đã chặn bài #055 của kho tiền nhiệm: bài có nhãn
    # `code-label bsd` nhưng không có <pre class="bsd"> nào. Hai chỗ khác nhau.
    if freebsd_blocks == 0:
        say('thiếu code block FreeBSD — cần ít nhất một <pre class="bsd">')

    visible = _visible_text(body)
    missing = [name for name, pattern in DISTRO_PATTERNS.items() if not re.search(pattern, visible)]
    if missing:
        say(f"thân bài chưa nhắc tới: {', '.join(missing)}")


def validate(posts: list[Post], *, allow_draft: bool = False) -> list[str]:
    errors: list[str] = []
    by_issue: dict[int, str] = {}
    for post in posts:
        _check_meta(post, errors, allow_draft)
        _check_body(post, errors)
        issue = post.meta.get("issue")
        if isinstance(issue, int):
            if issue in by_issue:
                errors.append(f"{post.slug}: issue #{issue:03d} trùng với {by_issue[issue]}")
            else:
                by_issue[issue] = post.slug
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--posts", default=None, help="Thư mục content/posts")
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="Nhận review_status='draft' — dùng để kiểm bài trong content/drafts/",
    )
    args = parser.parse_args(argv)

    try:
        posts = load_posts(Path(args.posts) if args.posts else None)
    except ContentError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    errors = validate(posts, allow_draft=args.allow_draft)
    if errors:
        print(f"✗ Cổng nội dung: {len(errors)} lỗi", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    mode = " (chế độ nháp)" if args.allow_draft else ""
    print(f"✓ Cổng nội dung{mode}: {len(posts)} bài đạt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
