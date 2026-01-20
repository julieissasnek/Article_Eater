"""
Interpretive Intelligence for Article Eater Post-Quinean.

Phase E: Implementation (Sprint E)
TODO 2: Interpretive Intelligence

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
    Two patterns initially (per Lampson).

    Start simple, add more only when these can't answer common questions.
    """
    EVIDENCE = "evidence"      # What supports this belief?
    PRACTICAL = "practical"    # What should I do with this?


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
                    ("Design recommendations (what to do)", ExplanationPattern.PRACTICAL)
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
        """Render practical implications to natural language."""
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

        Per Wilson: Achieve cognitive effect with minimal processing effort.

        Args:
            question: Natural language question
            detail: How much detail to include
            expertise: User's expertise level

        Returns:
            ExplanationResponse if successful, or ClarifyingQuestion if uncertain
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

        # Generate explanation for first matching belief
        request = ExplanationRequest(
            pattern=pattern,
            belief_id=belief_ids[0],
            detail=detail,
            expertise=expertise
        )

        return self.explain(request)

    def _find_relevant_beliefs(self, question: str) -> List[str]:
        """
        Find beliefs related to question terms.

        Uses vocabulary bridge if available, otherwise simple keyword matching.
        """
        q_lower = question.lower()
        relevant = []

        # Use vocabulary bridge if available
        if self.vocab:
            # Will be implemented in vocabulary_bridge.py
            pass

        # Simple keyword matching fallback
        for belief_id, belief in self.web.beliefs.items():
            content_lower = belief.content.lower()

            # Check for word overlap
            q_words = set(q_lower.split())
            content_words = set(content_lower.split())

            # Remove common words
            stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                        'to', 'of', 'in', 'for', 'on', 'with', 'that', 'this', 'it'}
            q_words -= stopwords
            content_words -= stopwords

            overlap = len(q_words & content_words)
            if overlap >= 2:  # At least 2 non-stopword matches
                relevant.append((belief_id, overlap))

        # Sort by overlap count
        relevant.sort(key=lambda x: x[1], reverse=True)

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
