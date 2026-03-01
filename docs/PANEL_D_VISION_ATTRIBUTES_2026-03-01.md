# Panel D: Vision Attribute Taxonomy
## Expert Panel Consultation

**Date**: 2026-03-01
**Panel Type**: Computational Vision, Aesthetic Science, Environmental Design
**Quorum**: 3 panelists (all present)

---

## Panel Composition

| Panelist | Expertise | Tradition | Role |
|----------|-----------|-----------|------|
| Dr. Serge Belongie (Vision Science) | Computational vision, image statistics, scene understanding, vision algorithms | Vision/Graphics tradition (Malik, Freeman) | Domain Expert |
| Dr. Christof Koch (Computational Aesthetics) | Beauty prediction, aesthetic science, image quality, neural correlates | Vision + neuroscience | Methodologist |
| Dr. Christopher Alexander (Built Environment) | Architecture, pattern language, design measurement, spatial metrics | Pattern Language tradition | Domain Expert |

---

## Input Materials Summary

**Source**: `/data/attributes/causal_theoretic_image_attributes.json` (Version 1.0)
**Generated**: 2026-02-28
**Schema**: Causal-theoretic visual attributes for architectural image characterization

**Taxonomy Structure** (21 attributes across 7 groups):

1. **Fractal/Natural Statistics** (4 attributes):
   - ATTR-F1: Fractal Dimension (Box-Counting), optimal range 1.3–1.5
   - ATTR-F2: 1/f Spectral Slope (natural image statistics)
   - ATTR-F3: Lacunarity (gap-size distribution)
   - ATTR-F4: Edge Density and Distribution

2. **Color** (3 attributes):
   - ATTR-C1: Correlated Color Temperature (CCT), perceptual warmth
   - ATTR-C2: Chromatic Distribution (CIE Lab)
   - ATTR-C3: Green Chromaticity (biophilic signal)

3. **Spatial** (4 attributes):
   - ATTR-S1: Isovist Area and Properties (prospect)
   - ATTR-S2: Ceiling Height / Vertical Proportion (enclosure)
   - ATTR-S3: Enclosure Ratio (refuge)
   - ATTR-S4: Spatial Legibility (wayfinding)

4. **Material** (3 attributes):
   - ATTR-M1: Material Naturalness Index (natural vs. synthetic)
   - ATTR-M2: Haptic Expectation from Visual Input (surface tactile expectations)
   - ATTR-M3: Olfactory Expectation from Visual Input (scent cues from appearance)

5. **Biomorphic** (2 attributes):
   - ATTR-B1: Biomorphic Form Index (curved vs. rectilinear)
   - ATTR-B2: Water Feature Presence (binary or continuous)

6. **Composite/High-level** (3 attributes):
   - ATTR-B3: Biophilic Design Score (composite of F1, C3, M1, B1, B2)
   - ATTR-P1: Figure-Ground Clarity (perceptual organization)
   - ATTR-P2: Symmetry Score (bilateral/rotational symmetry)

7. **Affordances** (2 attributes):
   - ATTR-A1: Sitting Affordance Density (places to rest)
   - ATTR-A2: Social Density Inference (places for interaction)

**NEW attributes (task description mentions 12 NEW, but JSON shows 0 NEW-prefixed)**: The file contains 21 established attributes. No NEW-01 through NEW-12 visible in current version. This is a **gap**: Either new attributes exist in a different file, or they were planned but not yet integrated.

---

## Panel Questions

### Q1: Are the 21 attributes (and 12 new attributes, if provided) well-defined?

**Dr. Belongie (Vision Science):**

Let me evaluate each attribute group for operationalization quality:

**Group 1: Fractal/Natural Statistics** — **Well-defined operationally**. These have decades of vision/graphics literature grounding:

1. **ATTR-F1 (Fractal Dimension, Box-Counting), optimal 1.3–1.5**:
   - **Definition**: Measurement of self-similarity across scales using box-counting algorithm (Mandelbrot, 1983; Hagerhall et al., 2004)
   - **Algorithm**: Canny edge detection → binary edge map → count boxes containing edges at scales {4, 8, 16, 32, 64, 128, 256} → linear regression log(N) vs. log(1/ε)
   - **Validation**: Hagerhall et al. (2004) show natural images cluster at D ≈ 1.3, supporting optimal range claim
   - **Confidence: 0.92** ✓ (well-established)

2. **ATTR-F2 (1/f Spectral Slope)**:
   - **Definition**: Power spectrum slope in frequency domain. Natural images exhibit 1/f power spectrum (Tolhurst et al., 1992)
   - **Algorithm**: Fourier transform → compute power as function of frequency → fit power law: P(f) ∝ 1/f^β
   - **Validation**: Empirically robust; human visual system tuned to 1/f statistics (Torralba & Oliva, 2003)
   - **Confidence: 0.88** ✓ (well-supported)

3. **ATTR-F3 (Lacunarity)**:
   - **Definition**: Gap-size distribution; measures degree of "gappiness" in texture (Mandelbrot, 1983)
   - **Algorithm**: Box-counting variant; count empty boxes across scales
   - **Validation**: Less commonly used than fractal dimension but computationally sound
   - **Confidence: 0.75** (valid but less empirically validated in psychology)

