import csv
import json
from pathlib import Path
from unittest.mock import patch

from src.extraction.batch_extract import run_batch_extraction


def _write_csv(path: Path) -> None:
    fieldnames = [
        "paper_id",
        "source_table_id",
        "source_table_row",
        "source_quote",
        "statement",
        "content",
        "title",
        "abstract",
        "article_type_predicted_family",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "paper_id": "p1",
                "source_table_id": "TBL1",
                "source_table_row": "1",
                "source_quote": "col_1: Predictor; col_2: beta=.31; col_3: p=.02",
                "statement": "",
                "content": "",
                "title": "Test paper",
                "abstract": "Effects of daylight on stress.",
                "article_type_predicted_family": "empirical_v2",
            }
        )


def _write_vocab(path: Path) -> None:
    payload = {
        "independent_variables": {
            "illuminance_lux": {"synonyms": ["daylight", "light", "illuminance"]},
        },
        "dependent_variables": {
            "stress": {"synonyms": ["stress", "anxiety"]},
            "creativity": {"synonyms": ["creativity"]},
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_d15_caption_dv_override_and_merge(tmp_path: Path):
    csv_path = tmp_path / "rows.csv"
    triage_path = tmp_path / "triage.json"
    table_class_path = tmp_path / "tables.json"
    vocab_path = tmp_path / "vocab.json"
    abstract_path = tmp_path / "abstract_claims.json"
    caption_lookup_path = tmp_path / "caption_dv_lookup.json"
    output_path = tmp_path / "structured_claims.json"

    _write_csv(csv_path)
    _write_vocab(vocab_path)

    triage_path.write_text(
        json.dumps(
            {
                "papers": [
                    {
                        "paper_id": "p1",
                        "triage_type": "empirical",
                        "article_type_family": "unknown",
                        "extractable": True,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    table_class_path.write_text(
        json.dumps(
            {
                "TBL1": {
                    "paper_id": "p1",
                    "type": "RESULTS_REGRESSION",
                    "extractable": True,
                    "page": 1,
                    "sample_content": "Table 1. Regression results for stress.",
                }
            }
        ),
        encoding="utf-8",
    )
    caption_lookup_path.write_text(json.dumps({"TBL1": "stress"}), encoding="utf-8")

    abstract_claims = [
        {
            "claim_id": "a1",
            "paper_id": "p1",
            "iv": "illuminance_lux",
            "dv": "stress",
            "direction": "decrease",
            "context": "lab",
            "source": "abstract",
        },
        {
            "claim_id": "c1",
            "paper_id": "p1",
            "iv": "illuminance_lux",
            "dv": "stress",
            "direction": "increase",
            "source": "caption",
        },
    ]
    abstract_path.write_text(json.dumps({"claims": abstract_claims}), encoding="utf-8")

    mocked_table_claims = [
        {
            "claim_id": "t1",
            "paper_id": "p1",
            "iv": "illuminance_lux",
            "iv_raw": "daylight",
            "iv_mapped": True,
            "iv_confidence": 0.9,
            "dv": "creativity",  # should be overridden via caption lookup
            "dv_raw": "creativity",
            "dv_mapped": True,
            "dv_confidence": 0.9,
            "direction": "decrease",
            "source_table_id": "TBL1",
            "source_page": 1,
            "source_quote": "beta = -0.31, p = .02",
            "effect_size": 0.6,
        }
    ]

    with patch("src.extraction.batch_extract.extract_claims_from_paper", return_value=mocked_table_claims):
        result = run_batch_extraction(
            csv_path=str(csv_path),
            triage_path=str(triage_path),
            table_class_path=str(table_class_path),
            vocabulary_path=str(vocab_path),
            abstract_claims_path=str(abstract_path),
            caption_dv_lookup_path=str(caption_lookup_path),
            output_path=str(output_path),
            method="enhanced",
        )

    assert result["summary"]["from_tables"] == 1
    assert result["summary"]["from_abstracts"] == 1
    assert result["summary"]["from_captions"] == 1
    # Table + abstract agree (decrease), caption conflicts (increase)
    assert result["summary"]["conflicts"] >= 1

    table_claim = next(c for c in result["claims"] if c.get("claim_source") == "table")
    assert table_claim["dv"] == "stress"
    assert table_claim["dv_from_caption_lookup"] is True
    assert table_claim["article_type_family"] == "empirical_v2"
    assert table_claim["claim_type"] in {"associational", "causal", "moderated", "null", "mechanistic"}
    assert table_claim["rule_type"] == "edge"
    assert table_claim["field_contract_family"] == "empirical_v2"
    assert isinstance(table_claim.get("field_targets"), list) and table_claim["field_targets"]


def test_d15_caption_dv_override_by_page_fallback(tmp_path: Path):
    csv_path = tmp_path / "rows.csv"
    triage_path = tmp_path / "triage.json"
    table_class_path = tmp_path / "tables.json"
    vocab_path = tmp_path / "vocab.json"
    abstract_path = tmp_path / "abstract_claims.json"
    caption_lookup_path = tmp_path / "caption_dv_lookup.json"
    output_path = tmp_path / "structured_claims.json"

    _write_csv(csv_path)
    _write_vocab(vocab_path)
    triage_path.write_text(
        json.dumps(
            {
                "papers": [
                    {
                        "paper_id": "p1",
                        "triage_type": "empirical",
                        "article_type_family": "empirical_v2",
                        "extractable": True,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    table_class_path.write_text(
        json.dumps(
            {
                "TBL1": {
                    "paper_id": "p1",
                    "type": "RESULTS_REGRESSION",
                    "extractable": True,
                    "page": 10,
                    "sample_content": "Table 1. Regression results for stress.",
                }
            }
        ),
        encoding="utf-8",
    )
    # Lookup uses different table id but same paper/page.
    caption_lookup_path.write_text(
        json.dumps(
            {
                "TBL-OTHER": {
                    "paper_id": "p1",
                    "source_page": 10,
                    "dv_raw": "stress",
                    "dv": "stress",
                    "confidence": 0.9,
                }
            }
        ),
        encoding="utf-8",
    )
    abstract_path.write_text(json.dumps({"claims": []}), encoding="utf-8")

    mocked_table_claims = [
        {
            "claim_id": "t1",
            "paper_id": "p1",
            "iv": "illuminance_lux",
            "iv_raw": "daylight",
            "iv_mapped": True,
            "iv_confidence": 0.9,
            "dv": "creativity",
            "dv_raw": "creativity",
            "dv_mapped": True,
            "dv_confidence": 0.4,  # low-confidence table DV should be override-eligible
            "direction": "decrease",
            "source_table_id": "TBL1",
            "source_page": 10,
            "source_quote": "beta = -0.31, p = .02",
            "effect_size": 0.6,
        }
    ]

    with patch("src.extraction.batch_extract.extract_claims_from_paper", return_value=mocked_table_claims):
        result = run_batch_extraction(
            csv_path=str(csv_path),
            triage_path=str(triage_path),
            table_class_path=str(table_class_path),
            vocabulary_path=str(vocab_path),
            abstract_claims_path=str(abstract_path),
            caption_dv_lookup_path=str(caption_lookup_path),
            output_path=str(output_path),
            method="enhanced",
        )

    table_claim = next(c for c in result["claims"] if c.get("claim_source") == "table")
    assert table_claim["dv"] == "stress"
    assert table_claim["dv_from_caption_lookup"] is True
    assert table_claim["dv_from_caption_lookup_mode"] == "paper_page_near"
