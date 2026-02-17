"""Claim extraction module for paper evaluation (Sprint 11 Task 11.6)."""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any


_POSITIVE_VERBS = {
    "increase",
    "increases",
    "increased",
    "enhance",
    "enhances",
    "enhanced",
    "promote",
    "promotes",
    "improve",
    "improves",
    "boost",
    "boosts",
    "raise",
    "raises",
    "elevate",
    "elevates",
    "affect",
    "affects",
    "cause",
    "causes",
    "lead to",
    "leads to",
    "result in",
    "results in",
}

_NEGATIVE_VERBS = {
    "decrease",
    "decreases",
    "decreased",
    "reduce",
    "reduces",
    "reduced",
    "lower",
    "lowers",
    "lowered",
    "inhibit",
    "inhibits",
    "impair",
    "impairs",
    "suppress",
    "suppresses",
}

_COMPARATIVE_TO_DIRECTION = {
    "shorter": "negative",
    "less": "negative",
    "lower": "negative",
    "longer": "positive",
    "more": "positive",
    "higher": "positive",
}

_STOPWORDS = {
    "the",
    "a",
    "an",
    "of",
    "and",
    "for",
    "to",
    "in",
    "on",
    "with",
    "by",
    "at",
    "from",
    "that",
    "this",
}

_SYNONYMS = {
    "nature views": "has_nature_view",
    "view of nature": "has_nature_view",
    "nature view": "has_nature_view",
    "high ceilings": "ceiling_height_m",
    "ceiling height": "ceiling_height_m",
    "noise": "ambient_noise_dba",
    "ambient noise": "ambient_noise_dba",
    "stress": "stress",
    "stress levels": "stress",
    "recovery time": "recovery_time",
    "recovery times": "recovery_time",
    "pain medication": "pain_medication_use",
    "pain medication use": "pain_medication_use",
}

_RELATION_PATTERN = re.compile(
    r"(?P<iv>[A-Za-z][\w\s/-]{1,80}?)\s+"
    r"(?P<rel>increases?|increased|enhances?|enhanced|promotes?|improves?|boosts?|"
    r"decreases?|decreased|reduces?|reduced|lowers?|lowered|affects?|causes?|"
    r"leads?\s+to|results?\s+in)\s+"
    r"(?P<dv>[A-Za-z][\w\s/-]{1,120})",
    flags=re.IGNORECASE,
)

_WITH_COMPARATIVE_PATTERN = re.compile(
    r"(?:with|in)\s+(?P<iv>[A-Za-z][\w\s/-]{1,80}?)\s+"
    r"(?:had|showed|experienced|reported|exhibited)\s+"
    r"(?P<comp>shorter|longer|less|more|lower|higher)\s+"
    r"(?P<dv>[A-Za-z][\w\s/-]{1,120})",
    flags=re.IGNORECASE,
)

_AND_REQUIRED_COMPARATIVE_PATTERN = re.compile(
    r"(?:and|,)\s+(?:required|reported|showed|had)?\s*"
    r"(?P<comp>shorter|longer|less|more|lower|higher)\s+"
    r"(?P<dv>[A-Za-z][\w\s/-]{1,120})",
    flags=re.IGNORECASE,
)


def _normalize(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s_]", " ", str(text).lower())
    tokens = [tok for tok in cleaned.split() if tok and tok not in _STOPWORDS]
    return " ".join(tokens)


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_direction(raw: Any) -> str:
    value = str(raw or "").strip().lower()
    if value in {"positive", "increase", "increases", "higher", "more"}:
        return "positive"
    if value in {"negative", "decrease", "decreases", "lower", "less", "reduce", "reduces"}:
        return "negative"
    if value in _POSITIVE_VERBS:
        return "positive"
    if value in _NEGATIVE_VERBS:
        return "negative"
    return "unknown"


