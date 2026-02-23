#!/usr/bin/env python3
"""Score field-level and claim-level inaccuracy risk for extracted claims."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extraction.evidence_risk import score_claim_risk


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _default_output_paths(input_path: Path) -> tuple[Path, Path]:
    if input_path.suffix.lower() == ".json":
        base = input_path.with_suffix("")
        return Path(f"{base}.risk_scored.json"), Path(f"{base}.risk_report.json")
    return Path(f"{input_path}.risk_scored.json"), Path(f"{input_path}.risk_report.json")


def _load_claims_payload(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        claims = payload.get("claims")
        if isinstance(claims, list):
            return payload, [c for c in claims if isinstance(c, dict)]
    raise SystemExit(f"Unsupported claims payload schema: {path}")


def _precision_indicators(claims: list[dict[str, Any]]) -> dict[str, int]:
    placeholder_re = re.compile(r"\b(col(?:umn)?[_\s-]*\d+|row[_\s-]*\d+)\b", re.IGNORECASE)
    out = Counter()
    for c in claims:
        iv_raw = _norm(c.get("iv_raw")).lower()
        dv_raw = _norm(c.get("dv_raw")).lower()
        if iv_raw and dv_raw and iv_raw == dv_raw:
            out["iv_raw_equals_dv_raw"] += 1
        if placeholder_re.search(iv_raw) or placeholder_re.search(dv_raw):
            out["placeholder_raw_fields"] += 1
        if _norm(c.get("direction")).lower() == "unknown":
            out["unknown_direction"] += 1
        if not _norm(c.get("evidence_quote") or c.get("source_quote")):
            out["missing_quote"] += 1
    out["total_claims"] = len(claims)
    return dict(out)


def _build_summary(scored_claims: list[dict[str, Any]]) -> dict[str, Any]:
    tiers = Counter(_norm(c.get("claim_risk_tier")).lower() or "unknown" for c in scored_claims)
    reasons = Counter()
    scores = []
    for c in scored_claims:
        s = c.get("claim_risk_score")
        if isinstance(s, (int, float)):
            scores.append(float(s))
        for r in c.get("claim_risk_reasons") or []:
            reasons[_norm(r) or "unknown_reason"] += 1
    return {
        "total_claims": len(scored_claims),
        "claim_risk_mean": round(mean(scores), 4) if scores else 0.0,
        "claim_risk_min": round(min(scores), 4) if scores else 0.0,
        "claim_risk_max": round(max(scores), 4) if scores else 0.0,
        "risk_tier_counts": dict(tiers),
        "risk_tier_pct": {
            k: round(100.0 * v / max(1, len(scored_claims)), 2)
            for k, v in tiers.items()
        },
        "top_risk_reasons": [
            {"reason": k, "count": v}
            for k, v in reasons.most_common(20)
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score claim-level wrong-risk from extraction evidence.")
    parser.add_argument(
        "--input",
        default="data/production/structured_claims.rag_llm_consensus.json",
        help="Input structured claims JSON path.",
    )
    parser.add_argument("--output", default="", help="Annotated output JSON path.")
    parser.add_argument("--report", default="", help="Summary report JSON path.")
    parser.add_argument("--min-risk", type=float, default=0.0, help="Optional filter for report high-risk table.")
    parser.add_argument("--top-n", type=int, default=30, help="Top risky claims to include in report.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    out_default, report_default = _default_output_paths(input_path)
    out_path = Path(args.output) if args.output else out_default
    report_path = Path(args.report) if args.report else report_default

    payload, claims = _load_claims_payload(input_path)
    scored_claims: list[dict[str, Any]] = []
    for claim in claims:
        annotated = dict(claim)
        annotated.update(score_claim_risk(claim))
        scored_claims.append(annotated)

    summary = _build_summary(scored_claims)
    indicators = _precision_indicators(scored_claims)
    risky = [
        {
            "claim_id": c.get("claim_id"),
            "paper_id": c.get("paper_id"),
            "claim_risk_score": c.get("claim_risk_score"),
            "claim_risk_tier": c.get("claim_risk_tier"),
            "direction": c.get("direction"),
            "iv_raw": c.get("iv_raw"),
            "dv_raw": c.get("dv_raw"),
            "claim_risk_reasons": c.get("claim_risk_reasons", [])[:6],
        }
        for c in sorted(scored_claims, key=lambda x: float(x.get("claim_risk_score") or 0.0), reverse=True)
        if float(c.get("claim_risk_score") or 0.0) >= max(0.0, args.min_risk)
    ][: max(1, args.top_n)]

    payload_out = dict(payload)
    payload_out["claims"] = scored_claims
    payload_out["risk_summary"] = {
        **summary,
        "precision_risk_indicators": indicators,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload_out, indent=2), encoding="utf-8")

    report_payload = {
        "input_path": str(input_path),
        "output_path": str(out_path),
        "summary": summary,
        "precision_risk_indicators": indicators,
        "top_risky_claims": risky,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")

    print(json.dumps(report_payload["summary"], indent=2))
    print(f"annotated_output={out_path}")
    print(f"risk_report={report_path}")


if __name__ == "__main__":
    main()
