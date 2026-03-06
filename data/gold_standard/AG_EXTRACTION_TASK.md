# Article Eater: Gold Standard Extraction — AG Worker Protocol (v3)

## Architecture: PDF-First

The PDF is the ground truth. Every PDF has a unique inventory ID (PDF-0001, PDF-0002, ...). You discover the title, authors, DOI, and all metadata by reading the paper.

## Step 0: Coordination — MANDATORY

```bash
cd ~/REPOS/Article_Eater_PostQuinean_v1

# Check status:
python3 scripts/extraction_coordinator.py status

# Claim your batch (5 papers at a time):
python3 scripts/extraction_coordinator.py claim ag --n 5

# After extracting each paper:
python3 scripts/extraction_coordinator.py complete ag PDF-NNNN

# If you need to restart:
python3 scripts/extraction_coordinator.py release ag
```

**NEVER extract without claiming first.**

## Step 1: Read the PDF — VISION-BASED (MANDATORY)

**Use your Read tool directly on the PDF file.** Your Read tool renders PDFs visually — you see them as images, exactly as a human reader would. This means you can see:
- **Tables** with their full structure (rows, columns, cell values)
- **Figures** showing experimental stimuli (rooms, lighting, VR environments, architectural renderings)
- **Charts/graphs** with data points and trends
- **Equations** and mathematical notation
- **Image quality and resolution**

**DO NOT** try to open PDFs in a browser.
**DO NOT** convert PDFs to text (this loses all visual information).
**DO NOT** use any text extraction tools (pdfplumber, PyPDF2, etc.).

Example — just use Read:
```
Read the file: /path/to/paper.pdf
```

For long papers (>20 pages), read in chunks: pages 1-10, then 11-20, then 21-end.

**WHY THIS MATTERS**: When you see a figure showing the experimental stimulus (a room layout, a lighting setup, a VR environment, an architectural rendering), you MUST describe it in the `stimulus_image_description` field. Text-only extraction cannot do this — only vision-based reading can capture what the stimulus actually looks like. This is one of the most valuable things you can extract.

## Step 2: Classify the Paper

Use EXACTLY one of these 15 canonical types:

| Type | Signals |
|------|---------|
| EMPIRICAL_RESEARCH | Methods + Results with statistics |
| META_ANALYSIS | "k studies", pooled effects, forest plots |
| SYSTEMATIC_REVIEW | PRISMA flowchart, structured search protocol |
| NARRATIVE_REVIEW | Literature overview without PRISMA |
| THEORETICAL | Frameworks/models, no original data |
| QUALITATIVE | Interviews, ethnography, phenomenology |
| MIXED_METHODS | Combines quantitative + qualitative |
| OBSERVATIONAL | No intervention (cohort, case-control) |
| REPORT | Technical/clinical reports, case studies |
| COMMENTARY | Opinion, editorial, perspective |
| LONGITUDINAL | Follow-up studies, panel data |
| INTERVENTION_DESIGN | Intervention testing protocols |
| INSTRUMENT_VALIDATION | Scale validation, reliability metrics |
| CONCEPTUAL_FRAMEWORK | Proposes new conceptual model |
| COMPARATIVE_ANALYSIS | Compares across populations/contexts |

Record `classification_confidence` (0.0–1.0) and `classification_signals` (list of reasons).

## Step 3: Extract Using the Correct Family Template

**The classification determines which extraction rules apply.** This is the entire point of classification — each article type has different required fields and different standards for what constitutes a "finding."

---

### Template A: EMPIRICAL_RESEARCH

**CRITICAL RULES:**

1. **ANTECEDENT**: Specific and operationalized
   - GOOD: "ceiling height > 3m (high condition) vs. 2.4m (low condition)"
   - BAD: "ceiling" or "room features"

2. **CONSEQUENT**: The measured outcome, not the condition
   - GOOD: "creative ideation scores on Torrance Test of Creative Thinking"
   - BAD: "cognitive performance" or "creativity"

3. **DIRECTION**: ONLY `increase | decrease | no_effect | mixed`

4. **SAMPLE_SIZE**: Required. Also `sample_size_source`: "reported" | "inferred" | "calculated"

5. **EFFECT_SIZE**: Exact from paper. Sign matches direction.

6. **INSTRUMENTS_USED**: Full names + abbreviation + construct_measured + n_items

7. **SCOPE_CONDITIONS**: setting, population, climate, duration, measurement_type, scope_unknown_dimensions

8. **CAUSAL_TIER**: EXPERIMENTAL | QUASI_EXPERIMENTAL | CORRELATIONAL

