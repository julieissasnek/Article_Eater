# PARALLEL_WORK.md

*Last updated: Tuesday, February 11, 2026*

This file coordinates parallel Claude Code sessions to prevent conflicts.

---

## How This Works

1. **Before starting work**: Check this file, claim your lane
2. **Claim a lane**: Edit the "Active Claims" section with your session ID
3. **Respect file ownership**: Only edit files in your lane
4. **Release when done**: Clear your claim when finished

---

## MVP Integration Work Lanes (Priority)

### Lane MVP-0: Contracts & Schemas
**Scope**: Define JSON schemas for MVP interfaces
**Owner**: UNCLAIMED
**Parallelizable with**: MVP-1, MVP-GUI (all independent)
**Files OWNED (exclusive write access)**:
- `contracts/ae_af/schemas/query_request.v1.schema.json` — NEW
- `contracts/ae_af/schemas/query_response.v1.schema.json` — NEW
- `contracts/ae_af/schemas/gap_report.v1.schema.json` — NEW
- `docs/MVP_CONTRACTS.md` — NEW

**Tasks**:
- [ ] Verify `af_paper.v1.json` exists and is correct
- [ ] Verify `ae_rule.v1.json` exists and is correct
- [ ] Define `query_request.v1.json` schema
- [ ] Define `query_response.v1.json` schema
- [ ] Define `gap_report.v1.json` schema

---

### Lane MVP-1: Persistent Web State
**Scope**: Implement save/load for accumulated web across runs
**Owner**: UNCLAIMED
**Parallelizable with**: MVP-0, MVP-GUI (all independent)
**Depends on**: None (can start immediately)
**Files OWNED (exclusive write access)**:
- `data/accumulated_web.json` — NEW (persistent state file)
- `data/events.jsonl` — NEW (event log)
- `src/services/web_accumulator.py` — NEW
- `tests/test_web_accumulator.py` — NEW

**Files SHARED (read-only)**:
- `src/services/web_persistence.py` — Reference existing logic
- `src/services/web_of_belief.py` — Reference WebOfBelief class

**Tasks**:
- [ ] Create `WebAccumulator` class with load/save methods
- [ ] Implement event sourcing (append-only events.jsonl)
- [ ] Implement merge logic for combining per-run web_state with accumulated
- [ ] Test: save web → restart → load → verify state intact

---

### Lane MVP-2: Batch Processing Script
**Scope**: Create script to process N papers end-to-end
**Owner**: UNCLAIMED
**Parallelizable with**: MVP-GUI (independent)
**Depends on**: MVP-1 (needs accumulator for persistence)
**Files OWNED (exclusive write access)**:
- `scripts/process_papers.py` — NEW (main batch script)
- `scripts/process_config.yaml` — NEW (configuration)
- `tests/test_batch_processing.py` — NEW

**Files SHARED (read-only)**:
- `app/tasks/pipeline.py` — Call existing extraction
- `src/services/web_accumulator.py` — Use for persistence (from MVP-1)

**Files SHARED (coordinate changes)**:
- Article Finder: `eater_interface/invoker.py` — May need minor updates

**Tasks**:
- [ ] Create batch processor that iterates over paper list
- [ ] Wire: AF query → job bundle → AE extraction → web accumulation
- [ ] Add progress tracking (papers processed, rules extracted, beliefs added)
- [ ] Implement circuit breaker (skip after 3 failures)
- [ ] Process 100 test papers end-to-end

---

### Lane MVP-3: Query Engine
**Scope**: Build query interface for asking questions of the web
**Owner**: UNCLAIMED
**Parallelizable with**: MVP-GUI (can coordinate on interface)
**Depends on**: MVP-1 (needs persistent web to query)
**Files OWNED (exclusive write access)**:
- `src/services/query_engine.py` — NEW
- `src/cli/query.py` — NEW (CLI entry point)
- `tests/test_query_engine.py` — NEW

**Files SHARED (read-only)**:
- `src/services/web_of_belief.py` — Use WebOfBelief queries
- `src/services/voi_search.py` — Use for gap identification
- `src/services/web_accumulator.py` — Load persistent web (from MVP-1)

