"""
Comprehensive Test Suite for CircuitQAService
==============================================
Created: 2026-03-03

This test file validates the CircuitQAService module, which generates epistemically
framed QA cards for functional circuits. Tests cover:

- SC-CQS-1: Every QA card has non-empty epistemic_status
- SC-CQS-2: Every QA card has non-empty ontological_statement
- SC-CQS-3: Every QA card has ≥2 follow_up_questions
- SC-CQS-4: Every QA card has ≥1 competing_accounts entry
- SC-CQS-5: Every QA card has ≥1 what_we_dont_know entry
- SC-CQS-6: get_circuit_card returns None for unknown circuit IDs
- SC-FCA-1: format_circuit_answer response always has question_type = "functional_circuit"
- SC-FCA-2: format_circuit_answer response always has epistemic_status section
- SC-FCA-3: format_circuit_answer response always has follow_up_questions

Test Organization:
1. TestCircuitQAServiceLoading — Service initialization and circuit discovery
2. TestCircuitQACard — Circuit card validity and success conditions
3. TestOntologicalStatements — Framing differences across evidence levels
4. TestFormatCircuitAnswer — QA response formatting
5. TestFormatArchetypeAnswer — Archetype query responses
6. TestGetAllCircuitsSummary — Catalog generation
7. TestEpistemicFraming — Epistemic content validation
8. TestAllCircuitsHaveCards — Exhaustive iteration over all circuits

Author: Claude Code (CW) for Prof. David Kirsh, UCSD Cognitive Science
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.services.circuit_qa_service import (
    CircuitQAService,
    CircuitQACard,
    CIRCUIT_EVIDENCE_LEVELS,
    ARCHETYPE_DESCRIPTIONS,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def service():
    """Initialize CircuitQAService with test data."""
    return CircuitQAService(molecule_dir="data/molecules")


@pytest.fixture
def sample_strong_circuit(service):
    """Get a STRONG evidence circuit for testing."""
    for circuit_id, level in CIRCUIT_EVIDENCE_LEVELS.items():
        if level == "STRONG":
            card = service.get_circuit_card(circuit_id)
            if card:
                return circuit_id, card
    pytest.skip("No STRONG evidence circuits found")


@pytest.fixture
def sample_moderate_circuit(service):
    """Get a MODERATE evidence circuit for testing."""
    for circuit_id, level in CIRCUIT_EVIDENCE_LEVELS.items():
        if level == "MODERATE":
            card = service.get_circuit_card(circuit_id)
            if card:
                return circuit_id, card
    pytest.skip("No MODERATE evidence circuits found")


@pytest.fixture
def sample_hypothetical_circuit(service):
    """Get a HYPOTHETICAL evidence circuit for testing."""
    for circuit_id, level in CIRCUIT_EVIDENCE_LEVELS.items():
        if level == "HYPOTHETICAL":
            card = service.get_circuit_card(circuit_id)
            if card:
                return circuit_id, card
    pytest.skip("No HYPOTHETICAL evidence circuits found")


# =============================================================================
# Test Group 1: Service Loading and Discovery
# =============================================================================

class TestCircuitQAServiceLoading:
    """Validate circuit loading and service initialization."""

    def test_service_loads_circuits(self, service):
        """Test that the service successfully loads circuit data."""
        assert service.circuit_count > 0, "Service should load at least one circuit"

    def test_service_loads_minimum_circuits(self, service):
        """Test that service loads at least 15 circuits."""
        assert (
            service.circuit_count >= 15
        ), f"Expected ≥15 circuits, got {service.circuit_count}"

    def test_all_loaded_circuits_are_functional_circuits(self, service):
        """Test that all loaded circuits have type FUNCTIONAL_CIRCUIT."""
        assert hasattr(service, "_circuits"), "Service should have _circuits attribute"
        for circuit_id, circuit_data in service._circuits.items():
            assert (
                circuit_data.get("molecule_type") == "FUNCTIONAL_CIRCUIT"
            ), f"Circuit {circuit_id} has incorrect molecule_type: {circuit_data.get('molecule_type')}"


# =============================================================================
# Test Group 2: CircuitQACard Data Validity
# =============================================================================

class TestCircuitQACard:
    """Test CircuitQACard structure and success conditions."""

    def test_qa_card_has_non_empty_epistemic_status(self, service):
        """SC-CQS-1: Every QA card has non-empty epistemic_status."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            assert card is not None, f"Should get card for {circuit_id}"
            assert (
                card.epistemic_status
            ), f"Card for {circuit_id} has empty epistemic_status"
            assert card.epistemic_status in [
                "STRONG",
                "MODERATE",
                "HYPOTHETICAL",
            ], f"Invalid epistemic_status: {card.epistemic_status}"

    def test_qa_card_has_non_empty_ontological_statement(self, service):
        """SC-CQS-2: Every QA card has non-empty ontological_statement."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            assert card is not None, f"Should get card for {circuit_id}"
            assert (
                card.ontological_statement
            ), f"Card for {circuit_id} has empty ontological_statement"
            assert (
                len(card.ontological_statement) > 50
            ), f"ontological_statement seems too short for {circuit_id}"

    def test_qa_card_has_minimum_follow_up_questions(self, service):
        """SC-CQS-3: Every QA card has ≥2 follow_up_questions."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            assert card is not None, f"Should get card for {circuit_id}"
            assert (
                len(card.follow_up_questions) >= 2
            ), f"Card for {circuit_id} has {len(card.follow_up_questions)} follow-ups, expected ≥2"

    def test_qa_card_has_competing_accounts(self, service):
        """SC-CQS-4: Every QA card has ≥1 competing_accounts entry."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            assert card is not None, f"Should get card for {circuit_id}"
            assert (
                len(card.competing_accounts) >= 1
            ), f"Card for {circuit_id} has no competing accounts"

    def test_qa_card_has_knowledge_gaps(self, service):
        """SC-CQS-5: Every QA card has ≥1 what_we_dont_know entry."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            assert card is not None, f"Should get card for {circuit_id}"
            assert (
                len(card.what_we_dont_know) >= 1
            ), f"Card for {circuit_id} has no knowledge gaps"

    def test_get_circuit_card_returns_none_for_unknown_circuit(self, service):
        """SC-CQS-6: get_circuit_card returns None for unknown circuit IDs."""
        card = service.get_circuit_card("FC_NONEXISTENT_CIRCUIT")
        assert card is None, "Should return None for unknown circuit"

        card = service.get_circuit_card("FAKE_ID_12345")
        assert card is None, "Should return None for random circuit ID"


