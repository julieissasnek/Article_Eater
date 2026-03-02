"""
t3_interp_bridge.py — T3 → Interpretation Space Bridge
=======================================================

Feeds T3 belief engine outputs into the interpretation space pipeline:
  1. Coverage gaps → search suggestions (gap_predictor source)
  2. Nascent beliefs → search seeds (t3_nascent source)
  3. Contested beliefs → argumentation targets (t3_contested source)
  4. Established beliefs with low confidence → validation targets

Sprint S2-1: Wires T3 layer into interpretation space loop.
"""

import logging
from typing import Dict, List, Optional, Any

from src.services.generalization_tree import (
    GeneralizationEngine, T3Belief, BeliefStatus, CoverageGap,
)
from src.services.interpretation_space_suggestions import (
    InterpretationSpaceSuggestionsManager, SuggestionRecord,
)

LOGGER = logging.getLogger(__name__)


class T3InterpBridge:
    """
    Bridges T3 empirical beliefs into the interpretation space pipeline.

    Converts T3 outputs (gaps, nascent beliefs, contested beliefs)
    into actionable search suggestions for the evidence acquisition loop.
    """

    # Priority weights for different suggestion types
    PRIORITY_GAP = 0.75          # Coverage gaps are high priority
    PRIORITY_NASCENT = 0.65      # Single-article seeds need replication
    PRIORITY_CONTESTED = 0.80    # Contested beliefs need resolution
    PRIORITY_VALIDATION = 0.60   # Low-confidence established beliefs need validation

    def __init__(
        self,
        engine: GeneralizationEngine,
        suggestion_manager: InterpretationSpaceSuggestionsManager,
    ):
        self.engine = engine
        self.suggestions = suggestion_manager

    @property
    def _beliefs(self):
        """Accessor compatible with both T3BeliefEngine and GeneralizationEngine."""
        return getattr(self.engine, 't3_beliefs', None) or getattr(self.engine, 'beliefs', {})

    def sync_all(self) -> Dict[str, int]:
        """
        Run the full sync: gaps, nascent, contested, validation targets.

        Returns counts of suggestions inserted per category.
        """
        counts = {}
        counts["gaps"] = self._sync_coverage_gaps()
        counts["nascent"] = self._sync_nascent_beliefs()
        counts["contested"] = self._sync_contested_beliefs()
        counts["validation"] = self._sync_validation_targets()
        
        total = sum(counts.values())
        LOGGER.info(
            "T3→InterpSpace sync: %d suggestions (%s)",
            total, ", ".join(f"{k}={v}" for k, v in counts.items())
        )
        return counts

    def _sync_coverage_gaps(self) -> int:
        """Convert T3 coverage gaps into search suggestions."""
        gaps = self.engine.get_coverage_gaps(min_priority=0.3)
        if not gaps:
            return 0

        # Clear old T3 gap suggestions first
        try:
            self.suggestions.clear_suggestions_for_source("t3_gap")
        except Exception:
            pass

        gap_dicts = []
        for gap in gaps:
            gap_dicts.append({
                "gap_id": gap.gap_id,
                "description": gap.description,
                "suggested_search": gap.search_query or f"{gap.iv_node} effect on {gap.dv_node}",
                "voi_score": gap.priority,
            })

        return self.suggestions.insert_gap_predictor_suggestions(
            gap_dicts, priority_score=self.PRIORITY_GAP
        )

    def _sync_nascent_beliefs(self) -> int:
        """Convert nascent beliefs (single-article) into replication search seeds."""
        nascent = [
            b for b in self._beliefs.values()
            if b.status == BeliefStatus.NASCENT
        ]
        if not nascent:
            return 0

        # Prioritize nascent beliefs that are most promising
        # Higher confidence + connected to established taxonomy nodes → more promising
        nascent.sort(key=lambda b: -b.confidence)

        # Clear old nascent suggestions
        try:
            self.suggestions.clear_suggestions_for_source("t3_nascent")
        except Exception:
            pass

        count = 0
        # Only top 100 nascent beliefs (otherwise too many)
        for belief in nascent[:100]:
            record = SuggestionRecord(
                source="t3_nascent",
                status="proposed",
                description=(
                    f"Nascent belief needs replication: "
                    f"{belief.natural_language}"
                ),
                suggested_search=belief.search_seed_query,
                priority_score=self.PRIORITY_NASCENT * belief.confidence,
            )
            try:
                self.suggestions.insert_suggestion(record)
                count += 1
            except Exception as e:
                LOGGER.debug(f"Failed to insert nascent suggestion: {e}")

        return count

    def _sync_contested_beliefs(self) -> int:
        """Convert contested beliefs into argumentation/resolution targets."""
        contested = [
            b for b in self._beliefs.values()
            if b.status == BeliefStatus.CONTESTED
        ]
        if not contested:
            return 0

        # Clear old contested suggestions
        try:
            self.suggestions.clear_suggestions_for_source("t3_contested")
        except Exception:
            pass

        suggestions = []
        for belief in contested:
            suggestions.append({
                "description": (
                    f"Contested: {belief.natural_language} — "
                    f"{belief.n_positive} positive vs {belief.n_negative} negative "
                    f"({belief.n_null} null). Needs moderator analysis."
                ),
                "search_query": (
                    f"{belief.iv_node} moderator variables "
                    f"{belief.dv_node} meta-analysis"
                ),
            })

        return self.suggestions.insert_argumentation_suggestions(
            suggestions, priority_score=self.PRIORITY_CONTESTED
        )

    def _sync_validation_targets(self) -> int:
        """
        Find established beliefs with low confidence (< 0.65) or small N.
        These need more evidence to validate.
        """
        validation_targets = [
            b for b in self._beliefs.values()
            if b.status == BeliefStatus.ESTABLISHED
            and (b.confidence < 0.65 or b.n_total < 5)
        ]
        if not validation_targets:
            return 0

        # Sort by priority: lowest confidence first
        validation_targets.sort(key=lambda b: b.confidence)

        # Clear old validation suggestions
        try:
            self.suggestions.clear_suggestions_for_source("t3_validation")
        except Exception:
            pass

        count = 0
        for belief in validation_targets[:50]:
            record = SuggestionRecord(
                source="t3_validation",
                status="proposed",
                description=(
                    f"Needs validation: {belief.natural_language} "
                    f"(confidence={belief.confidence:.2f}, N={belief.total_sample_n or '?'})"
                ),
                suggested_search=belief.search_seed_query,
                priority_score=self.PRIORITY_VALIDATION * (1.0 - belief.confidence),
            )
            try:
                self.suggestions.insert_suggestion(record)
                count += 1
            except Exception as e:
                LOGGER.debug(f"Failed to insert validation suggestion: {e}")

        return count

    def get_summary(self) -> Dict[str, Any]:
        """Summary of what's been synced."""
        beliefs = self._beliefs
        return {
            "total_beliefs": len(beliefs),
            "established": sum(1 for b in beliefs.values() if b.status == BeliefStatus.ESTABLISHED),
            "contested": sum(1 for b in beliefs.values() if b.status == BeliefStatus.CONTESTED),
            "nascent": sum(1 for b in beliefs.values() if b.status == BeliefStatus.NASCENT),
            "coverage_gaps": len(self.engine.gaps if hasattr(self.engine, 'gaps') else []),
            "suggestions_pending": self.suggestions.get_unacted_suggestions_count(),
        }
