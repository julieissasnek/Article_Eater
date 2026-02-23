"""
Interpretive Intelligence for Article Eater Post-Quinean.

TODO 2: Interpretive Intelligence

Sprints:
- Sprint E: Core patterns, vocabulary bridge, engine
- Sprint F: Credibility explainer, search context generator
- Sprint G: Template refinement, COMPREHENSIVE detail level

Per Phase D revised plan:
- Two patterns initially: EVIDENCE, PRACTICAL (per Lampson)
- Separated DetailLevel from ExpertiseLevel (per Simon)
- Question classification with clarification (per Wilson)
- Gap identification for TODO 3 integration

This module translates the web's epistemic structure into
human-understandable explanations.

Date: January 20, 2026
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Union
from enum import Enum
from datetime import datetime, timezone

from src.services.web_of_belief import (
    WebOfBelief,
    Belief,
    Constraint,
    Credence,
    EpistemicLevel,
    ConstraintType,
)

logger = logging.getLogger(__name__)


# =============================================================================
# SIMPLIFIED DATA STRUCTURES (per Lampson/Simon)
# =============================================================================

class ExplanationPattern(Enum):
    """
    Explanation patterns (expanded per Phase D plan).

    Started with two (per Lampson), added more as needed.
    """
    EVIDENCE = "evidence"          # What supports this belief?
    PRACTICAL = "practical"        # What should I do with this?
    MECHANISM = "mechanism"        # How does this work? (Pearl)
    DISAGREEMENT = "disagreement"  # Where do experts differ? (Cartwright)


class DetailLevel(Enum):
    """
    Separated from expertise (per Simon).

    Controls how much information to include.
    """
    SUMMARY = 1       # One paragraph
    STANDARD = 2      # Full explanation
    COMPREHENSIVE = 3 # All details


class ExpertiseLevel(Enum):
    """
    Separated from detail (per Simon).

    Controls vocabulary and assumed knowledge.
    """
    NOVICE = 1        # Define technical terms
    PRACTITIONER = 2  # Assume domain knowledge
    RESEARCHER = 3    # Assume methodological sophistication


@dataclass
class ExplanationRequest:
    """
    A request for explanation.

    Minimal structure per Lampson.
    """
    pattern: ExplanationPattern
    belief_id: str
    detail: DetailLevel = DetailLevel.STANDARD
    expertise: ExpertiseLevel = ExpertiseLevel.PRACTITIONER


@dataclass
class IdentifiedGap:
    """
    Gap discovered during explanation (feeds TODO 3).

    Per Phase D: Two types initially.
    """
    gap_type: str  # "uncertain" or "unexplored"
    description: str
    belief_id: str
    priority: float  # Higher = more important to fill

    def to_dict(self) -> Dict[str, Any]:
        return {
            'gap_type': self.gap_type,
            'description': self.description,
            'belief_id': self.belief_id,
            'priority': self.priority,
        }


@dataclass
class ExplanationResponse:
    """
    Response from explanation engine.

    Minimal structure per Lampson.
    """
    success: bool
    explanation: str = ""
    pattern: Optional[ExplanationPattern] = None
    detail: Optional[DetailLevel] = None
    identified_gaps: List[IdentifiedGap] = field(default_factory=list)
    structured_data: Optional[Any] = None
    message: Optional[str] = None  # For errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'explanation': self.explanation,
            'pattern': self.pattern.value if self.pattern else None,
            'detail': self.detail.value if self.detail else None,
            'identified_gaps': [g.to_dict() for g in self.identified_gaps],
            'message': self.message,
        }


@dataclass
class ClarifyingQuestion:
    """
    Question to ask user when classification uncertain (per Wilson).
    """
    prompt: str
    options: List[Tuple[str, ExplanationPattern]]


# =============================================================================
# EVIDENCE PATTERN STRUCTURES
# =============================================================================

@dataclass
class EvidenceItem:
    """A single piece of evidence supporting or contradicting a belief."""
    belief_id: str
    content: str
    source_paper: str
    constraint_strength: float
    study_quality: float  # Methodology score if available
    sample_size: Optional[int]
    effect_size: Optional[float]
    is_supporting: bool
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'belief_id': self.belief_id,
            'content': self.content,
            'source_paper': self.source_paper,
            'constraint_strength': self.constraint_strength,
            'study_quality': self.study_quality,
            'sample_size': self.sample_size,
            'effect_size': self.effect_size,
            'is_supporting': self.is_supporting,
            'summary': self.summary,
        }


@dataclass
class EvidenceTraceResult:
    """Result of evidence trace traversal."""
    target_belief: Belief
    supporting_evidence: List[EvidenceItem]
    contradicting_evidence: List[EvidenceItem]
    total_studies: int
    strongest_support: Optional[EvidenceItem]
    evidence_strength: str  # "strong", "moderate", "preliminary"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'target_belief_id': self.target_belief.belief_id,
            'target_content': self.target_belief.content,
            'n_supporting': len(self.supporting_evidence),
            'n_contradicting': len(self.contradicting_evidence),
            'total_studies': self.total_studies,
            'evidence_strength': self.evidence_strength,
            'supporting': [e.to_dict() for e in self.supporting_evidence],
            'contradicting': [e.to_dict() for e in self.contradicting_evidence],
        }


# =============================================================================
# PRACTICAL IMPLICATIONS STRUCTURES
# =============================================================================

@dataclass
class PracticalImplication:
    """A practical implication for design."""
    action: str
    evidence_strength: str  # "strong", "moderate", "preliminary"
    confidence: float
    caveats: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'action': self.action,
            'evidence_strength': self.evidence_strength,
            'confidence': self.confidence,
            'caveats': self.caveats,
        }


@dataclass
class PracticalResult:
    """Result of practical implications generation."""
    target_belief: Belief
    implications: List[PracticalImplication]
    design_considerations: List[str]
    caveats: List[str]
    applicability_note: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'target_belief_id': self.target_belief.belief_id,
            'implications': [i.to_dict() for i in self.implications],
            'design_considerations': self.design_considerations,
            'caveats': self.caveats,
            'applicability_note': self.applicability_note,
        }


# =============================================================================
# QUESTION CLASSIFICATION (per Wilson)
# =============================================================================

class QuestionClassifier:
    """
    Classify questions with confidence thresholding.

    Per Wilson: When uncertain, ask for clarification rather than guess.
    """

    PATTERN_KEYWORDS = {
        ExplanationPattern.EVIDENCE: [
            "evidence", "support", "studies", "research", "proof",
            "data", "findings", "shows", "demonstrated", "found"
        ],
        ExplanationPattern.PRACTICAL: [
            "should", "recommend", "design", "apply", "use",
            "implement", "practice", "suggest", "advice", "action"
        ],
        ExplanationPattern.MECHANISM: [
            "how", "why", "mechanism", "works", "cause", "causal",
            "process", "pathway", "mediator", "leads", "explains"
        ],
        ExplanationPattern.DISAGREEMENT: [
            "disagree", "controversy", "debate", "dispute", "conflict",
            "differ", "consensus", "contested", "agree", "opinion"
        ]
    }

    CLARIFICATION_THRESHOLD = 0.6

    def classify(self, question: str) -> Tuple[ExplanationPattern, float]:
        """
        Classify question and return confidence.

        Returns:
            Tuple of (pattern, confidence)
        """
        q_lower = question.lower()
        scores = {}

        for pattern, keywords in self.PATTERN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in q_lower)
            scores[pattern] = score

        if sum(scores.values()) == 0:
            # No keywords found, default to evidence with low confidence
            return ExplanationPattern.EVIDENCE, 0.3

        best_pattern = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = scores[best_pattern] / total if total > 0 else 0.5

        return best_pattern, confidence

    def classify_or_clarify(
        self,
        question: str
    ) -> Union[ExplanationPattern, ClarifyingQuestion]:
        """
        Return pattern or ask for clarification (per Wilson).

        When confidence is below threshold, ask user to clarify
        rather than making potentially wrong assumptions.
        """
        pattern, confidence = self.classify(question)

        if confidence < self.CLARIFICATION_THRESHOLD:
            return ClarifyingQuestion(
                prompt="What kind of answer are you looking for?",
                options=[
                    ("Evidence summary (what research shows)", ExplanationPattern.EVIDENCE),
                    ("Design recommendations (what to do)", ExplanationPattern.PRACTICAL),
                    ("Mechanism explanation (how it works)", ExplanationPattern.MECHANISM),
                    ("Disagreement summary (where experts differ)", ExplanationPattern.DISAGREEMENT)
                ]
            )

        return pattern


# =============================================================================
# EVIDENCE PATTERN IMPLEMENTATION
# =============================================================================

class EvidenceTracePattern:
    """
    Pattern: What evidence supports this belief?

    Traverses the web to gather supporting and contradicting evidence.
    """

    def traverse(self, web: WebOfBelief, belief_id: str) -> EvidenceTraceResult:
        """Traverse web to gather evidence for belief."""
        if belief_id not in web.beliefs:
            raise ValueError(f"Belief not found: {belief_id}")

        target = web.beliefs[belief_id]
        supporting = []
        contradicting = []

        # Get all constraints involving this belief
        for constraint_id, constraint in web.constraints.items():
            # Check if constraint involves our target belief
            is_source = constraint.source_id == belief_id
            is_target = constraint.target_id == belief_id

            if not (is_source or is_target):
                continue

            # Get the other belief in the constraint
            partner_id = constraint.target_id if is_source else constraint.source_id
            partner = web.beliefs.get(partner_id)

            if not partner:
                continue

            # Only consider empirical/observational evidence
            if partner.level not in [EpistemicLevel.EMPIRICAL, EpistemicLevel.OBSERVATIONAL]:
                continue

            # Create evidence item
            item = EvidenceItem(
                belief_id=partner.belief_id,
                content=partner.content,
                source_paper=self._get_source_paper(partner),
                constraint_strength=constraint.strength,
                study_quality=getattr(partner, 'methodology_score', 0.5),
                sample_size=getattr(partner, 'sample_size', None),
                effect_size=getattr(partner, 'effect_size', None),
                is_supporting=constraint.constraint_type == ConstraintType.SUPPORTS,
                summary=self._summarize_evidence(partner, constraint)
            )

            if constraint.constraint_type == ConstraintType.SUPPORTS:
                supporting.append(item)
            elif constraint.constraint_type == ConstraintType.CONTRADICTS:
                contradicting.append(item)

        # Sort by strength × quality
        supporting.sort(
            key=lambda e: e.constraint_strength * e.study_quality,
            reverse=True
        )
        contradicting.sort(
            key=lambda e: e.constraint_strength * e.study_quality,
            reverse=True
        )

        # Determine evidence strength
        n_studies = len(supporting) + len(contradicting)
        avg_effect = self._average_effect_size(supporting)

        if len(supporting) >= 5 and avg_effect and avg_effect > 0.3:
            evidence_strength = "strong"
        elif len(supporting) >= 2:
            evidence_strength = "moderate"
        else:
            evidence_strength = "preliminary"

        return EvidenceTraceResult(
            target_belief=target,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            total_studies=n_studies,
            strongest_support=supporting[0] if supporting else None,
            evidence_strength=evidence_strength
        )

    def _get_source_paper(self, belief: Belief) -> str:
        """Get source paper identifier from belief."""
        if hasattr(belief, 'paper_ids') and belief.paper_ids:
            return list(belief.paper_ids)[0]
        return "unknown"

    def _summarize_evidence(self, belief: Belief, constraint: Constraint) -> str:
        """Create a brief summary of the evidence."""
        content = belief.content[:100]
        if len(belief.content) > 100:
            content += "..."

        strength_desc = "strongly" if constraint.strength > 0.7 else "moderately" if constraint.strength > 0.4 else "weakly"
        return f"{strength_desc} supports: {content}"

    def _average_effect_size(self, evidence: List[EvidenceItem]) -> Optional[float]:
        """Calculate average effect size from evidence items."""
        effects = [e.effect_size for e in evidence if e.effect_size is not None]
        if not effects:
            return None
        return sum(effects) / len(effects)

    def render(
        self,
        result: EvidenceTraceResult,
        detail: DetailLevel,
        expertise: ExpertiseLevel
    ) -> str:
        """Render evidence trace to natural language."""
        if detail == DetailLevel.SUMMARY:
            return self._render_summary(result, expertise)
        elif detail == DetailLevel.STANDARD:
            return self._render_standard(result, expertise)
        else:
            return self._render_comprehensive(result, expertise)

    def _render_summary(self, result: EvidenceTraceResult, expertise: ExpertiseLevel) -> str:
        """One-paragraph summary."""
        n_support = len(result.supporting_evidence)
        n_contra = len(result.contradicting_evidence)

        # Adjust language for expertise level
        if expertise == ExpertiseLevel.NOVICE:
            confidence_phrase = {
                "strong": "well-supported by research",
                "moderate": "has some research support",
                "preliminary": "has limited research so far"
            }[result.evidence_strength]
        else:
            confidence_phrase = f"evidence strength: {result.evidence_strength}"

        text = f"**{result.target_belief.content}**\n\n"
        text += f"This finding is {confidence_phrase}. "
        text += f"Supported by {n_support} studies"
        if n_contra > 0:
            text += f", with {n_contra} studies reporting contrary findings"
        text += "."

        if result.strongest_support:
            text += f"\n\nStrongest support: {result.strongest_support.source_paper}"

        return text

    def _render_standard(self, result: EvidenceTraceResult, expertise: ExpertiseLevel) -> str:
        """Standard full explanation."""
        lines = []

        # Header
        lines.append(f"## Evidence for: {result.target_belief.content}")
        lines.append("")

        # Confidence summary
        credence = result.target_belief.credence
        if expertise == ExpertiseLevel.NOVICE:
            conf_pct = int(credence.value * 100)
            lines.append(f"**How confident?** About {conf_pct}% confident based on current research.")
        else:
            lines.append(f"**Confidence:** {credence.value:.0%} (± {credence.uncertainty:.0%})")
        lines.append("")

        # Supporting evidence
        lines.append(f"### Supporting Evidence ({len(result.supporting_evidence)} studies)")
        lines.append("")

        for i, item in enumerate(result.supporting_evidence[:5]):
            lines.append(f"- **{item.source_paper}**: {item.summary}")
            if expertise != ExpertiseLevel.NOVICE:
                details = f"  - Strength: {item.constraint_strength:.0%}"
                if item.sample_size:
                    details += f" | N={item.sample_size}"
                if item.effect_size:
                    details += f" | d={item.effect_size:.2f}"
                lines.append(details)
            lines.append("")

        if len(result.supporting_evidence) > 5:
            lines.append(f"*...and {len(result.supporting_evidence) - 5} more studies*")
            lines.append("")

        # Contradicting evidence
        if result.contradicting_evidence:
            lines.append(f"### Contradicting Evidence ({len(result.contradicting_evidence)} studies)")
            lines.append("")
            for item in result.contradicting_evidence[:3]:
                lines.append(f"- **{item.source_paper}**: {item.content[:80]}...")
            lines.append("")

        # Summary
        lines.append("### Summary")
        if result.strongest_support:
            lines.append(f"The strongest support comes from {result.strongest_support.source_paper}.")
        if result.contradicting_evidence:
            lines.append("Note: Some studies report contrary findings. See details above.")

        return "\n".join(lines)

    def _render_comprehensive(self, result: EvidenceTraceResult, expertise: ExpertiseLevel) -> str:
        """Comprehensive with all details."""
        lines = []

        lines.append(f"## Comprehensive Evidence Trace: {result.target_belief.content}")
        lines.append("")

        # Metadata
        lines.append("### Metadata")
        lines.append(f"- Belief ID: {result.target_belief.belief_id}")
        lines.append(f"- Epistemic Level: {result.target_belief.level.value}")
        if result.target_belief.scope:
            scope = result.target_belief.scope
            lines.append(f"- Scope: {getattr(scope, 'population', 'Unspecified')} / {getattr(scope, 'setting', 'Unspecified')}")
        lines.append("")

        # Quantitative summary
        lines.append("### Quantitative Summary")
        lines.append(f"- Total Studies: {result.total_studies}")
        lines.append(f"- Supporting: {len(result.supporting_evidence)}")
        lines.append(f"- Contradicting: {len(result.contradicting_evidence)}")
        if result.total_studies > 0:
            ratio = len(result.supporting_evidence) / result.total_studies
            lines.append(f"- Support Ratio: {ratio:.2f}")
        lines.append("")

        # Full evidence list
        lines.append("### Full Evidence List")
        lines.append("")

        for item in result.supporting_evidence:
            lines.append(f"#### {item.source_paper}")
            lines.append(f"- **Content:** {item.content}")
            lines.append(f"- **Constraint Strength:** {item.constraint_strength:.3f}")
            lines.append(f"- **Study Quality:** {item.study_quality:.2f}")
            lines.append(f"- **Sample Size:** {item.sample_size or 'NR'}")
            lines.append(f"- **Effect Size:** {f'{item.effect_size:.3f}' if item.effect_size else 'NR'}")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# PRACTICAL IMPLICATIONS PATTERN (per Kaplan)
# =============================================================================

class PracticalImplicationsPattern:
    """
    Pattern: What should I do with this?

    Per Kaplan: Every explanation should include actionable guidance.
    """

    # Mapping from domain concepts to design actions
    DESIGN_MAPPINGS = {
        ("natural_views", "stress"): "Provide visual access to natural elements (trees, plants, water) in high-stress areas",
        ("natural_plants", "stress"): "Incorporate live plants in spaces where stress reduction is important",
        ("natural_views", "mood"): "Maximize views of nature in occupied spaces to support positive mood",
        ("natural_lighting", "mood"): "Maximize natural daylight access in occupied spaces",
        ("natural_lighting", "productivity"): "Ensure adequate natural light in work areas",
        ("spatial_ceiling_height", "creativity"): "Consider higher ceilings in spaces intended for creative work",
        ("natural_elements", "restoration"): "Include natural materials and elements to support cognitive restoration",
        ("water_features", "stress"): "Consider water features in areas where calm is desired",
        ("greenery", "air_quality"): "Use appropriate plants for air quality improvement",
        ("biophilic", "wellbeing"): "Apply biophilic design principles to enhance occupant wellbeing",
    }

    def traverse(
        self,
        web: WebOfBelief,
        belief_id: str,
        evidence_result: Optional[EvidenceTraceResult] = None
    ) -> PracticalResult:
        """Generate practical implications for a belief."""
        if belief_id not in web.beliefs:
            raise ValueError(f"Belief not found: {belief_id}")

        belief = web.beliefs[belief_id]
        implications = []
        design_considerations = []
        caveats = []

        # Get evidence if not provided
        if evidence_result is None:
            evidence_pattern = EvidenceTracePattern()
            evidence_result = evidence_pattern.traverse(web, belief_id)

        evidence_strength = evidence_result.evidence_strength

        # Generate implications based on belief content
        design_action = self._map_to_design_action(belief)
        if design_action:
            implications.append(PracticalImplication(
                action=design_action,
                evidence_strength=evidence_strength,
                confidence=belief.credence.value,
                caveats=[]
            ))

        # Add design considerations based on belief level
        if belief.level == EpistemicLevel.EMPIRICAL:
            design_considerations.append(
                f"This is an empirically-tested finding with {evidence_strength} evidence."
            )
        elif belief.level == EpistemicLevel.THEORETICAL:
            design_considerations.append(
                "This is a theoretical principle; specific applications may vary."
            )

        # Add scope-based caveats
        if belief.scope:
            if hasattr(belief.scope, 'setting') and belief.scope.setting:
                caveats.append(f"Evidence primarily from {belief.scope.setting} settings")
            if hasattr(belief.scope, 'population') and belief.scope.population:
                caveats.append(f"Tested with {belief.scope.population}; may vary for other groups")

        # Lab-to-field caveat (per Kaplan)
        lab_count = 0
        for evidence in evidence_result.supporting_evidence:
            # Check if evidence is from lab setting
            if "lab" in evidence.content.lower() or "laboratory" in evidence.content.lower():
                lab_count += 1

        if len(evidence_result.supporting_evidence) > 0:
            if lab_count > len(evidence_result.supporting_evidence) * 0.5:
                caveats.append("Most evidence from laboratory settings; field effects may differ")

        # Applicability note
        n_studies = len(evidence_result.supporting_evidence)
        applicability_note = f"Evidence strength: {evidence_strength} ({n_studies} supporting studies)"

        return PracticalResult(
            target_belief=belief,
            implications=implications,
            design_considerations=design_considerations,
            caveats=caveats,
            applicability_note=applicability_note
        )

    def _map_to_design_action(self, belief: Belief) -> Optional[str]:
        """Map belief content to design recommendation."""
        content_lower = belief.content.lower()

        # Check for keyword matches
        for (env_key, outcome_key), action in self.DESIGN_MAPPINGS.items():
            if env_key.replace("_", " ") in content_lower or env_key in content_lower:
                if outcome_key in content_lower:
                    return action

        # Default recommendation based on content analysis
        if "nature" in content_lower or "natural" in content_lower:
            if "stress" in content_lower or "anxiety" in content_lower:
                return "Consider incorporating natural elements to support stress reduction"
            elif "attention" in content_lower or "cognitive" in content_lower:
                return "Consider natural elements to support cognitive function"
            elif "mood" in content_lower or "wellbeing" in content_lower:
                return "Consider natural elements to support occupant wellbeing"

        return None

    def render(
        self,
        result: PracticalResult,
        detail: DetailLevel,
        expertise: ExpertiseLevel
    ) -> str:
        """
        Render practical implications to natural language.

        Sprint G: Added proper detail level handling.
        """
        if detail == DetailLevel.SUMMARY:
            return self._render_practical_summary(result, expertise)
        elif detail == DetailLevel.STANDARD:
            return self._render_practical_standard(result, expertise)
        else:
            return self._render_practical_comprehensive(result, expertise)

    def _render_practical_summary(
        self,
        result: PracticalResult,
        expertise: ExpertiseLevel
    ) -> str:
        """One-paragraph practical summary."""
        if not result.implications:
            return f"No specific design recommendations could be derived from: {result.target_belief.content[:50]}..."

        impl = result.implications[0]
        if expertise == ExpertiseLevel.NOVICE:
            return f"**Recommendation:** {impl.action} This is supported by {impl.evidence_strength} evidence."
        else:
            return f"**{impl.action}** (Evidence: {impl.evidence_strength}, Confidence: {impl.confidence:.0%})"

    def _render_practical_standard(
        self,
        result: PracticalResult,
        expertise: ExpertiseLevel
    ) -> str:
        """Standard practical explanation."""
        lines = []

        lines.append("## Practical Implications")
        lines.append("")

        if result.implications:
            lines.append("### Design Recommendations")
            lines.append("")
            for impl in result.implications:
                strength_note = f"({impl.evidence_strength} evidence)"
                lines.append(f"- **{impl.action}** {strength_note}")
            lines.append("")

        if result.design_considerations:
            lines.append("### Design Considerations")
            lines.append("")
            for consideration in result.design_considerations:
                lines.append(f"- {consideration}")
            lines.append("")

        if result.caveats:
            lines.append("### Caveats for Implementation")
            lines.append("")
            for caveat in result.caveats:
                lines.append(f"- {caveat}")
            lines.append("")

        lines.append(f"*{result.applicability_note}*")

        return "\n".join(lines)

    def _render_practical_comprehensive(
        self,
        result: PracticalResult,
        expertise: ExpertiseLevel
    ) -> str:
        """
        Comprehensive practical explanation with all details.

        Sprint G: Added for COMPREHENSIVE detail level.
        """
        lines = []

        lines.append(f"## Comprehensive Practical Analysis: {result.target_belief.content}")
        lines.append("")

        # Metadata
        lines.append("### Analysis Metadata")
        lines.append(f"- Belief ID: `{result.target_belief.belief_id}`")
        lines.append(f"- Epistemic Level: {result.target_belief.level.value}")
        lines.append(f"- Credence: {result.target_belief.credence.value:.3f} (±{result.target_belief.credence.uncertainty:.3f})")
        if result.target_belief.scope:
            scope = result.target_belief.scope
            lines.append(f"- Population: {getattr(scope, 'population', 'Unspecified')}")
            lines.append(f"- Setting: {getattr(scope, 'setting', 'Unspecified')}")
        lines.append("")

        # Design Recommendations
        lines.append("### Design Recommendations")
        lines.append("")
        if result.implications:
            for i, impl in enumerate(result.implications, 1):
                lines.append(f"#### Recommendation {i}")
                lines.append(f"**Action:** {impl.action}")
                lines.append("")
                lines.append(f"- Evidence Strength: {impl.evidence_strength}")
                lines.append(f"- Confidence Level: {impl.confidence:.1%}")
                if impl.caveats:
                    lines.append("- Specific Caveats:")
                    for caveat in impl.caveats:
                        lines.append(f"  - {caveat}")
                lines.append("")
        else:
            lines.append("*No specific design recommendations derived.*")
            lines.append("")

        # Design Considerations
        if result.design_considerations:
            lines.append("### Design Considerations")
            lines.append("")
            for consideration in result.design_considerations:
                lines.append(f"- {consideration}")
            lines.append("")

        # Caveats and Limitations
        lines.append("### Caveats and Limitations")
        lines.append("")
        if result.caveats:
            for caveat in result.caveats:
                lines.append(f"- **{caveat}**")
        else:
            lines.append("- No specific caveats identified")
        lines.append("")

        # Applicability Assessment
        lines.append("### Applicability Assessment")
        lines.append(f"{result.applicability_note}")
        lines.append("")

        # Translation Guidance (per Kaplan)
        lines.append("### Lab-to-Practice Translation")
        lines.append("When applying these findings:")
        lines.append("- Consider local context and constraints")
        lines.append("- Start with pilot implementations")
        lines.append("- Monitor outcomes against research predictions")
        lines.append("- Document adaptations for future reference")

        return "\n".join(lines)


# =============================================================================
# MECHANISM PATTERN (per Pearl: explain causal structure)
# =============================================================================

@dataclass
class MechanismStep:
    """A single step in a causal mechanism chain."""
    belief_id: str
    content: str
    role: str  # "cause", "mediator", "effect", "moderator"
    evidence_strength: float
    mechanism_type: str  # "physiological", "psychological", "behavioral", "environmental"


@dataclass
class MechanismResult:
    """Result of mechanism traversal."""
    target_belief: Belief
    causal_chain: List[MechanismStep]
    mediators: List[MechanismStep]
    moderators: List[MechanismStep]
    mechanism_type: str
    confidence: float
    has_experimental_support: bool


class MechanismExplanationPattern:
    """
    Pattern: How does this work?

    Per Pearl: Explain causal mechanisms, not just correlations.
    Traces causal chains and identifies mediating/moderating factors.
    """

    def __init__(self, web: WebOfBelief):
        self.web = web

    # Constraint types that represent forward causal steps in a mechanism chain
    MECHANISM_FORWARD_TYPES = {
        ConstraintType.EPISTEMIC_MEDIATION,
        ConstraintType.SUPPORTS,
        ConstraintType.PROPOSES_MECHANISM,
        ConstraintType.THEORETICALLY_PREDICTS,
    }

    # Constraint types that represent cross-chain coherence (parallel routes)
    PARALLEL_ROUTE_TYPES = {
        ConstraintType.COHERENCE_SUPPORT,
    }

    def traverse(self, belief_id: str) -> Optional[MechanismResult]:
        """
        Trace causal mechanisms starting from a seed belief.

        Strategy:
          1. If belief_id points to a 'mechanism:' node, walk FORWARD along
             EPISTEMIC_MEDIATION / SUPPORTS chains to build the ordered chain.
          2. Otherwise (legacy: raw beliefs), look upstream for antecedents.
          3. Collect parallel routes (COHERENCE_SUPPORT) as additional mediators.
        """
        if belief_id not in self.web.beliefs:
            return None

        target = self.web.beliefs[belief_id]

        # --- Forward walk from mechanism: entry nodes ---
        if belief_id.startswith("mechanism:"):
            return self._traverse_forward(target)

        # --- Legacy: upstream antecedent search ---
        return self._traverse_upstream(target)

    def _traverse_forward(
        self,
        entry: Belief,
        max_depth: int = 8,
    ) -> MechanismResult:
        """
        Walk forward along EPISTEMIC_MEDIATION/SUPPORTS from the entry node.
        Returns an ordered causal chain as a list of MechanismSteps.
        """
        # Build forward index: source_id → list of (target_id, constraint)
        forward: Dict[str, List[tuple]] = {}
        for c in self.web.constraints.values():
            if c.constraint_type in self.MECHANISM_FORWARD_TYPES:
                forward.setdefault(c.source_id, []).append((c.target_id, c))
            if c.bidirectional and c.constraint_type in self.MECHANISM_FORWARD_TYPES:
                forward.setdefault(c.target_id, []).append((c.source_id, c))

        # BFS forward keeping insertion order for rendering
        visited: set = set()
        causal_chain: List[MechanismStep] = []
        mediators: List[MechanismStep] = []
        moderators: List[MechanismStep] = []
        parallel_routes: List[MechanismStep] = []
        has_experimental = False

        queue: List[tuple] = [(entry.belief_id, 0, None)]  # (belief_id, depth, incoming_constraint)
        while queue:
            node_id, depth, incoming_c = queue.pop(0)
            if node_id in visited or depth > max_depth:
                continue
            visited.add(node_id)

            node_belief = self.web.beliefs.get(node_id)
            if not node_belief:
                continue

            if node_id != entry.belief_id:
                # Determine role from incoming constraint
                role = "cause" if depth == 1 else "mediator"
                if incoming_c and getattr(incoming_c, 'mediator', None):
                    role = "mediator"

                step = MechanismStep(
                    belief_id=node_id,
                    content=node_belief.content,
                    role=role,
                    evidence_strength=getattr(incoming_c, 'strength', 0.5) if incoming_c else 0.5,
                    mechanism_type=self._infer_mechanism_type(node_belief),
                )
                # Attach mediator description from constraint for renderer
                if incoming_c and getattr(incoming_c, 'mediator', None):
                    step._mediator_desc = incoming_c.mediator
                else:
                    step._mediator_desc = None

                if role == "mediator":
                    mediators.append(step)
                causal_chain.append(step)

            # Follow forward edges — prefer mechanism: nodes first
            next_hops = sorted(
                forward.get(node_id, []),
                key=lambda x: (0 if x[0].startswith("mechanism:") else 1)
            )
            for next_id, c in next_hops:
                if next_id not in visited:
                    # Coherence edges = parallel routes, not sequential steps
                    if c.constraint_type in self.PARALLEL_ROUTE_TYPES:
                        nb = self.web.beliefs.get(next_id)
                        if nb:
                            parallel_routes.append(MechanismStep(
                                belief_id=next_id,
                                content=nb.content,
                                role="parallel_route",
                                evidence_strength=c.strength,
                                mechanism_type=self._infer_mechanism_type(nb),
                            ))
                    else:
                        queue.append((next_id, depth + 1, c))

        # Attach parallel routes as moderators slot (used in rendering)
        moderators = parallel_routes

        mechanism_type = self._determine_overall_mechanism(causal_chain, mediators)
        confidence = self._calculate_mechanism_confidence(causal_chain, mediators, has_experimental)

        return MechanismResult(
            target_belief=entry,
            causal_chain=causal_chain,
            mediators=mediators,
            moderators=moderators,
            mechanism_type=mechanism_type,
            confidence=confidence,
            has_experimental_support=has_experimental,
        )

    def _traverse_upstream(
        self,
        target: Belief,
    ) -> MechanismResult:
        """Legacy upstream traversal for non-mechanism: beliefs."""
        causal_chain = []
        mediators = []
        moderators = []
        has_experimental = False

        for constraint in self.web.constraints.values():
            if constraint.target_id != target.belief_id:
                continue
            source = self.web.beliefs.get(constraint.source_id)
            if not source:
                continue
            role = self._determine_role(constraint)
            step = MechanismStep(
                belief_id=source.belief_id,
                content=source.content,
                role=role,
                evidence_strength=getattr(constraint, 'strength', 0.5),
                mechanism_type=self._infer_mechanism_type(source),
            )
            step._mediator_desc = getattr(constraint, 'mediator', None)
            if role == "moderator":
                moderators.append(step)
            elif role == "mediator":
                mediators.append(step)
            else:
                causal_chain.append(step)

        mechanism_type = self._determine_overall_mechanism(causal_chain, mediators)
        confidence = self._calculate_mechanism_confidence(causal_chain, mediators, has_experimental)

        return MechanismResult(
            target_belief=target,
            causal_chain=causal_chain,
            mediators=mediators,
            moderators=moderators,
            mechanism_type=mechanism_type,
            confidence=confidence,
            has_experimental_support=has_experimental,
        )

    def _determine_role(self, constraint: Constraint) -> str:
        """Determine the causal role of a constraint."""
        ctype = constraint.constraint_type
        if ctype == ConstraintType.EXPLAINS:
            return "cause"
        elif hasattr(constraint, 'mediator') and constraint.mediator:
            return "mediator"
        elif hasattr(constraint, 'is_moderator') and constraint.is_moderator:
            return "moderator"
        return "cause"

    def _infer_mechanism_type(self, belief: Belief) -> str:
        """Infer the type of mechanism from belief content."""
        content_lower = belief.content.lower()
        if any(w in content_lower for w in ['cortisol', 'heart rate', 'blood', 'neural', 'brain']):
            return "physiological"
        elif any(w in content_lower for w in ['stress', 'attention', 'mood', 'cognitive', 'memory']):
            return "psychological"
        elif any(w in content_lower for w in ['behavior', 'action', 'movement', 'activity']):
            return "behavioral"
        return "environmental"

    def _determine_overall_mechanism(
        self,
        causal_chain: List[MechanismStep],
        mediators: List[MechanismStep]
    ) -> str:
        """Determine the dominant mechanism type."""
        all_steps = causal_chain + mediators
        if not all_steps:
            return "unknown"

        type_counts: Dict[str, int] = {}
        for step in all_steps:
            type_counts[step.mechanism_type] = type_counts.get(step.mechanism_type, 0) + 1

        return max(type_counts, key=type_counts.get)

    def _calculate_mechanism_confidence(
        self,
        causal_chain: List[MechanismStep],
        mediators: List[MechanismStep],
        has_experimental: bool
    ) -> float:
        """Calculate confidence in the mechanism explanation."""
        if not causal_chain:
            return 0.2

        # Average evidence strength
        all_steps = causal_chain + mediators
        avg_strength = sum(s.evidence_strength for s in all_steps) / len(all_steps)

        # Bonus for experimental support
        if has_experimental:
            avg_strength = min(1.0, avg_strength + 0.15)

        # Penalty for long chains (more uncertainty compounds)
        chain_penalty = max(0, (len(causal_chain) - 3) * 0.05)

        return max(0.1, avg_strength - chain_penalty)

    def render(
        self,
        result: MechanismResult,
        detail: DetailLevel,
        expertise: ExpertiseLevel
    ) -> str:
        """Render mechanism explanation as an ordered causal chain narrative."""
        lines = []

        # ── Header ────────────────────────────────────────────────────────────
        entry = result.target_belief
        entry_label = self._belief_label(entry)
        lines.append(f"## Causal Mechanism: {entry_label}")
        lines.append("")
        lines.append(
            f"**Mechanism type:** {result.mechanism_type.title()} "
            f"| **Confidence:** {result.confidence:.0%}"
        )
        if result.has_experimental_support:
            lines.append("*(Supported by experimental evidence)*")
        lines.append("")

        if not result.causal_chain:
            lines.append(
                "*No causal chain found in the belief graph for this node. "
                "More mechanism beliefs may need to be seeded.*"
            )
            return "\n".join(lines)

        # ── Ordered causal chain with arrow connectors ────────────────────────
        lines.append("### Causal Chain")
        lines.append("")

        # Entry node
        lines.append(f"**[STIMULUS / ENTRY]** {self._belief_label(entry)}")
        if detail != DetailLevel.SUMMARY:
            lines.append(f"> {self._first_sentence(entry.content)}")
        lines.append("")

        for i, step in enumerate(result.causal_chain):
            # Arrow connector with mediator description
            mediator_desc = getattr(step, '_mediator_desc', None)
            if mediator_desc:
                lines.append(f"  ↓ *[{mediator_desc}]*")
            else:
                lines.append("  ↓")

            # Role badge
            role_badge = {
                "cause": "STEP",
                "mediator": "MEDIATED BY",
                "parallel_route": "PARALLEL ROUTE",
            }.get(step.role, "STEP")

            label = self._belief_label_from_id(step.belief_id)
            lines.append(f"**[{role_badge} {i + 1}]** {label}")

            if detail == DetailLevel.SUMMARY:
                lines.append(f"> {step.content[:100]}...")
            else:
                lines.append(f"> {self._first_sentence(step.content)}")
                if detail == DetailLevel.COMPREHENSIVE:
                    lines.append(f"> *(Evidence strength: {step.evidence_strength:.0%} "
                                 f"| Type: {step.mechanism_type})*")
                    # Full content for comprehensive
                    rest = self._remaining_sentences(step.content)
                    if rest:
                        lines.append(f"> {rest}")
            lines.append("")

        # ── Parallel routes (simultaneously active chains) ─────────────────────
        if result.moderators and detail != DetailLevel.SUMMARY:
            parallel = [m for m in result.moderators if m.role == "parallel_route"]
            if parallel:
                lines.append("### Parallel Routes (simultaneous)")
                lines.append(
                    "The same stimulus also activates these concurrent pathways:"
                )
                lines.append("")
                for pr in parallel:
                    pr_label = self._belief_label_from_id(pr.belief_id)
                    lines.append(f"- **{pr_label}**")
                    lines.append(f"  {self._first_sentence(pr.content)}")
                lines.append("")

        # ── Expertise-appropriate closing note ────────────────────────────────
        if expertise == ExpertiseLevel.NOVICE:
            lines.append("### What This Means in Practice")
            lines.append(
                f"This works through a {result.mechanism_type} process — "
                f"the steps above show what actually happens in sequence, "
                f"from the environmental trigger to the final outcome."
            )
        elif expertise == ExpertiseLevel.RESEARCHER:
            n_steps = len(result.causal_chain)
            lines.append(
                f"*Chain length: {n_steps} steps. "
                f"Confidence attenuates multiplicatively through the chain; "
                f"each mediation step adds epistemic uncertainty.*"
            )

        return "\n".join(lines)

    # ── Rendering helpers ──────────────────────────────────────────────────────

    def _belief_label(self, belief: Belief) -> str:
        """Short human label from a belief object."""
        return self._belief_label_from_id(belief.belief_id)

    # ── Human-readable short labels for mechanism + outcome nodes ─────
    _CLEAN_LABELS = {
        # Mechanism nodes with custom readable names
        "mechanism:srt:olfactory_safety_classification":
            "Olfactory safety classification (piriform cortex)",
        # Outcome nodes
        "outcome:srt:skin_conductance_reduction": "Skin conductance ↓ (GSR; fastest, 30–90 s)",
        "outcome:srt:heart_rate_reduction":       "Heart rate ↓ (2–5 min)",
        "outcome:srt:hrv_increase":               "Heart rate variability ↑ (HRV; most sensitive, 1–5 min)",
        "outcome:srt:blood_pressure_reduction":    "Blood pressure ↓ (5–15 min)",
        "outcome:srt:cortisol_reduction":          "Cortisol ↓ (slowest, 15–30 min)",
        "outcome:srt:respiratory_normalization":   "Respiratory rate ↓ & depth ↑ (1–5 min)",
        "outcome:art:working_memory_recovery":     "Working memory ↑ (n-back, digit span)",
        "outcome:art:inhibitory_control_recovery": "Inhibitory control ↑ (Stroop, go/no-go)",
        "outcome:art:sustained_attention_recovery":"Sustained attention ↑ (SART, CPT)",
        "outcome:subjective:calm":                "Subjective calm (PANAS, PRS)",
        "outcome:subjective:vitality":            "Subjective vitality ↑ (SVS)",
    }

    def _belief_label_from_id(self, belief_id: str) -> str:
        """Convert belief IDs to clean human-readable labels.

        mechanism:art:soft_fascination → 'Soft Fascination (ART)'
        outcome:srt:heart_rate_reduction → 'Heart rate ↓ (2–5 min)'
        stimulus:wood:visual → 'Wood — Visual Channel'
        """
        # Custom clean labels (mechanism + outcome nodes)
        if belief_id in self._CLEAN_LABELS:
            return self._CLEAN_LABELS[belief_id]

        if belief_id.startswith("mechanism:"):
            parts = belief_id.split(":")
            if len(parts) >= 3:
                theory = parts[1].upper()
                step = parts[2].replace("_", " ").title()
                return f"{step} ({theory})"

        if belief_id.startswith("outcome:"):
            parts = belief_id.split(":")
            if len(parts) >= 3:
                step = parts[2].replace("_", " ").title()
                return step

        if belief_id.startswith("stimulus:"):
            parts = belief_id.split(":")
            if len(parts) >= 3:
                material = parts[1].title()
                modality = parts[2].replace("_", " ").title()
                return f"{material} — {modality} Channel"

        # Fallback: use content snippet from beliefs dict
        belief = self.web.beliefs.get(belief_id)
        if belief:
            return belief.content[:60] + ("..." if len(belief.content) > 60 else "")
        return belief_id

    @staticmethod
    def _first_sentence(text: str) -> str:
        """Return first sentence of text."""
        for sep in ('. ', '! ', '? ', '\n'):
            idx = text.find(sep)
            if idx != -1 and idx < 200:
                return text[:idx + 1]
        return text[:180] + ("..." if len(text) > 180 else "")

    @staticmethod
    def _remaining_sentences(text: str) -> str:
        """Return everything after the first sentence."""
        for sep in ('. ', '! ', '? '):
            idx = text.find(sep)
            if idx != -1 and idx < 200:
                return text[idx + 2:].strip()
        return ""


# =============================================================================
# DISAGREEMENT PATTERN (per Cartwright: where do experts differ?)
# =============================================================================

@dataclass
class DisagreementPoint:
    """A point of disagreement in the literature."""
    topic: str
    position_a: str
    position_b: str
    belief_a_id: str
    belief_b_id: str
    disagreement_type: str  # "empirical", "theoretical", "methodological", "scope"
    resolution_status: str  # "unresolved", "trending_toward", "context_dependent"


@dataclass
class DisagreementResult:
    """Result of disagreement analysis."""
    target_belief: Belief
    disagreements: List[DisagreementPoint]
    consensus_areas: List[str]
    main_controversies: List[str]
    resolution_prospects: str


class DisagreementSummaryPattern:
    """
    Pattern: Where do experts differ?

    Per Cartwright: Highlight where scientific consensus breaks down.
    Useful for understanding the state of knowledge.
    """

    def __init__(self, web: WebOfBelief):
        self.web = web

    def traverse(self, belief_id: str) -> Optional[DisagreementResult]:
        """Find disagreements related to a belief."""
        if belief_id not in self.web.beliefs:
            return None

        target = self.web.beliefs[belief_id]
        disagreements = []
        consensus_areas = []

        # Find contradicting beliefs
        for constraint_id, constraint in self.web.constraints.items():
            if constraint.constraint_type != ConstraintType.CONTRADICTS:
                continue

            # Check if target is involved
            if constraint.source_id == belief_id or constraint.target_id == belief_id:
                other_id = constraint.target_id if constraint.source_id == belief_id else constraint.source_id
                other_belief = self.web.beliefs.get(other_id)
                if not other_belief:
                    continue

                disagreements.append(DisagreementPoint(
                    topic=self._extract_topic(target, other_belief),
                    position_a=target.content,
                    position_b=other_belief.content,
                    belief_a_id=target.belief_id,
                    belief_b_id=other_belief.belief_id,
                    disagreement_type=self._classify_disagreement(target, other_belief, constraint),
                    resolution_status=self._assess_resolution_status(target, other_belief),
                ))

        # Find supporting beliefs (areas of consensus)
        for constraint_id, constraint in self.web.constraints.items():
            if constraint.constraint_type == ConstraintType.SUPPORTS:
                if constraint.source_id == belief_id or constraint.target_id == belief_id:
                    other_id = constraint.target_id if constraint.source_id == belief_id else constraint.source_id
                    other_belief = self.web.beliefs.get(other_id)
                    if other_belief:
                        consensus_areas.append(other_belief.content[:80])

        # Identify main controversies
        main_controversies = self._identify_main_controversies(disagreements)

        # Assess resolution prospects
        resolution_prospects = self._assess_resolution_prospects(disagreements)

        return DisagreementResult(
            target_belief=target,
            disagreements=disagreements,
            consensus_areas=consensus_areas[:5],  # Limit to top 5
            main_controversies=main_controversies,
            resolution_prospects=resolution_prospects,
        )

    def _extract_topic(self, belief_a: Belief, belief_b: Belief) -> str:
        """Extract the topic of disagreement."""
        # Simple approach: find common words
        words_a = set(belief_a.content.lower().split())
        words_b = set(belief_b.content.lower().split())
        common = words_a & words_b
        # Filter stopwords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'and', 'or', 'in', 'on', 'to', 'of', 'for', 'that', 'this'}
        topic_words = [w for w in common if w not in stopwords and len(w) > 3]
        if topic_words:
            return " ".join(topic_words[:3])
        return "unspecified"

    def _classify_disagreement(
        self,
        belief_a: Belief,
        belief_b: Belief,
        constraint: Constraint
    ) -> str:
        """Classify the type of disagreement."""
        # Check constraint metadata if available
        if hasattr(constraint, 'disagreement_type'):
            return constraint.disagreement_type

        # Infer from belief levels
        if belief_a.level != belief_b.level:
            return "scope"

        # Check for methodological keywords
        content = (belief_a.content + belief_b.content).lower()
        if any(w in content for w in ['method', 'measure', 'sample', 'study design']):
            return "methodological"
        if any(w in content for w in ['theory', 'model', 'framework', 'hypothesis']):
            return "theoretical"

        return "empirical"

    def _assess_resolution_status(self, belief_a: Belief, belief_b: Belief) -> str:
        """Assess whether the disagreement is resolving."""
        # Check credence values
        cred_a = belief_a.credence.value
        cred_b = belief_b.credence.value

        if abs(cred_a - cred_b) > 0.3:
            if cred_a > cred_b:
                return f"trending_toward_a (credence: {cred_a:.0%} vs {cred_b:.0%})"
            else:
                return f"trending_toward_b (credence: {cred_b:.0%} vs {cred_a:.0%})"

        # Check uncertainty
        if belief_a.credence.uncertainty > 0.3 or belief_b.credence.uncertainty > 0.3:
            return "unresolved (high uncertainty)"

        return "context_dependent"

    def _identify_main_controversies(self, disagreements: List[DisagreementPoint]) -> List[str]:
        """Identify the main controversies."""
        if not disagreements:
            return ["No major controversies identified"]

        # Group by type
        by_type: Dict[str, List[DisagreementPoint]] = {}
        for d in disagreements:
            if d.disagreement_type not in by_type:
                by_type[d.disagreement_type] = []
            by_type[d.disagreement_type].append(d)

        controversies = []
        for dtype, points in by_type.items():
            if len(points) >= 2:
                controversies.append(f"Multiple {dtype} disagreements ({len(points)} points)")
            else:
                controversies.append(f"{dtype.title()} disagreement: {points[0].topic}")

        return controversies[:3]

    def _assess_resolution_prospects(self, disagreements: List[DisagreementPoint]) -> str:
        """Assess overall resolution prospects."""
        if not disagreements:
            return "No disagreements to resolve"

        unresolved = sum(1 for d in disagreements if "unresolved" in d.resolution_status)
        trending = sum(1 for d in disagreements if "trending" in d.resolution_status)

        if trending > unresolved:
            return "Good - evidence is converging"
        elif unresolved > len(disagreements) * 0.7:
            return "Uncertain - many open questions remain"
        else:
            return "Mixed - some areas converging, others still contested"

    def render(
        self,
        result: DisagreementResult,
        detail: DetailLevel,
        expertise: ExpertiseLevel
    ) -> str:
        """Render disagreement summary as text."""
        lines = []

        # Header
        target_summary = result.target_belief.content[:60] + "..." if len(result.target_belief.content) > 60 else result.target_belief.content
        lines.append(f"## Where Experts Disagree: {target_summary}")
        lines.append("")

        # Overview
        lines.append(f"**Disagreements Found:** {len(result.disagreements)}")
        lines.append(f"**Resolution Prospects:** {result.resolution_prospects}")
        lines.append("")

        # Main controversies
        if result.main_controversies:
            lines.append("### Main Controversies")
            for controversy in result.main_controversies:
                lines.append(f"- {controversy}")
            lines.append("")

        # Detailed disagreements
        if detail != DetailLevel.SUMMARY and result.disagreements:
            lines.append("### Specific Disagreements")
            for i, d in enumerate(result.disagreements, 1):
                lines.append(f"#### {i}. {d.topic.title()}")
                lines.append(f"**Type:** {d.disagreement_type}")
                lines.append(f"**Status:** {d.resolution_status}")
                if detail == DetailLevel.COMPREHENSIVE:
                    lines.append(f"- Position A: {d.position_a}")
                    lines.append(f"- Position B: {d.position_b}")
                lines.append("")

        # Areas of consensus
        if result.consensus_areas and detail != DetailLevel.SUMMARY:
            lines.append("### Areas of Consensus")
            lines.append("Experts generally agree on:")
            for area in result.consensus_areas:
                lines.append(f"- {area}")
            lines.append("")

        # Expertise-appropriate note
        if expertise == ExpertiseLevel.NOVICE:
            lines.append("### What This Means for Practice")
            if not result.disagreements:
                lines.append("There is strong consensus on this topic, so findings can be applied with confidence.")
            else:
                lines.append("Because experts disagree, consider multiple perspectives before making decisions.")
                lines.append("Focus on areas of consensus where possible.")

        return "\n".join(lines)


# =============================================================================
# GAP IDENTIFICATION (for TODO 3 integration)
# =============================================================================

class GapIdentifier:
    """
    Identify epistemic gaps during explanation.

    Per Phase D: Two types initially - uncertain and unexplored.
    """

    UNCERTAINTY_THRESHOLD = 0.3
    MIN_SUPPORTING_STUDIES = 3

    def identify_gaps(
        self,
        belief: Belief,
        evidence_result: Optional[EvidenceTraceResult] = None
    ) -> List[IdentifiedGap]:
        """Find gaps relevant to this belief."""
        gaps = []

        # High uncertainty
        if belief.credence.uncertainty > self.UNCERTAINTY_THRESHOLD:
            gaps.append(IdentifiedGap(
                gap_type="uncertain",
                description=f"High uncertainty ({belief.credence.uncertainty:.0%}) - need more evidence",
                belief_id=belief.belief_id,
                priority=belief.credence.uncertainty
            ))

        # Few supporting studies
        if evidence_result:
            n_supporting = len(evidence_result.supporting_evidence)
            if n_supporting < self.MIN_SUPPORTING_STUDIES:
                gaps.append(IdentifiedGap(
                    gap_type="unexplored",
                    description=f"Only {n_supporting} supporting studies - more research needed",
                    belief_id=belief.belief_id,
                    priority=0.5 / max(n_supporting, 1)
                ))

        return gaps


# =============================================================================
# MAIN INTERFACE
# =============================================================================

class InterpretiveEngine:
    """
    Main interface for interpretive intelligence.

    Coordinates patterns, vocabulary, and rendering.
    """

    def __init__(self, web: WebOfBelief, vocab_bridge: Optional[Any] = None):
        """
        Initialize engine.

        Args:
            web: The web of belief to explain
            vocab_bridge: Optional vocabulary bridge for term translation
        """
        self.web = web
        self.vocab = vocab_bridge
        self.classifier = QuestionClassifier()
        self.evidence_pattern = EvidenceTracePattern()
        self.practical_pattern = PracticalImplicationsPattern()
        self.mechanism_pattern = MechanismExplanationPattern(web)
        self.disagreement_pattern = DisagreementSummaryPattern(web)
        self.gap_identifier = GapIdentifier()

    def explain(
        self,
        request: ExplanationRequest
    ) -> ExplanationResponse:
        """
        Generate explanation using specified pattern.

        Args:
            request: The explanation request

        Returns:
            ExplanationResponse with explanation text and any identified gaps
        """
        belief_id = request.belief_id

        if belief_id not in self.web.beliefs:
            return ExplanationResponse(
                success=False,
                message=f"Belief not found: {belief_id}"
            )

        belief = self.web.beliefs[belief_id]

        try:
            # Get evidence (needed for both patterns)
            evidence_result = self.evidence_pattern.traverse(self.web, belief_id)

            # Generate pattern-specific explanation
            if request.pattern == ExplanationPattern.EVIDENCE:
                explanation = self.evidence_pattern.render(
                    evidence_result,
                    request.detail,
                    request.expertise
                )
                structured_data = evidence_result

            elif request.pattern == ExplanationPattern.PRACTICAL:
                practical_result = self.practical_pattern.traverse(
                    self.web,
                    belief_id,
                    evidence_result
                )
                explanation = self.practical_pattern.render(
                    practical_result,
                    request.detail,
                    request.expertise
                )
                structured_data = practical_result

            elif request.pattern == ExplanationPattern.MECHANISM:
                mechanism_result = self.mechanism_pattern.traverse(belief_id)
                if not mechanism_result:
                    return ExplanationResponse(
                        success=False,
                        message=f"Could not trace mechanism for: {belief_id}"
                    )
                explanation = self.mechanism_pattern.render(
                    mechanism_result,
                    request.detail,
                    request.expertise
                )
                structured_data = mechanism_result

            elif request.pattern == ExplanationPattern.DISAGREEMENT:
                disagreement_result = self.disagreement_pattern.traverse(belief_id)
                if not disagreement_result:
                    return ExplanationResponse(
                        success=False,
                        message=f"Could not analyze disagreements for: {belief_id}"
                    )
                explanation = self.disagreement_pattern.render(
                    disagreement_result,
                    request.detail,
                    request.expertise
                )
                structured_data = disagreement_result

            else:
                return ExplanationResponse(
                    success=False,
                    message=f"Unknown pattern: {request.pattern}"
                )

            # Identify gaps (for TODO 3)
            gaps = self.gap_identifier.identify_gaps(belief, evidence_result)

            return ExplanationResponse(
                success=True,
                explanation=explanation,
                pattern=request.pattern,
                detail=request.detail,
                identified_gaps=gaps,
                structured_data=structured_data
            )

        except Exception as e:
            logger.error(f"Explanation failed for {belief_id}: {e}", exc_info=True)
            return ExplanationResponse(
                success=False,
                message=f"Error generating explanation: {str(e)}"
            )

    def answer_question(
        self,
        question: str,
        detail: DetailLevel = DetailLevel.STANDARD,
        expertise: ExpertiseLevel = ExpertiseLevel.PRACTITIONER
    ) -> Union[ExplanationResponse, ClarifyingQuestion]:
        """
        Answer a natural language question.

        For mechanism/WHY queries: traverses ALL relevant mechanism: entry beliefs
        and merges their chains, so e.g. "why is wood restorative?" shows both the
        ART cognitive chain and the SRT visual→amygdala→HPA physiological chain.

        Per Wilson: Achieve cognitive effect with minimal processing effort.
        """
        # Classify question
        classification = self.classifier.classify_or_clarify(question)
        if isinstance(classification, ClarifyingQuestion):
            return classification

        pattern = classification

        # Find relevant beliefs
        belief_ids = self._find_relevant_beliefs(question)
        if not belief_ids:
            return ExplanationResponse(
                success=False,
                message="I couldn't find relevant information for your question. "
                       "Try rephrasing or asking about a specific topic."
            )

        # Detect mechanism query: if multiple mechanism: nodes found, traverse all
        mechanism_ids = [b for b in belief_ids if b.startswith("mechanism:")]

        if len(mechanism_ids) >= 2:
            # Prune: remove any entry that is already reachable (downstream) of another
            # entry in the same candidate set — it will appear as a step in the root
            # chain and doesn't need its own traversal.
            root_ids = self._prune_to_roots(mechanism_ids)
            return self._answer_multi_chain(
                question, root_ids, pattern, detail, expertise
            )

        # Single belief path (non-mechanism or single entry)
        request = ExplanationRequest(
            pattern=pattern,
            belief_id=belief_ids[0],
            detail=detail,
            expertise=expertise
        )
        return self.explain(request)
    def _answer_multi_chain(
        self,
        question: str,
        entry_ids: List[str],
        pattern: ExplanationPattern,
        detail: DetailLevel,
        expertise: ExpertiseLevel,
    ) -> ExplanationResponse:
        """
        Traverse multiple mechanism entry nodes and produce a HUMAN-READABLE
        conditional narrative grouped by encounter mode.

        Output reads like:
          "There are three complementary explanations that depend in part on
           how a subject encounters wood.
           If they only see it — just the grain and colour — ...
           If they also smell it (the wood still gives off its woody scent) — ...
           If they touch it, running their hand along the railing — ..."
        """
        from src.services.interpretive_intelligence import (
            MechanismExplanationPattern, MechanismResult,
        )
        mech_pattern = MechanismExplanationPattern(self.web)

        # Traverse all entry points
        results: List[MechanismResult] = []
        for eid in entry_ids[:5]:
            r = mech_pattern.traverse(eid)
            if r and (r.causal_chain or r.mediators):
                results.append(r)

        if not results:
            return ExplanationResponse(
                success=False,
                message="Mechanism beliefs found but no traversable chains. "
                        "Seed more mechanism nodes to extend the chain."
            )

        # ── Classify each chain by encounter modality ────────────────────────
        # Look for stimulus: nodes feeding into each entry to determine modality
        encounter_chains = []
        for result in results:
            entry_id = result.target_belief.belief_id
            # Find any stimulus: node that feeds this entry
            modality, condition = self._infer_encounter_mode(entry_id)
            encounter_chains.append((modality, condition, result))

        # Deduplicate: if two chains share a modality, keep first
        seen_modalities: set = set()
        unique_chains = []
        for modality, condition, result in encounter_chains:
            if modality not in seen_modalities:
                unique_chains.append((modality, condition, result))
                seen_modalities.add(modality)

        # Sort by sensory priority: visual first (most common encounter),
        # then olfactory, haptic, acoustic, kinesthetic, then everything else
        MODALITY_ORDER = {
            "seeing it": 0, "seeing it up close": 1,
            "visual (attention pathway)": 0,
            "smelling it": 2,
            "touching it": 3, "multi-sensory (material pathway)": 3,
            "being in a noisy space with it": 4,
            "moving through it": 5,
        }
        unique_chains.sort(key=lambda x: MODALITY_ORDER.get(x[0], 99))

        # ── Build narrative ──────────────────────────────────────────────────
        lines = []
        q_clean = question.strip("?!. ").lower()

        # Extract the material from the query
        material = "this"
        for word in ("wood", "plants", "water", "stone", "daylight", "light", "nature"):
            if word in q_clean:
                material = word
                break

        n = len(unique_chains)
        lines.append(f"## {question.strip('?!').strip().title()}")
        lines.append("")
        lines.append(
            f"There are **{n} complementary explanation{'s' if n > 1 else ''}** "
            f"that depend in part on how a subject encounters {material}. "
            f"These operate simultaneously when multiple senses are engaged — "
            f"they are additive, not alternative."
        )
        lines.append("")

        seen_node_ids: set = set()

        for i, (modality, condition, result) in enumerate(unique_chains):
            # ── Encounter header ─────────────────────────────────────────────
            header = self._narrative_header(modality, condition, material, i, n)
            lines.append(f"---")
            lines.append(f"### {header}")
            lines.append("")

            # ── Walk the chain as narrative prose ────────────────────────────
            entry = result.target_belief
            entry_sent = mech_pattern._first_sentence(entry.content)

            # Opening sentence
            theory = entry.belief_id.split(":")[1].upper() if ":" in entry.belief_id else ""
            lines.append(
                f"This triggers the **{theory}** pathway. "
                f"{entry_sent}"
            )
            lines.append("")

            # Walk the chain steps as numbered prose with progressive disclosure
            step_lines = []
            for j, step in enumerate(result.causal_chain):
                if step.belief_id in seen_node_ids:
                    label = mech_pattern._belief_label_from_id(step.belief_id)
                    step_lines.append(
                        f"From here, the pathway converges with the route "
                        f"described above (→ *{label}*) and follows the same "
                        f"downstream chain."
                    )
                    break

                label = mech_pattern._belief_label_from_id(step.belief_id)
                first_sent = mech_pattern._first_sentence(step.content)
                remaining = mech_pattern._remaining_sentences(step.content)

                # Summary line (always visible)
                step_lines.append(f"{j + 1}. **{label}** — {first_sent}")

                # Progressive disclosure: expandable deeper explanation
                if detail != DetailLevel.SUMMARY and remaining:
                    step_lines.append(f"<details>")
                    step_lines.append(f"<summary>Why? (click to expand)</summary>")
                    step_lines.append(f"")
                    step_lines.append(f"{remaining}")
                    step_lines.append(f"")
                    step_lines.append(f"</details>")
                    step_lines.append(f"")

                seen_node_ids.add(step.belief_id)

            if step_lines:
                lines.extend(step_lines)
                lines.append("")

            # Outcome summary for this chain
            outcomes = [s for s in result.causal_chain
                        if s.belief_id.startswith("outcome:")]
            if outcomes and detail != DetailLevel.SUMMARY:
                lines.append("**Measurable outcomes:**")
                for out in outcomes:
                    label = mech_pattern._belief_label_from_id(out.belief_id)
                    mediator = getattr(out, '_mediator_desc', None)
                    if mediator:
                        lines.append(f"- {label} ({mediator})")
                    else:
                        lines.append(f"- {label}")
                lines.append("")

            seen_node_ids.add(entry.belief_id)

        # ── Closing summary ──────────────────────────────────────────────────
        if n > 1:
            lines.append("---")
            lines.append("### Combined Effect")
            lines.append("")
            lines.append(
                f"When multiple channels are active simultaneously "
                f"(e.g., seeing *and* smelling {material}), "
                f"the pathways above reinforce each other. The combined effect is "
                f"larger than any single channel alone — this convergent benefit "
                f"is why real {material} outperforms photographs or synthetic imitations "
                f"matched on any single sensory dimension."
            )
            lines.append("")

        if expertise == ExpertiseLevel.RESEARCHER:
            lines.append(
                f"*Technical: {len(entry_ids)} mechanism entry nodes scored; "
                f"{len(results)} traversable chains found; "
                f"{n} distinct encounter modalities rendered.*"
            )

        return ExplanationResponse(
            success=True,
            explanation="\n".join(lines),
        )

    def _infer_encounter_mode(self, mechanism_entry_id: str) -> tuple:
        """
        Given a mechanism: entry node ID, look for stimulus: nodes that
        feed into it via SUPPORTS constraints, and infer the encounter
        modality + condition from the stimulus node's tags/mediator.

        Returns (modality: str, condition: str)
        """
        MODALITY_MAP = {
            "visual": ("seeing it", "just looking at the grain and colour"),
            "fractal_visual": ("seeing it up close", "close enough to see the grain texture"),
            "olfactory": ("smelling it", "the wood still gives off its woody scent"),
            "haptic": ("touching it", "running a hand along the surface, like a wooden railing"),
            "acoustic": ("being in a noisy space with it", "wood surfaces absorb sound, reducing distraction"),
            "kinesthetic": ("moving through it", "walking on wood floors or past wood panels"),
        }

        # Check if the entry ID itself hints at modality
        eid_lower = mechanism_entry_id.lower()
        if "olfact" in eid_lower or "smell" in eid_lower:
            return MODALITY_MAP.get("olfactory", ("olfactory", ""))
        if "visual" in eid_lower or "ecological_appraisal" in eid_lower:
            return MODALITY_MAP.get("visual", ("visual", ""))

        # Search for stimulus: → this entry constraints
        for c in self.web.constraints.values():
            if c.target_id == mechanism_entry_id and c.source_id.startswith("stimulus:"):
                parts = c.source_id.split(":")
                if len(parts) >= 3:
                    modality = parts[2]  # stimulus:wood:visual → "visual"
                    if modality in MODALITY_MAP:
                        return MODALITY_MAP[modality]

        # Infer from the mechanism family
        if ":art:" in eid_lower:
            return ("visual (attention pathway)", "the environment captures involuntary attention")
        if ":srt:" in eid_lower:
            return ("visual/olfactory (stress pathway)", "the scene signals ecological safety")
        if ":mat4:" in eid_lower:
            return ("multi-sensory (material pathway)", "seeing, touching, and/or smelling the material")
        if ":dt1:" in eid_lower:
            return ("environmental (distraction pathway)", "the environment reduces false alarms")

        return ("sensory", "encountering the stimulus")

    def _narrative_header(
        self, modality: str, condition: str, material: str, index: int, total: int
    ) -> str:
        """Generate a human-readable section header for one encounter mode."""
        if index == 0:
            prefix = f"If they are only **{modality}**"
        elif index == total - 1:
            prefix = f"And if they are also **{modality}**"
        else:
            prefix = f"If they are also **{modality}**"

        if condition:
            return f"{prefix} — *{condition}*"
        return prefix

    def _prune_to_roots(self, candidate_ids: List[str]) -> List[str]:
        """
        Given a list of mechanism: belief IDs, remove any that are already
        reachable (downstream) from another candidate via MEDIATION/SUPPORTS.

        A 'root' is a node from which traversal begins fresh — not a node that
        will inevitably be visited as a step inside another chain.

        Example: given [biophilic_stimulus, soft_fascination], soft_fascination
        is downstream of biophilic_stimulus so is pruned. Only biophilic_stimulus
        is traversed; soft_fascination appears naturally as STEP 1.
        """
        FORWARD_TYPES = {
            ConstraintType.EPISTEMIC_MEDIATION,
            ConstraintType.SUPPORTS,
            ConstraintType.PROPOSES_MECHANISM,
        }
        candidate_set = set(candidate_ids)

        # Build reachability: for each candidate, which other candidates can it reach?
        reachable_from: Dict[str, set] = {cid: set() for cid in candidate_ids}

        for start in candidate_ids:
            visited: set = set()
            queue = [start]
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                for c in self.web.constraints.values():
                    if c.source_id == node and c.constraint_type in FORWARD_TYPES:
                        if c.target_id in candidate_set and c.target_id != start:
                            reachable_from[start].add(c.target_id)
                        if c.target_id not in visited:
                            queue.append(c.target_id)

        # Remove any candidate that is reachable from another candidate
        dominated = set()
        for cid in candidate_ids:
            dominated |= reachable_from[cid]

        roots = [cid for cid in candidate_ids if cid not in dominated]
        return roots if roots else candidate_ids[:2]  # safety fallback

    def _find_relevant_beliefs(self, question: str) -> List[str]:
        """
        Find beliefs related to question terms.

        For mechanism/WHY queries, prefer `mechanism:` belief nodes over raw
        PDF extracts, since those nodes represent the actual causal steps the
        MechanismPattern can traverse.
        """
        q_lower = question.lower()

        # Detect if this is a mechanism/WHY/HOW query
        is_mechanism_query = any(
            kw in q_lower
            for kw in (
                "mechanism", "why is", "why are", "why does", "why do",
                "how does", "how do", "what causes", "what explains",
                "same route", "same pathway", "restorative", "restoration",
            )
        )

        stopwords = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'to', 'of', 'in', 'for', 'on', 'with', 'that', 'this', 'it',
            'what', 'why', 'how', 'does', 'do', 'same', 'which',
        }
        q_words = set(q_lower.split()) - stopwords

        relevant = []

        for belief_id, belief in self.web.beliefs.items():
            content_lower = belief.content.lower()
            id_lower = belief_id.lower()

            # Score: word overlap in content
            content_words = set(content_lower.split()) - stopwords
            overlap = len(q_words & content_words)

            # Also check tags
            tag_overlap = sum(
                1 for t in belief.tags if any(w in t.lower() for w in q_words)
            )
            score = overlap + tag_overlap * 0.5

            # Strong boost for mechanism: nodes in mechanism queries
            if is_mechanism_query and belief_id.startswith("mechanism:"):
                # Extra boost for nodes whose ID words match query words
                id_words = set(id_lower.replace(":", " ").replace("_", " ").split())
                id_match = len(q_words & id_words)
                score += 10 + id_match * 2

            # Moderate penalty for raw PDF table rows (poor candidate for traversal)
            if belief_id.startswith("pdf:") and "-TBL-" in belief_id:
                score *= 0.3

            if score >= 1.5:
                relevant.append((belief_id, score))

        relevant.sort(key=lambda x: -x[1])
        return [bid for bid, _ in relevant[:5]]

    def explain_credibility_decision(
        self,
        report: Any,  # CredibilityReport from TODO 1
        detail: DetailLevel = DetailLevel.STANDARD
    ) -> str:
        """
        Explain why a paper was flagged (integration with TODO 1).

        Args:
            report: CredibilityReport from credibility testing
            detail: Detail level for explanation

        Returns:
            Human-readable explanation of credibility decision
        """
        context = report.to_explanation_context()

        if detail == DetailLevel.SUMMARY:
            return f"This paper was **{context['decision']}** due to {context['n_flags']} concerns: " + \
                   ", ".join(context['reasons'][:2])

        elif detail == DetailLevel.STANDARD:
            lines = [f"## Credibility Assessment: {context['decision'].upper()}"]
            lines.append("")
            lines.append(f"{context['n_flags']} concerns were identified:")
            lines.append("")
            for i, reason in enumerate(context['reasons'], 1):
                lines.append(f"{i}. {reason}")
            return "\n".join(lines)

        else:  # COMPREHENSIVE
            lines = [f"## Comprehensive Credibility Assessment: {context['decision'].upper()}"]
            lines.append("")
            lines.append(f"**Article:** {context['article_id']}")
            lines.append(f"**Total Concerns:** {context['n_flags']}")
            lines.append("")
            lines.append("### Detailed Concerns")
            lines.append("")
            for i, reason in enumerate(context['reasons'], 1):
                lines.append(f"#### Concern {i}")
                lines.append(reason)
                lines.append("")
            return "\n".join(lines)


# =============================================================================
# SPRINT F: CREDIBILITY EXPLAINER (Enhanced TODO 1 Integration)
# =============================================================================

@dataclass
class FlagExplanation:
    """Detailed explanation of a single credibility flag."""
    flag_type: str
    severity: str  # "critical" or "warning"
    explanation: str
    recommendation: str
    technical_detail: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'flag_type': self.flag_type,
            'severity': self.severity,
            'explanation': self.explanation,
            'recommendation': self.recommendation,
            'technical_detail': self.technical_detail,
        }


class CredibilityExplainer:
    """
    Enhanced credibility explanation for TODO 1 integration.

    Sprint F: Provides detailed, human-readable explanations of
    credibility flags with recommendations.
    """

    # Human-readable explanations for flag types
    FLAG_EXPLANATIONS = {
        "credence": {
            "explanation": "The stated confidence level is outside the valid range (must be between 0 and 1, exclusive).",
            "recommendation": "Check the original paper for the actual confidence level reported.",
            "severity": "critical"
        },
        "sample_size": {
            "explanation": "The sample size reported is invalid (must be a positive number).",
            "recommendation": "Verify the sample size from the original paper.",
            "severity": "critical"
        },
        "p_value": {
            "explanation": "The p-value reported is outside the valid range (must be between 0 and 1).",
            "recommendation": "Check the statistical analysis section of the original paper.",
            "severity": "critical"
        },
        "self_contradiction": {
            "explanation": "The paper appears to contain contradictory claims.",
            "recommendation": "Review the paper for potentially conflicting findings or extraction errors.",
            "severity": "critical"
        },
        "causal_direction": {
            "explanation": "The causal claim made is stronger than the study design can support.",
            "recommendation": "Consider weakening the causal language or noting the study design limitations.",
            "severity": "warning"
        },
        "scope": {
            "explanation": "The claimed scope of findings may extend beyond what the sample can support.",
            "recommendation": "Consider limiting claims to the specific population studied.",
            "severity": "warning"
        },
        "effect_size": {
            "explanation": "The effect size reported seems unusually large for this type of study.",
            "recommendation": "Verify the effect size calculation and consider replication evidence.",
            "severity": "warning"
        },
        "causal_cycle": {
            "explanation": "The causal relationships form a cycle, which may indicate feedback loops or extraction errors.",
            "recommendation": "Review whether this represents a genuine feedback mechanism.",
            "severity": "warning"
        },
        "confidence_interval": {
            "explanation": "The confidence interval spans zero, suggesting the effect may not be statistically reliable.",
            "recommendation": "Exercise caution in drawing conclusions from this finding.",
            "severity": "warning"
        },
        "multiple_comparison": {
            "explanation": "Multiple statistical tests were performed without correction, increasing false positive risk.",
            "recommendation": "Look for corrected analyses or treat findings as preliminary.",
            "severity": "warning"
        },
        "sample_description": {
            "explanation": "The study lacks adequate description of the sample population.",
            "recommendation": "Consider the generalizability limitations due to unknown sample characteristics.",
            "severity": "warning"
        },
        "subgroup_sample_size": {
            "explanation": "The claim targets a subgroup with a small sample size.",
            "recommendation": "Treat subgroup findings as preliminary until replicated with larger samples.",
            "severity": "warning"
        },
    }

    def explain_report(
        self,
        report: Any,  # CredibilityReport
        detail: DetailLevel = DetailLevel.STANDARD,
        expertise: ExpertiseLevel = ExpertiseLevel.PRACTITIONER
    ) -> str:
        """
        Generate comprehensive explanation of a credibility report.

        Args:
            report: CredibilityReport from credibility testing
            detail: How much detail to include
            expertise: User's expertise level

        Returns:
            Human-readable explanation
        """
        if report.is_clean:
            return self._render_clean_report(report, expertise)

        explanations = []
        for flag in report.flags:
            explanations.append(self._explain_flag(flag, expertise))

        return self._render_report(report, explanations, detail, expertise)

    def _explain_flag(
        self,
        flag: Any,  # CredibilityFlag
        expertise: ExpertiseLevel
    ) -> FlagExplanation:
        """Generate detailed explanation for a single flag."""
        flag_type = flag.field_name or "unknown"
        template = self.FLAG_EXPLANATIONS.get(flag_type, {
            "explanation": flag.reason,
            "recommendation": "Review the original source.",
            "severity": "warning"
        })

        # Adjust language for expertise level
        explanation = template["explanation"]
        if expertise == ExpertiseLevel.NOVICE:
            explanation = self._simplify_for_novice(explanation)

        technical_detail = None
        if expertise == ExpertiseLevel.RESEARCHER and flag.expected and flag.observed:
            technical_detail = f"Expected: {flag.expected}, Observed: {flag.observed}"

        return FlagExplanation(
            flag_type=flag_type,
            severity="critical" if flag.decision.value == "block" else "warning",
            explanation=explanation,
            recommendation=template["recommendation"],
            technical_detail=technical_detail
        )

    def _simplify_for_novice(self, text: str) -> str:
        """Simplify technical language for novice users."""
        replacements = {
            "p-value": "statistical significance measure",
            "confidence interval": "range of likely values",
            "effect size": "strength of the effect",
            "causal": "cause-and-effect",
            "statistical": "mathematical",
            "replication": "repeated studies",
        }
        result = text
        for technical, simple in replacements.items():
            result = result.replace(technical, simple)
        return result

    def _render_clean_report(self, report: Any, expertise: ExpertiseLevel) -> str:
        """Render explanation for a clean report."""
        if expertise == ExpertiseLevel.NOVICE:
            return f"**Good news!** This paper ({report.article_id}) passed all quality checks. " \
                   "The findings appear to be well-supported by the methodology."
        else:
            return f"**Credibility Assessment: ACCEPT**\n\n" \
                   f"Paper: {report.article_id}\n" \
                   "No credibility concerns identified. All checks passed."

    def _render_report(
        self,
        report: Any,
        explanations: List[FlagExplanation],
        detail: DetailLevel,
        expertise: ExpertiseLevel
    ) -> str:
        """Render full explanation for a flagged report."""
        lines = []

        # Header
        decision = report.overall_decision.value.upper()
        if expertise == ExpertiseLevel.NOVICE:
            if decision == "BLOCK":
                lines.append("**Caution Required!** This paper has significant quality concerns.")
            else:
                lines.append("**Review Recommended!** This paper has some quality concerns to consider.")
        else:
            lines.append(f"## Credibility Assessment: {decision}")

        lines.append("")
        lines.append(f"**Paper:** {report.article_id}")
        lines.append(f"**Concerns:** {len(report.flags)}")
        lines.append("")

        # Critical issues first
        critical = [e for e in explanations if e.severity == "critical"]
        warnings = [e for e in explanations if e.severity == "warning"]

        if critical:
            lines.append("### Critical Issues")
            lines.append("")
            for exp in critical:
                lines.extend(self._render_flag_explanation(exp, detail, expertise))
            lines.append("")

        if warnings and detail != DetailLevel.SUMMARY:
            lines.append("### Warnings")
            lines.append("")
            for exp in warnings:
                lines.extend(self._render_flag_explanation(exp, detail, expertise))
            lines.append("")

        # Overall recommendation
        lines.append("### Recommendation")
        lines.append("")
        if decision == "BLOCK":
            lines.append("This paper should not be automatically processed. "
                        "Manual review is required to address the critical issues above.")
        else:
            lines.append("This paper can be processed, but the concerns above "
                        "should be considered when interpreting the findings.")

        return "\n".join(lines)

    def _render_flag_explanation(
        self,
        exp: FlagExplanation,
        detail: DetailLevel,
        expertise: ExpertiseLevel
    ) -> List[str]:
        """Render a single flag explanation."""
        lines = []
        lines.append(f"**{exp.flag_type.replace('_', ' ').title()}**")
        lines.append(f"- {exp.explanation}")

        if detail != DetailLevel.SUMMARY:
            lines.append(f"- *Recommendation:* {exp.recommendation}")

        if detail == DetailLevel.COMPREHENSIVE and exp.technical_detail:
            lines.append(f"- *Technical:* {exp.technical_detail}")

        lines.append("")
        return lines


# =============================================================================
# SPRINT F: SEARCH CONTEXT (for TODO 3 Integration)
# =============================================================================

@dataclass
class SearchContext:
    """
    Context for TODO 3 VOI-driven search.

    Contains information about what to search for and why.
    """
    gap: IdentifiedGap
    search_queries: List[str]
    target_study_types: List[str]
    priority_score: float
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'gap': self.gap.to_dict(),
            'search_queries': self.search_queries,
            'target_study_types': self.target_study_types,
            'priority_score': self.priority_score,
            'rationale': self.rationale,
        }


class SearchContextGenerator:
    """
    Generate search contexts for identified gaps.

    Sprint F: Prepares gaps for TODO 3 VOI-driven search.
    """

    def generate_search_context(
        self,
        gap: IdentifiedGap,
        belief: Optional[Belief] = None
    ) -> SearchContext:
        """
        Generate search context for a gap.

        Args:
            gap: The identified gap
            belief: Optional belief associated with the gap

        Returns:
            SearchContext with search queries and priorities
        """
        queries = []
        target_studies = []
        rationale = ""

        if gap.gap_type == "uncertain":
            # Need more evidence for existing belief
            if belief:
                content_keywords = self._extract_keywords(belief.content)
                queries = [
                    f"{' '.join(content_keywords[:3])} meta-analysis",
                    f"{' '.join(content_keywords[:3])} systematic review",
                    f"{' '.join(content_keywords[:3])} replication",
                ]
                target_studies = ["meta-analysis", "systematic_review", "rct"]
                rationale = f"High uncertainty ({gap.priority:.0%}) on existing belief. " \
                           "Prioritize high-quality synthesis studies."

        elif gap.gap_type == "unexplored":
            # Topic area with sparse coverage
            if belief:
                content_keywords = self._extract_keywords(belief.content)
                queries = [
                    f"{' '.join(content_keywords[:3])} empirical study",
                    f"{' '.join(content_keywords[:3])} experiment",
                    f"{' '.join(content_keywords[:2])} {content_keywords[-1] if len(content_keywords) > 2 else ''}",
                ]
                target_studies = ["experiment", "longitudinal", "observational"]
                rationale = "Sparse evidence coverage. Prioritize primary studies."

        return SearchContext(
            gap=gap,
            search_queries=queries,
            target_study_types=target_studies,
            priority_score=gap.priority,
            rationale=rationale
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for search queries."""
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                    'to', 'of', 'in', 'for', 'on', 'with', 'that', 'this', 'it',
                    'and', 'or', 'but', 'can', 'may', 'will', 'would', 'could',
                    'should', 'have', 'has', 'had', 'do', 'does', 'did'}

        words = text.lower().split()
        keywords = [w.strip('.,;:!?()[]') for w in words if w not in stopwords and len(w) > 2]
        return keywords[:5]  # Top 5 keywords

    def prioritize_gaps(self, gaps: List[IdentifiedGap]) -> List[IdentifiedGap]:
        """
        Prioritize gaps for search.

        Returns gaps sorted by priority (highest first).
        """
        return sorted(gaps, key=lambda g: g.priority, reverse=True)


