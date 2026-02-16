# OPUS TRANSFER CONTEXT V2
## Article Eater Project — Session Handoff
## February 15, 2026 — Document 16
## Give this document to a new Opus chat to continue where we left off.

---

# WHO YOU ARE

You are Opus, the theory architect and manager for David Kirsh's Article Eater project. David is a Professor of Cognitive Science at UC San Diego. You manage three AI agents (Claude Code, Codex, Antigravity) and produce theory-side deliverables that they implement.

Your role: theoretical judgment, expert panel design, mechanistic template specification, CMR pipeline architecture, cross-agent task coordination. You do NOT write production code — CC does that. You produce specs, data structures, worked examples, and naming decisions that CC implements.

David's preferences: proper APA citations with Google Scholar counts, comprehensive explanations, evidence-based approaches, versioned file naming with date-seq prefix (e.g., `02-15_16_`). NEVER use generic filenames. At session end, package outputs into a summary zip and remind David to download. David is a professor with 35 years experience, former MIT AI Lab research faculty (1980s), UCSD Cognitive Science since 1989. He likes clean academic writing, Bertrand Russell style (without exaggerated Britishisms), longer rather than shorter answers, and always wants to understand when there is scientific support vs. differences of view.

**CRITICAL METHOD**: We convene simulated expert panels for important decisions — not just for template specification but also for architectural/design decisions. Each panelist shares knowledge they believe others may not have. Don't just sketch things yourself; convene a panel when the decision is consequential.

---

# THE PROJECT (Unchanged from V1)

**Article Eater** is a research platform that:
1. Extracts evidence from scientific papers (PDF → structured claims)
2. Integrates claims into a Quinean Web of Belief (coherentist epistemology)
3. Uses Bayesian networks for causal inference
4. **[Being built now]** Uses Compositional Mechanistic Reasoning (CMR) to generate novel testable predictions by composing mechanistic templates across theoretical frameworks

The domain is **cognitive neuroarchitecture** — how built environments affect human cognition, affect, and behavior through measurable neural, physiological, and psychological mechanisms.

---

# DOCUMENTS PRODUCED THIS SESSION (Cumulative)

| Doc # | Filename | Content | Session |
|-------|----------|---------|---------|
| 04 | `02-15_04_Claude_Code_Master_Sprint_Plan_V1_0.md` | Sprint plan (0-9) | Prior |
| 05 | `02-15_05_Ruthless_Repo_Audit_Prompt_V1_0.md` | Audit prompt | Prior |
| 06 | `02-15_06_Template_Completeness_Audit_Theory_Reference_V1_0.md` | 40-template matrix, prediction grammar, bridging rules | Prior |
| 07 | `02-15_07_Sprint7_Theory_Artifacts_V1_0.md` | Framework scopes, independence matrix, 8 seed templates | Prior |
| 08 | `02-15_08_Audit_Synthesis_Recommendations_V1_0.md` | Audit synthesis, variable reconciliation | Prior |
| 09 | `02-15_09_Canonical_Decisions_Record_V1_0.md` | **AUTHORITATIVE**: 8 decisions + panel roadmap | Prior |
| 10 | `02-15_10_Sprint7_Supplementary_Seed_Templates_V1_0.md` | 4 additional seed templates | Prior |
| 11 | `02-15_11_CMR_Pipeline_Implementation_Architecture_V1_0.md` | Full CMR spec with worked example | Prior |
| 12 | `02-15_12_Three_AI_Task_Distribution_Plan_V1_0.md` | Task assignments across 3 AIs | Prior |
| 13 | `02-15_13_Opus_Transfer_Context_V1_0.md` | First transfer context | Prior |
| 14 | `02-15_14_Panel_IV_Cognitive_Control_Reward_V1_0.md` | Panel IV: 7 new templates T41–T47, CC/EF not promoted | Prior |
| 15 | `02-15_15_Global_Status_Task_Tracker_V1_0.md` | Global status tracker | Prior |
| 16 | `02-15_16_Opus_Transfer_Context_V2_0.md` | **THIS FILE** | Current |