@lru_cache(maxsize=1)
def _load_template_vocabulary() -> dict[str, Any]:
    """
    Build extraction vocabulary from template JSON files.

    Returns:
      {
        "variables": set[str],
        "variable_to_templates": dict[str, list[str]]
      }
    """
    variables: set[str] = set()
    variable_to_templates: dict[str, set[str]] = {}
    templates_dir = Path("data/templates")

    if not templates_dir.exists():
        return {"variables": variables, "variable_to_templates": {}}

    for json_path in templates_dir.glob("*.json"):
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        template_id = str(payload.get("display_id") or payload.get("template_id") or json_path.stem)
        candidates: set[str] = set()

        for item in payload.get("inputs_required", []) or []:
            if isinstance(item, str):
                candidates.add(item)

        for link in payload.get("causal_links", []) or []:
            if not isinstance(link, dict):
                continue
            for key in ("from_variable", "from_entity", "to_variable", "to_entity"):
                value = link.get(key)
                if isinstance(value, str):
                    candidates.add(value)

        for value in candidates:
            norm = _normalize(value)
            if not norm:
                continue
            variables.add(norm)
            variable_to_templates.setdefault(norm, set()).add(template_id)

    # Add known aliases that commonly appear in abstracts
    for alias, canonical in _SYNONYMS.items():
        alias_norm = _normalize(alias)
        canonical_norm = _normalize(canonical)
        if alias_norm:
            variables.add(alias_norm)
        if canonical_norm:
            variables.add(canonical_norm)
            variable_to_templates.setdefault(alias_norm, set()).update(
                variable_to_templates.get(canonical_norm, set())
            )

    return {
        "variables": variables,
        "variable_to_templates": {k: sorted(v) for k, v in variable_to_templates.items()},
    }


def _map_variable(term: str) -> dict[str, Any]:
    vocab = _load_template_vocabulary()
    variables: set[str] = vocab["variables"]
    variable_to_templates: dict[str, list[str]] = vocab["variable_to_templates"]

    raw = str(term).strip()
    normalized = _normalize(raw)
    if not normalized:
        return {
            "raw": raw,
            "mapped": None,
            "mapping_status": "novel_variable",
            "mapping_score": 0.0,
            "candidate_templates": [],
        }

    if normalized in _SYNONYMS:
        synonym_target = _normalize(_SYNONYMS[normalized])
        return {
            "raw": raw,
            "mapped": synonym_target,
            "mapping_status": "mapped",
            "mapping_score": 1.0,
            "candidate_templates": variable_to_templates.get(synonym_target, []),
        }

    if normalized in variables:
        return {
            "raw": raw,
            "mapped": normalized,
            "mapping_status": "mapped",
            "mapping_score": 1.0,
            "candidate_templates": variable_to_templates.get(normalized, []),
        }

    best_match = None
    best_score = 0.0
    for candidate in variables:
        if normalized in candidate or candidate in normalized:
            score = 0.9
        else:
            score = SequenceMatcher(None, normalized, candidate).ratio()
        if score > best_score:
            best_score = score
            best_match = candidate

    if best_match and best_score >= 0.82:
        return {
            "raw": raw,
            "mapped": best_match,
            "mapping_status": "mapped",
            "mapping_score": round(best_score, 3),
            "candidate_templates": variable_to_templates.get(best_match, []),
        }

    return {
        "raw": raw,
        "mapped": None,
        "mapping_status": "novel_variable",
        "mapping_score": round(best_score, 3),
        "candidate_templates": [],
    }


def _build_claim(
    *,
    iv: str,
    dv: str,
    direction: str,
    relationship: str,
    sentence: str,
    source: str,
    base_confidence: float,
) -> dict[str, Any]:
    iv_map = _map_variable(iv)
    dv_map = _map_variable(dv)
    confidence = min(
        0.95,
        max(0.3, base_confidence + 0.15 * iv_map["mapping_score"] + 0.15 * dv_map["mapping_score"]),
    )

    return {
        "iv": iv.strip(),
        "dv": dv.strip(),
        "independent_variable": iv.strip(),
        "dependent_variable": dv.strip(),
        "direction": direction,
        "relationship": relationship,
        "confidence": round(confidence, 3),
        "source": source,
        "context": sentence.strip(),
        "description": sentence.strip(),
        "iv_mapped_to": iv_map["mapped"],
        "iv_mapping_status": iv_map["mapping_status"],
        "dv_mapped_to": dv_map["mapped"],
        "dv_mapping_status": dv_map["mapping_status"],
        "candidate_templates": sorted(
            set(iv_map["candidate_templates"]) | set(dv_map["candidate_templates"])
        ),
    }


