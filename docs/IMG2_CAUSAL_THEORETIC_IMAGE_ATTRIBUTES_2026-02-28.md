# IMG-2: Causal-Theoretic Visual Attribute Taxonomy for Architectural Image Characterization

**Date**: 2026-02-28
**Author**: CW Session 18
**Status**: Draft for DK review

---

## 1. The Philosophical Status of Visual Attribute Identification

When environmental psychology articles report that "rooms with plants reduced stress" or "high ceilings improved creativity," they use **everyday descriptors** — commonsense terms that pick out environmental features at the level of human practical understanding. The ATLAS system's task is to translate these everyday descriptors into **specific environmental attributes hypothesized to be causally active** in producing the observed psychological effects, and to specify the **vision algorithms** that can extract these attributes from architectural images.

This translation is neither trivial nor epistemically innocent. It involves a particular kind of theoretical commitment that deserves explicit philosophical characterization.

### 1.1 Beyond Theory-Ladenness

The standard "theory-ladenness of observation" thesis (Hanson, 1958; Kuhn, 1962) holds that what we see is shaped by what we know. But the translation from "plants" to "fractal dimension D ≈ 1.3-1.5" is something more than perceptual interpretation colored by theory. It is a **causal-theoretic decomposition**: a hypothesis about which physical properties of the stimulus are doing the causal work in producing the psychological effect. Three features distinguish this from mere theory-ladenness:

1. **It is a reduction claim.** We are claiming that the causally active ingredient in "plants" (for stress reduction) is not the concept "plant" but specific measurable properties: fractal self-similarity (D ≈ 1.3-1.5 per Hagerhall et al., 2004; Taylor et al., 2005), green chromaticity (in CIE Lab: a* < -10), biomorphic curvature (curvature index > 0.6), and possibly visual complexity within a tolerable range (Shannon entropy 3.5-5.0 bits). Each of these is independently manipulable by intervention.

2. **It generates testable predictions.** If fractal dimension is the active ingredient, then non-plant stimuli with D ≈ 1.3-1.5 (e.g., Jackson Pollock paintings, river networks, branching cracks) should produce similar stress reduction. This has been partially confirmed (Taylor et al., 2011; Spehar et al., 2003). If green chromaticity is the active ingredient, then green-tinted artificial surfaces should produce the effect without any plant. Each decomposition generates different experimental predictions.

3. **It is defeasible and revisable.** The decomposition might be wrong. Perhaps the active ingredient in "plants" is actually the implied moisture and air quality (an olfactory expectation derived from visual input), or the implied presence of other living things (a social-cognitive inference). The decomposition is a genuine empirical hypothesis, not a definitional truth.

### 1.2 The Proper Term: Mechanistic Decomposition of Causal Variables

In Woodward's (2003) interventionist framework for causation, a variable X is a cause of Y if and only if there is a possible intervention on X that would change Y while holding other variables fixed. Our task is to identify which **fine-grained variables** (fractal D, chromaticity, curvature, etc.) are the genuine causes, given that the experimenter manipulated a **coarse-grained variable** ("presence of plants").

This is what Craver (2007) calls **constitutive mechanistic explanation** — identifying the components and their activities that constitute a phenomenon. Bechtel & Abrahamsen (2005) describe this as **mechanistic decomposition**: taking a complex phenomenon (stress reduction from plants) and decomposing it into component operations at a lower level (visual processing of fractal patterns → fluency → reduced prediction error → lower arousal).

The philosophical literature offers several related terms, each emphasizing a different aspect:

| Term | Source | Emphasis | Fit |
|------|--------|----------|-----|
| **Mechanistic decomposition** | Bechtel & Abrahamsen (2005) | Identifying component operations | Good |
| **Constitutive mechanistic explanation** | Craver (2007) | Lower-level entities/activities that constitute the phenomenon | Good |
| **Causal variable identification** | Woodward (2003) | Which variables, under intervention, change the outcome | Best fit |
| **Type-reduction** | Nagel (1961) | Bridging higher-level to lower-level descriptions | Partial fit |
| **Theoretical identification** | Smart (1959), Place (1956) | Identifying everyday concepts with scientific ones | Partial fit |
| **Auxiliary hypotheses** | Lakatos (1970) | Assumptions connecting observation to theory | Partial fit |

We propose using **causal variable identification** as our primary term, drawing on Woodward. The claim that "plants reduce stress via fractal dimension" is a claim about **which variables, if intervened upon, would change the outcome** — and this is a genuine empirical contribution, not merely an interpretive gloss.

### 1.3 Significance as a Reduction

David Kirsh's observation that this constitutes "a genuine contribution — a reduction — that is significant" is exactly right. The reduction is significant because:

1. It **unifies** apparently disparate findings. If fractal D ≈ 1.3-1.5 is the active ingredient, then stress reduction from plants, from certain art, from nature views, and from certain material textures share a common cause — despite appearing completely unrelated at the everyday-descriptor level.

2. It **enables engineering**. If we know the causally active variable is fractal dimension (not "plants" per se), we can design built environments that achieve the same effect without plants — through material selection, surface patterning, facade design, or digital displays with appropriate fractal characteristics.

3. It **resolves apparent contradictions**. Some studies find plants help; some don't. The decomposition predicts this: plants with D < 1.2 (e.g., highly manicured topiary) may not produce the effect, while complex fractal arrangements of any material might.

