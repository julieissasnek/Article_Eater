"""
Vocabulary module for Article Eater extraction pipeline (Sprint D Task D.1).

Provides unified variable vocabulary for mapping natural language terms
to canonical CMR variable names.
"""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any


VOCABULARY_PATH = Path(__file__).parent.parent.parent / "data" / "vocabulary" / "variable_vocabulary.json"


@lru_cache(maxsize=1)
def load_vocabulary(vocab_path: str | Path | None = None) -> dict[str, Any]:
    """
    Load the canonical variable vocabulary.

    Args:
        vocab_path: Path to vocabulary JSON. Defaults to standard location.

    Returns:
        Dict with 'independent_variables', 'dependent_variables', etc.
    """
    path = Path(vocab_path) if vocab_path else VOCABULARY_PATH
    if not path.exists():
        raise FileNotFoundError(f"Vocabulary file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _normalize(text: str) -> str:
    """Normalize text for matching: lowercase, remove punctuation, collapse spaces."""
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _compute_similarity(term: str, target: str) -> float:
    """Compute similarity score between normalized terms."""
    if not term or not target:
        return 0.0

    norm_term = _normalize(term)
    norm_target = _normalize(target)

    if not norm_term or not norm_target:
        return 0.0

    # Exact match
    if norm_term == norm_target:
        return 1.0

    # Substring match (high confidence)
    if norm_term in norm_target or norm_target in norm_term:
        shorter = min(len(norm_term), len(norm_target))
        longer = max(len(norm_term), len(norm_target))
        return 0.85 + 0.1 * (shorter / longer)

    # Token overlap
    term_tokens = set(norm_term.split())
    target_tokens = set(norm_target.split())
    if term_tokens and target_tokens:
        overlap = len(term_tokens & target_tokens)
        total = len(term_tokens | target_tokens)
        if overlap > 0:
            token_score = 0.7 + 0.2 * (overlap / total)
            return token_score

    # Fuzzy sequence matching
    return SequenceMatcher(None, norm_term, norm_target).ratio()


def find_closest_iv(term: str, vocab: dict[str, Any] | None = None) -> tuple[str, float]:
    """
    Given a natural language term, find the closest canonical IV.

    Args:
        term: Natural language term to match (e.g., "ceiling height", "room tallness")
        vocab: Vocabulary dict (loads default if None)

    Returns:
        Tuple of (canonical_name, confidence) where confidence is 0.0-1.0.
        Returns (None, 0.0) if no reasonable match found.
    """
    if not term:
        return (None, 0.0)

    if vocab is None:
        vocab = load_vocabulary()

    ivs = vocab.get("independent_variables", {})

    best_match = None
    best_score = 0.0

    for canonical, data in ivs.items():
        # Check canonical name
        score = _compute_similarity(term, canonical)
        if score > best_score:
            best_score = score
            best_match = canonical

        # Check synonyms
        for synonym in data.get("synonyms", []):
            score = _compute_similarity(term, synonym)
            if score > best_score:
                best_score = score
                best_match = canonical

    # Threshold: require at least 0.4 similarity
    if best_score < 0.4:
        return (None, 0.0)

    return (best_match, round(best_score, 2))


def find_closest_dv(term: str, vocab: dict[str, Any] | None = None) -> tuple[str, float]:
    """
    Given a natural language term, find the closest canonical DV.

    Args:
        term: Natural language term to match (e.g., "cortisol levels", "creative output")
        vocab: Vocabulary dict (loads default if None)

    Returns:
        Tuple of (canonical_name, confidence) where confidence is 0.0-1.0.
        Returns (None, 0.0) if no reasonable match found.
    """
    if not term:
        return (None, 0.0)

    if vocab is None:
        vocab = load_vocabulary()

    dvs = vocab.get("dependent_variables", {})

    best_match = None
    best_score = 0.0

    for canonical, data in dvs.items():
        # Check canonical name
        score = _compute_similarity(term, canonical)
        if score > best_score:
            best_score = score
            best_match = canonical

        # Check synonyms
        for synonym in data.get("synonyms", []):
            score = _compute_similarity(term, synonym)
            if score > best_score:
                best_score = score
                best_match = canonical

        # Check measurement types (for DVs)
        for mtype in data.get("measurement_types", []):
            score = _compute_similarity(term, mtype)
            if score > best_score:
                best_score = score
                best_match = canonical

    # Threshold: require at least 0.4 similarity
    if best_score < 0.4:
        return (None, 0.0)

    return (best_match, round(best_score, 2))


def find_closest_variable(term: str, vocab: dict[str, Any] | None = None) -> tuple[str, str, float]:
    """
    Find the closest variable (IV or DV) for a term.

    Args:
        term: Natural language term to match
        vocab: Vocabulary dict (loads default if None)

    Returns:
        Tuple of (canonical_name, variable_type, confidence) where
        variable_type is "iv" or "dv".
        Returns (None, None, 0.0) if no match found.
    """
    iv_match, iv_conf = find_closest_iv(term, vocab)
    dv_match, dv_conf = find_closest_dv(term, vocab)

    if iv_conf >= dv_conf and iv_match:
        return (iv_match, "iv", iv_conf)
    elif dv_match:
        return (dv_match, "dv", dv_conf)
    else:
        return (None, None, 0.0)


def get_extraction_prompt_vocabulary(vocab: dict[str, Any] | None = None) -> str:
    """
    Format the vocabulary as a reference sheet for LLM extraction prompts.

    Returns a formatted string listing all IVs and DVs with synonyms,
    suitable for inclusion in an extraction prompt.
    """
    if vocab is None:
        vocab = load_vocabulary()

    lines = []

    # Independent Variables
    lines.append("INDEPENDENT VARIABLES (Environmental/Architectural Features):")
    lines.append("-" * 60)

    ivs = vocab.get("independent_variables", {})
    for canonical, data in sorted(ivs.items()):
        synonyms = data.get("synonyms", [])[:5]  # Top 5 synonyms
        unit = data.get("unit", "")
        domain = data.get("domain", "")

        syn_str = ", ".join(synonyms) if synonyms else ""
        unit_str = f" [{unit}]" if unit else ""

        lines.append(f"  {canonical}{unit_str}")
        if syn_str:
            lines.append(f"    Synonyms: {syn_str}")

    lines.append("")
    lines.append("DEPENDENT VARIABLES (Outcomes/Effects):")
    lines.append("-" * 60)

    dvs = vocab.get("dependent_variables", {})
    for canonical, data in sorted(dvs.items()):
        synonyms = data.get("synonyms", [])[:5]  # Top 5 synonyms
        measurements = data.get("measurement_types", [])[:3]  # Top 3 measures

        syn_str = ", ".join(synonyms) if synonyms else ""
        meas_str = ", ".join(measurements) if measurements else ""

        lines.append(f"  {canonical}")
        if syn_str:
            lines.append(f"    Synonyms: {syn_str}")
        if meas_str:
            lines.append(f"    Measures: {meas_str}")

    return "\n".join(lines)


def get_iv_list(vocab: dict[str, Any] | None = None) -> list[str]:
    """Return list of all canonical IV names."""
    if vocab is None:
        vocab = load_vocabulary()
    return list(vocab.get("independent_variables", {}).keys())


def get_dv_list(vocab: dict[str, Any] | None = None) -> list[str]:
    """Return list of all canonical DV names."""
    if vocab is None:
        vocab = load_vocabulary()
    return list(vocab.get("dependent_variables", {}).keys())


def get_all_synonyms(variable_type: str = "both", vocab: dict[str, Any] | None = None) -> dict[str, str]:
    """
    Get a flat mapping of all synonyms to canonical names.

    Args:
        variable_type: "iv", "dv", or "both"
        vocab: Vocabulary dict

    Returns:
        Dict mapping synonym -> canonical_name
    """
    if vocab is None:
        vocab = load_vocabulary()

    result = {}

    if variable_type in ("iv", "both"):
        for canonical, data in vocab.get("independent_variables", {}).items():
            result[_normalize(canonical)] = canonical
            for syn in data.get("synonyms", []):
                result[_normalize(syn)] = canonical

    if variable_type in ("dv", "both"):
        for canonical, data in vocab.get("dependent_variables", {}).items():
            result[_normalize(canonical)] = canonical
            for syn in data.get("synonyms", []):
                result[_normalize(syn)] = canonical

    return result


def validate_vocabulary(vocab: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Validate the vocabulary structure and return statistics.

    Returns:
        Dict with validation results and stats.
    """
    if vocab is None:
        vocab = load_vocabulary()

    ivs = vocab.get("independent_variables", {})
    dvs = vocab.get("dependent_variables", {})

    iv_count = len(ivs)
    dv_count = len(dvs)

    iv_synonym_count = sum(len(v.get("synonyms", [])) for v in ivs.values())
    dv_synonym_count = sum(len(v.get("synonyms", [])) for v in dvs.values())

    # Check for missing required fields
    issues = []
    for name, data in ivs.items():
        if not data.get("synonyms"):
            issues.append(f"IV '{name}' has no synonyms")
        if not data.get("domain"):
            issues.append(f"IV '{name}' has no domain")

    for name, data in dvs.items():
        if not data.get("synonyms"):
            issues.append(f"DV '{name}' has no synonyms")

    return {
        "valid": len(issues) == 0,
        "iv_count": iv_count,
        "dv_count": dv_count,
        "iv_synonym_count": iv_synonym_count,
        "dv_synonym_count": dv_synonym_count,
        "total_variables": iv_count + dv_count,
        "total_synonyms": iv_synonym_count + dv_synonym_count,
        "issues": issues,
    }


# Module-level convenience
if __name__ == "__main__":
    # Quick validation when run directly
    stats = validate_vocabulary()
    print(f"Vocabulary validated: {stats['valid']}")
    print(f"  IVs: {stats['iv_count']} ({stats['iv_synonym_count']} synonyms)")
    print(f"  DVs: {stats['dv_count']} ({stats['dv_synonym_count']} synonyms)")
    if stats['issues']:
        print(f"  Issues: {len(stats['issues'])}")
        for issue in stats['issues'][:5]:
            print(f"    - {issue}")
