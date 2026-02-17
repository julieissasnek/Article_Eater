#!/usr/bin/env python3
"""Quality gates for realtime table/PDF extraction artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_THRESHOLDS = {
    "max_no_claims_rate": 0.6,
    "min_anchor_coverage_global": 0.9,
    "max_unresolved_environment_rate": 0.65,
    "max_unresolved_outcome_rate": 0.65,
    "min_relation_type_diversity": 6.0,
    "min_theory_link_paper_coverage": 0.4,
    "min_inter_article_paper_coverage": 0.4,
    "max_manual_review_backlog": 400.0,
    "min_node_type_tag_rate": 0.95,
    "min_edge_type_tag_rate": 0.90,
    "min_article_type_metadata_coverage": 0.95,
    "max_article_type_low_confidence_rate": 0.65,
    "max_article_type_review_rate": 0.75,
    "max_missing_resolution_match_type_rate": 0.10,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Check extraction quality gates.")
    p.add_argument("--queue-csv", default="data/production/realtime_pdf_completion_queue.csv")
    p.add_argument("--confirmed-csv", default="data/production/realtime_pdf_confirmed_rows.csv")
    p.add_argument("--audit-jsonl", default="data/production/realtime_extraction_audit.jsonl")
    p.add_argument("--manual-review-csv", default="data/review/table_quality_manual_queue.csv")
    p.add_argument("--article-type-review-csv", default="data/review/article_type_manual_queue.csv")
    p.add_argument("--report-json", default="data/production/table_extraction_quality_report.json")
    p.add_argument("--thresholds", default="config/table_extraction_quality_thresholds.json")
    p.add_argument("--soft", action="store_true", help="Always exit 0")
    return p.parse_args()


def load_thresholds(path: Path) -> Dict[str, float]:
    out = dict(DEFAULT_THRESHOLDS)
    if not path.exists():
        return out
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return out
    for k, v in out.items():
        raw = data.get(k, v)
        try:
            out[k] = float(raw)
        except Exception:
            out[k] = v
    return out


def read_csv_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_jsonl_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def metric_ratio(num: int, den: int) -> float:
    return float(num) / float(den) if den else 0.0


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def main() -> int:
    args = parse_args()
    thresholds = load_thresholds(Path(args.thresholds))

    queue_rows = read_csv_rows(Path(args.queue_csv))
    confirmed_rows = read_csv_rows(Path(args.confirmed_csv))
    audit_rows = read_jsonl_rows(Path(args.audit_jsonl))
    manual_rows = read_csv_rows(Path(args.manual_review_csv))
    article_type_review_rows = read_csv_rows(Path(args.article_type_review_csv))

    extracted = sum(1 for r in queue_rows if r.get("status") == "completed_pdf_extracted")
    no_claims = sum(1 for r in queue_rows if r.get("status") == "completed_pdf_no_claims")
    processed = extracted + no_claims

    no_claims_rate = metric_ratio(no_claims, processed)

    anchored = sum(1 for r in confirmed_rows if str(r.get("source_quote_hash", "")).strip())
    unresolved_env = sum(
        1 for r in confirmed_rows if str(r.get("environment_canonical_id", "")).upper().startswith("UNRESOLVED:")
    )
    unresolved_out = sum(
        1 for r in confirmed_rows if str(r.get("outcome_canonical_id", "")).upper().startswith("UNRESOLVED:")
    )

    anchor_coverage = metric_ratio(anchored, len(confirmed_rows))
    unresolved_env_rate = metric_ratio(unresolved_env, len(confirmed_rows))
    unresolved_out_rate = metric_ratio(unresolved_out, len(confirmed_rows))
    resolution_rows = [
        r
        for r in confirmed_rows
        if str(r.get("environment_canonical_id", "")).strip()
        or str(r.get("outcome_canonical_id", "")).strip()
    ]
    env_match_type_counts = Counter(
        str(r.get("environment_resolution_match_type", "")).strip() or "missing"
        for r in resolution_rows
    )
    out_match_type_counts = Counter(
        str(r.get("outcome_resolution_match_type", "")).strip() or "missing"
        for r in resolution_rows
    )
    env_llm_rate = metric_ratio(env_match_type_counts.get("llm_lookup_fallback", 0), len(resolution_rows))
    out_llm_rate = metric_ratio(out_match_type_counts.get("llm_lookup_fallback", 0), len(resolution_rows))
    env_semantic_rate = metric_ratio(env_match_type_counts.get("semantic_lookup_fallback", 0), len(resolution_rows))
    out_semantic_rate = metric_ratio(out_match_type_counts.get("semantic_lookup_fallback", 0), len(resolution_rows))
    env_missing_match_type_rate = metric_ratio(env_match_type_counts.get("missing", 0), len(resolution_rows))
    out_missing_match_type_rate = metric_ratio(out_match_type_counts.get("missing", 0), len(resolution_rows))

    relation_types = {
        str(r.get("argument_relation_type", "")).strip()
        for r in confirmed_rows
        if str(r.get("argument_relation_type", "")).strip()
    }
    relation_type_diversity = len(relation_types)

    taggable_rows = [
        r
        for r in confirmed_rows
        if str(r.get("statement", "")).strip() or str(r.get("ae_confidence", "")).strip()
    ]
    node_type_populated = sum(1 for r in taggable_rows if str(r.get("node_type", "")).strip())
    node_type_tag_rate = metric_ratio(node_type_populated, len(taggable_rows))
    relation_rows = [
        r for r in taggable_rows
        if str(r.get("claim_type", "")).strip() in {"theory_link", "inter_article_relation"}
    ]
    edge_type_populated = sum(1 for r in relation_rows if str(r.get("edge_type", "")).strip())
    edge_type_tag_rate = metric_ratio(edge_type_populated, len(relation_rows))

    complete_audits = [
        a for a in audit_rows if str(a.get("status", "")).startswith("completed_pdf_")
    ]
    with_theory = sum(1 for a in complete_audits if int(a.get("theory_link_count", 0) or 0) > 0)
    with_inter_article = sum(1 for a in complete_audits if int(a.get("inter_article_relation_count", 0) or 0) > 0)
    theory_link_paper_coverage = metric_ratio(with_theory, len(complete_audits))
    inter_article_paper_coverage = metric_ratio(with_inter_article, len(complete_audits))

    manual_backlog = len(manual_rows)
    typed_rows = [r for r in queue_rows if str(r.get("article_type_family", "")).strip()]
    typed_metadata = [
        r
        for r in queue_rows
        if str(r.get("article_type_family", "")).strip()
        and str(r.get("article_type_confidence", "")).strip()
        and str(r.get("article_type_margin", "")).strip()
        and str(r.get("article_type_classifier_version", "")).strip()
    ]
    low_conf_typed = sum(
        1 for r in typed_rows if safe_float(r.get("article_type_confidence", 0.0), default=0.0) < 0.60
    )
    needs_review_typed = sum(
        1
        for r in typed_rows
        if str(r.get("article_type_needs_review", "")).strip().lower() in {"1", "true", "yes", "y"}
    )
    # Coverage should be measured on rows where article type is present.
    article_type_metadata_coverage = metric_ratio(len(typed_metadata), len(typed_rows))
    article_type_low_confidence_rate = metric_ratio(low_conf_typed, len(typed_rows))
    article_type_review_rate = metric_ratio(needs_review_typed, len(typed_rows))
    article_type_manual_backlog = len(article_type_review_rows)

    failures: List[str] = []

    if processed and no_claims_rate > thresholds["max_no_claims_rate"]:
        failures.append(
            f"no_claims_rate {no_claims_rate:.4f} > {thresholds['max_no_claims_rate']:.4f}"
        )
    if confirmed_rows and anchor_coverage < thresholds["min_anchor_coverage_global"]:
        failures.append(
            f"anchor_coverage {anchor_coverage:.4f} < {thresholds['min_anchor_coverage_global']:.4f}"
        )
    if confirmed_rows and unresolved_env_rate > thresholds["max_unresolved_environment_rate"]:
        failures.append(
            f"unresolved_environment_rate {unresolved_env_rate:.4f} > {thresholds['max_unresolved_environment_rate']:.4f}"
        )
    if confirmed_rows and unresolved_out_rate > thresholds["max_unresolved_outcome_rate"]:
        failures.append(
            f"unresolved_outcome_rate {unresolved_out_rate:.4f} > {thresholds['max_unresolved_outcome_rate']:.4f}"
        )
    if relation_type_diversity < int(thresholds["min_relation_type_diversity"]):
        failures.append(
            f"relation_type_diversity {relation_type_diversity} < {int(thresholds['min_relation_type_diversity'])}"
        )
    if complete_audits and theory_link_paper_coverage < thresholds["min_theory_link_paper_coverage"]:
        failures.append(
            f"theory_link_paper_coverage {theory_link_paper_coverage:.4f} < {thresholds['min_theory_link_paper_coverage']:.4f}"
        )
    if complete_audits and inter_article_paper_coverage < thresholds["min_inter_article_paper_coverage"]:
        failures.append(
            f"inter_article_paper_coverage {inter_article_paper_coverage:.4f} < {thresholds['min_inter_article_paper_coverage']:.4f}"
        )
    if manual_backlog > int(thresholds["max_manual_review_backlog"]):
        failures.append(
            f"manual_review_backlog {manual_backlog} > {int(thresholds['max_manual_review_backlog'])}"
        )
    # Apply new non-empirical tagging gates only when pipeline has begun producing these tags.
    if taggable_rows and node_type_tag_rate < thresholds["min_node_type_tag_rate"]:
        failures.append(
            f"node_type_tag_rate {node_type_tag_rate:.4f} < {thresholds['min_node_type_tag_rate']:.4f}"
        )
    if relation_rows and edge_type_populated > 0 and edge_type_tag_rate < thresholds["min_edge_type_tag_rate"]:
        failures.append(
            f"edge_type_tag_rate {edge_type_tag_rate:.4f} < {thresholds['min_edge_type_tag_rate']:.4f}"
        )
    if typed_rows and article_type_metadata_coverage < thresholds["min_article_type_metadata_coverage"]:
        failures.append(
            f"article_type_metadata_coverage {article_type_metadata_coverage:.4f} < {thresholds['min_article_type_metadata_coverage']:.4f}"
        )
    if typed_rows and article_type_low_confidence_rate > thresholds["max_article_type_low_confidence_rate"]:
        failures.append(
            f"article_type_low_confidence_rate {article_type_low_confidence_rate:.4f} > {thresholds['max_article_type_low_confidence_rate']:.4f}"
        )
    if typed_rows and article_type_review_rate > thresholds["max_article_type_review_rate"]:
        failures.append(
            f"article_type_review_rate {article_type_review_rate:.4f} > {thresholds['max_article_type_review_rate']:.4f}"
        )
    if resolution_rows and env_missing_match_type_rate > thresholds["max_missing_resolution_match_type_rate"]:
        failures.append(
            f"environment_missing_match_type_rate {env_missing_match_type_rate:.4f} > {thresholds['max_missing_resolution_match_type_rate']:.4f}"
        )
    if resolution_rows and out_missing_match_type_rate > thresholds["max_missing_resolution_match_type_rate"]:
        failures.append(
            f"outcome_missing_match_type_rate {out_missing_match_type_rate:.4f} > {thresholds['max_missing_resolution_match_type_rate']:.4f}"
        )

    print("Extraction quality metrics:")
    print(f"  processed_pdfs: {processed}")
    print(f"  completed_pdf_extracted: {extracted}")
    print(f"  completed_pdf_no_claims: {no_claims}")
    print(f"  no_claims_rate: {no_claims_rate:.4f}")
    print(f"  confirmed_rows: {len(confirmed_rows)}")
    print(f"  resolution_rows: {len(resolution_rows)}")
    print(f"  anchor_coverage: {anchor_coverage:.4f}")
    print(f"  unresolved_environment_rate: {unresolved_env_rate:.4f}")
    print(f"  unresolved_outcome_rate: {unresolved_out_rate:.4f}")
    print(f"  environment_resolution_match_type_counts: {json.dumps(dict(env_match_type_counts), sort_keys=True)}")
    print(f"  outcome_resolution_match_type_counts: {json.dumps(dict(out_match_type_counts), sort_keys=True)}")
    print(f"  environment_llm_fallback_rate: {env_llm_rate:.4f}")
    print(f"  outcome_llm_fallback_rate: {out_llm_rate:.4f}")
    print(f"  environment_semantic_fallback_rate: {env_semantic_rate:.4f}")
    print(f"  outcome_semantic_fallback_rate: {out_semantic_rate:.4f}")
    print(f"  environment_missing_match_type_rate: {env_missing_match_type_rate:.4f}")
    print(f"  outcome_missing_match_type_rate: {out_missing_match_type_rate:.4f}")
    print(f"  relation_type_diversity: {relation_type_diversity}")
    print(f"  taggable_rows: {len(taggable_rows)}")
    print(f"  node_type_tag_rate: {node_type_tag_rate:.4f}")
    print(f"  edge_type_tag_rate: {edge_type_tag_rate:.4f}")
    print(f"  audit_rows: {len(audit_rows)}")
    print(f"  theory_link_paper_coverage: {theory_link_paper_coverage:.4f}")
    print(f"  inter_article_paper_coverage: {inter_article_paper_coverage:.4f}")
    print(f"  manual_review_backlog: {manual_backlog}")
    print(f"  article_type_metadata_coverage: {article_type_metadata_coverage:.4f}")
    print(f"  article_type_typed_rows: {len(typed_rows)}")
    print(f"  article_type_low_confidence_rate: {article_type_low_confidence_rate:.4f}")
    print(f"  article_type_review_rate: {article_type_review_rate:.4f}")
    print(f"  article_type_manual_backlog: {article_type_manual_backlog}")

    if failures:
        print("quality_gate: FAIL")
        for item in failures:
            print(f"  FAIL {item}")
    else:
        print("quality_gate: PASS")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "processed_pdfs": processed,
            "completed_pdf_extracted": extracted,
            "completed_pdf_no_claims": no_claims,
            "no_claims_rate": round(no_claims_rate, 4),
            "confirmed_rows": len(confirmed_rows),
            "resolution_rows": len(resolution_rows),
            "anchor_coverage": round(anchor_coverage, 4),
            "unresolved_environment_rate": round(unresolved_env_rate, 4),
            "unresolved_outcome_rate": round(unresolved_out_rate, 4),
            "environment_resolution_match_type_counts": dict(env_match_type_counts),
            "outcome_resolution_match_type_counts": dict(out_match_type_counts),
            "environment_llm_fallback_rate": round(env_llm_rate, 4),
            "outcome_llm_fallback_rate": round(out_llm_rate, 4),
            "environment_semantic_fallback_rate": round(env_semantic_rate, 4),
            "outcome_semantic_fallback_rate": round(out_semantic_rate, 4),
            "environment_missing_match_type_rate": round(env_missing_match_type_rate, 4),
            "outcome_missing_match_type_rate": round(out_missing_match_type_rate, 4),
            "relation_type_diversity": relation_type_diversity,
            "node_type_tag_rate": round(node_type_tag_rate, 4),
            "edge_type_tag_rate": round(edge_type_tag_rate, 4),
            "theory_link_paper_coverage": round(theory_link_paper_coverage, 4),
            "inter_article_paper_coverage": round(inter_article_paper_coverage, 4),
            "manual_review_backlog": manual_backlog,
            "article_type_metadata_coverage": round(article_type_metadata_coverage, 4),
            "article_type_typed_rows": len(typed_rows),
            "article_type_low_confidence_rate": round(article_type_low_confidence_rate, 4),
            "article_type_review_rate": round(article_type_review_rate, 4),
            "article_type_manual_backlog": article_type_manual_backlog,
        },
        "failures": failures,
        "quality_gate": "FAIL" if failures else "PASS",
    }
    report_path = Path(args.report_json)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"  report_json: {report_path}")

    if args.soft:
        return 0
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
