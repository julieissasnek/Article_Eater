# SPRINT 7 THEORY ARTIFACTS: Data Structures for Implementation
## Article Eater — Opus-Side Deliverable
## Version 1.0 — February 15, 2026

**Purpose**: This document provides the actual typed data that Claude Code needs to
seed the theory tier. It contains three deliverables:

1. **Framework Scope Declarations** (Task 7.6) — what each framework "owns"
2. **Independence Matrix** (Task 7.4) — numeric scores for framework interactions
3. **Seed Template Encodings** (Task 7.5) — 8 templates as Python-compatible structures

**Variable naming convention**: Provisional snake_case names pending audit reconciliation.
Names marked with `# AUDIT-CHECK` need verification against existing codebase.

---

# SECTION 1: FRAMEWORK SCOPE DECLARATIONS

Each Tier 1 framework declares:
- Its canonical ID
- The variables it "owns" (can make mechanistic claims about)
- The outcome domains it speaks to
- The timescales it operates on
- Its boundary: what it CANNOT explain

```python
TIER1_FRAMEWORKS = {

    "PP": {
        "full_name": "Predictive Processing",
        "canonical_id": "PP",
        "owned_variables": [
            "prediction_error_magnitude",       # AUDIT-CHECK
            "prediction_error_valence",         # positive surprise vs negative
            "precision_weighting",              # confidence in prediction
            "generative_model_quality",         # how good the internal model is
            "spectral_match_efficiency",        # 1/f statistics match
            "visual_complexity",                # stimulus complexity dimension
            "auditory_complexity",
            "olfactory_complexity",
            "cultural_prior_distribution",      # learned statistical expectations
            "active_inference_policy_space",    # available PE-reducing actions
            "expected_free_energy",             # formal quantity from FEP
        ],
        "outcome_domains": [
            "cognitive_load",
            "metabolic_efficiency",
            "hedonic_valence",
            "approach_avoidance",
        ],
        "timescales": ["<200ms", "200ms-1s", "1-30s"],
        "cannot_explain": [
            "Why specific actions are chosen (only that PE-reducing actions are preferred)",
            "Social cognition (social PE uses different circuits)",
            "Long-term allostatic accumulation (feeds into NM/IC)",
        ],
    },

    "SN": {
        "full_name": "Spatial Navigation / Cognitive Mapping",
        "canonical_id": "SN",
        "owned_variables": [
            "cognitive_map_quality",            # AUDIT-CHECK
            "place_cell_stability",
            "grid_cell_coherence",
            "boundary_cell_activation",
            "theta_sequence_coherence",
            "wayfinding_efficiency",
            "spatial_layout_legibility",        # AUDIT-CHECK
            "landmark_distinctiveness",
            "path_continuity",
            "navigational_hierarchy_depth",
            "context_representation_stability",  # hippocampal context code
        ],
        "outcome_domains": [
            "wayfinding_performance",
            "spatial_anxiety",
            "cognitive_load_navigation",
            "memory_context_binding",
        ],
        "timescales": ["1-30s", "1-20min", "days-weeks"],
        "cannot_explain": [
            "Affective responses to spaces beyond navigation stress",
            "Aesthetic judgments (uses PP for complexity, DP for evaluation)",
            "Social behavior in spaces (uses EC/Social Brain)",
        ],
    },

    "DP": {
        "full_name": "Dual-Process Evaluation",
        "canonical_id": "DP",
        "owned_variables": [
            "implicit_evaluation_valence",      # fast System 1
            "explicit_evaluation_valence",      # slow System 2
            "implicit_explicit_discrepancy",    # mismatch between the two
            "processing_fluency",
            "subcortical_evaluation_speed",     # amygdala + basal ganglia
            "evaluation_override_probability",  # when explicit overrides implicit
        ],
        "outcome_domains": [
            "preference_judgment",
            "approach_avoidance",
            "aesthetic_evaluation",
        ],
        "timescales": ["<200ms", "200ms-1s"],
        "cannot_explain": [
            "What the implicit evaluation IS based on (PP provides the input)",
            "Long-term preference change (requires Memory Systems)",
            "Body-level responses (requires IC/EC)",
        ],
    },

    "DT": {
        "full_name": "DMN/TPN Dynamics",
        "canonical_id": "DT",
        "owned_variables": [
            "tpn_engagement_level",
            "dmn_engagement_level",
            "dmn_mtl_subsystem_activity",       # scene construction, memory
            "dmn_dmpfc_subsystem_activity",     # social cognition, self
            "directed_attention_fatigue",       # AUDIT-CHECK
            "restoration_level",
            "dmn_tpn_switching_efficiency",
        ],
        "outcome_domains": [
            "attentional_capacity",
            "creative_thinking",
            "social_cognition",
            "self_regulation",
            "memory_consolidation",
        ],
        "timescales": ["200ms-1s", "1-20min", "20min-hours"],
        "cannot_explain": [
            "What drives TPN engagement (specific demands come from PP, SN, HC)",
            "Sleep-dependent restoration (requires Chronobiological)",
            "Specific memory content (requires Memory Systems)",
        ],
    },

    "NM": {
        "full_name": "Neuromodulatory Systems",
        "canonical_id": "NM",
        "owned_variables": [
            "cortisol_level",                   # AUDIT-CHECK
            "cortisol_diurnal_slope",
            "norepinephrine_tonic_level",       # LC tonic mode
            "norepinephrine_phasic_response",   # LC phasic mode
            "dopamine_reward_pe",               # VTA/NAc reward prediction error
            "dopamine_incentive_salience",      # wanting
            "acetylcholine_tonic_level",        # BF expected uncertainty
            "serotonin_level",
            "hpa_axis_activation",              # AUDIT-CHECK
            "allostatic_load",                  # cumulative stress burden
            "allostatic_budget_surplus",        # remaining capacity
            "explore_exploit_state",
        ],
        "outcome_domains": [
            "stress_physiology",
            "arousal_level",
            "motivation_approach",
            "learning_rate",
            "immune_function",
        ],
        "timescales": ["200ms-1s", "1-20min", "20min-hours", "days-weeks", "months-years"],
        "cannot_explain": [
            "Why specific stimuli are threats (requires PP appraisal + DP evaluation)",
            "Spatial specificity of stress responses (requires SN)",
            "Subjective experience of emotion (requires IC)",
        ],
    },

    "IC": {
        "full_name": "Interoceptive / Constructionist Affect",
        "canonical_id": "IC",
        "owned_variables": [
            "interoceptive_prediction_error",
            "interoceptive_sensitivity",        # individual difference
            "body_state_valence",               # pleasant/unpleasant
            "body_state_arousal",               # activated/deactivated
            "affect_construction_category",     # the emotion label
            "allostatic_prediction_quality",    # how well brain predicts body needs
            "metabolic_efficiency",
        ],
        "outcome_domains": [
            "subjective_emotion",
            "mood",
            "wellbeing",
            "emotional_granularity",
        ],
        "timescales": ["200ms-1s", "1-30s", "1-20min"],
        "cannot_explain": [
            "What changes body state (all other frameworks provide inputs)",
            "Cognitive appraisal content (requires PP, DP)",
            "Basic emotion circuits IF they exist (contested with basic emotion theory)",
        ],
        "contested_claims": [
            "Constructionism vs basic emotions at link 3 of Template 12",
        ],
    },

    "MS": {
        "full_name": "Memory Systems",
        "canonical_id": "MS",
        "owned_variables": [
            "episodic_memory_encoding_strength",
            "context_memory_binding_quality",
            "memory_consolidation_rate",
            "spw_r_replay_frequency",            # sharp-wave ripples
            "schema_integration_quality",
            "familiarity_signal",
            "recollection_signal",
        ],
        "outcome_domains": [
            "learning_retention",
            "spatial_knowledge",
            "environmental_familiarity",
            "nostalgia_attachment",
        ],
        "timescales": ["1-20min", "20min-hours", "days-weeks"],
        "cannot_explain": [
            "Perceptual processing of environments (requires PP)",
            "Emotional quality of memories (requires IC, NM)",
            "Active navigation (requires SN)",
        ],
    },

    "EC": {
        "full_name": "Embodied Cognition",
        "canonical_id": "EC",
        "owned_variables": [
            "affordance_perception",            # AUDIT-CHECK
            "postural_state",
            "muscle_tension_pattern",
            "vagal_tone",
            "motor_preparation_state",
            "cognitive_offloading_degree",
            "environmental_legibility",          # AUDIT-CHECK — may overlap SN
            "vestibular_engagement",
        ],
        "outcome_domains": [
            "movement_behavior",
            "autonomic_regulation",
            "cognitive_load_reduction",
            "embodied_affect",
        ],
        "timescales": ["200ms-1s", "1-30s"],
        "cannot_explain": [
            "Spatial memory and mapping (requires SN)",
            "Conscious emotional experience (requires IC)",
            "Higher-order cognition (requires HC/EF)",
        ],
    },

    "CB": {
        "full_name": "Chronobiological Regulation",
        "canonical_id": "CB",
        "owned_variables": [
            "circadian_phase",
            "scn_entrainment_quality",
            "melatonin_onset_timing",
            "cortisol_awakening_response",       # shares with NM
            "core_body_temperature_rhythm",
            "immune_cycling_quality",
            "light_exposure_dose",               # lux × duration × spectrum
            "social_zeitgeber_strength",
        ],
        "outcome_domains": [
            "sleep_quality",
            "cognitive_performance_timing",
            "immune_function",
            "metabolic_regulation",
            "mood_regulation",
        ],
        "timescales": ["20min-hours", "days-weeks"],
        "cannot_explain": [
            "Acute environmental responses (requires PP, NM)",
            "Spatial processing (requires SN)",
            "Aesthetic judgment (requires PP, DP)",
        ],
    },

    "MSI": {
        "full_name": "Multisensory Integration",
        "canonical_id": "MSI",
        "owned_variables": [
            "crossmodal_congruency",
            "multisensory_enhancement_magnitude",
            "inverse_effectiveness_factor",
            "temporal_binding_window",
            "spatial_congruence_window",
            "reliability_weighting_per_modality",
            "dominant_modality",                 # which sense currently leads
        ],
        "outcome_domains": [
            "environmental_coherence_percept",
            "comfort_satisfaction",
            "object_recognition",
            "spatial_perception",
        ],
        "timescales": ["<200ms", "200ms-1s"],
        "cannot_explain": [
            "Unisensory processing within a modality (requires PP)",
            "Memory for multisensory experiences (requires MS)",
            "Higher-order meaning (requires DP, HC)",
        ],
    },
}
```

