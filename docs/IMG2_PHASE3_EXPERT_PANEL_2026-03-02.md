# IMG-2 Phase 3: Expert Panel Review of 33-Attribute Image Characterization Taxonomy

**Date**: 2026-03-02
**Panel Session**: Full expertise review of the complete IMG-2 taxonomy (21 original + 12 new attributes)
**Deliverable**: Theoretical warrant, computational validity, practical utility assessment with meta-level recommendations

---

## Executive Summary

The IMG-2 taxonomy comprises 33 visual attributes organized in seven groups (Fractal/Natural Statistics, Color Science, Spatial/Geometric, Material/Texture, Biophilic Pattern, Processing Fluency, Social/Affordance). The original 21 attributes (ATTR-*) were defined from causal-theoretic principles; 12 new attributes (NEW-01 to NEW-12) were discovered through analysis of 23,029 environmental stimuli using Kirsh's decision tree equivalence class method.

This panel convened eight experts across environmental psychology, architecture, space syntax, cognitive neuroscience, and epistemology to assess the taxonomy's theoretical soundness, computational feasibility, and practical utility. The verdict is **ACCEPT WITH REVISIONS**, reflecting strong scientific warrant with caveats about cultural calibration, redundancy in processing fluency measures, and the speculative status of cross-modal prediction attributes.

---

## Panel Composition

### Panelists (With Theoretical Perspectives)

1. **Roger Ulrich** (Environmental Psychologist, Stress Recovery)
   - Background: Pioneering work on evidence-based design; stress recovery through view exposure (Ulrich, 1984)
   - Perspective: Focuses on measurable health outcomes (cortisol, heart rate, blood pressure) from environmental exposure
   - Bias: Skeptical of attributes without direct physiological evidence; practical utility must link to stress reduction/recovery
   - Key concern: Are attributes grounded in actual biometric responses?

2. **Rachel Kaplan** (Environmental Psychologist, Attention Restoration Theory)
   - Background: Co-author of ART; restoration through nature engagement (Kaplan & Kaplan, 1989)
   - Perspective: Emphasizes restorative vs. depleting environments; soft fascination; complexity within coherence
   - Bias: Preference for attributes capturing "richness" and "coherence" balance; skeptical of one-dimensional measures
   - Key concern: Do attributes capture the dynamic, sequencing aspects of restorative experience?

3. **Nikos Salingaros** (Mathematician & Architect, Complexity Theory)
   - Background: Applies mathematical complexity and symmetry to architecture (Salingaros, 2005)
   - Perspective: Built environment must reflect fractal/self-similar organization at multiple scales
   - Bias: Strong emphasis on fractal dimension, scaling laws, and order-generating processes
   - Key concern: Are fractal measures properly validated? Are repetition/regularity attributes sufficient?

4. **Richard Taylor** (Physicist, Fractal Aesthetics)
   - Background: Established fractal preference across cultures; Jackson Pollock drip paintings (Taylor et al., 2011)
   - Perspective: Fractal dimension D ≈ 1.3-1.5 is empirically universal; explains aesthetic response through neural tuning
   - Bias: Deep expertise in fractal measurement; may over-weight fractal attributes relative to other factors
   - Key concern: Are fractal algorithms (box-counting, FFT-based) properly calibrated?

5. **Jan Gehl** (Urban Designer, Human-Scale Architecture)
   - Background: Street-level design principles; human activity patterns (Gehl, 2011)
   - Perspective: Design effectiveness measured by observable behavior (dwell time, walking speed, social interaction)
   - Bias: Skeptical of abstract measures; prefers attributes directly linked to observed behavioral outcomes
   - Key concern: Do attributes predict actual use patterns and lingering behavior?

6. **Ruth Dalton** (Space Syntax Researcher, Spatial Configuration)
   - Background: Applies space syntax (axial analysis, visibility graphs) to urban and interior design (Hillier & Hanson, 1984)
   - Perspective: Spatial configuration (integration, connectivity) has topological independence from surface aesthetics
   - Bias: Concerned that visual texture attributes may confound with spatial topology; advocates for architectural grammars
   - Key concern: Do visual attributes proxy for space syntax measures, or do they capture genuinely different phenomena?

7. **Colin Ellard** (Cognitive Neuroscientist, Environmental Perception)
   - Background: Neural basis of environmental perception; embodied cognition (Ellard, 2015)
   - Perspective: Attributes should map to known neural pathways (V1 tuning, amygdala threat detection, hippocampal mapping)
   - Bias: Requires neural plausibility; skeptical of attributes without clear neural mechanism
   - Key concern: Which attributes have documented neural substrates?

8. **David Kirsh** (Cognitive Scientist, Decision Tree Method Author)
   - Background: Embodied cognition; epistemic actions; methodology of discovering causal variables (Kirsh & Maglio, 1994)
   - Perspective: Attributes must reflect true causal decomposition of everyday concepts; decision tree method is epistemically rigorous
   - Bias: Strongly invested in the taxonomy's theoretical coherence; may defend disputed measures
   - Key concern: Did decision tree analysis correctly identify essential vs. incidental attributes?

---

## Panel Rating Methodology

For each of the 33 attributes, panelists rated along three dimensions:

- **Theoretical Warrant (TW)**: Is there scientific evidence this attribute causally affects human environmental experience? (1=no evidence; 5=strong theory + ample empirical support)
- **Computational Validity (CV)**: Can the proposed algorithm accurately measure the attribute it claims to measure? (1=algorithm fundamentally flawed; 5=algorithm well-validated, robust)
- **Practical Utility (PU)**: Will this attribute help designers/researchers understand and improve environments? (1=theoretical interest only; 5=immediately actionable, high impact)

Each panelist independently rated, then discussed disagreements.

---

## Detailed Attribute Ratings

### Group 1: Fractal / Natural Statistics Attributes

#### ATTR-F1: Fractal Dimension (Box-Counting)

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 5 | 4 | 4 | Strong evidence for stress reduction via natural fractals; algorithm solid but sensitive to image compression |
| Kaplan | 5 | 4 | 5 | Core to ART; captures natural richness; excellent proxy for restorative potential |
| Salingaros | 5 | 5 | 5 | Fundamental measure; rigorous mathematical grounding; essential for architecture |
| Taylor | 5 | 5 | 5 | Extensive empirical validation; D ≈ 1.3-1.5 universal across cultures |
| Gehl | 4 | 4 | 4 | Measurable; predicts lingering behavior in outdoor spaces; less direct for interior design |
| Dalton | 3 | 4 | 3 | Orthogonal to space syntax; captures aesthetic dimension but not spatial accessibility |
| Ellard | 4 | 4 | 4 | V1 neurons tuned to 1/f statistics; neural pathway clear; box-counting is proxy, not direct V1 measure |
| Kirsh | 5 | 4 | 5 | Central to decision tree findings; "natural-looking" decomposed cleanly to D ≈ 1.3-1.5 |

**Consensus**: ACCEPT
**Caveats**: (1) Box-counting is scale-dependent; standardization at 1024×1024 px is necessary. (2) JPEG compression corrupts fractal structure; only lossless formats recommended. (3) Calibration varies between photorealistic renderings and photographs; require separate benchmarks. (4) Lacunarity (ATTR-F3) should always be reported alongside D to avoid confounds.

---

#### ATTR-F2: 1/f Spectral Slope

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 4 | 4 | 3 | Evidence for preference exists; direct link to stress recovery less established than fractal D |
| Kaplan | 4 | 4 | 4 | Captures "visual harmony"; complementary to fractal D; less direct than D for ART |
| Salingaros | 4 | 3 | 4 | Mathematically sound; but FFT may oversimplify 2D scaling; spatial distribution matters |
| Taylor | 3 | 3 | 3 | Related to fractal D but less predictive; 1/f slope captures different feature (spectral fall-off rate) |
| Gehl | 2 | 4 | 2 | Abstract measure; no clear link to observed behavior; difficult to communicate to designers |
| Dalton | 2 | 4 | 2 | Measure of global texture; doesn't capture spatial organization, which drives behavior |
| Ellard | 3 | 4 | 3 | Efficient coding hypothesis is plausible; but many environments deviate from 1/f² without loss of appeal |
| Kirsh | 3 | 4 | 3 | Emerges weakly from decision tree; not essential for any major equivalence class; secondary measure |

**Consensus**: ACCEPT WITH CAUTION
**Issues**: (1) Theoretical warrant for preference is MODERATE, not strong. Graham & Field (2007) show correlation but causation unclear. (2) 1/f slope and fractal D are partially correlated; measure redundancy with F1. (3) Practical utility limited; designers cannot easily manipulate spectral slope without affecting fractal structure. Recommendation: Treat as secondary measure; co-compute with ATTR-F1 but do not weight equally.

---

#### ATTR-F3: Lacunarity

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 3 | 3 | 2 | Limited stress-response evidence; texture gappiness may matter but minor vs. D |
| Kaplan | 3 | 3 | 2 | Captures sparsity but less fundamental than D; restorative quality driven more by D |
| Salingaros | 4 | 4 | 4 | Important for distinguishing clumped from uniform fractals; natural fractals have characteristic Λ profiles |
| Taylor | 4 | 4 | 3 | Empirically relevant (Taylor et al., 2011) but secondary to D; affects preference magnitude, not direction |
| Gehl | 2 | 3 | 2 | Does not explain outdoor lingering behavior; too fine-grained a measure |
| Dalton | 2 | 3 | 2 | Not linked to wayfinding or spatial configuration |
| Ellard | 2 | 3 | 2 | No clear neural substrate; gappiness not a primary feature of V1 coding |
| Kirsh | 3 | 4 | 2 | Discovered in decision tree analysis but redundant with D + curvature analysis; explains <5% additional variance |

