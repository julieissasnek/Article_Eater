"""
Hard negative library for claim extraction precision.

Contains known-bad patterns from the corpus that should NOT produce claims.
Used as a CI gate to ensure recall improvements don't reintroduce garbage.

Sprint D improvement: Codex suggestion #10
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HardNegative:
    """A known bad pattern that should be rejected."""
    pattern_type: str  # author_bio, reference_list, figure_caption, ocr_garbage, model_fit
    sample_text: str
    why_bad: str


# Known bad rows from the corpus - these should NEVER produce claims
HARD_NEGATIVE_ROWS: list[HardNegative] = [
    # Author biographies
    HardNegative(
        pattern_type="author_bio",
        sample_text="Francesca Ostuzzi Design Faculty of Engineering and Architecture Ghent University",
        why_bad="Author affiliation, not a scientific finding"
    ),
    HardNegative(
        pattern_type="author_bio",
        sample_text="Dr. Sarah Johnson is a professor of environmental psychology at MIT",
        why_bad="Author bio, not data"
    ),
    HardNegative(
        pattern_type="author_bio",
        sample_text="Department of Architecture, University of California Berkeley",
        why_bad="Institutional affiliation"
    ),

    # Reference list entries
    HardNegative(
        pattern_type="reference_list",
        sample_text="Ulrich, R.S. (1984). View through a window may influence recovery from surgery. Science, 224, 420-421.",
        why_bad="Citation, not a finding from this paper"
    ),
    HardNegative(
        pattern_type="reference_list",
        sample_text="Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. Journal of Environmental Psychology, 15(3), 169-182.",
        why_bad="Reference entry, not extractable data"
    ),
    HardNegative(
        pattern_type="reference_list",
        sample_text="doi:10.1016/j.jenvp.2012.01.003",
        why_bad="DOI only, no content"
    ),

    # Figure captions
    HardNegative(
        pattern_type="figure_caption",
        sample_text="Figure 3. Sample photo of room with high ceiling condition",
        why_bad="Figure caption, not data"
    ),
    HardNegative(
        pattern_type="figure_caption",
        sample_text="Appendix Figure A1: Experimental stimuli showing nature views",
        why_bad="Appendix figure description"
    ),
    HardNegative(
        pattern_type="figure_caption",
        sample_text="Table 1. Participant demographics and baseline characteristics",
        why_bad="Table label for demographics, not results"
    ),

    # OCR garbage
    HardNegative(
        pattern_type="ocr_garbage",
        sample_text="ffititttiningg thhee sseennssoorrss",
        why_bad="Doubled character OCR artifact"
    ),
    HardNegative(
        pattern_type="ocr_garbage",
        sample_text="samplephotoofroomwithhighsalience",
        why_bad="Concatenated words, no spaces"
    ),
    HardNegative(
        pattern_type="ocr_garbage",
        sample_text="ttaaccttiillee pprrooppeerrttiieess",
        why_bad="Systematic character doubling"
    ),
    HardNegative(
        pattern_type="ocr_garbage",
        sample_text="@#$%^&*()_+{}|:<>?~`",
        why_bad="Non-word character sequences"
    ),

    # Model fit tables (no IV/DV)
    HardNegative(
        pattern_type="model_fit",
        sample_text="RMSEA = 0.05, CFI = 0.96, GFI = 0.94, χ²/df = 2.1",
        why_bad="Model fit indices only, no causal claim"
    ),
    HardNegative(
        pattern_type="model_fit",
        sample_text="χ² = 234.5, df = 120, p < .001, AIC = 456.2, BIC = 521.3",
        why_bad="Model comparison statistics, not effect"
    ),

    # Demographics (descriptive, not causal)
    HardNegative(
        pattern_type="demographics",
        sample_text="Age (M = 32.5, SD = 8.7), Gender (54% female), Education (42% college)",
        why_bad="Participant characteristics, not findings"
    ),
    HardNegative(
        pattern_type="demographics",
        sample_text="N = 120 participants were recruited from the university population",
        why_bad="Sample description, not result"
    ),

    # Notes and footnotes
    HardNegative(
        pattern_type="note",
        sample_text="Note: * p < .05, ** p < .01, *** p < .001",
        why_bad="Table footnote, not a claim"
    ),
    HardNegative(
        pattern_type="note",
        sample_text="a Higher scores indicate greater satisfaction",
        why_bad="Scale explanation note"
    ),
]


# Compiled patterns for fast rejection
_HARD_NEGATIVE_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "author_bio": [
        re.compile(r"\b(ph\.?d|professor|dr\.)\b.*\buniversity\b", re.I),
        re.compile(r"\bis\s+a\s+professor\s+of\b", re.I),
        re.compile(r"\bdr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b", re.I),
        re.compile(r"\bdepartment\s+of\s+(architecture|psychology|design)\b", re.I),
        re.compile(r"\bfaculty\s+of\b", re.I),
        re.compile(r"\baffiliations?:?\s*\d", re.I),
        re.compile(r"@[\w.-]+\.(edu|ac\.\w{2}|org)", re.I),
    ],
    "reference_list": [
        re.compile(r"\(\d{4}\)\.\s*[A-Z].*\.\s*[A-Z][a-z]+,?\s*\d+"),  # APA format
        re.compile(r"doi:\s*10\.\d{4,}", re.I),
        re.compile(r"\bvol\.\s*\d+.*pp\.\s*\d+", re.I),
        re.compile(r",\s*\d+\(\d+\),\s*\d+-\d+"),  # Journal citation pattern
        re.compile(r"\bet\s+al\.?\s*\(\d{4}\)", re.I),
    ],
    "figure_caption": [
        re.compile(r"^figure\s+\d", re.I),
        re.compile(r"^table\s+\d.*characteristics", re.I),
        re.compile(r"^appendix\s+(figure|table)", re.I),
        re.compile(r"sample\s+photo\s+of", re.I),
        re.compile(r"experimental\s+stimuli", re.I),
    ],
    "ocr_garbage": [
        re.compile(r"(.)\1{3,}"),  # 4+ repeated characters
        re.compile(r"(?:([a-z])\1){3,}", re.I),  # many doubled letters in sequence
        re.compile(r"\b[a-z]{25,}\b"),  # Very long single word
        re.compile(r"[^\w\s]{6,}"),  # 6+ non-word chars
        re.compile(r"^[\d\s.,;:]+$"),  # Numbers/punctuation only
    ],
    "model_fit": [
        re.compile(r"\b(rmsea|cfi|gfi|aic|bic)\s*=\s*[\d.]+", re.I),
        re.compile(r"χ²\s*/\s*df\s*=", re.I),
        re.compile(r"model\s+fit\s+(indices|statistics)", re.I),
    ],
    "demographics": [
        re.compile(r"age\s*\(?\s*m\s*=", re.I),
        re.compile(r"\bgender\s*\(.*%\s*(male|female)", re.I),
        re.compile(r"participants?\s+were\s+recruited", re.I),
        re.compile(r"(inclusion|exclusion)\s+criteria", re.I),
    ],
    "note": [
        re.compile(r"^notes?[:\s]", re.I),
        re.compile(r"^\*+\s*p\s*[<=>]", re.I),
        re.compile(r"^[a-z]\s+higher\s+scores", re.I),
    ],
}


def is_hard_negative(text: str) -> tuple[bool, str | None]:
    """
    Check if text matches a known hard negative pattern.

    Args:
        text: Row or cell text to check

    Returns:
        Tuple of (is_negative, pattern_type). If is_negative is True,
        pattern_type indicates why.
    """
    if not text or len(text.strip()) < 5:
        return (True, "too_short")

    lowered = text.lower()

    # Robust OCR artifact check for systematic doubled letters:
    # "ttaaccttiillee pprrooppeerrttiieess", "ffititttiningg", etc.
    doubled_pairs = len(re.findall(r"([a-z])\1", lowered))
    if doubled_pairs >= 4:
        return (True, "ocr_garbage")

    for pattern_type, patterns in _HARD_NEGATIVE_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text):
                return (True, pattern_type)

    return (False, None)


def filter_hard_negatives(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Filter out hard negative rows from a list of table rows.

    Args:
        rows: List of row dicts with 'text' or 'source_quote' field

    Returns:
        Tuple of (kept_rows, rejected_rows) where rejected_rows have
        an additional 'rejection_reason' field.
    """
    kept = []
    rejected = []

    for row in rows:
        text = row.get("text") or row.get("source_quote") or row.get("statement") or ""
        is_neg, reason = is_hard_negative(text)

        if is_neg:
            rejected.append({**row, "rejection_reason": reason})
        else:
            kept.append(row)

    return kept, rejected


