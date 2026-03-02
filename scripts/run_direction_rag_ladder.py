#!/usr/bin/env python3
"""Direction adjudication with local RAG + multi-model consensus (no HITL).

Pipeline:
1. Load direction tension queue.
2. Retrieve top local evidence chunks per claim from preprocess cache + existing claims.
3. Ask multiple LLM profiles (Codex models) to classify direction using only those chunks.
4. Verify model votes (evidence grounding + lexical/stat sign checks).
5. Apply 2-of-3 consensus to produce direction overrides.

Outputs:
- data/review/direction_overrides.rag_llm_consensus.json
- data/review/direction_rag_llm_consensus_report.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.llm import LLMClient

DEFAULT_QUEUE_PATH = "data/review/theory_direction_tension_queue.json"
DEFAULT_STRUCTURED_CLAIMS_PATH = "data/production/structured_claims.json"
DEFAULT_ABSTRACT_CLAIMS_PATH = "data/production/abstract_claims.json"
DEFAULT_PREPROCESS_DIR = "data/production/pdf_preprocess_cache"
DEFAULT_PROFILES_PATH = "config/llm_table_pilot_profiles.codex.json"
DEFAULT_OVERRIDES_OUT = "data/review/direction_overrides.rag_llm_consensus.json"
DEFAULT_REPORT_OUT = "data/review/direction_rag_llm_consensus_report.json"


@dataclass(frozen=True)
class ModelProfile:
    name: str
    provider: str
    model: str


@dataclass
class EvidenceChunk:
    chunk_id: str
    source: str
    page: int | None
    text: str
    score: float


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _safe_slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.:-]+", "_", text).strip("_") or "unknown"


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _failed_path(path: str | Path) -> Path:
    p = Path(path)
    if p.suffix.lower() == ".json":
        return p.with_name(f"{p.stem}_failed.json")
    return Path(f"{str(p)}_failed.json")


def _error_kind(msg: str) -> str:
    m = _normalize(msg)
    if not m:
        return "unknown_error"
    return m.split(":", 1)[0].strip() or "unknown_error"


def _load_profiles(path: str) -> list[ModelProfile]:
    payload = _load_json(path)
    out: list[ModelProfile] = []
    for item in payload.get("profiles", []):
        if not isinstance(item, dict):
            continue
        name = _normalize(item.get("name"))
        provider = _normalize(item.get("provider")).lower()
        model = _normalize(item.get("model"))
        if not name or not provider or not model:
            continue
        out.append(ModelProfile(name=name, provider=provider, model=model))
    if not out:
        raise SystemExit(f"No usable profiles found in {path}")
    return out


def _codex_complete(model: str, system: str, user: str, timeout_s: int = 180) -> str:
    prompt = f"SYSTEM:\n{system}\n\nUSER:\n{user}\n"
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp_path = tmp.name
    cmd = [
        "codex",
        "exec",
        "-m",
        model,
        "-s",
        "read-only",
        "--skip-git-repo-check",
        "--output-last-message",
        tmp_path,
        "-",
    ]
    try:
        proc = subprocess.run(
            cmd,
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(PROJECT_ROOT),
            timeout=timeout_s,
            check=False,
        )
        text = Path(tmp_path).read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            text = proc.stdout.decode("utf-8", errors="ignore").strip()
        if text:
            return text
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", errors="ignore")
            raise RuntimeError(f"codex_exec_failed rc={proc.returncode}: {err[:400]}")
        return text
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")


def _provider_complete(
    llm_client: LLMClient,
    profile: ModelProfile,
    system: str,
    user: str,
    timeout_s: int,
) -> str:
    provider = profile.provider.lower().strip()
    model = profile.model
    if provider in {"codex_exec", "codex"}:
        return _codex_complete(model=model, system=system, user=user, timeout_s=timeout_s)
    if provider == "openai":
        return llm_client.complete_openai(
            model=model,
            system=system,
            user=user,
            temperature=0.0,
            max_tokens=1200,
        )
    if provider in {"gemini", "google"}:
        return llm_client.complete_gemini(
            model=model,
            system=system,
            user=user,
            temperature=0.0,
            max_tokens=1200,
        )
    if provider == "ollama":
        return llm_client.complete_ollama(
            model=model,
            system=system,
            user=user,
            temperature=0.0,
            max_tokens=1200,
        )
    raise ValueError(f"Unsupported provider: {profile.provider}")


def _parse_json_object(raw: str) -> dict[str, Any] | None:
    text = _normalize(raw)
    if not text:
        return None
    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return payload
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        payload = json.loads(m.group(0))
        if isinstance(payload, dict):
            return payload
    except Exception as e:
        import logging; logging.getLogger(__name__).debug(f"Returning None: {e}")
        return None
    return None


def _norm_direction(value: Any) -> str:
    s = _normalize(value).lower()
    if s in {"increase", "increased", "higher", "up", "positive", "facilitates", "improves"}:
        return "increase"
    if s in {"decrease", "decreased", "lower", "down", "negative", "reduces", "impairs"}:
        return "decrease"
    if s in {"no_effect", "null", "none", "non_significant", "no-significant-effect"}:
        return "no_effect"
    return "unknown"


def _tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2]


def _direction_cues(text: str) -> tuple[bool, bool, bool]:
    t = text.lower()
    no_eff = bool(
        re.search(
            r"\b(no significant|not significant|non-significant|nonsignificant|ns\b|p\s*[>=]\s*0?\.0?5)\b",
            t,
        )
    )
    inc = bool(re.search(r"\b(increase|increased|higher|greater|improv|enhanc|positive association)\b", t))
    dec = bool(re.search(r"\b(decrease|decreased|lower|reduc|diminish|worse|negative association)\b", t))
    return inc, dec, no_eff


def _infer_direction_from_text(text: str) -> str:
    inc, dec, no_eff = _direction_cues(text)
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


def _paper_preprocess_path(preprocess_dir: str, paper_id: str) -> Path | None:
    p = Path(preprocess_dir) / f"{paper_id}.json"
    if p.exists():
        return p
    return None


def _load_preprocess_pages(preprocess_dir: str, paper_id: str) -> list[dict[str, Any]]:
    p = _paper_preprocess_path(preprocess_dir, paper_id)
    if p is None:
        return []
    try:
        payload = _load_json(p)
    except Exception:
        return []
    pages = payload.get("pages") if isinstance(payload, dict) else None
    if isinstance(pages, list):
        return [x for x in pages if isinstance(x, dict)]
    return []


def _split_text_windows(text: str, max_chars: int = 700, sentence_window: int = 4) -> list[str]:
    t = _normalize(text)
    if not t:
        return []
    parts = [p for p in re.split(r"(?<=[.!?])\s+", t) if p]
    if not parts:
        return [t[:max_chars]]
    out: list[str] = []
    i = 0
    while i < len(parts):
        chunk = " ".join(parts[i : i + sentence_window]).strip()
        if len(chunk) > max_chars:
            chunk = chunk[:max_chars]
        if chunk:
            out.append(chunk)
        i += max(1, sentence_window - 1)
    return out


def _candidate_keywords(claim: dict[str, Any]) -> set[str]:
    iv = _normalize(claim.get("iv")).replace("_", " ")
    dv = _normalize(claim.get("dv")).replace("_", " ")
    extras = "results discussion conclusion significant effect association impact relationship"
    return set(_tokenize(f"{iv} {dv} {extras}"))


def _score_chunk(text: str, keywords: set[str], iv: str, dv: str) -> float:
    t = _normalize(text)
    if not t:
        return 0.0
    toks = set(_tokenize(t))
    overlap = len(toks.intersection(keywords))
    score = float(overlap)
    low = t.lower()
    if iv and iv in low:
        score += 4.0
    if dv and dv in low:
        score += 4.0
    if re.search(r"\b(p\s*[<=>]\s*0?\.\d+|β|beta|r\s*=|t\(|f\(|η2|eta\^?2|odds ratio)\b", low):
        score += 2.0
    if re.search(r"\breferences?\b", low) and re.search(r"\bdoi\b", low):
        score -= 4.0
    if len(t) < 60:
        score -= 1.0
    return score


def _build_evidence_chunks(
    claim: dict[str, Any],
    structured_by_id: dict[str, dict[str, Any]],
    claims_by_paper: dict[str, list[dict[str, Any]]],
    abstract_by_paper: dict[str, list[dict[str, Any]]],
    preprocess_dir: str,
    top_k: int,
) -> list[EvidenceChunk]:
    iv = _normalize(claim.get("iv")).replace("_", " ").lower()
    dv = _normalize(claim.get("dv")).replace("_", " ").lower()
    keywords = _candidate_keywords(claim)
    paper_id = _normalize(claim.get("paper_id"))
    out: list[EvidenceChunk] = []
    seq = 1

    # 1) Existing claim quotes for the same claim_id / paper.
    claim_id = _normalize(claim.get("claim_id"))
    base_claim = structured_by_id.get(claim_id) or {}
    for src_field in ("source_quote", "evidence_text", "evidence_snippet", "context"):
        text = _normalize(base_claim.get(src_field))
        if not text:
            continue
        sc = _score_chunk(text, keywords, iv, dv) + 6.0
        out.append(EvidenceChunk(chunk_id=f"E{seq}", source=f"structured:{src_field}", page=None, text=text, score=sc))
        seq += 1

    # 2) Other structured claims from same paper.
    for rec in claims_by_paper.get(paper_id, [])[:80]:
        text = _normalize(rec.get("source_quote") or rec.get("context"))
        if not text:
            continue
        sc = _score_chunk(text, keywords, iv, dv) + 1.5
        if sc <= 0.0:
            continue
        out.append(
            EvidenceChunk(
                chunk_id=f"E{seq}",
                source=f"paper_claim:{_normalize(rec.get('claim_id')) or 'unknown'}",
                page=None,
                text=text,
                score=sc,
            )
        )
        seq += 1

    # 3) Abstract claims source quotes for same paper.
    for rec in abstract_by_paper.get(paper_id, [])[:120]:
        text = _normalize(rec.get("source_quote") or rec.get("context"))
        if not text:
            continue
        sc = _score_chunk(text, keywords, iv, dv) + 1.0
        if sc <= 0.0:
            continue
        out.append(
            EvidenceChunk(
                chunk_id=f"E{seq}",
                source=f"abstract_claim:{_normalize(rec.get('claim_id')) or 'unknown'}",
                page=None,
                text=text,
                score=sc,
            )
        )
        seq += 1

    # 4) PDF preprocess pages (local RAG).
    pages = _load_preprocess_pages(preprocess_dir, paper_id)
    for page in pages[:30]:
        pnum = int(page.get("page") or 0)
        text = _normalize(page.get("text"))
        if not text:
            continue
        for win in _split_text_windows(text, max_chars=700, sentence_window=4):
            sc = _score_chunk(win, keywords, iv, dv)
            if sc <= 0.0:
                continue
            out.append(EvidenceChunk(chunk_id=f"E{seq}", source="pdf_preprocess", page=pnum, text=win, score=sc))
            seq += 1

    # Deduplicate by normalized text.
    uniq: dict[str, EvidenceChunk] = {}
    for ch in out:
        key = _normalize(ch.text).lower()
        prev = uniq.get(key)
        if prev is None or ch.score > prev.score:
            uniq[key] = ch
    deduped = list(uniq.values())
    deduped.sort(key=lambda x: x.score, reverse=True)
    return deduped[:top_k]


def _adjudication_prompt(
    claim: dict[str, Any],
    chunks: list[EvidenceChunk],
) -> tuple[str, str]:
    evidence_lines = []
    for ch in chunks:
        page = f", page={ch.page}" if ch.page else ""
        evidence_lines.append(f"[{ch.chunk_id}] source={ch.source}{page}\n{ch.text}")
    evidence_block = "\n\n".join(evidence_lines) if evidence_lines else "[NONE]"
    system = (
        "You are a strict evidence-grounded adjudicator for scientific claim direction. "
        "Use only the provided evidence chunks. Do not use prior knowledge."
    )
    user = f"""
