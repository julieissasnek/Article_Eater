# T1.5 Expansion: Three New Domain Theory Reductions

**Version 0.1 — February 20, 2026**
**Status: DRAFT — requires expert review**

This document provides formal T1.5 reductions for three candidate domain theories, using the format established in THEORY_HIERARCHY_AND_MECHANISMS.md (V1.1). Each reduction decomposes the theory's constructs into existing T2 CMR templates, specifies coverage fractions, identifies irreducible residuals, and names the primary T1 frameworks invoked.

For context on the reduction format, the T1.5 criteria, and the rationale for expansion, see:
- Theory_Tier_Cascade_Narrative.md (the cascade story)
- THEORY_HIERARCHY_AND_MECHANISMS.md §Tier 1.5 (existing reductions: ART, SRT, Biophilia, Prospect-Refuge)

---

## 1. PRIVACY REGULATION THEORY (Altman, 1975)

### Source

Altman, I. (1975). *The environment and social behavior: Privacy, personal space, territory, crowding*. Brooks/Cole. (~4,500 GS citations)

Supporting: Westin, A. F. (1967). *Privacy and freedom*. Atheneum. (~5,000 GS citations); Pedersen, D. M. (1997). Psychological functions of privacy. *Journal of Environmental Psychology*, 17, 147–156. (~500 GS citations); Laurence, G. A., Fried, Y., & Slowik, L. H. (2013). "My space": A moderated mediation model of the effect of architectural and experienced privacy and workspace personalization on emotional exhaustion at work. *Journal of Environmental Psychology*, 36, 144–152. (~300 GS citations)

### Theory Summary

Privacy is a dialectical boundary-regulation process: individuals continuously seek an optimal level of social contact, using environmental mechanisms (walls, doors, distance, orientation, social norms) as regulators. The theory posits four key states:

- **Achieved privacy = desired privacy** → optimal state
- **Achieved privacy < desired privacy** → *crowding* (unwanted social contact)
- **Achieved privacy > desired privacy** → *isolation* (unwanted social absence)
- The optimum is dynamic, shifting with activity, mood, time, and social context

Altman identified four types of privacy (solitude, intimacy, anonymity, reserve) and multiple regulatory mechanisms (personal space, territory, verbal/paraverbal behavior, and the built environment).

### Why T1.5 (Not T1 or T2)

**Not T1**: Privacy regulation describes *what* people do (seek optimal social contact) and *what happens* when they fail (crowding, isolation), but specifies no neural mechanism for how optimal contact level is computed, how boundary violations are detected somatically, or why particular architectural features serve as effective regulators. It is phenomenological.

**Not T2**: It is not a single causal pathway (architectural feature → mechanism → outcome) but an organizing schema covering a large domain of person-environment transactions. Multiple T2 templates are needed to instantiate it.

### Constructs and Reductions

| Construct | Definition | Template Reductions | Coverage | Irreducible Residual |
|-----------|------------|---------------------|----------|---------------------|
| **Desired Privacy** | Internally generated target level of social contact | IC2 (35%): body budget prediction generates social-contact set point as interoceptive target<br>T7 (25%): environmental predictability allows accurate social forecasting<br>T_IE_001 (20%): activity frame sets privacy requirements (studying demands solitude; socializing demands access) | 80% | Cultural/personality variation in base privacy preference; temporal dynamics of shifting desire across minutes/hours |
| **Privacy Regulation Mechanisms** | Behavioral and environmental means of achieving desired privacy | T8 (30%): architectural affordances for privacy (doors, partitions as action possibilities)<br>ENCLOSURE (25%): spatial safety geometry doubles as privacy boundary<br>SC2 (20%): isovist control — visual access/exposure as regulable variable<br>T28 (15%): environmental legibility enables prediction of where others can see/reach | 90% | Social/verbal regulatory mechanisms (not architectural); cultural norms for privacy signaling |
| **Crowding** (achieved < desired) | Psychological experience of insufficient privacy despite or independent of physical density | T5 (30%): boundary violation → HPA activation, cortisol elevation<br>AX4 (25%): perceived loss of control over social contact → stress amplification<br>IC2 (20%): interoceptive prediction error — body expected less social stimulation than received<br>T29 (15%): cumulative allostatic demand from sustained boundary violation | 90% | Stokols's (1972) distinction between density and crowding requires cognitive appraisal component — explicit interpretation of *why* space is insufficient. This is the IE-DPT explicit channel (T_IE_003 semantic override: "I'm being crowded" vs. "this is a fun party" applied to identical density). |
| **Isolation** (achieved > desired) | Psychological experience of insufficient social contact | T50 (40%): social isolation load → allostatic dysregulation<br>T27 (25%): DMN hyper-engagement without social input → rumination<br>NM3 (15%): absence of expected social reward → dopaminergic prediction error | 80% | Volitional solitude (chosen isolation ≠ imposed isolation) — another IE-DPT explicit channel distinction. Activity frame determines whether being alone is "peaceful" or "lonely." |
| **Territory** | Spatial zones under personal/group control, graded from primary (home) to public | SN1 (30%): place recognition — PPA-mediated familiarity with owned space<br>E1 (25%): hippocampal binding of space × identity × affect → territorial memory<br>T66 (25%): learned safety — familiar controlled space inhibits threat circuits<br>T8 (10%): affordance structure of controlled vs. uncontrolled space | 90% | Legal/institutional ownership layer (property rights shape territorial behavior independently of neural mechanisms); symbolic marking (decorating as identity expression) |

