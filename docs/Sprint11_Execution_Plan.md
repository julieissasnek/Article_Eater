# ⚠️ SUPERSEDED — See (newer version exists) for current version

# SPRINT 11 EXECUTION PLAN
## Fix Building Eval Wiring + Paper Evaluation Pipeline
## February 17, 2026

---

## HOW TO USE THIS DOCUMENT

1. Find your agent type below (CC, Codex, or Antigravity)
2. Check docs/TASK_CLAIMS.md for the first AVAILABLE task where dependencies are met
3. Claim it per the concurrency rules, then go
4. When done, take the next available task

## CONCURRENCY CONTROL — MANDATORY

1. Read docs/TASK_CLAIMS.md
2. Check the task you want is **AVAILABLE**
3. Change status to **CLAIMED**, add your agent name and timestamp
4. `git commit -m "Claiming Task X.X" docs/TASK_CLAIMS.md` — commit BEFORE starting work
5. Check dependency column — if a dependency shows needed, verify it's **DONE**
6. When task is complete: update to **DONE**, commit TASK_CLAIMS.md with your code
7. If a task shows **CLAIMED**, pick a different one
8. Before every commit: resolve any conflicts, always keep the newer version

**No git push needed — local repo, all agents share the same filesystem.**

## BLANKET PERMISSIONS

All agents have blanket permission to create, modify, and delete files in src/, tests/, data/, docs/. Run migrations, run tests, install dependencies, make implementation decisions. **Do NOT ask for confirmation. Document decisions in DECISIONS.md. Keep going.**

## REFERENCE DOCUMENTS

- **Doc 68** (CMR Contract): Pipeline spec, data models
- **Doc 67** (Encoding Prep): Dedup map, WIS formulas, PE classifications
- **Doc 67 Part 2**: PE contribution tags for each template
- **Sprint10_Execution_Plan.md**: Prior sprint context

---

## CRITICAL CONTEXT: WHY SPRINT 11 STARTS WITH FIXES

Sprint 10 built all the components but **did not wire them together correctly.** Evidence:

- Salk Institute and open-plan office BOTH score WIS 50.0 — impossible if real computations are running
- All three age profiles return identical scores — lifespan moderation is not being applied
- No severe deficits flagged for open-plan office — SOC2, VIEW1, CREA2 should all flag badly
- The classroom "computed overrides" run (age 7 = 85.21, age 35 = 79.56) proves the real compute functions WORK when called directly

**Diagnosis**: The building_eval.py orchestrator is calling placeholder functions (return WIS 50) instead of the real template_computations.py functions. The compute functions exist. The orchestrator exists. They are not connected.

**Round 1 of Sprint 11 fixes this before anything else is built.**

---

## ROUND 1: FIX THE WIRING (CRITICAL — ALL HANDS)

### TASK 11.1 — CC — Wire Real Computations into Orchestrator
**Estimated time: 90–120 minutes**
**Dependency: none**
**HIGHEST PRIORITY — nothing else matters until this works**

Open src/cmr/building_eval.py. Find where template computations are called in Step 4. Currently it returns placeholder WIS 50. Replace with actual calls to the compute functions in src/cmr/template_computations.py.

Specifically:
- Import all compute functions from template_computations.py
- Build a dispatch map: `{"VF3": compute_vf3, "L1": compute_l1, "L2": compute_l2, ...}` for every template that has a real compute function
- In Step 4, look up each activated template in the dispatch map
- If found: call the real function with the measured_features and occupant_profile
- If not found: THEN fall back to placeholder WIS 50 with `{"needs_computation": true}` flag
- Pass the raw output to the WIS conversion functions (Step 5)
- Ensure occupant_profile.age is passed through to functions that apply lifespan moderation

**Validation — the pipeline MUST produce these results after this task:**

Salk Institute (age 35):
- VF3 should compute R_h ≈ 2.75/√18 ≈ 0.648 → "impressive" zone → WIS ~75
- VIEW1 should score HIGH (ocean view + nature)
- MAT should register concrete + teak
- Overall WIS should be WELL ABOVE 50

Open-plan office (age 35):
- SOC2 privacy should score LOW (no acoustic or visual privacy)
- VIEW1 should score LOW (no nature view)
- Noise at 62 dBA should flag problems for focus work
- Overall WIS should be BELOW 50 with at least one severe deficit

Classroom (age 7 vs age 35):
- Scores should DIFFER between ages
- Age 7 should show higher PE sensitivity (DEV-I U-curve)

Run the three worked examples and report all domain scores. If results don't match these expectations, debug until they do. Do NOT move to other tasks until the face-validity tests pass.

### TASK 11.2 — Codex — Wire Interaction Adjustments
**Estimated time: 45–60 minutes**
**Dependency: none (can run parallel to 11.1)**

Open src/cmr/building_eval.py. Find Step 6 (interaction adjustments). Verify it actually calls the functions in src/cmr/interactions.py. If it's using placeholder logic, wire in the real interaction module:

- Import apply_all_interactions from interactions.py
- After Step 5 (WIS conversion), pass template scores through apply_all_interactions
- Verify: if both L3 and MAT4 and VIEW1 are active → convergence triad super-additivity applied
- Verify: if CREA2 pathways A+C both active → sub-additivity 0.76 applied
- Verify: VF3 + CREA2B → single-chain deduplication, no double-count

Write a test that activates the convergence triad and confirms the super-additivity multiplier changes the domain score.

### TASK 11.3 — Codex — Wire Lifespan Moderation
**Estimated time: 45–60 minutes**
**Dependency: none (can run parallel to 11.1)**

Trace the lifespan moderation path through the pipeline:
1. occupant_profile.age enters at Step 1
2. It should be passed to each compute function in Step 4
3. Compute functions should apply AGE-I multipliers (age > 50) or DEV-I multipliers (age < 25)
4. The modified PE sensitivity should change the WIS output

Check: do the compute functions in template_computations.py actually accept and use an age parameter? If not, add it. The lifespan_sensitivity_multiplier is in every JSON template file (all 150). The compute functions need to READ it and APPLY it.

Test: Run VF3 for age 7 and age 35. The WIS should differ. Run L2 for age 70 and age 30. The elderly person should need ~2× melanopic irradiance (per AGE-I), so the same illuminance should score LOWER for the 70-year-old.

### TASK 11.4 — Codex — Feature-to-Template Input Mapping
**Estimated time: 45–60 minutes**
**Dependency: none**

The orchestrator's Step 2 maps measured_features (what the user provides) to template inputs (what each compute function expects). Check that this mapping is correct and complete.

The user provides flat keys like `ceiling_height_m`, `floor_area_m2`, `illuminance_lux`, `ambient_noise_dba`. Each compute function expects specific argument names. The mapping must translate.

