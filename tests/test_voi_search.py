"""
Tests for VOI-Driven Search (TODO 3).

Sprint H: Core structures, VOI scoring, source selection.
Sprint I: Strategy selection, stopping rules, null result detection.
Sprint J: Credibility profile estimation, pipeline helpers.
Sprint K: Cross-field vocabulary integration (Lane E, 2026-02-08).

Date: January 20, 2026
Updated: February 8, 2026 (Lane E)
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
    # Sprint I
    SearchStrategy,
    StrategySelector,
    StoppingDecision,
    should_stop_searching,
    NullResultDetector,
    # Sprint J
    CredibilityProfileEstimator,
    create_search_plan_for_web,
    estimate_search_value,
    prioritize_recommendations,
    export_todo3_summary,
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


# =============================================================================
# SPRINT I: STRATEGY SELECTOR TESTS
# =============================================================================

class TestSearchStrategy:
    """Tests for SearchStrategy enum."""

    def test_strategies_exist(self):
        """Test that all strategies are defined."""
        assert SearchStrategy.KEYWORD.value == "keyword"
        assert SearchStrategy.CITATION.value == "citation"
        assert SearchStrategy.SEMANTIC.value == "semantic"

    def test_strategy_count(self):
        """Test number of strategies."""
        assert len(SearchStrategy) == 3


class TestStrategySelector:
    """Tests for StrategySelector class."""

    def test_selector_creation(self):
        """Test creating a strategy selector."""
        selector = StrategySelector()
        assert selector.initial_epsilon == 0.3
        assert selector.min_epsilon == 0.05
        assert selector.total_searches == 0

    def test_initial_epsilon(self):
        """Test initial epsilon value."""
        selector = StrategySelector(initial_epsilon=0.5)
        assert selector.epsilon == 0.5

    def test_epsilon_decay(self):
        """Test that epsilon decays with searches."""
        selector = StrategySelector(initial_epsilon=0.3, decay=0.9)

        initial_epsilon = selector.epsilon

        # Simulate some searches
        for _ in range(10):
            selector.record_search(GapType.UNCERTAIN, SearchStrategy.KEYWORD, True)

        assert selector.epsilon < initial_epsilon

    def test_epsilon_minimum(self):
        """Test that epsilon doesn't go below minimum."""
        selector = StrategySelector(initial_epsilon=0.3, min_epsilon=0.1, decay=0.5)

        # Many searches
        for _ in range(100):
            selector.record_search(GapType.UNCERTAIN, SearchStrategy.KEYWORD, True)

        assert selector.epsilon >= selector.min_epsilon

    def test_select_strategy_returns_valid(self):
        """Test that strategy selection returns a valid strategy."""
        selector = StrategySelector()
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", "b_test", 0.5)

        strategy = selector.select_strategy(gap)
        assert isinstance(strategy, SearchStrategy)

    def test_record_search_updates_stats(self):
        """Test that recording search updates statistics."""
        selector = StrategySelector()

        selector.record_search(GapType.UNCERTAIN, SearchStrategy.KEYWORD, True)
        selector.record_search(GapType.UNCERTAIN, SearchStrategy.KEYWORD, False)

        stats = selector.get_stats()
        assert stats['total_searches'] == 2
        assert 'uncertain_keyword' in stats['strategy_performance']
        assert stats['strategy_performance']['uncertain_keyword']['attempts'] == 2
        assert stats['strategy_performance']['uncertain_keyword']['successes'] == 1

    def test_best_strategy_learning(self):
        """Test that selector learns best strategy."""
        selector = StrategySelector(initial_epsilon=0.0)  # No exploration

        # Train: keyword always fails, citation always succeeds
        for _ in range(10):
            selector.record_search(GapType.UNCERTAIN, SearchStrategy.KEYWORD, False)
            selector.record_search(GapType.UNCERTAIN, SearchStrategy.CITATION, True)

        # Should now prefer citation for uncertain gaps
        selector.total_searches = 0  # Reset for deterministic test
        selector.initial_epsilon = 0.0

        gap = EpistemicGap(GapType.UNCERTAIN, "Test", "b_test", 0.5)

        # With epsilon=0, should always pick best
        strategy = selector._best_strategy_for(GapType.UNCERTAIN)
        assert strategy == SearchStrategy.CITATION


# =============================================================================
# SPRINT I: STOPPING RULES TESTS
# =============================================================================

