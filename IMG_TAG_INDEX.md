# IMG-TAG Image Tagging Vocabulary - File Index

**Project**: Article_Eater_PostQuinean_v1  
**Date**: March 2, 2026  
**Status**: Complete, all 42 tests passing

---

## Quick Navigation

### Start Here
- **Quick Start Guide**: `/docs/IMG_TAG_QUICK_START.md` (15 KB)
  - 5-minute setup
  - All 41 attributes explained with examples
  - Common tagging patterns
  - Troubleshooting

### Full Documentation
- **Implementation Summary**: `/docs/IMG_TAG_IMPLEMENTATION_SUMMARY.md` (20 KB)
  - Complete technical reference
  - Vocabulary structure and scientific grounding
  - Service capabilities and usage
  - Future extensions

### Code & Data

#### Data Models
1. **Vocabulary Definition**: `/data/attributes/image_tagging_vocabulary.json` (45 KB)
   - 41 attributes across 7 domains
   - Measurement types, value ranges, theoretical grounding
   - Domain summary score specifications
   - Links to T1 theories and T2 templates

2. **Validation Schema**: `/data/attributes/image_tagging_schema.json` (15 KB)
   - JSON Schema Draft 7
   - Validates tag record structure
   - Inter-rater reliability tracking
   - Consistency rules

#### Service Implementation
3. **ImageTagService**: `/src/services/image_tag_service.py` (24 KB, 635 lines)
   - `tag_image()` - Create tag records
   - `validate_tags()` - Check structure and values
   - `get_domain_scores()` - Compute 5 summary scores
   - `get_relevant_templates()` - Link to T2 templates
   - `search_by_attribute()` - Find images by attribute
   - Full error handling and validation

#### Tests
4. **Test Suite**: `/tests/test_image_tag_service.py` (26 KB, 686 lines)
   - 42 comprehensive tests
   - 11 test classes
   - 100% pass rate
   - <1 second runtime

---

## Vocabulary at a Glance

### 7 Domains, 41 Attributes

| Domain | Attributes | Type |
|--------|-----------|------|
| **Spatial Properties** | volume, enclosure, prospect, mystery, legibility | 5 |
| **Lighting** | source, illuminance, color-temp, uniformity, shadow | 5 |
| **Materials & Texture** | types, naturalness, finish, complexity | 4 |
| **Vegetation** | presence, types, density, health, arrangement | 5 |
| **Color** | hues, saturation, contrast, warm-cool, naturalness | 5 |
| **Visual Complexity** | visual, clutter, information, pattern | 4 |
| **View & Space** | depth-cues, layering, focal-point, balance, flow | 5 |
| **Environmental Context** | built-natural, setting, scale, accessibility, activity | 5 |
| | **TOTAL** | **41** |

### 5 Domain Summary Scores

1. **Naturalness** - Natural vs. artificial character
2. **Visual Complexity** - Detail richness and information density
3. **Prospect-Refuge Index** - Balance of openness to enclosure
4. **Restorative Capacity** - Stress reduction potential
5. **Human-Centeredness** - Comfort and accessibility

---

## Getting Started

### Installation
```python
from src.services.image_tag_service import ImageTagService

service = ImageTagService()  # Auto-locates vocabulary and schema
```

### Basic Usage
```python
tags = {
    "spatial-properties": {
        "spatial-volume": {"value": 75},
        "spatial-enclosure-degree": {"value": "semi-enclosed (partial barriers, >180° view)"},
    },
    "vegetation": {
        "vegetation-presence": {"value": "abundant (major vegetation component, 25-50%)"},
    },
}

record = service.tag_image(
    image_id="img-001",
    tags=tags,
    tagged_by="rater-A",
    source_paper_id="10.1234/example"
)

# Access results
print(f"Naturalness: {record['domain_scores']['naturalness']['score']}")
print(f"Templates: {[t['template_id'] for t in record['relevant_templates']]}")
```

### Validation
```python
errors = service.validate_tags(tags)
if errors:
    print(f"Validation errors: {errors}")

is_valid, schema_errors = service.validate_tag_record(record)
```

---

## Test Coverage

