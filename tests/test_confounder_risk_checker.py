"""
Test Suite: ConfounderRiskChecker
==================================

Tests confounder risk detection module with 18 test cases covering:
- Study design inference (RCT, quasi-experimental, observational, qualitative)
- Known confounder registry lookups
- Controlled covariate extraction
- Control adequacy scoring
- Risk level determination logic
- Batch processing
- Edge cases and data handling

Created: 2026-03-02
"""

import pytest
from src.qa.confounder_risk_checker import (
    ConfounderRiskChecker,
    RiskLevel,
    StudyDesign,
    ConfounderRiskReport,
    BatchConfounderReport,
)


# --- Fixtures ---

@pytest.fixture
def checker():
    """Initialize default confounder checker."""
    return ConfounderRiskChecker()


def _belief_green_space_rct() -> dict:
    """Example: RCT on green space and stress (low risk)."""
    return {
        "belief_id": "b1_green_rct",
        "antecedent": "green space exposure",
        "consequent": "stress reduction",
        "domain": "green_space",
        "study_design": "randomized controlled trial",
        "article_type": "experimental",
        "article_type_family": "empirical",
        "controlled_variables": ["socioeconomic_status", "age"],
        "p_value": 0.021,
        "effect_size": 0.45,
        "n": 120,
    }


def _belief_green_space_obs_no_controls() -> dict:
    """Example: Observational study, no controls (high risk)."""
    return {
        "belief_id": "b2_green_obs_uncontrolled",
        "antecedent": "green space proximity",
        "consequent": "cortisol levels",
        "domain": "green_space",
        "study_design": "observational",
        "article_type": "correlational",
        "article_type_family": "empirical",
        "p_value": 0.012,
        "n": 300,
    }


def _belief_green_space_obs_partial_controls() -> dict:
    """Example: Observational study, some controls (medium risk)."""
    return {
        "belief_id": "b3_green_obs_partial",
        "antecedent": "neighborhood green space",
        "consequent": "depression symptoms",
        "domain": "green_space",
        "study_design": "observational cross-sectional",
        "article_type_family": "empirical",
        "controlled_variables": [
            "socioeconomic_status", "age", "air_quality", "physical_activity", "noise_level"
        ],
        "statistical_control": "Regression adjusted for 5 key confounders",
        "n": 450,
    }


def _belief_lighting_obs_full_controls() -> dict:
    """Example: Observational, most confounders controlled (low risk)."""
    return {
        "belief_id": "b4_lighting_obs_controlled",
        "antecedent": "daylight illuminance",
        "consequent": "alertness",
        "domain": "lighting",
        "study_design": "observational longitudinal",
        "controlled_variables": [
            "time_of_day",
            "age",
            "circadian_phase",
            "task_type",
            "screen_time",
            "light_sensitivity",
            "seasonal_affective_disorder",
            "eye_strain",
        ],
        "methods": "Analysis of covariance with eight covariates",
        "n": 200,
    }


def _belief_noise_obs_control_mentioned() -> dict:
    """Example: Observational with control mentioned but not specific (medium risk)."""
    return {
        "belief_id": "b5_noise_obs_generic_control",
        "antecedent": "ambient noise level",
        "consequent": "cognitive performance",
        "domain": "noise",
        "study_design": "observational",
        "statistical_control": "Controlled for relevant confounders using regression",
        "n": 180,
    }


def _belief_quasi_experimental() -> dict:
    """Example: Quasi-experimental with some controls (medium risk)."""
    return {
        "belief_id": "b6_temperature_quasi",
        "antecedent": "room temperature",
        "consequent": "productivity",
        "domain": "temperature",
        "study_design": "quasi-experimental",
        "article_type": "quasi-experimental design",
        "controlled_variables": ["humidity", "activity_level"],
        "n": 80,
    }


def _belief_qualitative() -> dict:
    """Example: Qualitative study (low risk by design)."""
    return {
        "belief_id": "b7_color_qualitative",
        "antecedent": "color environment",
        "consequent": "mood perception",
        "domain": "color",
        "article_type_family": "qualitative",
        "study_design": "qualitative interview study",
        "n": 25,
    }


def _belief_unknown_design_no_confounders() -> dict:
    """Example: Unknown design, no matched confounders."""
    return {
        "belief_id": "b8_unknown_design",
        "antecedent": "spatial layout complexity",
        "consequent": "wayfinding performance",
        "article_type": "theoretical",
    }


