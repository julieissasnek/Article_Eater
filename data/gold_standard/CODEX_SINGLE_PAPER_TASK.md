# Codex Task: Extract ONE Paper for Three-Way Comparison

## What to Do

Extract structured findings from ONE specific PDF using the full V4 extraction template below. Your extraction will be compared against Cowork (20 findings) and AG extractions of the same paper.

## The Paper

**PDF path:**
```
~/REPOS/Article_Eater_PostQuinean_v1/data/pdfs/neuroarch_batch/10.1016_j.jobe.2022.104552.pdf
```

**How to read it:** Use your Read tool directly on the PDF file. It handles PDFs natively. The paper is 29 pages — read in chunks if needed (pages 1-10, 11-20, 21-29).

**DO NOT** try to open it in a browser. **DO NOT** convert to text. Vision-based reading preserves tables, figures, and stimulus images.

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
- Interview/phenomenology methods → QUALITATIVE
- Has intervention description + testing protocol → INTERVENTION_DESIGN
- Validates scale/reliability metrics → INSTRUMENT_VALIDATION

Record your classification_confidence (0.0–1.0) and classification_signals (list of reasons).

---

## STEP 2: EXTRACT USING THE EMPIRICAL RESEARCH TEMPLATE

This paper is empirical research (EEG study of classroom architectural features). Use the following extraction rules — these are **mandatory**, not suggestions.

### CRITICAL RULES FOR EMPIRICAL EXTRACTION

1. **ANTECEDENT**: Must be specific and operationalized
   - GOOD: "Two-window classroom VR condition vs. windowless baseline"
   - BAD: "windows" or "architectural features"

2. **CONSEQUENT**: The measured response, not the condition
   - GOOD: "Digit Span backward recall accuracy (%)"
   - BAD: "cognitive performance" or "brain activity"

3. **DIRECTION**: ONLY these 4 values: `increase | decrease | no_effect | mixed`

4. **SAMPLE_SIZE**: REQUIRED for every finding. Search tables, text, figure captions.
   - Also record `sample_size_source`: "reported" | "inferred" | "calculated"

5. **EFFECT_SIZE**: Numeric with correct sign matching direction. Copy EXACTLY from paper.

6. **INSTRUMENTS_USED**: Full names, not abbreviations. Include:
   - `name`: Full instrument name
   - `abbreviation`: e.g., "TTCT"
   - `construct_measured`: What it measures
   - `n_items`: Number of items/subscales if reported

7. **SCOPE_CONDITIONS**: Required for empirical papers:
   - `setting`: laboratory | classroom | field | VR | etc.
   - `population`: specific description (not "students")
   - `climate`: if relevant
   - `duration`: acute | chronic | longitudinal
   - `measurement_type`: EEG | behavioral | self-report | etc.
   - `scope_unknown_dimensions`: What can't we generalize to?

8. **CAUSAL_TIER**: `EXPERIMENTAL | QUASI_EXPERIMENTAL | CORRELATIONAL`

9. **PROVENANCE**: Direct quote from paper (max 300 chars). Source location must be specific: "Table 2", "Results section 3.2", "Figure 4 caption"

### STIMULUS DESCRIPTION (CRITICAL — DO NOT SKIP)

For EVERY finding, describe the stimulus/experimental condition:

```json
"stimulus_description": {
  "primary_type": "spatial | visual | auditory | thermal | olfactory | multimodal",
  "components": [
    {
      "name": "component name",
      "category": "spatial | visual | auditory | etc.",
      "essential": true,
      "details": "specific parameters, dimensions, values"
    }
  ],
  "delivery_method": "VR | in_situ | photograph | video | screen | physical_model",
  "duration_seconds": null,
  "stimulus_image_available": true/false,
  "stimulus_image_description": "If figure shows the stimulus, describe what you see: room layout, lighting, colors, furniture arrangement, etc. Max 500 chars."
}
```

**IMPORTANT**: If the paper includes photographs, renderings, or diagrams of the experimental stimulus (the room, the lighting setup, the VR environment), set `stimulus_image_available: true` and write a detailed description in `stimulus_image_description`. This is how we capture visual information about what participants actually experienced.

### MECHANISM AND THEORY (CRITICAL — DO NOT SKIP)

**mechanism_chain**: For any causal claim, provide the multi-step causal path:
```json
"mechanism_chain": [
  {
    "step": 1,
    "from_construct": "window views in classroom",
    "to_construct": "visual access to nature",
    "mechanism_type": "perceptual",
    "evidence_strength": "direct | indirect | theoretical"
  },
  {
    "step": 2,
    "from_construct": "visual access to nature",
    "to_construct": "reduced cognitive fatigue",
    "mechanism_type": "restorative",
    "evidence_strength": "theoretical"
  }
]
```

**theory_links**: Every paper cites theories. Extract ALL of them:
```json
"theory_links": [
  {
    "theory_name": "Attention Restoration Theory",
    "authors": ["Kaplan"],
    "year": 1995
  }
]
```

