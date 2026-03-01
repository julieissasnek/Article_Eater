"""
cva_beauty.py — Beauty Readout Models
=======================================

Implements B = L(v) — four beauty readout models that map
valuation vectors to scalar beauty judgments:

  1. Linear:     B = w · v
  2. Quadratic:  B = v^T Q v + w · v
  3. Neural:     B = MLP(v)
  4. Rasa:       B = max(rasa_i(v))  (culturally-informed)

Reference: CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE (beauty readout)
AG_ASSIGNMENT Phase 2, Task 2.8
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import math

from src.models.cva_valuation import CVAValuationVector


class BeautyModelType(Enum):
    """Available beauty readout models."""
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    NEURAL = "neural"
    RASA = "rasa"


class BeautyReadout(ABC):
    """Abstract base for beauty readout models B = L(v)."""

    @abstractmethod
    def compute(self, valuation: CVAValuationVector) -> float:
        """Compute beauty score from valuation vector. Returns [0, 1]."""
        ...


@dataclass
class LinearBeautyReadout(BeautyReadout):
    """
    B = w · v (linear combination)

    Simplest model: each valuation dimension contributes proportionally.
    """
    weights: Dict[str, float] = field(default_factory=lambda: {
        "SafetyValue": 0.10,
        "InterestValue": 0.20,
        "RestorationValue": 0.10,
        "StatusValue": 0.05,
        "BelongingValue": 0.10,
        "IdentityCongruenceValue": 0.10,
        "AutonomySupportValue": 0.10,
        "CompetenceSupportValue": 0.15,
        "RelatednessSupportValue": 0.10,
    })

    def compute(self, valuation: CVAValuationVector) -> float:
        raw = sum(
            valuation.values.get(name, 0.0) * w
            for name, w in self.weights.items()
        )
        return max(0.0, min(1.0, raw))


@dataclass
class QuadraticBeautyReadout(BeautyReadout):
    """
    B = v^T Q v + w · v (captures interactions between valuations)

    The quadratic form allows modeling of synergies (e.g., Safety × Belonging)
    and antagonisms (e.g., Interest vs. Safety in exploration-averse subjects).
    """
    linear_weights: Dict[str, float] = field(default_factory=lambda: {
        "SafetyValue": 0.08,
        "InterestValue": 0.18,
        "RestorationValue": 0.08,
        "CompetenceSupportValue": 0.12,
    })
    # Interaction terms: (dim1, dim2) → weight
    interactions: Dict[tuple, float] = field(default_factory=lambda: {
        ("SafetyValue", "BelongingValue"): 0.15,
        ("InterestValue", "CompetenceSupportValue"): 0.20,
        ("RestorationValue", "SafetyValue"): 0.10,
    })

    def compute(self, valuation: CVAValuationVector) -> float:
        # Linear term
        linear = sum(
            valuation.values.get(n, 0.0) * w
            for n, w in self.linear_weights.items()
        )
        # Quadratic interaction term
        quad = sum(
            valuation.values.get(d1, 0.0) * valuation.values.get(d2, 0.0) * w
            for (d1, d2), w in self.interactions.items()
        )
        raw = linear + quad
        return max(0.0, min(1.0, raw))


@dataclass
class NeuralBeautyReadout(BeautyReadout):
    """
    B = MLP(v) — simple 2-layer neural approximation.

    Uses tanh activation in hidden layer, sigmoid output.
    Weights are hand-initialized from domain knowledge;
    intended to be fine-tuned from empirical data.
    """
    hidden_size: int = 6

    def __post_init__(self):
        # Initialize weights for a simple 9→6→1 network
        # These are placeholder weights; would be trained from data
        self._w1: List[List[float]] = [
            [0.1, 0.3, 0.1, 0.05, 0.1, 0.1, 0.1, 0.15, 0.1],
            [0.1, 0.1, 0.3, 0.05, 0.2, 0.1, 0.1, 0.1, 0.2],
            [0.2, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.2, 0.2, 0.1],
            [0.1, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.1, 0.1],
        ]
        self._b1 = [-0.3] * self.hidden_size
        self._w2 = [0.2, 0.25, 0.15, 0.15, 0.15, 0.1]
        self._b2 = -0.3

    def compute(self, valuation: CVAValuationVector) -> float:
        x = valuation.as_vector()
        # Pad or truncate to 9
        while len(x) < 9:
            x.append(0.5)
        x = x[:9]

        # Hidden layer: tanh(W1 @ x + b1)
        hidden = []
        for i in range(self.hidden_size):
            z = sum(self._w1[i][j] * x[j] for j in range(9)) + self._b1[i]
            hidden.append(math.tanh(z))

        # Output: sigmoid(w2 · hidden + b2)
        z_out = sum(self._w2[i] * hidden[i] for i in range(self.hidden_size)) + self._b2
        return 1.0 / (1.0 + math.exp(-z_out))


@dataclass
class RasaBeautyReadout(BeautyReadout):
    """
    B = max(rasa_i(v)) — holistic aesthetic-emotional states.

    Nine rasa (from Natyashastra), each as a non-linear function
    of the valuation vector. Beauty = strongest active rasa.

    This model is culturally-informed: it captures the Indian
    aesthetic insight that beauty is not a single dimension
    but the intensity of the dominant emotional-aesthetic state.
    """
    # Rasa configurations: each rasa activates from specific
    # valuation patterns (simplified linear thresholds)
    rasa_configs: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "shringara": {  # Love/Beauty
            "BelongingValue": 0.3, "RelatednessSupportValue": 0.3,
            "IdentityCongruenceValue": 0.2, "InterestValue": 0.2,
        },
        "hasya": {  # Joy/Humor
            "InterestValue": 0.4, "CompetenceSupportValue": 0.3,
            "SafetyValue": 0.2, "BelongingValue": 0.1,
        },
        "karuna": {  # Compassion
            "BelongingValue": 0.3, "RelatednessSupportValue": 0.3,
            "SafetyValue": -0.2, "IdentityCongruenceValue": 0.2,
        },
        "raudra": {  # Wrath/Power
            "AutonomySupportValue": 0.3, "CompetenceSupportValue": 0.3,
            "StatusValue": 0.2, "SafetyValue": -0.2,
        },
        "veera": {  # Heroism
            "CompetenceSupportValue": 0.3, "AutonomySupportValue": 0.3,
            "StatusValue": 0.2, "InterestValue": 0.2,
        },
        "bhayanaka": {  # Terror/Awe
            "SafetyValue": -0.3, "InterestValue": 0.3,
            "IdentityCongruenceValue": -0.2,
        },
        "bibhatsa": {  # Disgust
            "SafetyValue": -0.3, "InterestValue": -0.2,
            "RestorationValue": -0.3,
        },
        "adbhuta": {  # Wonder
            "InterestValue": 0.4, "CompetenceSupportValue": 0.2,
            "IdentityCongruenceValue": 0.2,
        },
        "shanta": {  # Peace/Serenity
            "RestorationValue": 0.4, "SafetyValue": 0.3,
            "BelongingValue": 0.2,
        },
    })

    def compute(self, valuation: CVAValuationVector) -> float:
        rasa_activations = {}
        for rasa_name, weights in self.rasa_configs.items():
            raw = sum(
                valuation.values.get(name, 0.5) * w
                for name, w in weights.items()
            )
            # Sigmoid activation
            rasa_activations[rasa_name] = 1.0 / (1.0 + math.exp(-4.0 * raw))

        # Beauty = max rasa activation
        return max(rasa_activations.values()) if rasa_activations else 0.5

    def dominant_rasa(self, valuation: CVAValuationVector) -> str:
        """Return the name of the dominant rasa."""
        best_name = "shanta"
        best_val = 0.0
        for rasa_name, weights in self.rasa_configs.items():
            raw = sum(
                valuation.values.get(name, 0.5) * w
                for name, w in weights.items()
            )
            activation = 1.0 / (1.0 + math.exp(-4.0 * raw))
            if activation > best_val:
                best_val = activation
                best_name = rasa_name
        return best_name


# Factory
def create_beauty_readout(model_type: BeautyModelType) -> BeautyReadout:
    """Factory for beauty readout models."""
    models = {
        BeautyModelType.LINEAR: LinearBeautyReadout,
        BeautyModelType.QUADRATIC: QuadraticBeautyReadout,
        BeautyModelType.NEURAL: NeuralBeautyReadout,
        BeautyModelType.RASA: RasaBeautyReadout,
    }
    return models[model_type]()
