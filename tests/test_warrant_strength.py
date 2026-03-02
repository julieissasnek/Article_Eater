"""
Tests for warrant strength (ω) computation module.

Sprint CREDENCE-WARRANT Phase 4: validates the panel-approved ω formula
and its component functions per §48.3B.

Tests cover:
1. Individual ω components (severity, confound, replication, meta)
2. Composite ω formula
3. Floor constraint R1 (Illari + Cartwright)
4. TEA score loading
5. Credence from warrants (parallel projection)
6. Design type inference helpers
"""

import json
import math
import os
import tempfile
from pathlib import Path

import pytest

from src.services.warrant_strength import (
    DesignType,
    PublicationType,
    OmegaResult,
    load_tea_scores,
    compute_omega_sev,
    compute_omega_theory,
    compute_omega_base,
    compute_omega_conf,
    compute_omega_rep,
    compute_omega_meta,
    compute_omega,
    compute_omega_from_extraction,
    compute_credence_from_warrants,
    _clamp,
    _logit,
    _sigmoid,
    CANONICAL_DISCOUNT_FACTORS,
)


# ============================================================================
# Utility function tests
# ============================================================================


class TestClamp:
    def test_within_range(self):
        assert _clamp(0.5) == 0.5

    def test_below_range(self):
        assert _clamp(-0.5) == 0.0

    def test_above_range(self):
        assert _clamp(1.5) == 1.0

    def test_at_boundaries(self):
        assert _clamp(0.0) == 0.0
        assert _clamp(1.0) == 1.0

    def test_custom_range(self):
        assert _clamp(5.0, 0.0, 10.0) == 5.0
        assert _clamp(-1.0, 0.0, 10.0) == 0.0


class TestLogitSigmoid:
    def test_logit_neutral(self):
        assert abs(_logit(0.5)) < 1e-10

    def test_logit_positive(self):
        assert _logit(0.75) > 0

    def test_logit_negative(self):
        assert _logit(0.25) < 0

    def test_sigmoid_neutral(self):
        assert abs(_sigmoid(0.0) - 0.5) < 1e-10

    def test_sigmoid_positive(self):
        assert _sigmoid(2.0) > 0.5

    def test_sigmoid_extreme(self):
        assert _sigmoid(200) == 1.0
        assert _sigmoid(-200) == 0.0

    def test_roundtrip(self):
        for p in [0.1, 0.3, 0.5, 0.7, 0.9]:
            assert abs(_sigmoid(_logit(p)) - p) < 1e-8


# ============================================================================
# Component function tests
# ============================================================================


class TestOmegaSev:
    def test_large_rct_high_n(self):
        sev = compute_omega_sev(DesignType.LARGE_RCT, sample_size=300)
        assert sev == 0.95

    def test_large_rct_low_n(self):
        sev = compute_omega_sev(DesignType.LARGE_RCT, sample_size=100)
        assert sev == 0.85

    def test_observational_baseline(self):
        sev = compute_omega_sev(DesignType.OBSERVATIONAL)
        assert 0.25 <= sev <= 0.40

    def test_pre_registration_bonus(self):
        base = compute_omega_sev(DesignType.STANDARD_RCT)
        boosted = compute_omega_sev(DesignType.STANDARD_RCT, pre_registered=True)
        assert boosted == base + 0.05

    def test_blinding_bonus(self):
        base = compute_omega_sev(DesignType.STANDARD_RCT)
        boosted = compute_omega_sev(DesignType.STANDARD_RCT, blinded=True)
        assert boosted == base + 0.05

    def test_self_report_penalty(self):
        base = compute_omega_sev(DesignType.STANDARD_RCT)
        penalized = compute_omega_sev(DesignType.STANDARD_RCT, self_report_only=True)
        assert penalized == base - 0.10

    def test_clamped_to_01(self):
        # Max modifiers on already-high design
        sev = compute_omega_sev(
            DesignType.LARGE_RCT, sample_size=500,
            pre_registered=True, blinded=True
        )
        assert 0.0 <= sev <= 1.0

    def test_case_study_low(self):
        sev = compute_omega_sev(DesignType.CASE_STUDY)
        assert sev < 0.30


