"""
Argument Attack Analysis System (ATK-1, ATK-3)
==============================================

Reintegrated: 2026-02-11
Source: quarantine/2026-02-10/epistemic_causal_bridge_features/argument_attack.py

This module analyzes scientific disagreements as contrast class shifts
rather than simple refutations.

KEY INSIGHT: Many apparent contradictions are contrast shifts, not true refutations.
"Paper A says X, Paper B says not-X" often means they used different contrasts.
Both may be correct within their respective contrast classes.

Components:
- AttackType: Types of argument attack in scientific literature
- ContrastShiftType: How an attack shifts the contrast class
- ArgumentAttack: An attack with contrast class analysis
- ShiftClassifier: Rule-based heuristics for classifying shifts (ATK-3)
- analyze_tension_as_attack: Integrates with tension detection (ATK-1)

References:
- Ioannidis, J.P.A. (2005). Contradicted and initially stronger effects. JAMA.
- Walton, D. (2008). Informal Logic: A Pragmatic Approach.
- Van Fraassen, B.C. (1980). The Scientific Image.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Import real contrast classes from epistemic_causal_bridge
from src.services.epistemic_causal_bridge import (
    ContrastClass,
    ContrastTransferType,
    ConditionSpec,
    PopulationContext,
)


class AttackType(Enum):
    """Types of argument attack in scientific literature."""
    CONFOUNDER = "confounder"           # "Effect is due to unmeasured confounder"
    BOUNDARY_CONDITION = "boundary_condition"  # "Only true under condition X"
    OVERGENERALIZATION = "overgeneralization"  # "Claim is too broad"
    MECHANISM = "mechanism"              # "Proposed mechanism is wrong"
    MEASUREMENT = "measurement"          # "Measurement was flawed"
    REPLICATION = "replication"          # "Failed to replicate"
    DOSE_RESPONSE = "dose_response"      # "Effect depends on dose differently"
    TEMPORAL = "temporal"                # "Timing/duration matters"


class ContrastShiftType(Enum):
    """How an attack shifts the contrast class."""
    PRESERVING = "preserving"       # Same contrast, disputes finding directly
    POPULATION_SHIFT = "population"  # Different population studied
    BASELINE_SHIFT = "baseline"      # Different baseline level assumed
    MEANING_SHIFT = "meaning"        # Different cultural/contextual meaning
    ALTERNATIVE_SHIFT = "alternative"  # Different comparison condition
    COMPLEX_SHIFT = "complex"        # Multiple shifts simultaneously


@dataclass
class ArgumentAttack:
    """
    An argument attack with contrast class analysis.

    Key insight: Many attacks are contrast shifts, not refutations.
    "Paper B contradicts Paper A" often means "Paper B tested a
    different population/setting/contrast and found different results."
    Both may be correct within their contrast classes.
    """
    attack_id: str
    source_paper_id: str          # Paper making the attack
    target_belief_id: str         # Belief being attacked
    attack_type: AttackType

    # The attack claim
    attack_claim: str             # e.g., "Effect disappears in rural populations"
    attack_credence: float        # How confident is the attack?

    # Contrast class analysis
    original_contrast: Optional[ContrastClass] = None
    shifted_contrast: Optional[ContrastClass] = None
    shift_type: ContrastShiftType = ContrastShiftType.PRESERVING

    # Outcome under each contrast
    outcome_under_original: Optional[str] = None  # e.g., "Effect present"
    outcome_under_shifted: Optional[str] = None   # e.g., "No effect"

    # Resolution
    resolution: Optional[str] = None              # e.g., "Boundary condition identified"
    resolution_credence: Optional[float] = None

    def is_contrast_preserving(self) -> bool:
        """True if attack disputes finding within same contrast class."""
        return self.shift_type == ContrastShiftType.PRESERVING

    def is_contrast_shifting(self) -> bool:
        """True if attack shifts to different contrast class."""
        return self.shift_type != ContrastShiftType.PRESERVING

    def is_true_refutation(self) -> bool:
        """True if this is a genuine contradiction (same contrast, opposite finding)."""
        return self.shift_type == ContrastShiftType.PRESERVING

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for tensions.jsonl output."""
        return {
            "attack_id": self.attack_id,
            "source_paper_id": self.source_paper_id,
            "target_belief_id": self.target_belief_id,
            "attack_type": self.attack_type.value,
            "attack_claim": self.attack_claim,
            "attack_credence": self.attack_credence,
            "shift_type": self.shift_type.value,
            "is_true_refutation": self.is_true_refutation(),
            "outcome_under_original": self.outcome_under_original,
            "outcome_under_shifted": self.outcome_under_shifted,
            "resolution": self.resolution,
            "resolution_credence": self.resolution_credence,
            "original_contrast_id": self.original_contrast.contrast_id if self.original_contrast else None,
            "shifted_contrast_id": self.shifted_contrast.contrast_id if self.shifted_contrast else None,
        }