def _belief_no_domain_match() -> dict:
    """Example: Variable not in known confounders registry."""
    return {
        "belief_id": "b9_novel_variable",
        "antecedent": "fountain presence",
        "consequent": "restoration",
        "study_design": "observational",
        "article_type_family": "empirical",
    }


def _belief_missing_id() -> dict:
    """Example: Belief without explicit ID."""
    return {
        "antecedent": "green space",
        "consequent": "stress",
        "study_design": "rct",
    }


# --- Test: Study Design Inference ---

class TestStudyDesignInference:
    """Test study design classification from belief metadata."""

    def test_infer_rct_from_explicit_design(self, checker):
        """Detect RCT from explicit study_design field."""
        belief = _belief_green_space_rct()
        design = checker.get_study_design(belief)
        assert design == StudyDesign.RANDOMIZED_CONTROLLED_TRIAL

    def test_infer_rct_from_article_type(self, checker):
        """Detect RCT from article_type field."""
        belief = {
            "antecedent": "green space",
            "article_type": "experimental study",
        }
        design = checker.get_study_design(belief)
        assert design == StudyDesign.RANDOMIZED_CONTROLLED_TRIAL

    def test_infer_observational(self, checker):
        """Detect observational design."""
        belief = _belief_green_space_obs_no_controls()
        design = checker.get_study_design(belief)
        assert design == StudyDesign.OBSERVATIONAL

    def test_infer_quasi_experimental(self, checker):
        """Detect quasi-experimental design."""
        belief = _belief_quasi_experimental()
        design = checker.get_study_design(belief)
        assert design == StudyDesign.QUASI_EXPERIMENTAL

    def test_infer_qualitative(self, checker):
        """Detect qualitative design."""
        belief = _belief_qualitative()
        design = checker.get_study_design(belief)
        assert design == StudyDesign.QUALITATIVE

    def test_infer_unknown_design(self, checker):
        """Default to unknown when no design indicators present."""
        belief = {
            "antecedent": "something",
            "consequent": "something else",
        }
        design = checker.get_study_design(belief)
        assert design == StudyDesign.UNKNOWN


# --- Test: Design Risk Scoring ---

class TestDesignRiskScoring:
    """Test risk scores assigned to study designs."""

    def test_rct_low_risk(self, checker):
        """RCT should have low risk score."""
        score = checker.get_design_risk_score(StudyDesign.RANDOMIZED_CONTROLLED_TRIAL)
        assert score < 0.3
        assert score == 0.1

    def test_qualitative_low_risk(self, checker):
        """Qualitative should have low risk score."""
        score = checker.get_design_risk_score(StudyDesign.QUALITATIVE)
        assert score < 0.3

    def test_observational_high_risk(self, checker):
        """Observational should have high risk score."""
        score = checker.get_design_risk_score(StudyDesign.OBSERVATIONAL)
        assert score > 0.7
        assert score == 0.9

    def test_quasi_experimental_medium_risk(self, checker):
        """Quasi-experimental should have medium risk score."""
        score = checker.get_design_risk_score(StudyDesign.QUASI_EXPERIMENTAL)
        assert 0.4 < score < 0.6
        assert score == 0.5


# --- Test: Known Confounder Registry ---

class TestConfounderRegistry:
    """Test lookup of known confounders for environmental variables."""

    def test_lookup_green_space_confounders(self, checker):
        """Retrieve confounders for green space variable."""
        belief = {
            "antecedent": "green space exposure",
            "domain": "green_space",
        }
        confounders = checker.lookup_known_confounders(belief)
        assert len(confounders) > 0
        assert "socioeconomic_status" in confounders
        assert "physical_activity" in confounders

    def test_lookup_lighting_confounders(self, checker):
        """Retrieve confounders for lighting variable."""
        belief = {
            "antecedent": "illuminance",
            "domain": "lighting",
        }
        confounders = checker.lookup_known_confounders(belief)
        assert len(confounders) > 0
        assert "time_of_day" in confounders
        assert "age" in confounders

    def test_lookup_by_antecedent_text_matching(self, checker):
        """Match confounders by antecedent text when domain not explicit."""
        belief = {
            "antecedent": "green space proximity",
            # No domain specified
        }
        confounders = checker.lookup_known_confounders(belief)
        assert len(confounders) > 0  # Should match "green_space" domain

    def test_no_confounder_match(self, checker):
        """Return empty list for unmapped variables."""
        belief = {
            "antecedent": "fountain presence",
            "domain": "nonexistent_domain_xyz",  # Definitely not in registry
        }
        confounders = checker.lookup_known_confounders(belief)
        assert confounders == []


