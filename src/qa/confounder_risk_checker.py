"""
Confounder Risk Detection Module — ATLAS System
================================================

Detects potential confounding variables in causal belief extraction.
Uses three strategies:

1. Known Confounder Registry — Common confounders in environmental psychology
2. Study Design Assessment — Observational vs. experimental risk profiles
3. Covariate Control Check — Did the study mention controlling for confounders?

This module implements Judea Pearl's causal hierarchy perspective on confounder risk:
confounders pose the greatest threat to causal inference in observational designs.

Usage:
    from src.qa.confounder_risk_checker import ConfounderRiskChecker

    checker = ConfounderRiskChecker()

    # Single belief assessment
    report = checker.assess_confounder_risk(belief)
    print(report.risk_level)  # HIGH/MEDIUM/LOW
    print(report.known_confounders)
    print(report.recommendation)

    # Batch assessment
    batch = checker.assess_all_beliefs(beliefs_dict)
    print(batch.high_risk_count)
    print(batch.summary())
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# --- Risk Level Enumeration ---

class RiskLevel(str, Enum):
    """Confounder risk severity level."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# --- Known Confounders Registry ---

KNOWN_CONFOUNDERS = {
    "green_space": [
        "socioeconomic_status",
        "physical_activity",
        "air_quality",
        "noise_level",
        "self_selection",
        "access_proximity",
        "neighborhood_safety",
        "urban_density",
    ],
    "lighting": [
        "time_of_day",
        "seasonal_affective_disorder",
        "task_type",
        "age",
        "circadian_phase",
        "eye_strain",
        "screen_time",
        "light_sensitivity",
    ],
    "noise": [
        "air_quality",
        "socioeconomic_status",
        "sleep_quality",
        "personality_trait",
        "hearing_sensitivity",
        "stress_level",
        "cognitive_load",
        "attention_capacity",
    ],
    "temperature": [
        "humidity",
        "air_quality",
        "clothing",
        "metabolic_rate",
        "acclimatization",
        "activity_level",
        "age",
        "body_composition",
    ],
    "spatial_layout": [
        "familiarity",
        "wayfinding_ability",
        "cultural_background",
        "mobility_status",
        "cognitive_ability",
        "vision_acuity",
        "prior_exposure",
    ],
    "color": [
        "cultural_association",
        "context",
        "personal_preference",
        "lighting_condition",
        "color_blindness",
        "age_related_vision",
        "emotional_state",
    ],
    "biophilia": [
        "novelty",
        "attention_restoration",
        "physical_activity",
        "social_interaction",
        "childhood_exposure",
        "cultural_background",
        "aesthetic_preference",
    ],
    "crowding": [
        "personal_space_norm",
        "cultural_background",
        "personality_trait",
        "control_perception",
        "familiarity_with_others",
        "social_anxiety",
        "age",
    ],
    "air_quality": [
        "humidity",
        "temperature",
        "particulate_matter",
        "volatile_organic_compounds",
        "ventilation_rate",
        "outdoor_pm",
        "pollen_count",
    ],
    "water_feature": [
        "sound_level",
        "temperature",
        "visual_complexity",
        "movement_type",
        "cultural_familiarity",
        "accessibility",
    ],
}


# --- Study Design Classification ---

class StudyDesign(str, Enum):
    """Study design classification affecting confounder risk."""
    RANDOMIZED_CONTROLLED_TRIAL = "rct"
    QUASI_EXPERIMENTAL = "quasi_experimental"
    OBSERVATIONAL = "observational"
    QUALITATIVE = "qualitative"
    UNKNOWN = "unknown"


# --- Data Models ---