class TestOmegaTheory:
    @pytest.fixture
    def tea_scores(self):
        return {"chronobiological-regulation": 0.928, "biophilia-hypothesis": 0.430, "attention-restoration-theory": 0.540}

    def test_known_theory(self, tea_scores):
        ot = compute_omega_theory("chronobiological-regulation", 0.8, tea_scores)
        assert abs(ot - 0.928 * 0.8) < 0.01

    def test_unknown_theory(self, tea_scores):
        ot = compute_omega_theory("nonexistent_theory", 0.8, tea_scores)
        assert ot == 0.0

    def test_zero_specificity(self, tea_scores):
        ot = compute_omega_theory("chronobiological-regulation", 0.0, tea_scores)
        assert ot == 0.0

    def test_full_specificity(self, tea_scores):
        ot = compute_omega_theory("biophilia-hypothesis", 1.0, tea_scores)
        assert abs(ot - 0.430) < 0.01


class TestOmegaBase:
    def test_non_mechanism_ignores_theory(self):
        base, applied = compute_omega_base(0.70, omega_theory=0.90, is_mechanism_edge=False)
        assert base == 0.70
        assert not applied

    def test_mechanism_combines(self):
        # ω_base = 0.70 + 0.60 × (1 - 0.70) = 0.70 + 0.18 = 0.88
        base, applied = compute_omega_base(0.70, omega_theory=0.60, is_mechanism_edge=True)
        assert abs(base - 0.88) < 0.01
        assert not applied

    def test_floor_constraint_r1(self):
        """R1: When ω_sev < 0.20, ω_base ≤ 2 × ω_sev."""
        base, applied = compute_omega_base(0.10, omega_theory=0.90, is_mechanism_edge=True)
        # Without floor: 0.10 + 0.90 × 0.90 = 0.91
        # With floor: capped at 2 × 0.10 = 0.20
        assert base <= 0.20
        assert applied

    def test_floor_not_applied_when_sev_high(self):
        base, applied = compute_omega_base(0.50, omega_theory=0.80, is_mechanism_edge=True)
        assert not applied

    def test_floor_edge_case_sev_exactly_020(self):
        """At exactly 0.20, floor should NOT apply (< 0.20 only)."""
        base, applied = compute_omega_base(0.20, omega_theory=0.80, is_mechanism_edge=True)
        assert not applied


class TestOmegaConf:
    def test_no_confounds_with_randomization(self):
        oc = compute_omega_conf(0, has_randomization=True)
        assert oc >= 0.95

    def test_many_confounds(self):
        oc = compute_omega_conf(5)
        assert oc <= 0.50

    def test_moderate_with_controls(self):
        oc = compute_omega_conf(2, has_randomization=True, has_active_control=True)
        assert 0.70 <= oc <= 1.0


class TestOmegaRep:
    def test_single_study(self):
        assert compute_omega_rep(0, 0) == 0.55

    def test_conceptual_only(self):
        assert compute_omega_rep(0, 3) == 0.70

    def test_independent_replication(self):
        assert compute_omega_rep(1, 0) == 1.00


class TestOmegaMeta:
    def test_registered_report(self):
        om = compute_omega_meta(PublicationType.REGISTERED_REPORT)
        assert om == 1.00

    def test_peer_reviewed(self):
        om = compute_omega_meta(PublicationType.PEER_REVIEWED)
        assert om == 0.90

    def test_preprint(self):
        om = compute_omega_meta(PublicationType.PREPRINT)
        assert om == 0.80

    def test_pre_registration_bonus(self):
        om = compute_omega_meta(PublicationType.PEER_REVIEWED, is_pre_registered=True)
        assert om == 1.00  # 0.90 + 0.10 = 1.00

    def test_grey_lit_with_prereg(self):
        om = compute_omega_meta(PublicationType.GREY_LITERATURE, is_pre_registered=True)
        assert abs(om - 0.80) < 0.01  # 0.70 + 0.10


# ============================================================================
# Composite formula tests
# ============================================================================


class TestComputeOmega:
    def test_all_maximal(self):
        omega = compute_omega(1.0, 1.0, 1.0, 1.0)
        assert omega == 1.0

    def test_multiplicative_reduction(self):
        omega = compute_omega(0.80, 0.90, 0.55, 0.90)
        expected = 0.80 * 0.90 * 0.55 * 0.90
        assert abs(omega - expected) < 0.001

    def test_single_weak_component(self):
        """A single weak component should drag down the composite."""
        omega = compute_omega(0.90, 0.90, 0.30, 0.90)
        assert omega < 0.30  # 0.90 * 0.90 * 0.30 * 0.90 ≈ 0.22


