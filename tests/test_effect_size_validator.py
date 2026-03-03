"""
Tests for Effect Size Validator — src/qa/effect_size_validator.py
==================================================================

Comprehensive tests for the EffectSizeValidator class, covering:
- Valid effect sizes for each measure type
- Outlier detection
- P-value misplacement detection
- Non-numeric value handling
- Batch validation
- Edge cases and boundary conditions

Date: 2026-03-02
"""

import pytest
from pathlib import Path
import json
import tempfile

from src.qa.effect_size_validator import (
    EffectSizeValidator,
    ValidationResult,
    ProblemType,
    MeasureType,
    BatchValidationReport,
)


# ═══════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture
def validator():
    """Provide a fresh EffectSizeValidator instance."""
    return EffectSizeValidator()


# ═══════════════════════════════════════════════════════════════════
# Tests: Valid Effect Sizes
# ═══════════════════════════════════════════════════════════════════

class TestValidEffectSizes:
    """Test cases for valid effect size values."""

    def test_cohens_d_valid(self, validator):
        """Cohen's d values in typical range should be valid."""
        for value in [-2.0, -0.8, 0, 0.5, 1.5, 2.0]:
            result = validator.validate_effect_size(value, "Cohen's d")
            assert result.is_valid, f"Cohen's d={value} should be valid"
            assert result.problem_type == ProblemType.VALID

    def test_cohens_d_boundary(self, validator):
        """Cohen's d at boundaries should be valid."""
        for value in [-4, 4]:
            result = validator.validate_effect_size(value, "Cohen's d")
            assert result.is_valid

    def test_pearsons_r_valid(self, validator):
        """Pearson's r values in [-1, 1] should be valid."""
        for value in [-1, -0.5, 0, 0.5, 1]:
            result = validator.validate_effect_size(value, "Pearson's r")
            assert result.is_valid

    def test_odds_ratio_valid(self, validator):
        """Odds ratio values > 0 should be valid."""
        for value in [0.5, 1, 2, 5, 10, 50]:
            result = validator.validate_effect_size(value, "Odds ratio")
            assert result.is_valid

    def test_eta_squared_valid(self, validator):
        """Eta squared in [0, 1] should be valid."""
        for value in [0, 0.1, 0.5, 0.99, 1]:
            result = validator.validate_effect_size(value, "Eta squared")
            assert result.is_valid

    def test_r_squared_valid(self, validator):
        """R² in [0, 1] should be valid."""
        for value in [0, 0.25, 0.5, 0.75, 1]:
            result = validator.validate_effect_size(value, "R²")
            assert result.is_valid

    def test_percent_valid(self, validator):
        """Percentage in [-100, 100] should be valid."""
        for value in [-100, -50, 0, 50, 100]:
            result = validator.validate_effect_size(value, "Percent")
            assert result.is_valid

    def test_hedges_g_valid(self, validator):
        """Hedges' g like Cohen's d should be valid."""
        for value in [-2, 0, 0.7, 2]:
            result = validator.validate_effect_size(value, "Hedges' g")
            assert result.is_valid

    def test_null_value_valid(self, validator):
        """Null/None values should be acceptable."""
        result = validator.validate_effect_size(None, "Cohen's d")
        assert result.is_valid
        assert result.problem_type == ProblemType.NULL_VALUE


# ═══════════════════════════════════════════════════════════════════
# Tests: Out-of-Range Detection
# ═══════════════════════════════════════════════════════════════════

class TestOutOfRange:
    """Test detection of values outside valid ranges."""

    def test_pearsons_r_over_1(self, validator):
        """Pearson's r > 1 should be invalid."""
        result = validator.validate_effect_size(1.5, "Pearson's r")
        assert not result.is_valid
        assert result.problem_type == ProblemType.OUT_OF_RANGE

    def test_pearsons_r_under_minus_1(self, validator):
        """Pearson's r < -1 should be invalid."""
        result = validator.validate_effect_size(-1.5, "Pearson's r")
        assert not result.is_valid
        assert result.problem_type == ProblemType.OUT_OF_RANGE

    def test_eta_squared_over_1(self, validator):
        """Eta squared > 1 should be invalid."""
        result = validator.validate_effect_size(1.5, "Eta squared")
        assert not result.is_valid
        assert result.problem_type == ProblemType.OUT_OF_RANGE

    def test_r_squared_negative(self, validator):
        """R² < 0 should be invalid."""
        result = validator.validate_effect_size(-0.1, "R²")
        assert not result.is_valid
        assert result.problem_type == ProblemType.NEGATIVE_INVALID

    def test_odds_ratio_zero(self, validator):
        """Odds ratio = 0 should be invalid (must be > 0)."""
        result = validator.validate_effect_size(0, "Odds ratio")
        assert not result.is_valid

    def test_odds_ratio_negative(self, validator):
        """Odds ratio < 0 should be invalid."""
        result = validator.validate_effect_size(-1, "Odds ratio")
        assert not result.is_valid
        assert result.problem_type == ProblemType.NEGATIVE_INVALID


