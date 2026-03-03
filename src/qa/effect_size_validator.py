"""
Effect Size Validator — Data Quality QA Module
===============================================

Validates and detects problematic effect size values in extraction findings.
Identifies outliers, misplaced p-values, non-numeric values, and out-of-range
effect sizes for their respective measure types.

Usage:
    from src.qa.effect_size_validator import EffectSizeValidator, ValidationResult

    validator = EffectSizeValidator()
    result = validator.validate_effect_size(0.45, measure_type="Pearson's r")
    print(result.is_valid)  # True
    print(result.problem_type)  # "valid"

    # Batch validation
    batch_report = validator.batch_validate(findings_list)
    print(batch_report.total_validated)
    print(batch_report.problems_by_type)

Effect Size Types and Valid Ranges:
    - Cohen's d: typically [-4, 4], flag > |5|
    - Pearson's r: must be [-1, 1]
    - Odds ratio: must be > 0, flag > 100
    - Eta squared (η²): must be [0, 1]
    - R²: must be [0, 1]
    - Beta/regression coefficient: typically [-10, 10], flag > |50|
    - Hedges' g: similar to Cohen's d, [-4, 4]
    - Percent/percentage: must be [0, 100] or [-100, 100]
    - Raw mean difference: context-dependent, flag > |1000|

Date: 2026-03-02
Version: 1.0.0
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Dict, List

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Problem Classification Enum
# ═══════════════════════════════════════════════════════════════════

class ProblemType(str, Enum):
    """Classifies the type of effect size problem detected."""
    VALID = "valid"
    OUTLIER = "outlier"  # Extreme value for the measure type
    WRONG_FIELD = "wrong_field"  # Likely p-value in effect_size field
    NON_NUMERIC = "non_numeric"  # Text or non-float value
    NEGATIVE_INVALID = "negative_invalid"  # Negative when measure must be positive
    OUT_OF_RANGE = "out_of_range"  # Outside valid range for the measure
    NULL_VALUE = "null_value"  # None or empty


# ═══════════════════════════════════════════════════════════════════
# Measure Type Enum
# ═══════════════════════════════════════════════════════════════════

class MeasureType(str, Enum):
    """Standardized effect size measure types."""
    COHENS_D = "Cohen's d"
    HEDGES_G = "Hedges' g"
    PEARSONS_R = "Pearson's r"
    ODDS_RATIO = "Odds ratio"
    ETA_SQUARED = "Eta squared"
    PARTIAL_ETA_SQUARED = "Partial eta squared"
    R_SQUARED = "R²"
    REGRESSION_COEFFICIENT = "Regression coefficient"
    BETA = "Beta"
    PERCENT = "Percent"
    PERCENTAGE = "Percentage"
    PARTIAL_R = "Partial r"
    CRAMERS_V = "Cramér's V"
    MEAN_DIFFERENCE = "Mean difference"
    STANDARDIZED_MEAN_DIFFERENCE = "Standardized mean difference"

    # Aliases for common variations
    @classmethod
    def normalize(cls, value: str) -> Optional[str]:
        """Normalize common measure type aliases to standard names."""
        if not value:
            return None

        normalized = {
            "cohens d": "Cohen's d",
            "cohen's d": "Cohen's d",
            "d": "Cohen's d",
            "hedges g": "Hedges' g",
            "hedges' g": "Hedges' g",
            "g": "Hedges' g",
            "pearsons r": "Pearson's r",
            "pearson's r": "Pearson's r",
            "r": "Pearson's r",
            "correlation": "Pearson's r",
            "odds ratio": "Odds ratio",
            "or": "Odds ratio",
            "eta squared": "Eta squared",
            "eta2": "Eta squared",
            "η2": "Eta squared",
            "partial eta squared": "Partial eta squared",
            "partial eta2": "Partial eta squared",
            "r2": "R²",
            "r squared": "R²",
            "r-squared": "R²",
            "regression coefficient": "Regression coefficient",
            "beta": "Beta",
            "partial r": "Partial r",
            "cramer": "Cramér's V",
            "cramers v": "Cramér's V",
            "cramér's v": "Cramér's V",
            "percent": "Percent",
            "percentage": "Percentage",
            "%": "Percent",
            "mean difference": "Mean difference",
            "standardized mean difference": "Standardized mean difference",
            "smd": "Standardized mean difference",
        }

        norm_input = value.lower().strip()
        return normalized.get(norm_input, value)


# ═══════════════════════════════════════════════════════════════════
# Validation Result Data Classes
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ValidationResult:
    """Result of validating a single effect size value."""
    value: Any
    measure_type: Optional[str]
    is_valid: bool
    problem_type: ProblemType
    message: str
    suggested_correction: Optional[float] = None
    confidence: float = 1.0  # 0.0–1.0, how confident is the classification

    def __repr__(self) -> str:
        problem = f" ({self.problem_type.value})" if self.problem_type != ProblemType.VALID else ""
        return f"ValidationResult(value={self.value}, valid={self.is_valid}{problem})"


@dataclass
class BatchValidationReport:
    """Report for batch validation of multiple effect sizes."""
    total_validated: int
    valid_count: int
    problem_count: int
    problems_by_type: Dict[str, int] = field(default_factory=dict)
    invalid_values: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def validity_rate(self) -> float:
        """Fraction of valid effect sizes (0.0–1.0)."""
        if self.total_validated == 0:
            return 1.0
        return self.valid_count / self.total_validated

    @property
    def problem_rate(self) -> float:
        """Fraction of problematic effect sizes (0.0–1.0)."""
        return 1.0 - self.validity_rate

    def summary(self) -> str:
        """Human-readable summary of validation results."""
        lines = [
            f"Batch Validation Report",
            f"  Total validated: {self.total_validated}",
            f"  Valid: {self.valid_count} ({self.validity_rate*100:.1f}%)",
            f"  Problems: {self.problem_count} ({self.problem_rate*100:.1f}%)",
        ]

        if self.problems_by_type:
            lines.append("  Problems by type:")
            for ptype, count in sorted(self.problems_by_type.items(), key=lambda x: -x[1]):
                lines.append(f"    - {ptype}: {count}")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# Effect Size Validator Class
# ═══════════════════════════════════════════════════════════════════

class EffectSizeValidator:
    """
    Validates effect size values and detects problematic data.

    Detects:
    - Extreme outliers (e.g., 360 billion)
    - Out-of-range values (e.g., r > 1)
    - Negative values for non-negative measures
    - P-values mistakenly placed in effect_size field
    - Non-numeric values
    """

    # Valid ranges for each measure type (min, max)
    VALID_RANGES = {
        MeasureType.COHENS_D.value: (-4, 4),
        MeasureType.HEDGES_G.value: (-4, 4),
        MeasureType.PEARSONS_R.value: (-1, 1),
        MeasureType.PARTIAL_R.value: (-1, 1),
        MeasureType.ODDS_RATIO.value: (0, float('inf')),
        MeasureType.ETA_SQUARED.value: (0, 1),
        MeasureType.PARTIAL_ETA_SQUARED.value: (0, 1),
        MeasureType.R_SQUARED.value: (0, 1),
        MeasureType.CRAMERS_V.value: (0, 1),
        MeasureType.PERCENT.value: (-100, 100),
        MeasureType.PERCENTAGE.value: (-100, 100),
        MeasureType.REGRESSION_COEFFICIENT.value: (-10, 10),
        MeasureType.BETA.value: (-10, 10),
        MeasureType.MEAN_DIFFERENCE.value: (-1000, 1000),
        MeasureType.STANDARDIZED_MEAN_DIFFERENCE.value: (-4, 4),
    }

    # Outlier thresholds (beyond typical range, flag as outlier)
    OUTLIER_THRESHOLDS = {
        MeasureType.COHENS_D.value: (-5, 5),
        MeasureType.HEDGES_G.value: (-5, 5),
        MeasureType.ODDS_RATIO.value: (0.01, 100),
        MeasureType.REGRESSION_COEFFICIENT.value: (-50, 50),
        MeasureType.BETA.value: (-50, 50),
        MeasureType.MEAN_DIFFERENCE.value: (-1000, 1000),
    }

    # Typical p-values that might be misplaced
    # Note: 0.1–0.5 are NOT included, as they are legitimate effect sizes
    TYPICAL_P_VALUES = {
        0.05, 0.01, 0.001, 0.0001,
        0.005, 0.02, 0.03, 0.04,
    }

    def __init__(self):
        """Initialize the validator."""
        pass

    def validate_effect_size(
        self,
        value: Any,
        measure_type: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validate a single effect size value.

        Args:
            value: The effect size value to validate
            measure_type: The type of effect size (e.g., "Cohen's d")

        Returns:
            ValidationResult with validation status and problem type
        """

        # Handle null values
        if value is None:
            return ValidationResult(
                value=value,
                measure_type=measure_type,
                is_valid=True,  # Null is acceptable
                problem_type=ProblemType.NULL_VALUE,
                message="Effect size is null (acceptable if not available)",
            )

        # Try to coerce to float
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return ValidationResult(
                value=value,
                measure_type=measure_type,
                is_valid=False,
                problem_type=ProblemType.NON_NUMERIC,
                message=f"Effect size is not numeric: {value!r}",
            )

        # Detect p-value misplacement
        if num_value in self.TYPICAL_P_VALUES or (0 < num_value < 0.5):
            # Check if it looks like a p-value
            if self._looks_like_pvalue(num_value, measure_type):
                return ValidationResult(
                    value=value,
                    measure_type=measure_type,
                    is_valid=False,
                    problem_type=ProblemType.WRONG_FIELD,
                    message=f"Value {num_value} appears to be a p-value, not an effect size",
                    confidence=0.9,
                )

        # Normalize measure type
        normalized_type = MeasureType.normalize(measure_type) if measure_type else None

        # If no measure type provided, do basic checks
        if not normalized_type:
            return self._validate_untyped(num_value)

        # Type-specific validation
        return self._validate_typed(num_value, normalized_type)

    def _validate_untyped(self, value: float) -> ValidationResult:
        """Validate effect size when measure type is unknown."""

        # Check for extreme outliers
        if abs(value) > 1e6:
            return ValidationResult(
                value=value,
                measure_type=None,
                is_valid=False,
                problem_type=ProblemType.OUTLIER,
                message=f"Extreme outlier: {value}",
            )

        # Check for obviously invalid (e.g., extremely negative for a ratio)
        if value < -1000 or value > 1e9:
            return ValidationResult(
                value=value,
                measure_type=None,
                is_valid=False,
                problem_type=ProblemType.OUTLIER,
                message=f"Value {value} is suspiciously extreme",
            )

        return ValidationResult(
            value=value,
            measure_type=None,
            is_valid=True,
            problem_type=ProblemType.VALID,
            message="Value appears valid (untyped check)",
        )

    def _validate_typed(self, value: float, measure_type: str) -> ValidationResult:
        """Validate effect size when measure type is known."""

        # Check valid range
        if measure_type in self.VALID_RANGES:
            min_val, max_val = self.VALID_RANGES[measure_type]

            # Check for negative when not allowed
            if min_val >= 0 and value < 0:
                return ValidationResult(
                    value=value,
                    measure_type=measure_type,
                    is_valid=False,
                    problem_type=ProblemType.NEGATIVE_INVALID,
                    message=f"{measure_type} cannot be negative (got {value})",
                )

            # Check out of range
            if value < min_val or value > max_val:
                return ValidationResult(
                    value=value,
                    measure_type=measure_type,
                    is_valid=False,
                    problem_type=ProblemType.OUT_OF_RANGE,
                    message=f"{measure_type} must be in [{min_val}, {max_val}], got {value}",
                )

        # Check for outliers within valid range
        if measure_type in self.OUTLIER_THRESHOLDS:
            min_thresh, max_thresh = self.OUTLIER_THRESHOLDS[measure_type]
            if value < min_thresh or value > max_thresh:
                return ValidationResult(
                    value=value,
                    measure_type=measure_type,
                    is_valid=False,
                    problem_type=ProblemType.OUTLIER,
                    message=f"{measure_type} value {value} is unusual (typical range [{min_thresh}, {max_thresh}])",
                    confidence=0.7,
                )

        return ValidationResult(
            value=value,
            measure_type=measure_type,
            is_valid=True,
            problem_type=ProblemType.VALID,
            message=f"Valid {measure_type} effect size",
        )

    def _looks_like_pvalue(self, value: float, measure_type: Optional[str]) -> bool:
        """
        Heuristic to detect if a value is likely a p-value.

        Only flags obvious p-values, not legitimate small effect sizes.

        Args:
            value: The numeric value
            measure_type: The declared measure type

        Returns:
            True if the value looks like a p-value
        """

        # Typical p-value pattern (exact matches)
        if value in self.TYPICAL_P_VALUES:
            return True

        # Scientific notation p-values (smaller than typical)
        if value > 0 and value < 0.001:
            return True

        # For correlations, only flag if in exact p-value set
        # (legitimate small r values exist)
        if measure_type and "correlation" in measure_type.lower():
            if value in self.TYPICAL_P_VALUES:
                return True

        return False

    def classify_problem(self, value: Any, measure_type: Optional[str] = None) -> str:
        """
        Classify the problem type for a value.

        Returns:
            The problem type as a string (e.g., "valid", "outlier", "wrong_field")
        """
        result = self.validate_effect_size(value, measure_type)
        return result.problem_type.value

    def suggest_correction(
        self,
        value: Any,
        measure_type: Optional[str] = None,
    ) -> Optional[float]:
        """
        Suggest a correction for a problematic effect size.

        Args:
            value: The problematic value
            measure_type: The declared measure type

        Returns:
            A suggested corrected value, or None if no suggestion available
        """

        result = self.validate_effect_size(value, measure_type)

        # No suggestion for valid values or non-numeric
        if result.is_valid or result.problem_type == ProblemType.NON_NUMERIC:
            return None

        # Try to coerce to float
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return None

        normalized_type = MeasureType.normalize(measure_type) if measure_type else None

        # For out-of-range values, clamp to valid range
        if normalized_type and normalized_type in self.VALID_RANGES:
            min_val, max_val = self.VALID_RANGES[normalized_type]
            if num_value < min_val:
                return min_val if min_val > float('-inf') else None
            if num_value > max_val:
                return max_val if max_val < float('inf') else None

        return None

    def batch_validate(
        self,
        findings: List[Dict[str, Any]],
    ) -> BatchValidationReport:
        """
        Validate effect sizes across a batch of findings.

        Args:
            findings: List of finding dicts, each with optional 'effect_size'
                     and 'effect_size_type' keys

        Returns:
            BatchValidationReport summarizing validation results
        """

        report = BatchValidationReport(
            total_validated=0,
            valid_count=0,
            problem_count=0,
            problems_by_type={},
            invalid_values=[],
        )

        for finding in findings:
            effect_size = finding.get("effect_size")
            measure_type = finding.get("effect_size_type")

            result = self.validate_effect_size(effect_size, measure_type)
            report.total_validated += 1

            if result.is_valid:
                report.valid_count += 1
            else:
                report.problem_count += 1
                problem_type = result.problem_type.value
                report.problems_by_type[problem_type] = (
                    report.problems_by_type.get(problem_type, 0) + 1
                )

                invalid_entry = {
                    "effect_size": effect_size,
                    "effect_size_type": measure_type,
                    "problem_type": problem_type,
                    "message": result.message,
                }
                report.invalid_values.append(invalid_entry)

        return report

    def validate_extraction_file(
        self,
        filepath: Path,
    ) -> BatchValidationReport:
        """
        Validate all effect sizes in an extraction JSON file.

        Args:
            filepath: Path to extraction JSON file

        Returns:
            BatchValidationReport for the file
        """

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read {filepath}: {e}")
            return BatchValidationReport(0, 0, 0)

        findings = data.get("findings", [])
        return self.batch_validate(findings)