---

## 2. The Extended Attribute Taxonomy

Below we define the **causal-theoretic visual attributes** organized by the type of causal mechanism hypothesized. Each attribute includes:

- **Everyday descriptors** (what experimenters typically write)
- **Causally active variable** (the hypothesized fine-grained cause)
- **Vision algorithm** (how to extract it from an image)
- **Theoretical warrant** (which theory/framework predicts this is the active variable)
- **Evidence strength** (how well the causal claim is supported)
- **CVA constraint mapping** (which ATLAS constraint this feeds)

### 2.1 Fractal / Natural Statistics Attributes

These attributes capture the hypothesis that human visual systems are tuned to the statistical regularities of natural scenes (Simoncelli & Olshausen, 2001; Geisler, 2008), and that built environments matching these statistics are processed more fluently.

#### ATTR-F1: Fractal Dimension (Box-Counting)

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "natural-looking," "organic," "rich texture," "detailed" |
| **Causally active variable** | Fractal dimension D (box-counting method), optimal range 1.3-1.5 for preference |
| **Definition** | Self-similarity across spatial scales, measured as the slope of log(N) vs. log(1/ε) where N = number of boxes of size ε needed to cover the edge map |
| **Vision algorithm** | (1) Canny edge detection → (2) binary edge map → (3) box-counting at scales ε = {4, 8, 16, 32, 64, 128, 256} px → (4) linear regression of log(N) on log(1/ε); D = |slope| |
| **Implementation** | OpenCV Canny + custom box-counting (Python: numpy grid subdivision); or `fractalpy` library |
| **Theoretical warrant** | Attention Restoration Theory (Kaplan, 1995): natural fractals elicit "soft fascination." Predictive processing: D ≈ 1.3-1.5 matches neural tuning to natural statistics, minimizing prediction error (Spehar et al., 2003). |
| **Evidence** | STRONG. Taylor et al. (2005, ~800 cit): D ≈ 1.3-1.5 preferred across cultures. Hagerhall et al. (2004, ~400 cit): nature images cluster at D ≈ 1.3. Spehar et al. (2003, ~250 cit): universal preference for intermediate D. |
| **CVA constraints** | prediction_error (low when D in optimal range), spatial_frequency_match |
| **Calibration notes** | D varies with image resolution and edge threshold. Standardize: 1024×1024 px, Canny σ=1.0, thresholds auto (Otsu). Biases: jpeg compression reduces D; photograph vs. render differences. |

#### ATTR-F2: 1/f Spectral Slope

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "natural balance," "visual harmony," "not too busy, not too plain" |
| **Causally active variable** | Spectral slope β in power spectrum P(f) ∝ 1/f^β; natural scenes: β ≈ 2.0 (1.8-2.2) |
| **Definition** | Rate at which spatial frequency power falls off; natural images have approximately 1/f² amplitude spectra |
| **Vision algorithm** | (1) Convert to grayscale → (2) 2D FFT → (3) radially averaged power spectrum → (4) log-log regression; β = |slope| |
| **Implementation** | `numpy.fft.fft2` + radial averaging; or `scikit-image` spectral analysis |
| **Theoretical warrant** | Efficient coding hypothesis (Barlow, 1961; Simoncelli & Olshausen, 2001): V1 neurons evolved for 1/f² statistics. Deviations from natural statistics increase processing cost. |
| **Evidence** | STRONG for 1/f² as natural statistic; MODERATE for preference link. Redies et al. (2007, ~200 cit): artworks tend toward natural spectral statistics. Graham & Field (2007, ~150 cit): aesthetic preference correlates with 1/f adherence. |
| **CVA constraints** | prediction_error, load_rate |

#### ATTR-F3: Lacunarity

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "gappiness," "sparse vs. dense texture," "regularity of holes" |
| **Causally active variable** | Lacunarity Λ: measures texture "gappiness" — how the fractal fills space (a fractal can have the same D but different lacunarity) |
| **Vision algorithm** | (1) Binary edge map → (2) gliding-box algorithm at multiple box sizes r → (3) Λ(r) = var(mass) / mean(mass)²; report Λ at characteristic scales |
| **Implementation** | Custom Python (numpy), or `fractalpy.lacunarity` |
| **Theoretical warrant** | Distinguishes "clumped" from "uniform" fractal patterns — relevant because natural fractals (trees, coastlines) tend to have specific lacunarity profiles that differ from synthetic fractals. |
| **Evidence** | MODERATE. Taylor et al. (2011): lacunarity affects preference independently of D. Less studied than D. |
| **CVA constraints** | prediction_error, figure_ground_separation |

#### ATTR-F4: Edge Density and Distribution

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "busy," "clean," "cluttered," "streamlined" |
| **Causally active variable** | Edge pixel density (proportion of image that is edge), and spatial distribution of edges (uniform vs. clustered) |
| **Vision algorithm** | (1) Canny edge detection → (2) edge pixel count / total pixels = density; (3) spatial entropy of edge distribution (divide into NxN grid, compute Shannon entropy of edge counts per cell) |
| **Implementation** | OpenCV Canny + numpy grid binning |
| **Theoretical warrant** | Processing fluency: higher edge density → more feature processing → higher cognitive load. Spatial clustering of edges increases local complexity unevenly. |
| **Evidence** | STRONG for edge density → complexity perception (Machado et al., 2015, ~150 cit). MODERATE for direct link to stress/preference. |
| **CVA constraints** | load_rate, prediction_error |

