"""
Tests for Credibility Testing Module.

Phase E: Implementation (Sprint B)
TODO 1: Credibility Testing Method

Test categories:
1. Unit tests for individual checks
2. Integration tests for CredibilityTester
3. Failure Standard corpus tests

Date: January 20, 2026
"""

import pytest
from datetime import datetime, timezone

from src.services.credibility_testing import (
    Decision,
    CredibilityFlag,
    CredibilityReport,
    CredibilityChecks,
    CredibilityTester,
    WebSnapshot,
    get_design_strength,
    scope_distance,
    classify_population,
    safe_check,
    create_tester,
    quick_check,
    DESIGN_STRENGTH,
    POPULATION_SPECIFICITY,
)

from src.services.web_of_belief import (
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType,
    CausalDirection,
    ScopeConditions,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_belief():
    """Create a sample belief for testing."""
    return Belief(
        belief_id="test_belief_1",
        content="Nature exposure reduces stress",
        level=EpistemicLevel.EMPIRICAL,
        status=BeliefStatus.TENTATIVE,
        credence=Credence(value=0.65, uncertainty=0.2),
        paper_ids=["paper_001"],
    )


@pytest.fixture
def sample_constraint():
    """Create a sample constraint for testing."""
    return Constraint(
        constraint_id="test_constraint_1",
        source_id="test_belief_1",
        target_id="test_belief_2",
        constraint_type=ConstraintType.SUPPORTS,
        strength=0.6,
        causal_direction=CausalDirection.CORRELATIONAL,
    )


@pytest.fixture
def checks():
    """Create CredibilityChecks instance."""
    return CredibilityChecks()


@pytest.fixture
def tester():
    """Create CredibilityTester instance."""
    return CredibilityTester()


# =============================================================================
# UNIT TESTS: Decision and CredibilityFlag
# =============================================================================

class TestDecision:
    """Tests for Decision enum."""

    def test_decision_values(self):
        """Verify Decision enum has expected values."""
        assert Decision.BLOCK.value == "block"
        assert Decision.REVIEW.value == "review"

    def test_decision_comparison(self):
        """Verify Decision values are distinct."""
        assert Decision.BLOCK != Decision.REVIEW


class TestCredibilityFlag:
    """Tests for CredibilityFlag dataclass."""

    def test_flag_creation(self):
        """Test basic flag creation."""
        flag = CredibilityFlag(
            decision=Decision.REVIEW,
            reason="Test reason",
            confidence=0.8,
        )
        assert flag.decision == Decision.REVIEW
        assert flag.reason == "Test reason"
        assert flag.confidence == 0.8

    def test_flag_to_dict(self):
        """Test flag serialization."""
        flag = CredibilityFlag(
            decision=Decision.BLOCK,
            reason="Invalid value",
            confidence=1.0,
            field_name="sample_size",
            expected="> 0",
            observed="-50",
        )
        d = flag.to_dict()
        assert d['decision'] == "block"
        assert d['field_name'] == "sample_size"


class TestCredibilityReport:
    """Tests for CredibilityReport."""

    def test_clean_report(self):
        """Test report with no flags."""
        report = CredibilityReport(
            article_id="test_001",
            timestamp=datetime.now(timezone.utc),
        )
        assert report.is_clean
        assert len(report.flags) == 0

    def test_add_flag(self):
        """Test adding flags to report."""
        report = CredibilityReport(
            article_id="test_001",
            timestamp=datetime.now(timezone.utc),
        )

        flag = CredibilityFlag(
            decision=Decision.REVIEW,
            reason="Test",
            confidence=0.5,
        )
        report.add_flag(flag)

        assert not report.is_clean
        assert len(report.flags) == 1
        assert report.overall_decision == Decision.REVIEW

    def test_block_wins(self):
        """Test that BLOCK decision wins over REVIEW."""
        report = CredibilityReport(
            article_id="test_001",
            timestamp=datetime.now(timezone.utc),
        )

        # Add REVIEW flag first
        report.add_flag(CredibilityFlag(
            decision=Decision.REVIEW,
            reason="Minor issue",
            confidence=0.5,
        ))
        assert report.overall_decision == Decision.REVIEW

        # Add BLOCK flag
        report.add_flag(CredibilityFlag(
            decision=Decision.BLOCK,
            reason="Critical issue",
            confidence=1.0,
        ))
        assert report.overall_decision == Decision.BLOCK

    def test_to_explanation_context(self):
        """Test conversion to explanation context for TODO 2."""
        report = CredibilityReport(
            article_id="test_001",
            timestamp=datetime.now(timezone.utc),
        )
        report.add_flag(CredibilityFlag(
            decision=Decision.REVIEW,
            reason="Scope overreach",
            confidence=0.7,
        ))

        context = report.to_explanation_context()
        assert context['article_id'] == "test_001"
        assert context['decision'] == "review"
        assert "Scope overreach" in context['reasons']


# =============================================================================
# UNIT TESTS: Helper Functions
# =============================================================================

class TestDesignStrength:
    """Tests for study design strength."""

    def test_known_designs(self):
        """Test strength values for known designs."""
        assert get_design_strength("rct") == 1.0
        assert get_design_strength("correlational") == 0.4
        assert get_design_strength("quasi_experiment") == 0.7

    def test_case_insensitive(self):
        """Test case insensitivity."""
        assert get_design_strength("RCT") == 1.0
        assert get_design_strength("Correlational") == 0.4

    def test_unknown_design(self):
        """Test default for unknown designs."""
        assert get_design_strength("unknown_type") == 0.4
        assert get_design_strength(None) == 0.4


class TestScopeDistance:
    """Tests for scope distance calculation."""

    def test_same_scope(self):
        """Test distance when sample matches scope."""
        distance = scope_distance("undergraduate students", "students")
        assert distance == 0.0 or distance < 0.1

    def test_large_distance(self):
        """Test distance for overreach."""
        distance = scope_distance("ADHD children", None)  # Universal claim
        assert distance > 0.5

    def test_classify_population_clinical(self):
        """Test population classification."""
        assert classify_population("patients with depression") == "specific_clinical"
        assert classify_population("hospital patients") == "clinical"

    def test_classify_population_demographic(self):
        """Test demographic classification."""
        assert classify_population("elderly adults") == "demographic_subset"
        assert classify_population("undergraduate students") == "demographic_subset"


class TestSafeCheck:
    """Tests for safe_check wrapper."""

    def test_successful_check(self):
        """Test wrapper with successful check."""
        def good_check() -> list:
            return [CredibilityFlag(Decision.REVIEW, "test", 0.5)]

        result = safe_check(good_check)
        assert len(result) == 1
        assert result[0].reason == "test"

    def test_failing_check(self):
        """Test wrapper catches exceptions."""
        def bad_check() -> list:
            raise ValueError("Something went wrong")

        result = safe_check(bad_check)
        assert len(result) == 1
        assert result[0].decision == Decision.REVIEW
        assert "failed" in result[0].reason.lower()


# =============================================================================
# UNIT TESTS: Individual Checks
# =============================================================================

class TestNumericValidityCheck:
    """Tests for numeric validity check."""

    def test_valid_values(self, checks, sample_belief):
        """Test with valid numeric values."""
        flags = checks.check_numeric_validity(
            [sample_belief],
            {'sample_size': 100, 'p_value': 0.05}
        )
        assert len(flags) == 0

    def test_negative_sample_size(self, checks, sample_belief):
        """Test detection of negative sample size."""
        flags = checks.check_numeric_validity(
            [sample_belief],
            {'sample_size': -50}
        )
        assert len(flags) == 1
        assert flags[0].decision == Decision.BLOCK
        assert "sample size" in flags[0].reason.lower()

    def test_invalid_p_value(self, checks, sample_belief):
        """Test detection of p-value > 1."""
        flags = checks.check_numeric_validity(
            [sample_belief],
            {'p_value': 1.5}
        )
        assert len(flags) == 1
        assert flags[0].decision == Decision.BLOCK

    def test_credence_at_boundary(self, checks):
        """Test detection of credence at boundaries.

        Note: Credence class auto-clamps to (0.01, 0.99) in __post_init__,
        so we test by manually setting the value after construction.
        """
        belief = Belief(
            belief_id="test",
            content="Test",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.5, uncertainty=0.2),
        )
        # Manually set to boundary value to test the check
        belief.credence.value = 0.0  # Invalid: 0
        flags = checks.check_numeric_validity([belief], {})
        assert len(flags) >= 1
        assert any(f.decision == Decision.BLOCK for f in flags)


