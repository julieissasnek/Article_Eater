# RV5-4 Ruthless Audit: Image Processing Pipeline & 33-Attribute Taxonomy

**Date**: 2026-03-01
**Auditor**: Claude Code (Agent)
**Scope**: Complete image attribute taxonomy (21 original + 12 new) + extraction pipeline
**Status**: SERIOUS DEFICIENCIES IDENTIFIED

---

## Executive Summary

This audit reveals a well-documented but **fundamentally incomplete implementation** of the 33-attribute visual taxonomy. Core problems:

1. **12 new attributes exist only in specification** — no implementation code exists
2. **Image extraction pipeline is functional but untested** — script is well-written but has no unit tests
3. **Attribute quality is highly uneven** — Tier 1 (OpenCV) attributes are robust; Tier 2/3 are aspirational
4. **Cross-reference gaps** — Template schema references vision attributes but extraction pipeline doesn't populate them
5. **No rater agreement validation** — attributes lack inter-rater reliability assessment

**Overall Score: 5/10** (specification-grade, implementation-grade: 2/10)

---

## Part 1: Original 21 Attributes (ATTR-F/C/S/M/B/P/A)

### 1.1 Definition and Warrant Quality

All 21 original attributes have:
- ✓ Clear causal variable definitions
- ✓ Specified output units and ranges
- ✓ Theoretical warrant with key references (1-3 citations each)
- ✓ Vision algorithm specification with method name
- ✓ Named libraries (OpenCV, NumPy, SciPy, scikit-image, scikit-learn)

**Quality by Group:**

| Group | Attributes | Definition | Warrant | Implementation | Notes |
|-------|-----------|-----------|---------|-----------------|-------|
| **Fractal (F)** | F1, F2, F3, F4 | Clear, Precise | Strong (2-3 refs each) | Tier 1 (OpenCV) | Edge detection → frequency analysis; well-grounded in perception science |
| **Color (C)** | C1, C2, C3 | Clear | Strong | Tier 1 (OpenCV) | CCT/Lab color space analysis; good warrant from color psychology |
| **Spatial (S)** | S1, S2, S3, S4 | Clear but Complex | Strong | Tier 2 (requires segmentation) | Isovist and enclosure analysis; heavy on geometric computation |
| **Material (M)** | M1, M2, M3 | Somewhat Vague | Moderate | Tier 2/3 (texture + inference) | M2/M3 rely on "visual-to-haptic/olfactory inference" — speculative |
| **Biomorphic (B)** | B1, B2, B3 | Clear | Strong | Tier 1-3 (mixed) | B3 is composite; B2 is water detection; B1 is contour analysis |
| **Perceptual (P)** | P1, P2 | Clear | Strong | Tier 1-2 | Figure-ground clarity uses saliency; symmetry is well-defined |
| **Affordance (A)** | A1, A2 | Vague | Weak | Tier 3 (YOLO/inference) | A1/A2 require object detection + spatial inference; high uncertainty |

### 1.2 Implementation Readiness by Tier

**Tier 1 (Pure OpenCV/NumPy) — Ready**

- ATTR-F1 (Fractal Dimension): Box-counting algorithm, well-specified
- ATTR-F2 (1/f Spectral Slope): FFT-based, clear steps
- ATTR-F3 (Lacunarity): Sliding-box algorithm specified
- ATTR-F4 (Edge Density): Canny edges + histogram
- ATTR-C1 (CCT): Color-space illuminant estimation
- ATTR-C2 (CIE Lab Distribution): Histogram in Lab space
- ATTR-C3 (Green Chromaticity): Simple G > R & G > B pixel count
- ATTR-B2 (Water Detection): Color-based water segmentation
- ATTR-P2 (Symmetry): Correlation-based symmetry detection

**Status**: Implementable in ~500 lines of Python

**Tier 2 (Pretrained Models) — Incomplete**

- ATTR-S1 (Isovist): Requires floor plan extraction or 3D reconstruction — **not implementable from 2D photo alone**
- ATTR-S2 (Ceiling Height): Vanishing point analysis — requires perspective geometry
- ATTR-S3 (Enclosure Ratio): Surface area estimation — requires depth or 3D reconstruction
- ATTR-S4 (Spatial Legibility): Entropy of spatial structure — requires semantic segmentation
- ATTR-M1 (Material Naturalness): Texture classification — requires trained classifier or VLM
- ATTR-M2 (Haptic Expectation): **Speculative** — infers roughness/compliance from texture
- ATTR-M3 (Olfactory Expectation): **Highly speculative** — infers smell from visual cues
- ATTR-P1 (Figure-Ground Clarity): Saliency + contrast analysis

