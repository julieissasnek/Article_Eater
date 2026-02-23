# Haiku Table Prompt Candidate (For Gold Benchmarking)

Use this prompt only after creating codex gold rows from the same table set.

## System Prompt
You extract scientific table rows into strict JSON. Never invent values. If a value is missing, output an empty string.

## User Prompt Template
Paper metadata:
- paper_id: {{paper_id}}
- title: {{title}}
- table_id: {{table_id}}

Table markdown:
{{table_markdown}}

Extract one JSON object per data row with fields:
- paper_id
- table_id
- row_index
- claim_type
- content
- intervention
- control
- outcome
- sample_size
- effect_size
- effect_size_type
- ci_lower
- ci_upper
- p_value

Rules:
1. `row_index` is zero-based row order in the table body.
2. `claim_type` must be one of: `effect`, `finding`, `sample`, `methodology`.
3. `content` must be a concise factual row summary.
4. Numeric fields must be plain numbers (no brackets, no units).
5. If confidence interval appears like `[0.1, 0.5]`, map to `ci_lower=0.1`, `ci_upper=0.5`.
6. If no value is present in the row, output empty string.
7. Return JSON array only, no prose.

## Evaluation Protocol
1. Run on the same paper/table set as codex gold rows.
2. Compare with:
   `python3 scripts/compare_gold_vs_model_tables.py --model-csv <haiku_csv>`
3. Promote prompt only if:
- overlap >= 90%
- `outcome`, `effect_size`, `p_value`, `ci_lower`, `ci_upper` each >= 85% exact-match
