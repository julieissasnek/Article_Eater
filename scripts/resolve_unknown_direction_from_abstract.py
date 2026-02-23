#!/usr/bin/env python3
"""Resolve unknown claim directions using abstract-focused evidence.

Policy:
- Only require direction for empirical claim contexts.
- For eligible unknowns, try:
  1) known-direction abstract claims from same paper,
  2) abstract text sentence-level directional cues,
  3) optional LLM adjudication over abstract text.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.llm import LLMClient
from src.extraction.direction_expectation import direction_expected_for_claim
from src.extraction.figure_direction import infer_direction_from_pdf_figures

DEFAULT_INPUT = "data/production/structured_claims.rag_llm_consensus.risk_scored.json"
DEFAULT_ABSTRACT_CLAIMS = "data/production/abstract_claims.json"
DEFAULT_PREPROCESS_DIR = "data/production/pdf_preprocess_cache"

_ABSTRACT_HEADING_RE = re.compile(r"\babstract\b\s*[:.\-]?\s*(?!art\b)", re.IGNORECASE)
_ABSTRACT_STOP_RE = re.compile(
    r"\b("
    r"keywords?|index\s+terms?|introduction|background|methods?|materials\s+and\s+methods|"
    r"study\s+\d|aims?\s+and\s+hypotheses|objective"
    r")\b",
    re.IGNORECASE,
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STAT_RE = re.compile(r"\b(p\s*[<=>]\s*0?\.\d+|β\s*=?\s*[+-]?\d*\.?\d+|r\s*=\s*[+-]?\d*\.?\d+|t\(|f\()", re.IGNORECASE)


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.lower()) if len(t) >= 3}


def _safe_slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.:-]+", "_", text).strip("_") or "unknown"


def _norm_direction(value: Any) -> str:
    s = _norm(value).lower()
    if s in {"increase", "increased", "higher", "up", "positive", "facilitates", "improves"}:
        return "increase"
    if s in {"decrease", "decreased", "lower", "down", "negative", "reduces", "impairs"}:
        return "decrease"
    if s in {"no_effect", "null", "none", "non_significant", "non-significant"}:
        return "no_effect"
    return "unknown"


def _paper_id_to_pdf_stem_candidates(paper_id: str) -> list[str]:
    pid = _norm(paper_id)
    if not pid:
        return []
    out: list[str] = []
    out.append(_safe_slug(pid))
    if pid.lower().startswith("doi:"):
        doi = pid[4:].strip()
        if doi:
            out.append(f"doi_{doi.replace('/', '_')}")
            out.append(f"doi_{doi.replace('/', '_').replace('.', '_')}")
    return [c for c in out if c]


def _resolve_pdf_for_paper(
    paper_id: str,
    pdf_dir: Path,
    pdf_index: dict[str, Path],
) -> Path | None:
    if not pdf_dir.exists():
        return None
    for stem in _paper_id_to_pdf_stem_candidates(paper_id):
        p = pdf_index.get(stem.lower())
        if p and p.exists():
            return p
    return None


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


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_abstract_from_preprocess(preprocess_dir: Path, paper_id: str) -> str:
    path = preprocess_dir / f"{paper_id}.json"
    if not path.exists():
        return ""
    try:
        payload = _load_json(path)
    except Exception:
        return ""
    pages = payload.get("pages") if isinstance(payload, dict) else []
    if not isinstance(pages, list):
        return ""
    text = "\n".join(_norm(p.get("text")) for p in pages[:2] if isinstance(p, dict))
    if not text:
        return ""
    m = _ABSTRACT_HEADING_RE.search(text)
    if m and m.start() < 6000:
        rest = text[m.end() : m.end() + 9000]
        stop = _ABSTRACT_STOP_RE.search(rest)
        cand = rest[: stop.start()] if stop else rest
        return _norm(cand)
    return ""


def _join_abstract_claim_quotes(abstract_claims_for_paper: list[dict[str, Any]]) -> str:
    parts = []
    for rec in abstract_claims_for_paper:
        if _norm(rec.get("source")).lower() != "abstract":
            continue
        q = _norm(rec.get("source_quote"))
        if q:
            parts.append(q)
    # Dedup preserve order.
    seen = set()
    uniq = []
    for p in parts:
        key = p.lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    return " ".join(uniq)


def _claim_token_signature(claim: dict[str, Any]) -> set[str]:
    iv = _norm(claim.get("iv")).replace("_", " ")
    dv = _norm(claim.get("dv")).replace("_", " ")
    iv_raw = _norm(claim.get("iv_raw"))
    dv_raw = _norm(claim.get("dv_raw"))
    return _tokens(f"{iv} {dv} {iv_raw} {dv_raw}")


def _text_match_score(text: str, sig: set[str]) -> float:
    toks = _tokens(text)
    if not toks:
        return 0.0
    overlap = len(toks.intersection(sig))
    score = float(overlap)
    if _STAT_RE.search(text):
        score += 1.2
    return score


def _resolve_from_known_abstract_claims(
    claim: dict[str, Any],
    abstract_claims_for_paper: list[dict[str, Any]],
) -> tuple[str, str, float]:
    sig = _claim_token_signature(claim)
    best = ("unknown", "", 0.0)
    for rec in abstract_claims_for_paper:
        if _norm(rec.get("source")).lower() != "abstract":
            continue
        d = _norm_direction(rec.get("direction"))
        if d == "unknown":
            continue
        quote = _norm(rec.get("source_quote"))
        if not quote:
            continue
        sc = _text_match_score(quote, sig)
        if sc > best[2]:
            best = (d, quote, sc)
    if best[2] >= 2.0:
        return best[0], best[1], min(0.92, 0.55 + 0.08 * best[2])
    return "unknown", "", 0.0


def _resolve_from_abstract_text(claim: dict[str, Any], abstract_text: str) -> tuple[str, str, float]:
    if not abstract_text:
        return "unknown", "", 0.0
    sig = _claim_token_signature(claim)
    best = ("unknown", "", 0.0)
    for sent in _SENTENCE_SPLIT_RE.split(abstract_text):
        s = _norm(sent)
        if len(s) < 30:
            continue
        match = _text_match_score(s, sig)
        if match < 1.0:
            continue
        d = _infer_direction_from_text(s)
        if d == "unknown":
            continue
        sc = match + (1.0 if _STAT_RE.search(s) else 0.0)
        if sc > best[2]:
            best = (d, s, sc)
    if best[2] > 0:
        return best[0], best[1], min(0.90, 0.50 + 0.08 * best[2])
    return "unknown", "", 0.0


def _parse_json_object(raw: str) -> dict[str, Any] | None:
    txt = _norm(raw)
    if not txt:
        return None
    try:
        obj = json.loads(txt)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        if isinstance(obj, dict):
            return obj
    except Exception:
        return None
    return None


def _codex_complete(model: str, system: str, user: str, timeout_s: int = 120) -> str:
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
        stdout = proc.stdout.decode("utf-8", errors="ignore").strip()
        if not text:
            text = stdout
        # Even non-zero may still produce usable JSON.
        if text:
            return text
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", errors="ignore")
            raise RuntimeError(f"codex_exec_failed rc={proc.returncode}: {err[:400]}")
        return text
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass


def _llm_direction_from_abstract(
    claim: dict[str, Any],
    abstract_text: str,
    llm_client: LLMClient,
    provider: str,
    model: str,
    timeout_s: int,
) -> tuple[str, str, float]:
    if not abstract_text:
        return "unknown", "", 0.0
    system = (
        "You are a strict scientific direction adjudicator. "
        "Use only the provided abstract text. Return JSON only."
    )
    user = f"""
