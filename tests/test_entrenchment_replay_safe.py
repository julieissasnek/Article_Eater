"""
Tests for ENT-6 safe replay DB strategy and runner.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.services.entrenchment_replay import ScholarlyReplayService
from src.services.web_of_belief import (
    Belief,
    BeliefStatus,
    Constraint,
    ConstraintType,
    Credence,
    EpistemicLevel,
    WebOfBelief,
)
from src.services.web_persistence import WebPersistenceService


def _seed_source_db(db_path: Path) -> None:
    persistence = WebPersistenceService(str(db_path))

    web = WebOfBelief()
    web.add_belief(
        Belief(
            belief_id="belief:alpha:1",
            content="Natural light improves alertness",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.7, 0.1),
            paper_ids=["paper:alpha"],
        )
    )
    web.add_belief(
        Belief(
            belief_id="belief:alpha:2",
            content="Daylight supports circadian alignment",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.ESTABLISHED,
            credence=Credence(0.72, 0.1),
            paper_ids=["paper:alpha"],
        )
    )
    web.add_constraint(
        Constraint(
            constraint_id="constraint:alpha:1",
            source_id="belief:alpha:1",
            target_id="belief:alpha:2",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.6,
        )
    )

    master_id = persistence.create_web("master:web:test", "Master", is_master=True)
    persistence.save_web(web, master_id)
    persistence.upsert_paper_publication(
        paper_id="paper:alpha",
        publication_year=2001,
        publication_date="2001-01-01",
        source="test",
    )


def test_with_safe_replay_copy_creates_distinct_db(tmp_path: Path) -> None:
    source_db = tmp_path / "source.db"
    _seed_source_db(source_db)

    service = ScholarlyReplayService.with_safe_replay_copy(
        source_db_path=str(source_db),
        copy_dir=str(tmp_path / "replay"),
    )

    assert Path(service.replay_db_path).exists()
    assert Path(service.replay_db_path).resolve() != source_db.resolve()
    assert service._same_db is False


def test_master_filtered_loader_returns_paper_scoped_web(tmp_path: Path) -> None:
    source_db = tmp_path / "source.db"
    _seed_source_db(source_db)

    service = ScholarlyReplayService(
        source_db_path=str(source_db),
        replay_db_path=str(tmp_path / "replay.db"),
    )
    loader = service.make_master_filtered_loader()

    paper_web = loader("paper:alpha")
    assert paper_web is not None
    assert len(paper_web.beliefs) == 2
    assert len(paper_web.constraints) == 1
    assert loader("paper:missing") is None


def test_safe_runner_script_executes_on_copied_db(tmp_path: Path) -> None:
    source_db = tmp_path / "source.db"
    _seed_source_db(source_db)
    out_json = tmp_path / "replay_summary.json"

    cmd = [
        sys.executable,
        "scripts/run_entrenchment_replay_safe.py",
        "--source-db",
        str(source_db),
        "--copy-dir",
        str(tmp_path / "copies"),
        "--output-json",
        str(out_json),
        "--limit",
        "1",
    ]
    proc = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    summary = payload["summary"]
    assert summary["safe_mode"] is True
    assert Path(summary["source_db"]).resolve() == source_db.resolve()
    assert Path(summary["replay_db"]).exists()
    assert Path(summary["replay_db"]).resolve() != source_db.resolve()
    assert summary["reports_count"] == 1
