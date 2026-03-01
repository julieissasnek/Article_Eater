# Panel C: Theory-Molecule Linkage
## Expert Panel Consultation

**Date**: 2026-03-01
**Panel Type**: Environmental Psychology Theory, Cognitive Science, Neuroaesthetics
**Quorum**: 3 panelists (all present)

---

## Panel Composition

| Panelist | Expertise | Tradition | Role |
|----------|-----------|-----------|------|
| Dr. Rachel Kaplan & Stephen Kaplan (Env Psych Theory) | Restorative environments, attention restoration theory, soft fascination, prospect-refuge theory | Kaplan & Kaplan research tradition | Domain Expert |
| Dr. James Gibson / Don Hoffman (CogSci) | Ecological psychology, affordances, embodied cognition, perceptual learning | Gibson / O'Regan ecological tradition | Integrator |
| Dr. V.S. Ramachandran (NeuroAesthetics) | Neuroaesthetics, beauty perception, neural correlates, perceptual fluency | Vision science + neuroscience | Skeptic |

---

## Input Materials Summary

**Sources**:
1. `/data/cva/rasa_attractors.json` (Natyashastra-inspired molecular taxonomy; 9 primary attractors + 3 cultural variants)
2. Theory frameworks available: NM (Neuromodulation), IC (Integrated Cognition), PP (Prospect-Refuge), SN (Social Networks), DP (Design Pattern), CB (Color-Biophilia), DT (Damage-Thresholds), EC (Embodied Cognition), MS (Multisensory)

**Molecular Inventory** (9 attractors):
- **shringara** (Love/Beauty): delight, SafetyValue 0.6, BelongingValue 0.8, RestorationValue 0.5
- **hasya** (Joy/Humor): laughter, InterestValue 0.8, CompetenceSupportValue 0.7
- **karuna** (Compassion): sorrow, RelatednessSupportValue 0.7, BelongingValue 0.7
- **raudra** (Wrath/Power): fury, StatusValue 0.8, AutonomySupportValue 0.8, SafetyValue 0.3
- **veera** (Heroism): vigor, CompetenceSupportValue 0.8, InterestValue 0.7, AutonomySupportValue 0.7
- **bhayanaka** (Terror/Awe): fear, prediction_error 0.8, control_efficacy 0.2, SafetyValue 0.2
- **bibhatsa** (Disgust): disgust, processing_cost 0.7, SafetyValue 0.2, all support values <0.3
- **adbhuta** (Wonder): astonishment, InterestValue 0.9, multisensory_coherence 0.7
- **shanta** (Peace): calm, RestorationValue 0.8, SafetyValue 0.7, processing_cost 0.2

**Cultural variants**: Japanese (ma-influenced: lower density, higher coherence), West African (àṣà-influenced: collective dignity), Indian (rasa-native: wider basins)

---

## Panel Questions

### Q1: Is the molecule vocabulary (perceptual-cognitive attractors) coherent? Are the named patterns real phenomena?

**Dr. Kaplan (Environmental Psychology):**

The rasa framework is **conceptually beautiful but empirically problematic** for environmental psychology.

**What the molecules capture correctly**:

1. **shanta (Peace/Serenity)** maps well to restorative environment theory. Kaplan & Kaplan (1989) and Ulrich (1983) identify environments that reduce stress and restore attention. Shanta's profile (RestorationValue 0.8, SafetyValue 0.7, processing_cost 0.2) is *phenomenologically accurate* for restorative spaces (e.g., quiet nature, views of water).

   **Confidence: 0.82** (empirically supported by decades of ART research)

2. **adbhuta (Wonder)** and **veera (Heroism)** capture the "soft fascination" concept from ART. Kaplan et al. (1989) argue that gentle engagement with complexity (fractals, weather patterns, water movement) restores attention. Adbhuta's profile (InterestValue 0.9, prediction_error 0.5, multisensory_coherence 0.7) and Veera's profile (CompetenceSupportValue 0.8, affordance_density 0.7) capture this dynamic exploratory state.

   **Confidence: 0.75** (conceptually coherent; less empirically validated than shanta)

