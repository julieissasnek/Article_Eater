"""
Tests for belief_env_outcome_extractor — confidence-graded extraction.

Success Conditions tested:
  SC-FTR-1: Extraction Coverage (≥30% of beliefs get env or outcome)
  SC-FTR-2: Extraction Precision (>50% writable matches are HIGH confidence)
  SC-FTR-3: Environment ID Coverage (≥20% of beliefs get env_id)
  SC-FTR-4: Outcome ID Coverage (≥25% of beliefs get outcome_id)
  SC-FTR-5: Bridge Vocabulary Utilization (≥40% of bridge vocabs used)
  SC-FTR-6: Low Confidence Ratio (<20% of extractions are LOW)
"""

import pytest
from src.services.belief_env_outcome_extractor import (
    extract_env_outcome,
    ExtractionResult,
    BeliefExtraction,
    Confidence,
    WRITE_THRESHOLD,
    check_success_conditions,
    ExtractionReport,
)


# ============================================================================
# Unit tests: confidence grading
# ============================================================================

class TestConfidenceGrading:
    """Test that confidence levels are assigned correctly."""

    def test_high_confidence_env(self):
        """Clear environmental matches should be HIGH confidence."""
        ex = extract_env_outcome("B1", "Ceiling height influences creative thinking")
        assert ex.best_env_id == "ceiling_height_m"
        assert ex.best_env_confidence >= 0.70
        assert ex.env_extractions[0].confidence_level == Confidence.HIGH

    def test_medium_confidence_env(self):
        """Moderate matches should be MEDIUM confidence."""
        ex = extract_env_outcome("B2", "Natural light exposure during morning hours")
        assert ex.best_env_id is not None
        assert ex.best_env_confidence >= WRITE_THRESHOLD
        assert ex.env_extractions[0].confidence_level in (Confidence.HIGH, Confidence.MEDIUM)

    def test_no_match(self):
        """Vague content should produce no match."""
        ex = extract_env_outcome("B3", "The quick brown fox jumps over the lazy dog")
        assert ex.best_env_id is None
        assert ex.best_outcome_id is None
        assert not ex.is_writable

    def test_is_writable_gate(self):
        """Only MEDIUM+ confidence extractions should be writable."""
        ex = extract_env_outcome("B4", "Noise level 70 dBA impairs attention")
        assert ex.is_writable
        assert ex.best_env_confidence >= WRITE_THRESHOLD or ex.best_outcome_confidence >= WRITE_THRESHOLD


# ============================================================================
# Unit tests: specific extractions
# ============================================================================

class TestSpecificExtractions:
    """Test extraction accuracy for known content patterns."""

    def test_nature_stress(self):
        """Nature + stress content should extract correctly."""
        ex = extract_env_outcome("B5", "Nature exposure reduces cortisol levels and stress markers")
        assert ex.best_env_id == "has_nature_view"
        assert ex.best_outcome_id == "stress"

    def test_noise_attention(self):
        """Noise + attention content should map correctly."""
        ex = extract_env_outcome("B6", "Noise level above 70 dBA impairs sustained attention tasks")
        assert ex.best_env_id == "ambient_noise_dba"
        assert ex.best_outcome_id == "attention"

    def test_ceiling_creativity(self):
        """Ceiling + creativity is a clear match."""
        ex = extract_env_outcome("B7", "Ceiling height influences creative thinking through spatial volume")
        assert ex.best_env_id == "ceiling_height_m"
        assert ex.best_outcome_id == "creativity"

    def test_window_belonging(self):
        """Windows + belonging should map to window_area_ratio + social_interaction."""
        ex = extract_env_outcome("B8", "Presence of windows -> sense of belonging score (increase)")
        assert ex.best_env_id == "window_area_ratio"
        assert ex.best_outcome_id == "social_interaction"

    def test_material_content(self):
        """Material property content should extract env."""
        ex = extract_env_outcome("B9", "Material: Wood surface; thermal effusivity affects touch response")
        assert ex.best_env_id == "primary_material"

    def test_color_temperature(self):
        """Color temperature content bridges to both light and thermal."""
        ex = extract_env_outcome("B10", "Color temperature affects perceived thermal comfort")
        assert ex.best_env_id is not None
        assert ex.best_outcome_id == "thermal_comfort"

    def test_wayfinding(self):
        """Wayfinding content should map correctly."""
        ex = extract_env_outcome("B11", "Navigation efficiency in complex hospital layouts")
        assert ex.best_outcome_id == "wayfinding"

    def test_sleep_circadian(self):
        """Circadian content should map to sleep_quality."""
        ex = extract_env_outcome("B12", "Circadian entrainment of melatonin rhythm improves sleep")
        assert ex.best_outcome_id == "sleep_quality"


# ============================================================================
# Integration test: no false positives for unrelated content
# ============================================================================