**theory_commitments**: How does this paper relate to existing theories?
```json
"theory_commitments": [
  {
    "theory_name": "Attention Restoration Theory",
    "commitment_type": "tests | assumes | extends | challenges | synthesizes",
    "specific_claim": "classroom window views provide 'soft fascination' that restores directed attention capacity"
  }
]
```

### RESEARCH QUESTION AND HYPOTHESIS

```json
"research_question": "The explicit research question stated in the paper (quote if possible)",
"hypotheses": [
  {
    "id": "H1",
    "statement": "The hypothesis as stated in the paper",
    "supported": true/false/null,
    "evidence_findings": ["F1", "F3"]
  }
]
```

### EEG-SPECIFIC EXTRACTION RULES

This paper uses EEG. Follow these rules:
- Each **frequency band** (alpha, beta, theta, gamma) is a SEPARATE finding
- Each **electrode region** with distinct results is a SEPARATE finding
- **Machine learning / classification results**: report accuracy and statistical significance as findings
- Specify frequency ranges: "theta (4-8 Hz)", "alpha (8-13 Hz)"
- Specify electrode locations: "frontal (Fz, F3, F4)", "parietal (Pz, P3, P4)"

---

## STEP 3: OUTPUT JSON

Save to:
```
~/REPOS/Article_Eater_PostQuinean_v1/data/gold_standard/HEAD_TO_HEAD_codex_10.1016_j.jobe.2022.104552.json
```

### Full JSON Template

```json
{
  "pdf_id": "HEAD_TO_HEAD_CODEX",
  "doi": "10.1016/j.jobe.2022.104552",
  "title": "title you read from the paper",
  "authors": ["authors you read from the paper"],
  "publication_year": 2022,
  "journal": "journal from the paper",
  "article_type": "empirical_research",
  "article_family": "neuroarchitecture",
  "domains": ["cognition", "perception", "physiology"],
  "model": "codex-terminal",
  "classification_confidence": 0.95,
  "classification_signals": ["Methods section present", "EEG methodology", "statistical tests"],
  "research_question": "The research question as stated in the paper",
  "hypotheses": [
    {
      "id": "H1",
      "statement": "hypothesis text",
      "supported": true,
      "evidence_findings": ["F1", "F2"]
    }
  ],
  "n_findings": 0,
  "findings": [
    {
      "id": "F1",
      "antecedent": "Specific operationalized IV — what was manipulated, at what levels, compared to what baseline",
      "consequent": "Specific measured DV — which instrument, which metric, which subscale",
      "direction": "increase | decrease | no_effect | mixed",
      "claim_type": "empirical_finding | moderated | mechanistic",
      "statement": "One sentence summary of this finding",
      "measure_type": "self_report | behavioral | physiological | cognitive_task | observational | mixed",
      "p_value": "exact as reported: number like 0.034 or string like '<0.001'",
      "effect_size": "exact as reported",
      "effect_size_type": "Cohen's d | eta_squared | partial_eta_squared | r | classification_accuracy | other",
      "test_statistic": "e.g. 'F(3,88) = 4.35' or 't(42) = 2.17'",
      "sample_size": 45,
      "sample_size_source": "reported | inferred | calculated",
      "confidence_interval": [0.12, 0.85],
      "sample": {"n": 45, "population": "university architecture students", "age_mean": 22.5, "country": "USA"},
      "instruments_used": [
        {
          "name": "Full Instrument Name",
          "abbreviation": "ABBR",
          "construct_measured": "what it measures",
          "n_items": null
        }
      ],
      "scope_conditions": {
        "setting": "VR laboratory",
        "population": "university architecture students",
        "climate": null,
        "duration": "acute",
        "measurement_type": "EEG + behavioral",
        "scope_unknown_dimensions": ["generalization to non-students", "real classroom effects"]
      },
      "causal_tier": "EXPERIMENTAL | QUASI_EXPERIMENTAL | CORRELATIONAL",
      "stimulus_description": {
        "primary_type": "spatial",
        "components": [
          {
            "name": "classroom window configuration",
            "category": "spatial",
            "essential": true,
            "details": "Two windows on south wall, 1.2m x 1.5m each, natural daylight view"
          }
        ],
        "delivery_method": "VR",
        "duration_seconds": null,
        "stimulus_image_available": true,
        "stimulus_image_description": "Figure 2 shows the four VR classroom conditions: (a) windowless room with artificial lighting, (b) single window on east wall, (c) two windows on south wall, (d) panoramic window. Rooms contain identical desks, chairs, and whiteboard."
      },
      "mechanism": "proposed mechanism or null",
      "mechanism_chain": [
        {
          "step": 1,
          "from_construct": "construct A",
          "to_construct": "construct B",
          "mechanism_type": "perceptual | cognitive | affective | physiological",
          "evidence_strength": "direct | indirect | theoretical"
        }
      ],
      "theory_links": [
        {
          "theory_name": "Full Theory Name",
          "authors": ["Lead Author"],
          "year": 1995
        }
      ],
      "theory_commitments": [
        {
          "theory_name": "Full Theory Name",
          "commitment_type": "tests | assumes | extends | challenges",
          "specific_claim": "what specific theoretical claim this finding addresses"
        }
      ],
      "moderators_reported": [],
      "source": "Results section, Table N, or Section X.X",
      "quote": "Direct quote from paper, max 300 chars",
      "source_zone": "results | table | figure | discussion",
      "provenance_depth": "direct_quote | paraphrase | inferred",
      "source_quality_indicators": {
        "pre_registered": false,
        "blinding": "single_blind | double_blind | none | unclear",
        "independence_flag": true,
        "replication_status": "original"
      }
    }
  ],
  "overall_theory_links": [
    {
      "theory_name": "Theory Name",
      "authors": ["Author"],
      "year": 1995
    }
  ],
  "limitations": [
    "limitation 1",
    "limitation 2"
  ],
  "extraction_metadata": {
    "extraction_version": "v4.0",
    "extractor_model": "codex-terminal",
    "extraction_confidence": 0.85
  }
}
```

