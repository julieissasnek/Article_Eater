"""
Article Eater - Extraction to Web of Belief Mapper
===================================================

Sprint 1: Core Mapper Implementation (Post-Expert Panel Review 2026-01-18)

Maps contract pipeline outputs (ae.claim.v1, ae.rule.v1) to the Quinean
web of belief (web_of_belief.py), enabling coherentist analysis of
extracted findings.

This module bridges Track A (production extraction pipeline) with
Track B (epistemic analysis engine).

Key Mappings:
- ae.claim.v1 → Belief nodes
- ae.rule.v1 → Constraint edges
- claim_type → EpistemicLevel
- outcome constructs → Theory relevance
- Missing theory connections → Stub status

Expert Panel Resolutions (2026-01-18):
1. claim_type → EpistemicLevel: "mechanistic" maps to INTERMEDIATE (not THEORETICAL)
   - Mechanistic claims are higher-generality generalizations, not core theory
   - Mechanistic claims get entrenchment boost (+0.15)
2. Theory threshold (0.4) is configurable via AE_THEORY_THRESHOLD env var
   - Multi-theory attachment supported for claims relevant to multiple theories
   - Secondary theories attached if score >= SECONDARY_THEORY_THRESHOLD (0.3)
3. Null findings are NOT automatically ANOMALOUS
   - No 50% credence penalty for null findings
   - Evidential direction tracked separately (supports/contradicts)
4. Theory inference uses diminishing returns (not max())
   - Multiple signals boost confidence but don't accumulate unboundedly
   - Formula: combined = 1 - (1 - current) * (1 - new * 0.5)
5. POLARITY_MODIFIERS: null → CONTRADICTS (not INDEPENDENT) with 0.6 strength
   - Null findings are evidence AGAINST an effect, not absence of evidence

Future Integration Points:
- TheoryRegistry: Belief IDs designed to be compatible with prediction_id format
- Bridge Warrants: applicability fields preserved for Sprint 3
- Dual Epistemology: Mapper produces data consumable by both tracks

References:
- Quine, W.V.O. (1951). Two Dogmas of Empiricism. Philosophical Review.
- BonJour, L. (1985). The Structure of Empirical Knowledge. Harvard.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import os
import re

# Import target structures from web of belief
from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType,
    ScopeConditions,
)

# Import semantic status from refined epistemic (for future use)
from src.services.refined_epistemic import SemanticStatus

# Import embedding-based theory matcher (TD-A: Theory Inference)
from src.services.theory_matcher import (
    TheoryMatchResult,
    get_theory_matcher,
)

# Import scope extractor (TD-B: Scope Extraction)
from src.services.scope_extractor import (
    extract_scope_from_claim,
)

# BN Coherence Integration (ARCH-4 Sprint 1.3)
from src.services.bn_coherence_client import (
    BNCoherenceClient,
)

# Phase 1B: Extraction Quality Gate
from src.qa.extraction_field_validator import (
    ExtractionFieldValidator,
)

# OC-3: Outcome Resolver Integration
try:
    from lib.outcome_resolver import resolve_outcome
    _HAS_OUTCOME_RESOLVER = True
except ImportError:
    _HAS_OUTCOME_RESOLVER = False

logger = logging.getLogger(__name__)

# Coherence check configuration
BN_COHERENCE_ENABLED = os.environ.get("AE_BN_COHERENCE_ENABLED", "true").lower() == "true"
BN_COHERENCE_BLOCK_CONFLICTS = os.environ.get("AE_BN_COHERENCE_BLOCK_CONFLICTS", "false").lower() == "true"

# Phase 1B: Quality gate configuration
VALIDATOR_BLOCKING_ENABLED = os.environ.get("ATLAS_VALIDATOR_BLOCKING", "true").lower() == "true"
QUALITY_THRESHOLD = float(os.environ.get("ATLAS_QUALITY_THRESHOLD", "0.75"))


# =============================================================================
# MAPPING CONFIGURATION
# =============================================================================

# Map claim_type to EpistemicLevel
# Expert Panel Resolution (2026-01-18):
#   - "mechanistic" → INTERMEDIATE (not THEORETICAL)
#   - Mechanistic claims are higher-generality generalizations, not core theory commitments
#   - True THEORETICAL: "nature reduces stress" (core theory statement)
#   - INTERMEDIATE: "reduced cortisol mediates nature's stress effects" (mechanistic)
CLAIM_TYPE_TO_LEVEL: Dict[str, EpistemicLevel] = {
    "mechanistic": EpistemicLevel.INTERMEDIATE,    # Mechanistic = higher-generality generalization
    "causal": EpistemicLevel.INTERMEDIATE,         # Generalizations
    "associational": EpistemicLevel.EMPIRICAL,     # Single-study findings
    "moderated": EpistemicLevel.EMPIRICAL,         # With moderator metadata
    "descriptive": EpistemicLevel.OBSERVATIONAL,   # Direct measurements
    "null": EpistemicLevel.EMPIRICAL,              # Null findings
}

# Entrenchment boost for mechanistic claims (they license more inferences)
MECHANISTIC_ENTRENCHMENT_BOOST: float = 0.15

# Theory inference threshold (configurable via environment variable)
# Expert Panel Resolution (2026-01-18):
#   - Default 0.4 is reasonable for discriminating multi-source theories
#   - Can be adjusted via AE_THEORY_THRESHOLD env var for different corpora
THEORY_THRESHOLD: float = float(os.environ.get("AE_THEORY_THRESHOLD", "0.4"))

# Secondary theory threshold for multi-theory attachment
# Theories scoring above this get attached as secondary
SECONDARY_THEORY_THRESHOLD: float = float(os.environ.get("AE_SECONDARY_THEORY_THRESHOLD", "0.3"))

# Enable embedding-based theory matching (TD-A: Theory Inference)
# When True, uses sentence-transformers for semantic similarity
# Falls back to keyword matching if embeddings unavailable
USE_EMBEDDING_THEORY_MATCHING: bool = os.environ.get("AE_USE_EMBEDDING_THEORY", "true").lower() == "true"

# Map rule_type + polarity to ConstraintType
RULE_TYPE_TO_CONSTRAINT: Dict[str, ConstraintType] = {
    "edge": ConstraintType.SUPPORTS,         # Default for edges
    "cpd_hint": ConstraintType.SUPPORTS,     # CPD hints are supportive
    "prior": ConstraintType.SUPPORTS,        # Prior information
    "constraint": ConstraintType.SUPPORTS,   # Explicit constraints
    "interaction": ConstraintType.ANALOGOUS, # Interactions are analogous
}

# Map polarity to constraint behavior
# Expert Panel Resolution (2026-01-18):
#   - Null findings CONTRADICT the predicted effect (not INDEPENDENT)
#   - Strength 0.6 reflects that null findings are meaningful evidence
#   - INDEPENDENT was wrong: a null is evidence against, not absence of evidence
POLARITY_MODIFIERS: Dict[str, Tuple[ConstraintType, float]] = {
    "positive": (ConstraintType.SUPPORTS, 1.0),
    "negative": (ConstraintType.CONTRADICTS, 1.0),
    "null": (ConstraintType.CONTRADICTS, 0.6),   # Null findings contradict the effect
    "u_shaped": (ConstraintType.SUPPORTS, 0.7),  # Partial support
    "unknown": (ConstraintType.SUPPORTS, 0.5),   # Uncertain support
}

# Theory inference: outcome domains → likely theories
# This mapping uses the outcome taxonomy structure
OUTCOME_DOMAIN_TO_THEORY: Dict[str, List[str]] = {
    "cog": ["ART", "Predictive_Processing"],           # Attention, cognitive processes
    "cog.attention": ["ART"],                          # Specifically attention → ART
    "cog.attention.sustained": ["ART"],
    "cog.attention.selective": ["ART"],
    "cog.memory": ["ART", "Predictive_Processing"],
    "cog.performance": ["ART"],
    "affect": ["SRT", "Biophilia"],                    # Emotional/stress outcomes
    "affect.stress": ["SRT"],
    "affect.mood": ["SRT", "Biophilia"],
    "affect.anxiety": ["SRT"],
    "physio": ["SRT"],                                 # Physiological outcomes
    "physio.alertness": ["SRT", "ART"],
    "physio.fatigue": ["SRT", "ART"],
    "physio.thermal": ["Adaptive_Thermal_Comfort"],
    "health": ["SRT", "Biophilia"],
    "health.wellbeing": ["SRT", "Biophilia"],
    "behav": ["ART", "SRT"],
    "behav.productivity": ["ART"],
    "behav.adaptive": ["Adaptive_Thermal_Comfort", "Privacy_Regulation"],
    "social": ["Biophilia", "Privacy_Regulation"],
    "social.privacy": ["Privacy_Regulation"],
    "social.crowding": ["Privacy_Regulation"],
    "social.interaction": ["Privacy_Regulation"],
    "affect.preference": ["Kaplan_Preference_Matrix"],
    "affect.aesthetics": ["Kaplan_Preference_Matrix"],
    "affect.comfort.thermal": ["Adaptive_Thermal_Comfort"],
    "spatial.configuration": ["Space_Syntax"],
    "spatial.navigation.wayfinding": ["Space_Syntax", "SN"],
    "spatial.movement": ["Space_Syntax"],
    "spatial.integration": ["Space_Syntax"],
    "spatial.intelligibility": ["Space_Syntax"],
    "behav.pedestrian": ["Space_Syntax"],
    "affect.spatial.disorientation": ["Space_Syntax"],
    "affect.perceived.safety.spatial": ["Space_Syntax", "Prospect_Refuge"],
    "acoustic.perception": ["Soundscape_Theory"],
    "acoustic.annoyance": ["Soundscape_Theory"],
    "acoustic.comfort": ["Soundscape_Theory"],
    "acoustic.restoration": ["Soundscape_Theory", "ART"],
    "health.noise": ["Soundscape_Theory"],
    "physio.cortisol.noise": ["Soundscape_Theory", "SRT"],
    "affect.soundscape": ["Soundscape_Theory"],
    "place.attachment": ["Place_Attachment"],
    "place.identity": ["Place_Attachment"],
    "place.familiarity": ["Place_Attachment", "SN"],
    "behav.relocation": ["Place_Attachment"],
    "affect.displacement": ["Place_Attachment"],
    "affect.rootedness": ["Place_Attachment"],
    "health.aging.place": ["Place_Attachment"],
    "affect.grief.relocation": ["Place_Attachment"],
}

# Theory inference: environmental factors (IVs) -> likely theories
ENVIRONMENT_DOMAIN_TO_THEORY: Dict[str, List[str]] = {
    "nature": ["ART", "SRT", "Biophilia"],
    "green": ["ART", "SRT", "Biophilia"],
    "plant": ["ART", "SRT", "Biophilia"],
    "outdoor": ["ART", "SRT", "Biophilia"],
    "park": ["ART", "SRT", "Biophilia"],
    "privacy": ["Privacy_Regulation"],
    "partition": ["Privacy_Regulation"],
    "enclosure": ["Privacy_Regulation"],
    "complexity": ["Kaplan_Preference_Matrix"],
    "mystery": ["Kaplan_Preference_Matrix"],
    "coherence": ["Kaplan_Preference_Matrix"],
    "natural_ventilation": ["Adaptive_Thermal_Comfort"],
    "operable_window": ["Adaptive_Thermal_Comfort"],
    "temperature": ["Adaptive_Thermal_Comfort"],
    "thermal": ["Adaptive_Thermal_Comfort"],
    "isovist": ["Space_Syntax", "Prospect_Refuge"],
    "integration": ["Space_Syntax"],
    "configuration": ["Space_Syntax"],
    "connectivity": ["Space_Syntax"],
    "topological_depth": ["Space_Syntax"],
    "spatial_layout": ["Space_Syntax"],
    "acoustic": ["Soundscape_Theory"],
    "noise": ["Soundscape_Theory"],
    "sound": ["Soundscape_Theory"],
    "traffic": ["Soundscape_Theory"],
    "birdsong": ["Soundscape_Theory"],
    "masking_sound": ["Soundscape_Theory"],
    "music": ["Soundscape_Theory"],
    "residence_length": ["Place_Attachment"],
    "length_of_stay": ["Place_Attachment"],
    "relocation": ["Place_Attachment"],
    "displacement": ["Place_Attachment"],
    "familiarity": ["Place_Attachment"],
    "personalization": ["Place_Attachment"],
    "ownership": ["Place_Attachment"],
    "duration": ["Place_Attachment"],
}

# Theory keywords in statements (fallback for inference)
THEORY_KEYWORDS: Dict[str, List[str]] = {
    "ART": ["attention restoration", "attention restorative", "ART", "directed attention",
            "soft fascination", "involuntary attention", "kaplan", "mental fatigue"],
    "SRT": ["stress recovery", "SRT", "ulrich", "cortisol", "heart rate", "HPA",
            "parasympathetic", "stress reduction", "physiological recovery"],
    "Biophilia": ["biophilia", "biophilic", "wilson", "innate", "evolved preference",
                  "evolutionary", "habitat", "savanna"],
    "Perceptual_Fluency": ["fluency", "processing ease", "fractal", "complexity",
                          "visual preference", "aesthetic"],
    "Predictive_Processing": ["predictive", "prediction error", "bayesian brain",
                             "expectation", "surprise"],
    "Privacy_Regulation": ["privacy regulation", "altman", "crowding", "personal space",
                           "territoriality", "social contact", "boundary regulation"],
    "Kaplan_Preference_Matrix": ["kaplan preference", "environmental preference", "coherence",
                                 "complexity", "legibility", "mystery"],
    "Adaptive_Thermal_Comfort": ["adaptive thermal", "thermal comfort", "de dear", "brager",
                                 "pmv", "natural ventilation", "temperature preference"],
    "Space_Syntax": ["space syntax", "hillier", "hanson", "axial analysis", "segment analysis",
                     "integration value", "mean depth", "connectivity", "intelligibility",
                     "natural movement", "isovist", "syntactic", "spatial network",
                     "pedestrian flow", "topological depth", "angular analysis", "depthmap"],
    "Soundscape_Theory": ["soundscape", "acoustic environment", "noise annoyance", "sound perception",
                          "ISO 12913", "axelsson", "kang", "schafer", "soundscape evaluation",
                          "pleasantness", "eventfulness", "acoustic comfort", "noise sensitivity",
                          "sound masking", "speech intelligibility", "biophilic sound", "noise exposure",
                          "environmental noise", "perceived noise", "acoustic restoration",
                          "circumplex", "soundscape design"],
    "Place_Attachment": ["place attachment", "sense of place", "place identity", "rootedness",
                         "topophilia", "place bonding", "scannell", "gifford", "lewicka",
                         "tuan", "altman", "relocation", "displacement", "aging in place",
                         "territorial familiarity", "biographical memory place",
                         "place meaning", "home attachment", "place disruption",
                         "post-disaster recovery place", "personalization attachment"],
}


# =============================================================================
# DATA CLASSES FOR MAPPING RESULTS
# =============================================================================

@dataclass
class MappingResult:
    """Result of mapping a single claim or rule."""
    success: bool
    entity_id: str
    entity_type: str  # "belief" or "constraint"
    entity: Optional[Any] = None

    # Diagnostic info
    theory_inferences: Dict[str, float] = field(default_factory=dict)
    # Multi-theory attachment: all theories above secondary threshold
    # Expert Panel Resolution (2026-01-18): Allow multi-theory attachment
    theory_ids: Dict[str, float] = field(default_factory=dict)
    primary_theory_id: Optional[str] = None
    is_stub: bool = False
    stub_reason: Optional[str] = None
    inference_trace: List[str] = field(default_factory=list)  # Audit trail for theory inference
    warnings: List[str] = field(default_factory=list)

    # TD-A: Enhanced theory inference fields
    theory_inference_method: str = "legacy"  # "legacy", "embedding", "hybrid"
    theory_confidence: float = 0.0
    needs_theory_review: bool = False
    theory_review_reason: Optional[str] = None
    disambiguation_applied: bool = False

    # Sprint 2.6 Track A: P-TC Panel Decisions (Task Context)
    # D1: How task type was determined
    inference_basis: str = "unknown"  # "stated", "inferred", "unknown"
    # D3: Flag for low-confidence keyword inference
    review_recommended: bool = False
    # D4: Whether ecological validity was presumed (not explicitly stated)
    presumed_lab: bool = False
    # D6: Effective demand computed from skill × cognitive_demand
    effective_demand: Optional[str] = None  # "very_high", "high", "moderate", "low", "very_low"
    # D7: Pure psych/neuro paper without architectural application
    mechanism_only: bool = False

    # Sprint CREDENCE-WARRANT: Warrant-derived credence (§48.3B)
    warrant_credence: Optional[Any] = None  # Credence object from warrant computation
    omega_audit: Optional[Dict[str, Any]] = None  # Full ω decomposition for auditability
    credence_discrepancy: Optional[float] = None  # |old - new| credence if > 0.15 (R6)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'theory_inferences': self.theory_inferences,
            'theory_ids': self.theory_ids,
            'primary_theory_id': self.primary_theory_id,
            'is_stub': self.is_stub,
            'stub_reason': self.stub_reason,
            'inference_trace': self.inference_trace,
            'warnings': self.warnings,
            # TD-A fields
            'theory_inference_method': self.theory_inference_method,
            'theory_confidence': self.theory_confidence,
            'needs_theory_review': self.needs_theory_review,
            'theory_review_reason': self.theory_review_reason,
            'disambiguation_applied': self.disambiguation_applied,
            # Sprint 2.6 Track A: P-TC Panel fields
            'inference_basis': self.inference_basis,
            'review_recommended': self.review_recommended,
            'presumed_lab': self.presumed_lab,
            'effective_demand': self.effective_demand,
            'mechanism_only': self.mechanism_only,
        }


@dataclass
class IntegrationReport:
    """Report from integrating a batch of claims/rules into the web."""
    n_claims_processed: int = 0
    n_claims_success: int = 0
    n_rules_processed: int = 0
    n_rules_success: int = 0
    n_stubs: int = 0
    n_anomalies: int = 0

    theory_distribution: Dict[str, int] = field(default_factory=dict)
    level_distribution: Dict[str, int] = field(default_factory=dict)
    stub_reasons: Dict[str, int] = field(default_factory=dict)

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    coherence_before: Optional[float] = None
    coherence_after: Optional[float] = None

    # BN coherence check stats (ARCH-4 Sprint 1.3)
    bn_coherence_stats: Dict[str, int] = field(default_factory=dict)

    # Phase 1B: Quality validator gate stats
    validator_stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'summary': {
                'claims_processed': self.n_claims_processed,
                'claims_success': self.n_claims_success,
                'rules_processed': self.n_rules_processed,
                'rules_success': self.n_rules_success,
                'stubs': self.n_stubs,
                'anomalies': self.n_anomalies
            },
            'distributions': {
                'by_theory': self.theory_distribution,
                'by_level': self.level_distribution,
                'stub_reasons': self.stub_reasons
            },
            'coherence': {
                'before': self.coherence_before,
                'after': self.coherence_after,
                'delta': (self.coherence_after - self.coherence_before)
                         if self.coherence_before and self.coherence_after else None
            },
            'bn_coherence': self.bn_coherence_stats,
            'validator_gate': self.validator_stats,
            'warnings': self.warnings,
            'errors': self.errors
        }


# =============================================================================
# CORE MAPPING FUNCTIONS
# =============================================================================

def infer_epistemic_level(claim_type: str) -> EpistemicLevel:
    """
    Map claim_type to EpistemicLevel.
    
    Expert Panel Decision Point:
    - Is the mapping from claim_type to epistemic level philosophically sound?
    - Should "mechanistic" really be THEORETICAL, or is it INTERMEDIATE?
    """
    return CLAIM_TYPE_TO_LEVEL.get(claim_type, EpistemicLevel.EMPIRICAL)


def infer_semantic_status(claim: Dict[str, Any]) -> SemanticStatus:
    """
    Infer Boghossian semantic status from claim characteristics.
    
    Most extracted claims are SYNTHETIC (empirical claims).
    CRITERIAL claims would be measurement-defining (rare in extractions).
    """
    claim_type = claim.get("claim_type", "")
    
    # Mechanistic claims about definitions/measures might be criterial
    if claim_type == "mechanistic":
        statement = claim.get("statement", "").lower()
        if any(w in statement for w in ["measures", "reflects", "indicates", "defines"]):
            return SemanticStatus.CRITERIAL
        return SemanticStatus.CENTRAL_SYNTHETIC
    
    # Most claims are synthetic
    if claim_type in ["causal", "associational", "moderated"]:
        return SemanticStatus.SYNTHETIC
    
    # Descriptive and null are peripheral
    return SemanticStatus.PERIPHERAL


def _diminishing_returns_combine(current: float, new_score: float) -> float:
    """
    Combine scores using diminishing returns formula.

    Expert Panel Resolution (2026-01-18):
    - Multiple signals for the same theory should boost confidence
    - But each additional signal adds less than the previous
    - Formula: combined = 1 - (1 - current) * (1 - new * 0.5)
    - This prevents runaway accumulation while rewarding corroboration

    Example:
    - 0.0 + 0.6 → 0.30 (first signal worth half its value)
    - 0.3 + 0.6 → 0.51 (second signal still helps, but less)
    - 0.5 + 0.6 → 0.65 (third signal helps even less)
    """
    if current == 0:
        return new_score * 0.5
    return 1 - (1 - current) * (1 - new_score * 0.5)


@dataclass
class TheoryInferenceResult:
    """Result of theory inference with audit trail."""
    relevance: Dict[str, float]
    trace: List[str]  # Human-readable audit trail
    # TD-A additions
    method: str = "legacy"  # "legacy", "embedding", "hybrid"
    confidence: float = 0.0
    needs_review: bool = False
    review_reason: Optional[str] = None
    disambiguation_applied: bool = False


def infer_theory_relevance_enhanced(
    claim: Dict[str, Any],
    outcome_lookup: Optional[Dict[str, Any]] = None,
    use_embeddings: bool = True
) -> TheoryInferenceResult:
    """
    Enhanced theory inference using embedding-based matching (TD-A).

    Combines:
    1. Embedding similarity (semantic matching via sentence-transformers)
    2. Outcome taxonomy mapping (structured knowledge)
    3. Disambiguation rules (false positive filtering)

    Args:
        claim: Claim dictionary with statement, constructs
        outcome_lookup: Optional outcome taxonomy
        use_embeddings: Whether to use embedding matching

    Returns:
        TheoryInferenceResult with relevance scores, confidence, and review flags
    """
    constructs = claim.get("constructs", {})
    outcomes = constructs.get("outcomes", [])
    environment_factors = constructs.get("environment_factors", [])
    statement = claim.get("statement", "")

    trace: List[str] = []
    relevance: Dict[str, float] = {}

    # Strategy 1: Embedding-based matching (if enabled and available)
    embedding_result: Optional[TheoryMatchResult] = None
    if use_embeddings and USE_EMBEDDING_THEORY_MATCHING:
        try:
            matcher = get_theory_matcher()
            # Build context from outcomes and environment
            outcome_ids = [o.get("id", "") for o in outcomes]
            env_ids = [e.get("id", "") for e in environment_factors]

            embedding_result = matcher.match_with_context(
                statement=statement,
                outcome_ids=outcome_ids if outcome_ids else None,
                environment_factors=env_ids if env_ids else None
            )

            # Use embedding scores as base
            relevance = embedding_result.scores.copy()
            trace.append(f"Embedding:{embedding_result.method.value} "
                        f"best={embedding_result.theory}:{embedding_result.confidence:.2f}")

            if embedding_result.disambiguation_applied:
                for note in embedding_result.disambiguation_notes:
                    trace.append(f"Disambiguation: {note}")

        except Exception as e:
            logger.warning(f"Embedding matching failed, falling back to legacy: {e}")
            embedding_result = None

    # Strategy 2: Outcome taxonomy mapping (always applied as boost)
    for outcome in outcomes:
        outcome_id = outcome.get("id", "")
        parts = outcome_id.split(".")
        for i in range(len(parts), 0, -1):
            partial_id = ".".join(parts[:i])
            if partial_id in OUTCOME_DOMAIN_TO_THEORY:
                for theory in OUTCOME_DOMAIN_TO_THEORY[partial_id]:
                    score = 0.5 + (i / len(parts)) * 0.3
                    old_val = relevance.get(theory, 0)
                    # If embeddings already scored this, use diminishing returns
                    if embedding_result and theory in embedding_result.scores:
                        relevance[theory] = _diminishing_returns_combine(old_val, score * 0.5)
                    else:
                        relevance[theory] = _diminishing_returns_combine(old_val, score)
                    trace.append(f"Outcome:{partial_id}→{theory} "
                               f"(combined: {old_val:.2f}→{relevance[theory]:.2f})")

    # Strategy 3: Environment factor mapping (always applied as boost)
    for env_factor in environment_factors:
        env_id = env_factor.get("id", "").lower()
        for env_keyword, theories in ENVIRONMENT_DOMAIN_TO_THEORY.items():
            if env_keyword in env_id:
                for theory in theories:
                    score = 1.2 # Maps to 0.6 through diminishing returns for first hit
                    old_val = relevance.get(theory, 0)
                    if embedding_result and theory in embedding_result.scores:
                        relevance[theory] = _diminishing_returns_combine(old_val, score * 0.5)
                    else:
                        relevance[theory] = _diminishing_returns_combine(old_val, score)
                    trace.append(f"EnvFactor:{env_id}→{theory} "
                               f"(combined: {old_val:.2f}→{relevance[theory]:.2f})")

    # Determine method and confidence
    if embedding_result:
        method = embedding_result.method.value
        confidence = embedding_result.confidence
        needs_review = embedding_result.needs_review
        review_reason = embedding_result.review_reason
        disambiguation_applied = embedding_result.disambiguation_applied
    else:
        method = "legacy"
        confidence = max(relevance.values()) if relevance else 0.0
        needs_review = confidence < THEORY_THRESHOLD
        review_reason = f"Low confidence: {confidence:.2f}" if needs_review else None
        disambiguation_applied = False

    return TheoryInferenceResult(
        relevance=relevance,
        trace=trace,
        method=method,
        confidence=confidence,
        needs_review=needs_review,
        review_reason=review_reason,
        disambiguation_applied=disambiguation_applied
    )


def infer_theory_relevance(
    claim: Dict[str, Any],
    outcome_lookup: Optional[Dict[str, Any]] = None
) -> Dict[str, float]:
    """
    Infer which theories this claim is relevant to.

    Uses three strategies with diminishing returns combination:
    1. Outcome taxonomy mapping (most reliable)
    2. Statement keyword matching (fallback)
    3. Environment factor matching (additional signal)

    Expert Panel Resolution (2026-01-18):
    - Uses diminishing returns instead of max() for score combination
    - Multiple signals boost confidence but don't accumulate unboundedly
    - Maintains audit trail for transparency

    Returns: Dict[theory_id, relevance_score (0-1)]
    """
    relevance: Dict[str, float] = {}
    trace: List[str] = []

    constructs = claim.get("constructs", {})
    outcomes = constructs.get("outcomes", [])
    environment_factors = constructs.get("environment_factors", [])
    statement = claim.get("statement", "").lower()

    # Strategy 1: Outcome taxonomy mapping
    for outcome in outcomes:
        outcome_id = outcome.get("id", "")

        # Check hierarchical matches (e.g., cog.attention.sustained matches cog, cog.attention)
        parts = outcome_id.split(".")
        for i in range(len(parts), 0, -1):
            partial_id = ".".join(parts[:i])
            if partial_id in OUTCOME_DOMAIN_TO_THEORY:
                for theory in OUTCOME_DOMAIN_TO_THEORY[partial_id]:
                    # More specific matches get higher scores
                    score = 0.5 + (i / len(parts)) * 0.3
                    old_val = relevance.get(theory, 0)
                    relevance[theory] = _diminishing_returns_combine(old_val, score)
                    trace.append(f"Outcome:{partial_id}→{theory} score={score:.2f} (combined: {old_val:.2f}→{relevance[theory]:.2f})")

    # Strategy 2: Keyword matching
    for theory, keywords in THEORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in statement:
                # Keywords in statement provide moderate signal
                old_val = relevance.get(theory, 0)
                relevance[theory] = _diminishing_returns_combine(old_val, 0.6)
                trace.append(f"Keyword:'{keyword}'→{theory} score=0.60 (combined: {old_val:.2f}→{relevance[theory]:.2f})")
                break

    # Strategy 3: Environment factor mapping
    for env_factor in environment_factors:
        env_id = env_factor.get("id", "").lower()
        for env_keyword, theories in ENVIRONMENT_DOMAIN_TO_THEORY.items():
            if env_keyword in env_id:
                for theory in theories:
                    old_val = relevance.get(theory, 0)
                    relevance[theory] = _diminishing_returns_combine(old_val, 1.2)
                    trace.append(f"EnvFactor:{env_id}→{theory} score=1.2 (combined: {old_val:.2f}→{relevance[theory]:.2f})")

    # Log trace at debug level
    if trace:
        logger.debug(f"Theory inference trace for claim: {trace}")

    return relevance


@dataclass
class CredenceResult:
    """Result of credence computation with evidential direction."""
    credence: "Credence"
    evidential_direction: str  # "supports", "contradicts", or "neutral"


def compute_credence_from_statistics(
    ae_confidence: float,
    statistics: Dict[str, Any],
    claim_type: str
) -> CredenceResult:
    """
    Compute initial credence from AE confidence and statistics.

    Expert Panel Resolution (2026-01-18):
    - No automatic credence penalty for null findings
    - Null findings are valid evidence that happened NOT to find an effect
    - Track evidential direction separately from credence value

    Combines:
    - ae_confidence: Extraction confidence (how sure we are about the claim)
    - p_value: Statistical significance (if available)
    - effect_size: Magnitude of effect
    """
    # Base credence from AE confidence
    base_value = ae_confidence

    # Adjust for p-value if available
    p_value = statistics.get("p_value")
    if p_value is not None:
        # Coerce string p-values (e.g., "<0.001", "0.05") to float
        if isinstance(p_value, str):
            p_str = p_value.strip().lstrip("<>≤≥~ ")
            try:
                p_value = float(p_str)
            except (ValueError, TypeError):
                p_value = None
    if p_value is not None:
        if p_value < 0.001:
            base_value = min(0.9, base_value * 1.1)
        elif p_value < 0.05:
            pass  # No adjustment
        elif p_value > 0.1:
            base_value = max(0.3, base_value * 0.8)

    # Expert Panel Resolution: NO automatic penalty for null findings
    # Null findings are valid evidence with the same credence as positive findings
    # The direction (supports vs contradicts) is tracked separately

    # Compute uncertainty (meta-uncertainty)
    # Higher with fewer statistics, lower with more
    effect_size = statistics.get("effect_size", {})
    ci95 = statistics.get("ci95")

    uncertainty = 0.4  # Default
    if effect_size.get("value") is not None and ci95 is not None:
        # Have both effect size and CI: lower uncertainty
        uncertainty = 0.25
    elif effect_size.get("value") is not None or ci95 is not None:
        uncertainty = 0.35

    # Determine evidential direction
    if claim_type == "null":
        evidential_direction = "contradicts"  # Null findings contradict the effect
        n_supporting = 0
        n_contradicting = 1
    else:
        evidential_direction = "supports"
        n_supporting = 1
        n_contradicting = 0

    credence = Credence(
        value=max(0.1, min(0.9, base_value)),
        uncertainty=uncertainty,
        n_supporting=n_supporting,
        n_contradicting=n_contradicting,
        n_observations=1
    )

    return CredenceResult(credence=credence, evidential_direction=evidential_direction)


def compute_credence_from_warrants(
    claim: Dict[str, Any],
    theory_id: Optional[str] = None,
    tea_scores: Optional[Dict[str, float]] = None
) -> Tuple[Optional["Credence"], Optional[Dict[str, Any]]]:
    """
    Compute warrant-derived credence per §48.3B (Sprint CREDENCE-WARRANT Phase 4).

    This function implements the panel-approved credence formula that replaces
    the naive statistics-based credence with a principled warrant-derived value.

    The function:
    1. Infers study design characteristics from the extraction claim
    2. Computes ω (warrant strength) via the 5-component formula
    3. Builds a projection edge from the extraction
    4. Computes credence via σ(d · ω · δ · logit(p_lab))

    For the R6 dual-credence transition period, callers should compute BOTH
    the old (statistics-based) and new (warrant-based) credence and flag
    discrepancies > 0.15 for manual review.

    Args:
        claim: Extraction claim dict with study metadata
        theory_id: Optional theory identifier for mechanism edges
        tea_scores: Pre-loaded TEA scores dict (loads from default if None)

    Returns:
        Tuple of:
        - Credence object (or None if computation fails)
        - omega_audit dict with full ω decomposition (or None)

    Reference:
        ATLAS §48.3B: Warrant Strength Assignment and Credence-Warrant Integration
        Panel Revision R6 (Cartwright): Dual credence transition period
    """
    try:
        from src.services.warrant_strength import (
            compute_omega_from_extraction,
            compute_credence_from_warrants as _warrant_credence,
            DesignType,
            PublicationType,
            CANONICAL_DISCOUNT_FACTORS,
        )
    except ImportError:
        logger.warning("warrant_strength module not available; skipping warrant credence")
        return None, None

    statistics = claim.get("statistics", {})
    study = claim.get("study", {})
    claim_type = claim.get("claim_type", "associational")
    ae_confidence = claim.get("ae_confidence", 0.5)

    # Infer design type from claim metadata
    design_type = _infer_design_type(claim)
    sample_size = _extract_sample_size(claim)
    is_mechanism_edge = claim_type in ("mechanistic", "causal_mechanism")

    # Build the finding dict for omega computation
    finding = {
        "design_type": design_type,
        "sample_size": sample_size,
        "pre_registered": study.get("pre_registered", False),
        "blinded": study.get("blinded", False),
        "self_report_only": study.get("self_report_only", False),
        "n_uncontrolled_confounds": study.get("n_uncontrolled_confounds", 0),
        "has_randomization": study.get("has_randomization", False),
        "has_active_control": study.get("has_active_control", False),
        "n_independent_replications": study.get("n_independent_replications", 0),
        "n_conceptual_replications": study.get("n_conceptual_replications", 0),
        "publication_type": study.get("publication_type", "peer_reviewed"),
        "is_mechanism_edge": is_mechanism_edge,
        "mechanism_specificity": study.get("mechanism_specificity", 0.5),
    }

    omega_result = compute_omega_from_extraction(finding, theory_id=theory_id, tea_scores=tea_scores)

    # Infer p_lab (laboratory effect probability) from statistics
    # This is the probability of the effect in the study context
    p_lab = _estimate_p_lab(ae_confidence, statistics)

    # Infer warrant type from claim characteristics
    tau = _infer_warrant_type(claim_type, is_mechanism_edge)

    # Build projection edge
    edge = {
        "p_lab": p_lab,
        "tau": tau,
        "omega": omega_result.omega,
        "delta": 1.0,  # Default: assume populations identical for now
    }

    # Compute warrant-derived credence
    warrant_credence_value = _warrant_credence([edge])

    # Determine evidential direction
    if claim_type == "null":
        n_supporting = 0
        n_contradicting = 1
    else:
        n_supporting = 1
        n_contradicting = 0

    # Compute uncertainty from omega: higher ω → lower uncertainty
    uncertainty = max(0.25, 0.50 * (1.0 - omega_result.omega))

    credence = Credence(
        value=max(0.1, min(0.9, warrant_credence_value)),
        uncertainty=uncertainty,
        n_supporting=n_supporting,
        n_contradicting=n_contradicting,
        n_observations=1
    )

    omega_audit = omega_result.to_dict()
    omega_audit["p_lab"] = p_lab
    omega_audit["tau"] = tau
    omega_audit["warrant_credence"] = warrant_credence_value

    return credence, omega_audit


def _infer_design_type(claim: Dict[str, Any]) -> str:
    """
    Infer DesignType string from extraction claim metadata.

    Examines claim_type, study metadata, and method descriptions to
    determine the most likely experimental design.

    Returns:
        Design type string matching DesignType enum values.
    """
    claim_type = claim.get("claim_type", "associational")
    study = claim.get("study", {})
    method = study.get("method", "").lower()
    design = study.get("design", "").lower()

    # Check for meta-analysis / systematic review first
    if claim_type in ("synthesis", "meta_analysis") or "meta-analysis" in method or "meta-analysis" in design:
        return "meta_analysis"
    if claim_type == "review" or "systematic review" in method:
        return "systematic_review"

    # Check for RCT indicators
    if any(kw in design for kw in ("randomized", "rct", "randomised")):
        sample_size = _extract_sample_size(claim)
        if sample_size and sample_size > 200 and study.get("pre_registered", False):
            return "large_rct"
        return "standard_rct"

    # Within-subjects / crossover
    if any(kw in design for kw in ("within-subjects", "crossover", "repeated measures", "within subjects")):
        return "within_subjects"

    # Quasi-experimental
    if any(kw in design for kw in ("quasi", "natural experiment", "interrupted time series", "quasi-experiment")):
        return "quasi_experimental"

    # Case study / qualitative
    if claim_type in ("qualitative", "case_study") or any(kw in method for kw in ("case study", "qualitative", "ethnograph")):
        return "case_study"

    # Default: observational for associational, standard_rct for causal/mechanistic
    if claim_type in ("mechanistic", "causal", "causal_mechanism", "experimental"):
        return "standard_rct"

    return "observational"


def _extract_sample_size(claim: Dict[str, Any]) -> Optional[int]:
    """Extract sample size from claim, coercing to int if possible."""
    study = claim.get("study", {})
    n = study.get("sample_size") or study.get("n") or claim.get("statistics", {}).get("n")
    if n is not None:
        try:
            return int(n)
        except (ValueError, TypeError):
            pass
    return None


def _estimate_p_lab(ae_confidence: float, statistics: Dict[str, Any]) -> float:
    """
    Estimate laboratory effect probability from extraction confidence and statistics.

    This bridges the extraction layer (which provides ae_confidence and p-values)
    to the projection layer (which expects p_lab as an effect probability).

    Heuristic:
    - ae_confidence is already a probability-like measure (0-1) of how likely
      the extracted claim is correct
    - Adjust upward for strong statistical evidence (low p, high effect)
    - Adjust downward for weak evidence

    Returns:
        p_lab ∈ (0.1, 0.9)
    """
    p_lab = ae_confidence

    p_value = statistics.get("p_value")
    if p_value is not None:
        if isinstance(p_value, str):
            p_str = p_value.strip().lstrip("<>≤≥~ ")
            try:
                p_value = float(p_str)
            except (ValueError, TypeError):
                p_value = None

    if p_value is not None:
        if p_value < 0.001:
            p_lab = min(0.9, p_lab * 1.1)
        elif p_value < 0.01:
            p_lab = min(0.85, p_lab * 1.05)
        elif p_value > 0.10:
            p_lab = max(0.3, p_lab * 0.85)

    effect_size = statistics.get("effect_size", {})
    es_value = effect_size.get("value")
    if es_value is not None:
        try:
            es_value = abs(float(es_value))
            if es_value > 0.8:  # Large effect
                p_lab = min(0.9, p_lab + 0.05)
            elif es_value < 0.2:  # Small effect
                p_lab = max(0.3, p_lab - 0.05)
        except (ValueError, TypeError):
            pass

    return max(0.1, min(0.9, p_lab))


def _infer_warrant_type(claim_type: str, is_mechanism_edge: bool) -> str:
    """
    Infer warrant type (τ) from claim characteristics.

    Maps extraction-level claim types to the ATLAS warrant type taxonomy
    used in the projection calculus.

    Returns:
        String matching CANONICAL_DISCOUNT_FACTORS keys.
    """
    if is_mechanism_edge or claim_type in ("mechanistic", "causal_mechanism"):
        return "mechanism"
    if claim_type in ("constitutive", "definitional"):
        return "constitutive"
    if claim_type in ("functional", "capacity_functional"):
        return "functional"
    if claim_type in ("theoretical", "theory_derived"):
        return "theory_derived"
    if claim_type in ("analogical", "cross_domain"):
        return "analogical"
    # Default: empirical association
    return "empirical_association"


def claim_to_belief(
    claim: Dict[str, Any],
    web: Optional[WebOfBelief] = None,
    outcome_lookup: Optional[Dict[str, Any]] = None
) -> MappingResult:
    """
    Map an ae.claim.v1 record to a Belief node.
    
    Args:
        claim: Dictionary conforming to ae.claim.v1.schema.json
        web: Optional WebOfBelief for context (existing beliefs, theories)
        outcome_lookup: Optional outcome taxonomy for theory inference
    
    Returns:
        MappingResult containing the Belief and diagnostic info
    """
    result = MappingResult(
        success=False,
        entity_id=claim.get("claim_id", "unknown"),
        entity_type="belief"
    )
    
    try:
        claim_id = claim.get("claim_id")
        claim_type = claim.get("claim_type", "associational")
        statement = claim.get("statement", "")
        paper_id = claim.get("paper_id", "")
        statistics = claim.get("statistics", {})
        ae_confidence = claim.get("ae_confidence", 0.5)
        constructs = claim.get("constructs", {})
        study = claim.get("study", {})
        
        # Infer epistemic level
        level = infer_epistemic_level(claim_type)

        # Infer theory relevance (TD-A: Use enhanced embedding-based matching)
        theory_result = infer_theory_relevance_enhanced(claim, outcome_lookup)
        theory_inferences = theory_result.relevance
        result.theory_inferences = theory_inferences

        # TD-A: Record enhanced inference metadata
        result.theory_inference_method = theory_result.method
        result.theory_confidence = theory_result.confidence
        result.needs_theory_review = theory_result.needs_review
        result.theory_review_reason = theory_result.review_reason
        result.disambiguation_applied = theory_result.disambiguation_applied
        result.inference_trace.extend(theory_result.trace)

        # Determine theory attachment with multi-theory support
        # Expert Panel Resolution (2026-01-18): Use configurable threshold and allow multi-theory
        theory_id = None
        attached_theories: Dict[str, float] = {}

        if theory_inferences:
            # Sort theories by score descending
            sorted_theories = sorted(theory_inferences.items(), key=lambda x: x[1], reverse=True)
            best_theory, best_score = sorted_theories[0]

            # Primary theory: must meet main threshold
            if best_score >= THEORY_THRESHOLD:
                theory_id = best_theory
                result.primary_theory_id = best_theory
                result.inference_trace.append(f"Primary: {best_theory}={best_score:.2f} (threshold={THEORY_THRESHOLD})")

                # Attach secondary theories above secondary threshold
                for theory, score in sorted_theories:
                    if score >= SECONDARY_THEORY_THRESHOLD:
                        attached_theories[theory] = score
                        if theory != best_theory:
                            result.inference_trace.append(f"Secondary: {theory}={score:.2f}")
            else:
                result.is_stub = True
                result.stub_reason = f"Theory scores below threshold (best: {best_theory}={best_score:.2f}, threshold={THEORY_THRESHOLD})"
                result.inference_trace.append(f"Stub: best={best_theory}={best_score:.2f} < threshold={THEORY_THRESHOLD}")
        else:
            result.is_stub = True
            result.stub_reason = "No theory relevance inferred from outcomes or statement"
            result.inference_trace.append("Stub: no theory relevance detected")

        result.theory_ids = attached_theories

        # Compute credence (returns CredenceResult with evidential_direction)
        credence_result = compute_credence_from_statistics(ae_confidence, statistics, claim_type)
        credence = credence_result.credence

        # R6 Dual-Credence Transition: compute warrant-derived credence alongside
        warrant_credence, omega_audit = compute_credence_from_warrants(
            claim, theory_id=theory_id
        )
        if warrant_credence is not None:
            result.omega_audit = omega_audit
            result.warrant_credence = warrant_credence
            # Flag discrepancies > 0.15 for manual review (Panel Revision R6)
            discrepancy = abs(credence.value - warrant_credence.value)
            if discrepancy > 0.15:
                result.credence_discrepancy = discrepancy
                result.review_recommended = True
                result.inference_trace.append(
                    f"R6 DISCREPANCY: statistics_credence={credence.value:.3f} vs "
                    f"warrant_credence={warrant_credence.value:.3f} (Δ={discrepancy:.3f} > 0.15)"
                )
            # During transition: use warrant credence as primary (it's the improved formula)
            credence = warrant_credence

        # Determine status
        # Expert Panel Resolution (2026-01-18): Null findings are NOT automatically ANOMALOUS
        # They are valid TENTATIVE evidence that happens to contradict an effect
        if result.is_stub:
            status = BeliefStatus.STUB
        else:
            status = BeliefStatus.TENTATIVE
            if claim_type == "null":
                result.inference_trace.append(f"Evidential direction: {credence_result.evidential_direction}")
        
        # Extract temporal parameters if available
        temporal_params = None
        effect_size = statistics.get("effect_size", {})
        if effect_size.get("value") is not None:
            # Could track temporal onset/duration if encoded in study.task
            pass  # Future enhancement
        
        # Compute entrenchment (mechanistic claims get a boost)
        base_entrenchment = 0.3 if not result.is_stub else 0.1
        if claim_type == "mechanistic":
            base_entrenchment += MECHANISTIC_ENTRENCHMENT_BOOST

        # Extract scope conditions (Panel Fix 2026-01-23)
        scope = _extract_scope(claim)
        environment_id = _extract_environment_id(claim)
        outcome_id = _extract_outcome_id(claim)

        # Sprint 2.6 Track A: Task context extraction (P-TC Panel)
        task_context = extract_task_context(claim)
        result.inference_basis = task_context.inference_basis
        result.review_recommended = task_context.review_recommended or result.needs_theory_review

        # D4: Presumed lab when ecological validity not explicitly stated
        result.presumed_lab = not scope.scope_specified

        # D6: Compute effective demand (default skill_level = intermediate)
        result.effective_demand = compute_effective_demand(
            task_context.cognitive_demand,
            claim.get("study", {}).get("skill_level", "intermediate")
        )

        # D7: Check if mechanism-only paper
        result.mechanism_only = is_mechanism_only(claim)

        # Create the Belief
        belief = Belief(
            belief_id=claim_id,
            content=statement,
            level=level,
            status=status,
            credence=credence,
            _legacy_entrenchment=base_entrenchment,
            paper_ids=[paper_id],
            theory_id=theory_id,
            domain=_extract_domain(constructs),
            tags=_extract_tags(claim),
            # Sprint 6/7 fields (Panel Fix 2026-01-23)
            scope=scope,
            environment_id=environment_id,
            outcome_id=outcome_id,
        )
        
        result.entity = belief
        result.success = True
        
    except Exception as e:
        result.warnings.append(f"Error mapping claim: {str(e)}")
        logger.exception(f"Failed to map claim {claim.get('claim_id', 'unknown')}")
    
    return result


def rule_to_constraints(
    rule: Dict[str, Any],
    web: Optional[WebOfBelief] = None,
    claim_to_belief_map: Optional[Dict[str, str]] = None
) -> List[MappingResult]:
    """
    Map an ae.rule.v1 record to Constraint edge(s).
    
    A single rule can produce multiple constraints (one per lhs-rhs pair).
    
    Args:
        rule: Dictionary conforming to ae.rule.v1.schema.json
        web: Optional WebOfBelief for context
        claim_to_belief_map: Mapping from claim_ids to belief_ids
    
    Returns:
        List of MappingResults, one per constraint created
    """
    results = []
    
    try:
        rule_id = rule.get("rule_id")
        rule_type = rule.get("rule_type", "edge")
        lhs = rule.get("lhs", [])
        rhs = rule.get("rhs", [])
        polarity = rule.get("polarity", "unknown")
        strength = rule.get("strength", {})
        applicability = rule.get("applicability", {})
        evidence_links = rule.get("evidence_links", [])
        
        # Determine constraint type from polarity
        constraint_type, strength_modifier = POLARITY_MODIFIERS.get(
            polarity, (ConstraintType.SUPPORTS, 0.5)
        )
        
        # Extract strength value
        strength_value = strength.get("value", 0.5)
        if strength_value is None:
            strength_value = 0.5
        effective_strength = strength_value * strength_modifier
        
        # Get linked claim IDs for evidence
        evidence_claim_ids = [link.get("claim_id") for link in evidence_links]
        
        # Create constraints for each lhs-rhs combination
        constraint_idx = 0
        for lhs_item in lhs:
            for rhs_item in rhs:
                constraint_id = f"{rule_id}:c{constraint_idx}"
                constraint_idx += 1
                
                source_var = lhs_item.get("var", "")
                target_var = rhs_item.get("var", "")
                
                # If we have a claim-to-belief map, resolve IDs
                source_id = source_var
                target_id = target_var
                if claim_to_belief_map:
                    # Try to find beliefs for these variables
                    # (In practice, vars are construct IDs, not claim IDs)
                    pass  # Future enhancement
                
                constraint = Constraint(
                    constraint_id=constraint_id,
                    source_id=source_id,
                    target_id=target_id,
                    constraint_type=constraint_type,
                    strength=effective_strength,
                    bidirectional=(polarity != "positive" and polarity != "negative"),
                    evidence_ids=evidence_claim_ids
                )
                
                result = MappingResult(
                    success=True,
                    entity_id=constraint_id,
                    entity_type="constraint",
                    entity=constraint
                )
                results.append(result)
        
        # If no constraints created, report issue
        if not results:
            result = MappingResult(
                success=False,
                entity_id=rule_id,
                entity_type="constraint",
                warnings=["No lhs or rhs items to create constraints from"]
            )
            results.append(result)
            
    except Exception as e:
        result = MappingResult(
            success=False,
            entity_id=rule.get("rule_id", "unknown"),
            entity_type="constraint",
            warnings=[f"Error mapping rule: {str(e)}"]
        )
        results.append(result)
        logger.exception(f"Failed to map rule {rule.get('rule_id', 'unknown')}")
    
    return results


# =============================================================================
# BATCH INTEGRATION
# =============================================================================

def integrate_extraction(
    claims: List[Dict[str, Any]],
    rules: List[Dict[str, Any]],
    web: WebOfBelief,
    outcome_lookup: Optional[Dict[str, Any]] = None,
    seek_equilibrium: bool = True,
    equilibrium_iterations: int = 5
) -> IntegrationReport:
    """
    Integrate a batch of claims and rules into the web of belief.
    
    This is the main entry point for connecting the contract pipeline
    to the epistemic analysis engine.
    
    Args:
        claims: List of ae.claim.v1 records
        rules: List of ae.rule.v1 records
        web: WebOfBelief to integrate into
        outcome_lookup: Optional outcome taxonomy
        seek_equilibrium: Whether to run reflective equilibrium after integration
        equilibrium_iterations: Number of equilibrium iterations
    
    Returns:
        IntegrationReport with summary statistics
    """
    report = IntegrationReport()
    
    # Record initial coherence
    try:
        report.coherence_before = web.coherence_score()
    except Exception:
        report.coherence_before = 0.0
    
    # Track claim-to-belief mapping for rule resolution
    claim_to_belief_map: Dict[str, str] = {}
    
    # Initialize BN coherence client if enabled
    bn_client = None
    if BN_COHERENCE_ENABLED:
        bn_client = BNCoherenceClient()
        if bn_client.is_available:
            logger.info("BN coherence checking enabled")
        else:
            logger.warning("BN coherence requested but BN_graphical not available")

    # Track coherence check stats
    coherence_stats = {
        "checked": 0,
        "passed": 0,
        "conflicts": 0,
        "blocked": 0
    }

    # Phase 1B: Quality validation gate
    # Track findings blocked by validator
    validator_stats = {
        "checked": 0,
        "passed": 0,
        "blocked": 0,
        "blocked_by_field": {}
    }

    # Process claims
    for claim in claims:
        report.n_claims_processed += 1

        # Phase 1B: Check if this claim (finding) passes quality validation
        # Only validate if the claim has sufficient structure to be validated
        should_process_claim = True
        if VALIDATOR_BLOCKING_ENABLED and claim.get("antecedent") and claim.get("consequent"):
            validator_stats["checked"] += 1

            # Create a minimal extraction for validation
            # (validator expects article-level structure)
            temp_extraction = {
                "article_type": claim.get("claim_type", "empirical_finding"),
                "article_family": claim.get("article_family", "empirical"),
                "findings": [claim],
                "_meta": {"source": "extraction_to_web", "claim_id": claim.get("id", "unknown")}
            }

            try:
                validator = ExtractionFieldValidator()
                passed, score, violations = validator.validate_and_gate(
                    temp_extraction,  # Pass dict directly, not path
                    threshold=QUALITY_THRESHOLD
                )

                if not passed:
                    should_process_claim = False
                    validator_stats["blocked"] += 1

                    # Track which fields caused blocking
                    for violation in violations:
                        field = violation.get("field", "unknown")
                        validator_stats["blocked_by_field"][field] = \
                            validator_stats["blocked_by_field"].get(field, 0) + 1

                    logger.warning(
                        f"Finding blocked by quality gate: {claim.get('id', 'unknown')} "
                        f"(score={score:.3f} < {QUALITY_THRESHOLD}). "
                        f"Top violations: {violations[:3]}"
                    )
                    report.warnings.append(
                        f"Finding '{claim.get('id', 'unknown')}' blocked by validator "
                        f"(score {score:.3f} < {QUALITY_THRESHOLD})"
                    )
                else:
                    validator_stats["passed"] += 1

            except Exception as e:
                # If validator fails, log but continue (fail-open)
                logger.warning(f"Validator error for claim {claim.get('id', 'unknown')}: {e}")
                report.warnings.append(f"Validator error: {e}")
        else:
            # Claim doesn't have required fields for validation
            should_process_claim = True

        if not should_process_claim:
            # Skip this finding
            continue

        result = claim_to_belief(claim, web, outcome_lookup)

        if result.success and result.entity:
            belief = result.entity

            # BN Coherence Check (ARCH-4 Sprint 1.3)
            should_add = True
            if bn_client and bn_client.is_available:
                coherence_stats["checked"] += 1

                # Convert belief to dict for coherence check
                belief_dict = {
                    "belief_id": belief.belief_id,
                    "content": belief.content,
                    "confidence": belief.credence.value,
                    "level": belief.level.value if hasattr(belief.level, 'value') else str(belief.level)
                }

                # Get existing beliefs for conflict detection
                existing_beliefs = {
                    bid: {
                        "belief_id": bid,
                        "content": b.content,
                        "confidence": b.credence.value,
                        "level": b.level.value if hasattr(b.level, 'value') else str(b.level)
                    }
                    for bid, b in web.beliefs.items()
                }

                check_result = bn_client.check_single_belief(belief_dict, existing_beliefs)

                if check_result.has_conflicts:
                    coherence_stats["conflicts"] += 1
                    conflict_ids = [c.get("conflict_id", "unknown") for c in check_result.conflicts]
                    logger.warning(f"Belief '{belief.belief_id}' has conflicts: {conflict_ids}")

                    if BN_COHERENCE_BLOCK_CONFLICTS:
                        should_add = False
                        coherence_stats["blocked"] += 1
                        report.warnings.append(
                            f"Belief '{belief.belief_id}' blocked due to conflicts: {conflict_ids}"
                        )
                else:
                    coherence_stats["passed"] += 1

            if not should_add:
                continue

            # Add to web
            try:
                web.add_belief(belief)
                report.n_claims_success += 1
                claim_to_belief_map[result.entity_id] = belief.belief_id
                
                # Update distributions
                level_name = belief.level.value
                report.level_distribution[level_name] = report.level_distribution.get(level_name, 0) + 1
                
                if belief.theory_id:
                    report.theory_distribution[belief.theory_id] = \
                        report.theory_distribution.get(belief.theory_id, 0) + 1
                
                if result.is_stub:
                    report.n_stubs += 1
                    reason = result.stub_reason or "unknown"
                    report.stub_reasons[reason] = report.stub_reasons.get(reason, 0) + 1
                
                if belief.status == BeliefStatus.ANOMALOUS:
                    report.n_anomalies += 1
                    
            except Exception as e:
                report.errors.append(f"Failed to add belief {belief.belief_id}: {str(e)}")
        else:
            report.errors.extend(result.warnings)
    
    # Process rules
    for rule in rules:
        report.n_rules_processed += 1
        results = rule_to_constraints(rule, web, claim_to_belief_map)
        
        for result in results:
            if result.success and result.entity:
                constraint = result.entity
                
                # Only add constraint if both endpoints exist in web
                if constraint.source_id in web.beliefs and constraint.target_id in web.beliefs:
                    try:
                        web.add_constraint(constraint)
                        report.n_rules_success += 1
                    except Exception as e:
                        report.errors.append(f"Failed to add constraint {constraint.constraint_id}: {str(e)}")
                else:
                    # Constraint endpoints don't exist - this is expected for variable-level rules
                    # We'll handle this differently in future (create beliefs for variables)
                    pass
            else:
                report.warnings.extend(result.warnings)
    
    # Seek equilibrium if requested
    if seek_equilibrium and report.n_claims_success > 0:
        try:
            web.seek_equilibrium(max_iterations=equilibrium_iterations)
        except Exception as e:
            report.errors.append(f"Failed to seek equilibrium: {str(e)}")
    
    # Record final coherence
    try:
        report.coherence_after = web.coherence_score()
    except Exception:
        report.coherence_after = 0.0

    # Record BN coherence stats
    report.bn_coherence_stats = coherence_stats
    if coherence_stats.get("checked", 0) > 0:
        logger.info(
            f"BN coherence: {coherence_stats['passed']}/{coherence_stats['checked']} passed, "
            f"{coherence_stats['conflicts']} conflicts, {coherence_stats['blocked']} blocked"
        )

    # Record Phase 1B validator gate stats
    report.validator_stats = validator_stats
    if validator_stats.get("checked", 0) > 0:
        logger.info(
            f"Quality validator gate: {validator_stats['passed']}/{validator_stats['checked']} passed, "
            f"{validator_stats['blocked']} blocked"
        )
        if validator_stats.get("blocked_by_field"):
            top_fields = sorted(validator_stats["blocked_by_field"].items(),
                              key=lambda x: -x[1])[:3]
            logger.info(f"Top blocking fields: {', '.join(f'{k}={v}' for k, v in top_fields)}")

    return report


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _extract_domain(constructs: Dict[str, Any]) -> str:
    """Extract primary domain from constructs."""
    outcomes = constructs.get("outcomes", [])
    if outcomes:
        # Take first outcome's top-level domain
        outcome_id = outcomes[0].get("id", "")
        parts = outcome_id.split(".")
        return parts[0] if parts else ""
    return ""


def _extract_tags(claim: Dict[str, Any]) -> List[str]:
    """Extract tags from claim for categorization."""
    tags = []
    
    claim_type = claim.get("claim_type", "")
    if claim_type:
        tags.append(f"type:{claim_type}")
    
    constructs = claim.get("constructs", {})
    
    # Add outcome tags
    for outcome in constructs.get("outcomes", []):
        tags.append(f"outcome:{outcome.get('id', '')}")
    
    # Add moderator tags
    for moderator in constructs.get("moderators", []):
        tags.append(f"mod:{moderator.get('id', '')}")
    
    # Study design
    study = claim.get("study", {})
    design = study.get("design", "")
    if design:
        tags.append(f"design:{design}")
    
    return tags


def _extract_scope(claim: Dict[str, Any]) -> ScopeConditions:
    """
    Extract scope conditions from claim's study metadata.

    TD-B Enhancement: Uses enhanced scope extraction from statement text
    when structured metadata is sparse.

    Maps ae.claim.v1 study fields to ScopeConditions:
    - study.sample.population → population
    - study.sample.country → geography
    - study.setting[].id → setting
    - study.design → measurement context

    Panel Fix (2026-01-23): Ensures subject type constraints flow through
    to the belief for proper scope-boundary conflict detection.
    """
    study = claim.get("study", {})
    sample = study.get("sample", {})
    settings = study.get("setting", [])

    # Extract setting from first setting item if available
    setting_value = None
    if settings and isinstance(settings, list) and len(settings) > 0:
        setting_value = settings[0].get("id") or settings[0].get("notes")

    # Start with structured metadata
    population = sample.get("population")
    geography = sample.get("country")
    measurement = study.get("design")

    # TD-B: Enhance with NLP extraction from statement text
    # Only if structured data is sparse
    has_structured = bool(population) or bool(setting_value) or bool(geography)

    if not has_structured:
        # Use enhanced scope extraction from claim text
        try:
            extracted = extract_scope_from_claim(claim)

            # Fill in missing fields from extraction
            if not population and extracted.population:
                population = extracted.population
            if not setting_value and extracted.setting:
                setting_value = extracted.setting
            if not geography and extracted.geography:
                geography = extracted.geography
            if not measurement and extracted.methodology:
                measurement = extracted.methodology

            # Log extraction
            if extracted.explicit_fields:
                logger.debug(f"TD-B: Extracted scope fields: {extracted.explicit_fields}")

        except Exception as e:
            logger.warning(f"TD-B: Scope extraction failed: {e}")

    # Determine if scope was explicitly specified
    # Scope is specified if we have population OR setting OR country
    has_population = bool(population)
    has_setting = bool(setting_value)
    has_geography = bool(geography)
    scope_specified = has_population or has_setting or has_geography

    return ScopeConditions(
        population=population,
        setting=setting_value,
        geography=geography,
        measurement=measurement,
        scope_specified=scope_specified
    )


def _extract_environment_id(claim: Dict[str, Any]) -> Optional[str]:
    """
    Extract primary environment factor ID from claim.

    Maps ae.claim.v1 constructs.environment_factors to canonical ID.
    Used for taxonomy-based matching and conflict detection.
    """
    constructs = claim.get("constructs", {})
    env_factors = constructs.get("environment_factors", [])
    if env_factors and isinstance(env_factors, list) and len(env_factors) > 0:
        return env_factors[0].get("id")
    return None


def _extract_outcome_id(claim: Dict[str, Any]) -> Optional[str]:
    """
    Extract primary outcome ID from claim.

    Maps ae.claim.v1 constructs.outcomes to canonical ID.
    Used for taxonomy-based matching and theory inference.

    OC-3: Resolves outcome IDs to canonical form via outcome_resolver.
    """
    constructs = claim.get("constructs", {})
    outcomes = constructs.get("outcomes", [])
    if outcomes and isinstance(outcomes, list) and len(outcomes) > 0:
        raw_id = outcomes[0].get("id")
        if raw_id and _HAS_OUTCOME_RESOLVER:
            try:
                paper_id = claim.get("paper_id")
                claim_id = claim.get("node_id") or claim.get("id")
                resolved = resolve_outcome(str(raw_id))
                if resolved:
                    canonical_id = resolved['canonical_id']
                    logger.info(f"Resolved outcome: {raw_id} → {canonical_id}")
                    return canonical_id
            except Exception as e:
                logger.warning(f"Outcome resolution failed for {raw_id}: {e}")
        return raw_id
    return None


# =============================================================================
# SPRINT 2.6 TRACK A: TASK CONTEXT EXTRACTION (P-TC Panel Decisions)
# =============================================================================

# Common experimental task keywords for instrument detection (D2: 0.95 confidence)
COMMON_INSTRUMENTS: Dict[str, Dict[str, Any]] = {
    "d2 test": {"cognitive_demand": "high_demand", "confidence": 0.95},
    "stroop": {"cognitive_demand": "high_demand", "confidence": 0.95},
    "n-back": {"cognitive_demand": "high_demand", "confidence": 0.95},
    "digit span": {"cognitive_demand": "high_demand", "confidence": 0.95},
    "trail making": {"cognitive_demand": "high_demand", "confidence": 0.95},
    "raven": {"cognitive_demand": "high_demand", "confidence": 0.95},
    "remote associates": {"cognitive_demand": "high_demand", "confidence": 0.95},
    "alternative uses": {"cognitive_demand": "high_demand", "confidence": 0.95},
    "continuous performance": {"cognitive_demand": "high_demand", "confidence": 0.95},
    "panas": {"cognitive_demand": "low_demand", "confidence": 0.80},
    "nature walk": {"cognitive_demand": "restorative", "confidence": 0.90},
}

# Keyword patterns for task inference (D3: 0.5-0.7 confidence)
TASK_KEYWORD_PATTERNS: Dict[str, List[Tuple[str, float]]] = {
    "high_demand": [
        (r"proofread|proofreading", 0.70),
        (r"analyz|analysis|analytical", 0.60),
        (r"problem.?solv", 0.65),
        (r"concentrat|focus", 0.55),
        (r"study|studying|learn", 0.50),
        (r"complex.?task", 0.65),
        (r"cognitive.?task", 0.70),
        (r"attention.?task", 0.70),
        (r"memory.?task", 0.70),
        (r"vigilance", 0.70),
    ],
    "low_demand": [
        (r"routine", 0.60),
        (r"data entry", 0.70),
        (r"familiar.?task", 0.60),
        (r"simple.?task", 0.55),
        (r"repetitive", 0.60),
    ],
    "restorative": [
        (r"break|rest|pause", 0.65),
        (r"walk|walking", 0.60),
        (r"relax|relaxation", 0.70),
        (r"recover|restoration", 0.70),
        (r"nature.?view|view.?nature", 0.70),
    ],
}

# Effective demand matrix (D6: skill × cognitive_demand interaction per Ericsson)
EFFECTIVE_DEMAND_MATRIX: Dict[Tuple[str, str], str] = {
    # (cognitive_demand, skill_level) → effective_demand
    ("high_demand", "novice"): "very_high",
    ("high_demand", "intermediate"): "high",
    ("high_demand", "expert"): "moderate",
    ("low_demand", "novice"): "moderate",
    ("low_demand", "intermediate"): "low",
    ("low_demand", "expert"): "very_low",
    ("restorative", "novice"): "low",
    ("restorative", "intermediate"): "very_low",
    ("restorative", "expert"): "very_low",
}


@dataclass
class TaskContextResult:
    """Result of task context extraction (Sprint 2.6 Track A)."""
    cognitive_demand: str = "high_demand"  # Default per D1
    social_structure: str = "solitary"  # Default per D1
    inference_basis: str = "unknown"  # "stated", "inferred", "unknown"
    inference_confidence: float = 0.0
    review_recommended: bool = False  # True if confidence < 0.7
    matched_instrument: Optional[str] = None
    matched_pattern: Optional[str] = None


def extract_task_context(claim: Dict[str, Any]) -> TaskContextResult:
    """
    Extract task context from claim (Sprint 2.6 Track A: P-TC D1, D2, D3).

    Inference priority:
    1. Named instruments (D2: 0.95 confidence)
    2. Keyword patterns (D3: 0.5-0.7 confidence)
    3. Default to high_demand.solitary with inference_basis="unknown" (D1)

    Args:
        claim: Claim dictionary

    Returns:
        TaskContextResult with inferred task context and metadata
    """
    result = TaskContextResult()
    statement = claim.get("statement", "").lower()
    study = claim.get("study", {})
    task_desc = study.get("task", {}).get("description", "").lower()
    combined_text = f"{statement} {task_desc}"

    # Step 1: Try to match named instruments (D2: high confidence)
    for instrument, config in COMMON_INSTRUMENTS.items():
        if instrument in combined_text:
            result.cognitive_demand = config["cognitive_demand"]
            result.inference_confidence = config["confidence"]
            result.inference_basis = "stated"
            result.matched_instrument = instrument
            result.review_recommended = False  # High confidence, no review needed
            logger.debug(f"Task context: matched instrument '{instrument}' → {config['cognitive_demand']}")
            return result

    # Step 2: Try keyword patterns (D3: medium confidence)
    best_match: Optional[Tuple[str, str, float]] = None  # (demand, pattern, confidence)

    for demand_type, patterns in TASK_KEYWORD_PATTERNS.items():
        for pattern, confidence in patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                if best_match is None or confidence > best_match[2]:
                    best_match = (demand_type, pattern, confidence)

    if best_match:
        result.cognitive_demand = best_match[0]
        result.inference_confidence = best_match[2]
        result.inference_basis = "inferred"
        result.matched_pattern = best_match[1]
        # D3: Flag for review if confidence < 0.7
        result.review_recommended = best_match[2] < 0.7
        logger.debug(f"Task context: matched pattern '{best_match[1]}' → {best_match[0]} (confidence={best_match[2]:.2f})")
        return result

    # Step 3: Default (D1: high_demand.solitary when unknown)
    result.cognitive_demand = "high_demand"
    result.social_structure = "solitary"
    result.inference_basis = "unknown"
    result.inference_confidence = 0.0
    result.review_recommended = True  # Unknown context warrants review
    logger.debug("Task context: no match, defaulting to high_demand.solitary")
    return result


def compute_effective_demand(
    cognitive_demand: str,
    skill_level: str = "intermediate"
) -> str:
    """
    Compute effective demand from skill × cognitive_demand (D6: Ericsson panel input).

    Args:
        cognitive_demand: "high_demand", "low_demand", or "restorative"
        skill_level: "novice", "intermediate", or "expert"

    Returns:
        Effective demand: "very_high", "high", "moderate", "low", or "very_low"
    """
    return EFFECTIVE_DEMAND_MATRIX.get(
        (cognitive_demand, skill_level),
        "moderate"  # Default fallback
    )


def is_mechanism_only(claim: Dict[str, Any]) -> bool:
    """
    Check if claim is mechanism-only (D7: pure psych/neuro without architectural application).

    A claim is mechanism-only if:
    - It has mechanistic content (claim_type or statement suggests mechanism)
    - It has NO environment factors
    - It has NO architectural outcomes

    Args:
        claim: Claim dictionary

    Returns:
        True if mechanism-only paper, False otherwise
    """
    claim_type = claim.get("claim_type", "")
    statement = claim.get("statement", "").lower()
    constructs = claim.get("constructs", {})

    # Check for mechanistic indicators
    is_mechanistic = claim_type == "mechanistic" or any(
        kw in statement for kw in ["mediates", "mechanism", "pathway", "neural", "cortisol", "HPA"]
    )

    if not is_mechanistic:
        return False

    # Check for absence of architectural context
    env_factors = constructs.get("environment_factors", [])
    outcomes = constructs.get("outcomes", [])

    # Mechanism-only if no environment factors and no design-relevant outcomes
    has_env = bool(env_factors)
    has_design_outcomes = any(
        o.get("id", "").startswith(("behav.", "perf.", "design."))
        for o in outcomes if isinstance(o, dict)
    )

    return not has_env and not has_design_outcomes


def load_outcome_lookup(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the outcome taxonomy lookup."""
    if path is None:
        # Default path relative to this file
        path = Path(__file__).parent.parent.parent / "contracts" / "outcome_vocab" / "outcome_lookup.json"

    if path.exists():
        with open(path) as f:
            return json.load(f)

    logger.warning(f"Outcome lookup not found at {path}")
    return {}