Build/verify a mapping dict:
```python
FEATURE_TO_TEMPLATE_INPUT = {
    "VF3": {"ceiling_height_m": "ceiling_height_m", "floor_area_m2": "floor_area_m2"},
    "L1": {"illuminance_lux": "illuminance_lux", "illuminance_distribution": "distribution"},
    "L2": {"illuminance_lux": "illuminance_lux"},
    "SOC2": {"ambient_noise_dba": "noise_level", "privacy_visual": "visual_privacy", 
             "privacy_acoustic": "acoustic_privacy", "density_m2_per_person": "density"},
    "CREA2": {"ambient_noise_dba": "noise_dba", "ceiling_height_m": "ceiling_height_m",
              "floor_area_m2": "floor_area_m2", "illuminance_lux": "illuminance_lux"},
    # ... all templates with compute functions
}
```

Verify: for each template in the dispatch map, the feature mapping provides all REQUIRED inputs. Flag templates where required inputs aren't available from the standard feature set.

---

## ROUND 2: VALIDATE THE FIX + BEGIN PAPER EVAL

### TASK 11.5 — Antigravity — Re-run All Worked Examples
**Estimated time: 60–90 minutes**
**Dependency: 11.1 DONE**

Re-run the three worked examples with the fixed pipeline. Report FULL results for each:

**Salk Institute (3 profiles: age 22, 35, 65)**
- Report all domain scores and overall WIS for each profile
- Verify: overall WIS > 60 (this is a great building)
- Verify: age differences exist and are in right direction
- Verify: VIEW1 scores high, VF3 shows "impressive" zone
- Report which templates activated and which hit data gaps

**Open-plan office (3 profiles: age 22, 35, 65)**
- Report all domain scores and overall WIS
- Verify: overall WIS < 50 (this is a bad environment for wellbeing)
- Verify: at least one severe deficit flagged (SOC2 privacy most likely)
- Verify: scores are DIFFERENT from Salk (this is the critical face-validity test)

**Classroom (age 7, age 35)**
- Report all domain scores for both profiles
- Verify: WIS differs between ages
- Verify: age 7 shows higher sensitivity (either higher scores for good features or lower scores for bad features)

If ANY of these fail face-validity, report the specific problem. Do NOT proceed to Round 3 until the building eval produces sensible, differentiated results.

### TASK 11.6 — CC — Paper Claim Extraction Module
**Estimated time: 120–180 minutes**
**Dependency: 11.1 DONE (building eval must work before paper eval)**

Create src/cmr/claim_extraction.py. This is Step 1 of the paper evaluation pipeline (Doc 68 Part 3.2).

Two modes:
```python
def extract_claims_structured(claims: list[dict]) -> list[dict]:
    """Accept pre-structured claims. Each claim:
    {independent_var: str, dependent_var: str, direction: str,
     effect_size: float|None, sample_n: int|None, context: str}
    Validate and normalize."""

def extract_claims_from_text(paper_text: str) -> list[dict]:
    """Extract causal claims from paper text.
    Use template parameter vocabulary as extraction targets.
    Returns list of structured claims."""
```

For extract_claims_from_text:
- Load template parameter names from the template DB as extraction vocabulary
- Use regex/NLP to identify causal patterns: "X increases/decreases/affects Y"
- Map extracted variables to template input/output names where possible
- Flag unmapped variables as "novel_variable"
- Include confidence score for each extraction

Test with the Ulrich 1984 abstract (or a reasonable approximation):
- Paper claims: hospital room with nature view → shorter recovery, less pain medication
- System should extract: {IV: "nature_view", DV: "recovery_time", direction: "decrease"} and map to VIEW1

### TASK 11.7 — Codex — Template Matching Module
**Estimated time: 60–90 minutes**
**Dependency: none**

Create src/cmr/template_matching.py. This is Step 2 of the paper evaluation pipeline.

```python
def match_claims_to_templates(
    claims: list[dict],
    template_registry: list[dict]
) -> list[dict]:
    """For each claim, find templates whose causal mechanisms match.
    Returns: [{claim: dict, matches: [{template_id: str, 
              match_type: "exact"|"partial"|"none",
              match_score: float, rationale: str}]}]"""
```

Matching logic:
- **Exact match**: claim IV maps to template input AND claim DV maps to template output
- **Partial match**: claim IV maps to template input OR claim DV maps to template output (but not both)
- **Mechanistic match**: claim describes a mechanism that the template's causal pathway includes
- **No match**: claim has no template correspondence (this is a gap finding)

Build a matching index from the template DB: for each template, extract all input names and output names. Use string similarity + synonym matching (e.g., "daylight" matches "illuminance", "noise" matches "ambient_noise_dba").

Test with:
- Claim {IV: "ceiling_height", DV: "creative_thinking"} → should match VF3 (exact on IV) + CREA2 (partial, ceiling is a pathway)
- Claim {IV: "nature_view", DV: "stress_reduction"} → should match VIEW1 (exact) + T6 (gap template, partial)
- Claim {IV: "carpet_color", DV: "productivity"} → should return no match or weak partial

### TASK 11.8 — Codex — Mechanism Tracing Module
**Estimated time: 60–90 minutes**
**Dependency: 11.7 DONE**

Create src/cmr/mechanism_tracing.py. This is Step 3 of the paper evaluation pipeline.

```python
def trace_mechanisms(
    claim_template_matches: list[dict]
) -> list[dict]:
    """For each claim-template match, assess mechanistic alignment.
    Apply SUBSTITUTE, VARY_MOD, BLOCK operations.
    Returns assessment per claim."""
```

Three operations per claim-template pair:

**SUBSTITUTE**: Could an alternative template explain this claim? Query the template DB for other templates with the same DV. If found, flag as "alternative mechanism available."

**VARY_MOD**: Do the moderators match? If the claim was measured in a specific population (e.g., elderly), check if the template's lifespan moderation covers that population. If the claim was in a specific climate, check climate_context. Mismatches reduce confidence.

**BLOCK**: If the template's mechanism were blocked, would the claim still hold? This is a thought-experiment assessment. If the template predicts the effect goes through pathway X, and the study controls for X, the claim is more strongly supported.

Output per claim:
```python
{
    "claim": {...},
    "template": "VIEW1",
    "substitute_alternatives": ["T16", "CREA3"],
    "moderator_match": "full" | "partial" | "mismatch",
    "moderator_details": "Study: elderly; template: age-moderated ✓",
    "block_assessment": "Mechanism path: soft_fascination → attention_restoration. 
                         If soft fascination blocked (urban view), effect should disappear.",
    "overall_confidence": "high" | "moderate" | "low"
}
```