@dataclass
class ConfounderRiskReport:
    """Risk assessment report for a single belief."""

    belief_id: str
    risk_level: RiskLevel
    study_design: StudyDesign
    known_confounders: List[str] = field(default_factory=list)
    controlled_covariates: List[str] = field(default_factory=list)
    design_risk_score: float = 0.0
    confounder_count: int = 0
    control_adequacy_score: float = 0.0
    confidence: float = 0.0
    recommendation: str = ""
    reasoning: str = ""
    panelist_concern: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return {
            "belief_id": self.belief_id,
            "risk_level": self.risk_level.value,
            "study_design": self.study_design.value,
            "known_confounders": self.known_confounders,
            "confounder_count": self.confounder_count,
            "controlled_covariates": self.controlled_covariates,
            "design_risk_score": round(self.design_risk_score, 3),
            "control_adequacy_score": round(self.control_adequacy_score, 3),
            "confidence": round(self.confidence, 3),
            "recommendation": self.recommendation,
            "reasoning": self.reasoning,
            "panelist_concern": self.panelist_concern,
        }

    def summary(self) -> str:
        """Human-readable summary of risk assessment."""
        lines = [
            f"Belief: {self.belief_id}",
            f"Risk Level: {self.risk_level.value.upper()}",
            f"Study Design: {self.study_design.value}",
            f"Known Confounders: {len(self.known_confounders)} identified",
            f"Controlled Covariates: {len(self.controlled_covariates)}",
            f"Confidence: {self.confidence:.2%}",
            f"",
            f"Recommendation: {self.recommendation}",
        ]
        if self.panelist_concern:
            lines.append(f"Panel Concern: {self.panelist_concern}")
        return "\n".join(lines)