### 2.2 Color Science Attributes

These attributes capture the hypothesis that color properties of environments have direct physiological and affective effects through chromatic adaptation, circadian pathways (melanopsin), and learned color associations.

#### ATTR-C1: Correlated Color Temperature (CCT)

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "warm lighting," "cool/clinical," "daylight quality," "cozy" |
| **Causally active variable** | CCT in Kelvin: warm (2700-3500K), neutral (3500-5000K), cool (5000-6500K), daylight (6500K+) |
| **Vision algorithm** | (1) Extract illuminant from image (gray-world assumption or learning-based: CNN illuminant estimator) → (2) Convert illuminant RGB to CIE xy chromaticity → (3) Map to Planckian locus → CCT via McCamy's approximation: CCT = 449n³ + 3525n² + 6823.3n + 5520.33, where n = (x - 0.3320)/(0.1858 - y) |
| **Implementation** | `colour-science` Python library: `colour.temperature.CCT_to_xy()`, or OpenCV white balance + custom mapping |
| **Theoretical warrant** | Kruithof (1941): pleasant lighting falls within specific CCT-illuminance combinations. Circadian health: CCT > 5000K suppresses melatonin via melanopsin (ipRGC pathway). Cultural calibration: East Asian preference for 5000-6500K vs. Western 2700-3000K (CH-7 finding). |
| **Evidence** | STRONG for physiological pathway (Brainard et al., 2001, ~2,800 cit; Cajochen et al., 2005, ~1,200 cit). MODERATE for preference (varies by culture). |
| **CVA constraints** | temporal_coherence, prediction_error (cultural expectation) |
| **Cultural note** | This is a Tier 2 ψ-calibrated attribute — the optimal CCT depends on cultural exposure history. |

#### ATTR-C2: Chromatic Distribution (CIE Lab)

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "colorful," "muted," "earth tones," "vibrant" |
| **Causally active variable** | Distribution of pixel values in CIE Lab space: mean(L*, a*, b*), std(a*, b*), gamut area |
| **Vision algorithm** | (1) Convert RGB→Lab (D65 illuminant) → (2) Compute statistics: mean L* (lightness), mean a* (green-red), mean b* (blue-yellow), std of a* and b* (chromatic variance), gamut area (convex hull of a*,b* points) |
| **Implementation** | `skimage.color.rgb2lab()` or OpenCV `cv2.cvtColor(img, cv2.COLOR_BGR2Lab)` |
| **Theoretical warrant** | Color harmony theory (Ou et al., 2004): certain Lab distributions are judged harmonious. Environmental color psychology (Kwallek et al., 1996): red environments increase arousal, blue environments decrease it (mediated by a* axis). |
| **Evidence** | MODERATE. Meta-analyses show small but reliable color-mood effects (Elliot & Maier, 2014, ~1,500 cit). Effect sizes often small and context-dependent. |
| **CVA constraints** | prediction_error, load_rate |

#### ATTR-C3: Green Chromaticity (Biophilic Color Signal)

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "greenery," "lush," "nature view," "garden visible" |
| **Causally active variable** | Proportion of pixels in green chromaticity range: a* < -10 in CIE Lab, AND L* > 25 (excludes dark/shadow pixels) |
| **Vision algorithm** | (1) RGB→Lab → (2) threshold: pixels where a* < -10 AND L* > 25 → (3) green ratio = green_pixels / total_pixels; also compute Green View Index (GVI) variant: green_pixels / non-sky_pixels |
| **Implementation** | OpenCV color conversion + numpy masking. For more precise: semantic segmentation (DeepLabV3+ or SegFormer) to identify vegetation class, then compute area ratio. |
| **Theoretical warrant** | Biophilia hypothesis (Wilson, 1984): evolved preference for nature indicators. Green specifically: associated with water availability, resource richness in savanna evolutionary environment (Orians, 1986). Green chromaticity as a "fast-and-frugal" visual heuristic for nature detection. |
| **Evidence** | STRONG for green view → wellbeing (Li et al., 2015, ~200 cit for GVI; Ulrich, 1984, ~8,000 cit for nature views). MODERATE for green color specifically (vs. nature form — the decomposition question). |
| **CVA constraints** | prediction_error (evolutionary expectation match), narrative_coherence |

### 2.3 Spatial / Geometric Attributes

These attributes capture the hypothesis that spatial configuration — independent of content — affects psychological responses through evolved mechanisms for navigation, threat detection, and resource evaluation.

