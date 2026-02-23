"""Centralized DB path resolution for AE/AF runtime scripts.

This module keeps path selection deterministic and auditable:
- web DB can be resolved by policy ("integrated" vs "latest")
- article finder DB is resolved from explicit/env/candidate paths
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MASTER_WEB_ID = "master:web:accumulated"


@dataclass(frozen=True)
class WebDbProfile:
    path: Path
    beliefs: int
    constraints: int
    bridges: int
    explains: int
    contradicts: int
    mtime: float

    @property
    def integrated_score(self) -> tuple[int, int, int, int, float]:
        # Prioritize operational integrated coverage over freshness.
        return (
            int(self.beliefs),
            int(self.bridges),
            int(self.explains + self.contradicts),
            int(self.constraints),
            float(self.mtime),
        )


def _normalize_path(path: Path | str | None) -> Path | None:
    if path is None:
        return None
    p = Path(path).expanduser()
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return p


def _existing_unique(paths: Iterable[Path | str | None]) -> list[Path]:
    out: list[Path] = []
    seen: set[Path] = set()
    for raw in paths:
        p = _normalize_path(raw)
        if p is None:
            continue
        if p.exists() and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def candidate_web_dbs(explicit: Path | str | None = None) -> list[Path]:
    return _existing_unique(
        [
            explicit,
            os.getenv("AE_WEB_DB"),
            PROJECT_ROOT / "data" / "web_persistence.db",
            PROJECT_ROOT / "data" / "web_persistence_v2.db",
        ]
    )


def _count_query(cur: sqlite3.Cursor, sql: str, params: tuple = ()) -> int:
    try:
        row = cur.execute(sql, params).fetchone()
        return int(row[0]) if row else 0
    except Exception:
        return 0


def profile_web_db(path: Path) -> WebDbProfile | None:
    try:
        conn = sqlite3.connect(str(path))
        cur = conn.cursor()
        beliefs = _count_query(
            cur,
            "SELECT COUNT(*) FROM beliefs WHERE web_id = ?",
            (MASTER_WEB_ID,),
        )
        if beliefs == 0:
            beliefs = _count_query(cur, "SELECT COUNT(*) FROM beliefs")

        constraints = _count_query(
            cur,
            "SELECT COUNT(*) FROM constraints WHERE web_id = ?",
            (MASTER_WEB_ID,),
        )
        if constraints == 0:
            constraints = _count_query(cur, "SELECT COUNT(*) FROM constraints")

        bridges = _count_query(
            cur,
            "SELECT COUNT(*) FROM bridges WHERE web_id = ?",
            (MASTER_WEB_ID,),
        )
        if bridges == 0:
            bridges = _count_query(cur, "SELECT COUNT(*) FROM bridges")

        explains = _count_query(
            cur,
            "SELECT COUNT(*) FROM constraints WHERE web_id = ? AND constraint_type = 'explains'",
            (MASTER_WEB_ID,),
        )
        contradicts = _count_query(
            cur,
            "SELECT COUNT(*) FROM constraints WHERE web_id = ? AND constraint_type = 'contradicts'",
            (MASTER_WEB_ID,),
        )
        if explains == 0 and contradicts == 0:
            explains = _count_query(
                cur,
                "SELECT COUNT(*) FROM constraints WHERE constraint_type = 'explains'",
            )
            contradicts = _count_query(
                cur,
                "SELECT COUNT(*) FROM constraints WHERE constraint_type = 'contradicts'",
            )

        conn.close()
        return WebDbProfile(
            path=path,
            beliefs=beliefs,
            constraints=constraints,
            bridges=bridges,
            explains=explains,
            contradicts=contradicts,
            mtime=path.stat().st_mtime,
        )
    except Exception:
        return None


def resolve_web_db(
    explicit: Path | str | None = None,
    *,
    prefer: str = "integrated",
) -> Path:
    candidates = candidate_web_dbs(explicit)
    if not candidates:
        raise FileNotFoundError("No web DB candidates found")
    if explicit is not None:
        p = _normalize_path(explicit)
        if p is None or not p.exists():
            raise FileNotFoundError(f"Web DB not found: {explicit}")
        return p

    profiles = [p for p in (profile_web_db(path) for path in candidates) if p is not None]
    if not profiles:
        raise FileNotFoundError("No readable web DB candidates found")

    if prefer == "latest":
        return max(profiles, key=lambda item: item.mtime).path
    # Default: integrated
    return max(profiles, key=lambda item: item.integrated_score).path


def candidate_article_finder_dbs(explicit: Path | str | None = None) -> list[Path]:
    return _existing_unique(
        [
            explicit,
            os.getenv("AE_AF_DB"),
            PROJECT_ROOT.parent / "Article_Finder_v3_2_3" / "data" / "article_finder.db",
            Path.home() / "REPOS" / "Article_Finder_v3_2_3" / "data" / "article_finder.db",
            PROJECT_ROOT / "data" / "article_finder.db",
        ]
    )


def _papers_count(path: Path) -> int:
    try:
        conn = sqlite3.connect(str(path))
        cur = conn.cursor()
        count = _count_query(cur, "SELECT COUNT(*) FROM papers")
        conn.close()
        return count
    except Exception:
        return 0


def resolve_article_finder_db(explicit: Path | str | None = None) -> Path:
    candidates = candidate_article_finder_dbs(explicit)
    if explicit is not None:
        p = _normalize_path(explicit)
        if p is None or not p.exists():
            raise FileNotFoundError(f"Article Finder DB not found: {explicit}")
        return p
    if not candidates:
        raise FileNotFoundError("No article_finder.db candidates found")
    scored = [(int(_papers_count(path)), float(path.stat().st_mtime), path) for path in candidates]
    return max(scored, key=lambda item: (item[0], item[1]))[2]