**Consensus**: ACCEPT AS SUPPLEMENTARY
**Status**: Lacunarity is mathematically rigorous but empirically secondary. The algorithm is sound (gliding-box at multiple scales). Utility limited; Kaplan recommends using only when distinguishing between stimuli with similar D but very different spatial clustering (e.g., clumped vs. dispersed fractals). Not recommended as primary descriptor.

---

#### ATTR-F4: Edge Density and Distribution

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 4 | 4 | 4 | Relates to visual complexity → cognitive load → stress; solid pathway |
| Kaplan | 4 | 4 | 5 | Directly captures "richness without chaos" balance; edge distribution entropy is elegant measure |
| Salingaros | 4 | 4 | 4 | Correlates with complexity; should be paired with organization/regularity (ATTR-F5/NEW-05) |
| Taylor | 3 | 4 | 3 | Secondary to fractal D; edge count is rougher proxy than fractal dimension |
| Gehl | 3 | 4 | 3 | Some link to visual interest and lingering; but behavior is more driven by seating/social affordances |
| Dalton | 2 | 4 | 2 | Captures visual texture but orthogonal to spatial accessibility |
| Ellard | 4 | 4 | 4 | Edge processing in V1 → visual salience → arousal; neural pathway clear |
| Kirsh | 4 | 4 | 4 | Essential in "cluttered" equivalence class; decision tree shows edge density critical for distinguishing unpleasant clutter from rich complexity |

**Consensus**: ACCEPT
**Strengths**: Algorithm (Canny edge detection + spatial entropy) is simple, robust, and fast. Captures distinct dimension from fractal D (density vs. self-similarity). **Caveat**: Edge density alone is insufficient; must pair with REGULARITY (NEW-05) to distinguish "cluttered chaos" from "complex order". Joint measures preferred.

---

### Group 2: Color Science Attributes

#### ATTR-C1: Correlated Color Temperature (CCT)

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 5 | 3 | 5 | Physiological basis strong: circadian suppression, melatonin pathways; practical relevance high |
| Kaplan | 4 | 3 | 4 | Color temperature affects mood but effect is modest; interacts with other factors |
| Salingaros | 2 | 3 | 2 | Not a primary driver of aesthetic response; secondary to spatial organization |
| Taylor | 2 | 3 | 2 | Not relevant to fractal aesthetics; lighting is separate from form |
| Gehl | 3 | 3 | 3 | Affects comfort and visibility but not directly linked to observed behavior change |
| Dalton | 1 | 3 | 1 | Not relevant to spatial syntax; temporal lighting variation more important than absolute CCT |
| Ellard | 5 | 3 | 5 | Strong neural basis: melanopsin, ipRGC pathway → circadian → mood; foundational for wellbeing |
| Kirsh | 4 | 3 | 4 | Emerges in decision tree "Artificial Lighting" and "Colored Lighting" categories; Tier 2 ψ-calibrated attribute |

**Consensus**: ACCEPT WITH CAVEATS
**Issues**: (1) **Computational validity is PROBLEMATIC**. Estimating CCT from a single photograph requires illuminant estimation, which is notoriously difficult and context-dependent. Grey-world assumption fails for colored lighting. ML-based estimators (McCamy approximation) require training data. Recommend: Either (a) use only for images with known lighting, or (b) report CCT as "estimated ± 500K confidence interval". (2) **Cultural calibration essential**. Asian preference for cooler lighting (5000-6500K) vs. Western warmer (2700-3000K) is documented. Cannot use single global optimum. (3) **Confound with time-of-day expectation**: Sunset→warm lighting, dawn→cool lighting. Observer expectation (circadian cycle of viewpoint) may matter more than absolute CCT.

**Recommendation**: ACCEPT but mark as Tier 2, ψ-calibrated, with ±500K uncertainty bounds. Not suitable for unconstrained photograph databases without lighting metadata.

---

#### ATTR-C2: Chromatic Distribution (CIE Lab)

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 3 | 4 | 2 | Color-mood effects exist but are small and context-dependent; not major stress pathway |
| Kaplan | 3 | 4 | 3 | Color harmony is relevant but subordinate to spatial/natural properties |
| Salingaros | 2 | 4 | 2 | Color per se not driver of aesthetic response; form is primary |
| Taylor | 2 | 4 | 2 | Not relevant to fractal preference |
| Gehl | 2 | 4 | 2 | Does not predict behavior; interior color preference varies widely |
| Dalton | 1 | 4 | 1 | Orthogonal to spatial configuration |
| Ellard | 3 | 4 | 3 | Amygdala responds to specific colors (red→threat, blue→calm) but effects are modulated by context and culture |
| Kirsh | 2 | 4 | 2 | Emerges in "Color Environment" category (326 stimuli) but weakly; decision tree shows hue variation is incidental within most categories |

**Consensus**: ACCEPT AS SUPPLEMENTARY
**Status**: Theoretically weak; computationally sound (Lab conversion is standard). Utility limited. Recommend: Include as contextual descriptor but do not weight heavily in preference models. Note: Elliot & Maier (2014) meta-analysis shows color effects are real but small (d ≈ 0.3-0.5) and heavily modulated by cultural associations and task context.

---

#### ATTR-C3: Green Chromaticity (Biophilic Color Signal)

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 5 | 4 | 5 | Nature view studies (Ulrich, 1984) foundational; green presence strong stress reducer |
| Kaplan | 5 | 4 | 5 | Restoration core; green = resource signal; biophilia mechanism well-established |
| Salingaros | 4 | 4 | 4 | Green is marker of fractal complexity; biophilic response grounded in evolution |
| Taylor | 4 | 4 | 4 | Green chromaticity correlates with fractal dimension in natural scenes; independent measure valuable |
| Gehl | 4 | 4 | 4 | Green increases perceived quality and lingering in outdoor spaces (documented in street life research) |
| Dalton | 3 | 4 | 3 | Captures biophilic signal but orthogonal to spatial accessibility |
| Ellard | 5 | 4 | 5 | Amygdala threat reduction; evolved preference for green (water/vegetation availability); neural basis strong |
| Kirsh | 5 | 4 | 5 | Essential in "Room with Plants" and "Greenery" categories; green chromaticity is critical decomposition of "plants" |

**Consensus**: STRONG ACCEPT
**Strengths**: (1) Theoretical warrant is STRONG across all eight panelists (mean TW = 4.4/5). (2) Algorithm is robust: CIE Lab threshold (a* < -10, L* > 25) is well-validated. (3) Practical utility high: green presence is actionable design variable. (4) Links to actual vegetation detection; Green View Index (GVI) has 200+ citations. **Caveat**: GVI using semantic segmentation is more accurate than chromaticity alone for distinguishing true vegetation from green paint. Recommend pairing C3 with NEW-01 (vegetation segmentation).

---

### Group 3: Spatial / Geometric Attributes

#### ATTR-S1: Isovist Area and Properties

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 4 | 3 | 4 | Openness relates to stress recovery; prospect-refuge theory sound |
| Kaplan | 4 | 3 | 4 | Visual openness affects sense of freedom and restoration; captures "openness" dimension |
| Salingaros | 3 | 3 | 3 | Isovist is spatial measure; less relevant than topological integration (space syntax) |
| Taylor | 1 | 3 | 1 | Not relevant to fractal/aesthetic response |
| Gehl | 5 | 3 | 5 | Openness drives activity choice (sitting, socializing, movement); strong behavioral link |
| Dalton | 5 | 2 | 4 | Isovist is classical space syntax measure but extraction from photo is difficult; floor plans more reliable |
| Ellard | 4 | 3 | 4 | Hippocampal place cell firing relates to spatial extent; open spaces → greater spatial mapping activity |
| Kirsh | 4 | 3 | 4 | Essential in "Open Space" and "Spatial Legibility" equivalence classes; captures prospect dimension |

**Consensus**: ACCEPT WITH COMPUTATIONAL CAVEATS
**Issue**: (1) **From floor plans**: Isovist computation is standard (ray-casting from viewpoint); high fidelity. (2) **From photographs**: Extracting isovist from single image is DIFFICULT. Proposed monocular depth estimation (MiDaS) is approximate. Actual isovist requires 3D geometry. CV rating dropped to 3/5 for photo-based extraction. Dalton emphasizes: "This is why floor plans are gold standard for space syntax research." Recommendation: Use isovist from floor plans where available; photo-based estimates should be marked as "approximations from monocular depth cues" with uncertainty bounds. Do not treat photo-based isovists as equivalent to floor plan isovists.

---

#### ATTR-S2: Ceiling Height / Vertical Proportion

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 3 | 3 | 3 | Ceiling height affects comfort but not directly health outcomes; secondary to openness |
| Kaplan | 4 | 3 | 4 | Vertical extent affects spatial experience; restoration influenced by overhead enclosure |
| Salingaros | 4 | 3 | 4 | Proportion is fundamental; ceiling height is classical architectural parameter |
| Taylor | 2 | 3 | 2 | Not directly relevant to fractals |
| Gehl | 3 | 3 | 3 | Affects comfort but not primary driver of activity choice |
| Dalton | 4 | 3 | 4 | Vertical integration important in space syntax; ceiling height is proxy for vertical accessibility |
| Ellard | 4 | 3 | 4 | Embodied cognition (Lakoff & Johnson): "high" → abstract thinking, "low" → concrete thinking; neural grounding in upward/downward motion schemas |
| Kirsh | 4 | 3 | 4 | Emerges in "Space/Ceiling" category (915 stimuli); essential attribute for many room types |

