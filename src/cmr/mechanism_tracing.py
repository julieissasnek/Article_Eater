"""Mechanism tracing module for paper evaluation (Doc 68 Part 3.3)."""

from __future__ import annotations

import json
import re
from typing import Any

# Focus on relationship verbs/adverbs, ignoring state adjectives like
# "high"/"low" to avoid confusing direction heuristics.
POSITIVE_KEYWORDS = {
    "increase",
    "increases",
    "increased",
    "enhance",
    "enhances",
    "enhanced",
    "more",
    "positive",
    "facilitate",
    "facilitates",
    "facilitated",
    "promote",
    "promotes",
    "promoted",
    "improve",
    "improves",
    "improved",
    "boost",
    "boosts",
    "boosted",
    "better",
    "primes",
    "activates",
    "supports",
}
NEGATIVE_KEYWORDS = {
    "decrease",
    "decreases",
    "decreased",
    "reduce",
    "reduces",
    "reduced",
    "lower",
    "lowered",
    "less",
    "negative",
    "inhibit",
    "inhibits",
    "inhibited",
    "impair",
    "impairs",
    "impaired",
    "suppress",
    "suppresses",
    "suppressed",
    "diminish",
    "diminishes",
    "diminished",
    "worse",
    "attenuates",
    "attenuated",
    "avoids",
    "avoided",
    "prevent",
    "prevents",
    "prevented",
}


def extract_direction(text: str) -> str:
    """
    Heuristic extraction of effect direction from text.
    Returns: "positive", "negative", or "unknown"
    """
    if not text:
        return "unknown"

    words = set(re.findall(r"\w+", text.lower()))
    pos_score = sum(1 for keyword in POSITIVE_KEYWORDS if keyword in words)
    neg_score = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword in words)

    if pos_score > neg_score:
        return "positive"
    if neg_score > pos_score:
        return "negative"
    return "unknown"


def _find_relevant_link(iv: str, dv: str, template_data: dict) -> dict | None:
    """Find the causal link in the template that most directly connects IV->DV."""
    links = template_data.get("causal_links", [])
    for link in links:
        src = str(link.get("from_variable") or link.get("from_entity") or "")
        dst = str(link.get("to_variable") or link.get("to_entity") or "")
        iv_in_src = iv.lower() in src.lower() or src.lower() in iv.lower()
        dv_in_dst = dv.lower() in dst.lower() or dst.lower() in dv.lower()
        if iv_in_src and dv_in_dst:
            return link
    
    chain = template_data.get("mechanism_chain", [])
    if isinstance(chain, list):
        for step in chain:
            if isinstance(step, dict):
                src = str(step.get("from") or "")
                dst = str(step.get("to") or "")
                iv_in_src = iv.lower() in src.lower() or src.lower() in iv.lower()
                dv_in_dst = dv.lower() in dst.lower() or dst.lower() in dv.lower()
                if iv_in_src and dv_in_dst:
                    return step
    
    return None


def _moderator_text(template_data: dict[str, Any]) -> str:
    fields = [
        template_data.get("lifespan_moderation"),
        template_data.get("climate_context"),
        template_data.get("scope_conditions"),
        template_data.get("moderators"),
    ]
    parts: list[str] = []
    for field in fields:
        if field is None:
            continue
        if isinstance(field, str):
            parts.append(field)
        else:
            parts.append(json.dumps(field, ensure_ascii=True))
    return " ".join(parts).lower()


def _assess_moderator_match(claim: dict[str, Any], template_data: dict[str, Any]) -> tuple[str, str]:
    population = str(
        claim.get("population")
        or claim.get("sample_population")
        or claim.get("occupant_group")
        or ""
    ).strip().lower()
    context = str(claim.get("context") or claim.get("setting") or "").strip().lower()

    if not population and not context:
        return "partial", "Claim provides no explicit population/context moderators."

    mod_text = _moderator_text(template_data)
    checks: list[bool] = []
    if population:
        checks.append(population in mod_text)
    if context:
        checks.append(context in mod_text)

    if checks and all(checks):
        return "full", "Claim moderators align with template moderation/scope fields."
    if checks and any(checks):
        return "partial", "Some claim moderators align; others are not represented."
    return "mismatch", "Claim moderators are not represented in template moderation/scope."


def _block_assessment(
    claim: dict[str, Any],
    template_id: str,
    template_data: dict[str, Any],
) -> str:
    links = template_data.get("causal_links", [])
    if links:
        link = links[0]
        source = link.get("from_variable") or link.get("from_entity") or claim.get("iv") or "input"
        target = link.get("to_variable") or link.get("to_entity") or claim.get("dv") or "output"
        return (
            f"Mechanism path: {source} -> {target}. "
            f"If {source} is blocked, the {template_id} pathway predicts attenuation of {target}."
        )
    iv = claim.get("iv") or "input"
    dv = claim.get("dv") or "output"
    return (
        f"Mechanism path for {template_id} is underspecified. "
        f"If the {iv} pathway is blocked, expected {dv} effect should weaken."
    )


