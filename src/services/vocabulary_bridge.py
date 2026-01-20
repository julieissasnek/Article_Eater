"""
Vocabulary Bridge for Interpretive Intelligence.

Sprint E: TODO 2 Implementation

Per Bates: Map between internal, academic, practitioner, and common terms.
This enables the system to understand user queries regardless of vocabulary
and respond in appropriate language for the user's expertise level.

Date: January 20, 2026
"""

import logging
import yaml
from pathlib import Path
from typing import List, Dict, Set, Optional, Any

from src.services.web_of_belief import WebOfBelief, Belief

logger = logging.getLogger(__name__)


class VocabularyBridge:
    """
    Translate between vocabulary domains.

    Handles bidirectional mapping between:
    - Internal IDs (used in code/database)
    - Academic terms (research papers)
    - Practitioner terms (professionals)
    - Common terms (general users)
    """

    def __init__(self, vocab_path: str):
        """
        Initialize vocabulary bridge.

        Args:
            vocab_path: Path to vocabulary_bridge.yaml
        """
        self.vocab_path = vocab_path
        self.vocab = self._load_vocab(vocab_path)
        self._build_indices()

    def _load_vocab(self, vocab_path: str) -> Dict[str, Any]:
        """Load vocabulary from YAML file."""
        path = Path(vocab_path)
        if not path.exists():
            logger.warning(f"Vocabulary file not found: {vocab_path}")
            return {"concepts": {}, "relationships": {}}

        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def _build_indices(self) -> None:
        """Build reverse indices for fast lookup."""
        self.common_to_internal: Dict[str, str] = {}
        self.academic_to_internal: Dict[str, str] = {}
        self.practitioner_to_internal: Dict[str, str] = {}
        self.internal_to_concept: Dict[str, str] = {}

        for concept_id, concept in self.vocab.get("concepts", {}).items():
            internal = concept.get("internal", concept_id)
            self.internal_to_concept[internal] = concept_id

            # Index common terms
            for term in concept.get("common", []):
                self.common_to_internal[term.lower()] = internal

            # Index academic terms
            for term in concept.get("academic", []):
                self.academic_to_internal[term.lower()] = internal

            # Index practitioner terms
            for term in concept.get("practitioner", []):
                self.practitioner_to_internal[term.lower()] = internal

    def query_to_internal(self, query: str) -> List[str]:
        """
        Map user query terms to internal IDs.

        Per Bates: Handle vocabulary mismatch gracefully.

        Args:
            query: User query string

        Returns:
            List of matching internal IDs
        """
        query_lower = query.lower()
        matches: Set[str] = set()

        # Check each index for substring matches
        for index in [self.common_to_internal, self.practitioner_to_internal, self.academic_to_internal]:
            for term, internal in index.items():
                if term in query_lower:
                    matches.add(internal)

        return list(matches)

    def internal_to_user(
        self,
        internal_id: str,
        expertise_level: str = "practitioner"
    ) -> str:
        """
        Convert internal term to user-appropriate term.

        Args:
            internal_id: Internal concept ID
            expertise_level: "novice", "practitioner", or "researcher"

        Returns:
            User-friendly term for the concept
        """
        concept_id = self.internal_to_concept.get(internal_id)
        if not concept_id:
            return internal_id  # Return as-is if not found

        concept = self.vocab.get("concepts", {}).get(concept_id, {})

        if expertise_level == "novice":
            terms = concept.get("common", [])
        elif expertise_level == "researcher":
            terms = concept.get("academic", [])
        else:  # practitioner
            terms = concept.get("practitioner", [])

        if terms:
            return terms[0]

        # Fallback through hierarchy
        for key in ["practitioner", "common", "academic"]:
            fallback_terms = concept.get(key, [])
            if fallback_terms:
                return fallback_terms[0]

        return internal_id

    def find_related_beliefs(
        self,
        query: str,
        web: WebOfBelief
    ) -> List[Belief]:
        """
        Find beliefs related to query terms.

        Uses vocabulary mapping to expand the search beyond
        exact matches.

        Args:
            query: User query string
            web: Web of belief to search

        Returns:
            List of related beliefs, sorted by relevance
        """
        # Get internal IDs from query
        internal_ids = self.query_to_internal(query)

        # Also do simple keyword matching for coverage
        query_words = set(query.lower().split())
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                    'to', 'of', 'in', 'for', 'on', 'with', 'that', 'this', 'it',
                    'what', 'how', 'why', 'does', 'do', 'can', 'should'}
        query_words -= stopwords

        related: List[tuple] = []

        for belief_id, belief in web.beliefs.items():
            score = 0

            # Check if belief content contains query words
            content_lower = belief.content.lower()
            content_words = set(content_lower.split()) - stopwords
            word_overlap = len(query_words & content_words)

            if word_overlap > 0:
                score += word_overlap * 2

            # Check if belief matches vocabulary concepts
            for internal_id in internal_ids:
                # Check environment_id or outcome_id if present
                if hasattr(belief, 'environment_id') and belief.environment_id:
                    if internal_id in belief.environment_id:
                        score += 3
                if hasattr(belief, 'outcome_id') and belief.outcome_id:
                    if internal_id in belief.outcome_id:
                        score += 3

                # Check content for vocabulary terms
                concept_id = self.internal_to_concept.get(internal_id)
                if concept_id:
                    concept = self.vocab.get("concepts", {}).get(concept_id, {})
                    for term_list in [concept.get("common", []),
                                     concept.get("practitioner", []),
                                     concept.get("academic", [])]:
                        for term in term_list:
                            if term.lower() in content_lower:
                                score += 2
                                break

            if score > 0:
                related.append((belief, score))

        # Sort by score descending
        related.sort(key=lambda x: x[1], reverse=True)

        return [belief for belief, score in related]

    def expand_query(self, query: str) -> List[str]:
        """
        Expand a query with related terms.

        Useful for search engines or more comprehensive matching.

        Args:
            query: Original query

        Returns:
            List of expanded terms
        """
        expanded = [query]
        internal_ids = self.query_to_internal(query)

        for internal_id in internal_ids:
            concept_id = self.internal_to_concept.get(internal_id)
            if not concept_id:
                continue

            concept = self.vocab.get("concepts", {}).get(concept_id, {})

            # Add all synonyms
            for key in ["academic", "practitioner", "common"]:
                terms = concept.get(key, [])
                expanded.extend(terms)

            # Add related concepts from relationships
            relationships = self.vocab.get("relationships", {}).get(concept_id, {})
            for related_id in relationships.get("related_outcomes", []):
                expanded.append(related_id)
            for related_id in relationships.get("related_environments", []):
                expanded.append(related_id)

        return list(set(expanded))

    def get_concept_info(self, query_term: str) -> Optional[Dict[str, Any]]:
        """
        Get full concept info for a term.

        Args:
            query_term: Term to look up

        Returns:
            Concept dictionary or None if not found
        """
        # First try to find the internal ID
        internal_id = None
        query_lower = query_term.lower()

        for index in [self.common_to_internal, self.practitioner_to_internal, self.academic_to_internal]:
            if query_lower in index:
                internal_id = index[query_lower]
                break

        if not internal_id:
            return None

        concept_id = self.internal_to_concept.get(internal_id)
        if not concept_id:
            return None

        return self.vocab.get("concepts", {}).get(concept_id)

    def translate_explanation(
        self,
        text: str,
        target_expertise: str = "practitioner"
    ) -> str:
        """
        Translate technical terms in explanation to target expertise level.

        Args:
            text: Original explanation text
            target_expertise: "novice", "practitioner", or "researcher"

        Returns:
            Translated text with appropriate vocabulary
        """
        result = text

        # Build a mapping from all terms to target-level terms
        replacements: Dict[str, str] = {}

        for concept_id, concept in self.vocab.get("concepts", {}).items():
            internal_id = concept.get("internal", concept_id)
            target_term = self.internal_to_user(internal_id, target_expertise)

            # Map academic terms to target
            for term in concept.get("academic", []):
                if term.lower() != target_term.lower():
                    replacements[term] = target_term

            # For novice, also map practitioner terms
            if target_expertise == "novice":
                for term in concept.get("practitioner", []):
                    if term.lower() != target_term.lower():
                        replacements[term] = target_term

        # Apply replacements (case-insensitive)
        for source_term, target_term in replacements.items():
            # Simple replacement - could be improved with regex for word boundaries
            if source_term.lower() in result.lower():
                # Find the actual case and replace
                import re
                pattern = re.compile(re.escape(source_term), re.IGNORECASE)
                result = pattern.sub(target_term, result)

        return result


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_vocabulary_bridge(vocab_path: Optional[str] = None) -> VocabularyBridge:
    """
    Create a vocabulary bridge instance.

    Args:
        vocab_path: Path to vocabulary file. If None, uses default location.

    Returns:
        VocabularyBridge instance
    """
    if vocab_path is None:
        # Default to contracts/vocab/vocabulary_bridge.yaml
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        vocab_path = os.path.join(project_root, "contracts", "vocab", "vocabulary_bridge.yaml")

    return VocabularyBridge(vocab_path)
