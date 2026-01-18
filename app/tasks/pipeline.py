
from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
from app.services.semantic_scholar import search as s2_search
from app.services.embeddings import embed_text, cosine
from app.services.extract_7panel import extract_findings_from_text
from app.pdf_ingest import extract_pdf_text
from lib.outcome_resolver import resolve_or_queue

DB = os.environ.get("AE_DB", "ae.db")
BN_EXPORT_VERSION = "0.2"
BN_EXPORT_GENERATOR = "article_eater_rulegraph_v2"

def _conn():
    return sqlite3.connect(DB)


def _resolve_db_path() -> Path:
    db = os.environ.get("AE_DB_PATH") or os.environ.get("AE_DB") or os.environ.get("DB_PATH")
    if not db:
        db_url = os.environ.get("DB_URL")
        if db_url and db_url.startswith("sqlite:///"):
            db = db_url.replace("sqlite:///", "", 1)
    return Path(db or "ae.db").expanduser().resolve()


def _db_has_table(con: sqlite3.Connection, name: str) -> bool:
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
    return cur.fetchone() is not None


def _load_rules_from_db(db_path: Path, paper_id: str) -> List[Dict[str, Any]]:
    if not db_path.exists():
        return []
    con = sqlite3.connect(str(db_path))
    try:
        if not _db_has_table(con, "rules"):
            return []
        cur = con.cursor()
        cur.execute(
            """
            SELECT rule_id, rule, confidence, triangulation_score, contradiction_count, job_id, created_at
            FROM rules
            ORDER BY created_at DESC
            """
        )
        rows = cur.fetchall()
        if not rows:
            return []
        rules: List[Dict[str, Any]] = []
        for row in rows:
            rule_id, rule_text, confidence, _, _, _, _ = row
            lhs = []
            rhs = []
            if rule_text and "->" in rule_text:
                parts = [p.strip() for p in rule_text.split("->", 1)]
                lhs_raw = [p.strip() for p in parts[0].split(",")] if parts[0] else []
                lhs = [{"var": v, "state": "present"} for v in lhs_raw if v]
                rhs = [{"var": parts[1], "state": "present"}] if parts[1] else []
            rules.append(
                {
                    "schema": "ae.rule.v1",
                    "rule_id": str(rule_id),
                    "paper_id": paper_id,
                    "rule_type": "edge",
                    "statement": rule_text or "",
                    "lhs": lhs,
                    "rhs": rhs,
                    "polarity": "unknown",
                    "strength": {
                        "kind": "confidence" if confidence is not None else "unknown",
                        "type": None,
                        "value": float(confidence) if confidence is not None else None,
                    },
                    "applicability": {"population": [], "setting": [], "boundary_conditions": []},
                    "evidence_links": [],
                    "bn_mapping": {"node_suggestions": [], "discretization_hint": "unknown"},
                    "ae_confidence": float(confidence) if confidence is not None else 0.0,
                }
            )
        return rules
    finally:
        con.close()

def _bn_export_from_rules(rules: List[Dict[str, Any]], paper_id: str) -> Dict[str, Any]:
    nodes = []
    edges = []
    export_rules = []
    for rule in rules:
        rule_id = str(rule.get("rule_id") or "")
        rule_text = rule.get("statement") or rule.get("rule") or rule.get("rule_text") or ""
        node_id = f"rule:{paper_id}:{rule_id}" if rule_id else f"rule:{paper_id}"
        nodes.append({"id": node_id, "type": "rule", "label": rule_text or node_id})
        export_rules.append(
            {
                "rule_id": rule_id,
                "paper_id": paper_id,
                "rule_text": rule_text,
                "subject_scope": {},
                "subject_moderators": [],
                "subject_scope_summary": "",
                "moderators_summary": "",
                "evidence": {"links": rule.get("evidence_links") or []},
                "provenance": {"source": "ae.rules"},
                "graph_version": "2.0",
                "status": "accepted",
            }
        )
    return {
        "bn_version": BN_EXPORT_VERSION,
        "generator": BN_EXPORT_GENERATOR,
        "filters": {"paper_id": paper_id, "text_filter": None, "age_band": None, "trait": None},
        "meta": {"rules_count": len(export_rules), "papers": [paper_id]},
        "nodes": nodes,
        "edges": edges,
        "rules": export_rules,
    }

