# VOI Collector Contract

**Version**: 1.0
**Date**: 2026-02-15
**Schema ID**: `ae.voi_collector.v1`

---

## Purpose

A VOI Collector is any agent (human or automated) that works to resolve
ResearchTargets from the Research Queue. This contract defines:

1. How collectors claim and work on targets
2. What they must report back
3. How their work is evaluated

---

## Collector Types

| Type | Description | Typical Targets |
|------|-------------|-----------------|
| `human_researcher` | Domain expert manually searching | HIGH priority, research opportunities |
| `human_assistant` | RA or student searcher | MEDIUM priority, systematic searches |
| `automated_searcher` | Bot using Semantic Scholar/PubMed APIs | LOW priority, bulk screening |
| `zotero_watcher` | Monitors Zotero for new additions | All — passive discovery |

---

## Collector Interface

### Registration

```python
@dataclass
class CollectorProfile:
    """Profile for a VOI collector."""
    collector_id: str
    collector_type: CollectorType
    name: str

    # Capabilities
    can_access_databases: List[str]  # ["semantic_scholar", "pubmed", "zotero"]
    can_access_paywalled: bool  # Has university library access?
    preferred_domains: List[str]  # ["healthcare", "offices", "education"]

    # Capacity
    max_concurrent_targets: int
    typical_turnaround_hours: float

    # Performance (tracked by system)
    targets_completed: int = 0
    gap_closure_rate: float = 0.0
    avg_articles_per_target: float = 0.0
```

### Claiming a Target

```python
def claim_target(
    collector_id: str,
    target_id: Optional[str] = None  # None = get next from queue
) -> ClaimResult:
    """
    Claim a research target to work on.

    Returns:
        ClaimResult with target details and search guidance
    """
    pass

@dataclass
class ClaimResult:
    success: bool
    target: Optional[ResearchTarget]
    search_guidance: SearchGuidance
    deadline: datetime  # When claim expires if no progress
```

### Search Guidance

```python
@dataclass
class SearchGuidance:
    """
    Guidance for the collector on how to search.

    Generated from VOI analysis and cross-field vocabulary.
    """
    # Primary queries
    primary_queries: List[str]

    # Expanded queries (cross-field vocabulary)
    expanded_queries: List[str]

    # Boolean combinations
    boolean_query: str  # e.g., "(stress recovery OR restoration) AND (architecture OR built environment)"

    # Recommended databases
    databases: List[DatabaseRecommendation]

    # What to look for
    target_study_types: List[str]  # ["RCT", "quasi-experimental", "meta-analysis"]
    target_populations: List[str]  # ["adults", "office workers"]
    target_settings: List[str]  # ["healthcare", "workplace"]

    # Theory predictions (what the article should test)
    mechanism_to_test: str
    expected_finding_pattern: str

    # Negative result guidance
    null_result_indicators: List[str]  # Signs that no articles exist
    when_to_stop: str  # Satisficing criteria
```

---

## Reporting Results

### SearchReport

```python
@dataclass
class SearchReport:
    """Report from a VOI collector about their search."""
    report_id: str
    collector_id: str
    target_id: str

    # Search executed
    queries_used: List[str]
    databases_searched: List[str]
    search_date: datetime
    time_spent_minutes: int

    # Results
    result_type: SearchResultType  # FOUND_RELEVANT, FOUND_TANGENTIAL, NOT_FOUND, INCONCLUSIVE

    # If articles found
    articles_found: List[ArticleReference]

    # If no articles found
    null_result_evidence: Optional[NullResultEvidence]

    # Collector's assessment
    confidence: float  # 0-1, how confident in search completeness
    notes: str
    is_research_opportunity: bool
    research_opportunity_framing: Optional[str]
```

### ArticleReference

```python
@dataclass
class ArticleReference:
    """Reference to a found article."""
    doi: Optional[str]
    title: str
    authors: List[str]
    year: int
    venue: str

    # Relevance assessment
    relevance_score: float  # 0-1
    relevance_rationale: str

    # Retrieval status
    pdf_available: bool
    pdf_path: Optional[str]  # If already in Zotero
    retrieval_method: Optional[RetrievalMethod]

    # What gap it addresses
    addresses_gap: bool
    gap_closure_estimate: float  # Estimated VOI reduction
```

### NullResultEvidence

```python
@dataclass
class NullResultEvidence:
    """
    Evidence that no relevant articles exist.

    This is valuable information — it identifies research opportunities.
    """
    # Search thoroughness
    n_databases_searched: int
    n_queries_tried: int
    n_results_screened: int

    # Why no articles found
    reason: NullResultReason
    # TOPIC_UNSTUDIED: No one has studied this
    # WRONG_TERMINOLOGY: Maybe different field uses different terms
    # TOO_SPECIFIC: Need broader search
    # PAYWALL_BARRIER: Articles may exist but inaccessible

    # Confidence this is a real gap
    confidence_is_gap: float

    # Research opportunity details
    suggested_study_design: str
    suggested_population: str
    suggested_setting: str
    predicted_contribution: str  # What this study would add to the field
```

---

## Workflow

```
1. CLAIM
   Collector claims target from queue
   Target status → ASSIGNED

2. SEARCH
   Collector executes search following guidance
   May use any database, any method

3. REPORT
   Collector submits SearchReport
   - If articles found → queue for ingestion
   - If not found → assess as research opportunity

4. VERIFY
   System ingests found articles
   Measures actual gap closure (VOI before/after)
   Updates collector performance metrics

5. CLOSE or ESCALATE
   - If gap closed → Target status → CLOSED
   - If research opportunity → add to opportunity registry
   - If inconclusive → escalate to human_researcher
```

---

## Performance Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Completion Rate | % of claimed targets completed | > 80% |
| Gap Closure Rate | % of targets that actually close gap | > 40% |
| Precision | % of found articles that are relevant | > 70% |
| Turnaround | Hours from claim to report | < 48h |
| Research Opportunity Quality | % of opportunities adopted by researchers | > 10% |

---

## Research Opportunity Registry

When a collector determines no articles exist, they create a research opportunity:

```python
@dataclass
class ResearchOpportunity:
    """A gap that requires new research, not existing articles."""
    opportunity_id: str
    source_target_id: str

    # The gap
    gap_description: str
    theory_drivers: List[str]
    mechanism_to_test: str

    # Why it matters
    voi_score: float
    impact_rationale: str

    # Suggested study
    suggested_design: str
    suggested_population: str
    suggested_setting: str
    suggested_measures: List[str]

    # Predictions
    predicted_finding: str
    null_hypothesis: str

    # Status
    status: OpportunityStatus  # PROPOSED, VALIDATED, IN_PROGRESS, PUBLISHED
    researcher_contact: Optional[str]
    publication_doi: Optional[str]

    created_at: datetime
    created_by: str  # collector_id
```

---

## Integration with Zotero

For collectors with Zotero access:

```python
def sync_zotero_to_queue(collector_id: str) -> List[ArticleReference]:
    """
    Scan collector's Zotero library for articles that match open targets.

    This enables passive discovery — researcher adds paper to Zotero
    for other reasons, system notices it addresses an open gap.
    """
    pass
```

---

## Expert Guidance (embedded in system)

- **Simon**: Satisficing — define clear stopping criteria, don't over-search
- **Bates**: Berrypicking — searches evolve, follow promising leads
- **Kleinberg**: Network analysis — find highly-cited papers first
- **Pearl**: Attribution — understand why searches fail to improve future
