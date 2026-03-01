# INTEGRATION RECEIPT — ALLOSTATIC_MASTER_001 (T29)
**Date:** 2026-02-23
**Verification doc:** `docs/REVIEW_T29_VERIFICATION.md`
**Parent panel:** NEUROMOD-I (S-07)

## Key integration facts
- T29 integrates all NEUROMOD-I outputs plus inputs from STRESS-I, SOCIAL-I, VISUAL-I, LIGHT-I, and THERMAL-I.
- Canonical additive formula (per Section 2.1) verified: `AL_total = AX4_HPA × w_HPA × HPA + AX4_NE × w_NE × NE + w_DA × DA + w_ACh × ACh + w_5HT × 5HT + w_inflammation × inflammatory − w_restoration × restoration`.
- All seven input terms traceable to source panels with constraint coverage (Section 2.2 table).

## Validation & enforcement status
- Constraints C-01 through C-12 all satisfied; there are zero reported violations and all coverage criteria (C-01 inheritances, C-03 additive weights, C-11 restoration chronic-only, C-12 AX4 moderation). 
- Double-counting audit (Section 2.3) found only a mild, accepted overlap between social isolation and inflammation; recorded for future audit.
- Additive structure compliance (Section 2.4) demonstrates formula meets all required properties (additive sum, equal weights flagged as THEORETICAL_DEFAULT, restoration floor, exposure monotonicity, etc.).

## Risk & confidence
- Overall confidence: 0.45 (per Section 4.1). Rationale: additive compounding of uncertain inputs, THEORETICAL_DEFAULT weights, and impractical direct measurement of building-specific allostatic load (Section 4.1/4.2). 
- Main risk: building-attributable allostatic load remains empirically unmeasured (Section 5). Risk rated high but acceptable with documentation.

## Theoretical defaults and residual gaps
- Seven weight parameters (w_HPA, w_NE, w_DA, w_ACh, w_5HT, w_inflammation, w_restoration) flagged as THEORETICAL_DEFAULT (flagged in Section 2.1 and Section 4). Each is annotated with justification referencing McEwen et al., Whitehall II, and other canonical studies.
- Chronic restoration threshold (T_exposure ≥ 7 days) flagged as EMPIRICAL_COVARIANCE with chronic mechanism support (Section 7).

## Retroactive/decision items
- Social isolation vs. inflammation overlap recorded as a mild limitation; no retroactive template edits were performed.
- Human decision requested for Barrett-Craig two-stage adoption (linked to NEUROMOD receipt).

## Database/provenance
- T29 already exists in `data/templates/ALLOSTATIC_MASTER_001.json` with `provenance: "panel_calibrated"`. No new DB insertion needed beyond verifying existing record.
- Receives `provenance` tag consistent with NEUROMOD post-review.

*Receipt anchored to the T29 verification document (REVIEW_T29_VERIFICATION.md) and is intended to satisfy the PANEL → WEB OF BELIEF integration checklist.*
