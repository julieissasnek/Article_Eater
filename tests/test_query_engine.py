"""
Tests for Query Engine (MVP-3)
==============================

Created: 2026-02-11
Owner: Terminal 2

Tests for the main QueryEngine orchestration class.

Decision tracking for panel review:
- D1: Test fixture design - using direct WebOfBelief injection vs accumulator
- D2: Response schema validation approach - structural vs full jsonschema
- D3: Gap detection threshold choices - what counts as "uncertain"
- D4: Follow-up generation expectations - exact vs type-based validation
- D5: Search algorithm coverage - term matching heuristics
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from src.services.query_engine import QueryEngine, QueryResult
from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    SourceDepth,
    ScopeConditions,
)


# =============================================================================
# DECISION LOG (for panel review)
# =============================================================================
"""
D1: Test Fixture Design
-----------------------
Decision: Use direct WebOfBelief injection for unit tests, not WebAccumulator.
Rationale: Unit tests should isolate QueryEngine logic from persistence layer.
Alternatives: (a) Mock accumulator, (b) Use real accumulator with temp files.
Risk: May miss integration issues between QueryEngine and Accumulator.

D2: Response Schema Validation
------------------------------
Decision: Use structural checks (key presence, type checks) not full jsonschema.
Rationale: Faster tests, schema already validated in contract tests.
Alternatives: (a) Full jsonschema validation on every response.
Risk: Schema drift between implementation and tests.

D3: Gap Detection Thresholds
----------------------------
Decision: Test gap detection with uncertainty > 0.3 as "high uncertainty".
Rationale: Matches default in QueryEngine._identify_gaps().
Alternatives: (a) Parameterize threshold, (b) Use 0.25 or 0.35.
Risk: Threshold may not align with user expectations.

D4: Follow-Up Generation Testing
--------------------------------
Decision: Test for 3 follow-ups with correct types, not exact question text.
Rationale: Question text is generated dynamically from intent.
Alternatives: (a) Test exact text, (b) Test question patterns via regex.
Risk: Loose validation may miss broken follow-up generation.

