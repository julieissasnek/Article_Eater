# SPRINT 11 TASK CLAIMS
## Concurrency control — all agents MUST check and update this file before starting any task

---

## RULES

1. Read this file before starting any task
2. Find the task you want — check it is AVAILABLE
3. If AVAILABLE: change status to CLAIMED, add your agent name and timestamp
4. `git commit` this file IMMEDIATELY before starting work
5. When task is DONE: change status to DONE, add completion timestamp
6. `git commit` this file along with your work
7. If a dependency is listed, verify it shows DONE below before starting
8. If a task shows CLAIMED by another agent, DO NOT take it

---

## ROUND 1 — FIX THE WIRING (CRITICAL)

| Task | Description | Status | Agent | Claimed | Done | Dependency |
|------|------------|--------|-------|---------|------|------------|
| 11.1 | Wire real computations into orchestrator | CLAIMED | Codex | 2026-02-17 16:50 CET | — | none |
| 11.2 | Wire interaction adjustments | DONE | Antigravity | 2026-02-17 16:55 CET | 2026-02-17 17:05 CET | none |
| 11.3 | Wire lifespan moderation | DONE | CC-Opus | 2026-02-17 16:43 CET | 2026-02-17 17:10 CET | none |
| 11.4 | Feature-to-template input mapping | CLAIMED | Codex | 2026-02-17 15:47 UTC | — | none |

## ROUND 2 — VALIDATE + BEGIN PAPER EVAL

| Task | Description | Status | Agent | Claimed | Done | Dependency |
|------|------------|--------|-------|---------|------|------------|
| 11.5 | Re-run all worked examples | AVAILABLE | — | — | — | 11.1 DONE |
| 11.6 | Paper claim extraction module | AVAILABLE | — | — | — | 11.1 DONE |
| 11.7 | Template matching module | CLAIMED | Antigravity | 2026-02-17 17:15 CET | — | none |
| 11.8 | Mechanism tracing module | AVAILABLE | — | — | — | 11.7 DONE |
| 11.9 | Convergence and composition modules | AVAILABLE | — | — | — | 11.8 DONE |
| 11.10 | Paper evaluation orchestrator | AVAILABLE | — | — | — | 11.6 + 11.7 + 11.8 + 11.9 DONE |

## ROUND 3 — WORKED EXAMPLES + HARDENING

| Task | Description | Status | Agent | Claimed | Done | Dependency |
|------|------------|--------|-------|---------|------|------------|
| 11.11 | Ulrich 1984 paper evaluation | AVAILABLE | — | — | — | 11.10 DONE |
| 11.12 | Paper report generator | AVAILABLE | — | — | — | 11.10 DONE |
| 11.13 | Building eval regression suite | AVAILABLE | — | — | — | 11.5 DONE |
| 11.14 | Paper eval contradicting study | AVAILABLE | — | — | — | 11.10 DONE |
| 11.15 | Paper eval novel finding (gap) | AVAILABLE | — | — | — | 11.10 DONE |
| 11.16 | CLI for paper evaluation | AVAILABLE | — | — | — | 11.10 DONE |
| 11.17 | Cross-pipeline integration test | AVAILABLE | — | — | — | 11.5 + 11.10 DONE |
| 11.18 | Paper eval validation sweep | AVAILABLE | — | — | — | 11.10 + 11.11 DONE |
| 11.19 | Batch 2 paper claims library | AVAILABLE | — | — | — | 11.10 DONE |
| 11.20 | VOI scoring module | AVAILABLE | — | — | — | 11.10 DONE |

---

*Last updated: 2026-02-17 by Codex (Task 11.4 claimed)*