9. **STIMULUS_DESCRIPTION**: Required for every finding:
   ```json
   {
     "primary_type": "spatial | visual | auditory | thermal | etc.",
     "components": [{"name": "...", "category": "...", "essential": true, "details": "specific parameters"}],
     "delivery_method": "VR | in_situ | photograph | etc.",
     "stimulus_image_available": true/false,
     "stimulus_image_description": "If paper has figures of stimulus, describe what you see. Max 500 chars."
   }
   ```

10. **MECHANISM_CHAIN**: 2+ steps for causal claims:
    ```json
    [{"step": 1, "from_construct": "A", "to_construct": "B", "mechanism_type": "perceptual", "evidence_strength": "direct"}]
    ```

11. **THEORY_LINKS**: ALL theories cited. Include author + year.

12. **THEORY_COMMITMENTS**: How this paper relates to each theory:
    ```json
    [{"theory_name": "...", "commitment_type": "tests | assumes | extends | challenges", "specific_claim": "..."}]
    ```

13. **RESEARCH_QUESTION**: Quote the explicit research question.

14. **HYPOTHESES**: List each hypothesis, whether supported, which findings provide evidence.

**Success criteria:** sample_size ≥ 80%, direction ≥ 95%, effect_size ≥ 70%, instruments ≥ 60%, scope_conditions ≥ 50%

---

### Template B: META_ANALYSIS

- Extract POOLED effects (not individual studies)
- Each forest plot row = one finding
- Required: k (number of studies), total_n, effect_size, CI, I²
- Moderation analyses: each significant moderator level = separate finding
- claim_type: "pooled_effect"

---

### Template C: SYSTEMATIC_REVIEW

- Extract SYNTHESIZED claims across studies (not individual study findings)
- Evidence strength: strong | moderate | weak | inconsistent
- May include embedded meta-analysis results
- N_studies supporting each synthesis

---

### Template D: NARRATIVE_REVIEW

- Extract key claims and cited evidence
- claim_type: cited | narrative | theoretical | comparative
- Include mechanisms/theories discussed
- Less structured than systematic review

---

### Template E: THEORETICAL

- Extract theoretical PROPOSITIONS (not empirical findings)
- **mechanism_chain is CRITICAL**: 2+ steps for causal propositions
- claim_type: theoretical_proposition | derived_guideline | assumed
- **theory_commitments REQUIRED**: tests | assumes | extends | challenges | synthesizes
- Mark whether propositions are empirically testable

---

### Template F: QUALITATIVE

- Extract THEMATIC findings
- claim_type: qualitative_theme
- Include participant quotes where possible
- provenance_depth usually "paraphrase" (from synthesized themes)

---

### Template G: INSTRUMENT_VALIDATION

- instruments_used is CRITICAL: full name, construct, abbreviation, n_items
- Extract reliability metrics: Cronbach's alpha, test-retest, inter-rater
- Extract validity evidence: convergent, discriminant, predictive

---

### Templates for other types (MIXED_METHODS, OBSERVATIONAL, REPORT, COMMENTARY, LONGITUDINAL, INTERVENTION_DESIGN, CONCEPTUAL_FRAMEWORK, COMPARATIVE_ANALYSIS):

Use the closest matching template above. Non-empirical papers with no findings should have `findings: []` and correct classification.

---

## Step 4: Full JSON Structure

Save to: `~/REPOS/Article_Eater_PostQuinean_v1/data/gold_standard/PDF-NNNN.json`

