"""
Tests for Sprint 7: Environment Taxonomy & Construct Identity.

This module tests:
1. Environment hierarchy and structure
2. Synonym resolution
3. Antonym detection
4. Construct distinction warnings
5. Antonym-aware conflict detection integration
6. Diversity index calculation

Per expert panel (Bates): Create structured ontology for terminology resolution.
"""

import pytest
from collections import Counter

from src.services.environment_taxonomy import (
    ENVIRONMENT_HIERARCHY,
    EnvironmentMatch,
    resolve_environment_term,
    get_environment_category,
    get_synonyms,
    are_antonyms,
    get_antonym,
    get_related,
    get_theory_link,
    get_all_environment_ids,
    get_all_synonyms,
    get_environment_description,
    normalize_environment_in_content,
    check_construct_distinction,
)

from src.services.web_persistence import (
    WebPersistenceService,
    CoherenceDashboard,
)

from src.services.web_of_belief import (
    Belief,
    Credence,
    EpistemicLevel,
    BeliefStatus,
)


class TestEnvironmentHierarchy:
    """Test Case 1: Environment hierarchy structure."""

    def test_hierarchy_has_main_categories(self):
        """Verify all main categories exist."""
        # Per panel Fix 4 (Bates): category renamed from "configurational" to "config" for consistency
        expected_categories = ["spatial", "natural", "sensory", "config", "aesthetic"]
        for cat in expected_categories:
            assert cat in ENVIRONMENT_HIERARCHY, f"Missing category: {cat}"

    def test_each_category_has_description(self):
        """Verify each category has a description."""
        for cat in ENVIRONMENT_HIERARCHY:
            if not cat.startswith("_"):
                assert "_description" in ENVIRONMENT_HIERARCHY[cat]

    def test_spatial_has_expected_terms(self):
        """Verify spatial category has expected environment IDs."""
        spatial = ENVIRONMENT_HIERARCHY["spatial"]
        expected = ["spatial.volume", "spatial.openness", "spatial.enclosure",
                   "spatial.prospect", "spatial.refuge"]
        for term in expected:
            assert term in spatial, f"Missing spatial term: {term}"

    def test_natural_has_expected_terms(self):
        """Verify natural category has expected environment IDs."""
        natural = ENVIRONMENT_HIERARCHY["natural"]
        expected = ["natural.vegetation", "natural.water", "natural.daylight", "natural.views"]
        for term in expected:
            assert term in natural, f"Missing natural term: {term}"


class TestSynonymResolution:
    """Test Case 2: Synonym resolution across terminology variations."""

    def test_exact_match_canonical(self):
        """Verify exact match on canonical ID works."""
        match = resolve_environment_term("spatial.openness")
        assert match is not None
        assert match.environment_id == "spatial.openness"
        assert match.confidence == 1.0

    def test_synonym_match(self):
        """Verify synonym matches resolve to canonical ID."""
        match = resolve_environment_term("indoor plants")
        assert match is not None
        assert match.environment_id == "natural.vegetation"
        assert match.confidence == 0.9

    def test_case_insensitive(self):
        """Verify matching is case-insensitive."""
        match1 = resolve_environment_term("GREENERY")
        match2 = resolve_environment_term("greenery")
        assert match1 is not None
        assert match2 is not None
        assert match1.environment_id == match2.environment_id == "natural.vegetation"

    def test_synonym_list_retrieval(self):
        """Verify synonym list can be retrieved."""
        synonyms = get_synonyms("spatial.openness")
        assert "open plan" in synonyms
        assert "spaciousness" in synonyms

    def test_partial_match(self):
        """Verify partial matches work with lower confidence."""
        match = resolve_environment_term("visual openness rating")
        # Should match "visual openness" as partial
        assert match is not None
        assert match.environment_id == "spatial.openness"
        assert match.confidence < 1.0

    def test_no_match_returns_none(self):
        """Verify unrecognized terms return None."""
        match = resolve_environment_term("xyznonexistent")
        assert match is None


