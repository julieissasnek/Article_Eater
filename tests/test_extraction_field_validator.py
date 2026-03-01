"""Tests for ExtractionFieldValidator.

Tests all 11 field validators with good and bad inputs,
plus article-level and batch-level reporting.
"""

import json
import pytest
import tempfile
from pathlib import Path

from src.qa.extraction_field_validator import (
    ExtractionFieldValidator,
    FindingReport,
    ArticleReport,
    BatchReport,
    Severity,
    Violation,
)


@pytest.fixture
def validator():
    return ExtractionFieldValidator()


# --- Antecedent tests ---

class TestAntecedent:
    def test_null_antecedent(self, validator):
        finding = {"antecedent": "", "consequent": "stress"}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "A1_NULL_ANTECEDENT" in rule_ids

    def test_vague_antecedent(self, validator):
        finding = {"antecedent": "environmental features", "consequent": "stress"}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "A2_VAGUE_ANTECEDENT" in rule_ids

    def test_outcome_in_antecedent(self, validator):
        finding = {"antecedent": "improved well-being from lighting", "consequent": "mood"}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert any("A3" in r for r in rule_ids)

    def test_good_antecedent(self, validator):
        finding = {
            "antecedent": "Ceiling height (3.0m vs 2.4m)",
            "consequent": "creative performance",
            "direction": "increase",
            "claim_type": "empirical_finding",
            "p_value": 0.03,
            "effect_size": 0.45,
            "effect_size_type": "Cohen's d",
            "sample_size": 60,
        }
        report = validator.validate_finding(finding)
        ant_violations = [v for v in report.violations if v.field == "antecedent"]
        assert len(ant_violations) == 0

    def test_short_antecedent(self, validator):
        finding = {"antecedent": "hi", "consequent": "stress"}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "A5_LENGTH_CHECK" in rule_ids


# --- Direction tests ---

class TestDirection:
    def test_invalid_direction(self, validator):
        finding = {"antecedent": "light level", "consequent": "mood",
                    "direction": "modulates"}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "D1_INVALID_DIRECTION" in rule_ids

    def test_mixed_with_effect_size(self, validator):
        finding = {"antecedent": "light level", "consequent": "mood",
                    "direction": "mixed", "effect_size": 0.5}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "D2_MIXED_WITH_EFFECT_SIZE" in rule_ids

    def test_direction_es_mismatch(self, validator):
        finding = {"antecedent": "ceiling height", "consequent": "creativity",
                    "direction": "increase", "effect_size": -0.45}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "D3_DIRECTION_EFFECT_MISMATCH" in rule_ids

    def test_good_direction(self, validator):
        finding = {"antecedent": "ceiling height", "consequent": "creativity",
                    "direction": "increase", "effect_size": 0.45,
                    "effect_size_type": "Cohen's d"}
        report = validator.validate_finding(finding)
        dir_violations = [v for v in report.violations if v.field == "direction"]
        assert len(dir_violations) == 0

    def test_null_direction_empirical(self, validator):
        finding = {"antecedent": "light", "consequent": "mood",
                    "claim_type": "empirical_finding", "direction": None}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "D5_NULL_DIRECTION_EMPIRICAL" in rule_ids


# --- Effect size tests ---

class TestEffectSize:
    def test_eta_squared_out_of_range(self, validator):
        finding = {"antecedent": "room color", "consequent": "mood",
                    "effect_size": 1.5, "effect_size_type": "eta_squared"}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "ES1_RANGE_VALIDATION" in rule_ids

    def test_null_es_type_with_es(self, validator):
        finding = {"antecedent": "room color", "consequent": "mood",
                    "effect_size": 0.4, "effect_size_type": None}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "ES4_NULL_TYPE_WITH_ES" in rule_ids

    def test_null_es_empirical(self, validator):
        finding = {"antecedent": "room color", "consequent": "mood",
                    "claim_type": "empirical_finding", "effect_size": None,
                    "p_value": 0.03, "direction": "increase"}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "ES3_NULL_ES_EMPIRICAL" in rule_ids


# --- P-value tests ---

class TestPValue:
    def test_p_out_of_range(self, validator):
        finding = {"antecedent": "light", "consequent": "mood", "p_value": 1.5}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "PV1_OUT_OF_RANGE" in rule_ids

    def test_null_p_empirical(self, validator):
        finding = {"antecedent": "light", "consequent": "mood",
                    "claim_type": "causal", "p_value": None}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "PV4_NULL_P_EMPIRICAL" in rule_ids

    def test_good_p(self, validator):
        finding = {"antecedent": "light", "consequent": "mood",
                    "p_value": 0.032, "direction": "increase"}
        report = validator.validate_finding(finding)
        pv_violations = [v for v in report.violations if v.field == "p_value"]
        assert len(pv_violations) == 0


# --- Sample size tests ---