@dataclass
class AttackContrastAnalysis:
    """
    Analysis of how an attack relates to contrast class.

    Used to determine whether an apparent contradiction is:
    1. A true refutation (same contrast, opposite finding)
    2. A boundary condition (different contrast, consistent findings)
    """
    attack_id: str
    analysis_type: str          # "preserving" or "shifting"

    original_contrast: Optional[ContrastClass] = None
    attack_contrast: Optional[ContrastClass] = None

    shift_type: Optional[ContrastShiftType] = None
    shift_dimensions: List[str] = field(default_factory=list)  # Which dimensions shifted

    implication: str = ""       # What this means for the original claim
    resolution_approach: str = ""  # How to resolve the tension

    # For shifting attacks, both may be valid
    original_validity: str = ""  # e.g., "Valid for urban populations"
    attack_validity: str = ""    # e.g., "Valid for rural populations"


# =============================================================================
# SHIFT CLASSIFIER (ATK-3)
# =============================================================================

class ShiftClassifier:
    """
    Rule-based heuristics for classifying contrast shifts.

    ATK-3: This is a rule-based approach. A future ML classifier
    could improve accuracy but requires labeled training data.
    """

    # Keywords that suggest different shift types
    POPULATION_KEYWORDS = {
        "population", "sample", "participants", "subjects", "cohort",
        "patients", "workers", "students", "children", "adults", "elderly",
        "women", "men", "rural", "urban", "clinical", "healthy"
    }

    BASELINE_KEYWORDS = {
        "baseline", "initial", "pre-existing", "chronic", "acute",
        "low", "high", "deficit", "saturated", "ceiling", "floor"
    }

    MEANING_KEYWORDS = {
        "culture", "cultural", "meaning", "interpretation", "context",
        "western", "eastern", "individualist", "collectivist",
        "definition", "conceptualization", "operationalization"
    }

    ALTERNATIVE_KEYWORDS = {
        "control", "comparison", "versus", "compared to", "relative to",
        "placebo", "sham", "active control", "treatment as usual"
    }

    DOSE_KEYWORDS = {
        "dose", "dosage", "duration", "frequency", "intensity",
        "exposure", "minutes", "hours", "days", "weeks", "session"
    }

    TEMPORAL_KEYWORDS = {
        "timing", "temporal", "acute", "chronic", "immediate",
        "delayed", "short-term", "long-term", "follow-up"
    }

    @classmethod
    def classify_from_text(
        cls,
        attack_claim: str,
        original_content: str,
        attack_content: str
    ) -> Tuple[ContrastShiftType, AttackType, List[str]]:
        """
        Classify shift type from textual content.

        Returns:
            Tuple of (shift_type, attack_type, shift_dimensions)
        """
        combined_text = f"{attack_claim} {original_content} {attack_content}".lower()

        shift_dimensions = []
        shift_scores = {
            ContrastShiftType.POPULATION_SHIFT: 0,
            ContrastShiftType.BASELINE_SHIFT: 0,
            ContrastShiftType.MEANING_SHIFT: 0,
            ContrastShiftType.ALTERNATIVE_SHIFT: 0,
        }

        # Score each shift type
        for kw in cls.POPULATION_KEYWORDS:
            if kw in combined_text:
                shift_scores[ContrastShiftType.POPULATION_SHIFT] += 1
                if kw not in shift_dimensions:
                    shift_dimensions.append(f"population:{kw}")

        for kw in cls.BASELINE_KEYWORDS:
            if kw in combined_text:
                shift_scores[ContrastShiftType.BASELINE_SHIFT] += 1
                if kw not in shift_dimensions:
                    shift_dimensions.append(f"baseline:{kw}")

        for kw in cls.MEANING_KEYWORDS:
            if kw in combined_text:
                shift_scores[ContrastShiftType.MEANING_SHIFT] += 1
                if kw not in shift_dimensions:
                    shift_dimensions.append(f"meaning:{kw}")

        for kw in cls.ALTERNATIVE_KEYWORDS:
            if kw in combined_text:
                shift_scores[ContrastShiftType.ALTERNATIVE_SHIFT] += 1
                if kw not in shift_dimensions:
                    shift_dimensions.append(f"alternative:{kw}")

        # Determine attack type
        attack_type = cls._classify_attack_type(combined_text)

        # Determine shift type
        max_score = max(shift_scores.values())
        if max_score == 0:
            # No clear shift detected — likely preserving (true contradiction)
            return ContrastShiftType.PRESERVING, attack_type, []

        # Check for complex shift (multiple high scores)
        high_scores = [k for k, v in shift_scores.items() if v >= max_score * 0.7 and v > 0]
        if len(high_scores) > 1:
            return ContrastShiftType.COMPLEX_SHIFT, attack_type, shift_dimensions

        # Return highest scoring shift type
        shift_type = max(shift_scores.keys(), key=lambda k: shift_scores[k])
        return shift_type, attack_type, shift_dimensions

    @classmethod
    def _classify_attack_type(cls, text: str) -> AttackType:
        """Classify the type of attack from text."""
        text = text.lower()

        # Check for specific attack patterns
        if any(kw in text for kw in ["confounder", "confounding", "unmeasured variable"]):
            return AttackType.CONFOUNDER

        if any(kw in text for kw in ["boundary", "condition", "only when", "only if"]):
            return AttackType.BOUNDARY_CONDITION

        if any(kw in text for kw in ["overgeneralize", "too broad", "limited to"]):
            return AttackType.OVERGENERALIZATION

        if any(kw in text for kw in ["mechanism", "pathway", "mediate", "process"]):
            return AttackType.MECHANISM

        if any(kw in text for kw in ["measurement", "measure", "operationalize", "instrument"]):
            return AttackType.MEASUREMENT

        if any(kw in text for kw in ["replicate", "replication", "reproduce", "failed to"]):
            return AttackType.REPLICATION

        if any(kw in text for kw in cls.DOSE_KEYWORDS):
            return AttackType.DOSE_RESPONSE

        if any(kw in text for kw in cls.TEMPORAL_KEYWORDS):
            return AttackType.TEMPORAL

        # Default to boundary condition (most common)
        return AttackType.BOUNDARY_CONDITION

    @classmethod
    def classify_from_contrasts(
        cls,
        original: Optional[ContrastClass],
        shifted: Optional[ContrastClass]
    ) -> Tuple[ContrastShiftType, List[str]]:
        """
        Classify shift type by comparing two contrast classes.

        This is more precise than text-based classification when
        explicit contrast classes are available.
        """
        if original is None or shifted is None:
            return ContrastShiftType.PRESERVING, []

        shift_dimensions = []

        # Compare population contexts
        if original.population_context and shifted.population_context:
            orig_pop = original.population_context
            shift_pop = shifted.population_context

            if orig_pop.population_id != shift_pop.population_id:
                shift_dimensions.append(f"population:{orig_pop.population_id}->{shift_pop.population_id}")

            # Compare baselines
            for var, orig_baseline in orig_pop.baselines.items():
                if var in shift_pop.baselines:
                    shift_baseline = shift_pop.baselines[var]
                    if orig_baseline.characterization != shift_baseline.characterization:
                        shift_dimensions.append(
                            f"baseline:{var}:{orig_baseline.characterization}->{shift_baseline.characterization}"
                        )

            # Compare cultural meanings
            if orig_pop.cultural_meanings != shift_pop.cultural_meanings:
                shift_dimensions.append("meaning:cultural_context_differs")

        # Compare focal conditions
        if original.focal.variable != shifted.focal.variable:
            shift_dimensions.append(f"focal:{original.focal.variable}->{shifted.focal.variable}")
        elif original.focal.value != shifted.focal.value:
            shift_dimensions.append(f"focal_value:{original.focal.value}->{shifted.focal.value}")

        # Compare contrast conditions
        orig_contrasts = {c.variable: c.value for c in original.contrasts}
        shift_contrasts = {c.variable: c.value for c in shifted.contrasts}
        if orig_contrasts != shift_contrasts:
            shift_dimensions.append("alternative:contrast_conditions_differ")

        # Determine shift type from dimensions
        if not shift_dimensions:
            return ContrastShiftType.PRESERVING, []

        has_population = any("population:" in d for d in shift_dimensions)
        has_baseline = any("baseline:" in d for d in shift_dimensions)
        has_meaning = any("meaning:" in d for d in shift_dimensions)
        has_alternative = any("alternative:" in d or "focal" in d for d in shift_dimensions)

        active_shifts = sum([has_population, has_baseline, has_meaning, has_alternative])

        if active_shifts > 1:
            return ContrastShiftType.COMPLEX_SHIFT, shift_dimensions

        if has_meaning:
            return ContrastShiftType.MEANING_SHIFT, shift_dimensions
        if has_population:
            return ContrastShiftType.POPULATION_SHIFT, shift_dimensions
        if has_baseline:
            return ContrastShiftType.BASELINE_SHIFT, shift_dimensions
        if has_alternative:
            return ContrastShiftType.ALTERNATIVE_SHIFT, shift_dimensions

        return ContrastShiftType.PRESERVING, shift_dimensions


