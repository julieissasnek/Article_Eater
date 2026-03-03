---
description: Check-in protocol for AG or Claude at session start
---

# Agent Check-In Workflow

// turbo-all

Every agent session MUST begin with this check-in protocol.

## Steps

1. Read the coordination state to understand current system metrics and what the other agent last did:
```bash
cat .agent_coord/COORDINATION_STATE.md
```

2. Check the message board for unread messages from the other agent:
```bash
cat .agent_coord/MESSAGE_BOARD.md
```

3. Read the changelog to see recent changes:
```bash
tail -50 .agent_coord/CHANGELOG.md
```

4. Read the shared task list for pending items:
```bash
cat docs/TASKS.md | head -100
```

5. Update COORDINATION_STATE.md:
   - Set your entry in the "Active Work / File Locks" table
   - Record what you plan to work on
   - Lock any files you'll be editing

6. If there are UNREAD messages for you in MESSAGE_BOARD.md:
   - Read them carefully
   - Mark as ACKNOWLEDGED
   - Act on any ACTION NEEDED items

## Rules

- **NEVER** edit a file that the other agent has locked in COORDINATION_STATE
- **ALWAYS** check the canonical source files listed in COORDINATION_STATE before hardcoding any counts
- T1=10, T1.5=13, T2=~166, Molecules=18, T3=DYNAMIC — load from JSON, don't hardcode
- If you change any tier taxonomy, follow `docs/TIER_TAXONOMY_PROPAGATION_PROCEDURE.md`
