#!/usr/bin/env python3
"""
Migration Script: Beliefs V23 → V24 (ARCH-4 Formal Epistemic Calculus)

This script migrates existing beliefs from the legacy credence/entrenchment format
to the new rank/warrant/grounding format per ARCH-4 Sprint 1.2.

Migration preserves:
- All legacy data in _legacy field for rollback
- Backward compatibility with v1 consumers
- Dual-format operation per BN_graphical coordination

Reference: docs/ARCH4_MIGRATION_STRATEGY.md

Usage:
    python scripts/migrate_beliefs_to_v24.py [--dry-run] [--input FILE] [--output FILE]

Options:
    --dry-run       Show what would be migrated without writing
    --input FILE    Input web state file (default: data/web_state.json)
    --output FILE   Output file (default: data/web_state_v24.json)
    --rollback      Convert v24 back to v23 format
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.propositional_content import PropositionalContent, ContentType
from src.models.epistemic_status import (
    EpistemicStatus, RankPair, WarrantStatus, DefeatType
)
from src.models.provenance import (
    Provenance, Directness, JustificationStatus, Source, SourceType
)


# ============================================================
# MIGRATION CONFIGURATION
# ============================================================

MAX_FIRMNESS = 5  # Per panel review: cap migrated belief firmness

LEVEL_TO_CONTENT_TYPE = {
    'theoretical': ContentType.THEORETICAL,
    'intermediate': ContentType.CAUSAL_CLAIM,
    'empirical': ContentType.CORRELATIONAL_CLAIM,
    'observational': ContentType.OBSERVATIONAL,
}

LEVEL_TO_DIRECTNESS = {
    'observational': Directness.DIRECT,
    'empirical': Directness.ONE_HOP,
    'intermediate': Directness.MULTI_HOP,
    'theoretical': Directness.THEORETICAL,
}

LEVEL_TO_GROUNDING = {
    'observational': 1.0,
    'empirical': 0.7,
    'intermediate': 0.4,
    'theoretical': 0.2,
}


# ============================================================
# MIGRATION FUNCTIONS
# ============================================================

def credence_to_ranks(credence_value: float, uncertainty: float) -> Tuple[int, int]:
    """
    Convert legacy credence/uncertainty to Spohn rank pair.

    Per migration strategy:
    - credence >= 0.5 → believed (neg_rank > rank)
    - credence < 0.5 → disbelieved (rank > neg_rank)
    - firmness capped at MAX_FIRMNESS for migrated beliefs
    """
    if credence_value >= 0.5:
        strength = credence_value - 0.5
        firmness = int(strength * 10 * (1 - uncertainty))
        firmness = min(MAX_FIRMNESS, firmness)
        return (0, firmness)
    else:
        strength = 0.5 - credence_value
        firmness = int(strength * 10 * (1 - uncertainty))
        firmness = min(MAX_FIRMNESS, firmness)
        return (firmness, 0)


def migrate_belief(legacy_belief: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate a single belief from v23 to v24 format.

    Returns belief with:
    - All legacy fields preserved
    - content_v2: PropositionalContent
    - status_v2: EpistemicStatus (with ranks + warrant)
    - provenance_v2: Provenance (with grounding)
    """
    belief_id = legacy_belief.get('belief_id', '')
    content = legacy_belief.get('content', '')
    level = legacy_belief.get('level', 'empirical').lower()
    status = legacy_belief.get('status', 'stub').lower()

    # Extract credence
    credence_data = legacy_belief.get('credence', {})
    if isinstance(credence_data, dict):
        credence_value = credence_data.get('credence', credence_data.get('value', 0.5))
        uncertainty = credence_data.get('uncertainty', 0.5)
    else:
        credence_value = 0.5
        uncertainty = 0.5

    # 1. Create PropositionalContent
    content_type = LEVEL_TO_CONTENT_TYPE.get(level, ContentType.CAUSAL_CLAIM)
    domain = legacy_belief.get('domain', '')

    content_v2 = PropositionalContent(
        proposition_id=belief_id,
        canonical_form=content,
        content_type=content_type,
        domain=domain or None
    )

    # 2. Create EpistemicStatus
    rank, neg_rank = credence_to_ranks(credence_value, uncertainty)

    # Determine warrant status
    if status == 'stub':
        warrant = WarrantStatus.UNGROUNDED
    elif status in ['tentative', 'established', 'entrenched']:
        warrant = WarrantStatus.WARRANTED
    elif status == 'anomalous':
        # Anomalous beliefs might be contested but still warranted
        warrant = WarrantStatus.WARRANTED
    else:
        warrant = WarrantStatus.WARRANTED

    # Prima facie warrant for observational beliefs
    prima_facie = (level == 'observational')

    status_v2 = EpistemicStatus(
        ranks=RankPair(rank=rank, neg_rank=neg_rank),
        warrant_status=warrant,
        prima_facie_warranted=prima_facie,
        last_computed=datetime.now()
    )

    # 3. Create Provenance
    directness = LEVEL_TO_DIRECTNESS.get(level, Directness.THEORETICAL)
    grounding = LEVEL_TO_GROUNDING.get(level, 0.2)

    # Extract sources from paper_ids
    sources = []
    for paper_id in legacy_belief.get('paper_ids', []):
        sources.append(Source(
            source_type=SourceType.PAPER,
            reference=paper_id
        ))

    provenance_v2 = Provenance(
        sources=sources,
        grounding_score=grounding,
        directness=directness,
        justification_status=JustificationStatus.WELL_JUSTIFIED,
        is_anchor=(level == 'observational')
    )

    # 4. Build migrated belief
    migrated = legacy_belief.copy()
    migrated['content_v2'] = content_v2.to_dict()
    migrated['status_v2'] = status_v2.to_dict()
    migrated['provenance_v2'] = provenance_v2.to_dict()
    migrated['_migration_version'] = '24.0.0'
    migrated['_migration_date'] = datetime.now().isoformat()

    return migrated


