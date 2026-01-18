# Comprehensive Summary: Neuroarchitecture Ontology and Rule System Development

## Document Purpose
This document summarizes all discussions and conclusions regarding the development of an ontology and rule system for neuroarchitecture research. It is designed to enable another Claude instance to integrate this work and continue development.

---

## PART I: THE CORE PROBLEM IDENTIFIED

### 1.1 The Ontological Asymmetry Problem

The fundamental concern identified is that **environmental antecedents are relatively homogeneous in ontological type** (physical features, configurations, properties of spaces), while **human consequents constitute a radically heterogeneous ontological zoo** spanning multiple levels of analysis, temporal dynamics, and causal depth.

Current systems (Article Eater, Article Finder) correctly distinguish environmental factors (IVs) from outcomes (DVs), and capture moderators, mediators, SubjectScope, and boundary conditions. **However, they treat all human consequents as ontologically similar**—a "mood change" and a "cognitive map formation" and a "social interaction disposition" are all just "outcomes."

This conflation obscures crucial differences in:
1. **Temporal dynamics** (seconds vs. years)
2. **Causal accessibility** (direct perception vs. chain-mediated)
3. **Level of analysis** (individual → dyadic → group)
4. **Reversibility** (transient states vs. permanent structures)

### 1.2 The Taxonomy of Human Consequents

The following taxonomy was developed to capture the heterogeneous nature of human responses:

| Category | Temporal Character | Level | Examples | Measurement Modality |
|----------|-------------------|-------|----------|---------------------|
| **Mental states** | Episodic | Individual | Attention focus, cognitive load, spatial orientation | EEG, eye-tracking, dual-task |
| **Mental structures** | Enduring | Individual | Cognitive maps, place schemas | Sketch maps, wayfinding |
| **Dispositional cognitive states** | Latent/activated | Individual | Readiness to engage, vigilance | Priming paradigms |
| **Cognitive processes** | Unfolding | Individual | Wayfinding, problem-solving | Think-aloud, process tracing |
| **Emotional states** | Episodic | Individual | Fear, delight, awe | Self-report, facial coding, physiology |
| **Emotional dispositions** | Trait-like | Individual | Place attachment, environmental sensitivity | Scales, longitudinal observation |
| **Affective states** | Episodic, valenced | Individual | Pleasure, arousal, dominance | PAD scales, SAM |
| **Affective processes** | Unfolding | Individual | Mood drift, affective habituation | Experience sampling |
| **Social interaction dispositions** | Latent | Dyadic/Group | Willingness to converse, approach/avoidance | Behavioral coding, proximity |
| **Spatial-social positioning** | Choice under social constraint | Individual-in-group | Seating choice, body orientation | Observation, spatial analysis |
| **Activity dispositions** | Situation-contingent | Individual | Readiness to work, play, rest | Behavioral affordance matching |
| **Affordance recognition** | Perceptual-cognitive | Individual | Seeing sit-ability, climb-ability | Action-relevant perception tasks |

---

## PART II: EXPLICIT RULE TYPES IN THE CURRENT SCHEMA

### 2.1 The Five Formal Rule Types

From the `ae.rule.v1.schema.json`, the system defines five formal rule types:

| Rule Type | Definition | Bayesian Network Role | Current Coverage |
|-----------|------------|----------------------|------------------|
| **edge** | A directed causal or associational relationship between an environmental factor and an outcome | Defines the structure of the BN (which nodes connect) | Well-covered |
| **cpd_hint** | Conditional probability distribution hint—information about the strength/direction of the relationship | Populates the CPT entries | Partially covered via `strength` and `polarity` |
| **prior** | Base rate information about a variable independent of other variables | Sets marginal priors | Rarely captured |
| **constraint** | Logical or boundary constraints on valid combinations | Constrains the BN structure | Via `boundary_conditions` in `applicability` |
| **interaction** | Effects that depend on combinations of multiple IVs | Specifies interaction terms | Via `moderators` in claim schema |

### 2.2 Implicit Rule Types NOT Formally Represented

| Implicit Type | What It Captures | Current Status |
|---------------|------------------|----------------|
| **State-inducing rules** | Environment → transient mental/emotional state | Conflated with all outcome rules |
| **Structure-modifying rules** | Environment → lasting cognitive/neural structure | Not distinguished |
| **Disposition-activating rules** | Environment → activation of latent tendency | Not distinguished |
| **Process-shaping rules** | Environment → ongoing cognitive/behavioral process | Not distinguished |
| **Level-crossing rules** | Individual effect → group-level emergence | Not represented |
| **Affordance-specifying rules** | Environment → action possibility perception | Implicit in some IVs |