class TestAntonymDetection:
    """Test Case 3: Antonym detection for conflict resolution."""

    def test_openness_enclosure_are_antonyms(self):
        """Verify openness and enclosure are antonyms."""
        assert are_antonyms("spatial.openness", "spatial.enclosure") is True
        assert are_antonyms("spatial.enclosure", "spatial.openness") is True

    def test_prospect_refuge_are_antonyms(self):
        """Verify prospect and refuge are antonyms."""
        assert are_antonyms("spatial.prospect", "spatial.refuge") is True

    def test_lighting_darkness_are_antonyms(self):
        """Verify lighting and darkness are antonyms."""
        assert are_antonyms("sensory.lighting", "sensory.darkness") is True

    def test_complexity_simplicity_are_antonyms(self):
        """Verify aesthetic complexity and simplicity are antonyms."""
        assert are_antonyms("aesthetic.complexity", "aesthetic.simplicity") is True

    def test_non_antonyms_return_false(self):
        """Verify non-antonyms return False."""
        assert are_antonyms("spatial.openness", "natural.vegetation") is False
        assert are_antonyms("sensory.lighting", "spatial.openness") is False

    def test_get_antonym_returns_correct_id(self):
        """Verify get_antonym returns correct antonym ID."""
        assert get_antonym("spatial.openness") == "spatial.enclosure"
        assert get_antonym("spatial.enclosure") == "spatial.openness"

    def test_no_antonym_returns_none(self):
        """Verify terms without antonyms return None."""
        assert get_antonym("natural.vegetation") is None


class TestConstructDistinction:
    """Test Case 4: Same-word, different-construct separation."""

    def test_complexity_distinction_warning(self):
        """Verify complexity disambiguation warning."""
        warning = check_construct_distinction("config.complexity", "aesthetic.complexity")
        assert warning is not None
        assert "complexity" in warning.lower()
        assert "distinct" in warning.lower()

    def test_same_construct_no_warning(self):
        """Verify same construct returns no warning."""
        warning = check_construct_distinction("config.complexity", "config.complexity")
        assert warning is None

    def test_unrelated_constructs_no_warning(self):
        """Verify unrelated constructs return no warning."""
        warning = check_construct_distinction("spatial.openness", "natural.vegetation")
        assert warning is None


class TestEnvironmentUtilities:
    """Test helper utility functions."""

    def test_get_environment_category(self):
        """Verify category extraction works."""
        assert get_environment_category("spatial.openness") == "spatial"
        assert get_environment_category("natural.vegetation") == "natural"

    def test_get_related(self):
        """Verify related IDs can be retrieved."""
        related = get_related("spatial.openness")
        assert "spatial.volume" in related or "spatial.prospect" in related

    def test_get_theory_link(self):
        """Verify theory links are retrieved."""
        theory = get_theory_link("spatial.prospect")
        assert theory == "prospect_refuge"

    def test_get_all_environment_ids(self):
        """Verify all IDs can be retrieved."""
        all_ids = get_all_environment_ids()
        assert "spatial.openness" in all_ids
        assert "natural.vegetation" in all_ids
        assert len(all_ids) > 20  # Should have many IDs

    def test_get_environment_description(self):
        """Verify descriptions can be retrieved."""
        desc = get_environment_description("spatial.openness")
        assert desc == "Volumetric and geometric properties"

    def test_normalize_environment_in_content(self):
        """Verify content normalization identifies environment terms."""
        content = "Indoor plants and natural light improve mood"
        _, matches = normalize_environment_in_content(content)

        env_ids = [m.environment_id for m in matches]
        # Should find vegetation and daylight
        assert any("vegetation" in eid for eid in env_ids)
        assert any("daylight" in eid or "light" in eid for eid in env_ids)


