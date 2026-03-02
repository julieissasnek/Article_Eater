#!/usr/bin/env python3
"""Persist finding template relevance annotations to web DB.

This script ensures that all findings are annotated with their template
relevance scores in the beliefs.epistemic_v2 field.

Usage:
    python scripts/persist_finding_annotations.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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
        "--annotation-key",
        type=str,
        default="template_relevance_v1",
        help="JSON key under beliefs.epistemic_v2 used for persisted payload",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Load findings and templates
    findings = load_findings_from_web_db(args.web_db)
    templates = load_template_profiles(args.templates_dir)

    # Resolve finding template relevance
    payload = resolve_findings(
        findings,
        templates,
        ResolverConfig(
            min_template_score=max(0.0, min(1.0, args.min_template_score)),
            top_k_templates=max(1, int(args.top_k_templates)),
            min_tier_support_score=max(0.0, min(1.0, args.min_tier_support_score)),
        ),
    )

    # Persist to web DB
    summary = persist_relevance_to_web_db(
        args.web_db,
        payload,
        annotation_key=args.annotation_key,
    )

    print(f"Persisted finding annotations:")
    print(f"  Updated beliefs: {summary['updated_beliefs']}")
    print(f"  Missing beliefs: {summary['missing_beliefs']}")
    print(f"  Annotation key: {args.annotation_key}")
    print(f"  Database: {args.web_db}")

    # Report metrics
    summary_stats = payload.get("summary", {})
    print(f"\nFinding Resolution Summary:")
    print(f"  Findings total: {summary_stats.get('findings_total', 0)}")
    print(f"  With Tier1 relevance: {summary_stats.get('findings_with_tier1_relevance', 0)}")
    print(f"  With Tier2 relevance: {summary_stats.get('findings_with_tier2_relevance', 0)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
