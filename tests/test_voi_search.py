"""
Tests for VOI-Driven Search (TODO 3).

Sprint H: Core structures, VOI scoring, source selection.

Date: January 20, 2026
"""

import pytest
from pathlib import Path

from src.services.voi_search import (
    GapType,
    EpistemicGap,
    SearchRecommendation,
    SearchResult,
    SearchSession,
    VOICalculator,
    SourceSelector,
    SOURCE_BY_DOMAIN,
    QueryGenerator,
    GapDetector,
    VOISearchCoordinator,
    create_voi_coordinator,
    detect_gaps,
    calculate_voi,
)

from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    ConstraintType,
    ScopeConditions,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_belief():
    """Create a sample belief for testing."""
    return Belief(
        belief_id="b_nature_stress",
        content="Natural views reduce stress levels in office workers",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(value=0.70, uncertainty=0.25),
        scope=ScopeConditions(population="office workers", setting="workplace"),
        paper_ids={"paper_1", "paper_2"}
    )


@pytest.fixture
def uncertain_belief():
    """Create a belief with high uncertainty."""
    return Belief(
        belief_id="b_uncertain",
        content="Water sounds affect cognitive performance",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(value=0.50, uncertainty=0.40),
        paper_ids={"paper_1"}
    )


@pytest.fixture
def unexplored_belief():
    """Create a belief with few supporting studies."""
    return Belief(
        belief_id="b_unexplored",
        content="Ceiling height influences creative thinking",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(value=0.60, uncertainty=0.20),
        paper_ids=set()  # No papers
    )


@pytest.fixture
def web_with_gaps():
    """Create a web with beliefs that have gaps."""
    web = WebOfBelief()

    # Add beliefs with varying levels of uncertainty and evidence
    web.add_belief(Belief(
        belief_id="b_central",
        content="Biophilic design improves wellbeing",
        level=EpistemicLevel.THEORETICAL,
        credence=Credence(value=0.75, uncertainty=0.15),
        paper_ids={"p1", "p2", "p3", "p4", "p5"}
    ))

    web.add_belief(Belief(
        belief_id="b_uncertain",
        content="Natural sounds reduce cortisol levels",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(value=0.55, uncertainty=0.35),
        paper_ids={"p1", "p2"}
    ))

    web.add_belief(Belief(
        belief_id="b_unexplored",
        content="Plant density affects air quality perception",
        level=EpistemicLevel.EMPIRICAL,
        credence=Credence(value=0.60, uncertainty=0.20),
        paper_ids={"p1"}
    ))

    # Add some constraints
    web.add_constraint(Constraint(
        constraint_id="c1",
        source_id="b_uncertain",
        target_id="b_central",
        constraint_type=ConstraintType.SUPPORTS,
        strength=0.6
    ))

    web.add_constraint(Constraint(
        constraint_id="c2",
        source_id="b_unexplored",
        target_id="b_central",
        constraint_type=ConstraintType.SUPPORTS,
        strength=0.5
    ))

    return web


# =============================================================================
# GAP TYPE TESTS
# =============================================================================

class TestGapType:
    """Tests for GapType enum."""

    def test_gap_types_exist(self):
        """Test that both gap types are defined."""
        assert GapType.UNCERTAIN.value == "uncertain"
        assert GapType.UNEXPLORED.value == "unexplored"

    def test_gap_type_values(self):
        """Test gap type string values."""
        assert len(GapType) == 2


# =============================================================================
# EPISTEMIC GAP TESTS
# =============================================================================

class TestEpistemicGap:
    """Tests for EpistemicGap dataclass."""

    def test_gap_creation(self):
        """Test creating an epistemic gap."""
        gap = EpistemicGap(
            gap_type=GapType.UNCERTAIN,
            description="High uncertainty on stress findings",
            primary_belief_id="b_test",
            voi_score=0.75
        )
        assert gap.gap_type == GapType.UNCERTAIN
        assert gap.voi_score == 0.75

    def test_to_search_context(self):
        """Test conversion to search context."""
        gap = EpistemicGap(
            gap_type=GapType.UNEXPLORED,
            description="Limited evidence",
            primary_belief_id="b_test",
            voi_score=0.6
        )
        context = gap.to_search_context()

        assert context['gap_type'] == "unexplored"
        assert context['belief_id'] == "b_test"
        assert context['voi_score'] == 0.6


# =============================================================================
# SEARCH RECOMMENDATION TESTS
# =============================================================================