class TestFalsePositivePrevention:
    """Ensure extractor doesn't produce false matches on non-architectural content."""

    def test_vague_psych_content(self):
        """Abstract psychological content without env context should not match env."""
        ex = extract_env_outcome("FP1", "Psychiatric ward design influences interpersonal difficulties")
        # This is too vague — no specific env/outcome terms
        assert ex.best_env_id is None or ex.best_env_confidence < WRITE_THRESHOLD

    def test_purely_abstract(self):
        """Abstract epistemological content should not match."""
        ex = extract_env_outcome("FP2", "Awareness of messages conveyed by sensory channels")
        assert not ex.is_writable

    def test_mechanism_only(self):
        """Pure mechanism content without env/outcome should not match."""
        ex = extract_env_outcome("FP3", "Dopamine modulates reward prediction error signals in VTA")
        # Might match 'reward' as outcome, but should not match env
        assert ex.best_env_id is None


# ============================================================================
# Success condition smoke test
# ============================================================================

class TestSuccessConditions:
    """Test success condition scoring."""

    def test_conditions_structure(self):
        """Success conditions should have correct structure."""
        report = ExtractionReport(total_beliefs=100, beliefs_with_env=40, beliefs_with_outcome=50)
        report.sc_env_coverage = 0.40
        report.sc_out_coverage = 0.50
        report.sc_coverage = 0.45
        report.sc_precision = 0.60
        report.sc_bridge_util = 0.50
        report.high_confidence_env = 20
        report.medium_confidence_env = 20
        report.high_confidence_outcome = 30
        report.medium_confidence_outcome = 20
        report.low_confidence_env = 5
        report.low_confidence_outcome = 5
        conditions = check_success_conditions(report)
        assert len(conditions) == 6
        assert all("id" in c for c in conditions)
        assert all("passed" in c for c in conditions)

    def test_healthy_report(self):
        """A good report should pass most conditions."""
        report = ExtractionReport(
            total_beliefs=100,
            beliefs_with_env=40,
            beliefs_with_outcome=50,
            sc_env_coverage=0.40,
            sc_out_coverage=0.50,
            sc_coverage=0.45,
            sc_precision=0.60,
            sc_bridge_util=0.50,
            high_confidence_env=20,
            medium_confidence_env=20,
            high_confidence_outcome=30,
            medium_confidence_outcome=20,
            low_confidence_env=3,
            low_confidence_outcome=3,
        )
        conditions = check_success_conditions(report)
        passed = sum(1 for c in conditions if c["passed"])
        assert passed >= 4, f"Expected ≥4 conditions to pass, got {passed}"


# ============================================================================
# Batch extraction test using actual extraction data
# ============================================================================

class TestBatchExtraction:
    """Test against a batch of real content from extraction JSONs."""

    @pytest.fixture
    def sample_beliefs(self):
        """Sample of real belief content from extraction data."""
        return [
            ("B-NATURE-1", "Nature exposure reduces cortisol levels in healthcare settings"),
            ("B-NOISE-1", "Background noise at 70 dBA impairs cognitive performance on sustained attention tasks"),
            ("B-LIGHT-1", "Natural light exposure via windows improves mood and circadian rhythm"),
            ("B-CEIL-1", "High ceilings promote creative divergent thinking through spatial volume perception"),
            ("B-MATER-1", "Material: Water; Effective flow resistivity: 2170 kPa·s/m2"),
            ("B-COLOR-1", "Warm color temperature enhances perceived thermal comfort"),
            ("B-SLEEP-1", "Morning light exposure shifts melatonin onset earlier, improving sleep quality"),
            ("B-WAYFIND-1", "Complex hospital layouts reduce wayfinding efficiency for elderly patients"),
            ("B-SOCIAL-1", "Presence of windows increases sense of belonging among workers"),
            ("B-VAGUE-1", "Design affects human experience in complex ways"),
        ]

    def test_batch_coverage(self, sample_beliefs):
        """At least 70% of specific beliefs should get at least one extraction."""
        writable_count = 0
        for bid, content in sample_beliefs:
            ex = extract_env_outcome(bid, content)
            if ex.is_writable:
                writable_count += 1
        # 9 of 10 are specific enough; the last is too vague
        assert writable_count >= 7, f"Expected ≥7 writable, got {writable_count}"

    def test_batch_no_misattribution(self, sample_beliefs):
        """No belief should get an obviously wrong env or outcome."""
        ex = extract_env_outcome("B-NOISE-1", "Background noise impairs attention tasks")
        assert ex.best_env_id == "ambient_noise_dba"
        assert ex.best_outcome_id == "attention"
        # NOT ceiling_height, NOT nature, NOT color
        assert ex.best_env_id != "ceiling_height_m"
        assert ex.best_env_id != "has_nature_view"