class TestCausalWarrantCheck:
    """Tests for causal warrant check."""

    def test_rct_with_causal_claim(self, checks):
        """RCT should support causal claims."""
        constraint = Constraint(
            constraint_id="c1",
            source_id="b1",
            target_id="b2",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.9,
            causal_direction=CausalDirection.FORWARD,
        )
        flags = checks.check_causal_warrant([constraint], "rct")
        assert len(flags) == 0

    def test_survey_with_causal_claim(self, checks):
        """Survey should not support strong causal claims."""
        constraint = Constraint(
            constraint_id="c1",
            source_id="b1",
            target_id="b2",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.8,  # High strength
            causal_direction=CausalDirection.FORWARD,  # Causal claim
        )
        flags = checks.check_causal_warrant([constraint], "cross_sectional")
        assert len(flags) >= 1
        assert flags[0].decision == Decision.REVIEW

    def test_correlational_claim_ok(self, checks):
        """Correlational claims should be fine from surveys."""
        constraint = Constraint(
            constraint_id="c1",
            source_id="b1",
            target_id="b2",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.8,
            causal_direction=CausalDirection.CORRELATIONAL,  # Not causal
        )
        flags = checks.check_causal_warrant([constraint], "survey")
        assert len(flags) == 0


class TestScopeOverreachCheck:
    """Tests for scope overreach check."""

    def test_appropriate_scope(self, checks):
        """Test when scope matches sample."""
        belief = Belief(
            belief_id="test",
            content="Test",
            level=EpistemicLevel.EMPIRICAL,
            scope=ScopeConditions(
                population="students",
                scope_specified=True
            ),
        )
        flags = checks.check_scope_overreach(
            [belief],
            "undergraduate psychology students"
        )
        assert len(flags) == 0

    def test_universal_from_students(self, checks):
        """Test overreach from student sample to universal."""
        belief = Belief(
            belief_id="test",
            content="Test",
            level=EpistemicLevel.EMPIRICAL,
            scope=ScopeConditions(
                population=None,  # Universal
                scope_specified=False
            ),
        )
        flags = checks.check_scope_overreach(
            [belief],
            "undergraduate students at Western university"
        )
        assert len(flags) >= 1
        assert flags[0].decision == Decision.REVIEW