#### ATTR-S1: Isovist Area and Properties

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "open," "spacious," "panoramic view," "enclosed," "claustrophobic" |
| **Causally active variable** | Isovist area (m²), isovist perimeter, compactness (4π·area/perimeter²), occlusivity (occluded perimeter / total perimeter), drift (distance from viewpoint to isovist centroid) |
| **Vision algorithm** | FROM 2D FLOOR PLAN: (1) Parse walls from image (Hough lines or ML wall detector) → (2) Cast rays at 1° intervals from viewpoint → (3) Compute intersection with walls → (4) Compute isovist polygon → area, perimeter, compactness, radial lengths. FROM PHOTOGRAPH: (1) Monocular depth estimation (MiDaS or DPT) → (2) Threshold depth to estimate visible volume → (3) Approximate isovist properties from depth map statistics: mean depth ≈ prospect, depth variance ≈ spatial complexity. |
| **Implementation** | Floor plans: `shapely` polygon operations + ray casting. Photos: `torch.hub.load('intel-isl/MiDaS')` for depth → numpy statistics |
| **Theoretical warrant** | Prospect-refuge theory (Appleton, 1975): evolved preference for spaces offering visual overview (prospect = large isovist area) with nearby enclosure (refuge = low local isovist). Benedikt (1979): isovist as fundamental unit of spatial experience. |
| **Evidence** | STRONG for prospect-refuge effects on preference and safety perception (Dosen & Ostwald, 2016, ~150 cit). MODERATE for specific isovist metric → outcome mappings. |
| **CVA constraints** | control_efficacy, prediction_error |

#### ATTR-S2: Ceiling Height / Vertical Proportion

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "soaring ceilings," "intimate," "lofty," "low ceiling," "cathedral" |
| **Causally active variable** | Ratio of vertical to horizontal extent; estimated ceiling height (m) |
| **Vision algorithm** | (1) Vanishing point detection (Hough lines → intersection) → (2) Identify ceiling plane (top vanishing region) → (3) Estimate vertical-to-horizontal ratio from perspective geometry. OR: (1) Monocular depth estimation → (2) Identify ceiling plane from depth discontinuities → (3) Estimate height from depth + camera parameters. Simple proxy: vertical gradient in depth map. |
| **Implementation** | OpenCV Hough lines + vanishing point geometry; or MiDaS depth + plane fitting |
| **Theoretical warrant** | Meyers-Levy & Zhu (2007, ~1,300 cit): high ceilings activate "freedom" concepts → abstract/creative thinking; low ceilings activate "confinement" → detail-oriented thinking. Mechanism: spatial metaphor through embodied cognition (Lakoff & Johnson, 1999). |
| **Evidence** | MODERATE-STRONG. Replicated in multiple studies but effect sizes vary. Cultural calibration needed (CH-4: JP ~2.4m baseline vs. US ~2.7m). |
| **CVA constraints** | control_efficacy, prediction_error |
| **Cultural note** | Tier 2 ψ-calibrated. The "high" threshold depends on cultural baseline expectation. |

#### ATTR-S3: Enclosure Ratio

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "cozy," "open plan," "walled," "exposed," "sheltered" |
| **Causally active variable** | Ratio of opaque vertical surface area to total visual field; proportion of visual field that is "bounded" |
| **Vision algorithm** | (1) Semantic segmentation (SegFormer/DeepLabV3+) → (2) Classify wall/ceiling/floor/window/opening → (3) enclosure_ratio = wall_pixels / (wall_pixels + window_pixels + opening_pixels); also sky_visibility = sky_pixels / upper_hemisphere_pixels |
| **Implementation** | Pre-trained semantic segmentation on ADE20K (includes wall, ceiling, window, door categories) |
| **Theoretical warrant** | Refuge theory (Appleton, 1975): enclosure provides protection/refuge. Over-enclosure → confinement anxiety. Optimal enclosure varies with activity frame (work: moderate; rest: high; exploration: low). |
| **Evidence** | STRONG for enclosure → safety perception (Stamps, 2005; Dosen & Ostwald, 2016). Activity-dependent modulation less studied. |
| **CVA constraints** | control_efficacy, prediction_error |

#### ATTR-S4: Spatial Legibility

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "easy to navigate," "confusing layout," "clear organization," "maze-like" |
| **Causally active variable** | Degree to which spatial organization can be understood and mentally mapped; operationalized as depth/integration from space syntax or as landmark visibility/distinctiveness |
| **Vision algorithm** | FROM FLOOR PLAN: space syntax (axial analysis, visibility graph analysis). FROM PHOTOGRAPH: (1) Scene classification (corridor/room/junction/stairway) → (2) Vanishing point count (1 = corridor, 2+ = junction → more legible if clear hierarchy) → (3) Depth variation (high variance = more spatial information). Proxy from photo: number of distinct depth planes. |
| **Implementation** | Floor plans: `depthmapX` or `sDNA` for space syntax. Photos: vanishing point detection + depth histogram analysis |
| **Theoretical warrant** | Lynch (1960, ~15,000 cit): imageability as basis of wayfinding. Kaplan's (1989) information model: legibility = "promise of finding one's way." |
| **Evidence** | STRONG for legibility → wayfinding performance and preference (Lynch, 1960; Weisman, 1981). MODERATE for neural pathway (hippocampal place cell activation). |
| **CVA constraints** | prediction_error, load_rate, control_efficacy |

### 2.4 Material / Texture Attributes

These attributes capture the hypothesis that surface materials affect psychological responses through visual texture processing, haptic expectations (affordance perception from vision), and material associations (natural vs. synthetic → biophilic response).

