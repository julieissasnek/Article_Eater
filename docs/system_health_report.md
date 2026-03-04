# AESHI System Health Report

- Generated (UTC): 2026-03-04T15:16:42.195847+00:00
- Overall score: **91.26**
- Band: **GREEN**
- Overall status: **PASS**

## Hard Gates

| Gate | Status | Time (s) | Detail |
|---|---|---:|---|
| sanity_check | PASS | 2.375 | [sanity_check] repo root: /Users/davidusa/REPOS/Article_Eater_PostQuinean_v1 [sanity_check] OK [sanity_check] WARNING... |
| offline_pipeline_smoke | PASS | 0.146 | [offline_pipeline_smoke] OK  - events in graph.jsonl: 4  - calibration files: 1 |
| offline_pipeline_v2_smoke | PASS | 0.150 | [offline_pipeline_v2_smoke] OK  - events in graph.jsonl: 3  - v2 rules emitted: 1 |
| web_of_belief_invariants | PASS | 55.776 | run_probe passed with counters={"add_belief": 125, "add_constraint": 144, "add_evidence": 124, "beliefs": 252, "const... |
| web_bn_minimum_viable | PASS | 0.000 | minimum_viable passed=12 failed=0 |
| finding_template_contracts | PASS | 0.000 | all finding-template contracts passed |

## Subscores

| Area | Score |
|---|---:|
| contract | 100.00 |
| pipeline | 95.42 |
| web_bn | 90.78 |
| theory | 82.21 |
| stability | 80.00 |
| qa_epistemic | 90.44 |

## Key Metrics

- findings_total: 4888
- tier2_coverage: 0.9204
- unique_tier1_count: 12
- CCI complete_chain_ratio: 0.8981
- web isolated_pct: 1.739
- bn unresolved_pct: 0.000