---

# SECTION 2: FRAMEWORK INDEPENDENCE MATRIX

## Purpose

When the CMR pipeline combines predictions from multiple frameworks, it needs to
know whether the frameworks are making independent predictions or overlapping ones.
Independence = 1.0 means the frameworks use entirely different neural systems and
share no variables. Independence = 0.0 means one is a subset of the other.

## Matrix

```python
# Independence scores: 0.0 (fully dependent) to 1.0 (fully independent)
# These are SYMMETRIC: INDEPENDENCE_MATRIX["PP"]["SN"] == INDEPENDENCE_MATRIX["SN"]["PP"]
# Scores reflect shared variables, neural circuits, and computational overlap

INDEPENDENCE_MATRIX = {
    #         PP    SN    DP    DT    NM    IC    MS    EC    CB    MSI
    "PP":  {"PP": 0.0, "SN": 0.7, "DP": 0.4, "DT": 0.5, "NM": 0.5, "IC": 0.4, "MS": 0.6, "EC": 0.5, "CB": 0.8, "MSI": 0.3},
    "SN":  {"PP": 0.7, "SN": 0.0, "DP": 0.8, "DT": 0.6, "NM": 0.5, "IC": 0.7, "MS": 0.3, "EC": 0.5, "CB": 0.8, "MSI": 0.7},
    "DP":  {"PP": 0.4, "SN": 0.8, "DP": 0.0, "DT": 0.6, "NM": 0.6, "IC": 0.4, "MS": 0.7, "EC": 0.7, "CB": 0.9, "MSI": 0.6},
    "DT":  {"PP": 0.5, "SN": 0.6, "DP": 0.6, "DT": 0.0, "NM": 0.4, "IC": 0.5, "MS": 0.3, "EC": 0.6, "CB": 0.5, "MSI": 0.7},
    "NM":  {"PP": 0.5, "SN": 0.5, "DP": 0.6, "DT": 0.4, "NM": 0.0, "IC": 0.3, "MS": 0.5, "EC": 0.5, "CB": 0.3, "MSI": 0.7},
    "IC":  {"PP": 0.4, "SN": 0.7, "DP": 0.4, "DT": 0.5, "NM": 0.3, "IC": 0.0, "MS": 0.6, "EC": 0.2, "CB": 0.6, "MSI": 0.5},
    "MS":  {"PP": 0.6, "SN": 0.3, "DP": 0.7, "DT": 0.3, "NM": 0.5, "IC": 0.6, "MS": 0.0, "EC": 0.7, "CB": 0.5, "MSI": 0.7},
    "EC":  {"PP": 0.5, "SN": 0.5, "DP": 0.7, "DT": 0.6, "NM": 0.5, "IC": 0.2, "MS": 0.7, "EC": 0.0, "CB": 0.8, "MSI": 0.4},
    "CB":  {"PP": 0.8, "SN": 0.8, "DP": 0.9, "DT": 0.5, "NM": 0.3, "IC": 0.6, "MS": 0.5, "EC": 0.8, "CB": 0.0, "MSI": 0.8},
    "MSI": {"PP": 0.3, "SN": 0.7, "DP": 0.6, "DT": 0.7, "NM": 0.7, "IC": 0.5, "MS": 0.7, "EC": 0.4, "CB": 0.8, "MSI": 0.0},
}
```

