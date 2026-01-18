# 7-Panel — Pass 2: Findings (V20 CI-aware)

Extract findings. For each finding, output a structured `statistics` JSON object **if present in the text**; otherwise set fields to null.

**Required JSON fields** (set null if not present):
- `p_value`: number
- `effect_size`: number
- `effect_size_type`: string (e.g., "cohen_d", "odds_ratio", "eta_squared", "r")
- `sample_size`: integer
- `ci_lower`: number (95% CI lower bound)
- `ci_upper`: number (95% CI upper bound)

**Example output snippet (for one finding):**
```json
{
  "finding_text": "A significant effect of natural light on stress was found.",
  "statistics": {
    "p_value": 0.03,
    "effect_size": 0.52,
    "effect_size_type": "cohen_d",
    "sample_size": 68,
    "ci_lower": 0.12,
    "ci_upper": 0.91
  },
  "quote": "The effect of light was significant (d=0.52, 95% CI [0.12, 0.91], p < .05)...",
  "page_span": "p. 7"
}
```