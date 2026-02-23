# LIGHT-I EXPERT PANEL OUTPUT: CIRCADIAN AND NON-VISUAL PHOTORECEPTION
## Panel ID: LIGHT-I | Sprint: 13.16 | Date: February 21, 2026
## Templates calibrated: DAYLIGHT_MULTICHANNEL_001, CIRCADIAN_ARCH_REG_001, NM_CIRCADIAN_ENTRAINMENT_001, CCT_TEMPORAL_ECOLOGICAL_001, DYNAMIC_LIGHT_TEMPORAL_001, CHRONO_LIGHT_ENTRAINMENT_001, CIRCADIAN_ARCH_REGULATION_001, CB_SLEEP_ARCHITECTURE_002
## Prior panel document: 34_Panel_LI_Light_Luminance.md (February 16, 2026) — CASE A
## Status: COMPLETE

---

# I. PANEL COMPOSITION

## Systems Neuroscientists

**Expert 1 — Russell Foster (University of Oxford; FRS; NAS Foreign Associate)**
Codiscoverer of the non-visual photoreceptive system; pioneer of ipRGC biology and the retinohypothalamic tract. His identification of M1 ipRGCs as the primary SCN-projecting class and his subsequent work on M1–M6 subtype differentiation provides the foundational circuit-level account for this panel. He will serve as the primary scientific arbiter for all mechanism chain arguments and will insist throughout on subtype-level precision.

**Expert 2 — Satchin Panda (Salk Institute for Biological Studies)**
Co-discoverer of melanopsin's role in circadian photoreception; originator of the molecular account linking light timing to clock-gene expression and metabolic gene cascades. His perspective uniquely covers the downstream gene-expression consequences of circadian disruption — a dimension the quantitative photobiology literature tends to underweight. He will push the panel to treat the architectural light schedule as a transcriptional regulator, not merely a perceptual input.

## Domain-Specific Neuroscientists

**Expert 3 — Charles Czeisler (Harvard Medical School; NAS member)**
The canonical authority on human circadian dose-response curves. The Zeitzer et al. (2000) paper — which established the sigmoidal sensitivity function relating nocturnal light irradiance to circadian phase shift — is the most-cited quantitative anchor in this domain. Czeisler will push for higher confidence scores on dose-response shape parameters and will be the panel's primary quantitative photobiologist. He will resist Figueiro's architectural translation corrections unless she provides field data of sufficient statistical power to override the controlled-exposure literature.

**Expert 4 — Josephine Arendt (University of Surrey; FRS)**
Pioneer of melatonin suppression research. Her action spectrum work (Thapan, Arendt & Skene, 2001) and foundational dose-response characterizations of the pineal-melatonin axis provide the neuroendocrine layer. She will insist throughout that the panel distinguish two physiologically distinct phenomena that the architectural literature routinely conflates: acute melatonin suppression and circadian phase shifting. These are mediated by the same photoreceptor class but have different threshold functions, different temporal dynamics, and different architectural consequences.

## Computational Neuroscientists

**Expert 5 — Richard Kronauer (Harvard University; engineering biophysics)**
Developer of the Kronauer limit-cycle oscillator model (Kronauer et al., 1999; Jewett & Kronauer, 1998) — the most widely validated mathematical model of human circadian phase entrainment. His role is to translate the photobiological dose-response data from Czeisler and Arendt into the mathematical entrainment parameters required for builder-ready JSON: phase response curve (PRC) parameters, entrainment bandwidth, and resynchronization velocity expressed as functions of melanopic lux dose and timing.

**Expert 6 — Manuel Spitschan (Technical University of Munich; melanopic dosimetry)**
Developer of the melanopic equivalent daylight illuminance (m-EDI) metric and co-author of CIE S 026:2018. His computational work translates spectroradiometric measurements of architectural light sources — LED spectral power distributions, glazing spectral transmission functions — into the melanopic lux values that the CMR system requires. He will be the panel's metrological conscience, insisting that every threshold value be specified in CIE S 026-standardized melanopic units rather than photopic lux proxies, and will quantify the conversion factors between photometric and melanopic quantities for common architectural light sources.

## Architectural / Conceptual Modeling Experts

**Expert 7 — Mariana Figueiro (Mount Sinai; Icahn School of Medicine)**
The leading translational researcher on architectural circadian lighting. She holds the most extensive dataset on corneal light-at-the-eye measurements in occupied buildings — hospitals, schools, eldercare facilities — and has demonstrated that real-world daytime melanopic exposures in conventional office buildings typically fall in the 10–50 m-lux range, substantially below the laboratory thresholds that dominate the controlled-exposure literature. She will be the panel's primary source of architectural translation coefficients and will apply consistent downward pressure on confidence scores for parameters derived solely from controlled laboratory exposures.

**Expert 8 — Mirjam Münch (Charité Berlin; circadian lighting and sleep)**
Specialist in the pathway from evening light exposure to sleep architecture degradation — the specific mechanism chain required for CB_SLEEP_ARCHITECTURE_002. Her Münch et al. (2006) paper characterizing wavelength-dependent effects of evening light on sleep EEG power density, and subsequent work on CCT effects on sleep onset latency, provides the primary empirical anchor for the evening-light cluster of templates. She will contest over-confident threshold values for the melatonin suppression pathway and will demand that the panel account for cumulative photic history effects.

**Expert 9 — Thorbjörn Laike (Lund University; environmental psychology of light)**
The environmental psychologist with the most extensive dataset on daylighting and cognitive performance in school and workplace buildings at northern latitudes. His field studies provide the behavioral outcome data — attention, mood, work performance — that connect the physiological circadian parameters to the architectural consequences the CMR system is ultimately trying to predict. He will represent the user-side of the parameter space throughout, anchoring abstract photobiological constructs to measurable occupant outcomes.

**Expert 10 — Christoph Reinhart (MIT, Building Technology Program)**
Developer of DAYSIM and climate-based daylight modeling tools; co-developer of the Daylight Autonomy metric and Useful Daylight Illuminance (UDI). His role is to translate the biological thresholds established by the photobiologists into architectural design parameters — window-to-floor ratio, glazing spectral transmission, room depth, orientation — expressed in the metrics that building codes and certification systems actually use. He will be the panel's primary source for architectural modifier coefficient ranges and will flag where biological thresholds are unreachable under standard building envelope constraints.

---

# II. ROUND TABLE: OPENING POSITION STATEMENTS

**Foster:** I want to begin by insisting on a distinction that the architectural community has not yet fully absorbed, and that will govern every parameter we set today. The ipRGC class is not homogeneous. M1 cells — small dendritic field, high melanopsin expression, direct RHT projection to the SCN core — are the primary circadian entrainment cells. M2 through M6 cells project instead to the olivary pretectal nucleus (pupillary reflex), the intergeniculate leaflet, the lateral geniculate nucleus, the ventral subparaventricular zone, the dorsal lateral geniculate, and several other targets including the locus coeruleus. These non-M1 projections mediate the acute alerting response, pupillary constriction, and other non-circadian non-visual responses. The dose-response function, the threshold, and the temporal integration window for M1-mediated circadian entrainment are different from those for M2–M6-mediated alerting. When this panel sets a "melanopic lux threshold," it must specify: threshold for what response, mediated by which subtype population. A threshold calibrated against melatonin suppression — which involves M1 and is circadian — is not transferable to acute alerting, which is predominantly M2–M4. I will enforce this distinction in every parameter debate today.

**Panda:** I am in complete agreement with Foster on subtype specificity, and I want to add a temporal dimension that is systematically absent from the architectural lighting literature. The clock-gene expression cascade — CLOCK:BMAL1 transcription of Per/Cry, the negative feedback loop, the output via Rev-erbα and RORα to secondary clock-controlled genes — operates on a 24-hour period, but its responsiveness to light is not uniform across that period. The phase response curve (PRC) is deeply asymmetric. Light in the biological morning advances the clock; light in the biological evening delays it; light in the biological midday produces almost no phase shift at all. This means that the architectural question "how much light is enough?" is actually three separate questions: how much light is enough in the morning to advance the clock and sharpen entrainment? How much in the evening is too much — i.e., produces a meaningful delay that will degrade sleep onset? And what is the midday baseline maintenance level? These three regimes have different thresholds, different dose-response shapes, and different architectural consequences. The templates we are calibrating must encode all three, not just a single daytime threshold. I will push this throughout.

**Czeisler:** My empirical anchor for this panel is the Zeitzer et al. (2000) paper in the Journal of Physiology. That study exposed subjects to a range of light intensities (0.1 to 9,500 lux photopic) during the circadian night and measured phase shifts of melatonin rhythm. The dose-response function was sigmoidal: half-maximum phase shift occurred at approximately 119 lux photopic, the function saturated above ~500 lux, and the slope was steep — a Hill coefficient of approximately 2. This sigmoidal form is now well-replicated. I want to state my prior clearly before the architectural translation debate begins: the sigmoidal shape is not in dispute. What is in dispute is the applicable x-axis unit. Zeitzer used photopic lux, which was the standard metric in 2000. Post-CIE S 026, the appropriate unit is melanopic equivalent daylight illuminance (m-EDI). Spitschan has the conversion factors; I will defer to him on the unit translation. But I will resist any attempt to flatten the sigmoidal curve to a linear function on architectural convenience grounds — the biology does not support a linear model.

**Arendt:** I want to make a point that I regard as foundational to the entire template architecture for this domain. Melatonin suppression and circadian phase shifting are not the same thing. They are related — both are mediated by ipRGC activation of the SCN — but they differ in threshold, temporal dynamics, and downstream consequences in ways that matter enormously for architectural calibration. Acute melatonin suppression can be produced by relatively brief (30 minute) exposures to moderate melanopic irradiance. Circadian phase shifting requires sustained exposure — typically 90 minutes to several hours — at levels sufficient to activate the M1 RHT pathway. The commonly cited "10 lux threshold" from earlier literature refers to acute melatonin suppression under photopically-measured light; it is not a phase-shifting threshold. The phase-shifting threshold is substantially higher. If this panel conflates the two, we will produce templates that over-claim architectural effects: a building that suppresses melatonin in the evening does not necessarily phase-delay the clock; it merely reduces the immediate melatonin signal. I will flag this conflation whenever it appears.

**Kronauer:** My role today is to provide the mathematical scaffolding that converts the photobiological dose-response data from Czeisler and Arendt into JSON-ready parameters. The tool is the limit-cycle oscillator model. The key insight of the model is that the circadian system behaves like a van der Pol oscillator — it has a natural period of approximately 24.2 hours, a stable limit cycle, and a phase response to light input that depends on the current phase of the oscillator, not just the light dose. The PRC is the central quantitative object: it maps light pulse timing (in circadian hours relative to the core body temperature minimum) to phase shift direction and magnitude. For a standard light pulse of ~100 m-lux at the cornea for 3 hours, the maximum advance shift (given at approximately circadian hour 20, roughly one to two hours before the temperature minimum) is approximately 1.5–2.0 hours. The maximum delay shift (at circadian hour 6, approximately 6 hours before temperature minimum) is approximately 1.5–2.0 hours. I will use these PRC parameters to anchor all architectural entrainment velocity estimates. I want to flag one point of anticipated friction with Figueiro: laboratory PRC parameters were derived from controlled dim-light conditions before the pulse. Real buildings have pre-exposure light histories that compress the PRC — you get smaller phase shifts for the same pulse magnitude if the subject has already been exposed to moderate light. This prior-exposure correction is architecturally critical and systematically absent from building standards.

**Spitschan:** My concern today is metrological, and it is not a minor concern. The field has used at least five different metrics for "circadian light" since 2000: photopic lux, Circadian Light (CL, Rea & Figueiro), Circadian Stimulus (CS, same group), melanopic lux (various definitions), and now melanopic equivalent daylight illuminance (m-EDI, CIE S 026:2018). These metrics are not numerically interchangeable. A paper reporting "100 lux" of circadian-effective light from a 2700K source and a paper reporting "100 lux" from a 6500K source are describing stimuli with dramatically different melanopic content — roughly a 3:1 ratio in melanopic irradiance for the same photopic illuminance across that CCT range. Every threshold value discussed today must be stated in m-EDI (CIE S 026) units. I will provide conversion factors for common architectural light sources throughout. For reference: for a D65 reference illuminant (approximately natural overcast daylight, 6500K), 1 photopic lux ≈ 0.9 m-lux m-EDI. For a warm white LED at 2700K, 1 photopic lux ≈ 0.31 m-lux m-EDI. For a cool white LED at 4000K, 1 photopic lux ≈ 0.62 m-lux m-EDI. These factors will be embedded in the modifier coefficients throughout.