---

## PART III: DETAILED RULE TYPE SPECIFICATIONS WITH EXAMPLES

### 3.1 Edge Rules (Environment → Outcome)

**Definition**: A directed relationship asserting that variation in an environmental feature produces variation in a human outcome.

**Current Schema Representation**:
```json
{
  "rule_type": "edge",
  "lhs": [{"var": "env.luminous.daylight.factor", "state": "high"}],
  "rhs": [{"var": "out.affective.mood.positive", "state": "increased"}],
  "polarity": "positive",
  "strength": {"kind": "effect_size", "type": "d", "value": 0.45}
}
```

**Example 1: Direct Perceptual Effect**
- **Rule**: High ceiling height → Increased abstract thinking  
- **Source**: Meyers-Levy & Zhu (2007)
- **Ontological Note**: This is a *state-inducing* rule operating at the individual level with rapid onset.
- **Effect size**: d = 0.52

**Example 2: Affective State Induction**
- **Rule**: Nature view from window → Reduced perceived stress  
- **Source**: Ulrich (1984); Kaplan (2001)
- **Ontological Note**: This is a *state-inducing* rule, but with a *dispositional* component—repeated exposure may create a *structure-modifying* effect (place attachment).
- **Effect size**: d = 0.38

**Example 3: Behavioral Affordance**
- **Rule**: Open spatial layout → Increased spontaneous social interaction  
- **Source**: Backhouse & Drew (1992); Allen (1977)
- **Ontological Note**: This operates through *affordance perception* (seeing others as reachable) and activates *social dispositions*. Level of analysis shifts from individual perception to dyadic/group behavior.
- **Effect size**: r = 0.34

### 3.2 CPD Hint Rules (Strength and Direction Specification)

**Definition**: Rules that specify the quantitative character of a relationship, beyond mere presence/absence.

**Example 1: Monotonic Dose-Response**
- **Rule**: As illuminance increases from 300 to 1000 lux, alertness increases linearly  
- **Source**: Cajochen et al. (2000)
- **CPD hint**: "linear, slope = 0.003 alertness_units/lux"

**Example 2: Inverted-U (Goldilocks)**
- **Rule**: Visual complexity has inverted-U relationship with preference—moderate complexity optimal  
- **Source**: Berlyne (1971); Kaplan & Kaplan (1989)
- **CPD hint**: "peak at complexity = 0.5 (normalized), falloff both directions"
- **Critical Gap**: The current schema has `polarity: u_shaped` but no mechanism to specify the optimal point or the curvature.

**Example 3: Threshold Effect**
- **Rule**: Noise above 55 dB produces distraction; below 55 dB, minimal effect  
- **Source**: Sundstrom (1986); Banbury & Berry (1998)
- **CPD hint**: "threshold at 55dB; above threshold d = -0.4/10dB"

### 3.3 Prior Rules (Base Rate Information)

**Definition**: Information about the baseline distribution of a variable, independent of specific environmental conditions.

**Example 1: Population Baseline**
- **Rule**: In office populations, 60% report some degree of environmental dissatisfaction  
- **Source**: Leaman & Bordass (2007)

**Example 2: Seasonal Baseline**
- **Rule**: Baseline positive affect is 0.3 SD lower in winter months at high latitudes  
- **Source**: Kasper et al. (1989)

**Example 3: Age-Related Baseline**
- **Rule**: Older adults have lower baseline working memory capacity  
- **Source**: Salthouse (1994)

### 3.4 Constraint Rules (Boundary Conditions)

**Definition**: Rules specifying conditions under which other rules do or do not apply.

**Example 1: Temporal Boundary**
- **Rule**: Circadian lighting effects only occur with exposure duration > 30 minutes  
- **Source**: Viola et al. (2008)

**Example 2: Population Boundary**
- **Rule**: Ceiling height effects on creativity do not replicate in populations with high autism-spectrum traits  
- **Source**: Hypothetical but plausible

**Example 3: Context Dependency**
- **Rule**: Open-plan benefits for communication require absence of focused work tasks  
- **Source**: Brennan et al. (2002)