## Justification for Key Scores

### Low independence (high overlap):
- **IC ↔ EC = 0.2**: Embodied cognition directly produces the body state changes that interoceptive inference reads. Postural → vagal tone → interoceptive signals is a near-continuous pipeline.
- **MSI ↔ PP = 0.3**: Multisensory integration IS prediction error computation across modalities. Crossmodal congruency = crossmodal PE. Reliability weighting = precision weighting. MSI is essentially PP applied to multi-modal inputs.
- **NM ↔ IC = 0.3**: Neuromodulatory state changes (cortisol, NE, DA) directly alter body state → interoceptive signals. The distinction is that NM specifies the mechanism (which molecule, which receptor) while IC specifies what the brain does with the resulting body signal.
- **NM ↔ CB = 0.3**: Chronobiological regulation operates largely through neuromodulatory systems (melatonin, cortisol rhythm, arousal cycling). CB adds the temporal structure; NM provides the effectors.
- **SN ↔ MS = 0.3**: Spatial navigation IS a memory system — the hippocampus does both. Context codes are place cell ensembles. Theta sequences during navigation become SPW-R replays during rest. These are deeply intertwined.
- **DT ↔ MS = 0.3**: DMN-MTL subsystem engagement IS memory consolidation in a different vocabulary. SPW-Rs occur during DMN engagement. These are the same neural events described from different theoretical angles.

### High independence (minimal overlap):
- **DP ↔ CB = 0.9**: Dual-process evaluation and circadian regulation use entirely different neural systems and have no shared computational principles. Time-of-day might modulate evaluation capacity, but this is a distal moderation, not shared mechanism.
- **PP ↔ CB = 0.8**: Predictive processing and circadian regulation share almost nothing. The only connection is that circadian phase modulates cortical excitability and therefore PE computation efficiency — very distal.
- **SN ↔ CB = 0.8**: Spatial navigation and circadian regulation share little. The hippocampus has some circadian modulation but this is not a core interaction.

### Usage Rule

When the CMR pipeline produces predictions from two frameworks about the same outcome:
- **Independence ≥ 0.7**: Predictions can be treated as approximately additive. Both are informative. Cross-framework convergence is strong evidence.
- **Independence 0.4–0.7**: Predictions partially overlap. Combined effect is less than sum. Convergence is moderate evidence.
- **Independence < 0.4**: Predictions are substantially overlapping. "Convergence" from these frameworks is NOT strong evidence because they share mechanism. Use the more specific framework's prediction.

---

# SECTION 3: SEED TEMPLATE ENCODINGS

## Encoding Format

These 8 templates are chosen to cover all 10 frameworks at least once and to span
the maturity range (how-actually to how-possibly). CC should implement these first
as the `MechanisticTemplate` data structure, then extend to all 40.

```python
from enum import Enum
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, field

class MaturityLevel(Enum):
    HOW_ACTUALLY = "how-actually"
    HOW_PLAUSIBLY = "how-plausibly"
    HOW_POSSIBLY = "how-possibly"

class BridgingQuality(Enum):
    HIGH = "high"
    MEDIUM_HIGH = "medium-high"
    MEDIUM = "medium"
    LOW_MEDIUM = "low-medium"
    LOW = "low"

class AnalysisLevel(Enum):
    """Craver's levels of mechanism"""
    ECOLOGICAL = "ecological"
    BEHAVIORAL = "behavioral"
    PSYCHOLOGICAL = "psychological"
    COMPUTATIONAL = "computational"
    CIRCUIT = "circuit"
    CELLULAR = "cellular"
    MOLECULAR = "molecular"
    SYSTEMS = "systems"
    CLINICAL = "clinical"

@dataclass
class ScopeCondition:
    condition: str
    effect: str  # what happens when condition is violated

@dataclass
class Moderator:
    variable: str
    effect_direction: str  # "increases", "decreases", "shifts_curve", "inverts"
    mechanism: str

@dataclass
class ParameterEstimate:
    variable: str
    value_low: Optional[float]
    value_high: Optional[float]
    unit: str
    confidence: str  # "measured", "estimated", "extrapolated"
    source: str

@dataclass
class CausalLink:
    from_variable: str
    to_variable: str
    activity: str  # what the mechanism DOES at this step
    from_level: AnalysisLevel
    to_level: AnalysisLevel
    bridging_quality: BridgingQuality
    maturity: MaturityLevel
    key_evidence: List[str]  # citation strings
    parameters: List[ParameterEstimate] = field(default_factory=list)
    is_contested: bool = False
    contested_by: Optional[str] = None

@dataclass
class TemplateInteraction:
    target_template_id: str
    shared_variable: str
    interaction_type: str  # "feeds_into", "competes_with", "modulates", "gates"
    description: str

@dataclass
class MechanisticTemplate:
    template_id: str
    name: str
    structural_pattern: str
    higher_order_principle: Optional[str]
    transferable_to: List[str]
    framework_ids: List[str]  # which Tier 1 frameworks this belongs to
    causal_links: List[CausalLink]
    scope_conditions: List[ScopeCondition]
    moderators: List[Moderator]
    interactions: List[TemplateInteraction]
    overall_maturity: MaturityLevel
    key_references: List[str]
    architectural_prediction: Optional[str] = None
    is_composed: bool = False
    component_template_ids: List[str] = field(default_factory=list)
```

---

## Seed Template 1: NM_THREAT_HPA_001 (T5)
**Chosen because**: how-actually, excellent params, foundational stress pathway