# =============================================================================
# TENSION INTEGRATION (ATK-1)
# =============================================================================

def analyze_tension_as_attack(
    anomaly_belief: Any,  # Belief from web_of_belief
    contradicting_belief: Any,  # Belief from web_of_belief
    source_paper_id: str = "unknown"
) -> Tuple[ArgumentAttack, List[StructuredAttackEvidence]]:
    """
    Analyze a detected tension as a potential argument attack.

    ATK-1: This function bridges the existing tension detection
    with the argument attack analysis system.

    Strategy (per user insight):
    1. FIRST try structured metadata detection (no NLP needed)
    2. THEN fall back to text-based classification if no structured evidence
    3. Use contrast class comparison if both have explicit contrast classes

    Args:
        anomaly_belief: The anomalous belief (attacking)
        contradicting_belief: The belief being contradicted (target)
        source_paper_id: Paper ID of the anomaly

    Returns:
        Tuple of (ArgumentAttack with shift classification, List of structured evidence)
    """
    # Get contrast classes if available
    original_contrast = getattr(contradicting_belief, 'contrast_class', None)
    shifted_contrast = getattr(anomaly_belief, 'contrast_class', None)

    # STEP 1: Try structured metadata detection (no NLP)
    structured_evidence = StructuredAttackDetector.detect_all(
        anomaly_belief, contradicting_belief
    )

    if structured_evidence:
        # Use structured evidence for classification
        shift_type, attack_type, shift_dimensions = classify_from_structured_evidence(
            structured_evidence
        )
    elif original_contrast and shifted_contrast:
        # STEP 2: Use precise contrast-based classification
        shift_type, shift_dimensions = ShiftClassifier.classify_from_contrasts(
            original_contrast, shifted_contrast
        )
        _, attack_type, _ = ShiftClassifier.classify_from_text(
            anomaly_belief.content,
            contradicting_belief.content,
            anomaly_belief.content
        )
    else:
        # STEP 3: Fall back to text-based classification (least precise)
        shift_type, attack_type, shift_dimensions = ShiftClassifier.classify_from_text(
            anomaly_belief.content,
            contradicting_belief.content,
            anomaly_belief.content
        )

    # Generate resolution suggestion based on shift type
    resolution = _generate_resolution(shift_type, shift_dimensions)

    attack = ArgumentAttack(
        attack_id=f"atk_{anomaly_belief.belief_id}_{contradicting_belief.belief_id}",
        source_paper_id=source_paper_id,
        target_belief_id=contradicting_belief.belief_id,
        attack_type=attack_type,
        attack_claim=anomaly_belief.content[:200],
        attack_credence=anomaly_belief.credence.value if hasattr(anomaly_belief.credence, 'value') else anomaly_belief.credence,
        original_contrast=original_contrast,
        shifted_contrast=shifted_contrast,
        shift_type=shift_type,
        outcome_under_original=f"Finding: {contradicting_belief.content[:100]}",
        outcome_under_shifted=f"Finding: {anomaly_belief.content[:100]}",
        resolution=resolution,
    )

    return attack, structured_evidence


