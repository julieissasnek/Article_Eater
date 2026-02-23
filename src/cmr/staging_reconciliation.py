"""Utilities for reconciling staging theory links with Tier 2 reductions."""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple


RECONCILIATION_OUTPUT = Path("data/reconciliation/staging_theory_links.json")


def _normalize_theory(theory: str) -> str:
    value = theory.strip()
    if not value:
        return ""
    if "(" in value and ")" in value:
        abbrev = value.split("(")[-1].split(")")[0].strip()
        if len(abbrev) <= 5:
            return abbrev.upper()
    return value.upper()


def _normalize_construct(construct: str) -> str:
    return construct.strip()


def load_reduction_claims(reductions_dir: Path) -> dict[Tuple[str, str], dict[str, Any]]:
    claims: dict[Tuple[str, str], dict[str, Any]] = {}
    for file in sorted(reductions_dir.glob("RC*.json")):
        payload = json.loads(file.read_text(encoding="utf-8"))
        theory = _normalize_theory(payload.get("tier2_theory", ""))
        construct = _normalize_construct(payload.get("tier2_construct", ""))
        if not theory or not construct:
            continue
        claims[(theory, construct)] = {
            "template_mappings": payload.get("template_mappings", []),
            "coverage": payload.get("total_coverage"),
            "irreducible_residual": payload.get("irreducible_residual"),
        }
    return claims


HEURISTIC_KEYWORDS: dict[str, dict[str, list[str]]] = {
    "ART": {
        "Being Away": [
            "being away",
            "retreat",
            "refuge",
            "escap",
            "distance",
            "away from",
            "retreat",
            "restor",
        ],
        "Soft Fascination": [
            "soft fascination",
            "nature",
            "green",
            "view",
            "trees",
            "water",
            "colour",
            "beaut",
            "calming",
            "gentle",
        ],
        "Hard Fascination": [
            "hard fascination",
            "challenge",
            "novelty",
            "disfluency",
            "puzz",
            "complex",
            "surpris",
            "tension",
        ],
        "Extent": [
            "extent",
            "scope",
            "horizon",
            "open",
            "legib",
            "depth",
            "peripher",
            "wayfinding",
        ],
        "Compatibility": [
            "compat",
            "task",
            "goal",
            "purpose",
            "fit",
            "match",
            "privacy",
            "function",
        ],
    },
    "BIOPHILIA": {
        "Nature In Space": [
            "nature",
            "plants",
            "green",
            "forest",
            "landscape",
            "botan",
            "leaf",
            "natural",
        ],
        "Natural Analogues": [
            "wood",
            "stone",
            "water",
            "texture",
            "analogue",
            "biomorphic",
            "earth",
        ],
        "Nature Of Space": [
            "spatial",
            "layout",
            "organ",
            "prospect",
            "refuge",
            "path",
            "enclos",
            "depth",
        ],
        "Remaining Patterns": ["pattern", "modular", "rhythm", "biophilia"],
    },
    "SRT": {
        "Autonomic Stress Reduction": [
            "stress",
            "cortisol",
            "heart rate",
            "parasympathetic",
            "recovery",
            "sympathetic",
        ],
        "Affective Response": [
            "mood",
            "affect",
            "emotion",
            "feeling",
            "positive",
            "negative",
        ],
        "Approach Avoidance": [
            "avoid",
            "approach",
            "safety",
            "threat",
            "danger",
            "comfort",
        ],
    },
}


def guess_construct(theory: str, statement: str) -> Optional[str]:
    theory_key = theory.strip().upper()
    heuristics = HEURISTIC_KEYWORDS.get(theory_key)
    if not heuristics:
        return None
    lower = statement.lower()
    for construct, keywords in heuristics.items():
        for keyword in keywords:
            if keyword and keyword in lower:
                return construct
    # fallback to first construct listed
    return next(iter(heuristics))


@dataclass
class ReconciliationResult:
    line_no: int
    theory: str
    construct: Optional[str]
    status: str
    template_ids: List[str]
    reason: Optional[str]


def _iter_staging_rows(csv_path: Path) -> Iterable[tuple[int, dict[str, str]]]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_no, row in enumerate(reader, start=2):
            theory_name = (row.get("theory_name") or "").strip()
            if not theory_name:
                continue
            yield line_no, row


def reconcile_staging_links(
    csv_path: Path = Path("data/review/tranche80_confirmed_rows.csv"),
    reductions_dir: Path = Path("data/reductions"),
    output_path: Path | None = RECONCILIATION_OUTPUT,
) -> dict[str, Any]:
    reductions = load_reduction_claims(reductions_dir)
    reconciled: List[ReconciliationResult] = []
    unreconciled: List[ReconciliationResult] = []
    counters: Counter[str] = Counter()

    for line_no, row in _iter_staging_rows(csv_path):
        theory_raw = row.get("theory_name", "")
        theory_key = _normalize_theory(theory_raw)
        statement = (row.get("statement") or "").strip()
        construct_guess = guess_construct(theory_key, statement)
        key = (theory_key, construct_guess) if construct_guess else None

        if key and key in reductions:
            template_ids = [m.get("template_id") for m in reductions[key]["template_mappings"] if m.get("template_id")]
            counters[theory_key + ":reconciled"] += 1
            result = ReconciliationResult(
                line_no=line_no,
                theory=theory_key,
                construct=construct_guess,
                status="reconciled",
                template_ids=template_ids,
                reason=None,
            )
            reconciled.append(result)
        else:
            counters[theory_key + ":unreconciled"] += 1
            result = ReconciliationResult(
                line_no=line_no,
                theory=theory_key,
                construct=construct_guess,
                status="unreconciled",
                template_ids=[],
                reason="unknown construct" if not construct_guess else "reduction missing",
            )
            unreconciled.append(result)

    summary = {
        "total": len(reconciled) + len(unreconciled),
        "reconciled": len(reconciled),
        "unreconciled": len(unreconciled),
        "theory_counts": {k: v for k, v in counters.items()},
    }

    payload = {
        "summary": summary,
        "reconciled": [r.__dict__ for r in reconciled],
        "unreconciled": [r.__dict__ for r in unreconciled],
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return summary


def run() -> None:
    summary = reconcile_staging_links()
    print("Reconciled theory links:", summary["reconciled"])
    print("Unreconciled theory links:", summary["unreconciled"])
    print("Total:", summary["total"])


if __name__ == "__main__":
    run()
