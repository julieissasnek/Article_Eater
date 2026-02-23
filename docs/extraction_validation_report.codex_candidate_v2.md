# Extraction Validation Report (Codex Candidate v2)

Generated: 2026-02-19
Input: `data/production/structured_claims.codex_candidate_v2.json`
Matcher: `scripts/validate_extraction.py` heuristic overlap evaluator

## Metrics

- True Positives: 1
- False Positives: 12
- False Negatives: 138
- Precision: 0.0769
- Recall: 0.0072
- F1: 0.0132

## Notes

- Precision is improved versus the prior codex candidate baseline (`0.0312`).
- Recall is unchanged in this matcher and remains the primary blocker.
- This report is isolated to the codex candidate artifact and does not overwrite `docs/extraction_validation_report.md`.

## Release Candidate

Input: `data/production/structured_claims.codex_release_candidate.json`

- True Positives: 1
- False Positives: 12
- False Negatives: 138
- Precision: 0.0769
- Recall: 0.0072
- F1: 0.0132