### 3.5 Interaction Rules (Multi-Factor Dependencies)

**Definition**: Rules where the effect of one environmental factor depends on the level of another.

**Example 1: Cross-Modal Interaction**
- **Rule**: Daylight improves mood more strongly when acoustic environment is quiet  
- **Source**: Veitch et al. (2008)
- **Mechanism**: cognitive_load_competition

**Example 2: Person × Environment Interaction**
- **Rule**: Introversion moderates open-plan effects on productivity  
- **Source**: Maher & von Hippel (2005)
- When introversion = "high", open_plan → productivity = -0.4d
- When introversion = "low", open_plan → productivity = +0.1d

**Example 3: Temporal × Spatial Interaction**
- **Rule**: Circadian lighting effectiveness depends on time-of-day exposure  
- **Source**: Lockley et al. (2006)

---

## PART IV: RULE INTERACTIONS—POSITIVE AND NEGATIVE

### 4.1 Positive Interactions (Synergistic Rules)

**Definition**: When multiple environmental factors combine to produce effects greater than the sum of individual effects.

**Example 1: Biophilic Clustering**
- R1: Nature view → stress reduction (d = 0.3)
- R2: Natural materials → stress reduction (d = 0.2)
- R3: Natural light → stress reduction (d = 0.25)
- R1+R2+R3 combined: stress reduction (d = 0.9, not 0.75)
- **Mechanism**: Consistent biophilic signals create coherent environmental message
- **Source**: Browning et al. (2014); Kellert (2005)

**Example 2: Congruent Sensory Channels**
- R1: High ceiling → freedom/expansiveness feeling (d = 0.4)
- R2: Light, airy color palette → freedom/expansiveness feeling (d = 0.2)
- R1+R2 combined: effect > additive (d = 0.7)
- **Mechanism**: Cross-modal metaphor consistency (SPACIOUS = FREE = LIGHT)
- **Source**: Meyers-Levy & Zhu (2007); Lakoff & Johnson (1980)

**Example 3: Coherence Premium**
- When daylight + thermal + acoustic are ALL good: satisfaction >> sum of individual satisfactions
- **Mechanism**: Environmental quality is holistic; one deficient modality disproportionately undermines overall experience.
- **Source**: Frontczak & Wargocki (2011); Kim & de Dear (2012)

### 4.2 Negative Interactions (Antagonistic/Competitive Rules)

**Example 1: Visual-Acoustic Conflict**
- R1: Open plan → visual access → sense of community (+)
- R2: Open plan → acoustic exposure → distraction (−)
- R3: Open plan → speech privacy loss → stress (+)
- **Net Effect**: R2 and R3 often override R1 for knowledge workers.
- **Mechanism**: Acoustic effects have faster onset and higher priority in attention system.
- **Source**: Kim & de Dear (2013); Brennan et al. (2002)

**Example 2: Prospect-Refuge Tension**
- R1: High prospect (visual openness) → sense of control (+)
- R2: High prospect → sense of exposure → vulnerability (−)
- R3: High refuge (enclosure) → sense of protection (+)
- R4: High refuge → sense of confinement → claustrophobia (−)
- **Net Effect**: Optimal requires balance; either extreme produces net negative.
- **Mechanism**: Evolutionary legacy of predator detection vs. concealment needs.
- **Source**: Appleton (1975); Dosen & Ostwald (2016)

**Example 3: Stimulation Level Conflict (Inverted-U)**
- R1: High environmental complexity → interest/engagement (+)
- R2: High environmental complexity → cognitive load → fatigue (−)
- R3: Low environmental complexity → ease of processing (+)
- R4: Low environmental complexity → boredom (−)
- **Net Effect**: Inverted-U; optimal complexity depends on task demands and individual arousal level.
- **Mechanism**: Yerkes-Dodson law applied to environmental stimulation.
- **Source**: Berlyne (1971); Kaplan (1987)

---

## PART V: CROSS-LEVEL RULE INTERACTIONS

### 5.1 The Level-of-Analysis Hierarchy