### Primary T1 Frameworks Invoked

IC (interoceptive set points for social contact), NM (stress/reward from boundary states), SN (spatial representation of boundaries and territories), EC (affordances of architectural privacy features), PP (prediction errors from boundary violations), MS (territorial memory), DP/IE-DPT (activity frame determines privacy requirements and crowding/isolation interpretation)

### Key Insight from Reduction

The crowding construct is particularly revealing. Stokols (1972) showed that density ≠ crowding; crowding is a *psychological* experience that depends on context. Template reduction shows that the physical-density component is well-covered by T5 (HPA) + AX4 (control) + IC2 (interoceptive PE), reaching ~90% coverage for the physiological response. But the critical Stokols insight — that *identical density* produces crowding in one context (unwanted) and pleasant atmosphere in another (desired) — is precisely what the IE-DPT templates capture. The activity frame ("I am studying" vs. "I am at a party") reconfigures what counts as a boundary violation. This is a clear case where T1.5 → T2 reduction reveals the IE-DPT explicit channel as the mechanism for context-dependence that the original theory could only describe.

### Scientific Consensus and Disagreement

The core dialectical model (privacy as boundary regulation toward a dynamic optimum) is well-supported and widely accepted (Gifford, 2024; Sundstrom, 1986). The main areas of disagreement concern: (a) whether the four privacy types (solitude, intimacy, anonymity, reserve) are truly distinct or collapse into fewer dimensions (Pedersen, 1979, found six types factor-analytically; Marshall, 1974, challenged the typology); (b) the relative contribution of architectural vs. social regulatory mechanisms — Archea (1977) argued that visual access and visual exposure are the fundamental architectural variables, while others emphasize acoustic privacy (Sundstrom et al., 1994) or territorial marking (Brown, 1987); and (c) cross-cultural universality — Altman's model was developed from a Western perspective, and while the dialectical structure may be universal, the specific privacy norms and regulatory mechanisms vary substantially (Newell, 1995; Rapoport, 2005).

---

## 2. KAPLAN PREFERENCE MATRIX (S. Kaplan, 1987; R. Kaplan & S. Kaplan, 1989)

### Source

Kaplan, S. (1987). Aesthetics, affect, and cognition: Environmental preference from an evolutionary perspective. *Environment and Behavior*, 19, 3–32. (~2,500 GS citations)

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press. (~5,000 GS citations)

Supporting: Stamps, A. E. (2004). Mystery, complexity, legibility and coherence: A meta-analysis. *Journal of Environmental Psychology*, 24, 1–16. (~500 GS citations); Herzog, T. R., & Kropscott, L. S. (2004). Legibility, mystery, and visual access as predictors of preference and perceived danger in field/forest settings. *Environment and Behavior*, 36, 659–677. (~200 GS citations)

### Theory Summary

Environmental preference is governed by two basic informational needs — **understanding** (making sense of the environment) and **exploration** (being involved in it) — operating at two temporal scales — **immediate** (the two-dimensional visual array) and **inferred** (the three-dimensional space one could enter). Crossing these yields four informational variables:

|  | Understanding | Exploration |
|--|---------------|-------------|
| **Immediate** (2D scene) | Coherence | Complexity |
| **Inferred** (3D space) | Legibility | Mystery |

All four are predicted to correlate positively with preference. The Kaplans proposed that the relationship between coherence/complexity and preference is inverted-U shaped (intermediate levels preferred), while legibility and mystery have more linear positive relationships.

### Why T1.5 (Not T1 or T2)

**Not T1**: The matrix describes *which informational properties* people prefer but does not specify the neural mechanisms underlying preference for these properties. It provides no account of *why* coherence is pleasurable at the neural level, what computational process produces the "promise of more information" that defines mystery, or how the understanding/exploration trade-off is resolved in real time.

**Not T2**: It is not a single feature → mechanism → outcome pathway but an organizing schema for multiple preference-relevant properties of environmental scenes.

### Relationship to Existing Theories

The Kaplan matrix overlaps substantially with both ART (the Kaplans developed both) and Berlyne's collative variables. ART applies the same informational framework specifically to *restorative* environments. Berlyne's (1971) complexity-preference inverted-U is essentially the complexity column of the matrix. The reduction below makes these overlaps explicit: several of the same templates appear in both ART reductions and Kaplan matrix reductions, confirming that these are not independent theories but overlapping phenomenological descriptions of partly shared mechanisms.

