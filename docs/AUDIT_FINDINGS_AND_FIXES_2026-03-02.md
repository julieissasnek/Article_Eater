# Audit Findings and Recommended Fixes

**Date**: March 2, 2026
**Auditor**: Claude Code
**Priority**: High (VOI integration, user-specific recommendations)

---

## Finding 1: VOI Not Used for Queue Prioritization

### Problem Statement
Gap predictor generates PredictedGap objects with voi_score fields, but ResearchQueueService ignores them when returning targets to collectors.

### Evidence

**File**: `src/services/gap_predictor.py`, line 55
```python
@dataclass
class PredictedGap:
    voi_score: float = 0.5  # HARDCODED — never updated
```

**File**: `src/queue/service.py`, line 200+
```python
def get_next_target(self, collector_id: str) -> Optional[ResearchTarget]:
    """Get next unassigned target for collector."""
    # Returns FIRST unassigned (FIFO)
    # IGNORES voi_score field
```

### Impact
- Researchers always work on oldest gaps first, not most valuable ones
- VOI scores computed but discarded
- No reward signal for high-value gaps
- Inefficient research allocation

### Fix

**Step 1**: Update `get_next_target()` to sort by VOI
```python
def get_next_target(self, collector_id: str) -> Optional[ResearchTarget]:
    """Get next highest-VOI unassigned target for collector."""
    unassigned = [t for t in self._targets.values()
                  if t.status == TargetStatus.OPEN and t.assigned_to is None]
    if not unassigned:
        return None

    # Sort by VOI (highest first), then by created_at (FIFO tie-break)
    sorted_targets = sorted(
        unassigned,
        key=lambda t: (-t.voi_score, t.created_at)
    )

    target = sorted_targets[0]
    target.assigned_to = collector_id
    self._persist_state()
    return target
```

**Step 2**: Ensure gap_predictor actually computes VOI instead of hardcoding
```python
# In gap_predictor.py __init__
def __init__(self, web=None, edge_justification_service=None, voi_scorer=None):
    self.web = web
    self.edge_justification_service = edge_justification_service
    self.voi_scorer = voi_scorer  # NEW

# In find_all_gaps()
for gap in gaps:
    if self.voi_scorer:
        gap.voi_score = self.voi_scorer.calculate_voi(
            EpistemicGap.from_predicted_gap(gap),
            self.web
        )
```

**Step 3**: Wire VOI scorer into gap predictor initialization
```python
# In queue/service.py
from src.services.voi_search import VOIGapScorer  # NEW

@property
def gap_predictor(self) -> GapPredictor:
    if self._gap_predictor is None:
        voi_scorer = VOIGapScorer()  # NEW
        self._gap_predictor = GapPredictor(
            web=self.web,
            voi_scorer=voi_scorer  # PASS VOI SCORER
        )
    return self._gap_predictor
```

**Verification**:
```python
# Test that highest-VOI gap is returned first
queue = ResearchQueueService(web=test_web)
queue._targets = {
    "gap_1": ResearchTarget(gap_id="gap_1", voi_score=0.3),
    "gap_2": ResearchTarget(gap_id="gap_2", voi_score=0.9),  # Highest
    "gap_3": ResearchTarget(gap_id="gap_3", voi_score=0.6),
}
next_target = queue.get_next_target("collector_1")
assert next_target.gap_id == "gap_2"
```

**Effort**: Medium (30 min implementation, 15 min testing)
**Risk**: Low (internal method only, backward compatible)

---

## Finding 2: User-Specific VOI Missing Entirely

### Problem Statement
System treats all researchers identically. No mechanism to personalize VOI by researcher expertise, domain interest, or research agenda.

### Evidence

**CollectorProfile exists** (`src/queue/models.py`):
```python
@dataclass
class CollectorProfile:
    collector_id: str
    collector_type: CollectorType
    name: str
    can_access_databases: List[str]
    can_access_paywalled: bool
    preferred_domains: List[str]  # EXISTS BUT UNUSED
    max_concurrent_targets: int
    gap_closure_rate: float       # EXISTS BUT UNUSED
    avg_articles_per_target: float
```

