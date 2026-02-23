# Sprint LIFECYCLE Completion Report

**Date**: 2026-02-09
**Version**: V23.0.1

## Summary

Implemented unified paper lifecycle tracking to monitor each paper's journey through the full processing pipeline: Discovery → Search → Retrieval → Storage → Typing → Extraction → Synthesis. This provides a single source of truth for paper processing health, replacing fragmented tracking across processing_queue, ephemeral JSONL files, and various outputs.

## Files Changed

| File | Type | Description |
|------|------|-------------|
| `db/sql/018_paper_lifecycle.sql` | NEW | SQLite schema migration for lifecycle tables and views |
| `src/services/paper_lifecycle.py` | NEW | Core lifecycle service (~780 lines) with stage transitions, context managers, queries |
| `app/tasks/pipeline.py` | MODIFIED | Integrated lifecycle tracking at each pipeline stage |
| `app/routes/lifecycle.py` | NEW | REST API endpoints for lifecycle queries and health dashboard |
| `app/main.py` | MODIFIED | Registered lifecycle router at `/api/v1/lifecycle/` |
| `scripts/ae_streamlit_control_room.py` | MODIFIED | Added Section 5: Paper Lifecycle dashboard |
| `/Users/davidusa/REPOS/CLAUDE.md` | MODIFIED | Added sprint completion report requirement |

## Key Design Decisions

1. **Paper-centric tracking**: Unlike the job-centric `processing_queue`, lifecycle tracks each paper's journey regardless of which job processed it.

2. **Dual-table design**:
   - `paper_lifecycle` for audit trail (every transition recorded)
   - `paper_metrics` for aggregate metrics (updated after each stage)
   - Added columns to `articles` table for current stage

3. **Stage enumeration**: 11 stages covering full path:
   - DISCOVERED → SEARCHED → RETRIEVED → STORED → TYPED → EXTRACTING → EXTRACTED → SYNTHESIZING → SYNTHESIZED → ARCHIVED → FAILED

4. **Context manager pattern**: `stage_context()` provides automatic success/failure tracking with timing:
   ```python
   with lifecycle_service.stage_context(paper_id, LifecycleStage.EXTRACTING, run_id=run_id) as ctx:
       # ... do work ...
       ctx.set_metrics(n_claims=5, n_rules=3)
   ```

5. **Graceful degradation**: All lifecycle tracking is wrapped in try/except to prevent pipeline failures if tracking unavailable.

## Integration Points

### Pipeline Integration (pipeline.py)
- After paper_id known: Transition to EXTRACTING
- After text extraction: Update text_source/text_length metrics
- After claims/rules: Update n_claims/n_rules/n_findings
- After table extraction: Update n_tables/n_table_claims
- Before web integration: Complete EXTRACTING → EXTRACTED → SYNTHESIZING
- After web integration: Complete SYNTHESIZING → SYNTHESIZED with coherence_score
- Final status: Archive or fail based on pipeline outcome

### API Endpoints (/api/v1/lifecycle/)
- `GET /health` - Pipeline health summary
- `GET /stages` - Paper distribution by stage
- `GET /papers` - Papers filtered by stage/status
- `GET /papers/blocked` - Blocked papers queue
- `GET /paper/{paper_id}` - Individual paper status
- `GET /paper/{paper_id}/history` - Full lifecycle history
- `POST /transition` - Manual stage transition
- `POST /paper/{paper_id}/unblock` - Reset blocked paper

### Streamlit Dashboard
- Section 5 in control room with:
  - Stage distribution bar chart
  - Blocked papers queue
  - Recent lifecycle activity
  - Pipeline health summary (7-day success rates)

## Testing Status

- All syntax checks pass
- Schema migration ready to apply (`db/sql/018_paper_lifecycle.sql`)
- Integration is non-breaking (graceful degradation if tables don't exist)
- Manual testing recommended after migration

## Next Steps

1. Run schema migration: `sqlite3 ae.db < db/sql/018_paper_lifecycle.sql`
2. Add tests for `PaperLifecycleService`
3. Consider adding lifecycle tracking to other processing pathways (Article Finder → AE)
4. Add alerting for blocked papers (email/Slack notifications)

---

*Sprint completed: 2026-02-09*
*Co-Authored-By: Claude Opus 4.5*