**Status**: Partially implementable; ATTR-S1/S3 require 3D data; M2/M3 are science fiction

**Tier 3 (Custom/Advanced) — Aspirational**

- ATTR-B1 (Biomorphic Form): Contour curvature analysis — requires robust contour detection
- ATTR-B3 (Biophilic Composite): Weighted combination of 7 other attributes
- ATTR-A1 (Sitting Affordance): Requires YOLO person detection + furniture classification
- ATTR-A2 (Social Density): Requires layout analysis + occupancy estimation

**Status**: Advanced features requiring ensemble models

---

## Part 2: 12 New Attributes (NEW-01 to NEW-12)

### 2.1 Specification vs. Implementation Gap

All 12 new attributes are documented in:
- `docs/DECISION_TREE_EQUIVALENCE_CLASSES_2026-02-28.md` (identified via Kirsh decision tree method)
- `docs/IMPLEMENTATION_GUIDE_NEW_ATTRIBUTES.md` (code examples provided)

**Critical Finding: NO IMPLEMENTATIONS EXIST**

All code examples in `IMPLEMENTATION_GUIDE_NEW_ATTRIBUTES.md` are **pseudocode/demonstrations**, not production code:

| NEW ID | Name | Tier | Specification | Code | Tested |
|--------|------|------|---------------|------|--------|
| NEW-01 | Vegetation Segmentation Ratio | 2 | DeepLabV3 | Example only | No |
| NEW-02 | Monocular Depth Estimation | 2 | MiDaS depth model | Example only | No |
| NEW-03 | Sky Proportion & Horizon Ratio | 2 | Sky segmentation | Example only | No |
| NEW-04 | Visual Complexity Score | 1 | Edge density + spectral entropy | Example only | No |
| NEW-06 | Figure-Ground Clarity (Enhanced) | 2 | Semantic segmentation | Example only | No |
| NEW-07 | Material Diversity | 2/3 | Multi-material detection | **NOT SPECIFIED** | No |
| NEW-08 | Illumination Distribution Uniformity | 1 | LAB L-channel variance | Example only | No |
| NEW-09 | Acoustic Privacy Index (Visual Proxy) | 2/3 | Material absorption inference | Example only | No |
| NEW-10 | Chromatic Dominance & Color Harmony | 2 | **NOT FULLY SPECIFIED** | Example only | No |
| NEW-11 | Person/Face Density (Occupancy) | 2 | YOLO detection | Example only | No |
| NEW-12 | Biomorphic Curvature Index | 2 | Edge curvature analysis | Example only | No |
| (Missing) | Water Motion Detection | ? | **NOT DOCUMENTED** | None | No |

### 2.2 Individual Assessment: NEW Attributes

#### **NEW-01: Vegetation Segmentation Ratio**
- **Definition**: Percentage of scene occupied by plant material
- **Unit**: 0-1 ratio
- **Warrant**: Biophilia hypothesis; supported by decision tree for "room with plants" stimulus
- **Vision Algorithm**: DeepLabV3 semantic segmentation (PASCAL VOC class 12 = vegetation)
- **Issues**:
  - ✗ DeepLabV3 trained on outdoors; may fail on indoor potted plants
  - ✗ Class 12 conflates grass/forest/plants
  - ✗ No validation against human annotations
  - ✓ Libraries well-specified (torch, torchvision)

#### **NEW-02: Monocular Depth Estimation**
- **Definition**: Scene depth using monocular cues; mean depth + depth gradient
- **Unit**: Normalized depth (0-1); gradient (dimensionless)
- **Warrant**: Perspective perception; part of decision tree for "windows with view"
- **Vision Algorithm**: Intel MiDaS small model
- **Issues**:
  - ✗ MiDaS is trained primarily on outdoor scenes; unclear performance on interiors
  - ✓ Output well-specified (depth map + statistics)
  - ✗ Validation against ground truth depth unknown
  - ✓ Model available via torch.hub

