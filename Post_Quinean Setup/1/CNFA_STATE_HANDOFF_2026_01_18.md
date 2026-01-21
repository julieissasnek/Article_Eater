# CNFA Knowledge System: State Handoff Document

**Version**: Sprint 1 Complete
**Date**: Sunday, January 18, 2026
**Previous Claude Session**: Frozen Saturday, January 17, 2026 ~10 PM
**Project**: Article Eater → Web of Belief Integration

---

## EXECUTIVE SUMMARY

You are continuing development of the **CNFA (Cognitive Neuroarchitecture) Knowledge System**, a tool for Professor David Kirsh (UCSD Cognitive Science) that:

1. Extracts scientific findings from environmental psychology papers
2. Integrates them into a **Quinean "Web of Belief"** (coherentist epistemology)
3. Generates predictions about how architectural spaces affect humans
4. Identifies high-value research targets via VOI (Value of Information) analysis

**Current Status**: Sprint 1 is COMPLETE. The core mapper (`extraction_to_web.py`) has been created and tested. Ready for Sprint 2 (pipeline integration) OR expert panel review of 5 decision points.

---

## THE PROBLEM BEING SOLVED

David wants a system that can:
1. **Predict**: Given a tagged image of a built space → deliver probabilistic hypotheses about effects on humans
2. **Prioritize**: Identify VOI-rich targets for experiments
3. **Encode**: Represent the state of knowledge AND ignorance in neuroarchitecture
4. **Evolve**: Avoid premature ossification—the system must revise its own structure

---

## ARCHITECTURAL OVERVIEW

### Four Parallel Tracks (Currently Disconnected)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ARTICLE EATER v20.8.0 ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TRACK A: CONTRACT PIPELINE (production) ← WHERE PAPERS GO IN              │
│  PDF → Seven-Panel extraction → claims.jsonl + rules.jsonl                  │
│  Location: app/tasks/pipeline.py                                            │
│  Status: WORKING, but outputs don't reach web of belief                     │
│                                                                             │
│  TRACK B: WEB OF BELIEF (research) ← THE QUINEAN ENGINE                    │
│  In-memory coherentist epistemology                                         │
│  Location: src/services/web_of_belief.py (1300 lines)                       │
│  Status: IMPLEMENTED, but not connected to Track A                          │
│                                                                             │
│  TRACK C: THEORY REGISTRY (database)                                        │
│  SQLite-backed theory/prediction storage                                    │
│  Location: src/services/theory_registry.py, db/sql/017_theories.sql        │
│  Status: IMPLEMENTED, but not connected to Track A or B                     │
│                                                                             │
│  TRACK D: DUAL EPISTEMOLOGY (analysis)                                      │
│  Foundationalist vs. Coherentist comparison                                 │
│  Location: src/services/dual_epistemology.py                                │
│  Status: IMPLEMENTED as standalone demo                                     │
│                                                                             │
│  >>> THE INTEGRATION TASK: Connect Track A → Track B <<<                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Quinean Commitment (Why This Matters)

David's epistemological commitment is **Quinean coherentism**, not foundationalism:
- Nothing is foundational—all beliefs are revisable
- Justification comes from coherence with other beliefs
- When evidence conflicts, ANY node can be revised (theory, auxiliary assumptions, measurement interpretation)
- The BN is a **derivative artifact** of the web, not the primary representation

This means:
- No hard-coded structure—the BN's DAG is generated from the web's "hardened" beliefs
- Explicit auxiliary assumptions on every edge
- Revision logging—what changed and why
- Minimal change principle—prefer revisions that disturb the least

---

## WHAT'S ALREADY IMPLEMENTED

| Component               | Lines | Key Features                                                     |
| ----------------------- | ----- | ---------------------------------------------------------------- |
| `web_of_belief.py`      | 1292  | Joint distribution over theory-worlds, stubs, reflective equilibrium, coherence assessment, tension detection |
| `refined_epistemic.py`  | 981   | Glymour dependency types, Boghossian semantic status, Bovens-Hartmann coherence |
| `abstraction_levels.py` | 720   | Theory nesting, model zoom (FLAT→DOMAIN→GROUNDED→FULL) |
| `theory_registry.py`    | 845   | SQLite CRUD, prediction search, competing predictions |
| `dual_epistemology.py`  | 530   | Side-by-side framework comparison, divergence analysis |

