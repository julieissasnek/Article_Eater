"""Field-level evidence risk scoring for extracted claims.

Goal:
- Preserve high-recall extraction outputs.
- Quantify likely inaccuracy risk per field and per claim.
- Provide transparent reasons so filtering can be policy-based, not hard-coded.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from src.extraction.direction_expectation import direction_expected_for_claim

_PLACEHOLDER_RE = re.compile(r"\b(col(?:umn)?[_\s-]*\d+|row[_\s-]*\d+|cell[_\s-]*\d+|var[_\s-]*\d+|x\d+|y\d+)\b", re.IGNORECASE)
_LONG_TOKEN_RE = re.compile(r"\b[^\s]{40,}\b")
_TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class FieldRisk:
    score: float
    reasons: list[str]


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.lower()) if len(t) >= 3}


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = _norm(value).replace(",", "").replace("−", "-")
    m = re.search(r"[-+]?\d*\.?\d+", text)
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def _norm_direction(value: Any) -> str:
    s = _norm(value).lower()
    if s in {"increase", "increased", "higher", "up", "positive", "facilitates", "improves"}:
        return "increase"
    if s in {"decrease", "decreased", "lower", "down", "negative", "reduces", "impairs"}:
        return "decrease"
    if s in {"no_effect", "null", "none", "non_significant", "non-significant"}:
        return "no_effect"
    return "unknown"


def _infer_direction_from_text(text: str) -> str:
    t = text.lower()
    no_eff = bool(
        re.search(
            r"\b(no significant|not significant|non-significant|nonsignificant|ns\b|p\s*[>=]\s*0?\.0?5)\b",
            t,
        )
    )
    inc = bool(re.search(r"\b(increase|increased|higher|greater|improv|enhanc|positive association)\b", t))
    dec = bool(re.search(r"\b(decrease|decreased|lower|reduc|diminish|worse|negative association)\b", t))
    if no_eff and not inc and not dec:
        return "no_effect"
    if inc and not dec:
        return "increase"
    if dec and not inc:
        return "decrease"
    return "unknown"


def _infer_direction_from_signed_stats(text: str) -> str:
    pat = re.compile(r"(?:β|beta|r|rho|ρ|d|t)\s*=?\s*([+-]\d*\.?\d+)", re.IGNORECASE)
    matches = pat.findall(text)
    if not matches:
        return "unknown"
    pos = 0
    neg = 0
    for m in matches:
        try:
            v = float(m)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Skipped: {e}")
            continue
        if v > 0:
            pos += 1
        elif v < 0:
            neg += 1
    if pos > 0 and neg == 0:
        return "increase"
    if neg > 0 and pos == 0:
        return "decrease"
    return "unknown"


def _section_risk(section: str) -> float:
    s = _norm(section).lower()
    if s in {"results", "table"}:
        return 0.05
    if s in {"abstract"}:
        return 0.12
    if s in {"figure_caption", "caption"}:
        return 0.18
    if s in {"discussion", "conclusion"}:
        return 0.22
    if s in {"introduction", "background"}:
        return 0.26
    if s in {"methods"}:
        return 0.30
    return 0.20


def _support_type_risk(support_type: str) -> float:
    s = _norm(support_type).lower()
    if s == "explicit":
        return 0.0
    if s == "derived":
        return 0.12
    if s == "inferred":
        return 0.24
    return 0.10


def _field_from_packet(claim: dict[str, Any], field: str) -> dict[str, Any]:
    packet = claim.get("field_evidence")
    if isinstance(packet, dict):
        rec = packet.get(field)
        if isinstance(rec, dict):
            return rec
    return {}


def _raw_text_noise_penalty(text: str, reasons: list[str]) -> float:
    penalty = 0.0
    if _PLACEHOLDER_RE.search(text):
        penalty += 0.25
        reasons.append("placeholder_token")
    if _LONG_TOKEN_RE.search(text):
        penalty += 0.16
        reasons.append("ocr_long_token")
    return penalty


def _score_iv_or_dv(claim: dict[str, Any], field: str) -> FieldRisk:
    reasons: list[str] = []
    score = 0.05
    value = _norm(claim.get(field))
    raw = _norm(claim.get(f"{field}_raw"))
    packet = _field_from_packet(claim, field)
    if not value:
        score += 0.42
        reasons.append("missing_value")
    if not raw:
        score += 0.24
        reasons.append("missing_raw_text")
    score += _raw_text_noise_penalty(raw, reasons)
    if packet:
        if not _norm(packet.get("evidence_quote")):
            score += 0.14
            reasons.append("packet_missing_evidence_quote")
        score += _support_type_risk(_norm(packet.get("support_type")))
    return FieldRisk(score=_clamp(score), reasons=sorted(set(reasons)))


def _score_direction(claim: dict[str, Any]) -> FieldRisk:
    reasons: list[str] = []
    score = 0.08
    direction = _norm_direction(claim.get("direction"))
    quote = _norm(claim.get("evidence_quote") or claim.get("source_quote"))
    section = _norm(claim.get("section"))
    packet = _field_from_packet(claim, "direction")
    expected, expected_reason = direction_expected_for_claim(claim)

    if direction == "unknown" and expected:
        score += 0.36
        reasons.append("unknown_direction")
    if direction == "unknown" and not expected:
        reasons.append(f"unknown_direction_not_required:{expected_reason}")
    if not quote:
        score += 0.25
        reasons.append("missing_evidence_quote")
    else:
        if len(quote) < 24:
            score += 0.12
            reasons.append("short_evidence_quote")
        lex_dir = _infer_direction_from_text(quote)
        signed_dir = _infer_direction_from_signed_stats(quote)
        if direction in {"increase", "decrease"} and lex_dir in {"increase", "decrease"} and lex_dir != direction:
            score += 0.22
            reasons.append("lexical_direction_conflict")
        if direction in {"increase", "decrease"} and signed_dir in {"increase", "decrease"} and signed_dir != direction:
            score += 0.22
            reasons.append("signed_stat_direction_conflict")
        if direction == "no_effect" and lex_dir in {"increase", "decrease"}:
            score += 0.18
            reasons.append("no_effect_but_directional_lexical_cue")

    p = _as_float(claim.get("p_value"))
    if p is not None:
        if p < 0.0 or p > 1.0:
            score += 0.35
            reasons.append("invalid_p_value")
        if p < 0.05 and direction == "no_effect":
            score += 0.20
            reasons.append("significant_but_no_effect_direction")
    score += _section_risk(section) * 0.5

    if packet:
        score += _support_type_risk(_norm(packet.get("support_type")))
        alts = packet.get("alt_interpretations")
        if isinstance(alts, list) and alts:
            score += min(0.16, 0.04 * len(alts))
            reasons.append("packet_multiple_alt_interpretations")
    return FieldRisk(score=_clamp(score), reasons=sorted(set(reasons)))


def _score_effect_size(claim: dict[str, Any]) -> FieldRisk:
    reasons: list[str] = []
    score = 0.06
    es = claim.get("effect_size")
    es_type = _norm(claim.get("effect_size_type")).lower()
    if es is None:
        score += 0.18
        reasons.append("missing_effect_size")
    else:
        if _as_float(es) is None:
            score += 0.28
            reasons.append("non_numeric_effect_size")
        if not es_type:
            score += 0.10
            reasons.append("missing_effect_size_type")
    return FieldRisk(score=_clamp(score), reasons=sorted(set(reasons)))


def _score_p_value(claim: dict[str, Any]) -> FieldRisk:
    reasons: list[str] = []
    score = 0.06
    p = _as_float(claim.get("p_value"))
    if p is None:
        score += 0.20
        reasons.append("missing_p_value")
    else:
        if p < 0.0 or p > 1.0:
            score += 0.45
            reasons.append("invalid_p_value")
    return FieldRisk(score=_clamp(score), reasons=sorted(set(reasons)))


def _score_evidence_grounding(claim: dict[str, Any]) -> FieldRisk:
    reasons: list[str] = []
    score = 0.08
    quote = _norm(claim.get("evidence_quote") or claim.get("source_quote"))
    section = _norm(claim.get("section"))
    if not quote:
        score += 0.42
        reasons.append("missing_quote")
    else:
        if len(quote) < 24:
            score += 0.14
            reasons.append("quote_too_short")
        iv_toks = _tokens(_norm(claim.get("iv") or claim.get("iv_raw")))
        dv_toks = _tokens(_norm(claim.get("dv") or claim.get("dv_raw")))
        q_toks = _tokens(quote)
        if iv_toks and not iv_toks.intersection(q_toks):
            score += 0.10
            reasons.append("iv_not_in_quote")
        if dv_toks and not dv_toks.intersection(q_toks):
            score += 0.10
            reasons.append("dv_not_in_quote")
    score += _section_risk(section)
    prov = _norm(claim.get("provenance_depth")).lower()
    if prov == "abstract":
        score += 0.10
        reasons.append("abstract_only_provenance")
    elif prov == "table":
        score += 0.04
    elif not prov:
        score += 0.08
        reasons.append("missing_provenance_depth")
    return FieldRisk(score=_clamp(score), reasons=sorted(set(reasons)))


def score_claim_risk(claim: dict[str, Any]) -> dict[str, Any]:
    """Return risk annotations for one claim.

    Output keys:
    - field_risk_scores: dict[field -> 0..1]
    - field_risk_reasons: dict[field -> list[str]]
    - claim_risk_score: 0..1
    - claim_risk_tier: low|medium|high
    - claim_risk_reasons: top aggregated reasons
    """
    iv = _score_iv_or_dv(claim, "iv")
    dv = _score_iv_or_dv(claim, "dv")
    direction = _score_direction(claim)
    effect_size = _score_effect_size(claim)
    p_value = _score_p_value(claim)
    grounding = _score_evidence_grounding(claim)

    scores = {
        "iv": iv.score,
        "dv": dv.score,
        "direction": direction.score,
        "effect_size": effect_size.score,
        "p_value": p_value.score,
        "evidence_grounding": grounding.score,
    }
    reasons = {
        "iv": iv.reasons,
        "dv": dv.reasons,
        "direction": direction.reasons,
        "effect_size": effect_size.reasons,
        "p_value": p_value.reasons,
        "evidence_grounding": grounding.reasons,
    }
    weights = {
        "iv": 0.19,
        "dv": 0.19,
        "direction": 0.27,
        "effect_size": 0.10,
        "p_value": 0.10,
        "evidence_grounding": 0.15,
    }
    total = 0.0
    for k, w in weights.items():
        total += scores[k] * w

    iv_raw = _norm(claim.get("iv_raw")).lower()
    dv_raw = _norm(claim.get("dv_raw")).lower()
    global_reasons: list[str] = []
    if iv_raw and dv_raw and iv_raw == dv_raw:
        total += 0.20
        global_reasons.append("iv_raw_equals_dv_raw")
    if _PLACEHOLDER_RE.search(iv_raw) or _PLACEHOLDER_RE.search(dv_raw):
        total += 0.16
        global_reasons.append("placeholder_raw_variable")
    if _LONG_TOKEN_RE.search(f"{iv_raw} {dv_raw}"):
        total += 0.12
        global_reasons.append("ocr_raw_variable_noise")

    claim_risk = _clamp(total)
    if claim_risk >= 0.70:
        tier = "high"
    elif claim_risk >= 0.45:
        tier = "medium"
    else:
        tier = "low"

    agg = Counter(global_reasons)
    for _, vals in reasons.items():
        agg.update(vals)
    top = [k for k, _ in agg.most_common(8)]

    return {
        "field_risk_scores": {k: round(v, 4) for k, v in scores.items()},
        "field_risk_reasons": reasons,
        "claim_risk_score": round(claim_risk, 4),
        "claim_risk_tier": tier,
        "claim_risk_reasons": top,
    }