def get_hard_negative_stats() -> dict[str, int]:
    """Return statistics about the hard negative library."""
    return {
        "total_examples": len(HARD_NEGATIVE_ROWS),
        "pattern_types": len(_HARD_NEGATIVE_PATTERNS),
        "total_patterns": sum(len(p) for p in _HARD_NEGATIVE_PATTERNS.values()),
        "by_type": {
            ptype: len(patterns)
            for ptype, patterns in _HARD_NEGATIVE_PATTERNS.items()
        },
    }


# For testing: verify all hard negatives are detected
def verify_hard_negatives() -> dict[str, Any]:
    """Verify that all hard negative examples are caught by patterns."""
    results = {"passed": 0, "failed": 0, "failures": []}

    for hn in HARD_NEGATIVE_ROWS:
        is_neg, detected_type = is_hard_negative(hn.sample_text)
        if is_neg:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["failures"].append({
                "expected_type": hn.pattern_type,
                "text": hn.sample_text[:80],
                "why_bad": hn.why_bad,
            })

    return results


if __name__ == "__main__":
    import json

    print("Hard Negative Library Stats:")
    print(json.dumps(get_hard_negative_stats(), indent=2))

    print("\nVerifying all examples are caught:")
    verification = verify_hard_negatives()
    print(f"  Passed: {verification['passed']}")
    print(f"  Failed: {verification['failed']}")
    if verification["failures"]:
        print("  Failures:")
        for f in verification["failures"]:
            print(f"    - {f['expected_type']}: {f['text'][:50]}...")
