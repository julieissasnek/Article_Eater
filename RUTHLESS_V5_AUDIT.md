# RUTHLESS V5 — Full-Repo Audit

*Created: 2026-02-28 by DK request*
*Status: ACTIVE — Execute immediately*

---

## Purpose

After a massive sprint of new code, schemas, frameworks, calibrations, and design decisions by both AG and CW — audit everything ruthlessly. The goal is to find what's broken, inconsistent, untested, unsupported, or poorly designed before it calcifies.

This is NOT a pat-on-the-back review. This is adversarial. Assume everything is wrong until proven otherwise.

---

## Scope

Everything created or modified in Sessions 14-18+ by AG and CW:

### Code (AG)
- `src/qa/extraction_field_validator.py` (680 LOC, 29 tests)
- CVA implementation: `cva_constraint.py`, `cva_valuation.py`, `subject_characteristics.py`, `activity_frame.py`, `cva_constraint_engine.py`, `cva_valuation_engine.py`, `cva_dynamics.py`, `cva_beauty.py`, `cva_attractor.py`, `overseer_playbooks.py`
- `scripts/run_panel_1_outcomes.py`
- Nightly pipeline QA_QUALITY_GATE wiring
- 23 neuroarch PDF extractions

### Code (CW)
- `scripts/backfill_operationalizations.py`
- `scripts/kirsh_decision_tree_analysis.py` (1,508 lines)
- `scripts/link_outcomes_to_instruments.py`
- `scripts/extract_stimulus_descriptions.py`
- Nightly pipeline QA_QUALITY_GATE + INV-10

### Data/Schemas (Both)
- `contracts/outcome_vocab/outcome_vocab.json` (116 terms, 311 operationalizations, instrument_ids)
- `contracts/instruments/instruments_registry.json` (95 instruments)
- `contracts/schemas/extraction_quality_rules.json` (50+ rules)
- `data/decision_tree_equivalence_classes.json` (25 equivalence classes)
- `data/attributes/causal_theoretic_image_attributes.json` (33 attributes)
- `data/stimulus_descriptions_from_articles.json` (22MB, 23K stimuli)
- `data/calibration/ch{1-7}_*.json` (7 calibration parameter files)
- `rasa_attractors.json`, 5 molecule JSONs

### Docs (Both)
- 30+ new documents in `docs/` — frameworks, reports, calibrations, implementation guides

---

## Audit Tasks

### RV5-1: Panel Consultation on Unreviewed Decisions
**What**: Many design decisions were made by AG or CW without expert panel review. Find them all, assess risk, convene panels for medium/high-risk ones.
**Where to look**: `docs/*DECISIONS_LOG*.md`, any file with "Decision:" or "Design choice:" headers, calibration parameter values (α, β, thresholds), schema design choices.
**Test**: For each decision, ask: "Would a domain expert disagree? Would a different choice change downstream results?"

### RV5-2: Comprehensive Test Suite
**What**: Run ALL tests. Fix failures. Add missing coverage for new modules.
**Commands**: `pytest` from repo root. Then check coverage for each new file.
**Target**: Zero failures, >80% coverage on new code.

### RV5-3: Extraction Pipeline Audit
**What**: Run extraction_field_validator on full corpus. Examine the 391 articles below 0.75. Identify systematic errors in antecedent fields (stimulus descriptions), consequent fields, direction normalization.
**Test**: Sample 20 low-scoring articles manually. Are the validator's flags correct? Are there errors it misses?

### RV5-4: Image Processing + Attribute Taxonomy Audit
**What**: Verify all 33 attributes (21 original + 12 new). Are vision algorithm specs real and implementable? Test Tier 1 algorithms on actual images. Check theoretical warrants — are references real? Do they support what we claim?
**Test**: `pip install opencv-python numpy scipy` then run NEW-04 (visual complexity) and NEW-08 (illumination uniformity) on 5 test images. Do results make sense?

### RV5-5: Tagging Consultants Audit (Antecedent + Consequent)
**What**: Check categorization quality in stimulus_descriptions_from_articles.json and outcome_vocab.json. Look for: miscategorized stimuli (e.g., "implantable cuff electrodes" in plants_greenery), overlapping terms, orphaned terms, broken instrument_ids links.
**Test**: Sample 50 stimuli from each category. What % are correctly categorized?

### RV5-6: Cultural Calibration Parameter Audit
**What**: Check all 7 CH calibration JSONs for: plausible numeric ranges, real APA references, consistent parameter naming, theoretical coherence across CH-1..CH-7. Do parameters interact? Are there contradictions?
**Test**: For each calibration formula, plug in extreme values. Do results stay in plausible range?

### RV5-7: CVA Implementation Code Audit
**What**: Audit all AG-written CVA code. Check: correct formula implementation vs. spec, edge cases, error handling, test coverage, schema compliance.
**Test**: Trace one complete CVA computation from input to output. Does it match the mathematical specification?

### RV5-8: Contracts and Schemas Audit
**What**: Validate all JSON files parse correctly. Check cross-references (instrument_ids in vocab → actual instruments in registry). Check schema versioning. Check for orphaned or duplicate entries.
**Test**: `python3 -c "import json; json.load(open(f))"` for every JSON. Then cross-reference checks.

### RV5-9: Synthesis — AESHI Re-score + Gap Report
**What**: After all audits, re-run AESHI scoring. Compare to last score (49/100 RED). Produce gap report: top 10 remaining issues, recommended next actions.
**Output**: `docs/RUTHLESS_V5_AUDIT_REPORT_2026-MM-DD.md`

---

## Rules of Engagement

1. **Adversarial mindset**: If you can break it, it's broken
2. **No credit for intent**: Code that's "meant to" do something but doesn't is a bug, not a feature
3. **References must be real**: Every APA citation must correspond to a real paper. Fabricated references are a critical failure.
4. **Parameters must be justified**: Every numeric threshold needs either empirical grounding or explicit "researcher's judgment" label
5. **Tests must test something**: A test that always passes tests nothing
6. **Cross-system consistency**: AG code and CW code must agree on schemas, field names, formulas
