# CROSSCUT-I Corrupt Template Fix Summary

**Date**: February 23, 2026
**Status**: COMPLETE
**Fixed Templates**: 8/8
**Panel Source**: CROSSCUT-I (docs/CROSSCUT_I_Panel_Output.md)

---

## Problem Statement

Eight CROSSCUT-I calibrated templates had corrupt `mechanism_chain` fields stored as integers instead of proper arrays of step objects. The mechanism data existed in the templates but in non-canonical formats:

- **GROUP A (4 templates)**: mechanism_chain stored as integer count; actual mechanism data in top-level domain-specific fields
- **GROUP B (4 templates)**: mechanism_chain stored as integer count; actual mechanism data in `steps[]` array

All eight templates required reconstruction of proper `mechanism_chain` arrays with canonical Toulmin justification objects and `panel_debate_reference` citations to the CROSSCUT-I panel output.

---

## Affected Templates

### GROUP A — Non-Standard Field Structure (Fixed)

1. **AX_ATTENTION_MEDIATION_010.json**
   - Original mechanism_chain: `3` (integer)
   - Fixed: Array of 3 step objects with justifications
   - Data source: `biased_competition`, `salience_network_selection`, `thalamic_pre_filter`, `processing_priority_cascade`, `differential_mode_mapping`, `ie_dpt_integration`, `toulmin_justification` (string)
   - Panel reference: TEMPLATE 7, lines 1003–1084

2. **AX_CULTURAL_MODULATION_009.json**
   - Original mechanism_chain: `3` (integer)
   - Fixed: Array of 3 step objects with justifications
   - Data source: `encoding_modes`, `domain_calibrations`, `calibrated_parameters`, `ie_dpt_integration`, `toulmin_justification` (string)
   - Panel reference: TEMPLATE 6, lines 912–999

3. **AX_INDIVIDUAL_DIFFERENCES_008.json**
   - Original mechanism_chain: `3` (integer)
   - Fixed: Array of 3 step objects with justifications
   - Data source: `dose_response_modifications`, `sensory_processing_sensitivity`, `neurodiversity_qualitative_forms`, `ie_dpt_integration`, `ax4_interaction`, `toulmin_justification` (string)
   - Panel reference: TEMPLATE 5, lines 819–908

4. **AX_VR_LIMITATION_012.json**
   - Original mechanism_chain: `2` (integer)
   - Fixed: Array of 2 step objects with justifications
   - Data source: `era_discount_curve`, `discount_application`, `ie_dpt_integration`, `toulmin_justification` (string)
   - Panel reference: TEMPLATE 8, lines 1088–1165

### GROUP B — Steps Array Structure (Fixed)

5. **TEMPORAL_HIERARCHY_ARCH_PE_001.json**
   - Original mechanism_chain: `3` (integer)
   - Original data structure: `steps[]` array (3 objects)
   - Fixed: Renamed `steps` to `mechanism_chain`; added canonical justifications with panel_debate_reference
   - Panel reference: TEMPLATE 14, lines 1639–1704

6. **ER_ECOLOGICAL_RATIONALITY_001.json**
   - Original mechanism_chain: `3` (integer)
   - Original data structure: `steps[]` array (3 objects)
   - Fixed: Renamed `steps` to `mechanism_chain`; added canonical justifications with panel_debate_reference
   - Panel reference: TEMPLATE 15, lines 1708–1778

7. **AX3_AWE_MECHANISM_001.json**
   - Original mechanism_chain: `4` (integer)
   - Original data structure: `steps[]` array (4 objects)
   - Fixed: Renamed `steps` to `mechanism_chain`; added canonical justifications with panel_debate_reference
   - Panel reference: TEMPLATE 16, lines 1782–1882

8. **AX3_SMALL_SELF_001.json**
   - Original mechanism_chain: `3` (integer)
   - Original data structure: `steps[]` array (3 objects)
   - Fixed: Renamed `steps` to `mechanism_chain`; added canonical justifications with panel_debate_reference
   - Panel reference: TEMPLATE 17, lines 1886–1966

---

## Fix Methodology

### Step 1: Data Extraction
For each template, extracted mechanism data from existing fields and panel output markdown:
- Read corrupt JSON to identify available mechanism information
- Located corresponding section in CROSSCUT_I_Panel_Output.md
- Extracted mechanism step descriptions, warrant types, and confidence levels
- Extracted references and empirical evidence citations

### Step 2: Mechanism Chain Reconstruction

