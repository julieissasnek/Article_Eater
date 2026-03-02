# Plan: Extraction Pipeline & Template Overhaul

## Context

RV5 audit scores: extraction pipeline 3.5/10, tagging 3.5/10, contracts 4/10 (now partially fixed), calibration 6.2/10. The core problems: 17.3% garbage direction values (FIXED), 82% missing sample_size, 32% vague antecedents, no image/stimulus fields in templates, weak theory/mechanism/molecule linkage, no validation gate in the pipeline. David's request: fix the extraction prompts, the template schema, the field values via LLM re-discovery, add quality inspection, wire expert panels for unreviewed decisions, and handle images/stimuli properly.

The previous plan (ATLAS System Completeness — overseer, notifications, nightly health, DOI lookup, HITL, pipeline wiring) remains valid but is **deferred** — this plan takes priority because garbage extraction data undermines everything downstream.

---

## Epistemic Principles Integration (Added 2026-03-01)

AG's `docs/EPISTEMIC_PRINCIPLES.md` codifies 10 science-writer norms that govern how ATLAS presents evidence. These are not merely presentation guidelines — they impose **structural requirements on extraction data**. If the extraction pipeline doesn't capture defeat relationships, scope conditions, causal design tiers, and conflict types, then the QA layer cannot compose principle-compliant answers. The 10 principles must therefore be wired into the extraction pipeline at multiple points.

### Principle → Phase Mapping

| # | Principle | Source | Phase 1A (Schema) | Phase 2 (Prompts) | Phase 3 (LLM Discovery) | Phase 1B (Validator) |
|---|-----------|--------|-------------------|-------------------|------------------------|---------------------|
| P1 | Defeasible Warrant | Pollock | `defeat_relationships[]` field | Extract rebutting/undercutting defeats | Infer defeat links from contradictory findings | Rule: ≥1 defeat check for high-credence claims |
| P2 | Foundherentism | Haack | `justification_status` enum | Classify each finding as GROUNDED vs COHERENT_ONLY | Flag coherent-only clusters across articles | Warning if >30% findings COHERENT_ONLY |
| P3 | Severe Testing | Mayo | `defeater_search_status` field | "List any null results, failed replications, or boundary conditions reported" | Pass 3D: defeater search across corpus | Rule: empirical findings must note defeaters or mark `defeater_search: not_attempted` |
| P4 | Scope Conditions | Cartwright | `scope_conditions{}` structured field | "Specify setting, population, climate, duration, measurement type" | Infer missing scope from methods sections | Rule: scope_conditions required for empirical; ≥2 dimensions filled |
| P5 | Causal Design Tier | Pearl | `causal_tier` enum | "Classify: EXPERIMENTAL, QUASI_EXPERIMENTAL, CORRELATIONAL, REVIEW" | Infer tier from methods description | Rule: causal language must match tier (no "causes" for CORRELATIONAL) |
| P6 | Source Quality | Longino+Cartwright | `source_quality_indicators{}` | "Note: pre-registration, blinding, independence from prior work" | Compute quality-weighted credence | Rule: independence flag required |
| P7 | Progressive Disclosure | Simon | (presentation layer, not extraction) | N/A | N/A | N/A |
| P8 | Multi-Dimensional Coherence | Simon+Thagard | `gap_type` enum on findings | Extract gap indicators per finding | Classify gaps (mediation, mechanism, boundary, direction, validation) | Rule: gap_type populated when coherence < 0.5 |
| P9 | Level-Specific Standards | Cartwright+Haack | `epistemic_level` enum | "Classify claim level: OBSERVATIONAL, EMPIRICAL, INTERMEDIATE, THEORETICAL" | Infer level from claim content | Rule: credence thresholds vary by level |
| P10 | Conflict Typology | Cartwright | `conflict_type` enum | "If findings conflict, classify: CONTRADICTS, WEAKENS, BOUNDARY_VIOLATION, DIRECTION_CONFLICT, PRECISION_DIFFERENCE" | Type conflicts across existing extraction corpus | Rule: raw "contradicts" flagged for typing |

### What This Changes in Each Phase

