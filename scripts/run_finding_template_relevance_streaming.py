#!/usr/bin/env python3
"""Resolve template/theory relevance for findings with memory-efficient streaming."""

from __future__ import annotations

import argparse
import json
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
        "--output",
        type=Path,
        default=Path("data/production/finding_template_theory_links.json"),
        help="Output JSON path",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Process findings in batches of this size",
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
        default=0.38,
        help="Minimum template score required to contribute Tier1/Tier2 relevance",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("Loading findings...")
    findings = load_findings_from_web_db(args.web_db)
    print(f"Loaded {len(findings)} findings")

    print("Loading templates...")
    templates = load_template_profiles(args.templates_dir)
    print(f"Loaded {len(templates)} templates")

    config = ResolverConfig(
        min_template_score=max(0.0, min(1.0, args.min_template_score)),
        top_k_templates=max(1, int(args.top_k_templates)),
        min_tier_support_score=max(0.0, min(1.0, args.min_tier_support_score)),
    )

    # Process in batches and aggregate results
    print(f"Processing {len(findings)} findings in batches of {args.batch_size}...")
    all_resolutions = []
    unique_templates = set()
    unique_tier2_frameworks = set()
    total_tier1_matches = 0
    total_template_candidates = 0
    total_candidate_links = 0

    for batch_idx, batch_start in enumerate(range(0, len(findings), args.batch_size)):
        batch_end = min(batch_start + args.batch_size, len(findings))
        batch = findings[batch_start:batch_end]

        print(f"  Batch {batch_idx+1}/{(len(findings)-1)//args.batch_size+1}: {batch_start}-{batch_end}...", end=" ", flush=True)

        batch_payload = resolve_findings(batch, templates, config)
        batch_resolutions = batch_payload["resolutions"]

        # Aggregate results
        all_resolutions.extend(batch_resolutions)
        total_tier1_matches += sum(1 for r in batch_resolutions if r.get('tier1_relevance'))
        total_template_candidates += sum(1 for r in batch_resolutions if r.get('top_templates'))

        for resolution in batch_resolutions:
            for template in resolution.get('top_templates', []):
                unique_templates.add(template.get('display_id'))
            for framework in resolution.get('tier2_relevance', {}).keys():
                unique_tier2_frameworks.add(framework)
            total_candidate_links += len(resolution.get('top_templates', []))

        tier2_in_batch = sum(1 for r in batch_resolutions if r.get('tier2_relevance'))
        print(f"{tier2_in_batch}/{len(batch)} have tier2")

        # Free memory for the batch
        del batch_payload

    # Finalize summary
    avg_links = total_candidate_links / len(all_resolutions) if all_resolutions else 0.0

    final_summary = {
        'findings_total': len(all_resolutions),
        'findings_with_template_candidates': total_template_candidates,
        'findings_with_tier1_relevance': total_tier1_matches,
        'unique_templates_linked': len(unique_templates),
        'unique_tier2_frameworks_linked': len(unique_tier2_frameworks),
        'candidate_template_links_total': total_candidate_links,
        'candidate_template_links_avg': round(avg_links, 4),
    }

    # Write output
    payload = {
        "summary": final_summary,
        "resolutions": all_resolutions,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(payload, f, indent=2)

    print(f"\nWrote relevance links: {args.output}")
    print(f"  findings_total: {final_summary['findings_total']}")
    print(f"  findings_with_template_candidates: {final_summary['findings_with_template_candidates']}")
    print(f"  findings_with_tier1_relevance: {final_summary['findings_with_tier1_relevance']}")
    print(f"  unique_templates_linked: {final_summary['unique_templates_linked']}")
    print(f"  unique_tier2_frameworks_linked: {final_summary['unique_tier2_frameworks_linked']}")
    print(f"  candidate_template_links_total: {final_summary['candidate_template_links_total']}")
    print(f"  candidate_template_links_avg: {final_summary['candidate_template_links_avg']}")

    # Calculate tier2 coverage
    tier2_count = sum(1 for r in all_resolutions if r.get('tier2_relevance'))
    tier2_coverage = 100 * tier2_count / len(all_resolutions) if all_resolutions else 0.0
    print(f"  Tier2 coverage: {tier2_coverage:.1f}% ({tier2_count}/{len(all_resolutions)})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
