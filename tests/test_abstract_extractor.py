import csv
import json
import sqlite3
from pathlib import Path

from src.extraction.abstract_extractor import (
    batch_extract_abstracts_and_captions,
    extract_claims_from_abstract,
    extract_claims_from_captions,
)


def _sample_vocab() -> dict:
    return {
        "independent_variables": {
            "illuminance_lux": {"synonyms": ["daylight", "light level", "lighting"]},
            "ambient_noise_dba": {"synonyms": ["noise", "ambient noise"]},
        },
        "dependent_variables": {
            "creativity": {"synonyms": ["creative thinking", "creativity"]},
            "stress": {"synonyms": ["stress", "anxiety"]},
        },
    }


def test_extract_claims_from_abstract_basic():
    claims = extract_claims_from_abstract(
        paper_id="p1",
        title="Noise and creativity",
        abstract=(
            "Results showed that a moderate level of ambient noise enhances creative thinking "
            "(r = .30, p = .01, n = 65)."
        ),
        vocabulary=_sample_vocab(),
        article_type_family="empirical_v2",
    )
    assert claims
    c = claims[0]
    assert c["paper_id"] == "p1"
    assert c["iv_mapped"] is True
    assert c["dv_mapped"] is True
    assert c["direction"] in {"increase", "decrease", "no_effect", "unknown"}
    assert c["source"] == "abstract"


def test_extract_claims_from_captions_filters_non_results():
    claims = extract_claims_from_captions(
        paper_id="p2",
        captions=[
            {"text": "Figure 2. Photograph of the experimental room setup."},
            {"text": "Table 3. Regression results for stress by condition; ambient noise beta = 0.31, p = .02"},
        ],
        vocabulary=_sample_vocab(),
        article_type_family="empirical_v2",
    )
    # Should ignore photo caption and keep the results caption-derived claim(s).
    assert claims
    assert all(c["source"] == "caption" for c in claims)


def test_batch_extract_abstracts_and_captions_outputs_artifacts(tmp_path: Path):
    vocab_path = tmp_path / "vocab.json"
    triage_path = tmp_path / "triage.json"
    confirmed_csv = tmp_path / "confirmed.csv"
    table_class_path = tmp_path / "table_classifications.json"
    out_claims = tmp_path / "abstract_claims.json"
    out_lookup = tmp_path / "caption_dv_lookup.json"

    vocab_path.write_text(json.dumps(_sample_vocab()), encoding="utf-8")
    triage_path.write_text(
        json.dumps(
            {
                "papers": [
                        {
                            "paper_id": "p1",
                            "title": "Test paper",
                            "abstract": (
                                "Results showed ambient noise increased stress during sustained attention tasks "
                                "in office settings (r = .35, p = .02, n = 80)."
                            ),
                            "article_type_family": "empirical_v2",
                        }
                    ]
                }
        ),
        encoding="utf-8",
    )

    with confirmed_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["paper_id", "source_quote", "source_table_id", "source_page_start", "source_page_end"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "paper_id": "p1",
                "source_quote": "Table 5. Regression results for stress by condition.",
                "source_table_id": "TBL-1",
                "source_page_start": "6",
                "source_page_end": "6",
            }
            )
    table_class_path.write_text("{}", encoding="utf-8")

    summary = batch_extract_abstracts_and_captions(
        triage_path=str(triage_path),
        confirmed_csv_path=str(confirmed_csv),
        table_classifications_path=str(table_class_path),
        vocabulary_path=str(vocab_path),
        output_path=str(out_claims),
        caption_lookup_output_path=str(out_lookup),
    )

    assert out_claims.exists()
    assert out_lookup.exists()
    payload = json.loads(out_claims.read_text(encoding="utf-8"))
    lookup = json.loads(out_lookup.read_text(encoding="utf-8"))
    assert summary["total_claims"] >= 1
    assert payload["claims"]
    assert "TBL-1" in lookup


