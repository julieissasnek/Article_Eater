# BBN Calibrator (v20.6.2)

Produces a **secondary** calibration artifact for the Bayesian layer **without** mutating the primary BN input structures.

## Input
- SevenPanelArtifact.items[] with stats: p_value, effect_size, effect_size_type, sample_size, ci_lower, ci_upper
- `confidence_config.yml` weights

## Output
- `calibration/bbn_calibration.json` with per-finding weights and overall rule confidence proposal.

## Demo
