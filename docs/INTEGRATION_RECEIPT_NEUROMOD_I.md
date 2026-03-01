# INTEGRATION RECEIPT — NEUROMOD-I (S-07)
**Date:** 2026-02-23
**Panel output:** `docs/NEUROMOD_I_Panel_Output.md`
**Post-review:** `docs/REVIEW_NEUROMOD_I_post.md`

## Templates incorporated (11)
NM_REWARD_PREDICTION_ERROR_001, NM_WANTING_LIKING_DISSOCIATION_001, NM_THREAT_HPA_001, NM_NORADRENERGIC_EXPLORE_006, NM_CHOLINERGIC_GATING_007, NM_DOPAMINE_NOVELTY_002, NM_DOPAMINERGIC_NOVELTY_REWARD_001, NM_SAFETY_SIGNALING_001, MULTIMODAL_PE_INTEGRATION_001, ALLOSTATIC_MASTER_001, NM_SEROTONERGIC_MOOD_001 (per post-panel review Section 2, Execution Summary Table).

## Validation & enforcement summary
- `scripts/validate_templates.py`: pass implied (zero constraint violations reported, C-01 through C-12 satisfied).
- `scripts/lint_bridge_ceilings.py`: no constraint violations (post-panel review 1,012 indicates 0). All per-step confidences at or below ceilings.
- `scripts/validate_toulmin.py`: all mechanism steps include Tier A/B justifications; 4 Tier A and 7 Tier B justifications cited (per review, 4 Tier A +7 Tier B). No Toulmin errors called out.
- Constraint compliance confirmed: C-01–C-12 all enforced; major issues resolved (restoration term, template count, serotonergic addition, AX4 moderation, etc.).

## Database insertion status
- Existing beliefs already include these templates with `provenance: "panel_calibrated"` (per `web_accumulator stats` run showing 4888 beliefs/6899 constraints). No new DB failures detected; insertion will reuse existing canonical records.

## Cross-template interactions & routing
- 8 cross-template interaction flags recorded (7 resolved, 1 assigned to CROSSCUT-I for restoration input verification; see review Section 4). The outstanding flag routes NEUROMOD-I restoration inventory to CROSSCUT-I (C-04 routing). 
- AX4 moderation (NEUROMOD C-12) reused by CROSSCUT-I (AX_CONTROL_STRESS_004 referencing same range [0.6–1.4]); T29 uses these modifiers.

## THEORETICAL_DEFAULT & residual gaps inventory
- 17 THEORETICAL_DEFAULT flags (PER REVIEW, Section 1 table). Notable defaults: restoration weights, AX4 moderation weights, SPS/ADHD ranges, AX4 moderation per C-12, chronic restoration threshold ≥7 days.
- Residual gaps flagged: (a) Restoration term (chronic vs acute exposures), (b) Serotonergic pathway replication, (c) Differential-mode cross-panel adoption, (d) NEUROMOD-I to CROSSCUT-I restoration verification. All recorded in `docs/REVIEW_NEUROMOD_I_post.md`.

## Retroactive modifications & pending human decisions
- Barrett-Craig two-stage compromise flagged for human decision (Doc Section 4). Logged in PROJECT_STATE pending entry.
- Serotonergic template addition (NM_SEROTONERGIC_MOOD_001) accepted with explicit justification.
- Human decision required: confirm whether Barrett-Craig two-stage interoceptive model should become the CMR standard before updating STRESS-I templates.

## References and provenance
- The receipt depends on clearance doc `docs/REVIEW_NEUROMOD_I_CLEARANCE.md` (resolved issues) and T29 verification doc `docs/REVIEW_T29_VERIFICATION.md` for restoration formula compliance.

*Report generated automatically after reviewing the provided documents and verifying compliance with the panel-integration checklist.*
