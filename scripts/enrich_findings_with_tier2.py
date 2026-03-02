#!/usr/bin/env python3
"""
Enrich findings with Tier2 frameworks using Tier1->Tier2 mapping.

Strategy:
1. Load Tier1->Tier2 mapping from tier1_to_tier2_mapping.json
2. For each finding with Tier1 but no Tier2:
   - Look up each Tier1 framework in the mapping
   - Collect all Tier2 frameworks suggested for that Tier1
   - Also check outcome_id-specific Tier2 mappings
   - Assign Tier2 frameworks with confidence based on mapping coverage
3. Report improvement in Tier2 coverage
"""

import json
import os
from collections import defaultdict

def load_tier1_to_tier2_mapping(mapping_path):
    """Load the Tier1->Tier2 mapping."""
    with open(mapping_path) as f:
        data = json.load(f)

    tier1_mapping = data.get('tier1_to_tier2_mapping', {})
    outcome_mapping = data.get('outcome_to_tier2_framework_mapping', {})

    return tier1_mapping, outcome_mapping

def enrich_findings(findings_path, mapping_path, output_path):
    """Enrich findings with Tier2 using Tier1->Tier2 mapping."""

    # Load data
    print(f"Loading findings from {findings_path}...")
    with open(findings_path) as f:
        data = json.load(f)

    resolutions = data['resolutions']
    original_summary = data.get('summary', {})

    print(f"Loading Tier1->Tier2 mapping from {mapping_path}...")
    tier1_mapping, outcome_mapping = load_tier1_to_tier2_mapping(mapping_path)
    print(f"  Loaded {len(tier1_mapping)} Tier1 frameworks")
    print(f"  Loaded {len(outcome_mapping)} outcome mappings")

    # Statistics
    stats = {
        'total_findings': len(resolutions),
        'already_tier2': 0,
        'enriched_via_tier1': 0,
        'enriched_via_outcome': 0,
        'enriched_via_combined': 0,
        'still_no_tier2': 0,
        'with_tier1_only': 0,
    }

    # Process findings
    for i, resolution in enumerate(resolutions):
        if (i + 1) % 500 == 0:
            print(f"  Processing finding {i+1}/{len(resolutions)}...")

        # Skip if already has Tier2
        if resolution.get('tier2_relevance'):
            stats['already_tier2'] += 1
            continue

        tier1 = resolution.get('tier1_relevance', {})
        outcome_id = resolution.get('outcome_id', '')

        if not tier1 and not outcome_id:
            continue

        # Collect candidate Tier2 frameworks
        tier2_candidates = defaultdict(float)

        # Strategy 1: Look up Tier1 frameworks
        if tier1:
            for tier1_fw in tier1.keys():
                if tier1_fw in tier1_mapping:
                    tier2_frameworks = tier1_mapping[tier1_fw]
                    # Weight by Tier1 relevance score
                    tier1_weight = tier1[tier1_fw]
                    for tier2_fw in tier2_frameworks:
                        tier2_candidates[tier2_fw] += tier1_weight / len(tier2_frameworks)

        # Strategy 2: Look up outcome_id
        if outcome_id and outcome_id in outcome_mapping:
            outcome_frameworks = outcome_mapping[outcome_id]
            # Weight outcome mapping less than Tier1 (0.7 factor)
            for tier2_fw in outcome_frameworks:
                tier2_candidates[tier2_fw] += 0.1 / len(outcome_frameworks)

        # If we found any candidates, assign them
        if tier2_candidates:
            tier2_relevance = {
                fw: round(score, 4)
                for fw, score in sorted(
                    tier2_candidates.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            }

            resolution['tier2_relevance'] = tier2_relevance

            # Track source
            if tier1 and outcome_id in outcome_mapping:
                resolution['tier2_source'] = 'tier1_and_outcome'
                stats['enriched_via_combined'] += 1
            elif tier1:
                resolution['tier2_source'] = 'tier1'
                stats['enriched_via_tier1'] += 1
            else:
                resolution['tier2_source'] = 'outcome'
                stats['enriched_via_outcome'] += 1
        else:
            stats['still_no_tier2'] += 1
            if tier1:
                stats['with_tier1_only'] += 1

    # Update summary statistics
    new_tier2_count = (
        stats['already_tier2'] +
        stats['enriched_via_tier1'] +
        stats['enriched_via_outcome'] +
        stats['enriched_via_combined']
    )
    coverage_pct = 100 * new_tier2_count / len(resolutions)

    updated_summary = {
        'findings_total': original_summary.get('findings_total', len(resolutions)),
        'findings_with_template_candidates': original_summary.get('findings_with_template_candidates', 0),
        'findings_with_tier1_relevance': original_summary.get('findings_with_tier1_relevance', 0),
        'findings_with_tier2_relevance': new_tier2_count,
        'tier2_coverage_percent': round(coverage_pct, 1),
        'unique_templates_linked': original_summary.get('unique_templates_linked', 0),
        'unique_tier2_frameworks_linked': original_summary.get('unique_tier2_frameworks_linked', 0),
        'enrichment_strategy': {
            'already_had_tier2': stats['already_tier2'],
            'enriched_via_tier1': stats['enriched_via_tier1'],
            'enriched_via_outcome': stats['enriched_via_outcome'],
            'enriched_via_tier1_and_outcome': stats['enriched_via_combined'],
            'still_no_tier2': stats['still_no_tier2'],
        }
    }

    # Write output
    print(f"\nWriting enriched findings to {output_path}...")
    output_data = {
        'summary': updated_summary,
        'resolutions': resolutions
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Report statistics
    print("\n" + "="*70)
    print("TIER2 ENRICHMENT RESULTS")
    print("="*70)
    print(f"Total findings: {stats['total_findings']}")
    print(f"  Already had Tier2: {stats['already_tier2']} ({100*stats['already_tier2']/stats['total_findings']:.1f}%)")
    print(f"  Enriched via Tier1: {stats['enriched_via_tier1']} ({100*stats['enriched_via_tier1']/stats['total_findings']:.1f}%)")
    print(f"  Enriched via outcome: {stats['enriched_via_outcome']} ({100*stats['enriched_via_outcome']/stats['total_findings']:.1f}%)")
    print(f"  Enriched via Tier1+outcome: {stats['enriched_via_combined']} ({100*stats['enriched_via_combined']/stats['total_findings']:.1f}%)")
    print(f"  Still no Tier2: {stats['still_no_tier2']} ({100*stats['still_no_tier2']/stats['total_findings']:.1f}%)")
    print(f"    (of which with Tier1 only: {stats['with_tier1_only']})")
    print(f"\nOVERALL TIER2 COVERAGE: {new_tier2_count}/{stats['total_findings']} ({coverage_pct:.1f}%)")
    print(f"Previous coverage was: 29.9% (1,460/4,888)")
    print(f"Improvement: +{coverage_pct - 29.9:.1f} percentage points")
    print("="*70)

if __name__ == '__main__':
    repo_root = '/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1'

    findings_path = os.path.join(repo_root, 'data/production/finding_template_theory_links.json')
    mapping_path = os.path.join(repo_root, 'data/tier1_to_tier2_mapping.json')
    output_path = os.path.join(repo_root, 'data/production/finding_template_theory_links_enriched.json')

    enrich_findings(findings_path, mapping_path, output_path)
    print("\nDone!")
