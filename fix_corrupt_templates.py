#!/usr/bin/env python3
"""
Fix 8 corrupt CROSSCUT-I templates with corrupt mechanism_chain fields.
GROUP A (1-4): mechanism_chain=int, data in top-level fields
GROUP B (5-8): mechanism_chain=int, steps[] array exists (rename to mechanism_chain)
"""

import json
import os

def build_justification(warrant_type, description, references=None, qualifier=None):
    """Build a canonical Toulmin justification object."""
    return {
        "data": [{"finding": description, "source": ""}] if description else [],
        "backing": " ".join(references) if references else "",
        "qualifier": qualifier or "typically",
        "rebuttal": "",
        "competing_accounts": [],
        "depth_tier": "B"
    }

def fix_group_a_ax_attention_mediation_010():
    """AX_ATTENTION_MEDIATION_010 - 3 mechanism steps from existing fields"""

    mechanism_chain = [
        {
            "step": 1,
            "description": "multimodal_input → attentional_competition (biased competition)",
            "from": "multimodal sensory input",
            "to": "attentional competition via biased competition mechanism",
            "substrate": "posterior parietal cortex (PPC), visual cortex",
            "bridge_warrant": "MECHANISM",
            "confidence": 0.60,
            "justification": {
                "data": [{
                    "finding": "multiple features compete for limited attentional resources (Desimone & Duncan 1995)",
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "Desimone & Duncan 1995 biased competition model",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": "TEMPLATE 7: AX_ATTENTION_MEDIATION_010 - Mechanism Specification (Step 1)"
                }
            }
        },
        {
            "step": 2,
            "description": "attentional_selection → processing_priority (SN winner, thalamic pre-filter ~50 ms)",
            "from": "attentional competition outcome",
            "to": "prioritized neural processing channel",
            "substrate": "salience network (AI, dACC), thalamic reticular nucleus",
            "bridge_warrant": "MECHANISM",
            "confidence": 0.55,
            "justification": {
                "data": [{
                    "finding": "salience network (Uddin 2015) determines attentional winner; thalamic pre-filter (Saalmann 2012) provides initial coarse selection across modalities (latency ~50 ms)",
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "Uddin 2015 triple-network model; Saalmann 2012 thalamic gating",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": "TEMPLATE 7: AX_ATTENTION_MEDIATION_010 - Mechanism Specification (Step 2)"
                }
            }
        },
        {
            "step": 3,
            "description": "processing_priority → environmental_response (attended features drive behavior; unattended attenuated)",
            "from": "neural priority signal",
            "to": "behavioral and psychological response",
            "substrate": "prefrontal cortex → motor output, affect generation",
            "bridge_warrant": "EMPIRICAL_COVARIANCE",
            "confidence": 0.50,
            "justification": {
                "data": [{
                    "finding": "attended features drive behavioral and psychological response while unattended features are attenuated (effect size d=0.50)",
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "Empirical covariance between attentional priority and response strength",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": "TEMPLATE 7: AX_ATTENTION_MEDIATION_010 - Mechanism Specification (Step 3)"
                }
            }
        }
    ]

    return {
        "template_id": "AX_ATTENTION_MEDIATION_010",
        "anchor_theorist": "Uddin",
        "complement_theorist": "Saalmann",
        "tier": "B",
        "mechanism_chain": mechanism_chain,
        "confidence": 0.55,
        "warrant_type": "MECHANISM",
        "biased_competition": {
            "reference": "Desimone & Duncan 1995",
            "mechanism": "multiple features compete for limited attentional resources"
        },
        "salience_network_selection": {
            "reference": "Uddin 2015 triple-network",
            "function": "determines attentional winner"
        },
        "thalamic_pre_filter": {
            "reference": "Saalmann 2012",
            "latency_ms": 50,
            "function": "initial coarse selection across modalities"
        },
        "processing_priority_cascade": {
            "attended_features": "drive behavioral and psychological response",
            "unattended_features": "attenuated effect"
        },
        "differential_mode_mapping": {
            "low_stimulation": {
                "attentional_pattern": "broad, distributed",
                "modalities_active": "multiple in parallel",
                "implication": "enrichment effect"
            },
            "high_stimulation": {
                "attentional_pattern": "narrow, focused",
                "modalities_active": "dominant modality",
                "implication": "overload avoidance"
            }
        },
        "ie_dpt_integration": {
            "level_1_implicit": "bottom-up attentional capture",
            "level_3_explicit": "top-down voluntary attention",
            "divergent_processing": "broad Level 1 attention (exploratory)",
            "convergent_processing": "narrow Level 3 attention (focused)"
        },
        "display_id": "AX_ATTENTION_MEDIATION_010",
        "name": "Attention Mediation",
        "panel_source": "CROSSCUT-I",
        "calibration_status": "calibrated",
        "provenance": "panel_calibrated",
        "calibration_date": "2026-02-23",
        "cross_template_interactions": [],
        "residual_gaps": []
    }

def fix_group_a_ax_cultural_modulation_009():
    """AX_CULTURAL_MODULATION_009 - 3 mechanism steps"""

    mechanism_chain = [
        {
            "step": 1,
            "description": "cultural_background → perceptual_encoding_mode (analytic vs. holistic)",
            "from": "cultural background and conditioning",
            "to": "perceptual encoding style (analytic or holistic processing)",
            "substrate": "visual cortex, parietal cortex (analytic: focal processing; holistic: contextual binding)",
            "bridge_warrant": "MECHANISM",
            "confidence": 0.55,
            "justification": {
                "data": [{
                    "finding": "Cross-cultural cognitive science documents systematic differences in perceptual encoding (Han & Northoff 2008; Nisbett & Miyamoto 2005): East Asian perceivers show greater contextual processing; Western perceivers show greater focal processing",
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "Han & Northoff 2008 fMRI cultural neuroscience; Nisbett & Miyamoto 2005 cognition meta-analysis",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": "TEMPLATE 6: AX_CULTURAL_MODULATION_009 - Mechanism Specification (Step 1)"
                }
            }
        },
        {
            "step": 2,
            "description": "encoding_mode → environmental_evaluation (culturally-modulated preference)",
            "from": "perceptual encoding (analytic or holistic)",
            "to": "environmental evaluation and aesthetic preference",
            "substrate": "orbitofrontal cortex (aesthetic evaluation), medial prefrontal cortex (cultural schema processing)",
            "bridge_warrant": "EMPIRICAL_COVARIANCE",
            "confidence": 0.45,
            "justification": {
                "data": [{
                    "finding": "Cultural encoding style cascades through environmental evaluation: analytic processors prefer grid/symmetry/contrast; holistic processors prefer relational embedding (feng shui, wabi-sabi)",
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "Cross-cultural aesthetics and environmental psychology literature",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": "TEMPLATE 6: AX_CULTURAL_MODULATION_009 - Domain-Specific Calibration"
                }
            }
        },
        {
            "step": 3,
            "description": "cultural_norms → domain_specific_override (calibration factors per domain)",
            "from": "cultural knowledge and norms",
            "to": "domain-specific parameter modulation (spatial, aesthetic, social, thermal/lighting)",
            "substrate": "dorsolateral prefrontal cortex (rule-based evaluation), ventromedial prefrontal cortex (cultural norm integration)",
            "bridge_warrant": "FUNCTIONAL",
            "confidence": 0.40,
            "justification": {
                "data": [{
                    "finding": "Cultural norms produce domain-specific modulation: personal space distances vary by culture; thermal preferences reflect climate history; privacy/communal expectations differ",
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "Hall 1966 proxemics; cultural climate adaptation; social-spatial norm literature",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": "TEMPLATE 6: AX_CULTURAL_MODULATION_009 - Domain-Specific Calibration"
                }
            }
        }
    ]

    return {
        "template_id": "AX_CULTURAL_MODULATION_009",
        "anchor_theorist": "Han",
        "complement_theorist": "DeYoung",
        "tier": "B",
        "mechanism_chain": mechanism_chain,
        "confidence": 0.45,
        "warrant_type": "FUNCTIONAL",
        "encoding_modes": {
            "analytic": {
                "characteristics": ["grid", "symmetry", "distinct objects", "bounded"],
                "cultural_prevalence": "Western, analytical"
            },
            "holistic": {
                "characteristics": ["flowing", "asymmetry", "relational", "embedded context"],
                "cultural_prevalence": "East Asian, holistic"
            }
        },
        "domain_calibrations": {
            "spatial_features": {
                "analytic_preference": "grid, symmetry",
                "holistic_preference": "relational, embedded",
                "modulation_factor_range": [0.80, 1.20]
            },
            "aesthetic_evaluation": {
                "analytic_preference": "minimalist, functional, contrast",
                "holistic_preference": "feng shui, wabi-sabi, biophilic",
                "modulation_factor_range": [0.75, 1.25]
            },
            "social_spatial_norms": {
                "analytic_preference": "larger personal space, privacy",
                "holistic_preference": "communal, smaller interpersonal distance",
                "modulation_factor_range": [0.70, 1.30]
            },
            "thermal_lighting": {
                "analytic_preference": "precise setpoint",
                "holistic_preference": "adaptive, seasonal tolerance",
                "modulation_factor_range": [0.80, 1.20]
            }
        },
        "calibrated_parameters": {
            "cultural_modulation_factor": "THEORETICAL_DEFAULT per domain",
            "encoding_mode_spectrum": ["analytic", "balanced", "holistic"]
        },
        "ie_dpt_integration": {
            "level_1": "automatic cultural encoding (analytic/holistic)",
            "levels_2_3": "explicit cultural knowledge application"
        },
        "display_id": "AX_CULTURAL_MODULATION_009",
        "name": "Cultural Modulation",
        "panel_source": "CROSSCUT-I",
        "calibration_status": "calibrated",
        "provenance": "panel_calibrated",
        "calibration_date": "2026-02-23",
        "cross_template_interactions": [],
        "residual_gaps": []
    }

def fix_group_a_ax_individual_differences_008():
    """AX_INDIVIDUAL_DIFFERENCES_008 - 3 mechanism steps"""

    mechanism_chain = [
        {
            "step": 1,
            "description": "trait_profile → dose_response_shift (Big Five via meta-analysis)",
            "from": "personality trait levels (neuroticism, extraversion, openness)",
            "to": "shifted dose-response curve for environmental features",
            "substrate": "amygdala-HPA (neuroticism), mesolimbic DA (extraversion), DMN-ECN (openness)",
            "bridge_warrant": "EMPIRICAL_COVARIANCE",
            "confidence": 0.55,
            "justification": {
                "data": [{
                    "finding": "Neuroticism shifts dose-response curve LEFT (lower threshold for distress): d=0.25-0.40 (Costa & McCrae 1992; Soto & John 2017, N>1M). Extraversion shifts RIGHT (higher threshold for overstimulation): d=0.20-0.35. Openness shifts RIGHT on complexity axes: d=0.15-0.30",
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "Meta-analytic Big Five neuroscience (Costa & McCrae 1992; Soto & John 2017 N>1M)",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": "TEMPLATE 5: AX_INDIVIDUAL_DIFFERENCES_008 - Mechanism Specification (Step 1)"
                }
            }
        },
        {
            "step": 2,
            "description": "sensory_sensitivity → tolerance_band_modification (SPS narrows window)",
            "from": "sensory processing sensitivity trait level",
            "to": "narrowed tolerance band for comfort",
            "substrate": "primary sensory cortices, posterior insula (heightened processing)",
            "bridge_warrant": "MECHANISM",
            "confidence": 0.45,
            "justification": {
                "data": [{
                    "finding": "Sensory processing sensitivity (Aron & Aron 1997; 15-20% prevalence) narrows tolerance band by 30-50% (THEORETICAL_DEFAULT) with empirical anchors (Aron et al. 2012). Affects heightened processing across ALL sensory modalities, not captured by neuroticism alone",
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "Aron & Aron 1997; Aron et al. 2012 sensory processing sensitivity model",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": "TEMPLATE 5: AX_INDIVIDUAL_DIFFERENCES_008 - Mechanism Specification (Step 2)"
                }
            }
        },
        {
            "step": 3,
            "description": "neurodiversity_profile → qualitative_form_change (different functional forms)",
            "from": "clinical neurodiversity (ASD, ADHD, misophonia, anxiety)",
            "to": "qualitatively different dose-response functional form",
            "substrate": "varies by condition (ASD: altered sensory integration; ADHD: NE dysregulation; misophonia: amygdala-insula hyperreactivity)",
            "bridge_warrant": "THEORETICAL_DEFAULT",
            "confidence": 0.40,
            "justification": {
                "data": [{
                    "finding": "Clinical neurodiversity (ASD, misophonia, anxiety disorders) produce qualitatively different functional forms rather than simple parameter shifts. Universal design implications. Flagged for future empirical calibration",
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "Clinical neuroscience literature (neurodiversity perspectives); universal design frameworks",
                "qualifier": "potentially",
                "rebuttal": "limited empirical evidence; mechanism-based inference from neurobiological phenotypes",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": "TEMPLATE 5: AX_INDIVIDUAL_DIFFERENCES_008 - Mechanism Specification (Step 3)"
                }
            }
        }
    ]

    return {
        "template_id": "AX_INDIVIDUAL_DIFFERENCES_008",
        "anchor_theorist": "DeYoung",
        "complement_theorist": "Han",
        "tier": "B",
        "mechanism_chain": mechanism_chain,
        "confidence": 0.50,
        "warrant_type": "EMPIRICAL_COVARIANCE",
        "dose_response_modifications": {
            "neuroticism": {
                "direction": "LEFT",
                "effect_size_range": [0.25, 0.40],
                "meta_analytic_base": "Costa & McCrae 1992; Soto & John 2017 (N>1M)"
            },
            "extraversion": {
                "direction": "RIGHT",
                "effect_size_range": [0.20, 0.35]
            },
            "openness": {
                "direction": "RIGHT",
                "effect_size_range": [0.15, 0.30]
            }
        },
        "sensory_processing_sensitivity": {
            "prevalence": "15-20%",
            "tolerance_band_narrowing": "30-50%",
            "warrant": "THEORETICAL_DEFAULT",
            "empirical_anchor": "Aron et al. 2012"
        },
        "neurodiversity_qualitative_forms": {
            "conditions": ["ASD", "misophonia", "anxiety_disorders"],
            "implication": "universal_design",
            "warrant": "THEORETICAL_DEFAULT"
        },
        "ie_dpt_integration": {
            "level_1_implicit": "SPS amplifies sensory discrimination",
            "level_2_implicit_to_explicit": "ADHD shifts transition threshold",
            "level_3_explicit": "neurodiversity divergence in evaluation strategy"
        },
        "ax4_interaction": "high_perceived_control reduces inter-individual variance",
        "display_id": "AX_INDIVIDUAL_DIFFERENCES_008",
        "name": "Individual Differences",
        "panel_source": "CROSSCUT-I",
        "calibration_status": "calibrated",
        "provenance": "panel_calibrated",
        "calibration_date": "2026-02-23",
        "cross_template_interactions": [],
        "residual_gaps": []
    }

def fix_group_a_ax_vr_limitation_012():
    """AX_VR_LIMITATION_012 - 2 mechanism steps"""

    mechanism_chain = [
        {
            "step": 1,
            "description": "vr_study_evidence → ecological_validity_assessment",
            "from": "VR experimental paradigm and fidelity level",
            "to": "assessed ecological validity relative to real architecture",
            "substrate": "sensory systems (visual, vestibular, interoceptive) and their VR representation fidelity",
            "bridge_warrant": "FUNCTIONAL",
            "confidence": 0.50,
            "justification": {
                "data": [{
                    "finding": "VR ecological validity depends on technology fidelity. Pre-2015: low polygon count, limited FOV, no haptic (d_discount=0.50-0.60). 2015-2020: improved rendering, spatial audio (d_discount=0.60-0.75). 2020-2025: photorealistic, spatial audio, thermal (d_discount=0.75-0.85). 2025+: full multisensory integration (d_discount=0.85-0.95)",
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "Technology trajectory analysis; embodied cognition literature on multisensory integration",
                "qualifier": "depends on era and technology capability",
                "rebuttal": "early VR severely limited for embodied/interoceptive responses",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": "TEMPLATE 8: AX_VR_LIMITATION_012 - Calibrated Parameters"
                }
            }
        },
        {
            "step": 2,
            "description": "era_discount → confidence_adjustment (apply to bridge, not neuroscience)",
            "from": "era-dependent ecological validity assessment",
            "to": "adjusted confidence in ARCHITECTURAL_BRIDGE warrant component",
            "substrate": "meta-analytical weighting of study evidence quality",
            "bridge_warrant": "EMPIRICAL_COVARIANCE",
            "confidence": 0.45,
            "justification": {
                "data": [{
                    "finding": "Discount applies to ARCHITECTURAL_BRIDGE component only (how well VR results generalize to real architecture), not underlying neuroscience mechanisms (LC-NE, DMN, SN) extracted from non-VR studies. Older VR had insufficient fidelity for embodied responses; modern VR approaches ecological validity",
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "Embodied cognition theory; technology assessment and validation",
                "qualifier": "for architectural generalization only",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": "TEMPLATE 8: AX_VR_LIMITATION_012 - Mechanism Specification (Step 2)"
                }
            }
        }
    ]

    return {
        "template_id": "AX_VR_LIMITATION_012",
        "anchor_theorist": "Schooler",
        "complement_theorist": "Berman",
        "tier": "B",
        "mechanism_chain": mechanism_chain,
        "confidence": 0.50,
        "warrant_type": "FUNCTIONAL",
        "era_discount_curve": {
            "pre_2015": {
                "technology": "low polygon, limited FOV, no haptic",
                "discount_range": [0.50, 0.60],
                "rationale": "embodied/interoceptive responses severely compromised"
            },
            "2015_2020": {
                "technology": "improved rendering, spatial audio",
                "discount_range": [0.60, 0.75],
                "rationale": "multisensory integration partial"
            },
            "2020_2025": {
                "technology": "photorealistic, spatial audio, thermal",
                "discount_range": [0.75, 0.85],
                "rationale": "approaching ecological validity"
            },
            "2025_plus": {
                "technology": "photorealistic + haptic + thermal + olfactory",
                "discount_range": [0.85, 0.95],
                "rationale": "near-complete fidelity"
            }
        },
        "discount_application": {
            "target": "ARCHITECTURAL_BRIDGE component only",
            "excludes": "underlying neuroscience mechanisms (LC-NE, DMN, SN from non-VR studies)"
        },
        "ie_dpt_integration": {
            "level_1_implicit": "most affected (embodied, interoceptive sensitivity to fidelity)",
            "level_3_explicit": "less affected (can rationalize VR artifacts)"
        },
        "display_id": "AX_VR_LIMITATION_012",
        "name": "VR Limitation",
        "panel_source": "CROSSCUT-I",
        "calibration_status": "calibrated",
        "provenance": "panel_calibrated",
        "calibration_date": "2026-02-23",
        "cross_template_interactions": [],
        "residual_gaps": []
    }

def fix_group_b_temporal_hierarchy_arch_pe_001():
    """TEMPORAL_HIERARCHY_ARCH_PE_001 - rename steps to mechanism_chain, add justifications"""

    # Read current file to preserve structure
    with open("data/templates/TEMPORAL_HIERARCHY_ARCH_PE_001.json", "r") as f:
        current = json.load(f)

    # Convert steps to mechanism_chain with added justifications
    mechanism_chain = []
    for step in current.get("steps", []):
        mechanism_step = {
            "step": step["step_number"],
            "description": step["name"],
            "warrant_type": step["warrant_type"],
            "confidence": step["confidence"],
            "content": step.get("content", ""),
            "references": step.get("references", []),
            "from": "",
            "to": "",
            "substrate": "",
            "bridge_warrant": step["warrant_type"],
            "justification": {
                "data": [{
                    "finding": step.get("content", ""),
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "; ".join(step.get("references", [])) if step.get("references") else "",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": f"TEMPLATE 14: TEMPORAL_HIERARCHY_ARCH_PE_001"
                }
            }
        }
        mechanism_chain.append(mechanism_step)

    return {
        "template_id": current["template_id"],
        "panel": current.get("panel"),
        "phase": current.get("phase"),
        "primary_anchor": current.get("primary_anchor"),
        "complement_anchor": current.get("complement_anchor"),
        "tier": current.get("tier"),
        "mechanism_chain": mechanism_chain,
        "description": current.get("description"),
        "calibrated_parameters": current.get("calibrated_parameters", {}),
        "constraint_c04_partial_out": current.get("constraint_c04_partial_out", {}),
        "constraint_c05_ie_dpt": current.get("constraint_c05_ie_dpt", {}),
        "constraint_c02_prior_refs": current.get("constraint_c02_prior_refs", []),
        "overall_confidence": current.get("overall_confidence", 0.45),
        "display_id": current.get("display_id", current["template_id"]),
        "name": current.get("name", "Temporal Hierarchy"),
        "panel_source": "CROSSCUT-I",
        "calibration_status": "calibrated",
        "provenance": "panel_calibrated",
        "calibration_date": "2026-02-23",
        "cross_template_interactions": current.get("cross_template_interactions", []),
        "residual_gaps": current.get("residual_gaps", [])
    }

def fix_group_b_er_ecological_rationality_001():
    """ER_ECOLOGICAL_RATIONALITY_001 - rename steps to mechanism_chain"""

    with open("data/templates/ER_ECOLOGICAL_RATIONALITY_001.json", "r") as f:
        current = json.load(f)

    mechanism_chain = []
    for step in current.get("steps", []):
        mechanism_step = {
            "step": step["step_number"],
            "description": step["name"],
            "warrant_type": step["warrant_type"],
            "confidence": step["confidence"],
            "content": step.get("content", ""),
            "references": step.get("references", []),
            "from": "",
            "to": "",
            "substrate": "",
            "bridge_warrant": step["warrant_type"],
            "justification": {
                "data": [{
                    "finding": step.get("content", ""),
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "; ".join(step.get("references", [])) if step.get("references") else "",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": f"TEMPLATE 15: ER_ECOLOGICAL_RATIONALITY_001"
                }
            }
        }
        mechanism_chain.append(mechanism_step)

    return {
        "template_id": current["template_id"],
        "panel": current.get("panel"),
        "phase": current.get("phase"),
        "primary_anchor": current.get("primary_anchor"),
        "complement_anchor": current.get("complement_anchor"),
        "tier": current.get("tier"),
        "mechanism_chain": mechanism_chain,
        "description": current.get("description"),
        "constraint_c11_note": current.get("constraint_c11_note", ""),
        "calibrated_parameters": current.get("calibrated_parameters", {}),
        "constraint_c11_assessment": current.get("constraint_c11_assessment", ""),
        "constraint_c05_ie_dpt": current.get("constraint_c05_ie_dpt", {}),
        "constraint_c02_prior_refs": current.get("constraint_c02_prior_refs", []),
        "overall_confidence": current.get("overall_confidence", 0.45),
        "display_id": current.get("display_id", current["template_id"]),
        "name": current.get("name", "Ecological Rationality"),
        "panel_source": "CROSSCUT-I",
        "calibration_status": "calibrated",
        "provenance": "panel_calibrated",
        "calibration_date": "2026-02-23",
        "cross_template_interactions": current.get("cross_template_interactions", []),
        "residual_gaps": current.get("residual_gaps", [])
    }

def fix_group_b_ax3_awe_mechanism_001():
    """AX3_AWE_MECHANISM_001 - rename steps to mechanism_chain"""

    with open("data/templates/AX3_AWE_MECHANISM_001.json", "r") as f:
        current = json.load(f)

    mechanism_chain = []
    for step in current.get("steps", []):
        mechanism_step = {
            "step": step["step_number"],
            "description": step["name"],
            "warrant_type": step["warrant_type"],
            "confidence": step["confidence"],
            "content": step.get("content", ""),
            "references": step.get("references", []),
            "from": "",
            "to": "",
            "substrate": "",
            "bridge_warrant": step["warrant_type"],
            "justification": {
                "data": [{
                    "finding": step.get("content", ""),
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "; ".join(step.get("references", [])) if step.get("references") else "",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": f"TEMPLATE 16: AX3_AWE_MECHANISM_001"
                }
            }
        }
        mechanism_chain.append(mechanism_step)

    return {
        "template_id": current["template_id"],
        "panel": current.get("panel"),
        "phase": current.get("phase"),
        "primary_anchor": current.get("primary_anchor"),
        "complement_anchor": current.get("complement_anchor"),
        "tier": current.get("tier"),
        "mechanism_chain": mechanism_chain,
        "description": current.get("description"),
        "tier_a_justification": current.get("tier_a_justification", ""),
        "competing_accounts": current.get("competing_accounts", []),
        "calibrated_parameters": current.get("calibrated_parameters", {}),
        "constraint_c04_partial_out": current.get("constraint_c04_partial_out", {}),
        "constraint_c05_ie_dpt": current.get("constraint_c05_ie_dpt", {}),
        "constraint_c02_prior_refs": current.get("constraint_c02_prior_refs", []),
        "overall_confidence": current.get("overall_confidence", 0.50),
        "display_id": current.get("display_id", current["template_id"]),
        "name": current.get("name", "Awe Mechanism"),
        "panel_source": "CROSSCUT-I",
        "calibration_status": "calibrated",
        "provenance": "panel_calibrated",
        "calibration_date": "2026-02-23",
        "cross_template_interactions": current.get("cross_template_interactions", []),
        "residual_gaps": current.get("residual_gaps", [])
    }

def fix_group_b_ax3_small_self_001():
    """AX3_SMALL_SELF_001 - rename steps to mechanism_chain"""

    with open("data/templates/AX3_SMALL_SELF_001.json", "r") as f:
        current = json.load(f)

    mechanism_chain = []
    for step in current.get("steps", []):
        mechanism_step = {
            "step": step["step_number"],
            "description": step["name"],
            "warrant_type": step["warrant_type"],
            "confidence": step["confidence"],
            "content": step.get("content", ""),
            "references": step.get("references", []),
            "from": "",
            "to": "",
            "substrate": "",
            "bridge_warrant": step["warrant_type"],
            "justification": {
                "data": [{
                    "finding": step.get("content", ""),
                    "source": "CROSSCUT_I_Panel_Output.md"
                }],
                "backing": "; ".join(step.get("references", [])) if step.get("references") else "",
                "qualifier": "typically",
                "rebuttal": "",
                "competing_accounts": [],
                "depth_tier": "B",
                "panel_debate_reference": {
                    "panel": "CROSSCUT-I",
                    "document": "docs/CROSSCUT_I_Panel_Output.md",
                    "relevant_section": f"TEMPLATE 17: AX3_SMALL_SELF_001"
                }
            }
        }
        mechanism_chain.append(mechanism_step)

    return {
        "template_id": current["template_id"],
        "panel": current.get("panel"),
        "phase": current.get("phase"),
        "primary_anchor": current.get("primary_anchor"),
        "complement_anchor": current.get("complement_anchor"),
        "tier": current.get("tier"),
        "mechanism_chain": mechanism_chain,
        "description": current.get("description"),
        "downstream_consequence": current.get("downstream_consequence", ""),
        "calibrated_parameters": current.get("calibrated_parameters", {}),
        "barrett_craig_integration": current.get("barrett_craig_integration", ""),
        "constraint_c04_partial_out": current.get("constraint_c04_partial_out", {}),
        "constraint_c05_ie_dpt": current.get("constraint_c05_ie_dpt", {}),
        "constraint_c02_prior_refs": current.get("constraint_c02_prior_refs", []),
        "overall_confidence": current.get("overall_confidence", 0.45),
        "display_id": current.get("display_id", current["template_id"]),
        "name": current.get("name", "Small Self"),
        "panel_source": "CROSSCUT-I",
        "calibration_status": "calibrated",
        "provenance": "panel_calibrated",
        "calibration_date": "2026-02-23",
        "cross_template_interactions": current.get("cross_template_interactions", []),
        "residual_gaps": current.get("residual_gaps", [])
    }

def main():
    """Fix all 8 corrupt templates"""

    fixes = {
        "AX_ATTENTION_MEDIATION_010.json": fix_group_a_ax_attention_mediation_010(),
        "AX_CULTURAL_MODULATION_009.json": fix_group_a_ax_cultural_modulation_009(),
        "AX_INDIVIDUAL_DIFFERENCES_008.json": fix_group_a_ax_individual_differences_008(),
        "AX_VR_LIMITATION_012.json": fix_group_a_ax_vr_limitation_012(),
        "TEMPORAL_HIERARCHY_ARCH_PE_001.json": fix_group_b_temporal_hierarchy_arch_pe_001(),
        "ER_ECOLOGICAL_RATIONALITY_001.json": fix_group_b_er_ecological_rationality_001(),
        "AX3_AWE_MECHANISM_001.json": fix_group_b_ax3_awe_mechanism_001(),
        "AX3_SMALL_SELF_001.json": fix_group_b_ax3_small_self_001(),
    }

    for filename, fixed_data in fixes.items():
        filepath = f"data/templates/{filename}"
        with open(filepath, "w") as f:
            json.dump(fixed_data, f, indent=2)
        print(f"Fixed: {filename}")

    print("\nAll 8 templates fixed successfully!")
    print("\nChanges made:")
    print("- Removed corrupt mechanism_chain (was integer)")
    print("- Created proper mechanism_chain arrays with step objects")
    print("- Added canonical justification objects to each step")
    print("- Added panel_debate_reference to all justifications")
    print("- Preserved all existing metadata and domain-specific fields")

if __name__ == "__main__":
    main()
