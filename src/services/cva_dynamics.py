"""
cva_dynamics.py — CVA Continuous-Time Dynamics
===============================================

Coupled ODE system for constraint–valuation evolution:

    ∂c/∂t = α · (c_target − c) + ε_constraint · feedback
    ∂v/∂t = β · V(c) − β · v + ε_valuation · feedback

With Jacobian stability analysis (κ_loop < 0.5 required).

Reference: AG_ASSIGNMENT Phase 2, Tasks 2.6–2.7
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math

from src.models.cva_constraint import Tier2ConstraintVector
from src.models.cva_valuation import CVAValuationVector


@dataclass
class DynamicsState:
    """
    State vector for the coupled ODE system.
    Contains both constraint and valuation vectors at time t.
    """
    t: float = 0.0
    constraints: List[float] = field(default_factory=lambda: [0.5] * 8)
    valuations: List[float] = field(default_factory=lambda: [0.5] * 9)

    # Feedback signals
    epsilon_constraint: List[float] = field(default_factory=lambda: [0.0] * 8)
    epsilon_valuation: List[float] = field(default_factory=lambda: [0.0] * 9)

    @property
    def full_state(self) -> List[float]:
        """Combined state vector [c, v]."""
        return self.constraints + self.valuations


@dataclass
class FeedbackSignal:
    """
    Decomposed feedback from spec §2.3/Task 2.4:
        ε_attn:  attentional prediction error
        ε_prec:  precision-weighted prediction error
        ε_prior: prior-expectation prediction error
    """
    epsilon_attn: float = 0.0
    epsilon_prec: float = 0.0
    epsilon_prior: float = 0.0

    @property
    def total(self) -> float:
        """Weighted combination of feedback components."""
        return 0.4 * self.epsilon_attn + 0.4 * self.epsilon_prec + 0.2 * self.epsilon_prior


class CVADynamics:
    """
    Continuous-time dynamics engine for CVA.

    Implements coupled ODEs with:
    - Exponential approach to target constraints
    - Valuation tracking of constraint state
    - Decomposed feedback signals
    - Jacobian stability analysis
    """

    def __init__(
        self,
        alpha: float = 2.0,     # Constraint adaptation rate
        beta: float = 1.5,      # Valuation tracking rate
        dt: float = 0.01,       # Time step
        stability_threshold: float = 0.5,  # κ_loop max
    ):
        self.alpha = alpha
        self.beta = beta
        self.dt = dt
        self.stability_threshold = stability_threshold

    def step(
        self,
        state: DynamicsState,
        target_constraints: List[float],
        target_valuations: List[float],
        feedback: Optional[FeedbackSignal] = None,
    ) -> DynamicsState:
        """
        Advance one time step via Euler integration.

        ∂c/∂t = α · (c_target − c) + ε_c · feedback
        ∂v/∂t = β · (v_target − v) + ε_v · feedback
        """
        if feedback is None:
            feedback = FeedbackSignal()

        fb = feedback.total
        new_c = []
        for i, (c, ct) in enumerate(zip(state.constraints, target_constraints)):
            eps = state.epsilon_constraint[i] if i < len(state.epsilon_constraint) else 0.0
            dc = self.alpha * (ct - c) + eps * fb
            new_c.append(max(0.0, min(1.0, c + dc * self.dt)))

        new_v = []
        for i, (v, vt) in enumerate(zip(state.valuations, target_valuations)):
            eps = state.epsilon_valuation[i] if i < len(state.epsilon_valuation) else 0.0
            dv = self.beta * (vt - v) + eps * fb
            new_v.append(max(0.0, min(1.0, v + dv * self.dt)))

        return DynamicsState(
            t=state.t + self.dt,
            constraints=new_c,
            valuations=new_v,
            epsilon_constraint=state.epsilon_constraint,
            epsilon_valuation=state.epsilon_valuation,
        )

    def simulate(
        self,
        initial: DynamicsState,
        target_constraints: List[float],
        target_valuations: List[float],
        duration: float = 1.0,
        feedback: Optional[FeedbackSignal] = None,
    ) -> List[DynamicsState]:
        """
        Simulate dynamics for a given duration.
        Returns list of states at each time step.
        """
        steps = int(duration / self.dt)
        trajectory = [initial]
        state = initial

        for _ in range(steps):
            state = self.step(state, target_constraints, target_valuations, feedback)
            trajectory.append(state)

        return trajectory

    def compute_jacobian(
        self,
        state: DynamicsState,
        target_constraints: List[float],
        target_valuations: List[float],
    ) -> List[List[float]]:
        """
        Numerical Jacobian of the dynamics around current state.

        For the linear system ∂c/∂t = α(c_t − c), the Jacobian
        is simply −αI for constraints and −βI for valuations (diagonal).
        """
        n_c = len(state.constraints)
        n_v = len(state.valuations)
        n = n_c + n_v

        J = [[0.0] * n for _ in range(n)]

        # Constraint block: −α on diagonal
        for i in range(n_c):
            J[i][i] = -self.alpha

        # Valuation block: −β on diagonal
        for i in range(n_v):
            J[n_c + i][n_c + i] = -self.beta

        return J

    def check_stability(
        self,
        state: DynamicsState,
        target_constraints: List[float],
        target_valuations: List[float],
    ) -> Tuple[bool, float]:
        """
        Check κ_loop < stability_threshold.

        For diagonal Jacobian, κ_loop = max(|eigenvalues| × dt).
        Eigenvalues are simply the diagonal entries.

        Returns:
            (is_stable, kappa_loop)
        """
        J = self.compute_jacobian(state, target_constraints, target_valuations)

        # For diagonal system, eigenvalues = diagonal entries
        eigenvalues = [J[i][i] for i in range(len(J))]
        max_eigenvalue = max(abs(e) for e in eigenvalues)

        kappa_loop = max_eigenvalue * self.dt
        is_stable = kappa_loop < self.stability_threshold

        return is_stable, kappa_loop

    def has_converged(
        self,
        state: DynamicsState,
        target_constraints: List[float],
        target_valuations: List[float],
        tolerance: float = 0.01,
    ) -> bool:
        """Check if state has converged to target within tolerance."""
        for c, ct in zip(state.constraints, target_constraints):
            if abs(c - ct) > tolerance:
                return False
        for v, vt in zip(state.valuations, target_valuations):
            if abs(v - vt) > tolerance:
                return False
        return True


# ══════════════════════════════════════════════════════════════════
# R2.4: Coupling Matrices & CVADynamicsEngine
# ══════════════════════════════════════════════════════════════════

import numpy as np


def phi(x: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    """Soft ReLU activation function.

    φ(x) = log(1 + exp(αx)) / α

    Properties:
      - Smooth (infinitely differentiable)
      - Near-ReLU behavior for large α
      - φ'(x) = sigmoid(αx)
      - φ(0) = log(2) / α ≈ 0.69

    Args:
        x: Input array or scalar
        alpha: Steepness parameter (default 1.0)

    Returns:
        Activated output, same shape as x
    """
    x = np.asarray(x, dtype=float)
    return np.log(1.0 + np.exp(alpha * np.clip(x, -20, 20))) / alpha


def phi_prime(x: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    """Derivative of soft ReLU: φ'(x) = sigmoid(αx) = 1/(1+exp(-αx))."""
    x = np.asarray(x, dtype=float)
    return 1.0 / (1.0 + np.exp(-alpha * np.clip(x, -20, 20)))