# ═══════════════════════════════════════════════════════════════════
# Tests: Outlier Detection
# ═══════════════════════════════════════════════════════════════════

class TestOutlierDetection:
    """Test detection of extreme outliers."""

    def test_cohens_d_extreme_positive(self, validator):
        """Cohen's d >> 5 should be flagged (beyond outlier threshold)."""
        result = validator.validate_effect_size(10, "Cohen's d")
        assert not result.is_valid
        # Could be OUT_OF_RANGE or OUTLIER depending on threshold
        assert result.problem_type in (ProblemType.OUTLIER, ProblemType.OUT_OF_RANGE)

    def test_cohens_d_extreme_negative(self, validator):
        """Cohen's d << -5 should be flagged (beyond outlier threshold)."""
        result = validator.validate_effect_size(-10, "Cohen's d")
        assert not result.is_valid
        # Could be OUT_OF_RANGE or OUTLIER depending on threshold
        assert result.problem_type in (ProblemType.OUTLIER, ProblemType.OUT_OF_RANGE)

    def test_odds_ratio_extreme(self, validator):
        """Odds ratio > 100 should be flagged as outlier."""
        result = validator.validate_effect_size(200, "Odds ratio")
        assert not result.is_valid
        assert result.problem_type == ProblemType.OUTLIER

    def test_odds_ratio_very_small(self, validator):
        """Odds ratio << 0.01 should be flagged."""
        result = validator.validate_effect_size(0.0001, "Odds ratio")
        # Very small values might be detected as p-values
        assert not result.is_valid

    def test_extreme_value_untyped(self, validator):
        """Extremely large values should be flagged even without type."""
        result = validator.validate_effect_size(1e10, None)
        assert not result.is_valid
        assert result.problem_type == ProblemType.OUTLIER

    def test_360_billion_outlier(self, validator):
        """The example 360 billion should be detected as outlier."""
        result = validator.validate_effect_size(360e9, None)
        assert not result.is_valid
        assert result.problem_type == ProblemType.OUTLIER


# ═══════════════════════════════════════════════════════════════════
# Tests: P-Value Misplacement Detection
# ═══════════════════════════════════════════════════════════════════

class TestPValueMisplacement:
    """Test detection of p-values in effect_size field."""

    def test_p_value_005(self, validator):
        """p=0.05 should be detected as likely p-value."""
        result = validator.validate_effect_size(0.05, "Cohen's d")
        assert not result.is_valid
        assert result.problem_type == ProblemType.WRONG_FIELD

    def test_p_value_001(self, validator):
        """p=0.001 should be detected as likely p-value."""
        result = validator.validate_effect_size(0.001, "Cohen's d")
        assert not result.is_valid
        assert result.problem_type == ProblemType.WRONG_FIELD

    def test_p_value_0001(self, validator):
        """p=0.0001 should be detected as likely p-value."""
        result = validator.validate_effect_size(0.0001, "Pearson's r")
        assert not result.is_valid
        assert result.problem_type == ProblemType.WRONG_FIELD

    def test_typical_p_value_in_set(self, validator):
        """Typical p-values should all be detected."""
        for p_val in [0.01, 0.05, 0.001]:
            result = validator.validate_effect_size(p_val, "Cohen's d")
            assert not result.is_valid
            assert result.problem_type == ProblemType.WRONG_FIELD

    def test_correlation_with_p_value_range(self, validator):
        """Correlation-like measure with 0-0.5 value should flag p-value."""
        # 0.03 could be a p-value when declared as correlation
        result = validator.validate_effect_size(0.03, "Pearson's r")
        assert not result.is_valid
        assert result.problem_type == ProblemType.WRONG_FIELD


# ═══════════════════════════════════════════════════════════════════
# Tests: Non-Numeric Value Handling
# ═══════════════════════════════════════════════════════════════════

