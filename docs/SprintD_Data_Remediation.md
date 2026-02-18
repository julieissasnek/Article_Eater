# SPRINT D: DATA REMEDIATION
## PDF Extraction Reprocessing, Vocabulary Consolidation, Web Rebuild
## February 17, 2026

---

## READ THIS FIRST — ALL AGENTS

This sprint runs IN PARALLEL with Sprints 11-13. It addresses a different problem: the PDF extraction data is garbage (see Doc 70 for full diagnosis). Sprints 11-13 fix the PIPELINE. Sprint D fixes the DATA.

Sprint D is mostly CC and Antigravity. Codex agents may assist on specific tasks if available, but they should prioritize their Sprint 12-13 assignments.

### COMPLETION TRACKING

Same protocol as Sprints 12-13. When you finish a task, append to `docs/DONE.md`:
```
D.1 DONE [CC] 2026-02-17T14:30
```

Check DONE.md for dependencies before starting tasks that need other agents' work.

### BLANKET PERMISSIONS

Same as all sprints. Create, modify, delete files. Run code. Make decisions. Document in DECISIONS.md. Do not ask David for confirmation. Do not stop.

### REFERENCE DOCUMENTS

| Document | Location | Who needs it |
|----------|----------|-------------|
| Doc 70 (Diagnosis) | docs/Doc70_PDF_Data_Diagnosis_and_Remediation.md | Everyone |
| The CSV | data/production/realtime_pdf_confirmed_rows.csv | CC, AG |
| feature_mapping.py | src/cmr/feature_mapping.py | CC (vocabulary source 1) |
| claim_extraction.py | src/cmr/claim_extraction.py | CC (vocabulary source 2) |
| template_matching.py | src/cmr/template_matching.py | CC (vocabulary source 3) |
| Template JSONs | data/templates/*.json | CC (for DV extraction) |
| web_persistence.db | data/web_persistence.db | AG (current web, to be rebuilt) |

### THE CORE PROBLEM IN ONE SENTENCE

pdfplumber extracted 171,840 table cells from 386 papers but treated every cell-pair as a causal relationship, producing garbage like `environment_variable: "francesca ostuzzi design"` and `outcome_variable: "ffititttiningg thhee sseennssoorrss"`. The web of belief was populated from this garbage. We need to reprocess the raw text with semantic understanding.

---

## AGENT ASSIGNMENTS

| Agent | Tasks | Total |
|-------|-------|-------|
| **CC** | D.1, D.2, D.3, D.5, D.6, D.8, D.10, D.12 | 8 |
| **Antigravity** | D.4, D.7, D.9, D.11, D.13 | 5 |

---

## CC TASK LIST

---

### CC-D1: TASK D.1 — Consolidated Vocabulary Sheet
**Estimated: 90–120 min · Dependency: none · HIGHEST PRIORITY — everything else depends on this**

The system has THREE scattered synonym/mapping dictionaries that define what variables it recognises. Consolidate them into one authoritative file.

**Source 1:** `FEATURE_TO_TEMPLATE_INPUT` in `src/cmr/feature_mapping.py` (lines 58-117)
Maps template IDs to their input parameter names. These are the building-eval IVs.

**Source 2:** `_SYNONYMS` in `src/cmr/claim_extraction.py` (lines 85-99)
Maps natural language terms to canonical variable names. Tiny — only 9 entries.

**Source 3:** `_SYNONYM_GROUPS` in `src/cmr/template_matching.py` (lines 89-95)
Groups of equivalent terms. Only 5 groups.

**Also extract DVs from:** Template JSON files in `data/templates/`. Look at the `causal_links` field — each link has a `to_level` and `change_produced` that implies a DV. Also look at the template `name` field — e.g., "Anterior Insula as Salience Hub for Physical and Social Pain" implies DVs of pain perception, social distress.

Create `data/vocabulary/variable_vocabulary.json`:

```json
{
    "version": "1.0",
    "created": "2026-02-17",
    "independent_variables": {
        "ceiling_height_m": {
            "canonical": "ceiling_height_m",
            "synonyms": [
                "ceiling height", "room height", "floor-to-ceiling height",
                "high ceilings", "low ceilings", "double-height ceiling"
            ],
            "unit": "meters",
            "templates": ["VF3", "CREA2"],
            "domain": "A6_Visual_Form",
            "extraction_hints": [
                "Look for: height values in meters or feet",
                "Context clues: room dimensions, spatial proportions"
            ]
        },
        "illuminance_lux": {
            "canonical": "illuminance_lux",
            "synonyms": [
                "daylight", "illuminance", "light level", "lux",
                "lighting", "ambient light", "desktop illuminance",
                "horizontal illuminance", "vertical illuminance"
            ],
            "unit": "lux",
            "templates": ["L1", "L2", "L3", "CREA2"],
            "domain": "A4_Light",
            "extraction_hints": [
                "Look for: lux values, foot-candles (convert: 1 fc = 10.76 lux)",
                "Context clues: lighting conditions, daylight exposure"
            ]
        },
        "ambient_noise_dba": {
            "canonical": "ambient_noise_dba",
            "synonyms": [
                "noise", "ambient noise", "sound level", "noise level",
                "background noise", "dB(A)", "decibels", "Leq",
                "speech intelligibility"
            ],
            "unit": "dB(A)",
            "templates": ["CREA2", "SOC2"],
            "domain": "A3_Sound",
            "extraction_hints": [
                "Look for: dB values, dB(A), Leq, Ldn",
                "Context clues: acoustic environment, noise exposure, office noise"
            ]
        }
    },
    "dependent_variables": {
        "creativity": {
            "canonical": "creativity",
            "synonyms": [
                "creative thinking", "creative output", "divergent thinking",
                "creative performance", "ideation", "creative ideation",
                "novel solutions"
            ],
            "measurement_types": [
                "Remote Associates Test (RAT)", "Alternative Uses Task (AUT)",
                "Torrance Tests", "self-report creativity"
            ],
            "templates": ["CREA1", "CREA2", "CREA3", "CREA4"]
        },
        "stress": {
            "canonical": "stress",
            "synonyms": [
                "stress reduction", "stress recovery", "psychological stress",
                "perceived stress", "anxiety", "tension"
            ],
            "measurement_types": [
                "cortisol (salivary)", "PSS", "STAI", "VAS-stress",
                "blood pressure", "skin conductance"
            ],
            "templates": ["VIEW1", "T6-gap", "T7-gap"]
        },
        "productivity": {
            "canonical": "productivity",
            "synonyms": [
                "work performance", "task performance", "cognitive performance",
                "work output", "efficiency", "work effectiveness"
            ],
            "measurement_types": [
                "typing speed", "error rate", "self-report",
                "supervisor rating", "output quantity"
            ],
            "templates": ["MAT1", "SOC2", "L2"]
        }
    },
    "unmapped_flag": "NEW_VARIABLE"
}
```

**CRITICAL:** This must be COMPREHENSIVE. Walk through ALL 150 template JSON files and extract every IV and DV. Walk through all three source dicts and merge. Add reasonable synonyms from your domain knowledge (you know what "RAT" means in creativity research, what "PSS" means in stress research, etc.).

The vocabulary should cover at MINIMUM:
- **IVs:** ceiling_height_m, floor_area_m2, illuminance_lux, ambient_noise_dba, has_nature_view, view_content, view_distance_m, view_sky_fraction, primary_material, natural_material_ratio, surface_effusivity, contact_temperature_c, operative_temp_c, running_mean_outdoor_c, ventilation_type, cct_kelvin, has_daylight_variation, shared_area_ratio, phone_booths_per_worker, visual_privacy_score, acoustic_privacy_stc, spatial_integration_score, layout_legibility, color (wall_colors), stair_dimensions, thermal_system, walking_paths, wayfinding_clarity
- **DVs:** creativity, stress, productivity, preference, recovery_time, pain_medication_use, cognitive_flexibility, attention, mood, well-being, thermal_comfort, acoustic_satisfaction, visual_comfort, wayfinding_success, social_interaction, privacy_satisfaction, physiological_arousal, cortisol, heart_rate_variability, blood_pressure, skin_conductance, sleep_quality, cognitive_load, memory, learning, restorative_experience, place_attachment, aesthetic_pleasure

Also create `src/extraction/vocabulary.py`:

```python
def load_vocabulary() -> dict:
    """Load the canonical variable vocabulary."""

def find_closest_iv(term: str) -> tuple[str, float]:
    """Given a natural language term, find the closest canonical IV.
    Returns (canonical_name, confidence).
    Uses fuzzy matching + synonym lookup."""

def find_closest_dv(term: str) -> tuple[str, float]:
    """Same for DVs."""

def get_extraction_prompt_vocabulary() -> str:
    """Format the vocabulary as a reference sheet for LLM extraction prompts.
    Returns a formatted string listing all IVs and DVs with synonyms."""
```

Write tests: `find_closest_iv("ceiling height")` → `("ceiling_height_m", 1.0)`. `find_closest_iv("room tallness")` → `("ceiling_height_m", 0.7)`. `find_closest_dv("cortisol levels")` → `("stress", 0.9)`.

When done: `D.1 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-D2: TASK D.2 — Paper Triage Classifier
**Estimated: 90–120 min · Dependency: none**

Of 386 papers in the CSV, identify which contain extractable empirical findings.

Create `src/extraction/paper_triage.py`:

```python
def triage_papers(csv_path: str = "data/production/realtime_pdf_confirmed_rows.csv") -> dict:
    """Classify each paper by type using its abstract + extracted content.
    Returns {paper_id: {type, confidence, n_rows, has_tables, relevant_domains}}"""
```

**Step 1:** Extract unique paper_ids from the CSV. Get all rows for each paper. From the `articles` table in ae.db, get the title and abstract where available.

**Step 2:** For each paper, construct a classification prompt using:
- Title + abstract (if available)
- The `article_type_predicted_family` from the CSV (use as a hint, not gospel)
- Count of table-sourced rows vs discourse-sourced rows
- A sample of the `statement` text (first 5 statements)

**Step 3:** Classify into:

| Type | Contains extractable findings? | Action |
|---|---|---|
| `empirical` | YES — original experiments or measurements | → Stage 1 |
| `review` | YES — summarises others' findings in tables | → Stage 1 |
| `meta_analysis` | YES — forest plots, summary effect sizes | → Stage 1 (high priority) |
| `theoretical` | NO — proposes frameworks, no data | → Theory links only |
| `methods` | NO — describes tools or protocols | → Skip |
| `off_topic` | NO — not about architecture/environment | → Skip |

**Step 4:** For `empirical`, `review`, and `meta_analysis` papers, flag which architectural DOMAINS they're relevant to (light, sound, spatial, materials, etc.) by keyword matching the abstract against domain vocabulary.

**Output:** `data/production/paper_triage.json`

**Classification method:** Use the Anthropic API (the system already has credentials and Sprint 11 shows API calls work). Send each paper's abstract + sample content to Sonnet with a structured classification prompt. This is a batch of ~386 short prompts — fast and cheap.

If the API is not available or you want to avoid costs: fall back to rule-based classification using `article_type_predicted_family` + keyword heuristics. The rule-based version will be ~70% accurate vs ~95% for the LLM version, but it's a start.

Write tests. Report: how many papers per type, how many proceed to Stage 1.

When done: `D.2 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-D3: TASK D.3 — Table Reconstruction and Classification
**Estimated: 120–180 min · Dependency: D.2 DONE**

The CSV has individual rows from tables, but we need WHOLE TABLES to classify them. Reconstruct tables from the `source_table_id` field, then classify each table.

Create `src/extraction/table_classifier.py`:

**Step 1 — Table Reconstruction:**

```python
def reconstruct_tables(csv_path: str, paper_ids: list[str]) -> dict:
    """Group CSV rows by source_table_id. For each table, collect:
    - All rows (in order by source_table_row)
    - The full content of each row
    - The paper_id and source_page
    Returns {source_table_id: {paper_id, page, rows: [...]}}"""
```

**Step 2 — Table Classification:**

For each reconstructed table from a triaged `empirical`/`review`/`meta_analysis` paper, classify its semantic type:

```python
TABLE_TYPES = [
    "RESULTS_ANOVA",        # F-tests, ANOVAs — IVs and DVs in the design
    "RESULTS_REGRESSION",   # Beta weights, R² — predictors and outcomes
    "RESULTS_CORRELATION",  # Correlation matrices — variable pairs
    "RESULTS_TTEST",        # t-tests, group comparisons
    "RESULTS_DESCRIPTIVE",  # Means/SDs of DV by condition — extractable
    "LITERATURE_REVIEW",    # Each row = a study with IV→DV — extractable
    "META_ANALYTIC",        # Forest plot data, summary effect sizes
    "DEMOGRAPHICS",         # Participant characteristics — skip
    "MODEL_FIT",            # χ², RMSEA, CFI — skip
    "PROTOCOL",             # Experimental procedure — skip
    "MATERIALS",            # Stimuli descriptions — flag for review
    "MEASUREMENT_SPECS",    # Instrument calibration — skip
    "OTHER",                # Unclassifiable
]
```

**Classification signals** (for rule-based or LLM-assisted):
- Contains F(df1, df2), t(df), χ² → RESULTS
- Contains β, B, SE → REGRESSION
- Contains r = 0.xx in a matrix layout → CORRELATION
- Column headers include "Mean", "SD", "N" by condition → DESCRIPTIVE
- Contains author names + year + findings → LITERATURE_REVIEW
- Contains "Effect size", "CI", "Weight" → META_ANALYTIC
- Contains "Age", "Gender", "Education" → DEMOGRAPHICS
- Contains "χ²/df", "RMSEA", "CFI", "GFI" → MODEL_FIT
- Contains "Step 1", "Procedure", "Protocol" → PROTOCOL
- Contains garbled text (doubled characters) → GARBAGE

**GARBAGE DETECTION:** Also flag tables with obvious OCR failures:
- Doubled character sequences (e.g., "ttaacctitliele" → "tactile")
- Columns concatenated without spaces (e.g., "samplephotoofroomwithhighsalience")
- Non-word character sequences

**Output:** `data/production/table_classifications.json`:
```json
{
    "TBL-20260214092226-002": {
        "paper_id": "doi:10.3390/ijerph7031036",
        "page": 8,
        "type": "RESULTS_REGRESSION",
        "confidence": 0.85,
        "n_rows": 4,
        "extractable": true,
        "ocr_quality": "clean",
        "sample_content": "b1 = 0.1626 b2 = 0.3428 ..."
    },
    "TBL-20260214092358-001": {
        "paper_id": "doi:10.1145/2079216.2079270",
        "page": 2,
        "type": "MATERIALS",
        "confidence": 0.70,
        "n_rows": 3,
        "extractable": false,
        "ocr_quality": "clean",
        "sample_content": "Visualproperties: Tactual properties"
    }
}
```

Report: how many tables total, how many extractable, how many garbage, how many by type.

When done: `D.3 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-D4: TASK D.5 — Gold Standard: Hand-Curate 15 Key Papers
**Estimated: 180–240 min · Dependency: D.1 DONE**

While the automated pipeline is being built, hand-curate claims from the 15 most important papers — the ones the calibration panels already cite. This produces a PERFECT validation dataset.

Create `data/gold_standard/` with one JSON file per paper.

**Paper list** (from calibration panel references — these are papers we KNOW contain relevant findings):

1. Ulrich (1984) — nature view → recovery (VIEW1)
2. Mehaffy & Salingaros (2015) — fractal dimension → preference (VF2)
3. Vartanian et al. (2013) — contour curvature → approach/avoid (VF1)
4. Baird et al. (2012) — ceiling height → creativity (VF3)
5. Mehta et al. (2012) — noise → creativity (CREA2)
6. Küller et al. (2006) — color → mood/performance (COL1)
7. Leaman & Bordass (2007) — building performance → satisfaction (SOC2)
8. de Dear & Brager (1998) — adaptive thermal comfort (MAT1/MAT2)
9. Heschong (1999) — daylight → student performance (L2)
10. Kaplan (1995) — ART theory paper (ART reduction)
11. Evans & McCoy (1998) — stress & architecture (T6/T7)
12. Appleton (1975) — prospect/refuge theory (SC2)
13. Kellert (2005) — biophilic design patterns (Biophilia reduction)
14. Salingaros (2012) — scaling coherence → affect (VF2/SCI)
15. Leesman (2017) — workplace effectiveness survey (SOC2/SOC3)

For each paper, create `data/gold_standard/ulrich_1984.json`:

```json
{
    "paper_id": "doi:10.1126/science.6143402",
    "citation": "Ulrich, R.S. (1984). View through a window may influence recovery from surgery. Science, 224, 420-421.",
    "article_type": "empirical",
    "claims": [
        {
            "claim_id": "ulrich_1984_c1",
            "iv": "has_nature_view",
            "iv_detail": "view of deciduous trees vs brick wall",
            "dv": "recovery_time",
            "dv_detail": "post-surgical hospital stay duration",
            "direction": "decrease",
            "effect_size": -0.71,
            "effect_size_type": "cohens_d",
            "sample_n": 46,
            "context": "hospital, cholecystectomy patients",
            "source": "Table 1 and text",
            "notes": "Matched pairs design, 23 pairs"
        },
        {
            "claim_id": "ulrich_1984_c2",
            "iv": "has_nature_view",
            "iv_detail": "view of trees vs brick wall",
            "dv": "pain_medication_use",
            "dv_detail": "number of moderate-strong analgesic doses",
            "direction": "decrease",
            "effect_size": -0.50,
            "effect_size_type": "cohens_d_estimated",
            "sample_n": 46,
            "context": "hospital, post-surgical days 2-5",
            "source": "Table 2",
            "notes": "Significant for days 2-5, not days 0-1"
        },
        {
            "claim_id": "ulrich_1984_c3",
            "iv": "has_nature_view",
            "iv_detail": "view of trees vs brick wall",
            "dv": "mood",
            "dv_detail": "negative evaluative comments in nurses' notes",
            "direction": "decrease",
            "effect_size": null,
            "effect_size_type": null,
            "sample_n": 46,
            "context": "hospital, nurse records",
            "source": "Results section",
            "notes": "Wall-view patients had more negative notes"
        }
    ],
    "theory_links": ["ART", "SRT"],
    "templates_expected": ["VIEW1"],
    "gold_standard": true
}
```

**IMPORTANT:** You know most of these papers from the panel documents. Use your knowledge. But if you need to verify specific numbers (effect sizes, sample sizes), note them as estimates and flag with `effect_size_type: "cohens_d_estimated"`.

This is painstaking work but it produces the ground truth the entire system validates against.

When done: `D.5 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-D5: TASK D.6 — Structured Claim Extraction Engine
**Estimated: 120–180 min · Dependency: D.1 + D.3 DONE**

The core extraction engine. Takes a classified table and produces structured claims using the vocabulary sheet.

Create `src/extraction/claim_extractor.py`:

```python
def extract_claims_from_table(
    table: dict,           # Reconstructed table from D.3
    paper_context: dict,   # {paper_id, title, abstract, article_type}
    vocabulary: dict,      # From D.1
    method: str = "llm"    # "llm" or "rule_based"
) -> list[dict]:
    """Extract structured IV→DV claims from a classified table.
    
    For RESULTS tables: identify the experimental design (IV conditions) 
    and outcome measures (DVs), extract each IV→DV pair with direction 
    and any available effect sizes.
    
    For LITERATURE_REVIEW tables: each row is typically one study, 
    extract the IV, DV, and finding per row.
    
    Returns list of claims in process_paper() format:
    [{iv, dv, direction, effect_size, sample_n, context, source_quote, ...}]
    """

def extract_claims_from_paper(
    paper_id: str,
    tables: list[dict],           # All tables for this paper
    paper_context: dict,
    vocabulary: dict,
    method: str = "llm"
) -> list[dict]:
    """Extract all claims from all extractable tables in a paper."""
```

**LLM extraction prompt** (this is the critical artifact):

```
You are extracting structured scientific claims from a data table in a 
research paper about how architectural features affect human wellbeing.

PAPER: {title}
ABSTRACT: {abstract}
TABLE TYPE: {table_type}
TABLE CONTENT:
{table_content}

TASK: Extract each causal claim from this table. For each claim, identify:
1. The independent variable (what was manipulated or measured as a predictor)
2. The dependent variable (what outcome was measured)
3. The direction of the effect (increase / decrease / no_effect)
4. The effect size (if available: Cohen's d, r, η², β, F, t, or p-value)
5. The sample size (if available)
6. The context (office, hospital, school, lab, etc.)

MAP variables to the closest term from this vocabulary:

INDEPENDENT VARIABLES:
{formatted_iv_vocabulary}

DEPENDENT VARIABLES:  
{formatted_dv_vocabulary}

If no close match exists, use a descriptive term and set mapped=false.

OUTPUT FORMAT (JSON array):
[
  {
    "iv": "canonical_iv_name",
    "iv_raw": "original text from table",
    "iv_mapped": true,
    "dv": "canonical_dv_name", 
    "dv_raw": "original text from table",
    "dv_mapped": true,
    "direction": "increase|decrease|no_effect",
    "effect_size": 0.5,
    "effect_size_type": "cohens_d|r|eta_squared|beta|f_value|t_value|null",
    "sample_n": 120,
    "p_value": 0.03,
    "context": "office",
    "source_quote": "exact text from table supporting this claim"
  }
]

RULES:
- Only extract CAUSAL or CORRELATIONAL claims, not descriptive statistics
- Skip demographic data, model fit indices, and measurement specifications
- If the table contains regression weights, the predictors are IVs and the criterion is the DV
- If the table is a correlation matrix, each significant correlation is a claim
- Report "no_effect" for non-significant findings — these are important too
- Include the EXACT source text that supports each claim
```

**Rule-based fallback** for when LLM is unavailable:

```python
def _rule_based_extract(table: dict, vocabulary: dict) -> list[dict]:
    """Heuristic extraction:
    1. Look for column headers matching IV/DV vocabulary
    2. Look for statistical values (F, t, r, p) in cells
    3. Look for direction words (increase, decrease, higher, lower)
    4. Construct claims from header-cell pairings
    """
```

The rule-based version will catch ~40% of what the LLM catches, but it's deterministic and free.

**Tests:** Run on the gold standard papers (D.5). The extractor should recover claims that match the hand-curated ones. Define matching criteria: same IV (or synonym), same DV (or synonym), same direction. Effect size match is a bonus.

When done: `D.6 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-D6: TASK D.8 — Effect Size Converter
**Estimated: 60–90 min · Dependency: none**

Many tables report F-values, t-values, r, η², or β instead of Cohen's d. The system needs Cohen's d for WIS conversion. Build the converter.

Create `src/extraction/effect_size_converter.py`:

```python
def to_cohens_d(
    value: float,
    stat_type: str,      # "f_value", "t_value", "r", "eta_squared", "beta", 
                         # "odds_ratio", "cohens_d", "p_value_only"
    df1: int = None,     # numerator df (for F)
    df2: int = None,     # denominator df / error df (for F, t)
    n: int = None,       # total sample size
    n1: int = None,      # group 1 size (for t with unequal groups)
    n2: int = None,      # group 2 size
) -> dict:
    """Convert any common effect size metric to Cohen's d.
    
    Returns {d: float, se: float, ci_lower: float, ci_upper: float, 
             method: str, assumptions: list[str]}
    """
```

**Conversion formulas:**

```python
# t → d (equal groups)
d = 2 * t / sqrt(df)

# t → d (unequal groups)  
d = t * sqrt(1/n1 + 1/n2)

# F (1 df_num) → d
d = 2 * sqrt(F / df2)

# r → d
d = 2 * r / sqrt(1 - r**2)

# η² → d  
d = 2 * sqrt(eta_sq / (1 - eta_sq))

# β (standardized regression) → d (approximate)
d = 2 * beta / sqrt(1 - beta**2)  # rough, note assumption

# Odds ratio → d
d = log(OR) * sqrt(3) / pi

# p-value only → d (last resort, requires N)
# Use inverse normal to get z, then d = 2*z/sqrt(N)
```

Include warnings for:
- F with df1 > 1 (omnibus test, not directional — d is approximate)
- Very small samples (d inflated — apply Hedges' g correction)
- β from multiple regression (d approximation assumes simple relationship)
- p-value-only conversion (very rough, flag as low confidence)

Apply **Hedges' g correction** for small samples:
```python
g = d * (1 - 3 / (4 * (n1 + n2) - 9))
```

**Tests:** Known values from textbooks:
- t(38) = 2.10 → d ≈ 0.68
- F(1, 60) = 4.0 → d ≈ 0.52
- r = 0.30 → d ≈ 0.63
- η² = 0.06 → d ≈ 0.51

When done: `D.8 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-D7: TASK D.10 — Batch Extraction Pipeline
**Estimated: 90–120 min · Dependency: D.2 + D.3 + D.6 + D.8 DONE**

Wire together triage → table classification → claim extraction → effect size conversion into a single batch pipeline.

Create `src/extraction/batch_extract.py`:

```python
def run_batch_extraction(
    csv_path: str = "data/production/realtime_pdf_confirmed_rows.csv",
    triage_path: str = "data/production/paper_triage.json",
    table_class_path: str = "data/production/table_classifications.json",
    vocabulary_path: str = "data/vocabulary/variable_vocabulary.json",
    output_path: str = "data/production/structured_claims.json",
    method: str = "rule_based",  # "llm" or "rule_based"
    limit: int = None,           # Process only N papers (for testing)
) -> dict:
    """Full batch extraction pipeline.
    
    1. Load triage results — filter to empirical/review/meta papers
    2. Load table classifications — filter to extractable types
    3. For each extractable table: run claim extraction
    4. For each extracted claim: convert effect sizes to Cohen's d
    5. Deduplicate claims (same IV+DV+direction from same paper)
    6. Save structured_claims.json
    7. Return summary statistics
    """
```

**Output:** `data/production/structured_claims.json`:
```json
{
    "extraction_date": "2026-02-17",
    "method": "rule_based",
    "papers_processed": 142,
    "tables_processed": 387,
    "claims_extracted": 1847,
    "claims_with_effect_size": 623,
    "claims_with_sample_n": 891,
    "new_variables_flagged": 47,
    "claims": [
        {
            "claim_id": "doi:10.20944/preprints201907.0323.v1:TBL-001:C001",
            "paper_id": "doi:10.20944/preprints201907.0323.v1",
            "iv": "operative_temp_c",
            "iv_raw": "Temperature deviation",
            "dv": "productivity",
            "dv_raw": "Lowering the rate of performance and productivity",
            "direction": "negative",
            "effect_size": null,
            "effect_size_type": null,
            "sample_n": null,
            "context": "office",
            "source_table_id": "TBL-20260214092258-001",
            "source_page": 10,
            "source_quote": "Deviation Contributors: Temperature...",
            "extraction_confidence": 0.75,
            "vocabulary_mapped": true
        }
    ]
}
```

CLI:
```bash
# Test on 5 papers
python -m src.extraction.batch_extract --limit 5 --method rule_based

# Full run
python -m src.extraction.batch_extract --method rule_based
```

When done: `D.10 DONE [CC] <timestamp>` → `docs/DONE.md`

---

### CC-D8: TASK D.12 — CMR Pipeline Integration
**Estimated: 60–90 min · Dependency: D.10 + D.11 (AG) DONE**

Feed the clean structured claims into the existing CMR paper evaluation pipeline.

Create `src/extraction/feed_cmr.py`:

```python
def feed_claims_to_cmr(
    claims_path: str = "data/production/structured_claims.json",
    gold_standard_dir: str = "data/gold_standard/",
    db_path: str = "ae.db"
) -> dict:
    """Process all extracted claims through the CMR pipeline.
    
    1. Load structured claims
    2. Group by paper_id
    3. For each paper: call process_paper() from src/cmr/process_paper.py
    4. Collect: template matches, contradictions, confirmations, gaps, VOI
    5. Compare results against gold standard (where available)
    6. Return comprehensive report
    """
```

**Validation:** For the 15 gold-standard papers, compare:
- Did the pipeline match the expected templates?
- Did it detect the right direction?
- Did the VOI scores make sense?

**Report:** `data/production/cmr_integration_report.json`:
```json
{
    "papers_processed": 142,
    "total_claims": 1847,
    "claims_matched_to_templates": 623,
    "claims_unmatched": 1224,
    "contradictions_found": 18,
    "confirmations_found": 412,
    "gaps_identified": 193,
    "update_proposals_generated": 31,
    "gold_standard_validation": {
        "papers_tested": 15,
        "template_match_accuracy": 0.87,
        "direction_accuracy": 0.93,
        "false_matches": 4,
        "missed_matches": 7
    }
}
```

When done: `D.12 DONE [CC] <timestamp>` → `docs/DONE.md`

---

## ANTIGRAVITY TASK LIST

---

### AG-D1: TASK D.4 — Garbage Audit: Quantify What's Usable
**Estimated: 60–90 min · Dependency: none**

Before we rebuild, precisely quantify the damage. Analyze the FULL 154 MB CSV (not just the first 10k rows).

Create `scripts/full_csv_audit.py`:

```python
def audit_csv(csv_path: str) -> dict:
    """Complete audit of the CSV."""
```

Report:

1. **Total rows by source type:**
   - `codex_pdfplumber` (table extractions) — how many?
   - `pdf_discourse_scan` (discourse fragments) — how many?
   - Any other sources?

2. **Table extractions breakdown:**
   - How many unique `source_table_id` values? (= number of tables extracted)
   - Average rows per table
   - How many tables have ≥1 row with a non-null environment_variable?

3. **OCR quality check:**
   - How many rows contain doubled character sequences (regex: `(.)\1{2,}` within words)?
   - How many rows have the `environment_variable == outcome_variable` (= extractor couldn't distinguish IV from DV)?
   - How many rows have `environment_resolution_confidence < 0.3`?
   - How many rows have `environment_resolution_match_type == "domain_inferred"` (= system guessed)?

4. **Discourse row classification:**
   - How many are `claim_type: inter_article_relation` (citation fragments)?
   - How many are `claim_type: theory_link` (theory invocations)?
   - How many are `claim_type: finding`?
   - Any other claim_types?

5. **Paper coverage:**
   - How many unique papers?
   - Distribution: papers with 1-10 rows, 10-100 rows, 100-500 rows, 500+ rows
   - Papers with ZERO extractable tables (pure discourse)

6. **The one good variable pair:**
   - How many rows have BOTH environment_variable AND outcome_variable present, AND environment_resolution_confidence > 0.5, AND outcome_resolution_confidence > 0.5?
   - List those variable pairs and their frequencies

Save report to `docs/full_csv_audit_report.md`.

When done: `D.4 DONE [AG] <timestamp>` → `docs/DONE.md`

---

### AG-D2: TASK D.7 — Gold Standard Validation Framework
**Estimated: 60–90 min · Dependency: D.5 (CC) DONE**

Build the test harness that validates automated extraction against gold standard.

Create `tests/test_extraction_accuracy.py`:

```python
def test_extraction_against_gold_standard():
    """For each gold-standard paper:
    1. Run the automated extractor on its tables
    2. Compare extracted claims against hand-curated claims
    3. Score: precision, recall, F1 for claim detection
    4. Score: accuracy for IV mapping, DV mapping, direction
    """

def compare_claims(extracted: list[dict], gold: list[dict]) -> dict:
    """Match extracted claims to gold claims.
    A match requires: same IV (or synonym), same DV (or synonym), same direction.
    Returns {precision, recall, f1, iv_accuracy, dv_accuracy, 
             direction_accuracy, effect_size_correlation}"""
```

Also create `scripts/extraction_accuracy_report.py` that runs the comparison and produces a human-readable report:

```
EXTRACTION ACCURACY REPORT
==========================
Paper: Ulrich (1984)
  Gold claims: 3
  Extracted claims: 4
  Matched: 3
  Precision: 0.75 (3/4)
  Recall: 1.00 (3/3)
  F1: 0.86
  
  Claim 1: nature_view → recovery_time (decrease)
    ✅ Matched: IV correct, DV correct, direction correct
    Effect size: gold=-0.71, extracted=-0.68 (Δ=0.03)
  
  Claim 2: nature_view → pain_medication_use (decrease)
    ✅ Matched: IV correct, DV correct, direction correct
    
  Claim 3: nature_view → mood (decrease in negative comments)
    ✅ Matched: IV correct, DV correct, direction correct

  Claim 4 (extracted, no gold match):
    ceiling_height → preference (increase)
    ❌ FALSE POSITIVE — from a citation in the discussion, not a finding
    
OVERALL:
  Mean precision: 0.82
  Mean recall: 0.73
  Mean F1: 0.77
  IV mapping accuracy: 0.91
  DV mapping accuracy: 0.85
  Direction accuracy: 0.94
```

This framework is what tells us whether the extraction pipeline is good enough.

When done: `D.7 DONE [AG] <timestamp>` → `docs/DONE.md`

---

### AG-D3: TASK D.9 — Web of Belief Health Report (Pre-Rebuild)
**Estimated: 60–90 min · Dependency: D.4 DONE**

Before rebuilding the web, document exactly what's in it and why it's bad. This is the "before" snapshot.

Create `scripts/web_health_report.py`:

Query `data/web_persistence.db` directly:

```python
def web_health_report(db_path: str = "data/web_persistence.db") -> dict:
    """Comprehensive health check of the current web of belief."""
```

Report:

1. **Belief quality:**
   - How many beliefs have `environment_id` starting with `env.unresolved.`? (= variable not mapped)
   - How many have `outcome_id` starting with `out.unresolved.`? (= outcome not mapped)
   - How many have `credence_value < 0.4`? (= system itself doesn't believe them)
   - How many have content that contains OCR artifacts (doubled characters)?
   - How many have content < 10 characters? (= truncated)
   - How many have content > 500 characters? (= probably a paragraph, not a claim)

2. **Constraint quality:**
   - How many constraints link two `unresolved` beliefs? (= linking garbage to garbage)
   - Distribution of constraint strengths
   - How many have `warrant_type: cross_paper_alignment`? (= based on shared variables — but the variables are wrong)

3. **Bridge quality:**
   - How many bridges have `confidence < 0.4`? 
   - How many have `status: hypothesized` (= never tested)?
   - Most common source_domain → target_domain pairs

4. **Coherence trajectory:**
   - Plot (text format) of coherence_score over time from coherence_history
   - 690 coherence alerts — all "sharp_decline"?

5. **Bottom line assessment:**
   - What percentage of beliefs contain real scientific claims?
   - What percentage are noise?
   - Is ANY part of the web worth preserving?

Save to `docs/web_health_report_pre_rebuild.md`.

When done: `D.9 DONE [AG] <timestamp>` → `docs/DONE.md`

---

### AG-D4: TASK D.11 — Web of Belief Rebuild
**Estimated: 120–180 min · Dependency: D.9 DONE + D.10 (CC) DONE**

Replace the garbage web with a clean one built from the structured claims.

Create `src/extraction/web_rebuilder.py`:

```python
def rebuild_web(
    claims_path: str = "data/production/structured_claims.json",
    gold_standard_dir: str = "data/gold_standard/",
    output_db_path: str = "data/web_persistence_v2.db",
    backup_current: bool = True
) -> dict:
    """Build a new web of belief from clean structured claims.
    
    1. Back up current web_persistence.db
    2. Create new empty web
    3. For each paper's claims:
       a. Create one belief per claim
       b. Set proper environment_id and outcome_id from vocabulary mapping
       c. Set credence based on: effect_size strength, sample_n, study type
       d. Create intra-paper constraints (claims from same paper are coherent)
    4. Create cross-paper constraints:
       a. Same IV→DV pair in different papers → replication link
       b. Same IV, different DV in different papers → scope extension
       c. Contradicting direction for same IV→DV → contradiction constraint
    5. Create template-level bridges:
       a. If two claims map to the same template → template bridge
       b. If two claims map to templates in the same domain → domain bridge
    6. Compute coherence
    7. Save to output_db_path
    """
```

**Credence assignment:**
```python
def compute_credence(claim: dict) -> float:
    """Assign credence (0-1) based on claim quality.
    
    Base: 0.5
    + 0.1 if effect_size present
    + 0.1 if sample_n > 50
    + 0.05 if sample_n > 200
    + 0.1 if from gold_standard paper
    + 0.05 if vocabulary_mapped = true (both IV and DV)
    - 0.1 if extraction_confidence < 0.5
    - 0.05 if effect_size_type = "p_value_only" (weak conversion)
    Cap at [0.2, 0.95]
    """
```

**Expected outcome:**
- ~1,000-5,000 real beliefs (down from 12,628 garbage)
- Each belief is a real scientific claim with mapped IV, DV, direction
- Constraints are meaningful (replication, contradiction, scope)
- Coherence score reflects actual scientific consensus

**DO NOT delete the old web.** Keep `data/web_persistence.db` as-is. Create `data/web_persistence_v2.db`. The CMR pipeline can be pointed at either.

Also produce `docs/web_health_report_post_rebuild.md` comparing the old and new webs.

When done: `D.11 DONE [AG] <timestamp>` → `docs/DONE.md`

---

### AG-D5: TASK D.13 — Sprint D Validation
**Estimated: 90–120 min · Dependency: ALL Sprint D tasks DONE**

Final validation of the entire data remediation.

Run:
1. **Extraction accuracy** on all 15 gold-standard papers (from D.7 framework)
2. **Web comparison**: old web vs new web (beliefs count, unresolved rate, coherence)
3. **Pipeline end-to-end**: feed 5 gold-standard papers through CMR pipeline, verify sensible results
4. **Regression check**: verify the pipeline STILL works on Sprint 11's synthetic test cases

Produce `docs/sprint_d_validation_report.md`:

```
SPRINT D VALIDATION REPORT
===========================

EXTRACTION ACCURACY:
  Papers tested: 15
  Mean F1: 0.XX
  IV mapping accuracy: 0.XX
  DV mapping accuracy: 0.XX
  
WEB OF BELIEF COMPARISON:
  Metric            Old Web     New Web
  ------            -------     -------
  Beliefs           12,628      X,XXX
  Unresolved IVs    XX%         X%
  Unresolved DVs    XX%         X%  
  Constraints       28,314      X,XXX
  Coherence         0.416       0.XXX
  
CMR PIPELINE RESULTS (5 gold papers):
  Paper                Template Matches    Direction OK?
  Ulrich 1984          VIEW1 ✅            ✅
  Mehta et al 2012     CREA2 ✅            ✅
  ...

VERDICT: [PASS / NEEDS WORK / FAIL]
```

When done: `D.13 DONE [AG] <timestamp>` → `docs/DONE.md`

---

## DEPENDENCY GRAPH

```
D.1 CC (vocabulary) ─────┬─→ D.5 CC (gold standard) ─→ D.7 AG (validation framework)
                          └─→ D.6 CC (extraction engine) ──┐
D.2 CC (triage) ──→ D.3 CC (table classification) ────────┘
                                                            │
D.8 CC (effect size converter, no deps) ───────────────────┘
                                                            │
D.4 AG (garbage audit, no deps) ──→ D.9 AG (web health)    │
                                                            ↓
                                              D.10 CC (batch pipeline)
                                                     │
                                                     ├─→ D.11 AG (web rebuild)
                                                     │        │
                                                     ↓        ↓
                                              D.12 CC (CMR integration)
                                                            │
                                                            ↓
                                              D.13 AG (sprint validation)
```

**Parallelism:**
- CC starts immediately on D.1, D.2, D.8 (all have no deps)
- AG starts immediately on D.4 (no deps)
- CC's D.3 unblocks after D.2; D.5 and D.6 unblock after D.1
- AG's D.7 unblocks after CC finishes D.5
- D.10 (batch pipeline) is the convergence point — needs D.2 + D.3 + D.6 + D.8
- D.11 (web rebuild) and D.12 (CMR integration) follow D.10
- D.13 validates everything

---

## COMPLETION CRITERIA

**Minimum viable:**
1. ✅ Vocabulary sheet consolidates all three sources + template DVs (D.1)
2. ✅ Paper triage classifies 386 papers (D.2)
3. ✅ Gold standard: 15 papers hand-curated (D.5)
4. ✅ Garbage audit quantifies the damage (D.4)
5. ✅ Extraction engine produces clean claims from classified tables (D.6)
6. ✅ Batch pipeline runs end-to-end (D.10)
7. ✅ Web rebuilt from clean data (D.11)

**Full sprint:**
8. ✅ Table classifier identifies extractable vs garbage tables (D.3)
9. ✅ Effect size converter handles F, t, r, η², β, OR (D.8)
10. ✅ Extraction accuracy measured against gold standard (D.7, D.13)
11. ✅ CMR pipeline produces sensible results on clean data (D.12)
12. ✅ Web health comparison: old vs new (D.9, D.11)
13. ✅ Sprint validation report produced (D.13)

---

*Sprint D: Data Remediation — February 17, 2026*
*13 tasks · CC: 8 tasks · Antigravity: 5 tasks*
*Estimated total effort: ~20-30 agent-hours*
*Runs in parallel with Sprints 11-13*
*After Sprint D: the system has clean data AND a working pipeline*
