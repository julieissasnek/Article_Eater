# ACTIVE_TASKS.md

*Auto-updated by Claude Code sessions*

This file tracks which tasks are actively being worked on by which terminal. **Check this file BEFORE starting any task.**

---

## Protocol

### Before Starting Work
1. **Read this file** to see what's claimed
2. **Claim your task** by adding a row to Active Claims
3. **Start work** only after claiming

### While Working
- Update status periodically if long-running
- Note any blockers in the Notes column

### When Done
1. **Move to Completed Today** section with outcome
2. **Remove from Active Claims**
3. **Update TASKS.md** with completion status

---

## Active Claims

| Task ID | Description | Terminal | Claimed At | Status | Notes |
|---------|-------------|----------|------------|--------|-------|
| — | — | — | — | — | — |

---

## Available Tasks (Not Claimed)

### High Priority (Infrastructure)
| Task ID | Description | Priority | Dependencies |
|---------|-------------|----------|--------------|
| — | All BIB tasks complete | — | — |

### Medium Priority (Extraction Tables - 3 Partial Remaining)
| Task ID | Description | Priority | Dependencies |
|---------|-------------|----------|--------------|
| EXT-14 | Complete Narrative Review spec | P2 | SCHEMA-1 ✓ |
| EXT-15 | Complete Theoretical spec | P2 | SCHEMA-1 ✓ |
| EXT-16 | Complete Thought Piece spec | P2 | SCHEMA-1 ✓ |

### Sprint 3.0 Extensions
| Task ID | Description | Priority | Dependencies |
|---------|-------------|----------|--------------|
| 3.0.1-D | Extended API layer (20 endpoints) | P2 | 3.0.1-B ✓ |
| 3.0.2-F | Add RELATED, TRENDING, CANONICAL patterns | P2 | 3.0.2-E ✓ |
| 3.0.3-E | Network visualization (vis.js deep integration) | P2 | 3.0.3-C ✓ |
| 3.0.4-F | Report generation (PDF/Markdown) | P3 | 3.0.4-E ✓ |
| 3.0.5-G | Export audit trail | P3 | 3.0.5-A ✓ |

### BibTeX Integration (AF-AE)
| Task ID | Description | Priority | Dependencies |
|---------|-------------|----------|--------------|
| — | All BIB tasks complete | — | — |

---

## Completed Today (2026-02-09)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| SCHEMA-1 | Add new rule types + causal/argument fields | Terminal-3 | 09:15 | Created ae.rule.v2.schema.json, ae.claim.v2.schema.json, argument_schemes.json |
| SCHEMA-2 | Update extraction specs with panel additions | Terminal-3 | 09:30 | Created EXTRACTION_TEMPLATE_PANEL_ADDITIONS_2026_02_09.md |
| SCHEMA-3 | Create stimulus documentation template | Terminal-3 | 09:45 | Created STIMULUS_DOCUMENTATION_TEMPLATE_2026_02_09.md |
| BUG-1 | Fix health check script integer comparison | Terminal-3 | 10:00 | Fixed ${VAR:-0} defaults in scheduled_health_check.sh |
| EXT-13 | Complete Systematic Review spec | Terminal-3 | 10:15 | Updated to v1.1 with panel additions |
| EXT-5 | Observational Field Study spec | Terminal-3 | 10:30 | Created EXTRACTION_TEMPLATE_OBSERVATIONAL_FIELD_2026_02_09.md |
| EXT-9 | Case Study spec | Terminal-3 | 10:45 | Created EXTRACTION_TEMPLATE_CASE_STUDY_2026_02_09.md |
| EXT-11 | Mixed Methods spec | Terminal-3 | 11:00 | Created EXTRACTION_TEMPLATE_MIXED_METHODS_2026_02_09.md |
| EXT-6 | Phenomenological Study spec | Terminal-3 | 11:15 | Created EXTRACTION_TEMPLATE_PHENOMENOLOGICAL_2026_02_09.md |
| EXT-7 | Ethnographic Study spec | Terminal-3 | 11:30 | Created EXTRACTION_TEMPLATE_ETHNOGRAPHIC_2026_02_09.md |
| EXT-8 | Grounded Theory Study spec | Terminal-3 | 11:45 | Created EXTRACTION_TEMPLATE_GROUNDED_THEORY_2026_02_09.md |
| EXT-10 | Interview Study spec | Terminal-3 | 12:00 | Created EXTRACTION_TEMPLATE_INTERVIEW_STUDY_2026_02_09.md |