class TestNonNumeric:
    """Test handling of non-numeric values."""

    def test_string_value(self, validator):
        """String values that are numeric should coerce to float."""
        result = validator.validate_effect_size("0.5", "Cohen's d")
        # "0.5" can be coerced to float, so should be valid
        assert result.is_valid  # float("0.5") works

    def test_pure_text(self, validator):
        """Non-numeric text should be flagged."""
        result = validator.validate_effect_size("not_a_number", "Cohen's d")
        assert not result.is_valid
        assert result.problem_type == ProblemType.NON_NUMERIC

    def test_empty_string(self, validator):
        """Empty string should be non-numeric."""
        result = validator.validate_effect_size("", "Cohen's d")
        assert not result.is_valid
        assert result.problem_type == ProblemType.NON_NUMERIC

    def test_dict_value(self, validator):
        """Dict/object values should be non-numeric."""
        result = validator.validate_effect_size({"value": 0.5}, "Cohen's d")
        assert not result.is_valid
        assert result.problem_type == ProblemType.NON_NUMERIC

    def test_list_value(self, validator):
        """List values should be non-numeric."""
        result = validator.validate_effect_size([0.5], "Cohen's d")
        assert not result.is_valid
        assert result.problem_type == ProblemType.NON_NUMERIC


# ═══════════════════════════════════════════════════════════════════
# Tests: Negative Value Detection
# ═══════════════════════════════════════════════════════════════════

class TestNegativeValidity:
    """Test detection of invalid negative values."""

    def test_negative_odds_ratio(self, validator):
        """Odds ratio cannot be negative."""
        result = validator.validate_effect_size(-2, "Odds ratio")
        assert not result.is_valid
        assert result.problem_type == ProblemType.NEGATIVE_INVALID

    def test_negative_eta_squared(self, validator):
        """Eta squared cannot be negative."""
        result = validator.validate_effect_size(-0.1, "Eta squared")
        assert not result.is_valid
        assert result.problem_type == ProblemType.NEGATIVE_INVALID

    def test_negative_r_squared(self, validator):
        """R² cannot be negative."""
        result = validator.validate_effect_size(-0.5, "R²")
        assert not result.is_valid
        assert result.problem_type == ProblemType.NEGATIVE_INVALID

    def test_cohens_d_can_be_negative(self, validator):
        """Cohen's d can legitimately be negative."""
        result = validator.validate_effect_size(-0.8, "Cohen's d")
        assert result.is_valid


# ═══════════════════════════════════════════════════════════════════
# Tests: Measure Type Normalization
# ═══════════════════════════════════════════════════════════════════

class TestMeasureTypeNormalization:
    """Test normalization of measure type aliases."""

    def test_normalize_cohens_d_variations(self):
        """Cohen's d aliases should normalize."""
        aliases = ["cohens d", "cohen's d", "d"]
        for alias in aliases:
            normalized = MeasureType.normalize(alias)
            assert normalized == "Cohen's d"

    def test_normalize_pearsons_r_variations(self):
        """Pearson's r aliases should normalize."""
        aliases = ["pearsons r", "pearson's r", "r", "correlation"]
        for alias in aliases:
            normalized = MeasureType.normalize(alias)
            assert normalized == "Pearson's r"

    def test_normalize_r_squared_variations(self):
        """R² aliases should normalize."""
        aliases = ["r2", "r squared", "r-squared"]
        for alias in aliases:
            normalized = MeasureType.normalize(alias)
            assert normalized == "R²"

    def test_normalize_odds_ratio_variations(self):
        """Odds ratio aliases should normalize."""
        aliases = ["odds ratio", "or"]
        for alias in aliases:
            normalized = MeasureType.normalize(alias)
            assert normalized == "Odds ratio"

    def test_normalize_eta_squared_variations(self):
        """Eta squared aliases should normalize."""
        aliases = ["eta squared", "eta2", "η2"]
        for alias in aliases:
            normalized = MeasureType.normalize(alias)
            assert normalized == "Eta squared"


# ═══════════════════════════════════════════════════════════════════
# Tests: Batch Validation
# ═══════════════════════════════════════════════════════════════════