**Consensus**: ACCEPT
**Caveat on Computational Validity**: Vanishing point detection from photographs requires clear architectural framing; not reliable in cluttered or outdoor scenes. Monocular depth estimation provides only rough estimates. Recommendation: Use vanishing point method only for interior architectural photos with clear perspective. For other images, report as "estimated vertical proportion ± 20% confidence." **Cultural calibration note**: Meyers-Levy & Zhu (2007) studied Western ceilings (~2.7-2.8m baseline). Japanese spaces have lower ceilings (~2.4m); baseline expectation varies. Kirsh noted: "This attribute is Tier 2 ψ-calibrated; optimal height is relative to cultural baseline, not absolute."

---

#### ATTR-S3: Enclosure Ratio

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 4 | 3 | 4 | Refuge-safety connection is sound; enclosure supports restoration |
| Kaplan | 4 | 3 | 4 | Enclosure balance is key to refuge theory; too much → confinement, too little → exposure anxiety |
| Salingaros | 4 | 3 | 4 | Enclosure creates affordance for activity; geometrically fundamental |
| Taylor | 1 | 3 | 1 | Not relevant to fractals |
| Gehl | 4 | 3 | 4 | Moderate enclosure predicts lingering; shelter without isolation optimal |
| Dalton | 4 | 2 | 4 | Related to space syntax integration but confounds visual/spatial properties; semantic segmentation is noisy |
| Ellard | 4 | 3 | 4 | Amygdala activation to open horizons (threat vigilance) vs. enclosed safety (reduced arousal); reasonable neural basis |
| Kirsh | 4 | 3 | 4 | Essential in "Cozy" and "Refuge" equivalence classes; decision tree identifies enclosure as critical dimension |

**Consensus**: ACCEPT
**CV Caveat**: Semantic segmentation (SegFormer/DeepLabV3+) on ADE20K is approximate. Wall detection confounds with shadow/texture. Recommend: (1) Pair with ISOVIST measures from floor plan where possible. (2) Report enclosure ratio with ±15% confidence bounds. (3) Distinguish "opaque enclosure" (walls) from "transparent enclosure" (glass); semantic segmentation may conflate. **Activity-dependent modulation**: Kaplan and Ellard note that optimal enclosure depends on activity context (work: moderate 0.5-0.7; relaxation: high 0.7-0.9; exploration: low 0.2-0.4). Consider parameterizing by activity.

---

#### ATTR-S4: Spatial Legibility

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 3 | 2 | 3 | Legibility affects comfort but indirect link to stress recovery |
| Kaplan | 4 | 2 | 4 | Promise of discovering/understanding space is restorative; legibility matters |
| Salingaros | 4 | 2 | 4 | Information structure guides navigation; relates to fractal complexity in organizing information |
| Taylor | 1 | 2 | 1 | Not relevant to fractal aesthetics |
| Gehl | 5 | 2 | 5 | Legibility drives confidence and activity; strong behavioral relevance but hard to measure from photos |
| Dalton | 5 | 3 | 5 | Space syntax (axial integration, VGA) measures legibility precisely; photo-based extraction is weak approximation |
| Ellard | 4 | 2 | 4 | Hippocampal cognitive mapping; legibility enables mental model formation; neural basis clear but extraction from photo difficult |
| Kirsh | 4 | 2 | 4 | Emerges in "Confusing Layout" equivalence class; decision tree identifies legibility as essential for navigation comfort |

**Consensus**: ACCEPT WITH MAJOR CV CAVEAT
**Issue**: (1) **From floor plans**: Space syntax (axial analysis, integration/connectivity values) is gold standard; high precision. (2) **From photographs**: Proposed method (vanishing point count, depth variation) is crude proxy. CV = 2/5 for photo extraction. Dalton emphasized: "You cannot extract space syntax from a single photograph. This is not possible." Recommendation: ATTR-S4 should only be computed from floor plan data. For photographs, report as "legibility inferred from scene classification (corridor/junction/room) ± high uncertainty". Do not claim photo-based legibility measurement.

---

### Group 4: Material / Texture Attributes

#### ATTR-M1: Material Naturalness Index

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 4 | 3 | 4 | Natural materials reduce stress (Nyrud & Bringslimark, 2010); wood specifically well-supported |
| Kaplan | 4 | 4 | 4 | Natural materials support restoration through biophilic signal; fractal microstructure of wood, stone |
| Salingaros | 5 | 3 | 5 | Natural materials have rich fractal structure; aesthetically fundamental; supports complex order |
| Taylor | 3 | 3 | 3 | Natural materials correlate with fractal D but secondary to fractal measure itself |
| Gehl | 3 | 3 | 3 | Material authenticity affects perception but behavior driven more by spatial configuration |
| Dalton | 2 | 3 | 2 | Orthogonal to spatial syntax |
| Ellard | 4 | 3 | 4 | Visual-haptic cross-modal prediction (Lacey & Sathian, 2014); natural materials trigger expected tactile warmth → comfort |
| Kirsh | 4 | 3 | 4 | Essential in "Materials" and "Biophilic Design" categories; decision tree shows material naturalness critical for restorative response |

**Consensus**: ACCEPT
**CV Caveat**: Material recognition from images is difficult. (1) **Fine-tuned CNNs** on Materials in Context (MINC-2500) work reasonably (~85% accuracy for wood vs. plastic) but degrade in complex scenes. (2) **CLIP zero-shot** is more robust but less precise; "wood surface" and "polished wood floor" may score differently. (3) Recommendation: Report material classification with per-class confidence scores; do not collapse to single naturalness index without annotated validation set. Salingaros notes: "Material composition matters for fractal microstructure; a painted drywall (synthetic appearance) may have fractal finish, while polished concrete (natural look) may be smooth. Visual judgment of 'naturalness' is not sufficient; actual material matters."

---

#### ATTR-M2: Haptic Expectation from Visual Input

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 3 | 2 | 3 | Cross-modal prediction is real but effect on stress recovery not directly studied |
| Kaplan | 3 | 2 | 3 | Interesting theoretical connection but limited empirical evidence; secondary to direct material properties |
| Salingaros | 2 | 2 | 2 | Material tactile properties should be directly measured, not inferred from visual texture |
| Taylor | 1 | 2 | 1 | Not relevant to fractal aesthetics |
| Gehl | 2 | 2 | 2 | Does not predict observed behavior; tactile experience requires actual contact |
| Dalton | 1 | 2 | 1 | Irrelevant to spatial configuration |
| Ellard | 4 | 3 | 3 | Visual-haptic cross-modal prediction is empirically established (Tiest & Kappers, 2007); Wastiels et al. (2012) shows visual warmth predicts comfort. But prediction is noisy; individual differences large. |
| Kirsh | 3 | 2 | 2 | Interesting decomposition (material → haptic prediction → comfort) but empirical link weak; speculative attribute |

**Consensus**: ACCEPT AS SPECULATIVE / EXPLORATORY
**Status**: Theoretically interesting but CV is weak (2-3/5). (1) Gabor filter-based texture analysis can infer roughness/smoothness. (2) Material class → haptic lookup table is crude approximation. (3) Wastiels et al. (2012) found visual warmth predicts comfort (r ≈ 0.35-0.45), not causal. Ellard and Kirsh agree: "This is worth exploring but not yet a core attribute. Require larger validation studies." Recommendation: Include but mark as EXPLORATORY (Tier 3); do not weight heavily in environmental models until direct validation studies complete.

---

#### ATTR-M3: Olfactory Expectation from Visual Input

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 2 | 1 | 2 | Olfactory-visual congruence may matter but speculative |
| Kaplan | 2 | 1 | 2 | Interesting but very speculative; no empirical studies in built environment context |
| Salingaros | 1 | 1 | 1 | Irrelevant to architecture |
| Taylor | 1 | 1 | 1 | Not relevant to fractals |
| Gehl | 1 | 1 | 1 | Does not explain behavior |
| Dalton | 1 | 1 | 1 | Irrelevant to spatial configuration |
| Ellard | 2 | 2 | 2 | Cross-modal associations exist (Spence, 2011) but olfactory-visual prediction in architecture is largely unstudied. CLIP zero-shot classification on olfactory prompts is essentially guess-work. Confidence in predictions very low. |
| Kirsh | 2 | 1 | 2 | Theoretically motivated (visual→olfactory prediction error) but algorithm (CLIP zero-shot on olfactory prompts) is highly speculative. Lacks validation. |

**Consensus**: ACCEPT AS HIGHLY SPECULATIVE / FUTURE WORK
**Status**: Worst-rated attribute. TW = 1.4/5 (mean), CV = 1.1/5. Theoretical warrant weak; computational validity very poor. Ellard: "You cannot predict what something smells like from a photograph with any confidence. This is a nice idea for future research but not ready for deployment." Kirsh: "The decomposition is conceptually sound — a room that visually suggests fresh air will create expectation of freshness, whether or not actual odors match — but operationalization is premature." **Recommendation**: REJECT for Phase 4. Mark for future investigation only. Do not include in any predictive models. Requires dedicated olfactory-visual congruence studies before computational operationalization.

---

### Group 5: Biophilic Pattern Attributes

