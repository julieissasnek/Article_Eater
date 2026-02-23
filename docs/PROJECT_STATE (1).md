# CMR PROJECT — COORDINATION PROTOCOL
## Location: docs/PROJECT_STATE.md
## Rule: Read before work. Claim before starting. Update after completing.
## Last updated: 2026-02-22 23:00 — HUMAN + OPUS/CHAT

---

# SECTION 1: CURRENT PHASE

```
CURRENT PHASE: 2 — STRUCTURAL REPAIR
MULTI-I complete. Cowork halted. CC and AG doing foundation work.
Critical path: E-01 → M-01 → E-02 → TJ-01 → TJ-07 → Cowork resumes.
```

| Phase | Status |
|-------|--------|
| 1 AUDIT | **COMPLETE** — 4 auditors, cross-validated, triage done |
| 2 STRUCTURAL REPAIR | **IN PROGRESS** — schema, variables, ceilings, governance |
| 3 TOULMIN FOUNDATION | BLOCKED by E-01 + M-01 |
| 4 PANEL PIPELINE RESUMES | BLOCKED by Phase 3 |
| 4b MULTI-I | **COMPLETE** — 9 templates + 9 Toulmin appendices |
| 5 RETRO TOULMIN | PARALLEL-OK with Phase 4 |
| 6 AE INTEGRATION | BLOCKED by Phase 5 |

---

# SECTION 2: TASK BOARD

## COMPLETED

| Task | By | Key Output |
|------|----|-----------|
| A-01 Audit | Codex | 20-checkpoint report, 62 ceiling violations, 184 template count, 15 test failures, multi-DB finding |
| A-02 Audit | AG/Opus | 115+ unique keys, JSON schema analysis, CC error corrections |
| A-03 Audit | Gemini 1.5 Pro | CROSSCUT-I context collapse, NEUROMOD-I math gap, 314 variables |
| A-04 Triage | OPUS/CHAT | CMR_SYSTEM_HEALTH_REPORT_Feb22_FINAL.md |
| R-01a-d | CC | IE_DPT fix, Panel_Implicit fix, TRANSFER update, Sprint Brief update |
| R-04 | CC | 11 SOCIAL-I JSONs extracted |
| R-05 | CC | gap_tracker confirmed working (but uses legacy schema) |
| R-06a | CC | CSV→DB loader |
| R-06b | AG | Belief seeder (22/22 tests) |
| R-06c | AG | Theory Agent Profiles T7.6 (73/73 tests) |
| R-07 | HUMAN | 172,091 findings loaded |
| R-08 | HUMAN | 34 beliefs + 50 constraints |
| P-03 | OPUS/CHAT | MULTI-I pre-panel clearance |
| P-03b | COWORK | MULTI-I panel output: 1,647 lines, 9 templates, 9 Toulmin appendices, 30 refs |
| P-03c | pending | MULTI-I post-review — HUMAN + OPUS/CHAT to review |

## ENFORCEMENT (Layer 1 — prevent future drift)

| Task | Description | Lane | Status | Priority |
|------|-------------|------|--------|----------|
| **E-01** | **Canonical JSON schema + validator** | CC | **AVAILABLE — HIGHEST** | P0 |
| **E-02** | **Bridge warrant ceiling lint** | CC | BLOCKED by E-01 | P0 |
| **E-03a** | **Canonical variable ontology** | AG | **AVAILABLE — HIGHEST** | P0 |
| E-03b | Variable lint script | CC | BLOCKED by E-03a | P1 |
| E-04 | Template count reconciliation command | CC | AVAILABLE (parallel) | P2 |
| E-05 | Panel output extraction standard | CC | Part of TJ-07 | P2 |

## REMEDIATION (Layer 2 — fix existing corpus)

| Task | Description | Lane | Status | Priority |
|------|-------------|------|--------|----------|
| **M-01** | **Schema migration (184 templates)** | CC | BLOCKED by E-01 | P0 |
| **M-02a** | **Ceiling violation report** | CC | BLOCKED by E-02 | P0 |
| **M-02b** | **Ceiling violation adjudication** | HUMAN | BLOCKED by M-02a | P0 |
| **M-03a** | **Variable migration script** | AG | BLOCKED by E-03a | P1 |
| M-03b | Variable migration execution | CC | BLOCKED by M-01 + M-03a | P1 |
| M-04 | Gap tracker rewrite (legacy→current schema) | CC | BLOCKED by M-01 | P1 |
| **M-05** | **DB consolidation (which DB is canonical?)** | HUMAN decision + CC/AG | **DECISION NEEDED** | P1 |
| **M-06** | **Extra warrant types (ratify or remove?)** | HUMAN decision + CC | **DECISION NEEDED** | P2 |
| M-07 | Test suite fix (15 failures) | CC | BLOCKED by M-01 | P2 |

## GOVERNANCE (Layer 3 — self-describing system)

