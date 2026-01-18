Return a JSON array. Each item is ONE finding with the following keys:

- finding_text: str
- statistics: object with fields (use null if absent)
  - p_value: number|null
  - effect_size: number|null
  - effect_size_type: "cohen_d"|"odds_ratio"|"eta_squared"|"r"|string|null
  - sample_size: integer|null
  - ci_lower: number|null
  - ci_upper: number|null
- quote: short verbatim evidence string
- page_span: "p. 7" or "pp. 7–8"
- raw_abstract: the paper's abstract as plain text (echo back if provided)

STRICT: Output must be valid JSON. No prose outside JSON.