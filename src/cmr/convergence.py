"""Convergence and composition modules for paper evaluation (Doc 68 Part 3.4)."""

from __future__ import annotations

from typing import Any

from src.cmr.interactions import get_interaction


def _claim_key(claim: dict[str, Any]) -> str:
    if claim.get("claim_id"):
        return str(claim["claim_id"])
    return str(sorted(claim.items()))


def _normalize_traced_claims(traced_claims: list[dict]) -> list[dict]:
    """
    Accept both supported input shapes:
    1) [{claim, traced_templates:[...]}]
    2) Flat mechanism traces [{claim, template, status, ...}, ...]
    """
    if not traced_claims:
        return []
    if "traced_templates" in traced_claims[0]:
        return traced_claims

    grouped: dict[str, dict[str, Any]] = {}
    for row in traced_claims:
        claim = row.get("claim", {})
        key = _claim_key(claim)
        if key not in grouped:
            grouped[key] = {
                "claim": claim,
                "traced_templates": [],
            }
        grouped[key]["traced_templates"].append(
            {
                "template_id": row.get("template") or row.get("template_id"),
                "status": row.get("status", "supported"),
                "confidence": row.get("match_score", row.get("confidence", 0.0)),
            }
        )
    return list(grouped.values())


def assess_convergence(traced_claims: list[dict]) -> list[dict]:
    """
    Assess convergence of supporting mechanisms for each claim.
    
    Args:
        traced_claims: List of claims with 'matches' and 'trace_result' (merged).
        
    Returns:
        List of claims with added 'convergence' dict.
    """
    normalized = _normalize_traced_claims(traced_claims)
    results = []

    for claim_entry in normalized:
        traced_templates = claim_entry.get("traced_templates", [])

        supported_count = 0
        contradiction_found = False
        supporting_ids = []
        contradicting_ids = []

        for trace in traced_templates:
            status = trace.get("status")
            if status == "supported":
                supported_count += 1
                supporting_ids.append(trace.get("template_id"))
            elif status == "contradicted":
                contradiction_found = True
                contradicting_ids.append(trace.get("template_id"))

        convergence_status = "unsupported"
        reasoning = "No matching templates found."

        if contradiction_found:
            convergence_status = "contradicted"
            reasoning = f"Contradicted by {', '.join(contradicting_ids)}."
        elif supported_count >= 3:
            convergence_status = "strong"
            reasoning = f"Supported by {supported_count} independent mechanisms ({', '.join(supporting_ids)})."
        elif supported_count == 2:
            convergence_status = "moderate"
            reasoning = f"Supported by 2 mechanisms ({', '.join(supporting_ids)})."
        elif supported_count == 1:
            convergence_status = "single_mechanism"
            reasoning = f"Supported by single mechanism ({supporting_ids[0]})."
            
        claim_entry["convergence"] = {
            "status": convergence_status,
            "supporting_templates": supporting_ids,
            "contradicting_templates": contradicting_ids,
            "reasoning": reasoning,
        }
        results.append(claim_entry)

    return results


def check_composition_failures(traced_claims: list[dict]) -> list[dict]:
    """
    Detect potential composition failures where multi-template claims 
    violate known interaction rules (e.g. sub-additivity).
    """
    normalized = _normalize_traced_claims(traced_claims)
    if normalized and "convergence" not in normalized[0]:
        normalized = assess_convergence(normalized)

    for claim_entry in normalized:
        convergence = claim_entry.get("convergence", {})
        supporting = convergence.get("supporting_templates", [])

        composition_warnings = []

        if len(supporting) >= 2:
            # Check interactions between supporting templates
            from itertools import combinations
            for t1, t2 in combinations(supporting, 2):
                interaction = get_interaction(t1, t2)
                if interaction:
                    # Check for sub-additivity warnings
                    if interaction.get("sub_additivity", 1.0) < 1.0:
                        warning = {
                            "pair": f"{t1}+{t2}",
                            "type": "sub_additivity",
                            "message": (
                                f"Templates {t1} and {t2} have sub-additive interaction "
                                f"({interaction['sub_additivity']}). Verify paper accounts "
                                "for diminishing returns."
                            ),
                        }
                        composition_warnings.append(warning)

                    # Check for interference/penalty
                    if interaction.get("convergent_penalty", 1.0) > 1.0:
                        warning = {
                            "pair": f"{t1}+{t2}",
                            "type": "interference",
                            "message": (
                                f"Templates {t1} and {t2} have interference penalty "
                                f"({interaction['convergent_penalty']}). Verify paper "
                                "addresses this trade-off."
                            ),
                        }
                        composition_warnings.append(warning)

        claim_entry["composition_analysis"] = {
            "warnings": composition_warnings,
            "status": "warning" if composition_warnings else "clean",
        }

    return normalized
