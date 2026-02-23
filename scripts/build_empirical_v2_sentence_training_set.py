#!/usr/bin/env python3
"""Build sentence->field training examples for empirical_v2 extraction.

This script creates:
1) A high-confidence "silver" training set JSONL.
2) A lower-confidence review queue JSONL for human cleanup into gold labels.

Primary source is structured claims (already merged across abstract/caption/table).
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CLAIMS_PATH = "data/production/structured_claims.json"
DEFAULT_OUT_TRAIN = "data/training/empirical_v2_sentence_field_pairs.jsonl"
DEFAULT_OUT_REVIEW = "data/training/empirical_v2_sentence_field_pairs.review.jsonl"
DEFAULT_OUT_SUMMARY = "data/training/empirical_v2_sentence_field_pairs.summary.json"
DEFAULT_ALLOWED_SOURCES = "abstract,caption"
DEFAULT_SENTENCES_PER_CLAIM = 2
GENERIC_SPAN_PATTERNS = [
    r"^in this study$",
    r"^this study$",
    r"^the study$",
    r"^results?$",
    r"^the results?$",
    r"^results? (indicate|indicated|suggest|suggested|show|showed|found)$",
    r"^we (found|showed|observed)$",
]


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _looks_ocr_noisy(text: str) -> bool:
    t = _normalize(text)
    if not t:
        return True
    # repeated characters, long no-space tokens, odd punctuation density
    if re.search(r"(.)\1{3,}", t):
        return True
    if re.search(r"\b[^\s]{35,}\b", t):
        return True
    punct = len(re.findall(r"[,;:()\[\]{}]", t))
    alpha = len(re.findall(r"[A-Za-z]", t))
    if alpha > 0 and punct / alpha > 0.35:
        return True
    return False


def _direction(value: Any) -> str:
    s = _normalize(value).lower()
    if s in {"increase", "decrease", "no_effect", "curvilinear", "unknown"}:
        return s
    return "unknown"


def _looks_placeholder_variable(text: str) -> bool:
    t = _normalize(text).lower()
    if not t:
        return True
    return bool(
        re.search(
            r"\b(col(?:umn)?[_\s-]*\d+|row[_\s-]*\d+|cell[_\s-]*\d+|var[_\s-]*\d+|x\d+|y\d+|value[_\s-]*\d*)\b",
            t,
        )
    )


def _sentence_direction_signal(sentence: str) -> str:
    s = sentence.lower()
    if re.search(r"\b(no significant|not significant|non-significant|ns\b|p\s*[>=]\s*0?\.0?5)\b", s):
        return "no_effect"
    inc = bool(re.search(r"\b(increase|increased|higher|greater|improv|enhanc|positive effect)\b", s))
    dec = bool(re.search(r"\b(decrease|decreased|lower|reduc|diminish|negative effect)\b", s))
    if inc and not dec:
        return "increase"
    if dec and not inc:
        return "decrease"
    return "unknown"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _reliability_score(claim: dict[str, Any], sentence: str) -> float:
    score = _safe_float(claim.get("extraction_confidence"), 0.0)
    direction = _direction(claim.get("direction"))
    if direction != "unknown":
        score += 0.08
    if claim.get("effect_size") is not None or claim.get("p_value") is not None:
        score += 0.08
    if _normalize(claim.get("claim_source")) in {"table", "caption"}:
        score += 0.04
    if _looks_ocr_noisy(sentence):
        score -= 0.20
    if _normalize(claim.get("iv")) == _normalize(claim.get("dv")):
        score -= 0.30
    return max(0.0, min(1.0, score))


def _split_sentences(quote: str) -> list[str]:
    text = _normalize(quote)
    if not text:
        return []
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]


def _candidate_sentence_score(sentence: str, iv_raw: str, dv_raw: str) -> int:
    low = sentence.lower()
    iv_low = _normalize(iv_raw).lower()
    dv_low = _normalize(dv_raw).lower()
    score = 0
    if iv_low and iv_low in low:
        score += 2
    if dv_low and dv_low in low:
        score += 2
    if re.search(r"\b(significant|associated|increase|decrease|effect|predict|p\s*[<=>])\b", low):
        score += 1
    return score


def _select_sentences(
    quote: str,
    iv_raw: str,
    dv_raw: str,
    max_sentences: int,
) -> list[tuple[int, str, str]]:
    """Pick up to N whole sentences plus a local context window."""
    parts = _split_sentences(quote)
    if not parts:
        return []
    scored = [(idx, sent, _candidate_sentence_score(sent, iv_raw, dv_raw)) for idx, sent in enumerate(parts)]
    scored.sort(key=lambda row: row[2], reverse=True)
    selected: list[tuple[int, str, str]] = []
    used: set[int] = set()
    for idx, sent, _ in scored:
        if idx in used:
            continue
        used.add(idx)
        left = parts[idx - 1] if idx > 0 else ""
        right = parts[idx + 1] if idx + 1 < len(parts) else ""
        window = " ".join([chunk for chunk in [left, sent, right] if chunk]).strip()
        selected.append((idx, sent, window))
        if len(selected) >= max(1, max_sentences):
            break
    selected.sort(key=lambda row: row[0])
    return selected


def _find_span(sentence: str, term: str) -> dict[str, Any] | None:
    if not sentence or not term:
        return None
    m = re.search(re.escape(term), sentence, flags=re.IGNORECASE)
    if not m:
        return None
    return {
        "text": sentence[m.start() : m.end()],
        "matched_term": term,
        "char_start": m.start(),
        "char_end": m.end(),
    }


def _regex_span(sentence: str, pattern: str) -> dict[str, Any] | None:
    if not sentence:
        return None
    m = re.search(pattern, sentence, flags=re.IGNORECASE)
    if not m:
        return None
    return {
        "text": sentence[m.start() : m.end()],
        "char_start": m.start(),
        "char_end": m.end(),
    }


def _candidate_terms(raw_value: str, canonical_value: str) -> list[str]:
    terms: list[str] = []
    raw = _normalize(raw_value)
    canonical = _normalize(canonical_value).replace("_", " ")
    for seed in [raw, canonical]:
        if seed and seed not in terms:
            terms.append(seed)
    if raw:
        for part in re.split(r"\b(?:while|and|which|that)\b|[,;:]", raw, flags=re.IGNORECASE):
            p = _normalize(part)
            if not p:
                continue
            if len(p) < 4:
                continue
            if len(p) > 60:
                continue
            if _is_generic_surface_term(p):
                continue
            if p not in terms:
                terms.append(p)
    return terms


def _is_generic_surface_term(term: str) -> bool:
    low = _normalize(term).lower()
    if not low:
        return True
    for pattern in GENERIC_SPAN_PATTERNS:
        if re.search(pattern, low):
            return True
    # If a very short phrase is mostly reporting verbs, treat as non-variable text.
    if len(low.split()) <= 4 and re.search(r"\b(results?|study|found|indicat\w*|suggest\w*|show\w*)\b", low):
        return True
    return False


def _best_span(sentence: str, raw_value: str, canonical_value: str) -> dict[str, Any] | None:
    candidates = _candidate_terms(raw_value, canonical_value)
    best: tuple[float, dict[str, Any]] | None = None
    canonical = _normalize(canonical_value).replace("_", " ").lower()
    for term in candidates:
        span = _find_span(sentence, term)
        if not span:
            continue
        low = term.lower()
        words = len([w for w in low.split() if w])
        score = 0.0
        if canonical and low == canonical:
            score += 3.0
        if _is_generic_surface_term(low):
            score -= 5.0
        if 1 <= words <= 5:
            score += 2.0
        if len(low) <= 40:
            score += 1.0
        score -= min(1.0, len(low) / 150.0)
        if best is None or score > best[0]:
            best = (score, span)
    return best[1] if best else None


def _field_evidence(sentence: str, claim: dict[str, Any]) -> dict[str, Any]:
    iv_raw = _normalize(claim.get("iv_raw")) or _normalize(claim.get("iv"))
    dv_raw = _normalize(claim.get("dv_raw")) or _normalize(claim.get("dv"))
    iv = _normalize(claim.get("iv"))
    dv = _normalize(claim.get("dv"))
    direction = _direction(claim.get("direction"))
    direction_pattern = (
        r"\b(increase|increased|higher|greater|improv\w*|enhanc\w*|positive effect)\b"
        if direction == "increase"
        else r"\b(decrease|decreased|lower|reduc\w*|diminish\w*|negative effect)\b"
        if direction == "decrease"
        else r"\b(no significant|not significant|non-significant|ns\b|p\s*[>=]\s*0?\.0?5)\b"
        if direction == "no_effect"
        else r"\b(increase|decrease|associated|effect|significant)\b"
    )
    return {
        "iv_span": _best_span(sentence, iv_raw, iv),
        "dv_span": _best_span(sentence, dv_raw, dv),
        "direction_span": _regex_span(sentence, direction_pattern),
        "p_value_span": _regex_span(sentence, r"\bp\s*[<=>]\s*0?\.\d+\b"),
        "effect_size_span": _regex_span(sentence, r"\b(?:d|g|r|eta2|η2|beta|β|or|odds ratio|f|t)\s*[=]\s*[-+]?\d*\.?\d+\b"),
        "significance_cue_span": _regex_span(sentence, r"\b(significant|associated|predict\w*|effect)\b"),
    }


def _build_record(
    claim: dict[str, Any],
    sentence: str,
    reliability: float,
    sentence_index: int,
    sentence_count_in_quote: int,
    context_window: str,
) -> dict[str, Any]:
    direction = _direction(claim.get("direction"))
    base_record_id = _normalize(claim.get("claim_id")) or "unknown_claim"
    evidence = _field_evidence(sentence, claim)
    record_id = f"{base_record_id}:S{sentence_index + 1}"
    return {
        "record_id": record_id,
        "claim_id": base_record_id,
        "paper_id": _normalize(claim.get("paper_id")),
        "article_type_family": _normalize(claim.get("article_type_family")) or "unknown",
        "claim_source": _normalize(claim.get("claim_source")) or _normalize(claim.get("source")) or "unknown",
        "sentence_text": sentence,
        "raw_quote": _normalize(claim.get("source_quote")),
        "context_window_text": _normalize(context_window) or sentence,
        "sentence_meta": {
            "sentence_index": sentence_index,
            "sentence_count_in_quote": sentence_count_in_quote,
        },
        "fields": {
            "iv_raw": _normalize(claim.get("iv_raw")) or _normalize(claim.get("iv")),
            "dv_raw": _normalize(claim.get("dv_raw")) or _normalize(claim.get("dv")),
            "iv": _normalize(claim.get("iv")) or None,
            "dv": _normalize(claim.get("dv")) or None,
            "direction": direction,
            "effect_size": claim.get("effect_size"),
            "effect_size_type": claim.get("effect_size_type"),
            "p_value": claim.get("p_value"),
            "sample_n": claim.get("sample_n"),
            "is_significant": claim.get("is_significant"),
            "context": _normalize(claim.get("context")) or None,
            "claim_type": _normalize(claim.get("claim_type")) or "unknown",
            "provenance_depth": _normalize(claim.get("provenance_depth")) or "unknown",
        },
        "field_evidence": evidence,
        "label_quality": {
            "extraction_confidence": _safe_float(claim.get("extraction_confidence"), 0.0),
            "reliability_score": round(reliability, 4),
            "ocr_noisy_sentence": _looks_ocr_noisy(sentence),
            "placeholder_variable_detected": _looks_placeholder_variable(_normalize(claim.get("iv_raw")))
            or _looks_placeholder_variable(_normalize(claim.get("dv_raw"))),
        },
        "created_at": _utc_iso(),
    }


def _write_jsonl(path: str, records: list[dict[str, Any]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=True) + "\n")


def build_dataset(
    claims_path: str,
    out_train: str,
    out_review: str,
    out_summary: str,
    min_reliability: float,
    min_sentence_chars: int,
    max_per_direction: int,
    allowed_sources: set[str],
    sentences_per_claim: int,
) -> dict[str, Any]:
    payload = json.loads(Path(claims_path).read_text(encoding="utf-8"))
    claims = payload.get("claims", []) if isinstance(payload, dict) else []

    train: list[dict[str, Any]] = []
    review: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    direction_cap: Counter[str] = Counter()
    claim_source_counts: Counter[str] = Counter()
    sentence_pick_counts: Counter[str] = Counter()
    span_hit_counts: Counter[str] = Counter()
    claims_with_selected = 0
    claims_with_multiple = 0

    for claim in claims:
        if not isinstance(claim, dict):
            continue
        if _normalize(claim.get("article_type_family")) not in {"empirical_v2", "unknown"}:
            continue

        quote = _normalize(claim.get("source_quote"))
        if not quote:
            continue
        source = _normalize(claim.get("claim_source")) or _normalize(claim.get("source")) or "unknown"
        if allowed_sources and "all" not in allowed_sources and source not in allowed_sources:
            continue
        selections = _select_sentences(
            quote=quote,
            iv_raw=_normalize(claim.get("iv_raw")) or _normalize(claim.get("iv")),
            dv_raw=_normalize(claim.get("dv_raw")) or _normalize(claim.get("dv")),
            max_sentences=sentences_per_claim,
        )
        if not selections:
            continue

        iv = _normalize(claim.get("iv"))
        dv = _normalize(claim.get("dv"))
        if not iv or not dv:
            continue

        selected_count_for_claim = 0
        for sent_idx, sentence, context_window in selections:
            if len(sentence) < min_sentence_chars:
                continue

            dedupe_key = (
                sentence.lower(),
                iv.lower(),
                dv.lower(),
                _direction(claim.get("direction")),
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            reliability = _reliability_score(claim, sentence)
            record = _build_record(
                claim=claim,
                sentence=sentence,
                reliability=reliability,
                sentence_index=sent_idx,
                sentence_count_in_quote=len(_split_sentences(quote)),
                context_window=context_window,
            )
            direction = record["fields"]["direction"]
            source = record["claim_source"]
            claim_source_counts[source] += 1
            sentence_pick_counts[str(source)] += 1
            noisy = bool(record["label_quality"]["ocr_noisy_sentence"])
            sent_signal = _sentence_direction_signal(sentence)
            label_dir = record["fields"]["direction"]
            direction_conflict = (
                sent_signal in {"increase", "decrease", "no_effect"}
                and label_dir in {"increase", "decrease", "no_effect"}
                and sent_signal != label_dir
            )
            placeholder_var = bool(record["label_quality"].get("placeholder_variable_detected"))
            for key, val in record.get("field_evidence", {}).items():
                if val:
                    span_hit_counts[key] += 1

            # Keep directional distribution from collapsing into a single class.
            if (
                (not noisy)
                and (not direction_conflict)
                and (not placeholder_var)
                and reliability >= min_reliability
                and direction_cap[direction] < max_per_direction
            ):
                train.append(record)
                direction_cap[direction] += 1
            else:
                if direction_conflict:
                    record.setdefault("label_quality", {})["direction_conflict_with_sentence"] = True
                    record["label_quality"]["sentence_direction_signal"] = sent_signal
                if placeholder_var:
                    record.setdefault("label_quality", {})["placeholder_variable_routed_to_review"] = True
                review.append(record)
            selected_count_for_claim += 1

        if selected_count_for_claim > 0:
            claims_with_selected += 1
        if selected_count_for_claim > 1:
            claims_with_multiple += 1

    _write_jsonl(out_train, train)
    _write_jsonl(out_review, review)

    summary = {
        "generated_at": _utc_iso(),
        "input_claims_path": claims_path,
        "input_claim_count": len(claims),
        "train_count": len(train),
        "review_count": len(review),
        "min_reliability": min_reliability,
        "direction_counts_train": dict(Counter(r["fields"]["direction"] for r in train)),
        "direction_counts_review": dict(Counter(r["fields"]["direction"] for r in review)),
        "claim_source_counts_seen": dict(claim_source_counts),
        "sentence_pick_counts_seen": dict(sentence_pick_counts),
        "field_evidence_span_hits": dict(span_hit_counts),
        "claims_with_at_least_one_sentence": claims_with_selected,
        "claims_with_multiple_sentences": claims_with_multiple,
        "sentences_per_claim": max(1, sentences_per_claim),
        "allowed_sources": sorted(allowed_sources),
        "outputs": {
            "train_jsonl": out_train,
            "review_jsonl": out_review,
        },
    }
    Path(out_summary).parent.mkdir(parents=True, exist_ok=True)
    Path(out_summary).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description="Build empirical_v2 sentence->field training set.")
    p.add_argument("--claims-path", default=DEFAULT_CLAIMS_PATH)
    p.add_argument("--out-train", default=DEFAULT_OUT_TRAIN)
    p.add_argument("--out-review", default=DEFAULT_OUT_REVIEW)
    p.add_argument("--out-summary", default=DEFAULT_OUT_SUMMARY)
    p.add_argument("--min-reliability", type=float, default=0.78)
    p.add_argument("--min-sentence-chars", type=int, default=40)
    p.add_argument("--max-per-direction", type=int, default=5000)
    p.add_argument(
        "--allowed-sources",
        default=DEFAULT_ALLOWED_SOURCES,
        help="Comma-separated claim sources to include (e.g., abstract,caption,table).",
    )
    p.add_argument("--sentences-per-claim", type=int, default=DEFAULT_SENTENCES_PER_CLAIM)
    args = p.parse_args()
    allowed_sources = {s.strip() for s in str(args.allowed_sources).split(",") if s.strip()}

    summary = build_dataset(
        claims_path=args.claims_path,
        out_train=args.out_train,
        out_review=args.out_review,
        out_summary=args.out_summary,
        min_reliability=max(0.0, min(1.0, args.min_reliability)),
        min_sentence_chars=max(20, args.min_sentence_chars),
        max_per_direction=max(100, args.max_per_direction),
        allowed_sources=allowed_sources,
        sentences_per_claim=max(1, args.sentences_per_claim),
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
