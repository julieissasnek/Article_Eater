"""
Query Response Generator
========================

Generates structured responses to parsed queries.

Per expert panel:
- Exactly 3 follow-ups: deeper, broader, uncertainty (Simon, Q2)
- Abstract-only caution badges (Cartwright, I3)
- Show vocabulary expansion transparently (Bates, Q3)

Date: January 21, 2026
Phase C Sprint C2
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from src.services.query_parser import QueryIntent, QueryType, ParseResult
from src.services.web_of_belief import (
    WebOfBelief, Belief, SourceDepth, EpistemicLevel
)
from src.services.stability_engine import StabilityEngine


# =============================================================================
# Response Models
# =============================================================================

class ResponseType(Enum):
    """Type of response generated."""
    DIRECT_ANSWER = "direct_answer"      # Clear answer to factual query
    SUMMARY = "summary"                   # Summary of multiple beliefs
    COMPARISON = "comparison"             # Comparison of options
    CONFIDENCE_REPORT = "confidence"      # Confidence assessment
    EVIDENCE_LIST = "evidence_list"       # List of supporting evidence
    GAP_REPORT = "gap_report"            # What we don't know
    SCOPE_REPORT = "scope_report"        # When/for whom something works
    CLARIFICATION_NEEDED = "clarification" # Need more info


@dataclass
class EvidenceItem:
    """Single piece of evidence."""
    belief_id: str
    content: str
    credence: float
    source_depth: str  # full_text, abstract, metadata
    paper_ids: List[str]
    is_causal: bool
    needs_caution: bool  # True if abstract-only causal claim

    def to_dict(self) -> Dict[str, Any]:
        return {
            'belief_id': self.belief_id,
            'content': self.content,
            'credence': self.credence,
            'source_depth': self.source_depth,
            'paper_ids': self.paper_ids,
            'is_causal': self.is_causal,
            'needs_caution': self.needs_caution
        }


@dataclass
class FollowUp:
    """A suggested follow-up question with executable query."""
    question: str
    type: str  # deeper, broader/scope, uncertainty
    rationale: str
    query_url: Optional[str] = None  # URL-encoded query for direct execution
    query_params: Dict[str, Any] = field(default_factory=dict)  # Parameters to pre-fill search

    def to_dict(self) -> Dict[str, Any]:
        return {
            'question': self.question,
            'type': self.type,
            'rationale': self.rationale,
            'query_url': self.query_url,
            'query_params': self.query_params
        }


@dataclass
class ContestedEvidence:
    """
    Contested evidence section grouping opposing views.

    Per Cartwright/Simon: Critical for epistemic transparency.
    Shows controversy prominently so researchers see disagreement.
    """
    topic: str
    supporting: List[EvidenceItem] = field(default_factory=list)
    contradicting: List[EvidenceItem] = field(default_factory=list)
    summary: str = ""  # Brief explanation of the controversy
    reasons_for_disagreement: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'topic': self.topic,
            'supporting': [e.to_dict() for e in self.supporting],
            'contradicting': [e.to_dict() for e in self.contradicting],
            'summary': self.summary,
            'reasons_for_disagreement': self.reasons_for_disagreement
        }


@dataclass
class QueryResponse:
    """Complete response to a query."""
    response_type: ResponseType
    query_intent: QueryIntent

    # Main response content
    summary: str
    confidence_level: str  # high, medium, low, unknown
    evidence_items: List[EvidenceItem] = field(default_factory=list)

    # Epistemic context
    total_supporting: int = 0
    total_contradicting: int = 0
    is_contested: bool = False
    abstract_only_warning: bool = False  # Cartwright: badge for abstract-only

    # H5: Contested evidence section (per Cartwright/Simon panel recommendation)
    contested_evidence: Optional[ContestedEvidence] = None

    # Follow-ups (exactly 3 per Simon)
    follow_ups: List[FollowUp] = field(default_factory=list)

    # Vocabulary expansion (per Bates: show transparently)
    vocabulary_used: Dict[str, List[str]] = field(default_factory=dict)

    # Scope information
    scope_conditions: Optional[Dict[str, Any]] = None
    enabling_conditions: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'response_type': self.response_type.value,
            'query_intent': self.query_intent.to_dict(),
            'summary': self.summary,
            'confidence_level': self.confidence_level,
            'evidence_items': [e.to_dict() for e in self.evidence_items],
            'total_supporting': self.total_supporting,
            'total_contradicting': self.total_contradicting,
            'is_contested': self.is_contested,
            'abstract_only_warning': self.abstract_only_warning,
            'contested_evidence': self.contested_evidence.to_dict() if self.contested_evidence else None,
            'follow_ups': [f.to_dict() for f in self.follow_ups],
            'vocabulary_used': self.vocabulary_used,
            'scope_conditions': self.scope_conditions,
            'enabling_conditions': self.enabling_conditions
        }


# =============================================================================
# Response Templates
# =============================================================================

RESPONSE_TEMPLATES = {
    QueryType.WHAT_IS: "{count} beliefs address the effect of {subject} on {object}. {main_finding}",
    QueryType.DOES_X_AFFECT_Y: "Based on {count} beliefs: {main_finding} Confidence: {confidence}.",
    QueryType.HOW_MUCH: "Effect size: {main_finding} Based on {count} studies.",
    QueryType.WHAT_DO_WE_KNOW: "We have {count} beliefs about {subject}. {main_finding}",
    QueryType.WHAT_EVIDENCE: "{count} pieces of evidence {direction} this claim. {main_finding}",
    QueryType.COMPARE: "Comparing {subject} and {object}: {main_finding}",
    QueryType.WHICH_IS_BETTER: "Based on available evidence: {main_finding}",
    QueryType.HOW_CONFIDENT: "Confidence level: {confidence}. {main_finding}",
    QueryType.WHY_BELIEVE: "This belief is supported by {count} sources. {main_finding}",
    QueryType.WHAT_CONTRADICTS: "{count} beliefs contradict this. {main_finding}",
    QueryType.WHAT_DONT_KNOW: "Key gaps in our knowledge: {main_finding}",
    QueryType.WHEN_DOES: "Scope conditions: {main_finding}",
    QueryType.FOR_WHOM: "Population applicability: {main_finding}",
    QueryType.UNKNOWN: "I couldn't parse your query clearly. {main_finding}",
}


# =============================================================================
# Query Response Generator
# =============================================================================

class QueryResponseGenerator:
    """
    Generates responses to parsed queries.

    Uses the web of belief to find relevant evidence and
    construct informative responses with follow-up suggestions.
    """

    def __init__(self, web: WebOfBelief):
        """Initialize with a web of belief."""
        self.web = web
        self.stability_engine = StabilityEngine(web)

    def generate(self, parse_result: ParseResult) -> QueryResponse:
        """
        Generate a response to a parsed query.

        Args:
            parse_result: The parsed query

        Returns:
            QueryResponse with answer and follow-ups
        """
        intent = parse_result.primary

        # Find relevant beliefs
        relevant = self._find_relevant_beliefs(intent)

        # Build response based on query type
        response = self._build_response(intent, relevant, parse_result.vocabulary_expansions)

        # Generate exactly 3 follow-ups (per Simon)
        response.follow_ups = self._generate_follow_ups(intent, relevant)

        return response

    def _find_relevant_beliefs(self, intent: QueryIntent) -> List[Belief]:
        """Find beliefs relevant to the query intent."""
        relevant = []

        # Get search terms
        search_terms = []
        if intent.subject:
            search_terms.append(intent.subject.lower())
            search_terms.extend([t.lower() for t in intent.subject_expansions])
        if intent.object:
            search_terms.append(intent.object.lower())
            search_terms.extend([t.lower() for t in intent.object_expansions])

        # Search beliefs
        for belief in self.web.beliefs.values():
            content_lower = belief.content.lower()
            score = 0

            for term in search_terms:
                if term in content_lower:
                    score += 1

            if score > 0:
                relevant.append((score, belief))

        # Sort by relevance score
        relevant.sort(key=lambda x: (-x[0], -x[1].credence.value))
        return [b for _, b in relevant[:20]]  # Top 20

    def _build_response(
        self,
        intent: QueryIntent,
        relevant: List[Belief],
        vocabulary: Dict[str, List[str]]
    ) -> QueryResponse:
        """Build response from relevant beliefs."""
        # Determine response type
        response_type = self._get_response_type(intent.query_type)

        # E1.D2 Panel (Pearl): Use directional opposition, not credence threshold
        # Credence represents belief strength, not support/contradiction
        positive_dir, negative_dir = self._has_directional_opposition(relevant, intent)

        # For backward compatibility, also track by credence for stats
        # But use directional opposition for contested detection
        supporting = positive_dir if positive_dir else [b for b in relevant if b.credence.value >= 0.5]
        contradicting = negative_dir if negative_dir else [b for b in relevant if b.credence.value < 0.5]

        # E1.D2: Check for contested beliefs using:
        # 1. Explicit contested flag on beliefs
        # 2. Directional opposition (X increases Y vs X decreases Y)
        is_contested = (
            any(b.contested for b in relevant) or  # Explicit flag
            (len(positive_dir) > 0 and len(negative_dir) > 0)  # Directional opposition
        )

        # Check for abstract-only causal claims (Cartwright warning)
        abstract_causal = [b for b in relevant
                          if b.source_depth == SourceDepth.ABSTRACT
                          and self._is_causal_claim(b)]
        abstract_only_warning = len(abstract_causal) > 0

        # Build evidence items
        evidence_items = []
        for belief in relevant[:10]:  # Top 10
            is_causal = self._is_causal_claim(belief)
            needs_caution = (belief.source_depth == SourceDepth.ABSTRACT and is_causal)

            evidence_items.append(EvidenceItem(
                belief_id=belief.belief_id,
                content=belief.content,
                credence=belief.credence.value,
                source_depth=belief.source_depth.value if belief.source_depth else "unknown",
                paper_ids=belief.paper_ids,
                is_causal=is_causal,
                needs_caution=needs_caution
            ))

        # Calculate confidence level
        if not relevant:
            confidence_level = "unknown"
        else:
            avg_credence = sum(b.credence.value for b in relevant) / len(relevant)
            if avg_credence >= 0.7:
                confidence_level = "high"
            elif avg_credence >= 0.4:
                confidence_level = "medium"
            else:
                confidence_level = "low"

        # Generate summary
        summary = self._generate_summary(intent, relevant, confidence_level)

        # Extract scope conditions from relevant beliefs
        scope_conditions = self._extract_scope_conditions(relevant)
        enabling_conditions = self._extract_enabling_conditions(relevant)

        # H5: Build contested evidence section if there is directional disagreement
        contested_evidence = None
        if is_contested:
            contested_evidence = self._build_contested_evidence(
                intent, positive_dir, negative_dir, evidence_items
            )

        return QueryResponse(
            response_type=response_type,
            query_intent=intent,
            summary=summary,
            confidence_level=confidence_level,
            evidence_items=evidence_items,
            total_supporting=len(supporting),
            total_contradicting=len(contradicting),
            is_contested=is_contested,
            abstract_only_warning=abstract_only_warning,
            contested_evidence=contested_evidence,
            vocabulary_used=vocabulary,
            scope_conditions=scope_conditions,
            enabling_conditions=enabling_conditions
        )

    def _get_response_type(self, query_type: QueryType) -> ResponseType:
        """Map query type to response type."""
        mapping = {
            QueryType.WHAT_IS: ResponseType.DIRECT_ANSWER,
            QueryType.DOES_X_AFFECT_Y: ResponseType.DIRECT_ANSWER,
            QueryType.HOW_MUCH: ResponseType.DIRECT_ANSWER,
            QueryType.WHAT_DO_WE_KNOW: ResponseType.SUMMARY,
            QueryType.WHAT_EVIDENCE: ResponseType.EVIDENCE_LIST,
            QueryType.COMPARE: ResponseType.COMPARISON,
            QueryType.WHICH_IS_BETTER: ResponseType.COMPARISON,
            QueryType.HOW_CONFIDENT: ResponseType.CONFIDENCE_REPORT,
            QueryType.WHY_BELIEVE: ResponseType.EVIDENCE_LIST,
            QueryType.WHAT_CONTRADICTS: ResponseType.EVIDENCE_LIST,
            QueryType.WHAT_DONT_KNOW: ResponseType.GAP_REPORT,
            QueryType.WHEN_DOES: ResponseType.SCOPE_REPORT,
            QueryType.FOR_WHOM: ResponseType.SCOPE_REPORT,
            QueryType.UNKNOWN: ResponseType.CLARIFICATION_NEEDED,
        }
        return mapping.get(query_type, ResponseType.DIRECT_ANSWER)

    def _is_causal_claim(self, belief: Belief) -> bool:
        """Check if belief makes a causal claim."""
        causal_keywords = [
            'cause', 'effect', 'affect', 'impact', 'influence',
            'improve', 'reduce', 'increase', 'decrease', 'lead to',
            'result in', 'because', 'due to'
        ]
        content_lower = belief.content.lower()
        return any(kw in content_lower for kw in causal_keywords)

    def _get_causal_direction(self, belief: Belief) -> Optional[str]:
        """
        E1.D2 Panel (Pearl): Detect the causal direction of a belief.

        Returns:
            'positive': Effect increases/improves/enhances the outcome
            'negative': Effect decreases/reduces/diminishes the outcome
            'neutral': Effect mentioned but direction unclear
            None: No directional language found
        """
        content_lower = belief.content.lower()

        # Positive direction indicators
        positive_terms = [
            'increase', 'improve', 'enhance', 'promote', 'facilitate',
            'boost', 'elevate', 'raise', 'strengthen', 'beneficial',
            'positive effect', 'positive impact', 'higher', 'better'
        ]

        # Negative direction indicators
        negative_terms = [
            'decrease', 'reduce', 'diminish', 'inhibit', 'impair',
            'lower', 'worsen', 'weaken', 'detrimental', 'harmful',
            'negative effect', 'negative impact', 'decline', 'worse'
        ]

        # Negation terms that flip the direction
        negation_terms = ['not ', 'no ', 'without ', "doesn't ", "don't ", "did not ", "does not "]

        has_positive = any(term in content_lower for term in positive_terms)
        has_negative = any(term in content_lower for term in negative_terms)
        has_negation = any(neg in content_lower for neg in negation_terms)

        # Handle negation flipping
        if has_negation:
            # Simplified negation handling - if negation is present, flip the detected direction
            if has_positive and not has_negative:
                return 'negative'
            elif has_negative and not has_positive:
                return 'positive'

        # Standard direction detection
        if has_positive and not has_negative:
            return 'positive'
        elif has_negative and not has_positive:
            return 'negative'
        elif has_positive and has_negative:
            return 'neutral'  # Mixed signals
        else:
            return None  # No directional language

    def _has_directional_opposition(
        self,
        beliefs: List[Belief],
        intent: QueryIntent
    ) -> Tuple[List[Belief], List[Belief]]:
        """
        E1.D2 Panel (Pearl): Detect directional opposition in beliefs.

        Rather than using credence threshold, identify beliefs that:
        - Assert X increases Y
        - Assert X decreases Y

        Returns:
            Tuple of (positive_direction, negative_direction) belief lists
        """
        positive = []
        negative = []
        neutral = []

        for belief in beliefs:
            direction = self._get_causal_direction(belief)
            if direction == 'positive':
                positive.append(belief)
            elif direction == 'negative':
                negative.append(belief)
            else:
                neutral.append(belief)

        return positive, negative

    def _build_contested_evidence(
        self,
        intent: QueryIntent,
        positive_direction: List[Belief],
        negative_direction: List[Belief],
        evidence_items: List[EvidenceItem]
    ) -> ContestedEvidence:
        """
        Build contested evidence section with opposing views grouped.

        E1.D2 Panel (Pearl): Use directional opposition, not credence threshold.
        Per Cartwright/Simon panel: Critical for epistemic transparency.
        Shows controversy prominently so researchers see disagreement.
        """
        topic = f"{intent.subject or 'this topic'}"
        if intent.object:
            topic += f" and {intent.object}"

        # E1.D2: Match evidence items to beliefs by directional opposition
        positive_ids = {b.belief_id for b in positive_direction}
        negative_ids = {b.belief_id for b in negative_direction}

        supporting_items = [
            e for e in evidence_items if e.belief_id in positive_ids
        ][:5]  # Top 5 positive direction

        contradicting_items = [
            e for e in evidence_items if e.belief_id in negative_ids
        ][:5]  # Top 5 negative direction

        # Generate summary of the controversy
        if supporting_items and contradicting_items:
            summary = (
                f"Evidence shows directional disagreement on {topic}. "
                f"{len(supporting_items)} sources suggest positive effects while "
                f"{len(contradicting_items)} sources suggest negative effects."
            )
        elif supporting_items:
            summary = f"Evidence suggests positive effects of {topic}."
        else:
            summary = f"Evidence suggests negative effects of {topic}."

        # Identify reasons for disagreement
        reasons = self._identify_disagreement_reasons(positive_direction, negative_direction)

        return ContestedEvidence(
            topic=topic,
            supporting=supporting_items,
            contradicting=contradicting_items,
            summary=summary,
            reasons_for_disagreement=reasons
        )

    def _identify_disagreement_reasons(
        self,
        positive_direction: List[Belief],
        negative_direction: List[Belief]
    ) -> List[str]:
        """
        Identify potential reasons for disagreement between beliefs.

        E1.D2 Panel: Updated terminology (positive_direction/negative_direction).

        Checks for differences in:
        - Source depth (abstract vs full-text) - evidence quality asymmetry
        - Population/setting scope
        - Methodology indicators
        - Measurement methods (per Cartwright panel: critical for neuroarchitecture)
        """
        reasons = []

        # Check source depth differences (per Cartwright: evidence quality asymmetry)
        positive_depths = {b.source_depth for b in positive_direction if b.source_depth}
        negative_depths = {b.source_depth for b in negative_direction if b.source_depth}
        if SourceDepth.ABSTRACT in positive_depths and SourceDepth.FULL_TEXT in negative_depths:
            reasons.append("Evidence quality asymmetry: positive findings rely more on abstracts; negative findings include full-text analysis")
        elif SourceDepth.FULL_TEXT in positive_depths and SourceDepth.ABSTRACT in negative_depths:
            reasons.append("Evidence quality asymmetry: negative findings rely more on abstracts; positive findings include full-text analysis")

        # Check scope differences
        positive_scopes = {b.scope.population for b in positive_direction if b.scope and b.scope.population}
        negative_scopes = {b.scope.population for b in negative_direction if b.scope and b.scope.population}
        if positive_scopes and negative_scopes and positive_scopes != negative_scopes:
            reasons.append(f"Scope mismatch: different populations studied - positive ({', '.join(positive_scopes)}) vs negative ({', '.join(negative_scopes)})")

        # Check for methodology keywords (lab vs field)
        lab_keywords = ['laboratory', 'controlled', 'experiment']
        field_keywords = ['field study', 'observational', 'real-world']

        positive_is_lab = any(
            any(kw in b.content.lower() for kw in lab_keywords)
            for b in positive_direction
        )
        negative_is_field = any(
            any(kw in b.content.lower() for kw in field_keywords)
            for b in negative_direction
        )
        if positive_is_lab and negative_is_field:
            reasons.append("Genuine scientific disagreement: positive findings from controlled settings; negative findings from field studies")

        # E1.D2 Panel (Cartwright): Check for measurement method differences
        # Critical for neuroarchitecture research where self-report vs physiological measures differ
        self_report_keywords = ['self-report', 'questionnaire', 'survey', 'subjective', 'perceived']
        physiological_keywords = ['physiological', 'cortisol', 'heart rate', 'blood pressure', 'EEG', 'fMRI', 'biomarker']
        behavioral_keywords = ['behavioral', 'performance', 'task', 'accuracy', 'reaction time']

        positive_self_report = any(
            any(kw in b.content.lower() for kw in self_report_keywords)
            for b in positive_direction
        )
        negative_physiological = any(
            any(kw in b.content.lower() for kw in physiological_keywords)
            for b in negative_direction
        )
        positive_physiological = any(
            any(kw in b.content.lower() for kw in physiological_keywords)
            for b in positive_direction
        )
        negative_self_report = any(
            any(kw in b.content.lower() for kw in self_report_keywords)
            for b in negative_direction
        )

        if positive_self_report and negative_physiological:
            reasons.append("Measurement method difference: positive findings from self-report; negative findings from physiological measures")
        elif positive_physiological and negative_self_report:
            reasons.append("Measurement method difference: positive findings from physiological measures; negative findings from self-report")

        # E1.D2: Check for temporal differences (per Kaplan - relevant for neuroarchitecture)
        short_term_keywords = ['short-term', 'acute', 'immediate', 'brief', 'minutes', 'hours']
        long_term_keywords = ['long-term', 'chronic', 'prolonged', 'weeks', 'months', 'years']

        positive_short = any(
            any(kw in b.content.lower() for kw in short_term_keywords)
            for b in positive_direction
        )
        negative_long = any(
            any(kw in b.content.lower() for kw in long_term_keywords)
            for b in negative_direction
        )
        if positive_short and negative_long:
            reasons.append("Temporal scope difference: positive findings from short-term studies; negative findings from long-term studies")

        # Default reason if none found
        if not reasons:
            reasons.append("Reasons for disagreement unclear - may reflect genuine uncertainty in the field")

        return reasons

    def _generate_summary(
        self,
        intent: QueryIntent,
        relevant: List[Belief],
        confidence: str
    ) -> str:
        """Generate summary text for response."""
        template = RESPONSE_TEMPLATES.get(intent.query_type,
                                          "Found {count} relevant beliefs. {main_finding}")

        # Main finding from highest credence belief
        if relevant:
            main_belief = max(relevant, key=lambda b: b.credence.value)
            main_finding = main_belief.content
        else:
            main_finding = "No directly relevant evidence found."

        # Direction for evidence queries
        direction = "support" if intent.query_type == QueryType.WHAT_EVIDENCE else "relate to"

        return template.format(
            count=len(relevant),
            subject=intent.subject or "the topic",
            object=intent.object or "the outcome",
            main_finding=main_finding,
            confidence=confidence,
            direction=direction
        )

    def _generate_follow_ups(
        self,
        intent: QueryIntent,
        relevant: List[Belief]
    ) -> List[FollowUp]:
        """
        Generate exactly 3 follow-up questions with executable queries.

        Per expert panel (Simon): deeper, scope, uncertainty.
        Per panel revision: "broader" replaced with "scope" (Cartwright/Simon compromise).
        Per Bates: follow-ups must be clickable/executable.
        """
        import urllib.parse

        follow_ups = []
        subject = intent.subject or "this topic"
        obj = intent.object or "outcomes"

        # 1. DEEPER follow-up
        deeper_q = f"What are the mechanisms by which {subject} affects {obj}?"
        deeper = FollowUp(
            question=deeper_q,
            type="deeper",
            rationale="Understand the underlying causal pathway",
            query_url=f"/api/query/search?query={urllib.parse.quote(deeper_q)}",
            query_params={'query': deeper_q, 'include_expansions': True}
        )
        follow_ups.append(deeper)

        # 2. SCOPE follow-up (replaced "broader" per Cartwright/Simon)
        scope_q = f"Under what conditions does {subject} affect {obj}?"
        scope = FollowUp(
            question=scope_q,
            type="scope",
            rationale="Understand when and for whom this applies",
            query_url=f"/api/query/search?query={urllib.parse.quote(scope_q)}",
            query_params={'query': scope_q, 'include_expansions': True}
        )
        follow_ups.append(scope)

        # 3. UNCERTAINTY follow-up
        if relevant:
            contested = [b for b in relevant if b.contested]
            if contested:
                uncertainty_q = f"Why is the evidence about {subject} contested?"
                uncertainty = FollowUp(
                    question=uncertainty_q,
                    type="uncertainty",
                    rationale="Understand sources of disagreement",
                    query_url=f"/api/query/search?query={urllib.parse.quote(uncertainty_q)}",
                    query_params={'query': uncertainty_q, 'include_expansions': True}
                )
            else:
                uncertainty_q = f"What don't we know about {subject}?"
                uncertainty = FollowUp(
                    question=uncertainty_q,
                    type="uncertainty",
                    rationale="Identify gaps in current knowledge",
                    query_url=f"/api/query/search?query={urllib.parse.quote(uncertainty_q)}",
                    query_params={'query': uncertainty_q, 'include_expansions': True}
                )
        else:
            uncertainty_q = f"What research is needed on {subject}?"
            uncertainty = FollowUp(
                question=uncertainty_q,
                type="uncertainty",
                rationale="Limited evidence available",
                query_url=f"/api/query/search?query={urllib.parse.quote(uncertainty_q)}",
                query_params={'query': uncertainty_q, 'include_expansions': True}
            )
        follow_ups.append(uncertainty)

        return follow_ups

    def _extract_scope_conditions(self, relevant: List[Belief]) -> Optional[Dict[str, Any]]:
        """Extract scope conditions from relevant beliefs."""
        conditions = {
            'populations': set(),
            'settings': set(),
            'durations': set()
        }

        for belief in relevant:
            if belief.scope:
                if belief.scope.population:
                    conditions['populations'].add(belief.scope.population)
                if belief.scope.setting:
                    conditions['settings'].add(belief.scope.setting)
                if belief.scope.duration:
                    conditions['durations'].add(belief.scope.duration)

        # Convert sets to lists and return if any found
        result = {k: list(v) for k, v in conditions.items() if v}
        return result if result else None

    def _extract_enabling_conditions(self, relevant: List[Belief]) -> Optional[Dict[str, Any]]:
        """Extract enabling conditions from relevant beliefs."""
        conditions = {
            'minimum_exposure': set(),
            'thresholds': set(),
            'temporal_order': set()
        }

        for belief in relevant:
            if belief.enabling_conditions:
                ec = belief.enabling_conditions
                if ec.minimum_exposure:
                    conditions['minimum_exposure'].add(ec.minimum_exposure)
                if ec.threshold:
                    conditions['thresholds'].add(ec.threshold)
                if ec.temporal_order:
                    conditions['temporal_order'].add(ec.temporal_order)

        result = {k: list(v) for k, v in conditions.items() if v}
        return result if result else None


# =============================================================================
# Convenience Functions
# =============================================================================

def generate_response(web: WebOfBelief, query: str) -> QueryResponse:
    """Generate response to a natural language query."""
    from src.services.query_parser import parse_query
    parse_result = parse_query(query)
    generator = QueryResponseGenerator(web)
    return generator.generate(parse_result)
