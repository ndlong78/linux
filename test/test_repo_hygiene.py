"""Cổng vệ sinh phải đỏ khi có file track nhầm, và đỏ cả khi không hỏi được git.

Dựng kho git thật trong tmp thay vì mock `subprocess`: thứ đang được kiểm chính
là hành vi của `git ls-files --cached --ignored`. Mock nó đi thì test chỉ khẳng
định lại giả định của chính mình rồi đo lại đúng giả định đó.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import repo_hygiene  # noqa: E402


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture()
def kho(tmp_path: Path) -> Path:
    repo = tmp_path / "kho"
    repo.mkdir()
    git(repo, "init", "-q")
    (repo / ".gitignore").write_text("rac/\n*.pyc\n", encoding="utf-8")
    (repo / "giu.txt").write_text("nội dung thật\n", encoding="utf-8")
    git(repo, "add", ".gitignore", "giu.txt")
    git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "nen")
    return repo


def test_kho_sach_thi_khong_bao_gi(kho: Path):
    assert repo_hygiene.tracked_but_ignored(kho) == []


def test_file_bi_ignore_nhung_da_track_van_bi_bat(kho: Path):
    """Đúng ca đã xảy ra hai lần: file vào index TRƯỚC, luật ignore có SAU."""
    (kho / "rac").mkdir()
    (kho / "rac" / "state.sqlite").write_text("x", encoding="utf-8")
    git(kho, "add", "-f", "rac/state.sqlite")

    assert repo_hygiene.tracked_but_ignored(kho) == ["rac/state.sqlite"]


def test_rac_chua_vao_index_thi_khong_tinh(kho: Path):
    """Rác trong thư mục làm việc là chuyện bình thường — cổng này không nói về nó."""
    (kho / "rac").mkdir()
    (kho / "rac" / "state.sqlite").write_text("x", encoding="utf-8")

    assert repo_hygiene.tracked_but_ignored(kho) == []


def test_khong_phai_kho_git_thi_dung_han(tmp_path: Path):
    """Fail closed: không hỏi được git thì phải đỏ, không được trả rỗng rồi báo sạch."""
    with pytest.raises(repo_hygiene.HygieneError):
        repo_hygiene.tracked_but_ignored(tmp_path)


def test_kho_that_hien_dang_sach():
    """Nếu test này đỏ, đừng sửa test — chạy `git rm -r --cached` cho file nó liệt kê."""
    assert repo_hygiene.tracked_but_ignored() == []