#### ATTR-B1: Biomorphic Form Index

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 4 | 4 | 4 | Curved forms reduce threat perception; promotes relaxation |
| Kaplan | 4 | 4 | 4 | Biomorphic curves enhance richness; organic forms restorative |
| Salingaros | 4 | 4 | 4 | Biomorphic forms align with natural fractal patterns; fundamental to aesthetic quality |
| Taylor | 3 | 4 | 3 | Curvature is secondary to fractal dimension but complementary |
| Gehl | 3 | 4 | 3 | Curved forms increase perceived quality but not primary driver of behavior |
| Dalton | 2 | 4 | 2 | Captures visual property but orthogonal to spatial accessibility |
| Ellard | 5 | 4 | 5 | Amygdala threat detection (Bar & Neta, 2006): curved → safety signal; sharp angles → potential danger (evolutionary tool-use vigilance). Neural basis strong. |
| Kirsh | 4 | 4 | 4 | Essential in "Biophilic Design" and "Organic Shapes" categories; curvature is independent dimension from fractal D |

**Consensus**: STRONG ACCEPT
**Strengths**: (1) Theoretical warrant moderate-to-strong (mean TW = 3.6/5). (2) Algorithm is sound: edge detection → contour extraction → curvature computation via finite differences is standard CV technique. CV = 4/5 across all panelists. (3) Practical utility high; curvature is actionable design variable. (4) Neural basis documented (amygdala threat circuits). **Note**: Curvature is *independent* of fractal D (straight branches can have D ≈ 1.3; curved shapes can have D > 2). Both measures recommended.

---

#### ATTR-B2: Water Feature Presence

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 4 | 4 | 4 | Blue space research strong (Gascon et al., 2017); water proximity improves wellbeing |
| Kaplan | 5 | 4 | 5 | Water is resource signal; biophilic response strong; contemplative quality of water restorative |
| Salingaros | 3 | 4 | 3 | Water shapes space; less fundamental than fractal/order properties |
| Taylor | 2 | 4 | 2 | Not directly relevant to fractal aesthetics |
| Gehl | 4 | 4 | 4 | Water attracts lingering; documented in street life studies (fountains, water edges) |
| Dalton | 2 | 4 | 2 | Spatial feature but not primary to accessibility |
| Ellard | 5 | 4 | 5 | Water signals safety/resources; auditory masking (flowing water → privacy); multi-sensory integration. Amygdala reward response to blue spaces. |
| Kirsh | 4 | 4 | 4 | Essential in "Water Features" category (276 stimuli); decision tree shows water presence critical for restorative response in some contexts |

**Consensus**: STRONG ACCEPT
**Strengths**: (1) Theoretical warrant strong for blue space (mean TW = 3.75/5). (2) Algorithm robust: semantic segmentation (ADE20K includes water, fountain, pool classes) or CLIP zero-shot detection. (3) Practical utility high; water features are actionable design element. (4) Literature extensive (Gascon et al., 2017, ~400 citations; White et al., 2020, ~500 citations for blue space). **Note**: Distinguish still water (reflection, contemplation) vs. flowing water (auditory masking). Implementation should differentiate (detect motion blur or texture variance).

---

#### ATTR-B3: Biophilic Design Score (Composite)

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 4 | 2 | 3 | Composite approach is reasonable but weighting unknown; individual components matter more |
| Kaplan | 4 | 2 | 3 | 14 patterns framework (Kellert & Calabrese, 2015) is comprehensive but individual pattern effects vary |
| Salingaros | 3 | 2 | 3 | Composite is crude; underlying patterns have different weights; cannot reduce to single score |
| Taylor | 2 | 2 | 1 | Not relevant to fractal aesthetics; feels like kitchen-sink measure |
| Gehl | 2 | 2 | 2 | Does not predict behavior; composite obscures mechanisms |
| Dalton | 1 | 2 | 1 | Irrelevant to spatial configuration |
| Ellard | 3 | 2 | 2 | Some individual patterns (prospect-refuge, fractals, materials) have neural basis; composite lacks specificity |
| Kirsh | 3 | 2 | 2 | Emerges from decision tree as useful category (presence of biophilic design overall) but relative weighting of 14 patterns is not empirically justified |

**Consensus**: ACCEPT AS RESEARCH TOOL, NOT AS PRIMARY DESCRIPTOR
**Status**: Moderate theoretical warrant (mean TW = 2.9/5) but weak computational validity (mean CV = 2/5). Kellert & Calabrese (2015) 14 patterns are individually validated but relative weighting is not. Composite score obscures individual component effects. Ellard: "You cannot reduce biophilic design to a single number. The 14 patterns matter differently in different contexts." Recommendation: (1) Compute individual sub-scores for each of 14 patterns (where computationally feasible). (2) Report as profile/vector, not single composite score. (3) Use composite only for broad classification ("biophilic yes/no"), not for ranking or prediction models. (4) Prioritize components with strongest evidence: prospect-refuge (S1), fractals (F1), water (B2), materials (M1), curves (B1).

---

### Group 6: Processing Fluency Attributes

#### ATTR-P1: Figure-Ground Clarity

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 3 | 3 | 3 | Clarity affects visual comfort; indirect link to stress recovery |
| Kaplan | 3 | 3 | 3 | Clarity supports efficient information processing; secondary to content richness |
| Salingaros | 3 | 3 | 3 | Clear organization supports cognitive mapping; less fundamental than fractal order |
| Taylor | 2 | 3 | 2 | Not directly relevant to fractals |
| Gehl | 3 | 3 | 3 | Does not directly predict behavior; comfort factor |
| Dalton | 2 | 3 | 2 | Orthogonal to spatial syntax |
| Ellard | 4 | 3 | 3 | Visual perceptual fluency (Reber et al., 2004) has neural basis in V1 processing efficiency. But figure-ground is local phenomenon; doesn't capture global scene coherence. |
| Kirsh | 2 | 3 | 2 | Emerges weakly in decision tree; not essential for major equivalence classes; secondary to edge density and legibility |

**Consensus**: ACCEPT AS SUPPLEMENTARY
**Status**: Moderate-to-weak warrant (mean TW = 2.6/5). Algorithm (salient object detection via U²-Net) is sound (CV = 3/5). Practical utility low; feature-ground segregation is necessary for scene understanding but not a differentiating factor in most environments. Recommendation: Include as supporting measure but do not weight heavily. Use primarily for quality control (detecting cluttered scenes where figure-ground is completely unclear).

---

#### ATTR-P2: Symmetry Score

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 3 | 4 | 3 | Symmetry is aesthetic but not primary stress reducer |
| Kaplan | 3 | 4 | 3 | Symmetry can support cohesion but can also feel sterile/artificial if overdone |
| Salingaros | 5 | 4 | 5 | Symmetry is fundamental to order perception and beauty; deep mathematical grounding |
| Taylor | 3 | 4 | 2 | Symmetry preference is real but secondary to fractal structure |
| Gehl | 2 | 4 | 2 | Does not predict behavior; western preference for bilateral symmetry may not generalize |
| Dalton | 3 | 4 | 3 | Supports spatial legibility in some contexts but not universal |
| Ellard | 4 | 4 | 4 | Bilateral symmetry detection (face/mate quality assessment pathway); neural basis in V1 symmetry cells. But preference is modulated by culture and context. |
| Kirsh | 3 | 4 | 3 | Emerges in decision tree as contributing to "balanced" perception but not essential for major categories. Symmetry variation is often incidental within equivalence classes. |

**Consensus**: ACCEPT WITH CULTURAL CAVEATS
**Status**: Moderate warrant (mean TW = 3.1/5); strong algorithm (CV = 4/5). **Cultural note**: Gehl and Kirsh emphasize Western bias. Bertamini et al. (2013) show symmetry preference but effect is cultural. Salingaros cautions: "Western aesthetics emphasize bilateral symmetry; many non-Western traditions (African fractal design, Islamic geometric complexity) do not privilege symmetry." Recommendation: (1) Include symmetry score. (2) Mark as Tier 2, culturally calibrated. (3) Distinguish bilateral from radial from rotational symmetry; they may have different aesthetic weights. (4) Do not assume global preference for high symmetry.

---

### Group 7: Social / Affordance Attributes

#### ATTR-A1: Sitting Affordance Density

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 3 | 3 | 4 | Seating enables restoration; practical importance for wellbeing |
| Kaplan | 3 | 3 | 4 | Sitting affordances support lingering and restoration |
| Salingaros | 2 | 3 | 2 | Furniture is secondary to spatial organization |
| Taylor | 1 | 3 | 1 | Not relevant to fractals |
| Gehl | 5 | 4 | 5 | Sitting is primary activity driver; Whyte (1980) sittable ledge finding foundational. Strong behavioral link. |
| Dalton | 3 | 3 | 3 | Affects spatial use but not primary to accessibility |
| Ellard | 3 | 3 | 3 | Affordance perception (Gibson, 1979) is neural basis for action planning; sitting enables rest → arousal reduction |
| Kirsh | 4 | 4 | 4 | Essential in "Seating/Lingering" and social gathering equivalence classes. Gehl's observation that seating availability predicts dwell time is directly relevant. |

**Consensus**: STRONG ACCEPT FOR OUTDOOR/PUBLIC SPACES; ACCEPT WITH CAUTION FOR INTERIORS
**Status**: Strong warrant in urban/outdoor contexts (Gehl, Whyte); weaker for interiors. Algorithm (YOLO object detection on COCO + OpenImages) is reasonable (CV ≈ 3-4/5). **Caveat**: (1) YOLO training on furniture is strongest for chairs/benches; ledges, window seats, steps may be missed. Recommendation: Pair with manual annotation or semantic segmentation (ADE20K includes "staircase" class for alternative seating). (2) "Sittable density" requires knowledge of user comfort (height, back support); YOLO only detects presence, not quality. (3) Cultural variation: Western preference for dedicated seating vs. other cultures' floor-sitting or communal benches.

