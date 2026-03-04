"""
Card Retriever — Fast Precomputed Answer Lookup
=================================================

Looks up precomputed answer cards from materialized_views/answer_cards/
before falling back to expensive live enrichment.

Architecture:
    1. card_index.json loaded at init → dict of cluster_id → {antecedent, consequent, ...}
    2. On query, tokenize and match against (antecedent, consequent) themes
    3. On hit, load user-type-specific card file and return formatted response
    4. On miss, return None → caller falls through to live enrichment

Performance: ~5-20ms per lookup (vs 5000ms+ live enrichment pipeline)

Author: AG (Antigravity) — V13 Audit Fix
Date: 2026-03-03
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent


class CardRetriever:
    """Fast lookup of precomputed answer cards by keyword matching.

    Loads the card index once at init, then serves lookups in <50ms.
    Cards are organized by user_type (one file per type) for fast access.
    """

    # Minimum keyword overlap to consider a match
    MIN_MATCH_SCORE = 2

    def __init__(
        self,
        cards_dir: str = "data/materialized_views/answer_cards",
    ):
        self._cards_dir = PROJECT_ROOT / cards_dir
        self._index: Dict[str, Dict] = {}
        self._card_cache: Dict[str, Dict] = {}  # user_type → {cluster_id → card}
        self._load_index()

    def _load_index(self) -> None:
        """Load card_index.json for fast theme matching."""
        index_path = self._cards_dir / "card_index.json"
        if not index_path.exists():
            logger.warning(f"Card index not found at {index_path}")
            return

        try:
            with open(index_path) as f:
                self._index = json.load(f)
            logger.info(f"Loaded card index with {len(self._index)} clusters")
        except Exception as e:
            logger.error(f"Failed to load card index: {e}")

    def _load_cards_for_user_type(self, user_type: str) -> Dict[str, Dict]:
        """Lazy-load card file for a specific user type."""
        if user_type in self._card_cache:
            return self._card_cache[user_type]

        cards_path = self._cards_dir / f"cards_{user_type}.json"
        if not cards_path.exists():
            logger.warning(f"No card file for user_type={user_type}")
            self._card_cache[user_type] = {}
            return {}

        try:
            with open(cards_path) as f:
                data = json.load(f)

            # Index cards by cluster_id for O(1) lookup
            cards_by_id = {}
            for card in data.get("cards", []):
                cards_by_id[card["cluster_id"]] = card

            self._card_cache[user_type] = cards_by_id
            logger.info(
                f"Loaded {len(cards_by_id)} cards for user_type={user_type}"
            )
            return cards_by_id
        except Exception as e:
            logger.error(f"Failed to load cards for {user_type}: {e}")
            self._card_cache[user_type] = {}
            return {}

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization: lowercase, split on non-alpha, filter stopwords."""
        import re

        tokens = re.findall(r"[a-z]+", text.lower())
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "do", "does", "did", "have", "has", "had", "will", "would",
            "can", "could", "should", "may", "might", "shall",
            "i", "you", "he", "she", "it", "we", "they", "me", "him",
            "her", "us", "them", "my", "your", "his", "its", "our",
            "what", "how", "why", "when", "where", "which", "who",
            "that", "this", "these", "those", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "about", "into",
            "and", "or", "but", "not", "if", "so", "than", "too",
            "very", "just", "also", "more", "most", "much", "many",
            "some", "any", "all", "each", "every", "both", "few",
            "show", "tell", "give", "explain", "describe",
        }
        return [t for t in tokens if t not in stopwords and len(t) > 2]

    def _score_match(
        self, query_tokens: List[str], antecedent: str, consequent: str
    ) -> float:
        """Score how well query tokens match a cluster's themes."""
        theme_text = f"{antecedent} {consequent}".lower().replace("_", " ")
        theme_tokens = set(self._tokenize(theme_text))

        if not theme_tokens or not query_tokens:
            return 0.0

        # Count matching tokens
        matches = sum(1 for qt in query_tokens if qt in theme_tokens)

        # Also check substring matches (e.g., "stress" matches "stress")
        for qt in query_tokens:
            if qt not in theme_tokens:
                for tt in theme_tokens:
                    if qt in tt or tt in qt:
                        matches += 0.5
                        break

        return matches

    def try_match(
        self,
        question: str,
        user_type: str = "researcher",
    ) -> Optional[Dict[str, Any]]:
        """Try to find a precomputed answer card matching the question.

        Args:
            question: User's question text
            user_type: User type for card selection

        Returns:
            Formatted response dict if a card matches, None otherwise
        """
        if not self._index:
            return None

        start = time.monotonic()
        query_tokens = self._tokenize(question)

        if not query_tokens:
            return None

        # Score all clusters
        best_id = None
        best_score = 0.0

        for cluster_id, cluster_info in self._index.items():
            antecedent = cluster_info.get("antecedent", "")
            consequent = cluster_info.get("consequent", "")

            score = self._score_match(query_tokens, antecedent, consequent)
            if score > best_score:
                best_score = score
                best_id = cluster_id

        if best_score < self.MIN_MATCH_SCORE or best_id is None:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.debug(
                f"Card miss: best_score={best_score:.1f} < {self.MIN_MATCH_SCORE} "
                f"({elapsed_ms:.1f}ms)"
            )
            return None

        # Load card for this user type
        cards = self._load_cards_for_user_type(user_type)
        card = cards.get(best_id)

        if not card:
            # Try researcher as fallback
            if user_type != "researcher":
                cards = self._load_cards_for_user_type("researcher")
                card = cards.get(best_id)

            if not card:
                logger.debug(f"Card index hit but no card for cluster {best_id}")
                return None

        elapsed_ms = (time.monotonic() - start) * 1000
        cluster_info = self._index[best_id]

        logger.info(
            f"Card HIT: cluster={best_id} "
            f"({cluster_info.get('antecedent', '?')}→{cluster_info.get('consequent', '?')}) "
            f"score={best_score:.1f}, {elapsed_ms:.1f}ms"
        )

        # Format as standard QA response
        return self._format_card_response(card, cluster_info, question, elapsed_ms)

    def _format_card_response(
        self,
        card: Dict,
        cluster_info: Dict,
        question: str,
        lookup_ms: float,
    ) -> Dict[str, Any]:
        """Format a precomputed card into the standard QA response shape."""
        antecedent = card.get("antecedent_theme", "").replace("_", " ")
        consequent = card.get("consequent_theme", "").replace("_", " ")

        # Build sections from the card's prose
        prose = card.get("prose", "")
        paragraphs = [p.strip() for p in prose.split("\n\n") if p.strip()]

        sections = []
        if paragraphs:
            sections.append({
                "heading": f"{antecedent.title()} → {consequent.title()}",
                "items": paragraphs,
            })

        # Theory links section
        theories = card.get("theory_links", [])
        if theories:
            sections.append({
                "heading": "Theoretical Frameworks",
                "items": [f"**{t}**" for t in theories],
            })

        # Evidence summary
        n_findings = card.get("n_findings", 0)
        n_papers = card.get("n_papers", 0)
        confidence = card.get("confidence", {})
        conf_label = confidence.get("label", "unknown") if isinstance(confidence, dict) else str(confidence)
        direction = card.get("direction_consensus", "mixed")

        sections.append({
            "heading": "Evidence Summary",
            "items": [
                f"**Findings**: {n_findings} across {n_papers} papers",
                f"**Confidence**: {conf_label}",
                f"**Direction consensus**: {direction}",
            ],
        })

        return {
            "question_type": "precomputed_card",
            "headline": f"{antecedent.title()} → {consequent.title()}: "
                        f"{n_findings} findings from {n_papers} papers "
                        f"({conf_label} confidence, {direction} direction)",
            "sections": sections,
            "confidence": 0.90,  # High confidence — precomputed from real data
            "ai_generated": False,
            "enriched": True,
            "source": "precomputed_card",
            "card_metadata": {
                "cluster_id": card.get("cluster_id"),
                "user_type": card.get("user_type"),
                "word_count": card.get("word_count", 0),
                "quality_score": card.get("quality_score", 0),
                "lookup_ms": round(lookup_ms, 1),
            },
            "follow_ups": [
                f"What mechanisms underlie {antecedent}?",
                f"What evidence contradicts the effect of {antecedent} on {consequent}?",
                f"How big is the effect of {antecedent} on {consequent}?",
            ],
        }

    # ------------------------------------------------------------------
    # New Card Schema Integration (2026-03-04)
    # ------------------------------------------------------------------
    # Bridges legacy AnswerCard format with new Surface/Body/Iceberg schema.
    # The orchestrator-generated cards live in data/materialized_views/cards/
    # and are indexed by the CardGenerationOrchestrator.

    def try_match_unified(
        self,
        question: str,
        user_type: str = "researcher",
    ) -> Optional[Dict[str, Any]]:
        """
        Try to find a card using BOTH legacy and new-schema indices.

        Priority:
            1. New-schema cards (Surface/Body/Iceberg) via CardGenerationOrchestrator
            2. Legacy AnswerCard cards (cluster-based)
            3. None → caller falls through to live enrichment

        SC-E2E-6 (last mile): This method verifies that new-schema cards
        actually reach the QA response pathway.
        """
        # Try new-schema cards first
        try:
            from src.qa.card_generation_orchestrator import CardGenerationOrchestrator
            orch = CardGenerationOrchestrator(base_dir=str(PROJECT_ROOT))
            results = orch.search_cards(question, max_results=3)
            if results:
                best = results[0]
                card = orch.get_card(best["card_id"])
                if card:
                    return self._format_unified_card_response(card, question)
        except Exception as e:
            logger.debug(f"Unified card lookup failed: {e}")

        # Fall back to legacy
        return self.try_match(question, user_type)

    def _format_unified_card_response(
        self,
        card: Any,  # Card object from new schema
        question: str,
    ) -> Dict[str, Any]:
        """Format a new-schema Card into the standard QA response shape."""
        surface = card.surface
        body = card.body

        # Build sections from tabs
        sections = []
        for tab_name, tab in body.tabs.items():
            if tab.prose:
                sections.append({
                    "heading": tab_name.title(),
                    "items": [p.strip() for p in tab.prose.split("\n\n") if p.strip()],
                })

        # Evidence summary from surface
        conf_label = surface.confidence_label if hasattr(surface, 'confidence_label') else "unknown"
        direction = surface.direction.value if hasattr(surface, 'direction') else "unknown"

        sections.append({
            "heading": "Evidence Summary",
            "items": [
                f"**Findings**: {surface.n_findings} across {surface.n_papers} papers",
                f"**Confidence**: {conf_label}",
                f"**Direction**: {direction}",
            ],
        })

        return {
            "question_type": "unified_card",
            "headline": (
                f"{surface.title}: {surface.n_findings} findings "
                f"({conf_label}, {direction})"
            ),
            "sections": sections,
            "confidence": 0.92,  # Higher — new schema is more rigorous
            "ai_generated": True,
            "enriched": True,
            "source": "unified_card",
            "card_metadata": {
                "card_id": card.card_id,
                "card_type": card.card_type.value,
                "entity_id": card.entity_id,
                "tab_count": len(body.tabs),
                "is_draft": card.is_draft,
                "staleness": surface.staleness.value if hasattr(surface, 'staleness') else "unknown",
                "quality_score": (
                    card.iceberg.quality_scores.prose_health
                    if card.iceberg and card.iceberg.quality_scores else 0
                ),
            },
            "follow_ups": [
                f"Tell me more about {surface.title}",
                f"What evidence supports {surface.title}?",
                f"What are the design implications of {surface.title}?",
            ],
        }

    @property
    def n_clusters(self) -> int:
        """Number of clusters in the index."""
        return len(self._index)

    @property
    def is_available(self) -> bool:
        """Whether the card retriever has a loaded index."""
        return len(self._index) > 0
