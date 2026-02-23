# Gap Resolution Process Improvements

**Date**: 2026-02-12
**Author**: Claude Code
**Purpose**: Design improvements based on manual gap resolution session

---

## 1. Process Review: What Happened

### Manual Steps I Performed

1. **Queried gaps endpoint** → Found 8 unjustified BN edges
2. **Did NOT check local corpus first** (user caught this)
3. **Searched web** for papers on each edge
4. **Created beliefs** with simple IDs like `noise`, `cognitive_load`
5. **Ingestion failed** (405 - endpoint not wired correctly)
6. **Used direct DB insertion** instead
7. **IDs didn't match** - had to fix `noise` → `sensory.noise`
8. **Keywords didn't match** - had to add "warmth" to content
9. **Server restart required** to pick up new beliefs
10. **Multiple iterations** to resolve all 8 edges

### What Should Have Been Automatic

| Step | Current | Should Be |
|------|---------|-----------|
| Check local corpus first | Manual | Automatic pre-search |
| Validate canonical IDs | None | Validate against BN_VARIABLE_MAPPINGS |
| Keyword enrichment | None | Ensure content contains mapping keywords |
| Hot reload web | Restart required | Live reload from DB |
| Ingestion endpoint | Broken (405) | Working POST endpoint |
| Gap → Search → Ingest | Manual | Automated pipeline |

---

## 2. Design Improvements Plan

### 2.1 Pre-Search Local Corpus Check

**File**: `src/services/gap_predictor.py`

Add method to check existing but unlinked evidence:

```python
def find_local_evidence_for_gap(self, gap: PredictedGap) -> List[Dict]:
    """
    Before suggesting external search, check:
    1. Unprocessed PDFs in data/pdfs/
    2. Extracted findings not yet converted to beliefs
    3. Existing beliefs that might match via keyword (not canonical ID)
    """
    evidence = []

    # Check extracted findings
    findings_dir = Path("data/extracted_findings")
    if findings_dir.exists():
        for jsonl_file in findings_dir.glob("*.jsonl"):
            # Search findings for gap-related keywords
            ...

    # Check existing beliefs via keyword matching
    keywords = self._get_gap_keywords(gap)
    for belief in self.web.beliefs.values():
        if self._belief_matches_keywords(belief, keywords):
            evidence.append(belief)

    return evidence
```

### 2.2 Canonical ID Validator

**File**: `src/services/belief_validator.py` (NEW)

```python
from src.services.edge_justification import BN_VARIABLE_MAPPINGS

class BeliefValidator:
    """Validate beliefs before insertion."""

    def validate_canonical_ids(self, belief: Belief) -> List[str]:
        """
        Check that environment_id and outcome_id match BN mappings.
        Returns list of warnings/suggestions.
        """
        warnings = []

        if belief.environment_id:
            valid_env_ids = self._get_all_valid_env_ids()
            if belief.environment_id not in valid_env_ids:
                suggestions = self._suggest_canonical_id(
                    belief.environment_id, 'environment'
                )
                warnings.append(
                    f"environment_id '{belief.environment_id}' not in BN mappings. "
                    f"Suggestions: {suggestions}"
                )

        # Similar for outcome_id
        return warnings

    def enrich_keywords(self, belief: Belief) -> Belief:
        """
        Ensure belief content contains keywords that will match
        BN variable mappings for its environment_id and outcome_id.
        """
        # If environment_id maps to keywords, check content contains at least one
        ...
```

### 2.3 Hot Reload Web State

**File**: `src/services/edge_justification.py`

```python
class EdgeJustificationService:
    def __init__(self, web: WebOfBelief = None, auto_reload: bool = True):
        self._web = web
        self._auto_reload = auto_reload
        self._last_load_time = None

    @property
    def web(self):
        """Lazy-load and auto-refresh web from DB."""
        if self._auto_reload:
            # Check if DB has been modified since last load
            if self._should_reload():
                self._reload_from_db()
        return self._web

    def _should_reload(self) -> bool:
        """Check if web_persistence.db has been modified."""
        db_path = Path("data/web_persistence.db")
        if db_path.exists():
            mtime = db_path.stat().st_mtime
            if self._last_load_time is None or mtime > self._last_load_time:
                return True
        return False
```

