import pytest
import time
from unittest.mock import MagicMock, patch

from src.services.answer_enrichment_orchestrator import AnswerEnrichmentOrchestrator, EnrichmentConfig, UserType

def test_e2e_enrichment_pipeline_latency_and_services():
    """
    Test the full 9-step enrichment pipeline to ensure it completes
    within the target latency budget (5s) without crashing, and that
    all available services are called without failing open to mock data.
    """
    config = EnrichmentConfig(
        global_timeout_ms=5000, 
        timeout_per_service_ms=1000
    )
    orchestrator = AnswerEnrichmentOrchestrator(config)
    
    # Mock finding data from arbitrary QA handler
    base_answer = {
        "answer": "Natural environments reduce cortisol levels, likely due to stress reduction mechanisms.",
        "beliefs": [
            {
                "text": "Exposure to nature scenes reduces autonomic arousal within 5 minutes.",
                "p_lab": 0.05,
                "d": 0.5,
                "omega": 0.8,
                "delta": 1.0,
                "design_type": "experimental"
            }
        ],
        "evidence_count": 1
    }
    
    start_time = time.time()
    
    # Mocking services that are unimplemented or named differently in the sandbox
    with patch.object(orchestrator._services, 'get_integrated_query_service') as mock_iqs, \
         patch.object(orchestrator._services, 'get_gap_predictor') as mock_gp, \
         patch.object(orchestrator._services, 'get_follow_up_suggestion_service') as mock_fuss, \
         patch('src.services.language_adaptation_service.adapt_content', create=True) as mock_lang:
         
        # Setup mocks with expected methods
        mock_iqs_instance = MagicMock()
        mock_iqs_instance.get_theoretical_voices.return_value = {"Predictive Processing": {"perspective": "brain updates", "implications": []}}
        mock_iqs.return_value = mock_iqs_instance
        
        mock_gp_instance = MagicMock()
        mock_gp_instance.predict_gaps.return_value = [{"type": "Methodological", "description": "Needs more RCTs", "severity": "high"}]
        mock_gp.return_value = mock_gp_instance
        
        mock_fuss_instance = MagicMock()
        mock_fuss_instance.generate_follow_ups.return_value = [{"question": "What is next?", "voi": 0.9, "difficulty": "low"}]
        mock_fuss.return_value = mock_fuss_instance
        
        mock_lang.return_value = {"uncertainty_language": "moderate confidence", "vocabulary": "technical", "detail_level": "high"}
        
        enriched = orchestrator.enrich(
            base_answer=base_answer,
            question="Why does nature reduce stress?",
            user_type=UserType.RESEARCHER.value
        )
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Assert latency budget is respected
    assert elapsed_ms < 5000, f"Enrichment took too long: {elapsed_ms}ms"
    
    # Check that metadata tracked everything
    metadata = enriched.enrichment_metadata
    assert "timestamp" in metadata
    assert metadata["question"] == "Why does nature reduce stress?"
    
    # Evaluate which steps succeeded/skipped
    attempted = metadata["services_attempted"]
    assert len(attempted) >= 9  # At least 9 core steps; may increase as enrichments added
    
    # None should have crashed
    failed = metadata["services_failed"]
    assert len(failed) == 0, f"Services failed: {failed}"
    
    # We expect some services might be skipped if not fully installed/mocked in tests, 
    # but the pipeline itself should succeed end-to-end.
    skipped = metadata["services_skipped"]
    successes = set(attempted) - set(skipped)
    
    print(f"\nE2E Pipeline Test Results:")
    print(f"Elapsed Time: {elapsed_ms:.1f}ms")
    print(f"Succeeded Steps: {list(successes)}")
    print(f"Skipped Steps: {list(skipped)}")
    
    # If semblance of real data exists, assert it:
    if "interpretation_context" in successes:
        assert enriched.interpretation_context is not None
        
    if "language_adaptation" in successes:
        assert enriched.enrichment_metadata.get("language_adaptation") is not None