```python
T5_NM_THREAT_HPA_001 = MechanisticTemplate(
    template_id="NM_THREAT_HPA_001",
    name="Environmental threat cues → amygdala → HPA axis → cortisol",
    structural_pattern="threat_detection → stress_cascade → physiological_mobilization",
    higher_order_principle=None,
    transferable_to=["any threat-related stimulus", "social threat", "financial threat cues"],
    framework_ids=["NM"],
    causal_links=[
        CausalLink(
            from_variable="environmental_threat_cues",  # AUDIT-CHECK
            to_variable="amygdala_activation",
            activity="rapid threat evaluation via subcortical visual pathway (SC → pulvinar → amygdala)",
            from_level=AnalysisLevel.ECOLOGICAL,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "LeDoux, 1996 (~15,000 citations)",
                "Ohman & Mineka, 2001 (~3,000 citations)",
            ],
            parameters=[
                ParameterEstimate("amygdala_response_onset_subcortical", 120, 120, "ms", "measured", "LeDoux 1996"),
                ParameterEstimate("amygdala_response_onset_cortical", 170, 170, "ms", "measured", "LeDoux 1996"),
            ],
        ),
        CausalLink(
            from_variable="amygdala_activation",
            to_variable="cortisol_elevation",
            activity="HPA axis cascade: amygdala → hypothalamic CRH → pituitary ACTH → adrenal cortisol",
            from_level=AnalysisLevel.CIRCUIT,
            to_level=AnalysisLevel.MOLECULAR,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "McEwen, 2007 (~5,500 citations)",
                "Ulrich-Lai & Herman, 2009 (~2,000 citations)",
            ],
            parameters=[
                ParameterEstimate("cortisol_onset", 15, 20, "min", "measured", "McEwen 2007"),
                ParameterEstimate("cortisol_peak", 30, 45, "min", "measured", "McEwen 2007"),
                ParameterEstimate("cortisol_recovery_halflife", 60, 60, "min", "measured", "McEwen 2007"),
                ParameterEstimate("cortisol_magnitude_above_baseline", 20, 100, "percent", "measured", "moderate stressors"),
            ],
        ),
        CausalLink(
            from_variable="cortisol_elevation",
            to_variable="metabolic_mobilization",
            activity="cortisol → glucose release, immune modulation, cardiovascular changes",
            from_level=AnalysisLevel.MOLECULAR,
            to_level=AnalysisLevel.SYSTEMS,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Sapolsky, 2004 (~5,000 citations)"],
            parameters=[],
        ),
    ],
    scope_conditions=[
        ScopeCondition("Responds to perceived not objective threat", "Cultural/individual variation in threat appraisal is large"),
        ScopeCondition("Chronic vs acute produce different dynamics", "Chronic → allostatic load, flattened cortisol curve"),
    ],
    moderators=[
        Moderator("familiarity", "decreases", "Familiar environments reduce amygdala reactivity via reduced PE"),
        Moderator("social_presence", "decreases", "Social buffering of HPA axis"),
        Moderator("perceived_control", "decreases", "Controllability reduces cortisol 15-30% (Dickerson & Kemeny 2004)"),
        Moderator("prior_trauma", "increases", "Sensitized amygdala reactivity"),
    ],
    interactions=[
        TemplateInteraction("PP_SPECTRAL_MATCH_001", "prediction_error_magnitude", "feeds_into",
                           "Lower PE from familiar environments reduces amygdala drive"),
        TemplateInteraction("NM_CORTISOL_HIPPOCAMPAL_005", "cortisol_level", "feeds_into",
                           "Chronic cortisol from this template damages hippocampus"),
        TemplateInteraction("IC_INTEROCEPTIVE_AFFECT_001", "body_state_changes", "feeds_into",
                           "Cortisol-driven body changes become interoceptive signals → affect construction"),
    ],
    overall_maturity=MaturityLevel.HOW_ACTUALLY,
    key_references=[
        "LeDoux (1996) cited ~15,000",
        "McEwen (2007) cited ~5,500",
        "Ulrich-Lai & Herman (2009) cited ~2,000",
        "Ohman & Mineka (2001) cited ~3,000",
    ],
)
```

## Seed Template 2: SN_LAYOUT_COGNITIVE_MAP_001 (T3)
**Chosen because**: how-actually, core spatial navigation, central to architecture

```python
T3_SN_LAYOUT_COGNITIVE_MAP_001 = MechanisticTemplate(
    template_id="SN_LAYOUT_COGNITIVE_MAP_001",
    name="Spatial layout → cognitive map formation quality",
    structural_pattern="environmental_structure → neural_representation_quality → downstream_cognitive_effects",
    higher_order_principle=None,
    transferable_to=["virtual environments", "narrative structure (metaphorical spatial mapping)"],
    framework_ids=["SN"],
    causal_links=[
        CausalLink(
            from_variable="spatial_layout_properties",  # AUDIT-CHECK
            to_variable="hippocampal_entorhinal_sampling",
            activity="architectural layout (paths, nodes, landmarks, vistas, boundaries) → exploration → hippocampal sampling",
            from_level=AnalysisLevel.ECOLOGICAL,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "O'Keefe & Nadel, 1978 (~10,000 citations)",
                "Moser et al., 2008 (~3,000 citations)",
            ],
            parameters=[],
        ),
        CausalLink(
            from_variable="layout_properties_regularity_hierarchy_landmarks",
            to_variable="cognitive_map_quality",
            activity="layout regularity, hierarchy, landmark distinctiveness → place cell stability + grid cell coherence",
            from_level=AnalysisLevel.CIRCUIT,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "Hafting et al., 2005 (~5,000 citations)",
                "Krupic et al., 2015 (~?)",
            ],
            parameters=[
                ParameterEstimate("place_field_stability_well_structured", 0.7, 0.9, "correlation_r", "measured", "rodent literature"),
                ParameterEstimate("place_field_stability_complex_irregular", 0.3, 0.5, "correlation_r", "measured", "rodent literature"),
            ],
        ),
        CausalLink(
            from_variable="cognitive_map_quality",
            to_variable="wayfinding_efficiency",
            activity="good cognitive map → efficient wayfinding + reduced spatial anxiety",
            from_level=AnalysisLevel.CIRCUIT,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "Maguire et al., 2000 (~4,500 citations)",
                "Epstein et al., 2017 (~800 citations)",
            ],
            parameters=[],
        ),
    ],
    scope_conditions=[
        ScopeCondition("Requires locomotion through space", "Passive viewing produces weaker maps"),
        ScopeCondition("Map formation takes 5-15 min for moderate complexity", "Brief visits insufficient"),
        ScopeCondition("Requires intact hippocampal function", "Impaired in hippocampal lesion/aging"),
    ],
    moderators=[
        Moderator("stress_cortisol", "decreases", "Cortisol impairs place cell formation (link to T6)"),
        Moderator("familiarity", "increases", "Repeated visits strengthen cognitive map"),
        Moderator("age", "decreases", "Hippocampal decline with aging reduces map quality"),
        Moderator("cognitive_load", "decreases", "Divided attention impairs map formation"),
    ],
    interactions=[
        TemplateInteraction("NM_CORTISOL_HIPPOCAMPAL_005", "hippocampal_function", "modulates",
                           "Chronic cortisol damages hippocampus → worse maps → more stress (vicious cycle)"),
        TemplateInteraction("SN_THETA_SEQUENCE_003", "theta_sequence_coherence", "feeds_into",
                           "Theta sequences build cognitive map during exploration"),
        TemplateInteraction("MS_RIPPLE_REPLAY_002", "place_cell_sequences", "feeds_into",
                           "Exploration sequences become replay content during rest"),
    ],
    overall_maturity=MaturityLevel.HOW_ACTUALLY,
    key_references=[
        "O'Keefe & Nadel (1978) cited ~10,000",
        "Hafting et al. (2005) cited ~5,000",
        "Moser et al. (2008) cited ~3,000",
        "Maguire et al. (2000) cited ~4,500",
        "Epstein et al. (2017) cited ~800",
    ],
)
```