def _write_metadata_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["paper_id", "doi", "title", "pdf_path"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_article_db(path: Path, rows: list[dict]) -> None:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE papers (
            paper_id TEXT,
            doi TEXT,
            title TEXT,
            abstract TEXT
        )
        """
    )
    for row in rows:
        cur.execute(
            "INSERT INTO papers (paper_id, doi, title, abstract) VALUES (?, ?, ?, ?)",
            (row.get("paper_id"), row.get("doi"), row.get("title"), row.get("abstract")),
        )
    conn.commit()
    conn.close()


def _write_preprocess_cache(path: Path, paper_id: str, text: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    payload = {"paper_id": paper_id, "pages": [{"page": 1, "text": text}]}
    out = path / f"{paper_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload), encoding="utf-8")


def test_batch_extract_backfills_abstract_from_article_db(tmp_path: Path):
    vocab_path = tmp_path / "vocab.json"
    triage_path = tmp_path / "triage.json"
    confirmed_csv = tmp_path / "confirmed.csv"
    table_class_path = tmp_path / "table_classifications.json"
    metadata_csv = tmp_path / "queue.csv"
    article_db = tmp_path / "article_finder.db"
    preprocess_dir = tmp_path / "preprocess"
    out_claims = tmp_path / "abstract_claims.json"
    out_lookup = tmp_path / "caption_dv_lookup.json"

    vocab_path.write_text(json.dumps(_sample_vocab()), encoding="utf-8")
    triage_path.write_text(
        json.dumps({"papers": [{"paper_id": "doi:10.1000/demo", "article_type_family": "empirical_v2"}]}),
        encoding="utf-8",
    )
    with confirmed_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["paper_id", "source_quote", "source_table_id"])
        writer.writeheader()
    table_class_path.write_text("{}", encoding="utf-8")
    _write_metadata_csv(
        metadata_csv,
        rows=[{"paper_id": "doi:10.1000/demo", "doi": "10.1000/demo", "title": "Noise and creativity", "pdf_path": ""}],
    )
    _write_article_db(
        article_db,
        rows=[
            {
                "paper_id": "doi:10.1000/demo",
                "doi": "10.1000/demo",
                "title": "Noise and creativity",
                "abstract": (
                    "Results showed that ambient noise increased stress in office workers during a controlled "
                    "task session, and the effect remained robust after adjustment for baseline differences "
                    "(r = .30, p = .01, n = 72)."
                ),
            }
        ],
    )

    summary = batch_extract_abstracts_and_captions(
        triage_path=str(triage_path),
        confirmed_csv_path=str(confirmed_csv),
        table_classifications_path=str(table_class_path),
        metadata_csv_path=str(metadata_csv),
        preprocess_cache_dir=str(preprocess_dir),
        article_db_path=str(article_db),
        vocabulary_path=str(vocab_path),
        output_path=str(out_claims),
        caption_lookup_output_path=str(out_lookup),
    )

    assert summary["papers_with_abstract"] == 1
    assert summary["abstract_source_counts"]["article_db"] == 1
    assert summary["from_abstracts"] >= 1


def test_batch_extract_fallbacks_to_preprocess_abstract_and_captions(tmp_path: Path):
    vocab_path = tmp_path / "vocab.json"
    triage_path = tmp_path / "triage.json"
    confirmed_csv = tmp_path / "confirmed.csv"
    table_class_path = tmp_path / "table_classifications.json"
    metadata_csv = tmp_path / "queue.csv"
    preprocess_dir = tmp_path / "preprocess"
    out_claims = tmp_path / "abstract_claims.json"
    out_lookup = tmp_path / "caption_dv_lookup.json"

    vocab_path.write_text(json.dumps(_sample_vocab()), encoding="utf-8")
    triage_path.write_text(
        json.dumps({"papers": [{"paper_id": "doi:10.1000/pre", "article_type_family": "empirical_v2"}]}),
        encoding="utf-8",
    )
    with confirmed_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["paper_id", "source_quote", "source_table_id"])
        writer.writeheader()
    table_class_path.write_text("{}", encoding="utf-8")
    _write_metadata_csv(metadata_csv, rows=[])
    _write_preprocess_cache(
        preprocess_dir,
        paper_id="doi:10.1000/pre",
        text=(
            "ABSTRACT: Results showed ambient noise increased stress in a lab experiment while participants "
            "completed a concentration task, and this relationship remained significant "
            "(r = .32, p = .02, n = 64). Keywords: acoustics\n"
            "Table 2. Effect of ambient noise on stress, beta = .31, p = .02."
        ),
    )

    summary = batch_extract_abstracts_and_captions(
        triage_path=str(triage_path),
        confirmed_csv_path=str(confirmed_csv),
        table_classifications_path=str(table_class_path),
        metadata_csv_path=str(metadata_csv),
        preprocess_cache_dir=str(preprocess_dir),
        article_db_path=str(tmp_path / "missing.db"),
        vocabulary_path=str(vocab_path),
        output_path=str(out_claims),
        caption_lookup_output_path=str(out_lookup),
    )

    assert summary["papers_with_abstract"] == 1
    assert summary["abstract_source_counts"]["preprocess_cache"] == 1
    assert summary["papers_with_caption_candidates"] == 1
    assert summary["from_captions"] >= 1


def test_caption_lookup_uses_table_classifications_source(tmp_path: Path):
    vocab_path = tmp_path / "vocab.json"
    triage_path = tmp_path / "triage.json"
    confirmed_csv = tmp_path / "confirmed.csv"
    table_class_path = tmp_path / "table_classifications.json"
    metadata_csv = tmp_path / "queue.csv"
    out_claims = tmp_path / "abstract_claims.json"
    out_lookup = tmp_path / "caption_dv_lookup.json"

    vocab_path.write_text(json.dumps(_sample_vocab()), encoding="utf-8")
    triage_path.write_text(
        json.dumps({"papers": [{"paper_id": "p1", "abstract": "", "article_type_family": "empirical_v2"}]}),
        encoding="utf-8",
    )
    with confirmed_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["paper_id", "source_quote", "source_table_id"])
        writer.writeheader()
    _write_metadata_csv(metadata_csv, rows=[])
    table_class_path.write_text(
        json.dumps(
            {
                "TBL-X": {
                    "paper_id": "p1",
                    "page": 3,
                    "sample_content": "Table 9. Regression results for stress by condition.",
                }
            }
        ),
        encoding="utf-8",
    )

    batch_extract_abstracts_and_captions(
        triage_path=str(triage_path),
        confirmed_csv_path=str(confirmed_csv),
        table_classifications_path=str(table_class_path),
        metadata_csv_path=str(metadata_csv),
        preprocess_cache_dir=str(tmp_path / "missing_preprocess"),
        article_db_path=str(tmp_path / "missing.db"),
        vocabulary_path=str(vocab_path),
        output_path=str(out_claims),
        caption_lookup_output_path=str(out_lookup),
    )

    lookup = json.loads(out_lookup.read_text(encoding="utf-8"))
    assert "TBL-X" in lookup