3. **shringara (Love/Beauty)** maps to aesthetic preference and biophilic attraction. The BelongingValue (0.8) and SafetyValue (0.6) capture the idea that beautiful spaces are those signaling safety and social possibility (Appleton's prospect-refuge, Ulrich's biophilic features—plants, water, openness).

   **Confidence: 0.72** (empirically plausible; confounds aesthetic appeal with functional restoration)

**What the molecules conflate or miss**:

1. **Confusion between aesthetic valence and causal efficacy**: Shringara (Beauty) is marked with high BelongingValue and low RestorationValue. But empirically, **beautiful spaces are not necessarily restorative**. A visually stunning but psychologically threatening environment (e.g., a cliff edge with a beautiful view) is high aesthetic valence but low restoration. Conversely, a plain, safe, restored wetland is low aesthetic valence but high restoration.

   The rasa framework *packages* emotional-perceptual states without distinguishing their **functional outcomes**. This is a critical epistemological problem.

   **Confidence in concern: 0.85**

2. **Missing temporal dynamics**: Rasa states are instantaneous/static. But restorative environments require **duration and habituation**. A 5-minute exposure to nature restores attention; 5 years in the same space may become boring (habituation). The molecules have basin_radius (0.3–0.35) but no temporal decay or habituation parameters.

   **Confidence in gap: 0.80**

3. **Missing moderators**: Environmental psychology findings are heavily moderated by:
   - Individual differences (restoration proneness; Laumann et al., 2001)
   - Cognitive style (visual vs. auditory preference)
   - Cultural background (Western vs. non-Western aesthetic preferences; Cimprich & Robb, 2002)

   Rasa has cultural_variants (Japanese, West African, Indian), but the variants are applied uniformly to constraints (shanta_constraint_delta for Japanese). **This assumes culture shifts affect all individuals equally**, which is false. Culture is **within-group variable**, not just between-group.

   **Confidence in gap: 0.75**

**Real phenomena identified by rasa?**

The attractors identify **real emotional-perceptual states** (delight, fear, wonder, calm), but these are **affect/emotion categories**, not **causal mechanisms**. Confusing the two is a category error.

- **Real**: Nature induces calm (shanta) via parasympathetic activation
- **Not established**: Calm is a standalone causal molecule; it's the *experience* of certain physiological states

**Confidence in coherence: 0.60** (molecules are coherent as phenomenological descriptions; less coherent as causal theories)

---

**Dr. Hoffman (Cognitive Science):**

I approach this from ecological psychology and embodied cognition perspective. The rasa framework is **too coarse-grained for cognitive mechanisms** and **relies on unvalidated mappings**.

**What's missing from a cognitive science lens**:

1. **Affordances**: Gibson (1979) defines affordances as action-possibilities that environments offer. The rasa framework mentions affordance_density (0.3–0.7) but doesn't operationalize **which affordances**. A space with high affordance_density might offer:
   - Prospect affordances (ability to see far)
   - Refuge affordances (ability to hide)
   - Locomotion affordances (paths to explore)
   - Social affordances (places to sit together)

   Different affordances support different cognitive/emotional states. Bundling them into a single "affordance_density" is reductive.

   **Confidence in gap: 0.85**

2. **Prediction error**: Rasa includes prediction_error as a constraint (0.1–0.8), which is neuroscientifically sound (prediction error drives learning; Friston, 2010). But prediction_error is **context-dependent**. The same visual scene has:
   - High prediction_error for a first-time visitor (novel affordances)
   - Low prediction_error for a habitual user (learned patterns)

   Rasa treats prediction_error as a property of the attractor, not the observer-environment interaction. This is a **fundamental misalignment with embodied cognition**.

   **Confidence in gap: 0.88** (high)

