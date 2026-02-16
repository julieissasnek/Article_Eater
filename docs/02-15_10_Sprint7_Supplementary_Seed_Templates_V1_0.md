# SPRINT 7 THEORY ARTIFACTS: Supplementary Seed Templates
## Article Eater — Opus-Side Deliverable
## Version 1.0 — February 15, 2026

**Purpose**: Completes the seed template set from document 07. These 4 templates
cover the 3 missing frameworks (DP, MS, EC) plus the master integrating template.

Combined with the 8 seeds in document 07, CC now has 12 templates covering
all 10 Tier 1 frameworks. Remaining 28 templates follow the same pattern.

**Uses the same dataclass definitions from document 07 Section 3.**

---

## Seed Template 9: DP_IMPLICIT_EVALUATION_001 (T9)
**Chosen because**: Covers Dual-Process framework, how-plausibly, contested link

```python
T9_DP_IMPLICIT_EVALUATION_001 = MechanisticTemplate(
    template_id="DP_IMPLICIT_EVALUATION_001",
    name="Environmental features → rapid implicit evaluation → affective response",
    structural_pattern="stimulus → fast_automatic_processing → default_evaluation",
    higher_order_principle=None,
    transferable_to=["faces", "products", "foods", "any stimulus domain"],
    framework_ids=["DP"],
    causal_links=[
        CausalLink(
            from_variable="environmental_lsf_features",
            to_variable="subcortical_visual_processing",
            activity="environmental features (LSF content, color temperature, enclosure, naturalness) → magnocellular pathway → superior colliculus → amygdala + basal ganglia",
            from_level=AnalysisLevel.ECOLOGICAL,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "Bar, Neta, & Linz (2006) cited ~1,500",
                "Vuilleumier et al. (2003)",
            ],
            parameters=[
                ParameterEstimate("processing_onset", 80, 120, "ms", "measured", "Bar et al. 2006"),
            ],
        ),
        CausalLink(
            from_variable="subcortical_evaluation",
            to_variable="implicit_affective_tag",
            activity="subcortical evaluation → implicit affective tag (positive/negative/neutral approach/avoid tendency)",
            from_level=AnalysisLevel.CIRCUIT,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=[
                "Multiple implicit measures converge: IAT, AMP, ERP early components",
            ],
            parameters=[],
        ),
        CausalLink(
            from_variable="implicit_affective_tag",
            to_variable="explicit_evaluation_influence",
            activity="implicit tag influences subsequent explicit evaluation (either ratified or overridden)",
            from_level=AnalysisLevel.PSYCHOLOGICAL,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=[
                "Evans & Stanovich (2013) cited ~3,500",
                "Melnikoff & Bargh (2018)",
            ],
            parameters=[],
            is_contested=True,
            contested_by="Timing and conditions of explicit override are debated; dual-process models agree on principle but disagree on boundary conditions",
        ),
    ],
    scope_conditions=[
        ScopeCondition("Most influential for first encounters and brief exposures (<2s)", "Extended exposure allows explicit override"),
        ScopeCondition("Individual differences in need-for-cognition moderate balance", "High NFC people override implicit more often"),
        ScopeCondition("Cultural familiarity with architectural styles affects which features trigger positive vs negative", "Cross-cultural variation in implicit response"),
    ],
    moderators=[
        Moderator("exposure_duration", "decreases", "Longer exposure → more explicit override of implicit tag"),
        Moderator("need_for_cognition", "decreases", "High NFC individuals rely less on implicit evaluation"),
        Moderator("cultural_familiarity", "shifts_curve", "Familiar architectural styles trigger more positive implicit tags"),
        Moderator("current_emotional_state", "shifts_curve", "Anxious observers generate more negative implicit tags from ambiguous input"),
    ],
    interactions=[
        TemplateInteraction("PP_RAPID_GIST_004", "lsf_content", "feeds_into",
                           "Rapid gist extraction provides the input for implicit evaluation"),
        TemplateInteraction("NM_THREAT_HPA_001", "amygdala_activation", "feeds_into",
                           "Threat-related implicit tags trigger amygdala via same magnocellular pathway"),
        TemplateInteraction("IC_INTEROCEPTIVE_AFFECT_001", "interoceptive_signals", "feeds_into",
                           "Implicit evaluation is partly constructed from interoceptive signals"),
    ],
    overall_maturity=MaturityLevel.HOW_PLAUSIBLY,
    key_references=[
        "Bar, Neta, & Linz (2006) cited ~1,500",
        "Evans & Stanovich (2013) cited ~3,500",
        "Kahneman (2011) cited ~60,000",
    ],
    architectural_prediction="Implicit-explicit discrepancy (saying you like a space while your body says otherwise) is itself a measurable and theoretically important variable.",
)
```