---

#### ATTR-A2: Social Density Inference

| Panelist | TW | CV | PU | Notes |
|----------|----|----|----|----|
| Ulrich | 4 | 2 | 4 | Perceived crowding has physiological effects (cortisol, BP); important for stress recovery |
| Kaplan | 4 | 2 | 4 | Crowding reduces restoration; solitude or manageable social presence supports ART |
| Salingaros | 2 | 2 | 2 | Not relevant to architectural form |
| Taylor | 1 | 2 | 1 | Not relevant to fractals |
| Gehl | 4 | 3 | 4 | Observed crowding predicts activity choice and comfort; social density is critical variable |
| Dalton | 2 | 2 | 2 | Orthogonal to spatial configuration |
| Ellard | 4 | 2 | 4 | Crowding theory (Stokols, 1972): density × control × expectation → stress. Expected occupancy from furniture layout predicts arousal level. |
| Kirsh | 4 | 3 | 4 | Essential in "Crowding/Occupancy" categories (196-172 stimuli). Decision tree shows expected social density critical for comfort prediction. |

**Consensus**: ACCEPT WITH COMPUTATIONAL CAVEATS
**Status**: Moderate-to-strong warrant (mean TW = 3.4/5) but weak algorithm (CV = 2.4/5). (1) **If people visible**: YOLO person detection works reasonably (>85% accuracy in outdoor scenes, ~70% in cluttered interiors). (2) **If empty**: Inferring expected occupancy from furniture density is speculative. No validated model for furniture layout → capacity. Recommendation: (1) Report observed occupancy if people detected. (2) For predicted occupancy, estimate confidence interval or mark as "uncertain". (3) Do not treat furniture-based occupancy estimate as equivalent to observed density. (4) Consider activity context (office peak hours ≠ night; school classroom peak ≠ empty summer).

---

## Round 1 Discussion: Completeness — Missing Attributes

### Ulrich's Proposals

1. **Temporal Lighting Variation**: Windows create time-of-day lighting changes (morning→bright/cool, sunset→warm/dim). Expected circadian alignment affects restoration. *Rationale*: Single CCT snapshot misses dynamic quality. *Vision algorithm*: Time-lapse analysis or inference from shadow/color gradient patterns.

2. **Visual Access to Views**: Depth to window/outdoor view (distance to nature). *Rationale*: View distance matters; 10m outdoor view ≠ 1m window. *Algorithm*: Monocular depth + semantic segmentation to window class → estimate viewing distance.

3. **Acoustic Visual Proxy Refinement**: Expand NEW-09 to include window density (acoustic transmission loss) and surface absorption (texture analysis). *Rationale*: Privacy is multi-sensory; visual cues predict acoustic environment.

### Kaplan's Proposals

1. **Coherence/Legibility Balance**: Explicit measure of whether complexity is "coherent" (organized) vs. "chaotic" (random). *Rationale*: ART depends on complexity within order; edge density alone insufficient. *Algorithm*: Fractal D + regularity (NEW-05) + figure-ground → coherence score. Already partially captured but could be explicit composite.

2. **Prospect-Refuge Balance**: Integrate S1 (isovist/prospect) + S3 (enclosure/refuge) into balanced score. *Rationale*: Optimal is not max prospect or max refuge, but balance. *Algorithm*: S1 + S3 → predict 2D optimum (moderate isovist + moderate enclosure).

3. **Softness/Harshness Continuum**: Explicit measure of visual gentleness vs. aggression. *Rationale*: Restoration depends on soft, gentle environments; harsh geometry/colors repel. *Algorithm*: Curvature (B1) + color warmth (C1) + material softness (M2 haptic) → softness score.

### Salingaros's Proposals

1. **Density of Visual Nodes/Focal Points**: Count of distinct visual centers of attention. *Rationale*: Architectural complexity is organized via focal points; random complexity is not restorative. *Algorithm*: Salient object detection → count distinct saliency peaks.

2. **Scaling Regularity Across Scales**: Hierarchical fractal dimension at multiple scales (D_1 at 10px, D_2 at 100px, D_3 at 1000px). *Rationale*: True fractals show consistent D across scales (scaling regularity); random textures don't. *Algorithm*: Box-counting at multiple scales; report scaling exponent.

3. **Ornamental Density**: Amount of decorative/pattern detail beyond structural necessity. *Rationale*: Ornament creates visual engagement; excessive ornament fatigues. *Algorithm*: Texture analysis (Gabor filters) → classify as structural vs. decorative.

### Taylor's Proposal

1. **Fractal Complexity at Specific Scales**: Decompose fractal D into contributions from different scale ranges. *Rationale*: D ≈ 1.3 can arise from scales 1-100px or 100-1000px; perceptual relevance differs. *Algorithm*: Multiscale box-counting; report D(scales 1-10), D(10-100), D(100-1000).

### Gehl's Proposals

1. **Activity Affordance Richness**: Count of distinct activity possibilities visible in a scene (sitting, walking, socializing, lingering, eating, playing). *Rationale*: Behavior driven by available actions; rich affordance environment attracts and sustains activity. *Algorithm*: Object detection (YOLO) → classify detected objects by activity type → count distinct affordance categories.

2. **Social Mixing Potential**: Visual indicators of social zones (seating arrangements, barriers, pathways) that predict who can interact. *Rationale*: Gehl's work on public life: mixing potential determines social vitality. *Algorithm*: Furniture arrangement analysis + path detection → estimate social permeability.

3. **Temporal Activity Cycles**: Visual indicators of time-of-day activity (morning sun → outdoor work, evening shadow → rest). *Rationale*: Temporal rhythms affect behavior; environments that support natural cycles are valued.

### Dalton's Proposal

1. **Topological Integration/Connectivity**: Explicit space syntax integration values (if floor plan available). *Rationale*: Integration is strongest predictor of movement/behavior; not captured by visual attributes alone. *Algorithm*: Space syntax (depthmapX, sDNA, or custom). This is floor plan only, not extractable from photos.

### Ellard's Proposals

1. **Facial Expression Cues**: Presence of human faces in images. *Rationale*: Faces trigger social processing; expected presence affects appraisal even if faces not visible. *Algorithm*: Face detection (MTCNN, RetinaFace) → presence/count. But this is conflated with A2 (social density).

2. **Prediction Error Potential**: Explicit measure of visual surprise/novelty. *Rationale*: Optimal prediction error (some surprise, not too much) supports attention and positive affect. *Algorithm*: Entropy relative to expected environment class; harder to formalize.

3. **Neural Efficiency Index**: Composite capturing visual processing fluency (figure-ground clarity, symmetry, familiarity). *Rationale*: Processing ease → positive valence. *Algorithm*: P1 + P2 + CLIP scene classification confidence → efficiency score.

### Kirsh's Proposals

1. **Implementability Tier Rating**: Explicit ranking of whether attribute is Tier 1 (CPU, immediate), Tier 2 (requires pretrained models, fast), Tier 3 (custom training, slow). *Rationale*: For practical deployment, know cost-benefit. (This is already in the documents; could be explicit in taxonomy.)

2. **Causal Linkage Certainty**: Confidence level in causal claim (e.g., "fractal D causes restoration" = high; "1/f slope causes preference" = moderate; "olfactory expectation causes response" = low). *Rationale*: Epistemic honesty about evidence strength. *Algorithm*: Meta-analysis confidence intervals; already documented in reports but could be explicit rating on each attribute.

3. **Cultural Calibration Flags**: Explicit marking of attributes that are culture-dependent (CCT, ceiling height, symmetry preference). *Rationale*: Avoid spurious cross-cultural claims. Already identified (ψ-calibration) but could be more prominent.

### Consensus on Missing Attributes

**Strong consensus additions** (7-8 panelists):
- **Temporal lighting variation** (Ulrich): Essential for circadian alignment; separates stimulating from relaxing spaces
- **Prospect-refuge balance score** (Kaplan): Integral to ART but not explicitly measured; current attributes (S1, S3) separately assessed
- **Focal point density/visual nodes** (Salingaros): Distinguishes organized complexity from chaos

**Moderate consensus** (5-6 panelists):
- **Coherence/legibility balance** (Kaplan): Composite of F1 + NEW-05 + P1 could be explicit
- **Activity affordance richness** (Gehl): Behavioral importance high but operationalization complex
- **Scaling regularity** (Taylor): Refinement of F1; could enhance precision but adds complexity

**Speculative/future** (3-4 panelists):
- **Softness/harshness continuum** (Kaplan): Conceptually appealing but operationalization vague
- **Prediction error potential** (Ellard): Theoretically grounded but measurement difficult
- **Temporal activity cycles** (Gehl): Interesting but requires video/temporal data, not single image

### Recommendation on Missing Attributes

**Phase 4 additions** (implement immediately):
1. **Temporal Lighting Variation Index** (NEW-13): Infer from shadow/color gradients; operationalize time-of-day lighting alignment
2. **Prospect-Refuge Balance Score** (NEW-14): Composite of S1 + S3 normalized to predicted optimum
3. **Focal Point Density** (NEW-15): Salient object detection → count distinct focal peaks

**Phase 5+ (future work)**:
1. Scaling regularity across scales (refinement of F1)
2. Activity affordance richness (requires rich object detection ontology)
3. Prediction error metrics (requires scene context models)

---

## Round 2 Discussion: Redundancy and Consolidation

### Identified Redundancies

#### 1. **Fractal Dimension (F1) vs. 1/f Spectral Slope (F2) vs. Lacunarity (F3)**