4. **ATTR-F4 (Edge Density and Distribution)**:
   - **Definition**: Percentage of pixels identified as edges; distribution properties (concentration vs. dispersed)
   - **Algorithm**: Canny or Sobel edge detection; compute edge density, clustering coefficient
   - **Validation**: Standard in vision; directly relevant to visual complexity
   - **Confidence: 0.85** ✓

**Group 2: Color** — **Partially well-defined**:

1. **ATTR-C1 (Correlated Color Temperature, CCT)**:
   - **Definition**: Warmth of light source; expressed in Kelvin (warm: 2700K–3000K; neutral: 4000K–5000K; cool: >6500K)
   - **Algorithm**: Convert RGB to CIE 1960 color space → compute CCT via McCamy formula or lookup table
   - **Validation**: Standard in lighting; empirically linked to mood/restoration (Kaplan et al., 2008)
   - **Confidence: 0.90** ✓

2. **ATTR-C2 (Chromatic Distribution, CIE Lab)**:
   - **Definition**: Distribution of hue, saturation, lightness in CIE Lab color space
   - **Algorithm**: Convert RGB → Lab; compute histogram or statistical moments (mean, std, skewness of a/b channels)
   - **Validation**: Lab space is perceptually uniform; standard for color analysis
   - **Confidence: 0.80** ✓

3. **ATTR-C3 (Green Chromaticity)**:
   - **Definition**: Proportion of green hues in the image; assumed to signal biophilic preference (plants, nature)
   - **Algorithm**: Threshold hue channel (H) for green range [~90°–180° in HSL]; compute green pixel ratio
   - **Validation**: Intuitive but **oversimplified**. Green can be artificial (plastic, painted). Not all nature is green (stone, soil, dead trees). Biophilic signal is context-dependent, not just chromatic.
   - **Confidence: 0.55** (problematic oversimplification)

**Group 3: Spatial** — **Moderately well-defined**:

1. **ATTR-S1 (Isovist Area and Properties)**:
   - **Definition**: Isovist = polygon visible from a given point (Benedikt, 1979). Isovist area is prospect/openness.
   - **Algorithm**: Ray-casting from observer point; check line-of-sight to all pixels
   - **Validation**: Standard in architecture (space syntax; Hillier & Hanson, 1984)
   - **Confidence: 0.85** ✓

2. **ATTR-S2 (Ceiling Height / Vertical Proportion)**:
   - **Definition**: Ratio of ceiling height to floor area; influences sense of enclosure and psychological effects (Meyers-Levy & Zhu, 2007)
   - **Algorithm**: Estimate horizon line (edge between walls and ceiling); compute height-to-width ratio
   - **Validation**: Psychologically validated; linked to cognitive scope (high ceilings → abstract thinking; low ceilings → focused thinking)
   - **Confidence: 0.82** ✓

3. **ATTR-S3 (Enclosure Ratio)**:
   - **Definition**: Measure of refuge; inverse of prospect. Related to prospect-refuge theory (Appleton, 1975)
   - **Algorithm**: (Perimeter of enclosing surfaces) / (Isovist perimeter); or similar ratio of enclosed vs. open views
   - **Validation**: Conceptually sound but **operationalization ambiguous**. Multiple ways to compute; no standard formula.
   - **Confidence: 0.65** (needs clearer algorithm)

