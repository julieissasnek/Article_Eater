You will receive a Seven-Panel findings array (validated JSON).
Cluster findings into coherent RULE CANDIDATES by semantic similarity of antecedent→consequent, noting contradictions.

Return JSON:
{
  "rule_candidates": [
    {
      "rule_id_hint": "PF-1",
      "antecedent_signature": "fractal_dimension~1.3–1.6 & scaling_hierarchy=high",
      "consequent_signature": ["beauty↑","stress↓","restoration↑"],
      "supporting_items_idx": [0,3,7],
      "notes": "mid-fractal preference cluster"
    }
  ],
  "contradictions": [
    {
      "items_idx": [2,11],
      "reason": "same direction claim but non-overlapping 95% CIs"
    }
  ]
}
Strict JSON only.