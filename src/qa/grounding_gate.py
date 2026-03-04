"""
Grounding Gate — Haack's Foundherentist Pre-Query Filter
=========================================================

Implements the principle: "No answer without evidence."

Before any enrichment runs, this gate checks:
  1. GROUNDING: Does the query have ≥1 empirical finding from the corpus?
  2. COHERENCE: Does the answer contradict established beliefs?
  3. VERDICT:   answer | abstain | flag_contradiction

If grounding fails, the system returns an explicit "I don't know" rather
than a confident template answer with zero evidence.

Usage:
    gate = GroundingGate()
    result = gate.check("Do natural environments enhance restoration?")
    if result.should_abstain:
        return AbstentionResponse(result.reason)
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class EmpiricalAnchor:
    """A single empirical finding that grounds the query."""
    source_file: str
    article_type: str
    antecedent: str
    consequent: str
    direction: str
    p_value: Optional[str] = None
    effect_size: Optional[float] = None
    theory_links: List[str] = field(default_factory=list)
    relevance_score: float = 0.0


@dataclass
class GroundingResult:
    """Result of the grounding gate check."""
    has_empirical_anchor: bool
    n_supporting_findings: int
    anchors: List[EmpiricalAnchor] = field(default_factory=list)
    coherence_status: str = "unknown"  # "consistent" | "contradicted" | "unknown"
    contradictions: List[Dict] = field(default_factory=list)
    should_abstain: bool = False
    reason: str = ""
    grounding_time_ms: float = 0.0

    @property
    def recommendation(self) -> str:
        if self.should_abstain:
            return "abstain"
        if self.contradictions:
            return "flag_contradiction"
        return "answer"


@dataclass
class AbstentionResponse:
    """Explicit 'I don't know' response when grounding fails."""
    reason: str
    confidence: float = 0.0
    suggestion: str = ""

    def to_dict(self) -> Dict:
        return {
            "abstention": True,
            "reason": self.reason,
            "confidence": self.confidence,
            "suggestion": self.suggestion,
            "message": (
                "This question cannot be answered with sufficient evidence "
                "from the current corpus. " + self.suggestion
            ),
        }


# ---------------------------------------------------------------------------
# Grounding Gate
# ---------------------------------------------------------------------------