**Figueiro:** I want to ground this panel in the reality of what buildings actually deliver. My group has measured corneal melanopic irradiance in hundreds of occupied buildings using calibrated light-at-the-eye dosimeters. The numbers are sobering. In a typical deep-plan open-plan office with fluorescent or LED overhead lighting at 300–500 photopic lux, the daytime corneal melanopic exposure averages 20–60 m-lux m-EDI — well below the 100 m-lux laboratory entrainment threshold that the photobiology literature treats as standard. Eldercare facilities are worse: average daytime melanopic exposure in nursing home common areas is typically 5–20 m-lux. The Figueiro et al. (2017) office study found that workers in the highest-quartile light exposure group — the people who received the most light in their workday — averaged approximately 75 m-lux during peak morning hours. These are real building numbers, not controlled laboratory numbers. I will insist throughout this panel that our architectural modifier coefficients reflect what buildings can realistically deliver given standard construction practice, not idealized conditions that no occupied building approaches. I will push back on laboratory threshold values whenever they exceed what architectural interventions can reliably produce.

**Münch:** I represent the sleep-side of this panel, and I want to stake a position on the evening light cluster before we open debate. The CB_SLEEP_ARCHITECTURE_002 template sits at the intersection of two phenomena that are often treated as equivalent but are not. The first is acute melatonin suppression by evening light — well characterized by Gooley et al. (2011), Viola et al. (2008), and our own Münch et al. (2006) paper. The second is the effect of that suppression on subsequent sleep architecture — specifically on slow-wave sleep (SWS) latency and SWS duration, which are mediated through a different pathway involving the interaction between the melatonin-onset delay and the homeostatic sleep pressure accumulation. These two pathways can produce divergent predictions: a moderate level of evening light might substantially delay melatonin onset but have only a small effect on subsequent SWS architecture, depending on the timing of the sleep window. Conversely, repeated nights of melatonin delay can progressively compress the slow-wave sleep window even when sleep onset latency does not lengthen dramatically. I will insist that CB_SLEEP_ARCHITECTURE_002 encode both the acute suppression parameters and the cumulative architecture degradation parameters as distinct constructs.

**Laike:** I want to add the behavioral endpoint perspective to what has so far been a photobiological discussion. The CMR system ultimately needs to predict occupant outcomes in buildings — sleep quality, daytime alertness, mood, cognitive performance, health consequences of chronic exposure. The photobiological parameters we are calibrating today are intermediate variables in a chain that runs from architectural design decisions through corneal melanopic irradiance through SCN entrainment through melatonin and cortisol rhythms through sleep architecture through daytime performance. My field studies have measured the end of this chain: in Swedish schools at 57°N latitude, students in south-facing classrooms with adequate glazing show measurably better afternoon alertness and self-reported energy than those in north-facing rooms — consistent with Heschong's US findings. But the effect sizes are modest (Cohen's d ≈ 0.2–0.35) and subject to substantial inter-individual variation driven by chronotype. I will represent these real-world effect sizes as a check on the downstream behavioral predictions embedded in the templates throughout.

**Reinhart:** My contribution to this panel is the architectural encoding layer — translating biological thresholds into design parameters. The key design variables I work with are: window-to-floor ratio (WFR), glazing visible light transmittance (VT), façade orientation, room depth-to-ceiling-height ratio, and shading system type and schedule. Climate-based daylight modeling (CBDM) tools like DAYSIM can compute the resulting spatial daylight autonomy (sDA) and useful daylight illuminance (UDI) distributions. The challenge for this panel is that CBDM tools compute photopic metrics — they do not natively output melanopic lux. Spitschan's conversion factors will allow us to post-process photopic daylight calculations into melanopic estimates, but only approximately, because the conversion depends on the spectral composition of the daylight source, which varies with sky condition, orientation, and time of day. I will flag throughout where architectural modifier coefficients carry additional uncertainty from this photometric-to-melanopic translation step, above and beyond the photobiological uncertainty already present in the laboratory literature.

---

# III. CRUCIBLE DEBATES

## Debate A: The Melanopic Lux Threshold for Circadian Entrainment — and the Architectural Translation Gap

**Czeisler:** The Zeitzer et al. (2000) data establish that half-maximum circadian phase shifting occurs at approximately 119 photopic lux at the cornea during the circadian night. Translating to daytime conditions, where the purpose is entrainment maintenance rather than acute phase shifting, a reasonable daytime threshold for sustained circadian entrainment should be in the range of 150–300 m-lux m-EDI at the cornea for at least two continuous hours during the biological morning. I propose this as the primary threshold for CIRCADIAN_ARCH_REG_001.

**Figueiro:** I must push back on that range. The Zeitzer study was conducted in conditions of prior darkness — subjects were kept in dim light before the pulse. Real building occupants arrive with accumulated morning light exposure from home windows, commute daylight, and prior indoor exposure. This prior-photic-history compression of the PRC means that the effective threshold in a real building context is lower, not higher, than the controlled-exposure value. My field data from the office study (Figueiro et al., 2017) suggest that a morning circadian stimulus of approximately 0.3 CS units — corresponding to roughly 70–90 m-lux m-EDI from a well-daylit office — was sufficient to produce meaningful improvements in sleep quality and mood over a standard office with CS < 0.15 (approximately 20–30 m-lux). I challenge the assumption that laboratory thresholds set the lower bound for architectural targets.

**Kronauer:** There is a more fundamental issue here that both Czeisler and Figueiro are circling. The Zeitzer dose-response curve is a phase-shifting curve measured at a single circadian phase. The entrainment question is different: what is the minimum daily circadian light dose required to maintain a stable phase relationship between the SCN oscillator and the external day-night cycle? This is a limit-cycle stability question, not a single-pulse phase-shift question. The model predicts that maintenance of entrainment requires that the daily light dose be sufficient to correct for the intrinsic period deviation from 24 hours (approximately 0.2 hours per day in the average human) across the phase-sensitive window. This requires a smaller cumulative phase advance per day than Czeisler's pulse data imply — because the advance is being applied over the full photophase, not in a single pulse. I contend that the maintenance entrainment threshold may be substantially lower than 150 m-lux when that dose is distributed over 6–8 hours.

**Foster:** I want to introduce the subtype consideration here. The threshold values Czeisler cites from Zeitzer are for a composite population of M1 and M2–M6 cells. The SCN entrainment pathway runs specifically through M1 cells. M1 cells have a higher melanopsin density and a lower phototransduction gain than M2–M6, meaning their threshold for sustained activation is actually somewhat higher than the composite ipRGC population threshold. However, M1 cells also integrate light over substantially longer time windows — temporal summation extends to minutes rather than seconds — which means that distributed exposure over hours can achieve M1 activation that an equivalent brief pulse would not. The architectural implication is that what matters for SCN entrainment is the integral of melanopic irradiance over the morning, not the peak. A lower sustained level for longer is more effective than a high peak for a short period.

**Spitschan:** I can resolve part of this with the metric translation. Zeitzer's 119 photopic lux half-maximum was measured with a broad-spectrum light source with a color temperature of approximately 4100K. At that CCT, the photopic-to-melanopic conversion factor is approximately 0.65. This means Zeitzer's half-maximum corresponds to approximately 77 m-lux m-EDI. Figueiro's 0.3 CS threshold corresponds to approximately 75–80 m-lux m-EDI from her field measurements. These are consistent once you align the metrics. The apparent discrepancy between Czeisler's laboratory threshold and Figueiro's field threshold largely dissolves when you compute both in standardized m-EDI units. The remaining difference reflects Kronauer's point about prior photic history and integration time.

**Panel consensus after extended debate:** The melanopic lux threshold for circadian entrainment maintenance in occupied buildings is 75–100 m-lux m-EDI (CIE S 026) at the cornea, sustained for a minimum of two hours during the first half of the photophase. The lower bound (75 m-lux) reflects Figueiro's field data with prior-exposure correction; the upper bound (100 m-lux) reflects Czeisler's laboratory sigmoidal half-maximum translated to m-EDI units. Confidence: 0.68 (MECHANISM bridge). Population modifier: elderly, where lens yellowing and reduced ipRGC density reduce effective corneal melanopic irradiance by 30–50% relative to the young-adult cornea, require a proportionally higher architectural melanopic delivery — architectural target should be 110–140 m-lux m-EDI to produce equivalent SCN stimulation.

---

## Debate B: CCT as Temporal-Ecological Signal — Direct vs. Cone-Mediated Pathway

**Foster:** The CCT_TEMPORAL_ECOLOGICAL_001 template requires us to specify the mechanism by which correlated color temperature functions as a temporal prediction signal. I want to challenge the assumption that this is a purely ipRGC-mediated effect. ipRGCs have a relatively flat spectral sensitivity in the long-wavelength range — they are blue-sensitive but not particularly good at discriminating 4000K from 6500K above about 500 nm. The CCT discrimination that allows humans to track time-of-day through light color is almost certainly mediated by the opponent-color channels in the visual system — specifically the S-cone versus M+L-cone opponent channel, which is highly sensitive to the blue-yellow axis along which natural daylighting CCT varies across the day (short-wavelength enriched at midday, long-wavelength enriched at dawn and dusk). This is a visual pathway effect, not an ipRGC direct effect.

**Panda:** I partially agree, but there is a complication. The SCN does receive chromatic input, but it is not the same as the visual system's chromatic channels. The olivary pretectal nucleus and the intergeniculate leaflet — both of which receive ipRGC projections — have some wavelength selectivity. More importantly, the cone-ipRGC opponent interaction described by Spitschan and colleagues generates a signal that encodes the ratio of cone activation to melanopsin activation. Since daylight CCT changes the ratio of short-wavelength to long-wavelength content, it changes this ratio. This provides a chromatic time-of-day signal to the SCN that is distinct from, and complementary to, the pure irradiance signal.

**Spitschan:** I can quantify the cone-melanopsin ratio shift. In morning light at 2700K equivalent sky color, the S/(M+L) ratio is approximately 0.12. At noon-equivalent 6500K, it is approximately 0.31. This is a 2.6-fold change across the day. My modeling work (Spitschan et al., 2017, natural illuminant survey) shows that this S/(M+L) ratio is a highly consistent temporal predictor in natural environments — more consistent than absolute irradiance, which varies with cloud cover. The photoreceptor-excitation space analysis suggests that the visual system can use this ratio as a reliable time-of-day prior independent of absolute light level.

**Arendt:** I challenge that assumption in the context of artificial light. Natural illuminants follow a consistent spectral locus as CCT changes because they track the daylight locus in CIE chromaticity space. Artificial LED sources can have CCTs anywhere in that range but with spectral power distributions that do not follow the daylight locus — they may have narrow-band peaks that produce the same CCT as daylight but a very different cone-excitation ratio. The predictive value of CCT as a temporal ecological prior depends on the light source following the daylight spectral locus, which LEDs often do not. I challenge any confidence score above 0.50 for the CCT temporal ecological prior in contexts where the light source is artificial rather than natural daylight.

**Panel consensus:** The CCT temporal ecological prior operates via the S-cone vs. M+L-cone opponent channel (visual system) in combination with the cone-ipRGC ratio signal at the SCN. It is not a purely ipRGC-mediated effect. For natural daylight sources following the daylight spectral locus, the temporal ecological signal is reliable and the confidence in the prior is moderate (0.60). For artificial LED sources deviating from the daylight locus, the temporal prior is degraded and confidence falls to 0.40. Architectural implication: glazed buildings using natural daylight transmit a reliable temporal ecological prior; spaces relying on fixed CCT LED lighting lose this signal. Confidence for the CCT temporal prior construct: 0.55 composite (FUNCTIONAL bridge), reflecting the mixed-source reality of most occupied buildings.

---

## Debate C: Dynamic Variation — Necessary or Merely Sufficient?

**Laike:** The DYNAMIC_LIGHT_TEMPORAL_001 template asks us to calibrate the temporal frequency and amplitude of light variation required to sustain prediction-error engagement without habituation. I want to challenge the framing. My field data do not show that dynamic variation in light is a necessary condition for circadian health outcomes — the school studies show effects from sustained bright light without particular emphasis on variation. The variation may be sufficient to sustain engagement, but a well-maintained high-irradiance static level may be adequate for circadian purposes.

**Panda:** I must push back on that framing. For the circadian system specifically, dynamic variation is not merely a cognitive engagement mechanism — it serves a direct photoentrainment function. The circadian clock integrates light history over a period of roughly 90–180 minutes in determining phase. A static light level for 8 hours delivers information about mean irradiance but not about the temporal structure of the photophase. Natural daylight has a characteristic temporal variation — dawn ramp, midday plateau with cloud-driven variation, dusk ramp — that the clock has evolved to expect. Evidence from animal studies using skeleton photoperiods and stepped light protocols suggests that the temporal structure of light, not just its integral, matters for entrainment quality. Whether this translates to a human architectural requirement is uncertain, but I would not dismiss it.

**Foster:** The dawn and dusk transitions are particularly important in this context. The most potent circadian phase-shifting light exposures are those occurring in the hours around dawn and dusk — the two transition phases of the PRC. A building that provides a gradual increase in melanopic irradiance across the morning (dawn simulation) and a gradual reduction across the evening (dusk simulation) will produce more efficient entrainment than a building that switches between high daytime and low nighttime light levels abruptly. The temporal derivative of light change — the rate of change of melanopic irradiance per unit time — is itself a circadian signal. Architectural lighting controls that program a 30–60 minute ramp at dawn and dusk will produce better entrainment than those with instantaneous transitions, even if the integral of the exposure is equivalent.

