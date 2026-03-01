"""
Paper Integration Pipeline — Data Models
=========================================

Created: 2026-02-25
Sprint: INTEGRATION-1

Core data models for the paper integration pipeline:
- PaperIntegrationEvent: Audit record per integration (one per paper)
- CascadeStep: Record of each step in the 14-step cascade
- SupersessionRecord: When Paper B's findings replace Paper A's
- BeliefVersionEntry: Per-belief version tracking across papers

All models are pure dataclasses with JSON serialization for SQLite storage.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
import json
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class IntegrationAction(str, Enum):
    """What kind of integration event this is."""
    INTEGRATE = "INTEGRATE"       # Normal paper integration
    SUPERSEDE = "SUPERSEDE"       # Paper supersedes an older one
    ROLLBACK = "ROLLBACK"         # Undo a previous integration


class IntegrationStatus(str, Enum):
    """Status of an integration event."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class SupersessionReason(str, Enum):
    """Why Paper B supersedes Paper A."""
    NEWER_DATA = "NEWER_DATA"
    LARGER_SAMPLE = "LARGER_SAMPLE"
    META_ANALYSIS = "META_ANALYSIS"
    METHODOLOGICAL_IMPROVEMENT = "METHODOLOGICAL_IMPROVEMENT"
    EXPLICIT_RETRACTION = "EXPLICIT_RETRACTION"
    SCOPE_REFINEMENT = "SCOPE_REFINEMENT"


