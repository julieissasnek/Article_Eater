import csv
import json
from pathlib import Path

from src.extraction.table_classifier import classify_table, classify_tables, reconstruct_tables


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "paper_id",
        "statement",
        "content",
        "source_quote",
        "source_table_id",
        "source_table_row",
        "source_page_start",
        "quality_flag",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_reconstruct_tables_groups_and_sorts_rows(tmp_path: Path):
    csv_path = tmp_path / "tables.csv"
    _write_csv(
        csv_path,
        [
            {
                "paper_id": "p1",
                "statement": "row2",
                "content": "",
                "source_quote": "",
                "source_table_id": "T1",
                "source_table_row": "2",
                "source_page_start": "10",
                "quality_flag": "ok",
            },
            {
                "paper_id": "p1",
                "statement": "row1",
                "content": "",
                "source_quote": "",
                "source_table_id": "T1",
                "source_table_row": "1",
                "source_page_start": "10",
                "quality_flag": "ok",
            },
        ],
    )
    tables = reconstruct_tables(str(csv_path), ["p1"])
    assert list(tables) == ["T1"]
    assert [row["text"] for row in tables["T1"]["rows"]] == ["row1", "row2"]


def test_classify_table_detects_regression():
    table = {
        "rows": [
            {"text": "Predictor beta SE p-value R2"},
            {"text": "Daylight β = 0.34 SE 0.10 p = 0.01"},
        ]
    }
    out = classify_table(table)
    assert out["type"] == "RESULTS_REGRESSION"
    assert out["extractable"] is True


def test_classify_table_detects_garbage_ocr():
    table = {
        "rows": [{"text": "ffititttiningg thhee sseennssoorrss samplephotoofroomwithhighsalience"}]
    }
    out = classify_table(table)
    assert out["type"] == "GARBAGE"
    assert out["ocr_quality"] == "garbled"


def test_classify_tables_filters_to_triaged_papers_and_writes_json(tmp_path: Path):
    csv_path = tmp_path / "rows.csv"
    triage_path = tmp_path / "paper_triage.json"
    output_path = tmp_path / "table_classifications.json"

    _write_csv(
        csv_path,
        [
            {
                "paper_id": "emp1",
                "statement": "F(1, 60)=4.0 Mean SD",
                "content": "",
                "source_quote": "",
                "source_table_id": "TBL1",
                "source_table_row": "1",
                "source_page_start": "5",
                "quality_flag": "ok",
            },
            {
                "paper_id": "offtopic1",
                "statement": "Age Gender Education",
                "content": "",
                "source_quote": "",
                "source_table_id": "TBL2",
                "source_table_row": "1",
                "source_page_start": "7",
                "quality_flag": "ok",
            },
        ],
    )
    triage_path.write_text(
        json.dumps(
            {
                "emp1": {"type": "empirical"},
                "offtopic1": {"type": "off_topic"},
            }
        ),
        encoding="utf-8",
    )

    summary = classify_tables(
        csv_path=str(csv_path),
        triage_path=str(triage_path),
        output_path=str(output_path),
    )
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert summary["tables_total"] == 1
    assert "TBL1" in data
    assert "TBL2" not in data
