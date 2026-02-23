# DB Investigation Report (M-05a)
## February 22, 2026
## System: OPUS/CC

---

## Summary

Two web persistence databases exist with vastly different content:
- **v1** (`data/web_persistence.db`): 12,668 beliefs - PDF extraction data
- **v2** (`data/web_persistence_v2.db`): 106 beliefs - stub/scaffold beliefs

---

## Findings

### 1. web_persistence.db (v1)

**Row count**: 12,668 beliefs

**Schema** (26 columns):
```
belief_id, web_id, content, level, status, credence_value, credence_uncertainty,
credence_n_supporting, credence_n_contradicting, credence_n_observations,
theory_id, entrenchment, domain, attribute_id, outcome_type, scope,
environment_id, outcome_id, evidence_cluster_id, tags, paper_ids,
epistemic_v2, created_at, updated_at, off_topic, template_ids
```

**Sample data** (first 5 rows):
- Content is raw PDF extraction: "Location C; Microphone 1: 52.4 dB(A)..."
- belief_id format: `pdf:doi:10.17863/cam.41365:doi:10.17863/cam.41365-TBL-C003`
- Tags: `["source:pdf", "provenance:pdf_confirmed"]`
- Dates: 2026-02-22 (today's date)
- All have `off_topic: 0`

**Interpretation**: This is the PDF extraction pipeline output. Raw claims extracted from papers, tagged with provenance. No theory alignment or template mapping visible.

### 2. web_persistence_v2.db (v2)

**Row count**: 106 beliefs

**Schema** (24 columns - missing `off_topic` and `template_ids`):
```
belief_id, web_id, content, level, status, credence_value, credence_uncertainty,
credence_n_supporting, credence_n_contradicting, credence_n_observations,
theory_id, entrenchment, domain, attribute_id, outcome_type, scope,
environment_id, outcome_id, evidence_cluster_id, tags, paper_ids,
epistemic_v2, created_at, updated_at
```

**Sample data** (first 5 rows):
- Content is empty (most rows)
- belief_id format: `doi:10.25916/sut.26402764.v1:TBL-20260216233658-036:C001`
- Tags: `["source:extraction_pipeline"]`
- Status: mostly `stub`
- Dates: 2026-02-21 (yesterday)

**Interpretation**: This appears to be an earlier extraction run with different schema. Stubs without content.

### 3. db_locator.py Behavior

**Location**: `src/services/db_locator.py`

**Resolution logic** (`resolve_web_db`):
- Candidates: explicit → env `AE_WEB_DB` → `data/web_persistence.db` → `data/web_persistence_v2.db`
- Default preference: `"integrated"` (not `"latest"`)
- `integrated_score` prioritizes: beliefs > bridges > explains+contradicts > constraints > mtime

**Effect**: With v1 having 12,668 beliefs vs v2's 106, `resolve_web_db()` will always return **v1** unless explicitly overridden.

### 4. Usages of db_locator

```
src/services/db_locator.py (definition)
scripts/seed_beliefs_from_templates.py (uses resolve_web_db)
src/services/web_of_belief.py (imports but may not call)
```

---

## Architecture Assessment

| Aspect | v1 (web_persistence.db) | v2 (web_persistence_v2.db) |
|--------|------------------------|--------------------------|
| Content | PDF extraction (raw) | Stubs (empty content) |
| Count | 12,668 | 106 |
| Schema | 26 columns | 24 columns |
| Provenance | `source:pdf` | `source:extraction_pipeline` |
| Template link | `template_ids` column | None |
| Status | Mixed (tentative, established) | Mostly stub |

---

## Recommendation for HUMAN Decision (M-05b)

**Observation**: The two DBs serve different purposes:
1. v1 = PDF-extracted raw claims (high volume, low quality, no theory alignment)
2. v2 = Earlier extraction with stubs (low volume, no content)

**Neither DB contains panel-calibrated beliefs.** The belief seeder script (`seed_beliefs_from_templates.py`) writes to whichever DB `resolve_web_db()` returns — currently v1.

**Options**:

1. **Single DB with two tiers**:
   - Add a `tier` column to beliefs: `tier1_panel_calibrated` vs `tier2_extraction`
   - Query by tier for different use cases
   - Panel beliefs get higher credence floor

2. **Dual DB architecture**:
   - Keep v1 for extraction
   - Use v2 (or new DB) for panel-calibrated beliefs only
   - db_locator returns different DB based on `prefer="panel"` vs `prefer="extraction"`

3. **Consolidate to v1, deprecate v2**:
   - v2 content is redundant (stubs with empty content)
   - v1 already has more features (`off_topic`, `template_ids`)
   - Delete v2, add tier column to v1

**Suggested**: Option 3 (consolidate). v2 adds nothing; v1 already has template_ids column for panel integration.

---

## Raw Query Output

### Count queries:
- v1 beliefs: 12,668
- v2 beliefs: 106

### Schema comparison:
v1 has 26 columns; v2 has 24 columns.
v1 additional columns: `off_topic`, `template_ids`

### db_locator.py behavior:
Selects DB with highest `integrated_score` = (beliefs, bridges, explains+contradicts, constraints, mtime).
v1 wins with 12,668 vs 106 beliefs.

---

*M-05a complete. Awaiting HUMAN decision on M-05b (consolidation strategy).*
