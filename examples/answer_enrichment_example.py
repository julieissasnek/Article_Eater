"""
Example: Using the Answer Enrichment Orchestrator

This example shows how to integrate the orchestrator into the ATLAS answer pipeline.

Author: Claude Code (agent for Prof. David Kirsh, UCSD Cognitive Science)
Date: 2026-03-03
"""

from src.services.answer_enrichment_orchestrator import (
    AnswerEnrichmentOrchestrator,
    EnrichmentConfig,
    create_orchestrator,
    enrich_answer,
)
from src.services.arbitrary_qa_handler import ArbitraryQAHandler


# =============================================================================
# EXAMPLE 1: Basic enrichment with defaults
# =============================================================================

def example_basic_enrichment():
    """Basic enrichment with all services enabled (default config)."""

    # Create orchestrator with default config
    orchestrator = create_orchestrator()

    # Get a base answer from the QA handler
    qa_handler = ArbitraryQAHandler()
    base_answer = qa_handler.answer("What is attention restoration theory?")

    # Enrich the answer
    enriched = orchestrator.enrich(
        base_answer=base_answer,
        question="What is attention restoration theory?",
        user_type="researcher",
    )

    # Access enriched components
    print(f"Framework voices ({len(enriched.framework_voices)}):")
    for voice in enriched.framework_voices:
        print(f"  - {voice['framework']}: {voice['voice']}")

    print(f"\nIdentified gaps ({len(enriched.gaps)}):")
    for gap in enriched.gaps:
        print(f"  - {gap['gap_type']}: {gap['description']} (VOI: {gap['voi_score']:.2f})")

    print(f"\nFollow-up questions ({len(enriched.follow_ups)}):")
    for follow_up in enriched.follow_ups[:3]:
        print(f"  - {follow_up['question']} (VOI: {follow_up['voi']:.2f})")


# =============================================================================
# EXAMPLE 2: Selective enrichment
# =============================================================================

def example_selective_enrichment():
    """Enable only specific enrichments (e.g., for performance-critical scenarios)."""

    # Create config with only credence and framework voices
    config = EnrichmentConfig(
        enable_credence_ci=True,
        enable_warrant_trace=True,
        enable_confounder_risk=False,
        enable_framework_voices=True,
        enable_gap_analysis=False,
        enable_follow_ups=False,
        enable_language_adaptation=False,
        enable_figure_suggestions=False,
        timeout_per_service_ms=1000,  # Short timeout
    )

    orchestrator = AnswerEnrichmentOrchestrator(config)

    # Use the convenience function
    qa_handler = ArbitraryQAHandler()
    base_answer = qa_handler.answer("How does green space affect stress recovery?")

    enriched = enrich_answer(
        base_answer=base_answer,
        question="How does green space affect stress recovery?",
        user_type="clinician",
        config=config,
    )

    # Show which services ran
    print("Services attempted:")
    for service in enriched.enrichment_metadata["services_attempted"]:
        elapsed = enriched.enrichment_metadata["timing"].get(service, 0)
        print(f"  - {service}: {elapsed:.1f}ms")


# =============================================================================
# EXAMPLE 3: User type adaptation
# =============================================================================

def example_user_type_adaptation():
    """Adapt answer enrichment based on user persona."""

    orchestrator = create_orchestrator()
    qa_handler = ArbitraryQAHandler()
    base_answer = qa_handler.answer("What is biophilia?")

    user_types = ["researcher", "student", "clinician", "policy_maker", "general_public"]

    for user_type in user_types:
        enriched = orchestrator.enrich(
            base_answer=base_answer,
            question="What is biophilia?",
            user_type=user_type,
        )

        adaptation = enriched.enrichment_metadata.get("language_adaptation", {})
        print(f"\n{user_type.upper()}:")
        print(f"  Vocabulary: {adaptation.get('vocabulary', 'N/A')}")
        print(f"  Detail level: {adaptation.get('detail_level', 'N/A')}")
        print(f"  Uncertainty language: {adaptation.get('uncertainty_language', 'N/A')}")


# =============================================================================
# EXAMPLE 4: Tight timeout for real-time performance
# =============================================================================

