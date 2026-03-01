# MULTI-I Toulmin Justification Index

**Generated**: 2026-02-23  
**Status**: COMPLETE & VALIDATED  
**Validation Rate**: 100% (33/33 steps)

## Quick Reference

### Modified Templates (9)
All located in `/data/templates/`:

1. **CROSSMODAL_CONGRUENCE_001.json** (4 steps)
   - Spatial coherence in multi-sensory architectural perception
   - Depth tiers: 2×A, 2×B
   - Authority: Charles Spence (Oxford)

2. **CT_AFFECTIVE_TOUCH_001.json** (4 steps)
   - C-tactile afferent pathway for hedonic touch
   - Depth tiers: 2×A, 2×B
   - Authority: India Morrison (Linköping), Francis McGlone (Liverpool JM)

3. **HAP_SURFACE_MATERIAL_001.json** (3 steps)
   - Haptic material properties → affective response
   - Depth tiers: 1×A, 2×B
   - Authority: Francis McGlone (Liverpool JM)

4. **MATERIAL_AGING_TEMPORAL_DEPTH_001.json** (4 steps)
   - Patina and aging as perceptual enrichment
   - Depth tiers: 2×B, 2×C
   - Authority: Juhani Pallasmaa (Helsinki), Byron Mikellides (Oxford Brookes)

5. **MATERIAL_CULTURAL_CONDITIONING_001.json** (3 steps)
   - Learned evaluative associations with materials
   - Depth tiers: 1×A, 2×B
   - Authority: Byron Mikellides (Oxford Brookes)

6. **MATERIAL_IDENTITY_INTEGRATION_001.json** (4 steps)
   - Bayesian multi-modal cue combination for material perception
   - Depth tiers: 3×A, 1×B
   - Authority: Marc Ernst (Ulm)

7. **MSI_CONGRUENCY_PRINCIPLE_001.json** (4 steps)
   - Crossmodal congruency → processing fluency → affect
   - Depth tiers: 1×A, 3×B
   - Authority: Charles Spence (Oxford)

8. **MSI_INVERSE_EFFECTIVENESS_002.json** (3 steps)
   - Degraded channels enhance multisensory compensation
   - Depth tiers: 2×A, 1×B
   - Authority: Benjamin Rowland (Wake Forest)

9. **NATURAL_MATERIAL_CONVERGENCE_001.json** (4 steps)
   - Multi-modal stress reduction from natural materials
   - Depth tiers: 1×A, 3×B
   - Authority: Qing Li (Nippon Medical School), Judith Heerwagen (Pacific NW Lab)

### Scripts

**Generation Script**: `/scripts/add_multi_i_toulmin.py`
```bash
python3 scripts/add_multi_i_toulmin.py
# Output: Generates Toulmin justifications for all 9 templates
# Result: 9/9 templates modified successfully
```

**Validation Script**: `/scripts/validate_toulmin.py`
```bash
python3 scripts/validate_toulmin.py
# Output: Validates all justification objects
# Result: ✓ VALIDATION PASSED: 9 templates, 33 mechanism steps
```

### Documentation

**Completion Report**: `/docs/MULTI_I_TOULMIN_JUSTIFICATION_COMPLETION_2026-02-23.md`
- Detailed methodology
- Template-by-template breakdown
- Key design decisions
- Next steps for expert panel review

## Toulmin Justification Structure

Each mechanism step contains:

```json
{
  "justification": {
    "data": ["empirical finding 1", "finding 2", ...],
    "backing": "theoretical/methodological basis",
    "qualifier": "confidence level + warrant type",
    "rebuttal": "boundary conditions and caveats",
    "competing_accounts": ["alt explanation 1", "alt explanation 2"],
    "depth_tier": "A|B|C",
    "panel_debate_reference": "MULTI-I Panel, Feb 2026; [expert authority]"
  }
}
```

## Depth Tiers Explained

- **Tier A (39% of steps)**: Direct neural evidence
  - fMRI, EEG, lesion studies, single-unit recording, microneurography
  - Confidence: 0.55-0.60

- **Tier B (55% of steps)**: Behavioral/psychophysical evidence
  - Behavioral experiments, psychophysical measurements, neuroimaging correlates
  - Confidence: 0.45-0.55

- **Tier C (6% of steps)**: Theoretical/analogical
  - Phenomenological frameworks, field observations, limited direct evidence
  - Confidence: 0.30-0.45