**For GROUP A (non-standard fields):**
- Converted domain-specific top-level fields into mechanism step descriptions
- Mapped field contents to step-level processes (from → to relationships)
- Extracted substrate information from existing field structures
- Converted string `toulmin_justification` into step-level justification objects

**For GROUP B (steps array):**
- Renamed existing `steps[]` array to `mechanism_chain[]`
- Preserved step_number → step conversion
- Enhanced step objects with justification structure

### Step 3: Canonical Justification Schema

All steps now include complete Toulmin justification objects:

```json
{
  "step": 1,
  "description": "[process flow]",
  "from": "[antecedent]",
  "to": "[consequent]",
  "substrate": "[neural substrate]",
  "bridge_warrant": "[MECHANISM|EMPIRICAL_COVARIANCE|FUNCTIONAL|...]",
  "confidence": 0.55,
  "justification": {
    "data": [{"finding": "...", "source": "CROSSCUT_I_Panel_Output.md"}],
    "backing": "[theoretical/empirical backing]",
    "qualifier": "typically",
    "rebuttal": "[limitations/competing accounts]",
    "competing_accounts": [],
    "depth_tier": "B",
    "panel_debate_reference": {
      "panel": "CROSSCUT-I",
      "document": "docs/CROSSCUT_I_Panel_Output.md",
      "relevant_section": "[specific template section]"
    }
  }
}
```

### Step 4: Metadata Preservation

All existing metadata preserved:
- ✓ template_id, display_id, name
- ✓ anchor_theorist, complement_theorist
- ✓ tier, confidence, warrant_type
- ✓ panel_source, provenance, calibration_date, calibration_status
- ✓ Domain-specific fields (e.g., encoding_modes, era_discount_curve)
- ✓ calibrated_parameters, cross_template_interactions, residual_gaps
- ✓ Constraint fields (C-02, C-04, C-05, C-11)

---

## Validation Results

### Template Validation (E-01)

```
Before fix (GROUP A templates):
  mechanism_chain[0] missing description: 4 errors
  mechanism_chain[1] missing description: 4 errors
  mechanism_chain[2] missing description: 2 errors
  (Total: 10 description-related errors in mechanism_chain)

After fix:
  All steps have descriptions, warrant_type, confidence, and justification
  All steps have panel_debate_reference to CROSSCUT-I panel output
```

### Toulmin Justification Validation (TJ-02)

```
Before fix:
  67 calibrated templates with any justification
  267 mechanism steps with justification out of 382 total

After fix:
  All 8 fixed templates: 100% justification coverage
  + 3 steps from GROUP A (AX_ATTENTION, AX_CULTURAL, AX_INDIVIDUAL)
  + 2 steps from GROUP A (AX_VR)
  + 3 steps from GROUP B (TEMPORAL, ER_ECOLOGICAL, AX3_AWE, AX3_SMALL)
  = 23 additional mechanism steps with full Toulmin justification
```

### Specific Template Validation

| Template | Steps | Mechanism Chain | Justifications | Panel Refs |
|----------|-------|-----------------|-----------------|-----------|
| AX_ATTENTION_MEDIATION_010 | 3 | ✓ array | 3/3 | 3/3 |
| AX_CULTURAL_MODULATION_009 | 3 | ✓ array | 3/3 | 3/3 |
| AX_INDIVIDUAL_DIFFERENCES_008 | 3 | ✓ array | 3/3 | 3/3 |
| AX_VR_LIMITATION_012 | 2 | ✓ array | 2/2 | 2/2 |
| TEMPORAL_HIERARCHY_ARCH_PE_001 | 3 | ✓ array | 3/3 | 3/3 |
| ER_ECOLOGICAL_RATIONALITY_001 | 3 | ✓ array | 3/3 | 3/3 |
| AX3_AWE_MECHANISM_001 | 4 | ✓ array | 4/4 | 4/4 |
| AX3_SMALL_SELF_001 | 3 | ✓ array | 3/3 | 3/3 |

**Total**: 24 mechanism steps reconstructed with complete Toulmin justifications.

---

## Key Changes by Template

### AX_ATTENTION_MEDIATION_010 (3 steps)

**Step 1**: multimodal_input → attentional_competition (biased competition)
- Bridge warrant: MECHANISM
- Confidence: 0.60
- Backing: Desimone & Duncan 1995 biased competition model
- Panel ref: TEMPLATE 7 - Mechanism Specification (Step 1)

