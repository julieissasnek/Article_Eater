"""Reduction lookup helpers (Sprint 12 Task 12.5)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

RECAP_DIR = Path("data/reductions")


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


@lru_cache(maxsize=1)
def _load_reduction_catalog() -> Dict[Tuple[str, str], dict[str, Any]]:
    catalog: Dict[Tuple[str, str], dict[str, Any]] = {}
    for file in sorted(RECAP_DIR.glob("*.json")):
        try:
            payload = json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            continue
        theory = payload.get("tier2_theory") or payload.get("theory") or ""
        construct = payload.get("tier2_construct")
        if not theory and payload.get("full_name"):
            theory = payload.get("full_name")
        if not theory:
            continue
        constructs = payload.get("constructs") or {}
        if construct:
            constructs = {construct: constructs.get(construct, {})}
        for name, detail in constructs.items():
            key = (_normalize_key(theory), _normalize_key(name))
            catalog[key] = {
                "theory": theory,
                "construct": name,
                "coverage": detail.get("total_coverage") or detail.get("coverage") or 0.0,
                "template_mappings": detail.get("template_mappings", []),
                "irreducible_residual": detail.get("irreducible_residual") or detail.get("irreducible_residual", ""),
                "confidence": detail.get("confidence") or payload.get("confidence"),
                "notes": detail.get("notes"),
                "source": str(file),
            }
    return catalog


def reduce_construct(theory: str, construct: str) -> Optional[dict[str, Any]]:
    """Return the reduction mapping for a given theory construct."""
    key = (_normalize_key(theory), _normalize_key(construct))
    catalog = _load_reduction_catalog()
    return catalog.get(key)


def reduce_theory(theory: str) -> List[dict[str, Any]]:
    """Return all reductions associated with a Tier 2 theory."""
    norm = _normalize_key(theory)
    catalog = _load_reduction_catalog()
    return [value for (t, _), value in catalog.items() if t == norm]


def find_template_theories(template_id: str) -> List[Tuple[str, str]]:
    """Find all Tier 2 theory constructs that reference a template."""
    norm = template_id.strip().upper()
    catalog = _load_reduction_catalog()
    results: List[Tuple[str, str]] = []
    for value in catalog.values():
        for mapping in value.get("template_mappings", []):
            if mapping.get("template_id", "").strip().upper() == norm:
                results.append((value["theory"], value["construct"]))
    return results


def get_reduction_coverage_summary() -> dict[str, Any]:
    """Return summary stats over the available reductions."""
    catalog = _load_reduction_catalog()
    by_theory: Dict[str, List[float]] = {}
    for (theory, _), value in catalog.items():
        by_theory.setdefault(theory, []).append(value.get("coverage", 0.0) or 0.0)
    summary = {
        theory: {
            "constructs": len([1 for (t, _) in catalog.keys() if t == theory]),
            "mean_coverage": (sum(values) / len(values)) if values else 0.0,
        }
        for theory, values in by_theory.items()
    }
    return {
        "total_constructs": len(catalog),
        "theory_summary": summary,
    }


__all__ = [
    "reduce_construct",
    "reduce_theory",
    "find_template_theories",
    "get_reduction_coverage_summary",
]