def extract_claims_structured(claims: list[dict]) -> list[dict]:
    """
    Validate and normalize pre-structured claims.

    Required fields: independent_var / iv, dependent_var / dv.
    Optional: direction, effect_size, sample_n, context.
    """
    normalized: list[dict] = []
    for claim in claims:
        iv = claim.get("independent_var") or claim.get("independent_variable") or claim.get("iv")
        dv = claim.get("dependent_var") or claim.get("dependent_variable") or claim.get("dv")
        if not iv or not dv:
            continue

        direction = _normalize_direction(claim.get("direction"))
        iv_text = str(iv).strip()
        dv_text = str(dv).strip()
        context = str(claim.get("context") or "")
        relationship = str(claim.get("relationship") or claim.get("direction") or "reported_effect")
        description = str(claim.get("description") or f"{iv_text} {relationship} {dv_text}")

        normalized.append(
            {
                **_build_claim(
                    iv=iv_text,
                    dv=dv_text,
                    direction=direction,
                    relationship=relationship,
                    sentence=description if description else context,
                    source="structured_input",
                    base_confidence=0.9,
                ),
                "effect_size": _safe_float(claim.get("effect_size")),
                "sample_n": _safe_int(claim.get("sample_n")),
            }
        )
    return normalized


def extract_claims_from_text(text: str) -> list[dict]:
    """
    Extract causal claims from paper text.

    Uses regex heuristics and maps extracted variables onto template vocabulary.
    Unmapped variables are flagged as `novel_variable`.
    """
    claims: list[dict] = []
    sentences = [seg.strip() for seg in re.split(r"[.!?]\s+", text) if seg.strip()]

    for sentence in sentences:
        # Pattern 1: explicit relation verb
        for match in _RELATION_PATTERN.finditer(sentence):
            rel = re.sub(r"\s+", " ", match.group("rel").strip().lower())
            direction = _normalize_direction(rel)
            claim = _build_claim(
                iv=match.group("iv"),
                dv=match.group("dv"),
                direction=direction,
                relationship=rel,
                sentence=sentence,
                source="text_extraction_regex",
                base_confidence=0.62,
            )
            claims.append(claim)

        # Pattern 2: comparative "with X had shorter Y"
        comp_match = _WITH_COMPARATIVE_PATTERN.search(sentence)
        if comp_match:
            comp = comp_match.group("comp").lower()
            direction = _COMPARATIVE_TO_DIRECTION.get(comp, "unknown")
            base_claim = _build_claim(
                iv=comp_match.group("iv"),
                dv=comp_match.group("dv"),
                direction=direction,
                relationship=comp,
                sentence=sentence,
                source="text_extraction_comparative",
                base_confidence=0.68,
            )
            claims.append(base_claim)

            # Additional comparative effects chained by "and ..."
            for tail in _AND_REQUIRED_COMPARATIVE_PATTERN.finditer(sentence):
                tail_comp = tail.group("comp").lower()
                tail_direction = _COMPARATIVE_TO_DIRECTION.get(tail_comp, "unknown")
                extra_claim = _build_claim(
                    iv=comp_match.group("iv"),
                    dv=tail.group("dv"),
                    direction=tail_direction,
                    relationship=tail_comp,
                    sentence=sentence,
                    source="text_extraction_comparative",
                    base_confidence=0.63,
                )
                claims.append(extra_claim)

    # Dedupe by (iv,dv,direction,source)
    deduped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for claim in claims:
        key = (
            _normalize(claim["iv"]),
            _normalize(claim["dv"]),
            claim["direction"],
            claim["source"],
        )
        existing = deduped.get(key)
        if existing is None or claim["confidence"] > existing["confidence"]:
            deduped[key] = claim
    return list(deduped.values())

