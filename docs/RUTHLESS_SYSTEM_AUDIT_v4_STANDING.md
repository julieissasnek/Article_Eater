# RUTHLESS SYSTEM AUDIT v4 — STANDING HEALTH CHECK
## Post-Panel-Calibration Verification & Ongoing CI/CD Validation
## February 23, 2026
## Run in: CC, then AG or Gemini, then Codex. Cross-validate findings.

---

# CONTEXT

This system has completed all 12 panel calibrations (103 templates calibrated),
a T1.5 theory audit and expansion panel, a ceiling recalibration panel, and
extensive structural repairs. The current system state is:

- **T1 frameworks**: 10 (PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI)
- **T1.5 theories**: 14 formally reduced (ART, SRT, Biophilia, Prospect-Refuge,
  Privacy Regulation, Kaplan Preference Matrix, Adaptive Thermal Comfort,
  Space Syntax, Soundscape Theory, Place Attachment, Fractal Fluency,
  Awe/Kama Muta, BRECVEMA, Flow Theory)
- **Total template JSON files**: 208
- **Calibrated templates**: 103 (all passing validation)
- **Scaffold-tier templates**: 105 (not yet panel-calibrated)
- **Completed panels**: 12 (VISUAL-I, SPATIAL-I, LIGHT-I, STRESS-I, SOCIAL-I,
  MEMORY-I, MULTI-I, CREATIVE-I, MUSIC-I, THERMAL-I, NEUROMOD-I, CROSSCUT-I)
- **T1.5 coverage**: 30/103 have formal T1.5 parent theories; 73 correctly have
  empty arrays (not every mechanism needs a T1.5 organizing theory)
- **Ceiling status**: Ceilings are Bayesian soft priors, NOT hard caps.
  Panel-reviewed exceedances are documented and accepted.

**The same rules apply as always: Do not be polite. Do not soften findings.
Cite file paths and line numbers. Quote conflicting passages verbatim.**

---

# SECTION 1: EXECUTE THE AUTOMATED GATES

Do not trust self-reports. Run the following commands sequentially and report
the literal output. If any gate CRASHES (exit code ≠ 0), immediately halt the
audit and report the exact trace.

## 1.1 Bridge Ceiling Lint (A-01 CI/CD)

Run the ceiling lint test:
```
pytest tests/test_bridge_ceilings.py -v
```

**IMPORTANT — REVISED EPISTEMICS (Feb 23, 2026):**

Bridge warrant ceilings are **Bayesian soft priors**, not hard constraints.
They represent the DEFAULT maximum confidence for a given warrant type.
When a panel assigns confidence ABOVE the ceiling, this is an epistemic
signal that the evidence is stronger than the warrant type's default.

The correct response to a ceiling exceedance is **panel review**, resulting
in one of three outcomes:
1. **Warrant upgrade** — the panel decides the evidence justifies a stronger
   warrant type (e.g., MECHANISM → CONSTITUTIVE). The ceiling is then
   naturally satisfied.
2. **Documented override** — the panel documents why the confidence exceeds
   the default ceiling (stored in `ceiling_override_rationale` field). The
   test accepts these.
3. **Confidence reduction** — the panel agrees the confidence was miscalibrated
   and reduces it.

The test should **PASS** even if ceiling violations exist, provided they have
been reviewed. Specifically:
- Violations with `ceiling_override_rationale` populated → ACCEPTED
- Violations with `ceiling_status == "exceeds"` → ACCEPTED (flagged for panel)
- Violations with neither → reported as **pytest warnings** (NOT failures)

**DO NOT run `scripts/auto_cap_ceilings.py` or any auto-clamping script.**
These scripts destructively clamp confidence values and destroy panel
calibrations. They are quarantine candidates.

**Verify:**
1. Does the test pass? (It should — test passes as long as lint script runs)
2. How many total ceiling exceedances are reported?
3. How many are REVIEWED (have override rationale or ceiling_status)?
4. How many are UNREVIEWED? (These need panel attention, but are NOT blockers)
5. Does `scripts/lint_bridge_ceilings.py` operate in REPORTING-ONLY mode?
   (It should NOT auto-fix anything)

**The ceiling hierarchy for reference:**
- CONSTITUTIVE: 0.75
- MECHANISM: 0.60
- EMPIRICAL_COVARIANCE: 0.60
- FUNCTIONAL: 0.50
- CAPACITY: 0.45
- THEORETICAL_DEFAULT: 0.40
- ANALOGICAL: 0.35

## 1.2 The Canonical Variable Enforcer (A-02 CI/CD)

Run the ontology enforcer:
```
pytest tests/test_canonical_variables.py -v
```
- Does the ontology check pass cleanly?
- Run `python3 scripts/lint_variables.py` directly. Does it confirm that all
  legacy variables sit safely within the `UNMAPPED_LEGACY` bucket inside
  `canonical_variables.json`?