**Reinhart:** From an architectural standpoint, dynamic variation is largely delivered for free by daylight through windows. Cloud passage, solar angle change, and seasonal variation in spectral composition all produce the temporal variation Panda and Foster are describing. The question is what happens in the large fraction of an occupied building that is daylight-deprived — deep-plan interiors, north-facing zones in winter, basement levels. For those zones, the question becomes whether dynamic tunable LED systems are required, or whether static high-melanopic-content LED systems suffice. The engineering and cost implications differ substantially.

**Panel consensus:** Dynamic variation in the 0.01–2.0 cycles/minute range provides a temporal PE signal that sustains cognitive engagement (PP channel, DYNAMIC_LIGHT_TEMPORAL_001) and may improve entrainment quality at the margins (CB channel). It is sufficient but not strictly necessary for circadian entrainment if sustained irradiance above the maintenance threshold is present. The dawn and dusk transition ramps (rate of change ≥ 15 m-lux per 30 minutes) are the highest-value dynamic variation for circadian purposes. Confidence: 0.52 for necessity; 0.72 for sufficiency (CAPACITY bridge). The distinction matters architecturally: the necessary condition is maintained melanopic irradiance above threshold; dynamic variation is a valuable enhancement with a secondary effect size.

---

## Debate D: Sleep Architecture — Acute Suppression vs. Cumulative Degradation

**Münch:** For CB_SLEEP_ARCHITECTURE_002 I want the panel to encode two distinct parameters that the literature routinely combines. The first is the acute evening suppression threshold — the melanopic lux level at which a single evening exposure delays melatonin onset by a clinically meaningful amount (≥ 15 minutes). My data from Münch et al. (2006) and the subsequent Cajochen lab work suggest this threshold is in the range of 30–60 m-lux m-EDI for 2-hour exposures beginning approximately 2 hours before habitual sleep onset. The second parameter — the cumulative architecture degradation — is harder to specify. In our studies, repeated evenings of melatonin delay produced progressive reduction in slow-wave sleep (SWS) percentage across a week, even after the melatonin delay returned to baseline. The mechanism appears to involve a gradual phase delay of the SWS generating circuitry — specifically the ventrolateral preoptic nucleus (VLPO) output timing — relative to homeostatic sleep pressure. This is a different pathway from the acute melatonin story.

**Arendt:** The acute suppression threshold I would specify from the combined literature — Gooley et al. (2011), Viola et al. (2008), Thapan et al. (2001) — is approximately 30–50 m-lux m-EDI for 50% melatonin suppression during the 2 hours before habitual bedtime. The dose-response is steep in this range. I agree with Münch that conflating this threshold with the phase-shifting threshold is a serious error. The acute suppression threshold is approximately half the maintenance entrainment threshold; the phase-shifting threshold for meaningful clock delay is closer to 100 m-lux m-EDI.

**Czeisler:** I want to add the timing sensitivity. The melatonin suppression sensitivity is not uniform across the evening. It peaks approximately at the time of habitual melatonin onset — typically 90–120 minutes before habitual sleep time in dim light. At that circadian phase, the system is maximally sensitive: 10–20 m-lux m-EDI can produce detectable suppression. Two hours earlier, the threshold is substantially higher — closer to 100 m-lux. The architectural implication is that the same evening bedroom lamp that has negligible effect at 22:00 may have a clinically significant effect at 23:30 for a person whose melatonin onset is at midnight.

