"""Automated queue searcher using Semantic Scholar query expansion.

Implements Sprint 9 I9.7: an automated searcher bot that claims queue targets,
runs bulk screening queries, and reports outcomes back to the queue.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from src.queue.models import (
    ArticleReference,
    CollectorProfile,
    CollectorType,
    SearchResult,
    SearchResultType,
)


@dataclass
class AutomatedSearcherConfig:
    collector_id: str = "auto_searcher"
    collector_name: str = "Automated Searcher"
    max_targets_per_run: int = 3
    max_queries_per_target: int = 3
    max_results_per_query: int = 10
    min_relevance: float = 0.25


@dataclass
class AutomatedTargetRun:
    target_id: str
    status: str
    n_candidates: int
    top_titles: list[str] = field(default_factory=list)
    message: str = ""


class AutomatedQueueSearcher:
    """Automated collector that bulk-screens candidate papers for open targets."""

    def __init__(
        self,
        queue_service: Any,
        search_fn: Optional[Callable[..., list[dict[str, Any]]]] = None,
        config: Optional[AutomatedSearcherConfig] = None,
    ):
        self.queue_service = queue_service
        self.config = config or AutomatedSearcherConfig()
        if search_fn is not None:
            self.search_fn = search_fn
        else:
            from app.services.semantic_scholar import search as semantic_scholar_search

            self.search_fn = semantic_scholar_search

        self._ensure_collector_registered()

    def _ensure_collector_registered(self) -> None:
        collector = self.queue_service.get_collector(self.config.collector_id)
        if collector is not None:
            return
        self.queue_service.register_collector(
            CollectorProfile(
                collector_id=self.config.collector_id,
                collector_type=CollectorType.AUTOMATED_SEARCHER,
                name=self.config.collector_name,
                can_access_databases=["semantic_scholar"],
                can_access_paywalled=False,
                preferred_domains=["architecture", "psychology", "neuroscience"],
                max_concurrent_targets=1,
                typical_turnaround_hours=1.0,
            )
        )

    def run_once(self) -> list[AutomatedTargetRun]:
        """Claim and process up to max_targets_per_run open queue targets."""
        runs: list[AutomatedTargetRun] = []

        for _ in range(self.config.max_targets_per_run):
            claim = self.queue_service.claim_target(self.config.collector_id)
            if not claim.success or claim.target is None or claim.search_guidance is None:
                break

            target = claim.target
            guidance = claim.search_guidance
            queries = guidance.primary_queries[: self.config.max_queries_per_target]
            if not queries:
                queries = [target.gap_description]

            candidates = self._run_queries(queries)
            if candidates:
                result_type = SearchResultType.FOUND_RELEVANT
                notes = "automated screening found candidate papers"
            else:
                result_type = SearchResultType.NOT_FOUND
                notes = "automated screening found no candidate papers"

            assessment = self.queue_service.report_search_result(
                target_id=target.target_id,
                result=SearchResult(
                    collector_id=self.config.collector_id,
                    result_type=result_type,
                    queries_used=queries,
                    databases_searched=["semantic_scholar"],
                    time_spent_minutes=1,
                    articles_found=candidates,
                    confidence=0.6 if candidates else 0.35,
                    notes=notes,
                    is_research_opportunity=(result_type == SearchResultType.NOT_FOUND),
                    research_opportunity_framing=(
                        f"No indexed papers found for: {target.gap_description}" if not candidates else None
                    ),
                ),
            )

            runs.append(
                AutomatedTargetRun(
                    target_id=target.target_id,
                    status=assessment.status.value,
                    n_candidates=len(candidates),
                    top_titles=[c.title for c in candidates[:3]],
                    message=assessment.message,
                )
            )

        return runs

    def _run_queries(self, queries: list[str]) -> list[ArticleReference]:
        """Execute search queries and convert scored hits to ArticleReference objects."""
        found: dict[str, ArticleReference] = {}

        for query in queries:
            rows = self.search_fn(query, limit=self.config.max_results_per_query)
            for row in rows or []:
                ref = self._row_to_reference(row)
                if ref is None:
                    continue
                key = (ref.doi or ref.title or "").lower().strip()
                if not key:
                    continue
                if key not in found or ref.relevance_score > found[key].relevance_score:
                    found[key] = ref

        return sorted(found.values(), key=lambda x: x.relevance_score, reverse=True)

    def _row_to_reference(self, row: dict[str, Any]) -> Optional[ArticleReference]:
        title = (row.get("title") or "").strip()
        if not title:
            return None

        abstract = (row.get("abstract") or "").strip()
        citation_count = int(row.get("citationCount", 0) or 0)
        has_abstract = 1.0 if abstract else 0.0
        citation_score = min(citation_count / 100.0, 1.0)
        relevance = round((0.55 * has_abstract) + (0.45 * citation_score), 4)
        if relevance < self.config.min_relevance:
            return None

        external_ids = row.get("externalIds") or {}
        doi = external_ids.get("DOI") if isinstance(external_ids, dict) else None

        authors_raw = row.get("authors") or []
        authors: list[str] = []
        for a in authors_raw:
            if isinstance(a, dict) and a.get("name"):
                authors.append(str(a["name"]))

        url = row.get("url")
        return ArticleReference(
            doi=doi,
            title=title,
            authors=authors,
            year=row.get("year"),
            venue="",
            relevance_score=relevance,
            relevance_rationale=f"abstract_present={bool(abstract)} citation_count={citation_count}",
            pdf_available=False,
            pdf_path=None,
            retrieval_method="semantic_scholar",
            addresses_gap=True,
            gap_closure_estimate=min(1.0, max(0.2, relevance)),
        )


__all__ = ["AutomatedQueueSearcher", "AutomatedSearcherConfig", "AutomatedTargetRun"]
