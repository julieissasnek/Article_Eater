# SPRINT D VALIDATION REPORT

Generated: 2026-02-19T00:58 CET

## EXTRACTION ACCURACY

- Papers tested (gold-standard target set): 15
- Papers with extracted claims: 5
- Total extracted claims on target set: 14
- Mean F1 (heuristic overlap scorer): 0.00
- IV mapping accuracy: 1.00
- DV mapping accuracy: 0.93

Notes:
- F1 is computed with the current heuristic matcher from `scripts/validate_extraction.py`.
- The gold-standard file currently has limited verified claim pairs, so mapping coverage is currently the most reliable signal.

## WEB OF BELIEF COMPARISON

| Metric | Old Web (`data/web_persistence.db`) | New Web (`data/web_persistence_v2.db`) |
|---|---:|---:|
| Beliefs | 12,628 | 72 |
| Constraints | 28,314 | 479 |
| Unresolved IVs | 3,388 (26.83%) | 2 (2.78%) |
| Unresolved DVs | 3,388 (26.83%) | 6 (8.33%) |
| Coherence | 0.41604 | 0.41604 |
| Connected components | 3,023 | 5 |
| Garbage-like beliefs | 435 | 0 |

Interpretation:
- Structural quality is significantly improved (no garbage-like beliefs, major drop in unresolved identifiers, and much tighter connectivity).
- Coherence remained stable at ~0.416 with the current constraint weighting.

## CMR PIPELINE RESULTS (5 GOLD PAPERS)

Source: `data/production/cmr_integration_report.json`

| Paper | Template Matches | Direction OK? |
|---|---:|---|
| doi:10.25916/sut.26402764.v1 | 1/1 | Not explicitly scored |
| doi:10.54864/planarch.1491955 | 2/3 | Not explicitly scored |
| doi:10.3389/fpsyg.2015.00637 | 3/5 | `false` in current report |
| doi:10.18419/opus-9385 | 1/1 | `false` in current report |
| doi:10.24382/5191 | 15/17 | Not explicitly scored |

Aggregate CMR integration signals:
- Papers processed: 22
- Claims matched to templates: 50
- Contradictions found: 1
- Gold-standard validation subset tested: 5 papers

## REGRESSION CHECK (SPRINT 11 SYNTHETIC SUITE)

Command:
- `python3 -m pytest tests/test_sprint_verification.py -q`

Result:
- 15 passed, 2 skipped

## VERDICT

**NEEDS WORK**

Why:
- Web rebuild quality is strong and regression checks pass.
- Gold-standard extraction validation coverage is still low (5/15 papers with claims) and heuristic F1 is currently 0.00 under the existing matcher.
- Next remediation should focus on increasing extraction coverage on the remaining 10 gold papers and improving claim-to-gold alignment.