class TestEffectSizePlausibility:
    """Tests for effect size plausibility check."""

    def test_reasonable_effect(self, checks):
        """Test with reasonable effect size."""
        flags = checks.check_effect_size_plausibility(
            {'effect_size': 0.5},
            "lab_experiment"
        )
        assert len(flags) == 0

    def test_implausible_effect(self, checks):
        """Test with implausibly large effect size."""
        flags = checks.check_effect_size_plausibility(
            {'effect_size': 2.5},
            "field_study"
        )
        assert len(flags) >= 1
        assert flags[0].decision == Decision.REVIEW

    def test_missing_effect_size(self, checks):
        """Test with no effect size (should not flag)."""
        flags = checks.check_effect_size_plausibility({}, "experiment")
        assert len(flags) == 0


# =============================================================================
# INTEGRATION TESTS: CredibilityTester
# =============================================================================

class TestCredibilityTester:
    """Integration tests for CredibilityTester."""

    def test_clean_article(self, tester, sample_belief, sample_constraint):
        """Test evaluation of clean article."""
        report = tester.evaluate(
            article_id="test_001",
            beliefs=[sample_belief],
            constraints=[sample_constraint],
            metadata={
                'sample_size': 100,
                'study_design': 'experiment',
                'sample_description': 'adults',
            }
        )
        assert report.is_clean or report.overall_decision == Decision.REVIEW

    def test_invalid_article(self, tester):
        """Test evaluation of article with obvious errors."""
        belief = Belief(
            belief_id="test",
            content="Test",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.5, uncertainty=0.2),
        )
        report = tester.evaluate(
            article_id="test_002",
            beliefs=[belief],
            constraints=[],
            metadata={'sample_size': -100}  # Invalid
        )
        assert not report.is_clean
        assert report.overall_decision == Decision.BLOCK

    def test_multiple_issues(self, tester):
        """Test article with multiple issues."""
        belief = Belief(
            belief_id="test",
            content="Test",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.5, uncertainty=0.2),
            scope=ScopeConditions(population=None, scope_specified=False),
        )
        constraint = Constraint(
            constraint_id="c1",
            source_id="test",
            target_id="other",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.9,
            causal_direction=CausalDirection.FORWARD,
        )

        report = tester.evaluate(
            article_id="test_003",
            beliefs=[belief],
            constraints=[constraint],
            metadata={
                'sample_size': 30,
                'study_design': 'survey',  # Survey with causal claim
                'sample_description': 'students',  # Universal scope from students
                'effect_size': 2.0,  # Large effect
            }
        )

        assert not report.is_clean
        assert len(report.flags) >= 2  # Multiple issues


