
# Seven-Panel Extraction — Pass 2: Findings (v20.4)

Return JSON only. For each distinct finding about {TARGET_TOPIC} in the paper, emit:
- finding_text
- antecedents (list of causal/independent factors; empty list if unknown)
- consequent (primary outcome/result; if unknown, reuse finding_text)
- measure_direction ("positive" | "negative" | "unknown")
- statistics: { p_value, effect_size, effect_size_type, sample_size, ci_lower, ci_upper }
- quote
- page_span

If any statistic is not present, set it to null. Do not guess. Include short quotes anchoring each finding.
If upstream metadata includes partial seven-panel fields, still perform a full extraction from the paper text.