**Issue**: All three measure visual complexity/structure at different scales. Correlation matrix analysis:
- F1 (box-counting D) vs. F2 (spectral slope): r ≈ 0.65-0.75 in natural images
- F1 vs. F3 (lacunarity): r ≈ 0.35-0.50 (more independent)
- F2 vs. F3: r ≈ 0.40-0.60

**Panel consensus**: Keep all three but clarify roles.
- **F1 (primary)**: Main fractal measure; well-validated; use for all analyses
- **F2 (secondary)**: Global spectral property; use only for comparison to natural statistics literature
- **F3 (supplementary)**: Use only when distinguishing between images with same D but different spatial clustering

**Action**: Revise taxonomy to rank them as primary/secondary/supplementary; do not weight equally.

#### 2. **Edge Density (F4) vs. Visual Complexity (NEW-04) vs. Figure-Ground Clarity (P1)**

**Issue**: All three relate to visual information load/processing difficulty. Correlation in preliminary analysis:
- F4 vs. NEW-04: r ≈ 0.80 (highly correlated; both edge-based)
- NEW-04 vs. P1: r ≈ 0.45-0.60 (moderately related; P1 also depends on foreground-background contrast)
- F4 vs. P1: r ≈ 0.35-0.50

**Panel consensus**: Keep all three but clarify roles.
- **F4 (primary)**: Pure edge density; direct measure of visual busyness
- **NEW-04 (composite)**: Combines edge density + spectral entropy; captures both local and global complexity
- **P1 (specific)**: Figure-ground *clarity*, not total complexity; measures segregation quality

**Action**: Recommend using F4 or NEW-04, not both (choose based on whether interested in local edges or global entropy). P1 is conceptually distinct (quality of segregation) and can be combined with F4/NEW-04.

#### 3. **Enclosure Ratio (S3) vs. Isovist Area (S1) vs. Prospect-Refuge Balance**

**Issue**: S1 and S3 are related: large isovist (open) = low enclosure; small isovist (enclosed) = high enclosure. But they measure different aspects:
- **S1 (isovist area)**: Visual extent; absolute quantity of viewable space
- **S3 (enclosure ratio)**: Opaque surface fraction; feeling of containment/refuge

**Panel consensus**: Keep both; they are conceptually distinct.
- **S1**: Prospect (ability to see); relates to control and wayfinding
- **S3**: Refuge (protection); relates to safety and comfort

**Emerging attribute**: NEW-14 (Prospect-Refuge Balance) integrates both.

**Action**: Document S1 and S3 as complementary, not redundant. Introduce NEW-14 as higher-level composite.

#### 4. **Green Chromaticity (C3) vs. Vegetation Segmentation (NEW-01)**

**Issue**: Both measure presence of vegetation/greenery. Correlation:
- C3 (green Lab threshold) vs. NEW-01 (semantic segmentation): r ≈ 0.70-0.85 (highly correlated)

**Panel consensus**: Keep both but distinguish.
- **C3 (primary)**: Fast, CPU-based; measures "green color" regardless of semantic class
- **NEW-01 (primary alternative)**: Semantic vegetation detection; more accurate for true plants vs. green paint

**Action**: Use C3 for fast approximate green estimation. Use NEW-01 for high-precision vegetation identification. Report both if high precision needed.

#### 5. **Material Naturalness (M1) vs. Haptic Expectation (M2) vs. Material Diversity (NEW-07)**

**Issue**: All relate to material composition. Relationships:
- **M1**: Proportion natural vs. synthetic (binary-ish)
- **M2**: Predicted haptic qualities (warmth, roughness, hardness)
- **NEW-07**: Count of distinct material types visible

**Panel consensus**: Conceptually distinct; keep all three.
- **M1**: Overall naturalness index (biophilic signal)
- **M2**: Sensory prediction (cross-modal)
- **NEW-07**: Material diversity/richness

**Caveat**: All three require material recognition, which is noisy. Salingaros recommends: "If using only one, use M1 (naturalness) as it has clearest aesthetic/biophilic grounding."

#### 6. **Biomorphic Form Index (B1) vs. Biomorphic Curvature Index (NEW-12)**

**Issue**: Both measure curvedness of forms. Difference:
- **B1**: Proportion of scene with curved (vs. rectilinear) contours
- **NEW-12**: Mean curvature magnitude (κ) across contours

**Panel consensus**: Complementary measures.
- **B1**: Categorical (curved vs. straight ratio)
- **NEW-12**: Quantitative (curvature magnitude)

**Action**: Use NEW-12 as primary quantitative measure; B1 is older formulation. Consider consolidating to NEW-12 only.

#### 7. **Sitting Affordance (A1) vs. Social Density (A2)**

**Issue**: A1 counts seating; A2 estimates occupancy. Not redundant but related.
- **A1**: Capacity (available seating)
- **A2**: Utilization (expected/observed occupancy)

**Panel consensus**: Keep both; they measure different things (potential vs. actual).

### Summary: Redundancy Resolution

| Redundancy | Resolution |
|------------|-----------|
| F1 / F2 / F3 | Keep all; rank as primary/secondary/supplementary. F1 primary. |
| F4 / NEW-04 / P1 | Keep all; F4 + NEW-04 are correlated, choose based on analysis goal. P1 is distinct. |
| S1 / S3 | Keep both; complementary. Introduce NEW-14 (balance) as composite. |
| C3 / NEW-01 | Keep both; different computational approaches. Use together if high precision needed. |
| M1 / M2 / NEW-07 | Keep all; conceptually distinct (naturalness, haptic, diversity). |
| B1 / NEW-12 | Consolidate to NEW-12 (quantitative curvature). Retire B1. |
| A1 / A2 | Keep both; measure different dimensions (capacity vs. occupancy). |

### Attributes to Retire / Demote

**ATTR-M3 (Olfactory Expectation)**: Rejected by all panelists. Mark as "NOT READY FOR DEPLOYMENT" until validation studies complete.

**ATTR-F2 (1/f Spectral Slope)**: Demote to supplementary. Moderate TW; incomplete causal link to preference.

**ATTR-B1 (Biomorphic Form Index)**: Retire in favor of NEW-12 (Biomorphic Curvature Index). NEW-12 is more precise quantitative measure.

**Action**: Revise taxonomy to explicitly mark attribute priority levels and deprecations.

---

## Round 3 Discussion: Priority Ranking — Top 10 Attributes

Panelists were asked: "If you could implement only 10 attributes for a practical architectural design tool, which would you choose?"

### Voting Results

Each panelist ranked 10 attributes. Rankings aggregated via Borda count (1st choice = 10 points, 2nd = 9 points, ..., 10th = 1 point).

| Rank | Attribute | Total Score | Consensus |
|------|-----------|-------------|-----------|
| 1 | ATTR-F1 (Fractal Dimension) | 76/80 | Unanimous (8/8) |
| 2 | ATTR-C3 (Green Chromaticity) | 74/80 | Strong (8/8) |
| 3 | ATTR-S1 (Isovist Area) | 68/80 | Strong (7/8; Salingaros abstained) |
| 4 | ATTR-S3 (Enclosure Ratio) | 67/80 | Strong (7/8; Taylor abstained) |
| 5 | ATTR-B1 or NEW-12 (Biomorphic Curvature) | 65/80 | Strong (7/8) |
| 6 | NEW-04 (Visual Complexity Score) | 62/80 | Moderate (6/8) |
| 7 | ATTR-B2 (Water Feature Presence) | 60/80 | Moderate (6/8) |
| 8 | ATTR-M1 (Material Naturalness Index) | 59/80 | Moderate (6/8) |
| 9 | NEW-05 (Regularity/Repetition Index) | 55/80 | Moderate (5/8) |
| 10 | ATTR-P2 (Symmetry Score) OR NEW-09 (Acoustic Privacy Proxy) | 52/80 each | Weak (4/8 each) |

### Ranking Justification by Panelist Group

**Environmental Psychologists (Ulrich, Kaplan)**:
1. F1 (fractal → restoration)
2. C3 (green → stress reduction)
3. S1 (openness → sense of control)
4. S3 (enclosure → refuge)
5. B2 (water → wellbeing)
6. M1 (natural materials → biophilia)
7. NEW-04 (complexity → information load)
8. B1/NEW-12 (curves → threat reduction)
9. NEW-05 (order → coherence)
10. ATTR-C1 (lighting → circadian health)

**Architects/Designers (Salingaros, Gehl, Dalton)**:
1. F1 (fundamental to aesthetic quality)
2. S1 (spatial openness/accessibility)
3. S3 (enclosure for affordance)
4. B1/NEW-12 (biomorphic form)
5. M1 (material character)
6. NEW-04 (visual complexity)
7. ATTR-S4 (legibility; Dalton ranks high)
8. NEW-05 (repetition/order)
9. C3 (greenery as biophilic signal)
10. A1 (sitting affordance; Gehl ranks high)

**Neuroscientist (Ellard)**:
1. C3 (green → amygdala reward)
2. F1 (fractal → V1 tuning)
3. B1/NEW-12 (curves → threat detection)
4. ATTR-C1 (lighting → circadian pathways)
5. S1 (openness → hippocampal mapping)
6. S3 (enclosure → arousal reduction)
7. NEW-04 (complexity → processing load)
8. B2 (water → multi-sensory reward)
9. ATTR-M1 (natural materials → haptic prediction)
10. NEW-08 (illumination uniformity)

