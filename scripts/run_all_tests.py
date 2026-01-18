#!/usr/bin/env python3
"""
Article Eater - Theory System Test Runner
Runs all tests and provides detailed diagnostics.

Usage:
    python scripts/run_all_tests.py           # Run all tests
    python scripts/run_all_tests.py --quick   # Quick smoke test only
    python scripts/run_all_tests.py --verbose # Verbose output
"""

import sys
import os
import argparse
import traceback
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def colored(text, color):
    return f"{color}{text}{Colors.RESET}"

def test_imports():
    """Test that all modules can be imported."""
    print("\n" + "="*60)
    print(colored("1. TESTING IMPORTS", Colors.BLUE))
    print("="*60)
    
    modules = [
        ("Theory Models", "src.models.theory_models"),
        ("Theory Registry", "src.services.theory_registry"),
        ("Prediction Generator", "src.services.prediction_generator"),
        ("Theory Bootstrap", "src.data.theory_bootstrap"),
    ]
    
    results = []
    for name, module in modules:
        try:
            __import__(module)
            print(f"  {colored('✓', Colors.GREEN)} {name}")
            results.append(True)
        except Exception as e:
            print(f"  {colored('✗', Colors.RED)} {name}: {e}")
            results.append(False)
    
    return all(results)

def test_registry():
    """Test theory registry operations."""
    print("\n" + "="*60)
    print(colored("2. TESTING THEORY REGISTRY", Colors.BLUE))
    print("="*60)
    
    from src.services.theory_registry import TheoryRegistry
    from src.data.theory_bootstrap import bootstrap_registry
    
    results = []
    
    # Test initialization
    try:
        registry = TheoryRegistry(":memory:")
        print(f"  {colored('✓', Colors.GREEN)} Registry initialization")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Registry initialization: {e}")
        return False
    
    # Test bootstrap
    try:
        result = bootstrap_registry(registry)
        assert result['theories_added'] == 6, f"Expected 6 theories, got {result['theories_added']}"
        assert result['total_predictions'] >= 20, f"Expected 20+ predictions"
        print(f"  {colored('✓', Colors.GREEN)} Bootstrap: {result['theories_added']} theories, {result['total_predictions']} predictions")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Bootstrap: {e}")
        results.append(False)
    
    # Test retrieval
    try:
        theory = registry.get_theory("theory:attention_restoration")
        assert theory is not None
        assert theory.name == "Attention Restoration Theory"
        print(f"  {colored('✓', Colors.GREEN)} Theory retrieval: {theory.name}")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Theory retrieval: {e}")
        results.append(False)
    
    # Test listing
    try:
        theories = registry.list_theories()
        assert len(theories) == 6
        print(f"  {colored('✓', Colors.GREEN)} Theory listing: {len(theories)} theories")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Theory listing: {e}")
        results.append(False)
    
    # Test statistics
    try:
        stats = registry.get_theory_statistics()
        assert 'theories_by_level' in stats
        print(f"  {colored('✓', Colors.GREEN)} Statistics: {stats['theories_by_level']}")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Statistics: {e}")
        results.append(False)
    
    return all(results)

def test_prediction_generator():
    """Test prediction generator."""
    print("\n" + "="*60)
    print(colored("3. TESTING PREDICTION GENERATOR", Colors.BLUE))
    print("="*60)
    
    from src.services.theory_registry import TheoryRegistry
    from src.services.prediction_generator import PredictionGenerator, Query
    from src.data.theory_bootstrap import bootstrap_registry
    
    results = []
    
    # Initialize
    registry = TheoryRegistry(":memory:")
    bootstrap_registry(registry)
    generator = PredictionGenerator(registry)
    
    # Test query with matches
    try:
        query = Query(
            query_id="test:1",
            independent_variable="nature_exposure",
            dependent_variable="attention_performance"
        )
        result = generator.generate(query)
        assert result.overall_confidence in ['very_low', 'low', 'medium', 'high', 'very_high']
        assert len(result.relevant_theories) > 0
        print(f"  {colored('✓', Colors.GREEN)} Query with matches: confidence={result.overall_confidence}, theories={len(result.relevant_theories)}")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Query with matches: {e}")
        results.append(False)
    
    # Test query without matches
    try:
        query = Query(
            query_id="test:2",
            independent_variable="unknown_factor",
            dependent_variable="unknown_outcome"
        )
        result = generator.generate(query)
        assert result.overall_confidence == 'very_low'
        print(f"  {colored('✓', Colors.GREEN)} Query without matches: confidence={result.overall_confidence}")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Query without matches: {e}")
        results.append(False)
    
    # Test prior distribution
    try:
        query = Query(
            query_id="test:3",
            independent_variable="chronic_noise",
            dependent_variable="stress_markers"
        )
        result = generator.generate(query)
        assert result.prior_distribution is not None
        assert hasattr(result.prior_distribution, 'mean')
        print(f"  {colored('✓', Colors.GREEN)} Prior distribution: type={result.prior_distribution.prior_type}, mean={result.prior_distribution.mean:.2f}")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Prior distribution: {e}")
        results.append(False)
    
    # Test VOI calculation
    try:
        assert 0 <= result.voi <= 1
        print(f"  {colored('✓', Colors.GREEN)} VOI calculation: {result.voi:.3f}")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} VOI calculation: {e}")
        results.append(False)
    
    return all(results)