#### ATTR-M1: Material Naturalness Index

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "natural materials," "wood paneling," "stone walls," "plastic/synthetic" |
| **Causally active variable** | Proportion of visible surfaces classified as natural materials (wood, stone, brick, plant material, earth) vs. synthetic (plastic, painted drywall, metal, glass) |
| **Vision algorithm** | (1) Semantic segmentation or material recognition CNN (Materials in Context database, OpenSurfaces) → (2) Classify each surface patch as natural/synthetic → (3) naturalness_index = natural_surface_area / total_surface_area |
| **Implementation** | Fine-tuned ResNet/EfficientNet on Materials in Context (MINC-2500, Bell et al., 2015) — 23 material categories. Or CLIP zero-shot: "wood surface" / "stone surface" / "plastic surface" etc. |
| **Theoretical warrant** | Biophilia (Wilson, 1984): preference for natural materials evolved. Material authenticity: natural materials have richer microstructure (higher fractal D) → more visually engaging. Nyrud & Bringslimark (2010): wood surfaces specifically reduce stress and increase wellbeing. |
| **Evidence** | MODERATE-STRONG for wood specifically (Nyrud & Bringslimark, 2010, ~200 cit; Fell, 2010, ~100 cit). Less evidence for other natural materials individually. General biophilia evidence STRONG. |
| **CVA constraints** | prediction_error (evolutionary match), spatial_frequency_match |

#### ATTR-M2: Haptic Expectation from Visual Input

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "looks warm/cold," "inviting to touch," "smooth," "rough-looking" |
| **Causally active variable** | Predicted haptic qualities inferred from visual texture: warmth (thermal diffusivity expectation), roughness (surface profile expectation), hardness (elastic deformation expectation) |
| **Vision algorithm** | (1) Texture analysis: Gabor filter bank (6 orientations × 4 scales) → mean response per filter = texture descriptor → (2) Map to haptic predictions via trained regression (Visual→Haptic transfer model) → predicted roughness, predicted warmth, predicted hardness. OR: (1) Material classification (ATTR-M1) → (2) Lookup table: wood → warm+medium_rough, stone → cold+smooth, fabric → warm+soft, metal → cold+smooth+hard, concrete → cold+rough+hard. |
| **Implementation** | Gabor filters: `skimage.filters.gabor()`. Transfer model: pre-trained on Tiest & Kappers (2007) visual-haptic correspondence data. Simpler: material class → haptic lookup. |
| **Theoretical warrant** | Cross-modal prediction (Lacey & Sathian, 2014, ~200 cit): visual system automatically generates haptic expectations. Materials that "look warm" reduce stress through anticipated thermal comfort. Gibson's affordance theory (1979): surfaces are perceived in terms of what they afford for action (graspable, supportable, touchable). |
| **Evidence** | MODERATE. Visual-haptic correspondences well-established psychophysically. Direct link to wellbeing outcomes less studied but emerging (Wastiels et al., 2012: visual warmth of materials affects comfort ratings). |
| **CVA constraints** | prediction_error, affordance_density |
| **Note** | This is a paradigmatic example of David's insight about causally active variables: the everyday descriptor is "wood feels warm" but the causally active visual variable is the texture statistics that generate the haptic prediction. |

#### ATTR-M3: Olfactory Expectation from Visual Input

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "fresh," "stuffy-looking," "garden-like," "industrial" |
| **Causally active variable** | Predicted olfactory qualities inferred from visual scene content: freshness expectation, nature scent expectation, chemical/industrial expectation |
| **Vision algorithm** | (1) Object/material detection → (2) Olfactory association model: plants → nature scent; water → freshness; wood → warmth/cedar; concrete → industrial; books → paper/dust → (3) Olfactory expectation vector (fresh_0-1, natural_0-1, chemical_0-1, food_0-1) |
| **Implementation** | CLIP zero-shot classification: score scene against olfactory prompts ("a room that smells fresh," "a room that smells stuffy," etc.) → softmax probabilities as olfactory expectation vector |
| **Theoretical warrant** | Cross-modal associations (Spence, 2011, ~300 cit): vision generates expectations about other modalities. Olfactory-visual congruence affects spatial experience (Herz & Engen, 1996). The prediction error from olfactory-visual mismatch (e.g., a garden that smells of exhaust) is aversive. |
| **Evidence** | WEAK-MODERATE. Cross-modal association literature is strong, but specific visual→olfactory prediction in architectural contexts is understudied. An emerging area. |
| **CVA constraints** | multisensory_coherence, prediction_error |
| **Note** | This attribute is more speculative than others but represents exactly the kind of causal decomposition that reveals hidden assumptions: when someone reports that "a room with plants felt fresh," part of the effect may be the visual→olfactory prediction (expected scent), not just the visual fractal/green properties. |

### 2.5 Biophilic Pattern Attributes

#### ATTR-B1: Biomorphic Form Index

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "organic shapes," "flowing forms," "natural curves" |
| **Causally active variable** | Proportion of curvilinear vs. rectilinear contours in the scene; curvature statistics of detected edges |
| **Vision algorithm** | (1) Edge detection → (2) Contour extraction → (3) For each contour: compute curvature at each point (κ = dθ/ds) → (4) biomorphic_index = mean(|κ|) weighted by contour length; also: curvilinear_ratio = curved_edge_length / total_edge_length (where "curved" = κ > threshold) |
| **Implementation** | OpenCV `findContours()` + curvature computation via finite differences on contour points |
| **Theoretical warrant** | Bar & Neta (2006, ~800 cit): sharp-angled objects perceived as more threatening than curved objects (amygdala activation). Vartanian et al. (2013, ~300 cit): curved architectural contours preferred and activate reward circuitry. Evolutionary: curved forms in nature → non-threat; sharp angles → potential danger/manufactured tools. |
| **Evidence** | STRONG for curved vs. angular preference (Bar & Neta, 2006; Vartanian et al., 2013). MODERATE for specific threshold values and built environment contexts. |
| **CVA constraints** | prediction_error (threat detection), symmetry_regularity |