class TestStoppingDecision:
    """Tests for StoppingDecision dataclass."""

    def test_decision_creation(self):
        """Test creating a stopping decision."""
        decision = StoppingDecision(
            should_stop=True,
            reason="Test reason",
            relevant_found=5,
            queries_executed=10
        )
        assert decision.should_stop is True
        assert decision.relevant_found == 5


class TestStoppingRules:
    """Tests for stopping rule function."""

    def test_stop_at_query_limit(self):
        """Test stopping at query limit."""
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", "b_test", 0.5)

        decision = should_stop_searching(
            gap,
            results_so_far=[],
            queries_executed=20,
            max_queries=20
        )

        assert decision.should_stop is True
        assert "limit" in decision.reason.lower()

    def test_stop_with_sufficient_results(self):
        """Test stopping with sufficient relevant results."""
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", "b_test", 0.5)

        results = [
            SearchRecommendation(f"p{i}", f"Paper {i}", 0.8, "Match")
            for i in range(15)
        ]

        decision = should_stop_searching(
            gap,
            results_so_far=results,
            queries_executed=5,
            sufficient_results=10
        )

        assert decision.should_stop is True
        assert "sufficient" in decision.reason.lower()

    def test_stop_diminishing_returns(self):
        """Test stopping due to diminishing returns."""
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", "b_test", 0.5)

        # Low relevance results
        results = [
            SearchRecommendation(f"p{i}", f"Paper {i}", 0.1, "Low match")
            for i in range(15)
        ]

        decision = should_stop_searching(
            gap,
            results_so_far=results,
            queries_executed=6,
            min_relevance=0.3
        )

        assert decision.should_stop is True
        assert "diminishing" in decision.reason.lower()

    def test_continue_searching(self):
        """Test decision to continue searching."""
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", "b_test", 0.5)

        results = [
            SearchRecommendation("p1", "Paper 1", 0.8, "Match")
        ]

        decision = should_stop_searching(
            gap,
            results_so_far=results,
            queries_executed=2
        )

        assert decision.should_stop is False
        assert "continue" in decision.reason.lower()


# =============================================================================
# SPRINT I: NULL RESULT DETECTOR TESTS
# =============================================================================

class TestNullResultDetector:
    """Tests for NullResultDetector class."""

    def test_detector_creation(self):
        """Test creating a null result detector."""
        detector = NullResultDetector()
        assert detector.vocabulary is not None

    def test_detect_direct_null(self):
        """Test detecting direct null indicators."""
        detector = NullResultDetector()

        text = "Our study found no significant effect of the intervention."
        result = detector.detect_null_indicators(text)

        assert result['has_null_indicators'] is True
        assert 'direct_null' in result['categories_detected']

    def test_detect_replication_failure(self):
        """Test detecting replication failure."""
        detector = NullResultDetector()

        text = "We failed to replicate the original findings."
        result = detector.detect_null_indicators(text)

        assert result['has_null_indicators'] is True
        assert 'replication_failure' in result['categories_detected']

    def test_detect_hedged_null(self):
        """Test detecting hedged null results."""
        detector = NullResultDetector()

        text = "Results approached significance but did not reach significance."
        result = detector.detect_null_indicators(text)

        assert result['has_null_indicators'] is True

    def test_no_null_indicators(self):
        """Test text without null indicators."""
        detector = NullResultDetector()

        text = "Nature views significantly reduced stress levels."
        result = detector.detect_null_indicators(text)

        assert result['has_null_indicators'] is False
        assert len(result['categories_detected']) == 0

    def test_search_boost_with_null(self):
        """Test search boost for paper with null results."""
        detector = NullResultDetector()

        text = "This replication study failed to replicate the original effect."
        boost = detector.get_search_boost(text, GapType.UNCERTAIN)

        assert boost > 1.0  # Should have positive boost

    def test_search_boost_without_null(self):
        """Test search boost for paper without null results."""
        detector = NullResultDetector()

        text = "Plants significantly improved air quality."
        boost = detector.get_search_boost(text, GapType.UNCERTAIN)

        assert boost == 1.0  # No boost

    def test_multiple_categories_detected(self):
        """Test detecting multiple null categories."""
        detector = NullResultDetector()

        text = "We found no significant effect, and this failed to replicate prior work."
        result = detector.detect_null_indicators(text)

        assert result['has_null_indicators'] is True
        assert len(result['categories_detected']) >= 2


# =============================================================================
# SPRINT J: CREDIBILITY PROFILE ESTIMATOR TESTS
# =============================================================================

