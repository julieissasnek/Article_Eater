# Renaming: seven_panel → article_essence_extraction

**Date**: 2026-02-11
**Status**: IN PROGRESS
**Rationale**: "seven_panel" is outdated naming from when extraction focused on 7 specific fields. Now we have 16+ extraction templates for different article types.

---

## Completed Changes

### 1. Database Migration
- Created: `migrations/020_rename_seven_panel_to_article_essence.sql`
- Renames `seven_panel` table to `article_essence`
- Added columns: `article_type`, `extraction_template`

### 2. Core Files Updated

| File | Change |
|------|--------|
| `app/services/extract_article_essence.py` | NEW (renamed from extract_7panel.py) |
| `app/db.py` | Table creation uses `article_essence` |
| `app/core/policy.py` | Uses `article_essence_extraction`, with backward compat |
| `config/app.policy.json` | Uses new naming |
| `contracts/ae_af/README.md` | Documents extraction templates |

### 3. Prompts
- New prompt: `prompts/ARTICLE_ESSENCE_findings.md` (to be created)
- Legacy prompt: `prompts/SEVEN_PANEL_pass2_findings.md` (kept for fallback)

---

## Backward Compatibility

The following aliases are maintained for backward compatibility:

```python
# In extract_article_essence.py
extract_seven_panel = extract_findings_from_text  # Legacy alias

# In policy.py
model_for("seven_panel", ...)  # Maps to article_essence_extraction
```

---

## Remaining Work (Technical Debt)

### Schema Classes (src/contracts/schemas.py)
- `SevenPanelArtifact` → `ArticleEssenceArtifact`
- `SevenPanelItem` → `ArticleEssenceItem`
- Requires careful migration due to Pydantic model usage

### Agent Files (src/agents/)
- `agent_stubs.py` - Uses SevenPanelArtifact, store.attach_seven_panel
- `agent_panels_v2.py` - Has extract_seven_panel_v2 function
- `agent_finder.py` - References seven_panel

### Service Files
- `graph_service_fallback.py` - attach_seven_panel method
- May have graph store integration

### Test Files
- `scripts/test_extract_7panel_parsing.py` → rename

### Documentation
- Various docs reference "seven panel"
- Update after code migration complete

---

## Migration Strategy

### Phase 1: Core Rename (DONE)
- Database table
- Extraction service
- Policy configuration
- Contract documentation

### Phase 2: Schema Classes (FUTURE)
- Create new Pydantic models with `ArticleEssence` prefix
- Add `@deprecated` decorator to old models
- Migrate callers incrementally

### Phase 3: Agent Layer (FUTURE)
- Update agent_stubs.py to use new models
- Update graph service methods
- Rename agent_panels_v2 functions

### Phase 4: Cleanup (FUTURE)
- Remove backward compatibility aliases
- Delete deprecated code paths
- Update all documentation

---

## Why Incremental?

1. **Risk management**: Renaming schemas can break serialization
2. **Test coverage**: Need to verify each change doesn't break extraction
3. **Production safety**: Real papers should process before deep refactors

---

## REMOVE_BY Dates

| Item | Remove By | Location |
|------|-----------|----------|
| `extract_seven_panel` alias | 2026-03-11 | extract_article_essence.py |
| `seven_panel` policy fallback | 2026-03-11 | policy.py |
| Legacy prompt fallback | 2026-04-01 | extract_article_essence.py |