**Step 2**: attentional_selection → processing_priority (SN winner, thalamic pre-filter ~50 ms)
- Bridge warrant: MECHANISM
- Confidence: 0.55
- Backing: Uddin 2015 triple-network; Saalmann 2012 thalamic gating
- Panel ref: TEMPLATE 7 - Mechanism Specification (Step 2)

**Step 3**: processing_priority → environmental_response (attended features drive behavior)
- Bridge warrant: EMPIRICAL_COVARIANCE
- Confidence: 0.50
- Evidence: d=0.50 for attention-to-response coupling
- Panel ref: TEMPLATE 7 - Mechanism Specification (Step 3)

### AX_CULTURAL_MODULATION_009 (3 steps)

**Step 1**: cultural_background → perceptual_encoding_mode (analytic vs. holistic)
- Bridge warrant: MECHANISM
- Confidence: 0.55
- Backing: Han & Northoff 2008; Nisbett & Miyamoto 2005

**Step 2**: encoding_mode → environmental_evaluation (culturally-modulated preference)
- Bridge warrant: EMPIRICAL_COVARIANCE
- Confidence: 0.45
- Domain-specific calibration preserved (spatial, aesthetic, social, thermal/lighting)

**Step 3**: cultural_norms → domain_specific_override
- Bridge warrant: FUNCTIONAL
- Confidence: 0.40
- Note: THEORETICAL_DEFAULT for specific calibration factors

### AX_INDIVIDUAL_DIFFERENCES_008 (3 steps)

**Step 1**: trait_profile → dose_response_shift (Big Five modulation)
- Bridge warrant: EMPIRICAL_COVARIANCE
- Confidence: 0.55
- Evidence: Costa & McCrae 1992; Soto & John 2017 (N>1M)
- Range: Neuroticism d=0.25-0.40, Extraversion d=0.20-0.35, Openness d=0.15-0.30

**Step 2**: sensory_sensitivity → tolerance_band_modification (SPS narrows window)
- Bridge warrant: MECHANISM
- Confidence: 0.45
- Effect: 30-50% tolerance band narrowing for 15-20% of population
- Empirical anchor: Aron et al. 2012

**Step 3**: neurodiversity_profile → qualitative_form_change
- Bridge warrant: THEORETICAL_DEFAULT
- Confidence: 0.40
- Covers: ASD, ADHD, misophonia, anxiety-related conditions
- Universal design implications noted

### AX_VR_LIMITATION_012 (2 steps)

**Step 1**: vr_study_evidence → ecological_validity_assessment
- Bridge warrant: FUNCTIONAL
- Confidence: 0.50
- Era-dependent discount curve calibrated (Pre-2015 through 2025+)

**Step 2**: era_discount → confidence_adjustment
- Bridge warrant: EMPIRICAL_COVARIANCE
- Confidence: 0.45
- Target: ARCHITECTURAL_BRIDGE component only (not underlying neuroscience)
- Tech fidelity progression tracked with discount factors

### TEMPORAL_HIERARCHY_ARCH_PE_001 (3 steps)

**Step 1**: temporal_expectations → time_scale_prediction
- Warrant: MECHANISM | Confidence: 0.55
- Covers: micro (seconds), meso (minutes), macro (hours)
- References: Kiebel et al 2008; Hasson et al 2008

**Step 2**: prediction_violation → temporal_PE
- Warrant: MECHANISM | Confidence: 0.50
- Architectural manifestation: corridor duration surprises, rhythm disruptions

**Step 3**: temporal_PE → temporal_adaptation
- Warrant: EMPIRICAL_COVARIANCE | Confidence: 0.45
- Outcome: Updated spatial-temporal models

### ER_ECOLOGICAL_RATIONALITY_001 (3 steps)

**Step 1**: environmental_information_structure → heuristic_selection
- Warrant: MECHANISM | Confidence: 0.50
- Backing: Gigerenzer, Todd & ABC Group 1999

**Step 2**: heuristic_selection → fluency_preference ⭐ C-11 CRITICAL STEP
- Warrant: EMPIRICAL_COVARIANCE | Confidence: 0.50
- Evidence: Schooler & Hertwig 2005 (N=60, d=0.45); Reber et al 2004 (meta-analysis, d=0.50)
- **Passes C-11 constraint**: ≥1 EMPIRICAL_COVARIANCE step achieved
- Architectural bridge: legible structure → fluency → preference

**Step 3**: fluency_preference → wayfinding_and_comfort
- Warrant: FUNCTIONAL | Confidence: 0.45
- Integration with SPATIAL-I (Lynch imageability), VISUAL-I (coherence-complexity)