Claim:
- claim_id: {claim.get("claim_id")}
- paper_id: {claim.get("paper_id")}
- iv: {claim.get("iv")}
- dv: {claim.get("dv")}
- observed_direction: {claim.get("direction")}

Evidence chunks:
{evidence_block}

Task:
1. Decide direction for IV -> DV from evidence only:
   increase | decrease | no_effect | unknown
2. If evidence is mismatched to this IV/DV pair or ambiguous, return unknown.
3. Prefer no_effect only for explicit null findings.
4. Cite chunk IDs and quote text exactly from those chunks.
5. Include a field-level evidence packet for direction with support_type and alternatives.

Return JSON only:
{{
  "direction": "increase|decrease|no_effect|unknown",
  "confidence": 0.0,
  "justification": "one short paragraph",
  "evidence_chunk_ids": ["E1","E3"],
  "evidence_quotes": ["exact quote 1", "exact quote 2"],
  "field_assessments": {{
    "direction": {{
      "value": "increase|decrease|no_effect|unknown",
      "support_type": "explicit|derived|inferred",
      "section": "abstract|methods|results|table|figure_caption|discussion|conclusion|unknown",
      "page": 1,
      "alt_interpretations": ["increase","decrease"],
      "confidence": 0.0
    }}
  }}
}}
"""
    return system, user


def _verify_vote(vote: dict[str, Any], chunks: list[EvidenceChunk]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    c_map = {c.chunk_id: c for c in chunks}
    direction = _norm_direction(vote.get("direction"))
    if direction not in {"increase", "decrease", "no_effect", "unknown"}:
        reasons.append("invalid_direction")
        return False, reasons

    ids = vote.get("evidence_chunk_ids")
    quotes = vote.get("evidence_quotes")
    if not isinstance(ids, list) or not ids:
        reasons.append("missing_evidence_chunk_ids")
        return False, reasons
    if not isinstance(quotes, list) or not quotes:
        reasons.append("missing_evidence_quotes")
        return False, reasons

    for cid in ids:
        if _normalize(cid) not in c_map:
            reasons.append(f"unknown_chunk_id:{cid}")
    if reasons:
        return False, reasons

    concat = " ".join(c_map[_normalize(cid)].text for cid in ids if _normalize(cid) in c_map).lower()
    for q in quotes:
        qn = _normalize(q).lower()
        if len(qn) < 12:
            reasons.append("quote_too_short")
            continue
        if qn not in concat:
            reasons.append("quote_not_found_in_chunks")
    if reasons:
        return False, reasons

    evidence_text = " ".join(quotes)
    lexical_dir = _infer_direction_from_text(evidence_text)
    signed_dir = _infer_direction_from_signed_stats(evidence_text)
    if direction in {"increase", "decrease"}:
        if lexical_dir in {"increase", "decrease"} and lexical_dir != direction:
            reasons.append("lexical_direction_conflict")
        if signed_dir in {"increase", "decrease"} and signed_dir != direction:
            reasons.append("signed_stat_direction_conflict")
    if direction == "no_effect":
        if lexical_dir in {"increase", "decrease"}:
            reasons.append("no_effect_but_directional_cue_present")

    return len(reasons) == 0, reasons


def _score_vote_risk(vote: dict[str, Any]) -> float:
    """Heuristic risk score (0..1) for one model vote."""
    risk = 0.06
    if not vote.get("verified"):
        risk += 0.34
    direction = _norm_direction(vote.get("direction"))
    if direction == "unknown":
        risk += 0.18
    if vote.get("raw_error"):
        risk += 0.35
    if vote.get("verify_reasons"):
        risk += min(0.22, 0.05 * len(vote.get("verify_reasons") or []))

    packet = vote.get("field_assessments")
    direction_packet = packet.get("direction") if isinstance(packet, dict) else None
    if isinstance(direction_packet, dict):
        support = _normalize(direction_packet.get("support_type")).lower()
        if support == "derived":
            risk += 0.10
        elif support == "inferred":
            risk += 0.20
        elif support not in {"explicit", "derived", "inferred"}:
            risk += 0.08
        if not _normalize(direction_packet.get("section")):
            risk += 0.07
        if direction_packet.get("page") in (None, "", 0):
            risk += 0.05
        alts = direction_packet.get("alt_interpretations")
        if isinstance(alts, list) and alts:
            risk += min(0.12, 0.03 * len(alts))
    else:
        risk += 0.16

    return max(0.0, min(1.0, risk))


def _build_override_entry(
    claim: dict[str, Any],
    final_direction: str,
    votes: list[dict[str, Any]],
    chunks: list[EvidenceChunk],
) -> dict[str, Any]:
    observed = _norm_direction(claim.get("direction"))
    valid = [v for v in votes if v.get("verified")]
    dir_counts = Counter(_norm_direction(v.get("direction")) for v in valid)
    top_vote = valid[0] if valid else (votes[0] if votes else {})
    quote = ""
    if isinstance(top_vote.get("evidence_quotes"), list) and top_vote["evidence_quotes"]:
        quote = _normalize(top_vote["evidence_quotes"][0])[:500]
    evidence_url = f"local://{DEFAULT_PREPROCESS_DIR}/{_safe_slug(_normalize(claim.get('paper_id')))}.json"
    rationale = (
        f"rag_llm_consensus observed={observed} final={final_direction}; "
        f"valid_votes={dict(dir_counts)}"
    )
    return {
        "claim_id": claim.get("claim_id"),
        "direction": final_direction,
        "status": "approved",
        "reviewer": "Codex-rag-llm-consensus",
        "rationale": rationale,
        "evidence_url": evidence_url,
        "evidence_quote": quote,
        "updated_at": _utc_iso(),
        "votes": [
            {
                "profile": v.get("profile"),
                "model": v.get("model"),
                "direction": _norm_direction(v.get("direction")),
                "confidence": v.get("confidence"),
                "verified": v.get("verified"),
                "verify_reasons": v.get("verify_reasons"),
            }
            for v in votes
        ],
        "evidence_chunks": [
            {
                "chunk_id": c.chunk_id,
                "source": c.source,
                "page": c.page,
                "score": round(c.score, 3),
                "text": c.text[:320],
            }
            for c in chunks[:4]
        ],
    }


def _consensus_direction(votes: list[dict[str, Any]], min_votes: int = 2) -> tuple[str, dict[str, int]]:
    valid_dirs = [_norm_direction(v.get("direction")) for v in votes if v.get("verified")]
    counts = Counter(valid_dirs)
    if not counts:
        return "unknown", {}
    best_dir, best_n = counts.most_common(1)[0]
    if best_n >= min_votes:
        return best_dir, dict(counts)
    return "unknown", dict(counts)


def _require_provider_credentials(profiles: list[ModelProfile], llm_client: LLMClient) -> list[str]:
    errs: list[str] = []
    for p in profiles:
        prov = p.provider.lower().strip()
        if prov == "openai":
            if not llm_client.openai_key and not (llm_client.base.startswith("http://localhost") or llm_client.base.startswith("http://127.0.0.1")):
                errs.append(f"{p.name}: missing OPENAI_API_KEY")
        elif prov in {"gemini", "google"}:
            if not llm_client.google_key:
                errs.append(f"{p.name}: missing GOOGLE_API_KEY/GEMINI_API_KEY")
        elif prov == "ollama":
            # No key required; connectivity check covers availability.
            pass
        elif prov in {"codex_exec", "codex"}:
            # No key check here.
            pass
        else:
            errs.append(f"{p.name}: unsupported provider '{p.provider}'")
    return errs


def _preflight_connectivity_check(
    profiles: list[ModelProfile],
    llm_client: LLMClient,
    timeout_s: int,
) -> dict[str, str]:
    system = "Return compact JSON only."
    user = '{"ok": true}'
    failures: dict[str, str] = {}
    for p in profiles:
        try:
            out = _provider_complete(
                llm_client=llm_client,
                profile=p,
                system=system,
                user=user,
                timeout_s=timeout_s,
            )
            if not _normalize(out):
                failures[p.name] = "empty_response"
        except Exception as exc:
            failures[p.name] = f"{type(exc).__name__}: {exc}"
    return failures


def _build_vote_stats(adjudications: list[dict[str, Any]]) -> dict[str, Any]:
    vote_total = 0
    vote_error_total = 0
    vote_verified_total = 0
    error_kinds: Counter[str] = Counter()
    verify_reason_counts: Counter[str] = Counter()
    for rec in adjudications:
        for v in rec.get("votes", []):
            vote_total += 1
            err = _normalize(v.get("raw_error"))
            if err:
                vote_error_total += 1
                error_kinds[_error_kind(err)] += 1
            if v.get("verified"):
                vote_verified_total += 1
            for r in v.get("verify_reasons") or []:
                verify_reason_counts[_normalize(r) or "unknown_verify_reason"] += 1
    all_votes_failed = vote_total > 0 and vote_error_total == vote_total
    return {
        "vote_total": vote_total,
        "vote_error_total": vote_error_total,
        "vote_verified_total": vote_verified_total,
        "all_votes_failed": all_votes_failed,
        "error_kinds": dict(error_kinds),
        "verify_reason_counts": dict(verify_reason_counts),
    }


def _write_failed_artifacts(
    report_out: str,
    overrides_out: str,
    summary: dict[str, Any],
    reasons: list[str],
    extra: dict[str, Any] | None = None,
) -> None:
    payload = {
        "status": "failed",
        "failed_at": _utc_iso(),
        "reasons": reasons,
        "summary": summary,
    }
    if extra:
        payload["details"] = extra
    _write_json(_failed_path(report_out), payload)
    _write_json(
        _failed_path(overrides_out),
        {
            "status": "failed",
            "failed_at": _utc_iso(),
            "reasons": reasons,
            "overrides": [],
            "summary": summary,
        },
    )


def _validate_extraction_success(
    extraction_path: str,
    baseline_path: str,
) -> tuple[bool, list[str], dict[str, Any]]:
    reasons: list[str] = []
    extra: dict[str, Any] = {}
    current = _load_json(extraction_path)
    baseline = _load_json(baseline_path)
    curr_summary = current.get("summary", {}) if isinstance(current, dict) else {}
    base_summary = baseline.get("summary", {}) if isinstance(baseline, dict) else {}

    overrides_applied = int(curr_summary.get("direction_overrides_applied") or 0)
    if overrides_applied <= 0:
        reasons.append("direction_overrides_applied<=0")

    curr_tension = int(curr_summary.get("theory_direction_tension_claims") or 0) + int(curr_summary.get("theory_null_tension_claims") or 0)
    base_tension = int(base_summary.get("theory_direction_tension_claims") or 0) + int(base_summary.get("theory_null_tension_claims") or 0)
    curr_dirs = current.get("counts_by_direction") if isinstance(current, dict) else {}
    base_dirs = baseline.get("counts_by_direction") if isinstance(baseline, dict) else {}
    tension_reduced = curr_tension < base_tension
    dir_changed = curr_dirs != base_dirs
    if not (tension_reduced or dir_changed):
        reasons.append("no_tension_or_direction_delta")

    extra = {
        "extraction_path": extraction_path,
        "baseline_path": baseline_path,
        "overrides_applied": overrides_applied,
        "tension_before": base_tension,
        "tension_after": curr_tension,
        "direction_counts_before": base_dirs,
        "direction_counts_after": curr_dirs,
        "tension_reduced": tension_reduced,
        "direction_counts_changed": dir_changed,
    }
    return len(reasons) == 0, reasons, extra


def _run_one_claim(
    claim: dict[str, Any],
    profiles: list[ModelProfile],
    llm_client: LLMClient,
    structured_by_id: dict[str, dict[str, Any]],
    claims_by_paper: dict[str, list[dict[str, Any]]],
    abstract_by_paper: dict[str, list[dict[str, Any]]],
    preprocess_dir: str,
    top_k_chunks: int,
    min_consensus_votes: int,
    model_timeout_s: int,
) -> dict[str, Any]:
    chunks = _build_evidence_chunks(
        claim=claim,
        structured_by_id=structured_by_id,
        claims_by_paper=claims_by_paper,
        abstract_by_paper=abstract_by_paper,
        preprocess_dir=preprocess_dir,
        top_k=top_k_chunks,
    )
    votes: list[dict[str, Any]] = []
    if not chunks:
        return {
            "claim_id": claim.get("claim_id"),
            "paper_id": claim.get("paper_id"),
            "observed_direction": _norm_direction(claim.get("direction")),
            "final_direction": "unknown",
            "consensus_counts": {},
            "chunks_used": 0,
            "votes": [],
            "error": "no_evidence_chunks",
        }

    for profile in profiles:
        system, user = _adjudication_prompt(claim, chunks)
        rec: dict[str, Any] = {
            "profile": profile.name,
            "model": profile.model,
            "direction": "unknown",
            "confidence": 0.0,
            "verified": False,
            "verify_reasons": [],
            "raw_error": None,
        }
        try:
            raw = _provider_complete(
                llm_client=llm_client,
                profile=profile,
                system=system,
                user=user,
                timeout_s=model_timeout_s,
            )
            obj = _parse_json_object(raw) or {}
            rec["direction"] = _norm_direction(obj.get("direction"))
            try:
                rec["confidence"] = float(obj.get("confidence") or 0.0)
            except Exception:
                rec["confidence"] = 0.0
            rec["justification"] = _normalize(obj.get("justification"))
            rec["evidence_chunk_ids"] = obj.get("evidence_chunk_ids")
            rec["evidence_quotes"] = obj.get("evidence_quotes")
            rec["field_assessments"] = obj.get("field_assessments")
            ok, reasons = _verify_vote(rec, chunks)
            rec["verified"] = ok
            rec["verify_reasons"] = reasons
            rec["vote_risk_score"] = _score_vote_risk(rec)
        except Exception as exc:
            rec["raw_error"] = f"{type(exc).__name__}: {exc}"
            rec["vote_risk_score"] = _score_vote_risk(rec)
        votes.append(rec)

    final_direction, counts = _consensus_direction(votes, min_votes=min_consensus_votes)
    return {
        "claim_id": claim.get("claim_id"),
        "paper_id": claim.get("paper_id"),
        "observed_direction": _norm_direction(claim.get("direction")),
        "final_direction": final_direction,
        "consensus_counts": counts,
        "chunks_used": len(chunks),
        "votes": votes,
        "override": _build_override_entry(claim, final_direction, votes, chunks),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local RAG + multi-LLM direction consensus.")
    parser.add_argument("--queue-path", default=DEFAULT_QUEUE_PATH)
    parser.add_argument("--structured-claims-path", default=DEFAULT_STRUCTURED_CLAIMS_PATH)
    parser.add_argument("--abstract-claims-path", default=DEFAULT_ABSTRACT_CLAIMS_PATH)
    parser.add_argument("--preprocess-dir", default=DEFAULT_PREPROCESS_DIR)
    parser.add_argument("--profiles", default=DEFAULT_PROFILES_PATH)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--top-k-chunks", type=int, default=10)
    parser.add_argument("--min-consensus-votes", type=int, default=2)
    parser.add_argument("--model-timeout-s", type=int, default=120)
    parser.add_argument("--preflight-timeout-s", type=int, default=45)
    parser.add_argument("--skip-preflight-connectivity", action="store_true")
    parser.add_argument("--allow-noop", action="store_true")
    parser.add_argument("--check-extraction-output")
    parser.add_argument("--baseline-extraction-path", default=DEFAULT_STRUCTURED_CLAIMS_PATH)
    parser.add_argument("--output-overrides", default=DEFAULT_OVERRIDES_OUT)
    parser.add_argument("--output-report", default=DEFAULT_REPORT_OUT)
    args = parser.parse_args()

    queue_payload = _load_json(args.queue_path)
    queue_items = queue_payload.get("items") if isinstance(queue_payload, dict) else queue_payload
    if not isinstance(queue_items, list):
        raise SystemExit("Queue payload must contain an items list.")
    if args.limit and args.limit > 0:
        queue_items = queue_items[: args.limit]

    structured_payload = _load_json(args.structured_claims_path)
    structured_claims = structured_payload.get("claims") if isinstance(structured_payload, dict) else []
    if not isinstance(structured_claims, list):
        structured_claims = []
    structured_by_id = {
        _normalize(c.get("claim_id")): c for c in structured_claims if isinstance(c, dict) and _normalize(c.get("claim_id"))
    }
    claims_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in structured_claims:
        if not isinstance(c, dict):
            continue
        pid = _normalize(c.get("paper_id"))
        if pid:
            claims_by_paper[pid].append(c)

    abstract_payload = _load_json(args.abstract_claims_path)
    abstract_claims = abstract_payload.get("claims") if isinstance(abstract_payload, dict) else []
    if not isinstance(abstract_claims, list):
        abstract_claims = []
    abstract_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in abstract_claims:
        if not isinstance(c, dict):
            continue
        pid = _normalize(c.get("paper_id"))
        if pid:
            abstract_by_paper[pid].append(c)

    profiles = _load_profiles(args.profiles)
    llm_client = LLMClient()

    preflight_summary = {
        "queue_items": len(queue_items),
        "profiles": [p.__dict__ for p in profiles],
    }
    preflight_reasons: list[str] = []
    preflight_details: dict[str, Any] = {}
    if len(queue_items) == 0:
        preflight_reasons.append("empty_queue_items")
    credential_errors = _require_provider_credentials(profiles, llm_client)
    if credential_errors:
        preflight_reasons.append("missing_or_invalid_provider_credentials")
        preflight_details["credential_errors"] = credential_errors
    if not args.skip_preflight_connectivity:
        connectivity_failures = _preflight_connectivity_check(
            profiles=profiles,
            llm_client=llm_client,
            timeout_s=max(10, args.preflight_timeout_s),
        )
        if connectivity_failures:
            preflight_reasons.append("provider_connectivity_check_failed")
            preflight_details["connectivity_failures"] = connectivity_failures

    if preflight_reasons:
        _write_failed_artifacts(
            report_out=args.output_report,
            overrides_out=args.output_overrides,
            summary=preflight_summary,
            reasons=preflight_reasons,
            extra=preflight_details,
        )
        print(json.dumps({"status": "failed", "stage": "preflight", "reasons": preflight_reasons, **preflight_details}, indent=2))
        raise SystemExit(2)

    adjudications: list[dict[str, Any]] = []
    for idx, item in enumerate(queue_items, start=1):
        if not isinstance(item, dict):
            continue
        result = _run_one_claim(
            claim=item,
            profiles=profiles,
            llm_client=llm_client,
            structured_by_id=structured_by_id,
            claims_by_paper=claims_by_paper,
            abstract_by_paper=abstract_by_paper,
            preprocess_dir=args.preprocess_dir,
            top_k_chunks=max(3, args.top_k_chunks),
            min_consensus_votes=max(2, args.min_consensus_votes),
            model_timeout_s=max(30, args.model_timeout_s),
        )
        adjudications.append(result)
        print(
            f"[{idx}/{len(queue_items)}] {result.get('claim_id')} "
            f"obs={result.get('observed_direction')} final={result.get('final_direction')} "
            f"counts={result.get('consensus_counts')}",
            flush=True,
        )

    overrides: list[dict[str, Any]] = []
    changed = 0
    for rec in adjudications:
        observed = _norm_direction(rec.get("observed_direction"))
        final = _norm_direction(rec.get("final_direction"))
        if final != observed:
            changed += 1
        # Keep all adjudicated claims so reruns are deterministic.
        ov = rec.get("override")
        if isinstance(ov, dict):
            overrides.append(ov)

    vote_stats = _build_vote_stats(adjudications)

    summary = {
        "generated_at": _utc_iso(),
        "queue_path": args.queue_path,
        "structured_claims_path": args.structured_claims_path,
        "abstract_claims_path": args.abstract_claims_path,
        "profiles": [p.__dict__ for p in profiles],
        "total_claims": len(adjudications),
        "changed_vs_observed": changed,
        "direction_counts_final": dict(Counter(_norm_direction(r.get("final_direction")) for r in adjudications)),
        "direction_counts_observed": dict(Counter(_norm_direction(r.get("observed_direction")) for r in adjudications)),
        **vote_stats,
    }
    report_payload = {
        "summary": summary,
        "adjudications": adjudications,
    }
    overrides_payload = {
        "generated_at": _utc_iso(),
        "protocol": "rag_llm_consensus_no_hitl",
        "consensus_rule": f"{max(2, args.min_consensus_votes)}_of_{len(profiles)}",
        "overrides": overrides,
    }

    # Validity gates: prevent false-success outputs.
    fail_reasons: list[str] = []
    if len(overrides) == 0:
        fail_reasons.append("overrides_empty")
    if vote_stats.get("all_votes_failed"):
        fail_reasons.append("all_votes_failed")
    if not args.allow_noop and changed <= 0:
        fail_reasons.append("no_direction_changes")

    extraction_gate: dict[str, Any] | None = None
    if args.check_extraction_output:
        ok, reasons, extra = _validate_extraction_success(
            extraction_path=args.check_extraction_output,
            baseline_path=args.baseline_extraction_path,
        )
        extraction_gate = {"ok": ok, "reasons": reasons, "details": extra}
        if not ok:
            fail_reasons.extend([f"extraction_gate:{r}" for r in reasons])

    if fail_reasons:
        fail_extra = {
            "vote_stats": vote_stats,
            "top_error_kinds": vote_stats.get("error_kinds", {}),
            "top_verify_reasons": vote_stats.get("verify_reason_counts", {}),
        }
        if extraction_gate is not None:
            fail_extra["extraction_gate"] = extraction_gate
        _write_failed_artifacts(
            report_out=args.output_report,
            overrides_out=args.output_overrides,
            summary=summary,
            reasons=fail_reasons,
            extra=fail_extra,
        )
        print(json.dumps({"status": "failed", "stage": "postrun", "reasons": fail_reasons, "vote_stats": vote_stats}, indent=2))
        raise SystemExit(2)

    _write_json(args.output_report, report_payload)
    _write_json(args.output_overrides, overrides_payload)

    print(json.dumps(summary, indent=2))
    print(f"report_written={args.output_report}")
    print(f"overrides_written={args.output_overrides}")


if __name__ == "__main__":
    main()
