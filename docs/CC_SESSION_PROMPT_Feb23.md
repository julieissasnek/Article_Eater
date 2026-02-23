# CC SESSION PROMPT — STRUCTURAL REPAIR + MUSIC-I EXTRACTION
## Date: February 23, 2026
## Copy this entire document into CC's context at session start.

---

# READ THESE FILES FIRST (in this order)

1. `docs/PROJECT_STATE.md` — coordination protocol, task board, dependencies
2. `docs/CC_REPAIR_SPRINT_INSTRUCTIONS.md` — your full repair sprint spec
3. `docs/CMR_SYSTEM_HEALTH_REPORT_Feb22_FINAL.md` — system diagnosis
4. `docs/PRE_PANEL_REVIEW_CLEARANCE_MUSIC_I.md` — MUSIC-I clearance with constraints
5. `schemas/template_canonical.json` — IF this exists (you may have built it already)

---

# CURRENT STATE (as of Feb 23, 2026)

## What's done:
- Four independent audits complete (Codex 20-checkpoint, AG/Opus, Gemini 1.5 Pro, Codex CSVs)
- MULTI-I panel complete (9 templates, 9 Toulmin appendices)
- MUSIC-I panel complete (13 templates, inline Toulmin, all 10 constraints met) — POST-REVIEW CLEARED
- TJ-07 done (panel meta-prompt updated with inline Toulmin)
- TJ-02 done (scripts/validate_toulmin.py built and working)
- Cowork has executed two panels ahead of what we expected
- 172,091 findings in ae.db; 34 beliefs + 50 constraints seeded in v2

## What Cowork is doing:
- May be executing THERMAL-I (S-05) next
- You should NOT wait for Cowork to finish — work in parallel on structural repair

## What YOU need to do this session:
- Waves 0-3 of the repair sprint (see below)
- MUSIC-I template extraction (13 templates)
- MULTI-I template extraction if not already done (9 templates)

---

# TASK SEQUENCE

## WAVE 0: QUICK FIXES (do these first, <10 min each)

### G-03: Sprint Brief Consolidation
1. `wc -l docs/SPRINT_TASK_BRIEF_for_Cowork.md`
2. If 0 lines: delete it OR copy content from SPRINT_TASK_BRIEF.md into it. One brief, not two.
3. Fix filename references in the surviving brief:
   - `_GENERALIZED_PANEL_META_PROMPT_Feb21.md` → `*GENERALIZED_PANEL_META_PROMPT_Feb21.md`
   - Check `V1_0` vs `V1.0` discrepancies
   - Verify every referenced file exists at stated path

### R-13: Mark CLAUDE.md SUPERSEDED
Add to top of docs/CLAUDE.md:
```
# ⚠️ SUPERSEDED — DO NOT USE FOR ARCHITECTURAL DECISIONS
# See docs/TRANSFER_Feb21_Session8_CORRECTED.md for current architecture.
# This file contains stale T1 roster information (ART/SRT listed as T1).
```

### M-06: Warrant Type Refactor
HUMAN DECISION (final): The three extra warrant types in bridge_warrants.py
(EPISTEMIC_COHERENCE_WARRANT, ARGUMENTATIVE_WARRANT, EPISTEMIC_VIGILANCE_WARRANT)
are Article Eater evidence-evaluation concepts, NOT CMR bridge types.

Action:
1. Create a NEW enum `EvidenceEvaluationType` in bridge_warrants.py:
```python
class EvidenceEvaluationType(str, Enum):
    """Types for evaluating evidence quality in Article Eater.
    NOT CMR bridge warrant types. No ceiling priors apply."""
    EPISTEMIC_COHERENCE = "EPISTEMIC_COHERENCE_WARRANT"
    ARGUMENTATIVE = "ARGUMENTATIVE_WARRANT"
    EPISTEMIC_VIGILANCE = "EPISTEMIC_VIGILANCE_WARRANT"
```
2. Remove these three from BridgeType enum.
3. grep codebase for all references; update imports.
4. Add comment at top of BridgeType: "Canonical CMR bridge warrant types (6 levels). For evidence evaluation types, see EvidenceEvaluationType."
5. `pytest tests/ -q --maxfail=5` — verify no regressions.