### Constructs and Reductions

| Construct | Definition | Template Reductions | Coverage | Irreducible Residual |
|-----------|------------|---------------------|----------|---------------------|
| **Coherence** | Scene organization; how well elements "hang together"; immediate understanding | T1 (35%): visual scene statistics — coherent scenes have structured spectral properties efficiently processed by V1<br>T22 (30%): rapid gist extraction — PFC categorizes coherent scenes faster (<130ms)<br>T67 (20%): processing fluency — organized scenes reduce cortical processing load → aesthetic pleasure | 85% | Semantic coherence beyond visual structure (a scene can be visually organized but semantically incoherent — furniture in a meadow). This is the conceptual/schema-level coherence that requires MS (E4: schema-dependent encoding) and IE-DPT (explicit categorization). |
| **Complexity** | Richness and variety of elements; how much there is to look at; immediate exploration | VF2 (35%): visual rhythm scaling — intermediate fractal/hierarchical complexity optimizes multi-scale pattern processing<br>NM2 (25%): novelty → dopamine — more distinct elements generate more exploration-reward signals<br>COL1 (15%): chromatic PE — color variety generates prediction errors sustaining interest<br>T9 (10%): rapid implicit evaluation — complexity level generates automatic approach/avoid | 85% | The inverted-U relationship: template reduction can specify *why* intermediate complexity is preferred (VF2 optimal processing) but the individual variation in optimal complexity level depends on expertise, arousal state, and activity frame — again, IE-DPT territory. A designer and a novice have different complexity optima for the same building. |
| **Legibility** | Ease of wayfinding; capacity to form a useful cognitive map; inferred understanding | T3 (40%): spatial layout → cognitive map quality — legible environments produce high-fidelity hippocampal representations<br>SC1 (25%): space syntax integration — integrated layouts enable efficient grid cell metric coding<br>T28 (20%): environmental legibility — landmarks and sight lines reduce internal computation | 85% | Legibility's affective dimension — the *feeling* of being oriented vs. lost goes beyond map quality to include emotional valence (confidence vs. anxiety). T66 (learned safety) partially captures this, but the positive affect of spatial mastery (not just threat absence) may involve NM3 (reward from spatial problem-solving). |
| **Mystery** | Promise of new information if one proceeds deeper; inferred exploration | SC3 (30%): architectural promenade — sequential space revelation generates episodic spatial encoding and anticipatory engagement<br>NM2 (25%): novelty anticipation → dopamine — the *promise* of information generates wanting-system activation<br>SC2 (20%): isovist visual prediction — partial occlusion + visible continuation generates spatial prediction with uncertain resolution<br>ENCLOSURE (10%): spatial safety must be maintained for mystery to be pleasant rather than threatening | 85% | Mystery vs. danger: the same partial occlusion can produce pleasant mystery or threat depending on perceived safety. Herzog & Miller (1998) showed that mystery and perceived danger interact — mystery enhances preference only when danger is low. This interaction requires the ENCLOSURE template as a gate, but the appraisal process ("is this mysterious or dangerous?") is an explicit-channel (IE-DPT) evaluation. |

### Primary T1 Frameworks Invoked

PP (all four constructs involve prediction error dynamics at different levels), SN (legibility is fundamentally cognitive-map quality; mystery involves spatial prediction), NM (exploration motivation; complexity-arousal relationship), EC (mystery and legibility involve potential movement through space), DT (coherence reduces attentional demand, enabling DMN engagement), DP/IE-DPT (expertise and activity frame shift all four optima)

### Key Insight from Reduction

The most revealing outcome is that all four Kaplan variables can be recast as different aspects of the prediction error landscape:

- **Coherence** = low aggregate PE in the visual field → efficient processing → fluency → preference
- **Complexity** = moderate aggregate PE → sustained engagement without overload → inverted-U
- **Legibility** = low *spatial* PE → confident cognitive map → reduced navigational anxiety
- **Mystery** = anticipated PE *reduction* upon exploration → dopaminergic wanting signal → approach

This means the Kaplan matrix, at one level of abstraction, *is* Predictive Processing applied to environmental scenes. The four constructs partition the PE landscape by temporal scale (immediate vs. inferred) and valence (understanding = PE reduction; exploration = PE pursuit). This is both elegant and potentially reductive — it suggests the Kaplan matrix may not need to stand as a separate T1.5 theory at all but may instead be a useful labeling system for PP-derived predictions about environmental preference.

However, the irreducible residuals — semantic coherence, individual complexity optima, the mystery/danger interaction — all point to the same thing: the explicit channel. The Kaplan matrix works well for immediate, pre-reflective environmental preference (the implicit channel), but needs IE-DPT to handle context-dependent, expertise-modulated, meaning-laden preference. This is consistent with the Kaplans' own framing, which is explicitly evolutionary and pre-cognitive.