---

## Seed Template 10: MS_RIPPLE_REPLAY_002 (T25)
**Chosen because**: Covers Memory Systems framework, how-actually, exemplary spec

```python
T25_MS_RIPPLE_REPLAY_002 = MechanisticTemplate(
    template_id="MS_RIPPLE_REPLAY_002",
    name="Environmental rest opportunities → sharp-wave ripple replay → spatial knowledge consolidation",
    structural_pattern="low_demand_pause → replay_opportunity → memory_consolidation",
    higher_order_principle="The hippocampus consolidates spatial experiences during quiet wakefulness via SPW-Rs. Architectural rest opportunities enable the neural mechanism for learning the building.",
    transferable_to=["skill consolidation during practice breaks", "conceptual learning during rest periods"],
    framework_ids=["MS"],
    causal_links=[
        CausalLink(
            from_variable="rest_affording_environmental_features",
            to_variable="behavioral_state_transition",
            activity="benches, alcoves, courtyards, window seats, waiting areas with views → transition from active exploration to quiet wakefulness",
            from_level=AnalysisLevel.ECOLOGICAL,
            to_level=AnalysisLevel.BEHAVIORAL,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["environmental psychology literature on rest affordances"],
            parameters=[],
        ),
        CausalLink(
            from_variable="quiet_wakefulness",
            to_variable="hippocampal_state_transition",
            activity="quiet wakefulness → hippocampal transition from theta (exploration) to LIA with intermittent SPW-Rs",
            from_level=AnalysisLevel.BEHAVIORAL,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=["Buzsaki (2015)"],
            parameters=[
                ParameterEstimate("spwr_frequency", 0.5, 2.0, "Hz", "measured", "Buzsaki 2015"),
                ParameterEstimate("spwr_event_duration", 50, 120, "ms", "measured", "Buzsaki 2015"),
                ParameterEstimate("experience_compression_ratio", None, None, "300ms-1s compressed to ~50ms", "measured", "Foster & Wilson 2006"),
            ],
        ),
        CausalLink(
            from_variable="spwr_events",
            to_variable="place_cell_sequence_reactivation",
            activity="SPW-Rs replay compressed versions of recent spatial experience → reactivation of place cell sequences from recent navigation",
            from_level=AnalysisLevel.CIRCUIT,
            to_level=AnalysisLevel.CIRCUIT,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "Lee & Wilson (2002)",
                "Foster & Wilson (2006)",
                "Huszar et al. (2024)",
            ],
            parameters=[],
        ),
        CausalLink(
            from_variable="replayed_sequences",
            to_variable="hippocampal_neocortical_consolidation",
            activity="replayed sequences → hippocampal-neocortical dialogue → consolidation of spatial knowledge in neocortex",
            from_level=AnalysisLevel.CIRCUIT,
            to_level=AnalysisLevel.SYSTEMS,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "Girardeau et al. (2009) — SPW-R disruption impairs consolidation",
                "Khodagholy, Gelinas, & Buzsaki (2017) — cortical ripples coordinate with hippocampal",
            ],
            parameters=[],
        ),
        CausalLink(
            from_variable="consolidated_spatial_knowledge",
            to_variable="improved_subsequent_wayfinding",
            activity="consolidated knowledge → improved wayfinding on subsequent visits → reduced navigational stress and cognitive load",
            from_level=AnalysisLevel.SYSTEMS,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=["established that consolidation improves spatial memory; architectural application is a derivation"],
            parameters=[],
        ),
    ],
    scope_conditions=[
        ScopeCondition("Requires genuine quiet wakefulness, not sleep", "Sleep consolidation uses similar but distinct mechanism"),
        ScopeCondition("Minimum rest duration matters", "SPW-Rs begin within seconds but cumulative replay benefit requires minutes"),
        ScopeCondition("Replay is of RECENT experience", "SPW-Rs preferentially replay trajectories from the last ~30 min of exploration"),
        ScopeCondition("Replay content biased toward rewarded and novel trajectories", "Emotional/motivational significance modulates replay probability"),
    ],
    moderators=[
        Moderator("rest_quality", "increases", "Genuine low-demand rest > mere sitting in noisy environment"),
        Moderator("prior_exploration_richness", "increases", "Richer exploration → more material for replay → better consolidation"),
        Moderator("acetylcholine_level", "gates", "ACh must be LOW for SPW-Rs to occur; high ACh (active exploration, caffeine) suppresses replay"),
        Moderator("sleep_deprivation", "decreases", "Sleep deprivation impairs SPW-R generation"),
    ],
    interactions=[
        TemplateInteraction("NM_CHOLINERGIC_GATING_007", "acetylcholine_level", "gates",
                           "CRITICAL gating: ACh ON = exploration/learning; ACh OFF = replay/consolidation. Mutually exclusive."),
        TemplateInteraction("SN_THETA_SEQUENCE_003", "theta_sequences", "feeds_into",
                           "Theta sequences during exploration are the raw material that SPW-Rs later replay"),
        TemplateInteraction("DT_DMN_MAINTENANCE_002", "dmn_mtl_subsystem", "gates",
                           "MTL subsystem engagement overlaps with SPW-R replay conditions"),
        TemplateInteraction("SN_LAYOUT_COGNITIVE_MAP_001", "cognitive_map_quality", "feeds_into",
                           "Replay consolidates the cognitive map built during exploration"),
    ],
    overall_maturity=MaturityLevel.HOW_ACTUALLY,
    key_references=[
        "Lee & Wilson (2002)",
        "Foster & Wilson (2006)",
        "Girardeau et al. (2009)",
        "Buzsaki (2015)",
        "Khodagholy, Gelinas, & Buzsaki (2017)",
        "Huszar et al. (2024)",
    ],
    architectural_prediction="Rest spaces are not luxury — they are the architectural enablement of neural consolidation. A hospital with benches at corridor intersections will produce patients who learn the building faster than one without rest points, because rest enables SPW-R replay of navigation experience.",
)
```