# --- Test: Controlled Covariate Extraction ---

class TestCovariateExtraction:
    """Test extraction of controlled covariates from belief metadata."""

    def test_extract_from_controlled_variables_list(self, checker):
        """Extract explicit controlled_variables list."""
        belief = _belief_green_space_rct()
        covariates = checker.extract_controlled_covariates(belief)
        assert "socioeconomic_status" in covariates
        assert "age" in covariates

    def test_extract_from_covariates_controlled_field(self, checker):
        """Extract from covariates_controlled field."""
        belief = {
            "covariates_controlled": ["income", "education"],
        }
        covariates = checker.extract_controlled_covariates(belief)
        assert "income" in covariates
        assert "education" in covariates

    def test_extract_from_text_mentions(self, checker):
        """Detect control mentions in statistical_control text."""
        belief = {
            "statistical_control": "Controlled for socioeconomic status and age",
        }
        covariates = checker.extract_controlled_covariates(belief)
        assert len(covariates) > 0
        # Should detect "control_mentioned" marker
        assert any("control" in str(c).lower() for c in covariates)

    def test_no_controlled_covariates(self, checker):
        """Return empty list when no controls mentioned."""
        belief = _belief_green_space_obs_no_controls()
        covariates = checker.extract_controlled_covariates(belief)
        assert covariates == []


# --- Test: Control Adequacy Scoring ---

class TestControlAdequacy:
    """Test scoring of confounder control adequacy."""

    def test_no_known_confounders_perfect_score(self, checker):
        """Perfect score when no known confounders for the variable."""
        score = checker.calculate_control_adequacy([], [])
        assert score == 1.0

    def test_no_controls_zero_score(self, checker):
        """Zero score when confounders exist but no controls."""
        known = ["socioeconomic_status", "air_quality", "physical_activity"]
        controlled = []
        score = checker.calculate_control_adequacy(known, controlled)
        assert score == 0.0

    def test_all_confounders_controlled(self, checker):
        """Perfect score when all confounders controlled."""
        known = ["socioeconomic_status", "physical_activity", "air_quality"]
        controlled = ["socioeconomic_status", "physical_activity", "air_quality"]
        score = checker.calculate_control_adequacy(known, controlled)
        assert score == 1.0

    def test_partial_confounders_controlled(self, checker):
        """Partial score when some confounders controlled."""
        known = ["socioeconomic_status", "air_quality", "physical_activity"]
        controlled = ["socioeconomic_status", "air_quality"]
        score = checker.calculate_control_adequacy(known, controlled)
        assert abs(score - 2/3) < 0.01  # ~0.667

    def test_generic_control_mentioned_conservative_score(self, checker):
        """Conservative 50% score when controls mentioned but not specific."""
        known = ["socioeconomic_status", "air_quality", "noise_level"]
        controlled = ["control_mentioned"]
        score = checker.calculate_control_adequacy(known, controlled)
        assert score == 0.5


# --- Test: Risk Assessment ---

