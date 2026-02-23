# POST-PANEL REVIEW — MEMORY-I (S-02)
## CMR Project — Confidence Score Summary and Flags
## Generated: February 22, 2026

---

## Panel summary

- **Templates calibrated**: 10
- **Experts on panel**: 10 (revised roster per PRE_PANEL_REVIEW_CLEARANCE_MEMORY_I.md)
- **Crucible debates**: 5
- **References**: 48
- **Output file**: MEMORY_I_Panel_Output.md

---

## Confidence score summary by template

| Template | Min confidence | Max confidence | Median | Bridge warrant range |
|----------|---------------|----------------|--------|---------------------|
| ED_HIPPOCAMPAL_ENCODING_001 | 0.45 | 0.75 | 0.55 | MECHANISM → CAPACITY |
| ED_RECONSOLIDATION_001 | 0.30 | 0.70 | 0.42 | MECHANISM → ANALOGICAL |
| ED_SCHEMA_ENCODING_001 | 0.45 | 0.65 | 0.53 | MECHANISM → CAPACITY |
| ED_SYSTEMS_CONSOLIDATION_001 | 0.35 | 0.80 | 0.53 | MECHANISM → ANALOGICAL |
| ED_PATTERN_SEP_COMP_001 | 0.45 | 0.70 | 0.55 | MECHANISM → CAPACITY |
| ED_PE_ENCODING_PRINCIPLE_001 | 0.45 | 0.60 | 0.53 | MECHANISM → CAPACITY |
| SN_CONTEXT_MEMORY_002 | 0.45 | 0.70 | 0.55 | MECHANISM → CAPACITY |
| MS_RIPPLE_REPLAY_002 | 0.40 | 0.80 | 0.53 | MECHANISM → THEORETICAL_DEFAULT |
| MS_CONSOLIDATION_RESTORATION_001 | 0.40 | 0.70 | 0.50 | MECHANISM → THEORETICAL_DEFAULT |
| THRESHOLD_EPISODIC_BOUNDARY_001 | 0.40 | 0.60 | 0.48 | EMPIRICAL_COVARIANCE → THEORETICAL_DEFAULT |

---

## Flags for reviewer

### Flag 1: Reconsolidation Architectural Translation (HIGH PRIORITY)

ED_RECONSOLIDATION_001 has the lowest median confidence (0.42) and the most speculative parameters (modification integration limit at 0.35, architectural layout change dose-response untested). The reconsolidation window has not been studied in architectural spatial contexts. This template is the most likely to require downward revision as the project proceeds.

**Recommendation**: Treat all reconsolidation architectural parameters as provisional hypotheses rather than calibrated design guidance. The builder AI should flag reconsolidation-based suggestions with an explicit uncertainty marker.

### Flag 2: SWR Replay Human Translation Gap

MS_RIPPLE_REPLAY_002 has the sharpest split between mechanism confidence (0.80 for rodent SWR) and architectural translation confidence (0.45 for human rest environments). The "consolidation-permissive environment" specification (SRV < 0.05, LAeq < 45 dBA, nature view, ~15° recline) is plausible but entirely THEORETICAL_DEFAULT for humans.

**Recommendation**: Human architectural neuroimaging study needed — specifically, measuring hippocampal-cortical connectivity during rest in varied architectural conditions. Until such data exist, the consolidation-permissive environment specification should be treated as a reasonable but unvalidated design heuristic.

### Flag 3: Doorway Effect Dose-Response Untested

THRESHOLD_EPISODIC_BOUNDARY_001 predicts a dose-response (spatial contrast ratio → episodic boundary strength) based on TCM and PE encoding theory, but Radvansky's empirical data are binary (door present/absent). The parametric prediction is the key design-actionable claim and the key empirical gap.

**Recommendation**: This is a testable prediction suitable for a CMR-funded validation study (vary threshold contrast magnitude in VR and measure episodic boundary strength).

### Flag 4: PE Encoding / NEUROMOD-I Double-Counting Risk

ED_PE_ENCODING_PRINCIPLE_001 calibrates dopaminergic prediction error → hippocampal encoding strength. NEUROMOD-I will calibrate Schultz's reward prediction error → dopaminergic release. The VTA → hippocampal pathway is shared. When NEUROMOD-I executes, the panel must ensure that the PE encoding boost is not counted twice (once as memory PE, once as reward PE).

**Recommendation**: Establish a formal partial-out rule when NEUROMOD-I is calibrated. MEMORY-I owns the encoding strength modulation; NEUROMOD-I owns the reward-valence modulation. The builder AI should compute PE encoding boost once (from MEMORY-I) and PE reward valence once (from NEUROMOD-I), not sum two separate PE effects.

### Flag 5: Schema Acceleration Magnitude Translation

ED_SCHEMA_ENCODING_001 uses Tse et al. (2007) ~50% schema acceleration from rodent paired-associate learning. Human spatial schema effects are directionally consistent but the quantitative magnitude may differ. The 1.5× speed multiplier is plausible but borrowed from a different species and task domain.

---

## Pre-panel review constraints: compliance check

| Constraint | Status |
|-----------|--------|
| Nader reconsolidation bridge ≤ CAPACITY (0.45) | **COMPLIANT** — all architectural parameters ≤ 0.45; most at ANALOGICAL (0.35) |
| Ripple replay human translation THEORETICAL_DEFAULT | **COMPLIANT** — all consolidation-permissive environment params at THEORETICAL_DEFAULT |
| Doorway effect binary = EMPIRICAL_COVARIANCE; dose-response = THEORETICAL_DEFAULT | **COMPLIANT** — binary at 0.60 EMPIRICAL_COVARIANCE; dose-response at 0.45 THEORETICAL_DEFAULT |
| Systems consolidation: acute moderate, outcome < 0.40 | **COMPLIANT** — acute at 0.55/0.45; outcome at 0.35 |
| SN_CONTEXT_MEMORY_002: reference SC1, no double-counting | **COMPLIANT** — spatial_navigation_contribution inherits from SC1 explicitly |

All five pre-panel review constraints were enforced during calibration.

---

## Decision required

Set `post_panel_review_cleared: true` for S-02 in SPRINT_TASK_BRIEF_for_Cowork.md after review.

---

*REVIEW_MEMORY_I_post.md — CMR Project*
*Generated by Cowork (Claude Opus 4.6), February 22, 2026*