| Level | Unit of Analysis | Example Variables | Measurement |
|-------|------------------|-------------------|-------------|
| **Neural** | Brain regions/networks | Amygdala activation, DMN coherence | fMRI, EEG |
| **Physiological** | Body systems | Cortisol, heart rate variability | Biomarkers |
| **Cognitive** | Mental operations | Working memory span, attention | Performance tasks |
| **Affective** | Feeling states | Mood, stress, preference | Self-report, physiology |
| **Behavioral** | Individual actions | Sitting choice, movement patterns | Observation, sensors |
| **Dyadic** | Two-person interactions | Conversation duration, eye contact | Observation, audio |
| **Group** | Collective patterns | Team productivity, social network density | Aggregation, network analysis |
| **Organizational** | System-level outcomes | Turnover, absenteeism | Records |

### 5.2 Upward Causation Examples

**Example 1: Neural → Cognitive → Behavioral**
```
Chain: 
env.biophilic.nature_in_space.visual_connection 
  → prefrontal_activation (neural)
  → directed_attention_restoration (cognitive)
  → sustained_task_performance (behavioral)

Temporal profile:
- Neural effect: onset 50-200ms
- Cognitive effect: measurable after 10+ minutes exposure
- Behavioral effect: measurable after 40+ minutes
```
**Source**: Berman et al. (2008); Bratman et al. (2015)

**Example 2: Individual Affect → Dyadic Behavior → Group Dynamics**
```
Chain:
env.spatial.layout.configuration = "open"
  → individual.sense_of_accessibility (affective)
  → dyadic.spontaneous_conversation_frequency (behavioral)
  → group.social_network_density (structural)
  → group.information_diffusion_speed (functional)

Temporal profile:
- Individual affect: hours
- Dyadic behavior change: days
- Network structure change: weeks
- Functional outcome: months
```
**Source**: Allen (1977); Sailer (2011)

**Example 3: Perceptual → Dispositional → Structural**
```
Chain:
env.spatial.enclosure.refuge = "present"
  → immediate.sense_of_safety (perceptual-affective state)
  → repeated_exposure → disposition.place_preference (dispositional)
  → long_term → structure.place_attachment (cognitive-affective structure)

Temporal profile:
- Perceptual-affective state: seconds to minutes
- Dispositional change: emerges over multiple exposures (weeks)
- Structural change: develops over months to years
```
**Source**: Altman & Low (1992); Scannell & Gifford (2010)

### 5.3 Downward Causation Examples

**Example 1: Group Norm → Individual Behavior**
```
Chain:
env.spatial.density.occupant = "crowded"
  → group.implicit_noise_norm = "quiet" (emergent norm)
  → individual.voice_modulation = "lowered"
  → individual.stress = "paradoxically_reduced" (vs. expectation from crowding alone)
```
**Source**: Evans & Lepore (1992)

### 5.4 Cross-Level Contradictions: The Open-Plan Paradox

```
Level-specific effects of open plan:
- Individual: concentration ↓, distraction ↑ (negative)
- Dyadic: communication frequency ↑ (positive)
- Group: team awareness ↑ (positive)
- Organizational: space efficiency ↑, turnover ↑ (mixed)

Resolution requires specifying:
- Which level is the target outcome?
- What is the task ecology (focused vs. collaborative)?
- What is the temporal window of interest?
```
**Source**: Bernstein & Turban (2018); Kim & de Dear (2013)

---

## PART VI: TEMPORAL CONSIDERATIONS

### 6.1 Temporal Taxonomy of Effects

| Temporal Class | Onset Latency | Duration | Decay Profile | Example |
|----------------|---------------|----------|---------------|---------|
| **Immediate-transient** | <1 sec | Seconds to minutes | Rapid | Startle from sudden noise |
| **Rapid-state** | Seconds | Minutes to hours | Gradual | Mood shift from entering bright space |
| **Delayed-state** | Minutes | Hours | Gradual | Attention restoration from nature exposure |
| **Cumulative-dispositional** | Days | Weeks to months | Slow decay | Preference development through repeated exposure |
| **Structural-developmental** | Weeks to months | Years to permanent | Very slow/irreversible | Place attachment, cognitive map formation |
| **Chronic-health** | Months | Permanent | Accumulating | Stress-related illness from chronic poor environment |

### 6.2 Detailed Temporal Examples

**Example 1: Immediate-Transient Effects**
- **Rule**: Sudden loud noise → Startle response
- **Temporal parameters**:
  - onset_latency: 50-200 ms
  - peak_effect: 200-500 ms
  - duration: 1-5 seconds
  - decay: exponential, τ ≈ 1 second
  - habituation: partial within 5-10 exposures
