"""
OVERSEER v2 Management Layer: Data Models

Comprehensive dataclasses for pipeline tracking, queue monitoring,
article flow, suggestion management, and panel convocation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional, Any


# ============================================================================
# Enums
# ============================================================================

class PipelineStatus(str, Enum):
    """Status of a pipeline."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    STALLED = "stalled"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class GapSourceType(str, Enum):
    """Source of suggestion/gap."""
    ARGUMENTATION = "argumentation"
    VOI = "voi"
    QA = "qa"
    INTERPRETATION_SPACE = "interpretation_space"
    OTHER = "other"


class ExtractionStage(str, Enum):
    """Stage in extraction pipeline."""
    DOWNLOADED = "downloaded"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    INTEGRATED = "integrated"


# ============================================================================
# Pipeline Registry Models
# ============================================================================

@dataclass
class PipelineRecord:
    """Record for a single pipeline."""
    pipeline_id: str                     # e.g., "article-discovery", "extraction"
    display_name: str
    components: List[str]                # services involved
    last_heartbeat: datetime
    status: PipelineStatus
    queue_depth: int                      # items waiting
    throughput_24h: int                   # items processed in 24h
    error_rate_24h: float                 # [0, 1]
    bottleneck: Optional[str]             # identified bottleneck component
    last_error: Optional[str] = None
    alerts: List[str] = field(default_factory=list)


# ============================================================================
# Queue Health Models
# ============================================================================

@dataclass
class QueueHealthReport:
    """Health assessment of research queue."""
    timestamp: datetime
    total_targets: int                   # all targets ever
    open_targets: int                    # waiting assignment
    searching_targets: int               # in progress
    found_targets: int                   # search succeeded
    closed_targets: int                  # gap closed
    stale_targets: int                   # abandoned

    search_to_found_rate: float          # % of searches that find articles
    avg_time_open_to_found_hours: float  # avg duration
    avg_time_open_to_closed_hours: float # avg duration

    oldest_open_target_hours: float      # age of oldest unassigned target
    oldest_searching_target_hours: float # age of oldest in-progress search

    health_status: str                   # OK, YELLOW (slow), RED (stalled)
    recommendations: List[str] = field(default_factory=list)


# ============================================================================
# Article Flow Models
# ============================================================================

@dataclass
class ArticleFlowStageMetrics:
    """Metrics for one stage in article flow."""
    stage_name: str                      # e.g., "suggestion→search", "PDF→extraction"
    items_waiting: int
    items_in_progress: int
    items_completed_24h: int
    items_completed_7d: int
    items_completed_30d: int
    failure_rate_24h: float              # [0, 1]
    avg_processing_time_hours: float
    bottleneck_score: float              # [0, 1], 1 = critical bottleneck
    bottleneck_component: Optional[str]  # which service is slow


@dataclass
class ArticleFlowReport:
    """Overall article flow through pipeline."""
    timestamp: datetime
    stages: List[ArticleFlowStageMetrics]
    overall_throughput_24h: int
    overall_throughput_7d: int

    # Aggregates
    total_items_in_system: int
    critical_bottleneck: Optional[str]   # stage with worst metrics
    flow_efficiency: float               # [0, 1], % of items successfully progressing

    health_status: str
    recommendations: List[str] = field(default_factory=list)


# ============================================================================
# Search Suggestion Models
# ============================================================================

@dataclass
class SuggestionAge:
    """Age distribution of suggestions."""
    count_0_1d: int                      # created < 1 day ago
    count_1_3d: int                      # 1-3 days old
    count_3_7d: int                      # 3-7 days old
    count_7_30d: int                     # 7-30 days old
    count_30plus_d: int                  # >30 days old
    oldest_suggestion_days: int


@dataclass
class SuggestionBacklogReport:
    """Report on suggestions waiting to be acted on."""
    timestamp: datetime

    total_unacted_suggestions: int
    age_distribution: SuggestionAge

    # By source
    by_argumentation_gaps: int
    by_voi_gaps: int
    by_qa_gaps: int
    by_interpretation_space_gaps: int
    by_other: int

    # Health metrics
    staleness_threshold_days: int        # flag if > N days old
    suggestions_exceeding_staleness: int # count
    max_age_to_stale_ratio: float        # ratio of oldest/threshold

    staleness_alert: bool               # true if critical backlog
    health_status: str                  # OK, YELLOW, RED
    recommendations: List[str] = field(default_factory=list)


# ============================================================================
# Extraction Queue Models
# ============================================================================

