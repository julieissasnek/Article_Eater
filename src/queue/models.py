"""Research Queue data models.

Implements the contract models for ae.research_queue.v1 and
collector-facing search reporting types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from src.epistemic.gap_types import GapType


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_iso_z(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TargetStatus(str, Enum):
    OPEN = "open"
    SEARCHING = "searching"
    FOUND = "found"
    CLOSED = "closed"
    STALE = "stale"


class SearchResultType(str, Enum):
    FOUND_RELEVANT = "found_relevant"
    FOUND_TANGENTIAL = "found_tangential"
    NOT_FOUND = "not_found"
    INCONCLUSIVE = "inconclusive"


class CollectorType(str, Enum):
    HUMAN_RESEARCHER = "human_researcher"
    HUMAN_ASSISTANT = "human_assistant"
    AUTOMATED_SEARCHER = "automated_searcher"
    ZOTERO_WATCHER = "zotero_watcher"


class QueueEvent(str, Enum):
    TARGET_CREATED = "target_created"
    TARGET_ASSIGNED = "target_assigned"
    SEARCH_COMPLETED = "search_completed"
    ARTICLES_FOUND = "articles_found"
    NO_ARTICLES_FOUND = "no_articles_found"
    RESEARCH_OPPORTUNITY_IDENTIFIED = "research_opportunity_identified"
    GAP_CLOSED = "gap_closed"


class OpportunityStatus(str, Enum):
    PROPOSED = "proposed"
    VALIDATED = "validated"
    IN_PROGRESS = "in_progress"
    PUBLISHED = "published"


@dataclass
class CollectorProfile:
    """Profile for a VOI collector."""

    collector_id: str
    collector_type: CollectorType
    name: str
    can_access_databases: list[str] = field(default_factory=list)
    can_access_paywalled: bool = False
    preferred_domains: list[str] = field(default_factory=list)
    max_concurrent_targets: int = 1
    typical_turnaround_hours: float = 24.0
    targets_completed: int = 0
    gap_closure_rate: float = 0.0
    avg_articles_per_target: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "collector_id": self.collector_id,
            "collector_type": self.collector_type.value,
            "name": self.name,
            "can_access_databases": self.can_access_databases,
            "can_access_paywalled": self.can_access_paywalled,
            "preferred_domains": self.preferred_domains,
            "max_concurrent_targets": self.max_concurrent_targets,
            "typical_turnaround_hours": self.typical_turnaround_hours,
            "targets_completed": self.targets_completed,
            "gap_closure_rate": self.gap_closure_rate,
            "avg_articles_per_target": self.avg_articles_per_target,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CollectorProfile":
        return cls(
            collector_id=data["collector_id"],
            collector_type=CollectorType(data.get("collector_type", CollectorType.HUMAN_ASSISTANT.value)),
            name=data.get("name", data.get("collector_id", "collector")),
            can_access_databases=list(data.get("can_access_databases") or []),
            can_access_paywalled=bool(data.get("can_access_paywalled", False)),
            preferred_domains=list(data.get("preferred_domains") or []),
            max_concurrent_targets=int(data.get("max_concurrent_targets", 1)),
            typical_turnaround_hours=float(data.get("typical_turnaround_hours", 24.0)),
            targets_completed=int(data.get("targets_completed", 0)),
            gap_closure_rate=float(data.get("gap_closure_rate", 0.0)),
            avg_articles_per_target=float(data.get("avg_articles_per_target", 0.0)),
        )


@dataclass
class SearchGuidance:
    """Guidance payload returned when a collector claims a target."""

    primary_queries: list[str] = field(default_factory=list)
    expanded_queries: list[str] = field(default_factory=list)
    boolean_query: str = ""
    databases: list[str] = field(default_factory=list)
    target_study_types: list[str] = field(default_factory=list)
    target_populations: list[str] = field(default_factory=list)
    target_settings: list[str] = field(default_factory=list)
    mechanism_to_test: str = ""
    expected_finding_pattern: str = ""
    null_result_indicators: list[str] = field(default_factory=list)
    when_to_stop: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "primary_queries": self.primary_queries,
            "expanded_queries": self.expanded_queries,
            "boolean_query": self.boolean_query,
            "databases": self.databases,
            "target_study_types": self.target_study_types,
            "target_populations": self.target_populations,
            "target_settings": self.target_settings,
            "mechanism_to_test": self.mechanism_to_test,
            "expected_finding_pattern": self.expected_finding_pattern,
            "null_result_indicators": self.null_result_indicators,
            "when_to_stop": self.when_to_stop,
        }


@dataclass
class ClaimResult:
    """Result of a collector claim operation."""

    success: bool
    target: Optional["ResearchTarget"] = None
    search_guidance: Optional[SearchGuidance] = None
    deadline: Optional[datetime] = None
    message: str = ""


@dataclass
class ResearchOpportunity:
    """A gap that likely requires new primary research."""

    opportunity_id: str
    source_target_id: str
    gap_description: str
    theory_drivers: list[str] = field(default_factory=list)
    mechanism_to_test: str = ""
    voi_score: float = 0.0
    impact_rationale: str = ""
    suggested_design: str = ""
    suggested_population: str = ""
    suggested_setting: str = ""
    suggested_measures: list[str] = field(default_factory=list)
    predicted_finding: str = ""
    null_hypothesis: str = ""
    status: OpportunityStatus = OpportunityStatus.PROPOSED
    researcher_contact: Optional[str] = None
    publication_doi: Optional[str] = None
    created_at: datetime = field(default_factory=utc_now)
    created_by: str = "system"

    def to_dict(self) -> dict[str, Any]:
        return {
            "opportunity_id": self.opportunity_id,
            "source_target_id": self.source_target_id,
            "gap_description": self.gap_description,
            "theory_drivers": self.theory_drivers,
            "mechanism_to_test": self.mechanism_to_test,
            "voi_score": self.voi_score,
            "impact_rationale": self.impact_rationale,
            "suggested_design": self.suggested_design,
            "suggested_population": self.suggested_population,
            "suggested_setting": self.suggested_setting,
            "suggested_measures": self.suggested_measures,
            "predicted_finding": self.predicted_finding,
            "null_hypothesis": self.null_hypothesis,
            "status": self.status.value,
            "researcher_contact": self.researcher_contact,
            "publication_doi": self.publication_doi,
            "created_at": iso_z(self.created_at),
            "created_by": self.created_by,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchOpportunity":
        return cls(
            opportunity_id=data["opportunity_id"],
            source_target_id=data.get("source_target_id", ""),
            gap_description=data.get("gap_description", ""),
            theory_drivers=list(data.get("theory_drivers") or []),
            mechanism_to_test=data.get("mechanism_to_test", ""),
            voi_score=float(data.get("voi_score", 0.0)),
            impact_rationale=data.get("impact_rationale", ""),
            suggested_design=data.get("suggested_design", ""),
            suggested_population=data.get("suggested_population", ""),
            suggested_setting=data.get("suggested_setting", ""),
            suggested_measures=list(data.get("suggested_measures") or []),
            predicted_finding=data.get("predicted_finding", ""),
            null_hypothesis=data.get("null_hypothesis", ""),
            status=OpportunityStatus(data.get("status", OpportunityStatus.PROPOSED.value)),
            researcher_contact=data.get("researcher_contact"),
            publication_doi=data.get("publication_doi"),
            created_at=parse_iso_z(data.get("created_at", iso_z(utc_now()))),
            created_by=data.get("created_by", "system"),
        )


@dataclass
class ArticleReference:
    """Reference to an article found by a collector."""

    doi: Optional[str]
    title: str
    authors: list[str] = field(default_factory=list)
    year: Optional[int] = None
    venue: str = ""
    relevance_score: float = 0.5
    relevance_rationale: str = ""
    pdf_available: bool = False
    pdf_path: Optional[str] = None
    retrieval_method: Optional[str] = None
    addresses_gap: bool = True
    gap_closure_estimate: float = 0.3

    def to_dict(self) -> dict[str, Any]:
        return {
            "doi": self.doi,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "venue": self.venue,
            "relevance_score": self.relevance_score,
            "relevance_rationale": self.relevance_rationale,
            "pdf_available": self.pdf_available,
            "pdf_path": self.pdf_path,
            "retrieval_method": self.retrieval_method,
            "addresses_gap": self.addresses_gap,
            "gap_closure_estimate": self.gap_closure_estimate,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArticleReference":
        return cls(
            doi=data.get("doi"),
            title=data.get("title", ""),
            authors=list(data.get("authors") or []),
            year=data.get("year"),
            venue=data.get("venue", ""),
            relevance_score=float(data.get("relevance_score", 0.5)),
            relevance_rationale=data.get("relevance_rationale", ""),
            pdf_available=bool(data.get("pdf_available", False)),
            pdf_path=data.get("pdf_path"),
            retrieval_method=data.get("retrieval_method"),
            addresses_gap=bool(data.get("addresses_gap", True)),
            gap_closure_estimate=float(data.get("gap_closure_estimate", 0.3)),
        )


@dataclass
class NullResultEvidence:
    """Evidence that a target appears unstudied in existing literature."""

    n_databases_searched: int = 0
    n_queries_tried: int = 0
    n_results_screened: int = 0
    reason: str = "topic_unstudied"
    confidence_is_gap: float = 0.5
    suggested_study_design: str = ""
    suggested_population: str = ""
    suggested_setting: str = ""
    predicted_contribution: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_databases_searched": self.n_databases_searched,
            "n_queries_tried": self.n_queries_tried,
            "n_results_screened": self.n_results_screened,
            "reason": self.reason,
            "confidence_is_gap": self.confidence_is_gap,
            "suggested_study_design": self.suggested_study_design,
            "suggested_population": self.suggested_population,
            "suggested_setting": self.suggested_setting,
            "predicted_contribution": self.predicted_contribution,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NullResultEvidence":
        return cls(
            n_databases_searched=int(data.get("n_databases_searched", 0)),
            n_queries_tried=int(data.get("n_queries_tried", 0)),
            n_results_screened=int(data.get("n_results_screened", 0)),
            reason=data.get("reason", "topic_unstudied"),
            confidence_is_gap=float(data.get("confidence_is_gap", 0.5)),
            suggested_study_design=data.get("suggested_study_design", ""),
            suggested_population=data.get("suggested_population", ""),
            suggested_setting=data.get("suggested_setting", ""),
            predicted_contribution=data.get("predicted_contribution", ""),
        )


@dataclass
class SearchResult:
    """Result submitted by a human or automated VOI collector."""

    collector_id: str
    result_type: SearchResultType
    queries_used: list[str] = field(default_factory=list)
    databases_searched: list[str] = field(default_factory=list)
    time_spent_minutes: int = 0
    articles_found: list[ArticleReference] = field(default_factory=list)
    null_result_evidence: Optional[NullResultEvidence] = None
    confidence: float = 0.5
    notes: str = ""
    is_research_opportunity: bool = False
    research_opportunity_framing: Optional[str] = None


@dataclass
class ClosureAssessment:
    """Outcome of reporting a target search result."""

    target_id: str
    status: TargetStatus
    closed: bool
    became_research_opportunity: bool
    n_articles_found: int
    message: str


@dataclass
class ResearchTarget:
    """A prioritized research target in the queue."""

    target_id: str

    # Gap framing
    gap_type: GapType
    gap_id: str
    gap_description: str

    # Theory-driven context
    theory_drivers: list[str] = field(default_factory=list)
    mechanism_predictions: list[str] = field(default_factory=list)

    # Priority and VOI
    voi_score: float = 0.0
    structural_voi: float = 0.0
    epistemic_voi: float = 0.0
    priority: Priority = Priority.LOW
    priority_rationale: str = ""

    # Search guidance
    suggested_queries: list[str] = field(default_factory=list)
    cross_field_terms: list[str] = field(default_factory=list)
    target_databases: list[str] = field(default_factory=list)

    # Research opportunity framing
    is_research_opportunity: bool = False
    opportunity_framing: Optional[str] = None

    # Status
    status: TargetStatus = TargetStatus.OPEN
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    # Optional context
    affected_beliefs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "gap_type": self.gap_type.value,
            "gap_id": self.gap_id,
            "gap_description": self.gap_description,
            "theory_drivers": self.theory_drivers,
            "mechanism_predictions": self.mechanism_predictions,
            "voi_score": self.voi_score,
            "structural_voi": self.structural_voi,
            "epistemic_voi": self.epistemic_voi,
            "priority": self.priority.value,
            "priority_rationale": self.priority_rationale,
            "suggested_queries": self.suggested_queries,
            "cross_field_terms": self.cross_field_terms,
            "target_databases": self.target_databases,
            "is_research_opportunity": self.is_research_opportunity,
            "opportunity_framing": self.opportunity_framing,
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "created_at": iso_z(self.created_at),
            "updated_at": iso_z(self.updated_at),
            "affected_beliefs": self.affected_beliefs,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchTarget":
        return cls(
            target_id=data["target_id"],
            gap_type=GapType(data["gap_type"]),
            gap_id=data.get("gap_id", data.get("target_id", "")),
            gap_description=data.get("gap_description", ""),
            theory_drivers=list(data.get("theory_drivers") or []),
            mechanism_predictions=list(data.get("mechanism_predictions") or []),
            voi_score=float(data.get("voi_score", 0.0)),
            structural_voi=float(data.get("structural_voi", 0.0)),
            epistemic_voi=float(data.get("epistemic_voi", 0.0)),
            priority=Priority(data.get("priority", Priority.LOW.value)),
            priority_rationale=data.get("priority_rationale", ""),
            suggested_queries=list(data.get("suggested_queries") or []),
            cross_field_terms=list(data.get("cross_field_terms") or []),
            target_databases=list(data.get("target_databases") or []),
            is_research_opportunity=bool(data.get("is_research_opportunity", False)),
            opportunity_framing=data.get("opportunity_framing"),
            status=TargetStatus(data.get("status", TargetStatus.OPEN.value)),
            assigned_to=data.get("assigned_to"),
            created_at=parse_iso_z(data.get("created_at", iso_z(utc_now()))),
            updated_at=parse_iso_z(data.get("updated_at", iso_z(utc_now()))),
            affected_beliefs=list(data.get("affected_beliefs") or []),
        )


@dataclass
class ResearchQueueState:
    """Complete queue state with prioritized target buckets."""

    queue_id: str
    generated_at: datetime
    high_priority: list[ResearchTarget] = field(default_factory=list)
    medium_priority: list[ResearchTarget] = field(default_factory=list)
    low_priority: list[ResearchTarget] = field(default_factory=list)
    research_opportunities: list[ResearchTarget] = field(default_factory=list)
    n_open: int = 0
    n_searching: int = 0
    n_found: int = 0
    n_closed: int = 0
    theory_coverage: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ae.research_queue.v1",
            "queue_id": self.queue_id,
            "generated_at": iso_z(self.generated_at),
            "high_priority": [t.to_dict() for t in self.high_priority],
            "medium_priority": [t.to_dict() for t in self.medium_priority],
            "low_priority": [t.to_dict() for t in self.low_priority],
            "research_opportunities": [t.to_dict() for t in self.research_opportunities],
            "n_open": self.n_open,
            "n_searching": self.n_searching,
            "n_found": self.n_found,
            "n_closed": self.n_closed,
            "theory_coverage": self.theory_coverage,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchQueueState":
        return cls(
            queue_id=data.get("queue_id", "queue"),
            generated_at=parse_iso_z(data.get("generated_at", iso_z(utc_now()))),
            high_priority=[ResearchTarget.from_dict(d) for d in data.get("high_priority", [])],
            medium_priority=[ResearchTarget.from_dict(d) for d in data.get("medium_priority", [])],
            low_priority=[ResearchTarget.from_dict(d) for d in data.get("low_priority", [])],
            research_opportunities=[
                ResearchTarget.from_dict(d) for d in data.get("research_opportunities", [])
            ],
            n_open=int(data.get("n_open", 0)),
            n_searching=int(data.get("n_searching", 0)),
            n_found=int(data.get("n_found", 0)),
            n_closed=int(data.get("n_closed", 0)),
            theory_coverage=dict(data.get("theory_coverage", {})),
        )