- **Source**: Blumenthal et al. (2005)

**Example 2: Rapid-State Effects**
- **Rule**: Entering high-ceiling space → Shift toward abstract thinking
- **Temporal parameters**:
  - onset_latency: ~30 seconds after entering
  - peak_effect: 2-5 minutes
  - duration: while in space + 5-10 minutes after
  - decay: gradual over 10-20 minutes after leaving
  - carryover: minimal to next day
- **Source**: Meyers-Levy & Zhu (2007)

**Example 3: Delayed-State Effects (Attention Restoration)**
- **Rule**: Nature exposure → Directed attention restoration
- **Temporal parameters**:
  - onset_latency: 10-15 minutes
  - threshold_dose: 15-20 minutes minimum exposure
  - peak_effect: 40-50 minutes
  - duration: 1-2 hours post-exposure
  - decay: gradual linear
  - dose_response: logarithmic (diminishing returns after 40 min)
- **Source**: Berman et al. (2008); Kaplan (1995)

**Example 4: Cumulative-Dispositional Effects**
- **Rule**: Repeated exposure to controllable environment → Increased environmental self-efficacy
- **Temporal parameters**:
  - onset_latency: observable after 2-4 weeks
  - accumulation: approximately linear with exposure frequency
  - plateau: 6-12 months of consistent experience
  - decay_if_removed: slow, 50% loss over 3-6 months
- **Source**: Lee & Brand (2005); Veitch & Newsham (2000)

**Example 5: Structural-Developmental Effects**
- **Rule**: Childhood exposure to natural environments → Adult environmental attitudes
- **Temporal parameters**:
  - critical_period: ages 5-12
  - accumulation: over years of exposure
  - consolidation: adolescence and early adulthood
  - permanence: largely stable in adulthood
  - reversibility: low (core structure), moderate (specific attitudes)
- **Source**: Chawla (1998); Wells & Lekies (2006)

**Example 6: Chronic-Health Effects**
- **Rule**: Chronic exposure to poor lighting → Circadian disruption → Depression risk
- **Temporal parameters**:
  - lag: months to years
  - mechanism_chain:
    - circadian_rhythm_disruption (weeks)
    - sleep_quality_degradation (weeks to months)
    - mood_regulation_impairment (months)
    - clinical_depression (months to years)
  - reversibility: good if intervention before clinical threshold
- **Source**: LeGates et al. (2014); Bedrosian & Nelson (2017)

### 6.3 Temporal Interaction Patterns

**Pattern 1: State-Disposition Transition**
```
repeated(state_induction) → disposition_formation
  Example: Repeated positive experiences in a space →
           place_preference → place_attachment

  Temporal parameters:
  - Number of exposures: 10-30
  - Spacing: distributed > massed
  - Emotional valence: consistent > variable
  - Duration of each exposure: threshold ~15-20 min
```

**Pattern 2: Priming and Decay**
```
state_induction → temporary_disposition → decay_to_baseline
  Example: Creative space exposure → enhanced divergent thinking →
           gradual return to baseline

  Temporal parameters:
  - Prime duration: 5-10 minutes
  - Effect duration: 20-40 minutes
  - Decay function: approximately exponential
  - Reactivation: faster with repeated priming
```

**Pattern 3: Cumulative Stress Model**
```
chronic_subthreshold_exposure → allostatic_load → health_outcome
  Example: Moderate noise (50-55dB) × years →
           cardiovascular risk

  Temporal parameters:
  - Individual exposure: below acute harm threshold
  - Accumulation period: years
  - Recovery if removed: partial, slow
  - Individual differences: large (stress reactivity)
```

**Pattern 4: Critical Period Effects**
```
exposure_during_sensitive_period → permanent_structural_change
  Example: Enriched vs. impoverished childhood environment →
           adult cognitive capacity, environmental preferences

  Temporal parameters:
  - Sensitive period: developmentally constrained (age-specific)
  - Exposure duration: months to years
  - Reversibility: low after period closes
  - Compensatory potential: some, but diminished
```

---

## PART VII: RECOMMENDED SCHEMA EXTENSIONS

### 7.1 Consequent Ontology Extension

Add to outcome taxonomy a meta-classification layer:

```yaml
consequent_ontology:
  temporal_character:
    - state  # Transient, context-bound
    - disposition  # Latent, activatable
    - process  # Ongoing, unfolding
    - structure  # Enduring, slowly modified
    
  level_of_analysis:
    - neural
    - physiological
    - cognitive
    - affective
    - behavioral
    - dyadic
    - group
    - organizational
    
  causal_accessibility:
    - direct  # Gibson-style affordance
    - single_mediated  # One intervening mechanism
    - chain_mediated  # Multiple mechanisms
    - emergent  # Arises from lower-level interactions
```

### 7.2 Temporal Parameter Extension

Add to rule schema:

```json
{
  "temporal": {
    "onset_latency": {"value": 15, "unit": "minutes", "uncertainty": "±5"},
    "exposure_threshold": {"value": 20, "unit": "minutes"},
    "peak_effect_time": {"value": 45, "unit": "minutes"},
    "duration": {"value": 2, "unit": "hours"},
    "decay_profile": "exponential",
    "decay_tau": {"value": 30, "unit": "minutes"},
    "accumulation_potential": true,
    "critical_period": null
  }
}
```

### 7.3 Cross-Level Interaction Encoding

Add to rule schema:

```json
{
  "level_dynamics": {
    "origin_level": "individual.cognitive",
    "target_level": "group.behavior",
    "causal_direction": "upward",
    "emergence_mechanism": "aggregation_nonlinear",
    "temporal_lag_between_levels": {"value": 2, "unit": "weeks"}
  }
}
```

### 7.4 Rule Interaction Encoding

New schema element for rule-rule relationships:

```json
{
  "rule_interaction": {
    "interacting_rules": ["rule_id_1", "rule_id_2"],
    "interaction_type": "synergistic|antagonistic|conditional|sequential",
    "net_effect_modifier": 1.3,
    "condition": "when both active simultaneously",
    "mechanism": "coherent_environmental_message"
  }
}
```

---

## PART VIII: HIGHER-LEVEL THEORIES CATALOG

### 8.1 Theories Already in the System

