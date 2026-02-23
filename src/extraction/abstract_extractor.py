"""Abstract and caption claim extraction for Sprint D addendum (D.14 support).

Deterministic extractor that mines:
- Abstract findings (multi-claim per abstract)
- Results-oriented figure/table captions
- Table-caption DV lookup for downstream table extraction override
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.claim_extractor import (
    _convert_to_cohens_d,
    _detect_context,
    _detect_direction,
    _extract_sample_size,
    _extract_statistics,
    _extract_variables_from_row,
)
from src.extraction.contracts import assert_valid_payload
from src.extraction.row_classifier_codex import normalize_ocr_text
from src.extraction.vocabulary import find_closest_dv, find_closest_iv, load_vocabulary
from src.services.db_locator import resolve_article_finder_db


_MIN_MAP_CONF = 0.65
_MIN_CLAIM_CONF = 0.56
_MIN_DB_TITLE_JACCARD = 0.30
_MIN_RELAXED_MAP_CONF = 0.55
_MIN_RELAXED_CLAIM_CONF = 0.52
_MAX_VAR_TOKENS = 12

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_STAT_SIGNAL_RE = re.compile(
    r"\b(p\s*[<=>]|r\s*[=:]|β|beta|t\(|f\(|η²|eta|cohen['’]?\s*s?\s*d)\b",
    re.IGNORECASE,
)
_FINDING_CUE_RE = re.compile(
    r"\b("
    r"results?|found|show(?:ed|s)?|demonstrat(?:ed|es)|indicat(?:ed|es)|reveal(?:ed|s)|"
    r"predict(?:ed|s)|associated|correlated|significant|non[- ]?significant|"
    r"no effect|increased|decreased|reduced|enhanced|improved|worse|better|"
    r"moderate level|high level"
    r")\b",
    re.IGNORECASE,
)

_CAPTION_START_RE = re.compile(r"^\s*(figure|fig\.?|table)\s*\d+[a-z]?[.:)]?\s*", re.IGNORECASE)
_RESULTS_CAPTION_RE = re.compile(
    r"\b("
    r"regression|anova|correlation|coefficients?|effect|relationship|predict(?:ing|ed|s)|"
    r"mean(?:s)?\s+(?:score|value|difference)|difference\s+between|significant|p\s*[<=>]|"
    r"β|beta|r\s*[=:]|t\(|f\(|t\s*=|f\s*="
    r")\b",
    re.IGNORECASE,
)
_NON_RESULTS_CAPTION_RE = re.compile(
    r"\b("
    r"photo(graph)?|image|diagram|layout|floor plan|apparatus|experimental setup|"
    r"workflow|simulation approach|distribution of published articles|stimuli|materials?|"
    r"proposal|displacement field|algorithm|pipeline|architecture diagram|conceptual model|"
    r"land use map|geological map|sample characteristics"
    r")\b",
    re.IGNORECASE,
)
_FIGURE_STAT_REQUIRED_RE = re.compile(
    r"\b(p\s*[<=>]|r\s*[=:]|β|beta|t\(|f\(|eta|odds ratio|cohen['’]?\s*d)\b",
    re.IGNORECASE,
)

_PAIR_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"(?:effect|impact|influence|association|relationship)s?\s+of\s+(?P<iv>[^.;:]{2,120}?)\s+on\s+(?P<dv>[^.;:]{2,120})",
            re.IGNORECASE,
        ),
        "unknown",
    ),
    (
        re.compile(
            r"relationship\s+between\s+(?P<iv>[^.;:]{2,120}?)\s+and\s+(?P<dv>[^.;:]{2,120})",
            re.IGNORECASE,
        ),
        "unknown",
    ),
    (re.compile(r"(?P<iv>[^.;:]{2,120}?)\s+predict(?:ed|s|ing)?\s+(?P<dv>[^.;:]{2,120})", re.IGNORECASE), "unknown"),
    (
        re.compile(
            r"(?P<iv>[^.;:]{2,120}?)\s+(?:was|were|is|are)?\s*(?:positively|negatively)?\s*(?:associated|correlated|related|linked)\s+(?:with|to)\s+(?P<dv>[^.;:]{2,120})",
            re.IGNORECASE,
        ),
        "unknown",
    ),
    (
        re.compile(
            r"(?P<iv>[^.;:]{2,120}?)\s+(?:had|has|have|showed|shows|demonstrated|indicated)?\s*(?:a\s+)?(?:positive|significant)\s+effect\s+on\s+(?P<dv>[^.;:]{2,120})",
            re.IGNORECASE,
        ),
        "increase",
    ),
    (
        re.compile(
            r"(?P<iv>[^.;:]{2,120}?)\s+(?:had|has|have|showed|shows|demonstrated|indicated)?\s*(?:a\s+)?(?:negative)\s+effect\s+on\s+(?P<dv>[^.;:]{2,120})",
            re.IGNORECASE,
        ),
        "decrease",
    ),
    (
        re.compile(
            r"(?P<iv>[^.;:]{2,120}?)\s+(?:significantly\s+)?(?:increased|enhanced|improved|boosted|elevated|raised)\s+(?P<dv>[^.;:]{2,120})",
            re.IGNORECASE,
        ),
        "increase",
    ),
    (
        re.compile(
            r"(?P<iv>[^.;:]{2,120}?)\s+(?:significantly\s+)?(?:decreased|reduced|impaired|lowered|diminished|worsened)\s+(?P<dv>[^.;:]{2,120})",
            re.IGNORECASE,
        ),
        "decrease",
    ),
]
_DV_ONLY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?:effect|impact|influence|association|relationship)s?\s+on\s+(?P<dv>[^.;:]{2,120})", re.IGNORECASE),
    re.compile(r"(?:increased|enhanced|improved|reduced|decreased)\s+(?P<dv>[^.;:]{2,120})", re.IGNORECASE),
]
_IV_ONLY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?:effect|impact|influence|association|relationship)s?\s+of\s+(?P<iv>[^.;:]{2,120})", re.IGNORECASE),
]
_CAPTION_PAIR_PATTERNS = [
    *(pattern for pattern, _ in _PAIR_PATTERNS),
    re.compile(
        r"(?:results?|analysis|regression|anova|correlation)\s+for\s+(?P<dv>[^.;:]+?)\s+by\s+(?P<iv>[^.;:]+)",
        re.IGNORECASE,
    ),
    re.compile(
        r"mean(?:s)?\s+(?P<dv>[^.;:]+?)\s+by\s+(?P<iv>[^.;:]+)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:results?|analysis|regression|anova|correlation)\s+for\s+(?P<dv>[^.;:]+?)[;,:]\s*(?P<iv>[^.;:]+?)\s+(?:β|beta|r\s*[=:]|p\s*[<=>]|t\(|f\()",
        re.IGNORECASE,
    ),
]
_LEADING_FINDER_RE = re.compile(
    r"^(?:"
    r"(?:the|our|these|those)\s+results?\s+(?:show(?:ed|s)?|indicat(?:ed|es)|reveal(?:ed|s))\s+that\s+|"
    r"results?\s+(?:show(?:ed|s)?|indicat(?:ed|es)|reveal(?:ed|s))\s+that\s+|"
    r"it\s+was\s+found\s+that\s+|"
    r"findings?\s+(?:show(?:ed|s)?|indicat(?:ed|es)|reveal(?:ed|s))\s+that\s+|"
    r"the\s+study\s+(?:show(?:ed|s)?|found)\s+that\s+"
    r")",
    re.IGNORECASE,
)
_TRAILING_CLAUSE_RE = re.compile(
    r"\b(?:in\s+(?:participants|subjects|patients|children|adults)|"
    r"during\s+[a-z0-9 _\-/]{2,60}|"
    r"after\s+[a-z0-9 _\-/]{2,60}|"
    r"under\s+[a-z0-9 _\-/]{2,60})$",
    re.IGNORECASE,
)
_LIST_SPLIT_RE = re.compile(r"\s*(?:,|;|\band\b|\bor\b)\s*", re.IGNORECASE)
_DIR_POS_RE = re.compile(
    r"\b(increase[sd]?|enhance[sd]?|improve[sd]?|boost[sd]?|raise[sd]?|elevate[sd]?|benefit(?:ed|s)?|positive\s+effect)\b",
    re.IGNORECASE,
)
_DIR_NEG_RE = re.compile(
    r"\b(decrease[sd]?|reduce[sd]?|diminish(?:ed|es)?|impair(?:ed|s)?|suppress(?:ed|es)?|lower(?:ed|s)?|worsen(?:ed|s)?|negative\s+effect)\b",
    re.IGNORECASE,
)
_DIR_NULL_RE = re.compile(
    r"\b(no\s+(?:significant\s+)?(?:effect|difference|change|impact|relationship)|non[- ]?significant|failed\s+to\s+reach\s+significance)\b",
    re.IGNORECASE,
)

_CAPTION_DV_PATTERNS = [
    re.compile(r"predict(?:ing|ed|s)?\s+(?P<dv>[a-z0-9 _\-/]{3,}?)\s+from", re.IGNORECASE),
    re.compile(r"(?:results?|analysis|regression|anova|correlation)\s+for\s+(?P<dv>[a-z0-9 _\-/]{3,})", re.IGNORECASE),
    re.compile(r"effects?\s+on\s+(?P<dv>[a-z0-9 _\-/]{3,})", re.IGNORECASE),
    re.compile(r"(?P<dv>[a-z0-9 _\-/]{3,}?)\s+by\s+(?:condition|group|level)", re.IGNORECASE),
    re.compile(r"mean(?:s)?\s+(?P<dv>[a-z0-9 _\-/]{3,}?)\s+(?:for|across|in|under|by)\b", re.IGNORECASE),
    re.compile(r"percentage(?:\s+of)?\s+(?P<dv>[a-z0-9 _\-/]{3,}?)\s+(?:for|by|across|before|after)\b", re.IGNORECASE),
    re.compile(r"number(?:\s+of)?\s+(?P<dv>[a-z0-9 _\-/]{3,}?)\s+(?:for|by|across|before|after)\b", re.IGNORECASE),
    re.compile(r"ratings?\s+of\s+(?P<dv>[a-z0-9 _\-/]{3,}?)\s+(?:for|by|across|under)\b", re.IGNORECASE),
    re.compile(
        r"effect[s]?\s*of\s+[a-z0-9 _\-/]{2,}?\s*on\s+(?:the\s+mean(?:\s*\(sd\))?\s+of\s+)?(?P<dv>[a-z0-9 _\-/]{3,})",
        re.IGNORECASE,
    ),
    re.compile(r"mediating\s+variable\s+of\s+(?P<dv>[a-z0-9 _\-/]{3,})", re.IGNORECASE),
    re.compile(r"across\s+[a-z0-9 _\-/]{2,}?\s+and\s+(?P<dv>[a-z0-9 _\-/]{3,})", re.IGNORECASE),
    re.compile(r"->\s*(?P<dv>[a-z0-9 _\-/]{3,})", re.IGNORECASE),
]
_ALPHA_TOKEN_RE = re.compile(r"[a-z]{4,}", re.IGNORECASE)
_ABSTRACT_HEADING_RE = re.compile(r"\babstract\b\s*[:.\-]?\s*(?!art\b)", re.IGNORECASE)
_ABSTRACT_STOP_RE = re.compile(
    r"\b("
    r"keywords?|index\s+terms?|introduction|background|methods?|materials\s+and\s+methods|"
    r"study\s+\d|aims?\s+and\s+hypotheses|objective"
    r")\b",
    re.IGNORECASE,
)
_CAPTION_LINE_RE = re.compile(r"(?:^|\n)\s*(figure|fig\.?|table)\s*\d+[a-z]?[.:)]?\s*", re.IGNORECASE)
_TABLE_START_SEARCH_RE = re.compile(r"\btable\s*\d+[a-z]?[.:)]?\s*", re.IGNORECASE)
_TABLE_START_RE = re.compile(r"^\s*table\s*\d+[a-z]?[.:)]?\s*", re.IGNORECASE)

_DEFAULT_METADATA_CSV = "data/production/realtime_pdf_completion_queue.csv"
_DEFAULT_PREPROCESS_DIR = "data/production/pdf_preprocess_cache"
_DEFAULT_ARTICLE_DB: str | None = None


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _as_int(value: Any) -> int | None:
    raw = _normalize_space(value)
    if not raw:
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


def _normalize_caption_text(text: str) -> str:
    t = normalize_ocr_text(str(text or ""))
    t = _normalize_space(t)
    t = re.sub(r"(?i)\b(table|figure|fig)\s*(\d)", r"\1 \2", t)
    # Common OCR glue around function words and affect terms.
    glue_fixes = {
        "showsthe": "shows the",
        "resultsof": "results of",
        "effectof": "effect of",
        "effectofthe": "effect of the",
        "ofthe": "of the",
        "inthe": "in the",
        "forthe": "for the",
        "andthe": "and the",
        "onthe": "on the",
        "mentalfatigue": "mental fatigue",
        "positiveemotions": "positive emotions",
        "negativeemotions": "negative emotions",
    }
    for old, new in glue_fixes.items():
        t = re.sub(old, new, t, flags=re.IGNORECASE)
    return _normalize_space(t)


def _tokenize_alpha(text: str) -> set[str]:
    return {m.group(0).lower() for m in _ALPHA_TOKEN_RE.finditer(str(text or ""))}


def _title_jaccard(a: str, b: str) -> float:
    ta = _tokenize_alpha(a)
    tb = _tokenize_alpha(b)
    if not ta and not tb:
        return 0.0
    return len(ta & tb) / max(1, len(ta | tb))


def _clean_abstract_text(text: str) -> str:
    t = str(text or "")
    t = t.replace("\x0c", " ")
    # Unwrap broken hyphenation from PDF line breaks.
    t = re.sub(r"(\w)-\s+(\w)", r"\1\2", t)
    # Front-matter boilerplate usually not part of abstract body.
    t = re.sub(r"\b(received|accepted|published online|copyright)\b.*", "", t, flags=re.IGNORECASE)
    t = _normalize_space(t)
    return t.strip(" .;:-")


def _looks_like_abstract(text: str) -> bool:
    t = _clean_abstract_text(text)
    words = t.split()
    if not (20 <= len(words) <= 450):
        return False
    alpha_chars = sum(1 for ch in t if ch.isalpha())
    if alpha_chars < 80:
        return False
    if alpha_chars / max(1, len(t)) < 0.58:
        return False
    if re.search(r"\b(references|bibliography|acknowledg(?:e)?ments?)\b", t, re.IGNORECASE):
        return False
    return True


def _extract_abstract_from_preprocess(paper_id: str, preprocess_dir: str) -> str | None:
    path = Path(preprocess_dir) / f"{paper_id}.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    pages = payload.get("pages") or []
    text = "\n".join(str(p.get("text") or "") for p in pages[:2])
    if not text.strip():
        return None

    m = _ABSTRACT_HEADING_RE.search(text)
    if m and m.start() < 4500:
        rest = text[m.end() : m.end() + 6000]
        stop = _ABSTRACT_STOP_RE.search(rest)
        candidate = rest[: stop.start()] if stop else rest
        cleaned = _clean_abstract_text(candidate)
        if _looks_like_abstract(cleaned):
            return cleaned

    # Fallback: first-page lead block before section headings.
    first_page = str((pages[0] if pages else {}).get("text") or "")
    if not first_page.strip():
        return None
    leading = first_page[:4500]
    stop = _ABSTRACT_STOP_RE.search(leading)
    if stop:
        leading = leading[: stop.start()]
    # Keep last block to avoid title/author lines at the top.
    leading = leading[-2600:]
    cleaned = _clean_abstract_text(leading)
    if _looks_like_abstract(cleaned) and _FINDING_CUE_RE.search(cleaned):
        return cleaned
    return None


def _paper_doi(paper_id: str, explicit_doi: str | None) -> str:
    doi = _normalize_space(explicit_doi).lower()
    if doi:
        return doi
    pid = _normalize_space(paper_id)
    if pid.lower().startswith("doi:"):
        return pid[4:].strip().lower()
    return ""


def _load_metadata_csv(path: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    p = Path(path)
    if not p.exists():
        return out
    with p.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            paper_id = _normalize_space(row.get("paper_id"))
            if not paper_id:
                continue
            out[paper_id] = {
                "paper_id": paper_id,
                "doi": _normalize_space(row.get("doi")).lower(),
                "title": _normalize_space(row.get("title")),
                "pdf_path": _normalize_space(row.get("pdf_path")),
            }
    return out


def _fetch_db_abstract(
    conn: sqlite3.Connection,
    paper_id: str,
    doi: str,
    expected_title: str,
) -> tuple[str | None, str | None]:
    cur = conn.cursor()
    row = None
    if doi:
        cur.execute(
            "SELECT title, abstract FROM papers WHERE lower(doi)=? ORDER BY rowid DESC LIMIT 1",
            (doi,),
        )
        row = cur.fetchone()
    if not row:
        cur.execute(
            "SELECT title, abstract FROM papers WHERE paper_id=? ORDER BY rowid DESC LIMIT 1",
            (paper_id,),
        )
        row = cur.fetchone()
    if not row:
        return None, None

    db_title = _normalize_space(row[0])
    abstract = _clean_abstract_text(row[1] or "")
    if not _looks_like_abstract(abstract):
        return None, None

    if expected_title and db_title:
        jaccard = _title_jaccard(expected_title, db_title)
        if jaccard < _MIN_DB_TITLE_JACCARD:
            return None, None
    return abstract, db_title or None


def _resolve_abstract_and_title(
    rec: dict[str, Any],
    metadata_map: dict[str, dict[str, str]],
    db_conn: sqlite3.Connection | None,
    preprocess_dir: str,
) -> tuple[str | None, str | None, str]:
    paper_id = _normalize_space(rec.get("paper_id"))
    meta = metadata_map.get(paper_id, {})
    triage_abstract = _clean_abstract_text(rec.get("abstract") or "")
    triage_title = _normalize_space(rec.get("title"))
    meta_title = _normalize_space(meta.get("title"))
    title = triage_title or meta_title or None

    if _looks_like_abstract(triage_abstract):
        return triage_abstract, title, "triage"

    doi = _paper_doi(paper_id, meta.get("doi"))
    if db_conn is not None:
        db_abstract, db_title = _fetch_db_abstract(
            db_conn,
            paper_id=paper_id,
            doi=doi,
            expected_title=title or "",
        )
        if db_abstract:
            return db_abstract, (title or db_title), "article_db"

    pre_abstract = _extract_abstract_from_preprocess(paper_id, preprocess_dir=preprocess_dir)
    if pre_abstract:
        return pre_abstract, title, "preprocess_cache"
    return None, title, "none"


def _sentence_candidates(text: str) -> list[str]:
    if not text:
        return []
    pieces = [_normalize_space(p) for p in _SENTENCE_SPLIT_RE.split(text)]
    return [p for p in pieces if len(p) >= 20]


def _is_finding_sentence(sentence: str) -> bool:
    if not sentence:
        return False
    return bool(_STAT_SIGNAL_RE.search(sentence) or _FINDING_CUE_RE.search(sentence))


def _clean_variable_phrase(raw: str) -> str:
    t = _normalize_space(raw)
    if not t:
        return ""
    t = _LEADING_FINDER_RE.sub("", t)
    t = re.sub(r"\([^)]{0,40}\)", "", t)
    t = re.sub(r"^[^a-zA-Z0-9]+", "", t)
    t = re.sub(r"^(?:the|a|an|this|that|these|those)\s+", "", t, flags=re.IGNORECASE)
    t = _TRAILING_CLAUSE_RE.sub("", t).strip(" .,:;")
    t = _normalize_space(t)
    parts = t.split()
    if len(parts) > _MAX_VAR_TOKENS:
        t = " ".join(parts[-_MAX_VAR_TOKENS:])
    return _normalize_space(t)


def _phrase_variants(raw: str) -> list[str]:
    base = _clean_variable_phrase(raw)
    if not base:
        return []
    variants: list[str] = [base]
    parts = base.split()
    if len(parts) >= 3:
        variants.append(" ".join(parts[: min(len(parts), 6)]))
        variants.append(" ".join(parts[max(0, len(parts) - 6) :]))
    if _LIST_SPLIT_RE.search(base):
        for part in _LIST_SPLIT_RE.split(base):
            part_clean = _clean_variable_phrase(part)
            if part_clean and len(part_clean.split()) <= _MAX_VAR_TOKENS:
                variants.append(part_clean)
    dedup: list[str] = []
    seen: set[str] = set()
    for variant in variants:
        key = variant.lower()
        if key in seen or len(variant) < 2:
            continue
        seen.add(key)
        dedup.append(variant)
    return dedup


def _best_map(
    term: str,
    vocab: dict[str, Any],
    *,
    kind: str,
    min_conf: float,
) -> tuple[str | None, float, str]:
    best_term = ""
    best_mapped = None
    best_conf = 0.0
    for variant in _phrase_variants(term):
        if kind == "iv":
            mapped, conf = find_closest_iv(variant, vocab)
        else:
            mapped, conf = find_closest_dv(variant, vocab)
        conf_val = float(conf or 0.0)
        if mapped and conf_val > best_conf:
            best_conf = conf_val
            best_mapped = mapped
            best_term = variant
    if best_mapped and best_conf >= min_conf:
        return best_mapped, best_conf, (best_term or _clean_variable_phrase(term))
    return None, best_conf, (best_term or _clean_variable_phrase(term))


def _map_iv(term: str, vocab: dict[str, Any], min_conf: float = _MIN_MAP_CONF) -> tuple[str | None, float, str]:
    mapped, conf, cleaned = _best_map(term, vocab, kind="iv", min_conf=min_conf)
    return mapped, conf, cleaned


def _map_dv(term: str, vocab: dict[str, Any], min_conf: float = _MIN_MAP_CONF) -> tuple[str | None, float, str]:
    mapped, conf, cleaned = _best_map(term, vocab, kind="dv", min_conf=min_conf)
    return mapped, conf, cleaned


def _extract_pair_candidates(text: str, vocab: dict[str, Any], min_conf: float = _MIN_MAP_CONF) -> list[dict[str, Any]]:
    pairs: list[tuple[str, str, str]] = []
    for c in _extract_variables_from_row(text, vocab):
        iv_raw = _normalize_space(c.get("iv_raw", ""))
        dv_raw = _normalize_space(c.get("dv_raw", ""))
        if iv_raw and dv_raw:
            pairs.append((iv_raw, dv_raw, "unknown"))

    for pat, direction_hint in _PAIR_PATTERNS:
        for match in pat.finditer(text):
            iv_raw = _normalize_space(match.group("iv")).strip(" .,:;")
            dv_raw = _normalize_space(match.group("dv")).strip(" .,:;")
            if iv_raw and dv_raw:
                dv_options = [d for d in _LIST_SPLIT_RE.split(dv_raw) if _normalize_space(d)]
                if not dv_options:
                    dv_options = [dv_raw]
                for dv_option in dv_options[:4]:
                    pairs.append((iv_raw, _normalize_space(dv_option), direction_hint))

    for pat in _DV_ONLY_PATTERNS:
        for match in pat.finditer(text):
            dv_raw = _normalize_space(match.group("dv")).strip(" .,:;")
            if dv_raw:
                for dv_option in [d for d in _LIST_SPLIT_RE.split(dv_raw) if _normalize_space(d)][:4]:
                    pairs.append(("", _normalize_space(dv_option), "unknown"))
    for pat in _IV_ONLY_PATTERNS:
        for match in pat.finditer(text):
            iv_raw = _normalize_space(match.group("iv")).strip(" .,:;")
            if iv_raw:
                for iv_option in [d for d in _LIST_SPLIT_RE.split(iv_raw) if _normalize_space(d)][:4]:
                    pairs.append((_normalize_space(iv_option), "", "unknown"))

    dedup_seen: set[tuple[str, str, str]] = set()
    out: list[dict[str, Any]] = []
    for iv_raw, dv_raw, direction_hint in pairs:
        key = (iv_raw.lower(), dv_raw.lower(), direction_hint)
        if key in dedup_seen:
            continue
        dedup_seen.add(key)
        iv, iv_conf, iv_clean = _map_iv(iv_raw, vocab, min_conf=min_conf) if iv_raw else (None, 0.0, "")
        dv, dv_conf, dv_clean = _map_dv(dv_raw, vocab, min_conf=min_conf) if dv_raw else (None, 0.0, "")
        if iv and dv and iv == dv:
            continue
        if not iv and not dv:
            continue
        out.append(
            {
                "iv_raw": iv_clean or iv_raw,
                "dv_raw": dv_clean or dv_raw,
                "iv": iv,
                "dv": dv,
                "iv_conf": iv_conf,
                "dv_conf": dv_conf,
                "direction_hint": direction_hint,
            }
        )
    return out


def _direction_anchor_terms(pair: dict[str, Any]) -> list[str]:
    terms: list[str] = []
    for raw in (pair.get("dv_raw"), pair.get("iv_raw")):
        t = _clean_variable_phrase(str(raw or ""))
        if t:
            terms.append(t)
    for mapped in (pair.get("dv"), pair.get("iv")):
        m = str(mapped or "").strip().replace("_", " ")
        if m:
            terms.append(m)
    dedup: list[str] = []
    seen: set[str] = set()
    for term in terms:
        term = _normalize_space(term)
        if len(term) < 3:
            continue
        key = term.lower()
        if key in seen:
            continue
        seen.add(key)
        dedup.append(term)
    return dedup[:6]


def _local_direction_from_anchor(sentence: str, anchor: str) -> str:
    text = str(sentence or "")
    low = text.lower()
    a = anchor.lower()
    idx = low.find(a)
    if idx < 0:
        return "unknown"
    # Tight local window to avoid mixed-clause cross-talk.
    win = text[max(0, idx - 48) : min(len(text), idx + len(anchor) + 48)]
    if _DIR_NULL_RE.search(win):
        return "no_effect"
    pos = bool(_DIR_POS_RE.search(win))
    neg = bool(_DIR_NEG_RE.search(win))
    if pos and not neg:
        return "increase"
    if neg and not pos:
        return "decrease"
    return "unknown"


def _pair_specific_direction(
    sentence: str,
    pair: dict[str, Any],
    sentence_direction: str,
) -> str:
    hint = _normalize_space(pair.get("direction_hint")).lower()
    if hint and hint != "unknown":
        return hint

    found_dirs: list[str] = []
    for anchor in _direction_anchor_terms(pair):
        d = _local_direction_from_anchor(sentence, anchor)
        if d != "unknown":
            found_dirs.append(d)
    if found_dirs:
        uniq = {d for d in found_dirs}
        if len(uniq) == 1:
            return next(iter(uniq))
    if sentence_direction and sentence_direction != "unknown":
        return sentence_direction
    return "unknown"


def _backfill_unknown_directions(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not claims:
        return []

    known_by_pair: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    for claim in claims:
        direction = _normalize_space(claim.get("direction")).lower() or "unknown"
        if direction == "unknown":
            continue
        key = (
            _normalize_space(claim.get("paper_id")).lower(),
            _normalize_space(claim.get("iv") or claim.get("iv_raw")).lower(),
            _normalize_space(claim.get("dv") or claim.get("dv_raw")).lower(),
        )
        if all(key):
            known_by_pair[key][direction] += 1

    key_order: list[tuple[str, str, str, str]] = []
    dedup: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for claim in claims:
        patched = dict(claim)
        pair_key = (
            _normalize_space(patched.get("paper_id")).lower(),
            _normalize_space(patched.get("iv") or patched.get("iv_raw")).lower(),
            _normalize_space(patched.get("dv") or patched.get("dv_raw")).lower(),
        )
        direction = _normalize_space(patched.get("direction")).lower() or "unknown"
        if direction == "unknown":
            known = known_by_pair.get(pair_key, Counter())
            if len(known) == 1:
                inferred = next(iter(known))
                patched["direction"] = inferred
                patched["direction_inferred_from"] = "paper_pair_consensus"
                method = str(patched.get("extraction_method") or "").strip()
                if method and "dir_backfill" not in method:
                    patched["extraction_method"] = f"{method}+dir_backfill"
                elif not method:
                    patched["extraction_method"] = "abstract_rule_v2+dir_backfill"
                direction = inferred

        dkey = (*pair_key, direction)
        existing = dedup.get(dkey)
        if existing is None:
            dedup[dkey] = patched
            key_order.append(dkey)
            continue
        old_conf = float(existing.get("extraction_confidence") or 0.0)
        new_conf = float(patched.get("extraction_confidence") or 0.0)
        if new_conf > old_conf:
            dedup[dkey] = patched

    return [dedup[k] for k in key_order]


def _extract_caption_pair_candidates(text: str, vocab: dict[str, Any]) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    t = _normalize_caption_text(text)
    for pat in _CAPTION_PAIR_PATTERNS:
        for match in pat.finditer(t):
            iv_raw = _normalize_space(match.group("iv")).strip(" .,:;")
            dv_raw = _normalize_space(match.group("dv")).strip(" .,:;")
            if not iv_raw or not dv_raw:
                continue
            iv, iv_conf, iv_clean = _map_iv(iv_raw, vocab)
            dv, dv_conf, dv_clean = _map_dv(dv_raw, vocab)
            if not iv or not dv or iv == dv:
                continue
            key = (iv, dv)
            if key in seen:
                continue
            seen.add(key)
            pairs.append(
                {
                    "iv_raw": iv_clean or iv_raw,
                    "dv_raw": dv_clean or dv_raw,
                    "iv": iv,
                    "dv": dv,
                    "iv_conf": iv_conf,
                    "dv_conf": dv_conf,
                }
            )
    return pairs


def _is_results_caption(text: str) -> bool:
    if not text:
        return False
    t = _normalize_caption_text(text)
    m = _CAPTION_START_RE.match(t)
    if not m:
        return False
    kind = (m.group(1) or "").lower()
    if _NON_RESULTS_CAPTION_RE.search(t):
        return False
    has_signal = bool(_RESULTS_CAPTION_RE.search(t))
    if not has_signal and kind.startswith("table"):
        has_signal = bool(_extract_statistics(t))
    if not has_signal:
        return False
    # Figure captions are noisier than table captions; require explicit stats to keep precision high.
    if kind.startswith("fig") or kind.startswith("figure"):
        return bool(_FIGURE_STAT_REQUIRED_RE.search(t))
    return True


def _extract_table_caption_span(text: str) -> str | None:
    t = str(text or "")
    m = _TABLE_START_SEARCH_RE.search(t)
    if not m:
        return None
    return _normalize_caption_text(t[m.start() : m.start() + 700]) or None


def _extract_caption_dv(text: str, vocab: dict[str, Any]) -> tuple[str | None, str | None, float]:
    t = _normalize_caption_text(text)
    if not t:
        return None, None, 0.0
    candidates: list[tuple[str, str | None, float]] = []
    for pat in _CAPTION_DV_PATTERNS:
        m = pat.search(t)
        if not m:
            continue
        raw = _normalize_space(m.group("dv")).strip(" .,:;")
        if len(raw) < 3:
            continue
        mapped, conf, _ = _map_dv(raw, vocab)
        candidates.append((raw, mapped, conf))
    if not candidates:
        return None, None, 0.0
    candidates.sort(key=lambda item: item[2], reverse=True)
    return candidates[0]


def _claim_confidence(
    iv_conf: float,
    dv_conf: float,
    direction: str,
    has_effect: bool,
    sample_n: int | None,
) -> float:
    conf = 0.40 + 0.22 * float(iv_conf) + 0.22 * float(dv_conf)
    if direction != "unknown":
        conf += 0.08
    if has_effect:
        conf += 0.06
    if sample_n and sample_n >= 20:
        conf += 0.04
    return min(0.95, conf)


def extract_claims_from_abstract(
    paper_id: str,
    title: str,
    abstract: str,
    vocabulary: dict[str, Any],
    article_type_family: str | None = None,
) -> list[dict[str, Any]]:
    """Extract structured claims from one abstract."""
    abstract = _normalize_space(abstract)
    if len(abstract) < 40:
        return []

    sentences = _sentence_candidates(abstract)
    global_n = _extract_sample_size(abstract)
    context = _detect_context(f"{title or ''} {abstract}")
    abstract_level_pairs = _extract_pair_candidates(abstract, vocabulary, min_conf=_MIN_RELAXED_MAP_CONF)
    global_iv_prior = Counter(
        p.get("iv")
        for p in abstract_level_pairs
        if p.get("iv") and float(p.get("iv_conf", 0.0)) >= _MIN_MAP_CONF
    )
    global_dv_prior = Counter(
        p.get("dv")
        for p in abstract_level_pairs
        if p.get("dv") and float(p.get("dv_conf", 0.0)) >= _MIN_MAP_CONF
    )

    def _global_top(counter: Counter[str]) -> str | None:
        if not counter:
            return None
        top, count = counter.most_common(1)[0]
        return top if count >= 2 else None

    claims: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    seq = 0
    fallback_global_iv = _global_top(global_iv_prior)
    fallback_global_dv = _global_top(global_dv_prior)

    for sentence in sentences:
        if not _is_finding_sentence(sentence):
            continue
        stats = _extract_statistics(sentence)
        pairs = _extract_pair_candidates(sentence, vocabulary, min_conf=_MIN_MAP_CONF)
        relaxed_pass = False
        if not pairs:
            pairs = _extract_pair_candidates(sentence, vocabulary, min_conf=_MIN_RELAXED_MAP_CONF)
            relaxed_pass = True
        if not pairs:
            continue

        sentence_ivs = Counter(p.get("iv") for p in pairs if p.get("iv"))
        sentence_dvs = Counter(p.get("dv") for p in pairs if p.get("dv"))
        fallback_sentence_iv = sentence_ivs.most_common(1)[0][0] if sentence_ivs else None
        fallback_sentence_dv = sentence_dvs.most_common(1)[0][0] if sentence_dvs else None

        sample_n = _extract_sample_size(sentence) or global_n
        direction = _detect_direction(sentence, stats)
        effect_size, effect_type = _convert_to_cohens_d(stats, sample_n) if stats else (None, None)

        for pair in pairs:
            iv = pair.get("iv")
            dv = pair.get("dv")
            iv_raw = pair.get("iv_raw")
            dv_raw = pair.get("dv_raw")
            iv_conf = float(pair.get("iv_conf", 0.0))
            dv_conf = float(pair.get("dv_conf", 0.0))

            if not iv and dv:
                iv = fallback_sentence_iv or fallback_global_iv
                if iv and iv != dv:
                    iv_conf = max(iv_conf, _MIN_MAP_CONF)
                    if not iv_raw:
                        iv_raw = iv
            if not dv and iv:
                dv = fallback_sentence_dv or fallback_global_dv
                if dv and dv != iv:
                    dv_conf = max(dv_conf, _MIN_MAP_CONF)
                    if not dv_raw:
                        dv_raw = dv
            if not iv or not dv:
                continue
            if iv == dv:
                continue

            direction_for_pair = _pair_specific_direction(
                sentence=sentence,
                pair=pair,
                sentence_direction=direction or "unknown",
            )

            key = (
                _normalize_space(iv or iv_raw).lower(),
                _normalize_space(dv or dv_raw).lower(),
                direction_for_pair,
            )
            if key in seen:
                continue
            conf = _claim_confidence(
                iv_conf=iv_conf,
                dv_conf=dv_conf,
                direction=direction_for_pair,
                has_effect=effect_size is not None,
                sample_n=sample_n,
            )
            min_conf = _MIN_RELAXED_CLAIM_CONF if relaxed_pass else _MIN_CLAIM_CONF
            if conf < min_conf:
                continue
            seen.add(key)
            seq += 1
            claims.append(
                {
                    "claim_id": f"abs:{paper_id}:C{seq:03d}",
                    "paper_id": paper_id,
                    "iv": iv,
                    "iv_raw": iv_raw,
                    "iv_mapped": bool(iv),
                    "iv_confidence": round(iv_conf, 2),
                    "dv": dv,
                    "dv_raw": dv_raw,
                    "dv_mapped": bool(dv),
                    "dv_confidence": round(dv_conf, 2),
                    "direction": direction_for_pair,
                    "effect_size": effect_size,
                    "effect_size_type": effect_type,
                    "sample_n": sample_n,
                    "p_value": stats.get("p_value"),
                    "context": context,
                    "source_quote": sentence[:600],
                    "extraction_confidence": round(conf, 2),
                    "vocabulary_mapped": bool(iv and dv),
                    "source": "abstract",
                    "extraction_method": "abstract_rule_v3" if relaxed_pass else "abstract_rule_v2",
                    "article_type_family": article_type_family,
                }
            )
    return _backfill_unknown_directions(claims)


def extract_claims_from_captions(
    paper_id: str,
    captions: list[dict[str, Any]],
    vocabulary: dict[str, Any],
    article_type_family: str | None = None,
) -> list[dict[str, Any]]:
    """Extract claims from result-oriented figure/table captions."""
    claims: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    seq = 0

    for item in captions:
        caption = _normalize_space(item.get("text"))
        if not _is_results_caption(caption):
            continue
        stats = _extract_statistics(caption)
        sample_n = _extract_sample_size(caption)
        direction = _detect_direction(caption, stats)
        effect_size, effect_type = _convert_to_cohens_d(stats, sample_n) if stats else (None, None)
        pairs = _extract_caption_pair_candidates(caption, vocabulary)
        if not pairs:
            continue

        for pair in pairs:
            iv = pair.get("iv")
            iv_raw = pair.get("iv_raw")
            dv = pair.get("dv")
            dv_raw = pair.get("dv_raw")
            dv_conf = float(pair.get("dv_conf", 0.0))
            if not iv or not dv:
                continue
            if iv == dv:
                continue
            key = (
                _normalize_space(iv or iv_raw).lower(),
                _normalize_space(dv or dv_raw).lower(),
                direction,
                _normalize_space(item.get("source_table_id")).lower(),
            )
            if key in seen:
                continue
            conf = _claim_confidence(
                iv_conf=float(pair.get("iv_conf", 0.0)),
                dv_conf=dv_conf,
                direction=direction,
                has_effect=effect_size is not None,
                sample_n=sample_n,
            )
            if conf < _MIN_CLAIM_CONF:
                continue
            seen.add(key)
            seq += 1
            claims.append(
                {
                    "claim_id": f"cap:{paper_id}:C{seq:03d}",
                    "paper_id": paper_id,
                    "iv": iv,
                    "iv_raw": iv_raw,
                    "iv_mapped": bool(iv),
                    "iv_confidence": round(float(pair.get("iv_conf", 0.0)), 2),
                    "dv": dv,
                    "dv_raw": dv_raw,
                    "dv_mapped": bool(dv),
                    "dv_confidence": round(dv_conf, 2),
                    "direction": direction,
                    "effect_size": effect_size,
                    "effect_size_type": effect_type,
                    "sample_n": sample_n,
                    "p_value": stats.get("p_value"),
                    "context": _detect_context(caption),
                    "source_table_id": item.get("source_table_id"),
                    "source_page": item.get("source_page"),
                    "source_origin": item.get("source_origin"),
                    "source_quote": caption[:600],
                    "extraction_confidence": round(conf, 2),
                    "vocabulary_mapped": bool(iv and dv),
                    "source": "caption",
                    "extraction_method": "caption_rule_v2",
                    "article_type_family": article_type_family,
                }
            )
    return claims


def _load_triage_records(path: str) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    assert_valid_payload("paper_triage", payload, strict=True)
    if isinstance(payload, dict) and isinstance(payload.get("papers"), list):
        return [p for p in payload["papers"] if isinstance(p, dict)]
    if isinstance(payload, dict):
        out = []
        for pid, rec in payload.items():
            if not isinstance(rec, dict):
                continue
            out.append({"paper_id": pid, **rec})
        return out
    return []


def _collect_captions_from_confirmed_csv(path: str) -> dict[str, list[dict[str, Any]]]:
    by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[tuple[str, str, str]] = set()
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            quote = _extract_table_caption_span(row.get("source_quote", ""))
            if not quote:
                continue
            paper_id = _normalize_space(row.get("paper_id"))
            if not paper_id:
                continue
            table_id = _normalize_space(row.get("source_table_id"))
            key = (paper_id, table_id, quote.lower())
            if key in seen:
                continue
            seen.add(key)
            by_paper[paper_id].append(
                {
                    "text": quote,
                    "source_table_id": table_id or None,
                    "source_page": _as_int(row.get("source_page_start") or row.get("source_page_end")),
                    "source_origin": "confirmed_csv",
                }
            )
    return by_paper


def _extract_captions_from_page_text(text: str, page: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    raw_text = str(text or "")
    matches = list(_CAPTION_LINE_RE.finditer(raw_text))
    for idx, m in enumerate(matches):
        start = m.start()
        next_start = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw_text)
        end = min(next_start, m.end() + 420)
        raw = raw_text[start:end]
        cap = _normalize_space(raw)
        if len(cap) < 20:
            continue
        out.append(
            {
                "text": cap,
                "source_table_id": None,
                "source_page": page,
                "source_origin": "preprocess_cache",
            }
        )
    return out


def _collect_captions_from_preprocess_cache(
    paper_ids: list[str],
    preprocess_dir: str,
) -> dict[str, list[dict[str, Any]]]:
    by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for paper_id in paper_ids:
        path = Path(preprocess_dir) / f"{paper_id}.json"
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        pages = payload.get("pages") or []
        for page in pages[:35]:
            page_num = int(page.get("page") or 0)
            page_text = str(page.get("text") or "")
            by_paper[paper_id].extend(_extract_captions_from_page_text(page_text, page_num))
    return by_paper


def _merge_caption_sources(
    csv_caps: dict[str, list[dict[str, Any]]],
    preprocess_caps: dict[str, list[dict[str, Any]]],
    table_class_caps: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[tuple[str, str, str]] = set()
    for source_map, source_name in (
        (csv_caps, "confirmed_csv"),
        (preprocess_caps, "preprocess_cache"),
        (table_class_caps, "table_classifications"),
    ):
        for paper_id, caps in source_map.items():
            for cap in caps:
                text = _normalize_space(cap.get("text"))
                if not text:
                    continue
                table_id = _normalize_space(cap.get("source_table_id"))
                key = (paper_id, table_id, text.lower())
                if key in seen:
                    continue
                seen.add(key)
                merged = dict(cap)
                merged.setdefault("source_origin", source_name)
                out[paper_id].append(merged)
    return out


def _collect_captions_from_table_classifications(path: str, strict_contracts: bool = False) -> dict[str, list[dict[str, Any]]]:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    assert_valid_payload("table_classifications", payload, strict=strict_contracts)

    items: list[tuple[str, dict[str, Any]]] = []
    if isinstance(payload, dict) and not isinstance(payload.get("tables"), list):
        items = [(str(tid), rec) for tid, rec in payload.items() if isinstance(rec, dict)]
    elif isinstance(payload, dict) and isinstance(payload.get("tables"), list):
        for idx, rec in enumerate(payload.get("tables", [])):
            if not isinstance(rec, dict):
                continue
            table_id = str(rec.get("table_id") or rec.get("source_table_id") or f"TBL-{idx:06d}")
            items.append((table_id, rec))
    elif isinstance(payload, list):
        for idx, rec in enumerate(payload):
            if not isinstance(rec, dict):
                continue
            table_id = str(rec.get("table_id") or rec.get("source_table_id") or f"TBL-{idx:06d}")
            items.append((table_id, rec))

    by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for table_id, rec in items:
        paper_id = _normalize_space(rec.get("paper_id"))
        raw_text = rec.get("sample_content") or rec.get("caption") or ""
        text = _extract_table_caption_span(raw_text)
        if not paper_id or not text:
            continue
        by_paper[paper_id].append(
            {
                "text": text,
                "source_table_id": table_id,
                "source_page": _as_int(rec.get("page")),
                "source_origin": "table_classifications",
            }
        )
    return by_paper


def _build_table_page_index(path: str, strict_contracts: bool = False) -> dict[str, dict[int, list[str]]]:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}
    assert_valid_payload("table_classifications", payload, strict=strict_contracts)

    index: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    items: list[tuple[str, dict[str, Any]]] = []
    if isinstance(payload, dict) and not isinstance(payload.get("tables"), list):
        items = [(str(tid), rec) for tid, rec in payload.items() if isinstance(rec, dict)]
    elif isinstance(payload, dict) and isinstance(payload.get("tables"), list):
        for idx, rec in enumerate(payload.get("tables", [])):
            if not isinstance(rec, dict):
                continue
            table_id = str(rec.get("table_id") or rec.get("source_table_id") or f"TBL-{idx:06d}")
            items.append((table_id, rec))
    elif isinstance(payload, list):
        for idx, rec in enumerate(payload):
            if not isinstance(rec, dict):
                continue
            table_id = str(rec.get("table_id") or rec.get("source_table_id") or f"TBL-{idx:06d}")
            items.append((table_id, rec))

    for table_id, rec in items:
        paper_id = _normalize_space(rec.get("paper_id"))
        page = _as_int(rec.get("page"))
        if not paper_id or page is None:
            continue
        index[paper_id][page].append(table_id)
    return index


def _attach_table_ids_by_page(
    captions_by_paper: dict[str, list[dict[str, Any]]],
    table_page_index: dict[str, dict[int, list[str]]],
) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for paper_id, captions in captions_by_paper.items():
        page_map = table_page_index.get(paper_id, {})
        for cap in captions:
            c = dict(cap)
            if c.get("source_table_id"):
                out[paper_id].append(c)
                continue
            text = _normalize_space(c.get("text"))
            if not _TABLE_START_RE.match(text):
                out[paper_id].append(c)
                continue
            page = _as_int(c.get("source_page"))
            if page is None:
                out[paper_id].append(c)
                continue
            candidate_ids = list(page_map.get(page, []))
            if len(candidate_ids) != 1:
                # fallback to nearest page if unique best candidate
                nearest: list[str] = []
                for delta in (1, 2):
                    ids = page_map.get(page - delta, []) + page_map.get(page + delta, [])
                    if len(ids) == 1:
                        nearest = ids
                        break
                candidate_ids = nearest
            if len(candidate_ids) == 1:
                c["source_table_id"] = candidate_ids[0]
                c["source_origin"] = str(c.get("source_origin") or "unknown") + "+page_match"
            out[paper_id].append(c)
    return out


def _build_caption_dv_lookup(
    captions_by_paper: dict[str, list[dict[str, Any]]],
    vocabulary: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for paper_id, captions in captions_by_paper.items():
        for cap in captions:
            table_id = _normalize_space(cap.get("source_table_id"))
            if not table_id:
                continue
            text = _normalize_space(cap.get("text"))
            if not _TABLE_START_RE.match(text):
                continue
            if not _is_results_caption(text):
                continue
            dv_raw, dv, conf = _extract_caption_dv(text, vocabulary)
            if not dv_raw or not dv or conf < 0.65:
                continue
            prev = lookup.get(table_id)
            if prev and float(prev.get("confidence", 0.0)) >= conf:
                continue
            lookup[table_id] = {
                "paper_id": paper_id,
                "source_page": _as_int(cap.get("source_page")),
                "dv_raw": dv_raw,
                "dv": dv,
                "confidence": round(float(conf), 3),
                "caption": text[:600],
            }
    return lookup


def batch_extract_abstracts_and_captions(
    triage_path: str = "data/production/paper_triage.json",
    confirmed_csv_path: str = "data/production/realtime_pdf_confirmed_rows.csv",
    table_classifications_path: str = "data/production/table_classifications.json",
    metadata_csv_path: str = _DEFAULT_METADATA_CSV,
    preprocess_cache_dir: str = _DEFAULT_PREPROCESS_DIR,
    article_db_path: str | None = _DEFAULT_ARTICLE_DB,
    vocabulary_path: str = "data/vocabulary/variable_vocabulary.json",
    output_path: str = "data/production/abstract_claims.json",
    caption_lookup_output_path: str = "data/production/caption_dv_lookup.json",
    limit: int | None = None,
    strict_contracts: bool = True,
) -> dict[str, Any]:
    """Batch extract abstract and caption claims and persist required artifacts."""
    vocab = load_vocabulary(vocabulary_path)
    triage_records = _load_triage_records(triage_path)
    if limit is not None:
        triage_records = triage_records[:limit]

    metadata_map = _load_metadata_csv(metadata_csv_path)
    db_path: Path | None = None
    try:
        db_path = resolve_article_finder_db(article_db_path)
    except Exception:
        if article_db_path:
            db_path = Path(article_db_path)
    db_conn: sqlite3.Connection | None = None
    if db_path is not None and db_path.exists():
        try:
            db_conn = sqlite3.connect(str(db_path))
        except Exception:
            db_conn = None

    abstract_claims: list[dict[str, Any]] = []
    abstracts_seen = 0
    abstract_source_counts: Counter[str] = Counter()
    for rec in triage_records:
        paper_id = _normalize_space(rec.get("paper_id"))
        abstract, title, abstract_source = _resolve_abstract_and_title(
            rec=rec,
            metadata_map=metadata_map,
            db_conn=db_conn,
            preprocess_dir=preprocess_cache_dir,
        )
        abstract = _normalize_space(abstract)
        abstract_source_counts[abstract_source] += 1
        if not paper_id or len(abstract) < 40:
            continue
        abstracts_seen += 1
        new_claims = extract_claims_from_abstract(
            paper_id=paper_id,
            title=title or "",
            abstract=abstract,
            vocabulary=vocab,
            article_type_family=_normalize_space(rec.get("article_type_family")) or None,
        )
        for claim in new_claims:
            claim["abstract_source"] = abstract_source
        abstract_claims.extend(new_claims)

    if db_conn is not None:
        db_conn.close()

    paper_ids = [_normalize_space(rec.get("paper_id")) for rec in triage_records if _normalize_space(rec.get("paper_id"))]
    csv_captions = _collect_captions_from_confirmed_csv(confirmed_csv_path)
    preprocess_captions = _collect_captions_from_preprocess_cache(
        paper_ids=paper_ids,
        preprocess_dir=preprocess_cache_dir,
    )
    table_class_captions = _collect_captions_from_table_classifications(
        table_classifications_path,
        strict_contracts=False,
    )
    captions_by_paper = _merge_caption_sources(csv_captions, preprocess_captions, table_class_captions)
    table_page_index = _build_table_page_index(table_classifications_path, strict_contracts=False)
    captions_by_paper = _attach_table_ids_by_page(captions_by_paper, table_page_index)

    caption_claims: list[dict[str, Any]] = []
    caption_papers = 0
    caption_source_counts: Counter[str] = Counter()
    for rec in triage_records:
        paper_id = _normalize_space(rec.get("paper_id"))
        caps = captions_by_paper.get(paper_id, [])
        if not caps:
            continue
        for cap in caps:
            caption_source_counts[str(cap.get("source_origin") or "unknown")] += 1
        caption_papers += 1
        caption_claims.extend(
            extract_claims_from_captions(
                paper_id=paper_id,
                captions=caps,
                vocabulary=vocab,
                article_type_family=_normalize_space(rec.get("article_type_family")) or None,
            )
        )

    caption_lookup = _build_caption_dv_lookup(captions_by_paper, vocab)
    all_claims = [*abstract_claims, *caption_claims]

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "rule_based_v2",
        "papers_considered": len(triage_records),
        "papers_with_abstract": abstracts_seen,
        "papers_with_caption_candidates": caption_papers,
        "from_abstracts": len(abstract_claims),
        "from_captions": len(caption_claims),
        "total_claims": len(all_claims),
        "caption_dv_lookup_entries": len(caption_lookup),
        "abstract_source_counts": dict(abstract_source_counts),
        "caption_source_counts": dict(caption_source_counts),
        "source_counts": dict(Counter(str(c.get("source") or "unknown") for c in all_claims)),
    }

    output_payload = {
        "generated_at": summary["generated_at"],
        "claims": all_claims,
        "summary": summary,
    }
    assert_valid_payload("abstract_claims", output_payload, strict=strict_contracts)
    assert_valid_payload("caption_dv_lookup", caption_lookup, strict=strict_contracts)

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output_payload, indent=2, ensure_ascii=True), encoding="utf-8")

    lookup_path = Path(caption_lookup_output_path)
    lookup_path.parent.mkdir(parents=True, exist_ok=True)
    lookup_path.write_text(json.dumps(caption_lookup, indent=2, ensure_ascii=True), encoding="utf-8")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch abstract/caption extraction for Sprint D.")
    parser.add_argument("--triage-path", default="data/production/paper_triage.json")
    parser.add_argument("--confirmed-csv-path", default="data/production/realtime_pdf_confirmed_rows.csv")
    parser.add_argument("--table-classifications-path", default="data/production/table_classifications.json")
    parser.add_argument("--metadata-csv-path", default=_DEFAULT_METADATA_CSV)
    parser.add_argument("--preprocess-cache-dir", default=_DEFAULT_PREPROCESS_DIR)
    parser.add_argument(
        "--article-db-path",
        default=_DEFAULT_ARTICLE_DB,
        help="Path to article_finder.db (auto-resolved if omitted)",
    )
    parser.add_argument("--vocabulary-path", default="data/vocabulary/variable_vocabulary.json")
    parser.add_argument("--output-path", default="data/production/abstract_claims.json")
    parser.add_argument("--caption-lookup-output-path", default="data/production/caption_dv_lookup.json")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--no-strict-contracts", action="store_true")
    args = parser.parse_args()

    summary = batch_extract_abstracts_and_captions(
        triage_path=args.triage_path,
        confirmed_csv_path=args.confirmed_csv_path,
        table_classifications_path=args.table_classifications_path,
        metadata_csv_path=args.metadata_csv_path,
        preprocess_cache_dir=args.preprocess_cache_dir,
        article_db_path=args.article_db_path,
        vocabulary_path=args.vocabulary_path,
        output_path=args.output_path,
        caption_lookup_output_path=args.caption_lookup_output_path,
        limit=args.limit,
        strict_contracts=not args.no_strict_contracts,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
