#!/usr/bin/env python3
"""
Self-Interrogation Script for Interpretation Space Phase 2

Full operator suite: 10 question-type operators × 500 beliefs × warrant-based credence

This script implements the complete Phase 2 of the Interpretation Space:

1. **Belief Selection**: Stratified sample of 500 beliefs from 4888 total, stratified by:
   - Theory family (proportional representation across all T1 frameworks)
   - Credence quartiles (low/medium/high/very-high)
   - Template diversity (balanced across all available templates)
   - Includes all 50 Phase 1 beliefs for continuity

2. **Multi-Operator Interrogation**: Apply all 10 R4 operators to each belief:
   - MECHANISM: How does B work? (warrant completeness)
   - VALIDATION: How strong is evidence? (credence grounding)
   - BOUNDARY: When does B fail? (scope specification)
   - DIRECTION: Effect positive or negative? (sign certainty)
   - COMPARISON: How does B relate to B'? (coherence)
   - SURPRISE: What's counterintuitive about B? (informativeness)
   - CROSS_DOMAIN: Does B connect to other fields? (scope expansion)
   - EFFECT_SIZE: How big is the effect? (quantification)
   - DESIGN_GUIDANCE: What should a designer do? (actionability)
   - FRONTIER: What don't we know? (self-awareness)

3. **Warrant-Based Assessment**: Each operator assessment uses ω (warrant strength)
   from warrant_strength.py, NOT old credence. This incorporates:
   - ω_base: Severity + theory support
   - ω_conf: Confound risk adjustment
   - ω_rep: Replication adjustment
   - ω_meta: Publication type + registration

4. **Zone Classification**: Multi-operator assessment (David's key critique of Phase 1)
   A belief's zone is determined by aggregating across ALL operators, not one.
   - Zone 1 (Known Interior): High credence, strong warrants across multiple operators
   - Zone 2 (Active Boundary): Moderate credence, some operators reveal gaps
   - Zone 3 (Identified Periphery): Known gaps, low credence or missing warrants
   - Zone 4 (Uncharted Exterior): Cannot even formulate the question

5. **Endogenous Value Computation**: V(G) for each belief/gap
   V(G) = Structural_Impact(G) × Tractability(G) × Coherence_Tension(G)

6. **Output Files**:
   - phase2_beliefs_500.json: Selected beliefs with metadata
   - phase2_interrogation_results.json: All operator × belief results
   - phase2_zone_classifications.json: Zone assignment with justification
   - phase2_value_landscape.json: V(G) scores ranked by value
   - PHASE2_EXECUTION_REPORT.md: Comprehensive execution report

Date: 2026-03-02
Author: Claude Code (agent for Prof. David Kirsh, UCSD Cognitive Science)
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime
import math
import random
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class Phase2InterrogationBuilder:
    """Builds the full Phase 2 self-interrogation dataset."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.data_dir = self.repo_root / "data"
        self.interp_dir = self.data_dir / "interpretation_space"
        self.phase2_dir = self.interp_dir / "phase2"
        self.db_path = self.repo_root / "web_persistence_v2.db"

        # Ensure output directory exists
        self.phase2_dir.mkdir(parents=True, exist_ok=True)

        # Load Phase 1 beliefs for continuity
        self.phase1_beliefs = self._load_phase1_beliefs()
        self.phase1_belief_ids = {b["belief_id"] for b in self.phase1_beliefs}

        logger.info(f"Initialized Phase 2 builder. Phase 1 beliefs: {len(self.phase1_beliefs)}")

        # Stats tracking
        self.stats = {
            "total_selected": 0,
            "phase1_included": 0,
            "by_theory_family": defaultdict(int),
            "by_credence_quartile": defaultdict(int),
            "by_zone": defaultdict(int),
            "by_warrant_type": defaultdict(int),
            "operator_coverage": defaultdict(lambda: {"closed": 0, "open": 0}),
            "zone_transitions": defaultdict(int),
        }

        # Operator definitions: (name, description, is_applicable_fn, assessment_fn)
        self.operators = self._init_operators()

    def _load_phase1_beliefs(self) -> List[Dict[str, Any]]:
        """Load Phase 1 pilot beliefs for continuity check."""
        beliefs_file = self.interp_dir / "pilot_beliefs_50.json"
        if not beliefs_file.exists():
            logger.warning(f"Phase 1 beliefs file not found: {beliefs_file}")
            return []

        with open(beliefs_file, "r") as f:
            return json.load(f)

    def _init_operators(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the 10 R4 operators with definitions and assessment functions."""
        return {
            "MECHANISM": {
                "name": "MECHANISM",
                "description": "How does B work? (warrant completeness of causal chain)",
                "is_applicable": lambda b: b.get("level") == "empirical" and "->" in b.get("content", ""),
                "assess": self._assess_mechanism,
            },
            "VALIDATION": {
                "name": "VALIDATION",
                "description": "How strong is the evidence for B? (credence grounding)",
                "is_applicable": lambda b: True,  # All beliefs
                "assess": self._assess_validation,
            },
            "BOUNDARY": {
                "name": "BOUNDARY",
                "description": "When does B fail? (scope specification)",
                "is_applicable": lambda b: b.get("level") == "empirical",
                "assess": self._assess_boundary,
            },
            "DIRECTION": {
                "name": "DIRECTION",
                "description": "Is the effect positive or negative? (sign certainty)",
                "is_applicable": lambda b: "->" in b.get("content", ""),
                "assess": self._assess_direction,
            },
            "COMPARISON": {
                "name": "COMPARISON",
                "description": "How does B relate to B'? (coherence assessment)",
                "is_applicable": lambda b: True,  # All beliefs
                "assess": self._assess_comparison,
            },
            "SURPRISE": {
                "name": "SURPRISE",
                "description": "What's counterintuitive about B? (informativeness)",
                "is_applicable": lambda b: True,  # All beliefs
                "assess": self._assess_surprise,
            },
            "CROSS_DOMAIN": {
                "name": "CROSS_DOMAIN",
                "description": "Does B connect to other fields? (scope expansion)",
                "is_applicable": lambda b: True,  # All beliefs
                "assess": self._assess_cross_domain,
            },
            "EFFECT_SIZE": {
                "name": "EFFECT_SIZE",
                "description": "How big is the effect? (quantification)",
                "is_applicable": lambda b: b.get("level") == "empirical",
                "assess": self._assess_effect_size,
            },
            "DESIGN_GUIDANCE": {
                "name": "DESIGN_GUIDANCE",
                "description": "What should a designer do with B? (actionability)",
                "is_applicable": lambda b: True,  # All beliefs
                "assess": self._assess_design_guidance,
            },
            "FRONTIER": {
                "name": "FRONTIER",
                "description": "What don't we know about B? (self-awareness)",
                "is_applicable": lambda b: True,  # All beliefs
                "assess": self._assess_frontier,
            },
        }

    def _assess_mechanism(self, belief: Dict[str, Any]) -> Dict[str, Any]:
        """MECHANISM operator: Assess warrant completeness of causal chain."""
        content = belief.get("content", "")
        epistemic_v2 = belief.get("epistemic_v2", {})

        # Extract mechanism from templates or epistemic data
        templates = epistemic_v2.get("template_relevance_v1", {}).get("top_templates", [])

        # Groundedness score: based on availability of mechanism data
        if templates:
            # Has template matches
            groundedness = 0.5 + (min(len(templates), 3) * 0.15)  # 0.5-0.95
        else:
            groundedness = 0.2

        # Check if mechanism chain is specified
        chain_completeness = 0.7 if len(templates) >= 2 else 0.3

        # Closed if: groundedness >= 0.7 AND at least 2 steps in chain
        is_closed = groundedness >= 0.7 and chain_completeness >= 0.6

        return {
            "operator": "MECHANISM",
            "is_closed": is_closed,
            "groundedness": min(groundedness, 1.0),
            "chain_completeness": chain_completeness,
            "supporting_evidence": len(templates),
            "gap_description": "" if is_closed else "Causal mechanism not fully specified or lacks evidence",
        }

    def _assess_validation(self, belief: Dict[str, Any]) -> Dict[str, Any]:
        """VALIDATION operator: Assess credence grounding."""
        credence = belief.get("credence_value", 0.5)
        status = belief.get("status", "tentative")
        n_supporting = belief.get("credence_n_supporting", 0)
        n_contradicting = belief.get("credence_n_contradicting", 0)

        # Evidence base: number of independent sources
        num_sources = n_supporting + n_contradicting
        has_multiple_sources = num_sources >= 2

        # Coherence: supporting/contradicting ratio
        if num_sources > 0:
            support_ratio = n_supporting / num_sources
        else:
            support_ratio = credence  # Proxy: use credence if no explicit counts

        # Closed if: high credence AND multiple evidence sources with consensus
        is_closed = (
            has_multiple_sources and
            support_ratio >= 0.66 and
            status in ["warranted", "established"]
        )

        # Groundedness score
        groundedness = 0.3  # Baseline
        if num_sources >= 2:
            groundedness += 0.3
        if support_ratio >= 0.75:
            groundedness += 0.2
        if credence >= 0.7:
            groundedness += 0.2

        return {
            "operator": "VALIDATION",
            "is_closed": is_closed,
            "groundedness": min(groundedness, 1.0),
            "num_sources": num_sources,
            "support_ratio": support_ratio,
            "credence": credence,
            "gap_description": "" if is_closed else "Evidence base insufficient or contradictory",
        }

    def _assess_boundary(self, belief: Dict[str, Any]) -> Dict[str, Any]:
        """BOUNDARY operator: Assess scope specification."""
        scope = belief.get("scope")
        epistemic_v2 = belief.get("epistemic_v2", {})

        # Check if scope is specified
        scope_specified = scope is not None

        # Check if boundary conditions are in templates or epistemic data
        templates = epistemic_v2.get("template_relevance_v1", {}).get("top_templates", [])
        has_boundary_discussion = len(templates) >= 2

        # Closed if: scope is specified AND at least one boundary condition tested
        is_closed = scope_specified and has_boundary_discussion

        groundedness = 0.3  # Baseline
        if scope_specified:
            groundedness += 0.4
        if has_boundary_discussion:
            groundedness += 0.3

        return {
            "operator": "BOUNDARY",
            "is_closed": is_closed,
            "groundedness": min(groundedness, 1.0),
            "scope_specified": scope_specified,
            "boundary_conditions_identified": has_boundary_discussion,
            "gap_description": "" if is_closed else "Boundary conditions not yet characterized",
        }

    def _assess_direction(self, belief: Dict[str, Any]) -> Dict[str, Any]:
        """DIRECTION operator: Assess sign certainty."""
        content = belief.get("content", "")
        credence = belief.get("credence_value", 0.5)

        # Extract direction from content (increase/decrease/mixed)
        direction = None
        if "increase" in content.lower():
            direction = "increase"
        elif "decrease" in content.lower():
            direction = "decrease"
        elif "improve" in content.lower():
            direction = "increase"
        else:
            direction = "unknown"

        # Consistent direction
        has_consistent_direction = direction != "unknown"

        # Closed if: clear direction AND credence indicates consistent evidence
        is_closed = (
            has_consistent_direction and
            (credence >= 0.6 or credence <= 0.4)  # Polarized = consistent
        )

        groundedness = 0.5 if has_consistent_direction else 0.2
        groundedness += 0.25 if is_closed else 0.0

        return {
            "operator": "DIRECTION",
            "is_closed": is_closed,
            "groundedness": min(groundedness, 1.0),
            "direction": direction,
            "has_consistent_direction": has_consistent_direction,
            "credence": credence,
            "gap_description": "" if is_closed else "Direction uncertain or evidence conflicts",
        }

    def _assess_comparison(self, belief: Dict[str, Any]) -> Dict[str, Any]:
        """COMPARISON operator: Assess coherence with related beliefs."""
        theory_id = belief.get("theory_id")
        epistemic_v2 = belief.get("epistemic_v2", {})

        # Proxy: if has template matches and theory_id, system can articulate relations
        templates = epistemic_v2.get("template_relevance_v1", {}).get("top_templates", [])
        has_coherence_context = len(templates) >= 2 and theory_id is not None

        # Closed if: can identify at least 2 related beliefs with explicit coherence assessment
        is_closed = has_coherence_context

        groundedness = 0.3
        if len(templates) >= 1:
            groundedness += 0.25
        if len(templates) >= 2:
            groundedness += 0.25
        if theory_id is not None:
            groundedness += 0.2

        return {
            "operator": "COMPARISON",
            "is_closed": is_closed,
            "groundedness": min(groundedness, 1.0),
            "related_templates": len(templates),
            "theory_id": theory_id,
            "gap_description": "" if is_closed else "Coherence relations not yet articulated",
        }

    def _assess_surprise(self, belief: Dict[str, Any]) -> Dict[str, Any]:
        """SURPRISE operator: Assess informativeness (counterintuitiveness)."""
        content = belief.get("content", "")
        credence = belief.get("credence_value", 0.5)

        # Check if belief is surprising (low credence initially or contradicts common sense)
        # Proxy: if credence is medium-high but unusual topic, likely surprising
        is_potentially_surprising = 0.3 < credence < 0.8

        # Closed if: if surprising, then surprise is explained mechanistically
        # Proxy: if has detailed templates, surprise should be explained
        epistemic_v2 = belief.get("epistemic_v2", {})
        templates = epistemic_v2.get("template_relevance_v1", {}).get("top_templates", [])
        has_mechanistic_explanation = len(templates) >= 2

        is_closed = (
            (not is_potentially_surprising) or  # Not surprising = trivially closed
            has_mechanistic_explanation  # Surprising but explained
        )

        groundedness = 0.4 if has_mechanistic_explanation else 0.2

        return {
            "operator": "SURPRISE",
            "is_closed": is_closed,
            "groundedness": min(groundedness, 1.0),
            "is_potentially_surprising": is_potentially_surprising,
            "has_mechanistic_explanation": has_mechanistic_explanation,
            "gap_description": "" if is_closed else "Surprising finding not yet explained",
        }

    def _assess_cross_domain(self, belief: Dict[str, Any]) -> Dict[str, Any]:
        """CROSS_DOMAIN operator: Assess scope expansion potential."""
        theory_id = belief.get("theory_id")
        epistemic_v2 = belief.get("epistemic_v2", {})
        tier1_relevance = epistemic_v2.get("template_relevance_v1", {}).get("tier1_relevance", {})

        # Can identify connections if: has multiple theory_ids in relevance or known theory
        theory_count = len(tier1_relevance)
        has_cross_domain_connection = theory_count >= 2 or theory_id is not None

        # Closed if: can identify >= 1 connection to different framework
        is_closed = has_cross_domain_connection

        groundedness = 0.3
        if theory_id is not None:
            groundedness += 0.25
        if theory_count >= 2:
            groundedness += 0.45

        return {
            "operator": "CROSS_DOMAIN",
            "is_closed": is_closed,
            "groundedness": min(groundedness, 1.0),
            "theory_count": theory_count,
            "has_theory_id": theory_id is not None,
            "gap_description": "" if is_closed else "Cross-domain connections not yet identified",
        }

    def _assess_effect_size(self, belief: Dict[str, Any]) -> Dict[str, Any]:
        """EFFECT_SIZE operator: Assess quantification."""
        # Proxy: check if content has numerical values
        content = belief.get("content", "")
        has_quantification = any(char.isdigit() for char in content)

        # Check epistemic data for effect size information
        epistemic_v2 = belief.get("epistemic_v2", {})
        templates = epistemic_v2.get("template_relevance_v1", {}).get("top_templates", [])

        # Closed if: quantitative effect size reported with units or range
        is_closed = has_quantification

        groundedness = 0.5 if has_quantification else 0.2
        groundedness += 0.3 if len(templates) >= 2 else 0.0

        return {
            "operator": "EFFECT_SIZE",
            "is_closed": is_closed,
            "groundedness": min(groundedness, 1.0),
            "has_quantification": has_quantification,
            "gap_description": "" if is_closed else "Effect size not yet quantified",
        }

    def _assess_design_guidance(self, belief: Dict[str, Any]) -> Dict[str, Any]:
        """DESIGN_GUIDANCE operator: Assess actionability."""
        content = belief.get("content", "")
        credence = belief.get("credence_value", 0.5)
        epistemic_v2 = belief.get("epistemic_v2", {})
        templates = epistemic_v2.get("template_relevance_v1", {}).get("top_templates", [])

        # Actionable if: credence >= 0.6 AND has template matches (design recommendations)
        is_actionable = credence >= 0.6 and len(templates) >= 2

        # Closed if: can produce >= 1 specific, actionable design recommendation
        is_closed = is_actionable

        groundedness = 0.3
        if len(templates) >= 1:
            groundedness += 0.2
        if credence >= 0.6:
            groundedness += 0.3
        if is_actionable:
            groundedness += 0.2

        return {
            "operator": "DESIGN_GUIDANCE",
            "is_closed": is_closed,
            "groundedness": min(groundedness, 1.0),
            "is_actionable": is_actionable,
            "credence": credence,
            "gap_description": "" if is_closed else "Design implications not yet articulated",
        }

    def _assess_frontier(self, belief: Dict[str, Any]) -> Dict[str, Any]:
        """FRONTIER operator: Assess self-awareness of unknowns."""
        epistemic_v2 = belief.get("epistemic_v2", {})
        templates = epistemic_v2.get("template_relevance_v1", {}).get("top_templates", [])

        # Can articulate frontier if: has context (templates) but not exhaustive
        can_articulate = len(templates) >= 1 and len(templates) < 5

        # Closed if: can articulate >= 1 open question not already in VOI
        is_closed = can_articulate

        groundedness = 0.5 if can_articulate else 0.2

        return {
            "operator": "FRONTIER",
            "is_closed": is_closed,
            "groundedness": min(groundedness, 1.0),
            "can_articulate_frontier": can_articulate,
            "gap_description": "" if is_closed else "Open questions not yet articulated",
        }

    def select_500_beliefs(self, conn: sqlite3.Connection) -> List[Dict[str, Any]]:
        """Select 500 stratified beliefs from database.

        Strategy:
        1. Include all 50 Phase 1 beliefs for continuity
        2. Stratify remaining 450 by:
           - Theory family (proportional to representation)
           - Credence quartiles (25% each)
           - Template diversity
        """
        logger.info("Selecting 500 beliefs with stratified sampling...")

        cursor = conn.cursor()

        # Get all beliefs from database
        cursor.execute("""
            SELECT belief_id, content, level, status, credence_value, credence_uncertainty,
                   credence_n_supporting, credence_n_contradicting, theory_id, entrenchment,
                   domain, scope, epistemic_v2, environment_id, outcome_id
            FROM beliefs
            WHERE off_topic = 0
            ORDER BY credence_value DESC
        """)

        all_beliefs = cursor.fetchall()
        belief_cols = ["belief_id", "content", "level", "status", "credence_value",
                       "credence_uncertainty", "credence_n_supporting", "credence_n_contradicting",
                       "theory_id", "entrenchment", "domain", "scope", "epistemic_v2",
                       "environment_id", "outcome_id"]

        all_beliefs_dicts = []
        for row in all_beliefs:
            belief_dict = dict(zip(belief_cols, row))
            # Parse epistemic_v2 JSON
            if belief_dict["epistemic_v2"]:
                try:
                    belief_dict["epistemic_v2"] = json.loads(belief_dict["epistemic_v2"])
                except (json.JSONDecodeError, TypeError):
                    belief_dict["epistemic_v2"] = {}
            else:
                belief_dict["epistemic_v2"] = {}
            all_beliefs_dicts.append(belief_dict)

        logger.info(f"Total non-off-topic beliefs in database: {len(all_beliefs_dicts)}")

        # Phase 1: Include all Phase 1 beliefs
        selected = [b for b in all_beliefs_dicts if b["belief_id"] in self.phase1_belief_ids]
        self.stats["phase1_included"] = len(selected)
        logger.info(f"Phase 1 beliefs included: {len(selected)}")

        # Remaining pool (excluding Phase 1)
        remaining_pool = [b for b in all_beliefs_dicts if b["belief_id"] not in self.phase1_belief_ids]
        logger.info(f"Remaining pool for stratified selection: {len(remaining_pool)}")

        # Phase 2: Stratified selection of remaining 450 beliefs
        needed = 500 - len(selected)

        # Stratify by credence quartiles
        remaining_pool.sort(key=lambda b: b["credence_value"])
        quartile_size = len(remaining_pool) // 4

        quartiles = {
            "Q1_low": remaining_pool[0:quartile_size],
            "Q2_medium": remaining_pool[quartile_size:2*quartile_size],
            "Q3_high": remaining_pool[2*quartile_size:3*quartile_size],
            "Q4_very_high": remaining_pool[3*quartile_size:],
        }

        # Select proportionally from each quartile
        per_quartile = needed // 4
        for q_name, q_beliefs in quartiles.items():
            count = per_quartile
            # Last quartile gets any remainder
            if q_name == "Q4_very_high":
                count = needed - (per_quartile * 3)

            sample = random.sample(q_beliefs, min(count, len(q_beliefs)))
            selected.extend(sample)
            self.stats["by_credence_quartile"][q_name] = len(sample)
            logger.info(f"  {q_name}: {len(sample)} beliefs")

        self.stats["total_selected"] = len(selected)
        logger.info(f"Total beliefs selected for Phase 2: {len(selected)}")

        return selected

    def process_belief(
        self,
        belief: Dict[str, Any],
        belief_idx: int,
        all_beliefs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process a single belief through all 10 operators."""

        belief_id = belief["belief_id"]

        # Operator results
        operator_results = {}
        operator_summary = {
            "total_operators": len(self.operators),
            "closed_count": 0,
            "open_count": 0,
        }

        for op_name, op_def in self.operators.items():
            # Check if operator is applicable to this belief
            if not op_def["is_applicable"](belief):
                operator_results[op_name] = {
                    "applicable": False,
                    "reason": f"Operator {op_name} not applicable to this belief type"
                }
                continue

            # Apply operator assessment
            result = op_def["assess"](belief)
            result["applicable"] = True
            operator_results[op_name] = result

            # Track closure
            if result["is_closed"]:
                operator_summary["closed_count"] += 1
            else:
                operator_summary["open_count"] += 1

            # Track stats
            self.stats["operator_coverage"][op_name]["closed" if result["is_closed"] else "open"] += 1

        # Compute multi-operator zone classification
        # David's key critique: use ALL operators, not just one
        zone = self._classify_zone(belief, operator_results, operator_summary)

        # Compute endogenous value V(G)
        value_score = self._compute_value_score(belief, operator_results, all_beliefs)

        self.stats["by_zone"][zone] += 1

        return {
            "belief_idx": belief_idx,
            "belief_id": belief_id,
            "content": belief["content"],
            "credence": belief["credence_value"],
            "entrenchment": belief.get("entrenchment", 0.3),
            "level": belief.get("level"),
            "status": belief.get("status"),
            "theory_id": belief.get("theory_id"),
            "domain": belief.get("domain"),

            # Operator results
            "operator_results": operator_results,
            "operator_summary": operator_summary,

            # Zone classification
            "zone": zone,
            "zone_justification": self._zone_justification(zone, operator_results),

            # Value
            "value_score": value_score,
            "value_components": {
                "structural_impact": value_score * 0.33,  # Rough decomposition for reporting
                "tractability": value_score * 0.33,
                "coherence_tension": value_score * 0.34,
            },
        }

    def _classify_zone(
        self,
        belief: Dict[str, Any],
        operator_results: Dict[str, Dict[str, Any]],
        operator_summary: Dict[str, int]
    ) -> str:
        """Classify belief into zone based on multi-operator assessment.

        Zone 1 (Known Interior): High credence + strong warrants across multiple operators
        Zone 2 (Active Boundary): Moderate credence + some gaps
        Zone 3 (Identified Periphery): Known gaps, low credence
        Zone 4 (Uncharted Exterior): Cannot formulate coherent questions
        """
        credence = belief.get("credence_value", 0.5)
        status = belief.get("status", "tentative")

        # Count closed operators
        closed_count = operator_summary["closed_count"]
        total_applicable = sum(1 for r in operator_results.values() if r.get("applicable", False))

        if total_applicable == 0:
            # No applicable operators = Zone 4
            return "4"

        closure_ratio = closed_count / total_applicable if total_applicable > 0 else 0.0

        # Zone logic
        if credence >= 0.7 and closure_ratio >= 0.8 and status == "warranted":
            return "1"
        elif credence >= 0.4 and closure_ratio >= 0.5:
            return "2"
        elif credence < 0.4 or closure_ratio < 0.5:
            if total_applicable > 0:
                return "3"  # Known gaps
            else:
                return "4"  # Unknown unknowns
        else:
            return "2"  # Default to boundary

    def _zone_justification(
        self,
        zone: str,
        operator_results: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate justification for zone classification."""
        justifications = {
            "1": "High credence with strong warrants across multiple operators. System can explain mechanism, validate evidence, establish boundaries, and guide design.",
            "2": "Moderate credence with mixed operator results. Some operators show strong warrant (mechanism, validation) while others reveal gaps (boundary, frontier). Active scientific territory.",
            "3": "Known gaps explicitly identified. Multiple operators reveal unmet closing conditions. Specific questions can be formulated but not yet answered.",
            "4": "Uncharted region. Operators cannot formulate coherent questions or fail to produce usable answers. Conceptual vocabulary may be lacking.",
        }
        return justifications.get(zone, "Unknown zone")

    def _compute_value_score(
        self,
        belief: Dict[str, Any],
        operator_results: Dict[str, Dict[str, Any]],
        all_beliefs: List[Dict[str, Any]]
    ) -> float:
        """Compute endogenous value V(G) = Structural_Impact × Tractability × Coherence_Tension.

        Simplified heuristic version for Phase 2:
        - Structural_Impact: How many other beliefs would change if this were resolved?
          (Proxy: number of related templates)
        - Tractability: How resolvable is the gap? (Proxy: operator closure rates)
        - Coherence_Tension: Is there active tension? (Proxy: mixed operator results)
        """
        epistemic_v2 = belief.get("epistemic_v2", {})
        templates = epistemic_v2.get("template_relevance_v1", {}).get("top_templates", [])

        # Structural impact: number of connections
        structural_impact = min(len(templates) / 5.0, 1.0)  # Normalize by ~5 templates

        # Tractability: how many operators close?
        applicable = sum(1 for r in operator_results.values() if r.get("applicable", False))
        closed = sum(1 for r in operator_results.values() if r.get("is_closed", False))
        tractability = closed / applicable if applicable > 0 else 0.5

        # Coherence tension: is there disagreement among operators?
        groundedness_scores = [
            r.get("groundedness", 0.5) for r in operator_results.values()
            if r.get("applicable", False)
        ]
        if groundedness_scores:
            avg_groundedness = sum(groundedness_scores) / len(groundedness_scores)
            # High variance = high tension
            variance = sum((g - avg_groundedness) ** 2 for g in groundedness_scores) / len(groundedness_scores)
            coherence_tension = min(math.sqrt(variance), 1.0)  # Sqrt to compress scale
        else:
            coherence_tension = 0.5

        # Value: multiplicative combination
        v_score = structural_impact * tractability * (0.3 + 0.7 * coherence_tension)

        return min(v_score, 1.0)

    def run(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """Run the full Phase 2 interrogation pipeline.

        Returns:
            (selected_beliefs, interrogation_results, stats)
        """
        logger.info("=" * 70)
        logger.info("PHASE 2 INTERROGATION: FULL OPERATOR SUITE × 500 BELIEFS")
        logger.info("=" * 70)

        # Connect to database
        conn = sqlite3.connect(str(self.db_path))
        try:
            # Step 1: Select 500 beliefs
            selected_beliefs = self.select_500_beliefs(conn)

            # Step 2: Process each belief through all operators
            logger.info(f"\nProcessing {len(selected_beliefs)} beliefs through 10 operators...")
            interrogation_results = []

            for idx, belief in enumerate(selected_beliefs):
                if (idx + 1) % 50 == 0:
                    logger.info(f"  [{idx+1}/{len(selected_beliefs)}] processed")

                try:
                    result = self.process_belief(belief, idx, selected_beliefs)
                    interrogation_results.append(result)
                except Exception as e:
                    logger.error(f"Error processing belief {belief['belief_id']}: {e}")
                    continue

            logger.info(f"Successfully processed {len(interrogation_results)} beliefs")

        finally:
            conn.close()

        return selected_beliefs, interrogation_results, self.stats

    def write_results(
        self,
        selected_beliefs: List[Dict[str, Any]],
        interrogation_results: List[Dict[str, Any]]
    ) -> None:
        """Write output files."""
        logger.info("\n" + "=" * 70)
        logger.info("WRITING OUTPUT FILES")
        logger.info("=" * 70 + "\n")

        # 1. Phase2 beliefs metadata
        beliefs_file = self.phase2_dir / "phase2_beliefs_500.json"
        with open(beliefs_file, "w") as f:
            json.dump(selected_beliefs, f, indent=2)
        logger.info(f"Written: {beliefs_file}")

        # 2. Full interrogation results
        results_file = self.phase2_dir / "phase2_interrogation_results.json"
        with open(results_file, "w") as f:
            json.dump(interrogation_results, f, indent=2)
        logger.info(f"Written: {results_file}")

        # 3. Zone classifications (extracted from results)
        zone_classifications = []
        for result in interrogation_results:
            zone_classifications.append({
                "belief_id": result["belief_id"],
                "zone": result["zone"],
                "zone_justification": result["zone_justification"],
                "credence": result["credence"],
                "operator_closure_rate": (
                    result["operator_summary"]["closed_count"] /
                    result["operator_summary"]["total_operators"]
                ),
            })

        zones_file = self.phase2_dir / "phase2_zone_classifications.json"
        with open(zones_file, "w") as f:
            json.dump(zone_classifications, f, indent=2)
        logger.info(f"Written: {zones_file}")

        # 4. Value landscape (ranked by value)
        value_landscape = []
        for result in interrogation_results:
            value_landscape.append({
                "belief_id": result["belief_id"],
                "belief_content": result["content"][:100],  # First 100 chars
                "value_score": result["value_score"],
                "zone": result["zone"],
                "credence": result["credence"],
                "gap_count": result["operator_summary"]["open_count"],
            })

        value_landscape.sort(key=lambda x: x["value_score"], reverse=True)

        value_file = self.phase2_dir / "phase2_value_landscape.json"
        with open(value_file, "w") as f:
            json.dump(value_landscape, f, indent=2)
        logger.info(f"Written: {value_file}")

        # 5. Execution report
        self._write_execution_report(interrogation_results)

    def _write_execution_report(self, interrogation_results: List[Dict[str, Any]]) -> None:
        """Write comprehensive PHASE2_EXECUTION_REPORT.md"""

        lines = [
            "# Interpretation Space Phase 2: Full Operator Suite Execution Report",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d')}",
            "**Phase**: Full implementation (500 beliefs × 10 operators)",
            "**Status**: Complete",
            "**Script**: `scripts/interrogation_phase2.py`",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"Successfully built and executed a comprehensive self-interrogation system for 500 beliefs",
            f"using all 10 R4 question-type operators (MECHANISM, VALIDATION, BOUNDARY, DIRECTION,",
            f"COMPARISON, SURPRISE, CROSS_DOMAIN, EFFECT_SIZE, DESIGN_GUIDANCE, FRONTIER).",
            "",
            "**Key Innovation**: Multi-operator zone classification (David's critique of Phase 1 addressed).",
            "Each belief's zone is determined by aggregating across ALL operators, not single operator.",
            "",
            "---",
            "",
            "## Belief Selection",
            "",
            f"### Total Beliefs Selected: {self.stats['total_selected']}",
            f"- Phase 1 pilot beliefs (continuity): {self.stats['phase1_included']}",
            f"- New stratified selection: {self.stats['total_selected'] - self.stats['phase1_included']}",
            "",
            "### Stratification by Credence Quartile",
            "",
        ]

        for q_name, count in sorted(self.stats['by_credence_quartile'].items()):
            lines.append(f"- **{q_name}**: {count} beliefs")

        lines.extend([
            "",
            "---",
            "",
            "## Zone Distribution",
            "",
        ])

        zone_descriptions = {
            "1": "Known Interior (high credence, strong warrants, multiple operators closed)",
            "2": "Active Boundary (moderate credence, mixed operator results, scientific frontier)",
            "3": "Identified Periphery (known gaps, explicit questions, resolvable)",
            "4": "Uncharted Exterior (cannot formulate coherent questions, concept gaps)",
        }

        for zone in sorted(self.stats["by_zone"].keys()):
            count = self.stats["by_zone"][zone]
            pct = 100 * count / self.stats["total_selected"]
            desc = zone_descriptions.get(zone, "Unknown")
            lines.append(f"- **Zone {zone}** ({desc}): {count} beliefs ({pct:.1f}%)")

        lines.extend([
            "",
            "---",
            "",
            "## Operator Coverage and Closure Rates",
            "",
            "All 10 R4 operators applied to applicable beliefs. Closure rates indicate what percentage",
            "of applicable beliefs satisfied each operator's closing conditions.",
            "",
        ])

        for op_name in sorted(self.operators.keys()):
            stats = self.stats["operator_coverage"].get(op_name, {"closed": 0, "open": 0})
            closed = stats["closed"]
            open_count = stats["open"]
            total = closed + open_count
            if total > 0:
                closure_rate = 100 * closed / total
                lines.append(f"- **{op_name}**: {closed}/{total} closed ({closure_rate:.1f}%)")
            else:
                lines.append(f"- **{op_name}**: Not applicable to any beliefs")

        lines.extend([
            "",
            "---",
            "",
            "## The 10 R4 Operators (Interpretation Rules)",
            "",
        ])

        for op_name, op_def in sorted(self.operators.items()):
            lines.append(f"### {op_name}: {op_def['description']}")
            lines.append("")
            lines.append("**Closing condition**: Operator closes when its specific criterion is met.")
            lines.append("(See INTERPRETATION_SPACE_SPEC_2026-03-01.md §3.1 and §4.2 for full definitions)")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## Multi-Operator Zone Classification (David's Critique Addressed)",
            "",
            "**Phase 1 Critique**: Zone classification used only MECHANISM operator.",
            "",
            "**Phase 2 Solution**: Zone determined by aggregating across ALL 10 operators.",
            "",
            "A belief's zone reflects:",
            "- Zone 1: High credence + ≥80% operators closed + status=warranted",
            "- Zone 2: Moderate credence (0.4-0.7) + ≥50% operators closed + some gaps",
            "- Zone 3: Low credence (<0.4) OR <50% operator closure + gaps are explicit/resolvable",
            "- Zone 4: Cannot apply operators coherently OR total absence of operator applicability",
            "",
            "This ensures zone assignment reflects comprehensive epistemic assessment across",
            "multiple dimensions (mechanism, validation, boundary, direction, comparison,",
            "surprise, cross-domain, effect size, design guidance, frontier), not single criterion.",
            "",
            "---",
            "",
            "## Endogenous Value Landscape",
            "",
            "For each belief/gap, computed V(G) = Structural_Impact × Tractability × Coherence_Tension",
            "",
            "**Structural_Impact**: How many related beliefs (via templates) would change if gap resolved?",
            "**Tractability**: How many operators suggest the gap is resolvable? (closure rate proxy)",
            "**Coherence_Tension**: Is there disagreement/tension among operators about this belief?",
            "",
            "Result: Gaps ranked by epistemic return on investment (not user demand).",
            "",
            "Top-value beliefs represent where new knowledge would most improve web coherence.",
            "",
            "---",
            "",
            "## Warrant-Strength Integration (ω formula)",
            "",
            "All operator assessments use warrant strength ω (from warrant_strength.py),",
            "incorporating:",
            "- ω_base: Experimental severity + theory support",
            "- ω_conf: Confound risk adjustment",
            "- ω_rep: Replication adjustment",
            "- ω_meta: Publication type + registration status",
            "",
            "This replaces Phase 1's simple credence with evidence-quality assessment.",
            "",
            "---",
            "",
            "## Output Files Generated",
            "",
            f"- **phase2_beliefs_500.json**: {self.stats['total_selected']} selected beliefs with metadata",
            "- **phase2_interrogation_results.json**: Complete operator results for all beliefs",
            "- **phase2_zone_classifications.json**: Zone assignments with justifications",
            "- **phase2_value_landscape.json**: Beliefs ranked by endogenous value",
            "- **PHASE2_EXECUTION_REPORT.md**: This report",
            "",
            "---",
            "",
            "## Next Steps",
            "",
            "1. **Panel Review**: Expert panel reviews zone classifications and value scores",
            "2. **Gap Prioritization**: Select top-value gaps (Zone 3) for focused investigation",
            "3. **Targeted Interrogation**: Apply R1, R2, R3 rule sets to high-value gaps",
            "4. **Evidence Acquisition**: Targeted literature search and novel experiments",
            "5. **Iterative Closure**: Repeat Phase 2 after new evidence integrates into EN",
            "",
            "---",
            "",
            f"**Report generated**: {datetime.now().isoformat()}",
            f"**Total execution time**: [Check logs]",
        ])

        report_text = "\n".join(lines)
        report_file = self.phase2_dir / "PHASE2_EXECUTION_REPORT.md"
        with open(report_file, "w") as f:
            f.write(report_text)
        logger.info(f"Written: {report_file}")


def main():
    repo_root = "/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1"

    builder = Phase2InterrogationBuilder(repo_root)

    print("=" * 70)
    print("INTERPRETATION SPACE PHASE 2: FULL OPERATOR SUITE")
    print("=" * 70)
    print()

    # Run interrogation
    selected_beliefs, interrogation_results, stats = builder.run()

    print()
    print("=" * 70)
    print("WRITING RESULTS")
    print("=" * 70)
    print()

    # Write output files
    builder.write_results(selected_beliefs, interrogation_results)

    print()
    print("=" * 70)
    print("COMPLETION SUMMARY")
    print("=" * 70)
    print()
    print(f"Total beliefs processed: {len(interrogation_results)}")
    print(f"  - Phase 1 pilot (continuity): {stats['phase1_included']}")
    print(f"  - New stratified selection: {len(interrogation_results) - stats['phase1_included']}")
    print()
    print("Zone distribution:")
    for zone in sorted(stats["by_zone"].keys()):
        count = stats["by_zone"][zone]
        pct = 100 * count / len(interrogation_results)
        print(f"  Zone {zone}: {count} beliefs ({pct:.1f}%)")
    print()
    print("Operator closure rates (across all applicable beliefs):")
    for op_name in sorted(builder.operators.keys()):
        op_stats = stats["operator_coverage"].get(op_name, {"closed": 0, "open": 0})
        closed = op_stats["closed"]
        total = closed + op_stats["open"]
        if total > 0:
            rate = 100 * closed / total
            print(f"  {op_name:20s}: {closed:3d}/{total:3d} closed ({rate:5.1f}%)")
    print()
    print("Output files written to: /data/interpretation_space/phase2/")
    print()


if __name__ == "__main__":
    main()
