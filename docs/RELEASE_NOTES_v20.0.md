# ⚠️ SUPERSEDED — See (newer version exists) for current version

# Article Eater v20.0

**Date:** 2025-11-15 21:46:41

## Summary
- **Findings schema upgrade:** add `effect_size_type`, `ci_lower`, `ci_upper`.
- **CI-aware extraction:** new Pass-2 findings prompt (`prompts/7panel_pass2_findings_v20.md`).
- **Rule interactions:** new `rule_interactions` table and `app/relational_analysis.py` (contradictions + CI conflicts; synergy/chaining hooks).
- **HITL UI:** `/interactions/review` router + `frontend/interactions.html` & `js/interactions.js` for inspection and actions.
- **RAG trigger:** POST action `prompt` writes `disambiguation_prompt` and enqueues an L0 harvest job with rich query (when `processing_queue` exists).
- **Governance:** contracts added; superseded files archived; no deletions.

## Upgrade
1. Run migration: `python scripts/migrate_v20.py ./ae.db` (or your DB path).
2. In `app/main.py`, include the router:
   ```python
   from .routes import interactions
   app.include_router(interactions.router)
   ```
3. Use the new Pass-2 prompt in your pipeline or policies.

## Backward Compatibility
- Existing DBs: use migration script.
- Fresh installs: 015 schema plus patch ensures CI columns exist.