class TestQuickCheck:
    """Tests for quick_check function."""

    def test_quick_check_pass(self):
        """Test quick check with valid data."""
        belief = Belief(
            belief_id="test",
            content="Test",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.6, uncertainty=0.2),
        )
        result = quick_check(
            [belief], [],
            {'sample_size': 100}
        )
        assert result is True

    def test_quick_check_fail(self):
        """Test quick check with invalid data."""
        belief = Belief(
            belief_id="test",
            content="Test",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.5, uncertainty=0.2),
        )
        result = quick_check(
            [belief], [],
            {'sample_size': -50}  # Invalid
        )
        assert result is False


# =============================================================================
# FAILURE STANDARD TESTS
# =============================================================================

class TestFailureStandard:
    """Tests against Failure Standard corpus."""

    def test_negative_sample_size_detected(self, tester):
        """Failure case: negative sample size must be blocked."""
        belief = Belief(
            belief_id="b_negative_n_1",
            content="Nature exposure reduces cortisol levels",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.65, uncertainty=0.2),
        )
        report = tester.evaluate(
            article_id="test_negative_n_001",
            beliefs=[belief],
            constraints=[],
            metadata={'sample_size': -50}
        )

        assert not report.is_clean
        assert report.overall_decision == Decision.BLOCK
        assert any("sample" in f.reason.lower() for f in report.flags)

    def test_causal_from_survey_flagged(self, tester):
        """Failure case: causal claim from survey should be reviewed."""
        belief = Belief(
            belief_id="b_causal_survey_1",
            content="Time spent in nature causes reduced stress levels",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.70, uncertainty=0.15),
        )
        constraint = Constraint(
            constraint_id="c_causal_survey_1",
            source_id="b_causal_survey_1",
            target_id="theory_nature_stress",
            constraint_type=ConstraintType.SUPPORTS,
            strength=0.7,
            causal_direction=CausalDirection.FORWARD,
        )

        report = tester.evaluate(
            article_id="test_causal_survey_001",
            beliefs=[belief],
            constraints=[constraint],
            metadata={
                'sample_size': 500,
                'study_design': 'cross_sectional',
            }
        )

        assert not report.is_clean
        assert any("causal" in f.reason.lower() for f in report.flags)

    def test_scope_overreach_flagged(self, tester):
        """Failure case: universal claim from students should be reviewed."""
        belief = Belief(
            belief_id="b_scope_overreach_1",
            content="Biophilic design elements improve cognitive performance",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.72, uncertainty=0.18),
            scope=ScopeConditions(population=None, scope_specified=False),
        )

        report = tester.evaluate(
            article_id="test_scope_overreach_001",
            beliefs=[belief],
            constraints=[],
            metadata={
                'sample_size': 48,
                'study_design': 'experiment',
                'sample_description': 'Psychology undergraduate students at a Western university',
            }
        )

        assert not report.is_clean
        assert any("scope" in f.reason.lower() for f in report.flags)


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_beliefs(self, tester):
        """Test with no beliefs."""
        report = tester.evaluate(
            article_id="empty_001",
            beliefs=[],
            constraints=[],
            metadata={}
        )
        # Should not crash, may or may not flag
        assert report.article_id == "empty_001"

    def test_empty_metadata(self, tester, sample_belief):
        """Test with no metadata."""
        report = tester.evaluate(
            article_id="no_meta_001",
            beliefs=[sample_belief],
            constraints=[],
            metadata=None
        )
        # Should not crash
        assert report.article_id == "no_meta_001"

    def test_missing_fields_handled(self, tester):
        """Test graceful handling of missing fields."""
        # Belief with minimal fields
        belief = Belief(
            belief_id="minimal",
            content="Minimal belief",
            level=EpistemicLevel.EMPIRICAL,
        )
        report = tester.evaluate(
            article_id="minimal_001",
            beliefs=[belief],
            constraints=[],
            metadata={}
        )
        # Should not crash
        assert report is not None