# =============================================================================
# STRUCTURED METADATA DETECTION (No NLP Required)
# =============================================================================

@dataclass
class StructuredAttackEvidence:
    """
    Evidence for an attack derived from structured metadata.

    No NLP required — uses explicit fields from beliefs and studies.
    """
    evidence_type: str  # e.g., "population_mismatch", "confound_present"
    field_a: str        # Field name in source belief/study
    value_a: Any        # Value in source
    field_b: str        # Field name in target belief/study
    value_b: Any        # Value in target
    confidence: float   # How confident are we this is meaningful?
    implication: str    # What this evidence suggests


class StructuredAttackDetector:
    """
    Detect argument attacks from structured metadata.

    Key insight from user: Many attacks fall into categories that
    should be relatively easy to identify without NLP:
    - Confounds in stimulus
    - Bias in sample population
    - Methodological differences
    - Measurement operationalization differences
    - Dosage/exposure level differences
    """

    @classmethod
    def detect_population_mismatch(
        cls,
        belief_a: Any,  # Belief with contrast_class
        belief_b: Any,  # Belief with contrast_class
    ) -> Optional[StructuredAttackEvidence]:
        """
        Detect population mismatch from PopulationContext.

        Checks: region, population_id, baseline characterizations
        """
        cc_a = getattr(belief_a, 'contrast_class', None)
        cc_b = getattr(belief_b, 'contrast_class', None)

        if not cc_a or not cc_b:
            return None

        pop_a = getattr(cc_a, 'population_context', None)
        pop_b = getattr(cc_b, 'population_context', None)

        if not pop_a or not pop_b:
            return None

        mismatches = []

        # Check population_id
        if pop_a.population_id != pop_b.population_id:
            mismatches.append(f"population_id: {pop_a.population_id} vs {pop_b.population_id}")

        # Check region
        if hasattr(pop_a, 'region') and hasattr(pop_b, 'region'):
            if pop_a.region != pop_b.region:
                mismatches.append(f"region: {pop_a.region} vs {pop_b.region}")

        # Check baseline characterizations
        for var in pop_a.baselines:
            if var in pop_b.baselines:
                char_a = pop_a.baselines[var].characterization
                char_b = pop_b.baselines[var].characterization
                if char_a != char_b:
                    mismatches.append(f"baseline_{var}: {char_a} vs {char_b}")

        if not mismatches:
            return None

        return StructuredAttackEvidence(
            evidence_type="population_mismatch",
            field_a="population_context",
            value_a=pop_a.population_id,
            field_b="population_context",
            value_b=pop_b.population_id,
            confidence=0.9,  # High confidence — explicit metadata
            implication=f"Different populations: {'; '.join(mismatches)}"
        )

    @classmethod
    def detect_baseline_shift(
        cls,
        belief_a: Any,
        belief_b: Any,
    ) -> Optional[StructuredAttackEvidence]:
        """
        Detect baseline level differences.

        Example: Study A on population with low baseline light exposure
                 Study B on population with high baseline light exposure
        """
        cc_a = getattr(belief_a, 'contrast_class', None)
        cc_b = getattr(belief_b, 'contrast_class', None)

        if not cc_a or not cc_b:
            return None

        pop_a = getattr(cc_a, 'population_context', None)
        pop_b = getattr(cc_b, 'population_context', None)

        if not pop_a or not pop_b:
            return None

        baseline_diffs = []

        for var in pop_a.baselines:
            if var in pop_b.baselines:
                base_a = pop_a.baselines[var]
                base_b = pop_b.baselines[var]

                # Check characterization (very_low, low, moderate, high, saturated)
                char_order = ["very_low", "low", "moderate", "high", "saturated"]
                try:
                    idx_a = char_order.index(base_a.characterization)
                    idx_b = char_order.index(base_b.characterization)
                    if abs(idx_a - idx_b) >= 2:  # At least 2 levels apart
                        baseline_diffs.append({
                            "variable": var,
                            "level_a": base_a.characterization,
                            "level_b": base_b.characterization,
                            "typical_a": base_a.typical_value,
                            "typical_b": base_b.typical_value,
                        })
                except ValueError:
                    pass

        if not baseline_diffs:
            return None

        return StructuredAttackEvidence(
            evidence_type="baseline_shift",
            field_a="baselines",
            value_a={d["variable"]: d["level_a"] for d in baseline_diffs},
            field_b="baselines",
            value_b={d["variable"]: d["level_b"] for d in baseline_diffs},
            confidence=0.85,
            implication=f"Baseline levels differ significantly: {baseline_diffs}"
        )

    @classmethod
    def detect_contrast_condition_mismatch(
        cls,
        belief_a: Any,
        belief_b: Any,
    ) -> Optional[StructuredAttackEvidence]:
        """
        Detect different comparison conditions.

        Example: Study A compares forest vs office
                 Study B compares forest vs urban park
        """
        cc_a = getattr(belief_a, 'contrast_class', None)
        cc_b = getattr(belief_b, 'contrast_class', None)

        if not cc_a or not cc_b:
            return None

        # Compare focal conditions
        focal_mismatch = None
        if cc_a.focal.variable == cc_b.focal.variable:
            if cc_a.focal.value != cc_b.focal.value:
                focal_mismatch = f"focal_{cc_a.focal.variable}: {cc_a.focal.value} vs {cc_b.focal.value}"

        # Compare contrast conditions
        contrasts_a = {c.variable: c.value for c in cc_a.contrasts}
        contrasts_b = {c.variable: c.value for c in cc_b.contrasts}

        contrast_diffs = []
        all_vars = set(contrasts_a.keys()) | set(contrasts_b.keys())
        for var in all_vars:
            val_a = contrasts_a.get(var, "NOT_PRESENT")
            val_b = contrasts_b.get(var, "NOT_PRESENT")
            if val_a != val_b:
                contrast_diffs.append(f"contrast_{var}: {val_a} vs {val_b}")

        if not focal_mismatch and not contrast_diffs:
            return None

        all_diffs = ([focal_mismatch] if focal_mismatch else []) + contrast_diffs

        return StructuredAttackEvidence(
            evidence_type="contrast_condition_mismatch",
            field_a="contrast_conditions",
            value_a={"focal": cc_a.focal.value, "contrasts": contrasts_a},
            field_b="contrast_conditions",
            value_b={"focal": cc_b.focal.value, "contrasts": contrasts_b},
            confidence=0.95,  # Very high — explicit experimental conditions
            implication=f"Different comparison conditions: {'; '.join(all_diffs)}"
        )

    @classmethod
    def detect_dosage_mismatch(
        cls,
        belief_a: Any,
        belief_b: Any,
    ) -> Optional[StructuredAttackEvidence]:
        """
        Detect dosage/exposure level differences.

        Uses EnablingConditions.dosage_satisfies from beliefs.
        """
        # Check for enabling conditions
        ec_a = getattr(belief_a, 'enabling_conditions', None)
        ec_b = getattr(belief_b, 'enabling_conditions', None)

        if not ec_a or not ec_b:
            return None

        # Compare dosage_satisfies patterns
        dosage_a = set(getattr(ec_a, 'dosage_satisfies', []))
        dosage_b = set(getattr(ec_b, 'dosage_satisfies', []))

        if not dosage_a and not dosage_b:
            return None

        if dosage_a == dosage_b:
            return None

        only_a = dosage_a - dosage_b
        only_b = dosage_b - dosage_a

        return StructuredAttackEvidence(
            evidence_type="dosage_mismatch",
            field_a="dosage_satisfies",
            value_a=list(dosage_a),
            field_b="dosage_satisfies",
            value_b=list(dosage_b),
            confidence=0.8,
            implication=f"Dosage patterns differ. Only in A: {only_a}. Only in B: {only_b}"
        )

    @classmethod
    def detect_measurement_mismatch(
        cls,
        belief_a: Any,
        belief_b: Any,
    ) -> Optional[StructuredAttackEvidence]:
        """
        Detect different outcome operationalizations.

        Checks tags for outcome: prefixes and compares them.
        """
        tags_a = set(getattr(belief_a, 'tags', []))
        tags_b = set(getattr(belief_b, 'tags', []))

        outcome_tags_a = {t for t in tags_a if t.startswith("outcome:")}
        outcome_tags_b = {t for t in tags_b if t.startswith("outcome:")}

        if not outcome_tags_a or not outcome_tags_b:
            return None

        # Check if they're measuring different outcomes
        if outcome_tags_a == outcome_tags_b:
            return None

        # Check overlap
        overlap = outcome_tags_a & outcome_tags_b
        only_a = outcome_tags_a - outcome_tags_b
        only_b = outcome_tags_b - outcome_tags_a

        if overlap and (only_a or only_b):
            # Partial overlap — might be different operationalizations of same construct
            return StructuredAttackEvidence(
                evidence_type="measurement_mismatch",
                field_a="outcome_tags",
                value_a=list(outcome_tags_a),
                field_b="outcome_tags",
                value_b=list(outcome_tags_b),
                confidence=0.7,
                implication=f"Partial outcome overlap. Shared: {overlap}. Different: A={only_a}, B={only_b}"
            )
        elif not overlap:
            # No overlap — different outcomes entirely
            return StructuredAttackEvidence(
                evidence_type="outcome_mismatch",
                field_a="outcome_tags",
                value_a=list(outcome_tags_a),
                field_b="outcome_tags",
                value_b=list(outcome_tags_b),
                confidence=0.9,
                implication=f"Different outcomes measured: {outcome_tags_a} vs {outcome_tags_b}"
            )

        return None

    @classmethod
    def detect_theory_conflict(
        cls,
        belief_a: Any,
        belief_b: Any,
    ) -> Optional[StructuredAttackEvidence]:
        """
        Detect when beliefs come from conflicting theoretical frameworks.
        """
        theory_a = set(getattr(belief_a, 'theory_ids', {}).keys())
        theory_b = set(getattr(belief_b, 'theory_ids', {}).keys())

        if not theory_a or not theory_b:
            return None

        # Check for overlap
        if theory_a & theory_b:
            return None  # Same theory — not a theory conflict

        return StructuredAttackEvidence(
            evidence_type="theory_conflict",
            field_a="theory_ids",
            value_a=list(theory_a),
            field_b="theory_ids",
            value_b=list(theory_b),
            confidence=0.75,
            implication=f"Different theoretical frameworks: {theory_a} vs {theory_b}"
        )

    @classmethod
    def detect_all(
        cls,
        belief_a: Any,
        belief_b: Any,
    ) -> List[StructuredAttackEvidence]:
        """
        Run all structured detectors and return evidence list.
        """
        evidence = []

        detectors = [
            cls.detect_population_mismatch,
            cls.detect_baseline_shift,
            cls.detect_contrast_condition_mismatch,
            cls.detect_dosage_mismatch,
            cls.detect_measurement_mismatch,
            cls.detect_theory_conflict,
        ]

        for detector in detectors:
            result = detector(belief_a, belief_b)
            if result:
                evidence.append(result)

        return evidence


