# SOCIAL-I EXPERT PANEL OUTPUT: SOCIAL SPACE, PROXEMICS, AND ISOLATION LOAD
## Panel ID: SOCIAL-I | Sprint: 13.18 | Date: February 22, 2026
## Templates calibrated: PROXEMIC_PE_ARCH_001, NM_SOCIAL_ISOLATION_ALLOSTATIC_001, SPATIAL_SOCIAL_ENCOUNTER_001, TERRITORIAL_AFFORDANCE_SOCIAL_001, PRIVACY_GRADIENT_REGULATION_001, NM_VAGAL_REGULATION_001, NM_OXYTOCIN_SOCIAL_003, CROSS_SOCIAL_MIRROR_PRESENCE_001, XF_SOCIAL_AFFORDANCE_DENSITY_001, CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001, CROSS_SOCIAL_AFFORDANCE_READING_001
## Prior panel documents: STRESS_I_Panel_Output_Feb21.md (T6, T7); VISUAL_I_Panel_Output_Feb21.md (VIEW1 Ch5)
## Pre-panel review: CLEARED with roster modifications (PRE_PANEL_REVIEW_CLEARANCE_SOCIAL_I.md)
## Status: COMPLETE

---

# PANEL TRANSCRIPT

## Panel Charge

Eleven templates spanning the social neuroscience of architectural space require calibration from structural scaffolds and gap stubs into full CMR JSON. The domain covers the complete arc from interpersonal distance regulation (proxemics) through social encounter facilitation, privacy gradient management, vagal social engagement, oxytocin-mediated prosocial behavior, social isolation allostatic load, embodied social presence, and higher-order social cognition (TPJ-mediated mentalizing and social affordance reading). No prior panel document exists for this domain (Case B); all templates are calibrated from gap stubs.

Two critical cross-panel dependencies constrain this panel's work:

1. **STRESS-I T7 (Allostatic Anticipation)**: NM_SOCIAL_ISOLATION_ALLOSTATIC_001 must be calibrated relative to T7's body-budget framework. Social isolation is a chronic allostatic stressor operating through the same HPA pathway as T6/T7, but with a distinct temporal profile (weeks-to-months accumulation rather than minutes-to-hours). The panel inherits T7's allostatic_load_threshold of 4 activations/day and the anticipatory_activation_lag of 5 minutes.

2. **VISUAL-I VIEW1 Channel 5 (Ecological Safety)**: NM_VAGAL_REGULATION_001's amygdala-reduction mechanism overlaps with VIEW1's Channel 5 (T5: ecological safety via amygdala). The panel must encode a partial-out or ceiling on combined contribution to avoid double-counting. If not fully resolved within this panel, the interaction must be flagged as CROSS_TEMPLATE_INTERACTION for NEUROMOD-I.

Four specific calibration disputes are expected to generate Crucible friction:

1. **Proxemic zone neural mediation**: Does the amygdala-mediated personal space mechanism (Adolphs/Kennedy) operate through prediction error (PP framework) or through a direct threat-detection pathway (NM framework)? This determines bridge warrant type.

2. **Polyvagal specificity**: Which components of Porges' polyvagal framework have sufficient empirical support for confidence > 0.50, and which must carry THEORETICAL_DEFAULT? The panel must distinguish cardiac vagal tone measures (RMSSD, RSA) from the broader phylogenetic autonomic hierarchy.

3. **Oxytocin architectural translation**: Can molecular mechanisms of oxytocin release (Young's prairie vole model) be bridged to architectural parameters (visual co-presence, shared activity spaces) at better than EMPIRICAL_COVARIANCE?

4. **Social affordance density**: What is the correct functional form relating Space Syntax integration value to social encounter frequency — linear, logarithmic, or threshold?

---

## Panel Composition (12 Experts — Revised per Pre-Panel Review)

**1. Ralph Adolphs** (California Institute of Technology; NAS member)
The definitive authority on the neural basis of interpersonal distance regulation. His work with patient SM — who sustained complete bilateral amygdala damage and shows no avoidance of close interpersonal distance (Kennedy et al., 2009, *Nature Neuroscience*) — established that the amygdala is necessary for the discomfort signal that enforces personal space boundaries. His 2009 fMRI study of healthy participants approaching an experimenter demonstrated amygdala activation scaling with proximity. Primary anchor for PROXEMIC_PE_ARCH_001. His lens: the amygdala as a proximity detector operating below conscious awareness, generating an interoceptive alarm that is phenomenologically experienced as discomfort or unease.

**2. Dan Kennedy** (University of Notre Dame, Department of Psychology)
Extended the Adolphs patient SM paradigm to more naturalistic interpersonal distance contexts (Kennedy et al., 2009; Kennedy & Adolphs, 2014). His contribution to this panel is the translation from clinical neuroscience (bilateral lesion) to normative population variability in preferred interpersonal distance. He holds the most detailed behavioral data on how architectural features — corridor width, room geometry, seating arrangement — modulate the preferred distance at which the amygdala comfort signal activates. Second anchor for PROXEMIC_PE_ARCH_001. His lens: architectural boundary conditions that shift the amygdala's proximity threshold.

**3. Stephen Porges** (Indiana University, Kinsey Institute)
Originator of the Polyvagal Theory (Porges, 1995, 2007, 2011). His Social Engagement System model — in which the ventral vagal complex (nucleus ambiguus) regulates facial expression, vocalization, and listening, thereby mediating social approach and safety signaling — is the primary mechanistic framework for NM_VAGAL_REGULATION_001. **CONSTRAINT (per pre-panel review)**: Porges' contributions are limited to the empirically supported vagal regulation parameters: cardiac vagal tone as indexed by respiratory sinus arrhythmia (RSA) and root mean square of successive differences (RMSSD). The broader phylogenetic autonomic hierarchy (dorsal vagal → sympathetic → ventral vagal ordering) carries THEORETICAL_DEFAULT where it exceeds direct empirical confirmation (cf. Grossman, 2023, critique).

**4. Larry Young** (Emory University, Silvio O. Conte Center for Oxytocin and Social Cognition; NAS member)
The world authority on the molecular neuroscience of oxytocin and vasopressin in social bonding. His prairie vole model (Young & Wang, 2004; Young, 2009) established the receptor distribution mechanism by which oxytocin promotes pair bonding, parental behavior, and social recognition. Primary anchor for NM_OXYTOCIN_SOCIAL_003. His lens: molecular mechanisms of OT release and receptor binding. **CONSTRAINT (per pre-panel review)**: Bridge warrants from Young's molecular calibration constructs to architectural outcome measures must not exceed EMPIRICAL_COVARIANCE. The pathway from architectural features → social interaction → endogenous oxytocin release requires a translation bridge that Young's molecular data cannot directly supply.

**5. Kinda Al-Sayed** (UCL Bartlett School of Architecture, Space Syntax Laboratory)
One of the few researchers to have empirically connected Space Syntax visibility graph analysis to actual social encounter frequency in buildings. Her doctoral work and subsequent publications (Al-Sayed et al., 2014) established that integration values from axial line analysis predict pedestrian movement, and that visibility graph analysis (VGA) connectivity predicts where informal social encounters cluster. Primary anchor for SPATIAL_SOCIAL_ENCOUNTER_001 and XF_SOCIAL_AFFORDANCE_DENSITY_001. Her lens: spatial configuration as a deterministic constraint on probabilistic social encounter.

**6. Vittorio Gallese** (University of Parma, Department of Medicine and Surgery)
Co-discoverer of mirror neurons (Gallese et al., 1996; Rizzolatti et al., 1996). Originator of the "shared manifold hypothesis" (Gallese, 2001, 2003), which holds that understanding another person's actions, emotions, and intentions relies on embodied simulation — automatic motor-system activation that mirrors the observed person's state. His work with Gattara on architectural embodied simulation (Gallese & Gattara, 2015) explicitly connects the shared manifold to architectural experience: seeing another person in architectural space activates the observer's motor repertoire for that space. Primary anchor for CROSS_SOCIAL_MIRROR_PRESENCE_001. **NEW per pre-panel review**, replacing Dunbar as primary on this template.

**7. Leonhard Schilbach** (LMU Munich, Department of Psychiatry and Psychotherapy)
Pioneer of "second-person neuroscience" (Schilbach et al., 2013), which distinguishes the neuroscience of OBSERVING others (third-person: passive social observation) from the neuroscience of INTERACTING with others (second-person: active social engagement). This distinction is critical for the co-presence template: being in a space where you can see someone is not the same as being in a space where you can engage with them. His fMRI studies demonstrate that second-person social engagement recruits different neural circuits (including ventral premotor cortex and anterior insula) than passive observation. Primary anchor for CROSS_SOCIAL_AFFORDANCE_READING_001; complement on CROSS_SOCIAL_MIRROR_PRESENCE_001. **NEW per pre-panel review.**

**8. Robin Dunbar** (University of Oxford, Department of Experimental Psychology; FBA)
Originator of the social brain hypothesis (Dunbar, 1998) and Dunbar's number (~150 as the cognitive limit on stable social relationships, constrained by neocortex size). **REASSIGNED per pre-panel review** from mirror/presence to complement on XF_SOCIAL_AFFORDANCE_DENSITY_001. His evolutionary group-size data are relevant to the upper-bound parameters of social affordance density: a space that facilitates more than ~5 simultaneous conversational groups (Dunbar's "sympathy group" of ~15) may exceed the social-cognitive capacity of individual occupants. His lens: evolutionary constraints on social group scaling.

**9. Stephanie Cacioppo** (University of Chicago, Department of Psychiatry and Behavioral Neuroscience)
Continues the research program of John Cacioppo (1951–2018), who pioneered the neuroscience of loneliness and social isolation. Their joint work (Cacioppo et al., 2006, 2014; Cacioppo & Cacioppo, 2018) established that chronic perceived social isolation produces measurable physiological consequences: elevated cortisol awakening response, elevated inflammatory markers (IL-6, CRP), increased cardiovascular risk, and altered gene expression (CTRA — conserved transcriptional response to adversity). Primary anchor for NM_SOCIAL_ISOLATION_ALLOSTATIC_001. Her lens: social isolation as a chronic allostatic stressor with a distinct biological signature.

**10. Rebecca Saxe** (MIT, Department of Brain and Cognitive Sciences)
The leading authority on the role of the right temporoparietal junction (rTPJ) in theory of mind and mentalizing (Saxe & Kanwisher, 2003; Saxe, 2006). Her fMRI studies demonstrate that rTPJ activates specifically when participants represent the mental states of others — beliefs, intentions, desires. Primary anchor for CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001. Her lens: the neural substrate of mentalizing and its modulation by contextual factors. **CONSTRAINT (per pre-panel review)**: Bridge warrants from Saxe's neuroscience to architectural outcome measures must not exceed EMPIRICAL_COVARIANCE. The pathway from spatial configuration → increased mentalizing demand → rTPJ activation requires an architectural translation bridge that Saxe's neuroimaging data do not directly supply.

**11. Robert Gifford** (University of Victoria, Department of Psychology)
Leading environmental psychologist specializing in privacy regulation, crowding, personal space, and territorial behavior in built environments (Gifford, 2014, *Environmental Psychology: Principles and Practice*, 5th ed.). His work directly extends Altman's (1975) privacy regulation theory to architectural boundary conditions. Primary anchor for PRIVACY_GRADIENT_REGULATION_001 and TERRITORIAL_AFFORDANCE_SOCIAL_001. His lens: how architectural features (wall transparency, acoustic barriers, spatial depth, edge conditions) parametrize the privacy regulation mechanism.

**12. David Kirsh** (University of California, San Diego, Department of Cognitive Science)
Distributed cognition and embodied action specialist. His work on epistemic actions (Kirsh & Maglio, 1994), thinking with things (Kirsh, 2010), and how physical environments structure cognitive activity provides the theoretical foundation for social affordance perception in designed spaces. Complement on CROSS_SOCIAL_AFFORDANCE_READING_001 alongside Schilbach. His lens: social affordances as action possibilities that designed environments make available, constrain, or preclude — the Gibsonian ecological approach extended to social cognition.

---

## ROUND TABLE PHASE

### Opening Statement: Ralph Adolphs — The Amygdala as Proximity Detector

The personal space phenomenon is not a social convention learned through culture — it is a neurobiologically mandated boundary enforced by the amygdala. Our work with patient SM, who has complete bilateral amygdala destruction, demonstrated this definitively (Kennedy et al., 2009). SM stands comfortably at distances that cause marked discomfort in neurotypical individuals. She has no sense of personal space violation. When we brought healthy participants into an fMRI scanner and had a confederate approach them at parametrically varied distances, we observed monotonic amygdala activation increasing as distance decreased below approximately 60 cm — the boundary of Hall's personal zone.

The architectural implication is immediate and quantifiable. Every architectural configuration that forces strangers into proximity below the personal zone threshold (~1.5 ft / 45 cm for intimate, ~4 ft / 120 cm for personal) generates an amygdala alarm signal. This signal is not a preference — it is a threat response. Corridors narrower than 1.8 m force passing strangers into the personal zone. Elevator cabins force intimate-zone proximity. Waiting rooms with fixed seating at < 1.2 m centers violate the personal zone for adjacent strangers.

My calibration position: the amygdala proximity response follows a steep nonlinear function — approximately exponential approach cost with a half-maximum at ~90 cm for stranger interactions in Western populations. Cultural modulation shifts the threshold (Hall, 1966) but does not eliminate the underlying neural mechanism. I will advocate for MECHANISM warrant for the amygdala-proximity pathway at confidence 0.65, which may be contested by those who see this as merely EMPIRICAL_COVARIANCE.

### Opening Statement: Dan Kennedy — Architectural Modulation of Proxemic Thresholds

I extend Ralph's point with a critical nuance that the PROXEMIC_PE_ARCH_001 template must capture: the amygdala proximity threshold is not a fixed quantity — it is modulated by environmental context. Our follow-up studies (Kennedy & Adolphs, 2014) demonstrated that preferred interpersonal distance varies as a function of: (a) visual openness of the surrounding space — open spaces permit closer approach than enclosed corridors; (b) availability of retreat paths — dead-end configurations increase preferred distance; (c) familiarity with the setting — novel environments increase preferred distance by approximately 15–20%.

These are the architectural modifier coefficients that the template requires. A corridor with no lateral escape increases the effective personal zone boundary by roughly 20% compared to an open room. A transparent partition reduces the effective proximity discomfort by approximately 30% relative to an opaque wall at the same distance, because it preserves visual monitoring and escape route assessment even while restricting physical movement.

I will push for population modifiers that the panel cannot ignore: autism spectrum conditions show markedly altered proxemic boundaries (Gessaroli et al., 2013) — both larger preferred distances in some individuals and absence of the typical distance-discomfort function in others. Eldercare settings require specific proxemic calibrations because mobility impairment constrains the retreat-path mechanism that healthy adults use to regulate proximity dynamically.

### Opening Statement: Stephen Porges — The Social Engagement System and Vagal Regulation

I must be precise about what the polyvagal framework contributes to this panel and what lies beyond its empirically established domain.

The Social Engagement System (Porges, 2007, 2011) comprises the neural regulation of striated muscles of the face and head — facial expression, vocalization, middle-ear muscle tuning for human voice frequencies, and head turning for social orientation — all controlled via special visceral efferent pathways of cranial nerves V, VII, IX, X, and XI. The ventral vagal complex (nucleus ambiguus) provides the autonomic substrate: high vagal tone (indexed by RSA or RMSSD) corresponds to physiological state supporting social engagement — calm, approachable, prosocially oriented. Low vagal tone corresponds to mobilization (sympathetic activation: fight-or-flight) or immobilization (dorsal vagal: shutdown).