# =============================================================================
# SPRINT F: PIPELINE INTEGRATION
# =============================================================================

def explain_article_assessment(
    report: Any,  # CredibilityReport
    detail: DetailLevel = DetailLevel.STANDARD,
    expertise: ExpertiseLevel = ExpertiseLevel.PRACTITIONER
) -> str:
    """
    Pipeline helper: Generate explanation for article credibility assessment.

    Args:
        report: CredibilityReport from credibility testing
        detail: Detail level for explanation
        expertise: User's expertise level

    Returns:
        Human-readable explanation
    """
    explainer = CredibilityExplainer()
    return explainer.explain_report(report, detail, expertise)


def generate_search_contexts(
    gaps: List[IdentifiedGap],
    beliefs: Optional[Dict[str, Belief]] = None
) -> List[SearchContext]:
    """
    Pipeline helper: Generate search contexts for identified gaps.

    Args:
        gaps: List of identified gaps
        beliefs: Optional dict of belief_id -> Belief

    Returns:
        List of SearchContext objects for TODO 3
    """
    generator = SearchContextGenerator()
    contexts = []

    for gap in generator.prioritize_gaps(gaps):
        belief = beliefs.get(gap.belief_id) if beliefs else None
        context = generator.generate_search_context(gap, belief)
        contexts.append(context)

    return contexts


