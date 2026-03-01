# Stimulus Description Extraction Summary

**Date Generated**: 2026-02-28
**Script**: `extract_stimulus_descriptions.py`
**Output File**: `stimulus_descriptions_from_articles.json` (22 MB)

---

## Overview

Extracted and categorized 23,029 unique environmental stimulus descriptions from 1,043 scientific article extraction files (32,819 findings processed). These describe physical and environmental conditions used as stimuli in empirical research on human responses to built environments.

---

## Extraction Statistics

| Metric | Value |
|--------|-------|
| Files processed | 1,043 |
| Processing errors | 4 |
| Total findings parsed | 32,819 |
| Unique stimuli identified | 23,029 |
| Categories created | 13 |
| Output file size | 22 MB |

---

## Stimulus Categories & Distribution

| Category | Count | Percentage | Description |
|----------|-------|-----------|-------------|
| Other | 8,710 | 28.6% | Environmental stimuli not matching specific categories |
| Lighting | 3,527 | 11.6% | Natural and artificial lighting conditions, daylighting |
| Art/Decoration | 2,923 | 9.6% | Artistic elements, decorations, aesthetic qualities |
| Sound/Acoustic | 2,712 | 8.9% | Acoustic conditions, noise, soundscapes |
| Color/Material | 2,529 | 8.3% | Colors, materials, textures, surface finishes |
| Nature | 2,296 | 7.5% | Outdoor environments, landscapes, natural elements |
| Outdoor Environment | 1,475 | 4.8% | Outdoor spaces, gardens, plazas, streets |
| Building Type | 1,429 | 4.7% | Hospital, office, school, residential, commercial |
| Spatial Configuration | 1,320 | 4.3% | Room layout, open vs. enclosed, spatial density |
| Thermal | 1,066 | 3.5% | Temperature, ventilation, humidity, thermal comfort |
| Plants/Greenery | 1,150 | 3.8% | Indoor plants, green walls, biophilic design |
| Views | 657 | 2.2% | Window views and visual connections to nature |
| Furniture/Interior | 625 | 2.1% | Furniture, interior design, spatial furnishings |

---

## Most Frequently Referenced Stimuli (Top 20)

These are stimulus descriptions appearing across multiple source articles:

1. **Gender** (19 sources) – Demographic factor
2. **Biophilic design** (17 sources) – Nature-inspired design approaches
3. **Natural light** (17 sources) – Daylight exposure
4. **Noise** (12 sources) – Sound/acoustic environment
5. **Daylight** (11 sources) – Natural lighting
6. **Indoor plants** (10 sources) – Greenery in interior spaces
7. **Red light** (7 sources) – Specific wavelength lighting
8. **Acoustic environment** (7 sources) – Overall acoustic conditions
9. **Soundscapes** (7 sources) – Complex sound environments
10. **Light** (7 sources) – General lighting
11. **Illuminance** (7 sources) – Brightness measurement
12. **Light therapy** (7 sources) – Therapeutic use of light
13. **Daylighting** (7 sources) – Natural window lighting
14. **Gender (male vs. female)** (7 sources) – Gender comparison
15. **Water features** (7 sources) – Water elements in environments
16. **Blue light** (6 sources) – Blue wavelength lighting
17. **Light exposure** (6 sources) – Duration/intensity of light
18. **Ceiling height** (6 sources) – Vertical spatial dimension
19. **Social factors** (6 sources) – Social environmental aspects
20. **Music** (6 sources) – Auditory stimuli

---

## Key Findings

### Environmental Dimension Coverage

The extraction reveals strong coverage of built environment research across multiple dimensions:

- **Sensory Dimensions**: Lighting (11.6%), Sound/Acoustic (8.9%), Color/Material (8.3%)
- **Spatial Dimensions**: Spatial Configuration (4.3%), Outdoor Environment (4.8%), Building Type (4.7%)
- **Biophilic/Nature**: Plants/Greenery (3.8%), Views (2.2%), Nature (7.5%)
- **Comfort/Control**: Thermal (3.5%), Furniture/Interior (2.1%)
- **Aesthetic**: Art/Decoration (9.6%)

### Dominant Research Areas

1. **Lighting Research**: Natural light, daylight, daylighting, and illuminance are consistently present (multiple sources each)
2. **Acoustic Research**: Noise, acoustic environments, and soundscapes are well-documented
3. **Biophilic Research**: Plants, biophilic design, and nature exposure feature prominently
4. **Thermal Comfort**: Temperature and ventilation are regularly studied
5. **Spatial Design**: Building type, room layout, and spatial density are common stimuli

### Notable Patterns

