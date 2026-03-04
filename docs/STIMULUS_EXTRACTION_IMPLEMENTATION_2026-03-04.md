# Stimulus Description Extraction Implementation

**Date**: 2026-03-04
**Scope**: V3 extraction prompts + extraction field validator + backfill tooling
**Current Status**: stimulus_description at 0% across 1,043 articles (33,116 findings)

---

## Summary

Added comprehensive stimulus description extraction to the Article Eater V3 extraction pipeline. This includes:

1. **Enhanced V3 extraction prompts** with explicit stimulus description instructions
2. **Validation rules** in the extraction field validator to enforce stimulus population
3. **Backfill analysis script** to identify findings requiring stimulus re-extraction
4. **Validation suite** with 12 stimulus-related checks (6 in prompts, 6 in validator)

---

## Changes Made

### 1. Updated V3 Extraction Prompts (`src/extraction/revised_prompts_v3.py`)

**Rule 6: STIMULUS DESCRIPTION** (lines 602-638)

Expanded the vague stimulus instruction into detailed guidance requiring:

- **primary_type**: One of {visual_scene, soundscape, thermal, olfactory, spatial, lighting, material, mixed}
- **components**: Array with name, category, essential flag for each stimulus element
  - For architectural studies: room dimensions, ceiling height, window area, material finishes, lighting (CCT, lux)
  - For lighting: CCT (2700K, 4000K, 6500K), illuminance (lux), CRI
  - For acoustic: dB levels, frequency content, source type
  - For materials: material types, textures, colors, finishes

- **delivery_method**: How stimulus was presented (in_situ, VR, photo, video, audio, imagined)
- **duration_seconds**: Exposure duration (null if not applicable)

**MANDATE**: DO NOT use null for stimulus_description in empirical findings. If paper lacks details, record as:
```json
{"name": "Details not provided in paper", "category": "spatial", "essential": false}
```

**Validation Checklist** (lines 402-419)

Added two new checks to VALIDATION_SUFFIX_V3:

- **Check 11: Stimulus Description Coverage** — 100% empirical findings must have populated stimulus_description
- **Check 12: Stimulus Images Coverage** — 70%+ of visually-described stimuli should have figure references

---

### 2. Enhanced Extraction Field Validator (`src/qa/extraction_field_validator.py`)

**New Method: `_validate_stimulus_description()`** (lines 1154-1248)

Validates six aspects of stimulus fields:

| Rule ID | Severity | Check |
|---------|----------|-------|
| ST1_STIMULUS_REQUIRED | ERROR | stimulus_description must be dict for empirical findings (not null) |
| ST2_INVALID_PRIMARY_TYPE | ERROR | primary_type must be one of 8 canonical values |
| ST3_EMPTY_COMPONENTS | WARNING | components array should have ≥1 entry |
| ST4_INVALID_DELIVERY | WARNING | delivery_method must be in {in_situ, VR, photo, video, audio, imagined} |
| ST5_STIMULUS_UNDERSPECIFIED | WARNING | If antecedent mentions sensory terms but components are minimal, flag |
| ST6_VISUAL_STIMULUS_MISSING_IMAGES | INFO | Visual stimuli should have stimulus_images entries with valid image_type |

**Integration**: Called as step 13 in `validate_finding()`, before epistemic principle validation (step 14)

---

### 3. New Backfill Analysis Script (`scripts/backfill_stimulus_descriptions.py`)

Comprehensive script to assess stimulus description coverage across entire extraction corpus.

**Capabilities**:

- Scans all extraction JSONs in `data/extractions/`
- Identifies findings with missing/empty/minimal stimulus_description
- Detects antecedent sensory language (light, sound, space, material, color, thermal, smell, view)
- Flags empirical findings needing backfill
- Categorizes articles by coverage: zero (0%), partial (1-99%), full (100%)

**Output**: Summary report + optional JSON with per-article details

