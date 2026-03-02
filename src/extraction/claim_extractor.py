"""
Structured claim extraction engine for Sprint D Task D.6.

Extracts IV→DV causal claims from classified tables using vocabulary mapping
and effect size conversion.

PRECISION IMPROVEMENTS (2026-02-18):
- Garbage detection filters OCR artifacts before extraction
- Table-type-aware extraction strategies
- Statistical sign inference for direction
- Stricter confidence thresholds
- Better causal pattern matching with correct IV/DV ordering

CODEX INTEGRATION (2026-02-18):
- Integrated table_semantics_codex for pre-extraction profiling
- Integrated row_classifier_codex for row-level filtering
- Added confidence decomposition (table_type, row_quality, iv_map, dv_map, stat_parse)
- Added header-based IV/DV inference for regression tables
- Enhanced p-value parsing (.03., <.05, ns, etc.)
- Added hard negative filtering
- Added significance-aware extraction (is_significant flag)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from src.extraction.effect_size_converter import to_cohens_d
from src.extraction.hard_negatives import filter_hard_negatives
from src.extraction.row_classifier_codex import RowProfile, classify_row_content, normalize_ocr_text
from src.extraction.table_semantics_codex import build_table_content_profile
from src.extraction.article_type_contract import get_family_contract
from src.extraction.vocabulary import (
    find_closest_dv,
    find_closest_iv,
    get_extraction_prompt_vocabulary,
    load_vocabulary,
)


# ============================================================================
# CONFIDENCE DECOMPOSITION (Codex suggestion #8)
# ============================================================================

@dataclass
class ConfidenceDecomposition:
    """Per-component confidence scores for extraction quality assessment."""
    table_type_confidence: float = 0.0  # How confident in table semantic type
    row_quality_confidence: float = 0.0  # Row-level quality (non-junk)
    iv_map_confidence: float = 0.0  # IV vocabulary mapping confidence
    dv_map_confidence: float = 0.0  # DV vocabulary mapping confidence
    stat_parse_confidence: float = 0.0  # Statistical value parsing confidence

    # Minimum thresholds per component
    MIN_TABLE_TYPE: float = 0.5
    MIN_ROW_QUALITY: float = 0.6
    MIN_IV_MAP: float = 0.4
    MIN_DV_MAP: float = 0.4
    MIN_STAT_PARSE: float = 0.3

    def meets_thresholds(self) -> bool:
        """Check if all components meet minimum thresholds."""
        return (
            self.table_type_confidence >= self.MIN_TABLE_TYPE
            and self.row_quality_confidence >= self.MIN_ROW_QUALITY
            and (self.iv_map_confidence >= self.MIN_IV_MAP or self.dv_map_confidence >= self.MIN_DV_MAP)
        )

    def aggregate(self) -> float:
        """Compute weighted aggregate confidence."""
        weights = {
            "table_type": 0.15,
            "row_quality": 0.20,
            "iv_map": 0.25,
            "dv_map": 0.25,
            "stat_parse": 0.15,
        }
        return (
            self.table_type_confidence * weights["table_type"]
            + self.row_quality_confidence * weights["row_quality"]
            + self.iv_map_confidence * weights["iv_map"]
            + self.dv_map_confidence * weights["dv_map"]
            + self.stat_parse_confidence * weights["stat_parse"]
        )

    def to_dict(self) -> dict[str, float]:
        """Convert to dict for JSON serialization."""
        return {
            "table_type_confidence": round(self.table_type_confidence, 3),
            "row_quality_confidence": round(self.row_quality_confidence, 3),
            "iv_map_confidence": round(self.iv_map_confidence, 3),
            "dv_map_confidence": round(self.dv_map_confidence, 3),
            "stat_parse_confidence": round(self.stat_parse_confidence, 3),
            "aggregate": round(self.aggregate(), 3),
            "meets_thresholds": self.meets_thresholds(),
        }


# ============================================================================
# GARBAGE DETECTION (filter before extraction)
# ============================================================================

# OCR artifact patterns - doubled characters like "ffititttiningg"
_OCR_DOUBLED_PATTERN = re.compile(r"(.)\1{2,}")  # 3+ repeated chars
_OCR_WORD_DOUBLED = re.compile(r"\b(\w{2,})\1\b", re.I)  # "halfhalf"

# Non-word garbage patterns
_GARBAGE_PATTERNS = [
    re.compile(r"^[\d\s.,;:]+$"),  # Only numbers/punctuation
    re.compile(r"[^\x00-\x7F]{3,}"),  # Long non-ASCII sequences
    re.compile(r"\b[A-Z]{10,}\b"),  # Very long all-caps (likely garbled)
    re.compile(r"appendix\s+figure", re.I),  # Figure captions
    re.compile(r"^figure\s+\d", re.I),  # Figure labels
    re.compile(r"^table\s+\d", re.I),  # Table labels (not content)
    re.compile(r"sample\s*photo\s*of", re.I),  # Photo captions
    re.compile(r"@.*\.(edu|com|org)", re.I),  # Email addresses
    re.compile(r"https?://", re.I),  # URLs
]

# Author biography indicators
_AUTHOR_PATTERNS = [
    re.compile(r"\b(ph\.?d|professor|dr\.)\b.*\buniversity\b", re.I),
    re.compile(r"\bdepartment\s+of\b", re.I),
    re.compile(r"\baffiliations?\b", re.I),
]


def _is_garbage(text: str) -> bool:
    """
    Detect if text is garbage (OCR artifacts, author bios, figure captions).

    Returns True if text should be filtered out before extraction.
    """
    if not text or len(text.strip()) < 10:
        return True

    # Check for doubled characters (OCR artifacts)
    word_count = len(text.split())
    doubled_matches = len(_OCR_DOUBLED_PATTERN.findall(text))
    if doubled_matches > word_count * 0.3:  # >30% of words have doubled chars
        return True

    # Check explicit garbage patterns
    for pattern in _GARBAGE_PATTERNS:
        if pattern.search(text):
            return True

    # Check author patterns
    for pattern in _AUTHOR_PATTERNS:
        if pattern.search(text):
            return True

    # Check for word doubling (like "half-life half-life")
    if _OCR_WORD_DOUBLED.search(text):
        return True

    return False


def _clean_text(text: str) -> str:
    """Clean text before extraction: normalize whitespace, remove artifacts."""
    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove obvious OCR doubled sequences (conservative)
    # e.g., "ttaacctitliele" but not legitimate doubles like "committee"
    text = re.sub(r"(.)\1{3,}", r"\1\1", text)  # Reduce 4+ to 2

    return text


# ============================================================================
# DIRECTION DETECTION (with statistical sign awareness)
# ============================================================================

_POSITIVE_PATTERNS = [
    re.compile(r"\b(increase[sd]?|enhance[sd]?|improve[sd]?|boost[sd]?|raise[sd]?|elevate[sd]?)\b", re.I),
    re.compile(r"\b(higher|greater|more|better)\b", re.I),  # Removed "positive" - too ambiguous
    re.compile(r"\b(promote[sd]?|facilitate[sd]?|support[sd]?|strengthen[sd]?)\b", re.I),
    re.compile(r"\bpositively\s+(associated|correlated|related)\b", re.I),
    re.compile(r"\b(positive|direct)\s+(association|correlation|relationship)\b", re.I),
]

_NEGATIVE_PATTERNS = [
    re.compile(r"\b(decrease[sd]?|reduce[sd]?|diminish[ed]?|inhibit[sd]?|attenuate[sd]?)\b", re.I),
    re.compile(r"\b(less|fewer|worse)\b", re.I),  # Removed "lower" - ambiguous
    re.compile(r"\b(impair[sd]?|suppress[ed]?|prevent[sd]?|disrupt[sd]?)\b", re.I),
    re.compile(r"\bnegatively\s+(associated|correlated|related)\b", re.I),
    re.compile(r"\b(negative|inverse)\s+(association|correlation|relationship)\b", re.I),
]

_NO_EFFECT_PATTERNS = [
    re.compile(r"\b(no\s+(?:significant\s+)?(?:effect|difference|change|impact|relationship))\b", re.I),
    re.compile(r"\bnon[-\s]?significant\b", re.I),
    re.compile(r"\bp\s*[>=]\s*0\.0?5\b", re.I),
    re.compile(r"\bns\b", re.I),
    re.compile(r"\bfailed\s+to\s+(reach|achieve)\s+significance\b", re.I),
]

# Statistical patterns for effect size detection
_STAT_PATTERNS = {
    "f_value": re.compile(r"[Ff]\s*\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)\s*[=:]?\s*([-\d.]+)"),
    "t_value": re.compile(r"[Tt]\s*\(\s*([\d.]+)\s*\)\s*[=:]?\s*([-\d.]+)"),
    "r": re.compile(r"\br\s*[=:]?\s*([-\d.]+)\b"),
    "eta_squared": re.compile(r"(?:η²|eta\s*squared|partial\s+eta)\s*=?\s*([\d.]+)", re.I),
    "cohens_d": re.compile(r"(?:cohen['']?s?\s+)?d\s*[=:]?\s*([-\d.]+)\b", re.I),
    "beta": re.compile(r"(?:β|beta)\s*[=:]?\s*([-\d.]+)\b", re.I),
    "p_value": re.compile(r"p\s*[<>=]\s*([\d.]+)"),
}

# Enhanced p-value patterns for robust parsing (Codex suggestion #7)
_P_VALUE_PATTERNS = [
    # Standard formats: p < .05, p = 0.03, p > 0.10
    re.compile(r"p\s*<\s*\.?(\d+\.?\d*)", re.I),
    re.compile(r"p\s*=\s*\.?(\d+\.?\d*)", re.I),
    re.compile(r"p\s*>\s*\.?(\d+\.?\d*)", re.I),
    # Trailing period artifacts: .03. -> .03
    re.compile(r"p\s*[<>=]\s*(\d*\.?\d+)\.(?:\s|$)", re.I),
    # Non-significant markers
    re.compile(r"\bns\b", re.I),
    re.compile(r"n\.?s\.?", re.I),
    # Asterisk significance: *, **, ***
    re.compile(r"\*{3}"),  # *** = p < .001
    re.compile(r"\*{2}(?!\*)"),  # ** = p < .01
    re.compile(r"\*(?!\*)"),  # * = p < .05
]

_SIGNIFICANCE_THRESHOLDS = {
    "***": 0.001,
    "**": 0.01,
    "*": 0.05,
}

_SAMPLE_PATTERNS = [
    re.compile(r"\b[Nn]\s*[=:]?\s*(\d{2,5})\b"),
    re.compile(r"\bsample\s*(?:size)?[:=]\s*(\d+)", re.I),
    re.compile(r"(\d+)\s+participants", re.I),
]

_STAT_COL_HEADER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("beta", re.compile(r"\b(β|beta|std\.?\s*beta|coefficient|coeff)\b", re.I)),
    ("r", re.compile(r"\b(r|corr(?:elation)?)\b", re.I)),
    ("p_value", re.compile(r"\b(p|sig(?:nificance)?)\b", re.I)),
    ("t_value", re.compile(r"\bt\b", re.I)),
    ("f_value", re.compile(r"\bf\b", re.I)),
    ("eta_squared", re.compile(r"(η²|eta)", re.I)),
    ("cohens_d", re.compile(r"\b(cohen|cohens?|d)\b", re.I)),
    ("sample_n", re.compile(r"\b(n|sample)\b", re.I)),
]

# Context indicators
_CONTEXT_PATTERNS = {
    "office": re.compile(r"\b(office|workplace|work\s*space|cubicle)\b", re.I),
    "hospital": re.compile(r"\b(hospital|healthcare|clinic|medical|patient)\b", re.I),
    "school": re.compile(r"\b(school|classroom|student|education|university)\b", re.I),
    "residential": re.compile(r"\b(home|residential|apartment|house|living)\b", re.I),
    "laboratory": re.compile(r"\b(laboratory|lab|experimental|controlled)\b", re.I),
    "outdoor": re.compile(r"\b(outdoor|nature|park|garden|forest)\b", re.I),
    "retail": re.compile(r"\b(retail|store|shop|commercial)\b", re.I),
}


def _generate_claim_id(paper_id: str, table_id: str | None, seq: int) -> str:
    """Generate a unique claim ID."""
    table_part = table_id or "UNKNOWN"
    return f"{paper_id}:{table_part}:C{seq:03d}"


def _detect_direction(text: str, stats: dict[str, Any] | None = None) -> str:
    """
    Detect effect direction from text and statistical values.

    Uses multiple signals:
    1. Explicit direction words (increase, decrease, etc.)
    2. Statistical signs (negative beta, negative t-value, negative r)
    3. No-effect indicators (ns, p > .05)

    Args:
        text: The source text to analyze
        stats: Optional dict with extracted statistics (beta, t_value, r, etc.)

    Returns: "increase", "decrease", "no_effect", or "unknown"
    """
    if not text:
        return "unknown"

    stats = stats or {}

    # Check for no effect first (most specific)
    for pattern in _NO_EFFECT_PATTERNS:
        if pattern.search(text):
            return "no_effect"

    # STATISTICAL SIGN INFERENCE
    # Negative beta/t/r values indicate negative relationship
    stat_direction = None

    if "beta" in stats:
        if stats["beta"] < -0.05:
            stat_direction = "decrease"
        elif stats["beta"] > 0.05:
            stat_direction = "increase"

    if stat_direction is None and "t_value" in stats:
        if stats["t_value"] < -1.5:
            stat_direction = "decrease"
        elif stats["t_value"] > 1.5:
            stat_direction = "increase"

    if stat_direction is None and "r" in stats:
        if stats["r"] < -0.1:
            stat_direction = "decrease"
        elif stats["r"] > 0.1:
            stat_direction = "increase"

    if stat_direction is None and "cohens_d" in stats:
        if stats["cohens_d"] < -0.1:
            stat_direction = "decrease"
        elif stats["cohens_d"] > 0.1:
            stat_direction = "increase"

    # TEXTUAL DIRECTION
    positive_count = sum(1 for p in _POSITIVE_PATTERNS if p.search(text))
    negative_count = sum(1 for p in _NEGATIVE_PATTERNS if p.search(text))

    text_direction = None
    if positive_count > negative_count:
        text_direction = "increase"
    elif negative_count > positive_count:
        text_direction = "decrease"

    # COMBINE SIGNALS
    # Statistical sign is more reliable than text when available
    if stat_direction is not None:
        return stat_direction

    if text_direction is not None:
        return text_direction

    return "unknown"


def _extract_p_value_robust(text: str) -> tuple[float | None, bool]:
    """
    Extract p-value with robust parsing for common artifacts.

    Handles:
    - Standard formats: p < .05, p = 0.03, p > 0.10
    - Trailing periods: .03. (OCR artifact)
    - Non-significant markers: ns, n.s.
    - Asterisk notation: *, **, ***

    Returns: (p_value, is_significant)
    """
    if not text:
        return None, False

    # Check for explicit non-significance
    if re.search(r"\bns\b|\bn\.?s\.?(?:\s|$)", text, re.I):
        return 0.10, False  # Assume ns means p > .05, use .10 as placeholder

    # Check for asterisk significance
    if "***" in text:
        return 0.001, True
    if re.search(r"\*{2}(?!\*)", text):
        return 0.01, True
    if re.search(r"\*(?!\*)", text):
        return 0.05, True

    # Try standard p-value patterns
    p_value = None
    p_type = None  # "<", "=", ">"

    # p < value
    match = re.search(r"p\s*<\s*\.?(\d+\.?\d*)", text, re.I)
    if match:
        try:
            raw = match.group(1).rstrip(".")
            # Handle missing leading zero: .05 -> 0.05
            if raw.startswith(".") or (not "." in raw and len(raw) <= 2):
                raw = "0." + raw.lstrip(".")
            p_value = float(raw)
            p_type = "<"
        except ValueError:
            pass

    # p = value
    if p_value is None:
        match = re.search(r"p\s*=\s*\.?(\d+\.?\d*)", text, re.I)
        if match:
            try:
                raw = match.group(1).rstrip(".")
                if raw.startswith(".") or (not "." in raw and len(raw) <= 2):
                    raw = "0." + raw.lstrip(".")
                p_value = float(raw)
                p_type = "="
            except ValueError:
                pass

    # p > value
    if p_value is None:
        match = re.search(r"p\s*>\s*\.?(\d+\.?\d*)", text, re.I)
        if match:
            try:
                raw = match.group(1).rstrip(".")
                if raw.startswith(".") or (not "." in raw and len(raw) <= 2):
                    raw = "0." + raw.lstrip(".")
                p_value = float(raw)
                p_type = ">"
            except ValueError:
                pass

    # Validate p-value range
    if p_value is not None:
        if p_value > 1:
            p_value = p_value / 100 if p_value <= 100 else None  # Handle 5 -> 0.05
        if p_value is not None and (p_value <= 0 or p_value > 1):
            p_value = None

    # Determine significance
    is_significant = False
    if p_value is not None:
        if p_type == "<":
            is_significant = p_value <= 0.05
        elif p_type == "=":
            is_significant = p_value < 0.05
        else:  # ">"
            is_significant = False

    return p_value, is_significant


def _extract_statistics(text: str) -> dict[str, Any]:
    """
    Extract statistical values from text.

    Returns dict with any found statistics, including is_significant flag.
    """
    stats: dict[str, Any] = {}

    # F-value: F(df1, df2) = value
    f_match = _STAT_PATTERNS["f_value"].search(text)
    if f_match:
        try:
            stats["f_value"] = float(f_match.group(3).rstrip('.'))
            stats["df1"] = float(f_match.group(1))
            stats["df2"] = float(f_match.group(2))
        except ValueError:
            pass

    # t-value: t(df) = value
    t_match = _STAT_PATTERNS["t_value"].search(text)
    if t_match:
        try:
            stats["t_value"] = float(t_match.group(2).rstrip('.'))
            stats["df2"] = float(t_match.group(1))
        except ValueError:
            pass

    # Correlation: r = value
    r_match = _STAT_PATTERNS["r"].search(text)
    if r_match:
        try:
            val = float(r_match.group(1).rstrip('.'))
            if -1 < val < 1:  # Valid correlation
                stats["r"] = val
        except ValueError:
            pass

    # Eta squared
    eta_match = _STAT_PATTERNS["eta_squared"].search(text)
    if eta_match:
        try:
            val = float(eta_match.group(1).rstrip('.'))
            if 0 <= val < 1:
                stats["eta_squared"] = val
        except ValueError:
            pass

    # Cohen's d
    d_match = _STAT_PATTERNS["cohens_d"].search(text)
    if d_match:
        try:
            stats["cohens_d"] = float(d_match.group(1).rstrip('.'))
        except ValueError:
            pass

    # Beta
    beta_match = _STAT_PATTERNS["beta"].search(text)
    if beta_match:
        try:
            val = float(beta_match.group(1).rstrip('.'))
            if -1 < val < 1:
                stats["beta"] = val
        except ValueError:
            pass

    # P-value with robust parsing (Codex enhancement)
    p_value, is_significant = _extract_p_value_robust(text)
    if p_value is not None:
        stats["p_value"] = p_value
        stats["is_significant"] = is_significant
    else:
        # Fallback to simple pattern
        p_match = _STAT_PATTERNS["p_value"].search(text)
        if p_match:
            try:
                val = float(p_match.group(1).rstrip('.'))
                if 0 < val <= 1:
                    stats["p_value"] = val
                    stats["is_significant"] = val < 0.05
            except ValueError:
                pass

    return stats


def _extract_sample_size(text: str) -> int | None:
    """Extract sample size from text."""
    for pattern in _SAMPLE_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                n = int(match.group(1))
                if n > 0:
                    return n
            except (ValueError, IndexError):
                continue
    return None


def _infer_sample_size_from_stats(stats: dict[str, Any]) -> int | None:
    """Infer approximate N from test dfs when explicit sample size is missing."""
    try:
        df2 = stats.get("df2")
        if df2 is not None:
            df2 = int(float(df2))
            if "t_value" in stats and df2 > 0:
                # Two-group t-test approximation: df = n - 2.
                return df2 + 2
            if "f_value" in stats and df2 > 0:
                # One-way ANOVA approximation: n ~= df1 + df2 + 1.
                df1 = int(float(stats.get("df1", 1)))
                return max(2, df1 + df2 + 1)
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Returning None: {e}")
        return None
    return None


def _detect_context(text: str) -> str | None:
    """Detect study context from text."""
    for context_name, pattern in _CONTEXT_PATTERNS.items():
        if pattern.search(text):
            return context_name
    return None


def _convert_to_cohens_d(stats: dict[str, Any], sample_n: int | None) -> tuple[float | None, str | None]:
    """
    Convert extracted statistics to Cohen's d.

    Returns: (effect_size, effect_size_type)
    """
    # Priority order: Cohen's d > r > eta_squared > t_value > f_value > beta

    if "cohens_d" in stats:
        return stats["cohens_d"], "cohens_d"

    if "r" in stats:
        try:
            result = to_cohens_d(stats["r"], "r")
            return round(result["d"], 3), "r_converted"
        except ValueError:
            pass

    if "eta_squared" in stats:
        try:
            result = to_cohens_d(stats["eta_squared"], "eta_squared")
            return round(result["d"], 3), "eta_squared_converted"
        except ValueError:
            pass

    if "t_value" in stats:
        try:
            result = to_cohens_d(
                stats["t_value"],
                "t_value",
                df2=stats.get("df2"),
                n=sample_n,
            )
            return round(result["d"], 3), "t_value_converted"
        except ValueError:
            pass

    if "f_value" in stats:
        try:
            result = to_cohens_d(
                stats["f_value"],
                "f_value",
                df1=stats.get("df1"),
                df2=stats.get("df2"),
            )
            return round(result["d"], 3), "f_value_converted"
        except ValueError:
            pass

    if "beta" in stats:
        try:
            result = to_cohens_d(stats["beta"], "beta")
            return round(result["d"], 3), "beta_converted"
        except ValueError:
            pass

    # Last resort: p-value only (low confidence)
    if "p_value" in stats and sample_n and sample_n > 10:
        try:
            result = to_cohens_d(stats["p_value"], "p_value_only", n=sample_n)
            return round(result["d"], 3), "p_value_only"
        except ValueError:
            pass

    return None, None


def _parse_col_fields(row_text: str) -> dict[int, str]:
    """Parse row text with 'col_N: value' segments into an indexed dict."""
    cols: dict[int, str] = {}
    for idx, value in re.findall(r"col_(\d+)\s*:\s*([^;]+)", row_text or "", flags=re.IGNORECASE):
        try:
            cols[int(idx)] = value.strip()
        except ValueError:
            continue
    return cols


def _parse_numeric(value: str | None) -> float | None:
    """Parse a numeric token from noisy cell text."""
    if not value:
        return None
    match = re.search(r"[-+]?\d*\.?\d+", str(value))
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _infer_stat_column_semantics(rows: list[dict[str, Any]]) -> dict[int, str]:
    """
    Infer statistical meaning of column indices from header-like rows.

    Example:
      col_2: beta, col_3: t, col_4: p  -> {2: "beta", 3: "t_value", 4: "p_value"}
    """
    semantics: dict[int, str] = {}
    for row in rows[:8]:
        text = _clean_text(row.get("text") or row.get("source_quote") or "")
        cols = _parse_col_fields(text)
        if not cols:
            continue
        for col_idx, token in cols.items():
            if col_idx <= 1:
                continue
            token_l = token.strip().lower()
            if not token_l or _parse_numeric(token_l) is not None:
                continue
            for stat_key, pattern in _STAT_COL_HEADER_PATTERNS:
                if pattern.search(token_l):
                    semantics[col_idx] = stat_key
                    break
    return semantics


def _augment_stats_from_semantic_columns(
    row_text: str,
    stats: dict[str, Any],
    col_semantics: dict[int, str],
) -> dict[str, Any]:
    """Augment parsed stats using inferred column semantics for col_N rows."""
    if not col_semantics:
        return stats
    cols = _parse_col_fields(row_text)
    if not cols:
        return stats

    out = dict(stats)
    for col_idx, stat_key in col_semantics.items():
        raw = cols.get(col_idx, "")
        if not raw:
            continue

        if stat_key == "p_value":
            probe = raw if "p" in raw.lower() else f"p = {raw}"
            p_val, is_sig = _extract_p_value_robust(probe)
            if p_val is not None:
                out["p_value"] = p_val
                out["is_significant"] = is_sig
            continue

        if stat_key == "sample_n":
            n_val = _extract_sample_size(raw)
            if n_val is None:
                parsed = _parse_numeric(raw)
                if parsed is not None and parsed >= 1:
                    n_val = int(parsed)
            if n_val is not None:
                out["sample_n"] = n_val
            continue

        num = _parse_numeric(raw)
        if num is None:
            continue
        if stat_key in {"beta", "r", "eta_squared"} and not (-1 <= num <= 1):
            continue
        if stat_key == "cohens_d":
            out["cohens_d"] = num
        elif stat_key == "f_value":
            if num >= 0:
                out["f_value"] = num
        elif stat_key == "t_value":
            out["t_value"] = num
        elif stat_key == "beta":
            out["beta"] = num
        elif stat_key == "r":
            out["r"] = num
        elif stat_key == "eta_squared":
            if 0 <= num < 1:
                out["eta_squared"] = num

    return out


def _split_row_index_label(label: str) -> tuple[int | None, str]:
    """Split labels like '1 Age' or '(2) Stress' into (index, variable_label)."""
    raw = (label or "").strip()
    match = re.match(r"^\s*\(?(\d{1,2})\)?[.\s-]+(.+?)\s*$", raw)
    if match:
        return int(match.group(1)), match.group(2).strip()
    return None, raw


def _extract_caption_first_dv(
    table: dict[str, Any],
    vocab: dict[str, Any],
) -> tuple[str | None, str | None, float]:
    """Caption/context-first DV extraction per Doc71."""
    if table.get("caption_dv"):
        raw = str(table.get("caption_dv") or "").strip()
        if raw:
            mapped, conf = find_closest_dv(raw, vocab)
            if mapped and conf >= 0.5:
                return raw, mapped, conf
    contexts = [
        str(table.get("sample_content") or ""),
        str(table.get("title") or ""),
        str(table.get("abstract") or ""),
    ]
    patterns = [
        re.compile(r"predicting\s+([a-z0-9 _\-/]+?)\s+from", re.IGNORECASE),
        re.compile(r"effects?\s+on\s+([a-z0-9 _\-/]+)", re.IGNORECASE),
        re.compile(r"impact\s+on\s+([a-z0-9 _\-/]+)", re.IGNORECASE),
        re.compile(r"dependent\s+variable\s*[:=]\s*([a-z0-9 _\-/]+)", re.IGNORECASE),
        re.compile(r"([a-z0-9 _\-/]+?)\s+by\s+condition", re.IGNORECASE),
    ]
    for text in contexts:
        for pattern in patterns:
            match = pattern.search(text)
            if not match:
                continue
            raw = match.group(1).strip(" .,:;")
            if len(raw) < 3:
                continue
            mapped, conf = find_closest_dv(raw, vocab)
            if mapped and conf >= 0.5:
                return raw, mapped, conf
    return None, None, 0.0


def _map_variable_token(
    raw: str,
    vocab: dict[str, Any],
    prefer: str = "iv",
) -> tuple[str | None, float]:
    """Map a raw variable token to canonical vocabulary with side preference."""
    iv_match, iv_conf = find_closest_iv(raw, vocab)
    dv_match, dv_conf = find_closest_dv(raw, vocab)

    if prefer == "iv":
        if iv_match and iv_conf >= 0.5:
            return iv_match, iv_conf
        if dv_match and dv_conf >= 0.5:
            return dv_match, dv_conf
    else:
        if dv_match and dv_conf >= 0.5:
            return dv_match, dv_conf
        if iv_match and iv_conf >= 0.5:
            return iv_match, iv_conf

    if iv_match and iv_conf >= dv_conf:
        return iv_match, iv_conf
    if dv_match:
        return dv_match, dv_conf
    return None, 0.0


def _extract_correlation_text_fallback(
    paper_id: str,
    table: dict[str, Any],
    vocab: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Extract correlation claims from sentence-style rows.

    Handles rows like:
    - "Daylight and productivity: r = 0.42, p < .01"
    - "Acoustic privacy r = 0.48 with job satisfaction"
    """
    rows = table.get("rows", [])
    if not rows:
        return []

    claims: list[dict[str, Any]] = []
    all_text = " ".join(_clean_text(r.get("text", "") or r.get("source_quote", "")) for r in rows)
    global_sample = _extract_sample_size(all_text)

    pair_patterns = [
        re.compile(
            r"(?P<a>[a-z][a-z0-9 _\-/]{2,}?)\s+and\s+(?P<b>[a-z][a-z0-9 _\-/]{2,}?)\s*[:,-]?\s*r\s*=\s*(?P<r>-?\d*\.?\d+)",
            re.I,
        ),
        re.compile(
            r"(?P<a>[a-z][a-z0-9 _\-/]{2,}?)\s+r\s*=\s*(?P<r>-?\d*\.?\d+)\s+(?:with|to)\s+(?P<b>[a-z][a-z0-9 _\-/]{2,})",
            re.I,
        ),
    ]

    for row in rows:
        row_text = _clean_text(row.get("text", "") or row.get("source_quote", ""))
        if not row_text:
            continue
        stats = _extract_statistics(row_text)
        r_val = stats.get("r")
        if r_val is None or not (-1 <= r_val <= 1) or abs(r_val) == 1.0:
            continue
        if abs(r_val) < 0.2:
            continue

        raw_a: str | None = None
        raw_b: str | None = None
        for pattern in pair_patterns:
            match = pattern.search(row_text)
            if match:
                raw_a = match.group("a").strip(" .,:;")
                raw_b = match.group("b").strip(" .,:;")
                break
        if not raw_a or not raw_b:
            continue

        iv_match, iv_conf = _map_variable_token(raw_a, vocab, prefer="iv")
        dv_match, dv_conf = _map_variable_token(raw_b, vocab, prefer="dv")
        if iv_match and dv_match and iv_match == dv_match:
            continue

        effect_size, effect_type = _convert_to_cohens_d({"r": r_val, "p_value": stats.get("p_value")} if stats.get("p_value") else {"r": r_val}, global_sample)
        direction = "increase" if r_val > 0 else "decrease"

        claims.append(
            {
                "claim_id": _generate_claim_id(paper_id, table.get("table_id"), len(claims) + 1),
                "paper_id": paper_id,
                "iv": iv_match,
                "iv_raw": raw_a,
                "iv_mapped": bool(iv_match),
                "iv_confidence": round(float(iv_conf), 2),
                "dv": dv_match,
                "dv_raw": raw_b,
                "dv_mapped": bool(dv_match),
                "dv_confidence": round(float(dv_conf), 2),
                "direction": direction,
                "effect_size": effect_size,
                "effect_size_type": effect_type,
                "sample_n": global_sample,
                "p_value": stats.get("p_value"),
                "context": "correlation_text",
                "source_table_id": table.get("table_id"),
                "source_page": table.get("page"),
                "source_quote": row_text[:500],
                "extraction_confidence": 0.78 if stats.get("p_value") is not None else 0.7,
                "vocabulary_mapped": bool(iv_match and dv_match),
                "extraction_method": "correlation_text",
                "warnings": [],
            }
        )

    return claims




