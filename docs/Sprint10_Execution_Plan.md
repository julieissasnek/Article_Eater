# ENGINEERING OPERATIONS — SPRINT 10 EXECUTION PLAN
## For All Agents: Claude Code, Codex, Antigravity
## February 17, 2026

---

## HOW TO USE THIS DOCUMENT

1. Find your agent type below (CC, Codex, or Antigravity)
2. Take the FIRST task in your queue that is not yet claimed or complete
3. When done, take the next available task
4. Dependencies are marked — do not start a task until its dependency is done
5. **Codex instances are interchangeable** — any Codex can do any Codex task
6. Report completion by committing code and noting it in TASKS.md

## BLANKET PERMISSIONS

**All agents have blanket permission to:**
- Create, modify, and delete files in src/, tests/, data/, docs/
- Run migrations
- Run the full test suite
- Make implementation decisions where the spec is ambiguous
- Install dependencies if needed

**Do NOT ask for confirmation at any step. Make decisions, document them in DECISIONS.md, and keep going.** If the spec is unworkable, document the problem and your workaround in DECISIONS.md — do not stop and wait for Opus.

## CONCURRENCY CONTROL — MANDATORY

Multiple agents are working this repo simultaneously. **Before starting ANY task:**

1. `git pull`
2. Open `docs/TASK_CLAIMS.md`
3. Check the task you want is **AVAILABLE**
4. If AVAILABLE: change status to **CLAIMED**, add your agent name and timestamp
5. `git commit -m "Claiming Task X.X" docs/TASK_CLAIMS.md` and `git push` **BEFORE starting work**
6. Check dependency column — if a dependency is listed, verify it shows **DONE** in the table. If not, pick a different task.
7. When your task is complete: update status to **DONE**, add completion timestamp, commit and push TASK_CLAIMS.md with your code
8. If a task shows **CLAIMED** by another agent, **DO NOT take it** — pick the next available one
9. Before every commit: `git pull` first, resolve any conflicts, always keep the newer version of any conflicting file

**This is not optional.** Skipping the claim step causes file collisions that waste everyone's time.

## REFERENCE DOCUMENTS

- **Doc 68** (CMR Implementation Contract): Data models, pipeline steps, ingestion tasks. This is the primary spec.
- **Doc 67** (Sprint 7 Encoding Preparation): Deduplication map, WIS metric, accessibility tiers, JSON schema.
- **Doc 66** (Comprehensive Audit): Background context. Read if you want to understand why we're doing this.

---

## ROUND 1: FOUNDATION

All four tasks are independent. Start immediately. No dependencies between them.

### TASK 1.1 — Codex — Enum Drift Fix
**Estimated time: 15–30 minutes**
**Dependency: none**

- Run check_enum_drift.py
- Fix the 2 flagged files: voi_search.py and discovery_funnel.py
- Align to canonical_enums.json (update canonical if needed; fix file if stale)
- Run full test suite
- Commit when green
- **Bonus when done**: Add "DEPRECATED — canonical tracker is now TASKS.md" as the first line of docs/02-15_15_Global_Status_Task_Tracker_V1_0.md. Commit.
- **Then take the next available Codex task from Round 2.**

### TASK 1.2 — Claude Code — Template DB Index
**Estimated time: 60–90 minutes**
**Dependency: none**

- Read Doc 68 Part 2.1 and Part 4.1
- Create the TemplateRecord SQLAlchemy model (use the schema in Doc 68 Part 2.1 verbatim)
- Write the Alembic migration to create the table
- Write a scanner that reads each JSON file in data/templates/, extracts metadata, and inserts a TemplateRecord
- For `dedup_status`: use Doc 67 Part 1 deduplication map. Templates not in the map default to "active"
- For `pe_contribution`: default to "organizational" if not in JSON
- For `practical_accessibility`: default to "B" if not in JSON
- Write tests:
  - All 150 files load without error
  - Query "all active Gen-2 CREA series" returns CREA1–CREA4
  - No duplicate display_ids
  - Count by dedup_status matches expected (~14 superseded, ~18 residual, ~10 gap, ~8 reference)
