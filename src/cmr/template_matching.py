"""Template matching module for paper evaluation (Doc 68 Part 3.2)."""

from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Any, Iterable

from src.cmr.models import TemplateRecord
from src.cmr.reduction_api import reduce_construct


REDUCTION_KEYWORDS = {
    # ART constructs
    "soft fascination": ("ART", "Fascination_Soft"),
    "soft fasc": ("ART", "Fascination_Soft"),
    "being away": ("ART", "Being_Away"),
    "compatibility": ("ART", "Compatibility"),
    "extent": ("ART", "Extent"),
    "hard fascination": ("ART", "Fascination_Hard"),
    "attention restoration": ("ART", "Being_Away"),
    # Biophilia constructs
    "nature in space": ("BIOPHILIA", "Nature_In_Space"),
    "nature_in_space": ("BIOPHILIA", "Nature_In_Space"),
    "natural analogues": ("BIOPHILIA", "Natural_Analogues"),
    "nature of space": ("BIOPHILIA", "Nature_Of_Space"),
    "remaining patterns": ("BIOPHILIA", "Remaining_Patterns"),
    "nature view": ("BIOPHILIA", "Nature_In_Space"),
    "nature_view": ("BIOPHILIA", "Nature_In_Space"),
    "tree view": ("BIOPHILIA", "Nature_In_Space"),
    "window view": ("BIOPHILIA", "Nature_In_Space"),
    # SRT constructs
    "stress recovery": ("SRT", "Autonomic_Stress_Reduction"),
    "stress reduction": ("SRT", "Autonomic_Stress_Reduction"),
    "recovery time": ("SRT", "Autonomic_Stress_Reduction"),
    "recovery_time": ("SRT", "Autonomic_Stress_Reduction"),
    "affective response": ("SRT", "Affective_Response"),
    "approach avoidance": ("SRT", "Approach_Avoidance"),
    "pain medication": ("SRT", "Autonomic_Stress_Reduction"),
    "analgesic": ("SRT", "Autonomic_Stress_Reduction"),
}


def _claim_text(claim: dict[str, Any]) -> str:
    parts = [
        str(claim.get("iv", "")),
        str(claim.get("dv", "")),
        str(claim.get("description", "")),
        str(claim.get("context", "")),
    ]
    return " ".join(part.lower() for part in parts if part).strip()


def _reduce_construct_from_claim(claim: dict[str, Any]) -> tuple[str, str] | None:
    text = _claim_text(claim)
    for keyword, value in REDUCTION_KEYWORDS.items():
        if keyword in text:
            return value
    return None


def match_claims_via_reduction(claims: list[dict], template_index: dict[str, dict]) -> list[dict]:
    results: list[dict] = []
    for claim in claims:
        match_info: list[dict] = []
        reduction_key = _reduce_construct_from_claim(claim)
        if reduction_key:
            reduction = reduce_construct(*reduction_key)
            if reduction:
                for mapping in reduction.get("template_mappings", []):
                    tid = mapping.get("template_id")
                    if not tid:
                        continue
                    coverage = float(mapping.get("coverage", 0.0) or 0.0)
                    match_info.append(
                        {
                            "template_id": tid,
                            "match_type": "reduction",
                            "confidence": min(1.0, max(0.0, coverage)),
                            "rationale": mapping.get("mechanism", "") or reduction.get("irreducible_residual", ""),
                        }
                    )
        results.append({"claim": claim, "matches": match_info})
    return results



_SYNONYM_GROUPS = [
    {"daylight", "illuminance", "light_level", "lux"},
    {"noise", "ambient_noise", "ambient_noise_dba"},
    {"nature_view", "has_nature_view", "view_quality", "green_view"},
    {"creative_thinking", "creative_output", "creativity"},
    {"stress_reduction", "stress", "cortisol_reduction"},
]


def _normalize_term(value: str | None) -> str:
    return str(value or "").strip().lower().replace("_", " ")


def _expand_term_candidates(term: str) -> set[str]:
    normalized = _normalize_term(term)
    if not normalized:
        return set()

    candidates = {normalized}
    normalized_key = normalized.replace(" ", "_")
    for group in _SYNONYM_GROUPS:
        normalized_group = {_normalize_term(item) for item in group}
        group_keys = {item.replace(" ", "_") for item in normalized_group}
        if normalized in normalized_group or normalized_key in group_keys:
            candidates.update(normalized_group)
    return candidates