#### ATTR-B2: Water Feature Presence

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "fountain," "pond," "water wall," "reflecting pool" |
| **Causally active variable** | Presence and type of water features: still water (reflection), flowing water (auditory expectation), coverage area |
| **Vision algorithm** | (1) Semantic segmentation → water class detection → (2) Water type classification: still (flat, reflective surface → low texture variance in detected region) vs. flowing (high texture variance, possible motion blur) → (3) water_coverage = water_pixels / total_pixels |
| **Implementation** | ADE20K segmentation (includes water, river, sea, pool, fountain classes); or CLIP zero-shot with water feature prompts |
| **Theoretical warrant** | Prospect-refuge theory extension: water indicates resource availability. Blue space research (Gascon et al., 2017, ~400 cit): proximity to water improves mental health. Auditory dimension: even visual water generates expected sound (flowing water as auditory masking → privacy). |
| **Evidence** | STRONG for blue space → wellbeing at landscape scale (Gascon et al., 2017; White et al., 2020, ~500 cit). MODERATE for indoor water features specifically. |
| **CVA constraints** | prediction_error (resource signal), multisensory_coherence (visual→auditory expectation) |

#### ATTR-B3: Biophilic Design Score (Composite)

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "biophilic design," "nature-inspired," "living building" |
| **Causally active variable** | Composite score across Kellert & Calabrese's (2015) 14 biophilic patterns, assessed from visual evidence |
| **Vision algorithm** | Compute sub-scores for detectable patterns: (1) Visual connection with nature (green ratio + water presence), (2) Non-visual connection with nature (implied from material → olfactory/haptic), (3) Non-rhythmic sensory stimuli (dynamic elements, dappled light), (4) Thermal & airflow variability (not directly from image), (5) Presence of water (ATTR-B2), (6) Dynamic & diffuse light (light variation in image), (7) Connection with natural systems (time-of-day indicators), (8) Biomorphic forms (ATTR-B1), (9) Material connection with nature (ATTR-M1), (10) Complexity & order (ATTR-F1 fractal D), (11) Prospect (ATTR-S1), (12) Refuge (enclosure local regions), (13) Mystery (depth gradient, partially occluded spaces), (14) Risk/peril (height, cantilever, glass floor). Score: sum of detected / 14. |
| **Implementation** | Composite of other ATTR scores + scene-level CLIP classification for non-computable patterns |
| **Theoretical warrant** | Kellert & Calabrese (2015): 14 patterns of biophilic design. Each pattern hypothesized to trigger evolved responses. The composite aggregates. |
| **Evidence** | MODERATE. Individual patterns well-supported (prospect-refuge STRONG, fractals STRONG, materials MODERATE). The composite scoring is less validated — relative weighting unknown. |
| **CVA constraints** | Multiple: prediction_error, control_efficacy, narrative_coherence |

### 2.6 Processing Fluency Attributes

#### ATTR-P1: Figure-Ground Clarity

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "clear layout," "objects pop out," "everything blends together," "hard to make out" |
| **Causally active variable** | Degree to which foreground objects are distinguishable from background surfaces; measured as contrast at object boundaries |
| **Vision algorithm** | (1) Salient object detection (U²-Net or TRACER) → (2) Compute contrast at boundary: mean|foreground_luminance - background_luminance| → (3) figure_ground_clarity = boundary_contrast / max_possible_contrast |
| **Implementation** | `torch.hub.load()` U²-Net for saliency; boundary contrast via numpy operations on luminance channel |
| **Theoretical warrant** | Perceptual fluency theory (Reber et al., 2004, ~2,500 cit): stimuli that are easier to process are judged more positively. Figure-ground segregation is a fundamental perceptual operation; difficulty → negative affect. Gestalt: good figure-ground organization → "good form." |
| **Evidence** | STRONG for fluency → positive evaluation (Reber et al., 2004). MODERATE for specific figure-ground → architectural preference link. |
| **CVA constraints** | figure_ground_separation, prediction_error |

#### ATTR-P2: Symmetry Score

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "balanced," "formal," "symmetric," "lopsided" |
| **Causally active variable** | Degree of bilateral symmetry in the scene, measured as similarity between left-right halves |
| **Vision algorithm** | (1) Convert to grayscale → (2) Flip image horizontally → (3) symmetry_score = 1 - RMSE(original, flipped) / max_RMSE; also compute: rotational symmetry (auto-correlation at rotations), and local symmetry (SIFT keypoint matching between halves) |
| **Implementation** | numpy operations for global; SIFT keypoints via OpenCV for local symmetry |
| **Theoretical warrant** | Evolutionary aesthetics: symmetry detection → mate quality assessment (Møller, 1992). Perceptual fluency: symmetric patterns processed faster (Reber et al., 2004). Cultural note: Western preference for bilateral symmetry may not generalize (CH-6: West African fractal/organic layouts). |
| **Evidence** | STRONG for symmetry preference in general (Bertamini et al., 2013, ~200 cit). MODERATE for architectural symmetry specifically. Cultural variation significant. |
| **CVA constraints** | symmetry_regularity, prediction_error |
| **Cultural note** | Tier 2 ψ-calibrated. Optimal symmetry level depends on cultural exposure. |