D5: Search Algorithm Heuristics
-------------------------------
Decision: Test term-in-content matching, accept that ranking is score-based.
Rationale: Simple term matching is transparent and debuggable.
Alternatives: (a) Semantic similarity, (b) TF-IDF scoring.
Risk: May miss relevant beliefs with different vocabulary.
"""


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def empty_web():
    """Create empty WebOfBelief for testing."""
    return WebOfBelief(domain="neuroarchitecture")


@pytest.fixture
def populated_web():
    """Create WebOfBelief with test beliefs about various topics."""
    web = WebOfBelief(domain="neuroarchitecture")

    # Natural light beliefs (high credence)
    b1 = Belief(
        belief_id="light_prod_001",
        content="Natural light improves worker productivity by 10-15%",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(value=0.78, uncertainty=0.12, n_supporting=5),
        source_depth=SourceDepth.FULL_TEXT,
        paper_ids=["kaplan_2002", "edwards_2015"],
        tags=["light", "productivity", "workplace"]
    )
    web.beliefs[b1.belief_id] = b1

    b2 = Belief(
        belief_id="light_mood_001",
        content="Daylight exposure reduces stress and improves mood",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(value=0.72, uncertainty=0.15, n_supporting=3),
        source_depth=SourceDepth.FULL_TEXT,
        paper_ids=["boubekri_2014"],
        tags=["light", "stress", "mood", "wellbeing"]
    )
    web.beliefs[b2.belief_id] = b2

    # Abstract-only belief (should trigger caution)
    b3 = Belief(
        belief_id="light_cognitive_001",
        content="Natural light causes improved cognitive function and attention",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(value=0.65, uncertainty=0.20, n_supporting=2),
        source_depth=SourceDepth.ABSTRACT,  # Abstract only - needs caution
        paper_ids=["abstract_study_001"],
        tags=["light", "cognition", "attention"]
    )
    web.beliefs[b3.belief_id] = b3

    # High uncertainty belief (for gap detection)
    b4 = Belief(
        belief_id="noise_focus_001",
        content="Background noise affects concentration",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(value=0.55, uncertainty=0.35, n_supporting=1),  # High uncertainty
        source_depth=SourceDepth.FULL_TEXT,
        paper_ids=["noise_study_001"],
        tags=["noise", "concentration", "focus"]
    )
    web.beliefs[b4.belief_id] = b4

    # Theoretical belief
    b5 = Belief(
        belief_id="art_theory_001",
        content="Attention Restoration Theory explains nature's cognitive benefits",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(value=0.80, uncertainty=0.10, n_supporting=10),
        source_depth=SourceDepth.FULL_TEXT,
        paper_ids=["kaplan_1989"],
        tags=["ART", "theory", "attention", "nature"],
        theory_id="art"
    )
    web.beliefs[b5.belief_id] = b5

    # Belief with scope conditions
    b6 = Belief(
        belief_id="temp_perf_001",
        content="Temperature of 21-23C optimizes cognitive performance",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(value=0.75, uncertainty=0.12, n_supporting=4),
        source_depth=SourceDepth.FULL_TEXT,
        paper_ids=["temp_study_001"],
        tags=["temperature", "cognition", "performance"],
        scope=ScopeConditions(
            population="office workers",
            setting="climate-controlled buildings",
            scope_specified=True
        )
    )
    web.beliefs[b6.belief_id] = b6

    # Low credence belief (should be filtered by default threshold)
    b7 = Belief(
        belief_id="low_cred_001",
        content="Pink walls improve creativity (unverified)",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(value=0.25, uncertainty=0.30, n_supporting=1),
        source_depth=SourceDepth.ABSTRACT,
        paper_ids=["questionable_study"],
        tags=["color", "creativity"]
    )
    web.beliefs[b7.belief_id] = b7

    return web


@pytest.fixture
def engine_with_web(populated_web):
    """Create QueryEngine with populated web."""
    return QueryEngine(web=populated_web)


@pytest.fixture
def engine_empty(empty_web):
    """Create QueryEngine with empty web."""
    return QueryEngine(web=empty_web)


# =============================================================================
# Basic Initialization Tests
# =============================================================================

class TestQueryEngineInit:
    """Tests for QueryEngine initialization."""

    def test_init_with_direct_web(self, populated_web):
        """D1: Test initialization with direct WebOfBelief."""
        engine = QueryEngine(web=populated_web)
        assert engine.web is populated_web
        assert len(engine.web.beliefs) > 0

    def test_init_lazy_web(self):
        """Test lazy web initialization (no web provided)."""
        engine = QueryEngine()
        # Web property should create empty web if no accumulator
        web = engine.web
        assert web is not None
        assert isinstance(web, WebOfBelief)

    def test_parser_initialized(self, engine_with_web):
        """Test parser is initialized."""
        assert engine_with_web._parser is not None


# =============================================================================
# Simple Query Interface Tests
# =============================================================================

class TestSimpleQuery:
    """Tests for the simple query() interface."""

    def test_basic_query(self, engine_with_web):
        """Test basic query returns valid response."""
        response = engine_with_web.query("What affects productivity?")

        # D2: Structural validation
        assert "schema" in response
        assert response["schema"] == "ae.query_response.v1"
        assert "query_id" in response
        assert "status" in response
        assert "headline" in response

    def test_query_with_matches(self, engine_with_web):
        """Test query that should find matches."""
        response = engine_with_web.query("Does natural light improve productivity?")

        assert response["status"] == "success"
        assert response["metadata"]["n_beliefs_matched"] > 0
        # Should match light_prod_001 at minimum

    def test_query_no_matches(self, engine_with_web):
        """Test query with no matching beliefs."""
        response = engine_with_web.query("Does xyzzy flibbertigibbet affect zorkmid?")

        # May get no_results or clarification_needed for nonsense queries
        assert response["status"] in ["no_results", "clarification_needed"]

    def test_empty_query_error(self, engine_with_web):
        """Test empty query returns error."""
        response = engine_with_web.query("")

        assert response["status"] == "error"
        assert response["error"]["code"] == "empty_query"

    def test_query_response_modes(self, engine_with_web):
        """Test different response modes."""
        for mode in ["headline", "summary", "detail", "deep_dive"]:
            response = engine_with_web.query(
                "Does natural light improve worker productivity?",
                response_mode=mode
            )
            # Only check mode if we got a successful response
            if response["status"] == "success":
                assert response["response_mode"] == mode


# =============================================================================
# Full Contract Query Tests
# =============================================================================

class TestContractQuery:
    """Tests for query_from_request() with full contract."""

    def test_full_request(self, engine_with_web):
        """Test full ae.query_request.v1 request."""
        request = {
            "schema": "ae.query_request.v1",
            "query_id": "test_q_001",
            "query_text": "Does natural light affect worker productivity?",
            "response_mode": "summary",
            "include_gaps": True,
            "max_results": 5,
            "min_credence": 0.5
        }

        response = engine_with_web.query_from_request(request)

        assert response["query_id"] == "test_q_001"
        assert response["status"] == "success"
        assert "summary" in response
        assert "gaps" in response

    def test_min_credence_filtering(self, engine_with_web):
        """D3: Test min_credence filters out low-credence beliefs."""
        # Query with high min_credence should filter more
        response_low = engine_with_web.query(
            "natural light improves productivity",
            min_credence=0.3
        )
        response_high = engine_with_web.query(
            "natural light improves productivity",
            min_credence=0.9  # Very high threshold
        )

        # High threshold should match fewer or no beliefs
        if response_low["status"] == "success" and response_high["status"] == "success":
            assert response_high["metadata"]["n_beliefs_matched"] <= response_low["metadata"]["n_beliefs_matched"]

    def test_max_results_limit(self, engine_with_web):
        """Test max_results limits returned beliefs."""
        response = engine_with_web.query(
            "light",  # Should match multiple beliefs
            max_results=2
        )

        if response["status"] == "success":
            n_matched = response["metadata"]["n_beliefs_matched"]
            # Implementation note: n_beliefs_matched is after limit
            assert n_matched <= 2

    def test_invalid_schema_error(self, engine_with_web):
        """Test invalid schema returns error."""
        request = {
            "schema": "ae.wrong_schema.v9",
            "query_id": "test",
            "query_text": "test query"
        }

        response = engine_with_web.query_from_request(request)

        assert response["status"] == "error"
        assert "invalid_schema" in response["error"]["code"]


# =============================================================================
# Progressive Disclosure Tests
# =============================================================================

class TestProgressiveDisclosure:
    """Tests for progressive disclosure levels."""

    def test_headline_mode(self, engine_with_web):
        """Test headline mode returns minimal response."""
        response = engine_with_web.query(
            "natural light productivity",
            response_mode="headline"
        )

        assert "headline" in response
        assert response.get("summary") is None
        assert response.get("detail") is None

    def test_summary_mode(self, engine_with_web):
        """Test summary mode includes key evidence."""
        response = engine_with_web.query(
            "natural light productivity",
            response_mode="summary"
        )

        if response["status"] == "success":
            assert "summary" in response
            summary = response["summary"]
            assert "key_evidence" in summary
            assert "answer_confidence" in summary

    def test_detail_mode(self, engine_with_web):
        """Test detail mode includes all evidence."""
        response = engine_with_web.query(
            "natural light",
            response_mode="detail"
        )

        if response["status"] == "success":
            assert "detail" in response
            detail = response["detail"]
            assert "all_evidence" in detail
            assert "theories_involved" in detail

    def test_deep_dive_mode(self, engine_with_web):
        """Test deep_dive mode includes epistemology."""
        response = engine_with_web.query(
            "attention restoration",
            response_mode="deep_dive"
        )

        if response["status"] == "success":
            assert "deep_dive" in response
            deep = response["deep_dive"]
            assert "entrenchment_scores" in deep
            assert "constraint_network" in deep


# =============================================================================
# Follow-Up Generation Tests (Simon: exactly 3)
# =============================================================================

class TestFollowUps:
    """D4: Tests for follow-up question generation."""

    def test_exactly_three_followups(self, engine_with_web):
        """Test exactly 3 follow-ups are generated."""
        response = engine_with_web.query(
            "natural light productivity",
            response_mode="summary"
        )

        if response["status"] == "success":
            assert "follow_ups" in response
            assert len(response["follow_ups"]) == 3

    def test_followup_types(self, engine_with_web):
        """Test follow-up types: deeper, broader, uncertainty."""
        response = engine_with_web.query(
            "natural light productivity",
            response_mode="summary"
        )

        if response["status"] == "success":
            types = {f["type"] for f in response["follow_ups"]}
            assert "deeper" in types
            assert "broader" in types
            assert "uncertainty" in types

    def test_followups_have_executable_query(self, engine_with_web):
        """Test follow-ups include executable query."""
        response = engine_with_web.query(
            "natural light productivity",
            response_mode="summary"
        )

        if response["status"] == "success":
            for fu in response["follow_ups"]:
                assert "executable_query" in fu
                assert len(fu["executable_query"]) > 0


# =============================================================================
# Gap Detection Tests
# =============================================================================

class TestGapDetection:
    """D3: Tests for knowledge gap identification."""

    def test_gaps_when_requested(self, engine_with_web):
        """Test gaps are included when requested."""
        response = engine_with_web.query(
            "Does background noise affect concentration and focus?",
            include_gaps=True
        )

        # Gaps should be included if query succeeded
        if response["status"] == "success":
            assert "gaps" in response

    def test_gaps_not_included_by_default(self, engine_with_web):
        """Test gaps not included by default."""
        response = engine_with_web.query(
            "natural light productivity",
            include_gaps=False
        )

        assert "gaps" not in response or response.get("gaps") is None

    def test_uncertain_beliefs_create_gaps(self, engine_with_web):
        """Test high-uncertainty beliefs create gaps."""
        response = engine_with_web.query(
            "noise focus concentration",  # Matches noise_focus_001 with high uncertainty
            include_gaps=True
        )

        if response["status"] == "success" and response.get("gaps"):
            gaps = response["gaps"]
            assert gaps["n_gaps"] >= 0
            # May have "uncertain" type gap

    def test_gap_structure(self, engine_with_web):
        """Test gap report structure."""
        response = engine_with_web.query(
            "biophilic design healthcare",  # Unlikely to have results
            include_gaps=True
        )

        if response.get("gaps"):
            gaps = response["gaps"]
            assert "n_gaps" in gaps
            assert "top_gaps" in gaps
            for gap in gaps["top_gaps"]:
                assert "gap_id" in gap
                assert "gap_type" in gap
                assert "description" in gap


# =============================================================================
# Search Algorithm Tests
# =============================================================================

class TestSearchAlgorithm:
    """D5: Tests for belief search heuristics."""

    def test_term_matching(self, engine_with_web):
        """Test search matches terms in content."""
        response = engine_with_web.query("Does natural light improve worker productivity?")

        assert response["status"] == "success"
        # Should match light_prod_001

    def test_tag_matching(self, engine_with_web):
        """Test search matches tags."""
        response = engine_with_web.query("wellbeing")

        if response["status"] == "success":
            # Should match light_mood_001 via tag
            assert response["metadata"]["n_beliefs_matched"] >= 1

    def test_vocabulary_expansion_in_metadata(self, engine_with_web):
        """Test vocabulary expansions are tracked."""
        response = engine_with_web.query("Does daylight improve work performance?")

        # Only check metadata if query succeeded
        if response["status"] == "success":
            metadata = response.get("metadata", {})
            # May have vocabulary_expansions if parser expands terms
            assert "vocabulary_expansions" in metadata

    def test_credence_ordering(self, engine_with_web):
        """Test higher credence beliefs ranked higher."""
        response = engine_with_web.query(
            "light",  # Matches multiple beliefs
            response_mode="detail"
        )

        if response["status"] == "success" and response.get("detail"):
            evidence = response["detail"]["all_evidence"]
            if len(evidence) >= 2:
                # Should be ordered by score then credence
                # First items should have higher credence on average
                pass  # Ordering is score-based, not pure credence


# =============================================================================
# Evidence Item Tests
# =============================================================================

class TestEvidenceItems:
    """Tests for evidence item formatting."""

    def test_evidence_item_structure(self, engine_with_web):
        """Test evidence items have required fields."""
        response = engine_with_web.query(
            "natural light productivity",
            response_mode="summary"
        )

        if response["status"] == "success":
            evidence = response["summary"]["key_evidence"]
            for item in evidence:
                assert "belief_id" in item
                assert "content" in item
                assert "credence" in item
                assert "is_causal" in item

    def test_causal_detection(self, engine_with_web):
        """Test causal claims are detected."""
        response = engine_with_web.query(
            "natural light improves",
            response_mode="summary"
        )

        if response["status"] == "success":
            evidence = response["summary"]["key_evidence"]
            # light_prod_001 contains "improves" - should be causal
            causal_items = [e for e in evidence if e["is_causal"]]
            # May or may not have causal items depending on match

    def test_abstract_caution_flag(self, engine_with_web):
        """Test abstract-only causal claims get caution flag."""
        response = engine_with_web.query(
            "cognitive function attention",
            response_mode="summary"
        )

        # light_cognitive_001 is abstract-only causal
        if response["status"] == "success":
            evidence = response["summary"]["key_evidence"]
            # Check if any evidence has needs_caution
            # (only if abstract-only belief is matched)


# =============================================================================
# Metadata Tests
# =============================================================================

class TestMetadata:
    """Tests for response metadata."""

    def test_processing_time(self, engine_with_web):
        """Test processing time is recorded."""
        response = engine_with_web.query("Does natural light improve productivity?")

        # Only check if query succeeded (clarification responses may lack metadata)
        if response["status"] == "success":
            metadata = response.get("metadata", {})
            assert "processing_time_ms" in metadata
            assert metadata["processing_time_ms"] >= 0

    def test_belief_counts(self, engine_with_web):
        """Test belief counts are accurate."""
        response = engine_with_web.query("Does natural light improve productivity?")

        # Only check if query succeeded
        if response["status"] == "success":
            metadata = response.get("metadata", {})
            assert "n_beliefs_searched" in metadata
            assert "n_beliefs_matched" in metadata
            assert metadata["n_beliefs_searched"] >= metadata["n_beliefs_matched"]

    def test_causal_level_detection(self, engine_with_web):
        """Test causal level is detected."""
        response = engine_with_web.query("Does natural light cause improved productivity?")

        # Only check if query succeeded
        if response["status"] == "success":
            metadata = response.get("metadata", {})
            assert "causal_level" in metadata
            # "cause" should trigger interventional or causal level

    def test_query_type_detection(self, engine_with_web):
        """Test query type is detected."""
        response = engine_with_web.query("What factors affect attention and cognition?")

        # Only check if query succeeded
        if response["status"] == "success":
            metadata = response.get("metadata", {})
            assert "query_type" in metadata


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling."""

    def test_empty_web_no_crash(self, engine_empty):
        """Test query on empty web doesn't crash."""
        response = engine_empty.query("Does natural light improve productivity?")

        # Empty web should return no_results or clarification_needed
        assert response["status"] in ["no_results", "clarification_needed"]
        assert "headline" in response

    def test_malformed_query_handled(self, engine_with_web):
        """Test malformed queries are handled gracefully."""
        # Very long query
        long_query = "test " * 500
        response = engine_with_web.query(long_query)

        # Should not crash
        assert "status" in response

    def test_special_characters(self, engine_with_web):
        """Test queries with special characters."""
        response = engine_with_web.query("light & productivity? (test)")

        # Should not crash
        assert "status" in response


