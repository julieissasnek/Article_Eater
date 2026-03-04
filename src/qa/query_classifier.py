"""
Query Classifier — Map Queries to Pre-Computed Archetypes
==========================================================

Classifies an incoming query into a (topic_cluster, question_pattern, user_type)
archetype that maps to a pre-computed enriched answer.

Question patterns:
  EVIDENCE    — "What does the evidence say about X?"
  MECHANISM   — "How does X work?" / "What mechanism..."
  PRACTICAL   — "How should I design X?" / "What should I do..."
  COMPARISON  — "Is X better than Y?"
  DISAGREEMENT — "Why do studies disagree on X?"
  DEFINITION  — "What is X?"
  LATENT      — "What are the latent variables in X?" (Deep Researcher)
  META_REVIEW — "Summarize the findings on X" (Deep Researcher)

Usage:
    classifier = QueryClassifier()
    archetype = classifier.classify("Do natural environments enhance restoration?", "student")
    # archetype.topic_cluster = "nature_restoration"
    # archetype.question_pattern = "EVIDENCE"
    # archetype.user_type = "student"
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class QueryArchetype:
    """A classified query mapped to a pre-computed archetype."""
    topic_cluster: str
    question_pattern: str  # EVIDENCE, MECHANISM, PRACTICAL, etc.
    user_type: str
    confidence: float = 0.0
    matched_keywords: List[str] = None

    def __post_init__(self):
        if self.matched_keywords is None:
            self.matched_keywords = []

    @property
    def cache_key(self) -> str:
        """Unique key for cache lookup."""
        return f"{self.topic_cluster}:{self.question_pattern}:{self.user_type}"


# ---------------------------------------------------------------------------
# Topic clusters (derived from the extraction corpus domains + theory links)
# ---------------------------------------------------------------------------

TOPIC_CLUSTERS = {
    "nature_restoration": {
        "keywords": ["nature", "natural", "restoration", "restorative", "biophilia",
                     "green", "park", "garden", "outdoor", "vegetation"],
        "theories": ["ART", "SRT", "Biophilia"],
    },
    "lighting_performance": {
        "keywords": ["light", "lighting", "daylight", "illumination", "luminance",
                     "color temperature", "circadian", "bright", "dim"],
        "theories": ["PP", "DP"],
    },
    "thermal_comfort": {
        "keywords": ["thermal", "temperature", "comfort", "heat", "cold", "hvac",
                     "climate", "warmth", "cooling"],
        "theories": ["PP", "EC"],
    },
    "acoustics_noise": {
        "keywords": ["acoustic", "noise", "sound", "quiet", "loudness", "speech",
                     "auditory", "sonic", "music"],
        "theories": ["PP", "IC"],
    },
    "spatial_cognition": {
        "keywords": ["spatial", "wayfinding", "navigation", "layout", "open plan",
                     "enclosure", "prospect", "refuge", "ceiling", "room size"],
        "theories": ["Prospect-Refuge", "PP"],
    },
    "privacy_territory": {
        "keywords": ["privacy", "territory", "personal space", "crowding", "density",
                     "boundary", "distraction", "interruption"],
        "theories": ["Privacy Regulation", "PP"],
    },
    "color_affect": {
        "keywords": ["color", "colour", "hue", "saturation", "warm", "cool",
                     "chromatic", "paint", "palette"],
        "theories": ["PP", "EC"],
    },
    "multisensory_integration": {
        "keywords": ["multisensory", "crossmodal", "sensory", "integration",
                     "congruent", "multimodal", "synesthetic"],
        "theories": ["MSI", "PP"],
    },
    "workspace_productivity": {
        "keywords": ["office", "workspace", "productivity", "work", "task performance",
                     "concentration", "focus", "coworking"],
        "theories": ["DT", "PP"],
    },
    "wellbeing_health": {
        "keywords": ["wellbeing", "well-being", "health", "stress", "anxiety",
                     "mood", "affect", "positive", "mental health"],
        "theories": ["SRT", "ART", "Biophilia"],
    },
}


# ---------------------------------------------------------------------------
# Question pattern detection
# ---------------------------------------------------------------------------

QUESTION_PATTERNS = {
    "EVIDENCE": [
        r"what (does|do) .* (evidence|research|studies|data|findings?) (say|show|suggest|indicate)",
        r"is there evidence",
        r"what (is|are) the effect",
        r"does .* (enhance|increase|decrease|affect|influence|impact)",
        r"do .* (enhance|increase|decrease|affect|influence|impact)",
    ],
    "MECHANISM": [
        r"how does .* work",
        r"what (is|are) the mechanism",
        r"why does .* (cause|lead|result)",
        r"through what (process|pathway|mechanism)",
        r"what mediates",
        r"what moderates",
    ],
    "PRACTICAL": [
        r"how (should|can|do) (i|we|you) (design|build|create|implement)",
        r"what (should|can) (i|we) do",
        r"best practice",
        r"recommendation",
        r"guideline",
    ],
    "COMPARISON": [
        r"(is|are) .* (better|worse|more|less) than",
        r"compare .* (with|to|and|vs)",
        r"which is (better|more|preferred)",
        r"difference between .* and",
    ],
    "DISAGREEMENT": [
        r"why do .* disagree",
        r"conflicting (findings|evidence|results)",
        r"inconsisten",
        r"controversy",
        r"debate",
    ],
    "DEFINITION": [
        r"what is (?:a |an |the )?(?!\w+ (?:effect|impact))",
        r"define ",
        r"meaning of",
    ],
    "LATENT": [
        r"latent (variable|factor|construct)",
        r"hidden (variable|factor)",
        r"underlying (factor|mechanism|cause)",
        r"confound",
    ],
    "META_REVIEW": [
        r"summarize .* findings",
        r"meta.?review",
        r"meta.?analysis",
        r"overview of .* research",
        r"main lesson",
        r"what .* need.* (to be|be) (done|researched|studied)",
    ],
}


# ---------------------------------------------------------------------------
# Query Classifier
# ---------------------------------------------------------------------------

class QueryClassifier:
    """
    Classifies queries into pre-computed archetypes.

    Uses keyword matching against topic clusters and regex patterns
    for question type classification.
    """

    _STOP_WORDS = frozenset([
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "do", "does", "did", "will", "would", "could", "should",
        "of", "in", "to", "for", "with", "on", "at", "by", "from",
        "and", "but", "or", "not", "that", "this", "it", "its",
        "how", "what", "which", "who", "when", "where", "why",
    ])

    def classify(self, query: str, user_type: str = "researcher") -> QueryArchetype:
        """
        Classify a query into its archetype.

        Args:
            query: The user's question text
            user_type: One of: researcher, student, architect, reviewer, quick_lookup, deep_researcher

        Returns:
            QueryArchetype with topic_cluster, question_pattern, user_type
        """
        # 1. Detect question pattern
        question_pattern, pattern_confidence = self._detect_question_pattern(query)

        # 2. Classify topic cluster
        topic_cluster, topic_confidence, matched_keywords = self._classify_topic(query)

        # Combined confidence
        confidence = (pattern_confidence + topic_confidence) / 2

        archetype = QueryArchetype(
            topic_cluster=topic_cluster,
            question_pattern=question_pattern,
            user_type=user_type,
            confidence=confidence,
            matched_keywords=matched_keywords,
        )

        logger.info(
            f"QueryClassifier: '{query[:50]}...' → "
            f"{archetype.cache_key} (conf={confidence:.2f})"
        )

        return archetype

    def _detect_question_pattern(self, query: str) -> Tuple[str, float]:
        """Detect the question pattern using regex patterns."""
        query_lower = query.lower().strip()

        best_pattern = "EVIDENCE"  # Default
        best_confidence = 0.3

        for pattern_name, regexes in QUESTION_PATTERNS.items():
            for regex in regexes:
                if re.search(regex, query_lower):
                    return pattern_name, 0.85

        return best_pattern, best_confidence

    def _classify_topic(self, query: str) -> Tuple[str, float, List[str]]:
        """Classify the query into a topic cluster via keyword matching."""
        query_lower = query.lower()
        query_words = set(re.findall(r'\b[a-z]{3,}\b', query_lower)) - self._STOP_WORDS

        best_cluster = "general"
        best_score = 0.0
        best_keywords = []

        for cluster_name, cluster_info in TOPIC_CLUSTERS.items():
            keywords = cluster_info["keywords"]
            matched = []
            for kw in keywords:
                if " " in kw:
                    # Multi-word keyword: check substring
                    if kw in query_lower:
                        matched.append(kw)
                else:
                    if kw in query_words:
                        matched.append(kw)

            if matched:
                score = len(matched) / len(keywords)
                if score > best_score:
                    best_score = score
                    best_cluster = cluster_name
                    best_keywords = matched

        confidence = min(best_score * 3, 1.0)  # Scale up (3 keywords = full confidence)
        return best_cluster, confidence, best_keywords
