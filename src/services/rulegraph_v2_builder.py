"""RuleGraph v2 builder.

This module translates Seven-Panel v2 bundles into RuleGraph v2 rule
objects that conform to schemas/rule_graph.schema.json.

Design goals:
- Keep the mapping simple and conservative.
- Make subject_scope and subject_moderators explicit per rule.
- Stay additive: existing RuleGraph v1 / Seven-Panel flows remain untouched.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.contracts.schemas import (
    SevenPanelV2Bundle,
    PanelHeterogeneity,
)

# Optional: Outcome resolver integration (if lib.outcome_resolver is available)
try:
    from lib.outcome_resolver import resolve_or_queue
    _HAS_OUTCOME_RESOLVER = True
except ImportError:
    _HAS_OUTCOME_RESOLVER = False


def _resolve_outcome_id(raw_id, paper_id=None):
    """Resolve outcome ID through Outcome_Contractor if available."""
    if _HAS_OUTCOME_RESOLVER:
        try:
            result = resolve_or_queue(str(raw_id), paper_id=paper_id)
            return result['canonical_id']
        except Exception:
            pass
    return str(raw_id)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_subject_scope(bundle: SevenPanelV2Bundle) -> Optional[Dict[str, Any]]:
    if not bundle.subjects or not bundle.subjects.sample:
        return None
    # Pydantic model -> plain dict, ready to validate against SubjectScope schema.
    return bundle.subjects.sample.dict(exclude_none=True)


def _build_moderators_map(
    heterogeneity: Optional[PanelHeterogeneity],
) -> Dict[str, List[Dict[str, Any]]]:
    """Group moderation patterns by finding_id, ready for RuleGraph v2.

    Each entry is shaped to match $defs/SubjectModerator in the JSON schema.
    """
    out: Dict[str, List[Dict[str, Any]]] = {}
    if not heterogeneity or not heterogeneity.moderation_patterns:
        return out

    for pat in heterogeneity.moderation_patterns:
        rec = {
            "attribute": pat.moderator,
            "dimension": pat.dimension,
            "levels": pat.levels_compared or None,
            "pattern": pat.pattern,
            "evidence_ids": [pat.finding_id],
        }
        out.setdefault(pat.finding_id, []).append(rec)
    return out


def _build_theory_links(
    bundle: SevenPanelV2Bundle,
) -> Optional[List[Dict[str, Any]]]:
    """Extract theory links from mechanism claims (T7.3).

    Each MechanismClaim with a non-null ``theory`` field becomes a TheoryLink
    entry conforming to $defs/TheoryLink in rule_graph.schema.json.
    """
    if not bundle.mechanisms or not bundle.mechanisms.mechanism_claims:
        return None

    links: List[Dict[str, Any]] = []
    seen_theories: set = set()

    for claim in bundle.mechanisms.mechanism_claims:
        if not claim.theory:
            continue
        # Deduplicate by theory name within a single bundle
        theory_key = claim.theory.strip().lower()
        if theory_key in seen_theories:
            continue
        seen_theories.add(theory_key)

        link: Dict[str, Any] = {
            "theory_id": claim.theory.strip(),
        }
        if claim.phenomenon:
            link["from_variable"] = claim.phenomenon
        if claim.role:
            link["activity"] = claim.role
        if claim.strength:
            # Map strength to maturity
            strength_to_maturity = {
                "strong": "established",
                "moderate": "supported",
                "weak": "speculative",
            }
            link["maturity"] = strength_to_maturity.get(
                claim.strength.lower(), "unknown"
            )
        links.append(link)

    return links or None


def build_rulegraph_v2_rules(
    paper_id: str,
    bundle: SevenPanelV2Bundle,
) -> List[Dict[str, Any]]:
    """Construct a list of RuleGraph v2 rule dicts from a SevenPanelV2Bundle.

    This is intentionally conservative:

    - We focus on rule_text + subject_scope + subject_moderators +
      per-finding evidence, leaving factor_nodes/outcome_nodes for
      future, more structured passes.
    - Factors/outcomes string lists are left empty for now but present,
      to satisfy the schema and keep room for future enrichment.
    """
    rules: List[Dict[str, Any]] = []

    if not bundle.findings or not bundle.findings.items:
        return rules

    subject_scope = _build_subject_scope(bundle)
    moderators_map = _build_moderators_map(bundle.heterogeneity)
    theory_links = _build_theory_links(bundle)

    for finding in bundle.findings.items:
        finding_id = finding.finding_id
        evidence_entry: Dict[str, Any] = {
            "finding_id": finding_id,
            "statistics": finding.statistics.dict(exclude_none=True)
            if finding.statistics
            else None,
            "quote": finding.quote,
            "page_span": finding.page_span,
            "task_id": finding.task_id,
            "indicator_ids": finding.indicator_ids,
        }

        subject_moderators = moderators_map.get(finding_id, [])

        rule = {
            "rule_id": f"{paper_id}:{finding_id}",
            "status": "prima_facie",
            "rule_text": finding.finding_text,
            # For now we keep these empty; future passes will parse explicit
            # environment/subject nodes and populate them.
            "factors": [],
            "outcomes": [],
            "provenance": {
                "paper_id": paper_id,
                "source": "SevenPanelV2",
                "provider": bundle.provider,
                "model": bundle.model,
            },
            "evidence": [evidence_entry],
            "subject_scope": subject_scope,
            "subject_moderators": subject_moderators or None,
            "theory_links": theory_links,
            "tags": bundle.tags or (bundle.context.tags if bundle.context else None),
            "graph_version": "2.0",
            "created_at": _now_iso(),
        }
        rules.append(rule)

    return rules

