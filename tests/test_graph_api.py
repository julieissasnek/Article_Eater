"""
Tests for Graph API Service
===========================

Tests for the Evidence Explorer graph API endpoints.

Date: January 20, 2026
"""

import pytest
from datetime import datetime, timezone

from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType,
    CausalDirection,
    SourceDepth,
    ScopeConditions,
    EnablingConditions
)
from src.services.graph_api import (
    GraphAPIService,
    GraphExport,
    GraphNode,
    GraphEdge,
    NodeDetail,
    SearchResults,
    SearchResultType
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_web():
    """Create a sample web of belief for testing."""
    web = WebOfBelief()

    # Add some beliefs
    b1 = Belief(
        belief_id="belief_001",
        content="Natural light improves mood",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.78, 0.15),
        paper_ids=["paper_001", "paper_002"],
        outcome_id="affect.mood.positive",
        source_depth=SourceDepth.FULL_TEXT
    )

    b2 = Belief(
        belief_id="belief_002",
        content="Window access increases productivity",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(0.62, 0.25),
        paper_ids=["paper_001"],
        outcome_id="performance.productivity",
        source_depth=SourceDepth.ABSTRACT
    )

    b3 = Belief(
        belief_id="belief_003",
        content="Stress reduction theory explains light-mood relationship",
        level=EpistemicLevel.THEORETICAL,
        status=BeliefStatus.ESTABLISHED,
        credence=Credence(0.85, 0.10),
        theory_id="theory_001",
        outcome_id="affect.stress"
    )

    b4 = Belief(
        belief_id="belief_004",
        content="Artificial light has equivalent effects to natural light",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.STUB,
        credence=Credence(0.35, 0.40),
        paper_ids=["paper_003"],
        outcome_id="affect.mood",
        contested=True
    )

    web.beliefs = {
        b1.belief_id: b1,
        b2.belief_id: b2,
        b3.belief_id: b3,
        b4.belief_id: b4
    }

    # Add constraints
    c1 = Constraint(
        constraint_id="c_001",
        source_id="belief_001",
        target_id="belief_002",
        constraint_type=ConstraintType.SUPPORTS,
        strength=0.6,
        causal_direction=CausalDirection.FORWARD
    )

    c2 = Constraint(
        constraint_id="c_002",
        source_id="belief_003",
        target_id="belief_001",
        constraint_type=ConstraintType.EXPLAINS,
        strength=0.75,
        causal_direction=CausalDirection.FORWARD
    )

    c3 = Constraint(
        constraint_id="c_003",
        source_id="belief_001",
        target_id="belief_004",
        constraint_type=ConstraintType.CONTRADICTS,
        strength=0.5,
        causal_direction=CausalDirection.CORRELATIONAL
    )

    web.constraints = {
        c1.constraint_id: c1,
        c2.constraint_id: c2,
        c3.constraint_id: c3
    }

    return web


@pytest.fixture
def paper_metadata():
    """Sample paper metadata."""
    return {
        "paper_001": {
            "title": "Effects of Natural Light on Mood and Productivity",
            "authors": ["Ulrich, R.", "Smith, J."],
            "year": 2020,
            "strength": 0.85
        },
        "paper_002": {
            "title": "Window Views and Psychological Wellbeing",
            "authors": ["Kaplan, R."],
            "year": 2018,
            "strength": 0.72
        },
        "paper_003": {
            "title": "Comparing Light Sources in Office Settings",
            "authors": ["Jones, M.", "Smith, J."],
            "year": 2022,
            "strength": 0.55
        }
    }


@pytest.fixture
def graph_service(sample_web, paper_metadata):
    """Create a graph API service instance."""
    return GraphAPIService(sample_web, paper_metadata)


# =============================================================================
# Graph Export Tests
# =============================================================================