## Seed Template 3: PP_COMPLEXITY_GOLDILOCKS_002 (T2)
**Chosen because**: Central to Goldilocks framework, domain-general, links to India fieldwork

```python
T2_PP_COMPLEXITY_GOLDILOCKS_002 = MechanisticTemplate(
    template_id="PP_COMPLEXITY_GOLDILOCKS_002",
    name="Stimulus complexity → inverted-U hedonic response",
    structural_pattern="stimulus_dimension → optimization_zone → hedonic_evaluation",
    higher_order_principle="Goldilocks optimization: moderate PE is rewarding; too little boring; too much aversive",
    transferable_to=[
        "visual complexity", "auditory complexity", "spatial complexity",
        "social density", "information density", "thermal variation", "olfactory complexity",
    ],
    framework_ids=["PP", "NM"],
    causal_links=[
        CausalLink(
            from_variable="stimulus_complexity",  # AUDIT-CHECK
            to_variable="prediction_error_magnitude",
            activity="complexity on any sensory dimension → prediction error magnitude",
            from_level=AnalysisLevel.ECOLOGICAL,
            to_level=AnalysisLevel.COMPUTATIONAL,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Berlyne, 1971 (~4,500)", "Schmidhuber, 2010 (~1,500)", "Van de Cruys, 2017 (~200)"],
            parameters=[],
        ),
        CausalLink(
            from_variable="prediction_error_magnitude",
            to_variable="precision_weighting_demand",
            activity="PE magnitude → precision-weighting demand → metabolic cost",
            from_level=AnalysisLevel.COMPUTATIONAL,
            to_level=AnalysisLevel.CELLULAR,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=[],
            parameters=[],
        ),
        # Branch: LOW PE
        CausalLink(
            from_variable="low_prediction_error",
            to_variable="boredom_disengagement",
            activity="low PE → low dopaminergic reward signal → boredom",
            from_level=AnalysisLevel.COMPUTATIONAL,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=["Schultz reward prediction error model"],
            parameters=[],
        ),
        # Branch: MODERATE PE
        CausalLink(
            from_variable="moderate_prediction_error",
            to_variable="positive_valence",
            activity="moderate (resolvable) PE → PE reduction over time → positive valence signal → preference",
            from_level=AnalysisLevel.COMPUTATIONAL,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=["Van de Cruys, 2017", "Joffily & Coricelli, 2013 (~400)"],
            parameters=[],
        ),
        # Branch: HIGH PE
        CausalLink(
            from_variable="high_prediction_error",
            to_variable="negative_affect_avoidance",
            activity="high (unresolvable) PE → sustained metabolic demand + NE arousal → negative affect → avoidance",
            from_level=AnalysisLevel.COMPUTATIONAL,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=[],
            parameters=[],
        ),
    ],
    scope_conditions=[
        ScopeCondition("Applies to any dimension processable by generative model", ""),
        ScopeCondition("Requires engaged observer", "Distracted or task-focused observers don't show inverted-U"),
        ScopeCondition("Inverted-U may flatten for unattended dimensions", ""),
    ],
    moderators=[
        Moderator("familiarity", "shifts_curve", "Rightward shift — more familiar observers tolerate higher complexity"),
        Moderator("cultural_visual_ecology", "shifts_curve", "High-density cultures have rightward-shifted curves (Goldilocks India framework)"),
        Moderator("expertise", "shifts_curve", "Architects rightward-shifted vs laypeople for architectural complexity"),
        Moderator("current_arousal", "shifts_curve", "Already-aroused observers have leftward-shifted curves"),
    ],
    interactions=[
        TemplateInteraction("PP_CULTURAL_PRIOR_CALIBRATION_001", "cultural_prior_distribution", "modulates",
                           "Cultural ecology shifts the location of the inverted-U peak"),
        TemplateInteraction("NM_NORADRENERGIC_EXPLORE_006", "norepinephrine_level", "modulates",
                           "LC-NE state modulates threshold for novelty-driven exploration"),
    ],
    overall_maturity=MaturityLevel.HOW_PLAUSIBLY,
    key_references=[
        "Berlyne (1971) cited ~4,500",
        "Schmidhuber (2010) cited ~1,500",
        "Van de Cruys (2017) cited ~200",
        "Joffily & Coricelli (2013) cited ~400",
    ],
)
```

## Seed Template 4: IC_INTEROCEPTIVE_AFFECT_001 (T12)
**Chosen because**: BRIDGE TEMPLATE — connects all body-affecting templates to experience

```python
T12_IC_INTEROCEPTIVE_AFFECT_001 = MechanisticTemplate(
    template_id="IC_INTEROCEPTIVE_AFFECT_001",
    name="Interoceptive prediction error → affect construction",
    structural_pattern="body_state_mismatch → affect_generation → conceptual_categorization",
    higher_order_principle=None,
    transferable_to=["all affective experience (domain-general)"],
    framework_ids=["IC"],
    causal_links=[
        CausalLink(
            from_variable="environmental_body_state_change",  # AUDIT-CHECK
            to_variable="interoceptive_signal_change",
            activity="environmental influences on body (autonomic, postural, metabolic, thermal) → changed interoceptive signals",
            from_level=AnalysisLevel.SYSTEMS,
            to_level=AnalysisLevel.CELLULAR,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Craig, 2009 (~6,000 citations)"],
            parameters=[],
        ),
        CausalLink(
            from_variable="interoceptive_signals",
            to_variable="interoceptive_prediction_error",
            activity="changed signals vs brain's predictions → interoceptive PE → anterior insular cortex",
            from_level=AnalysisLevel.CELLULAR,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Seth, 2013 (~2,500)", "Barrett & Simmons, 2015 (~1,800)"],
            parameters=[],
        ),
        CausalLink(
            from_variable="interoceptive_prediction_error",
            to_variable="constructed_affect",
            activity="interoceptive PE + available conceptual categories → affect construction (emotion, mood, valence/arousal)",
            from_level=AnalysisLevel.CIRCUIT,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=["Barrett, 2017 (~4,000)"],
            parameters=[],
            is_contested=True,
            contested_by="Basic emotion theory predicts discrete circuits firing regardless of conceptual categorization",
        ),
    ],
    scope_conditions=[
        ScopeCondition("Poor interoceptive sensitivity → reduced affect differentiation", "Low interoceptive accuracy = blunted affective response"),
        ScopeCondition("Cross-cultural variation in conceptual categories", "Different emotion vocabularies → different affective experience"),
        ScopeCondition("Alexithymia: intact physiology but impaired categorization", "Clinical dissociation of body response from affect label"),
    ],
    moderators=[
        Moderator("interoceptive_sensitivity", "increases", "Better body awareness → richer affect differentiation"),
        Moderator("emotional_vocabulary", "increases", "More conceptual categories → finer-grained affect"),
        Moderator("cultural_emotion_concepts", "shifts_curve", "Culture-specific emotion categories shape what gets constructed"),
    ],
    interactions=[
        TemplateInteraction("NM_THREAT_HPA_001", "cortisol_body_changes", "feeds_into",
                           "Cortisol-driven body changes become interoceptive input"),
        TemplateInteraction("EC_AFFORDANCE_POSTURAL_001", "postural_autonomic_changes", "feeds_into",
                           "Postural changes → autonomic shifts → interoceptive signals"),
        TemplateInteraction("ALLOSTATIC_MASTER_001", "allostatic_demand", "feeds_into",
                           "All allostatic demands produce body state changes → interoceptive input"),
    ],
    overall_maturity=MaturityLevel.HOW_PLAUSIBLY,
    key_references=[
        "Barrett (2017) cited ~4,000",
        "Seth (2013) cited ~2,500",
        "Craig (2009) cited ~6,000",
        "Barrett & Simmons (2015) cited ~1,800",
    ],
    architectural_prediction="Every template that changes autonomic state, cortisol, postural tone, or metabolic demand connects to this template via interoceptive signals. This is the universal bridge to subjective experience.",
)
```

