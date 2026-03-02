# ATLAS Figure-Document Consistency System

**Created**: 2026-03-02  
**Version**: V22.0.0  
**Status**: Operational

## Overview

This system validates that all 24 master document figures (M-1 through M-24) remain consistent with the current source text in `docs/master_doc_parts/`. It uses **contract-driven verification**: each figure declares its data dependencies with specific grep patterns, and a validation script checks that these patterns are found in the corresponding Part files.

## System Components

### 1. FIGURE_DEPENDENCIES.json

**Location**: `contracts/FIGURE_DEPENDENCIES.json`

A JSON contract declaring all data dependencies for the 24 figures. Each figure entry includes:

- **Figure metadata**: ID, title, figure_number (M-1 to M-24), description
- **Source parts**: List of Part files (PART_I_EXPLANATION_GAP.md, etc.) containing the figure's source material
- **Dependencies**: 1-8 per figure, each specifying:
  - `type`: STRUCTURE, FORMULA, PARAMETER, TAXONOMY, MECHANISM, FRAMEWORK, etc.
  - `claim`: The exact claim the figure encodes
  - `grep_pattern`: Regex pattern (case-insensitive) to find evidence in source text
  - `severity`: CRITICAL (blocking), MINOR (quality-of-life)
  - `notes`: Why this dependency matters

### 2. check_figure_consistency.py

**Location**: `scripts/check_figure_consistency.py`

A command-line validation tool that:

1. Loads `FIGURE_DEPENDENCIES.json`
2. For each figure, searches its source Part files using the dependency patterns
3. Reports staleness: **CURRENT** (all found), **STALE-MINOR** (some non-critical deps missing), **STALE-CRITICAL** (any critical deps missing)
4. Supports targeted checking and WCAG-accessible color output (cyan/yellow/green, never dark blue)
5. Can append stale findings to `TASKS.md` for tracking

## Usage

### Quick Check (Critical Dependencies Only)
```bash
python scripts/check_figure_consistency.py --quick
```
Faster scan; only validates CRITICAL dependencies. Good for CI/CD pipelines.

**Exit codes:**
- 0: All critical deps found
- 2: Any critical dep missing

### Full Check (All Dependencies)
```bash
python scripts/check_figure_consistency.py --full
```
Comprehensive validation of all CRITICAL and MINOR dependencies.

**Exit codes:**
- 0: All deps found (CURRENT)
- 1: Some MINOR deps missing (STALE-MINOR)
- 2: Any CRITICAL dep missing (STALE-CRITICAL)

### Single Figure Check
```bash
python scripts/check_figure_consistency.py --figure m4_projection_formula -v
```
Detailed check of just one figure with verbose output showing matched context.

### Add Stale Findings to TASKS.md
```bash
python scripts/check_figure_consistency.py --full --add-tasks
```
Runs full check and appends any stale dependencies to `TASKS.md` with a table for tracking.

### Verbose Output
```bash
python scripts/check_figure_consistency.py --full -v
```
Shows detailed info for each dependency: pattern, matched text, source file.

## Figure Coverage

All 24 master figures are tracked:

### Architecture & Core (M-1 to M-3)
- **M-1**: Three computational layers + IE-DPT envelope
- **M-2**: Epistemic network architecture and warrant taxonomy
- **M-3**: Bayesian network structure and CPT linkage

### Credence & Computation (M-4 to M-6)
- **M-4**: Projection formula d·ω·δ·logit(p_lab) → p_target
- **M-5**: Warrant strength decomposition
- **M-6**: Population transfer (δ) heatmap

### Domain Panels (M-7 to M-18)
- **M-7**: VISUAL-I (fractal dimension, contour, proportions)
- **M-8**: LIGHT-I (dual-pathway, circadian, convergence)
- **M-9**: THERMAL-I (adaptive comfort, culture calibration)
- **M-10**: ACOUSTIC-I (speech intelligibility, masking)
- **M-11**: AIR_QUALITY-I (CO2, ventilation)
- **M-12**: BIOPHILIA-I (nature views, restoration)
- **M-13**: WAYFINDING-I (legibility, landmarks)
- **M-14**: CIRCADIAN_ARCH-I (entrainment windows, zeitgebers)
- **M-15**: ERGONOMIC_WORKSPACE-I (heights, postures)
- **M-16**: VEGETATION_MANAGEMENT-I (plant welfare, maintenance)
- **M-17**: PRIVACY_SOUND-I (speech privacy, SII)
- **M-18**: EMERGENCY_EGRESS-I (exit clarity, wayfinding stress)

