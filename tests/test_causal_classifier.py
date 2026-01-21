"""
Tests for Causal Classifier Service
====================================

H1: Three-tier causal classification per Pearl panel recommendation.

Date: January 21, 2026
Sprint E1 (Panel HIGH Priority)
"""

import pytest
from src.services.causal_classifier import (
    CausalClassifier,
    CausalClassification,
    CausalTier,
    classify_causal_tier,
    get_causal_tier
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def classifier():
    """Create a classifier instance."""
    return CausalClassifier()


# =============================================================================
# Basic Classification Tests
# =============================================================================

class TestBasicClassification:
    """Tests for basic tier classification."""

    def test_classifier_creation(self, classifier):
        """Test classifier can be created."""
        assert classifier is not None

    def test_classify_returns_classification(self, classifier):
        """Test classify returns a CausalClassification."""
        result = classifier.classify("Natural light improves productivity")
        assert isinstance(result, CausalClassification)
        assert result.tier in CausalTier

    def test_classification_has_all_fields(self, classifier):
        """Test classification has all required fields."""
        result = classifier.classify("Light causes improved mood")
        assert hasattr(result, 'tier')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'evidence_type')
        assert hasattr(result, 'matched_patterns')
        assert hasattr(result, 'warnings')
        assert hasattr(result, 'confounder_mentioned')
        assert hasattr(result, 'mechanism_mentioned')


# =============================================================================
# Causal Tier Tests
# =============================================================================

class TestCausalTier:
    """
    Tests for CAUSAL tier classification.

    E1.D5 Panel (Pearl): Design-first approach means:
    - Causal language ALONE (without experimental, mechanism, or confounder) → SUGGESTIVE
    - Causal language WITH experimental/mechanism/confounder → CAUSAL
    """

    def test_causal_language_alone_is_suggestive(self, classifier):
        """E1.D5: Causal language without support is SUGGESTIVE, not CAUSAL (per Pearl)."""
        # Per Pearl: Causal language in observational studies without mechanism
        # or confounder control should be classified as SUGGESTIVE
        result = classifier.classify("Natural light causes improved productivity")
        assert result.tier == CausalTier.SUGGESTIVE
        assert 'causal:causes' in result.matched_patterns

    def test_causal_with_mechanism_is_causal(self, classifier):
        """E1.D5: Causal language WITH mechanism is CAUSAL."""
        result = classifier.classify(
            "Natural light causes improved productivity through the circadian mechanism"
        )
        assert result.tier == CausalTier.CAUSAL
        assert result.mechanism_mentioned is True

    def test_causal_with_confounder_control_is_causal(self, classifier):
        """E1.D5: Causal language WITH confounder control is CAUSAL."""
        result = classifier.classify(
            "Natural light causes improved productivity when controlled for age"
        )
        assert result.tier == CausalTier.CAUSAL
        assert result.confounder_mentioned is True

    def test_experimental_language(self, classifier):
        """Test experimental language boosts to CAUSAL."""
        result = classifier.classify(
            "In a randomized controlled trial, natural light improved productivity"
        )
        assert result.tier == CausalTier.CAUSAL
        assert "experimental" in result.evidence_type

    def test_causal_mechanism_language(self, classifier):
        """Test causal mechanism language is CAUSAL."""
        result = classifier.classify(
            "The causal mechanism involves circadian rhythm regulation"
        )
        assert result.tier == CausalTier.CAUSAL

    def test_quasi_experimental_with_causal_is_causal(self, classifier):
        """E1.D5: Quasi-experimental design + causal language is CAUSAL."""
        # Use diff-in-diff terminology to avoid "experiment" matching experimental
        result = classifier.classify(
            "Using difference-in-differences, we found light causes productivity gains"
        )
        assert result.tier == CausalTier.CAUSAL
        assert result.is_quasi_experimental is True
        assert "quasi-experimental" in result.evidence_type

    def test_quasi_experimental_detected(self, classifier):
        """E1.D5: Quasi-experimental patterns are detected."""
        result = classifier.classify(
            "Using a difference-in-differences approach, we found light affects mood"
        )
        assert result.is_quasi_experimental is True
        assert any("quasi-exp:" in p for p in result.matched_patterns)