### Scientific Consensus and Disagreement

Stamps (2004) conducted the most comprehensive meta-analysis (28 studies, 6,288 participants, 1,820 scenes) and found significant but heterogeneous support: mystery was the most consistent predictor (weighted mean r ≈ 0.30 across environments), coherence was positive for built environments but weaker for natural, complexity showed the most variability, and legibility had the weakest and most inconsistent results. The considerable heterogeneity in all four variables is exactly what the tier architecture would predict: the phenomenological constructs are real but insufficiently specified to produce consistent results without controlling for the neural-level variables (individual PE landscapes, expertise, activity frame) that the T1 frameworks provide.

Joye and van den Berg (2011) argued that the evolutionary framing of the Kaplans' preference model is unnecessary — the preference patterns can be explained by general perceptual processing principles without invoking evolutionary adaptation to ancestral landscapes. This critique is consistent with the PP reduction above: if coherence, complexity, legibility, and mystery are all PE variables, they apply to *any* environment (natural, built, virtual, abstract), not just landscapes, and no evolutionary story is needed. Partial confirmation comes from studies showing the same preference patterns in non-landscape stimuli (abstract art, building facades, interior spaces — see Herzog & Shier, 2000; Dosen & Ostwald, 2016).

---

## 3. ADAPTIVE THERMAL COMFORT THEORY (de Dear & Brager, 1998; de Dear, Brager, & Cooper, 1998)

### Source

de Dear, R. J., & Brager, G. S. (1998). Developing an adaptive model of thermal comfort and preference. *ASHRAE Transactions*, 104(1), 145–167. (~5,000 GS citations)

Contrasted with: Fanger, P. O. (1970). *Thermal comfort: Analysis and applications in environmental engineering*. Danish Technical Press. (~8,000 GS citations)

Supporting: Nicol, J. F., & Humphreys, M. A. (2002). Adaptive thermal comfort and sustainable thermal standards for buildings. *Energy and Buildings*, 34, 563–572. (~3,500 GS citations); Brager, G. S., & de Dear, R. J. (1998). Thermal adaptation in the built environment: A literature review. *Energy and Buildings*, 27, 83–96. (~3,000 GS citations)

### Theory Summary

Fanger's (1970) Predicted Mean Vote (PMV) model treated thermal comfort as a static heat-balance problem: given air temperature, humidity, air velocity, mean radiant temperature, metabolic rate, and clothing insulation, a single "neutral" temperature can be computed. The model predicted that all humans, in all contexts, would prefer approximately the same thermal conditions once clothing and activity were accounted for.

de Dear and Brager's adaptive model challenged this by analyzing field studies from 160 buildings across four continents (the ASHRAE RP-884 database). They found:

1. **In naturally ventilated buildings**, occupants accepted and preferred a *wider* range of temperatures than PMV predicted, and their comfort temperature tracked outdoor temperature (approximately: T_comfort ≈ 0.31 × T_outdoor_running_mean + 17.8°C)
2. **In air-conditioned buildings**, occupants matched PMV predictions more closely and accepted narrower temperature ranges
3. The discrepancy was attributed to three adaptive mechanisms:
   - **Behavioral adaptation**: adjusting clothing, opening windows, moving to cooler/warmer zones
   - **Physiological adaptation**: acclimatization over days to weeks
   - **Psychological adaptation**: adjusted expectations, perceived control, naturalness of conditions

The psychological adaptation component — that people who *expect* variation and *have control* tolerate wider ranges — is the most architecturally consequential claim and the most clearly T1.5.

### Why T1.5 (Not T1 or T2)

**Not T1**: The adaptive model organizes robust field data showing that context and expectations matter for thermal comfort, but specifies no neural mechanism for *why* perceived control changes thermal tolerance, *how* expectations are formed and updated neurally, or *what* interoceptive prediction process generates comfort vs. discomfort.

**Not T2**: It covers an entire domain of thermal-environment transactions (not a single pathway), and its core insight — that psychological factors modulate physical comfort — requires multiple mechanisms.

### Constructs and Reductions

