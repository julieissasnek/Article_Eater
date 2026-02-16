# OPUS TRANSFER CONTEXT
## Article Eater Project — Session Handoff
## February 15, 2026
## Give this document to a new Opus chat to continue where we left off.

---

# WHO YOU ARE

You are Opus, the theory architect and manager for David Kirsh's Article Eater project. David is a Professor of Cognitive Science at UC San Diego. You manage three AI agents (Claude Code, Codex, Antigravity) and produce theory-side deliverables that they implement.

Your role: theoretical judgment, expert panel design, mechanistic template specification, CMR pipeline architecture, cross-agent task coordination. You do NOT write production code — CC does that. You produce specs, data structures, worked examples, and naming decisions that CC implements.

David's preferences: proper APA citations with Google Scholar counts, comprehensive explanations, evidence-based approaches, versioned file naming with date-seq prefix (e.g., `02-15_01_`). NEVER use generic filenames. At session end, package outputs into a summary zip and remind David to download.

---

# THE PROJECT

**Article Eater** is a research platform that:
1. Extracts evidence from scientific papers (PDF → structured claims)
2. Integrates claims into a Quinean Web of Belief (coherentist epistemology)
3. Uses Bayesian networks for causal inference
4. **[Being built now]** Uses Compositional Mechanistic Reasoning (CMR) to generate novel testable predictions by composing mechanistic templates across theoretical frameworks

The domain is **cognitive neuroarchitecture** — how built environments affect human cognition, affect, and behavior through measurable neural, physiological, and psychological mechanisms.

---

# WHAT EXISTS IN THE CODEBASE

## Working (Epistemic Tier)
- Web of Belief: 10,653 beliefs, 25,943 constraints, coherence score 0.416
- Extraction pipeline: PDF → claims via pdfplumber + LLM
- Gap predictor: 8 gap types (now canonically unified)
- Bridge warrants: theory-finding connections
- Coherence engine: quadratic constraint satisfaction
- Incremental BN: Beta-Bernoulli updates (NO graphical model inference yet)
- 1,170 papers processed, 37 PDFs, 96 test files (now passing: 2578 pass, 1 fail)

## Not Yet Implemented (Theory Tier + CMR)
- Theory framework models in DB (Sprint 7)
- Mechanistic template library in DB (Sprint 7)
- CMR pipeline (Sprint 8) — 0% implemented
- Research queue service (Sprint 6) — contract only
- Template learning (Sprint 8, Step 8) — deferred

---

# THE 10 TIER 1 FRAMEWORKS

1. **PP** — Predictive Processing
2. **SN** — Spatial Navigation / Cognitive Mapping
3. **DP** — Dual-Process Evaluation
4. **DT** — DMN/TPN Dynamics
5. **NM** — Neuromodulatory Systems
6. **IC** — Interoceptive / Constructionist Affect
7. **MS** — Memory Systems
8. **EC** — Embodied Cognition
9. **CB** — Chronobiological Regulation
10. **MSI** — Multisensory Integration

All 10 have scope declarations, owned variables, and at least one seed template.
Independence matrix is 10×10 symmetric (range 0.2 to 0.9).

---

# DOCUMENTS PRODUCED THIS SESSION

All in `docs/` in the Article Eater repo and in `/mnt/user-data/outputs/`.