## Completed (2026-02-08)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| 3.0-PLAN | Sprint 3.0 Planning (expert panel) | Terminal-1 | 20:30 | Created SPRINT_3.0_PLAN.md with 21 expert panel consultation. Updated TASKS.md with full breakdown. |
| 3.0.1-A/B/C | Unified API (Core 7 endpoints) | Terminal-1 | 20:30 | Created app/routes/api_unified.py (~700 lines). Beliefs, queries, export, communities, constraints, papers, admin endpoints. |
| 3.0.2-A/E | Query Engine + Multi-AI Orchestration | Terminal-1 | 20:30 | Created src/services/llm_query_bridge.py (~600 lines). Multi-model tiering (Haiku→Sonnet→Opus), query type detection, progressive disclosure. |
| 3.0.3-A/B/C/D | Streamlit Interface | Terminal-1 | 20:30 | Created streamlit_app/ with 6 files (~2000 lines). User types with common questions, query interface, explore page, communities page, export wizard, admin dashboard. |
| 3.0.4-A/B/C/D/E | Export Engine | Terminal-1 | 20:30 | Created src/services/export_engine.py (~500 lines). BibTeX generator, evidence summaries with scope metadata, verification checklists, purpose-driven bundles. |
| 3.0.5-A/B/C/D/E/F | Admin Dashboard | Terminal-1 | 20:30 | Streamlit pages/5_admin.py. System overview, belief browser, constraint viewer, community browser, paper browser. |
| Sprint 3.0 Tests | Tests for new code | Terminal-1 | 20:30 | Created tests/test_sprint_3_0.py (38 tests). All passing. |
| 2.0.5 | Error handling and logging | Terminal-2 | 19:05 | Added pipeline_logging.py with custom exception hierarchy, ErrorCollector, retry mechanism, and pipeline_stage context manager. Enhanced pipeline.py with structured logging, validation error handling, and errors.jsonl output. 32 new tests passing, 1346 total tests passing. |
| 2.0.4 | Test pipeline with sample papers | Terminal-2 | 18:20 | Pipeline tested with minimal bundle. All outputs verified (web_state, manifest, cluster_stats, bn_edges). Fixed entrenchment compat issues. 1442 tests passing. |
| V23.0.0 | Emergent Entrenchment | Terminal-1 | 17:55 | Breaking change committed. 15 files, 8 tests. |
| 2.6.1-7 | P-TC Track A | Terminal-? | Earlier | Task context fields added |
| 2.6.8-14 | P-QW Track B | Terminal-? | Earlier | Quality weighting updated |

---

## Blocked Tasks

| Task ID | Description | Blocked By | Since |
|---------|-------------|------------|-------|
| — | — | — | — |

---

## Rules

1. **One task per terminal** at a time (focus)
2. **Claim before work** — no silent starts
3. **Update on completion** — don't leave stale claims
4. **Check dependencies** — don't start blocked tasks
5. **Communicate blockers** — update Blocked section if stuck

---

## Terminal Identification

Terminals should self-identify using a consistent ID pattern:
- `Terminal-1`, `Terminal-2`, etc. (simple)
- `CLAUDE-{timestamp}` (unique per session)
- Or use the session ID from the transcript path

---

*Last coordination check: 2026-02-09 12:00*