## 1.3 Template Validation (A-03 CI/CD)

Run the template validator:
```
python3 scripts/validate_templates.py
```
- Do all 103 calibrated templates pass?
- What fields are checked? (bridge_warrant, confidence, t1_frameworks,
  mechanism_chain, tier, cross_template_interactions)
- Are scaffold-tier templates reported separately? (They have different
  requirements)

## 1.4 Baseline System Tests (A-10 CI/CD)

Run the core test suite:
```
pytest tests/ -v -k "not test_bridge_ceilings and not test_canonical_variables"
```
- Does the entire suite pass green?
- Report: passed, failed, skipped counts

---

# SECTION 2: THEORETICAL ARCHITECTURE vs RUNTIME REALITY

## 2.1 The Belief Graph Integrity

Execute: `PYTHONPATH=. python3 -m src.services.web_accumulator stats`
- Report the total belief count
- Are there any `unresolved` junk items sneaking back into the pipeline?

## 2.2 The Toulmin Justification Schema

Inspect 5 calibrated templates from different panels (e.g., one each from
SOCIAL-I, VISUAL-I, MULTI-I, MEMORY-I, MUSIC-I). For each template:

1. Does each mechanism_chain step contain a `justification` object with:
   `data` (array), `backing` (string), `qualifier` (string),
   `rebuttal` (string), `competing_accounts` (array), `depth_tier` (string)?
2. Are any steps missing justification entirely?

**NOTE**: The Toulmin fields live INSIDE each mechanism_chain step under
the key `justification`, not as a separate top-level `toulmin_justification`
field. The structure is:
```json
{
  "mechanism_chain": [
    {
      "step": 1,
      "warrant": "MECHANISM",
      "confidence": 0.60,
      "justification": {
        "data": [...],
        "backing": "...",
        "qualifier": "...",
        "rebuttal": "...",
        "competing_accounts": [...],
        "depth_tier": "A"
      }
    }
  ]
}
```

## 2.3 Theory Tier Architecture

### T1 Framework Assignments
- Do all 103 calibrated templates have non-empty `t1_frameworks` arrays?
- Do all assigned T1 codes belong to the canonical 10?
  (PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI)

### T1.5 Theory Assignments
- How many templates have non-empty `t1_5_parent_theories`? (Should be ~30)
- Do all assigned T1.5 theories belong to the canonical 14?
  (ART, SRT, Biophilia, Prospect_Refuge, Privacy_Regulation,
  Kaplan_Preference_Matrix, Adaptive_Thermal_Comfort, Space_Syntax,
  Soundscape, Place_Attachment, Fractal_Fluency, Awe_Kama_Muta,
  BRECVEMA, Flow_Theory)
- Are there any FABRICATED theory names in `t1_5_parent_theories`?
  (Names like "Dose_Response_Theory", "Individual_Differences",
  "Color_Psychology", "Virtual_Reality_Theory" are NOT formal T1.5 theories
  and should NOT appear.)
- Is there a `t1_5_candidates` field containing plausible-but-unreduced
  theories? (These are held for future panel review, not formal assignments.)

### Ceiling Review Status
- How many templates have mechanism chain steps with `ceiling_status: "exceeds"`?
- Do ALL of these have corresponding `ceiling_override_rationale`?
- Reference document: `docs/CEILING_RECALIBRATION_PANEL_Feb23.md`

## 2.4 Cross-Template Interactions

- Do all 103 calibrated templates have `cross_template_interactions`?
- Are there any with empty or placeholder interactions?
- For 5 randomly chosen interaction pairs: does the referenced target
  template actually exist in `data/templates/`?

## 2.5 Theory Profiles & Routing

Review the internal profiles at `src/cmr/theory_profiles/`.
- Are all 10 T1 formal profiles present and returning valid `get_profile()` dicts?
- Can the extraction pipeline successfully load these targets?

---

# SECTION 3: BRIDGE WARRANT CEILING DEEP AUDIT

**THIS SECTION REPLACES THE OLD "ZERO VIOLATIONS" REQUIREMENT.**

The old approach (auto-clamping all confidences to ceiling maximums) was
epistemically destructive. It destroyed information about when panels judged
evidence to be stronger than the warrant type's default. The current approach
preserves this information and requires human/panel review.

**Verify the following:**

1. **No auto-clamping scripts are active.** The following scripts should be
   quarantined or marked as deprecated:
   - `scripts/auto_cap_ceilings.py`
   - `scripts/repair_bridge_ceilings.py`
   - `scripts/repair_bridge_ceilings2.py`
   These scripts must NEVER be run against the templates again.

2. **The lint script is reporting-only.** Run:
   ```
   python3 scripts/lint_bridge_ceilings.py --report data/ceiling_violation_report.json
   ```
   Verify that:
   - It produces a JSON report with violation details
   - It does NOT modify any template files
   - It prints "REPORTING ONLY" in its output header

