"""Tests for ARCH-6 severe testing and ARCH-3 independence scoring.

Tests cover:
- StudyDesign and EvidenceQuality enum membership
- Severity computation with study design modulation (ARCH-6a)
- Evidence quality classification (ARCH-6d)
- Severity gate for high-credence beliefs (ARCH-6c)
- Independence scoring (ARCH-3b)
"""

import pytest

from src.services.web_of_belief import Belief, Credence, EpistemicLevel
from src.services.web_of_belief_components import (
    EvidenceQuality,
    StudyDesign,
    STUDY_DESIGN_SEVERITY_WEIGHT,
)
from src.services.web_of_belief_modules.independence import compute_independence_score


# ===== ARCH-6a: StudyDesign enum =====

class TestStudyDesignEnum:
    def test_all_members_present(self):
        assert StudyDesign.RCT.value == "rct"
        assert StudyDesign.META_ANALYSIS.value == "meta_analysis"
        assert StudyDesign.QUASI_EXPERIMENTAL.value == "quasi_experimental"
        assert StudyDesign.OBSERVATIONAL.value == "observational"
        assert StudyDesign.CASE_STUDY.value == "case_study"
        assert StudyDesign.QUALITATIVE.value == "qualitative"
        assert StudyDesign.THEORETICAL.value == "theoretical"
        assert StudyDesign.UNKNOWN.value == "unknown"

    def test_severity_weights_cover_all_members(self):
        for member in StudyDesign:
            assert member.value in STUDY_DESIGN_SEVERITY_WEIGHT, (
                f"Missing weight for {member}"
            )

    def test_severity_weights_ordered(self):
        """RCT should have highest weight, THEORETICAL lowest."""
        assert STUDY_DESIGN_SEVERITY_WEIGHT["rct"] > STUDY_DESIGN_SEVERITY_WEIGHT["observational"]
        assert STUDY_DESIGN_SEVERITY_WEIGHT["observational"] > STUDY_DESIGN_SEVERITY_WEIGHT["case_study"]
        assert STUDY_DESIGN_SEVERITY_WEIGHT["case_study"] > STUDY_DESIGN_SEVERITY_WEIGHT["theoretical"]


# ===== ARCH-6a + 6b: compute_severity incorporating study design =====

class TestSeverityWithStudyDesign:
    def _make_belief(self, **kwargs):
        defaults = dict(
            belief_id="test_belief",
            content="test content",
            level=EpistemicLevel.EMPIRICAL,
        )
        defaults.update(kwargs)
        return Belief(**defaults)

    def test_rct_higher_severity_than_observational(self):
        """Same evidence metrics but RCT should score higher."""
        rct = self._make_belief(
            belief_id="rct_belief",
            study_design=StudyDesign.RCT,
            evidence_sample_n=100,
            evidence_effect_size=0.5,
            evidence_p_value=0.01,
            credence=Credence(0.7, 0.3),
        )
        obs = self._make_belief(
            belief_id="obs_belief",
            study_design=StudyDesign.OBSERVATIONAL,
            evidence_sample_n=100,
            evidence_effect_size=0.5,
            evidence_p_value=0.01,
            credence=Credence(0.7, 0.3),
        )
        assert rct.compute_severity() > obs.compute_severity()

    def test_theoretical_very_low_severity(self):
        """Theoretical belief with no empirical data should have very low severity."""
        b = self._make_belief(study_design=StudyDesign.THEORETICAL)
        assert b.compute_severity() < 0.15

    def test_severity_bounded_0_1(self):
        """Severity should always be in [0,1]."""
        for design in StudyDesign:
            b = self._make_belief(
                study_design=design,
                evidence_sample_n=10000,
                evidence_effect_size=2.0,
                evidence_p_value=0.0001,
                credence=Credence(0.9, 0.1),
            )
            sev = b.compute_severity()
            assert 0.0 <= sev <= 1.0, f"Severity {sev} out of bounds for {design}"


# ===== ARCH-6d: classify_evidence_quality =====

class TestEvidenceQualityClassification:
    def _make_belief(self, **kwargs):
        defaults = dict(
            belief_id="test_belief",
            content="test",
            level=EpistemicLevel.EMPIRICAL,
        )
        defaults.update(kwargs)
        return Belief(**defaults)

    def test_rct_with_strong_evidence_is_severely_tested(self):
        b = self._make_belief(
            study_design=StudyDesign.RCT,
            evidence_sample_n=200,
            evidence_effect_size=0.6,
            evidence_p_value=0.001,
            credence=Credence(0.75, 0.2),
        )
        assert b.classify_evidence_quality() == EvidenceQuality.SEVERELY_TESTED

    def test_observational_with_data_is_consistent_or_moderate(self):
        b = self._make_belief(
            study_design=StudyDesign.OBSERVATIONAL,
            evidence_sample_n=50,
            evidence_effect_size=0.3,
            evidence_p_value=0.04,
            credence=Credence(0.5, 0.4),
        )
        quality = b.classify_evidence_quality()
        assert quality in (EvidenceQuality.MODERATELY_TESTED, EvidenceQuality.CONSISTENT_ONLY)

    def test_no_evidence_is_untested(self):
        b = self._make_belief(study_design=StudyDesign.UNKNOWN)
        assert b.classify_evidence_quality() == EvidenceQuality.UNTESTED

    def test_theoretical_with_p_value_is_consistent_only(self):
        b = self._make_belief(
            study_design=StudyDesign.THEORETICAL,
            evidence_p_value=0.05,
            credence=Credence(0.4, 0.5),
        )
        assert b.classify_evidence_quality() == EvidenceQuality.CONSISTENT_ONLY


