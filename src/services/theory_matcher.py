"""
Theory Matcher: Embedding-based theory inference with disambiguation.

Sprint: TD-A (Theory Inference)
Panel: P-TD (Technical Debt)
Created: February 8, 2026

This module provides embedding-based theory matching that improves on
simple keyword matching. It uses sentence-transformers to compute
semantic similarity between claim text and theory descriptions.

Target accuracy: 85% (up from ~60% with keywords alone)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)

# =============================================================================
# THEORY DESCRIPTIONS
# =============================================================================

# Rich descriptions of each theory for embedding
# These capture the core concepts, mechanisms, and typical contexts

THEORY_DESCRIPTIONS: Dict[str, str] = {
    "ART": """
        Attention Restoration Theory (ART) proposes that natural environments
        restore directed attention capacity that becomes depleted through mental
        effort and sustained focus. Key concepts include soft fascination (effortless
        attention to nature), being away (psychological distance from routine),
        extent (scope and coherence of environment), and compatibility (fit between
        environment and purpose). ART predicts that nature exposure reduces mental
        fatigue, improves concentration, and enhances cognitive performance.
        Associated with Kaplan & Kaplan's research on restorative environments.
        Outcomes include attention, concentration, executive function, cognitive
        performance, mental fatigue recovery, and directed attention capacity.
    """,

    "SRT": """
        Stress Recovery Theory (SRT) proposes that natural environments promote
        rapid psychophysiological recovery from stress through evolved affective
        responses. Key mechanisms include parasympathetic activation, cortisol
        reduction, and positive affect. SRT predicts that nature exposure reduces
        physiological stress markers (heart rate, blood pressure, cortisol, skin
        conductance) and improves emotional state. Associated with Ulrich's
        research on restorative responses to nature. Outcomes include stress
        reduction, relaxation, mood improvement, anxiety reduction, and
        physiological recovery including HPA axis regulation.
    """,

    "Biophilia": """
        Biophilia Hypothesis proposes that humans have an innate, evolved affiliation
        with living systems and nature. This biological predisposition manifests as
        preference for natural environments, attention to living things, and positive
        responses to nature contact. Associated with E.O. Wilson's work on human-nature
        connection. Predicts that preferences for nature are universal, develop early,
        and have evolutionary origins. Related to habitat selection, environmental
        preference, and the deep human-nature relationship.
    """,

    "Prospect-Refuge": """
        Prospect-Refuge Theory proposes that humans prefer environments that offer
        both prospect (open views, ability to see) and refuge (shelter, protection,
        enclosure). This preference reflects evolutionary advantages of environments
        that allowed both surveillance and hiding. Associated with Appleton's work
        on landscape aesthetics. Predicts preferences for edge locations, elevated
        viewpoints, spaces with overhead canopy, and environments balancing openness
        with enclosure. Related to defensible space, visual access, and feeling safe.
    """,

    "Topophilia": """
        Topophilia describes the affective bond between people and places. It
        encompasses emotional attachment to environment, sense of place, and
        place identity. Associated with Yi-Fu Tuan's humanistic geography.
        Predicts that meaningful places support wellbeing, that place attachment
        develops through experience, and that displacement causes distress.
        Related to environmental identity, rootedness, and belonging.
    """,

    "Affordance": """
        Affordance Theory (ecological perception) proposes that environments are
        perceived in terms of action possibilities they offer. Affordances are
        relational properties between organism capabilities and environmental
        features. Associated with Gibson's ecological psychology. In built
        environment contexts, predicts that design features enabling desired
        actions support wellbeing and performance. Related to wayfinding,
        usability, and functional fit between person and environment.
    """
}

# Shorter version for embedding (more focused, less noise)
THEORY_CORE_DESCRIPTIONS: Dict[str, str] = {
    "ART": "Attention restoration through nature exposure reduces mental fatigue and improves concentration and cognitive performance via soft fascination and directed attention recovery",

    "SRT": "Stress recovery through nature exposure reduces physiological stress markers like cortisol and heart rate via parasympathetic activation and psychophysiological restoration",

    "Biophilia": "Innate human affiliation with nature and living systems reflects evolved preference for natural environments and biological connection to life",

    "Prospect-Refuge": "Environmental preference for views and shelter reflects evolutionary advantage of spaces offering both prospect for surveillance and refuge for protection",

    "Topophilia": "Emotional attachment to place and sense of belonging reflects affective bond between person and meaningful environment",

    "Affordance": "Environmental perception in terms of action possibilities offered by features relative to organism capabilities"
}


# =============================================================================
# DISAMBIGUATION RULES
# =============================================================================

@dataclass
class DisambiguationRule:
    """Rule for disambiguating false positive matches."""
    theory: str
    false_positive_patterns: List[str]  # Patterns that indicate NOT this theory
    required_context: List[str]  # At least one must be present for valid match
    exclusion_boost: float = 0.3  # Amount to reduce score if false positive detected


# Known false positive patterns
DISAMBIGUATION_RULES: List[DisambiguationRule] = [
    DisambiguationRule(
        theory="SRT",
        false_positive_patterns=[
            r"\bmechanical stress\b",
            r"\bstress test(ing)?\b",
            r"\bmaterial stress\b",
            r"\bstress fracture\b",
            r"\bthermal stress\b",
            r"\bstructural stress\b",
            r"\bstress-strain\b",
            r"\bengineering\b.*\bstress\b",
        ],
        required_context=[
            "nature", "natural", "green", "park", "forest", "garden",
            "outdoor", "environment", "restoration", "recovery",
            "psycho", "physiolog", "cortisol", "heart rate", "blood pressure",
            "anxiety", "mood", "wellbeing", "well-being", "relaxation"
        ]
    ),
    DisambiguationRule(
        theory="ART",
        false_positive_patterns=[
            r"\battention to detail\b",
            r"\bpay(ing)? attention\b",
            r"\battention span\b(?!.*restor)",  # Unless restoration mentioned
            r"\battention deficit\b(?!.*nature)",  # Unless nature context
            r"\battention-grabbing\b",
            r"\bmarketing\b.*\battention\b",
            r"\battention economy\b",
        ],
        required_context=[
            "nature", "natural", "green", "restoration", "restorative",
            "fatigue", "directed attention", "soft fascination",
            "kaplan", "cognitive", "concentration", "mental"
        ]
    ),
    DisambiguationRule(
        theory="Biophilia",
        false_positive_patterns=[
            r"\bphilia\b(?!.*bio)",  # Other philias
            r"\bphilosophy\b",
        ],
        required_context=[
            "nature", "natural", "living", "life", "evolved", "innate",
            "wilson", "preference", "affiliation"
        ]
    ),
    DisambiguationRule(
        theory="Prospect-Refuge",
        false_positive_patterns=[
            r"\bprospect(s|ive)?\b(?!.*refuge)",  # Prospect without refuge context
            r"\bjob prospect\b",
            r"\bfuture prospect\b",
            r"\bbusiness prospect\b",
            r"\brefugee\b",
        ],
        required_context=[
            "view", "visibility", "shelter", "enclosure", "landscape",
            "appleton", "edge", "canopy", "open", "defensible"
        ]
    ),
]


# =============================================================================
# THEORY MATCHER RESULT
# =============================================================================

class MatchMethod(Enum):
    """How the theory match was determined."""
    EMBEDDING = "embedding"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    CONSENSUS = "consensus"
    UNCERTAIN = "uncertain"


@dataclass
class TheoryMatchResult:
    """Result of theory matching with confidence and provenance."""
    theory: Optional[str]
    confidence: float
    method: MatchMethod

    # All theory scores
    scores: Dict[str, float] = field(default_factory=dict)

    # Disambiguation info
    disambiguation_applied: bool = False
    disambiguation_notes: List[str] = field(default_factory=list)

    # Review flag
    needs_review: bool = False
    review_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theory": self.theory,
            "confidence": self.confidence,
            "method": self.method.value,
            "scores": self.scores,
            "disambiguation_applied": self.disambiguation_applied,
            "disambiguation_notes": self.disambiguation_notes,
            "needs_review": self.needs_review,
            "review_reason": self.review_reason
        }


# =============================================================================
# EMBEDDING THEORY MATCHER
# =============================================================================

class EmbeddingTheoryMatcher:
    """
    Matches claim text to theories using semantic embeddings.

    Uses sentence-transformers to compute similarity between claim
    text and theory descriptions. Falls back to keyword matching
    when embedding similarity is uncertain.
    """

    # Singleton instance
    _instance: Optional['EmbeddingTheoryMatcher'] = None

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the matcher.

        Args:
            model_name: Sentence transformer model to use.
                       Default is lightweight but effective model.
        """
        self.model_name = model_name
        self._model = None
        self._theory_embeddings: Dict[str, Any] = {}
        self._initialized = False

    @classmethod
    def get_instance(cls) -> 'EmbeddingTheoryMatcher':
        """Get singleton instance (lazy initialization)."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _ensure_initialized(self) -> bool:
        """
        Lazily initialize the model and embeddings.

        Returns:
            True if initialization succeeded, False otherwise.
        """
        if self._initialized:
            return True

        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)

            # Pre-compute theory embeddings
            logger.info("Computing theory embeddings...")
            for theory, description in THEORY_CORE_DESCRIPTIONS.items():
                self._theory_embeddings[theory] = self._model.encode(
                    description,
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )

            self._initialized = True
            logger.info(f"Theory matcher initialized with {len(self._theory_embeddings)} theories")
            return True

        except ImportError:
            logger.warning("sentence-transformers not installed, falling back to keyword matching")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            return False

    def _compute_embedding_scores(self, text: str) -> Dict[str, float]:
        """
        Compute embedding similarity scores for each theory.

        Args:
            text: Claim text to match

        Returns:
            Dict mapping theory names to similarity scores (0-1)
        """
        if not self._ensure_initialized():
            return {}

        import numpy as np

        # Encode the claim text
        text_embedding = self._model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        # Compute cosine similarity with each theory
        scores = {}
        for theory, theory_emb in self._theory_embeddings.items():
            # Dot product of normalized vectors = cosine similarity
            similarity = float(np.dot(text_embedding, theory_emb))
            # Shift from [-1, 1] to [0, 1] range
            scores[theory] = (similarity + 1) / 2

        return scores

    def _apply_disambiguation(
        self,
        text: str,
        scores: Dict[str, float]
    ) -> Tuple[Dict[str, float], List[str]]:
        """
        Apply disambiguation rules to reduce false positives.

        Args:
            text: Original claim text
            scores: Current theory scores

        Returns:
            Tuple of (adjusted_scores, notes)
        """
        text_lower = text.lower()
        adjusted = scores.copy()
        notes = []

        for rule in DISAMBIGUATION_RULES:
            if rule.theory not in adjusted:
                continue

            # Check for false positive patterns
            for pattern in rule.false_positive_patterns:
                if re.search(pattern, text_lower):
                    # False positive detected
                    reduction = rule.exclusion_boost
                    old_score = adjusted[rule.theory]
                    adjusted[rule.theory] = max(0, old_score - reduction)
                    notes.append(
                        f"Reduced {rule.theory} by {reduction:.2f} "
                        f"(pattern: {pattern[:30]}...)"
                    )
                    break

            # Check if required context is present
            if adjusted[rule.theory] > 0.3:  # Only check if still a candidate
                has_context = any(
                    ctx.lower() in text_lower
                    for ctx in rule.required_context
                )
                if not has_context:
                    # Reduce confidence without required context
                    old_score = adjusted[rule.theory]
                    adjusted[rule.theory] = old_score * 0.7
                    notes.append(
                        f"Reduced {rule.theory} by 30% (missing required context)"
                    )

        return adjusted, notes

    def _keyword_scores(self, text: str) -> Dict[str, float]:
        """
        Compute keyword-based scores (fallback method).

        Uses the existing THEORY_KEYWORDS from extraction_to_web.py
        """
        from src.services.extraction_to_web import THEORY_KEYWORDS

        text_lower = text.lower()
        scores = {theory: 0.0 for theory in THEORY_KEYWORDS}

        for theory, keywords in THEORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # Accumulate with diminishing returns
                    scores[theory] = min(1.0, scores[theory] + 0.25)

        return scores

    def match(
        self,
        text: str,
        high_confidence_threshold: float = 0.7,
        low_confidence_threshold: float = 0.5,
        use_hybrid: bool = True
    ) -> TheoryMatchResult:
        """
        Match claim text to a theory.

        Args:
            text: Claim text (typically the claim statement)
            high_confidence_threshold: Score above this = auto-assign
            low_confidence_threshold: Score below this = uncertain
            use_hybrid: Combine embedding + keyword scores

        Returns:
            TheoryMatchResult with theory, confidence, and metadata
        """
        if not text or not text.strip():
            return TheoryMatchResult(
                theory=None,
                confidence=0.0,
                method=MatchMethod.UNCERTAIN,
                needs_review=True,
                review_reason="Empty text"
            )

        # Get embedding scores (if available)
        embedding_scores = self._compute_embedding_scores(text)

        # Get keyword scores (always available)
        keyword_scores = self._keyword_scores(text)

        # Determine method and combine scores
        if embedding_scores and use_hybrid:
            # Hybrid: weighted combination
            scores = {}
            for theory in set(embedding_scores.keys()) | set(keyword_scores.keys()):
                emb = embedding_scores.get(theory, 0.0)
                kw = keyword_scores.get(theory, 0.0)
                # Embedding weight: 0.7, Keyword weight: 0.3
                scores[theory] = 0.7 * emb + 0.3 * kw
            method = MatchMethod.HYBRID
        elif embedding_scores:
            scores = embedding_scores
            method = MatchMethod.EMBEDDING
        else:
            scores = keyword_scores
            method = MatchMethod.KEYWORD

        # Apply disambiguation rules
        scores, disambiguation_notes = self._apply_disambiguation(text, scores)
        disambiguation_applied = len(disambiguation_notes) > 0

        # Find best match
        if not scores:
            return TheoryMatchResult(
                theory=None,
                confidence=0.0,
                method=MatchMethod.UNCERTAIN,
                scores={},
                needs_review=True,
                review_reason="No theories scored"
            )

        best_theory = max(scores, key=scores.get)
        best_score = scores[best_theory]

        # Determine if needs review
        needs_review = False
        review_reason = None

        if best_score < low_confidence_threshold:
            needs_review = True
            review_reason = f"Low confidence: {best_score:.2f}"
            theory = None
        elif best_score < high_confidence_threshold:
            needs_review = True
            review_reason = f"Medium confidence: {best_score:.2f}"
            theory = best_theory
        else:
            theory = best_theory

        # Check for close second
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) > 1:
            gap = sorted_scores[0] - sorted_scores[1]
            if gap < 0.1 and best_score > low_confidence_threshold:
                needs_review = True
                review_reason = f"Close alternatives (gap={gap:.2f})"

        return TheoryMatchResult(
            theory=theory,
            confidence=best_score,
            method=method,
            scores=scores,
            disambiguation_applied=disambiguation_applied,
            disambiguation_notes=disambiguation_notes,
            needs_review=needs_review,
            review_reason=review_reason
        )

    def match_with_context(
        self,
        statement: str,
        outcome_ids: Optional[List[str]] = None,
        environment_factors: Optional[List[str]] = None
    ) -> TheoryMatchResult:
        """
        Match with additional context from outcomes and environment.

        Args:
            statement: Main claim statement
            outcome_ids: Outcome taxonomy IDs
            environment_factors: Environment taxonomy IDs

        Returns:
            TheoryMatchResult with enhanced matching
        """
        # Build enriched text with context
        parts = [statement]

        if outcome_ids:
            parts.append(f"Outcomes: {', '.join(outcome_ids)}")

        if environment_factors:
            parts.append(f"Environment: {', '.join(environment_factors)}")

        enriched_text = " ".join(parts)

        return self.match(enriched_text)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_theory_matcher() -> EmbeddingTheoryMatcher:
    """Get the singleton theory matcher instance."""
    return EmbeddingTheoryMatcher.get_instance()


def match_theory(
    text: str,
    use_embeddings: bool = True
) -> TheoryMatchResult:
    """
    Match text to a theory.

    Args:
        text: Claim text to match
        use_embeddings: Whether to use embedding similarity

    Returns:
        TheoryMatchResult
    """
    matcher = get_theory_matcher()
    return matcher.match(text, use_hybrid=use_embeddings)


def get_theory_confidence(text: str, theory: str) -> float:
    """
    Get confidence score for a specific theory.

    Args:
        text: Claim text
        theory: Theory name to check

    Returns:
        Confidence score (0-1)
    """
    result = match_theory(text)
    return result.scores.get(theory, 0.0)
