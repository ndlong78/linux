#!/usr/bin/env python3
"""Kho không được track file mà chính nó đã bảo là bỏ qua.

`.gitignore` chỉ ngăn file MỚI bị thêm; nó không gỡ file đã nằm trong index. Nên
một file lọt vào trước khi có luật ignore sẽ ở lại vĩnh viễn, trong khi
`git status` sạch trơn — không còn dấu hiệu nào để ai nhận ra.

Kho này đã dính đúng vậy hai lần:

  content/manifest.json          artifact dẫn xuất, commit rồi mới thêm luật
  .wrangler/state/** (9 file)    sqlite state của `wrangler dev`
  tools|tests/__pycache__ (2)    bytecode, một cái của test đã bị xoá

Lần nào cũng lọt vì `.gitignore` trông đã đúng. Cả 11 file nay đã được gỡ; cổng
này để không có lần thứ ba.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HygieneError(RuntimeError):
    """Không hỏi được git — nói rõ nguyên nhân thay vì coi như kho sạch."""


def tracked_but_ignored(root: Path | None = None) -> list[str]:
    """File vừa nằm trong index vừa khớp luật ignore.

    Hỏi thẳng git thay vì tự đọc `.gitignore` rồi so khớp lại: bản tự parse sẽ
    lệch với git ở negation (`!`), luật theo thư mục, và `core.excludesFile`
    toàn cục — mà lệch ở đây nghĩa là cổng báo nhầm hoặc bỏ sót.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--ignored", "--exclude-standard", "-z"],
            cwd=root or ROOT, capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        # Fail closed. Nuốt lỗi rồi trả danh sách rỗng là biến cổng thành
        # "luôn xanh" ở đúng lúc nó không chạy được.
        raise HygieneError(f"không hỏi được git trong {root or ROOT}: {exc}") from exc
    return [path for path in result.stdout.split("\0") if path]


def main(argv=None) -> int:
    try:
        offenders = tracked_but_ignored()
    except HygieneError as exc:
        print(f"✗ Vệ sinh kho: {exc}", file=sys.stderr)
        return 1

    if offenders:
        print(
            f"✗ Vệ sinh kho: {len(offenders)} file đang được track dù .gitignore đã loại:",
            file=sys.stderr,
        )
        for path in offenders:
            print(f"  - {path}", file=sys.stderr)
        print(
            "  Gỡ khỏi index nhưng giữ file trên đĩa: git rm -r --cached <đường dẫn>",
            file=sys.stderr,
        )
        return 1

    print("✓ Vệ sinh kho: không có file track nhầm.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