### Key Classes/Enums in web_of_belief.py

```python
class EpistemicLevel(Enum):
    THEORETICAL = 4      # Core commitments
    INTERMEDIATE = 3     # Generalizations, mechanisms
    EMPIRICAL = 2        # Research findings
    OBSERVATIONAL = 1    # Direct measurements

class BeliefStatus(Enum):
    STUB = "stub"              # Exists but not integrated
    TENTATIVE = "tentative"    # Weakly held
    ESTABLISHED = "established" # Well-supported
    ENTRENCHED = "entrenched"  # Costly to revise
    ANOMALOUS = "anomalous"    # In tension with web

class ConstraintType(Enum):
    SUPPORTS, CONTRADICTS, EXPLAINS, INSTANTIATES, ANALOGOUS, INDEPENDENT
```

---

## SPRINT 1: COMPLETED ✓

### Deliverables Created

1. **`src/services/extraction_to_web.py`** (~700 lines)
   - `claim_to_belief()`: Maps `ae.claim.v1` → `Belief` nodes
   - `rule_to_constraint()`: Maps `ae.rule.v1` → `Constraint` edges
   - `infer_epistemic_level()`: Maps claim_type → EpistemicLevel
   - `infer_theory_relevance()`: Uses outcome taxonomy + keywords
   - `is_stub()`: Detects findings without theory connections
   - `integrate_extraction()`: Batch integration with reporting

2. **`tests/test_extraction_to_web.py`** — 15 tests, all passing

3. **`docs/SPRINT_1_COMPLETION.md`** — Summary with expert panel questions

### Mapping Logic Implemented

| claim_type    | → EpistemicLevel | Rationale                         |
| ------------- | ---------------- | --------------------------------- |
| mechanistic   | THEORETICAL      | Mechanism claims are theory-level |
| causal        | INTERMEDIATE     | Generalizations                   |
| associational | EMPIRICAL        | Single-study findings             |
| descriptive   | OBSERVATIONAL    | Direct measurements               |
| moderated     | EMPIRICAL        | With moderator metadata           |
| null          | EMPIRICAL        | Null findings → ANOMALOUS status  |

### Five Decision Points Flagged for Expert Review

1. **claim_type → EpistemicLevel mapping** — Is "mechanistic" appropriately THEORETICAL?
2. **Theory inference threshold** (0.4) — Too high? Too low?
3. **Null finding treatment** — ANOMALOUS with 50% credence reduction
4. **Multi-strategy theory inference** — Is keyword matching too noisy?
5. **Polarity → ConstraintType mapping** — Are strength modifiers appropriate?

---

## SPRINT PLAN (Remaining)

### Sprint 2: Pipeline Integration
- Wire mapper into `app/tasks/pipeline.py`
- New outputs: `web_state.json`, `stubs.jsonl`, `tensions.jsonl`, `coherence_summary.json`
- Update contracts per governance requirements

### Sprint 3: Bridge Warrant Foundation
- Schema extension with `bridge` field
- Bridge types: mechanism, functional, analogical, constitutive
- Bridge-weighted credence calculation

### Sprint 4: Outcome Taxonomy Enhancement
- Add temporal classes: immediate_state, delayed_state, cumulative_dispositional, chronic_health
- Category-aware bridge validity

### Sprint 5: Persistence & Accumulation
- JSON persistence with versioning
- Corpus-level processing

### Sprint 6: VOI Computation
- Tension resolution value
- Bridge validation value
- Population coverage value
- Stub integration value

### Sprint 7: BN Export & Multiple Models
- Empirical BN vs. Theory-loaded BN
- Comparison report

### Sprint 8: Integration Testing & Documentation

### Priority Order (Pre-India Trip)
1. Sprint 1 ✓ DONE
2. Sprint 2 (essential)
3. Sprint 3 (high value)
4. Sprint 5 (needed for real use)

---

## EXPERT PANEL (Constructed Voices)

The previous Claude convened an expert panel for design decisions:

- **Dr. Judea Pearl** — Bayesian networks, causal inference
- **Dr. Nancy Cartwright** — Philosophy of science, bridge warrants
- **Dr. Herbert Simon** — Bounded rationality, system design
- **Dr. Marcia Bates** — Information science, knowledge organization
- **Dr. Rachel Kaplan** — Environmental psychology (the domain)