3. **Multisensory coherence**: Rasa includes multisensory_coherence (0.3–0.8). But coherence *of what*? If I'm in a forest (coherent visual-auditory-olfactory properties) vs. a train station (incoherent sensory signals), the former is high multisensory_coherence. But is coherence *good* or *bad*?
   - **Good** for restoration (Ulrich, 1983): coherent natural scenes restore attention
   - **Bad** for engagement (Berlyne, 1971): novel, incoherent stimuli drive interest

   Rasa doesn't disambiguate. Calling multisensory_coherence 0.8 for shanta and 0.7 for adbhuta suggests coherence is uniformly desirable, which is wrong.

   **Confidence in concern: 0.80**

**Can rasa molecules map to cognitive mechanisms?**

I attempted to map rasa attractors to validated cognitive theories:

| Rasa | Potential Cognitive Mechanism | Strength |
|------|--------------------------------|----------|
| shanta | Reduced working memory load + predictability (low prediction_error 0.1) | Moderate (0.65) |
| adbhuta | Optimal prediction error (0.5) + novelty (InterestValue 0.9) | Moderate (0.70) |
| veera | Goal-aligned affordance engagement (control_efficacy 0.8) | Weak (0.55) |
| shringara | Biophilic signal processing (safety + belonging cues) | Weak (0.50) |
| bhayanaka | Threat response (prediction_error 0.8, control_efficacy 0.2) | Moderate (0.68) |

**Most molecules are phenomenologically vivid but cognitively underspecified.**

**Confidence in mapping: 0.58** (weak explanatory power)

---

**Dr. Ramachandran (NeuroAesthetics):**

I evaluate the molecules from neuroscience of beauty and vision science perspective. The framework is **intriguing but lacks neural grounding**.

**Neural plausibility of molecules**:

1. **shanta (Peace/Serenity)**: Maps to parasympathetic activation (polyvagal theory; Porges, 2011). Neural mechanisms:
   - Low visual complexity (processing_cost 0.2) → reduced demand on lateral intraparietal cortex
   - High multisensory_coherence (0.8) → integrated processing in superior colliculus
   - Familiar patterns (low prediction_error 0.1) → reduced prefrontal error-monitoring

   **Neural plausibility: 0.78** ✓

2. **adbhuta (Wonder)**: Maps to novelty-seeking and striatal dopamine release. Neural mechanisms:
   - High prediction_error (0.5) → anterior cingulate activation (prediction error signal)
   - High InterestValue (0.9) → ventral striatum reward response
   - Intact control_efficacy (0.6) → no amygdala threat response (unlike fear)

   **Neural plausibility: 0.75** ✓

3. **bhayanaka (Terror/Awe)**: Maps to threat-response circuits (amygdala, periaqueductal gray). Neural mechanisms:
   - High prediction_error (0.8) → error signal without predictive model
   - Low control_efficacy (0.2) → insula activation (interoceptive threat)
   - Low affordance_density (0.3) → limited action options (dorsolateral prefrontal down-regulation)

   **Neural plausibility: 0.80** ✓

4. **shringara (Love/Beauty)**: Maps to aesthetic preference circuits, but **conflates multiple systems**:
   - Biophilic response (amygdala-vOFC pathway for safe stimuli)
   - Beauty perception (fusiform face area for symmetry; ventral visual stream for form)
   - Social approach (nucleus accumbens for affiliative cues)

   Bundling these as a single rasa is neurally **incoherent**. Beauty, safety, and social approach recruit distinct neural systems with different time courses (beauty is fast ~150ms; social approach slower ~300ms).

   **Neural plausibility: 0.45** ✗ (conflates distinct systems)