### 2.4 Automated Gap Resolution Pipeline

**File**: `src/services/gap_resolver.py` (NEW)

```python
class GapResolver:
    """
    Automated pipeline for resolving knowledge gaps.

    Pipeline:
    1. Identify gap
    2. Check local corpus (unprocessed papers, existing findings)
    3. If local evidence found → create beliefs
    4. If not → generate search queries
    5. (Optional) Execute web search
    6. Validate and ingest findings
    7. Verify gap is resolved
    """

    def resolve_gap(self, gap: PredictedGap, auto_search: bool = False) -> GapResolutionResult:
        """
        Attempt to resolve a gap.

        Returns:
            GapResolutionResult with status, evidence found, actions taken
        """
        result = GapResolutionResult(gap_id=gap.gap_id)

        # Step 1: Check local corpus
        local_evidence = self._check_local_corpus(gap)
        if local_evidence:
            result.local_evidence = local_evidence
            beliefs = self._create_beliefs_from_evidence(local_evidence, gap)
            result.beliefs_created = beliefs
            result.status = "resolved_locally"
            return result

        # Step 2: Generate search queries
        queries = self._generate_search_queries(gap)
        result.suggested_queries = queries

        # Step 3: Optional web search
        if auto_search:
            search_results = self._execute_searches(queries)
            result.search_results = search_results

        result.status = "pending_external_evidence"
        return result
```

### 2.5 Fix Ingestion Endpoint

**File**: `app/routes/ingestion.py`

The 405 error suggests the router isn't properly mounted. Check `app/main.py`:

```python
# Ensure ingestion router is included
from app.routes.ingestion import router as ingestion_router
app.include_router(ingestion_router)
```

---

## 3. Implementation Tasks

| ID | Task | Priority | Effort |
|----|------|----------|--------|
| GR-1 | Create `BeliefValidator` class | HIGH | 2h |
| GR-2 | Add `find_local_evidence_for_gap()` to GapPredictor | HIGH | 3h |
| GR-3 | Implement hot-reload in EdgeJustificationService | MEDIUM | 2h |
| GR-4 | Create `GapResolver` pipeline class | HIGH | 4h |
| GR-5 | Fix ingestion endpoint wiring | HIGH | 1h |
| GR-6 | Add canonical ID suggestions to gap output | MEDIUM | 2h |
| GR-7 | Create `/api/v1/gaps/{id}/resolve` endpoint | MEDIUM | 3h |
| GR-8 | Add tests for gap resolution pipeline | HIGH | 3h |

---

## 4. API Endpoint Additions

```yaml
POST /api/v1/integration/gaps/{gap_id}/resolve:
  description: Attempt to resolve a specific gap
  parameters:
    - gap_id: string
    - check_local: boolean (default: true)
    - auto_search: boolean (default: false)
  returns:
    - status: resolved_locally | pending_external | unresolvable
    - local_evidence: list of matching findings/beliefs
    - suggested_queries: list of search queries
    - beliefs_created: list of new belief IDs

GET /api/v1/integration/gaps/{gap_id}/local-evidence:
  description: Find local evidence that might address a gap
  returns:
    - unprocessed_papers: list
    - extracted_findings: list
    - keyword_matched_beliefs: list
```

---

## 5. Configuration

Add to `config/gap_resolution.yaml`:

```yaml
gap_resolution:
  # Always check local corpus before suggesting external search
  check_local_first: true

  # Paths to check for unprocessed papers
  unprocessed_paths:
    - data/pdfs/
    - data/abstracts/

  # Extracted findings directory
  findings_path: data/extracted_findings/

  # Canonical ID validation
  validate_canonical_ids: true
  suggest_corrections: true

  # Auto-reload web from DB
  hot_reload: true
  reload_check_interval_seconds: 5
```