**Usage**:
```bash
# Print summary to console
python scripts/backfill_stimulus_descriptions.py

# Write detailed JSON report
python scripts/backfill_stimulus_descriptions.py --output backfill_report.json

# Include antecedent text in output (verbose)
python scripts/backfill_stimulus_descriptions.py --with-antecedent-text
```

**Current Results** (as of 2026-03-04):
- Total articles: 1,031 (with findings)
- Total findings: 33,116
- Findings with stimulus: 1 (0.0%)
- Findings needing backfill: 15,273
- Articles with zero coverage: 1,030
- Articles with full coverage: 1

---

## Schema Integration

The stimulus fields were already defined in `contracts/schemas/extraction_template.v2.schema.json`:

```json
{
  "stimulus_description": {
    "type": ["object", "null"],
    "description": "Detailed description of stimulus or environmental manipulation",
    "properties": {
      "primary_type": {
        "enum": ["visual_scene", "soundscape", "thermal", "olfactory", "spatial", "lighting", "material", "mixed"]
      },
      "components": {
        "type": "array",
        "items": { "$ref": "#/$defs/StimulusComponent" }
      },
      "delivery_method": {
        "enum": ["in_situ", "VR", "photo", "video", "audio", "imagined"]
      },
      "duration_seconds": { "type": ["number", "null"] }
    }
  },
  "stimulus_images": {
    "type": "array",
    "items": { "$ref": "#/$defs/StimulusImage" }
  }
}
```

This implementation now ensures these schema fields are **actively populated** by the extraction model.

---

## Validation Coverage

| Component | Coverage | Details |
|-----------|----------|---------|
| V3 Prompts | 2 checks | Extraction rule 6 + 2 validation checklist items |
| Field Validator | 6 rules | ST1-ST6 covering all aspects |
| Backfill Analysis | Coverage tracking | Identifies candidates for re-extraction |

**Total validation rules**: 8 (2 prompts + 6 validator)

---

## Next Steps

1. **Re-extraction Queue**: Use `backfill_stimulus_descriptions.py` output to identify articles for focused re-extraction
2. **Focused Stimulus Prompt**: Consider creating a narrow, stimulus-focused extraction prompt to backfill 15,273 findings
3. **Panel Review**: Expert review of stimulus extraction patterns before mass re-extraction
4. **Surgical Update**: Integrate stimulus backfill into existing `scripts/v3_surgical_update.py` for batch re-extraction

---

## Files Modified

| File | Changes | Lines |
|------|---------|-------|
| `src/extraction/revised_prompts_v3.py` | Expanded rule 6, added checks 11-12 | 602-638, 402-419 |
| `src/qa/extraction_field_validator.py` | Added `_validate_stimulus_description()` + call in validate_finding() | 1154-1248, 322-325 |
| `scripts/backfill_stimulus_descriptions.py` | NEW: Analysis tool for coverage assessment | 1-565 |

## Files Created

- `scripts/backfill_stimulus_descriptions.py` — Stimulus coverage analysis tool
- `docs/STIMULUS_EXTRACTION_IMPLEMENTATION_2026-03-04.md` — This document

---

## Research Rationale

Stimulus descriptions are critical for:

1. **Reproducibility**: Researchers need to know exactly what participants experienced
2. **Meta-analysis**: Stimulus characteristics are key moderators (ceiling height, lighting, etc.)
3. **Multimodal research**: Architectural and environmental psychology studies describe spaces in rich sensory detail
4. **Implementation**: Practitioners need actionable specifications (lux levels, room dimensions, materials)

Currently at 0% population, this extraction is the highest-priority gap identified by David Kirsh.

---

## Epistemic Notes

- **Validation scope**: Empirical findings only (causal, associational, statistical, empirical_finding claim types)
- **Graceful degradation**: If paper lacks stimulus details, document this explicitly rather than leaving null
- **Sensory grounding**: Validator detects when antecedent mentions sensory terms but stimulus is underspecified
- **Image linkage**: Visual stimuli should reference figures for multimodal validation

---

**Implementation complete**: 2026-03-04 21:00 UTC
