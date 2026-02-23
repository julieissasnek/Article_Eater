"""Rules for when direction should be expected for a claim."""

from __future__ import annotations

import re
from typing import Any

EMPIRICAL_FAMILIES = {
    "empirical_v2",
    "observational_field",
    "case_study",
    "mixed_methods",
}

_ABSTRACT_AIM_RE = re.compile(
    r"\b("
    r"aim(?:ed)?\s+to|objective(?:s)?\s+(?:was|were|is|are|to)|purpose\s+of\s+(?:this|the)\s+study|"
    r"this\s+study\s+(?:aims?|examines?|investigates?|explores?|tests?)|"
    r"we\s+(?:aimed|examine[ds]?|investigate[ds]?|explore[ds]?|test(?:ed|s)?)|"
    r"to\s+(?:examine|investigate|explore|test|understand)"
    r")\b",
    re.IGNORECASE,
)
_RESULT_CUE_RE = re.compile(
    r"\b("
    r"found|show(?:ed|s)?|results?\s+(?:show|indicate|reveal)|demonstrat(?:ed|es)|"
    r"significant|associated|correlated|predicted|increased|decreased|reduced|improved|"
    r"no\s+significant|non[- ]?significant|p\s*[<=>]|β|r\s*=|t\(|f\("
    r")\b",
    re.IGNORECASE,
)


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def direction_expected_by_article_type(article_type_family: str | None) -> bool:
    return _norm(article_type_family) in EMPIRICAL_FAMILIES


def direction_expected_for_claim(claim: dict[str, Any]) -> tuple[bool, str]:
    """Return whether direction should be expected plus reason code."""
    family = _norm(claim.get("article_type_family") or claim.get("field_contract_family"))
    if family not in EMPIRICAL_FAMILIES:
        return False, "non_empirical_family"

    claim_type = _norm(claim.get("claim_type"))
    if claim_type in {"mechanistic", "theoretical", "descriptive"}:
        return False, "claim_type_not_directional"

    source = _norm(claim.get("claim_source"))
    quote = str(claim.get("source_quote") or claim.get("evidence_quote") or "")
    if source == "abstract":
        if _ABSTRACT_AIM_RE.search(quote) and not _RESULT_CUE_RE.search(quote):
            return False, "abstract_aim_statement"

    # Default for empirical claims: direction should usually be recoverable.
    return True, "expected_empirical_claim"

