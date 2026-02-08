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
| 2.0.4 | Test pipeline with sample papers | Terminal-2 | 2026-02-08 17:30 | IN_PROGRESS | Running sample papers through pipeline |

---

## Available Tasks (Not Claimed)

| Task ID | Description | Priority | Dependencies |
|---------|-------------|----------|--------------|
| 2.0.5 | Error handling and logging | P2 | 2.0.4 |
| 3.0.1 | Unified API | P3 | 2.0, 2.5 |
| 3.0.2 | Query engine (NL → structured) | P3 | 2.5 |
| 3.0.3 | Visualization (web, community graphs) | P3 | 2.5 |
| 3.0.4 | Export (BibTeX, summaries) | P3 | 2.0 |

---

## Completed Today (2026-02-08)

| Task ID | Description | Terminal | Completed At | Outcome |
|---------|-------------|----------|--------------|---------|
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

*Last coordination check: 2026-02-08 18:00*
