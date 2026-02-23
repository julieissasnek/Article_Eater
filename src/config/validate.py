"""
Startup Validation Module

Validates environment configuration at application startup.
Fails fast with clear error messages if critical configuration is missing.

Usage:
    from src.config.validate import validate_startup

    # Call at app initialization
    validate_startup()  # Raises StartupValidationError if critical config missing

    # Or check without raising
    result = validate_startup(raise_on_error=False)
    if not result.valid:
        print(f"Warnings: {result.warnings}")

Author: Claude Code (Feb 23, 2026)
"""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# Project root
ROOT = Path(__file__).resolve().parents[2]


class StartupValidationError(Exception):
    """Raised when critical startup validation fails."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        msg = "Startup validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        super().__init__(msg)


@dataclass
class ValidationResult:
    """Result of startup validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks_passed: int = 0
    checks_failed: int = 0


def _check_env_var(name: str, required: bool = True) -> tuple[bool, str | None]:
    """Check if environment variable is set."""
    value = os.getenv(name)
    if value:
        return True, None
    if required:
        return False, f"Missing required environment variable: {name}"
    return True, f"Optional environment variable not set: {name}"


def _check_path_exists(path: Path, description: str) -> tuple[bool, str | None]:
    """Check if a path exists."""
    if path.exists():
        return True, None
    return False, f"{description} not found: {path}"


def _check_db_connection(db_path: Path) -> tuple[bool, str | None]:
    """Check if database is accessible."""
    if not db_path.exists():
        return False, f"Database file not found: {db_path}"
    try:
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        conn.execute("SELECT 1")
        conn.close()
        return True, None
    except Exception as e:
        return False, f"Database connection failed: {e}"


def _check_templates_dir() -> tuple[bool, str | None]:
    """Check if templates directory exists and has templates."""
    templates_dir = ROOT / "data" / "templates"
    if not templates_dir.exists():
        return False, f"Templates directory not found: {templates_dir}"
    template_count = len(list(templates_dir.glob("*.json")))
    if template_count == 0:
        return False, "No template files found in templates directory"
    return True, None


def _check_schemas_dir() -> tuple[bool, str | None]:
    """Check if schemas directory exists."""
    schemas_dir = ROOT / "schemas"
    if not schemas_dir.exists():
        return False, f"Schemas directory not found: {schemas_dir}"
    return True, None


# Define validation checks
# Each tuple: (check_function, is_critical, description)
VALIDATION_CHECKS: list[tuple[Callable[[], tuple[bool, str | None]], bool, str]] = [
    # Critical checks (will raise error)
    (_check_templates_dir, True, "Templates directory"),
    (_check_schemas_dir, True, "Schemas directory"),
    # Non-critical checks (warnings only)
    (lambda: _check_path_exists(ROOT / "data" / "vocabulary", "Vocabulary directory"), False, "Vocabulary"),
]


def validate_startup(*, raise_on_error: bool = True) -> ValidationResult:
    """
    Validate startup configuration.

    Args:
        raise_on_error: If True, raise StartupValidationError on critical failures.
                       If False, return ValidationResult with errors/warnings.

    Returns:
        ValidationResult with validation outcome.

    Raises:
        StartupValidationError: If raise_on_error=True and critical checks fail.
    """
    result = ValidationResult(valid=True)

    # Run all checks
    for check_fn, is_critical, description in VALIDATION_CHECKS:
        try:
            passed, message = check_fn()
            if passed:
                result.checks_passed += 1
            else:
                result.checks_failed += 1
                if is_critical:
                    result.errors.append(message or f"{description} check failed")
                    result.valid = False
                else:
                    result.warnings.append(message or f"{description} check warning")
        except Exception as e:
            result.checks_failed += 1
            msg = f"{description} check raised exception: {e}"
            if is_critical:
                result.errors.append(msg)
                result.valid = False
            else:
                result.warnings.append(msg)

    # Check database if AE_DB_PATH is set or default exists
    db_path_env = os.getenv("AE_DB_PATH")
    db_path = Path(db_path_env) if db_path_env else ROOT / "ae.db"
    if db_path.exists():
        passed, message = _check_db_connection(db_path)
        if passed:
            result.checks_passed += 1
        else:
            result.checks_failed += 1
            result.warnings.append(message or "Database check failed")

    # Raise if critical errors and raise_on_error is True
    if not result.valid and raise_on_error:
        raise StartupValidationError(result.errors)

    return result


def validate_or_warn() -> None:
    """
    Validate startup and log warnings (does not raise).

    Use this for non-critical startup validation that logs issues
    but allows the application to continue.
    """
    import logging

    logger = logging.getLogger(__name__)

    result = validate_startup(raise_on_error=False)

    if result.errors:
        for error in result.errors:
            logger.error("Startup validation error: %s", error)

    if result.warnings:
        for warning in result.warnings:
            logger.warning("Startup validation warning: %s", warning)

    if result.valid:
        logger.info(
            "Startup validation passed: %d checks passed, %d warnings",
            result.checks_passed,
            len(result.warnings),
        )