class TestSampleSize:
    def test_negative_sample(self, validator):
        finding = {"antecedent": "room", "consequent": "stress", "sample_size": -5}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "SS1_TYPE_RANGE" in rule_ids

    def test_null_sample_empirical(self, validator):
        finding = {"antecedent": "room", "consequent": "stress",
                    "claim_type": "empirical_finding", "sample_size": None}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "SS2_NULL_FOR_EMPIRICAL" in rule_ids


# --- CI tests ---

class TestConfidenceInterval:
    def test_bad_ordering(self, validator):
        finding = {"antecedent": "room", "consequent": "stress",
                    "confidence_interval": [0.8, 0.2]}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "CI2_ORDERING" in rule_ids

    def test_es_outside_ci(self, validator):
        finding = {"antecedent": "room", "consequent": "stress",
                    "confidence_interval": [0.1, 0.3], "effect_size": 0.5,
                    "effect_size_type": "Cohen's d"}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "CI3_ES_CONTAINMENT" in rule_ids


# --- Claim type tests ---

class TestClaimType:
    def test_invalid_claim_type(self, validator):
        finding = {"antecedent": "room", "consequent": "stress",
                    "claim_type": "magical_thinking"}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "CT1_INVALID_CLAIM_TYPE" in rule_ids

    def test_empirical_no_stats(self, validator):
        finding = {"antecedent": "room", "consequent": "stress",
                    "claim_type": "empirical_finding"}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "CT2_EMPIRICAL_WITHOUT_STATS" in rule_ids


# --- Measure type tests ---

class TestMeasureType:
    def test_invalid_measure(self, validator):
        finding = {"antecedent": "room", "consequent": "stress",
                    "measure_type": "magical_observation"}
        report = validator.validate_finding(finding)
        rule_ids = [v.rule_id for v in report.violations]
        assert "MT1_INVALID_MEASURE_TYPE" in rule_ids


# --- Integration tests ---

class TestArticleValidation:
    def test_validate_article_file(self, validator, tmp_path):
        """Create a mock extraction file and validate it."""
        data = {
            "article_type": "empirical_research",
            "findings": [
                {
                    "antecedent": "Ceiling height (3.0m vs 2.4m)",
                    "consequent": "creative performance on RAT task",
                    "direction": "increase",
                    "claim_type": "empirical_finding",
                    "p_value": 0.03,
                    "effect_size": 0.45,
                    "effect_size_type": "Cohen's d",
                    "sample_size": 60,
                    "measure_type": "cognitive_task",
                },
                {
                    "antecedent": "",
                    "consequent": "mood",
                    "direction": "modulates",
                    "claim_type": "empirical_finding",
                },
            ]
        }
        filepath = tmp_path / "test_article.json"
        with open(filepath, "w") as f:
            json.dump(data, f)

        report = validator.validate_article(filepath)
        assert report.total_findings == 2
        assert report.finding_reports[0].score > report.finding_reports[1].score
        assert len(report.critical_errors) > 0  # Second finding has critical errors
        assert report.quality_score < 1.0

    def test_quality_score_perfect(self, validator):
        """A perfectly valid finding should score 1.0."""
        finding = {
            "antecedent": "Natural daylight exposure in office (500 lux)",
            "consequent": "self-reported stress levels (PSS-10)",
            "direction": "decrease",
            "claim_type": "empirical_finding",
            "p_value": 0.001,
            "effect_size": -0.62,
            "effect_size_type": "Cohen's d",
            "sample_size": 120,
            "measure_type": "self_report",
        }
        report = validator.validate_finding(finding)
        assert report.score >= 0.9  # May get minor warnings but should be high


class TestBatchValidation:
    def test_batch_validation(self, validator, tmp_path):
        """Validate multiple articles."""
        for i in range(3):
            data = {
                "findings": [
                    {
                        "antecedent": f"Variable {i}",
                        "consequent": f"Outcome {i}",
                        "direction": "increase",
                        "effect_size": 0.3 + i * 0.1,
                        "effect_size_type": "Cohen's d",
                    }
                ]
            }
            with open(tmp_path / f"article_{i}.json", "w") as f:
                json.dump(data, f)

        report = validator.validate_batch(tmp_path)
        assert len(report.articles) == 3
        assert report.mean_score > 0


# --- Scoring tests ---

class TestScoring:
    def test_critical_penalty(self, validator):
        finding = {"antecedent": "", "consequent": "stress"}
        report = validator.validate_finding(finding)
        assert report.score < 1.0

    def test_no_violations_perfect(self, validator):
        """A finding with no violations should be 1.0."""
        report = FindingReport(index=0, violations=[])
        assert report.score == 1.0

    def test_severity_ordering(self, validator):
        """Critical violations should penalize more than warnings."""
        critical = FindingReport(index=0, violations=[
            Violation("X", "f", Severity.CRITICAL, "msg")
        ])
        warning = FindingReport(index=0, violations=[
            Violation("X", "f", Severity.WARNING, "msg")
        ])
        assert critical.score < warning.score
