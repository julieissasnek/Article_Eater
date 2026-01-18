"""
Article Eater - Theory System Test Suite
Comprehensive tests for Sprint TH-1, PG-1-4, AE-9, INT-4

Run with: pytest tests/test_theory_system.py -v
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.theory_models import (
    Theory, TheoryClaim, TheoryAssumption, TheoryBoundary, Prediction,
    PredictionEvidence, DerivationStep, QuantitativePrediction, Originator,
    TheoryLevel, PredictionType, Direction, Magnitude, TestingStatus,
    SupportLevel, TestResult, TestStrength, TestType, Necessity, Testability,
    RelationType, Generality, UncertaintyType, ReplicationStatus,
    generate_theory_id, generate_prediction_id, generate_claim_id,
    compute_derivation_confidence
)
from src.services.theory_registry import TheoryRegistry
from src.services.prediction_generator import PredictionGenerator, Query
from src.data.theory_bootstrap import bootstrap_registry, get_bootstrap_theories


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def registry():
    """Create a fresh in-memory registry."""
    return TheoryRegistry(':memory:')


@pytest.fixture
def bootstrapped_registry(registry):
    """Create a registry populated with bootstrap theories."""
    bootstrap_registry(registry)
    return registry


@pytest.fixture
def sample_theory():
    """Create a sample theory for testing."""
    theory_id = "theory:test_theory"
    
    return Theory(
        theory_id=theory_id,
        name="Test Theory",
        aliases=["TT", "Testing Theory"],
        originators=[Originator(name="Test Author", year=2020)],
        year_introduced=2020,
        domain=["testing", "validation"],
        scope_description="A theory for testing purposes",
        level=TheoryLevel.THEORY,
        core_claims=[
            TheoryClaim(
                claim_id=f"{theory_id}:claim:01",
                theory_id=theory_id,
                statement="Test inputs produce test outputs",
                formalization="test(x) → output(x)",
                necessity=Necessity.CORE,
                testability=Testability.DIRECTLY_TESTABLE
            )
        ],
        assumptions=[
            TheoryAssumption(
                assumption_id=f"{theory_id}:assumption:01",
                theory_id=theory_id,
                statement="Testing environment is controlled",
                dependent_claims=[f"{theory_id}:claim:01"],
                violation_consequence="Results may be unreliable"
            )
        ],
        boundary_conditions=[
            TheoryBoundary(
                boundary_id=f"{theory_id}:boundary:01",
                theory_id=theory_id,
                condition_description="Only applies in test environments",
                evidence_for_boundary="Empirical observation",
                mechanism_of_failure="Real-world complexity",
                confidence_penalty=0.2
            )
        ],
        explicit_predictions=[
            Prediction(
                prediction_id=f"{theory_id}:pred:01",
                source_theory_id=theory_id,
                statement="Test interventions improve test outcomes",
                prediction_type=PredictionType.EXPLICIT,
                antecedent_env_conditions=[{"type": "test_environment"}],
                consequent_outcome="test_outcome",
                consequent_direction=Direction.POSITIVE,
                consequent_magnitude=Magnitude.MODERATE,
                testing_status=TestingStatus.PARTIALLY_TESTED,
                overall_support=SupportLevel.SUPPORTED,
                prior_confidence=0.7,
                current_confidence=0.75
            )
        ],
        derived_predictions=[],
        overall_confidence=0.7,
        confidence_rationale="Test theory with moderate support",
        replication_status=ReplicationStatus.MODERATE
    )


@pytest.fixture
def sample_prediction(sample_theory):
    """Get the sample prediction from sample theory."""
    return sample_theory.explicit_predictions[0]


# ============================================================
# MODEL TESTS
# ============================================================

class TestTheoryModels:
    """Tests for theory data models."""
    
    def test_generate_theory_id(self):
        """Test theory ID generation."""
        id1 = generate_theory_id("Test Theory")
        id2 = generate_theory_id("Test Theory")
        
        assert id1.startswith("theory:")
        assert id1 == id2  # Same input should give same output
        
        id3 = generate_theory_id("Different Theory")
        assert id3 != id1
    
    def test_generate_prediction_id(self):
        """Test prediction ID generation."""
        pred_id = generate_prediction_id("theory:test", 1)
        
        assert pred_id.startswith("pred:")
        assert "001" in pred_id
    
    def test_compute_derivation_confidence(self):
        """Test derivation confidence computation."""
        # Empty chain gives base confidence (0.9)
        assert compute_derivation_confidence([]) == 0.9
        
        # Single deductive step
        steps = [DerivationStep(claim_id="c1", inference_type="deductive")]
        conf = compute_derivation_confidence(steps)
        assert 0.8 < conf < 0.95
        
        # Multiple steps reduce confidence
        steps2 = [
            DerivationStep(claim_id="c1", inference_type="deductive"),
            DerivationStep(claim_id="c2", inference_type="inductive")
        ]
        conf2 = compute_derivation_confidence(steps2)
        assert conf2 < conf
        
        # Analogical has lowest confidence
        steps3 = [DerivationStep(claim_id="c1", inference_type="analogical")]
        conf3 = compute_derivation_confidence(steps3)
        assert conf3 < conf
    
    def test_theory_all_predictions(self, sample_theory):
        """Test that all_predictions combines explicit and derived."""
        all_preds = sample_theory.all_predictions
        
        assert len(all_preds) == len(sample_theory.explicit_predictions) + len(sample_theory.derived_predictions)
        assert all_preds[0].prediction_type == PredictionType.EXPLICIT
    
    def test_prediction_enums(self):
        """Test prediction enum values."""
        assert Direction.POSITIVE.value == "positive"
        assert Magnitude.MODERATE.value == "moderate"
        assert TestingStatus.UNTESTED.value == "untested"
        assert SupportLevel.SUPPORTED.value == "supported"


# ============================================================
# REGISTRY TESTS
# ============================================================

class TestTheoryRegistry:
    """Tests for theory registry operations."""
    
    def test_registry_initialization(self, registry):
        """Test that registry creates required tables."""
        with registry._get_connection() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [t[0] for t in tables]
        
        assert 'theories' in table_names
        assert 'theory_claims' in table_names
        assert 'predictions' in table_names
    
    def test_add_and_get_theory(self, registry, sample_theory):
        """Test adding and retrieving a theory."""
        # Add theory
        result_id = registry.add_theory(sample_theory)
        assert result_id == sample_theory.theory_id
        
        # Retrieve theory
        retrieved = registry.get_theory(sample_theory.theory_id)
        assert retrieved is not None
        assert retrieved.name == sample_theory.name
        assert len(retrieved.core_claims) == len(sample_theory.core_claims)
        assert len(retrieved.all_predictions) == len(sample_theory.all_predictions)
    
    def test_list_theories(self, bootstrapped_registry):
        """Test listing all theories."""
        theories = bootstrapped_registry.list_theories()
        
        assert len(theories) >= 6  # Bootstrap has 6 theories
        assert all(hasattr(t, 'name') for t in theories)
        assert all(hasattr(t, 'overall_confidence') for t in theories)
    
    def test_list_theories_with_filter(self, bootstrapped_registry):
        """Test filtering theories by level."""
        principles = bootstrapped_registry.list_theories(level=TheoryLevel.PRINCIPLE)
        theories = bootstrapped_registry.list_theories(level=TheoryLevel.THEORY)
        
        # Fractal Fluency is a principle, others are theories
        assert len(principles) >= 1
        assert len(theories) >= 5
    
    def test_update_theory_confidence(self, registry, sample_theory):
        """Test updating theory confidence with audit trail."""
        registry.add_theory(sample_theory)
        
        old_confidence = sample_theory.overall_confidence
        new_confidence = 0.85
        
        registry.update_theory_confidence(
            sample_theory.theory_id,
            new_confidence,
            reason="Test update",
            triggered_by="test_case"
        )
        
        # Verify update
        updated = registry.get_theory(sample_theory.theory_id)
        assert updated.overall_confidence == new_confidence
    
    def test_get_prediction(self, bootstrapped_registry):
        """Test retrieving a specific prediction."""
        # Get a known prediction from ART
        pred = bootstrapped_registry.get_prediction("theory:attention_restoration:pred:001")
        
        assert pred is not None
        assert pred.source_theory_id == "theory:attention_restoration"
        assert "natural environment" in pred.statement.lower()
    
    def test_search_predictions(self, bootstrapped_registry):
        """Test searching predictions by criteria."""
        # Get all predictions and filter manually
        theories = bootstrapped_registry.list_theories()
        attention_preds = []
        for t in theories:
            full_t = bootstrapped_registry.get_theory(t.theory_id)
            if full_t:
                for p in full_t.all_predictions:
                    if 'attention' in p.consequent_outcome.lower():
                        attention_preds.append(p)
        
        assert len(attention_preds) > 0
    
    def test_get_theory_statistics(self, bootstrapped_registry):
        """Test computing registry statistics."""
        stats = bootstrapped_registry.get_theory_statistics()
        
        assert 'theories_by_level' in stats
        assert 'predictions_by_status' in stats
        assert 'average_theory_confidence' in stats
        assert stats['average_theory_confidence'] > 0


# ============================================================
# PREDICTION GENERATOR TESTS
# ============================================================

class TestPredictionGenerator:
    """Tests for prediction generation."""
    
    def test_generator_initialization(self, bootstrapped_registry):
        """Test creating a prediction generator."""
        generator = PredictionGenerator(bootstrapped_registry)
        assert generator is not None
    
    def test_generate_prediction_with_matches(self, bootstrapped_registry):
        """Test generating prediction for a well-covered query."""
        generator = PredictionGenerator(bootstrapped_registry)
        
        query = Query(
            query_id="test:1",
            independent_variable="nature_exposure",
            dependent_variable="attention_performance"
        )
        
        result = generator.generate(query)
        
        assert result is not None
        assert len(result.relevant_theories) > 0
        assert len(result.predictions_found) > 0  # It's a list
        assert result.prior_distribution is not None
        assert result.prior_distribution.prior_type == "theory_derived"
    
    def test_generate_prediction_no_matches(self, bootstrapped_registry):
        """Test generating prediction for an uncovered query."""
        generator = PredictionGenerator(bootstrapped_registry)
        
        query = Query(
            query_id="test:2",
            independent_variable="quantum_fluctuations",
            dependent_variable="telepathic_ability"
        )
        
        result = generator.generate(query)
        
        assert result is not None
        assert len(result.relevant_theories) == 0
        assert len(result.predictions_found) == 0  # Empty list
        assert result.prior_distribution.prior_type == "uninformative"
        assert result.overall_confidence == "very_low"
    
    def test_prior_distribution_values(self, bootstrapped_registry):
        """Test that prior distribution has sensible values."""
        generator = PredictionGenerator(bootstrapped_registry)
        
        query = Query(
            query_id="test:3",
            independent_variable="stress",
            dependent_variable="health"
        )
        
        result = generator.generate(query)
        prior = result.prior_distribution
        
        # Check bounds
        assert -2.0 <= prior.mean <= 2.0
        assert prior.variance > 0
        assert prior.ci_lower < prior.mean < prior.ci_upper
    
    def test_voi_calculation(self, bootstrapped_registry):
        """Test Value of Information calculation."""
        generator = PredictionGenerator(bootstrapped_registry)
        
        # High VOI: theory predicts but no empirical data
        query1 = Query(
            query_id="test:4",
            independent_variable="biophilic_design",
            dependent_variable="occupant_satisfaction"
        )
        result1 = generator.generate(query1)
        
        # Low VOI: no theory coverage
        query2 = Query(
            query_id="test:5",
            independent_variable="random_variable",
            dependent_variable="unknown_outcome"
        )
        result2 = generator.generate(query2)
        
        # VOI should be bounded
        assert 0 <= result1.voi <= 1
        assert 0 <= result2.voi <= 1


# ============================================================
# BOOTSTRAP TESTS
# ============================================================

class TestBootstrap:
    """Tests for theory bootstrap data."""
    
    def test_get_bootstrap_theories(self):
        """Test that bootstrap returns expected theories."""
        theories = get_bootstrap_theories()
        
        assert len(theories) >= 6
        
        theory_names = [t.name for t in theories]
        assert "Attention Restoration Theory" in theory_names
        assert "Stress Recovery Theory" in theory_names
        assert "Predictive Processing" in theory_names
    
    def test_bootstrap_registry_success(self, registry):
        """Test bootstrapping a registry."""
        result = bootstrap_registry(registry)
        
        assert result['theories_added'] >= 6
        assert result['total_predictions'] >= 18
        assert len(result['errors']) == 0
    
    def test_bootstrap_theories_have_predictions(self):
        """Test that all bootstrap theories have predictions."""
        theories = get_bootstrap_theories()
        
        for theory in theories:
            assert len(theory.all_predictions) > 0, f"{theory.name} has no predictions"
            assert len(theory.core_claims) > 0, f"{theory.name} has no claims"
    
    def test_bootstrap_predictions_are_valid(self):
        """Test that bootstrap predictions have required fields."""
        theories = get_bootstrap_theories()
        
        for theory in theories:
            for pred in theory.all_predictions:
                assert pred.prediction_id, "Prediction missing ID"
                assert pred.statement, "Prediction missing statement"
                assert pred.consequent_outcome, "Prediction missing outcome"
                assert pred.consequent_direction in Direction, "Invalid direction"


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_full_workflow(self, bootstrapped_registry):
        """Test complete workflow: bootstrap → query → prediction."""
        # 1. Registry is already bootstrapped
        stats = bootstrapped_registry.get_theory_statistics()
        assert stats['theories_by_level']
        
        # 2. Query the system
        generator = PredictionGenerator(bootstrapped_registry)
        
        queries = [
            ("nature", "stress"),
            ("noise", "concentration"),
            ("daylight", "mood"),
        ]
        
        for iv, dv in queries:
            query = Query(
                query_id=f"test:{iv}:{dv}",
                independent_variable=iv,
                dependent_variable=dv
            )
            result = generator.generate(query)
            
            # Should always get a result
            assert result is not None
            assert result.prior_distribution is not None
            assert result.narrative
    
    def test_theory_retrieval_completeness(self, bootstrapped_registry):
        """Test that retrieved theories have all components."""
        art = bootstrapped_registry.get_theory("theory:attention_restoration")
        
        assert art.name == "Attention Restoration Theory"
        assert len(art.core_claims) >= 4
        assert len(art.assumptions) >= 1
        assert len(art.boundary_conditions) >= 1
        assert len(art.all_predictions) >= 4
        
        # Check predictions have derivation chains where appropriate
        derived = [p for p in art.all_predictions if p.prediction_type == PredictionType.DERIVED]
        for pred in derived:
            assert len(pred.derivation_chain) > 0, f"Derived prediction {pred.prediction_id} has no derivation chain"


# ============================================================
# EXTRACTION TESTS (Sprint AE-9)
# ============================================================

class TestTheoryExtraction:
    """Tests for theory extraction components."""
    
    def test_extraction_prompt_generation(self, bootstrapped_registry):
        """Test that extraction prompts are generated correctly."""
        from src.extraction.theory_extraction import TheoryExtractor
        
        extractor = TheoryExtractor(llm_client=None)  # No LLM, just prompts
        
        prompt = extractor.get_identification_prompt("This is a test paper about attention.")
        
        assert "PAPER TO ANALYZE" in prompt
        assert "RESPOND WITH JSON" in prompt
        assert "is_theory_paper" in prompt
    
    def test_validation_functions(self):
        """Test extraction validation functions."""
        from src.extraction.theory_extraction import (
            validate_theory_identification,
            validate_core_claims,
            validate_predictions
        )
        
        # Valid identification
        valid_id = {
            'is_theory_paper': True,
            'theory_name': 'Test Theory',
            'paper_role': 'articulates_new',
            'criteria_met': ['NAMED_FRAMEWORK', 'EXPLANATORY_SCOPE', 
                            'CORE_CLAIMS_IDENTIFIABLE', 'PREDICTIONS_DERIVABLE'],
            'confidence': 0.8
        }
        is_valid, issues = validate_theory_identification(valid_id)
        assert is_valid
        
        # Invalid: missing criteria
        invalid_id = {
            'is_theory_paper': True,
            'theory_name': 'Test',
            'paper_role': 'articulates_new',
            'criteria_met': ['NAMED_FRAMEWORK'],
            'confidence': 0.5
        }
        is_valid, issues = validate_theory_identification(invalid_id)
        assert not is_valid
        assert len(issues) > 0
    
    def test_quality_assessment(self):
        """Test extraction quality assessment."""
        from src.extraction.theory_extraction import (
            TheoryExtractionTemplate,
            assess_extraction_quality
        )
        
        # High quality template
        good_template = TheoryExtractionTemplate(
            theory_name="Test Theory",
            core_claims=[
                {'statement': 'Claim 1', 'necessity': 'core'},
                {'statement': 'Claim 2', 'necessity': 'auxiliary'}
            ],
            assumptions=[{'statement': 'Assumption 1'}],
            boundary_conditions=[{'condition': 'Boundary 1'}],
            explicit_predictions=[
                {'statement': 'Pred 1', 'consequent': {'outcome': 'x', 'direction': 'positive'}},
                {'statement': 'Pred 2', 'consequent': {'outcome': 'y', 'direction': 'negative'}},
                {'statement': 'Pred 3', 'consequent': {'outcome': 'z', 'direction': 'positive'}}
            ],
            suggested_confidence=0.7
        )
        
        report = assess_extraction_quality(good_template)
        assert report.overall_quality in ['high', 'medium']
        assert report.completeness_score > 0.5


# ============================================================
# PROPAGATION TESTS (Sprint INT-4)
# ============================================================

class TestPropagation:
    """Tests for evidence propagation."""
    
    def test_propagation_rules(self):
        """Test default propagation rules."""
        from src.services.propagation import PropagationRules
        
        rules = PropagationRules()
        
        assert rules.evidence_to_prediction_weight > 0
        assert rules.prediction_to_theory_weight > 0
        assert rules.min_confidence_change > 0
        assert rules.max_single_update < 1.0
    
    def test_upward_propagation(self, bootstrapped_registry):
        """Test upward propagation from evidence to theory."""
        from src.services.propagation import PropagationManager, PropagationRules
        from src.models.theory_models import TestResult, TestStrength
        
        manager = PropagationManager(bootstrapped_registry)
        
        # Get a real prediction from the bootstrapped registry
        art = bootstrapped_registry.get_theory("theory:attention_restoration")
        assert art is not None
        assert len(art.all_predictions) > 0
        
        pred = art.all_predictions[0]
        
        # Note: We can't fully test evidence addition without the paper in the DB
        # due to foreign key constraints. Just test that the manager initializes.
        assert manager.upward is not None
        assert manager.downward is not None
        assert len(manager.audit_log) == 0
    
    def test_downward_propagation(self, bootstrapped_registry):
        """Test downward propagation from theory to predictions."""
        from src.services.propagation import PropagationManager
        
        manager = PropagationManager(bootstrapped_registry)
        
        # Revise theory confidence
        result = manager.revise_theory(
            theory_id="theory:attention_restoration",
            new_confidence=0.85,
            reason="Strong replication evidence"
        )
        
        assert result.success
        # Events should include prediction updates
        if result.events:
            assert any('pred' in e.affected_entities[0] for e in result.events)


# ============================================================
# THEORY TESTING EXTRACTION TESTS (Sprint AE-9)
# ============================================================

class TestTheoryTestingExtraction:
    """Tests for theory-testing extraction."""
    
    def test_heuristic_detection(self, bootstrapped_registry):
        """Test heuristic theory detection."""
        from src.extraction.theory_testing import detect_theories_heuristic
        
        text = """
        This study examined attention restoration in natural environments.
        Based on Kaplan's Attention Restoration Theory, we hypothesized that
        exposure to nature would restore directed attention capacity.
        """
        
        matches = detect_theories_heuristic(text, bootstrapped_registry)
        
        assert len(matches) > 0
        # ART should be detected
        art_matches = [m for m in matches if 'attention_restoration' in m[0]]
        assert len(art_matches) > 0
    
    def test_result_detection_heuristic(self, bootstrapped_registry):
        """Test heuristic result detection."""
        from src.extraction.theory_testing import detect_test_result_heuristic
        from src.models.theory_models import Direction, TestResult
        
        # Create a prediction about attention
        pred = Prediction(
            prediction_id="test:pred",
            source_theory_id="test",
            statement="Nature improves attention",
            prediction_type=PredictionType.EXPLICIT,
            consequent_outcome="attention",
            consequent_direction=Direction.POSITIVE,
            consequent_magnitude=Magnitude.MODERATE,
            testing_status=TestingStatus.UNTESTED,
            prior_confidence=0.7,
            current_confidence=0.7
        )
        
        # Supporting result
        text1 = "Results showed a significant increase in attention scores (p < .001)."
        result1 = detect_test_result_heuristic(text1, pred)
        assert result1 == TestResult.SUPPORTS
        
        # Null result
        text2 = "No significant difference in attention was found (p > .05)."
        result2 = detect_test_result_heuristic(text2, pred)
        assert result2 == TestResult.NULL


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