# =============================================================================
# STUB MANAGEMENT
# =============================================================================

def get_stubs(web: WebOfBelief) -> List[Belief]:
    """Get all stub beliefs from the web."""
    return [b for b in web.beliefs.values() if b.is_stub()]


def get_stub_report(web: WebOfBelief) -> Dict[str, Any]:
    """Generate a report on stub beliefs."""
    stubs = get_stubs(web)
    
    report = {
        "total_stubs": len(stubs),
        "by_level": {},
        "by_domain": {},
        "stub_list": []
    }
    
    for stub in stubs:
        # By level
        level = stub.level.value
        report["by_level"][level] = report["by_level"].get(level, 0) + 1
        
        # By domain
        domain = stub.domain or "unknown"
        report["by_domain"][domain] = report["by_domain"].get(domain, 0) + 1
        
        # Add to list
        report["stub_list"].append({
            "belief_id": stub.belief_id,
            "content": stub.content[:100] + "..." if len(stub.content) > 100 else stub.content,
            "level": level,
            "domain": domain,
            "credence": stub.credence.value
        })
    
    return report


# =============================================================================
# TENSION DETECTION (ATK-1 Enhanced)
# =============================================================================

# Try to import argument attack analysis (ATK-1, ATK-3)
try:
    from src.services.argument_attack import enhance_tension_with_attack_analysis
    ARGUMENT_ATTACK_AVAILABLE = True