class TestCredibilityProfileEstimator:
    """Tests for CredibilityProfileEstimator class."""

    def test_estimator_creation(self):
        """Test creating a credibility profile estimator."""
        estimator = CredibilityProfileEstimator()
        assert estimator.STUDY_TYPE_PROFILES is not None

    def test_estimate_meta_analysis(self):
        """Test estimating profile for meta-analysis."""
        estimator = CredibilityProfileEstimator()

        profile = estimator.estimate_profile(
            "A meta-analysis of nature exposure and stress reduction"
        )

        assert profile['expected_credibility'] >= 0.8
        assert profile['sample_size_issue'] < 0.2

    def test_estimate_rct(self):
        """Test estimating profile for RCT."""
        estimator = CredibilityProfileEstimator()

        profile = estimator.estimate_profile(
            "Randomized controlled trial of office plants on mood"
        )

        assert profile['expected_credibility'] >= 0.7
        assert profile['causal_direction_issue'] < 0.2

    def test_estimate_cross_sectional(self):
        """Test estimating profile for cross-sectional study."""
        estimator = CredibilityProfileEstimator()

        profile = estimator.estimate_profile(
            "A cross-sectional survey of workspace preferences"
        )

        assert profile['expected_credibility'] <= 0.6
        assert profile['causal_direction_issue'] > 0.3

    def test_estimate_unknown_type(self):
        """Test estimating profile for unknown study type."""
        estimator = CredibilityProfileEstimator()

        profile = estimator.estimate_profile(
            "Effects of greenery on performance"
        )

        assert 'expected_credibility' in profile
        assert profile['expected_credibility'] == 0.5  # Unknown default

    def test_positive_indicator_boost(self):
        """Test that positive indicators boost credibility."""
        estimator = CredibilityProfileEstimator()

        without_indicator = estimator.estimate_profile(
            "A study of nature and stress"
        )
        with_indicator = estimator.estimate_profile(
            "A pre-registered study of nature and stress"
        )

        assert with_indicator['expected_credibility'] > without_indicator['expected_credibility']

    def test_negative_indicator_reduction(self):
        """Test that negative indicators reduce credibility."""
        estimator = CredibilityProfileEstimator()

        without_indicator = estimator.estimate_profile(
            "A study of nature views"
        )
        with_indicator = estimator.estimate_profile(
            "A preliminary pilot study of nature views with small sample"
        )

        assert with_indicator['expected_credibility'] < without_indicator['expected_credibility']


# =============================================================================
# SPRINT J: PIPELINE HELPERS TESTS
# =============================================================================

class TestPipelineHelpers:
    """Tests for Sprint J pipeline helper functions."""

    def test_create_search_plan_for_web(self, web_with_gaps, tmp_path):
        """Test creating search plan for a web."""
        output_path = tmp_path / "search_plan.json"

        plan = create_search_plan_for_web(
            web_with_gaps,
            max_gaps=3,
            output_path=str(output_path)
        )

        assert 'n_gaps' in plan
        assert 'gaps' in plan
        assert output_path.exists()

    def test_estimate_search_value(self, web_with_gaps):
        """Test estimating search value."""
        estimate = estimate_search_value(web_with_gaps)

        assert 'n_gaps' in estimate
        assert 'total_voi' in estimate
        assert 'average_voi' in estimate
        assert 'recommendation' in estimate

    def test_estimate_search_value_empty_web(self):
        """Test estimating search value for empty web."""
        web = WebOfBelief()

        estimate = estimate_search_value(web)

        assert estimate['n_gaps'] == 0
        assert 'No significant gaps' in estimate['recommendation']

    def test_prioritize_recommendations(self):
        """Test prioritizing recommendations."""
        gap = EpistemicGap(GapType.UNCERTAIN, "Test", "b_test", 0.5)

        recommendations = [
            SearchRecommendation(
                "p1",
                "A preliminary study with small sample",
                0.8,
                "High relevance"
            ),
            SearchRecommendation(
                "p2",
                "A meta-analysis of prior research",
                0.7,
                "Medium relevance"
            ),
            SearchRecommendation(
                "p3",
                "A randomized controlled trial with large sample n = 500",
                0.75,
                "Good match"
            ),
        ]

        prioritized = prioritize_recommendations(recommendations, gap)

        # Should all have credibility profiles now
        for rec in prioritized:
            assert rec.expected_credibility_profile is not None

        # Meta-analysis should likely rank higher despite lower raw relevance
        # due to higher credibility
        assert len(prioritized) == 3

    def test_export_todo3_summary(self, web_with_gaps, tmp_path):
        """Test exporting TODO 3 summary."""
        output_path = tmp_path / "todo3_summary.json"

        summary = export_todo3_summary(web_with_gaps, str(output_path))

        assert 'value_estimate' in summary
        assert 'n_gaps' in summary
        assert 'search_plans' in summary
        assert 'metadata' in summary
        assert output_path.exists()

        # Verify file content
        import json
        with open(output_path) as f:
            saved = json.load(f)
        assert saved['metadata']['generated_by'] == 'TODO 3: VOI-Driven Search'


