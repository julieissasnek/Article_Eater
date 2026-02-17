"""Research Queue Service implementation.

Implements Sprint 9 tasks:
- I9.1: Unified queue from GapPredictor + VOI query guidance
- I9.2: Theory-driven gap detection from Tier 1 framework predictions
- I9.3: Zotero watcher sync hooks are implemented in src.queue.zotero_watcher
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from src.data.theory_bootstrap import get_tier1_frameworks
from src.epistemic.gap_types import GapType, GAP_TYPE_WEIGHTS
from src.queue.models import (
    ArticleReference,
    ClaimResult,
    CollectorProfile,
    ClosureAssessment,
    OpportunityStatus,
    Priority,
    ResearchOpportunity,
    ResearchQueueState,
    ResearchTarget,
    SearchGuidance,
    SearchResult,
    SearchResultType,
    TargetStatus,
    iso_z,
    parse_iso_z,
)
from src.services.gap_predictor import GapPredictor

logger = logging.getLogger(__name__)


class _FallbackQueryGenerator:
    """Fallback query builder used when VOI search dependencies are unavailable."""

    _STOPWORDS = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "that",
        "this",
        "it",
        "and",
        "or",
        "from",
        "by",
        "as",
    }

    def _extract_terms(self, text: str) -> list[str]:
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_\-]+", (text or "").lower())
        return [t for t in tokens if len(t) > 3 and t not in self._STOPWORDS]

    def generate_queries(self, text: str, gap_type: GapType, max_queries: int = 5) -> list[str]:
        terms = self._extract_terms(text)
        if not terms:
            return ["architecture cognition mechanism"]
        base = " ".join(terms[:6])
        queries = [base]
        if gap_type == GapType.VALIDATION:
            queries.append(f"{base} replication")
            queries.append(f"{base} meta analysis")
        elif gap_type == GapType.MECHANISM:
            queries.append(f"{base} mechanism")
            queries.append(f"{base} pathway")
        elif gap_type == GapType.DIRECTION:
            queries.append(f"{base} causal direction")
        elif gap_type == GapType.BOUNDARY:
            queries.append(f"{base} boundary condition")
        return queries[:max_queries]

    def generate_cross_field_queries(self, text: str, max_queries: int = 3) -> list[str]:
        terms = self._extract_terms(text)[:3]
        if not terms:
            return []
        quoted = " OR ".join([f"\"{t}\"" for t in terms])
        return [f"({quoted}) AND architecture", f"({quoted}) AND neuroscience"][:max_queries]


class ResearchQueueService:
    """Unified queue driven by predicted gaps, VOI, and Tier 1 frameworks."""

    DEFAULT_TARGET_DATABASES = ["semantic_scholar", "pubmed", "zotero"]

    def __init__(
        self,
        web: Optional[Any] = None,
        gap_predictor: Optional[GapPredictor] = None,
        query_generator: Optional[Any] = None,
        discovery_funnel: Optional[Any] = None,
        queue_path: str | Path = "data/production/research_queue_state.json",
        frameworks: Optional[list[Any]] = None,
    ):
        self._web = web
        self._gap_predictor = gap_predictor
        self._query_generator = query_generator
        self.discovery_funnel = discovery_funnel
        self.queue_path = Path(queue_path)
        self._frameworks = frameworks
        self._targets: dict[str, ResearchTarget] = {}
        self._collectors: dict[str, CollectorProfile] = {}
        self._opportunities: dict[str, ResearchOpportunity] = {}
        self._queue_id = f"queue_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        self._load_state()

    # ------------------------------------------------------------------
    # Lazy dependencies
    # ------------------------------------------------------------------

    @property
    def web(self) -> Any:
        if self._web is not None:
            return self._web
        try:
            from src.services.web_accumulator import get_accumulator

            acc = get_accumulator()
            self._web, _ = acc.get_master_web()
        except Exception as exc:
            logger.warning("ResearchQueueService: failed to load web (%s)", exc)
            self._web = None
        return self._web

    @property
    def gap_predictor(self) -> GapPredictor:
        if self._gap_predictor is None:
            self._gap_predictor = GapPredictor(web=self.web)
        return self._gap_predictor

    @property
    def query_generator(self) -> Any:
        if self._query_generator is None:
            try:
                from src.services.voi_search import QueryGenerator  # lazy import

                self._query_generator = QueryGenerator()
            except Exception as exc:
                logger.warning(
                    "ResearchQueueService: VOI query generator unavailable (%s); using fallback",
                    exc,
                )
                self._query_generator = _FallbackQueryGenerator()
        return self._query_generator

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refresh_queue(self, max_gaps: int = 50, include_theory: bool = True) -> ResearchQueueState:
        """Regenerate queue from current web/gaps and optional theory predictions."""
        generated_targets: list[ResearchTarget] = []

        try:
            gap_report = self.gap_predictor.find_all_gaps(max_gaps=max_gaps)
            for gap in gap_report.gaps:
                generated_targets.append(self._target_from_predicted_gap(gap))
        except Exception as exc:
            logger.warning("ResearchQueueService: gap refresh failed (%s)", exc)

        if include_theory:
            for framework in self._get_frameworks():
                generated_targets.extend(self.detect_theory_gaps(framework))

        merged: dict[str, ResearchTarget] = {}
        for target in generated_targets:
            existing = self._targets.get(target.target_id)
            if existing:
                target.status = existing.status
                target.assigned_to = existing.assigned_to
                target.created_at = existing.created_at
                if existing.is_research_opportunity:
                    target.is_research_opportunity = True
                if existing.opportunity_framing and not target.opportunity_framing:
                    target.opportunity_framing = existing.opportunity_framing
            merged[target.target_id] = target

        self._targets = merged
        self._persist_state()
        return self._build_state()

    def get_next_target(self, collector_id: str) -> Optional[ResearchTarget]:
        """Assign next unclaimed high-value target to a collector."""
        open_targets = [
            t for t in self._targets.values() if t.status == TargetStatus.OPEN and not t.assigned_to
        ]
        if not open_targets:
            return None

        open_targets.sort(
            key=lambda t: (
                self._priority_rank(t.priority),
                t.voi_score,
                t.created_at,
            ),
            reverse=True,
        )
        target = open_targets[0]
        target.assigned_to = collector_id
        target.status = TargetStatus.SEARCHING
        target.updated_at = datetime.now(timezone.utc)
        self._persist_state()
        return target

    def register_collector(self, profile: CollectorProfile) -> CollectorProfile:
        """Register or update a VOI collector profile."""
        self._collectors[profile.collector_id] = profile
        self._persist_state()
        return profile

    def get_collector(self, collector_id: str) -> Optional[CollectorProfile]:
        return self._collectors.get(collector_id)

    def list_collectors(self) -> list[CollectorProfile]:
        return sorted(self._collectors.values(), key=lambda c: c.collector_id)

    def list_research_opportunities(
        self, status: Optional[OpportunityStatus] = None
    ) -> list[ResearchOpportunity]:
        opportunities = list(self._opportunities.values())
        if status is not None:
            opportunities = [o for o in opportunities if o.status == status]
        opportunities.sort(key=lambda o: (o.voi_score, o.created_at), reverse=True)
        return opportunities

    def get_research_opportunity(self, opportunity_id: str) -> Optional[ResearchOpportunity]:
        return self._opportunities.get(opportunity_id)

    def update_research_opportunity(
        self,
        opportunity_id: str,
        status: Optional[OpportunityStatus] = None,
        researcher_contact: Optional[str] = None,
        publication_doi: Optional[str] = None,
    ) -> Optional[ResearchOpportunity]:
        opportunity = self._opportunities.get(opportunity_id)
        if opportunity is None:
            return None
        if status is not None:
            opportunity.status = status
        if researcher_contact is not None:
            opportunity.researcher_contact = researcher_contact
        if publication_doi is not None:
            opportunity.publication_doi = publication_doi
            if status is None:
                opportunity.status = OpportunityStatus.PUBLISHED
        self._persist_state()
        return opportunity

    def claim_target(self, collector_id: str, target_id: Optional[str] = None) -> ClaimResult:
        """
        Claim a target for a registered collector.

        If target_id is None, assigns next available highest-priority target.
        """
        collector = self._collectors.get(collector_id)
        if collector is None:
            return ClaimResult(
                success=False,
                message=f"collector not registered: {collector_id}",
            )

        active = self._active_assignments(collector_id)
        if active >= max(1, collector.max_concurrent_targets):
            return ClaimResult(
                success=False,
                message=(
                    f"collector at capacity ({active}/{collector.max_concurrent_targets}); "
                    "complete or release current targets first"
                ),
            )

        target: Optional[ResearchTarget]
        if target_id:
            target = self._targets.get(target_id)
            if target is None:
                return ClaimResult(success=False, message=f"target not found: {target_id}")
            if target.status != TargetStatus.OPEN:
                return ClaimResult(
                    success=False,
                    message=f"target not open (status={target.status.value}): {target_id}",
                )
            if target.assigned_to:
                return ClaimResult(
                    success=False,
                    message=f"target already assigned to {target.assigned_to}: {target_id}",
                )
            target.assigned_to = collector_id
            target.status = TargetStatus.SEARCHING
            target.updated_at = datetime.now(timezone.utc)
        else:
            target = self.get_next_target(collector_id)
            if target is None:
                return ClaimResult(success=False, message="no open targets available")

        guidance = self._build_search_guidance(target, collector)
        deadline = datetime.now(timezone.utc) + timedelta(
            hours=max(1.0, float(collector.typical_turnaround_hours))
        )
        self._persist_state()
        return ClaimResult(
            success=True,
            target=target,
            search_guidance=guidance,
            deadline=deadline,
            message="target claimed",
        )

    def report_search_result(self, target_id: str, result: SearchResult) -> ClosureAssessment:
        """Update target status based on collector search report."""
        target = self._targets.get(target_id)
        if target is None:
            return ClosureAssessment(
                target_id=target_id,
                status=TargetStatus.STALE,
                closed=False,
                became_research_opportunity=False,
                n_articles_found=0,
                message="target not found",
            )

        became_opportunity = False
        n_articles = len(result.articles_found)

        if result.result_type in {SearchResultType.FOUND_RELEVANT, SearchResultType.FOUND_TANGENTIAL} and n_articles > 0:
            target.status = TargetStatus.FOUND
            target.assigned_to = result.collector_id
            message = f"{n_articles} candidate article(s) found"
        elif result.result_type == SearchResultType.NOT_FOUND:
            should_flag_opportunity = (
                result.is_research_opportunity
                or (
                    result.null_result_evidence is not None
                    and result.null_result_evidence.confidence_is_gap >= 0.7
                )
            )
            target.status = TargetStatus.STALE
            target.assigned_to = result.collector_id
            if should_flag_opportunity:
                target.is_research_opportunity = True
                if result.research_opportunity_framing:
                    target.opportunity_framing = result.research_opportunity_framing
                self._ensure_opportunity_for_target(target, result)
                became_opportunity = True
            message = "no matching articles found"
        else:
            target.status = TargetStatus.OPEN
            target.assigned_to = None
            message = "search inconclusive; returned to open queue"

        target.updated_at = datetime.now(timezone.utc)
        self._persist_state()

        return ClosureAssessment(
            target_id=target.target_id,
            status=target.status,
            closed=(target.status == TargetStatus.CLOSED),
            became_research_opportunity=became_opportunity,
            n_articles_found=n_articles,
            message=message,
        )

    def get_theory_predictions(self, framework_id: str) -> list[ResearchTarget]:
        """Return active theory-driven targets for a specific framework."""
        matches: list[ResearchTarget] = []
        for framework in self._get_frameworks():
            if getattr(framework, "theory_id", None) == framework_id:
                matches.extend(self.detect_theory_gaps(framework))
                break
        return matches

    def detect_theory_gaps(self, framework: Any) -> list[ResearchTarget]:
        """Generate validation targets where framework predictions lack support."""
        targets: list[ResearchTarget] = []

        for prediction in getattr(framework, "all_predictions", []):
            statement = (getattr(prediction, "statement", "") or "").strip()
            if not statement:
                continue

            support_score = self._prediction_support_score(
                framework_id=getattr(framework, "theory_id", ""),
                statement=statement,
            )
            if support_score >= 0.5:
                continue

            base_conf = float(getattr(framework, "overall_confidence", 0.5) or 0.5)
            voi = min(max(base_conf * (1.0 - support_score), 0.0), 1.0)
            priority = self._priority_bucket(voi)
            q = self._build_queries_from_text(
                text=f"{getattr(framework, 'name', 'framework')} {statement}",
                gap_type=GapType.VALIDATION,
                belief_id=f"theory:{getattr(framework, 'theory_id', 'unknown')}",
            )

            target = ResearchTarget(
                target_id=f"theory:{getattr(framework, 'theory_id', 'unknown')}:{getattr(prediction, 'prediction_id', statement[:24])}",
                gap_type=GapType.VALIDATION,
                gap_id=getattr(prediction, "prediction_id", ""),
                gap_description=f"{getattr(framework, 'name', 'Framework')} predicts: {statement}",
                theory_drivers=[getattr(framework, "theory_id", "")],
                mechanism_predictions=[statement],
                voi_score=voi,
                structural_voi=min(0.4 + GAP_TYPE_WEIGHTS.get(GapType.VALIDATION, 0.5) * 0.3, 1.0),
                epistemic_voi=1.0 - support_score,
                priority=priority,
                priority_rationale=(
                    f"theory-driven validation gap ({getattr(framework, 'theory_id', 'unknown')}); "
                    f"support={support_score:.2f}"
                ),
                suggested_queries=q,
                cross_field_terms=self._extract_cross_field_terms(q),
                target_databases=self.DEFAULT_TARGET_DATABASES.copy(),
                status=TargetStatus.OPEN,
            )
            targets.append(target)

        return targets

    def get_target(self, target_id: str) -> Optional[ResearchTarget]:
        return self._targets.get(target_id)

    def list_targets(self) -> list[ResearchTarget]:
        return sorted(
            self._targets.values(),
            key=lambda t: (self._priority_rank(t.priority), t.voi_score),
            reverse=True,
        )

    def set_target_status(
        self,
        target_id: str,
        status: TargetStatus,
        assigned_to: Optional[str] = None,
    ) -> Optional[ResearchTarget]:
        """Manually update a target status (dashboard/admin workflow)."""
        target = self._targets.get(target_id)
        if target is None:
            return None
        target.status = status
        if assigned_to is not None:
            target.assigned_to = assigned_to
        if status in {TargetStatus.OPEN, TargetStatus.CLOSED, TargetStatus.STALE} and assigned_to is None:
            # Clear assignment for terminal states unless explicitly overridden.
            target.assigned_to = None
        target.updated_at = datetime.now(timezone.utc)
        self._persist_state()
        return target

    def get_dashboard_snapshot(self) -> dict[str, Any]:
        """Aggregate queue state for Streamlit/dashboard use."""
        targets = list(self._targets.values())
        by_status = {s.value: 0 for s in TargetStatus}
        by_priority = {p.value: 0 for p in Priority}
        for t in targets:
            by_status[t.status.value] = by_status.get(t.status.value, 0) + 1
            by_priority[t.priority.value] = by_priority.get(t.priority.value, 0) + 1

        return {
            "queue_id": self._queue_id,
            "n_targets": len(targets),
            "by_status": by_status,
            "by_priority": by_priority,
            "n_collectors": len(self._collectors),
            "n_opportunities": len(self._opportunities),
            "top_targets": [
                t.to_dict()
                for t in sorted(
                    targets,
                    key=lambda x: (self._priority_rank(x.priority), x.voi_score),
                    reverse=True,
                )[:10]
            ],
            "updated_at": iso_z(datetime.now(timezone.utc)),
        }

    def sync_zotero_to_queue(
        self,
        bibtex_path: str | Path,
        collector_id: str = "zotero_watcher",
        state_path: str | Path = "data/production/zotero_watcher_state.json",
        min_score: float = 0.18,
    ) -> list[ArticleReference]:
        """
        Passively match newly added Zotero/BibTeX entries to open queue targets.

        Returns:
            List of matched article references.
        """
        from src.queue.zotero_watcher import ZoteroWatcher

        watcher = ZoteroWatcher(bibtex_path=bibtex_path, state_path=state_path)
        matches = watcher.sync_to_queue(
            queue_service=self,
            collector_id=collector_id,
            min_score=min_score,
        )
        if matches:
            self._persist_state()
        return matches

    def run_automated_searcher(
        self,
        max_targets_per_run: int = 3,
        max_queries_per_target: int = 3,
        max_results_per_query: int = 10,
        min_relevance: float = 0.25,
    ) -> list[dict[str, Any]]:
        """
        Run the default automated searcher bot for one screening cycle.
        """
        from src.queue.automated_searcher import AutomatedQueueSearcher, AutomatedSearcherConfig

        bot = AutomatedQueueSearcher(
            queue_service=self,
            config=AutomatedSearcherConfig(
                max_targets_per_run=max_targets_per_run,
                max_queries_per_target=max_queries_per_target,
                max_results_per_query=max_results_per_query,
                min_relevance=min_relevance,
            ),
        )
        runs = bot.run_once()
        return [
            {
                "target_id": r.target_id,
                "status": r.status,
                "n_candidates": r.n_candidates,
                "top_titles": r.top_titles,
                "message": r.message,
            }
            for r in runs
        ]

    def _ensure_opportunity_for_target(
        self, target: ResearchTarget, result: SearchResult
    ) -> ResearchOpportunity:
        # Reuse existing opportunity for this target if available.
        for opportunity in self._opportunities.values():
            if opportunity.source_target_id == target.target_id:
                return opportunity

        null_ev = result.null_result_evidence
        opportunity_id = f"opp:{target.target_id}:{uuid.uuid4().hex[:8]}"
        opportunity = ResearchOpportunity(
            opportunity_id=opportunity_id,
            source_target_id=target.target_id,
            gap_description=target.gap_description,
            theory_drivers=target.theory_drivers.copy(),
            mechanism_to_test=(
                target.mechanism_predictions[0]
                if target.mechanism_predictions
                else target.gap_description
            ),
            voi_score=target.voi_score,
            impact_rationale=target.priority_rationale,
            suggested_design=(
                null_ev.suggested_study_design
                if null_ev and null_ev.suggested_study_design
                else "quasi-experimental"
            ),
            suggested_population=(
                null_ev.suggested_population
                if null_ev and null_ev.suggested_population
                else "adults"
            ),
            suggested_setting=(
                null_ev.suggested_setting
                if null_ev and null_ev.suggested_setting
                else "real-world built environment"
            ),
            suggested_measures=[
                "subjective_outcome",
                "objective_behavioral_outcome",
                "physiological_marker",
            ],
            predicted_finding=(
                result.research_opportunity_framing
                or target.opportunity_framing
                or "intervention is expected to affect target outcome under scoped conditions"
            ),
            null_hypothesis="no difference across environmental conditions",
            status=OpportunityStatus.PROPOSED,
            created_by=result.collector_id or "system",
        )
        self._opportunities[opportunity_id] = opportunity
        return opportunity

    def _build_search_guidance(
        self, target: ResearchTarget, collector: CollectorProfile
    ) -> SearchGuidance:
        primary_queries = target.suggested_queries[:5]

        expanded_queries: list[str] = []
        qgen = self.query_generator
        if not isinstance(qgen, _FallbackQueryGenerator):
            try:
                for q in primary_queries[:3]:
                    for variant in qgen.expand_query_terms(
                        q,
                        target_fields=["psychology", "neuroscience", "architecture", "medicine"],
                    )[:2]:
                        if variant not in expanded_queries and variant not in primary_queries:
                            expanded_queries.append(variant)
            except Exception:
                pass
        if not expanded_queries:
            expanded_queries = [q + " review" for q in primary_queries[:2]]

        boolean_terms = []
        if primary_queries:
            boolean_terms.append(f"({primary_queries[0]})")
        if target.cross_field_terms:
            boolean_terms.append("(" + " OR ".join([f"\"{t}\"" for t in target.cross_field_terms[:4]]) + ")")
        boolean_query = " AND ".join(boolean_terms) if boolean_terms else ""

        collector_dbs = set(collector.can_access_databases or self.DEFAULT_TARGET_DATABASES)
        preferred_dbs = [d for d in target.target_databases if d in collector_dbs]
        databases = preferred_dbs or sorted(collector_dbs)

        if target.gap_type == GapType.VALIDATION:
            study_types = ["meta-analysis", "direct_replication", "quasi-experimental"]
            expected = "find evidence that confirms or falsifies the predicted effect pattern"
        elif target.gap_type == GapType.MECHANISM:
            study_types = ["mechanistic", "mediation", "experimental"]
            expected = "identify pathway-level evidence linking environment to outcome"
        elif target.gap_type == GapType.BOUNDARY:
            study_types = ["moderation", "subgroup_analysis", "field_study"]
            expected = "identify where the effect holds versus breaks"
        else:
            study_types = ["experimental", "longitudinal", "systematic_review"]
            expected = "resolve directional or structural uncertainty"

        return SearchGuidance(
            primary_queries=primary_queries,
            expanded_queries=expanded_queries,
            boolean_query=boolean_query,
            databases=databases,
            target_study_types=study_types,
            target_populations=["adults", "students", "patients"],
            target_settings=["healthcare", "workplace", "education"],
            mechanism_to_test=(
                target.mechanism_predictions[0]
                if target.mechanism_predictions
                else target.gap_description
            ),
            expected_finding_pattern=expected,
            null_result_indicators=[
                "no relevant records across multiple databases",
                "only tangential papers after term expansion",
                "repeated terminology mismatch across fields",
            ],
            when_to_stop=(
                f"Stop after {int(max(1.0, collector.typical_turnaround_hours))}h or after screening 50 results "
                "without relevant matches."
            ),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _target_from_predicted_gap(self, gap: Any) -> ResearchTarget:
        voi = float(getattr(gap, "voi_score", 0.0) or 0.0)
        gap_type = getattr(gap, "gap_type", GapType.MECHANISM)
        if isinstance(gap_type, str):
            gap_type = GapType(gap_type)

        description = (getattr(gap, "description", "") or "").strip()
        gap_id = str(getattr(gap, "gap_id", "unknown_gap"))
        belief_id = self._pick_belief_id(gap)

        suggested_queries = self._build_queries_from_text(description, gap_type, belief_id)

        structural_weight = GAP_TYPE_WEIGHTS.get(gap_type, 0.5)
        structural_voi = min(voi * (0.5 + structural_weight * 0.5), 1.0)
        epistemic_voi = max(0.0, min(voi * (1.0 - structural_weight * 0.4), 1.0))

        return ResearchTarget(
            target_id=f"gap:{gap_id}",
            gap_type=gap_type,
            gap_id=gap_id,
            gap_description=description,
            theory_drivers=[],
            mechanism_predictions=self._maybe_mechanism_prediction(gap),
            voi_score=voi,
            structural_voi=structural_voi,
            epistemic_voi=epistemic_voi,
            priority=self._priority_bucket(voi),
            priority_rationale=(
                f"gap={gap_type.value}; voi={voi:.2f}; weight={structural_weight:.2f}"
            ),
            suggested_queries=suggested_queries,
            cross_field_terms=self._extract_cross_field_terms(suggested_queries),
            target_databases=self.DEFAULT_TARGET_DATABASES.copy(),
            status=TargetStatus.OPEN,
            affected_beliefs=list(getattr(gap, "affected_beliefs", []) or []),
        )

    def _build_queries_from_text(self, text: str, gap_type: GapType, belief_id: str) -> list[str]:
        query_seed = (text or "").strip() or "architectural cognition mechanism"
        qgen = self.query_generator
        if isinstance(qgen, _FallbackQueryGenerator):
            generated = qgen.generate_queries(query_seed, gap_type, max_queries=5)
            cross = qgen.generate_cross_field_queries(query_seed, max_queries=3)
        else:
            from src.services.voi_search import EpistemicGap

            ep_gap = EpistemicGap(
                gap_type=gap_type,
                description=query_seed,
                primary_belief_id=belief_id,
                voi_score=0.5,
            )
            generated = qgen.generate_queries(ep_gap, belief=None, max_queries=5)
            cross = qgen.generate_cross_field_queries(
                ep_gap,
                belief=None,
                target_fields=["psychology", "neuroscience", "architecture", "medicine"],
                max_queries=3,
            )
        merged = []
        seen = set()
        for q in generated + cross:
            norm = q.strip().lower()
            if not norm or norm in seen:
                continue
            seen.add(norm)
            merged.append(q.strip())
        return merged[:8]

    def _extract_cross_field_terms(self, queries: list[str]) -> list[str]:
        terms: list[str] = []
        seen = set()
        for q in queries:
            for token in re.findall(r'"([^"]+)"', q):
                norm = token.lower().strip()
                if norm and norm not in seen:
                    seen.add(norm)
                    terms.append(token)
        return terms[:20]

    def _maybe_mechanism_prediction(self, gap: Any) -> list[str]:
        implied = list(getattr(gap, "implied_by", []) or [])
        if implied:
            return implied[:2]
        desc = (getattr(gap, "description", "") or "").strip()
        return [desc] if desc else []

    def _pick_belief_id(self, gap: Any) -> str:
        beliefs = list(getattr(gap, "affected_beliefs", []) or [])
        if beliefs:
            return beliefs[0]
        edge = getattr(gap, "affected_edge", None)
        if edge:
            return str(edge)
        return "unknown_belief"

    def _priority_bucket(self, score: float) -> Priority:
        if score >= 0.7:
            return Priority.HIGH
        if score >= 0.4:
            return Priority.MEDIUM
        return Priority.LOW

    def _priority_rank(self, priority: Priority) -> int:
        if priority == Priority.HIGH:
            return 3
        if priority == Priority.MEDIUM:
            return 2
        return 1

    def _active_assignments(self, collector_id: str) -> int:
        return sum(
            1
            for t in self._targets.values()
            if t.assigned_to == collector_id and t.status == TargetStatus.SEARCHING
        )

    def _prediction_support_score(self, framework_id: str, statement: str) -> float:
        """Approximate support by matching prediction text to existing beliefs."""
        web = self.web
        if web is None or not getattr(web, "beliefs", None):
            return 0.0

        pred_tokens = self._tokenize(statement)
        if not pred_tokens:
            return 0.0

        best = 0.0
        for belief in getattr(web, "beliefs", {}).values():
            content = (getattr(belief, "content", "") or "").strip()
            if not content:
                continue
            credence = float(getattr(getattr(belief, "credence", None), "value", 0.5) or 0.5)

            belief_tokens = self._tokenize(content)
            if not belief_tokens:
                continue
            overlap = len(pred_tokens.intersection(belief_tokens)) / float(len(pred_tokens))
            score = min(1.0, overlap * credence)
            if framework_id and getattr(belief, "theory_id", None) == framework_id:
                # Same-theory beliefs are somewhat more relevant, but still require textual overlap.
                score = min(1.0, score + 0.15)
            best = max(best, score)

        return best

    def _tokenize(self, text: str) -> set[str]:
        return {t for t in re.findall(r"[a-zA-Z][a-zA-Z0-9_\-]+", text.lower()) if len(t) > 3}

    def _get_frameworks(self) -> list[Any]:
        if self._frameworks is not None:
            return self._frameworks
        try:
            self._frameworks = get_tier1_frameworks()
        except Exception as exc:
            logger.warning("ResearchQueueService: failed to load frameworks (%s)", exc)
            self._frameworks = []
        return self._frameworks

    def _build_state(self) -> ResearchQueueState:
        targets = list(self._targets.values())
        high = [t for t in targets if t.priority == Priority.HIGH]
        medium = [t for t in targets if t.priority == Priority.MEDIUM]
        low = [t for t in targets if t.priority == Priority.LOW]

        for bucket in (high, medium, low):
            bucket.sort(key=lambda t: t.voi_score, reverse=True)

        opportunities = [t for t in targets if t.is_research_opportunity]
        opportunities.sort(key=lambda t: t.voi_score, reverse=True)

        theory_coverage = self._compute_theory_coverage()

        return ResearchQueueState(
            queue_id=self._queue_id,
            generated_at=datetime.now(timezone.utc),
            high_priority=high,
            medium_priority=medium,
            low_priority=low,
            research_opportunities=opportunities,
            n_open=sum(1 for t in targets if t.status == TargetStatus.OPEN),
            n_searching=sum(1 for t in targets if t.status == TargetStatus.SEARCHING),
            n_found=sum(1 for t in targets if t.status == TargetStatus.FOUND),
            n_closed=sum(1 for t in targets if t.status == TargetStatus.CLOSED),
            theory_coverage=theory_coverage,
        )

    def _compute_theory_coverage(self) -> dict[str, float]:
        coverage: dict[str, float] = {}
        frameworks = self._get_frameworks()
        if not frameworks:
            return coverage

        for framework in frameworks:
            fw_id = getattr(framework, "theory_id", "")
            if not fw_id:
                continue
            predictions = list(getattr(framework, "all_predictions", []))
            if not predictions:
                coverage[fw_id] = 0.0
                continue

            supported = 0
            for prediction in predictions:
                statement = (getattr(prediction, "statement", "") or "").strip()
                if statement and self._prediction_support_score(fw_id, statement) >= 0.5:
                    supported += 1
            coverage[fw_id] = round(supported / float(len(predictions)), 4)

        return coverage

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _persist_state(self) -> None:
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "ae.research_queue.v1",
            "queue_id": self._queue_id,
            "saved_at": iso_z(datetime.now(timezone.utc)),
            "targets": [t.to_dict() for t in self._targets.values()],
            "collectors": [c.to_dict() for c in self._collectors.values()],
            "research_opportunities": [o.to_dict() for o in self._opportunities.values()],
        }
        with self.queue_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=True)
            f.write("\n")

    def _load_state(self) -> None:
        if not self.queue_path.exists():
            return
        try:
            with self.queue_path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            self._queue_id = payload.get("queue_id", self._queue_id)
            targets = payload.get("targets", [])
            self._targets = {t["target_id"]: ResearchTarget.from_dict(t) for t in targets}
            collectors = payload.get("collectors", [])
            self._collectors = {
                c["collector_id"]: CollectorProfile.from_dict(c) for c in collectors if c.get("collector_id")
            }
            opportunities = payload.get("research_opportunities", [])
            self._opportunities = {
                o["opportunity_id"]: ResearchOpportunity.from_dict(o)
                for o in opportunities
                if o.get("opportunity_id")
            }
        except Exception as exc:
            logger.warning("ResearchQueueService: failed to load prior state (%s)", exc)
            self._targets = {}
            self._collectors = {}
            self._opportunities = {}


__all__ = ["ResearchQueueService"]
