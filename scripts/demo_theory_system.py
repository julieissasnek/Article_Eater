#!/usr/bin/env python3
"""
Article Eater - Theory System Demo
Sprint TH-1 / PG-1-4 Demonstration

Demonstrates:
1. Theory registry bootstrap
2. Theory storage and retrieval
3. Prediction generation for queries
"""

import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.theory_registry import TheoryRegistry
from src.services.prediction_generator import PredictionGenerator, Query
from src.data.theory_bootstrap import get_all_bootstrap_theories, bootstrap_registry


def demo_theory_registry(db_path: str = ":memory:"):
    """Demonstrate theory registry operations."""
    print("=" * 70)
    print("THEORY REGISTRY DEMONSTRATION")
    print("=" * 70)
    
    # Initialize registry
    print("\n1. Initializing theory registry...")
    registry = TheoryRegistry(db_path)
    
    # Bootstrap with initial theories
    print("\n2. Bootstrapping with environmental psychology theories...")
    result = bootstrap_registry(registry)
    
    print(f"   Added {result['theories_added']} theories")
    print(f"   Total predictions: {result['total_predictions']}")
    
    for t in result['added']:
        print(f"   - {t['name']}: {t['n_claims']} claims, {t['n_predictions']} predictions")
    
    if result['errors']:
        print(f"   Errors: {result['errors']}")
    
    # Get statistics
    print("\n3. Registry statistics:")
    stats = registry.get_theory_statistics()
    print(f"   Theories by level: {stats['theories_by_level']}")
    print(f"   Predictions by status: {stats['predictions_by_status']}")
    print(f"   Average theory confidence: {stats['average_theory_confidence']}")
    print(f"   High-VOI predictions (untested, high confidence): {stats['high_voi_predictions']}")
    
    # Retrieve a specific theory
    print("\n4. Retrieving Attention Restoration Theory...")
    art = registry.get_theory("theory:attention_restoration")
    if art:
        print(f"   Name: {art.name}")
        print(f"   Aliases: {art.aliases}")
        print(f"   Level: {art.level.value}")
        print(f"   Confidence: {art.overall_confidence}")
        print(f"   Core claims: {len(art.core_claims)}")
        print(f"   Explicit predictions: {len(art.explicit_predictions)}")
        print(f"   Derived predictions: {len(art.derived_predictions)}")
        
        print("\n   Sample predictions:")
        for pred in art.all_predictions[:3]:
            print(f"   - [{pred.prediction_type.value}] {pred.statement[:80]}...")
            print(f"     Direction: {pred.consequent_direction.value}, Status: {pred.testing_status.value}")
    
    # List all theories
    print("\n5. All registered theories:")
    for theory in registry.list_theories():
        print(f"   - {theory.name} (conf={theory.overall_confidence:.2f}, level={theory.level.value})")
    
    return registry


def demo_prediction_generator(registry: TheoryRegistry):
    """Demonstrate prediction generation."""
    print("\n" + "=" * 70)
    print("PREDICTION GENERATOR DEMONSTRATION")
    print("=" * 70)
    
    generator = PredictionGenerator(registry)
    
    # Query 1: Nature exposure and attention
    print("\n1. Query: Does nature exposure improve attention?")
    print("-" * 50)
    
    query1 = Query(
        query_id="demo:nature:attention",
        independent_variable="nature_exposure",
        dependent_variable="attention_performance",
        environment_type="outdoor",
        temporal_frame="acute",
    )
    
    result1 = generator.generate(query1)
    print_prediction_result(result1)
    
    # Query 2: Noise and stress
    print("\n2. Query: Does chronic noise increase stress?")
    print("-" * 50)
    
    query2 = Query(
        query_id="demo:noise:stress",
        independent_variable="chronic_noise",
        dependent_variable="stress_markers",
        environment_type="office",
        temporal_frame="chronic",
    )
    
    result2 = generator.generate(query2)
    print_prediction_result(result2)
    
    # Query 3: Fractal patterns and aesthetics
    print("\n3. Query: Do fractal patterns affect aesthetic preference?")
    print("-" * 50)
    
    query3 = Query(
        query_id="demo:fractals:aesthetics",
        independent_variable="fractal_patterns",
        dependent_variable="aesthetic_preference",
    )
    
    result3 = generator.generate(query3)
    print_prediction_result(result3)
    
    # Query 4: Something with less theory coverage
    print("\n4. Query: Does ceiling height affect creativity? (less coverage)")
    print("-" * 50)
    
    query4 = Query(
        query_id="demo:ceiling:creativity",
        independent_variable="ceiling_height",
        dependent_variable="creative_performance",
        environment_type="office",
    )
    
    result4 = generator.generate(query4)
    print_prediction_result(result4)


