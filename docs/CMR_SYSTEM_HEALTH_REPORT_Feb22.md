# CMR SYSTEM HEALTH REPORT — FOUR-AUDITOR SYNTHESIS
## Cross-validation: CC (Opus), AG (Opus), Gemini 1.5 Pro, Codex
## Synthesized by: OPUS/CHAT, February 22, 2026

---

# EXECUTIVE DIAGNOSIS

The CMR theoretical architecture is sound. The credence formula, T1 roster,
T1.5 roster, bridge warrant hierarchy, and panel calibration method are
consistent across all documents. Four independent auditors confirmed this
unanimously. The ideas are right.

The computational substrate is a mess. The 174 template JSONs use 1,533
variable entries across 931 unique root names, of which only 33 appear in
more than one template. The cross-template interaction flags — the mechanism
by which the system is supposed to compute joint effects — are largely
decorative, because the templates they reference use different variable
names for the same constructs. The JSON schemas are wildly inconsistent
(115+ unique top-level keys, two different field names for calibration status,
mechanism chain, bridge warrant, and cross-template interactions). Only 8 of
480 documents in docs/ are marked CURRENT; 246 are UNKNOWN status.

The panel calibration pipeline (Cowork) is working well. Six panels completed,
all passing review, with good expert roster curation and disciplined confidence
scoring. The Crucible debate method is producing high-quality calibrations.

The code infrastructure exists and is functional (BN, coherence, credence
computation, extraction pipeline, belief seeder, theory agents, 172K findings
loaded). But the code and the calibrated theory can't talk to each other
because the template corpus — the bridge between them — is structurally
incoherent.

**In short: the theory is solid, the code works, and the data layer
connecting them is broken.**

---

# WHAT EACH AUDITOR FOUND

## What all four agree on (highest confidence):

- Credence formula consistent everywhere
- T1 roster correct (10 frameworks) after CC fix
- Bridge warrant hierarchy consistent across docs, panels, code
- Core codebase functional (BN, coherence, credence, extraction)
- Cowork pipeline inputs all present
- Panel dependency DAG is structurally sound

## CC (A-01) — broad survey, some errors:

Found: overall architecture sound, DB empty (since fixed), extraction pipeline
functional with 228K claims. Recommended conditional proceed.

Errors: said OPUS_REVIEW_GUIDE.md and exemplar_panel_criteria.md were missing
(both exist). Imprecise template count ("160+"). Missed JSON schema chaos
entirely. Did not assess variable vocabulary.

## AG/Opus (A-02) — best structural finding:

Found: 174 templates with 115+ unique top-level keys, two different field
names for every major concept, 129 templates with no calibration status.
Corrected CC's file-existence errors. Identified the JSON schema as the
top structural risk.

Missed: did not go inside mechanism chains to assess variable-level
consistency. Did not assess sprint execution risks.

## Gemini 1.5 Pro (A-03) — best execution risk findings:

Found three things nobody else caught:
1. CROSSCUT-I (S-08) will collapse the context window — loading all prior
   panel outputs exceeds model limits