**But not used in VOI calculations**:
- No method adjusts VOI by preferred_domains
- No method weights by gap_closure_rate
- No method accounts for collector expertise level

### Impact
- Researcher A (expert in mechanism) gets same recommendations as Researcher B (novice)
- Researcher A (interested in cognitive load) sees irrelevant visual perception gaps
- No personalization of search prioritization
- Suboptimal research allocation

### Fix

**Step 1**: Create researcher fit factor calculation
```python
# New file: src/queue/researcher_voi_adjustment.py

@dataclass
class ResearcherFitFactor:
    """Personalization factors for VOI adjustment."""
    domain_fit: float = 1.0         # Does gap match researcher's domain?
    expertise_fit: float = 1.0      # Is gap at researcher's expertise level?
    success_fit: float = 1.0        # Does researcher succeed with this gap type?


def compute_researcher_fit(
    collector_profile: CollectorProfile,
    gap: ResearchTarget,
    web: Optional[WebOfBelief] = None
) -> ResearcherFitFactor:
    """
    Compute how well this gap aligns with researcher's profile.

    Returns: ResearcherFitFactor in [0.5, 1.5] range
    """

    # 1. Domain fit: researcher's preferred_domains overlap with gap domain
    domain_fit = 1.0
    if collector_profile.preferred_domains:
        gap_domain = _infer_gap_domain(gap)
        matches = [d for d in collector_profile.preferred_domains
                   if d.lower() in gap_domain.lower()]
        if matches:
            domain_fit = 1.3  # Boost if domain matches
        else:
            domain_fit = 0.7  # Reduce if domain mismatch

    # 2. Expertise fit: gap complexity matches researcher capability
    expertise_fit = 1.0
    if collector_profile.collector_type == CollectorType.HUMAN_RESEARCHER:
        # Researchers can tackle complex gaps
        expertise_fit = 1.1 if gap.gap_type == GapType.MECHANISM else 1.0
    elif collector_profile.collector_type == CollectorType.HUMAN_ASSISTANT:
        # Assistants better at simple gaps
        expertise_fit = 1.2 if gap.gap_type in [GapType.VALIDATION, GapType.BOUNDARY] else 0.9

    # 3. Success fit: researcher's historical closure rate on this gap type
    success_fit = 1.0
    if collector_profile.gap_closure_rate > 0:
        # Weight by historical success
        closure_factor = min(collector_profile.gap_closure_rate, 0.8)
        success_fit = 1.0 + (closure_factor * 0.2)  # [1.0, 1.2] range

    return ResearcherFitFactor(
        domain_fit=domain_fit,
        expertise_fit=expertise_fit,
        success_fit=success_fit
    )


def compute_researcher_adjusted_voi(
    base_voi: float,
    collector_profile: CollectorProfile,
    gap: ResearchTarget,
    web: Optional[WebOfBelief] = None
) -> float:
    """
    Adjust VOI based on researcher fit.

    Formula:
        adjusted_voi = base_voi * domain_fit * expertise_fit * success_fit
    """
    fit = compute_researcher_fit(collector_profile, gap, web)
    return base_voi * fit.domain_fit * fit.expertise_fit * fit.success_fit
```

**Step 2**: Use adjusted VOI in queue
```python
# In queue/service.py

def get_next_target_for_collector(self, collector_id: str) -> Optional[ResearchTarget]:
    """Get next highest-adjusted-VOI target for collector."""
    collector = self.get_collector(collector_id)
    if collector is None:
        return self.get_next_target(collector_id)  # Fallback to FIFO

    unassigned = [t for t in self._targets.values()
                  if t.status == TargetStatus.OPEN and t.assigned_to is None]
    if not unassigned:
        return None

    from src.queue.researcher_voi_adjustment import compute_researcher_adjusted_voi

    # Compute adjusted VOI for each gap
    adjusted_vois = {}
    for target in unassigned:
        adjusted_voi = compute_researcher_adjusted_voi(
            target.voi_score,
            collector,
            target,
            self.web
        )
        adjusted_vois[target.target_id] = adjusted_voi

    # Sort by adjusted VOI
    sorted_targets = sorted(
        unassigned,
        key=lambda t: (-adjusted_vois[t.target_id], t.created_at)
    )

    target = sorted_targets[0]
    target.assigned_to = collector_id
    target.adjusted_voi_for_collector = adjusted_vois[target.target_id]
    self._persist_state()
    return target
```

