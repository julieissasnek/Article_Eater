# Pipeline Repair Integration Guide — V2.0

**Date:** 2026-02-24  
**Author:** Opus (Architecture)  
**Sprint:** Pipeline Repair (consolidated after full template library review)

---

## Deliverables

| File | Lines | What it does |
|------|-------|-------------|
| `src/extraction/revised_prompts_v2.py` | ~490 | All extraction prompts. 166-template matching guide, 15 article sub-types in 5 families, provenance depth, graceful degradation, negative examples, terminology bridge. Drop-in `PROMPT_MAP` replacement. |
| `src/extraction/pipeline_repairs.py` | ~1135 | Classification v2 (intro+conclusion pages, ~60% cheaper), quality v2 (4-tier routing), partial extraction repair, normalization, image bug fix, `patch_pipeline()` helper. |

**Supersedes** the earlier V1.0 `revised_prompts.py` and V1.1 addendum. Those files are no longer needed.

---

## Quick Start

```python
from src.extraction.pdf_extraction_module import ExtractionPipeline
from src.extraction.pipeline_repairs import patch_pipeline

pipeline = ExtractionPipeline(
    pdf_dir="/path/to/pdfs",
    output_dir="data/extraction_pipeline"
)

patch_pipeline(pipeline)  # Replaces PROMPT_MAP, classification, quality eval, image extraction

pipeline.process_batch(batch_size=10)  # Start small to validate
```

---

## What's in V2.0

### 1. Template Matching Guide (166 templates)

Based on the full template library you uploaded (208 files, 166 unique IDs). Organized by framework with per-cluster listing:

| Framework | Templates | Key clusters |
|-----------|-----------|-------------|
| PP | 58 | Core visual (T1/T2/T22), active inference (T21/PP4), visual form (VF1-3), color (COL1-2), implicit-explicit (T_IE_001–012), BRECVEMA, dose-response (AX2/7/9/12) |
| SN | 13 | Space syntax (SC1/SC2), memory (SN1/SN2/SCM2), social-spatial (SC4/XSAD1), navigation modes (T43) |
| DP | 3 | T9, DP2, CROSS_PROACTIVE_REACTIVE |
| DT | 15 | Restoration (T4/T16/T27), creativity (CREA1-3), attention (DT1/DT2/AX10), individual differences (AX8) |
| NM | 18 | Stress (NM8/T6/AX4), reward (NM1/NM2/NM4), arousal (NM5/NM6), social (NOS3/NVR1), allostatic (T29/NSIA1) |
| IC | 15 | Core (T12/IC2/T7), thermal, olfactory, social (CSMP1/CSAR1/PGR1), acoustic emotion |
| MS | 15 | Encoding (EHE1/EPEP1/ESE1), consolidation (MCR1/MRR2), WM (T36/MS2), boundaries (TEB1) |
| EC | 8 | Core (T8/T18/T28), touch (HSM1/CAT1), sensorimotor (EC2/TP1) |
| CB | 10 | Circadian (T30/L2), lighting detail (L3/L4/L5), sleep (CSA2) |
| MSI | 11 | Congruence (MCP1/CC1), materials (NMC1/MII1/MATD1/MCC1), audio (AUD_*) |

### 2. Article Type Taxonomy (15 sub-types, 5 families)

Aligned with `article_type_contract.py`:

| Family | Sub-types | Required fields |
|--------|-----------|----------------|
| Empirical | empirical_v2, observational_field, case_study, mixed_methods | research_question, design_type, participants, stimuli_or_exposures, measures, findings, limitations |
| Synthesis | meta_analysis, systematic_review, narrative_review | review_question, inclusion_exclusion_criteria, evidence_base_summary, synthesis_conclusions, evidence_gaps |
| Theoretical | theoretical, conceptual_framework, thought_piece | central_proposition, concept_definitions, argument_structure, mechanism_or_causal_logic, testable_hypotheses_or_predictions |
| Qualitative | interview_study, ethnographic, grounded_theory, phenomenological | research_focus, sample_context, data_collection_method, coding_or_analysis_approach, themes_or_constructs, supporting_quotes_or_evidence_snippets, transferability_limits |
| Methods | methods | (components, psychometric_properties, recommended_use) |

The PROMPT_MAP has entries for ALL 15 sub-types plus legacy names. The classification prompt now returns both `article_type` (specific) and `article_family` (for threshold lookup).

### 3. Provenance Depth