| Construct | Definition | Template Reductions | Coverage | Irreducible Residual |
|-----------|------------|---------------------|----------|---------------------|
| **Thermal Neutrality** | Temperature range judged "neither warm nor cool" | T57 (40%): thermal comfort — thermoregulatory interoception produces body-state signals about thermal balance<br>IC2 (30%): body budget prediction — the brain maintains a thermal prediction model; "comfort" = low interoceptive PE between predicted and actual body temperature<br>T74 (20%): adaptive thermal / allesthesia — thermal pleasure from correcting deviation (drinking cold water on a hot day) | 90% | Individual variation in metabolic rate, body composition, and peripheral vasoregulation that sets different neutral points even controlling for clothing and activity |
| **Behavioral Adaptation** | Occupant actions to modify thermal environment or personal thermal state | T8 (40%): architectural affordances — operable windows, movable shading, accessible thermostats are action possibilities the motor system represents<br>AX4 (25%): perceived control — availability of adaptive actions buffers HPA stress response *independently of whether actions are taken*<br>EC2 (20%): action-perception coupling — thermal discomfort generates motor preparation for adaptive action | 85% | Social constraints on adaptive behavior (can't remove clothing in formal contexts; can't adjust thermostat in shared office). These are norm-governed explicit-channel constraints — IE-DPT territory. |
| **Physiological Adaptation** | Biological acclimatization to repeated thermal exposure | AX11 (40%): acute vs. chronic — temporal exposure pattern drives receptor-level and systemic adaptation<br>AX7 (25%): dose-response — magnitude and duration of thermal exposure determine adaptation extent<br>T7 (15%): predictability → allostasis — regular thermal patterns allow efficient physiological preparation | 80% | True peripheral physiology (sweat gland density, brown fat activation, vascular remodeling) operates below any cognitive level. These are physiological, not psychological, mechanisms and may not require CMR template representation. |
| **Psychological Adaptation** | Adjusted expectations and tolerance due to context and perceived control | IC2 (30%): body budget prediction shifts — *expected* thermal conditions update the interoceptive prediction model; discomfort = deviation from expectation, not from absolute temperature<br>AX4 (25%): perceived control — belief in controllability reduces thermal stress even when no action is taken (Paciuk, 1990: perceived control was the strongest predictor of thermal satisfaction, stronger than temperature itself)<br>T_IE_001 (20%): activity frame — "I chose a naturally ventilated building" constitutes an explicit frame that reconfigures thermal expectations<br>E4 (10%): schema-dependent encoding — prior thermal experience creates contextual schemas for expected conditions | 85% | "Naturalness" preference — de Dear & Brager found that people prefer natural thermal stimulation (breezes, sun patches) even when equivalent artificial stimulation is available. This is a biophilia-related preference that goes beyond expectation management. May require MSI (cross-modal natural-cue convergence via MAT4) and possibly biophilia constructs. |

### Primary T1 Frameworks Invoked

IC (interoceptive prediction as the computational basis of thermal comfort), PP (thermal prediction error as discomfort signal), NM (HPA activation from thermal stress; control as HPA buffer), EC (affordances for behavioral adaptation), MS (schema-dependent thermal expectations), DP/IE-DPT (activity frame determines expected thermal range; explicit choice of building type reconfigures tolerance)

### Key Insight from Reduction

The adaptive model's most important finding — that occupants of naturally ventilated buildings tolerate wider thermal ranges — reduces with remarkable specificity to the IE-DPT framework. Here is the causal chain:

1. **Building type selection** (naturally ventilated vs. air-conditioned) is an explicit, Type 2 decision — or at minimum, an explicit context-frame
2. This frame generates **thermal expectations** (IC2: body budget prediction) — "in this building, temperature will vary"
3. Wider expected range means each actual temperature generates **smaller interoceptive PE** — predicted variation ≈ experienced variation
4. Smaller PE → **less discomfort** even at temperatures that would be uncomfortable in an AC building where the expectation is narrow
5. Simultaneously, operable windows and adjustable shading provide **perceived control** (AX4), which buffers HPA stress response independently of actual temperature
6. The combination of accurate expectations + perceived control produces the observed **wider comfort band**

This is a textbook case of the IE-DPT four-step bridge mechanism:
- Step 1: Activity/context frame selection (EXPLICIT) — "I'm in a naturally ventilated building"
- Step 2: Frame reconfigures affordance ecology — what adaptive actions are available
- Step 3: Reconfiguration is largely IMPLICIT — interoceptive prediction model adjusts expected range
- Step 4: Effective stimulus changes — same 28°C generates less PE in NV context than AC context → different comfort rating

The Fanger PMV model, by contrast, operates entirely within the implicit channel — it computes thermal balance from physical variables as if no expectation, control, or context exists. This is why PMV works in air-conditioned buildings (where the context minimizes explicit-channel contributions) but fails in naturally ventilated buildings (where the explicit channel is heavily engaged).

### Scientific Consensus and Disagreement

The adaptive model is well-supported and has been incorporated into international standards (ASHRAE Standard 55-2017; EN 15251:2007). The main areas of disagreement concern: (a) the regression coefficients — Humphreys and Nicol (2002) found somewhat different slopes for the comfort-outdoor temperature relationship in different climates, and the Griffiths method vs. regression slope debate continues (Humphreys et al., 2016); (b) whether the adaptive model applies to mixed-mode buildings (Brager & Baker, 2009, found intermediate adaptation); (c) the relative contribution of the three adaptation channels — physiological adaptation may account for more of the variance than de Dear and Brager attributed to it (Haldi & Robinson, 2008), and psychological adaptation is methodologically difficult to isolate; and (d) heating-season adaptation — most field data come from cooling-season studies, and whether the adaptive model applies symmetrically to cold conditions is debated (Nicol & Roaf, 2017).