def _compute_af_decision(
    claims: List[Dict[str, Any]],
    rules: List[Dict[str, Any]],
    blocking_issues: List[str],
) -> Dict[str, Any]:
    min_rules = int(os.environ.get("AE_ACCEPT_MIN_RULES", "1"))
    min_conf = float(os.environ.get("AE_ACCEPT_MIN_CONF", "0.2"))
    claim_conf = max([c.get("ae_confidence", 0.0) for c in claims], default=0.0)
    rule_conf = max([r.get("ae_confidence", 0.0) for r in rules], default=0.0)
    best_conf = max(claim_conf, rule_conf)
    if not claims and not rules:
        return {"decision": "reject", "reason": "no_extracts", "confidence": best_conf}
    if blocking_issues:
        return {"decision": "accept_with_caveats", "reason": "blocking_issues", "confidence": best_conf}
    if len(rules) < min_rules:
        return {"decision": "accept_with_caveats", "reason": "insufficient_rules", "confidence": best_conf}
    if best_conf < min_conf:
        return {"decision": "accept_with_caveats", "reason": "low_confidence", "confidence": best_conf}
    return {"decision": "accept", "reason": "meets_thresholds", "confidence": best_conf}

def run_l0_harvest(job_id: int, query: str, limit: int=20):
    hits = s2_search(query, limit=limit)
    with _conn() as con:
        for h in hits:
            con.execute("INSERT OR IGNORE INTO articles (s2_id,title,abstract,year,url,citation_count) VALUES (?,?,?,?,?,?)",
                        (h.get('paperId'), h.get('title'), h.get('abstract'), h.get('year'), h.get('url'), h.get('citationCount',0)))
        con.execute("UPDATE processing_queue SET status='done', result='l0_harvested' WHERE id=?", (job_id,))
    return len(hits)

def run_l1_clustering(job_id: int, topic: str, sample: int=200):
    with _conn() as con:
        rows = con.execute("SELECT id, abstract FROM articles WHERE abstract IS NOT NULL LIMIT ?", (sample,)).fetchall()
    vecs = [(rid, embed_text(ab or "")) for rid, ab in rows]
    # naive single-pass threshold clustering
    clusters = []
    TH = 0.8
    for rid, v in vecs:
        placed=False
        for c in clusters:
            if cosine(v, c['centroid']) > TH:
                c['ids'].append(rid)
                placed=True; break
        if not placed:
            clusters.append({'ids':[rid], 'centroid': v})
    with _conn() as con:
        for i, c in enumerate(clusters):
            for rid in c['ids']:
                con.execute("UPDATE articles SET cluster=? WHERE id=?", (i, rid))
        con.execute("UPDATE processing_queue SET status='done', result='l1_clustered' WHERE id=?", (job_id,))
    return len(clusters)

def run_l2_extraction(job_id: int, article_id: int, topic: str):
    with _conn() as con:
        row = con.execute("SELECT id, title, abstract, pdf_text FROM articles WHERE id=?", (article_id,)).fetchone()
    if not row: return 0
    text = row[3] or row[2] or ""
    findings = extract_findings_from_text(text, topic=topic, is_admin=False)
    with _conn() as con:
        for f in findings:
            st = f.get("statistics",{}) if isinstance(f, dict) else {}
            con.execute("""INSERT INTO findings(article_id, finding_text, p_value, effect_size, effect_size_type, sample_size, ci_lower, ci_upper, quote, page_span)
                        VALUES(?,?,?,?,?,?,?,?,?,?)""", (article_id, 
                            f.get("finding_text") if isinstance(f, dict) else str(f),
                            st.get("p_value"), st.get("effect_size"), st.get("effect_size_type"), st.get("sample_size"),
                            st.get("ci_lower"), st.get("ci_upper"),
                            f.get("quote"), f.get("page_span")))
        con.execute("UPDATE processing_queue SET status='done', result='l2_extracted' WHERE id=?", (job_id,))
    return len(findings)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_jsonl(p: Path, rows: List[Dict[str, Any]]) -> None:
    with p.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _audit_event(run_id: str, paper_id: str, stage: str, event: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema": "ae.audit_event.v1",
        "ts": _utc_now(),
        "run_id": run_id,
        "paper_id": paper_id,
        "stage": stage,
        "event": event,
        "data": data,
    }


def _review_item(run_id: str, paper_id: str, item_id: str, severity: str, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema": "ae.review_item.v1",
        "paper_id": paper_id,
        "run_id": run_id,
        "item_id": item_id,
        "severity": severity,
        "question": question,
        "context": context,
    }


