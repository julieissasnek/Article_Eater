# v20.6.0 — Control Room, Confidence Engine, Raw Abstract, Agents powered (no deletions)
- NEW: `/admin` Control Room GUI (Prompts + Confidence tabs).
- NEW: `/api/admin` endpoints to list/update prompts and confidence weights.
- NEW: `prompts/7panel_pass2_findings.md` (explicit stats+CI contract).
- NEW: `confidence_config.yml` read/write; agents and BN use it at runtime.
- NEW: Provider-agnostic LLM agents (`src/agents/agent_finder.py`, `agent_aggregator.py`).
- NEW: `scripts/run_migrations_v20_6.py` adds `articles.raw_abstract` (idempotent).
- NEW: Safe patchers: `scripts/patch_schemas_v206.py`, `scripts/patch_wire_admin_v206.py` (archive originals; no deletes).
- Governance: All replaced files saved under `archive/_replaced_*`.