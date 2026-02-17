# CMR Implementation Decisions Log

*Last updated: February 17, 2026*

This document tracks implementation decisions made during Sprint 10 CMR pipeline development, per the root-level CLAUDE.md governance requirements.

---

## Task 1.2: Template DB Index

### D1.2.1: SQLAlchemy vs Raw SQLite
- **Context**: Existing codebase uses raw SQLite. Doc 68 Part 2.1 specifies SQLAlchemy models.
- **Decision**: Use SQLAlchemy as specified in Doc 68 to enable ORM queries and consistency with the frozen contract.
- **Rationale**: The CMR pipeline is new infrastructure that should follow its own contract; SQLAlchemy provides cleaner query interfaces and the models can coexist with existing raw SQLite tables.
- **Risk**: Low — SQLAlchemy wraps the same SQLite database.

### D1.2.2: Generation Classification for Non-Standard Series
- **Context**: Doc 67 defines Gen-1 (T/M/AX) and Gen-2 (domain series). Templates like "CROSS-", "E-", "CB-" series are not explicitly classified.
- **Decision**: Default CROSS-, E-, CB- series to Gen-1 (framework/cross-cutting templates). Default dedup_status to "active" since they serve organizational roles.
- **Rationale**: Cross-framework templates are structural connectors, not superseded Gen-1 or calibrated Gen-2. They should be active but classified as Gen-1 per their non-quantitative nature.
- **Risk**: Low — these templates are flagged for later review.

### D1.2.3: T-Series Partial Classification (T41-T52)
- **Context**: Doc 67 Part 1 table explicitly classifies T1-T40 but marks T41-T52 as "deferred to individual assessment."
- **Decision**: Default T41-T52 to "residual" status since they're Gen-1 templates potentially partially captured by Gen-2 but needing individual review.
- **Rationale**: "residual" is safer than "active" (avoids double-counting) or "gap" (implies no partial Gen-2 coverage). These can be reclassified when the individual assessment is completed.
- **Risk**: Medium — some T41-T52 templates may be fully superseded or gaps. Document for future panel review.

### D1.2.4: AX and M Series Default to "gap"
- **Context**: AX (Auxiliary) and M (Music) series are Gen-1 templates not in the explicit deduplication map.
- **Decision**: Default to "gap" status since they lack Gen-2 calibrated equivalents.
- **Rationale**: These templates describe mechanisms (acoustic, music) without calibrated domain panels. Gap classification flags them for future calibration work.
- **Risk**: Low — conservative classification.

### D1.2.5: pe_contribution Default
- **Context**: Many templates lack explicit `pe_contribution` field.
- **Decision**: Default to "organizational" per spec if not found in JSON. Infer "predictive" if template has `predictive_processing` in framework_ids, or "explanatory" if causal_links have strong bridging_quality.
- **Rationale**: Most templates serve organizational/structural roles in the assessment framework. Predictive and explanatory contributions are higher-confidence labels requiring explicit evidence.
- **Risk**: Low — defaults are conservative.

### D1.2.6: practical_accessibility Default
- **Context**: Many templates lack explicit `practical_accessibility` field.
- **Decision**: Default to "B" per spec. If `inputs_required` array exists with accessibility tiers, use the highest (worst-case) tier among required inputs.
- **Rationale**: Tier B (specialized measurement) is a reasonable middle ground. Many templates require lux meters or sound level meters but not research-grade equipment.
- **Risk**: Low — can be corrected with template enrichment task (3.4).

### D1.2.7: maturity Field Extraction
- **Context**: Templates use various field names: `overall_maturity`, `maturity`, or maturity embedded in `causal_links`.
- **Decision**: Check `overall_maturity` first, then `maturity`, then first causal link maturity. Default to "speculative" if not found.
- **Rationale**: Follows apparent template evolution where newer templates use `overall_maturity` while older ones use different patterns.
- **Risk**: Low — conservative default.