### 2.7 Social / Affordance Attributes

#### ATTR-A1: Sitting Affordance Density

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "lots of seating," "nowhere to sit," "inviting benches" |
| **Causally active variable** | Number and variety of sittable surfaces per unit visible floor area |
| **Vision algorithm** | (1) Object detection (YOLO/Faster R-CNN on furniture dataset) → detect chairs, benches, sofas, ledges → (2) sitting_density = count / estimated_floor_area; (3) variety_index = Shannon entropy of sitting types |
| **Implementation** | Pre-trained YOLO on COCO (includes chair, couch, bench) + Open Images v7 for more furniture |
| **Theoretical warrant** | Gibson (1979): affordances are directly perceived opportunities for action. Sitting affordance → rest possibility → safety signal. Gehl (2011, ~5,000 cit): street furniture density predicts lingering behavior. |
| **Evidence** | STRONG for sitting availability → dwell time (Gehl, 2011; Whyte, 1980, ~3,000 cit). The "sittable ledge" finding from Whyte is classic. |
| **CVA constraints** | affordance_density, control_efficacy |

#### ATTR-A2: Social Density Inference

| Field | Value |
|-------|-------|
| **Everyday descriptors** | "crowded," "empty," "buzzing," "desolate" |
| **Causally active variable** | Expected occupancy level from spatial layout: desk density, seating arrangement (clustered vs. distributed), corridor width → predicted density |
| **Vision algorithm** | (1) Detect furniture/workstations → (2) Estimate capacity from layout → (3) If people visible: person detection (YOLO) → actual count / estimated capacity = occupancy rate; (4) If empty: predict expected occupancy from furniture density |
| **Implementation** | YOLO person detection + furniture counting; or CLIP scene classification: "crowded room" vs "empty room" confidence |
| **Theoretical warrant** | Crowding theory (Stokols, 1972): perceived crowding depends on density × control × expectation. High density with low control → stress. The image attribute captures the *expected* social density from spatial cues. |
| **Evidence** | STRONG for crowding → stress (Evans, 1979, ~500 cit; Saegert, 1973). MODERATE for visual prediction of social density specifically. |
| **CVA constraints** | social_cue_density, control_efficacy |

---

## 3. Summary: The Translation Table

This is the core deliverable — mapping everyday experimental descriptors to causally active variables with vision algorithms.

| Everyday Descriptor | Causally Active Variable(s) | Extraction Method | Theoretical Warrant | Evidence |
|---|---|---|---|---|
| "rooms with plants" | Fractal D (1.3-1.5), green chromaticity (a*<-10), biomorphic curves, olfactory expectation | ATTR-F1 + ATTR-C3 + ATTR-B1 + ATTR-M3 | ART (Kaplan), Biophilia (Wilson), Efficient Coding | STRONG |
| "natural materials" | Material naturalness index, surface texture statistics, haptic warmth prediction | ATTR-M1 + ATTR-M2 | Biophilia, cross-modal prediction (Lacey & Sathian) | MODERATE-STRONG |
| "high ceilings" | Vertical proportion ratio, estimated height (m), depth map vertical extent | ATTR-S2 | Embodied cognition (Lakoff & Johnson), conceptual metaphor | MODERATE-STRONG |
| "open space" | Isovist area, depth mean, enclosure ratio, sky visibility | ATTR-S1 + ATTR-S3 | Prospect-refuge (Appleton), space syntax (Hillier) | STRONG |
| "good lighting" | CCT (K), illuminance distribution, daylight factor, light uniformity | ATTR-C1 + diffuse/direct ratio | Kruithof, circadian biology, visual comfort | STRONG |
| "nature views" | Green ratio (GVI), fractal D of visible vegetation, depth to natural elements, water presence | ATTR-C3 + ATTR-F1 + ATTR-B2 | Biophilia, ART (Kaplan), Blue Space | STRONG |
| "cluttered" | Edge density, visual entropy, object count, clutter density | ATTR-F4 + compression ratio | Processing fluency (Reber), cognitive load | STRONG |
| "cozy" | Enclosure ratio (0.5-0.7), warm CCT (<3500K), haptic warmth, material naturalness | ATTR-S3 + ATTR-C1 + ATTR-M2 + ATTR-M1 | Refuge, thermal comfort expectation | MODERATE |
| "peaceful" | Low edge density, fractal D in optimal range, green chromaticity, water presence | ATTR-F4 + ATTR-F1 + ATTR-C3 + ATTR-B2 | ART (all 4 components), stress reduction pathway | STRONG |
| "confusing layout" | Low spatial legibility, high depth variance, few landmarks, many choice points | ATTR-S4 | Lynch imageability, wayfinding theory | STRONG |
| "beautiful" | Fractal D optimal, 1/f² spectral match, symmetry, figure-ground clarity, curvature | ATTR-F1 + ATTR-F2 + ATTR-P2 + ATTR-P1 + ATTR-B1 | Processing fluency, neuroaesthetics | MODERATE |
| "warm/inviting" | Warm CCT (<3500K), material warmth, wood surfaces, biomorphic forms | ATTR-C1 + ATTR-M2 + ATTR-M1 + ATTR-B1 | Cross-modal prediction, material psychology | MODERATE |

---

## 4. Implementation Priority