# ============================================================================
# TEA score loading
# ============================================================================


class TestLoadTeaScores:
    def test_load_structured_format(self, tmp_path):
        data = {
            "metadata": {"version": "1.0.0"},
            "theories": [
                {"theory_id": "attention-restoration-theory", "T_ent": 0.540},
                {"theory_id": "biophilia-hypothesis", "T_ent": 0.430},
            ],
        }
        path = tmp_path / "tea_scores.json"
        path.write_text(json.dumps(data))

        scores = load_tea_scores(str(path))
        # New hyphenated keys should be present
        assert scores["attention-restoration-theory"] == 0.540
        assert scores["biophilia-hypothesis"] == 0.430
        # Backward compatibility mappings are also present (old keys)
        assert len(scores) >= 2

    def test_load_flat_format(self, tmp_path):
        data = {"attention-restoration-theory": 0.54, "biophilia-hypothesis": 0.43}
        path = tmp_path / "tea_scores.json"
        path.write_text(json.dumps(data))

        scores = load_tea_scores(str(path))
        assert scores["attention-restoration-theory"] == 0.54

    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_tea_scores("/nonexistent/path/tea_scores.json")


# ============================================================================
# OmegaResult dataclass
# ============================================================================


class TestOmegaResult:
    def test_clamping(self):
        result = OmegaResult(
            omega=1.5, omega_base=1.2, omega_sev=0.5,
            omega_theory=0.3, omega_conf=0.8, omega_rep=0.6, omega_meta=0.9
        )
        assert result.omega == 1.0
        assert result.omega_base == 1.0

    def test_to_dict(self):
        result = OmegaResult(
            omega=0.5, omega_base=0.6, omega_sev=0.7,
            omega_theory=0.3, omega_conf=0.8, omega_rep=0.6, omega_meta=0.9,
            floor_constraint_applied=True
        )
        d = result.to_dict()
        assert d["omega"] == 0.5
        assert d["floor_constraint_applied"] is True
        assert "design_type" in d


# ============================================================================
# Integration: compute_omega_from_extraction
# ============================================================================


class TestComputeOmegaFromExtraction:
    @pytest.fixture
    def tea_scores(self):
        return {"attention-restoration-theory": 0.540, "chronobiological-regulation": 0.928}

    def test_basic_rct(self, tea_scores):
        finding = {
            "design_type": "standard_rct",
            "sample_size": 80,
            "has_randomization": True,
            "publication_type": "peer_reviewed",
        }
        result = compute_omega_from_extraction(finding, tea_scores=tea_scores)
        assert isinstance(result, OmegaResult)
        assert 0.0 < result.omega < 1.0
        assert result.design_type == "standard_rct"

    def test_mechanism_edge_with_theory(self, tea_scores):
        finding = {
            "design_type": "standard_rct",
            "is_mechanism_edge": True,
            "mechanism_specificity": 0.80,
            "has_randomization": True,
        }
        result = compute_omega_from_extraction(
            finding, theory_id="chronobiological-regulation", tea_scores=tea_scores
        )
        assert result.omega_theory > 0
        assert result.omega_base > result.omega_sev  # Theory should boost base

    def test_observational_no_theory(self, tea_scores):
        finding = {"design_type": "observational"}
        result = compute_omega_from_extraction(finding, tea_scores=tea_scores)
        assert result.omega_sev < 0.40
        assert result.omega_theory == 0.0

    def test_invalid_design_type(self, tea_scores):
        finding = {"design_type": "nonsense_design"}
        with pytest.raises(ValueError):
            compute_omega_from_extraction(finding, tea_scores=tea_scores)


# ============================================================================
# Credence from warrants (projection formula)
# ============================================================================


