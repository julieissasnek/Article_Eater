"""
Article Eater - Outcome Taxonomy Extensions (Refined)
======================================================

Sprint 4: Outcome Taxonomy Extensions (2026-01-18)
Expert Panel Refinements Applied (2026-01-18)

Extends the basic outcome vocabulary system to support:
1. Theory-outcome mappings with causal pathway documentation
2. Contextual epistemic level assignment based on measurement method
3. CNFA-specific extensions restructured as feature/percept/response
4. Stub outcome queuing with construct validity estimates
5. Bridge candidate identification with mechanism annotation

Expert Panel Refinements Incorporated:
- Decision 4.1: Causal pathways documented; configurable thresholds
- Decision 4.2: Method-dependent epistemic levels; access level facet
- Decision 4.3: Restructured arch domain; added ART/prospect-refuge constructs
- Decision 4.4: Stub queuing with construct validity (not claim credence)
- Decision 4.5: Mechanism annotation; tiered confidence; default to analogical

References:
- Quine, W.V.O. (1951). Two Dogmas of Empiricism
- Kaplan, R. & Kaplan, S. (1989). The Experience of Nature
- Ulrich, R.S. (1983). Aesthetic and affective response to natural environment
- Appleton, J. (1975). The Experience of Landscape
- Gibson, J.J. (1979). The Ecological Approach to Visual Perception
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timezone
from pathlib import Path
import json
import logging

# Import from web of belief
from src.services.web_of_belief import EpistemicLevel

# Import bridge warrants for cross-domain suggestions
try:
    from src.services.bridge_warrants import (
        BridgeWarrant,
        BridgeType,
        BridgeStatus,
        create_bridge,
        suggest_bridges
    )
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False

logger = logging.getLogger(__name__)


# =============================================================================
# ACCESS LEVEL (Expert Panel 4.2: Separate from epistemic level)
# =============================================================================

class AccessLevel(Enum):
    """
    What aspect of the phenomenon is measured.

    Per expert panel (Kaplan): physiological measures access different phenomena
    (autonomic states vs. conscious experience) rather than the same phenomenon
    more directly. Access level captures this distinction.
    """
    CONSCIOUS = "conscious"          # Self-report, conscious experience
    AUTONOMIC = "autonomic"          # Physiological, unconscious processes
    BEHAVIORAL = "behavioral"        # Observable behavior, performance
    NEURAL = "neural"                # Brain activity measures
    ENVIRONMENTAL = "environmental"  # Features of the environment itself


# =============================================================================
# MEASUREMENT METHOD FACETS (Expert Panel 4.2)
# =============================================================================

class MeasurementMethod(Enum):
    """
    Measurement method facet for contextual epistemic level assignment.

    Per expert panel (Kaplan, Bates): The same outcome has different epistemic
    status depending on how it is measured. Method is a facet modifier.
    """
    SELF_REPORT = "self_report"          # Questionnaires, Likert scales
    CORTISOL = "cortisol"                # Salivary/blood cortisol
    HEART_RATE = "heart_rate"            # HR, HRV
    EEG = "eeg"                          # Electroencephalography
    FMRI = "fmri"                        # Functional MRI
    BEHAVIORAL_TASK = "behavioral_task"  # Cognitive tasks, RT
    OBSERVATION = "observation"          # Observer ratings
    PHYSIOLOGICAL = "physiological"      # General physiological
    OBJECTIVE_MEASURE = "objective"      # Objective environmental measure
    UNSPECIFIED = "unspecified"          # Method not specified


# Method → Epistemic Level mapping (Expert Panel 4.2)
# Note: These are defaults; context may override
METHOD_EPISTEMIC_LEVELS: Dict[MeasurementMethod, EpistemicLevel] = {
    MeasurementMethod.SELF_REPORT: EpistemicLevel.INTERMEDIATE,
    MeasurementMethod.CORTISOL: EpistemicLevel.EMPIRICAL,
    MeasurementMethod.HEART_RATE: EpistemicLevel.EMPIRICAL,
    MeasurementMethod.EEG: EpistemicLevel.EMPIRICAL,
    MeasurementMethod.FMRI: EpistemicLevel.EMPIRICAL,
    MeasurementMethod.BEHAVIORAL_TASK: EpistemicLevel.EMPIRICAL,
    MeasurementMethod.OBSERVATION: EpistemicLevel.OBSERVATIONAL,
    MeasurementMethod.PHYSIOLOGICAL: EpistemicLevel.EMPIRICAL,
    MeasurementMethod.OBJECTIVE_MEASURE: EpistemicLevel.OBSERVATIONAL,
    MeasurementMethod.UNSPECIFIED: EpistemicLevel.EMPIRICAL,  # Default
}

# Method → Access Level mapping
METHOD_ACCESS_LEVELS: Dict[MeasurementMethod, AccessLevel] = {
    MeasurementMethod.SELF_REPORT: AccessLevel.CONSCIOUS,
    MeasurementMethod.CORTISOL: AccessLevel.AUTONOMIC,
    MeasurementMethod.HEART_RATE: AccessLevel.AUTONOMIC,
    MeasurementMethod.EEG: AccessLevel.NEURAL,
    MeasurementMethod.FMRI: AccessLevel.NEURAL,
    MeasurementMethod.BEHAVIORAL_TASK: AccessLevel.BEHAVIORAL,
    MeasurementMethod.OBSERVATION: AccessLevel.BEHAVIORAL,
    MeasurementMethod.PHYSIOLOGICAL: AccessLevel.AUTONOMIC,
    MeasurementMethod.OBJECTIVE_MEASURE: AccessLevel.ENVIRONMENTAL,
    MeasurementMethod.UNSPECIFIED: AccessLevel.CONSCIOUS,  # Default assumption
}


# =============================================================================
# THEORY-OUTCOME MAPPINGS WITH CAUSAL PATHWAYS (Expert Panel 4.1)
# =============================================================================

@dataclass
class TheoryOutcomeMapping:
    """
    Theory-outcome mapping with explicit causal pathway documentation.

    Per expert panel (Pearl): Relevance scores should have documented causal
    pathways. Per Kaplan: Distinguish core vs. derived predictions.
    """
    theory_id: str
    outcome_id: str
    relevance: float  # 0-1
    prediction_type: str  # "core", "derived", "exploratory"
    causal_pathway: Optional[str]  # Explicit mechanism description
    scope_conditions: List[str] = field(default_factory=list)  # When score applies
    literature_support: str = "moderate"  # "extensive", "moderate", "sparse", "theoretical"


# Theory-outcome mappings with causal pathway documentation
THEORY_OUTCOME_RELEVANCE: Dict[str, Dict[str, float]] = {
    "ART": {
        # Attention Restoration Theory (Kaplan & Kaplan)
        # Core predictions: soft fascination → directed attention recovery
        "cog": 0.9,
        "cog.attention": 1.0,
        "cog.attention.sustained": 1.0,
        "cog.attention.selective": 0.9,
        "cog.memory": 0.7,
        "cog.memory.working": 0.8,
        "cog.performance": 0.85,
        "physio.fatigue": 0.8,
        "physio.alertness": 0.7,
        "behav.productivity": 0.75,
        # ART-specific constructs (Expert Panel 4.3)
        "art.fascination": 1.0,
        "art.extent": 1.0,
        "art.compatibility": 1.0,
        "art.being_away": 1.0,
    },
    "SRT": {
        # Stress Recovery Theory (Ulrich)
        # Core predictions: nature → parasympathetic activation → stress recovery
        "affect": 0.9,
        "affect.stress": 1.0,
        "affect.anxiety": 0.9,
        "affect.mood": 0.8,
        "affect.mood.positive": 0.85,
        "affect.mood.negative": 0.85,
        "physio": 0.9,
        "physio.alertness": 0.7,
        "health.wellbeing": 0.8,
    },
    "Biophilia": {
        # Biophilia Hypothesis (Wilson)
        "affect.mood": 0.8,
        "affect.mood.positive": 0.85,
        "health.wellbeing": 0.9,
        "social": 0.6,
        "social.interaction": 0.65,
    },
    "Prospect_Refuge": {
        # Prospect-Refuge Theory (Appleton, 1975)
        "arch.config.prospect": 1.0,
        "arch.config.refuge": 1.0,
        "arch.config.hazard": 0.9,
        "arch.response.safety": 0.95,
        "affect.mood": 0.7,
    },
    "Perceptual_Fluency": {
        # Perceptual Fluency Theory
        "cog.performance": 0.7,
        "affect.mood.positive": 0.8,
        "arch.percept.aesthetic": 0.9,
    },
    "Predictive_Processing": {
        # Predictive Processing / Bayesian Brain
        "cog": 0.8,
        "cog.attention": 0.85,
        "affect.anxiety": 0.7,
        "neural": 0.9,
    },
}

# Causal pathway documentation (Expert Panel 4.1: Pearl)
CAUSAL_PATHWAYS: Dict[str, Dict[str, str]] = {
    "ART": {
        "cog.attention.sustained": "nature_exposure → involuntary_attention_engagement → directed_attention_recovery → sustained_attention_improvement",
        "cog.memory.working": "nature_exposure → directed_attention_recovery → reduced_cognitive_load → working_memory_improvement (DERIVED)",
        "physio.fatigue": "directed_attention_fatigue → [antecedent_condition] → nature_restores",
    },
    "SRT": {
        "affect.stress": "nature_exposure → parasympathetic_activation → reduced_cortisol → stress_reduction",
        "physio": "nature_exposure → autonomic_regulation → physiological_recovery",
    },
    "Prospect_Refuge": {
        "arch.response.safety": "prospect_refuge_configuration → evolutionary_threat_assessment → perceived_safety",
    },
}

# Scope conditions for when relevance scores apply (Expert Panel 4.1: Cartwright)
SCOPE_CONDITIONS: Dict[str, List[str]] = {
    "ART:cog.attention": [
        "Sufficient exposure duration (typically >15 min)",
        "Baseline directed attention depletion present",
        "Environment has restorative qualities (fascination, extent, compatibility, being-away)",
    ],
    "SRT:affect.stress": [
        "Baseline stress present",
        "Environment perceived as safe",
        "Exposure duration sufficient for parasympathetic response",
    ],
}


# =============================================================================
# CONFIGURABLE THRESHOLDS (Expert Panel 4.1)
# =============================================================================

@dataclass
class RelevanceThresholds:
    """
    Purpose-specific relevance thresholds.

    Per expert panel (Cartwright, Simon): Different thresholds for different
    purposes. Low threshold for exploratory flagging, high for auto-processing.
    """
    exploratory: float = 0.3    # Flag for review
    standard: float = 0.4       # Default threshold
    auto_assign: float = 0.7    # Automatic theory assignment

    def get_threshold(self, purpose: str = "standard") -> float:
        return getattr(self, purpose, self.standard)


DEFAULT_THRESHOLDS = RelevanceThresholds()


# Reverse mapping: outcome → theories
def _build_outcome_theory_map() -> Dict[str, List[Tuple[str, float]]]:
    """Build reverse mapping from outcomes to theories."""
    result: Dict[str, List[Tuple[str, float]]] = {}
    for theory, outcomes in THEORY_OUTCOME_RELEVANCE.items():
        for outcome, relevance in outcomes.items():
            if outcome not in result:
                result[outcome] = []
            result[outcome].append((theory, relevance))
    # Sort by relevance descending
    for outcome in result:
        result[outcome].sort(key=lambda x: -x[1])
    return result

OUTCOME_THEORY_MAP = _build_outcome_theory_map()


# =============================================================================
# EPISTEMIC LEVEL DEFAULTS (Base levels, modified by method)
# =============================================================================

# Default epistemic levels for outcome domains (without method modifier)
# Per Expert Panel 4.2: These are "degree of interpretive mediation" not "observational directness"
OUTCOME_EPISTEMIC_LEVELS: Dict[str, EpistemicLevel] = {
    # Root domains - represent interpretive mediation level
    "cog": EpistemicLevel.INTERMEDIATE,
    "affect": EpistemicLevel.INTERMEDIATE,
    "behav": EpistemicLevel.EMPIRICAL,
    "social": EpistemicLevel.EMPIRICAL,
    "physio": EpistemicLevel.EMPIRICAL,  # Changed from OBSERVATIONAL per expert panel
    "neural": EpistemicLevel.EMPIRICAL,   # Changed from OBSERVATIONAL per expert panel
    "health": EpistemicLevel.INTERMEDIATE,
    "arch": EpistemicLevel.INTERMEDIATE,
    "art": EpistemicLevel.INTERMEDIATE,   # ART-specific constructs

    # Specific outcomes
    "cog.attention": EpistemicLevel.INTERMEDIATE,
    "cog.attention.sustained": EpistemicLevel.EMPIRICAL,
    "cog.attention.selective": EpistemicLevel.EMPIRICAL,
    "cog.memory": EpistemicLevel.INTERMEDIATE,
    "cog.memory.working": EpistemicLevel.EMPIRICAL,
    "cog.performance": EpistemicLevel.EMPIRICAL,

    "affect.stress": EpistemicLevel.EMPIRICAL,
    "affect.anxiety": EpistemicLevel.EMPIRICAL,
    "affect.mood": EpistemicLevel.INTERMEDIATE,
    "affect.mood.positive": EpistemicLevel.EMPIRICAL,
    "affect.mood.negative": EpistemicLevel.EMPIRICAL,

    # Per Expert Panel: physio not automatically observational
    "physio.alertness": EpistemicLevel.OBSERVATIONAL,
    "physio.fatigue": EpistemicLevel.OBSERVATIONAL,

    "behav.productivity": EpistemicLevel.EMPIRICAL,
    "behav.sleep": EpistemicLevel.OBSERVATIONAL,

    "health.wellbeing": EpistemicLevel.EMPIRICAL,

    "social.interaction": EpistemicLevel.EMPIRICAL,
    "social.collaboration": EpistemicLevel.EMPIRICAL,

    # CNFA architectural outcomes
    "arch.feature": EpistemicLevel.OBSERVATIONAL,
    "arch.percept": EpistemicLevel.EMPIRICAL,
    "arch.response": EpistemicLevel.EMPIRICAL,
    "arch.config": EpistemicLevel.OBSERVATIONAL,
}


# =============================================================================
# CNFA EXTENSIONS - RESTRUCTURED (Expert Panel 4.3)
# =============================================================================

# Restructured per expert panel (Kaplan, Bates):
# - arch.feature: Objective spatial properties
# - arch.percept: Perceptual judgments
# - arch.response: Psychological/physiological responses
# - arch.config: Spatial configurations (prospect-refuge, etc.)

CNFA_OUTCOME_EXTENSIONS: Dict[str, Dict[str, Any]] = {
    # Root domain
    "arch": {
        "name": "Architectural",
        "domain": "arch",
        "parent": None,
        "description": "Architectural perception and spatial cognition outcomes"
    },

    # === FEATURES (Objective spatial properties) ===
    "arch.feature": {
        "name": "Spatial Features",
        "domain": "arch",
        "parent": "arch",
        "description": "Objective, measurable spatial properties"
    },
    "arch.feature.ceiling_height": {
        "name": "Ceiling Height",
        "domain": "arch",
        "parent": "arch.feature",
        "description": "Objective ceiling height measurement"
    },
    "arch.feature.view_distance": {
        "name": "View Distance",
        "domain": "arch",
        "parent": "arch.feature",
        "description": "Maximum unobstructed view distance"
    },
    "arch.feature.window_ratio": {
        "name": "Window-to-Wall Ratio",
        "domain": "arch",
        "parent": "arch.feature",
        "description": "Proportion of glazing to wall area"
    },
    "arch.feature.daylight_factor": {
        "name": "Daylight Factor",
        "domain": "arch",
        "parent": "arch.feature",
        "description": "Objective daylight measurement"
    },
    "arch.feature.green_ratio": {
        "name": "Green Ratio",
        "domain": "arch",
        "parent": "arch.feature",
        "description": "Proportion of visible greenery"
    },

    # === PERCEPTS (Perceptual judgments) ===
    "arch.percept": {
        "name": "Perceptual Judgments",
        "domain": "arch",
        "parent": "arch",
        "description": "Subjective perceptual ratings of space"
    },
    "arch.percept.openness": {
        "name": "Perceived Openness",
        "domain": "arch",
        "parent": "arch.percept",
        "description": "Subjective sense of spaciousness"
    },
    "arch.percept.enclosure": {
        "name": "Perceived Enclosure",
        "domain": "arch",
        "parent": "arch.percept",
        "description": "Subjective sense of containment"
    },
    "arch.percept.complexity": {
        "name": "Perceived Complexity",
        "domain": "arch",
        "parent": "arch.percept",
        "description": "Subjective visual complexity rating"
    },
    "arch.percept.coherence": {
        "name": "Perceived Coherence",
        "domain": "arch",
        "parent": "arch.percept",
        "description": "Subjective visual order rating"
    },
    "arch.percept.naturalness": {
        "name": "Perceived Naturalness",
        "domain": "arch",
        "parent": "arch.percept",
        "description": "Subjective naturalness rating"
    },
    "arch.percept.aesthetic": {
        "name": "Aesthetic Judgment",
        "domain": "arch",
        "parent": "arch.percept",
        "description": "Subjective beauty/aesthetic rating"
    },
    "arch.percept.legibility": {
        "name": "Perceived Legibility",
        "domain": "arch",
        "parent": "arch.percept",
        "description": "Ease of understanding spatial organization (Lynch)"
    },

    # === SPATIAL CONFIGURATIONS (Expert Panel: prospect-refuge here) ===
    "arch.config": {
        "name": "Spatial Configurations",
        "domain": "arch",
        "parent": "arch",
        "description": "Theoretically significant spatial configurations"
    },
    "arch.config.prospect": {
        "name": "Prospect",
        "domain": "arch",
        "parent": "arch.config",
        "description": "Opportunity to see; unimpeded views (Appleton)"
    },
    "arch.config.refuge": {
        "name": "Refuge",
        "domain": "arch",
        "parent": "arch.config",
        "description": "Opportunity to hide; protective shelter (Appleton)"
    },
    "arch.config.hazard": {
        "name": "Hazard",
        "domain": "arch",
        "parent": "arch.config",
        "description": "Perceived threat in environment (Appleton)"
    },
    "arch.config.prospect_refuge_balance": {
        "name": "Prospect-Refuge Balance",
        "domain": "arch",
        "parent": "arch.config",
        "description": "Optimal balance of overview and shelter"
    },

    # === RESPONSES (Psychological/physiological) ===
    "arch.response": {
        "name": "Spatial Responses",
        "domain": "arch",
        "parent": "arch",
        "description": "Psychological and physiological responses to space"
    },
    "arch.response.safety": {
        "name": "Perceived Safety",
        "domain": "arch",
        "parent": "arch.response",
        "description": "Felt sense of safety in space"
    },
    "arch.response.calming": {
        "name": "Calming Effect",
        "domain": "arch",
        "parent": "arch.response",
        "description": "Restorative/calming quality of space"
    },
    "arch.response.arousing": {
        "name": "Arousing Effect",
        "domain": "arch",
        "parent": "arch.response",
        "description": "Stimulating/energizing quality of space"
    },
    "arch.response.place_attachment": {
        "name": "Place Attachment",
        "domain": "arch",
        "parent": "arch.response",
        "description": "Emotional bond with place (Altman & Low)"
    },
    "arch.response.control": {
        "name": "Perceived Control",
        "domain": "arch",
        "parent": "arch.response",
        "description": "Sense of control over environment"
    },
    "arch.response.restoration": {
        "name": "Perceived Restoration",
        "domain": "arch",
        "parent": "arch.response",
        "description": "Felt sense of restoration from environment"
    },

    # === WAYFINDING (Expert Panel: Bates) ===
    "arch.wayfinding": {
        "name": "Wayfinding",
        "domain": "arch",
        "parent": "arch",
        "description": "Navigation and orientation in space"
    },
    "arch.wayfinding.orientation": {
        "name": "Orientation",
        "domain": "arch",
        "parent": "arch.wayfinding",
        "description": "Sense of where one is"
    },
    "arch.wayfinding.navigation": {
        "name": "Navigation Ease",
        "domain": "arch",
        "parent": "arch.wayfinding",
        "description": "Ease of finding one's way"
    },

    # === ENVIRONMENTAL QUALITIES ===
    "arch.environ": {
        "name": "Environmental Qualities",
        "domain": "arch",
        "parent": "arch",
        "description": "Environmental qualities of space"
    },
    "arch.environ.daylight": {
        "name": "Daylight Quality",
        "domain": "arch",
        "parent": "arch.environ",
        "description": "Perceived quality of natural light"
    },
    "arch.environ.biophilic": {
        "name": "Biophilic Elements",
        "domain": "arch",
        "parent": "arch.environ",
        "description": "Presence of nature elements"
    },
    "arch.environ.thermal": {
        "name": "Thermal Comfort",
        "domain": "arch",
        "parent": "arch.environ",
        "description": "Thermal comfort perception"
    },
    "arch.environ.acoustic": {
        "name": "Acoustic Comfort",
        "domain": "arch",
        "parent": "arch.environ",
        "description": "Acoustic environment quality"
    },

    # === ART-SPECIFIC CONSTRUCTS (Expert Panel 4.3: Kaplan) ===
    "art": {
        "name": "ART Constructs",
        "domain": "art",
        "parent": None,
        "description": "Attention Restoration Theory specific constructs"
    },
    "art.fascination": {
        "name": "Fascination",
        "domain": "art",
        "parent": "art",
        "description": "Soft fascination; effortless attention (Kaplan)"
    },
    "art.extent": {
        "name": "Extent",
        "domain": "art",
        "parent": "art",
        "description": "Perceived scope; sense of being in a whole other world"
    },
    "art.compatibility": {
        "name": "Compatibility",
        "domain": "art",
        "parent": "art",
        "description": "Fit between environment and inclinations"
    },
    "art.being_away": {
        "name": "Being Away",
        "domain": "art",
        "parent": "art",
        "description": "Psychological distance from demands"
    },
}

# Geometry as facet modifier (Expert Panel 4.3: Bates)
# Applied via +modifier syntax
GEOMETRY_FACETS: Dict[str, str] = {
    "+curved": "Curved/smooth forms",
    "+angular": "Angular/sharp forms",
    "+fractal": "Fractal/self-similar patterns",
    "+organic": "Organic/biomorphic forms",
    "+rectilinear": "Rectilinear/orthogonal forms",
}

# Updated lookup synonyms for CNFA outcomes
CNFA_LOOKUP_EXTENSIONS: Dict[str, str] = {
    # Features
    "ceiling height": "arch.feature.ceiling_height",
    "view distance": "arch.feature.view_distance",
    "window ratio": "arch.feature.window_ratio",
    "daylight factor": "arch.feature.daylight_factor",
    "green ratio": "arch.feature.green_ratio",

    # Percepts
    "spaciousness": "arch.percept.openness",
    "openness": "arch.percept.openness",
    "perceived openness": "arch.percept.openness",
    "sense of space": "arch.percept.openness",
    "enclosure": "arch.percept.enclosure",
    "containment": "arch.percept.enclosure",
    "complexity": "arch.percept.complexity",
    "visual complexity": "arch.percept.complexity",
    "coherence": "arch.percept.coherence",
    "visual coherence": "arch.percept.coherence",
    "order": "arch.percept.coherence",
    "naturalness": "arch.percept.naturalness",
    "natural materials": "arch.percept.naturalness",
    "beauty": "arch.percept.aesthetic",
    "perceived beauty": "arch.percept.aesthetic",
    "aesthetic appeal": "arch.percept.aesthetic",
    "visual beauty": "arch.percept.aesthetic",
    "legibility": "arch.percept.legibility",
    "imageability": "arch.percept.legibility",

    # Configurations
    "prospect": "arch.config.prospect",
    "refuge": "arch.config.refuge",
    "prospect-refuge": "arch.config.prospect_refuge_balance",
    "prospect refuge": "arch.config.prospect_refuge_balance",
    "hazard": "arch.config.hazard",

    # Responses
    "safety": "arch.response.safety",
    "perceived safety": "arch.response.safety",
    "calming": "arch.response.calming",
    "soothing": "arch.response.calming",
    "restorative": "arch.response.restoration",
    "restoration": "arch.response.restoration",
    "arousing": "arch.response.arousing",
    "stimulating": "arch.response.arousing",
    "energizing": "arch.response.arousing",
    "place attachment": "arch.response.place_attachment",
    "sense of place": "arch.response.place_attachment",
    "control": "arch.response.control",
    "perceived control": "arch.response.control",

    # Wayfinding
    "wayfinding": "arch.wayfinding",
    "navigation": "arch.wayfinding.navigation",
    "orientation": "arch.wayfinding.orientation",

    # Environmental
    "daylight": "arch.environ.daylight",
    "natural light": "arch.environ.daylight",
    "daylighting": "arch.environ.daylight",
    "biophilic": "arch.environ.biophilic",
    "biophilic design": "arch.environ.biophilic",
    "nature elements": "arch.environ.biophilic",
    "plants": "arch.environ.biophilic",
    "greenery": "arch.environ.biophilic",
    "thermal comfort": "arch.environ.thermal",
    "acoustic comfort": "arch.environ.acoustic",

    # ART constructs
    "fascination": "art.fascination",
    "soft fascination": "art.fascination",
    "extent": "art.extent",
    "scope": "art.extent",
    "compatibility": "art.compatibility",
    "being away": "art.being_away",
    "being-away": "art.being_away",
    "escape": "art.being_away",
}


# =============================================================================
# STUB QUEUE WITH CONSTRUCT VALIDITY (Expert Panel 4.4)
# =============================================================================

@dataclass
class StubOutcome:
    """
    Stub outcome queued for review with construct validity estimate.

    Per expert panel (Pearl, Cartwright):
    - Don't assign claim credence to unvetted stubs
    - Assign "construct validity" estimate based on source quality, domain confidence, corroboration
    - Only convert to credence after review
    """
    stub_id: str
    raw_term: str
    inferred_domain: str
    domain_confidence: float  # How confident in domain inference (0-1)

    # Construct validity estimate (NOT claim credence)
    construct_validity: float  # Estimate that this is a valid construct (0-1)
    validity_basis: str  # "source_quality", "corroboration", "theoretical"

    # Provenance
    source_papers: List[str] = field(default_factory=list)
    source_quality: str = "peer_reviewed"  # "peer_reviewed", "conference", "preprint"
    first_seen: Optional[datetime] = None

    # Review status
    review_status: str = "pending"  # "pending", "approved", "rejected", "merged"
    canonical_mapping: Optional[str] = None  # If merged, points to canonical outcome_id
    review_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stub_id": self.stub_id,
            "raw_term": self.raw_term,
            "inferred_domain": self.inferred_domain,
            "domain_confidence": self.domain_confidence,
            "construct_validity": self.construct_validity,
            "validity_basis": self.validity_basis,
            "source_papers": self.source_papers,
            "source_quality": self.source_quality,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "review_status": self.review_status,
            "canonical_mapping": self.canonical_mapping,
            "review_notes": self.review_notes,
        }


# =============================================================================
# BRIDGE CANDIDATE WITH MECHANISM ANNOTATION (Expert Panel 4.5)
# =============================================================================

@dataclass
class BridgeCandidate:
    """
    Bridge candidate with mechanism annotation and tiered confidence.

    Per expert panel (Pearl, Cartwright, Simon):
    - Require mechanism annotation
    - Tiered confidence (high/moderate/low)
    - Default to analogical type
    """
    source_outcome: str
    target_outcome: str
    source_domain: str
    target_domain: str

    # Bridge type (Expert Panel: default to analogical)
    bridge_type: str = "analogical"  # "mechanism", "functional", "analogical"

    # Mechanism annotation (Expert Panel: required)
    mechanism: Optional[str] = None  # Explicit mechanism if known
    mechanism_specified: bool = False

    # Tiered confidence (Expert Panel: Simon)
    confidence_tier: str = "low"  # "high", "moderate", "low"
    literature_support: str = "sparse"  # "extensive", "moderate", "sparse", "theoretical"

    # Shared theoretical basis
    shared_theories: List[str] = field(default_factory=list)

    # Causal graph consistency (Expert Panel: Pearl)
    causal_path: Optional[str] = None
    causal_consistent: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_outcome": self.source_outcome,
            "target_outcome": self.target_outcome,
            "source_domain": self.source_domain,
            "target_domain": self.target_domain,
            "bridge_type": self.bridge_type,
            "mechanism": self.mechanism,
            "mechanism_specified": self.mechanism_specified,
            "confidence_tier": self.confidence_tier,
            "literature_support": self.literature_support,
            "shared_theories": self.shared_theories,
            "causal_path": self.causal_path,
            "causal_consistent": self.causal_consistent,
        }


# =============================================================================
# EXTENDED OUTCOME DATA CLASS
# =============================================================================

@dataclass
class ExtendedOutcome:
    """
    Extended outcome with theory relevance and contextual epistemic level.
    """
    outcome_id: str
    name: str
    domain: str
    parent: Optional[str]

    # Base epistemic level (without method modifier)
    epistemic_level: EpistemicLevel = EpistemicLevel.EMPIRICAL

    # Theory relevance
    theory_relevance: Dict[str, float] = field(default_factory=dict)

    # Stub status
    is_stub: bool = False
    stub_reason: Optional[str] = None

    # Description
    description: Optional[str] = None

    # Bridge candidates
    bridge_candidates: List[str] = field(default_factory=list)

    # NEW: Category type (Expert Panel 4.3)
    category_type: Optional[str] = None  # "feature", "percept", "response", "config"

    # NEW: Default access level
    default_access_level: AccessLevel = AccessLevel.CONSCIOUS

    def get_epistemic_level(self, method: MeasurementMethod = MeasurementMethod.UNSPECIFIED) -> EpistemicLevel:
        """
        Get contextual epistemic level based on measurement method.

        Per Expert Panel 4.2: Epistemic level depends on how outcome is measured.
        """
        if method != MeasurementMethod.UNSPECIFIED:
            return METHOD_EPISTEMIC_LEVELS.get(method, self.epistemic_level)
        return self.epistemic_level

    def get_access_level(self, method: MeasurementMethod = MeasurementMethod.UNSPECIFIED) -> AccessLevel:
        """Get access level based on measurement method."""
        if method != MeasurementMethod.UNSPECIFIED:
            return METHOD_ACCESS_LEVELS.get(method, self.default_access_level)
        return self.default_access_level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outcome_id": self.outcome_id,
            "name": self.name,
            "domain": self.domain,
            "parent": self.parent,
            "epistemic_level": self.epistemic_level.value,
            "theory_relevance": self.theory_relevance,
            "is_stub": self.is_stub,
            "stub_reason": self.stub_reason,
            "description": self.description,
            "bridge_candidates": self.bridge_candidates,
            "category_type": self.category_type,
            "default_access_level": self.default_access_level.value,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ExtendedOutcome':
        access_level_str = d.get("default_access_level", "conscious")
        try:
            access_level = AccessLevel(access_level_str)
        except ValueError:
            access_level = AccessLevel.CONSCIOUS

        return cls(
            outcome_id=d["outcome_id"],
            name=d["name"],
            domain=d["domain"],
            parent=d.get("parent"),
            epistemic_level=EpistemicLevel(d.get("epistemic_level", "empirical")),
            theory_relevance=d.get("theory_relevance", {}),
            is_stub=d.get("is_stub", False),
            stub_reason=d.get("stub_reason"),
            description=d.get("description"),
            bridge_candidates=d.get("bridge_candidates", []),
            category_type=d.get("category_type"),
            default_access_level=access_level,
        )


# =============================================================================
# EXTENDED TAXONOMY SERVICE
# =============================================================================

class ExtendedOutcomeTaxonomy:
    """
    Extended outcome taxonomy with expert panel refinements.
    """

    def __init__(
        self,
        base_lookup_path: Optional[Path] = None,
        thresholds: Optional[RelevanceThresholds] = None
    ):
        self.base_lookup_path = base_lookup_path or (
            Path(__file__).parent.parent.parent / "contracts" / "vocab" / "outcome_lookup.json"
        )
        self.thresholds = thresholds or DEFAULT_THRESHOLDS

        self._base_data: Dict[str, Any] = {}
        self._extended_outcomes: Dict[str, ExtendedOutcome] = {}
        self._lookup: Dict[str, str] = {}

        # Stub queue (Expert Panel 4.4: queue for review, don't integrate)
        self._stub_queue: Dict[str, StubOutcome] = {}

        # Bridge candidates (Expert Panel 4.5: with mechanism annotation)
        self._bridge_candidates: List[BridgeCandidate] = []

        self._load_base_taxonomy()
        self._add_cnfa_extensions()
        self._build_theory_relevance()
        self._identify_bridge_candidates()

    def _load_base_taxonomy(self) -> None:
        """Load base outcome taxonomy."""
        if self.base_lookup_path.exists():
            with open(self.base_lookup_path) as f:
                self._base_data = json.load(f)
        else:
            logger.warning(f"Base taxonomy not found at {self.base_lookup_path}")
            self._base_data = {"lookup": {}, "terms": {}, "domains": []}

        for term_id, term_data in self._base_data.get("terms", {}).items():
            level = self._get_epistemic_level(term_id)
            self._extended_outcomes[term_id] = ExtendedOutcome(
                outcome_id=term_id,
                name=term_data.get("name", term_id),
                domain=term_data.get("domain", term_id.split(".")[0]),
                parent=term_data.get("parent"),
                epistemic_level=level
            )

        self._lookup = dict(self._base_data.get("lookup", {}))

    def _add_cnfa_extensions(self) -> None:
        """Add restructured CNFA-specific outcome extensions."""
        for term_id, term_data in CNFA_OUTCOME_EXTENSIONS.items():
            if term_id not in self._extended_outcomes:
                level = self._get_epistemic_level(term_id)

                # Determine category type from ID
                category_type = None
                if ".feature" in term_id:
                    category_type = "feature"
                elif ".percept" in term_id:
                    category_type = "percept"
                elif ".response" in term_id:
                    category_type = "response"
                elif ".config" in term_id:
                    category_type = "config"

                # Determine default access level
                access_level = AccessLevel.CONSCIOUS
                if category_type == "feature":
                    access_level = AccessLevel.ENVIRONMENTAL
                elif category_type == "response":
                    access_level = AccessLevel.CONSCIOUS

                self._extended_outcomes[term_id] = ExtendedOutcome(
                    outcome_id=term_id,
                    name=term_data.get("name", term_id),
                    domain=term_data.get("domain", "arch"),
                    parent=term_data.get("parent"),
                    epistemic_level=level,
                    description=term_data.get("description"),
                    category_type=category_type,
                    default_access_level=access_level,
                )

        self._lookup.update(CNFA_LOOKUP_EXTENSIONS)

        # Add domains
        domains = set(self._base_data.get("domains", []))
        domains.add("arch")
        domains.add("art")
        self._base_data["domains"] = list(domains)

    def _get_epistemic_level(self, outcome_id: str) -> EpistemicLevel:
        """Get epistemic level for an outcome (with hierarchy fallback)."""
        if outcome_id in OUTCOME_EPISTEMIC_LEVELS:
            return OUTCOME_EPISTEMIC_LEVELS[outcome_id]

        parts = outcome_id.split(".")
        for i in range(len(parts) - 1, 0, -1):
            parent_id = ".".join(parts[:i])
            if parent_id in OUTCOME_EPISTEMIC_LEVELS:
                return OUTCOME_EPISTEMIC_LEVELS[parent_id]

        return EpistemicLevel.EMPIRICAL

    def _build_theory_relevance(self) -> None:
        """Build theory relevance for all outcomes."""
        for outcome_id, outcome in self._extended_outcomes.items():
            relevance = {}

            if outcome_id in OUTCOME_THEORY_MAP:
                for theory, score in OUTCOME_THEORY_MAP[outcome_id]:
                    relevance[theory] = score

            parts = outcome_id.split(".")
            for i in range(len(parts) - 1, 0, -1):
                parent_id = ".".join(parts[:i])
                if parent_id in OUTCOME_THEORY_MAP:
                    for theory, score in OUTCOME_THEORY_MAP[parent_id]:
                        if theory not in relevance:
                            relevance[theory] = score * 0.8

            outcome.theory_relevance = relevance

    def _identify_bridge_candidates(self) -> None:
        """
        Identify bridge candidates with mechanism annotation.

        Per Expert Panel 4.5: Default to analogical; require mechanism annotation.
        """
        arch_to_other_mappings = {
            "arch.response.calming": {
                "targets": ["affect.mood.positive", "affect.stress"],
                "mechanism": "Environmental features → perceptual processing → affective response",
                "literature": "moderate",
            },
            "arch.response.arousing": {
                "targets": ["affect.mood", "physio.alertness"],
                "mechanism": "Environmental stimulation → autonomic activation",
                "literature": "moderate",
            },
            "arch.percept.openness": {
                "targets": ["affect.mood", "cog.attention"],
                "mechanism": "Spatial perception → cognitive/affective effects (pathway unspecified)",
                "literature": "sparse",
            },
            "arch.environ.biophilic": {
                "targets": ["affect.stress", "health.wellbeing", "cog.attention.sustained"],
                "mechanism": "Biophilic elements → SRT/ART pathways → outcomes",
                "literature": "extensive",
            },
            "arch.percept.naturalness": {
                "targets": ["affect.mood.positive", "health.wellbeing"],
                "mechanism": "Perceived naturalness → biophilia activation",
                "literature": "moderate",
            },
            "arch.config.prospect_refuge_balance": {
                "targets": ["arch.response.safety", "affect.mood"],
                "mechanism": "Prospect-refuge configuration → evolutionary safety assessment → felt safety",
                "literature": "moderate",
            },
        }

        for arch_outcome, mapping in arch_to_other_mappings.items():
            if arch_outcome not in self._extended_outcomes:
                continue

            arch_obj = self._extended_outcomes[arch_outcome]

            for target_id in mapping["targets"]:
                target_obj = self._extended_outcomes.get(target_id)
                if not target_obj:
                    continue

                # Determine bridge type using Expert Panel heuristics (Bates)
                if arch_obj.domain == target_obj.domain:
                    bridge_type = "mechanism"
                elif arch_obj.domain == "arch" and target_obj.domain in ["affect", "cog"]:
                    bridge_type = "functional"
                else:
                    bridge_type = "analogical"  # Default per Cartwright

                # Determine confidence tier (Simon)
                lit_support = mapping.get("literature", "sparse")
                if lit_support == "extensive":
                    confidence_tier = "high"
                elif lit_support == "moderate":
                    confidence_tier = "moderate"
                else:
                    confidence_tier = "low"

                candidate = BridgeCandidate(
                    source_outcome=target_id,
                    target_outcome=arch_outcome,
                    source_domain=target_obj.domain,
                    target_domain=arch_obj.domain,
                    bridge_type=bridge_type,
                    mechanism=mapping.get("mechanism"),
                    mechanism_specified=mapping.get("mechanism") is not None,
                    confidence_tier=confidence_tier,
                    literature_support=lit_support,
                    shared_theories=list(
                        set(arch_obj.theory_relevance.keys()) &
                        set(target_obj.theory_relevance.keys())
                    ),
                    causal_path=mapping.get("mechanism"),
                    causal_consistent=True,
                )

                self._bridge_candidates.append(candidate)

                # Also set on outcome object for backward compatibility
                if target_id not in arch_obj.bridge_candidates:
                    arch_obj.bridge_candidates.append(target_id)

    def resolve(self, raw_term: str, fuzzy_threshold: float = 0.85) -> Optional[ExtendedOutcome]:
        """Resolve a raw outcome term to extended outcome."""
        raw_lower = raw_term.lower().strip()

        if raw_lower in self._lookup:
            outcome_id = self._lookup[raw_lower]
            return self._extended_outcomes.get(outcome_id)

        from difflib import SequenceMatcher
        best_match = None
        best_score = 0.0

        for lookup_text, outcome_id in self._lookup.items():
            score = SequenceMatcher(None, raw_lower, lookup_text).ratio()
            if score > best_score and score >= fuzzy_threshold:
                best_score = score
                best_match = outcome_id

        if best_match:
            return self._extended_outcomes.get(best_match)

        return None

    def resolve_or_stub(
        self,
        raw_term: str,
        paper_id: Optional[str] = None,
        context: Optional[str] = None,
        source_quality: str = "peer_reviewed"
    ) -> ExtendedOutcome:
        """
        Resolve outcome or queue stub for review.

        Per Expert Panel 4.4: Stubs are queued, not integrated. They get
        construct validity estimates, not claim credence.
        """
        resolved = self.resolve(raw_term)
        if resolved:
            return resolved

        # Create stub ID
        stub_id = f"STUB:{raw_term.lower().replace(' ', '_')}"

        # Check if already in queue
        if stub_id in self._stub_queue:
            stub = self._stub_queue[stub_id]
            # Update with additional source
            if paper_id and paper_id not in stub.source_papers:
                stub.source_papers.append(paper_id)
                # Increase validity with corroboration
                stub.construct_validity = min(0.9, stub.construct_validity + 0.1)
                stub.validity_basis = "corroboration"

            # Return as ExtendedOutcome for API compatibility
            return self._stub_to_extended_outcome(stub)

        # Infer domain with confidence
        domain, domain_confidence = self._infer_domain_with_confidence(raw_term)

        # Calculate construct validity (Expert Panel 4.4: Pearl)
        validity = self._calculate_construct_validity(
            source_quality=source_quality,
            domain_confidence=domain_confidence,
            n_sources=1
        )

        # Create stub and queue for review
        stub = StubOutcome(
            stub_id=stub_id,
            raw_term=raw_term,
            inferred_domain=domain,
            domain_confidence=domain_confidence,
            construct_validity=validity,
            validity_basis="source_quality",
            source_papers=[paper_id] if paper_id else [],
            source_quality=source_quality,
            first_seen=datetime.now(timezone.utc),
            review_status="pending",
        )

        self._stub_queue[stub_id] = stub
        logger.info(f"Queued outcome stub for review: {stub_id} (validity={validity:.2f})")

        return self._stub_to_extended_outcome(stub)

    def _stub_to_extended_outcome(self, stub: StubOutcome) -> ExtendedOutcome:
        """Convert stub to ExtendedOutcome for API compatibility."""
        return ExtendedOutcome(
            outcome_id=stub.stub_id,
            name=stub.raw_term,
            domain=stub.inferred_domain,
            parent=None,
            epistemic_level=EpistemicLevel.EMPIRICAL,
            is_stub=True,
            stub_reason=f"Queued for review (validity={stub.construct_validity:.2f}, status={stub.review_status})",
        )

    def _infer_domain_with_confidence(self, raw_term: str) -> Tuple[str, float]:
        """Infer domain with confidence score."""
        raw_lower = raw_term.lower()

        domain_keywords = {
            'cog': (['attention', 'memory', 'cognit', 'think', 'learn', 'focus', 'mental'], 0.8),
            'affect': (['mood', 'emotion', 'affect', 'stress', 'anxiety', 'feel'], 0.8),
            'behav': (['behavior', 'action', 'sleep', 'product', 'perform'], 0.7),
            'social': (['social', 'interact', 'collaborat', 'communi'], 0.7),
            'physio': (['heart', 'blood', 'cortisol', 'fatigue', 'alertness', 'physiolog'], 0.85),
            'neural': (['brain', 'neural', 'cortex', 'eeg', 'fmri', 'neuro'], 0.9),
            'health': (['health', 'wellbeing', 'well-being', 'wellness'], 0.75),
            'arch': (['space', 'room', 'building', 'architec', 'interior', 'daylight', 'window'], 0.8),
            'art': (['fascination', 'restoration', 'being away', 'extent'], 0.85),
        }

        best_domain = "unknown"
        best_confidence = 0.3  # Default low confidence for unknown

        for domain, (keywords, base_confidence) in domain_keywords.items():
            matches = sum(1 for kw in keywords if kw in raw_lower)
            if matches > 0:
                confidence = base_confidence * min(1.0, 0.5 + matches * 0.25)
                if confidence > best_confidence:
                    best_domain = domain
                    best_confidence = confidence

        return best_domain, best_confidence

    def _calculate_construct_validity(
        self,
        source_quality: str,
        domain_confidence: float,
        n_sources: int
    ) -> float:
        """
        Calculate construct validity estimate.

        Per Expert Panel (Pearl): Based on source quality, domain confidence, corroboration.
        """
        # Source quality factor
        quality_factors = {
            "peer_reviewed": 0.6,
            "conference": 0.4,
            "preprint": 0.3,
        }
        quality_factor = quality_factors.get(source_quality, 0.3)

        # Corroboration factor
        corroboration_factor = min(1.0, 0.5 + n_sources * 0.1)

        # Combine
        validity = quality_factor * domain_confidence * corroboration_factor

        return min(0.9, max(0.1, validity))

    def _infer_domain(self, raw_term: str) -> str:
        """Infer domain from term keywords (backward compatibility)."""
        domain, _ = self._infer_domain_with_confidence(raw_term)
        return domain

    def get_theories_for_outcome(
        self,
        outcome_id: str,
        threshold: Optional[float] = None,
        purpose: str = "standard"
    ) -> List[Tuple[str, float]]:
        """Get theories relevant to an outcome."""
        if threshold is None:
            threshold = self.thresholds.get_threshold(purpose)

        outcome = self._extended_outcomes.get(outcome_id)
        if not outcome:
            return []

        return [
            (theory, score)
            for theory, score in outcome.theory_relevance.items()
            if score >= threshold
        ]

    def get_outcomes_for_theory(
        self,
        theory_id: str,
        threshold: Optional[float] = None,
        purpose: str = "standard"
    ) -> List[Tuple[str, float]]:
        """Get outcomes relevant to a theory."""
        if threshold is None:
            threshold = self.thresholds.get_threshold(purpose)

        results = []
        for outcome_id, outcome in self._extended_outcomes.items():
            score = outcome.theory_relevance.get(theory_id, 0)
            if score >= threshold:
                results.append((outcome_id, score))

        results.sort(key=lambda x: -x[1])
        return results

    def suggest_bridges_for_outcome(
        self,
        outcome_id: str,
        min_confidence_tier: str = "low"
    ) -> List[Dict[str, Any]]:
        """
        Suggest bridge warrants with mechanism annotation.

        Per Expert Panel 4.5: Returns candidates with mechanism annotation
        and tiered confidence.
        """
        tier_order = {"high": 3, "moderate": 2, "low": 1}
        min_tier_value = tier_order.get(min_confidence_tier, 1)

        suggestions = []
        for candidate in self._bridge_candidates:
            if candidate.target_outcome == outcome_id or candidate.source_outcome == outcome_id:
                candidate_tier_value = tier_order.get(candidate.confidence_tier, 1)
                if candidate_tier_value >= min_tier_value:
                    suggestions.append(candidate.to_dict())

        return suggestions

    def get_all_outcomes(self) -> List[ExtendedOutcome]:
        """Get all outcomes (not including queued stubs)."""
        return list(self._extended_outcomes.values())

    def get_stubs(self) -> List[ExtendedOutcome]:
        """Get all stub outcomes (backward compatibility)."""
        return [self._stub_to_extended_outcome(s) for s in self._stub_queue.values()]

    def get_stub_queue(self) -> List[StubOutcome]:
        """Get stub queue for review."""
        return list(self._stub_queue.values())

    def review_stub(
        self,
        stub_id: str,
        action: str,  # "approve", "reject", "merge"
        canonical_mapping: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Review a queued stub.

        Per Expert Panel 4.4: Stubs can be approved, rejected, or merged.
        Merged stubs become deprecated synonyms pointing to canonical outcome.
        """
        if stub_id not in self._stub_queue:
            return False

        stub = self._stub_queue[stub_id]

        if action == "approve":
            stub.review_status = "approved"
            stub.review_notes = notes
            # Create as full outcome
            self._extended_outcomes[stub_id] = ExtendedOutcome(
                outcome_id=stub_id,
                name=stub.raw_term,
                domain=stub.inferred_domain,
                parent=None,
                epistemic_level=EpistemicLevel.EMPIRICAL,
                is_stub=False,
                description=f"Approved from stub. {notes or ''}"
            )

        elif action == "reject":
            stub.review_status = "rejected"
            stub.review_notes = notes

        elif action == "merge" and canonical_mapping:
            stub.review_status = "merged"
            stub.canonical_mapping = canonical_mapping
            stub.review_notes = notes
            # Add as synonym (Bates: see references)
            self._lookup[stub.raw_term.lower()] = canonical_mapping

        return True

    def get_causal_pathway(self, theory_id: str, outcome_id: str) -> Optional[str]:
        """Get documented causal pathway for theory-outcome relationship."""
        if theory_id in CAUSAL_PATHWAYS:
            return CAUSAL_PATHWAYS[theory_id].get(outcome_id)
        return None

    def get_scope_conditions(self, theory_id: str, outcome_id: str) -> List[str]:
        """Get scope conditions for when relevance score applies."""
        key = f"{theory_id}:{outcome_id}"
        return SCOPE_CONDITIONS.get(key, [])

    def export_extended_lookup(self, path: Path) -> None:
        """Export extended lookup with all refinements."""
        export_data = {
            "schema": "ae.extended_outcome_lookup.v2",  # Version bump for refinements
            "version": "2.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "lookup": self._lookup,
            "terms": {
                oid: outcome.to_dict()
                for oid, outcome in self._extended_outcomes.items()
            },
            "stub_queue": {
                sid: stub.to_dict()
                for sid, stub in self._stub_queue.items()
            },
            "bridge_candidates": [c.to_dict() for c in self._bridge_candidates],
            "domains": self._base_data.get("domains", []),
            "theory_outcome_relevance": THEORY_OUTCOME_RELEVANCE,
            "causal_pathways": CAUSAL_PATHWAYS,
            "scope_conditions": SCOPE_CONDITIONS,
            "thresholds": {
                "exploratory": self.thresholds.exploratory,
                "standard": self.thresholds.standard,
                "auto_assign": self.thresholds.auto_assign,
            },
            "stats": {
                "terms_count": len(self._extended_outcomes),
                "lookup_entries": len(self._lookup),
                "stubs_queued": len(self._stub_queue),
                "bridge_candidates": len(self._bridge_candidates),
                "cnfa_terms_count": len(CNFA_OUTCOME_EXTENSIONS),
            }
        }

        with open(path, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Exported extended outcome lookup to {path}")

    @classmethod
    def from_extended_lookup(cls, path: Path) -> 'ExtendedOutcomeTaxonomy':
        """Load from extended lookup file."""
        taxonomy = cls.__new__(cls)
        taxonomy.base_lookup_path = path
        taxonomy._extended_outcomes = {}
        taxonomy._lookup = {}
        taxonomy._stub_queue = {}
        taxonomy._bridge_candidates = []

        with open(path) as f:
            data = json.load(f)

        taxonomy._base_data = data
        taxonomy._lookup = data.get("lookup", {})

        # Load thresholds
        thresholds_data = data.get("thresholds", {})
        taxonomy.thresholds = RelevanceThresholds(
            exploratory=thresholds_data.get("exploratory", 0.3),
            standard=thresholds_data.get("standard", 0.4),
            auto_assign=thresholds_data.get("auto_assign", 0.7),
        )

        # Load terms
        for term_id, term_data in data.get("terms", {}).items():
            taxonomy._extended_outcomes[term_id] = ExtendedOutcome.from_dict(term_data)

        # Load stub queue
        for stub_id, stub_data in data.get("stub_queue", data.get("stubs", {})).items():
            if "construct_validity" in stub_data:
                # New format
                taxonomy._stub_queue[stub_id] = StubOutcome(
                    stub_id=stub_data["stub_id"],
                    raw_term=stub_data["raw_term"],
                    inferred_domain=stub_data["inferred_domain"],
                    domain_confidence=stub_data.get("domain_confidence", 0.5),
                    construct_validity=stub_data["construct_validity"],
                    validity_basis=stub_data.get("validity_basis", "source_quality"),
                    source_papers=stub_data.get("source_papers", []),
                    source_quality=stub_data.get("source_quality", "peer_reviewed"),
                    review_status=stub_data.get("review_status", "pending"),
                    canonical_mapping=stub_data.get("canonical_mapping"),
                    review_notes=stub_data.get("review_notes"),
                )
            else:
                # Old format - convert
                taxonomy._stub_queue[stub_id] = StubOutcome(
                    stub_id=stub_id,
                    raw_term=stub_data.get("name", stub_id),
                    inferred_domain=stub_data.get("domain", "unknown"),
                    domain_confidence=0.5,
                    construct_validity=0.4,
                    validity_basis="legacy",
                    review_status="pending",
                )

        return taxonomy


# =============================================================================
# INTEGRATION WITH WEB OF BELIEF
# =============================================================================

def outcome_to_belief_metadata(
    outcome: ExtendedOutcome,
    method: MeasurementMethod = MeasurementMethod.UNSPECIFIED
) -> Dict[str, Any]:
    """
    Convert outcome to metadata for belief creation.

    Per Expert Panel 4.2: Include contextual epistemic level based on method.
    """
    return {
        "outcome_id": outcome.outcome_id,
        "outcome_name": outcome.name,
        "outcome_domain": outcome.domain,
        "epistemic_level": outcome.get_epistemic_level(method).value,
        "access_level": outcome.get_access_level(method).value,
        "theory_relevance": outcome.theory_relevance,
        "is_outcome_stub": outcome.is_stub,
        "category_type": outcome.category_type,
        "measurement_method": method.value,
    }


def infer_theory_from_outcomes(
    outcomes: List[ExtendedOutcome],
    threshold: Optional[float] = None,
    thresholds: Optional[RelevanceThresholds] = None
) -> Tuple[Optional[str], Dict[str, float]]:
    """
    Infer most likely theory from a list of outcomes.
    """
    if threshold is None:
        threshold = (thresholds or DEFAULT_THRESHOLDS).standard

    combined: Dict[str, float] = {}

    for outcome in outcomes:
        for theory, score in outcome.theory_relevance.items():
            if theory not in combined:
                combined[theory] = 0
            combined[theory] = 1 - (1 - combined[theory]) * (1 - score * 0.5)

    if not combined:
        return None, {}

    sorted_theories = sorted(combined.items(), key=lambda x: -x[1])
    primary = sorted_theories[0][0] if sorted_theories[0][1] >= threshold else None

    return primary, combined


# =============================================================================
# MAIN (Demo/Test)
# =============================================================================

if __name__ == "__main__":
    taxonomy = ExtendedOutcomeTaxonomy()

    print("=== Extended Outcome Taxonomy (Refined) Demo ===\n")

    # Test resolution
    test_terms = [
        "sustained attention",
        "stress",
        "prospect-refuge",
        "fascination",
        "biophilic design",
        "unknown_outcome_xyz"
    ]

    for term in test_terms:
        result = taxonomy.resolve_or_stub(term, paper_id="demo:001")
        print(f"'{term}' -> {result.outcome_id}")
        print(f"  Level: {result.epistemic_level.value}")
        print(f"  Stub: {result.is_stub}")
        if not result.is_stub:
            print(f"  Theories: {list(result.theory_relevance.keys())[:3]}")
        print()

    # Test contextual epistemic level
    print("=== Contextual Epistemic Levels ===")
    stress = taxonomy.resolve("stress")
    if stress:
        for method in [MeasurementMethod.SELF_REPORT, MeasurementMethod.CORTISOL]:
            level = stress.get_epistemic_level(method)
            access = stress.get_access_level(method)
            print(f"  stress[{method.value}] -> {level.value} (access: {access.value})")

    # Test theory → outcome lookup
    print("\n=== Outcomes for ART (exploratory threshold) ===")
    for outcome_id, score in taxonomy.get_outcomes_for_theory("ART", purpose="exploratory")[:5]:
        print(f"  {outcome_id}: {score:.2f}")

    # Test bridge suggestions
    print("\n=== Bridge Suggestions for arch.environ.biophilic ===")
    for suggestion in taxonomy.suggest_bridges_for_outcome("arch.environ.biophilic"):
        print(f"  {suggestion['source_outcome']} -> {suggestion['target_outcome']}")
        print(f"    Type: {suggestion['bridge_type']}")
        print(f"    Mechanism: {suggestion['mechanism']}")
        print(f"    Confidence: {suggestion['confidence_tier']}")

    # Test stub queue
    print("\n=== Stub Queue ===")
    for stub in taxonomy.get_stub_queue():
        print(f"  {stub.stub_id}: validity={stub.construct_validity:.2f}, status={stub.review_status}")