**Tasks**:
- [ ] Create `QueryEngine` class with `query(question) -> QueryResult`
- [ ] Implement `identify_gaps() -> GapReport`
- [ ] Parse natural language questions to belief queries
- [ ] Return beliefs with confidence scores and source citations
- [ ] CLI: `python -m src.cli.query "What affects attention?"`

---

### Lane MVP-GUI: Streamlit Interface
**Scope**: Build minimal GUI for demo
**Owner**: UNCLAIMED
**Parallelizable with**: MVP-0, MVP-1 (all independent until integration)
**Depends on**: MVP-3 for query integration (but can build UI scaffolding first)
**Files OWNED (exclusive write access)**:
- `streamlit_app/mvp/` — NEW directory
- `streamlit_app/mvp/app.py` — NEW (main app)
- `streamlit_app/mvp/pages/1_status.py` — NEW
- `streamlit_app/mvp/pages/2_query.py` — NEW
- `streamlit_app/mvp/pages/3_gaps.py` — NEW

**Files SHARED (read-only)**:
- `src/services/query_engine.py` — Call for queries (from MVP-3)
- `src/services/web_accumulator.py` — Get status (from MVP-1)

**Tasks**:
- [ ] Create Streamlit app structure (3 pages)
- [ ] Status page: papers processed, rules, beliefs counts
- [ ] Query page: text input, results with confidence bars
- [ ] Gaps page: coverage heatmap, suggested searches

---

### Lane MVP-5: Polish & Demo
**Scope**: Error handling, logging, demo script
**Owner**: UNCLAIMED
**Parallelizable with**: None (final integration)
**Depends on**: MVP-1, MVP-2, MVP-3, MVP-GUI (all must be functional)
**Files OWNED (exclusive write access)**:
- `docs/DEMO_SCRIPT.md` — NEW
- `docs/MVP_USER_GUIDE.md` — NEW
- Various files for error handling improvements

**Tasks**:
- [ ] Add timeouts on LLM calls
- [ ] Add circuit breakers
- [ ] Comprehensive logging
- [ ] Write 10-minute demo script
- [ ] Documentation for demo

---

## Parallel Execution Plan

### Phase A: Foundation (Can all run in parallel)
```
┌─────────────────────────────────────────────────────────┐
│                   PARALLEL PHASE A                       │
├─────────────────┬─────────────────┬─────────────────────┤
│   Lane MVP-0    │   Lane MVP-1    │    Lane MVP-GUI     │
│   (Contracts)   │  (Persistence)  │   (UI Scaffolding)  │
│                 │                 │                      │
│  • Schemas      │  • Accumulator  │  • App structure    │
│  • Verify       │  • Events log   │  • Page layouts     │
│    existing     │  • Merge logic  │  • Mock data        │
└─────────────────┴─────────────────┴─────────────────────┘
         │                 │                   │
         └────────────────┬┴───────────────────┘
                          │
                          ▼
```

### Phase B: Processing (Sequential after MVP-1)
```
┌─────────────────────────────────────────────────────────┐
│                   PHASE B (after MVP-1)                  │
├─────────────────────────┬───────────────────────────────┤
│      Lane MVP-2         │         Lane MVP-3            │
│   (Batch Processing)    │       (Query Engine)          │
│                         │                               │
│  Depends on: MVP-1      │    Depends on: MVP-1          │
│  • Batch script         │    • Query parser             │
│  • AF→AE wiring         │    • Gap identification       │
│  • Progress tracking    │    • CLI interface            │
└─────────────────────────┴───────────────────────────────┘
         │                           │
         └───────────┬───────────────┘
                     │
                     ▼
```

### Phase C: Integration & Polish (After B)
```
┌─────────────────────────────────────────────────────────┐
│              PHASE C (after MVP-2, MVP-3)               │
├─────────────────────────────────────────────────────────┤
│                    Lane MVP-GUI                          │
│              (Wire to real backends)                     │
│                                                          │
│  • Connect Status to WebAccumulator                      │
│  • Connect Query to QueryEngine                          │
│  • Connect Gaps to VOI search                            │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Lane MVP-5                            │
│                  (Polish & Demo)                         │
└─────────────────────────────────────────────────────────┘
```