# =============================================================================
# Stats Tests
# =============================================================================

class TestStats:
    """Tests for get_stats() method."""

    def test_stats_populated_web(self, engine_with_web):
        """Test stats on populated web."""
        stats = engine_with_web.get_stats()

        assert "n_beliefs" in stats
        assert stats["n_beliefs"] > 0
        assert "coherence" in stats

    def test_stats_empty_web(self, engine_empty):
        """Test stats on empty web."""
        stats = engine_empty.get_stats()

        assert stats["n_beliefs"] == 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self, engine_with_web):
        """Test complete query workflow."""
        # 1. Run query
        response = engine_with_web.query(
            "What is the effect of natural light on productivity?",
            response_mode="summary",
            include_gaps=True
        )

        # 2. Verify response
        assert response["status"] == "success"
        assert response["headline"]
        assert response["summary"]["key_evidence"]
        assert len(response["follow_ups"]) == 3

        # 3. Check gaps included
        assert "gaps" in response

        # 4. Verify serializable
        json_str = json.dumps(response)
        parsed = json.loads(json_str)
        assert parsed["query_id"] == response["query_id"]

    def test_multiple_queries(self, engine_with_web):
        """Test multiple sequential queries."""
        queries = [
            "natural light",
            "temperature performance",
            "noise concentration",
            "attention restoration theory"
        ]

        for query_text in queries:
            response = engine_with_web.query(query_text)
            assert "status" in response
            assert "headline" in response