**Phase 1A additions**: 6 new schema fields — `defeat_relationships[]`, `justification_status`, `defeater_search_status`, `scope_conditions{}`, `causal_tier`, `source_quality_indicators{}`. The `conflict_type` and `epistemic_level` and `gap_type` fields already exist partially in the web of belief but must be extractable from articles.

**Phase 2 additions**: The validation prompt suffix (appended to all families) grows from 5 checks to 10:
```
6. scope_conditions has ≥2 dimensions filled for empirical findings
7. causal_tier is specified and causal language matches (no "X causes Y" for CORRELATIONAL)
8. At least one defeater or null result noted, OR defeater_search marked "none_reported"
9. justification_status is GROUNDED (has empirical anchor) not just COHERENT_ONLY
10. conflict_type is specified when findings disagree with prior extractions on same IV→DV
```

**Phase 3 additions**: New Pass 3D — Principle Compliance Inference (~2 hrs)
- Input: all 1,043 articles
- For each: infer `causal_tier` from methods, classify `justification_status`, fill `scope_conditions`, search for `defeat_relationships` across corpus
- This pass runs AFTER Passes 3A-3C since it builds on their outputs

**Phase 4 addition**: Panel E — Epistemic Principle Compliance Review
- Panelists: Pollock (defeasibility), Haack (grounding), Mayo (severe testing), Cartwright (scope)
- Question: "Review 20 sample extractions. Are the principle-compliance fields correctly populated? Which principles are hardest to operationalize at extraction time?"

---

## Parallelism Map

```
TIME ──────────────────────────────────────────────────────────►

TRACK A (CW):  [Phase 1A: Schema]──►[Phase 3A: LLM field discovery]──►[Phase 5: Re-extract]
                     │                        │
TRACK B (CW):  [Phase 1B: Validator gate]     │
                     │                        │
TRACK C (CW):  [Phase 2: Prompt v3]───────────┘
                     │
TRACK D (AG):  [Phase 2D: AG prompt review]──►[Phase 3D: AG molecule/theory linking]
                     │
TRACK E (CW):  [Phase 4: Expert panels] ← runs after Phase 1+2 complete, informs Phase 5

Phase 6 (verification) runs after Phase 5 completes.
```

**Phases 1A, 1B, 2, and 4-prep can all run in parallel.** Phase 3 requires Phase 1A (schema) and Phase 2 (prompts) to be done. Phase 5 requires Phase 3 + Phase 4 panel decisions. Phase 6 is sequential at the end.

---

## Phase 1A: Template Schema Upgrade (~2 hrs) — CW, PARALLEL

**Problem**: Current extraction templates lack fields for stimuli, images, vision attributes, molecule linkage, and success conditions. The `findings` array captures individual claims but the template-level metadata is thin.

**Files to modify**:
- `contracts/schemas/extraction_quality_rules.json` — add rules for new fields
- `src/extraction/revised_prompts_v2.py` → will be replaced in Phase 2 but schema must be defined first

**New template-level fields** (added to extraction JSON schema):

```
stimulus_description: {          # structured, not free text
  primary_type: enum[visual_scene, soundscape, thermal, olfactory, spatial, lighting, material, mixed],
  components: [{name, category, essential: bool}],
  equivalence_class_id: str,     # links to decision_tree_equivalence_classes.json
  delivery_method: enum[in_situ, VR, photo, video, audio, imagined],
  duration_seconds: float|null
}
stimulus_images: [{              # NEW — currently not extracted at all
  description: str,
  figure_ref: str,               # e.g. "Figure 2a"
  image_type: enum[photo, rendering, diagram, floor_plan, graph],
  vision_attributes: {attr_id: float}  # links to 33-attribute taxonomy
}]
theory_commitments: [{           # stronger than current theory_links
  theory_name: str,
  framework_id: str|null,        # links to t1_frameworks
  commitment_type: enum[tests, extends, contradicts, assumes, proposes],
  specific_claim: str
}]
mechanism_chain: [{              # already in some templates, now mandatory
  step: int,
  from_construct: str,
  to_construct: str,
  mechanism_type: enum[neural, perceptual, cognitive, affective, behavioral, physiological],
  evidence_strength: enum[direct, indirect, theoretical, assumed]
}]
molecule_ids: [str]              # links to rasa_attractors.json molecule vocabulary
success_conditions: {            # meta-field: what would make this extraction "good"?
  min_findings: int,
  required_fields: [str],
  theory_link_expected: bool,
  mechanism_expected: bool
}
```

