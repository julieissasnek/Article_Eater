# Causal-Theoretic Image Attributes Taxonomy

## Overview

This directory contains a comprehensive taxonomy of 21 visual attributes for architectural image characterization, grounded in perception science, biophilic design theory, and vision algorithms.

**Generated**: 2026-02-28  
**Version**: 1.0.0  
**Schema**: `image_attributes.causal.v1`

## What's Here

### Primary Taxonomy
- **`causal_theoretic_image_attributes.json`** (48 KB)
  - Complete taxonomy with all 21 attributes
  - Vision algorithms with implementation tiers
  - Theoretical warrant with peer-reviewed references
  - Everyday-to-causal mappings

### Documentation
- **`TAXONOMY_GENERATION_REPORT.md`** (6.8 KB)
  - High-level overview
  - Design decisions and theoretical foundations
  - Integration roadmap with BN_graphical
  - Next implementation steps

- **`USAGE_GUIDE.md`** (9.5 KB)
  - Practical guide for developers
  - Code examples for loading and using the taxonomy
  - Pipeline architecture (Tier 1, 2, 3)
  - Cultural calibration notes

- **`README.md`** (this file)
  - Quick orientation guide

### Generation Script
- **`../scripts/generate_causal_attributes.py`** (57 KB)
  - Reproducible Python script
  - Full documentation and theoretical comments
  - Can be re-run to regenerate the taxonomy

## Quick Start

### Load the taxonomy in Python

```python
import json

with open('causal_theoretic_image_attributes.json', 'r') as f:
    taxonomy = json.load(f)

# Access all attributes
attributes = taxonomy['attributes']

# Look up everyday terms
cozy_attributes = taxonomy['everyday_to_causal_map']['cozy']
# Returns: ['ATTR-S3', 'ATTR-C1', 'ATTR-M2', 'ATTR-M1']
```

### Explore the structure

```python
# Get one attribute
attr_f1 = attributes[0]  # Fractal Dimension

print(attr_f1['name'])              # "Fractal Dimension (Box-Counting)"
print(attr_f1['causal_variable'])   # "Fractal dimension D..."
print(attr_f1['optimal_range'])     # [1.3, 1.5]
print(attr_f1['status'])            # "ready_to_implement"
print(attr_f1['vision_algorithm']['tier'])  # 1 (low complexity)
```

## The 21 Attributes

### Fractal & Natural Statistics (4)
| ID | Name | Optimal Range | Tier | Status |
|---|---|---|---|---|
| ATTR-F1 | Fractal Dimension | 1.3-1.5 | 1 | Ready |
| ATTR-F2 | 1/f Spectral Slope | 0.9-1.1 | 1 | Ready |
| ATTR-F3 | Lacunarity | 1.0-1.5 | 1 | Ready |
| ATTR-F4 | Edge Density | 15-35% | 1 | Ready |

### Color (3)
| ID | Name | Optimal Range | Tier | Status |
|---|---|---|---|---|
| ATTR-C1 | CCT (Kelvin) | 3000-5500K | 1 | Ready |
| ATTR-C2 | Chromatic Distribution | balanced | 1 | Ready |
| ATTR-C3 | Green Chromaticity | 10-40% | 1 | Ready |

### Spatial (4)
| ID | Name | Optimal Range | Tier | Status |
|---|---|---|---|---|
| ATTR-S1 | Isovist Area | 0.4-0.8 | 2 | Ready |
| ATTR-S2 | Ceiling Height | 0.6-1.0 | 2 | Ready |
| ATTR-S3 | Enclosure Ratio | 1.0-1.8 | 2 | Ready |
| ATTR-S4 | Spatial Legibility | 2.5-4.5 bits | 2 | Ready |

### Material (3)
| ID | Name | Optimal Range | Tier | Status |
|---|---|---|---|---|
| ATTR-M1 | Material Naturalness | 40-80% | 2 | Ready |
| ATTR-M2 | Haptic Expectation | varied | 2 | Ready |
| ATTR-M3 | Olfactory Expectation | varied | 2 | Research |

### Biophilic (3)
| ID | Name | Optimal Range | Tier | Status |
|---|---|---|---|---|
| ATTR-B1 | Biomorphic Form | 30-70% curves | 2 | Ready |
| ATTR-B2 | Water Features | presence | 1 | Ready |
| ATTR-B3 | Biophilic Score | 60-85 | 3 | Ready |

### Perceptual (2)
| ID | Name | Optimal Range | Tier | Status |
|---|---|---|---|---|
| ATTR-P1 | Figure-Ground Clarity | 0.6-0.95 | 2 | Ready |
| ATTR-P2 | Symmetry Score | 0.4-0.8 | 1 | Ready |

