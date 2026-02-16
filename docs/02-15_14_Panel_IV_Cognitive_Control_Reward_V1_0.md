# PANEL IV: COGNITIVE CONTROL & REWARD
## Article Eater — Expert Panel Discussion
## February 15, 2026 — Document 14

---

## Panel Charter

**Primary Question**: Should Cognitive Control / Executive Function (CC/EF) be promoted to Tier 1 Framework #11?

**Secondary Question**: Should Reward/Valuation receive its own dedicated templates, and if so, where should they be housed?

**Methodology**: Simulated expert panel discussion following the project's established method — 6 researchers with complementary expertise discuss until reaching consensus on mechanistic claims, causal chains, parameter ranges, and scope conditions. Each panelist shares knowledge they believe the other experts may not have, producing genuine knowledge exchange rather than parallel monologues.

**Presiding**: Opus (theory architect)

---

## Panelists

| Name | Affiliation | Domain Expertise |
|---|---|---|
| **David Badre** | Brown University | Hierarchical control, rostro-caudal PFC organization |
| **Wolfram Schultz** | University of Cambridge | Reward prediction error, dopaminergic signaling |
| **Nathaniel Daw** | University of Pennsylvania | Model-based vs model-free decision making, RL theory |
| **Todd Braver** | Washington University in St. Louis | Dual mechanisms of cognitive control (proactive vs reactive) |
| **Sabine Kastner** | Princeton University | Attention and thalamic gating |
| **Earl Miller** | MIT | Working memory, prefrontal dynamics, gamma/beta oscillations |

---

## Part 1: Individual Position Statements

### 1.1 David Badre — The Case for Hierarchical Control

The existing template library captures several consequences of cognitive control — attentional demand (T4), working memory load (T36), cognitive load and metabolic cost (T38) — but it treats these as isolated effects rather than as expressions of a unified hierarchical system. The central insight from two decades of neuroimaging and lesion work is that prefrontal cortex is organized along a rostro-caudal gradient of policy abstraction (Badre, 2008; Badre & Nee, 2018). Posterior PFC (premotor regions) handles concrete stimulus-response mappings; mid-lateral PFC handles contextual rules; anterior PFC handles the most abstract, temporally extended task sets.

This matters for architecture because different buildings demand control at different levels of the hierarchy. A well-signed corridor with clear sightlines requires only low-level sensorimotor control. A complex hospital with context-dependent wayfinding rules ("turn left if you're a visitor, right if you're staff") engages mid-level PFC. A research building that requires switching between collaborative and focused modes throughout the day engages the highest levels of abstract task management.

None of the current 10 frameworks captures this hierarchical structure. Predictive Processing (PP) handles surprise but not the policy hierarchy that generates predictions. DMN/TPN Dynamics (DT) captures the toggle between rest and task engagement but not the gradient within TPN. The hierarchy is a distinct computational architecture with its own neural substrate, its own developmental trajectory, and its own failure modes.

**Position**: Promote CC/EF to Tier 1.

### 1.2 Wolfram Schultz — Reward Prediction Error in Naturalistic Environments

The neuromodulatory framework (NM) already houses dopaminergic templates — T5 (cortisol/HPA threat), T6 (serotonergic mood), T7 (noradrenergic arousal), T17 (dopaminergic novelty). But these templates treat dopamine primarily through the lens of novelty seeking and arousal modulation. The reward prediction error (RPE) signal — the phasic dopaminergic response to outcomes that are better or worse than expected — is computationally distinct from tonic dopamine's role in motivational state (Schultz, Dayan, & Montague, 1997).

What the panel may not fully appreciate is how RPE operates in naturalistic environments as opposed to laboratory paradigms. In the lab, rewards are discrete events (juice drops, monetary gains). In architectural experience, rewards are continuous and multidimensional — the view that opens up as you round a corner, the thermal comfort of entering a well-conditioned space, the social reward of encountering a colleague in a well-designed atrium. These produce RPE signals, but they are distributed over time and modulated by expectations that are themselves shaped by the building's legibility.

The critical distinction, drawn from Berridge and Robinson's incentive salience framework (Berridge & Robinson, 2016), is between *wanting* (incentive salience, driven by mesolimbic dopamine) and *liking* (hedonic impact, driven by opioid hotspots in nucleus accumbens and parabrachial nucleus). An architect can design a space that people are drawn to explore (wanting) without it actually being pleasant to inhabit (liking), and vice versa. This distinction is not captured by any current template and has immediate design implications.

**Position**: Do not create a separate Reward framework. Instead, add 2–3 reward-specific templates to NM, because the dopaminergic substrate is already NM territory. But these templates must formalize the RPE computation and the wanting/liking dissociation, not merely extend existing arousal concepts.

### 1.3 Nathaniel Daw — Model-Based vs Model-Free Arbitration

The deepest connection between cognitive control and architectural experience runs through the distinction between model-based and model-free behavioral strategies (Daw et al., 2005; Daw et al., 2011). When you navigate a familiar building, you rely largely on model-free habitual routes — cached stimulus-response chains that are computationally cheap but inflexible. When the building is novel, or when your usual route is blocked, you switch to model-based planning using your cognitive map (the hippocampal system formalized in T3).

This arbitration is itself a form of cognitive control, and the factors that govern it are well understood: model-based control dominates when stakes are high, when the environment is volatile, and when cognitive resources are available. Model-free control dominates when the task is familiar, when cognitive load is high, and when speed matters. The arbitration is implemented in prefrontal-striatal circuits (Lee et al., 2014) that are distinct from both the habitual system (dorsolateral striatum) and the planning system (hippocampus/ventromedial PFC).

For the Article Eater project, the key question is whether this arbitration mechanism is already captured by the interaction between Spatial Navigation (SN, T3 cognitive map) and Dual-Process Evaluation (DP, T9 implicit evaluation, T37 ecological rationality). My concern is that it is partially but not fully captured. T37 addresses ecological rationality — when heuristics outperform deliberation — but the neural arbitration mechanism is more specific than a general dual-process account. The prefrontal-striatal arbitration circuit has measurable signatures (e.g., BOLD signal in inferior frontal gyrus predicts model-based choice on a trial-by-trial basis) that T37 does not formalize.

**Position**: Agnostic on Tier 1 promotion. The arbitration mechanism needs a template regardless of where it is housed. Could live in SN (since it governs navigation strategy), in DP (since it is a dual-process phenomenon), or in a new CC/EF framework.

### 1.4 Todd Braver — The Dual Mechanisms of Cognitive Control

The Dual Mechanisms of Control (DMC) framework (Braver, 2012) distinguishes proactive control — sustained, anticipatory maintenance of goal-relevant information in lateral PFC — from reactive control — transient, stimulus-driven retrieval of goal information, often mediated by anterior cingulate cortex (ACC) detection of conflict or surprise.

This is the executive function analogue of the Goldilocks principle, and the connection has not been made explicit in the current template library. A highly predictable building (long straight corridors, repetitive layouts) allows users to engage proactive control: they form a plan, maintain it, and execute it with minimal conflict monitoring. This is metabolically efficient — sustained PFC activation is costly but less costly than repeated reactive mobilization. A surprising or illegible building forces reactive control: each decision point triggers conflict detection, ACC engagement, and transient PFC recruitment. The metabolic cost (formalized in T38) is higher per unit time in reactive mode.

The piece I would bring that the other panelists may not emphasize: there are stable individual differences in proactive vs reactive control tendencies, with aging, stress, and psychiatric conditions (particularly schizophrenia and ADHD) shifting the balance toward reactive control (Braver et al., 2007). This means the same building imposes different cognitive control demands on different populations. An environment designed for proactive control (predictable, legible) may be especially beneficial for populations with compromised proactive capacity — the elderly, the stressed, those with attentional disorders. This is a testable prediction with direct design implications.

The critical connection to the existing template library is through T38 (cognitive load / metabolic cost) and the allostatic master template T29. Proactive control has a steady metabolic cost; reactive control has a bursty, higher-peak cost. T29 should be sensitive to this distinction, but currently it is not.

**Position**: Promote CC/EF to Tier 1. The proactive/reactive distinction is a fundamental organizing principle that cuts across multiple existing frameworks and cannot be reduced to any of them.

### 1.5 Sabine Kastner — Thalamic Gating and Environmental Filtering

A mechanism that is conspicuously absent from the entire template library is the role of the thalamus — specifically the pulvinar nucleus — in filtering environmental information before it reaches cortex (Saalmann & Kastner, 2011). The cholinergic gating template (T26) captures acetylcholine's role in modulating the gain of sensory processing, but the thalamic relay is a prior, more fundamental bottleneck.