---

## Seed Template 11: EC_AFFORDANCE_POSTURAL_001 (T8)
**Chosen because**: Covers Embodied Cognition framework, connects body to affect via IC bridge

```python
T8_EC_AFFORDANCE_POSTURAL_001 = MechanisticTemplate(
    template_id="EC_AFFORDANCE_POSTURAL_001",
    name="Architectural affordances → postural adjustment → autonomic state",
    structural_pattern="environmental_structure → body_response → physiological_regulation",
    higher_order_principle=None,
    transferable_to=["any environment affording or constraining movement"],
    framework_ids=["EC"],
    causal_links=[
        CausalLink(
            from_variable="architectural_spatial_features",
            to_variable="perceived_affordances",
            activity="ceiling height, enclosure level, floor surface, passage width → perceived affordances for movement",
            from_level=AnalysisLevel.ECOLOGICAL,
            to_level=AnalysisLevel.COMPUTATIONAL,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "Gibson (1979) cited ~35,000",
                "Warren (1984) cited ~800",
            ],
            parameters=[],
        ),
        CausalLink(
            from_variable="perceived_affordances",
            to_variable="postural_motor_preparation",
            activity="perceived affordances → postural motor preparation (muscle tension, stance width, head orientation, breathing pattern)",
            from_level=AnalysisLevel.COMPUTATIONAL,
            to_level=AnalysisLevel.BEHAVIORAL,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "Stoffregen (2003)",
                "Mark (1987)",
            ],
            parameters=[],
        ),
        CausalLink(
            from_variable="postural_state",
            to_variable="vagal_tone_modulation",
            activity="postural state → vagal tone modulation → autonomic state (sympathetic/parasympathetic balance)",
            from_level=AnalysisLevel.BEHAVIORAL,
            to_level=AnalysisLevel.SYSTEMS,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=[
                "Porges (2007) cited ~3,000 — polyvagal theory; specific architectural application less established",
            ],
            parameters=[
                ParameterEstimate("postural_effect_on_hrv", 0.3, 0.5, "cohens_d", "estimated", "postural physiology literature"),
            ],
        ),
    ],
    scope_conditions=[
        ScopeCondition("Requires physical presence in space", "Not applicable to images or VR without proprioceptive feedback — important methodological implication"),
        ScopeCondition("Stronger in environments that constrain or expand movement range", "Moderate/neutral spaces produce weaker effects"),
    ],
    moderators=[
        Moderator("body_awareness", "increases", "Individuals with high body awareness show stronger postural-autonomic coupling"),
        Moderator("physical_mobility", "decreases", "Wheelchair users or mobility-impaired individuals show different postural-affordance coupling"),
        Moderator("prior_experience", "shifts_curve", "Dancers, athletes may show different postural responses to same affordances"),
    ],
    interactions=[
        TemplateInteraction("IC_INTEROCEPTIVE_AFFECT_001", "autonomic_state_change", "feeds_into",
                           "Postural → vagal → autonomic change → interoceptive signals → affect construction. This is the EC→IC bridge."),
        TemplateInteraction("PP_ACTIVE_INFERENCE_003", "action_policy_space", "feeds_into",
                           "Affordances = prediction-error-reducing action policies in active inference framing"),
        TemplateInteraction("ALLOSTATIC_MASTER_001", "postural_regulation_cost", "feeds_into",
                           "Constrained postures have allostatic cost; relaxed postures reduce it"),
    ],
    overall_maturity=MaturityLevel.HOW_PLAUSIBLY,
    key_references=[
        "Gibson (1979) cited ~35,000",
        "Warren (1984) cited ~800",
        "Porges (2007) cited ~3,000",
        "Meyers-Levy & Zhu (2007) cited ~1,000",
    ],
    architectural_prediction="Ceiling height → vertical posture → feelings of freedom (Meyers-Levy & Zhu, 2007). Narrow passages → contracted posture → elevated sympathetic tone. Open spaces → expanded posture → parasympathetic dominance.",
)
```