---

## WAVE 1: SCHEMA + DB INVESTIGATION (parallel)

### E-01: Canonical JSON Schema + Validator
(Skip if you already built this — check if schemas/template_canonical.json exists)

1. Create `schemas/template_canonical.json` (JSON Schema draft-07+) with two tiers:

**Scaffold tier** (all templates must pass):
- template_id (string, required)
- display_id (string, required)
- name (string, required)
- t1_frameworks (array of strings from: PP, SN, DP, DT, NM, IC, MS, EC, CB, MSI)
- calibration_status (string, enum: calibrated | scaffold | uncalibrated | partial)
- panel_source (string or null)

**Calibrated tier** (additionally required):
- mechanism_chain (array of step objects)
- bridge_warrant (string, one of 6 canonical + THEORETICAL_DEFAULT)
- confidence (number, 0.0-1.0)
- calibrated_parameters (object)
- cross_template_interactions (array)
- residual_gaps (array)
- population_modifiers (object or null)
- architectural_modifiers (object or null)

**Field name resolution table** (apply during migration):

| Found | Rename to |
|-------|-----------|
| `status: "calibrated"` | `calibration_status: "calibrated"` |
| `mechanism_steps` | `mechanism_chain` |
| `bridge_warrant_type` | `bridge_warrant` |
| `super_template_interactions` | `cross_template_interactions` |
| `prior_confidence` | `confidence` |
| `architectural_modifier_coefficients` | `architectural_modifiers` |
| missing `display_id` | generate from template_id |
| missing `name` | derive from template_id |

