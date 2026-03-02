import json
from pathlib import Path
import sqlite3

from src.services.finding_template_relevance import (
    FindingRecord,
    ResolverConfig,
    load_template_profiles,
    persist_relevance_to_web_db,
    resolve_finding,
    resolve_findings,
)


def _write_template(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_load_template_profiles_supports_variable_schema(tmp_path: Path) -> None:
    _write_template(
        tmp_path / "t41.json",
        {
            "template_id": "NM_REWARD_PREDICTION_ERROR_001",
            "display_id": "T41",
            "name": "Environmental Reward Prediction Error",
            "framework_ids": ["NM", "REWARD_PROCESSING"],
            "causal_links": [
                {
                    "from_variable": "environmental_outcome",
                    "to_variable": "reward_prediction_error",
                    "activity": "compute_temporal_difference",
                    "from_level": "environmental",
                    "to_level": "subcortical",
                    "bridging_quality": "HIGH",
                    "key_evidence": "Schultz et al. 1997",
                }
            ],
        },
    )

    profiles = load_template_profiles(tmp_path)
    assert len(profiles) == 1
    profile = profiles[0]
    assert profile.display_id == "T41"
    assert "environmental_outcome" in profile.input_terms
    assert "reward_prediction_error" in profile.endpoint_terms


def test_resolve_finding_uses_bridge_terms_for_matching(tmp_path: Path) -> None:
    _write_template(
        tmp_path / "dt2.json",
        {
            "template_id": "DT_DIRECTED_ATTENTION_001",
            "display_id": "DT2",
            "name": "Directed Attention Fatigue & Restoration",
            "framework_ids": ["ATTENTION_RESTORATION"],
            "structural_pattern": "Nature exposure restores directed attention.",
            "causal_links": [
                {
                    "from_entity": "nature_scene_exposure",
                    "to_entity": "directed_attention",
                    "activity": "restores",
                    "from_level": "environmental",
                    "to_level": "cognitive",
                    "bridging_quality": "strong",
                    "evidence_base": "behavioral and neural studies",
                }
            ],
        },
    )
    profiles = load_template_profiles(tmp_path)
    finding = FindingRecord(
        belief_id="b:1",
        content="Nature view improved attention in office workers",
        environment_id="has_nature_view",
        outcome_id="attention",
        paper_ids="paper:1",
    )

    result = resolve_finding(finding, profiles, ResolverConfig(min_template_score=0.25, top_k_templates=5))
    assert result.top_templates
    assert result.top_templates[0].display_id == "DT2"
    assert result.tier1_relevance.get("ART", 0.0) > 0.0


def test_resolve_findings_summary_counts(monkeypatch, tmp_path: Path) -> None:
    _write_template(
        tmp_path / "l2.json",
        {
            "template_id": "CIRCADIAN_ARCH_REG_001",
            "display_id": "L2",
            "name": "Circadian Architectural Regulation",
            "framework_ids": ["circadian_neuroscience", "SRT"],
            "causal_links": [
                {
                    "from_entity": "light_intensity",
                    "to_entity": "circadian_alignment",
                    "activity": "entrains",
                    "from_level": "environmental",
                    "to_level": "physiological",
                    "bridging_quality": "strong",
                }
            ],
        },
    )
    profiles = load_template_profiles(tmp_path)
    findings = [
        FindingRecord(
            belief_id="b:light",
            content="Higher illuminance improved sleep quality",
            environment_id="illuminance_lux",
            outcome_id="sleep_quality",
            paper_ids="paper:2",
        )
    ]

    monkeypatch.setattr(
        "src.services.finding_template_relevance.infer_theory_relevance",
        lambda claim, outcome_lookup=None: {"SRT": 0.4},
    )

    payload = resolve_findings(findings, profiles, ResolverConfig(min_template_score=0.2, top_k_templates=3))
    summary = payload["summary"]
    assert summary["findings_total"] == 1
    assert summary["findings_with_template_candidates"] == 1
    assert summary["findings_with_tier1_relevance"] == 1
    assert summary["unique_templates_linked"] == 1


def test_low_scoring_template_does_not_propagate_tier_links(tmp_path: Path) -> None:
    _write_template(
        tmp_path / "weak.json",
        {
            "template_id": "WEAK_REL_001",
            "display_id": "WK1",
            "name": "Weak relation",
            "framework_ids": ["adaptive_thermal_comfort"],
            "causal_links": [
                {
                    "from_entity": "temperature",
                    "to_entity": "cognitive_load",
                    "activity": "modulates",
                    "from_level": "environmental",
                    "to_level": "cognitive",
                }
            ],
        },
    )
    profiles = load_template_profiles(tmp_path)
    finding = FindingRecord(
        belief_id="b:weak",
        content="Minor temperature variation potentially changed outcomes.",
        environment_id="unknown_factor",
        outcome_id="unknown_outcome",
    )
    result = resolve_finding(
        finding,
        profiles,
        ResolverConfig(min_template_score=0.1, top_k_templates=3, min_tier_support_score=0.9),
    )
    assert result.top_templates
    assert result.tier1_relevance == {}
    assert result.tier2_relevance == {}


def test_domain_guard_blocks_music_template_for_noise_finding(tmp_path: Path) -> None:
    _write_template(
        tmp_path / "music.json",
        {
            "template_id": "MUSICAL_CHILLS_001",
            "display_id": "MUS1",
            "name": "Music-Evoked Emotion Route",
            "domain": "music_emotion",
            "framework_ids": ["MUSIC_COGNITION"],
            "causal_links": [
                {
                    "from_entity": "ambient_noise_level",
                    "to_entity": "stress",
                    "activity": "modulates",
                    "from_level": "environmental",
                    "to_level": "physiological",
                }
            ],
        },
    )
    _write_template(
        tmp_path / "acoustics.json",
        {
            "template_id": "ACOUSTIC_LOAD_001",
            "display_id": "AC1",
            "name": "Acoustic Load and Stress",
            "domain_tags": ["acoustics"],
            "framework_ids": ["ACOUSTIC_COMMUNICATION"],
            "causal_links": [
                {
                    "from_entity": "ambient_noise_level",
                    "to_entity": "stress",
                    "activity": "amplifies",
                    "from_level": "environmental",
                    "to_level": "physiological",
                }
            ],
        },
    )
    profiles = load_template_profiles(tmp_path)
    finding = FindingRecord(
        belief_id="b:noise",
        content="Office background noise increased stress.",
        environment_id="ambient_noise_dba",
        outcome_id="stress",
        paper_ids="paper:noise",
    )

    result = resolve_finding(finding, profiles, ResolverConfig(min_template_score=0.2, top_k_templates=5))
    assert result.top_templates
    assert result.top_templates[0].display_id == "AC1"
    assert not any(item.display_id == "MUS1" for item in result.top_templates)


def test_resolve_finding_expands_tier1_taxonomy(tmp_path: Path) -> None:
    _write_template(
        tmp_path / "thermal.json",
        {
            "template_id": "THERMAL_ADAPTIVE_PE_001",
            "display_id": "TH1",
            "name": "Thermal Adaptation and Load",
            "framework_ids": ["adaptive_thermal_comfort", "cognitive_load_theory"],
            "causal_links": [
                {
                    "from_entity": "temperature",
                    "to_entity": "cognitive_load",
                    "activity": "increases",
                    "from_level": "environmental",
                    "to_level": "cognitive",
                }
            ],
        },
    )
    profiles = load_template_profiles(tmp_path)
    finding = FindingRecord(
        belief_id="b:thermal",
        content="Higher indoor temperature increased cognitive load in students.",
        environment_id="temperature",
        outcome_id="cognitive_load",
        paper_ids="paper:thermal",
    )
    result = resolve_finding(finding, profiles, ResolverConfig(min_template_score=0.2, top_k_templates=3))

    assert result.top_templates
    assert result.top_templates[0].display_id == "TH1"
    # Verify that thermal and cognitive load framework links are present using new hyphenated IDs
    assert result.tier1_relevance.get("interoceptive-constructionist-affect", 0.0) > 0.0
    assert result.tier1_relevance.get("dual-process-evaluation", 0.0) > 0.0


def test_framework_mapping_is_token_safe_for_art(tmp_path: Path) -> None:
    _write_template(
        tmp_path / "arch.json",
        {
            "template_id": "ARCH_NEURO_001",
            "display_id": "AN1",
            "name": "Architectural Neuroscience Stress Pathway",
            "framework_ids": ["architectural_neuroscience", "stress_physiology"],
            "causal_links": [
                {
                    "from_entity": "ceiling_height",
                    "to_entity": "stress",
                    "activity": "modulates",
                    "from_level": "environmental",
                    "to_level": "physiological",
                }
            ],
        },
    )
    profiles = load_template_profiles(tmp_path)
    finding = FindingRecord(
        belief_id="b:arch",
        content="Lower ceiling height increased stress.",
        environment_id="ceiling_height_m",
        outcome_id="stress",
        paper_ids="paper:arch",
    )
    result = resolve_finding(finding, profiles, ResolverConfig(min_template_score=0.2, top_k_templates=3))

    assert result.top_templates
    assert result.tier1_relevance.get("SRT", 0.0) > 0.0
    assert result.tier1_relevance.get("ART", 0.0) == 0.0


def test_persist_relevance_to_web_db_writes_epistemic_payload(tmp_path: Path) -> None:
    db_path = tmp_path / "web.db"
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            CREATE TABLE beliefs (
                belief_id TEXT PRIMARY KEY,
                content TEXT,
                environment_id TEXT,
                outcome_id TEXT,
                paper_ids TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute(
            """
            INSERT INTO beliefs (belief_id, content, environment_id, outcome_id, paper_ids, updated_at)
            VALUES ('b:1', 'finding text', 'ambient_noise_dba', 'attention', '', '2026-02-01T00:00:00+00:00')
            """
        )
        conn.commit()
    finally:
        conn.close()

    payload = {
        "summary": {"findings_total": 1},
        "resolutions": [
            {
                "belief_id": "b:1",
                "environment_id": "ambient_noise_dba",
                "outcome_id": "attention",
                "top_templates": [{"template_id": "T58", "display_id": "T58", "score": 0.82, "reasons": []}],
                "tier1_relevance": {"COGNITIVE_CONTROL": 0.55},
                "tier2_relevance": {"COGNITIVE_LOAD_THEORY": 0.55},
            }
        ],
    }
    summary = persist_relevance_to_web_db(db_path, payload, annotation_key="template_relevance_v1")
    assert summary == {"updated_beliefs": 1, "missing_beliefs": 0}

    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute("SELECT epistemic_v2 FROM beliefs WHERE belief_id = 'b:1'").fetchone()
        assert row is not None
        persisted = json.loads(row[0])
    finally:
        conn.close()

    annotation = persisted["template_relevance_v1"]
    assert annotation["schema_version"] == 1
    assert annotation["environment_id"] == "ambient_noise_dba"
    assert annotation["outcome_id"] == "attention"
    assert annotation["tier1_relevance"]["COGNITIVE_CONTROL"] == 0.55
