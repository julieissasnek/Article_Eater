# CANONICAL DECISIONS RECORD
## Article Eater — Approved by David, February 15, 2026
## ALL AGENTS: Treat this document as authoritative. Do not deviate.

---

## Decision 1: GapType Enum
**CANONICAL**: `gap_predictor.py` 8-value enum
```
MEDIATION, MECHANISM, BOUNDARY, DIRECTION, INTERACTION,
VALIDATION, UNJUSTIFIED_EDGE, CRITICAL_QUESTION, ARGUMENT_ATTACK
```
All other services (`voi_search.py`, `discovery_funnel.py`) must import this enum.
Stub implementations required for `find_critical_question_gaps()` and `find_argument_attack_gaps()`.

## Decision 2: Template IDs
**CANONICAL**: Short form from summary tables (e.g., `IC_INTEROCEPTIVE_AFFECT_001`)
- Create alias map for long forms (e.g., `IC_INTEROCEPTIVE_AFFECT_CONSTRUCTION_001`)
- Template 31 = `AUD_SCENE_ANALYSIS_001` (Panel III final, not Panel II proposed)

## Decision 3: Tier 1 Framework Count
**CANONICAL**: 10 frameworks
1. PP — Predictive Processing
2. SN — Spatial Navigation / Cognitive Mapping
3. DP — Dual-Process Evaluation
4. DT — DMN/TPN Dynamics
5. NM — Neuromodulatory Systems
6. IC — Interoceptive / Constructionist Affect
7. MS — Memory Systems
8. EC — Embodied Cognition
9. CB — Chronobiological Regulation *(added by Panel II)*
10. MSI — Multisensory Integration *(added by Panel III)*

Update `theory_bootstrap.py` from 8 to 10.

## Decision 4: Pathway Taxonomy
**CANONICAL**: `SUBPERSONAL / PERSONAL_EPISTEMIC / MIXED`
- This is what's implemented in `pathway_classifier.py` and `web_of_belief.py`
- Update `CLAUDE.md` and `IMPLEMENTATION_TASKS.md` to match
- Retire `EXPLICIT / IMPLICIT_COGNITIVE / IMPLICIT_PHYSIOLOGICAL / MIXED` from all docs

## Decision 5: Causal Chain Endpoint Naming
**CANONICAL**:
- In template data structures: `from_variable` / `to_variable`
- In BN bridge layer only: `antecedent` / `consequent` / `mediators`
- Adapter converts between them at the bridge boundary