| Doc # | Filename | Content |
|-------|----------|---------|
| 04 | `02-15_04_Claude_Code_Master_Sprint_Plan_V1_0.md` | Full sprint plan (Sprints 0-9), task specs, dependency graph |
| 05 | `02-15_05_Ruthless_Repo_Audit_Prompt_V1_0.md` | Audit prompt given to CC and Codex |
| 06 | `02-15_06_Template_Completeness_Audit_Theory_Reference_V1_0.md` | 40-template completeness matrix, prediction generation grammar (8 operations), cross-framework bridging rules (legitimate + illegitimate bridges) |
| 07 | `02-15_07_Sprint7_Theory_Artifacts_V1_0.md` | 10 framework scope declarations as Python dicts, 10×10 independence matrix, 8 seed template encodings as Python dataclasses |
| 08 | `02-15_08_Audit_Synthesis_Recommendations_V1_0.md` | Synthesized CC + Codex audit findings, top 5 fixes, reconciled variable vocabulary, revised sprint ordering |
| 09 | `02-15_09_Canonical_Decisions_Record_V1_0.md` | **AUTHORITATIVE**: 8 binding naming decisions + full panel roadmap for template deepening (Panels IV, V, T2-A, T2-B, T2-C with named experts and "bring to discussion" notes) |
| 10 | `02-15_10_Sprint7_Supplementary_Seed_Templates_V1_0.md` | 4 additional seed templates: T9 (DP), T25 (MS), T8 (EC), T29 (Allostatic Master). Completes all 10 frameworks. |
| 11 | `02-15_11_CMR_Pipeline_Implementation_Architecture_V1_0.md` | Sprint 8 implementation reference: module structure, all data models as Python dataclasses, function signatures for 8 steps, complete worked example (Ulrich 1984 → 7 ranked predictions), 4-week MVP build plan |
| 12 | `02-15_12_Three_AI_Task_Distribution_Plan_V1_0.md` | Task assignments across CC, Codex, Antigravity for all 9 sprints |

**Bundle**: `02-15_Opus_Sprint_Theory_Bundle_V1_3.tar.gz` contains docs 04-11.

---

# THE 8 CANONICAL DECISIONS (All approved by David)