The pulvinar is the largest nucleus in the human thalamus, and it has reciprocal connections with nearly all of visual cortex, parietal cortex, and prefrontal cortex. It does not merely relay information; it actively filters and coordinates cortical processing. In spatial attention, the pulvinar implements what I would call the "spotlight vs floodlight" distinction — focused attention on a specific spatial location vs distributed monitoring of the broader environment. This distinction maps onto architectural experience in a direct way: navigating a narrow corridor with a specific goal engages spotlight mode; entering a large open atrium engages floodlight mode. The switch between these modes has measurable neural signatures (alpha-band synchronization between pulvinar and cortex) and measurable behavioral consequences (detection speed, peripheral awareness, sense of safety).

Neither the attentional demand template (T4) nor the cholinergic gating template (T26) captures this thalamic mechanism. T4 treats attention as a resource that is depleted by environmental complexity, which is a useful abstraction but misses the qualitative distinction between attention modes. T26 captures neuromodulatory gain control but not the thalamic relay architecture.

**Position**: Whether or not CC/EF is promoted, the thalamic filtering mechanism needs its own template. It could plausibly live in MSI (multisensory integration, since the pulvinar integrates across modalities), in a new CC/EF framework, or as a cross-framework template. I lean toward MSI because the mechanism is more about sensory gating than executive control per se.

### 1.6 Earl Miller — Working Memory Dynamics and Ecological Measurement

Working memory is already represented in T36, but the template treats WM as a static capacity that is loaded by environmental complexity. The recent picture from our lab is more dynamic (Lundqvist et al., 2016; Miller, Lundqvist, & Bastos, 2018). Working memory representations are maintained not by sustained firing (the classical model) but by brief gamma-frequency bursts (~60–100 Hz) that encode content, alternating with beta-frequency bursts (~15–30 Hz) that clear or gate information. WM is better understood as a rhythmic process of writing and clearing, mediated by prefrontal-parietal-thalamic loops.

This matters for architecture because it makes WM load *measurable in ecological settings* via non-invasive EEG or MEG. If a complex building increases the number of gamma bursts per unit time (because more items must be maintained) and decreases the beta-gating efficiency (because the environment keeps injecting new information before old items are consolidated), this should be detectable with mobile EEG. This gives T36 a physiological operationalization that the current template lacks.

The piece I want to bring to discussion is the interaction between WM dynamics and cognitive control more broadly. In our framework, PFC gamma/beta dynamics implement a form of control: beta bursts are the "veto" signal, preventing irrelevant information from entering WM. Environmental designs that constantly intrude on WM (open offices with visual and auditory distractions) reduce beta gating efficiency, leading to more gamma-burst "false starts" and higher metabolic cost. This is a mechanism for the well-documented productivity costs of open-plan offices, and it connects T36 to T38 through a specific neural pathway.

**Position**: I am sympathetic to promoting CC/EF because the gamma/beta dynamics constitute a distinct computational mechanism. However, I acknowledge that these dynamics could also be formalized as extensions to existing templates (T36 in MS, T26 in NM) rather than requiring a new framework. I could be persuaded either way.

---

## Part 2: Panel Discussion

### Thread 1: The Independence Problem

**Opus** (moderating): Before we debate the merits, I need to raise a structural constraint. The CMR pipeline uses an independence matrix to score convergence — when multiple frameworks independently support the same prediction, confidence increases multiplicatively. If we add CC/EF as framework #11, what would its independence scores look like relative to the existing 10?

**Badre**: That is a fair concern. Cognitive control interacts with nearly everything. I would estimate independence with PP at perhaps 0.3 — prediction error is a control signal. With DT, perhaps 0.2 — DMN/TPN dynamics are essentially about control state switching. With DP, maybe 0.3 — dual-process theory is fundamentally about control allocation between System 1 and System 2.

**Braver**: Agreed on those estimates. CB might be 0.7, EC perhaps 0.6. But DT at 0.2 is the real problem. If CC/EF is only 0.2 independent from DT, then any prediction supported by both frameworks gets minimal convergence bonus. It almost argues that CC/EF and DT should be *merged* rather than CC/EF added separately.

**Miller**: I would push back on merging. DT captures the toggle between default mode and task-positive networks — a coarse, binary distinction. Cognitive control is the fine-grained structure *within* the task-positive state. You can be in TPN mode (DT) while exercising very different levels of hierarchical control (CC/EF). They are correlated but not identical.

**Kastner**: The thalamic mechanisms I described operate upstream of both DT and any hypothetical CC/EF. The pulvinar gates information before PFC decides what to do with it. This makes the thalamic template independent of control hierarchy — it is a filtering mechanism, not a decision mechanism.

**Daw**: Let me offer a different framing. The independence matrix scores for CC/EF would average roughly 0.4 across all 10 frameworks. For comparison, what is the average independence for existing frameworks?

**Opus**: The existing 10 range from 0.2 to 0.9, with most pairs in the 0.5–0.7 range. The lowest existing pair is PP–DP at approximately 0.3. The mean across all 45 pairs is roughly 0.55.

**Daw**: So CC/EF at an average of 0.4 would be the least independent framework in the system. That is not disqualifying, but it would degrade the overall discriminability of the convergence scoring.

### Thread 2: Framework vs Meta-Process

**Schultz**: I want to raise a conceptual point that might reframe the entire question. The 10 Tier 1 frameworks each describe a *domain-specific computational system* with its own neural substrate, its own variables, and its own characteristic failure modes. Predictive Processing has prediction error. Spatial Navigation has cognitive maps. Neuromodulation has specific transmitter systems. Each framework answers the question: "What is computed, and by what neural mechanism?"

Cognitive control does not answer that question in the same way. Control is what *coordinates* the other computations. It is more like an operating system than an application. Promoting it to Tier 1 would be a category error — like listing "management" alongside "engineering," "marketing," and "finance" as a department that produces its own product.

**Badre**: With respect, that characterization understates the specificity of the control hierarchy. PFC is not a general-purpose coordinator. It has its own computational architecture — the rostro-caudal abstraction gradient — that makes specific predictions about which brain regions will be engaged by which environmental demands. A hospital wayfinding task engages mid-lateral PFC; abstract workspace planning engages anterior PFC. These are not predictions that fall out of any other framework.

**Braver**: And the proactive/reactive distinction is a specific computational mechanism with its own neural signatures (sustained lateral PFC vs transient ACC), its own metabolic profile, and its own population-level variation. It is not merely "coordination."

**Schultz**: I take the point about specificity. But consider the independence problem Daw raised. If CC/EF's function is to coordinate the other frameworks, then by definition it cannot be independent of them. The low independence scores are not an accident — they reflect the actual nature of cognitive control as a meta-process. And the CMR pipeline specifically depends on high independence for convergence scoring to work.

**Miller**: There may be a middle path. What if we formalize the specific mechanisms — hierarchical control, proactive/reactive switching, gamma/beta gating — as templates that are *cross-framework* rather than owned by a new framework? The allostatic master template (T29) already sets this precedent: it integrates across all frameworks without belonging to any single one. We could create 3–4 "control templates" with the same cross-framework status.

### Thread 3: The Reward Question

**Opus**: Let us turn to the secondary question. Wolfram, you argued for 2–3 reward templates within NM rather than a separate framework. Does the panel agree?

**Schultz**: The case is straightforward. RPE is computed by midbrain dopamine neurons (VTA, substantia nigra). The neuromodulatory framework already owns the dopaminergic system through T17 (dopaminergic novelty). What T17 misses is the *computational* specificity of RPE — the temporal difference learning signal, the distinction between reward magnitude and reward probability, and crucially the wanting/liking dissociation. These should be additional NM templates, not a new framework.

**Daw**: I agree that the dopaminergic substrate belongs in NM. But I want to ensure we formalize the *arbitration* between model-based and model-free systems, because this is where reward interacts with control. When you navigate to the cafeteria in a familiar building, you are executing a model-free habitual policy that was shaped by past reward (the food was good). When the cafeteria moves, you must switch to model-based planning. The arbitration between these strategies is mediated by a prefrontal-striatal circuit that computes the relative reliability of model-based vs model-free predictions.

**Braver**: That arbitration mechanism sounds like it belongs with the control templates rather than the reward templates.

**Daw**: It sits at the intersection. The arbitration uses reward signals (RPE magnitude under each strategy) to decide which strategy to trust. But the *implementation* of the switch is a control operation. I propose it gets its own template that is tagged to both NM (reward input) and the control template set.

**Schultz**: Acceptable. As long as the reward computation itself — the RPE signal, the wanting/liking split — is formalized within NM.

