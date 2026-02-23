"""Row-level table content classification for Codex isolated D10 improvements."""

from __future__ import annotations

import re
from dataclasses import dataclass


ROW_LABELS = {
    "HEADER",
    "STAT_ROW",
    "GROUP_LABEL",
    "DEMOGRAPHIC_ROW",
    "MODEL_FIT_ROW",
    "CITATION_ROW",
    "NOTE_ROW",
    "JUNK_ROW",
    "TEXT_ROW",
}

_CITATION_RE = re.compile(
    r"\b([A-Z][a-z]+(?:\s+et al\.)?\s*\(\d{4}\)|doi:|vol\.|pp\.|journal)\b",
    re.IGNORECASE,
)
_MODEL_FIT_RE = re.compile(r"\b(rmsea|cfi|gfi|aic|bic|chi[-\s]?square|χ²/df)\b", re.IGNORECASE)
_DEMOGRAPHIC_RE = re.compile(r"\b(age|gender|sex|education|participants?|male|female)\b", re.IGNORECASE)
_STAT_TOKEN_RE = re.compile(r"\b(p\s*[<=>]|f\s*\(|t\s*\(|r\s*=|β|beta|η²|odds\s*ratio|or\s*=)\b", re.IGNORECASE)
_HEADER_TOKEN_RE = re.compile(r"\b(mean|sd|se|n|variable|predictor|outcome|condition|group)\b", re.IGNORECASE)
_NOTE_RE = re.compile(r"^(note|notes?)\b|^\*+\s*", re.IGNORECASE)
_LONG_GLUE_RE = re.compile(r"\b[a-z]{22,}\b")


def normalize_ocr_text(text: str) -> str:
    """Normalize common OCR artifacts without changing semantics aggressively."""
    if not text:
        return ""

    tokens = re.split(r"(\s+)", text)
    fixed_tokens: list[str] = []

    for token in tokens:
        if token.isspace():
            fixed_tokens.append(token)
            continue

        # Collapse exact char-pair duplication: "ttaaccttiillee" -> "tactile".
        if len(token) >= 6 and len(token) % 2 == 0:
            pair_hits = sum(1 for i in range(0, len(token), 2) if token[i : i + 2] and token[i] == token[i + 1])
            if pair_hits >= (len(token) // 2) * 0.8:
                token = "".join(token[i] for i in range(0, len(token), 2))

        # Reduce 3+ repeats to 2 for general OCR stutter.
        token = re.sub(r"(.)\1{2,}", r"\1\1", token)

        # If many doubled neighbors remain, collapse pairs globally.
        collapsed_pairs = re.sub(r"(.)\1", r"\1", token)
        if len(token) >= 8 and len(collapsed_pairs) <= int(len(token) * 0.72):
            token = collapsed_pairs

        # Insert spaces into known glued compounds.
        token = re.sub(
            r"(sample)(photo|image|room|table|figure)",
            r"\1 \2",
            token,
            flags=re.IGNORECASE,
        )
        token = re.sub(
            r"(room)(with|without|high|low)",
            r"\1 \2",
            token,
            flags=re.IGNORECASE,
        )
        token = re.sub(
            r"(appendix)(figure|table)",
            r"\1 \2",
            token,
            flags=re.IGNORECASE,
        )
        fixed_tokens.append(token)

    normalized = "".join(fixed_tokens)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


@dataclass(frozen=True)
class RowProfile:
    label: str
    confidence: float
    normalized_text: str
    artifact_flags: tuple[str, ...]


def _artifact_flags(text: str) -> tuple[str, ...]:
    flags: list[str] = []
    lowered = text.lower()

    letters = [c for c in lowered if c.isalpha()]
    dup_adj = sum(1 for i in range(len(letters) - 1) if letters[i] == letters[i + 1])
    dup_ratio = dup_adj / max(1, len(letters))
    if dup_ratio > 0.09:
        flags.append("doubled_characters")
    if _LONG_GLUE_RE.search(lowered):
        flags.append("concatenated_words")
    if re.search(r"[^\w\s]{6,}", text):
        flags.append("non_word_sequence")
    return tuple(flags)


def classify_row_content(text: str) -> RowProfile:
    """Classify a table row into semantic row labels for table understanding."""
    raw_text = text or ""
    normalized = normalize_ocr_text(raw_text)
    flags = tuple(sorted(set(_artifact_flags(raw_text)) | set(_artifact_flags(normalized))))

    if not normalized or len(normalized) < 3:
        return RowProfile("JUNK_ROW", 0.95, normalized, flags + ("empty",))

    lowered = normalized.lower()
    digit_ratio = sum(ch.isdigit() for ch in normalized) / max(1, len(normalized))

    if ("doubled_characters" in flags and "concatenated_words" in flags) or (
        len(flags) >= 2 and not _STAT_TOKEN_RE.search(normalized)
    ):
        return RowProfile("JUNK_ROW", 0.9, normalized, flags)

    if _NOTE_RE.search(normalized):
        return RowProfile("NOTE_ROW", 0.88, normalized, flags)

    if _MODEL_FIT_RE.search(normalized):
        return RowProfile("MODEL_FIT_ROW", 0.9, normalized, flags)

    if _CITATION_RE.search(normalized) and not _STAT_TOKEN_RE.search(normalized):
        return RowProfile("CITATION_ROW", 0.86, normalized, flags)

    if _DEMOGRAPHIC_RE.search(normalized) and ("mean" in lowered or "sd" in lowered or digit_ratio > 0.08):
        return RowProfile("DEMOGRAPHIC_ROW", 0.82, normalized, flags)

    if _STAT_TOKEN_RE.search(normalized):
        return RowProfile("STAT_ROW", 0.85, normalized, flags)

    if _HEADER_TOKEN_RE.search(normalized) and digit_ratio < 0.08:
        return RowProfile("HEADER", 0.78, normalized, flags)

    if digit_ratio < 0.02 and len(normalized.split()) <= 5:
        return RowProfile("GROUP_LABEL", 0.7, normalized, flags)

    return RowProfile("TEXT_ROW", 0.6, normalized, flags)