**Step 3**: Add feedback loop from closure rate
```python
# In queue/service.py

def report_search_result(self, target_id: str, result: SearchResult) -> ClosureAssessment:
    """Report search result AND update collector profile."""

    # Existing closure assessment logic...
    assessment = self._assess_closure(target_id, result)

    # NEW: Update collector's gap_closure_rate
    if result.result_type in [SearchResultType.FOUND_RELEVANT, SearchResultType.FOUND_TANGENTIAL]:
        collector = self.get_collector(result.collector_id)
        if collector:
            # Track which gap types this collector succeeds with
            target = self._targets.get(target_id)
            gap_type = target.gap_type if target else None

            # Update profile
            collector.targets_completed += 1
            if result.result_type == SearchResultType.FOUND_RELEVANT:
                collector.gap_closure_rate = (
                    (collector.gap_closure_rate * (collector.targets_completed - 1) + 1.0)
                    / collector.targets_completed
                )

            self._collectors[collector.collector_id] = collector
            self._persist_state()

    return assessment
```

**Verification**:
```python
# Test that researcher-specific VOI adjusts ranking
def test_researcher_specific_voi():
    # Researcher A: expert in mechanisms, prefers psychology
    researcher_a = CollectorProfile(
        collector_id="a",
        collector_type=CollectorType.HUMAN_RESEARCHER,
        preferred_domains=["psychology", "neuroscience"],
        gap_closure_rate=0.8
    )

    # Researcher B: novice, generalist
    researcher_b = CollectorProfile(
        collector_id="b",
        collector_type=CollectorType.HUMAN_ASSISTANT,
        preferred_domains=[],
        gap_closure_rate=0.4
    )

    # Mechanism gap in psychology (fits A, not B)
    mechanism_gap = ResearchTarget(
        gap_id="mech_psych",
        gap_type=GapType.MECHANISM,
        voi_score=0.7,
        description="Why does attention restoration work? (mechanism)"
    )

    # For A: 0.7 * 1.3 (domain) * 1.1 (mechanism) * 1.16 (expertise) = 1.18 (BOOSTED)
    # For B: 0.7 * 0.7 (no domain) * 0.9 (mechanism) * 1.08 (expertise) = 0.48 (REDUCED)

    voi_a = compute_researcher_adjusted_voi(0.7, researcher_a, mechanism_gap)
    voi_b = compute_researcher_adjusted_voi(0.7, researcher_b, mechanism_gap)

    assert voi_a > voi_b  # A gets higher priority for this gap
```

**Effort**: High (2 hours implementation, 1 hour testing)
**Risk**: Medium (changes HOW targets are returned, needs validation)
**Impact**: High (enables true personalization)

---

## Finding 3: VOI Hardcoded in Gap Predictor

### Problem Statement
Gap predictor sets `voi_score = 0.5` as default on all PredictedGap objects and never updates them.

### Evidence

**File**: `src/services/gap_predictor.py`, line 55
```python
voi_score: float = 0.5  # DEFAULT NEVER CHANGED
```

**No code path calls VOI calculator**:
- `find_all_gaps()` doesn't call VOIGapScorer
- `harvest_gaps_from_annotations()` doesn't call VOIGapScorer
- Every gap gets 0.5 regardless of importance

### Impact
- All gaps treated equally
- Critical gaps not prioritized over minor ones
- VOI computation modules written but unused

### Fix