**Kastner**: May I add one observation? The thalamic mechanism I described also interacts with reward. The pulvinar gates visual information preferentially toward rewarded locations. This is a form of reward-guided attention that is neither purely attentional (Kastner territory) nor purely reward-related (Schultz territory). It is implemented by a specific anatomical pathway — the pulvinar-amygdala-PFC loop — that deserves explicit representation.

### Thread 4: Toward Consensus

**Opus**: Let me attempt a synthesis. I am hearing three points of agreement and one remaining disagreement.

**Agreement 1**: Cognitive control mechanisms are insufficiently represented in the current template library. The hierarchical control gradient (Badre), the proactive/reactive distinction (Braver), the gamma/beta WM dynamics (Miller), and the thalamic gating mechanism (Kastner) are all genuine mechanistic contributions that the existing 10 frameworks do not capture.

**Agreement 2**: Reward/Valuation should be formalized within the NM framework through 2–3 new templates, not as a separate Tier 1 framework. The dopaminergic substrate is already NM territory.

**Agreement 3**: The model-based/model-free arbitration (Daw) needs a dedicated template that bridges control and reward.

**Disagreement**: Whether CC/EF should be promoted to Tier 1 #11 (Badre, Braver in favor; Schultz, Kastner, Daw leaning against or agnostic; Miller persuadable either way).

**Badre**: I want to register one more argument for promotion. If we create "cross-framework control templates," they have no home in the independence matrix. They cannot be part of convergence scoring. That means the CMR pipeline will never use control mechanisms to strengthen predictions. Is that acceptable?

**Opus**: That is an important structural point. Cross-framework templates like T29 participate in mechanism tracing (CMR Step 3) but do not contribute independent convergence evidence (CMR Step 5). They compose with other templates but do not multiply confidence.

**Braver**: Which means that if two frameworks independently predict that a predictable environment reduces metabolic cost, and the mechanism in both cases runs through proactive control, the convergence score would not reflect the control mechanism's role. The prediction would be attributed to the two source frameworks, with the control template as a mere intermediary.

**Schultz**: But that accurately reflects the epistemology. If control is a meta-process that coordinates domain-specific computations, then the *evidence* for a prediction comes from the domain-specific studies, not from studies of control per se. A study showing that a legible building reduces cortisol is evidence about the neuromodulatory system, not about cognitive control — even if control is the mediating mechanism.

**Miller**: I am now persuaded by Schultz's argument. The meta-process framing is correct. Control coordinates; it does not independently generate evidence. The cross-framework template approach is epistemically appropriate.

**Badre**: I disagree with the characterization that control merely coordinates. There are studies of PFC patients with specific control deficits who show architectural disorientation that is *not* attributable to spatial navigation deficits, memory deficits, or sensory processing deficits. The control hierarchy generates its own unique predictions. But I acknowledge the independence matrix problem is real, and I can accept the cross-framework compromise if the templates are specified with the same rigor as framework-owned templates.

**Braver**: I will accept the compromise as well, with one condition: we create a formal mechanism for revisiting this decision once the template library is mature enough to empirically test whether control templates contribute independent predictive power.

---

## Part 3: Verdicts

### Verdict 1: CC/EF Tier 1 Promotion

**DECISION: DO NOT PROMOTE.** Cognitive Control / Executive Function will not become Tier 1 Framework #11.

**Rationale** (consensus with noted dissent):

1. *Independence problem*. CC/EF would have an estimated mean independence score of approximately 0.40 across the existing 10 frameworks, with critical pairs as low as 0.2 (DT) and 0.3 (PP, DP). This would be the lowest-independence framework in the system and would degrade convergence scoring in the CMR pipeline.

2. *Category distinction*. The panel majority (4 of 6: Schultz, Daw, Kastner, Miller) concluded that cognitive control is better understood as a meta-process that coordinates domain-specific computations rather than as a parallel domain-specific system. It generates predictions, but these predictions are epistemically grounded in domain-specific evidence, not in independent control-specific evidence.

3. *Pragmatic resolution*. The specific mechanisms identified (hierarchical control, proactive/reactive switching, thalamic gating, gamma/beta dynamics) will be formalized as cross-framework control templates with the same specification rigor as framework-owned templates. These participate in CMR mechanism tracing (Step 3) and composition (Step 4) but do not contribute to convergence scoring (Step 5).

**Dissent**: Badre and Braver maintain that the control hierarchy constitutes a genuinely independent computational architecture with its own unique failure modes and that the cross-framework approach underrepresents control's explanatory power. Both accepted the compromise on pragmatic grounds.

**Review clause**: This decision will be revisited after Sprint 9 when empirical prediction testing could demonstrate whether control templates contribute independent predictive power not captured by existing frameworks.

### Verdict 2: Reward/Valuation

**DECISION: ADD TO NM.** Two new templates (T41, T42) will be added to the Neuromodulatory Systems framework. One cross-framework template (T43) will formalize the model-based/model-free arbitration.

**Rationale** (unanimous):

The dopaminergic substrate of reward computation is already owned by NM. Creating a separate framework would fracture the neuromodulatory system unnecessarily. The new templates must formalize (a) the RPE computation in naturalistic environments and (b) the wanting/liking dissociation.

### Verdict 3: Cross-Framework Control Templates

**DECISION: CREATE FOUR TEMPLATES.** T44–T47, specified below, with cross-framework status equivalent to T29 (allostatic master).

---

## Part 4: New Template Specifications

### T41: NM_REWARD_PREDICTION_ERROR_001

**Framework**: NM (Neuromodulatory Systems)
**Name**: Environmental Reward Prediction Error
**Structural Pattern**: MEDIATION (environment → RPE signal → approach/avoid behavior)
**Higher-Order Principle**: Midbrain dopamine neurons compute the temporal difference between expected and received environmental reward, producing phasic signals that update cached values and guide exploration.

```python
MechanisticTemplate(
    template_id="NM_REWARD_PREDICTION_ERROR_001",
    name="Environmental Reward Prediction Error",
    structural_pattern="MEDIATION",
    higher_order_principle=(
        "Midbrain dopamine neurons compute temporal difference "
        "between expected and received environmental reward; "
        "phasic RPE updates cached place/route values and "
        "modulates exploratory versus exploitative behavior."
    ),
    transferable_to=[
        "wayfinding reward at destination",
        "view reward upon vista opening",
        "thermal comfort upon entering conditioned space",
        "social reward upon encountering others in shared space"
    ],
    framework_ids=["NM"],
    causal_links=[
        CausalLink(
            from_variable="environmental_outcome",
            to_variable="reward_prediction_error",
            activity="compute_temporal_difference",
            from_level="PERSONAL_EPISTEMIC",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Schultz, Dayan, & Montague, 1997",
            parameters={"response_latency_ms": "50-100",
                        "signal_duration_ms": "200-500",
                        "magnitude_range": "±3 SD of baseline firing"}
        ),
        CausalLink(
            from_variable="reward_prediction_error",
            to_variable="cached_place_value",
            activity="update_value_estimate",
            from_level="SUBPERSONAL",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="O'Doherty et al., 2004",
            parameters={"learning_rate_alpha": "0.1-0.4",
                        "discount_factor_gamma": "0.9-0.99"}
        ),
        CausalLink(
            from_variable="cached_place_value",
            to_variable="exploration_exploitation_balance",
            activity="modulate_behavioral_policy",
            from_level="SUBPERSONAL",
            to_level="PERSONAL_EPISTEMIC",
            bridging_quality="MEDIUM",
            maturity="how-plausibly",
            key_evidence="Daw et al., 2006",
            parameters={"softmax_temperature_range": "0.1-5.0"}
        )
    ],
    scope_conditions=[
        "Applies when environmental outcomes deviate from expectation",
        "Requires intact VTA/substantia nigra dopaminergic system",
        "Magnitude scales with unexpectedness, not absolute reward value",
        "Habituates: repeated identical outcomes → RPE → 0"
    ],
    moderators=[
        "prior_expectation_precision (higher precision → larger RPE for violations)",
        "metabolic_state (hunger, thermal discomfort amplify reward signals)",
        "context_novelty (novel environments have less precise priors → smaller RPE)",
        "individual_dopaminergic_tone (genetic/pharmacological variation)"
    ],
    interactions=[
        {"template": "PP_PREDICTION_ERROR_001 (T1)", "type": "SHARED_MECHANISM",
         "description": "Perceptual PE (T1) and reward PE (T41) share the temporal difference computation but operate in different domains — sensory vs motivational. Double dissociation demonstrated in neuroimaging."},
        {"template": "NM_DOPAMINERGIC_NOVELTY_001 (T17)", "type": "EXTENSION",
         "description": "T17 captures tonic dopamine's role in novelty-seeking; T41 captures phasic dopamine's role in outcome evaluation. They are complementary phases of the same neuromodulatory system."},
        {"template": "IC_INTEROCEPTIVE_AFFECT_001 (T12)", "type": "INPUT",
         "description": "Interoceptive signals (thermal comfort, proprioceptive ease) provide the 'received reward' input to the RPE computation."}
    ],
    overall_maturity="how-actually",
    key_references=[
        "Schultz, Dayan, & Montague (1997) Science",
        "O'Doherty et al. (2004) Science",
        "Daw, O'Doherty, Dayan, Seymour, & Dolan (2006) Nature",
        "Berridge & Robinson (2016) American Psychologist"
    ]
)
```