**Deliverable**: Updated JSON schema file at `contracts/schemas/extraction_template.v2.schema.json`

---

## Phase 1B: Make Validator Blocking + Overseer Wiring (~1 hr) — CW, PARALLEL with 1A

**Problem**: `extraction_field_validator.py` (680 LOC, 50+ rules) exists but is advisory. Articles scoring below 0.75 are flagged but not blocked from integration.

**Changes**:
- `src/qa/extraction_field_validator.py`: Add `validate_and_gate(extraction_path) → (pass: bool, score: float, violations: list)` — returns False if score < 0.75
- `scripts/scheduled_pipeline.py` extraction stage: after Gemini extraction, call `validate_and_gate()`. If fail → move to `data/extractions/needs_repair/` + queue notification
- `src/services/overseer.py`: INV-10 (QA_QUALITY_GATE) already wired — verify it checks `needs_repair/` count
- Add 5 tests for the gating logic

---

## Phase 2: Extraction Prompt Overhaul — `revised_prompts_v3.py` (~4 hrs) — CW, PARALLEL with Phase 1

**Problem**: Current prompts (`revised_prompts_v2.py`, 781 lines) produce:
- Vague antecedents (32%): "the environment" instead of "open-plan office with 45 dB background noise"
- Missing sample sizes (82%): prompt asks but doesn't insist
- Weak theory links: free-text string instead of structured commitment
- No stimulus image extraction
- No mechanism chain enforcement for empirical papers
- Direction field allowed free text (now fixed to 4 canonical values, but prompt should enforce)

**New file: `src/extraction/revised_prompts_v3.py`** (~1,000 lines)

Key prompt changes by family:

**All families**:
- Direction field: explicit enum constraint `"direction": "increase" | "decrease" | "no_effect" | "mixed"` — no other values accepted
- Antecedent field: "Describe the specific environmental condition. Include measurable quantities where reported (e.g., '65 dB pink noise', '2700K LED lighting at 300 lux', 'room with 3 potted plants visible'). Do NOT use vague terms like 'the environment' or 'the condition'."
- Consequent field: "Use the closest term from this vocabulary: [inject outcome_vocab terms for relevant domains]"
- Theory links: structured object with commitment_type enum, not free text
- Mechanism: mandatory for empirical, encouraged for all others

**EMPIRICAL family** additions:
- `stimulus_description` with structured sub-fields (type, components, delivery_method)
- `stimulus_images`: "List any figures showing the experimental stimulus or environment. For each, note the figure number and describe what it depicts."
- `sample_size`: "This field is REQUIRED. If not explicitly stated, estimate from the methods section and mark as estimated."
- `instruments_used`: "Name the specific measurement instrument (e.g., 'PANAS', 'WHO-5', 'Visual Analogue Scale'). Do not describe the construct; name the tool."

**SYNTHESIS family** additions:
- `included_studies_count` (the k in meta-analysis)
- `heterogeneity_metrics` (I², τ², Q)
- Better handling of pooled effects vs. individual study findings

**THEORETICAL family** additions:
- `mechanism_chain` now mandatory (was optional)
- `testable_predictions` with falsifiability assessment
- `bridge_warrants` linking to existing web-of-belief propositions

**QUALITATIVE family** additions:
- `transferability_context` (what settings/populations)
- `saturation_evidence` (did they reach saturation?)

