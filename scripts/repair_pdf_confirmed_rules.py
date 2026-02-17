#!/usr/bin/env python3
"""
Repair and sanitize rule-like fields in realtime_pdf_confirmed_rows.csv.

Focus:
- Backfill missing statement/node_type/edge_type/verification fields.
- Flag or downgrade garbled table statements to avoid misleading rules.
- Keep output schema stable and write atomically.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Sequence


UTC = timezone.utc

GENERIC_ENV_KEYWORDS = {
    "daylight": ["daylight", "sunlight", "natural light", "illuminance", "lighting", "cct", "luminance"],
    "noise": ["noise", "acoustic", "sound", "db", "dba", "speech"],
    "thermal": ["thermal", "temperature", "humidity", "heat", "cooling", "comfort"],
    "air_quality": ["air quality", "iaq", "co2", "ventilation", "voc", "particulate"],
    "biophilia": ["biophilic", "biophilia", "plants", "green", "nature", "vegetation"],
    "spatial_layout": ["layout", "density", "ceiling", "enclosure", "space syntax", "wayfinding"],
}

GENERIC_OUTCOME_KEYWORDS = {
    "stress": ["stress", "cortisol", "anxiety", "arousal", "tension"],
    "attention": ["attention", "focus", "vigilance", "concentration"],
    "cognition": ["cognitive", "memory", "working memory", "executive", "learning", "accuracy"],
    "productivity": ["productivity", "performance", "efficiency", "task performance"],
    "mood": ["mood", "affect", "emotion", "wellbeing", "well-being", "satisfaction"],
    "sleep": ["sleep", "circadian", "sleepiness", "alertness", "fatigue"],
    "comfort": ["comfort", "thermal comfort", "visual comfort", "acoustic comfort"],
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Repair rule fields in PDF-confirmed rows CSV.")
    p.add_argument(
        "--confirmed-csv",
        type=Path,
        default=Path("data/production/realtime_pdf_confirmed_rows.csv"),
        help="Input/output confirmed rows CSV",
    )
    p.add_argument(
        "--backup",
        action="store_true",
        help="Write a timestamped backup before replacing file",
    )
    p.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help="Optional report path (default: data/production/rule_cleanup_report_<ts>.json)",
    )
    p.add_argument(
        "--recompute-translation",
        action="store_true",
        help="Recompute translation_status/confidence/warnings for all table rows.",
    )
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def now_ts() -> str:
    return datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")


def truthy(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def append_flag(flags: str, flag: str) -> str:
    items = [x.strip() for x in str(flags or "").split("|") if x.strip()]
    if flag not in items:
        items.append(flag)
    return "|".join(items)


def remove_flag(flags: str, flag: str) -> str:
    items = [x.strip() for x in str(flags or "").split("|") if x.strip()]
    kept = [x for x in items if x != flag]
    return "|".join(kept)


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z][a-z0-9_\-]{1,}", normalize(text).lower())


def overlap_ratio(a: str, b: str) -> float:
    ta = set(tokenize(a))
    tb = set(tokenize(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(1, len(ta))


def map_relation_to_edge_type(relation_type: str) -> str:
    rel = str(relation_type or "").strip().lower()
    if rel == "supports":
        return "CONFIRMS_PREDICTION"
    if rel == "contradicts":
        return "DISCONFIRMS_PREDICTION"
    return "COHERENCE_SUPPORT"


def infer_relation_type(effect_direction: str) -> str:
    ed = str(effect_direction or "").strip().lower()
    if ed in {"negative", "null"}:
        return "contradicts"
    if ed == "positive":
        return "explains"
    return "explains"


def infer_node_type(claim_type: str, article_type_family: str) -> str:
    ctype = str(claim_type or "").strip().lower()
    family = str(article_type_family or "").strip().lower()

    if ctype in {"theory_link"}:
        return "THEORETICAL_PROPOSITION"
    if ctype in {"inter_article_relation"}:
        return "EMPIRICAL_FINDING"
    if ctype in {"sample", "methodology", "effect", "finding"}:
        return "EMPIRICAL_FINDING"
    if family in {"meta_analysis", "systematic_review"}:
        return "SYNTHESIS_CONCLUSION"
    if family in {"narrative_review", "thought_piece"}:
        return "EXPERT_SYNTHESIS"
    if family in {"theoretical", "conceptual_framework"}:
        return "THEORETICAL_PROPOSITION"
    return "EMPIRICAL_FINDING"


def infer_translation_status_from_row(row: Dict[str, str]) -> str:
    claim_type = normalize(row.get("claim_type", "")).lower()
    if claim_type in {"sample", "methodology"}:
        return "noncausal"
    quality = normalize(row.get("quality_flag", "")).lower()
    if "garbled_statement" in quality or "auto_reconstructed_from_table" in quality:
        return "untranslatable_noise"

    env_match = normalize(row.get("environment_resolution_match_type", "")).lower()
    out_match = normalize(row.get("outcome_resolution_match_type", "")).lower()
    env_cid = normalize(row.get("environment_canonical_id", ""))
    out_cid = normalize(row.get("outcome_canonical_id", ""))
    env_unresolved = env_cid.startswith("UNRESOLVED:")
    out_unresolved = out_cid.startswith("UNRESOLVED:")
    env_raw = normalize(row.get("environment_variable", ""))
    out_raw = normalize(row.get("outcome_variable", ""))
    low_info = (
        env_raw.startswith("col_")
        or out_raw.startswith("col_")
        or env_raw in {"", "col col", "unspecified_environment"}
        or out_raw in {"", "col col", "unspecified_outcome"}
    )

    if env_match == "exact" and out_match == "exact":
        return "exact"
    if (
        (env_match in {"exact", "fuzzy"} and out_match in {"exact", "fuzzy"})
        and (not env_unresolved)
        and (not out_unresolved)
    ):
        return "fuzzy"
    if env_unresolved and out_unresolved and low_info:
        return "untranslatable_noise"
    return "inferred"


def detect_generic_class(text: str, mapping: Dict[str, List[str]]) -> str:
    norm = normalize(text)
    best = ""
    best_score = 0
    for canonical, keywords in mapping.items():
        score = sum(1 for kw in keywords if normalize(kw) in norm)
        if score > best_score:
            best = canonical
            best_score = score
    return best if best_score > 0 else ""


def _to_float(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def fallback_statement(row: Dict[str, str]) -> str:
    source_quote = normalize(row.get("source_quote", ""))
    justification = normalize(row.get("justification", ""))
    if source_quote:
        return source_quote
    if justification:
        return justification

    env = normalize(row.get("environment_variable", "")) or normalize(row.get("environment_canonical_id", ""))
    out = normalize(row.get("outcome_variable", "")) or normalize(row.get("outcome_canonical_id", ""))
    direction = normalize(row.get("effect_direction", "")) or "unknown"
    if env and out:
        return f"Observed table claim: {env} -> {out} ({direction})."
    return "Observed table claim; manual verification required."


def fallback_discourse_statement(row: Dict[str, str]) -> str:
    source_quote = normalize(row.get("source_quote", ""))
    justification = normalize(row.get("justification", ""))
    if source_quote:
        return source_quote
    if justification:
        return justification
    claim_type = normalize(row.get("claim_type", "")) or "discourse"
    return f"Observed {claim_type} claim from discourse extraction; manual verification required."


def map_discourse_edge_type(claim_type: str, relation_hint: str, argument_relation_type: str) -> str:
    ctype = normalize(claim_type).lower()
    hint = normalize(relation_hint).lower()
    arg_type = normalize(argument_relation_type).lower()

    if hint == "contradicts":
        return "THEORY_TENSION" if ctype == "theory_link" else "COHERENCE_TENSION"
    if hint == "supports":
        return "COHERENCE_SUPPORT"
    if arg_type in {"cites", "mentions"}:
        return "INTERPRETS_AS"
    if ctype == "theory_link":
        return "INTERPRETS_AS"
    return "INTERPRETS_AS"


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

    # OCR-like numeric clusters and fragmented tokens.
    if re.search(r"\b\d+\.\d+\s+\d+\.\d+\b", s):
        return True
    if re.search(r"\b[a-z]{0,2}\d{1,2}\.\d\b", low):
        return True

    return False


def load_rows(path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_rows_atomic(path: Path, fieldnames: Sequence[str], rows: Sequence[Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=str(path.parent))
    try:
        writer = csv.DictWriter(tmp, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)
    finally:
        tmp.close()
    Path(tmp.name).replace(path)


def main() -> int:
    args = parse_args()
    confirmed_csv = args.confirmed_csv
    if not confirmed_csv.exists():
        raise SystemExit(f"Missing file: {confirmed_csv}")

    fieldnames, rows = load_rows(confirmed_csv)
    for col in [
        "statement",
        "node_type",
        "edge_type",
        "needs_verification",
        "quality_flag",
        "argument_relation_type",
        "argument_relation",
        "relation_type_hint",
        "translation_status",
        "translation_confidence",
        "translation_warnings",
        "environment_candidate_scores",
        "outcome_candidate_scores",
    ]:
        if col not in fieldnames:
            fieldnames.append(col)

    stats = {
        "rows_total": len(rows),
        "table_rows_scanned": 0,
        "discourse_rows_scanned": 0,
        "backfilled_statement": 0,
        "backfilled_node_type": 0,
        "backfilled_edge_type": 0,
        "backfilled_needs_verification": 0,
        "backfilled_relation_type_hint": 0,
        "backfilled_argument_relation_type": 0,
        "backfilled_argument_relation": 0,
        "edge_type_normalized_from_relation": 0,
        "garbled_rows_flagged": 0,
        "garbled_rows_sanitized_statement": 0,
        "garbled_rows_sanitized_edge": 0,
        "garbled_rows_sanitized_effect_direction": 0,
        "backfilled_translation_status": 0,
        "backfilled_translation_confidence": 0,
        "backfilled_translation_warnings": 0,
        "backfilled_env_canonical_from_inference": 0,
        "backfilled_out_canonical_from_inference": 0,
        "statement_realigned_to_source_quote": 0,
        "stale_manual_flags_removed": 0,
    }

    for row in rows:
        evidence_level = normalize(row.get("evidence_level", ""))
        if evidence_level not in {"pdf_table_extracted", "pdf_discourse_extracted"}:
            continue

        claim_type = normalize(row.get("claim_type", ""))
        family = normalize(row.get("article_type_family", ""))

        if evidence_level == "pdf_table_extracted":
            stats["table_rows_scanned"] += 1

            # Missing statement backfill.
            if not normalize(row.get("statement", "")):
                row["statement"] = fallback_statement(row)
                stats["backfilled_statement"] += 1

            relation_hint = normalize(row.get("relation_type_hint", ""))
            if not relation_hint:
                relation_hint = infer_relation_type(row.get("effect_direction", ""))
                row["relation_type_hint"] = relation_hint
                stats["backfilled_relation_type_hint"] += 1

            if not normalize(row.get("argument_relation_type", "")):
                row["argument_relation_type"] = "table_claim"
                stats["backfilled_argument_relation_type"] += 1
            if not normalize(row.get("argument_relation", "")):
                row["argument_relation"] = relation_hint
                stats["backfilled_argument_relation"] += 1

            if not normalize(row.get("node_type", "")):
                row["node_type"] = infer_node_type(claim_type, family)
                stats["backfilled_node_type"] += 1

            expected_edge_type = map_relation_to_edge_type(relation_hint)
            if not normalize(row.get("edge_type", "")):
                row["edge_type"] = expected_edge_type
                stats["backfilled_edge_type"] += 1
            else:
                current_edge = normalize(row.get("edge_type", ""))
                if relation_hint == "contradicts" and current_edge != "DISCONFIRMS_PREDICTION":
                    row["edge_type"] = "DISCONFIRMS_PREDICTION"
                    stats["edge_type_normalized_from_relation"] += 1
                elif relation_hint == "supports" and current_edge != "CONFIRMS_PREDICTION":
                    row["edge_type"] = "CONFIRMS_PREDICTION"
                    stats["edge_type_normalized_from_relation"] += 1

            if not normalize(row.get("needs_verification", "")):
                row["needs_verification"] = "true" if truthy(row.get("article_type_needs_review", "")) else "false"
                stats["backfilled_needs_verification"] += 1

            if args.recompute_translation or not normalize(row.get("translation_status", "")):
                row["translation_status"] = infer_translation_status_from_row(row)
                stats["backfilled_translation_status"] += 1
            if args.recompute_translation or not normalize(row.get("translation_confidence", "")):
                conf = 0.0
                if normalize(row.get("translation_status", "")) == "exact":
                    conf = 0.95
                elif normalize(row.get("translation_status", "")) == "fuzzy":
                    conf = 0.78
                elif normalize(row.get("translation_status", "")) == "inferred":
                    conf = 0.45
                elif normalize(row.get("translation_status", "")) == "noncausal":
                    conf = 0.30
                row["translation_confidence"] = f"{conf:.4g}"
                stats["backfilled_translation_confidence"] += 1
            if args.recompute_translation or not normalize(row.get("translation_warnings", "")):
                warnings: List[str] = []
                if normalize(row.get("translation_status", "")) == "noncausal":
                    warnings.append("noncausal_claim_type")
                if normalize(row.get("environment_canonical_id", "")).startswith("UNRESOLVED:"):
                    warnings.append("environment_unresolved")
                if normalize(row.get("outcome_canonical_id", "")).startswith("UNRESOLVED:"):
                    warnings.append("outcome_unresolved")
                if normalize(row.get("translation_status", "")) == "untranslatable_noise":
                    warnings.append("low_information_source")
                row["translation_warnings"] = "|".join(sorted(set(warnings)))
                stats["backfilled_translation_warnings"] += 1

            if normalize(row.get("translation_status", "")) == "inferred":
                infer_text = " ".join(
                    [
                        normalize(row.get("environment_variable", "")),
                        normalize(row.get("outcome_variable", "")),
                        normalize(row.get("statement", "")),
                        normalize(row.get("source_quote", "")),
                    ]
                )

                env_cid = normalize(row.get("environment_canonical_id", ""))
                if env_cid.startswith("UNRESOLVED:"):
                    env_generic = detect_generic_class(infer_text, GENERIC_ENV_KEYWORDS)
                    if env_generic:
                        row["environment_canonical_id"] = f"env.generic.{env_generic}"
                        row["environment_resolution_match_type"] = "generic_keyword"
                        row["environment_resolution_confidence"] = f"{max(_to_float(row.get('environment_resolution_confidence', '0')), 0.42):.4g}"
                        row["translation_warnings"] = append_flag(row.get("translation_warnings", ""), "environment_domain_inferred")
                        stats["backfilled_env_canonical_from_inference"] += 1
                    elif normalize(row.get("environment_variable", "")) not in {"", "unspecified_environment", "col col"}:
                        row["environment_canonical_id"] = "env.inferred.design_factor"
                        row["environment_resolution_match_type"] = "domain_inferred"
                        row["environment_resolution_confidence"] = f"{max(_to_float(row.get('environment_resolution_confidence', '0')), 0.25):.4g}"
                        row["translation_warnings"] = append_flag(row.get("translation_warnings", ""), "environment_domain_inferred")
                        stats["backfilled_env_canonical_from_inference"] += 1

                out_cid = normalize(row.get("outcome_canonical_id", ""))
                if out_cid.startswith("UNRESOLVED:"):
                    out_generic = detect_generic_class(infer_text, GENERIC_OUTCOME_KEYWORDS)
                    if out_generic:
                        row["outcome_canonical_id"] = f"out.generic.{out_generic}"
                        row["outcome_resolution_match_type"] = "generic_keyword"
                        row["outcome_resolution_confidence"] = f"{max(_to_float(row.get('outcome_resolution_confidence', '0')), 0.42):.4g}"
                        row["translation_warnings"] = append_flag(row.get("translation_warnings", ""), "outcome_domain_inferred")
                        stats["backfilled_out_canonical_from_inference"] += 1
                    elif normalize(row.get("outcome_variable", "")) not in {"", "unspecified_outcome", "col col"}:
                        row["outcome_canonical_id"] = "out.inferred.general"
                        row["outcome_resolution_match_type"] = "domain_inferred"
                        row["outcome_resolution_confidence"] = f"{max(_to_float(row.get('outcome_resolution_confidence', '0')), 0.25):.4g}"
                        row["translation_warnings"] = append_flag(row.get("translation_warnings", ""), "outcome_domain_inferred")
                        stats["backfilled_out_canonical_from_inference"] += 1

            if normalize(row.get("translation_status", "")) == "noncausal":
                if normalize(row.get("environment_canonical_id", "")).startswith("UNRESOLVED:"):
                    row["environment_canonical_id"] = "env.noncausal.unspecified"
                    row["environment_resolution_match_type"] = "noncausal"
                    row["environment_resolution_confidence"] = "0.3"
                    stats["backfilled_env_canonical_from_inference"] += 1
                if normalize(row.get("outcome_canonical_id", "")).startswith("UNRESOLVED:"):
                    row["outcome_canonical_id"] = "out.noncausal.unspecified"
                    row["outcome_resolution_match_type"] = "noncausal"
                    row["outcome_resolution_confidence"] = "0.3"
                    stats["backfilled_out_canonical_from_inference"] += 1

            # Fast mapper repair: if statement drifts from informative source quote, realign.
            statement_before = normalize(row.get("statement", ""))
            source_quote = normalize(row.get("source_quote", ""))
            t_status = normalize(row.get("translation_status", ""))
            if (
                source_quote
                and not is_garbled_statement(source_quote)
                and t_status in {"inferred", "fuzzy", "exact"}
            ):
                ov = overlap_ratio(statement_before, source_quote)
                if ov < 0.20 or is_garbled_statement(statement_before):
                    row["statement"] = source_quote
                    stats["statement_realigned_to_source_quote"] += 1

            # Garbled rows: downgrade to safe placeholder and force verification.
            statement = normalize(row.get("statement", ""))
            if is_garbled_statement(statement):
                stats["garbled_rows_flagged"] += 1
                row["quality_flag"] = append_flag(row.get("quality_flag", ""), "garbled_statement")
                row["quality_flag"] = append_flag(row.get("quality_flag", ""), "needs_manual_rule_cleanup")
                row["needs_verification"] = "true"

                if statement != "Table extraction text is low quality; manual verification required.":
                    row["statement"] = "Table extraction text is low quality; manual verification required."
                    stats["garbled_rows_sanitized_statement"] += 1
                if normalize(row.get("edge_type", "")) != "INTERPRETS_AS":
                    row["edge_type"] = "INTERPRETS_AS"
                    stats["garbled_rows_sanitized_edge"] += 1
                if normalize(row.get("effect_direction", "")) != "unknown":
                    row["effect_direction"] = "unknown"
                    stats["garbled_rows_sanitized_effect_direction"] += 1
                # Keep relation hint weakly interpretive, not confirmatory.
                row["relation_type_hint"] = "explains"
                row["translation_status"] = "untranslatable_noise"
                row["translation_confidence"] = "0"
                row["translation_warnings"] = append_flag(row.get("translation_warnings", ""), "low_information_source")
            else:
                # Drop stale cleanup flags for rows that are now non-garbled.
                before_flags = normalize(row.get("quality_flag", ""))
                cleaned = before_flags
                for stale in ("needs_manual_rule_cleanup", "auto_reconstructed_from_table", "auto_denoised_statement"):
                    cleaned = remove_flag(cleaned, stale)
                if cleaned != before_flags:
                    row["quality_flag"] = cleaned
                    stats["stale_manual_flags_removed"] += 1
            continue

        # Discourse row cleanup (legacy rows often lack rule fields).
        stats["discourse_rows_scanned"] += 1

        if not normalize(row.get("statement", "")):
            row["statement"] = fallback_discourse_statement(row)
            stats["backfilled_statement"] += 1

        relation_hint = normalize(row.get("relation_type_hint", ""))
        if not relation_hint:
            arg_relation = normalize(row.get("argument_relation", "")).lower()
            relation_hint = arg_relation if arg_relation in {"supports", "contradicts", "explains"} else "explains"
            row["relation_type_hint"] = relation_hint
            stats["backfilled_relation_type_hint"] += 1

        if not normalize(row.get("argument_relation_type", "")):
            row["argument_relation_type"] = "theory_relation" if claim_type.lower() == "theory_link" else "citation_relation"
            stats["backfilled_argument_relation_type"] += 1
        if not normalize(row.get("argument_relation", "")):
            row["argument_relation"] = relation_hint
            stats["backfilled_argument_relation"] += 1

        if not normalize(row.get("node_type", "")):
            row["node_type"] = infer_node_type(claim_type, family)
            stats["backfilled_node_type"] += 1

        if not normalize(row.get("edge_type", "")):
            row["edge_type"] = map_discourse_edge_type(
                claim_type=claim_type,
                relation_hint=relation_hint,
                argument_relation_type=row.get("argument_relation_type", ""),
            )
            stats["backfilled_edge_type"] += 1

        if not normalize(row.get("needs_verification", "")):
            flagged = "needs_citation_resolution" in normalize(row.get("quality_flag", ""))
            row["needs_verification"] = "true" if flagged or truthy(row.get("article_type_needs_review", "")) else "false"
            stats["backfilled_needs_verification"] += 1

    timestamp = now_ts()
    report_path = args.report_json or Path(f"data/production/rule_cleanup_report_{timestamp}.json")
    report = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "confirmed_csv": str(confirmed_csv),
        "dry_run": bool(args.dry_run),
        "stats": stats,
    }

    if args.dry_run:
        print(json.dumps(report, indent=2))
        return 0

    backup_path = None
    if args.backup:
        backup_path = confirmed_csv.with_name(f"{confirmed_csv.stem}.backup_before_rule_cleanup_{timestamp}{confirmed_csv.suffix}")
        shutil.copy2(confirmed_csv, backup_path)
        report["backup_csv"] = str(backup_path)

    write_rows_atomic(confirmed_csv, fieldnames, rows)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