except ImportError:
    ARGUMENT_ATTACK_AVAILABLE = False


def get_tensions(web: WebOfBelief, include_attack_analysis: bool = True) -> List[Dict[str, Any]]:
    """
    Get beliefs in tension with the web.

    ATK-1: Enhanced with argument attack analysis when available.
    Detects whether tensions are true contradictions or contrast shifts.

    Args:
        web: The WebOfBelief to analyze
        include_attack_analysis: Whether to include ATK analysis (default True)

    Returns:
        List of tension dicts, optionally enhanced with attack analysis
    """
    tensions = []

    anomalies = [b for b in web.beliefs.values() if b.is_anomalous()]

    for anomaly in anomalies:
        # Find which beliefs it contradicts
        contradicting_ids = []
        contradicting_beliefs = []
        for constraint in web.constraints.values():
            if constraint.source_id == anomaly.belief_id or constraint.target_id == anomaly.belief_id:
                if constraint.constraint_type == ConstraintType.CONTRADICTS:
                    other_id = constraint.target_id if constraint.source_id == anomaly.belief_id else constraint.source_id
                    if other_id in web.beliefs:
                        contradicting_ids.append(web.beliefs[other_id].content[:50])
                        contradicting_beliefs.append(web.beliefs[other_id])

        # Build base tension record
        tension = {
            "belief_id": anomaly.belief_id,
            "content": anomaly.content[:100],
            "credence": anomaly.credence.value,
            "contradicts": contradicting_ids
        }

        # ATK-1: Enhance with attack analysis if available
        if include_attack_analysis and ARGUMENT_ATTACK_AVAILABLE and contradicting_beliefs:
            tension = enhance_tension_with_attack_analysis(
                tension=tension,
                anomaly_belief=anomaly,
                contradicting_beliefs=contradicting_beliefs,
                web=web
            )

        tensions.append(tension)

    return tensions


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

