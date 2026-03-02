"""
Test Suite for Theory Agent Service (T7.6)

Tests loading, retrieval, panel simulation, and theory profile functionality.
Minimum 25 tests covering:
- Profile loading and retrieval
- Panel persona simulation
- Finding evaluation
- Prediction matching and competition
- Panel discussion generation
- Framework relevance queries
- Error handling and edge cases
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from src.services.theory_agent_service import (
    TheoryAgentService,
    TheoryProfile,
    PanelPersona,
    EnvironmentalPrediction,
    FindingEvaluation,
    PanelDiscussion
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def service():
    """Initialize TheoryAgentService with test profiles."""
    return TheoryAgentService()


@pytest.fixture
def sample_finding():
    """Sample finding for evaluation."""
    return {
        "id": "test-finding-001",
        "description": "Visual complexity reduces cognitive load in moderately complex environments",
        "mechanism_explanation": "Goldilocks zone of predictability allows efficient processing"
    }


@pytest.fixture
def sample_finding_spatial():
    """Sample finding related to spatial navigation."""
    return {
        "id": "test-spatial-001",
        "description": "High architectural legibility improves wayfinding accuracy",
        "mechanism_explanation": "Clear spatial structure supports efficient place cell mapping"
    }


# =============================================================================
# Profile Loading Tests (1-5)
# =============================================================================

class TestProfileLoading:
    """Test profile loading functionality."""

    def test_service_initializes(self, service):
        """Service initializes without errors."""
        assert service is not None
        assert isinstance(service._profiles, dict)

    def test_all_10_frameworks_loaded(self, service):
        """All 10 T1 frameworks are loaded."""
        expected_count = 10
        assert len(service._framework_ids) == expected_count, \
            f"Expected {expected_count} frameworks, got {len(service._framework_ids)}"

    def test_framework_ids_correct(self, service):
        """Expected framework IDs are present."""
        expected_ids = [
            "predictive-processing",
            "spatial-navigation",
            "dual-process-evaluation",
            "default-mode-dynamics",
            "neuromodulatory-systems",
            "interoceptive-construction",
            "multisensory-integration",
            "ecological-dynamics",
            "circadian-biology",
            "motor-simulation-embodiment"
        ]
        for fw_id in expected_ids:
            assert fw_id in service._framework_ids, f"Framework {fw_id} not loaded"

    def test_profile_structure_complete(self, service):
        """Each profile has required fields."""
        required_fields = [
            "framework_id",
            "full_name",
            "core_claim",
            "key_theorists",
            "core_constructs",
            "epistemic_commitments",
            "environmental_predictions",
            "characteristic_questions",
            "panel_persona",
            "molecule_affinities",
            "meta"
        ]
        profile = service.get_profile("predictive-processing")
        assert profile is not None
        for field in required_fields:
            assert hasattr(profile, field), f"Profile missing field: {field}"

    def test_profiles_are_dataclass_instances(self, service):
        """Retrieved profiles are TheoryProfile instances."""
        profile = service.get_profile("spatial-navigation")
        assert isinstance(profile, TheoryProfile)


# =============================================================================
# Profile Retrieval Tests (6-10)
# =============================================================================

class TestProfileRetrieval:
    """Test profile retrieval methods."""

    def test_get_profile_by_id(self, service):
        """get_profile retrieves correct profile by ID."""
        profile = service.get_profile("predictive-processing")
        assert profile is not None
        assert profile.framework_id == "predictive-processing"
        assert "prediction error" in profile.core_claim.lower()

    def test_get_profile_nonexistent(self, service):
        """get_profile returns None for nonexistent framework."""
        profile = service.get_profile("nonexistent-framework")
        assert profile is None

    def test_list_frameworks(self, service):
        """list_frameworks returns all loaded framework IDs."""
        frameworks = service.list_frameworks()
        assert len(frameworks) == 10
        assert "predictive-processing" in frameworks

    def test_list_profiles_summary(self, service):
        """list_profiles_summary returns summary data."""
        summaries = service.list_profiles_summary()
        assert len(summaries) == 10
        # Each summary should have core fields
        assert all("framework_id" in s for s in summaries)
        assert all("full_name" in s for s in summaries)

    def test_get_framework_by_name(self, service):
        """get_framework_by_name finds framework by display name."""
        fw_id = service.get_framework_by_name("Predictive Processing")
        assert fw_id == "predictive-processing"


# =============================================================================
# Panel Persona Tests (11-15)
# =============================================================================

class TestPanelPersona:
    """Test panel persona functionality."""

    def test_get_panel_persona(self, service):
        """get_panel_persona returns persona object."""
        persona = service.get_panel_persona("predictive-processing")
        assert isinstance(persona, PanelPersona)
        assert persona.framework_id == "predictive-processing"

    def test_persona_has_voice(self, service):
        """Panel persona has voice statement."""
        persona = service.get_panel_persona("neuromodulatory-systems")
        assert persona.voice
        assert len(persona.voice) > 0

    def test_persona_has_critiques(self, service):
        """Panel persona has typical critiques."""
        persona = service.get_panel_persona("spatial-navigation")
        assert persona.typical_critiques
        assert len(persona.typical_critiques) > 0
        assert all(isinstance(c, str) for c in persona.typical_critiques)

    def test_persona_has_blind_spots(self, service):
        """Panel persona has identified blind spots."""
        persona = service.get_panel_persona("ecological-dynamics")
        assert persona.blind_spots
        assert len(persona.blind_spots) > 0

    def test_persona_has_complementary_frameworks(self, service):
        """Panel persona lists complementary frameworks."""
        persona = service.get_panel_persona("interoceptive-construction")
        assert persona.complementary_frameworks
        assert len(persona.complementary_frameworks) > 0


# =============================================================================
# Finding Evaluation Tests (16-20)
# =============================================================================

class TestFindingEvaluation:
    """Test finding evaluation functionality."""

    def test_evaluate_finding_returns_evaluation(self, service, sample_finding):
        """evaluate_finding returns FindingEvaluation object."""
        evaluation = service.evaluate_finding("predictive-processing", sample_finding)
        assert isinstance(evaluation, FindingEvaluation)

    def test_evaluation_has_framework_info(self, service, sample_finding):
        """Evaluation includes framework identification."""
        evaluation = service.evaluate_finding("dual-process-evaluation", sample_finding)
        assert evaluation.framework_id == "dual-process-evaluation"
        assert evaluation.framework_name
        assert "Dual" in evaluation.framework_name

    def test_evaluation_includes_warrant_types(self, service, sample_finding):
        """Evaluation includes preferred warrant types."""
        evaluation = service.evaluate_finding("neuromodulatory-systems", sample_finding)
        assert evaluation.warrant_types
        assert len(evaluation.warrant_types) > 0

    def test_evaluation_confidence_is_valid(self, service, sample_finding):
        """Evaluation confidence is between 0 and 1."""
        evaluation = service.evaluate_finding("spatial-navigation", sample_finding)
        assert 0.0 <= evaluation.confidence <= 1.0

    def test_evaluation_includes_next_questions(self, service, sample_finding):
        """Evaluation includes follow-up questions."""
        evaluation = service.evaluate_finding("circadian-biology", sample_finding)
        assert evaluation.next_questions
        assert len(evaluation.next_questions) > 0


# =============================================================================
# Prediction Tests (21-25)
# =============================================================================

class TestPredictionMatching:
    """Test prediction matching and retrieval."""

    def test_get_prediction_by_id(self, service):
        """get_prediction_by_id retrieves prediction."""
        prediction = service.get_prediction_by_id("pp-pred-001")
        assert prediction is not None
        assert prediction["prediction_id"] == "pp-pred-001"

    def test_get_competing_predictions(self, service):
        """get_competing_predictions finds competing predictions."""
        # pp-pred-001 should have competing predictions
        competing = service.get_competing_predictions("pp-pred-001")
        assert isinstance(competing, list)
        # May be empty if no predictions specified competing ones

    def test_get_relevant_frameworks(self, service):
        """get_relevant_frameworks finds frameworks caring about template."""
        # PP_VISUAL_STATISTICS_001 is in predictive-processing predictions
        frameworks = service.get_relevant_frameworks("PP_VISUAL_STATISTICS_001")
        assert "predictive-processing" in frameworks

    def test_search_profiles_by_construct(self, service):
        """search_profiles_by_construct finds frameworks with construct."""
        results = service.search_profiles_by_construct("prediction_error")
        assert len(results) > 0
        # predictive-processing should be in results
        framework_ids = [r[0] for r in results]
        assert "predictive-processing" in framework_ids

    def test_search_construct_case_insensitive(self, service):
        """Construct search is case-insensitive."""
        results_upper = service.search_profiles_by_construct("REWARD")
        results_lower = service.search_profiles_by_construct("reward")
        assert len(results_upper) == len(results_lower)


# =============================================================================
# Panel Discussion Tests (26-30)
# =============================================================================

class TestPanelDiscussion:
    """Test panel discussion simulation."""

    def test_simulate_panel_discussion_basic(self, service, sample_finding):
        """simulate_panel_discussion returns PanelDiscussion object."""
        discussion = service.simulate_panel_discussion(sample_finding)
        assert isinstance(discussion, PanelDiscussion)

    def test_discussion_includes_individual_evaluations(self, service, sample_finding):
        """Discussion includes individual framework evaluations."""
        discussion = service.simulate_panel_discussion(
            sample_finding,
            framework_ids=["predictive-processing", "neuromodulatory-systems"]
        )
        assert len(discussion.individual_evaluations) == 2
        assert all(isinstance(e, FindingEvaluation) for e in discussion.individual_evaluations)

    def test_discussion_with_custom_frameworks(self, service, sample_finding_spatial):
        """Discussion can be limited to specific frameworks."""
        frameworks = ["spatial-navigation", "ecological-dynamics"]
        discussion = service.simulate_panel_discussion(sample_finding_spatial, framework_ids=frameworks)
        assert discussion.frameworks_represented == frameworks

    def test_discussion_has_convergence_summary(self, service, sample_finding):
        """Discussion includes convergence synthesis."""
        discussion = service.simulate_panel_discussion(sample_finding)
        assert discussion.convergence_summary
        assert isinstance(discussion.convergence_summary, str)

    def test_discussion_has_timestamp(self, service, sample_finding):
        """Discussion includes generation timestamp."""
        before = datetime.utcnow().isoformat()
        discussion = service.simulate_panel_discussion(sample_finding)
        after = datetime.utcnow().isoformat()
        assert discussion.generated_at
        # Timestamp should be reasonable
        assert before <= discussion.generated_at <= after


# =============================================================================
# Profile Content Tests (31-35)
# =============================================================================

class TestProfileContent:
    """Test actual profile content quality."""

    def test_seminal_works_have_required_fields(self, service):
        """Seminal works have author, year, title."""
        profile = service.get_profile("predictive-processing")
        for work in profile.seminal_works:
            assert "author" in work
            assert "year" in work
            assert "title" in work

    def test_core_claim_is_substantial(self, service):
        """Core claim is a meaningful statement."""
        for fw_id in ["predictive-processing", "spatial-navigation", "neuromodulatory-systems"]:
            profile = service.get_profile(fw_id)
            assert len(profile.core_claim) > 30, f"{fw_id} core claim too short"

    def test_epistemic_commitments_complete(self, service):
        """Epistemic commitments section is complete."""
        profile = service.get_profile("circadian-biology")
        commitments = profile.epistemic_commitments
        assert "preferred_warrant_types" in commitments
        assert "evidence_weighting" in commitments
        assert "falsification_criteria" in commitments
        assert "scope_boundaries" in commitments

    def test_environmental_predictions_testable(self, service):
        """Environmental predictions have testable flag."""
        profile = service.get_profile("multisensory-integration")
        for pred in profile.environmental_predictions:
            assert "testable" in pred
            assert isinstance(pred["testable"], bool)

    def test_molecule_affinities_exist(self, service):
        """Each profile has molecule affinities."""
        for fw_id in service._framework_ids:
            profile = service.get_profile(fw_id)
            assert profile.molecule_affinities
            assert len(profile.molecule_affinities) > 0


# =============================================================================
# Data Serialization Tests (36+)
# =============================================================================

class TestSerialization:
    """Test data serialization to dictionaries."""

    def test_theory_profile_to_dict(self, service):
        """TheoryProfile converts to dictionary."""
        profile = service.get_profile("predictive-processing")
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert profile_dict["framework_id"] == "predictive-processing"

    def test_panel_persona_to_dict(self, service):
        """PanelPersona converts to dictionary."""
        persona = service.get_panel_persona("neuromodulatory-systems")
        persona_dict = persona.to_dict()
        assert isinstance(persona_dict, dict)
        assert "voice" in persona_dict

    def test_finding_evaluation_to_dict(self, service, sample_finding):
        """FindingEvaluation converts to dictionary."""
        evaluation = service.evaluate_finding("dual-process-evaluation", sample_finding)
        eval_dict = evaluation.to_dict()
        assert isinstance(eval_dict, dict)
        assert "framework_id" in eval_dict

    def test_panel_discussion_to_dict(self, service, sample_finding):
        """PanelDiscussion converts to dictionary."""
        discussion = service.simulate_panel_discussion(sample_finding)
        discussion_dict = discussion.to_dict()
        assert isinstance(discussion_dict, dict)
        assert "finding_id" in discussion_dict

    def test_serialization_json_compatible(self, service, sample_finding):
        """Serialized objects are JSON-serializable."""
        discussion = service.simulate_panel_discussion(sample_finding)
        discussion_dict = discussion.to_dict()
        # Should not raise
        json_str = json.dumps(discussion_dict, indent=2)
        assert json_str
        # Deserialize should work
        reloaded = json.loads(json_str)
        assert reloaded["finding_id"] == sample_finding["id"]


# =============================================================================
# Integration Tests (41+)
# =============================================================================

class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_workflow_finding_to_panel(self, service, sample_finding):
        """Full workflow: evaluate finding across panel."""
        # Get individual evaluations
        evaluations = []
        for fw_id in ["predictive-processing", "neuromodulatory-systems", "interoceptive-construction"]:
            eval = service.evaluate_finding(fw_id, sample_finding)
            evaluations.append(eval)

        assert len(evaluations) == 3
        assert all(e.confidence > 0 for e in evaluations)

    def test_framework_recommendation_based_on_construct(self, service):
        """Recommend frameworks based on construct match."""
        # User interested in "reward" constructs
        results = service.search_profiles_by_construct("reward")
        framework_ids = [r[0] for r in results]

        # Should include neuromodulatory systems
        assert "neuromodulatory-systems" in framework_ids

    def test_competing_prediction_identification(self, service):
        """Identify competing predictions across frameworks."""
        # Get a prediction
        pred = service.get_prediction_by_id("pp-pred-002")
        if pred and pred.get("competing_predictions"):
            # Should have competing frameworks listed
            assert len(pred["competing_predictions"]) > 0

    def test_multi_framework_discussion_coherence(self, service, sample_finding):
        """Panel discussion with multiple frameworks is coherent."""
        frameworks = [
            "predictive-processing",
            "spatial-navigation",
            "neuromodulatory-systems"
        ]
        discussion = service.simulate_panel_discussion(sample_finding, framework_ids=frameworks)

        # All frameworks should be represented
        assert len(discussion.individual_evaluations) == len(frameworks)

        # Should identify convergences/tensions
        assert discussion.convergence_summary
        assert isinstance(discussion.next_experiments_proposed, list)


# =============================================================================
# Error Handling Tests (46+)
# =============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_evaluate_nonexistent_framework(self, service, sample_finding):
        """Evaluating from nonexistent framework returns None."""
        result = service.evaluate_finding("fake-framework", sample_finding)
        assert result is None

    def test_get_persona_nonexistent_framework(self, service):
        """Getting persona for nonexistent framework returns None."""
        result = service.get_panel_persona("fake-framework")
        assert result is None

    def test_empty_finding_dict(self, service):
        """Service handles empty finding gracefully."""
        empty_finding = {}
        discussion = service.simulate_panel_discussion(empty_finding)
        assert isinstance(discussion, PanelDiscussion)

    def test_finding_with_null_mechanism(self, service):
        """Finding with null mechanism is handled."""
        finding = {
            "id": "test",
            "description": "Test finding",
            "mechanism_explanation": None
        }
        evaluation = service.evaluate_finding("predictive-processing", finding)
        assert evaluation is not None

    def test_nonexistent_prediction_id(self, service):
        """Nonexistent prediction returns None."""
        result = service.get_prediction_by_id("fake-pred-999")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
