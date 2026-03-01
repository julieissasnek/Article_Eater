#!/usr/bin/env python3
"""
Add Toulmin justification objects to MULTI-I templates (9 templates).
For each mechanism step, generate: data, backing, qualifier, rebuttal, competing_accounts, depth_tier, panel_debate_reference.
"""

import json
import os
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "data" / "templates"

# Define Toulmin justifications for each template's mechanism steps
JUSTIFICATIONS = {
    "CROSSMODAL_CONGRUENCE_001": [
        {
            "step": 1,
            "justification": {
                "data": [
                    "Multi-sensory spatial information is processed by modality-specific neural systems",
                    "Visual spatial maps encode object locations (dorsal stream, parietal cortex)",
                    "Auditory spatial maps encode sound source locations (superior temporal cortex, IC)",
                    "Haptic spatial maps localize contact points (SI/SII cortex)",
                    "Olfactory localization is achieved through nostril comparison and head movement"
                ],
                "backing": "Foundational neuroanatomy of spatial processing from Stein & Meredith (1993). Visual dorsal stream is established from Ungerleider & Mishkin (1982). Auditory spatial processing from King & Carlile (1993). Haptic spatial maps from Penfield & Boldrey (1937); modern confirmation via fMRI.",
                "qualifier": "Confidence 0.6 reflects robust neural evidence across primate and human studies. MECHANISM warrant: direct neural pathways are anatomically documented.",
                "rebuttal": "Under conditions of severe sensory degradation (aphantasia, deafness, severe neuropathy), some spatial channels may be non-functional, but alternative channels can partially compensate (see inverse effectiveness).",
                "competing_accounts": [
                    "Amodal perception hypothesis: spatial information is processed in a single amodal representation (weak evidence; channel-specific anatomy is clear)",
                    "Sensorimotor contingency account: space is constructed through action, not perception (compatible; motor output uses modality-specific maps)"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Spence (2011) authority"
            }
        },
        {
            "step": 2,
            "justification": {
                "data": [
                    "Superior colliculus multisensory neurons fire to stimuli from the SAME spatial location (integration)",
                    "Multisensory neurons show enhanced responses (>50% amplification) when stimuli are spatially aligned",
                    "Neurons show suppression or no response when stimuli are from different spatial locations",
                    "Spatial alignment window: ~30 cm (Stein & Meredith, 1993); ~200 ms temporal (Meredith et al., 1987)",
                    "This principle is conserved across species (cat, ferret, primate)"
                ],
                "backing": "Stein & Meredith (1993) 'The Merging of the Senses' is foundational text with unit recording data from cat superior colliculus (multisensory neurons). Temporal window from Meredith et al. (1987) single-unit recording. Human behavioral analogues support spatial principle (Spence & Driver, 1997).",
                "qualifier": "Confidence 0.6 reflects direct neural recording evidence in animals and consistent behavioral data in humans. MECHANISM warrant: neural mechanism for spatial binding is directly measured.",
                "rebuttal": "The spatial window is not absolute; context and attention can modulate boundaries (Spence, 2011). Individual variability exists across observers.",
                "competing_accounts": [
                    "Temporal binding as primary principle: timing, not space, determines integration (partial; timing is also important but spatial alignment is primary in colliculus)",
                    "Feature binding through binding probability: probability is strictly Bayesian (compatible; Bayesian formalization builds on spatial-temporal constraints)"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Stein & Meredith authority (foundational)"
            }
        },
        {
            "step": 3,
            "justification": {
                "data": [
                    "Spatially congruent environments (visual, auditory, haptic sources co-located) produce unified spatial percept",
                    "Spatially incongruent environments (sound from wrong direction, haptic properties don't match visual surface) produce perceptual fragmentation",
                    "Fragmentation is measurable: reduced spatial presence ratings, lower cognitive mapping accuracy, increased wayfinding errors"
                ],
                "backing": "Spence (2011) review of crossmodal correspondences. Körding et al. (2007) Bayesian causal inference framework shows how incongruent spatial signals impair position estimation. Spatial presence literature (Witmer & Singer, 1998) shows coherence effects on presence.",
                "qualifier": "Confidence 0.5 reflects behavioral and psychophysical evidence but not direct neural recording in humans under architectural conditions. EMPIRICAL_ASSOCIATION warrant: correlations are measured but mechanisms partially inferred.",
                "rebuttal": "Perceptual fragmentation may be task-dependent: some observers may ignore incongruent cues and focus on dominant channel. Individual differences in spatial weighting could moderate the effect.",
                "competing_accounts": [
                    "Selective attention: incongruence is ignored if bottom-up salience is low (partially true; automatic spatial binding still occurs)",
                    "Channel dominance account: vision always wins regardless of incongruence (refuted by numerous crossmodal studies)"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Spence authority; Körding et al. Bayesian framework"
            }
        },
        {
            "step": 4,
            "justification": {
                "data": [
                    "Fragmentation from spatial incoherence produces negative affect: anxiety, unease, disorientation",
                    "Coherent environments produce positive affect: comfort, spatial legibility, place familiarity",
                    "Effect size: coherence produces d ≈ 0.25-0.40 improvement in spatial presence and affect ratings",
                    "Spatial presence supports spatial memory encoding: coherent spaces are recalled with higher accuracy"
                ],
                "backing": "Spence (2011) on congruence and affect. Spatial presence literature (Witmer & Singer, 1998; Slater & Wilbur, 1997) on affect and presence. Memory-space interaction from Maguire et al. (1997) hippocampal place cells.",
                "qualifier": "Confidence 0.45 reflects field studies and user ratings but mechanisms are partially inferred. CAPACITY warrant: functional capacity is measured (affect, memory) but neural mechanisms are theoretical.",
                "rebuttal": "Affect effects may be mediated by expectation violations rather than coherence per se. Individual differences in spatial anxiety could moderate affect magnitude. Very familiar spaces may reduce coherence sensitivity.",
                "competing_accounts": [
                    "Cognitive load hypothesis: incongruence increases processing load, not specifically affects spatial coherence (compatible; a mechanism, not competing)",
                    "Novelty account: incongruence is negative only because it violates expectations (partially true but doesn't explain why coherent designs are inherently preferred)"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Spence authority"
            }
        }
    ],
    "CT_AFFECTIVE_TOUCH_001": [
        {
            "step": 1,
            "justification": {
                "data": [
                    "C-tactile (CT) afferents are unmyelinated, slowly conducting fibres (0.5-2 m/s)",
                    "CT afferents respond maximally to stroking velocities 1-10 cm/s, peak ~3 cm/s",
                    "CT afferents are innervated primarily on hairy skin (forearm, back, leg), absent on glabrous skin (palm, sole)",
                    "Aβ mechanoreceptors are myelinated, fast-conducting (35-70 m/s), serve discriminative touch",
                    "Architectural contact (hand on railing, foot on floor) activates both channels but at different effective velocities"
                ],
                "backing": "Löken et al. (2009) microelectrode recordings from CT afferents in humans; velocity tuning is directly measured. Morrison et al. (2010) on CT innervation density. Classic mechanoreceptor physiology from Sinclair (1967).",
                "qualifier": "Confidence 0.6 reflects direct human neural recording of CT afferent responses. MECHANISM warrant: CT fiber properties and velocity tuning are directly measured.",
                "rebuttal": "CT density varies across body regions; architectural contact points (hands, feet, back) have lower CT densities than optimal laboratory sites (forearm). Individual variation in CT density exists.",
                "competing_accounts": [
                    "Aβ fibers alone mediate affective touch (refuted by CT lesion studies; CT afferents are necessary)",
                    "Affective touch is mediated by slow temporal integration of pressure (partially true but CT fiber tuning is the primary mechanism)"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Löken & Morrison authorities"
            }
        },
        {
            "step": 2,
            "justification": {
                "data": [
                    "CT afferent firing rate peaks at ~3 cm/s stroking velocity",
                    "Pleasant touch is optimal at moderate roughness (Ra 1-10 μm)",
                    "Pleasant touch is optimal at skin-temperature warmth (~32°C surface)",
                    "Pleasant touch requires moderate compliance (not too hard, not too soft)",
                    "Inverted-U response profile: sub-threshold and supra-threshold velocities produce weaker responses"
                ],
                "backing": "Löken et al. (2009) single-fiber recordings with velocity, texture, and temperature manipulation. McGlone et al. (2014) review of CT afferent physiology. Watkins et al. (2021) on palm CT-like responses.",
                "qualifier": "Confidence 0.6 reflects controlled laboratory electrophysiology. MECHANISM warrant: CT encoding properties are directly measured under controlled conditions.",
                "rebuttal": "Laboratory conditions (passive stroking) differ from architectural use (active contact, variable pressure, variable velocity). Field parameters (roughness, temperature, compliance) vary more than lab conditions.",
                "competing_accounts": [
                    "Affective response is purely top-down (cognitive expectation): refuted by CT fiber physiology independent of cognition",
                    "Temperature dominates pleasantness: refuted by velocity and texture effects demonstrated independently of temperature"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Löken et al. authority (direct physiology)"
            }
        },
        {
            "step": 3,
            "justification": {
                "data": [
                    "CT afferent signals project to dorsal horn (spinal) then spinothalamic tract",
                    "Posterior insular cortex (piriform insular) receives CT projections",
                    "Posterior insula is site of hedonic valuation, not discriminative localization",
                    "Posterior insula integrates with anterior insula (interoception) and OFC (valuation)",
                    "This pathway is distinct from discriminative touch (SI cortex, Aβ-dominant)"
                ],
                "backing": "Craig (2009) on insular cortex organization. Morrison (2016) on insular projections from CT afferents. Neuroimaging (PET, fMRI) localizes hedonic touch responses to posterior insula.",
                "qualifier": "Confidence 0.55 reflects human neuroimaging and lesion evidence but less extensive than animal single-unit work. MECHANISM warrant: neural projection pathways are established from tracing and imaging.",
                "rebuttal": "Insular cortex has multiple functional subdivisions; precise localization of CT response within posterior insula is debated. Individual variability in insular organization exists.",
                "competing_accounts": [
                    "Anterior insula alone mediates hedonic touch (refuted by focal posterior insula responses to CT stimulation)",
                    "OFC is the primary site (compatible; OFC receives insular input and generates final valuation)"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Craig authority on insula; Morrison on CT projections"
            }
        },
        {
            "step": 4,
            "justification": {
                "data": [
                    "CT stimulation (pleasing touch) reduces heart rate (parasympathetic marker)",
                    "CT stimulation reduces cortisol (stress hormone)",
                    "CT stimulation increases positive affect (self-report, facial EMG)",
                    "Effect is mediated by insular cortex connections to nucleus accumbens and periaqueductal gray (PAG)",
                    "Effect is attenuated in patients with damage to insular cortex or disrupted vagal afferents"
                ],
                "backing": "McGlone et al. (2014) on autonomic effects of C-tactile stimulation. Morrison (2016) review of hedonic touch pathway. Walker et al. (2017) on touch and stress reduction.",
                "qualifier": "Confidence 0.45 reflects field studies and physiological correlates but causality is inferred. CAPACITY warrant: functional effects are measured but the complete pathway is partially inferred.",
                "rebuttal": "Autonomic responses could be mediated by expectation (top-down) rather than CT signals alone. Individual differences in parasympathetic tone could moderate effects. Architectural contact is less controlled than laboratory stroking.",
                "competing_accounts": [
                    "Stress reduction is purely psychological (expectation): refuted by CT-mediated effects in non-human primates lacking explicit expectations",
                    "Sympathetic arousal masks CT benefit: partially true; high baseline arousal might occlude parasympathetic shift"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; McGlone authority"
            }
        }
    ],
    "HAP_SURFACE_MATERIAL_001": [
        {
            "step": 1,
            "justification": {
                "data": [
                    "Hand/foot/body contact with surface transduces mechanical properties",
                    "Roughness (Ra, arithmetic mean roughness) is encoded by mechanoreceptors: Meissner corpuscles (fine texture), Pacinian corpuscles (vibration), Merkel cells (sustained pressure), Ruffini endings (skin stretch)",
                    "Thermal conductivity (λ) is encoded by thermoreceptors (TRPM8 cold, TRPV3/V4 warm)",
                    "Compliance (Young's modulus E) is encoded by pressure-sensitive receptors",
                    "Texture grain orientation is encoded by directionally sensitive receptors"
                ],
                "backing": "Sinclair (1967) foundational mechanoreceptor physiology. McGlone et al. (2014) on somatosensory transduction of material properties. Klatzky & Lederman (2002) on haptic perception of surfaces.",
                "qualifier": "Confidence 0.6 reflects established receptor physiology. MECHANISM warrant: sensory transduction mechanisms are directly measured.",
                "rebuttal": "Architectural contact conditions (gloved hands, footwear, limited contact time) differ from optimal transduction conditions. Receptor density varies across body regions.",
                "competing_accounts": [
                    "Material properties are perceived entirely through visual cues: refuted by blind and visually impaired discrimination of materials",
                    "Thermal properties dominate material perception: partially true; temperature is important but texture and compliance contribute independently"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; McGlone authority"
            }
        },
        {
            "step": 2,
            "justification": {
                "data": [
                    "Aβ mechanoreceptors encode discriminative properties (roughness magnitude, texture spatial frequency, hardness) and project to SI cortex",
                    "CT afferents encode affective valence (pleasant/unpleasant) and project to posterior insula",
                    "SI cortex represents material texture and hardness with spatial topography",
                    "Posterior insula generates hedonic dimension independent of discriminative detail",
                    "Dual-process model is supported by dissociation in lesion studies and neuroimaging"
                ],
                "backing": "McGlone et al. (2014) on dual-process haptic processing. Morrison (2016) on affective vs. discriminative pathways. Neuroimaging studies (Simmons et al., 2013; Veldhuijzen et al., 2010) show channel separation.",
                "qualifier": "Confidence 0.55 reflects neuroimaging and dual-dissociation evidence. MECHANISM warrant: dual neural pathways are anatomically segregated.",
                "rebuttal": "Some convergence between channels occurs at higher levels (OFC, anterior insula). Top-down expectation can modulate both discriminative and affective components.",
                "competing_accounts": [
                    "Single integrated haptic stream: refuted by double-dissociation in clinical populations (some retain discrimination with lost affect, and vice versa)",
                    "Affect is computed from discriminative properties (compatible; affect could be derived from discrimination, but dissociations suggest independent channels)"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; McGlone authority on dual-process"
            }
        },
        {
            "step": 3,
            "justification": {
                "data": [
                    "Wood (warm, Ra 5-15 μm, E ~10 GPa): hedonic_score 0.75",
                    "Natural textile (warm, Ra 10-30 μm, E <0.1 GPa): hedonic_score 0.80",
                    "Cork (warm, Ra 15-40 μm, E ~0.02 GPa): hedonic_score 0.70",
                    "Stone warm/neutral (cool, λ 1.5-2.5 W/m·K): hedonic_score 0.30-0.45",
                    "Metal room temp (cold, λ 15-50 W/m·K): hedonic_score 0.20",
                    "Concrete raw (cold, Ra >100 μm, rigid): hedonic_score 0.25"
                ],
                "backing": "Hedonic rankings from McGlone et al. (2014) psychophysical experiments. Thermal conductivity from materials databases (CRC). Correlation between λ and hedonic score is robust (r ≈ -0.80).",
                "qualifier": "Confidence 0.5 reflects empirical psychophysical ratings but limited sample sizes. EMPIRICAL_ASSOCIATION warrant: correlations between material properties and affect are measured.",
                "rebuttal": "Cultural context modulates baseline hedonic scores (see MATERIAL_CULTURAL_CONDITIONING_001). Temperature at time of contact modulates effect independently of material λ. Individual preferences vary (some prefer metal aesthetic).",
                "competing_accounts": [
                    "Visual appearance drives affect (refuted by blind blindfold studies; haptic alone drives ratings similarly)",
                    "Temperature is the only driver of pleasantness (refuted by roughness and compliance effects demonstrated independently of temperature)"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; McGlone authority"
            }
        }
    ],
    "MATERIAL_AGING_TEMPORAL_DEPTH_001": [
        {
            "step": 1,
            "justification": {
                "data": [
                    "Patina (oxidation): copper green, bronze brown (visual + chemical signature)",
                    "Wear patterns: polished stone thresholds, smooth wood handrails (visual + haptic smoothing)",
                    "Weathering: lichen on stone, grain exposure on wood (visual + haptic roughening)",
                    "Staining: use patterns, water marks, UV bleaching (visual temporal signature)",
                    "Olfactory aging: aged wood scent differs from new wood (volatile profile changes)"
                ],
                "backing": "Mikellides (1990) empirical study of material aging perception. Pallasmaa (2005) phenomenological framework. Materials science (Zuo et al., 2015) on patina formation and aging kinetics.",
                "qualifier": "Confidence 0.5 reflects field observation and psychophysical measurement. EMPIRICAL_ASSOCIATION warrant: aging features are measured and correlate with time.",
                "rebuttal": "Aging features can be artificially induced (artificial patina, distressed finishes), suggesting perceptual cues are separable from actual age. Some occupants may perceive aging as deterioration rather than enrichment.",
                "competing_accounts": [
                    "Aging is primarily visual degradation: partially true but haptic smoothing and olfactory signature are distinct channels",
                    "Aging perception is purely learned (expectation): refuted by infant and non-human animal responses to textural complexity, suggesting perceptual salience"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Mikellides empirical authority; Pallasmaa theoretical"
            }
        },
        {
            "step": 2,
            "justification": {
                "data": [
                    "Visual temporal feature extraction: wear patterns detected by texture analysis (statistical deviation from new material)",
                    "Somatosensory wear-pattern detection: smoothing of high-friction surfaces is detectable through haptic exploration",
                    "Patina and weathering are statistical outliers in material appearance databases",
                    "Temporal depth is automatically inferred by visual system without conscious deliberation"
                ],
                "backing": "Pallasmaa (2005) on phenomenological 'existential anchoring'. Mikellides (1990) on automatic perceptual categorization. Visual texture analysis literature (Portilla & Simoncelli, 2000) on texture statistics extraction.",
                "qualifier": "Confidence 0.45 reflects theoretical framework and field observation but limited direct evidence. CAPACITY warrant: functional capacity to extract temporal features is inferred from behavioral outcomes.",
                "rebuttal": "Temporal depth inference requires prior knowledge of 'new' material baseline; unfamiliar materials may not trigger this inference. Some occupants may not extract temporal information consciously.",
                "competing_accounts": [
                    "Aging perception is purely cultural learning (partially true; cultural context modulates baseline but perceptual salience of texture changes is pre-cultural)",
                    "Temporal depth is conscious deliberation only (refuted by rapid implicit categorization of aged vs. new materials)"
                ],
                "depth_tier": "C",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Pallasmaa theoretical framework"
            }
        },
        {
            "step": 3,
            "justification": {
                "data": [
                    "Aged materials rated 0.40-0.60 SD higher on authenticity and character (Mikellides, 1990)",
                    "Authenticity effect persists across European cultural contexts",
                    "Aged materials are rated as more trustworthy and durable",
                    "Implicit inference: 'this material has survived; it is reliable'"
                ],
                "backing": "Mikellides (1990) controlled semantic differential study. Pallasmaa (2005) existential anchoring framework. Field observation from Heerwagen (2009).",
                "qualifier": "Confidence 0.45 reflects empirical psychophysical ratings but limited sample diversity. CAPACITY warrant: affect effects are measured but underlying mechanisms (inferences about durability, cultural meaning) are partially inferred.",
                "rebuttal": "Authenticity effect is culturally variable (see MATERIAL_CULTURAL_CONDITIONING_001 for cultural modulation). Effect size is modest; individual differences are substantial. Pristine materials may be preferred in some contexts (medical, laboratory).",
                "competing_accounts": [
                    "Aged materials are preferred due to visual novelty: refuted by preference for authentic wear over artificial distressing",
                    "Temporal depth is dispreferred in contemporary design: partially true in some markets but wabi-sabi tradition (Japan) shows opposite preference"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Mikellides empirical, Pallasmaa theoretical"
            }
        },
        {
            "step": 4,
            "justification": {
                "data": [
                    "Buildings with natural material aging show upward satisfaction trajectories over 5-10 years",
                    "Buildings with static finishes show flat or downward trajectories",
                    "Gracefully aging materials (copper patina, wood darkening) show positive aging",
                    "Ungracefully aging materials (peeling paint, yellowing plastic) show negative aging"
                ],
                "backing": "Heerwagen (2009) field observations and post-occupancy evaluation data. Zuo et al. (2015) on material aging and aesthetic value. Karana et al. (2015) on emotional responses to aging.",
                "qualifier": "Confidence 0.4 reflects field observation data but not controlled longitudinal studies. THEORY_DERIVED warrant: satisfaction trajectories are measured but confounds (occupant tenure, maintenance investment) are not fully controlled.",
                "rebuttal": "Satisfaction trajectories could be confounded with occupant familiarity and habituation rather than material aging per se. Maintenance practices vary widely. Selection bias: buildings designed for natural aging may differ in other ways.",
                "competing_accounts": [
                    "Satisfaction plateaus regardless of material aging: partially true; some contexts show plateau, but natural material buildings show documented upward slopes",
                    "Aging is purely aesthetic and not functional: refuted by durability and structural benefit of graceful aging (reduced maintenance costs)"
                ],
                "depth_tier": "C",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Heerwagen field authority; Karana design research"
            }
        }
    ],
    "MATERIAL_CULTURAL_CONDITIONING_001": [
        {
            "step": 1,
            "justification": {
                "data": [
                    "Occupant perceives material category: wood, stone, concrete, steel, glass, fabric",
                    "Material categorization is rapid (< 200 ms) and automatic",
                    "Ventral visual stream (IT cortex) shows material-selective neurons",
                    "Somatosensory cortex confirms material identity through haptic feedback"
                ],
                "backing": "Ernst (2006) on multisensory material perception. Neuroimaging (fMRI) shows material-selective responses in IT cortex (Chao & Martin, 2000). Haptic-visual integration literature (Ernst & Banks, 2002).",
                "qualifier": "Confidence 0.6 reflects neural imaging and psychophysical evidence. MECHANISM warrant: material processing pathways are anatomically documented.",
                "rebuttal": "Material categorization is ambiguous when visual cues are degraded (dim lighting, distance). Haptic confirmation requires contact, which is not always available.",
                "competing_accounts": [
                    "Material is purely a visual category: refuted by blind individual's material discrimination ability",
                    "Material identity requires explicit conscious deliberation: refuted by rapid implicit categorization"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Ernst authority"
            }
        },
        {
            "step": 2,
            "justification": {
                "data": [
                    "Material-context pairings are learned through repeated exposure: marble in banks → wealth/trust",
                    "Exposed brick in cafés → authenticity/informality",
                    "Raw concrete in prisons → austerity/oppression",
                    "Learned associations are stored in medial temporal (memory) and OFC (valuation)",
                    "Associations are culturally acquired (vary by geographic region, generation)"
                ],
                "backing": "Mikellides (1990) on learned associations. Contextual memory literature (Eichenbaum et al., 2007). OFC value coding literature (Kable & Glimcher, 2009).",
                "qualifier": "Confidence 0.55 reflects behavioral studies and neural value coding. EMPIRICAL_ASSOCIATION warrant: learned associations are measured behaviorally and correlate with neural activity.",
                "rebuttal": "Associations are not truly arbitrary; they may rest on perceptual properties (marble is cold → luxurious; concrete is hard → institutional). Cultural homogenization may be reducing diversity of local associations.",
                "competing_accounts": [
                    "All material preferences are biophilic (innate): refuted by cultural variation in material preferences",
                    "Associations are purely rational inference: refuted by implicit association test showing non-conscious cultural learning"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Mikellides cultural authority"
            }
        },
        {
            "step": 3,
            "justification": {
                "data": [
                    "Culturally positive associations amplify innate hedonic response",
                    "Culturally negative associations suppress or reverse affective response",
                    "Top-down modulation from mPFC/OFC on amygdala and insular cortex is documented",
                    "Effect is multiplicative, not additive: cultural conditioning modulates the biophilic baseline"
                ],
                "backing": "Neuroimaging shows OFC-amygdala connectivity for value-based decision making (Kable & Glimcher, 2009). Emotion regulation literature shows top-down modulation of affective regions (Ochsner & Gross, 2005).",
                "qualifier": "Confidence 0.5 reflects neural evidence for top-down modulation but limited direct measurement of material-specific cultural effects. EMPIRICAL_ASSOCIATION warrant: top-down valuation mechanisms are established; specific application to materials is inferred.",
                "rebuttal": "Top-down modulation effects are context-dependent. Implicit cultural associations may vary within cultural groups (e.g., socioeconomic variation). Young people may reject inherited cultural associations.",
                "competing_accounts": [
                    "Cultural conditioning is independent of biophilic baseline (incorrect; conditioning operates on top of baseline)",
                    "Biophilic baseline is fixed and cannot be culturally overridden (refuted by Japanese preference for raw concrete, contrary to Western baseline)"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Mikellides cultural authority; Kable neural value authority"
            }
        }
    ],
    "MATERIAL_IDENTITY_INTEGRATION_001": [
        {
            "step": 1,
            "justification": {
                "data": [
                    "Multi-sensory material perception occurs in parallel: visual texture/color, haptic roughness/temperature/compliance, acoustic tap signature, olfactory VOC signature",
                    "Modality-specific processing is documented in visual (texture selectivity), somatosensory (material-responsive neurons), auditory (material-dependent resonance), olfactory (VOC-specific receptors)",
                    "Integration occurs downstream of modality-specific processing"
                ],
                "backing": "Ernst & Banks (2002) foundational paper on multisensory material perception. Ernst (2006) review on haptic-visual material integration. Stein & Meredith (1993) on multisensory integration principles.",
                "qualifier": "Confidence 0.6 reflects established neuroanatomy and psychophysical evidence. MECHANISM warrant: parallel processing pathways are anatomically segregated and documented.",
                "rebuttal": "Modality-specific processing is not entirely independent; some cross-talk occurs. Top-down expectations can bias early processing.",
                "competing_accounts": [
                    "Material perception is primarily visual: refuted by blind individual's precise material discrimination",
                    "Material perception is amodal: partially true at higher levels but channel-specific processing is foundational"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Ernst authority on multisensory material integration"
            }
        },
        {
            "step": 2,
            "justification": {
                "data": [
                    "Bayesian causal inference framework: P(common cause | signals) is computed from signal reliability and spatial-temporal alignment",
                    "Common-cause probability is high when signals share properties (wood-colored + wood-textured + wood-scented)",
                    "Common-cause probability is low when signals conflict (wood-colored laminate + plastic feel + no wood scent)",
                    "Integration occurs when P(common cause) > threshold; segregation when P(common cause) < threshold"
                ],
                "backing": "Körding et al. (2007) explicit Bayesian causal inference model for multisensory integration. Shams & Beierholm (2010) review of Bayesian multisensory models. Neural implementation in posterior parietal cortex and STS (neuroimaging).",
                "qualifier": "Confidence 0.6 reflects explicit computational models and supporting neuroimaging. MECHANISM warrant: Bayesian causal inference is a documented computational principle in multisensory processing.",
                "rebuttal": "Bayesian model is a simplification; actual computations may use heuristics. Prior probability for 'common cause' may vary with context and experience.",
                "competing_accounts": [
                    "Integration is rule-based (e.g., spatial coincidence only): partially true; spatial-temporal rules are part of the Bayesian computation",
                    "Integration is always successful if signals are from same object: refuted by strong incongruence suppressing integration"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Körding authority on Bayesian multisensory integration"
            }
        },
        {
            "step": 3,
            "justification": {
                "data": [
                    "Integrated material percept has lower variance than individual channels",
                    "Precision-weighted combination formula: σ_integrated² = 1 / (1/σ_visual² + 1/σ_haptic²)",
                    "Visual + haptic integration improves discrimination by ~25%",
                    "Visual + haptic + olfactory improves by ~35%"
                ],
                "backing": "Ernst & Banks (2002) maximum likelihood estimation (MLE) model with human psychophysics. Laboratory measurements of precision gain (30-40% typical). Architectural application discounted to 20-30% (less controlled conditions).",
                "qualifier": "Confidence 0.55 reflects laboratory evidence but architectural discount for uncontrolled conditions. MECHANISM warrant: MLE principle is established; architectural application is FUNCTIONAL (effectiveness is measured in field).",
                "rebuttal": "Laboratory precision gains may not transfer to architecture (shorter contact times, competing visual attention). Individual differences in channel reliability weighting exist.",
                "competing_accounts": [
                    "Channels are independent and should not be combined: refuted by lower variance in combined estimates",
                    "All channels have equal weight: refuted by reliability-weighted evidence from multiple studies"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Ernst authority on MLE material integration"
            }
        },
        {
            "step": 4,
            "justification": {
                "data": [
                    "Multi-modal material percept (visual + haptic + olfactory) generates affective response",
                    "Material identity (wood, stone, metal, fabric) triggers learned evaluative associations (see MATERIAL_CULTURAL_CONDITIONING_001)",
                    "Material identity also triggers innate biophilic preferences (see NATURAL_MATERIAL_CONVERGENCE_001)",
                    "Affective response is faster and stronger with multi-modal input than visual alone"
                ],
                "backing": "Ernst (2006) on multisensory affect. Spence (2011) on crossmodal correspondences and affect. Biophilia literature (Kaplan & Kaplan, 1989) on innate material preferences.",
                "qualifier": "Confidence 0.5 reflects convergent evidence but mechanisms are partially inferred. FUNCTIONAL warrant: affective effects are measured behaviorally (ratings, autonomic response).",
                "rebuttal": "Affect effects could be mediated by expectation (top-down) rather than multisensory integration per se. Individual preferences vary widely.",
                "competing_accounts": [
                    "Affect is determined entirely by visual appearance: refuted by blind individual's material preference studies",
                    "Multisensory affect is purely additive: partially true but congruence effects suggest non-linear combination"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Ernst material authority, Spence crossmodal authority"
            }
        }
    ],
    "MSI_CONGRUENCY_PRINCIPLE_001": [
        {
            "step": 1,
            "justification": {
                "data": [
                    "Architectural environment presents multi-sensory stimulus array: visual (color, texture, luminance), acoustic (reverberation, absorption, spectrum), haptic (temperature, roughness, compliance), olfactory (VOCs, moisture, age)",
                    "Each modality carries information about materials and space",
                    "Sensory information is processed in parallel in modality-specific cortices"
                ],
                "backing": "Spence (2011) foundational review. Foundational multisensory processing literature (Stein & Meredith, 1993).",
                "qualifier": "Confidence 0.6 reflects basic neuroanatomy. MECHANISM warrant: parallel sensory processing is anatomically established.",
                "rebuttal": "Sensory dominance (visual) may suppress non-dominant channels in high-arousal conditions.",
                "competing_accounts": [
                    "Perception is unisensory dominant: partially true; vision dominates in many contexts but multisensory integration still occurs"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Spence authority"
            }
        },
        {
            "step": 2,
            "justification": {
                "data": [
                    "Crossmodal congruency is evaluated: visual warmth + haptic warmth + acoustic warmth + olfactory warmth = CONGRUENT",
                    "Visual warmth + haptic coldness + hard reverberation + chemical scent = INCONGRUENT",
                    "Congruency evaluation occurs in STS and IFG (neuroimaging)",
                    "Evaluation is rapid and largely automatic"
                ],
                "backing": "Spence (2011) on crossmodal congruency. Spence & Gallace (2011) on neural substrates. STS neuroimaging literature (Beauchamp et al., 2004).",
                "qualifier": "Confidence 0.55 reflects neural evidence and behavioral measurement. EMPIRICAL_ASSOCIATION warrant: congruency is measured and correlates with neural activity.",
                "rebuttal": "Congruency thresholds vary with attention and context. Some incongruence may be tolerated or go unnoticed.",
                "competing_accounts": [
                    "Congruency is consciously deliberative only: refuted by implicit congruency effects in priming studies",
                    "All sensory dimensions are equally important: refuted by evidence that some dimensions are more salient than others"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Spence crossmodal authority"
            }
        },
        {
            "step": 3,
            "justification": {
                "data": [
                    "Congruent multi-sensory arrays produce processing fluency: reduced computational effort, positive metacognitive signal",
                    "Incongruent arrays produce disfluency: increased processing effort, negative metacognitive signal",
                    "Processing fluency is documented in cognitive psychology (Reber et al., 2004)",
                    "Fluency produces affect generation via somatic marker pathway"
                ],
                "backing": "Reber et al. (2004) fluency-based affect model. Damasio (1994) somatic marker hypothesis. Spence (2011) application to multisensory congruency.",
                "qualifier": "Confidence 0.5 reflects behavioral evidence and theoretical integration. EMPIRICAL_ASSOCIATION warrant: processing fluency effects are measured; affect generation is inferred from somatic marker theory.",
                "rebuttal": "Fluency effects can be weak in high-expertise observers (architects may overlook congruence). Individual differences in sensitivity exist.",
                "competing_accounts": [
                    "Affect is driven by objective properties, not processing fluency: refuted by fluency effects on affect independent of objective quality",
                    "Congruence is too subtle for affective influence: refuted by strong affect effects in experimental studies"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Reber fluency authority, Spence multisensory application"
            }
        },
        {
            "step": 4,
            "justification": {
                "data": [
                    "Congruent environments rated more pleasant (d ≈ 0.30-0.50)",
                    "Congruent environments rated more coherent",
                    "Congruent environments rated more trustworthy",
                    "Incongruent environments produce unease, suspicion, reduced dwelling time"
                ],
                "backing": "Spence (2011) effect sizes from congruency studies. Reber et al. (2004) fluency-affect relationship. OFC valuation literature (Kable & Glimcher, 2009).",
                "qualifier": "Confidence 0.5 reflects behavioral ratings and neural valuation evidence. EMPIRICAL_ASSOCIATION warrant: affect effects are measured; neural mechanisms are partially inferred.",
                "rebuttal": "Affect effects are context-dependent (some incongruence may be valued as 'interesting'). Cultural context moderates baseline preferences.",
                "competing_accounts": [
                    "Pleasantness is driven entirely by individual channel quality: refuted by congruency effect independent of channel quality",
                    "Trustworthiness is cognitive, not affective: partially true but affect and cognition interact in value computation"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Spence congruency authority"
            }
        }
    ],
    "MSI_INVERSE_EFFECTIVENESS_002": [
        {
            "step": 1,
            "justification": {
                "data": [
                    "Occupant perceives environment through multiple channels (visual, auditory, haptic, olfactory)",
                    "Each channel has signal-to-noise ratio (SNR) that varies with conditions",
                    "Visual clarity degrades in dim light, fog, distance",
                    "Auditory clarity degrades in noise",
                    "Haptic clarity degrades with gloves or numbness"
                ],
                "backing": "Stein & Meredith (1993) foundational work on signal-to-noise in multisensory integration. Signal detection theory (Green & Swets, 1966) on channel reliability.",
                "qualifier": "Confidence 0.6 reflects established neurophysiology. MECHANISM warrant: SNR variation in sensory channels is documented.",
                "rebuttal": "Some observers may not notice channel degradation (top-down compensation, selective attention).",
                "competing_accounts": [
                    "Sensory channels are independent: refuted by inverse effectiveness showing interaction effects",
                    "Channel degradation always reduces perception: refuted by multisensory compensation"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Stein & Meredith authority"
            }
        },
        {
            "step": 2,
            "justification": {
                "data": [
                    "When unisensory signal is weak, addition of congruent signal produces GREATER enhancement",
                    "Multisensory gain is inversely proportional to unisensory signal strength",
                    "Effect is documented in superior colliculus multisensory neurons (cat)",
                    "Behavioral analogues are consistent in humans"
                ],
                "backing": "Stein & Meredith (1993) single-unit recordings from cat superior colliculus. Rowland & Stein (2014) comprehensive review. Human behavioral evidence from Rowland et al. (2007) and others.",
                "qualifier": "Confidence 0.6 reflects neural recording in animals and behavioral evidence in humans. EMPIRICAL_ASSOCIATION warrant: inverse effectiveness is directly measured in neural and behavioral data.",
                "rebuttal": "Human neural mechanism may differ from cat colliculus. Cortical integration may follow different rules.",
                "competing_accounts": [
                    "Multisensory integration is always additive: refuted by inverse effectiveness and super-additivity",
                    "Weak signals are ignored: refuted by enhancement of weak signals by congruent signals"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Stein & Meredith animal authority, Rowland behavioral authority"
            }
        },
        {
            "step": 3,
            "justification": {
                "data": [
                    "Super-additive responses occur when individual channels are below ~50% detection accuracy",
                    "Combined response exceeds the sum of individual responses",
                    "Effect requires congruent (common-cause) signals",
                    "Incongruent signals show sub-additive or inhibitory responses"
                ],
                "backing": "Rowland et al. (2007) data on super-additivity conditions. Rowland & Stein (2014) review. Nonlinear integration literature (Avilés et al., 2005).",
                "qualifier": "Confidence 0.55 reflects neural and behavioral measurements. EMPIRICAL_ASSOCIATION warrant: super-additivity is measured under specified conditions.",
                "rebuttal": "Threshold for super-additivity (50% detection) may vary with stimulus type and cortical region. Human thresholds may differ from cat.",
                "competing_accounts": [
                    "Integration is always linear: refuted by super-additive and sub-additive effects",
                    "Integration effectiveness is independent of signal strength: refuted by inverse effectiveness"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Rowland super-additivity authority"
            }
        }
    ],
    "NATURAL_MATERIAL_CONVERGENCE_001": [
        {
            "step": 1,
            "justification": {
                "data": [
                    "Natural materials (wood, stone, natural fibre) emit multi-sensory signals",
                    "Visual: fractal statistics (owned by VISUAL-I T1)",
                    "Haptic: warmth (low λ) + moderate roughness (optimal Ra) = CT pathway activation",
                    "Olfactory: phytoncides from wood (20-80 μg/m³ indoor concentrations)"
                ],
                "backing": "Li et al. (2009) phytoncide measurements. McGlone et al. (2014) haptic properties. Taylor et al. (2005) on visual fractal statistics of nature. Li (2010) on forest therapy research.",
                "qualifier": "Confidence 0.6 reflects direct measurement of natural material signals. MECHANISM warrant: natural material properties are documented in materials science and physiology.",
                "rebuttal": "Phytoncide indoor concentrations are variable (depends on ventilation, material finish). Haptic properties vary with moisture and temperature.",
                "competing_accounts": [
                    "Natural materials are not inherently different from synthetic: refuted by distinct phytoncide presence and haptic profiles",
                    "Visual properties alone account for natural material effects: refuted by stress reduction in blind individuals exposed to natural materials"
                ],
                "depth_tier": "A",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Li phytoncide authority, McGlone haptic authority"
            }
        },
        {
            "step": 2,
            "justification": {
                "data": [
                    "Visual fractal statistics → perceptual fluency → reduced cortical arousal (see VISUAL-I T1 for mechanism)",
                    "Haptic warmth/roughness → CT afferent firing → posterior insula → parasympathetic shift (see CT_AFFECTIVE_TOUCH_001)",
                    "Phytoncides → olfactory receptors → olfactory bulb → amygdala → HPA axis suppression (Li et al., 2009)",
                    "Three independent pathways converging on parasympathetic activation"
                ],
                "backing": "Li (2010) review of phytoncide pathways. Morrison (2016) on CT insular pathway. Multiple independent literatures (visual perceptual fluency, olfactory stress reduction, autonomic regulation).",
                "qualifier": "Confidence 0.55 reflects convergent evidence from independent domains. EMPIRICAL_ASSOCIATION warrant: each pathway is established; convergence is inferred.",
                "rebuttal": "Pathways may not be truly independent at higher levels (OFC, mPFC). Top-down expectations could amplify or suppress individual channel effects.",
                "competing_accounts": [
                    "Single dominant pathway explains natural material effects: refuted by effects persisting when one channel is removed",
                    "Pathways are competitive, not convergent: refuted by additive/synergistic stress reduction effects"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Li (phytoncide), Morrison (haptic), independent experts"
            }
        },
        {
            "step": 3,
            "justification": {
                "data": [
                    "Convergence bonus ≈ 1.2 (20% enhancement)",
                    "Combined stress reduction exceeds arithmetic sum of individual channel effects",
                    "Mechanism: convergent parasympathetic activation from independent pathways"
                ],
                "backing": "Heerwagen & Hase (2001) field observations. Heerwagen (2009) post-occupancy data. Autonomic physiology literature on convergent parasympathetic inputs.",
                "qualifier": "Confidence 0.45 reflects field data but limited controlled studies. CAPACITY warrant: convergence bonus is measured in field; mechanism is partially inferred.",
                "rebuttal": "Field confounds (occupant expectations, context effects) may inflate convergence bonus. Individual variability in autonomic response is substantial.",
                "competing_accounts": [
                    "Multi-channel exposure is no better than single best channel: refuted by measured convergence bonus",
                    "Channels are strictly additive: refuted by synergistic effects exceeding sum"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Heerwagen field authority"
            }
        },
        {
            "step": 4,
            "justification": {
                "data": [
                    "Stress reduction: cortisol ↓ ~8-15%, blood pressure ↓, HRV shift to parasympathetic",
                    "NK cell activity ↑ ~50% (forest exposure); ~25-30% (indoor exposure)",
                    "Duration: hours for physiological markers; accumulated benefit from chronic exposure"
                ],
                "backing": "Li et al. (2009) forest therapy studies with cortisol and NK cell data. Li (2010) literature review. Multiple independent studies on nature exposure and stress reduction.",
                "qualifier": "Confidence 0.5 reflects convergent physiological measurements. EMPIRICAL_ASSOCIATION warrant: physiological outcomes are directly measured.",
                "rebuttal": "Effect sizes vary widely across studies. Individual differences in stress response are substantial. Habituation to natural environments may occur.",
                "competing_accounts": [
                    "Stress reduction is purely psychological (placebo): refuted by stress reduction in sleep, non-conscious contexts",
                    "Nature exposure is not superior to other stress-reduction methods: partially true; comparisons show moderate effects"
                ],
                "depth_tier": "B",
                "panel_debate_reference": "MULTI-I Panel, Feb 2026; Li forest therapy authority"
            }
        }
    ]
}

def generate_toulmin_for_step(template_id: str, step: int) -> dict:
    """Fetch Toulmin justification for a specific template step."""
    if template_id in JUSTIFICATIONS:
        for entry in JUSTIFICATIONS[template_id]:
            if entry["step"] == step:
                return entry["justification"]
    return None

def add_justifications_to_template(template_path: Path) -> bool:
    """Add Toulmin justifications to a template."""
    with open(template_path, 'r') as f:
        template = json.load(f)

    template_id = template.get("template_id")
    if not template_id:
        print(f"  ERROR: No template_id in {template_path.name}")
        return False

    if "mechanism_chain" not in template:
        print(f"  ERROR: No mechanism_chain in {template_id}")
        return False

    modified = False
    for step_obj in template["mechanism_chain"]:
        step_num = step_obj.get("step")

        # Only add justification if it doesn't already exist
        if "justification" not in step_obj or step_obj["justification"] is None:
            justification = generate_toulmin_for_step(template_id, step_num)
            if justification:
                step_obj["justification"] = justification
                modified = True
                print(f"  ✓ Step {step_num}: Added Toulmin justification")
            else:
                print(f"  ⚠ Step {step_num}: No justification found in JUSTIFICATIONS")
        else:
            print(f"  → Step {step_num}: Justification already present (skipped)")

    if modified:
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)
        print(f"✓ WROTE: {template_id}")
        return True
    else:
        print(f"→ SKIPPED: {template_id} (no changes)")
        return False

def main():
    """Process all 9 MULTI-I templates."""
    target_templates = [
        "CROSSMODAL_CONGRUENCE_001.json",
        "CT_AFFECTIVE_TOUCH_001.json",
        "HAP_SURFACE_MATERIAL_001.json",
        "MATERIAL_AGING_TEMPORAL_DEPTH_001.json",
        "MATERIAL_CULTURAL_CONDITIONING_001.json",
        "MATERIAL_IDENTITY_INTEGRATION_001.json",
        "MSI_CONGRUENCY_PRINCIPLE_001.json",
        "MSI_INVERSE_EFFECTIVENESS_002.json",
        "NATURAL_MATERIAL_CONVERGENCE_001.json",
    ]

    print("=" * 80)
    print("MULTI-I TOULMIN JUSTIFICATION PANEL - Adding Justifications")
    print("=" * 80)

    modified_count = 0
    for template_file in target_templates:
        template_path = TEMPLATES_DIR / template_file

        if not template_path.exists():
            print(f"\n✗ NOT FOUND: {template_file}")
            continue

        print(f"\nProcessing: {template_file}")
        if add_justifications_to_template(template_path):
            modified_count += 1

    print("\n" + "=" * 80)
    print(f"COMPLETED: {modified_count}/{len(target_templates)} templates modified")
    print("=" * 80)

if __name__ == "__main__":
    main()