---

## Seed Template 12: ALLOSTATIC_MASTER_001 (T29)
**Chosen because**: MASTER TEMPLATE — the integrating framework. All other templates feed into this.

```python
T29_ALLOSTATIC_MASTER_001 = MechanisticTemplate(
    template_id="ALLOSTATIC_MASTER_001",
    name="Cumulative environmental demands → total allostatic cost → resource allocation for function",
    structural_pattern="demand_summation → metabolic_budget_allocation → functional_capacity",
    higher_order_principle="The brain manages a metabolic budget. Every environmental demand draws from this budget. A building's total impact = sum of allostatic demands relative to organism's metabolic capacity.",
    transferable_to=["urban environment assessment", "workplace design evaluation", "hospital design", "school design"],
    framework_ids=["NM", "IC"],  # Cross-framework master
    causal_links=[
        CausalLink(
            from_variable="concurrent_environmental_demands",
            to_variable="total_regulatory_cost",
            activity="Multiple concurrent demands (thermal deviation, acoustic filtering, visual complexity, navigational uncertainty, social regulation, air quality, circadian misalignment) each impose regulatory cost",
            from_level=AnalysisLevel.ECOLOGICAL,
            to_level=AnalysisLevel.SYSTEMS,
            bridging_quality=BridgingQuality.MEDIUM_HIGH,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=[
                "Sterling (2012) cited ~800 — allostatic regulation",
                "McEwen (2007) cited ~5,500 — allostatic load",
            ],
            parameters=[],
        ),
        CausalLink(
            from_variable="total_regulatory_cost",
            to_variable="metabolic_budget_draw",
            activity="sum of regulatory demands → total allostatic cost → draw on metabolic budget",
            from_level=AnalysisLevel.SYSTEMS,
            to_level=AnalysisLevel.SYSTEMS,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=[
                "Sterling (2012)",
                "Key assumption: demands are approximately additive with some interactions",
            ],
            parameters=[],
        ),
        # Branch: SURPLUS (cost < budget)
        CausalLink(
            from_variable="budget_surplus",
            to_variable="resource_allocation_positive",
            activity="surplus resources allocated to: cognitive function (PFC), immune function, social engagement, growth/repair",
            from_level=AnalysisLevel.SYSTEMS,
            to_level=AnalysisLevel.PSYCHOLOGICAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=[],
            parameters=[],
        ),
        # Branch: DEFICIT (cost > budget)
        CausalLink(
            from_variable="budget_deficit",
            to_variable="triage_cascade",
            activity="triage: first sacrificed = immune/growth, then social/creative, last = thermoregulation/cardiovascular",
            from_level=AnalysisLevel.SYSTEMS,
            to_level=AnalysisLevel.CLINICAL,
            bridging_quality=BridgingQuality.MEDIUM,
            maturity=MaturityLevel.HOW_PLAUSIBLY,
            key_evidence=[
                "Sapolsky (2004) cited ~5,000 — triage hierarchy",
                "Hamilton et al. (2015) cited ~600 — social/creative sacrifice",
            ],
            parameters=[],
        ),
        CausalLink(
            from_variable="chronic_allostatic_overload",
            to_variable="health_consequences",
            activity="chronic overload → allostatic load accumulation → cardiovascular disease, metabolic syndrome, immune suppression, cognitive decline, mood disorders",
            from_level=AnalysisLevel.SYSTEMS,
            to_level=AnalysisLevel.CLINICAL,
            bridging_quality=BridgingQuality.HIGH,
            maturity=MaturityLevel.HOW_ACTUALLY,
            key_evidence=[
                "McEwen (2007) cited ~5,500",
                "Juster, McEwen, & Lupien (2010) cited ~1,000",
            ],
            parameters=[],
        ),
    ],
    scope_conditions=[
        ScopeCondition("Population-level template — individual responses vary significantly", "Based on metabolic capacity and concurrent stressors"),
        ScopeCondition("Summation model is an approximation", "Some demand combinations may interact synergistically (noise × thermal > noise + thermal)"),
        ScopeCondition("Requires long-duration exposure (hours to days)", "Brief exposures to demanding environments may be stimulating rather than depleting (hormesis)"),
    ],
    moderators=[
        Moderator("individual_metabolic_capacity", "shifts_curve", "Age, health, fitness, sleep quality, genetics all affect available budget"),
        Moderator("non_architectural_stressors", "decreases", "Work stress, relationship problems, financial anxiety reduce remaining budget"),
        Moderator("adaptive_capacity", "increases", "Regular exposure to moderate demands increases capacity (hormesis)"),
        Moderator("recovery_quality", "increases", "Good sleep, exercise, social support replenish metabolic budget"),
    ],
    interactions=[
        TemplateInteraction("PP_SPECTRAL_MATCH_001", "visual_processing_cost", "feeds_into",
                           "Efficient visual processing reduces allostatic draw"),
        TemplateInteraction("SN_LAYOUT_COGNITIVE_MAP_001", "navigational_cost", "feeds_into",
                           "Good cognitive map reduces navigation demand on budget"),
        TemplateInteraction("DT_ATTENTIONAL_DEMAND_001", "attentional_cost", "feeds_into",
                           "Sustained TPN engagement is a budget draw"),
        TemplateInteraction("NM_THREAT_HPA_001", "threat_cost", "feeds_into",
                           "Cortisol response is a major budget draw"),
        TemplateInteraction("IC_ALLOSTATIC_ANTICIPATION_001", "predictability_savings", "feeds_into",
                           "Predictable environments reduce anticipatory allostatic cost"),
        TemplateInteraction("PP_ACTIVE_INFERENCE_003", "controllability_savings", "feeds_into",
                           "Controllable environments reduce expected cost"),
        TemplateInteraction("EC_COGNITIVE_OFFLOADING_002", "offloading_savings", "feeds_into",
                           "Legible environments reduce cognitive budget draw"),
        TemplateInteraction("CHRONO_LIGHT_ENTRAINMENT_001", "circadian_cost", "feeds_into",
                           "Circadian disruption is an ongoing allostatic demand"),
        TemplateInteraction("AUD_SCENE_ANALYSIS_001", "auditory_processing_cost", "feeds_into",
                           "ASA demand draws from the same metabolic budget"),
    ],
    overall_maturity=MaturityLevel.HOW_PLAUSIBLY,
    key_references=[
        "Sterling (2012) cited ~800",
        "Sterling & Eyer (1988) cited ~2,000",
        "McEwen (2007) cited ~5,500",
        "Juster, McEwen, & Lupien (2010) cited ~1,000",
        "Sapolsky (2004) cited ~5,000",
    ],
    architectural_prediction="A building's allostatic cost can be estimated by: HRV profile of occupants (higher HRV = lower cost), diurnal cortisol variability (flatter slope = higher load), inflammatory markers (CRP, IL-6), and subjective wellbeing. The master template: every other template's effects ultimately cash out here.",
    is_composed=True,
    component_template_ids=[
        "PP_SPECTRAL_MATCH_001",
        "SN_LAYOUT_COGNITIVE_MAP_001",
        "DT_ATTENTIONAL_DEMAND_001",
        "NM_THREAT_HPA_001",
        "IC_ALLOSTATIC_ANTICIPATION_001",
        "PP_ACTIVE_INFERENCE_003",
        "EC_COGNITIVE_OFFLOADING_002",
        "CHRONO_LIGHT_ENTRAINMENT_001",
        "AUD_SCENE_ANALYSIS_001",
    ],
)
```