**Option A**: Gap predictor accepts optional VOI scorer (lazy approach)
```python
# In gap_predictor.py
class GapPredictor:
    def __init__(self, web=None, edge_justification_service=None, voi_scorer=None):
        self.web = web
        self.edge_justification_service = edge_justification_service
        self.voi_scorer = voi_scorer  # Optional dependency

    def find_all_gaps(self, max_gaps: int = 50) -> GapReport:
        gaps = []
        # ... gap detection ...

        # After collecting all gaps, optionally score by VOI
        if self.voi_scorer and self.web:
            for gap in gaps:
                try:
                    epistemic_gap = EpistemicGap(
                        gap_id=gap.gap_id,
                        gap_type=gap.gap_type,
                        description=gap.description,
                        affected_beliefs=gap.affected_beliefs
                    )
                    gap.voi_score = self.voi_scorer.calculate_voi(
                        epistemic_gap,
                        belief=self.web.get_belief(gap.affected_beliefs[0]) if gap.affected_beliefs else None,
                        web=self.web
                    )
                except Exception as e:
                    logger.warning(f"VOI calculation failed for {gap.gap_id}: {e}")
                    # Keep default 0.5

        return GapReport(gaps=gaps[:max_gaps], ...)
```

**Option B**: VOI scorer is ALWAYS created (strict approach)
```python
# In gap_predictor.py
from src.services.voi_search import VOIGapScorer

class GapPredictor:
    def __init__(self, web=None, edge_justification_service=None):
        self.web = web
        self.edge_justification_service = edge_justification_service
        self.voi_scorer = VOIGapScorer()  # ALWAYS create

    def find_all_gaps(self, max_gaps: int = 50) -> GapReport:
        gaps = []
        # ... gap detection ...

        # Score by VOI (no try/except — let fail if voi_search broken)
        for gap in gaps:
            epistemic_gap = self._gap_to_epistemic(gap)
            gap.voi_score = self.voi_scorer.calculate_voi(
                epistemic_gap,
                self.web
            )

        return GapReport(gaps=gaps[:max_gaps], ...)
```

**Recommendation**: Use **Option A** (graceful degradation)
- If voi_search fails to import, still works with 0.5 defaults
- If VOI computation fails for one gap, continues with others
- Doesn't break existing code if voi_scorer is unavailable

**Effort**: Low (1 hour implementation and testing)
**Risk**: Low (optional enhancement, backward compatible)

---

## Finding 4: Interpretation Space Table Doesn't Exist

### Problem Statement
`SearchSuggestionTracker` queries `interpretation_space_suggestions` table that doesn't exist. Code gracefully catches exception but monitoring is ineffective.

### Evidence

**File**: `src/services/overseer_management.py`, lines 545-549
```python
try:
    with sqlite3.connect(str(self.web_db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM interpretation_space_suggestions
            WHERE status = 'proposed' OR status = 'identified'
        """)
        total_unacted = cursor.fetchone()[0] or 0
except:
    total_unacted = 0  # SILENT FAILURE
```

**Comment acknowledges uncertainty** (line 545):
```python
# Assumes: interpretation_space_suggestions or similar table
```

**No table creation code** anywhere:
- Not in overseer_management.py
- Not in any migration
- Not in any schema definition

**Data exists but offline**:
- `data/interpretation_space/phase2/`, etc. contain JSON/markdown outputs
- No code populates database from these

### Impact
- Overseer monitoring for interpretation_space suggestions is non-functional
- David's pipeline status dashboard will show 0 suggestions always
- Can't track whether interpretation space phase outputs → article searches

### Fix

