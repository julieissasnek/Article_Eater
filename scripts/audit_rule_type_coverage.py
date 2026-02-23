#!/usr/bin/env python3
"""Audit rule-type coverage from extracted semantic claims.

Goal:
- detect missing/underrepresented rule types for Web/BN integration
- separate current claim_type labels from inferred candidate rule families
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


KNOWN_RULE_TYPES = {
    "associational",
    "causal",
    "descriptive",
    "moderated",
    "mechanistic",
    "null",
    "finding",
    "effect",
    "methodology",
    "sample",
    "theory_link",
    "inter_article_relation",
    "interaction",
    "constraint",
    "prior",
    "edge",
    "cpd_hint",
}

CANONICAL_RULE_ALIASES = {
    "associational_effect": "associational",
    "causal_effect": "causal",
    "moderated_effect": "moderated",
    "null_finding": "null",
    "mechanistic_explanation": "mechanistic",
    "methodological_constraint": "methodology",
}


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_claims(path: Path) -> list[dict[str, Any]]:
    payload = _load_json(path)
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        claims = payload.get("claims")
        if isinstance(claims, list):
            return [x for x in claims if isinstance(x, dict)]
    return []


def _load_triage_map(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    payload = _load_json(path)
    out: dict[str, str] = {}
    if isinstance(payload, dict):
        papers = payload.get("papers")
        if isinstance(papers, list):
            for row in papers:
                if not isinstance(row, dict):
                    continue
                pid = str(row.get("paper_id") or "").strip()
                fam = str(row.get("article_type_family") or "").strip().lower()
                if pid:
                    out[pid] = fam or "unknown"
            return out
        # map style
        for pid, row in payload.items():
            if not isinstance(row, dict):
                continue
            fam = str(row.get("article_type_family") or "").strip().lower()
            if str(pid).strip():
                out[str(pid).strip()] = fam or "unknown"
    return out


def _guess_rule_type(claim: dict[str, Any]) -> str:
    existing = _norm(claim.get("claim_type"))
    if existing:
        return existing

    iv = _norm(claim.get("iv"))
    dv = _norm(claim.get("dv"))
    source_quote = _norm(claim.get("source_quote"))
    context = _norm(claim.get("context"))
    semantic_type = _norm(claim.get("semantic_type"))
    blob = " ".join(x for x in (source_quote, context, semantic_type) if x)

    if re.search(r"\b(mediat|path model|indirect effect)\b", blob):
        return "mediated_effect"
    if re.search(r"\b(moderat|interaction|depends on|contingent)\b", blob):
        return "moderated_effect"
    if re.search(r"\b(mechanis|pathway|process|mediat)\b", blob):
        return "mechanistic_explanation"
    if re.search(r"\b(non[- ]?significant|null|no effect|ns\b)\b", blob):
        if iv and dv:
            return "null_finding"
    if re.search(r"\b(randomi|experiment|trial|intervention|treatment|causal)\b", blob):
        if iv and dv:
            return "causal_effect"
    if re.search(r"\b(sample|participant|cohort|n=|demograph|population)\b", blob):
        return "population_scope"
    if re.search(r"\b(method|procedure|protocol|measure|instrument)\b", blob):
        return "methodological_constraint"
    if re.search(r"\b(theory|framework|model predicts|hypothesis)\b", blob):
        return "theory_link"
    if re.search(r"\b(et al\.|prior work|consistent with|in line with|contrary to)\b", blob):
        return "inter_article_relation"
    if iv and dv:
        return "associational_effect"
    return "narrative_observation"


def _clip(text: str, limit: int = 180) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    if len(t) <= limit:
        return t
    return t[: limit - 3] + "..."


def _canonical_rule_type(rule_type: str) -> str:
    key = _norm(rule_type)
    if not key:
        return "unknown"
    return CANONICAL_RULE_ALIASES.get(key, key)


def _render_md(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Rule Type Coverage Audit")
    lines.append("")
    lines.append(f"- Claims file: `{summary['claims_path']}`")
    lines.append(f"- Triage file: `{summary.get('triage_path') or 'none'}`")
    lines.append(f"- Total claims: `{summary['total_claims']}`")
    lines.append(f"- Missing explicit claim_type: `{summary['missing_claim_type']}`")
    lines.append("")
    lines.append("## Existing Claim Types")
    for k, v in summary["existing_claim_type_counts"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("## Inferred Candidate Rule Types")
    for k, v in summary["inferred_rule_type_counts"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("## Candidate Missing Rule Types")
    if summary["candidate_missing_rule_types"]:
        for k in summary["candidate_missing_rule_types"]:
            lines.append(f"- `{k}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Coverage by Article Family")
    lines.append("| article_type_family | claims | missing_claim_type | top_inferred_rule_type |")
    lines.append("|---|---:|---:|---|")
    for row in summary["family_coverage"]:
        lines.append(
            f"| {row['article_type_family']} | {row['claims']} | "
            f"{row['missing_claim_type']} | {row['top_inferred_rule_type']} |"
        )
    lines.append("")
    lines.append("## Example Missing-Rule Candidates")
    for row in summary["example_missing_rule_candidates"]:
        lines.append(
            f"- `{row['inferred_rule_type']}` | `{row['paper_id']}` | {row['source_quote']}"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit missing rule types from extracted claims.")
    parser.add_argument("--claims", required=True, help="Path to structured claims JSON")
    parser.add_argument("--triage", default="", help="Optional paper_triage JSON")
    parser.add_argument("--out-json", required=True, help="Output JSON report path")
    parser.add_argument("--out-md", default="", help="Optional markdown report path")
    args = parser.parse_args()

    claims_path = Path(args.claims)
    triage_path = Path(args.triage) if args.triage else None
    out_json = Path(args.out_json)
    out_md = Path(args.out_md) if args.out_md else out_json.with_suffix(".md")

    claims = _load_claims(claims_path)
    triage_map = _load_triage_map(triage_path)

    existing_counts: Counter[str] = Counter()
    inferred_counts: Counter[str] = Counter()
    family_claims: Counter[str] = Counter()
    family_missing: Counter[str] = Counter()
    family_inferred: dict[str, Counter[str]] = defaultdict(Counter)
    missing_examples: list[dict[str, str]] = []
    missing_claim_type = 0

    for claim in claims:
        existing = _norm(claim.get("claim_type"))
        inferred = _guess_rule_type(claim)
        inferred_canonical = _canonical_rule_type(inferred)
        existing_counts[existing or "missing"] += 1
        inferred_counts[inferred_canonical] += 1

        paper_id = str(claim.get("paper_id") or "").strip()
        family = _norm(claim.get("article_type_family")) or _norm(triage_map.get(paper_id)) or "unknown"
        family_claims[family] += 1
        family_inferred[family][inferred_canonical] += 1

        if not existing:
            missing_claim_type += 1
            family_missing[family] += 1

        if inferred_canonical not in KNOWN_RULE_TYPES and len(missing_examples) < 20:
            missing_examples.append(
                {
                    "inferred_rule_type": inferred,
                    "canonical_rule_type": inferred_canonical,
                    "paper_id": paper_id or "unknown",
                    "source_quote": _clip(str(claim.get("source_quote") or claim.get("context") or "")),
                }
            )

    family_rows: list[dict[str, Any]] = []
    for family, count in family_claims.most_common():
        top = family_inferred[family].most_common(1)
        family_rows.append(
            {
                "article_type_family": family,
                "claims": count,
                "missing_claim_type": int(family_missing.get(family, 0)),
                "top_inferred_rule_type": top[0][0] if top else "none",
            }
        )

    candidate_missing = sorted(rt for rt in inferred_counts if rt not in KNOWN_RULE_TYPES)

    summary = {
        "claims_path": str(claims_path),
        "triage_path": str(triage_path) if triage_path else None,
        "total_claims": len(claims),
        "missing_claim_type": missing_claim_type,
        "known_rule_types": sorted(KNOWN_RULE_TYPES),
        "canonical_rule_aliases": CANONICAL_RULE_ALIASES,
        "existing_claim_type_counts": dict(existing_counts.most_common()),
        "inferred_rule_type_counts": dict(inferred_counts.most_common()),
        "candidate_missing_rule_types": candidate_missing,
        "family_coverage": family_rows,
        "example_missing_rule_candidates": missing_examples,
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    out_md.write_text(_render_md(summary), encoding="utf-8")

    print(f"wrote_json={out_json}")
    print(f"wrote_md={out_md}")
    print(f"total_claims={len(claims)}")
    print(f"missing_claim_type={missing_claim_type}")
    print(f"candidate_missing_rule_types={len(candidate_missing)}")


if __name__ == "__main__":
    main()