class TestBatchValidation:
    """Test batch validation across multiple findings."""

    def test_batch_all_valid(self, validator):
        """Batch with all valid values."""
        findings = [
            {"effect_size": 0.8, "effect_size_type": "Cohen's d"},
            {"effect_size": 1.2, "effect_size_type": "Cohen's d"},
            {"effect_size": 0.6, "effect_size_type": "Pearson's r"},
        ]
        report = validator.batch_validate(findings)
        assert report.total_validated == 3
        assert report.valid_count == 3
        assert report.problem_count == 0

    def test_batch_with_problems(self, validator):
        """Batch with mixed valid and invalid."""
        findings = [
            {"effect_size": 0.8, "effect_size_type": "Cohen's d"},  # valid
            {"effect_size": 2.0, "effect_size_type": "Pearson's r"},  # out of range
            {"effect_size": 0.05, "effect_size_type": "Cohen's d"},  # p-value
            {"effect_size": None, "effect_size_type": "Cohen's d"},  # null (valid)
        ]
        report = validator.batch_validate(findings)
        assert report.total_validated == 4
        assert report.valid_count == 2  # 0.8 and None
        assert report.problem_count == 2

    def test_batch_validity_rate(self, validator):
        """Test validity_rate property."""
        findings = [
            {"effect_size": 0.8, "effect_size_type": "Cohen's d"},
            {"effect_size": 2.0, "effect_size_type": "Pearson's r"},
        ]
        report = validator.batch_validate(findings)
        assert report.validity_rate == 0.5
        assert report.problem_rate == 0.5

    def test_batch_problems_by_type(self, validator):
        """Test problems_by_type classification."""
        findings = [
            {"effect_size": 1.5, "effect_size_type": "Pearson's r"},  # out_of_range
            {"effect_size": "text", "effect_size_type": "Cohen's d"},  # non_numeric
            {"effect_size": 0.05, "effect_size_type": "Cohen's d"},  # wrong_field
            {"effect_size": -1, "effect_size_type": "Odds ratio"},  # negative_invalid
        ]
        report = validator.batch_validate(findings)
        assert report.problems_by_type.get("out_of_range", 0) == 1
        assert report.problems_by_type.get("non_numeric", 0) == 1
        assert report.problems_by_type.get("wrong_field", 0) == 1
        assert report.problems_by_type.get("negative_invalid", 0) == 1

    def test_batch_summary(self, validator):
        """Test summary() method."""
        findings = [
            {"effect_size": 0.8, "effect_size_type": "Cohen's d"},
            {"effect_size": 2.0, "effect_size_type": "Pearson's r"},
        ]
        report = validator.batch_validate(findings)
        summary = report.summary()
        assert "Batch Validation Report" in summary
        assert "2" in summary
        assert "50.0%" in summary


# ═══════════════════════════════════════════════════════════════════
# Tests: Suggest Correction
# ═══════════════════════════════════════════════════════════════════

class TestSuggestCorrection:
    """Test correction suggestions."""

    def test_suggest_correction_out_of_range_high(self, validator):
        """Out-of-range high should suggest max."""
        suggestion = validator.suggest_correction(1.5, "Pearson's r")
        assert suggestion == 1.0  # max for correlation

    def test_suggest_correction_out_of_range_low(self, validator):
        """Out-of-range low should suggest min."""
        suggestion = validator.suggest_correction(-0.1, "Eta squared")
        assert suggestion == 0.0  # min for eta squared

    def test_suggest_correction_valid(self, validator):
        """Valid values should return None."""
        suggestion = validator.suggest_correction(0.5, "Cohen's d")
        assert suggestion is None

    def test_suggest_correction_non_numeric(self, validator):
        """Non-numeric should return None."""
        suggestion = validator.suggest_correction("text", "Cohen's d")
        assert suggestion is None

    def test_suggest_correction_null(self, validator):
        """Null should return None."""
        suggestion = validator.suggest_correction(None, "Cohen's d")
        assert suggestion is None


# ═══════════════════════════════════════════════════════════════════
# Tests: Edge Cases and Boundary Conditions
# ═══════════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_effect_size(self, validator):
        """Zero should be valid for most measures."""
        result = validator.validate_effect_size(0, "Cohen's d")
        assert result.is_valid

    def test_integer_coercion(self, validator):
        """Integer should coerce to float."""
        result = validator.validate_effect_size(1, "Pearson's r")
        assert result.is_valid

    def test_scientific_notation(self, validator):
        """Scientific notation should be parsed."""
        result = validator.validate_effect_size(1e-3, "Cohen's d")
        assert result.is_valid or result.problem_type == ProblemType.WRONG_FIELD

    def test_very_small_positive(self, validator):
        """Very small positive might be detected as p-value."""
        result = validator.validate_effect_size(0.0001, "Cohen's d")
        assert not result.is_valid
        assert result.problem_type == ProblemType.WRONG_FIELD

    def test_case_insensitive_measure_type(self, validator):
        """Measure type should be case-insensitive."""
        result1 = validator.validate_effect_size(0.5, "COHEN'S D")
        result2 = validator.validate_effect_size(0.5, "cohen's d")
        # Both should either both be valid or both be invalid
        assert result1.is_valid == result2.is_valid

    def test_whitespace_normalization(self, validator):
        """Whitespace should be normalized in measure type."""
        result1 = validator.validate_effect_size(0.5, "  Cohen's d  ")
        result2 = validator.validate_effect_size(0.5, "Cohen's d")
        assert result1.is_valid == result2.is_valid


