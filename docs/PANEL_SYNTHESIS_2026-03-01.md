# Panel Synthesis: MUST DO Recommendations
## Cross-Panel Critical Issues

**Date**: 2026-03-01
**Scope**: Aggregate of all MUST DO items from Panels A–D
**Total MUST DO items**: 19
**Estimated implementation timeline**: 4–6 weeks
**Priority**: BLOCKING (should be completed before production deployment)

---

## Executive Summary

Four expert panels reviewed core infrastructure for the Article Eater PostQuinean system:
- **Panel A (Schema Review)**: Template v2 schema + new fields
- **Panel B (Quality Thresholds)**: Extraction quality rules + 0.75 acceptance threshold
- **Panel C (Theory-Molecule Linkage)**: Rasa attractors + t1_frameworks mapping
- **Panel D (Vision Attributes)**: Causal-theoretic image attributes taxonomy

**Key finding**: All four areas have **foundational gaps** that must be addressed before mainline deployment. None are ready for production use in meta-analysis without substantial revision.

**Overall risk assessment**: MEDIUM-HIGH
- Schema (Panel A): Moderate risk (good foundation; some gaps)
- Quality rules (Panel B): Medium-high risk (threshold too coarse; consistency rules missing)
- Theory-molecule (Panel C): HIGH RISK (unvalidated mappings; epistemological confusion)
- Vision attributes (Panel D): HIGH RISK (38% unspecified operationally; redundancy unquantified)

---

## MUST DO Items by Area

### PANEL A: Schema Review (5 MUST DO items)

**A1. Specify vision_attributes enum** (CRITICAL)
- **Current problem**: `"additionalProperties: { type: number }"` invites garbage data
- **Solution**: Create closed enum of vision attributes with units and ranges:
  ```json
  "vision_attribute_definitions": {
    "fractal_dimension": { "unit": "dimensionless", "range": [1.0, 2.0], "source": "box-counting" },
    "brightness_nits": { "unit": "cd/m²", "range": [10, 5000] },
    "contrast_ratio": { "unit": "dimensionless", "range": [1, 21] },
    "complexity_entropy": { "unit": "bits/pixel", "range": [0, 8] },
    ...
  }
  ```
- **Why MUST DO**: Prevents low-quality stimulus_images data; enables downstream analysis
- **Timeline**: 1 week
- **Owner**: Data/schema team
- **Blocking**: Yes; blocks Panel D integration

---

**A2. Mark mechanism_chain as conditional** (CRITICAL)
- **Current problem**: Mechanism extraction is high-risk without epistemic grounding
- **Solution**: Add field `mechanism_expectation`:
  ```json
  "mechanism_expectation": {
    "type": "string",
    "enum": ["required", "expected", "optional"],
    "mapping": {
      "empirical_finding": "required",
      "causal": "required",
      "theoretical": "expected",
      "moderated": "expected",
      "qualitative_theme": "optional",
      "cited": "optional"
    }
  }
  ```
- **Why MUST DO**: Prevents extraction of speculative mechanisms; improves quality
- **Timeline**: 3 days
- **Owner**: Schema team
- **Blocking**: Partially (affects extraction QC)

---

**A3. Separate success_conditions into data-tier and epistemic-tier** (HIGH PRIORITY)
- **Current problem**: Conflates data quality with theoretical expectations
- **Solution**:
  ```json
  "success_conditions": {
    "data_tier": {
      "required_fields": ["antecedent", "consequent", "direction"],
      "min_quality_score": 0.75
    },
    "epistemic_tier": {
      "theory_link_expected": { "type": "boolean", "varies_by_claim_type": true },
      "mechanism_expected": { "type": "boolean", "varies_by_claim_type": true }
    }
  }
  ```
- **Why MUST DO**: Enables correct acceptance criteria; different standards for different claim types
- **Timeline**: 1 week
- **Owner**: Schema team
- **Blocking**: Affects Panel B quality thresholds

---

**A4. Add temporal/familiarity properties to StimulusDescription** (HIGH PRIORITY)
- **Current problem**: Missing critical moderators in environmental psychology
- **Solution**: Expand StimulusDescription:
  ```json
  "stimulus_temporal": {
    "exposure_frequency": { "enum": ["discrete", "continuous", "intermittent"] },
    "exposure_prior_familiarity": { "type": ["number", "null"], "minimum": 0, "maximum": 1 },
    "habituation_control": { "type": "boolean" }
  }
  ```