@dataclass
class CoupledDynamicsState:
    """State of the full 17-dim coupled constraint-valuation system.

    Extension of DynamicsState for use with CVADynamicsEngine.
    Uses numpy arrays for efficient matrix operations.
    """
    constraints: np.ndarray = field(default_factory=lambda: np.full(8, 0.5))
    valuations: np.ndarray = field(default_factory=lambda: np.full(9, 0.5))
    constraint_target: np.ndarray = field(default_factory=lambda: np.full(8, 0.5))
    valuation_target: np.ndarray = field(default_factory=lambda: np.full(9, 0.5))
    dt: float = 0.01
    time: float = 0.0

    def __post_init__(self):
        self.constraints = np.asarray(self.constraints, dtype=float)
        self.valuations = np.asarray(self.valuations, dtype=float)
        self.constraint_target = np.asarray(self.constraint_target, dtype=float)
        self.valuation_target = np.asarray(self.valuation_target, dtype=float)

    @property
    def full_state(self) -> np.ndarray:
        """Combined [17] state vector [c, v]."""
        return np.concatenate([self.constraints, self.valuations])


@dataclass
class CVACouplingMatrices:
    """Coupling matrices for constraint-valuation dynamics.

    The coupled system uses four matrices:
      K_cc [8×8]: constraint←constraint coupling
      K_cv [8×9]: constraint←valuation coupling
      K_vc [9×8]: valuation←constraint coupling
      K_vv [9×9]: valuation←valuation coupling

    Coupling strength κ_loop should be < 0.1 for biological plausibility.
    """
    K_cc: np.ndarray  # [8, 8]
    K_cv: np.ndarray  # [8, 9]
    K_vc: np.ndarray  # [9, 8]
    K_vv: np.ndarray  # [9, 9]

    @classmethod
    def default(cls) -> "CVACouplingMatrices":
        """Default weak coupling, biologically plausible (κ_loop ≈ 0.038)."""
        rng = np.random.RandomState(seed=42)
        K_cc = np.eye(8) * -0.1
        K_cv = np.zeros((8, 9))
        K_vc = rng.randn(9, 8) * 0.02
        K_vv = np.eye(9) * -0.05 + rng.randn(9, 9) * 0.01
        return cls(K_cc=K_cc, K_cv=K_cv, K_vc=K_vc, K_vv=K_vv)

    @classmethod
    def from_dict(cls, data: Dict) -> "CVACouplingMatrices":
        """Deserialize from dictionary."""
        return cls(
            K_cc=np.array(data["K_cc"]),
            K_cv=np.array(data["K_cv"]),
            K_vc=np.array(data["K_vc"]),
            K_vv=np.array(data["K_vv"]),
        )

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "K_cc": self.K_cc.tolist(),
            "K_cv": self.K_cv.tolist(),
            "K_vc": self.K_vc.tolist(),
            "K_vv": self.K_vv.tolist(),
        }

    def estimate_coupling_strength(self) -> float:
        """Estimate κ_loop from off-diagonal coupling (Frobenius norm)."""
        off_diag = (
            np.linalg.norm(self.K_cv, "fro")
            + np.linalg.norm(self.K_vc, "fro")
        ) / 2.0
        return float(off_diag)