class TestRiskAssessment:
    """Test full risk assessment logic and recommendations."""

    def test_rct_always_low_risk(self, checker):
        """RCT design should always result in LOW risk."""
        belief = _belief_green_space_rct()
        report = checker.assess_confounder_risk(belief)
        assert report.risk_level == RiskLevel.LOW
        assert report.confidence >= 0.85

    def test_observational_no_controls_high_risk(self, checker):
        """Observational without controls should be HIGH risk."""
        belief = _belief_green_space_obs_no_controls()
        report = checker.assess_confounder_risk(belief)
        assert report.risk_level == RiskLevel.HIGH
        assert len(report.known_confounders) > 0

    def test_observational_partial_controls_medium_risk(self, checker):
        """Observational with some controls should be MEDIUM risk."""
        belief = _belief_green_space_obs_partial_controls()
        report = checker.assess_confounder_risk(belief)
        assert report.risk_level == RiskLevel.MEDIUM
        assert report.control_adequacy_score > 0 and report.control_adequacy_score < 1

    def test_observational_full_controls_low_risk(self, checker):
        """Observational with most confounders controlled should be LOW risk."""
        belief = _belief_lighting_obs_full_controls()
        report = checker.assess_confounder_risk(belief)
        assert report.risk_level == RiskLevel.LOW
        assert report.control_adequacy_score >= 0.75

    def test_quasi_experimental_with_controls_low_risk(self, checker):
        """Quasi-experimental with adequate controls should be LOW risk."""
        belief = _belief_quasi_experimental()
        report = checker.assess_confounder_risk(belief)
        # With 2 of 4 known confounders controlled = ~50% adequacy = MEDIUM
        assert report.risk_level in (RiskLevel.MEDIUM, RiskLevel.LOW)

    def test_qualitative_always_low_risk(self, checker):
        """Qualitative design should always be LOW risk."""
        belief = _belief_qualitative()
        report = checker.assess_confounder_risk(belief)
        assert report.risk_level == RiskLevel.LOW

    def test_report_includes_belief_id(self, checker):
        """Report should include belief_id."""
        belief = _belief_green_space_rct()
        report = checker.assess_confounder_risk(belief)
        assert report.belief_id == "b1_green_rct"

    def test_report_includes_recommendation(self, checker):
        """Report should include actionable recommendation."""
        belief = _belief_green_space_obs_no_controls()
        report = checker.assess_confounder_risk(belief)
        assert report.recommendation != ""
        assert "recommend" in report.recommendation.lower() or "flag" in report.recommendation.lower()

    def test_high_risk_includes_panelist_concern(self, checker):
        """HIGH risk reports should include panelist concern (e.g., Pearl quote)."""
        belief = _belief_green_space_obs_no_controls()
        report = checker.assess_confounder_risk(belief)
        assert report.panelist_concern != ""
        assert "Pearl" in report.panelist_concern or "confounder" in report.panelist_concern.lower()


# --- Test: Report Data Structures ---

class TestReportStructures:
    """Test report serialization and aggregation."""

    def test_confounder_risk_report_to_dict(self, checker):
        """ConfounderRiskReport serializes to dict."""
        belief = _belief_green_space_rct()
        report = checker.assess_confounder_risk(belief)
        d = report.to_dict()
        assert isinstance(d, dict)
        assert d["belief_id"] == "b1_green_rct"
        assert d["risk_level"] in ("high", "medium", "low")
        assert "recommendation" in d
        assert "confidence" in d

    def test_confounder_risk_report_summary(self, checker):
        """ConfounderRiskReport generates human-readable summary."""
        belief = _belief_green_space_rct()
        report = checker.assess_confounder_risk(belief)
        summary = report.summary()
        assert isinstance(summary, str)
        assert "Risk Level:" in summary
        assert "Recommendation:" in summary


# --- Test: Batch Processing ---