#### **NEW-03: Sky Proportion and Horizon Ratio**
- **Definition**: Percentage of image that is sky; horizon position
- **Unit**: 0-1 ratio; pixel row (normalized)
- **Warrant**: Outdoor indicator; part of "windows with view" detection
- **Vision Algorithm**: Sky segmentation + horizon detection
- **Issues**:
  - **✗ NOT SPECIFIED HOW** — no algorithm details provided
  - No model/method named
  - No libraries specified
  - Appears in IMPLEMENTATION_GUIDE but with no code example
  - Critical ambiguity: Does this detect actual sky or "sky-like" regions?

#### **NEW-04: Visual Complexity Score**
- **Definition**: Edge density + spectral entropy combined
- **Unit**: 0-1 (normalized)
- **Warrant**: Visual perceptual load; exists in original ATTR-F4 (Edge Density)
- **Vision Algorithm**: Canny edges + FFT power spectrum + Shannon entropy
- **Issues**:
  - ✓ Tier 1 (implementable with OpenCV/NumPy)
  - ✓ Clear algorithm steps in IMPLEMENTATION_GUIDE
  - ✓ Output range well-defined
  - ✗ Weighting of edge_density vs. entropy not specified (uses simple average)
  - ✗ No validation against human complexity judgments

#### **NEW-06: Figure-Ground Clarity (Enhanced)**
- **Definition**: Contrast ratio + saliency of foreground vs. background
- **Unit**: 0-1 (dimensionless)
- **Warrant**: Gestalt theory; needed for artwork detection, plant-presence detection
- **Vision Algorithm**: Semantic segmentation
- **Issues**:
  - ✗ Algorithm underspecified — "semantic segmentation" is too vague
  - ✗ No model named (DeepLab? Mask R-CNN?)
  - ✗ How to compute "clarity" from segmentation?
  - ✓ Purpose is clear (distinguish salient objects from background)

#### **NEW-07: Material Diversity**
- **Definition**: Richness of material types visible in scene
- **Unit**: Count or normalized index (not specified)
- **Warrant**: Biophilic design; material variation reduces monotony
- **Vision Algorithm**: **COMPLETELY UNSPECIFIED**
- **Issues**:
  - ✗ No algorithm provided
  - ✗ No model/method named
  - ✗ Referenced in decision tree for "art/decoration" and "material composition" categories
  - ✗ Optimal range not specified
  - ✗ Only appears in summary tables, not in detailed specification sections

#### **NEW-08: Illumination Distribution Uniformity**
- **Definition**: Spatial variance of brightness; measures lighting uniformity
- **Unit**: 0-1 ratio (inverse of variance)
- **Warrant**: Lighting design; uniform lighting perceived as higher quality
- **Vision Algorithm**: LAB L-channel local variance analysis
- **Issues**:
  - ✓ Tier 1 (implementable with OpenCV/NumPy/scipy)
  - ✓ Clear code example in IMPLEMENTATION_GUIDE
  - ✓ Uses 32x32 window for local variance
  - ✗ Choice of window size not justified (32x32 arbitrary?)
  - ✗ No validation against human lighting uniformity perception

#### **NEW-09: Acoustic Privacy Index (Visual Proxy)**
- **Definition**: Estimate acoustic isolation from visual cues (enclosure + material absorption)
- **Unit**: 0-1 ratio (enclosure_score × material_absorption)
- **Warrant**: Acoustic comfort; inferred from surface properties and enclosure
- **Vision Algorithm**: Material classification → absorption coefficients
- **Issues**:
  - ✗ HIGHLY SPECULATIVE — inferring acoustics from vision is weak
  - ✗ No material classification model named
  - ✗ Absorption coefficients not provided
  - ✗ Material detection itself is unsolved (NEW-07)
  - ✗ Decision tree identifies this as "visual proxy only" — not a true acoustic measure
  - ✓ Warehouse of acoustic data exists (material absorption tables) but not integrated