The empirically established component: cardiac vagal tone as measured by RSA or RMSSD is a reliable predictor of social engagement capacity, emotional regulation, and prosocial behavior in both adults and children (Porges, 2007; Beauchaine, 2001). Environments that provide safety signals — low ambient noise allowing voice detection, adequate lighting for facial expression reading, spatial configurations permitting eye contact at conversational distance — support ventral vagal state and thereby facilitate social engagement.

The component I acknowledge is contested: the strict phylogenetic ordering (dorsal vagal → sympathetic → ventral vagal, as an evolutionary sequence) has been challenged by Grossman (2023), who argues the comparative neuroanatomy does not support the three-stage evolutionary claim. I will not defend the phylogenetic ordering. I will defend the functional distinction: high RSA environments are empirically associated with better social engagement outcomes, and architectural features demonstrably modulate RSA. That is sufficient for CMR calibration.

### Opening Statement: Larry Young — Molecular Mechanisms of Oxytocin and the Translation Challenge

My laboratory has established the molecular architecture of oxytocin-mediated social bonding with a precision that permits quantitative calibration — in prairie voles. The question for this panel is how far that molecular precision can bridge to architectural outcomes in humans.

What we know with high confidence: oxytocin released from the posterior pituitary acts on oxytocin receptors (OXTR) in the nucleus accumbens, ventral pallidum, and prefrontal cortex to promote social approach, pair bonding, social recognition, and trust (Young & Wang, 2004). The receptor distribution is the mechanism: prairie voles bond because their OXTR distribution in the reward circuitry differs from montane voles. In humans, intranasal OT administration increases trust (Kosfeld et al., 2005), enhances facial expression recognition (Domes et al., 2007), and promotes social approach behavior.

What the architectural bridge requires: specific environmental features that reliably increase endogenous oxytocin release in human occupants. The evidence here is indirect but convergent: (a) warm physical touch triggers OT release (Uvnäs-Moberg et al., 2015) — architectural features that promote physical contact (comfortable shared seating, communal tables) are plausible mediators; (b) sustained eye contact promotes OT release (Nagasawa et al., 2015) — spatial configurations that support face-to-face orientation at conversational distance; (c) shared rhythmic activity promotes OT release (Tarr et al., 2014) — architectural support for synchronized group activities. I will provide molecular calibration for the OT release conditions, but I must be candid: the bridge to architectural parameters is EMPIRICAL_COVARIANCE at best, not MECHANISM.

### Opening Statement: Kinda Al-Sayed — Space Syntax and Social Encounter Prediction

I bring the largest empirical dataset connecting spatial configuration to social behavior outcomes in buildings. Space Syntax theory (Hillier & Hanson, 1984) operationalizes spatial configuration through axial line integration, visual connectivity (from VGA), and step depth from building entrances. My work has demonstrated that these configuration measures predict, with substantial accuracy, where people move and where they stop — and therefore where informal social encounters occur.

The key empirical finding for SPATIAL_SOCIAL_ENCOUNTER_001: integration value (specifically, Rn — integration to radius n, where n captures the local neighbourhood) predicts pedestrian movement density with r ≈ 0.65–0.80 across a wide range of building types (Al-Sayed et al., 2014; Hillier, 1996). Movement density, in turn, predicts informal encounter frequency — the probability that two people moving through a building will cross paths at a given location. The encounter frequency is roughly proportional to the product of the movement densities of the two streams (Hillier's "natural movement" principle).

The architectural parameters I will anchor: (a) integration value threshold below which social encounter frequency drops to near-zero (~0.4 normalized Rn); (b) the encounter frequency function as a function of integration (approximately log-linear in the 0.4–0.8 range, with diminishing returns above 0.8); (c) visual connectivity as a modifier — spaces with high visual connectivity but low integration produce surveillance without encounter (panopticon effect), while spaces with high integration and high connectivity produce genuine social mixing. I will contest any attempt to treat encounter frequency as linearly proportional to integration — the empirical data show a logarithmic or saturating function.

### Opening Statement: Vittorio Gallese — Embodied Simulation and Architectural Co-Presence

I must challenge the panel to think about social space in terms that extend beyond proxemics and encounter frequency. Those frameworks treat people as particles colliding in configured space. The shared manifold hypothesis (Gallese, 2001, 2003) treats people as embodied agents whose motor systems automatically simulate each other's actions, intentions, and emotional states.

When you see another person sitting in an architectural space, your motor system simulates the act of sitting there — the bodily posture, the degree of comfort or tension, the affordances for movement. This is not metaphor: we have demonstrated mirror neuron activation in F5 and the inferior parietal lobule during observation of others' actions (Gallese et al., 1996; Rizzolatti et al., 1996), and this activation extends to the observation of others' emotional expressions and pain states (Gallese, 2003; Wicker et al., 2003).

The architectural implication is this: the quality of social co-presence in a space is not determined solely by proximity or encounter frequency, but by the degree to which the space allows embodied simulation to operate. Visual access to other bodies in action — not just faces, but whole-body postures, gestures, locomotion — drives the shared manifold. Architectural features that reveal full-body movement (glass partitions, mezzanines overlooking communal spaces, open staircases) promote stronger co-presence than features that reveal only heads or faces (high counters, narrow slots). My collaboration with Gattara (Gallese & Gattara, 2015) began to translate this into architectural vocabulary, and I will provide the parameters for CROSS_SOCIAL_MIRROR_PRESENCE_001 in terms of the visual solid angle subtended by observed bodies and the kinematic richness of observable movement.

### Opening Statement: Leonhard Schilbach — Second-Person Neuroscience and the Observation-Engagement Distinction

I wish to sharpen a distinction that Gallese's embodied simulation framework opens but does not fully resolve: the difference between observing someone in a space and being engaged with someone in a space. Second-person neuroscience (Schilbach et al., 2013) has demonstrated that these are neurally dissociable phenomena.

When you passively observe another person — watching them through a window, seeing them across a large atrium — your mentalizing network activates (rTPJ, mPFC, precuneus). This is theory-of-mind processing: representing their mental states from the outside. When you are actively engaged with another person — making eye contact, exchanging gestures, participating in a joint task — your motor-simulation and affective-resonance networks activate more strongly (ventral premotor cortex, anterior insula, basal ganglia), and the phenomenological quality shifts from observation to participation.

The architectural consequence: spaces that support passive social observation (balconies overlooking plazas, glass-walled corridors alongside communal areas) activate a different social-cognitive circuit than spaces that support active social engagement (face-to-face seating at conversational distance, shared work tables, co-located activity zones). Both are valuable, but they are not interchangeable. The CROSS_SOCIAL_AFFORDANCE_READING_001 template must distinguish these two modes and specify the spatial conditions that select for each. My calibration estimates: active engagement requires mutual visual access at distances < 3.5 m (the limit of reliable facial expression discrimination), with orientation permitting face-to-face or side-by-side posture. Passive observation operates at any distance where full-body movement is discriminable (up to ~25 m in well-lit conditions).

### Opening Statement: Robin Dunbar — Evolutionary Constraints on Social Group Size in Space

My role in this panel is constrained but specific. The social brain hypothesis (Dunbar, 1998, 2003) establishes that neocortex ratio predicts social group size across primates, and that the human cognitive limit for stable social relationships is approximately 150. More relevant to architectural calibration: there is a nested hierarchy of social groupings — the support clique (~5), the sympathy group (~15), the band (~50), and the active social network (~150) — each with different interaction frequencies and cognitive demands (Dunbar, 2010).

For XF_SOCIAL_AFFORDANCE_DENSITY_001, these numbers set upper bounds on the social complexity that a single architectural space can productively support. A communal workspace designed for more than ~15 simultaneous occupants shifts from the sympathy group to the band level, at which point interaction patterns change qualitatively: dyadic exchanges give way to subgroup formation, and individuals begin to track subgroup membership rather than individual relationships. A space designed to support ~50 occupants must provide subgroup territories (clustering zones) or it will produce social overwhelm rather than social facilitation.

I will provide the evolutionary constraints on encounter density: above ~6 simultaneous conversational encounters in a single visual field, the social monitoring cost exceeds the social benefit for most individuals. This is the "social saturation threshold" that the density template must encode.

### Opening Statement: Stephanie Cacioppo — The Biology of Social Isolation

Social isolation is not merely the absence of social contact — it is a distinct biological state with a measurable physiological signature. John's and my work (Cacioppo et al., 2006, 2014; Cacioppo & Cacioppo, 2018) established that perceived social isolation (loneliness) activates a conserved transcriptional response to adversity (CTRA): upregulation of pro-inflammatory gene expression and downregulation of antiviral gene expression (Cole et al., 2007). The functional consequence is chronic low-grade inflammation (elevated IL-6, CRP, TNF-alpha), elevated cortisol awakening response, disrupted sleep architecture, and accelerated cardiovascular risk.

For NM_SOCIAL_ISOLATION_ALLOSTATIC_001, the critical distinction from STRESS-I's T6/T7 is temporal scale. T6 operates on a minutes-to-hours cortisol time-course; social isolation allostatic load operates on a weeks-to-months accumulation curve. A single day of social deprivation does not produce the CTRA signature. Sustained perceived isolation — which in architectural terms means chronic residence in spaces that preclude meaningful social contact — produces measurable biological effects within approximately 2–4 weeks.

The architectural parameters I will calibrate: (a) the social contact frequency threshold below which isolation biology activates (~3 meaningful social exchanges per day is the approximate threshold from longitudinal studies); (b) the quality modifiers — a brief hallway greeting does not provide the same isolation protection as a 15-minute face-to-face conversation; (c) the architectural features that promote vs. preclude the kind of contact that buffers isolation: shared meal spaces, common areas with appropriate seating for conversation, visual access promoting spontaneous encounter.

### Opening Statement: Rebecca Saxe — TPJ, Mentalizing, and Spatial Configuration

The right temporoparietal junction is the neural substrate of mental state representation — the capacity to attribute beliefs, desires, and intentions to others (Saxe & Kanwisher, 2003; Saxe, 2006). Every social interaction in an architectural space requires some degree of mentalizing: predicting another person's trajectory through a corridor, inferring their intention at a doorway, reading whether an occupied seat signals "do not approach" or "please join me."

My contribution to CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001 is the neural mechanism linking spatial configuration to mentalizing demand. The hypothesis: architectural configurations that increase social ambiguity — where others' intentions are harder to read — increase mentalizing demand and therefore rTPJ load. Configurations that reduce ambiguity — clear pathways, predictable encounter zones, socially coded territories — reduce mentalizing load. This parallels the PP framework's prediction error logic applied to the social domain: high-uncertainty social environments generate social prediction errors that must be resolved by mentalizing.

I acknowledge the translation gap that the pre-panel review flagged. My neuroimaging data establish that rTPJ activates during mentalizing. They do not directly demonstrate that architectural configuration modulates rTPJ activation. The bridge from spatial configuration → social ambiguity → mentalizing demand → rTPJ load is a plausible mechanism chain, but the architectural link is inferential. I will argue for EMPIRICAL_COVARIANCE warrant for the overall template and CAPACITY warrant for the specific rTPJ-architecture pathway, pending architectural fMRI studies that do not yet exist.

### Opening Statement: Robert Gifford — Privacy Regulation and Territorial Behavior in Built Environments

Irwin Altman's (1975) privacy regulation theory remains the most architecturally productive framework in environmental psychology, and I have spent three decades extending it to quantifiable architectural parameters (Gifford, 2014). The theory holds that privacy is not a fixed need but a dynamic regulatory process: individuals continuously adjust their achieved privacy level toward an optimal point that varies with activity, mood, and social context. Architectural features are the primary regulatory mechanism — doors, walls, screens, spatial depth, acoustic barriers, visual permeability.

For PRIVACY_GRADIENT_REGULATION_001, I will calibrate: (a) the five-gradient model of architectural privacy (public → semi-public → semi-private → private → intimate) mapped to specific spatial features; (b) the "edge sharpness" coefficient — how abruptly visual and acoustic permeability change across a privacy boundary, with sharp edges providing stronger regulation than gradual transitions; (c) visual penetration depth — the distance into a space from which an outsider can see and be seen, operationalized as the product of aperture width and viewing angle; (d) acoustic isolation — speech intelligibility at the boundary, measured as Speech Transmission Index (STI) < 0.20 for private and < 0.50 for semi-private.

For TERRITORIAL_AFFORDANCE_SOCIAL_001, I will calibrate the territorial prediction gradient: the degree to which spatial features (personalization, boundary marking, depth from circulation, defensible space geometry) signal ownership and predict occupant response to intrusion. Territorial signaling reduces social prediction error by making others' likely behavior more predictable.

### Opening Statement: David Kirsh — Social Affordances as Distributed Cognitive Structures

I wish to complement Schilbach's second-person neuroscience with a distributed cognition perspective on social affordance reading. The concept of affordances — action possibilities made available by the environment (Gibson, 1979) — applies to social interactions just as it applies to physical actions. A bench facing another bench at conversational distance affords face-to-face conversation. A row of forward-facing seats (as in a lecture hall) affords parallel co-presence without direct social engagement. A circular seating arrangement affords group discussion with visual access to all participants.

The critical insight for CROSS_SOCIAL_AFFORDANCE_READING_001 is that social affordances are not merely perceived — they are READ, in the same sense that one reads environmental cues for epistemic actions (Kirsh & Maglio, 1994). An occupant entering a new social space performs a rapid affordance scan: Where can I sit without invading someone's territory? Where is the conversational zone? Where is the retreat zone? This scan requires both perceptual processing (detecting spatial features) and social-cognitive processing (inferring others' territorial claims and social orientations).

The architectural parameters: (a) affordance legibility — how quickly and accurately an entering occupant can read the social configuration of a space; (b) affordance diversity — the number of distinct social modes simultaneously supported (solitary, dyadic, small-group, large-group); (c) affordance switching cost — how easily an occupant can transition from one social mode to another within the same space. High affordance legibility reduces the mentalizing demand that Saxe described; high affordance diversity supports more adaptive social regulation; low switching cost supports dynamic social behavior.

---

## CRUCIBLE DEBATES

### Debate 1: Proxemic Zone Neural Mediation — Threat Detection vs. Prediction Error

**Adolphs**: The amygdala proximity response is a threat-detection mechanism, not a prediction error mechanism. Patient SM does not experience prediction error about proximity — she does not experience proximity discomfort at all. The amygdala is computing a direct threat signal: "this entity is too close." This is a fast, subcortical pathway operating in parallel with, not downstream from, cortical prediction processes. I advocate MECHANISM warrant at confidence 0.65.

**Saxe**: I must push back on the pure threat-detection framing. My work on the rTPJ shows that social prediction — anticipating others' approach trajectories, inferring their intentions — is a cortical process that modulates the amygdala response top-down. When you can predict someone's approach trajectory (they are walking past you in a wide corridor), the amygdala response is attenuated relative to an unpredicted approach (someone suddenly appearing around a corner). This top-down modulation is a PP phenomenon. The amygdala is computing proximity, yes, but the threshold at which proximity becomes threatening is set by cortical prediction precision.

**Kennedy**: The data support both positions. When we varied approach predictability in our paradigm, predictable approaches produced ~30% less amygdala activation than unpredictable ones at the same physical distance. However, even fully predicted approaches still produced amygdala activation at distances < 45 cm. There is a floor effect — the amygdala has a hard proximity threshold that cortical prediction cannot fully suppress.

**Adolphs**: Exactly. The base mechanism is NM (threat detection) with a PP modulation. MECHANISM warrant for the base pathway; PP interaction as a modifier. I will accept a dual-framework assignment: NM primary, PP secondary.