- **Why MUST DO**: Temporal dynamics are major moderators; missing these blocks environmental psych validity
- **Timeline**: 1 week
- **Owner**: Domain expert + schema team
- **Blocking**: Affects downstream theory-outcome mappings

---

**A5. Do NOT mandate molecule_ids; clarify epistemology** (CRITICAL)
- **Current problem**: Unvalidated mappings; unclear if molecules are causal or descriptive
- **Solution**:
  1. Make molecule_ids optional, not required
  2. Pilot validation on 50-paper subsample (2 weeks)
  3. Compute inter-rater reliability on molecule assignment
  4. Publish validation results before mainline adoption
  5. Mark molecules as "PILOT/EXPERIMENTAL" in production
- **Why MUST DO**: Prevents premature use of unvalidated constructs; manages epistemic risk
- **Timeline**: 2-week pilot
- **Owner**: Panel C + data team
- **Blocking**: Yes; blocks Panel C recommendations

---

### PANEL B: Quality Thresholds (5 MUST DO items)

**B1. Implement field-specific quality thresholds by article_family** (CRITICAL)
- **Current problem**: 0.75 threshold treats qualitative findings with same standards as RCTs
- **Solution**:
  ```json
  "quality_thresholds_by_family": {
    "empirical_research": 0.85,
    "experimental": 0.88,
    "observational": 0.82,
    "qualitative": 0.70,
    "review": 0.75,
    "theoretical": 0.70,
    "default": 0.75
  }
  ```
- **Why MUST DO**: One-size-fits-all threshold is invalid; empirical and qualitative have different validity conditions
- **Timeline**: 1 week
- **Owner**: QC team
- **Blocking**: Affects acceptance/rejection decisions; impacts downstream meta-analysis

---

**B2. Add consistency rules for cross-field validation** (CRITICAL)
- **Current problem**: Missing inter-field contradictions (p-value vs. direction, effect_size vs. sample_size, claim_type vs. article_type)
- **Solution**: Add rules:
  ```json
  {
    "rule_id": "CONS1_DIRECTION_P_VALUE_CONSISTENCY",
    "severity": "error",
    "check_type": "conditional",
    "condition": "direction in ['increase', 'decrease'] and p_value >= 0.05",
    "error_message": "Direction implies significance but p_value >= 0.05"
  },
  {
    "rule_id": "CONS2_EFFECT_SIZE_PLAUSIBILITY",
    "severity": "critical",
    "check_type": "range_validation",
    "ranges": { "Cohen's d": [-3, 3], "r": [-1, 1], "odds_ratio": [0, 100] }
  },
  {
    "rule_id": "CONS3_CLAIM_ARTICLE_TYPE_MISMATCH",
    "severity": "warning",
    "context_check": "article_type='experimental' should have mostly 'causal', 'empirical_finding' claim_types"
  }
  ```
- **Why MUST DO**: Prevents contradictory findings from passing QC; improves meta-analytic validity
- **Timeline**: 2 weeks
- **Owner**: QC team
- **Blocking**: Yes; major impact on extraction quality

---

**B3. Upgrade A4_BARE_DEMOGRAPHIC to conditional ERROR** (HIGH PRIORITY)
- **Current problem**: Demographic IVs in experiments are confounds, not manipulations
- **Solution**:
  ```json
  {
    "rule_id": "A4_BARE_DEMOGRAPHIC",
    "severity": "varies",
    "check_type": "conditional",
    "conditions": {
      "ERROR": "article_type='experimental' AND antecedent is bare demographic AND no factorial design detected",
      "WARNING": "article_type='observational' AND demographic used as moderator"
    }
  }
  ```
- **Why MUST DO**: Prevents confounded claims from inflating effect estimates; improves internal validity
- **Timeline**: 1 week
- **Owner**: QC team
- **Blocking**: Affects empirical papers; medium-high impact

---

