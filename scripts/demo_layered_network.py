#!/usr/bin/env python3
"""
Demo: Layered Network from Extracted Rules
Sprint INT Demo — 2026-02-11

Demonstrates:
1. Creating beliefs from paper abstracts
2. Building the epistemic web
3. Connecting to BN structure
4. Visualizing as a layered network
5. Finding gaps and justifications

This script populates test data and shows the integration working.
"""

import sys
from pathlib import Path
import json
from datetime import datetime, timezone

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def create_demo_beliefs():
    """
    Create demo beliefs simulating extraction from paper abstracts.

    These beliefs represent findings from environmental psychology papers.
    """
    from src.services.web_of_belief import (
        WebOfBelief, Belief, Credence, EpistemicLevel, BeliefStatus,
        Constraint, ConstraintType
    )

    web = WebOfBelief()

    # =========================================================================
    # Layer 1: Environment → Mediator Beliefs (from empirical papers)
    # =========================================================================

    # Daylight research
    web.add_belief(Belief(
        belief_id="b_daylight_circadian_001",
        content="Natural daylight exposure regulates circadian rhythm, improving alertness",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.85, 0.12),
        paper_ids=["boyce_2003"],
        environment_id="sensory.light.natural",
        outcome_id="cog.alertness",
        tags=["setting:office", "theory:circadian"]
    ))

    web.add_belief(Belief(
        belief_id="b_daylight_mood_001",
        content="Daylight exposure correlates with improved mood states in office workers",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.78, 0.15),
        paper_ids=["edwards_2002"],
        environment_id="sensory.light.natural",
        outcome_id="affect.mood",
        tags=["setting:office"]
    ))

    # Plants/biophilia research
    web.add_belief(Belief(
        belief_id="b_plants_restoration_001",
        content="Indoor plants increase perceived restorativeness of office environments",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.75, 0.18),
        paper_ids=["lohr_1996"],
        environment_id="natural.vegetation",
        outcome_id="psych.restoration",
        tags=["setting:office", "theory:biophilia"]
    ))

    web.add_belief(Belief(
        belief_id="b_plants_stress_001",
        content="Presence of plants reduces reported stress levels",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.72, 0.20),
        paper_ids=["dijkstra_2008"],
        environment_id="natural.vegetation",
        outcome_id="psych.stress",
        tags=["setting:office", "setting:healthcare"]
    ))

    # Nature view research
    web.add_belief(Belief(
        belief_id="b_view_recovery_001",
        content="Views of nature accelerate recovery from stress and mental fatigue",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.82, 0.14),
        paper_ids=["ulrich_1984"],
        environment_id="natural.view",
        outcome_id="psych.stress",
        tags=["setting:healthcare", "theory:SRT"]
    ))

    # Noise research
    web.add_belief(Belief(
        belief_id="b_noise_cognitive_001",
        content="Background noise above 55dB increases cognitive load and impairs concentration",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.80, 0.12),
        paper_ids=["banbury_1998"],
        environment_id="sensory.noise",
        outcome_id="cog.load",
        tags=["setting:office"]
    ))

    # =========================================================================
    # Layer 2: Mediator → Outcome Beliefs
    # =========================================================================

    web.add_belief(Belief(
        belief_id="b_alertness_productivity_001",
        content="Increased alertness leads to higher productivity in cognitive tasks",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.76, 0.16),
        paper_ids=["kaida_2006"],
        environment_id="cog.alertness",
        outcome_id="perf.productivity",
        tags=["setting:office"]
    ))

    web.add_belief(Belief(
        belief_id="b_stress_focus_001",
        content="Lower stress levels enable better focus and sustained attention",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.74, 0.18),
        paper_ids=["hockey_1997"],
        environment_id="psych.stress",
        outcome_id="cog.attention",
        tags=["setting:office"]
    ))

    web.add_belief(Belief(
        belief_id="b_restoration_satisfaction_001",
        content="Perceived restorativeness increases workplace satisfaction",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.70, 0.20),
        paper_ids=["kaplan_1995"],
        environment_id="psych.restoration",
        outcome_id="psych.satisfaction",
        tags=["setting:office", "theory:ART"]
    ))

    # =========================================================================
    # Theoretical Beliefs (mechanism explanations)
    # =========================================================================

    web.add_belief(Belief(
        belief_id="b_art_theory_001",
        content="Attention Restoration Theory: Natural environments restore directed attention capacity",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.80, 0.15),
        paper_ids=["kaplan_1989"],
        theory_id="ART",
        tags=["theory:ART"]
    ))

    web.add_belief(Belief(
        belief_id="b_srt_theory_001",
        content="Stress Recovery Theory: Nature exposure triggers parasympathetic response reducing stress",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.78, 0.16),
        paper_ids=["ulrich_1991"],
        theory_id="SRT",
        tags=["theory:SRT"]
    ))

    # =========================================================================
    # Add Constraints (support relationships)
    # =========================================================================

    # Theory supports empirical findings
    web.add_constraint(Constraint(
        constraint_id="c_art_plants",
        source_id="b_art_theory_001",
        target_id="b_plants_restoration_001",
        constraint_type=ConstraintType.EXPLAINS,
        strength=0.7
    ))
    web.add_constraint(Constraint(
        constraint_id="c_srt_view",
        source_id="b_srt_theory_001",
        target_id="b_view_recovery_001",
        constraint_type=ConstraintType.EXPLAINS,
        strength=0.8
    ))
    web.add_constraint(Constraint(
        constraint_id="c_srt_plants",
        source_id="b_srt_theory_001",
        target_id="b_plants_stress_001",
        constraint_type=ConstraintType.EXPLAINS,
        strength=0.6
    ))

    # Empirical beliefs support each other
    web.add_constraint(Constraint(
        constraint_id="c_mood_circadian",
        source_id="b_daylight_mood_001",
        target_id="b_daylight_circadian_001",
        constraint_type=ConstraintType.SUPPORTS,
        strength=0.5
    ))
    web.add_constraint(Constraint(
        constraint_id="c_alertness_daylight",
        source_id="b_alertness_productivity_001",
        target_id="b_daylight_circadian_001",
        constraint_type=ConstraintType.SUPPORTS,
        strength=0.4
    ))

    return web


