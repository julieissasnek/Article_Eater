# AG Task: Extract ONE Paper for Head-to-Head Comparison

## What to Do

Extract structured findings from ONE specific PDF using the full V4 extraction template below. Your extraction will be compared against Cowork's extraction of the same paper.

## The Paper

**PDF path:**
```
~/REPOS/Article_Eater_PostQuinean_v1/data/pdfs/neuroarch_batch/10.1016_j.jobe.2022.104552.pdf
```

**How to read it:** Use your Read tool directly on the PDF file. Like this:

```
Read the file at ~/REPOS/Article_Eater_PostQuinean_v1/data/pdfs/neuroarch_batch/10.1016_j.jobe.2022.104552.pdf
```

**DO NOT** try to open it in a browser. **DO NOT** convert it to text. Just use your Read tool — it handles PDFs natively and preserves tables, figures, and stimulus images.

The paper is 29 pages. You may need to read it in chunks if your Read tool has page limits (e.g., read pages 1-10, then 11-20, then 21-29).

---

## STEP 1: CLASSIFY THE PAPER

Use EXACTLY one of these 15 canonical types:

1. EMPIRICAL_RESEARCH: Original experiments, surveys, field studies (has Methods/Results)
2. META_ANALYSIS: Quantitative synthesis with pooled effects (k studies, pooled effect sizes)
3. SYSTEMATIC_REVIEW: Structured literature review (PRISMA protocol, bias assessment)
4. NARRATIVE_REVIEW: Traditional literature overview (unstructured synthesis)
5. THEORETICAL: Frameworks, models, conceptual papers (no original data)
6. QUALITATIVE: Interviews, ethnography, phenomenology, grounded theory
7. MIXED_METHODS: Combines quantitative and qualitative data
8. OBSERVATIONAL: Observational studies without intervention (cohort, case-control)
9. REPORT: Technical/clinical reports, case studies
10. COMMENTARY: Opinion, editorial, perspective, discussion
11. LONGITUDINAL: Follow-up studies, panel data
12. INTERVENTION_DESIGN: Describes intervention testing (protocols, feasibility)
13. INSTRUMENT_VALIDATION: Validates measurement scales/instruments
14. CONCEPTUAL_FRAMEWORK: Proposes new conceptual model
15. COMPARATIVE_ANALYSIS: Compares across populations/contexts

**Decision tree:**
- Has Methods section + Results tables/statistics → EMPIRICAL_RESEARCH or OBSERVATIONAL
- States "k studies" or "pooled effect" → META_ANALYSIS
- Has PRISMA flowchart → SYSTEMATIC_REVIEW
- "This paper reviews..." without PRISMA → NARRATIVE_REVIEW
- Theoretical framework, no methods → THEORETICAL

Record your classification_confidence (0.0–1.0) and classification_signals.

---

## STEP 2: EXTRACT USING THE EMPIRICAL RESEARCH TEMPLATE

This paper is empirical research (EEG study of classroom architectural features). The following extraction rules are **mandatory**.

### CRITICAL RULES FOR EMPIRICAL EXTRACTION

1. **ANTECEDENT**: Must be specific and operationalized
   - GOOD: "Two-window classroom VR condition vs. windowless baseline"
   - BAD: "windows" or "architectural features"

2. **CONSEQUENT**: The measured response, not the condition
   - GOOD: "EEG theta power (4-8 Hz) at frontal electrodes (Fz, F3, F4)"
   - BAD: "brain activity" or "cognitive performance"

3. **DIRECTION**: ONLY these 4 values: `increase | decrease | no_effect | mixed`

4. **SAMPLE_SIZE**: REQUIRED. Also record `sample_size_source`: "reported" | "inferred" | "calculated"

5. **EFFECT_SIZE**: Numeric with correct sign matching direction. Copy EXACTLY from paper.

6. **INSTRUMENTS_USED**: Full names, not abbreviations. Include `construct_measured` and `n_items`.

7. **SCOPE_CONDITIONS**: Required:
   - `setting`, `population`, `duration`, `measurement_type`
   - `scope_unknown_dimensions`: What can't we generalize to?

8. **CAUSAL_TIER**: `EXPERIMENTAL | QUASI_EXPERIMENTAL | CORRELATIONAL`