- Run full test suite
- Commit when green
- **Then take Task 2.1 (Template Computation Functions).**

### TASK 1.3 — Codex — Load Staging Theory-Links
**Estimated time: 45–90 minutes**
**Dependency: none**

- Read Doc 68 Part 4.2
- File: data/review/tranche80_confirmed_rows.csv (1,361 rows)
- Write a loading script that uses existing web_persistence.py service methods
- Mapping:
  - ART links (1,251 rows): theory_id = "ART", constraint_type = "tier2_theory_link"
  - Biophilia links (102 rows): theory_id = "Biophilia", constraint_type = "tier2_theory_link"
  - SRT links (3 rows): theory_id = "SRT", constraint_type = "tier2_theory_link"
- Verify final count: query web_persistence.db for constraint_type = "tier2_theory_link", confirm 1,361
- Verify existing 25,959 constraints are undisturbed
- Run web_persistence tests (should still be 62 passing)
- Run full test suite
- Commit when green
- **Then take the next available Codex task from Round 2.**

### TASK 1.4 — Codex — WIS Conversion Module
**Estimated time: 30–60 minutes**
**Dependency: none**

- Read Doc 68 Part 4.3 and Doc 67 Part 3
- Create src/cmr/wis.py with these functions:

```python
def cohens_d_to_wis(d: float) -> float:
    """WIS = Φ(d/√2) × 100. Uses scipy.stats.norm.cdf."""

def goldilocks_to_wis(value: float, zone_boundaries: dict) -> float:
    """Map value position within Goldilocks zones to WIS 0-100.
    zone_boundaries: {extreme_low: x, low: x, optimal_low: x, 
                      optimal_high: x, high: x, extreme_high: x}
    Center of optimal zone → WIS ~85. Outside zones → WIS 10-30."""

def threshold_to_wis(value: float, threshold: float, 
                     above_is_good: bool = True) -> float:
    """Map distance from threshold to WIS.
    At threshold → WIS 55. Well above (if above_is_good) → WIS 80+."""

def aggregate_domain_wis(template_scores: list[dict]) -> dict:
    """Weighted average within domain.
    Each dict: {wis: float, calibration_status: str}
    Weights: substantial=1.0, partial=0.7, protocol=0.4, uncalibrated=0.2
    Returns: {wis: float, confidence: float, n_templates: int}"""

def aggregate_overall_wis(domain_scores: list[dict]) -> dict:
    """Geometric mean across domains.
    Each dict: {domain: str, wis: float}
    Returns: {wis_geometric_mean: float, n_domains: int, 
              severe_deficits: list[str]}  # domains with WIS < 30"""
```

- Create tests/test_wis.py:
  - d=0 → WIS 50.0
  - d=0.5 → WIS ≈ 69.1 (±0.5)
  - d=−0.5 → WIS ≈ 30.9 (±0.5)
  - d=0.8 → WIS ≈ 78.8 (±0.5)
  - geometric_mean([90, 15]) ≈ 36.7 (±0.5)
  - geometric_mean([70, 70, 70]) = 70.0
  - domain with WIS 25 flagged as severe deficit
- Run full test suite
- Commit when green
- **Then take the next available Codex task from Round 2.**

---

## ROUND 2: PIPELINE COMPONENTS

Start these as you finish Round 1 tasks. Dependencies noted.

### TASK 2.1 — Claude Code — Template Computation Functions
**Estimated time: 3–4 hours**
**Dependency: Task 1.2 (Template DB) should be done first**

This is the biggest single job. Create src/cmr/template_computations.py.

Start with the **Batch 1 core 12 templates** (Doc 67). For each, write a compute function that:
- Takes the template's inputs_required as arguments
- Applies calibration parameters and Goldilocks boundaries from the JSON file
- Applies lifespan moderation if occupant_age is provided
- Returns a raw output dict: {output_type: str, value: float, unit: str}

