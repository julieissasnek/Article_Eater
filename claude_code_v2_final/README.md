# How to Use This With Claude Code

## What's In This Package

```
CLAUDE.md                           ← Claude Code reads this automatically
docs/IMPLEMENTATION_TASKS.md        ← 30 atomic, sequential, testable tasks
docs/THEORY_REFERENCE.md            ← (you add this) theoretical context if CC needs it
```

## Setup Steps

### 1. Copy files into your Article Eater project

```bash
# From your Article Eater project root:
cp <this-folder>/CLAUDE.md ./CLAUDE.md
mkdir -p docs/
cp <this-folder>/docs/IMPLEMENTATION_TASKS.md ./docs/IMPLEMENTATION_TASKS.md
```

### 2. Update CLAUDE.md with real file paths

Open CLAUDE.md and replace the guessed paths in "Architecture Quick Reference"
with the actual paths in your project. This is critical — Claude Code will
look for these files.

### 3. Optionally add the theory reference

If you want Claude Code to understand WHY it's building what it's building
(useful if it needs to make judgment calls), copy the working paper:

```bash
cp Missing_Fourth_Channel_Epistemic_Tier2_V1.0.docx docs/
```

Or better, create a condensed `docs/THEORY_REFERENCE.md` with just the
template specs, BN node definitions, and panel consensus. Claude Code
works better with markdown than with docx.

### 4. Commit the setup

```bash
git add CLAUDE.md docs/
git commit -m "[Sprint 0 / Setup] Add implementation plan for epistemic Tier 2"
```

## Running Claude Code

### Start each session with context

```bash
# In your project root:
claude

# Then tell it:
> Read CLAUDE.md and docs/IMPLEMENTATION_TASKS.md. We're working on
> the Epistemic Tier 2 integration. What task should we do next?
```

### If starting a new session (Claude Code has no memory between sessions)

```bash
claude

> Read CLAUDE.md. Check git log --oneline -20 to see what's been
> done. Then read docs/IMPLEMENTATION_TASKS.md and pick up where
> we left off.
```

### Key phrases that help

- "Read the task file and do Task 1.3"
- "Run the acceptance test for the task you just completed"
- "Run the full test suite before committing"
- "Don't proceed to the next task until this test passes"

### If Claude Code gets confused

- "Stop. Read CLAUDE.md again."
- "Look at the actual codebase — run `find . -name '*.py' | head -20`"
- "The task says X but the codebase uses Y. Adapt the task to match the codebase."

## What Can Go Wrong and How to Fix It

### Problem: CC invents file structures that don't match your project
**Fix**: Task 0.1 (codebase discovery) exists precisely for this. Make sure
CC completes it and records real paths before doing anything else.

### Problem: CC tries to do multiple tasks at once
**Fix**: Tell it "Do only Task N.M. Nothing else."

### Problem: CC skips writing tests
**Fix**: Every task has a Test section. Say "Write the test first, then implement."

### Problem: CC doesn't understand the domain (what IS a bridge warrant?)
**Fix**: Point it at docs/THEORY_REFERENCE.md or give a one-sentence definition:
"A bridge warrant is a typed justification linking evidence to a claim. Types
include mechanism, functional, analogical, constitutive. See the existing code."

### Problem: CC runs out of context on a complex task
**Fix**: Break the session. Start a new one with "Read CLAUDE.md. We just
finished Task N.M. Do Task N.(M+1)."

### Problem: Existing codebase doesn't have the structures the tasks assume
**Fix**: This WILL happen. The tasks assume generic structures (Node model,
Edge model, enum file). CC should adapt. Tell it: "The tasks are a specification.
The codebase is ground truth. If they conflict, adapt the task to the codebase."

## Session Management Strategy

Claude Code works best in focused sessions. Recommended approach:

- **Session 1**: Sprint 0 (discovery) — 15 minutes
- **Session 2**: Sprint 1, Tasks 1.1–1.7 (enums) — 30 minutes
- **Session 3**: Sprint 1, Tasks 1.8–1.11 (model extensions) — 30 minutes
- **Session 4**: Sprint 2, Tasks 2.1–2.3 (BN structure) — 45 minutes
- **Session 5**: Sprint 2, Tasks 2.4–2.6 (pathway tagging, source quality) — 30 minutes
- **Session 6**: Sprint 3, Tasks 3.1–3.2 (audit, asymmetry) — 45 minutes
- **Session 7**: Sprint 3, Tasks 3.3–3.5 (bias, adversarial, tests) — 45 minutes
- **Session 8**: Sprint 4, Tasks 4.1–4.5 (extraction) — 45 minutes
- **Session 9**: Sprint 5 (integration testing) — 60 minutes

Total: ~6–7 hours of Claude Code time across ~9 sessions.
