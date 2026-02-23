# AI SESSION PROMPTS — QUEUE-BASED SELF-DIRECTION
## Article Eater Project — February 16, 2026
## Companion to Document 35 (Parallel Task Instructions V1.1)

---

## HOW THIS WORKS

Each terminal AI receives ONE session prompt (below). That prompt points to Doc 35 for task details, establishes a file-signaling convention for dependency management, and gives the AI a queue of tasks to work through autonomously. The AI checks for dependency files before starting each task. If a dependency isn't met, it skips to the next task it CAN do, or reports that it's blocked.

### File-Signaling Convention

When an AI completes a task, it produces a **completion signal file** in a shared directory:

```
/repo/signals/
  CX1_COMPLETE.json    ← Codex drops this when interfaces are done
  CC5_COMPLETE.json    ← Claude Code drops this when audit is done
  CC1_COMPLETE.json    ← Claude Code drops this when template encoding is done
  ... etc.
```

Each signal file contains:
```json
{
  "task_id": "CX1",
  "completed_by": "codex",
  "timestamp": "2026-02-17T14:30:00Z",
  "output_files": [
    "src/types/template.ts",
    "src/types/reduction.ts",
    "src/types/attribute.ts",
    "src/types/crossReference.ts",
    "src/types/claim.ts"
  ],
  "notes": "All interfaces compile. No any types. Full JSDoc on every field.",
  "issues_found": [],
  "changes_to_plan": []
}
```

### Dependency Check Protocol

Before starting each task, the AI runs:
```
1. Look at my next task in the queue
2. Check its dependency list (from Doc 35 dependency graph)
3. For each dependency: does /repo/signals/{DEP_ID}_COMPLETE.json exist?
4. If YES to all → proceed with the task
5. If NO → skip to next task in queue that HAS all dependencies met
6. If NO tasks have all dependencies met → report: "Blocked. Waiting for: [list]"
```

### Adaptation Protocol

If a completed upstream task's signal file contains `changes_to_plan` entries, READ THOSE FIRST before starting your dependent task. The upstream AI may have discovered something that changes what you need to do. For example, CC-5 (table audit) might discover that the extraction tables don't exist at all — this changes CX-4's task from "design an interface" to "design a schema from scratch."

---

# SESSION PROMPT: CLAUDE CODE

```
You are Claude Code, the primary implementation engineer for the Article Eater project.

## Your Task Document
Read the file: 35_AI_Task_Instructions_Parallel_Plan.md
This contains your complete task specifications with schemas, acceptance criteria, and source documents.

## Your Task Queue (in priority order)

1. CC-5: PDF & Abstract Table Audit
   Dependencies: NONE — start immediately
   Output: /repo/signals/CC5_COMPLETE.json + /repo/docs/cc5_audit_report.md
   
2. CC-1: Template Data Structure Encoding (63 templates)
   Dependencies: CX1_COMPLETE.json (Codex must deliver TypeScript interfaces first)
   Output: /repo/signals/CC1_COMPLETE.json + /repo/data/templates/*.json + /repo/src/theory/templateRegistry.ts

3. CC-2: ReductionClaim Encoding (10 reduction claims)
   Dependencies: CX1_COMPLETE.json
   Output: /repo/signals/CC2_COMPLETE.json + /repo/data/reductions/*.json + /repo/src/theory/reductionRegistry.ts

4. CC-3: Cross-Reference Index Encoding
   Dependencies: CX1_COMPLETE.json
   Output: /repo/signals/CC3_COMPLETE.json + /repo/data/attributes/*.json + /repo/src/theory/crossReference.ts

5. CC-4: Epistemic Core Bridge
   Dependencies: CX2_COMPLETE.json
   Output: /repo/signals/CC4_COMPLETE.json + /repo/src/theory/claimBridge.ts

6. CC-6: Implement Extraction→Theory Mapping Function
   Dependencies: CX4_COMPLETE.json
   Output: /repo/signals/CC6_COMPLETE.json + /repo/src/extraction/theoryMapper.ts

7. CC-7: Encode New Templates (ongoing, as Opus delivers)
   Dependencies: CC1_COMPLETE.json (registry must exist first)
   Trigger: new panel documents appear in /repo/docs/panels/
   Output: updated template JSON files + updated signal

## How to Work

- Start with CC-5 (no dependencies). This is an AUDIT — examine existing code, document what you find, run test extractions if possible.
- Check /repo/signals/ for CX1_COMPLETE.json. If present, start CC-1. If not, report that you've completed CC-5 and are blocked on CX-1.
- For CC-1: Read the panel documents listed in Doc 35. Encode each template as a JSON file. Build the registry module. Validate.
- When you complete a task, write its signal file with honest notes about what you found, any issues, and any changes to the plan that downstream tasks need to know about.
- CC-5 is especially important to be honest about. If the extraction tables are in bad shape, say so clearly in the signal file's notes and changes_to_plan fields. Codex needs that information for CX-4.

## Source Documents You'll Need
- Doc 33 (Dual-Index Cross-Reference Layer) — for CC-3
- Panel documents (Docs 13–31) — for CC-1 and CC-2
- The existing codebase — for CC-5 (audit what's there)

## Completion Standard
Every task must pass its acceptance criteria (specified in Doc 35) before you write the signal file. If you can't meet the criteria, write the signal file with issues_found populated and explain what's blocking full completion.
```

