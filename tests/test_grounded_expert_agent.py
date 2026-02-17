import json
import sqlite3
from pathlib import Path

import src.services.grounded_expert_agent as gea
from src.services.grounded_expert_agent import GroundedExpertAgent


def _write_template(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _create_web_db(path: Path) -> None:
    with sqlite3.connect(str(path)) as conn:
        conn.execute(
            """
            CREATE TABLE beliefs (
                belief_id TEXT PRIMARY KEY,
                web_id TEXT NOT NULL,
                content TEXT NOT NULL,
                level TEXT NOT NULL,
                status TEXT NOT NULL,
                credence_value REAL NOT NULL,
                paper_ids TEXT,
                environment_id TEXT,
                outcome_id TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO beliefs (
                belief_id, web_id, content, level, status, credence_value,
                paper_ids, environment_id, outcome_id, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "belief:empirical:1",
                "master:web:accumulated",
                "Higher daylight exposure improved sustained attention in classroom tasks.",
                "empirical",
                "established",
                0.83,
                json.dumps(["paper:daylight:001"]),
                "env.daylight",
                "out.attention",
                "2026-02-17T00:00:00Z",
            ),
        )
        conn.commit()


def test_recursive_chain_resolves_template_id_aliases(tmp_path):
    templates_dir = tmp_path / "templates"
    panels_dir = tmp_path / "panels"
    templates_dir.mkdir()
    panels_dir.mkdir()

    _write_template(
        templates_dir / "A1.json",
        {
            "display_id": "A1",
            "template_id": "TEMP_A",
            "name": "High ceilings and creativity",
            "short_description": "Higher ceilings can improve creative thinking.",
            "structural_pattern": "ceiling_height -> creativity",
            "interactions": [{"template_id": "TEMP_B"}],
            "maturity": "supported",
        },
    )
    _write_template(
        templates_dir / "B1.json",
        {
            "display_id": "B1",
            "template_id": "TEMP_B",
            "name": "Broadened attentional scope",
            "short_description": "Reduced enclosure threat broadens attention.",
            "structural_pattern": "enclosure_threat -> attentional_scope",
            "interactions": [],
            "maturity": "supported",
        },
    )

    agent = GroundedExpertAgent(
        panels_dir=str(panels_dir),
        templates_dir=str(templates_dir),
    )
    explanation = agent.ask_deeper(
        "Why do high ceilings increase creativity?",
        max_depth=2,
        verbose=False,
    )

    assert explanation.chain[0] == "A1"
    assert "B1" in explanation.chain


def test_claim_confidence_uses_overall_maturity(tmp_path):
    templates_dir = tmp_path / "templates"
    panels_dir = tmp_path / "panels"
    templates_dir.mkdir()
    panels_dir.mkdir()

    _write_template(
        templates_dir / "L3.json",
        {
            "display_id": "L3",
            "template_id": "DAYLIGHT_MULTICHANNEL_001",
            "name": "Daylight multichannel convergence",
            "short_description": "Daylight exposure improves attention under specific conditions.",
            "structural_pattern": "daylight -> attention",
            "overall_maturity": "supported_preliminary",
            "interactions": [],
        },
    )

    agent = GroundedExpertAgent(
        panels_dir=str(panels_dir),
        templates_dir=str(templates_dir),
    )
    response = agent.ask("How does daylight affect attention?", verbose=False)

    assert response.grounded_claims
    assert response.grounded_claims[0].confidence == "moderate"
    assert "supported_preliminary" in " ".join(response.grounded_claims[0].caveats)


def test_ask_includes_empirical_web_evidence_layer(tmp_path):
    templates_dir = tmp_path / "templates"
    panels_dir = tmp_path / "panels"
    db_path = tmp_path / "web_persistence.db"
    templates_dir.mkdir()
    panels_dir.mkdir()
    _create_web_db(db_path)

    agent = GroundedExpertAgent(
        panels_dir=str(panels_dir),
        templates_dir=str(templates_dir),
        web_db_path=str(db_path),
        web_id="master:web:accumulated",
    )
    response = agent.ask("Does daylight improve attention?", verbose=False)

    assert "empirical claim(s)" in response.source_summary
    assert any(c.claim.startswith("Empirical findings") for c in response.grounded_claims)
    assert any(
        src.source_type == "empirical"
        for claim in response.grounded_claims
        for src in claim.sources
    )


def test_bn_calibration_layer_uses_edge_posteriors(tmp_path, monkeypatch):
    templates_dir = tmp_path / "templates"
    panels_dir = tmp_path / "panels"
    db_path = tmp_path / "web_persistence.db"
    templates_dir.mkdir()
    panels_dir.mkdir()
    _create_web_db(db_path)

    monkeypatch.setattr(
        gea,
        "get_edge_estimate",
        lambda source, target: 0.77 if (source, target) == ("env.daylight", "out.attention") else None,
    )

    agent = GroundedExpertAgent(
        panels_dir=str(panels_dir),
        templates_dir=str(templates_dir),
        web_db_path=str(db_path),
        web_id="master:web:accumulated",
    )
    response = agent.ask("Does daylight improve attention?", verbose=False)

    assert response.bn_calibration is not None
    assert response.bn_calibration["status"] == "calibrated"
    assert response.bn_calibration["n_edges_calibrated"] == 1
    assert response.bn_calibration["mean_posterior"] == 0.77
    assert "BN calibration" in response.confidence_statement
