#!/usr/bin/env python3
"""LLM ceiling pilot for abstract claim extraction.

Compares rule-based abstract extraction vs LLM extraction on the same subset.
Optionally adds intro/conclusion snippets from preprocess cache to help resolve
direction when abstract wording is ambiguous.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.abstract_extractor import (
    _DEFAULT_ARTICLE_DB,
    _DEFAULT_METADATA_CSV,
    _DEFAULT_PREPROCESS_DIR,
    _load_metadata_csv,
    _load_triage_records,
    _resolve_abstract_and_title,
    extract_claims_from_abstract,
)
from src.extraction.vocabulary import find_closest_dv, find_closest_iv, load_vocabulary


@dataclass(frozen=True)
class PaperAbstract:
    paper_id: str
    title: str
    abstract: str
    article_type_family: str | None
    intro_tail: str
    concl_tail: str


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _load_preprocess_snippets(paper_id: str, preprocess_dir: str) -> tuple[str, str]:
    path = Path(preprocess_dir) / f"{paper_id}.json"
    if not path.exists():
        return "", ""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "", ""
    pages = payload.get("pages") or []
    if not pages:
        return "", ""
    first_text = " ".join(_normalize(p.get("text")) for p in pages[:2])[:2200]
    last_text = " ".join(_normalize(p.get("text")) for p in pages[-2:])[:2200]
    return first_text, last_text


def _select_papers(
    triage_path: str,
    metadata_csv_path: str,
    article_db_path: str,
    preprocess_dir: str,
    n_papers: int,
) -> list[PaperAbstract]:
    import sqlite3

    records = _load_triage_records(triage_path)
    metadata_map = _load_metadata_csv(metadata_csv_path)
    db_conn = None
    if Path(article_db_path).exists():
        db_conn = sqlite3.connect(article_db_path)

    out: list[PaperAbstract] = []
    for rec in records:
        paper_id = _normalize(rec.get("paper_id"))
        if not paper_id:
            continue
        abstract, title, _source = _resolve_abstract_and_title(
            rec=rec,
            metadata_map=metadata_map,
            db_conn=db_conn,
            preprocess_dir=preprocess_dir,
        )
        abstract = _normalize(abstract)
        if len(abstract) < 60:
            continue
        intro_tail, concl_tail = _load_preprocess_snippets(paper_id, preprocess_dir)
        out.append(
            PaperAbstract(
                paper_id=paper_id,
                title=_normalize(title),
                abstract=abstract,
                article_type_family=_normalize(rec.get("article_type_family")) or None,
                intro_tail=intro_tail,
                concl_tail=concl_tail,
            )
        )
        if len(out) >= n_papers:
            break

    if db_conn is not None:
        db_conn.close()
    return out


def _codex_complete(model: str, system: str, user: str) -> str:
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
            timeout=300,
            check=False,
        )
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", errors="ignore")
            raise RuntimeError(f"codex_exec_failed rc={proc.returncode}: {err[:300]}")
        text = Path(tmp_path).read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            text = proc.stdout.decode("utf-8", errors="ignore").strip()
        return text
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass


def _parse_json_array(raw: str) -> list[dict[str, Any]]:
    text = _normalize(raw)
    if not text:
        return []
    try:
        payload = json.loads(text)
        if isinstance(payload, list):
            return [x for x in payload if isinstance(x, dict)]
    except Exception:
        pass
    m = re.search(r"\[\s*\{.*\}\s*\]|\[\s*\]", raw, re.DOTALL)
    if not m:
        return []
    try:
        payload = json.loads(m.group(0))
        if isinstance(payload, list):
            return [x for x in payload if isinstance(x, dict)]
    except Exception:
        return []
    return []


def _norm_direction(value: Any) -> str:
    s = _normalize(value).lower()
    if s in {"increase", "increased", "positive", "up"}:
        return "increase"
    if s in {"decrease", "decreased", "negative", "down"}:
        return "decrease"
    if s in {"no_effect", "null", "none", "non_significant"}:
        return "no_effect"
    if s in {"curvilinear", "inverted_u", "u_shaped"}:
        return "curvilinear"
    return "unknown"


def _map_term(term: str, *, kind: str, vocab: dict[str, Any], min_conf: float = 0.65) -> tuple[str | None, float]:
    if kind == "iv":
        mapped, conf = find_closest_iv(term, vocab)
    else:
        mapped, conf = find_closest_dv(term, vocab)
    conf_val = float(conf or 0.0)
    if mapped and conf_val >= min_conf:
        return mapped, conf_val
    return None, conf_val


def _llm_extract_claims(
    paper: PaperAbstract,
    model: str,
    vocab: dict[str, Any],
    include_intro_conclusion: bool,
) -> list[dict[str, Any]]:
    iv_keys = list((vocab.get("independent_variables") or {}).keys())[:240]
    dv_keys = list((vocab.get("dependent_variables") or {}).keys())[:240]
    system = (
        "You extract explicit empirical findings from scientific abstracts. "
        "Do not hallucinate. Return JSON only."
    )
    context_block = ""
    if include_intro_conclusion:
        context_block = (
            f"\nINTRO/LEAD CONTEXT (for direction disambiguation only):\n{paper.intro_tail[:1400]}\n"
            f"\nCONCLUSION/TAIL CONTEXT (for direction disambiguation only):\n{paper.concl_tail[:1400]}\n"
        )
    user = f"""