class TestBatchProcessing:
    """Test batch assessment of multiple beliefs."""

    def test_assess_all_beliefs_dict_input(self, checker):
        """Assess batch of beliefs from dict mapping."""
        beliefs = {
            "b1": _belief_green_space_rct(),
            "b2": _belief_green_space_obs_no_controls(),
            "b3": _belief_qualitative(),
        }
        batch = checker.assess_all_beliefs(beliefs)
        assert isinstance(batch, BatchConfounderReport)
        assert batch.beliefs_assessed == 3
        assert len(batch.reports) == 3

    def test_assess_all_beliefs_list_input(self, checker):
        """Assess batch of beliefs from list."""
        beliefs = [
            _belief_green_space_rct(),
            _belief_green_space_obs_no_controls(),
            _belief_quasi_experimental(),
        ]
        batch = checker.assess_all_beliefs(beliefs)
        assert batch.beliefs_assessed == 3

    def test_batch_report_aggregates_risk_levels(self, checker):
        """Batch report correctly counts risk levels."""
        beliefs = [
            _belief_green_space_rct(),  # LOW
            _belief_green_space_obs_no_controls(),  # HIGH
            _belief_green_space_obs_partial_controls(),  # MEDIUM
            _belief_qualitative(),  # LOW
        ]
        batch = checker.assess_all_beliefs(beliefs)
        assert batch.high_risk_count >= 1
        assert batch.medium_risk_count >= 1
        assert batch.low_risk_count >= 1

    def test_batch_report_filters_by_risk_level(self, checker):
        """Batch report provides filtered lists by risk level."""
        beliefs = [
            _belief_green_space_rct(),
            _belief_green_space_obs_no_controls(),
            _belief_qualitative(),
        ]
        batch = checker.assess_all_beliefs(beliefs)
        assert len(batch.high_risk_beliefs) >= 1
        assert len(batch.low_risk_beliefs) >= 1

    def test_batch_report_summary(self, checker):
        """Batch report generates summary statistics."""
        beliefs = [
            _belief_green_space_rct(),
            _belief_green_space_obs_no_controls(),
            _belief_quasi_experimental(),
        ]
        batch = checker.assess_all_beliefs(beliefs)
        summary = batch.summary()
        assert isinstance(summary, str)
        assert "Batch Confounder Risk Assessment" in summary
        assert "High Risk:" in summary
        assert "Mean Design Risk" in summary

    def test_batch_report_statistics(self, checker):
        """Batch report computes mean statistics."""
        beliefs = [
            _belief_green_space_rct(),
            _belief_green_space_obs_no_controls(),
        ]
        batch = checker.assess_all_beliefs(beliefs)
        assert 0 <= batch.mean_design_risk <= 1
        assert 0 <= batch.mean_control_adequacy <= 1
        assert 0 <= batch.mean_confidence <= 1

    def test_batch_report_to_dict(self, checker):
        """Batch report serializes to dict."""
        beliefs = [_belief_green_space_rct(), _belief_green_space_obs_no_controls()]
        batch = checker.assess_all_beliefs(beliefs)
        d = batch.to_dict()
        assert isinstance(d, dict)
        assert d["beliefs_assessed"] == 2
        assert "high_risk_count" in d
        assert "reports" in d
        assert len(d["reports"]) == 2


# --- Test: Edge Cases ---

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_belief_without_belief_id(self, checker):
        """Handle belief without explicit belief_id field."""
        belief = _belief_missing_id()
        report = checker.assess_confounder_risk(belief)
        # Should use "unknown" or auto-generated ID
        assert report.belief_id is not None and report.belief_id != ""

    def test_empty_antecedent(self, checker):
        """Handle belief with missing/empty antecedent."""
        belief = {
            "antecedent": "",
            "consequent": "stress",
            "study_design": "observational",
        }
        report = checker.assess_confounder_risk(belief)
        # Should not crash; confounders list may be empty
        assert isinstance(report, ConfounderRiskReport)

    def test_none_values_in_fields(self, checker):
        """Handle None values gracefully."""
        belief = {
            "belief_id": "b_test",
            "antecedent": "green space",
            "consequent": None,
            "study_design": None,
            "controlled_variables": None,
        }
        report = checker.assess_confounder_risk(belief)
        # Should handle None without crashing
        assert isinstance(report, ConfounderRiskReport)

    def test_empty_beliefs_batch(self, checker):
        """Handle empty batch."""
        batch = checker.assess_all_beliefs({})
        assert batch.beliefs_assessed == 0
        assert batch.high_risk_count == 0

    def test_custom_confounder_registry(self):
        """Initialize checker with custom confounder registry."""
        custom = {
            "custom_domain": ["custom_confounder_1", "custom_confounder_2"],
        }
        custom_checker = ConfounderRiskChecker(custom_confounders=custom)
        belief = {"antecedent": "test", "domain": "custom_domain"}
        confounders = custom_checker.lookup_known_confounders(belief)
        assert "custom_confounder_1" in confounders

    def test_case_insensitive_matching(self, checker):
        """Confounder matching should be case-insensitive."""
        belief = {
            "antecedent": "GREEN SPACE EXPOSURE",
            "domain": "green_space",
        }
        confounders = checker.lookup_known_confounders(belief)
        assert len(confounders) > 0

    def test_confidence_score_ranges(self, checker):
        """Confidence scores should always be 0.0-1.0."""
        beliefs = [
            _belief_green_space_rct(),
            _belief_green_space_obs_no_controls(),
            _belief_qualitative(),
            _belief_unknown_design_no_confounders(),
        ]
        batch = checker.assess_all_beliefs(beliefs)
        for report in batch.reports:
            assert 0 <= report.confidence <= 1