### TASK 11.9 — Codex — Convergence and Composition Modules
**Estimated time: 60–90 minutes**
**Dependency: 11.8 DONE**

Create src/cmr/convergence.py. Steps 4 and 5 of the paper evaluation pipeline.

**Convergence Assessment (Step 4):**
```python
def assess_convergence(traced_claims: list[dict]) -> list[dict]:
    """Claims supported by multiple independent mechanisms get
    higher convergence scores."""
```
- Count unique template matches per claim
- If 3+ independent templates support a claim → convergence "strong"
- If 2 templates → "moderate"  
- If 1 template → "single_mechanism"
- If 0 templates → "unsupported" (gap finding)
- If templates CONTRADICT the claim → "contradicted" (high-value finding)

**Composition Check (Step 5 — Barrett R10):**
```python
def check_composition_failures(traced_claims: list[dict]) -> list[dict]:
    """Detect cases where individual mechanisms are valid but their
    combination produces unexpected interactions."""
```
- Check the interaction matrices: if a claim involves multiple templates that have known interactions, verify the claimed combined effect is consistent with the interaction coefficient
- Example: if a paper claims noise + dim light doubles creative output, but CREA2 says sub-additivity at 0.76, flag as "composition concern"

### TASK 11.10 — Codex — Paper Evaluation Orchestrator
**Estimated time: 60–90 minutes**
**Dependency: 11.6 + 11.7 + 11.8 + 11.9 DONE**

Create src/cmr/paper_eval.py. Wire Steps 1–7 from Doc 68 Part 3.2:

```python
def evaluate_paper(
    paper_text: str = None,
    structured_claims: list[dict] = None
) -> dict:
    """Full paper evaluation pipeline."""
```

1. Claim extraction (call claim_extraction.py)
2. Template matching (call template_matching.py)
3. Mechanism tracing (call mechanism_tracing.py)
4. Convergence assessment (call convergence.py)
5. Composition check (call convergence.py)
6. Prioritization: rank findings by VOI — contradictions highest, gaps second, confirmations lowest
7. Report generation

Return a structured report:
```python
{
    "paper_summary": str,
    "n_claims_extracted": int,
    "n_claims_matched": int,
    "n_claims_unmatched": int,
    "findings": [
        {"claim": dict, "assessment": str, "convergence": str, 
         "confidence": str, "voi": "high"|"medium"|"low"}
    ],
    "template_system_updates": [
        {"type": "confirms"|"contradicts"|"extends"|"gap",
         "template": str, "detail": str}
    ]
}
```

Test with a dummy paper containing 3 claims: one that matches VIEW1, one that contradicts CREA2 predictions, one with no template match.

---

## ROUND 3: WORKED EXAMPLES + HARDENING

### TASK 11.11 — CC — Ulrich 1984 Paper Evaluation
**Estimated time: 60–90 minutes**
**Dependency: 11.10 DONE**

The canonical validation test. Ulrich (1984) "View through a window may influence recovery from surgery." Claims:
1. Patients with tree view had shorter post-operative stays (7.96 vs 8.70 days)
2. Patients with tree view required fewer analgesic doses
3. Patients with tree view had fewer negative evaluative comments from nurses

Run evaluate_paper with these structured claims. The system should:
- Match claim 1 to VIEW1 (nature view → restoration)
- Match claim 2 to VIEW1 + T6 (stress/cortisol reduction)
- Match claim 3 to VIEW1 + SOC templates (behavioral expression of wellbeing)
- Convergence: high (multiple mechanisms support nature-view benefits)
- No composition failures
- VOI: low (confirms well-calibrated template)

Report full results. This is the demo that proves the system works end-to-end for its original mission.

### TASK 11.12 — Codex — Paper Report Generator
**Estimated time: 45–60 minutes**
**Dependency: 11.10 DONE**

Create src/cmr/paper_report.py. Takes the output of evaluate_paper() and produces:

```python
def generate_paper_report(evaluation: dict) -> dict:
    """Structured report for paper evaluation."""

def format_paper_report_text(report: dict) -> str:
    """Human-readable text version."""
```

Report sections:
- Paper summary and claim count
- Per-claim assessment table (claim, matched templates, confidence, VOI)
- High-VOI findings highlighted (contradictions, gaps)
- Template system update recommendations
- Methodology note (N templates consulted, coverage of claim space)

### TASK 11.13 — Antigravity — Building Eval Regression Suite
**Estimated time: 60–90 minutes**
**Dependency: 11.5 DONE (face-validity confirmed)**

Create tests/test_building_eval_regression.py. Encode the three worked examples as regression tests so future changes don't break face-validity:

- test_salk_scores_above_60: Salk overall WIS > 60
- test_salk_view_domain_high: VIEW domain > 70
- test_openplan_scores_below_50: open-plan overall WIS < 50
- test_openplan_has_severe_deficit: at least one domain < 30
- test_salk_beats_openplan: Salk WIS > open-plan WIS (fundamental)
- test_age_differences_exist: same building, different ages → different scores
- test_child_higher_sensitivity: age 7 sensitivity ≥ age 35 sensitivity
- test_elderly_circadian_penalty: L2 for age 70 < L2 for age 30 at same illuminance

These are the FACE-VALIDITY INVARIANTS. If any of these break, the system is wrong.

### TASK 11.14 — Codex — Paper Eval with Contradicting Study
**Estimated time: 60 minutes**
**Dependency: 11.10 DONE**

Test the paper evaluation pipeline with a paper that CONTRADICTS template predictions:

Fabricated study: "High ceilings impair creative performance"
Claims:
1. {IV: "ceiling_height_3.5m", DV: "divergent_thinking", direction: "decrease", d: -0.3}
2. {IV: "ceiling_height_3.5m", DV: "convergent_thinking", direction: "increase", d: 0.4}

The system should:
- Match to VF3 and CREA2
- Flag claim 1 as CONTRADICTING VF3/CREA2 predictions (high ceiling should HELP divergent thinking)
- Flag claim 2 as PARTIALLY CONSISTENT (CREA2 does predict liberating ceiling helps convergent less)
- VOI: HIGH (contradiction with well-calibrated template)
- Recommend: review VF3 Goldilocks boundaries, check if effect reverses above R_h 0.80

This tests the system's ability to learn from disconfirmation, not just confirm what it already believes.

### TASK 11.15 — Codex — Paper Eval with Novel Finding
**Estimated time: 60 minutes**
**Dependency: 11.10 DONE**

Test with a paper that falls in a GAP:

Fabricated study: "Indoor air quality affects cognitive performance via CO2 concentration"
Claims:
1. {IV: "co2_1000ppm", DV: "decision_making", direction: "decrease", d: -0.7}
2. {IV: "co2_2500ppm", DV: "cognitive_function", direction: "decrease", d: -1.4}

