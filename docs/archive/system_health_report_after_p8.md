# AESHI System Health Report

- Generated (UTC): 2026-02-21T01:25:07.343557+00:00
- Overall score: **49.0**
- Band: **RED**
- Overall status: **FAIL**

## Hard Gates

| Gate | Status | Time (s) | Detail |
|---|---|---:|---|
| sanity_check | PASS | 1.559 | /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/contracts/schemas.py:97: UserWarning: Field name "construct" i... |
| offline_pipeline_smoke | PASS | 0.156 | /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/contracts/schemas.py:97: UserWarning: Field name "construct" i... |
| offline_pipeline_v2_smoke | PASS | 0.159 | /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/contracts/schemas.py:97: UserWarning: Field name "construct" i... |
| web_of_belief_invariants | PASS | 0.177 | run_probe passed with counters={"add_belief": 125, "add_constraint": 144, "add_evidence": 124, "beliefs": 252, "const... |
| web_bn_minimum_viable | PASS | 0.000 | minimum_viable passed=12 failed=0 |
| finding_template_contracts | FAIL | 0.000 | persisted_ratio 0.000 < 1.000 |

## Subscores

| Area | Score |
|---|---:|
| contract | 69.29 |
| pipeline | 55.00 |
| web_bn | 74.37 |
| theory | 85.46 |
| stability | 94.17 |

## Key Metrics

- findings_total: 382
- tier2_coverage: 0.9921
- unique_tier1_count: 18
- CCI complete_chain_ratio: 0.0000
- web isolated_pct: 22.474
- bn unresolved_pct: 0.000
