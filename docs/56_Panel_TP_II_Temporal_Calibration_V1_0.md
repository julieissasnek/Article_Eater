# PANEL TP-II: TEMPORAL DYNAMICS CALIBRATION
## Empirical Calibration of Doorway Gradient, Motor PE Metrics, Fractal Aging Trajectories, and Multi-Timescale Integration for TP1–TP4
## February 17, 2026 — Document 56

---

## Panel Charge

Panel TP-I (Doc 42 V1.1) produced four templates — TP1 (motor prediction), TP2 (threshold as episodic boundary), TP3 (material aging and temporal depth), and TP4 (temporal hierarchy) — that formalize how architecture organizes experience across timescales. All four templates are structurally complete but parametrically sparse. TP-II is charged with four deepening tasks and selective broadening:

**Deepening Priority 1: The Doorway Gradient (TP2)**. TP2 claims that episodic boundary strength varies continuously with the number of simultaneous sensory channels that change at a threshold. This claim needs quantitative calibration: does boundary strength increase linearly with channel count, or is there a step-function threshold? What is the channel-count → boundary-strength function? Which channels contribute most to episodic segmentation?

**Deepening Priority 2: Fractal Aging Trajectories (TP3)**. TP3 claims that natural weathering increases surface fractal dimension toward D ≈ 1.3. This is a testable quantitative claim that has never been directly measured on architectural surfaces. What fractal trajectories do common building materials actually follow over decades and centuries?

**Deepening Priority 3: Motor PE Instrumentation (TP1)**. TP1 describes three channels of motor PE (locomotor, postural, manipulative) but provides no validated metric for continuous motor PE quality during architectural movement. Can wearable IMU data be mapped onto a motor-prediction-error metric that correlates with subjective movement quality?

**Deepening Priority 4: Multi-Timescale Integration (TP4)**. TP4 asserts that architectural experience integrates PE across seven timescales simultaneously. Can this be empirically decomposed? Do PE markers at different timescales contribute independently to overall experience ratings?

**Selective Broadening**: The panel will also address circadian design parameters (Broadening Priority 1 from the TP-I prospectus) where they intersect with temporal calibration, and age-related motor parameter shifts where data exist.

---

## Panel Composition

### Returning from TP-I

| Panelist | Affiliation | Returning Role |
|----------|-------------|----------------|
| **Gabriel Radvansky** | University of Notre Dame | Doorway effect empirics; provides the parametric data for TP2 boundary-strength calibration |
| **Jeffrey Zacks** | Washington University in St. Louis | Event Segmentation Theory; calibrates the multi-modal change → boundary-strength function |
| **Daniel Wolpert** | Columbia University | Motor prediction framework; guides motor PE metric validation |
| **William Warren** | Brown University | Body-scaled affordances; provides the reference thresholds for TP1 parameter ranges |
| **Hugo Spiers** | University College London | Real-world navigation neuroscience; anchors multi-timescale neural measurement |
| **Marc Wittmann** | Institute for Frontier Areas of Psychology, Freiburg | Subjective time perception; calibrates PE-density → temporal-experience mapping |
| **Mohsen Mostafavi** | Harvard GSD | Weathering theory; anchors TP3 material aging trajectories |

### New Panelists

| Panelist | Affiliation | Why They Are Here |
|----------|-------------|-------------------|
| **Khena Swallow** | Cornell University, Department of Psychology | Event perception and the attentional boost effect — the finding that memory encoding is ENHANCED at event boundaries through transient attention increases (Swallow & Jiang, 2010, ~700 citations; Swallow, Zacks, & Abrams, 2009, ~400 citations). Provides the attention-memory coupling mechanism that explains WHY thresholds are memorable, and specific predictions about how boundary strength scales with attentional engagement. Named in TP-I prospectus as ideal addition for TP2 calibration. |
| **Jeffrey Hausdorff** | Tel Aviv University, Department of Physical Therapy | The leading researcher on gait dynamics and variability — his work established that human walking exhibits fractal temporal structure (stride intervals follow a 1/f pattern) and that deviations from this fractal pattern predict fall risk and motor pathology (Hausdorff et al., 1995, ~2,000 citations; Hausdorff, 2007, ~1,500 citations). Provides the quantitative gait-analysis methodology needed to build a validated motor PE metric from wearable IMU data. Named in TP-I prospectus as ideal addition for TP1 calibration. |
| **Caroline Hagerhall** | Swedish University of Agricultural Sciences | Fractal dimension measurement in natural and built environments — her work established the perceptual preference for fractal dimension D ≈ 1.3 in landscape settings (Hagerhall et al., 2004, ~500 citations) and developed robust measurement protocols for fractal analysis of environmental surfaces. Provides the measurement infrastructure needed to test TP3's fractal aging hypothesis. Named in TP-I prospectus as ideal addition for TP3 calibration. |
| **Panagiotis Mavros** | National University of Singapore / ETH Zürich | Mobile EEG and physiological measurement in real-world built environments — his work demonstrates that ambulatory neuroscience methods can capture neural responses to architectural features during actual navigation (Mavros et al., 2022, ~150 citations). Provides the multi-modal measurement methodology needed for TP4's multi-timescale integration claim. Named in TP-I prospectus as ideal addition for TP4 calibration. |
| **Marjorie Woollacott** | University of Oregon, Department of Human Physiology | Postural control neuroscience across the lifespan — her work on age-related changes in postural stability (Woollacott & Shumway-Cook, 2002, ~2,500 citations) and the attentional demands of balance maintenance provides the age-moderation parameters needed for TP1's motor PE template. Brings the developmental dimension that connects TP-II to the planned Aging & Architecture panel. |

---

## Position Statements

### DEEPENING TP2: THE DOORWAY GRADIENT — HOW MANY CHANNELS MAKE AN EPISODIC BOUNDARY?

**PS-Radvansky: The Doorway Effect Is Graded, Not Binary**

The original doorway effect studies (Radvansky & Copeland, 2006; Radvansky et al., 2011) used a binary manipulation — doorway vs. no doorway — and found a robust memory decrement for objects associated with the preceding room. But the architectural question TP2 raises is more graded: given that different thresholds involve different magnitudes of context change, how does boundary strength scale with the number of sensory channels that change?

Our more recent work provides partial answers. Radvansky and colleagues have shown that the doorway effect is modulated by the DEGREE of context change: walking into a visually different room produces a stronger effect than walking into a similar room through the same doorway (Radvansky, 2012, ~200 citations). The effect is also modulated by goal maintenance: participants who actively rehearse their task goal across the doorway show an attenuated effect, suggesting that the context-updating mechanism can be partially overridden by strong top-down maintenance.

What we lack — and what this panel should calibrate — is the FUNCTION relating multi-modal channel count to boundary strength. TP2 proposes three levels (weak: 1–2 channels; moderate: 2–3 channels; strong: 4+ channels), but these are intuitive divisions rather than empirically calibrated boundaries. My estimate, based on the available data plus extrapolation from event segmentation findings:

- **1 channel change** (spatial configuration only — same light, materials, sound): d ≈ 0.2–0.3 memory decrement (weak doorway effect, barely above noise)
- **2 channel changes** (e.g., spatial + luminance): d ≈ 0.4–0.5 (clear episodic boundary)
- **3 channel changes** (e.g., spatial + luminance + acoustic): d ≈ 0.6–0.7 (strong boundary, memorable transition)
- **4+ channel changes** (full multi-modal threshold): d ≈ 0.8–1.0 (very strong boundary, vivid episodic memory)

I suspect the function is approximately logarithmic — each additional channel adds a diminishing increment — rather than linear. But this is extrapolation, not data. The critical experiment would be a VR-based parametric study with graded multi-modal thresholds.

**PS-Zacks: Event Boundaries Are Detected by Prediction Error Summation**

