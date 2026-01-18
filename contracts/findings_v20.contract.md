# Contract: Findings Record (V20)

**Purpose:** Persist effect size type and 95% CI bounds for BN use.

## Fields (additions)
- `effect_size_type: TEXT` — e.g., `cohen_d`, `odds_ratio`, `r`, `eta_squared`.
- `ci_lower: REAL` — lower bound (95% CI).
- `ci_upper: REAL` — upper bound (95% CI).

## Invariants
- If `effect_size` is not null, `effect_size_type` SHOULD be set when reported.
- If either `ci_lower` or `ci_upper` is set, both SHOULD be set.
- Units: match the effect size type.