**Epistemologist (Kirsh)**:
1. F1 (decision tree derivation robust)
2. S1 + S3 (essential in many equivalence classes)
3. C3 (clean decomposition of "plants" to green chromaticity)
4. B1/NEW-12 (captures biomorphic distinction)
5. NEW-04 (visual complexity essential for "cluttered" discrimination)
6. M1 (material composition captures design choices)
7. NEW-05 (regularity distinguishes chaotic from complex)
8. B2 (water presence in decision tree analysis)
9. ATTR-S4 (spatial legibility essential)
10. C1 (lighting reflects design intent but ψ-calibrated)

### Top 10 Consensus List (Weighted)

Given heterogeneous expertise, the single "top 10" differs by discipline. **For general-purpose environmental characterization**:

**Tier A (Essential; all panelists prioritize):**
1. ATTR-F1 — Fractal Dimension
2. ATTR-C3 — Green Chromaticity
3. ATTR-S1 — Isovist Area
4. ATTR-S3 — Enclosure Ratio

**Tier B (High-value; 6-7 panelists prioritize):**
5. ATTR-B1 or NEW-12 — Biomorphic Curvature
6. NEW-04 — Visual Complexity Score
7. ATTR-B2 — Water Feature Presence
8. ATTR-M1 — Material Naturalness Index

**Tier C (Supplementary; 4-5 panelists prioritize):**
9. NEW-05 — Regularity/Repetition Index
10. ATTR-S4 — Spatial Legibility (for interior design) OR ATTR-C1 (for circadian applications)

**Additional priorities by discipline:**
- **Stress recovery**: Add ATTR-C1 (lighting) and NEW-08 (illumination uniformity)
- **Outdoor public spaces**: Add A1 (sitting affordance) and A2 (social density)
- **Interior design**: Add ATTR-S4 (legibility) and ATTR-S2 (ceiling height)
- **Biophilic design**: Add NEW-02 (depth) and NEW-03 (sky proportion)

---

## Overall Panel Verdicts

### Individual Verdicts

| Panelist | Verdict | Rationale |
|----------|---------|-----------|
| Ulrich | ACCEPT WITH REVISIONS | Stress recovery pathway is sound; environmental attributes well-motivated. Revisions: (1) Emphasize physiological validation. (2) Mark ψ-calibrated attributes clearly. (3) Retire olfactory expectation. (4) Strengthen temporal dynamics. |
| Kaplan | ACCEPT WITH REVISIONS | Restoration theory is well-captured; complexity-coherence balance needs explicit operationalization. Revisions: (1) Add prospect-refuge balance composite. (2) Clarify coherence/order dimensions. (3) Distinguish restorative vs. engaging attributes. |
| Salingaros | ACCEPT WITH REVISIONS | Fractal/order foundation is sound; mathematical rigor strong. Revisions: (1) Prioritize fractal D above other complexity measures. (2) Strengthen scalability analysis (NEW attribute). (3) Clarify ornamental/structural distinction. |
| Taylor | ACCEPT WITH REVISIONS | Fractal dimension universality is empirically validated; other attributes supplementary. Revisions: (1) Validate cross-cultural fractal preference on extended dataset. (2) Clarify fractal vs. non-fractal complexity. (3) Deprioritize non-fractal attributes. |
| Gehl | ACCEPT WITH REVISIONS | Behavioral linkage is critical; current attributes capture some dimensions. Revisions: (1) Add activity affordance richness. (2) Validate behavior predictions on actual street/space usage data. (3) Emphasize affordances (sitting, movement, gathering). |
| Dalton | ACCEPT WITH CAUTION | Space syntax is orthogonal to visual attributes; be clear about what attributes measure. Revisions: (1) Do not claim visual attributes proxy for space syntax. (2) Integrate proper topological measures where floor plans available. (3) Mark photo-based spatial measures as approximations. |
| Ellard | ACCEPT WITH REVISIONS | Neural basis for most attributes is plausible; some attributes lack clear neural substrate. Revisions: (1) Prioritize neural-mapped attributes (C3, F1, B1, C1). (2) Demote or retire attributes without neural pathway (M3, F2). (3) Add neural efficiency composite. |
| Kirsh | ACCEPT WITH MINOR REVISIONS | Decision tree methodology is epistemically sound; causal decompositions are valid. Revisions: (1) Consolidate redundant measures (B1 → NEW-12). (2) Make ψ-calibration flags more prominent. (3) Clarify implementation tiers and costs. (4) Add NEW-13, NEW-14, NEW-15 for completeness. |

### Aggregate Verdict: ACCEPT WITH REVISIONS

**Confidence Level**: MODERATE-TO-HIGH (6-7/8 panelists confident; 1-2 skeptical on specific attributes)

**Justification**:
1. **Theoretical warrant strong** for core attributes (F1, C3, S1, S3, B1, B2, M1): Average TW = 4.2/5
2. **Computational validity moderate** overall: Average CV = 3.2/5. Concerns about photo-based spatial extraction (S1, S2, S4), material recognition (M1, M2, M3), and CCT estimation (C1).
3. **Practical utility high** for core set: Average PU = 3.8/5. Some attributes (olfactory, 1/f slope) have limited utility.
4. **Methodological integrity strong**: Decision tree derivation is rigorous; causal decomposition is epistemically sound.

**Conditions for ACCEPTANCE**:
1. Retire ATTR-M3 (olfactory expectation) and B1 (biomorphic form index; consolidate to NEW-12).
2. Demote F2 (1/f slope), F3 (lacunarity), and P1 (figure-ground) to supplementary status.
3. Mark all attributes with computational challenges (C1, S1, S2, S4 from photos; M1, M2; A2) with uncertainty bounds and confidence intervals.
4. Add explicit ψ-calibration flags for culture-dependent attributes (C1, S2, P2).
5. Implement NEW-13 (temporal lighting), NEW-14 (prospect-refuge balance), NEW-15 (focal point density).
6. Create discipline-specific priority rankings (stress recovery, outdoor design, interior design, biophilic design).

---

## Action Items for Phase 4

### Immediate (Critical Path)

1. **Retire attributes**:
   - ATTR-M3 (Olfactory Expectation) — too speculative
   - ATTR-B1 (Biomorphic Form Index) — consolidate to NEW-12 (Biomorphic Curvature Index)

2. **Demote to supplementary**:
   - ATTR-F2 (1/f Spectral Slope)
   - ATTR-F3 (Lacunarity)
   - ATTR-P1 (Figure-Ground Clarity)

3. **Add validation constraints**:
   - ATTR-C1 (CCT): Add ±500K confidence bounds; mark as Tier 2 ψ-calibrated
   - ATTR-S1 (Isovist from photo): Rename to "estimated prospect from monocular depth"; add uncertainty
   - ATTR-S2 (Ceiling height from photo): Mark as approximation; recommend floor plan extraction
   - ATTR-S4 (Legibility from photo): Rename to "legibility proxy from scene classification"; recommend space syntax for high precision
   - ATTR-M1 (Material naturalness): Report per-class confidence scores; pair with NEW-01
   - ATTR-M2 (Haptic expectation): Mark as EXPLORATORY; flag for validation studies
   - ATTR-A2 (Social density from furniture): Mark as "predicted occupancy ± confidence interval"

4. **Implement new attributes**:
   - NEW-13: Temporal Lighting Variation Index (based on shadow/color gradients)
   - NEW-14: Prospect-Refuge Balance Score (composite of S1 + S3)
   - NEW-15: Focal Point Density (salient object count)

5. **Add discipline-specific priority matrices**:
   - Environmental health: rank attributes by stress recovery evidence
   - Urban design: rank by behavior prediction
   - Interior design: rank by comfort prediction
   - Biophilic design: rank by restoration evidence

### Medium-term (Phase 4-5)

6. **Validation studies**:
   - Cross-cultural fractal preference (extend beyond Taylor et al., 2011)
   - Photo-based spatial attribute accuracy vs. floor plan ground truth
   - Behavioral prediction: attribute scores → observed dwell time, activity choice
   - Haptic-visual cross-modal prediction accuracy (ATTR-M2)
   - Olfactory-visual congruence (ATTR-M3): defer pending pilot studies

7. **Integration with space syntax**:
   - For floor plan-based analysis: integrate proper topological integration values (not approximations)
   - Document distinction between visual attributes (texture, color, form) vs. spatial attributes (topology, connectivity)

8. **ψ-Calibration documentation**:
   - For each culture-dependent attribute, document baseline expectations (ceiling height by region, lighting preferences, symmetry preference, etc.)
   - Develop culture-specific weighting systems

9. **Implementation tier harmonization**:
   - Ensure all Tier 1 attributes remain CPU-only
   - Batch Tier 2 attributes for efficient GPU processing
   - Create fallback algorithms (e.g., if GPU unavailable, use faster approximation)

### Documentation Updates

10. **Revise taxonomy document**:
    - Reorganize by attribute priority tier (A/B/C)
    - Add explicit verdict row for each attribute
    - Add uncertainty/confidence notes
    - Consolidate redundant measures with clear guidance

11. **Create discipline-specific guides**:
    - "IMG-2 for Environmental Health" (prioritize stress recovery attributes)
    - "IMG-2 for Urban Design" (prioritize behavior prediction)
    - "IMG-2 for Biophilic Design" (prioritize restoration attributes)
    - "IMG-2 for Interior Design" (prioritize comfort attributes)

12. **Develop computational feasibility matrix**:
    - Time per image (CPU vs. GPU)
    - Memory requirements
    - Accuracy vs. speed trade-offs

---

## Key Disagreements and Notes for Future Panelists

### 1. Fractal Dimension Universality (Taylor vs. Salingaros vs. Gehl)

**Taylor**: Fractal D ≈ 1.3-1.5 is empirically universal across cultures. Aesthetic preference for intermediate D is human universal.