# ============================================================================
# CORRELATION MATRIX EXTRACTION (Recall Improvement)
# ============================================================================

def _extract_correlation_matrix(
    paper_id: str,
    table: dict[str, Any],
    vocab: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """
    Extract claims from a correlation matrix using Row-Index Mapping.
    
    Strategy:
    1. Parse row labels to build index map: "1. Age" -> {1: "Age"}
    2. Resolve numbered headers: Col "1" -> "Age"
    3. Extract cells (i, j) in lower triangle
    """
    if vocab is None:
        vocab = load_vocabulary()

    claims: list[dict[str, Any]] = []
    rows = table.get("rows", [])
    if not rows:
        return []

    parsed_rows = []
    for row in rows:
        text = _clean_text(row.get("text", "") or row.get("source_quote", ""))
        cols = _parse_col_fields(text)
        parsed_rows.append({"text": text, "cols": cols})

    # Sentence-style correlation rows fallback (no col_N structure available).
    if not any(row["cols"] for row in parsed_rows):
        return _extract_correlation_text_fallback(paper_id, table, vocab)

    # Locate header row by numeric column references (e.g., 1,2,3).
    header_row_idx = 0
    best_numeric_tokens = -1
    for ridx, row in enumerate(parsed_rows[:6]):
        numeric_tokens = 0
        for cidx, token in row["cols"].items():
            if cidx <= 1:
                continue
            if re.fullmatch(r"\(?\d{1,2}\)?", token.strip()):
                numeric_tokens += 1
        if numeric_tokens > best_numeric_tokens:
            best_numeric_tokens = numeric_tokens
            header_row_idx = ridx

    # Build row index -> variable mapping from first-column labels.
    row_idx_to_var: dict[int, dict[str, Any]] = {}
    ordered_rows: list[tuple[int, dict[str, str]]] = []
    next_idx = 1
    for ridx, row in enumerate(parsed_rows):
        if ridx == header_row_idx:
            continue
        first_col = row["cols"].get(1, "") or row["cols"].get(0, "")
        if not first_col:
            first_col = row["text"].split(";")[0]
        # Handle split format: col_1 is index, col_2 is variable name.
        idx = None
        raw_name = ""
        if re.fullmatch(r"\(?\d{1,2}\)?", first_col.strip()):
            idx = int(re.sub(r"\D", "", first_col))
            raw_name = (row["cols"].get(2, "") or "").strip()
        if not raw_name:
            idx, raw_name = _split_row_index_label(first_col)
        if idx is None:
            idx = next_idx
        next_idx = max(next_idx, idx + 1)
        raw_name = raw_name.strip()
        if len(raw_name) < 2:
            continue
        mapped, conf = _map_variable_token(raw_name, vocab, prefer="iv")
        row_idx_to_var[idx] = {"raw": raw_name, "mapped": mapped, "conf": conf, "idx": idx}
        ordered_rows.append((idx, row["cols"]))

    if len(ordered_rows) < 2:
        return _extract_correlation_text_fallback(paper_id, table, vocab)

    # Column mapping from header row with numeric references (1,2,3) -> row vars.
    header_cols = parsed_rows[header_row_idx]["cols"] if parsed_rows else {}
    col_to_var: dict[int, dict[str, Any]] = {}
    for cidx, token in header_cols.items():
        if cidx == 1:
            continue
        token = token.strip()
        if re.fullmatch(r"\(?\d{1,2}\)?", token):
            idx = int(re.sub(r"\D", "", token))
            if idx in row_idx_to_var:
                col_to_var[cidx] = row_idx_to_var[idx]
        elif token:
            mapped, conf = _map_variable_token(token, vocab, prefer="iv")
            col_to_var[cidx] = {"raw": token, "mapped": mapped, "conf": conf, "idx": cidx - 1}

    cell_pattern = re.compile(r"(-?\d?\.\d{2,3})(\*{1,3})?")
    for row_idx, cols in ordered_rows:
        row_var = row_idx_to_var.get(row_idx)
        if not row_var:
            continue
        for cidx, raw_cell in cols.items():
            if cidx == 1:
                continue
            match = cell_pattern.search(raw_cell)
            if not match:
                continue
            r_val = float(match.group(1))
            if not (-1 <= r_val <= 1) or abs(r_val) == 1.0:
                continue
            col_var = col_to_var.get(cidx) or row_idx_to_var.get(cidx - 1)
            if not col_var or col_var["raw"] == row_var["raw"]:
                continue
            if col_var.get("mapped") and row_var.get("mapped") and col_var["mapped"] == row_var["mapped"]:
                continue

            # Keep one triangle only when index information exists.
            if isinstance(col_var.get("idx"), int) and col_var["idx"] >= row_idx:
                continue

            sig_marker = match.group(2) or ""
            p_val = None
            if "***" in sig_marker:
                p_val = 0.001
            elif "**" in sig_marker:
                p_val = 0.01
            elif "*" in sig_marker:
                p_val = 0.05
            elif abs(r_val) < 0.2:
                continue  # precision-first

            stats = {"r": r_val}
            if p_val is not None:
                stats["p_value"] = p_val
            effect_size, effect_type = _convert_to_cohens_d(stats, None)
            direction = "increase" if r_val > 0 else "decrease"

            claims.append(
                {
                    "claim_id": _generate_claim_id(paper_id, table.get("table_id"), len(claims) + 1),
                    "paper_id": paper_id,
                    "iv": col_var.get("mapped"),
                    "iv_raw": col_var.get("raw"),
                    "iv_mapped": bool(col_var.get("mapped")),
                    "iv_confidence": round(float(col_var.get("conf", 0.0)), 2),
                    "dv": row_var.get("mapped"),
                    "dv_raw": row_var.get("raw"),
                    "dv_mapped": bool(row_var.get("mapped")),
                    "dv_confidence": round(float(row_var.get("conf", 0.0)), 2),
                    "direction": direction,
                    "effect_size": effect_size,
                    "effect_size_type": effect_type,
                    "sample_n": None,
                    "p_value": p_val,
                    "context": "correlation_matrix",
                    "source_table_id": table.get("table_id"),
                    "source_page": table.get("page"),
                    "source_quote": f"{row_var.get('raw')} was associated with {col_var.get('raw')} (r = {r_val}).",
                    "extraction_confidence": 0.82 if p_val is not None else 0.72,
                    "vocabulary_mapped": bool(col_var.get("mapped") and row_var.get("mapped")),
                    "extraction_method": "correlation_matrix",
                    "warnings": [],
                }
            )

    if claims:
        return claims
    return _extract_correlation_text_fallback(paper_id, table, vocab)


# ============================================================================
# STEPWISE REGRESSION EXTRACTION (Recall Improvement)
# ============================================================================

def _extract_stepwise_regression(
    paper_id: str,
    table: dict[str, Any],
    vocab: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """
    Extract claims from Stepwise Regression tables.
    
    Structure:
    - Independent variables in rows.
    - "Model 1", "Step 2" blocks.
    - Dependent variable often in caption or header.
    """
    if vocab is None: vocab = load_vocabulary()
    
    claims: list[dict[str, Any]] = []
    rows = table.get("rows", [])
    if not rows:
        return []
    col_semantics = _infer_stat_column_semantics(rows)

    dv_raw, dv_match, dv_conf = _extract_caption_first_dv(table, vocab)
    if not dv_match:
        # Fallback to header inference
        _, dv_cand, conf = _infer_iv_dv_from_headers(rows[:3], vocab)
        if dv_cand:
            dv_match = dv_cand
            dv_conf = conf
            dv_raw = dv_cand
    if not dv_match:
        return []

    current_step = "step_1"
    global_sample = _extract_sample_size(
        " ".join(
            [
                str(table.get("sample_content") or ""),
                str(table.get("title") or ""),
                str(table.get("abstract") or ""),
                *[r.get("text", "") for r in rows[:8]],
            ]
        )
    )

    for row in rows:
        raw_text = _clean_text(row.get("text", "") or row.get("source_quote", ""))
        if not raw_text:
            continue

        step_match = re.search(r"\b(step|model)\s*(\d+)\b", raw_text, re.I)
        if step_match and len(raw_text) <= 45:
            current_step = f"{step_match.group(1).lower()}_{step_match.group(2)}"
            continue

        cols = _parse_col_fields(raw_text)
        predictor = cols.get(1, raw_text.split(";")[0]).strip()
        if re.search(r"\b(constant|intercept|model|step)\b", predictor, re.I):
            continue

        stats = _extract_statistics(raw_text)
        stats = _augment_stats_from_semantic_columns(raw_text, stats, col_semantics)
        if not any(k in stats for k in ["beta", "t_value", "f_value", "p_value"]):
            continue
        if ("beta" in stats and abs(stats["beta"]) < 0.05) and (not stats.get("is_significant", False)):
            continue

        iv_match, iv_conf = find_closest_iv(predictor, vocab)
        if not iv_match or iv_conf < 0.5:
            continue

        direction = _detect_direction(raw_text, stats)
        sample_n = stats.get("sample_n") or _infer_sample_size_from_stats(stats) or global_sample
        effect_size, effect_type = _convert_to_cohens_d(stats, sample_n)

        claim = {
            "claim_id": _generate_claim_id(paper_id, table.get("table_id"), len(claims) + 1),
            "paper_id": paper_id,
            "iv": iv_match,
            "iv_raw": predictor,
            "iv_mapped": True,
            "iv_confidence": round(iv_conf, 2),
            "dv": dv_match,
            "dv_raw": dv_raw or dv_match,
            "dv_mapped": True,
            "dv_confidence": round(dv_conf, 2),
            "direction": direction,
            "effect_size": effect_size,
            "effect_size_type": effect_type,
            "sample_n": sample_n,
            "p_value": stats.get("p_value"),
            "context": current_step,
            "source_table_id": table.get("table_id"),
            "source_page": table.get("page"),
            "source_quote": raw_text[:500],
            "extraction_confidence": round(min(0.9, 0.45 + 0.25 * iv_conf + 0.2 * dv_conf), 2),
            "vocabulary_mapped": True,
            "extraction_method": "stepwise_regression",
            "warnings": [],
        }
        claims.append(claim)
        
    return claims


def _enhanced_extract_with_codex(
    table: dict[str, Any],
    vocabulary: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Enhanced extraction using Codex improvements.
    
    Integrates:
    - Semantic Routing (Correlation, Stepwise)
    - Table semantic profiling
    - Row-level classification
    - Header-based IV/DV inference
    - Confidence decomposition
    """
    claims: list[dict[str, Any]] = []
    rows = table.get("rows", [])

    if not rows:
        return []

    paper_id = table.get("paper_id", "unknown")
    table_id = table.get("table_id")

    # STEP 1: Build table semantic profile
    table_profile = build_table_content_profile(table)
    
    # NEW: Semantic Type Routing
    semantic_type = table_profile.get("semantic_type", "unknown")
    semantic_conf = table_profile.get("semantic_confidence", 0.5)

    # 1.1 Specialized Strategies
    if semantic_type == "correlation_matrix":
        return _extract_correlation_matrix(paper_id, table, vocabulary)
        
    if semantic_type == "stepwise_regression":
        return _extract_stepwise_regression(paper_id, table, vocabulary)

    # Gate 1: Reject non-extractable table types 
    if not table_profile.get("extractable", True):
        return []

    # STEP 2: Classify rows and filter
    row_profiles: list[tuple[dict[str, Any], RowProfile]] = []
    for row in rows:
        text = row.get("text") or row.get("source_quote") or row.get("statement") or ""
        profile = classify_row_content(text)
        row_profiles.append((row, profile))

    # Keep only HEADER, STAT_ROW, and TEXT_ROW with stats
    extractable_rows = [
        (row, profile) for row, profile in row_profiles
        if profile.label in {"HEADER", "STAT_ROW", "TEXT_ROW", "GROUP_LABEL"}
        and profile.confidence >= 0.5
    ]

    if not extractable_rows:
        return []

    # STEP 3: Hard negative filtering
    row_texts = [row.get("text") or row.get("source_quote") or "" for row, _ in extractable_rows]
    kept_rows_data, rejected = filter_hard_negatives(
        [{"text": text, "row": row, "profile": profile} for (row, profile), text in zip(extractable_rows, row_texts)]
    )

    # STEP 4: Header-based IV/DV inference
    header_iv, header_dv, header_conf = _infer_iv_dv_from_headers(rows, vocabulary)
    col_semantics = _infer_stat_column_semantics(rows)

    # STEP 5: Extract from each kept row
    all_text = " ".join(
        [
            str(table.get("sample_content") or ""),
            str(table.get("title") or ""),
            str(table.get("abstract") or ""),
            *row_texts,
        ]
    )
    global_context = _detect_context(all_text)
    global_sample = _extract_sample_size(all_text)

    claim_seq = 0

    for item in kept_rows_data:
        row = item.get("row", item)
        profile = item.get("profile")
        row_text = item.get("text", "")

        if not row_text or len(row_text.strip()) < 15:
            continue

        # Skip header rows for claim extraction (they provide context only)
        if profile and profile.label == "HEADER":
            continue

        # Normalize OCR text
        normalized_text = normalize_ocr_text(row_text)

        # Extract statistics with robust p-value parsing
        stats = _extract_statistics(normalized_text)
        stats = _augment_stats_from_semantic_columns(normalized_text, stats, col_semantics)
        sample_n = (
            _extract_sample_size(normalized_text)
            or stats.get("sample_n")
            or _infer_sample_size_from_stats(stats)
            or global_sample
        )

        # Row quality based on profile
        row_quality = profile.confidence if profile else 0.6

        # Try to extract variable pairs (with header inference)
        var_candidates = _extract_variables_from_row(normalized_text, vocabulary, header_iv, header_dv)

        for candidate in var_candidates:
            iv_raw = candidate.get("iv_raw", "")
            dv_raw = candidate.get("dv_raw", "")

            # Map to vocabulary
            iv_match, iv_conf = find_closest_iv(iv_raw, vocabulary)
            dv_match, dv_conf = find_closest_dv(dv_raw, vocabulary)

            # Use header-inferred values as fallback
            if not iv_match and candidate.get("header_inferred_iv"):
                iv_match = candidate["header_inferred_iv"]
                iv_conf = header_conf * 0.8  # Discount for inference

            if not dv_match and candidate.get("header_inferred_dv"):
                dv_match = candidate["header_inferred_dv"]
                dv_conf = header_conf * 0.8

            # Detect direction (with statistical sign awareness)
            direction = _detect_direction(normalized_text, stats)

            # Convert effect size
            effect_size, effect_type = _convert_to_cohens_d(stats, sample_n)

            # Compute confidence decomposition
            stat_parse_conf = 0.8 if any(k in stats for k in ["beta", "r", "f_value", "t_value", "eta_squared", "cohens_d"]) else 0.3
            if "p_value" in stats:
                stat_parse_conf += 0.1

            conf_decomp = ConfidenceDecomposition(
                table_type_confidence=semantic_conf,
                row_quality_confidence=row_quality,
                iv_map_confidence=iv_conf if iv_match else 0.0,
                dv_map_confidence=dv_conf if dv_match else 0.0,
                stat_parse_confidence=min(0.95, stat_parse_conf),
            )

            # Skip claims that don't meet thresholds
            if not conf_decomp.meets_thresholds():
                continue

            claim_seq += 1
            claims.append({
                "claim_id": _generate_claim_id(paper_id, table_id, claim_seq),
                "paper_id": paper_id,
                "iv": iv_match,
                "iv_raw": iv_raw,
                "iv_mapped": iv_match is not None,
                "iv_confidence": iv_conf if iv_match else 0.0,
                "dv": dv_match,
                "dv_raw": dv_raw,
                "dv_mapped": dv_match is not None,
                "dv_confidence": dv_conf if dv_match else 0.0,
                "direction": direction,
                "effect_size": effect_size,
                "effect_size_type": effect_type,
                "sample_n": sample_n,
                "p_value": stats.get("p_value"),
                "is_significant": stats.get("is_significant", False),
                "context": global_context,
                "source_table_id": table_id,
                "source_page": table.get("page"),
                "source_quote": normalized_text[:500],
                "extraction_confidence": round(conf_decomp.aggregate(), 3),
                "confidence_decomposition": conf_decomp.to_dict(),
                "vocabulary_mapped": (iv_match is not None) and (dv_match is not None),
                "extraction_method": "enhanced_codex",
                "semantic_type": semantic_type,
            })

    return claims



def _rule_based_extract(
    table: dict[str, Any],
    vocabulary: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Heuristic extraction for when LLM is unavailable.

    1. Look for column headers matching IV/DV vocabulary
    2. Look for statistical values (F, t, r, p) in cells
    3. Look for direction words (increase, decrease, higher, lower)
    4. Construct claims from header-cell pairings

    NOTE: Use _enhanced_extract_with_codex for better precision.
    This is kept for backward compatibility.
    """
    claims: list[dict[str, Any]] = []
    rows = table.get("rows", [])
    
    # Fallback: if no structured rows, try to use sample_content
    if not rows and table.get("sample_content"):
        # Split sample content into lines to simulate rows
        content_lines = str(table.get("sample_content", "")).split('\n')
        rows = [{"text": line, "source_quote": line} for line in content_lines if len(line.strip()) > 10]
        
    paper_id = table.get("paper_id", "unknown")
    table_id = table.get("table_id")

    # Combine all row text for context
    all_text = " ".join(
        [
            str(table.get("sample_content") or ""),
            str(table.get("title") or ""),
            str(table.get("abstract") or ""),
            *[
                (row.get("text") or row.get("source_quote") or row.get("statement") or "")
                for row in rows
            ],
        ]
    )

    # Extract global context
    global_context = _detect_context(all_text)
    global_sample = _extract_sample_size(all_text)
    col_semantics = _infer_stat_column_semantics(rows)

    claim_seq = 0

    for row in rows:
        row_text = row.get("text") or row.get("source_quote") or row.get("statement") or ""
        if not row_text or len(row_text.strip()) < 15:
            continue

        # Extract statistics from this row
        stats = _extract_statistics(row_text)
        stats = _augment_stats_from_semantic_columns(row_text, stats, col_semantics)
        sample_n = (
            _extract_sample_size(row_text)
            or stats.get("sample_n")
            or _infer_sample_size_from_stats(stats)
            or global_sample
        )

        # Try to extract variable pairs
        var_candidates = _extract_variables_from_row(row_text, vocabulary)

        for candidate in var_candidates:
            iv_raw = candidate["iv_raw"]
            dv_raw = candidate["dv_raw"]

            # Map to vocabulary
            iv_match, iv_conf = find_closest_iv(iv_raw, vocabulary)
            dv_match, dv_conf = find_closest_dv(dv_raw, vocabulary)

            # Detect direction
            direction = _detect_direction(row_text)

            # Convert effect size
            effect_size, effect_type = _convert_to_cohens_d(stats, sample_n)

            # Compute extraction confidence
            conf = 0.5
            if iv_match and iv_conf > 0.6:
                conf += 0.15
            if dv_match and dv_conf > 0.6:
                conf += 0.15
            if effect_size is not None:
                conf += 0.1
            if direction != "unknown":
                conf += 0.05
            if sample_n and sample_n > 20:
                conf += 0.05

            conf = min(0.95, conf)

            claim_seq += 1
            claims.append({
                "claim_id": _generate_claim_id(paper_id, table_id, claim_seq),
                "paper_id": paper_id,
                "iv": iv_match,
                "iv_raw": iv_raw,
                "iv_mapped": iv_match is not None,
                "iv_confidence": iv_conf if iv_match else 0.0,
                "dv": dv_match,
                "dv_raw": dv_raw,
                "dv_mapped": dv_match is not None,
                "dv_confidence": dv_conf if dv_match else 0.0,
                "direction": direction,
                "effect_size": effect_size,
                "effect_size_type": effect_type,
                "sample_n": sample_n,
                "p_value": stats.get("p_value"),
                "context": global_context,
                "source_table_id": table_id,
                "source_page": table.get("page"),
                "source_quote": row_text[:500],
                "extraction_confidence": round(conf, 2),
                "vocabulary_mapped": (iv_match is not None) and (dv_match is not None),
                "extraction_method": "rule_based",
            })

    # If no variable pairs found, try to extract from statistics alone
    if not claims and rows:
        # Look for regression tables (beta weights)
        for row in rows:
            row_text = row.get("text") or row.get("source_quote") or ""
            stats = _extract_statistics(row_text)
            stats = _augment_stats_from_semantic_columns(row_text, stats, col_semantics)

            if any(k in stats for k in ["beta", "r", "f_value", "t_value", "eta_squared"]):
                # Try to identify predictor and outcome from row structure
                iv_match, _ = find_closest_iv(row_text, vocabulary)
                dv_match, _ = find_closest_dv(row_text, vocabulary)

                if iv_match or dv_match:
                    direction = _detect_direction(row_text)
                    sample_n = (
                        _extract_sample_size(row_text)
                        or stats.get("sample_n")
                        or _infer_sample_size_from_stats(stats)
                        or global_sample
                    )
                    effect_size, effect_type = _convert_to_cohens_d(stats, sample_n)

                    claim_seq += 1
                    claims.append({
                        "claim_id": _generate_claim_id(paper_id, table_id, claim_seq),
                        "paper_id": paper_id,
                        "iv": iv_match,
                        "iv_raw": row_text[:100] if iv_match else None,
                        "iv_mapped": iv_match is not None,
                        "iv_confidence": 0.5 if iv_match else 0.0,
                        "dv": dv_match,
                        "dv_raw": row_text[:100] if dv_match else None,
                        "dv_mapped": dv_match is not None,
                        "dv_confidence": 0.5 if dv_match else 0.0,
                        "direction": direction,
                        "effect_size": effect_size,
                        "effect_size_type": effect_type,
                        "sample_n": sample_n,
                        "p_value": stats.get("p_value"),
                        "context": global_context,
                        "source_table_id": table_id,
                        "source_page": table.get("page"),
                        "source_quote": row_text[:500],
                        "extraction_confidence": 0.4,
                        "vocabulary_mapped": False,
                        "extraction_method": "rule_based_stats_only",
                    })

    return claims


def extract_claims_from_table(
    table: dict[str, Any],
    paper_context: dict[str, Any] | None = None,
    vocabulary: dict[str, Any] | None = None,
    method: str = "enhanced",
) -> list[dict[str, Any]]:
    """
    Extract structured IV→DV claims from a classified table.

    Args:
        table: Reconstructed table from table_classifier (D.3)
            Expected keys: paper_id, page, rows, table_id (optional)
        paper_context: Optional context dict with title, abstract, article_type
        vocabulary: Vocabulary dict from D.1 (loads default if None)
        method: "enhanced" (Codex improvements), "rule_based" (legacy), or "llm"

    Returns:
        List of claim dicts with:
        - iv, dv, direction, effect_size, sample_n, context
        - source_quote, extraction_confidence, vocabulary_mapped
        - (enhanced only) confidence_decomposition, is_significant, semantic_type
    """
    if vocabulary is None:
        vocabulary = load_vocabulary()

    # Add paper context to table for extraction
    if paper_context:
        table = {**table, **paper_context}

    if method == "enhanced":
        # Use Codex-improved extraction with all enhancements
        return _enhanced_extract_with_codex(table, vocabulary)
    elif method == "rule_based":
        # Legacy extraction for backward compatibility
        return _rule_based_extract(table, vocabulary)
    elif method == "llm":
        # LLM extraction would go here
        # For now, fall back to enhanced
        return _enhanced_extract_with_codex(table, vocabulary)
    else:
        raise ValueError(f"Unknown extraction method: {method}. Use 'enhanced', 'rule_based', or 'llm'.")


def extract_claims_from_paper(
    paper_id: str,
    tables: list[dict[str, Any]],
    paper_context: dict[str, Any] | None = None,
    vocabulary: dict[str, Any] | None = None,
    method: str = "rule_based",
) -> list[dict[str, Any]]:
    """
    Extract all claims from all extractable tables in a paper.

    Args:
        paper_id: Paper identifier
        tables: List of classified tables from table_classifier
        paper_context: Optional context (title, abstract, article_type)
        vocabulary: Vocabulary dict
        method: "llm" or "rule_based"

    Returns:
        List of all claims from all tables, deduplicated.
    """
    if vocabulary is None:
        vocabulary = load_vocabulary()

    all_claims: list[dict[str, Any]] = []

    for table in tables:
        # Ensure paper_id is set
        table_with_paper = {**table, "paper_id": paper_id}

        claims = extract_claims_from_table(
            table_with_paper,
            paper_context=paper_context,
            vocabulary=vocabulary,
            method=method,
        )
        all_claims.extend(claims)
    
    # NEW: Validate Direction Consistency (Precision)
    all_claims = _validate_direction_consistency(all_claims)

    # Deduplicate: same IV+DV+direction from same paper
    seen = set()
    deduped: list[dict[str, Any]] = []

    for claim in all_claims:
        key = (
            claim.get("paper_id"),
            claim.get("iv"),
            claim.get("dv"),
            claim.get("direction"),
        )
        if key not in seen:
            seen.add(key)
            deduped.append(claim)

    return deduped


# Header tokens that indicate IV (predictor) columns
_IV_HEADER_PATTERNS = [
    re.compile(r"\bpredictor[s]?\b", re.I),
    re.compile(r"\bindependent\s+var", re.I),
    re.compile(r"\bcondition[s]?\b", re.I),
    re.compile(r"\bgroup[s]?\b", re.I),
    re.compile(r"\bexposure\b", re.I),
]

# Header tokens that indicate DV (outcome) columns
_DV_HEADER_PATTERNS = [
    re.compile(r"\boutcome[s]?\b", re.I),
    re.compile(r"\bdependent\s+var", re.I),
    re.compile(r"\bcriterion\b", re.I),
    re.compile(r"\bresponse\b", re.I),
    re.compile(r"\beffect[s]?\b", re.I),
    re.compile(r"\bresult[s]?\b", re.I),
]

_ARTICLE_FAMILY_ALIASES = {
    "empirical": "empirical_v2",
    "empirical_v2": "empirical_v2",
    "experimental": "empirical_v2",
    "experiment": "empirical_v2",
    "review": "narrative_review",
    "narrative_review": "narrative_review",
    "systematic_review": "systematic_review",
    "meta": "meta_analysis",
    "meta_analysis": "meta_analysis",
    "meta-analysis": "meta_analysis",
    "observational": "observational_field",
    "observational_field": "observational_field",
    "case_study": "case_study",
    "mixed_methods": "mixed_methods",
    "theoretical": "theoretical",
    "conceptual_framework": "conceptual_framework",
    "thought_piece": "thought_piece",
    "interview": "interview_study",
    "interview_study": "interview_study",
    "ethnographic": "ethnographic",
    "grounded_theory": "grounded_theory",
    "phenomenological": "phenomenological",
}

_NULL_CLAIM_PATTERN = re.compile(r"\b(non[- ]?significant|null|no effect|ns\b)\b", re.I)
_MODERATED_CLAIM_PATTERN = re.compile(r"\b(interaction|moderat|depends on|contingent)\b", re.I)
_MECHANISTIC_CLAIM_PATTERN = re.compile(r"\b(mediat|mechanis|pathway|process)\b", re.I)
_CAUSAL_CLAIM_PATTERN = re.compile(r"\b(randomi|intervention|treatment|manipulat|causal|experiment)\b", re.I)
_SAMPLE_CLAIM_PATTERN = re.compile(r"\b(sample|participant|cohort|n\s*=|demograph|male|female|age\b|years?)\b", re.I)
_METHOD_CLAIM_PATTERN = re.compile(r"\b(method|procedure|protocol|instrument|questionnaire|scale|anova|regression|model|analysis)\b", re.I)
_THEORY_CLAIM_PATTERN = re.compile(r"\b(theory|framework|model predicts|hypothesis)\b", re.I)

_CLAIM_TYPE_TO_RULE_TYPE = {
    "sample": "constraint",
    "methodology": "constraint",
    "descriptive": "constraint",
    "theory_link": "interaction",
    "inter_article_relation": "interaction",
}

_CLAIM_TYPE_FIELD_TARGETS = {
    "causal": ["findings", "synthesis_conclusions", "themes_or_constructs"],
    "associational": ["findings", "synthesis_conclusions", "themes_or_constructs"],
    "moderated": ["findings", "moderators", "synthesis_conclusions"],
    "null": ["findings", "limitations", "evidence_gaps"],
    "mechanistic": ["mechanisms", "mechanism_or_causal_logic", "bridge_warrants"],
    "theory_link": ["central_proposition", "mechanism_or_causal_logic", "bridge_warrants"],
    "sample": ["participants", "sample_context", "evidence_base_summary"],
    "methodology": ["design_type", "data_collection_method", "measures"],
    "inter_article_relation": ["evidence_base_summary", "synthesis_conclusions", "methodological_critiques"],
    "descriptive": ["minimum_safe_summary", "findings", "synthesis_conclusions"],
}

_ATTACK_TYPE_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "confounder": [
        re.compile(r"\bconfound(?:er|ing)?\b", re.I),
        re.compile(r"\bunmeasured\b.*\bvariable\b", re.I),
    ],
    "boundary_condition": [
        re.compile(r"\bonly\s+(?:when|if)\b", re.I),
        re.compile(r"\bunder\s+(?:specific|certain)\s+conditions?\b", re.I),
    ],
    "overgeneralization": [
        re.compile(r"\btoo\s+broad\b", re.I),
        re.compile(r"\bdoes\s+not\s+generalize\b", re.I),
    ],
    "mechanism": [
        re.compile(r"\bmechanism\b", re.I),
        re.compile(r"\bpathway\b", re.I),
        re.compile(r"\bmediat(?:e|ed|ion)\b", re.I),
    ],
    "measurement": [
        re.compile(r"\bmeasurement\b", re.I),
        re.compile(r"\binstrument\b", re.I),
        re.compile(r"\boperationaliz", re.I),
    ],
    "replication": [
        re.compile(r"\breplication\b", re.I),
        re.compile(r"\bfailed\s+to\s+replicate\b", re.I),
    ],
    "dose_response": [
        re.compile(r"\bdose\b", re.I),
        re.compile(r"\bduration\b", re.I),
        re.compile(r"\bintensity\b", re.I),
    ],
    "temporal": [
        re.compile(r"\bshort[- ]term\b", re.I),
        re.compile(r"\blong[- ]term\b", re.I),
        re.compile(r"\bfollow[- ]up\b", re.I),
    ],
}


def _normalize_article_family(value: str | None) -> str:
    key = str(value or "").strip().lower()
    if not key:
        return "unknown"
    if key in _ARTICLE_FAMILY_ALIASES:
        return _ARTICLE_FAMILY_ALIASES[key]
    if "systematic" in key:
        return "systematic_review"
    if "meta" in key:
        return "meta_analysis"
    if "narrative" in key or key == "review":
        return "narrative_review"
    if "observational" in key:
        return "observational_field"
    if "case" in key:
        return "case_study"
    if "mixed" in key:
        return "mixed_methods"
    if any(token in key for token in ("empirical", "experiment", "quasi", "anova", "regression", "rct")):
        return "empirical_v2"
    if "interview" in key:
        return "interview_study"
    if "ethnograph" in key:
        return "ethnographic"
    if "grounded" in key:
        return "grounded_theory"
    if "phenomen" in key:
        return "phenomenological"
    if "conceptual" in key or "framework" in key:
        return "conceptual_framework"
    if "thought" in key or "commentary" in key:
        return "thought_piece"
    if "theor" in key:
        return "theoretical"
    return "unknown"


def _infer_claim_type(claim: dict[str, Any], article_type_family: str) -> str:
    raw = str(claim.get("claim_type") or "").strip().lower()
    if raw:
        return raw

    direction = str(claim.get("direction") or "").strip().lower()
    iv = str(claim.get("iv") or claim.get("iv_raw") or "").strip()
    dv = str(claim.get("dv") or claim.get("dv_raw") or "").strip()
    text_blob = " ".join(
        str(claim.get(k) or "")
        for k in ("source_quote", "context", "semantic_type", "extraction_method")
    ).lower()

    has_pair = bool(iv and dv)
    if has_pair:
        if direction in {"no_effect", "null"} or _NULL_CLAIM_PATTERN.search(text_blob):
            return "null"
        if _MODERATED_CLAIM_PATTERN.search(text_blob):
            return "moderated"
        if _MECHANISTIC_CLAIM_PATTERN.search(text_blob):
            return "mechanistic"
        if _CAUSAL_CLAIM_PATTERN.search(text_blob) and article_type_family in {
            "empirical_v2",
            "observational_field",
            "case_study",
            "mixed_methods",
            "empirical",
        }:
            return "causal"
        return "associational"

    if _SAMPLE_CLAIM_PATTERN.search(text_blob):
        return "sample"
    if _METHOD_CLAIM_PATTERN.search(text_blob):
        return "methodology"
    if _THEORY_CLAIM_PATTERN.search(text_blob):
        return "theory_link"
    return "descriptive"


def _infer_rule_type(claim_type: str) -> str:
    return _CLAIM_TYPE_TO_RULE_TYPE.get(claim_type, "edge")


def _field_targets_for_claim_type(claim_type: str, article_type_family: str) -> list[str]:
    contract = get_family_contract(article_type_family)
    allowed = set(contract.required_fields) | set(contract.optional_fields)
    preferred = _CLAIM_TYPE_FIELD_TARGETS.get(claim_type, [])
    targets = [field for field in preferred if field in allowed]
    if targets:
        return targets
    if contract.required_fields:
        return list(contract.required_fields[:3])
    return []


def detect_attack_patterns_from_text(text: str) -> list[dict[str, Any]]:
    """ATK-2: Detect argument-attack cues in claim-supporting text."""
    if not text:
        return []

    matches: list[dict[str, Any]] = []
    for attack_type, patterns in _ATTACK_TYPE_PATTERNS.items():
        matched_terms: list[str] = []
        for pattern in patterns:
            found = pattern.search(text)
            if found:
                matched_terms.append(found.group(0))

        if matched_terms:
            confidence = min(0.95, 0.4 + 0.15 * len(matched_terms))
            matches.append(
                {
                    "attack_type": attack_type,
                    "matched_terms": sorted(set(matched_terms)),
                    "confidence": round(confidence, 3),
                }
            )
    return matches


def _annotate_claim_semantics(
    claims: list[dict[str, Any]],
    table: dict[str, Any],
    paper_context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not claims:
        return claims

    family = _normalize_article_family(
        str(table.get("article_type_family") or table.get("article_type") or "")
    )
    if family == "unknown" and paper_context:
        family = _normalize_article_family(
            str(
                paper_context.get("article_type_family")
                or paper_context.get("article_type")
                or ""
            )
        )

    contract = get_family_contract(family)
    out: list[dict[str, Any]] = []
    for claim in claims:
        c = dict(claim)
        claim_type = _infer_claim_type(c, family)
        c["claim_type"] = claim_type
        c.setdefault("rule_type", _infer_rule_type(claim_type))
        c.setdefault("article_type_family", family)
        c.setdefault("field_contract_family", contract.family)
        c["field_targets"] = _field_targets_for_claim_type(claim_type, family)

        # ATK-2: Attach lightweight argument-attack cues from extracted text.
        attack_text = " ".join(
            str(c.get(key) or "")
            for key in ("source_quote", "context", "semantic_type", "iv_raw", "dv_raw")
        ).strip()
        attack_patterns = detect_attack_patterns_from_text(attack_text)
        c["attack_patterns"] = attack_patterns
        c["attack_detected"] = bool(attack_patterns)
        c["attack_types"] = [m["attack_type"] for m in attack_patterns]
        c["attack_max_confidence"] = (
            max((float(m.get("confidence", 0.0)) for m in attack_patterns), default=0.0)
        )
        out.append(c)
    return out


def _infer_iv_dv_from_headers(
    rows: list[dict[str, Any]],
    vocab: dict[str, Any] | None = None,
) -> tuple[str | None, str | None, float]:
    """
    Infer IV and DV from table header structure (Codex suggestion #6).

    For regression tables: predictors in left-most columns, outcomes in column headers.
    For ANOVA tables: conditions are IVs, measured variables are DVs.

    Returns: (iv_name, dv_name, confidence)
    """
    if not rows:
        return None, None, 0.0

    # Get first few rows as potential headers
    header_texts = []
    for row in rows[:3]:
        text = row.get("text") or row.get("source_quote") or ""
        if text:
            header_texts.append(text.lower())

    combined_headers = " ".join(header_texts)

    # Look for IV indicators
    iv_candidate = None
    iv_conf = 0.0
    for pattern in _IV_HEADER_PATTERNS:
        if pattern.search(combined_headers):
            # Try to extract the actual variable name
            match = pattern.search(combined_headers)
            if match:
                # Look for vocabulary match in surrounding context
                context = combined_headers[max(0, match.start()-50):min(len(combined_headers), match.end()+50)]
                iv_match, conf = find_closest_iv(context, vocab)
                if conf > iv_conf:
                    iv_candidate = iv_match
                    iv_conf = conf

    # Look for DV indicators
    dv_candidate = None
    dv_conf = 0.0
    for pattern in _DV_HEADER_PATTERNS:
        if pattern.search(combined_headers):
            match = pattern.search(combined_headers)
            if match:
                context = combined_headers[max(0, match.start()-50):min(len(combined_headers), match.end()+50)]
                dv_match, conf = find_closest_dv(context, vocab)
                if conf > dv_conf:
                    dv_candidate = dv_match
                    dv_conf = conf

    # Confidence is average of IV and DV confidence
    overall_conf = (iv_conf + dv_conf) / 2 if (iv_candidate or dv_candidate) else 0.0

    return iv_candidate, dv_candidate, overall_conf


def _extract_variables_from_row(
    row_text: str,
    vocab: dict[str, Any] | None = None,
    header_iv: str | None = None,
    header_dv: str | None = None,
    row_has_stat_signal: bool = False,
) -> list[dict[str, Any]]:
    """
    Extract potential IV-DV pairs from a single row of text.

    Uses heuristics to identify variable mentions and map them to vocabulary.
    Can use header-inferred IV/DV as defaults when text patterns don't match.
    """
    if not row_text or len(row_text.strip()) < 10:
        return []

    candidates = []
    relation_signal = bool(
        re.search(
            r"(?:->|→|\b(affect|effect|impact|influenc|predict|associate|correlat|relat(?:ed)?\s+to|leads?\s+to|results?\s+in|increas|decreas)\b)",
            row_text,
            re.I,
        )
    )

    # Look for patterns like "X affects Y", "X → Y", "X leads to Y"
    causal_patterns = [
        re.compile(r"([^;.]+?)\s+(?:affects?|influences?|impacts?|causes?)\s+([^;.]+)", re.I),
        re.compile(r"([^;.]+?)\s+(?:leads?\s+to|results?\s+in)\s+([^;.]+)", re.I),
        re.compile(r"([^;.]+?)\s+(?:increases?|decreases?|reduces?|enhances?)\s+([^;.]+)", re.I),
        re.compile(r"([^;.]+?)\s*(?:→|->|=>)+\s*([^;.]+)", re.I),
        # Passive voice
        re.compile(r"([^;.]+?)\s+(?:affected|influenced|impacted|caused)\s+by\s+([^;.]+)", re.I),
        re.compile(r"([^;.]+?)\s+was\s+(?:associated|correlated)\s+with\s+([^;.]+)", re.I),
        # Correlation sentence variants
        re.compile(r"([^;.]+?)\s+and\s+([^;.]+?)\s*:\s*r\s*=\s*[-.\d]+", re.I),
        re.compile(r"([^;.]+?)\s+r\s*=\s*[-.\d]+\s+(?:with|to)\s+([^;.]+)", re.I),
    ]

    for pattern in causal_patterns:
        matches = pattern.finditer(row_text)
        for match in matches:
            iv_raw = match.group(1).strip()[:100]
            dv_raw = match.group(2).strip()[:100]

            if len(iv_raw) > 3 and len(dv_raw) > 3:
                candidates.append({
                    "iv_raw": iv_raw,
                    "dv_raw": dv_raw,
                    "source_text": row_text,
                })

    # If no explicit pair pattern is present, only use header fallback when the row
    # still looks claim-like (relation cue or statistical evidence).
    if not candidates and (header_iv or header_dv):
        stats_hint = _extract_statistics(row_text)
        has_stat_signal = any(
            key in stats_hint
            for key in ("beta", "r", "t_value", "f_value", "eta_squared", "cohens_d", "p_value")
        )
        if not (relation_signal or has_stat_signal or row_has_stat_signal):
            return candidates

        # Extract row-level variable mentions at conservative confidence.
        iv_match, iv_conf = find_closest_iv(row_text, vocab)
        dv_match, dv_conf = find_closest_dv(row_text, vocab)
        if iv_conf < 0.65:
            iv_match = None
        if dv_conf < 0.65:
            dv_match = None

        if (iv_match or header_iv) and (dv_match or header_dv):
            candidates.append({
                "iv_raw": row_text[:80] if iv_match else (header_iv or row_text[:80]),
                "dv_raw": row_text[:80] if dv_match else (header_dv or row_text[:80]),
                "source_text": row_text,
                "header_inferred_iv": header_iv,
                "header_inferred_dv": header_dv,
            })

    return candidates


def _enhanced_extract_with_codex(
    table: dict[str, Any],
    vocabulary: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Enhanced extraction using Codex improvements.

    Integrates:
    - Table semantic profiling (pre-filter non-extractable tables)
    - Row-level classification (filter junk/citation/demographic rows)
    - Hard negative filtering
    - Header-based IV/DV inference
    - Confidence decomposition
    - Significance-aware extraction
    """
    claims: list[dict[str, Any]] = []
    rows = table.get("rows", [])

    if not rows:
        return []

    paper_id = table.get("paper_id", "unknown")
    table_id = table.get("table_id")

    # STEP 1: Build table semantic profile
    table_profile = build_table_content_profile(table)
    semantic_type = table_profile.get("semantic_type", "unknown")
    semantic_conf = table_profile.get("semantic_confidence", 0.5)
    table_type_hint = str(table.get("type") or "").upper()

    # Semantic routing for special table types (correlation/stepwise regression).
    preview = " ".join((r.get("text") or "") for r in rows[:8]).lower()
    if semantic_type == "unknown" and (
        table_type_hint in {"RESULTS_CORRELATION", "CORRELATION_MATRIX"}
        or ("correlation" in preview and "r =" in preview)
    ):
        semantic_type = "correlation_matrix"
    stepwise_cue_count = sum(
        1 for token in ("step", "model", "beta", "β", "r2", "r²", "predictor", "coefficient")
        if token in preview
    )
    if (
        table_type_hint == "RESULTS_REGRESSION"
        or (semantic_type == "unknown" and stepwise_cue_count >= 2)
    ):
        semantic_type = "stepwise_regression"

    if semantic_type == "correlation_matrix":
        return _extract_correlation_matrix(paper_id, table, vocabulary)
    if semantic_type == "stepwise_regression":
        return _extract_stepwise_regression(paper_id, table, vocabulary)

    # Gate 1: Reject non-extractable table types
    if not table_profile.get("extractable", True):
        return []

    # STEP 2: Classify rows and filter
    row_profiles: list[tuple[dict[str, Any], RowProfile]] = []
    for row in rows:
        text = row.get("text") or row.get("source_quote") or row.get("statement") or ""
        profile = classify_row_content(text)
        row_profiles.append((row, profile))

    # Keep only HEADER, STAT_ROW, and TEXT_ROW with stats
    extractable_rows = [
        (row, profile) for row, profile in row_profiles
        if profile.label in {"HEADER", "STAT_ROW", "TEXT_ROW", "GROUP_LABEL"}
        and profile.confidence >= 0.5
    ]

    if not extractable_rows:
        return []

    # STEP 3: Hard negative filtering
    row_texts = [row.get("text") or row.get("source_quote") or "" for row, _ in extractable_rows]
    kept_rows_data, rejected = filter_hard_negatives(
        [{"text": text, "row": row, "profile": profile} for (row, profile), text in zip(extractable_rows, row_texts)]
    )

    # STEP 4: Header-based IV/DV inference
    header_iv, header_dv, header_conf = _infer_iv_dv_from_headers(rows, vocabulary)
    col_semantics = _infer_stat_column_semantics(rows)

    # STEP 5: Extract from each kept row
    all_text = " ".join(
        [
            str(table.get("sample_content") or ""),
            str(table.get("title") or ""),
            str(table.get("abstract") or ""),
            *row_texts,
        ]
    )
    global_context = _detect_context(all_text)
    global_sample = _extract_sample_size(all_text)

    claim_seq = 0

    for item in kept_rows_data:
        row = item.get("row", item)
        profile = item.get("profile")
        row_text = item.get("text", "")

        if not row_text or len(row_text.strip()) < 15:
            continue

        # Skip header rows for claim extraction (they provide context only)
        if profile and profile.label == "HEADER":
            continue

        # Normalize OCR text
        normalized_text = normalize_ocr_text(row_text)
        if _is_garbage(normalized_text):
            continue

        # Extract statistics with robust p-value parsing
        stats = _extract_statistics(normalized_text)
        stats = _augment_stats_from_semantic_columns(normalized_text, stats, col_semantics)
        has_stat_signal = any(
            key in stats
            for key in ("beta", "r", "t_value", "f_value", "eta_squared", "cohens_d", "p_value")
        )
        relation_signal = bool(
            re.search(
                r"(?:->|→|\b(affect|effect|impact|influenc|predict|associate|correlat|relat(?:ed)?\s+to|leads?\s+to|results?\s+in|increas|decreas|significant|non[- ]?significant|ns)\b)",
                normalized_text,
                re.I,
            )
        )
        if not (has_stat_signal or relation_signal or (profile and profile.label == "STAT_ROW")):
            continue
        sample_n = (
            _extract_sample_size(normalized_text)
            or stats.get("sample_n")
            or _infer_sample_size_from_stats(stats)
            or global_sample
        )

        # Row quality based on profile
        row_quality = profile.confidence if profile else 0.6

        # Try to extract variable pairs (with header inference)
        var_candidates = _extract_variables_from_row(
            normalized_text,
            vocabulary,
            header_iv,
            header_dv,
            row_has_stat_signal=has_stat_signal,
        )

        for candidate in var_candidates:
            iv_raw = candidate.get("iv_raw", "")
            dv_raw = candidate.get("dv_raw", "")

            # Map to vocabulary
            iv_match, iv_conf = find_closest_iv(iv_raw, vocabulary)
            dv_match, dv_conf = find_closest_dv(dv_raw, vocabulary)

            # Use header-inferred values as fallback
            if not iv_match and candidate.get("header_inferred_iv"):
                iv_match = candidate["header_inferred_iv"]
                iv_conf = header_conf * 0.8  # Discount for inference

            if not dv_match and candidate.get("header_inferred_dv"):
                dv_match = candidate["header_inferred_dv"]
                dv_conf = header_conf * 0.8

            if iv_match and dv_match and iv_match == dv_match:
                continue

            # Detect direction (with statistical sign awareness)
            direction = _detect_direction(normalized_text, stats)

            # Convert effect size
            effect_size, effect_type = _convert_to_cohens_d(stats, sample_n)

            # Compute confidence decomposition
            stat_parse_conf = 0.8 if any(k in stats for k in ["beta", "r", "f_value", "t_value", "eta_squared", "cohens_d"]) else 0.3
            if "p_value" in stats:
                stat_parse_conf += 0.1

            conf_decomp = ConfidenceDecomposition(
                table_type_confidence=semantic_conf,
                row_quality_confidence=row_quality,
                iv_map_confidence=iv_conf if iv_match else 0.0,
                dv_map_confidence=dv_conf if dv_match else 0.0,
                stat_parse_confidence=min(0.95, stat_parse_conf),
            )

            # Skip claims that don't meet thresholds
            if not conf_decomp.meets_thresholds():
                continue
            # Low-signal unknown-direction rows are usually OCR/header leakage.
            if (
                direction == "unknown"
                and not has_stat_signal
                and (not profile or profile.label != "STAT_ROW")
                and conf_decomp.aggregate() < 0.62
            ):
                continue

            claim_seq += 1
            claims.append({
                "claim_id": _generate_claim_id(paper_id, table_id, claim_seq),
                "paper_id": paper_id,
                "iv": iv_match,
                "iv_raw": iv_raw,
                "iv_mapped": iv_match is not None,
                "iv_confidence": iv_conf if iv_match else 0.0,
                "dv": dv_match,
                "dv_raw": dv_raw,
                "dv_mapped": dv_match is not None,
                "dv_confidence": dv_conf if dv_match else 0.0,
                "direction": direction,
                "effect_size": effect_size,
                "effect_size_type": effect_type,
                "sample_n": sample_n,
                "p_value": stats.get("p_value"),
                "is_significant": stats.get("is_significant", False),
                "context": global_context,
                "source_table_id": table_id,
                "source_page": table.get("page"),
                "source_quote": normalized_text[:500],
                "extraction_confidence": round(conf_decomp.aggregate(), 3),
                "confidence_decomposition": conf_decomp.to_dict(),
                "vocabulary_mapped": (iv_match is not None) and (dv_match is not None),
                "extraction_method": "enhanced_codex",
                "semantic_type": semantic_type,
            })

    return claims


def _rule_based_extract(
    table: dict[str, Any],
    vocabulary: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Heuristic extraction for when LLM is unavailable.

    1. Look for column headers matching IV/DV vocabulary
    2. Look for statistical values (F, t, r, p) in cells
    3. Look for direction words (increase, decrease, higher, lower)
    4. Construct claims from header-cell pairings

    NOTE: Use _enhanced_extract_with_codex for better precision.
    This is kept for backward compatibility.
    """
    claims: list[dict[str, Any]] = []
    rows = table.get("rows", [])
    
    # Fallback: if no structured rows, try to use sample_content
    if not rows and table.get("sample_content"):
        # Split sample content into lines to simulate rows
        content_lines = str(table.get("sample_content", "")).split('\n')
        rows = [{"text": line, "source_quote": line} for line in content_lines if len(line.strip()) > 10]
        
    paper_id = table.get("paper_id", "unknown")
    table_id = table.get("table_id")

    # Combine all row text for context
    all_text = " ".join(
        (row.get("text") or row.get("source_quote") or row.get("statement") or "")
        for row in rows
    )

    # Extract global context
    global_context = _detect_context(all_text)
    global_sample = _extract_sample_size(all_text)

    claim_seq = 0

    for row in rows:
        row_text = row.get("text") or row.get("source_quote") or row.get("statement") or ""
        if not row_text or len(row_text.strip()) < 15:
            continue

        # Extract statistics from this row
        stats = _extract_statistics(row_text)
        sample_n = _extract_sample_size(row_text) or global_sample

        # Try to extract variable pairs
        var_candidates = _extract_variables_from_row(row_text, vocabulary)

        for candidate in var_candidates:
            iv_raw = candidate["iv_raw"]
            dv_raw = candidate["dv_raw"]

            # Map to vocabulary
            iv_match, iv_conf = find_closest_iv(iv_raw, vocabulary)
            dv_match, dv_conf = find_closest_dv(dv_raw, vocabulary)

            # Detect direction
            direction = _detect_direction(row_text)

            # Convert effect size
            effect_size, effect_type = _convert_to_cohens_d(stats, sample_n)

            # Compute extraction confidence
            conf = 0.5
            if iv_match and iv_conf > 0.6:
                conf += 0.15
            if dv_match and dv_conf > 0.6:
                conf += 0.15
            if effect_size is not None:
                conf += 0.1
            if direction != "unknown":
                conf += 0.05
            if sample_n and sample_n > 20:
                conf += 0.05

            conf = min(0.95, conf)

            claim_seq += 1
            claims.append({
                "claim_id": _generate_claim_id(paper_id, table_id, claim_seq),
                "paper_id": paper_id,
                "iv": iv_match,
                "iv_raw": iv_raw,
                "iv_mapped": iv_match is not None,
                "iv_confidence": iv_conf if iv_match else 0.0,
                "dv": dv_match,
                "dv_raw": dv_raw,
                "dv_mapped": dv_match is not None,
                "dv_confidence": dv_conf if dv_match else 0.0,
                "direction": direction,
                "effect_size": effect_size,
                "effect_size_type": effect_type,
                "sample_n": sample_n,
                "p_value": stats.get("p_value"),
                "context": global_context,
                "source_table_id": table_id,
                "source_page": table.get("page"),
                "source_quote": row_text[:500],
                "extraction_confidence": round(conf, 2),
                "vocabulary_mapped": (iv_match is not None) and (dv_match is not None),
                "extraction_method": "rule_based",
            })

    # If no variable pairs found, try to extract from statistics alone
    if not claims and rows:
        # Look for regression tables (beta weights)
        for row in rows:
            row_text = row.get("text") or row.get("source_quote") or ""
            stats = _extract_statistics(row_text)

            if any(k in stats for k in ["beta", "r", "f_value", "t_value", "eta_squared"]):
                # Try to identify predictor and outcome from row structure
                iv_match, _ = find_closest_iv(row_text, vocabulary)
                dv_match, _ = find_closest_dv(row_text, vocabulary)

                if iv_match or dv_match:
                    direction = _detect_direction(row_text)
                    sample_n = _extract_sample_size(row_text) or global_sample
                    effect_size, effect_type = _convert_to_cohens_d(stats, sample_n)

                    claim_seq += 1
                    claims.append({
                        "claim_id": _generate_claim_id(paper_id, table_id, claim_seq),
                        "paper_id": paper_id,
                        "iv": iv_match,
                        "iv_raw": row_text[:100] if iv_match else None,
                        "iv_mapped": iv_match is not None,
                        "iv_confidence": 0.5 if iv_match else 0.0,
                        "dv": dv_match,
                        "dv_raw": row_text[:100] if dv_match else None,
                        "dv_mapped": dv_match is not None,
                        "dv_confidence": 0.5 if dv_match else 0.0,
                        "direction": direction,
                        "effect_size": effect_size,
                        "effect_size_type": effect_type,
                        "sample_n": sample_n,
                        "p_value": stats.get("p_value"),
                        "context": global_context,
                        "source_table_id": table_id,
                        "source_page": table.get("page"),
                        "source_quote": row_text[:500],
                        "extraction_confidence": 0.4,
                        "vocabulary_mapped": False,
                        "extraction_method": "rule_based_stats_only",
                    })

    return claims


def extract_claims_from_table(
    table: dict[str, Any],
    paper_context: dict[str, Any] | None = None,
    vocabulary: dict[str, Any] | None = None,
    method: str = "enhanced",
) -> list[dict[str, Any]]:
    """
    Extract structured IV→DV claims from a classified table.

    Args:
        table: Reconstructed table from table_classifier (D.3)
            Expected keys: paper_id, page, rows, table_id (optional)
        paper_context: Optional context dict with title, abstract, article_type
        vocabulary: Vocabulary dict from D.1 (loads default if None)
        method: "enhanced" (Codex improvements), "rule_based" (legacy), or "llm"

    Returns:
        List of claim dicts with:
        - iv, dv, direction, effect_size, sample_n, context
        - source_quote, extraction_confidence, vocabulary_mapped
        - (enhanced only) confidence_decomposition, is_significant, semantic_type
    """
    if vocabulary is None:
        vocabulary = load_vocabulary()

    # Add paper context to table for extraction
    if paper_context:
        table = {**table, **paper_context}

    if method == "enhanced":
        raw_claims = _enhanced_extract_with_codex(table, vocabulary)
    elif method == "rule_based":
        raw_claims = _rule_based_extract(table, vocabulary)
    elif method == "llm":
        raw_claims = _enhanced_extract_with_codex(table, vocabulary)
    else:
        raise ValueError(f"Unknown extraction method: {method}. Use 'enhanced', 'rule_based', or 'llm'.")
    return _annotate_claim_semantics(raw_claims, table, paper_context)


def extract_claims_from_paper(
    paper_id: str,
    tables: list[dict[str, Any]],
    paper_context: dict[str, Any] | None = None,
    vocabulary: dict[str, Any] | None = None,
    method: str = "rule_based",
) -> list[dict[str, Any]]:
    """
    Extract all claims from all extractable tables in a paper.

    Args:
        paper_id: Paper identifier
        tables: List of classified tables from table_classifier
        paper_context: Optional context (title, abstract, article_type)
        vocabulary: Vocabulary dict
        method: "llm" or "rule_based"

    Returns:
        List of all claims from all tables, deduplicated.
    """
    if vocabulary is None:
        vocabulary = load_vocabulary()

    all_claims: list[dict[str, Any]] = []

    for table in tables:
        # Ensure paper_id is set
        table_with_paper = {**table, "paper_id": paper_id}

        claims = extract_claims_from_table(
            table_with_paper,
            paper_context=paper_context,
            vocabulary=vocabulary,
            method=method,
        )
        all_claims.extend(claims)

    # Deduplicate: same IV+DV+direction from same paper
    seen = set()
    deduped: list[dict[str, Any]] = []

    for claim in all_claims:
        key = (
            claim.get("paper_id"),
            claim.get("iv"),
            claim.get("dv"),
            claim.get("direction"),
        )
        if key not in seen:
            seen.add(key)
            deduped.append(claim)

    return deduped


def get_llm_extraction_prompt(
    table_content: str,
    table_type: str,
    paper_title: str | None = None,
    paper_abstract: str | None = None,
    vocabulary: dict[str, Any] | None = None,
) -> str:
    """
    Generate the LLM extraction prompt for a table.

    This prompt is designed for use with Claude or similar models
    to extract structured claims from table content.
    """
    if vocabulary is None:
        vocabulary = load_vocabulary()

    vocab_text = get_extraction_prompt_vocabulary(vocabulary)

    prompt = f"""You are extracting structured scientific claims from a data table in a
research paper about how architectural features affect human wellbeing.

PAPER: {paper_title or "Unknown"}
ABSTRACT: {paper_abstract or "Not available"}
TABLE TYPE: {table_type}
TABLE CONTENT:
{table_content}

TASK: Extract each causal claim from this table. For each claim, identify:
1. The independent variable (what was manipulated or measured as a predictor)
2. The dependent variable (what outcome was measured)
3. The direction of the effect (increase / decrease / no_effect)
4. The effect size (if available: Cohen's d, r, η², β, F, t, or p-value)
5. The sample size (if available)
6. The context (office, hospital, school, lab, etc.)

MAP variables to the closest term from this vocabulary:

{vocab_text}

If no close match exists, use a descriptive term and set mapped=false.

OUTPUT FORMAT (JSON array):
[
  {{
    "iv": "canonical_iv_name",
    "iv_raw": "original text from table",
    "iv_mapped": true,
    "dv": "canonical_dv_name",
    "dv_raw": "original text from table",
    "dv_mapped": true,
    "direction": "increase|decrease|no_effect",
    "effect_size": 0.5,
    "effect_size_type": "cohens_d|r|eta_squared|beta|f_value|t_value|null",
    "sample_n": 120,
    "p_value": 0.03,
    "context": "office",
    "source_quote": "exact text from table supporting this claim"
  }}
]

RULES:
- Only extract CAUSAL or CORRELATIONAL claims, not descriptive statistics
- Skip demographic data, model fit indices, and measurement specifications
- If the table contains regression weights, the predictors are IVs and the criterion is the DV
- If the table is a correlation matrix, each significant correlation is a claim
- Report "no_effect" for non-significant findings — these are important too
- Include the EXACT source text that supports each claim
"""
    return prompt


# CLI interface
def main() -> None:
    """Run claim extraction from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Extract claims from classified tables")
    parser.add_argument(
        "--table-file",
        help="JSON file containing a single table to process",
    )
    parser.add_argument(
        "--output",
        default="claims.json",
        help="Output file for extracted claims",
    )
    parser.add_argument(
        "--method",
        choices=["enhanced", "rule_based", "llm"],
        default="enhanced",
        help="Extraction method: enhanced (Codex improvements), rule_based (legacy), llm",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output",
    )

    args = parser.parse_args()

    if args.table_file:
        with open(args.table_file, "r", encoding="utf-8") as f:
            table = json.load(f)

        claims = extract_claims_from_table(table, method=args.method)

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(claims, f, indent=2)

        if args.verbose:
            print(f"Extracted {len(claims)} claims")
            for claim in claims:
                print(f"  {claim.get('iv')} → {claim.get('dv')} ({claim.get('direction')})")
    else:
        print("No input specified. Use --table-file to process a table.")


if __name__ == "__main__":
    main()