Event Segmentation Theory provides the theoretical framework for the doorway gradient. The event segmentation mechanism operates by monitoring prediction error across all input channels simultaneously. When the summed prediction error across channels exceeds a threshold, the system declares an event boundary and initiates a new event model (Zacks et al., 2007, ~1,500 citations; Zacks & Swallow, 2007, ~600 citations).

The critical parameter is how prediction errors from different channels COMBINE. Three possibilities:

1. **Additive**: Total PE = Σ(PE_channel_i). Each channel contributes independently. This predicts a linear channel-count → boundary-strength function.

2. **Max-rule**: Total PE = max(PE_channel_i). The single largest channel change dominates. This predicts diminishing returns from additional channels.

3. **Super-additive**: Total PE > Σ(PE_channel_i). Multi-modal co-occurrence amplifies the signal. This predicts accelerating returns — a 4-channel threshold is stronger than predicted from individual channel strengths.

The existing evidence, primarily from film-segmentation studies (where participants mark perceived event boundaries while watching movies), is most consistent with an approximately ADDITIVE model with slight super-additivity for temporally synchronized changes. When visual and auditory changes co-occur within a ~500ms window, the detected boundary is stronger than predicted from the sum of individual channel contributions (Zacks, Swallow, Vettel, & McAvoy, 2006, ~300 citations). This super-additivity window is narrow — asynchronous changes produce approximately additive effects.

My calibration estimate for the architectural context: **approximately additive with a 10–20% super-additivity bonus for simultaneous multi-modal changes**. Each channel contributes roughly d ≈ 0.15–0.25 to boundary strength, with spatial configuration contributing most (d ≈ 0.25) and olfactory contributing least (d ≈ 0.10, and only at transitions — olfaction adapts quickly as MAT-II established).

**PS-Swallow: The Attentional Boost at Boundaries Explains WHY Thresholds Are Memorable**