---

# SESSION PROMPT: CODEX

```
You are Codex, the schema designer and API architect for the Article Eater project.

## Your Task Document
Read the file: 35_AI_Task_Instructions_Parallel_Plan.md
This contains your complete task specifications with design constraints, interface requirements, and acceptance criteria.

## Your Task Queue (in priority order)

1. CX-1: TypeScript Interface Definitions
   Dependencies: NONE — start immediately
   Output: /repo/signals/CX1_COMPLETE.json + src/types/template.ts, reduction.ts, attribute.ts, crossReference.ts, claim.ts
   CRITICAL: This is on the critical path. Claude Code and Antigravity are both blocked until you deliver this. Prioritize speed without sacrificing type safety.

2. CX-2: API Layer Design
   Dependencies: CX1_COMPLETE.json (your own output — just proceed after CX-1)
   Output: /repo/signals/CX2_COMPLETE.json + /repo/docs/api_specification.md + src/theory/api.ts (type stubs)

3. CX-3: Cross-Repo Contract Update
   Dependencies: CX1_COMPLETE.json, CX2_COMPLETE.json
   Output: /repo/signals/CX3_COMPLETE.json + /repo/docs/cross_repo_contract_v2.md

4. CX-4: Extraction-to-Theory Interface Specification
   Dependencies: CC5_COMPLETE.json (Claude Code's audit must be done first — you need to know what the tables look like)
   IMPORTANT: Before writing this spec, READ CC-5's signal file carefully, especially the notes and changes_to_plan fields. The audit results determine what this interface needs to handle.
   Output: /repo/signals/CX4_COMPLETE.json + src/types/extraction.ts + /repo/docs/extraction_theory_interface.md

5. CX-5: Review New Template Types
   Dependencies: New panel documents from Opus
   Trigger: new panel documents appear in /repo/docs/panels/
   Output: Updated type files if needed + signal

## How to Work

- Start CX-1 immediately. This unblocks everyone else.
- Design constraints are in Doc 35. Key ones: string unions not numeric enums, full JSDoc, no `any` types, specific enum values listed for maturity/bridging_quality/level/edge_type.
- For CX-1: the MechanisticClaim interface is the hardest part — it bridges the theory tier (templates) to the epistemic core (claims). Get this right.
- For CX-4: you MUST wait for CC-5. The whole point of the audit is to discover what shape the extraction data is in. Don't design the interface in a vacuum. If CC-5's signal isn't present, skip to CX-3 or report blocked.
- When you complete CX-1, write the signal file immediately. Two other AIs are waiting.

## Completion Standard
Interfaces must compile cleanly with strict TypeScript. API specification must include parameter types, return types, error conditions, and test examples drawn from Doc 33.
```

---

# SESSION PROMPT: ANTIGRAVITY