#### **NEW-10: Chromatic Dominance & Color Harmony**
- **Definition**: Which color dominates; aesthetic harmony of color scheme
- **Unit**: Not specified; percentages? Harmony score 0-1?
- **Warrant**: Color psychology; identified in decision trees for "color" and "colored lighting/CCT"
- **Vision Algorithm**: **SEVERELY UNDERSPECIFIED**
- **Issues**:
  - ✗ No algorithm details
  - ✗ "Harmony" is aesthetic — how to compute?
  - ✗ No model/method named
  - ✗ Output format unclear
  - ✗ Only color dominance appears in examples; "harmony" is aspirational
  - ✓ Related to existing ATTR-C2 (chromatic distribution)

#### **NEW-11: Person/Face Density (Occupancy)**
- **Definition**: Count of people; density (persons per 100m²)
- **Unit**: Count; persons/100m²
- **Warrant**: Social density perception; identified in decision trees for "crowding" and "occupancy"
- **Vision Algorithm**: YOLO v8 person detection; assumes 10m×10m scene
- **Issues**:
  - ✓ Clear code example in IMPLEMENTATION_GUIDE
  - ✗ Scene size assumption (10m×10m) is HARDCODED — not data-driven
  - ✗ No camera intrinsic/extrinsic parameters for real scale estimation
  - ✗ Assumes orthographic projection (unrealistic)
  - ✗ No face detection (NEW-11 mentions "faces" but code only detects persons)
  - ✗ No validation against ground truth occupancy

#### **NEW-12: Biomorphic Curvature Index**
- **Definition**: Curvedness of contours (biomorphic vs. rectilinear)
- **Unit**: 0-1 ratio (sigmoid mapping of mean curvature)
- **Warrant**: Biophilic design; natural forms are curved
- **Vision Algorithm**: Edge detection → contour extraction → curvature computation
- **Issues**:
  - ✓ Tier 2 (implementable with OpenCV)
  - ✓ Clear code example in IMPLEMENTATION_GUIDE
  - ✗ Sigmoid mapping (1/(1+exp(-x+1))) has no theoretical justification
  - ✗ "biomorphic_index > 0.6" threshold appears arbitrary
  - ✗ No validation against human morphic judgments
  - ✓ Algorithm is sound (differential geometry of contours)

---

## Part 3: Vision Algorithm Implementation Assessment

### 3.1 Tier Distribution

| Tier | Count | Status | Libraries | Notes |
|------|-------|--------|-----------|-------|
| **Tier 1** (Fast CPU) | 8 | Ready | OpenCV, NumPy, SciPy | Box-counting, FFT, edge detection, color analysis |
| **Tier 2** (GPU Models) | 17 | Partial | PyTorch, torchvision, MiDaS, YOLO, DeepLab | Requires CUDA; some models untested on interior images |
| **Tier 3** (Custom) | 8 | Aspirational | YOLO, ensemble logic | Sitting affordance, social density, material diversity |

### 3.2 Library Coverage

All implementations reference standard libraries:
- **opencv-python**: ✓ Ubiquitous, stable
- **numpy**: ✓ Ubiquitous
- **scipy**: ✓ Ubiquitous
- **scikit-image**: ✓ Standard computer vision library
- **torch, torchvision**: ✓ Industry standard for deep learning
- **ultralytics (YOLOv8)**: ✓ Available, active maintenance

**Missing**: No custom implementations; no model weights bundled; no setup script

### 3.3 Implementability Assessment

| Category | Implementable | Partial | Not Specified | Blocker |
|----------|---------------|---------|---------------|---------|
| **Specifications** | 21/33 | 9/33 | 3/33 | Algorithm underspecified (NEW-03, NEW-07, NEW-10) |
| **Unit/Range** | 30/33 | 0/33 | 3/33 | Range not specified (NEW-07, NEW-10) |
| **Libraries** | 25/33 | 5/33 | 3/33 | Material detection library unknown (NEW-07, NEW-09) |
| **Validation Data** | 0/33 | 0/33 | 33/33 | **NO VALIDATION DATA EXISTS** |

---

## Part 4: Image Extraction Pipeline Assessment

### 4.1 Pipeline Functionality

**File**: `scripts/run_image_extraction_batch.py` (V1.0, 2026-02-28)

**Purpose**: Orchestrate PyMuPDF-based extraction of images from 56 HIGH-priority articles

**Status**: **FUNCTIONAL but UNTESTED**