## Seed Template 5: CHRONO_LIGHT_ENTRAINMENT_001 (T30)
**Chosen because**: Exemplary specification, new framework (CB), practical parameters

```python
T30_CHRONO_LIGHT_ENTRAINMENT_001 = MechanisticTemplate(
    template_id="CHRONO_LIGHT_ENTRAINMENT_001",
    name="Architectural light exposure → circadian entrainment quality → physiological coordination",
    structural_pattern="light_input → clock_synchronization → systemic_coordination",
    higher_order_principle="SCN coordinates all physiological rhythms to 24h cycle; buildings mediate most light exposure for indoor populations",
    transferable_to=["workspace scheduling", "hospital ward design", "school design", "urban planning"],
    framework_ids=["CB"],
    causal_links=[
        CausalLink(
            from_variable="architectural_light_environment",  # AUDIT-CHECK
            to_variable="retinal_light_input",
            activity="window size, orientation, glazing, electric light spectrum/level/timing → spectral composition, intensity, timing, duration",
            from_level=AnalysisLevel.ECOLOGICAL,
            to_level=AnalysisLevel.CELLULAR,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Boubekri et al., 2014 (~200)"],
            parameters=[],
        ),
        CausalLink(
            from_variable="retinal_light_input",
            to_variable="scn_activation",
            activity="ipRGCs (melanopsin) → retinohypothalamic tract → SCN",
            from_level=AnalysisLevel.CELLULAR,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "Berson, Dunn, & Takao, 2002 (~2,500)",
                "Hattar et al., 2002 (~2,000)",
                "LeGates, Fernandez, & Hattar, 2014 (~1,500)",
            ],
            parameters=[
                ParameterEstimate("iprgc_peak_sensitivity", 480, 480, "nm", "measured", "Berson 2002"),
                ParameterEstimate("circadian_entrainment_threshold", 100, 200, "lux_at_cornea", "measured", "Czeisler 1999"),
                ParameterEstimate("bright_light_effective_dose", 1000, None, "lux", "measured", "phase shifting literature"),
            ],
        ),
        CausalLink(
            from_variable="scn_activation_pattern",
            to_variable="circadian_coordination",
            activity="SCN → melatonin rhythm + cortisol rhythm + temperature rhythm + immune cycling",
            from_level=AnalysisLevel.CIRCUIT,
            to_level=AnalysisLevel.SYSTEMS,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Czeisler et al., 1999 (~2,500)", "Roenneberg & Merrow, 2016 (~1,000)"],
            parameters=[],
        ),
        CausalLink(
            from_variable="circadian_coordination",
            to_variable="optimal_physiological_function",
            activity="well-synchronized → optimal cognitive performance, immune function, metabolic regulation, mood",
            from_level=AnalysisLevel.SYSTEMS,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Walker, 2017 (~2,000)"],
            parameters=[],
        ),
    ],
    scope_conditions=[
        ScopeCondition("Requires adequate light reaching the retina", "Cataracts, small pupils, dark sunglasses reduce input"),
        ScopeCondition("Timing matters more than dose", "Morning light advances phase; evening light delays"),
        ScopeCondition("Spectrum matters", "Blue-enriched (480nm) most effective; incandescent (warm) weaker"),
    ],
    moderators=[
        Moderator("age", "decreases", "Lens yellowing reduces blue light transmission; 70yr olds get ~50% of 20yr olds' circadian input"),
        Moderator("screen_exposure_evening", "decreases", "Blue light from screens delays melatonin onset"),
        Moderator("latitude", "shifts_curve", "Higher latitudes have greater seasonal light variation"),
        Moderator("chronotype", "shifts_curve", "Morning vs evening types have different phase preferences"),
        Moderator("shift_work", "decreases", "Forced desynchronization between light cycle and activity"),
    ],
    interactions=[
        TemplateInteraction("NM_THREAT_HPA_001", "cortisol_diurnal_rhythm", "modulates",
                           "SCN controls cortisol awakening response; disruption amplifies stress reactivity"),
        TemplateInteraction("ALLOSTATIC_MASTER_001", "circadian_regulation_cost", "feeds_into",
                           "Circadian disruption is an ongoing allostatic demand"),
        TemplateInteraction("MS_RIPPLE_REPLAY_002", "sleep_quality", "modulates",
                           "Circadian disruption → poor sleep → reduced SPW-R replay → impaired consolidation"),
    ],
    overall_maturity=MaturityLevel.HOW_ACTUALLY,
    key_references=[
        "Czeisler et al. (1999) cited ~2,500",
        "LeGates, Fernandez, & Hattar (2014) cited ~1,500",
        "Roenneberg & Merrow (2016) cited ~1,000",
        "Berson, Dunn, & Takao (2002) cited ~2,500",
        "Walker (2017) cited ~2,000",
        "Boubekri et al. (2014) cited ~200",
    ],
)
```

## Seed Template 6: DT_DMN_MAINTENANCE_002 (T27)
**Chosen because**: Exemplary DT specification, DMN subsystem distinction, practical predictions