### T42: NM_WANTING_LIKING_DISSOCIATION_001

**Framework**: NM (Neuromodulatory Systems)
**Name**: Architectural Wanting–Liking Dissociation
**Structural Pattern**: DIVERGENCE (environmental stimulus → two separable pathways → distinct behavioral/affective outcomes)
**Higher-Order Principle**: Incentive salience ("wanting," mesolimbic dopamine) and hedonic impact ("liking," mu-opioid hotspots) are neurally and behaviorally dissociable — spaces can attract without satisfying and satisfy without attracting.

```python
MechanisticTemplate(
    template_id="NM_WANTING_LIKING_DISSOCIATION_001",
    name="Architectural Wanting-Liking Dissociation",
    structural_pattern="DIVERGENCE",
    higher_order_principle=(
        "Incentive salience (wanting, mesolimbic DA) and hedonic "
        "impact (liking, opioid hotspots in NAc shell / parabrachial) "
        "are neurally and behaviorally dissociable. Spaces can attract "
        "exploration without producing satisfaction, and produce "
        "satisfaction without attracting approach."
    ),
    transferable_to=[
        "museum exhibit design (curiosity-pull vs dwell satisfaction)",
        "retail environments (browsing drive vs purchase satisfaction)",
        "workspace design (desire to be present vs comfort while present)",
        "urban plazas (attraction from distance vs comfort on arrival)"
    ],
    framework_ids=["NM"],
    causal_links=[
        CausalLink(
            from_variable="environmental_cue_salience",
            to_variable="incentive_salience_wanting",
            activity="attribute_motivational_value",
            from_level="SUBPERSONAL",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Berridge, 2007; Berridge & Robinson, 2016",
            parameters={"substrate": "mesolimbic_DA_VTA_to_NAc",
                        "modulated_by": "prior_deprivation_state"}
        ),
        CausalLink(
            from_variable="environmental_sensory_quality",
            to_variable="hedonic_impact_liking",
            activity="generate_pleasure_response",
            from_level="SUBPERSONAL",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Berridge & Kringelbach, 2015",
            parameters={"substrate": "opioid_hotspots_NAc_shell_parabrachial",
                        "cortical_amplifier": "orbitofrontal_cortex"}
        ),
        CausalLink(
            from_variable="incentive_salience_wanting",
            to_variable="approach_exploration_behavior",
            activity="drive_spatial_approach",
            from_level="SUBPERSONAL",
            to_level="PERSONAL_EPISTEMIC",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Berridge, 2007",
            parameters={}
        ),
        CausalLink(
            from_variable="hedonic_impact_liking",
            to_variable="dwell_time_satisfaction",
            activity="sustain_engagement",
            from_level="SUBPERSONAL",
            to_level="PERSONAL_EPISTEMIC",
            bridging_quality="MEDIUM",
            maturity="how-plausibly",
            key_evidence="Inferred from Berridge framework; direct architectural evidence sparse",
            parameters={"measurable_via": "self_report_pleasure, facial_EMG_zygomaticus"}
        )
    ],
    scope_conditions=[
        "Applies to environments with distinct approach and consummatory phases",
        "Dissociation is most evident when design optimizes one dimension over the other",
        "Wanting pathway is more susceptible to sensitization and contextual cues",
        "Liking pathway is more stable but lower-bandwidth"
    ],
    moderators=[
        "deprivation_state (hunger/thirst/thermal stress amplifies wanting selectively)",
        "prior_sensitization (repeated exposure to rewarding spaces amplifies wanting)",
        "individual_anhedonia (depression blunts liking but may spare wanting)",
        "cultural_aesthetic_priors (trained preferences modulate both pathways)"
    ],
    interactions=[
        {"template": "T41 (RPE)", "type": "COMPLEMENT",
         "description": "T41 computes whether outcome exceeded expectation; T42 dissects the outcome into wanting and liking components. RPE can be positive for wanting (drew you in effectively) but negative for liking (disappointing on arrival)."},
        {"template": "T9 (DP_IMPLICIT_EVALUATION_001)", "type": "INPUT",
         "description": "Implicit evaluation (T9) provides the rapid valence assessment that feeds into the wanting pathway. The dual-process evaluation determines whether approach is initiated."},
        {"template": "T29 (ALLOSTATIC_MASTER_001)", "type": "OUTPUT",
         "description": "Sustained wanting without liking (approaching but not enjoying) has an allostatic cost — the motivational system is engaged without consummatory reward, producing stress."}
    ],
    overall_maturity="how-actually (for neural dissociation); how-plausibly (for architectural applications)",
    key_references=[
        "Berridge (2007) Psychopharmacology",
        "Berridge & Robinson (2016) American Psychologist",
        "Berridge & Kringelbach (2015) Neuron",
        "Pool, Sennwald, Delplanque, Brosch, & Sander (2016) Biological Psychology"
    ]
)
```

### T43: CROSS_MB_MF_ARBITRATION_001

**Frameworks**: SN + DP + NM (cross-framework)
**Name**: Model-Based / Model-Free Navigation Arbitration
**Structural Pattern**: COMPETITION (two parallel systems → arbitration → behavioral output)
**Higher-Order Principle**: Navigation and spatial behavior are governed by competition between a model-based system (hippocampal cognitive map, flexible but metabolically costly) and a model-free system (dorsolateral striatal habits, cheap but inflexible), with a prefrontal-striatal arbitration circuit allocating control based on environmental volatility, stakes, and cognitive resource availability.

```python
MechanisticTemplate(
    template_id="CROSS_MB_MF_ARBITRATION_001",
    name="Model-Based / Model-Free Navigation Arbitration",
    structural_pattern="COMPETITION",
    higher_order_principle=(
        "Spatial behavior alternates between model-based planning "
        "(hippocampal cognitive map, flexible, costly) and model-free "
        "habits (dorsolateral striatum, cheap, inflexible). Prefrontal-"
        "striatal circuit arbitrates based on environmental volatility, "
        "stakes, and available cognitive resources."
    ),
    transferable_to=[
        "hospital wayfinding (habitual staff routes vs novel patient navigation)",
        "campus design (learned desire paths vs intentional circulation)",
        "emergency egress (overlearned exit routes vs novel escape planning)",
        "retail layout changes (disrupting habits to force model-based exploration)"
    ],
    framework_ids=["SN", "DP", "NM"],
    causal_links=[
        CausalLink(
            from_variable="environmental_volatility",
            to_variable="arbitration_signal",
            activity="estimate_relative_reliability",
            from_level="SUBPERSONAL",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Daw et al., 2005; Lee, Shimojo, & O'Doherty, 2014",
            parameters={"arbitration_region": "inferior_frontal_gyrus",
                        "volatility_threshold": "context_dependent"}
        ),
        CausalLink(
            from_variable="arbitration_signal",
            to_variable="navigation_strategy",
            activity="select_behavioral_controller",
            from_level="SUBPERSONAL",
            to_level="PERSONAL_EPISTEMIC",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Daw et al., 2011",
            parameters={"model_based_substrate": "hippocampus_vmPFC",
                        "model_free_substrate": "dorsolateral_striatum",
                        "switch_cost_ms": "200-500"}
        ),
        CausalLink(
            from_variable="cognitive_resource_availability",
            to_variable="arbitration_signal",
            activity="modulate_model_based_weight",
            from_level="SUBPERSONAL",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Otto, Gershman, Markman, & Daw, 2013",
            parameters={"note": "Cognitive load biases toward model-free; WM capacity predicts MB use"}
        )
    ],
    scope_conditions=[
        "Applies when both habitual and planned routes are available",
        "Model-based dominates in novel environments or after layout changes",
        "Model-free dominates under time pressure, cognitive load, or stress",
        "Arbitration itself has a metabolic cost mediated by PFC engagement"
    ],
    moderators=[
        "familiarity (extensive experience → stronger model-free habits)",
        "stakes (emergency → model-free unless trained otherwise)",
        "individual_WM_capacity (higher WM → more model-based; links T36)",
        "age (aging biases toward model-free; Eppinger, Walter, Heekeren, & Li, 2013)",
        "stress_hormones (cortisol biases toward model-free; Schwabe & Wolf, 2009)"
    ],
    interactions=[
        {"template": "T3 (SN_COGNITIVE_MAP_001)", "type": "SUBSTRATE",
         "description": "T3 provides the model-based planning system. When arbitration selects model-based, T3's cognitive map is the computational resource used for navigation."},
        {"template": "T37 (DP_ECOLOGICAL_RATIONALITY_001)", "type": "PARALLEL",
         "description": "T37 formalizes when heuristics outperform deliberation. T43 formalizes the neural mechanism that implements this arbitration specifically for spatial behavior."},
        {"template": "T41 (NM_RPE_001)", "type": "INPUT",
         "description": "RPE signals (T41) update the cached values used by the model-free system and provide the outcome feedback that drives learning in both systems."},
        {"template": "T38 (CROSS_COGNITIVE_LOAD_001)", "type": "MODULATOR",
         "description": "Cognitive load (T38) biases arbitration toward model-free by consuming the PFC resources model-based planning requires."}
    ],
    overall_maturity="how-actually",
    key_references=[
        "Daw, Niv, & Dayan (2005) Nature Neuroscience",
        "Daw, Gershman, Seymour, Dayan, & Dolan (2011) Neuron",
        "Lee, Shimojo, & O'Doherty (2014) Neuron",
        "Otto, Gershman, Markman, & Daw (2013) Psychological Science",
        "Schwabe & Wolf (2009) Journal of Neuroscience"
    ]
)
```