@dataclass
class ExtractionQueueMetrics:
    """Metrics for extraction queue at one stage."""
    stage: ExtractionStage
    count: int
    avg_age_hours: float
    oldest_age_hours: float
    quality_score_mean: Optional[float]  # if validated stage


@dataclass
class ExtractionQueueReport:
    """Report on PDFs waiting to be encoded into templates."""
    timestamp: datetime

    pdfs_downloaded_not_extracted: int
    pdfs_extracted_not_validated: int
    pdfs_validated_not_integrated: int

    # Quality distribution
    quality_distribution: Dict[str, int] # "excellent" -> count, "poor" -> count
    extraction_quality_mean: float

    # Throughput
    throughput_24h: int
    throughput_7d: int
    estimated_hours_to_clear: float

    # Health
    critical_backlog: bool
    health_status: str
    recommendations: List[str] = field(default_factory=list)


# ============================================================================
# Panel Convocation Models
# ============================================================================

@dataclass
class PanelRecommendation:
    """Recommendation to convene a panel."""
    panel_type: str                      # e.g., "coherence_review", "qa_audit"
    urgency: str                         # "low", "medium", "high"
    reason: str
    context: Dict[str, Any]
    data_required: List[str]            # what data to gather


# ============================================================================
# Management Dashboard Models
# ============================================================================

@dataclass
class ManagementReport:
    """Complete single-page management view."""
    timestamp: datetime

    # All monitoring components
    pipeline_statuses: Dict[str, PipelineRecord]
    queue_health: QueueHealthReport
    article_flow: ArticleFlowReport
    suggestion_backlog: SuggestionBacklogReport
    extraction_queue: ExtractionQueueReport
    panel_needs: List[PanelRecommendation]

    # Error/failure trends
    error_count_24h: int
    error_rate_trend: str               # "improving", "stable", "degrading"
    most_common_error: Optional[str]

    # Executive summary
    overall_health: str                 # "HEALTHY", "YELLOW", "RED"
    critical_alerts: List[str]
    immediate_actions_recommended: List[str]

    # Historical context
    previous_report_timestamp: Optional[datetime] = None
    changes_since_previous: Dict[str, Any] = field(default_factory=dict)

    # QA system monitoring (reflexes and success conditions)
    reflex_health: Dict[str, Any] = field(default_factory=dict)
    success_conditions: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Pipeline Status Summary (for quick reporting)
# ============================================================================

@dataclass
class PipelineStatusSummary:
    """Quick summary of all pipeline statuses."""
    timestamp: datetime
    total_pipelines: int
    healthy_count: int
    degraded_count: int
    stalled_count: int
    blocked_count: int
    unknown_count: int

    status_by_pipeline: Dict[str, str]  # pipeline_id -> status

    def critical_alert(self) -> Optional[str]:
        """Return critical alert if any pipeline blocked."""
        if self.blocked_count > 0:
            return f"{self.blocked_count} pipeline(s) BLOCKED — immediate investigation needed"
        if self.stalled_count > 2:
            return f"{self.stalled_count} pipeline(s) STALLED — review throughput bottlenecks"
        return None


# ============================================================================
# Trend Tracking (for detecting patterns)
# ============================================================================

@dataclass
class MetricTrend:
    """Track metric over time for trend detection."""
    metric_name: str
    values: List[float]                 # recent values (last N checks)
    timestamps: List[datetime]

    def is_improving(self) -> bool:
        """Simple trend: is metric improving (values increasing)?"""
        if len(self.values) < 2:
            return False
        return self.values[-1] > self.values[0]

    def is_declining(self) -> bool:
        """Is metric declining?"""
        if len(self.values) < 2:
            return False
        return self.values[-1] < self.values[0]

    def slope(self) -> float:
        """Rough slope indicator."""
        if len(self.values) < 2:
            return 0.0
        return (self.values[-1] - self.values[0]) / len(self.values)


@dataclass
class SystemHealthTrend:
    """Track overall system health trends."""
    coherence_trend: MetricTrend
    throughput_trend: MetricTrend
    error_rate_trend: MetricTrend
    queue_backlog_trend: MetricTrend

    def overall_direction(self) -> str:
        """Aggregate trend."""
        improving = sum([
            self.coherence_trend.is_improving(),
            self.throughput_trend.is_improving(),
            not self.error_rate_trend.is_improving(),  # lower is better
            not self.queue_backlog_trend.is_improving()  # lower is better
        ])
        if improving >= 3:
            return "IMPROVING"
        elif improving <= 1:
            return "DECLINING"
        else:
            return "STABLE"
