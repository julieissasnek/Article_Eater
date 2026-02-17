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
| 11.1 | Wire real computations into orchestrator | CLAIMED | Codex | 2026-02-17 20:13 CET | — | none |
| 11.2 | Wire interaction adjustments | AVAILABLE | — | — | — | none |
| 11.3 | Wire lifespan moderation | AVAILABLE | — | — | — | none |
| 11.4 | Feature-to-template input mapping | AVAILABLE | — | — | — | none |

## ROUND 2 — VALIDATE + BEGIN PAPER EVAL

| Task | Description | Status | Agent | Claimed | Done | Dependency |
|------|------------|--------|-------|---------|------|------------|
| 11.5 | Re-run all worked examples | AVAILABLE | — | — | — | 11.1 DONE |
| 11.6 | Paper claim extraction module | AVAILABLE | — | — | — | 11.1 DONE |
| 11.7 | Template matching module | AVAILABLE | — | — | — | none |
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

## ROUND 3 CONTINUED — GLOBAL INTEGRATION TESTS

| Task | Description | Status | Agent | Claimed | Done | Dependency |
|------|------------|--------|-------|---------|------|------------|
| 11.21 | Input sensitivity sweep | AVAILABLE | — | — | — | 11.1 DONE |
| 11.22 | Function signature audit | AVAILABLE | — | — | — | 11.1 DONE |
| 11.23 | Web of belief integration test | AVAILABLE | — | — | — | 11.10 DONE |
| 11.24 | VOI end-to-end verification | AVAILABLE | — | — | — | 11.20 DONE |
| 11.25 | Bayesian network health check | AVAILABLE | — | — | — | none |
| 11.26 | Argument structure tracing | AVAILABLE | — | — | — | 11.1 + 11.10 DONE |
| 11.27 | Template-theory data dependency test | AVAILABLE | — | — | — | 11.23 DONE |
| 11.28 | Enum and schema drift check | AVAILABLE | — | — | — | none |
| 11.29 | No-placeholder audit | AVAILABLE | — | — | — | 11.1 DONE |
| 11.30 | Completeness inventory | AVAILABLE | — | — | — | 11.22 DONE |
| 11.31 | Sprint verification test suite (Part 1) | AVAILABLE | — | — | — | 11.1 DONE |
| 11.32 | Building eval provenance tests (Part 2a) | AVAILABLE | — | — | — | 11.1 DONE |
| 11.33 | Paper eval provenance tests (Part 2b) | AVAILABLE | — | — | — | 11.10 DONE |

---

*Last updated: 2026-02-17 by Codex (Task 11.1 claimed after board refresh)*
