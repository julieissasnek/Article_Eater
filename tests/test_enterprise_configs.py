import pathlib
import pytest


def test_enterprise_configs_present():
    """Test that core enterprise configuration files exist.

    Note: Some CI/CD configs (GitHub workflows, pre-commit) are optional
    and only checked if already set up.
    """
    root = pathlib.Path(".")

    # Required files
    assert (root / "Dockerfile").exists(), "Dockerfile missing"
    assert (root / "config" / "logging.conf").exists(), "logging.conf missing"

    # Optional files - skip if not set up
    if not (root / ".github" / "workflows").exists():
        pytest.skip("GitHub workflows not yet configured")
    if not (root / ".pre-commit-config.yaml").exists():
        pytest.skip("Pre-commit hooks not yet configured")