def _confidence_band(
    match_confidence: float,
    moderator_match: str,
    has_alternatives: bool,
) -> str:
    adjusted = match_confidence
    if moderator_match == "mismatch":
        adjusted -= 0.25
    elif moderator_match == "partial":
        adjusted -= 0.1
    if has_alternatives:
        adjusted -= 0.05

    if adjusted >= 0.75:
        return "high"
    if adjusted >= 0.45:
        return "moderate"
    return "low"


def trace_mechanisms(claim_template_matches: list[dict]) -> list[dict]:
    """
    For each claim-template match, apply SUBSTITUTE, VARY_MOD, and BLOCK checks.

    Returns one traced record per claim-template pair.
    """
    traced: list[dict[str, Any]] = []
    for claim_entry in claim_template_matches:
        claim = claim_entry.get("claim", {})
        matches = claim_entry.get("matches", []) or []

        template_ids = [m.get("template_id") for m in matches if m.get("template_id")]
        for match in matches:
            template_id = str(match.get("template_id") or "")
            if not template_id:
                continue

            template_data = match.get("template_data", {}) or {}
            alternatives = [tid for tid in template_ids if tid and tid != template_id]
            moderator_match, moderator_details = _assess_moderator_match(claim, template_data)
            block = _block_assessment(claim, template_id, template_data)
            match_conf = float(match.get("match_score", match.get("confidence", 0.0)) or 0.0)

            traced.append(
                {
                    "claim": claim,
                    "template": template_id,
                    "match_type": match.get("match_type"),
                    "match_score": match_conf,
                    "status": match.get("trace_status", "supported"),
                    "substitute_alternatives": alternatives,
                    "moderator_match": moderator_match,
                    "moderator_details": moderator_details,
                    "block_assessment": block,
                    "overall_confidence": _confidence_band(
                        match_confidence=match_conf,
                        moderator_match=moderator_match,
                        has_alternatives=bool(alternatives),
                    ),
                }
            )
    return traced


def trace_claim(claim: dict, template_data: dict) -> dict:
    """
    Trace a claim against a template to determine support status.

    Args:
        claim: Dict with {"description": str, "iv": str, "dv": str}
        template_data: Template JSON data

    Returns:
        {
            "status": "supported" | "contradicted" | "novel" | "nuanced",
            "confidence": float,
            "reasoning": str
        }
    """
    claim_desc = claim.get("description", "") or (
        f"{claim.get('iv', '')} {claim.get('relationship', '')} {claim.get('direction', '')} {claim.get('dv', '')}"
    )
    claim_direction = extract_direction(claim_desc)

    if claim_direction == "unknown":
        return {
            "status": "nuanced",
            "confidence": 0.3,
            "reasoning": "Could not determine direction of claim effect.",
        }

    iv = claim.get("iv") or claim.get("independent_variable")
    dv = claim.get("dv") or claim.get("dependent_variable")
    link = _find_relevant_link(iv, dv, template_data)

    if link:
        notes = link.get("notes", "") or link.get("description", "") or link.get("mechanism", "") or link.get("evidence_base", "")
        activity = link.get("activity", "")
        template_text = f"{activity} {notes}"
        template_direction = extract_direction(template_text)
    else:
        structural = template_data.get("structural_pattern", "")
        if not structural:
            chain = template_data.get("mechanism_chain", [])
            chain_texts = []
            if isinstance(chain, list):
                for step in chain:
                    if isinstance(step, dict):
                        chain_texts.append(str(step.get("description") or step.get("mechanism") or step.get("notes") or ""))
                    elif isinstance(step, str):
                        chain_texts.append(step)
            structural = " ".join(chain_texts)
        template_direction = extract_direction(structural)

    if template_direction == "unknown":
        return {
            "status": "nuanced",
            "confidence": 0.3,
            "reasoning": "Could not determine template mechanism direction.",
        }

    if claim_direction == template_direction:
        return {
            "status": "supported",
            "confidence": 0.8,
            "reasoning": f"Both claim and template indicate {claim_direction} relationship.",
        }
    return {
        "status": "contradicted",
        "confidence": 0.7,
        "reasoning": (
            f"Claim indicates {claim_direction} effect, "
            f"but template indicates {template_direction} effect."
        ),
    }


__all__ = [
    "extract_direction",
    "trace_claim",
    "trace_mechanisms",
]