### T44: CROSS_HIERARCHICAL_CONTROL_001

**Frameworks**: PP + DT + MS (cross-framework)
**Name**: Hierarchical Control Gradient in Architectural Demands
**Structural Pattern**: STRATIFICATION (environmental demands engage different levels of a PFC hierarchy depending on abstraction of required policy)
**Higher-Order Principle**: Prefrontal cortex is organized along a rostro-caudal gradient of policy abstraction. Architectural environments systematically engage different levels of this hierarchy based on the abstractness and temporal extent of the required behavioral policy.

```python
MechanisticTemplate(
    template_id="CROSS_HIERARCHICAL_CONTROL_001",
    name="Hierarchical Control Gradient in Architectural Demands",
    structural_pattern="STRATIFICATION",
    higher_order_principle=(
        "PFC rostro-caudal gradient of policy abstraction: posterior "
        "PFC handles concrete sensorimotor mappings; mid-lateral PFC "
        "handles contextual rules; anterior PFC handles temporally "
        "extended abstract task sets. Architectural environments "
        "systematically engage different levels based on behavioral "
        "policy complexity."
    ),
    transferable_to=[
        "hospital design (simple corridors vs context-dependent wayfinding)",
        "office design (focused execution vs multi-project workspace management)",
        "educational facilities (structured vs self-directed learning environments)",
        "mixed-use buildings (frequent policy switching across zones)"
    ],
    framework_ids=["PP", "DT", "MS"],
    causal_links=[
        CausalLink(
            from_variable="architectural_policy_complexity",
            to_variable="pfc_hierarchy_level_engaged",
            activity="recruit_appropriate_control_level",
            from_level="PERSONAL_EPISTEMIC",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Badre, 2008; Badre & Nee, 2018",
            parameters={"level_1": "premotor (sensorimotor)",
                        "level_2": "mid_lateral_PFC (contextual rules)",
                        "level_3": "anterior_PFC (abstract policies)",
                        "level_4": "frontopolar (meta-cognitive / relational)"}
        ),
        CausalLink(
            from_variable="pfc_hierarchy_level_engaged",
            to_variable="metabolic_demand_pfc",
            activity="scale_resource_consumption",
            from_level="SUBPERSONAL",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Badre & Nee, 2018; Koechlin & Summerfield, 2007",
            parameters={"cost_scaling": "approximately_linear_with_level",
                        "note": "Higher levels activate lower levels recursively → cumulative cost"}
        ),
        CausalLink(
            from_variable="metabolic_demand_pfc",
            to_variable="sustained_task_performance",
            activity="deplete_or_sustain_control",
            from_level="SUBPERSONAL",
            to_level="PERSONAL_EPISTEMIC",
            bridging_quality="MEDIUM",
            maturity="how-plausibly",
            key_evidence="Shenhav, Botvinick, & Cohen, 2013",
            parameters={"note": "EVC theory: anterior cingulate computes expected value of control and may disengage when cost exceeds expected benefit"}
        )
    ],
    scope_conditions=[
        "Applies to environments requiring maintained behavioral policies (not passive observation)",
        "Hierarchy is engaged sequentially bottom-up; higher levels subsume lower",
        "Individual differences in PFC maturation (adolescents) and decline (aging) shift capacity at each level",
        "Disrupted in patients with frontal lobe lesions — architectural accessibility implications"
    ],
    moderators=[
        "signage_clarity (clear signage reduces required policy level by offloading contextual rules)",
        "layout_predictability (predictable layouts reduce the level of abstraction required)",
        "task_switching_frequency (frequent zone changes between task demands increase level 3-4 engagement)",
        "user_expertise (experts develop compiled routines that reduce level of engagement)"
    ],
    interactions=[
        {"template": "T38 (CROSS_COGNITIVE_LOAD_001)", "type": "SPECIFICATION",
         "description": "T44 specifies the mechanism that T38 abstracts. T38 says architectural complexity costs energy; T44 says specifically which PFC levels and at what scaling."},
        {"template": "T4 (PP_ATTENTIONAL_DEMAND_001)", "type": "INPUT",
         "description": "Attentional demand (T4) feeds the lowest level of the control hierarchy; higher levels are engaged only when attentional demands require rule-governed or abstract policy responses."},
        {"template": "T27 (DT_DMN_TPN_DYNAMICS_001)", "type": "CONTEXT",
         "description": "DT captures the binary toggle into task-positive mode; T44 captures the graded hierarchy within that mode."}
    ],
    overall_maturity="how-actually (for PFC gradient); how-plausibly (for architectural mapping)",
    key_references=[
        "Badre (2008) Trends in Cognitive Sciences",
        "Badre & Nee (2018) Trends in Cognitive Sciences",
        "Koechlin & Summerfield (2007) Trends in Cognitive Sciences",
        "Shenhav, Botvinick, & Cohen (2013) Neuron",
        "Botvinick & Cohen (2014) Cognitive Science"
    ]
)
```

### T45: CROSS_PROACTIVE_REACTIVE_CONTROL_001

**Frameworks**: PP + DT + NM (cross-framework)
**Name**: Proactive–Reactive Control Mode and Architectural Predictability
**Structural Pattern**: BIFURCATION (environmental predictability → selection of one of two control modes with distinct neural signatures, metabolic profiles, and population sensitivities)
**Higher-Order Principle**: Predictable environments engage proactive control (sustained lateral PFC, low-cost maintenance); unpredictable environments engage reactive control (transient ACC, high-cost conflict monitoring). Individual variation in proactive capacity (reduced in aging, stress, ADHD, schizophrenia) means the same building imposes different cognitive costs on different populations.

