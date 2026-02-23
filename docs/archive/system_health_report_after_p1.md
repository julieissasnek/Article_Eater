# AESHI System Health Report

- Generated (UTC): 2026-02-20T22:46:30.888513+00:00
- Overall score: **76.14**
- Band: **YELLOW**
- Overall status: **PASS**

## Hard Gates

| Gate | Status | Time (s) | Detail |
|---|---|---:|---|
| sanity_check | PASS | 1.592 | /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/contracts/schemas.py:97: UserWarning: Field name "construct" i... |
| offline_pipeline_smoke | PASS | 0.146 | /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/contracts/schemas.py:97: UserWarning: Field name "construct" i... |
| offline_pipeline_v2_smoke | PASS | 0.160 | /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1/src/contracts/schemas.py:97: UserWarning: Field name "construct" i... |
| web_of_belief_invariants | PASS | 0.173 | run_probe passed with counters={"add_belief": 125, "add_constraint": 144, "add_evidence": 124, "beliefs": 252, "const... |
| web_bn_minimum_viable | PASS | 0.000 | minimum_viable passed=12 failed=0 |
| finding_template_contracts | PASS | 0.000 | all finding-template contracts passed |

## Subscores

| Area | Score |
|---|---:|
| contract | 85.71 |
| pipeline | 72.55 |
| web_bn | 52.44 |
| theory | 85.46 |
| stability | 100.00 |

## Key Metrics

- findings_total: 382
- tier2_coverage: 0.9921
- unique_tier1_count: 18
- CCI complete_chain_ratio: 0.3901
- web isolated_pct: 22.482
- bn unresolved_pct: 0.000
