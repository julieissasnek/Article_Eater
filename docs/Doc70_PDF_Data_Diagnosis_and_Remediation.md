# PDF DATA PIPELINE: FULL DIAGNOSIS AND REMEDIATION ARCHITECTURE
## Document 70 — February 17, 2026
## Prepared by Opus for David Kirsh

---

## 1. EXECUTIVE SUMMARY

The PDF extraction pipeline is producing noise, not data. The problem is not that 93% of rows lack structure — it's that **the 7% that HAVE structure are also garbage.** The "structured" rows contain raw PDF table cell scrapes being treated as scientific variables: author biographies mistaken for independent variables, OCR artifacts treated as dependent variables, statistical fit indices labelled as causal findings.

The web of belief (12,628 beliefs, 28,314 constraints) was populated from this garbage. It is not a knowledge base — it is a 83 MB monument to garbage-in-garbage-out. The 0.42 coherence score is measuring the internal consistency of noise.

The good news: the raw SOURCE material is there. The `source_quote` and `statement` fields contain real text from real papers. The problem is entirely in the INTERPRETATION layer — the code that decides what a table cell MEANS. This is fixable, but it requires rethinking the extraction architecture, not patching the current one.

---

## 2. THE FIVE INTERLOCKING FAILURES

### Failure 1: pdfplumber Extracts Table Cells, Not Table Semantics

The extraction source is `codex_pdfplumber`. It correctly extracts text from PDF tables. But it treats every cell-pair as a potential IV→DV relationship. Consider what it produced:

```
environment_variable: "half-life half-life"
outcome_variable: "half-life half-life"
```

This is a regression coefficient table. "Half-life" is a COLUMN HEADER in a table of pollutant decay rates. pdfplumber extracted the cell content but has no idea that this row contains `b1 = 0.1626, b2 = 0.3428, b3 = -0.1387` — i.e., regression weights, not a causal relationship.

More examples from the structured 7%:

| environment_variable | What it actually is |
|---|---|
| `francesca ostuzzi design` | Author biography from an About the Authors section |
| `ffititttiningg thhee sseennssoorrss` | OCR duplication artifact: "Fitting the sensors" with doubled characters |
| `ttaacctitliele exxppeerirmimenentt dduummmmyy` | Same OCR doubling: "Tactile experiment: Dummy" |
| `pure white chocolate` | Color swatch labels from a materials experiment |
| `appendix figurea1 samplephotoofroomwithhighsalience` | Figure caption, not a variable |
| `common value s5a` | SEM fit indices (χ², df, RMSEA) from a model fit table |
| `csihpipless aobrsdtrera csttrbuicotluorge` | Completely garbled text from column misalignment |

Only ONE of the 20 structured sample rows contained a real causal relationship:

```
environment_variable: "deviation contributors temperature"
outcome_variable: "productivity"
effect_direction: negative
```

That's from doi:10.20944/preprints201907.0323.v1, and it's a genuine finding — temperature deviations reduce productivity. But even here, the environment_variable is a table header fragment ("Deviation Contributors: Temperature"), not a clean variable name.

**Diagnosis:** The extractor has no model of table structure. It does not distinguish: header rows from data rows, results tables from demographics tables, figure captions from findings, author biographies from methods sections, or column headers from cell values.

### Failure 2: Variable Resolution Maps to Meaningless Canonical IDs

The few rows where a real variable WAS extracted get mapped to overly generic canonical IDs:

```
environment_variable: "ceiling height"
environment_canonical_id: env.generic.spatial_layout    # Too vague
environment_resolution_match_type: generic_keyword
environment_resolution_confidence: 0.35                  # System knows it's guessing
```

The CMR pipeline already has a `_SYNONYMS` dict that maps "ceiling height" → `ceiling_height_m`. But the PDF extractor uses a DIFFERENT resolution system that maps to generic IDs like `env.generic.spatial_layout` or `env.inferred.design_factor` — these are useless for template matching.

The resolution system is ALSO mapping garbage variables to canonical IDs via fuzzy matching:

```
environment_variable: "instruction"
environment_canonical_id: env.ae.hazard_indicators
environment_resolution_confidence: 0.87     # High confidence in a wrong match!
```

"Instruction" (an experimental protocol step: "Instruction: return hand") was fuzzy-matched to "hazard_indicators" with 87% confidence. The system is confidently wrong.

### Failure 3: The Unstructured 93% Are Citation Fragments, Not Findings

The 159,456 rows without environment/outcome variables are not "unstructured findings waiting for variable extraction." They are discourse fragments — snippets of introduction text, citation markers, and cross-references:

```
claim_type: inter_article_relation
statement: "GramannK(2017)Walkingthrough In recent years..."
source: pdf_discourse_scan
```

These are sentences that MENTION other papers. They don't contain findings. No amount of re-processing will extract IV/DV pairs from "Edelstein and Macagno, 2012, active for shapes with rectilinear features (Nasr et al., 2014)" because this sentence is a CITATION, not a finding.

Some of the discourse rows DO contain potentially useful theory links:

```
claim_type: theory_link
theory_name: ART
statement: "Several neuroarchitectural studies have..."
```

These are legitimately interesting — they map papers to the theories they invoke. But they still don't contain causal triplets.

### Failure 4: The Web of Belief Is Populated from Garbage

The web_persistence.db contains:

- **12,628 beliefs** — these are the CSV rows dumped directly as "beliefs"
- **28,314 constraints** — pairwise links between the beliefs
- **1,555 bridges** — cross-domain links

Sample belief:
```
content: ": Location C; Microphone 1: 52.4 dB(A); Microphone 2: 51.3 dB(A)"
environment_id: env.unresolved.location_microphone_microphone
outcome_id: out.unresolved.location_microphone_microphone
```

This is a noise measurement table from an acoustics paper. It's not a "belief" — it's a data point. The web of belief machinery (entrenchment scoring, coherence computation, constraint satisfaction) is running on this data as if it were epistemically meaningful propositions. It's not.

The 690 coherence_alerts are all "sharp_decline" warnings — every paper integration drops coherence. Of course it does: you can't get coherence from incoherent inputs.

### Failure 5: Two Disconnected Databases

The system has TWO databases that should be one:
- `ae.db` (8.3 MB): has CMR tables (templates, evaluations) BUT its beliefs/constraints tables are EMPTY
- `data/web_persistence.db` (83 MB): has the populated web of belief BUT no CMR tables

The CMR pipeline reads from ae.db. The web of belief lives in web_persistence.db. Sprint 11's Task 11.23 (web of belief integration test) would have discovered this — but the data IN web_persistence.db is garbage anyway, so connecting them would only propagate the problem.

---

## 3. WHAT ACTUALLY EXISTS THAT'S USABLE

Not everything is lost. The pipeline DID capture real information, it just stored it in the wrong fields:

### 3a. The source_quote field is gold (171,840 rows at 100% coverage)

Every row has the original PDF text. For the structured rows, this IS the table content. For the discourse rows, this IS the citation context. The raw material for extraction exists — it's the INTERPRETATION that failed.

### 3b. The paper_id field identifies 386 real papers

We have DOIs for most papers. We know which papers are in the corpus.

### 3c. The article_type_classifier shows some signal

While mostly returning "unknown" (low confidence), it does correctly identify some papers as `empirical_v2`, `case_study`, `thought_piece`. The `thought_piece` label for doi:10.3389/fnhum.2017.00477 is correct — it's a perspective article, not an empirical study.

### 3d. The theory_link claim_type identifies theory invocations

The discourse scanner DID identify when papers invoke ART, SRT, Biophilia, etc. These ~1,361 theory-links (the staging links from earlier sprints) are the ONE class of extracted data that's actually correct.

### 3e. Row 5 proves the format can work

```
environment_variable: "deviation contributors temperature"
outcome_variable: "productivity"
effect_direction: negative
environment_canonical_id: env.generic.thermal
outcome_canonical_id: behav.productivity
outcome_resolution_confidence: 1.0
outcome_resolution_match_type: exact
```