```json
{
  "pdf_id": "PDF-NNNN",
  "doi": "discovered from paper, or null",
  "title": "actual title from the paper itself",
  "authors": [],
  "publication_year": null,
  "journal": "",
  "article_type": "one of 15 canonical types",
  "article_family": "neuroarchitecture | environmental_psychology | lighting | acoustics | thermal_comfort | biophilia | color | spatial_cognition | multisensory | other",
  "domains": ["cognition", "affect", "behavior", "health", "perception", "physiology"],
  "model": "ag-opus-4",
  "classification_confidence": 0.95,
  "classification_signals": [],
  "research_question": "explicit research question from paper, or null",
  "hypotheses": [
    {"id": "H1", "statement": "...", "supported": null, "evidence_findings": []}
  ],
  "has_stimulus_figures": true,
  "stimulus_figure_pages": [3, 5, 7],
  "n_findings": 0,
  "findings": [
    {
      "id": "F1",
      "antecedent": "Specific operationalized IV",
      "consequent": "Specific measured DV",
      "direction": "increase | decrease | no_effect | mixed",
      "claim_type": "empirical_finding | moderated | mechanistic | pooled_effect | synthesized | narrative | theoretical_proposition | qualitative_theme | methodological",
      "statement": "One-sentence summary",
      "measure_type": "self_report | behavioral | physiological | cognitive_task | observational | mixed",
      "p_value": null,
      "effect_size": null,
      "effect_size_type": null,
      "test_statistic": null,
      "sample_size": null,
      "sample_size_source": null,
      "confidence_interval": null,
      "sample": {"n": null, "population": null, "age_mean": null, "country": null},
      "instruments_used": [{"name": "", "abbreviation": "", "construct_measured": "", "n_items": null}],
      "scope_conditions": {
        "setting": null,
        "population": null,
        "climate": null,
        "duration": null,
        "measurement_type": null,
        "scope_unknown_dimensions": []
      },
      "causal_tier": "EXPERIMENTAL | QUASI_EXPERIMENTAL | CORRELATIONAL",
      "stimulus_description": {
        "primary_type": null,
        "components": [],
        "delivery_method": null,
        "stimulus_image_available": false,
        "stimulus_figure_pages": [],
        "stimulus_figure_labels": [],
        "stimulus_image_description": null,
        "stimulus_image_files": []
      },
      "mechanism": null,
      "mechanism_chain": [],
      "theory_links": [],
      "theory_commitments": [],
      "moderators_reported": [],
      "source": "",
      "quote": "max 300 chars",
      "source_zone": "abstract | methods | results | discussion | table | figure",
      "provenance_depth": "direct_quote | paraphrase | inferred | synthesized",
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
  "filename_mismatch": null,
  "extraction_metadata": {
    "extraction_version": "v4.0",
    "extractor_model": "ag-opus-4",
    "extraction_confidence": 0.85
  }
}
```

If filename doesn't match actual content:
```json
"filename_mismatch": {
  "inventory_filename": "Original filename from Zotero",
  "actual_paper": "Actual Author et al. Year"
}
```

## Step 5: Validation Checklist (Run BEFORE saving)

### For ALL papers:
- [ ] article_type is one of 15 canonical types (exact spelling)
- [ ] classification_confidence and classification_signals populated
- [ ] research_question populated (null only if truly absent)
- [ ] All finding IDs unique (F1, F2, ...)
- [ ] n_findings matches actual count
- [ ] direction values ONLY: increase | decrease | no_effect | mixed
- [ ] Quotes are verbatim, max 300 chars
- [ ] No hallucinated data

### For EMPIRICAL papers:
- [ ] sample_size ≥ 80% filled
- [ ] effect_size ≥ 70% filled (where reported)
- [ ] instruments_used with full names ≥ 60%
- [ ] scope_conditions has setting + population
- [ ] stimulus_description populated
- [ ] theory_links and theory_commitments populated
- [ ] mechanism_chain for causal claims (2+ steps)
- [ ] Effect size sign matches direction

### For THEORETICAL papers:
- [ ] mechanism_chain with 2+ steps for propositions
- [ ] theory_commitments populated
- [ ] No empirical statistics claimed

### For META_ANALYSIS:
- [ ] Pooled effects, not individual studies
- [ ] CI populated for each pooled effect
- [ ] k and total_n documented

**Fix any failures before saving.**

## Step 6: Extract and Save Stimulus Images (MANDATORY)

You can run scripts. After saving the extraction JSON, extract all images from the PDF:

```bash
cd ~/REPOS/Article_Eater_PostQuinean_v1
python3 scripts/extract_stimulus_images.py PDF-NNNN
```

This grabs all embedded images (>150×150 px) from the PDF and saves them to:
```
data/gold_standard/stimulus_images/PDF-NNNN/
```

**For papers with important stimulus figures** (experimental rooms, VR environments, lighting setups, architectural renderings), also render those specific pages at high resolution:
```bash
python3 scripts/extract_stimulus_images.py PDF-NNNN --pages 3,5,7
```

After running the script, update your extraction JSON to reference the actual image files:

```json
"stimulus_image_manifest": {
  "image_directory": "stimulus_images/PDF-NNNN/",
  "total_images": 17,
  "image_files": ["PDF-NNNN_p2_img3.jpeg", "PDF-NNNN_p3_img4.jpeg"]
}
```

And in each finding's `stimulus_description`:
```json
"stimulus_image_available": true,
"stimulus_figure_pages": [3, 5],
"stimulus_figure_labels": ["Figure 2: VR classroom conditions", "Figure 4: Spectral power distribution"],
"stimulus_image_description": "Figure 2 shows four VR classroom conditions...",
"stimulus_image_files": ["PDF-NNNN_p3_img4.jpeg", "PDF-NNNN_p5_img6.jpeg"]
```

**A text description of a figure is not the figure.** We need the actual images extracted and saved. This is one of the most important steps in the pipeline.

## Step 7: Complete and Repeat

```bash
python3 scripts/extraction_coordinator.py complete ag PDF-NNNN
python3 scripts/extraction_coordinator.py claim ag --n 5
```