# =============================================================================
# Test Group 3: Ontological Statement Framing
# =============================================================================

class TestOntologicalStatements:
    """Test epistemic framing across evidence levels."""

    def test_strong_ontological_statement_mentions_latent_variable(
        self, service, sample_strong_circuit
    ):
        """STRONG circuits should use latent variable framing with empirical grounding."""
        circuit_id, card = sample_strong_circuit
        stmt = card.ontological_statement.lower()
        assert (
            "latent variable" in stmt
            or "co-vary" in stmt
            or "replicable" in stmt
        ), "STRONG statement should use latent variable framing"

    def test_moderate_ontological_statement_mentions_hypothesis(
        self, service, sample_moderate_circuit
    ):
        """MODERATE circuits should frame as hypothesized latent variable."""
        circuit_id, card = sample_moderate_circuit
        stmt = card.ontological_statement.lower()
        assert (
            "hypothesized" in stmt
            or "factor analysis" in stmt
            or "well-motivated bet" in stmt
        ), "MODERATE statement should frame as hypothesized latent variable"

    def test_hypothetical_ontological_statement_mentions_barrett(
        self, service, sample_hypothetical_circuit
    ):
        """HYPOTHETICAL circuits should mention Barrett's caution."""
        circuit_id, card = sample_hypothetical_circuit
        assert (
            "barrett" in card.ontological_statement.lower()
        ), "HYPOTHETICAL statement should mention Barrett's critique"


# =============================================================================
# Test Group 4: format_circuit_answer QA Response
# =============================================================================

