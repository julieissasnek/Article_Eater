"""Tests for empirical_v2 output validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    script_path = root / "scripts" / "validate_empirical_v2_output.py"
    spec = importlib.util.spec_from_file_location("validate_empirical_v2_output", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_flags_q_as_p_value():
    mod = _load_module()
    payload = {
        "claims": [
            {
                "claim_id": "C1",
                "significance_text": "q < .05",
                "p_value": 0.01,
            }
        ]
    }
    issues = mod.validate_payload(payload, "x.json")
    codes = {i["code"] for i in issues}
    assert "Q_AS_P_VALUE" in codes


def test_flags_abstract_source_mismatch_and_numeric_support():
    mod = _load_module()
    payload = {
        "claims": [
            {
                "claim_id": "C2",
                "claim_source": "abstract",
                "section": "Results",
                "provenance_depth": "section",
                "effect_size": 0.4,
                "p_value": 0.03,
                "evidence_quote": "Children reported more crowding overall.",
            }
        ]
    }
    issues = mod.validate_payload(payload, "x.json")
    codes = {i["code"] for i in issues}
    assert "ABSTRACT_SOURCE_SECTION_MISMATCH" in codes
    assert "ABSTRACT_SOURCE_PROVENANCE_MISMATCH" in codes
    assert "ABSTRACT_NUMERIC_WITHOUT_QUOTE_SUPPORT" in codes


def test_flags_sign_direction_conflict_without_reverse_note():
    mod = _load_module()
    payload = {
        "claims": [
            {
                "claim_id": "C3",
                "direction": "decrease",
                "effect_size_type": "beta",
                "effect_size": 0.8,
                "notes": "",
                "evidence_quote": "Higher ceiling height reduced stress.",
            }
        ]
    }
    issues = mod.validate_payload(payload, "x.json")
    codes = {i["code"] for i in issues}
    assert "SIGN_DIRECTION_CONFLICT" in codes


def test_does_not_flag_sign_direction_with_reverse_note():
    mod = _load_module()
    payload = {
        "claims": [
            {
                "claim_id": "C4",
                "direction": "increase",
                "effect_size_type": "beta",
                "effect_size": -4.8,
                "notes": "reverse-coded outcome scale",
                "evidence_quote": "Lower score indicates more crowding.",
            }
        ]
    }
    issues = mod.validate_payload(payload, "x.json")
    codes = {i["code"] for i in issues}
    assert "SIGN_DIRECTION_CONFLICT" not in codes


def test_flags_interaction_without_moderator():
    mod = _load_module()
    payload = {
        "claims": [
            {
                "claim_id": "C5",
                "iv_raw": "perceived crowding × ceiling height",
                "moderators": [],
            }
        ]
    }
    issues = mod.validate_payload(payload, "x.json")
    codes = {i["code"] for i in issues}
    assert "INTERACTION_WITHOUT_MODERATOR_FIELD" in codes


def test_flags_marginal_significance_marked_true():
    mod = _load_module()
    payload = {
        "claims": [
            {
                "claim_id": "C6",
                "significance_text": "q < .10 (marginal)",
                "is_significant": True,
            }
        ]
    }
    issues = mod.validate_payload(payload, "x.json")
    codes = {i["code"] for i in issues}
    assert "MARGINAL_FLAGGED_SIGNIFICANT" in codes