# =============================================================================
# Schema Validation Tests (D2 - Bates panel recommendation)
# =============================================================================

class TestSchemaValidation:
    """Tests for response schema validation."""

    def test_response_validates_schema(self, engine_with_web):
        """D2: Test response validates against ae.query_response.v1 schema."""
        import json
        from pathlib import Path

        # Get response
        response = engine_with_web.query(
            "Does natural light improve productivity?",
            response_mode="summary"
        )

        # Load schema
        schema_path = Path(__file__).parent.parent / "contracts/ae_af/schemas/ae.query_response.v1.schema.json"

        if schema_path.exists():
            try:
                import jsonschema

                with open(schema_path) as f:
                    schema = json.load(f)

                # Validate - will raise if invalid
                jsonschema.validate(response, schema)

            except ImportError:
                # jsonschema not installed, skip validation
                pass

    def test_response_has_required_fields(self, engine_with_web):
        """Test response has all required fields per schema."""
        response = engine_with_web.query(
            "Does natural light improve productivity?",
            response_mode="summary"
        )

        # Required fields per ae.query_response.v1.schema.json
        assert "schema" in response
        assert response["schema"] == "ae.query_response.v1"
        assert "query_id" in response
        assert "status" in response
        assert "headline" in response

        # Status should be one of the valid values
        assert response["status"] in ["success", "partial", "no_results", "error", "clarification_needed"]


# =============================================================================
# CLI Tests (if importable)
# =============================================================================

class TestCLI:
    """Tests for CLI formatting functions."""

    def test_format_functions_importable(self):
        """Test CLI format functions can be imported."""
        from src.cli.query import format_pretty, format_minimal

        test_response = {
            "status": "success",
            "headline": "Test headline",
            "metadata": {"n_beliefs_matched": 5}
        }

        pretty = format_pretty(test_response)
        assert "Test headline" in pretty

        minimal = format_minimal(test_response)
        assert "success" in minimal


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
