# AESHI System Health Report

- Generated (UTC): 2026-03-01T06:43:40.912827+00:00
- Overall score: **49.0**
- Band: **RED**
- Overall status: **FAIL**

## Hard Gates

| Gate | Status | Time (s) | Detail |
|---|---|---:|---|
| sanity_check | PASS | 3.289 | [sanity_check] repo root: /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1 [sanity_check] OK [sanity... |
| offline_pipeline_smoke | PASS | 0.185 | /sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/scripts/offline_pipeline_smoke.py:123: PydanticDepr... |
| offline_pipeline_v2_smoke | PASS | 0.172 | [offline_pipeline_v2_smoke] OK  - events in graph.jsonl: 3  - v2 rules emitted: 1 |
| web_of_belief_invariants | PASS | 0.226 | run_probe passed with counters={"add_belief": 125, "add_constraint": 144, "add_evidence": 124, "beliefs": 252, "const... |
| web_bn_minimum_viable | PASS | 0.000 | minimum_viable passed=12 failed=0 |
| finding_template_contracts | FAIL | 0.000 | non_music_music_top 28 > 0 |

## Subscores

| Area | Score |
|---|---:|
| contract | 97.14 |
| pipeline | 55.00 |
| web_bn | 72.37 |
| theory | 66.93 |
| stability | 94.17 |

## Key Metrics

- findings_total: 3420
- tier2_coverage: 1.0000
- unique_tier1_count: 18
- CCI complete_chain_ratio: 0.0000
- web isolated_pct: 25.061
- bn unresolved_pct: 0.000