The system should:
- Find NO exact template match (air quality is not covered by any template)
- Partial match to T27 (interoceptive inference residual) — CO2 is an interoceptive signal
- Flag as GAP finding: "No template covers indoor air quality. Consider AIR-I panel."
- VOI: HIGH (novel domain, strong effect sizes)

This tests gap detection — one of the system's most valuable functions.

### TASK 11.16 — CC — CLI for Paper Evaluation
**Estimated time: 45–60 minutes**
**Dependency: 11.10 DONE**

Extend src/cmr/cli.py to support paper evaluation:

```bash
python -m src.cmr.cli evaluate-paper \
  --claims '[{"iv": "nature_view", "dv": "recovery_time", "direction": "decrease", "d": 0.5}]'

python -m src.cmr.cli evaluate-paper \
  --file paper_claims.json

python -m src.cmr.cli evaluate-paper \
  --text "Patients with nature views recovered faster..."
```

Include --json and --verbose flags matching the building eval CLI.

### TASK 11.17 — Codex — Cross-Pipeline Integration Test
**Estimated time: 60–90 minutes**
**Dependency: 11.5 + 11.10 DONE**

Write tests/test_cross_pipeline.py that tests BOTH pipelines together:

1. Evaluate the Salk Institute (building eval) → get domain scores
2. Feed a paper about the Salk Institute into paper eval → get claim assessments  
3. Verify: the building eval's strong VIEW1 score is CONSISTENT with the paper eval's confirmation of nature-view claims
4. Verify: if the paper claims a feature the building doesn't have, the building eval should show a gap in that domain

This tests that the two pipelines produce coherent, non-contradictory outputs about the same building.

### TASK 11.18 — Antigravity — Paper Eval Validation Sweep
**Estimated time: 60–90 minutes**
**Dependency: 11.10 + 11.11 DONE**

Validation sweep for the paper evaluation pipeline:

1. Run Ulrich 1984 evaluation — verify sensible output
2. Run contradicting study (11.14) — verify contradiction flagged
3. Run novel finding (11.15) — verify gap detected
4. Run full test suite — verify zero new failures
5. Count: how many templates can be matched? How many claims can be assessed? What's the coverage?
6. Report: overall assessment of paper eval pipeline readiness

### TASK 11.19 — CC — Batch 2 Paper Claims Library
**Estimated time: 90–120 minutes**
**Dependency: 11.10 DONE**

Create data/test_papers/ directory with 5-10 structured claim files from real papers in the architecture-wellbeing literature:

1. Ulrich 1984 (nature view → recovery)
2. Mehta et al. 2012 (ambient noise → creativity)
3. Vartanian et al. 2015 (contour → beauty/approach)
4. Steidle & Werth 2013 (dim light → creativity)
5. de Dear & Brager 1998 (adaptive thermal comfort)
6. Heschong 1999 (daylight → test scores)
7. Evans & Johnson 2000 (open-plan noise → stress)
8. Kaplan 1995 (attention restoration theory)
9. Leesman workplace survey (privacy → satisfaction)
10. Oppezzo & Schwartz 2014 (walking → creativity)

For each, create a JSON file with structured claims that can be fed to evaluate_paper(). These become the system's validation corpus.

### TASK 11.20 — Codex — VOI Scoring Module
**Estimated time: 60–90 minutes**
**Dependency: 11.10 DONE**

Create src/cmr/voi_scoring.py. Implements the prioritization logic from Step 6:

```python
def score_voi(findings: list[dict]) -> list[dict]:
    """Score Value of Information for each finding.
    Returns findings sorted by VOI, highest first."""
```

VOI scoring rules:
- **Contradiction** with well-calibrated template (maturity "supported" or better): VOI = 1.0
- **Contradiction** with preliminary template: VOI = 0.7
- **Gap** finding (no template match) with strong effect size (d > 0.5): VOI = 0.8
- **Gap** finding with weak effect: VOI = 0.4
- **Extension** (confirms template but adds new moderator or boundary): VOI = 0.6
- **Confirmation** of well-calibrated template: VOI = 0.2
- **Confirmation** of preliminary template: VOI = 0.5

Also compute aggregate VOI for the paper: what is the expected information gain from fully processing this paper? Papers with many contradictions/gaps are more valuable than papers that only confirm known findings.

---

## ROUND 3 CONTINUED: GLOBAL INTEGRATION & SYSTEM INTEGRITY TESTS

These tasks test whether the system's components are actually CONNECTED — not just present. The Sprint 10 WIS 50.0 failure (every building scores identical) was a CONNECTIVITY failure: components existed but weren't wired. These tests are designed so that type of failure can NEVER go undetected again.

### TASK 11.21 — Antigravity — Input Sensitivity Sweep
**Estimated time: 90–120 minutes**
**Dependency: 11.1 DONE**

The most fundamental test: **vary one input, verify the output changes.** If it doesn't change, something is disconnected.

Create tests/test_input_sensitivity.py. For EACH compute function that exists:

```python
def test_sensitivity_vf3():
    """Vary ceiling height, verify WIS changes."""
    base = evaluate_building(features={"ceiling_height_m": 2.7, "floor_area_m2": 25.0, ...})
    high = evaluate_building(features={"ceiling_height_m": 5.0, "floor_area_m2": 25.0, ...})
    low  = evaluate_building(features={"ceiling_height_m": 2.0, "floor_area_m2": 25.0, ...})
    assert base["overall_wis"] != high["overall_wis"], "VF3 insensitive to ceiling height"
    assert base["overall_wis"] != low["overall_wis"], "VF3 insensitive to ceiling height"
```

Do this for EVERY major input variable:
- ceiling_height_m → should change VF3, CREA2
- illuminance_lux → should change L1, L2, CREA2
- ambient_noise_dba → should change CREA2, SOC2
- has_nature_view → should change VIEW1
- privacy_visual → should change SOC2
- primary_material → should change MAT1, MAT2, MAT4
- occupant_age → should change ALL templates with lifespan moderation

Each test: change ONE input, hold all others constant, verify the output changes. If ANY test shows zero delta, that input is disconnected. Report the full matrix:

| Input Variable | Templates Expected to React | Actually Reacted? | Delta |
|---------------|---------------------------|-------------------|-------|

This is the test that would have caught the Sprint 10 failure on day one.

### TASK 11.22 — CC — Function Signature Audit
**Estimated time: 60–90 minutes**
**Dependency: 11.1 DONE**

Automated drift detection: verify that every function is being CALLED with the arguments it EXPECTS.

Create tests/test_function_signatures.py:

```python
import inspect
from src.cmr import template_computations, building_eval, interactions, wis

def test_dispatch_map_signatures():
    """Every function in the dispatch map must accept the args 
    the orchestrator passes."""
    dispatch = building_eval.TEMPLATE_DISPATCH  # or however it's structured
    for template_id, func in dispatch.items():
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        # Verify 'occupant_age' is accepted (for lifespan moderation)
        assert 'occupant_age' in params or any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
        ), f"{template_id}: {func.__name__} doesn't accept occupant_age"

def test_feature_mapping_completeness():
    """Every template in dispatch map has a feature mapping entry."""
    dispatch = building_eval.TEMPLATE_DISPATCH
    mapping = building_eval.FEATURE_TO_TEMPLATE_INPUT
    for template_id in dispatch:
        assert template_id in mapping, f"No feature mapping for {template_id}"

def test_feature_mapping_arg_match():
    """Feature mapping output keys match function parameter names."""
    dispatch = building_eval.TEMPLATE_DISPATCH
    mapping = building_eval.FEATURE_TO_TEMPLATE_INPUT
    for template_id, func in dispatch.items():
        sig = inspect.signature(func)
        expected_params = set(sig.parameters.keys()) - {'self', 'kwargs', 'occupant_age'}
        mapped_params = set(mapping.get(template_id, {}).values())
        missing = expected_params - mapped_params - {'occupant_age'}
        # Allow some unmapped (optional params) but flag required ones
        required = {k for k, v in sig.parameters.items() 
                    if v.default is inspect.Parameter.empty and k != 'occupant_age'}
        unmapped_required = required - mapped_params
        assert not unmapped_required, \
            f"{template_id}: required params {unmapped_required} have no feature mapping"

def test_wis_conversion_called():
    """Verify the orchestrator actually calls WIS conversion, 
    not returning raw values or placeholders."""
    result = evaluate_building(
        features={"ceiling_height_m": 2.7, "floor_area_m2": 25.0},
        occupant_profile={"age": 35}
    )
    # If WIS conversion is working, no score should be exactly 50.0 
    # for a building with real inputs (statistically near-impossible)
    activations = result.get("template_activations", [])
    placeholder_count = sum(1 for a in activations if a.get("wis_score") == 50.0)
    total = len(activations)
    assert placeholder_count / max(total, 1) < 0.5, \
        f"{placeholder_count}/{total} templates returned exactly 50.0 — likely placeholders"

def test_interaction_module_called():
    """Verify interactions are actually applied, not skipped."""
    # Feed inputs that should trigger convergence triad
    result = evaluate_building(
        features={"illuminance_lux": 500, "primary_material": "wood",
                  "has_nature_view": True, "ceiling_height_m": 3.0,
                  "floor_area_m2": 30.0},
        occupant_profile={"age": 35}
    )
    # Check for interaction adjustment records
    assert result.get("interactions_applied") or \
           any(a.get("interaction_adjustments") for a in result.get("template_activations", [])), \
        "Convergence triad inputs provided but no interaction adjustments recorded"
```

This catches: wrong argument names, missing mappings, placeholder returns, and bypassed modules. Run and fix any failures.

### TASK 11.23 — Codex — Web of Belief Integration Test
**Estimated time: 90–120 minutes**
**Dependency: 11.10 DONE**

The web of belief has 10,670 beliefs, 25,959 constraints, and 1,555 bridges. **Are ANY of these actually consulted during paper or building evaluation?** If not, the web is an expensive database that nothing reads.

Create tests/test_web_integration.py:

```python
def test_paper_eval_queries_web():
    """Paper evaluation should query the web of belief 
    for existing beliefs about the claim's variables."""
    # Instrument or mock web_persistence to track queries
    with query_tracker(web_persistence) as tracker:
        evaluate_paper(structured_claims=[
            {"iv": "nature_view", "dv": "stress_reduction", 
             "direction": "decrease", "d": 0.5}
        ])
    assert tracker.query_count > 0, \
        "Paper eval made zero web of belief queries"
    assert any("nature" in str(q) or "view" in str(q) or "stress" in str(q) 
               for q in tracker.queries), \
        "Paper eval queries didn't reference claim variables"

def test_building_eval_queries_web():
    """Building eval should check web for constraints 
    relevant to activated templates."""
    with query_tracker(web_persistence) as tracker:
        evaluate_building(
            features={"ceiling_height_m": 3.0, "floor_area_m2": 25.0},
            occupant_profile={"age": 35}
        )
    # Building eval may not query web — document whether it should
    # If it doesn't, this test documents a design decision, not a bug
    print(f"Building eval made {tracker.query_count} web queries")

def test_staging_links_reachable():
    """The 1,361 staging theory-links should be queryable 
    and structurally valid."""
    from src.services.web_persistence import get_constraints_for_web
    links = get_constraints_for_web(constraint_type="tier2_theory_link")
    assert len(links) >= 1361, f"Expected 1361+ theory links, found {len(links)}"
    # Verify structure
    for link in links[:10]:  # spot check
        assert "theory_id" in link or hasattr(link, "theory_id"), \
            f"Theory link missing theory_id: {link}"

def test_beliefs_have_evidence():
    """Beliefs in the web should have evidence/source fields, 
    not be empty shells."""
    from src.services.web_persistence import get_beliefs_for_web
    master_web = get_or_create_master_web()
    beliefs = get_beliefs_for_web(master_web.id, limit=100)
    empty_count = sum(1 for b in beliefs 
                      if not getattr(b, 'evidence', None) and 
                         not getattr(b, 'source', None))
    assert empty_count / max(len(beliefs), 1) < 0.3, \
        f"{empty_count}/100 sampled beliefs have no evidence or source"

def test_constraints_reference_valid_templates():
    """Constraints that reference templates should reference 
    templates that actually exist in the DB."""
    from src.services.web_persistence import get_constraints_for_web
    constraints = get_constraints_for_web(limit=200)
    template_ids = {t.display_id for t in TemplateRecord.query.all()}
    for c in constraints:
        if hasattr(c, 'template_id') and c.template_id:
            assert c.template_id in template_ids, \
                f"Constraint references non-existent template: {c.template_id}"
```

If the web is NOT being queried by either pipeline, that's a major design finding — document it and recommend whether it SHOULD be.

### TASK 11.24 — Codex — VOI End-to-End Verification
**Estimated time: 60–90 minutes**
**Dependency: 11.20 DONE**

Test that VOI scoring is actually SENSITIVE to content, not returning fixed values.

Create tests/test_voi_integration.py:

```python
def test_voi_varies_with_contradiction():
    """A paper that contradicts templates should have higher VOI 
    than one that confirms them."""
    confirming = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "restoration", "direction": "increase", "d": 0.5}
    ])
    contradicting = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "restoration", "direction": "decrease", "d": -0.5}
    ])
    assert contradicting["aggregate_voi"] > confirming["aggregate_voi"], \
        "Contradicting paper should have higher VOI than confirming paper"

def test_voi_varies_with_effect_size():
    """Larger effect sizes in gap areas should produce higher VOI."""
    weak = evaluate_paper(structured_claims=[
        {"iv": "air_quality", "dv": "cognition", "direction": "decrease", "d": -0.1}
    ])
    strong = evaluate_paper(structured_claims=[
        {"iv": "air_quality", "dv": "cognition", "direction": "decrease", "d": -1.4}
    ])
    assert strong["aggregate_voi"] > weak["aggregate_voi"], \
        "Stronger effect in gap area should have higher VOI"

def test_voi_sensitive_to_template_maturity():
    """Contradicting a well-calibrated template should have higher VOI 
    than contradicting a speculative one."""
    # Need to identify a well-calibrated and a speculative template
    # and construct claims that contradict each
    # The VOI for contradicting the well-calibrated one should be higher
    pass  # Implement based on actual template maturity values

def test_existing_voi_service_consistency():
    """If src/services/ has its own VOI calculation (from Sprint 6/9), 
    verify it's consistent with src/cmr/voi_scoring.py."""
    # Check if there's an existing VOI module in the research queue
    import importlib
    try:
        old_voi = importlib.import_module("src.services.voi_search")
        new_voi = importlib.import_module("src.cmr.voi_scoring")
        # Document the relationship
        print(f"Old VOI module: {old_voi.__file__}")
        print(f"New VOI module: {new_voi.__file__}")
        # These should either be the same module or explicitly documented
        # as different (paper VOI vs research queue VOI)
    except ImportError as e:
        print(f"VOI module import issue: {e}")
```

CRITICAL: The repo already has a VOI module in the research queue (Sprint 6/9, voi_search.py). The Sprint 11 VOI scoring (11.20) may be a DUPLICATE or a DIFFERENT thing. This task must clarify: are there two VOI systems? If so, do they agree? If not, which is canonical?

### TASK 11.25 — Antigravity — Bayesian Network Health Check
**Estimated time: 90–120 minutes**
**Dependency: none**

The system has a Bayesian network / web of belief. This task verifies it is functioning as a NETWORK, not just a database.

Create tests/test_bn_health.py:

```python
def test_belief_update_propagates():
    """Adding evidence for one belief should affect related beliefs' 
    posteriors through the network structure."""
    # Get a belief connected to others via bridges
    # Record its posterior
    # Add confirming evidence to a connected belief
    # Check: did the original belief's posterior change?
    # If posteriors never change, the BN is a static DB, not a network
    pass

def test_constraint_satisfaction():
    """Constraints should actually constrain — violating a constraint 
    should produce a coherence warning or penalty."""
    # Find a constraint (e.g., "T6 cortisol > threshold → memory impaired")
    # Set beliefs inconsistent with this constraint
    # Check: does the system detect the inconsistency?
    pass

def test_bridge_connectivity():
    """Bridges connect beliefs across theories. Verify they're not 
    orphaned (connecting to deleted/missing beliefs)."""
    bridges = query_all_bridges()
    for bridge in bridges[:100]:
        source = get_belief(bridge.source_id)
        target = get_belief(bridge.target_id)
        assert source is not None, f"Bridge {bridge.id} source {bridge.source_id} missing"
        assert target is not None, f"Bridge {bridge.id} target {bridge.target_id} missing"

def test_theory_link_bidirectional():
    """Theory links (the 1,361 staging rows) should be traversable 
    in both directions: paper→theory and theory→paper."""
    # Pick an ART theory link
    # Can we go from ART construct → paper claims?
    # Can we go from paper claim → ART construct?
    # Both directions should work
    pass

def test_web_not_static():
    """The web should respond to new evidence — if we add a new belief 
    with evidence, something in the system should change."""
    before = snapshot_web_state()
    add_test_belief("test_belief_001", evidence="fabricated test evidence")
    after = snapshot_web_state()
    assert before != after, "Adding a belief didn't change web state at all"
    # Cleanup
    remove_test_belief("test_belief_001")
```

If the BN is just a static database (beliefs stored but never updated, constraints stored but never checked, bridges stored but never traversed), that's a critical finding. Document exactly which network operations WORK and which are UNIMPLEMENTED.

### TASK 11.26 — CC — Argument Structure Tracing
**Estimated time: 90–120 minutes**
**Dependency: 11.1 + 11.10 DONE**

Trace a single claim through the ENTIRE system and verify every handoff passes the right data structure.

Create tests/test_argument_tracing.py:

Pick a simple, well-understood claim: "Nature views reduce stress (d = 0.5)."

Trace it through EVERY step with assertions at each boundary:

```python
def test_full_trace_nature_view_claim():
    """Trace a single claim through every system boundary."""
    
    claim = {"iv": "nature_view", "dv": "stress_reduction", 
             "direction": "decrease", "d": 0.5, 
             "sample_n": 46, "context": "hospital"}
    
    # STEP 1: Claim extraction
    extracted = extract_claims_structured([claim])
    assert len(extracted) == 1
    assert extracted[0]["iv"] == "nature_view"
    assert extracted[0]["d"] == 0.5
    
    # STEP 2: Template matching
    matches = match_claims_to_templates(extracted, get_all_active_templates())
    assert len(matches) > 0
    assert any(m["template_id"] == "VIEW1" for m_list in matches 
               for m in m_list.get("matches", []))
    view1_match = [m for m_list in matches for m in m_list.get("matches", []) 
                   if m["template_id"] == "VIEW1"][0]
    assert view1_match["match_type"] in ("exact", "partial")
    assert view1_match["match_score"] > 0.5
    
    # STEP 3: Mechanism tracing
    traced = trace_mechanisms(matches)
    assert len(traced) > 0
    view1_trace = [t for t in traced if t.get("template") == "VIEW1"][0]
    # SUBSTITUTE check: are alternative explanations listed?
    assert "substitute_alternatives" in view1_trace
    # VARY_MOD check: hospital context acknowledged?
    assert view1_trace["moderator_match"] in ("full", "partial")
    
    # STEP 4: Convergence
    convergence = assess_convergence(traced)
    assert convergence[0]["convergence"] in ("strong", "moderate", "single_mechanism")
    
    # STEP 5: Composition
    composition = check_composition_failures(traced)
    # Nature view claim should have no composition issues
    
    # STEP 6: VOI
    scored = score_voi(convergence)
    assert scored[0]["voi"] < 0.5  # Confirming well-calibrated template = low VOI
    
    # STEP 7: Report
    report = evaluate_paper(structured_claims=[claim])
    assert report["n_claims_matched"] >= 1
    assert "VIEW1" in str(report["findings"])
    
    # CROSS-CHECK: Building eval for same building
    hospital_with_view = evaluate_building(
        features={"has_nature_view": True, "view_content": "trees_garden",
                  "ceiling_height_m": 2.7, "floor_area_m2": 20.0},
        occupant_profile={"age": 50}
    )
    hospital_without_view = evaluate_building(
        features={"has_nature_view": False, "view_content": "parking_lot",
                  "ceiling_height_m": 2.7, "floor_area_m2": 20.0},
        occupant_profile={"age": 50}
    )
    # The paper says nature view helps → building with view should score higher
    assert hospital_with_view["overall_wis"] > hospital_without_view["overall_wis"], \
        "Paper says nature view helps, but building eval doesn't show benefit"
```