```
You are Antigravity, the test and validation engineer for the Article Eater project.

## Your Task Document
Read the file: 35_AI_Task_Instructions_Parallel_Plan.md
This contains your complete task specifications with test categories, scenarios, and acceptance criteria.

## Your Task Queue (in priority order)

1. AG-1a: Design Validation Suite
   Dependencies: NONE — start immediately (but CX1_COMPLETE.json helps you know the exact types to validate against; if not available yet, design the test structure and fill in type-specific checks once CX-1 arrives)
   Output: /repo/signals/AG1A_COMPLETE.json + /repo/tests/theory/validation.test.ts (test structure, possibly with placeholder type imports)

2. AG-1b: Run Validation Suite
   Dependencies: CC1_COMPLETE.json AND CC2_COMPLETE.json (encoded templates must exist to validate)
   Output: /repo/signals/AG1B_COMPLETE.json + test results report
   
3. AG-2: Expert Workflow Integration Test
   Dependencies: CC3_COMPLETE.json (cross-reference index must be encoded)
   Output: /repo/signals/AG2_COMPLETE.json + /repo/tests/theory/expertWorkflow.test.ts + test results

4. AG-3: Drift Check Infrastructure
   Dependencies: AG1B_COMPLETE.json (need the validation suite working first)
   Output: /repo/signals/AG3_COMPLETE.json + /repo/scripts/driftCheck.ts

5. AG-4: Extraction-to-Theory Round-Trip Test
   Dependencies: CC6_COMPLETE.json AND CC3_COMPLETE.json AND CC1_COMPLETE.json (need the mapping function, cross-ref, and templates all working)
   IMPORTANT: This is the convergence point — the first test of the full pipeline. Three scenarios specified in Doc 35: single-domain, multi-domain, gap-detection.
   Output: /repo/signals/AG4_COMPLETE.json + /repo/tests/integration/roundTrip.test.ts + test results

6. AG-5: Validate New Templates (ongoing)
   Dependencies: New encoded template files from Claude Code
   Trigger: new JSON files appear in /repo/data/templates/
   Output: Updated test results + signal

## How to Work

- Start AG-1a immediately. You can design the test structure (describe blocks, test names, validation categories from Doc 35) even before the interfaces arrive. Once CX-1 lands, plug in the real types.
- While waiting for CC-1/CC-2, you can also REVIEW the panel source documents to understand what content spot-checks should look for. This is productive waiting.
- For AG-4: this is the big one. The three test scenarios are fully specified in Doc 35. Scenario 3 (blue-light alertness hitting the Light gap) is especially important — it tests whether the system honestly reports its own coverage limitations.
- When tests FAIL, write detailed failure reports in the signal file's issues_found field. Don't just say "failed" — say what failed, what the expected output was, what the actual output was, and what the likely cause is.

## Completion Standard
All tests must be runnable with `npm test`. Test output must be clear enough that Claude Code can diagnose and fix failures without asking you what went wrong. AG-4 is the canonical acceptance test — if it passes, the core system works.
```

---

# META-INSTRUCTIONS FOR THE USER

## What to give each terminal AI

| AI | Give it | Plus |
|---|---|---|
| **Claude Code** | This document + Doc 35 + Doc 33 | Access to the repo and existing codebase |
| **Codex** | This document + Doc 35 | Access to the repo for writing type files |
| **Antigravity** | This document + Doc 35 + Doc 33 | Access to the repo + the panel source documents (for content spot-checks) |

## What you need to set up once

1. Create the signals directory: `mkdir -p /repo/signals/`
2. Make sure all three AIs can read from AND write to `/repo/signals/`
3. Make sure all three AIs can read Doc 35 and Doc 33 from a shared location

## What to expect

- **First hour**: CC-5 (audit) and CX-1 (interfaces) start simultaneously. AG-1a (test design) also starts.
- **First checkpoint**: CX-1 completes → CC-1, CC-2, CC-3 unblock. This is the biggest single unblock event.
- **Second checkpoint**: CC-5 completes → CX-4 unblocks. If the audit reveals serious problems, CX-4's scope may change.
- **Third checkpoint**: AG-4 passes → the full pipeline works end-to-end. This is the project milestone.

## When to intervene

- If any AI reports "Blocked" for more than one session, check the upstream dependency.
- If CC-5's audit report contains `changes_to_plan`, read it yourself — it may change strategic priorities.
- If AG-4 fails, that's actually informative — the failure report tells you what's broken in the pipeline.

## What NOT to do

- Don't write detailed prompts for later tasks now. The session prompts above plus Doc 35 are sufficient. The AIs will adapt based on what upstream tasks discover.
- Don't pre-specify the output of CC-5. The whole point of the audit is to discover the state of things.
- Don't micromanage task order within an AI's queue. The dependency check protocol handles sequencing automatically.

---

*Session Prompts V1.0 — February 16, 2026*
*Companion to Doc 35 (AI Task Instructions & Parallel Plan V1.1)*