**B4. Add implausibility checks** (CRITICAL)
- **Current problem**: LLM extraction can hallucinate impossible statistics
- **Solution**: Add rules:
  ```json
  {
    "rule_id": "ES1_IMPLAUSIBLE_EFFECT_SIZE",
    "severity": "critical",
    "ranges": { "Cohen's d": [-3, 3], "r": [-1, 1], "odds_ratio": [0, 100] }
  },
  {
    "rule_id": "P1_INVALID_PVALUE",
    "severity": "critical",
    "check_type": "range_validation",
    "min": 0.0,
    "max": 1.0
  },
  {
    "rule_id": "CI1_SIGN_CONSISTENCY",
    "severity": "error",
    "description": "CI bounds must be consistent with effect_size sign"
  },
  {
    "rule_id": "POWER1_IMPLAUSIBILITY",
    "severity": "error",
    "description": "Given n and effect_size, is p_value plausible? (post-hoc power analysis)"
  }
  ```
- **Why MUST DO**: Catches LLM hallucinations; essential for data integrity
- **Timeline**: 2 weeks (requires power analysis implementation)
- **Owner**: QC team
- **Blocking**: Yes; critical for preventing garbage data

---

**B5. Expand A3_OUTCOME_IN_ANTECEDENT forbidden_terms** (HIGH PRIORITY)
- **Current problem**: Regex patterns are brittle; miss synonyms
- **Solution**:
  1. Expand forbidden_terms list to include: "increased", "enhanced", "facilitated", "improved", "promoted", "reduced", "decreased", "modulated", "suppressed"
  2. Add secondary semantic check: compute cosine similarity between antecedent and consequent embeddings (BERT); flag if >0.7

- **Why MUST DO**: Improves detection of outcome language in antecedents
- **Timeline**: 1 week
- **Owner**: QC team
- **Blocking**: No; improves quality but not blocking

---

### PANEL C: Theory-Molecule Linkage (5 MUST DO items)

**C1. Separate molecules into three categories** (CRITICAL)
- **Current problem**: Conflates emotion, motivation, and perception
- **Solution**: Create taxonomy:
  ```json
  {
    "molecule_categories": {
      "phenomenological": [
        "shanta (Peace/Serenity)",
        "adbhuta (Wonder)",
        "bhayanaka (Terror/Awe)",
        "shringara (Love/Beauty)",
        "hasya (Joy)",
        "karuna (Compassion)",
        "bibhatsa (Disgust)"
      ],
      "motivational": [
        "veera (Heroism)",
        "raudra (Wrath/Power)"
      ],
      "descriptive_only": [
        "Note: Molecules in 'motivational' conflate perception with social-cognitive values and should NOT be used as causal attractors"
      ]
    }
  }
  ```
- **Why MUST DO**: Clarifies epistemological status; prevents misuse as causal mechanisms
- **Timeline**: 3 days
- **Owner**: Panel C + theory team
- **Blocking**: Yes; blocks downstream theory mappings

---

**C2. Create explicit many-to-many theory-molecule mappings** (CRITICAL)
- **Current problem**: No explicit theory ↔ molecule mappings; confounds aesthetic with functional
- **Solution**: Create mapping document:
  ```json
  {
    "framework_molecule_mapping": {
      "ART_Kaplan": ["adbhuta (soft fascination)", "shanta (escape from directed attention demands)"],
      "SRT_Ulrich": ["shanta (parasympathetic activation)"],
      "Biophilia_Wilson": ["shringara (biophilic attraction)", "shanta (safety signal)", "adbhuta (interest)"],
      "ProspectRefuge_Appleton": ["adbhuta (prospect)", "shanta (refuge)"],
      ...
    }
  }
  ```
- **Why MUST DO**: Enables systematic theory-outcome hypothesis testing; prevents post-hoc rationalization
- **Timeline**: 2 weeks
- **Owner**: Domain expert (env psych) + theory team
- **Blocking**: Yes; blocks all downstream molecule analysis

---

**C3. Add explicit outcome mappings** (CRITICAL)
- **Current problem**: Molecules are phenomenological; no link to measured outcomes
- **Solution**:
  ```json
  {
    "molecule_outcome_mapping": {
      "shanta": {
        "primary_outcomes": ["cortisol_reduction", "heart_rate_reduction", "attention_restoration"],
        "secondary_outcomes": ["mood_improvement", "satisfaction"],
        "mechanism": "Parasympathetic activation"
      },
      "adbhuta": {
        "primary_outcomes": ["interest_increase", "engagement_increase"],
        "secondary_outcomes": ["learning_gain", "exploration"],
        "mechanism": "Optimal prediction error + reward (dopamine)"
      },
      ...
    }
  }
  ```