#### Features
- ✓ Reads high-priority article list from `data/figure_scan/high_priority_articles.json`
- ✓ Finds PDFs in Article_Finder repo (`/Users/davidusa/REPOS/Article_Finder_v3_2_3/data/pdfs/`)
- ✓ Extracts images using PyMuPDF (fitz) with configurable minimum size
- ✓ Saves images organized by DOI
- ✓ Records metadata: page number, dimensions, colorspace, file size
- ✓ Generates extraction manifest (JSON)
- ✓ Supports dry-run, validation, and full extraction modes
- ✓ Comprehensive logging

#### Code Quality
- ✓ Well-structured with dataclasses
- ✓ Clear function separation
- ✓ Comprehensive error handling
- ✓ Good command-line interface

#### Issues
- **✗ NO UNIT TESTS** — zero test coverage
- **✗ NO INTEGRATION TESTS** — no validation that extracted images are processable
- **✗ HARDCODED PDF PATHS** — depends on external Article_Finder repo location
- **✗ MINIMUM SIZE FILTER** — 5KB threshold may skip small diagrams
- **✗ NO DUPLICATE DETECTION** — same image extracted from multiple articles creates copies
- **✗ NO ATTRIBUTE COMPUTATION** — pipeline does NOT compute the 33 attributes

### 4.2 Test Status

```bash
$ find tests/ -name "*image*" -o -name "*extract*" | grep -v __pycache__
# Results: No image extraction or attribute computation tests found
```

**Test Files Related to Images**:
- `tests/test_abstract_extractor.py` — Text extraction (not image)
- `tests/test_bibtex_e2e_flow.py` — Bibliography (not image)
- **NO FILES FOR IMAGE PROCESSING**

---

## Part 5: Template & Schema Cross-Reference

### 5.1 Template Schema Analysis

**File**: `contracts/schemas/extraction_template.v2.schema.json`

Key schema elements:
- `StimulusImage` object includes `vision_attributes` field
- `vision_attributes` defined as `object` with keys/values (string → number)
- Examples: `'brightness', 'complexity', 'hue_variation'`

**Issue**: Schema defines vision_attributes as **arbitrary key-value pairs** with no enumeration of valid attribute IDs.

### 5.2 Cross-Reference Gaps

| Template Element | Links to Attributes? | Status |
|------------------|----------------------|--------|
| `StimulusImage.vision_attributes` | Implicitly (no validation) | **No schema validation** |
| `StimulusComponent.category` | Covers modalities (visual, acoustic, etc.) | Orthogonal to attributes |
| `Finding.template_ids` | Links to stimulus templates | **No attribute linkage** |
| `Finding.mechanism_chain` | Theory commitments | **No visual attribute linkage** |

### 5.3 Missing Integrations

1. **No enumeration of valid attribute IDs** in schema
   - Template accepts any `vision_attributes` key
   - No validation against 33-attribute taxonomy

2. **No population of vision_attributes in extraction pipeline**
   - `run_image_extraction_batch.py` extracts images only
   - Does not compute any of the 33 attributes
   - No code path from extracted images to attribute computation

3. **No template-to-attribute mapping**
   - Schema does not link stimulus templates to required/optional attributes
   - E.g., "room with plants" stimulus should require {NEW-01, NEW-12, ATTR-C3}

---

## Part 6: Inter-Rater Reliability & Validation

### 6.1 Rater Agreement Assessment

**Finding**: No inter-rater reliability data exists for any attribute.

**Problem**: Attributes define themselves as measurable but lack:
- Ground truth annotations
- Multiple independent raters
- Agreement statistics (Fleiss' kappa, ICC, Cronbach's alpha)
- Systematic disagreement analysis

**High-Risk Attributes**:
- ATTR-M2 (Haptic Expectation): Purely subjective inference
- ATTR-M3 (Olfactory Expectation): Highly speculative
- NEW-09 (Acoustic Privacy): Visual proxy for unmeasurable property
- NEW-10 (Color Harmony): Aesthetic judgment
- NEW-11 (Person Density): Hardcoded scene assumption undermines reliability

### 6.2 Validation Dataset

**Status**: DOES NOT EXIST

Required:
- Set of annotated images (50-100 images minimum)
- Human raters (3+ independent raters per attribute)
- Ground truth for Tier 2 attributes (depth, segmentation)
- Rater agreement statistics for each attribute

---

## Part 7: Critical Gaps and Blockers

### 7.1 Blocking Issues (Prevent Implementation)