def classify_from_structured_evidence(
    evidence_list: List[StructuredAttackEvidence]
) -> Tuple[ContrastShiftType, AttackType, List[str]]:
    """
    Determine shift type and attack type from structured evidence.

    No NLP required — purely based on metadata comparison.
    """
    if not evidence_list:
        return ContrastShiftType.PRESERVING, AttackType.REPLICATION, []

    shift_dimensions = []
    attack_type = AttackType.BOUNDARY_CONDITION  # Default

    evidence_types = {e.evidence_type for e in evidence_list}

    # Map evidence types to shift types
    shift_type = ContrastShiftType.PRESERVING

    if "population_mismatch" in evidence_types:
        shift_type = ContrastShiftType.POPULATION_SHIFT
        attack_type = AttackType.BOUNDARY_CONDITION

    if "baseline_shift" in evidence_types:
        if shift_type != ContrastShiftType.PRESERVING:
            shift_type = ContrastShiftType.COMPLEX_SHIFT
        else:
            shift_type = ContrastShiftType.BASELINE_SHIFT
        attack_type = AttackType.BOUNDARY_CONDITION

    if "contrast_condition_mismatch" in evidence_types:
        if shift_type != ContrastShiftType.PRESERVING:
            shift_type = ContrastShiftType.COMPLEX_SHIFT
        else:
            shift_type = ContrastShiftType.ALTERNATIVE_SHIFT
        attack_type = AttackType.BOUNDARY_CONDITION

    if "dosage_mismatch" in evidence_types:
        attack_type = AttackType.DOSE_RESPONSE
        if shift_type == ContrastShiftType.PRESERVING:
            shift_type = ContrastShiftType.BASELINE_SHIFT

    if "measurement_mismatch" in evidence_types or "outcome_mismatch" in evidence_types:
        attack_type = AttackType.MEASUREMENT
        # Could still be same contrast, different measurement

    if "theory_conflict" in evidence_types:
        attack_type = AttackType.MECHANISM

    # Collect all implications as shift dimensions
    for e in evidence_list:
        shift_dimensions.append(f"{e.evidence_type}:{e.implication[:50]}")

    return shift_type, attack_type, shift_dimensions