3. **Panel review documentation exists.** Check:
   - `docs/CEILING_RECALIBRATION_PANEL_Feb23.md` — full panel deliberation
   - `data/ceiling_decisions.json` — machine-readable decisions
   - Each decision is one of: warrant_upgrade, accept_override, reduce_confidence

4. **Override rationales are present.** For every ceiling exceedance in the
   template corpus, verify that EITHER:
   - The step has `ceiling_override_rationale` (a string explaining why), OR
   - The step has `ceiling_status: "exceeds"` (flagged for panel review)
   Exceedances with NEITHER field are unreviewed and need attention.

---

# SECTION 4: DATA QUALITY SPOT CHECKS

## 4.1 Per-Template Compliance (Sample of 10)

Pick 10 calibrated templates from different panels. For each, verify:

| Check | Requirement |
|-------|-------------|
| `mechanism_chain` | Non-empty array, each step has from/to/warrant/confidence |
| `justification` | Each step has Toulmin justification with data/backing/qualifier/rebuttal |
| `bridge_warrant` | Present and in canonical enum |
| `confidence` | Present and numeric |
| `t1_frameworks` | Non-empty array, all codes in canonical 10 |
| `tier` | Present, one of A/B/C |
| `cross_template_interactions` | Present and non-empty |
| `calibration_status` | "calibrated" |
| `panel_source` | Present and identifies source panel |

## 4.2 Cross-Template Variable Sharing

Pick 5 known cross-template interaction pairs. For each pair:
1. Does the output variable of template A use the SAME canonical name as
   the input variable of template B?
2. Are the confidence values at the interface plausible (not 1.0 or 0.0)?

## 4.3 Credence Formula Consistency

Search every document in docs/ for the three-factor formula:
`P(CNFA effect) = P(parent theory) × P(bridge) × P(CNFA-specific)`

Is it stated identically everywhere? Does code implement it correctly?
Does `compute_bridged_credence()` in `bridge_warrants.py` match the spec?

---

# SECTION 5: THE FINAL DETERMINATION

Based on your execution of the automated gates, your structural inspection,
and your spot checks:

1. Are the CI/CD wrappers in `test_bridge_ceilings.py` and
   `test_canonical_variables.py` correctly enforcing quality WITHOUT
   being epistemically destructive?
2. Are the T1.5 assignments clean (formal roster only, no fabricated names)?
3. Are the ceiling exceedances properly documented with panel rationale?
4. Are there any lurking architectural deficits bridging the conceptual
   theory to the runtime database?

Do not hallucinate praise. Write your final response as a
**RUTHLESS AUDITOR'S REPORT**. Detail exact logs, point out any lingering
misalignments, and if the baseline is sound, issue the authorization to
proceed with the next phase.

---

# KEY REFERENCE DOCUMENTS

| Document | Path | Purpose |
|----------|------|---------|
| Ceiling Recalibration Panel | `docs/CEILING_RECALIBRATION_PANEL_Feb23.md` | Panel review of all ceiling exceedances |
| Ceiling Decisions (machine-readable) | `data/ceiling_decisions.json` | Per-violation decisions |
| T1.5 Expansion Panel | `docs/T1_5_EXPANSION_PANEL_Feb23.md` | Panel deliberation on 13 T1.5 candidates |
| T1.5 Formal Roster | `schemas/field_aliases.json` → `t1_5_formal_enum` | Canonical list of 14 T1.5 theories |
| IE-DPT Full T1 Specification | `docs/IE_DPT_Full_T1_Specification.md` | Superordinate framework + T1 specs |
| Theory Hierarchy | `docs/THEORY_HIERARCHY_AND_MECHANISMS.md` | ART, SRT, Biophilia, PR reductions |
| Tier Architecture | `docs/02-14_07_Theory_Tier_Architecture_V1.0.md` | T1.5 qualification criteria |

---

# SCHEDULING

This audit should be run:
- **Once** after each major structural change
- **Once** before any autonomous pipeline activation
- **Periodically** as a standing health check

---

# CHANGES FROM v3

1. **Ceiling epistemics revised**: Ceilings are now Bayesian soft priors, not
   hard caps. The test passes with panel-reviewed exceedances. Auto-clamping
   scripts are deprecated.
2. **T1.5 audit added**: Fabricated T1.5 names must be caught. Only 14 formally
   reduced theories are valid assignments.
3. **Template count updated**: 103 calibrated (was stated as ~53 in v2).
4. **Panel count updated**: 12 completed (was 8 in v2).
5. **Toulmin schema clarified**: Lives inside mechanism_chain steps as
   `justification`, not as a separate top-level field.
6. **Section 3 added**: Deep ceiling audit replacing the old "zero violations"
   requirement.

*RUTHLESS_SYSTEM_AUDIT_v4_STANDING.md*
*Post-panel-calibration verification + ongoing health check*
*Run in: CC → AG/Gemini → Codex. Cross-validate findings.*