| Issue | Severity | Attributes Affected | Mitigation |
|-------|----------|---------------------|-----------|
| NEW-03 algorithm unspecified | CRITICAL | NEW-03 | Specify horizon detection method (e.g., semantic segmentation) |
| NEW-07 algorithm absent | CRITICAL | NEW-07 | Implement material classification (texture CNN or VLM-based) |
| NEW-10 harmony undefined | HIGH | NEW-10 | Define "harmony" metric (e.g., color theory, Gestalt principles) |
| Spatial attributes require 3D | HIGH | ATTR-S1, ATTR-S3 | Use depth estimation (NEW-02) as proxy; document limitation |
| No attribute computation pipeline | CRITICAL | All 33 | Build compute_all_attributes.py orchestrator |
| Hardcoded scene size in NEW-11 | HIGH | NEW-11 | Estimate camera focal length; use vanishing points |

### 7.2 Quality Issues (Reduce Confidence)

| Issue | Severity | Attributes Affected | Evidence |
|-------|----------|---------------------|----------|
| DeepLabV3 trained outdoors | MEDIUM | NEW-01, NEW-06 | PASCAL VOC outdoor bias; weak indoor performance |
| Tier 2 models untested on stimuli | MEDIUM | 17 attributes | No validation images in repo |
| Arbitrary thresholds | MEDIUM | NEW-01 (0.05), NEW-12 (0.6) | No justification in papers |
| Sigmoid mapping unjustified | LOW | NEW-12 | 1/(1+exp(-x+1)) appears arbitrary |
| Material absorption not provided | MEDIUM | NEW-09 | No coefficient table for acoustics estimation |

### 7.3 Documentation Issues

| Issue | Type | Severity |
|-------|------|----------|
| NEW-03 (sky detection): No algorithm in detailed spec | Omission | HIGH |
| NEW-07 (material diversity): No detailed spec section | Omission | CRITICAL |
| NEW-10 (color harmony): Underspecified output format | Ambiguity | HIGH |
| Validation dataset: No mention in any doc | Omission | CRITICAL |
| Test plan: No testing strategy documented | Omission | HIGH |
| Rater agreement: No inter-rater study mentioned | Omission | CRITICAL |

---

## Part 8: Per-Attribute Quality Scorecard

### 8.1 Scoring Rubric

Each attribute rated on 10-point scale across 5 dimensions:

1. **Definition Clarity** (0-2): Is the attribute unambiguously defined?
2. **Theoretical Warrant** (0-2): Are there published citations supporting the construct?
3. **Vision Algorithm** (0-2): Is the algorithm fully specified and implementable?
4. **Output Specification** (0-2): Are units, ranges, and normalization clear?
5. **Validation** (0-2): Is there evidence of inter-rater agreement or ground truth?

**Total = sum of 5 dimensions**

### 8.2 Scorecards

#### **ORIGINAL 21 ATTRIBUTES**

| ID | Name | Def | Warrant | Algo | Output | Valid | **Total** |
|----|------|-----|---------|------|--------|-------|---------|
| ATTR-F1 | Fractal Dimension | 2 | 2 | 2 | 2 | 0 | **8** |
| ATTR-F2 | 1/f Spectral Slope | 2 | 2 | 2 | 2 | 0 | **8** |
| ATTR-F3 | Lacunarity | 2 | 1 | 2 | 2 | 0 | **7** |
| ATTR-F4 | Edge Density | 2 | 2 | 2 | 2 | 0 | **8** |
| ATTR-C1 | CCT | 2 | 2 | 2 | 2 | 0 | **8** |
| ATTR-C2 | Chromatic Distribution | 2 | 2 | 2 | 2 | 0 | **8** |
| ATTR-C3 | Green Chromaticity | 2 | 2 | 2 | 2 | 0 | **8** |
| ATTR-S1 | Isovist Area | 2 | 2 | 1 | 2 | 0 | **7** |
| ATTR-S2 | Ceiling Height | 2 | 2 | 1 | 2 | 0 | **7** |
| ATTR-S3 | Enclosure Ratio | 2 | 2 | 1 | 2 | 0 | **7** |
| ATTR-S4 | Spatial Legibility | 2 | 2 | 1 | 2 | 0 | **7** |
| ATTR-M1 | Material Naturalness | 2 | 2 | 1 | 2 | 0 | **7** |
| ATTR-M2 | Haptic Expectation | 1 | 1 | 1 | 1 | 0 | **4** |
| ATTR-M3 | Olfactory Expectation | 1 | 1 | 1 | 1 | 0 | **4** |
| ATTR-B1 | Biomorphic Form | 2 | 2 | 1 | 2 | 0 | **7** |
| ATTR-B2 | Water Feature | 2 | 2 | 2 | 2 | 0 | **8** |
| ATTR-B3 | Biophilic Score | 2 | 2 | 1 | 2 | 0 | **7** |
| ATTR-P1 | Figure-Ground Clarity | 2 | 2 | 1 | 2 | 0 | **7** |
| ATTR-P2 | Symmetry | 2 | 2 | 2 | 2 | 0 | **8** |
| ATTR-A1 | Sitting Affordance | 1 | 1 | 1 | 1 | 0 | **4** |
| ATTR-A2 | Social Density | 1 | 1 | 1 | 1 | 0 | **4** |
| | **MEAN** | **1.81** | **1.81** | **1.43** | **1.81** | **0** | **6.86** |

