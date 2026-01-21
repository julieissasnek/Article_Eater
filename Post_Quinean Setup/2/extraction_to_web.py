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
from typing import Dict, Any, List, Optional, Tuple, Set
from enum import Enum
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
    UncertainQuantity,
    EpistemicLevel,
    BeliefStatus,
    ConstraintType
)

# Import semantic status from refined epistemic (for future use)
from src.services.refined_epistemic import SemanticStatus

logger = logging.getLogger(__name__)


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
    "health": ["SRT", "Biophilia"],
    "health.wellbeing": ["SRT", "Biophilia"],
    "behav": ["ART", "SRT"],
    "behav.productivity": ["ART"],
    "social": ["Biophilia"],
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
            'warnings': self.warnings
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

    # Strategy 3: Environment factors (weaker signal)
    for env_factor in environment_factors:
        env_id = env_factor.get("id", "").lower()
        if any(w in env_id for w in ["nature", "green", "plant", "outdoor", "park"]):
            # Nature-related factors suggest ART, SRT, Biophilia
            for theory in ["ART", "SRT", "Biophilia"]:
                old_val = relevance.get(theory, 0)
                relevance[theory] = _diminishing_returns_combine(old_val, 0.4)
                trace.append(f"EnvFactor:{env_id}→{theory} score=0.40 (combined: {old_val:.2f}→{relevance[theory]:.2f})")

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
        
        # Infer theory relevance
        theory_inferences = infer_theory_relevance(claim, outcome_lookup)
        result.theory_inferences = theory_inferences

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

        # Create the Belief
        belief = Belief(
            belief_id=claim_id,
            content=statement,
            level=level,
            status=status,
            credence=credence,
            entrenchment=base_entrenchment,
            paper_ids=[paper_id],
            theory_id=theory_id,
            domain=_extract_domain(constructs),
            tags=_extract_tags(claim)
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
    
    # Process claims
    for claim in claims:
        report.n_claims_processed += 1
        result = claim_to_belief(claim, web, outcome_lookup)
        
        if result.success and result.entity:
            belief = result.entity
            
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
# TENSION DETECTION
# =============================================================================

def get_tensions(web: WebOfBelief) -> List[Dict[str, Any]]:
    """Get beliefs in tension with the web."""
    tensions = []
    
    anomalies = [b for b in web.beliefs.values() if b.is_anomalous()]
    
    for anomaly in anomalies:
        # Find which beliefs it contradicts
        contradicting = []
        for constraint in web.constraints.values():
            if constraint.source_id == anomaly.belief_id or constraint.target_id == anomaly.belief_id:
                if constraint.constraint_type == ConstraintType.CONTRADICTS:
                    other_id = constraint.target_id if constraint.source_id == anomaly.belief_id else constraint.source_id
                    if other_id in web.beliefs:
                        contradicting.append(web.beliefs[other_id].content[:50])
        
        tensions.append({
            "belief_id": anomaly.belief_id,
            "content": anomaly.content[:100],
            "credence": anomaly.credence.value,
            "contradicts": contradicting
        })
    
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

def belief_to_prediction_format(belief: Belief) -> Dict[str, Any]:
    """
    Convert a Belief to a format compatible with TheoryRegistry predictions table.
    
    This enables future integration where beliefs can be stored in the
    persistent theory registry.
    
    Note: Not all belief fields map cleanly to predictions; this is a
    lossy conversion for compatibility purposes.
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
        "prior_weight": belief.entrenchment,
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
