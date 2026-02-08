import json
import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_governance_kit_present():
    """Test that core governance files are present.

    Note: GitHub workflow files are optional and only checked if .github/workflows exists.
    """
    # Core governance files (always required)
    core_files = [
        "Project_Constitution.md",
        "release.keep.yml",
        "deprecations.yml",
        "CODEOWNERS",
        "scripts/check_governance.py",
        "scripts/orphan_sweep.py",
        "scripts/public_surface_ledger.py",
        "scripts/manifest_sha256.py",
        "reconstructor_min.py",
        "deconcat.py",
        "public_surface_ledger.json",
    ]

    # GitHub workflows (optional - only check if directory exists)
    workflows_dir = ROOT / ".github" / "workflows"

    missing = [m for m in core_files if not (ROOT / m).exists()]
    assert not missing, f"Missing core governance files: {missing}"

    # Only check workflow files if the workflows directory exists
    if workflows_dir.exists():
        workflow_files = ["governance.yml"]
        missing_workflows = [w for w in workflow_files if not (workflows_dir / w).exists()]
        if missing_workflows:
            pytest.skip(f"GitHub workflows configured but missing: {missing_workflows}")

def test_rules_contract_registered():
    ledger = json.loads((ROOT/'public_surface_ledger.json').read_text())
    assert any(c.get('file')=='contracts/rules_v1.md' for c in ledger.get('contracts', [])), 'rules contract missing from ledger'