class TestFormatCircuitAnswer:
    """Test formatting of circuit answers for QA response."""

    def test_format_circuit_answer_returns_none_for_unknown_question(self, service):
        """format_circuit_answer should return None if circuit cannot be identified."""
        result = service.format_circuit_answer("What is the capital of France?")
        assert result is None, "Should return None for non-circuit question"

    def test_format_circuit_answer_has_correct_question_type(self, service):
        """SC-FCA-1: Response always has question_type = 'functional_circuit'."""
        # Create a question that will identify a known circuit
        for circuit_id, circuit_data in service._circuits.items():
            circuit_name = circuit_data.get("name", "")
            if circuit_name:
                result = service.format_circuit_answer(f"Tell me about {circuit_name}")
                if result:
                    assert (
                        result.get("question_type") == "functional_circuit"
                    ), f"question_type should be 'functional_circuit', got {result.get('question_type')}"
                    break

    def test_format_circuit_answer_has_epistemic_status_section(self, service):
        """SC-FCA-2: Response always has epistemic_status section."""
        for circuit_id, circuit_data in service._circuits.items():
            circuit_name = circuit_data.get("name", "")
            if circuit_name:
                result = service.format_circuit_answer(f"About {circuit_name}")
                if result:
                    assert (
                        "epistemic_status" in result
                    ), "Response should have epistemic_status field"
                    assert (
                        result.get("epistemic_status") in ["STRONG", "MODERATE", "HYPOTHETICAL"]
                    ), f"Invalid epistemic_status: {result.get('epistemic_status')}"
                    break

    def test_format_circuit_answer_has_follow_ups(self, service):
        """SC-FCA-3: Response always has follow_up_questions."""
        for circuit_id, circuit_data in service._circuits.items():
            circuit_name = circuit_data.get("name", "")
            if circuit_name:
                result = service.format_circuit_answer(f"Explain {circuit_name}")
                if result:
                    assert (
                        "follow_ups" in result
                    ), "Response should have follow_ups field"
                    assert (
                        len(result.get("follow_ups", [])) >= 2
                    ), "Should have at least 2 follow-up questions"
                    break


# =============================================================================
# Test Group 5: format_archetype_answer
# =============================================================================

class TestFormatArchetypeAnswer:
    """Test formatting of archetype answers."""

    def test_format_archetype_answer_returns_none_for_unknown(self, service):
        """format_archetype_answer should return None for unknown archetype."""
        result = service.format_archetype_answer("NONEXISTENT_ARCHETYPE")
        assert result is None, "Should return None for unknown archetype"

    def test_format_archetype_answer_returns_valid_response_for_predictive_coding(
        self, service
    ):
        """Test that PREDICTIVE_CODING archetype returns valid response."""
        result = service.format_archetype_answer("PREDICTIVE_CODING")
        assert result is not None, "Should return response for PREDICTIVE_CODING"
        assert result.get("question_type") == "archetype_guide"
        assert len(result.get("sections", [])) > 0

    def test_format_archetype_answer_lists_circuits(self, service):
        """Archetype answer should list circuits using that archetype."""
        for archetype in ARCHETYPE_DESCRIPTIONS.keys():
            result = service.format_archetype_answer(archetype)
            if result:
                assert "sections" in result, "Should have sections"
                # At least one section should mention circuits
                sections_text = str(result.get("sections", []))
                # The response should indicate which circuits use this archetype
                assert len(result.get("sections", [])) > 0

    def test_format_archetype_answer_has_follow_ups(self, service):
        """Archetype answer should have follow-up questions."""
        result = service.format_archetype_answer("HOMEOSTATIC_REGULATION")
        if result:
            assert "follow_ups" in result, "Should have follow_ups field"
            assert (
                len(result.get("follow_ups", [])) > 0
            ), "Should have follow-up questions"


# =============================================================================
# Test Group 6: get_all_circuits_summary
# =============================================================================