**Key insights**:
- Fractal/color attributes are strong (8/10)
- Spatial attributes hamstrung by 3D requirement (7/10)
- Material/affordance attributes speculative (4/10)
- **ALL 21 lack validation data (0/10 on validation)**

#### **NEW 12 ATTRIBUTES**

| ID | Name | Def | Warrant | Algo | Output | Valid | **Total** |
|----|------|-----|---------|------|--------|-------|---------|
| NEW-01 | Vegetation Ratio | 2 | 2 | 1 | 2 | 0 | **7** |
| NEW-02 | Depth Estimation | 2 | 2 | 1 | 2 | 0 | **7** |
| NEW-03 | Sky Proportion | 2 | 1 | 0 | 1 | 0 | **4** |
| NEW-04 | Visual Complexity | 2 | 2 | 2 | 1 | 0 | **7** |
| NEW-06 | Figure-Ground Clarity | 1 | 2 | 1 | 1 | 0 | **5** |
| NEW-07 | Material Diversity | 1 | 1 | 0 | 0 | 0 | **2** |
| NEW-08 | Illumination Uniformity | 2 | 1 | 2 | 2 | 0 | **7** |
| NEW-09 | Acoustic Privacy | 1 | 1 | 1 | 1 | 0 | **4** |
| NEW-10 | Color Harmony | 1 | 1 | 0 | 0 | 0 | **2** |
| NEW-11 | Person Density | 2 | 1 | 1 | 0 | 0 | **4** |
| NEW-12 | Biomorphic Curvature | 2 | 2 | 2 | 1 | 0 | **7** |
| **(Missing)** | Water Motion | 0 | 0 | 0 | 0 | 0 | **0** |
| | **MEAN** | **1.45** | **1.27** | **0.82** | **0.82** | **0** | **4.36** |

**Key insights**:
- NEW-01, NEW-02, NEW-04, NEW-08, NEW-12 are implementable (7/10)
- NEW-03, NEW-07, NEW-10 are incomplete (2-4/10)
- NEW-09, NEW-11 are speculative (4/10)
- **ALL 12 lack validation data**
- **One attribute (water motion) completely missing**

---

## Part 9: Recommendations (Priority Order)

### **IMMEDIATE (Blocking Delivery)**

1. **Complete NEW-03 specification**
   - Define sky detection algorithm (semantic segmentation or custom detector)
   - Provide model name and library
   - Specify horizon detection method
   - Write implementation code and unit test

2. **Complete NEW-07 specification**
   - Define "material diversity" metric operationally
   - Implement material classification (CNN or VLM-based)
   - Provide optimal range
   - Write implementation code

3. **Clarify NEW-10 output format**
   - Define "color harmony" computationally
   - Specify output: single score or multi-dimensional?
   - Provide threshold for "harmony" classification
   - Write implementation code

4. **Build image attribute compute pipeline**
   - Create `scripts/compute_image_attributes.py`
   - Orchestrate all 33 attributes on extracted images
   - Integrate with template schema
   - Output JSON with per-image attribute values