**Validation prompt suffix** (appended to all families):
```
Before returning your JSON, check:
1. Every finding has a non-vague antecedent (no "the environment", "the condition", "exposure")
2. Every finding has direction ∈ {increase, decrease, no_effect, mixed}
3. sample_size is filled for every empirical finding
4. At least one theory_commitment if the paper mentions ANY theoretical framework
5. mechanism_chain has at least 2 steps for empirical papers with causal claims
6. scope_conditions has ≥2 dimensions filled (setting, population, climate, duration, measurement) [P4 Cartwright]
7. causal_tier is set AND causal language matches tier (no "X causes Y" for CORRELATIONAL designs) [P5 Pearl]
8. At least one defeater/null result noted, OR defeater_search: "none_reported" [P3 Mayo]
9. justification_status is classified (GROUNDED vs COHERENT_ONLY vs EXPERIENTIAL_CLAIM) [P2 Haack]
10. conflict_type specified when findings disagree with known prior results on same IV→DV [P10 Cartwright]
```

---

## Phase 3: LLM-Powered Field Value Discovery & Cleanup (~6 hrs) — CW, after Phases 1A+2

**Problem**: 1,043 existing extractions have dirty/missing field values. Re-extracting all of them is expensive (~$15-30 in API costs, ~20 hours of Gemini time). For many fields, we can surgically fix values without full re-extraction.

**Approach**: Three targeted LLM passes over existing extractions:

### Pass 3A: Antecedent Refinement (~2 hrs)
- Input: findings where antecedent is flagged as vague by validator (score < 0.5 on antecedent rules)
- LLM prompt: "Given this paper title, abstract, and the current vague antecedent '{antecedent}', rewrite it to be specific and measurable. Include quantities, materials, and conditions where possible."
- Batch: ~3,300 findings across ~400 articles
- Output: updated antecedent values in extraction JSONs

### Pass 3B: Sample Size Inference (~1.5 hrs)
- Input: findings where sample_size is null
- LLM prompt: "Given this paper's participants section: '{participants}', what is the sample size for this finding? If the paper reports multiple groups, give the relevant group size."
- Batch: ~27,000 findings across ~850 articles
- Output: sample_size values (marked `"sample_size_source": "inferred"`)

### Pass 3C: Theory/Molecule/Instrument Linking (~2.5 hrs)
- Input: all 1,043 articles
- LLM prompt: "Given this paper's extracted findings and these reference vocabularies [inject: t1_frameworks list, molecule vocabulary, instrument registry], identify: (1) which theoretical frameworks this paper tests, extends, or assumes; (2) which molecules (perceptual-cognitive patterns) are relevant; (3) which measurement instruments were used."
- Output: populated `theory_commitments[]`, `molecule_ids[]`, `instruments_used[]`

### Pass 3D: Epistemic Principle Compliance (~2 hrs) — NEW, added 2026-03-01
- Input: all 1,043 articles (runs after Passes 3A-3C complete)
- **Causal tier inference**: From methods section, classify each finding as EXPERIMENTAL / QUASI_EXPERIMENTAL / CORRELATIONAL / REVIEW. Check that existing causal language in the extraction matches tier (flag "X causes Y" on correlational findings).
- **Scope condition fill**: From methods, extract setting type, population, climate/geography, exposure duration, measurement type. Structured output per Cartwright P4.
- **Justification status**: For each finding, determine if it's GROUNDED (has independent empirical anchor), COHERENT_ONLY (supported by theoretical fit but no direct observation), or EXPERIENTIAL_CLAIM (direct observation, no theoretical framing). Per Haack P2.
- **Defeat relationship search**: For each high-credence finding (≥0.70), search the corpus for contradicting findings on the same IV→DV pair. Classify any hits as REBUTTING (attacks conclusion) or UNDERCUTTING (attacks method). Per Pollock P1 and Mayo P3.
- **Conflict typing**: Where findings on the same IV→DV disagree, classify as CONTRADICTS, WEAKENS, BOUNDARY_VIOLATION, DIRECTION_CONFLICT, or PRECISION_DIFFERENCE. Per Cartwright P10.
- Batch: full corpus, but only high-priority fields per article (not full re-extraction)
- Output: populated principle-compliance fields in extraction JSONs

**Quality control**: After each pass, re-run validator. Compare before/after scores. Sample 20 articles manually for spot-check.

---

## Phase 4: Expert Panels (~3 hrs total) — CW, can START after Phase 1A, FINALIZE before Phase 5

Four focused panels using `src/services/ai_panel_resolver.py`:

