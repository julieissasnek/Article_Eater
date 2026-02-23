# Belief Value Analysis (SY-9)

`WebOfBelief.belief_value()` computes epistemic value as:

- **Centrality**: structural importance in the web
- **Sensitivity**: coherence impact under belief perturbation

Default formula:

`value = 0.5 * centrality + 0.5 * sensitivity`

## API

- `belief_value(belief_id: str, centrality_weight: float = 0.5) -> float`
- `beliefs_by_value(top_n: Optional[int] = None) -> List[(belief_id, value, centrality, sensitivity)]`
- `high_value_beliefs(threshold: float = 0.5) -> List[dict]`

## Example

```python
from src.services.web_of_belief import WebOfBelief

web = WebOfBelief()
# ... add beliefs/constraints ...

top_targets = web.beliefs_by_value(top_n=10)
for belief_id, value, centrality, sensitivity in top_targets:
    print(belief_id, value, centrality, sensitivity)
```

## Recommended Use

1. Run value ranking after each integration batch.
2. Prioritize top-value beliefs for:
   - manual review
   - replication checks
   - contradiction resolution
3. Combine with:
   - `Belief.compute_severity()` for test strength
   - `WebOfBelief.compute_independence_score()` for evidence independence

This gives a practical “importance × fragility × evidence quality” triage.