def export_stubs_jsonl(web: WebOfBelief, path: Path) -> int:
    """Export stubs to JSONL file."""
    stubs = get_stubs(web)
    
    with open(path, 'w') as f:
        for stub in stubs:
            record = {
                "belief_id": stub.belief_id,
                "content": stub.content,
                "level": stub.level.value,
                "domain": stub.domain,
                "credence": stub.credence.to_dict(),
                "paper_ids": stub.paper_ids,
                "tags": stub.tags
            }
            f.write(json.dumps(record) + "\n")
    
    return len(stubs)


def export_tensions_jsonl(web: WebOfBelief, path: Path) -> int:
    """Export tensions to JSONL file."""
    tensions = get_tensions(web)
    
    with open(path, 'w') as f:
        for tension in tensions:
            f.write(json.dumps(tension) + "\n")
    
    return len(tensions)


# =============================================================================
# COMPATIBILITY WITH THEORY REGISTRY
# =============================================================================

def belief_to_prediction_format(belief: Belief, entrenchment: Optional[float] = None) -> Dict[str, Any]:
    """
    Convert a Belief to a format compatible with TheoryRegistry predictions table.

    This enables future integration where beliefs can be stored in the
    persistent theory registry.

    Note: Not all belief fields map cleanly to predictions; this is a
    lossy conversion for compatibility purposes.

    Args:
        belief: The belief to convert
        entrenchment: V23.0.0 - Computed entrenchment value (emergent, not stored).
                      If None, uses _legacy_entrenchment for backward compatibility.
    """
    return {
        "prediction_id": belief.belief_id,
        "source_theory_id": belief.theory_id or "stub",
        "statement": belief.content,
        "prediction_type": "derived" if belief.theory_id else "newly_derived",
        "antecedent_env_conditions": None,  # Would need extraction
        "antecedent_population": None,
        "antecedent_temporal": None,
        "antecedent_state": None,
        "consequent_outcome": belief.domain,
        "consequent_direction": None,  # Would need extraction
        "consequent_magnitude": None,
        "consequent_mechanism": None,
        "relation_type": "probabilistic",
        "derivation_chain": None,
        "auxiliary_assumptions": None,
        "quantitative_point_estimate": None,
        "quantitative_ci_lower": belief.credence.confidence_interval()[0],
        "quantitative_ci_upper": belief.credence.confidence_interval()[1],
        "functional_form": None,
        "generality": "domain_specific",
        "applicable_populations": None,
        "applicable_contexts": None,
        "known_exceptions": None,
        "testing_status": "partially_tested" if belief.credence.n_observations > 0 else "untested",
        "overall_support": "supported" if belief.credence.value > 0.6 else "mixed",
        "test_summary": None,
        "prior_confidence": 0.5,
        "current_confidence": belief.credence.value,
        "theory_contribution": 0.3 if belief.theory_id else 0.0,
        "derivation_contribution": 0.0,
        "empirical_contribution": 0.7,
        "uncertainty_type": "both",
        "maps_to_edge_id": None,
        "maps_to_nodes": None,
        "contributes_prior": 1,
        # V23.0.0: Entrenchment is emergent, not stored. Use provided value or legacy.
        "prior_weight": entrenchment if entrenchment is not None else getattr(belief, '_legacy_entrenchment', 0.5),
        "extraction_source": ",".join(belief.paper_ids),
        "created_at": belief.created_at.isoformat() if belief.created_at else None,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }


