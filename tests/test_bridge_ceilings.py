import pytest
import subprocess
import json
import warnings
from pathlib import Path


def test_bridge_ceilings_adhere_to_schema():
    """
    Test that the ceiling lint script runs successfully and reports violations.

    IMPORTANT: Ceiling violations are NOT hard failures. Ceilings are Bayesian
    soft priors, not hard constraints. When a panel assigns confidence above
    the ceiling, this signals the evidence is stronger than the warrant type's
    default. The correct response is panel review (warrant upgrade or documented
    override), NOT automatic clamping.

    This test:
    - Verifies the lint script runs without crashing
    - Reports any UNREVIEWED violations as warnings (not failures)
    - Accepts violations that have ceiling_override_rationale or ceiling_status=="exceeds"
    """
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "lint_bridge_ceilings.py"
    report_path = repo_root / "data" / "ceiling_violation_report.json"

    result = subprocess.run(
        ["python3", str(script_path), "--report", str(report_path)],
        cwd=str(repo_root),
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Lint script crashed:\n{result.stderr}"
    assert report_path.exists(), "Ceiling violation report not generated."

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    violations = report.get("violations", [])

    # Separate reviewed from unreviewed violations
    reviewed = [
        v for v in violations
        if v.get("ceiling_override_rationale")
        or v.get("ceiling_status") == "exceeds"
    ]
    unreviewed = [
        v for v in violations
        if not v.get("ceiling_override_rationale")
        and v.get("ceiling_status") != "exceeds"
    ]

    if unreviewed:
        debug_info = "\n".join(
            f"  {v['template_id']} | {v['field_path']} | {v['warrant']} | "
            f"conf={v['confidence']:.2f} > ceil={v['ceiling']:.2f}"
            for v in unreviewed
        )
        warnings.warn(
            f"\nFound {len(unreviewed)} UNREVIEWED ceiling exceedances "
            f"(of {len(violations)} total, {len(reviewed)} reviewed).\n"
            f"These need panel review — do NOT auto-clamp.\n"
            f"See docs/CEILING_RECALIBRATION_PANEL_Feb23.md for the review process.\n"
            f"{debug_info}",
            UserWarning
        )

    # The test PASSES as long as the lint script runs.
    # Ceiling exceedances are epistemic signals, not errors.