class TestSearchRecommendation:
    """Tests for SearchRecommendation dataclass."""

    def test_recommendation_creation(self):
        """Test creating a search recommendation."""
        rec = SearchRecommendation(
            paper_id="doi:10.1234/test",
            title="Effects of nature on stress",
            relevance_score=0.85,
            ranking_explanation="High keyword match"
        )
        assert rec.paper_id == "doi:10.1234/test"
        assert rec.relevance_score == 0.85

    def test_to_dict(self):
        """Test conversion to dict."""
        rec = SearchRecommendation(
            paper_id="test_id",
            title="Test Paper",
            relevance_score=0.7,
            ranking_explanation="Test"
        )
        d = rec.to_dict()

        assert d['paper_id'] == "test_id"
        assert d['relevance_score'] == 0.7
        assert 'expected_credibility_profile' in d


# =============================================================================
# SEARCH SESSION TESTS
# =============================================================================

class TestSearchSession:
    """Tests for SearchSession dataclass."""

    def test_session_creation(self):
        """Test creating a search session."""
        gap = EpistemicGap(
            gap_type=GapType.UNCERTAIN,
            description="Test",
            primary_belief_id="b_test",
            voi_score=0.5
        )
        session = SearchSession(gap=gap)

        assert session.gap == gap
        assert session.total_queries == 0
        assert len(session.results) == 0

    def test_all_recommendations(self):
        """Test getting all recommendations."""
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", "b_test", 0.5)
        session = SearchSession(gap=gap)

        # Add some results
        result1 = SearchResult(
            query="test query 1",
            source="semantic_scholar",
            recommendations=[
                SearchRecommendation("p1", "Paper 1", 0.8, "Match"),
                SearchRecommendation("p2", "Paper 2", 0.6, "Match"),
            ],
            raw_count=10
        )
        result2 = SearchResult(
            query="test query 2",
            source="pubmed",
            recommendations=[
                SearchRecommendation("p3", "Paper 3", 0.7, "Match"),
            ],
            raw_count=5
        )
        session.results = [result1, result2]

        all_recs = session.all_recommendations
        assert len(all_recs) == 3

    def test_unique_papers(self):
        """Test counting unique papers."""
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", "b_test", 0.5)
        session = SearchSession(gap=gap)

        # Add results with duplicate papers
        result = SearchResult(
            query="test",
            source="test",
            recommendations=[
                SearchRecommendation("p1", "Paper 1", 0.8, "Match"),
                SearchRecommendation("p1", "Paper 1 duplicate", 0.7, "Match"),
                SearchRecommendation("p2", "Paper 2", 0.6, "Match"),
            ],
            raw_count=10
        )
        session.results = [result]

        assert session.unique_papers == 2


# =============================================================================
# VOI CALCULATOR TESTS
# =============================================================================

class TestVOICalculator:
    """Tests for VOICalculator class."""

    def test_calculate_voi_uncertain(self, uncertain_belief):
        """Test VOI calculation for uncertain gap."""
        calc = VOICalculator()
        voi = calc.calculate_voi(GapType.UNCERTAIN, uncertain_belief)

        assert 0 <= voi <= 1
        # High uncertainty should give higher VOI
        assert voi > 0.3

    def test_calculate_voi_unexplored(self, unexplored_belief):
        """Test VOI calculation for unexplored gap."""
        calc = VOICalculator()
        voi = calc.calculate_voi(GapType.UNEXPLORED, unexplored_belief)

        assert 0 <= voi <= 1
        # Unexplored should have high sparsity component
        assert voi > 0.3

    def test_voi_with_web_centrality(self, web_with_gaps):
        """Test VOI calculation with web for centrality."""
        calc = VOICalculator()
        belief = web_with_gaps.beliefs["b_uncertain"]

        voi = calc.calculate_voi(GapType.UNCERTAIN, belief, web_with_gaps)

        assert 0 <= voi <= 1

    def test_higher_uncertainty_higher_voi(self):
        """Test that higher uncertainty gives higher VOI."""
        calc = VOICalculator()

        low_uncertainty = Belief(
            belief_id="b1",
            content="Test",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.7, uncertainty=0.1)
        )
        high_uncertainty = Belief(
            belief_id="b2",
            content="Test",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.7, uncertainty=0.4)
        )

        voi_low = calc.calculate_voi(GapType.UNCERTAIN, low_uncertainty)
        voi_high = calc.calculate_voi(GapType.UNCERTAIN, high_uncertainty)

        assert voi_high > voi_low


# =============================================================================
# SOURCE SELECTOR TESTS
# =============================================================================