class CVADynamicsEngine:
    """Coupled constraint-valuation dynamics with full 17×17 ODE system.

    Implements:
      dc/dt = -D_c(c − c_target) + φ(K_cc·c + K_cv·v)
      dv/dt = -D_v(v − v_target) + φ(K_vv·v + K_vc·c)

    where φ is soft ReLU and D_c, D_v are dissipation matrices.

    Reference: AG_PHASE2_REMEDIATION R2.4
    """

    CONSTRAINT_NAMES = [
        "spatial_containment", "force_dynamics", "stability", "safety",
        "attraction", "repulsion", "support", "resistance",
    ]
    VALUATION_NAMES = [
        "autonomy", "competence", "relatedness", "novelty", "beauty",
        "meaning", "security", "justice", "flourishing",
    ]

    def __init__(
        self,
        dissipation_c: Optional[np.ndarray] = None,
        dissipation_v: Optional[np.ndarray] = None,
        dt: float = 0.01,
    ):
        self.dt = dt
        self.dissipation_c = dissipation_c if dissipation_c is not None else np.full(8, 0.3)
        self.dissipation_v = dissipation_v if dissipation_v is not None else np.full(9, 0.2)

    def step(
        self,
        state: CoupledDynamicsState,
        coupling: CVACouplingMatrices,
        phi_alpha: float = 1.0,
    ) -> CoupledDynamicsState:
        """Single Euler integration step.

        dc/dt = -D_c(c − c_target) + φ(K_cc·c + K_cv·v)
        dv/dt = -D_v(v − v_target) + φ(K_vv·v + K_vc·c)
        """
        D_c = np.diag(self.dissipation_c)
        D_v = np.diag(self.dissipation_v)

        drift_c = -D_c @ (state.constraints - state.constraint_target)
        coupling_c = phi(
            coupling.K_cc @ state.constraints + coupling.K_cv @ state.valuations,
            alpha=phi_alpha,
        )
        dc_dt = drift_c + coupling_c

        drift_v = -D_v @ (state.valuations - state.valuation_target)
        coupling_v = phi(
            coupling.K_vv @ state.valuations + coupling.K_vc @ state.constraints,
            alpha=phi_alpha,
        )
        dv_dt = drift_v + coupling_v

        return CoupledDynamicsState(
            constraints=state.constraints + self.dt * dc_dt,
            valuations=state.valuations + self.dt * dv_dt,
            constraint_target=state.constraint_target,
            valuation_target=state.valuation_target,
            dt=self.dt,
            time=state.time + self.dt,
        )

    def run_to_convergence(
        self,
        initial: CoupledDynamicsState,
        coupling: CVACouplingMatrices,
        max_steps: int = 10000,
        tolerance: float = 1e-4,
        phi_alpha: float = 1.0,
    ) -> Tuple[CoupledDynamicsState, List[CoupledDynamicsState]]:
        """Run dynamics until convergence. Returns (final_state, trajectory)."""
        trajectory = [initial]
        state = initial

        for _ in range(max_steps):
            new_state = self.step(state, coupling, phi_alpha)
            trajectory.append(new_state)

            dc = np.linalg.norm(new_state.constraints - state.constraints)
            dv = np.linalg.norm(new_state.valuations - state.valuations)
            if dc < tolerance and dv < tolerance:
                return new_state, trajectory

            state = new_state

        return state, trajectory

    # ── R2.5: Lyapunov Analysis ──────────────────────────────────

    def _dynamics_derivative(
        self,
        state: CoupledDynamicsState,
        coupling: CVACouplingMatrices,
        phi_alpha: float = 1.0,
    ) -> np.ndarray:
        """Compute [dc/dt, dv/dt] as single [17] vector."""
        D_c = np.diag(self.dissipation_c)
        D_v = np.diag(self.dissipation_v)

        dc_dt = -D_c @ (state.constraints - state.constraint_target) + phi(
            coupling.K_cc @ state.constraints + coupling.K_cv @ state.valuations,
            alpha=phi_alpha,
        )
        dv_dt = -D_v @ (state.valuations - state.valuation_target) + phi(
            coupling.K_vv @ state.valuations + coupling.K_vc @ state.constraints,
            alpha=phi_alpha,
        )
        return np.concatenate([dc_dt, dv_dt])

    def compute_full_jacobian(
        self,
        state: CoupledDynamicsState,
        coupling: CVACouplingMatrices,
        phi_alpha: float = 1.0,
        h: float = 1e-5,
    ) -> np.ndarray:
        """Compute full 17×17 Jacobian via central finite differences.

        J[i,j] = ∂(ẋ_i)/∂(x_j) where x = [c, v]
        """
        x = np.concatenate([state.constraints, state.valuations])
        J = np.zeros((17, 17))

        for j in range(17):
            x_plus = x.copy()
            x_plus[j] += h
            x_minus = x.copy()
            x_minus[j] -= h

            s_plus = CoupledDynamicsState(
                constraints=x_plus[:8], valuations=x_plus[8:],
                constraint_target=state.constraint_target,
                valuation_target=state.valuation_target, dt=self.dt,
            )
            s_minus = CoupledDynamicsState(
                constraints=x_minus[:8], valuations=x_minus[8:],
                constraint_target=state.constraint_target,
                valuation_target=state.valuation_target, dt=self.dt,
            )

            f_plus = self._dynamics_derivative(s_plus, coupling, phi_alpha)
            f_minus = self._dynamics_derivative(s_minus, coupling, phi_alpha)
            J[:, j] = (f_plus - f_minus) / (2 * h)

        return J

    def check_attractor_stability(
        self,
        fixed_point: np.ndarray,
        coupling: CVACouplingMatrices,
        phi_alpha: float = 1.0,
    ) -> Dict:
        """Analyze stability of a fixed point via eigenvalue decomposition.

        Returns dict with eigenvalues, max_real_eigenvalue, is_stable,
        kappa_loop, and dominance_profile.
        """
        state = CoupledDynamicsState(
            constraints=fixed_point[:8],
            valuations=fixed_point[8:],
            constraint_target=fixed_point[:8],
            valuation_target=fixed_point[8:],
            dt=self.dt,
        )

        J = self.compute_full_jacobian(state, coupling, phi_alpha)
        eigenvalues = np.linalg.eigvals(J)
        max_real_eig = float(np.max(np.real(eigenvalues)))
        kappa_loop = float(np.abs(max_real_eig)) * self.dt

        # Dominance analysis
        idx = np.argmax(np.abs(np.real(eigenvalues)))
        _, eigvecs = np.linalg.eig(J)
        dom_vec = eigvecs[:, idx].real
        c_mag = float(np.linalg.norm(dom_vec[:8]))
        v_mag = float(np.linalg.norm(dom_vec[8:]))

        return {
            "eigenvalues": eigenvalues,
            "max_real_eigenvalue": max_real_eig,
            "is_stable": max_real_eig < 0,
            "kappa_loop": kappa_loop,
            "dominance_profile": {
                "constraint_magnitude": c_mag,
                "valuation_magnitude": v_mag,
                "constraint_dominates": c_mag > v_mag,
            },
        }

    def find_fixed_points(
        self,
        coupling: CVACouplingMatrices,
        num_initial: int = 20,
        max_steps: int = 10000,
        tolerance: float = 1e-5,
        phi_alpha: float = 1.0,
    ) -> List[Tuple[np.ndarray, Dict]]:
        """Find fixed points by running from random initial conditions.

        Returns list of (fixed_point [17], stability_analysis) tuples.
        """
        rng = np.random.RandomState(seed=123)
        fixed_points: List[Tuple[np.ndarray, Dict]] = []

        for _ in range(num_initial):
            c0 = rng.randn(8) * 0.1
            v0 = rng.randn(9) * 0.1
            state = CoupledDynamicsState(
                constraints=c0, valuations=v0,
                constraint_target=c0, valuation_target=v0, dt=self.dt,
            )

            final, _ = self.run_to_convergence(
                state, coupling, max_steps=max_steps,
                tolerance=tolerance, phi_alpha=phi_alpha,
            )

            fp = np.concatenate([final.constraints, final.valuations])
            is_new = all(
                np.linalg.norm(fp - existing) > tolerance * 10
                for existing, _ in fixed_points
            )
            if is_new:
                stab = self.check_attractor_stability(fp, coupling, phi_alpha)
                fixed_points.append((fp, stab))

        return fixed_points