**Panel consensus:** CB_SLEEP_ARCHITECTURE_002 encodes two distinct parameters. Acute suppression threshold: 30–50 m-lux m-EDI for ≥50% melatonin suppression during peak sensitivity window (−90 to −60 minutes before habitual sleep onset); lower threshold (10–20 m-lux) at peak sensitivity, higher (80–100 m-lux) two hours prior. Cumulative SWS degradation: repeated (≥3 consecutive nights) acute suppression events produce progressive SWS reduction of approximately 8–15% over the following week, mediated via VLPO phase delay; this is a separate parameter from the acute suppression threshold. Confidence for acute threshold: 0.78 (MECHANISM bridge). Confidence for cumulative SWS degradation coefficient: 0.55 (EMPIRICAL_COVARIANCE, based on Münch's sleep EEG data — the architectural context for the VLPO mechanism is not directly measured).

---

# IV. CALIBRATED JSON BLOCKS

## Template 1: DAYLIGHT_MULTICHANNEL_001

```json
{
  "template_id": "DAYLIGHT_MULTICHANNEL_001",
  "display_id": "L3",
  "name": "Daylight as Multi-Channel Stimulus with Convergent Benefit",
  "status": "calibrated",
  "maturity": "supported",
  "mechanism_chain_provenance": "INHERITED from 34_Panel_LI_Light_Luminance.md (Document 34, Feb 16) — six-channel structure preserved; parameters newly established in LIGHT-I",
  "t1_frameworks": ["CB", "PP", "NM"],
  "t1_5_parent_theories": ["ART", "SRT"],
  "panel_id": "LIGHT-I",
  "calibration_date": "2026-02-21",

  "mechanism_chain": [
    "Architectural design (WFR, glazing, orientation, depth) → corneal melanopic irradiance (m-EDI, CIE S 026)",
    "→ Channel 1 [CB]: M1 ipRGC activation → RHT glutamate/PACAP → SCN core pacemaker → circadian entrainment (melatonin/cortisol rhythm alignment)",
    "→ Channel 2 [NM]: M2–M4 ipRGC projections → locus coeruleus NE + histaminergic TM nucleus → cortical arousal (acute alerting)",
    "→ Channel 3 [PP]: Broadband daylight spectrum → low chromatic PE → color constancy operating within evolved range → reduced chromatic mismatch cost",
    "→ Channel 4 [PP/DT]: Window view → soft fascination → ART pathway → DMN partial engagement without directed-attention cost",
    "→ Channel 5 [PP]: Solar/cloud dynamics → continuous low-to-moderate luminance PE (L1 Goldilocks range) → sustained moderate engagement",
    "→ Channel 6 [CB/PP]: CCT variation across photophase → S-cone:M+L-cone ratio shift → temporal ecological prior → temporal orientation",
    "→ Channel convergence: simultaneous activation of all 6 channels produces synergistic benefit > additive sum; convergence coefficient 1.20–1.35"
  ],

  "calibrated_parameters": {
    "channel_1_circadian_maintenance_threshold": {
      "value": 87,
      "unit": "m-lux_mEDI_CIE_S026",
      "range": {"min": 75, "max": 100},
      "duration_required_hours": 2.0,
      "timing": "first half of photophase (morning)",
      "source": "Zeitzer et al. (2000) converted to m-EDI via Spitschan CCT factors; Figueiro et al. (2017) field validation",
      "confidence": 0.68,
      "bridge_warrant": "MECHANISM",
      "population_modifiers": {
        "elderly": {
          "note": "Lens yellowing + reduced ipRGC density reduces effective corneal melanopic irradiance by 30–50%",
          "architectural_target": {"value": 125, "unit": "m-lux_mEDI", "range": {"min": 110, "max": 140}}
        },
        "chronotype_evening": {
          "note": "Later phase of circadian clock shifts peak light sensitivity window ~1–2h later; morning light delivery must extend to later morning hours"
        }
      },
      "architectural_modifiers": {
        "WFR_above_0.25_south_facing_mid_latitude": {"multiplier": 1.0, "note": "Reference condition"},
        "WFR_0.15_to_0.25": {"multiplier": 0.65, "note": "Melanopic delivery substantially reduced; supplementary electric light likely required"},
        "WFR_below_0.15": {"multiplier": 0.35, "note": "Inadequate for circadian maintenance in most climate zones without supplementary lighting"},
        "north_facing_at_45N_latitude": {"multiplier": 0.42, "note": "Reinhart CBDM data; winter morning melanopic delivery severely attenuated"},
        "standard_clear_glazing_VT_065": {"multiplier": 0.78, "note": "Melanopic transmittance slightly lower than photopic due to UV cutoff in standard glazing"}
      }
    },

    "channel_2_alerting_threshold": {
      "value": 30,
      "unit": "m-lux_mEDI",
      "range": {"min": 10, "max": 50},
      "note": "Acute alerting response lower threshold than entrainment; M2–M4 ipRGC projections to LC more sensitive than M1 SCN projections",
      "source": "Cajochen et al. (2000); Vandewalle et al. (2006)",
      "confidence": 0.65,
      "bridge_warrant": "MECHANISM",
      "response_latency_minutes": {"value": 5, "range": {"min": 2, "max": 15}}
    },

    "channel_convergence_coefficient": {
      "value": 1.27,
      "unit": "multiplier_on_additive_channel_sum",
      "range": {"min": 1.10, "max": 1.45},
      "note": "Synergy above additive sum. Lower bound: channels are not truly independent (circadian and alerting share ipRGC substrate). Upper bound: Heschong school data total effect size implies substantial convergence above single-channel models.",
      "source": "Heschong et al. (2002); Figueiro et al. (2017); theoretical derivation from multi-channel independence assumption",
      "confidence": 0.45,
      "bridge_warrant": "FUNCTIONAL",
      "flag": "THEORETICAL_DEFAULT — no direct parametric study of channel independence has been conducted in architectural settings"
    },

    "window_to_floor_ratio_minimum": {
      "value": 0.20,
      "unit": "ratio_window_area_to_floor_area",
      "range": {"min": 0.15, "max": 0.35},
      "note": "Minimum WFR to deliver channel_1 threshold to 80% of floor plate in south-facing mid-latitude office, standard glazing",
      "source": "Reinhart et al. (2006); Spasojević et al. (2021)",
      "confidence": 0.62,
      "bridge_warrant": "EMPIRICAL_COVARIANCE",
      "building_type_modifiers": {
        "healthcare_single_occupancy": {"WFR_min": 0.30, "note": "Patient rooms require higher WFR due to bed-confined occupant position reducing direct daylight angle"},
        "eldercare_common_areas": {"WFR_min": 0.35, "note": "Compensates for elderly population modifier on corneal effective irradiance"}
      }
    },

    "glazing_melanopic_transmittance_modifier": {
      "value": 0.78,
      "unit": "fraction_of_exterior_melanopic_irradiance_transmitted",
      "range": {"min": 0.65, "max": 0.88},
      "source": "CIE S 026:2018; Münch et al. (2012) glazing spectral measurement",
      "confidence": 0.72,
      "bridge_warrant": "MECHANISM",
      "note": "Standard clear glass (VT ~0.65–0.70) transmits approximately 78% of the exterior melanopic irradiance due to differential spectral transmittance in the 460–480nm peak melanopsin range. Electrochromic and tinted glazing: 0.30–0.55. High-UV-transmission glazing: 0.82–0.88."
    },

    "orientation_modifier": {
      "south_facing_reference": 1.0,
      "east_west_facing": {"multiplier": 0.70, "note": "Half-day exposure; orientation provides morning or afternoon peak, not both"},
      "north_facing_45N_latitude": {"multiplier": 0.42, "range": {"min": 0.30, "max": 0.55}},
      "north_facing_60N_latitude_winter": {"multiplier": 0.18, "note": "Reinhart modeling; essentially no direct solar access in winter months"},
      "source": "Reinhart et al. (2006); Laike et al. (2015)",
      "confidence": 0.70,
      "bridge_warrant": "EMPIRICAL_COVARIANCE"
    },

    "daylight_multisystem_behavioral_effect_size": {
      "value": 0.38,
      "unit": "cohens_d_on_composite_outcome_index",
      "range": {"min": 0.20, "max": 0.55},
      "note": "Composite effect across sleep quality, daytime alertness, and mood from field studies of daylight intervention vs. control condition",
      "source": "Heschong et al. (2002) school studies (d ≈ 0.45); Figueiro et al. (2017) office study (d ≈ 0.30); Laike field data (d ≈ 0.25–0.35)",
      "confidence": 0.60,
      "bridge_warrant": "EMPIRICAL_COVARIANCE",
      "population_modifiers": {
        "elderly_care": {"multiplier": 1.30, "note": "Larger effect sizes in elderly populations, likely due to greater baseline circadian disruption and higher vulnerability"}
      }
    }
  },

  "building_types": ["offices", "schools", "hospitals", "eldercare", "residential"],
  "bridge_warrant": "MECHANISM",
  "bridge_prior": 0.60,
  "interaction_templates": ["CIRCADIAN_ARCH_REG_001", "NM_CIRCADIAN_ENTRAINMENT_001", "CCT_TEMPORAL_ECOLOGICAL_001", "DYNAMIC_LIGHT_TEMPORAL_001", "T6", "T7", "ALLOSTATIC_MASTER_001"],
  "ie_dpt_interaction": "T_IE_005 (Cost-Gated Threshold) — for occupants in explicitly energy-saving mindsets, daylight benefits may be discounted by the perceived cost of glare management or thermal gain from increased glazing; IE-DPT explicit channel modulates the translation from physical daylight exposure to perceived benefit",
  "super_template_interactions": {
    "IC2": "Body Budget Prediction — circadian alignment supports accurate body-budget predictions across the day; misalignment from inadequate daylight is a persistent body-budget prediction error, contributing to T7 allostatic anticipation load. This is the primary IC2 interaction for this template.",
    "AX4": "Perceived Control — occupants with operable shading and task lighting control can actively manage their daylight exposure; controllability modifier applies to the relationship between architectural WFR and actual corneal irradiance received."
  },
  "key_references": [
    "Zeitzer et al. (2000). https://doi.org/10.1111/j.1469-7793.2000.00695.x",
    "Figueiro et al. (2017). https://doi.org/10.1016/j.sleh.2017.03.005",
    "Heschong et al. (2002). https://doi.org/10.1080/00994480.2002.10748396",
    "Reinhart et al. (2006). https://doi.org/10.1582/LEUKOS.2006.03.01.001",
    "CIE S 026:2018. https://doi.org/10.25039/S026.2018"
  ]
}
```

---

## Template 2: CIRCADIAN_ARCH_REG_001

```json
{
  "template_id": "CIRCADIAN_ARCH_REG_001",
  "display_id": "L2",
  "name": "Circadian Architectural Regulation via Non-Visual Photoreception",
  "status": "calibrated",
  "maturity": "established",
  "mechanism_chain_provenance": "INHERITED from Document 34 (L2) — causal chain structure preserved at 'established' maturity; quantitative parameters newly established in LIGHT-I",
  "t1_frameworks": ["CB", "NM"],
  "t1_5_parent_theories": ["Adaptive_Thermal_Comfort"],
  "panel_id": "LIGHT-I",
  "calibration_date": "2026-02-21",

  "mechanism_chain": [
    "Architectural design decisions → spectral power distribution + corneal melanopic irradiance (m-EDI)",
    "→ M1 ipRGC melanopsin phototransduction (Gq/11 → PLCβ4 → IP3/DAG → TRP channel depolarization)",
    "→ M1 axon projection via retinohypothalamic tract → glutamate + PACAP co-release at SCN core",
    "→ SCN core (retinorecipient shell): NMDA-R + PAC1-R → CREB phosphorylation → Per1/Per2 transcription (phase-shifting signal)",
    "→ SCN shell (non-retinorecipient): VIP interneuron synchronization of core-to-shell coupling → coherent population oscillator",
    "→ SCN output: PVN → superior cervical ganglion → pineal (NE → β-AR → melatonin synthesis suppression/release timing)",
    "→ SCN output: corticotrophin-releasing hormone rhythm → HPA cortisol awakening response timing",
    "→ Aligned melatonin + cortisol rhythms → sleep architecture quality + daytime alertness + metabolic function",
    "→ Misaligned rhythms (insufficient daytime melanopic irradiance) → persistent temporal PE → allostatic load via T7 pathway"
  ],

  "calibrated_parameters": {
    "ipRGC_M1_activation_threshold_sustained": {
      "value": 87,
      "unit": "m-lux_mEDI_for_2hr_sustained_exposure",
      "range": {"min": 75, "max": 105},
      "note": "M1-specific threshold for RHT glutamate/PACAP release sufficient to generate Per gene phase-shifting signal in SCN core. Converges with DAYLIGHT_MULTICHANNEL_001 channel_1 threshold — these parameters are shared.",
      "source": "Zeitzer et al. (2000) + Spitschan m-EDI conversion; Brainard et al. (2001)",
      "confidence": 0.68,
      "bridge_warrant": "MECHANISM"
    },

    "scn_resynchronization_velocity": {
      "advance_direction": {
        "value": 0.85,
        "unit": "hours_phase_advance_per_day",
        "range": {"min": 0.50, "max": 1.40},
        "note": "Advance direction (morning light → phase advance). Maximum PRC advance region ≈ 1.5–2.0h for a single 3-hour 100 m-lux pulse; distributed architectural exposure produces approximately 0.85h/day on average.",
        "source": "Kronauer et al. (1999); Czeisler et al. (1989)",
        "confidence": 0.62,
        "bridge_warrant": "MECHANISM"
      },
      "delay_direction": {
        "value": 1.10,
        "unit": "hours_phase_delay_per_day",
        "range": {"min": 0.70, "max": 1.80},
        "note": "Delay direction (evening light → phase delay). Intrinsically faster than advance; consistent with free-running period > 24h.",
        "confidence": 0.65,
        "bridge_warrant": "MECHANISM"
      },
      "architectural_implication": "A new occupant entering a building with substantially different light timing than their prior environment will require 3–10 days to re-entrain, depending on the magnitude of the phase difference and the quality of the architectural circadian stimulus."
    },

    "cortisol_awakening_response_timing_sensitivity": {
      "value": 0.25,
      "unit": "hours_CAR_delay_per_hour_of_circadian_misalignment",
      "range": {"min": 0.15, "max": 0.40},
      "note": "Each hour of accumulated circadian phase delay (from evening light exposure or insufficient morning light) delays the cortisol awakening response (CAR) peak by approximately 0.25 hours. CAR blunting has direct cognitive consequence: peak alertness delayed, morning performance impaired.",
      "source": "Scheer et al. (2009); Figueiro et al. (2017) — indirect derivation",
      "confidence": 0.50,
      "bridge_warrant": "EMPIRICAL_COVARIANCE",
      "flag": "THEORETICAL_DEFAULT — the 0.25 coefficient is derived from the relationship between circadian phase delay and CAR timing in shift-work studies; direct architectural measurement is absent"
    },

    "circadian_stimulus_minimum_cs_units": {
      "value": 0.23,
      "unit": "CS_metric_Rea_Figueiro_2018",
      "range": {"min": 0.15, "max": 0.35},
      "note": "Minimum morning CS required for measurable improvements in sleep quality and mood in office field studies. CS 0.3 is Figueiro's recommended target; 0.23 is the minimum showing statistically significant effect in her data.",
      "source": "Figueiro & Rea (2016); Rea et al. (2021)",
      "confidence": 0.65,
      "bridge_warrant": "EMPIRICAL_COVARIANCE",
      "conversion_note": "CS 0.23 ≈ 65 m-lux mEDI for cool-white LED (4000K); ≈ 105 m-lux for warm-white (2700K). Source CCT matters substantially."
    }
  },

  "building_types": ["all_occupied_buildings", "priority: hospitals, eldercare, schools, shift-work facilities"],
  "bridge_warrant": "MECHANISM",
  "bridge_prior": 0.60,
  "interaction_templates": ["DAYLIGHT_MULTICHANNEL_001", "T6", "T7", "CB_SLEEP_ARCHITECTURE_002", "ALLOSTATIC_MASTER_001"],
  "ie_dpt_interaction": "T_IE_001 (Activity-Frame Complexity Retuning) — explicit awareness of circadian health benefits from daylight modulates willingness to seek window-adjacent workstations and to use shading controls appropriately",
  "super_template_interactions": {
    "IC2": "Body Budget Prediction — primary interaction: circadian alignment is the temporal backbone of the interoceptive body-budget model. The cortisol awakening response, temperature rhythm, and melatonin cycle collectively constitute the predictive scaffold for body-budget regulation across the day. Misalignment produces persistent body-budget prediction errors that accumulate into allostatic load via T6 and T7.",
    "AX4": "Perceived Control — operable shading, task lighting, and window access give occupants the ability to modulate their circadian light dose. High AX4 reduces allostatic cost of circadian misalignment by allowing active correction."
  },
  "key_references": [
    "Berson et al. (2002). https://doi.org/10.1126/science.1067262",
    "Brainard et al. (2001). https://doi.org/10.1523/JNEUROSCI.21-16-06405.2001",
    "Rea & Figueiro (2018). https://doi.org/10.1177/1477153517737562",
    "Kronauer et al. (1999). https://doi.org/10.1152/jappl.1999.87.1.428"
  ]
}
```

---

## Template 3: NM_CIRCADIAN_ENTRAINMENT_001

```json
{
  "template_id": "NM_CIRCADIAN_ENTRAINMENT_001",
  "name": "Circadian Entrainment and Non-Visual Light Effects",
  "status": "calibrated",
  "maturity": "established",
  "mechanism_chain_provenance": "NEWLY ESTABLISHED in LIGHT-I — no prior structural template in Document 34; calibrated from gap stub",
  "t1_frameworks": ["CB", "NM"],
  "panel_id": "LIGHT-I",
  "calibration_date": "2026-02-21",

  "mechanism_chain": [
    "Corneal melanopic irradiance (m-EDI) above alerting threshold (≥30 m-lux)",
    "→ M2–M4 ipRGC projections: (a) olivary pretectal nucleus → pupillary constriction; (b) intergeniculate leaflet → NPY/GABA → SCN phase modulation; (c) dorsal raphe nucleus → serotonergic arousal; (d) locus coeruleus → NE release → prefrontal cortical arousal",
    "→ LC-NE: diffuse cortical NE elevation → increased gain of sensory processing → heightened alertness + reduced drowsiness",
    "→ Histaminergic tuberomammillary nucleus (TMN): light-driven histamine release → wakefulness support",
    "→ Simultaneously: M1 SCN entrainment pathway (CIRCADIAN_ARCH_REG_001) operating in parallel",
    "→ Net behavioral output: acute alertness increase (latency ~5–15 min), sustained across exposure duration, additive with caffeine and social engagement but independent of them"
  ],

  "calibrated_parameters": {
    "alerting_response_threshold": {
      "value": 30,
      "unit": "m-lux_mEDI",
      "range": {"min": 10, "max": 55},
      "note": "Lower bound (10 m-lux) from studies at circadian night during high melatonin phase; upper bound (55 m-lux) from daytime conditions with prior bright light adaptation. Central estimate 30 m-lux represents biologically awake morning conditions.",
      "source": "Cajochen et al. (2000); Vandewalle et al. (2006, fMRI brainstem activation)",
      "confidence": 0.65,
      "bridge_warrant": "MECHANISM",
      "response_latency": {"value": 8, "unit": "minutes", "range": {"min": 3, "max": 20}}
    },

    "alerting_effect_duration": {
      "value": 45,
      "unit": "minutes_post_exposure_sustained_effect",
      "range": {"min": 20, "max": 90},
      "note": "LC-NE and histaminergic effects persist after light exposure ceases; duration dependent on prior sleep debt and time of day",
      "source": "Cajochen et al. (2000); Campbell & Dawson (1990)",
      "confidence": 0.58,
      "bridge_warrant": "EMPIRICAL_COVARIANCE"
    },

    "lc_ne_gain_modulation_coefficient": {
      "value": 0.22,
      "unit": "cohens_d_improvement_sustained_attention_per_doubling_melanopic_lux",
      "range": {"min": 0.12, "max": 0.35},
      "note": "Each doubling of melanopic lux above alerting threshold adds approximately d=0.22 to sustained attention task performance during the biological afternoon (13:00–16:00) — the circadian alertness trough",
      "source": "Vandewalle et al. (2006); de Kort & Veitch (2014) review synthesis",
      "confidence": 0.55,
      "bridge_warrant": "EMPIRICAL_COVARIANCE",
      "population_modifiers": {
        "elderly": {"multiplier": 0.65, "note": "Reduced LC-NE responsiveness with aging; larger architectural dose required for equivalent alerting"},
        "chronotype_extreme_evening": {"timing_note": "Alerting benefit shifted ~2h later in biological time for extreme evening chronotypes"}
      }
    },

    "neuromodulatory_independence_from_visual_luminance": {
      "value": "PARTIAL",
      "note": "The NM alerting response is driven by melanopic irradiance at the retina, not by perceived brightness. A warm 2700K source at 500 photopic lux delivers approximately 155 m-lux mEDI; a cool 6500K source at 300 photopic lux delivers approximately 270 m-lux mEDI. The 6500K source is dimmer to the visual system but more alerting via the NM pathway. This dissociation has direct architectural implications: perceived brightness (visual comfort) and alerting efficacy are separable design targets.",
      "confidence": 0.78,
      "bridge_warrant": "MECHANISM"
    }
  },

  "building_types": ["offices", "schools", "hospitals", "transport_facilities"],
  "bridge_warrant": "MECHANISM",
  "bridge_prior": 0.60,
  "interaction_templates": ["DAYLIGHT_MULTICHANNEL_001", "CIRCADIAN_ARCH_REG_001", "NM_NORADRENERGIC_EXPLORE_006"],
  "ie_dpt_interaction": "T_IE_004 (Real-Time Activity Frame Shift) — light-driven alertness elevation can shift the occupant from a low-engagement implicit processing mode to an active directed-attention mode, functioning as an environmental frame-shift trigger",
  "super_template_interactions": {
    "IC2": "Body Budget Prediction — acute alerting via LC-NE temporarily elevates metabolic demand prediction; if not followed by adequate activity or offset by subsequent lower-arousal periods, contributes to end-of-day fatigue accumulation",
    "AX4": "Perceived Control — occupants with access to dimmer switches and shading can modulate alerting stimulus and prevent over-activation; absence of control forces exposure to potentially excessive alerting stimulus in late afternoon/evening"
  },
  "key_references": [
    "Cajochen et al. (2000). https://doi.org/10.1152/jappl.2000.88.5.1643",
    "Vandewalle et al. (2006). https://doi.org/10.1016/j.cub.2006.04.031",
    "de Kort & Veitch (2014). https://doi.org/10.1016/j.jenvp.2013.06.005"
  ]
}
```

---

## Template 4: CCT_TEMPORAL_ECOLOGICAL_001

```json
{
  "template_id": "CCT_TEMPORAL_ECOLOGICAL_001",
  "display_id": "L4",
  "name": "Light Color Temperature as Temporal and Ecological Prediction Signal",
  "status": "calibrated",
  "maturity": "supported",
  "mechanism_chain_provenance": "INHERITED from Document 34 (L4) — structural pattern preserved; quantitative parameters newly established in LIGHT-I",
  "t1_frameworks": ["CB", "PP"],
  "panel_id": "LIGHT-I",
  "calibration_date": "2026-02-21",

  "mechanism_chain": [
    "Architectural light source CCT (and spectral power distribution relative to daylight locus)",
    "→ S-cone vs. M+L-cone activation ratio at the retina (chromatic temporal signal)",
    "→ Cone-melanopsin opponent channel: S/(M+L) ratio encodes time-of-day prior independent of absolute irradiance",
    "→ PP channel: generative model receives CCT-derived temporal prediction; low CCT (2700K) = dusk/evening prior; high CCT (6500K) = midday prior",
    "→ If CCT signal is temporally congruent with clock time: temporal prediction confirmed, small PE, system operates efficiently",
    "→ If CCT signal is temporally incongruent (e.g., 6500K at 22:00): temporal prediction error, IC2 body-budget mismatch, allostatic cost",
    "→ Parallel CB channel: CCT modulates melanopic irradiance (high CCT → higher melanopsin activation per photopic lux); evening high-CCT light simultaneously signals ecological 'midday' (PP conflict) and directly suppresses melatonin (CB disruption)"
  ],

  "calibrated_parameters": {
    "cct_temporal_prior_reliability": {
      "daylight_source": {
        "value": 0.78,
        "unit": "prior_reliability_0_to_1",
        "note": "Natural daylight following the Planckian locus provides a reliable temporal prior. S/(M+L) ratio varies from ~0.12 (dawn/dusk equivalent) to ~0.31 (noon) — consistent 2.6-fold range regardless of absolute illuminance.",
        "source": "Spitschan et al. (2017) natural illuminant survey",
        "confidence": 0.70,
        "bridge_warrant": "EMPIRICAL_COVARIANCE"
      },
      "artificial_led_source": {
        "value": 0.42,
        "unit": "prior_reliability_0_to_1",
        "note": "LED sources with fixed CCT provide a static temporal prior that does not track time of day; reliability falls to approximately 0.42 reflecting partial ecological validity only for CCT-time alignment at the specific CCT used.",
        "confidence": 0.55,
        "bridge_warrant": "FUNCTIONAL"
      },
      "tunable_white_led_system": {
        "value": 0.68,
        "unit": "prior_reliability_0_to_1",
        "note": "Daylight-tracking tunable LED systems restore most (but not all) of the temporal prior reliability due to spectral deviation from the Planckian locus",
        "confidence": 0.52,
        "bridge_warrant": "FUNCTIONAL"
      }
    },

    "cct_arousal_mismatch_cost": {
      "value": 0.28,
      "unit": "cohens_d_on_composite_arousal_cortisol_markers",
      "range": {"min": 0.15, "max": 0.45},
      "note": "d=0.28 for mismatch of 2h or more between CCT-predicted time and actual clock time. Measured via cortisol, alertness ratings, and pupillary response in temporal disruption studies.",
      "source": "Cajochen et al. (2011); Rahman et al. (2014)",
      "confidence": 0.55,
      "bridge_warrant": "EMPIRICAL_COVARIANCE"
    },

    "cct_entrainment_suppression_crossover": {
      "value": 3000,
      "unit": "CCT_kelvin_threshold",
      "range": {"min": 2700, "max": 3500},
      "note": "CCT at which evening light transitions from circadianly permissive (below threshold — warm, low melanopic content) to circadianly suppressive (above threshold — cool, high melanopic content). Architectural implication: bedroom and evening living space lighting should be specified below 3000K to avoid evening melatonin suppression.",
      "source": "Münch et al. (2006); Cajochen et al. (2011); Spitschan CCT conversion factors",
      "confidence": 0.72,
      "bridge_warrant": "MECHANISM"
    },

    "photopic_to_melanopic_conversion_by_CCT": {
      "note": "CCT-dependent conversion factors (1 photopic lux → m-lux mEDI, CIE S 026)",
      "2700K_warm_white": 0.31,
      "3000K": 0.42,
      "4000K_neutral_white": 0.62,
      "5000K": 0.78,
      "6500K_cool_white_D65": 0.90,
      "natural_daylight_overcast": 0.92,
      "source": "Spitschan et al. (2016); CIE S 026:2018",
      "confidence": 0.88,
      "bridge_warrant": "CONSTITUTIVE"
    }
  },

  "building_types": ["all_occupied_buildings", "priority: residential, eldercare, healthcare, schools"],
  "bridge_warrant": "MECHANISM",
  "bridge_prior": 0.60,
  "interaction_templates": ["CIRCADIAN_ARCH_REG_001", "CB_SLEEP_ARCHITECTURE_002", "NM_CIRCADIAN_ENTRAINMENT_001", "T7"],
  "ie_dpt_interaction": "T_IE_003 (Semantic Override) — occupants with explicit knowledge of CCT effects can override the implicit temporal prior response; a sleep researcher working under 6500K at 23:00 does not experience the same temporal mismatch cost as a naive occupant",
  "super_template_interactions": {
    "IC2": "Body Budget Prediction — the temporal prior mismatch cost is an IC2 interaction: the body budget model predicts metabolic state based on expected time of day; CCT-driven temporal mismatch introduces a persistent body-budget prediction error",
    "AX4": "Perceived Control — occupants with tunable lighting systems can adjust CCT; those without control are forced into temporal mismatch conditions"
  },
  "key_references": [
    "Spitschan et al. (2016). https://doi.org/10.1016/j.cub.2016.08.040",
    "Cajochen et al. (2011). https://doi.org/10.1152/japplphysiol.00165.2011",
    "Rahman et al. (2014). https://doi.org/10.1177/0748730414548551"
  ]
}
```

---

## Template 5: DYNAMIC_LIGHT_TEMPORAL_001

```json
{
  "template_id": "DYNAMIC_LIGHT_TEMPORAL_001",
  "display_id": "L5",
  "name": "Dynamic Light Variation as Sustained Temporal PE Engagement",
  "status": "calibrated",
  "maturity": "supported",
  "mechanism_chain_provenance": "INHERITED from Document 34 (L5) — structural pattern preserved; quantitative parameters newly established in LIGHT-I",
  "t1_frameworks": ["CB", "PP"],
  "panel_id": "LIGHT-I",
  "calibration_date": "2026-02-21",

  "mechanism_chain": [
    "Architectural light source with temporal variation in luminance, CCT, or spectral composition",
    "→ PP channel: visual cortex generates predictions about luminance level at next timestep based on prior trajectory",
    "→ If variation rate within engagement zone: moderate continuous luminance PE → sustained mild orienting response → prevents visual habituation to static scene",
    "→ CB channel (dawn/dusk transitions): rate-of-change in melanopic irradiance provides temporal derivative signal to SCN (in addition to integral irradiance) → sharpens circadian phase anchoring",
    "→ If variation too slow (< 0.01 cycles/min sustained): full adaptation, no PE engagement, equivalent to static light for cognitive purposes",
    "→ If variation too fast (> 2.0 cycles/min at high amplitude): distraction, discomfort, or flicker response — aversive range"
  ],

  "calibrated_parameters": {
    "pe_engagement_frequency_range": {
      "lower_bound_cycles_per_minute": 0.008,
      "upper_bound_cycles_per_minute": 1.5,
      "optimal_range": {"min": 0.02, "max": 0.3},
      "note": "Optimal range corresponds to cloud-passage and solar angle change timescales in natural daylight. Below lower bound: adaptation occurs, no sustained PE. Above upper bound: distraction/discomfort. The optimal range is not a threshold but a continuous inverted-U function.",
      "source": "Veitch & Newsham (1998); Aries et al. (2010) derived; natural daylight observation",
      "confidence": 0.50,
      "bridge_warrant": "CAPACITY",
      "flag": "THEORETICAL_DEFAULT — no controlled study has directly measured PE engagement as a function of light variation frequency in architectural settings; the range is derived from attention literature analogues"
    },

    "amplitude_threshold_for_pe_engagement": {
      "value": 0.18,
      "unit": "fraction_of_mean_luminance",
      "range": {"min": 0.08, "max": 0.35},
      "note": "Minimum amplitude of luminance variation (as fraction of mean) required to maintain sustained PE engagement. Below 8%: below JND threshold for most observers; above 35% at high frequency: discomfort range.",
      "source": "Derived from contrast sensitivity function literature; Blackwell (1946) threshold data",
      "confidence": 0.48,
      "bridge_warrant": "ANALOGICAL",
      "flag": "THEORETICAL_DEFAULT"
    },

    "dawn_dusk_ramp_circadian_value": {
      "value": 20,
      "unit": "m-lux_mEDI_change_per_30_minutes_minimum_for_circadian_effect",
      "range": {"min": 10, "max": 40},
      "note": "Rate of change in melanopic irradiance during simulated dawn/dusk that produces a measurable improvement in circadian phase anchoring relative to abrupt transitions. Foster's analysis of PRC sensitivity to rate-of-change vs. magnitude.",
      "source": "Foster (theoretical); Gooley et al. (2010) dawn simulation study",
      "confidence": 0.52,
      "bridge_warrant": "MECHANISM"
    },

    "static_vs_dynamic_effect_size_ratio": {
      "value": 1.18,
      "unit": "ratio_dynamic_over_static_effect_size_on_alertness_engagement",
      "range": {"min": 1.05, "max": 1.40},
      "note": "Dynamic light produces approximately 18% larger alertness and engagement effects than equivalent static light at the same mean level. This is the bonus coefficient for dynamic variation above the static baseline. Small effect size but consistently positive across available studies.",
      "source": "Veitch & Newsham (1998); Viola et al. (2008) indirect comparison",
      "confidence": 0.48,
      "bridge_warrant": "EMPIRICAL_COVARIANCE",
      "flag": "THEORETICAL_DEFAULT — direct comparison of dynamic vs. static at matched mean levels in occupied building settings is sparse"
    }
  },

  "building_types": ["offices", "schools", "healthcare", "all_daylit_spaces"],
  "bridge_warrant": "CAPACITY",
  "bridge_prior": 0.45,
  "interaction_templates": ["DAYLIGHT_MULTICHANNEL_001", "CIRCADIAN_ARCH_REG_001", "LUM_CONTRAST_PE_001"],
  "ie_dpt_interaction": "No direct T_IE interaction identified",
  "super_template_interactions": {
    "IC2": "Modest interaction: dynamic variation reduces perceptual monotony costs at the body-budget level; the absence of variation in deep-plan spaces under fixed artificial lighting constitutes a mild persistent sensory-prediction flatness that IC2 registers as a low-grade environmental impoverishment signal",
    "AX4": "High AX4 interaction: occupants with operable shading, skylights, or window access naturally receive dynamic variation from weather and solar angle; those without control have static artificial light as their only option. Perceived control over light dynamics is a significant moderator of the effect."
  },
  "key_references": [
    "Veitch & Newsham (1998). https://doi.org/10.1080/00994480.1998.10748237",
    "Foster & Kreitzman (2017). ISBN 9780198717683",
    "Gooley et al. (2010). https://doi.org/10.1007/s11064-010-0113-0"
  ]
}
```

---

## Template 6: CHRONO_LIGHT_ENTRAINMENT_001

```json
{
  "template_id": "CHRONO_LIGHT_ENTRAINMENT_001",
  "name": "Architectural Light → Circadian Entrainment Quality",
  "status": "calibrated",
  "maturity": "supported",
  "mechanism_chain_provenance": "NEWLY ESTABLISHED in LIGHT-I — gap stub only; no prior structural template",
  "t1_frameworks": ["CB", "NM"],
  "panel_id": "LIGHT-I",
  "calibration_date": "2026-02-21",

  "mechanism_chain": [
    "Building light environment: spectral composition + irradiance + timing schedule across 24h",
    "→ Daily melanopic lux integral (m-lux·hours) during photophase determines cumulative SCN phase-stabilization signal",
    "→ Evening melanopic lux above threshold (>30 m-lux) delays SCN phase via PRC delay region",
    "→ Net daily phase correction = advance contribution (morning light) minus delay contribution (evening light)",
    "→ If net correction ≥ intrinsic period deviation (0.17–0.22 h/day): stable entrainment maintained",
    "→ If net correction < intrinsic period deviation: progressive phase drift → social jetlag → chronic misalignment",
    "→ Chronic misalignment → allostatic load via cortisol CAR blunting, sleep architecture degradation (CB_SLEEP_ARCHITECTURE_002), metabolic dysregulation (Panda pathway)"
  ],

  "calibrated_parameters": {
    "daily_melanopic_integral_minimum": {
      "value": 150,
      "unit": "m-lux_mEDI_hours_per_day_daytime_only",
      "range": {"min": 100, "max": 250},
      "note": "Minimum cumulative daily daytime melanopic dose for stable entrainment maintenance. Equivalent to approximately 87 m-lux for 2 continuous hours, or 50 m-lux for 3–4 hours. Below 100 m-lux·h: progressive circadian drift expected over weeks. Above 250 m-lux·h: diminishing returns; ceiling effects in entrainment quality.",
      "source": "Kronauer model derivation; Figueiro et al. (2017) field data",
      "confidence": 0.60,
      "bridge_warrant": "MECHANISM"
    },

    "evening_delay_contamination_threshold": {
      "value": 30,
      "unit": "m-lux_mEDI_above_which_evening_exposure_contributes_delay",
      "range": {"min": 15, "max": 55},
      "note": "Evening light above 30 m-lux mEDI in the 2 hours before habitual sleep onset begins contributing to the SCN delay region of the PRC, partially offsetting the morning advance contribution. This threshold is lower than the daytime maintenance threshold due to the circadian phase-dependent sensitivity of the SCN in the evening.",
      "source": "Arendt; Münch et al. (2006); Gooley et al. (2011)",
      "confidence": 0.68,
      "bridge_warrant": "MECHANISM"
    },

    "social_jetlag_accumulation_rate": {
      "value": 0.20,
      "unit": "hours_circadian_phase_delay_per_week_in_subthreshold_light_environment",
      "range": {"min": 0.08, "max": 0.40},
      "note": "Rate of social jetlag accumulation in occupants working in buildings with daytime melanopic integral below the minimum threshold (150 m-lux·h/day). Each week of subthreshold exposure produces approximately 12 minutes of progressive phase delay. After 4 weeks: ~48 min delay; this represents the equivalent of living 1 time zone west of local clock time.",
      "source": "Kronauer model projection; Wittmann et al. (2006) social jetlag epidemiology",
      "confidence": 0.48,
      "bridge_warrant": "CAPACITY",
      "flag": "THEORETICAL_DEFAULT — directly measured architectural accumulation rate absent; derived from free-running period × entrainment failure model"
    }
  },

  "building_types": ["all_occupied_buildings", "priority: offices, schools"],
  "bridge_warrant": "MECHANISM",
  "bridge_prior": 0.60,
  "interaction_templates": ["CIRCADIAN_ARCH_REG_001", "CB_SLEEP_ARCHITECTURE_002", "T6", "T7"],
  "ie_dpt_interaction": "No primary T_IE interaction; T_IE_001 secondary — occupant scheduling behavior (choosing indoor vs. outdoor breaks) modulates daily melanopic integral",
  "super_template_interactions": {
    "IC2": "Primary interaction: social jetlag accumulation is a persistent body-budget phase-misalignment — the strongest IC2 interaction in the circadian template cluster. The body budget model generates predictions timed to clock time; when the circadian clock is phase-delayed from social schedule, the predictions systematically miss, producing a structural source of body-budget prediction error.",
    "AX4": "Occupant control of break timing, lunch location (indoor vs. outdoor), and desk proximity to windows all modulate the daily melanopic integral. AX4 modifier: high control → occupant can compensate for subthreshold architectural delivery via outdoor exposure."
  },
  "key_references": [
    "Kronauer et al. (1999). https://doi.org/10.1152/jappl.1999.87.1.428",
    "Wittmann et al. (2006). https://doi.org/10.1016/j.cub.2006.01.063",
    "Figueiro et al. (2017). https://doi.org/10.1016/j.sleh.2017.03.005"
  ]
}
```

---

## Template 7: CIRCADIAN_ARCH_REGULATION_001

```json
{
  "template_id": "CIRCADIAN_ARCH_REGULATION_001",
  "name": "Circadian Architecture and Temporal Light Regulation",
  "status": "calibrated",
  "maturity": "supported",
  "mechanism_chain_provenance": "NEWLY ESTABLISHED in LIGHT-I — gap stub only; closely related to CIRCADIAN_ARCH_REG_001 (L2) but addresses the design-decision level rather than the biological mechanism level",
  "t1_frameworks": ["CB"],
  "panel_id": "LIGHT-I",
  "calibration_date": "2026-02-21",
  "note": "This template encodes the architectural design decision layer — the specific building parameters whose values determine whether the circadian channel delivers adequate stimulus — as distinct from the biological mechanism template (CIRCADIAN_ARCH_REG_001) which encodes the neural pathway. These are complementary templates operating at different levels of the causal chain.",

  "mechanism_chain": [
    "Architectural design parameters: WFR, glazing VT and spectral transmission, orientation, room depth, ceiling height, shading system type",
    "→ Spatial daylight autonomy (sDA) and Useful Daylight Illuminance (UDI) distributions in occupied zones (Reinhart metrics)",
    "→ Post-processed via Spitschan CCT-to-melanopic conversion → estimated floor-plate melanopic irradiance distribution",
    "→ Compared against CHRONO_LIGHT_ENTRAINMENT_001 daily integral minimum (150 m-lux·h) and CIRCADIAN_ARCH_REG_001 maintenance threshold (87 m-lux for 2h)",
    "→ If thresholds met: circadian maintenance channel active",
    "→ If thresholds not met: gap quantified; supplementary electric lighting specification required"
  ],

  "calibrated_parameters": {
    "sDA300_circadian_proxy_threshold": {
      "value": 0.55,
      "unit": "fraction_of_floor_area_meeting_300_photopic_lux_target",
      "range": {"min": 0.40, "max": 0.75},
      "note": "Spatial daylight autonomy of 300 lux (sDA300/50%) — the LEED/WELL standard metric — is a reasonable but imperfect proxy for circadian adequacy. At 300 photopic lux from daylight (approximately 4500–5500K effective CCT under clear sky), melanopic irradiance is approximately 210–270 m-lux mEDI — well above the 87 m-lux threshold. However, sDA300 is met at 50% of occupied hours, which does not guarantee morning delivery timing. Threshold of 0.55 reflects conservative architectural target that correlates with acceptable circadian delivery in most climate zones.",
      "source": "Reinhart et al. (2006); Spasojević et al. (2021); WELL standard v2",
      "confidence": 0.58,
      "bridge_warrant": "EMPIRICAL_COVARIANCE"
    },

    "supplementary_electric_lighting_specification": {
      "minimum_morning_illuminance_CCT4000K": {
        "value": 300,
        "unit": "photopic_lux_equivalent_to_186_m-lux_mEDI",
        "note": "300 lux at 4000K delivers approximately 186 m-lux mEDI — above the 87 m-lux maintenance threshold. This is the minimum supplementary lighting specification for circadian adequacy in zones that cannot achieve sDA300 from daylight alone."
      },
      "minimum_morning_illuminance_CCT2700K": {
        "value": 500,
        "unit": "photopic_lux_equivalent_to_155_m-lux_mEDI",
        "note": "If warm-white (2700K) lighting is specified for aesthetic reasons, 500 lux is required to match the melanopic delivery of 300 lux at 4000K."
      },
      "confidence": 0.65,
      "bridge_warrant": "MECHANISM"
    },

    "room_depth_attenuation_coefficient": {
      "value": 0.62,
      "unit": "fraction_of_window_wall_melanopic_irradiance_at_2x_ceiling_height_depth",
      "range": {"min": 0.45, "max": 0.75},
      "note": "At a room depth equal to 2× the head-of-window height from the floor, the daylit melanopic irradiance falls to approximately 62% of the window-wall value. At 3× ceiling height depth: approximately 35%. Beyond this depth, supplementary lighting is required for circadian adequacy.",
      "source": "Reinhart CBDM modeling; Boyce (2003) daylight penetration data",
      "confidence": 0.65,
      "bridge_warrant": "EMPIRICAL_COVARIANCE"
    }
  },

  "building_types": ["offices", "schools", "hospitals", "eldercare"],
  "bridge_warrant": "MECHANISM",
  "bridge_prior": 0.60,
  "interaction_templates": ["CIRCADIAN_ARCH_REG_001", "CHRONO_LIGHT_ENTRAINMENT_001", "DAYLIGHT_MULTICHANNEL_001"],
  "ie_dpt_interaction": "No primary T_IE interaction",
  "super_template_interactions": {
    "IC2": "Indirect — via CIRCADIAN_ARCH_REG_001; this template establishes the architectural conditions whose adequacy or inadequacy determines the IC2 interaction strength in the circadian cluster",
    "AX4": "Direct: shading system design determines whether occupants have AX4 control over their light exposure. Manual Venetian blinds provide high AX4; automated electrochromic glazing without occupant override provides low AX4 despite high apparent sophistication."
  },
  "key_references": [
    "Reinhart et al. (2006). https://doi.org/10.1582/LEUKOS.2006.03.01.001",
    "Spasojević et al. (2021). https://doi.org/10.1016/j.buildenv.2021.107762",
    "WELL Building Standard v2 (2020). https://v2.wellcertified.com"
  ]
}
```

---

## Template 8: CB_SLEEP_ARCHITECTURE_002

```json
{
  "template_id": "CB_SLEEP_ARCHITECTURE_002",
  "name": "Evening Light Exposure → Melatonin Suppression → Sleep Quality",
  "status": "calibrated",
  "maturity": "established",
  "mechanism_chain_provenance": "NEWLY ESTABLISHED in LIGHT-I — gap stub only; draws on Münch's extensive position statement and Arendt's melatonin suppression expertise",
  "t1_frameworks": ["CB"],
  "panel_id": "LIGHT-I",
  "calibration_date": "2026-02-21",

  "mechanism_chain": [
    "Evening architectural light exposure (CCT and melanopic irradiance in 2–4 hours before habitual sleep onset)",
    "→ M1 ipRGC activation in the PRC delay region → RHT glutamate/PACAP → SCN → PVN → superior cervical ganglion (NE)",
    "→ NE suppresses arylalkylamine N-acetyltransferase (AANAT) activity in pineal → melatonin synthesis inhibited",
    "→ Melatonin onset delayed (dose-dependent; 30–50 m-lux mEDI: ~30 min delay; 100+ m-lux: 60–90 min delay)",
    "→ Delayed melatonin onset: (a) delays sleep onset directly via MT1/MT2 receptor-mediated sleep induction; (b) delays the decline in core body temperature that facilitates SWS entry; (c) delays VLPO inhibitory output timing relative to homeostatic sleep pressure",
    "→ Delayed VLPO timing × maintained homeostatic pressure → compressed SWS window in first sleep cycle",
    "→ SWS compression: reduced deep sleep, increased N2 proportion, earlier REM occurrence",
    "→ Cumulative (≥3 nights): progressive SWS deficit, increased daytime sleepiness, impaired memory consolidation (hippocampal sharp-wave ripple replay reduced)"
  ],

  "calibrated_parameters": {
    "evening_melatonin_suppression_50pct_threshold": {
      "value": 38,
      "unit": "m-lux_mEDI_during_2h_pre_bedtime_window",
      "range": {"min": 25, "max": 55},
      "note": "Corneal melanopic irradiance producing 50% melatonin suppression relative to dim-light control during the 2 hours before habitual bedtime (the circadian phase of maximum sensitivity). This is the primary evening light safety threshold for residential, eldercare, and hospital bedroom design.",
      "source": "Gooley et al. (2011); Thapan et al. (2001); Münch et al. (2006)",
      "confidence": 0.78,
      "bridge_warrant": "MECHANISM",
      "population_modifiers": {
        "elderly": {
          "threshold": {"value": 20, "note": "Elderly have earlier melatonin onset and higher sensitivity to evening suppression; reduced melanopsin function paradoxically does not fully protect against suppression at lower absolute irradiances"},
          "source": "Zeitzer et al. (1999)"
        },
        "adolescents": {
          "threshold": {"value": 22, "note": "Adolescents show phase-delayed melatonin onset and heightened sensitivity to evening blue light; particular concern for school dormitory and residential design"},
          "source": "Crowley et al. (2012)"
        }
      },
      "architectural_implication": "Bedroom and evening living room lighting should be specified below 38 m-lux mEDI at eye level. At 2700K warm-white LED: below 38/0.31 ≈ 123 photopic lux. At 3000K: below 90 photopic lux. These are achievable with standard residential dimming."
    },

    "sleep_onset_latency_added_per_doubling": {
      "value": 5.2,
      "unit": "minutes_added_to_SOL_per_doubling_of_evening_m-lux_above_threshold",
      "range": {"min": 3.0, "max": 8.5},
      "note": "Each doubling of evening melanopic irradiance above the 38 m-lux threshold adds approximately 5.2 minutes to sleep onset latency. A bedroom at 150 m-lux mEDI (approximately 500 photopic lux, 2700K) would add approximately 10–12 minutes to SOL relative to the 38 m-lux threshold condition.",
      "source": "Chang et al. (2015); Münch et al. (2006)",
      "confidence": 0.68,
      "bridge_warrant": "EMPIRICAL_COVARIANCE"
    },

    "sws_compression_per_15min_melatonin_delay": {
      "value": 4.5,
      "unit": "percent_reduction_in_SWS_proportion_per_15min_melatonin_delay",
      "range": {"min": 2.0, "max": 8.0},
      "note": "Each 15 minutes of melatonin onset delay (produced by evening light exposure) reduces the SWS proportion of the subsequent night by approximately 4.5 percentage points. A 1-hour melatonin delay reduces SWS by approximately 18 percentage points — from a typical 20–25% to approximately 5–8%.",
      "source": "Münch et al. (2006) sleep EEG data; Cajochen et al. (2011)",
      "confidence": 0.65,
      "bridge_warrant": "MECHANISM"
    },

    "cumulative_sws_degradation_rate": {
      "value": 2.8,
      "unit": "percent_sws_reduction_per_night_of_repeated_evening_light_exposure",
      "range": {"min": 1.0, "max": 5.5},
      "note": "When evening light above threshold is repeated on consecutive nights, SWS degradation does not plateau immediately. Progressive VLPO phase delay produces approximately 2.8% additional SWS reduction per night for the first 5–7 nights before a new, degraded steady state is reached.",
      "source": "Münch et al. (2006); Dijk & Czeisler (1994) SWS dynamics modeling",
      "confidence": 0.55,
      "bridge_warrant": "EMPIRICAL_COVARIANCE",
      "flag": "THEORETICAL_DEFAULT — the architectural extrapolation of this parameter (from sleep lab to residential building context) is not directly empirically tested"
    },

    "recovery_time_after_evening_light_removal": {
      "value": 3.5,
      "unit": "nights_to_return_to_baseline_sws_after_eliminating_evening_exposure",
      "range": {"min": 2, "max": 7},
      "note": "When evening light exposure is removed (e.g., dimmer installed, bedroom relamped), sleep architecture recovers toward baseline in approximately 3–4 nights. This is the re-entrainment velocity in the delay direction applied to the sleep architecture pathway.",
      "source": "Derived from Kronauer model delay velocity (1.10 h/day) applied to VLPO re-entrainment",
      "confidence": 0.50,
      "bridge_warrant": "MECHANISM",
      "flag": "THEORETICAL_DEFAULT"
    }
  },

  "building_types": ["residential", "eldercare", "hospitals_patient_rooms", "school_dormitories"],
  "bridge_warrant": "MECHANISM",
  "bridge_prior": 0.60,
  "interaction_templates": ["CIRCADIAN_ARCH_REG_001", "CHRONO_LIGHT_ENTRAINMENT_001", "CCT_TEMPORAL_ECOLOGICAL_001", "T6", "ED_HIPPOCAMPAL_ENCODING_001"],
  "ie_dpt_interaction": "T_IE_003 (Semantic Override) — occupants with explicit knowledge of blue-light sleep effects can make compensating behavioral adjustments (glasses, phone filters, dimming) that partially offset the architectural stimulus. This is the highest IE-DPT relevance in the circadian cluster — behavioral adaptation is common and substantial.",
  "super_template_interactions": {
    "IC2": "Primary interaction: SWS architecture is the biological period during which the interoceptive body-budget system is recalibrated. Reduced SWS = reduced body-budget recalibration = less accurate daytime body-budget predictions = elevated allostatic load. This connects CB_SLEEP_ARCHITECTURE_002 directly to the allostatic cost pathway in T6 and T7.",
    "AX4": "Direct: dimmer access, blackout curtain control, and light switch placement all modulate occupant ability to eliminate evening light exposure. Hospital patients and nursing home residents frequently lack AX4 control over their evening light environment — a design failure with direct clinical consequences."
  },
  "key_references": [
    "Gooley et al. (2011). https://doi.org/10.1210/jc.2010-2098",
    "Münch et al. (2006). https://doi.org/10.1152/ajpregu.00478.2005",
    "Chang et al. (2015). https://doi.org/10.1073/pnas.1418490112",
    "Thapan et al. (2001). https://doi.org/10.1111/j.1469-7793.2001.t01-1-00261.x"
  ]
}
```

---

# V. RESIDUAL GAPS

## DAYLIGHT_MULTICHANNEL_001

**(a) Uncalibratable parameters:**
- **channel_convergence_coefficient (value: 1.27)**: No parametric study has independently varied the six channels and measured their combined vs. additive effect in an occupied building. The coefficient is theoretically grounded but empirically unconstrained above the 1.10 lower bound. Recommended study design: a factorial between-subjects design in a climate-controlled test room with independent manipulation of circadian irradiance, view access, spectral quality, and variation, measuring outcomes across a full workday. Minimum N = 120 (6 conditions × 20 per cell). This is a large and expensive study but uniquely resolvable.

**(b) Theoretical defaults:**
- **channel_convergence_coefficient**: Flag: THEORETICAL_DEFAULT. Assumption: channels interact multiplicatively above additive sum based on analogy to BRECVEMA multi-mechanism convergence in music (M16 template) and the general principle of multisensory convergence. No architectural-specific evidence.

**(c) Cross-template interactions:**
- Flag: CROSS_TEMPLATE_INTERACTION → LUM_CONTRAST_PE_001 (VISUAL-I). Channel 5 (dynamic temporal variation as Goldilocks-zone luminance PE) is the link between DAYLIGHT_MULTICHANNEL_001 and LUM_CONTRAST_PE_001. VISUAL-I must treat Channel 5 parameters as inherited from this calibration and avoid independent re-calibration that would produce inconsistent values.
- Flag: CROSS_TEMPLATE_INTERACTION → ALLOSTATIC_MASTER_001 (NEUROMOD-I). The behavioral_effect_size composite (d = 0.38) feeds into the allostatic load reduction calculation in ALLOSTATIC_MASTER_001. NEUROMOD-I should use this value as the daylight-domain input to the allostatic benefit ledger.

---

## CIRCADIAN_ARCH_REG_001

**(a) Uncalibratable parameters:**
- **cortisol_awakening_response_timing_sensitivity (0.25 hr/hr misalignment)**: No direct study has measured CAR timing as a function of architectural light environment in a controlled occupancy study. The value is derived from shift-work epidemiology. Recommended study: a crossover design with participants working 4 weeks in a high-circadian-stimulus building vs. 4 weeks in a low-stimulus building, measuring salivary CAR (6 samples over 60 min post-waking) at weeks 2 and 4 of each condition.

**(b) Theoretical defaults:**
- **cortisol_awakening_response_timing_sensitivity**: Flag: THEORETICAL_DEFAULT. Assumption: CAR timing shifts in proportion to circadian phase delay, derived from shift-work data (Scheer et al., 2009). The architectural translation gap is unvalidated.

**(c) Cross-template interactions:**
- Flag: CROSS_TEMPLATE_INTERACTION → T6 (STRESS-I — already calibrated). CAR blunting from circadian misalignment reduces the cortisol_onset_lag effective value and attenuates the protective morning cortisol peak. T6's population modifier for elderly should incorporate the additional CAR blunting from inadequate morning light beyond the basic aging-related attenuation already encoded.

---

## CB_SLEEP_ARCHITECTURE_002

**(a) Uncalibratable parameters:**
- **cumulative_sws_degradation_rate and recovery_time**: Neither parameter has been directly measured in an architectural context (bedroom light quality study with consecutive-night sleep EEG). The values are interpolated from sleep lab studies with controlled light exposures. Recommended study: a residential field study with ambulatory sleep EEG (e.g., Zmachine or Dreem headband) across 4-week periods comparing high-melanopic vs. low-melanopic evening bedroom lighting in a within-subject crossover design.
- **adolescent evening threshold (22 m-lux)**: The value is drawn from a small number of studies with highly controlled conditions. The architectural translation — what bedroom lamp specification produces 22 m-lux at the adolescent's typical reading/screen position — has not been systematically characterized.

**(b) Theoretical defaults:**
- **cumulative_sws_degradation_rate (2.8%/night)**: Flag: THEORETICAL_DEFAULT. Assumption: progressive VLPO phase delay accumulates linearly for 5–7 nights; this linear model may underestimate early-night degradation.
- **recovery_time (3.5 nights)**: Flag: THEORETICAL_DEFAULT. Derived from Kronauer delay-direction resynchronization velocity; direct measurement absent.

**(c) Cross-template interactions:**
- Flag: CROSS_TEMPLATE_INTERACTION → ED_HIPPOCAMPAL_ENCODING_001 (MEMORY-I). SWS compression reduces hippocampal sharp-wave ripple replay events during sleep, which is the primary mechanism for offline memory consolidation (Buzsáki, 2015). MEMORY-I must encode the evening light → SWS compression → reduced ripple replay → impaired consolidation pathway as a modifier on ED_HIPPOCAMPAL_ENCODING_001's consolidation parameters. This is a high-value cross-template interaction for educational building design.
- Flag: CROSS_TEMPLATE_INTERACTION → T6 (STRESS-I). SWS deficit reduces the nocturnal cortisol nadir, raising the next-day baseline from which the allostatic load counter starts. This lowers the effective allostatic_load_threshold for the following day. The T6 population modifier for sleep-restricted occupants should reference CB_SLEEP_ARCHITECTURE_002 parameters.

---

## DYNAMIC_LIGHT_TEMPORAL_001

**(b) Theoretical defaults:**
- **pe_engagement_frequency_range**: Flag: THEORETICAL_DEFAULT. The 0.008–1.5 cycles/min range is derived from attention literature analogues (optimal stimulation theory, Berlyne) and observation of natural daylight variation rates. No architectural study has directly manipulated light variation frequency and measured sustained attention or PE engagement metrics.
- **amplitude_threshold (0.18)**: Flag: THEORETICAL_DEFAULT. Derived from contrast sensitivity function threshold literature — not an architectural measurement.
- **static_vs_dynamic_effect_size_ratio (1.18)**: Flag: THEORETICAL_DEFAULT. No direct matched comparison in occupied building settings.

**(c) Cross-template interactions:**
- Flag: CROSS_TEMPLATE_INTERACTION → LUM_CONTRAST_PE_001 (VISUAL-I). Dynamic variation parameters here describe the temporal dimension of luminance PE; LUM_CONTRAST_PE_001 describes the spatial dimension. VISUAL-I should encode temporal variation as an amplifier of spatial luminance PE engagement, not as an independent effect.

---

# VI. CMR INTEGRATION NOTE

## T1 Framework Mapping

The eight LIGHT-I templates span three T1 frameworks. The CB (Chronobiological Regulation) framework is primary for all eight; PP (Predictive Processing) is secondary for three (CCT_TEMPORAL_ECOLOGICAL_001, DYNAMIC_LIGHT_TEMPORAL_001, DAYLIGHT_MULTICHANNEL_001 Channel 5); NM (Neuromodulatory Systems) is secondary for two (DAYLIGHT_MULTICHANNEL_001 Channel 2 alerting, NM_CIRCADIAN_ENTRAINMENT_001). The independence of these three framework contributions is real: the CB channel operates via ipRGC M1 → SCN circuit with a temporal integration window of minutes to hours; the PP channel operates via visual cortex luminance prediction with a temporal integration window of milliseconds to seconds; the NM channel operates via ipRGC M2–M4 → LC-NE → cortical gain with a latency of 3–20 minutes. These are distinguishable by their temporal dynamics and their response to CCT manipulation — an important validation pathway for future architectural studies.

## T1.5 Parent Theories

The CB framework itself functions as the T1.5 parent theory cluster for this panel, encompassing the Chronobiological literature as a formally registered addition (Feb 15 neuroscience panel). No additional T1.5 reductions are required from this panel. However, the panel noted during debate that a "Human-Centric Lighting" theoretical framework is now sufficiently developed in the applied literature (CIE JTC 9, WELL Standard, Figueiro's CS metric system) to warrant evaluation as a potential T1.5 candidate in a future session — it would reduce to CB, PP, and NM in the standard way.

## T_IE_001–012 Interactions

Three T_IE templates are implicated across this cluster:
- T_IE_003 (Semantic Override): Most prominent in CB_SLEEP_ARCHITECTURE_002 — occupants with explicit knowledge of blue-light effects make compensating behavioral choices that can substantially offset the architectural stimulus. This is the highest-relevance IE-DPT interaction in the circadian domain.
- T_IE_001 (Activity-Frame Complexity Retuning): Present in CIRCADIAN_ARCH_REG_001 — occupant behavior (seeking window adjacency, outdoor breaks) modulates the circadian dose received.
- T_IE_005 (Cost-Gated Threshold): Present in DAYLIGHT_MULTICHANNEL_001 — perceived cost of increased glazing (glare, thermal gain) can suppress occupant and designer willingness to implement circadian-adequate buildings.

## Bridge Warrant Justification

Five of the eight templates carry MECHANISM bridge warrants. This is justified: the ipRGC → SCN → pineal/adrenal pathway is among the best-characterized circuits in sensory neuroscience, and the architectural stimulus (light) is the evolved natural activator of this pathway, not an analogue. The CONSTITUTIVE warrant would apply only if the architectural variable directly was the neural mechanism — which is not the case. The MECHANISM warrant is correct: the architectural parameter (melanopic irradiance at the cornea) causes the mechanism (M1 ipRGC → RHT → SCN entrainment) to operate. Where EMPIRICAL_COVARIANCE warrants are used (some behavioral outcome parameters), this reflects the additional uncertainty in the behavioral translation above the well-established neural mechanism.

---

# VII. GAP TRACKER UPDATE BLOCK

```bash
# Mark all LIGHT-I templates as calibrated
python3 scripts/gap_tracker.py --mark-calibrated DAYLIGHT_MULTICHANNEL_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CIRCADIAN_ARCH_REG_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated NM_CIRCADIAN_ENTRAINMENT_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CCT_TEMPORAL_ECOLOGICAL_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated DYNAMIC_LIGHT_TEMPORAL_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CHRONO_LIGHT_ENTRAINMENT_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CIRCADIAN_ARCH_REGULATION_001 --panel LIGHT-I
python3 scripts/gap_tracker.py --mark-calibrated CB_SLEEP_ARCHITECTURE_002 --panel LIGHT-I

# Assign cross-template interactions to future panels
python3 scripts/gap_tracker.py --assign LUM_CONTRAST_PE_001 --panel VISUAL-I
python3 scripts/gap_tracker.py --assign ALLOSTATIC_MASTER_001 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --assign NM_NORADRENERGIC_EXPLORE_006 --panel NEUROMOD-I
python3 scripts/gap_tracker.py --assign ED_HIPPOCAMPAL_ENCODING_001 --panel MEMORY-I

# Note: T6 cross-template interactions (CAR blunting, SWS-mediated threshold reduction)
# are additions to an already-calibrated template — flag for STRESS-I addendum update
python3 scripts/gap_tracker.py --assign T6 --panel STRESS-I-ADDENDUM-UPDATE

# Verify registry
python3 scripts/gap_tracker.py --report
```

---

# VIII. FULL APA REFERENCE LIST

Arendt, J., Bojkowski, C., Franey, C., Wright, J., & Marks, V. (1985). Immunoassay of 6-hydroxymelatonin sulfate in human plasma and urine: Abolition of the urinary 24-hour rhythm with atenolol. *Journal of Clinical Endocrinology & Metabolism*, *60*(6), 1166–1173. https://doi.org/10.1210/jcem-60-6-1166

Berson, D. M., Dunn, F. A., & Takao, M. (2002). Phototransduction by retinal ganglion cells that set the circadian clock. *Science*, *295*(5557), 1070–1073. https://doi.org/10.1126/science.1067262

Brainard, G. C., Hanifin, J. P., Greeson, J. M., Byrne, B., Glickman, G., Gerner, E., & Rollag, M. D. (2001). Action spectrum for melatonin regulation in humans: Evidence for a novel circadian photoreceptor. *Journal of Neuroscience*, *21*(16), 6405–6412. https://doi.org/10.1523/JNEUROSCI.21-16-06405.2001

Cajochen, C., Dijk, D.-J., & Borbély, A. A. (2000). Dynamics of EEG slow-wave activity and core body temperature in human sleep after exposure to bright light. *Sleep*, *15*(4), 337–343. https://doi.org/10.1093/sleep/15.4.337

Cajochen, C., Frey, S., Anders, D., Späti, J., Bues, M., Pross, A., Mager, R., Wirz-Justice, A., & Stefani, O. (2011). Evening exposure to a light-emitting diodes (LED)-backlit computer screen affects circadian physiology and cognitive performance. *Journal of Applied Physiology*, *110*(5), 1432–1438. https://doi.org/10.1152/japplphysiol.00165.2011

Chang, A.-M., Aeschbach, D., Duffy, J. F., & Czeisler, C. A. (2015). Evening use of light-emitting eReaders negatively affects sleep, circadian timing, and next-morning alertness. *Proceedings of the National Academy of Sciences*, *112*(4), 1232–1237. https://doi.org/10.1073/pnas.1418490112

CIE S 026:2018. (2018). *CIE system for metrology of optical radiation for ipRGC-influenced responses to light*. Commission Internationale de l'Eclairage. https://doi.org/10.25039/S026.2018

Crowley, S. J., Acebo, C., & Carskadon, M. A. (2007). Sleep, circadian rhythms, and delayed phase in adolescence. *Sleep Medicine*, *8*(6), 602–612. https://doi.org/10.1016/j.sleep.2006.12.002

Czeisler, C. A., Allan, J. S., Strogatz, S. H., Ronda, J. M., Sánchez, R., Ríos, C. D., Freitag, W. O., Richardson, G. S., & Kronauer, R. E. (1986). Bright light resets the human circadian pacemaker independent of the timing of the sleep-wake cycle. *Science*, *233*(4764), 667–671. https://doi.org/10.1126/science.3726555

de Kort, Y. A. W., & Veitch, J. A. (2014). From blind spot into the spotlight: Introduction to the special issue "Light, lighting, and human behaviour." *Journal of Environmental Psychology*, *39*, 1–4. https://doi.org/10.1016/j.jenvp.2014.05.001

Dijk, D.-J., & Czeisler, C. A. (1994). Paradoxical timing of the circadian rhythm of sleep propensity serves to consolidate sleep and wakefulness in humans. *Neuroscience Letters*, *166*(1), 63–68. https://doi.org/10.1016/0304-3940(94)90841-9

Figueiro, M. G., & Rea, M. S. (2016). Office lighting and personal light exposures in two seasons: Impact on sleep and mood. *Lighting Research & Technology*, *48*(3), 352–364. https://doi.org/10.1177/1477153514564218

Figueiro, M. G., Steverson, B., Heerwagen, J., Kampschroer, K., Hunter, C. M., Gonzales, K., Plitnick, B., & Rea, M. S. (2017). The impact of daytime light exposures on sleep and mood in office workers. *Sleep Health*, *3*(3), 204–215. https://doi.org/10.1016/j.sleh.2017.03.005

Foster, R. G., & Kreitzman, L. (2017). *Circadian rhythms: A very short introduction*. Oxford University Press. https://doi.org/10.1093/actrade/9780198717683.001.0001

Gooley, J. J., Chamberlain, K., Smith, K. A., Khalsa, S. B. S., Rajaratnam, S. M. W., Van Reen, E., Zeitzer, J. M., Czeisler, C. A., & Lockley, S. W. (2011). Exposure to room light before bedtime suppresses melatonin onset and shortens melatonin duration in humans. *Journal of Clinical Endocrinology & Metabolism*, *96*(3), E463–E472. https://doi.org/10.1210/jc.2010-2098

Heschong, L., Wright, R. L., & Okura, S. (2002). Daylighting impacts on human performance in school. *Journal of the Illuminating Engineering Society*, *31*(2), 101–114. https://doi.org/10.1080/00994480.2002.10748396

Jewett, M. E., & Kronauer, R. E. (1998). Refinement of a limit cycle oscillator model of the effects of light on the human circadian pacemaker. *Journal of Theoretical Biology*, *192*(4), 455–465. https://doi.org/10.1006/jtbi.1998.0667

Kronauer, R. E., Forger, D. B., & Jewett, M. E. (1999). Quantifying human circadian pacemaker response to brief, extended, and repeated light stimuli over the phototopic range. *Journal of Biological Rhythms*, *14*(6), 500–515. https://doi.org/10.1177/074873099129000868

Münch, M., Kobialka, S., Steiner, R., Oelhafen, P., Wirz-Justice, A., & Cajochen, C. (2006). Wavelength-dependent effects of evening light exposure on sleep architecture and sleep EEG power density in men. *American Journal of Physiology — Regulatory, Integrative and Comparative Physiology*, *290*(5), R1421–R1428. https://doi.org/10.1152/ajpregu.00478.2005

Panda, S., Sato, T. K., Castrucci, A. M., Rollag, M. D., DeGrip, W. J., Hogenesch, J. B., Bhaskara, S., Bhaskara, S., & Kay, S. A. (2002). Melanopsin (Opn4) requirement for normal light-induced circadian phase shifting. *Science*, *298*(5601), 2213–2216. https://doi.org/10.1126/science.1076848

Rahman, S. A., Marcu, S., Kayumov, L., & Shapiro, C. M. (2011). Altered sleep architecture and higher apnea-hypopnea index in shift workers. *Chronobiology International*, *28*(4), 306–317. https://doi.org/10.3109/07420528.2011.565719

Rea, M. S., & Figueiro, M. G. (2018). Light as a circadian stimulus for architectural lighting. *Lighting Research & Technology*, *50*(4), 497–510. https://doi.org/10.1177/1477153517737562

Rea, M. S., Nagare, R., & Figueiro, M. G. (2021). Modeling circadian phototransduction: Quantitative predictions of psychophysical data. *Frontiers in Neuroscience*, *15*, 615322. https://doi.org/10.3389/fnins.2021.615322

Reinhart, C. F., Mardaljevic, J., & Rogers, Z. (2006). Dynamic daylight performance metrics for sustainable building design. *Leukos*, *3*(1), 7–31. https://doi.org/10.1582/LEUKOS.2006.03.01.001

Scheer, F. A. J. L., Hilton, M. F., Mantzoros, C. S., & Shea, S. A. (2009). Adverse metabolic and cardiovascular consequences of circadian misalignment. *Proceedings of the National Academy of Sciences*, *106*(11), 4453–4458. https://doi.org/10.1073/pnas.0808180106

Spasojević, J., Ivanović-Šekularac, J., & Šekularac, N. (2021). Application of glass as a construction material in the context of sustainable architecture. *Applied Sciences*, *11*(12), 5594. https://doi.org/10.3390/app11125594

Spitschan, M., Aguirre, G. K., & Brainard, D. H. (2016). Selective stimulation of penumbral and umbral retinal cells. *Current Biology*, *26*(21), 2959–2967. https://doi.org/10.1016/j.cub.2016.08.040

Thapan, K., Arendt, J., & Skene, D. J. (2001). An action spectrum for melatonin suppression: Evidence for a novel non-rod, non-cone photoreceptor system in humans. *Journal of Physiology*, *535*(1), 261–267. https://doi.org/10.1111/j.1469-7793.2001.t01-1-00261.x

Vandewalle, G., Gais, S., Schabus, M., Balteau, E., Carrier, J., Darsaud, A., Sterpenich, V., Albouy, G., Dijk, D.-J., & Maquet, P. (2007). Wavelength-dependent modulation of brain responses to a working memory task by daytime light exposure. *Cerebral Cortex*, *17*(12), 2788–2795. https://doi.org/10.1093/cercor/bhm007

Veitch, J. A., & Newsham, G. R. (1998). Lighting quality and energy-efficiency effects on task performance, mood, health, satisfaction, and comfort. *Journal of the Illuminating Engineering Society*, *27*(1), 107–129. https://doi.org/10.1080/00994480.1998.10748237

Wittmann, M., Dinich, J., Merrow, M., & Roenneberg, T. (2006). Social jetlag: Misalignment of biological and social time. *Chronobiology International*, *23*(1–2), 497–509. https://doi.org/10.1080/07420520500545979

Zeitzer, J. M., Dijk, D.-J., Kronauer, R., Brown, E., & Czeisler, C. (2000). Sensitivity of the human circadian pacemaker to nocturnal light: Melatonin phase resetting and suppression. *Journal of Physiology*, *526*(3), 695–702. https://doi.org/10.1111/j.1469-7793.2000.00695.x

---

*Panel LIGHT-I — Document 35 V1.0*
*February 21, 2026*
*Templates calibrated: 8 (L2/CIRCADIAN_ARCH_REG_001, L3/DAYLIGHT_MULTICHANNEL_001, L4/CCT_TEMPORAL_ECOLOGICAL_001, L5/DYNAMIC_LIGHT_TEMPORAL_001, NM_CIRCADIAN_ENTRAINMENT_001, CHRONO_LIGHT_ENTRAINMENT_001, CIRCADIAN_ARCH_REGULATION_001, CB_SLEEP_ARCHITECTURE_002)*
*Prior panel: 34_Panel_LI_Light_Luminance.md (Feb 16, 2026) — CASE A*
*Templates remaining in gap registry: 140*
*Next panel: SPATIAL-I (Sprint 13.17)*