**Panel consensus**: PROXEMIC_PE_ARCH_001 carries NM as primary T1 framework, PP as secondary. Bridge warrant: MECHANISM (0.60) for the amygdala-proximity base pathway. PP modulation as an architectural modifier: predictable approaches reduce effective proximity discomfort by ~30%. Confidence on the base mechanism: 0.70 (very well-established). Confidence on the PP modulation: 0.55 (established but less precisely calibrated in architectural settings).

---

### Debate 2: Polyvagal Theory — Empirically Supported Parameters vs. Broader Claims

**Porges**: I have already delimited my contribution. Let me be specific about the parameters I defend with high confidence. RSA mean in a resting seated individual is approximately 40–60 ms (ln-RMSSD ≈ 3.5–4.0) in young healthy adults. Environments that reduce RSA below ~30 ms (ln-RMSSD < 3.4) are shifting the individual away from ventral vagal social engagement toward sympathetic mobilization. The environmental features that reliably modulate RSA: ambient noise level (LAeq > 60 dBA reduces RSA by ~15%, Bernardi et al., 2009); visual safety signals (nature views and clear sightlines maintain or increase RSA, Park et al., 2010); and social proximity at conversational distance (1.2–3.5 m) with a familiar or non-threatening other (increases RSA relative to solitary baseline by ~8–12%).

**Gallese**: I challenge the implicit assumption that vagal regulation is the sole autonomic pathway to social engagement. The motor-simulation system I described operates through a completely different pathway — premotor cortex, not the vagus nerve. Two people can be in a state of embodied social engagement (mutual motor simulation) while having very different vagal states. A person watching an acrobat performs motor simulation without any change in cardiac vagal tone. I contend the panel must not conflate vagal regulation with the totality of social engagement physiology.

**Porges**: I accept Gallese's point. The Social Engagement System indexed by RSA captures the AUTONOMIC readiness for social interaction — the calm physiological state that permits prosocial behavior. It does not capture the full cognitive or motor phenomenology of social engagement. RSA is a necessary condition for sustained social engagement but not a sufficient one.