This is the GOLD STANDARD test. If this passes, the system's argument structure is connected end-to-end. If it fails at any step, we know exactly WHERE the break is.

### TASK 11.27 — Codex — Template-Theory Data Dependency Test
**Estimated time: 60–90 minutes**
**Dependency: 11.23 DONE**

The user asks: "Do the theories actually care what the data is in the articles?" This task tests whether the theoretical structure (templates, web of belief) is RESPONSIVE to empirical data or operates independently of it.

Create tests/test_data_dependency.py:

```python
def test_paper_data_changes_assessment():
    """Same paper structure, different effect sizes → different assessment."""
    small_effect = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "restoration", "direction": "increase", "d": 0.1}
    ])
    large_effect = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "restoration", "direction": "increase", "d": 1.2}
    ])
    assert small_effect != large_effect, \
        "System produces identical output for d=0.1 and d=1.2 — data-insensitive"

def test_sample_size_affects_confidence():
    """Larger samples should produce higher confidence assessments."""
    small_n = evaluate_paper(structured_claims=[
        {"iv": "ceiling_height", "dv": "creativity", "direction": "increase", 
         "d": 0.5, "sample_n": 12}
    ])
    large_n = evaluate_paper(structured_claims=[
        {"iv": "ceiling_height", "dv": "creativity", "direction": "increase", 
         "d": 0.5, "sample_n": 500}
    ])
    # At minimum, confidence should differ
    assert small_n["findings"][0].get("confidence") != large_n["findings"][0].get("confidence") or \
           small_n["findings"][0].get("voi") != large_n["findings"][0].get("voi"), \
        "System ignores sample size — data-insensitive"

def test_context_affects_matching():
    """Same IV/DV but different contexts should produce different 
    template matches or moderator assessments."""
    hospital = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "recovery", "direction": "increase", 
         "d": 0.5, "context": "hospital"}
    ])
    office = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "recovery", "direction": "increase", 
         "d": 0.5, "context": "office"}
    ])
    # At least moderator match should differ
    # Hospital = VIEW1 primary context; office = VIEW1 + CREA3 secondary

def test_contradictory_data_different_from_confirming():
    """The system must produce DIFFERENT outputs for data that confirms 
    vs contradicts its templates. If it doesn't, it's dogmatic."""
    confirms = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "restoration", "direction": "increase", "d": 0.5}
    ])
    contradicts = evaluate_paper(structured_claims=[
        {"iv": "nature_view", "dv": "restoration", "direction": "decrease", "d": -0.5}
    ])
    assert confirms != contradicts, \
        "System produces same output for confirming and contradicting data — DOGMATIC"
    # The contradicting paper should get higher VOI
    assert contradicts["aggregate_voi"] > confirms["aggregate_voi"], \
        "Contradicting evidence doesn't increase VOI — system doesn't learn from disconfirmation"

def test_novel_variable_detected():
    """A claim about a variable the system has never seen should be 
    flagged as novel, not silently dropped."""
    novel = evaluate_paper(structured_claims=[
        {"iv": "electromagnetic_field_exposure", "dv": "sleep_quality", 
         "direction": "decrease", "d": -0.4}
    ])
    assert novel["n_claims_unmatched"] >= 1 or \
           any("gap" in str(f) or "novel" in str(f) for f in novel.get("findings", [])), \
        "Novel variable silently dropped — system should flag unknowns"
```

### TASK 11.28 — Antigravity — Enum and Schema Drift Check
**Estimated time: 60 minutes**
**Dependency: none**

Sprint 10 had enum drift issues. Verify they're fixed AND check for new drift introduced by Sprint 10/11 work.

```bash
# Run existing drift checker
python check_enum_drift.py

# Additional checks:
# 1. All template_computations.py function names match template display_ids
# 2. All interaction matrix keys match template display_ids  
# 3. All feature mapping keys match template display_ids
# 4. All dedup_status values are from the allowed set: 
#    "active", "superseded", "residual", "reference", "gap"
# 5. All pe_contribution values are from: 
#    "predictive", "explanatory", "organizational"
# 6. All calibration_status values are from: 
#    "substantial", "partial", "protocol", "uncalibrated"
# 7. All practical_accessibility values are from: "A", "B", "C", "D"
```

Create tests/test_enum_consistency.py that checks ALL enum-like fields across ALL components. If Sprint 10 introduced "supported" in one place and "substantial" in another for the same concept, catch it.

### TASK 11.29 — CC — No-Placeholder Audit
**Estimated time: 60–90 minutes**
**Dependency: 11.1 DONE**

Systematically find and eliminate ALL remaining placeholder/stub code in the CMR pipeline.

```bash
# Search for common placeholder patterns
grep -rn "placeholder" src/cmr/
grep -rn "TODO" src/cmr/
grep -rn "stub" src/cmr/
grep -rn "not.implemented" src/cmr/
grep -rn "pass$" src/cmr/   # empty function bodies
grep -rn "return 50" src/cmr/  # the Sprint 10 killer
grep -rn "wis.*=.*50" src/cmr/
grep -rn "needs_computation" src/cmr/
```

For each placeholder found:
- If a real implementation exists elsewhere, wire it in
- If no implementation exists, mark it explicitly: `raise NotImplementedError("TEMPLATE_X: no compute function — see Doc 67 gap list")`
- Do NOT leave silent placeholders that return default values

The rule is: **the system must either compute a real answer or explicitly refuse.** Returning WIS 50 without flagging it as a placeholder is a lie.

### TASK 11.30 — Codex — Completeness Inventory
**Estimated time: 60 minutes**
**Dependency: 11.22 DONE (signature audit)**

Generate a machine-readable inventory of what's connected and what isn't.

Create scripts/generate_completeness_report.py that outputs:

```
TEMPLATE COMPLETENESS INVENTORY
================================
Template | JSON | DB Record | Compute Fn | Feature Map | WIS Conv | Interactions | Status
---------|------|-----------|------------|-------------|----------|--------------|-------
VF3      | ✅   | ✅         | ✅          | ✅           | ✅        | ✅ (VF1×VF3) | COMPLETE
L1       | ✅   | ✅         | ✅          | ✅           | ✅        | — (none)     | COMPLETE  
T6       | ✅   | ✅         | ⚠️ stub     | ❌           | ❌        | — (none)     | GAP
...

SUMMARY
=======
Complete (all columns ✅): 34/150
Partial (some ✅): 45/150
Stub only: 15/150
No compute function: 56/150

WEB OF BELIEF CONNECTIVITY
===========================
Beliefs with evidence: X/10670
Constraints with valid template refs: X/25959
Bridges with valid endpoints: X/1555
Theory links loaded: 1361/1361

PIPELINE CONNECTIVITY
=====================
Building eval → template dispatch: X/Y templates wired
Building eval → WIS conversion: connected/disconnected
Building eval → interaction module: connected/disconnected
Building eval → lifespan moderation: connected/disconnected
Paper eval → claim extraction: connected/disconnected
Paper eval → template matching: connected/disconnected
Paper eval → web of belief: connected/disconnected
```

This report becomes the definitive answer to "what actually works." Commit it to docs/completeness_report.md and update it with every sprint.

### TASK 11.31 — CC or Codex — Sprint Verification Test Suite
**Estimated time: 90–120 minutes**
**Dependency: 11.1 DONE**

Read docs/Sprint_Verification_And_Provenance_Tests.md Part 1. Implement tests/test_sprint_verification.py. This suite verifies Sprint 10 AND Sprint 11 deliverables actually function in the integrated system. Adapt function calls to match the actual codebase — the test doc has approximate signatures. Every failing test is a finding — report it, don't just make the test pass.

Key tests:
- Template DB populated with classifications (S10-V01, V02)
- WIS module produces non-50 values and is monotonic (S10-V03)
- Compute functions exist and return real values (S10-V04)
- Orchestrator produces DIFFERENT scores for Salk vs open-plan (S10-V05)
- Lifespan moderation produces age differences (S10-V05)
- Salk scores > 55, open-plan < 50, Salk beats open-plan (S11-V01)
- Paper eval runs, finds VIEW1, and is direction-sensitive (S11-V02)

### TASK 11.32 — Antigravity or Codex — Building Eval Provenance Tests
**Estimated time: 90–120 minutes**
**Dependency: 11.1 DONE**

Read docs/Sprint_Verification_And_Provenance_Tests.md Part 2 (Building Evaluation Provenance). Implement tests/test_provenance_building.py. These tests verify that every WIS score is traceable back to specific inputs, templates, and parameters.

Key tests:
- Overall WIS = geometric mean of domain scores (PROV-B01)
- Domain scores traceable to specific template activations (PROV-B01)
- Template activations record inputs and raw outputs (PROV-B01)
- Parameters come from JSON calibration files, not hardcoded (PROV-B02)
- Lifespan moderation differences are recorded, not just present (PROV-B03)
- Interaction adjustments are recorded when triggered (PROV-B04)

### TASK 11.33 — CC or Codex — Paper Eval Provenance Tests
**Estimated time: 90–120 minutes**
**Dependency: 11.10 DONE**

Read docs/Sprint_Verification_And_Provenance_Tests.md Part 2 (Paper Evaluation Provenance). Implement tests/test_provenance_paper.py. These tests verify the system's paper assessments are grounded in actual data and correct template/theory application.

Key tests:
- Claim matches record WHY they matched (PROV-P01)
- Claim direction matters — increase ≠ decrease (PROV-P01)
- Effect size matters — d=0.1 ≠ d=1.5 (PROV-P01)
- Contradictions detected correctly (PROV-P02)
- Gaps flagged for unmapped variables (PROV-P02)
- Full provenance chain: data → extraction → matching → tracing → convergence → VOI → report (PROV-P03)
- Cross-pipeline consistency: paper eval and building eval agree directionally (PROV-P04)

---

## COMPLETION CRITERIA

**Minimum viable (end of Rounds 1+2):**
1. ✅ Building eval produces DIFFERENTIATED scores (Salk ≠ open-plan)
2. ✅ Lifespan moderation produces age differences
3. ✅ At least one severe deficit flagged for open-plan office
4. ✅ Paper eval pipeline runs end-to-end with structured claims
5. ✅ Template matching finds correct matches for known papers
6. ✅ Full test suite green

**Full sprint (Round 3 worked examples):**
7. ✅ Ulrich 1984 paper evaluation produces sensible results (11.11)
8. ✅ Building eval regression tests pass (11.13)
9. ✅ Contradiction detection works (11.14)
10. ✅ Gap detection works (11.15)
11. ✅ CLI works for both pipelines (11.16)
12. ✅ Cross-pipeline consistency verified (11.17)
13. ✅ Paper eval validation sweep passes (11.18)
14. ✅ 5-10 test paper claim files created (11.19)
15. ✅ VOI scoring implemented and sensitive to content (11.20 + 11.24)

**Full sprint (Round 3 integration tests):**
16. ✅ Input sensitivity: EVERY major input variable produces output change (11.21)
17. ✅ Function signatures: no mismatched args between caller and callee (11.22)
18. ✅ Web of belief: documented which pipeline queries actually use it (11.23)
19. ✅ VOI: contradicting papers score higher than confirming ones (11.24)
20. ✅ BN health: network operations documented as working or unimplemented (11.25)
21. ✅ Argument tracing: single claim traced end-to-end through entire system (11.26)
22. ✅ Data dependency: system produces DIFFERENT outputs for different data (11.27)
23. ✅ Enum drift: zero drift across all components (11.28)
24. ✅ No placeholders: zero silent default-value returns in pipeline (11.29)
25. ✅ Completeness inventory: machine-readable report of what's wired (11.30)
26. ✅ Sprint verification suite: all S10 and S11 deliverables confirmed working (11.31)
27. ✅ Building provenance: every WIS score traceable to inputs and templates (11.32)
28. ✅ Paper provenance: every assessment traceable to data, theory, and template (11.33)

---

*Sprint 11 Execution Plan — February 17, 2026*
*33 tasks across 3 rounds*
*Estimated total effort: ~40–50 agent-hours*
*Agents: 1 CC + 3 Codex + 1 Antigravity*
*Round 1: FIX BUILDING EVAL WIRING — nothing else until face-validity passes*
*Round 2: Paper evaluation pipeline*
*Round 3: Worked examples + global integration tests that prevent Sprint-10-style silent failures*