@dataclass
class BatchConfounderReport:
    """Risk assessment report for multiple beliefs."""

    beliefs_assessed: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    reports: List[ConfounderRiskReport] = field(default_factory=list)

    @property
    def high_risk_beliefs(self) -> List[ConfounderRiskReport]:
        """Filter for high-risk beliefs."""
        return [r for r in self.reports if r.risk_level == RiskLevel.HIGH]

    @property
    def medium_risk_beliefs(self) -> List[ConfounderRiskReport]:
        """Filter for medium-risk beliefs."""
        return [r for r in self.reports if r.risk_level == RiskLevel.MEDIUM]

    @property
    def low_risk_beliefs(self) -> List[ConfounderRiskReport]:
        """Filter for low-risk beliefs."""
        return [r for r in self.reports if r.risk_level == RiskLevel.LOW]

    @property
    def mean_design_risk(self) -> float:
        """Average design risk across all beliefs."""
        if not self.reports:
            return 0.0
        return sum(r.design_risk_score for r in self.reports) / len(self.reports)

    @property
    def mean_control_adequacy(self) -> float:
        """Average control adequacy across all beliefs."""
        if not self.reports:
            return 0.0
        return sum(r.control_adequacy_score for r in self.reports) / len(self.reports)

    @property
    def mean_confidence(self) -> float:
        """Average assessment confidence."""
        if not self.reports:
            return 0.0
        return sum(r.confidence for r in self.reports) / len(self.reports)

    def summary(self) -> str:
        """Human-readable summary of batch assessment."""
        lines = [
            f"Batch Confounder Risk Assessment",
            f"{'=' * 50}",
            f"Beliefs Assessed: {self.beliefs_assessed}",
            f"High Risk: {self.high_risk_count} ({100*self.high_risk_count/max(1, self.beliefs_assessed):.1f}%)",
            f"Medium Risk: {self.medium_risk_count} ({100*self.medium_risk_count/max(1, self.beliefs_assessed):.1f}%)",
            f"Low Risk: {self.low_risk_count} ({100*self.low_risk_count/max(1, self.beliefs_assessed):.1f}%)",
            f"",
            f"Mean Design Risk Score: {self.mean_design_risk:.3f}",
            f"Mean Control Adequacy: {self.mean_control_adequacy:.3f}",
            f"Mean Assessment Confidence: {self.mean_confidence:.3f}",
        ]
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert batch report to dictionary format."""
        return {
            "beliefs_assessed": self.beliefs_assessed,
            "high_risk_count": self.high_risk_count,
            "medium_risk_count": self.medium_risk_count,
            "low_risk_count": self.low_risk_count,
            "mean_design_risk": round(self.mean_design_risk, 3),
            "mean_control_adequacy": round(self.mean_control_adequacy, 3),
            "mean_confidence": round(self.mean_confidence, 3),
            "reports": [r.to_dict() for r in self.reports],
        }


# --- Main Checker Class ---

class ConfounderRiskChecker:
    """
    Confounder risk detector for causal beliefs in environmental psychology.

    Implements three detection strategies:
    1. Known confounder registry lookup
    2. Study design risk assessment (observational >> experimental)
    3. Covariate control adequacy check

    Risk scoring logic:
    - Observational design + known confounders + no controls = HIGH
    - Quasi-experimental + known confounders + partial controls = MEDIUM
    - RCT design = LOW (regardless of confounders, randomization controls them)
    - Qualitative design = LOW (different epistemic standard)
    """

    def __init__(self, custom_confounders: Optional[Dict[str, List[str]]] = None):
        """
        Initialize confounder checker.

        Args:
            custom_confounders: Optional custom confounder registry.
                               Defaults to KNOWN_CONFOUNDERS.
        """
        self.confounders = custom_confounders or KNOWN_CONFOUNDERS
        logger.info(f"ConfounderRiskChecker initialized with {len(self.confounders)} domains")

    def get_study_design(self, belief: Dict[str, Any]) -> StudyDesign:
        """
        Infer study design from belief metadata.

        Args:
            belief: Belief dict with optional fields:
                   - study_design: explicit design string
                   - article_type: experimental/observational/qualitative
                   - article_type_family: empirical/qualitative/theoretical
                   - n: sample size
                   - p_value: presence of p_value suggests statistical test
        """
        # Explicit design field
        design = (belief.get("study_design") or "").lower()
        if "rct" in design or "randomized" in design or "controlled trial" in design:
            return StudyDesign.RANDOMIZED_CONTROLLED_TRIAL
        if "quasi" in design:
            return StudyDesign.QUASI_EXPERIMENTAL
        if "observational" in design or "correlational" in design or "longitudinal" in design or "cross-sectional" in design:
            return StudyDesign.OBSERVATIONAL

        # Article type family
        article_type = (belief.get("article_type") or "").lower()
        if "experimental" in article_type:
            return StudyDesign.RANDOMIZED_CONTROLLED_TRIAL
        if "quasi" in article_type:
            return StudyDesign.QUASI_EXPERIMENTAL
        if "observational" in article_type or "correlational" in article_type:
            return StudyDesign.OBSERVATIONAL

        article_family = (belief.get("article_type_family") or "").lower()
        if "qualitative" in article_family:
            return StudyDesign.QUALITATIVE
        if "empirical" in article_family:
            # Default empirical to observational unless randomized is mentioned
            return StudyDesign.OBSERVATIONAL

        return StudyDesign.UNKNOWN

    def get_design_risk_score(self, design: StudyDesign) -> float:
        """
        Score confounder risk based on study design.

        RCT/Qualitative: 0.1 (low, randomization controls confounders)
        Quasi-experimental: 0.5 (medium risk)
        Observational: 0.9 (high risk, no randomization)
        Unknown: 0.6 (default to medium-high)

        Args:
            design: StudyDesign enum value

        Returns:
            Risk score 0.0-1.0
        """
        design_risk_map = {
            StudyDesign.RANDOMIZED_CONTROLLED_TRIAL: 0.1,
            StudyDesign.QUALITATIVE: 0.1,
            StudyDesign.QUASI_EXPERIMENTAL: 0.5,
            StudyDesign.OBSERVATIONAL: 0.9,
            StudyDesign.UNKNOWN: 0.6,
        }
        return design_risk_map.get(design, 0.6)

    def lookup_known_confounders(self, belief: Dict[str, Any]) -> List[str]:
        """
        Lookup plausible confounders for a belief's antecedent variable.

        Searches across all domains if domain not explicitly identified.

        Args:
            belief: Belief dict with field:
                   - antecedent: The independent variable (e.g., "green space")
                   - domain: Optional domain key (e.g., "green_space")

        Returns:
            List of plausible confounders from registry
        """
        antecedent = (belief.get("antecedent") or "").lower()
        domain = (belief.get("domain") or "").lower()

        # Try explicit domain first
        if domain in self.confounders:
            return self.confounders[domain][:]

        # Search by antecedent text matching
        for domain_key, confounder_list in self.confounders.items():
            if domain_key.replace("_", " ") in antecedent:
                return confounder_list[:]

        # No match found
        return []

    def extract_controlled_covariates(self, belief: Dict[str, Any]) -> List[str]:
        """
        Extract covariates mentioned as controlled in the belief.

        Searches fields:
        - controlled_variables: explicit list
        - covariates_controlled: explicit list
        - statistical_control: text description
        - methods: text description

        Args:
            belief: Belief dict

        Returns:
            List of covariates mentioned as controlled
        """
        covariates = []

        # Check explicit controlled variable fields
        ctrl_vars = belief.get("controlled_variables") or []
        if isinstance(ctrl_vars, list):
            covariates.extend([v.lower() for v in ctrl_vars if isinstance(v, str)])

        covariates_ctrl = belief.get("covariates_controlled") or []
        if isinstance(covariates_ctrl, list):
            covariates.extend([v.lower() for v in covariates_ctrl if isinstance(v, str)])

        # Check text descriptions
        stat_control = (belief.get("statistical_control") or "").lower()
        methods = (belief.get("methods") or "").lower()

        # Simple keyword detection for control mentions
        control_keywords = ["controlled for", "adjusted for", "covariate", "analysis of covariance",
                           "ancova", "regression control", "partial correlation"]
        for keyword in control_keywords:
            if keyword in stat_control or keyword in methods:
                # Mark as mentioning control (specific covariates may not be extractable)
                if "control" not in covariates:
                    covariates.append("control_mentioned")

        return covariates

    def calculate_control_adequacy(self, known_confounders: List[str],
                                  controlled_covariates: List[str]) -> float:
        """
        Score adequacy of controls for known confounders.

        If any controlled covariate matches a known confounder, that confounder
        is considered controlled. Score is ratio of controlled to total known.

        If "control_mentioned" exists but specific covariates aren't listed,
        assume 50% adequacy (conservative).

        Args:
            known_confounders: List of plausible confounders for this belief
            controlled_covariates: List of covariates mentioned as controlled

        Returns:
            Score 0.0-1.0 (1.0 = all confounders controlled, 0.0 = none)
        """
        if not known_confounders:
            return 1.0  # No known confounders = perfect control

        if not controlled_covariates:
            return 0.0  # No controls mentioned

        # Check for generic "control_mentioned" marker
        if "control_mentioned" in controlled_covariates and len(controlled_covariates) == 1:
            # Study mentions controls but we can't extract specifics
            # Conservative: assume 50% adequacy
            return 0.5

        # Count how many known confounders are explicitly controlled
        controlled_count = 0
        for covariate in controlled_covariates:
            for confounder in known_confounders:
                if confounder.lower() in covariate.lower() or covariate.lower() in confounder.lower():
                    controlled_count += 1
                    break

        return controlled_count / len(known_confounders)

    def assess_confounder_risk(self, belief: Dict[str, Any]) -> ConfounderRiskReport:
        """
        Assess confounder risk for a single belief.

        Combines:
        1. Study design risk
        2. Known confounder identification
        3. Control adequacy assessment

        Risk scoring logic:
        - RCT or Qualitative: LOW (design mitigates confounding)
        - Observational + known confounders + no controls: HIGH
        - Observational + known confounders + partial controls: MEDIUM
        - Quasi-experimental: MEDIUM default, adjusted by controls

        Args:
            belief: Belief dict from extraction with fields:
                   antecedent, consequent, study_design, article_type, etc.

        Returns:
            ConfounderRiskReport with assessment and recommendation
        """
        belief_id = belief.get("belief_id") or belief.get("id") or "unknown"

        # 1. Infer study design
        design = self.get_study_design(belief)
        design_risk = self.get_design_risk_score(design)

        # 2. Lookup known confounders
        confounders = self.lookup_known_confounders(belief)
        confounder_count = len(confounders)

        # 3. Extract controlled covariates
        controlled = self.extract_controlled_covariates(belief)

        # 4. Calculate control adequacy
        control_adequacy = self.calculate_control_adequacy(confounders, controlled)

        # 5. Determine risk level
        # RCT or qualitative → always LOW regardless of confounders
        if design in (StudyDesign.RANDOMIZED_CONTROLLED_TRIAL, StudyDesign.QUALITATIVE):
            risk_level = RiskLevel.LOW
            confidence = 0.95
            reasoning = f"{design.value} design mitigates confounding through randomization/methodology."
            recommendation = "Risk is low. No additional confounder controls needed."
            panelist_concern = ""

        # Observational design
        elif design == StudyDesign.OBSERVATIONAL:
            if not confounders:
                # No known confounders identified
                risk_level = RiskLevel.LOW
                confidence = 0.60
                reasoning = "Observational design but no known confounders for this variable."
                recommendation = "Monitor for unmeasured confounding. Consider sensitivity analysis."
                panelist_concern = ""
            elif control_adequacy >= 0.75:
                # Most confounders controlled
                risk_level = RiskLevel.LOW
                confidence = 0.85
                reasoning = f"Observational design but {control_adequacy:.0%} of known confounders controlled."
                recommendation = "Risk mitigated by extensive controls. Acceptable for inclusion."
                panelist_concern = "Verify covariate selection was theory-driven, not p-hacking."
            elif control_adequacy >= 0.50:
                # Some confounders controlled
                risk_level = RiskLevel.MEDIUM
                confidence = 0.80
                reasoning = f"Observational design with {control_adequacy:.0%} of confounders controlled. Risk remains."
                recommendation = "Acceptable with cautious interpretation. Flag for panel review."
                panelist_concern = "Pearl: unobserved confounders may still bias estimates."
            else:
                # Few or no confounders controlled
                risk_level = RiskLevel.HIGH
                confidence = 0.90
                reasoning = f"Observational design with {confounder_count} known confounders, <50% controlled."
                recommendation = "High confounder risk. Recommend rejection or substantial revision."
                panelist_concern = (
                    "Pearl: observational study without confounder control violates identification assumptions. "
                    "Causal claim cannot be established."
                )

        # Quasi-experimental design
        elif design == StudyDesign.QUASI_EXPERIMENTAL:
            if not confounders:
                risk_level = RiskLevel.LOW
                confidence = 0.70
                reasoning = "Quasi-experimental design with no known confounders identified."
                recommendation = "Risk acceptable. Monitor for group differences."
                panelist_concern = ""
            elif control_adequacy >= 0.75:
                risk_level = RiskLevel.LOW
                confidence = 0.80
                reasoning = f"Quasi-experimental design with {control_adequacy:.0%} of confounders controlled."
                recommendation = "Risk mitigated. Acceptable for inclusion."
                panelist_concern = ""
            else:
                risk_level = RiskLevel.MEDIUM
                confidence = 0.75
                reasoning = f"Quasi-experimental design with uncontrolled confounders (adequacy: {control_adequacy:.0%})."
                recommendation = "Medium risk. Recommend additional analysis or matching strategies."
                panelist_concern = "Verify treatment groups are comparable on key covariates (e.g., via balance table)."

        # Unknown design
        else:
            if not confounders:
                risk_level = RiskLevel.LOW
                confidence = 0.50
                reasoning = "Unknown study design; no known confounders identified."
                recommendation = "Clarify study design before final acceptance."
                panelist_concern = ""
            else:
                risk_level = RiskLevel.MEDIUM
                confidence = 0.50
                reasoning = f"Unknown study design with {confounder_count} known confounders."
                recommendation = "Require clarification of study design. Current risk assessment provisional."
                panelist_concern = ""

        return ConfounderRiskReport(
            belief_id=belief_id,
            risk_level=risk_level,
            study_design=design,
            known_confounders=confounders,
            controlled_covariates=controlled,
            design_risk_score=design_risk,
            confounder_count=confounder_count,
            control_adequacy_score=control_adequacy,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning,
            panelist_concern=panelist_concern,
        )

    def assess_all_beliefs(self, beliefs: Dict[str, Any] | List[Dict[str, Any]]) -> BatchConfounderReport:
        """
        Assess confounder risk for multiple beliefs.

        Args:
            beliefs: Dict mapping belief_id → belief dict, or List of belief dicts

        Returns:
            BatchConfounderReport with aggregate statistics and all reports
        """
        # Normalize input
        belief_list = []
        if isinstance(beliefs, dict):
            for belief_id, belief_dict in beliefs.items():
                if "belief_id" not in belief_dict:
                    belief_dict["belief_id"] = belief_id
                belief_list.append(belief_dict)
        else:
            belief_list = beliefs

        # Assess each belief
        reports = []
        for belief in belief_list:
            report = self.assess_confounder_risk(belief)
            reports.append(report)

        # Aggregate statistics
        batch = BatchConfounderReport(
            beliefs_assessed=len(reports),
            reports=reports,
        )
        batch.high_risk_count = len(batch.high_risk_beliefs)
        batch.medium_risk_count = len(batch.medium_risk_beliefs)
        batch.low_risk_count = len(batch.low_risk_beliefs)

        logger.info(
            f"Batch assessment complete: {batch.high_risk_count} high, "
            f"{batch.medium_risk_count} medium, {batch.low_risk_count} low"
        )

        return batch