# ══════════════════════════════════════════════════════════════════
# R2.2: Decomposed Feedback Engine
# ══════════════════════════════════════════════════════════════════

class DecomposedFeedbackEngine:
    """Computes three independent feedback signals with distinct timescales.

    Three pathways:
      ε_attn:  Sampling bias toward constraint-informative regions
               τ ≈ 0.4s (fastest, dorsal frontoparietal attention network)

      ε_prec:  Gain modulation on valuation error
               τ ≈ 1.0s (medium, V1/V2 gain modulation circuits)

      ε_prior: Expectation shift from cultural/learned priors
               τ ≈ 3.0s (slowest, mPFC-hippocampal systems)

    Reference: AG_PHASE2_REMEDIATION R2.2 (Chat's Q2: Nelson/Attention Dynamics)
    """

    TAU_ATTENTION: float = 0.4
    TAU_PRECISION: float = 1.0
    TAU_PRIOR: float = 3.0

    CONSTRAINT_NAMES = [
        "spatial_containment", "force_dynamics", "stability", "safety",
        "attraction", "repulsion", "support", "resistance",
    ]

    def compute_attention_error(
        self,
        constraint_dist: "ConstraintDistribution",
        valuation_state: np.ndarray,
        activity_frame: str,
        gaze_weights: Optional[np.ndarray] = None,
    ) -> float:
        """Attention error: sampling bias toward informative regions.

        If gaze_weights provided: ε_attn = dot(gaze, precision)
        Otherwise: ε_attn = RMS(precision)

        Returns: scalar float ≥ 0
        """
        from src.services.cva_constraint_engine import ConstraintDistribution
        prec = np.asarray(constraint_dist.precision, dtype=float)
        if gaze_weights is not None:
            gaze = np.asarray(gaze_weights, dtype=float)
            return float(np.dot(gaze, prec))
        else:
            return float(np.sqrt(np.mean(prec ** 2)))

    def compute_precision_error(
        self,
        constraint_history: List[np.ndarray],
        activity_frame: str,
        psi: Optional[object] = None,
    ) -> float:
        """Precision error: mismatch between observed and expected variance.

        ε_prec = ||observed_var − expected_var||_2

        Returns: scalar float ≥ 0
        """
        if len(constraint_history) < 2:
            return 0.0

        from src.services.cva_constraint_engine import FRAME_PRECISIONS
        samples = np.array(constraint_history)
        observed_var = np.var(samples, axis=0)

        expected_prec = np.array(
            FRAME_PRECISIONS.get(activity_frame, [1.0] * 8)
        )
        expected_var = 1.0 / (expected_prec + 1e-8)

        return float(np.linalg.norm(observed_var - expected_var))

    def compute_prior_error(
        self,
        constraint_state: np.ndarray,
        valuation_state: np.ndarray,
        activity_frame: str,
        psi: Optional[object] = None,
        cultural_baseline: Optional[np.ndarray] = None,
    ) -> float:
        """Prior error: deviation from cultural/learned expectations.

        ε_prior = ||valuation − cultural_baseline||_2

        Returns: scalar float ≥ 0
        """
        if cultural_baseline is None:
            return 0.0
        val = np.asarray(valuation_state, dtype=float)
        base = np.asarray(cultural_baseline, dtype=float)
        return float(np.linalg.norm(val - base))

    def compose_feedback(
        self,
        e_attn: float,
        e_prec: float,
        e_prior: float,
        dt: float = 0.01,
    ) -> "DecomposedFeedback":
        """Compose three signals with timescale-specific exponential decay.

        ε_x(t+dt) = ε_x(t) · exp(−dt/τ_x)

        Attention decays fastest; prior decays slowest.
        """
        return DecomposedFeedback(
            epsilon_attention=e_attn * np.exp(-dt / self.TAU_ATTENTION),
            epsilon_precision=e_prec * np.exp(-dt / self.TAU_PRECISION),
            epsilon_prior=e_prior * np.exp(-dt / self.TAU_PRIOR),
            timescale_attention=self.TAU_ATTENTION,
            timescale_precision=self.TAU_PRECISION,
            timescale_prior=self.TAU_PRIOR,
        )


@dataclass
class DecomposedFeedback:
    """Three-part feedback with distinct neural/temporal timescales.

    Extension of FeedbackSignal with timescale metadata.
    """
    epsilon_attention: float = 0.0
    epsilon_precision: float = 0.0
    epsilon_prior: float = 0.0
    timescale_attention: float = 0.4
    timescale_precision: float = 1.0
    timescale_prior: float = 3.0

    def total_magnitude(self) -> float:
        """L2 norm of feedback components."""
        return float(np.sqrt(
            self.epsilon_attention ** 2
            + self.epsilon_precision ** 2
            + self.epsilon_prior ** 2
        ))

    def dominance(self) -> str:
        """Which signal dominates?"""
        signals = {
            "attention": self.epsilon_attention,
            "precision": self.epsilon_precision,
            "prior": self.epsilon_prior,
        }
        return max(signals, key=signals.get)