def rollback_belief(migrated_belief: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rollback a migrated belief to v23 format.

    Removes v2 fields, preserving legacy data.
    """
    rolled_back = migrated_belief.copy()

    # Remove v2 fields
    for field in ['content_v2', 'status_v2', 'provenance_v2',
                  '_migration_version', '_migration_date']:
        rolled_back.pop(field, None)

    return rolled_back


def migrate_web_state(web_state: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """
    Migrate entire web state from v23 to v24.

    Args:
        web_state: Full web state dictionary
        dry_run: If True, don't modify, just report

    Returns:
        Migrated web state (or original if dry_run)
    """
    beliefs = web_state.get('beliefs', [])
    migrated_count = 0
    error_count = 0
    errors = []

    migrated_beliefs = []
    for belief in beliefs:
        try:
            if dry_run:
                # Just validate migration would work
                migrate_belief(belief)
                migrated_beliefs.append(belief)
            else:
                migrated_beliefs.append(migrate_belief(belief))
            migrated_count += 1
        except Exception as e:
            error_count += 1
            errors.append({
                'belief_id': belief.get('belief_id', 'unknown'),
                'error': str(e)
            })
            # Keep original belief on error
            migrated_beliefs.append(belief)

    print(f"Migration summary:")
    print(f"  Total beliefs: {len(beliefs)}")
    print(f"  Migrated: {migrated_count}")
    print(f"  Errors: {error_count}")

    if errors:
        print(f"\nErrors:")
        for err in errors[:10]:  # Show first 10
            print(f"  - {err['belief_id']}: {err['error']}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    if dry_run:
        return web_state

    result = web_state.copy()
    result['beliefs'] = migrated_beliefs
    result['_format_version'] = '24.0.0'
    result['_migration_date'] = datetime.now().isoformat()

    return result


def rollback_web_state(web_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rollback entire web state from v24 to v23.
    """
    beliefs = web_state.get('beliefs', [])
    rolled_back_beliefs = [rollback_belief(b) for b in beliefs]

    result = web_state.copy()
    result['beliefs'] = rolled_back_beliefs
    result.pop('_format_version', None)
    result.pop('_migration_date', None)

    return result


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='Migrate beliefs from v23 to v24 format (ARCH-4)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Show what would be migrated without writing'
    )
    parser.add_argument(
        '--input', type=str, default='data/web_state.json',
        help='Input web state file'
    )
    parser.add_argument(
        '--output', type=str, default=None,
        help='Output file (default: input file with _v24 suffix)'
    )
    parser.add_argument(
        '--rollback', action='store_true',
        help='Rollback v24 to v23 format'
    )
    parser.add_argument(
        '--in-place', action='store_true',
        help='Modify input file in place (use with caution)'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Determine output path
    if args.in_place:
        output_path = input_path
    elif args.output:
        output_path = Path(args.output)
    else:
        suffix = '_v23' if args.rollback else '_v24'
        output_path = input_path.with_suffix('').with_suffix(f'{suffix}.json')

    # Load web state
    print(f"Loading: {input_path}")
    with open(input_path, 'r') as f:
        web_state = json.load(f)

    # Perform migration or rollback
    if args.rollback:
        print("Rolling back to v23 format...")
        result = rollback_web_state(web_state)
    else:
        print("Migrating to v24 format...")
        result = migrate_web_state(web_state, dry_run=args.dry_run)

    # Write output
    if not args.dry_run:
        print(f"Writing: {output_path}")
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print("Done!")
    else:
        print("Dry run complete. No files modified.")


if __name__ == '__main__':
    main()
