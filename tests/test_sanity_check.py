from __future__ import annotations

from pathlib import Path

from scripts.sanity_check import _load_todo_allowlist


def test_load_todo_allowlist_handles_comments_and_blank_lines(tmp_path: Path) -> None:
    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_text(
        "# comment line\n\nsrc/services/a.py\n  src/services/b.py  \n# trailing\n",
        encoding="utf-8",
    )
    assert _load_todo_allowlist(allowlist) == {"src/services/a.py", "src/services/b.py"}


def test_load_todo_allowlist_missing_file_returns_empty(tmp_path: Path) -> None:
    missing = tmp_path / "missing.txt"
    assert _load_todo_allowlist(missing) == set()