Claim context:
- iv: {_norm(claim.get("iv") or claim.get("iv_raw"))}
- dv: {_norm(claim.get("dv") or claim.get("dv_raw"))}

Abstract:
{abstract_text[:12000]}

Task:
Decide IV->DV direction from abstract evidence only:
increase | decrease | no_effect | unknown

Return JSON:
{{
  "direction": "increase|decrease|no_effect|unknown",
  "confidence": 0.0,
  "evidence_quote": "exact quote from abstract"
}}
"""
    raw = ""
    prov = provider.lower().strip()
    if prov in {"codex_exec", "codex"}:
        raw = _codex_complete(model=model, system=system, user=user, timeout_s=timeout_s)
    elif prov == "openai":
        raw = llm_client.complete_openai(model=model, system=system, user=user, temperature=0.0, max_tokens=700)
    elif prov in {"gemini", "google"}:
        raw = llm_client.complete_gemini(model=model, system=system, user=user, temperature=0.0, max_tokens=700)
    elif prov == "ollama":
        raw = llm_client.complete_ollama(model=model, system=system, user=user, temperature=0.0, max_tokens=700)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    obj = _parse_json_object(raw) or {}
    direction = _norm_direction(obj.get("direction"))
    quote = _norm(obj.get("evidence_quote"))
    try:
        conf = float(obj.get("confidence") or 0.0)
    except Exception:
        conf = 0.0
    if direction not in {"increase", "decrease", "no_effect", "unknown"}:
        direction = "unknown"
    return direction, quote, max(0.0, min(1.0, conf))


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve unknown directions from abstracts with expectation gating.")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--abstract-claims", default=DEFAULT_ABSTRACT_CLAIMS)
    parser.add_argument("--preprocess-dir", default=DEFAULT_PREPROCESS_DIR)
    parser.add_argument("--output", default="")
    parser.add_argument("--report", default="")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--use-llm", action="store_true")
    parser.add_argument("--use-figure-vision", action="store_true")
    parser.add_argument("--pdf-dir", default="data/production/pdf_repaired")
    parser.add_argument("--figure-max-pages", type=int, default=30)
    parser.add_argument("--llm-provider", default="codex_exec")
    parser.add_argument("--llm-model", default="gpt-5.2-codex")
    parser.add_argument("--llm-timeout-s", type=int, default=90)
    args = parser.parse_args()

    input_path = Path(args.input)
    abstract_path = Path(args.abstract_claims)
    preprocess_dir = Path(args.preprocess_dir)
    payload = _load_json(input_path)
    claims = payload.get("claims") if isinstance(payload, dict) else None
    if not isinstance(claims, list):
        raise SystemExit("input payload must be dict with claims list")

    out_path = Path(args.output) if args.output else input_path.with_name(f"{input_path.stem}.dir_resolved.json")
    report_path = Path(args.report) if args.report else input_path.with_name(f"{input_path.stem}.dir_resolved_report.json")

    abs_payload = _load_json(abstract_path)
    abs_claims = abs_payload.get("claims") if isinstance(abs_payload, dict) else abs_payload
    if not isinstance(abs_claims, list):
        abs_claims = []
    abs_by_paper: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in abs_claims:
        if not isinstance(rec, dict):
            continue
        pid = _norm(rec.get("paper_id"))
        if pid:
            abs_by_paper[pid].append(rec)

    llm_client = LLMClient()
    pdf_dir = Path(args.pdf_dir)
    pdf_index: dict[str, Path] = {}
    if args.use_figure_vision and pdf_dir.exists():
        for p in pdf_dir.glob("*.pdf"):
            pdf_index[p.stem.lower()] = p

    counters = Counter()
    unresolved_examples: list[dict[str, Any]] = []
    changed = 0
    scanned = 0

    for claim in claims:
        if not isinstance(claim, dict):
            continue
        d = _norm_direction(claim.get("direction"))
        if d != "unknown":
            continue
        scanned += 1
        if args.limit and scanned > args.limit:
            break

        expected, reason = direction_expected_for_claim(claim)
        claim["direction_expected"] = bool(expected)
        claim["direction_expected_reason"] = reason

        if not expected:
            counters["unknown_not_required"] += 1
            claim["direction_resolution_status"] = "not_required"
            continue

        pid = _norm(claim.get("paper_id"))
        paper_abs_claims = abs_by_paper.get(pid, [])
        abstract_text = _extract_abstract_from_preprocess(preprocess_dir, pid)
        if not abstract_text:
            abstract_text = _join_abstract_claim_quotes(paper_abs_claims)

        # Step 1: known abstract claim direction matching
        r1_dir, r1_quote, r1_conf = _resolve_from_known_abstract_claims(claim, paper_abs_claims)
        if r1_dir != "unknown":
            claim["direction"] = r1_dir
            claim["direction_resolution_status"] = "resolved"
            claim["direction_resolution_method"] = "abstract_claim_match"
            claim["direction_resolution_quote"] = r1_quote
            claim["direction_resolution_confidence"] = round(r1_conf, 3)
            counters["resolved_abstract_claim_match"] += 1
            changed += 1
            continue

        # Step 2: abstract text cueing
        r2_dir, r2_quote, r2_conf = _resolve_from_abstract_text(claim, abstract_text)
        if r2_dir != "unknown":
            claim["direction"] = r2_dir
            claim["direction_resolution_status"] = "resolved"
            claim["direction_resolution_method"] = "abstract_text_heuristic"
            claim["direction_resolution_quote"] = r2_quote
            claim["direction_resolution_confidence"] = round(r2_conf, 3)
            counters["resolved_abstract_text_heuristic"] += 1
            changed += 1
            continue

        # Step 3: optional LLM
        if args.use_figure_vision:
            pdf_path = _resolve_pdf_for_paper(pid, pdf_dir, pdf_index)
            if pdf_path is not None:
                try:
                    vis = infer_direction_from_pdf_figures(
                        pdf_path=pdf_path,
                        claim=claim,
                        max_pages=max(1, int(args.figure_max_pages)),
                    )
                except Exception as exc:
                    counters["figure_errors"] += 1
                    claim["direction_resolution_figure_error"] = f"{type(exc).__name__}: {exc}"
                    vis = None
                if vis and vis.direction in {"increase", "decrease"}:
                    claim["direction"] = vis.direction
                    claim["direction_resolution_status"] = "resolved"
                    claim["direction_resolution_method"] = "figure_line_slope"
                    claim["direction_resolution_quote"] = vis.evidence_quote
                    claim["direction_resolution_confidence"] = round(float(vis.confidence), 3)
                    claim["direction_resolution_source_page"] = vis.source_page
                    claim["direction_resolution_visual_diagnostics"] = vis.diagnostics
                    counters["resolved_figure_line_slope"] += 1
                    changed += 1
                    continue
            else:
                counters["figure_pdf_missing"] += 1

        # Step 4: optional LLM
        if args.use_llm and abstract_text:
            try:
                r3_dir, r3_quote, r3_conf = _llm_direction_from_abstract(
                    claim=claim,
                    abstract_text=abstract_text,
                    llm_client=llm_client,
                    provider=args.llm_provider,
                    model=args.llm_model,
                    timeout_s=max(20, int(args.llm_timeout_s)),
                )
            except Exception as exc:
                counters["llm_errors"] += 1
                claim["direction_resolution_llm_error"] = f"{type(exc).__name__}: {exc}"
                r3_dir, r3_quote, r3_conf = "unknown", "", 0.0
            if r3_dir != "unknown":
                claim["direction"] = r3_dir
                claim["direction_resolution_status"] = "resolved"
                claim["direction_resolution_method"] = "llm_abstract_adjudication"
                claim["direction_resolution_quote"] = r3_quote
                claim["direction_resolution_confidence"] = round(r3_conf, 3)
                counters["resolved_llm_abstract_adjudication"] += 1
                changed += 1
                continue

        counters["unresolved_required"] += 1
        claim["direction_resolution_status"] = "unresolved"
        if len(unresolved_examples) < 40:
            unresolved_examples.append(
                {
                    "claim_id": claim.get("claim_id"),
                    "paper_id": claim.get("paper_id"),
                    "article_type_family": claim.get("article_type_family"),
                    "claim_source": claim.get("claim_source"),
                    "iv": claim.get("iv"),
                    "dv": claim.get("dv"),
                    "source_quote": _norm(claim.get("source_quote"))[:220],
                }
            )

    # Recompute summary directional counts if present.
    dir_counts = Counter(_norm_direction(c.get("direction")) for c in claims if isinstance(c, dict))
    if isinstance(payload.get("counts_by_direction"), dict):
        payload["counts_by_direction"] = dict(dir_counts)
    payload["claims"] = claims
    payload["direction_resolution_summary"] = {
        "generated_at": _utc_iso(),
        "input": str(input_path),
        "total_claims": len([c for c in claims if isinstance(c, dict)]),
        "unknown_scanned": scanned if not args.limit else min(scanned, args.limit),
        "changed": changed,
        "counters": dict(counters),
        "llm_used": bool(args.use_llm),
        "figure_vision_used": bool(args.use_figure_vision),
        "figure_pdf_dir": str(pdf_dir) if args.use_figure_vision else None,
        "llm_provider": args.llm_provider if args.use_llm else None,
        "llm_model": args.llm_model if args.use_llm else None,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    report = {
        "summary": payload["direction_resolution_summary"],
        "unknown_after_resolution": dir_counts.get("unknown", 0),
        "direction_counts_after": dict(dir_counts),
        "unresolved_examples": unresolved_examples,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report["summary"], indent=2))
    print(f"resolved_output={out_path}")
    print(f"resolution_report={report_path}")


if __name__ == "__main__":
    main()