```python
T27_DT_DMN_MAINTENANCE_002 = MechanisticTemplate(
    template_id="DT_DMN_MAINTENANCE_002",
    name="Low-demand periods → DMN subsystem re-engagement → model maintenance and restoration",
    structural_pattern="demand_reduction → maintenance_opportunity → model_integrity_preservation",
    higher_order_principle="DMN performs essential maintenance suppressed by sustained demands; environments must provide low-demand periods",
    transferable_to=["work scheduling", "educational design", "clinical recovery environments"],
    framework_ids=["DT"],
    causal_links=[
        CausalLink(
            from_variable="low_attentional_demand_environment",
            to_variable="tpn_deactivation",
            activity="nature view, quiet waiting area, familiar safe space → TPN disengagement",
            from_level=AnalysisLevel.ECOLOGICAL,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Raichle et al., 2001 (~15,000)", "Fox et al., 2005 (~10,000)"],
            parameters=[],
        ),
        CausalLink(
            from_variable="tpn_deactivation",
            to_variable="dmn_reengagement",
            activity="TPN off → DMN anticorrelation release → DMN re-engagement",
            from_level=AnalysisLevel.CIRCUIT,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["robust fMRI finding; onset within seconds of task cessation"],
            parameters=[],
        ),
        CausalLink(
            from_variable="dmn_reengagement",
            to_variable="subsystem_maintenance_operations",
            activity="MTL subsystem → scene construction, spatial model updating, episodic memory, future simulation; dmPFC subsystem → social cognition, theory of mind, self-reference",
            from_level=AnalysisLevel.CIRCUIT,
            to_level=AnalysisLevel.COMPUTATIONAL,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Andrews-Hanna et al., 2010 (~3,500)", "Buckner & DiNicola, 2019 (~1,500)"],
            parameters=[
                ParameterEstimate("mtl_maintenance_onset", 5, 5, "min", "estimated", "fMRI literature"),
                ParameterEstimate("full_dmn_cycling_duration", 15, 20, "min", "estimated", "fMRI literature"),
            ],
        ),
        CausalLink(
            from_variable="subsystem_maintenance",
            to_variable="model_quality_preservation",
            activity="MTL → updated spatial models, consolidated memories; dmPFC → maintained social models, self-concept",
            from_level=AnalysisLevel.COMPUTATIONAL,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=["Hamilton et al., 2015 (~600)"],
            parameters=[],
        ),
    ],
    scope_conditions=[
        ScopeCondition("Requires subjective safety", "Threatening environments maintain TPN even without tasks"),
        ScopeCondition("Individual differences in DMN dynamics", "Meditation practice may enhance DMN switching"),
        ScopeCondition("Applies to neurotypical adult brains", "DMN dynamics differ in ASD, schizophrenia, ADHD"),
    ],
    moderators=[
        Moderator("anxiety", "decreases", "Anxious rumination hijacks DMN for repetitive self-focused processing"),
        Moderator("rest_environment_quality", "increases", "Genuine low-stimulus needed; noisy rest area fails"),
        Moderator("meditation_practice", "increases", "Meditators show faster DMN re-engagement"),
    ],
    interactions=[
        TemplateInteraction("MS_RIPPLE_REPLAY_002", "mtl_subsystem_engagement", "gates",
                           "MTL subsystem engagement overlaps with SPW-R replay conditions"),
        TemplateInteraction("DT_ATTENTIONAL_DEMAND_001", "directed_attention_fatigue", "modulates",
                           "This template is the recovery mechanism for fatigue produced by T4"),
        TemplateInteraction("NM_CHOLINERGIC_GATING_007", "acetylcholine_level", "gates",
                           "Low ACh → DMN + replay; high ACh → TPN + active processing"),
    ],
    overall_maturity=MaturityLevel.HOW_PLAUSIBLY,
    key_references=[
        "Raichle et al. (2001) cited ~15,000",
        "Fox et al. (2005) cited ~10,000",
        "Andrews-Hanna et al. (2010) cited ~3,500",
        "Buckner & DiNicola (2019) cited ~1,500",
        "Hamilton et al. (2015) cited ~600",
    ],
    architectural_prediction="Offices with window views → MTL subsystem → better spatial memory + creativity. Communal rest areas → dmPFC subsystem → better social cohesion vs isolated rest areas.",
)
```

## Seed Template 7: AUD_SCENE_ANALYSIS_001 (T31)
**Chosen because**: Best-parameterized template in library, MSI framework, practical

```python
T31_AUD_SCENE_ANALYSIS_001 = MechanisticTemplate(
    template_id="AUD_SCENE_ANALYSIS_001",
    name="Acoustic environment complexity → auditory scene analysis demand → cognitive resource allocation",
    structural_pattern="sensory_complexity → processing_demand → resource_depletion",
    higher_order_principle=None,
    transferable_to=["any multi-source auditory environment"],
    framework_ids=["PP", "MSI"],
    causal_links=[
        CausalLink(
            from_variable="acoustic_environment_complexity",  # AUDIT-CHECK
            to_variable="asa_parsing_demand",
            activity="multiple concurrent sources → auditory scene analysis demand",
            from_level=AnalysisLevel.ECOLOGICAL,
            to_level=AnalysisLevel.COMPUTATIONAL,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Bregman, 1990 (~8,000)", "McDermott, 2009 (~200)"],
            parameters=[
                ParameterEstimate("asa_source_capacity", 3, 5, "concurrent_sources", "measured", "Bregman 1990"),
                ParameterEstimate("onset_grouping_window", 30, 30, "ms", "measured", "Bregman 1990"),
                ParameterEstimate("frequency_segregation_threshold", 1, 1, "semitone", "measured", "Bregman 1990"),
                ParameterEstimate("spatial_segregation_threshold", 15, 15, "degrees_azimuth", "measured", "psychoacoustic literature"),
            ],
        ),
        CausalLink(
            from_variable="asa_parsing_demand",
            to_variable="cortical_processing_load",
            activity="ASA demand → bilateral STG, planum temporale, IPS recruitment",
            from_level=AnalysisLevel.COMPUTATIONAL,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["fMRI studies of auditory attention"],
            parameters=[
                ParameterEstimate("bold_increase_per_source", 5, 5, "percent", "measured", "fMRI auditory cortex"),
            ],
        ),
        CausalLink(
            from_variable="cortical_processing_load",
            to_variable="cognitive_capacity_reduction",
            activity="high ASA demand → diverted attention → reduced capacity for concurrent tasks",
            from_level=AnalysisLevel.CIRCUIT,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Szalma & Hancock, 2011 (~500)"],
            parameters=[
                ParameterEstimate("speech_in_noise_95pct_correct", 15, 15, "dB_SNR", "measured", "psychoacoustics"),
                ParameterEstimate("speech_in_noise_50pct_correct", 0, 0, "dB_SNR", "measured", "psychoacoustics"),
                ParameterEstimate("wm_degradation_in_60dBA", 10, 20, "percent", "measured", "Szalma & Hancock 2011"),
                ParameterEstimate("complex_task_degradation_per_10dB", 5, 15, "percent", "measured", "Szalma & Hancock 2011"),
            ],
        ),
    ],
    scope_conditions=[
        ScopeCondition("Steady-state noise less disruptive than fluctuating", "HVAC hum < speech at same dB"),
        ScopeCondition("Meaningful irrelevant speech is maximally disruptive", "Irrelevant speech effect"),
        ScopeCondition("Familiar/predictable patterns less disruptive", "Connects to PP — auditory PE"),
    ],
    moderators=[
        Moderator("introversion", "increases", "Introverts ~2x more affected by noise"),
        Moderator("sensory_processing_sensitivity", "increases", "HSP amplifies all effects ~1.5-2x"),
        Moderator("auditory_processing_disorder", "increases", "APD ~2x more affected"),
        Moderator("age", "increases", "Older adults: declining ASA capacity"),
    ],
    interactions=[
        TemplateInteraction("HC_WORKING_MEMORY_LOAD_001", "cognitive_resource_depletion", "feeds_into",
                           "ASA demand competes for WM resources"),
        TemplateInteraction("DT_ATTENTIONAL_DEMAND_001", "sustained_attention_demand", "feeds_into",
                           "Chronic noise monitoring suppresses DMN"),
    ],
    overall_maturity=MaturityLevel.HOW_ACTUALLY,
    key_references=[
        "Bregman (1990) cited ~8,000",
        "McDermott (2009) cited ~200",
        "Szalma & Hancock (2011) cited ~500",
        "Jones & Macken (1993) cited ~300",
    ],
)
```

