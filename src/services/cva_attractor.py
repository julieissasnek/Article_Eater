"""
cva_attractor.py — CVA Attractor Engine
=========================================

Fixed-point solver, Lyapunov stability analysis,
basin-of-attraction computation, and rasa attractor configurations.

Reference: AG_ASSIGNMENT Phase 3, Tasks 3.1–3.7
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math
import json

from src.models.cva_valuation import CVAValuationVector, CulturalVariant
from src.services.cva_dynamics import CVADynamics, DynamicsState, FeedbackSignal


# ──────────────────────────────────────────────────────────────────
# Attractor Point
# ──────────────────────────────────────────────────────────────────

@dataclass
class AttractorPoint:
    """A fixed point in the constraint-valuation state space."""
    name: str
    constraints: List[float]
    valuations: List[float]
    stability: str = "stable"  # stable, unstable, saddle
    basin_radius: float = 0.0
    lyapunov_exponent: float = 0.0
    metadata: Dict = field(default_factory=dict)

    @property
    def state(self) -> DynamicsState:
        return DynamicsState(constraints=self.constraints, valuations=self.valuations)

    def distance_to(self, state: DynamicsState) -> float:
        """Euclidean distance from state to this attractor."""
        d_c = sum((a - b) ** 2 for a, b in zip(self.constraints, state.constraints))
        d_v = sum((a - b) ** 2 for a, b in zip(self.valuations, state.valuations))
        return math.sqrt(d_c + d_v)


# ──────────────────────────────────────────────────────────────────
# Nine Rasa Attractor Configurations
# ──────────────────────────────────────────────────────────────────

RASA_ATTRACTORS: Dict[str, AttractorPoint] = {
    "shringara": AttractorPoint(  # Love/Beauty
        name="shringara",
        constraints=[0.3, 0.3, 0.2, 0.6, 0.5, 0.6, 0.7, 0.7],
        valuations=[0.6, 0.7, 0.5, 0.3, 0.8, 0.7, 0.5, 0.5, 0.8],
        stability="stable", basin_radius=0.3,
        metadata={"rasa": "Love/Beauty", "dominant_emotion": "delight"},
    ),
    "hasya": AttractorPoint(  # Joy/Humor
        name="hasya",
        constraints=[0.2, 0.4, 0.3, 0.7, 0.6, 0.5, 0.6, 0.5],
        valuations=[0.5, 0.8, 0.4, 0.3, 0.6, 0.5, 0.6, 0.7, 0.5],
        stability="stable", basin_radius=0.25,
        metadata={"rasa": "Joy/Humor", "dominant_emotion": "laughter"},
    ),
    "karuna": AttractorPoint(  # Compassion
        name="karuna",
        constraints=[0.4, 0.3, 0.4, 0.4, 0.4, 0.6, 0.5, 0.6],
        valuations=[0.4, 0.4, 0.5, 0.2, 0.7, 0.6, 0.4, 0.4, 0.7],
        stability="stable", basin_radius=0.25,
        metadata={"rasa": "Compassion", "dominant_emotion": "sorrow"},
    ),
    "raudra": AttractorPoint(  # Wrath/Power
        name="raudra",
        constraints=[0.5, 0.6, 0.6, 0.8, 0.6, 0.4, 0.4, 0.4],
        valuations=[0.3, 0.5, 0.2, 0.8, 0.3, 0.6, 0.8, 0.7, 0.3],
        stability="stable", basin_radius=0.2,
        metadata={"rasa": "Wrath/Power", "dominant_emotion": "fury"},
    ),
    "veera": AttractorPoint(  # Heroism
        name="veera",
        constraints=[0.4, 0.5, 0.4, 0.8, 0.7, 0.4, 0.5, 0.6],
        valuations=[0.4, 0.7, 0.3, 0.6, 0.4, 0.7, 0.7, 0.8, 0.4],
        stability="stable", basin_radius=0.25,
        metadata={"rasa": "Heroism", "dominant_emotion": "vigor"},
    ),
    "bhayanaka": AttractorPoint(  # Terror/Awe
        name="bhayanaka",
        constraints=[0.7, 0.6, 0.8, 0.2, 0.3, 0.5, 0.3, 0.3],
        valuations=[0.2, 0.6, 0.2, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
        stability="stable", basin_radius=0.2,
        metadata={"rasa": "Terror/Awe", "dominant_emotion": "fear"},
    ),
    "bibhatsa": AttractorPoint(  # Disgust
        name="bibhatsa",
        constraints=[0.7, 0.4, 0.5, 0.2, 0.3, 0.5, 0.3, 0.2],
        valuations=[0.2, 0.2, 0.2, 0.3, 0.3, 0.2, 0.3, 0.2, 0.3],
        stability="stable", basin_radius=0.15,
        metadata={"rasa": "Disgust", "dominant_emotion": "disgust"},
    ),
    "adbhuta": AttractorPoint(  # Wonder
        name="adbhuta",
        constraints=[0.3, 0.4, 0.5, 0.6, 0.6, 0.4, 0.7, 0.6],
        valuations=[0.5, 0.9, 0.4, 0.3, 0.5, 0.6, 0.6, 0.7, 0.5],
        stability="stable", basin_radius=0.3,
        metadata={"rasa": "Wonder", "dominant_emotion": "astonishment"},
    ),
    "shanta": AttractorPoint(  # Peace/Serenity
        name="shanta",
        constraints=[0.2, 0.2, 0.1, 0.5, 0.4, 0.4, 0.8, 0.6],
        valuations=[0.7, 0.3, 0.8, 0.2, 0.6, 0.6, 0.5, 0.4, 0.6],
        stability="stable", basin_radius=0.35,
        metadata={"rasa": "Peace/Serenity", "dominant_emotion": "calm"},
    ),
}

# Cultural attractor variants (shift attractor positions)
CULTURAL_ATTRACTOR_SHIFTS: Dict[str, Dict[str, List[float]]] = {
    "japanese": {
        # Ma-influenced: lower affordance density, higher coherence
        "shanta": [0, 0, 0, 0, -0.15, -0.1, 0.1, 0],
        "adbhuta": [0, 0, 0, 0, -0.1, -0.1, 0.1, 0.1],
    },
    "west_african": {
        # Àṣà-influenced: higher social density, belonging
        "shringara": [0, 0, 0, 0, 0, 0.15, 0, 0.1],
        "hasya": [0, 0, 0, 0, 0, 0.1, 0, 0],
    },
    "indian": {
        # Rasa-native: wider basins, stronger attractors
        "shringara": [0, 0, 0, 0.05, 0.05, 0, 0.05, 0.05],
        "shanta": [0, 0, 0, 0, 0, 0, 0.1, 0.05],
    },
}


class CVAAttractorEngine:
    """
    Attractor engine for CVA dynamics.

    Finds fixed points, computes basins of attraction,
    and handles attractor transitions.
    """

    def __init__(
        self,
        dynamics: Optional[CVADynamics] = None,
        attractors: Optional[Dict[str, AttractorPoint]] = None,
    ):
        self.dynamics = dynamics or CVADynamics(alpha=3.0, beta=2.0, dt=0.01)
        self.attractors = attractors or dict(RASA_ATTRACTORS)

    def find_nearest_attractor(self, state: DynamicsState) -> Tuple[str, float]:
        """Find the nearest attractor to current state."""
        best_name = ""
        best_dist = float("inf")
        for name, attr in self.attractors.items():
            d = attr.distance_to(state)
            if d < best_dist:
                best_dist = d
                best_name = name
        return best_name, best_dist

    def in_basin(self, state: DynamicsState, attractor_name: str) -> bool:
        """Check if state is within the basin of an attractor."""
        attr = self.attractors.get(attractor_name)
        if not attr:
            return False
        return attr.distance_to(state) <= attr.basin_radius

    def find_fixed_point(
        self,
        initial: DynamicsState,
        max_iterations: int = 5000,
        tolerance: float = 0.001,
    ) -> Tuple[DynamicsState, bool]:
        """
        Find fixed point by simulating dynamics until convergence.

        Returns (final_state, converged).
        """
        state = initial
        target_c = initial.constraints
        target_v = initial.valuations

        for i in range(max_iterations):
            new_state = self.dynamics.step(state, target_c, target_v)
            # Check convergence: rate of change < tolerance
            delta = sum(
                (a - b) ** 2
                for a, b in zip(new_state.full_state, state.full_state)
            )
            if math.sqrt(delta) < tolerance:
                return new_state, True
            state = new_state

        return state, False

    def compute_lyapunov(
        self,
        state: DynamicsState,
        perturbation: float = 0.01,
        steps: int = 100,
    ) -> float:
        """
        Estimate maximum Lyapunov exponent via perturbation method.

        Negative → stable attractor
        Zero → marginally stable
        Positive → unstable / chaotic
        """
        target_c = state.constraints
        target_v = state.valuations

        # Create perturbed state
        perturbed = DynamicsState(
            constraints=[c + perturbation for c in state.constraints],
            valuations=[v + perturbation for v in state.valuations],
        )

        # Evolve both
        s1 = state
        s2 = perturbed
        total_log = 0.0

        for _ in range(steps):
            s1 = self.dynamics.step(s1, target_c, target_v)
            s2 = self.dynamics.step(s2, target_c, target_v)

            dist = math.sqrt(sum(
                (a - b) ** 2
                for a, b in zip(s1.full_state, s2.full_state)
            ))
            if dist > 0:
                total_log += math.log(dist / perturbation)

        return total_log / steps if steps > 0 else 0.0

    def transition_path(
        self,
        from_attractor: str,
        to_attractor: str,
        steps: int = 200,
    ) -> List[DynamicsState]:
        """
        Compute transition path between two attractors.

        Simulates dynamics from one attractor's fixed point
        toward another's target state.
        """
        src = self.attractors.get(from_attractor)
        dst = self.attractors.get(to_attractor)
        if not src or not dst:
            return []

        initial = src.state
        target_c = dst.constraints
        target_v = dst.valuations

        return self.dynamics.simulate(initial, target_c, target_v,
                                       duration=steps * self.dynamics.dt)

    def apply_cultural_shift(self, culture: str):
        """Apply cultural shifts to attractor positions."""
        shifts = CULTURAL_ATTRACTOR_SHIFTS.get(culture, {})
        for attr_name, constraint_shift in shifts.items():
            if attr_name in self.attractors:
                attr = self.attractors[attr_name]
                new_c = [
                    max(0, min(1, c + s))
                    for c, s in zip(attr.constraints, constraint_shift)
                ]
                self.attractors[attr_name] = AttractorPoint(
                    name=attr.name,
                    constraints=new_c,
                    valuations=attr.valuations,
                    stability=attr.stability,
                    basin_radius=attr.basin_radius,
                    metadata=attr.metadata,
                )

    def neurotype_basin_modulation(
        self, neurotype: str
    ) -> Dict[str, float]:
        """
        Modulate basin sizes based on neurotype.

        PTSD: shanta basin wider (craves peace), bhayanaka narrower
        ASD: adbhuta wider (wonder-seeking), shringara narrower
        ADHD: hasya/adbhuta wider (novelty), shanta narrower
        """
        mods: Dict[str, Dict[str, float]] = {
            "ptsd": {"shanta": 1.5, "bhayanaka": 0.5, "raudra": 0.5},
            "asd": {"adbhuta": 1.4, "shanta": 1.3, "shringara": 0.7},
            "adhd": {"hasya": 1.4, "adbhuta": 1.3, "shanta": 0.6},
            "depression": {"shanta": 0.7, "hasya": 0.5, "karuna": 1.5},
            "anxiety": {"shanta": 1.5, "bhayanaka": 1.3, "raudra": 0.5},
            "gifted": {"adbhuta": 1.5, "veera": 1.3},
        }
        factors = mods.get(neurotype, {})
        result = {}
        for name, attr in self.attractors.items():
            factor = factors.get(name, 1.0)
            result[name] = attr.basin_radius * factor
        return result

    def save_attractors_json(self, path: str):
        """Save attractor configurations to JSON."""
        data = {}
        for name, attr in self.attractors.items():
            data[name] = {
                "constraints": attr.constraints,
                "valuations": attr.valuations,
                "stability": attr.stability,
                "basin_radius": attr.basin_radius,
                "metadata": attr.metadata,
            }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