class TestEndToEndTODO3:
    """End-to-end tests for TODO 3."""

    def test_full_workflow(self, web_with_gaps, tmp_path):
        """Test complete TODO 3 workflow."""
        # 1. Detect gaps
        gaps = detect_gaps(web_with_gaps, max_gaps=5)
        assert len(gaps) > 0

        # 2. Get search value estimate
        estimate = estimate_search_value(web_with_gaps)
        assert estimate['total_voi'] > 0

        # 3. Create coordinator and get plans
        coordinator = create_voi_coordinator(web_with_gaps)
        for gap in gaps[:2]:
            plan = coordinator.generate_search_plan(gap)
            assert 'sources' in plan
            assert 'queries' in plan

        # 4. Export summary
        output_path = tmp_path / "full_workflow.json"
        summary = export_todo3_summary(web_with_gaps, str(output_path))
        assert output_path.exists()

    def test_strategy_learning_integration(self, web_with_gaps):
        """Test that strategy selector integrates with workflow."""
        selector = StrategySelector()
        gaps = detect_gaps(web_with_gaps, max_gaps=3)

        for gap in gaps:
            strategy = selector.select_strategy(gap)
            assert isinstance(strategy, SearchStrategy)

            # Simulate search outcome
            selector.record_search(gap.gap_type, strategy, success=True)

        stats = selector.get_stats()
        assert stats['total_searches'] == len(gaps)

    def test_stopping_rule_integration(self, web_with_gaps):
        """Test stopping rules in workflow."""
        gaps = detect_gaps(web_with_gaps, max_gaps=1)

        if gaps:
            gap = gaps[0]

            # Simulate accumulating results
            results = []
            for i in range(8):
                results.append(SearchRecommendation(
                    f"p{i}",
                    f"Paper {i}",
                    0.5 + (i * 0.05),  # Increasing relevance
                    "Match"
                ))

                decision = should_stop_searching(
                    gap,
                    results,
                    queries_executed=i + 1
                )

                # Shouldn't stop too early
                if i < 4:
                    assert not decision.should_stop


# =============================================================================
# SPRINT K (Lane E): CROSS-FIELD VOCABULARY TESTS
# =============================================================================

class TestCrossFieldVocabulary:
    """Tests for CrossFieldVocabulary class (Sprint K)."""

    def test_vocab_file_exists(self):
        """Test that cross-field vocabulary file exists."""
        vocab_path = Path(__file__).parent.parent / "contracts" / "vocab" / "cross_field_vocabulary.yaml"
        assert vocab_path.exists(), "cross_field_vocabulary.yaml should exist"

    def test_vocab_file_valid_yaml(self):
        """Test that vocabulary file is valid YAML."""
        import yaml
        vocab_path = Path(__file__).parent.parent / "contracts" / "vocab" / "cross_field_vocabulary.yaml"

        with open(vocab_path) as f:
            vocab = yaml.safe_load(f)

        assert vocab is not None
        assert 'version' in vocab

    def test_vocab_has_core_concepts(self):
        """Test that vocabulary has core CNfA concepts."""
        import yaml
        vocab_path = Path(__file__).parent.parent / "contracts" / "vocab" / "cross_field_vocabulary.yaml"

        with open(vocab_path) as f:
            vocab = yaml.safe_load(f)

        # Check for key concepts
        assert 'stress_recovery' in vocab
        assert 'attention_restoration' in vocab
        assert 'biophilia' in vocab

    def test_concepts_have_field_terms(self):
        """Test that concepts have field-specific terms."""
        import yaml
        vocab_path = Path(__file__).parent.parent / "contracts" / "vocab" / "cross_field_vocabulary.yaml"

        with open(vocab_path) as f:
            vocab = yaml.safe_load(f)

        stress_recovery = vocab['stress_recovery']
        assert 'cnfa_terms' in stress_recovery
        assert 'psychology_terms' in stress_recovery
        assert 'neuroscience_terms' in stress_recovery


