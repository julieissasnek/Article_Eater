# Contract: Relational Analysis (Rule Interactions)

## Input
- Database with `findings` and `rules` populated (post-7-panel extraction).

## Output
- Rows in `rule_interactions` with:
  - `interaction_type` in {contradiction, statistical_conflict, synergistic, antagonistic, chaining, redundant}
  - `notes` describing rationale
  - `disambiguation_prompt` optionally set

## Invariants
- Do not duplicate identical interactions for the same rule pair/type in a single analysis run.
- CI math: declare `statistical_conflict` when 95% CIs do not overlap and directions match.
- Opposite `measure_direction` for same (antecedent, consequent) → `contradiction`.