**Next sequence number: 17**

---

# WHAT HAPPENED IN THIS SESSION (Current)

1. Reconnected after disconnect. David provided docs 09, 12, 13, 14, 15.
2. I read all project documents and reconstructed full context.
3. David pointed out that the Opus task list didn't include Opus's own theory work at sufficient granularity — particularly the Tier 2 panel tasks.
4. I identified 6 questions for the three agents to determine what exists in the codebase relevant to Tier 2 reduction work.
5. David relayed the questions and received answers from all three agents.

## Agent Responses (Critical New Information)

### Claude Code (CC) — Questions 1-3:
- **No ReductionClaim model exists.** Nearest structure is `MechanismTrace` from CMR pipeline (doc 11). A `ReductionClaim` would be a pre-stored `MechanismTrace` linking a Tier 2 construct to Tier 1 templates.
- **CMR pipeline has no explicit Tier 2 input path**, but Tier 2 claims can enter if treated as "findings to be explained." A cleaner design would add a `reduce_tier2_theory()` entry point — suggested as a Sprint 8 addition.
- **Sprint 0.1–0.3 is DONE** (files in place, not git-committed). Sprint 0 is effectively complete.

### Codex — Questions 4-5:
- **No cross-repo TheoryLevel enum.** Only AE-local `TheoryLevel` with `framework_theory`, `domain_theory`, etc. Drift checker doesn't validate theory-tier enums.
- **No ReductionClaim model anywhere.** Nearest placeholders: `parent_theories` on Theory, `derivation_path` on beliefs, `EPISTEMIC_DERIVATION` / `EPISTEMIC_CROSS_TEMPLATE` constraint types, commented `FindingMechanismLink`.
- **ART/SRT/biophilia in web of belief**: Only 6 persisted beliefs (2 ART, 4 biophilia, 0 SRT). All tagged generically, `beliefs.theory_id` is NULL for all rows.
- **CRITICAL FINDING**: In staging/review artifacts: **1,361 theory-link rows** not yet persisted — **1,251 ART, 102 biophilia, 3 SRT**. These include edge labels like `COHERENCE_SUPPORT` / `CONFIRMS_PREDICTION`. Location: `data/review/tranche80_confirmed_rows.csv`.

### Antigravity — Question 6:
- **Yes**, Panel I–III source docs already contain Tier 2 → Tier 1 connections explicitly.
- Antigravity extracted a **preliminary construct map** to `docs/tier2_construct_map_preliminary.md`:
  - ART: Soft Fascination → T27+T31+T2; Being Away → T23+T29; Extent → T3 (minus T14); Compatibility → T8+T1+T37
  - SRT: Immediate Affective Response → T9+T22; Parasympathetic → T8→T12; Cortisol → T5 reversal
  - Biophilia: Prospect/Refuge → T3+T5; Complexity → T2; Fractal Fluency → T1

---

# KEY SYNTHESIS FROM AGENT RESPONSES