When the table structure is simple enough (a literature review table with clear column headers), the extractor CAN produce real IV→DV pairs. It just needs help identifying WHICH tables have this structure.

---

## 4. THE REMEDIATION ARCHITECTURE

This requires a new extraction pass. Not a patch — a fundamentally different approach to what the extractor DOES.

### Stage 0: Paper Triage (human + classifier)

**Goal:** Of 386 papers, identify the ~100-150 that contain empirical findings relevant to our template system.

**Method:**
1. Pull the title + abstract for all 386 DOIs (many are already in the `articles` table)
2. Classify each as: EMPIRICAL (has experiments/measurements), REVIEW (summarises others' findings), THEORETICAL (proposes frameworks), METHODS (describes tools), OFF-TOPIC (wrong domain)
3. Only EMPIRICAL and REVIEW papers go to Stage 1

**Who does this:** An LLM pass using the paper abstract. David reviews borderline cases. Fast: ~2 hours.

**Output:** `data/production/paper_triage.json` — a list of paper_ids with their classification.

### Stage 1: Table Semantic Classification

**Goal:** For each table in each triaged paper, determine what KIND of table it is.

**Method:** Send the LLM the COMPLETE table (not individual cells) plus: the table caption, the surrounding paragraph, and the paper's abstract. Ask it to classify:

| Table Type | Contains IV→DV? | Action |
|---|---|---|
| RESULTS (ANOVA, regression, t-test) | YES — the IVs and DVs are in the design | Extract |
| LITERATURE_REVIEW (summary of prior work) | YES — each row is a study with IV→DV | Extract |
| DESCRIPTIVE_STATS (means, SDs of sample) | NO — these describe the sample, not effects | Skip |
| MODEL_FIT (χ², RMSEA, CFI) | NO — these assess model quality, not causal links | Skip |
| DEMOGRAPHICS (age, gender, N) | NO — participant characteristics | Skip |
| PROTOCOL (experimental procedure steps) | NO — methodology description | Skip |
| MATERIALS (stimuli descriptions) | MAYBE — if stimuli ARE the IV | Flag for review |

**Key insight:** This classification requires seeing the WHOLE TABLE plus context. pdfplumber gives us the table content (in `source_quote`), and we have `source_table_id` to group rows from the same table. We need to reconstruct each table, then classify it.

**Who does this:** LLM pass (Sonnet is fine) with a structured prompt. ~4-6 hours for all tables.

**Output:** `data/production/table_classifications.json` — each source_table_id mapped to its type.

### Stage 2: Structured Claim Extraction

**Goal:** From RESULTS and LITERATURE_REVIEW tables, extract clean IV→DV claims in the CMR pipeline's controlled vocabulary.

**Method:** For each extractable table, send the LLM:
- The full table content
- The table caption
- The paper abstract
- A VOCABULARY SHEET listing all valid IVs and DVs the system recognises

The vocabulary sheet is built from two sources that ALREADY EXIST in the codebase:

**Valid IVs** (from `FEATURE_TO_TEMPLATE_INPUT` + `_SYNONYMS`):
```
ceiling_height_m, floor_area_m2, illuminance_lux, ambient_noise_dba,
has_nature_view, view_content, primary_material, surface_effusivity,
contact_temperature_c, operative_temp_c, running_mean_outdoor_c,
cct_kelvin, shared_area_ratio, phone_booths_per_worker,
spatial_integration_score, layout_legibility, has_daylight_variation,
natural_material_ratio, visual_privacy_score, acoustic_privacy_stc,
...
```

**Valid DVs** (from template output variables + `_SYNONYM_GROUPS`):
```
creativity, stress, productivity, preference, recovery_time,
pain_medication_use, cognitive_flexibility, attention, mood,
thermal_comfort, acoustic_satisfaction, visual_comfort,
wayfinding_success, social_interaction, privacy_satisfaction,
physiological_arousal, cortisol, heart_rate_variability,
...
```

The prompt says: "Extract each causal claim from this table. Map the independent variable to the closest term from the IV vocabulary. Map the dependent variable to the closest term from the DV vocabulary. If no close match exists, use a descriptive term and flag as NEW_VARIABLE."

**Output per claim:**
```json
{
    "paper_id": "doi:10.20944/preprints201907.0323.v1",
    "source_table_id": "TBL-20260214092258-001",
    "iv": "thermal_deviation",
    "iv_mapped": "operative_temp_c",
    "iv_mapping_confidence": 0.8,
    "dv": "productivity",
    "dv_mapped": "productivity",
    "dv_mapping_confidence": 1.0,
    "direction": "negative",
    "effect_size": null,
    "effect_size_type": null,
    "sample_n": null,
    "context": "office",
    "source_quote": "Deviation Contributors: Temperature...",
    "extraction_confidence": 0.85
}
```

**Who does this:** LLM pass with structured JSON output. This is the expensive step — needs careful prompting. ~8-12 hours for all extractable tables.

**Output:** `data/production/structured_claims.json` — clean, vocabulary-aligned claims.

### Stage 3: Effect Size Recovery

**Goal:** For claims that have statistical results in the table but where the extractor didn't capture effect sizes, go back and extract them.

Many results tables contain: F-values, t-values, p-values, η², R², β, r. These can be converted to Cohen's d equivalents.

**Method:** For each claim from Stage 2 that lacks an effect_size, check whether the source table contains statistical values. If so, extract and convert.

**Conversion formulas** (well-established):
- t → d: `d = 2t / √(df)`
- F (1 df_num) → d: `d = 2√(F / df_error)`
- r → d: `d = 2r / √(1 - r²)`
- η² → d: `d = 2√(η² / (1 - η²))`

**Who does this:** Code, not LLM. Deterministic conversion once the statistical values are identified.

**Output:** Updated structured_claims.json with effect_size and effect_size_type fields populated.

### Stage 4: Web of Belief Rebuild

**Goal:** Replace the garbage web with a clean one built from Stage 2-3 outputs.

**Method:**
1. Back up current web_persistence.db (it's already backed up at `data/production/rebuild_backup_20260213_193206/`)
2. Create a new web with ONLY the Stage 2-3 structured claims as beliefs
3. Each belief has: clean content, proper environment_id (from IV vocabulary), proper outcome_id (from DV vocabulary), effect_size, credence based on study quality
4. Constraints are generated from: same-paper claims (intra-paper coherence), cross-paper claims about the same IV→DV (replication), and template-level connections (if two claims map to the same template, they're constrained)

**Expected outcome:**
- ~1,000-5,000 real beliefs (vs 12,628 garbage ones)
- ~2,000-10,000 real constraints (vs 28,314 garbage ones)
- Coherence score that MEANS something
- Every belief traceable to a specific table in a specific paper

### Stage 5: CMR Pipeline Integration

**Goal:** Feed the clean structured claims into the existing CMR paper evaluation pipeline.

The pipeline ALREADY works with clean claims (Sprint 11 proved this with hand-crafted Ulrich 1984 claims). The problem has always been getting clean claims IN.

**Method:**
1. The `process_paper()` function already accepts `claims: list[dict]` with `iv`, `dv`, `direction`, `effect_size`, `sample_n`
2. Stage 2-3 outputs are already in this format
3. Run each paper's claims through process_paper()
4. Collect: template matches, contradictions, confirmations, gaps, VOI scores, update proposals

**Expected outcome:** The system finally does what it was designed to do — evaluate papers against the template corpus and learn from them.

---

## 5. IMPLEMENTATION PLAN

### Who Does What

| Stage | Agent | Time Est. | Input | Output |
|---|---|---|---|---|
| **0: Paper Triage** | CC | 2-3 hrs | 386 DOIs + abstracts | paper_triage.json |
| **1: Table Classification** | CC | 4-6 hrs | Grouped table rows + contexts | table_classifications.json |
| **2: Claim Extraction** | CC + Codex | 8-12 hrs | Classified tables + vocab sheet | structured_claims.json |
| **3: Effect Size Recovery** | Codex | 2-3 hrs | Claims + source tables | Updated structured_claims.json |
| **4: Web Rebuild** | Codex | 3-4 hrs | Clean claims | New web_persistence.db |
| **5: Pipeline Integration** | CC | 2-3 hrs | Clean claims | Paper eval results |

**Total estimated effort: 21-31 hours across 2-3 agents**

### What Gets Built

**New files:**
- `src/extraction/paper_triage.py` — classify papers by type
- `src/extraction/table_classifier.py` — classify tables by semantic type
- `src/extraction/claim_extractor.py` — extract structured claims with vocabulary alignment
- `src/extraction/effect_size_converter.py` — convert stats to Cohen's d
- `src/extraction/vocabulary_sheet.py` — generate the IV/DV vocabulary from existing code
- `src/extraction/web_rebuilder.py` — rebuild web of belief from clean claims
- `data/production/paper_triage.json`
- `data/production/table_classifications.json`
- `data/production/structured_claims.json`

**Modified files:**
- Web of belief population logic (point at new claims, not raw CSV)
- CMR paper_eval to accept claims from the new extraction pipeline

### Dependency on Sprint 11-13

This work is INDEPENDENT of Sprints 11-13. It addresses the DATA QUALITY problem, while those sprints address the PIPELINE ENGINEERING problem. Both are necessary. The pipeline needs clean data to produce real results. The data needs the pipeline to be evaluated.

**Recommended sequencing:**
1. Sprints 11-13 continue as planned (pipeline engineering)
2. This remediation runs IN PARALLEL as "Sprint D" (D for Data)
3. When both complete, run the structured claims through the fixed pipeline
4. THAT produces the first real system-level results

---

## 6. THE VOCABULARY BRIDGE

The single most important artifact is the **vocabulary sheet** — the controlled list of IVs and DVs the system recognises. This already exists scattered across the codebase:

**Source 1: `FEATURE_TO_TEMPLATE_INPUT` in feature_mapping.py** (the building eval vocabulary)
```python
"VF3":  {"ceiling_height_m", "floor_area_m2"}
"L1":   {"cv_luminance"}
"L2":   {"illuminance_lux", "daylight_exposure_hours", "time_of_day"}
"CREA2": {"ambient_noise_dba", "illuminance_lux", "baseline_creativity"}
"MAT1": {"surface_effusivity", "contact_temperature_c", "climate_context"}
"SOC2": {"shared_area_ratio", "phone_booths_per_worker", ...}
"VIEW1": {"view_content", "view_layers", "view_sky_fraction", "has_nature_view"}
...
```

**Source 2: `_SYNONYMS` in claim_extraction.py** (the natural language → canonical mapping)
```python
"nature views" → "has_nature_view"
"ceiling height" → "ceiling_height_m"
"noise" → "ambient_noise_dba"
"stress" → "stress"
"recovery time" → "recovery_time"
```

**Source 3: `_SYNONYM_GROUPS` in template_matching.py** (the fuzzy matching groups)
```python
{"daylight", "illuminance", "light_level", "lux"}
{"noise", "ambient_noise", "ambient_noise_dba"}
{"nature_view", "has_nature_view", "view_quality", "green_view"}
```

The remediation's first concrete task is to CONSOLIDATE these three sources into a single authoritative vocabulary file:

```json
{
    "independent_variables": {
        "ceiling_height_m": {
            "canonical": "ceiling_height_m",
            "synonyms": ["ceiling height", "room height", "floor-to-ceiling height"],
            "unit": "meters",
            "templates": ["VF3", "CREA2"],
            "domain": "A6_Visual_Form"
        },
        "illuminance_lux": {
            "canonical": "illuminance_lux",
            "synonyms": ["daylight", "illuminance", "light level", "lux", "lighting"],
            "unit": "lux",
            "templates": ["L1", "L2", "L3", "CREA2"],
            "domain": "A4_Light"
        },
        ...
    },
    "dependent_variables": {
        "creativity": {
            "canonical": "creativity",
            "synonyms": ["creative thinking", "creative output", "divergent thinking", "RAT score"],
            "measurement_types": ["RAT", "AUT", "self-report"],
            "templates": ["CREA1", "CREA2", "CREA3", "CREA4"]
        },
        "stress": {
            "canonical": "stress",
            "synonyms": ["stress reduction", "cortisol", "anxiety", "physiological arousal"],
            "measurement_types": ["cortisol", "PSS", "STAI", "HRV"],
            "templates": ["VIEW1", "T6-gap", "T7-gap"]
        },
        ...
    },
    "new_variable_flag": "NEW_VARIABLE"
}
```

This vocabulary sheet serves THREE purposes:
1. It's the reference for the LLM extraction prompt (Stage 2)
2. It's the authoritative mapping for variable resolution
3. It documents what the system CAN and CANNOT assess

---

## 7. WHAT THIS MEANS FOR THE WEB OF BELIEF

The current web of belief (12,628 beliefs, 28,314 constraints, 1,555 bridges) needs to be understood for what it IS vs what it SHOULD BE.

**What it IS:** A persistence layer that stores whatever the PDF extractor produces. The ingestion code (`paper_integrations`: 3,300 entries) treats every CSV row as a potential belief and creates constraints between beliefs from the same paper. The entrenchment/coherence machinery runs on these, producing numbers that look real but aren't.

**What it SHOULD BE:** A curated knowledge base where each belief is a PROPOSITIONAL CLAIM with: a clear subject (IV), a clear predicate (effect direction + magnitude), a clear object (DV), a source (paper + table), and a confidence (based on study quality, replication status, effect size).

**The rebuild** doesn't just swap out data — it changes the SEMANTICS of what a belief means. Currently: "a row existed in a PDF table." After rebuild: "a study found that X affects Y with effect size d in context Z."

This is the difference between a database and a knowledge base.

---

## 8. COST OF NOT FIXING THIS

If we proceed with Sprints 12-13 without fixing the data:
- The Tier 2 reductions (Sprint 12, Tasks 12.1-12.3) will be correct in THEORY but have nothing to reduce FROM — the staging links point to garbage beliefs
- The evidence accumulation engine (Sprint 13, Task 13.3) will accumulate garbage evidence
- The paper processing pipeline (Sprint 13, Task 13.13) will process papers that were already (badly) processed, with no way to reconcile the old garbage with new clean extractions
- The web of belief ↔ template bridge (Sprint 12, Task 12.18) will connect templates to noise

The pipeline will work on synthetic test cases (hand-crafted Ulrich 1984 claims) but fail on every real paper in the corpus.

---

## 9. DECISION REQUIRED FROM DAVID

Three options:

**Option A: Fix Data First, Then Finish Pipeline**
Pause Sprints 12-13. Run Sprint D (data remediation). Then resume 12-13 with clean data. Risk: delays pipeline completion by 2-3 weeks.

**Option B: Run in Parallel (Recommended)**
Sprints 11-13 continue on pipeline engineering using synthetic test cases. Sprint D runs simultaneously on data remediation. When both finish, connect them. Risk: some Sprint 12-13 tasks may need minor rework when real data arrives.

**Option C: Minimal Data Fix**
Instead of reprocessing all 386 papers, hand-curate claims for the 10-20 papers most relevant to our templates (the papers the panel documents already cite). Get a small but PERFECT dataset. Use that for system validation. Defer full corpus reprocessing. Risk: system validated but not yet operational at scale.

My recommendation is **Option B with elements of C**: continue the sprints, but immediately hand-curate 15-20 "gold standard" papers as validation data. Then run the full automated reprocessing pipeline once it's built and tested against the gold standard.

---

*Document 70 — PDF Data Pipeline Diagnosis and Remediation Architecture*
*February 17, 2026*