# ═══════════════════════════════════════════════════════════════════
# Tests: File-Based Validation
# ═══════════════════════════════════════════════════════════════════

class TestFileValidation:
    """Test validation of extraction JSON files."""

    def test_validate_extraction_file_valid(self, validator):
        """Should validate effect sizes in an extraction file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            extraction = {
                "doi": "10.1234/example",
                "findings": [
                    {"effect_size": 0.8, "effect_size_type": "Cohen's d"},
                    {"effect_size": 1.2, "effect_size_type": "Cohen's d"},
                ]
            }
            json.dump(extraction, f)
            f.flush()
            filepath = Path(f.name)

        try:
            report = validator.validate_extraction_file(filepath)
            assert report.total_validated == 2
            assert report.valid_count == 2
        finally:
            filepath.unlink()

    def test_validate_extraction_file_with_problems(self, validator):
        """Should detect problems in extraction file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            extraction = {
                "doi": "10.1234/example",
                "findings": [
                    {"effect_size": 0.8, "effect_size_type": "Cohen's d"},  # valid
                    {"effect_size": 2.0, "effect_size_type": "Pearson's r"},  # out of range
                ]
            }
            json.dump(extraction, f)
            f.flush()
            filepath = Path(f.name)

        try:
            report = validator.validate_extraction_file(filepath)
            assert report.total_validated == 2
            assert report.valid_count == 1
            assert report.problem_count == 1
        finally:
            filepath.unlink()

    def test_validate_extraction_file_missing_findings(self, validator):
        """Should handle extraction with no findings."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            extraction = {
                "doi": "10.1234/example",
            }
            json.dump(extraction, f)
            f.flush()
            filepath = Path(f.name)

        try:
            report = validator.validate_extraction_file(filepath)
            assert report.total_validated == 0
        finally:
            filepath.unlink()


# ═══════════════════════════════════════════════════════════════════
# Tests: Classification Method
# ═══════════════════════════════════════════════════════════════════

class TestClassifyProblem:
    """Test the classify_problem method."""

    def test_classify_valid(self, validator):
        """Valid should return 'valid'."""
        classification = validator.classify_problem(0.8, "Cohen's d")
        assert classification == "valid"

    def test_classify_out_of_range(self, validator):
        """Out of range should return 'out_of_range'."""
        classification = validator.classify_problem(2.0, "Pearson's r")
        assert classification == "out_of_range"

    def test_classify_p_value(self, validator):
        """P-value should return 'wrong_field'."""
        classification = validator.classify_problem(0.05, "Cohen's d")
        assert classification == "wrong_field"

    def test_classify_non_numeric(self, validator):
        """Non-numeric should return 'non_numeric'."""
        classification = validator.classify_problem("text", "Cohen's d")
        assert classification == "non_numeric"


# ═══════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════

class TestIntegration:
    """Integration tests with real-world scenarios."""

    def test_real_world_mixed_data(self, validator):
        """Test with realistic mixed data."""
        findings = [
            {"effect_size": 0.52, "effect_size_type": "Cohen's d"},
            {"effect_size": 0.24, "effect_size_type": "partial_eta_squared"},
            {"effect_size": None, "effect_size_type": None},
            {"effect_size": 2.5, "effect_size_type": "Pearson's r"},  # out of range
            {"effect_size": 0.05, "effect_size_type": "Cohen's d"},  # p-value
            {"effect_size": 360e9, "effect_size_type": "Cohen's d"},  # outlier
            {"effect_size": "n.s.", "effect_size_type": "Cohen's d"},  # non-numeric
        ]
        report = validator.batch_validate(findings)
        assert report.total_validated == 7
        assert report.valid_count == 3  # 0.52, 0.24, None
        assert report.problem_count == 4

    def test_workflow_detect_and_fix(self, validator):
        """Test detect-and-fix workflow."""
        findings = [
            {"effect_size": 2.0, "effect_size_type": "Pearson's r"},
            {"effect_size": 1.5, "effect_size_type": "Eta squared"},
        ]

        # First, validate
        report = validator.batch_validate(findings)
        assert report.problem_count == 2

        # Then, suggest corrections
        for finding in findings:
            correction = validator.suggest_correction(
                finding["effect_size"],
                finding["effect_size_type"]
            )
            # Apply correction
            if correction is not None:
                finding["_original_effect_size"] = finding["effect_size"]
                finding["effect_size"] = correction

        # Verify corrections work
        report2 = validator.batch_validate(findings)
        assert report2.problem_count == 0