class TestGraphExport:
    """Tests for graph export functionality."""

    def test_export_all_nodes(self, graph_service):
        """Test exporting all nodes."""
        export = graph_service.export_graph()

        assert len(export.nodes) == 4
        assert len(export.edges) == 3

    def test_export_metadata(self, graph_service):
        """Test that metadata is included."""
        export = graph_service.export_graph()

        assert export.metadata.total_beliefs == 4
        assert export.metadata.total_constraints == 3
        assert export.metadata.contested_count == 1
        assert export.metadata.stub_count == 1

    def test_export_excludes_stubs(self, graph_service):
        """Test filtering out stubs."""
        export = graph_service.export_graph(include_stubs=False)

        assert len(export.nodes) == 3
        # Stub belief should be excluded
        node_ids = [n.id for n in export.nodes]
        assert "belief_004" not in node_ids

    def test_export_min_credence_filter(self, graph_service):
        """Test filtering by minimum credence."""
        export = graph_service.export_graph(min_credence=0.7)

        assert len(export.nodes) == 2
        # Only high-credence beliefs
        for node in export.nodes:
            assert node.credence >= 0.7

    def test_export_max_nodes_limit(self, graph_service):
        """Test limiting number of nodes."""
        export = graph_service.export_graph(max_nodes=2)

        assert len(export.nodes) == 2
        # Should be highest credence nodes
        credences = [n.credence for n in export.nodes]
        assert credences[0] >= credences[1]

    def test_export_outcome_filter(self, graph_service):
        """Test filtering by outcome category."""
        export = graph_service.export_graph(outcome_filter="affect.")

        # Should only include affect.* outcomes
        for node in export.nodes:
            if node.outcome_category:
                assert node.outcome_category.startswith("affect.")

    def test_node_has_correct_fields(self, graph_service):
        """Test that nodes have all required fields."""
        export = graph_service.export_graph()

        for node in export.nodes:
            assert node.id is not None
            assert node.label is not None
            assert 0 <= node.credence <= 1
            assert node.status is not None
            assert isinstance(node.has_conflict, bool)
            assert isinstance(node.contested, bool)
            assert node.source_depth is not None
            assert 0.3 <= node.node_size <= 1.0

    def test_edge_correlational_flag(self, graph_service):
        """Test that correlational edges are flagged."""
        export = graph_service.export_graph()

        correlational_edges = [e for e in export.edges if e.is_correlational]
        causal_edges = [e for e in export.edges if not e.is_correlational]

        # We have one correlational edge (c_003)
        assert len(correlational_edges) >= 1

    def test_edge_conflict_detection(self, graph_service):
        """Test that nodes with conflicts are flagged."""
        export = graph_service.export_graph()

        # belief_001 and belief_004 have a CONTRADICTS constraint
        b1_node = next(n for n in export.nodes if n.id == "belief_001")
        b4_node = next(n for n in export.nodes if n.id == "belief_004")

        assert b1_node.has_conflict is True
        assert b4_node.has_conflict is True

    def test_export_to_dict(self, graph_service):
        """Test conversion to dictionary for JSON serialization."""
        export = graph_service.export_graph()
        d = export.to_dict()

        assert 'nodes' in d
        assert 'edges' in d
        assert 'metadata' in d
        assert isinstance(d['nodes'], list)
        assert isinstance(d['edges'], list)


# =============================================================================
# Node Detail Tests
# =============================================================================

class TestNodeDetail:
    """Tests for node detail functionality."""

    def test_get_node_detail(self, graph_service):
        """Test getting detail for a node."""
        detail = graph_service.get_node_detail("belief_001")

        assert detail is not None
        assert detail.belief_id == "belief_001"
        assert detail.content == "Natural light improves mood"
        assert detail.credence == 0.78

    def test_node_detail_sources(self, graph_service):
        """Test that sources are included."""
        detail = graph_service.get_node_detail("belief_001")

        assert len(detail.sources) == 2
        # Check source metadata is populated
        source = detail.sources[0]
        assert source.paper_id in ["paper_001", "paper_002"]

    def test_node_detail_constraints(self, graph_service):
        """Test that constraints are included."""
        detail = graph_service.get_node_detail("belief_001")

        # belief_001 has outgoing constraints to belief_002 and belief_004
        # and incoming from belief_003
        assert len(detail.outgoing_constraints) >= 1
        assert len(detail.incoming_constraints) >= 1

    def test_node_detail_not_found(self, graph_service):
        """Test handling of non-existent node."""
        detail = graph_service.get_node_detail("nonexistent")

        assert detail is None

    def test_node_detail_contested(self, graph_service):
        """Test detail for contested belief."""
        detail = graph_service.get_node_detail("belief_004")

        assert detail.contested is True
        # Should have credence range
        assert detail.credence_range is not None or detail.credence_range == (0.35, 0.35)

    def test_simplified_detail(self, graph_service):
        """Test simplified view for novice users."""
        detail = graph_service.get_node_detail("belief_001")
        simplified = detail.to_simplified_dict()

        assert 'belief_id' in simplified
        assert 'content' in simplified
        assert 'confidence_level' in simplified
        assert simplified['confidence_level'] == "HIGH"  # 0.78 > 0.7

    def test_node_detail_to_dict(self, graph_service):
        """Test conversion to dictionary."""
        detail = graph_service.get_node_detail("belief_001")
        d = detail.to_dict()

        assert 'belief_id' in d
        assert 'content' in d
        assert 'credence' in d
        assert 'sources' in d
        assert 'outgoing_constraints' in d
        assert 'incoming_constraints' in d


# =============================================================================
# Search Tests
# =============================================================================