class TestSourceSelector:
    """Tests for SourceSelector class."""

    def test_default_sources(self):
        """Test getting default sources."""
        selector = SourceSelector()
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", "b_test", 0.5)

        sources = selector.select_sources(gap)
        assert "semantic_scholar" in sources

    def test_domain_specific_sources(self):
        """Test domain-specific source selection."""
        selector = SourceSelector()

        neuro_belief = Belief(
            belief_id="b_neuro",
            content="Amygdala activation correlates with stress response",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.7, uncertainty=0.2)
        )
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", "b_neuro", 0.5)

        sources = selector.select_sources(gap, neuro_belief)
        assert "pubmed" in sources

    def test_environmental_psychology_sources(self, sample_belief):
        """Test sources for environmental psychology domain."""
        selector = SourceSelector()
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", sample_belief.belief_id, 0.5)

        sources = selector.select_sources(gap, sample_belief)
        # CNfA domain should get psychology/environmental psychology sources
        assert len(sources) > 0

    def test_infer_domain_neuroscience(self):
        """Test domain inference for neuroscience."""
        selector = SourceSelector()
        belief = Belief(
            belief_id="b_test",
            content="The amygdala and cortisol response in the brain",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.7, uncertainty=0.2)
        )

        domain = selector._infer_domain(belief)
        assert domain == "neuroscience"

    def test_infer_domain_healthcare(self):
        """Test domain inference for healthcare."""
        selector = SourceSelector()
        belief = Belief(
            belief_id="b_test",
            content="Patient outcomes in hospital settings with treatment",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.7, uncertainty=0.2)
        )

        domain = selector._infer_domain(belief)
        assert domain == "healthcare"


# =============================================================================
# QUERY GENERATOR TESTS
# =============================================================================

class TestQueryGenerator:
    """Tests for QueryGenerator class."""

    def test_generate_basic_queries(self, sample_belief):
        """Test generating queries from gap."""
        generator = QueryGenerator()
        gap = EpistemicGap(
            gap_type=GapType.UNCERTAIN,
            description="High uncertainty on stress reduction",
            primary_belief_id=sample_belief.belief_id,
            voi_score=0.6
        )

        queries = generator.generate_queries(gap, sample_belief)

        assert len(queries) > 0
        assert len(queries) <= 5

    def test_queries_include_belief_content(self, sample_belief):
        """Test that queries include belief content terms."""
        generator = QueryGenerator()
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", sample_belief.belief_id, 0.5)

        queries = generator.generate_queries(gap, sample_belief)

        # At least one query should contain key terms
        all_queries = " ".join(queries).lower()
        assert "natural" in all_queries or "stress" in all_queries

    def test_uncertain_gap_includes_meta_analysis(self, sample_belief):
        """Test that uncertain gaps generate meta-analysis queries."""
        generator = QueryGenerator()
        gap = EpistemicGap(GapType.UNCERTAIN, "High uncertainty", sample_belief.belief_id, 0.5)

        queries = generator.generate_queries(gap, sample_belief)

        all_queries = " ".join(queries).lower()
        assert "meta-analysis" in all_queries or "replication" in all_queries

    def test_unexplored_gap_includes_systematic_review(self, unexplored_belief):
        """Test that unexplored gaps generate systematic review queries."""
        generator = QueryGenerator()
        gap = EpistemicGap(GapType.UNEXPLORED, "Limited evidence", unexplored_belief.belief_id, 0.5)

        queries = generator.generate_queries(gap, unexplored_belief)

        all_queries = " ".join(queries).lower()
        assert "systematic review" in all_queries

    def test_queries_are_unique(self, sample_belief):
        """Test that generated queries are unique."""
        generator = QueryGenerator()
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", sample_belief.belief_id, 0.5)

        queries = generator.generate_queries(gap, sample_belief)

        # All queries should be unique (case-insensitive)
        lower_queries = [q.lower() for q in queries]
        assert len(lower_queries) == len(set(lower_queries))


# =============================================================================
# GAP DETECTOR TESTS
# =============================================================================

class TestGapDetector:
    """Tests for GapDetector class."""

    def test_detect_uncertain_gap(self, web_with_gaps):
        """Test detecting uncertain gaps."""
        detector = GapDetector()
        gaps = detector.detect_gaps(web_with_gaps)

        uncertain_gaps = [g for g in gaps if g.gap_type == GapType.UNCERTAIN]
        assert len(uncertain_gaps) >= 1

    def test_detect_unexplored_gap(self, web_with_gaps):
        """Test detecting unexplored gaps."""
        detector = GapDetector()
        gaps = detector.detect_gaps(web_with_gaps)

        unexplored_gaps = [g for g in gaps if g.gap_type == GapType.UNEXPLORED]
        assert len(unexplored_gaps) >= 1

    def test_gaps_sorted_by_voi(self, web_with_gaps):
        """Test that gaps are sorted by VOI score."""
        detector = GapDetector()
        gaps = detector.detect_gaps(web_with_gaps)

        # Check descending order
        for i in range(len(gaps) - 1):
            assert gaps[i].voi_score >= gaps[i+1].voi_score

    def test_max_gaps_limit(self, web_with_gaps):
        """Test that max_gaps limit is respected."""
        detector = GapDetector()
        gaps = detector.detect_gaps(web_with_gaps, max_gaps=2)

        assert len(gaps) <= 2


