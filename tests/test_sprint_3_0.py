"""
Tests for Sprint 3.0 — Unified API, Query Engine, Export
2026-02-08

Tests cover:
- LLM Query Bridge (multi-AI orchestration)
- Export Engine (BibTeX, summaries, checklists)
- API models and validation
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.llm_query_bridge import (
    MultiAIOrchestrator,
    QueryType,
    CausalLevel,
    ModelTier,
    ParsedQuery,
    QueryResponse,
    MODEL_REGISTRY,
    get_orchestrator,
    process_query
)

from src.services.export_engine import (
    ExportEngine,
    BibTeXGenerator,
    EvidenceSummaryGenerator,
    VerificationChecklistGenerator,
    SourcePaper,
    ExportedBelief,
    ExportFormat,
    ExportPurpose,
    export_bibtex,
    export_summary
)


# =============================================================================
# LLM Query Bridge Tests
# =============================================================================

class TestQueryTypes:
    """Test query type classification."""

    def test_query_type_enum(self):
        """Test QueryType enum values."""
        assert QueryType.WHAT.value == "what"
        assert QueryType.WHY.value == "why"
        assert QueryType.COMPARE.value == "compare"
        assert QueryType.GAPS.value == "gaps"
        assert len(QueryType) == 10  # All 10 types

    def test_causal_level_enum(self):
        """Test CausalLevel enum values."""
        assert CausalLevel.ASSOCIATIONAL.value == "associational"
        assert CausalLevel.INTERVENTIONAL.value == "interventional"
        assert CausalLevel.COUNTERFACTUAL.value == "counterfactual"

    def test_model_tier_enum(self):
        """Test ModelTier enum values."""
        assert ModelTier.NONE.value == "none"
        assert ModelTier.FAST.value == "fast"
        assert ModelTier.CAPABLE.value == "capable"
        assert ModelTier.BEST.value == "best"


class TestModelRegistry:
    """Test model configuration registry."""

    def test_model_registry_has_anthropic_models(self):
        """Test that Anthropic models are registered."""
        assert "claude-haiku" in MODEL_REGISTRY
        assert "claude-sonnet" in MODEL_REGISTRY
        assert "claude-opus" in MODEL_REGISTRY

    def test_model_registry_has_openai_models(self):
        """Test that OpenAI models are registered."""
        assert "gpt-4o-mini" in MODEL_REGISTRY
        assert "gpt-4o" in MODEL_REGISTRY

    def test_model_tiers_correct(self):
        """Test that model tiers are correctly assigned."""
        assert MODEL_REGISTRY["claude-haiku"].tier == ModelTier.FAST
        assert MODEL_REGISTRY["claude-sonnet"].tier == ModelTier.CAPABLE
        assert MODEL_REGISTRY["claude-opus"].tier == ModelTier.BEST

    def test_model_costs_defined(self):
        """Test that all models have cost information."""
        for model_id, config in MODEL_REGISTRY.items():
            assert config.cost_per_1k_input >= 0
            assert config.cost_per_1k_output >= 0


class TestParsedQuery:
    """Test ParsedQuery dataclass."""

    def test_parsed_query_creation(self):
        """Test creating a ParsedQuery."""
        pq = ParsedQuery(
            original="What reduces stress in hospitals?",
            query_type=QueryType.WHAT,
            causal_level=CausalLevel.ASSOCIATIONAL,
            entities=["stress", "hospitals"],
            subject="stress",
            object="hospitals",
            confidence=0.85
        )
        assert pq.original == "What reduces stress in hospitals?"
        assert pq.query_type == QueryType.WHAT
        assert pq.causal_level == CausalLevel.ASSOCIATIONAL
        assert "stress" in pq.entities
        assert pq.confidence == 0.85

    def test_parsed_query_defaults(self):
        """Test ParsedQuery default values."""
        pq = ParsedQuery(
            original="test",
            query_type=QueryType.WHAT,
            causal_level=CausalLevel.ASSOCIATIONAL
        )
        assert pq.entities == []
        assert pq.subject is None
        assert pq.object is None
        assert pq.scope_hints == {}
        assert pq.confidence == 0.0


class TestMultiAIOrchestrator:
    """Test MultiAIOrchestrator functionality."""

    def test_orchestrator_creation(self):
        """Test creating an orchestrator with default models."""
        orch = MultiAIOrchestrator()
        assert orch.intent_model is not None
        assert orch.synthesis_model is not None
        assert orch.explanation_model is not None

    def test_orchestrator_custom_models(self):
        """Test creating orchestrator with custom models."""
        orch = MultiAIOrchestrator(
            intent_model="gpt-4o-mini",
            synthesis_model="gpt-4o"
        )
        assert orch.intent_model.model_id == "gpt-4o-mini"
        assert orch.synthesis_model.model_id == "gpt-4o"

    def test_detect_intent_returns_parsed_query(self):
        """Test that detect_intent returns a ParsedQuery."""
        orch = MultiAIOrchestrator()
        result = orch.detect_intent("What reduces stress in hospitals?")
        assert isinstance(result, ParsedQuery)
        assert result.original == "What reduces stress in hospitals?"

    def test_process_query_returns_response(self):
        """Test that process_query returns a QueryResponse."""
        orch = MultiAIOrchestrator()
        result = orch.process_query("What reduces stress?")
        assert isinstance(result, QueryResponse)
        assert result.query == "What reduces stress?"

    def test_usage_stats_tracking(self):
        """Test that usage statistics are tracked."""
        orch = MultiAIOrchestrator()
        orch.detect_intent("test query")
        stats = orch.get_usage_stats()
        assert "total_cost" in stats
        assert "call_count" in stats
        assert stats["call_count"] >= 1

    def test_get_orchestrator_singleton(self):
        """Test that get_orchestrator returns a singleton."""
        orch1 = get_orchestrator()
        orch2 = get_orchestrator()
        assert orch1 is orch2

    def test_process_query_convenience(self):
        """Test the process_query convenience function."""
        result = process_query("What is biophilia?")
        assert isinstance(result, QueryResponse)


# =============================================================================
# Export Engine Tests
# =============================================================================

class TestBibTeXGenerator:
    """Test BibTeX generation."""

    def test_generate_article(self):
        """Test generating BibTeX for an article."""
        gen = BibTeXGenerator()
        paper = SourcePaper(
            paper_id="P001",
            title="Test Article",
            authors=["Smith, John", "Doe, Jane"],
            year=2024,
            journal="Test Journal",
            volume="42",
            pages="1-10",
            doi="10.1234/test"
        )
        bibtex = gen.generate([paper])
        assert "@article{" in bibtex
        assert "2024," in bibtex
        assert "Smith, John and Doe, Jane" in bibtex
        assert "Test Article" in bibtex
        assert "Test Journal" in bibtex
        assert "2024" in bibtex

    def test_generate_book(self):
        """Test generating BibTeX for a book (no journal)."""
        gen = BibTeXGenerator()
        paper = SourcePaper(
            paper_id="P002",
            title="Test Book",
            authors=["Author, A."],
            year=2020
        )
        bibtex = gen.generate([paper])
        assert "@misc{" in bibtex
        assert "2020," in bibtex
        assert "Test Book" in bibtex

    def test_generate_multiple(self):
        """Test generating BibTeX for multiple papers."""
        gen = BibTeXGenerator()
        papers = [
            SourcePaper(paper_id="P1", title="Paper 1", authors=["A"], year=2020),
            SourcePaper(paper_id="P2", title="Paper 2", authors=["B"], year=2021),
        ]
        bibtex = gen.generate(papers)
        assert "Paper 1" in bibtex
        assert "Paper 2" in bibtex

    def test_format_authors(self):
        """Test author formatting."""
        gen = BibTeXGenerator()
        result = gen._format_authors(["Smith, J.", "Doe, J.", "Brown, A."])
        assert result == "Smith, J. and Doe, J. and Brown, A."


class TestEvidenceSummaryGenerator:
    """Test evidence summary generation."""

    def test_generate_markdown_summary(self):
        """Test generating a Markdown summary."""
        gen = EvidenceSummaryGenerator()
        beliefs = [
            ExportedBelief(
                id="B001",
                content="Plants reduce stress",
                credence=0.75,
                uncertainty=0.10,
                status="ACCEPTED",
                level="EMPIRICAL",
                theory="Biophilia",
                sources=["Source 1", "Source 2"]
            )
        ]
        summary = gen.generate("Stress reduction", beliefs, format="markdown")
        assert "# Evidence Summary: Stress reduction" in summary
        assert "Plants reduce stress" in summary
        assert "ACCEPTED" in summary

    def test_generate_json_summary(self):
        """Test generating a JSON summary."""
        gen = EvidenceSummaryGenerator()
        beliefs = [
            ExportedBelief(
                id="B001",
                content="Test belief",
                credence=0.70,
                uncertainty=0.15,
                status="ACCEPTED",
                level="EMPIRICAL"
            )
        ]
        summary = gen.generate("Test topic", beliefs, format="json")
        data = json.loads(summary)
        assert data["topic"] == "Test topic"
        assert "key_finding" in data
        assert "scope" in data

    def test_aggregate_scope(self):
        """Test scope aggregation from multiple beliefs."""
        gen = EvidenceSummaryGenerator()
        beliefs = [
            ExportedBelief(
                id="B001",
                content="Belief 1",
                credence=0.70,
                uncertainty=0.10,
                status="ACCEPTED",
                level="EMPIRICAL",
                scope_conditions={"population": "Adults"}
            ),
            ExportedBelief(
                id="B002",
                content="Belief 2",
                credence=0.65,
                uncertainty=0.15,
                status="ACCEPTED",
                level="EMPIRICAL",
                scope_conditions={"population": "Children", "setting": "Schools"}
            )
        ]
        scope = gen._aggregate_scope(beliefs)
        assert "Adults" in scope["population"]
        assert "Children" in scope["population"]
        assert "Schools" in scope["setting"]

    def test_confidence_label(self):
        """Test confidence label assignment."""
        gen = EvidenceSummaryGenerator()

        high_cred = [ExportedBelief(id="1", content="", credence=0.80, uncertainty=0.05, status="ACCEPTED", level="EMPIRICAL")]
        summary = gen._build_summary("test", high_cred, None)
        assert summary.confidence_label == "high"

        mod_cred = [ExportedBelief(id="1", content="", credence=0.55, uncertainty=0.10, status="ACCEPTED", level="EMPIRICAL")]
        summary = gen._build_summary("test", mod_cred, None)
        assert summary.confidence_label == "moderate"

        low_cred = [ExportedBelief(id="1", content="", credence=0.30, uncertainty=0.20, status="ACCEPTED", level="EMPIRICAL")]
        summary = gen._build_summary("test", low_cred, None)
        assert summary.confidence_label == "low"


class TestVerificationChecklistGenerator:
    """Test verification checklist generation."""

    def test_generate_checklist(self):
        """Test generating a verification checklist."""
        gen = VerificationChecklistGenerator()
        beliefs = [
            ExportedBelief(
                id="B001",
                content="Belief 1",
                credence=0.70,
                uncertainty=0.10,
                status="ACCEPTED",
                level="EMPIRICAL",
                scope_conditions={"population": "Adults"},
                sources=["Source 1"]
            )
        ]
        sources = [
            SourcePaper(paper_id="P1", title="Paper 1", authors=["A"], year=2020)
        ]
        checklist = gen.generate(beliefs, sources)
        assert checklist.total_items > 0
        assert checklist.completed_items >= 0
        assert isinstance(checklist.items, list)

    def test_checklist_to_markdown(self):
        """Test converting checklist to Markdown."""
        gen = VerificationChecklistGenerator()
        beliefs = [
            ExportedBelief(
                id="B001",
                content="Test",
                credence=0.70,
                uncertainty=0.10,
                status="ACCEPTED",
                level="EMPIRICAL",
                sources=["S1"]
            )
        ]
        checklist = gen.generate(beliefs, [])
        md = gen.to_markdown(checklist)
        assert "# " in md
        assert "[✓]" in md or "[☐]" in md


class TestExportEngine:
    """Test the main ExportEngine class."""

    def test_engine_creation(self):
        """Test creating an ExportEngine."""
        engine = ExportEngine()
        assert engine.bibtex_gen is not None
        assert engine.summary_gen is not None
        assert engine.checklist_gen is not None

    def test_export_bibtex(self):
        """Test BibTeX export through engine."""
        engine = ExportEngine()
        papers = [
            SourcePaper(paper_id="P1", title="Test", authors=["A"], year=2020)
        ]
        bibtex = engine.export_bibtex(papers)
        assert "@" in bibtex
        assert "2020" in bibtex

    def test_export_summary(self):
        """Test summary export through engine."""
        engine = ExportEngine()
        beliefs = [
            ExportedBelief(
                id="B001",
                content="Test belief",
                credence=0.70,
                uncertainty=0.10,
                status="ACCEPTED",
                level="EMPIRICAL"
            )
        ]
        summary = engine.export_summary("Test topic", beliefs)
        assert "Test topic" in summary

    def test_export_checklist(self):
        """Test checklist export through engine."""
        engine = ExportEngine()
        beliefs = [
            ExportedBelief(
                id="B001",
                content="Test",
                credence=0.70,
                uncertainty=0.10,
                status="ACCEPTED",
                level="EMPIRICAL"
            )
        ]
        sources = [
            SourcePaper(paper_id="P1", title="Paper", authors=["A"], year=2020)
        ]
        checklist = engine.export_checklist(beliefs, sources)
        assert "Verification" in checklist or "verified" in checklist.lower()


class TestExportEnums:
    """Test export-related enums."""

    def test_export_format_enum(self):
        """Test ExportFormat enum."""
        assert ExportFormat.MARKDOWN.value == "markdown"
        assert ExportFormat.JSON.value == "json"
        assert ExportFormat.BIBTEX.value == "bibtex"
        assert ExportFormat.JSONL.value == "jsonl"

    def test_export_purpose_enum(self):
        """Test ExportPurpose enum."""
        assert ExportPurpose.PRACTITIONER_BRIEFING.value == "practitioner_briefing"
        assert ExportPurpose.LITERATURE_REVIEW.value == "literature_review"
        assert ExportPurpose.SYSTEMATIC_REVIEW.value == "systematic_review"
        assert ExportPurpose.DATA_PIPELINE.value == "data_pipeline"


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_export_bibtex_function(self):
        """Test export_bibtex convenience function."""
        papers = [
            SourcePaper(paper_id="P1", title="Test", authors=["A"], year=2020)
        ]
        result = export_bibtex(papers)
        assert "@" in result

    def test_export_summary_function(self):
        """Test export_summary convenience function."""
        beliefs = [
            ExportedBelief(
                id="B001",
                content="Test",
                credence=0.70,
                uncertainty=0.10,
                status="ACCEPTED",
                level="EMPIRICAL"
            )
        ]
        result = export_summary("Topic", beliefs)
        assert "Topic" in result


# =============================================================================
# API Models Tests (would need FastAPI test client for full integration)
# =============================================================================

class TestAPIModels:
    """Test API Pydantic models."""

    def test_models_importable(self):
        """Test that API models can be imported."""
        from app.routes.api_unified import (
            BeliefSummary,
            BeliefDetail,
            QueryRequest,
            QueryResponse,
            ExportRequest,
            SystemStats
        )
        # Just verify imports work
        assert BeliefSummary is not None
        assert QueryRequest is not None


# =============================================================================
# Streamlit Config Tests
# =============================================================================

class TestStreamlitConfig:
    """Test Streamlit configuration."""

    def test_config_importable(self):
        """Test that Streamlit config can be imported."""
        sys.path.insert(0, str(Path(__file__).parent.parent / "streamlit_app"))
        from config import USER_TYPES, QUERY_TYPES, COLORS

        assert len(USER_TYPES) == 5
        assert "practitioner" in USER_TYPES
        assert "senior_researcher" in USER_TYPES
        assert "graduate_student" in USER_TYPES

    def test_user_types_have_questions(self):
        """Test that all user types have common questions."""
        sys.path.insert(0, str(Path(__file__).parent.parent / "streamlit_app"))
        from config import USER_TYPES

        for type_id, user_type in USER_TYPES.items():
            assert len(user_type.common_questions) >= 5, f"{type_id} should have at least 5 questions"

    def test_query_types_complete(self):
        """Test that all 10 query types are defined."""
        sys.path.insert(0, str(Path(__file__).parent.parent / "streamlit_app"))
        from config import QUERY_TYPES

        expected = ["WHAT", "WHY", "COMPARE", "GAPS", "CONTRADICT",
                   "CONTINGENT", "HOW_CONFIDENT", "RELATED", "TRENDING", "CANONICAL"]
        for qt in expected:
            assert qt in QUERY_TYPES, f"Missing query type: {qt}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