# =============================================================================
# SPRINT C TESTS: New Checks
# =============================================================================

class TestCausalCycleCheck:
    """Tests for causal cycle detection."""

    def test_no_cycle(self, checks):
        """Test with linear constraint chain (no cycle)."""
        constraints = [
            Constraint(
                constraint_id="c1",
                source_id="a",
                target_id="b",
                constraint_type=ConstraintType.EXPLAINS,
                causal_direction=CausalDirection.FORWARD,
            ),
            Constraint(
                constraint_id="c2",
                source_id="b",
                target_id="c",
                constraint_type=ConstraintType.EXPLAINS,
                causal_direction=CausalDirection.FORWARD,
            ),
        ]
        flags = checks.check_causal_cycles(constraints)
        assert len(flags) == 0

    def test_cycle_detected(self, checks):
        """Test that cycle is detected."""
        constraints = [
            Constraint(
                constraint_id="c1",
                source_id="a",
                target_id="b",
                constraint_type=ConstraintType.EXPLAINS,
                causal_direction=CausalDirection.FORWARD,
            ),
            Constraint(
                constraint_id="c2",
                source_id="b",
                target_id="a",  # Creates cycle: a → b → a
                constraint_type=ConstraintType.EXPLAINS,
                causal_direction=CausalDirection.FORWARD,
            ),
        ]
        flags = checks.check_causal_cycles(constraints)
        assert len(flags) >= 1
        assert flags[0].decision == Decision.REVIEW
        assert "cycle" in flags[0].reason.lower()


class TestStatisticalValidityCheck:
    """Tests for statistical validity checks."""

    def test_ci_not_spanning_zero(self, checks):
        """Test CI that doesn't span zero."""
        flags = checks.check_statistical_validity({
            'confidence_interval': [0.1, 0.5],
            'p_value': 0.01
        })
        assert len(flags) == 0

    def test_ci_spans_zero(self, checks):
        """Test CI that spans zero."""
        flags = checks.check_statistical_validity({
            'confidence_interval': [-0.1, 0.5],
            'p_value': 0.01  # Claimed significant despite CI spanning zero
        })
        assert len(flags) >= 1
        assert any("confidence interval" in f.reason.lower() for f in flags)

    def test_multiple_comparison_problem(self, checks):
        """Test multiple comparison without correction."""
        flags = checks.check_statistical_validity({
            'n_comparisons': 20,
            'n_significant': 1,  # Expected ~1 by chance
            'correction_applied': False
        })
        assert len(flags) >= 1
        assert any("comparison" in f.reason.lower() for f in flags)

    def test_multiple_comparison_with_correction(self, checks):
        """Test multiple comparison with correction (should pass)."""
        flags = checks.check_statistical_validity({
            'n_comparisons': 20,
            'n_significant': 3,
            'correction_applied': True  # Correction applied
        })
        assert len(flags) == 0


