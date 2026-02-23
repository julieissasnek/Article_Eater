import json
import subprocess
import sys
from pathlib import Path

from scripts.run_web_of_belief_health_baseline import build_markdown, parse_seeds


def test_parse_seeds() -> None:
    assert parse_seeds("1337, 2026,4242") == [1337, 2026, 4242]
    assert parse_seeds("  ") == []


def test_build_markdown_has_expected_sections() -> None:
    data = {
        "generated_at_utc": "2026-02-19T00:00:00+00:00",
        "iterations": 100,
        "seeds": [1, 2],
        "runs": [
            {
                "seed": 1,
                "elapsed_seconds": 1.23,
                "counters": {
                    "beliefs": 10,
                    "constraints": 20,
                    "add_belief": 3,
                    "add_constraint": 4,
                    "add_evidence": 2,
                    "seek_equilibrium": 1,
                    "theory_worlds": 8,
                },
            }
        ],
        "aggregate": {
            "mean_elapsed_seconds": 1.23,
            "min_elapsed_seconds": 1.23,
            "max_elapsed_seconds": 1.23,
        },
    }
    text = build_markdown(data)
    assert "# WebOfBelief Stress Baseline" in text
    assert "## Runs" in text
    assert "## Aggregate" in text
    assert "| Seed | Elapsed (s) |" in text


def test_baseline_runner_writes_outputs(tmp_path: Path) -> None:
    json_out = tmp_path / "baseline.json"
    md_out = tmp_path / "baseline.md"
    cmd = [
        sys.executable,
        "scripts/run_web_of_belief_health_baseline.py",
        "--iterations",
        "50",
        "--seeds",
        "1337",
        "--markdown-out",
        str(md_out),
        "--json-out",
        str(json_out),
    ]
    subprocess.run(cmd, check=True, cwd=Path(__file__).resolve().parents[1])

    assert json_out.exists()
    assert md_out.exists()

    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert payload["iterations"] == 50
    assert payload["seeds"] == [1337]
    assert len(payload["runs"]) == 1
    assert "mean_elapsed_seconds" in payload["aggregate"]