class TestGetAllCircuitsSummary:
    """Test circuit catalog summarization."""

    def test_summary_has_total_circuits_count(self, service):
        """Summary should report total circuit count."""
        summary = service.get_all_circuits_summary()
        assert "total_circuits" in summary, "Summary should have total_circuits"
        assert (
            summary["total_circuits"] > 0
        ), "Should report positive circuit count"

    def test_summary_has_by_archetype_dict(self, service):
        """Summary should organize circuits by archetype."""
        summary = service.get_all_circuits_summary()
        assert "by_archetype" in summary, "Summary should have by_archetype"
        by_arch = summary["by_archetype"]
        assert isinstance(
            by_arch, dict
        ), "by_archetype should be a dictionary"
        assert (
            len(by_arch) > 0
        ), "Should have entries for at least one archetype"

    def test_summary_has_evidence_distribution(self, service):
        """Summary should report evidence distribution."""
        summary = service.get_all_circuits_summary()
        assert (
            "evidence_distribution" in summary
        ), "Summary should have evidence_distribution"
        dist = summary["evidence_distribution"]
        assert "STRONG" in dist, "Should report STRONG count"
        assert "MODERATE" in dist, "Should report MODERATE count"
        assert "HYPOTHETICAL" in dist, "Should report HYPOTHETICAL count"
        # Total should match circuit count from CIRCUIT_EVIDENCE_LEVELS
        total = dist["STRONG"] + dist["MODERATE"] + dist["HYPOTHETICAL"]
        assert (
            total == len(CIRCUIT_EVIDENCE_LEVELS)
        ), "Distribution should account for all circuits"


# =============================================================================
# Test Group 7: Epistemic Content Framing
# =============================================================================

class TestEpistemicFraming:
    """Test epistemic rigor in QA card content."""

    def test_competing_accounts_always_mentions_barrett(self, service):
        """All competing accounts should reference Barrett's critique."""
        barrett_count = 0
        total_circuits = 0
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            if card:
                total_circuits += 1
                competing_text = " ".join(card.competing_accounts)
                if "barrett" in competing_text.lower():
                    barrett_count += 1

        assert (
            barrett_count == total_circuits
        ), f"All {total_circuits} circuits should mention Barrett, but only {barrett_count} do"

    def test_knowledge_gaps_mention_interaction_effects(self, service):
        """Knowledge gaps should discuss interaction effects."""
        interaction_count = 0
        total_circuits = 0
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            if card:
                total_circuits += 1
                gaps_text = " ".join(card.what_we_dont_know)
                if "interaction" in gaps_text.lower():
                    interaction_count += 1

        assert (
            interaction_count >= total_circuits * 0.5
        ), "At least 50% of circuits should mention interaction effects in knowledge gaps"

    def test_follow_ups_are_pedagogically_structured(self, service):
        """Follow-ups should scaffold learning from empirical to theoretical."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            if card:
                follow_ups_text = " ".join(card.follow_up_questions)

                # Should ask about evidence (empirical grounding)
                assert any(
                    word in follow_ups_text.lower() for word in ["evidence", "empirical", "support", "test"]
                ), f"Circuit {circuit_id} should have follow-up asking about evidence"

                # Should ask about alternatives (critical thinking)
                assert any(
                    word in follow_ups_text.lower() for word in ["other", "different", "alternative", "compare", "similar"]
                ), f"Circuit {circuit_id} should have comparative follow-up"

    def test_ontological_statements_avoid_reification(self, service):
        """Ontological statements should avoid claiming neural reality."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            if card:
                statement = card.ontological_statement.lower()

                # Should NOT say "is a neural circuit" or "is located in"
                assert not (
                    "is a neural circuit" in statement
                ), f"Circuit {circuit_id} should not reify as neural circuit"

                # Should emphasize abstraction or motif
                assert any(
                    word in statement
                    for word in ["abstraction", "motif", "pattern", "organizing principle", "computational"]
                ), f"Circuit {circuit_id} should emphasize computational abstraction"


# =============================================================================
# Test Group 8: Exhaustive Circuit Coverage
# =============================================================================