Key panel consensus points:
1. The Quinean layer is **foundational infrastructure**, not optional
2. Bridge warrants are the **novel epistemological contribution**
3. The outcome taxonomy should start coarse (4 categories) and refine
4. Multiple BN architectures should be compared, not assumed
5. Meta-level flexibility requires **discipline**—build joints, not infinite flexibility

---

## KEY CONCEPTS

### Bridge Warrants
When a finding from one domain (e.g., object-level studies) is applied to another (e.g., architecture), a **bridge warrant** licenses the transfer:
- **Mechanism bridge**: Same causal pathway operates in both domains
- **Functional bridge**: Same input-output relationship, possibly different mechanism
- **Analogical bridge**: Structural similarity licenses inference
- **Constitutive bridge**: Target domain literally composed of source domain

Example: Bar & Neta found amygdala activation for angular objects. Vartanian found ACC (not amygdala) activation for angular rooms. The **mechanism bridge failed**. This failure is informative—it's where VOI lives.

### Three-Level Credence Decomposition
```
P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)
```
If P(parent theory) is high and P(bridge) is low, the valuable experiment tests the **bridge**, not the theory.

### Stubs
Findings that don't fit the current ontology aren't forced in or dropped—they're held as **stubs** until the ontology evolves. This is how good researchers actually work.

---

## REPO LOCATION AND STRUCTURE

**Local Path**: `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1`

**Streamlining Plan** (agreed upon 2026-01-18):
- Aggressive version increments (V20.8.0 → V21.0.0 for Post-Quinean)
- Minimal essential ZIPs with dated names
- Docs extracted to `DOCS_DATED/` with timestamps in filenames
- Obsolete files → `quarantine/YYYY-MM-DD/` (no deletions per governance)
- Human-informative docs always dated and well-marked

**Claude Code** can handle implementation and repo operations directly.

---

## FILES DAVID SHOULD PROVIDE

To continue effectively, ask David to upload:

1. **Sprint 1 deliverables** (if not already in repo):
   - `src/services/extraction_to_web.py`
   - `tests/test_extraction_to_web.py`
   - `docs/SPRINT_1_COMPLETION.md`

2. **Core project files**:
   - `src/services/web_of_belief.py`
   - `app/tasks/pipeline.py`
   - Claim/rule schemas from `contracts/ae_af/schemas/`

3. **If available**: Current project ZIP or directory listing

---

## GOVERNANCE REQUIREMENTS

The project has strict governance (from Project Constitution):
1. **Contract-first**: All public-surface changes require micro-contract updates
2. **No deletions**: Obsolete files go to `quarantine/YYYY-MM-DD/`
3. **Governance kit immutable**: Files in `release.keep.yml` are protected
4. **Release format**: ZIP repo + concatenated TXT + SHA256 manifest

---

## NEXT STEPS

**Option A**: Proceed to Sprint 2 (pipeline integration)
- Modify `pipeline.py` to call the mapper
- Add new output files to bundle
- Test with real papers

**Option B**: Convene expert panel first
- Review the 5 decision points from Sprint 1
- Get philosophical validation before proceeding

David's preference was for expert consultation to happen **as a function of what is being completed**, especially if surprises emerge during implementation.

---

## DAVID'S PREFERENCES (For Response Style)

- Clean academic writing (Bertrand Russell style without exaggerated Britishisms)
- Academic references with APA citations and bibliography
- Longer rather than shorter answers
- Clear distinction between scientific support vs. differences of view
- NEVER use generic download names—always use descriptive versioned names
- ALWAYS include complete reference lists with DOIs where available

---

## CONTEXT ALERT PROTOCOL

When context is running low:
1. Alert David proactively
2. Create an updated state handoff document like this one
3. Save to outputs so David can upload to new instance
4. Summarize what was accomplished and what remains

---

## TOOLING SETUP

**Claude.ai Project**: "Post_Quinean AE"
- For: Planning, expert panels, architecture, document review
- Knowledge base contains: This handoff doc + key source files

**Claude Code** (Terminal):
- For: Writing code, running tests, git, file operations, streamlining
- Start with: `cd /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1 && claude`

**Workflow**: Use Project chat for decisions, Claude Code for implementation. Sync via updated handoff docs.

---

*Document created: Sunday, January 18, 2026*
*For use in spinning up new Claude instances when current instance freezes*
