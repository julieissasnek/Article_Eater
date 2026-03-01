# AESHI System Health Report

- Generated (UTC): 2026-03-01T02:11:21.380821+00:00
- Overall score: **49.0**
- Band: **RED**
- Overall status: **FAIL**

## Hard Gates

| Gate | Status | Time (s) | Detail |
|---|---|---:|---|
| sanity_check | PASS | 0.000 | skipped |
| offline_pipeline_smoke | PASS | 0.000 | skipped |
| offline_pipeline_v2_smoke | PASS | 0.000 | skipped |
| web_of_belief_invariants | PASS | 0.000 | skipped |
| web_bn_minimum_viable | PASS | 0.000 | minimum_viable passed=12 failed=0 |
| finding_template_contracts | FAIL | 0.000 | unique_tier1 7 < 10; tier2_coverage 0.000 < 0.900 |

## Subscores

| Area | Score |
|---|---:|
| contract | 97.14 |
| pipeline | 40.00 |
| web_bn | 72.37 |
| theory | 20.00 |
| stability | 84.17 |

## Key Metrics

- findings_total: 3420
- tier2_coverage: 0.0000
- unique_tier1_count: 7
- CCI complete_chain_ratio: 0.0000
- web isolated_pct: 25.061
- bn unresolved_pct: 0.000