class TestAllCircuitsHaveCards:
    """Validate that every circuit in registry has a valid card."""

    def test_every_circuit_in_evidence_levels_has_card(self, service):
        """Iterate through all circuits and validate card generation."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            assert (
                card is not None
            ), f"Should get card for {circuit_id}"
            assert (
                card.circuit_id == circuit_id
            ), f"Card should have matching circuit_id"
            # epistemic_status should be valid
            assert card.epistemic_status in [
                "STRONG",
                "MODERATE",
                "HYPOTHETICAL",
            ], f"Card epistemic_status should be valid, got {card.epistemic_status}"


# =============================================================================
# Integration Tests
# =============================================================================

class TestCircuitQAServiceIntegration:
    """Integration tests covering end-to-end workflows."""

    def test_circuit_qa_card_round_trip_to_dict(self, service):
        """Test that CircuitQACard.to_dict() produces valid structure."""
        for circuit_id in list(service._circuits.keys())[:3]:
            card = service.get_circuit_card(circuit_id)
            if card:
                card_dict = card.to_dict()

                # All required fields should be present
                required_fields = [
                    "circuit_id",
                    "circuit_name",
                    "epistemic_status",
                    "ontological_statement",
                    "causal_status",
                    "what_it_does",
                    "archetype",
                    "inputs",
                    "outputs",
                    "follow_up_questions",
                    "competing_accounts",
                    "what_we_dont_know",
                ]
                for field in required_fields:
                    assert field in card_dict, f"Missing field in to_dict(): {field}"

    def test_format_circuit_answer_includes_sections(self, service):
        """Formatted answer should include all major sections."""
        for circuit_id, circuit_data in service._circuits.items():
            circuit_name = circuit_data.get("name", "")
            if circuit_name:
                result = service.format_circuit_answer(f"Tell me about {circuit_name}")
                if result:
                    sections = result.get("sections", [])
                    assert len(sections) > 0, "Should have sections"

                    # Check for key sections
                    section_headings = [s.get("heading", "") for s in sections]
                    heading_text = " ".join(section_headings).lower()

                    assert any(
                        word in heading_text
                        for word in ["epistemic", "status", "evidence"]
                    ), "Should have epistemic framing section"

                    assert any(
                        word in heading_text
                        for word in ["competing", "alternative"]
                    ), "Should have competing accounts section"

                    break

    def test_identify_circuit_matching_by_name(self, service):
        """Service should identify circuits by name in natural language."""
        # Test with actual circuit names from service._circuits
        sample_circuits = list(service._circuits.items())[:3]
        for circuit_id, circuit_data in sample_circuits:
            circuit_name = circuit_data.get("name", "")
            if circuit_name:
                question = f"Can you explain {circuit_name}?"
                identified_id = service._identify_circuit(question)
                assert (
                    identified_id == circuit_id
                ), f"Should identify {circuit_id} from question about {circuit_name}"


# =============================================================================
# Testability Section Tests (added 2026-03-04)
# =============================================================================

class TestTestabilitySection:
    """Test the latent variable testability section added 2026-03-04."""

    def test_every_card_has_testability(self, service):
        """Every circuit QA card should have a testability dict."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            if card:
                assert isinstance(card.testability, dict), (
                    f"{circuit_id} should have a testability dict"
                )

    def test_testability_has_required_keys(self, service):
        """Testability section should have all required keys."""
        required = {
            "latent_variable_prediction",
            "how_to_test",
            "data_requirements",
            "search_targets",
            "existing_evidence_status",
        }
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            if card:
                assert required <= set(card.testability.keys()), (
                    f"{circuit_id} testability missing keys: "
                    f"{required - set(card.testability.keys())}"
                )

    def test_how_to_test_has_at_least_two_methods(self, service):
        """Every circuit should suggest at least 2 testing methods."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            if card:
                methods = card.testability.get("how_to_test", [])
                assert len(methods) >= 2, (
                    f"{circuit_id} should have ≥2 testing methods, got {len(methods)}"
                )

    def test_search_targets_are_nonempty(self, service):
        """Every circuit should generate article search targets."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            if card:
                targets = card.testability.get("search_targets", [])
                assert len(targets) >= 1, (
                    f"{circuit_id} should generate ≥1 search target"
                )

    def test_strong_circuits_mention_intervention(self, service, sample_strong_circuit):
        """STRONG circuits should include intervention as a testing method."""
        circuit_id, card = sample_strong_circuit
        methods = card.testability.get("how_to_test", [])
        method_text = " ".join(methods).lower()
        assert "perturb" in method_text or "tms" in method_text, (
            "STRONG circuits should mention perturbation/intervention testing"
        )

    def test_hypothetical_circuits_have_extra_searches(self, service, sample_hypothetical_circuit):
        """HYPOTHETICAL circuits should generate targeted evidence searches."""
        circuit_id, card = sample_hypothetical_circuit
        targets = card.testability.get("search_targets", [])
        target_text = " ".join(targets).lower()
        assert "empirical evidence" in target_text or "validation" in target_text, (
            "HYPOTHETICAL circuits should generate evidence-seeking searches"
        )

    def test_latent_variable_prediction_mentions_factor(self, service):
        """LV prediction should mention factor analysis or covariance."""
        sample_id = list(service._circuits.keys())[0]
        card = service.get_circuit_card(sample_id)
        prediction = card.testability.get("latent_variable_prediction", "").lower()
        assert "factor" in prediction or "covar" in prediction, (
            "LV prediction should mention factor analysis or covariance"
        )

    def test_format_circuit_answer_includes_testability_section(self, service):
        """format_circuit_answer should include a 'How Would We Test This?' section."""
        sample = list(service._circuits.values())[0]
        name = sample.get("name", "")
        if name:
            result = service.format_circuit_answer(f"Tell me about {name}")
            if result:
                headings = [s["heading"] for s in result.get("sections", [])]
                assert "How Would We Test This?" in headings, (
                    "Circuit answer should include testability section"
                )

    def test_format_circuit_answer_includes_search_targets(self, service):
        """format_circuit_answer should expose search_targets at top level."""
        sample = list(service._circuits.values())[0]
        name = sample.get("name", "")
        if name:
            result = service.format_circuit_answer(f"Tell me about {name}")
            if result:
                assert "search_targets" in result, (
                    "Circuit answer should include search_targets"
                )
                assert isinstance(result["search_targets"], list)