class TestCredenceFromWarrants:
    def test_empty_edges(self):
        """No evidence → neutral credence."""
        assert compute_credence_from_warrants([]) == 0.5

    def test_single_strong_positive(self):
        """Strong positive evidence → credence > 0.5."""
        edges = [{"p_lab": 0.80, "tau": "empirical_association", "omega": 0.85, "delta": 1.0}]
        c = compute_credence_from_warrants(edges)
        assert c > 0.5

    def test_single_strong_negative(self):
        """Strong negative evidence (p_lab < 0.5) → credence < 0.5."""
        edges = [{"p_lab": 0.20, "tau": "empirical_association", "omega": 0.85, "delta": 1.0}]
        c = compute_credence_from_warrants(edges)
        assert c < 0.5

    def test_convergent_evidence(self):
        """Multiple independent positive lines → higher credence than single."""
        single = [{"p_lab": 0.70, "tau": "mechanism", "omega": 0.80, "delta": 1.0}]
        convergent = [
            {"p_lab": 0.70, "tau": "mechanism", "omega": 0.80, "delta": 1.0},
            {"p_lab": 0.65, "tau": "empirical_association", "omega": 0.75, "delta": 0.90},
        ]
        c_single = compute_credence_from_warrants(single)
        c_convergent = compute_credence_from_warrants(convergent)
        assert c_convergent > c_single

    def test_population_discount(self):
        """Low delta → weaker evidence transfer → closer to 0.5."""
        full = [{"p_lab": 0.80, "tau": "mechanism", "omega": 0.85, "delta": 1.0}]
        discounted = [{"p_lab": 0.80, "tau": "mechanism", "omega": 0.85, "delta": 0.30}]
        c_full = compute_credence_from_warrants(full)
        c_disc = compute_credence_from_warrants(discounted)
        assert abs(c_disc - 0.5) < abs(c_full - 0.5)

    def test_neutral_p_lab(self):
        """p_lab = 0.5 → logit = 0 → no contribution → 0.5."""
        edges = [{"p_lab": 0.5, "tau": "mechanism", "omega": 1.0, "delta": 1.0}]
        c = compute_credence_from_warrants(edges)
        assert abs(c - 0.5) < 0.01

    def test_canonical_discount_factors(self):
        """Higher-trust warrant types should produce stronger credence shifts."""
        constitutive = [{"p_lab": 0.75, "tau": "constitutive", "omega": 0.80, "delta": 1.0}]
        analogical = [{"p_lab": 0.75, "tau": "analogical", "omega": 0.80, "delta": 1.0}]
        c_const = compute_credence_from_warrants(constitutive)
        c_analog = compute_credence_from_warrants(analogical)
        assert c_const > c_analog  # Constitutive (d=0.95) > Analogical (d=0.40)


# ============================================================================
# Sanity checks: known worked examples from §48.3B/§48.3C
# ============================================================================


class TestWorkedExamples:
    """Validate against the worked examples in the master doc."""

    def test_circadian_rct(self):
        """
        Circadian (chronobiological-regulation): Large RCT, T_ent=0.928, high specificity.
        Should produce ω > 0.60 (strong warrant).
        """
        tea = {"chronobiological-regulation": 0.928}
        finding = {
            "design_type": "large_rct",
            "sample_size": 250,
            "pre_registered": True,
            "blinded": True,
            "has_randomization": True,
            "has_active_control": True,
            "n_independent_replications": 3,
            "publication_type": "peer_reviewed",
            "is_mechanism_edge": True,
            "mechanism_specificity": 0.90,
        }
        result = compute_omega_from_extraction(finding, theory_id="chronobiological-regulation", tea_scores=tea)
        assert result.omega > 0.60
        assert not result.floor_constraint_applied

    def test_biophilia_observational(self):
        """
        Biophilia (biophilia-hypothesis): Observational, T_ent=0.430, low specificity.
        Should produce ω < 0.25 (weak warrant).
        """
        tea = {"biophilia-hypothesis": 0.430}
        finding = {
            "design_type": "observational",
            "self_report_only": True,
            "publication_type": "peer_reviewed",
        }
        result = compute_omega_from_extraction(finding, theory_id="biophilia-hypothesis", tea_scores=tea)
        assert result.omega < 0.25

    def test_floor_constraint_weak_design_strong_theory(self):
        """
        Case study with strong theory backing (chronobiological-regulation): floor constraint should fire.
        """
        tea = {"chronobiological-regulation": 0.928}
        finding = {
            "design_type": "case_study",
            "is_mechanism_edge": True,
            "mechanism_specificity": 0.95,
        }
        result = compute_omega_from_extraction(finding, theory_id="chronobiological-regulation", tea_scores=tea)
        assert result.floor_constraint_applied
        # ω_sev for case_study ≈ 0.17, floor = 2 × 0.17 = 0.34
        assert result.omega_base <= 0.35
