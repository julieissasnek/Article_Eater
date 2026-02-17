# CX-5 MAT-I Type Review (Doc 37)

Date: 2026-02-16
Task: `CX5_MAT`
Input: `docs/37_Panel_MAT_I_Materials.md`

## Summary

The MAT-I review required two schema updates and one confirmation:

1. **MAT1 pathway levels**: added `somatosensory` and `interoceptive-insular` to the `Level` enum in `src/types/template.ts` so CT-afferent to posterior-insular routing can be represented without overloading generic `neural` labels.
2. **MAT2 physiological PE distinction**: added `pe_regime?: PredictionErrorRegime` on `CausalLink` to explicitly tag links as `physiological` (vs `perceptual`, etc.), so thermal adaptive prediction error is typed as a distinct regime rather than inferred only from timescale.
3. **MAT4 convergence structure**: no new structure required. Existing fields added for L3 already generalize to MAT4:
   - `causal_topology?: "serial" | "parallel" | "hybrid"`
   - `convergence_rule?: "additive" | "multiplicative" | "super_additive" | "competitive" | "unknown"`
   - link-level `channel_id?` and `converges_on?`

## Validation

- `tsc -p tsconfig.theory-tier.json` passes.
- `node scripts/check_template_enum_drift.js` currently reports one existing data drift issue:
  - `data/templates/L3_daylight_multichannel_convergence.json` contains `from_level: "multi_channel"` (non-canonical level token).
- `node scripts/check_template_contract_compatibility.js` runs and refreshes compatibility report; legacy/unknown-shape findings remain in historical template files.

## Notes for MAT encoding

When CC encodes MAT1-MAT5, use canonical link shape (`from_variable`, `to_variable`, `from_level`, `to_level`) and set:
- `pe_regime: "physiological"` for MAT2 thermal adaptive links
- `causal_topology: "parallel"` + channel metadata for MAT4
- `from_level/to_level` values from expanded set including `somatosensory` and `interoceptive-insular` where biologically appropriate