```python
MechanisticTemplate(
    template_id="CROSS_PROACTIVE_REACTIVE_CONTROL_001",
    name="Proactive-Reactive Control Mode and Architectural Predictability",
    structural_pattern="BIFURCATION",
    higher_order_principle=(
        "Predictable environments enable proactive control (sustained "
        "lateral PFC, anticipatory goal maintenance, metabolically "
        "steady). Unpredictable environments force reactive control "
        "(transient ACC conflict detection, stimulus-driven retrieval, "
        "metabolically bursty). Populations with reduced proactive "
        "capacity bear disproportionate cost in unpredictable buildings."
    ),
    transferable_to=[
        "healthcare design (predictable layouts for cognitively impaired populations)",
        "educational design (structured vs discovery-based learning environments)",
        "workplace design (open-plan interruption → forced reactive mode)",
        "wayfinding systems (clear signage enables proactive route planning)"
    ],
    framework_ids=["PP", "DT", "NM"],
    causal_links=[
        CausalLink(
            from_variable="architectural_predictability",
            to_variable="control_mode_selection",
            activity="bias_toward_proactive_or_reactive",
            from_level="PERSONAL_EPISTEMIC",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Braver, 2012",
            parameters={"proactive_substrate": "sustained_lateral_PFC_DLPFC",
                        "reactive_substrate": "transient_ACC_plus_lateral_PFC",
                        "switch_latency_ms": "500-1500"}
        ),
        CausalLink(
            from_variable="control_mode_selection",
            to_variable="metabolic_temporal_profile",
            activity="determine_energy_expenditure_pattern",
            from_level="SUBPERSONAL",
            to_level="SUBPERSONAL",
            bridging_quality="MEDIUM",
            maturity="how-plausibly",
            key_evidence="Braver, 2012; Botvinick & Cohen, 2014",
            parameters={"proactive_profile": "steady_moderate_sustained",
                        "reactive_profile": "bursty_high_peak_then_low",
                        "integrated_cost_comparison": "reactive > proactive for extended tasks"}
        ),
        CausalLink(
            from_variable="individual_proactive_capacity",
            to_variable="control_mode_selection",
            activity="modulate_mode_accessibility",
            from_level="SUBPERSONAL",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Braver et al., 2007; Edwards et al., 2010",
            parameters={"reduced_in": ["aging", "high_stress", "ADHD", "schizophrenia", "low_WM_capacity"],
                        "note": "These populations are pushed toward reactive mode even in moderately predictable environments"}
        )
    ],
    scope_conditions=[
        "Applies to environments requiring sustained goal-directed behavior (not passive exposure)",
        "Predictability assessed at architectural scale (layout regularity, signage, material consistency)",
        "Mixed environments (predictable macro-layout, surprising micro-details) may support proactive macro-control with reactive micro-adjustments",
        "Proactive mode requires PFC integrity and sufficient WM capacity"
    ],
    moderators=[
        "environmental_legibility (SN variable — clear spatial structure supports proactive)",
        "interruption_frequency (open-plan offices force reactive mode)",
        "circadian_phase (proactive control degrades with circadian misalignment, connecting to CB)",
        "acute_stress (cortisol biases toward reactive; links NM/T5)",
        "familiarity_with_building (expertise enables proactive even in complex buildings)"
    ],
    interactions=[
        {"template": "T44 (CROSS_HIERARCHICAL_CONTROL_001)", "type": "ORTHOGONAL",
         "description": "T44 specifies WHICH level of control hierarchy is engaged; T45 specifies the temporal MODE (sustained vs transient) at that level. Orthogonal dimensions that combine: proactive at level 3 is efficient; reactive at level 3 is very costly."},
        {"template": "T29 (ALLOSTATIC_MASTER_001)", "type": "OUTPUT",
         "description": "T29 should be parameterized by control mode: proactive mode produces steady allostatic load; reactive mode produces bursty allostatic spikes. Chronic reactive mode is allostatic overload."},
        {"template": "T38 (CROSS_COGNITIVE_LOAD_001)", "type": "REFINEMENT",
         "description": "T38 predicts cognitive load from environmental complexity. T45 refines this: the SAME environmental complexity produces different load profiles depending on control mode."},
        {"template": "T1 (PP_PREDICTION_ERROR_001)", "type": "TRIGGER",
         "description": "Prediction error (T1) is the signal that can force a switch from proactive to reactive control. Large PE → ACC conflict signal → reactive mobilization."}
    ],
    overall_maturity="how-actually (for DMC framework); how-plausibly (for architectural mapping)",
    key_references=[
        "Braver (2012) Trends in Cognitive Sciences",
        "Braver, Gray, & Burgess (2007) in Conway et al., Variation in Working Memory",
        "Edwards, Barch, & Braver (2010) Psychological Medicine",
        "Botvinick & Cohen (2014) Cognitive Science",
        "Gratton, Cooper, Fabiani, Carter, & Karayanidis (2018) Trends in Cognitive Sciences"
    ]
)
```

### T46: CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001

**Frameworks**: MSI + PP (cross-framework)
**Name**: Thalamic Environmental Filtering (Pulvinar)
**Structural Pattern**: GATING (environmental input → thalamic filter → cortical access)
**Higher-Order Principle**: The pulvinar nucleus acts as a dynamic filter on environmental information reaching cortex, implementing attentional modes (focused "spotlight" vs distributed "floodlight") that are shaped by spatial configuration and modulated by behavioral goals.

```python
MechanisticTemplate(
    template_id="CROSS_THALAMIC_ENVIRONMENTAL_FILTER_001",
    name="Thalamic Environmental Filtering (Pulvinar)",
    structural_pattern="GATING",
    higher_order_principle=(
        "Pulvinar nucleus dynamically filters environmental information "
        "reaching cortex, implementing attentional modes — focused "
        "'spotlight' for narrow corridors and target-directed movement, "
        "distributed 'floodlight' for open spaces and ambient monitoring. "
        "Mode selection is driven by spatial configuration and modulated "
        "by top-down behavioral goals and bottom-up salience."
    ),
    transferable_to=[
        "corridor vs atrium design (spotlight vs floodlight engagement)",
        "safety-critical environments (monitoring demands require floodlight)",
        "focused work environments (spotlight mode reduces distraction)",
        "retail design (floodlight for browsing vs spotlight for purchase)"
    ],
    framework_ids=["MSI", "PP"],
    causal_links=[
        CausalLink(
            from_variable="spatial_configuration",
            to_variable="pulvinar_filtering_mode",
            activity="select_attentional_mode",
            from_level="PERSONAL_EPISTEMIC",
            to_level="SUBPERSONAL",
            bridging_quality="MEDIUM",
            maturity="how-plausibly",
            key_evidence="Saalmann & Kastner, 2011; Kastner & Ungerleider, 2000",
            parameters={"spotlight_trigger": "narrow_FOV, proximal_goal",
                        "floodlight_trigger": "wide_FOV, ambient_monitoring",
                        "modulation_band": "alpha (8-12 Hz) synchronization"}
        ),
        CausalLink(
            from_variable="pulvinar_filtering_mode",
            to_variable="cortical_information_access",
            activity="gate_sensory_throughput",
            from_level="SUBPERSONAL",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Saalmann, Pinsk, Wang, Li, & Kastner, 2012",
            parameters={"mechanism": "alpha-band pulvinar-cortex synchronization",
                        "effect": "spotlight narrows cortical representation; floodlight broadens it"}
        ),
        CausalLink(
            from_variable="cortical_information_access",
            to_variable="environmental_awareness_type",
            activity="shape_perceptual_experience",
            from_level="SUBPERSONAL",
            to_level="PERSONAL_EPISTEMIC",
            bridging_quality="MEDIUM",
            maturity="how-plausibly",
            key_evidence="Inferred from Saalmann & Kastner, 2011; direct architectural evidence limited",
            parameters={"spotlight_experience": "focused, detailed, tunnel-like",
                        "floodlight_experience": "ambient, panoramic, peripherally aware"}
        )
    ],
    scope_conditions=[
        "Applies to sighted individuals in illuminated environments",
        "Mode selection is influenced but not determined by spatial layout — top-down goals can override",
        "Pulvinar also integrates cross-modal information — not strictly visual",
        "Damaged or underdeveloped pulvinar (some premature infants) → impaired filtering"
    ],
    moderators=[
        "threat_level (threat biases toward floodlight for monitoring; links T5)",
        "reward_location (known reward location biases toward spotlight; links T41)",
        "task_demands (search tasks → spotlight; monitoring tasks → floodlight)",
        "developmental_status (pulvinar matures late; children may default to floodlight)"
    ],
    interactions=[
        {"template": "T4 (PP_ATTENTIONAL_DEMAND_001)", "type": "MECHANISM",
         "description": "T4 abstracts attentional demand as a resource cost; T46 specifies the thalamic mechanism that determines HOW attention is deployed (spotlight vs floodlight), which has different resource profiles."},
        {"template": "T26 (NM_CHOLINERGIC_GATING_001)", "type": "COMPLEMENT",
         "description": "T26 captures neuromodulatory gain control (acetylcholine sharpens cortical representations); T46 captures the thalamic relay that determines which representations reach cortex in the first place. Sequential mechanisms: pulvinar selects → ACh amplifies."},
        {"template": "T31 (AUD_SCENE_ANALYSIS_001)", "type": "PARALLEL",
         "description": "T31 captures auditory scene analysis; T46 captures the visual/multisensory thalamic gating that operates on a parallel but interacting stream. Pulvinar also processes auditory spatial information."}
    ],
    overall_maturity="how-actually (thalamic gating mechanism); how-possibly (architectural mapping — inferred, not directly tested in built environments)",
    key_references=[
        "Saalmann & Kastner (2011) Neuron",
        "Kastner & Ungerleider (2000) Annual Review of Neuroscience",
        "Saalmann, Pinsk, Wang, Li, & Kastner (2012) Science",
        "Arcaro, Pinsk, & Kastner (2015) Journal of Neuroscience"
    ]
)
```

### T47: CROSS_WM_GAMMA_BETA_DYNAMICS_001