Every finding now carries a `provenance_depth` field:
- `abstract` — from abstract only (least reliable)
- `caption` — from figure/table captions
- `table` — from table body (most reliable for statistics)
- `section` — from section body text
- `fulltext_multi` — corroborated across multiple sections (highest confidence)

### 4. Graceful Degradation (unchanged from V1.0)

10 rules for extracting findings with incomplete statistics. Key principle: partial > nothing. A finding with antecedent + consequent + direction but no p-value is still extracted.

### 5. Negative Examples (unchanged from V1.0)

Explicit list of what NOT to extract: other papers' results, untested hypotheses, demographics, manipulation checks.

### 6. Domain Terminology Bridge (expanded from V1.0)

20 common terms mapped (added "soundscape", "prospect-refuge", "complexity" mappings).

---

## Pipeline Repairs (pipeline_repairs.py)

### Classification v2
- Uses intro + conclusion pages only (saves ~60% API cost)
- Returns 15 sub-types + family + confidence + signals
- Stores `item.article_type_sub` for fine-grained prompt selection

### Quality Evaluation v2
- Family-based thresholds (empirical/synthesis_meta/synthesis_other/theoretical/qualitative/methods)
- 4-tier routing: accept → repair → requeue → fail
- Partial credit scoring with `FIELD_WEIGHTS_V2` (includes template_ids, test_statistic)

### Partial Extraction Repair
- Saves partial extractions to `partial_extractions/`
- Two targeted repair prompts: statistics repair + specificity repair
- Re-evaluates after repair; accepts-with-low-confidence after max retries

### Normalization
- `pooled_effects` → `findings`, `themes` → `findings`, `propositions` → `findings`
- Ensures all canonical fields present with null defaults
- Maps qualitative `theme_name` → `antecedent`

### Image Extraction Bug Fix
- `page.get_images()` moved inside the page loop (was outside)

---

## Testing Plan

### Phase 1: Import Check (2 min)
```python
from src.extraction.revised_prompts_v2 import PROMPT_MAP, FAMILY_MAP, CLASSIFICATION_PROMPT
assert len(PROMPT_MAP) == 17  # 15 sub-types + 'empirical' + 'qualitative' legacy
assert "empirical_v2" in PROMPT_MAP
assert "interview_study" in PROMPT_MAP
assert FAMILY_MAP["conceptual_framework"] == "theoretical"
```

### Phase 2: Normalization (5 min)
```python
from src.extraction.pipeline_repairs import normalize_extraction

# Meta-analysis with pooled_effects key
data = {"pooled_effects": [{"id": 1, "antecedent": "nature", "consequent": "stress"}]}
result = normalize_extraction(data)
assert "findings" in result and len(result["findings"]) == 1

# Qualitative with themes key
data = {"themes": [{"theme_name": "daylight", "description": "valued natural light"}]}
result = normalize_extraction(data)
assert result["findings"][0]["antecedent"] == "daylight"
```

### Phase 3: Single Paper (30 min)
```python
pipeline = ExtractionPipeline(...)
patch_pipeline(pipeline)
item = pipeline.add_to_queue("10.xxxx/known_doi", "/path/to/pdf")
result = pipeline.process_one(item)
print(json.dumps(item.quality_report, indent=2))
```

### Phase 4: Batch Comparison (2 hours)
Run 20 papers through original + patched pipeline. Compare acceptance rate, findings count, theory_links population, template_ids population, cost.

---

## Task Distribution

| Agent | Task | Priority |
|-------|------|----------|
| **AG (Antigravity)** | Test revised prompts against Gemini API with 5 papers (1 per family). Report findings count, template_ids accuracy, provenance_depth coverage. Use the improved panel prompt from `02-24_01_Extraction_Pipeline_Audit_and_Improved_AG_Prompt.md`. | P1 |
| **CC (Claude Code)** | Integrate `pipeline_repairs.py` into main module (replace monkey-patching). Add unit tests for `normalize_extraction()` and `evaluate_quality_v2()`. Update `ExtractionResult` dataclass to include `template_ids`, `test_statistic`, `provenance_depth`. | P2 |
| **Codex** | Verify schema consistency: `revised_prompts_v2.py` JSON schemas ↔ `ExtractionResult`/`Finding` dataclasses ↔ `article_type_contract.py` field contracts. Flag any mismatches. Update `template_id_aliases.json` if needed (currently 51 entries; should be 166). | P2 |

---

## Files to Remove (superseded)

- `src/extraction/revised_prompts.py` (V1.0 — replaced by `revised_prompts_v2.py`)
- `src/extraction/revised_prompts_v1_1.py` (V1.1 addendum — merged into V2.0)
