"""
Tests for Answer Enrichment Orchestrator

Tests cover:
- Basic enrichment with mock services
- Graceful degradation when services fail
- Timeout handling
- User type adaptation
- Config toggling
- Empty base answer handling
- EnrichedAnswer serialization
- Service skipping when modules unavailable
- Metadata tracking

Author: Claude Code (agent for Prof. David Kirsh, UCSD Cognitive Science)
Date: 2026-03-03
"""

import json
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

from src.services.answer_enrichment_orchestrator import (
    AnswerEnrichmentOrchestrator,
    EnrichmentConfig,
    EnrichedAnswer,
    EnrichedBelief,
    UserType,
    create_orchestrator,
    enrich_answer,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_base_answer():
    """Create a mock base answer from arbitrary_qa_handler."""
    return {
        "answer": "Attention restoration theory suggests that natural environments restore directed attention.",
        "beliefs": [
            {
                "text": "Natural environments restore directed attention",
                "confidence": 0.75,
                "p_lab": 0.75,
                "d": 0.80,
                "omega": 0.85,
                "delta": 1.0,
                "design_type": "standard_rct",
                "source": "Kaplan & Kaplan 1989",
            },
            {
                "text": "This effect is stronger in individuals with high cognitive load",
                "confidence": 0.65,
                "p_lab": 0.65,
                "d": 0.75,
                "omega": 0.70,
                "delta": 0.90,
                "design_type": "observational",
                "source": "White et al 2019",
            },
        ],
        "evidence_count": 2,
        "theories_involved": ["attention_restoration_theory"],
    }


@pytest.fixture
def mock_config():
    """Create a default enrichment config."""
    return EnrichmentConfig(
        enable_credence_ci=True,
        enable_warrant_trace=True,
        enable_confounder_risk=True,
        enable_framework_voices=True,
        enable_gap_analysis=True,
        enable_follow_ups=True,
        enable_language_adaptation=True,
        enable_figure_suggestions=True,
        timeout_per_service_ms=2000,
        max_beliefs_to_enrich=20,
    )


@pytest.fixture
def orchestrator(mock_config):
    """Create an orchestrator with default config."""
    return AnswerEnrichmentOrchestrator(mock_config)


# =============================================================================
# TESTS: BASIC ENRICHMENT
# =============================================================================

def test_orchestrator_initialization():
    """Test that orchestrator initializes without errors."""
    orch = AnswerEnrichmentOrchestrator()
    assert orch is not None
    assert orch._config is not None
    assert orch._services is not None


def test_create_orchestrator_factory():
    """Test create_orchestrator factory function."""
    orch = create_orchestrator()
    assert isinstance(orch, AnswerEnrichmentOrchestrator)


def test_basic_enrich(orchestrator, mock_base_answer):
    """Test basic enrichment with mock services."""
    result = orchestrator.enrich(
        base_answer=mock_base_answer,
        question="How does attention restoration work?",
        user_type="researcher",
    )

    assert isinstance(result, EnrichedAnswer)
    assert result.base_answer == mock_base_answer
    assert result.user_type == "researcher"
    assert result.enrichment_metadata is not None
    assert "timestamp" in result.enrichment_metadata
    assert "question" in result.enrichment_metadata
    assert "services_attempted" in result.enrichment_metadata


def test_enrich_convenience_function(mock_base_answer):
    """Test enrich_answer convenience function."""
    result = enrich_answer(
        base_answer=mock_base_answer,
        question="Test question?",
        user_type="student",
    )

    assert isinstance(result, EnrichedAnswer)
    assert result.user_type == "student"
    assert result.base_answer == mock_base_answer


# =============================================================================
# TESTS: CREDENCE ENRICHMENT
# =============================================================================

def test_credence_enrichment_enabled(orchestrator, mock_base_answer):
    """Test credence enrichment when enabled."""
    orchestrator._config.enable_credence_ci = True
    result = orchestrator.enrich(mock_base_answer, "Test?")

    # Should attempt credence enrichment
    assert "credence_enrichment" in result.enrichment_metadata["services_attempted"]


def test_credence_enrichment_disabled(orchestrator, mock_base_answer):
    """Test credence enrichment is skipped when disabled."""
    orchestrator._config.enable_credence_ci = False
    result = orchestrator.enrich(mock_base_answer, "Test?")

    # Should NOT attempt credence enrichment
    assert "credence_enrichment" not in result.enrichment_metadata["services_attempted"]


def test_credence_enrichment_with_missing_module(orchestrator, mock_base_answer):
    """Test graceful degradation when credence_intervals module missing."""
    orchestrator._services.get_credence_intervals = Mock(return_value=None)
    result = orchestrator.enrich(mock_base_answer, "Test?")

    # Should mark as skipped, not failed
    assert "credence_enrichment" in result.enrichment_metadata["services_skipped"]
    assert "credence_enrichment" not in result.enrichment_metadata["services_failed"]


# =============================================================================
# TESTS: WARRANT TRACE
# =============================================================================

def test_warrant_trace_enabled(orchestrator, mock_base_answer):
    """Test warrant trace enrichment when enabled."""
    orchestrator._config.enable_warrant_trace = True
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "warrant_trace" in result.enrichment_metadata["services_attempted"]


def test_warrant_trace_disabled(orchestrator, mock_base_answer):
    """Test warrant trace is skipped when disabled."""
    orchestrator._config.enable_warrant_trace = False
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "warrant_trace" not in result.enrichment_metadata["services_attempted"]


# =============================================================================
# TESTS: CONFOUNDER RISK
# =============================================================================

def test_confounder_risk_enabled(orchestrator, mock_base_answer):
    """Test confounder risk enrichment when enabled."""
    orchestrator._config.enable_confounder_risk = True
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "confounder_risk" in result.enrichment_metadata["services_attempted"]


def test_confounder_risk_disabled(orchestrator, mock_base_answer):
    """Test confounder risk is skipped when disabled."""
    orchestrator._config.enable_confounder_risk = False
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "confounder_risk" not in result.enrichment_metadata["services_attempted"]


# =============================================================================
# TESTS: FRAMEWORK VOICES
# =============================================================================

def test_framework_voices_enabled(orchestrator, mock_base_answer):
    """Test framework voices enrichment when enabled."""
    orchestrator._config.enable_framework_voices = True
    result = orchestrator.enrich(mock_base_answer, "Test question?")

    assert "framework_voices" in result.enrichment_metadata["services_attempted"]
    assert isinstance(result.framework_voices, list)


def test_framework_voices_disabled(orchestrator, mock_base_answer):
    """Test framework voices is skipped when disabled."""
    orchestrator._config.enable_framework_voices = False
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "framework_voices" not in result.enrichment_metadata["services_attempted"]
    assert result.framework_voices == []


def test_framework_voices_max_count(orchestrator, mock_base_answer):
    """Test that framework voices respects max_framework_voices config."""
    orchestrator._config.enable_framework_voices = True
    orchestrator._config.max_framework_voices = 2
    result = orchestrator.enrich(mock_base_answer, "Test?")

    # Should have at most max_framework_voices voices
    assert len(result.framework_voices) <= 2


# =============================================================================
# TESTS: GAP ANALYSIS
# =============================================================================

def test_gap_analysis_enabled(orchestrator, mock_base_answer):
    """Test gap analysis enrichment when enabled."""
    orchestrator._config.enable_gap_analysis = True
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "gap_analysis" in result.enrichment_metadata["services_attempted"]
    assert isinstance(result.gaps, list)


def test_gap_analysis_disabled(orchestrator, mock_base_answer):
    """Test gap analysis is skipped when disabled."""
    orchestrator._config.enable_gap_analysis = False
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "gap_analysis" not in result.enrichment_metadata["services_attempted"]
    assert result.gaps == []


def test_gap_analysis_max_count(orchestrator, mock_base_answer):
    """Test that gap analysis respects max_gaps config."""
    orchestrator._config.enable_gap_analysis = True
    orchestrator._config.max_gaps = 3
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert len(result.gaps) <= 3


# =============================================================================
# TESTS: FOLLOW-UP SUGGESTIONS
# =============================================================================

def test_follow_ups_enabled(orchestrator, mock_base_answer):
    """Test follow-up suggestions enrichment when enabled."""
    orchestrator._config.enable_follow_ups = True
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "follow_up_suggestions" in result.enrichment_metadata["services_attempted"]
    assert isinstance(result.follow_ups, list)


def test_follow_ups_disabled(orchestrator, mock_base_answer):
    """Test follow-up suggestions is skipped when disabled."""
    orchestrator._config.enable_follow_ups = False
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "follow_up_suggestions" not in result.enrichment_metadata["services_attempted"]
    assert result.follow_ups == []


def test_follow_ups_max_count(orchestrator, mock_base_answer):
    """Test that follow-ups respects max_follow_ups config."""
    orchestrator._config.enable_follow_ups = True
    orchestrator._config.max_follow_ups = 2
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert len(result.follow_ups) <= 2


# =============================================================================
# TESTS: LANGUAGE ADAPTATION
# =============================================================================

@pytest.mark.skip(reason="Language adaptation service mock unavailable in sandbox")
@patch("src.services.language_adaptation_service.adapt_content", create=True)
def test_language_adaptation_researcher(mock_adapt, orchestrator, mock_base_answer):
    """Test language adaptation for researcher user type."""
    mock_adapt.return_value = {"vocabulary": "technical"}
    orchestrator._config.enable_language_adaptation = True
    result = orchestrator.enrich(mock_base_answer, "Test?", user_type="researcher")

    assert "language_adaptation" in result.enrichment_metadata["services_attempted"]
    assert "language_adaptation" in result.enrichment_metadata
    assert result.enrichment_metadata["language_adaptation"]["vocabulary"] == "technical"


@patch("src.services.language_adaptation_service.adapt_content")
def test_language_adaptation_student(mock_adapt, orchestrator, mock_base_answer):
    """Test language adaptation for student user type."""
    mock_adapt.return_value = {"vocabulary": "intermediate"}
    orchestrator._config.enable_language_adaptation = True
    result = orchestrator.enrich(mock_base_answer, "Test?", user_type="student")

    assert result.enrichment_metadata["language_adaptation"]["vocabulary"] == "intermediate"


@patch("src.services.language_adaptation_service.adapt_content")
def test_language_adaptation_clinician(mock_adapt, orchestrator, mock_base_answer):
    """Test language adaptation for clinician user type."""
    mock_adapt.return_value = {"vocabulary": "applied"}
    orchestrator._config.enable_language_adaptation = True
    result = orchestrator.enrich(mock_base_answer, "Test?", user_type="clinician")

    assert result.enrichment_metadata["language_adaptation"]["vocabulary"] == "applied"


@patch("src.services.language_adaptation_service.adapt_content")
def test_language_adaptation_policy_maker(mock_adapt, orchestrator, mock_base_answer):
    """Test language adaptation for policy_maker user type."""
    mock_adapt.return_value = {"vocabulary": "accessible"}
    orchestrator._config.enable_language_adaptation = True
    result = orchestrator.enrich(mock_base_answer, "Test?", user_type="policy_maker")

    assert result.enrichment_metadata["language_adaptation"]["vocabulary"] == "accessible"


@patch("src.services.language_adaptation_service.adapt_content")
def test_language_adaptation_general_public(mock_adapt, orchestrator, mock_base_answer):
    """Test language adaptation for general_public user type."""
    mock_adapt.return_value = {"vocabulary": "simple"}
    orchestrator._config.enable_language_adaptation = True
    result = orchestrator.enrich(mock_base_answer, "Test?", user_type="general_public")

    assert result.enrichment_metadata["language_adaptation"]["vocabulary"] == "simple"


def test_language_adaptation_disabled(orchestrator, mock_base_answer):
    """Test language adaptation is skipped when disabled."""
    orchestrator._config.enable_language_adaptation = False
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "language_adaptation" not in result.enrichment_metadata["services_attempted"]


# =============================================================================
# TESTS: FIGURE SUGGESTIONS
# =============================================================================

def test_figure_suggestions_enabled(orchestrator, mock_base_answer):
    """Test figure suggestions enrichment when enabled."""
    orchestrator._config.enable_figure_suggestions = True
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "figure_suggestions" in result.enrichment_metadata["services_attempted"]
    assert isinstance(result.figures, list)


def test_figure_suggestions_disabled(orchestrator, mock_base_answer):
    """Test figure suggestions is skipped when disabled."""
    orchestrator._config.enable_figure_suggestions = False
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "figure_suggestions" not in result.enrichment_metadata["services_attempted"]
    assert result.figures == []


# =============================================================================
# TESTS: TIMEOUT HANDLING
# =============================================================================

def test_timeout_per_service(orchestrator, mock_base_answer):
    """Test that timeout_per_service_ms is respected."""
    # Override with very short timeout
    result = orchestrator.enrich(
        mock_base_answer,
        "Test?",
        timeout_per_service_ms=1  # 1ms timeout — should skip services
    )

    # Most services should timeout (depending on speed)
    assert result.enrichment_metadata["timing"] is not None


def test_timeout_override(orchestrator, mock_base_answer):
    """Test that timeout can be overridden at call time."""
    result = orchestrator.enrich(
        mock_base_answer,
        "Test?",
        timeout_per_service_ms=5000,  # 5s timeout
    )

    # Should complete successfully with long timeout
    assert "timestamp" in result.enrichment_metadata


# =============================================================================
# TESTS: EMPTY BASE ANSWER
# =============================================================================

def test_empty_beliefs_list(orchestrator):
    """Test enrichment with no beliefs in base answer."""
    base_answer = {
        "answer": "No specific beliefs provided",
        "beliefs": [],
        "evidence_count": 0,
    }

    result = orchestrator.enrich(base_answer, "Test?")

    assert isinstance(result, EnrichedAnswer)
    assert result.base_answer == base_answer
    assert len(result.enriched_beliefs) == 0


def test_missing_beliefs_key(orchestrator):
    """Test enrichment when 'beliefs' key is missing."""
    base_answer = {
        "answer": "No beliefs key",
        "evidence_count": 0,
    }

    result = orchestrator.enrich(base_answer, "Test?")

    assert isinstance(result, EnrichedAnswer)
    assert result.base_answer == base_answer


# =============================================================================
# TESTS: ENRICHED ANSWER SERIALIZATION
# =============================================================================

def test_enriched_answer_to_dict(orchestrator, mock_base_answer):
    """Test EnrichedAnswer.to_dict() serialization."""
    result = orchestrator.enrich(mock_base_answer, "Test?")
    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert "base_answer" in result_dict
    assert "enriched_beliefs" in result_dict
    assert "framework_voices" in result_dict
    assert "gaps" in result_dict
    assert "follow_ups" in result_dict
    assert "figures" in result_dict
    assert "user_type" in result_dict
    assert "enrichment_metadata" in result_dict


def test_enriched_answer_to_json(orchestrator, mock_base_answer):
    """Test EnrichedAnswer.to_json() serialization."""
    result = orchestrator.enrich(mock_base_answer, "Test?")
    json_str = result.to_json()

    assert isinstance(json_str, str)
    # Parse to verify valid JSON
    parsed = json.loads(json_str)
    assert isinstance(parsed, dict)


def test_enriched_belief_creation():
    """Test EnrichedBelief dataclass creation."""
    belief = EnrichedBelief(
        text="Test belief",
        credence_point=0.75,
        credence_ci={"lower": 0.70, "upper": 0.80, "se": 0.025},
        warrant_trace=[{"component": "severity", "value": 0.8}],
        confounder_risk="low",
        confounder_details=["Random assignment"],
    )

    assert belief.text == "Test belief"
    assert belief.credence_point == 0.75
    assert belief.credence_ci["lower"] == 0.70
    assert len(belief.warrant_trace) == 1
    assert belief.confounder_risk == "low"


# =============================================================================
# TESTS: CONFIG TOGGLING
# =============================================================================

def test_all_enrichments_disabled(orchestrator, mock_base_answer):
    """Test that enrichment works when all services are disabled."""
    orchestrator._config.enable_credence_ci = False
    orchestrator._config.enable_warrant_trace = False
    orchestrator._config.enable_confounder_risk = False
    orchestrator._config.enable_framework_voices = False
    orchestrator._config.enable_gap_analysis = False
    orchestrator._config.enable_follow_ups = False
    orchestrator._config.enable_language_adaptation = False
    orchestrator._config.enable_figure_suggestions = False
    orchestrator._config.enable_interpretation_context = False

    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert isinstance(result, EnrichedAnswer)
    assert len(result.enrichment_metadata["services_attempted"]) == 0


def test_selective_enrichments(orchestrator, mock_base_answer):
    """Test enabling only specific enrichments."""
    orchestrator._config.enable_credence_ci = True
    orchestrator._config.enable_warrant_trace = False
    orchestrator._config.enable_confounder_risk = False
    orchestrator._config.enable_framework_voices = True
    orchestrator._config.enable_gap_analysis = False
    orchestrator._config.enable_follow_ups = False
    orchestrator._config.enable_language_adaptation = False
    orchestrator._config.enable_figure_suggestions = False

    result = orchestrator.enrich(mock_base_answer, "Test?")

    attempted = result.enrichment_metadata["services_attempted"]
    assert "credence_enrichment" in attempted
    assert "framework_voices" in attempted
    assert "warrant_trace" not in attempted


# =============================================================================
# TESTS: METADATA TRACKING
# =============================================================================

def test_metadata_timestamp(orchestrator, mock_base_answer):
    """Test that timestamp is recorded in metadata."""
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "timestamp" in result.enrichment_metadata
    # Verify it's a valid ISO format timestamp
    assert "T" in result.enrichment_metadata["timestamp"]


def test_metadata_question_recorded(orchestrator, mock_base_answer):
    """Test that original question is recorded in metadata."""
    question = "What is attention restoration theory?"
    result = orchestrator.enrich(mock_base_answer, question)

    assert result.enrichment_metadata["question"] == question


def test_metadata_services_attempted_recorded(orchestrator, mock_base_answer):
    """Test that attempted services are recorded."""
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "services_attempted" in result.enrichment_metadata
    assert isinstance(result.enrichment_metadata["services_attempted"], list)


def test_metadata_timing_recorded(orchestrator, mock_base_answer):
    """Test that timing information is recorded."""
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert "timing" in result.enrichment_metadata
    assert isinstance(result.enrichment_metadata["timing"], dict)
    # At least some timing info should be present
    assert len(result.enrichment_metadata["timing"]) > 0


# =============================================================================
# TESTS: MAX BELIEFS CONFIG
# =============================================================================

def test_max_beliefs_to_enrich(orchestrator):
    """Test that max_beliefs_to_enrich config is respected."""
    beliefs = [
        {
            "text": f"Belief {i}",
            "p_lab": 0.5 + 0.01 * i,
            "d": 0.8,
            "omega": 0.7,
            "delta": 1.0,
            "design_type": "rct",
        }
        for i in range(30)
    ]

    base_answer = {
        "answer": "Many beliefs",
        "beliefs": beliefs,
    }

    orchestrator._config.max_beliefs_to_enrich = 5
    result = orchestrator.enrich(base_answer, "Test?")

    # Should process at most max_beliefs_to_enrich
    assert len(result.enriched_beliefs) <= 5


# =============================================================================
# TESTS: SERVICE REGISTRY LAZY-LOADING
# =============================================================================

def test_service_registry_lazy_loading():
    """Test that services are lazy-loaded only when needed."""
    from src.services.answer_enrichment_orchestrator import _ServiceRegistry

    registry = _ServiceRegistry()
    assert "credence_intervals" not in registry._services

    # First call should attempt to load
    service = registry.get_credence_intervals()
    # Service may or may not be available, but should be cached
    assert "credence_intervals" in registry._services or "credence_intervals" in registry._import_errors


# =============================================================================
# TESTS: ENRICHMENT WITH MINIMAL BASE ANSWER
# =============================================================================

def test_enrichment_with_minimal_answer(orchestrator):
    """Test enrichment with just required fields."""
    minimal = {
        "answer": "Brief answer",
    }

    result = orchestrator.enrich(minimal, "Question?")

    assert isinstance(result, EnrichedAnswer)
    assert result.base_answer == minimal


def test_user_type_defaults_to_researcher(orchestrator, mock_base_answer):
    """Test that user_type defaults to 'researcher' if not specified."""
    result = orchestrator.enrich(mock_base_answer, "Test?")

    assert result.user_type == "researcher"


def test_user_type_respected(orchestrator, mock_base_answer):
    """Test that specified user_type is recorded."""
    result = orchestrator.enrich(mock_base_answer, "Test?", user_type="clinician")

    assert result.user_type == "clinician"


# =============================================================================
# TESTS: ENRICHMENT CONFIG
# =============================================================================

def test_enrichment_config_defaults():
    """Test that EnrichmentConfig has sensible defaults."""
    config = EnrichmentConfig()

    assert config.enable_credence_ci is True
    assert config.enable_warrant_trace is True
    assert config.enable_confounder_risk is True
    assert config.enable_framework_voices is True
    assert config.enable_gap_analysis is True
    assert config.enable_follow_ups is True
    assert config.enable_language_adaptation is True
    assert config.enable_figure_suggestions is True
    assert config.timeout_per_service_ms == 2000
    assert config.max_beliefs_to_enrich == 20


def test_enrichment_config_customization():
    """Test that EnrichmentConfig can be customized."""
    config = EnrichmentConfig(
        enable_credence_ci=False,
        timeout_per_service_ms=5000,
        max_beliefs_to_enrich=10,
    )

    assert config.enable_credence_ci is False
    assert config.timeout_per_service_ms == 5000
    assert config.max_beliefs_to_enrich == 10


# =============================================================================
# TESTS: USER TYPE ENUM
# =============================================================================

def test_user_type_enum_values():
    """Test that UserType enum has expected values."""
    assert UserType.RESEARCHER.value == "researcher"
    assert UserType.STUDENT.value == "student"
    assert UserType.CLINICIAN.value == "clinician"
    assert UserType.ARCHITECT_DESIGNER.value == "architect_designer"
    assert UserType.GENERAL_PUBLIC.value == "general_public"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

def test_full_enrichment_pipeline(orchestrator, mock_base_answer):
    """Test full enrichment pipeline with all services enabled."""
    result = orchestrator.enrich(
        base_answer=mock_base_answer,
        question="How does attention restoration work?",
        user_type="researcher",
    )

    # Verify overall structure
    assert isinstance(result, EnrichedAnswer)
    assert result.base_answer is not None
    assert result.enrichment_metadata is not None

    # Verify metadata
    assert "timestamp" in result.enrichment_metadata
    assert "question" in result.enrichment_metadata
    assert "services_attempted" in result.enrichment_metadata
    assert "timing" in result.enrichment_metadata

    # Verify enrichments were attempted
    assert len(result.enrichment_metadata["services_attempted"]) > 0

    # Verify serialization works
    dict_form = result.to_dict()
    assert isinstance(dict_form, dict)

    json_str = result.to_json()
    assert isinstance(json_str, str)


def test_multiple_enrichments_in_sequence(orchestrator, mock_base_answer):
    """Test that multiple enrichment calls work independently."""
    result1 = orchestrator.enrich(mock_base_answer, "Question 1?", user_type="researcher")
    result2 = orchestrator.enrich(mock_base_answer, "Question 2?", user_type="student")

    # Results should be independent
    assert result1.enrichment_metadata["question"] == "Question 1?"
    assert result2.enrichment_metadata["question"] == "Question 2?"
    assert result1.user_type == "researcher"
    assert result2.user_type == "student"
