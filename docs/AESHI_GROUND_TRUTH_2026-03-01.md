# AESHI System Health Report

- Generated (UTC): 2026-03-01T13:46:08.234937+00:00
- Overall score: **79.73**
- Band: **YELLOW**
- Overall status: **PASS**

## Hard Gates

| Gate | Status | Time (s) | Detail |
|---|---|---:|---|
| sanity_check | PASS | 3.905 | [sanity_check] repo root: /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1 [sanity_check] OK [sanity... |
| offline_pipeline_smoke | PASS | 0.158 | /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/scripts/offline_pipeline_smoke.py:123: PydanticDepr... |
| offline_pipeline_v2_smoke | PASS | 0.225 | [offline_pipeline_v2_smoke] OK  - events in graph.jsonl: 3  - v2 rules emitted: 1 |
| web_of_belief_invariants | PASS | 0.228 | run_probe passed with counters={"add_belief": 125, "add_constraint": 144, "add_evidence": 124, "beliefs": 252, "const... |
| web_bn_minimum_viable | PASS | 0.000 | minimum_viable passed=12 failed=0 |
| finding_template_contracts | PASS | 0.000 | all finding-template contracts passed |

## Subscores

| Area | Score |
|---|---:|
| contract | 97.14 |
| pipeline | 55.47 |
| web_bn | 72.37 |
| theory | 81.28 |
| stability | 100.00 |

## Key Metrics

- findings_total: 4888
- tier2_coverage: 0.9204
- unique_tier1_count: 17
- CCI complete_chain_ratio: 0.0104
- web isolated_pct: 25.061
- bn unresolved_pct: 0.000