### Operations & Summary (M-19 to M-24)
- **M-19**: AESHI operations pipeline (5 stages)
- **M-20**: Credence aggregation (serial & parallel)
- **M-21**: Explanatory boost mechanism
- **M-22**: Evidence dashboard (beliefs, frameworks, warrants)
- **M-23**: Theory framework taxonomy
- **M-24**: Gap analysis by domain

## Dependency Types

| Type | Meaning | Example |
|------|---------|---------|
| STRUCTURE | Architectural/organizational claim | "Three computational layers: EN, BN, IE-DPT" |
| FORMULA | Mathematical expression | "logit(p_target) = d·ω·δ·logit(p_lab)" |
| DEFINITION | Formal definition of a term | "Warrant strength ω = study quality..." |
| PARAMETER | Quantitative specification | "Fractal dimension peaks at D ≈ 1.3" |
| MECHANISM | Causal explanation | "Gaps feed back upward to trigger searches" |
| WORKED_EXAMPLE | Concrete numerical instance | "p_lab=0.80, d=0.80, ω=0.65, δ=0.85 → p_target=0.68" |
| TAXONOMY | Classification system | "Seven warrant types: CONSTITUTIVE, MECHANISM, ..." |
| FRAMEWORK | Theoretical grounding | "Three T1 frameworks: Predictive Processing, ..." |
| HIERARCHY | Ordering/priority relationships | "Light > Temperature >> Activity in entrainment" |
| MODEL | Complex multi-component system | "Daylight multi-channel convergence (6 channels)" |
| MAPPING | Set of value assignments | "CONSTITUTIVE d:0.95; MECHANISM d:0.80; ..." |
| TRADEOFF | Design decision involving tension | "Plant welfare vs. air quality benefit" |
| CALIBRATION | Lookup table or reference values | "Delta tables for population pairs" |
| ADJUSTMENT | Modification rule | "Reduce δ by 0.10-0.20 for neurodiverse" |
| COUNT | Numeric inventory | "3,420+ scientific findings in Evidence Store" |
| RELATIONSHIP | Association between entities | "Warrant type τ independent from strength ω" |
| RANGE | Interval or bound specification | "ω ∈ (0, 1)" |
| PATTERN | Observable regularity | "Functional claims lower δ than preference claims" |
| INVENTORY | Documentation of collected items | "13 residual gaps; 7 T1.5 candidates" |
| CONSTRAINT | Requirement or limitation | "IE-DPT determines which processes activate" |
| WARRANT_STATUS | Epistemic readiness classification | "L2 ESTABLISHED; L3 SUPPORTED (experiment pending)" |
| WARRANT_DISTRIBUTION | Frequency/proportion data | "Panel warrant profile: ~70% EMPIRICAL_ASSOCIATION" |
| BIOLOGY | Biological mechanism/anatomy | "TRPM8 cool threshold ≈ 28°C (Craig neuroanatomy)" |
| METABOLISM | Metabolic process specification | "BAT cost: 2-5% per °C below TNZ" |
| EMPIRICAL_CEILING | Honest bound on predictive power | "Coburn metrics: R²=0.35 (0.42 with color)" |
| LOOP | Feedback or iterative process | "AESHI pipeline: gap detection loops back to GATHER" |

## Severity Levels

| Severity | Meaning | Exit Code | Action |
|----------|---------|-----------|--------|
| CRITICAL | Core architectural claim; figure is wrong if missing | 2 | Must fix immediately; blocks downstream work |
| MINOR | Supporting detail; figure is correct but incomplete | 1 | Track in TASKS.md; schedule refinement |

## Example: M-4 Projection Formula

The M-4 figure encodes the projection formula with 6 dependencies:

```json
{
  "m4_projection_formula": {
    "title": "Projection Formula: d·ω·δ·logit(p_lab) → p_target",
    "figure_number": "M-4",
    "source_parts": ["PART_IV_CREDENCE.md"],
    "dependencies": [
      {
        "type": "FORMULA",
        "claim": "logit(p_target) = d·ω·δ·logit(p_lab)",
        "grep_pattern": "logit\\(p_target\\)|d.*ω.*δ.*logit|projection.*formula",
        "severity": "CRITICAL",
        "notes": "Fundamental credence computation"
      },
      {
        "type": "DEFINITION",
        "claim": "Warrant strength ω: study quality (replication, sample, methods, rigor)",
        "grep_pattern": "warrant strength.*ω|ω.*replication|ω.*quality",
        "severity": "CRITICAL",
        "notes": "Reducible by better evidence"
      },
      ...
    ]
  }
}
```

When you run `check_figure_consistency.py --figure m4_projection_formula`, it:

1. Reads each dependency's grep pattern
2. Searches PART_IV_CREDENCE.md for matches (case-insensitive)
3. Reports found/not-found with context snippets
4. Outputs overall status: CURRENT (all 6 found), STALE-MINOR, or STALE-CRITICAL

## Integration with TASKS.md

When you discover a figure is STALE-CRITICAL, run:

```bash
python scripts/check_figure_consistency.py --full --add-tasks
```

This appends a new section to `TASKS.md`:

```markdown
## Figure Consistency Check - Stale Dependencies

| Figure | Type | Claim | Pattern | Severity |
|--------|------|-------|---------|----------|
| M-14 | HIERARCHY | Zeitgeber strength: light > temperature >> activity | `zeitgeber.*strength\|light.*temperat...` | MINOR |
| M-22 | COUNT | Total belief/edge count in Epistemic Network | `total.*belief\|total.*edge\|network.*si...` | MINOR |
| M-22 | COVERAGE | Domain panel coverage ratings (★ Minimal, ...) | `coverage.*rating\|★.*Minimal\|★★.*Part...` | MINOR |
```

Then you can prioritize updates based on figure importance and severity.

## Workflow

### When Master Doc Changes

After updating any Part file, run:

```bash
python scripts/check_figure_consistency.py --quick
```

If any CRITICAL deps fail, investigate and fix:
1. Update the figure or Part file to match
2. Or update the dependency pattern if it was overly specific
3. Rerun to confirm CURRENT status

### Before Major Releases

```bash
python scripts/check_figure_consistency.py --full
```

Ensure all figures are CURRENT. If STALE-MINOR, document in release notes or backlog as known gaps.

### CI/CD Integration

Add to pipeline:

```bash
python scripts/check_figure_consistency.py --quick || exit $?
```

This ensures critical figures never go stale unnoticed.

## Design Principles

1. **Contract-First**: Figures declare their requirements upfront; don't rely on manual inspection
2. **Regex Patterns**: Patterns are human-readable and maintainable; easy to adjust if source text rephrasing occurs
3. **Case-Insensitive**: Tolerates minor wording variations
4. **WCAG Compliance**: Uses cyan/yellow/green (not dark blue) for accessibility
5. **Graceful Degradation**: MINOR gaps don't block; CRITICAL gaps stop immediately
6. **Auditable Trail**: All matched context is shown; patterns are transparent

## Known Limitations

1. **Pattern Fragility**: Overly specific patterns (e.g., exact number matching) may fail if source is reformatted; use ranges where safe
2. **False Negatives**: Complex claims may not be directly stated; some patterns require paraphrasing tolerance
3. **Population Coverage**: Patterns currently cover only the 24 main figures; future work could extend to sub-figures
4. **Version Tracking**: No diff/blame tracking across versions; relies on timestamp for staleness assessment

## Future Enhancements

- [ ] Generate figure dependency patterns automatically from figure metadata
- [ ] Track pattern changes and auto-suggest updates when sources refactor
- [ ] Create sub-figure dependency contracts for component-level validation
- [ ] Integrate with documentation generation pipeline to auto-regenerate figures
- [ ] Add confidence scores to dependencies based on pattern match quality

## Contact

Questions or issues: See TASKS.md for ongoing figure consistency work.

---

**Last Updated**: 2026-03-02  
**Status**: Operational. All 24 figures tracked. M-14 and M-22 have MINOR gaps (expected during active authoring).