def example_fast_enrichment():
    """Fast enrichment with tight timeout for real-time scenarios."""

    config = EnrichmentConfig(
        enable_credence_ci=True,
        enable_warrant_trace=False,
        enable_confounder_risk=False,
        enable_framework_voices=True,
        enable_gap_analysis=False,
        enable_follow_ups=False,
        enable_language_adaptation=True,
        enable_figure_suggestions=False,
        timeout_per_service_ms=500,  # Very tight timeout
    )

    orchestrator = AnswerEnrichmentOrchestrator(config)

    qa_handler = ArbitraryQAHandler()
    base_answer = qa_handler.answer("What theories explain environmental psychology effects?")

    enriched = orchestrator.enrich(
        base_answer=base_answer,
        question="What theories explain environmental psychology effects?",
        user_type="student",
    )

    # Show which services succeeded vs. timed out
    print("Services completed successfully:")
    for service in enriched.enrichment_metadata["services_attempted"]:
        if service not in enriched.enrichment_metadata["services_failed"]:
            elapsed = enriched.enrichment_metadata["timing"].get(service, 0)
            print(f"  - {service}: {elapsed:.1f}ms")

    print("\nServices that timed out:")
    for service in enriched.enrichment_metadata["services_failed"]:
        print(f"  - {service}")


# =============================================================================
# EXAMPLE 5: JSON output for downstream processing
# =============================================================================

def example_json_output():
    """Export enriched answer as JSON for downstream processing."""

    import json

    orchestrator = create_orchestrator()
    qa_handler = ArbitraryQAHandler()
    base_answer = qa_handler.answer("What is prospect-refuge theory?")

    enriched = orchestrator.enrich(
        base_answer=base_answer,
        question="What is prospect-refuge theory?",
        user_type="researcher",
    )

    # Export as JSON
    json_output = enriched.to_json()

    # Pretty-print (truncated)
    data = json.loads(json_output)
    print("Enriched answer structure:")
    print(f"  - base_answer: {len(str(data['base_answer']))} chars")
    print(f"  - enriched_beliefs: {len(data['enriched_beliefs'])} beliefs")
    print(f"  - framework_voices: {len(data['framework_voices'])} voices")
    print(f"  - gaps: {len(data['gaps'])} gaps")
    print(f"  - follow_ups: {len(data['follow_ups'])} follow-ups")
    print(f"  - figures: {len(data['figures'])} figures")
    print(f"  - user_type: {data['user_type']}")
    print(f"\nMetadata:")
    print(f"  - timestamp: {data['enrichment_metadata']['timestamp']}")
    print(f"  - services_attempted: {data['enrichment_metadata']['services_attempted']}")
    print(f"  - services_failed: {data['enrichment_metadata']['services_failed']}")
    print(f"  - services_skipped: {data['enrichment_metadata']['services_skipped']}")


# =============================================================================
# EXAMPLE 6: Graceful degradation with missing modules
# =============================================================================

def example_graceful_degradation():
    """Demonstrate graceful degradation when services are unavailable."""

    orchestrator = create_orchestrator()
    qa_handler = ArbitraryQAHandler()
    base_answer = qa_handler.answer("What is spatial navigation?")

    # Mock missing service
    orchestrator._services.get_credence_intervals = lambda: None

    enriched = orchestrator.enrich(
        base_answer=base_answer,
        question="What is spatial navigation?",
        user_type="researcher",
    )

    # Show that system still works despite missing service
    print("Enrichment completed despite missing module:")
    print(f"  - Services attempted: {enriched.enrichment_metadata['services_attempted']}")
    print(f"  - Services skipped: {enriched.enrichment_metadata['services_skipped']}")
    print(f"  - Services failed: {enriched.enrichment_metadata['services_failed']}")
    print(f"\nAnswer still enriched with:")
    print(f"  - Framework voices: {len(enriched.framework_voices)}")
    print(f"  - Gaps: {len(enriched.gaps)}")
    print(f"  - Follow-ups: {len(enriched.follow_ups)}")


if __name__ == "__main__":
    print("=" * 80)
    print("EXAMPLE 1: Basic Enrichment")
    print("=" * 80)
    try:
        example_basic_enrichment()
    except Exception as e:
        print(f"Note: {e}")

    print("\n" + "=" * 80)
    print("EXAMPLE 2: Selective Enrichment")
    print("=" * 80)
    try:
        example_selective_enrichment()
    except Exception as e:
        print(f"Note: {e}")

    print("\n" + "=" * 80)
    print("EXAMPLE 3: User Type Adaptation")
    print("=" * 80)
    try:
        example_user_type_adaptation()
    except Exception as e:
        print(f"Note: {e}")

    print("\n" + "=" * 80)
    print("EXAMPLE 4: Fast Enrichment (Tight Timeout)")
    print("=" * 80)
    try:
        example_fast_enrichment()
    except Exception as e:
        print(f"Note: {e}")

    print("\n" + "=" * 80)
    print("EXAMPLE 5: JSON Output")
    print("=" * 80)
    try:
        example_json_output()
    except Exception as e:
        print(f"Note: {e}")

    print("\n" + "=" * 80)
    print("EXAMPLE 6: Graceful Degradation")
    print("=" * 80)
    try:
        example_graceful_degradation()
    except Exception as e:
        print(f"Note: {e}")
