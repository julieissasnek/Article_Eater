"""Tests for empirical_v2 sentence->field training set builder."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_builder_module():
    root = Path(__file__).resolve().parents[1]
    script_path = root / "scripts" / "build_empirical_v2_sentence_training_set.py"
    spec = importlib.util.spec_from_file_location("empirical_v2_builder", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_select_sentences_prefers_iv_dv_and_returns_context():
    mod = _load_builder_module()
    quote = (
        "We measured interior density and mood outcomes. "
        "Higher interior density significantly increased stress ratings (p < .05). "
        "No ceiling-height buffering was found in this sample."
    )
    picks = mod._select_sentences(
        quote=quote,
        iv_raw="interior density",
        dv_raw="stress ratings",
        max_sentences=2,
    )

    assert len(picks) == 2
    first = picks[0]
    assert isinstance(first[0], int)
    assert "interior density" in first[1].lower() or "stress ratings" in first[1].lower()
    assert "stress ratings" in first[2].lower()


def test_build_dataset_emits_sentence_level_field_evidence(tmp_path):
    mod = _load_builder_module()
    claims_path = tmp_path / "claims.json"
    out_train = tmp_path / "train.jsonl"
    out_review = tmp_path / "review.jsonl"
    out_summary = tmp_path / "summary.json"

    payload = {
        "claims": [
            {
                "claim_id": "C1",
                "paper_id": "P1",
                "article_type_family": "empirical_v2",
                "claim_source": "abstract",
                "source_quote": (
                    "Higher noise exposure increased stress ratings in children. "
                    "This relationship was significant (p = 0.03)."
                ),
                "iv": "noise_exposure",
                "dv": "stress",
                "iv_raw": "noise exposure",
                "dv_raw": "stress ratings",
                "direction": "increase",
                "extraction_confidence": 0.9,
                "claim_type": "associational",
            }
        ]
    }
    claims_path.write_text(json.dumps(payload), encoding="utf-8")

    summary = mod.build_dataset(
        claims_path=str(claims_path),
        out_train=str(out_train),
        out_review=str(out_review),
        out_summary=str(out_summary),
        min_reliability=0.5,
        min_sentence_chars=20,
        max_per_direction=5000,
        allowed_sources={"abstract"},
        sentences_per_claim=2,
    )

    assert summary["train_count"] >= 1
    rows = [json.loads(line) for line in out_train.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows
    row = rows[0]
    assert row["sentence_text"]
    assert row["context_window_text"]
    assert row["fields"]["iv"] == "noise_exposure"
    assert row["fields"]["dv"] == "stress"
    assert "field_evidence" in row
    assert row["field_evidence"]["iv_span"] is not None
    assert row["field_evidence"]["dv_span"] is not None


def test_placeholder_variable_labels_route_to_review(tmp_path):
    mod = _load_builder_module()
    claims_path = tmp_path / "claims.json"
    out_train = tmp_path / "train.jsonl"
    out_review = tmp_path / "review.jsonl"
    out_summary = tmp_path / "summary.json"

    payload = {
        "claims": [
            {
                "claim_id": "C2",
                "paper_id": "P2",
                "article_type_family": "empirical_v2",
                "claim_source": "table",
                "source_quote": "row_1 shows col_2 increased compared with baseline.",
                "iv": "lighting",
                "dv": "stress",
                "iv_raw": "col_2",
                "dv_raw": "stress",
                "direction": "increase",
                "extraction_confidence": 0.95,
                "claim_type": "associational",
            }
        ]
    }
    claims_path.write_text(json.dumps(payload), encoding="utf-8")

    summary = mod.build_dataset(
        claims_path=str(claims_path),
        out_train=str(out_train),
        out_review=str(out_review),
        out_summary=str(out_summary),
        min_reliability=0.5,
        min_sentence_chars=20,
        max_per_direction=5000,
        allowed_sources={"all"},
        sentences_per_claim=1,
    )

    assert summary["train_count"] == 0
    assert summary["review_count"] == 1
    rows = [json.loads(line) for line in out_review.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows[0]["label_quality"]["placeholder_variable_detected"] is True