### D1.2.8: calibration_status Normalization
- **Context**: Templates use various terms: "partially_calibrated", "deepened", "protocol", etc.
- **Decision**: Normalize to four canonical values per Doc 68: "substantial", "partial", "protocol", "uncalibrated". Map "deepened" → "partial", check for calibration_data/calibration_parameters presence.
- **Rationale**: Consistent values enable query filtering and WIS weight calculation.
- **Risk**: Low — explicit mapping rules.

### D1.2.9: source_docs Extraction
- **Context**: Some templates have `source_docs` array, others have `source_panel` string with embedded doc number.
- **Decision**: Try `source_docs` first; if not present, extract leading digits from `source_panel` or `source_panel_doc` using regex. Default to empty string.
- **Rationale**: Source documentation is important for traceability but not required for pipeline operation.
- **Risk**: Low — missing values flagged as empty string.

---

## Summary Statistics (Post-Scan)

| Metric | Value |
|--------|-------|
| Total templates loaded | 150 |
| Active | 52 |
| Gap | 38 |
| Residual | 44 |
| Superseded | 9 |
| Reference | 7 |
| Gen-1 | 118 |
| Gen-2 | 32 |

Expected counts from Doc 67: ~14 superseded, ~18 residual, ~10 gap, ~8 reference. Actual counts differ due to:
1. T41-T52 defaulting to residual (12 templates)
2. AX/M series defaulting to gap (29 templates)
3. CROSS/E/CB series defaulting to active

These classifications are correct given the inference rules above. Individual review can refine them.

---

---

## Task 2.1: Template Computation Functions

### D2.1.1: ComputeResult Standard Structure
- **Context**: Need consistent return type across all 12 compute functions.
- **Decision**: Create ComputeResult dataclass with: output_type, value, unit, zone (optional), confidence, details (dict).
- **Rationale**: Standard structure enables uniform WIS conversion and reporting. Details dict captures template-specific context.
- **Risk**: Low — simple structure.

### D2.1.2: Lifespan Moderation Implementation
- **Context**: All templates have age_band_modifiers and lifespan_sensitivity_multiplier in JSON.
- **Decision**: Implement u_curve_piecewise model with reference band age_25_50 = 1.0. Return multiplier that can be applied to effect magnitude.
- **Rationale**: Per template JSON calibration. Higher values at extremes (children, elderly) indicate greater sensitivity.
- **Risk**: Low — directly from template JSON.

### D2.1.3: Goldilocks Zone Boundaries
- **Context**: VF3, L1, MAT2 use Goldilocks models with zone boundaries.
- **Decision**: Use exact boundaries from template calibration_data. Return zone classification in result.
- **Rationale**: Zone boundaries are calibrated in template JSON; no need to recalibrate.
- **Risk**: Low — boundaries from templates.

### D2.1.4: CREA2 Matrix Keys
- **Context**: CREA2 has 2×2×2 matrix with sub-additivity factors.
- **Decision**: Use string keys like "A+B+C" for matrix lookup. Classify pathways: A=noise 65-75dB, B=ceiling R_h 0.35-0.50, C=light 100-200 lux.
- **Rationale**: Clean lookup pattern; pathway boundaries from CREA2 calibration_data.
- **Risk**: Low — directly from template.

### D2.1.5: Channel Weights for L3 and MAT4
- **Context**: Multi-channel templates have preliminary expert-estimated weights.
- **Decision**: Use weights from template calibration_parameters directly. Flag as preliminary in confidence score.
- **Rationale**: Expert estimates are best available; lower confidence reflects uncertainty.
- **Risk**: Medium — weights may change with future calibration. Confidence appropriately set to 0.70-0.75.

### D2.1.6: VIEW1 VQI Scale
- **Context**: VIEW1 needs 0-100 VQI score.
- **Decision**: Compute weighted channel composite (0-1), apply area modifier, scale to 0-100. Add 15% super-additivity bonus when 4+ channels active.
- **Rationale**: VQI is industry-standard 0-100 scale. Multi-channel bonus reflects convergence principle.
- **Risk**: Low — standard approach.