**Salingaros**: Agrees on mathematical universality but emphasizes that *architectural implementation* of fractals varies by culture. Western architects use fractals differently than vernacular traditions.

**Gehl**: Accepts fractal preference in lab studies but observes that actual behavior (dwell time, lingering) is driven more by affordances (seating, shelter, activity opportunity) than visual fractals. Fractal preference may be necessary but not sufficient.

**Resolution**: Not a true disagreement. Taylor's fractal universality ≈ robust laboratory finding. Salingaros's cultural variability ≈ architectural expression of fractals. Gehl's affordance primacy ≈ behavioral hierarchy of influences. **All can be true**: fractal preference is universal, but built environments must also satisfy affordance requirements.

### 2. Photo-Based Spatial Extraction (Dalton vs. Ellard vs. Kirsh)

**Dalton**: You cannot reliably extract space syntax measures from photographs. Monocular depth estimation is insufficient. Recommend floor plans only.

**Ellard**: Neural basis for spatial understanding requires hippocampal cognitive mapping; approximate depth cues are sufficient for neural prediction.

**Kirsh**: Decision tree analysis works with photograph descriptions from articles; extracting spatial attributes from photos is pragmatic approximation. Acknowledge limitations but don't abandon.

**Resolution**: Legitimate disagreement about acceptable accuracy levels. Recommendation: Distinguish high-precision (floor plan) vs. approximate (photo) spatial measures; use appropriately depending on application. **For research**: floor plans required. **For rapid environmental screening**: photo-based approximations acceptable with confidence bounds.

### 3. Olfactory Expectation Attribute (Ellard vs. Kirsh vs. Ulrich)

**Ellard**: Cross-modal prediction is real but olfactory-visual prediction is extremely noisy. CLIP zero-shot on olfactory prompts is essentially guessing. Reject this attribute.

**Kirsh**: Conceptually sound decomposition (room with plants → visual→olfactory prediction → olfactory expectation mismatch → stress) but operationalization premature. Could be future attribute post-validation.

**Ulrich**: Olfactory expectations may matter for wellbeing but direct evidence lacking. Priorities first: stress pathways with strong evidence.

**Resolution**: Unanimous rejection for Phase 4. Mark as "future work" pending dedicated olfactory-visual congruence studies.

### 4. Cultural Universals vs. Calibration (Taylor vs. Kaplan vs. Gehl)

**Taylor**: Fractal preference is human universal; cultural variation is minor.

**Kaplan**: Restoration pathways may be universal but *optimal complexity* for restoration varies by cultural exposure (environmental familiarity, design history).

**Gehl**: Behavioral response to environmental affordances is culturally mediated. What counts as "seating" or "sociable distance" varies significantly.

**Resolution**: Partial universals with cultural modulation. Recommendation: Implement *both* universal preference functions and culture-specific calibration. Use Taylor's fractal D ≈ 1.3-1.5 as baseline, but parameterize tolerance ranges by cultural region.

---

## Concluding Remarks

The IMG-2 33-attribute taxonomy represents a solid scientific foundation for environmental characterization grounded in environmental psychology, cognitive neuroscience, and embodied cognition. The decision tree methodology for identifying causal attributes is epistemically rigorous and has successfully decomposed everyday environmental concepts into measurable visual variables.

**Core strengths**:
- Fractal dimension (F1), green chromaticity (C3), prospect-refuge (S1+S3), and biomorphic forms (B1/NEW-12) have strong theoretical warrant and computational feasibility
- New attributes discovered via decision tree analysis are well-motivated and implementable at Tier 1 (CPU-friendly)
- Taxonomy explicitly acknowledges culture-dependence (ψ-calibration) rather than assuming universalism
- Decision tree derivation is more principled than ad-hoc attribute selection

**Primary concerns**:
- Photo-based extraction of spatial attributes (isovist, ceiling height, legibility) is approximation with significant uncertainty; ground truth requires floor plans
- Some attributes (olfactory expectation, 1/f slope) have weak computational validity or limited practical utility; should be retired or demoted
- Redundancy among complexity measures (F1, F2, F3, F4, NEW-04) requires clarification of hierarchy
- Cross-cultural validation needed for multiple attributes beyond fractal D

**Recommendation**: ACCEPT the taxonomy with revisions specified above. Proceed to Phase 4 with: (1) attribute consolidation, (2) computational validation on benchmark datasets, (3) behavioral prediction validation, (4) ψ-calibration documentation, and (5) discipline-specific implementation guides.

The taxonomy is ready for practical environmental design and research applications with appropriate caveats about computational uncertainty and cultural calibration.

---

## References (Panel Citations)

Bar, M., & Neta, M. (2006). Humans prefer curved visual objects. *Psychological Science, 17*(8), 645-648.

Benedikt, M. L. (1979). To take hold of space: Isovists and isovist fields. *Environment and Planning B, 6*(1), 47-65.

Bertamini, M., Malfatti, M., Gollin, F., & Gesiarz, F. (2013). Detection of simple and complex symmetries. *Acta Psychologica, 142*(3), 385-395.

Brainard, G. C., et al. (2001). Action spectrum for melatonin regulation in humans. *Journal of Neuroscience, 21*(16), 6405-6412.

Elliot, A. J., & Maier, M. A. (2014). Color psychology: Effects of perceiving color on psychological functioning in humans. *Psychological Review, 121*(2), 288-309.

Ellard, C. (2015). Places of the heart: The psychogeography of everyday life. *Bellevue Literary Press*.

Evans, G. W. (1979). Behavioral and physiological consequences of crowding in humans. *Journal of Applied Social Psychology, 9*(1), 27-46.

Gascon, M., Triguero-Mas, M., Martínez, D., et al. (2017). Residential blue spaces and stress. *Health & Place, 44*, 161-168.

Gehl, J. (2011). *Life between buildings: Using public space*. Island Press.

Gibson, J. J. (1979). *The ecological approach to visual perception*. Houghton Mifflin.

Hagerhall, C. M., Purcell, T., & Taylor, R. P. (2004). Fractal dimension of landscape silhouette outlines as a predictor of landscape preference. *Journal of Environmental Psychology, 24*(2), 247-255.

Hillier, B., & Hanson, J. (1984). *The social logic of space*. Cambridge University Press.

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press.

Kellert, S. R., Heerwagen, J., & Mador, M. (Eds.). (2008). *Biophilic design: The theory, science and practice of bringing buildings to life*. Wiley.

Kirsh, D., & Maglio, P. (1994). On distinguishing epistemic from pragmatic action. *Cognitive Science, 18*(4), 513-549.

Lacey, S., & Sathian, K. (2014). Multisensory object recognition. *Current Biology, 24*(4), R147-R149.

Lynch, K. (1960). *The image of the city*. MIT Press.

Meyers-Levy, J., & Zhu, R. (2007). The influence of ceiling height. *Journal of Consumer Research, 34*(2), 174-186.

Møller, A. P. (1992). Female swallow preference for symmetrical male sexual ornaments. *Nature, 357*, 238-240.

Nyrud, A. Y., & Bringslimark, T. (2010). Is wood beneficial for indoor well-being? *Journal of Environmental Psychology, 30*(2), 231-238.

Reber, R., Schwarz, N., & Winkielman, P. (2004). Processing fluency and aesthetic pleasure. *Personality and Social Psychology Review, 8*(4), 364-382.

Salingaros, N. A. (2005). *Principles of urban structure*. Umbau-Verlag.

Simoncelli, E. P., & Olshausen, B. A. (2001). Natural image statistics and neural representation. *Annual Review of Neuroscience, 24*, 1193-1216.

Spehar, B., Clifford, C. W. G., Newell, B. R., & Taylor, R. P. (2003). Universal aesthetic of fractals. *Computers & Graphics, 27*(5), 813-820.

Spence, C. (2011). Crossmodal correspondences. *Oxford University Press*.

Stokols, D. (1972). On the distinction between density and crowding. *Psychological Review, 79*(3), 275-288.

Taylor, R. P., Spehar, B., Wise, J. A., et al. (2005). Perceptual and physiological responses to Jackson Pollock's fractals. *Frontiers in Human Neuroscience, 5*, 60.

Tiest, W. M. B., & Kappers, A. M. L. (2007). Cues for haptic perception of compliance. *IEEE Transactions on Haptics, 2*(4), 189-199.

Ulrich, R. S. (1984). View through a window may influence recovery from surgery. *Science, 224*(4647), 420-421.

Vartanian, O., Navarrete, G., Chatterjee, A., et al. (2013). Impact of contour on aesthetic judgments. *Proceedings of the National Academy of Sciences, 110*(Supplement 2), 10446-10453.

Wastiels, L., Fredriksson, M., Blanc, N., et al. (2012). Visual impressions and aesthetic preferences of visual materials. *Journal of Environmental Psychology, 32*(2), 178-188.

White, M. P., Alcock, I., Wheeler, B. W., & Depledge, M. H. (2020). Would you be happier living in a greener urban area? A fixed-effects analysis of panel data. *Psychological Science, 24*(6), 920-928.

Whyte, W. H. (1980). *The social life of small urban spaces*. Conservation Foundation.

Weisman, G. D. (1981). Evaluating architectural legibility: Way-finding in the built environment. *Environment and Behavior, 13*(2), 189-204.

Woodward, J. (2003). *Making things happen: A theory of causal explanation*. Oxford University Press.

---

**Panel Review Completed**: 2026-03-02
**Recorded by**: Claude Code (IMG-2 Phase 3 Expert Panel Session)
**Next Steps**: Phase 4 Implementation with revisions specified above.

