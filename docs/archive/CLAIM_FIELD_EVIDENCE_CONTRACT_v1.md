# Claim Field Evidence Contract v1

Purpose: maximize recall while explicitly exposing uncertainty so downstream risk scoring can separate reliable vs risky claims.

Use this contract when asking an LLM to extract or adjudicate claim fields from abstract/PDF text.

## Prompt Core

System instruction:

`Return only JSON. Ground every field decision in explicit evidence from the provided text. If uncertain, keep the candidate value but mark support_type as inferred and list alternatives.`

User instruction template:

1. Read the provided article content (abstract + body/table snippets).
2. Fill each claim field.
3. For each field, include exact quote evidence, section/page, support type, alternatives, and confidence.
4. Do not omit uncertain fields; encode uncertainty explicitly.

## Output JSON Contract

```json
{
  "claim_id": "string",
  "paper_id": "string",
  "fields": {
    "iv": {
      "value": "string|null",
      "evidence_quote": "string|null",
      "page": 1,
      "section": "abstract|methods|results|table|figure_caption|discussion|conclusion|unknown",
      "support_type": "explicit|derived|inferred",
      "alt_interpretations": ["string"],
      "confidence": 0.0
    },
    "dv": {
      "value": "string|null",
      "evidence_quote": "string|null",
      "page": 1,
      "section": "results",
      "support_type": "explicit|derived|inferred",
      "alt_interpretations": [],
      "confidence": 0.0
    },
    "direction": {
      "value": "increase|decrease|no_effect|unknown",
      "evidence_quote": "string|null",
      "page": 1,
      "section": "results",
      "support_type": "explicit|derived|inferred",
      "alt_interpretations": ["increase|decrease|no_effect"],
      "confidence": 0.0
    },
    "effect_size": {
      "value": 0.52,
      "effect_size_type": "d|r|beta|eta2|or|unknown",
      "evidence_quote": "string|null",
      "page": 1,
      "section": "table",
      "support_type": "explicit|derived|inferred",
      "alt_interpretations": [],
      "confidence": 0.0
    },
    "p_value": {
      "value": 0.014,
      "evidence_quote": "string|null",
      "page": 1,
      "section": "results",
      "support_type": "explicit|derived|inferred",
      "alt_interpretations": [],
      "confidence": 0.0
    }
  },
  "global_notes": [
    "short ambiguity note"
  ]
}
```

## Design Notes

- High recall is preserved because uncertain fields are still emitted.
- Precision risk is made measurable by:
  - `support_type`
  - quote availability/quality
  - section strength
  - alternatives count
  - per-field confidence
- Downstream scorer should compute:
  - `field_risk_scores`
  - `claim_risk_score`
  - `claim_risk_tier`

## Example (Direction Ambiguity)

If quote says “significant interaction observed” without sign:

- `direction.value = "unknown"`
- `support_type = "explicit"` (because quote is exact, but non-directional)
- `alt_interpretations = ["increase", "decrease"]`
- `confidence` low (e.g., 0.35)