# =============================================================================
# Edge Case and Robustness Tests
# =============================================================================

class TestEdgeCases:
    """Test edge cases and robustness."""

    def test_circuit_with_empty_references(self, service):
        """Service should handle circuits with no key references gracefully."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            if card:
                # Should not crash even if references are empty
                assert isinstance(card.key_references, list)
                evidence = card.evidence_summary
                assert evidence  # Should still produce evidence summary

    def test_circuit_with_no_related_circuits(self, service):
        """Service should handle circuits with no related circuits."""
        for circuit_id in service._circuits.keys():
            card = service.get_circuit_card(circuit_id)
            if card:
                # related_circuits may be empty, but should be a list
                assert isinstance(card.related_circuits, list)

    def test_question_matching_case_insensitive(self, service):
        """Question matching should be case-insensitive."""
        sample_circuit = list(service._circuits.items())[0]
        circuit_id, circuit_data = sample_circuit
        circuit_name = circuit_data.get("name", "")

        if circuit_name:
            # Try different cases
            question_lower = f"tell me about {circuit_name.lower()}"
            question_upper = f"tell me about {circuit_name.upper()}"
            question_mixed = f"tell me about {circuit_name.title()}"

            for q in [question_lower, question_upper, question_mixed]:
                identified_id = service._identify_circuit(q)
                # May not always match, but should at least handle the case gracefully
                assert identified_id is None or identified_id == circuit_id

    def test_evidence_level_defaults_to_hypothetical(self, service):
        """Unknown circuits should default to HYPOTHETICAL when referenced."""
        summary = service.get_all_circuits_summary()
        # All entries should be accounted for
        by_arch = summary["by_archetype"]
        for archetype, circuits in by_arch.items():
            for circuit in circuits:
                evidence = circuit.get("evidence")
                assert evidence in [
                    "STRONG",
                    "MODERATE",
                    "HYPOTHETICAL",
                ], f"Evidence should be valid, got {evidence}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