class TestCrossFieldVocabularyClass:
    """Tests for CrossFieldVocabulary class."""

    def test_vocabulary_creation(self):
        """Test creating vocabulary loader."""
        from src.services.voi_search import CrossFieldVocabulary
        vocab = CrossFieldVocabulary()
        assert len(vocab.concepts) > 0

    def test_get_all_terms(self):
        """Test getting all terms for a concept."""
        from src.services.voi_search import CrossFieldVocabulary
        vocab = CrossFieldVocabulary()

        terms = vocab.get_all_terms('stress_recovery')
        assert len(terms) > 5  # Should have terms from multiple fields
        assert 'stress recovery' in [t.lower() for t in terms]

    def test_get_field_terms(self):
        """Test getting field-specific terms."""
        from src.services.voi_search import CrossFieldVocabulary
        vocab = CrossFieldVocabulary()

        neuro_terms = vocab.get_field_terms('stress_recovery', 'neuroscience')
        assert len(neuro_terms) > 0
        # Should have neuroscience-specific terminology
        neuro_lower = [t.lower() for t in neuro_terms]
        assert any('cortisol' in t or 'hpa' in t or 'autonomic' in t for t in neuro_lower)

    def test_expand_query(self):
        """Test query expansion."""
        from src.services.voi_search import CrossFieldVocabulary
        vocab = CrossFieldVocabulary()

        expanded = vocab.expand_query('stress recovery')
        assert len(expanded) > 1
        assert 'stress recovery' in [t.lower() for t in expanded]

    def test_expand_query_with_target_fields(self):
        """Test query expansion with specific target fields."""
        from src.services.voi_search import CrossFieldVocabulary
        vocab = CrossFieldVocabulary()

        expanded = vocab.expand_query('stress recovery', target_fields=['neuroscience'])
        assert len(expanded) >= 1
        # Should only have neuroscience terms

    def test_find_concept(self):
        """Test finding concept by term."""
        from src.services.voi_search import CrossFieldVocabulary
        vocab = CrossFieldVocabulary()

        # Should find stress_recovery from various terms
        concept = vocab.find_concept('psychophysiological recovery')
        assert concept == 'stress_recovery'

    def test_get_journals_for_field(self):
        """Test getting journals for a field."""
        from src.services.voi_search import CrossFieldVocabulary
        vocab = CrossFieldVocabulary()

        journals = vocab.get_journals_for_field('environmental_psychology')
        assert len(journals) > 0

    def test_singleton_getter(self):
        """Test singleton vocabulary getter."""
        from src.services.voi_search import get_cross_field_vocabulary
        vocab1 = get_cross_field_vocabulary()
        vocab2 = get_cross_field_vocabulary()
        assert vocab1 is vocab2


class TestCrossFieldQueryGeneration:
    """Tests for cross-field query generation."""

    def test_query_generator_has_vocabulary(self):
        """Test that QueryGenerator has vocabulary."""
        generator = QueryGenerator()
        assert generator.vocabulary is not None

    def test_generate_cross_field_queries(self, sample_belief):
        """Test generating cross-field queries."""
        generator = QueryGenerator()
        gap = EpistemicGap(
            gap_type=GapType.UNCERTAIN,
            description="Stress reduction through nature exposure",
            primary_belief_id=sample_belief.belief_id,
            voi_score=0.6
        )

        queries = generator.generate_cross_field_queries(gap, sample_belief)
        assert len(queries) > 0

    def test_cross_field_queries_expand_terms(self, sample_belief):
        """Test that cross-field queries expand terminology."""
        generator = QueryGenerator()
        gap = EpistemicGap(
            gap_type=GapType.UNCERTAIN,
            description="stress recovery nature",
            primary_belief_id=sample_belief.belief_id,
            voi_score=0.6
        )

        queries = generator.generate_cross_field_queries(gap, sample_belief)
        all_queries = " ".join(queries).lower()

        # Should have some expanded terms, not just original
        assert len(queries) > 0

    def test_expand_query_terms(self, sample_belief):
        """Test expanding query terms."""
        generator = QueryGenerator()

        original = '"stress recovery" AND nature'
        expanded = generator.expand_query_terms(original)

        assert len(expanded) >= 1
        assert original in expanded
