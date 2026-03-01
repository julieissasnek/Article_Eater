# Causal-Theoretic Image Attributes: Usage Guide

## Quick Start

Load the taxonomy:

```python
import json

with open('causal_theoretic_image_attributes.json', 'r') as f:
    taxonomy = json.load(f)

# All 21 attributes
attributes = taxonomy['attributes']

# Everyday-to-causal mappings
everyday_map = taxonomy['everyday_to_causal_map']
```

## Organization

### By Group (7 groups)

```python
# Group all attributes by category
by_group = {}
for attr in taxonomy['attributes']:
    group = attr['group']
    if group not in by_group:
        by_group[group] = []
    by_group[group].append(attr)

# Access fractal attributes
fractal_attrs = by_group['fractal_natural_statistics']
```

### By Status (Ready vs. Research)

```python
# Only ready-to-implement attributes
ready = [a for a in taxonomy['attributes'] if a['status'] == 'ready_to_implement']

# Only research-phase attributes
research = [a for a in taxonomy['attributes'] if a['status'] == 'research_phase']
```

### By Implementation Tier (1-3)

```python
# Group by vision algorithm complexity
by_tier = {}
for attr in taxonomy['attributes']:
    tier = attr['vision_algorithm']['tier']
    if tier not in by_tier:
        by_tier[tier] = []
    by_tier[tier].append(attr)

# Quick-to-implement (Tier 1)
quick_win_attrs = by_tier[1]
```

## Using Individual Attributes

Each attribute has this structure:

```python
attr = taxonomy['attributes'][0]  # ATTR-F1

# Basic info
attr['attribute_id']           # "ATTR-F1"
attr['name']                   # "Fractal Dimension (Box-Counting)"
attr['group']                  # "fractal_natural_statistics"
attr['everyday_descriptors']   # ["natural-looking", "organic", ...]

# Causal definition
attr['causal_variable']        # "Fractal dimension D (box-counting), optimal 1.3-1.5"
attr['unit']                   # "dimensionless (1.0-2.0)"
attr['optimal_range']          # [1.3, 1.5]

# Vision algorithm
attr['vision_algorithm']['method']                  # "box_counting_fractal_dimension"
attr['vision_algorithm']['steps']                   # List of algorithm steps
attr['vision_algorithm']['libraries']              # ["opencv-python", "numpy", "scipy"]
attr['vision_algorithm']['implementation_complexity'] # "low"
attr['vision_algorithm']['tier']                    # 1

# Theoretical grounding
attr['theoretical_warrant']['theory']              # "Attention Restoration Theory + ..."
attr['theoretical_warrant']['key_refs']            # List of papers with DOI
attr['theoretical_warrant']['evidence_strength']   # "strong", "moderate", etc.
attr['theoretical_warrant']['mechanism']           # How this attribute works

# Metadata
attr['cva_constraints']        # ["prediction_error", "spatial_frequency_match"]
attr['cultural_calibration']   # True/False: requires culture-specific tuning?
attr['status']                 # "ready_to_implement" or "research_phase"
```

## Using the Everyday-to-Causal Map

Translate user language to causal attributes:

```python
# "That room feels cozy" → which attributes define coziness?
coziness_attrs = taxonomy['everyday_to_causal_map']['cozy']
# ['ATTR-S3', 'ATTR-C1', 'ATTR-M2', 'ATTR-M1']

# Get full attribute definitions
cozy_definitions = [a for a in taxonomy['attributes'] if a['attribute_id'] in coziness_attrs]

# Cozy = moderate enclosure + warm lighting + soft textures + natural materials
for attr in cozy_definitions:
    print(f"{attr['attribute_id']}: {attr['name']}")
    print(f"  Optimal: {attr['optimal_range']}")
    print(f"  Everyday: {attr['everyday_descriptors']}")
```

## Building a Vision Pipeline

### Tier 1 (Quick, low complexity)

Start with these 8 easy-to-compute attributes:

```python
tier1 = [a for a in taxonomy['attributes'] if a['vision_algorithm']['tier'] == 1]
# [ATTR-F1, ATTR-F2, ATTR-F3, ATTR-F4, ATTR-C1, ATTR-C2, ATTR-C3, ATTR-B2, ATTR-P2]

# For each Tier 1 attribute, implement the algorithm in vision_algorithm['steps']
# These require only OpenCV, NumPy, basic image processing
```

### Tier 2 (Medium complexity)

Once Tier 1 works, add these 9 attributes requiring spatial analysis & classification:

```python
tier2 = [a for a in taxonomy['attributes'] if a['vision_algorithm']['tier'] == 2]
# [ATTR-S1, ATTR-S2, ATTR-S3, ATTR-S4, ATTR-M1, ATTR-M2, ATTR-B1, ATTR-P1, ATTR-M3]

# These require: 3D reconstruction, material classification models, spatial metrics
```

### Tier 3 (High complexity)

Finally, implement composite & advanced algorithms:

```python
tier3 = [a for a in taxonomy['attributes'] if a['vision_algorithm']['tier'] == 3]
# [ATTR-B3, ATTR-A1, ATTR-A2]

# ATTR-B3: Weighted composite of 7 components
# ATTR-A1, ATTR-A2: Deep learning object detection, affordance inference
```

## Computing a Biophilic Design Score

Example: compute ATTR-B3 (Biophilic Design Score) from component attributes:

```python
# ATTR-B3 weights components:
# 0.15*F1 + 0.15*C3 + 0.12*B1 + 0.10*B2 + 0.15*M1 + 0.15*S1 + 0.18*M3

def compute_biophilic_score(image):
    """Compute composite biophilic design score (0-100)"""

    # Compute component attributes (normalize to 0-100)
    attr_f1 = fractal_dimension(image)        # D value 1.0-2.0 → scale to 0-100
    attr_c3 = green_chromaticity(image)       # already 0-100
    attr_b1 = biomorphic_form_index(image)    # curved proportion 0-100
    attr_b2 = water_feature_present(image)    # 0 or 100
    attr_m1 = material_naturalness(image)     # 0-100
    attr_s1 = isovist_area(image)             # normalized 0-100
    attr_m3 = olfactory_freshness(image)      # 0-100

    # Weighted sum
    score = (
        0.15 * attr_f1 +
        0.15 * attr_c3 +
        0.12 * attr_b1 +
        0.10 * attr_b2 +
        0.15 * attr_m1 +
        0.15 * attr_s1 +
        0.18 * attr_m3
    )

    return score  # 0-100

# Optimal biophilic score: 60-85
```

## References and Theoretical Grounding

Every attribute links to peer-reviewed papers. Example:

```python
attr = [a for a in taxonomy['attributes'] if a['attribute_id'] == 'ATTR-F1'][0]

# Key research papers
for ref in attr['theoretical_warrant']['key_refs']:
    print(f"{ref['authors']} ({ref['year']})")
    print(f"  Finding: {ref['finding']}")
    print(f"  DOI: {ref['doi']}")
    print()

# Output:
# Hagerhall et al. (2004)
#   Finding: Nature images cluster at D ≈ 1.3
#   DOI: 10.1121/1.1646134
# Taylor et al. (2005)
#   Finding: D ≈ 1.3-1.5 preferred cross-culturally in fractals and landscapes
#   DOI: 10.1167/5.5.5
# Spehar et al. (2003)
#   Finding: Universal preference for intermediate D across cultures
#   DOI: 10.1167/3.8.5
```

## Cultural Calibration

Some attributes are culturally variable and need region-specific tuning:

```python
culturally_variable = [a for a in taxonomy['attributes'] if a['cultural_calibration']]
# [ATTR-C1, ATTR-C2, ATTR-C3, ATTR-M1, ATTR-M2, ATTR-M3, ATTR-P2, ATTR-A1, ATTR-A2]

# For example, ATTR-C1 (Correlated Color Temperature):
# - Western preferences: 3000-5500K (warm to daylight)
# - May differ in other cultural contexts with different lighting traditions
# - Requires validation with local populations
```

## CVA Constraints

Some attributes are linked by Causal Variable Analysis (CVA) constraints:

```python
attr = [a for a in taxonomy['attributes'] if a['attribute_id'] == 'ATTR-F1'][0]
constraints = attr['cva_constraints']
# ['prediction_error', 'spatial_frequency_match']

# These constraints define how attributes interact in the Bayesian network
# e.g., fractal dimension affects prediction error, which affects visual comfort
```

## Integration with BN_graphical

These attributes form the observed nodes in the Bayesian network:

```python
# Each attribute ID becomes a network node
# optimal_range defines prior distributions
# evidence_strength calibrates conditional probability tables
# cva_constraints define network edges

# Example BN structure:
# ATTR-F1 (fractal dimension)
#   ├─→ ATTR-C3 (green chromaticity)  [both support biophilia]
#   └─→ ATTR-B3 (biophilic score)
```

## Example: Analyzing an Architectural Image

```python
import cv2
import numpy as np

def analyze_image(image_path, taxonomy):
    """Compute all computable attributes for an image"""

    img = cv2.imread(image_path)
    results = {}

    # Tier 1: Quick attributes
    for attr in [a for a in taxonomy['attributes'] if a['vision_algorithm']['tier'] == 1]:
        attr_id = attr['attribute_id']

        if attr_id == 'ATTR-F1':
            results[attr_id] = fractal_dimension_box_counting(img)
        elif attr_id == 'ATTR-F2':
            results[attr_id] = spectral_slope_1_over_f(img)
        elif attr_id == 'ATTR-C1':
            results[attr_id] = cct_from_image(img)
        elif attr_id == 'ATTR-C3':
            results[attr_id] = green_chromaticity(img)
        # ... etc.

    # Return dictionary with attribute_id → computed_value
    return results

# Use results
results = analyze_image('room.jpg', taxonomy)
print(f"Fractal dimension: {results['ATTR-F1']:.2f} (optimal: 1.3-1.5)")
print(f"Green content: {results['ATTR-C3']:.1f}% (optimal: 10-40%)")
```

## Next Steps

1. **Implement Tier 1 algorithms** → quick wins, validate results
2. **Benchmark against preference data** → do optimal ranges match empirical preferences?
3. **Build material classification** (Tier 2) → enable ATTR-M1, ATTR-M2
4. **Validate with human subjects** → especially Tier 3 and research-phase attributes
5. **Submit to panel review** → get feedback on weighting, especially ATTR-B3
6. **Integrate with BN_graphical** → create causal Bayesian network

---

**Contact**: Professor David Kirsh, UCSD Cognitive Science
**Related repo**: BN_graphical (Bayesian causal modeling)
**Generated**: 2026-02-28