- **Cross-category stimuli**: Some descriptions appear in multiple categories (e.g., "Distinctive personal living space" includes lighting, color_material, furniture_interior, building_type, and art_decoration)
- **"Other" category dominance**: ~29% of stimuli don't clearly fit predefined categories, suggesting diverse research landscapes and non-environmental factors (gender, social factors, etc.)
- **Replication across studies**: Top 20 stimuli appear 5-19 times, indicating consistent research foci

---

## Output File Structure

The output JSON file (`stimulus_descriptions_from_articles.json`) contains:

```json
{
  "metadata": {
    "generated": "YYYY-MM-DD",
    "source": "N extraction files",
    "total_findings_processed": N,
    "total_unique_stimuli": N,
    "total_unique_categories": N,
    "files_processed_successfully": N,
    "files_with_errors": N
  },
  "categories": {
    "lighting": {
      "description": "...",
      "count": N,
      "stimuli": [
        {
          "antecedent": "stimulus description",
          "doi": "10.xxxx/yyyy",
          "title": "article title",
          "claim_type": "empirical_finding|causal|associational|...",
          "categories": ["lighting", "other_category"]
        },
        ...
      ]
    },
    ...
  },
  "all_stimuli": [
    {
      "antecedent": "stimulus description",
      "source_count": N,
      "sources": [
        {
          "doi": "10.xxxx/yyyy",
          "title": "article title",
          "claim_type": "..."
        },
        ...
      ],
      "categories": ["category1", "category2"]
    },
    ...
  ]
}
```

---

## Extraction Methodology

### Data Source
- 1,043 JSON extraction files from scientific articles
- Each file contains article metadata and structured findings
- Findings include antecedent (stimulus) and consequent (outcome) pairs

### Categorization Strategy
- **Keyword matching**: Case-insensitive substring matching against category-specific keyword lists
- **Multi-category assignment**: Stimuli can be assigned to multiple categories
- **Conservative approach**: Stimuli not matching any category assigned to "other"

### Keyword Categories
- **Lighting**: light, illumination, daylight, window, luminance, etc.
- **Plants/Greenery**: plant, vegetation, biophil, green wall, flora, etc.
- **Views**: view, window view, vista, prospect, scenic, etc.
- **Spatial Configuration**: layout, open plan, enclosed, crowding, density, etc.
- **Color/Material**: color, material, texture, surface, wood, brick, etc.
- **Sound/Acoustic**: sound, noise, acoustic, quiet, reverb, etc.
- **Thermal**: temperature, heating, cooling, ventilation, humidity, etc.
- **Nature**: outdoor, natural environment, landscape, water, sky, etc.
- **Furniture/Interior**: furniture, desk, seating, interior, decor, etc.
- **Building Type**: hospital, office, school, residential, workplace, etc.
- **Outdoor Environment**: patio, terrace, plaza, garden, street, etc.
- **Art/Decoration**: art, aesthetic, artwork, design, ornament, etc.

---

## Usage Notes

### Access the Data

**Full dataset with all sources**:
```python
import json
with open('stimulus_descriptions_from_articles.json', 'r') as f:
    data = json.load(f)
```

**By category**:
```python
lighting_stimuli = data['categories']['lighting']['stimuli']
```

**Most frequent stimuli**:
```python
top_20 = data['all_stimuli'][:20]
```

### Applications

1. **Evidence synthesis**: Understand what environmental variables are studied
2. **Research design**: Identify common and novel stimulus types
3. **Replication mapping**: See which stimuli have been used multiple times
4. **Gap analysis**: Identify understudied environmental dimensions
5. **Stimulus library**: Build experimental stimulus sets for new research

---

## Technical Notes

- **Encoding handling**: Processed files with `utf-8` encoding and fallback to `replace` strategy for problematic characters
- **Duplicate handling**: Unique antecedents tracked across multiple sources
- **Source tracking**: Each stimulus linked to DOI, title, and claim type of source articles
- **Error tolerance**: 4 files skipped due to JSON parsing errors (0.4% failure rate)

---

## Recommendations for Use

1. **Validate categories**: Review stimuli in "other" category for potential recategorization
2. **Distinguish claim types**: Filter by `claim_type` (empirical, causal, associational, narrative) based on your needs
3. **Source diversity**: Use `source_count` to identify well-studied vs. novel stimulus types
4. **Multi-category analysis**: Recognize that many stimuli operate across multiple environmental dimensions
5. **Domain specificity**: Consider filtering by `building_type` for domain-specific applications

---

## Script Reference

**Location**: `extract_stimulus_descriptions.py`

Generates the full JSON output with categorization, frequency analysis, and summary reporting.

Run with:
```bash
python3 extract_stimulus_descriptions.py
```

---

*Dataset extracted 2026-02-28 from Article_Eater extraction pipeline.*