class TestSearch:
    """Tests for search functionality."""

    def test_search_beliefs(self, graph_service):
        """Test searching beliefs by content."""
        results = graph_service.search("light")

        assert results.total_count > 0
        assert len(results.beliefs) > 0

        # Should find beliefs mentioning "light"
        for result in results.beliefs:
            assert "light" in result.title.lower() or "light" in result.snippet.lower()

    def test_search_papers(self, graph_service):
        """Test searching papers by title."""
        results = graph_service.search("Natural Light")

        assert len(results.papers) > 0
        # Should find the paper with "Natural Light" in title

    def test_search_authors(self, graph_service):
        """Test searching by author name."""
        results = graph_service.search("Ulrich")

        assert len(results.authors) > 0
        assert results.authors[0].title == "Ulrich, R."

    def test_search_case_insensitive(self, graph_service):
        """Test that search is case insensitive."""
        results1 = graph_service.search("LIGHT")
        results2 = graph_service.search("light")

        assert results1.total_count == results2.total_count

    def test_search_results_sorted_by_relevance(self, graph_service):
        """Test that results are sorted by relevance."""
        results = graph_service.search("mood")

        if len(results.beliefs) > 1:
            for i in range(len(results.beliefs) - 1):
                assert results.beliefs[i].relevance >= results.beliefs[i + 1].relevance

    def test_search_max_results(self, graph_service):
        """Test limiting search results."""
        results = graph_service.search("light", max_results=1)

        assert len(results.beliefs) <= 1
        assert len(results.papers) <= 1

    def test_search_filter_categories(self, graph_service):
        """Test filtering search categories."""
        results = graph_service.search(
            "light",
            include_beliefs=True,
            include_papers=False,
            include_authors=False
        )

        assert len(results.papers) == 0
        assert len(results.authors) == 0

    def test_search_results_to_dict(self, graph_service):
        """Test conversion to dictionary."""
        results = graph_service.search("light")
        d = results.to_dict()

        assert 'query' in d
        assert 'total_count' in d
        assert 'beliefs' in d
        assert 'papers' in d
        assert 'authors' in d


# =============================================================================
# Top Beliefs Tests
# =============================================================================

class TestTopBeliefs:
    """Tests for top beliefs functionality."""

    def test_get_top_beliefs(self, graph_service):
        """Test getting top beliefs by credence."""
        top = graph_service.get_top_beliefs(n=2)

        assert len(top) == 2
        # Should be sorted by credence
        assert top[0]['credence'] >= top[1]['credence']

    def test_top_beliefs_default(self, graph_service):
        """Test default limit of 30."""
        top = graph_service.get_top_beliefs()

        # We only have 4 beliefs, so should return all
        assert len(top) == 4

    def test_top_beliefs_fields(self, graph_service):
        """Test that returned beliefs have expected fields."""
        top = graph_service.get_top_beliefs(n=1)

        belief = top[0]
        assert 'belief_id' in belief
        assert 'content' in belief
        assert 'credence' in belief
        assert 'status' in belief
        assert 'contested' in belief


# =============================================================================
# Edge Cases and Integration Tests
# =============================================================================

class TestEdgeCases:
    """Edge case and integration tests."""

    def test_empty_web(self):
        """Test handling of empty web."""
        empty_web = WebOfBelief()
        service = GraphAPIService(empty_web)

        export = service.export_graph()
        assert len(export.nodes) == 0
        assert len(export.edges) == 0

    def test_no_constraints(self):
        """Test handling web with beliefs but no constraints."""
        web = WebOfBelief()
        web.beliefs["b1"] = Belief(
            belief_id="b1",
            content="Test belief",
            level=EpistemicLevel.EMPIRICAL
        )
        service = GraphAPIService(web)

        export = service.export_graph()
        assert len(export.nodes) == 1
        assert len(export.edges) == 0

    def test_missing_paper_metadata(self, sample_web):
        """Test handling missing paper metadata gracefully."""
        service = GraphAPIService(sample_web, paper_metadata={})

        detail = service.get_node_detail("belief_001")
        assert detail is not None
        assert len(detail.sources) == 2
        # Sources should still exist, just without metadata
        for source in detail.sources:
            assert source.paper_id is not None

    def test_belief_with_scope_and_enabling(self, sample_web, paper_metadata):
        """Test belief with scope and enabling conditions."""
        # Add scope and enabling conditions to a belief
        belief = sample_web.beliefs["belief_001"]
        belief.scope = ScopeConditions(
            setting="office",
            population="adults",
            scope_specified=True
        )
        belief.enabling_conditions = EnablingConditions(
            minimum_exposure=">30 minutes",
            threshold=">300 lux"
        )

        service = GraphAPIService(sample_web, paper_metadata)
        detail = service.get_node_detail("belief_001")

        assert detail.scope is not None
        assert "Setting: office" in detail.scope.applies
        assert detail.enabling_conditions is not None
        assert detail.enabling_conditions['minimum_exposure'] == ">30 minutes"

    def test_truncation(self, graph_service):
        """Test that long content is truncated."""
        # Add a belief with very long content
        long_content = "A" * 200
        graph_service.web.beliefs["long"] = Belief(
            belief_id="long",
            content=long_content,
            level=EpistemicLevel.EMPIRICAL
        )

        export = graph_service.export_graph()
        long_node = next(n for n in export.nodes if n.id == "long")

        assert len(long_node.label) <= 83  # 80 + "..."