1. Stress Recovery Theory (SRT) - Ulrich
2. Attention Restoration Theory (ART) - Kaplan & Kaplan
3. Allostatic Load Theory - McEwen
4. Affective Appraisal Theories (Russell's Core Affect)
5. Predictive Processing and Perception
6. Neural Entrainment and Acoustic Environments
7. Circadian Entrainment via Light
8. Color-Emotion Interaction Models
9. Cognitive Map Theory (Tolman, O'Keefe & Nadel)
10. Affordance Theory (Gibson)
11. Embodied Cognition in Spatial Perception
12. Prospect-Refuge Theory (Appleton)

### 8.2 Additional Theories Developed

**Perceptual Organization & Processing**
| Theory | Domain | Key References |
|--------|--------|----------------|
| Gestalt Principles | How proximity, similarity, continuity, closure shape spatial perception | Wertheimer (1923); Wagemans et al. (2012) |
| Perceptual Fluency Theory | Ease of processing drives aesthetic preference | Reber, Schwarz & Winkielman (2004) |
| Feature Integration Theory | How attention binds visual features | Treisman & Gelade (1980) |
| Crossmodal Correspondences | Mappings between sensory modalities | Spence (2011) |

**Cognitive Load & Resource Allocation**
| Theory | Domain | Key References |
|--------|--------|----------------|
| Cognitive Load Theory | Environmental complexity taxes working memory | Sweller (1988); Choi et al. (2014) |
| Dual-Process Theory | Automatic vs. deliberate spatial processing | Kahneman (2011); Ellard (2015) |
| Selective Attention & Distraction | Feature capture/release of attention | Lavie (2005); Mehta, Zhu & Cheema (2012) |
| Schema Theory / Scene Gist | Rapid categorization from templates | Oliva & Torralba (2006) |

**Aesthetic & Preference Mechanisms**
| Theory | Domain | Key References |
|--------|--------|----------------|
| Fractal Fluency Hypothesis | Preference for D ≈ 1.3–1.5 | Taylor et al. (2011); Hagerhall et al. (2004) |
| Peak Shift Principle | Exaggerated features drive stronger responses | Ramachandran & Hirstein (1999) |
| Optimal Stimulation Level Theory | Seeking environments matching arousal set-point | Berlyne (1971); Mehrabian (1976) |
| MAYA Principle | Novelty bounded by familiarity | Hekkert, Snelders & van Wieringen (2003) |

**Evolutionary & Biophilic Mechanisms**
| Theory | Domain | Key References |
|--------|--------|----------------|
| Biophilia Hypothesis | Innate affiliation with living systems | Wilson (1984); Kellert & Wilson (1993) |
| Savanna Hypothesis | Preference for savanna-like landscapes | Orians & Heerwagen (1992) |
| Habitat Selection Theory | Rapid resource/safety assessment | Kaplan (1992); Appleton (1975) |
| Defensive Architecture | Spaces satisfying predator-avoidance | Hildebrand (1999) |

**Social-Spatial Mechanisms**
| Theory | Domain | Key References |
|--------|--------|----------------|
| Proxemics | Personal space distances | Hall (1966) |
| Privacy Regulation Theory | Dynamic boundary control | Altman (1975) |
| Behavior Setting Theory | Standing behavioral patterns tied to contexts | Barker (1968) |
| Social Facilitation/Inhibition | Presence effects on performance | Zajonc (1965); Bernstein & Turban (2018) |
| Territoriality & Personalization | Space marking for identity/control | Brown & Altman (1983) |

**Neurobiological Substrates**
| Theory | Domain | Key References |
|--------|--------|----------------|
| Place/Grid/Border Cells | Neural encoding of location, distance, boundaries | O'Keefe & Nadel (1978); Moser et al. (2008) |
| Default Mode Network | Self-referential processing in familiar environments | Buckner et al. (2008) |
| Neuroaesthetics of Architecture | fMRI of beauty, complexity, approach/avoidance | Vartanian et al. (2013); Coburn et al. (2020) |
| Autonomic Nervous System Coupling | HRV, skin conductance as stress/restoration markers | Ulrich et al. (1991); Yin et al. (2020) |

**Temporal & Adaptive Mechanisms**
| Theory | Domain | Key References |
|--------|--------|----------------|
| Adaptation Level Theory | Judgments relative to exposure history | Helson (1964); Frederick & Loewenstein (1999) |
| Ultradian & Infradian Rhythms | 90-min, weekly, seasonal cycles | Kleitman (1963); Roenneberg (2012) |
| Temporal Discounting in Spatial Decisions | Short-term comfort vs. long-term wellbeing | Laibson (1997) |

**Information-Theoretic & Computational**
| Theory | Domain | Key References |
|--------|--------|----------------|
| Information Rate & Visual Complexity | Bits/second processing load | Stamps (2002); Cavalcante et al. (2014) |
| Free Energy Principle | Minimizing prediction error | Friston (2010); Van de Cruys & Wagemans (2011) |
| Statistical Learning of Scene Regularities | Implicit environmental structure learning | Turk-Browne et al. (2005) |

---

## PART IX: LITERATURE-JUSTIFIED RULES FOR THE BAYESIAN NETWORK

### 9.1 Core Rules with Effect Sizes

| # | Rule | Source | Effect Size | Temporal Class |
|---|------|--------|-------------|----------------|
| 1 | High ceiling → Abstract thinking | Meyers-Levy & Zhu (2007) | d = 0.52 | Rapid-state |
| 2 | Nature view → Stress reduction | Ulrich (1984) | d = 0.38 | Rapid-state |
| 3 | Open layout → Social interaction | Allen (1977) | r = 0.34 | Behavioral affordance |
| 4 | Illuminance 300-1000 lux → Alertness | Cajochen et al. (2000) | Linear, 0.003/lux | Rapid-state |
| 5 | Noise > 55 dB → Distraction | Sundstrom (1986) | d = -0.4/10dB | Threshold effect |
| 6 | Circadian light × 30+ min → Alertness | Viola et al. (2008) | d = 0.45 | Delayed-state |
| 7 | Complexity → Preference | Berlyne (1971) | Inverted-U | State-inducing |
| 8 | Open plan × Introversion → Productivity | Maher & von Hippel (2005) | d = -0.4 (high intro) | Interaction |
| 9 | Blue light × Evening → Sleep quality | Lockley et al. (2006) | d = -0.3 | Temporal interaction |
| 10 | Daylight × Quiet → Mood | Veitch et al. (2008) | d = 0.5 (quiet) vs 0.2 (noisy) | Cross-modal interaction |
| 11 | Nature walk 20+ min → Attention restoration | Berman et al. (2008) | d = 0.46 | Delayed-state |

### 9.2 Additional Rules from Theoretical Review

| # | Rule | Source | Mechanism |
|---|------|--------|-----------|
| 12 | Fractal D ≈ 1.3-1.5 → Aesthetic preference | Taylor et al. (2011) | Perceptual fluency |
| 13 | Biophilic clustering → Synergistic stress reduction | Browning et al. (2014) | Coherent environmental message |
| 14 | Prospect-refuge balance → Optimal comfort | Appleton (1975) | Evolutionary safety |
| 15 | High visual complexity → Cognitive load | Choi et al. (2014) | Resource depletion |
| 16 | Personal space violation → Stress | Hall (1966) | Proxemic norm violation |
| 17 | Environmental control → Self-efficacy | Lee & Brand (2005) | Cumulative-dispositional |
| 18 | Childhood nature exposure → Adult environmental attitudes | Chawla (1998) | Structural-developmental |
| 19 | Chronic poor lighting → Depression risk | Bedrosian & Nelson (2017) | Chronic-health via circadian |

---

## PART X: PHILOSOPHICAL FOUNDATIONS

### States vs. Dispositions (Ryle, 1949)
States are occurrent (happening now); dispositions are categorical bases for states (could happen given trigger). Environment may *trigger* a state from a *disposition*, or *modify* a disposition through repeated state inductions.

### Processes vs. Structures (Piaget, 1970)
Processes are temporal unfoldings (wayfinding as you navigate); structures are the products of processes that persist (the cognitive map formed through wayfinding). Environments can shape both, at different timescales.

### Affordances as Relational Properties (Gibson, 1979; Chemero, 2003)
Affordances are neither purely in the environment nor purely in the person—they are relations between environmental features and organism capabilities. This complicates simple IV→DV thinking.

### Levels and Emergence (Kim, 1999; Craver, 2007)
Group-level phenomena emerge from but are not simply reducible to individual-level phenomena. The rule system needs to represent this without committing to strong reductionism or mysterious emergence.

---

## PART XI: KEY DOCUMENTS AND ARTIFACTS

### Created During These Sessions

1. **rule_ontology_analysis.md** - Full analysis of rule types with examples
2. **bn_theory_rule_compendium.docx** - 8-page Word document with:
   - PPT-ready tables of 25+ higher-level theories
   - Full node specifications with indicator variables for 4 key theories
   - 11 literature-justified rules formatted for BN implementation
3. **Presentations** - Multiple PowerPoint presentations explaining rule types for undergraduates

### Key Files in User's System

- `ae.rule.v1.schema.json` - Current rule schema
- `ae.claim.v1.schema.json` - Current claim schema
- `taxonomy.yaml` - Environmental feature taxonomy (TagRegistry)
- `outcome_taxonomy.yaml` - Outcome taxonomy

---

## PART XII: SUMMARY OF KEY CONCLUSIONS

1. **The current system conflates ontologically distinct consequent types** - all outcomes are treated similarly regardless of whether they are states, dispositions, processes, or structures.

2. **Temporal parameters are critically missing** - effects ranging from milliseconds to years are not formally distinguished.

3. **Cross-level dynamics are not represented** - individual → dyadic → group → organizational emergence patterns cannot be encoded.

4. **Rule-rule interactions need formal encoding** - synergistic, antagonistic, conditional, and sequential relationships between rules are implicit at best.

5. **The "Goldilocks" problem is underspecified** - inverted-U relationships exist but optimal points and curvatures cannot be encoded.

6. **The schema has good foundations** - the separation of claims from rules, SubjectScope, SubjectModerators, and applicability/boundary_conditions concepts are excellent starting points.

### Recommended Next Steps

1. Extend the outcome taxonomy with the meta-classification layer (temporal_character, level_of_analysis, causal_accessibility)
2. Add temporal parameters to the rule schema
3. Create a mechanism for representing rule-rule interactions
4. Enable cross-level relationship specification
5. Add Goldilocks/inverted-U parameterization (optimal point, curvature, asymmetry)

This would transform the system from capturing "environment X affects outcome Y" to capturing "environment X, through mechanism M, with temporal profile T, at level L, induces/modifies/activates consequent Y (type: state/disposition/process/structure), with interactions Z when combined with environment W."

---

## REFERENCES

*(See the rule_ontology_analysis.md document for the complete reference list with Google Scholar citation counts)*