5. **veera (Heroism)** and **raudra (Wrath)**: Problematic.
   - veera claims high CompetenceSupportValue (0.8) and AutonomySupportValue (0.7), but these are **motivational constructs**, not neural attractors. There's no "heroism circuit" in the brain.
   - raudra claims StatusValue (0.8) and AutonomySupportValue (0.8), but status/autonomy are **social-cognitive constructs**, not perceptual-emotional states.

   **Neural plausibility: 0.35–0.40** ✗ (conflate perception with motivation)

**Major problem: Status and Autonomy are not sensory/emotional properties**. They're social evaluations. Including them as "valuations" in a perceptual-emotional framework is category confusion.

**Confidence in concern: 0.90** (high)

**Are the molecules real phenomena?**

Yes, **as emotional states**. People experience peace, wonder, awe, disgust, etc. But **no**, as **causal mechanisms in environmental psychology**. The molecules describe *feelings*, not *why those feelings occur*.

**Confidence: 0.65** (molecules describe phenomenology well; poor as causal mechanisms)

---

## Points of Agreement (Panelist Consensus)

1. **Molecules capture real emotional/perceptual states** (unanimous, confidence >0.75). Shanta, adbhuta, bhayanaka are well-characterized phenomenologically.

2. **Major gap: Confounding of aesthetic valence with functional efficacy** (unanimous, confidence >0.85). Shringara (Beauty) doesn't necessarily restore; beautiful spaces can be stressful.

3. **Prediction error and multisensory coherence are context-dependent** (unanimous, confidence >0.80). They should vary with observer expertise, not be fixed properties of attractors.

4. **Missing temporal dynamics** (unanimous, confidence >0.80). Rasa states are instantaneous; environmental psychology requires habituation, duration, and learning curves.

5. **Molecules lack explicit links to measured outcomes** (unanimous, confidence >0.85). No rasa says "leads to stress reduction" or "improves working memory." They're purely phenomenological.

---

## Points of Disagreement

1. **Should molecules be abandoned or refined?**
   - **Kaplan**: Refine; address confounds and add temporal dynamics (0.65 confidence in viability)
   - **Hoffman**: Rebuild from cognitive affordances; current framework too loose (0.45)
   - **Ramachandran**: Use as phenomenological categories only; don't treat as causal (0.50)
   - **Resolution**: Use molecules as *post-hoc descriptive categories* for extracted findings (not a priori drivers of extraction). Add outcome-mapping (which molecules predict which measured outcomes?).

2. **Cultural variants: Are they empirically grounded?**
   - **Kaplan**: Skeptical (0.55); cultural shifts in perception are within-group variable, not between-group. Japanese individuals vary widely; ma-influenced aesthetics is not universal.
   - **Hoffman**: Unclear (0.40); need evidence that Japanese observers have systematically different affordance perception than Western observers.
   - **Ramachandran**: Plausible but unvalidated (0.60); cross-cultural neuroaesthetics is emerging field (Bar & Neta, 2006; Cahan et al., 2015), insufficient data to validate variants.
   - **Resolution**: Mark cultural_variants as *hypothetical*. Conduct empirical validation studies (eye-tracking, fMRI cross-cultural samples) before using in analysis.

---

### Q2: Are there major theories in environmental psychology missing from the framework?

**Dr. Kaplan:**

Looking at available t1_frameworks (NM, IC, PP, SN, DP, CB, DT, EC, MS), I identify:

**Covered well**:
- Prospect-Refuge (PP) ✓
- Biophilia (CB = Color-Biophilia) ~ Partial coverage
- Embodied Cognition (EC) ✓
- Neuromodulation (NM) ✓

**Critically missing**:
1. **Attention Restoration Theory (ART; Kaplan & Kaplan, 1989)** — *Not explicitly listed*. ART predicts that soft fascination (gentle engagement with complexity) and sense of being away (escape from directed attention demands) restore mental resources. This is the **dominant theory in environmental psychology** (1000+ citations). Absence is major gap.

   **Confidence in gap: 0.95** (critical)