def test_theory_search():
    """Test Article Finder integration."""
    print("\n" + "="*60)
    print(colored("4. TESTING ARTICLE FINDER INTEGRATION", Colors.BLUE))
    print("="*60)
    
    results = []
    
    # Try to import Article Finder components
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "article_finder"))
        from knowledge.theory_search import TheoryAwareSearch, create_theory_search
        print(f"  {colored('✓', Colors.GREEN)} Article Finder imports")
        results.append(True)
    except ImportError as e:
        print(f"  {colored('⚠', Colors.YELLOW)} Article Finder not available: {e}")
        print("     (This is OK if running standalone)")
        return True  # Not a failure
    
    from src.services.theory_registry import TheoryRegistry
    from src.data.theory_bootstrap import bootstrap_registry
    
    # Initialize
    registry = TheoryRegistry(":memory:")
    bootstrap_registry(registry)
    
    try:
        search = TheoryAwareSearch(registry)
        print(f"  {colored('✓', Colors.GREEN)} TheoryAwareSearch initialization")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} TheoryAwareSearch initialization: {e}")
        results.append(False)
        return all(results)
    
    # Test opportunities
    try:
        opps = search.get_testing_opportunities(limit=5)
        assert len(opps) > 0
        print(f"  {colored('✓', Colors.GREEN)} Testing opportunities: {len(opps)} found")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Testing opportunities: {e}")
        results.append(False)
    
    # Test gaps
    try:
        gaps = search.identify_gaps()
        print(f"  {colored('✓', Colors.GREEN)} Theory gaps: {len(gaps)} identified")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Theory gaps: {e}")
        results.append(False)
    
    # Test query generation
    try:
        pred = search.generate_theory_query('daylight', 'mood')
        print(f"  {colored('✓', Colors.GREEN)} Query generation: confidence={pred.overall_confidence}")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Query generation: {e}")
        results.append(False)
    
    return all(results)

def test_data_models():
    """Test data model constraints and methods."""
    print("\n" + "="*60)
    print(colored("5. TESTING DATA MODELS", Colors.BLUE))
    print("="*60)
    
    from src.models.theory_models import (
        Theory, Prediction, generate_theory_id, generate_prediction_id,
        TheoryLevel, Direction, TestingStatus
    )
    
    results = []
    
    # Test ID generation
    try:
        tid = generate_theory_id("Test Theory")
        assert tid.startswith("theory:")
        pid = generate_prediction_id("theory:test", 1)  # index is an int
        assert pid.startswith("pred:")
        print(f"  {colored('✓', Colors.GREEN)} ID generation: theory={tid}, pred={pid}")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} ID generation: {e}")
        results.append(False)
    
    # Test theory level enum
    try:
        levels = [TheoryLevel.PRINCIPLE, TheoryLevel.THEORY, TheoryLevel.MECHANISM]
        assert len(levels) == 3
        print(f"  {colored('✓', Colors.GREEN)} Theory levels: {[l.value for l in levels]}")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Theory levels: {e}")
        results.append(False)
    
    # Test prediction validation
    try:
        pred = Prediction(
            prediction_id="pred:test:001",
            source_theory_id="theory:test",
            prediction_type="explicit",
            statement="Test prediction",
            consequent_direction=Direction.POSITIVE,
            consequent_outcome="test_outcome"
        )
        assert pred.testing_status == TestingStatus.UNTESTED
        print(f"  {colored('✓', Colors.GREEN)} Prediction creation: {pred.prediction_type}")
        results.append(True)
    except Exception as e:
        print(f"  {colored('✗', Colors.RED)} Prediction creation: {e}")
        results.append(False)
    
    return all(results)

def run_pytest():
    """Run the full pytest suite."""
    print("\n" + "="*60)
    print(colored("6. RUNNING PYTEST SUITE", Colors.BLUE))
    print("="*60)
    
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_theory_system.py", "-v", "--tb=short"],
        cwd=str(Path(__file__).parent.parent),
        capture_output=True,
        text=True
    )
    
    # Count passed/failed
    lines = result.stdout.split('\n')
    passed = sum(1 for l in lines if ' PASSED' in l)
    failed = sum(1 for l in lines if ' FAILED' in l)
    
    if failed == 0:
        print(f"  {colored('✓', Colors.GREEN)} {passed} tests passed")
        return True
    else:
        print(f"  {colored('✗', Colors.RED)} {failed} tests failed, {passed} passed")
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
        return False

def main():
    parser = argparse.ArgumentParser(description="Theory System Test Runner")
    parser.add_argument('--quick', action='store_true', help='Quick smoke test only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--skip-pytest', action='store_true', help='Skip pytest suite')
    args = parser.parse_args()
    
    print(colored("\n" + "="*60, Colors.BOLD))
    print(colored("ARTICLE EATER - THEORY SYSTEM TEST SUITE", Colors.BOLD))
    print(colored("="*60, Colors.BOLD))
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_passed = True
    
    # Run tests
    all_passed &= test_imports()
    all_passed &= test_registry()
    
    if not args.quick:
        all_passed &= test_prediction_generator()
        all_passed &= test_theory_search()
        all_passed &= test_data_models()
        
        if not args.skip_pytest:
            all_passed &= run_pytest()
    
    # Summary
    print("\n" + "="*60)
    if all_passed:
        print(colored("ALL TESTS PASSED", Colors.GREEN + Colors.BOLD))
    else:
        print(colored("SOME TESTS FAILED", Colors.RED + Colors.BOLD))
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