### STIMULUS DESCRIPTION (CRITICAL — DO NOT SKIP)

For EVERY finding, describe the experimental stimulus:
```json
"stimulus_description": {
  "primary_type": "spatial | visual | auditory | etc.",
  "components": [{"name": "...", "category": "...", "essential": true, "details": "specific parameters"}],
  "delivery_method": "VR | in_situ | photograph | etc.",
  "stimulus_image_available": true/false,
  "stimulus_image_description": "If the paper has figures showing the stimulus, describe what you see in detail. Max 500 chars."
}
```

**If the paper includes photographs, renderings, or diagrams of the experimental conditions**, set `stimulus_image_available: true` and describe the image in detail.

### MECHANISM AND THEORY (CRITICAL — DO NOT SKIP)

**mechanism_chain**: Multi-step causal path (2+ steps for causal claims):
```json
"mechanism_chain": [
  {"step": 1, "from_construct": "A", "to_construct": "B", "mechanism_type": "perceptual", "evidence_strength": "direct"}
]
```

**theory_links**: ALL theories cited in the paper.

**theory_commitments**: How this paper relates to each theory:
```json
"theory_commitments": [
  {"theory_name": "Theory Name", "commitment_type": "tests | assumes | extends | challenges", "specific_claim": "what claim"}
]
```

### RESEARCH QUESTION AND HYPOTHESES

```json
"research_question": "The explicit research question from the paper",
"hypotheses": [{"id": "H1", "statement": "hypothesis text", "supported": true/false/null, "evidence_findings": ["F1"]}]
```

### EEG-SPECIFIC RULES

- Each **frequency band** (alpha, beta, theta, gamma) = SEPARATE finding
- Each **electrode region** with distinct results = SEPARATE finding
- **Machine learning / classification**: report accuracy as findings
- Specify frequency ranges and electrode locations precisely

---

## STEP 3: OUTPUT JSON

Save as:
```
~/REPOS/Article_Eater_PostQuinean_v1/data/gold_standard/HEAD_TO_HEAD_ag_opus_10.1016_j.jobe.2022.104552.json
```

Use this structure (ALL fields required — use null if not reported, never omit the field):

```json
{
  "pdf_id": "HEAD_TO_HEAD_AG",
  "doi": "10.1016/j.jobe.2022.104552",
  "title": "title you read from the paper",
  "authors": ["authors you read from the paper"],
  "publication_year": 2022,
  "journal": "journal from the paper",
  "article_type": "empirical_research",
  "article_family": "neuroarchitecture",
  "domains": ["cognition", "perception", "physiology"],
  "model": "ag-opus-4",
  "classification_confidence": 0.95,
  "classification_signals": ["Methods section present", "EEG data", "statistical results"],
  "research_question": "quote or paraphrase of the research question",
  "hypotheses": [
    {"id": "H1", "statement": "...", "supported": null, "evidence_findings": []}
  ],
  "n_findings": 0,
  "findings": [
    {
      "id": "F1",
      "antecedent": "Specific operationalized IV",
      "consequent": "Specific measured DV",
      "direction": "increase | decrease | no_effect | mixed",
      "claim_type": "empirical_finding | moderated | mechanistic",
      "statement": "One sentence summary",
      "measure_type": "self_report | behavioral | physiological | cognitive_task | mixed",
      "p_value": "exact: 0.034 or '<0.001'",
      "effect_size": "exact as reported",
      "effect_size_type": "Cohen's d | eta_squared | partial_eta_squared | r | classification_accuracy | other",
      "test_statistic": "e.g. 'F(3,88) = 4.35'",
      "sample_size": null,
      "sample_size_source": "reported | inferred | calculated",
      "confidence_interval": null,
      "sample": {"n": null, "population": "", "age_mean": null, "country": ""},
      "instruments_used": [{"name": "Full Name", "abbreviation": "", "construct_measured": "", "n_items": null}],
      "scope_conditions": {
        "setting": "",
        "population": "",
        "duration": "",
        "measurement_type": "",
        "scope_unknown_dimensions": []
      },
      "causal_tier": "EXPERIMENTAL | QUASI_EXPERIMENTAL | CORRELATIONAL",
      "stimulus_description": {
        "primary_type": "",
        "components": [],
        "delivery_method": "",
        "stimulus_image_available": false,
        "stimulus_image_description": null
      },
      "mechanism": null,
      "mechanism_chain": [],
      "theory_links": [],
      "theory_commitments": [],
      "moderators_reported": [],
      "source": "Results Section, Table N",
      "quote": "Direct quote max 300 chars",
      "source_zone": "results | table | figure | discussion",
      "provenance_depth": "direct_quote | paraphrase | inferred",
      "source_quality_indicators": {
        "pre_registered": false,
        "blinding": null,
        "independence_flag": true,
        "replication_status": "original"
      }
    }
  ],
  "overall_theory_links": [],
  "limitations": [],
  "extraction_metadata": {
    "extraction_version": "v4.0",
    "extractor_model": "ag-opus-4",
    "extraction_confidence": 0.85
  }
}
```