# =============================================================================
# MAIN (Demo/Test)
# =============================================================================

if __name__ == "__main__":
    # Demo usage
    from src.services.web_of_belief import create_neuroarchitecture_web
    
    # Create a test web
    web = create_neuroarchitecture_web()
    
    # Sample claim
    test_claim = {
        "schema": "ae.claim.v1",
        "claim_id": "test:claim:001",
        "paper_id": "test:paper:001",
        "claim_type": "causal",
        "statement": "Exposure to natural environments reduces cortisol levels",
        "constructs": {
            "environment_factors": [{"id": "env.nature", "role": "iv"}],
            "outcomes": [{"id": "affect.stress", "role": "dv"}],
            "mediators": [],
            "moderators": []
        },
        "study": {
            "design": "RCT",
            "sample": {"n": 100, "population": "adults", "age_mean": 35, "country": "USA"},
            "task": [],
            "setting": []
        },
        "statistics": {
            "effect_size": {"type": "d", "value": 0.45},
            "p_value": 0.01,
            "ci95": [0.15, 0.75]
        },
        "evidence": [],
        "constraints": [],
        "ae_confidence": 0.75
    }
    
    # Map claim to belief
    result = claim_to_belief(test_claim)
    
    print("=== Claim to Belief Mapping ===")
    print(f"Success: {result.success}")
    print(f"Entity ID: {result.entity_id}")
    print(f"Theory inferences: {result.theory_inferences}")
    print(f"Is stub: {result.is_stub}")
    if result.entity:
        belief = result.entity
        print(f"Belief level: {belief.level.value}")
        print(f"Belief status: {belief.status.value}")
        print(f"Theory ID: {belief.theory_id}")
        print(f"Credence: {belief.credence.value:.2f} ± {belief.credence.uncertainty:.2f}")