# =============================================================================
# Suggestive Tier Tests
# =============================================================================

class TestSuggestiveTier:
    """Tests for SUGGESTIVE tier classification."""

    def test_affects_language(self, classifier):
        """Test 'affects' is classified as SUGGESTIVE."""
        result = classifier.classify("Natural light affects worker wellbeing")
        assert result.tier == CausalTier.SUGGESTIVE

    def test_improves_language(self, classifier):
        """Test 'improves' is classified as SUGGESTIVE."""
        result = classifier.classify("Daylight improves cognitive performance")
        assert result.tier == CausalTier.SUGGESTIVE

    def test_reduces_language(self, classifier):
        """Test 'reduces' is classified as SUGGESTIVE."""
        result = classifier.classify("Natural light reduces stress levels")
        assert result.tier == CausalTier.SUGGESTIVE

    def test_influences_language(self, classifier):
        """Test 'influences' is classified as SUGGESTIVE."""
        result = classifier.classify("Window views influence mood significantly")
        assert result.tier == CausalTier.SUGGESTIVE

    def test_may_cause_language(self, classifier):
        """Test 'may cause' is classified as SUGGESTIVE."""
        result = classifier.classify("Lack of natural light may cause fatigue")
        assert result.tier == CausalTier.SUGGESTIVE

    def test_suggests_affect_language(self, classifier):
        """Test 'suggests that X affects' is SUGGESTIVE."""
        result = classifier.classify("Evidence suggests that light affects mood")
        assert result.tier == CausalTier.SUGGESTIVE


# =============================================================================
# Associational Tier Tests
# =============================================================================

class TestAssociationalTier:
    """Tests for ASSOCIATIONAL tier classification."""

    def test_correlation_language(self, classifier):
        """Test 'correlation' is classified as ASSOCIATIONAL."""
        result = classifier.classify(
            "There is a correlation between daylight and productivity"
        )
        assert result.tier == CausalTier.ASSOCIATIONAL

    def test_association_language(self, classifier):
        """Test 'association' is classified as ASSOCIATIONAL."""
        result = classifier.classify(
            "Natural light is associated with better wellbeing"
        )
        assert result.tier == CausalTier.ASSOCIATIONAL

    def test_related_to_language(self, classifier):
        """Test 'related to' is classified as ASSOCIATIONAL."""
        result = classifier.classify("Mood levels are related to light exposure")
        assert result.tier == CausalTier.ASSOCIATIONAL

    def test_linked_to_language(self, classifier):
        """Test 'linked to' is classified as ASSOCIATIONAL."""
        result = classifier.classify("Productivity is linked to daylight access")
        assert result.tier == CausalTier.ASSOCIATIONAL

    def test_purely_observational(self, classifier):
        """Test purely observational language is ASSOCIATIONAL."""
        result = classifier.classify(
            "We observed that workers with window access and higher satisfaction scores"
        )
        assert result.tier == CausalTier.ASSOCIATIONAL


# =============================================================================
# Confounder Detection Tests
# =============================================================================

class TestConfounderDetection:
    """Tests for confounder acknowledgment detection."""

    def test_controlled_for_detected(self, classifier):
        """Test 'controlled for' is detected."""
        result = classifier.classify(
            "Light improves productivity when controlled for age"
        )
        assert result.confounder_mentioned is True

    def test_adjusted_for_detected(self, classifier):
        """Test 'adjusted for' is detected."""
        result = classifier.classify(
            "Effects remain significant after adjusting for income"
        )
        assert result.confounder_mentioned is True

    def test_covariate_detected(self, classifier):
        """Test 'covariate' is detected."""
        result = classifier.classify(
            "Including education as a covariate, the effect persists"
        )
        assert result.confounder_mentioned is True

    def test_no_confounder_warning(self, classifier):
        """E1.D5: Causal language without confounder is now SUGGESTIVE (per Pearl)."""
        # Without mechanism or confounder, causal language → SUGGESTIVE
        result = classifier.classify("Light causes improved productivity")
        assert result.tier == CausalTier.SUGGESTIVE
        # Note: warning about confounder is only on CAUSAL tier
        assert result.confounder_mentioned is False

    def test_no_warning_with_confounder(self, classifier):
        """Test no confounder warning when confounders mentioned."""
        result = classifier.classify(
            "Light causes improved productivity when controlling for experience"
        )
        # Should not have the confounder warning
        assert not any(
            "without explicit confounder" in w for w in result.warnings
        )


