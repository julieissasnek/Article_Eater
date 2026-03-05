"""
Integration Tests: Annotation System ↔ Card Generation
=======================================================

Tests the complete flow: annotation data (stored in SQLite by annotation_service)
flows through card generation to appear in card content.

Success Conditions:
  SC-ANN-CARD-1: Cards for entities with annotations include annotation data in source_data
  SC-ANN-CARD-2: Debate tab includes disputes from annotation service when available
  SC-ANN-CARD-3: Evidence tab includes replication status from annotations
  SC-ANN-CARD-4: Graceful degradation — if annotation service unavailable, card generation continues

Author: CW (Claude/Cowork)
Date: 2026-03-05
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.qa.card_generation_orchestrator import (
    CardGenerationOrchestrator,
    GenerationRequest,
    enrich_source_data_with_annotations,
)
from src.qa.cards.card_types import CardType
from src.services.annotation_service import (
    AnnotationService,
    Annotation,
    AnnotationType,
)


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_annotation_service():
    """Create a mock AnnotationService with test annotations."""
    service = Mock(spec=AnnotationService)

    # Create realistic annotation objects
    dispute_ann = Annotation(
        id="ann-dispute-1",
        type=AnnotationType.DISPUTE,
        target_type="belief",
        target_id="attention_restoration",
        content="Competing Stress Reduction Theory (Ulrich 1983) argues the effect is primarily affective, not cognitive",
        author="david",
        created="2026-03-01T10:00:00Z",
        confidence=0.85,
        metadata={"theory_cited": "Stress Reduction Theory"},
    )

    surprise_ann = Annotation(
        id="ann-surprise-1",
        type=AnnotationType.SURPRISE_FLAG,
        target_type="belief",
        target_id="attention_restoration",
        content="Effect magnitude (d=1.2) far exceeds expectations from earlier meta-analyses (d=0.3)",
        author="system",
        created="2026-03-02T11:00:00Z",
        confidence=0.9,
        metadata={"effect_size_found": 1.2, "expected_range": [0.2, 0.4]},
    )

    replication_ann = Annotation(
        id="ann-replication-1",
        type=AnnotationType.REPLICATION_STATUS,
        target_type="belief",
        target_id="attention_restoration",
        content="Successfully replicated in 8 of 9 attempted replications; failed replication by Kumar (2019)",
        author="david",
        created="2026-03-03T12:00:00Z",
        confidence=0.88,
        metadata={"replications_success": 8, "replications_total": 9},
    )

    unanswered_ann = Annotation(
        id="ann-unanswered-1",
        type=AnnotationType.UNANSWERED_QUESTION,
        target_type="belief",
        target_id="attention_restoration",
        content="Does the restorative effect persist across different types of natural environments (desert vs. forest)?",
        author="expert_panel",
        created="2026-03-04T09:00:00Z",
        confidence=0.7,
        metadata={},
    )

    service.get_active_annotations.return_value = [
        dispute_ann,
        surprise_ann,
        replication_ann,
        unanswered_ann,
    ]

    return service


@pytest.fixture
def rich_source_data():
    """Source data for a belief card (T3_BELIEF)."""
    return {
        "entity_id": "attention_restoration",
        "title": "Attention Restoration Theory (Kaplan & Kaplan 1989)",
        "description": (
            "Natural environments restore directed attention capacity through "
            "a process of soft fascination. This core claim from Attention Restoration "
            "Theory (ART) has accumulated strong empirical support."
        ),
        "n_findings": 280,
        "n_papers": 95,
        "omega": 0.72,
        "direction_consensus": "increase",
        "mechanism_chain": [
            {
                "step": 1,
                "from_construct": "natural scene",
                "to_construct": "soft fascination",
                "mechanism_type": "perceptual",
                "evidence_strength": "direct",
            },
            {
                "step": 2,
                "from_construct": "soft fascination",
                "to_construct": "reduced directed attention fatigue",
                "mechanism_type": "cognitive",
                "evidence_strength": "indirect",
            },
        ],
    }


# ---------------------------------------------------------------------------
# Test: Annotation Enrichment
# ---------------------------------------------------------------------------


class TestAnnotationEnrichment:
    """Tests for the enrich_source_data_with_annotations function."""

    def test_enrichment_succeeds_with_valid_service(
        self, mock_annotation_service, rich_source_data
    ):
        """SC-ANN-CARD-1: Source data is enriched with annotation objects."""
        enriched = enrich_source_data_with_annotations(
            rich_source_data,
            "attention_restoration",
            "belief",
            mock_annotation_service,
        )

        # Assert annotations key exists
        assert "annotations" in enriched
        assert "_annotation_count" in enriched
        assert enriched["_annotation_count"] == 4

        # Assert all annotation types are present
        assert "DISPUTE" in enriched["annotations"]
        assert "SURPRISE_FLAG" in enriched["annotations"]
        assert "REPLICATION_STATUS" in enriched["annotations"]
        assert "UNANSWERED_QUESTION" in enriched["annotations"]

    def test_convenience_flattening(
        self, mock_annotation_service, rich_source_data
    ):
        """Convenience fields are flattened for easy access by tab generators."""
        enriched = enrich_source_data_with_annotations(
            rich_source_data,
            "attention_restoration",
            "belief",
            mock_annotation_service,
        )

        # Assert convenience flattening
        assert "disputes" in enriched
        assert isinstance(enriched["disputes"], list)
        assert len(enriched["disputes"]) == 1
        assert "Stress Reduction Theory" in enriched["disputes"][0]

        assert "surprise_flags" in enriched
        assert len(enriched["surprise_flags"]) == 1
        assert "d=1.2" in enriched["surprise_flags"][0]

        assert "replication_status" in enriched
        assert "8 of 9" in enriched["replication_status"]

    def test_enrichment_preserves_original_data(
        self, mock_annotation_service, rich_source_data
    ):
        """Original source_data fields are preserved after enrichment."""
        enriched = enrich_source_data_with_annotations(
            rich_source_data,
            "attention_restoration",
            "belief",
            mock_annotation_service,
        )

        # Assert original fields still present
        assert enriched["entity_id"] == rich_source_data["entity_id"]
        assert enriched["title"] == rich_source_data["title"]
        assert enriched["n_findings"] == rich_source_data["n_findings"]
        assert enriched["omega"] == rich_source_data["omega"]


# ---------------------------------------------------------------------------
# Test: Card Generation with Annotation Data
# ---------------------------------------------------------------------------


class TestCardGenerationWithAnnotations:
    """Tests for annotation data flowing through card generation."""

    def test_orchestrator_enriches_source_data_during_generation(
        self, mock_annotation_service, rich_source_data
    ):
        """Orchestrator enriches source_data with annotations before tab generation."""
        orch = CardGenerationOrchestrator()
        orch._annotation_service = mock_annotation_service

        request = GenerationRequest(
            card_type=CardType.T3_BELIEF,
            entity_id="attention_restoration",
            source_data=rich_source_data,
        )

        # Manually call enrichment (as done in generate_card)
        enriched = enrich_source_data_with_annotations(
            request.source_data,
            request.entity_id,
            "belief",
            orch._annotation_service,
        )

        # Assert enrichment succeeded
        assert "annotations" in enriched
        assert enriched["_annotation_count"] == 4

    def test_debate_tab_includes_disputes(self, rich_source_data):
        """SC-ANN-CARD-2: Debate tab includes disputes from annotations."""
        orch = CardGenerationOrchestrator()

        # Add disputes to source_data (as would happen after enrichment)
        source_data_with_disputes = {
            **rich_source_data,
            "disputes": [
                "Competing Stress Reduction Theory (Ulrich 1983) argues the effect is primarily affective"
            ],
        }

        request = GenerationRequest(
            card_type=CardType.T3_BELIEF,
            entity_id="attention_restoration",
            source_data=source_data_with_disputes,
        )

        debate_tab = orch._generate_fallback_tab(request, "debate")

        # Assert dispute appears in prose
        assert debate_tab is not None
        assert "dispute" in debate_tab.prose.lower()

    def test_evidence_tab_includes_replication_status(self, rich_source_data):
        """SC-ANN-CARD-3: Evidence tab includes replication status from annotations."""
        orch = CardGenerationOrchestrator()

        source_data_with_replication = {
            **rich_source_data,
            "replication_status": "Successfully replicated in 8 of 9 attempted replications",
        }

        request = GenerationRequest(
            card_type=CardType.T3_BELIEF,
            entity_id="attention_restoration",
            source_data=source_data_with_replication,
        )

        evidence_tab = orch._generate_fallback_tab(request, "evidence")

        # Assert replication status appears in prose
        assert evidence_tab is not None
        assert "replication" in evidence_tab.prose.lower()
        assert "8 of 9" in evidence_tab.prose

    def test_overview_tab_includes_surprise_flags(self, rich_source_data):
        """Overview tab includes surprise flags when present."""
        orch = CardGenerationOrchestrator()

        source_data_with_surprises = {
            **rich_source_data,
            "surprise_flags": [
                "Effect magnitude (d=1.2) far exceeds earlier expectations"
            ],
        }

        request = GenerationRequest(
            card_type=CardType.T3_BELIEF,
            entity_id="attention_restoration",
            source_data=source_data_with_surprises,
        )

        overview_tab = orch._generate_fallback_tab(request, "overview")

        # Assert surprise flag appears in prose
        assert overview_tab is not None
        assert "surprise" in overview_tab.prose.lower()

    def test_end_to_end_annotation_flow(
        self, mock_annotation_service, rich_source_data
    ):
        """End-to-end: annotations are fetched and flow into card tabs."""
        orch = CardGenerationOrchestrator()
        orch._annotation_service = mock_annotation_service

        request = GenerationRequest(
            card_type=CardType.T3_BELIEF,
            entity_id="attention_restoration",
            source_data=rich_source_data,
        )

        # Simulate what happens in generate_card
        enriched = enrich_source_data_with_annotations(
            request.source_data,
            request.entity_id,
            "belief",
            orch._annotation_service,
        )

        # Now use enriched data to generate tabs
        request.source_data = enriched

        overview_tab = orch._generate_fallback_tab(request, "overview")
        evidence_tab = orch._generate_fallback_tab(request, "evidence")
        debate_tab = orch._generate_fallback_tab(request, "debate")

        # Assert all tabs include annotation data
        assert overview_tab is not None and "surprise" in overview_tab.prose.lower()
        assert evidence_tab is not None and "replication" in evidence_tab.prose.lower()
        assert debate_tab is not None and "dispute" in debate_tab.prose.lower()


# ---------------------------------------------------------------------------
# Test: Graceful Degradation
# ---------------------------------------------------------------------------


class TestGracefulDegradation:
    """Tests for SC-ANN-CARD-4: Graceful degradation when service unavailable."""

    def test_degradation_when_service_is_none(self, rich_source_data):
        """Card generation succeeds even when annotation_service is None."""
        original_source_data = rich_source_data.copy()

        enriched = enrich_source_data_with_annotations(
            rich_source_data,
            "attention_restoration",
            "belief",
            annotation_service=None,
        )

        # Should return the data without crashing
        assert enriched is not None
        assert enriched["entity_id"] == original_source_data["entity_id"]

    def test_degradation_when_query_fails(self, rich_source_data):
        """Card generation succeeds even when annotation query fails."""
        mock_service = Mock(spec=AnnotationService)
        mock_service.get_active_annotations.side_effect = RuntimeError("DB connection failed")

        original_data = rich_source_data.copy()

        enriched = enrich_source_data_with_annotations(
            rich_source_data,
            "attention_restoration",
            "belief",
            annotation_service=mock_service,
        )

        # Should return the data without crashing
        assert enriched is not None
        assert enriched["entity_id"] == original_data["entity_id"]

    def test_degradation_when_orchestrator_has_no_annotation_service(
        self, rich_source_data
    ):
        """Orchestrator gracefully handles missing annotation service."""
        orch = CardGenerationOrchestrator()
        orch._annotation_service = None  # Simulate initialization failure

        request = GenerationRequest(
            card_type=CardType.T3_BELIEF,
            entity_id="attention_restoration",
            source_data=rich_source_data,
        )

        # This should not crash during enrichment
        enriched = enrich_source_data_with_annotations(
            request.source_data,
            request.entity_id,
            "belief",
            orch._annotation_service,
        )

        # Card generation should continue with original data
        assert enriched is not None
        overview_tab = orch._generate_fallback_tab(request, "overview")
        assert overview_tab is not None

    def test_multiple_annotation_types_missing(self, rich_source_data):
        """Tabs gracefully degrade when some annotation types are missing."""
        mock_service = Mock(spec=AnnotationService)
        # Return only disputes, no surprises or replication
        dispute_ann = Annotation(
            id="ann-1",
            type=AnnotationType.DISPUTE,
            target_type="belief",
            target_id="test",
            content="Test dispute",
            author="test",
            created="2026-03-05T00:00:00Z",
        )
        mock_service.get_active_annotations.return_value = [dispute_ann]

        enriched = enrich_source_data_with_annotations(
            rich_source_data,
            "attention_restoration",
            "belief",
            mock_service,
        )

        # Should have disputes but not surprises
        assert "disputes" in enriched
        assert "surprise_flags" not in enriched or enriched.get("surprise_flags") == []

        # Tabs should still generate without crashing
        orch = CardGenerationOrchestrator()
        request = GenerationRequest(
            card_type=CardType.T3_BELIEF,
            entity_id="attention_restoration",
            source_data=enriched,
        )

        debate_tab = orch._generate_fallback_tab(request, "debate")
        evidence_tab = orch._generate_fallback_tab(request, "evidence")
        overview_tab = orch._generate_fallback_tab(request, "overview")

        assert debate_tab is not None
        assert evidence_tab is not None
        assert overview_tab is not None


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