def export_gaps_for_search(
    gaps: List[IdentifiedGap],
    beliefs: Optional[Dict[str, Belief]] = None,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Pipeline helper: Export gaps as search contexts for TODO 3.

    Args:
        gaps: List of identified gaps
        beliefs: Optional dict of belief_id -> Belief
        output_path: Optional path to write JSON output

    Returns:
        Dict with search contexts
    """
    contexts = generate_search_contexts(gaps, beliefs)

    result = {
        'n_gaps': len(gaps),
        'n_search_contexts': len(contexts),
        'search_contexts': [c.to_dict() for c in contexts],
    }

    if output_path:
        import json
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

    return result


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_engine(web: WebOfBelief, vocab_path: Optional[str] = None) -> InterpretiveEngine:
    """Create an interpretive engine instance."""
    vocab = None
    if vocab_path:
        # Will load vocabulary bridge when implemented
        pass
    return InterpretiveEngine(web, vocab)


def quick_explain(
    web: WebOfBelief,
    belief_id: str,
    pattern: ExplanationPattern = ExplanationPattern.EVIDENCE
) -> str:
    """
    Quick explanation without full engine setup.

    Returns explanation text or error message.
    """
    engine = InterpretiveEngine(web)
    request = ExplanationRequest(
        pattern=pattern,
        belief_id=belief_id,
        detail=DetailLevel.SUMMARY,
        expertise=ExpertiseLevel.PRACTITIONER
    )
    response = engine.explain(request)
    return response.explanation if response.success else response.message or "Error"


# =============================================================================
# TODO 3 HANDOFF (Sprint G)
# =============================================================================
"""
TODO 3 Handoff Summary: VOI-Driven Search

This module provides the foundation for TODO 3 through:

1. Gap Identification (GapIdentifier class)
   - Identifies UNCERTAIN gaps (high credence uncertainty)
   - Identifies UNEXPLORED gaps (few supporting studies)
   - Returns prioritized IdentifiedGap objects

2. Search Context Generation (SearchContextGenerator class)
   - Converts IdentifiedGap -> SearchContext
   - Generates search queries based on gap type
   - Specifies target study types (RCT, longitudinal, etc.)
   - Calculates priority scores

3. Pipeline Integration Functions
   - generate_search_contexts(gaps, beliefs) -> List[SearchContext]
   - export_gaps_for_search(gaps, beliefs, path) -> JSON output

4. Data Flow for TODO 3:

   InterpretiveEngine.explain()
       |
       v
   GapIdentifier.identify_gaps()
       |
       v
   SearchContextGenerator.generate_search_context()
       |
       v
   SearchContext (contains: queries, study_types, priority, rationale)
       |
       v
   TODO 3: VOI-Driven Search

5. Key Classes for TODO 3 Integration:
   - IdentifiedGap: gap_type, description, belief_id, priority
   - SearchContext: gap, search_queries, target_study_types, priority_score, rationale

6. Extension Points:
   - Add new gap types to GapIdentifier (CAUSAL, SCOPE per Phase D)
   - Add VOI scoring to SearchContextGenerator
   - Implement source selection (per Giles) in TODO 3

See: docs/implementation_plans/PHASE_D_REVISED_PLANS_2026_01_20.md
"""