2. **Stress Reduction Theory (SRT; Ulrich, 1983)** — *Not explicitly listed*. SRT predicts that **brief exposure to nature reduces physiological stress** (cortisol, heart rate). Empirically robust (Ulrich et al., 1991; Park et al., 2009). Absence is major gap.

   **Confidence in gap: 0.92** (critical)

3. **Biophilia Hypothesis (E.O. Wilson, 1985)** — *Partially covered as CB*. But CB is "Color-Biophilia," which is too specific. Biophilia encompasses preference for:
   - Fractals (Hagerhall et al., 2004)
   - Water and landscapes (Kaplan & Kaplan, 1989)
   - Evolutionary safety signals (Öhman & Mineka, 2001)
   - Not just color

   **Confidence in gap: 0.80** (CB too narrow)

4. **Preference-For-Prospect-Refuge (Jay Appleton, 1975)** — *Listed as PP*. Good coverage ✓.

5. **Information-Rate Hypothesis (Berlyne, 1971; Kaplan, 1987)** — *Not listed*. Predicts optimal visual complexity (not too simple, not too chaotic). Empirically supported (Hagerhall et al., 2004; Purcell et al., 2009). Missing.

   **Confidence in gap: 0.75**

6. **Meaning-Making / Narrative Identity (McAdams, 2006; relational theory)** — *Not listed*. How people create meaning from environments (e.g., "this park reminds me of my childhood"; "this office reflects my values"). Important for personalization and attachment (Lewicka, 2011).

   **Confidence in gap: 0.70**

**Summary**: Framework covers **3 of 6 major environmental psychology theories**. Missing ART, SRT, and detailed biophilia/complexity theory.

**Confidence: 0.85** (substantial gap)

---

**Dr. Hoffman (Cognitive Science):**

From ecological psychology, frameworks should include:

1. **Affordance Theory (J.J. Gibson, 1979; continued by Chemero, O'Regan)** — Environments afford certain actions. Agents perceive affordances directly (not via conscious inference). This is *foundational* to ecological psychology.
   - Is it covered as "affordance_density" in rasa? Partially, but under-operationalized (what affordances?).
   - **Recommendation**: Add explicit AFFORDANCE framework mapping actions to environmental features.

   **Confidence in importance: 0.90** (foundational)

2. **Enactivism (O'Regan & Noë, 2001; Varela et al., 1991)** — Perception is action-dependent. How you move through an environment determines what you perceive. This is critical for dynamic environments (water, trees moving, people).
   - Not covered in available frameworks.
   - **Confidence in gap: 0.75**

3. **Situated Cognition (Lave & Wenger, 1991; Rogoff, 2003)** — Knowledge and skills are embedded in context. Learning in one environment may not transfer to another. Important for environmental design that supports learning (classrooms, playgrounds).
   - Not covered.
   - **Confidence in gap: 0.70**

**Summary**: t1_frameworks missing **foundational cognitive science theories**. Rasa framework is more phenomenological (emotion-based) than cognitive (mechanism-based).

---

**Dr. Ramachandran (NeuroAesthetics):**

Available frameworks should include:

1. **Perceptual Fluency Hypothesis (Reber et al., 2004)** — Stimuli that are easy to process (fluent) are liked better. Neural basis: less demand on dorsolateral prefrontal cortex, more positive affect from insula. Relevant to beauty and restoration (simple environments are easier to process).
   - Not explicitly listed.
   - **Confidence in gap: 0.75**

2. **Peak Shift Effect (Ramachandran & Hirstein, 1999)** — Exaggerated features are perceived as more beautiful/prototypical than actual stimuli (e.g., caricatures). Neural basis: tuning curves in IT cortex. Relevant to why exaggerated nature (vivid colors, extreme forms) is beautiful.
   - Not listed.
   - **Confidence in gap: 0.70**

3. **Implicit Familiarity (Zajonc mere-exposure effect; Kunst-Wilson & Zajonc, 1980)** — Repeated exposure increases liking, even without conscious recognition. Neural basis: amygdala sensitization. Relevant to attachment and restoration (familiar spaces are more restorative).
   - Not listed.
   - **Confidence in gap: 0.75**

---

## Q3: Is the mapping between theories and molecules defensible?

**Panelist consensus: NO. Mappings are speculative and untested.**

**Examples of weak mappings**:

1. **Shanta (Peace) ← Stress-Reduction Theory**: Conceptually plausible (low arousal, safety signals) but **empirically untested**. SRT predicts cortisol reduction; does shanta have lower processing_cost, higher SafetyValue in environments where cortisol actually drops? Unknown.

2. **Adbhuta (Wonder) ← Attention Restoration Theory**: ART emphasizes soft fascination (gentle engagement with complexity). Adbhuta has InterestValue 0.9, prediction_error 0.5. But ART doesn't emphasize *excitement*; it emphasizes *gentle* engagement. Adbhuta's profile is too high-arousal for ART.

   **Confidence in mismatch: 0.75**

3. **Veera (Heroism) ← No clear theory**: Veera isn't mapped to any explicit environmental psychology theory. What phenomenon does it capture? Empowerment? Achievement? Unclear.

4. **Raudra (Wrath/Power) ← No theory**: Similar issue. This appears to describe high-stress, high-control states (maybe threat-approach?), but it's not grounded in environmental psychology.

**Overall assessment**: Mappings between theories and molecules appear **post-hoc and untested**, not grounded in empirical environmental psychology literature.

**Confidence in finding: 0.85** (mappings are weak)

---

## Q4: How should we handle theories that span multiple molecules or levels of analysis?

**Example**: Biophilia spans multiple emotional states:
- Safety response (Shringara? Shanta?)
- Interest response (Adbhuta?)
- Social belonging (Shringara emphasizes BelongingValue 0.8)

Is biophilia one molecule or many?

**Dr. Kaplan recommendation**: Biophilia should be treated as a **meta-theory** spanning multiple molecules. Create explicit mappings:
- Biophilia → Shringara (beauty aspect) + Shanta (safety aspect) + Adbhuta (interest aspect)

This requires **many-to-many mapping** (theories ↔ molecules), not one-to-one.

**Confidence: 0.70** (many-to-many mapping adds complexity)

**Dr. Hoffman recommendation**: Some theories operate at **different levels of analysis** (perception vs. cognition vs. emotion) and shouldn't be mixed. Separate:
- **Perceptual level** (affordances, visual processing) → molecules tied to perception (adbhuta)
- **Cognitive level** (restoration, attention) → theories, not molecules
- **Affective level** (emotion, values) → molecules tied to emotion (shanta, raudra)

This requires **stratified mapping** by level of analysis.

**Confidence: 0.65** (adds necessary precision)

**Dr. Ramachandran recommendation**: Distinguish **bottom-up** (neural/perceptual) from **top-down** (conceptual/cultural) theories:
- **Bottom-up** (neural plausibility): Shanta (parasympathetic), Adbhuta (dopamine), Bhayanaka (threat)
- **Top-down** (cultural meaning): Raudra (power), Veera (heroism), Shringara (beauty)

Only map **bottom-up** to molecules; keep **top-down** as conceptual categories.

**Confidence: 0.70** (useful stratification)

---

## Q5: What are the most important theory-molecule linkages to validate first?

**Panelist prioritized list**:

| Priority | Theory-Molecule | Importance | Validation Strategy | Confidence |
|----------|-----------------|-----------|-------------------|----------|
| 1 | ART ← Adbhuta | Central to environmental psychology | Eye-tracking on natural scenes; soft fascination proxy | 0.80 |
| 2 | SRT ← Shanta | Dominant empirical evidence | Cortisol/heart rate in low-processing-cost environments | 0.85 |
| 3 | Biophilia ← Shringara + Shanta | Widespread theory | Preference ratings for biophilic vs. abstract designs | 0.75 |
| 4 | Prospect-Refuge ← (Spatial layout molecules) | Well-established | Gaze patterns in high-affordance environments | 0.80 |
| 5 | Cognitive Load ← Processing cost | Testable | Reaction time / memory span in complex vs. simple scenes | 0.75 |
| 6 | Cultural variants (Japanese ma) ← Shanta | Novel hypothesis | Cross-cultural preference ratings (Japanese vs. Western) | 0.50 |

**Confidence in priority ranking: 0.72** (based on empirical maturity of theories)

---

## Recommendations with Priority

### MUST DO (Block linkage without)

1. **Separate molecules into three categories**:
   - **Phenomenological** (describe what people experience): shanta, adbhuta, bhayanaka, shringara, hasya, karuna, bibhatsa
   - **Motivational** (describe goals/values): veera, raudra
   - **Theoretical** (map to environmental psychology theories): TBD, explicit mapping required

   *Why*: Current conflation of emotion with motivation with perception creates conceptual incoherence.

2. **Create explicit many-to-many mappings between t1_frameworks and molecules**:
   ```json
   {
     "framework_molecule_mapping": {
       "ART": ["adbhuta (soft fascination)", "shanta (escape from directed attention demands)"],
       "SRT": ["shanta (parasympathetic activation)"],
       "Biophilia": ["shringara (biophilic attraction)", "shanta (safety signal)", "adbhuta (interest)"],
       "Prospect-Refuge": ["veera (open vistas)", "shanta (enclosed refuge)"],
       ...
     }
   }
   ```

   *Why*: Prevents one-to-one oversimplification; enables complex theories to span molecules.

3. **Add explicit outcome mappings** (molecules → measured outcomes):
   ```json
   {
     "molecule_outcome_mapping": {
       "shanta": ["cortisol_reduction", "heart_rate_reduction", "attention_restoration"],
       "adbhuta": ["interest_increase", "engagement_increase", "learning_gain"],
       "bhayanaka": ["threat_response_increase", "heart_rate_increase", "attention_narrowing"],
       ...
     }
   }
   ```

   *Why*: Currently, molecules are purely phenomenological. Link to **measured, operationalized outcomes** from environmental psychology.

4. **Conduct pilot validation** of top 3 mappings (ART↔adbhuta, SRT↔shanta, Biophilia↔shringara+shanta) on 50-paper subsample:
   - Do articles about ART findings consistently invoke adbhuta language? (inter-rater reliability)
   - Do articles about SRT findings consistently invoke shanta language? (inter-rater reliability)
   - Can extractors reliably map published findings to molecules? (extraction reliability)

   *Why*: Establish empirical grounding before mainline adoption.

   **Timeline**: 2-week pilot

5. **Mark molecules as PILOT/EXPERIMENTAL** in production until validation complete:
   - molecule_ids field can be populated but flagged as "not yet validated for meta-analysis"
   - Allow exploratory analysis; block use in formal meta-analyses until validation complete

   *Why*: Manages expectations; prevents premature use of unvalidated linkages.

### SHOULD DO (Improves linkage coherence)

6. **Expand t1_frameworks to explicitly include missing major theories**:
   - ART_Kaplan (Attention Restoration Theory)
   - SRT_Ulrich (Stress Reduction Theory)
   - Biophilia_Wilson (Biophilic Hypothesis)
   - Complexity_Kaplan (Information-Rate/Visual Complexity)
   - Affordances_Gibson (Ecological Psychology)

   *Why*: Ensures framework doesn't inadvertently omit major theories.

7. **Create temporal dynamics rules** (molecules vary over time):
   - Habituation: repeated exposure reduces intensity (novelty fades)
   - Learning: exposure enables affordance recognition (adbhuta → shanta over time)
   - Attachment: familiarity increases positive valence (shingara increases with repeated exposure; mere-exposure effect)

   *Why*: Addresses critical gap identified by Kaplan; real restorative effects emerge over sustained engagement.

8. **Document cultural validity** of molecules:
   - Separate "universal aspects" (e.g., fear response to threat cues) from "culturally variable aspects" (e.g., beauty preferences)
   - Conduct empirical cross-cultural study (Japanese, Western, Indian, West African samples; N=30–50 per group) on molecule-feature mappings
   - Publish findings before using cultural_variants in analysis

   *Why*: Current cultural_variants are speculative; need empirical grounding.

### CONSIDER (Nice-to-have; lower priority)

9. **Add neural grounding to plausible molecules**:
   - Shanta: Cite Porges (polyvagal theory); Lisman & Grace (cortical-hippocampal integration)
   - Adbhuta: Cite Lisman & Grace (prediction error); Knutson et al. (dopamine/striatum)
   - Bhayanaka: Cite LeDoux (amygdala threat circuit); Critchley (interoception)
   - *Separate molecules with weak neural plausibility (Veera, Raudra, Shringara); mark as phenomenological only*

   *Why*: Strengthens credibility; clarifies which molecules are neuroscientifically grounded vs. phenomenological.

10. **Create molecule-feature registry** (which visual/spatial features map to which molecules):
    - Shanta features: low visual complexity (fractal D ~1.3), high legibility, water presence, enclosed space
    - Adbhuta features: moderate visual complexity (fractal D ~1.4–1.6), partial obscuration (mystery), novel arrangement
    - Bhayanaka features: high visual chaos (fractal D >1.8), threat signals (cliff edges, predator cues), uncontrollable elements

    *Why*: Enables downstream vision algorithms to detect molecules from image features.

---

## Summary: Theory-Molecule Linkage Assessment

**Overall Grade**: D+ (Conceptually interesting; empirically ungrounded; requires major revision)

**Strengths**:
- Rasa framework provides vivid, phenomenologically rich descriptions of emotional-perceptual states
- Some molecules (shanta, adbhuta, bhayanaka) have plausible neural and psychological grounding
- Framework addresses real gap: environmental psychology lacks unified emotional taxonomy

**Weaknesses**:
- **Mappings to environmental psychology theories are untested and post-hoc** (major issue)
- **Confounds aesthetic valence with functional efficacy** (Shringara isn't restorative just because it's beautiful)
- **Conflates perception, emotion, and motivation** (Veera, Raudra include value/motivational constructs; doesn't belong in perceptual taxonomy)
- **Lacks outcome mappings** (which molecules predict which measured outcomes?)
- **Missing major theories** (ART, SRT not explicitly listed)
- **Cultural variants unvalidated** (hypothetical; need cross-cultural empirical studies)
- **No temporal dynamics** (habituation, learning curves missing)

**Fitness for Purpose**: **NOT READY for meta-analysis use** without substantial development:
1. Pilot validation of top 3 mappings (2 weeks)
2. Explicit theory-molecule mapping (1 week)
3. Outcome mapping (1 week)
4. Temporal dynamics rules (2 weeks)
5. Cultural validation study (6–8 weeks)

**Estimated time to production-ready**: 12–16 weeks

**Confidence in Recommendation**: 0.75 (molecules are promising; current form premature for deployment)

---

## Next Steps for Panel

1. Implement MUST DO items (5 changes)
2. Conduct 2-week pilot validation on 50-paper subsample
3. Expand t1_frameworks with explicit ART, SRT, Biophilia, Complexity
4. Design cross-cultural molecule-feature validation study (method paper)
5. Schedule Panel D (Vision Attributes) after theory-molecule linkage is clarified

**Prepared by**: Panel Secretariat
**Date**: 2026-03-01
**Reviewers**: Kaplan, Hoffman, Ramachandran (all endorsed)