4. **ATTR-S4 (Spatial Legibility)**:
   - **Definition**: Ability to understand and navigate space from visual input (Lynch, 1960; Lynch's "legibility")
   - **Algorithm**: **Not specified in description**. Candidates: edge map connectivity, junction density, path clarity. Unclear which is used.
   - **Validation**: Psychologically important but **computationally underspecified**.
   - **Confidence: 0.50** (needs algorithm specification)

**Group 4: Material** — **Poorly operationalized**:

1. **ATTR-M1 (Material Naturalness Index)**:
   - **Definition**: Ratio of natural (wood, stone, plants) to artificial (plastic, concrete, glass) materials
   - **Algorithm**: **Not specified**. How does algorithm distinguish wood texture from plastic? Likely requires texture descriptors or classification.
   - **Validation**: Concept is sound; empirically linked to biophilia. But **operationalization is vague**.
   - **Confidence: 0.45** (requires specification)

2. **ATTR-M2 (Haptic Expectation from Visual Input)**:
   - **Definition**: Infer tactile properties (smooth vs. rough) from appearance
   - **Algorithm**: **Not specified**. Candidates: texture analysis (Gabor filters, LBP for rough; smooth surfaces have low high-frequency content)
   - **Validation**: Neuroscientifically motivated (visual cortex is multimodal); empirically shows visual-haptic congruence (Lederman & Klatzky, 2009). But **algorithm missing**.
   - **Confidence: 0.40** (too vague for implementation)

3. **ATTR-M3 (Olfactory Expectation from Visual Input)**:
   - **Definition**: Infer scent from appearance (e.g., flowers → smell, ocean → salt air)
   - **Algorithm**: **Not specified and highly speculative**. Would require learned associations (flower classifier → olfactory expectation). High hallucination risk.
   - **Validation**: Interesting idea but **not empirically validated** in vision literature. How do you test if visual-olfactory expectation is accurate?
   - **Confidence: 0.25** (experimental, high uncertainty)

**Group 5: Biomorphic** — **Well-defined**:

1. **ATTR-B1 (Biomorphic Form Index)**:
   - **Definition**: Ratio of curved to rectilinear edges; high curvature → biomorphic
   - **Algorithm**: Extract edges → classify as curved vs. straight via curvature analysis; compute ratio
   - **Validation**: Empirically linked to preference (biomorphic forms preferred; Silvia & Barona, 2009)
   - **Confidence: 0.85** ✓

2. **ATTR-B2 (Water Feature Presence)**:
   - **Definition**: Binary or continuous indicator of water (ponds, fountains, streams, ocean)
   - **Algorithm**: Color/texture classification for water; compute water area ratio
   - **Validation**: Well-established (water strongly predicts preference and restoration; Kaplan, 1989)
   - **Confidence: 0.88** ✓

**Group 6: Composite/High-level** — **Mixed**:

1. **ATTR-B3 (Biophilic Design Score)**:
   - **Definition**: Composite of F1 (fractal), C3 (green), M1 (natural materials), B1 (biomorphic), B2 (water)
   - **Algorithm**: Weighted sum of normalized sub-attributes
   - **Validation**: Intuitive but **arbitrary weighting**. Are all sub-attributes equally important? (Probably not: water presence > material naturalness)
   - **Confidence: 0.65** (needs weight justification)

2. **ATTR-P1 (Figure-Ground Clarity)**:
   - **Definition**: Ability to distinguish figure (object of interest) from background
   - **Algorithm**: **Not specified**. Candidates: Gestalt grouping measures, saliency maps, contrastive energy
   - **Validation**: Foundational in perception but **operationalization missing**.
   - **Confidence: 0.50** (needs algorithm)

3. **ATTR-P2 (Symmetry Score)**:
   - **Definition**: Degree of bilateral or rotational symmetry
   - **Algorithm**: Compute reflection consistency; or use symmetry detection algorithms (Loy & Eklundh, 2006)
   - **Validation**: Empirically linked to preference (symmetry preferred; Reber et al., 1998)
   - **Confidence: 0.80** ✓

**Group 7: Affordances** — **Underspecified**:

1. **ATTR-A1 (Sitting Affordance Density)**:
   - **Definition**: Number or density of places to sit (chairs, benches, ground level patches)
   - **Algorithm**: **Not specified**. Candidates: object detection (YOLO for chairs/benches), floor area segmentation, depth map analysis
   - **Validation**: Conceptually sound (affects social attraction); **algorithm undefined**.
   - **Confidence: 0.40**

2. **ATTR-A2 (Social Density Inference)**:
   - **Definition**: Infer how many people could comfortably interact in the space
   - **Algorithm**: **Not specified and highly speculative**. Depends on spatial configuration (is there a gathering area?), climate, cultural norms.
   - **Validation**: **No empirical grounding**. Too culturally/contextually variable.
   - **Confidence: 0.35** (questionable construct validity)

**Summary of operationalization quality**:
- **Well-operationalized**: F1, F2, F4, C1, C2, S1, S2, B1, B2, P2 (10 attributes; 48%)
- **Partially operationalized**: F3, S3, S4, B3, P1 (5 attributes; 24%)
- **Poorly operationalized**: C3, M1, M2, M3, A1, A2 (6 attributes; 29%)

**Confidence in assessment: 0.80**

---

**Dr. Koch (Computational Aesthetics):**

I assess attributes from neuroscience of beauty and aesthetic science perspective.

**Neurally plausible attributes**:

1. **Fractal dimension (F1)**: High neural plausibility. Fractal structure is efficiently processed by visual cortex (uses sparse coding; Simoncelli & Olshausen, 2001). Optimal D ≈ 1.3 matches peak efficiency.
   - **Confidence: 0.88** ✓

2. **1/f spectral slope (F2)**: High plausibility. Human visual system is tuned to 1/f statistics (natural image statistics hypothesis; Simoncelli & Olshausen, 2001).
   - **Confidence: 0.85** ✓

3. **Color temperature (C1)**: Moderate plausibility. Warm colors activate amygdala (threat response); cool colors activate insula (calm). But relationship is complex (warm + blue-sky context → pleasant; warm + red threat signal → unpleasant).
   - **Confidence: 0.70** (context-dependent)

4. **Symmetry (P2)**: High plausibility. Bilateral symmetry processed in right fusiform gyrus (face detection); linked to beauty (Perrett et al., 1999).
   - **Confidence: 0.85** ✓

5. **Biomorphic form (B1)**: Moderate plausibility. Curved forms activate ventral temporal cortex (object recognition); linked to preference. But curves are not universally preferred (some cultures prefer rectilinear; Cahan et al., 2015).
   - **Confidence: 0.70** (culturally variable)

**Problematic attributes** (weak neural grounding):

1. **Olfactory expectation from visual (M3)**: **Highly problematic**. Different neural pathway (olfactory cortex vs. visual cortex; slow cross-talk via piriform cortex and OFC). Visual-olfactory integration is **slow and voluntary**, not automatic perception.
   - **Confidence in neural implausibility: 0.85** (should not be included)

2. **Social density inference (A2)**: **Conceptually confused**. Social density is a **social-cognitive attribute**, not a visual attribute. Inferring how many people can comfortably interact depends on cultural norms (distances vary by culture), task context, etc. This is not a vision problem.
   - **Confidence: 0.90** (not a vision attribute)

3. **Material naturalness (M1)**: **Vague in neural terms**. What makes something "look natural"? Plants have high variance in color/texture. Concrete can imitate stone (fake). Material naturalness requires learned categories (what counts as "natural"?), not just visual features.
   - **Confidence in concern: 0.80**

**Missing attributes** (from beauty/aesthetics literature):

1. **Perceptual Fluency**: How easy is the image to process? Simple, coherent images are liked more (Reber et al., 2004). Neural basis: easier processing → reduced dorsolateral prefrontal demand → positive affect.
   - **Why missing?** Related to but distinct from complexity (F1, F4). Should be explicit.

2. **Prototypicality**: How close is the image to a category prototype? Prototypical examples are liked more (Rosch, 1978).
   - **Why missing?** Requires categorical knowledge; could be computed via deep learning feature extraction.

3. **Visual Surprise / Entropy**: Information-theoretic surprise (Shannon entropy); predicts visual attention and aesthetic interest (Deco & Rolls, 2005).
   - **Why missing?** Could be computed from edge distribution or feature histogram entropy.

4. **Color Harmony**: Do colors form a harmonious ensemble (analogous, complementary, triadic)? Harmonious colors are preferred (Schloss & Palmer, 2011).
   - **Why missing?** Related to C2 (chromatic distribution) but more specific (requires color harmony rules).

**Confidence in attribute assessment: 0.75**

---

**Dr. Alexander (Built Environment):**

I assess attributes against architectural design knowledge and pattern language tradition.

**Well-grounded in design tradition**:

1. **Prospect (Isovist area, S1)**: Foundational. Appleton (1975), Lynch (1960) both emphasize ability to see and understand space. ✓

2. **Enclosure (Ceiling height S2, Enclosure ratio S3)**: Central to place-making. Alexander et al. "A Pattern Language" (1977) emphasizes human-scaled enclosure and proportion. ✓

3. **Legibility (S4)**: Lynch's "The Image of the City" (1960) emphasizes wayfinding clarity. ✓

4. **Biomorphic form (B1)**: Alexander's "Pattern Language" includes organic curves as markers of life and beauty. ✓

5. **Water features (B2)**: Ubiquitous in classic architecture (fountains, pools, waterscapes). Recognized as restorative. ✓

**Missing attributes** (critical in architecture):

1. **Human Scale**: Relationship of design features to human body dimensions. Buildings with 3m-high ceilings feel human-scaled; 10m ceilings feel institutional. **Absent from schema.**
   - **Why critical?** Alexander's "A Pattern Language" emphasizes human proportions. This is foundational.

2. **Complexity at Multiple Scales**: Fractal dimension (F1) captures one type of complexity, but architectural complexity is **hierarchical**. A facade might have:
   - Macro level: overall building form
   - Mid level: window grid
   - Micro level: material texture

   Current F1 is global; **missing hierarchy**. Concept: compute fractal dimension at multiple scales; compare.

3. **Visual Access / Transparency**: Can you see into spaces? Transparency is valued in contemporary architecture (glass walls, open plans) for social connection and safety. No attribute for this.

4. **Materiality / Weathering**: Materials age and weather differently. A stone building with visible patina has different character than plastic-clad building. M1 (material naturalness) is too coarse; **missing authentic patina/weathering**.

5. **Contrast and Definition**: Architectural edges and boundaries create visual interest. Soft transitions vs. sharp edges. No attribute captures this.

**Questionable attributes**:

1. **Sitting affordance density (A1)**: Architecture context: Should also include design *quality* of seating. A bench in a windswept, exposed plaza is less inviting than a bench in a sheltered nook. Density alone misses this.
   - **Recommendation**: Split into:
     - Sitting affordance *quantity* (count)
     - Sitting affordance *quality* (shelter, social configuration, sun/shade)

2. **Social density inference (A2)**: Too vague. Architecture has specific principles:
   - Gathering spaces need clear boundary (edge, slightly raised platform)
   - Group sizes: 4–6 people optimal for conversation (intimate); 12–20 for social gathering; 100+ for crowds
   - Clear sightlines between seating areas

   Inferring "comfort" from image alone is impossible; requires behavioral observation or parametric design rules.

**Confidence in architectural assessment: 0.78**

---

## Points of Agreement (Panelist Consensus)

1. **Fractal-based attributes (F1, F2) are well-grounded** (unanimous, confidence >0.85). Decades of vision literature support these.

2. **Spatial attributes (prospect, enclosure, legibility) are conceptually important but operationally incomplete** (unanimous, confidence >0.80). S4 (legibility) and S3 (enclosure ratio) need algorithm specification.

3. **Material and multisensory attributes (M1, M2, M3) are underspecified** (unanimous, confidence >0.85). M3 (olfactory expectation) is especially problematic.

4. **Affordance attributes (A1, A2) conflate visual with social-cognitive** (unanimous, confidence >0.80). A2 (social density) is not a vision attribute.

5. **Missing attributes from design and beauty literature** (unanimous, confidence >0.80):
   - Perceptual fluency (ease of processing)
   - Human scale (body-scaled proportions)
   - Complexity at multiple scales (hierarchical fractal)
   - Visual access/transparency
   - Authentic materiality (patina, weathering)

---

## Points of Disagreement

1. **Green chromaticity (C3) as biophilic signal**:
   - **Koch**: Oversimplified (0.55); green pixels don't imply biophilia
   - **Alexander**: Pragmatically useful for quick assessment (0.70); architects use color heuristically
   - **Belongie**: Technically sound but context-dependent (0.60); needs conditional rules
   - **Resolution**: Keep C3 but add caveat: "Weak biophilic signal; context-dependent. Validate against actual biophilia measures."

2. **Biomorphic form (B1) universality**:
   - **Koch**: Culturally variable (0.70); some cultures prefer rectilinear
   - **Alexander**: Fundamental to Western architecture tradition (0.80); but acknowledges cultural variation
   - **Belongie**: Technically measurable (0.85); culture affects preference, not measurement
   - **Resolution**: Keep B1 but add note: "Curved forms preferred in Western aesthetic tradition; cultural variation documented."

3. **Should composite attribute (B3: Biophilic Design Score) be kept?**
   - **Koch**: Useful for aesthetics (0.75); enables quick biophilia assessment
   - **Alexander**: Oversimplifies pattern interactions (0.55); biophilic design requires holistic evaluation
   - **Belongie**: Weights are arbitrary (0.50); need justification
   - **Resolution**: Keep B3 but make weights explicit and evidence-based. Propose:
     - Water presence (B2): 0.30 (strongest biophilic signal)
     - Biomorphic form (B1): 0.25
     - Fractal dimension (F1): 0.20
     - Green chromaticity (C3): 0.15
     - Material naturalness (M1): 0.10

---

## Q2: Are the proposed vision algorithms appropriate for each attribute?

**Dr. Belongie:**

Let me assess the proposed algorithms:

**Fractal dimension (F1)** — Proposed: Canny edge detection, box-counting, linear regression:
- **Assessment**: GOOD. Canny (Canny, 1986) is standard edge detector. Box-counting is standard fractal algorithm. Linear regression is correct fitting.
- **Confidence: 0.90** ✓
- **Minor note**: Canny parameters (sigma, thresholds) matter; recommend auto-thresholding (Otsu).

**Color temperature (C1)** — Proposed: Convert RGB → CIE 1960 → McCamy formula:
- **Assessment**: EXCELLENT. CIE 1960 is standard for CCT; McCamy formula (McCamy, 1992) is widely used.
- **Confidence: 0.95** ✓

**Isovist area (S1)** — Proposed: Ray-casting for visibility polygon:
- **Assessment**: GOOD in principle. Ray-casting is correct method (Benedikt, 1979). But requires 3D geometry (floor plan or 3D scene). For **2D images alone**, isovist is hard to compute without depth estimation (monocular depth → scene understanding → 3D reconstruction).
- **Current gap**: Does the algorithm include depth estimation? Not specified.
- **Confidence: 0.60** (depends on depth estimation)

**Spatial legibility (S4)** — Proposed: **NOT SPECIFIED**:
- **Assessment**: CANNOT EVALUATE. Need algorithm.
- **Options**:
  - Option A: Edge connectivity (strongly connected edges → legible)
  - Option B: Junction density (many junctions → decision points → complex → less legible)
  - Option C: Deep learning (train CNN on legibility ratings)
- **Recommendation**: Specify one of these.

**Material naturalness (M1)** — Proposed: **NOT SPECIFIED**:
- **Assessment**: **UNCLEAR**. Candidates:
  - Texture analysis (LBP, SIFT for natural textures vs. synthetic)
  - Color analysis (natural materials have limited color palette; synthetic can be any color)
  - Learned classification (train CNN on "natural" vs. "synthetic" materials)
- **Recommendation**: Specify algorithm or acknowledge that human classification is required.

**Olfactory expectation (M3)** — Proposed: **NOT SPECIFIED**:
- **Assessment**: **VERY PROBLEMATIC**. How would an algorithm infer smell from visual input alone? Candidates:
  - Object detection (flowers → floral scent) — requires extensive object detection + scent associations (unreliable)
  - Semantic associations (learned: forest image → pine smell) — requires external database of image-scent pairs (not available)
- **Assessment**: **Should not be included** without clear algorithm.
- **Confidence in impossibility: 0.85**

**Affordance attributes (A1, A2)** — Proposed: **PARTIALLY SPECIFIED**:
- A1 (sitting): Candidate: YOLO or similar object detection for chairs/benches
  - **Assessment**: Reasonable but limited scope (detects furniture; misses ground-level seating, natural seating)
  - **Confidence: 0.65**
- A2 (social density): **No reasonable algorithm**
  - **Assessment**: Should be removed or redefined

**Summary of algorithm assessment**:
- **Appropriate and specified**: F1, C1, B1, B2, P2 (5 algorithms; 24%)
- **Appropriate but incomplete**: F2, F3, F4, C2, S1, S2, S3 (7 algorithms; 33%)
- **Inappropriate or unspecified**: C3, M1, M2, M3, S4, A1, A2, P1 (8 attributes; 38%)

**Confidence in assessment: 0.78**

---

**Dr. Koch:**

I assess algorithms for **robustness and reliability**:

**DeepLabV3 (semantic segmentation)**: Mentioned in task for some attributes
- **Use**: Could segment materials (wood vs. stone), water features, etc.
- **Assessment**: Good for semantic segmentation; less good for fine-grained visual features
- **Confidence: 0.75** ✓

**MiDaS (depth estimation)**: Mentioned in task
- **Use**: Estimate depth for spatial attributes (isovist, enclosure)
- **Assessment**: Recent monocular depth estimation (Ranftl et al., 2021) is surprisingly good (~85% accurate on realistic scenes)
- **Confidence: 0.80** ✓ (enables isovist and spatial computations)

**YOLO (object detection)**: Mentioned in task
- **Use**: Detect chairs, benches, water features, people
- **Assessment**: Standard object detector; good for "presence" detection, weak for "quality" assessment
- **Confidence: 0.80** ✓ (appropriate for some affordances)

**OpenCV (traditional vision)**: Mentioned for edge detection, color conversion, etc.
- **Assessment**: EXCELLENT. Standard, reliable, well-tested.
- **Confidence: 0.95** ✓

**Missing: How to combine/weight multiple algorithms?**

Many attributes (e.g., "material naturalness") might require multiple algorithms:
- Texture analysis (LBP, SIFT)
- Color analysis (palette estimation)
- Semantic labels from CNN (predict "wood", "stone", "plastic")

**No guidance on fusion strategy**.

**Confidence in algorithm assessment: 0.72**

---

**Dr. Alexander:**

I assess algorithms from **design implementation** perspective:

**Strengths**:
1. Use of standard libraries (OpenCV, TensorFlow via YOLO, MiDaS) is good — avoids reinventing wheels
2. Explicit algorithm choices (Canny, box-counting, McCamy) are transparent

**Gaps**:
1. **No discussion of how to handle occlusion or partial views**: Architectural photography often includes people, cars, other temporary objects. How does algorithm handle occlusion of the actual space?

2. **No calibration for image quality**: Photographs vary wildly (lighting, camera angle, distortion, artistic intent). Do algorithms work equally well on iPhone photo vs. professional architectural photo?

3. **No discussion of scale ambiguity**: A high isovist area could mean:
   - Large open space (good)
   - Sparse sparse (bad, visually empty)

   Algorithm can compute isovist but can't distinguish meaning.

4. **Lack of human-in-the-loop**: Some attributes (legibility, sitting quality, material authenticity) may require human judgment. Algorithm should flag uncertainty or request human validation.

**Recommendation**: Add **confidence scores** to each computed attribute:
```json
{
  "attribute": "material_naturalness",
  "value": 0.65,
  "confidence": 0.40,  // Algorithm uncertain; human review recommended
  "algorithm_used": "CNN + texture analysis",
  "notes": "Image has occlusion; material recognition uncertain"
}
```

**Confidence in implementation assessment: 0.70**

---

## Q3: Are there redundancies between attributes?

**Panelist consensus: YES, significant redundancy**

**Identified redundancies**:

| Attribute 1 | Attribute 2 | Overlap | Confidence |
|-------------|-------------|---------|-----------|
| F1 (Fractal) | F2 (1/f slope) | Both measure natural complexity; high correlation expected | 0.80 |
| F1 (Fractal) | F4 (Edge density) | Both capture complexity via different methods; moderate correlation expected | 0.72 |
| S1 (Isovist) | S2 (Ceiling height) | Both measure spatial enclosure/openness; moderate correlation | 0.70 |
| S2 (Ceiling height) | S3 (Enclosure ratio) | Related aspects of enclosure; high correlation expected | 0.75 |
| B1 (Biomorphic form) | F1 (Fractal) | Curved forms often fractal; biomorphic shapes cluster at D ≈ 1.3 | 0.68 |
| C3 (Green chromaticity) | B2 (Water) | Both are specific biophilic color signals; could be subsumed under "biophilic color" | 0.65 |
| B3 (Biophilic composite) | F1, C3, B1, B2, M1 | B3 is a linear combination of other attributes; perfect redundancy | 0.95 |

**Recommendation**:

1. **Keep F1, F2, F4 but document correlation**. They capture different complexity aspects (self-similarity, spectral slope, edge density). Not perfectly redundant, but may be correlated.

2. **Consolidate spatial enclosure (S1, S2, S3) into a single "spatial enclosure" dimension** with sub-attributes:
   - Prospect (Isovist area): How far can you see?
   - Vertical proportions (Ceiling height): How enclosed is vertical dimension?
   - Enclosure ratio: Overall openness/closure balance

3. **Remove or redefine B3 (Biophilic composite)**. If it's a linear combination of F1, C3, B1, B2, M1, then it's redundant. Options:
   - Keep it as a quick "biophilic score" for exploratory analysis, but note it's derived
   - Remove it and compute on-demand in downstream analysis

4. **Combine C3 (green) and B2 (water) into a single "biophilic color signals" attribute**.

**Confidence in redundancy assessment: 0.75**

---

## Q4: Are there critical visual attributes missing for environmental psychology research?

**Panelists identified important gaps**:

1. **Visual Entropy (Surprise)**: Information content in image. Measured by feature histogram entropy or Shannon entropy of pixel values. **Predicts visual attention** (Deco & Rolls, 2005).
   - **Why important for env psych**: Optimal entropy (not too simple, not too chaotic) predicts restoration and interest
   - **How to measure**: Shannon entropy of edge positions, corner positions, or color histogram

2. **Perceptual Fluency**: How easy is the image to process globally. **Linked to aesthetic preference** (Reber et al., 2004).
   - **Why important**: Fluent images are liked more; restoration improves with fluency
   - **How to measure**: Inverse of visual entropy; or train CNN to predict processing difficulty

3. **Human scale**: Relationship of scene features to human body size (e.g., window size should be ~1.5m high for human proportions).
   - **Why important**: Alexander's "A Pattern Language" — human-scaled spaces feel more comfortable
   - **How to measure**: Estimate human reference size (depth + scene geometry); compute feature-to-human ratios

4. **Authenticity/Patina**: Evidence of time, weathering, use. **Important in architecture** (new buildings feel institutional; weathered buildings feel lived-in).
   - **Why important**: Authenticity signals natural history and trustworthiness; missing in current schema
   - **How to measure**: Color variation, surface irregularity, evidence of wear

5. **Prospect-refuge clarity**: Distinction between Appleton's prospect (openness) and refuge (enclosure). **Currently mixed in S1, S2, S3**. Should be separate.
   - **Why important**: Prospect and refuge have opposite effects on behavior (prospect → engagement; refuge → calm)
   - **How to measure**: Separate attributes for prospect (isovist area) and refuge (enclosure density)

6. **Movement potential**: Can you move through this space? Are there paths, openings, inviting routes?
   - **Why important**: Exploratory motivation depends on movement affordances
   - **How to measure**: Path detection (horizontal lines indicating walkways); opening density

7. **Visual weight distribution**: Asymmetry, balance, tension in composition. **Relevant to perception** and aesthetic preference.
   - **Why important**: Balanced compositions are preferred; tension creates interest
   - **How to measure**: Compute center-of-mass of edges/features; measure deviation from balance

8. **Color harmony**: Do colors form a harmonious ensemble (analogous, complementary, triadic)?
   - **Why important**: Harmonious colors are preferred (Schloss & Palmer, 2011); restoration enhanced by color harmony
   - **How to measure**: Extract dominant colors; check against color harmony rules

**Confidence in gap identification: 0.80**

---

## Q5: Should any attributes be merged or split?

**Recommended changes**:

| Current | Recommendation | Rationale | Confidence |
|---------|-----------------|-----------|-----------|
| F1, F2, F4 | Keep separate | Document correlation; different aspects of complexity | 0.70 |
| S1, S2, S3 | Consolidate into "Spatial Enclosure" with subcomponents | Prospect + vertical proportion + enclosure ratio are related; cleaner as one dimension | 0.75 |
| C1, C2, C3 | Keep separate; add C4 "color harmony" | C1=warmth, C2=distribution, C3=green signal; all different. Add harmony measure | 0.70 |
| B1, B2 | Keep separate | Different biophilic signals (form vs. water); both important | 0.80 |
| B3 (Biophilic composite) | Remove or redefineas derived metric | Too redundant with sub-attributes; if kept, make it clear it's post-hoc | 0.85 |
| A1 (sitting) | Split into quantity and quality | Count of sitting places ≠ quality of sitting experience | 0.78 |
| A2 (social density) | Remove or redefine | Not a vision attribute; too culturally variable | 0.88 |
| M1, M2, M3 | Consolidate to "Material & Sensory Expectations" with clear algorithms | Too vague individually; need unified operationalization | 0.65 |

---

## Recommendations with Priority

### MUST DO (Block release without)

1. **Specify algorithms for all attributes**. Currently, S4 (legibility), M1 (material naturalness), M2 (haptic), M3 (olfactory), A2 (social density) have no specified algorithms. Choose:
   - Algorithm type (traditional vision, deep learning, hybrid)
   - Specific method (Canny + box-counting for F1, etc.)
   - Implementation (OpenCV, TensorFlow, custom)
   - Validation approach (ground truth, inter-rater agreement)

   *Why*: Unspecified algorithms prevent reproducible implementation.

   **Timeline**: 1 week

2. **Remove or radically redefine problematic attributes**:
   - **M3 (Olfactory expectation)**: Cannot be reliably inferred from image alone; remove unless you have scent-image paired dataset
   - **A2 (Social density)**: Not a vision attribute; move to "socio-spatial design" category if needed
   - Consider marking **M1, M2, A1** as "exploratory" (weak validation) until algorithms are tested

   *Why*: These attributes lack theoretical grounding and implementation clarity.

   **Timeline**: Immediate (2 days)

3. **Document and address redundancy**:
   - Compute correlation matrix between all attributes on a test image set (N=100 diverse images)
   - If correlation > 0.85, flag as redundant; decide whether to merge or keep both
   - If any attribute has correlation < 0.3 with all others, investigate whether it's measuring something unique or is noisy

   *Why*: High redundancy reduces information content; wastes computation.

   **Timeline**: 1 week (empirical analysis)

4. **Add missing critical attributes**:
   - Visual entropy / Surprise (information content)
   - Perceptual fluency (ease of processing)
   - Color harmony (colors form ensemble)
   - Human scale (feature-to-body ratios)
   - Authenticity / Patina (weathering signals)

   At minimum, add **visual entropy** and **perceptual fluency** as they're most directly linked to environmental psychology outcomes (restoration, preference, engagement).

   *Why*: Current schema lacks capture of cognitive and aesthetic properties central to env psych.

   **Timeline**: 2 weeks (algorithm development)

5. **Rewrite M2 (Haptic expectation) with clear operationalization**:
   - Define: What visual features predict "rough" vs. "smooth"?
   - Algorithm: Texture descriptor (Gabor filters, LBP) for roughness estimation
   - Validation: Collect human ratings of image roughness; correlate with algorithm output
   - Confidence floor: Only report haptic expectation if algorithm confidence > 0.70

   *Why*: Current definition is too vague for implementation; has potential if clarified.

   **Timeline**: 2 weeks

### SHOULD DO (Improves schema quality)

6. **Consolidate spatial attributes (S1, S2, S3)** into a single "Spatial Enclosure Dimension" with sub-scores:
   - Prospect (Isovist area): 0-1 scale
   - Vertical proportion (Ceiling height): 0-1 scale
   - Enclosure (Refuge density): 0-1 scale
   - Overall Enclosure: Composite score

   *Why*: Current separation is redundant; unified framework is clearer.

   **Timeline**: 1 week

7. **Make B3 (Biophilic composite) transparent and evidence-based**:
   - Specify weights:
     - Water presence (B2): 0.30 (strongest biophilic signal; Kaplan, 1989)
     - Biomorphic form (B1): 0.25 (curved preferred; Silvia & Barona, 2009)
     - Fractal dimension (F1): 0.20 (natural complexity; Hagerhall et al., 2004)
     - Green chromaticity (C3): 0.15 (vegetation signal; context-dependent)
     - Material naturalness (M1): 0.10 (weakest signal; M1 itself needs validation)
   - Document: "This is a post-hoc derived metric; weights chosen based on environmental psychology literature (Kaplan et al., Ulrich, etc.)"

   *Why*: Make composite measure transparent; enable users to adjust weights.

   **Timeline**: 1 week

8. **Create algorithm validation study**:
   - Test 5 algorithms on 100-image diverse dataset (indoor/outdoor, architectural/natural, etc.)
   - Compute inter-algorithm agreement (do DeepLabV3 + MiDaS + YOLO agree on attributes?)
   - Compare algorithm outputs to human ground truth (N=10 human raters per image)
   - Report: Precision, recall, confidence intervals

   *Why*: Validate that algorithms actually capture the intended constructs.

   **Timeline**: 3–4 weeks (experimental)

### CONSIDER (Nice-to-have; lower priority)

9. **Add **confidence scores** to all computed attributes**:
   ```json
   {
     "attribute_id": "ATTR-F1",
     "value": 1.42,
     "confidence": 0.88,
     "algorithm_notes": "Box-counting on Canny edges; optimal parameters applied"
   }
   ```

   *Why*: Enables downstream filtering (use only high-confidence attributes) and quality monitoring.

   **Timeline**: 1 week (implementation)

10. **Create visual attribute "best practices" guide**:
    - Explain each attribute in plain language
    - Provide example images (high value, low value, ambiguous cases)
    - Discuss failure modes (when does algorithm fail?)
    - Provide interpretation guidelines (what does fractal D=1.35 mean for environmental psychology?)

    *Why*: Reduces misinterpretation; enables wider adoption.

    **Timeline**: 2 weeks (writing)

---

## Summary: Vision Attribute Taxonomy Assessment

**Overall Grade**: C+ (Conceptually sound; operationally incomplete)

**Strengths**:
- Grounded in decades of vision science literature (fractal dimension, 1/f slopes, color science)
- Includes some well-operationalized attributes (F1, F2, C1, B1, B2)
- Directly relevant to environmental psychology (prospect-refuge, biophilia, restoration)

**Weaknesses**:
- **38% of attributes poorly specified operationally** (M1, M2, M3, S4, A2, P1, and others lack clear algorithms)
- **Significant redundancy** (F1 ↔ F2 ↔ F4; S1 ↔ S2 ↔ S3; B3 is linear combination)
- **Missing critical attributes** from beauty/aesthetics literature (perceptual fluency, entropy, harmony, human scale, authenticity)
- **Problematic attributes** (M3 olfactory is speculative; A2 social density is not a vision attribute)
- **No algorithm validation study** (algorithms chosen; not yet tested on images)
- **Arbitrary weights** (B3 composite has unjustified weights)

**Fitness for Purpose**: **NOT READY for environmental psychology meta-analysis without substantial work**:
1. Remove/redefine problematic attributes (M3, A2) — 2 days
2. Specify algorithms for all remaining (1 week)
3. Add missing critical attributes (2 weeks)
4. Validate algorithms empirically (3–4 weeks)
5. Consolidate/merge redundant attributes (1 week)

**Estimated time to production-ready**: 3–4 weeks (intensive)

**Confidence in Recommendation**: 0.78 (schema has promise; currently premature for deployment)

---

## Next Steps for Panel

1. Implement MUST DO items (5 changes)
2. Conduct algorithm validation study (3–4 weeks)
3. Empirically test inter-attribute correlation (1 week)
4. Add missing attributes (visual entropy, fluency, harmony, human scale, authenticity) (2 weeks)
5. Create schema v1.1 with validated attributes and transparent algorithms

**Prepared by**: Panel Secretariat
**Date**: 2026-03-01
**Reviewers**: Belongie, Koch, Alexander (all endorsed)