---

## STEP 4: VALIDATION CHECKLIST (Run BEFORE saving)

Before submitting your JSON, verify ALL of the following:

### Structure
- [ ] All root-level fields present (doi, article_type, title, authors, findings, research_question, hypotheses)
- [ ] findings is an array (even if empty)
- [ ] Each finding has unique id (F1, F2, ...)
- [ ] n_findings matches actual count

### Field Completeness (Empirical Requirements)
- [ ] sample_size populated for >= 80% of findings
- [ ] direction populated for >= 95% of findings
- [ ] effect_size populated for >= 70% of findings (where reported)
- [ ] instruments_used populated for >= 60% of findings
- [ ] scope_conditions has setting + population for every finding

### Data Quality
- [ ] direction values are ONLY: increase | decrease | no_effect | mixed
- [ ] Sample sizes are positive integers
- [ ] Effect sizes have correct sign (positive for increase, negative for decrease)
- [ ] P-values are numeric [0,1] OR strings like '<0.001'
- [ ] Confidence intervals are [lower, upper] numeric arrays
- [ ] Antecedents are specific and operationalized (NOT vague)
- [ ] Consequents describe measured outcomes (NOT conditions)

### Theory and Mechanism
- [ ] theory_links populated (at least one entry)
- [ ] theory_commitments populated for papers that test/extend theories
- [ ] mechanism_chain has 2+ steps for causal claims
- [ ] overall_theory_links lists all theories referenced in the paper

### Stimulus
- [ ] stimulus_description populated for every finding
- [ ] stimulus_image_available checked — if paper has figures of the stimulus, describe them
- [ ] stimulus components are specific (dimensions, parameters, not vague)

### Provenance
- [ ] Quotes are actual text from the paper (max 300 chars)
- [ ] Source locations are specific: "Table 2", "Section 3.2", "Figure 4"
- [ ] provenance_depth correctly categorizes each entry

### No Hallucinations
- [ ] All statistics match paper exactly (p-values, effect sizes, sample sizes)
- [ ] All quotes are verbatim or clearly marked as paraphrase
- [ ] No made-up findings not in the paper
- [ ] No speculative mechanism steps without evidence from paper

**If any check fails, FIX IT before saving.**

---

## STEP 5: Extract Stimulus Images (MANDATORY)

Install PyMuPDF if not already present, then extract ALL embedded images from the PDF:

```bash
cd ~/REPOS/Article_Eater_PostQuinean_v1
pip3 install pymupdf --break-system-packages 2>/dev/null

# Extract all embedded images
python3 scripts/extract_stimulus_images.py HEAD_TO_HEAD_CODEX --pdf-path ~/REPOS/Article_Eater_PostQuinean_v1/data/pdfs/neuroarch_batch/10.1016_j.jobe.2022.104552.pdf

# Also render the pages with VR classroom figures at high resolution
python3 scripts/extract_stimulus_images.py HEAD_TO_HEAD_CODEX --pdf-path ~/REPOS/Article_Eater_PostQuinean_v1/data/pdfs/neuroarch_batch/10.1016_j.jobe.2022.104552.pdf --pages 3,4,5
```

This saves actual image files to `data/gold_standard/stimulus_images/HEAD_TO_HEAD_CODEX/`.

Then update your extraction JSON:

1. Add root-level image manifest:
```json
"stimulus_image_manifest": {
  "image_directory": "stimulus_images/HEAD_TO_HEAD_CODEX/",
  "total_images": 12,
  "image_files": ["HEAD_TO_HEAD_CODEX_p3_img1.jpeg", ...]
}
```

2. In each finding's `stimulus_description`, add the actual image file references:
```json
"stimulus_image_available": true,
"stimulus_figure_pages": [3, 4, 5],
"stimulus_image_files": ["HEAD_TO_HEAD_CODEX_p3_img1.jpeg", "HEAD_TO_HEAD_CODEX_p4_img2.jpeg"]
```

**A text description of a figure is not the figure.** We need the actual images extracted and saved as files.

## After Saving

Print a summary:
- Total finding count
- Breakdown: behavioral vs EEG/neural vs survey/self-report
- How many have p-values
- How many have effect sizes
- How many have mechanism_chains
- How many have theory_commitments
- Whether stimulus images were found and described

Cowork extracted 20 findings from this paper. Your extraction will be compared against that.