| Task | Description | Lane | Status | Priority |
|------|-------------|------|--------|----------|
| **G-01** | **Document lifecycle (479→~40 current)** | AG | **AVAILABLE** (parallel) | P1 |
| G-02 | PROJECT_STATE.md maintenance | all | ONGOING | — |
| **G-03** | **Sprint Brief consolidation** | CC | **AVAILABLE** (quick) | P1 |
| G-04 | Orphan cross-template target resolution | HUMAN | AVAILABLE | P2 |
| G-05 | Template ID crosswalk (T#/series/canonical) | CC | Part of M-01 | P2 |

## REMAINING REMEDIATION (from earlier — still needed)

| Task | Description | Lane | Status |
|------|-------------|------|--------|
| R-09 | Extract MEMORY-I JSONs (10 templates) | CC | AVAILABLE |
| R-10 | Update TRANSFER doc (34→53 after MEMORY-I + MULTI-I) | CC | AVAILABLE |
| R-11 | Sprint Brief S-02 cleared | CC | AVAILABLE |
| R-12 | Sprint Brief S-03 cleared | CC | AVAILABLE |
| A-06 | NEUROMOD-I PE note → S-07 | any | AVAILABLE |
| R-13 | Mark CLAUDE.md SUPERSEDED | any | AVAILABLE |

## TOULMIN FOUNDATION (Phase 3 — after structural repair)

| Task | Description | Lane | Status |
|------|-------------|------|--------|
| TJ-01 | Toulmin schema extension (on canonical base) | CC | BLOCKED by M-01 |
| TJ-02 | Toulmin validation tooling | CC | BLOCKED by TJ-01 |
| TJ-07 | Forward integration (panel prompt + exemplar + E-05) | CC/AG | BLOCKED by TJ-01 |

## FUTURE (known requirements, not yet scheduled)

| Task | When | Lane | Details |
|------|------|------|---------|
| P-03c MULTI-I post-review | NOW | HUMAN + OPUS/CHAT | Review MULTI_I_Panel_Output.md + REVIEW_MULTI_I_post.md |
| MUSIC-I (P-04) | After TJ-07 | COWORK | First Toulmin-native panel |
| CROSSCUT-I synthesis script | Before S-08 | CC/AG | Extract flags into <10KB summary |
| Allostatic integration spec | Before S-07 | HUMAN | Math for ALLOSTATIC_MASTER_001 |
| TJ-03-06 Retro Toulmin | After TJ-02 | CC/AG | VISUAL, SPATIAL, LIGHT, STRESS |
| TJ-08 AE integration | After TJ-03-06 | CC | |

---

# SECTION 3: DEPENDENCY MAP

```
CC TRACK:                          AG TRACK:
E-01 (schema)                      E-03a (variable ontology)
  |                                   |
  v                                   v
M-01 (migration) ←─────────────── M-03a (migration script)
  |                                   |
  v                                   v
E-02 (ceiling lint)               M-03b (variable migration)
  |                                [runs after M-01]
  v
M-02a (ceiling report)            G-01 (document lifecycle)
  |                                [parallel, non-blocking]
  v
HUMAN: M-02b (adjudicate ceilings), M-05 (DB), M-06 (warrants)
  |
  v
M-04 (gap tracker rewrite)
  |
  v
TJ-01 → TJ-02 → TJ-07
  |
  v
COWORK RESUMES (MUSIC-I onward, with enforcement)
```

---

# SECTION 4: HUMAN DECISIONS NEEDED

| Decision | Options | Impact |
|----------|---------|--------|
| **M-05: Canonical DB** | (a) web_persistence.db (12,668 beliefs) or (b) web_persistence_v2.db (140 beliefs, clean) | All WoB queries use one DB |
| **M-06: Extra warrant types** | (a) Ratify EPISTEMIC_COHERENCE, ARGUMENTATIVE, EPISTEMIC_VIGILANCE with ceiling priors, or (b) remove from code | Spec-code alignment |
| **M-02b: Ceiling violations** | Per-violation: reduce confidence or upgrade warrant | 62 decisions (can batch by pattern) |
| **G-04: Orphan targets** | Map SC-III, VF-III, SPATIAL-II, etc. to current panels or declare dead | CROSSCUT-I scope |
| **Allostatic integration** | Weighted sum, worst-of-N, threshold model, or other | NEUROMOD-I math |

---

# SECTION 5: CHANGELOG

| When | Who | What |
|------|-----|------|
| 23:00 | OPUS/CHAT | PROJECT_STATE FINAL — four auditors fully read, strategic plan |
| 22:00 | OPUS/CHAT | Health report FINAL — corrected Codex credit, 10 real problems |
| 21:00 | COWORK | MULTI-I complete (9 templates, 9 Toulmin appendices), HALTED |
| 20:30 | HUMAN | PROJECT_STATE v4 |
| — | Codex | A-01 complete (20 checkpoints) |
| — | AG/Opus | A-02 complete + R-06b + R-06c |
| — | Gemini 1.5 | A-03 complete |
| — | CC | R-01a-d, R-04-06a complete |
| — | HUMAN | R-07, R-08 complete |

---

# SECTION 6: INSTRUCTIONS BY SYSTEM

**CC**: Read this file + CMR_SYSTEM_HEALTH_REPORT_Feb22_FINAL.md.
Start E-01 (canonical schema). Then M-01, E-02, M-02a in sequence.
G-03 (brief consolidation) in parallel. R-09 through R-13 when convenient.

**AG**: Read this file + Health Report. Start E-03a (variable ontology)
using the Codex variable inventory CSV. G-01 (document lifecycle) in
parallel. M-03a (migration script) after E-03a.

**COWORK**: HALTED. Do not proceed until this file shows Phase 4 ACTIVE.

**HUMAN**: Review MULTI-I output (P-03c). Make decisions: M-05 (DB),
M-06 (warrants), G-04 (orphan targets). Adjudicate ceiling violations
when M-02a report arrives. Specify allostatic math before S-07.

---

*PROJECT_STATE.md — Read before doing anything. Update after doing anything.*
