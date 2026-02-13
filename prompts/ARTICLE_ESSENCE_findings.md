# Article Essence Extraction — Findings (v21.0)

**Updated**: 2026-02-11 (renamed from Seven-Panel)

Return JSON only. For each distinct finding about {TARGET_TOPIC} in the paper, emit:
- finding_text
- antecedents (list of causal/independent factors; empty list if unknown)
- consequent (primary outcome/result; if unknown, reuse finding_text)
- measure_direction ("positive" | "negative" | "unknown")
- statistics: { p_value, effect_size, effect_size_type, sample_size, ci_lower, ci_upper }
- quote
- page_span

If any statistic is not present, set it to null. Do not guess. Include short quotes anchoring each finding.

## Article Type Awareness

This extraction supports multiple article types:
- Empirical studies (experiments, RCTs, field studies)
- Meta-analyses (effect size aggregation)
- Systematic reviews (qualitative synthesis)
- Theoretical papers (framework development)
- Case studies (in-depth single cases)
- And others (see extraction templates)

Adapt your extraction based on what type of evidence the paper provides.

## Output Format

```json
[
  {
    "finding_text": "Natural light exposure improves sustained attention by 15%",
    "antecedents": ["natural daylight exposure", "office environment"],
    "consequent": "sustained attention",
    "measure_direction": "positive",
    "statistics": {
      "p_value": 0.01,
      "effect_size": 0.45,
      "effect_size_type": "Cohen's d",
      "sample_size": 120,
      "ci_lower": 0.25,
      "ci_upper": 0.65
    },
    "quote": "Participants in the daylight condition showed significantly higher attention scores (M=78.3, SD=12.1) compared to artificial lighting (M=68.2, SD=14.3), t(118)=4.21, p<.01, d=0.45",
    "page_span": [7, 8]
  }
]
```
