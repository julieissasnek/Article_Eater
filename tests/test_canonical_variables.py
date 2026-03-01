import pytest
import subprocess
from pathlib import Path

def test_all_variables_registered_in_schema():
    """
    Test that all variables referenced in template JSON mechanism chains,
    inputs, and outputs exist inside canonical_variables.json. Calls the A-02
    lint script.
    """
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "lint_variables.py"
    
    result = subprocess.run(
        ["python3", str(script_path), "--strict"],
        cwd=str(repo_root),
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        pytest.fail(
            f"Unregistered variables found in the templates.\n"
            f"Please register them in schemas/canonical_variables.json:\n\n{result.stdout}\n{result.stderr}"
        )