5. **Build test suite for image pipeline**
   - Unit tests for Tier 1 attributes (at least 5 test images)
   - Integration tests for extraction → attributes workflow
   - Validation against synthetic/ground-truth images
   - Minimum coverage: 70%

### **HIGH PRIORITY (Quality)**

6. **Reduce arbitrary thresholds**
   - Justify NEW-01 vegetation threshold (0.05) from literature or pilot data
   - Justify NEW-12 curvature threshold (0.6) with human annotations
   - Conduct sensitivity analysis on all threshold values

7. **Validate Tier 2 models on interior images**
   - Evaluate DeepLabV3 on 20-50 interior images with manual vegetation annotation
   - Evaluate MiDaS depth on same images; compare to ground truth depth
   - Measure YOLO performance on person detection in indoor/occupancy scenarios
   - Document known limitations (e.g., "DeepLabV3 underperforms on potted plants")

8. **Fix NEW-11 scene size assumption**
   - Remove hardcoded 10m×10m assumption
   - Estimate focal length from image EXIF or user input
   - Use vanishing points to infer scale
   - If scale unknowable, report density as "persons per image area" (normalized)

9. **Integrate material absorption data**
   - For NEW-09, obtain acoustic absorption coefficients for common materials
   - Map material classes to absorption values (curated table)
   - Document source of acoustic data (ISO 354 standard, etc.)

### **MEDIUM PRIORITY (Robustness)**

10. **Create validation dataset**
    - Collect 50-100 diverse interior images
    - Manually annotate ground truth for: vegetation %, depth, sky %, complexity, person count
    - For subset, obtain 3+ rater annotations for inter-rater agreement
    - Release as benchmarks/validation_images/

11. **Document inter-rater agreement**
    - Establish minimum acceptable Fleiss' kappa (0.6+) for each attribute
    - For vision-based attributes, compare to ground truth, not other raters
    - For subjective attributes (harmony, affordance), require multiple raters

12. **Resolve Tier 2/3 implementation gaps**
    - ATTR-S1 (isovist): Use depth map proxy; document "estimated" isovist
    - ATTR-M1 (material): Implement CNN texture classifier or use VLM (CLIP) embeddings
    - ATTR-A1, ATTR-A2: Use object detection + spatial layout; validate on furniture/people

### **LOW PRIORITY (Polish)**

13. Document performance benchmarks
    - Runtime per attribute on CPU and GPU
    - Memory requirements for each Tier 2/3 model
    - Batch processing recommendations

14. Create human-interpretable documentation
    - Visual guide: Example images with attribute values
    - Optimal vs. suboptimal ranges illustrated
    - Use case guidance (when to use which attributes)

---

## Part 10: Implementation Checklist

### Deliver This Sprint

- [ ] Implement and test run_image_extraction_batch.py (script exists; needs tests)
- [ ] Write unit tests for Tier 1 attributes (8 attributes)
- [ ] Implement compute_image_attributes.py orchestrator
- [ ] Complete NEW-03, NEW-07, NEW-10 specifications + code
- [ ] Build 50-image validation dataset
- [ ] Write integration test: extract → compute → validate

### Next Sprint

- [ ] Validate Tier 2 models on validation dataset
- [ ] Measure inter-rater agreement on validation set
- [ ] Document known limitations and failure modes
- [ ] Fix arbitrary thresholds based on validation

### Future

- [ ] Implement advanced material classification (Tier 3)
- [ ] Optimize runtime for batch processing
- [ ] Create web UI for annotation/visualization

---

## Overall Quality Score: 5/10

**Breakdown**:
- **Specification**: 6.5/10 (complete for 30/33, but NEW-03/07/10 incomplete)
- **Implementation**: 2/10 (12 new attributes have no code; extraction pipeline untested)
- **Validation**: 0/10 (zero inter-rater agreement data; no test dataset)
- **Documentation**: 6/10 (detailed but missing test plan and validation strategy)
- **Robustness**: 3/10 (hardcoded thresholds; models untested on domain; no error bounds)

**Verdict**: This is a **high-quality specification document with minimal implementation and zero validation**. Before deployment, invest heavily in:
1. Completing underspecified attributes
2. Building the compute pipeline
3. Validation dataset + inter-rater studies
4. Comprehensive testing

---

**Audit completed**: 2026-03-01 18:15 UTC
**Next review**: After implementing recommendations 1-5 above