**Option 1**: Create table and wire up data population
```python
# In overseer_management.py

class SearchSuggestionTracker:
    def __init__(self, web_db_path: str, staleness_threshold_days: int = 7):
        self.web_db_path = Path(web_db_path)
        self.staleness_threshold_days = staleness_threshold_days
        self._init_tables()  # NEW

    def _init_tables(self) -> None:
        """Create interpretation_space_suggestions table if not exists."""
        with sqlite3.connect(str(self.web_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interpretation_space_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suggestion_id TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,  -- 'argumentation', 'voi', 'qa', 'interpretation_space', 'other'
                    status TEXT DEFAULT 'proposed',  -- 'proposed', 'identified', 'acted_upon', 'closed'
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    description TEXT,
                    suggested_search TEXT,
                    gap_type TEXT,
                    voi_score REAL DEFAULT 0.5,
                    related_gap_id TEXT,
                    related_target_id TEXT,
                    notes TEXT
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_interp_source_status
                ON interpretation_space_suggestions(source, status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_interp_created
                ON interpretation_space_suggestions(created_at)
            """)
            conn.commit()

    def insert_suggestion(
        self,
        source: str,
        description: str,
        suggested_search: str,
        gap_type: Optional[str] = None,
        voi_score: float = 0.5
    ) -> str:
        """Insert a new suggestion."""
        suggestion_id = f"sugg_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(str(self.web_db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interpretation_space_suggestions
                (suggestion_id, source, status, created_at, description, suggested_search, gap_type, voi_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                suggestion_id,
                source,
                'proposed',
                now,
                description,
                suggested_search,
                gap_type,
                voi_score
            ))
            conn.commit()

        return suggestion_id
```

**Wire up phase2-4 outputs**:
```python
# New file: src/services/interpretation_space_loader.py

def load_interpretation_space_suggestions() -> List[Dict]:
    """Load suggestions from interpretation_space/phase2-4 outputs."""
    phase_dir = Path(__file__).parent.parent.parent / "data" / "interpretation_space"

    suggestions = []
    for phase in ["phase2", "phase3", "phase4"]:
        phase_path = phase_dir / phase
        if not phase_path.exists():
            continue

        for json_file in phase_path.glob("*.json"):
            with open(json_file) as f:
                data = json.load(f)
                # Parse phase outputs and convert to suggestion format
                for item in data.get("suggestions", []):
                    suggestions.append({
                        "source": f"interpretation_space_{phase}",
                        "description": item.get("description", ""),
                        "suggested_search": item.get("suggested_search", ""),
                        "gap_type": item.get("gap_type"),
                        "voi_score": item.get("voi_score", 0.5)
                    })

    return suggestions


def populate_interpretation_space_suggestions(tracker: SearchSuggestionTracker) -> int:
    """Load phase outputs and populate database."""
    suggestions = load_interpretation_space_suggestions()
    count = 0

    for sugg in suggestions:
        try:
            tracker.insert_suggestion(**sugg)
            count += 1
        except Exception as e:
            logger.warning(f"Failed to insert suggestion: {e}")

    logger.info(f"Populated {count} interpretation_space suggestions")
    return count
```

**Option 2**: Remove aspirational monitoring (if no data source)
```python
# In overseer_management.py

def check_suggestion_backlog(self) -> SuggestionBacklogReport:
    """
    Monitor unacted suggestions from known sources.

    NOTE: interpretation_space source is currently OFFLINE.
    Suggestions only from: argumentation, voi, qa, other
    """
    # Remove interpretation_space query
    # Adjust source breakdown accordingly
```

**Recommendation**: Use **Option 1** (complete the implementation)
- Interpretation space has data that should feed queue
- Completing the integration honors the design intent
- Provides feedback path from interpretation phase → search