**Frameworks**: MS + DT (cross-framework)
**Name**: Working Memory Gamma/Beta Dynamics in Environmental Processing
**Structural Pattern**: OSCILLATORY GATING (environmental information load → gamma burst frequency × beta gating efficiency → WM performance and metabolic cost)
**Higher-Order Principle**: Working memory content is maintained by brief gamma bursts (~60–100 Hz) and cleared by beta bursts (~15–30 Hz) in prefrontal-parietal circuits. Environments that overload gamma frequency or degrade beta gating efficiency impose measurable neural costs detectable via non-invasive EEG.

```python
MechanisticTemplate(
    template_id="CROSS_WM_GAMMA_BETA_DYNAMICS_001",
    name="WM Gamma/Beta Dynamics in Environmental Processing",
    structural_pattern="OSCILLATORY_GATING",
    higher_order_principle=(
        "WM representations maintained by prefrontal gamma bursts "
        "(~60-100 Hz, content encoding) and cleared by beta bursts "
        "(~15-30 Hz, gating/clearing). Environmental information load "
        "modulates gamma burst frequency; distraction degrades beta "
        "gating efficiency. Both are measurable via non-invasive EEG "
        "in ecological settings."
    ),
    transferable_to=[
        "open-plan office design (distraction → degraded beta gating)",
        "hospital design (information-dense environments → gamma overload)",
        "classroom design (optimizing information presentation rate for WM capacity)",
        "control room design (sustained monitoring demands on WM dynamics)"
    ],
    framework_ids=["MS", "DT"],
    causal_links=[
        CausalLink(
            from_variable="environmental_information_load",
            to_variable="gamma_burst_frequency",
            activity="encode_items_to_WM",
            from_level="PERSONAL_EPISTEMIC",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Lundqvist et al., 2016",
            parameters={"frequency_range_Hz": "60-100",
                        "burst_duration_ms": "50-150",
                        "capacity_limit": "3-5 items (gamma bursts per cycle)"}
        ),
        CausalLink(
            from_variable="environmental_distraction_level",
            to_variable="beta_gating_efficiency",
            activity="degrade_clearing_mechanism",
            from_level="PERSONAL_EPISTEMIC",
            to_level="SUBPERSONAL",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Miller, Lundqvist, & Bastos, 2018",
            parameters={"frequency_range_Hz": "15-30",
                        "effect": "distractors trigger gamma bursts that compete with maintained items; insufficient beta fails to clear them"}
        ),
        CausalLink(
            from_variable="gamma_burst_frequency",
            to_variable="prefrontal_metabolic_cost",
            activity="scale_energy_consumption",
            from_level="SUBPERSONAL",
            to_level="SUBPERSONAL",
            bridging_quality="MEDIUM",
            maturity="how-plausibly",
            key_evidence="Lundqvist et al., 2016; metabolic cost inferred from fMRI BOLD and computational models",
            parameters={"note": "More gamma bursts per second → higher PFC metabolic demand → faster cognitive fatigue"}
        ),
        CausalLink(
            from_variable="beta_gating_efficiency",
            to_variable="wm_task_accuracy",
            activity="determine_maintenance_fidelity",
            from_level="SUBPERSONAL",
            to_level="PERSONAL_EPISTEMIC",
            bridging_quality="HIGH",
            maturity="how-actually",
            key_evidence="Lundqvist et al., 2016; Miller et al., 2018",
            parameters={"measurable_via": "mobile_EEG_beta_power_over_PFC",
                        "prediction": "lower beta power in open-plan vs enclosed offices"}
        )
    ],
    scope_conditions=[
        "Applies to environments requiring active maintenance of information in WM",
        "Gamma/beta dynamics require intact prefrontal-parietal network",
        "Ecological measurement via mobile EEG is feasible but requires careful artifact rejection",
        "Capacity limits are relatively fixed — architectural design should work within them, not assume they can be expanded"
    ],
    moderators=[
        "acoustic_environment (speech distractors are especially potent at disrupting beta gating)",
        "visual_complexity (high visual information density increases gamma load)",
        "individual_WM_capacity (varies with age, training, and PFC integrity)",
        "circadian_phase (gamma/beta dynamics degrade with sleep deprivation; links CB)"
    ],
    interactions=[
        {"template": "T36 (MS_WORKING_MEMORY_LOAD_001)", "type": "MECHANISM",
         "description": "T36 treats WM load as a capacity-based abstraction. T47 provides the oscillatory mechanism: load = gamma burst frequency; overload = gamma exceeds beta clearing rate."},
        {"template": "T44 (CROSS_HIERARCHICAL_CONTROL_001)", "type": "SUBSTRATE",
         "description": "The gamma/beta dynamics implement the lowest level of the control hierarchy (T44 Level 1). Higher control levels recruit additional PFC regions with their own oscillatory dynamics."},
        {"template": "T29 (ALLOSTATIC_MASTER_001)", "type": "OUTPUT",
         "description": "Chronic gamma overload (environmentally induced) contributes to allostatic burden. T47 provides a specific, measurable pathway from environment to metabolic cost."},
        {"template": "T45 (CROSS_PROACTIVE_REACTIVE_001)", "type": "MODE",
         "description": "Proactive control (T45) maintains goal representations via sustained gamma activity; reactive control triggers transient gamma bursts. Different metabolic signatures at the oscillatory level."}
    ],
    overall_maturity="how-actually (gamma/beta mechanism); how-plausibly (ecological EEG measurement); how-possibly (specific architectural predictions)",
    key_references=[
        "Lundqvist, Rose, Herman, Brincat, Buschman, & Miller (2016) Neuron",
        "Miller, Lundqvist, & Bastos (2018) Neuron",
        "Bastos et al. (2018) eLife",
        "Kornblith, Buschman, & Miller (2016) Cerebral Cortex"
    ]
)
```

---

## Part 5: Updated Independence Matrix Implications

Since CC/EF is not promoted to Tier 1, no new row/column is added to the 10×10 independence matrix. However, the seven new templates (T41–T47) interact extensively with existing frameworks. For CMR pipeline purposes:

**Cross-framework template participation in mechanism tracing (Step 3)**:

| Template | Participates When |
|---|---|
| T43 (MB/MF Arbitration) | Any finding involving navigation strategy or spatial decision-making |
| T44 (Hierarchical Control) | Any finding involving task demands graded by abstraction |
| T45 (Proactive/Reactive) | Any finding involving environmental predictability or legibility |
| T46 (Thalamic Filtering) | Any finding involving attentional mode in spatial contexts |
| T47 (Gamma/Beta WM) | Any finding involving information load or distraction |

**Cross-framework templates do NOT contribute to Step 5 convergence scoring.** They provide mechanistic detail within a trace but not independent evidential weight. This is consistent with the panel's verdict that control is a meta-process coordinating domain-specific computations.

---

## Part 6: Testable Predictions Generated by New Templates

The panel identified five high-priority testable predictions that follow from the new templates and that were not generable from the existing 10-framework library:

### Prediction 1 (from T42)
**Wanting–liking dissociation in museum design**: A visually dramatic entrance hall (high incentive salience) paired with an uncomfortable gallery (low hedonic impact) will show high visit initiation rates but low dwell times and reduced return visits. Conversely, an unassuming entrance with comfortable galleries will show lower initiation but higher dwell and return. **Measurable via**: visit logs (approach), dwell time (liking), return rates, self-report pleasure ratings. **Predicted dissociation**: entrance drama correlates with initiation but not satisfaction; gallery comfort correlates with satisfaction but not initiation.

### Prediction 2 (from T45)
**Proactive–reactive control and population vulnerability**: In a hospital with unpredictable layout, elderly patients (reduced proactive capacity) will show elevated cortisol and longer wayfinding times compared to a matched population in a predictable hospital — and this difference will be *larger* for the elderly than for young adults navigating the same pair of hospitals. **Measurable via**: salivary cortisol, wayfinding time, mobile EEG (ACC activation as proxy for reactive control engagement). **Critical test**: the age × predictability interaction should be driven by reactive control load, not spatial memory per se.

### Prediction 3 (from T43)
**Model-based/model-free arbitration and layout changes**: When a familiar building undergoes a layout change (e.g., retail store reorganization), navigators will show a transient period of increased PFC activation (model-based recruitment) followed by habituation back to model-free routing. The duration of this transient should scale with the magnitude of the layout change and correlate inversely with individual WM capacity. **Measurable via**: mobile fNIRS/EEG, navigation path efficiency, individual WM span assessment.

### Prediction 4 (from T46)
**Spotlight/floodlight modes and spatial configuration**: Narrow corridors should show increased alpha synchronization between estimated pulvinar and visual cortex sources (spotlight mode), while open atriums should show decreased alpha synchronization (floodlight mode). Behavioral correlate: corridor navigation shows faster detection of objects directly ahead but poorer peripheral awareness; atrium behavior shows slower focused detection but better ambient monitoring. **Measurable via**: high-density mobile EEG with source localization, eye tracking, peripheral detection task.

