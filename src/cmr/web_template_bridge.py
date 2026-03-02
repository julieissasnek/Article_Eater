"""Bridge between the web of belief and Tier 1 templates (Sprint 12 Task 12.18)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional

from src.cmr.reduction_api import find_template_theories, reduce_theory
from src.services.db_locator import resolve_web_db
from src.services.web_persistence import WebPersistenceService

try:
    DEFAULT_DB = resolve_web_db(prefer="integrated")
except Exception:
    DEFAULT_DB = Path("data/web_persistence.db")  # Static fallback


def _normalize_theory(theory: Optional[str]) -> str:
    if not theory:
        return ""
    return theory.strip().upper()


def _master_web_id(service: WebPersistenceService) -> str:
    return service.create_or_get_master_web()


def get_beliefs_for_template(
    template_id: str,
    *,
    service: WebPersistenceService | None = None,
    db_path: Path | str | None = None,
) -> List[Any]:
    service = service or WebPersistenceService(str(db_path or DEFAULT_DB))
    web_id = _master_web_id(service)
    beliefs = service.get_beliefs_for_web(web_id)
    theories = { _normalize_theory(theory) for theory, _ in find_template_theories(template_id) }
    result: List[Any] = []
    for belief in beliefs:
        if _normalize_theory(belief.theory_id) in theories:
            result.append(belief)
            continue
        if template_id.lower() in (belief.content or "").lower():
            result.append(belief)
    return result


def get_templates_for_belief(
    belief_id: str,
    *,
    service: WebPersistenceService | None = None,
    db_path: Path | str | None = None,
) -> List[str]:
    service = service or WebPersistenceService(str(db_path or DEFAULT_DB))
    web_id = _master_web_id(service)
    belief = service.load_belief(belief_id, web_id)
    if belief is None:
        return []
    theory = _normalize_theory(belief.theory_id)
    reductions = reduce_theory(theory)
    templates: List[str] = []
    for reduction in reductions:
        for mapping in reduction.get("template_mappings", []):
            tid = mapping.get("template_id")
            if tid:
                templates.append(tid)
    return sorted(set(templates))


@dataclass
class EvidenceStrength:
    supporting: int
    contradicting: int
    neutral: int
    total: int
    ratio: float


def get_evidence_strength(
    template_id: str,
    *,
    service: WebPersistenceService | None = None,
    db_path: Path | str | None = None,
) -> EvidenceStrength:
    beliefs = get_beliefs_for_template(template_id, service=service, db_path=db_path)
    supporting = sum(getattr(b.credence, "n_supporting", 0) for b in beliefs)
    contradicting = sum(getattr(b.credence, "n_contradicting", 0) for b in beliefs)
    total = len(beliefs)
    neutral = max(0, total - supporting - contradicting)
    ratio = supporting / max(1, supporting + contradicting) if supporting + contradicting else 0.0
    return EvidenceStrength(
        supporting=supporting,
        contradicting=contradicting,
        neutral=neutral,
        total=total,
        ratio=ratio,
    )


__all__ = [
    "EvidenceStrength",
    "get_beliefs_for_template",
    "get_templates_for_belief",
    "get_evidence_strength",
]