### D2.1.7: Confidence Levels by Maturity
- **Context**: Templates have varying maturity levels (established, supported, preliminary).
- **Decision**: Map maturity to confidence: established=0.90, supported=0.80, preliminary=0.70, expert_estimate=0.70.
- **Rationale**: Confidence informs downstream WIS weighting and uncertainty propagation.
- **Risk**: Low — conservative mapping.

---

---

## Task 3.2: Template Computation Functions Batch 2

### D3.2.1: Stub Implementation for Uncalibrated Templates
- **Context**: Several templates (TP3, TP4, CREA4, COL2, VF2) lack calibration data sufficient for real computation.
- **Decision**: Implement stub functions returning value=0.5 (neutral) with `needs_calibration: true` flag and confidence=0.40.
- **Rationale**: Per Sprint10_Execution_Plan.md guidance: "If a template's JSON lacks enough info for a real computation, write a stub that returns WIS 50 with a flag `{"needs_calibration": true}`"
- **Risk**: Low — stubs are explicitly flagged for future calibration work.

### D3.2.2: CCT Range Boundaries for L4
- **Context**: L4 requires classification of CCT into zones and time-of-day congruence.
- **Decision**: Use five CCT zones (warm_firelight, warm_incandescent, neutral, cool_daylight, overcast_sky) and define expected CCT ranges per time of day (morning: 4500-6500K, evening: 2000-3500K).
- **Rationale**: Aligns with L4 calibration_parameters and circadian science (higher CCT in morning, lower in evening).
- **Risk**: Low — boundaries from template JSON.

### D3.2.3: Proxemic Zone Boundaries for SOC1
- **Context**: SOC1 requires interpersonal distance evaluation with cultural calibration.
- **Decision**: Use Hall's four zones (intimate: <45cm, personal: 45-120cm, social: 120-360cm, public: >360cm) with cultural adjustment multipliers from SOC1 calibration.
- **Rationale**: SOC1 calibration references Hall (10,000+ citations); cultural variation is explicitly calibrated.
- **Risk**: Low — established empirical framework.

### D3.2.4: Channel Weights for TP2 Threshold Boundary
- **Context**: TP2 episodic boundary strength depends on number of modality channels changing.
- **Decision**: Use TP2 calibration parameters for channel weights (spatial: 0.25, light: 0.20, sound: 0.18, material: 0.15, olfactory: 0.12) with 15-20% super-additivity bonus for synchronized change.
- **Rationale**: Directly from TP2 calibration_parameters and Event Segmentation Theory.
- **Risk**: Low — calibrated values.

### D3.2.5: Walking Effect Size for CREA3
- **Context**: CREA3 models divergent thinking benefit from walking.
- **Decision**: Use walking effect sizes from CREA3 calibration: indoor d≈0.58, outdoor d≈0.74, with nature bonus +0.17. Optimal duration 5-20 minutes.
- **Rationale**: Based on Oppezzo & Schwartz replications and CREA3 calibration.
- **Risk**: Low — empirically calibrated.

### D3.2.6: Olfactory Adaptation Time for OLF1
- **Context**: OLF1 treats olfaction as a "transition modality" due to rapid adaptation.
- **Decision**: Model adaptation as decaying from 1.0 (fresh) to 0.1 (fully adapted) over 2-10 minutes.
- **Rationale**: Per OLF1 calibration: "adaptation_timecourse: 2-10 minutes for most odorants".
- **Risk**: Low — well-established olfactory science.

---

## Summary Statistics (Post-Batch 2)

| Metric | Value |
|--------|-------|
| Total templates implemented | 32 |
| Batch 1 (fully calibrated) | 12 |
| Batch 2 (calibrated) | 14 |
| Batch 2 (stub - needs calibration) | 6 |
| Total test count | 107 |
| Full suite (3101 passed) | ✓ |

---

*Document maintained per root-level CLAUDE.md governance requirements.*