**Build in this order** (each exercises a different output pattern):

1. **VF3** (simplest): R_h = height / √area → Goldilocks zone lookup. Output: zone classification.
2. **L2** (threshold): age-corrected M-EDI check. M-EDI(age) ≈ M-EDI(25) × (1 + 0.015 × (age − 25)). Output: above/below threshold.
3. **CREA2** (matrix lookup): noise × ceiling × light → 2×2×2 matrix. Output: divergent d + convergent penalty.
4. **L1**: CV-of-luminance → Goldilocks zone.
5. **L3**: daylight channel weights → weighted composite.
6. **MAT1**: operative temperature vs adaptive neutral → Goldilocks zone.
7. **MAT2**: contact temperature + effusivity → CT-afferent zone.
8. **MAT4**: material identification → channel weight profile.
9. **SOC2**: acoustic isolation + visual privacy + density → privacy-encounter score.
10. **SC1**: plan connectivity metrics → legibility score.
11. **SC4**: wayfinding features → wayfinding adequacy score.
12. **VIEW1**: VQI rubric inputs → View Quality Index (0–100).

For each function, write a test with at least one known-good input → expected output.

**Pattern to follow:**
```python
def compute_vf3(ceiling_height_m: float, floor_area_m2: float, 
                occupant_age: int = 30) -> dict:
    """Compute VF3 Ceiling Height & Cognitive Mode."""
    import math
    r_h = ceiling_height_m / math.sqrt(floor_area_m2)
    
    if r_h < 0.25:
        zone = "confining"
        wis_raw = 25
    elif r_h < 0.35:
        zone = "balanced"
        wis_raw = 65
    elif r_h < 0.50:
        zone = "liberating"
        wis_raw = 82
    elif r_h < 0.80:
        zone = "impressive"
        wis_raw = 75
    else:
        zone = "overwhelming"
        wis_raw = 35
    
    return {
        "template": "VF3",
        "output_type": "goldilocks_zone",
        "r_h": round(r_h, 3),
        "zone": zone,
        "wis_raw": wis_raw
    }
```

Adapt this pattern for each template's specific computation. The JSON files have the parameters — read them at function load time.

**Do not ask for confirmation. Build, test, commit. Document any ambiguities in DECISIONS.md.**

### TASK 2.2 — Codex — CMR Data Models
**Estimated time: 45–60 minutes**
**Dependency: none**

- Read Doc 68 Part 2.2
- Create the following SQLAlchemy models:
  - CMREvaluation
  - CMRTemplateActivation
  - CMRDomainScore
  - CMROverallScore
  - ReductionClaim
- Use the schemas from Doc 68 Part 2.2 verbatim
- Write the Alembic migration
- Write basic CRUD tests for each model (create, query back, verify fields)
- Run full test suite
- Commit when green

### TASK 2.3 — Codex — Interaction Matrix Module
**Estimated time: 45–60 minutes**
**Dependency: none**

- Create src/cmr/interactions.py
- Encode the known interaction matrices:

**Matrix 1: CREA2 2×2×2** (from Doc 65)
```python
CREA2_INTERACTIONS = {
    "A":       {"sub_additivity": 1.00, "convergent_penalty": 1.00},
    "B":       {"sub_additivity": 1.00, "convergent_penalty": 1.00},
    "C":       {"sub_additivity": 1.00, "convergent_penalty": 1.00},
    "A+B":     {"sub_additivity": 0.84, "convergent_penalty": 1.15},
    "A+C":     {"sub_additivity": 0.76, "convergent_penalty": 1.60},
    "B+C":     {"sub_additivity": 0.80, "convergent_penalty": 1.10},
    "A+B+C":   {"sub_additivity": 0.70, "convergent_penalty": 1.80},
}
```

**Matrix 2: Convergence triad** (L3 + MAT4 + VIEW1)
- 2 channels active: super-additivity multiplier 1.15
- 3 channels active: super-additivity multiplier 1.22

