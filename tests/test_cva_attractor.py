"""
test_cva_attractor.py — Tests for CVA Attractor Engine (Phase 3)
"""

import pytest
from src.services.cva_attractor import (
    CVAAttractorEngine, AttractorPoint, RASA_ATTRACTORS,
    CULTURAL_ATTRACTOR_SHIFTS,
)
from src.services.cva_dynamics import DynamicsState


class TestAttractorEngine:
    def test_nine_rasa_attractors(self):
        assert len(RASA_ATTRACTORS) == 9

    def test_find_nearest_attractor(self):
        engine = CVAAttractorEngine()
        # State near shanta (low cost, high coherence, safety)
        state = DynamicsState(
            constraints=[0.2, 0.2, 0.1, 0.5, 0.4, 0.4, 0.8, 0.6],
            valuations=[0.7, 0.3, 0.8, 0.2, 0.6, 0.6, 0.5, 0.4, 0.6],
        )
        name, dist = engine.find_nearest_attractor(state)
        assert name == "shanta"
        assert dist < 0.1

    def test_in_basin(self):
        engine = CVAAttractorEngine()
        # Exact attractor state → should be in basin
        attr = RASA_ATTRACTORS["shanta"]
        state = attr.state
        assert engine.in_basin(state, "shanta")

    def test_not_in_distant_basin(self):
        engine = CVAAttractorEngine()
        state = DynamicsState(
            constraints=[0.9] * 8,
            valuations=[0.1] * 9,
        )
        assert not engine.in_basin(state, "shanta")

    def test_transition_path_length(self):
        engine = CVAAttractorEngine()
        path = engine.transition_path("shanta", "adbhuta", steps=100)
        assert len(path) > 50

    def test_cultural_shift_modifies_attractors(self):
        engine = CVAAttractorEngine()
        before = engine.attractors["shanta"].constraints[:]
        engine.apply_cultural_shift("japanese")
        after = engine.attractors["shanta"].constraints
        assert before != after

    def test_neurotype_basin_modulation(self):
        engine = CVAAttractorEngine()
        mods = engine.neurotype_basin_modulation("ptsd")
        # PTSD: shanta wider, bhayanaka narrower
        assert mods["shanta"] > RASA_ATTRACTORS["shanta"].basin_radius
        assert mods["bhayanaka"] < RASA_ATTRACTORS["bhayanaka"].basin_radius

    def test_lyapunov_negative_at_attractor(self):
        engine = CVAAttractorEngine()
        attr = RASA_ATTRACTORS["shanta"]
        # Use dynamics stability check (Jacobian-based) instead of perturbation
        is_stable, kappa = engine.dynamics.check_stability(
            attr.state, attr.constraints, attr.valuations
        )
        assert is_stable
        assert kappa < 0.5

    def test_attractor_distance(self):
        a = AttractorPoint("a", [0.5]*8, [0.5]*9)
        state = DynamicsState(constraints=[0.5]*8, valuations=[0.5]*9)
        assert a.distance_to(state) == 0.0


class TestRasaConfigurations:
    def test_all_constraints_in_range(self):
        for name, attr in RASA_ATTRACTORS.items():
            for v in attr.constraints:
                assert 0.0 <= v <= 1.0, f"{name} constraint out of range"

    def test_all_valuations_in_range(self):
        for name, attr in RASA_ATTRACTORS.items():
            for v in attr.valuations:
                assert 0.0 <= v <= 1.0, f"{name} valuation out of range"

    def test_constraint_length(self):
        for name, attr in RASA_ATTRACTORS.items():
            assert len(attr.constraints) == 8, f"{name}: {len(attr.constraints)}"

    def test_valuation_length(self):
        for name, attr in RASA_ATTRACTORS.items():
            assert len(attr.valuations) == 9, f"{name}: {len(attr.valuations)}"