class CascadeStepStatus(str, Enum):
    """Status of an individual cascade step."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# =============================================================================
# CASCADE STEP
# =============================================================================

@dataclass
class CascadeStep:
    """
    Record of a single step in the 14-step integration cascade.

    Each step is logged with timing, status, and any error information.
    Non-critical steps can fail without aborting the cascade.
    """
    step_number: int
    step_name: str
    status: CascadeStepStatus = CascadeStepStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    is_critical: bool = True
    items_processed: int = 0
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    def start(self) -> None:
        self.status = CascadeStepStatus.RUNNING
        self.started_at = datetime.now(timezone.utc).isoformat()

    def complete(self, items_processed: int = 0, details: Optional[Dict] = None) -> None:
        self.status = CascadeStepStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.items_processed = items_processed
        if details:
            self.details = details

    def fail(self, error: str) -> None:
        self.status = CascadeStepStatus.FAILED
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.error_message = error

    def skip(self, reason: str = "") -> None:
        self.status = CascadeStepStatus.SKIPPED
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.error_message = reason

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> CascadeStep:
        d["status"] = CascadeStepStatus(d["status"])
        return cls(**d)


# =============================================================================
# SUPERSESSION RECORD
# =============================================================================

@dataclass
class SupersessionRecord:
    """
    Records when Paper B's findings supersede Paper A's.

    Supersession is not all-or-nothing: Paper B may supersede only some
    beliefs from Paper A (partial supersession). The construct_overlap_score
    measures how much the two papers address the same constructs.

    Uses existing web_persistence.py ConflictType categories to classify
    the type of supersession.
    """
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    superseding_paper_id: str = ""
    superseded_paper_id: str = ""
    reason: SupersessionReason = SupersessionReason.NEWER_DATA
    construct_overlap_score: float = 0.0
    confidence: float = 0.0
    beliefs_superseded: List[str] = field(default_factory=list)
    beliefs_retained: List[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    rolled_back: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["reason"] = self.reason.value
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> SupersessionRecord:
        d["reason"] = SupersessionReason(d["reason"])
        return cls(**d)


# =============================================================================
# PAPER INTEGRATION EVENT
# =============================================================================

@dataclass
class PaperIntegrationEvent:
    """
    Complete audit record for a single paper's integration into the CMR system.

    One event per paper per integration attempt. If a paper is rolled back
    and re-integrated, that produces two events (ROLLBACK + new INTEGRATE).

    The cascade_steps list records the outcome of each of the 14 steps.
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    paper_id: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    action: IntegrationAction = IntegrationAction.INTEGRATE
    status: IntegrationStatus = IntegrationStatus.PENDING

    # Snapshot bookkeeping
    pre_snapshot_id: Optional[str] = None
    post_snapshot_id: Optional[str] = None

    # What changed
    beliefs_added: List[str] = field(default_factory=list)
    beliefs_retired: List[str] = field(default_factory=list)
    constraints_added: List[str] = field(default_factory=list)
    constraints_retired: List[str] = field(default_factory=list)
    bn_edges_updated: List[str] = field(default_factory=list)
    molecules_affected: List[str] = field(default_factory=list)
    tags_assigned: Dict[str, List[str]] = field(default_factory=dict)

    # Cascade tracking
    cascade_steps: List[CascadeStep] = field(default_factory=list)

    # Supersession
    supersedes_paper_id: Optional[str] = None
    supersession_records: List[SupersessionRecord] = field(default_factory=list)

    # Error handling
    error_log: Optional[str] = None

    # Bibliographic metadata (enriched from Semantic Scholar; Sprint METADATA-1)
    paper_year: Optional[int] = None
    paper_authors: List[str] = field(default_factory=list)
    paper_journal: Optional[str] = None
    paper_citation_count: Optional[int] = None
    paper_references: List[str] = field(default_factory=list)
    paper_cited_by: List[str] = field(default_factory=list)

    # Rollback reference
    rollback_of_event_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "event_id": self.event_id,
            "paper_id": self.paper_id,
            "timestamp": self.timestamp,
            "action": self.action.value,
            "status": self.status.value,
            "pre_snapshot_id": self.pre_snapshot_id,
            "post_snapshot_id": self.post_snapshot_id,
            "beliefs_added": self.beliefs_added,
            "beliefs_retired": self.beliefs_retired,
            "constraints_added": self.constraints_added,
            "constraints_retired": self.constraints_retired,
            "bn_edges_updated": self.bn_edges_updated,
            "molecules_affected": self.molecules_affected,
            "tags_assigned": self.tags_assigned,
            "cascade_steps": [s.to_dict() for s in self.cascade_steps],
            "supersedes_paper_id": self.supersedes_paper_id,
            "supersession_records": [r.to_dict() for r in self.supersession_records],
            "paper_year": self.paper_year,
            "paper_authors": self.paper_authors,
            "paper_journal": self.paper_journal,
            "paper_citation_count": self.paper_citation_count,
            "paper_references": self.paper_references,
            "paper_cited_by": self.paper_cited_by,
            "error_log": self.error_log,
            "rollback_of_event_id": self.rollback_of_event_id,
        }
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> PaperIntegrationEvent:
        d["action"] = IntegrationAction(d["action"])
        d["status"] = IntegrationStatus(d["status"])
        if d.get("cascade_steps"):
            d["cascade_steps"] = [CascadeStep.from_dict(s) for s in d["cascade_steps"]]
        if d.get("supersession_records"):
            d["supersession_records"] = [
                SupersessionRecord.from_dict(r) for r in d["supersession_records"]
            ]
        return cls(**d)

    def mark_in_progress(self) -> None:
        self.status = IntegrationStatus.IN_PROGRESS

    def mark_completed(self) -> None:
        self.status = IntegrationStatus.COMPLETED

    def mark_failed(self, error: str) -> None:
        self.status = IntegrationStatus.FAILED
        self.error_log = error

    def mark_rolled_back(self) -> None:
        self.status = IntegrationStatus.ROLLED_BACK


# =============================================================================
# BELIEF VERSION ENTRY
# =============================================================================

@dataclass
class BeliefVersionEntry:
    """
    Tracks a single version of a belief's state as contributed by a paper.

    Multiple papers may contribute to the same belief (via accumulation in
    web_persistence.py). This tracks each paper's contribution separately
    so that rollback can remove a specific paper's influence.
    """
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    belief_id: str = ""
    paper_id: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    credence_mean: Optional[float] = None
    credence_se: Optional[float] = None
    status: Optional[str] = None
    scope_json: Optional[str] = None
    is_current: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> BeliefVersionEntry:
        return cls(**d)


# =============================================================================
# TAG ASSIGNMENT
# =============================================================================

@dataclass
class TagAssignment:
    """
    A single tag assignment in the 3D taxonomy.

    Dimensions:
    - entity: What domain/topic (lighting, thermal, acoustic, spatial, etc.)
    - theoretical: Which T1 framework, T1.5 theory, or molecule
    - effect_size: Cohen's d categorization (negligible, small, medium, large)
    """
    belief_id: str = ""
    tag_dimension: str = ""     # "entity" | "theoretical" | "effect_size"
    tag_value: str = ""
    paper_id: str = ""
    confidence: float = 0.0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