class TestCalibration:
    """Tests for calibration functions."""

    def test_calibration_with_data(self):
        """Test calibration with sample data."""
        from src.services.credibility_testing import calibrate_thresholds, CredibilityReport, CredibilityFlag
        from datetime import datetime, timezone

        # Create sample reports
        reports = []

        # True positives (flagged and actually problematic)
        for i in range(5):
            report = CredibilityReport(
                article_id=f"tp_{i}",
                timestamp=datetime.now(timezone.utc),
            )
            report.add_flag(CredibilityFlag(
                decision=Decision.REVIEW,
                reason="Test flag",
                confidence=0.7 + i * 0.05,
                field_name="test_type"
            ))
            reports.append((report, True))  # is_problem=True

        # True negatives (not flagged and not problematic)
        for i in range(5):
            report = CredibilityReport(
                article_id=f"tn_{i}",
                timestamp=datetime.now(timezone.utc),
            )
            reports.append((report, False))

        # False positives (flagged but not actually problematic)
        for i in range(2):
            report = CredibilityReport(
                article_id=f"fp_{i}",
                timestamp=datetime.now(timezone.utc),
            )
            report.add_flag(CredibilityFlag(
                decision=Decision.REVIEW,
                reason="False alarm",
                confidence=0.4 + i * 0.1,
                field_name="test_type"
            ))
            reports.append((report, False))

        # Run calibration
        results = calibrate_thresholds(reports, target_sensitivity=0.8)

        assert "test_type" in results
        assert results["test_type"].n_samples >= 5


class TestSprintCFailureStandard:
    """Tests for Sprint C failure cases."""

    def test_causal_cycle_case(self, tester):
        """Test causal cycle failure case."""
        belief1 = Belief(
            belief_id="b_nature_stress",
            content="Nature exposure reduces stress",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.70, uncertainty=0.15),
        )
        belief2 = Belief(
            belief_id="b_stress_nature",
            content="Lower stress increases nature-seeking",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.65, uncertainty=0.18),
        )

        # Constraints creating a cycle
        constraints = [
            Constraint(
                constraint_id="c1",
                source_id="b_nature_stress",
                target_id="b_stress_nature",
                constraint_type=ConstraintType.EXPLAINS,
                causal_direction=CausalDirection.FORWARD,
            ),
            Constraint(
                constraint_id="c2",
                source_id="b_stress_nature",
                target_id="b_nature_stress",  # Creates cycle
                constraint_type=ConstraintType.EXPLAINS,
                causal_direction=CausalDirection.FORWARD,
            ),
        ]

        report = tester.evaluate(
            article_id="test_cycle_001",
            beliefs=[belief1, belief2],
            constraints=constraints,
            metadata={'sample_size': 200, 'study_design': 'longitudinal'}
        )

        assert not report.is_clean
        assert any("cycle" in f.reason.lower() for f in report.flags)

    def test_ci_spans_zero_case(self, tester):
        """Test CI spanning zero failure case."""
        belief = Belief(
            belief_id="b_ci_zero",
            content="Nature reduces anxiety",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.68, uncertainty=0.15),
        )

        report = tester.evaluate(
            article_id="test_ci_001",
            beliefs=[belief],
            constraints=[],
            metadata={
                'sample_size': 80,
                'study_design': 'experiment',
                'confidence_interval': [-0.05, 0.75],
                'p_value': 0.06
            }
        )

        # Should flag CI spanning zero
        assert not report.is_clean
        assert any("confidence interval" in f.reason.lower() for f in report.flags)


# =============================================================================
# SPRINT D TESTS: Calibration Enhancements
# =============================================================================

class TestMissingMethodologyCheck:
    """Tests for missing methodology detection."""

    def test_missing_sample_size_empirical(self, checks):
        """Test detection of missing sample size for empirical study."""
        flags = checks.check_missing_methodology({
            'study_design': 'experiment',
            'sample_description': '',  # No description either
        })
        assert len(flags) >= 1
        assert any("sample" in f.reason.lower() for f in flags)

    def test_missing_sample_size_theory_ok(self, checks):
        """Test that theory papers don't need sample size."""
        flags = checks.check_missing_methodology({
            'study_design': 'theory',
            'sample_description': '',
        })
        # Theory papers shouldn't be flagged for missing sample info
        assert len(flags) == 0

    def test_complete_methodology(self, checks):
        """Test that complete methodology passes."""
        flags = checks.check_missing_methodology({
            'sample_size': 100,
            'study_design': 'experiment',
            'sample_description': 'Adults aged 18-65',
        })
        assert len(flags) == 0