The Tier 2 panels will NOT be working from scratch. They will reconcile:
1. **Top-down**: theoretical decomposition (Antigravity's construct map from doc 09)
2. **Bottom-up**: 1,361 empirical theory-link connections already extracted from papers (Codex's staging data)

This changes the panel methodology: experts reason about the decomposition, then we check against the empirical base, flagging discrepancies. Agreement validates both directions; disagreement is scientifically interesting.

The `ReductionClaim` data structure design is a consequential decision that should be made by expert panel (Panel D-1), not just sketched ad hoc.

---

# WHAT OPUS SHOULD DO NEXT (Priority Order)

## Immediate (This Session or Next)

### 1. Panel D-1: Reduction Claim Architecture (SHORT — ~30 min)
**Purpose**: Design the canonical `ReductionClaim` data structure.
**Inputs**:
- CC's finding that `MechanismTrace` is nearest structure
- Codex's list of adjacent placeholders (`derivation_path`, `EPISTEMIC_DERIVATION`, `FindingMechanismLink`)
- Antigravity's construct map showing what the panels will produce
- The 1,361 staging rows that need a persisted home
**Output**: A Python dataclass spec for `ReductionClaim` that CC implements in Sprint 7.
**Panelists**: Epistemologists and knowledge representation experts — suggest: Clark Glymour (CMU, causal modeling), Patrick Suppes (legacy, formal epistemology), Judea Pearl (UCLA, causal inference), Peter Gärdenfors (Lund, conceptual spaces), William Bechtel (UCSD, mechanistic explanation). Bechtel is particularly relevant because his work on mechanistic explanation directly addresses what it means to "reduce" a theory to component mechanisms.
**Key questions**:
- Should a reduction be a single chain or a DAG (multiple parallel paths)?
- How do we represent "irreducible residual" — the piece a panel says cannot be reduced?
- Should reductions be versioned (they may change as the template library matures)?
- How does a `ReductionClaim` integrate with the existing constraint types in the web of belief?
- What is the relationship between a `ReductionClaim` and the 1,361 staging theory-links?

### 2. Panel V: Social Brain (FULL — ~2 hours equivalent)
**Purpose**: Should Social Brain be promoted to Tier 1? What happens to T19 (social affordance)?
**Panelists** (from doc 09): Lieberman (UCLA), Saxe (MIT), Dunbar (Oxford), Bavelier (Geneva), S. Cacioppo (Baylor, for J. Cacioppo legacy).
**Questions** (from doc 09):
- Promote Social Brain to Tier 1?
- TPJ dual role in spatial reorienting AND social cognition
- Dunbar's number as architectural constraint
- Social enrichment/deprivation as allostatic factor
**Independent of Tier 2 work — can proceed in parallel.**

### 3. Break Tier 2 Panels into Granular Tasks
**After D-1 produces the ReductionClaim spec**, break each panel into:
- T2-A (ART): 4 constructs × reduction claims + irreducible residual assessment + comparison against 1,251 staging ART links
- T2-B (SRT): 3 constructs × reduction claims + comparison against 3 staging SRT links (sparse — panel does most of the work top-down)
- T2-C (Biophilia/Prospect-Refuge): 4+ constructs × reduction claims + comparison against 102 staging biophilia links
Each should have explicit inputs, outputs, dependencies, and estimated effort.

## Downstream (After Above Complete)

### 4. Update Sprint Plan
- Insert `ReductionClaim` model into Sprint 7 task list (new task 7.9)
- Insert `reduce_tier2_theory()` into Sprint 8 task list (new task 8.14)
- Insert staging theory-link persistence into Sprint 5 or 7 (the 1,361 rows need a home)
- Update doc 15 (Global Status Tracker)

### 5. Review Antigravity's Template Encodings
When Antigravity completes Sprint 7.5 (28 templates), review each batch for theoretical accuracy.

### 6. Review CMR Output vs Ulrich Worked Example
When CC completes Sprint 8.13, validate pipeline output against expected predictions from doc 11.

### 7. Theory Referee
On call for CC during Sprint 1 (enum consolidation) and Sprints 7-8 (template encoding, CMR architecture).

---

# CURRENT STATUS OF ALL AGENTS

## Claude Code (CC)
- **Sprint 0**: ✅ DONE (0.1–0.3 complete, not git-committed)
- **Next**: Review Codex migration patches → Sprint 1.1 (claim node extensions) → Sprint 1.2-1.3 (enum consolidation)
- **Needs from Opus**: Theory referee if enum merger raises theoretical questions

## Codex
- **Sprint 0.6**: ✅ DONE (canonical_enums.json + check_enum_drift.py)
- **Sprint 0.7**: ✅ DONE (5 migration scripts, dry-run verified)
- **Next**: Stage migration artifacts for CC review → Sprint 1.4 (drift check after enum changes)
- **Key finding delivered this session**: 1,361 staging theory-links

## Antigravity
- **Sprint 0.0**: ✅ DONE (test suite)
- **Sprint 0.4**: ✅ DONE (stale docs)
- **Sprint 0.5**: ✅ DONE (template alias map for T1-T40; needs T41-T47 update)
- **Next immediate**: Update alias map with T41-T47 (data provided in doc 15)
- **After that**: Idle until Sprint 4b.3 or Sprint 7.5
- **This session**: Extracted preliminary Tier 2 construct map

## Opus (Me)
- **Panel IV**: ✅ DONE (doc 14)
- **Panel D-1**: READY TO RUN (ReductionClaim architecture)
- **Panel V**: READY TO RUN (Social Brain)
- **Tier 2 task breakdown**: BLOCKED on D-1 output
- **Sprint plan update**: BLOCKED on D-1 + Tier 2 breakdown

---

# THE 10 TIER 1 FRAMEWORKS (Unchanged)

1. PP — Predictive Processing
2. SN — Spatial Navigation / Cognitive Mapping
3. DP — Dual-Process Evaluation
4. DT — DMN/TPN Dynamics
5. NM — Neuromodulatory Systems
6. IC — Interoceptive / Constructionist Affect
7. MS — Memory Systems
8. EC — Embodied Cognition
9. CB — Chronobiological Regulation
10. MSI — Multisensory Integration

---

# THE 8 CANONICAL DECISIONS (Unchanged — doc 09 is authoritative)

1. GapType: 8-value enum canonical
2. Template IDs: Short form canonical, alias map for long forms
3. Tier 1 count: 10 frameworks
4. Pathway taxonomy: SUBPERSONAL / PERSONAL_EPISTEMIC / MIXED
5. Chain endpoints: from_variable/to_variable in templates; antecedent/consequent in BN bridge
6. Confidence stack: 4 separate dimensions, never averaged
7. Epistemic certainty: ARCH-4 rank-based canonical
8. Variable names: Reconciliation table from doc 08

---

# TEMPLATE COUNT

- Tier 1 framework-owned: 40 (T1–T40, from Panels I–III)
- Panel IV additions: 7 (T41–T47: 2 NM-owned, 5 cross-framework)
- **Total specified: 47**
- **Total encoded in code: 0** (Sprint 7 not started)

---

# FILE NAMING CONVENTION

`MM-DD_SEQ_Description_VX_Y.ext`
Next sequence number for this date: **17**

---

# PANEL ROADMAP STATUS

| Panel | Status | Notes |
|-------|--------|-------|
| I (Embodied Prediction) | ✅ DONE | Templates T1-T20 |
| II (Neuroscience) | ✅ DONE | Templates T21-T30, added CB framework |
| III (Multimodal/Higher Cog) | ✅ DONE | Templates T31-T40, added MSI framework |
| IV (Cognitive Control & Reward) | ✅ DONE | T41-T47, CC/EF NOT promoted |
| D-1 (ReductionClaim Architecture) | **READY** | Design panel — short job |
| V (Social Brain) | **READY** | Full panel — awaiting David's go-ahead |
| T2-A (ART Reduction) | NOT STARTED | Depends on D-1 output |
| T2-B (SRT Reduction) | NOT STARTED | Depends on D-1 output |
| T2-C (Biophilia/Prospect-Refuge) | NOT STARTED | Depends on D-1 output |

---

# IMPORTANT CONTEXT FOR NEXT INSTANCE

- David was about to leave. He asked for this transfer document specifically because connectivity may drop.
- The proposed work sequence is: D-1 first (short), then Panel V (longer), then Tier 2 task breakdown.
- David has NOT yet given the go-ahead for Panel V — only confirmed it's "ready to run."
- The staging theory-links discovery (1,361 rows, mostly ART) is a significant finding that changes how the Tier 2 panels should work. The next Opus should ensure this is integrated into the panel methodology.
- All project documents (docs 04–15) should be available as uploads. If any are missing, ask David to re-upload or check `/mnt/user-data/uploads/`.

---

*Transfer document V2 created: February 15, 2026*
*Session document count: 13 (docs 04-16)*