def demonstrate_edge_justification(web):
    """Demonstrate edge justification service."""
    print("\n" + "="*70)
    print("EDGE JUSTIFICATION DEMO")
    print("="*70)

    from src.services.edge_justification import EdgeJustificationService

    service = EdgeJustificationService(web=web)

    # Test a few edges
    test_edges = [
        ("daylight", "stress"),
        ("plants", "restoration"),
        ("noise", "focus"),
        ("unknown_var", "unknown_target"),  # Should be unjustified
    ]

    for source, target in test_edges:
        print(f"\nEdge: {source} → {target}")
        print("-" * 40)

        j = service.get_justification(source, target)

        print(f"  Status: {j.justification_status.value.upper()}")
        print(f"  Aggregate Credence: {j.aggregate_credence:.2f} ± {j.aggregate_uncertainty:.2f}")
        print(f"  Supporting Beliefs: {len(j.supporting_beliefs)}")
        print(f"  Conflicting Beliefs: {len(j.conflicting_beliefs)}")

        if j.supporting_beliefs:
            print(f"  Top Evidence:")
            for b in j.supporting_beliefs[:2]:
                print(f"    - {b.content_summary[:60]}... ({b.credence:.2f})")


def demonstrate_gap_prediction(web):
    """Demonstrate gap prediction."""
    print("\n" + "="*70)
    print("GAP PREDICTION DEMO")
    print("="*70)

    from src.services.gap_predictor import GapPredictor

    predictor = GapPredictor(web=web)
    report = predictor.find_all_gaps(max_gaps=10)

    print(f"\nTotal Gaps Found: {report.n_gaps}")
    print(f"High Priority: {report.n_high_priority}")
    print(f"\nGap Type Distribution:")
    for gap_type, count in report.summary.get('gap_type_counts', {}).items():
        print(f"  {gap_type}: {count}")

    print(f"\nTop Gaps by VOI:")
    for i, gap in enumerate(report.gaps[:5], 1):
        print(f"\n{i}. [{gap.priority.value.upper()}] {gap.gap_type.value}")
        print(f"   {gap.description}")
        print(f"   VOI: {gap.voi_score:.2f}")
        print(f"   Suggested Search: {gap.suggested_search}")