class TestSubgroupSampleSizeCheck:
    """Tests for subgroup sample size detection."""

    def test_adequate_subgroup_size(self, checks, sample_belief):
        """Test that adequate subgroup size passes."""
        flags = checks.check_subgroup_sample_size(
            [sample_belief],
            {'subgroup_sizes': {'adults': 100}}
        )
        assert len(flags) == 0

    def test_small_subgroup_detected(self, checks):
        """Test detection of small subgroup sample size."""
        belief = Belief(
            belief_id="test_subgroup",
            content="Elderly benefit from nature",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.7, uncertainty=0.15),
            scope=ScopeConditions(population="elderly", scope_specified=True),
        )
        flags = checks.check_subgroup_sample_size(
            [belief],
            {'subgroup_sizes': {'elderly': 25}}  # Below threshold
        )
        assert len(flags) >= 1
        assert any("subgroup" in f.reason.lower() for f in flags)

    def test_no_subgroup_info(self, checks, sample_belief):
        """Test handling when no subgroup info provided."""
        flags = checks.check_subgroup_sample_size([sample_belief], {})
        assert len(flags) == 0  # No subgroup info = no flags


class TestRawCredenceDetection:
    """Tests for raw credence value detection (bypassing auto-clamping)."""

    def test_raw_credence_zero_detected(self, checks):
        """Test detection of credence=0 via raw_credences."""
        flags = checks.check_numeric_validity(
            [],  # No beliefs, using raw_credences
            {'raw_credences': [0.0, 0.5]}
        )
        assert len(flags) >= 1
        assert any("0.0" in f.observed or "0" in f.reason for f in flags)

    def test_raw_credence_one_detected(self, checks):
        """Test detection of credence=1 via raw_credences."""
        flags = checks.check_numeric_validity(
            [],
            {'raw_credences': [0.5, 1.0]}
        )
        assert len(flags) >= 1
        assert any("1.0" in f.observed or "1" in f.reason for f in flags)

    def test_valid_raw_credences(self, checks):
        """Test that valid raw credences pass."""
        flags = checks.check_numeric_validity(
            [],
            {'raw_credences': [0.3, 0.5, 0.7]}
        )
        assert len(flags) == 0


class TestSprintDFailureStandard:
    """Tests for Sprint D failure standard cases."""

    def test_subgroup_n_case(self, tester):
        """Test subgroup N failure case from failure standard."""
        belief = Belief(
            belief_id="b_subgroup",
            content="Nature exposure reduces stress in elderly adults",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.72, uncertainty=0.18),
            scope=ScopeConditions(population="elderly", scope_specified=True),
        )

        report = tester.evaluate(
            article_id="test_subgroup_n_001",
            beliefs=[belief],
            constraints=[],
            metadata={
                'sample_size': 200,  # Total N looks adequate
                'study_design': 'experiment',
                'sample_description': 'Adults aged 18-65',
                'subgroup_sizes': {'elderly': 45},  # But critical subgroup is small
            }
        )

        # Should flag small subgroup
        assert not report.is_clean
        assert any("subgroup" in f.reason.lower() for f in report.flags)

    def test_multiple_comparison_case(self, tester):
        """Test multiple comparison failure case."""
        belief = Belief(
            belief_id="b_multiple",
            content="Nature reduces anxiety (one of 15 outcomes)",
            level=EpistemicLevel.EMPIRICAL,
            credence=Credence(value=0.65, uncertainty=0.2),
        )

        report = tester.evaluate(
            article_id="test_multiple_001",
            beliefs=[belief],
            constraints=[],
            metadata={
                'sample_size': 120,
                'study_design': 'experiment',
                'n_comparisons': 15,
                'n_significant': 2,  # About expected by chance
                'correction_applied': False,
            }
        )

        # Should flag multiple comparison concern
        assert not report.is_clean
        assert any("comparison" in f.reason.lower() for f in report.flags)