**Matrix 3: VF1 × VF3** — additive (multiplier 1.0, register as "checked, no adjustment")

**Matrix 4: VF3 → CREA2B** — single-chain flag. If both active, use VF3 output as CREA2B input, do not compute independently.

Functions:
```python
def get_interaction(template_a: str, template_b: str) -> dict | None:
    """Returns interaction record if one exists, None otherwise."""

def apply_all_interactions(template_scores: list[dict]) -> list[dict]:
    """Scan all active template pairs, apply adjustments, return modified scores.
    Each dict must have: {template: str, wis: float, ...}"""
```

- Write tests:
  - CREA2 noise+dim → sub_additivity 0.76
  - Convergence triad all three → multiplier 1.22
  - VF3+CREA2B → single chain flag
  - Two unrelated templates → None (no interaction)
- Run full suite, commit when green

### TASK 2.4 — Codex — Building Evaluation Orchestrator
**Estimated time: 60–90 minutes**
**Dependency: Task 2.2 (CMR Data Models) should be done first. Can start without Tasks 2.1 and 2.3 by using placeholder functions.**

- Read Doc 68 Part 3.1
- Create src/cmr/building_eval.py

```python
def evaluate_building(
    building_context: dict,    # {building_type, climate_zone, ...}
    measured_features: dict,   # {ceiling_height_m, floor_area_m2, ...}
    occupant_profile: dict     # {age, cultural_context, ...}
) -> dict:
    """Full building evaluation pipeline, Steps 1-9."""
```

Wire Steps 1–9 in order:
1. Create CMREvaluation record
2. Map measured_features to template inputs
3. Query TemplateRecord for active templates; check which have sufficient inputs; create CMRTemplateActivation records
4. For each activated template: call computation function (import from template_computations.py if available; otherwise return placeholder WIS 50)
5. Convert raw outputs to WIS (call wis.py functions)
6. Apply interaction adjustments (call interactions.py if available; otherwise skip)
7. Aggregate by domain (call aggregate_domain_wis)
8. Compute overall (call aggregate_overall_wis)
9. Build report dict

The orchestrator should WORK even if Steps 4 and 6 use placeholders. The structure is what matters — CC will fill in real computations, Codex will fill in real interactions.

