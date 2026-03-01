# ATLAS Ruthless System Audit Prompt

*Date: 2026-02-27*
*Purpose: Multi-level, adversarial audit of the ATLAS system*
*Target: Any capable LLM agent with codebase access*

---

## Instructions for the Auditor

You are conducting a **ruthless, multi-level audit** of the ATLAS system (Architecture for Typed, Layered Assessment of Science), a coherentist epistemology engine that extracts scientific claims from research articles and integrates them into a Quinean web of belief with a parallel Bayesian network. The system domain is neuroarchitecture — the intersection of cognitive science, neuroscience, and the built environment.

The system comprises approximately 875 Python files, a Streamlit dashboard, a 14-step integration cascade, an overseer governance module, and a pipeline scheduler. It is maintained by Professor David Kirsh (UCSD Cognitive Science) with AI assistant support.

**Your mandate:** Be intellectually honest and adversarial. Identify genuine failures, not cosmetic issues. Distinguish between (a) principled design decisions worth defending, (b) implementation gaps that undermine the design, and (c) architectural confusions where the code contradicts the stated philosophy. Praise what deserves praise. Damn what deserves damning. Do not soften your findings.

Before beginning, run:

```bash
python scripts/atlas_system_map.py
```

This generates structural data in `docs/system_maps/` — module dependency graph, web topology, BN structure, pipeline map, and data flow audit. Use this data throughout your audit.

---

## Level 1: Philosophical Foundations

The system claims to implement a **Quinean coherentist epistemology** (Quine, 1951) with elements of **foundherentism** (Haack, 1993) and **reflective equilibrium** (Rawls, 1971). The Bayesian network layer draws on **Pearl's causal inference** (Pearl, 2009).

### 1.1 Does the web actually behave coherentistically?

Examine `src/services/web_of_belief.py` (2,167 lines) and answer:

- **Quinean revisability**: Can *any* belief at *any* epistemic level be revised, including theoretical commitments and "observations"? Or does the code smuggle in foundationalist assumptions (e.g., observations treated as incorrigible, theory treated as privileged)?
- **Mutual constraint**: Does warrant genuinely flow in all directions, or only top-down (theory → prediction → observation)? Trace the actual constraint satisfaction logic.
- **Coherence criterion**: What is the precise mathematical definition of "coherence" in this system? Is it (a) constraint satisfaction ratio, (b) explanatory power in Thagard's sense, (c) probabilistic coherence (Bovens & Hartmann, 2003), or (d) something ad hoc? Does the implementation match the stated philosophy?
- **Stubs**: The system allows "stubs" — beliefs without theoretical attachment. This is philosophically interesting (it means observations aren't required to fit existing theory). Are stubs actually *used* in practice, or just defined? What happens to them over time?
- **Theory worlds**: The system maintains parallel "theory worlds." How does this relate to Quinean holism? Quine doesn't have theory worlds — he has one web. Is this a justified extension or a philosophical confusion?

### 1.2 Four credence formulas at four layers — coherent or confused?

The system reportedly has different credence formulas at different layers:

1. **Bridge multiplicative** — warrant ceiling × strength
2. **Noisy-OR multi-channel** — convergence across independent evidence channels
3. **Warrant combination with ceilings** — type-specific credence limits (CONSTITUTIVE: 0.75, MECHANISM: 0.60, etc.)
4. **BN weighted linear** — Bayesian network probability

**Question**: Do these four formulas compose coherently into a single epistemic assessment, or do they produce contradictory credence values for the same proposition? Trace a concrete claim through all four layers. What happens when Layer 1 says credence = 0.72 but Layer 3's ceiling caps it at 0.60? Is the semantics of "credence" consistent across layers?

### 1.3 The π projection function: Web → BN

How does the system project from the web of belief into the Bayesian network? Find and evaluate the actual code that performs this mapping. Specifically:

- Is there a well-defined mathematical projection function, or is it ad hoc wiring?
- What is lost in translation? (The web has holistic coherence; the BN has conditional independence assumptions. These are in tension.)
- When the BN updates probabilities, does information flow *back* to the web? If not, is the BN just an export artifact with no epistemological standing?
- Check `src/epistemic/bn_edges.py` PATHWAY_DEFAULTS — these map keywords to pathway types. Is this principled or brittle keyword matching?

### 1.4 Warrant typology

Seven warrant types with ceilings: CONSTITUTIVE(0.75), MECHANISM(0.60), EMPIRICAL_COVARIANCE(0.60), FUNCTIONAL(0.50), CAPACITY(0.45), THEORETICAL_DEFAULT(0.40), ANALOGICAL(0.35).

- Are these ceilings empirically calibrated or arbitrary? What is the epistemological justification for these specific numbers?
- Should warrants have fixed ceilings at all, or should ceiling height be context-dependent?
- How do these warrant types relate to established epistemological frameworks? (Toulmin's warrant schema? Pollock's defeasible reasoning? Walton's argumentation schemes?)

---

## Level 2: Architectural Integrity

### 2.1 Module coupling and cohesion

Run `python scripts/atlas_system_map.py --modules` and examine the dependency graph.

- **Hub modules**: Which modules are imported by 10+ others? Are these justified hubs (core abstractions) or accidental god-objects?
- **Orphan modules**: Which modules are never imported? Are these dead code, or independently runnable scripts?
- **Circular dependencies**: Are there import cycles? (Common in Python, devastating for reasoning about the system.)
- **Package structure**: Does the directory layout (`src/services/`, `src/epistemic/`, `src/api/`, `src/models/`) reflect genuine architectural boundaries, or is it cosmetic organization over tangled code?

### 2.2 Contract enforcement

The system uses `ClaimV2` (see `src/epistemic/contracts/claim_v2.py`) as a universal ingestion contract.

- Is ClaimV2 actually *enforced* at all entry points, or are there code paths that bypass it?
- Search for any code that creates beliefs or nodes without going through ClaimV2 validation.
- Are the 12 NodeType values actually used in practice, or do most nodes use a generic type?
- What happens when a claim fails validation? Is it silently dropped, quarantined, or does it halt the pipeline?

### 2.3 Database architecture

The system uses SQLite databases:
- `web_of_belief.db` — the epistemic web
- `overseer.db` — governance and pipeline state
- Various JSON files (extraction queue, notification queue, approval log)

**Questions:**
- Is there a single source of truth, or can the web.db and the JSON queue disagree about a paper's status?
- What happens during concurrent access? (SQLite WAL mode? File locking?)
- Is there a migration strategy? What happens when the schema changes?
- Are there any foreign key constraints enforced, or is referential integrity left to application code?

### 2.4 The 14-step integration cascade

Examine `src/services/paper_integration/orchestrator.py`:

- Are all 14 steps actually implemented, or are some stubs/placeholders?
- What is the transaction semantics? If step 9 fails, are steps 1-8 rolled back?
- Is the cascade idempotent? Can you safely re-run it for the same paper?
- What happens if the cascade is interrupted mid-execution?

---

## Level 3: Code Quality

### 3.1 Dead code and unreachable paths

Search for:
- Functions defined but never called (especially in `src/services/overseer.py`)
- Classes instantiated with wrong constructor signatures (check `OverseerService.__init__` — it takes 3 positional args: `overseer_db_path`, `web`, `web_db_path`)
- Import statements that import symbols never used
- Try/except blocks that silently swallow errors (`except Exception: pass`)

### 3.2 Error handling philosophy

Does the system follow a consistent error handling strategy?

- Are errors propagated, logged, or swallowed?
- Count instances of bare `except:` or `except Exception: pass`
- Is there a centralized logging configuration, or does each module configure its own logger?
- When a pipeline stage fails, does the system degrade gracefully or cascade-fail?

### 3.3 Type safety

- Is the codebase type-annotated? What percentage of functions have type hints?
- Are there any runtime type checks (isinstance, assert) that compensate for missing static analysis?
- Does the system use dataclasses/Pydantic for structured data, or are there bare dicts flowing through the system?

### 3.4 Test coverage

- How many test files exist in `tests/`? What is the approximate coverage?
- Are there integration tests that exercise the full pipeline (discovery → integration)?
- Are the tests actually runnable? (`pytest tests/ -x --tb=short`)
- Are there any tests for the philosophical invariants (e.g., "no belief is incorrigible")?

---

## Level 4: Robustness Under Adversarial Conditions

### 4.1 Missing databases

What happens if you:

```bash
mv data/web_of_belief.db data/web_of_belief.db.bak
python scripts/overseer_nightly_v2.py
```

Does the overseer crash? Degrade gracefully? Create an empty database?

### 4.2 Malformed extraction input

What happens if the extraction queue contains:
- A paper with `extraction_result: null`
- A finding with negative p-values
- A claim with credence > 1.0
- An extraction with 10,000 findings (memory pressure)

### 4.3 Circular constraints

What happens if belief A supports belief B and belief B supports belief A? Does the coherence calculation converge, oscillate, or stack-overflow?

### 4.4 Concurrent pipeline runs

What happens if `scheduled_pipeline.py run --stage integration` is running while someone approves a paper via `review_extractions.py approve`?

---

## Level 5: Intelligibility

### 5.1 Documentation audit

- Is `ARCHITECTURE.md` accurate and up-to-date? Cross-check at least 5 claims against actual code.
- Is `SCHEMA_REGISTRY.md` current? Do the documented table schemas match the actual database?
- Does the main `README.md` explain what the system *does* clearly enough for a first-time reader?
- Is there a glossary of the 50+ domain-specific terms (AESHI, warrant ceiling, foundherentism, noisy-OR, entrenchment, etc.)?

### 5.2 Onboarding test

Could a competent Python developer with no cognitive science background, given only the codebase and documentation:

1. Understand what the system does within 30 minutes?
2. Run the system and see it process a paper within 60 minutes?
3. Make a meaningful code change (e.g., add a new warrant type) within 120 minutes?

Identify the specific gaps that would block each milestone.

### 5.3 System organization visualization

Run `python scripts/atlas_system_map.py` and evaluate the generated report at `docs/system_maps/atlas_system_report.md`:

- Does the module graph reveal the true architecture, or is it too noisy to be useful?
- Is the pipeline flow comprehensible?
- Can you trace data flow from "PDF on disk" to "belief in web" through the documented stores?

### 5.4 Naming discipline

- Are file names descriptive and versioned per project conventions?
- Are there files named `utils.py`, `helpers.py`, `misc.py`, or other uninformative names?
- Do function names in the epistemic layer use vocabulary consistent with the philosophical literature? (e.g., "entrenchment" should mean what Quine meant, not some ad hoc measure)

---

## Level 6: Overseer and Governance

### 6.1 Overseer coverage

The overseer (`src/services/overseer.py`) defines invariants INV-0 through INV-5:

- INV-0: System operational
- INV-1: Provenance (Haack)
- INV-2: BN-web sync (Pearl)
- INV-3: ClaimV2 schema
- INV-4: Coherence decline ≤ 5% (Dijkstra)
- INV-5: Credence bounds [0,1]

**For each invariant:**
- Is it actually checked in `check_integrity()`?
- Has it ever *caught* a real violation? (Check `data/notifications/queue.json` and overseer reports)
- Could the invariant be satisfied vacuously? (e.g., INV-4 is trivially satisfied if the web has 0 beliefs)

### 6.2 Pipeline registry

- Is the pipeline registry (`pipeline_registry` table in overseer.db) populated?
- Does `register_canonical_pipelines()` get called at startup, or only manually?
- Can the overseer detect a stale pipeline (one that hasn't run in 24+ hours)?

### 6.3 HITL effectiveness

- When a notification is queued (extraction review, health alert), is there any mechanism to *escalate* if it goes unacknowledged?
- Is the notification queue ever pruned, or does it grow indefinitely?
- Can a human reviewer see *why* the extraction looks the way it does (provenance back to the PDF)?

### 6.4 AESHI health score

The system reports an AESHI (Article Eater System Health Index) score.

- What are the exact components and weights of AESHI?
- Is the scoring formula documented?
- Has the score ever been above 70? If not, is the formula miscalibrated?

---

## Level 7: Integration Testing Gauntlet

Run the following commands and document every failure:

```bash
# 1. System map
python scripts/atlas_system_map.py

# 2. Pipeline status
python scripts/scheduled_pipeline.py status

# 3. Notification check
python scripts/check_notifications.py pending

# 4. Extraction review queue
python scripts/review_extractions.py list

# 5. Health check
python scripts/overseer_nightly_v2.py --dry-run 2>&1 || echo "OVERSEER FAILED"

# 6. Test suite
pytest tests/ -x --tb=short -q 2>&1 | tail -20

# 7. Import check (can all modules be imported?)
python -c "
import sys, importlib, pathlib
root = pathlib.Path('src')
failures = []
for f in sorted(root.rglob('*.py')):
    if '__pycache__' in str(f) or f.name == '__init__.py':
        continue
    mod = str(f).replace('/', '.').replace('.py', '')
    try:
        importlib.import_module(mod)
    except Exception as e:
        failures.append((mod, str(e)[:80]))
print(f'{len(failures)} import failures out of {len(list(root.rglob(\"*.py\")))} modules')
for m, e in failures[:20]:
    print(f'  FAIL: {m}: {e}')
"

# 8. Lint check
ruff check src/ --select E,W --statistics 2>&1 | tail -15
```

For each failure, classify it as:
- **CRITICAL**: System claim violated (e.g., an invariant that doesn't work)
- **MAJOR**: Functionality that should work but doesn't
- **MINOR**: Cosmetic or non-blocking issue
- **DESIGN**: Architectural decision worth revisiting

---

## Deliverable Format

Structure your audit report as follows:

```
# ATLAS System Audit Report
Date: [date]
Auditor: [identity]

## Executive Summary
[3-paragraph honest assessment: what works, what's broken, what's confused]

## Scores (1-10)
- Philosophical coherence: X/10
- Architectural integrity: X/10
- Code quality: X/10
- Robustness: X/10
- Intelligibility: X/10
- Overseer/governance: X/10
- Overall: X/10

## Level 1 Findings: Philosophy
[...]

## Level 2 Findings: Architecture
[...]

## Level 3 Findings: Code Quality
[...]

## Level 4 Findings: Robustness
[...]

## Level 5 Findings: Intelligibility
[...]

## Level 6 Findings: Governance
[...]

## Level 7 Findings: Integration Tests
[...]

## Top 10 Critical Issues (Ranked by Severity)
1. [Most severe issue]
...
10. [10th most severe issue]

## Top 5 Strengths
1. [Genuine achievement worth preserving]
...

## Recommended Priority Actions
1. [Most impactful improvement]
...

## References
[APA style, with Google Scholar citation counts where available]
```

---

## Philosophical References for the Auditor

- Quine, W.V.O. (1951). Two dogmas of empiricism. *Philosophical Review*, 60(1), 20–43. [15,000+ citations]
- Haack, S. (1993). *Evidence and Inquiry: Towards Reconstruction in Epistemology*. Blackwell. [2,000+ citations]
- Rawls, J. (1971). *A Theory of Justice*. Harvard University Press. [80,000+ citations]
- Pearl, J. (2009). *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press. [30,000+ citations]
- Thagard, P. (1989). Explanatory coherence. *Behavioral and Brain Sciences*, 12(3), 435–467. [1,500+ citations]
- BonJour, L. (1985). *The Structure of Empirical Knowledge*. Harvard University Press. [2,000+ citations]
- Bovens, L., & Hartmann, S. (2003). *Bayesian Epistemology*. Oxford University Press. [1,200+ citations]
- Toulmin, S.E. (1958). *The Uses of Argument*. Cambridge University Press. [10,000+ citations]
- Pollock, J.L. (1995). *Cognitive Carpentry: A Blueprint for How to Build a Person*. MIT Press. [500+ citations]
- Walton, D. (1996). *Argumentation Schemes for Presumptive Reasoning*. Erlbaum. [1,500+ citations]

---

*This prompt was generated by the ATLAS system itself (specifically, by a Claude agent operating within the codebase on 2026-02-27). The fact that the system can generate its own audit criteria is itself an interesting data point about self-reflexivity — but do not let that make you sympathetic. Be ruthless.*