def print_prediction_result(result):
    """Pretty print a prediction result."""
    print(f"\n   Query: {result.query.independent_variable} → {result.query.dependent_variable}")
    
    print(f"\n   Relevant theories ({len(result.relevant_theories)}):")
    for match in result.relevant_theories[:3]:
        print(f"   - {match.theory.name} (relevance={match.relevance_score:.2f})")
        if match.match_reasons:
            print(f"     Reasons: {', '.join(match.match_reasons[:2])}")
    
    print(f"\n   Predictions found: {len(result.predictions_found)}")
    print(f"   Agreement: {result.prediction_agreement}")
    
    print(f"\n   Prior distribution:")
    print(f"   - Type: {result.prior_distribution.prior_type}")
    print(f"   - Mean: {result.prior_distribution.mean:.3f}")
    print(f"   - 95% CI: [{result.prior_distribution.ci_lower:.3f}, {result.prior_distribution.ci_upper:.3f}]")
    print(f"   - Source theories: {len(result.prior_distribution.source_theories)}")
    
    if result.prior_distribution.conflict_flag:
        print("   ⚠️  CONFLICTING PREDICTIONS")
    
    print(f"\n   Overall confidence: {result.overall_confidence.upper()}")
    print(f"   Value of Information (VOI): {result.voi:.2f}")
    
    if result.limiting_factors:
        print(f"   Limiting factors:")
        for factor in result.limiting_factors:
            print(f"   - {factor}")
    
    print(f"\n   Narrative: {result.narrative[:200]}...")


def demo_untested_predictions(registry: TheoryRegistry):
    """Show high-VOI untested predictions."""
    print("\n" + "=" * 70)
    print("HIGH-VOI UNTESTED PREDICTIONS")
    print("=" * 70)
    
    untested = registry.get_untested_predictions(limit=10)
    
    print(f"\nFound {len(untested)} untested predictions:\n")
    
    for pred in untested:
        print(f"• {pred.statement[:70]}...")
        print(f"  Theory: {pred.source_theory_id}")
        print(f"  Prior confidence: {pred.prior_confidence:.2f}")
        print(f"  Outcome: {pred.consequent_outcome}")
        print(f"  Direction: {pred.consequent_direction.value}")
        print()


def main():
    """Run the demo."""
    print("\n" + "=" * 70)
    print("ARTICLE EATER - THEORY SYSTEM DEMO")
    print("Sprint TH-1 (Theory Registry) + PG-1-4 (Prediction Generator)")
    print("=" * 70)
    
    # Use in-memory database for demo
    registry = demo_theory_registry(":memory:")
    
    # Demonstrate prediction generation
    demo_prediction_generator(registry)
    
    # Show untested predictions
    demo_untested_predictions(registry)
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nThe theory system is ready for integration with Article Eater.")
    print("Next steps:")
    print("1. Connect to production database")
    print("2. Integrate with extraction pipeline")
    print("3. Add theory-testing detection to paper extraction")
    print("4. Build frontend for theory exploration")


if __name__ == "__main__":
    main()
