# Causal-Theoretic Image Attributes Taxonomy

**Generated**: 2026-02-28T17:17:57.304099  
**Version**: 1.0.0  
**Schema**: `image_attributes.causal.v1`  
**Location**: `/data/attributes/causal_theoretic_image_attributes.json`

## Overview

This taxonomy encodes **21 causal-theoretic visual attributes** for architectural image characterization. Each attribute:

1. Maps everyday descriptors to measurable causal variables
2. Specifies vision algorithms with implementation complexity and libraries
3. Grounds choices in perception science (Hagerhall, Taylor, Spehar, Kaplan, etc.)
4. Defines optimal ranges based on empirical evidence
5. Tracks cultural calibration requirements
6. Lists implementation readiness status

## Attributes by Group

### Fractal & Natural Statistics (4 attributes)
- **ATTR-F1**: Fractal Dimension (box-counting) — D ≈ 1.3-1.5 optimal
- **ATTR-F2**: 1/f Spectral Slope — α ≈ 0.9-1.1 optimal
- **ATTR-F3**: Lacunarity — gap distribution at multiple scales
- **ATTR-F4**: Edge Density & Distribution — 15-35% edges optimal

*Theory*: Attention Restoration Theory + Efficient Coding Hypothesis  
*Status*: 4/4 ready to implement

### Color (3 attributes)
- **ATTR-C1**: Correlated Color Temperature (CCT) — 3000-5500K optimal
- **ATTR-C2**: Chromatic Distribution (CIE Lab) — balanced hue entropy
- **ATTR-C3**: Green Chromaticity — 10-40% vegetation optimal

*Theory*: Color Psychology + Biophilia Hypothesis  
*Status*: 3/3 ready to implement

### Spatial (4 attributes)
- **ATTR-S1**: Isovist Area — visible floor area from viewpoint
- **ATTR-S2**: Ceiling Height — vertical proportion and openness
- **ATTR-S3**: Enclosure Ratio — wall area to floor area balance
- **ATTR-S4**: Spatial Legibility — complexity entropy of layout

*Theory*: Prospect-Refuge Theory + Wayfinding Theory  
*Status*: 4/4 ready to implement

### Material (3 attributes)
- **ATTR-M1**: Material Naturalness Index — % natural vs. synthetic
- **ATTR-M2**: Haptic Expectation — inferred tactile properties
- **ATTR-M3**: Olfactory Expectation — inferred odor character

*Theory*: Biophilic Design + Cross-Modal Perception  
*Status*: 2/3 ready to implement; 1/3 in research phase

### Biophilic (3 attributes)
- **ATTR-B1**: Biomorphic Form Index — curved vs. rectilinear
- **ATTR-B2**: Water Feature Presence — fountains, aquariums
- **ATTR-B3**: Biophilic Design Score — weighted composite (7 components)

*Theory*: Biophilic Design Institute + Evolutionary Aesthetics  
*Status*: 3/3 ready to implement

### Perceptual (2 attributes)
- **ATTR-P1**: Figure-Ground Clarity — contrast and saliency
- **ATTR-P2**: Symmetry Score — bilateral and rotational balance

*Theory*: Gestalt Theory + Aesthetic Preference  
*Status*: 2/2 ready to implement

### Affordance (2 attributes)
- **ATTR-A1**: Sitting Affordance Density — places to sit per m²
- **ATTR-A2**: Social Density Inference — expected occupancy and interaction

*Theory*: Gibson's Affordance Theory + Proxemics  
*Status*: 0/2 ready; 2/2 in research phase

## Implementation Complexity Tiers

| Tier | Complexity | Examples | Count |
|------|-----------|----------|-------|
| 1 | Low | Canny edges, color histograms, spectral analysis | 8 |
| 2 | Medium | Perspective estimation, material classification, spatial entropy | 9 |
| 3 | High | Deep learning object detection, 3D reconstruction, spatial integration | 2 |

## Everyday-to-Causal Mappings

The taxonomy includes 14 mappings from everyday descriptors to causal attributes:

- "rooms with plants" → F1, C3, B1, M3
- "natural materials" → M1, M2
- "high ceilings" → S2
- "open space" → S1, S3
- "good lighting" → C1
- "nature views" → C3, F1, B2
- "cluttered" → F4
- "cozy" → S3, C1, M2, M1
- "peaceful" → F4, F1, C3, B2
- "confusing layout" → S4
- "beautiful" → F1, F2, P2, P1, B1
- "warm/inviting" → C1, M2, M1, B1
- "noisy-looking" → A2 (high social density)
- "sterile/clinical" → C1 (high CCT), M1 (low naturalness), S3 (low enclosure)

## Key Design Decisions

1. **Causal over descriptive**: Attributes measure causal variables (fractal dimension) not subjective impressions
2. **Grounding in perception science**: Every attribute traces to empirical research with DOI references
3. **Vision algorithms specified**: Each attribute includes detailed algorithm steps, libraries, and complexity rating
4. **Optimal ranges empirically derived**: Ranges based on cross-cultural preference studies (Hagerhall, Taylor, Spehar, Palmer, etc.)
5. **Cultural calibration tracking**: 9/21 attributes marked as requiring culture-specific calibration
6. **Implementation readiness tiers**: Clear separation of what's ready to build vs. what needs research

## Theoretical Foundations

The taxonomy integrates multiple theoretical frameworks:

- **Attention Restoration Theory (ART)**: Why fractal natural statistics reduce cognitive fatigue
- **Efficient Coding Hypothesis**: How visual system exploits natural scene statistics for efficient processing
- **Biophilia Hypothesis**: Why presence of vegetation, natural materials, and water reduces stress
- **Prospect-Refuge Theory**: Why balance between openness and enclosure feels secure and comfortable
- **Gestalt Theory**: Why figure-ground clarity and symmetry support perceptual organization
- **Embodied Cognition**: Why ceiling height influences abstract thinking, material texture activates somatosensory cortex
- **Cross-Modal Perception**: How visual context primes olfactory and tactile expectations

## Next Steps

1. **Immediate**: Implement Tier 1 algorithms (low complexity) for fractal, color, and edge-based attributes
2. **Short-term**: Build material classification models (Tier 2) using transfer learning
3. **Medium-term**: Develop spatial analysis algorithms (isovist computation, spatial entropy) with 3D reconstruction
4. **Research phase**: Validate ATTR-M3, ATTR-A1, ATTR-A2 with human subjects (cross-modal associations, affordance detection)
5. **Panel review**: Present composite ATTR-B3 (Biophilic Score) to experts for feedback on weighting

## Integration with BN_graphical

These attributes feed into the Bayesian network infrastructure in the sibling repo `BN_graphical`:

- **Causal variables**: Serve as observed nodes in the Bayesian network
- **Optimal ranges**: Inform prior distributions and likelihood functions
- **CVA constraints**: Define conditional dependencies between attributes
- **Evidence strength**: Calibrate conditional probability tables based on theoretical warrant

## File Statistics

- **Size**: 48 KB (47.5 KB JSON)
- **Attributes**: 21
- **Mappings**: 14
- **References**: 30+ peer-reviewed papers with DOIs
- **Status**: 13 ready to implement, 4 in research phase, 4 ready to implement

---

**Generated by**: Claude Code (Anthropic)  
**Repository**: Article_Eater_PostQuinean_v1  
**Related**: BN_graphical (Bayesian causal modeling)