# ===== ARCH-6c: severity_gate_check =====

class TestSeverityGate:
    def _make_belief(self, **kwargs):
        defaults = dict(
            belief_id="test_belief",
            content="test",
            level=EpistemicLevel.EMPIRICAL,
        )
        defaults.update(kwargs)
        return Belief(**defaults)

    def test_low_credence_always_passes(self):
        """Beliefs with credence <= 0.70 should never trigger the gate."""
        b = self._make_belief(
            credence=Credence(0.60, 0.5),
            study_design=StudyDesign.UNKNOWN,
        )
        assert b.severity_gate_check() is None

    def test_high_credence_no_evidence_fails_gate(self):
        """High credence + no testing evidence should trigger warning."""
        b = self._make_belief(
            credence=Credence(0.80, 0.2),
            study_design=StudyDesign.UNKNOWN,
        )
        warning = b.severity_gate_check()
        assert warning is not None
        assert "SEVERITY_GATE" in warning
        assert "test_belief" in warning

    def test_high_credence_with_rct_passes_gate(self):
        """High credence + strong RCT evidence should pass the gate."""
        b = self._make_belief(
            credence=Credence(0.80, 0.2),
            study_design=StudyDesign.RCT,
            evidence_sample_n=200,
            evidence_effect_size=0.6,
            evidence_p_value=0.001,
        )
        assert b.severity_gate_check() is None

    def test_gate_returns_informative_message(self):
        """Warning message should include belief_id, credence, and details."""
        b = self._make_belief(
            belief_id="overconfident_claim",
            credence=Credence(0.85, 0.15),
            study_design=StudyDesign.CASE_STUDY,
        )
        warning = b.severity_gate_check()
        assert warning is not None
        assert "overconfident_claim" in warning
        assert "0.85" in warning
        assert "case_study" in warning


# ===== ARCH-3b: compute_independence_score =====

class TestIndependenceScoring:
    def test_single_lab_low_diversity(self):
        records = [
            {"lab": "Lab A", "method": "fMRI", "population": "students"},
            {"lab": "Lab A", "method": "fMRI", "population": "students"},
            {"lab": "Lab A", "method": "fMRI", "population": "students"},
        ]
        result = compute_independence_score(records)
        assert result["lab_diversity"] < 0.5
        assert result["independence_score"] < 0.3

    def test_diverse_labs_high_score(self):
        records = [
            {"lab": "Lab A", "method": "fMRI", "population": "students"},
            {"lab": "Lab B", "method": "EEG", "population": "elderly"},
            {"lab": "Lab C", "method": "behavioral", "population": "patients"},
        ]
        result = compute_independence_score(records)
        assert result["lab_diversity"] == 1.0
        assert result["method_diversity"] == 1.0
        assert result["population_diversity"] == 1.0
        assert result["independence_score"] > 0.8

    def test_empty_records(self):
        result = compute_independence_score([])
        assert result["n_records"] == 0.0
        assert result["lab_diversity"] == 0.0
        assert result["method_diversity"] == 0.0
        assert result["population_diversity"] == 0.0

    def test_mixed_independence(self):
        """Two labs, one method, two populations → moderate."""
        records = [
            {"lab": "Lab A", "method": "fMRI", "population": "students"},
            {"lab": "Lab B", "method": "fMRI", "population": "elderly"},
        ]
        result = compute_independence_score(records)
        assert result["lab_diversity"] == 1.0
        assert result["method_diversity"] < 1.0
        assert 0.3 < result["independence_score"] < 0.8


# ===== to_dict includes new fields =====

class TestBeliefSerialization:
    def test_to_dict_includes_new_fields(self):
        b = Belief(
            belief_id="serialization_test",
            content="test",
            level=EpistemicLevel.EMPIRICAL,
            study_design=StudyDesign.RCT,
        )
        d = b.to_dict()
        assert "study_design" in d
        assert d["study_design"] == "rct"
        assert "evidence_quality" in d
        assert "severity_gate_warning" in d
        assert "severity" in d
