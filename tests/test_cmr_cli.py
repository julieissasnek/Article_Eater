"""Tests for the CMR CLI module (Sprint 10 Task 3.9)."""

import json
from pathlib import Path

from src.cmr.cli import build_parser, main


def test_parser_has_evaluate_subcommand():
    parser = build_parser()
    args = parser.parse_args(["evaluate", "--ceiling-height", "3.0", "--floor-area", "25.0"])
    assert args.command == "evaluate"
    assert args.ceiling_height == 3.0
    assert args.floor_area == 25.0


def test_parser_accepts_all_building_features():
    parser = build_parser()
    args = parser.parse_args([
        "evaluate",
        "--ceiling-height", "2.75",
        "--floor-area", "18.0",
        "--building-type", "research_institute",
        "--climate-zone", "3C",
        "--illuminance", "350",
        "--noise", "38",
        "--window-area-ratio", "0.4",
        "--primary-material", "concrete",
        "--secondary-material", "teak",
        "--has-nature-view",
        "--rt60", "0.6",
        "--view-content", "ocean_horizon",
        "--occupant-age", "35",
        "--cultural-context", "Western",
    ])
    assert args.building_type == "research_institute"
    assert args.climate_zone == "3C"
    assert args.illuminance == 350
    assert args.noise == 38
    assert args.window_area_ratio == 0.4
    assert args.primary_material == "concrete"
    assert args.secondary_material == "teak"
    assert args.has_nature_view is True
    assert args.rt60 == 0.6
    assert args.view_content == "ocean_horizon"
    assert args.occupant_age == 35
    assert args.cultural_context == "Western"


def test_parser_json_flag():
    parser = build_parser()
    args = parser.parse_args([
        "evaluate",
        "--ceiling-height", "3.0",
        "--floor-area", "25.0",
        "--json",
    ])
    assert args.json_output is True


def test_parser_verbose_flag():
    parser = build_parser()
    args = parser.parse_args([
        "evaluate",
        "--ceiling-height", "3.0",
        "--floor-area", "25.0",
        "-v",
    ])
    assert args.verbose is True


def test_parser_default_values():
    parser = build_parser()
    args = parser.parse_args([
        "evaluate",
        "--ceiling-height", "3.0",
        "--floor-area", "25.0",
    ])
    assert args.building_type == "generic"
    assert args.climate_zone == "4A"
    assert args.occupant_age == 35
    assert args.cultural_context == "Western"
    assert args.json_output is False
    assert args.verbose is False


def test_main_without_command_returns_zero():
    # Running with no command should print help and return 0
    result = main([])
    assert result == 0


def test_main_evaluate_runs_without_error(tmp_path):
    db_path = tmp_path / "test_cli.db"
    result = main([
        "evaluate",
        "--ceiling-height", "3.0",
        "--floor-area", "25.0",
        "--db-path", str(db_path),
    ])
    assert result == 0


def test_main_evaluate_json_output_is_valid_json(tmp_path, capsys):
    db_path = tmp_path / "test_cli_json.db"
    result = main([
        "evaluate",
        "--ceiling-height", "3.0",
        "--floor-area", "25.0",
        "--db-path", str(db_path),
        "--json",
    ])
    assert result == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert "summary" in report
    assert "overall_wis" in report["summary"]


def test_parser_has_evaluate_paper_subcommand():
    parser = build_parser()
    args = parser.parse_args([
        "evaluate-paper",
        "--claims",
        '[{"iv":"nature_view","dv":"restoration","direction":"increase"}]',
    ])
    assert args.command == "evaluate-paper"
    assert args.claims is not None


def test_main_evaluate_paper_claims_json_output(tmp_path, capsys):
    db_path = tmp_path / "test_cli_paper_json.db"
    result = main([
        "evaluate-paper",
        "--claims",
        '[{"iv":"nature_view","dv":"restoration","direction":"increase","effect_size":0.5}]',
        "--db-path",
        str(db_path),
        "--json",
    ])
    assert result == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert "summary" in report
    assert "claim_assessments" in report


def test_main_evaluate_paper_file_and_verbose(tmp_path, capsys):
    db_path = tmp_path / "test_cli_paper_file.db"
    claims_path = Path(tmp_path) / "paper_claims.json"
    claims_path.write_text(
        json.dumps(
            [
                {
                    "iv": "nature_view",
                    "dv": "stress_reduction",
                    "direction": "decrease",
                    "effect_size": -0.4,
                }
            ]
        ),
        encoding="utf-8",
    )

    result = main([
        "evaluate-paper",
        "--file",
        str(claims_path),
        "--db-path",
        str(db_path),
        "--json",
        "--verbose",
    ])
    assert result == 0
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert "raw_evaluation" in report
    assert report["raw_evaluation"]["status"] == "complete"


def test_main_evaluate_paper_text_output(tmp_path, capsys):
    db_path = tmp_path / "test_cli_paper_text.db"
    result = main([
        "evaluate-paper",
        "--text",
        "Patients with nature views had less stress.",
        "--db-path",
        str(db_path),
    ])
    assert result == 0
    captured = capsys.readouterr()
    assert "PAPER EVALUATION REPORT" in captured.out


def test_parser_quick_assess_accepts_tier_b_inputs():
    parser = build_parser()
    args = parser.parse_args([
        "quick-assess",
        "--ceiling", "3.0",
        "--area", "25.0",
        "--illuminance", "450",
        "--noise", "42",
        "--rt60", "0.5",
    ])
    assert args.command == "quick-assess"
    assert args.illuminance == 450
    assert args.noise == 42
    assert args.rt60 == 0.5


def test_main_quick_assess_json_includes_tier_b_reveals(capsys):
    result = main([
        "quick-assess",
        "--ceiling", "3.0",
        "--area", "25.0",
        "--nature-view", "nature",
        "--illuminance", "450",
        "--noise", "42",
        "--rt60", "0.5",
        "--json",
    ])
    assert result == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["tier_mode"] == "A+B"
    assert isinstance(payload["tier_b_reveals"], list)
