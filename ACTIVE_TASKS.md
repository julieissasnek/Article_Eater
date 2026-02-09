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
| DISC-3 | Add search execution logging | Terminal-1 | 21:00 | IN_PROGRESS | Article Finder integration |

---

## Available Tasks (Not Claimed)

### High Priority (Infrastructure)
| Task ID | Description | Priority | Dependencies |
|---------|-------------|----------|--------------|
| DISC-3 | Add search execution logging to Article Finder | P1 | DISC-2 ✓ |
| ENT-6 | Replay DB strategy (safe runner) | P1 | ENT-1-5 ✓ |

### Sprint 3.0 Extensions (P2/P3)
| Task ID | Description | Priority | Dependencies |
|---------|-------------|----------|--------------|
| — | All Sprint 3.0 P2 tasks complete | — | — |

---

## Completed Today (2026-02-09)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| 3.0.2-G | Alerting/monitoring capability | Terminal-5 | 23:30 | query_alerts.py (~1400 lines), 80 tests, panel review |
| 3.0.1-D | Extended API layer (20 endpoints) | Terminal-5 | 22:45 | api_extended.py (~950 lines), 37 tests |
| 3.0.4-E | Purpose-driven export bundles (Munzner) | Terminal-5 | 22:15 | export_bundles.py (~1000 lines), 54 tests |
| 3.0.4-D | BibTeX generator with full metadata | Terminal-5 | 21:45 | bibtex_generator.py (~700 lines), 83 tests |
| DISC-2 | Wire VOI search to emit gaps | Terminal-1 | 20:30 | voi_search.py funnel integration, 4 tests |
| DISC-1 | Discovery funnel schema + service | Terminal-1 | 20:00 | 006_discovery_funnel.sql, discovery_funnel.py (~900 lines), 31 tests |
| 3.0.3-C | Claim network graph component | Terminal-1 | 18:30 | components/network.py (~300 lines), 2_explore.py updated |
| 3.0.3-D | Admin dashboard wired to real data | Terminal-1 | 18:45 | 5_admin.py with WebOfBelief/API integration |
| 3.0.3-E | Network visualization (vis.js) | Terminal-3 | 17:00 | network_service.py (~1000 lines), 44 tests |
| 3.0.3-F | GraphML/GEXF/DOT export | Terminal-1 | 19:15 | graph_export.py (~1100 lines) |
| 3.0.3-G | Community network visualization | Terminal-1 | 19:20 | 3_communities.py network tab |
| 3.0.3-H | Interactive HTML export | Terminal-1 | 19:30 | graph_export.py to_html() method |
| 3.0.4-F | Report generation (PDF/Markdown) | Terminal-3 | 17:00 | report_generator.py (~958 lines), 46 tests |
| 3.0.5-G | Export audit trail | Terminal-3 | 17:00 | export_audit.py (~650 lines), 34 tests |
| ENT-1-5 | Entrenchment historical replay | Terminal-3 | 17:00 | entrenchment_replay.py, API routes, monitor UI, 16 tests |
| 3.0.2-C | Scope-aware output generation | Terminal-3 | 13:15 | scope_renderer.py (~550 lines), 31 tests |
| 3.0.2-E | LLM integration - WebOfBelief integration | Terminal-4 | 13:30 | llm_query_bridge.py enhancements, 34 tests |
| 3.0.2-F | RELATED, TRENDING, CANONICAL patterns | Terminal-3 | 14:00 | Bates berrypicking extensions, 48 tests |
| 3.0.4-A | Evidence summary generator | Terminal-3 | 14:30 | evidence_summarizer.py (~600 lines), 35 tests |
| 3.0.4-B | Pipeline-friendly formats | Terminal-3 | 14:45 | export_formats.py (~650 lines), 38 tests |
| 3.0.4-C | Verification checklists | Terminal-3 | 15:00 | export_checklists.py (~650 lines), 37 tests |
| SCHEMA-1/2/3 | V2 schemas + extraction templates | Terminal-3 | 09:45 | ae.rule.v2, ae.claim.v2, argument_schemes.json |
| EXT-1-16 | All 16 extraction templates | Terminal-3 | 12:45 | Complete coverage for all article types |
| BIB-1-7 | BibTeX integration | Terminal-2 | Earlier | bibtex_utils.py, ingestion, Streamlit page |

---

## Completed (2026-02-08)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
| V23.0.0 | Emergent Entrenchment | Terminal-1 | 17:55 | Breaking change committed |
| 3.0-PLAN | Sprint 3.0 Planning | Terminal-1 | 20:30 | 21 expert panel consultation |
| 3.0.1-A/B/C | Unified API (Core 7 endpoints) | Terminal-1 | 20:30 | api_unified.py (~700 lines) |
| 3.0.2-A/B/D | Query Engine + Progressive Disclosure | Terminal-1 | 20:30 | query_parser.py, query_response.py |
| 3.0.3-A/B | Streamlit Interface Core | Terminal-1 | 20:30 | streamlit_app/ (~2000 lines) |
| 2.0.4/2.0.5 | Pipeline testing + Error handling | Terminal-2 | 19:05 | pipeline_logging.py, 1346 tests |
| TD-A/B/C/D/E | All Technical Debt sprints | Various | Earlier | theory_matcher, scope_extractor, scalable_coherence, temporal_parser, incremental_bn |

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

*Last coordination check: 2026-02-09 23:30*