def _run_from_contract_bundle_impl(
    *, in_dir: Path, out_dir: Path, profile: str, hitl: str
) -> dict:
    """
    Read AF-style bundle in in_dir, run AE extraction, write AE outputs to out_dir,
    and return a summary dict (counts, warnings, etc).
    """
    in_dir = Path(in_dir).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    run_id = f"ae.run.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    audits: List[Dict[str, Any]] = []
    review_items: List[Dict[str, Any]] = []

    pdf_path = in_dir / "paper.pdf"
    paper_path = in_dir / "paper.json"
    paper = json.loads(paper_path.read_text(encoding="utf-8"))

    paper_id = paper.get("paper_id", "unknown")
    pdf_sha256 = _sha256_file(pdf_path) if pdf_path.exists() else "0" * 64
    paper_json_sha256 = _sha256_file(paper_path)

    audits.append(_audit_event(run_id, paper_id, "ingest", "start", {"profile": profile, "hitl": hitl}))

    text = ""
    fulltext_path = in_dir / "fulltext.txt"
    abstract_path = in_dir / "abstract.txt"
    if fulltext_path.exists():
        text = fulltext_path.read_text(encoding="utf-8", errors="ignore")
    elif abstract_path.exists():
        text = abstract_path.read_text(encoding="utf-8", errors="ignore")
    elif pdf_path.exists():
        text = extract_pdf_text(pdf_path) or ""

    if not text:
        audits.append(_audit_event(run_id, paper_id, "extract", "fail", {"reason": "no_text_extracted"}))
        review_items.append(
            _review_item(
                run_id,
                paper_id,
                "rev_missing_text",
                "blocking",
                "No text could be extracted from the input bundle.",
                {"pdf": str(pdf_path)},
            )
        )

    topic = paper.get("title") or paper.get("doi") or "unknown"
    findings = []
    llm_blocked = False
    if text:
        has_llm_key = bool(
            os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("OLLAMA_MODEL")
            or os.environ.get("OLLAMA_BASE")
            or os.environ.get("AE_LLM_MODEL")
        )
        if not has_llm_key:
            llm_blocked = True
            audits.append(_audit_event(run_id, paper_id, "extract", "skip", {"reason": "llm_not_configured"}))
            review_items.append(
                _review_item(
                    run_id,
                    paper_id,
                    "rev_llm_key",
                    "blocking",
                    "LLM API key missing; configure GOOGLE_API_KEY or OPENAI_API_KEY.",
                    {},
                )
            )
        else:
            try:
                findings = extract_findings_from_text(text, topic=topic, is_admin=False)
            except Exception as exc:
                llm_blocked = True
                audits.append(_audit_event(run_id, paper_id, "extract", "fail", {"reason": str(exc)}))
                review_items.append(
                    _review_item(
                        run_id,
                        paper_id,
                        "rev_llm_error",
                        "blocking",
                        "LLM extraction failed; check provider configuration.",
                        {"error": str(exc)},
                    )
                )

    claims: List[Dict[str, Any]] = []
    rules: List[Dict[str, Any]] = []
    for idx, finding in enumerate(findings, start=1):
        if isinstance(finding, dict):
            stats = finding.get("statistics", {}) or {}
            antecedents = finding.get("antecedents") or finding.get("antecedent") or []
            if isinstance(antecedents, str):
                antecedents = [antecedents]
            if not antecedents:
                constructs = finding.get("constructs") or {}
                env_factors = constructs.get("environment_factors") or []
                if isinstance(env_factors, str):
                    env_factors = [env_factors]
                antecedents = env_factors
            consequent = (
                finding.get("consequent")
                or finding.get("finding_text")
                or finding.get("statement")
                or "Unspecified finding"
            )
            statement = finding.get("finding_text") or finding.get("statement") or consequent
            confidence = float(finding.get("ae_confidence") or finding.get("confidence") or 0.0)
        else:
            stats = {}
            antecedents = []
            consequent = str(finding) or "Unspecified finding"
            statement = str(finding) or "Unspecified finding"
            confidence = 0.0

        claim_id = f"{paper_id}.claim.{idx}"
        claim = {
            "schema": "ae.claim.v1",
            "claim_id": claim_id,
            "paper_id": paper_id,
            "claim_type": "descriptive",
            "statement": statement,
            "constructs": {
                "environment_factors": [],
                "outcomes": [],
                "mediators": [],
                "moderators": [],
            },
            "study": {
                "design": "unknown",
                "sample": {
                    "n": stats.get("sample_size"),
                    "population": None,
                    "age_mean": None,
                    "country": None,
                },
                "task": [],
                "setting": [],
            },
            "statistics": {
                "effect_size": {
                    "type": stats.get("effect_size_type"),
                    "value": stats.get("effect_size"),
                },
                "p_value": stats.get("p_value"),
                "ci95": None,
            },
            "evidence": [],
            "constraints": [],
            "ae_confidence": confidence,
        }
        claims.append(claim)

        n_val = stats.get("sample_size")
        d_val = stats.get("effect_size")
        p_val = stats.get("p_value")
        rule_statement = (
            f"{statement} (n={n_val if n_val is not None else 'unknown'}, "
            f"d={d_val if d_val is not None else 'unknown'}, "
            f"p={p_val if p_val is not None else 'unknown'})"
        )

        rule_id = f"{paper_id}.rule.{idx}"
        measure_dir = finding.get("measure_direction") if isinstance(finding, dict) else None
        if measure_dir == "positive":
            polarity = "positive"
        elif measure_dir == "negative":
            polarity = "negative"
        elif stats.get("effect_size") is not None:
            polarity = "positive" if float(stats.get("effect_size")) >= 0 else "negative"
        else:
            polarity = "unknown"
        strength = {"kind": "unknown", "type": None, "value": None}
        if stats.get("effect_size") is not None:
            strength = {
                "kind": "effect_size",
                "type": stats.get("effect_size_type"),
                "value": stats.get("effect_size"),
            }
        elif stats.get("p_value") is not None:
            strength = {"kind": "p_value", "type": None, "value": stats.get("p_value")}

        rule = {
            "schema": "ae.rule.v1",
            "rule_id": rule_id,
            "paper_id": paper_id,
            "rule_type": "edge",
            "statement": rule_statement,
            "lhs": antecedents if isinstance(antecedents, list) else [],
            "rhs": [consequent] if consequent else [],
            "polarity": polarity,
            "strength": strength,
            "applicability": {"population": [], "setting": [], "boundary_conditions": []},
            "evidence_links": [{"claim_id": claim_id}],
            "bn_mapping": {"node_suggestions": [], "discretization_hint": "unknown"},
            "ae_confidence": confidence,
        }
        rules.append(rule)

    db_rules = _load_rules_from_db(_resolve_db_path(), paper_id)
    if db_rules:
        rules = db_rules
        audits.append(_audit_event(run_id, paper_id, "rules", "source", {"source": "db", "n_rules": len(rules)}))

    bn_export = None
    if rules:
        bn_export = _bn_export_from_rules(rules, paper_id)
        _write_json(out_dir / "bn_export.json", bn_export)
        audits.append(
            _audit_event(
                run_id,
                paper_id,
                "bn_export",
                "done",
                {"path": "bn_export.json", "n_rules": len(rules)},
            )
        )

    status = "SUCCESS" if claims else ("FAIL" if not text else "PARTIAL_SUCCESS")
    blocking = []
    errors = []
    if not text:
        blocking.append("no_text_extracted")
        errors.append({"code": "no_text", "message": "No text could be extracted from bundle inputs."})
    elif llm_blocked:
        blocking.append("llm_not_configured")
        errors.append({"code": "llm_not_configured", "message": "Missing or misconfigured LLM API key."})
    elif not claims:
        blocking.append("no_findings")

    decision = _compute_af_decision(claims, rules, blocking)
    warnings = []
    if decision["decision"] != "accept":
        warnings.append(f"af_decision:{decision['decision']}:{decision['reason']}")
        review_items.append(
            _review_item(
                run_id,
                paper_id,
                "rev_accept_criteria",
                "info",
                "Review AE accept criteria; partially useful papers should not be rejected.",
                {"decision": decision, "blocking_issues": blocking},
            )
        )

    result = {
        "schema": "ae.result.v1",
        "paper_id": paper_id,
        "pdf_sha256": pdf_sha256,
        "run_id": run_id,
        "status": status,
        "profile": profile,
        "hitl": hitl,
        "summary": {
            "n_claims": len(claims),
            "n_rules": len(rules),
            "n_effect_sizes": len([c for c in claims if c["statistics"]["effect_size"]["value"] is not None]),
            "n_population_records": len([c for c in claims if c["study"]["sample"]["n"] is not None]),
            "n_environment_factors": sum(len(c["constructs"]["environment_factors"]) for c in claims),
        },
        "artifacts": {
            "claims_jsonl": "claims.jsonl",
            "rules_jsonl": "rules.jsonl",
            "provenance_json": "provenance.json",
            "audit_log_jsonl": "audit.log.jsonl",
        },
        "quality": {
            "confidence": decision["confidence"],
            "blocking_issues": blocking,
            "warnings": warnings,
            "af_decision": decision,
        },
        "errors": errors,
    }
    audits.append(_audit_event(run_id, paper_id, "decision", "af", decision))
    if decision["decision"] != "accept" and status == "SUCCESS":
        status = "PARTIAL_SUCCESS"
        result["status"] = status

    provenance = {
        "schema": "ae.provenance.v1",
        "paper_id": paper_id,
        "run_id": run_id,
        "created_at": _utc_now(),
        "inputs": {"pdf_sha256": pdf_sha256, "paper_json_sha256": paper_json_sha256},
        "environment": {"python": sys.version.split()[0], "platform": sys.platform},
        "models": [],
        "tools": [{"name": "ae.pipeline", "version": "v1"}],
    }

    audits.append(_audit_event(run_id, paper_id, "extract", "done", {"n_claims": len(claims), "n_rules": len(rules)}))
    audits.append(_audit_event(run_id, paper_id, "finalize", "done", {"status": status}))

    _write_json(out_dir / "result.json", result)
    _write_jsonl(out_dir / "claims.jsonl", claims)
    _write_jsonl(out_dir / "rules.jsonl", rules)
    _write_json(out_dir / "provenance.json", provenance)
    _write_jsonl(out_dir / "audit.log.jsonl", audits)
    _write_jsonl(out_dir / "review_items.jsonl", review_items)

    return {
        "run_id": run_id,
        "paper_id": paper_id,
        "status": status,
        "n_claims": len(claims),
        "n_rules": len(rules),
        "blocking_issues": blocking,
    }

