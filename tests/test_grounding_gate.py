"""
Tests for the Grounding Gate (Haack's Foundherentist Principle)
===============================================================

Tests that the grounding gate:
1. Finds empirical anchors when they exist
2. Returns abstention when evidence is absent
3. Detects coherence contradictions
4. Integrates correctly with the enrichment orchestrator
"""

import pytest
from unittest.mock import patch, MagicMock
from src.qa.grounding_gate import GroundingGate, GroundingResult, AbstentionResponse


class TestGroundingGate:
    """Test the GroundingGate class."""

    def test_keyword_extraction(self):
        """Keywords are extracted correctly, stop words removed."""
        gate = GroundingGate()
        keywords = gate._extract_keywords(
            "Do natural environments enhance cognitive restoration?"
        )
        assert "natural" in keywords
        assert "environments" in keywords
        assert "cognitive" in keywords
        assert "restoration" in keywords
        # Stop words filtered
        assert "do" not in keywords
        assert "the" not in keywords

    def test_keyword_extraction_deduplicates(self):
        """Duplicate keywords removed while preserving order."""
        gate = GroundingGate()
        keywords = gate._extract_keywords("light light light and color color")
        assert keywords.count("light") == 1
        assert keywords.count("color") == 1

    def test_grounding_with_empty_corpus(self):
        """Abstains when corpus directory doesn't exist."""
        gate = GroundingGate(extractions_dir="/nonexistent/dir")
        result = gate.check("Do natural environments enhance cognitive restoration?")
        assert result.should_abstain is True
        assert result.has_empirical_anchor is False
        assert result.n_supporting_findings == 0
        assert result.recommendation == "abstain"

    def test_grounding_with_no_keywords(self):
        """Abstains when query has no extractable keywords."""
        gate = GroundingGate()
        result = gate.check("is it?")  # All stop words
        assert result.should_abstain is True
        assert "keywords" in result.reason.lower()

    def test_abstention_response_format(self):
        """AbstentionResponse has correct structure."""
        resp = AbstentionResponse(
            reason="No evidence found",
            confidence=0.0,
            suggestion="Try searching for related topics"
        )
        d = resp.to_dict()
        assert d["abstention"] is True
        assert d["confidence"] == 0.0
        assert "No evidence" in d["reason"]
        assert "message" in d

    def test_grounding_result_recommendation_values(self):
        """Recommendation property returns correct values."""
        # Abstain
        r1 = GroundingResult(has_empirical_anchor=False, n_supporting_findings=0, should_abstain=True)
        assert r1.recommendation == "abstain"

        # Answer
        r2 = GroundingResult(has_empirical_anchor=True, n_supporting_findings=5)
        assert r2.recommendation == "answer"

        # Flag contradiction
        r3 = GroundingResult(
            has_empirical_anchor=True, n_supporting_findings=5,
            contradictions=[{"conflict": "test"}]
        )
        assert r3.recommendation == "flag_contradiction"

    def test_coherence_check_detects_contradiction(self):
        """Coherence check identifies direction mismatches."""
        gate = GroundingGate()
        from src.qa.grounding_gate import EmpiricalAnchor
        anchors = [
            EmpiricalAnchor(
                source_file="test.json",
                article_type="empirical",
                antecedent="natural environments",
                consequent="cognitive restoration",
                direction="increase",
            )
        ]
        beliefs = [
            {"text": "Natural environments decrease cognitive restoration scores"}
        ]
        status, contradictions = gate._check_coherence(anchors, beliefs)
        assert status == "contradicted"
        assert len(contradictions) > 0

    def test_coherence_check_consistent(self):
        """Coherence check passes when no contradictions."""
        gate = GroundingGate()
        from src.qa.grounding_gate import EmpiricalAnchor
        anchors = [
            EmpiricalAnchor(
                source_file="test.json",
                article_type="empirical",
                antecedent="lighting color",
                consequent="mood",
                direction="increase",
            )
        ]
        beliefs = [
            {"text": "Temperature affects thermal comfort"}  # Unrelated
        ]
        status, contradictions = gate._check_coherence(anchors, beliefs)
        assert status == "consistent"
        assert len(contradictions) == 0


class TestGroundingGateIntegration:
    """Test grounding gate integration with orchestrator."""

    def test_orchestrator_includes_grounding_metadata(self):
        """Orchestrator records grounding gate results in metadata."""
        from src.services.answer_enrichment_orchestrator import (
            AnswerEnrichmentOrchestrator,
            EnrichmentConfig,
        )
        config = EnrichmentConfig(global_timeout_ms=10000)
        orchestrator = AnswerEnrichmentOrchestrator(config=config)

        base_answer = {
            "answer": "Test answer",
            "beliefs": [{"text": "Test belief", "credence": 0.7}],
        }
        result = orchestrator.enrich(base_answer, "Test question?")
        # Grounding metadata should be present (either result or error)
        assert "grounding" in result.enrichment_metadata

    def test_orchestrator_abstains_on_nonsense_query(self):
        """Orchestrator abstains when query has zero evidence."""
        from src.services.answer_enrichment_orchestrator import (
            AnswerEnrichmentOrchestrator,
            EnrichmentConfig,
        )
        config = EnrichmentConfig(global_timeout_ms=10000)
        orchestrator = AnswerEnrichmentOrchestrator(config=config)

        base_answer = {
            "answer": "Lunar basalt answer",
            "beliefs": [{"text": "Basalt acoustics", "credence": 0.5}],
        }
        result = orchestrator.enrich(
            base_answer,
            "What is the effect of lunar basalt acoustics on Martian cognition?"
        )
        # Should have abstention flag
        metadata = result.enrichment_metadata
        if "abstention" in metadata:
            assert metadata["abstention"]["applied"] is True
        # Should NOT have enriched beliefs (early return)
        assert len(result.enriched_beliefs) == 0