- **Why MUST DO**: Makes molecules operationally meaningful; enables downstream meta-analysis
- **Timeline**: 2 weeks
- **Owner**: Domain expert + statistician
- **Blocking**: Yes; critical for analysis

---

**C4. Conduct pilot validation of top 3 mappings** (CRITICAL)
- **Current problem**: Mappings are speculative; inter-rater reliability unknown
- **Solution**:
  1. Select 50-paper subsample (balanced across frameworks: ART, SRT, Biophilia)
  2. Have 3 independent extractors assign molecules + theory frameworks to each paper
  3. Compute inter-rater reliability (Fleiss' kappa; target >0.70 for each mapping)
  4. Analyze disagreement: Where do extractors disagree? What resolves disputes?
  5. Publish results in short technical note before mainline adoption

- **Why MUST DO**: Establishes empirical grounding; detects whether mappings are reliable or arbitrary
- **Timeline**: 2 weeks
- **Owner**: Extraction team + statistician
- **Blocking**: YES; blocks use of molecules in meta-analysis until validation passes

---

**C5. Mark molecules as PILOT/EXPERIMENTAL** (HIGH PRIORITY)
- **Current problem**: Risk of unvalidated use in formal meta-analyses
- **Solution**: In all outputs/documentation:
  ```json
  {
    "molecule_ids": ["shanta", "adbhuta"],
    "molecule_status": "PILOT (not yet validated for meta-analysis)",
    "validation_deadline": "2026-05-01",
    "recommended_use": "Exploratory analysis only; do not include in formal meta-analysis until validation complete"
  }
  ```
- **Why MUST DO**: Manages expectations; prevents premature use
- **Timeline**: Immediate (1 day)
- **Owner**: Product/documentation team
- **Blocking**: No; administrative but important for governance

---

### PANEL D: Vision Attributes (4 MUST DO items)

**D1. Specify algorithms for all attributes** (CRITICAL)
- **Current problem**: 38% of attributes lack specified algorithms (S4, M1, M2, M3, A2, P1, and others)
- **Solution**: For each attribute, specify:
  1. Algorithm type (traditional vision, deep learning, hybrid)
  2. Specific method (Canny+box-counting for F1, etc.)
  3. Implementation (OpenCV, TensorFlow, custom code)
  4. Validation approach (ground truth, inter-rater agreement)
  5. Failure modes (when does algorithm break?)

  Example for S4 (Spatial legibility):
  ```json
  {
    "attribute_id": "ATTR-S4",
    "name": "Spatial Legibility",
    "algorithm": "Edge connectivity analysis",
    "steps": [
      "Edge detection (Canny, sigma=1.0)",
      "Connected component analysis on edges",
      "Compute junction density (junctions per pixel)",
      "Normalize by image size"
    ],
    "expected_range": [0, 1],
    "validation": "Correlation with human wayfinding task success (N=50 images)"
  }
  ```

- **Why MUST DO**: Prevents reproducibility failures; enables implementation
- **Timeline**: 2 weeks
- **Owner**: Vision team
- **Blocking**: YES; blocks all vision attribute deployment

---

**D2. Remove/redefine problematic attributes** (CRITICAL)
- **Current problem**: M3 (olfactory), A2 (social density) lack theoretical/empirical grounding
- **Solution**:
  1. **Remove M3 (Olfactory expectation)**. Cannot be reliably inferred from image alone without extensive scent-image training data (unavailable). Recommendation: Remove entirely.
  2. **Redefine A2 (Social density)** → Move to "socio-spatial design" category if needed, or remove. Not a vision attribute; requires behavioral/cultural knowledge.
  3. **Mark M1, M2, A1 as "exploratory"** (weak validation) until algorithms tested

- **Why MUST DO**: Prevents deployment of unvalidated/unfalsifiable constructs
- **Timeline**: 1 week
- **Owner**: Vision team + domain experts
- **Blocking**: YES; affects schema

---

**D3. Document and address redundancy** (HIGH PRIORITY)
- **Current problem**: Significant redundancy (F1 ↔ F2 ↔ F4; S1 ↔ S2 ↔ S3; B3 is linear combination)
- **Solution**:
  1. Compute correlation matrix on 100-image test set (diverse: indoor/outdoor, architectural/natural)
  2. If correlation > 0.85, flag as redundant; decide: merge or keep both?
  3. Publish redundancy analysis as technical note

  Example findings to investigate:
  - Are F1 and F2 correlated >0.80? If so, keep only F1 (box-counting is most interpretable)
  - Are S1, S2, S3 correlated >0.75? If so, consolidate into "Spatial Enclosure" dimension

- **Why MUST DO**: High redundancy reduces information content; wastes computation; inflates false certainty
- **Timeline**: 2 weeks (empirical analysis)
- **Owner**: Vision team + statistician
- **Blocking**: Partially (doesn't block deployment, but informs schema optimization)

---

**D4. Add missing critical attributes** (CRITICAL)
- **Current problem**: Missing perceptual and aesthetic attributes central to env psych
- **Solution**: Add at minimum:
  1. **Visual entropy / Surprise** (information content)
     - Measures unpredictability; predicts visual attention
     - Algorithm: Shannon entropy of edge positions, corner positions, or color histogram
     - Optimal: Moderate entropy (not too simple, not too chaotic)

  2. **Perceptual fluency** (ease of processing)
     - Measures how easily global scene can be understood
     - Algorithm: Inverse of visual entropy, or train CNN to predict processing difficulty
     - Linked to aesthetic preference and restoration

  3. **Color harmony** (colors form coherent ensemble)
     - Measures whether dominant colors are harmonious (analogous, complementary, triadic)
     - Algorithm: Extract dominant colors; check against color harmony rules
     - Linked to preference and restoration

  4. **Human scale** (feature-to-body ratios)
     - Relationship of scene features (window height, doorway, furniture) to human body size
     - Algorithm: Estimate scene scale via depth + geometry; compute feature/human ratios
     - Important for comfort and scale perception

  5. **Authenticity / Patina** (weathering signals)
     - Evidence of time, use, natural aging
     - Algorithm: Color variation over surfaces, irregularity, wear patterns
     - Linked to trust and liveliness in architecture

- **Why MUST DO**: Current schema lacks capture of key env psych constructs
- **Timeline**: 3–4 weeks (algorithm development + validation)
- **Owner**: Vision team + domain experts
- **Blocking**: Partially (doesn't block current deployment, but enables richer future analysis)

---

## Consolidated Implementation Timeline

### Week 1 (Immediate)
- **A1**: Specify vision_attributes enum (1 week)
- **A5**: Mark molecule_ids optional; pilot plan (start planning)
- **C5**: Mark molecules PILOT/EXPERIMENTAL (1 day)
- **B3**: Upgrade bare demographic rule (1 week)
- **B5**: Expand forbidden_terms (1 week)
- **C1**: Separate molecules into categories (3 days)

### Weeks 2–3
- **A2**: Mark mechanism_chain conditional (3 days)
- **A3**: Separate success_conditions tiers (1 week)
- **A4**: Add temporal/familiarity properties (1 week)
- **B1**: Implement family-specific thresholds (1 week)
- **B2**: Add consistency rules (2 weeks; partially overlaps with A3)
- **B4**: Add implausibility checks (2 weeks; partially overlaps with B2)
- **C2**: Create theory-molecule mappings (2 weeks)
- **C3**: Add outcome mappings (2 weeks; partially overlaps with C2)
- **D1**: Specify algorithms (2 weeks)
- **D2**: Remove/redefine problematic attributes (1 week)

### Weeks 4–6
- **A5**: Pilot validation 50-paper subsample (2 weeks)
- **C4**: Pilot validation top 3 mappings (2 weeks; parallel with A5)
- **D3**: Redundancy analysis (2 weeks; empirical)
- **D4**: Add missing attributes (3–4 weeks; overlaps with D1, D3)

### Total Estimated Effort
- **4–6 weeks** (critical path)
- **Team size**: 8–10 people (schema, QC, domain experts, vision, statisticians)
- **Dependencies**: Sequential in some areas (e.g., C2 needed before C4), parallel in others

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Molecules unvalidated | HIGH | C4 pilot required before meta-analysis use |
| 0.75 threshold too coarse | MEDIUM | B1 family-specific thresholds address |
| Vision attributes incomplete | HIGH | D1 algorithm specification + D4 missing attributes |
| Theory-molecule mappings arbitrary | HIGH | C2 explicit mapping + C4 validation |
| Redundancy inflates false certainty | MEDIUM | D3 correlation analysis |
| LLM hallucination of statistics | HIGH | B4 implausibility checks |
| Vague operators (material, haptic, olfactory) | MEDIUM | D2 remove/redefine problematic; D1 specify algorithms |

---

## Success Criteria

For each MUST DO item, define acceptance:

| Item | Success Criterion |
|------|-------------------|
| A1 | Vision attributes enum specified with units and ranges; used in 100+ paper sample test |
| A2 | Mechanism_chain conditional logic tested; extractors agree >80% on expectation classification |
| A3 | Success_conditions tiers used in pilot extraction; different thresholds applied by claim_type |
| A4 | Temporal properties captured in 50-paper sample; effect sizes with temporal moderators extractable |
| A5 | 50-paper pilot: inter-rater reliability κ > 0.70 for top 3 molecule mappings |
| B1 | Quality scores computed by article_family; thresholds applied correctly in acceptance decisions |
| B2 | Consistency rules prevent contradictory findings; p-value vs. direction mismatch detected 100% |
| B3 | Bare demographic rule triggers correctly; manual review identifies legitimate vs. confounded uses |
| B4 | Implausible statistics (d > 3, p < 0, p > 1) blocked; LLM hallucinations caught |
| B5 | Forbidden terms expanded; semantic similarity check tested on 100 papers; false positive rate <5% |
| C1 | Molecule categories documented; veera/raudra marked as motivational (not attractors) |
| C2 | Explicit many-to-many mapping created; each theory linked to 1–3 molecules |
| C3 | Each molecule linked to primary outcomes; mechanisms documented |
| C4 | Pilot 50-paper subsample: κ > 0.70 for ART, SRT, Biophilia mappings |
| D1 | All 21 attributes have specified algorithms; at least 5 implemented and tested |
| D2 | M3 removed; A2 redefined or removed; M1, M2, A1 marked exploratory |
| D3 | Correlation matrix computed; redundancy >0.85 identified and reconciled |
| D4 | At least 2 new attributes implemented (visual entropy + perceptual fluency) and validated |

---

## Critical Dependencies

```
A3 (success_conditions tiers)
├─ B1 (family-specific thresholds)
└─ affects both Panel B and downstream Panel C

C2 (theory-molecule mapping)
├─ C1 (molecule categorization)
├─ C3 (outcome mapping)
└─ C4 (validation pilot)

D1 (algorithm specification)
├─ A1 (vision_attributes enum)
├─ D2 (remove problematic)
└─ D3 (redundancy analysis)
```

The critical path runs through:
1. A1 → D1 (vision attributes specification)
2. C2 → C4 (theory-molecule validation)
3. B1 → B2 (quality threshold implementation)

All three paths can run in parallel but must be complete before production deployment.

---

## Ownership and Accountability

| Panel | Primary Owner | Secondary Owners |
|-------|---------------|------------------|
| A (Schema) | Data/Schema team | Domain experts (env psych) |
| B (QC) | QC team | Statisticians |
| C (Theory) | Theory team | Domain experts (env psych, cog sci) |
| D (Vision) | Vision/ML team | Design experts, domain experts |

Each owner reports progress weekly to steering committee until all MUST DO items complete.

---

## Approval Sign-Off

This synthesis document requires approval from:
1. ✓ Panel A chair (Shadish)
2. ✓ Panel B chair (Carmines)
3. ✓ Panel C chair (Kaplan)
4. ✓ Panel D chair (Belongie)
5. Project stakeholder (Professor David Kirsh)

**Status**: Pending approval
**Timeline**: Approval by 2026-03-02; implementation starts 2026-03-03

---

## Next Steps

1. **Present all four panel documents + synthesis to steering committee** (2026-03-01 EOD)
2. **Secure approval and resource allocation** (2026-03-02)
3. **Begin implementation Week 1 items** (2026-03-03)
4. **Weekly progress reports** to steering committee
5. **Pilot validation milestones** (C4, A5) by 2026-03-17
6. **Production readiness review** by 2026-03-31

---

**Prepared by**: Panel Secretariat
**Date**: 2026-03-01
**Reviewed by**: All four panel chairs
**Status**: Ready for steering committee review