---

## What YOU (David) Can Do In Parallel

While Claude works on one lane, you can:

### Independent Work (No Coordination Needed)
1. **Test paper selection**: Pick 100 on-topic papers from AF for batch processing test
2. **Demo scenario design**: Write the questions you want to demonstrate
3. **Foundational book abstracts**: Continue adding extended_notes to HBE books
4. **Zotero organization**: Continue HBE bibliography cleanup

### Coordination Work (Check with Claude first)
1. **Schema review**: Review contracts as MVP-0 produces them
2. **UI feedback**: Review Streamlit pages as MVP-GUI produces them
3. **Test queries**: Try queries against QueryEngine once MVP-3 is ready

---

## Terminal Assignments (Pre-Allocated)

Each terminal maintains context from related work. Start terminals in order shown.

### Terminal 1: Data & Processing Track
**Focus**: Backend persistence and batch processing
**Order**: MVP-1 → MVP-2
**Why**: MVP-2 uses the accumulator built in MVP-1; context carries forward

| Step | Lane | Description | Depends On |
|------|------|-------------|------------|
| 1.1 | MVP-1 | Persistent Web State (accumulator, events) | None - START HERE |
| 1.2 | MVP-2 | Batch Processing Script | MVP-1 complete |

### Terminal 2: Contracts & Query Track
**Focus**: Schemas and query engine
**Order**: MVP-0 → MVP-3
**Why**: MVP-0 defines schemas that MVP-3 implements; context carries forward

| Step | Lane | Description | Depends On |
|------|------|-------------|------------|
| 2.1 | MVP-0 | Contracts & Schemas | None - START HERE |
| 2.2 | MVP-3 | Query Engine | MVP-0 + MVP-1 complete |

### Terminal 3: UI & Demo Track
**Focus**: User interface and final polish
**Order**: MVP-GUI → MVP-5
**Why**: MVP-GUI scaffolding informs MVP-5 demo script; context carries forward

| Step | Lane | Description | Depends On |
|------|------|-------------|------------|
| 3.1 | MVP-GUI | Streamlit Interface (scaffolding first) | None - START HERE |
| 3.2 | MVP-GUI | Streamlit Integration (wire backends) | MVP-1, MVP-3 complete |
| 3.3 | MVP-5 | Polish & Demo Script | All lanes complete |

---

## Execution Timeline

```
TIME ──────────────────────────────────────────────────────────────────────────>

TERMINAL 1 (Data):
├─────────────────────────┼─────────────────────────────┼
│      MVP-1              │          MVP-2              │  DONE
│  (Persistence ~3hr)     │   (Batch Processing ~4hr)   │
└─────────────────────────┴─────────────────────────────┘
                          ↑
                    MVP-1 must finish

TERMINAL 2 (Query):
├─────────────────────────┼───────────────────────────────────────┼
│      MVP-0              │              MVP-3                    │  DONE
│   (Contracts ~2hr)      │        (Query Engine ~4hr)            │
└─────────────────────────┴───────────────────────────────────────┘
                          ↑
                    MVP-0 + MVP-1 must finish

TERMINAL 3 (UI):
├─────────────────────────┼───────────────────────────────┼───────────────┼
│    MVP-GUI scaffold     │    MVP-GUI integration        │    MVP-5      │ DONE
│     (mock data ~2hr)    │    (wire backends ~2hr)       │  (polish ~2hr)│
└─────────────────────────┴───────────────────────────────┴───────────────┘
                                      ↑                           ↑
                              MVP-1 + MVP-3 must finish     ALL must finish
```

---

## Quick Start Commands

### To Start Terminal 1 (Data Track):
```
Say: "Start MVP-1: Persistent Web State. This is Terminal 1 of the Data Track."
```

