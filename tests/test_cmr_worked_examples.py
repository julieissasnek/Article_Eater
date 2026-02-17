"""Tests for Sprint 10 worked examples."""

from src.cmr.worked_examples import run_primary_school_classroom_example


def test_primary_school_classroom_shows_developmental_difference(tmp_path):
    report = run_primary_school_classroom_example(db_path=str(tmp_path / "cmr_worked_example.db"))

    child = report["profiles"]["child_age_7"]
    teacher = report["profiles"]["teacher_age_35"]
    delta = report["delta_child_minus_teacher"]

    assert child["overall_wis"] > teacher["overall_wis"]
    assert delta["overall_wis"] > 3.0

    # Developmental uplift should be visible in at least these key domains.
    assert delta["domain_scores"]["L"] > 0
    assert delta["domain_scores"]["TP"] > 0