## Seed Template 8: PP_CULTURAL_PRIOR_CALIBRATION_001 (T15)
**Chosen because**: how-possibly, central to India fieldwork, shows speculative template structure

```python
T15_PP_CULTURAL_PRIOR_CALIBRATION_001 = MechanisticTemplate(
    template_id="PP_CULTURAL_PRIOR_CALIBRATION_001",
    name="Cultural visual ecology → generative model calibration → preference set-points",
    structural_pattern="developmental_exposure → model_calibration → shifted_optimization_zone",
    higher_order_principle="Goldilocks framework for cross-cultural variation: inverted-U same shape but SHIFTED along stimulus dimension by cultural experience",
    transferable_to=[
        "auditory complexity (music)", "olfactory complexity (spice tolerance)",
        "thermal comfort range", "social density tolerance",
    ],
    framework_ids=["PP"],
    causal_links=[
        CausalLink(
            from_variable="cultural_visual_ecology_density",  # AUDIT-CHECK
            to_variable="generative_model_calibration",
            activity="developmental + ongoing exposure to cultural visual environment → statistical learning in visual generative model",
            from_level=AnalysisLevel.ECOLOGICAL,
            to_level=AnalysisLevel.COMPUTATIONAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=["theoretical derivation from PP + statistical learning; cross-cultural application is novel"],
            parameters=[],
        ),
        CausalLink(
            from_variable="calibrated_generative_model",
            to_variable="shifted_prediction_error_function",
            activity="calibrated model → shifted PE function (moderate PE in Culture A = low PE in Culture B if B has higher baseline density)",
            from_level=AnalysisLevel.COMPUTATIONAL,
            to_level=AnalysisLevel.COMPUTATIONAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_POSSIBLY,
            key_evidence=["central theoretical claim of Goldilocks cultural framework; not directly tested"],
            parameters=[],
        ),
        CausalLink(
            from_variable="shifted_pe_function",
            to_variable="shifted_complexity_preference",
            activity="shifted PE → shifted optimal complexity → Culture B prefers higher complexity than Culture A",
            from_level=AnalysisLevel.COMPUTATIONAL,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_POSSIBLY,
            key_evidence=["forthcoming India fieldwork program"],
            parameters=[],
        ),
    ],
    scope_conditions=[
        ScopeCondition("Applies to any sensory dimension with systematic cultural variation", ""),
        ScopeCondition("Developmental sensitive period likely strongest in childhood", "But ongoing calibration throughout life"),
        ScopeCondition("Most speculative template in initial library", "Generates specific testable predictions"),
    ],
    moderators=[
        Moderator("developmental_vs_adult_exposure", "shifts_curve", "Childhood visual ecology produces stronger calibration than adult relocation"),
        Moderator("urban_vs_rural_within_culture", "shifts_curve", "Urban environments within India more dense than rural"),
        Moderator("sensory_modality", "shifts_curve", "Calibration may differ across modalities — visual vs auditory vs olfactory"),
    ],
    interactions=[
        TemplateInteraction("PP_COMPLEXITY_GOLDILOCKS_002", "inverted_u_peak_location", "modulates",
                           "This template SHIFTS the peak of the Goldilocks curve from T2"),
    ],
    overall_maturity=MaturityLevel.HOW_POSSIBLY,
    key_references=[
        "Clark (2013) cited ~5,500",
        "Friston (2010) cited ~8,000",
        "India fieldwork program (forthcoming)",
    ],
    architectural_prediction="Indian sensory set-points are elevated across modalities — not cultural 'preference' but calibrated generative model that processes higher intensity as moderate rather than overwhelming.",
)
```

---

# SECTION 4: IMPLEMENTATION NOTES FOR CLAUDE CODE

## What To Do With This Document

1. **Sprint 7, Task 7.3 (Tier1Framework model)**: Use the TIER1_FRAMEWORKS dict in Section 1. Each entry becomes a `Tier1Framework` database record. The `owned_variables` lists become the variable registry seeds.

2. **Sprint 7, Task 7.4 (Independence matrix)**: Use INDEPENDENCE_MATRIX in Section 2 directly. Store as a symmetric matrix table or JSON blob. The usage rules (≥0.7, 0.4-0.7, <0.4) should be constants in the convergence assessment code.

3. **Sprint 7, Task 7.5 (MechanisticTemplate + CausalLink)**: The dataclass definitions in Section 3 preamble define the schema. The 8 seed templates define the first data. All 40 templates will follow this format.

4. **Variable names marked AUDIT-CHECK**: These are provisional. After the audit returns, reconcile with existing codebase variable names. If conflicts, prefer whatever is already in the database schema.

5. **Branching causal chains** (T2 Goldilocks): The current CausalLink model is a linear chain. T2 has a branching structure (low/mod/high PE go to different outcomes). CC should implement this as a `branch_condition` field on CausalLink or as separate sub-chains. This is a design decision CC can make.

6. **Composed templates** (T13, T14, T20): These reference other templates by ID. The `component_template_ids` field handles this. Composed templates should be flagged `is_composed=True` and their "links" should reference base templates rather than duplicating mechanism.

## Remaining Templates (32 more)

The 8 seeds cover: PP (T2, T15), SN (T3), DT (T27), NM (T5), IC (T12), CB (T30), MSI/PP (T31). Missing framework coverage: DP, MS, EC.

**Priority for next batch**:
- T9 (DP_IMPLICIT_EVALUATION_001) — covers Dual-Process
- T25 (MS_RIPPLE_REPLAY_002) — covers Memory Systems
- T8 (EC_AFFORDANCE_POSTURAL_001) — covers Embodied Cognition
- T29 (ALLOSTATIC_MASTER_001) — the master integrating template

These 4 + the 8 seeds = 12 templates covering all 10 frameworks. Then CC can extend to all 40 by following the pattern.
