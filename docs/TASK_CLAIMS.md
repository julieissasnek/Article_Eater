# SPRINT 10 TASK CLAIMS
## Concurrency control — all agents MUST check and update this file before starting any task

---

## RULES

1. **git pull** before reading this file
2. Find the task you want — check it is AVAILABLE
3. If AVAILABLE: change status to CLAIMED, add your agent name and timestamp
4. **git commit and push this file IMMEDIATELY** before starting work
5. When task is DONE: change status to DONE, add completion timestamp
6. **git commit and push this file** along with your work
7. **Dependency check**: if a task has a dependency, verify the dependency shows DONE below. If not, pick a different task.
8. If a task shows CLAIMED by another agent, DO NOT take it — pick the next available one

---

## ROUND 1 — FOUNDATION

| Task | Description | Status | Agent | Claimed | Done | Dependency |
|------|------------|--------|-------|---------|------|------------|
| 1.1 | Enum drift fix | AVAILABLE | — | — | — | none |
| 1.2 | Template DB index | AVAILABLE | — | — | — | none |
| 1.3 | Load staging theory-links | AVAILABLE | — | — | — | none |
| 1.4 | WIS conversion module | AVAILABLE | — | — | — | none |

## ROUND 2 — PIPELINE COMPONENTS

| Task | Description | Status | Agent | Claimed | Done | Dependency |
|------|------------|--------|-------|---------|------|------------|
| 2.1 | Template computation functions (Batch 1, 12 templates) | AVAILABLE | — | — | — | 1.2 DONE |
| 2.2 | CMR data models | AVAILABLE | — | — | — | none |
| 2.3 | Interaction matrix module | AVAILABLE | — | — | — | none |
| 2.4 | Building eval orchestrator skeleton | AVAILABLE | — | — | — | 2.2 DONE |

## ROUND 3 — VALIDATION + OVERFLOW

| Task | Description | Status | Agent | Claimed | Done | Dependency |
|------|------------|--------|-------|---------|------|------------|
| 3.1 | Antigravity validation sweep | AVAILABLE | — | — | — | Round 1+2 DONE |
| 3.2 | Batch 2 template computations (22 templates) | AVAILABLE | — | — | — | 2.1 DONE |
| 3.3 | Report generator | AVAILABLE | — | — | — | 2.4 DONE |
| 3.4 | Template JSON enrichment | AVAILABLE | — | — | — | 1.2 DONE |
| 3.5 | Gap template stubs | AVAILABLE | — | — | — | 1.2 DONE |
| 3.6 | Paper evaluation skeleton | AVAILABLE | — | — | — | 2.4 DONE |
| 3.7 | Salk Institute worked example | AVAILABLE | — | — | — | 2.1 + 2.3 + 2.4 DONE |

---

*Last updated: — (agents update this line with each commit)*
