#!/usr/bin/env python3
"""
Load staging theory-link rows into the master Web of Belief constraints table.

Doc 68 Part 4.2 requires loading theory-link staging rows from:
  data/review/tranche80_confirmed_rows.csv
as Tier-2 theory-link constraints.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

# Ensure `src` imports resolve when executed as a script.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.epistemic.edge_types import convert_legacy_constraint_type
from src.services.web_of_belief import (
    Belief,
    BeliefStatus,
    Constraint,
    Credence,
    EpistemicLevel,
)
from src.services.web_persistence import WebPersistenceService


PRIMARY_THEORY_MAP = {
    "ART": "ART",
    "biophilia": "Biophilia",
    "SRT": "SRT",
}


def _parse_strength(row: dict[str, str]) -> float:
    for key in ("relation_strength_hint", "weight"):
        raw = (row.get(key) or "").strip()
        if not raw:
            continue
        try:
            return max(0.0, min(1.0, float(raw)))
        except ValueError:
            continue
    return 0.4


def _theory_id_for_row(theory_name: str) -> str:
    if theory_name in PRIMARY_THEORY_MAP:
        return PRIMARY_THEORY_MAP[theory_name]
    return theory_name.strip()


def _iter_theory_rows(csv_path: Path) -> Iterable[tuple[int, dict[str, str]]]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for line_no, row in enumerate(reader, start=2):  # header is line 1
            theory_name = (row.get("theory_name") or "").strip()
            if theory_name:
                yield line_no, row


def _count_constraints(service: WebPersistenceService, web_id: str) -> tuple[int, set[str]]:
    constraints = service.get_constraints_for_web(web_id)
    ids = {c.constraint_id for c in constraints}
    return len(constraints), ids


def _ensure_belief(
    service: WebPersistenceService,
    web_id: str,
    belief_id: str,
    *,
    content: str,
    level: EpistemicLevel,
    theory_id: str | None = None,
    paper_id: str | None = None,
) -> None:
    if service.load_belief(belief_id, web_id) is not None:
        return
    belief = Belief(
        belief_id=belief_id,
        content=content,
        level=level,
        status=BeliefStatus.STUB,
        credence=Credence(value=0.5, uncertainty=0.5),
        theory_id=theory_id,
        paper_ids=[paper_id] if paper_id else [],
    )
    service.save_belief(web_id, belief)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("data/review/tranche80_confirmed_rows.csv"),
        help="Path to tranche80 confirmed rows CSV.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/web_persistence.db"),
        help="Path to web persistence SQLite DB.",
    )
    parser.add_argument(
        "--expect-before",
        type=int,
        default=25959,
        help="Expected baseline constraint count before loading.",
    )
    parser.add_argument(
        "--expect-new",
        type=int,
        default=1361,
        help="Expected number of newly added constraints.",
    )
    args = parser.parse_args()

    if not args.csv.exists():
        raise FileNotFoundError(f"CSV not found: {args.csv}")
    if not args.db.exists():
        raise FileNotFoundError(f"DB not found: {args.db}")

    service = WebPersistenceService(str(args.db))
    master_web_id = service.create_or_get_master_web()

    before_count, before_ids = _count_constraints(service, master_web_id)
    if args.expect_before is not None and before_count != args.expect_before:
        raise RuntimeError(
            f"Unexpected baseline constraints: {before_count} (expected {args.expect_before})"
        )

    rows = list(_iter_theory_rows(args.csv))
    if len(rows) != args.expect_new:
        raise RuntimeError(
            f"Unexpected theory-link row count: {len(rows)} (expected {args.expect_new})"
        )

    per_theory: Counter[str] = Counter()
    passthrough_theories: Counter[str] = Counter()

    for line_no, row in rows:
        theory_name = (row.get("theory_name") or "").strip()
        theory_id = _theory_id_for_row(theory_name)
        per_theory[theory_id] += 1
        if theory_name not in PRIMARY_THEORY_MAP:
            passthrough_theories[theory_name] += 1

        source_id = (
            (row.get("claim_id") or "").strip()
            or (row.get("node_id") or "").strip()
            or (row.get("source_node_id") or "").strip()
            or f"staging:theory_link:source:{line_no}"
        )
        target_id = f"theory:{theory_id.lower()}"
        paper_id = (row.get("paper_id") or "").strip()
        statement = (row.get("statement") or "").strip()
        edge_type = (row.get("edge_type") or "").strip()

        _ensure_belief(
            service,
            master_web_id,
            source_id,
            content=statement or source_id,
            level=EpistemicLevel.EMPIRICAL,
            theory_id=theory_id,
            paper_id=paper_id or None,
        )
        _ensure_belief(
            service,
            master_web_id,
            target_id,
            content=f"Tier 2 theory construct: {theory_id}",
            level=EpistemicLevel.THEORETICAL,
            theory_id=theory_id,
        )

        constraint = Constraint(
            constraint_id=f"tier2_theory_link:{line_no}",
            source_id=source_id,
            target_id=target_id,
            constraint_type=convert_legacy_constraint_type(edge_type or "coherence_support"),
            strength=_parse_strength(row),
            bidirectional=False,
            evidence_ids=[source_id, paper_id],
        )
        # Preserve explicit Tier-2 theory-link label from contract mapping.
        constraint.warrant_type = "tier2_theory_link"  # type: ignore[attr-defined]
        constraint.provenance = json.dumps(  # type: ignore[attr-defined]
            {
                "loader": "scripts/load_tranche80_theory_links.py",
                "source_csv": str(args.csv),
                "row_line_number": line_no,
                "theory_name": theory_name,
                "theory_id": theory_id,
                "constraint_type": "tier2_theory_link",
                "edge_type": edge_type,
                "paper_id": paper_id,
            },
            sort_keys=True,
        )
        service.save_constraint(master_web_id, constraint)

    after_count, after_ids = _count_constraints(service, master_web_id)
    added = after_count - before_count

    if not before_ids.issubset(after_ids):
        raise RuntimeError("Existing constraints were altered or removed.")
    if added != args.expect_new:
        raise RuntimeError(
            f"Constraint delta mismatch: +{added} (expected +{args.expect_new})"
        )

    print(f"Master web: {master_web_id}")
    print(f"Before constraints: {before_count}")
    print(f"After constraints:  {after_count}")
    print(f"New constraints:    {added}")
    print("Per-theory loaded:")
    for theory_id, count in sorted(per_theory.items()):
        print(f"  - {theory_id}: {count}")
    if passthrough_theories:
        print("Passthrough theory_name rows (outside explicit ART/Biophilia/SRT map):")
        for theory_name, count in sorted(passthrough_theories.items()):
            print(f"  - {theory_name}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