def _generate_resolution(shift_type: ContrastShiftType, shift_dimensions: List[str]) -> str:
    """Generate a resolution suggestion based on shift type."""
    if shift_type == ContrastShiftType.PRESERVING:
        return "TRUE CONTRADICTION: Findings directly conflict within same contrast class. Requires empirical resolution."

    if shift_type == ContrastShiftType.POPULATION_SHIFT:
        return f"BOUNDARY CONDITION: Findings differ across populations. Both may be valid. Dimensions: {', '.join(shift_dimensions)}"

    if shift_type == ContrastShiftType.BASELINE_SHIFT:
        return f"BASELINE EFFECT: Different starting points may explain different outcomes. Check for ceiling/floor effects. Dimensions: {', '.join(shift_dimensions)}"

    if shift_type == ContrastShiftType.MEANING_SHIFT:
        return f"CONCEPTUAL DIVERGENCE: Construct may mean different things. Cannot directly compare. Dimensions: {', '.join(shift_dimensions)}"

    if shift_type == ContrastShiftType.ALTERNATIVE_SHIFT:
        return f"DIFFERENT COMPARISON: Different control/comparison conditions used. Not directly comparable. Dimensions: {', '.join(shift_dimensions)}"

    if shift_type == ContrastShiftType.COMPLEX_SHIFT:
        return f"COMPLEX SHIFT: Multiple dimensions differ. Careful decomposition needed. Dimensions: {', '.join(shift_dimensions)}"

    return "Unknown shift type"


