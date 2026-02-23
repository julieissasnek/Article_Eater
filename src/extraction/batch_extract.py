"""Sprint D.15 batch extraction and merge pipeline.

Merges table claims (D.10) with abstract/caption claims (D.14), and applies
caption-derived DV overrides for table extraction.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import re
import subprocess
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import glob


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.claim_extractor import extract_claims_from_paper  # noqa: E402
from src.extraction.table_classifier import EXTRACTABLE_TYPES  # noqa: E402
from src.extraction.vocabulary import find_closest_dv, load_vocabulary  # noqa: E402
from src.extraction.article_type_contract import get_family_contract  # noqa: E402
from src.extraction.contracts import assert_valid_payload  # noqa: E402


EXTRACTABLE_PAPER_TYPES = {"empirical", "review", "meta_analysis"}
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
_SAMPLE_CLAIM_PATTERN = re.compile(r"\b(sample|participant|cohort|n\s*=|demograph|male|female|age\b|years?)\b", re.I)
_METHOD_CLAIM_PATTERN = re.compile(r"\b(method|procedure|protocol|instrument|questionnaire|scale|anova|regression|analysis)\b", re.I)
_THEORY_CLAIM_PATTERN = re.compile(r"\b(theory|framework|model predicts|hypothesis)\b", re.I)
_CLAIM_TYPE_TO_RULE_TYPE = {
    "sample": "constraint",
    "methodology": "constraint",
    "descriptive": "constraint",
    "theory_link": "interaction",
    "inter_article_relation": "interaction",
}
_ALLOWED_DIRECTIONS = {"increase", "decrease", "no_effect", "unknown"}
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
_RELATION_SIGNAL_PATTERN = re.compile(
    r"(?:->|→|\b(affect|effect|impact|influenc|predict|associate|correlat|relat(?:ed)?\s+to|leads?\s+to|results?\s+in|increas|decreas)\b)",
    re.I,
)
_NO_EFFECT_PATTERN = re.compile(r"\b(no\s+(?:significant\s+)?effect|non[- ]?significant|ns\b|p\s*[>=]\s*0\.0?5)\b", re.I)
_INCREASE_PATTERN = re.compile(
    r"\b(increase[sd]?|higher|greater|improve[sd]?|enhance[sd]?|boost[sd]?|positively\s+(?:associated|related|correlated))\b",
    re.I,
)
_DECREASE_PATTERN = re.compile(
    r"\b(decrease[sd]?|lower|reduce[sd]?|impair[sd]?|worse|negatively\s+(?:associated|related|correlated))\b",
    re.I,
)
_DIRECTION_FIELDS_TO_CLEAR = (
    "theory_candidates",
    "theory_direction_expectations",
    "theory_direction_tension",
    "theory_direction_conflicts",
    "theory_null_tension",
    "theory_null_conflicts",
)
_THEORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ART": (
        "attention restoration",
        "art",
        "soft fascination",
        "being away",
        "restorative",
        "directed attention",
    ),
    "SRT": (
        "stress recovery",
        "srt",
        "ulrich",
        "physiological stress",
        "cortisol",
        "parasympathetic",
    ),
    "Biophilia": (
        "biophilia",
        "biophilic",
        "nature connectedness",
        "living systems",
    ),
    "Prospect-Refuge": (
        "prospect-refuge",
        "prospect refuge",
        "prospect",
        "refuge",
        "appleton",
        "shelter",
        "openness and enclosure",
    ),
}
_NATURE_IV_HINTS = {
    "has_nature_view",
    "view_content",
    "window_area_ratio",
    "natural_material_ratio",
    "primary_material",
}
_ART_DV_INCREASE = {
    "attention",
    "cognitive_flexibility",
    "memory",
    "learning",
    "restorative_experience",
    "well_being",
    "mood",
    "productivity",
}
_ART_DV_DECREASE = {"stress", "cognitive_load", "physiological_arousal"}
_SRT_DV_DECREASE = {
    "stress",
    "cortisol",
    "blood_pressure",
    "physiological_arousal",
    "recovery_time",
    "pain_medication_use",
}
_SRT_DV_INCREASE = {"heart_rate_variability", "well_being", "mood", "sleep_quality"}
_BIOPHILIA_DV_INCREASE = {"well_being", "mood", "preference", "aesthetic_pleasure", "place_attachment"}
_BIOPHILIA_DV_DECREASE = {"stress", "physiological_arousal"}
_PR_DV_INCREASE = {"preference", "well_being", "privacy_satisfaction", "aesthetic_pleasure"}
_PR_DV_DECREASE = {"stress", "physiological_arousal"}


def _normalize_key_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _normalize_article_family(value: Any) -> str:
    key = _normalize_key_text(value)
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


def _coalesce_article_family(primary: Any, fallback: Any) -> str:
    """Prefer primary family unless it normalizes to unknown."""
    p = _normalize_article_family(primary)
    if p != "unknown":
        return p
    return _normalize_article_family(fallback)


def _infer_claim_type(claim: dict[str, Any], article_type_family: str) -> str:
    existing = _normalize_key_text(claim.get("claim_type"))
    if existing:
        return existing

    direction = _normalize_key_text(claim.get("direction"))
    iv = _normalize_key_text(claim.get("iv") or claim.get("iv_raw"))
    dv = _normalize_key_text(claim.get("dv") or claim.get("dv_raw"))
    text_blob = " ".join(
        str(claim.get(k) or "")
        for k in ("source_quote", "context", "semantic_type", "extraction_method")
    ).lower()

    if iv and dv:
        if direction in {"no_effect", "null"} or _NULL_CLAIM_PATTERN.search(text_blob):
            return "null"
        if _MODERATED_CLAIM_PATTERN.search(text_blob):
            return "moderated"
        if _MECHANISTIC_CLAIM_PATTERN.search(text_blob):
            return "mechanistic"
        return "associational"

    if _SAMPLE_CLAIM_PATTERN.search(text_blob):
        return "sample"
    if _METHOD_CLAIM_PATTERN.search(text_blob):
        return "methodology"
    if _THEORY_CLAIM_PATTERN.search(text_blob):
        return "theory_link"
    return "descriptive"


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


def _safe_int(value: str | int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


def _table_sort_key(row: dict[str, Any]) -> tuple[int, int]:
    row_index = row.get("row_index")
    if isinstance(row_index, int):
        return (0, row_index)
    return (1, int(row.get("_seq", 0)))


def _load_triage(triage_path: str) -> dict[str, dict[str, Any]]:
    with open(triage_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    assert_valid_payload("paper_triage", payload, strict=True)

    if isinstance(payload, dict) and isinstance(payload.get("papers"), list):
        out: dict[str, dict[str, Any]] = {}
        for paper in payload["papers"]:
            if not isinstance(paper, dict):
                continue
            paper_id = str(paper.get("paper_id") or "").strip()
            if not paper_id:
                continue
            out[paper_id] = {
                "type": paper.get("triage_type") or paper.get("type"),
                "article_type_family": paper.get("article_type_family"),
                "confidence": paper.get("confidence"),
                "extractable": paper.get("extractable"),
                "title": paper.get("title"),
                "abstract": paper.get("abstract"),
            }
        return out

    if isinstance(payload, dict):
        out: dict[str, dict[str, Any]] = {}
        for paper_id, info in payload.items():
            if not isinstance(info, dict):
                continue
            out[str(paper_id)] = {
                "type": info.get("type") or info.get("triage_type"),
                "article_type_family": info.get("article_type_family"),
                "confidence": info.get("confidence"),
                "extractable": info.get("extractable"),
                "title": info.get("title"),
                "abstract": info.get("abstract"),
            }
        return out

    raise ValueError(f"Unsupported triage payload in {triage_path}")


def _load_table_classifications(table_class_path: str) -> dict[str, dict[str, Any]]:
    with open(table_class_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    assert_valid_payload("table_classifications", payload, strict=True)

    if isinstance(payload, dict) and not isinstance(payload.get("tables"), list):
        return {str(tid): rec for tid, rec in payload.items() if isinstance(rec, dict)}

    items: list[Any]
    if isinstance(payload, dict) and isinstance(payload.get("tables"), list):
        items = payload["tables"]
    elif isinstance(payload, list):
        items = payload
    else:
        raise ValueError(f"Unsupported table classifications payload in {table_class_path}")

    out: dict[str, dict[str, Any]] = {}
    for idx, rec in enumerate(items):
        if not isinstance(rec, dict):
            continue
        table_id = str(rec.get("table_id") or rec.get("source_table_id") or f"TBL-{idx:06d}")
        out[table_id] = rec
    return out


def _is_table_extractable(table_rec: dict[str, Any]) -> bool:
    extractable = table_rec.get("extractable")
    if isinstance(extractable, bool):
        return extractable
    table_type = str(table_rec.get("type") or "").strip()
    return table_type in EXTRACTABLE_TYPES


def _load_rows_from_csv(
    csv_path: str,
    allowed_papers: set[str],
    allowed_tables: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, str]]]:
    table_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    paper_context: dict[str, dict[str, str]] = {}

    with open(csv_path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for seq, row in enumerate(reader):
            paper_id = (row.get("paper_id") or "").strip()
            if paper_id not in allowed_papers:
                continue

            table_id = (row.get("source_table_id") or "").strip()
            if table_id and table_id in allowed_tables:
                text = (
                    row.get("source_quote")
                    or row.get("statement")
                    or row.get("content")
                    or ""
                ).strip()
                table_rows[table_id].append(
                    {
                        "row_index": _safe_int(row.get("source_table_row")),
                        "text": text,
                        "source_quote": (row.get("source_quote") or "").strip(),
                        "_seq": seq,
                    }
                )

            if paper_id not in paper_context:
                paper_context[paper_id] = {
                    "title": (row.get("title") or "").strip(),
                    "abstract": (row.get("abstract") or "").strip(),
                    "article_type": (row.get("article_type_predicted_family") or "").strip(),
                }

    for rows in table_rows.values():
        rows.sort(key=_table_sort_key)
        for row in rows:
            row.pop("_seq", None)
    return table_rows, paper_context


def _load_caption_dv_lookup(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    assert_valid_payload("caption_dv_lookup", payload, strict=True)
    if isinstance(payload, dict):
        return payload
    return {}


def _resolve_artifact_path(primary_path: str, glob_patterns: list[str]) -> str | None:
    """Resolve artifact path, supporting alternate filenames from parallel agents."""
    primary = Path(primary_path)
    if primary.exists():
        return str(primary)

    candidates: list[Path] = []
    for pattern in glob_patterns:
        for raw in glob.glob(pattern):
            p = Path(raw)
            if p.exists() and p.is_file():
                candidates.append(p)
    if not candidates:
        return None
    # Prefer newest artifact.
    newest = max(candidates, key=lambda p: p.stat().st_mtime)
    return str(newest)


def _extract_caption_dv_raw(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        for key in ("dv", "dv_raw", "caption_dv", "outcome", "label"):
            raw = str(value.get(key) or "").strip()
            if raw:
                return raw
    if isinstance(value, list):
        for item in value:
            raw = _extract_caption_dv_raw(item)
            if raw:
                return raw
    return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int_any(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _lookup_dv_confidence(value: Any) -> float:
    if isinstance(value, dict):
        return _safe_float(value.get("confidence"), 0.0)
    return 0.0


def _resolve_lookup_entry_for_claim(
    claim: dict[str, Any],
    caption_lookup: dict[str, Any],
) -> tuple[Any | None, str | None]:
    table_id = str(claim.get("source_table_id") or "").strip()
    if table_id and table_id in caption_lookup:
        return caption_lookup.get(table_id), "table_id_exact"

    paper_id = str(claim.get("paper_id") or "").strip()
    page = _safe_int_any(claim.get("source_page"))
    if not paper_id:
        return None, None

    candidates: list[tuple[int, float, Any]] = []
    for rec in caption_lookup.values():
        if not isinstance(rec, dict):
            continue
        if str(rec.get("paper_id") or "").strip() != paper_id:
            continue
        rec_page = _safe_int_any(rec.get("source_page"))
        if page is None or rec_page is None:
            continue
        dist = abs(rec_page - page)
        if dist <= 1:
            candidates.append((dist, -_lookup_dv_confidence(rec), rec))
    if candidates:
        candidates.sort(key=lambda x: (x[0], x[1]))
        return candidates[0][2], "paper_page_near"

    # very conservative paper-level fallback: one unique high-confidence DV only
    paper_recs = [
        rec
        for rec in caption_lookup.values()
        if isinstance(rec, dict) and str(rec.get("paper_id") or "").strip() == paper_id
    ]
    dv_set = {str(rec.get("dv") or "").strip() for rec in paper_recs if str(rec.get("dv") or "").strip()}
    if len(dv_set) == 1 and paper_recs:
        best = max(paper_recs, key=_lookup_dv_confidence)
        if _lookup_dv_confidence(best) >= 0.85:
            return best, "paper_single_dv"
    return None, None


def _apply_caption_dv_override(
    claims: list[dict[str, Any]],
    caption_lookup: dict[str, Any],
    vocab: dict[str, Any],
) -> list[dict[str, Any]]:
    if not caption_lookup:
        return claims

    out: list[dict[str, Any]] = []
    for claim in claims:
        entry, match_mode = _resolve_lookup_entry_for_claim(claim, caption_lookup)
        if not entry:
            out.append(claim)
            continue

        raw_dv = _extract_caption_dv_raw(entry)
        if not raw_dv:
            out.append(claim)
            continue

        mapped_dv, conf = find_closest_dv(raw_dv, vocab)
        lookup_conf = _lookup_dv_confidence(entry)
        current_dv = str(claim.get("dv") or "").strip()
        current_conf = _safe_float(claim.get("dv_confidence"), 0.0)
        current_mapped = bool(claim.get("dv_mapped"))

        should_override = (
            match_mode == "table_id_exact"
            or
            not current_dv
            or not current_mapped
            or current_conf < 0.70
            or (lookup_conf >= 0.85 and mapped_dv and mapped_dv != current_dv and current_conf < 0.80)
        )
        if not should_override:
            out.append(claim)
            continue

        patched = dict(claim)
        patched["table_dv_original"] = claim.get("dv")
        patched["table_dv_original_raw"] = claim.get("dv_raw")
        patched["caption_dv_raw"] = raw_dv
        patched["dv_from_caption_lookup"] = True
        patched["dv_from_caption_lookup_mode"] = match_mode
        patched["caption_lookup_confidence"] = round(lookup_conf, 3)
        if mapped_dv and conf >= 0.65:
            patched["dv"] = mapped_dv
            patched["dv_raw"] = raw_dv
            patched["dv_mapped"] = True
            patched["dv_confidence"] = round(conf, 2)
        else:
            patched["dv"] = raw_dv
            patched["dv_raw"] = raw_dv
            patched["dv_mapped"] = False
            patched["dv_confidence"] = 0.0
        out.append(patched)
    return out


def _load_abstract_caption_claims(path: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    p = Path(path)
    if not p.exists():
        return [], []

    with p.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    assert_valid_payload("abstract_claims", payload, strict=True)

    claims: list[dict[str, Any]]
    if isinstance(payload, dict) and isinstance(payload.get("claims"), list):
        claims = [c for c in payload["claims"] if isinstance(c, dict)]
    elif isinstance(payload, list):
        claims = [c for c in payload if isinstance(c, dict)]
    else:
        return [], []

    abstracts: list[dict[str, Any]] = []
    captions: list[dict[str, Any]] = []

    for claim in claims:
        source_hint = " ".join(
            str(claim.get(k) or "")
            for k in ("source", "provenance", "extraction_method", "claim_id")
        ).lower()
        if "caption" in source_hint or "figure" in source_hint or "table_caption" in source_hint:
            c = dict(claim)
            c["claim_source"] = "caption"
            captions.append(c)
        else:
            c = dict(claim)
            c["claim_source"] = "abstract"
            abstracts.append(c)

    return abstracts, captions


def _claim_key(claim: dict[str, Any]) -> tuple[str, str, str]:
    return (
        _normalize_key_text(claim.get("paper_id")),
        _normalize_key_text(claim.get("iv") or claim.get("iv_raw")),
        _normalize_key_text(claim.get("dv") or claim.get("dv_raw")),
    )


def _claim_key_with_direction(claim: dict[str, Any]) -> tuple[str, str, str, str]:
    return (*_claim_key(claim), _normalize_key_text(claim.get("direction") or "unknown"))


def _enrich_claim_context(
    claims: list[dict[str, Any]],
    paper_type_map: dict[str, str],
    provenance_depth: str,
) -> list[dict[str, Any]]:
    """Attach paper-family and provenance depth metadata to claims."""
    out: list[dict[str, Any]] = []
    for claim in claims:
        c = dict(claim)
        pid = str(c.get("paper_id") or "").strip()
        family = _normalize_article_family(c.get("article_type_family"))
        if family == "unknown":
            family = _normalize_article_family(paper_type_map.get(pid))
        claim_type = _infer_claim_type(c, family)
        c["article_type_family"] = family
        c["claim_type"] = claim_type
        c.setdefault("rule_type", _CLAIM_TYPE_TO_RULE_TYPE.get(claim_type, "edge"))
        c["field_contract_family"] = get_family_contract(family).family
        c["field_targets"] = _field_targets_for_claim_type(claim_type, family)
        c.setdefault("provenance_depth", provenance_depth)
        out.append(c)
    return out


def _claim_evidence_score(claim: dict[str, Any]) -> float:
    direction = _normalize_key_text(claim.get("direction") or "unknown")
    score = 0.0
    if direction != "unknown":
        score += 3.0
    if claim.get("effect_size") is not None:
        score += 2.0
    if claim.get("p_value") is not None:
        score += 2.0
    if claim.get("is_significant") is True:
        score += 1.0
    score += _safe_float(claim.get("extraction_confidence"), 0.0)
    return score


def _collapse_intra_source_duplicates(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep one strongest claim per (paper, iv, dv, source)."""
    grouped: dict[tuple[str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        grouped[
            (
                _normalize_key_text(claim.get("paper_id")),
                _normalize_key_text(claim.get("iv") or claim.get("iv_raw")),
                _normalize_key_text(claim.get("dv") or claim.get("dv_raw")),
                _normalize_key_text(claim.get("claim_source")),
            )
        ].append(claim)

    out: list[dict[str, Any]] = []
    for items in grouped.values():
        if len(items) == 1:
            out.append(items[0])
            continue
        best = max(items, key=_claim_evidence_score)
        if len(items) > 1:
            merged = dict(best)
            merged["intra_source_variants"] = len(items)
            merged["intra_source_directions"] = sorted(
                {_normalize_key_text(i.get("direction") or "unknown") for i in items}
            )
            out.append(merged)
        else:
            out.append(best)
    return out


def _filter_low_signal_table_claims(
    claims: list[dict[str, Any]],
    min_unknown_confidence: float = 0.62,
) -> tuple[list[dict[str, Any]], int]:
    """Drop table claims that are likely OCR/header leakage."""
    kept: list[dict[str, Any]] = []
    dropped = 0
    for claim in claims:
        iv = str(claim.get("iv") or "").strip()
        dv = str(claim.get("dv") or "").strip()
        if not iv or not dv:
            dropped += 1
            continue
        if iv == dv:
            dropped += 1
            continue
        # If extractor didn't provide confidence, assume neutral quality.
        conf = _safe_float(claim.get("extraction_confidence"), 0.7)
        direction = _normalize_key_text(claim.get("direction") or "unknown")
        has_stats = (
            claim.get("effect_size") is not None
            or claim.get("p_value") is not None
            or claim.get("is_significant") is True
        )
        source_text = f"{claim.get('source_quote') or ''} {claim.get('context') or ''}"
        has_relation_signal = bool(_RELATION_SIGNAL_PATTERN.search(source_text))
        if conf < 0.45:
            dropped += 1
            continue
        if direction == "unknown" and not has_stats and not has_relation_signal and conf < min_unknown_confidence:
            dropped += 1
            continue
        kept.append(claim)
    return kept, dropped


def _backfill_unknown_direction_from_text(claims: list[dict[str, Any]]) -> int:
    """Infer missing direction from explicit lexical cues in quote/context."""
    updated = 0
    for claim in claims:
        direction = _normalize_key_text(claim.get("direction") or "unknown")
        if direction != "unknown":
            continue
        text = f"{claim.get('source_quote') or ''} {claim.get('context') or ''}"
        if not text.strip():
            continue
        if _NO_EFFECT_PATTERN.search(text):
            claim["direction"] = "no_effect"
            claim["direction_inferred_from"] = "text_lexical_no_effect"
            updated += 1
            continue
        inc = bool(_INCREASE_PATTERN.search(text))
        dec = bool(_DECREASE_PATTERN.search(text))
        if inc and not dec:
            claim["direction"] = "increase"
            claim["direction_inferred_from"] = "text_lexical_positive"
            updated += 1
        elif dec and not inc:
            claim["direction"] = "decrease"
            claim["direction_inferred_from"] = "text_lexical_negative"
            updated += 1
    return updated


def _infer_theory_candidates(claim: dict[str, Any]) -> list[tuple[str, float]]:
    text = " ".join(
        [
            str(claim.get("iv") or claim.get("iv_raw") or ""),
            str(claim.get("dv") or claim.get("dv_raw") or ""),
            str(claim.get("source_quote") or ""),
            str(claim.get("context") or ""),
            str(claim.get("claim_type") or ""),
        ]
    ).lower()
    iv = _normalize_key_text(claim.get("iv") or claim.get("iv_raw"))
    dv = _normalize_key_text(claim.get("dv") or claim.get("dv_raw"))

    scores: dict[str, float] = defaultdict(float)
    for theory, keywords in _THEORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                scores[theory] += 1.0

    if iv in _NATURE_IV_HINTS:
        scores["ART"] += 1.0
        scores["SRT"] += 1.0
        scores["Biophilia"] += 1.0
    if dv in _ART_DV_INCREASE or dv in _ART_DV_DECREASE:
        scores["ART"] += 1.0
    if dv in _SRT_DV_INCREASE or dv in _SRT_DV_DECREASE:
        scores["SRT"] += 1.0
    if dv in _BIOPHILIA_DV_INCREASE or dv in _BIOPHILIA_DV_DECREASE:
        scores["Biophilia"] += 1.0
    if dv in _PR_DV_INCREASE or dv in _PR_DV_DECREASE:
        scores["Prospect-Refuge"] += 1.0
    if any(token in iv for token in ("prospect", "refuge")):
        scores["Prospect-Refuge"] += 1.5

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return [(theory, score) for theory, score in ranked if score >= 2.0][:2]


def _expected_direction_by_theory(theory: str, dv: str) -> str | None:
    if theory == "ART":
        if dv in _ART_DV_INCREASE:
            return "increase"
        if dv in _ART_DV_DECREASE:
            return "decrease"
    elif theory == "SRT":
        if dv in _SRT_DV_INCREASE:
            return "increase"
        if dv in _SRT_DV_DECREASE:
            return "decrease"
    elif theory == "Biophilia":
        if dv in _BIOPHILIA_DV_INCREASE:
            return "increase"
        if dv in _BIOPHILIA_DV_DECREASE:
            return "decrease"
    elif theory == "Prospect-Refuge":
        if dv in _PR_DV_INCREASE:
            return "increase"
        if dv in _PR_DV_DECREASE:
            return "decrease"
    return None


def _annotate_theory_direction_tensions(claims: list[dict[str, Any]]) -> dict[str, int]:
    """Flag claims where observed direction conflicts with theory expectations."""
    annotated = 0
    tension_direction = 0
    tension_null = 0

    for claim in claims:
        direction = _normalize_key_text(claim.get("direction") or "unknown")
        dv = _normalize_key_text(claim.get("dv") or claim.get("dv_raw"))
        if not dv:
            continue

        candidates = _infer_theory_candidates(claim)
        if not candidates:
            continue
        annotated += 1
        claim["theory_candidates"] = [{"theory": t, "score": round(s, 2)} for t, s in candidates]

        expectations = []
        direction_conflicts = []
        null_conflicts = []
        for theory, score in candidates:
            expected = _expected_direction_by_theory(theory, dv)
            if not expected:
                continue
            expectations.append({"theory": theory, "expected_direction": expected, "score": round(score, 2)})
            if direction in {"increase", "decrease"} and direction != expected:
                direction_conflicts.append({"theory": theory, "expected_direction": expected, "observed_direction": direction})
            elif direction == "no_effect":
                null_conflicts.append({"theory": theory, "expected_direction": expected, "observed_direction": direction})

        if expectations:
            claim["theory_direction_expectations"] = expectations
        if direction_conflicts:
            claim["theory_direction_tension"] = True
            claim["theory_direction_conflicts"] = direction_conflicts
            tension_direction += 1
        else:
            claim["theory_direction_tension"] = False
        if null_conflicts:
            claim["theory_null_tension"] = True
            claim["theory_null_conflicts"] = null_conflicts
            tension_null += 1
        else:
            claim["theory_null_tension"] = False

    return {
        "theory_annotated_claims": annotated,
        "theory_direction_tension_claims": tension_direction,
        "theory_null_tension_claims": tension_null,
    }


def _refresh_theory_direction_tensions(claims: list[dict[str, Any]]) -> dict[str, int]:
    for claim in claims:
        for field in _DIRECTION_FIELDS_TO_CLEAR:
            claim.pop(field, None)
    return _annotate_theory_direction_tensions(claims)


def _load_direction_overrides(path: str | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    payload = json.loads(p.read_text(encoding="utf-8"))

    out: dict[str, dict[str, Any]] = {}
    items: list[dict[str, Any]] = []
    if isinstance(payload, dict) and isinstance(payload.get("overrides"), list):
        items = [x for x in payload["overrides"] if isinstance(x, dict)]
    elif isinstance(payload, list):
        items = [x for x in payload if isinstance(x, dict)]
    elif isinstance(payload, dict):
        for claim_id, rec in payload.items():
            if isinstance(rec, dict):
                item = dict(rec)
                item.setdefault("claim_id", claim_id)
                items.append(item)

    for item in items:
        claim_id = str(item.get("claim_id") or "").strip()
        direction = _normalize_key_text(item.get("direction"))
        status = _normalize_key_text(item.get("status") or "approved")
        if not claim_id:
            continue
        if direction not in _ALLOWED_DIRECTIONS:
            continue
        if status in {"reject", "rejected", "skip"}:
            continue
        out[claim_id] = item
    return out


def _apply_direction_overrides(
    claims: list[dict[str, Any]],
    overrides: dict[str, dict[str, Any]],
) -> int:
    if not overrides:
        return 0
    updated = 0
    for claim in claims:
        claim_id = str(claim.get("claim_id") or "").strip()
        if not claim_id or claim_id not in overrides:
            continue
        override = overrides[claim_id]
        new_direction = _normalize_key_text(override.get("direction"))
        if new_direction not in _ALLOWED_DIRECTIONS:
            continue
        old_direction = _normalize_key_text(claim.get("direction") or "unknown")
        if old_direction == new_direction:
            continue
        claim["direction_original"] = old_direction
        claim["direction"] = new_direction
        claim["direction_override_applied"] = True
        claim["direction_override_reviewer"] = override.get("reviewer")
        claim["direction_override_rationale"] = override.get("rationale")
        claim["direction_override_timestamp"] = override.get("updated_at")
        updated += 1
    return updated


def _direction_from_signed_stats(claim: dict[str, Any]) -> str | None:
    for key in ("beta", "r", "t_value", "cohens_d", "effect_size"):
        value = _safe_float_or_none(claim.get(key))
        if value is None:
            continue
        if value > 0:
            return "increase"
        if value < 0:
            return "decrease"
    return None


def _compute_direction_confidence(claim: dict[str, Any]) -> tuple[float, list[str]]:
    direction = _normalize_key_text(claim.get("direction") or "unknown")
    source_text = f"{claim.get('source_quote') or ''} {claim.get('context') or ''}"
    evidence: list[str] = []
    if direction == "unknown":
        return 0.0, ["direction_unknown"]

    conf = 0.2
    extraction_conf = _safe_float(claim.get("extraction_confidence"), 0.0)
    if extraction_conf >= 0.8:
        conf += 0.2
        evidence.append("high_extraction_confidence")
    elif extraction_conf >= 0.65:
        conf += 0.1
        evidence.append("mid_extraction_confidence")

    stat_dir = _direction_from_signed_stats(claim)
    if direction in {"increase", "decrease"} and stat_dir == direction:
        conf += 0.4
        evidence.append("stat_sign_aligned")
    elif direction in {"increase", "decrease"} and stat_dir and stat_dir != direction:
        conf -= 0.35
        evidence.append("stat_sign_conflict")

    if direction == "no_effect":
        p = _safe_float_or_none(claim.get("p_value"))
        if p is not None and p >= 0.05:
            conf += 0.45
            evidence.append("p_value_non_significant")
        if claim.get("is_significant") is False:
            conf += 0.35
            evidence.append("is_significant_false")
        if _NO_EFFECT_PATTERN.search(source_text):
            conf += 0.25
            evidence.append("explicit_no_effect_language")
    else:
        inc = bool(_INCREASE_PATTERN.search(source_text))
        dec = bool(_DECREASE_PATTERN.search(source_text))
        if direction == "increase" and inc and not dec:
            conf += 0.25
            evidence.append("lexical_positive_alignment")
        elif direction == "decrease" and dec and not inc:
            conf += 0.25
            evidence.append("lexical_negative_alignment")
        elif inc and dec:
            conf -= 0.2
            evidence.append("mixed_polarity_language")

        p = _safe_float_or_none(claim.get("p_value"))
        if p is not None and p < 0.05:
            conf += 0.2
            evidence.append("p_value_significant")
        if claim.get("is_significant") is True:
            conf += 0.15
            evidence.append("is_significant_true")

    if claim.get("theory_direction_tension"):
        conf -= 0.35
        evidence.append("theory_direction_tension_penalty")
    if claim.get("theory_null_tension"):
        conf -= 0.25
        evidence.append("theory_null_tension_penalty")

    return max(0.0, min(1.0, conf)), evidence


def _apply_direction_mode(
    claims: list[dict[str, Any]],
    mode: str = "default",
    hard_threshold: float = 0.8,
) -> int:
    """Attach direction confidence and optionally demote weak directions."""
    demoted = 0
    for claim in claims:
        conf, evidence = _compute_direction_confidence(claim)
        claim["direction_confidence"] = round(conf, 3)
        claim["direction_evidence"] = evidence
        direction = _normalize_key_text(claim.get("direction") or "unknown")
        if mode != "hard":
            continue
        if direction in {"increase", "decrease", "no_effect"} and conf < hard_threshold:
            claim["direction_original"] = direction
            claim["direction"] = "unknown"
            claim["direction_demoted_reason"] = "hard_direction_mode_low_confidence"
            demoted += 1
    return demoted


def _build_resolution_questions(item: dict[str, Any]) -> dict[str, str]:
    iv = item.get("iv") or item.get("iv_raw") or "IV"
    dv = item.get("dv") or item.get("dv_raw") or "DV"
    observed = item.get("direction") or "unknown"
    paper = item.get("paper_id") or "unknown_paper"
    quote = (item.get("source_quote") or "").strip()
    quote_snip = quote[:260] + ("..." if len(quote) > 260 else "")
    return {
        "hitl_question": (
            f"For {paper}, does the evidence support `{iv} -> {dv}` as {observed}, "
            "or should direction be increase/decrease/no_effect/unknown?"
        ),
        "rag_query": (
            f"{paper} abstract introduction methods results discussion conclusion "
            f"{iv} {dv} direction effect "
            "increase decrease no significant effect"
        ),
        "llm_prompt": (
            "Classify the claim direction using the strongest available evidence. "
            "Do not assume the observed direction is correct. "
            "Use any relevant evidence you can retrieve from the paper and credible secondary sources. "
            "Return one label: increase/decrease/no_effect/unknown. "
            "Provide short justification with source URL(s) and quote evidence. "
            f"Claim: {iv} -> {dv}, observed={observed}. Candidate evidence snippet: {quote_snip}"
        ),
        "web_verification_instruction": (
            "Use retrieval/web search across full-paper evidence and credible external summaries. "
            "Return direction only when supported by URL + quote evidence; otherwise return unknown."
        ),
    }


def _write_direction_adjudication_packets(
    claims: list[dict[str, Any]],
    queue_path: str | None,
    questions_path: str | None,
    overrides_template_path: str | None,
) -> dict[str, Any]:
    tension_items = []
    for claim in claims:
        if not claim.get("theory_direction_tension") and not claim.get("theory_null_tension"):
            continue
        item = {
            "claim_id": claim.get("claim_id"),
            "paper_id": claim.get("paper_id"),
            "claim_source": claim.get("claim_source"),
            "iv": claim.get("iv"),
            "dv": claim.get("dv"),
            "direction": claim.get("direction"),
            "direction_confidence": claim.get("direction_confidence"),
            "theory_candidates": claim.get("theory_candidates", []),
            "theory_direction_conflicts": claim.get("theory_direction_conflicts", []),
            "theory_null_conflicts": claim.get("theory_null_conflicts", []),
            "source_quote": (claim.get("source_quote") or "")[:500],
            "questions": _build_resolution_questions(claim),
        }
        tension_items.append(item)

    written = {"queue_path": None, "questions_path": None, "overrides_template_path": None}
    if queue_path:
        qp = Path(queue_path)
        qp.parent.mkdir(parents=True, exist_ok=True)
        qp.write_text(
            json.dumps({"count": len(tension_items), "items": tension_items}, indent=2),
            encoding="utf-8",
        )
        written["queue_path"] = str(qp)

    if questions_path:
        qsp = Path(questions_path)
        qsp.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Direction Adjudication Questions",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            f"Tension claims: {len(tension_items)}",
            "",
        ]
        for idx, item in enumerate(tension_items, start=1):
            lines.append(f"## Q{idx}: {item.get('claim_id')}")
            lines.append(f"- Paper: `{item.get('paper_id')}`")
            lines.append(f"- Claim: `{item.get('iv')} -> {item.get('dv')}`")
            lines.append(f"- Observed direction: `{item.get('direction')}`")
            lines.append(f"- HITL: {item['questions']['hitl_question']}")
            lines.append(f"- RAG query: `{item['questions']['rag_query']}`")
            lines.append(f"- LLM prompt: {item['questions']['llm_prompt']}")
            lines.append(f"- Evidence snippet: {item.get('source_quote')}")
            lines.append("")
        qsp.write_text("\n".join(lines), encoding="utf-8")
        written["questions_path"] = str(qsp)

    if overrides_template_path:
        op = Path(overrides_template_path)
        op.parent.mkdir(parents=True, exist_ok=True)
        overrides = {
            "overrides": [
                {
                    "claim_id": item.get("claim_id"),
                    "direction": "unknown",
                    "status": "pending",
                    "reviewer": "",
                    "rationale": "",
                    "evidence_url": "",
                    "evidence_quote": "",
                    "updated_at": "",
                }
                for item in tension_items
            ]
        }
        op.write_text(json.dumps(overrides, indent=2), encoding="utf-8")
        written["overrides_template_path"] = str(op)

    return {
        "tension_items": len(tension_items),
        **written,
    }


def _merge_claim_sources(
    table_claims: list[dict[str, Any]],
    abstract_claims: list[dict[str, Any]],
    caption_claims: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    for c in table_claims:
        c["claim_source"] = "table"
    all_claims = [*table_claims, *abstract_claims, *caption_claims]
    all_claims = _collapse_intra_source_duplicates(all_claims)

    groups_by_pair: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for claim in all_claims:
        groups_by_pair[_claim_key(claim)].append(claim)

    corroborated_pairs = 0
    conflict_pairs = 0

    for pair_key, claims in groups_by_pair.items():
        source_set = {c.get("claim_source", "unknown") for c in claims}
        dirs = {_normalize_key_text(c.get("direction") or "unknown") for c in claims}
        known_dirs = {d for d in dirs if d and d != "unknown"}

        # If one source resolves direction and others are unknown, backfill unknowns.
        if len(known_dirs) == 1 and "unknown" in dirs:
            inferred = next(iter(known_dirs))
            for claim in claims:
                if _normalize_key_text(claim.get("direction") or "unknown") == "unknown":
                    claim["direction"] = inferred
                    claim["direction_inferred_from"] = "cross_source_pair_consensus"

        table_effect = next((c.get("effect_size") for c in claims if c.get("claim_source") == "table" and c.get("effect_size") is not None), None)
        abstract_context = next((c.get("context") for c in claims if c.get("claim_source") == "abstract" and c.get("context")), None)
        if abstract_context is None:
            abstract_context = next((c.get("context") for c in claims if c.get("claim_source") == "caption" and c.get("context")), None)

        # Conflict means multiple non-unknown directions disagree.
        if len(known_dirs) > 1:
            conflict_pairs += 1
            for claim in claims:
                claim["corroboration_status"] = "conflict"
                claim["corroboration_sources"] = sorted(source_set)
                claim["conflict_on_pair"] = {
                    "paper_id": pair_key[0],
                    "iv": pair_key[1],
                    "dv": pair_key[2],
                }
                if table_effect is not None and claim.get("effect_size") is None:
                    claim["effect_size_preferred_table"] = table_effect
                if abstract_context and not claim.get("context"):
                    claim["context_preferred_abstract"] = abstract_context
            continue

        if len(source_set) >= 2:
            corroborated_pairs += 1
            for claim in claims:
                claim["corroboration_status"] = "corroborated"
                claim["corroboration_sources"] = sorted(source_set)
                if table_effect is not None and claim.get("effect_size") is None:
                    claim["effect_size_preferred_table"] = table_effect
                if abstract_context and not claim.get("context"):
                    claim["context_preferred_abstract"] = abstract_context
        else:
            for claim in claims:
                claim["corroboration_status"] = "unique"
                claim["corroboration_sources"] = sorted(source_set)

    # Deduplicate identical claims across same source
    deduped: list[dict[str, Any]] = []
    seen = set()
    for claim in all_claims:
        dkey = (_claim_key_with_direction(claim), claim.get("claim_source"))
        if dkey in seen:
            continue
        seen.add(dkey)
        deduped.append(claim)

    direction_backfilled = _backfill_unknown_direction_from_text(deduped)
    theory_stats = _annotate_theory_direction_tensions(deduped)

    summary = {
        "total_claims": len(deduped),
        "from_abstracts": sum(1 for c in deduped if c.get("claim_source") == "abstract"),
        "from_captions": sum(1 for c in deduped if c.get("claim_source") == "caption"),
        "from_tables": sum(1 for c in deduped if c.get("claim_source") == "table"),
        "corroborated": sum(1 for c in deduped if c.get("corroboration_status") == "corroborated"),
        "conflicts": sum(1 for c in deduped if c.get("corroboration_status") == "conflict"),
        "corroborated_pairs": corroborated_pairs,
        "conflict_pairs": conflict_pairs,
        "direction_backfilled_from_text": direction_backfilled,
        **theory_stats,
    }
    return deduped, summary


def run_batch_extraction(
    csv_path: str = "data/production/realtime_pdf_confirmed_rows.csv",
    triage_path: str = "data/production/paper_triage.json",
    table_class_path: str = "data/production/table_classifications.json",
    vocabulary_path: str = "data/vocabulary/variable_vocabulary.json",
    abstract_claims_path: str = "data/production/abstract_claims.json",
    caption_dv_lookup_path: str = "data/production/caption_dv_lookup.json",
    output_path: str = "data/production/structured_claims.json",
    method: str = "enhanced",
    limit: int | None = None,
    strict_d14: bool = False,
    strict_contracts: bool = True,
    direction_mode: str = "default",
    direction_hard_threshold: float = 0.8,
    direction_overrides_path: str | None = "data/review/direction_overrides.json",
    tension_queue_path: str | None = "data/review/theory_direction_tension_queue.json",
    tension_questions_path: str | None = "docs/HITL_LLM_RAG_direction_questions.md",
    overrides_template_path: str | None = "data/review/direction_overrides.template.json",
) -> dict[str, Any]:
    """D.15 pipeline: table extraction + abstract/caption integration."""
    triage = _load_triage(triage_path)
    eligible_papers = [
        paper_id
        for paper_id, rec in triage.items()
        if _normalize_key_text(rec.get("type")) in EXTRACTABLE_PAPER_TYPES
    ]
    if limit is not None:
        eligible_papers = eligible_papers[:limit]
    eligible_set = set(eligible_papers)

    table_classes = _load_table_classifications(table_class_path)
    extractable_tables = {
        table_id: rec
        for table_id, rec in table_classes.items()
        if _normalize_key_text(rec.get("paper_id")) in eligible_set and _is_table_extractable(rec)
    }
    extractable_table_ids = set(extractable_tables.keys())

    table_rows, csv_context = _load_rows_from_csv(
        csv_path=csv_path,
        allowed_papers=eligible_set,
        allowed_tables=extractable_table_ids,
    )
    warnings: list[str] = []

    resolved_abstract_path = _resolve_artifact_path(
        abstract_claims_path,
        glob_patterns=[
            "data/production/abstract_claims*.json",
            "data/production/*abstract*claims*.json",
        ],
    )
    resolved_caption_lookup_path = _resolve_artifact_path(
        caption_dv_lookup_path,
        glob_patterns=[
            "data/production/caption_dv_lookup*.json",
            "data/production/*caption*lookup*.json",
            "data/production/*caption*dv*.json",
        ],
    )

    if not resolved_abstract_path:
        warnings.append("D.14 abstract claims artifact missing; merge will be table-only.")
        if strict_d14:
            raise FileNotFoundError(
                "D.14 dependency missing: expected abstract claims JSON (e.g., data/production/abstract_claims.json)."
            )
    if not resolved_caption_lookup_path:
        warnings.append("D.14 caption DV lookup missing; table DV override disabled.")
        if strict_d14:
            raise FileNotFoundError(
                "D.14 dependency missing: expected caption DV lookup JSON (e.g., data/production/caption_dv_lookup.json)."
            )

    caption_lookup = _load_caption_dv_lookup(resolved_caption_lookup_path) if resolved_caption_lookup_path else {}
    vocab = load_vocabulary(vocabulary_path)

    tables_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for table_id, rec in extractable_tables.items():
        paper_id = str(rec.get("paper_id") or "").strip()
        table_payload = {
            "table_id": table_id,
            "paper_id": paper_id,
            "page": rec.get("page"),
            "type": rec.get("type"),
            "sample_content": rec.get("sample_content") or "",
            "rows": table_rows.get(table_id, []),
        }
        # pass caption DV into extraction context as an extra hint
        raw_dv = _extract_caption_dv_raw(caption_lookup.get(table_id))
        if raw_dv:
            table_payload["caption_dv"] = raw_dv
        tables_by_paper[paper_id].append(table_payload)

    table_claims: list[dict[str, Any]] = []
    papers_processed = 0
    for paper_id in eligible_papers:
        paper_tables = tables_by_paper.get(paper_id, [])
        if not paper_tables:
            continue
        paper_info = triage.get(paper_id, {})
        context = {
            "title": paper_info.get("title") or csv_context.get(paper_id, {}).get("title"),
            "abstract": paper_info.get("abstract") or csv_context.get(paper_id, {}).get("abstract"),
            "article_type_family": _coalesce_article_family(
                paper_info.get("article_type_family"),
                paper_info.get("type"),
            ),
            "article_type": (
                csv_context.get(paper_id, {}).get("article_type")
                or _coalesce_article_family(
                    paper_info.get("article_type_family"),
                    paper_info.get("type"),
                )
                or paper_info.get("type")
            ),
        }
        claims = extract_claims_from_paper(
            paper_id=paper_id,
            tables=paper_tables,
            paper_context=context,
            vocabulary=vocab,
            method=method,
        )
        claims = _apply_caption_dv_override(claims, caption_lookup, vocab)
        table_claims.extend(claims)
        papers_processed += 1

    table_claims, dropped_low_signal = _filter_low_signal_table_claims(table_claims)

    abstract_claims, caption_claims = (
        _load_abstract_caption_claims(resolved_abstract_path) if resolved_abstract_path else ([], [])
    )
    paper_type_map = {
        str(pid): _coalesce_article_family(
            info.get("article_type_family"),
            info.get("type"),
        )
        for pid, info in triage.items()
    }
    table_claims = _enrich_claim_context(table_claims, paper_type_map, provenance_depth="table")
    abstract_claims = _enrich_claim_context(abstract_claims, paper_type_map, provenance_depth="abstract")
    caption_claims = _enrich_claim_context(caption_claims, paper_type_map, provenance_depth="caption")
    merged_claims, merge_summary = _merge_claim_sources(table_claims, abstract_claims, caption_claims)
    overrides = _load_direction_overrides(direction_overrides_path)
    overrides_applied = _apply_direction_overrides(merged_claims, overrides)
    theory_stats = _refresh_theory_direction_tensions(merged_claims)
    demoted_hard_mode = _apply_direction_mode(
        merged_claims,
        mode=direction_mode,
        hard_threshold=direction_hard_threshold,
    )
    if demoted_hard_mode:
        theory_stats = _refresh_theory_direction_tensions(merged_claims)
    packet_stats = _write_direction_adjudication_packets(
        merged_claims,
        queue_path=tension_queue_path,
        questions_path=tension_questions_path,
        overrides_template_path=overrides_template_path,
    )
    merge_summary.update(theory_stats)
    merge_summary["direction_overrides_applied"] = overrides_applied
    merge_summary["direction_demoted_hard_mode"] = demoted_hard_mode
    merge_summary["direction_mode"] = direction_mode
    merge_summary["direction_hard_threshold"] = round(direction_hard_threshold, 3)

    summary = {
        "extraction_date": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "papers_eligible": len(eligible_papers),
        "papers_processed": papers_processed,
        "tables_extractable": len(extractable_tables),
        "resolved_paths": {
            "abstract_claims_path": resolved_abstract_path,
            "caption_dv_lookup_path": resolved_caption_lookup_path,
        },
        "caption_lookup_entries": len(caption_lookup),
        "caption_lookup_used": sum(1 for c in table_claims if c.get("dv_from_caption_lookup")),
        "table_claims_after_filter": len(table_claims),
        "table_claims_dropped_low_signal": dropped_low_signal,
        "direction_overrides_path": direction_overrides_path,
        "direction_mode": direction_mode,
        "direction_hard_threshold": direction_hard_threshold,
        "direction_adjudication_packets": packet_stats,
        "warnings": warnings,
        "claims": merged_claims,
        "summary": merge_summary,
        "counts_by_direction": dict(Counter(_normalize_key_text(c.get("direction") or "unknown") for c in merged_claims)),
    }
    assert_valid_payload("structured_claims", summary, strict=strict_contracts)

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Sprint D.15 merged extraction pipeline.")
    parser.add_argument("--csv-path", default="data/production/realtime_pdf_confirmed_rows.csv")
    parser.add_argument("--triage-path", default="data/production/paper_triage.json")
    parser.add_argument("--table-class-path", default="data/production/table_classifications.json")
    parser.add_argument("--vocabulary-path", default="data/vocabulary/variable_vocabulary.json")
    parser.add_argument("--abstract-claims-path", default="data/production/abstract_claims.json")
    parser.add_argument("--caption-dv-lookup-path", default="data/production/caption_dv_lookup.json")
    parser.add_argument("--output-path", default="data/production/structured_claims.json")
    parser.add_argument("--method", choices=["enhanced", "rule_based", "llm"], default="enhanced")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--strict-d14", action="store_true", help="Fail if D.14 artifacts are missing.")
    parser.add_argument("--no-strict-contracts", action="store_true")
    parser.add_argument("--direction-mode", choices=["default", "hard"], default="default")
    parser.add_argument("--direction-hard-threshold", type=float, default=0.8)
    parser.add_argument("--direction-overrides-path", default="data/review/direction_overrides.json")
    parser.add_argument("--no-direction-overrides", action="store_true")
    parser.add_argument("--tension-queue-path", default="data/review/theory_direction_tension_queue.json")
    parser.add_argument("--tension-questions-path", default="docs/HITL_LLM_RAG_direction_questions.md")
    parser.add_argument("--overrides-template-path", default="data/review/direction_overrides.template.json")
    parser.add_argument("--no-adjudication-packets", action="store_true")
    args = parser.parse_args()

    direction_overrides_path = None if args.no_direction_overrides else args.direction_overrides_path
    if args.no_adjudication_packets:
        tension_queue_path = None
        tension_questions_path = None
        overrides_template_path = None
    else:
        tension_queue_path = args.tension_queue_path
        tension_questions_path = args.tension_questions_path
        overrides_template_path = args.overrides_template_path

    result = run_batch_extraction(
        csv_path=args.csv_path,
        triage_path=args.triage_path,
        table_class_path=args.table_class_path,
        vocabulary_path=args.vocabulary_path,
        abstract_claims_path=args.abstract_claims_path,
        caption_dv_lookup_path=args.caption_dv_lookup_path,
        output_path=args.output_path,
        method=args.method,
        limit=args.limit,
        strict_d14=args.strict_d14,
        strict_contracts=not args.no_strict_contracts,
        direction_mode=args.direction_mode,
        direction_hard_threshold=args.direction_hard_threshold,
        direction_overrides_path=direction_overrides_path,
        tension_queue_path=tension_queue_path,
        tension_questions_path=tension_questions_path,
        overrides_template_path=overrides_template_path,
    )
    print(json.dumps({k: v for k, v in result.items() if k != "claims"}, indent=2))


if __name__ == "__main__":
    main()
