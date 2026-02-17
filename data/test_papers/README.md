# Batch 2 Paper Claims Library (Sprint 11 Task 11.19)

These files provide structured claims for paper-evaluation validation.

Format:
- Top-level object with `paper_id`, `citation`, and `claims`.
- `claims` is compatible with `cmr evaluate-paper --file ...`.

Examples:
- `python -m src.cmr.cli evaluate-paper --file data/test_papers/ulrich_1984.json --json`
- `python -m src.cmr.cli evaluate-paper --file data/test_papers/evans_johnson_2000.json --json`
