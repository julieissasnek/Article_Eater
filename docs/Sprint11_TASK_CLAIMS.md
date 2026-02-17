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
| 11.1 | Wire real computations into orchestrator | DONE | Codex | 2026-02-17 20:13 CET | 2026-02-17 20:21 CET | none |
| 11.2 | Wire interaction adjustments | DONE | Codex | 2026-02-17 17:08 UTC | 2026-02-17 17:09 UTC | none |
| 11.3 | Wire lifespan moderation | DONE | Codex | 2026-02-17 17:10 UTC | 2026-02-17 17:11 UTC | none |
| 11.4 | Feature-to-template input mapping | DONE | Codex | 2026-02-17 17:11 UTC | 2026-02-17 17:12 UTC | none |

## ROUND 2 — VALIDATE + BEGIN PAPER EVAL

| Task | Description | Status | Agent | Claimed | Done | Dependency |
|------|------------|--------|-------|---------|------|------------|
| 11.5 | Re-run all worked examples | DONE | Codex | 2026-02-17 20:23 CET | 2026-02-17 20:27 CET | 11.1 DONE |
| 11.6 | Paper claim extraction module | DONE | Codex | 2026-02-17 17:15 UTC | 2026-02-17 17:15 UTC | 11.1 DONE |
| 11.7 | Template matching module | DONE | Codex | 2026-02-17 17:12 UTC | 2026-02-17 17:13 UTC | none |
| 11.8 | Mechanism tracing module | DONE | Codex | 2026-02-17 17:13 UTC | 2026-02-17 17:13 UTC | 11.7 DONE |
| 11.9 | Convergence and composition modules | DONE | Codex | 2026-02-17 17:14 UTC | 2026-02-17 17:14 UTC | 11.8 DONE |
| 11.10 | Paper evaluation orchestrator | DONE | Codex | 2026-02-17 16:50 UTC | 2026-02-17 17:08 UTC | 11.6 + 11.7 + 11.8 + 11.9 DONE |

## ROUND 3 — WORKED EXAMPLES + HARDENING

| Task | Description | Status | Agent | Claimed | Done | Dependency |
|------|------------|--------|-------|---------|------|------------|
| 11.11 | Ulrich 1984 paper evaluation | DONE | Codex | 2026-02-17 17:15 UTC | 2026-02-17 17:25 UTC | 11.10 DONE |
| 11.12 | Paper report generator | DONE | Codex | 2026-02-17 17:16 UTC | 2026-02-17 17:16 UTC | 11.10 DONE |
| 11.13 | Building eval regression suite | DONE | Codex | 2026-02-17 17:16 UTC | 2026-02-17 17:18 UTC | 11.5 DONE |
| 11.14 | Paper eval contradicting study | DONE | Codex | 2026-02-17 17:18 UTC | 2026-02-17 17:18 UTC | 11.10 DONE |
| 11.15 | Paper eval novel finding (gap) | DONE | Codex | 2026-02-17 17:19 UTC | 2026-02-17 17:19 UTC | 11.10 DONE |
| 11.16 | CLI for paper evaluation | DONE | Codex | 2026-02-17 17:20 UTC | 2026-02-17 17:20 UTC | 11.10 DONE |
| 11.17 | Cross-pipeline integration test | DONE | Codex | 2026-02-17 17:21 UTC | 2026-02-17 20:39 CET | 11.5 + 11.10 DONE |
| 11.18 | Paper eval validation sweep | CLAIMED | Codex | 2026-02-17 20:40 CET | — | 11.10 + 11.11 DONE |
| 11.19 | Batch 2 paper claims library | DONE | Codex | 2026-02-17 17:49 UTC | 2026-02-17 17:51 UTC | 11.10 DONE |
| 11.20 | VOI scoring module | DONE | Codex | 2026-02-17 17:26 UTC | 2026-02-17 17:27 UTC | 11.10 DONE |

## ROUND 3 CONTINUED — GLOBAL INTEGRATION TESTS

| Task | Description | Status | Agent | Claimed | Done | Dependency |
|------|------------|--------|-------|---------|------|------------|
| 11.21 | Input sensitivity sweep | DONE | CC-Opus | 2026-02-17 20:15 CET | 2026-02-17 20:50 CET | 11.1 DONE |
| 11.22 | Function signature audit | DONE | CC-Opus | 2026-02-17 20:55 CET | 2026-02-17 21:05 CET | 11.1 DONE |
| 11.23 | Web of belief integration test | DONE | Antigravity | 2026-02-17 19:15 CET | — | 11.10 DONE |
| 11.24 | VOI end-to-end verification | DONE | Codex | 2026-02-17 17:52 UTC | 2026-02-17 17:54 UTC | 11.20 DONE |
| 11.25 | Bayesian network health check | CLAIMED | CC-Opus | 2026-02-17 21:55 CET | — | none |
| 11.26 | Argument structure tracing | AVAILABLE | — | — | — | 11.1 + 11.10 DONE |
| 11.27 | Template-theory data dependency test | CLAIMED | Antigravity | 2026-02-17 19:30 CET | — | 11.23 DONE |
| 11.28 | Enum and schema drift check | DONE | CC-Opus | 2026-02-17 21:40 CET | 2026-02-17 21:50 CET | none |
| 11.29 | No-placeholder audit | DONE | CC-Opus | 2026-02-17 21:25 CET | 2026-02-17 21:35 CET | 11.1 DONE |
| 11.30 | Completeness inventory | DONE | CC-Opus | 2026-02-17 21:10 CET | 2026-02-17 21:20 CET | 11.22 DONE |
| 11.31 | Sprint verification test suite (Part 1) | DONE | Codex | 2026-02-17 17:09 UTC | 2026-02-17 17:34 UTC | 11.1 DONE |
| 11.32 | Building eval provenance tests (Part 2a) | DONE | Codex | 2026-02-17 17:28 UTC | 2026-02-17 17:30 UTC | 11.1 DONE |
| 11.33 | Paper eval provenance tests (Part 2b) | DONE | Codex | 2026-02-17 17:30 UTC | 2026-02-17 17:32 UTC | 11.10 DONE |

---

*Last updated: 2026-02-17 17:54 UTC by Codex (11.24 completed)*