### To Start Terminal 2 (Query Track):
```
Say: "Start MVP-0: Contracts & Schemas. This is Terminal 2 of the Query Track."
```

### To Start Terminal 3 (UI Track):
```
Say: "Start MVP-GUI scaffolding with mock data. This is Terminal 3 of the UI Track."
```

---

## Active Claims

**IMPORTANT**: Edit this section to claim/release lanes.

| Lane | Terminal | Session ID | Claimed At | Status | Notes |
|------|----------|------------|------------|--------|-------|
| MVP-0 | T2 | TERMINAL-2 | 2026-02-11 | ✓ COMPLETE | 3 schemas + docs |
| MVP-1 | T1 | MAIN-TERMINAL | 2026-02-11 | ✓ COMPLETE | 10 tests pass |
| MVP-2 | T1 | MAIN-TERMINAL | 2026-02-11 | ✓ COMPLETE | 14 tests pass |
| MVP-3 | T2 | TERMINAL-2 | 2026-02-11 | IN PROGRESS | Query Engine |
| MVP-GUI | T1 | MAIN-TERMINAL | 2026-02-11 | IN PROGRESS | UI scaffold |
| MVP-5 | T3 | UNCLAIMED | — | BLOCKED | Needs all lanes |

---

## Completed Lanes (Previous Work)

| Lane | Description | Completed | Outcome |
|------|-------------|-----------|---------|
| A | Sprint 2.5 Schema Design | 2026-02-08 | P-SE panel consulted |
| B | Sprint 2.5 Implementation | 2026-02-08 | social_epistemology.py (~1300 lines) |
| C | TODO 1 Credibility Testing | 2026-02-08 | Feedback module, semantic coherence |
| D | TODO 2 Interpretive Intelligence | 2026-02-08 | MECHANISM + DISAGREEMENT patterns |
| E | TODO 3 VOI-Driven Search | 2026-02-08 | Cross-field vocabulary, 92 tests |
| F | P-TC and P-QW panels | 2026-02-08 | Panel consultations complete |
| G | Fixed failing tests | 2026-02-08 | 11 tests fixed |

---

## File Ownership Matrix (MVP)

| File | MVP-0 | MVP-1 | MVP-2 | MVP-3 | MVP-GUI | MVP-5 |
|------|-------|-------|-------|-------|---------|-------|
| `contracts/ae_af/schemas/*.json` | **WRITE** | read | read | read | read | read |
| `data/accumulated_web.json` | — | **WRITE** | read | read | read | read |
| `data/events.jsonl` | — | **WRITE** | write | read | read | read |
| `src/services/web_accumulator.py` | — | **WRITE** | read | read | read | read |
| `scripts/process_papers.py` | — | — | **WRITE** | — | — | read |
| `src/services/query_engine.py` | — | — | — | **WRITE** | read | read |
| `src/cli/query.py` | — | — | — | **WRITE** | — | read |
| `streamlit_app/mvp/*` | — | — | — | read | **WRITE** | read |
| `docs/DEMO_SCRIPT.md` | — | — | — | — | — | **WRITE** |

Legend: **WRITE** = exclusive, read = read-only, — = no access needed

---

## Quick Start for New Terminal

```bash
# 1. Check what's claimed
cat PARALLEL_WORK.md | grep -A 10 "Active Claims"

# 2. Pick an unclaimed lane from Phase A (MVP-0, MVP-1, or MVP-GUI)

# 3. Edit this file to claim it:
# | MVP-X | CLAUDE-$(date +%s) | $(date) | ~N hours | Working on X |

# 4. Start work on that lane's tasks

# 5. When done, update ACTIVE_TASKS.md and clear your claim here
```

---

## Conflict Resolution

If two sessions need the same file:

1. **Check this file first** — see who has the claim
2. **Coordinate via ACTIVE_TASKS.md** — leave a note
3. **Serialize if necessary** — one finishes, then the other starts
4. **Create interface files** — if extending, add a new file that imports from shared

---

*Created: February 8, 2026*
*Updated: February 11, 2026 (MVP Integration Lanes)*