---

## UPDATED COVERAGE TABLE

| Seed # | Template | Framework(s) Covered | Maturity | Document |
|--------|----------|---------------------|----------|----------|
| 1 | T5 NM_THREAT_HPA_001 | **NM** | how-actually | doc 07 |
| 2 | T3 SN_LAYOUT_COGNITIVE_MAP_001 | **SN** | how-actually | doc 07 |
| 3 | T2 PP_COMPLEXITY_GOLDILOCKS_002 | **PP**, NM | how-plausibly | doc 07 |
| 4 | T12 IC_INTEROCEPTIVE_AFFECT_001 | **IC** | how-plausibly | doc 07 |
| 5 | T30 CHRONO_LIGHT_ENTRAINMENT_001 | **CB** | how-actually | doc 07 |
| 6 | T27 DT_DMN_MAINTENANCE_002 | **DT** | how-plausibly | doc 07 |
| 7 | T31 AUD_SCENE_ANALYSIS_001 | **MSI**, PP | how-actually | doc 07 |
| 8 | T15 PP_CULTURAL_PRIOR_CALIBRATION_001 | PP | how-possibly | doc 07 |
| 9 | T9 DP_IMPLICIT_EVALUATION_001 | **DP** | how-plausibly | **this doc** |
| 10 | T25 MS_RIPPLE_REPLAY_002 | **MS** | how-actually | **this doc** |
| 11 | T8 EC_AFFORDANCE_POSTURAL_001 | **EC** | how-plausibly | **this doc** |
| 12 | T29 ALLOSTATIC_MASTER_001 | NM, IC (master) | how-plausibly | **this doc** |

**All 10 Tier 1 frameworks now have at least one seed template.**

PP: T2, T15 | SN: T3 | DP: T9 | DT: T27 | NM: T5 | IC: T12 | MS: T25 | EC: T8 | CB: T30 | MSI: T31

Plus the master integrating template T29 that connects to all of them.

CC can now implement Sprint 7 Task 7.5 with complete framework coverage. The remaining 28 templates follow the same pattern — CC can encode them mechanically from the panel documents using these 12 as exemplars.