---

## STEP 4: VALIDATION CHECKLIST (Run BEFORE saving)

### Empirical Completeness
- [ ] sample_size populated for >= 80% of findings
- [ ] direction populated for >= 95% of findings
- [ ] effect_size populated for >= 70% of findings (where paper reports them)
- [ ] instruments_used populated for >= 60% of findings
- [ ] scope_conditions has setting + population for every finding

### Data Quality
- [ ] direction values ONLY: increase | decrease | no_effect | mixed
- [ ] Effect sizes have correct sign (positive=increase, negative=decrease)
- [ ] P-values are numeric [0,1] OR strings like '<0.001'
- [ ] Antecedents are specific and operationalized
- [ ] Consequents describe measured outcomes, not conditions

### Theory and Mechanism
- [ ] theory_links populated (at least one entry)
- [ ] theory_commitments populated
- [ ] mechanism_chain has 2+ steps for causal claims
- [ ] overall_theory_links lists all theories referenced

### Stimulus
- [ ] stimulus_description populated for every finding
- [ ] stimulus_image_available checked — describe figures showing stimuli
- [ ] stimulus components are specific (dimensions, parameters)

### Provenance
- [ ] Quotes are verbatim from paper (max 300 chars)
- [ ] Source locations are specific: "Table 2", "Section 3.2"
- [ ] No hallucinated statistics or made-up findings

**If any check fails, FIX IT before saving.**

---

## STEP 5: Extract Stimulus Images (MANDATORY)

Install PyMuPDF if needed, then extract ALL embedded images from the PDF:

```bash
cd ~/REPOS/Article_Eater_PostQuinean_v1
pip3 install pymupdf --break-system-packages 2>/dev/null

# Extract all embedded images
python3 scripts/extract_stimulus_images.py HEAD_TO_HEAD_AG --pdf-path ~/REPOS/Article_Eater_PostQuinean_v1/data/pdfs/neuroarch_batch/10.1016_j.jobe.2022.104552.pdf

# Render key figure pages showing VR classroom conditions
python3 scripts/extract_stimulus_images.py HEAD_TO_HEAD_AG --pdf-path ~/REPOS/Article_Eater_PostQuinean_v1/data/pdfs/neuroarch_batch/10.1016_j.jobe.2022.104552.pdf --pages 3,4,5
```

This saves actual image files to `data/gold_standard/stimulus_images/HEAD_TO_HEAD_AG/`.

Then update your extraction JSON:

1. Add root-level manifest:
```json
"stimulus_image_manifest": {
  "image_directory": "stimulus_images/HEAD_TO_HEAD_AG/",
  "total_images": 12,
  "image_files": ["HEAD_TO_HEAD_AG_p3_img1.jpeg", ...]
}
```

2. In each finding's `stimulus_description`:
```json
"stimulus_image_available": true,
"stimulus_figure_pages": [3, 4, 5],
"stimulus_image_files": ["HEAD_TO_HEAD_AG_p3_img1.jpeg"]
```

**A text description of a figure is not the figure.** We need the actual images extracted as files.

## After Saving

Print a summary:
- Total finding count
- Breakdown: behavioral vs EEG/neural vs survey
- How many have p-values, effect sizes, mechanism_chains, theory_commitments
- Whether stimulus images were found and described

Cowork extracted 20 findings from this paper. Your extraction will be compared against that.