class TestAntonymAwareConflictDetection:
    """Test Case 5: Integration of antonym awareness in conflict detection."""

    def test_antonym_equivalence_detected(self):
        """Verify antonym equivalence is detected and prevents false conflict."""
        service = WebPersistenceService(":memory:")

        # "Openness increases wellbeing" ≡ "Enclosure decreases wellbeing"
        b1 = Belief(
            belief_id="antonym:001",
            content="Spatial openness increases wellbeing",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )

        b2 = Belief(
            belief_id="antonym:002",
            content="Spatial enclosure decreases wellbeing",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.65, 0.2)
        )

        # Should be detected as antonym equivalent (same finding)
        assert service._check_antonym_equivalence(b1, b2) is True

    def test_non_antonym_equivalence_not_detected(self):
        """Verify non-antonym pairs are not marked as equivalent."""
        service = WebPersistenceService(":memory:")

        b1 = Belief(
            belief_id="nonantonym:001",
            content="Plants increase wellbeing",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )

        b2 = Belief(
            belief_id="nonantonym:002",
            content="Light decreases stress",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.65, 0.2)
        )

        # Different environments, should NOT be antonym equivalent
        assert service._check_antonym_equivalence(b1, b2) is False

    def test_same_direction_not_antonym_equivalent(self):
        """Verify same direction effects are not antonym equivalent."""
        service = WebPersistenceService(":memory:")

        # Same direction effects with antonym environments = genuine conflict
        b1 = Belief(
            belief_id="samedir:001",
            content="Openness increases stress",
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.7, 0.2)
        )

        b2 = Belief(
            belief_id="samedir:002",
            content="Enclosure increases stress",  # Same direction, should not be equivalent
            level=EpistemicLevel.EMPIRICAL,
            status=BeliefStatus.TENTATIVE,
            credence=Credence(0.65, 0.2)
        )

        assert service._check_antonym_equivalence(b1, b2) is False


class TestDiversityIndex:
    """Test Case 6: Diversity index calculation."""

    def test_shannon_entropy_uniform(self):
        """Verify Shannon entropy calculation for uniform distribution."""
        service = WebPersistenceService(":memory:")

        # Uniform distribution should have maximum entropy
        counts = Counter({"a": 10, "b": 10, "c": 10, "d": 10})
        entropy = service._shannon_entropy(counts)

        # Maximum entropy for 4 categories = ln(4) ≈ 1.386
        import math
        expected = math.log(4)
        assert abs(entropy - expected) < 0.01

    def test_shannon_entropy_skewed(self):
        """Verify Shannon entropy for skewed distribution."""
        service = WebPersistenceService(":memory:")

        # Highly skewed distribution should have low entropy
        counts = Counter({"a": 100, "b": 1, "c": 1, "d": 1})
        entropy = service._shannon_entropy(counts)

        # Should be much lower than uniform
        import math
        max_entropy = math.log(4)
        assert entropy < max_entropy * 0.5

    def test_shannon_entropy_single(self):
        """Verify Shannon entropy for single category is zero."""
        service = WebPersistenceService(":memory:")

        counts = Counter({"a": 100})
        entropy = service._shannon_entropy(counts)

        assert entropy == 0.0

    def test_diversity_index_empty(self):
        """Verify diversity index is zero for empty list."""
        service = WebPersistenceService(":memory:")

        diversity = service._compute_diversity_index([])
        assert diversity == 0.0

    def test_diversity_index_computation(self):
        """Verify diversity index combines environment and outcome entropy."""
        service = WebPersistenceService(":memory:")

        # Create beliefs with varied domains
        beliefs = [
            Belief(
                belief_id=f"div:{i}",
                content=f"Belief {i}",
                level=EpistemicLevel.EMPIRICAL,
                status=BeliefStatus.TENTATIVE,
                credence=Credence(0.5, 0.2),
                domain=domain
            )
            for i, domain in enumerate(["cog", "affect", "physio", "cog", "affect"])
        ]

        diversity = service._compute_diversity_index(beliefs)

        # Should be > 0 since we have multiple domains
        assert diversity > 0.0

    def test_coherence_dashboard_includes_diversity(self):
        """Verify CoherenceDashboard includes diversity_index field."""
        dashboard = CoherenceDashboard(
            global_coherence=0.7,
            n_beliefs=10,
            n_constraints=5,
            constraint_density=0.1,
            n_conflicts=1,
            n_isolated_beliefs=2,
            n_theories=2,
            inter_theory_coherence=0.5,
            entropy=1.0,
            mean_uncertainty=0.3,
            diversity_index=0.8
        )

        assert dashboard.diversity_index == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