# =============================================================================
# VOI SEARCH COORDINATOR TESTS
# =============================================================================

class TestVOISearchCoordinator:
    """Tests for VOISearchCoordinator class."""

    def test_coordinator_creation(self, web_with_gaps):
        """Test creating a coordinator."""
        coordinator = VOISearchCoordinator(web_with_gaps)

        assert coordinator.web == web_with_gaps
        assert coordinator.gap_detector is not None
        assert coordinator.source_selector is not None

    def test_identify_search_priorities(self, web_with_gaps):
        """Test identifying search priorities."""
        coordinator = VOISearchCoordinator(web_with_gaps)
        priorities = coordinator.identify_search_priorities(max_gaps=3)

        assert len(priorities) <= 3
        assert all(isinstance(g, EpistemicGap) for g in priorities)

    def test_create_search_session(self, web_with_gaps):
        """Test creating a search session."""
        coordinator = VOISearchCoordinator(web_with_gaps)
        gaps = coordinator.identify_search_priorities(max_gaps=1)

        if gaps:
            session = coordinator.create_search_session(gaps[0])
            assert isinstance(session, SearchSession)
            assert session.gap == gaps[0]

    def test_generate_search_plan(self, web_with_gaps):
        """Test generating a search plan."""
        coordinator = VOISearchCoordinator(web_with_gaps)
        gaps = coordinator.identify_search_priorities(max_gaps=1)

        if gaps:
            plan = coordinator.generate_search_plan(gaps[0])

            assert 'gap' in plan
            assert 'sources' in plan
            assert 'queries' in plan
            assert len(plan['sources']) > 0
            assert len(plan['queries']) > 0

    def test_export_search_priorities(self, web_with_gaps, tmp_path):
        """Test exporting search priorities."""
        coordinator = VOISearchCoordinator(web_with_gaps)
        output_path = tmp_path / "priorities.json"

        result = coordinator.export_search_priorities(
            str(output_path),
            max_gaps=3
        )

        assert 'n_gaps' in result
        assert 'gaps' in result
        assert output_path.exists()


# =============================================================================
# FACTORY FUNCTION TESTS
# =============================================================================

class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_voi_coordinator(self, web_with_gaps):
        """Test creating coordinator via factory."""
        coordinator = create_voi_coordinator(web_with_gaps)
        assert isinstance(coordinator, VOISearchCoordinator)

    def test_detect_gaps_function(self, web_with_gaps):
        """Test detect_gaps helper function."""
        gaps = detect_gaps(web_with_gaps, max_gaps=5)

        assert isinstance(gaps, list)
        assert all(isinstance(g, EpistemicGap) for g in gaps)

    def test_calculate_voi_function(self, sample_belief):
        """Test calculate_voi helper function."""
        voi = calculate_voi(GapType.UNCERTAIN, sample_belief)

        assert 0 <= voi <= 1


# =============================================================================
# NULL RESULT VOCABULARY TESTS
# =============================================================================

class TestNullResultVocabulary:
    """Tests for null result indicators vocabulary file."""

    def test_vocab_file_exists(self):
        """Test that null result vocabulary file exists."""
        vocab_path = Path(__file__).parent.parent / "contracts" / "vocab" / "null_result_indicators.yaml"
        assert vocab_path.exists()

    def test_vocab_file_valid_yaml(self):
        """Test that vocabulary file is valid YAML."""
        import yaml
        vocab_path = Path(__file__).parent.parent / "contracts" / "vocab" / "null_result_indicators.yaml"

        with open(vocab_path) as f:
            vocab = yaml.safe_load(f)

        assert vocab is not None
        assert 'null_result_vocabulary' in vocab

    def test_vocab_has_required_categories(self):
        """Test that vocabulary has all required categories."""
        import yaml
        vocab_path = Path(__file__).parent.parent / "contracts" / "vocab" / "null_result_indicators.yaml"

        with open(vocab_path) as f:
            vocab = yaml.safe_load(f)

        categories = vocab['null_result_vocabulary']
        assert 'direct_null' in categories
        assert 'replication_failure' in categories
        assert 'hedged_null' in categories

    def test_vocab_categories_have_terms(self):
        """Test that each category has terms."""
        import yaml
        vocab_path = Path(__file__).parent.parent / "contracts" / "vocab" / "null_result_indicators.yaml"

        with open(vocab_path) as f:
            vocab = yaml.safe_load(f)

        for category, data in vocab['null_result_vocabulary'].items():
            assert 'terms' in data
            assert len(data['terms']) > 0