# =============================================================================
# Mechanism Detection Tests
# =============================================================================

class TestMechanismDetection:
    """Tests for mechanism mention detection."""

    def test_mechanism_detected(self, classifier):
        """Test 'mechanism' is detected."""
        result = classifier.classify(
            "The mechanism by which light affects mood involves serotonin"
        )
        assert result.mechanism_mentioned is True

    def test_pathway_detected(self, classifier):
        """Test 'pathway' is detected."""
        result = classifier.classify(
            "This pathway links daylight to circadian rhythm regulation"
        )
        assert result.mechanism_mentioned is True

    def test_mediated_by_detected(self, classifier):
        """Test 'mediated by' is detected."""
        result = classifier.classify(
            "The effect is mediated by cortisol levels"
        )
        assert result.mechanism_mentioned is True


# =============================================================================
# Context Tests
# =============================================================================

class TestContextEffects:
    """Tests for context effects on classification."""

    def test_experimental_context_boosts_tier(self, classifier):
        """Test experimental context boosts classification."""
        result = classifier.classify(
            "Light affects productivity",
            context={'study_type': 'RCT'}
        )
        assert result.tier == CausalTier.CAUSAL

    def test_abstract_only_warning(self, classifier):
        """Test warning for causal claims from abstracts."""
        # Need mechanism or confounder to get CAUSAL tier (to trigger warning)
        result = classifier.classify(
            "Light causes improved productivity via circadian pathway",
            context={'source_depth': 'abstract'}
        )
        assert result.tier == CausalTier.CAUSAL
        assert any("abstract" in w.lower() for w in result.warnings)

    def test_observational_study_warning(self, classifier):
        """Test warning for causal language in observational study."""
        # Need mechanism or confounder to get CAUSAL tier (to trigger warning)
        result = classifier.classify(
            "Light causes improved productivity after controlling for age",
            context={'study_type': 'observational'}
        )
        assert result.tier == CausalTier.CAUSAL
        assert any("observational" in w.lower() for w in result.warnings)


# =============================================================================
# Confidence Tests
# =============================================================================

class TestConfidenceScores:
    """Tests for confidence scoring."""

    def test_strong_causal_high_confidence(self, classifier):
        """Test strong causal language has high confidence."""
        result = classifier.classify(
            "In a randomized trial, natural light causes significantly improved productivity"
        )
        assert result.confidence >= 0.7

    def test_weak_signal_lower_confidence(self, classifier):
        """Test weak signals have lower confidence."""
        result = classifier.classify("Light was observed in the workspace")
        assert result.confidence < 0.6

    def test_confidence_capped(self, classifier):
        """Test confidence is capped at reasonable level."""
        result = classifier.classify(
            "A randomized controlled trial demonstrated that natural light causes "
            "improved productivity, leads to better mood, and results in reduced stress"
        )
        assert result.confidence <= 0.95


# =============================================================================
# Serialization Tests
# =============================================================================

class TestSerialization:
    """Tests for classification serialization."""

    def test_to_dict(self, classifier):
        """Test to_dict serialization."""
        result = classifier.classify("Light affects mood")
        d = result.to_dict()

        assert 'tier' in d
        assert 'confidence' in d
        assert 'evidence_type' in d
        assert 'matched_patterns' in d
        assert 'warnings' in d
        assert 'confounder_mentioned' in d
        assert 'mechanism_mentioned' in d

    def test_tier_value_in_dict(self, classifier):
        """Test tier is serialized as string value."""
        # Need mechanism to get CAUSAL tier (per Pearl)
        result = classifier.classify("Light causes mood changes via serotonin pathway")
        d = result.to_dict()
        assert d['tier'] == 'causal'
        assert 'is_quasi_experimental' in d  # E1.D5 new field


