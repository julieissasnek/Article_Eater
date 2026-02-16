# Table Extraction Playbook (Haiku-First)

## Inputs
- Pruning gate doc: `../Article_Finder_v3_2_3/docs/PRODUCTION_RUN.md`
- Gate script: `../Article_Finder_v3_2_3/scripts/production_run.py`
- Reject export: `../Article_Finder_v3_2_3/data/review/reject_candidates.csv`
- HBE allowlist: `../Article_Finder_v3_2_3/config/hbe_journals_allowlist.txt`
- Neuroscience allowlist: `../Article_Finder_v3_2_3/config/neuroscience_venues_allowlist.txt`
- Must-include seeds: `config/table_must_include_seeds.txt`

## Safety Rules Before Extraction
1. Never auto-reject HBE allowlist journals.
2. Never auto-reject neuroscience venues.
3. Never auto-reject papers with `cited_by_count >= 150` (or equivalent configured threshold).
4. Do not start table extraction until reject candidates are reviewed.

## Queue Construction
Use the queue builder that enforces topic breadth and importance:

```bash
python3 scripts/build_table_extraction_queue.py \
  --db /Users/davidusa/REPOS/Article_Finder_v3_2_3/data/article_finder.db \
  --reject-csv /Users/davidusa/REPOS/Article_Finder_v3_2_3/data/review/reject_candidates.csv \
  --must-include-seeds config/table_must_include_seeds.txt \
  --per-topic-target 8 \
  --max-total 120 \
  --high-cite-threshold 150 \
  --output-dir data/table_queue
```

Generated artifacts:
- `data/table_queue/table_extraction_queue.csv`
- `data/table_queue/protected_rejects_review.csv`
- `data/table_queue/table_extraction_queue_summary.md`

## Low-Cost Model Strategy (Haiku-Level)
Goal: get near high-end quality with cheap models by adding deterministic checks.

1. Pass A (cheap extractor):
- Model: Haiku-class.
- Task: table-to-JSON extraction only.
- Output must be schema-constrained JSON.

2. Deterministic validation:
- Reject malformed rows (missing IV, DV, or statistic fields when expected).
- Verify sign consistency: `effect_direction` vs numeric statistic where possible.
- Normalize variable names to canonical ontology labels.

3. Pass B (cheap verifier):
- Model: same cheap model.
- Task: compare source row text vs extracted JSON and produce mismatch flags.
- Escalate only flagged rows.

4. Escalation path:
- Route only uncertain/flagged rows to stronger model.
- Keep high-confidence rows from cheap path.

5. Active learning:
- Store frequent mismatch patterns.
- Add prompt examples for those patterns.
- Re-run cheap model; this reduces expensive escalations over time.

## Acceptance Criteria
1. Topic spread: no single topic dominates >35% of queue.
2. Must-include seed papers with PDFs are present in queue.
3. Protected rejects are not dropped; they are moved to explicit review.
4. Escalation rate to expensive model stays below 20% of rows.