def enhance_tension_with_attack_analysis(
    tension: Dict[str, Any],
    anomaly_belief: Any,
    contradicting_beliefs: List[Any],
    web: Any  # WebOfBelief
) -> Dict[str, Any]:
    """
    Enhance a tension dict with argument attack analysis.

    ATK-1: This is the main integration point. Called from
    extraction_to_web.get_tensions() to enrich tension output.

    Args:
        tension: Original tension dict from get_tensions()
        anomaly_belief: The anomalous belief
        contradicting_beliefs: Beliefs that contradict the anomaly
        web: The WebOfBelief (for accessing belief objects)

    Returns:
        Enhanced tension dict with attack analysis
    """
    attacks = []
    all_structured_evidence = []

    for contradicting in contradicting_beliefs:
        attack, structured_evidence = analyze_tension_as_attack(
            anomaly_belief=anomaly_belief,
            contradicting_belief=contradicting,
            source_paper_id=getattr(anomaly_belief, 'source_paper_id', 'unknown')
        )
        attack_dict = attack.to_dict()

        # Add structured evidence to attack
        attack_dict["structured_evidence"] = [
            {
                "type": e.evidence_type,
                "field_a": e.field_a,
                "value_a": e.value_a if isinstance(e.value_a, (str, int, float, bool, list)) else str(e.value_a),
                "field_b": e.field_b,
                "value_b": e.value_b if isinstance(e.value_b, (str, int, float, bool, list)) else str(e.value_b),
                "confidence": e.confidence,
                "implication": e.implication,
            }
            for e in structured_evidence
        ]
        attack_dict["detection_method"] = "structured" if structured_evidence else "text_heuristic"

        attacks.append(attack_dict)
        all_structured_evidence.extend(structured_evidence)

    # Determine overall tension type
    if not attacks:
        tension_type = "isolated_anomaly"
    elif all(a["is_true_refutation"] for a in attacks):
        tension_type = "true_contradiction"
    elif all(not a["is_true_refutation"] for a in attacks):
        tension_type = "contrast_shift"
    else:
        tension_type = "mixed"

    # Summarize structured evidence types
    evidence_type_counts = {}
    for e in all_structured_evidence:
        evidence_type_counts[e.evidence_type] = evidence_type_counts.get(e.evidence_type, 0) + 1

    # Enhance the tension dict
    enhanced = {
        **tension,
        "attack_analysis": {
            "tension_type": tension_type,
            "n_attacks": len(attacks),
            "n_true_refutations": sum(1 for a in attacks if a["is_true_refutation"]),
            "n_contrast_shifts": sum(1 for a in attacks if not a["is_true_refutation"]),
            "n_structured_detections": sum(1 for a in attacks if a.get("detection_method") == "structured"),
            "evidence_type_summary": evidence_type_counts,
            "attacks": attacks,
        }
    }

    return enhanced
