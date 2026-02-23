#!/usr/bin/env python3
"""Validate empirical_v2 extraction payloads for statistical/provenance consistency.

This script is designed for error-mining and parser hardening:
- run on one JSON output or a directory/glob of outputs,
- emit structured issues with stable codes,
- summarize issue frequencies to prioritize fixes.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_INPUT = "data/production/structured_claims.json"
DEFAULT_OUT_REPORT = "data/review/empirical_v2_validation_report.json"
DEFAULT_OUT_ISSUES = "data/review/empirical_v2_validation_issues.jsonl"


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _lower(value: Any) -> str:
    return _norm(value).lower()


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _contains_q_sig(text: str) -> bool:
    return bool(re.search(r"\bq\s*[<=>]\s*0?\.?\d+", _lower(text)))


def _contains_marginal_sig(text: str) -> bool:
    t = _lower(text)
    return bool(re.search(r"\b(marginal|trend|q\s*<\s*0?\.?10|p\s*<\s*0?\.?10)\b", t))


def _contains_numeric_stat_cue(text: str) -> bool:
    t = _lower(text)
    return bool(
        re.search(
            r"\b(beta|β|p|q|t|f|r|η2|eta2|d|g|or|odds ratio)\s*[<=>]\s*[-+]?\d*\.?\d+",
            t,
        )
        or re.search(r"\b(n|sample)\s*[=:\s]\s*\d+\b", t)
    )


def _looks_interaction(iv_raw: str) -> bool:
    t = _norm(iv_raw)
    return bool(
        ("×" in t)
        or re.search(r"\b[xX]\b", t)
        or re.search(r"\binteraction\b", _lower(t))
        or "*" in t
    )


def _has_reverse_scale_note(text: str) -> bool:
    t = _lower(text)
    return bool(
        re.search(
            r"\b(reverse[- ]?coded|reverse score|reverse scale|lower .* = .* more|higher .* = .* less|coding direction)\b",
            t,
        )
    )


def _issue(
    *,
    file_path: str,
    code: str,
    severity: str,
    path: str,
    message: str,
    suggestion: str,
    evidence: str | None = None,
    claim_id: str | None = None,
) -> dict[str, Any]:
    return {
        "file_path": file_path,
        "code": code,
        "severity": severity,
        "path": path,
        "claim_id": claim_id,
        "message": message,
        "suggestion": suggestion,
        "evidence": _norm(evidence) or None,
    }


def _validate_claim(claim: dict[str, Any], idx: int, file_path: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    claim_id = _norm(claim.get("claim_id")) or None
    claim_path = f"claims[{idx}]"
    significance_text = _norm(claim.get("significance_text"))
    evidence_quote = _norm(claim.get("evidence_quote") or claim.get("source_quote"))
    notes = _norm(claim.get("notes"))
    claim_source = _lower(claim.get("claim_source"))
    section = _lower(claim.get("section"))
    provenance = _lower(claim.get("provenance_depth"))

    p_value = claim.get("p_value")
    effect_size = _to_float(claim.get("effect_size"))
    direction = _lower(claim.get("direction"))
    effect_size_type = _lower(claim.get("effect_size_type"))
    is_significant = claim.get("is_significant")
    moderators = claim.get("moderators")
    iv_raw = _norm(claim.get("iv_raw"))

    if _contains_q_sig(significance_text) and p_value is not None:
        issues.append(
            _issue(
                file_path=file_path,
                code="Q_AS_P_VALUE",
                severity="high",
                path=f"{claim_path}.p_value",
                claim_id=claim_id,
                message="q-corrected significance is stored in p_value.",
                suggestion="Add q_value (and correction method), reserve p_value for raw p only.",
                evidence=significance_text,
            )
        )

    if _contains_marginal_sig(significance_text) and is_significant is True:
        issues.append(
            _issue(
                file_path=file_path,
                code="MARGINAL_FLAGGED_SIGNIFICANT",
                severity="medium",
                path=f"{claim_path}.is_significant",
                claim_id=claim_id,
                message="Marginal significance is represented as fully significant.",
                suggestion="Add significance_tier (significant/marginal/ns) and keep threshold policy explicit.",
                evidence=significance_text,
            )
        )

    if claim_source == "abstract":
        if section and section not in {"abstract"}:
            issues.append(
                _issue(
                    file_path=file_path,
                    code="ABSTRACT_SOURCE_SECTION_MISMATCH",
                    severity="high",
                    path=f"{claim_path}.section",
                    claim_id=claim_id,
                    message="claim_source is abstract but section is not Abstract.",
                    suggestion="Set claim_source/provenance to section/fulltext, or constrain fields to abstract evidence only.",
                    evidence=section,
                )
            )
        if provenance and provenance not in {"abstract"}:
            issues.append(
                _issue(
                    file_path=file_path,
                    code="ABSTRACT_SOURCE_PROVENANCE_MISMATCH",
                    severity="high",
                    path=f"{claim_path}.provenance_depth",
                    claim_id=claim_id,
                    message="claim_source is abstract but provenance_depth is not abstract.",
                    suggestion="Align provenance with source, or move claim to section/fulltext source.",
                    evidence=provenance,
                )
            )
        if any(val is not None for val in [p_value, effect_size, claim.get("sample_n")]) and not _contains_numeric_stat_cue(evidence_quote):
            issues.append(
                _issue(
                    file_path=file_path,
                    code="ABSTRACT_NUMERIC_WITHOUT_QUOTE_SUPPORT",
                    severity="medium",
                    path=f"{claim_path}.evidence_quote",
                    claim_id=claim_id,
                    message="Abstract-sourced claim has numeric stats without numeric support in quote.",
                    suggestion="Either add quote with stats or downgrade/remove unsupported numeric fields.",
                    evidence=evidence_quote,
                )
            )

    if effect_size is not None and direction in {"increase", "decrease"} and effect_size_type in {
        "beta",
        "r",
        "cohens_d",
        "hedges_g",
        "d",
        "g",
    }:
        sign_conflict = (effect_size < 0 and direction == "increase") or (effect_size > 0 and direction == "decrease")
        if sign_conflict and not _has_reverse_scale_note(f"{notes} {evidence_quote}"):
            issues.append(
                _issue(
                    file_path=file_path,
                    code="SIGN_DIRECTION_CONFLICT",
                    severity="medium",
                    path=f"{claim_path}.direction",
                    claim_id=claim_id,
                    message="Effect-size sign conflicts with encoded direction and no reverse-scale explanation was found.",
                    suggestion="Add scale-orientation metadata or correct direction/effect-size encoding.",
                    evidence=f"effect_size={effect_size}, direction={direction}",
                )
            )

    if _looks_interaction(iv_raw):
        no_mods = not isinstance(moderators, list) or not [m for m in moderators if _norm(m)]
        if no_mods:
            issues.append(
                _issue(
                    file_path=file_path,
                    code="INTERACTION_WITHOUT_MODERATOR_FIELD",
                    severity="medium",
                    path=f"{claim_path}.moderators",
                    claim_id=claim_id,
                    message="Interaction term appears in iv_raw but moderators field is empty.",
                    suggestion="Populate moderators explicitly or split interaction into iv + moderator + interaction_term fields.",
                    evidence=iv_raw,
                )
            )

    return issues


def _validate_finding(finding: dict[str, Any], idx: int, file_path: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    finding_path = f"empirical_v2_fields.findings[{idx}]"
    significance_text = _norm(finding.get("significance_text"))

    if _contains_q_sig(significance_text) and finding.get("p_value") is not None:
        issues.append(
            _issue(
                file_path=file_path,
                code="Q_AS_P_VALUE",
                severity="high",
                path=f"{finding_path}.p_value",
                message="q-corrected significance is stored in p_value.",
                suggestion="Add q_value (and correction method), reserve p_value for raw p only.",
                evidence=significance_text,
            )
        )
    return issues


def validate_payload(payload: dict[str, Any], file_path: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    claims = payload.get("claims", [])
    if isinstance(claims, list):
        for idx, claim in enumerate(claims):
            if isinstance(claim, dict):
                issues.extend(_validate_claim(claim, idx, file_path))

    findings = (
        payload.get("empirical_v2_fields", {}).get("findings", [])
        if isinstance(payload.get("empirical_v2_fields"), dict)
        else []
    )
    if isinstance(findings, list):
        for idx, finding in enumerate(findings):
            if isinstance(finding, dict):
                issues.extend(_validate_finding(finding, idx, file_path))
    return issues


def _iter_input_files(input_arg: str) -> list[Path]:
    p = Path(input_arg)
    if p.exists() and p.is_file():
        return [p]
    if p.exists() and p.is_dir():
        return sorted(x for x in p.glob("*.json") if x.is_file())
    # fallback to glob
    matches = [Path(x) for x in glob.glob(input_arg)]
    return sorted(x for x in matches if x.is_file())


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate empirical_v2 extraction outputs.")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to JSON file, directory, or glob.")
    parser.add_argument("--out-report", default=DEFAULT_OUT_REPORT)
    parser.add_argument("--out-issues-jsonl", default=DEFAULT_OUT_ISSUES)
    parser.add_argument("--max-examples-per-code", type=int, default=3)
    args = parser.parse_args()

    files = _iter_input_files(args.input)
    all_issues: list[dict[str, Any]] = []
    file_issue_counts: dict[str, int] = {}

    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                all_issues.append(
                    _issue(
                        file_path=str(path),
                        code="INVALID_TOP_LEVEL",
                        severity="high",
                        path="$",
                        message="Top-level JSON is not an object.",
                        suggestion="Ensure output is a JSON object with claims/findings.",
                    )
                )
                file_issue_counts[str(path)] = 1
                continue
            issues = validate_payload(payload, str(path))
            file_issue_counts[str(path)] = len(issues)
            all_issues.extend(issues)
        except Exception as exc:  # pragma: no cover - defensive
            issue = _issue(
                file_path=str(path),
                code="READ_OR_PARSE_ERROR",
                severity="high",
                path="$",
                message=f"Failed to parse JSON: {exc}",
                suggestion="Repair JSON syntax and rerun validation.",
            )
            file_issue_counts[str(path)] = 1
            all_issues.append(issue)

    severity_counts = Counter(i["severity"] for i in all_issues)
    code_counts = Counter(i["code"] for i in all_issues)
    examples_by_code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in all_issues:
        code = issue["code"]
        if len(examples_by_code[code]) < max(1, args.max_examples_per_code):
            examples_by_code[code].append(issue)

    report = {
        "generated_at": _utc_iso(),
        "inputs": [str(p) for p in files],
        "files_validated": len(files),
        "total_issues": len(all_issues),
        "severity_counts": dict(severity_counts),
        "code_counts": dict(code_counts),
        "file_issue_counts": file_issue_counts,
        "pass": severity_counts.get("high", 0) == 0,
        "examples_by_code": dict(examples_by_code),
    }

    out_report = Path(args.out_report)
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    _write_jsonl(Path(args.out_issues_jsonl), all_issues)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

