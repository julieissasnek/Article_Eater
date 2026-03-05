# Quick Reference: Using Annotations in Card Generation

## For Tab Generators

When you have access to `source_data` in a tab generator, you can now use annotation data:

### Check for Disputes (Debate Tab)
```python
def generate_debate_tab(source_data: Dict[str, Any]) -> CardTab:
    # Disputes are automatically flattened into source_data
    disputes = source_data.get("disputes", [])

    if disputes:
        # Use dispute data
        prose = "Active disputes in the literature:\n"
        for dispute in disputes:
            prose += f"  • {dispute}\n"
    else:
        # Fallback if no annotations
        prose = source_data.get("competing_accounts", "No known disputes.")

    return CardTab(tab_name="debate", prose=prose)
```

### Check for Replication Status (Evidence Tab)
```python
def generate_evidence_tab(source_data: Dict[str, Any]) -> CardTab:
    # Replication status is automatically flattened into source_data
    replication = source_data.get("replication_status")

    prose = f"Based on {source_data.get('n_findings')} findings."
    if replication:
        prose += f" {replication}"

    return CardTab(tab_name="evidence", prose=prose)
```

### Check for Surprise Flags (Overview Tab)
```python
def generate_overview_tab(source_data: Dict[str, Any]) -> CardTab:
    # Surprise flags are automatically flattened into source_data
    surprises = source_data.get("surprise_flags", [])

    prose = source_data.get("description", "")

    if surprises:
        prose += "\n\n**Notable findings:**\n"
        for surprise in surprises:
            prose += f"  • {surprise}\n"

    return CardTab(tab_name="overview", prose=prose)
```

## For Full Annotation Access

If you need to access all annotation metadata (author, confidence, created timestamp), use the full `annotations` dict:

```python
# Raw annotation data (organized by type)
all_annotations = source_data.get("annotations", {})

# Get all disputes with full metadata
disputes_raw = all_annotations.get("DISPUTE", [])
for dispute in disputes_raw:
    author = dispute["author"]
    confidence = dispute["confidence"]  # 0.0-1.0
    created = dispute["created"]  # ISO 8601
    content = dispute["content"]
```

## In LLM Prompts

You can mention annotation data in LLM prompts for richer context:

```python
def build_evidence_context(source_data: Dict[str, Any]) -> str:
    context = f"""
    Evidence base: {source_data['n_findings']} findings from {source_data['n_papers']} papers
    Confidence: {source_data['omega']}
    """

    # If annotation data exists, mention it
    replication = source_data.get("replication_status")
    if replication:
        context += f"\n\nReplication history: {replication}"

    return context
```

## Handling Missing Annotations

All annotation fields are **optional**. If an entity has no annotations, the fields simply won't be present:

```python
# Safe access pattern (always works)
disputes = source_data.get("disputes", [])  # Empty list if no annotations
surprises = source_data.get("surprise_flags", [])  # Empty list if no annotations
replication = source_data.get("replication_status")  # None if no annotations

# No need for try/except — graceful degradation is built in
```

## When Does Enrichment Happen?

Enrichment happens **automatically** in `CardGenerationOrchestrator.generate_card()`:

1. GenerationRequest arrives with source_data
2. `enrich_source_data_with_annotations()` is called (see line 540)
3. Annotation service is queried for all active annotations on the entity
4. Enriched source_data (with annotations) is used for all tab generation
5. Tab generators see annotation data in source_data

**You don't need to call enrichment manually** — it's done by the orchestrator.

## Testing Annotations in Your Generator

When writing tests for tab generators that use annotations:

```python
from unittest.mock import Mock
from src.services.annotation_service import Annotation, AnnotationType

def test_debate_tab_with_disputes():
    # Create mock annotation data
    source_data = {
        "entity_id": "test",
        "title": "Test",
        "disputes": [
            "Theory X argues alternative mechanism",
            "Theory Y challenges core assumption",
        ],
    }

    # Test your generator
    tab = my_debate_tab_generator(source_data)

    # Verify annotation data appears in output
    assert "Theory X" in tab.prose
```

## Where Are Annotations Stored?

- **Database**: SQLite table `annotations` in the integrated database
- **Query API**: `AnnotationService.get_active_annotations(target_type, target_id)`
- **In Cards**: Stored in `iceberg.raw_data` for provenance and regeneration
- **During Generation**: Flattened into `source_data` for easy access by tab generators

## Annotation Types Used in Card Generation

| Type | Tab | Meaning | Example |
|------|-----|---------|---------|
| DISPUTE | Debate | Active disagreement | "Competing theory proposes alternative mechanism" |
| SURPRISE_FLAG | Overview | Unexpected finding | "Effect size far exceeds expectations" |
| REPLICATION_STATUS | Evidence | Replication history | "Successfully replicated 8 of 9 times" |
| UNANSWERED_QUESTION | All | Open research question | "Does effect persist in all populations?" |

Other annotation types (CALIBRATION_NOTE, SENSITIVITY_FLAG, etc.) are available in the full `annotations` dict but not auto-flattened.

## Graceful Degradation

If the annotation service:
- Fails to initialize
- Throws an error during query
- Returns no annotations for an entity

**Result**: Card generation continues normally. No annotations appear in source_data, but tabs still generate with original data. No crashes.

---

**See Also**:
- `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/src/services/annotation_service.py` — Full annotation API
- `/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/ANNOTATION_CARD_INTEGRATION_2026-03-05.md` — Technical details
- `tests/test_annotation_card_integration.py` — Example tests
