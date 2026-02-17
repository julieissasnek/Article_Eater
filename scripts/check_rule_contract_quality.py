#!/usr/bin/env python3
"""
Validate rule-contract quality for PDF-confirmed extraction rows.

Primary goal: detect malformed, misleading, or under-specified rule rows.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


UTC = timezone.utc

VALID_NODE_TYPES = {
    "EMPIRICAL_FINDING",
    "THEORETICAL_PROPOSITION",
    "QUALITATIVE_FINDING",
    "EXPERT_SYNTHESIS",
    "SYNTHESIS_CONCLUSION",
    "CONCEPTUAL_DEFINITION",
    "DERIVED_HYPOTHESIS",
    "KNOWLEDGE_GAP",
    "BRIDGE_WARRANT",
    "METHODOLOGICAL_CRITIQUE",
    "FRAMEWORK_STRUCTURE",
    "CONCEPTUAL_CONSTRAINT",
}

VALID_EDGE_TYPES = {
    "COHERENCE_SUPPORT",
    "COHERENCE_TENSION",
    "ATTRIBUTES_FINDING",
    "INTERPRETS_AS",
    "CONFIRMS_PREDICTION",
    "DISCONFIRMS_PREDICTION",
    "THEORETICALLY_PREDICTS",
    "PROPOSES_MECHANISM",
    "DEFINES_CONSTRUCT",
    "THEORY_TENSION",
    "SUBSUMES_THEORY",
    "INCLUDES_IN_SYNTHESIS",
}

VALID_RELATION_HINTS = {"supports", "contradicts", "explains"}
VALID_EFFECT_DIRECTIONS = {"positive", "negative", "null", "unknown"}
VALID_TABLE_CLAIM_TYPES = {"finding", "sample", "methodology", "effect"}
VALID_DISCOURSE_CLAIM_TYPES = {"theory_link", "inter_article_relation"}
VALID_TRANSLATION_STATUS = {"exact", "fuzzy", "inferred", "noncausal", "untranslatable_noise"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Check rule-contract quality for confirmed rows.")
    p.add_argument(
        "--confirmed-csv",
        type=Path,
        default=Path("data/production/realtime_pdf_confirmed_rows.csv"),
    )
    p.add_argument(
        "--violations-csv",
        type=Path,
        default=Path("data/review/rule_contract_violations.csv"),
    )
    p.add_argument(
        "--report-json",
        type=Path,
        default=Path("data/production/rule_contract_report.json"),
    )
    p.add_argument(
        "--history-jsonl",
        type=Path,
        default=Path("data/production/rule_contract_history.jsonl"),
    )
    p.add_argument("--recent-rows", type=int, default=0, help="Check only most recent N rows (0 = all)")
    p.add_argument("--max-error-rate", type=float, default=0.01)
    p.add_argument("--max-garbled-rate", type=float, default=0.10)
    p.add_argument("--sample-limit", type=int, default=2000, help="Max violations to write to CSV")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def truthy(value: str) -> bool:
    return normalize(value).lower() in {"1", "true", "yes", "y"}


def _to_float(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def is_garbled_statement(text: str) -> bool:
    s = normalize(text)
    if not s:
        return True
    low = s.lower()
    if low.startswith("col_") or "col_1:" in low or "col_2:" in low:
        return True
    letters = sum(ch.isalpha() for ch in s)
    digits = sum(ch.isdigit() for ch in s)
    non_space = sum(not ch.isspace() for ch in s)
    punctuation = sum(not ch.isalnum() and not ch.isspace() for ch in s)
    if letters < 12 and len(s) < 50:
        return True
    if letters > 0 and digits / max(1, letters) > 1.8:
        return True
    if non_space > 0 and punctuation / non_space > 0.35 and len(s) < 80:
        return True
    if re.search(r"\b\d+\.\d+\s+\d+\.\d+\b", s):
        return True
    return False


def iter_rows(path: Path) -> Iterable[Tuple[int, Dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for idx, row in enumerate(r, start=1):
            yield idx, row


def evaluate_row(row: Dict[str, str]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    evidence = normalize(row.get("evidence_level", ""))
    claim_type = normalize(row.get("claim_type", ""))
    node_type = normalize(row.get("node_type", ""))
    edge_type = normalize(row.get("edge_type", ""))
    statement = normalize(row.get("statement", ""))
    provenance = normalize(row.get("provenance_tier", ""))
    relation_hint = normalize(row.get("relation_type_hint", "")).lower()
    effect_direction = normalize(row.get("effect_direction", "")).lower()
    quality_flag = normalize(row.get("quality_flag", ""))
    needs_verification = truthy(row.get("needs_verification", ""))
    translation_status = normalize(row.get("translation_status", "")).lower()
    translation_confidence = _to_float(row.get("translation_confidence", "0"))

    # Core required keys for all rule-like rows.
    for key in ("paper_id", "claim_id", "claim_type", "statement", "node_type", "edge_type", "provenance_tier"):
        if not normalize(row.get(key, "")):
            errors.append(f"missing_{key}")

    if evidence not in {"pdf_table_extracted", "pdf_discourse_extracted"}:
        warnings.append("unexpected_evidence_level")
        return errors, warnings

    if provenance != "pdf_confirmed":
        errors.append("invalid_provenance_tier")

    if node_type and node_type not in VALID_NODE_TYPES:
        errors.append("invalid_node_type")
    if edge_type and edge_type not in VALID_EDGE_TYPES:
        errors.append("invalid_edge_type")

    if evidence == "pdf_table_extracted":
        if claim_type not in VALID_TABLE_CLAIM_TYPES:
            errors.append("invalid_table_claim_type")

        if not translation_status:
            warnings.append("missing_translation_status")
            if claim_type in {"sample", "methodology"}:
                translation_status = "noncausal"
            else:
                env_cid = normalize(row.get("environment_canonical_id", ""))
                out_cid = normalize(row.get("outcome_canonical_id", ""))
                if env_cid.startswith("UNRESOLVED:") and out_cid.startswith("UNRESOLVED:"):
                    translation_status = "untranslatable_noise"
                elif env_cid and out_cid:
                    translation_status = "inferred"
                else:
                    translation_status = "untranslatable_noise"
        elif translation_status not in VALID_TRANSLATION_STATUS:
            errors.append("invalid_translation_status")

        if translation_confidence < 0.0 or translation_confidence > 1.0:
            errors.append("invalid_translation_confidence")

        if translation_status != "noncausal":
            if not normalize(row.get("environment_canonical_id", "")):
                errors.append("missing_environment_canonical_id")
            if not normalize(row.get("outcome_canonical_id", "")):
                errors.append("missing_outcome_canonical_id")

        if effect_direction and effect_direction not in VALID_EFFECT_DIRECTIONS:
            errors.append("invalid_effect_direction")

        if relation_hint and relation_hint not in VALID_RELATION_HINTS:
            errors.append("invalid_relation_type_hint")

        if effect_direction in {"negative", "null"} and edge_type == "CONFIRMS_PREDICTION":
            errors.append("effect_edge_contradiction")
        if effect_direction == "positive" and edge_type == "DISCONFIRMS_PREDICTION":
            errors.append("effect_edge_contradiction")

        garbled = is_garbled_statement(statement)
        if garbled:
            warnings.append("garbled_statement")
            if "garbled_statement" not in quality_flag:
                errors.append("garbled_not_flagged")
            if not needs_verification:
                errors.append("garbled_without_verification")
            if edge_type not in {"INTERPRETS_AS", ""}:
                warnings.append("garbled_with_strong_edge_type")
            if translation_status != "untranslatable_noise":
                warnings.append("garbled_without_noise_status")

    elif evidence == "pdf_discourse_extracted":
        if claim_type not in VALID_DISCOURSE_CLAIM_TYPES:
            errors.append("invalid_discourse_claim_type")
        if claim_type in VALID_DISCOURSE_CLAIM_TYPES and not normalize(row.get("source_quote_hash", "")):
            errors.append("missing_source_quote_hash")

    return errors, warnings


def main() -> int:
    args = parse_args()
    if not args.confirmed_csv.exists():
        raise SystemExit(f"Missing file: {args.confirmed_csv}")

    violations: List[Dict[str, str]] = []
    error_counts: Counter[str] = Counter()
    warning_counts: Counter[str] = Counter()
    evidence_counts: Counter[str] = Counter()

    rows = list(iter_rows(args.confirmed_csv))
    if args.recent_rows > 0:
        rows = rows[-args.recent_rows :]

    scoped_rows = 0
    table_rows = 0
    garbled_rows = 0
    for idx, row in rows:
        evidence = normalize(row.get("evidence_level", ""))
        if evidence not in {"pdf_table_extracted", "pdf_discourse_extracted"}:
            continue
        scoped_rows += 1
        evidence_counts[evidence] += 1
        if evidence == "pdf_table_extracted":
            table_rows += 1

        errors, warnings = evaluate_row(row)
        if "garbled_statement" in warnings:
            garbled_rows += 1

        for code in errors:
            error_counts[code] += 1
            if len(violations) < args.sample_limit:
                violations.append(
                    {
                        "severity": "error",
                        "code": code,
                        "row_index": str(idx),
                        "paper_id": row.get("paper_id", ""),
                        "claim_id": row.get("claim_id", ""),
                        "evidence_level": evidence,
                        "claim_type": row.get("claim_type", ""),
                    }
                )
        for code in warnings:
            warning_counts[code] += 1
            if len(violations) < args.sample_limit:
                violations.append(
                    {
                        "severity": "warning",
                        "code": code,
                        "row_index": str(idx),
                        "paper_id": row.get("paper_id", ""),
                        "claim_id": row.get("claim_id", ""),
                        "evidence_level": evidence,
                        "claim_type": row.get("claim_type", ""),
                    }
                )

    errors_total = sum(error_counts.values())
    error_rate = (errors_total / scoped_rows) if scoped_rows else 0.0
    garbled_rate = (garbled_rows / table_rows) if table_rows else 0.0

    report = {
        "checked_at": datetime.now(tz=UTC).isoformat(),
        "confirmed_csv": str(args.confirmed_csv),
        "scoped_rows": scoped_rows,
        "table_rows": table_rows,
        "evidence_counts": dict(evidence_counts),
        "errors_total": errors_total,
        "warnings_total": sum(warning_counts.values()),
        "error_rate": round(error_rate, 6),
        "garbled_rate_table_rows": round(garbled_rate, 6),
        "error_counts": dict(error_counts),
        "warning_counts": dict(warning_counts),
        "thresholds": {
            "max_error_rate": args.max_error_rate,
            "max_garbled_rate": args.max_garbled_rate,
        },
    }

    failed = False
    failure_reasons: List[str] = []
    if error_rate > float(args.max_error_rate):
        failed = True
        failure_reasons.append("error_rate_above_threshold")
    if table_rows and garbled_rate > float(args.max_garbled_rate):
        failed = True
        failure_reasons.append("garbled_rate_above_threshold")

    report["status"] = "FAIL" if failed else "PASS"
    report["failure_reasons"] = failure_reasons

    # Persist artifacts unless dry-run.
    if not args.dry_run:
        args.violations_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.violations_csv.open("w", encoding="utf-8", newline="") as f:
            fields = ["severity", "code", "row_index", "paper_id", "claim_id", "evidence_level", "claim_type"]
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(violations)

        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

        args.history_jsonl.parent.mkdir(parents=True, exist_ok=True)
        with args.history_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(report) + "\n")

    print(json.dumps(report, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
