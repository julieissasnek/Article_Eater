"""
validation_reflexes.py — Inline Success Condition Framework
=============================================================

Provides reusable validation functions ("reflexes") that each 
data-populating function calls to validate its own output.

Design:
  - validate_*() functions return (ok, message) tuples
  - escalate() logs + raises if not ok (fail-fast)
  - warn() logs but continues (soft failure)
  
Usage in any script:
  from src.utils.validation_reflexes import validate_template, escalate
  
  template = build_template(...)
  ok, msg = validate_template(template)
  escalate(ok, msg, context="calibrate_templates.calibrate_single")

Added: 2026-02-28 (V6 prevention — function-level success conditions)
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Core: validate → escalate/warn pattern
# ═══════════════════════════════════════════════════════════════════

class ValidationError(Exception):
    """Raised when a reflex detects unfixable bad data."""
    pass


def escalate(ok: bool, msg: str, context: str = ""):
    """Fail-fast: raise if validation fails."""
    if not ok:
        full_msg = f"[REFLEX FAIL] {context}: {msg}" if context else f"[REFLEX FAIL] {msg}"
        logger.error(full_msg)
        raise ValidationError(full_msg)


def warn(ok: bool, msg: str, context: str = ""):
    """Soft failure: log warning but continue."""
    if not ok:
        full_msg = f"[REFLEX WARN] {context}: {msg}" if context else f"[REFLEX WARN] {msg}"
        logger.warning(full_msg)
    return ok


# ═══════════════════════════════════════════════════════════════════
# Template validation reflexes
# ═══════════════════════════════════════════════════════════════════

def validate_template(t: dict) -> Tuple[bool, str]:
    """Validate a single template has required fields and valid values."""
    if not t.get("template_id"):
        return False, "Missing template_id"
    
    status = t.get("calibration_status", "uncalibrated")
    valid_statuses = {"calibrated", "uncalibrated", "manual_override"}
    if status not in valid_statuses:
        return False, f"Invalid calibration_status: '{status}'"
    
    if status == "calibrated":
        if not t.get("direction_consensus"):
            return False, f"{t['template_id']}: calibrated but missing direction_consensus"
        
        agreement = t.get("direction_agreement")
        if agreement is not None and not (0 <= agreement <= 1):
            return False, f"{t['template_id']}: direction_agreement {agreement} not in [0,1]"
        
        evidence = t.get("evidence_count", 0)
        if evidence < 1:
            return False, f"{t['template_id']}: calibrated with zero evidence"
    
    return True, "OK"


def validate_calibration_batch(templates: List[dict]) -> Tuple[bool, str]:
    """Validate a batch of calibrated templates."""
    errors = []
    for t in templates:
        ok, msg = validate_template(t)
        if not ok:
            errors.append(msg)
    
    if errors:
        return False, f"{len(errors)} template(s) invalid: {errors[:3]}"
    return True, f"All {len(templates)} templates valid"


# ═══════════════════════════════════════════════════════════════════
# Theory validation reflexes
# ═══════════════════════════════════════════════════════════════════

def validate_formalization(theory_id: str, form: dict) -> Tuple[bool, str]:
    """Validate a single theory formalization structure."""
    if not isinstance(form, dict):
        return False, f"{theory_id}: function_form is not a dict"
    
    required = ["function_form", "variables", "predictions"]
    for field in required:
        if field not in form:
            return False, f"{theory_id}: missing '{field}' in function_form"
    
    if not isinstance(form["variables"], dict):
        return False, f"{theory_id}: variables must be a dict"
    
    if len(form["variables"]) < 2:
        return False, f"{theory_id}: too few variables ({len(form['variables'])})"
    
    if not isinstance(form["predictions"], list) or len(form["predictions"]) < 1:
        return False, f"{theory_id}: predictions must be non-empty list"
    
    if len(form["function_form"]) < 5:
        return False, f"{theory_id}: equation too short"
    
    return True, "OK"


def validate_theory_file(theory: dict) -> Tuple[bool, str]:
    """Validate a complete theory JSON file."""
    tid = theory.get("theory_id") or theory.get("name", "unknown")
    
    if not theory.get("theory_id") and not theory.get("name"):
        return False, "Theory has neither theory_id nor name"
    
    if "function_form" not in theory:
        return False, f"{tid}: missing function_form"
    
    return validate_formalization(tid, theory["function_form"])


# ═══════════════════════════════════════════════════════════════════
# Annotation validation reflexes
# ═══════════════════════════════════════════════════════════════════

def validate_annotation_item(item: dict, annotation_type: str) -> Tuple[bool, str]:
    """Validate a single annotation item based on its type."""
    
    type_requirements = {
        "a9": ["antecedent", "consequent"],  # or actual_finding
        "a10": ["parameter", "confidence"],
        "a11": ["claim", "positions"],
        "a13": ["replication_count", "status"],
        "a14": ["effect_size"],
        "a17": ["theory", "hook"],
        "a18": ["question", "estimated_difficulty"],
    }
    
    req = type_requirements.get(annotation_type, [])
    missing = [f for f in req if f not in item]
    
    if missing:
        return False, f"{annotation_type} item missing: {missing}"
    
    # Type-specific checks
    if annotation_type == "a14":
        es = item.get("effect_size")
        if not isinstance(es, (int, float)):
            return False, f"a14 effect_size must be numeric, got {type(es).__name__}"
    
    if annotation_type == "a13":
        if item.get("replication_count", 0) < 2:
            return False, "a13 replication_count must be ≥ 2"
    
    if annotation_type == "a10":
        if item.get("confidence") not in ("high", "medium", "low"):
            return False, f"a10 invalid confidence: {item.get('confidence')}"
    
    return True, "OK"


def validate_annotation_batch(items: list, annotation_type: str, 
                               min_count: int = 1) -> Tuple[bool, str]:
    """Validate a batch of annotations."""
    if not isinstance(items, list):
        return False, f"{annotation_type}: expected list, got {type(items).__name__}"
    
    if len(items) < min_count:
        return False, f"{annotation_type}: only {len(items)} items (need ≥{min_count})"
    
    errors = []
    for i, item in enumerate(items):
        ok, msg = validate_annotation_item(item, annotation_type)
        if not ok:
            errors.append(f"  [{i}] {msg}")
            if len(errors) >= 5:  # Cap error reporting
                errors.append(f"  ... and {len(items) - i - 1} more unchecked")
                break
    
    if errors:
        return False, f"{annotation_type}: {len(errors)} validation errors:\n" + "\n".join(errors)
    
    return True, f"{annotation_type}: all {len(items)} items valid"


# ═══════════════════════════════════════════════════════════════════
# Finding/belief validation reflexes
# ═══════════════════════════════════════════════════════════════════

def validate_finding(finding: dict) -> Tuple[bool, str]:
    """Validate a single extraction finding."""
    required = ["antecedent", "consequent", "direction"]
    for field in required:
        if not finding.get(field):
            return False, f"Finding missing or empty: '{field}'"
    
    valid_directions = {"increase", "decrease", "no_effect", "mixed", "varies"}
    if finding["direction"] not in valid_directions:
        return False, f"Invalid direction: '{finding['direction']}'"
    
    es = finding.get("effect_size")
    if es is not None:
        try:
            float(es)
        except (ValueError, TypeError):
            return False, f"Non-numeric effect_size: {es}"
    
    ss = finding.get("sample_size")
    if ss is not None:
        try:
            if int(ss) <= 0:
                return False, f"Non-positive sample_size: {ss}"
        except (ValueError, TypeError):
            return False, f"Non-numeric sample_size: {ss}"
    
    return True, "OK"


def validate_belief(belief_text: str, credence: float = None) -> Tuple[bool, str]:
    """Validate a single belief before database insertion."""
    if not belief_text or len(belief_text.strip()) < 5:
        return False, f"Belief text too short: '{belief_text}'"
    
    if credence is not None and not (0 <= credence <= 1):
        return False, f"Credence {credence} out of [0,1] range"
    
    return True, "OK"


# ═══════════════════════════════════════════════════════════════════
# JSON file validation reflexes
# ═══════════════════════════════════════════════════════════════════

def validate_json_file(path: Path) -> Tuple[bool, str]:
    """Validate a JSON file is readable and parseable."""
    if not path.exists():
        return False, f"File not found: {path}"
    
    try:
        data = json.load(open(path))
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in {path.name}: {e}"
    
    if data is None:
        return False, f"File {path.name} parsed to None"
    
    return True, "OK"


def validate_data_directory(dir_path: Path, 
                            min_files: int = 1,
                            extension: str = ".json") -> Tuple[bool, str]:
    """Validate a data directory has minimum expected files."""
    if not dir_path.exists():
        return False, f"Directory not found: {dir_path}"
    
    files = list(dir_path.glob(f"*{extension}"))
    if len(files) < min_files:
        return False, f"{dir_path.name}: only {len(files)} files (need ≥{min_files})"
    
    # Spot-check first 5 files parse
    for f in files[:5]:
        ok, msg = validate_json_file(f)
        if not ok:
            return False, msg
    
    return True, f"{dir_path.name}: {len(files)} valid files"