### Affordance (2)
| ID | Name | Optimal Range | Tier | Status |
|---|---|---|---|---|
| ATTR-A1 | Sitting Affordance | 0.1-0.5/m² | 3 | Research |
| ATTR-A2 | Social Density | 15-60 | 3 | Research |

## Everyday-to-Causal Mappings

Translate natural language to measurement:

| Descriptor | Maps to | Meaning |
|---|---|---|
| "rooms with plants" | F1, C3, B1, M3 | Fractal nature + green + organic forms + freshness |
| "cozy" | S3, C1, M2, M1 | Enclosed + warm + soft textures + natural materials |
| "beautiful" | F1, F2, P2, P1, B1 | Complex fractals + symmetric + clear + organic |
| "peaceful" | F4, F1, C3, B2 | Not cluttered + natural complexity + green + water |
| "natural materials" | M1, M2 | High % natural + soft/warm to touch |
| "high ceilings" | S2 | Large vertical proportion (>60% of view) |

See `USAGE_GUIDE.md` for complete list and code examples.

## Implementation Roadmap

### Phase 1: Tier 1 (This Week)
Quick implementations, 8 attributes:
- Canny edge detection → ATTR-F1, ATTR-F3, ATTR-F4
- FFT power spectrum → ATTR-F2
- Color analysis → ATTR-C1, ATTR-C2, ATTR-C3
- Symmetry detection → ATTR-P2

### Phase 2: Tier 2 (Next 2 Weeks)
Moderate complexity, 9 attributes:
- Spatial analysis (isovist, legibility)
- Material classification (vision transformer or CNN)
- Water feature detection
- Biomorphic form analysis

### Phase 3: Tier 3 (1+ Month)
High complexity, 2 attributes:
- ATTR-B3: Composite biophilic score
- ATTR-A1, ATTR-A2: Affordance detection with deep learning

See `TAXONOMY_GENERATION_REPORT.md` for detailed next steps.

## Theoretical Foundations

Every attribute grounds in peer-reviewed research:

- **Perception Science**: Hagerhall, Taylor, Spehar (fractals and natural preferences)
- **Color Theory**: Palmer & Schloss (color psychology), Berson et al. (circadian rhythms)
- **Spatial Cognition**: Appleton (prospect-refuge), Lynch (legibility), Benedikt (isovist)
- **Design**: Biophilic Design Institute, Wilson (biophilia hypothesis)
- **Neuroscience**: Gallace & Spence (cross-modal perception), Okamoto et al. (ceiling height)

30+ papers with DOI citations. See each attribute's `theoretical_warrant` field for details.

## Technical Specs

- **Format**: JSON (RFC 7158 compatible)
- **Schema**: `image_attributes.causal.v1`
- **Size**: 48 KB
- **Attributes**: 21 complete
- **Mappings**: 14 everyday-to-causal entries

## Integration with BN_graphical

These attributes feed into the sibling repository's Bayesian network:

- Attributes → Observed nodes in the network
- Optimal ranges → Prior distributions
- CVA constraints → Conditional dependencies
- Evidence strength → Calibrates conditional probability tables

See `TAXONOMY_GENERATION_REPORT.md` for integration details.

## Validation

- JSON schema: Valid
- All 21 attributes: Present with complete fields
- Vision algorithms: Specified with methods, steps, libraries, complexity
- Theoretical warrant: Theory + references + evidence strength + mechanism
- Everyday mappings: All reference valid attribute IDs

## Cultural Calibration

9 attributes marked as culturally variable and may need region-specific tuning:
- ATTR-C1 (color temperature preferences vary)
- ATTR-C2, ATTR-C3 (color preferences vary)
- ATTR-M1, ATTR-M2, ATTR-M3 (material perception varies)
- ATTR-P2 (symmetry preferences vary)
- ATTR-A1, ATTR-A2 (social norms vary)

12 attributes are considered universal across human populations (fractal preferences, spatial perception, etc.)

## Key Files Summary

| File | Size | Purpose | Audience |
|---|---|---|---|
| `causal_theoretic_image_attributes.json` | 48 KB | Master taxonomy | All |
| `generate_causal_attributes.py` | 57 KB | Reproducible generation | Engineers |
| `TAXONOMY_GENERATION_REPORT.md` | 6.8 KB | Overview & decisions | Managers, Researchers |
| `USAGE_GUIDE.md` | 9.5 KB | How-to guide | Developers |
| `README.md` | This file | Quick orientation | Everyone |

## Contact

**Owner**: Professor David Kirsh, UCSD Cognitive Science  
**Generated**: 2026-02-28T17:17:57.304099  
**Related**: BN_graphical (Bayesian causal modeling)

---

For questions or extensions, see `USAGE_GUIDE.md` for examples or contact the project owner.
