"""
Template Loading Utilities with Schema Validation

Provides centralized template loading with optional schema validation.
All template loading throughout the codebase should use these functions
to ensure consistency and schema compliance.

Usage:
    from src.data.template_loader import load_template, load_all_templates

    # Load single template with validation
    template = load_template("ED_HIPPOCAMPAL_ENCODING_001")

    # Load all templates
    templates = load_all_templates()

    # Load without validation (faster, for trusted contexts)
    template = load_template("ED_HIPPOCAMPAL_ENCODING_001", validate=False)

Author: Claude Code (Feb 23, 2026)
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Paths
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = _PROJECT_ROOT / "data" / "templates"
SCHEMA_PATH = _PROJECT_ROOT / "schemas" / "template_canonical.json"


class TemplateValidationError(Exception):
    """Raised when template validation fails."""

    def __init__(self, template_id: str, errors: list[str]):
        self.template_id = template_id
        self.errors = errors
        super().__init__(f"Template '{template_id}' validation failed: {errors}")


class TemplateNotFoundError(Exception):
    """Raised when template file is not found."""

    def __init__(self, template_id: str):
        self.template_id = template_id
        super().__init__(f"Template not found: {template_id}")


@lru_cache(maxsize=1)
def _load_schema() -> dict[str, Any]:
    """Load the canonical template schema (cached)."""
    if not SCHEMA_PATH.exists():
        logger.warning("Schema file not found: %s", SCHEMA_PATH)
        return {}
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _get_validator():
    """Get JSON Schema validator (cached). Returns None if jsonschema not available."""
    try:
        from jsonschema import Draft202012Validator

        schema = _load_schema()
        if schema:
            return Draft202012Validator(schema)
    except ImportError:
        logger.debug("jsonschema not installed, schema validation disabled")
    return None


def _validate_scaffold_tier(data: dict[str, Any]) -> list[str]:
    """Validate scaffold tier requirements."""
    errors = []

    if not data.get("template_id"):
        errors.append("Missing required field: template_id")

    if not data.get("display_id"):
        errors.append("Missing required field: display_id")

    if not data.get("name") and not data.get("template_name"):
        errors.append("Missing required field: name or template_name")

    status = data.get("calibration_status") or data.get("status")
    if status not in ("calibrated", "scaffold", "uncalibrated", "partial", None):
        errors.append(f"Invalid calibration_status: {status}")

    return errors


def _validate_calibrated_tier(data: dict[str, Any]) -> list[str]:
    """Validate calibrated tier requirements."""
    errors = []

    status = data.get("calibration_status") or data.get("status")
    is_calibrated = status == "calibrated" or data.get("calibrated") is True

    if not is_calibrated:
        return []

    chain = data.get("mechanism_chain") or data.get("mechanism_steps", [])
    if not chain:
        errors.append("Calibrated template missing mechanism_chain")

    return errors


def validate_template(data: dict[str, Any], template_id: str = "unknown") -> list[str]:
    """
    Validate template data against schema and tier requirements.

    Args:
        data: Template dictionary
        template_id: Template ID for error messages

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # JSON Schema validation
    validator = _get_validator()
    if validator:
        for error in validator.iter_errors(data):
            path = ".".join(str(p) for p in error.absolute_path)
            if path:
                errors.append(f"{path}: {error.message}")
            else:
                errors.append(error.message)

    # Scaffold tier validation
    errors.extend(_validate_scaffold_tier(data))

    # Calibrated tier validation
    errors.extend(_validate_calibrated_tier(data))

    return errors


def load_template(
    template_id: str,
    *,
    validate: bool = True,
    raise_on_error: bool = True,
) -> dict[str, Any]:
    """
    Load a template by ID with optional schema validation.

    Args:
        template_id: Template ID (e.g., "ED_HIPPOCAMPAL_ENCODING_001")
        validate: Whether to validate against schema (default True)
        raise_on_error: Whether to raise exception on validation errors (default True)

    Returns:
        Template dictionary

    Raises:
        TemplateNotFoundError: If template file doesn't exist
        TemplateValidationError: If validation fails and raise_on_error=True
    """
    # Handle both with and without .json extension
    if template_id.endswith(".json"):
        template_id = template_id[:-5]

    file_path = TEMPLATES_DIR / f"{template_id}.json"

    if not file_path.exists():
        raise TemplateNotFoundError(template_id)

    data = json.loads(file_path.read_text(encoding="utf-8"))

    if validate:
        errors = validate_template(data, template_id)
        if errors:
            if raise_on_error:
                raise TemplateValidationError(template_id, errors)
            else:
                logger.warning(
                    "Template '%s' has validation errors: %s",
                    template_id,
                    errors,
                )

    return data


def load_all_templates(
    *,
    validate: bool = False,
    skip_invalid: bool = True,
) -> dict[str, dict[str, Any]]:
    """
    Load all templates from the templates directory.

    Args:
        validate: Whether to validate each template (default False for performance)
        skip_invalid: Whether to skip invalid templates (default True)

    Returns:
        Dictionary mapping template_id to template data
    """
    templates = {}

    if not TEMPLATES_DIR.exists():
        logger.warning("Templates directory not found: %s", TEMPLATES_DIR)
        return templates

    for file_path in sorted(TEMPLATES_DIR.glob("*.json")):
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            template_id = data.get("template_id") or file_path.stem

            if validate:
                errors = validate_template(data, template_id)
                if errors:
                    if skip_invalid:
                        logger.warning(
                            "Skipping invalid template '%s': %s",
                            template_id,
                            errors,
                        )
                        continue
                    else:
                        raise TemplateValidationError(template_id, errors)

            templates[template_id] = data

        except json.JSONDecodeError as e:
            logger.warning("Skipping malformed JSON file '%s': %s", file_path.name, e)
            if not skip_invalid:
                raise

    return templates


def get_calibrated_templates(
    *,
    validate: bool = False,
) -> dict[str, dict[str, Any]]:
    """
    Load only calibrated templates.

    Args:
        validate: Whether to validate each template

    Returns:
        Dictionary mapping template_id to template data for calibrated templates only
    """
    all_templates = load_all_templates(validate=validate)
    return {
        tid: data
        for tid, data in all_templates.items()
        if (data.get("calibration_status") or data.get("status")) == "calibrated"
        or data.get("calibrated") is True
    }


def template_exists(template_id: str) -> bool:
    """Check if a template file exists."""
    if template_id.endswith(".json"):
        template_id = template_id[:-5]
    return (TEMPLATES_DIR / f"{template_id}.json").exists()