### Panel A: Template Schema Review (~45 min)
- **Panelists**: methodologist (Shadish/Cook tradition), environmental psychologist (Kaplan tradition), meta-scientist (Ioannidis tradition)
- **Question**: "Review the v2 extraction template schema. Are the new fields (stimulus_description, stimulus_images, theory_commitments, mechanism_chain, molecule_ids, success_conditions) well-defined? Are any fields missing? Are any over-engineered?"
- **Input**: `contracts/schemas/extraction_template.v2.schema.json`

### Panel B: Extraction Quality Thresholds (~45 min)
- **Panelists**: psychometrician, information scientist, data quality specialist
- **Question**: "Review the 50+ extraction quality rules. Are the severity levels (critical/error/warning) correctly assigned? Is the 0.75 threshold for blocking appropriate? Should any rules be added/removed?"
- **Input**: `contracts/schemas/extraction_quality_rules.json`

### Panel C: Theory-Molecule Linkage (~45 min)
- **Panelists**: environmental psychology theorist, cognitive scientist, neuroaesthetics researcher
- **Question**: "Review the molecule vocabulary (rasa_attractors.json) and t1_frameworks list. Is the mapping between theories and molecules coherent? Are there major theories missing?"
- **Input**: `rasa_attractors.json`, t1_frameworks from web of belief

### Panel E: Epistemic Principle Compliance (~45 min) — NEW, added 2026-03-01
- **Panelists**: Pollock (defeasible reasoning), Haack (foundherentism), Mayo (severe testing), Cartwright (causal scope)
- **Question**: "Review 20 sample extractions that have been enriched with principle-compliance fields (causal_tier, scope_conditions, justification_status, defeat_relationships, conflict_type). Are these fields correctly populated? Which principles are hardest to operationalize at extraction time? Are there systematic biases (e.g., over-classifying as GROUNDED, under-reporting defeaters)?"
- **Input**: 20 extraction JSONs (5 per family: empirical, synthesis, theoretical, qualitative) with Pass 3D fields populated

### Panel D: Vision Attribute Taxonomy (~45 min)
- **Panelists**: vision scientist, computational aesthetics researcher, environmental psychologist
- **Question**: "Review the 33-attribute taxonomy (21 original + 12 new from Kirsh decision tree method). Are the new attributes (vegetation segmentation, scene depth, visual complexity, etc.) well-defined and implementable? Any redundancies or gaps?"
- **Input**: `data/attributes/causal_theoretic_image_attributes.json`

---

## Phase 5: Full Re-Extraction of Priority Articles (~8 hrs) — CW+AG, after Phases 3+4

Not all 1,043 articles need full re-extraction. Strategy:

### Tier 1: Re-extract with v3 prompts (~200 articles, ~$5)
- The 391 articles scoring below 0.75 on quality validator
- Use `revised_prompts_v3.py` with all new fields
- Run validator immediately after; target >0.85 mean score

### Tier 2: Surgical LLM updates only (~600 articles)
- Articles scoring 0.75-0.89 — already decent, just need the new fields filled
- Run Phase 3 passes (antecedent refinement, sample size, theory/molecule linking) — no full re-extraction

### Tier 3: Leave as-is (~250 articles)
- Articles scoring >0.89 — add new fields via Phase 3 passes but don't re-extract findings

### AG coordination (via COORDINATION.md):
- AG runs Tier 1 re-extraction batches (it has Gemini API access and batch infrastructure from EN-0C)
- CW runs Tier 2/3 surgical updates and quality validation

---

## Phase 6: Integration Testing & Verification (~2 hrs) — CW, sequential

1. **Gold standard test**: Select 50 articles spanning all 5 families. Manually verify extraction quality against original PDFs (where available). Target: >0.90 mean quality score.
2. **Schema compliance**: Validate all 1,043 extraction JSONs against `extraction_template.v2.schema.json`
3. **Cross-reference integrity**: All instrument names → registry IDs, all molecule_ids → rasa_attractors.json, all theory framework IDs → t1_frameworks
4. **Pipeline end-to-end**: Extract 5 new test papers through full pipeline (discovery → triage → extraction → validation gate → approval → integration). Verify all stages work.
5. **AESHI re-score**: Run full system health assessment. Target: extraction sub-score from 3.5/10 → 7+/10

