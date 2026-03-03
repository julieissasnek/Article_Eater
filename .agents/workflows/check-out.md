---
description: Check-out protocol for AG or Claude at session end
---

# Agent Check-Out Workflow

// turbo-all

Every agent session MUST end with this check-out protocol.

## Steps

1. Run the test suite and record the count:
```bash
python3 -m pytest tests/ -q --tb=no -m 'not slow' 2>&1 | tail -3
```

2. Run the tier taxonomy consistency test specifically:
```bash
python3 -m pytest tests/test_tier_taxonomy_consistency.py -v 2>&1 | tail -20
```

3. Append your session to CHANGELOG.md with:
   - Timestamp
   - Your agent name (AG or Claude)
   - Files changed (list them)
   - Summary of what you did
   - Test impact (new count, any failures)

4. Update COORDINATION_STATE.md:
   - Update "System Metrics" table with new test count
   - Clear your file locks in "Active Work / File Locks"
   - Update "Last Session Summary" for your agent
   - Update any changed canonical values (T1.5 count, AESHI, etc.)

5. Leave messages in MESSAGE_BOARD.md for the other agent:
   - What you changed that they should know about
   - Any ACTION NEEDED items
   - Any files they should audit or verify

6. Update docs/TASKS.md:
   - Mark completed items
   - Add any new items discovered
   - Update status on in-progress items

## Message Format

```markdown
## Message NNN

| Field | Value |
|-------|-------|
| **From** | [AG or Claude] |
| **To** | [Claude or AG] |
| **Date** | [ISO timestamp] |
| **Priority** | [HIGH/MEDIUM/LOW] |
| **Status** | UNREAD |
| **Subject** | [one-line summary] |

**Body**: [details]
```

## Rules

- **NEVER** leave a session without updating COORDINATION_STATE and CHANGELOG
- **ALWAYS** run the test suite before checking out
- If tests fail, fix them before checking out (or document the failure in a message)
- If you touched tier taxonomy, verify `test_tier_taxonomy_consistency.py` passes