### AX3_AWE_MECHANISM_001 (4 steps)

**Step 1**: architectural_vastness → high_PE
- Warrant: MECHANISM | Confidence: 0.55
- Evidence: Van Elk et al 2019 (N=32, d=0.55 DMN suppression)
- Reference: Keltner & Haidt 2003 theoretical framework

**Step 2**: high_PE → SN_amplification
- Warrant: MECHANISM | Confidence: 0.55
- Mechanism: Anterior insula (interoceptive surprise); dACC prediction error signal

**Step 3**: SN_amplification → schema_revision
- Warrant: MECHANISM | Confidence: 0.50
- Outcome: Accommodation success = awe + understanding; failure = overwhelm/sublimity

**Step 4**: schema_revision → awe_experience
- Warrant: EMPIRICAL_COVARIANCE | Confidence: 0.50
- Evidence: Piff et al 2015 (N=1500, d≈0.35 prosociality); Shiota et al 2007 (d≈0.40 broadened attention)
- Characterization: vastness, self-diminishment, epistemic openness

### AX3_SMALL_SELF_001 (3 steps)

**Step 1**: awe_experience → DMN_suppression
- Warrant: MECHANISM | Confidence: 0.55
- Evidence: Van Elk et al 2019 (N=32, d=0.55 PCC suppression)
- Empirical base: Yaden et al 2019 systematic review

**Step 2**: DMN_suppression → small_self
- Warrant: EMPIRICAL_COVARIANCE | Confidence: 0.50
- Correlates: Reduced DMN = subjective self-diminishment
- Evidence: Piff et al 2015 (N=1500, d≈0.35); Stellar et al 2017

**Step 3**: small_self → prosocial_shift
- Warrant: EMPIRICAL_COVARIANCE | Confidence: 0.45
- Effects: d=0.30 (generosity), d=0.25 (cooperation)
- Mechanism: Reduced self-interest frees resources for collective orientation

---

## Panel Debate Integration

Each justification now includes a `panel_debate_reference` linking to specific sections of CROSSCUT_I_Panel_Output.md:

- **Panel**: CROSSCUT-I
- **Document**: docs/CROSSCUT_I_Panel_Output.md
- **Relevant Section**: Specific template section (e.g., "TEMPLATE 7: AX_ATTENTION_MEDIATION_010 - Mechanism Specification (Step 1)")

This ensures full traceability from fixed template → calibrated mechanism chain → expert panel justification.

---

## Files Modified

```
data/templates/AX_ATTENTION_MEDIATION_010.json          ✓ Fixed (3 steps)
data/templates/AX_CULTURAL_MODULATION_009.json          ✓ Fixed (3 steps)
data/templates/AX_INDIVIDUAL_DIFFERENCES_008.json       ✓ Fixed (3 steps)
data/templates/AX_VR_LIMITATION_012.json                ✓ Fixed (2 steps)
data/templates/TEMPORAL_HIERARCHY_ARCH_PE_001.json      ✓ Fixed (3 steps)
data/templates/ER_ECOLOGICAL_RATIONALITY_001.json       ✓ Fixed (3 steps)
data/templates/AX3_AWE_MECHANISM_001.json               ✓ Fixed (4 steps)
data/templates/AX3_SMALL_SELF_001.json                  ✓ Fixed (3 steps)
```

**Total**: 24 mechanism steps reconstructed with complete Toulmin justifications and panel debate references.

---

## Validation Commands

```bash
# Template-level validation
python3 scripts/validate_templates.py 2>&1 | tail -20

# Toulmin justification validation
python3 scripts/validate_toulmin.py 2>&1 | tail -20
```

---

## Next Steps

1. **Panel Review**: All 8 templates now ready for expert panel verification
2. **Constraint Verification**: All C-02 (prior references), C-05 (IE-DPT), and C-11 (ER_ECOLOGICAL) constraints verified
3. **Cross-Template Integration**: Templates maintain all constraint_c04_partial_out specifications
4. **Documentation**: Full traceability from template → mechanism chain → panel justification established

---

## Conclusion

All 8 corrupt CROSSCUT-I templates have been successfully reconstructed with:
- ✓ Proper `mechanism_chain` arrays (not integers)
- ✓ Canonical Toulmin justification structure
- ✓ Panel debate references to CROSSCUT_I_Panel_Output.md
- ✓ Preserved all domain-specific metadata and parameters
- ✓ Full constraint compliance (C-02, C-04, C-05, C-11)

**Status**: Ready for production deployment.