1. **GapType**: `gap_predictor.py` 8-value enum is canonical
2. **Template IDs**: Short form canonical (e.g., `IC_INTEROCEPTIVE_AFFECT_001`), alias map for long forms
3. **Tier 1 count**: 10 frameworks (PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI)
4. **Pathway taxonomy**: SUBPERSONAL / PERSONAL_EPISTEMIC / MIXED (what's coded)
5. **Chain endpoints**: `from_variable`/`to_variable` in templates; `antecedent`/`consequent` only in BN bridge
6. **Confidence stack**: 4 separate dimensions (extraction, statistical, mechanism, epistemic), never averaged
7. **Epistemic certainty**: ARCH-4 rank-based canonical in bridge; `credence` is legacy adapter
8. **Variable names**: Reconciliation table in doc 08 accepted as-is

---

# CURRENT STATUS OF ALL 3 AIs

## Claude Code (CC)
**Assigned**: Sprint 0 Tasks 0.1-0.3
- 0.1: Create `src/queue/`, `src/theory/`, `src/cmr/` with `__init__.py`
- 0.2: Unify GapType enum → `src/epistemic/gap_types.py`, update 3 services, add stubs for `find_critical_question_gaps()` and `find_argument_attack_gaps()`
- 0.3: Update `theory_bootstrap.py` from 8 to 10 frameworks (add CB, MSI)

**Prompt given**: See session transcript. Key instruction: "Read docs/02-15_09_Canonical_Decisions_Record_V1_0.md FIRST."

**After Sprint 0**: Proceeds to Sprint 1 (epistemic core extensions).

## Codex
**Completed**: Cross-repo vocabulary contract (`canonical_enums.json` + `check_enum_drift.py`)
**Assigned**: Sprint 0.7 — Migration adapter scripts for top 5 collisions:
- `migrate_gap_type.py`, `migrate_ci_shape.py`, `migrate_claim_type.py`, `migrate_evidence_type.py`, `migrate_article_type.py`
- Each produces patches/adapters for CC review, not direct changes
- Each includes `test_migration_lossless()` round-trip test

**After Sprint 0**: Periodic drift checks + cross-repo validation at sprint boundaries.

## Antigravity
**Completed**: Test suite fix (2578 passing, 0 collection errors)
**Assigned**: Sprint 0.4-0.5
- 0.4: Update CLAUDE.md (pathway taxonomy, tier list) and IMPLEMENTATION_TASKS.md
- 0.5: Create `template_id_aliases.json` from 3 panel documents

**After Sprint 0**: Sprint 7.5 — encode remaining 28 templates mechanically following seed patterns.

---

# AUDIT FINDINGS (Key Facts)

**From CC's audit** (REPO_AUDIT_REPORT):
- 12 test collection errors → FIXED by Antigravity
- `FindingMechanismLink` is commented-out placeholder → blocks Sprint 8
- Two competing edge type enums (ConstraintType 13 values vs EdgeType 19 values) → Sprint 1 consolidation
- Two competing node type enums (NodeDomain vs NodeTypeFamily) → Sprint 1 consolidation
- CMR spec is 89KB of narrative, 0% implemented → doc 11 provides architecture
- Sprint Plan references paths that don't exist (`src/queue/`, `src/theory/`, `src/cmr/`) → CC creating in Sprint 0.1
- `extracted_by: "claude_manual"` on findings → extraction not yet automated

**From Codex's audit** (Top 25 Cross-Repo Collisions):
- #1 risk: Epistemic certainty model (`credence` vs `rank/warrant_status`) → Decision 7 resolves
- #2 risk: Gap taxonomy (3 competing enums) → Decision 1 resolves
- 4,320 semantic variable tokens across 5 repos, 232 cross-repo drift candidates
- CI wire shape inconsistency (scalar pairs vs object) → Codex building adapter

---

# WHAT OPUS SHOULD WORK ON NEXT

Priority order:

1. **Review any agent outputs** David shares (CC Sprint 0 results, Codex migration scripts, Antigravity template alias map)
2. **Expert panels for template deepening** — Panel IV (Cognitive Control + Reward) and Tier 2 reduction panels are specified in doc 09 but not yet executed. When David is ready, run these panels.
3. **Theory questions from CC** — When CC hits a theoretical judgment call during Sprint 7-8, Opus provides the answer.
4. **Template review** — When Antigravity produces the 28 remaining template encodings (Sprint 7.5), Opus reviews for theoretical accuracy.
5. **CMR pipeline refinement** — As CC implements Sprint 8, Opus answers architecture questions and validates prediction output against the Ulrich worked example.

---

# PANEL ROADMAP (In Canonical Decisions Record, doc 09)

## Future Panels (Not Yet Run)

**Panel IV**: Cognitive Control + Reward — Badre, Schultz, Daw, Braver, Kastner, Miller
→ Question: Promote CC/EF to Tier 1 #11? Reward templates?

**Panel V**: Social Brain — Lieberman, Saxe, Dunbar, Bavelier, S. Cacioppo
→ Question: Promote Social Brain to Tier 1?

**Panel T2-A**: ART Reduction — Berman, R. Kaplan, Hunter, Kahn, Joye, White
→ Question: Express ART claims as Tier 1 mechanistic templates

**Panel T2-B**: SRT Reduction — Ulrich, Berto, Grinde, Ellard
→ Question: Map SRT onto NM templates

**Panel T2-C**: Biophilia/Prospect-Refuge — Beatley (for Kellert), Hildebrand, Salingaros, Altomonte
→ Question: Reduce design theories to mechanistic templates

Each panelist has a "bring to discussion" note specifying unique knowledge they contribute.

---

# KEY TERMINOLOGY

- **CMR**: Compositional Mechanistic Reasoning — the prediction generation system
- **Template**: A formalized causal chain (DAG fragment) with typed links, maturity tags, parameters
- **Bridging quality**: How well-established a cross-level causal link is (HIGH/MEDIUM/LOW)
- **Maturity**: How-possibly → how-plausibly → how-actually (Darden's mechanism discovery stages)
- **Independence matrix**: Framework-pair scores (0.0-1.0) indicating how independent their evidence is
- **Goldilocks framework**: David's research on optimal sensory set-points and complexity preferences
- **Web of belief**: Quinean coherentist network of claims with constraint satisfaction
- **Allostatic master template** (T29): The integrating template — all environmental effects cash out as metabolic budget impacts

---

# FILE NAMING CONVENTION

`MM-DD_SEQ_Description_VX_Y.ext`

Example: `02-15_13_Next_Document_V1_0.md`

Next sequence number for this date: **13**

---

*Transfer document created: February 15, 2026*
*Session document count: 9 (docs 04-12)*
*Bundle: 02-15_Opus_Sprint_Theory_Bundle_V1_3.tar.gz*