---

## CROSS-CUTTING ANALYSIS: WHAT THE THREE REDUCTIONS REVEAL

### 1. IE-DPT Appears Everywhere

All three reductions independently converge on IE-DPT (the explicit channel) to explain their most interesting phenomena:

- **Privacy Regulation**: The Stokols density ≠ crowding insight requires activity-frame-dependent appraisal of the *same* physical density
- **Kaplan Matrix**: Individual variation in complexity optima, the mystery/danger interaction, and semantic (vs. visual) coherence all require explicit-channel processing
- **Adaptive Thermal Comfort**: The entire adaptive model's most consequential finding (wider comfort bands in NV buildings) is an IE-DPT four-step bridge mechanism

This pattern — that T1.5 theories work well for the implicit channel but need IE-DPT for context-dependence — appears to be a *general property* of T1.5 → T2 reduction. It confirms the superordinate status of IE-DPT: the activity frame is not one factor among many but the *configurational context* within which all implicit-level processing operates.

### 2. Irreducible Residuals Cluster in Predictable Ways

Across all three theories (and the four previously reduced), the irreducible residuals fall into a few categories:

| Residual Type | Examples | Likely Resolution |
|---------------|----------|-------------------|
| **Explicit-channel effects** | Crowding appraisal, expertise-modulated complexity, NV building expectations | IE-DPT templates (T_IE_001–012) |
| **Cultural/social norms** | Privacy norms, social constraints on thermal adaptation, symbolic territorial marking | Require cultural-context module (not yet specified) |
| **Individual physiological variation** | Autonomic tone, metabolic rate, receptor density | Below cognitive level; may not require CMR templates |
| **Temporal dynamics** | Shifting privacy desires, adaptation over days/weeks, habituation | AX11 (acute vs. chronic) partially covers; may need temporal extension of template format |

### 3. Template Re-Use Reveals Cross-Theory Structure

Several templates appear across multiple T1.5 reductions:

| Template | Appears in | Role |
|----------|-----------|------|
| AX4 (Perceived Control) | Privacy Regulation, Adaptive Thermal Comfort, [SRT] | Control as universal stress buffer |
| IC2 (Body Budget Prediction) | Privacy Regulation, Adaptive Thermal Comfort | Interoceptive prediction as substrate for "comfort" in multiple modalities |
| T8 (Architectural Affordances) | Privacy Regulation, Adaptive Thermal Comfort | Environmental action possibilities as regulatory mechanisms |
| ENCLOSURE (Spatial Safety) | Privacy Regulation, Kaplan Matrix, [Biophilia, Prospect-Refuge, SRT] | Safety geometry as prerequisite for non-threatening environmental engagement |
| NM2 (Novelty → Dopamine) | Kaplan Matrix (complexity, mystery) | Exploration motivation |
| SC2 (Isovist Visual Prediction) | Privacy Regulation, Kaplan Matrix, [ART, Prospect-Refuge] | Visual access/exposure as fundamental environmental variable |

AX4 (perceived control) and IC2 (body budget prediction) are emerging as *core architectural templates* — they appear in almost every T1.5 reduction because control and predictability are universal modulators of environmental experience. This suggests they may warrant elevation to something like "super-templates" or "meta-templates" that interact with most other templates.

### 4. New Templates May Be Needed

The reductions suggest several templates not yet in the library that would improve coverage:

| Proposed ID | Name | Framework | Need |
|-------------|------|-----------|------|
| PR1 | Social Boundary Detection | IC + NM | Interoceptive detection of interpersonal distance violations; peripersonal space representation; amygdala-mediated boundary defense (Kennedy et al., 2009) |
| PR2 | Territorial Familiarity | MS + SN | Hippocampal binding of space-identity-safety forming territorial attachment; related to but distinct from E1 and SN1 |
| KP1 | Scene Coherence Processing | PP | Visual-statistical coherence extraction at V1 level; related to T1 but specific to organizational structure rather than spectral statistics |
| KP2 | Spatial Mystery / Anticipated PE | PP + NM | Dopaminergic anticipation from partial environmental information; the "promise of more" as wanting-system activation from predicted PE reduction |
| TC1 | Thermal Expectation Update | IC + PP | Context-dependent shifting of interoceptive thermal predictions; mechanism underlying psychological adaptation in the adaptive model |

---

## PROPOSED EXPANDED T1.5 ROSTER

Including the four existing reductions and three new ones, plus candidates identified but not yet reduced:

| # | Theory | Status | Domain |
|---|--------|--------|--------|
| 1 | ART (Kaplan, 1995) | **Reduced** — in THEORY_HIERARCHY | Nature/Restoration |
| 2 | SRT (Ulrich, 1983) | **Reduced** — in THEORY_HIERARCHY | Nature/Restoration |
| 3 | Biophilia (Wilson, 1984) | **Reduced** — in THEORY_HIERARCHY | Nature/Restoration |
| 4 | Prospect-Refuge (Appleton, 1975) | **Reduced** — in THEORY_HIERARCHY | Nature/Restoration |
| 5 | **Privacy Regulation (Altman, 1975)** | **Reduced** — this document | Social-Spatial |
| 6 | **Kaplan Preference Matrix (Kaplan & Kaplan, 1989)** | **Reduced** — this document | Visual Preference |
| 7 | **Adaptive Thermal Comfort (de Dear & Brager, 1998)** | **Reduced** — this document | Thermal/IEQ |
| 8 | Berlyne Complexity-Preference (1971) | Candidate — partially overlaps with Kaplan Matrix | Visual Preference |
| 9 | Space Syntax (Hillier & Hanson, 1984) | **Candidate — high priority** | Spatial Configuration |
| 10 | Defensible Space / CPTED (Newman, 1972) | Candidate | Spatial Configuration |
| 11 | Place Attachment (Altman & Low, 1992; Scannell & Gifford, 2010) | **Candidate — high priority** | Place Experience |
| 12 | Crowding Theory (Stokols, 1972; Baum & Valins, 1977) | Candidate — partially covered by Privacy Regulation | Social-Spatial |
| 13 | Proxemics (Hall, 1966; Sommer, 1969) | Candidate — has some neural evidence (Kennedy et al., 2009) | Social-Spatial |
| 14 | Soundscape Theory (Schafer, 1977; ISO 12913) | **Candidate — high priority** | Acoustic/IEQ |
| 15 | Mehrabian-Russell PAD Model (1974) | Candidate | Affective Response |
| 16 | Conceptual Metaphor / Architecture (Lakoff & Johnson, 1980) | Candidate — evidence mixed | Embodied Meaning |
| 17 | Savanna Hypothesis (Orians, 1986) | Candidate — may collapse into Biophilia + Prospect-Refuge | Nature/Restoration |
| 18 | Fractal Fluency (Taylor, 2006) | Candidate — may collapse into Berlyne inverted-U | Visual Preference |

Bold "high priority" marks theories with large empirical literatures and clear reducibility.

---

## REFERENCES

Altman, I. (1975). *The environment and social behavior: Privacy, personal space, territory, crowding*. Brooks/Cole. (~4,500 GS)

Altman, I., & Low, S. M. (Eds.). (1992). *Place attachment*. Plenum Press. (~5,000 GS)

Appleton, J. (1975). *The experience of landscape*. Wiley. (~3,500 GS)

Archea, J. (1977). The place of architectural factors in behavioral theories of privacy. *Journal of Social Issues*, 33, 116–137. (~400 GS)

Baum, A., & Valins, S. (1977). *Architecture and social behavior: Psychological studies of social density*. Erlbaum. (~1,200 GS)

Berlyne, D. E. (1971). *Aesthetics and psychobiology*. Appleton-Century-Crofts. (~4,000 GS)

Brager, G. S., & Baker, L. (2009). Occupant satisfaction in mixed-mode buildings. *Building Research & Information*, 37, 369–380. (~200 GS)

Brager, G. S., & de Dear, R. J. (1998). Thermal adaptation in the built environment: A literature review. *Energy and Buildings*, 27, 83–96. (~3,000 GS)

Brown, B. B. (1987). Territoriality. In D. Stokols & I. Altman (Eds.), *Handbook of environmental psychology* (Vol. 1, pp. 505–531). Wiley. (~300 GS)

de Dear, R. J., & Brager, G. S. (1998). Developing an adaptive model of thermal comfort and preference. *ASHRAE Transactions*, 104(1), 145–167. (~5,000 GS)

de Dear, R. J., Brager, G. S., & Cooper, D. (1998). *Developing an adaptive model of thermal comfort and preference* (ASHRAE RP-884 final report). ASHRAE. (~2,000 GS)

Dosen, A. S., & Ostwald, M. J. (2016). Evidence for prospect-refuge theory: A meta-analysis of the findings of environmental preference research. *City, Territory and Architecture*, 3, 4. (~150 GS)

Fanger, P. O. (1970). *Thermal comfort: Analysis and applications in environmental engineering*. Danish Technical Press. (~8,000 GS)

Gifford, R. (2024). *Environmental psychology: Principles and practice* (6th ed.). Optimal Environments. (~4,000 GS for earlier editions)

Haldi, F., & Robinson, D. (2008). On the behaviour and adaptation of office occupants. *Building and Environment*, 43, 2163–2177. (~500 GS)