def visualize_layered_network(web):
    """Create a text-based visualization of the layered network."""
    print("\n" + "="*70)
    print("LAYERED NETWORK VISUALIZATION")
    print("="*70)

    # Organize beliefs by layer
    layer1_env = []  # Environment factors
    layer2_med = []  # Mediators
    layer3_out = []  # Outcomes
    theories = []

    for belief in web.beliefs.values():
        if belief.level.value == 'theoretical':
            theories.append(belief)
        elif belief.environment_id and belief.outcome_id:
            # Classify by what it connects
            env = belief.environment_id.split('.')[0]
            out = belief.outcome_id.split('.')[0]

            if env in ['sensory', 'natural', 'spatial']:
                if out in ['cog', 'psych', 'affect']:
                    layer1_env.append(belief)
                elif out in ['perf']:
                    layer2_med.append(belief)
            elif env in ['cog', 'psych', 'affect']:
                layer3_out.append(belief)

    print("""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                          LAYERED NETWORK                                │
    │                                                                         │
    │  THEORIES (Grounding)                                                   │
    │  ═══════════════════                                                    │""")

    for t in theories[:3]:
        print(f"    │  • {t.content[:65]}...")

    print("""    │                                                                         │
    │  LAYER 1: Environment → Mediators                                       │
    │  ═════════════════════════════════                                      │""")

    for b in layer1_env[:4]:
        env = b.environment_id.split('.')[-1] if b.environment_id else "?"
        out = b.outcome_id.split('.')[-1] if b.outcome_id else "?"
        cred = b.credence.value if hasattr(b.credence, 'value') else b.credence
        print(f"    │  [{env}] ──({cred:.2f})──► [{out}]")

    print("""    │                                                                         │
    │  LAYER 2: Mediators → Outcomes                                          │
    │  ═════════════════════════════                                          │""")

    for b in layer2_med[:4]:
        env = b.environment_id.split('.')[-1] if b.environment_id else "?"
        out = b.outcome_id.split('.')[-1] if b.outcome_id else "?"
        cred = b.credence.value if hasattr(b.credence, 'value') else b.credence
        print(f"    │  [{env}] ──({cred:.2f})──► [{out}]")

    print("""    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘
    """)

    # Summary statistics
    print(f"Network Statistics:")
    print(f"  Total Beliefs: {len(web.beliefs)}")
    print(f"  Total Constraints: {len(web.constraints)}")
    print(f"  Theories: {len(theories)}")
    print(f"  Empirical Beliefs: {len([b for b in web.beliefs.values() if b.level.value == 'empirical'])}")


def main():
    """Run the full demo."""
    print("="*70)
    print("ARTICLE EATER: Layered Network Demo")
    print("Sprint INT Integration — 2026-02-11")
    print("="*70)

    # Create demo beliefs
    print("\n1. Creating beliefs from paper abstracts...")
    web = create_demo_beliefs()
    print(f"   Created {len(web.beliefs)} beliefs and {len(web.constraints)} constraints")

    # Visualize the network
    print("\n2. Visualizing layered network...")
    visualize_layered_network(web)

    # Demonstrate edge justification
    print("\n3. Testing edge justification...")
    demonstrate_edge_justification(web)

    # Demonstrate gap prediction
    print("\n4. Predicting knowledge gaps...")
    demonstrate_gap_prediction(web)

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