2. NEUROMOD-I allostatic integration is mathematically underspecified
3. 314 unique variable names (went deeper than AG's top-level key count)

Missed: did not produce the variable inventory data that Codex produced.

## Codex (A-04 partial) — best empirical data:

Produced before running out of context:
1. Complete variable inventory: 1,533 entries, 931 unique roots
2. Complete document inventory: 480 files with status classification
3. The devastating finding: only 33 of 931 variables appear in more
   than one template

---

# THE FIVE STRUCTURAL PROBLEMS (ordered by severity)

## 1. VARIABLE ISOLATION — CRITICAL

**Finding**: 1,500 of 1,533 variable entries appear in only ONE template.
33 variables appear in 2+ templates. The most shared variable (`aging_65plus`)
appears in only 9 templates out of 174.

**Why it matters**: The CMR's entire value proposition is compositional
reasoning — computing how Template A's output interacts with Template B's
input. This requires shared variable names at the interface points. If
Template A outputs `cortisol_elevation` and Template B expects
`HPA_axis_output`, the system cannot compose them without a mapping layer.

The cross-template interaction flags say "this template interacts with that
template" but the variables they use are mutually unintelligible.

**What must happen**: A canonical variable ontology. Not 931 names — probably
80-120 core variables organized by domain (environmental input, neural
mechanism, psychological state, behavioral outcome, population modifier,
architectural modifier). Every template's mechanism chain, parameters, and
modifiers mapped to this ontology. This is the Variable Normalization Sprint
that Gemini recommended.

## 2. JSON SCHEMA CHAOS — CRITICAL

**Finding**: 115+ unique top-level keys. Two field names for every major
concept (`status`/`calibration_status`, `mechanism_chain`/`mechanism_steps`,
`bridge_warrant`/`bridge_warrant_type`, `cross_template_interactions`/
`super_template_interactions`). 129 templates with no calibration status.

**Why it matters**: Every consumer of the template corpus (belief seeder,
gap tracker, Toulmin validator, Article Eater display layer) must handle
arbitrary structural variation. AG's P1 (canonical schema + migration)
addresses this. It is the prerequisite for everything else.

## 3. DOCUMENT SPRAWL — MODERATE

**Finding**: 480 files in docs/. 8 marked CURRENT. 246 UNKNOWN. Multiple
versions of the same document (11 Transfer Context versions, duplicate
Panel files). Documents marked with dates from Feb 14-22 with no
supersession chain.

**Why it matters**: Any AI system reading docs/ has no way to know which
documents are authoritative without reading PROJECT_STATE.md first. A new
CC or AG session that reads a stale document will make decisions based on
outdated specifications.

**What must happen**: A document lifecycle pass. For every file in docs/,
mark it CURRENT, SUPERSEDED (by what), or ARCHIVE. Move archived files
to docs/archive/. The Codex document inventory CSV is the input for this.

## 4. CROSSCUT-I CONTEXT COLLAPSE — HIGH (but distant)

**Finding**: S-08 requires ALL prior panel outputs as input. Estimated
1.5-2MB of dense markdown. Exceeds context limits.

**Why it matters**: CROSSCUT-I is the capstone panel that reconciles
everything. If it can't see everything, it can't reconcile.

**What must happen**: Build a synthesis script (as Gemini recommended) that
extracts THEORETICAL_DEFAULT flags, unresolved cross-template interactions,
and residual gaps from all panel outputs into a compressed summary (<10KB).
Feed the summary to CROSSCUT-I, not the raw panels. This script can be built
well in advance — it's a known problem with a known solution.

## 5. NEUROMOD-I ALLOSTATIC INTEGRATION — HIGH (but distant)

**Finding**: S-07 tells Cowork to calibrate ALLOSTATIC_MASTER_001 by
integrating HPA cortisol, dopaminergic, noradrenergic, and cholinergic
parameters. No mathematical specification of the integration function.

**Why it matters**: An LLM forced to invent the integration math will
produce something plausible but ungrounded. This is exactly the kind of
theoretical judgment call the Sprint Task Brief shouldn't leave to
autonomous execution.

**What must happen**: Human (you) specifies the allostatic integration
function before S-07 runs. Options: (a) weighted sum with empirically
derived weights, (b) worst-of-N (allostatic load = whichever subsystem
is most stressed), (c) threshold model (load = count of subsystems
exceeding their individual thresholds). Each has different theoretical
commitments. This is a §5.4 Underspecified Judgment Call.

---

# SYSTEM HEALTH SCORECARD

| Domain | Health | Details |
|--------|--------|---------|
| **Theoretical architecture** | ✅ HEALTHY | Formula, tiers, warrants, panel method all consistent |
| **Panel calibration pipeline** | ✅ HEALTHY | 6 panels done, Cowork executing well, review protocol working |
| **Codebase** | ✅ FUNCTIONAL | BN, coherence, credence, extraction, seeder, agents all work |
| **Database** | ✅ POPULATED | 172K findings, 34 beliefs, 50 constraints |
| **Template JSON corpus** | ❌ BROKEN | 115+ keys, 931 variables, 1500 isolated, no canonical schema |
| **Variable ontology** | ❌ ABSENT | Cross-template computation impossible without mapping |
| **Document management** | ⚠️ POOR | 480 files, 8 marked current, 246 unknown |
| **Sprint execution risk** | ⚠️ KNOWN RISKS | CROSSCUT-I context, NEUROMOD-I math — both solvable |

---

# TASK ASSIGNMENTS

## OPUS/CC — Critical path + cleanup

| Priority | Task | Details |
|----------|------|---------|
| **1** | **P1: Canonical JSON schema + migration** | Define schema, build validator/migrator, migrate 174 templates. Unblocks TJ-01. |
| **2** | R-09: Extract MEMORY-I JSONs | 10 templates → data/templates/ |
| **3** | R-10, R-11, R-12: TRANSFER + Sprint Brief updates | Bookkeeping |
| **4** | A-06: NEUROMOD-I PE note | Add to Sprint Brief S-07 |
| **5** | R-13: Mark CLAUDE.md SUPERSEDED | Quick fix |
| **6** | R-15: Check 7 UNKNOWN bridge warrants | Seeder diagnostic |

## OPUS/AG — Variable ontology + future Toulmin

| Priority | Task | Details |
|----------|------|---------|
| **1** | **V-01: Canonical variable ontology** | Using Codex inventory CSV as input, collapse 931 root variables into ~80-120 canonical names organized by domain. Produce `schemas/canonical_variables.json` with mapping from every current name to canonical name. |
| **2** | **V-02: Variable migration script** | Script that reads canonical_variables.json and renames variables inside all 174 template JSONs. Must handle mechanism_chain steps, calibrated_parameters, population_modifiers, architectural_modifiers. |
| **3** | D-01: Document lifecycle pass | Using Codex doc inventory CSV, classify all 480 files as CURRENT/SUPERSEDED/ARCHIVE. Move archived to docs/archive/. |
| Later | TJ-03 through TJ-06 | Retroactive Toulmin extraction (after TJ-02) |

## COWORK — Panel execution

| Priority | Task | Details |
|----------|------|---------|
| **1** | P-03b: Execute MULTI-I | Use clearance doc + TOULMIN_CAPTURE_INTERIM.md |
| **2** | HALT after MULTI-I | Wait for Phase 4 gate |

## HUMAN — Judgment calls

| Priority | Task | Details |
|----------|------|---------|
| **1** | Specify allostatic integration function | Before NEUROMOD-I (S-07). Mathematical form for combining HPA + DA + NE + ACh into single load metric. |
| **2** | Review MULTI-I post-panel output | When Cowork produces it |
| **3** | Approve variable ontology (V-01) | When AG produces it — canonical names are theoretical decisions |

## OPUS/CHAT — Review + strategy

| Priority | Task | Details |
|----------|------|---------|
| Next | Review MULTI-I post-panel | When produced |
| Standing | Cross-validate any further findings | As they arrive |

---

# REVISED CRITICAL PATH

```
NOW (parallel):
  CC: P1 (canonical schema) ──→ TJ-01 ──→ TJ-02 ──→ TJ-07 ──→ Cowork resumes
  AG: V-01 (variable ontology) ──→ V-02 (variable migration)
  COWORK: MULTI-I (gate override) ──→ HALT
  AG: D-01 (document lifecycle) — parallel, non-blocking

THEN:
  TJ-07 + V-02 both complete ──→ Cowork resumes with MUSIC-I
  TJ-03-06 (retroactive Toulmin) — parallel with Cowork
  TJ-08 (AE integration) — after retroactive Toulmin

BEFORE S-07:
  HUMAN: allostatic integration spec

BEFORE S-08:
  CC or AG: build CROSSCUT-I synthesis script
```

---

# PROGNOSIS

The system is architecturally sound at the theory level and functionally
capable at the code level. The data layer connecting them — the template
corpus — needs structural repair that will take CC and AG perhaps 2-3
focused sessions (P1 + V-01 + V-02). This is not a crisis; it's
maintenance debt from building the theoretical architecture across dozens
of Claude sessions without an enforced schema.

Once P1 and V-01/V-02 are complete:
- Every template has a consistent JSON structure
- Every variable has a canonical name
- Cross-template computation becomes mechanically possible
- The Toulmin layer has a stable base to extend
- The Article Eater can actually consume what the panels produce

The panel calibration work (6 panels, 44 templates calibrated) is excellent
and is not at risk. The Crucible debate method produces high-quality content.
The review protocol catches real problems. Cowork's autonomous execution is
working as designed. The remaining 8 panels will proceed cleanly once the
data layer is repaired.

---

*CMR_SYSTEM_HEALTH_REPORT_Feb22.md*
*Four-auditor synthesis: CC, AG, Gemini 1.5 Pro, Codex*
*Reviewed by: OPUS/CHAT*