Hall, E. T. (1966). *The hidden dimension*. Doubleday. (~15,000 GS)

Herzog, T. R., & Miller, E. J. (1998). The role of mystery in perceived danger and environmental preference. *Environment and Behavior*, 30, 429–449. (~300 GS)

Herzog, T. R., & Shier, R. L. (2000). Complexity, age, and building preference. *Environment and Behavior*, 32, 557–575. (~200 GS)

Hillier, B., & Hanson, J. (1984). *The social logic of space*. Cambridge University Press. (~7,000 GS)

Humphreys, M. A., & Nicol, J. F. (2002). The validity of ISO-PMV for predicting comfort votes in every-day thermal environments. *Energy and Buildings*, 34, 667–684. (~1,500 GS)

Humphreys, M. A., Rijal, H. B., & Nicol, J. F. (2013). Updating the adaptive relation between climate and comfort indoors: New insights and an extended database. *Building and Environment*, 63, 40–55. (~500 GS)

Joye, Y., & van den Berg, A. E. (2011). Is love for green in our genes? A critical analysis of evolutionary assumptions in restorative environments research. *Urban Forestry & Urban Greening*, 10, 261–268. (~250 GS)

Kaplan, R., & Kaplan, S. (1989). *The experience of nature: A psychological perspective*. Cambridge University Press. (~5,000 GS)

Kaplan, S. (1987). Aesthetics, affect, and cognition: Environmental preference from an evolutionary perspective. *Environment and Behavior*, 19, 3–32. (~2,500 GS)

Kennedy, D. P., Gläscher, J., Tyszka, J. M., & Adolphs, R. (2009). Personal space regulation by the human amygdala. *Nature Neuroscience*, 12, 1226–1227. (~700 GS)

Lakoff, G., & Johnson, M. (1980). *Metaphors we live by*. University of Chicago Press. (~50,000 GS)

Laurence, G. A., Fried, Y., & Slowik, L. H. (2013). "My space": A moderated mediation model of the effect of architectural and experienced privacy and workspace personalization on emotional exhaustion at work. *Journal of Environmental Psychology*, 36, 144–152. (~300 GS)

Marshall, N. J. (1974). Dimensions of privacy preferences. *Multivariate Behavioral Research*, 9, 255–271. (~200 GS)

Mehrabian, A., & Russell, J. A. (1974). *An approach to environmental psychology*. MIT Press. (~6,000 GS)

Newell, P. B. (1995). Perspectives on privacy. *Journal of Environmental Psychology*, 15, 87–104. (~400 GS)

Newman, O. (1972). *Defensible space: Crime prevention through urban design*. Macmillan. (~4,000 GS)

Nicol, J. F., & Humphreys, M. A. (2002). Adaptive thermal comfort and sustainable thermal standards for buildings. *Energy and Buildings*, 34, 563–572. (~3,500 GS)

Nicol, F., & Roaf, S. (2017). Rethinking thermal comfort. *Building Research & Information*, 45, 711–716. (~150 GS)

Paciuk, M. (1990). The role of personal control of the environment in thermal comfort and satisfaction at the workplace. In *Coming of age: Proceedings of the 21st Annual Conference of the Environmental Design Research Association* (pp. 303–312). EDRA. (~200 GS)

Pedersen, D. M. (1979). Dimensions of privacy. *Perceptual and Motor Skills*, 48, 1291–1297. (~200 GS)

Pedersen, D. M. (1997). Psychological functions of privacy. *Journal of Environmental Psychology*, 17, 147–156. (~500 GS)

Rapoport, A. (2005). *Culture, architecture, and design*. Locke Science Publishing. (~300 GS)

Scannell, L., & Gifford, R. (2010). Defining place attachment: A tripartite organizing framework. *Journal of Environmental Psychology*, 30, 1–10. (~3,000 GS)

Sommer, R. (1969). *Personal space: The behavioral basis of design*. Prentice-Hall. (~5,000 GS)

Stamps, A. E. (2004). Mystery, complexity, legibility and coherence: A meta-analysis. *Journal of Environmental Psychology*, 24, 1–16. (~500 GS)

Stokols, D. (1972). On the distinction between density and crowding: Some implications for future research. *Psychological Review*, 79, 275–277. (~2,500 GS)

Sundstrom, E. (1986). *Work places: The psychology of the physical environment in offices and factories*. Cambridge University Press. (~1,000 GS)

Sundstrom, E., Town, J. P., Rice, R. W., Osborn, D. P., & Brill, M. (1994). Office noise, satisfaction, and performance. *Environment and Behavior*, 26, 195–222. (~500 GS)

Taylor, R. P. (2006). Reduction of physiological stress using fractal art and architecture. *Leonardo*, 39, 245–251. (~400 GS)

Westin, A. F. (1967). *Privacy and freedom*. Atheneum. (~5,000 GS)