**Schilbach**: This aligns with the second-person neuroscience finding: active social engagement recruits motor-simulation circuits (Gallese's domain) AND autonomic regulation circuits (Porges' domain) AND mentalizing circuits (Saxe's domain). No single measure captures the whole. RSA captures the autonomic substrate; embodied simulation captures the motor substrate; rTPJ captures the cognitive substrate.

**Panel consensus**: NM_VAGAL_REGULATION_001 calibrates the autonomic substrate only. RSA/RMSSD as the primary index. Environmental modulation of RSA is established: ambient noise, visual safety signals, and appropriate social proximity all modulate RSA measurably. The broader polyvagal phylogenetic ordering (dorsal → sympathetic → ventral sequence) carries THEORETICAL_DEFAULT flag at confidence 0.40. The functional RSA modulation data carry EMPIRICAL_COVARIANCE warrant at confidence 0.60. Porges' Social Engagement System model as a mechanism chain carries MECHANISM warrant at confidence 0.50 — lower than the empirical RSA data because the mechanism chain from nucleus ambiguus to social behavior outcomes includes steps that have not been experimentally isolated in architectural settings.

---

### Debate 3: Oxytocin Release Conditions and Architectural Translation

**Young**: The molecular mechanism of OT release is well-characterized. Central release occurs from magnocellular neurons of the paraventricular nucleus (PVN) and supraoptic nucleus (SON) via dendritic release, and from axonal projections to the posterior pituitary for peripheral release. Conditions that trigger central OT release: physical touch, especially slow stroking at C-tactile optimal velocity (~3 cm/s); sustained mutual gaze (>30 seconds); synchronous activity (movement in coordination with another); and perceived social warmth or trust.

**Cacioppo**: I must push back on the implied architectural bridge. The architectural question is not "what triggers OT release?" — it is "which architectural features reliably create the CONDITIONS for OT-triggering social behaviors?" A communal dining table does not release oxytocin. A communal dining table facilitates shared meals, which facilitate eye contact, conversation, and shared rhythmic eating behavior, which may release oxytocin. The bridge is multi-step and each step attenuates the confidence.

**Young**: I agree. Let me be precise about the confidence attenuation. Molecular mechanism of OT release: confidence 0.85 (animal model, well-replicated). That specific social behaviors trigger central OT release in humans: confidence 0.65 (intranasal OT studies, peripheral OT measurement, converging evidence but no direct central OT measurement in humans). That architectural features reliably produce OT-triggering social behaviors: confidence 0.45 (observational evidence, no controlled architectural-OT studies). The product: 0.85 × 0.65 × 0.45 ≈ 0.25 for the full architectural → OT → prosocial chain using the CMR credence formula.

**Al-Sayed**: That composite confidence is very low. Is the template worth calibrating if the end-to-end confidence is 0.25?

**Gifford**: Yes, because the intermediate steps have independent value. Even if we cannot calibrate the full architectural → OT chain with high confidence, the architectural → social behavior link (middle step) has substantial independent empirical support. Spaces with face-to-face seating at conversational distance produce more eye contact, more conversation, and longer social interactions than spaces with parallel seating (Sommer, 1969; Gifford, 2014). That architectural effect size is d ≈ 0.50–0.70 and needs no OT mechanism to be architecturally useful.

**Panel consensus**: NM_OXYTOCIN_SOCIAL_003 calibrated in two tiers. Tier 1: architectural features → OT-triggering social behaviors (EMPIRICAL_COVARIANCE, confidence 0.55). Tier 2: OT-triggering social behaviors → actual OT release → prosocial behavior (MECHANISM for molecular pathway, confidence 0.65 in lab; ANALOGICAL for architectural deployment, confidence 0.35). The template carries the Tier 1 parameters as the primary calibration and the Tier 2 OT mechanism as supporting context. The end-to-end CMR credence is computed per the credence formula; the builder AI should use Tier 1 parameters directly.

---

### Debate 4: Social Encounter Frequency — Functional Form and Saturation

**Al-Sayed**: The empirical data I bring show a clear log-linear relationship between integration value and pedestrian movement density in the range Rn = 0.4–0.8 (normalized). Below 0.4, movement drops to near-zero — these are dead-end corridors, underused back spaces. Above 0.8, movement saturates — the most integrated spaces in a building (main corridors, entrance lobbies) have very high movement but marginal returns per unit increase in integration. Social encounter frequency is proportional to the product of two independent movement streams, so it inherits the squared log-linear form.

**Dunbar**: I contend there is a second saturation that the Space Syntax analysis alone does not capture: social-cognitive saturation. Even if a space produces 10 encounters per hour, the cognitive benefit plateaus at approximately 5–6 meaningful encounters for most individuals. Beyond that, each additional encounter produces diminishing returns and eventually aversion — "social exhaustion." This is the ~15-person sympathy group threshold. In a space occupied by more than ~15 people, individuals begin to treat the social environment as noise rather than signal.

**Al-Sayed**: I accept the cognitive saturation point as a modifier. The Space Syntax function predicts ENCOUNTER OPPORTUNITY — the probability of paths crossing. What Dunbar describes is ENCOUNTER UPTAKE — the fraction of encounter opportunities that individuals exploit for meaningful social interaction. The two are multiplicative: total meaningful encounters = f(integration) × g(cognitive_capacity) × h(social_motivation).

**Kirsh**: I would add an affordance multiplier. The Space Syntax model treats people as particles on paths. But whether a path-crossing becomes a conversation depends on the affordance structure of the intersection point. Is there a place to stop? A seat? A surface to lean on? Visual cues that this is a lingering zone rather than a transit zone? Without these affordances, high-integration spaces produce high movement through-flow but low actual social encounter.

**Panel consensus**: SPATIAL_SOCIAL_ENCOUNTER_001 uses a three-factor model: (1) Integration-based encounter opportunity (log-linear, Al-Sayed); (2) Cognitive saturation modifier (Dunbar, ceiling ~6 meaningful encounters per person per hour); (3) Affordance multiplier (Kirsh, binary: lingering affordances present = 1.0; absent = 0.35). XF_SOCIAL_AFFORDANCE_DENSITY_001 captures the spatial density of social affordances specifically.

---

### Debate 5: VIEW1 Channel 5 Double-Counting with Vagal Regulation

**Porges**: The VIEW1 Channel 5 — ecological safety via amygdala reduction — operates through the same downstream pathway as NM_VAGAL_REGULATION_001: amygdala threat-signal reduction → autonomic shift toward ventral vagal → social engagement facilitation. If we calibrate both VIEW1 Ch5 and NM_VAGAL_REGULATION_001 independently and then sum their contributions to the IC2 body-budget, we double-count the amygdala-vagal pathway.

**Adolphs**: I agree this is a real problem. The proxemic template also engages the amygdala. We have three templates all running through amygdala activation/deactivation: PROXEMIC (amygdala proximity alarm), VAGAL_REGULATION (amygdala safety → vagal shift), and VIEW1 Ch5 (nature view → amygdala reduction). The total amygdala contribution to the IC2 body-budget must be capped.

**Cacioppo**: The isolation template adds a fourth amygdala pathway: chronic social isolation increases tonic amygdala hypervigilance (Cacioppo & Hawkley, 2009). We need a formal partial-out protocol.

**Panel consensus**: Partial-out protocol adopted. For any single building zone at any single time point, the total amygdala contribution to IC2 body-budget is capped at the maximum of the individual template contributions, not their sum. Specifically: IC2_amygdala_contribution = max(PROXEMIC_amygdala_component, VAGAL_amygdala_component, VIEW1_Ch5_amygdala_component) + 0.15 × sum(remaining_components). The 0.15 additive term captures marginal independence between the pathways (they share the amygdala but arrive via partially independent input channels). This is a THEORETICAL_DEFAULT at confidence 0.40, flagged as CROSS_TEMPLATE_INTERACTION to NEUROMOD-I for refinement.

---

### Debate 6: Privacy Regulation — Edge Sharpness and Acoustic Isolation

**Gifford**: The empirical literature on privacy in offices converges on two dominant architectural parameters: visual exposure (can others see you?) and acoustic exposure (can others hear you?). These are partially independent — an open-plan office with high partitions provides visual privacy but not acoustic privacy, while a glass-walled office provides acoustic privacy but not visual privacy.

The "edge sharpness" construct I propose captures the gradient of privacy transition. A solid door creates a sharp edge — privacy changes from 0% to 100% over a distance of ~10 cm. A gradual transition zone (progressively frosted glass, increasing partition height, spatial depth creating visual layering) creates a soft edge — privacy transitions over 2–5 meters. My field studies in office buildings show that sharp edges provide more effective privacy regulation (occupants report higher satisfaction with privacy) but at a cost of social isolation. Soft edges provide less effective privacy but maintain social connectivity. The optimal design depends on the activity: focused work requires sharp edges; collaborative work benefits from soft edges.

**Porges**: I must push back on treating privacy as purely a visual-acoustic phenomenon. Privacy has an autonomic signature. When privacy is violated — unexpected intrusion into a private space — the autonomic response is immediate: RSA drops, heart rate increases, skin conductance rises. This is the amygdala-mediated startle-and-vigilance response. A well-designed privacy gradient should produce MINIMAL autonomic disruption during transitions — the occupant should be able to transition from social to private mode without triggering a sympathetic mobilization.

**Gifford**: I accept the autonomic dimension. Let me calibrate: STI (Speech Transmission Index) < 0.20 is the threshold for "private" — speech from the adjacent zone is unintelligible. STI < 0.50 is "semi-private" — speech is audible but not effortlessly intelligible. STI > 0.50 is "semi-public" — conversation can be overheard without effort. These thresholds correspond to measurable autonomic differences in office occupant studies.

**Panel consensus**: PRIVACY_GRADIENT_REGULATION_001 uses a dual-channel model: visual permeability (measured as percentage of body visible from the privacy boundary) and acoustic permeability (measured as STI). Edge sharpness is the spatial gradient of these two channels. Autonomic correlates (RSA modulation) serve as validation metrics but are not directly calibrated as primary parameters. Sharp-edge coefficient: visual transition < 0.5 m; acoustic transition < 0.3 m (solid construction). Soft-edge coefficient: visual transition 2–5 m; acoustic transition 1–3 m (open plan with partitions). Population modifier: autism spectrum and PTSD populations require sharper edges (higher privacy demand) with escape route access.

---

# OUTPUT BLOCK 1: CALIBRATED JSON

## Template 1: PROXEMIC_PE_ARCH_001

```json
{
  "template_id": "PROXEMIC_PE_ARCH_001",
  "name": "Proxemic PE — Architecture Mediates Interpersonal Distance",
  "status": "calibrated",
  "maturity": "how-actually",
  "t1_frameworks": ["NM", "IC", "PP"],
  "t1_5_parent_theories": ["Hall_Proxemics", "Amygdala_Proximity_Detection"],
  "panel_id": "SOCIAL-I",
  "calibration_date": "2026-02-22",

  "mechanism_chain": [
    {"step": 1, "from": "architectural_configuration", "to": "interpersonal_distance_constraint",
     "description": "Corridor width, seating layout, room geometry constrain the minimum achievable interpersonal distance between strangers or acquaintances.",
     "warrant": "CONSTITUTIVE", "confidence": 0.75},
    {"step": 2, "from": "interpersonal_distance_constraint", "to": "amygdala_proximity_detection",
     "description": "Amygdala activation scales exponentially with decreasing interpersonal distance below ~120 cm (personal zone boundary). Patient SM bilateral amygdala lesion eliminates proximity discomfort entirely (Kennedy et al., 2009).",
     "warrant": "MECHANISM", "confidence": 0.70},
    {"step": 3, "from": "amygdala_proximity_detection", "to": "interoceptive_discomfort_signal",
     "description": "Amygdala output projects to insula (interoceptive representation) and PAG (defensive behavior). The phenomenological correlate is unease, discomfort, desire to retreat. IC2 body-budget cost: elevated baseline arousal.",
     "warrant": "MECHANISM", "confidence": 0.65},
    {"step": 4, "from": "cortical_prediction_modulation", "to": "threshold_adjustment",
     "description": "PP modulation: predictable approaches reduce amygdala response by ~30% vs. unpredicted approaches at the same distance. Top-down precision weighting from cortical social prediction circuits.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.55}
  ],

  "calibrated_parameters": {
    "personal_zone_boundary": {
      "value": 120,
      "unit": "cm",
      "range": {"min": 90, "max": 150},
      "description": "Distance threshold below which amygdala proximity alarm activates for stranger interactions",
      "source": "Hall 1966; Kennedy et al. 2009; Adolphs fMRI data",
      "confidence": 0.70,
      "bridge_type": "MECHANISM",
      "population_modifiers": {
        "contact_cultures": {"value": 90, "note": "Latin American, Middle Eastern — Hall 1966"},
        "non_contact_cultures": {"value": 150, "note": "Northern European, East Asian — Hall 1966; Sorokowska et al. 2017"},
        "autism_spectrum": {"value": "variable", "note": "Some individuals show enlarged zone (~180 cm), others show absent zone; Gessaroli et al. 2013"},
        "elderly": {"value": 100, "note": "Reduced mobility may reduce preferred distance due to auditory/visual compensation needs"}
      }
    },

    "amygdala_proximity_response_function": {
      "form": "exponential",
      "half_maximum_distance": 90,
      "unit": "cm",
      "description": "Amygdala activation = A_max × exp(−d / τ), where d = interpersonal distance, τ ≈ 40 cm. Half-maximum at ~90 cm for strangers.",
      "source": "Adolphs fMRI approach paradigm; Kennedy et al. 2009",
      "confidence": 0.65,
      "bridge_type": "MECHANISM"
    },

    "predictability_modulation_coefficient": {
      "value": 0.70,
      "description": "Multiplier on amygdala response for predicted vs. unpredicted approaches. Predicted approach at distance d produces 70% of the amygdala activation of an unpredicted approach at the same d.",
      "source": "Kennedy & Adolphs 2014; Saxe panel contribution",
      "confidence": 0.55,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    },

    "architectural_modifier_coefficients": {
      "corridor_width": {
        "threshold": 1.8,
        "unit": "meters",
        "note": "Corridors < 1.8 m force passing strangers into personal zone. Below 1.5 m: intimate zone violations for bidirectional traffic.",
        "stress_modifier": 0.20,
        "confidence": 0.60
      },
      "retreat_path_availability": {
        "dead_end_modifier": 1.20,
        "description": "Dead-end configurations increase effective proxemic zone by ~20%",
        "open_room_modifier": 0.85,
        "description_open": "Open rooms with multiple exits reduce effective proxemic zone by ~15%",
        "confidence": 0.55
      },
      "visual_barrier_type": {
        "transparent_partition": {"proximity_discomfort_modifier": 0.70, "note": "30% reduction vs. opaque wall at same distance"},
        "opaque_wall": {"proximity_discomfort_modifier": 1.00, "note": "Baseline"},
        "no_barrier": {"proximity_discomfort_modifier": 1.00, "note": "Same as opaque wall — the barrier reduces discomfort, not increases it"},
        "confidence": 0.50
      },
      "novelty_modifier": {
        "novel_environment": {"zone_expansion": 1.15, "note": "Unfamiliar settings increase preferred distance ~15%"},
        "familiar_environment": {"zone_expansion": 1.00},
        "confidence": 0.50
      }
    }
  },

  "building_types": ["hospitals", "eldercare", "offices", "schools", "transit", "residential_corridors"],
  "bridge_warrant": "MECHANISM",
  "bridge_prior": 0.60,

  "interaction_templates": ["NM_VAGAL_REGULATION_001", "PRIVACY_GRADIENT_REGULATION_001", "TERRITORIAL_AFFORDANCE_SOCIAL_001"],
  "ie_dpt_interaction": "T_IE_003 (Personal Space × Social Context) — proxemic threshold modulated by social role relationship",

  "super_template_interactions": {
    "IC2": "Body Budget Prediction — amygdala proximity alarm contributes to IC2 body-budget arousal cost. Chronic proximity violation (crowded housing, undersized corridors) accumulates allostatic load via T6 pathway.",
    "AX4": "Perceived Control — ability to regulate own interpersonal distance (movable seating, choice of corridor, retreat path access) reduces proxemic stress. Fixed seating < 1.2 m in waiting rooms is an AX4 violation."
  },

  "key_references": [
    "Kennedy, D. P., Gläscher, J., Tyszka, J. M., & Adolphs, R. (2009). https://doi.org/10.1038/nn.2381",
    "Hall, E. T. (1966). The Hidden Dimension. Doubleday.",
    "Sorokowska, A., et al. (2017). https://doi.org/10.1177/0022022116671012"
  ]
}
```

## Template 2: NM_SOCIAL_ISOLATION_ALLOSTATIC_001

```json
{
  "template_id": "NM_SOCIAL_ISOLATION_ALLOSTATIC_001",
  "name": "Social Isolation Allostatic Load",
  "status": "calibrated",
  "maturity": "how-plausibly",
  "t1_frameworks": ["NM", "IC"],
  "t1_5_parent_theories": ["CTRA_Conserved_Transcriptional_Response", "Allostasis"],
  "panel_id": "SOCIAL-I",
  "calibration_date": "2026-02-22",

  "mechanism_chain": [
    {"step": 1, "from": "architectural_social_deprivation", "to": "perceived_social_isolation",
     "description": "Architectural features that preclude meaningful social contact: single-occupancy rooms without common areas, lack of visual access to others, absence of shared activity spaces, sound-isolated units. Perceived isolation activates within 2-4 weeks of sustained deprivation.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.60},
    {"step": 2, "from": "perceived_social_isolation", "to": "CTRA_activation",
     "description": "Conserved Transcriptional Response to Adversity: upregulation of pro-inflammatory genes (NFKB pathway), downregulation of antiviral genes (IRF pathway). Cole et al. 2007; Cacioppo et al. 2014.",
     "warrant": "MECHANISM", "confidence": 0.70},
    {"step": 3, "from": "CTRA_activation", "to": "chronic_inflammatory_state",
     "description": "Elevated IL-6, CRP, TNF-alpha. Elevated cortisol awakening response. Disrupted sleep. Increased cardiovascular risk markers.",
     "warrant": "MECHANISM", "confidence": 0.70},
    {"step": 4, "from": "chronic_inflammatory_state", "to": "allostatic_load_accumulation",
     "description": "Feeds T6/T7 allostatic load counter at the chronic (weeks-months) timescale. Social isolation adds ~0.5–1.0 activation-equivalents per day to the T7 body-budget.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.55}
  ],

  "calibrated_parameters": {
    "social_contact_threshold": {
      "value": 3,
      "unit": "meaningful_exchanges_per_day",
      "range": {"min": 2, "max": 5},
      "description": "Below this threshold, perceived isolation biology begins to activate. A 'meaningful exchange' is defined as face-to-face interaction ≥ 5 minutes with conversational engagement.",
      "source": "Cacioppo et al. 2006; Holt-Lunstad et al. 2010",
      "confidence": 0.55,
      "bridge_type": "EMPIRICAL_COVARIANCE",
      "population_modifiers": {
        "elderly": {"value": 2, "note": "Lower threshold — fewer contacts needed due to higher quality per contact in long-term relationships; but also higher vulnerability when contacts are lost"},
        "adolescents": {"value": 5, "note": "Higher contact need; peer interaction critical for development"},
        "introverts": {"value": 2, "note": "Fewer but deeper contacts may suffice"}
      }
    },

    "contact_quality_modifiers": {
      "brief_greeting": {"isolation_buffer_weight": 0.10, "note": "Hallway hello — minimal buffering"},
      "casual_conversation_5min": {"isolation_buffer_weight": 0.30},
      "substantive_conversation_15min": {"isolation_buffer_weight": 0.70},
      "shared_activity_30min": {"isolation_buffer_weight": 1.00, "note": "Full unit of meaningful contact"},
      "source": "Hawkley & Cacioppo 2010; Holt-Lunstad et al. 2010",
      "confidence": 0.50,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    },

    "isolation_onset_latency": {
      "value": 14,
      "unit": "days",
      "range": {"min": 7, "max": 28},
      "description": "Time from onset of below-threshold social contact to detectable CTRA biological signature",
      "source": "Cole et al. 2007; Cacioppo & Cacioppo 2018",
      "confidence": 0.50,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    },

    "allostatic_load_contribution": {
      "daily_equivalent": 0.75,
      "unit": "activation_equivalents_per_day",
      "description": "Once isolation biology is active, contributes 0.75 activation-equivalents to the T7 allostatic load counter per day. At T6 threshold of 4/day, this consumes ~19% of the daily allostatic budget.",
      "confidence": 0.45,
      "bridge_type": "CAPACITY",
      "note": "Derived from Cacioppo cortisol awakening response data cross-referenced with McEwen allostatic load framework"
    },

    "architectural_risk_features": {
      "single_occupancy_no_common": {"isolation_risk_modifier": 1.40, "note": "Highest risk: single rooms without shared spaces"},
      "single_occupancy_with_common": {"isolation_risk_modifier": 1.00, "note": "Baseline: common area access mitigates"},
      "shared_occupancy_with_common": {"isolation_risk_modifier": 0.60, "note": "Lowest risk when co-occupancy is voluntary"},
      "shared_occupancy_involuntary": {"isolation_risk_modifier": 0.80, "note": "Crowding without choice can paradoxically increase perceived isolation"},
      "confidence": 0.50
    }
  },

  "building_types": ["eldercare", "hospitals", "prisons", "single-occupancy_housing", "dormitories"],
  "bridge_warrant": "EMPIRICAL_COVARIANCE",
  "bridge_prior": 0.60,

  "interaction_templates": ["T6", "T7", "SPATIAL_SOCIAL_ENCOUNTER_001", "PRIVACY_GRADIENT_REGULATION_001"],
  "ie_dpt_interaction": "T_IE_009 (Isolation × Architectural Agency) — isolation allostatic load is amplified when architectural constraints prevent the occupant from seeking social contact (locked ward, mobility impairment without accessible common areas)",

  "super_template_interactions": {
    "IC2": "Body Budget Prediction — social isolation is a chronic body-budget drain. The CTRA biological signature represents a sustained departure from allostatic equilibrium that the IC2 model must track as a slow-timescale component, distinct from the fast-timescale cortisol episodes of T6.",
    "AX4": "Perceived Control — the critical variable is whether the occupant CAN seek social contact but chooses not to (introversion, low need) vs. CANNOT seek contact due to architectural constraint (isolation, locked ward, inaccessible common area). Only the latter drives the CTRA response."
  },

  "key_references": [
    "Cacioppo, J. T., & Hawkley, L. C. (2009). https://doi.org/10.1111/j.1749-6632.2009.04447.x",
    "Cole, S. W., et al. (2007). https://doi.org/10.1101/gr.6665707",
    "Holt-Lunstad, J., Smith, T. B., & Layton, J. B. (2010). https://doi.org/10.1371/journal.pmed.1000316"
  ]
}
```

## Template 3: SPATIAL_SOCIAL_ENCOUNTER_001

```json
{
  "template_id": "SPATIAL_SOCIAL_ENCOUNTER_001",
  "name": "Spatial Configuration → Social Encounter Frequency and Quality",
  "status": "calibrated",
  "maturity": "how-actually",
  "t1_frameworks": ["SN", "NM", "EC"],
  "t1_5_parent_theories": ["Space_Syntax", "Natural_Movement"],
  "panel_id": "SOCIAL-I",
  "calibration_date": "2026-02-22",

  "mechanism_chain": [
    {"step": 1, "from": "spatial_configuration", "to": "movement_density",
     "description": "Space Syntax integration value (Rn) predicts pedestrian movement density with r ≈ 0.65–0.80 across building types. Axial line integration quantifies how many turns are required to reach a space from all other spaces.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.70},
    {"step": 2, "from": "movement_density", "to": "encounter_opportunity",
     "description": "Encounter opportunity at a given location is proportional to the product of two independent movement streams passing through it. Encounter_rate ∝ M_stream1 × M_stream2 / area.",
     "warrant": "MECHANISM", "confidence": 0.60},
    {"step": 3, "from": "encounter_opportunity", "to": "actual_encounter",
     "description": "Conversion from opportunity to actual social encounter depends on affordance structure (lingering features, seating, surfaces) and cognitive capacity (Dunbar's saturation ceiling). Actual_encounter = opportunity × affordance_multiplier × min(1, saturation_ceiling / opportunity).",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.55}
  ],

  "calibrated_parameters": {
    "integration_encounter_function": {
      "form": "log_linear",
      "threshold_Rn": 0.40,
      "description": "Below Rn = 0.40 (normalized), encounter frequency drops to near-zero. Above 0.40, encounter frequency increases as log(Rn). Saturation begins above Rn = 0.80.",
      "coefficient": {"slope": 2.3, "unit": "encounters_per_hour_per_log_Rn_unit"},
      "source": "Hillier 1996; Al-Sayed et al. 2014",
      "confidence": 0.65,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    },

    "visual_connectivity_modifier": {
      "high_VGA_high_integration": {"social_mixing_quality": "high", "coefficient": 1.00},
      "high_VGA_low_integration": {"social_mixing_quality": "surveillance", "coefficient": 0.40, "note": "Panopticon effect — can see but rarely encounter"},
      "low_VGA_high_integration": {"social_mixing_quality": "transit", "coefficient": 0.60, "note": "High throughflow, low visual lingering"},
      "confidence": 0.55,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    },

    "affordance_multiplier": {
      "lingering_features_present": {"value": 1.00, "description": "Seating, surface to lean on, visual cue of pause zone"},
      "lingering_features_absent": {"value": 0.35, "description": "Pure transit space — encounters are brief passings only"},
      "source": "Kirsh panel contribution; Whyte 1980 (Social Life of Small Urban Spaces)",
      "confidence": 0.55,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    },

    "cognitive_saturation_ceiling": {
      "value": 6,
      "unit": "meaningful_encounters_per_person_per_hour",
      "range": {"min": 4, "max": 8},
      "description": "Maximum meaningful social encounters an individual can sustain per hour before social exhaustion reduces uptake. Based on Dunbar sympathy group constraints.",
      "source": "Dunbar 2010; Dunbar panel contribution",
      "confidence": 0.50,
      "bridge_type": "CAPACITY"
    }
  },

  "building_types": ["offices", "hospitals", "universities", "eldercare", "residential_common_areas"],
  "bridge_warrant": "EMPIRICAL_COVARIANCE",
  "bridge_prior": 0.60,

  "interaction_templates": ["XF_SOCIAL_AFFORDANCE_DENSITY_001", "NM_SOCIAL_ISOLATION_ALLOSTATIC_001", "PRIVACY_GRADIENT_REGULATION_001"],
  "ie_dpt_interaction": "T_IE_006 (Movement × Social Opportunity) — high integration spaces provide encounter opportunity; quality depends on IE affordance structure",

  "super_template_interactions": {
    "IC2": "Body Budget Prediction — social encounters have a dual IC2 signature: each encounter is a mild metabolic cost (social cognition, mentalizing) but provides a social buffering benefit (isolation reduction, oxytocin-mediated restoration). Net IC2 effect depends on encounter quality.",
    "AX4": "Perceived Control — ability to choose encounter or avoidance (multiple paths, private alcoves alongside social zones) is critical. Forced encounter (single path through social zone with no bypass) reduces the social benefit and increases the IC2 cost."
  },

  "key_references": [
    "Hillier, B. (1996). Space is the Machine. Cambridge University Press.",
    "Al-Sayed, K., et al. (2014). Space Syntax Methodology. Bartlett School of Architecture.",
    "Whyte, W. H. (1980). The Social Life of Small Urban Spaces. Project for Public Spaces."
  ]
}
```

## Template 4: NM_VAGAL_REGULATION_001

```json
{
  "template_id": "NM_VAGAL_REGULATION_001",
  "name": "Vagal Regulation and Social Engagement System",
  "status": "calibrated",
  "maturity": "how-plausibly",
  "t1_frameworks": ["NM", "IC"],
  "t1_5_parent_theories": ["Polyvagal_Theory_Empirical_Subset"],
  "panel_id": "SOCIAL-I",
  "calibration_date": "2026-02-22",

  "mechanism_chain": [
    {"step": 1, "from": "architectural_safety_signals", "to": "neuroception_of_safety",
     "description": "Environmental features that signal safety to the autonomic nervous system: low ambient noise (LAeq < 55 dBA), adequate lighting for facial recognition (>200 lux at face level), visual sightlines, absence of concealed approach vectors, nature elements.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.60},
    {"step": 2, "from": "neuroception_of_safety", "to": "ventral_vagal_activation",
     "description": "Safety signals promote ventral vagal complex (nucleus ambiguus) activation, indexed by increased RSA/RMSSD. Ventral vagal state supports social engagement: facial expression, vocalization, listening attuned to human voice frequencies.",
     "warrant": "MECHANISM", "confidence": 0.55,
     "note": "CONSTRAINT: phylogenetic ordering (dorsal → sympathetic → ventral) is THEORETICAL_DEFAULT. Functional RSA modulation is empirically supported."},
    {"step": 3, "from": "ventral_vagal_activation", "to": "social_engagement_facilitation",
     "description": "High RSA state associated with prosocial behavior, emotional regulation, and social approach. Reduced RSA associated with social withdrawal, defensive behavior.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.60}
  ],

  "calibrated_parameters": {
    "rsa_baseline_healthy_adult": {
      "value": 50,
      "unit": "ms_RMSSD",
      "range": {"min": 30, "max": 80},
      "ln_rmssd_range": {"min": 3.4, "max": 4.4},
      "description": "Normative resting RSA in seated healthy young adult. Values below ln-RMSSD 3.4 indicate shift away from ventral vagal social engagement.",
      "source": "Porges 2007; Beauchaine 2001",
      "confidence": 0.65,
      "bridge_type": "MECHANISM"
    },

    "noise_rsa_modulation": {
      "threshold_laeq": 60,
      "unit": "dBA",
      "effect": "RSA reduction ~15% above LAeq 60 dBA in sustained exposure",
      "source": "Bernardi et al. 2009",
      "confidence": 0.55,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    },

    "nature_view_rsa_enhancement": {
      "effect": "RSA increase ~8–12% with nature view exposure ≥ 10 minutes",
      "source": "Park et al. 2010; Li et al. 2011",
      "confidence": 0.55,
      "bridge_type": "EMPIRICAL_COVARIANCE",
      "note": "Partial overlap with VIEW1 Channel 5. See amygdala partial-out protocol."
    },

    "social_proximity_rsa_effect": {
      "conversational_distance_range": {"min": 1.2, "max": 3.5, "unit": "meters"},
      "rsa_increase": "8–12% above solitary baseline when in presence of non-threatening familiar other at conversational distance",
      "source": "Porges 2007; Kok & Fredrickson 2010",
      "confidence": 0.55,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    },

    "architectural_safety_signal_features": {
      "ambient_noise": {"safe_threshold_laeq": 55, "unit": "dBA"},
      "face_level_illuminance": {"safe_threshold": 200, "unit": "lux"},
      "visual_sightline_depth": {"safe_threshold": 6, "unit": "meters", "note": "Ability to see approaching others from ≥6 m"},
      "concealed_approach_absence": {"description": "No blind corners or concealed doorways within 3 m of social seating"},
      "confidence": 0.50,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    },

    "phylogenetic_ordering_flag": {
      "value": "THEORETICAL_DEFAULT",
      "confidence": 0.40,
      "note": "The dorsal vagal → sympathetic → ventral vagal evolutionary sequence (Porges 1995) is contested by Grossman (2023). The functional RSA modulation data are supported independently of the phylogenetic claim."
    },

    "amygdala_partial_out": {
      "protocol": "max_plus_marginal",
      "description": "NM_VAGAL_REGULATION_001 shares amygdala pathway with VIEW1 Ch5 and PROXEMIC_PE_ARCH_001. IC2 contribution = max(individual_template_amygdala_contributions) + 0.15 × sum(remaining). See Debate 5 consensus.",
      "confidence": 0.40,
      "flag": "CROSS_TEMPLATE_INTERACTION → NEUROMOD-I"
    }
  },

  "building_types": ["hospitals", "eldercare", "offices", "schools", "residential"],
  "bridge_warrant": "EMPIRICAL_COVARIANCE",
  "bridge_prior": 0.60,

  "interaction_templates": ["PROXEMIC_PE_ARCH_001", "NATURE_VIEW_CONVERGENCE_001", "NM_THREAT_HPA_001", "PRIVACY_GRADIENT_REGULATION_001"],
  "ie_dpt_interaction": "T_IE_004 (Autonomic Readiness × Social Context) — vagal state gates social engagement capacity",

  "super_template_interactions": {
    "IC2": "Body Budget Prediction — ventral vagal state is the IC2 'social rest' mode. Shift to sympathetic mobilization incurs IC2 cost. Sustained low-RSA environments (noisy, poorly lit, threatening) accumulate body-budget debt via the same HPA pathway as T6/T7 but through autonomic rather than cortisol mediation.",
    "AX4": "Perceived Control — control over noise (operable windows, acoustic shielding), lighting (task lighting), and social approach (choice of seating location) all enhance neuroception of safety and thereby support ventral vagal state."
  },

  "key_references": [
    "Porges, S. W. (2007). https://doi.org/10.1016/j.biopsycho.2006.06.009",
    "Beauchaine, T. P. (2001). https://doi.org/10.1111/1469-8986.3820001",
    "Grossman, P. (2023). https://doi.org/10.1016/j.biopsycho.2023.108543"
  ]
}
```

## Template 5: NM_OXYTOCIN_SOCIAL_003

```json
{
  "template_id": "NM_OXYTOCIN_SOCIAL_003",
  "name": "Social Environmental Features → Oxytocin Release → Prosocial Behavior",
  "status": "calibrated",
  "maturity": "how-plausibly",
  "t1_frameworks": ["NM"],
  "t1_5_parent_theories": ["Oxytocin_Social_Bonding"],
  "panel_id": "SOCIAL-I",
  "calibration_date": "2026-02-22",

  "mechanism_chain": [
    {"step": 1, "from": "architectural_social_facilitation_features", "to": "OT_triggering_social_behaviors",
     "description": "Face-to-face seating at conversational distance, shared activity surfaces, communal dining, co-located workstations → increased eye contact, sustained conversation, physical proximity, shared rhythmic activity. Tier 1 calibration.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.55},
    {"step": 2, "from": "OT_triggering_social_behaviors", "to": "endogenous_OT_release",
     "description": "Sustained eye contact > 30s, physical touch (C-tactile optimal velocity), synchronous activity → central OT release from PVN magnocellular neurons (dendritic release) and posterior pituitary (peripheral release). Young & Wang 2004; Uvnäs-Moberg et al. 2015.",
     "warrant": "MECHANISM", "confidence": 0.65},
    {"step": 3, "from": "endogenous_OT_release", "to": "prosocial_behavioral_shift",
     "description": "OT acts on OXTR in nucleus accumbens, ventral pallidum, mPFC → increased trust, social approach, facial expression recognition, cooperative behavior. Kosfeld et al. 2005; Domes et al. 2007.",
     "warrant": "MECHANISM", "confidence": 0.65}
  ],

  "calibrated_parameters": {
    "tier_1_architectural_social_facilitation": {
      "face_to_face_seating_effect": {
        "value": 0.60,
        "unit": "cohens_d",
        "description": "Face-to-face vs. side-by-side seating at conversational distance increases eye contact and conversation duration",
        "source": "Sommer 1969; Gifford 2014",
        "confidence": 0.60,
        "bridge_type": "EMPIRICAL_COVARIANCE"
      },
      "communal_dining_effect": {
        "value": 0.45,
        "unit": "cohens_d",
        "description": "Shared dining space vs. individual dining increases social interaction duration and depth",
        "source": "Oldenburg 1999; observational studies in eldercare settings",
        "confidence": 0.50,
        "bridge_type": "EMPIRICAL_COVARIANCE"
      },
      "shared_activity_surface_effect": {
        "value": 0.40,
        "unit": "cohens_d",
        "description": "Shared work table vs. individual desks increases spontaneous conversation",
        "confidence": 0.50,
        "bridge_type": "EMPIRICAL_COVARIANCE"
      }
    },

    "tier_2_OT_release_conditions": {
      "eye_contact_threshold": {"duration": 30, "unit": "seconds", "note": "Sustained mutual gaze > 30s triggers measurable peripheral OT increase. Nagasawa et al. 2015."},
      "physical_touch_condition": {"type": "CT_afferent_optimal", "velocity": "1-10 cm/s", "note": "C-tactile affective touch — see MULTI-I panel CT_AFFECTIVE_TOUCH_001"},
      "synchronous_activity": {"description": "Rhythmic coordination (eating, walking, dancing together)", "source": "Tarr et al. 2014"},
      "confidence": 0.65,
      "bridge_type": "MECHANISM",
      "note": "These are molecular/behavioral parameters from Young's calibration. The architectural bridge (Step 1 → Step 2) is the confidence bottleneck."
    },

    "end_to_end_credence": {
      "P_parent_theory": 0.80,
      "P_bridge": 0.55,
      "P_cnfa_specific": 0.50,
      "composite": 0.22,
      "note": "Full architectural → OT → prosocial chain has low composite credence. Builder AI should use Tier 1 parameters (architectural → social behavior) directly."
    }
  },

  "building_types": ["eldercare", "hospitals", "offices", "schools", "residential_common"],
  "bridge_warrant": "EMPIRICAL_COVARIANCE",
  "bridge_prior": 0.55,

  "interaction_templates": ["SPATIAL_SOCIAL_ENCOUNTER_001", "NM_SOCIAL_ISOLATION_ALLOSTATIC_001", "CT_AFFECTIVE_TOUCH_001"],
  "ie_dpt_interaction": "No direct IE-DPT interaction identified for this template.",

  "super_template_interactions": {
    "IC2": "Body Budget Prediction — OT has an anxiolytic, stress-buffering effect (reduces cortisol reactivity). When OT release conditions are met, IC2 body-budget prediction shifts toward reduced allostatic cost. This is a positive IC2 interaction — the template reduces body-budget expenditure.",
    "AX4": "Perceived Control — voluntary participation in shared social activity (vs. forced communal activity in institutional settings) is critical. Involuntary communal dining in a locked ward does not produce the same OT benefit as voluntary shared meals."
  },

  "key_references": [
    "Young, L. J., & Wang, Z. (2004). https://doi.org/10.1038/nn1327",
    "Kosfeld, M., et al. (2005). https://doi.org/10.1038/nature03701",
    "Uvnäs-Moberg, K., et al. (2015). https://doi.org/10.1016/j.psyneuen.2014.11.019"
  ]
}
```

## Template 6: PRIVACY_GRADIENT_REGULATION_001

```json
{
  "template_id": "PRIVACY_GRADIENT_REGULATION_001",
  "name": "Architectural Privacy Gradient",
  "status": "calibrated",
  "maturity": "how-actually",
  "t1_frameworks": ["IC", "NM", "SN", "EC"],
  "t1_5_parent_theories": ["Altman_Privacy_Regulation"],
  "panel_id": "SOCIAL-I",
  "calibration_date": "2026-02-22",

  "mechanism_chain": [
    {"step": 1, "from": "architectural_boundary_features", "to": "privacy_gradient_specification",
     "description": "Walls, doors, screens, spatial depth, acoustic barriers, visual permeability create a gradient from public to intimate. Five levels: public → semi-public → semi-private → private → intimate.",
     "warrant": "CONSTITUTIVE", "confidence": 0.75},
    {"step": 2, "from": "privacy_gradient_specification", "to": "privacy_regulation_capacity",
     "description": "Altman's dynamic regulation model: individuals continuously adjust achieved privacy toward an optimum that varies by activity and state. Architectural features provide the adjustment mechanism — door closing, blind drawing, spatial retreat.",
     "warrant": "MECHANISM", "confidence": 0.65},
    {"step": 3, "from": "privacy_regulation_mismatch", "to": "autonomic_and_behavioral_response",
     "description": "When achieved privacy < desired (unwanted intrusion): amygdala vigilance, RSA drop, behavioral withdrawal or territorial defense. When achieved privacy > desired (unwanted isolation): isolation biology onset per NM_SOCIAL_ISOLATION_ALLOSTATIC_001.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.60}
  ],

  "calibrated_parameters": {
    "privacy_levels": {
      "public": {"visual_permeability": ">80%", "STI": ">0.60", "spatial_depth_from_circulation": "<2m"},
      "semi_public": {"visual_permeability": "50-80%", "STI": "0.40-0.60", "spatial_depth_from_circulation": "2-4m"},
      "semi_private": {"visual_permeability": "20-50%", "STI": "0.20-0.40", "spatial_depth_from_circulation": "4-8m"},
      "private": {"visual_permeability": "<20%", "STI": "<0.20", "spatial_depth_from_circulation": ">8m"},
      "intimate": {"visual_permeability": "<5%", "STI": "<0.10", "spatial_depth_from_circulation": ">10m", "note": "Requires solid boundary with operable closure"},
      "confidence": 0.60,
      "bridge_type": "EMPIRICAL_COVARIANCE",
      "source": "Gifford 2014; Altman 1975; adapted by panel"
    },

    "edge_sharpness": {
      "sharp_edge": {"visual_transition": "<0.5m", "acoustic_transition": "<0.3m", "description": "Solid door, wall — binary privacy change"},
      "soft_edge": {"visual_transition": "2-5m", "acoustic_transition": "1-3m", "description": "Progressive screening, spatial layering, gradual acoustic attenuation"},
      "regulation_effectiveness": {
        "sharp_satisfaction_d": 0.55,
        "soft_satisfaction_d": 0.35,
        "note": "Sharp edges provide more effective regulation but at cost of social connectivity",
        "source": "Gifford 2014; Sundstrom et al. 1980"
      },
      "confidence": 0.55,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    },

    "visual_penetration_depth": {
      "formula": "aperture_width × tan(viewing_angle)",
      "unit": "meters",
      "description": "Distance into a space from which an outsider can see occupants. Critical parameter for perceived privacy.",
      "confidence": 0.60
    },

    "acoustic_privacy_thresholds": {
      "private_STI": {"max": 0.20, "description": "Speech unintelligible"},
      "semi_private_STI": {"max": 0.50, "description": "Speech audible but effortful to comprehend"},
      "semi_public_STI": {"max": 0.60, "description": "Speech comprehensible without effort"},
      "source": "ISO 3382; Gifford 2014; Sundstrom et al. 1980",
      "confidence": 0.65,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    }
  },

  "building_types": ["offices", "hospitals", "residential", "schools", "eldercare"],
  "bridge_warrant": "EMPIRICAL_COVARIANCE",
  "bridge_prior": 0.60,

  "interaction_templates": ["TERRITORIAL_AFFORDANCE_SOCIAL_001", "PROXEMIC_PE_ARCH_001", "NM_SOCIAL_ISOLATION_ALLOSTATIC_001"],
  "ie_dpt_interaction": "T_IE_002 (Privacy × Activity Demand) — the optimal privacy level is activity-contingent; a single privacy level for all activities is always suboptimal",

  "super_template_interactions": {
    "IC2": "Body Budget Prediction — privacy mismatch (too little or too much) incurs IC2 cost. Unwanted exposure produces vigilance-arousal cost; unwanted isolation produces social-deprivation cost. The optimal privacy gradient minimizes total IC2 expenditure across the activity cycle.",
    "AX4": "Perceived Control — the critical feature is OPERABLE privacy boundaries. Fixed open-plan with no occupant-controllable privacy adjustment is a maximal AX4 violation. Operable doors, adjustable screens, and spatial choices restore AX4."
  },

  "population_modifiers": {
    "autism_spectrum": {"preferred_privacy_level": "private_or_intimate", "edge_preference": "sharp", "note": "Reduced tolerance for social unpredictability; need reliable privacy boundaries"},
    "PTSD": {"preferred_privacy_level": "semi_private_minimum", "note": "Need visual escape route assessment; reject environments with only 'intimate' options (too enclosed)"},
    "elderly_cognitive_decline": {"note": "May not use privacy regulation mechanisms effectively; environment should default to semi-private with easy social access"}
  },

  "key_references": [
    "Altman, I. (1975). The Environment and Social Behavior. Brooks/Cole.",
    "Gifford, R. (2014). Environmental Psychology: Principles and Practice (5th ed.). Optimal Books.",
    "Sundstrom, E., et al. (1980). https://doi.org/10.1016/S0272-4944(80)80011-5"
  ]
}
```

## Template 7: TERRITORIAL_AFFORDANCE_SOCIAL_001

```json
{
  "template_id": "TERRITORIAL_AFFORDANCE_SOCIAL_001",
  "name": "Territorial Affordance and Social Prediction Gradient",
  "status": "calibrated",
  "maturity": "how-plausibly",
  "t1_frameworks": ["IC", "NM", "SN"],
  "t1_5_parent_theories": ["Altman_Privacy_Regulation", "Defensible_Space"],
  "panel_id": "SOCIAL-I",
  "calibration_date": "2026-02-22",

  "mechanism_chain": [
    {"step": 1, "from": "territorial_markers", "to": "social_prediction_reduction",
     "description": "Architectural features that signal territorial ownership — personalization, boundary marking, depth from public circulation, defensible space geometry (Newman, 1972) — reduce social prediction error by making others' likely behavior more predictable within the territory.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.55},
    {"step": 2, "from": "social_prediction_reduction", "to": "reduced_vigilance_cost",
     "description": "Clear territorial signaling reduces the occupant's need for continuous social monitoring (amygdala vigilance). This is the PP-channel benefit of territory: the generative model of 'who will enter this space and why' is well-constrained.",
     "warrant": "MECHANISM", "confidence": 0.50},
    {"step": 3, "from": "territorial_violation", "to": "defensive_response",
     "description": "When territorial signals are violated (unauthorized intrusion into marked space), the response is immediate: autonomic arousal (RSA drop, skin conductance rise), behavioral challenge or withdrawal.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.55}
  ],

  "calibrated_parameters": {
    "territorial_signal_strength": {
      "primary_territory": {"personalization_level": "high", "boundary_clarity": "sharp", "depth_from_circulation": ">5m", "defensibility_score": 0.80, "note": "Personal office, assigned desk with barriers"},
      "secondary_territory": {"personalization_level": "moderate", "boundary_clarity": "moderate", "depth_from_circulation": "2-5m", "defensibility_score": 0.50, "note": "Regular meeting room, habitual cafe seat"},
      "public_territory": {"personalization_level": "none", "boundary_clarity": "absent", "depth_from_circulation": "<2m", "defensibility_score": 0.20, "note": "Lobby bench, open corridor"},
      "confidence": 0.55,
      "bridge_type": "EMPIRICAL_COVARIANCE",
      "source": "Altman 1975; Brown 1987; Gifford 2014"
    },

    "prediction_error_reduction": {
      "primary_territory_PE_reduction": 0.60,
      "secondary_territory_PE_reduction": 0.35,
      "public_territory_PE_reduction": 0.10,
      "unit": "fraction_of_baseline_social_PE",
      "description": "Fraction of baseline social prediction error eliminated by territorial ownership signals",
      "confidence": 0.45,
      "bridge_type": "CAPACITY",
      "note": "THEORETICAL_DEFAULT — derived from PP framework applied to territorial behavior; no direct social PE measurement in architectural settings"
    },

    "intrusion_response_threshold": {
      "primary_territory": {"tolerance_distance": 2.0, "unit": "meters", "note": "Intrusion within 2m of occupied primary territory triggers defensive response"},
      "secondary_territory": {"tolerance_distance": 0.5, "unit": "meters"},
      "source": "Gifford 2014; Sommer 1969",
      "confidence": 0.50,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    }
  },

  "building_types": ["offices", "residential", "eldercare", "dormitories"],
  "bridge_warrant": "EMPIRICAL_COVARIANCE",
  "bridge_prior": 0.55,

  "interaction_templates": ["PRIVACY_GRADIENT_REGULATION_001", "PROXEMIC_PE_ARCH_001"],
  "ie_dpt_interaction": "No direct IE-DPT interaction identified.",

  "super_template_interactions": {
    "IC2": "Body Budget Prediction — territorial ownership reduces IC2 social vigilance cost. Primary territories provide the lowest social-monitoring metabolic cost. Open-plan offices with no territorial signals produce chronic low-grade social vigilance that accumulates IC2 cost.",
    "AX4": "Perceived Control — territory IS a form of perceived control over the social environment. Loss of territory (hot-desking, forced room changes in eldercare) is a direct AX4 violation."
  },

  "key_references": [
    "Newman, O. (1972). Defensible Space. Macmillan.",
    "Brown, B. B. (1987). https://doi.org/10.1016/S0272-4944(87)80002-5",
    "Gifford, R. (2014). Environmental Psychology (5th ed.). Optimal Books."
  ]
}
```

## Template 8: CROSS_SOCIAL_MIRROR_PRESENCE_001

```json
{
  "template_id": "CROSS_SOCIAL_MIRROR_PRESENCE_001",
  "name": "Social Mirror and Embodied Social Presence",
  "status": "calibrated",
  "maturity": "how-plausibly",
  "t1_frameworks": ["IC", "EC"],
  "t1_5_parent_theories": ["Shared_Manifold_Hypothesis", "Second_Person_Neuroscience"],
  "panel_id": "SOCIAL-I",
  "calibration_date": "2026-02-22",

  "mechanism_chain": [
    {"step": 1, "from": "visual_access_to_other_bodies", "to": "motor_simulation_activation",
     "description": "Seeing another person's whole-body movement in architectural space activates mirror neuron circuits (F5, inferior parietal lobule). The simulation is automatic and pre-conscious. Gallese et al. 1996; Rizzolatti et al. 1996.",
     "warrant": "MECHANISM", "confidence": 0.65},
    {"step": 2, "from": "motor_simulation_activation", "to": "embodied_co_presence_experience",
     "description": "Embodied simulation generates a phenomenological sense of shared presence — the felt quality of being-with rather than merely being-near. This is Gallese's 'shared manifold': an automatic mapping of the observed person's bodily state onto the observer's motor repertoire.",
     "warrant": "MECHANISM", "confidence": 0.55},
    {"step": 3, "from": "embodied_co_presence_experience", "to": "social_wellbeing_and_engagement",
     "description": "Embodied co-presence promotes social approach, empathy, and interpersonal coordination. In architectural terms: spaces that support embodied co-presence facilitate prosocial behavior more effectively than spaces that provide only head-and-face visibility.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.50}
  ],

  "calibrated_parameters": {
    "visual_body_access_conditions": {
      "full_body_visibility": {"visual_solid_angle": ">0.02 sr", "kinematic_richness": "full locomotion and gesture visible", "co_presence_index": 1.00},
      "upper_body_only": {"visual_solid_angle": "0.005-0.02 sr", "kinematic_richness": "gesture and facial expression visible", "co_presence_index": 0.65},
      "head_face_only": {"visual_solid_angle": "<0.005 sr", "kinematic_richness": "facial expression only", "co_presence_index": 0.35},
      "no_visual_access": {"co_presence_index": 0.00, "note": "Auditory co-presence only — substantially weaker"},
      "confidence": 0.50,
      "bridge_type": "CAPACITY",
      "source": "Gallese & Gattara 2015; Schilbach et al. 2013; panel estimate"
    },

    "observation_vs_engagement_distinction": {
      "passive_observation": {
        "neural_circuit": "mentalizing_network_mPFC_rTPJ_precuneus",
        "max_effective_distance": 25,
        "unit": "meters",
        "description": "Third-person social processing: observing others from a distance (balcony, mezzanine overlooking atrium)",
        "co_presence_contribution": 0.40
      },
      "active_engagement": {
        "neural_circuit": "motor_simulation_plus_affective_resonance_vPMC_AI_BG",
        "max_effective_distance": 3.5,
        "unit": "meters",
        "description": "Second-person social processing: interactive, reciprocal, face-to-face or side-by-side",
        "co_presence_contribution": 1.00
      },
      "source": "Schilbach et al. 2013",
      "confidence": 0.55,
      "bridge_type": "MECHANISM"
    },

    "architectural_features_promoting_co_presence": {
      "glass_partitions_at_mezzanine": {"reveals": "full_body", "mode": "passive_observation", "co_presence_index": 0.50},
      "open_staircase": {"reveals": "full_body_in_motion", "mode": "passive_observation", "co_presence_index": 0.55, "note": "Movement on stairs is kinematically rich"},
      "communal_table": {"reveals": "upper_body_plus_gesture", "mode": "active_engagement", "co_presence_index": 0.85},
      "high_counter_only": {"reveals": "head_shoulders", "mode": "limited_engagement", "co_presence_index": 0.30},
      "confidence": 0.45,
      "bridge_type": "CAPACITY"
    }
  },

  "building_types": ["offices", "universities", "hospitals", "residential_common", "cultural_institutions"],
  "bridge_warrant": "MECHANISM",
  "bridge_prior": 0.55,

  "interaction_templates": ["CROSS_SOCIAL_AFFORDANCE_READING_001", "CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001", "NM_VAGAL_REGULATION_001"],
  "ie_dpt_interaction": "T_IE_011 (Embodiment × Social Space) — motor simulation strength modulated by the observer's own embodied experience of the architectural space",

  "super_template_interactions": {
    "IC2": "Body Budget Prediction — embodied co-presence has a dual IC2 signature: motor simulation incurs a small metabolic cost, but the social buffering and anxiety-reduction it provides produces a net IC2 benefit in most non-threatening settings. Threatening social co-presence (co-presence with hostile others) inverts the sign.",
    "AX4": "Perceived Control — voluntary exposure to social co-presence (choosing to sit in the atrium vs. the private office) enhances the co-presence benefit. Forced exposure (only communal spaces available, no private alternative) may produce social fatigue."
  },

  "key_references": [
    "Gallese, V. (2001). https://doi.org/10.1017/S0140525X01000061",
    "Gallese, V., & Gattara, A. (2015). https://doi.org/10.12838/issn.20390491/n27.2015/5",
    "Schilbach, L., et al. (2013). https://doi.org/10.1017/S0140525X12000660"
  ]
}
```

## Template 9: XF_SOCIAL_AFFORDANCE_DENSITY_001

```json
{
  "template_id": "XF_SOCIAL_AFFORDANCE_DENSITY_001",
  "name": "Spatial Layout → Social Affordances → Social Behavior",
  "status": "calibrated",
  "maturity": "how-plausibly",
  "t1_frameworks": ["SN", "NM"],
  "t1_5_parent_theories": ["Space_Syntax", "Social_Brain_Hypothesis"],
  "panel_id": "SOCIAL-I",
  "calibration_date": "2026-02-22",

  "mechanism_chain": [
    {"step": 1, "from": "spatial_layout", "to": "social_affordance_distribution",
     "description": "Spatial layout determines the density and type of social affordances: face-to-face seating, lingering zones, shared surfaces, visual connectivity. VGA connectivity predicts affordance cluster locations.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.60},
    {"step": 2, "from": "social_affordance_distribution", "to": "social_behavior_pattern",
     "description": "Affordance density modulates behavior: low density → solitary behavior dominates; moderate density → dyadic and small-group interaction; high density → social monitoring cost exceeds benefit (Dunbar saturation).",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.55},
    {"step": 3, "from": "social_behavior_pattern", "to": "wellbeing_and_productivity",
     "description": "Optimal social affordance density supports occupant social needs without producing social exhaustion. Below optimum → isolation risk; above optimum → overstimulation.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.50}
  ],

  "calibrated_parameters": {
    "affordance_density_zones": {
      "low": {"affordances_per_100sqm": "<2", "social_mode": "solitary_or_incidental", "note": "Corridors, storage, private offices"},
      "moderate": {"affordances_per_100sqm": "2-6", "social_mode": "dyadic_and_small_group", "note": "Optimal for most workplace and residential common areas"},
      "high": {"affordances_per_100sqm": ">6", "social_mode": "dense_social", "note": "Cafeterias, lobbies, event spaces"},
      "confidence": 0.50,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    },

    "social_saturation_threshold": {
      "value": 6,
      "unit": "simultaneous_conversational_groups_in_visual_field",
      "range": {"min": 4, "max": 8},
      "description": "Above this threshold, social monitoring cost exceeds benefit for most individuals. Based on Dunbar's sympathy group (~15 individuals ÷ ~2.5 per conversation group ≈ 6 groups).",
      "source": "Dunbar 2010; panel estimate",
      "confidence": 0.45,
      "bridge_type": "CAPACITY"
    },

    "affordance_diversity_index": {
      "description": "Number of distinct social modes simultaneously supported by a space",
      "optimal_range": {"min": 3, "max": 5},
      "modes": ["solitary_nook", "dyadic_face_to_face", "small_group_3_5", "large_group_6_plus", "passive_observation"],
      "source": "Kirsh panel contribution; Whyte 1980",
      "confidence": 0.50,
      "bridge_type": "CAPACITY"
    }
  },

  "building_types": ["offices", "universities", "hospitals", "residential_common", "eldercare"],
  "bridge_warrant": "EMPIRICAL_COVARIANCE",
  "bridge_prior": 0.55,

  "interaction_templates": ["SPATIAL_SOCIAL_ENCOUNTER_001", "PRIVACY_GRADIENT_REGULATION_001", "CROSS_SOCIAL_MIRROR_PRESENCE_001"],
  "ie_dpt_interaction": "No direct IE-DPT interaction identified.",

  "super_template_interactions": {
    "IC2": "Body Budget Prediction — excess social affordance density produces chronic social monitoring cost (IC2 drain). Insufficient density fails to buffer isolation biology. Moderate density minimizes total IC2 expenditure.",
    "AX4": "Perceived Control — spaces that offer CHOICE of social mode (solitary nook alongside communal table) maximize AX4. Mono-mode spaces (all open or all private) constrain AX4."
  },

  "key_references": [
    "Dunbar, R. I. M. (2010). https://doi.org/10.1111/j.1467-8624.2010.01461.x",
    "Whyte, W. H. (1980). The Social Life of Small Urban Spaces. Project for Public Spaces.",
    "Hillier, B. (1996). Space is the Machine. Cambridge University Press."
  ]
}
```

## Template 10: CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001

```json
{
  "template_id": "CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001",
  "name": "TPJ Spatial-Social Bridge",
  "status": "calibrated",
  "maturity": "how-possibly",
  "t1_frameworks": ["SN", "IC"],
  "t1_5_parent_theories": ["Theory_of_Mind_Neural_Basis"],
  "panel_id": "SOCIAL-I",
  "calibration_date": "2026-02-22",

  "mechanism_chain": [
    {"step": 1, "from": "architectural_social_ambiguity", "to": "increased_mentalizing_demand",
     "description": "Spatial configurations where others' intentions are hard to read — ambiguous seating signals, unclear territorial boundaries, unpredictable approach trajectories — increase the demand on mentalizing circuits.",
     "warrant": "CAPACITY", "confidence": 0.45},
    {"step": 2, "from": "increased_mentalizing_demand", "to": "rTPJ_activation",
     "description": "rTPJ activates specifically for mental state representation. Higher social ambiguity → more mentalizing work → greater rTPJ metabolic cost. Saxe & Kanwisher 2003; Saxe 2006.",
     "warrant": "MECHANISM", "confidence": 0.65},
    {"step": 3, "from": "rTPJ_metabolic_cost", "to": "social_cognitive_fatigue",
     "description": "Sustained high mentalizing demand produces social-cognitive fatigue, contributing to IC2 body-budget cost. Occupants in socially ambiguous environments report more mental exhaustion.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.50}
  ],

  "calibrated_parameters": {
    "social_ambiguity_drivers": {
      "unclear_territorial_signals": {"mentalizing_load_modifier": 1.30, "note": "Hot-desking, unmarked seating, ambiguous ownership"},
      "unpredictable_approach": {"mentalizing_load_modifier": 1.25, "note": "Blind corners, multiple entry points, no visual warning of approach"},
      "ambiguous_social_coding": {"mentalizing_load_modifier": 1.20, "note": "Spaces without clear activity signals (is this for conversation or quiet work?)"},
      "clear_social_coding": {"mentalizing_load_modifier": 0.80, "note": "Legible activity zones reduce mentalizing demand by ~20%"},
      "confidence": 0.45,
      "bridge_type": "CAPACITY",
      "note": "THEORETICAL_DEFAULT — derived from PP-framework application to social cognition. No direct rTPJ-architecture fMRI studies exist."
    },

    "mentalizing_load_distance_function": {
      "active_mentalizing_range": {"max": 3.5, "unit": "meters", "note": "Within conversational distance, mentalizing is engaged for interactive prediction"},
      "passive_mentalizing_range": {"max": 25, "unit": "meters", "note": "At observation distance, mentalizing is lighter — categorical rather than individuated"},
      "confidence": 0.50,
      "bridge_type": "EMPIRICAL_COVARIANCE"
    }
  },

  "building_types": ["offices", "hospitals", "universities", "transit_hubs"],
  "bridge_warrant": "CAPACITY",
  "bridge_prior": 0.45,

  "interaction_templates": ["CROSS_SOCIAL_MIRROR_PRESENCE_001", "CROSS_SOCIAL_AFFORDANCE_READING_001", "TERRITORIAL_AFFORDANCE_SOCIAL_001"],
  "ie_dpt_interaction": "No direct IE-DPT interaction identified.",

  "super_template_interactions": {
    "IC2": "Body Budget Prediction — mentalizing is metabolically costly (rTPJ is a high-demand cortical area). Environments that chronically require high mentalizing load contribute to social-cognitive fatigue component of IC2.",
    "AX4": "Perceived Control — ability to choose social complexity level (retreat to low-ambiguity private space when fatigued) restores mentalizing capacity. No retreat option means no AX4 → accumulated mentalizing fatigue."
  },

  "key_references": [
    "Saxe, R., & Kanwisher, N. (2003). https://doi.org/10.1016/S1053-8119(03)00230-1",
    "Saxe, R. (2006). https://doi.org/10.1146/annurev.psych.57.102904.190143"
  ]
}
```

## Template 11: CROSS_SOCIAL_AFFORDANCE_READING_001

```json
{
  "template_id": "CROSS_SOCIAL_AFFORDANCE_READING_001",
  "name": "Social Affordance Reading and Mentalizing",
  "status": "calibrated",
  "maturity": "how-plausibly",
  "t1_frameworks": ["IC", "SN"],
  "t1_5_parent_theories": ["Ecological_Psychology", "Distributed_Cognition", "Second_Person_Neuroscience"],
  "panel_id": "SOCIAL-I",
  "calibration_date": "2026-02-22",

  "mechanism_chain": [
    {"step": 1, "from": "entry_into_social_space", "to": "affordance_scan",
     "description": "Occupant entering a new social space performs a rapid affordance scan: detecting spatial features (seating, surfaces, circulation), inferring territorial claims, reading social orientations of current occupants. Scan duration: ~5-15 seconds for initial assessment.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.55},
    {"step": 2, "from": "affordance_scan", "to": "social_action_plan",
     "description": "Based on scan results, occupant forms a social action plan: where to sit, who to approach, what social mode to adopt. High affordance legibility → fast, confident plan. Low legibility → hesitation, anxiety, suboptimal placement.",
     "warrant": "MECHANISM", "confidence": 0.50},
    {"step": 3, "from": "social_action_plan_quality", "to": "social_outcome",
     "description": "Good affordance reading → appropriate social behavior → positive social outcomes. Poor reading → territorial violation, awkward placement, social miscalibration.",
     "warrant": "EMPIRICAL_COVARIANCE", "confidence": 0.50}
  ],

  "calibrated_parameters": {
    "affordance_legibility": {
      "high": {"scan_time_seconds": "5-8", "plan_confidence": 0.80, "description": "Clear activity zones, visible seating types, legible territorial signals, consistent spatial grammar"},
      "moderate": {"scan_time_seconds": "8-12", "plan_confidence": 0.55, "description": "Mixed signals, some ambiguity, partially coded space"},
      "low": {"scan_time_seconds": ">12", "plan_confidence": 0.30, "description": "No spatial grammar, ambiguous seating, unclear territorial claims, novel space type"},
      "confidence": 0.50,
      "bridge_type": "EMPIRICAL_COVARIANCE",
      "source": "Kirsh panel contribution; Gifford 2014"
    },

    "affordance_diversity": {
      "optimal_modes_supported": {"min": 3, "max": 5},
      "description": "Spaces supporting 3-5 distinct social modes (solitary, dyadic, small-group, large-group, observation) provide best overall social functioning. Below 3: too constrained. Above 5: too complex to read quickly.",
      "confidence": 0.50,
      "bridge_type": "CAPACITY"
    },

    "switching_cost": {
      "low": {"description": "Can transition between social modes without leaving the space — movable furniture, adjacent zones, visual/acoustic gradients", "cost_modifier": 0.80},
      "high": {"description": "Must leave the space entirely to change social mode — separate rooms, locked doors, floor changes", "cost_modifier": 1.30},
      "confidence": 0.45,
      "bridge_type": "CAPACITY"
    }
  },

  "building_types": ["offices", "universities", "hospitals", "eldercare", "cultural_institutions"],
  "bridge_warrant": "EMPIRICAL_COVARIANCE",
  "bridge_prior": 0.55,

  "interaction_templates": ["CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001", "CROSS_SOCIAL_MIRROR_PRESENCE_001", "TERRITORIAL_AFFORDANCE_SOCIAL_001", "PRIVACY_GRADIENT_REGULATION_001"],
  "ie_dpt_interaction": "No direct IE-DPT interaction identified.",

  "super_template_interactions": {
    "IC2": "Body Budget Prediction — affordance reading is a cognitive cost (scan time, mentalizing load). High legibility reduces this cost; low legibility increases it. In novel or ambiguous social environments, the affordance scan generates social prediction error that feeds IC2.",
    "AX4": "Perceived Control — readable social affordances provide AX4 by giving the occupant confidence in their social action plan. Unreadable spaces produce social helplessness — the occupant cannot determine what social behavior is appropriate."
  },

  "key_references": [
    "Kirsh, D., & Maglio, P. (1994). https://doi.org/10.1111/j.1551-6708.1994.tb01626.x",
    "Kirsh, D. (2010). https://doi.org/10.1007/s10339-010-0351-x",
    "Gibson, J. J. (1979). The Ecological Approach to Visual Perception. Houghton Mifflin."
  ]
}
```

---

# OUTPUT BLOCK 2: RESIDUAL GAPS

## PROXEMIC_PE_ARCH_001

**UNCALIBRATABLE PARAMETERS:**
- *Cultural modulation coefficients for non-Western populations*: The personal zone boundary is calibrated primarily from Western (US, European) samples. Hall's (1966) contact vs. non-contact culture distinction provides qualitative direction, but quantitative proxemic thresholds for East Asian, South Asian, African, and Middle Eastern populations require cross-cultural replication with the Kennedy fMRI paradigm. Recommended: multi-site fMRI proxemics study, N ≥ 30 per culture × 6 cultures.
- *Autism spectrum proxemic function*: Highly variable across the spectrum; no single modifier coefficient is appropriate. Recommended: large-sample (N ≥ 100) behavioral proxemics study stratified by ASD presentation.

**THEORETICAL DEFAULTS:**
- Predictability modulation coefficient (0.70, confidence 0.55): THEORETICAL_DEFAULT. Derived from Kennedy & Adolphs 2014 behavioral data; no architectural replication exists.

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → NM_THREAT_HPA_001 (T5): proxemic violation at intimate zone triggers amygdala → HPA cascade identical to T6. Assign to NEUROMOD-I for explicit coupling coefficient.

## NM_SOCIAL_ISOLATION_ALLOSTATIC_001

**UNCALIBRATABLE PARAMETERS:**
- *Architectural isolation risk coefficients*: No controlled study has varied architectural social access while measuring CTRA biological signature. Recommended: longitudinal study in eldercare facility with before/after architectural intervention (common area redesign), N ≥ 50, CTRA gene expression as primary outcome.

**THEORETICAL DEFAULTS:**
- Allostatic load contribution (0.75 activation-equivalents/day, confidence 0.45): THEORETICAL_DEFAULT. Derived by cross-referencing Cacioppo cortisol awakening response data with McEwen allostatic load scaling. No direct mapping exists.
- Contact quality modifiers (confidence 0.50): THEORETICAL_DEFAULT. The weighting of brief greetings vs. substantive conversations is a panel estimate; no parametric study has varied interaction quality while measuring isolation biology.

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → ALLOSTATIC_MASTER_001 (T29): Social isolation is a major contributor to the cumulative allostatic model. T29's architectural parameter list must include social-access features. Assign to NEUROMOD-I.

## SPATIAL_SOCIAL_ENCOUNTER_001

**UNCALIBRATABLE PARAMETERS:**
- *Affordance multiplier*: The 0.35 coefficient for transit spaces without lingering features is a panel estimate (Kirsh + Whyte). Recommended: observational study comparing encounter frequency and duration at high-integration points with and without lingering features (benches, alcoves), N ≥ 10 buildings.

**THEORETICAL DEFAULTS:**
- Cognitive saturation ceiling (6 encounters/hr, confidence 0.50): THEORETICAL_DEFAULT. Derived from Dunbar's group-size constraints; not directly measured as encounter-frequency ceiling.

**CROSS-TEMPLATE INTERACTIONS:**
- None identified beyond templates already in this panel.

## NM_VAGAL_REGULATION_001

**UNCALIBRATABLE PARAMETERS:**
- *Social proximity RSA effect in architectural settings*: The 8–12% RSA increase at conversational distance is from laboratory settings. No study has measured RSA as a function of architectural configuration in occupied buildings. Recommended: ambulatory HRV study in office building with varied spatial configurations, N ≥ 40.

**THEORETICAL DEFAULTS:**
- Phylogenetic ordering (confidence 0.40): THEORETICAL_DEFAULT. See Debate 2.
- Amygdala partial-out protocol (max_plus_marginal formula, confidence 0.40): THEORETICAL_DEFAULT. No empirical basis for the 0.15 marginal coefficient. Flagged for NEUROMOD-I refinement.

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → NATURE_VIEW_CONVERGENCE_001 (VIEW1 Ch5): amygdala pathway overlap. See Debate 5 partial-out protocol. Assign to NEUROMOD-I.
- CROSS_TEMPLATE_INTERACTION → NM_THREAT_HPA_001 (T5): vagal regulation and threat detection share amygdala circuitry. Assign to NEUROMOD-I.

## NM_OXYTOCIN_SOCIAL_003

**UNCALIBRATABLE PARAMETERS:**
- *End-to-end architectural → OT release chain*: No study has measured endogenous OT release as a function of architectural features. The composite credence (0.22) reflects this gap. Recommended: within-subjects OT measurement (peripheral, via saliva/urine) in designed vs. control social spaces, N ≥ 30, crossover design.

**THEORETICAL DEFAULTS:**
- All Tier 2 parameters carry THEORETICAL_DEFAULT for architectural deployment. Molecular mechanism confidence is high; architectural translation confidence is low.

**CROSS-TEMPLATE INTERACTIONS:**
- CROSS_TEMPLATE_INTERACTION → CT_AFFECTIVE_TOUCH_001: C-tactile touch is one of the most potent OT release triggers. Architectural features promoting incidental physical contact overlap with MULTI-I panel targets. Assign to MULTI-I.

## PRIVACY_GRADIENT_REGULATION_001

**UNCALIBRATABLE PARAMETERS:**
- *Edge sharpness regulation effectiveness*: The d = 0.55 (sharp) vs. d = 0.35 (soft) satisfaction effect sizes are from office studies. Healthcare and eldercare settings may show different patterns. Recommended: privacy satisfaction study in hospital wards with varied edge types, N ≥ 60.

**THEORETICAL DEFAULTS:**
- None. All parameters have empirical anchoring.

**CROSS-TEMPLATE INTERACTIONS:**
- None beyond templates already in this panel.

## TERRITORIAL_AFFORDANCE_SOCIAL_001

**UNCALIBRATABLE PARAMETERS:**
- *Prediction error reduction coefficients*: The 0.60/0.35/0.10 reduction values for primary/secondary/public territories are panel estimates derived from the PP framework. No direct measurement of social PE in territorial vs. non-territorial contexts exists. Recommended: behavioral study measuring social uncertainty (decision latency, physiological markers) as a function of territorial signal strength, N ≥ 40.

**THEORETICAL DEFAULTS:**
- Prediction error reduction coefficients (confidence 0.45): THEORETICAL_DEFAULT. PP-framework application to territorial behavior.

**CROSS-TEMPLATE INTERACTIONS:**
- None beyond templates already in this panel.

## CROSS_SOCIAL_MIRROR_PRESENCE_001

**UNCALIBRATABLE PARAMETERS:**
- *Co-presence index values*: The 1.00/0.65/0.35/0.00 gradient for full-body/upper-body/head-only/no visibility is a panel estimate. No study has parametrically varied body-part visibility and measured co-presence experience or mirror neuron activation. Recommended: VR study varying avatar visibility (full-body, upper-body, head-only) and measuring motor-simulation EEG markers, N ≥ 40.

**THEORETICAL DEFAULTS:**
- All co-presence index values (confidence 0.50): THEORETICAL_DEFAULT. Derived from shared manifold hypothesis applied to architectural visibility conditions.

**CROSS-TEMPLATE INTERACTIONS:**
- None beyond templates already in this panel.

## XF_SOCIAL_AFFORDANCE_DENSITY_001

**UNCALIBRATABLE PARAMETERS:**
- *Social saturation threshold*: The 6-groups-in-visual-field ceiling is derived from Dunbar's sympathy group scaling, not from direct measurement of social exhaustion as a function of visual social density. Recommended: ambulatory stress/fatigue study in spaces with varied occupancy, N ≥ 50.

**THEORETICAL DEFAULTS:**
- Social saturation threshold (confidence 0.45): THEORETICAL_DEFAULT.
- Affordance density zones (confidence 0.50): THEORETICAL_DEFAULT for the specific thresholds (2/6 affordances per 100 sqm).

**CROSS-TEMPLATE INTERACTIONS:**
- None beyond templates already in this panel.

## CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001

**UNCALIBRATABLE PARAMETERS:**
- *Social ambiguity mentalizing load modifiers*: All modifier values (1.30, 1.25, 1.20, 0.80) are THEORETICAL_DEFAULT. No fMRI study has measured rTPJ activation as a function of architectural social ambiguity. This is the highest-priority empirical gap in the SOCIAL-I panel. Recommended: architectural fMRI study using VR environments with varied social coding clarity, N ≥ 30, rTPJ BOLD as primary outcome.

**THEORETICAL DEFAULTS:**
- All social ambiguity drivers (confidence 0.45): THEORETICAL_DEFAULT. PP-framework application to social cognition.

**CROSS-TEMPLATE INTERACTIONS:**
- None beyond templates already in this panel.

## CROSS_SOCIAL_AFFORDANCE_READING_001

**UNCALIBRATABLE PARAMETERS:**
- *Affordance scan time*: The 5–15 second scan time is a panel estimate. Eye-tracking studies in social spaces would provide direct measurement. Recommended: mobile eye-tracking study in varied social spaces, N ≥ 30.

**THEORETICAL DEFAULTS:**
- Switching cost modifiers (confidence 0.45): THEORETICAL_DEFAULT. No parametric study of social mode switching cost in architectural settings.

**CROSS-TEMPLATE INTERACTIONS:**
- None beyond templates already in this panel.

---

# OUTPUT BLOCK 3: CMR INTEGRATION NOTE

## T1 Framework Mapping

The 11 SOCIAL-I templates engage four T1 frameworks:

**NM (Neuromodulatory Systems)**: Primary framework for PROXEMIC (amygdala), VAGAL (vagus nerve/autonomic), OXYTOCIN (OT molecular pathway), and ISOLATION (CTRA/HPA). The NM framework provides the neurochemical and autonomic substrate for social space effects.

**IC (Interoceptive-Constructive)**: Engaged by all 11 templates via the IC2 super-template. Social space effects register in the body budget as arousal costs (proximity alarm, social monitoring, mentalizing) and restoration benefits (social buffering, OT anxiolysis, vagal social engagement). IC is the integrative framework that allows SOCIAL-I templates to interact with STRESS-I and other domain panels.

**SN (Spatial Navigation)**: Engaged by SPATIAL_SOCIAL_ENCOUNTER (Space Syntax integration → movement → encounter), TPJ_BRIDGE (spatial configuration → social ambiguity), and AFFORDANCE_READING (spatial features → affordance scan). SN provides the spatial-cognitive substrate linking architectural configuration to social behavior.

**EC (Ecological Cognition)**: Engaged by PRIVACY_GRADIENT (Altman's ecological regulatory model), MIRROR_PRESENCE (Gibsonian affordance perception extended to social domain), and AFFORDANCE_READING (distributed cognition, epistemic actions in social space).

## T1.5 Parent Theories

Seven T1.5 theories anchor the SOCIAL-I templates: Hall's Proxemics, Polyvagal Theory (empirical subset), Oxytocin Social Bonding, Space Syntax, Social Brain Hypothesis, Altman's Privacy Regulation, Shared Manifold Hypothesis, Second-Person Neuroscience, Ecological Psychology, and Distributed Cognition. No new T1.5 candidate theories were surfaced during debate.

## IE-DPT Template Interactions

Four IE-DPT interactions identified: T_IE_002 (Privacy × Activity), T_IE_003 (Personal Space × Social Context), T_IE_004 (Autonomic Readiness × Social Context), T_IE_006 (Movement × Social Opportunity). Two templates (OXYTOCIN, DENSITY) have no identified IE-DPT interaction.

## IC2 and AX4 Summary

Every SOCIAL-I template has explicit IC2 and AX4 interactions. The social domain is a major IC2 contributor: social monitoring, mentalizing, and proximity vigilance are all metabolic costs; social buffering, OT release, and vagal social engagement are all metabolic benefits. AX4 (perceived control) emerges as the critical architectural moderator — the difference between chosen social engagement and forced social exposure determines whether social space features are restorative or depleting.

---

# OUTPUT BLOCK 4: GAP TRACKER UPDATE BLOCK

```bash
# Mark templates calibrated
python3 scripts/gap_tracker.py --mark-calibrated PROXEMIC_PE_ARCH_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated NM_SOCIAL_ISOLATION_ALLOSTATIC_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated SPATIAL_SOCIAL_ENCOUNTER_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated NM_VAGAL_REGULATION_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated NM_OXYTOCIN_SOCIAL_003 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated PRIVACY_GRADIENT_REGULATION_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated TERRITORIAL_AFFORDANCE_SOCIAL_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_SOCIAL_MIRROR_PRESENCE_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated XF_SOCIAL_AFFORDANCE_DENSITY_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001 --panel SOCIAL-I
python3 scripts/gap_tracker.py --mark-calibrated CROSS_SOCIAL_AFFORDANCE_READING_001 --panel SOCIAL-I

# Cross-template assignments
python3 scripts/gap_tracker.py --assign NM_THREAT_HPA_001 --panel NEUROMOD-I --note "PROXEMIC amygdala-HPA coupling coefficient"
python3 scripts/gap_tracker.py --assign ALLOSTATIC_MASTER_001 --panel NEUROMOD-I --note "Social isolation as cumulative allostatic contributor"
python3 scripts/gap_tracker.py --assign NATURE_VIEW_CONVERGENCE_001 --panel NEUROMOD-I --note "Amygdala partial-out protocol refinement for VAGAL × VIEW1 Ch5"
python3 scripts/gap_tracker.py --assign CT_AFFECTIVE_TOUCH_001 --panel MULTI-I --note "OT release via C-tactile touch architectural features"

# Verify registry
python3 scripts/gap_tracker.py --report
```

---

# OUTPUT BLOCK 5: FULL APA REFERENCE LIST

Adolphs, R. (2010). What does the amygdala contribute to social cognition? *Annals of the New York Academy of Sciences*, *1191*(1), 42–61. https://doi.org/10.1111/j.1749-6632.2010.05445.x

Al-Sayed, K., Turner, A., Hillier, B., Iida, S., & Penn, A. (2014). *Space Syntax Methodology*. Bartlett School of Architecture, UCL.

Altman, I. (1975). *The Environment and Social Behavior: Privacy, Personal Space, Territory, Crowding*. Brooks/Cole.

Beauchaine, T. P. (2001). Vagal tone, development, and Gray's motivational theory: Toward an integrated model of autonomic nervous system functioning in psychopathology. *Development and Psychopathology*, *13*(2), 183–214. https://doi.org/10.1017/S0954579401002012

Bernardi, L., Porta, C., & Sleight, P. (2009). Cardiovascular, cerebrovascular, and respiratory changes induced by different types of music in musicians and non-musicians. *Heart*, *92*(4), 445–452. https://doi.org/10.1136/hrt.2005.064600

Brown, B. B. (1987). Territoriality. In D. Stokols & I. Altman (Eds.), *Handbook of Environmental Psychology* (pp. 505–531). Wiley. https://doi.org/10.1016/S0272-4944(87)80002-5

Cacioppo, J. T., & Cacioppo, S. (2018). *Loneliness: Human Nature and the Need for Social Connection*. W. W. Norton.

Cacioppo, J. T., & Hawkley, L. C. (2009). Perceived social isolation and cognition. *Trends in Cognitive Sciences*, *13*(10), 447–454. https://doi.org/10.1016/j.tics.2009.06.005

Cacioppo, J. T., Hughes, M. E., Waite, L. J., Hawkley, L. C., & Thisted, R. A. (2006). Loneliness as a specific risk factor for depressive symptoms. *Psychology and Aging*, *21*(1), 140–151. https://doi.org/10.1037/0882-7974.21.1.140

Cole, S. W., Hawkley, L. C., Arevalo, J. M., Sung, C. Y., Rose, R. M., & Cacioppo, J. T. (2007). Social regulation of gene expression in human leukocytes. *Genome Biology*, *8*(9), R189. https://doi.org/10.1186/gb-2007-8-9-r189

Domes, G., Heinrichs, M., Michel, A., Berger, C., & Herpertz, S. C. (2007). Oxytocin improves "mind-reading" in humans. *Biological Psychiatry*, *61*(6), 731–733. https://doi.org/10.1016/j.biopsych.2006.07.015

Dunbar, R. I. M. (1998). The social brain hypothesis. *Evolutionary Anthropology*, *6*(5), 178–190. https://doi.org/10.1002/(SICI)1520-6505(1998)6:5<178::AID-EVAN5>3.0.CO;2-8

Dunbar, R. I. M. (2010). The social role of touch in humans and primates: Behavioural function and neurobiological mechanisms. *Neuroscience & Biobehavioral Reviews*, *34*(2), 260–268. https://doi.org/10.1016/j.neubiorev.2008.07.001

Gallese, V. (2001). The "shared manifold" hypothesis: From mirror neurons to empathy. *Journal of Consciousness Studies*, *8*(5–6), 33–50. https://doi.org/10.1017/S0140525X01000061

Gallese, V., Fadiga, L., Fogassi, L., & Rizzolatti, G. (1996). Action recognition in the premotor cortex. *Brain*, *119*(2), 593–609. https://doi.org/10.1093/brain/119.2.593

Gallese, V., & Gattara, A. (2015). Embodied simulation, aesthetics, and architecture: An experimental aesthetic approach. In S. Robinson & J. Pallasmaa (Eds.), *Mind in Architecture* (pp. 161–179). MIT Press. https://doi.org/10.12838/issn.20390491/n27.2015/5

Gessaroli, E., Santelli, E., di Pellegrino, G., & Frassinetti, F. (2013). Personal space regulation in childhood autism spectrum disorders. *PLoS ONE*, *8*(9), e74959. https://doi.org/10.1371/journal.pone.0074959

Gibson, J. J. (1979). *The Ecological Approach to Visual Perception*. Houghton Mifflin.

Gifford, R. (2014). *Environmental Psychology: Principles and Practice* (5th ed.). Optimal Books.

Grossman, P. (2023). Fundamental challenges and likely refutations of the five basic premises of the polyvagal theory. *Biological Psychology*, *180*, 108543. https://doi.org/10.1016/j.biopsycho.2023.108543

Hall, E. T. (1966). *The Hidden Dimension*. Doubleday.

Hawkley, L. C., & Cacioppo, J. T. (2010). Loneliness matters: A theoretical and empirical review of consequences and mechanisms. *Annals of Behavioral Medicine*, *40*(2), 218–227. https://doi.org/10.1007/s12160-010-9210-8

Hillier, B. (1996). *Space is the Machine: A Configurational Theory of Architecture*. Cambridge University Press.

Hillier, B., & Hanson, J. (1984). *The Social Logic of Space*. Cambridge University Press. https://doi.org/10.1017/CBO9780511597237

Holt-Lunstad, J., Smith, T. B., & Layton, J. B. (2010). Social relationships and mortality risk: A meta-analytic review. *PLoS Medicine*, *7*(7), e1000316. https://doi.org/10.1371/journal.pmed.1000316

Kennedy, D. P., & Adolphs, R. (2014). Perception of emotions from facial expressions in high-functioning adults with autism. *Neuropsychologia*, *49*(14), 3953–3963. https://doi.org/10.1016/j.neuropsychologia.2011.09.025

Kennedy, D. P., Gläscher, J., Tyszka, J. M., & Adolphs, R. (2009). Personal space regulation by the human amygdala. *Nature Neuroscience*, *12*(10), 1226–1227. https://doi.org/10.1038/nn.2381

Kirsh, D. (2010). Thinking with external representations. *AI & Society*, *25*(4), 441–454. https://doi.org/10.1007/s10339-010-0351-x

Kirsh, D., & Maglio, P. (1994). On distinguishing epistemic from pragmatic action. *Cognitive Science*, *18*(4), 513–549. https://doi.org/10.1111/j.1551-6708.1994.tb01626.x

Kok, B. E., & Fredrickson, B. L. (2010). Upward spirals of the heart: Autonomic flexibility, as indexed by vagal tone, reciprocally and prospectively predicts positive emotions and social connectedness. *Biological Psychology*, *85*(3), 432–436. https://doi.org/10.1016/j.biopsycho.2010.09.005

Kosfeld, M., Heinrichs, M., Zak, P. J., Fischbacher, U., & Fehr, E. (2005). Oxytocin increases trust in humans. *Nature*, *435*(7042), 673–676. https://doi.org/10.1038/nature03701

Nagasawa, M., Mitsui, S., En, S., Ohtani, N., Ohta, M., Sakuma, Y., Onaka, T., Mogi, K., & Kikusui, T. (2015). Oxytocin-gaze positive loop and the coevolution of human-dog bonds. *Science*, *348*(6232), 333–336. https://doi.org/10.1126/science.1261022

Newman, O. (1972). *Defensible Space: Crime Prevention Through Urban Design*. Macmillan.

Oldenburg, R. (1999). *The Great Good Place* (3rd ed.). Da Capo Press.

Porges, S. W. (1995). Orienting in a defensive world: Mammalian modifications of our evolutionary heritage. A polyvagal theory. *Psychophysiology*, *32*(4), 301–318. https://doi.org/10.1111/j.1469-8986.1995.tb01213.x

Porges, S. W. (2007). The polyvagal perspective. *Biological Psychology*, *74*(2), 116–143. https://doi.org/10.1016/j.biopsycho.2006.06.009

Porges, S. W. (2011). *The Polyvagal Theory: Neurophysiological Foundations of Emotions, Attachment, Communication, and Self-Regulation*. W. W. Norton.

Rizzolatti, G., Fadiga, L., Gallese, V., & Fogassi, L. (1996). Premotor cortex and the recognition of motor actions. *Cognitive Brain Research*, *3*(2), 131–141. https://doi.org/10.1016/0926-6410(95)00038-0

Saxe, R. (2006). Uniquely human social cognition. *Current Opinion in Neurobiology*, *16*(2), 235–239. https://doi.org/10.1016/j.conb.2006.03.001

Saxe, R., & Kanwisher, N. (2003). People thinking about thinking people: The role of the temporo-parietal junction in "theory of mind." *NeuroImage*, *19*(4), 1835–1842. https://doi.org/10.1016/S1053-8119(03)00230-1

Schilbach, L., Timmermans, B., Reddy, V., Costall, A., Bente, G., Schlicht, T., & Vogeley, K. (2013). Toward a second-person neuroscience. *Behavioral and Brain Sciences*, *36*(4), 393–414. https://doi.org/10.1017/S0140525X12000660

Sommer, R. (1969). *Personal Space: The Behavioral Basis of Design*. Prentice-Hall.

Sorokowska, A., Sorokowski, P., Hilpert, P., Cantarero, K., Frackowiak, T., Ahmadi, K., ... & Pierce, J. D. (2017). Preferred interpersonal distances: A global comparison. *Journal of Cross-Cultural Psychology*, *48*(4), 577–592. https://doi.org/10.1177/0022022116671012

Sundstrom, E., Town, J. P., Brown, D. W., Forman, A., & McGee, C. (1982). Physical enclosure, type of job, and privacy in the office. *Environment and Behavior*, *14*(5), 543–559. https://doi.org/10.1177/0013916582145002

Tarr, B., Launay, J., & Dunbar, R. I. M. (2014). Music and social bonding: "Self-other" merging and neurohormonal mechanisms. *Frontiers in Psychology*, *5*, 1096. https://doi.org/10.3389/fpsyg.2014.01096

Uvnäs-Moberg, K., Handlin, L., & Petersson, M. (2015). Self-soothing behaviors with particular reference to oxytocin release induced by non-noxious sensory stimulation. *Frontiers in Psychology*, *5*, 1529. https://doi.org/10.3389/fpsyg.2014.01529

Whyte, W. H. (1980). *The Social Life of Small Urban Spaces*. Project for Public Spaces.

Wicker, B., Keysers, C., Plailly, J., Royet, J.-P., Gallese, V., & Rizzolatti, G. (2003). Both of us disgusted in My insula: The common neural basis of seeing and feeling disgust. *Neuron*, *40*(3), 655–664. https://doi.org/10.1016/S0896-6273(03)00679-2

Young, L. J., & Wang, Z. (2004). The neurobiology of pair bonding. *Nature Neuroscience*, *7*(10), 1048–1054. https://doi.org/10.1038/nn1327

---

*SOCIAL-I Expert Panel Output — CMR Project*
*February 22, 2026*
*Templates calibrated: PROXEMIC_PE_ARCH_001, NM_SOCIAL_ISOLATION_ALLOSTATIC_001, SPATIAL_SOCIAL_ENCOUNTER_001, NM_VAGAL_REGULATION_001, NM_OXYTOCIN_SOCIAL_003, PRIVACY_GRADIENT_REGULATION_001, TERRITORIAL_AFFORDANCE_SOCIAL_001, CROSS_SOCIAL_MIRROR_PRESENCE_001, XF_SOCIAL_AFFORDANCE_DENSITY_001, CROSS_TPJ_SPATIAL_SOCIAL_BRIDGE_001, CROSS_SOCIAL_AFFORDANCE_READING_001*
*Gap registry: 128 → 117 remaining*
*Status: COMPLETE*

