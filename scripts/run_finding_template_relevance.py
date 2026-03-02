#!/usr/bin/env python3
"""Resolve template/theory relevance for findings in Web persistence DB."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.services.finding_template_relevance import (
from src.services.db_locator import get_web_db
    ResolverConfig,
    load_findings_from_web_db,
    load_template_profiles,
    persist_relevance_to_web_db,
    resolve_findings,
    write_resolution_output,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--web-db",
        type=Path,
        default=get_web_db(),
        help="Path to WebOfBelief SQLite DB",
    )
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=Path("data/templates"),
        help="Directory with template JSON files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/production/finding_template_theory_links.json"),
        help="Output JSON path",
    )
    parser.add_argument(
        "--min-template-score",
        type=float,
        default=0.35,
        help="Minimum template relevance score [0,1] to keep",
    )
    parser.add_argument(
        "--top-k-templates",
        type=int,
        default=5,
        help="Maximum candidate templates per finding",
    )
    parser.add_argument(
        "--min-tier-support-score",
        type=float,
        default=0.45,
        help="Minimum template score required to contribute Tier1/Tier2 relevance",
    )
    parser.add_argument(
        "--persist-to-web-db",
        action="store_true",
        help="Persist finding relevance payload into beliefs.epistemic_v2",
    )
    parser.add_argument(
        "--annotation-key",
        type=str,
        default="template_relevance_v1",
        help="JSON key under beliefs.epistemic_v2 used for persisted payload",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = load_findings_from_web_db(args.web_db)
    templates = load_template_profiles(args.templates_dir)
    payload = resolve_findings(
        findings,
        templates,
        ResolverConfig(
            min_template_score=max(0.0, min(1.0, args.min_template_score)),
            top_k_templates=max(1, int(args.top_k_templates)),
            min_tier_support_score=max(0.0, min(1.0, args.min_tier_support_score)),
        ),
    )
    write_resolution_output(payload, args.output)

    summary = payload["summary"]
    print(f"Wrote relevance links: {args.output}")
    print(f"  findings_total: {summary['findings_total']}")
    print(f"  findings_with_template_candidates: {summary['findings_with_template_candidates']}")
    print(f"  findings_with_tier1_relevance: {summary['findings_with_tier1_relevance']}")
    print(f"  unique_templates_linked: {summary['unique_templates_linked']}")
    print(f"  unique_tier2_frameworks_linked: {summary['unique_tier2_frameworks_linked']}")
    print(f"  candidate_template_links_total: {summary['candidate_template_links_total']}")
    print(f"  candidate_template_links_avg: {summary['candidate_template_links_avg']}")
    if args.persist_to_web_db:
        persist_summary = persist_relevance_to_web_db(
            args.web_db,
            payload,
            annotation_key=args.annotation_key,
        )
        print(f"Persisted relevance to: {args.web_db}")
        print(f"  annotation_key: {args.annotation_key}")
        print(f"  updated_beliefs: {persist_summary['updated_beliefs']}")
        print(f"  missing_beliefs: {persist_summary['missing_beliefs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