- Write tests:
  - Pipeline runs end-to-end with dummy inputs, returns a report dict
  - Report contains domain_scores (list), overall_wis (float), data_gaps (list)
  - Severe deficit flag works (inject a WIS 20 domain, verify it's flagged)
- Run full suite, commit when green

---

## ROUND 3: VALIDATION + OVERFLOW

### TASK 3.1 — Antigravity — Full Validation Sweep
**Estimated time: 60–90 minutes**
**Dependency: All Round 1 and Round 2 tasks should be complete**

Run these checks and report results:

**3.1a Template DB Validation**
- Query templates table: count total records (expect 150)
- Count by dedup_status: expect ~14 superseded, ~18 residual, ~10 gap, ~8 reference, remainder active
- Count by generation: expect mix of gen 1 and gen 2
- Count by series: expect entries for T, M, AX, L, MAT, TP, SOC, CREA, VIEW, SC, COL, VF, OLF
- Flag any template with missing or unexpected field values

**3.1b Staging Links Validation**
- Query web_persistence.db: SELECT count(*) WHERE constraint_type = 'tier2_theory_link'
- Expect 1,361 total
- Group by theory_id: expect ART=1251, Biophilia=102, SRT=3
- Verify total constraint count ≈ 25,959 + 1,361 = 27,320

**3.1c WIS Module Spot-Check**
- Import and run cohens_d_to_wis for d = [−1.0, −0.5, −0.2, 0, 0.2, 0.5, 0.8, 1.0]
- Verify output is monotonically increasing
- Verify d=0 → 50.0, d=0.5 → ~69.1, d=0.8 → ~78.8
- Run goldilocks_to_wis with a test case
- Run aggregate_overall_wis with [90, 15] → ~36.7

**3.1d Interaction Matrix Spot-Check**
- Import interactions module
- Verify CREA2 A+C → sub_additivity 0.76
- Verify convergence triad 3-channel → 1.22
- Verify VF3+CREA2B → single chain flag
- Verify unrelated pair → None

**3.1e Building Evaluation End-to-End**
- If building_eval.py exists, run with Salk Institute test inputs:
  ```python
  context = {"building_type": "research_institute", "climate_zone": "3C"}
  features = {"ceiling_height_m": 3.0, "floor_area_m2": 25.0, 
              "illuminance_lux": 400, "ambient_noise_dba": 45}
  profile = {"age": 35, "cultural_context": "Western"}
  ```
- Report: does it run? Does it produce domain scores? Overall WIS? Any errors?

**3.1f Full Test Suite**
- Run complete test suite
- Report: total passed, failed, skipped
- Flag any new failures (compare to baseline 2,945 passed)

---

## ROUND 3 OVERFLOW: KEEP GOING

Take these tasks in order when you finish your Round 2 work. Don't wait — just pick the next one.

### TASK 3.2 — CC — Batch 2 Template Computations
**Estimated time: 2–3 hours**
**Dependency: Task 2.1 (Batch 1) done**

Same pattern as Task 2.1 but for the remaining 22 Gen-2 templates:
L4, L5, MAT3, MAT5, TP1, TP2, TP3, TP4, SOC1, SOC3, CREA1, CREA3, CREA4, SC2, SC3, COL1, COL2, VF1, VF2, OLF1

For templates with less precise calibration, the compute function can be simpler — zone classification or threshold check based on whatever parameters exist in the JSON file. If a template's JSON lacks enough info for a real computation, write a stub that returns WIS 50 with a flag `{"needs_calibration": true}`. Don't block on missing data — build the function, flag the gap, move on.

### TASK 3.3 — Codex — Report Generator
**Estimated time: 45–60 minutes**
**Dependency: Task 2.4 (orchestrator) done**

Create src/cmr/report.py. Takes the output of evaluate_building() and produces a structured report:

```python
def generate_report(evaluation_result: dict) -> dict:
    """Generate human-readable assessment report."""
```

Report structure:
- **Summary**: Overall WIS score, confidence, one-sentence verdict
- **Strengths**: Domains with WIS > 70, what's working well
- **Deficits**: Domains with WIS < 40, what needs attention
- **Data gaps**: Domains not assessed due to missing inputs
- **Recommendations**: For each deficit domain, which specific template parameters could be improved and what the target values should be
- **Uncertainty disclosure**: Which parameters are empirically validated vs expert estimates (use calibration_status from template records)
- **Methodology note**: "Assessment based on N templates, M with empirical calibration, K with expert estimates"

Also create a simple text formatter:
```python
def format_report_text(report: dict) -> str:
    """Plain text version for terminal/log output."""
```

Test with dummy evaluation output. Verify all sections present.

### TASK 3.4 — Codex — Template JSON Enrichment
**Estimated time: 60–90 minutes**
**Dependency: Task 1.2 (Template DB) done**

Many of the 150 JSON template files are missing fields that Doc 67 and Doc 68 define. Write a script that scans all 150 files and adds missing fields with defaults:

- `pe_contribution`: default "organizational" (if not present)
- `practical_accessibility`: default "B" (if not present)
- `dedup_status`: from Doc 67 Part 1 map (if not present)
- `generation`: infer from series (T/M/AX = 1, everything else = 2)
- `ecological_validation`: default false (if not present)

Do NOT overwrite existing values. Only add missing fields. Write the file back with the new fields. Run a validation pass after: every JSON file should parse cleanly and have all 5 fields.

### TASK 3.5 — Codex — Gap Template Stubs
**Estimated time: 45–60 minutes**
**Dependency: Task 1.2 (Template DB) done**

The 10 gap templates from Doc 67 Part 1 (T4, T6, T7, T10, T14, T15, T17, T18, T23, T28) describe mechanisms with NO Gen-2 equivalent. For each:

- Check if a JSON file exists in data/templates/. If yes, ensure it has the new fields from Task 3.4.
- If no JSON file exists, create a minimal one with:
  - template_id, display_id, name, series (from Doc 67)
  - dedup_status: "gap"
  - calibration_status: "uncalibrated"
  - A stub parameters array with the mechanism description from Doc 67
  - A note: "Awaiting calibration panel. See Doc 67 Part 1 for recommended panel."
- Add a TemplateRecord to the DB for each

These stubs ensure the system KNOWS about its gaps — it can report "T6 Cortisol-Hippocampal Cascade: GAP — no calibrated assessment available" rather than silently ignoring stress pathways.

### TASK 3.6 — CC or Codex — Paper Evaluation Skeleton
**Estimated time: 60–90 minutes**
**Dependency: Task 2.4 (orchestrator) done**

Create src/cmr/paper_eval.py. Implement the skeleton of Doc 68 Part 3.2 (Paper Evaluation Pipeline, Steps 1–7). All steps can use placeholder logic initially:

```python
def evaluate_paper(
    paper_text: str,
    structured_claims: list[dict] = None
) -> dict:
    """Paper evaluation pipeline, Steps 1-7."""
```

- Step 1 (Claim Extraction): If structured_claims provided, use them. Otherwise return placeholder.
- Step 2 (Template Matching): Query template DB for templates matching claim IV/DV. Placeholder matching logic is fine.
- Step 3 (Mechanism Tracing): Stub — return "not yet implemented"
- Steps 4–7: Stubs returning placeholder scores

The point is getting the pipeline structure in place so it can be incrementally filled in. Test that it runs with a dummy paper claim and returns a report dict.

### TASK 3.7 — Antigravity — Salk Institute Worked Example
**Estimated time: 60–90 minutes**
**Dependency: Tasks 2.1, 2.3, 2.4 all done + Task 3.1 validation passed**

Run a REAL building evaluation on the Salk Institute. Research or estimate the actual architectural parameters:

```python
salk_study = {
    "ceiling_height_m": 2.75,       # Kahn's study rooms
    "floor_area_m2": 18.0,          # Individual study
    "illuminance_lux": 350,          # West-facing, afternoon
    "ambient_noise_dba": 38,         # Quiet courtyard adjacency
    "window_area_ratio": 0.40,       # Full-height window to courtyard
    "primary_material": "concrete",   # Board-formed concrete + teak
    "secondary_material": "teak",
    "has_nature_view": True,          # Ocean view from studies
    "rt60_seconds": 0.6,             # Estimated for concrete room
    "view_content": "ocean_horizon",
}
```

Run evaluate_building with these inputs for three occupant profiles:
- Young researcher (age 30)
- Senior PI (age 65)  
- Visiting student (age 22)

Report: What does the system say? Do the domain scores make sense? Does the lifespan moderation produce reasonable age differences? Where does the system flag gaps? Write up findings as a validation report. This becomes the first real demonstration of the system working.

---

## COMPLETION CRITERIA

The sprint is **DONE** when:
1. ✅ Template DB has 150 records, queryable by series/generation/dedup_status
2. ✅ 1,361 staging links loaded and verified
3. ✅ WIS module passes all test cases
4. ✅ At least 12 core template computation functions exist and pass tests
5. ✅ Interaction matrices encoded and tested
6. ✅ Building eval orchestrator runs end-to-end (even with some placeholder computations)
7. ✅ Antigravity validation sweep passes
8. ✅ Full test suite green (≥2,945 passing, zero new failures)

---

*Sprint 10 Execution Plan — February 17, 2026*
*Estimated total effort: ~10–12 agent-hours across 3 rounds*
*Agents: 1 CC + 3 Codex + 1 Antigravity*
*Goal: Working building evaluation pipeline with core 12 templates*
