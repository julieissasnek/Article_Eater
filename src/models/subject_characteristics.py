"""
subject_characteristics.py — ψ Parameter Space for CVA
=======================================================

Implements the structured subject-characteristics parameter space:
    ψ = {ψ_culture, ψ_neuro, ψ_dev, ψ_exp, ψ_state, ψ_trait}

Each component captures a different dimension of individual
differences that modulate constraint perception and valuation.

Reference: CVA_SUBJECT_CHARACTERISTICS_ARCHITECTURE §1.1
ADR-001: Extension layer — new file, no existing code modified.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional
import json


# ──────────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────────

class SelfConstrual(Enum):
    """κ_self: self-construal axis (Markus & Kitayama, 1991)."""
    INDEPENDENT = "independent"         # Western individualist
    INTERDEPENDENT = "interdependent"   # East Asian
    RELATIONAL = "relational"           # West African
    DHARMIC = "dharmic"                 # Indian/South Asian


class SocialStructure(Enum):
    """κ_social: social structure preference."""
    EGALITARIAN = "egalitarian"
    HIERARCHICAL_SECURE = "hierarchical_secure"
    COLLECTIVE_DIGNITY = "collective_dignity"
    HIERARCHICAL_COSMIC = "hierarchical_cosmic"


class ExpertiseDomain(Enum):
    """e_domain: primary expertise domain."""
    ARCHITECTURE = "architecture"
    VISUAL_ART = "visual_art"
    MUSIC = "music"
    SPATIAL_NAVIGATION = "spatial_navigation"
    SOCIAL = "social"
    GENERAL = "general"
    NONE = "none"


class NeurotypeName(Enum):
    """Named neurotype profiles from spec §3."""
    TYPICAL = "typical"
    PTSD = "ptsd"
    ASD = "asd"
    ADHD = "adhd"
    OLDER_ADULT = "older_adult"
    CHILD_5_8 = "child_5_8"
    CHILD_9_12 = "child_9_12"
    ALZHEIMERS = "alzheimers"
    DEPRESSION = "depression"
    ANXIETY = "anxiety"
    BIPOLAR_MANIC = "bipolar_manic"
    BIPOLAR_DEPRESSED = "bipolar_depressed"
    GIFTED = "gifted"


# ──────────────────────────────────────────────────────────────────
# ψ Components
# ──────────────────────────────────────────────────────────────────

@dataclass
class CulturalContext:
    """
    ψ_culture = {κ_self, κ_social, κ_aesthetics, κ_ecology}

    Cultural values, spatial aesthetics, social norms, ecological history.
    """
    kappa_self: SelfConstrual = SelfConstrual.INDEPENDENT
    kappa_social: SocialStructure = SocialStructure.EGALITARIAN
    kappa_aesthetics: Dict[str, float] = field(default_factory=lambda: {
        "material_density_preference": 0.5,
        "symmetry_preference": 0.5,
        "color_saturation_preference": 0.5,
        "temporal_pacing": 0.5,
        "ornamentation": 0.5,
    })
    kappa_ecology: Dict[str, float] = field(default_factory=lambda: {
        "settlement_density": 0.5,
        "threat_level": 0.3,
        "material_availability": 0.7,
        "climate_adaptation": 0.5,
    })


@dataclass
class NeurotypeProfile:
    """
    ψ_neuro = {ν_sensory, ν_integration, ν_learning, ν_threat, ν_social, ν_reward}

    Atypical neural sensitivities and processing characteristics.
    All ν values in [0, 1] where 0.5 = typical, <0.5 = reduced, >0.5 = heightened.
    """
    name: NeurotypeName = NeurotypeName.TYPICAL
    nu_sensory: float = 0.5        # Sensory thresholds
    nu_integration: float = 0.5    # Multimodal binding speed
    nu_learning: float = 0.5       # Perceptual calibration rate
    nu_threat: float = 0.5         # Threat detection threshold
    nu_social: float = 0.5         # Social salience weighting
    nu_reward: float = 0.5         # Reward sensitivity

    def as_vector(self) -> List[float]:
        return [
            self.nu_sensory, self.nu_integration, self.nu_learning,
            self.nu_threat, self.nu_social, self.nu_reward,
        ]


@dataclass
class DevelopmentalStage:
    """
    ψ_dev = {a, m_visual, m_motor, m_exec, m_social}

    Age-indexed maturation of perceptual and cognitive systems.
    Maturation values in [0, 1] where 1.0 = fully mature.
    """
    age: float = 30.0          # Chronological age (years)
    m_visual: float = 1.0      # Visual development
    m_motor: float = 1.0       # Motor development
    m_exec: float = 1.0        # Executive function
    m_social: float = 1.0      # Theory of mind


@dataclass
class ExperienceProfile:
    """
    ψ_exp = {e_domain, e_years, e_mastery}

    Domain-specific perceptual calibration and expertise.
    """
    domain: ExpertiseDomain = ExpertiseDomain.GENERAL
    years: float = 0.0
    mastery: float = 0.0  # 0 = novice, 1 = expert


@dataclass
class AcuteState:
    """
    ψ_state = {ρ_fatigue, ρ_arousal, ρ_stress, ρ_affect}

    Transient psychological/physiological conditions.
    All values in [0, 1].
    """
    fatigue: float = 0.0      # 0 = rested, 1 = severe
    arousal: float = 0.5      # 0 = hypo, 1 = hyper
    stress: float = 0.0       # 0 = none, 1 = severe
    affect: float = 0.5       # 0 = very negative, 1 = very positive


@dataclass
class TraitProfile:
    """
    ψ_trait = {τ_openness, τ_conscientiousness, τ_extraversion,
               τ_sensitivity, τ_risk}

    Stable personality traits. Values in [0, 1].
    """
    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    sensitivity: float = 0.5
    risk_tolerance: float = 0.5


# ──────────────────────────────────────────────────────────────────
# Full Subject Characteristics (ψ)
# ──────────────────────────────────────────────────────────────────

@dataclass
class SubjectCharacteristics:
    """
    ψ = {ψ_culture, ψ_neuro, ψ_dev, ψ_exp, ψ_state, ψ_trait}

    Complete subject-characteristics parameterization for CVA.
    Used by constraint engine (θ(ψ)) and valuation engine (g(ψ), τ(ψ), κ(ψ)).
    """
    subject_id: str = ""
    culture: CulturalContext = field(default_factory=CulturalContext)
    neurotype: NeurotypeProfile = field(default_factory=NeurotypeProfile)
    development: DevelopmentalStage = field(default_factory=DevelopmentalStage)
    experience: ExperienceProfile = field(default_factory=ExperienceProfile)
    state: AcuteState = field(default_factory=AcuteState)
    trait: TraitProfile = field(default_factory=TraitProfile)

    def compute_precision(self) -> float:
        """
        precision(ψ) = β₀ · (1 − ρ_fatigue − ρ_stress) · P_neuro · (1 + τ_conscientiousness)

        From CVA spec §2.3.
        """
        beta_0 = 1.5  # baseline precision (inverse temperature)
        state_factor = max(0.1, 1.0 - self.state.fatigue - self.state.stress)
        neuro_factor = self._neuro_precision_factor()
        trait_factor = 1.0 + self.trait.conscientiousness
        return beta_0 * state_factor * neuro_factor * trait_factor

    def _neuro_precision_factor(self) -> float:
        """P_neuro: neurotype-specific precision scaling."""
        factors = {
            NeurotypeName.TYPICAL: 1.0,
            NeurotypeName.ADHD: 0.6,
            NeurotypeName.ALZHEIMERS: 0.3,
            NeurotypeName.ASD: 1.3,
            NeurotypeName.OLDER_ADULT: 0.7,
            NeurotypeName.PTSD: 0.8,
            NeurotypeName.DEPRESSION: 0.7,
            NeurotypeName.ANXIETY: 0.9,
            NeurotypeName.BIPOLAR_MANIC: 0.5,
            NeurotypeName.BIPOLAR_DEPRESSED: 0.6,
            NeurotypeName.GIFTED: 1.2,
            NeurotypeName.CHILD_5_8: 0.5,
            NeurotypeName.CHILD_9_12: 0.7,
        }
        return factors.get(self.neurotype.name, 1.0)

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps({
            "subject_id": self.subject_id,
            "culture": {
                "kappa_self": self.culture.kappa_self.value,
                "kappa_social": self.culture.kappa_social.value,
                "kappa_aesthetics": self.culture.kappa_aesthetics,
                "kappa_ecology": self.culture.kappa_ecology,
            },
            "neurotype": {
                "name": self.neurotype.name.value,
                "nu_sensory": self.neurotype.nu_sensory,
                "nu_integration": self.neurotype.nu_integration,
                "nu_learning": self.neurotype.nu_learning,
                "nu_threat": self.neurotype.nu_threat,
                "nu_social": self.neurotype.nu_social,
                "nu_reward": self.neurotype.nu_reward,
            },
            "development": {
                "age": self.development.age,
                "m_visual": self.development.m_visual,
                "m_motor": self.development.m_motor,
                "m_exec": self.development.m_exec,
                "m_social": self.development.m_social,
            },
            "experience": {
                "domain": self.experience.domain.value,
                "years": self.experience.years,
                "mastery": self.experience.mastery,
            },
            "state": asdict(self.state),
            "trait": asdict(self.trait),
        })

    @classmethod
    def from_json(cls, data: str | dict) -> "SubjectCharacteristics":
        """Deserialize from JSON."""
        if isinstance(data, str):
            data = json.loads(data)
        return cls(
            subject_id=data.get("subject_id", ""),
            culture=CulturalContext(
                kappa_self=SelfConstrual(data.get("culture", {}).get("kappa_self", "independent")),
                kappa_social=SocialStructure(data.get("culture", {}).get("kappa_social", "egalitarian")),
                kappa_aesthetics=data.get("culture", {}).get("kappa_aesthetics", {}),
                kappa_ecology=data.get("culture", {}).get("kappa_ecology", {}),
            ),
            neurotype=NeurotypeProfile(
                name=NeurotypeName(data.get("neurotype", {}).get("name", "typical")),
                nu_sensory=data.get("neurotype", {}).get("nu_sensory", 0.5),
                nu_integration=data.get("neurotype", {}).get("nu_integration", 0.5),
                nu_learning=data.get("neurotype", {}).get("nu_learning", 0.5),
                nu_threat=data.get("neurotype", {}).get("nu_threat", 0.5),
                nu_social=data.get("neurotype", {}).get("nu_social", 0.5),
                nu_reward=data.get("neurotype", {}).get("nu_reward", 0.5),
            ),
            development=DevelopmentalStage(
                age=data.get("development", {}).get("age", 30),
                m_visual=data.get("development", {}).get("m_visual", 1.0),
                m_motor=data.get("development", {}).get("m_motor", 1.0),
                m_exec=data.get("development", {}).get("m_exec", 1.0),
                m_social=data.get("development", {}).get("m_social", 1.0),
            ),
            experience=ExperienceProfile(
                domain=ExpertiseDomain(data.get("experience", {}).get("domain", "general")),
                years=data.get("experience", {}).get("years", 0),
                mastery=data.get("experience", {}).get("mastery", 0),
            ),
            state=AcuteState(**data.get("state", {})) if data.get("state") else AcuteState(),
            trait=TraitProfile(**data.get("trait", {})) if data.get("trait") else TraitProfile(),
        )


# ──────────────────────────────────────────────────────────────────
# Pre-defined Neurotype Profiles (from spec §3)
# ──────────────────────────────────────────────────────────────────

NEUROTYPE_PROFILES: Dict[str, NeurotypeProfile] = {
    "typical": NeurotypeProfile(NeurotypeName.TYPICAL, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
    "ptsd": NeurotypeProfile(NeurotypeName.PTSD, 0.7, 0.3, 0.5, 0.9, 0.5, 0.3),
    "asd": NeurotypeProfile(NeurotypeName.ASD, 0.8, 0.3, 0.5, 0.5, 0.2, 0.4),
    "adhd": NeurotypeProfile(NeurotypeName.ADHD, 0.5, 0.3, 0.7, 0.5, 0.5, 0.8),
    "older_adult": NeurotypeProfile(NeurotypeName.OLDER_ADULT, 0.3, 0.3, 0.3, 0.5, 0.5, 0.4),
    "child_5_8": NeurotypeProfile(NeurotypeName.CHILD_5_8, 0.6, 0.4, 0.7, 0.4, 0.4, 0.6),
    "child_9_12": NeurotypeProfile(NeurotypeName.CHILD_9_12, 0.5, 0.5, 0.7, 0.4, 0.6, 0.6),
    "alzheimers": NeurotypeProfile(NeurotypeName.ALZHEIMERS, 0.3, 0.2, 0.1, 0.5, 0.3, 0.3),
    "depression": NeurotypeProfile(NeurotypeName.DEPRESSION, 0.5, 0.4, 0.3, 0.6, 0.4, 0.2),
    "anxiety": NeurotypeProfile(NeurotypeName.ANXIETY, 0.7, 0.5, 0.5, 0.8, 0.6, 0.5),
    "bipolar_manic": NeurotypeProfile(NeurotypeName.BIPOLAR_MANIC, 0.5, 0.5, 0.7, 0.3, 0.5, 0.9),
    "bipolar_depressed": NeurotypeProfile(NeurotypeName.BIPOLAR_DEPRESSED, 0.5, 0.4, 0.3, 0.7, 0.4, 0.2),
    "gifted": NeurotypeProfile(NeurotypeName.GIFTED, 0.6, 0.6, 0.8, 0.5, 0.5, 0.6),
}

# Pre-defined cultural presets
CULTURAL_PRESETS: Dict[str, CulturalContext] = {
    "western": CulturalContext(
        kappa_self=SelfConstrual.INDEPENDENT,
        kappa_social=SocialStructure.EGALITARIAN,
    ),
    "japanese": CulturalContext(
        kappa_self=SelfConstrual.INTERDEPENDENT,
        kappa_social=SocialStructure.HIERARCHICAL_SECURE,
        kappa_aesthetics={
            "material_density_preference": 0.3,  # lower (Ma)
            "symmetry_preference": 0.4,           # asymmetry valued
            "color_saturation_preference": 0.3,   # muted
            "temporal_pacing": 0.3,               # slower
            "ornamentation": 0.3,                 # minimal
        },
    ),
    "west_african": CulturalContext(
        kappa_self=SelfConstrual.RELATIONAL,
        kappa_social=SocialStructure.COLLECTIVE_DIGNITY,
        kappa_aesthetics={
            "material_density_preference": 0.6,
            "symmetry_preference": 0.5,
            "color_saturation_preference": 0.7,
            "temporal_pacing": 0.6,
            "ornamentation": 0.7,
        },
    ),
    "indian": CulturalContext(
        kappa_self=SelfConstrual.DHARMIC,
        kappa_social=SocialStructure.HIERARCHICAL_COSMIC,
        kappa_aesthetics={
            "material_density_preference": 0.7,
            "symmetry_preference": 0.6,
            "color_saturation_preference": 0.8,
            "temporal_pacing": 0.5,
            "ornamentation": 0.8,
        },
    ),
}
