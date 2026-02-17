"""Research Queue module.

Public API:
- ResearchQueueService: queue refresh/assignment/reporting
- Queue models in src.queue.models
"""

from src.queue.models import (
    ArticleReference,
    ClaimResult,
    ClosureAssessment,
    CollectorProfile,
    CollectorType,
    NullResultEvidence,
    OpportunityStatus,
    Priority,
    QueueEvent,
    ResearchOpportunity,
    ResearchQueueState,
    ResearchTarget,
    SearchGuidance,
    SearchResult,
    SearchResultType,
    TargetStatus,
)
from src.queue.automated_searcher import (
    AutomatedQueueSearcher,
    AutomatedSearcherConfig,
    AutomatedTargetRun,
)
from src.queue.service import ResearchQueueService
from src.queue.zotero_watcher import ZoteroWatcher

__all__ = [
    "AutomatedQueueSearcher",
    "AutomatedSearcherConfig",
    "AutomatedTargetRun",
    "ArticleReference",
    "ClaimResult",
    "ClosureAssessment",
    "CollectorProfile",
    "CollectorType",
    "NullResultEvidence",
    "OpportunityStatus",
    "Priority",
    "QueueEvent",
    "ResearchOpportunity",
    "ResearchQueueService",
    "ResearchQueueState",
    "ResearchTarget",
    "SearchGuidance",
    "SearchResult",
    "SearchResultType",
    "TargetStatus",
    "ZoteroWatcher",
]