# --- CHATGPT_PATCH_AE_AF_WIRING_V1 BEGIN ---
"""
Contract wiring entrypoint for Article Finder to Article Eater.

This function is called by app/cli/article_eater_contract_cli.py when present.
It is intentionally defensive: it attempts to call the existing extraction pipeline
if available, but will degrade gracefully if the extractor signature differs.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import importlib
import hashlib

def _resolve_outcome_id(raw_id, paper_id=None):
    """Resolve outcome ID through Outcome_Contractor."""
    try:
        result = resolve_or_queue(str(raw_id), paper_id=paper_id)
        return result['canonical_id']
    except Exception:
        return str(raw_id)


def _read_text_if_exists(p: Path) -> Optional[str]:
    try:
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    return None

def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _safe_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None

def _try_call_extractor(fulltext: str, meta: Dict[str, Any], profile: str) -> Dict[str, Any]:
    mod = _safe_import("app.services.extract_7panel")
    if mod is None:
        return {"_error": "extract_7panel_import_failed"}
    candidates = ["extract_7panel","extract","run_extract","run","main_extract"]
    last = None
    for name in candidates:
        fn = getattr(mod, name, None)
        if callable(fn):
            try:
                # Try a few common call patterns
                try:
                    return fn(fulltext=fulltext, meta=meta, profile=profile)  # type: ignore
                except TypeError:
                    pass
                try:
                    return fn(fulltext, meta)  # type: ignore
                except TypeError:
                    pass
                try:
                    return fn(fulltext)  # type: ignore
                except TypeError:
                    pass
                try:
                    return fn({"fulltext": fulltext, "meta": meta, "profile": profile})  # type: ignore
                except TypeError:
                    pass
            except Exception as e:
                last = e
                continue
    if last is not None:
        return {"_error": "extractor_call_failed: %s: %s" % (last.__class__.__name__, str(last))}
    return {"_error": "no_extractor_entrypoint_found"}

def run_from_contract_bundle(*, in_dir: Path, out_dir: Path, profile: str, hitl: str) -> Dict[str, Any]:
    """Compat wrapper used by CLI; delegates to implementation with contract outputs."""
    return _run_from_contract_bundle_impl(in_dir=in_dir, out_dir=out_dir, profile=profile, hitl=hitl)
# --- CHATGPT_PATCH_AE_AF_WIRING_V1 END ---
