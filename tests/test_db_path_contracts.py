from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = (
    REPO_ROOT / "scripts",
    REPO_ROOT / "src",
    REPO_ROOT / "app",
    REPO_ROOT / "streamlit_app",
)
SKIP_PARTS = ("archive", "_archive", "quarantine")
ABSOLUTE_DB_PATTERNS = (
    re.compile(r"/Users/davidusa/REPOS/.+article_finder\.db"),
    re.compile(r"/Users/davidusa/REPOS/.+web_persistence(?:_v2)?\.db"),
)


def _iter_candidate_files() -> list[Path]:
    files: list[Path] = []
    for base in SCAN_DIRS:
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in {".py", ".sh"}:
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if any(part in rel for part in SKIP_PARTS):
                continue
            files.append(path)
    return files


def test_no_hardcoded_absolute_web_or_af_db_paths() -> None:
    offenders: list[str] = []
    for path in _iter_candidate_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in ABSOLUTE_DB_PATTERNS:
            if pattern.search(text):
                offenders.append(f"{path.relative_to(REPO_ROOT)} :: {pattern.pattern}")
                break
    assert not offenders, "Hardcoded absolute DB paths found:\n" + "\n".join(sorted(offenders))
