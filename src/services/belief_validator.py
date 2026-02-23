"""
Article Eater - Belief Validator
================================

Created: 2026-02-12
Purpose: Validate beliefs before insertion, ensure canonical IDs match BN mappings

Key Features:
1. Validate environment_id against BN_VARIABLE_MAPPINGS
2. Validate outcome_id against BN_VARIABLE_MAPPINGS
3. Suggest corrections for mismatched IDs
4. Enrich belief content with keywords for matching
5. Check belief completeness

Per Gap Resolution Improvements (2026-02-12):
- GR-1: Canonical ID validation
- GR-2: Keyword enrichment
"""

import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Import BN variable mappings
from src.services.edge_justification import BN_VARIABLE_MAPPINGS


@dataclass
class ValidationResult:
    """Result of belief validation."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: Dict[str, List[str]] = field(default_factory=dict)
    enriched_content: Optional[str] = None


class BeliefValidator:
    """
    Validates beliefs before insertion into the epistemic web.

    Ensures:
    1. Canonical IDs match BN variable mappings
    2. Content contains keywords that will match during edge justification
    3. Required fields are present
    """

    def __init__(self):
        """Initialize with BN variable mappings."""
        self._build_id_lookup()

    def _build_id_lookup(self):
        """Build lookup tables for valid IDs."""
        self.valid_env_ids: Set[str] = set()
        self.valid_outcome_ids: Set[str] = set()
        self.variable_keywords: Dict[str, List[str]] = {}

        for var_name, mapping in BN_VARIABLE_MAPPINGS.items():
            env_ids = mapping.get('environment_ids', [])
            out_ids = mapping.get('outcome_ids', [])
            keywords = mapping.get('keywords', [var_name])

            self.valid_env_ids.update(env_ids)
            self.valid_outcome_ids.update(out_ids)
            self.variable_keywords[var_name] = keywords

            # Also map IDs to keywords
            for eid in env_ids:
                self.variable_keywords[eid] = keywords
            for oid in out_ids:
                self.variable_keywords[oid] = keywords

    def validate(self, belief) -> ValidationResult:
        """
        Validate a belief before insertion.

        Args:
            belief: Belief object or dict with belief attributes

        Returns:
            ValidationResult with errors, warnings, and suggestions
        """
        result = ValidationResult()

        # Extract attributes (handle both Belief objects and dicts)
        if hasattr(belief, 'environment_id'):
            env_id = belief.environment_id
            out_id = belief.outcome_id
            content = belief.content
        else:
            env_id = belief.get('environment_id')
            out_id = belief.get('outcome_id')
            content = belief.get('content', '')

        # Validate environment_id
        if env_id:
            if env_id not in self.valid_env_ids:
                # Check if it's a simple name that should be canonical
                suggestions = self._suggest_canonical_id(env_id, 'environment')
                if suggestions:
                    result.warnings.append(
                        f"environment_id '{env_id}' not in BN mappings. "
                        f"Consider using: {', '.join(suggestions)}"
                    )
                    result.suggestions['environment_id'] = suggestions
                else:
                    result.warnings.append(
                        f"environment_id '{env_id}' not recognized in BN mappings"
                    )

        # Validate outcome_id
        if out_id:
            if out_id not in self.valid_outcome_ids:
                suggestions = self._suggest_canonical_id(out_id, 'outcome')
                if suggestions:
                    result.warnings.append(
                        f"outcome_id '{out_id}' not in BN mappings. "
                        f"Consider using: {', '.join(suggestions)}"
                    )
                    result.suggestions['outcome_id'] = suggestions
                else:
                    result.warnings.append(
                        f"outcome_id '{out_id}' not recognized in BN mappings"
                    )

        # Check keyword matching
        keyword_warnings = self._check_keyword_coverage(content, env_id, out_id)
        result.warnings.extend(keyword_warnings)

        # Suggest enriched content if keywords missing
        if keyword_warnings:
            enriched = self._enrich_content(content, env_id, out_id)
            if enriched != content:
                result.enriched_content = enriched

        # Check required fields
        if not content or len(content) < 20:
            result.errors.append("Content is missing or too short (min 20 chars)")
            result.is_valid = False

        # Set overall validity
        if result.errors:
            result.is_valid = False

        return result

    def _suggest_canonical_id(self, simple_id: str, id_type: str) -> List[str]:
        """
        Suggest canonical IDs for a simple/non-canonical ID.

        Args:
            simple_id: The ID used (e.g., 'noise', 'stress')
            id_type: 'environment' or 'outcome'

        Returns:
            List of suggested canonical IDs
        """
        suggestions = []
        simple_lower = simple_id.lower()

        for var_name, mapping in BN_VARIABLE_MAPPINGS.items():
            # Check if simple_id matches the variable name
            if simple_lower == var_name.lower():
                if id_type == 'environment':
                    suggestions.extend(mapping.get('environment_ids', []))
                else:
                    suggestions.extend(mapping.get('outcome_ids', []))

            # Check if simple_id matches any keywords
            keywords = mapping.get('keywords', [])
            if any(simple_lower in kw.lower() or kw.lower() in simple_lower
                   for kw in keywords):
                if id_type == 'environment':
                    suggestions.extend(mapping.get('environment_ids', []))
                else:
                    suggestions.extend(mapping.get('outcome_ids', []))

        return list(set(suggestions))  # Deduplicate

    def _check_keyword_coverage(
        self,
        content: str,
        env_id: Optional[str],
        out_id: Optional[str]
    ) -> List[str]:
        """
        Check if content contains keywords that will match during edge justification.

        Returns:
            List of warnings about missing keywords
        """
        warnings = []
        content_lower = content.lower() if content else ""

        # Check environment keywords
        if env_id:
            env_keywords = self._get_keywords_for_id(env_id)
            if env_keywords and not any(kw.lower() in content_lower for kw in env_keywords):
                warnings.append(
                    f"Content missing keywords for environment '{env_id}'. "
                    f"Consider including: {', '.join(env_keywords[:3])}"
                )

        # Check outcome keywords
        if out_id:
            out_keywords = self._get_keywords_for_id(out_id)
            if out_keywords and not any(kw.lower() in content_lower for kw in out_keywords):
                warnings.append(
                    f"Content missing keywords for outcome '{out_id}'. "
                    f"Consider including: {', '.join(out_keywords[:3])}"
                )

        return warnings

    def _get_keywords_for_id(self, var_id: str) -> List[str]:
        """Get keywords associated with a variable ID."""
        # Direct lookup
        if var_id in self.variable_keywords:
            return self.variable_keywords[var_id]

        # Search in mappings
        for var_name, mapping in BN_VARIABLE_MAPPINGS.items():
            env_ids = mapping.get('environment_ids', [])
            out_ids = mapping.get('outcome_ids', [])
            if var_id in env_ids or var_id in out_ids:
                return mapping.get('keywords', [var_name])

        return []

    def _enrich_content(
        self,
        content: str,
        env_id: Optional[str],
        out_id: Optional[str]
    ) -> str:
        """
        Enrich content with keywords to improve matching.

        Appends a parenthetical note with relevant keywords if missing.
        """
        content_lower = content.lower()
        additions = []

        # Check environment
        if env_id:
            env_keywords = self._get_keywords_for_id(env_id)
            if env_keywords:
                present = [kw for kw in env_keywords if kw.lower() in content_lower]
                if not present:
                    additions.append(env_keywords[0])

        # Check outcome
        if out_id:
            out_keywords = self._get_keywords_for_id(out_id)
            if out_keywords:
                present = [kw for kw in out_keywords if kw.lower() in content_lower]
                if not present:
                    additions.append(out_keywords[0])

        if additions:
            return f"{content} [Keywords: {', '.join(additions)}]"
        return content

    def get_valid_environment_ids(self) -> List[str]:
        """Return all valid environment IDs."""
        return sorted(self.valid_env_ids)

    def get_valid_outcome_ids(self) -> List[str]:
        """Return all valid outcome IDs."""
        return sorted(self.valid_outcome_ids)

    def get_variable_keywords(self, variable_name: str) -> List[str]:
        """Get keywords for a BN variable name."""
        mapping = BN_VARIABLE_MAPPINGS.get(variable_name.lower(), {})
        return mapping.get('keywords', [variable_name])


# Singleton instance
_validator: Optional[BeliefValidator] = None


def get_belief_validator() -> BeliefValidator:
    """Get or create the belief validator singleton."""
    global _validator
    if _validator is None:
        _validator = BeliefValidator()
    return _validator


def validate_belief(belief) -> ValidationResult:
    """
    Convenience function to validate a belief.

    Args:
        belief: Belief object or dict

    Returns:
        ValidationResult
    """
    return get_belief_validator().validate(belief)