### Prediction 5 (from T47)
**Open-plan offices and beta gating degradation**: Workers in open-plan offices should show reduced prefrontal beta power during WM tasks compared to the same workers in enclosed offices, indicating degraded gating. This should correlate with (a) higher subjective distraction ratings, (b) increased gamma burst "false starts" (encoding irrelevant distractors), and (c) reduced WM task accuracy. **Measurable via**: mobile EEG comparing within-subject across workspace configurations. **Design implication**: partitions that reduce auditory distraction should restore beta gating efficiency even without full enclosure.

---

## Part 7: Implementation Notes for CC and Antigravity

### For Claude Code (Sprint 7):
- Templates T41 and T42 are NM-framework-owned. Add them to the NM scope declaration's template list.
- Templates T43–T47 are cross-framework. Use the same data model as T29 (allostatic master). Tag with `cross_framework=True` and list all participating `framework_ids`.
- The `structural_pattern` field gains two new values: `COMPETITION` (T43), `STRATIFICATION` (T44), `BIFURCATION` (T45), `GATING` (T46), `OSCILLATORY_GATING` (T47). Add these to the structural pattern enum.
- **Do not add a row/column to the independence matrix.** CC/EF is not Tier 1.

### For Antigravity (Sprint 7.5):
- When encoding remaining 28 templates, use the new templates here as additional seed patterns for cross-framework templates. T43–T47 demonstrate the format.
- Cross-framework templates should always list interactions with framework-owned templates they connect.

### For Codex:
- Validate that the 5 new structural pattern values are registered in `canonical_enums.json` after CC implements them.
- Run `check_enum_drift.py` for `structural_pattern` after Sprint 7.

---

## Part 8: Full Reference List

Arcaro, M. J., Pinsk, M. A., & Kastner, S. (2015). The anatomical and functional organization of the human visual pulvinar. *Journal of Neuroscience*, *35*(27), 9848–9871. [~250 citations]

Badre, D. (2008). Cognitive control, hierarchy, and the rostro-caudal organization of the frontal lobes. *Trends in Cognitive Sciences*, *12*(5), 193–200. [~1,800 citations]

Badre, D., & Nee, D. E. (2018). Frontal cortex and the hierarchical control of behavior. *Trends in Cognitive Sciences*, *22*(2), 170–188. [~450 citations]

Bastos, A. M., Loonis, R., Kornblith, S., Lundqvist, M., & Miller, E. K. (2018). Laminar recordings in frontal cortex suggest distinct layers for maintenance and control of working memory. *Proceedings of the National Academy of Sciences*, *115*(5), 1117–1122. [~250 citations]

Berridge, K. C. (2007). The debate over dopamine's role in reward: The case for incentive salience. *Psychopharmacology*, *191*(3), 391–431. [~2,000 citations]

Berridge, K. C., & Kringelbach, M. L. (2015). Pleasure systems in the brain. *Neuron*, *86*(3), 646–664. [~1,500 citations]

Berridge, K. C., & Robinson, T. E. (2016). Liking, wanting, and the incentive-sensitization theory of addiction. *American Psychologist*, *71*(8), 670–679. [~1,200 citations]

Botvinick, M. M., & Cohen, J. D. (2014). The computational and neural basis of cognitive control: Charted territory and new frontiers. *Cognitive Science*, *38*(6), 1249–1285. [~400 citations]

Braver, T. S. (2012). The variable nature of cognitive control: A dual mechanisms framework. *Trends in Cognitive Sciences*, *16*(2), 106–113. [~2,100 citations]

Braver, T. S., Gray, J. R., & Burgess, G. C. (2007). Explaining the many varieties of working memory variation: Dual mechanisms of cognitive control. In A. R. A. Conway, C. Jarrold, M. J. Kane, A. Miyake, & J. N. Towse (Eds.), *Variation in working memory* (pp. 76–106). Oxford University Press. [~750 citations]

Daw, N. D., Gershman, S. J., Seymour, B., Dayan, P., & Dolan, R. J. (2011). Model-based influences on humans' choices and striatal prediction errors. *Neuron*, *69*(6), 1204–1215. [~2,100 citations]

Daw, N. D., Niv, Y., & Dayan, P. (2005). Uncertainty-based competition between prefrontal and dorsolateral striatal systems for behavioral control. *Nature Neuroscience*, *8*(12), 1704–1711. [~2,600 citations]

Daw, N. D., O'Doherty, J. P., Dayan, P., Seymour, B., & Dolan, R. J. (2006). Cortical substrates for exploratory decisions in humans. *Nature*, *441*(7095), 876–879. [~1,800 citations]

Edwards, B. G., Barch, D. M., & Braver, T. S. (2010). Improving prefrontal cortex function in schizophrenia through focused training of cognitive control. *Frontiers in Human Neuroscience*, *4*, 32. [~150 citations]

Eppinger, B., Walter, M., Heekeren, H. R., & Li, S. C. (2013). Of goals and habits: Age-related and individual differences in goal-directed decision-making. *Frontiers in Neuroscience*, *7*, 253. [~200 citations]

Gratton, G., Cooper, P., Fabiani, M., Carter, C. S., & Karayanidis, F. (2018). Dynamics of cognitive control: Theoretical bases, paradigms, and a view for the future. *Psychophysiology*, *55*(3), e13016. [~200 citations]

Kastner, S., & Ungerleider, L. G. (2000). Mechanisms of visual attention in the human cortex. *Annual Review of Neuroscience*, *23*(1), 315–341. [~5,200 citations]

Koechlin, E., & Summerfield, C. (2007). An information theoretical approach to prefrontal executive function. *Trends in Cognitive Sciences*, *11*(6), 229–235. [~600 citations]

Kornblith, S., Buschman, T. J., & Miller, E. K. (2016). Stimulus load and oscillatory activity in higher cortex. *Cerebral Cortex*, *26*(9), 3772–3784. [~100 citations]

Lee, S. W., Shimojo, S., & O'Doherty, J. P. (2014). Neural computations underlying arbitration between model-based and model-free learning. *Neuron*, *81*(3), 687–699. [~600 citations]

Lundqvist, M., Rose, J., Herman, P., Brincat, S. L., Buschman, T. J., & Miller, E. K. (2016). Gamma and beta bursts underlie working memory. *Neuron*, *90*(1), 152–164. [~750 citations]

Miller, E. K., & Cohen, J. D. (2001). An integrative theory of prefrontal cortex function. *Annual Review of Neuroscience*, *24*(1), 167–202. [~15,500 citations]

Miller, E. K., Lundqvist, M., & Bastos, A. M. (2018). Working Memory 2.0. *Neuron*, *100*(2), 463–475. [~850 citations]

O'Doherty, J. P., Dayan, P., Schultz, J., Deichmann, R., Friston, K., & Dolan, R. J. (2004). Dissociable roles of ventral and dorsal striatum in instrumental conditioning. *Science*, *304*(5669), 452–454. [~2,200 citations]

Otto, A. R., Gershman, S. J., Markman, A. B., & Daw, N. D. (2013). The curse of planning: Dissecting multiple reinforcement-learning systems by taxing the central executive. *Psychological Science*, *24*(5), 751–761. [~700 citations]

Pool, E., Sennwald, V., Delplanque, S., Brosch, T., & Sander, D. (2016). Measuring wanting and liking from animals to humans: A systematic review. *Neuroscience & Biobehavioral Reviews*, *63*, 124–142. [~200 citations]

Saalmann, Y. B., & Kastner, S. (2011). Cognitive and perceptual functions of the visual thalamus. *Neuron*, *71*(2), 209–223. [~650 citations]

Saalmann, Y. B., Pinsk, M. A., Wang, L., Li, X., & Kastner, S. (2012). The pulvinar regulates information transmission between cortical areas based on attention demands. *Science*, *337*(6095), 753–756. [~800 citations]

Schultz, W., Dayan, P., & Montague, P. R. (1997). A neural substrate of prediction and reward. *Science*, *275*(5306), 1593–1599. [~8,500 citations]

Schwabe, L., & Wolf, O. T. (2009). Stress prompts habit behavior in humans. *Journal of Neuroscience*, *29*(22), 7191–7198. [~900 citations]

Shenhav, A., Botvinick, M. M., & Cohen, J. D. (2013). The expected value of control: An integrative theory of anterior cingulate cortex function. *Neuron*, *79*(2), 217–240. [~2,200 citations]

---

*Panel IV completed: February 15, 2026*
*Verdicts: CC/EF NOT promoted to Tier 1; 2 reward templates added to NM; 5 cross-framework control templates specified (T41–T47)*
*Next panel: Panel V (Social Brain) when David is ready*
*Next sequence number: 15*