---

## Parallel Execution Summary

| Track | Phase | Owner | Can start | Depends on | Est. hours |
|-------|-------|-------|-----------|------------|-----------|
| A | 1A: Schema upgrade | CW | Immediately | — | 2.5 (+0.5 for principle fields) |
| B | 1B: Validator gate | CW | Immediately | — | 1.5 (+0.5 for principle rules) |
| C | 2: Prompt v3 | CW | Immediately | — | 5 (+1 for principle checks) |
| D | 4-prep: Panel briefs | CW | Immediately | — | 1.5 (+0.5 for Panel E brief) |
| E | 4: Run panels (A-E) | CW | After 1A | 1A (schema to review) | 4 (+1 for Panel E) |
| F | 3: LLM field discovery (3A-3D) | CW | After 1A + 2 | Schema + prompts | 8 (+2 for Pass 3D) |
| G | 5: Re-extraction | CW+AG | After 3 + 4 | Clean fields + panel decisions | 8 |
| H | 6: Verification | CW | After 5 | Everything | 2 |

**Critical path**: 1A (2.5h) → 3 (8h) → 5 (8h) → 6 (2h) = **20.5 hours minimum**
**With parallelism**: Phases 1A, 1B, 2, 4-prep all run simultaneously in first sprint (~5h wall time). Then 3+4 overlap (~8h). Then 5 (~8h). Then 6 (~2h). **Total wall time: ~23 hours across 4-5 sessions.**

---

## Files Summary

| File | Action | Est. Lines |
|------|--------|-----------|
| `contracts/schemas/extraction_template.v2.schema.json` | CREATE — includes 6 principle-compliance fields | ~250 |
| `contracts/schemas/extraction_quality_rules.json` | MODIFY — add new field rules + principle checks | +80 |
| `src/extraction/revised_prompts_v3.py` | CREATE — 10-check validation suffix (5 original + 5 principle) | ~1,200 |
| `src/qa/extraction_field_validator.py` | MODIFY — add gating logic + principle violation rules | +80 |
| `scripts/scheduled_pipeline.py` | MODIFY — wire validator gate | +30 |
| `scripts/llm_field_discovery.py` | CREATE — 4 surgical LLM passes (3 original + Pass 3D principle compliance) | ~550 |
| `scripts/run_panels_extraction.py` | CREATE — 5 panel consultations (4 original + Panel E) | ~250 |
| 1,043 extraction JSONs in `data/extractions/` | MODIFY — field updates + principle compliance fields | varies |

---

## Key Design Decisions

| ID | Decision | Rationale | Risk |
|----|----------|-----------|------|
| D1 | Surgical LLM passes over full re-extraction | 3x cheaper, 4x faster, preserves human-verified edits | Medium — may miss cross-field inconsistencies |
| D2 | Tiered re-extraction (200/600/250 split) | Focus effort where quality is lowest | Low — validator scores guide the tiers objectively |
| D3 | Prompt v3 as new file, not edit of v2 | Preserves v2 for comparison and rollback | Low |
| D4 | Panels review schema before re-extraction | Expert input prevents schema churn after 1,043 articles processed | Low — delays Phase 5 by ~1 session |
| D5 | stimulus_images as structured field with vision_attributes | Connects image extraction pipeline (IMG-1) to per-article data | Medium — requires IMG-1 PDFs (currently blocked) |
| D6 | Direction restricted to 4 canonical values at prompt level | Belt-and-suspenders with validator; prevents garbage at source | Low |

---

## Verification Plan

1. Validator gate test: submit 3 bad extractions, confirm they get routed to `needs_repair/`
2. Prompt v3 test: extract 10 articles (2 per family) with v3 prompts, compare quality scores to v2
3. LLM field discovery test: run all 3 passes on 20 articles, manually verify accuracy
4. Panel outputs: review panel recommendations, integrate accepted changes
5. Re-extraction spot check: sample 30 re-extracted articles, verify improvement
6. AESHI delta: extraction sub-score should increase from 3.5/10 to 7+/10