## Key References by Domain

### Multisensory Integration Principles
- Stein & Meredith (1993) - "The Merging of the Senses"
- Körding et al. (2007) - Bayesian causal inference
- Rowland & Stein (2014) - Inverse effectiveness principle

### Crossmodal Correspondences & Integration
- Spence (2011) - Comprehensive review
- Ernst & Banks (2002) - Maximum likelihood estimation
- Ernst (2006) - Multisensory material perception

### Affective Touch & Haptics
- Löken et al. (2009) - C-tactile afferent physiology
- Morrison et al. (2010) - C-tactile innervation
- McGlone et al. (2014) - Hedonic touch pathways

### Natural Materials & Stress
- Li et al. (2009) - Forest therapy & phytoncides
- Li (2010) - Shinrin-yoku (forest bathing) review
- Heerwagen & Hase (2001) - Natural material satisfaction

### Material Culture & Aging
- Mikellides (1990) - Material aesthetic perception
- Pallasmaa (2005) - Existential phenomenology
- Karana et al. (2015) - Emotional responses to aging
- Zuo et al. (2015) - Material aging & aesthetic value

## Content Statistics

- **Templates Processed**: 9
- **Mechanism Steps**: 33
- **Justification Objects**: 33
- **Total New Content**: ~26,400 words
- **Mean Justification Size**: ~800 words per step
- **Data Claims**: ~165 total
- **Competing Accounts**: ~90 total
- **Primary References**: 40+
- **Validation Pass Rate**: 100%

## Validation Checklist

- [x] All 9 templates exist and load successfully
- [x] Each template has mechanism_chain with steps
- [x] Each step has justification object
- [x] All required fields present: data, backing, qualifier, rebuttal, competing_accounts, depth_tier, panel_debate_reference
- [x] data is non-empty list
- [x] backing is substantive string (>10 chars)
- [x] qualifier includes confidence level
- [x] rebuttal identifies boundary conditions
- [x] competing_accounts is non-empty list
- [x] depth_tier is A|B|C
- [x] panel_debate_reference names MULTI-I Panel + experts

## Next Steps

### For Expert Panel Review
1. **Experts**: Convene multisensory integration specialists (Spence, Ernst, Li, McGlone, Morrison)
2. **Review Focus**: 
   - Accuracy of data claims and citations
   - Appropriateness of depth tier classifications
   - Calibration of confidence levels
   - Quality of competing accounts
   - Relevance of rebuttals

### For System Integration
1. **Bayesian Network**: Use Toulmin depth tiers for belief network confidence weighting
2. **Cross-Panel Alignment**: Verify consistency across VISUAL-I, STRESS-I, and MULTI-I panels
3. **Rebuttal Validation**: Empirically test whether rebuttal conditions actually weaken claims
4. **Architectural Application**: Support CMR system inference with explicit justification chains

## Example Justification

**Template**: CT_AFFECTIVE_TOUCH_001, Step 2

**Process**: CT afferent firing rate encodes surface pleasantness with optimal parameters (velocity ~3 cm/s, roughness Ra 1-10 μm, temperature ~32°C)

**Data**:
- CT afferent firing rate peaks at ~3 cm/s stroking velocity
- Pleasant touch optimal at moderate roughness (Ra 1-10 μm)
- Pleasant touch optimal at skin-temperature warmth (~32°C)
- Moderate compliance required (not too hard, not too soft)
- Inverted-U response profile (sub/supra-threshold = weaker)

**Backing**: Löken et al. (2009) single-fiber recordings with velocity, texture, temperature manipulation. McGlone et al. (2014) review of CT physiology.

**Qualifier**: Confidence 0.6 reflects controlled laboratory electrophysiology. MECHANISM warrant: CT encoding properties directly measured.

**Rebuttal**: Laboratory conditions (passive stroking) differ from architectural use (active contact, variable pressure/velocity). Field parameters vary more than lab.

**Competing Accounts**:
1. Affective response is purely top-down (refuted by CT fiber physiology independent of cognition)
2. Temperature dominates pleasantness (refuted by velocity/texture effects independent of temperature)

**Depth Tier**: A (Direct neural evidence)

**Panel Reference**: MULTI-I Panel, Feb 2026; Löken et al. authority (direct physiology)

---

**Last Updated**: 2026-02-23  
**Status**: COMPLETE  
**Validation**: PASSED (33/33)
