#!/usr/bin/env python3
"""
Canonical field alias resolver for CMR template validation.

All enforcement scripts MUST use resolve_field() or normalize_template()
before accessing template data, to handle field name variants consistently.

Created: 2026-02-23
"""

import json
import os
import copy
from pathlib import Path

# Load aliases from schema
_ALIAS_PATH = Path(__file__).parent.parent / "schemas" / "field_aliases.json"

def _load_aliases():
    with open(_ALIAS_PATH) as f:
        data = json.load(f)
    return data.get("aliases", {})

_ALIASES = _load_aliases()

def resolve_field(template: dict, canonical_name: str, default=None):
    """
    Get a field value from a template, checking canonical name first,
    then all known aliases.

    Args:
        template: The template dict
        canonical_name: The canonical field name to look up
        default: Default value if not found

    Returns:
        The field value, or default if not found under any alias
    """
    # Check canonical name first
    if canonical_name in template:
        return template[canonical_name]

    # Check all aliases that map to this canonical name
    for alias, canon in _ALIASES.items():
        if canon == canonical_name and alias in template:
            return template[alias]

    return default


def normalize_template(template: dict, in_place: bool = False) -> dict:
    """
    Return a copy of the template with all aliased fields renamed to canonical names.
    Also normalizes mechanism_chain step-level fields.

    Args:
        template: The template dict
        in_place: If True, modify the original dict

    Returns:
        Normalized template dict
    """
    t = template if in_place else copy.deepcopy(template)

    # Rename top-level aliases
    for alias, canonical in _ALIASES.items():
        if alias in t and canonical not in t:
            t[canonical] = t.pop(alias)
        elif alias in t and canonical in t:
            # Both exist — keep canonical, remove alias
            del t[alias]

    # Normalize mechanism_chain steps
    mc = t.get("mechanism_chain", [])
    if isinstance(mc, list):
        for step in mc:
            if not isinstance(step, dict):
                continue
            # Normalize step-level aliases
            for alias, canonical in _ALIASES.items():
                if alias in step and canonical not in step:
                    step[canonical] = step.pop(alias)
                elif alias in step and canonical in step:
                    del step[alias]

    return t


def get_mechanism_chain(template: dict) -> list:
    """
    Safely get the mechanism chain from a template,
    handling the mechanism_steps alias and the corrupt int case.

    Returns:
        list of mechanism steps, or empty list if corrupt/missing
    """
    mc = resolve_field(template, "mechanism_chain")
    if isinstance(mc, list):
        return mc

    # Handle corrupt int case — check for 'steps' field as fallback
    steps = template.get("steps", [])
    if isinstance(steps, list) and steps:
        return steps

    return []


def get_confidence(template: dict) -> float:
    """Get confidence from any known alias."""
    return resolve_field(template, "confidence", default=None)


def get_bridge_warrant(template: dict) -> str:
    """Get bridge warrant from any known alias."""
    return resolve_field(template, "bridge_warrant", default=None)


def get_panel_source(template: dict) -> str:
    """Get panel source from any known alias."""
    return resolve_field(template, "panel_source", default=None)


def get_calibration_status(template: dict) -> str:
    """
    Get calibration status, handling all variants.
    Returns normalized status string or None.
    """
    status = resolve_field(template, "calibration_status")
    if status:
        return status.lower() if isinstance(status, str) else status

    # Check boolean 'calibrated' field
    if template.get("calibrated") is True:
        return "calibrated"

    return None


def is_calibrated(template: dict) -> bool:
    """Check if a template is calibrated, handling all field variants."""
    status = get_calibration_status(template)
    return status == "calibrated"