Extract ALL explicit findings from this ABSTRACT.
You may use INTRO/CONCLUSION context only to resolve direction (increase/decrease/no_effect) for the same claim.
If direction is not explicit, return "unknown".

PAPER_ID: {paper.paper_id}
TITLE: {paper.title}
ABSTRACT:
{paper.abstract}
{context_block}

Return a JSON array. Each item must be:
{{
  "iv_raw": "text",
  "dv_raw": "text",
  "direction": "increase|decrease|no_effect|unknown|curvilinear",
  "sample_n": null_or_int,
  "p_value": null_or_number,
  "effect_size": null_or_number,
  "effect_size_type": null_or_text,
  "evidence_quote": "short quote from abstract"
}}

Allowed IV vocab IDs (reference): {iv_keys}
Allowed DV vocab IDs (reference): {dv_keys}
"""
    raw = _codex_complete(model=model, system=system, user=user)
    items = _parse_json_array(raw)

    out: list[dict[str, Any]] = []
    seq = 0
    for item in items:
        iv_raw = _normalize(item.get("iv_raw"))
        dv_raw = _normalize(item.get("dv_raw"))
        if not iv_raw or not dv_raw:
            continue
        iv, iv_conf = _map_term(iv_raw, kind="iv", vocab=vocab)
        dv, dv_conf = _map_term(dv_raw, kind="dv", vocab=vocab)
        if iv and dv and iv == dv:
            continue
        seq += 1
        out.append(
            {
                "claim_id": f"llmabs:{paper.paper_id}:C{seq:03d}",
                "paper_id": paper.paper_id,
                "iv": iv,
                "iv_raw": iv_raw,
                "iv_mapped": bool(iv),
                "iv_confidence": round(iv_conf, 3),
                "dv": dv,
                "dv_raw": dv_raw,
                "dv_mapped": bool(dv),
                "dv_confidence": round(dv_conf, 3),
                "direction": _norm_direction(item.get("direction")),
                "sample_n": item.get("sample_n"),
                "p_value": item.get("p_value"),
                "effect_size": item.get("effect_size"),
                "effect_size_type": item.get("effect_size_type"),
                "source_quote": _normalize(item.get("evidence_quote"))[:500],
                "source": "abstract",
                "extraction_method": "llm_abstract_v1",
            }
        )
    return out


def _metrics(claims: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(claims)
    mapped_both = sum(1 for c in claims if c.get("iv_mapped") and c.get("dv_mapped"))
    unknown = sum(1 for c in claims if _norm_direction(c.get("direction")) == "unknown")
    with_n = sum(1 for c in claims if c.get("sample_n") is not None)
    with_stats = sum(1 for c in claims if c.get("effect_size") is not None or c.get("p_value") is not None)
    return {
        "claims": n,
        "mapped_both": mapped_both,
        "mapped_both_pct": round((mapped_both / n) * 100, 2) if n else 0.0,
        "unknown_direction": unknown,
        "unknown_direction_pct": round((unknown / n) * 100, 2) if n else 0.0,
        "with_sample_n": with_n,
        "with_sample_n_pct": round((with_n / n) * 100, 2) if n else 0.0,
        "with_effect_or_p": with_stats,
        "with_effect_or_p_pct": round((with_stats / n) * 100, 2) if n else 0.0,
        "direction_counts": dict(Counter(_norm_direction(c.get("direction")) for c in claims)),
        "papers": len({c.get("paper_id") for c in claims if c.get("paper_id")}),
    }


def run_pilot(
    *,
    n_papers: int,
    model: str,
    include_intro_conclusion: bool,
    triage_path: str,
    metadata_csv_path: str,
    article_db_path: str,
    preprocess_dir: str,
    vocabulary_path: str,
    output_path: str,
    require_rule_claim: bool,
) -> dict[str, Any]:
    vocab = load_vocabulary(vocabulary_path)
    papers = _select_papers(
        triage_path=triage_path,
        metadata_csv_path=metadata_csv_path,
        article_db_path=article_db_path,
        preprocess_dir=preprocess_dir,
        n_papers=max(n_papers * 12, n_papers),
    )

    llm_claims: list[dict[str, Any]] = []
    rule_claims: list[dict[str, Any]] = []
    per_paper: list[dict[str, Any]] = []

    kept_papers = 0
    for paper in papers:
        rc = extract_claims_from_abstract(
            paper_id=paper.paper_id,
            title=paper.title,
            abstract=paper.abstract,
            vocabulary=vocab,
            article_type_family=paper.article_type_family,
        )
        if require_rule_claim and len(rc) == 0:
            continue
        lc = _llm_extract_claims(
            paper=paper,
            model=model,
            vocab=vocab,
            include_intro_conclusion=include_intro_conclusion,
        )
        rule_claims.extend(rc)
        llm_claims.extend(lc)
        kept_papers += 1
        per_paper.append(
            {
                "paper_id": paper.paper_id,
                "rule_claims": len(rc),
                "llm_claims": len(lc),
                "rule_unknown_pct": _metrics(rc)["unknown_direction_pct"],
                "llm_unknown_pct": _metrics(lc)["unknown_direction_pct"],
            }
        )
        if kept_papers >= n_papers:
            break

    payload = {
        "generated_at": _utc_iso(),
        "model": model,
        "n_papers": kept_papers,
        "include_intro_conclusion": include_intro_conclusion,
        "require_rule_claim": require_rule_claim,
        "rule_metrics": _metrics(rule_claims),
        "llm_metrics": _metrics(llm_claims),
        "delta_llm_minus_rule": {
            "claims": _metrics(llm_claims)["claims"] - _metrics(rule_claims)["claims"],
            "mapped_both_pct": round(_metrics(llm_claims)["mapped_both_pct"] - _metrics(rule_claims)["mapped_both_pct"], 2),
            "unknown_direction_pct": round(_metrics(llm_claims)["unknown_direction_pct"] - _metrics(rule_claims)["unknown_direction_pct"], 2),
            "with_sample_n_pct": round(_metrics(llm_claims)["with_sample_n_pct"] - _metrics(rule_claims)["with_sample_n_pct"], 2),
            "with_effect_or_p_pct": round(_metrics(llm_claims)["with_effect_or_p_pct"] - _metrics(rule_claims)["with_effect_or_p_pct"], 2),
        },
        "per_paper": per_paper,
    }
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LLM abstract extraction ceiling pilot.")
    parser.add_argument("--n-papers", type=int, default=8)
    parser.add_argument("--model", default="gpt-5.3-codex")
    parser.add_argument("--include-intro-conclusion", action="store_true")
    parser.add_argument("--allow-zero-rule-claims", action="store_true")
    parser.add_argument("--triage-path", default="data/production/paper_triage.json")
    parser.add_argument("--metadata-csv-path", default=_DEFAULT_METADATA_CSV)
    parser.add_argument("--article-db-path", default=_DEFAULT_ARTICLE_DB)
    parser.add_argument("--preprocess-dir", default=_DEFAULT_PREPROCESS_DIR)
    parser.add_argument("--vocabulary-path", default="data/vocabulary/variable_vocabulary.json")
    parser.add_argument("--output-path", default="data/production/llm_pilot/abstract_llm_baseline.json")
    args = parser.parse_args()

    result = run_pilot(
        n_papers=args.n_papers,
        model=args.model,
        include_intro_conclusion=args.include_intro_conclusion,
        triage_path=args.triage_path,
        metadata_csv_path=args.metadata_csv_path,
        article_db_path=args.article_db_path,
        preprocess_dir=args.preprocess_dir,
        vocabulary_path=args.vocabulary_path,
        output_path=args.output_path,
        require_rule_claim=not args.allow_zero_rule_claims,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