### Tier 1: Implementable now with standard CV libraries

| Attribute | Library | Complexity |
|-----------|---------|------------|
| ATTR-F1 (Fractal D) | OpenCV + numpy | Low — well-defined algorithm |
| ATTR-F2 (1/f slope) | numpy FFT | Low |
| ATTR-F4 (Edge density) | OpenCV Canny | Low |
| ATTR-C2 (Lab distribution) | skimage/OpenCV | Low |
| ATTR-C3 (Green ratio) | OpenCV + numpy | Low |
| ATTR-P2 (Symmetry) | OpenCV + numpy | Low |

### Tier 2: Requires pre-trained models

| Attribute | Model | Source |
|-----------|-------|--------|
| ATTR-S1 (Isovist from photo) | MiDaS depth estimation | torch.hub / HuggingFace |
| ATTR-S2 (Ceiling height) | MiDaS + plane fitting | torch.hub |
| ATTR-S3 (Enclosure) | SegFormer/DeepLabV3+ on ADE20K | HuggingFace |
| ATTR-M1 (Material naturalness) | MINC-2500 or CLIP | HuggingFace |
| ATTR-B1 (Biomorphic forms) | OpenCV contours + curvature | Medium complexity |
| ATTR-P1 (Figure-ground) | U²-Net saliency | torch.hub |
| ATTR-A1 (Sitting affordance) | YOLO on COCO | Ultralytics |

### Tier 3: Requires custom training or composition

| Attribute | Approach | Notes |
|-----------|----------|-------|
| ATTR-C1 (CCT) | Illuminant estimation CNN + Planckian locus | colour-science library |
| ATTR-M2 (Haptic prediction) | Material class → lookup; or trained regression | Novel but feasible |
| ATTR-M3 (Olfactory prediction) | CLIP zero-shot | Speculative |
| ATTR-S4 (Legibility from photo) | Composite: VP detection + depth + scene class | Complex |
| ATTR-A2 (Social density) | YOLO + furniture counting + capacity model | Medium |
| ATTR-B3 (Biophilic composite) | Aggregation of other ATTR scores | Depends on component ATTRs |

---

## 5. References

Appleton, J. (1975). *The experience of landscape*. Wiley.

Bar, M., & Neta, M. (2006). Humans prefer curved visual objects. *Psychological Science, 17*(8), 645-648.

Bechtel, W., & Abrahamsen, A. (2005). Explanation: A mechanist alternative. *Studies in History and Philosophy of Science Part C, 36*(2), 421-441.

Benedikt, M. L. (1979). To take hold of space: Isovists and isovist fields. *Environment and Planning B, 6*(1), 47-65.

Craver, C. F. (2007). *Explaining the brain: Mechanisms and the mosaic unity of neuroscience*. Oxford University Press.

Dosen, A. S., & Ostwald, M. J. (2016). Evidence for prospect-refuge theory: A meta-study of the findings of environmental preference research. *City, Territory and Architecture, 3*(4), 1-14.

Gehl, J. (2011). *Life between buildings: Using public space*. Island Press.

Gibson, J. J. (1979). *The ecological approach to visual perception*. Houghton Mifflin.

Hagerhall, C. M., Purcell, T., & Taylor, R. P. (2004). Fractal dimension of landscape silhouette outlines as a predictor of landscape preference. *Journal of Environmental Psychology, 24*(2), 247-255.

Hanson, N. R. (1958). *Patterns of discovery*. Cambridge University Press.

Kaplan, S. (1995). The restorative benefits of nature: Toward an integrative framework. *Journal of Environmental Psychology, 15*(3), 169-182.

Kellert, S. R., & Calabrese, E. F. (2015). *The practice of biophilic design*. www.biophilic-design.com.

Lynch, K. (1960). *The image of the city*. MIT Press.

Meyers-Levy, J., & Zhu, R. (2007). The influence of ceiling height: The effect of priming on the type of processing that people use. *Journal of Consumer Research, 34*(2), 174-186.

Reber, R., Schwarz, N., & Winkielman, P. (2004). Processing fluency and aesthetic pleasure: Is beauty in the perceiver's processing experience? *Personality and Social Psychology Review, 8*(4), 364-382.

Simoncelli, E. P., & Olshausen, B. A. (2001). Natural image statistics and neural representation. *Annual Review of Neuroscience, 24*(1), 1193-1216.

Spehar, B., Clifford, C. W. G., Newell, B. R., & Taylor, R. P. (2003). Universal aesthetic of fractals. *Computers & Graphics, 27*(5), 813-820.

Taylor, R. P., Spehar, B., Van Donkelaar, P., & Hagerhall, C. M. (2011). Perceptual and physiological responses to Jackson Pollock's fractals. *Frontiers in Human Neuroscience, 5*, 60.

Vartanian, O., Navarrete, G., Chatterjee, A., Fich, L. B., Leder, H., Modroño, C., ... & Skov, M. (2013). Impact of contour on aesthetic judgments and approach-avoidance decisions in architecture. *Proceedings of the National Academy of Sciences, 110*(Supplement 2), 10446-10453.

Whyte, W. H. (1980). *The social life of small urban spaces*. Conservation Foundation.

Wilson, E. O. (1984). *Biophilia*. Harvard University Press.

Woodward, J. (2003). *Making things happen: A theory of causal explanation*. Oxford University Press.