def _fuzzy_match(term: str, target_list: Iterable[str], threshold: float = 0.8) -> str | None:
    """Find the best fuzzy match for a term in a target list."""
    if not term:
        return None
    term_candidates = _expand_term_candidates(term) or {_normalize_term(term)}

    best_match = None
    best_score = 0.0

    for target in target_list:
        normalized_target = _normalize_term(target)
        score = 0.0
        for candidate in term_candidates:
            if candidate in normalized_target or normalized_target in candidate:
                # Substring match boost
                candidate_score = 0.9 if len(candidate) > 3 else 0.7
            else:
                matcher = difflib.SequenceMatcher(None, candidate, normalized_target)
                candidate_score = matcher.ratio()
            score = max(score, candidate_score)

        if score > best_score and score >= threshold:
            best_score = score
            best_match = target

    return best_match


def build_template_index(template_records: Iterable[TemplateRecord]) -> dict[str, dict]:
    """
    Build an index of templates for matching.
    
    Returns:
        Dict mapping template_id to its index data:
        {
            "display_id": "VF3",
            "inputs": {"ceiling_height", "volume"},
            "outputs": {"processing_style", "creativity"},
            "mechanisms": "text description...",
            "json_data": full_json
        }
    """
    index = {}
    
    for record in template_records:
        json_path = Path(record.json_path)
        if not json_path.exists():
            continue
            
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue
            
        inputs = set()
        outputs = set()
        mechanisms = set()
        
        # Extract from causal_links
        # Handle loose schema: from_variable/from_entity, to_variable/to_entity
        for link in data.get("causal_links", []):
            # Inputs (Environmental level)
            if link.get("from_level") == "environmental":
                src = link.get("from_variable") or link.get("from_entity")
                if src:
                    inputs.add(src)
            
            # Outputs (Non-environmental levels: cognitive, affective, etc.)
            if link.get("to_level") in ["cognitive", "affective", "physiological", "behavioral", "neural"]:
                dst = link.get("to_variable") or link.get("to_entity")
                if dst:
                    outputs.add(dst)
        
        # Extract mechanism text for mechanistic matching
        if "structural_pattern" in data:
            mechanisms.add(data["structural_pattern"])
        if "higher_order_principle" in data:
            mechanisms.add(data["higher_order_principle"])
            
        index[record.display_id] = {
            "display_id": record.display_id,
            "inputs": inputs,
            "outputs": outputs,
            "mechanisms": " ".join(mechanisms).lower(),
            "json_data": data
        }
        
    return index


def match_claims_to_templates(
    claims: list[dict], 
    template_index: dict[str, dict],
    threshold: float = 0.65
) -> list[dict]:
    """
    Match extracted claims to templates.
    
    Args:
        claims: List of claim dicts {iv, dv, ...}
        template_index: Index from build_template_index
        threshold: Fuzzy match threshold
        
    Returns:
        List of results:
        [
            {
                "claim": original_claim_dict,
                "matches": [
                    {
                        "template_id": "VF3",
                        "match_type": "exact" | "partial_iv" | "partial_dv" | "mechanistic",
                        "confidence": float,
                        "rationale": str
                    },
                    ...
                ]
            }
        ]
    """
    results = []
    
    for claim in claims:
        iv = claim.get("iv") or claim.get("independent_variable")
        dv = claim.get("dv") or claim.get("dependent_variable")
        
        result_entry = {
            "claim": claim,
            "matches": []
        }
        
        for tmpl_id, tmpl_data in template_index.items():
            # Check IV match (Input)
            iv_match = _fuzzy_match(iv, tmpl_data["inputs"], threshold)
            
            # Check DV match (Output)
            dv_match = _fuzzy_match(dv, tmpl_data["outputs"], threshold)
            
            match_type = "none"
            confidence = 0.0
            rationale = ""
            
            if iv_match and dv_match:
                match_type = "exact"
                confidence = 0.9
                rationale = f"Exact match: IV '{iv}' matches input '{iv_match}' AND DV '{dv}' matches output '{dv_match}'"
            elif iv_match:
                match_type = "partial_iv"
                confidence = 0.6
                rationale = f"Partial match: IV '{iv}' matches input '{iv_match}'"
            elif dv_match:
                match_type = "partial_dv"
                confidence = 0.5
                rationale = f"Partial match: DV '{dv}' matches output '{dv_match}'"
            else:
                # Mechanistic text search (fallback)
                mech_text = tmpl_data["mechanisms"]
                iv_in_mech = iv and iv.lower() in mech_text
                dv_in_mech = dv and dv.lower() in mech_text
                
                if iv_in_mech or dv_in_mech:
                    match_type = "mechanistic"
                    confidence = 0.4
                    rationale = "Claim variables found in template mechanism description"
            
            if match_type != "none":
                result_entry["matches"].append({
                    "template_id": tmpl_id,
                    "match_type": match_type,
                    "confidence": confidence,
                    "match_score": confidence,
                    "rationale": rationale,
                    "details": {
                        "iv_match": iv_match,
                        "dv_match": dv_match
                    }
                })
        
        # Sort matches by confidence
        result_entry["matches"].sort(key=lambda x: x["confidence"], reverse=True)
        results.append(result_entry)
        
    return results
