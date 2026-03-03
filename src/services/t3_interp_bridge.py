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

    # ══════════════════════════════════════════════════════════════════
    # Wave 9: Bidirectional T2↔T3 Cross-Level Justification
    # V10 #2 Epistemologist: "Cross-level justification is essential"
    # ══════════════════════════════════════════════════════════════════

    def ground_t2_in_t3(self, t2_templates: List[Dict]) -> List[Dict[str, Any]]:
        """
        Upward justification: ground T2 theoretical templates in T3 empirical beliefs.

        For each T2 template, find T3 beliefs that provide empirical support
        by matching IV/DV taxonomy nodes. Compute an empirical grounding score.

        Args:
            t2_templates: List of T2 template dicts with at least
                          {template_id, antecedent, consequent}

        Returns:
            List of grounding assessments per template.
        """
        beliefs = self._beliefs
        groundings = []

        for template in t2_templates:
            tid = template.get("template_id", "?")
            t2_iv = template.get("antecedent", "").lower()
            t2_dv = template.get("consequent", "").lower()

            supporting = []
            contradicting = []

            for belief in beliefs.values():
                if belief.status not in (BeliefStatus.ESTABLISHED, BeliefStatus.CONTESTED):
                    continue

                # Match if IV or DV taxonomy nodes overlap
                iv_match = (
                    belief.iv_node.lower() in t2_iv or
                    t2_iv in belief.iv_node.lower() or
                    any(seg in t2_iv for seg in belief.iv_node.split(".") if len(seg) > 3)
                )
                dv_match = (
                    belief.dv_node.lower() in t2_dv or
                    t2_dv in belief.dv_node.lower() or
                    any(seg in t2_dv for seg in belief.dv_node.split(".") if len(seg) > 3)
                )

                if iv_match and dv_match:
                    entry = {
                        "t3_id": belief.t3_id,
                        "direction": belief.effect_direction,
                        "confidence": belief.confidence,
                        "n_findings": belief.n_total,
                        "status": belief.status.value,
                    }
                    t2_dir = template.get("direction", "positive")
                    if belief.effect_direction == t2_dir:
                        supporting.append(entry)
                    else:
                        contradicting.append(entry)

            # Compute grounding score
            n_sup = len(supporting)
            n_con = len(contradicting)
            if n_sup + n_con == 0:
                grounding_score = 0.0
                grounding_label = "orphaned"
            elif n_con == 0:
                avg_conf = sum(s["confidence"] for s in supporting) / n_sup
                grounding_score = min(1.0, avg_conf * (1 + 0.1 * (n_sup - 1)))
                grounding_label = "well-grounded" if grounding_score > 0.7 else "partially-grounded"
            else:
                grounding_score = (n_sup - n_con) / (n_sup + n_con)
                grounding_label = "contested" if grounding_score > 0 else "counter-indicated"

            groundings.append({
                "template_id": tid,
                "grounding_score": round(grounding_score, 3),
                "grounding_label": grounding_label,
                "n_supporting": n_sup,
                "n_contradicting": n_con,
                "supporting_beliefs": supporting[:5],
                "contradicting_beliefs": contradicting[:5],
            })

        # Summary
        n_orphaned = sum(1 for g in groundings if g["grounding_label"] == "orphaned")
        n_well = sum(1 for g in groundings if g["grounding_label"] == "well-grounded")
        LOGGER.info(
            "T2→T3 grounding: %d/%d well-grounded, %d orphaned",
            n_well, len(groundings), n_orphaned,
        )

        return groundings

    def propagate_t2_constraints(self, t2_templates: List[Dict]) -> int:
        """
        Downward constraint: annotate T3 beliefs with T2 theory links.

        When a T2 theoretical claim predicts a specific direction,
        annotate matching T3 beliefs with the theory reference.
        This allows T3 to track WHICH theories each belief supports.

        Returns count of beliefs annotated.
        """
        beliefs = self._beliefs
        count = 0

        for template in t2_templates:
            tid = template.get("template_id", "?")
            t2_iv = template.get("antecedent", "").lower()
            t2_dv = template.get("consequent", "").lower()
            t2_theory = template.get("theory", template.get("theory_commitments", ""))

            for belief in beliefs.values():
                iv_match = any(
                    seg in t2_iv for seg in belief.iv_node.split(".") if len(seg) > 3
                )
                dv_match = any(
                    seg in t2_dv for seg in belief.dv_node.split(".") if len(seg) > 3
                )
                if iv_match and dv_match:
                    if tid not in belief.linked_templates:
                        belief.linked_templates.append(tid)
                        count += 1
                    # Add theory info to boundary conditions if available
                    if t2_theory and "t2_theory" not in belief.boundary_conditions:
                        belief.boundary_conditions["t2_theory"] = str(t2_theory)[:200]

        LOGGER.info("T2→T3 constraint propagation: %d beliefs annotated", count)
        return count

    def cross_level_report(self, t2_templates: List[Dict]) -> Dict[str, Any]:
        """
        Generate a cross-level justification report.

        Shows which T2 claims are empirically grounded (upward) and
        which T3 beliefs are theoretically motivated (downward).
        """
        groundings = self.ground_t2_in_t3(t2_templates)
        n_annotated = self.propagate_t2_constraints(t2_templates)

        beliefs = self._beliefs
        linked = sum(1 for b in beliefs.values() if b.linked_templates)
        unlinked = len(beliefs) - linked

        return {
            "t2_grounding": {
                "total_templates": len(groundings),
                "well_grounded": sum(1 for g in groundings if g["grounding_label"] == "well-grounded"),
                "partially_grounded": sum(1 for g in groundings if g["grounding_label"] == "partially-grounded"),
                "orphaned": sum(1 for g in groundings if g["grounding_label"] == "orphaned"),
                "contested": sum(1 for g in groundings if g["grounding_label"] == "contested"),
                "counter_indicated": sum(1 for g in groundings if g["grounding_label"] == "counter-indicated"),
                "details": groundings[:20],
            },
            "t3_linkage": {
                "total_beliefs": len(beliefs),
                "theory_linked": linked,
                "empirical_only": unlinked,
                "newly_annotated": n_annotated,
            },
        }
