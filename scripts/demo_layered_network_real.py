#!/usr/bin/env python3
"""
Demo: Layered Network from REAL Extracted Rules
Sprint INT Demo — 2026-02-11

Demonstrates the layered network using actual rules extracted from:
- 85 paper abstracts (DOI-based)
- 12 ceiling height studies (Meyers-Levy, Vartanian)
- 16 spatial/prospect-refuge studies
- 5 theoretical frameworks (ART, SRT, Biophilia, Prospect-Refuge, Ceiling Priming)

Total: 120 beliefs, 30 theory-empirical constraints
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_real_web():
    """Load the actual web of belief from persistence."""
    from src.services.web_accumulator import WebAccumulator

    accumulator = WebAccumulator()
    web, bridge_registry = accumulator.get_master_web()

    print(f"Loaded web with {len(web.beliefs)} beliefs and {len(web.constraints)} constraints")
    return web


def visualize_layered_network(web):
    """Create a text-based visualization of the layered network."""
    print("\n" + "=" * 70)
    print("LAYERED NETWORK VISUALIZATION (REAL DATA)")
    print("=" * 70)

    # Organize beliefs by layer and type
    theories = []
    empirical_by_env = defaultdict(list)
    empirical_by_outcome = defaultdict(list)

    for belief in web.beliefs.values():
        if belief.level.value == 'theoretical':
            theories.append(belief)
        elif belief.environment_id and belief.outcome_id:
            env_category = belief.environment_id.split('.')[0]
            out_category = belief.outcome_id.split('.')[0]
            empirical_by_env[env_category].append(belief)
            empirical_by_outcome[out_category].append(belief)

    # Print theories
    print("""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                     THEORETICAL LAYER (Grounding)                       │
    └─────────────────────────────────────────────────────────────────────────┘""")

    for t in theories:
        theory_name = t.theory_id or t.belief_id
        cred = t.credence.value if hasattr(t.credence, 'value') else t.credence
        print(f"    [{theory_name}] ({cred:.2f}) {t.content[:60]}...")

    # Environment categories
    print("""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                     ENVIRONMENT LAYER (Inputs)                          │
    └─────────────────────────────────────────────────────────────────────────┘""")

    env_counts = {}
    for env_cat, beliefs in empirical_by_env.items():
        env_counts[env_cat] = len(beliefs)
        # Group by specific environment_id
        by_specific = defaultdict(list)
        for b in beliefs:
            by_specific[b.environment_id].append(b)

        print(f"\n    {env_cat.upper()} ({len(beliefs)} beliefs):")
        for env_id, bs in list(by_specific.items())[:3]:
            avg_cred = sum(b.credence.value if hasattr(b.credence, 'value') else b.credence for b in bs) / len(bs)
            print(f"      • {env_id.split('.')[-1]}: {len(bs)} findings (avg credence {avg_cred:.2f})")

    # Outcome categories
    print("""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                      OUTCOME LAYER (Effects)                            │
    └─────────────────────────────────────────────────────────────────────────┘""")

    for out_cat, beliefs in empirical_by_outcome.items():
        by_specific = defaultdict(list)
        for b in beliefs:
            by_specific[b.outcome_id].append(b)

        print(f"\n    {out_cat.upper()} ({len(beliefs)} beliefs):")
        for out_id, bs in list(by_specific.items())[:3]:
            avg_cred = sum(b.credence.value if hasattr(b.credence, 'value') else b.credence for b in bs) / len(bs)
            print(f"      • {out_id.split('.')[-1]}: {len(bs)} findings (avg credence {avg_cred:.2f})")

    # Network statistics
    print("""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                        NETWORK STATISTICS                               │
    └─────────────────────────────────────────────────────────────────────────┘""")

    n_theoretical = len([b for b in web.beliefs.values() if b.level.value == 'theoretical'])
    n_empirical = len([b for b in web.beliefs.values() if b.level.value == 'empirical'])
    n_intermediate = len([b for b in web.beliefs.values() if b.level.value == 'intermediate'])

    print(f"""
    Total Beliefs: {len(web.beliefs)}
      - Theoretical: {n_theoretical}
      - Empirical: {n_empirical}
      - Intermediate: {n_intermediate}

    Total Constraints: {len(web.constraints)}

    Environment Categories: {', '.join(env_counts.keys())}
    """)


def demonstrate_edge_justification(web):
    """Demonstrate edge justification with real data."""
    print("\n" + "=" * 70)
    print("EDGE JUSTIFICATION (REAL DATA)")
    print("=" * 70)

    from src.services.edge_justification import EdgeJustificationService

    service = EdgeJustificationService(web=web)

    # Test edges that should have support in the real data
    test_edges = [
        ("ceiling", "cognition"),      # Ceiling height → cognitive effects
        ("noise", "attention"),        # Noise → attention
        ("noise", "memory"),           # Noise → working memory
        ("biophilic", "stress"),       # Biophilic design → stress
        ("plants", "restoration"),     # Plants → restoration
        ("prospect", "preference"),    # Prospect → preference
        ("daylight", "mood"),          # Daylight → mood
    ]

    for source, target in test_edges:
        print(f"\nEdge: {source} → {target}")
        print("-" * 40)

        j = service.get_justification(source, target)

        print(f"  Status: {j.justification_status.value.upper()}")
        print(f"  Aggregate Credence: {j.aggregate_credence:.2f} ± {j.aggregate_uncertainty:.2f}")
        print(f"  Supporting Beliefs: {len(j.supporting_beliefs)}")

        if j.supporting_beliefs:
            print(f"  Top Evidence:")
            for b in j.supporting_beliefs[:3]:
                print(f"    - {b.content_summary[:70]}... ({b.credence:.2f})")


def demonstrate_gap_prediction(web):
    """Demonstrate gap prediction with real data."""
    print("\n" + "=" * 70)
    print("GAP PREDICTION (REAL DATA)")
    print("=" * 70)

    from src.services.gap_predictor import GapPredictor

    predictor = GapPredictor(web=web)
    report = predictor.find_all_gaps(max_gaps=20)

    print(f"\nTotal Gaps Found: {report.n_gaps}")
    print(f"High Priority: {report.n_high_priority}")

    print(f"\nGap Type Distribution:")
    for gap_type, count in report.summary.get('gap_type_counts', {}).items():
        print(f"  {gap_type}: {count}")

    print(f"\nTop 10 Gaps by VOI:")
    for i, gap in enumerate(report.gaps[:10], 1):
        print(f"\n{i}. [{gap.priority.value.upper()}] {gap.gap_type.value}")
        print(f"   {gap.description[:80]}")
        print(f"   VOI: {gap.voi_score:.2f}")
        print(f"   Suggested: {gap.suggested_search}")


def show_sample_beliefs(web):
    """Show sample beliefs from different categories."""
    print("\n" + "=" * 70)
    print("SAMPLE BELIEFS BY CATEGORY")
    print("=" * 70)

    # Group by source type
    by_source = defaultdict(list)
    for belief in web.beliefs.values():
        if belief.belief_id.startswith('b_abstract_'):
            by_source['abstract'].append(belief)
        elif belief.belief_id.startswith('b_ceiling_'):
            by_source['ceiling'].append(belief)
        elif belief.belief_id.startswith('b_spatial_'):
            by_source['spatial'].append(belief)
        elif belief.belief_id.startswith('b_theory_'):
            by_source['theory'].append(belief)
        else:
            by_source['other'].append(belief)

    for source, beliefs in by_source.items():
        print(f"\n{source.upper()} ({len(beliefs)} beliefs):")
        for b in beliefs[:3]:
            cred = b.credence.value if hasattr(b.credence, 'value') else b.credence
            print(f"  [{cred:.2f}] {b.content[:75]}...")


def main():
    """Run the full demo with real data."""
    print("=" * 70)
    print("ARTICLE EATER: Layered Network Demo (REAL DATA)")
    print("Sprint INT Integration — 2026-02-11")
    print("=" * 70)

    # Load real web
    print("\n1. Loading beliefs from web_persistence.db...")
    web = load_real_web()

    if len(web.beliefs) == 0:
        print("\nERROR: No beliefs found. Run migrate_rules_to_web.py first.")
        return

    # Show sample beliefs
    print("\n2. Sample beliefs by category...")
    show_sample_beliefs(web)

    # Visualize the network
    print("\n3. Visualizing layered network...")
    visualize_layered_network(web)

    # Demonstrate edge justification
    print("\n4. Testing edge justification...")
    demonstrate_edge_justification(web)

    # Demonstrate gap prediction
    print("\n5. Predicting knowledge gaps...")
    demonstrate_gap_prediction(web)

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