### 42 Tests in 11 Classes
- Service initialization (6 tests)
- Tag creation (3 tests)
- Tag validation (8 tests)
- Domain scoring (7 tests)
- Template linking (3 tests)
- Attribute lookup (4 tests)
- Vocabulary queries (2 tests)
- Schema validation (2 tests)
- Batch operations (1 test)
- Integration workflows (2 tests)
- Edge cases (4 tests)

**Run tests**:
```bash
python -m pytest tests/test_image_tag_service.py -v
```

---

## Scientific Foundation

### Primary References
- Appleton, J. (1975) - Prospect-Refuge Theory
- Kaplan & Kaplan (1989) - Landscape Preference Models
- Ulrich, R. S. (1983) - Stress Reduction Theory
- Berlyne, D. E. (1971) - Hedonic Tone & Complexity
- Gibson, J. J. (1979) - Ecological Optics

### T1 Theory Integration
- ART: Attention Restoration Theory
- PRT: Prospect-Refuge Theory
- SRT: Stress Reduction Theory
- BH: Biophilia Hypothesis
- LPM: Landscape Preference Models
- CRT: Circadian Rhythm Theory

### T2 Template Links
- AX1, AX3–AX6: Spatial and affective templates
- CB2: Computational and behavioral
- COL1–COL2: Color and aesthetics
- CREA1–CREA4: Creativity and cognition

---

## Key Features

### Measurement Types
- **Continuous**: Numeric ranges (0–100, lux, Kelvin, %)
- **Categorical**: Discrete classes (non-exclusive possible)
- **Ordinal**: Ranked levels (converted to numeric for scoring)

### Validation
- Domain and attribute structure validation
- Value range and type checking
- 7 consistency rules enforced
- JSON Schema compliance

### Scoring
- Weighted domain summary scores
- Completeness tracking (% of attributes tagged)
- Contributing attribute records
- Missing attributes identified

### Template Linking
- Attributes mapped to relevant T2 templates
- Relevance scores (0–1)
- Ranked by importance
- Limited to top 10 most relevant

---

## Naming Conventions

All identifiers follow ATLAS project standards:

- **Hyphenated**: `spatial-volume`, `vegetation-presence`
- **Lowercase**: No mixed case
- **Descriptive**: Full terms, no abbreviations
- **Consistent**: Matching scientific literature

Example IDs:
- Attributes: `spatial-volume`, `lighting-illuminance`, `vegetation-density`
- Domains: `spatial-properties`, `lighting`, `vegetation`, `environmental-context`
- Templates: AX1, AX3, COL1, CREA1, CB2

---

## File Locations

```
Article_Eater_PostQuinean_v1/
├── data/attributes/
│   ├── image_tagging_vocabulary.json    ← Master vocabulary
│   └── image_tagging_schema.json         ← Validation schema
├── src/services/
│   └── image_tag_service.py              ← Service implementation
├── tests/
│   └── test_image_tag_service.py         ← 42 tests
├── docs/
│   ├── IMG_TAG_IMPLEMENTATION_SUMMARY.md ← Technical reference
│   └── IMG_TAG_QUICK_START.md            ← Quick start guide
└── IMG_TAG_INDEX.md                      ← This file
```

---

## Troubleshooting

**File Not Found**
- Ensure you're in the project root directory
- Check that files are in `data/attributes/`, `src/services/`, `tests/`

**Validation Errors**
- Verify ordinal values use full descriptive text
- Check continuous values are in specified range
- Review consistency rules

**Service Issues**
- Run tests to verify installation: `pytest tests/test_image_tag_service.py`
- Check that both vocabulary and schema files load
- Verify Python 3.8+ and required dependencies

---

## Next Steps

1. **Read Quick Start**: `/docs/IMG_TAG_QUICK_START.md`
2. **Review Full Docs**: `/docs/IMG_TAG_IMPLEMENTATION_SUMMARY.md`
3. **Tag Your Images**: Use the service to create records
4. **Run Tests**: Verify everything works locally
5. **Batch Process**: Scale to multiple images

---

## Contact

**Created**: March 2, 2026  
**For**: Professor David Kirsh, UCSD Cognitive Science  
**Project**: ATLAS (Article Tagging via Learning and Selection) - Post-Quinean

This implementation supports evidence extraction from environmental psychology papers by providing structured, theory-grounded visual attribute vocabulary for image characterization.