class GroundingGate:
    """
    Pre-query evidence gate implementing Haack's foundherentist principle.

    Searches the extraction corpus (data/extractions/) for empirical findings
    that anchor the query before allowing enrichment to proceed.
    """

    def __init__(
        self,
        extractions_dir: str = "data/extractions",
        min_anchors: int = 1,
        relevance_threshold: float = 0.3,
    ):
        self._extractions_dir = Path(extractions_dir)
        self._min_anchors = min_anchors
        self._relevance_threshold = relevance_threshold
        self._corpus_loaded = False
        self._corpus: List[Dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check(self, query: str, beliefs: Optional[List[Dict]] = None) -> GroundingResult:
        """
        Check whether a query has empirical grounding in the corpus.

        Args:
            query: The user's question text
            beliefs: Optional existing beliefs from the web (for coherence check)

        Returns:
            GroundingResult with anchors, coherence status, and recommendation
        """
        import time
        start = time.time()

        # Extract keywords from the query
        keywords = self._extract_keywords(query)
        if not keywords:
            elapsed = (time.time() - start) * 1000
            return GroundingResult(
                has_empirical_anchor=False,
                n_supporting_findings=0,
                should_abstain=True,
                reason="Could not extract meaningful keywords from query",
                grounding_time_ms=elapsed,
            )

        # Search the corpus for empirical anchors
        anchors = self._search_corpus(keywords)

        # Check coherence if beliefs are provided
        coherence_status = "unknown"
        contradictions = []
        if beliefs and anchors:
            coherence_status, contradictions = self._check_coherence(anchors, beliefs)

        # Determine verdict
        has_anchor = len(anchors) >= self._min_anchors
        should_abstain = not has_anchor

        elapsed = (time.time() - start) * 1000

        if should_abstain:
            reason = (
                f"No empirical findings found for query keywords {keywords[:5]}. "
                f"The corpus has no evidence to ground an answer."
            )
        elif contradictions:
            reason = (
                f"Found {len(anchors)} supporting findings but "
                f"{len(contradictions)} contradictions in the belief web."
            )
        else:
            reason = f"Grounded: {len(anchors)} empirical findings support this query."

        logger.info(
            f"GroundingGate: query='{query[:50]}...' "
            f"keywords={keywords[:5]} anchors={len(anchors)} "
            f"abstain={should_abstain} elapsed={elapsed:.1f}ms"
        )

        return GroundingResult(
            has_empirical_anchor=has_anchor,
            n_supporting_findings=len(anchors),
            anchors=anchors[:10],  # Return top 10
            coherence_status=coherence_status,
            contradictions=contradictions,
            should_abstain=should_abstain,
            reason=reason,
            grounding_time_ms=elapsed,
        )

    def build_abstention_response(self, query: str, result: GroundingResult) -> AbstentionResponse:
        """Build explicit 'I don't know' response."""
        # Suggest what the user could look for
        keywords = self._extract_keywords(query)
        suggestion = (
            f"Try searching for related topics: {', '.join(keywords[:3])}. "
            f"Or consider adding relevant papers to the corpus."
        )
        return AbstentionResponse(
            reason=result.reason,
            confidence=0.0,
            suggestion=suggestion,
        )

    # ------------------------------------------------------------------
    # Corpus search
    # ------------------------------------------------------------------

    def _ensure_corpus_loaded(self):
        """Lazy-load the extraction corpus."""
        if self._corpus_loaded:
            return
        if not self._extractions_dir.exists():
            logger.warning(f"Extractions directory not found: {self._extractions_dir}")
            self._corpus_loaded = True
            return

        count = 0
        for json_file in self._extractions_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                # Get findings (different keys for different article types)
                findings = (
                    data.get("findings", [])
                    or data.get("pooled_effects", [])
                    or data.get("propositions", [])
                    or data.get("themes", [])
                    or data.get("key_claims", [])
                )
                if not findings:
                    continue

                article_type = data.get("article_type", "unknown")
                for finding in findings:
                    self._corpus.append({
                        "source_file": json_file.name,
                        "article_type": article_type,
                        "antecedent": finding.get("antecedent", ""),
                        "consequent": finding.get("consequent", ""),
                        "direction": finding.get("direction", ""),
                        "p_value": finding.get("p_value"),
                        "effect_size": finding.get("effect_size"),
                        "theory_links": finding.get("theory_links", []),
                        "finding_text": finding.get("finding_text", ""),
                        "quote": finding.get("quote", ""),
                        # Build searchable text
                        "_search_text": " ".join(filter(None, [
                            finding.get("antecedent", ""),
                            finding.get("consequent", ""),
                            finding.get("mechanism", ""),
                            finding.get("quote", ""),
                            finding.get("finding_text", ""),
                        ])).lower(),
                    })
                    count += 1
            except (json.JSONDecodeError, Exception) as e:
                logger.debug(f"Skipping {json_file.name}: {e}")

        self._corpus_loaded = True
        logger.info(f"GroundingGate: loaded {count} findings from {self._extractions_dir}")

    def _search_corpus(self, keywords: List[str]) -> List[EmpiricalAnchor]:
        """Search the corpus for findings matching the keywords."""
        self._ensure_corpus_loaded()

        scored_matches = []
        keywords_lower = [k.lower() for k in keywords]

        for entry in self._corpus:
            search_text = entry.get("_search_text", "")
            if not search_text:
                continue

            # Score by keyword overlap
            matched = sum(1 for kw in keywords_lower if kw in search_text)
            if matched == 0:
                continue

            relevance = matched / len(keywords_lower)
            if relevance < self._relevance_threshold:
                continue

            anchor = EmpiricalAnchor(
                source_file=entry["source_file"],
                article_type=entry["article_type"],
                antecedent=entry["antecedent"],
                consequent=entry["consequent"],
                direction=entry["direction"],
                p_value=entry.get("p_value"),
                effect_size=entry.get("effect_size"),
                theory_links=entry.get("theory_links", []),
                relevance_score=relevance,
            )
            scored_matches.append(anchor)

        # Sort by relevance, return top matches
        scored_matches.sort(key=lambda a: a.relevance_score, reverse=True)
        return scored_matches[:50]

    # ------------------------------------------------------------------
    # Coherence check
    # ------------------------------------------------------------------

    def _check_coherence(
        self, anchors: List[EmpiricalAnchor], beliefs: List[Dict]
    ) -> Tuple[str, List[Dict]]:
        """
        Check if empirical anchors contradict established beliefs.

        Returns:
            (status, contradictions) where status is "consistent" or "contradicted"
        """
        contradictions = []

        for anchor in anchors[:10]:  # Check top 10 anchors
            for belief in beliefs:
                belief_text = belief.get("text", "").lower()
                anchor_text = f"{anchor.antecedent} {anchor.consequent}".lower()

                # Simple direction contradiction check
                if (
                    anchor.direction == "increase"
                    and "decrease" in belief_text
                    and self._texts_overlap(anchor_text, belief_text)
                ):
                    contradictions.append({
                        "anchor_source": anchor.source_file,
                        "anchor_direction": anchor.direction,
                        "belief_text": belief.get("text", "")[:100],
                        "conflict_type": "direction_mismatch",
                    })
                elif (
                    anchor.direction == "decrease"
                    and "increase" in belief_text
                    and self._texts_overlap(anchor_text, belief_text)
                ):
                    contradictions.append({
                        "anchor_source": anchor.source_file,
                        "anchor_direction": anchor.direction,
                        "belief_text": belief.get("text", "")[:100],
                        "conflict_type": "direction_mismatch",
                    })

        status = "contradicted" if contradictions else "consistent"
        return status, contradictions

    # ------------------------------------------------------------------
    # Text utilities
    # ------------------------------------------------------------------

    _STOP_WORDS = frozenset([
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can",
        "of", "in", "to", "for", "with", "on", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "and",
        "but", "or", "nor", "not", "so", "that", "this", "these",
        "those", "what", "which", "who", "whom", "how", "when",
        "where", "why", "between", "about", "than", "its", "it",
        "their", "they", "them", "more", "less", "much", "many",
        "each", "every", "all", "any", "both", "few", "some",
        "effect", "effects", "impact", "influence", "study", "research",
    ])

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text, removing stop words."""
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        keywords = [w for w in words if w not in self._STOP_WORDS]
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)
        return unique

    def _texts_overlap(self, text_a: str, text_b: str) -> bool:
        """Check if two texts share meaningful keyword overlap."""
        words_a = set(self._extract_keywords(text_a))
        words_b = set(self._extract_keywords(text_b))
        overlap = words_a & words_b
        return len(overlap) >= 2