## Decision 6: Confidence/Quality Stack
**CANONICAL**: Four separate dimensions, never averaged:
1. `extraction_confidence` — How well did AI extract this from the paper?
2. `statistical_confidence` — p-value, CI, effect size (the paper's own numbers)
3. `mechanism_confidence` — Bridging quality + maturity from template chain
4. `epistemic_confidence` — Entrenchment in web of belief (emergent, not assigned)

Legacy field `ae_confidence` maps to `extraction_confidence`.

## Decision 7: Epistemic Certainty Model
**CANONICAL**: ARCH-4 rank-based model in all bridge payloads
- `rank`, `neg_rank`, `warrant_status` are the canonical fields
- `credence` retained as read-only legacy adapter inside AE only
- No new code should write to `credence`

## Decision 8: Theory-Tier Variable Names
**CANONICAL**: Accept reconciliation table from doc 08 as written:
- 9 variables match existing code fields — use as-is
- ~20 new variables created by theory tier — use names from Sprint 7 Theory Artifacts (doc 07)
- 3 overlaps resolved by level distinction:
  - `environment_factors` = extraction-level field (keep)
  - `environmental_threat_cues` = template-level theoretical variable (new)
  - `environmental_legibility` = EC framework variable (new, overlaps SN; independence matrix = 0.5)

---

## Reference Documents (in order of authority)
1. **This file** — naming decisions
2. `02-15_07_Sprint7_Theory_Artifacts_V1_0.md` — framework scopes, independence matrix, seed encodings
3. `02-15_06_Template_Completeness_Audit_Theory_Reference_V1_0.md` — template completeness, prediction grammar, bridging rules
4. `02-15_08_Audit_Synthesis_Recommendations_V1_0.md` — full audit synthesis
5. `02-15_04_Claude_Code_Master_Sprint_Plan_V1_0.md` — sprint structure

---

---

# CANONICAL ROADMAP: TEMPLATE LIBRARY DEEPENING

## Methodology

All template filling uses the **expert panel discussion method**: assemble 4-6 leading researchers with complementary expertise, have them discuss until they reach consensus on mechanistic claims, causal chains, parameter ranges, and scope conditions. Critical instruction: each panelist should share knowledge they believe the other experts may not have, so the discussion produces genuine knowledge exchange rather than parallel monologues.

## Phase 1: Tier 1 Remaining 28 Templates (Sprint 7)

**Method**: Mechanical encoding — information already exists in Panel I-III documents. CC or Antigravity encode following the 12 seed template patterns.

**No new panels needed.** All 40 templates are specified in narrative form.

## Phase 2: Tier 1.5 Promotion Decisions (Post-Sprint 7)

### Panel IV: Cognitive Control & Reward

**Question**: Should Cognitive Control/Executive Function be promoted to Tier 1 #11? Should Reward/Valuation get its own templates?

**Panelists**:
- **David Badre** (Brown) — hierarchical control, rostro-caudal PFC organization. Already consulted in Panel III.
- **Wolfram Schultz** (Cambridge) — reward prediction error, dopaminergic signaling. Foundational work on RPE that connects to T17 (dopaminergic novelty). *Bring to discussion*: how RPE in naturalistic environments differs from lab paradigms; the distinction between wanting (incentive salience) and liking (hedonic impact) in architectural experience.
- **Nathaniel Daw** (Penn) — model-based vs model-free decision making, reinforcement learning theory. *Bring to discussion*: whether architectural navigation uses model-based (cognitive map) vs model-free (habitual route) strategies, and what determines the switch between them. This directly connects T3 (cognitive map) to T37 (ecological rationality).
- **Todd Braver** (WashU) — dual mechanisms of cognitive control (proactive vs reactive). *Bring to discussion*: proactive control in predictable buildings vs reactive control in surprising ones — this is the executive function analogue of the Goldilocks principle. How PFC metabolic cost (T38) interacts with sustained vs transient control demands.
- **Sabine Kastner** (Princeton) — attention and thalamic gating. *Bring to discussion*: thalamic pulvinar's role in environmental attention that neither the cholinergic gating template (T26) nor the attentional demand template (T4) currently captures — the "spotlight" vs "floodlight" distinction in spatial attention.
- **Earl Miller** (MIT) — working memory and prefrontal function. Already consulted in Panel III. *Bring to discussion*: his recent work on gamma/beta bursts and WM — whether architectural WM load (T36) could be measured via non-invasive EEG in ecological settings.

### Panel V: Social Brain / Social Cognition

**Question**: Should Social Brain be promoted to Tier 1? T19 (social affordance) is currently cross-framework — does it need its own home?

**Panelists**:
- **Matthew Lieberman** (UCLA) — social cognitive neuroscience, default mode and social cognition. *Bring to discussion*: why social cognition shares neural substrate with DMN (T27 dmPFC subsystem) — is this coincidence or deep architectural constraint?
- **Rebecca Saxe** (MIT) — theory of mind, TPJ function. *Bring to discussion*: TPJ's dual role in spatial reorienting AND social cognition — this may explain why certain spatial layouts facilitate or inhibit social interaction at the neural level.
- **Robin Dunbar** (Oxford) — social brain hypothesis, group size constraints. *Bring to discussion*: Dunbar's number as an architectural constraint — how many people can a space support socially before the social brain is overwhelmed? This gives T19 its quantitative parameters.
- **Daphne Bavelier** (Geneva) — attention, neuroplasticity, environmental enrichment. *Bring to discussion*: how enriched vs impoverished social environments produce measurable neural differences, connecting the social dimension to the allostatic framework (T29).
- **John Cacioppo's legacy work** (Chicago, deceased) — loneliness and social neuroscience. Reference his published framework on how architectural isolation produces measurable neuroendocrine consequences. Represented by **Stephanie Cacioppo** (now at Baylor) who continues the research program. *Bring to discussion*: loneliness as an allostatic stressor — isolated architectural designs have neuroendocrine cost measurable via cortisol and inflammatory markers.

## Phase 3: Tier 2 Theory Reduction (Post-Sprint 8)

Each Tier 2 theory gets a mini-panel. The question is NOT "is this theory valid?" but "express this theory's claims AS mechanistic templates using Tier 1 vocabulary."

### Panel T2-A: Attention Restoration Theory

**Goal**: Show how ART's constructs map onto Tier 1 mechanisms.
- "Soft fascination" → DMN re-engagement (T27) + low ASA demand (T31) + moderate visual PE (T2)
- "Being away" → context shift → hippocampal remapping (T23) + allostatic demand reduction (T29)
- "Extent" → cognitive map engagement (T3) without navigational stress (T14)
- "Compatibility" → affordance match (T8) + low PE (T1) + ecological rationality (T37)

**Panelists**:
- **Marc Berman** (Chicago) — computational approaches to ART, fractal dimension studies. *Bring to discussion*: his quantitative work linking fractal dimension to restoration — does this validate the PP spectral match template (T1) as ART's mechanism?
- **Rachel Kaplan** (Michigan, emerita) — co-originator of ART. *Bring to discussion*: what she thinks ART claims that CANNOT be reduced to component mechanisms — the irreducible core, if any.
- **MaryCarol Hunter** (Michigan) — nature dose-response research. *Bring to discussion*: her dose-response data (20-minute nature exposure for cortisol reduction) — how this constrains the temporal parameters of restoration templates T16 and T27.
- **Peter Kahn** (U Washington) — technological nature, nature contact hierarchy. *Bring to discussion*: his studies showing real nature > nature videos > no nature — this tests whether the mechanism is really PP spectral match (T1, which should work for videos too) or something requiring embodied presence (T8).
- **Yannick Joye** (ISM Dortmund) — fractal fluency, biophilic design mechanisms. *Bring to discussion*: his work explicitly connecting fractal architecture to processing fluency — the bridge between PP and ART.
- **Mathew White** (U Exeter) — BlueHealth project, blue space benefits. *Bring to discussion*: whether blue space restoration uses different mechanisms than green space — if so, ART as a unified theory needs revision.

### Panel T2-B: Stress Reduction Theory

**Goal**: Map SRT onto NM templates (T5, T6, T7) and the allostatic master (T29).
- Ulrich's "immediate affective response" → T9 (implicit evaluation) + T22 (rapid gist)
- "Parasympathetic activation" → T8 (postural) → T12 (interoceptive) → affect
- "Cortisol reduction" → T5 reversal pathway

**Panelists**:
- **Roger Ulrich** (Chalmers) — originator of SRT. *Bring to discussion*: what he considers the irreducible mechanism of SRT — is it really just the NM threat pathway (T5) running in reverse?
- **Berto Raffaello** (U Valle d'Aosta) — visual preference and restoration. *Bring to discussion*: the studies showing restoration occurs even for preferred urban scenes — this challenges the nature-specificity of SRT.
- **Bjorn Grinde** (Norwegian Institute of Public Health) — evolutionary mismatch theory. *Bring to discussion*: his framework for quantifying evolutionary mismatch — which gives the cultural calibration template (T15) its evolutionary grounding.
- **Colin Ellard** (Waterloo) — psychogeography, urban neuroscience, physiological measurement. *Bring to discussion*: his ambulatory EDA/HRV studies in real urban environments — empirical data that could parameterize T5 and T29 in ecological rather than laboratory settings.

### Panel T2-C: Biophilia / Prospect-Refuge / Pattern Language

**Goal**: Reduce these design theories to mechanistic templates.

**Panelists**:
- **Stephen Kellert's legacy** (Yale, deceased) — biophilic design framework. Represented by **Tim Beatley** (UVA) who continues biophilic cities work. *Bring to discussion*: which of Kellert's 72 biophilic attributes have actual mechanistic backing vs which are aesthetic preferences.
- **Grant Hildebrand** (U Washington) — prospect-refuge in architecture. *Bring to discussion*: his specific spatial metrics for prospect (vista >6m) and refuge (overhead plane <3m) — these give quantitative parameters for templates combining T3 (spatial navigation) with T5 (threat).
- **Nikos Salingaros** (U Texas San Antonio) — mathematical architecture, pattern language formalization. *Bring to discussion*: his computational complexity measures for architecture — do they predict the same outcomes as the PP Goldilocks template (T2)?
- **Sergio Altomonte** (Louvain) — environmental quality, multisensory architecture. *Bring to discussion*: his IEQ research showing how thermal, acoustic, visual, and air quality interact multiplicatively, not additively — this directly challenges the summation assumption in T29.

## Phase 4: Tier 3 Design Heuristics (Post-Sprint 9)

Lowest priority. Practitioner rules traced back through Tier 2 → Tier 1 chains.
No panels needed — this is mechanical derivation from the template library.

---

*Approved: David Kirsh, 2026-02-15*
