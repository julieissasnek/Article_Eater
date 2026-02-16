# Research Queue Service Contract

**Version**: 1.0
**Date**: 2026-02-15
**Schema ID**: `ae.research_queue.v1`

---

## Purpose

The Research Queue Service unifies gap prediction, VOI scoring, theory-driven priorities,
and discovery funnel tracking into a single actionable queue of research targets.

It answers: **"What should I be looking for next?"**

---

## Architecture

```
                     ┌──────────────────────┐
                     │   EpistemicOrchestrator   │
                     │   (P2-P6 services)        │
                     └──────────┬───────────────┘
                                │
┌───────────────┐               ▼               ┌──────────────────┐
│ Tier 1 Theory │◄────────────────────────────►│  GapPredictor    │
│  Frameworks   │  theory-driven predictions   │  (7 gap types)   │
└───────────────┘                               └────────┬─────────┘
                                                         │
                     ┌───────────────────────────────────┤
                     │                                   │
                     ▼                                   ▼
              ┌─────────────┐                   ┌───────────────┐
              │ VOI Scorer  │◄─────────────────►│ ResearchQueue │
              │ (priority)  │                   │   Service     │
              └─────────────┘                   └───────┬───────┘
                                                        │
                     ┌──────────────────────────────────┤
                     │                                  │
                     ▼                                  ▼
              ┌──────────────┐                  ┌───────────────┐
              │ Discovery    │                  │ VOI Collectors│
              │ Funnel       │                  │ (humans/bots) │
              └──────────────┘                  └───────────────┘
```

---

## Data Structures

### ResearchTarget

```python
@dataclass
class ResearchTarget:
    """A prioritized research target in the queue."""
    target_id: str

    # What gap this addresses
    gap_type: GapType  # MECHANISM, VALIDATION, BOUNDARY, etc.
    gap_id: str
    gap_description: str

    # Why this matters (theory-driven)
    theory_drivers: List[str]  # e.g., ["framework:predictive_processing"]
    mechanism_predictions: List[str]  # What Tier 1 predicts should exist

    # Priority and VOI
    voi_score: float  # 0-1, value of information
    priority: Priority  # HIGH, MEDIUM, LOW
    priority_rationale: str

    # Search guidance
    suggested_queries: List[str]  # Semantic Scholar, PubMed queries
    cross_field_terms: List[str]  # Expanded vocabulary
    target_databases: List[str]  # ["semantic_scholar", "pubmed", "zotero"]

    # Research opportunity framing (if no articles exist)
    is_research_opportunity: bool
    opportunity_framing: Optional[str]  # "Study needed that tests X under Y"

    # Status
    status: TargetStatus  # OPEN, SEARCHING, FOUND, CLOSED, STALE
    assigned_to: Optional[str]  # VOI collector ID
    created_at: datetime
    updated_at: datetime
```

### ResearchQueueState

```python
@dataclass
class ResearchQueueState:
    """Complete state of the research queue."""
    queue_id: str
    generated_at: datetime

    # Targets by priority
    high_priority: List[ResearchTarget]
    medium_priority: List[ResearchTarget]
    low_priority: List[ResearchTarget]

    # Research opportunities (gaps that may require new research)
    research_opportunities: List[ResearchTarget]

    # Statistics
    n_open: int
    n_searching: int
    n_found: int
    n_closed: int

    # Theory coverage
    theory_coverage: Dict[str, float]  # framework_id -> % gaps addressed
```

---

## Service Interface

### Core Methods

```python
class ResearchQueueService:
    """
    Unified research queue driven by gaps, VOI, and theory.

    Expert Guidance:
    - Simon: Satisficing — stop searching when good enough
    - Pearl: Causal attribution — why did search succeed/fail?
    - Haack: Foundherentism — gaps appear where grounding weak
    - Thagard: Coherence — prioritize gaps that most improve coherence
    """

    def refresh_queue(self) -> ResearchQueueState:
        """
        Regenerate queue from current web state.

        1. Run GapPredictor to identify gaps
        2. Add theory-driven predictions from Tier 1 frameworks
        3. Score each gap by VOI
        4. Generate search queries with cross-field vocabulary
        5. Classify research opportunities vs. findable articles
        """
        pass

    def get_next_target(self, collector_id: str) -> Optional[ResearchTarget]:
        """
        Get next target for a VOI collector to work on.

        Assigns target to collector and updates status to SEARCHING.
        """
        pass

    def report_search_result(
        self,
        target_id: str,
        result: SearchResult
    ) -> ClosureAssessment:
        """
        Report search result and assess gap closure.

        If articles found: transition to FOUND, queue for ingestion
        If no articles: mark as research_opportunity or STALE
        """
        pass

    def get_theory_predictions(
        self,
        framework_id: str
    ) -> List[ResearchTarget]:
        """
        Get targets driven by a specific Tier 1 framework.

        Uses framework's mechanistic claims to predict what
        empirical findings SHOULD exist but haven't been found.
        """
        pass
```

### Theory-Driven Gap Detection

```python
def detect_theory_gaps(self, framework: Theory) -> List[ResearchTarget]:
    """
    Use Tier 1 framework to predict missing research.

    For each framework prediction that lacks empirical support:
    1. Generate ResearchTarget with suggested_queries
    2. If no articles found, frame as research_opportunity

    Example:
        Framework: Predictive Processing
        Prediction: "Environments with learnable structure reduce anxiety"
        Gap: No empirical studies testing this in healthcare settings
        Target: Search for "predictable environments anxiety hospital"
        If not found: "Study needed: test PP prediction in hospital wayfinding"
    """
    targets = []

    for prediction in framework.explicit_predictions + framework.derived_predictions:
        # Check if prediction has empirical support in web
        support = self.web.find_supporting_beliefs(prediction)

        if not support or support.credence < 0.5:
            # Create research target
            target = ResearchTarget(
                gap_type=GapType.VALIDATION,
                theory_drivers=[framework.theory_id],
                mechanism_predictions=[prediction.statement],
                suggested_queries=self._generate_queries(prediction),
                is_research_opportunity=False,  # Updated after search
            )
            targets.append(target)

    return targets
```

---

## Queue Priorities

| Priority | Criteria | Examples |
|----------|----------|----------|
| HIGH | VOI > 0.7 + affects multiple beliefs + theory predicts | Missing mechanism for entrenched finding |
| MEDIUM | VOI > 0.4 OR theory predicts | Boundary condition unclear |
| LOW | VOI > 0.2 | Nice to have, weak coherence impact |

---

## Integration Points

1. **GapPredictor** — provides 7 gap types
2. **VOISearch** — provides cross-field vocabulary, search strategies
3. **DiscoveryFunnel** — tracks search → retrieval → closure
4. **Tier 1 Frameworks** — provide mechanism predictions
5. **BibTeX Ingestion** — receives found articles
6. **VOI Collectors** — humans/bots that work targets

---

## Events

```python
class QueueEvent(Enum):
    TARGET_CREATED = "target_created"
    TARGET_ASSIGNED = "target_assigned"
    SEARCH_COMPLETED = "search_completed"
    ARTICLES_FOUND = "articles_found"
    NO_ARTICLES_FOUND = "no_articles_found"
    RESEARCH_OPPORTUNITY_IDENTIFIED = "research_opportunity_identified"
    GAP_CLOSED = "gap_closed"
```

---

## Success Metrics

- **Gap Closure Rate**: % of targets that find useful articles
- **Theory Coverage**: % of Tier 1 predictions with empirical support
- **VOI Accuracy**: Correlation between predicted VOI and actual credence change
- **Opportunity Quality**: % of research opportunities that get picked up by researchers