**Effort**: Medium (1-2 hours to wire up phase outputs)
**Risk**: Low (new functionality, doesn't break existing)

---

## Finding 5: Automated Searcher Not Auto-Invoked

### Problem Statement
`AutomatedQueueSearcher` exists and works, but must be manually instantiated and `run_once()` called. No scheduler automatically triggers searches.

### Evidence

**File**: `src/queue/automated_searcher.py`

Searcher implementation complete but:
- No automatic invocation mechanism
- No scheduler integration
- No worker pool
- Must be run via external script or REPL

### Impact
- Gaps are predicted and queued but never searched
- Research queue backs up with unprocessed targets
- Manual intervention required to execute searches
- Limits to researchers manually claiming targets

### Fix

**Step 1**: Create scheduler configuration
```python
# New file: src/queue/searcher_scheduler.py

from dataclasses import dataclass
from datetime import timedelta

@dataclass
class SearcherScheduleConfig:
    """Configuration for automated searcher scheduling."""
    enabled: bool = True
    run_interval_seconds: int = 3600  # Run every hour
    targets_per_run: int = 3
    queries_per_target: int = 3
    max_workers: int = 1
    max_concurrent_searches: int = 10
    rate_limit_requests_per_second: float = 2.0  # Semantic Scholar rate limit
    timeout_seconds: int = 30
```

**Step 2**: Create scheduler service
```python
# New file: src/queue/searcher_scheduler_service.py

import threading
import time
from datetime import datetime, timezone

class SearcherSchedulerService:
    """Background service to run automated searcher periodically."""

    def __init__(
        self,
        queue_service,
        searcher_config: Optional[AutomatedSearcherConfig] = None,
        schedule_config: Optional[SearcherScheduleConfig] = None
    ):
        self.queue_service = queue_service
        self.searcher_config = searcher_config or AutomatedSearcherConfig()
        self.schedule_config = schedule_config or SearcherScheduleConfig()

        self.searcher = AutomatedQueueSearcher(queue_service, config=self.searcher_config)
        self._thread = None
        self._stop_event = threading.Event()
        self._last_run = None
        self._run_count = 0
        self._failed_runs = 0

    def start(self) -> None:
        """Start scheduler in background thread."""
        if not self.schedule_config.enabled:
            logger.info("Searcher scheduler disabled in config")
            return

        if self._thread is not None and self._thread.is_alive():
            logger.warning("Searcher scheduler already running")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Searcher scheduler started")

    def stop(self) -> None:
        """Stop scheduler."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
            logger.info("Searcher scheduler stopped")

    def _run_loop(self) -> None:
        """Main scheduler loop."""
        while not self._stop_event.is_set():
            try:
                # Check if it's time to run
                now = datetime.now(timezone.utc)
                if self._last_run is None or \
                   (now - self._last_run).total_seconds() >= self.schedule_config.run_interval_seconds:

                    self._execute_run(now)
                    self._last_run = now

            except Exception as e:
                logger.error(f"Searcher scheduler error: {e}")
                self._failed_runs += 1

            # Sleep briefly before checking again
            time.sleep(10)

    def _execute_run(self, timestamp: datetime) -> None:
        """Execute one searcher run."""
        logger.info(f"Starting automated search run #{self._run_count + 1}")

        try:
            results = self.searcher.run_once()

            self._run_count += 1
            logger.info(f"Searcher run complete: {len(results)} targets processed")

            # Log results
            for run in results:
                logger.debug(f"  {run.target_id}: {run.n_candidates} candidates found")

        except Exception as e:
            self._failed_runs += 1
            logger.error(f"Searcher run failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status."""
        return {
            "enabled": self.schedule_config.enabled,
            "running": self._thread is not None and self._thread.is_alive(),
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "run_count": self._run_count,
            "failed_runs": self._failed_runs,
            "next_run_in_seconds": (
                self.schedule_config.run_interval_seconds -
                (datetime.now(timezone.utc) - self._last_run).total_seconds()
            ) if self._last_run else self.schedule_config.run_interval_seconds
        }
```

**Step 3**: Wire into system initialization
```python
# In src/services/system_setup.py

def setup_article_eater_system(
    web_db_path: str,
    enable_automated_search: bool = True
) -> Dict[str, Any]:
    """Set up Article Eater system and start background services."""

    # Existing initialization...
    queue_service = ResearchQueueService(queue_path=...)
    discovery_funnel = DiscoveryFunnelService(db_path=...)

    # NEW: Start automated searcher
    if enable_automated_search:
        searcher_scheduler = SearcherSchedulerService(queue_service)
        searcher_scheduler.start()
        logger.info("Automated searcher scheduler started")
    else:
        searcher_scheduler = None

    return {
        "queue_service": queue_service,
        "discovery_funnel": discovery_funnel,
        "searcher_scheduler": searcher_scheduler,
    }
```

**Step 4**: Add API endpoint to control scheduler
```python
# In src/api/management.py (if REST API exists)

@app.get("/api/v1/searcher/status")
def get_searcher_status():
    """Get automated searcher status."""
    return searcher_scheduler.get_status()

@app.post("/api/v1/searcher/start")
def start_searcher():
    """Start automated searcher."""
    searcher_scheduler.start()
    return {"status": "started"}

@app.post("/api/v1/searcher/stop")
def stop_searcher():
    """Stop automated searcher."""
    searcher_scheduler.stop()
    return {"status": "stopped"}

@app.post("/api/v1/searcher/run-now")
def run_searcher_now():
    """Trigger search run immediately."""
    results = searcher_scheduler.searcher.run_once()
    return {"results": results}
```

**Effort**: Medium (2-3 hours implementation and testing)
**Risk**: Medium (new background thread, needs monitoring)
**Impact**: High (enables automatic search execution)

---

## Finding 6: No Feedback Loop from Closure to VOI

### Problem Statement
When gaps are closed (papers found and integrated), the closure assessment doesn't feed back to revise VOI scores or re-prioritize the queue.

### Evidence

**File**: `src/services/paper_integration/orchestrator.py`

Closure assessment exists but:
- One-way only (assessment → storage)
- No feedback to discovery_funnel VOI
- No revision of queue priorities
- No learning from closure outcomes

### Impact
- System doesn't adapt to what gaps are actually resolvable
- High-VOI gaps that never close stay high priority
- Low-VOI gaps that close easily stay low priority
- No data-driven optimization

### Fix

**Step 1**: Add closure feedback to discovery_funnel
```python
# In discovery_funnel.py

@dataclass
class VOIGapWithClosure:
    voi_gap: VOIGap
    closure_assessment: Optional[GapClosure] = None
    closure_speed_hours: Optional[float] = None
    research_efficiency: Optional[float] = None  # VOI / time_to_close


def record_closure_with_feedback(
    self,
    gap_id: str,
    closure_type: ClosureType,
    closing_papers: List[str],
    time_to_close_hours: float,
    researcher_notes: str = ""
) -> VOIGapWithClosure:
    """
    Record closure AND compute feedback signal.
    """
    gap = self.get_gap(gap_id)

    closure = GapClosure(
        gap_id=gap_id,
        closure_type=closure_type,
        closing_papers=closing_papers,
        closed_at=datetime.now(timezone.utc),
        researcher_notes=researcher_notes
    )

    # Record closure
    self._record_closure_to_db(gap_id, closure)

    # Compute feedback signal
    closure_speed = time_to_close_hours
    research_efficiency = (gap.voi_score / closure_speed) if closure_speed > 0 else 0.0

    # Store for analysis
    gap_with_closure = VOIGapWithClosure(
        voi_gap=gap,
        closure_assessment=closure,
        closure_speed_hours=closure_speed,
        research_efficiency=research_efficiency
    )

    return gap_with_closure
```

**Step 2**: Feed back to queue for re-prioritization
```python
# In queue/service.py

def report_gap_closure(
    self,
    gap_id: str,
    closure_type: str,
    closing_papers: List[str],
    time_to_close_hours: float
) -> None:
    """
    Report gap closure and update queue priorities.
    """
    # Update target status
    target = self._targets.get(gap_id)
    if target:
        target.status = TargetStatus.CLOSED

        # Store closure metadata
        target.closure_type = closure_type
        target.closing_papers = closing_papers
        target.time_to_close_hours = time_to_close_hours

        # Compute research efficiency
        efficiency = target.voi_score / max(time_to_close_hours, 1.0)
        target.research_efficiency = efficiency

        # Update collector profile (learning signal)
        if target.assigned_to:
            collector = self.get_collector(target.assigned_to)
            if collector:
                # Update success rate
                collector.targets_completed += 1
                if closure_type in ["strongly_supported", "weakly_supported"]:
                    collector.gap_closure_rate = (
                        (collector.gap_closure_rate * (collector.targets_completed - 1) + 1.0)
                        / collector.targets_completed
                    )

                # Update average articles per target
                collector.avg_articles_per_target = (
                    (collector.avg_articles_per_target * (collector.targets_completed - 1) +
                     len(closing_papers))
                    / collector.targets_completed
                )

                self._collectors[target.assigned_to] = collector

        self._persist_state()
        logger.info(f"Gap {gap_id} closed with efficiency={efficiency:.2f}")
```

**Step 3**: Analyze closure patterns
```python
# New file: src/queue/closure_analytics.py

def analyze_closure_patterns(
    queue_service: ResearchQueueService
) -> Dict[str, Any]:
    """
    Analyze which gap types close successfully.
    Use to improve future VOI estimates.
    """
    closed_targets = [t for t in queue_service._targets.values()
                      if t.status == TargetStatus.CLOSED]

    by_gap_type = {}
    for target in closed_targets:
        gap_type = str(target.gap_type)
        if gap_type not in by_gap_type:
            by_gap_type[gap_type] = {
                "count": 0,
                "avg_voi": 0.0,
                "avg_time_hours": 0.0,
                "avg_efficiency": 0.0,
                "success_rate": 0.0
            }

        stats = by_gap_type[gap_type]
        stats["count"] += 1
        stats["avg_voi"] = (stats["avg_voi"] * (stats["count"] - 1) + target.voi_score) / stats["count"]
        stats["avg_time_hours"] = (
            (stats["avg_time_hours"] * (stats["count"] - 1) + target.time_to_close_hours)
            / stats["count"]
        ) if target.time_to_close_hours else 0
        stats["avg_efficiency"] = (stats["avg_efficiency"] * (stats["count"] - 1) +
                                  target.research_efficiency) / stats["count"]

    return {
        "total_closed": len(closed_targets),
        "by_gap_type": by_gap_type,
        "most_efficient_gap_type": max(
            by_gap_type.items(),
            key=lambda x: x[1]["avg_efficiency"]
        )[0] if by_gap_type else None
    }
```

**Effort**: Medium-High (2-3 hours implementation and testing)
**Risk**: Medium (adds complexity to closure reporting)
**Impact**: High (enables continuous learning and optimization)

---

## Summary of Fixes

| Finding | Fix | Effort | Risk | Impact |
|---------|-----|--------|------|--------|
| 1. VOI not used | Sort queue by VOI | Medium | Low | HIGH |
| 2. No user-specific VOI | Create researcher fit factors | High | Medium | HIGH |
| 3. VOI hardcoded | Call VOI scorer in gap predictor | Low | Low | MEDIUM |
| 4. Interp space table missing | Create table + wire phase outputs | Medium | Low | MEDIUM |
| 5. No auto search | Add scheduler service | Medium | Medium | HIGH |
| 6. No closure feedback | Implement feedback loop | High | Medium | MEDIUM |

---

## Recommended Implementation Order

1. **First** (Immediate, 2-3 hours):
   - Fix 1: VOI queue prioritization
   - Fix 3: VOI computation in gap predictor

2. **Second** (Next sprint, 4-5 hours):
   - Fix 5: Automated searcher scheduling
   - Fix 4: Interpretation space table

3. **Third** (Design review, 6+ hours):
   - Fix 2: Researcher-specific VOI
   - Fix 6: Closure feedback loop

---

## Success Metrics

After fixes implemented:

1. **VOI Impact**:
   - Queue targets ranked by VOI
   - High-VOI gaps resolved first
   - Measure: gap closure latency by VOI percentile

2. **Researcher Personalization**:
   - Recommendations adapt to researcher profile
   - Domain fit increases completion rate
   - Measure: closure rate by researcher type

3. **Automated Search**:
   - Queue backs up < 50 unresolved targets
   - Average search latency < 1 hour from gap detection
   - Measure: time-to-search distribution

4. **Feedback Loop**:
   - System learns which gaps are most resolvable
   - VOI estimates improve over time
   - Measure: prediction accuracy of closure speed

---

**Report Complete**
**Next Step**: Schedule panel review to prioritize fixes
