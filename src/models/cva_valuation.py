"""
cva_valuation.py — CVA Valuation Vector Data Structures
========================================================

Implements the 9-dimensional valuation space with 4 cultural variants:
  1. Western (9D: Safety, Interest, Restoration, Status, Belonging,
     Identity, Autonomy, Competence, Relatedness)
  2. Japanese (9D: replaces Autonomy with Amae; adds Ma)
  3. West African (6D: collapses social dimensions into Àṣà)
  4. Indian (4D: Rasa + Dharma + Belonging + Competence)

Reference: CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE §2.2
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import json
import math


# ──────────────────────────────────────────────────────────────────
# Cultural Variant Enum
# ──────────────────────────────────────────────────────────────────

class CulturalVariant(Enum):
    """Structurally distinct valuation decompositions."""
    WESTERN = "western"
    JAPANESE = "japanese"
    WEST_AFRICAN = "west_african"
    INDIAN = "indian"


# ──────────────────────────────────────────────────────────────────
# Valuation Name Enums
# ──────────────────────────────────────────────────────────────────

class ValuationName(Enum):
    """Universal valuation names (superset across all variants)."""
    SAFETY = "SafetyValue"
    INTEREST = "InterestValue"
    RESTORATION = "RestorationValue"
    STATUS = "StatusValue"
    BELONGING = "BelongingValue"
    IDENTITY_CONGRUENCE = "IdentityCongruenceValue"
    AUTONOMY_SUPPORT = "AutonomySupportValue"
    COMPETENCE_SUPPORT = "CompetenceSupportValue"
    RELATEDNESS_SUPPORT = "RelatednessSupportValue"
    # Cultural-specific valuations
    AMAE = "AmaeValue"             # Japanese: secure dependence
    MA = "MaValue"                 # Japanese: emptiness/liminality
    ASA = "ÀṣàValue"              # West African: collective dignity
    RASA = "RasaValue"             # Indian: holistic aesthetic-emotional
    DHARMA = "DharmaValue"         # Indian: cosmic/social rightness


# ──────────────────────────────────────────────────────────────────
# Valuation Vector Base
# ──────────────────────────────────────────────────────────────────

@dataclass
class CVAValuationVector:
    """
    v(ψ) = V(c; g(ψ), τ(ψ), κ(ψ_culture, ψ_neuro))

    Culture-aware valuation vector. The dimension count and meaning
    of each axis depend on the cultural variant.

    Western:      9D (all orthogonal)
    Japanese:     9D (Autonomy → Amae; + Ma auxiliary)
    West African: 6D (social dims → Àṣà)
    Indian:       4D (Rasa + Dharma + Belonging + Competence)
    """
    values: Dict[str, float] = field(default_factory=dict)
    variant: CulturalVariant = CulturalVariant.WESTERN
    gains: Dict[str, float] = field(default_factory=dict)
    timescales: Dict[str, float] = field(default_factory=dict)

    # Metadata
    subject_id: Optional[str] = None
    scene_id: Optional[str] = None

    def __post_init__(self):
        # If values empty, initialize from variant defaults
        if not self.values:
            self.values = self._default_values()
        # Clamp all values to [0, 1]
        self.values = {
            k: max(0.0, min(1.0, float(v)))
            for k, v in self.values.items()
        }

    def _default_values(self) -> Dict[str, float]:
        """Default valuation vector for this cultural variant."""
        if self.variant == CulturalVariant.WESTERN:
            return {
                "SafetyValue": 0.5,
                "InterestValue": 0.5,
                "RestorationValue": 0.5,
                "StatusValue": 0.5,
                "BelongingValue": 0.5,
                "IdentityCongruenceValue": 0.5,
                "AutonomySupportValue": 0.5,
                "CompetenceSupportValue": 0.5,
                "RelatednessSupportValue": 0.5,
            }
        elif self.variant == CulturalVariant.JAPANESE:
            return {
                "SafetyValue": 0.5,
                "InterestValue": 0.5,
                "RestorationValue": 0.5,
                "StatusValue": 0.5,
                "BelongingValue": 0.5,
                "IdentityCongruenceValue": 0.5,
                "AmaeValue": 0.5,         # replaces AutonomySupportValue
                "CompetenceSupportValue": 0.5,
                "RelatednessSupportValue": 0.5,
                "MaValue": 0.5,            # auxiliary: emptiness/liminality
            }
        elif self.variant == CulturalVariant.WEST_AFRICAN:
            return {
                "SafetyValue": 0.5,
                "InterestValue": 0.5,
                "RestorationValue": 0.5,
                "ÀṣàValue": 0.5,          # collapsed social/identity/status
                "AutonomySupportValue": 0.5,
                "CompetenceSupportValue": 0.5,
            }
        elif self.variant == CulturalVariant.INDIAN:
            return {
                "RasaValue": 0.5,          # holistic aesthetic-emotional
                "DharmaValue": 0.5,        # cosmic/social rightness
                "BelongingValue": 0.5,
                "CompetenceSupportValue": 0.5,
            }
        return {}

    @property
    def dimensionality(self) -> int:
        """Number of valuation dimensions for this variant."""
        return len(self.values)

    def as_vector(self) -> List[float]:
        """Ordered list of values."""
        return list(self.values.values())

    def as_dict(self) -> Dict[str, float]:
        """Name → value mapping."""
        return dict(self.values)

    def dimension_names(self) -> List[str]:
        """Ordered list of dimension names."""
        return list(self.values.keys())

    def distance(self, other: "CVAValuationVector") -> float:
        """
        Euclidean distance. Only compares shared dimensions.
        Warns if variants differ (cross-cultural comparison is
        epistemically problematic per Barrett et al., 2016).
        """
        shared_keys = set(self.values.keys()) & set(other.values.keys())
        if not shared_keys:
            return float("inf")
        return math.sqrt(sum(
            (self.values[k] - other.values[k]) ** 2 for k in shared_keys
        ))

    def net_valuation(self) -> float:
        """Sum of all valuations (simple utility proxy)."""
        return sum(self.values.values())

    def dominant_valuation(self) -> str:
        """Name of the highest-valued dimension."""
        return max(self.values, key=self.values.get)

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            "values": self.values,
            "variant": self.variant.value,
            "gains": self.gains,
            "timescales": self.timescales,
            "subject_id": self.subject_id,
            "scene_id": self.scene_id,
        })

    @classmethod
    def from_json(cls, data: str | dict) -> "CVAValuationVector":
        """Deserialize from JSON."""
        if isinstance(data, str):
            data = json.loads(data)
        return cls(
            values=data.get("values", {}),
            variant=CulturalVariant(data.get("variant", "western")),
            gains=data.get("gains", {}),
            timescales=data.get("timescales", {}),
            subject_id=data.get("subject_id"),
            scene_id=data.get("scene_id"),
        )

    def __getitem__(self, name: str) -> float:
        return self.values[name]

    def __setitem__(self, name: str, value: float):
        self.values[name] = max(0.0, min(1.0, float(value)))


# ──────────────────────────────────────────────────────────────────
# Neurotype Valuation Modifiers
# ──────────────────────────────────────────────────────────────────

@dataclass
class NeurotypeValuationModifier:
    """
    Neurotype-specific valuation modulation from CVA spec §2.2.2.

    Applies multiplicative gain and additive bias to specific
    valuation dimensions.
    """
    neurotype: str
    gain_modifiers: Dict[str, float] = field(default_factory=dict)
    bias_modifiers: Dict[str, float] = field(default_factory=dict)
    description: str = ""

    def apply(self, valuation: CVAValuationVector) -> CVAValuationVector:
        """Return a new valuation vector with modifiers applied."""
        new_values = dict(valuation.values)
        for dim, gain in self.gain_modifiers.items():
            if dim in new_values:
                new_values[dim] = max(0.0, min(1.0, new_values[dim] * gain))
        for dim, bias in self.bias_modifiers.items():
            if dim in new_values:
                new_values[dim] = max(0.0, min(1.0, new_values[dim] + bias))
        return CVAValuationVector(
            values=new_values,
            variant=valuation.variant,
            gains=valuation.gains,
            timescales=valuation.timescales,
            subject_id=valuation.subject_id,
            scene_id=valuation.scene_id,
        )


# Pre-defined neurotype modifiers (from spec §3.1–3.10)
NEUROTYPE_MODIFIERS: Dict[str, NeurotypeValuationModifier] = {
    "ptsd": NeurotypeValuationModifier(
        neurotype="ptsd",
        gain_modifiers={
            "SafetyValue": 2.5,      # 5× amplification for threats
            "InterestValue": 0.3,     # suppressed globally
            "RestorationValue": 0.5,  # inaccessible without safety
        },
        description="PTSD: safety-dominated, interest suppressed (van der Kolk, 2014)",
    ),
    "asd": NeurotypeValuationModifier(
        neurotype="asd",
        gain_modifiers={
            "CompetenceSupportValue": 1.5,    # mastery prioritized
            "RelatednessSupportValue": 0.6,   # social affiliation reduced
            "BelongingValue": 0.7,
        },
        description="ASD: mastery over social affiliation (Markram & Markram, 2010)",
    ),
    "adhd": NeurotypeValuationModifier(
        neurotype="adhd",
        gain_modifiers={
            "InterestValue": 3.5,             # 3-4× typical
            "CompetenceSupportValue": 1.3,    # with immediate feedback
        },
        description="ADHD: novelty-seeking, extreme temporal discounting (Volkow, 2009)",
    ),
    "depression": NeurotypeValuationModifier(
        neurotype="depression",
        gain_modifiers={
            "InterestValue": 0.4,
            "RestorationValue": 0.4,
            "CompetenceSupportValue": 0.5,
        },
        description="Depression: anhedonic flattening (Mayberg, 2003)",
    ),
    "anxiety": NeurotypeValuationModifier(
        neurotype="anxiety",
        gain_modifiers={
            "SafetyValue": 2.5,
        },
        bias_modifiers={
            "SafetyValue": 0.2,
        },
        description="Anxiety: safety-elevated, control reduced (Stein & Stein, 2008)",
    ),
    "bipolar_manic": NeurotypeValuationModifier(
        neurotype="bipolar_manic",
        gain_modifiers={
            "InterestValue": 3.0,
            "StatusValue": 2.5,
            "SafetyValue": 0.5,  # risk-taking
        },
        description="Bipolar manic: stimulation-seeking, grandiosity (Phillips & Kupfer, 2013)",
    ),
    "bipolar_depressed": NeurotypeValuationModifier(
        neurotype="bipolar_depressed",
        gain_modifiers={
            "InterestValue": 0.4,
            "RestorationValue": 0.4,
            "CompetenceSupportValue": 0.5,
        },
        description="Bipolar depressed: same as unipolar depression",
    ),
    "alzheimers": NeurotypeValuationModifier(
        neurotype="alzheimers",
        gain_modifiers={
            "SafetyValue": 2.0,
            "CompetenceSupportValue": 0.3,
        },
        bias_modifiers={
            "BelongingValue": 0.2,
        },
        description="Alzheimer's: familiarity-dependent, control near zero (Selkoe, 2002)",
    ),
    "gifted": NeurotypeValuationModifier(
        neurotype="gifted",
        gain_modifiers={
            "InterestValue": 1.5,
            "CompetenceSupportValue": 1.5,
        },
        description="Gifted: challenge-seeking, boredom aversion (Winner, 1996)",
    ),
    "older_adult": NeurotypeValuationModifier(
        neurotype="older_adult",
        gain_modifiers={
            "SafetyValue": 1.75,
        },
        description="Older adults: elevated safety, reduced control efficacy (Owsley, 2011)",
    ),
}