2. Create `scripts/validate_templates.py` — validates all files in data/templates/*.json.
3. Run it. Record how many pass/fail and why.

### M-05a: DB Investigation
Run these queries and save output to docs/DB_INVESTIGATION_REPORT.md:

```bash
# v1 contents
sqlite3 data/web_persistence.db "SELECT COUNT(*) FROM beliefs;"
sqlite3 data/web_persistence.db "PRAGMA table_info(beliefs);"
sqlite3 data/web_persistence.db "SELECT * FROM beliefs ORDER BY ROWID LIMIT 5;"
sqlite3 data/web_persistence.db "SELECT DISTINCT substr(source, 1, 50) FROM beliefs LIMIT 20;" 2>/dev/null || echo "no source column"
sqlite3 data/web_persistence.db "SELECT MIN(created_at), MAX(created_at) FROM beliefs;" 2>/dev/null || echo "no created_at column"

# v2 contents
sqlite3 data/web_persistence_v2.db "SELECT COUNT(*) FROM beliefs;"
sqlite3 data/web_persistence_v2.db "PRAGMA table_info(beliefs);"
sqlite3 data/web_persistence_v2.db "SELECT * FROM beliefs ORDER BY ROWID LIMIT 5;"

# db_locator logic
cat src/services/db_locator.py

# who calls it
grep -rn "resolve_web_db\|db_locator\|web_persistence" src/ scripts/ --include="*.py" | head -30
```

**HUMAN decision context**: Likely architecture is two-tier beliefs in one DB. Panel-calibrated = tier 1 (high quality). Extraction-derived = tier 2 (automated). Migrate everything into one DB with a provenance/tier column. But we need to confirm what's in v1 first.

---

## WAVE 2: MIGRATION + CEILING LINT

### M-01: Schema Migration
(Depends on E-01)

1. Create `scripts/migrate_templates.py`
2. Apply field name resolution table to all templates in data/templates/
3. Add missing required fields with null/default values
4. Generate display_id for files that lack it
5. Run migration
6. Run validator — target: ALL templates pass scaffold; all calibrated pass calibrated tier
7. Run template_scanner.py — verify no more skip warnings
8. `pytest tests/test_template_record.py -v`

### E-02: Bridge Warrant Ceiling Lint
(Can build in parallel with M-01)

Create `scripts/lint_bridge_ceilings.py`:
- Ceiling values: CONSTITUTIVE 0.75, MECHANISM 0.60, EMPIRICAL_COVARIANCE 0.60, FUNCTIONAL 0.50, CAPACITY 0.45, ANALOGICAL 0.35, THEORETICAL_DEFAULT 0.40
- Check top-level confidence AND per-step confidence in mechanism_chain
- Output: console table + data/ceiling_violation_report.json

Run against current corpus. The Feb 22 Codex audit found 62 violations.

---

## WAVE 3: EXTRACTION + BOOKKEEPING

### MUSIC-I Template Extraction (13 templates)

Extract all 13 calibrated templates from docs/MUSIC_I_Panel_Output.md to data/templates/:

Templates to extract:
1. BRECVEMA_MULTI_MECHANISM_001
2. BRECVEMA_BRAINSTEM_001
3. BRECVEMA_RHYTHMIC_ENTRAINMENT_002
4. BRECVEMA_CONTAGION_003
5. BRECVEMA_EXPECTANCY_004
6. BRECVEMA_MEMORY_005
7. NEURAL_MUSIC_EMOTION_ARCH_001
8. PLEASURABLE_SADNESS_001
9. ACOUSTIC_EMOTION_MAPPING_001
10. MS_ACOUSTIC_ECOLOGY_001
11. AUD_SCENE_ANALYSIS_001
12. AUD_REVERBERATION_SPACE_003
13. AUDITORY_FRACTAL_SCALING_001

**Requirements:**
- Use canonical field names from E-01 schema
- Use `calibration_status: "calibrated"` (NOT `status: "calibrated"`)
- Include `panel_source: "MUSIC-I"`
- Fix minor JSON issues found in review:
  - `"n": 32"` → `"n": 32` (remove trailing quote, several instances)
  - `"n": 40+"` → `"n": 40` (remove +")
  - `"n": 60"` → `"n": 60` (remove trailing quote)
- Run schema validator on all 13 — must pass calibrated tier
- Run ceiling lint on all 13 — must show 0 violations
- Run validate_toulmin.py on all 13 — must pass

### MULTI-I Template Extraction (if not already done — check data/templates/)

Same process for 9 MULTI-I templates from MULTI_I_Panel_Output.md.
Include `panel_source: "MULTI-I"`.

### R-09: MEMORY-I Template Extraction (if not already done)

10 templates from MEMORY_I_Panel_Output.md.
Include `panel_source: "MEMORY-I"`.

### VF2 Confidence Upgrade (from MUSIC-I C-02 resolution)

MUSIC-I's auditory calibration of rhythmic entrainment CONFIRMS the parameters
used by VISUAL-I's VF2_VISUAL_RHYTHM_001 analogical bridge. Per panel consensus:

In data/templates/VF2_VISUAL_RHYTHM_001.json (or whatever the file is named):
- Change confidence from 0.40 to 0.45
- Add note: "Confidence upgraded from 0.40 to 0.45 per MUSIC-I BRECVEMA_RHYTHMIC_ENTRAINMENT_002 calibration confirming the auditory side of the visual-auditory rhythm analogy (Feb 23, 2026)"
- Keep bridge_warrant as ANALOGICAL
- Keep THEORETICAL_DEFAULT flag (visual mechanism still not independently tested)

### NEUROMOD-I Cross-Template Flags (add to Sprint Brief S-07)

MUSIC-I produced 3 flags for NEUROMOD-I. Add to Sprint Brief S-07:

```
CROSS-TEMPLATE FLAGS FROM MUSIC-I (February 23, 2026):

1. BRECVEMA_BRAINSTEM_001 → NM_THREAT_HPA_001
   General acoustic startle shares brainstem pathway with threat-HPA response.
   Partial-out: NEUROMOD-I owns the HPA cascade; MUSIC-I owns the acoustic
   startle-to-arousal pathway. Do not double-count brainstem activation.

2. BRECVEMA_BRAINSTEM_001 + BRECVEMA_MULTI_MECHANISM_001 → ALLOSTATIC_MASTER_001
   Repeated acoustic startle and sustained negative acoustic environments
   contribute to cumulative allostatic load. NEUROMOD-I should include
   acoustic environment as an input channel to the allostatic integration.

3. NEURAL_MUSIC_EMOTION_ARCH_001 → NM_DOPAMINERGIC_NOVELTY_REWARD_001
   VTA-NAcc reward circuit is shared between music pleasure and novelty-reward.
   Partial-out: NEUROMOD-I owns the dopaminergic mechanism; MUSIC-I owns
   the music-specific reward response. Do not double-count VTA activation.
```

### CROSSCUT-I Cross-Template Flag (add to Sprint Brief S-08)

```
CROSS-TEMPLATE FLAG FROM MUSIC-I (February 23, 2026):

BRECVEMA_CONTAGION_003 → MATERIAL_CULTURAL_CONDITIONING_001
Cultural conditioning moderator (0.50-0.70 attenuation for culturally
unfamiliar music) is shared with MULTI-I material-cultural template.
CROSSCUT-I should reconcile the cultural conditioning parameters
across music contagion and material perception.
```

### R-10: Update TRANSFER Doc

Update template counts in TRANSFER_Feb21_Session8_CORRECTED.md:
- Add MUSIC-I row (13 templates)
- Update totals
- Also update OPUS_REVIEW_GUIDE.md counts (currently stale: 23/128/151)

### E-04: Template Count Reconciliation

After all extractions, verify counts agree:
- `ls data/templates/*.json | wc -l`
- TRANSFER doc stated total
- gap_tracker output (if M-04 done)
- ae.db templates table (if applicable)

---

## WAVE 4: CLEANUP (if time permits)

### M-02a: Ceiling Violation Report
Run lint_bridge_ceilings.py against ENTIRE corpus (not just new templates).
Produce docs/CEILING_VIOLATION_REPORT.md grouped by pattern:
- Delta ≤ 0.05: suggest REDUCE (clamp to ceiling)
- Delta > 0.05 from calibrated panel: suggest REVIEW (warrant may need upgrading)
- Delta > 0.05 from pre-panel scaffold: suggest REDUCE

### M-04: Gap Tracker Rewrite
Rewrite scripts/gap_tracker.py to use canonical fields:
- Calibrated: `calibration_status == "calibrated"`
- Has mechanism: `mechanism_chain` exists and non-empty
- Has parameters: `calibrated_parameters` exists and non-empty
Run and verify count matches E-04.

### M-07: Test Suite Triage
Run `pytest -q --maxfail=20`. Compare to Codex baseline (15 failed, 4049 passed).
After M-01 migration, many failures should be resolved.

---

# COORDINATION RULES

1. **Claim tasks in PROJECT_STATE.md before starting.**
2. **Update PROJECT_STATE.md after completing each task.**
3. **Append to changelog with timestamp and output paths.**
4. AG is working in parallel on E-03a (variable ontology) and G-01 (document lifecycle). Do not duplicate their work.
5. If you encounter a decision that requires HUMAN input, document it in PROJECT_STATE.md Section 4 and move to the next task.

---

# PRIORITY ORDER (if you can't finish everything)

1. E-01 (schema) — unblocks everything
2. M-01 (migration) — fixes the template corpus
3. MUSIC-I extraction (13 templates) — captures the best panel output
4. E-02 (ceiling lint) — enforcement tool
5. M-06 (warrant refactor) — quick code fix
6. Everything else in wave order

---

*CC_SESSION_PROMPT_Feb23.md*
*Paste into CC context at session start.*