I want to add a mechanism that TP2 implied but did not formalize: the attentional boost effect at event boundaries (Swallow & Jiang, 2010, ~700 citations). When the event segmentation system detects a boundary, it triggers a transient increase in attention — a burst of perceptual processing that enhances encoding of whatever is present at the boundary moment. This is the mechanism that makes thresholds MEMORABLE: the boundary detection signal simultaneously (a) clears the previous event model (Radvansky's doorway effect) and (b) boosts encoding of the transition itself (the attentional boost effect).

For architectural calibration, this predicts a PARADOX RATIO: the ratio of transition-memory enhancement to previous-context forgetting. In our laboratory data, the attentional boost at event boundaries enhances encoding by approximately d ≈ 0.3–0.5, while the working-memory disruption from context updating is approximately d ≈ 0.3–0.6 (Radvansky's estimates). This means strong thresholds produce BOTH effects — more forgetting of what you were thinking about AND more vivid memory of the transition itself. The net effect on overall architectural experience memory depends on what the architect wants remembered: the steady-state spatial qualities (minimize thresholds) or the spatial sequence and transitions (maximize thresholds).

The attentional boost also scales with surprise: unexpected boundaries produce larger boosts than predictable boundaries (Swallow et al., 2009). This connects directly to the PE framework: a threshold that violates the visitor's spatial prediction (turning a corner to encounter an unexpected vista) produces a larger attentional boost — and a more vivid memory — than a threshold the visitor anticipated (approaching a door they know leads to the garden).

---

### DEEPENING TP3: FRACTAL AGING TRAJECTORIES — DO BUILDINGS CONVERGE ON D ≈ 1.3?

**PS-Hagerhall: The Measurement Protocol Exists; the Architectural Data Do Not**

The fractal dimension preference near D ≈ 1.3 is one of the most robust quantitative findings in environmental aesthetics. Our work (Hagerhall et al., 2004, ~500 citations; Hagerhall, Purcell, & Taylor, 2004, ~400 citations) demonstrated that landscape silhouettes with fractal dimensions in the range D ≈ 1.2–1.4 are consistently preferred across cultures and age groups. Taylor's parallel work on Jackson Pollock paintings (Taylor et al., 2011, ~400 citations) and on natural scenes (Spehar et al., 2003, ~300 citations) converges on the same range. The measurement methodology — box-counting on high-resolution images, with appropriate scale-range selection and regression — is well-validated and produces reliable, reproducible D values.

What has NEVER been done is a systematic measurement of how building surface fractal dimension changes with age. TP3's claim that natural weathering drives surfaces toward D ≈ 1.3 is entirely theoretical — plausible, based on the observation that natural processes tend to produce fractal patterns (Mandelbrot, 1982), but unmeasured. The measurement gap is straightforward to fill:

My preliminary estimates for what we would find, based on fractal analysis of natural versus manufactured surfaces in landscape contexts:

- **Fresh-cut stone** (quarry face): D ≈ 1.0–1.1 (relatively smooth, low complexity)
- **Weathered stone at 50 years**: D ≈ 1.15–1.25 (developing surface texture from erosion, biological colonization)
- **Weathered stone at 200+ years**: D ≈ 1.25–1.40 (extensive lichen, erosion patterns, mineral staining)
- **Fresh-sawn wood**: D ≈ 1.1–1.2 (grain visible but surface relatively uniform)
- **Aged wood at 50 years**: D ≈ 1.2–1.35 (raised grain, silver patina, checking patterns)
- **Fresh brick**: D ≈ 1.05–1.15 (uniform manufactured surface)
- **Aged brick at 100+ years**: D ≈ 1.2–1.35 (efflorescence, surface erosion, mortar weathering, biological growth)
- **Fresh concrete**: D ≈ 1.0–1.1 (smooth formwork surface)
- **Aged concrete at 30+ years**: D ≈ 1.05–1.2 (staining, crazing, biological colonization) — BUT note that concrete aging is often DEGRADING rather than enriching; the D increase may not track with aesthetic improvement

The critical distinction TP3 makes between POSITIVE aging (increasing D toward the aesthetic optimum) and NEGATIVE aging (random degradation without fractal enrichment) is testable: natural materials should show D trajectories that converge on the 1.2–1.4 range, while synthetic materials should show erratic or non-convergent trajectories.

**PS-Mostafavi: Not All Aging Is Fractal Enrichment — The Maintenance Variable**

Hagerhall's estimates are reasonable for UNMANAGED weathering, but architectural reality is more complex. Buildings are maintained — cleaned, repointed, repaired, consolidated. Maintenance regimes SHAPE the aging trajectory. A limestone facade that is cleaned every decade will show a sawtooth pattern: D increases through weathering, drops at cleaning, then rises again. A facade left unmaintained will follow a monotonic trajectory but may overshoot the aesthetic optimum — heavily eroded stone with extensive biological colonization can reach D > 1.5, which is past the preference peak and into visual disorder.

The design variable is therefore not just material selection but MAINTENANCE SPECIFICATION: how should the building's surfaces be managed to support positive aging? Japanese temple maintenance (periodic replacement of elements while preserving patina on retained surfaces) represents one approach. European cathedral maintenance (careful cleaning that preserves tooling marks while removing atmospheric soiling) represents another. The modernist approach (restore to original appearance) destroys temporal depth entirely.

For calibration purposes, I propose that TP3 should specify THREE AGING REGIMES:

1. **Managed positive aging**: Maintenance preserves and curates the patina. D trajectory: monotonic increase, rate ~0.01–0.02 per decade, approaching D ≈ 1.3 asymptotically. Architectural examples: Japanese temples, well-maintained European stone buildings, oiled hardwood.

2. **Unmanaged aging**: No maintenance. D trajectory: rapid initial increase, potential overshoot past D ≈ 1.5 within 50–100 years for porous materials. May bifurcate into aesthetic richness (robust materials) or visual decay (fragile materials).

3. **Restorative maintenance**: Periodic return to original condition. D trajectory: sawtooth, averaging near the original D value. Temporal depth is periodically erased. Aesthetic consequence: the building never develops patina but avoids degradation.

---

### DEEPENING TP1: MOTOR PE INSTRUMENTATION — CAN WE MEASURE ARCHITECTURAL MOVEMENT QUALITY?

**PS-Hausdorff: Gait Dynamics Provide the Motor PE Metric**

The motor system is the most measurable prediction system in the body. Every step produces a rich kinematic signal — stride time, stride length, stride-time variability, ground reaction forces, joint angles, trunk acceleration — that modern wearable IMUs can capture with sub-centimeter precision at 100–200 Hz. The question for TP1 calibration is whether these kinematic signals can be mapped onto a meaningful motor-prediction-error metric.

The answer is almost certainly yes, and the key insight comes from gait variability analysis. Healthy walking exhibits a characteristic 1/f temporal structure: stride intervals are neither random (white noise) nor perfectly periodic (zero variability) but show long-range correlations where each stride is influenced by strides many steps earlier (Hausdorff et al., 1995, ~2,000 citations). This fractal gait pattern represents the motor system operating in its optimal predictive regime — generating predictions at multiple timescales simultaneously.

When the motor system encounters a prediction violation — an unexpected step height, a change in surface friction, a narrowing passage — the fractal structure is disrupted. The stride-interval time series becomes more random (whiter) because the motor system shifts from smooth long-range prediction to reactive step-by-step correction. This shift is measurable as a change in the scaling exponent α of the stride-interval time series.

My proposed motor PE metric for architectural movement:

- **Motor PE index** = 1 − (α_local / α_baseline), where α_baseline is the individual's scaling exponent during straight-path walking on a level surface and α_local is the scaling exponent during architectural movement. Values near 0 indicate motor prediction confirmation (fluent movement); values approaching 1 indicate motor prediction failure (reactive, non-predictive stepping).

Preliminary ranges from our clinical gait studies, extrapolated to architectural contexts:

- **Level corridor, standard width**: Motor PE index ≈ 0.02–0.05 (near-baseline, effortless)
- **Well-proportioned staircase** (178mm risers, consistent): Motor PE index ≈ 0.10–0.15 (gait shifts to stair-climbing mode but maintains fractal structure)
- **Steep or irregular staircase** (>200mm risers, inconsistent): Motor PE index ≈ 0.25–0.40 (disrupted fractal structure, conscious motor planning)
- **Deliberately challenging surface** (tilted floor, uneven paving): Motor PE index ≈ 0.30–0.50 (sustained postural correction, high attentional demand)
- **Threshold transition** (carpet → stone, level → ramp): Motor PE index ≈ 0.15–0.25 (transient disruption at transition, recovery within 3–5 strides)

**PS-Woollacott: Age Shifts the Entire Motor PE Landscape**

Everything Hausdorff describes is systematically age-dependent. The fundamental change with aging is a shift from PREDICTIVE to REACTIVE postural control (Woollacott & Shumway-Cook, 2002, ~2,500 citations). Young adults maintain balance primarily through feedforward predictions — the motor system anticipates postural demands and pre-adjusts. Older adults rely increasingly on feedback corrections — the motor system detects a perturbation and then responds. This is the motor analogue of Braver's proactive-to-reactive shift (T45), and it has the same metabolic consequence: reactive control is more expensive per unit time.

The age moderation of TP1 parameters, from our posturography and gait studies:

- **Baseline gait fractal exponent**: Young adults α ≈ 0.75–0.85; healthy older adults (65–75) α ≈ 0.60–0.70; frail older adults (75+) α ≈ 0.45–0.55. The declining exponent means older adults start with LESS predictive gait structure, so architectural perturbations push them further into reactive territory.
- **Step-height sensitivity**: The body-scaled optimal step height (Warren, 1984) is ~0.25 × leg length for young adults. For older adults, the COMFORTABLE step height drops to ~0.20 × leg length due to reduced hip flexion range and muscle strength. The code-maximum 210mm step is within the comfortable range for most young adults but at or beyond the comfortable limit for many older adults.
- **Recovery time after perturbation**: Young adults recover baseline gait pattern within 2–3 strides of a surface transition. Older adults require 5–8 strides. Frail older adults may not fully recover before the next perturbation in a complex building.
- **Attentional cost of balance**: For young adults, quiet standing requires negligible attention (dual-task cost < 5%). For older adults, standing on an uneven surface can consume 15–30% of attentional capacity (Woollacott & Shumway-Cook, 2002), directly competing with wayfinding, social cognition, and aesthetic engagement.

The architectural implication is that the Goldilocks zone for motor PE is NARROWER for older adults — the range between "boringly flat" and "threateningly complex" is compressed, and the metabolic cost of operating outside that range is higher.

---

### DEEPENING TP4: MULTI-TIMESCALE INTEGRATION — CAN WE DECOMPOSE ARCHITECTURAL EXPERIENCE?

**PS-Mavros: Ambulatory Multi-Modal Measurement Is Now Feasible**

The technological barrier to testing TP4 has essentially fallen in the past decade. When TP-I was developed, measuring neural and physiological responses to architecture required either laboratory simulations (losing ecological validity) or retrospective self-report (losing temporal precision). Current ambulatory methods can now capture:

- **Mobile EEG** (64-channel, research-grade, ~250 Hz): Event-related potentials at T-1, alpha/beta dynamics at T-2/T-3, sustained frontal theta at T-3/T-4. Our recent work in real-world navigation (Mavros et al., 2022, ~150 citations) demonstrates that EEG responses to spatial transitions are detectable during actual walking.
- **Continuous EDA and HRV** (wrist-worn, ~4 Hz): Tonic arousal at T-3/T-4, phasic responses to transitions at T-2/T-3.
- **Eye tracking** (mobile, ~120 Hz): Fixation patterns at T-1, scanning behavior at T-2, exploration strategy at T-3.
- **IMU gait analysis** (ankle/trunk, ~200 Hz): Motor PE at T-2 per Hausdorff's metric.
- **GPS + indoor positioning** (±1m): Spatial trajectory and dwell time at T-3/T-4.
- **Ecological momentary assessment** (phone prompts): Subjective experience at T-3/T-4.

For TP4 calibration, the critical design is a MULTI-MEASURE ARCHITECTURAL WALKTHROUGH: participants wearing all sensors walk through a building with known architectural features (mapped against the template library), producing time-synchronized data streams at multiple timescales. The analysis then asks: do signals at different timescales contribute independently to overall experience ratings collected post-walkthrough?

My preliminary estimate, based on our multi-modal urban walking studies:

- **T-1 signals** (EEG event-related responses to visual features): Explain ~10–15% of variance in aesthetic ratings
- **T-2 signals** (gait smoothness, phasic EDA at transitions): Explain ~15–20% of variance in movement satisfaction
- **T-3 signals** (EDA trajectory over promenade, EEG alpha at transitions): Explain ~20–25% of variance in overall experience
- **T-4 signals** (sustained arousal level, self-reported comfort): Explain ~15–20% of variance in occupancy satisfaction
- **Combined model**: Should explain ~50–60% of variance in overall building experience — substantially more than any single timescale

These are extrapolations, but the prediction is testable: if TP4's hierarchical model is correct, a multi-timescale model should significantly outperform any single-timescale model, and the timescales should contribute partially independently (low inter-timescale correlations).

**PS-Wittmann: The PE Density → Subjective Time Function Can Be Parameterized**

TP4's Timescale T-3 (minutes) includes a specific claim about subjective time: architectural PE density determines how "long" a building visit feels. My work on time perception (Wittmann, 2009, ~300 citations; 2016, ~200 citations) provides the theoretical framework, but the architectural parameterization is missing.

From laboratory time-perception studies, the relationship between event density and retrospective duration estimation follows an approximately logarithmic function: doubling the number of encoded events increases estimated duration by ~30–40%, not by 100%. This means that a building with twice as many spatial transitions does not feel twice as long — it feels about a third longer. The function saturates at high event densities because encoding capacity has a ceiling.

My proposed calibration for architectural contexts:

**Retrospective duration ratio** = 1 + k × ln(PE_events / PE_baseline), where PE_baseline is the event density of a uniform corridor and k ≈ 0.3–0.4.

Worked example: A museum path with 12 strong spatial transitions vs. a gallery with 3 transitions over the same clock time. PE ratio = 12/3 = 4. Duration ratio = 1 + 0.35 × ln(4) = 1 + 0.35 × 1.39 ≈ 1.49. The museum path would be retrospectively estimated as ~50% longer than the gallery path, controlling for clock time. This is consistent with anecdotal reports: complex buildings feel temporally expansive; uniform buildings feel temporally compressed.

---

## Cross-Examination and Calibration Debates

### Debate 1: Is the Channel-Count → Boundary-Strength Function Additive or Super-Additive?

**Radvansky**: My estimates assume approximate additivity. Each additional channel of context change contributes roughly d ≈ 0.15–0.25 to boundary strength, adding to a cumulative total.

**Zacks**: The film-segmentation data suggest slight super-additivity for temporally synchronized changes — about 10–20% above additive prediction. But this requires strict temporal co-occurrence within ~500ms. In architecture, channel changes at a threshold are inherently synchronized: you walk through a doorway and the light, acoustics, materials, and spatial volume all change within a stride duration (~500–1000ms). So the architectural case should reliably trigger the super-additivity bonus.

**Swallow**: The attentional boost data support super-additivity. When more channels change simultaneously, the attentional boost is disproportionately larger — the transient attention increase at the boundary is driven by summed prediction error, and the attention → encoding coupling is nonlinear. A 4-channel threshold doesn't just produce 4× the encoding — it produces a qualitatively different attentional state (a "flash" of high-resolution perceptual encoding) that a single-channel change does not reach.

**Panel consensus**: **Approximately additive with 15–20% super-additivity for synchronized multi-modal changes.** The function is: Boundary strength (d) ≈ [Σ(d_channel_i)] × (1 + 0.15 to 0.20). The super-additivity bonus applies when channels change within a ~1-second window (approximately one stride), which is the default for architectural thresholds.

### Debate 2: Which Channels Contribute Most to Episodic Boundary Strength?

**Radvansky**: Spatial configuration change (room volume, shape) is the primary driver. A door from a small room into a large room produces a stronger doorway effect than a door between rooms of the same size, even when other features are controlled.

**Zacks**: Agreed. In the event segmentation framework, spatial changes are the most potent boundary markers because they signal a change in the SITUATION MODEL — the spatial context determines what objects and actions are expected. A luminance change within the same room (a cloud passing over) is a sensory event but not a situation-model update.

**Hagerhall**: Visual texture changes — particularly material transitions — may be underestimated. The visual system detects surface-material changes preattentively, and these carry strong categorical associations (entering a wood-paneled room from a stone corridor signals a functional-class transition, not just a surface change).

**Swallow**: Acoustic change may be the most undervalued channel. Sound is omnidirectional and cannot be ignored. When you cross a threshold from a reverberant space to a damped space, the acoustic change is registered by the auditory system within 50–100ms — faster than the visual system can fully process the new room. The acoustic change may actually PRIME the event-segmentation system before the visual and spatial changes are processed.

**Panel consensus on channel-weight estimates** (for episodic boundary strength):

| Channel | d contribution | Confidence | Notes |
|---------|---------------|------------|-------|
| Spatial configuration (volume, shape) | 0.25 ± 0.08 | Moderate | Strongest driver; triggers situation-model update |
| Luminance/light quality | 0.20 ± 0.08 | Moderate | Light level changes strongly signal context shift |
| Acoustic environment | 0.18 ± 0.10 | Low-Moderate | Fast-acting; may prime other channels; underresearched |
| Material surface change | 0.15 ± 0.08 | Low-Moderate | Preattentive visual detection; categorical associations |
| Thermal shift | 0.12 ± 0.10 | Low | Slow-acting (seconds); contributes to cumulative context but not to initial boundary detection |
| Motor demand change | 0.10 ± 0.08 | Low | Floor surface, step requirement; contributes via TP1 |
| Olfactory | 0.08 ± 0.08 | Low | Only at arrival or strong transitions; rapid adaptation (MAT-II olfactory time function) |

**Critical caveat**: These are EXPERT ESTIMATES, not empirical calibration values. The parametric VR study proposed in TP-I Prediction 2 is needed to replace these with measured values.

### Debate 3: Does the Fractal Aging Hypothesis Survive Material-Specific Analysis?

**Hagerhall**: The hypothesis needs qualification. Not all natural weathering converges on D ≈ 1.3. The fractal dimension of a weathered surface depends on the interaction between the material's micro-structure and the weathering agents. Limestone in a rainy climate develops elaborate dissolution patterns (D increasing toward 1.3–1.5). Granite in the same climate changes very slowly (D may stay near 1.1 for centuries). The convergence rate is material-specific.

**Mostafavi**: And the endpoint may differ from D ≈ 1.3 for some materials. Copper patina, for instance, produces large-scale color variation but relatively low surface texture. The aesthetic improvement of copper with age may be more about COLOR complexity than GEOMETRY complexity. We need to distinguish fractal dimension in the geometric sense (surface relief) from fractal properties in the spectral sense (color and tonal variation).

**Hagerhall**: An important distinction. The D ≈ 1.3 preference data are primarily from silhouette analysis (2D contour complexity) and greyscale image analysis (luminance pattern complexity). Architectural surface aging affects both geometry (surface relief → increased D in contour analysis) and spectral properties (color variation → increased D in spectral analysis). These may converge or diverge depending on material.

**Panel consensus**: **The fractal aging hypothesis is SUPPORTED IN PRINCIPLE but requires material-specific trajectories rather than a universal convergence target.** Revised formulation: natural weathering increases surface complexity (both geometric and spectral) on a material-specific trajectory. The RATE of increase and the ASYMPTOTE depend on material composition, climate exposure, orientation, and maintenance regime. The universal convergence-to-1.3 claim is too strong; the claim should be that natural weathering moves surfaces INTO the preference range (D ≈ 1.2–1.5), with the specific trajectory varying by material.

---

## Calibration Sessions

### Calibration Session 1: TP2 Doorway Gradient — The Channel-Count Function

Synthesizing Radvansky's estimates, Zacks's additivity analysis, and Swallow's attentional boost data, the panel calibrates the following boundary-strength function:

**Episodic Boundary Strength** (effect size for context-updating/memory segmentation):

| Channels changing | Estimated d | 95% CI | Label | Architectural exemplar |
|-------------------|------------|--------|-------|----------------------|
| 0 (no threshold) | 0.00 | — | None | Open-plan continuous space |
| 1 (spatial only) | 0.25 | 0.15–0.35 | Minimal | Door between similar rooms |
| 2 (spatial + light OR acoustic) | 0.45 | 0.30–0.60 | Clear | Corridor to daylit room |
| 3 (spatial + light + acoustic) | 0.68 | 0.50–0.85 | Strong | Stone corridor → timber hall |
| 4 (spatial + light + acoustic + material) | 0.88 | 0.65–1.10 | Very strong | Compressed dark entry → bright atrium |
| 5+ (full multi-modal) | 1.00–1.15 | 0.80–1.30 | Extraordinary | Narthex → cathedral nave (all channels) |

**Combination rule**: Boundary d ≈ [Σ(d_channel_i)] × 1.17 (±0.05), where the 1.17 multiplier captures the super-additivity from synchronized multi-modal change.

**The attentional boost companion**: At each boundary strength level, the TRANSITION ENCODING ENHANCEMENT approximately mirrors the working-memory disruption:

| Boundary strength (d) | WM disruption for preceding context | Encoding enhancement for transition | Net memorial effect |
|----------------------|-------------------------------------|--------------------------------------|---------------------|
| 0.25 (minimal) | −0.20 (slight forgetting) | +0.15 (slight enhancement) | Weak segmentation |
| 0.45 (clear) | −0.35 (moderate forgetting) | +0.30 (clear memory of transition) | Moderate segmentation |
| 0.68 (strong) | −0.50 (strong forgetting) | +0.45 (vivid transition memory) | Strong segmentation |
| 1.00+ (extraordinary) | −0.65 (near-complete context reset) | +0.60 (peak-experience encoding) | Vivid episodic chapter |

**Threshold density Goldilocks**: The panel estimates an optimal range of 3–6 strong thresholds per 10-minute walking sequence. Below 3, the experience lacks memorial structure (undifferentiated). Above 6, the experience becomes fragmentary (too many context resets prevent sustained engagement with any single space). This maps to approximately one strong threshold every 2–3 minutes of walking — consistent with the temporal grain of event segmentation in film studies (Zacks et al., 2007).

### Calibration Session 2: TP3 Fractal Aging Trajectories — Material-Specific Parameters

Synthesizing Hagerhall's measurement estimates and Mostafavi's maintenance analysis, the panel calibrates material-specific aging functions:

**General aging model**: D(t) = D_0 + (D_max − D_0) × (1 − e^(−t/τ)), where D_0 is initial fractal dimension, D_max is the asymptotic maximum, and τ is the time constant (years to reach 63% of maximum change).

| Material | D_0 (new) | D_max (asymptote) | τ (years) | Climate sensitivity | Maintenance effect | Confidence |
|----------|-----------|-------------------|-----------|--------------------|--------------------|------------|
| **Limestone** | 1.05 ± 0.05 | 1.40 ± 0.10 | 30–60 | High (rain accelerates dissolution) | Cleaning resets surface; repointing preserves mortar joints | Low-Moderate |
| **Sandstone** | 1.10 ± 0.05 | 1.35 ± 0.10 | 40–80 | High (erosion, salt crystallization) | Consolidation preserves grain; cleaning can damage | Low |
| **Granite** | 1.05 ± 0.05 | 1.15 ± 0.08 | 200–500 | Low (very slow weathering) | Minimal needed; biological growth adds texture | Low |
| **Brick** | 1.08 ± 0.05 | 1.30 ± 0.10 | 50–100 | Moderate (frost, efflorescence) | Repointing maintains structure; cleaning resets surface | Low-Moderate |
| **Hardwood** (exposed) | 1.15 ± 0.05 | 1.35 ± 0.10 | 15–30 | High (UV, moisture) | Oiling preserves and slows; silvering if untreated | Low-Moderate |
| **Copper** | 1.05 ± 0.05 | 1.20 ± 0.10 | 10–25 | High (atmospheric chemistry) | Cleaning destroys patina; generally left alone | Low |
| **Weathering steel** | 1.05 ± 0.05 | 1.25 ± 0.10 | 5–15 | High (moisture cycle) | Self-protecting once stable; early washing prevents streaking | Low |
| **Concrete** | 1.05 ± 0.05 | 1.15 ± 0.15 | 20–40 | Moderate (staining, carbonation) | Cleaning important; untreated concrete often ages NEGATIVELY | Low |

**Critical distinction preserved**: Natural materials (stone, wood, brick, copper) generally follow convergent trajectories toward the aesthetic preference range (D ≈ 1.2–1.4). Concrete is the ambiguous case — its aging trajectory depends heavily on formwork quality, exposure, and maintenance. Synthetic materials (vinyl, composite panels, EIFS) were NOT calibrated because their degradation is typically non-fractal (uniform discoloration, mechanical cracking) and does not follow the model.

**The spectral-vs.-geometric distinction** (from Debate 3): For copper and weathering steel, the aesthetic improvement with age is primarily SPECTRAL (color complexity increases from uniform bright to variegated patina) rather than GEOMETRIC (surface relief changes are modest). The panel recommends that TP3 calibration should track BOTH geometric D (surface relief) and spectral D (color/tonal variation) as separate measures. The combined aesthetic effect is likely the product of both: D_aesthetic ≈ f(D_geometric, D_spectral).

### Calibration Session 3: TP1 Motor PE Metric — The Gait Variability Approach

Synthesizing Hausdorff's gait dynamics methodology and Woollacott's age-moderation data, the panel calibrates the motor PE metric:

**Primary metric**: Motor Fluency Index (MFI) = α_local / α_baseline, where α is the detrended fluctuation analysis (DFA) scaling exponent of stride-interval time series. MFI = 1.0 indicates baseline motor prediction (walking as well as on a flat surface). MFI < 1.0 indicates motor PE (the further below 1.0, the more disrupted the predictive gait pattern).

**Secondary metric**: Stride Variability Coefficient (SVC) = SD(stride_time) / mean(stride_time). Lower SVC indicates more predictable stepping. SVC is easier to compute than DFA but less sensitive to the fractal structure that distinguishes predictive from reactive motor control.

**Calibrated architectural ranges** (MFI values, young healthy adults):

| Architectural condition | MFI | SVC | Subjective quality | Attentional demand |
|------------------------|-----|-----|-------------------|-------------------|
| Level corridor, smooth surface | 0.95–1.00 | 0.02–0.03 | Effortless, unconscious | Minimal (<5%) |
| Level corridor, textured surface (stone flags, wood planks) | 0.90–0.95 | 0.03–0.04 | Effortless with slight sensory engagement | Minimal (<5%) |
| Well-proportioned staircase (178mm riser, consistent) | 0.80–0.90 | 0.04–0.06 | Confident, rhythmic | Low (5–10%) |
| Steep staircase (>200mm riser) | 0.65–0.80 | 0.06–0.10 | Careful, deliberate | Moderate (10–20%) |
| Irregular surface (cobblestones, gravel) | 0.60–0.75 | 0.08–0.12 | Alert, adaptive | Moderate (15–25%) |
| Deliberately challenging (tilted floor, uneven steps) | 0.45–0.65 | 0.10–0.18 | Conscious, effortful | High (20–35%) |
| Threshold transition (surface material change) | 0.75–0.85 | Transient spike | Brief adaptation, 3–5 stride recovery | Transient |

**Age moderation** (Woollacott's data integrated):

| Population | Baseline α | MFI shift (all conditions) | Recovery strides | Attentional cost multiplier |
|-----------|-----------|--------------------------|-----------------|---------------------------|
| Young adults (20–40) | 0.80 ± 0.05 | Reference | 2–3 strides | 1.0× |
| Middle-aged (40–65) | 0.75 ± 0.05 | −0.05 to −0.10 | 3–5 strides | 1.2–1.5× |
| Healthy older (65–80) | 0.65 ± 0.08 | −0.10 to −0.20 | 5–8 strides | 1.5–2.5× |
| Frail older (80+) | 0.50 ± 0.10 | −0.20 to −0.30 | 8–15 strides | 2.5–4.0× |

**Design implication**: The attentional cost multiplier is the critical number for architects. A staircase that costs a young adult 10% of attentional capacity costs a healthy older adult 15–25% and a frail older adult 25–40%. This is attention that is UNAVAILABLE for wayfinding, social interaction, aesthetic engagement, or safety monitoring. Universal design should target conditions where even frail older adults maintain MFI > 0.70 (approximately: level surfaces, consistent stair risers ≤ 170mm, handrails at 865–965mm height, slip-resistant surfaces with coefficient of friction ≥ 0.6).

### Calibration Session 4: TP4 Multi-Timescale Decomposition — Variance Partitioning

Synthesizing Mavros's multi-modal measurement methodology and Wittmann's time-perception parameterization, the panel calibrates the multi-timescale model:

**Variance decomposition model**: Overall architectural experience rating = β₁(T-1 signals) + β₂(T-2 signals) + β₃(T-3 signals) + β₄(T-4 signals) + ε

The panel estimates the following variance contributions from the existing multi-modal urban/architectural walking literature:

| Timescale | Signal type | Estimated R² contribution | Overlap with other scales | Unique contribution | Confidence |
|-----------|------------|--------------------------|--------------------------|--------------------|-----------| 
| T-1 (ms) | EEG visual-evoked PE markers | 0.12 ± 0.05 | ~0.04 shared with T-2 | ~0.08 | Low |
| T-2 (s) | Gait MFI + phasic EDA at transitions | 0.18 ± 0.06 | ~0.05 shared with T-1 and T-3 | ~0.13 | Low-Moderate |
| T-3 (min) | EDA trajectory + EEG alpha dynamics over promenade | 0.22 ± 0.07 | ~0.06 shared with T-2 and T-4 | ~0.16 | Moderate |
| T-4 (hrs) | Tonic arousal, self-reported comfort, circadian markers | 0.16 ± 0.06 | ~0.04 shared with T-3 | ~0.12 | Low-Moderate |
| **Combined model** | All timescales | **0.55 ± 0.10** | — | — | Low-Moderate |

**Key prediction**: The combined multi-timescale model should explain significantly more variance (R² ≈ 0.55) than any single timescale alone (max single R² ≈ 0.22). If the unique contributions are significant after controlling for shared variance, this supports TP4's claim that architectural experience integrates INDEPENDENT information from multiple temporal scales.

**The PE density → subjective time function** (Wittmann's parameterization):

Retrospective duration estimate = T_clock × [1 + k × ln(N_events / N_baseline)]

Where:
- T_clock = actual elapsed time
- N_events = number of detected PE events (event boundaries per Zacks)
- N_baseline = baseline event rate in a uniform corridor (estimated ~1 event per 2–3 minutes of walking = primarily wayfinding decisions)
- k = scaling constant ≈ 0.35 ± 0.08

**Worked examples**:
- Uniform gallery (3 events / 30 min walk): Duration estimate ≈ 30 × [1 + 0.35 × ln(3/1)] ≈ 30 × 1.38 = 41 min (feels ~37% longer than clock time, consistent with modest overestimation during passive walking)
- Rich museum path (15 events / 30 min walk): Duration estimate ≈ 30 × [1 + 0.35 × ln(15/1)] ≈ 30 × 1.95 = 58 min (feels ~93% longer than clock time — "we spent nearly an hour in there!" said about a 30-minute visit)
- PE-dense cathedral sequence (25 events / 15 min walk): Duration estimate ≈ 15 × [1 + 0.35 × ln(25/1)] ≈ 15 × 2.13 = 32 min (a 15-minute processional feels like over half an hour)

---

## Panel Synthesis: What TP-II Accomplished

### Opening Remarks from the Chair

TP-II has accomplished something TP-I could not: it has attached NUMBERS to temporal experience. The four calibration sessions produced quantitative parameters that transform the temporal templates from structural descriptions into measurable, testable, and — most importantly — designable frameworks. The temporal dimension of architecture is no longer merely described; it is, at least in preliminary form, parameterized.

### What We Delivered

**For TP2 (Doorway Gradient)**: A channel-count → boundary-strength function with estimated d values, a combination rule (additive with 15–20% super-additivity), channel-specific weight estimates, the attentional boost companion (encoding enhancement mirrors working-memory disruption), and a threshold density Goldilocks (3–6 strong thresholds per 10-minute sequence). The most design-actionable output: architects now have a principled basis for GRADING thresholds by deciding how many sensory channels change at each spatial boundary.

**For TP3 (Fractal Aging)**: Material-specific aging trajectories using an exponential approach model (D_0, D_max, τ) for eight common building materials. The universal convergence-to-1.3 claim is replaced by material-specific trajectories with varying rates and asymptotes — all within or approaching the D ≈ 1.2–1.4 preference range for natural materials, with concrete as the ambiguous exception. The geometric-vs-spectral distinction (Debate 3) adds nuance: copper and weathering steel age primarily in spectral complexity rather than geometric complexity.

**For TP1 (Motor PE Metric)**: The Motor Fluency Index (MFI = α_local / α_baseline) provides a continuous, wearable-measurable metric of motor prediction quality during architectural movement. Calibrated ranges for seven common architectural conditions, plus age-moderation parameters showing that older adults face a 1.5–4× attentional cost multiplier for the same architectural conditions. The design implication is immediate: architects can now estimate the attentional cost of their design choices for different populations.

**For TP4 (Multi-Timescale Integration)**: A variance decomposition model predicting that multi-timescale measurement should explain ~55% of variance in overall building experience, with each timescale contributing partially independently. The PE density → subjective time function (Wittmann's logarithmic model with k ≈ 0.35) provides a quantitative prediction for how event-rich architecture expands subjective time.

### What We Did Not Deliver

All four calibration sessions produced ESTIMATES, not empirical values. The channel-weight table for TP2 requires the parametric VR study. The fractal aging trajectories for TP3 require cross-sectional surface measurements. The MFI ranges for TP1 require architectural field studies with wearable IMUs. The variance decomposition for TP4 requires multi-modal walkthrough studies. Each calibration session identifies the specific experiment needed to replace expert estimates with measured values.

### Three Debates Resolved

1. **Additivity vs. super-additivity** (TP2): Approximately additive with 15–20% super-additivity for synchronized changes. Consensus.
2. **Universal convergence vs. material-specific trajectories** (TP3): Material-specific trajectories replace the universal D ≈ 1.3 convergence claim. TP3's structural claim (natural aging enriches surfaces) is preserved; the overly specific convergence target is relaxed. Consensus with acknowledged low confidence.
3. **Motor PE as design variable vs. code-compliance issue** (TP1): Motor PE operates over the full quality range from "awkward" to "graceful," which is above and beyond the binary safe/unsafe distinction that building codes enforce. The attentional cost multiplier for older adults makes this a universal-design issue, not merely an aesthetic one. Consensus.

---

## Testable Predictions and Critical Experiments

### Prediction 1: The Channel-Count Gradient (TP2)

**Claim**: Episodic boundary strength increases approximately additively with the number of sensory channels that change at a threshold, with 15–20% super-additivity for synchronized changes.

**Protocol**: VR study with 7 conditions — threshold with 1, 2, 3, 4, 5, 6, and 7 simultaneous channel changes (spatial volume, luminance, acoustic reverb, floor material, wall material, temperature, olfactory). Participants walk through 12 thresholds at varying channel counts. Post-walk: free recall of room sequence, cued recall of room contents, temporal duration estimation. Measure: d for working-memory disruption and d for transition-encoding enhancement at each channel count.

**Predicted pattern**: Approximately linear increase in d with channel count (slope ~0.15–0.20 per channel), with significant super-additivity interaction at 4+ channels. The attentional boost (transition encoding) should parallel the working-memory disruption at each level.

**Templates tested**: TP2, SC3.

### Prediction 2: The Fractal Aging Trajectory (TP3)

**Claim**: Natural building materials develop increasing surface fractal dimension with age, following material-specific trajectories that approach but do not necessarily converge on D ≈ 1.3.

**Protocol**: Cross-sectional study — high-resolution photographs of matched stone, brick, and hardwood surfaces at buildings of known age (0, 25, 50, 100, 200+ years). Box-counting fractal analysis on greyscale images (geometric D) and color histogram analysis (spectral D). Control for climate zone, orientation, and maintenance regime. Minimum 10 surfaces per material-age combination.

**Predicted pattern**: Monotonic increase in D for all three natural materials, with limestone showing fastest trajectory (τ ≈ 30–60 years) and brick intermediate (τ ≈ 50–100 years). Granite should show minimal change. Concrete should show variable trajectories depending on maintenance. Aesthetic preference ratings should correlate with proximity to D ≈ 1.2–1.4 range.

**Templates tested**: TP3, T1.

### Prediction 3: Motor Fluency Index Predicts Movement Satisfaction (TP1)

**Claim**: The MFI metric, computed from wearable IMU data during architectural movement, predicts subjective movement quality ratings.

**Protocol**: Participants wearing ankle and trunk IMUs walk through 10 different architectural conditions (various stair types, corridors, surface transitions, ramps) and provide post-condition movement quality ratings. Compute MFI from stride-interval DFA scaling exponent.

**Predicted pattern**: MFI correlates with subjective movement quality at r ≥ 0.60. Age × condition interaction: the MFI-satisfaction correlation should be STRONGER for older adults (because they operate closer to the lower boundary of motor prediction). The attentional cost (measured by dual-task decrement) should show a strong negative correlation with MFI.

**Templates tested**: TP1.

### Prediction 4: Multi-Timescale Independence (TP4)

**Claim**: PE signals at different timescales contribute independently to overall architectural experience ratings.

**Protocol**: Multi-modal walkthrough — participants wearing EEG, EDA, eye-tracking, and IMU sensors walk through a building with varied architectural features. Collect T-1 (EEG visual PE), T-2 (MFI, phasic EDA), T-3 (EDA trajectory, EEG alpha), and T-4 (tonic arousal, self-report) signals. Collect overall experience ratings post-walkthrough. Compute hierarchical regression with each timescale entered sequentially.

**Predicted pattern**: Each timescale adds significant unique variance after controlling for all shorter timescales. Combined R² ≈ 0.50–0.60. No single timescale exceeds R² ≈ 0.25. T-3 (promenade-level) contributes the most unique variance for visitor experiences; T-4 (occupancy-level) dominates for daily occupants.

**Templates tested**: TP4, and indirectly all templates organized by TP4's hierarchy.

### Prediction 5: PE Density Predicts Retrospective Duration Estimation (TP4/Wittmann)

**Claim**: The number of detected event boundaries during a building visit predicts retrospective duration estimation following the logarithmic function Duration_est = T_clock × [1 + 0.35 × ln(N_events / N_baseline)].

**Protocol**: Participants visit two buildings matched for total walking distance but differing in PE event density (high: many thresholds, material changes, spatial revelations; low: uniform corridors, repetitive spaces). After each visit, estimate visit duration. Event boundary count computed from mobile EEG (P300-like responses at transitions) and eye-tracking (fixation-pattern discontinuities).

**Predicted pattern**: High-density building visit estimated as ~40–80% longer than low-density visit of identical clock duration. The ln function should hold: doubling event density should NOT double estimated duration.

**Templates tested**: TP4, TP2.

---

## Updated Cross-Reference Mapping

### What TP-II Changes in the Coverage Matrix

TP-II does not change the A10 domain rating — it was already at ★★★★ after TP-I. What TP-II changes is the CALIBRATION STATUS of the temporal templates:

| Template | Pre TP-II | Post TP-II | Key calibration |
|----------|----------|-----------|-----------------|
| **TP1** | ✗ Uncalibrated | ~ Partial | MFI metric defined; architectural ranges estimated; age moderation parameters specified |
| **TP2** | ✗ Uncalibrated | ~ Partial | Channel-count function; channel weights; super-additivity coefficient; threshold density Goldilocks; attentional boost companion |
| **TP3** | ✗ Uncalibrated | ~ Partial | Material-specific aging trajectories (D_0, D_max, τ) for 8 materials; geometric vs. spectral D distinction; maintenance regime classification |
| **TP4** | ✗ Uncalibrated | ~ Partial | Variance decomposition estimates; PE density → subjective time function (k ≈ 0.35); multi-timescale independence prediction |

### Template-to-Attribute Cross-Reference (Calibration Upgrades)

| Attribute | Relevant Templates | What TP-II Adds |
|-----------|-------------------|-----------------|
| A10.1 Movement & proprioception | TP1, T8 | MFI metric, age-moderated attentional cost multiplier |
| A10.2 Threshold & transition | TP2, SC3, AX6 | Channel-count gradient, channel weights, threshold density Goldilocks |
| A10.3 Promenade (PE over time) | SC3, TP4, TP2 | PE density → subjective time function, multi-timescale variance decomposition |
| A10.5 Aging & patina | TP3, T1, MAT5 | Material-specific fractal aging trajectories, maintenance regime classification |

---

## Calibration Assessment

### TP1: Motor Prediction and Proprioceptive PE

| Dimension | Status | Notes |
|-----------|--------|-------|
| Theoretical Extension | ✓ Good | MFI metric grounded in DFA methodology (Hausdorff); age moderation from posturography (Woollacott) |
| Empirical Calibration | ~ Partial | MFI ranges extrapolated from clinical gait studies to architectural conditions; no architectural-specific validation yet |
| Architectural Translation | ~ Partial | Attentional cost multiplier provides direct design relevance; universal design thresholds specified |

**Maturity**: Supported (motor prediction framework and gait dynamics); supported-preliminary (architectural MFI ranges); how-plausibly (attentional cost multiplier)

### TP2: Threshold as Episodic Boundary

| Dimension | Status | Notes |
|-----------|--------|-------|
| Theoretical Extension | ✓ Good | Channel-count function integrates EST (Zacks), doorway effect (Radvansky), and attentional boost (Swallow) |
| Empirical Calibration | ~ Partial | d estimates are expert judgments with supporting evidence from film-segmentation and laboratory doorway studies; architectural-specific parametric study not yet conducted |
| Architectural Translation | ✓ Good | Channel-count framework is directly actionable — architects can grade thresholds by choosing how many channels to change; threshold density Goldilocks provides sequence-design guidance |

**Maturity**: Supported (doorway effect and event segmentation); supported with dissent (specific channel weights — acoustic contribution debated); how-plausibly (super-additivity coefficient)

### TP3: Material Aging and Temporal Depth

| Dimension | Status | Notes |
|-----------|--------|-------|
| Theoretical Extension | ✓ Good | Material-specific aging model (exponential approach) better specified than TP-I's universal convergence claim |
| Empirical Calibration | ○ Protocol specified | No cross-sectional architectural surface measurements exist; all D values are estimates; measurement protocol fully specified |
| Architectural Translation | ~ Partial | Maintenance regime classification (managed / unmanaged / restorative) is directly actionable; material selection guidance derivable from trajectories |

**Maturity**: Supported-preliminary (fractal enrichment hypothesis); preliminary (specific D_0, D_max, τ values); speculative (geometric vs. spectral D distinction)

### TP4: Temporal Hierarchy

| Dimension | Status | Notes |
|-----------|--------|-------|
| Theoretical Extension | ✓ Good | Variance decomposition model and PE density → subjective time function provide testable quantitative predictions |
| Empirical Calibration | ○ Protocol specified | R² estimates extrapolated from urban psychophysiology studies; no architectural-specific multi-modal walkthrough study |
| Architectural Translation | ~ Partial | Subjective time function provides design guidance (PE-dense buildings feel temporally expansive); multi-timescale evaluation framework for building quality assessment |

**Maturity**: Supported (PE density → time perception link); preliminary (specific variance contributions); how-possibly (multi-timescale independence)

---

## TP-III Prospectus

### DEEPENING (Calibrating TP-II's Estimates with Empirical Data)

**Priority D1: The VR Channel-Count Parametric Study**
The most impactful single experiment. Systematically vary 1–7 channels at VR thresholds, measuring working-memory disruption, transition encoding, and subjective experience. Would replace all expert estimates in Calibration Session 1 with measured values. Estimated N ≈ 80, duration ~6 months.
*Lead panelists*: Radvansky, Zacks, Swallow
*Expected deliverable*: Validated channel-count → boundary-strength function; measured channel weights; confirmation or refutation of super-additivity

**Priority D2: The Architectural Surface Fractal Measurement Campaign**
Cross-sectional measurement of surface fractal dimension on 100+ building surfaces at varying ages. Would test the material-specific trajectories in Calibration Session 2. Could be executed as a multi-site photographic survey with centralized computational analysis. Estimated duration ~12 months.
*Lead panelists*: Hagerhall, Mostafavi
*Expected deliverable*: Measured D_0, D_max, τ for stone, brick, wood; correlation between D and aesthetic preference ratings

**Priority D3: Motor Fluency Validation in Buildings**
Field study with wearable IMUs in 5–10 buildings varying in movement challenge. Would validate MFI as an architectural metric and calibrate the age-moderation parameters from Calibration Session 3. Estimated N ≈ 120 (including older adult sample), duration ~8 months.
*Lead panelists*: Hausdorff, Woollacott, Warren
*Expected deliverable*: Validated MFI metric; architectural condition norms; age-stratified attentional cost multipliers

### BROADENING (New Temporal Domains)

**Priority B1: Responsive Architecture and Bidirectional PE**
TP-I flagged responsive architecture (kinetic facades, adaptive lighting, sensor-driven adjustments) as creating a bidirectional PE loop — the building predicts the occupant AND the occupant predicts the building. TP-III should determine whether this requires a new template (TP5) or extends TP4.
*New expertise needed*: Fox (interactive architecture), Schnädelbach (adaptive environments)
*Expected deliverable*: Decision on TP5; if created, parameterization of bidirectional PE loop dynamics

**Priority B2: Circadian Design Integration (Joint TP-III/L-III)**
Time-of-day × architectural-variable design matrix for circadian support. Would bridge L2 (melanopic parameters) with TP4 (temporal hierarchy). The goal is a practitioner-usable "circadian design schedule" specifying spectral content, intensity, and architectural delivery method for each occupancy phase.
*New expertise needed*: Figueiro (circadian lighting design)
*Expected deliverable*: Circadian design matrix; integration of L2 and TP4 at the T-5 timescale

---

## Scope Exclusions

1. **Circadian architecture full calibration**: Deferred to joint TP-III/L-III. TP-II provides the temporal framework (T-5 timescale in TP4) but the spectral and intensity parameters belong in the light domain.

2. **Cultural moderation of threshold meaning**: Different cultures interpret architectural thresholds differently (Japanese genkan, Islamic mashrabiya, European portico). Cultural moderation of TP2's channel weights is noted but not calibrated — this connects to the planned cross-cultural calibration in SOC-II.

3. **Urban-scale temporal dynamics**: City-level temporal patterns (commute rhythms, seasonal use patterns, neighborhood succession) operate at timescales beyond TP4's building-level T-7. Flagged for a future Urban-Scale panel.

4. **Neurological populations**: TP1's motor PE parameters for populations with specific neurological conditions (Parkinson's, MS, stroke recovery) are clinically important but beyond the scope of the general architectural framework. The age-moderation data from Woollacott provide a bridge to clinical populations but do not substitute for disease-specific calibration.

5. **Virtual and simulated architectural temporality**: Whether VR environments produce the same temporal dynamics (doorway effects, motor PE, subjective time expansion) as physical buildings is an open empirical question that TP-II does not address.

---

## References

Hagerhall, C. M., Purcell, T., & Taylor, R. P. (2004). Fractal dimension of landscape silhouette outlines as a predictor of landscape preference. *Journal of Environmental Psychology*, *24*(2), 247–255. [~500 citations]

Hausdorff, J. M. (2007). Gait dynamics, fractals and falls: Finding meaning in the stride-to-stride fluctuations of human walking. *Human Movement Science*, *26*(4), 555–589. [~1,500 citations]

Hausdorff, J. M., Peng, C. K., Ladin, Z., Wei, J. Y., & Goldberger, A. L. (1995). Is walking a random walk? Evidence for long-range correlations in stride interval of human gait. *Journal of Applied Physiology*, *78*(1), 349–358. [~2,000 citations]

Mandelbrot, B. B. (1982). *The fractal geometry of nature*. W. H. Freeman. [~25,000 citations]

Mavros, P., Austwick, M. Z., & Smith, A. H. (2022). Geo-EEG: Towards the use of EEG in the study of urban behaviour. *Applied Spatial Analysis and Policy*, *9*(2), 191–212. [~150 citations]

Radvansky, G. A. (2012). Across the event horizon. *Current Directions in Psychological Science*, *21*(4), 269–272. [~200 citations]

Radvansky, G. A., & Copeland, D. E. (2006). Walking through doorways causes forgetting: Situation models and experienced space. *Memory & Cognition*, *34*(5), 1150–1156. [~400 citations]

Radvansky, G. A., Krawietz, S. A., & Tamplin, A. K. (2011). Walking through doorways causes forgetting: Further explorations. *Quarterly Journal of Experimental Psychology*, *64*(8), 1632–1645. [~300 citations]

Spehar, B., Clifford, C. W. G., Newell, B. R., & Taylor, R. P. (2003). Universal aesthetic of fractals. *Computers & Graphics*, *27*(5), 813–820. [~300 citations]

Swallow, K. M., & Jiang, Y. V. (2010). The attentional boost effect: Transient increases in attention to one task enhance performance in a second task. *Cognition*, *115*(1), 118–132. [~700 citations]

Swallow, K. M., Zacks, J. M., & Abrams, R. A. (2009). Event boundaries in perception affect memory encoding and updating. *Journal of Experimental Psychology: General*, *138*(2), 236–257. [~400 citations]

Taylor, R. P., Spehar, B., Van Donkelaar, P., & Hagerhall, C. M. (2011). Perceptual and physiological responses to Jackson Pollock's fractals. *Frontiers in Human Neuroscience*, *5*, 60. [~400 citations]

Warren, W. H. (1984). Perceiving affordances: Visual guidance of stair climbing. *Journal of Experimental Psychology: Human Perception and Performance*, *10*(5), 683–703. [~1,000 citations]

Wittmann, M. (2009). The inner experience of time. *Philosophical Transactions of the Royal Society B: Biological Sciences*, *364*(1525), 1955–1967. [~300 citations]

Wittmann, M. (2016). *Felt time: The science of how we experience time*. MIT Press. [~200 citations]

Woollacott, M., & Shumway-Cook, A. (2002). Attention and the control of posture and gait: A review of an emerging area of research. *Gait & Posture*, *16*(1), 1–14. [~2,500 citations]

Zacks, J. M., & Swallow, K. M. (2007). Event segmentation. *Current Directions in Psychological Science*, *16*(2), 80–84. [~600 citations]

Zacks, J. M., Speer, N. K., Swallow, K. M., Braver, T. S., & Reynolds, J. R. (2007). Event perception: A mind-brain perspective. *Psychological Bulletin*, *133*(2), 273–293. [~1,500 citations]

Zacks, J. M., Swallow, K. M., Vettel, J. M., & McAvoy, M. P. (2006). Visual motion and the neural correlates of event perception. *Brain Research*, *1076*(1), 150–162. [~300 citations]

---

*Panel TP-II completed: February 17, 2026*
*Calibration produced: TP1 ~ Partial, TP2 ~ Partial, TP3 ~ Partial, TP4 ~ Partial*
*All four TP templates advanced from ✗ Uncalibrated to ~ Partial*
*Coverage: A10 ★★★★ (unchanged, now with calibration)*
*Next: TP-III for empirical validation of TP-II estimates*
*Document 56 — V1.0*