# =============================================================================
# Convenience Function Tests
# =============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_classify_causal_tier_function(self):
        """Test classify_causal_tier convenience function."""
        # Need mechanism for CAUSAL tier per Pearl
        result = classify_causal_tier("Light causes improved mood via the circadian mechanism")
        assert isinstance(result, CausalClassification)
        assert result.tier == CausalTier.CAUSAL

    def test_get_causal_tier_function(self):
        """Test get_causal_tier convenience function."""
        tier = get_causal_tier("Light is associated with mood")
        assert tier == CausalTier.ASSOCIATIONAL


# =============================================================================
# Edge Case Tests
# =============================================================================

# =============================================================================
# E1.D5: Neuroarchitecture Domain Patterns (per Kaplan)
# =============================================================================

class TestNeuroarchitecturePatterns:
    """E1.D5: Tests for neuroarchitecture-specific patterns (per Kaplan)."""

    def test_design_intervention_detected(self, classifier):
        """Test 'design intervention' is detected as causal."""
        result = classifier.classify(
            "The design intervention improved occupant comfort"
        )
        assert any("causal:design intervention" in p for p in result.matched_patterns)

    def test_restorative_effect_detected(self, classifier):
        """Test 'restorative effect' is detected as suggestive."""
        result = classifier.classify(
            "The restorative effect of nature views was observed"
        )
        assert any("suggestive:restorative effect" in p for p in result.matched_patterns)
        assert result.tier == CausalTier.SUGGESTIVE

    def test_biophilic_response_detected(self, classifier):
        """Test 'biophilic response' is detected as suggestive."""
        result = classifier.classify(
            "Participants showed a biophilic response to natural elements"
        )
        assert any("suggestive:biophilic response" in p for p in result.matched_patterns)

    def test_preference_for_detected(self, classifier):
        """Test 'preference for' is detected as associational."""
        result = classifier.classify(
            "Workers showed a preference for natural lighting"
        )
        assert any("associational:preference for" in p for p in result.matched_patterns)
        assert result.tier == CausalTier.ASSOCIATIONAL

    def test_rated_higher_detected(self, classifier):
        """Test 'rated higher' is detected as associational."""
        result = classifier.classify(
            "Natural light conditions were rated higher by participants"
        )
        # Pattern captures 'higher' (the variable part), so check for that
        assert any("associational:higher" in p for p in result.matched_patterns)
        assert result.tier == CausalTier.ASSOCIATIONAL


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_content(self, classifier):
        """Test empty content is handled."""
        result = classifier.classify("")
        assert result.tier == CausalTier.ASSOCIATIONAL
        assert result.confidence < 0.5

    def test_no_causal_language(self, classifier):
        """Test content without causal language."""
        result = classifier.classify("The study measured light levels")
        assert result.tier == CausalTier.ASSOCIATIONAL

    def test_mixed_signals(self, classifier):
        """Test content with mixed causal/correlational language."""
        # Need mechanism for CAUSAL tier per Pearl
        result = classifier.classify(
            "While correlated, natural light causes improved productivity via circadian mechanism"
        )
        # Should classify as causal due to mechanism support
        assert result.tier == CausalTier.CAUSAL
        # But should warn about mixed signals
        assert any("mixed" in w.lower() for w in result.warnings)

    def test_very_long_content(self, classifier):
        """Test very long content is handled."""
        long_content = "Natural light affects productivity. " * 100
        result = classifier.classify(long_content)
        assert result is not None
        assert result.tier in CausalTier

    def test_special_characters(self, classifier):
        """Test content with special characters."""
        result = classifier.classify(
            "Light affects mood (p<0.05) — significantly improved!"
        )
        assert result is not None
        assert result.tier == CausalTier.SUGGESTIVE
