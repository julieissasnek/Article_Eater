# AG Head-to-Head Extraction Prompt

## Instructions for David

1. Open AG (Google AI Studio / Agentic Gemini — whatever interface you have)
2. Make sure the model is set to **Opus**
3. Upload the PDF: `~/REPOS/Article_Eater_PostQuinean_v1/data/pdfs/neuroarch_batch/10.1016_j.jobe.2022.104552.pdf`
4. Paste the prompt below
5. Save AG's response as: `~/REPOS/Article_Eater_PostQuinean_v1/data/gold_standard/HEAD_TO_HEAD_ag_opus_10.1016_j.jobe.2022.104552.json`

## The Prompt (copy everything between the lines)

---

You are performing a precise scientific article extraction. Read the attached PDF completely and extract every finding into structured JSON.

DOI: 10.1016/j.jobe.2022.104552

**OUTPUT FORMAT**: Return ONLY a single valid JSON object (no markdown, no explanation before or after). The JSON must have these exact top-level keys:

```
{
  "doi": "10.1016/j.jobe.2022.104552",
  "title": "exact paper title",
  "authors": ["Author1", "Author2"],
  "publication_year": YYYY,
  "journal": "journal name",
  "article_type": "empirical_research | meta_analysis | systematic_review | narrative_review | theoretical | qualitative | mixed_methods | observational",
  "article_family": "environmental_psychology | neuroscience | architecture | etc.",
  "domains": ["cognition", "affect", "behavior", "health", "perception", "physiology"],
  "model": "ag-opus-4",
  "n_findings": N,
  "findings": [ ... ],
  "limitations": ["limitation 1", "limitation 2"],
  "overall_theory_links": [{"theory_name": "...", "authors": ["..."], "year": YYYY}]
}
```

**EACH FINDING** in the `findings` array must have ALL of these fields (use `null` if not reported in the paper — do NOT invent values):

```
{
  "id": "F1",
  "antecedent": "Specific, operationalized independent variable or condition (e.g., 'Two-window classroom condition vs. neutral baseline in VR' NOT just 'windows')",
  "consequent": "Specific measured outcome (e.g., 'Digit Span Test backward recall accuracy' NOT just 'cognitive performance')",
  "direction": "increase | decrease | no_effect | mixed",
  "claim_type": "empirical_finding | null | moderated | mechanistic | causal | associational",
  "statement": "Natural language summary of this finding",
  "p_value": 0.023,
  "effect_size": 0.67,
  "effect_size_type": "Cohen's d | eta_squared | partial_eta_squared | r | odds_ratio | Hedges' g | classification_accuracy",
  "test_statistic": "F(3,88) = 4.35 | t(45) = 2.34 | χ²(3) = 12.5 | H(3) = 8.72",
  "confidence_interval": [0.15, 1.19],
  "sample_size": 90,
  "sample": {
    "n": 90,
    "population": "university students",
    "age_mean": 25.7,
    "country": "USA"
  },
  "measure_type": "self_report | behavioral | physiological | cognitive_task | observational | mixed",
  "instruments_used": [
    {
      "name": "Full instrument name",
      "abbreviation": "ABBR",
      "construct_measured": "what it measures"
    }
  ],
  "source": "Results section, Table 3 | Figure 4 | Section 4.2",
  "quote": "Direct quote from paper supporting this finding (max 300 chars)",
  "source_zone": "abstract | methods | results | discussion | table | figure",
  "provenance_depth": "direct_quote | paraphrase | inferred",
  "causal_tier": "EXPERIMENTAL | QUASI_EXPERIMENTAL | CORRELATIONAL",
  "scope_conditions": {
    "setting": "laboratory | classroom | office | etc.",
    "population": "who was studied",
    "climate": "if relevant",
    "duration": "acute | subchronic | chronic",
    "measurement_type": "EEG | fNIRS | behavioral | survey"
  },
  "stimulus_description": {
    "primary_type": "visual_scene | spatial | lighting | etc.",
    "delivery_method": "in_situ | VR | photo | video",
    "duration_seconds": null,
    "components": [
      {"name": "component name", "category": "visual | spatial", "essential": true}
    ]
  },
  "mechanism": "Proposed mechanism if discussed (or null)",
  "theory_links": [{"theory_name": "...", "authors": ["..."], "year": YYYY}],
  "moderators_reported": ["moderator1", "moderator2"],
  "source_quality_indicators": {
    "pre_registered": false,
    "blinding": "double_blind | single_blind | unblinded",
    "replication_status": "original | replication"
  }
}
```

**EXTRACTION RULES** (these are critical):

1. Extract EVERY statistical test reported in the paper, including null results (direction: "no_effect")
2. Be precise about antecedents — operationalize them (e.g., "Wide classroom condition (1.5× width) in VR" not "room width")
3. Be precise about consequents — name the specific measure (e.g., "Stroop Test interference accuracy" not "attention")
4. Copy p-values exactly as reported. If "<0.001", use the string "<0.001"
5. Copy effect sizes exactly. If classification accuracy, report the percentage as decimal
6. Include EEG frequency band findings (alpha, beta, theta, etc.) as separate findings
7. Include both behavioral AND neural results
8. For machine learning results: report accuracy, chance level, and significance
9. Include any survey or questionnaire results
10. Quote directly from the paper for the "quote" field

**VALIDATION** (check before returning):
- All finding IDs are unique (F1, F2, F3...)
- direction is ONLY: increase | decrease | no_effect | mixed
- No invented statistics — if not in the paper, use null
- antecedent describes the condition, consequent describes the measurement
- JSON is valid (no trailing commas, all strings quoted, all brackets closed)

Return ONLY the JSON. No other text.

---

## After AG Finishes

Note the time it took and any token count AG reports. Save the JSON output to:
```
~/REPOS/Article_Eater_PostQuinean_v1/data/gold_standard/HEAD_TO_HEAD_ag_opus_10.1016_j.jobe.2022.104552.json
```

Then tell Cowork "AG extraction is done" and I'll run the comparison automatically.
