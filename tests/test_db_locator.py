from __future__ import annotations

import sqlite3
from pathlib import Path

from src.services import db_locator


def _init_web_db(path: Path, beliefs: int, constraints: int, bridges: int, explains: int, contradicts: int) -> None:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE beliefs (belief_id TEXT, web_id TEXT)"
    )
    cur.execute(
        "CREATE TABLE constraints (constraint_id TEXT, web_id TEXT, constraint_type TEXT)"
    )
    cur.execute(
        "CREATE TABLE bridges (bridge_id TEXT, web_id TEXT)"
    )
    for i in range(beliefs):
        cur.execute("INSERT INTO beliefs VALUES (?, ?)", (f"b{i}", db_locator.MASTER_WEB_ID))
    for i in range(explains):
        cur.execute(
            "INSERT INTO constraints VALUES (?, ?, ?)",
            (f"ce{i}", db_locator.MASTER_WEB_ID, "explains"),
        )
    for i in range(contradicts):
        cur.execute(
            "INSERT INTO constraints VALUES (?, ?, ?)",
            (f"cc{i}", db_locator.MASTER_WEB_ID, "contradicts"),
        )
    remaining = max(0, constraints - explains - contradicts)
    for i in range(remaining):
        cur.execute(
            "INSERT INTO constraints VALUES (?, ?, ?)",
            (f"cs{i}", db_locator.MASTER_WEB_ID, "supports"),
        )
    for i in range(bridges):
        cur.execute("INSERT INTO bridges VALUES (?, ?)", (f"br{i}", db_locator.MASTER_WEB_ID))
    conn.commit()
    conn.close()


def _init_af_db(path: Path, papers: int) -> None:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE papers (paper_id TEXT)")
    for i in range(papers):
        cur.execute("INSERT INTO papers VALUES (?)", (f"p{i}",))
    conn.commit()
    conn.close()


def test_resolve_web_db_prefers_integrated_profile(monkeypatch, tmp_path: Path) -> None:
    legacy = tmp_path / "legacy.db"
    v2 = tmp_path / "v2.db"
    _init_web_db(legacy, beliefs=1000, constraints=5000, bridges=500, explains=200, contradicts=80)
    _init_web_db(v2, beliefs=300, constraints=7000, bridges=0, explains=0, contradicts=0)

    monkeypatch.setattr(db_locator, "candidate_web_dbs", lambda explicit=None: [legacy, v2])
    resolved = db_locator.resolve_web_db(prefer="integrated")
    assert resolved == legacy


def test_resolve_web_db_prefers_latest_when_requested(monkeypatch, tmp_path: Path) -> None:
    older = tmp_path / "older.db"
    newer = tmp_path / "newer.db"
    _init_web_db(older, beliefs=100, constraints=100, bridges=10, explains=5, contradicts=1)
    _init_web_db(newer, beliefs=50, constraints=50, bridges=0, explains=0, contradicts=0)
    newer.touch()

    monkeypatch.setattr(db_locator, "candidate_web_dbs", lambda explicit=None: [older, newer])
    resolved = db_locator.resolve_web_db(prefer="latest")
    assert resolved == newer


def test_resolve_article_finder_db_prefers_larger_papers(monkeypatch, tmp_path: Path) -> None:
    small = tmp_path / "small_af.db"
    big = tmp_path / "big_af.db"
    _init_af_db(small, papers=10)
    _init_af_db(big, papers=200)

    monkeypatch.setattr(db_locator, "candidate_article_finder_dbs", lambda explicit=None: [small, big])
    assert db_locator.resolve_article_finder_db() == big

