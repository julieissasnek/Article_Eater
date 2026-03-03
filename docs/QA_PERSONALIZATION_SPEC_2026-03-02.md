# QA System Personalization Specification

**Date**: March 2, 2026
**Version**: V23.1
**Status**: Expert Panel Deliberation + Implementation Specification

---

## Executive Summary

The current QA system supports 5 user personas (practitioner/designer, senior researcher, graduate student, systematic reviewer, quick lookup) but provides only cosmetic differentiation. All users receive essentially identical answers with different button labels and question suggestions.

This specification defines **real personalization** based on:
- Different presupposition frames (background knowledge assumed)
- Different answer structures (what gets foregrounded vs backgrounded)
- Different uncertainty communication strategies
- Different vocabulary registers and citation styles
- Different actionability levels (theory vs practice)

The specification is grounded in expert panel deliberation from 8 researchers across cognitive science, HCI, science communication, and epistemology.

---

## Part A: User Type Profiles

### Profile 1: Architect / Practitioner-Designer

**Primary Role**: Making evidence-based design decisions for real buildings/spaces.

#### Presupposition Frame
- Understands basic design language (materials, spatial layout, daylighting, etc.)
- May lack deep background in psychological theory or research methods
- Knows roughly what "evidence-based design" means (usually EBD standards)
- Familiar with constraints: budget, buildability, codes, timelines
- **Default assumption**: "I need actionable guidance, not literature review"

#### Primary Question Mode
- "What should I do?" (prescriptive, not descriptive)
- "What's the evidence for X in my context?" (contextual, bounded)
- "What's the minimum effective dose?" (practical thresholds)
- "What can I measure to know if it's working?" (KPIs, proxy metrics)

#### Completeness Criteria
A complete answer for an architect includes:
1. **Design parameter(s)**: Specific, measurable values or ranges
   - *Example*: "Ceiling height: 10+ feet for creative cognition; evidence threshold at 9.8 ft"
2. **Scope of applicability**: Population, setting, and boundary conditions
   - *Example*: "Applies to knowledge workers in office settings; weaker in manual labor"
3. **Evidence summary**: Strength (EBD level), number of studies, effect size range
4. **Practical implications**: What to do, what to avoid, trade-offs
5. **Measurement approach**: How to know if the design worked
6. **Contraindications**: When this guidance doesn't apply or backfires
7. **Cost-effectiveness** (if applicable): ROI or priority ranking vs other interventions

**NOT required**: Mechanism, detailed epistemology, contested foundations

#### Vocabulary Register
- **Preferred**: Plain English + standard design terms
- **Avoid**: Heavy jargon (don't use "predictive error minimization" without explanation)
- **Translate**: "Attention Restoration Theory" → "the design lets your directed attention system recover"
- **Quantify**: Use concrete units (feet, lux, square meters) not abstract metrics
- **Citation style**: Minimal; list key studies by author-year in footnotes, not inline

#### Actionability Needs
- 70% of the answer should enable a decision
- Explicit trade-offs (e.g., "Open plans increase communication but reduce focus")
- Recommendations ranked by evidence strength
- Known exceptions and boundary conditions

#### Uncertainty Communication
- Credence as percentage with verbal qualifier
- *Example*: "We're 65% confident (moderate confidence) that this effect is real"
- Confidence intervals not precise p-values
- Discuss stability across populations: "Weaker for older adults; stronger for introverts"

---

### Profile 2: Senior Researcher

**Primary Role**: Generating or evaluating research synthesis; identifying research gaps; critiquing methodology.

#### Presupposition Frame
- PhD-level training in their discipline (psychology, environmental science, neuroscience, etc.)
- Understands research design, stats, and limitations
- Expects nuance: contested findings, effect size variability, scope conditions
- **Default assumption**: "I want to know what the literature really says, not a simplified summary"

#### Primary Question Mode
- "What's the state of the art?" (comprehensive, with disputes)
- "What's the evidence quality?" (methodology, limitations, confounds)
- "Where are the gaps?" (what's unknown, what needs studying)
- "What would change if X finding were retracted?" (sensitivity analysis)
- "How strong is this really?" (effect sizes, heterogeneity, publication bias)

#### Completeness Criteria
A complete answer for a senior researcher includes:
1. **Effect sizes** with confidence intervals (or full distribution)
2. **Mechanism(s)** with supporting evidence at each step
3. **Scope conditions** with evidence for each (population, setting, moderators)
4. **Methodology summary**: Common designs, sample sizes, outcome measures
5. **Quality issues**: Publication bias, replication rate, contested interpretations
6. **Heterogeneity**: Effect size varies by what? (moderators identified)
7. **Competing explanations**: Alternative theories that fit some data
8. **Research gaps**: What's missing, what would move the field forward
9. **Uncertainty quantified**: Credence intervals, not point estimates
10. **Conflicts**: Where does this community debate each other?

**NOT required**: Step-by-step actionability; simplified language

#### Vocabulary Register
- **Preferred**: Technical language, domain-specific terms defined precisely
- **Assume**: Understanding of statistics, study design, measurement
- **Transparency**: Show assumptions and limitations openly
- **Citations**: Full APA with DOIs; inline when relevant to interpretation

#### Actionability Needs
- 20% of the answer should enable a decision
- 80% should satisfy intellectual curiosity about evidence quality
- Discuss what would constitute falsification or strong contrary evidence
- Map contested areas: who believes what and why

#### Uncertainty Communication
- Credence intervals (e.g., 0.60–0.75)
- Effect size distributions, not point estimates
- Explicitly discuss publication bias, replication rate
- Estimate what percentage of findings would reverse if unmeasured confounders existed
- *Example*: "We assess 65% credence, range 55–75%, with moderate publication bias likely inflating estimates by ~10–20%"

---

### Profile 3: Graduate Student

**Primary Role**: Learning the field; identifying research directions; mastering foundational theories.

#### Presupposition Frame
- Developing expert knowledge; basic research literacy
- Wants to understand "why" things work, not just "what works"
- Uncertain about theory landscape and field politics
- **Default assumption**: "I need to understand the foundations, and I don't know what I don't know yet"

#### Primary Question Mode
- "How does theory X work?" (foundational understanding)
- "What are the key papers?" (seminal works, must-read articles)
- "What's contested?" (debates that matter for research direction)
- "Where should I focus my work?" (thesis opportunities, open questions)
- "What methodologies dominate this area?" (what training do I need)

#### Completeness Criteria
A complete answer for a graduate student includes:
1. **Theoretical framework** explained from first principles
2. **Key papers** (with brief context about why they matter)
3. **Evidence hierarchy**: What's established vs contested vs speculative
4. **Theory map**: How this theory connects to others
5. **Historical context**: How did we get here? What changed?
6. **Practitioner applications** (if any): Does this matter outside academia?
7. **Methods commonly used** and their strengths/limitations
8. **Open questions**: Interesting research directions
9. **Field politics** (gently): Who disagrees and about what?
10. **Learning path**: "If you want to master this, here's the sequence"

**NOT required**: Engineering precision; actionable design thresholds

#### Vocabulary Register
- **Preferred**: Define technical terms on first use; explain theory-specific concepts
- **Assume**: Smart but not yet expert; willing to learn
- **Scaffold**: Provide conceptual bridges from familiar to unfamiliar
- **Balance**: Accessible language + precise terminology

#### Actionability Needs
- 30% of the answer enables research planning
- 70% satisfies learning goals
- Point toward next reading or research question
- Acknowledge what the student needs to learn next

#### Uncertainty Communication
- Credence with brief explanation of why (e.g., "moderate credence — only 5 RCTs on this, limited scope")
- Discuss where expert opinion divides and why
- *Example*: "70% credence. The mechanism is fairly well-studied, but the effect size varies widely across populations."

---

### Profile 4: Systematic Reviewer

**Primary Role**: Comprehensive, reproducible evidence synthesis for systematic reviews or meta-analysis.

#### Presupposition Frame
- Expertise in systematic review methodology (PRISMA, Cochrane standards)
- Needs machine-readable, reproducible output
- Often filtering evidence for specific inclusion criteria
- **Default assumption**: "I need structured data I can export and analyze independently"

#### Primary Question Mode
- "All evidence for outcome X" (complete enumeration, not synthesis)
- "Studies matching criteria Y" (filtered by methodology, population, etc.)
- "Export data for meta-analysis" (structured, computable format)
- "GRADE ratings" (standardized quality assessment)
- "Effect heterogeneity breakdown" (effects split by study characteristics)

#### Completeness Criteria
A complete answer for a systematic reviewer includes:
1. **Study-level data** (exportable table format):
   - Study ID, authors, year, design, N, population, outcome, effect size (with CI), quality score
2. **GRADE assessment** for each outcome
3. **Inclusion/exclusion criteria** applied (transparency)
4. **Heterogeneity metrics** (I², Q test, explanation of variance)
5. **Publication bias assessment** (funnel plot assessment or Egger test)
6. **Sensitivity analyses**: Remove low-quality studies, show effect change
7. **Subgroup analyses**: Effects by population, setting, intervention type
8. **Forest plot data**: Ready for meta-analysis software import
9. **Search strategy documented**: How studies were found (reproducibility)
10. **Excluded studies** (optionally): High-quality studies that didn't meet criteria

**NOT required**: Narrative synthesis; interpretation of meaning

#### Vocabulary Register
- **Preferred**: Standardized terminology (PRISMA, Cochrane)
- **Format**: Structured data (JSON, CSV, compatible with RevMan or other software)
- **Avoid**: Narrative language; use tables and data structures
- **Citations**: Complete bibliographic info (for import into Zotero, Mendeley)

#### Actionability Needs
- 100% of output should be actionable for statistical synthesis
- Enable independent analysis and interpretation
- Provide raw data, not conclusions

#### Uncertainty Communication
- GRADE certainty of evidence (high, moderate, low, very low)
- Effect size with 95% confidence intervals
- I² heterogeneity statistics
- Publication bias metrics

---

### Profile 5: Quick Lookup

**Primary Role**: Fast answer to a specific question; no time for deep reading.

#### Presupposition Frame
- Busy professional or student with limited time
- Wants the answer in <2 minutes
- May lack domain expertise; needs credence translated
- **Default assumption**: "Just tell me: Is this true and how confident are you?"

#### Primary Question Mode
- Yes/no questions: "Is X supported by evidence?"
- Quick credence: "How confident should I be about Y?"
- Simple facts: "How many studies on Z?"
- Directional: "Does this help or hurt?"

#### Completeness Criteria
A complete answer for quick lookup includes:
1. **Headline** (one sentence)
2. **Credence level** (high/moderate/low)
3. **Why** (one-sentence mechanism)
4. **Scope** (one sentence: for whom/when)
5. **Caveat** (one sentence: main limitation)

**NOT required**: Detail; evidence counts; methodology

#### Vocabulary Register
- **Preferred**: Plain English, no jargon
- **Assume**: General education, smart but not expert
- **Length**: <50 words for the whole answer

#### Actionability Needs
- 90% should help the person decide quickly
- Example: "Plants in offices? Yes, moderate confidence. They reduce stress via visual attention. Works best with living plants, not artificial. Main caveat: weak evidence in very cold climates."

#### Uncertainty Communication
- Simple label: "High / Moderate / Low / Very Low confidence"
- One-sentence reason: "Only 3 studies, all small"

---

## Part B: Personalization Dimensions

These are the axes along which answers should differ per user type.

### Dimension 1: Answer Structure (What Gets Foregrounded)

| User Type | Structure | Leading Element |
|-----------|-----------|-----------------|
| **Architect** | Parameter → Scope → Evidence | Design threshold or specification |
| **Researcher** | Mechanism → Evidence → Heterogeneity | What the mechanism is and how confident we are |
| **Student** | Theory → History → Evidence | Foundational concept and its intellectual context |
| **Reviewer** | Study-by-study data table | Structured, exportable evidence |
| **Quick Lookup** | Headline → Credence → One caveat | Simple yes/no with confidence |

### Dimension 2: Evidence Presentation

| User Type | Evidence Depth | Format | Key Metrics |
|-----------|---|---|---|
| **Architect** | Moderate | Design parameters + practical examples | EBD level, effect size range, sample size |
| **Researcher** | Deep | Effects by population, publication bias, heterogeneity | Effect size (Cohen's d), 95% CI, I², p(bias) |
| **Student** | Moderate | Landmark papers, methodological notes | Study count, quality, what's contested |
| **Reviewer** | Complete | Exportable table (study-level) | All GRADE elements, raw effect sizes |
| **Quick Lookup** | Minimal | Count of studies supporting the claim | Study count only ("5 studies show this") |

### Dimension 3: Vocabulary Register

| User Type | Style | Examples |
|-----------|-------|----------|
| **Architect** | Plain + design terms | "Windows with nature views (Ulrich 1984): daylighting > 200 lux correlated with reduced stress cortisol" |
| **Researcher** | Technical + precise | "Attention Restoration Theory posits that directed attention depletion is recovered via involuntary attention to natural patterns (fascination); meta-analytic d = 0.45 (95% CI: 0.38–0.52)" |
| **Student** | Accessible + conceptual | "Kaplan's Attention Restoration Theory says that nature lets your conscious attention system take a break. Here's how..." |
| **Reviewer** | Standardized terms | PRISMA terminology, GRADE language, effect size notation |
| **Quick Lookup** | Conversational | "Yep, pretty solid evidence. Plants seem to help with stress." |

### Dimension 4: Uncertainty Communication

| User Type | How We Say "We're Unsure" | Example |
|-----------|---|---|
| **Architect** | Percentage + scope variance | "65% confident. Stronger in offices (70%), weaker in homes (55%)." |
| **Researcher** | Credence interval + mechanism for spread | "60–70% credence. Range reflects methodological variation and small-study effects; publication bias likely inflates by 10–15%." |
| **Student** | Verbal + reason | "Fairly well-supported, though contested on mechanisms. All agree the effect is real; debate is about *why*." |
| **Reviewer** | GRADE level + I² | "Moderate certainty (GRADE). I² = 62%, suggesting moderate heterogeneity." |
| **Quick Lookup** | Simple label | "Moderate confidence." |

### Dimension 5: Actionability

| User Type | How We Make It Actionable |
|-----------|---|
| **Architect** | Specific values: "Ceiling height 10+ feet for creative work; minimize to 8 ft for focus tasks." |
| **Researcher** | Methodological recommendations: "Test for moderation by personality; replicate in non-Western samples." |
| **Student** | Reading path: "Start with Kaplan & Kaplan 1989; then read recent critiques by Yuan et al. 2021." |
| **Reviewer** | Export format: "JSON dump of all study-level data; 47 RCTs, 12 quasiexperimental studies." |
| **Quick Lookup** | One sentence recommendation: "Use living plants (not artificial); evidence stronger with natural light." |

---

## Example: Same Question, Different Answers

**Query**: "Do plants reduce stress in office environments?"

### Answer for Architect
---

**Design Finding: Biophilic Elements (Plants) in Offices**

**Recommendation**: Include living plants visible from work areas. Evidence supports this as a moderate-confidence, low-cost stress reduction intervention.

**Design Parameters**:
- **Living plants visible** from 50% of workstations (sight lines matter)
- **Placement**: Within 2–3 meters of seated workers; views stronger than mere presence
- **Plant density**: Studies effective at 1 plant per 20 m²; diminishing returns above 5 per 20 m²
- **Maintenance**: Must be live and healthy (stressed plants show opposite effect)

**Evidence Strength**: EBD Level C–B (5 RCTs, 12 observational studies); median effect size r = 0.35 (moderate)

**Scope**: Office knowledge workers; effect weakens for outdoor workers, manual labor, and environments with already-strong biophilia access. Limited evidence in hot climates (>30°C).

**Trade-offs**:
- **Pro**: Low cost, multi-benefit (aesthetics, air quality, stress, mood)
- **Con**: Requires maintenance; takes 4 weeks to see stress benefits; takes up floor space

**Measurement**:
- Primary KPI: Self-reported stress (survey) or cortisol sampling (invasive but objective)
- Secondary KPI: Sick days, productivity metrics (mixed evidence)
- Proxy: Employee satisfaction with workspace

**When This Doesn't Apply**: Sealed buildings with poor ventilation (benefit may reverse); workplaces where plants aren't culturally valued; cost-constrained projects where HVAC upgrades are more impactful.

---

### Answer for Researcher
---

**Biophilic Elements and Workplace Stress: Evidence Synthesis**

**Mechanism** (Supported): Natural elements (plants, views, wood) interact with Attention Restoration Theory (ART) and Stress Recovery Theory (SRT) to reduce acute and chronic stress via:
1. Involuntary attention to natural patterns → directed attention recovery (ART)
2. Unthreatening visual features → parasympathetic activation and positive affect (SRT)

Individual differences significant: effect stronger in nature-deprived populations, for people with high baseline cortisol, and for environments lacking other restorative features.

**Effect Size Meta-Analysis**:
- **Plants visible (vs. none)**: r = 0.35 (95% CI: 0.28–0.42), k = 17, N = 1,247
  - RCT subset: r = 0.32 (k = 5); observational subset: r = 0.38 (k = 12)
  - I² = 48% (moderate heterogeneity)
- **Outcome heterogeneity**:
  - Cortisol/stress biomarkers: d = 0.48 (k = 8)
  - Self-report stress: d = 0.31 (k = 9)
  - Mood/affect: d = 0.41 (k = 7)

**Scope Conditions** (with evidence):
- **Population**: Strongest in office workers (r = 0.38); weaker in clinical populations (r = 0.25, n = 3 studies); students show intermediate effect (r = 0.33, k = 6)
- **Setting**: Indoor office settings (r = 0.38); hospitals (r = 0.28, only 2 RCTs); outdoor baseline (r = 0.12, weak)
- **Moderators found** (via subgroup analysis):
  - Plant visibility (direct view): r = 0.41 vs. no view: r = 0.22 (p < .05)
  - Living vs. artificial plants: r = 0.39 vs. r = 0.18 (p < .01)
  - Proximity <3 m: r = 0.42 vs. >5 m: r = 0.24 (p < .05)

**Quality Issues**:
- **Publication bias**: Funnel plot asymmetry suggests small studies with large effects unpublished (Egger p = 0.08)
- **Replication rate**: Only 5 RCTs; 3 show effect, 2 null (60% success rate)
- **Methodological concerns**:
  - Most studies assess stress via self-report (demand characteristics possible)
  - Only 2 blinded studies; most participants aware of intervention
  - Causality unclear: does plant presence reduce stress, or do people who choose plant-rich offices have lower baseline stress?

**Contested Issues**:
- **Mechanism**: ART vs. SRT debate. SRT camp (Ulrich) emphasizes visual preference + parasympathetic; ART camp (Kaplan) emphasizes attention dynamics. Data fit both; no decisive test yet.
- **Dose**: Some studies show ceiling effect at 1 plant per 20 m²; others show linear improvement. Unclear if true dose-response or confounded by other factors (office size, baseline biophilia access).
- **Ecological Validity**: Most lab studies use potted plants or photos; few test real office redesigns longitudinally.

**Research Gaps**:
1. Long-term effects: All studies <12 weeks. Does benefit persist or adapt away?
2. Dose-response: Systematic variation in plant density, species, placement
3. Mechanisms: Neuroimaging studies of ART vs SRT distinguishing them
4. Non-Western populations: 85% of studies from Western countries; unclear if findings generalize to cultures with different nature aesthetics
5. Interaction with other interventions: Do plants + lighting upgrades + flexible scheduling stack? Or substitute?

**Credence Assessment**: 65% confidence (range: 55–75%).
- Evidence quality moderate (mostly observational; publication bias likely; RCT base small)
- Effect robustness moderate (replicates across settings but with heterogeneity)
- Mechanism partially supported (both ART and SRT components have evidence)
- Likelihood of reversal if unmeasured confounders exist: ~20% (moderate risk)

---

### Answer for Graduate Student
---

**Biophilic Design and Stress: A Learning Guide**

**The Core Idea**: Rachel and Stephen Kaplan's Attention Restoration Theory (ART) proposes that directed attention (what you use to focus on work or complex problems) gets depleted with use. Natural environments, especially those with "fascination" — things that capture your attention effortlessly — let your directed attention system recover. Roger Ulrich's Stress Recovery Theory (SRT) makes a similar but different claim: unthreatening natural features trigger positive emotions and parasympathetic activation, directly reducing stress.

Both theories predict that office plants should reduce stress. The question: which mechanism dominates? Are plants just pretty (SRT), or do they actively restore cognitive resources (ART)?

**Historical Context**:
- **1984**: Ulrich's landmark hospital window study showed patients near windows recovered faster post-surgery (fewer painkillers, shorter stays). Sparked the EBD movement.
- **1989**: Kaplans' ART paper formalized attention restoration. Became dominant in landscape architecture circles.
- **2000s**: Proliferation of small office studies showing plants reduce self-report stress. Limited mechanism work.
- **2010s**: Debate sharpened: does nature work *because* it's restorative (ART), *because* it's beautiful (SRT), *because* it signals status/control (evolutionary view), or *because* of air quality (biomechanical)? Most likely: all contribute.
- **2020s**: Emerging neuroscience work (fMRI, EEG) beginning to test mechanisms directly.

**Key Papers** (what you should read):
1. **Foundational**:
   - Ulrich, R. S. (1984). "View through a window may influence recovery." Science, 224(4647), 224–225. [The seminal study. Short, elegant, easy to read.]
   - Kaplan, S., & Kaplan, R. (1989). The experience of nature: A psychological perspective. Cambridge University Press. [Dense but essential for ART.]

2. **Recent Strong Studies**:
   - Marselle, M. R., et al. (2019). "Neighbourhood nature and mental wellbeing in working ages." Landscape & Urban Planning, 192, 103658. [Meta-analysis; shows heterogeneity.]
   - Birks, A., Tirney, S., et al. (2017). "Nature helps." Journal of Environmental Psychology, 51, 157–166. [Office study with mechanism checks.]

3. **Critical/Contrarian** (to understand debates):
   - Hartig, T., & Staats, H. (2006). "Linking preference and health in natural landscapes." Journal of Environmental Psychology, 26(4), 326–338. [Critiques oversimplification.]
   - Brymer, E., & Cuddihy, T. F. (2020). "The biophilia hypothesis and environmental education." Australian Journal of Environmental Education, 36(3), 284–296. [Questions whether biophilia is universal.]

**Evidence Summary**:
- ~17 studies show plants reduce self-reported stress (moderate effect size)
- Mechanism partially tested: some evidence for both ART and SRT; no study clearly distinguishes
- Strong methodological limitations: mostly observational; small samples; limited long-term follow-up
- About 60% of RCTs show the effect (good, but not overwhelming)

**Where the Field Debates**:
- **Mechanism**: Is it attention restoration, or just visual beauty, or air quality, or status signaling? (Probably all, differently for different people.)
- **Individual Differences**: Do introverts benefit more than extroverts? People with higher baseline anxiety? Nature-lovers vs. city-dwellers? (Understudied.)
- **Dose-Response**: How much nature is enough? Is 1 plant sufficient, or do you need a "biophilic rich" environment? (Unclear.)
- **Causality**: Do plants reduce stress, or do less-stressed people choose offices with plants? (Mostly observational, so hard to know.)

**Research Opportunities**:
1. **Mechanism studies**: Use fMRI or EEG to directly test whether ART or SRT dominates. (Hypothesis: probably both, moderated by individual differences.)
2. **Longitudinal effects**: Plant effects in the lab persist for hours; do they fade after weeks in a real office? (Adaptation?)
3. **Cultural variation**: Test in non-Western contexts. Are Kaplans' "fascination" categories universal? (Doubt it.)
4. **Interaction studies**: Do plants + music + flexible seating + circadian lighting stack their effects, or substitute? (System question, hard to test.)

**Learning Path**:
- Start: Read Ulrich 1984 (15 min) for the origin story
- Then: Skim Kaplan & Kaplan 1989 introduction (30 min) to understand ART
- Then: Read 2–3 recent office studies (1 hour) to see current state
- Then: Read 1 critical paper (30 min) to understand limitations and debates
- **Project idea**: Design a study that tests mechanism. Pick one of: (a) ART vs SRT using reaction time + fMRI, (b) Dose-response with randomized plant density, (c) Individual differences with personality measures.

---

### Answer for Systematic Reviewer
---

**Biophilic Elements (Plants) and Workplace Stress: Data Export**

**Inclusion Criteria Applied**:
- Publication year: 2000–2026
- Design: RCT, quasi-experimental, or observational cohort
- Population: Adult workers (age 18+), office settings
- Intervention: Visible living plants (excluding photos, potted plants only, no plant tours)
- Outcome: Stress (cortisol, self-report, physiological) OR affect/mood

**Exclusion**: Studies combining plants with other interventions (meditation, music); outdoor/environmental samples; clinical populations

**Results**: 17 studies identified (5 RCT, 12 observational cohort); 1,247 participants total

**GRADE Evidence Summary**:
| Outcome | # Studies | Design | Certanty | Effect (95% CI) | I² | Notes |
|---------|-----------|--------|----------|---|---|---|
| Self-report stress | 9 | 5 RCT, 4 obs | **Moderate** | r = 0.31 (0.23–0.39) | 34% | Demand characteristics possible; only 2 blinded |
| Cortisol/biomarkers | 8 | 3 RCT, 5 obs | **Low** | d = 0.48 (0.32–0.64) | 52% | Small sample sizes; mixed methodology |
| Affect/mood | 7 | 2 RCT, 5 obs | **Low** | r = 0.41 (0.28–0.52) | 48% | Overlaps with stress but separate outcome |

**Publication Bias Assessment**: Funnel plot shows asymmetry (small studies with large effects); Egger test p = 0.08 (suggestive). Trim-fill adjustment suggests 2–4 studies with null effects unpublished.

**Heterogeneity Breakdown** (Self-Report Stress; I² = 34%):
- By proximity: <3 m away: r = 0.42 vs. >5 m: r = 0.24 (p < 0.05)
- By plant type: Living vs. artificial: r = 0.39 vs. r = 0.18 (p < 0.01)
- By population: Office workers: r = 0.38 vs. students: r = 0.33 vs. clinical: r = 0.25 (p = 0.12, non-sig but trend)

**Study-Level Data** (CSV export format below; see attached file for complete table):

```csv
study_id,year,first_author,design,n_total,population,intervention_type,outcome,effect_size,ci_lower,ci_upper,rct_blinded,methodological_concerns
1,2019,Marselle,observational,150,office_workers,plants_visible,self_report_stress,r_0.35,0.23,0.46,no,uncontrolled_assignment
2,2017,Birks,rct,42,office_workers,plants_vs_control,cortisol,d_0.52,0.05,0.99,yes,small_n
3,2021,Park,rct,68,students,plants_visible,mood,r_0.38,0.15,0.57,yes,short_timeframe
...
[16 more rows in full export]
```

**Sensitivity Analyses**:
1. **Remove low-quality studies** (quality score <6/10): Pooled effect r = 0.33 (vs. r = 0.31 overall) — consistent
2. **RCTs only**: r = 0.32 (k=5, N=216) — slightly weaker but similar
3. **Exclude publication bias** (trim-fill): Estimated true effect r = 0.27 (range: 0.19–0.35) — still significant

**Recommended Meta-Analysis Approach**:
- Use random-effects model (I² = 34% indicates between-study heterogeneity)
- Consider outcome subgroups (stress, mood, cognition separate)
- Sensitivity: remove studies with extreme effect sizes and recalculate
- Meta-regression: test whether proximity, plant type, study design predict effect size

**Search Strategy Documentation** (Reproducibility):
- Databases: PubMed, PsycINFO, Web of Science (2000–2026)
- Search terms: ("plant*" OR "biophil*" OR "green*") AND ("office" OR "workplace" OR "work* environment") AND ("stress" OR "mood" OR "affect*" OR "cortisol*")
- Hand-search: References of included studies + related Cochrane reviews
- Total retrieved: 324 unique; screened 324; included 17; agreement (Cohen's κ = 0.82)

---

### Answer for Quick Lookup
---

**Do plants reduce stress in offices?**

**Yes.** Moderate confidence. About 17 studies show living plants visible from your desk reduce stress slightly. Effect is real but modest.

**Why?** Plants seem to let your attention system take a break (or they're just nice to look at—debate ongoing).

**When?** Strongest evidence in office workers. Needs to be a living plant, visible from where you sit. Artificial plants don't work.

**Main caveat**: Most studies are small. Only 5 proper randomized experiments; the rest are observational.

**Bottom line**: Low-cost, multiple benefits (aesthetic, air quality, stress). Worth doing if space allows.

---

## Part C: Implementation Architecture

### High-Level Design

Personalization happens at **response generation time**, not presentation time. We generate genuinely different answers per user type because they need different content, not just different formatting.

```
User Query → Detect User Type → Route to Type-Specific Handler →
Format for Type → Return Answer
```

### Integration Point: Extend ArbitraryQAHandler

The current `ArbitraryQAHandler` routes questions to static handlers or AI. We extend it with **user-type-aware routing**:

```python
class ArbitraryQAHandler:
    def answer(
        self,
        query: str,
        user_type: UserType = None  # NEW
    ) -> Dict[str, Any]:
        """
        Route query to type-specific handler and generate personalized answer.
        """
        # Classify question type (existing)
        q_type = self._classify_question(query)

        # NEW: Select handler based on both question type AND user type
        handler = self._get_handler(q_type, user_type)

        # Generate answer with type-specific logic
        response = handler(query, user_type)

        return response
```

### Data Structures

#### UserType (Enhanced from Config)

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional

class UserTypeID(Enum):
    """Canonical user type identifiers."""
    ARCHITECT = "architect"
    RESEARCHER = "researcher"
    STUDENT = "student"
    REVIEWER = "reviewer"
    QUICK_LOOKUP = "quick_lookup"

@dataclass
class UserProfile:
    """Complete user type profile."""
    type_id: UserTypeID
    name: str
    presupposition_frame: str  # What they assume they know
    primary_question_modes: List[str]
    completeness_criteria: List[str]  # What constitutes a full answer
    vocabulary_register: str  # plain / technical / moderate
    actionability_level: float  # 0-1, what % of answer should enable decisions
    uncertainty_communication: str  # how to express credence
    answer_structure: str  # What comes first: parameter, mechanism, theory, data, headline
    evidence_depth: str  # minimal / moderate / deep
    citation_style: str  # none / footnote / inline / full_apa

    def __post_init__(self):
        """Validate profile completeness."""
        required = [
            self.presupposition_frame,
            self.primary_question_modes,
            self.completeness_criteria,
        ]
        assert all(required), "Incomplete user profile"
```

#### TypedAnswer (Response Structure)

```python
@dataclass
class TypedAnswer:
    """Answer customized for a user type."""
    user_type_id: UserTypeID

    # Content layers (per type, some may be None)
    headline: Optional[str]  # For quick lookup
    design_parameters: Optional[List[Dict]]  # For architect
    mechanism: Optional[str]  # For researcher, student
    theory_explanation: Optional[str]  # For student
    effect_sizes: Optional[Dict]  # For researcher (with CI, I², etc.)
    study_data: Optional[List[Dict]]  # For reviewer (exportable table)
    evidence_summary: str  # All types get this
    scope_conditions: List[str]  # Customized by type
    actionability_section: str  # Type-specific "what to do"
    uncertainty_expressed: str  # Type-specific credence communication
    citations: List[str]  # Formatted per type

    # Metadata
    answer_completeness: float  # 0-1, how complete for this type
    sources_used: List[str]  # Which templates, papers, etc.
    confidence_reasoning: str  # Why we have this credence

    def to_text(self, **formatting_opts) -> str:
        """Render to readable text per type."""
        pass

    def to_json(self) -> Dict:
        """Export for API/storage."""
        pass
```

#### DesignParameter (for Architects)

```python
@dataclass
class DesignParameter:
    """Actionable design specification."""
    parameter_name: str  # "Ceiling height", "Plant density", etc.
    recommended_range: Tuple[float, float]  # (min, max)
    unit: str  # "feet", "plants per 20m²", etc.
    evidence_level: str  # "High", "Moderate", "Low"
    population_scope: Dict[str, float]  # {"office_workers": 0.38, "home": 0.22}
    trade_offs: List[str]
    measurement_approach: str  # How to know if it's working
    contraindications: List[str]  # When NOT to apply
```

#### ResearcherEffectData (for Researchers)

```python
@dataclass
class ResearcherEffectData:
    """Complete effect size data for meta-analysis."""
    outcome: str  # "stress", "mood", "cortisol", etc.
    k: int  # Number of studies
    n_total: int  # Total participants
    effect_size: float  # Cohen's d or Pearson's r
    ci_lower: float
    ci_upper: float
    i_squared: float  # Heterogeneity
    p_heterogeneity: float
    publication_bias_assessment: str  # "No bias detected", "Likely bias", etc.
    egger_p: Optional[float]
    trim_fill_estimate: Optional[float]
    subgroup_analyses: Dict[str, List[Dict]]  # {"population": [...], "setting": [...]}
    credence_interval: Tuple[float, float]  # e.g., (0.55, 0.75)
    credence_reasoning: str
```

### Handlers by Question Type + User Type

Create type-specific handlers for common question types:

```python
class TypeSpecificHandlers:
    """Routes and generates type-specific answers."""

    def handle_mechanism_question(
        self,
        query: str,
        user_type: UserTypeID
    ) -> TypedAnswer:
        """
        "How does X cause Y?"
        Routes differently per type:
        - ARCHITECT: mechanism → design implications
        - RESEARCHER: mechanism → evidence quality → heterogeneity
        - STUDENT: mechanism → theory → historical context
        - REVIEWER: mechanism-supporting studies (exportable)
        - QUICK: mechanism (one sentence)
        """

        # Get base mechanism from knowledge base
        base_mechanism = self._retrieve_mechanism(query)

        # Type-specific enrichment
        if user_type == UserTypeID.ARCHITECT:
            return self._architect_mechanism_handler(base_mechanism, query)
        elif user_type == UserTypeID.RESEARCHER:
            return self._researcher_mechanism_handler(base_mechanism, query)
        elif user_type == UserTypeID.STUDENT:
            return self._student_mechanism_handler(base_mechanism, query)
        elif user_type == UserTypeID.REVIEWER:
            return self._reviewer_mechanism_handler(base_mechanism, query)
        else:  # QUICK_LOOKUP
            return self._quick_mechanism_handler(base_mechanism, query)

    def handle_evidence_question(
        self,
        query: str,
        user_type: UserTypeID
    ) -> TypedAnswer:
        """
        "What evidence supports / contradicts X?"
        """
        # Similar dispatch per type
        pass

    def handle_scope_question(
        self,
        query: str,
        user_type: UserTypeID
    ) -> TypedAnswer:
        """
        "When does X apply? For whom? In what settings?"
        """
        # Similar dispatch per type
        pass

    # ... more handlers for other question types
```

### Integration with Existing Code

#### Update 1_query.py

```python
# streamlit_app/pages/1_query.py

def execute_query(query: str, user_type: Optional[str] = None):
    """Execute query with personalization."""
    client = get_client()

    # Convert user type string to enum if needed
    user_profile = None
    if user_type:
        user_profile = get_user_profile(user_type)

    request = QueryRequest(
        query=query,
        mode=st.session_state.response_mode,
        user_type=user_type,  # NEW: pass user type to API
        user_profile=user_profile,  # NEW: optional profile data
        include_scope=True,
        include_practitioner_implications=True,
    )

    with st.spinner("Searching evidence base..."):
        result = client.execute_query(request)
        st.session_state.query_result = result

        # NEW: Detect if this is a personalized response
        if result.is_personalized:
            st.info(f"Answer customized for {result.user_type.name}")
```

#### Update api_client.py

```python
# streamlit_app/api_client.py

@dataclass
class QueryRequest:
    query: str
    mode: str
    user_type: Optional[str] = None  # NEW
    user_profile: Optional[Dict] = None  # NEW
    include_scope: bool = True
    include_practitioner_implications: bool = True

    def to_json(self) -> Dict:
        """Serialize for HTTP request."""
        return {
            "query": self.query,
            "mode": self.mode,
            "user_type": self.user_type,
            "user_profile": self.user_profile,
            "include_scope": self.include_scope,
            "include_practitioner_implications": self.include_practitioner_implications,
        }

@dataclass
class QueryResult:
    headline: str
    summary: str
    user_type: Optional[str]  # NEW
    is_personalized: bool  # NEW
    personalization_notes: str  # NEW
    # ... rest of fields
```

#### Update arbitrary_qa_handler.py

```python
# src/services/arbitrary_qa_handler.py

class ArbitraryQAHandler:
    """AI-routed QA with type-specific personalization."""

    def __init__(self):
        self.question_classifier = QuestionClassifier()
        self.handlers = TypeSpecificHandlers()
        self.user_profiles = self._load_user_profiles()

    def answer(
        self,
        query: str,
        user_type_id: Optional[UserTypeID] = None,
        **options
    ) -> Dict[str, Any]:
        """
        Answer a question, personalized by user type if provided.

        Args:
            query: The user's question
            user_type_id: UserTypeID enum (e.g., UserTypeID.ARCHITECT)
            **options: Additional parameters (mode, include_scope, etc.)

        Returns:
            TypedAnswer converted to dict
        """
        # Classify the question
        q_type = self.question_classifier.classify(query)

        # Get user profile (if type provided)
        user_profile = None
        if user_type_id:
            user_profile = self.user_profiles.get(user_type_id)

        # Route to type-aware handler
        if user_profile is not None:
            typed_answer = self.handlers.handle_typed_question(
                query=query,
                question_type=q_type,
                user_type_id=user_type_id,
                user_profile=user_profile,
                **options
            )
        else:
            # Fallback: generate generic answer (backward compatible)
            typed_answer = self._generate_generic_answer(query, q_type, **options)

        return typed_answer.to_dict()

    def _load_user_profiles(self) -> Dict[UserTypeID, UserProfile]:
        """Load canonical user type profiles."""
        return {
            UserTypeID.ARCHITECT: UserProfile(
                type_id=UserTypeID.ARCHITECT,
                name="Architect / Designer",
                presupposition_frame="Understands design, needs actionable guidance",
                primary_question_modes=[
                    "What should I do?",
                    "What's the evidence in my context?",
                    "What's the minimum effective dose?",
                ],
                completeness_criteria=[
                    "Design parameters with measurable values",
                    "Scope of applicability",
                    "Evidence summary (strength, studies, effect size)",
                    "Practical implications",
                    "Measurement approach (KPIs)",
                    "Contraindications",
                ],
                vocabulary_register="plain_with_design_terms",
                actionability_level=0.7,
                uncertainty_communication="percentage_with_scope_variance",
                answer_structure="parameter_first",
                evidence_depth="moderate",
                citation_style="footnote",
            ),
            # ... and 4 more profiles
        }
```

---

## Part D: Epistemic Guardrails

### Rule 1: No Misrepresentation via Simplification

**Principle**: Simplifying for one user type must not create false certainty or omit crucial qualifications.

**Implementation**:
- Every answer, regardless of depth, must include:
  - What we know (stated as credence, not certainty)
  - What we don't know (explicit limitations)
  - What's contested (if applicable)
- **Required disclosure for all types**: Any finding with credence < 0.70 must include one caveat

**Example**:
- **WRONG (oversimplified)**: "Plants reduce stress." (Architect answer that drops all uncertainty)
- **RIGHT (appropriately nuanced)**: "Plants reduce stress (moderate confidence, 65%). Strongest evidence in offices with direct views; weaker evidence in hospitals."

### Rule 2: Evidence Quality Transparency

**Principle**: Personalization may adjust presentation, but must never hide evidence problems.

**Implementation**:
- **Quick Lookup** answer can omit details, but must disclose quality level:
  - "High confidence: 10+ RCTs, consistent effects"
  - "Moderate confidence: 5 RCTs, some heterogeneity"
  - "Low confidence: only 2 RCTs, weak effects"

- **Architect** answer must disclose: "Based on EBD Level C evidence" (what that means)
- **Researcher** answer must include: Publication bias assessment, replication rate, effect heterogeneity
- **Student** answer must include: "Contested on mechanisms; all agree the effect is real"

### Rule 3: No Threshold Inflation

**Principle**: Design parameters must not imply false precision.

**Implementation**:
- If a researcher says "the effect ranges from r = 0.25 to r = 0.48 depending on population," the architect parameter should NOT say "ceiling height 10.0 feet" (false precision).
- Instead: "Ceiling height 10+ feet; evidence weaker below 9.8 ft but not eliminated; no studies >12 ft"

### Rule 4: Mechanism Honesty

**Principle**: If mechanism is unknown or contested, say so even in simplified answers.

**Implementation**:
- Researcher finds: "Mechanism unclear; both ART and SRT frameworks fit the data"
- Architect can simplify to: "Plants reduce stress via visual or cognitive mechanisms (mechanism still being studied)"
- Student should learn: "The field debates whether it's attention restoration or visual beauty"
- Quick lookup can say: "Why is debated among experts"

### Rule 5: Scope Conditions Are Not Optional

**Principle**: Every answer must include when the evidence applies and doesn't.

**Implementation**:
- **Researcher**: Full subgroup table (effect by population, setting, intervention type)
- **Architect**: "Works in office settings with natural light; evidence weak in hospitals"
- **Student**: "Stronger in Western populations; limited non-Western research"
- **Reviewer**: Structured metadata: population filters, setting filters, design type filters
- **Quick lookup**: One-sentence scope: "Works best with living plants visible from your desk"

### Rule 6: Individual Differences Must Be Disclosed

**Principle**: If effect varies substantially by person type, we must say so.

**Implementation**:
- Researcher finds: Effect size r = 0.35 overall, but r = 0.50 for introverts, r = 0.22 for extroverts
- This must appear in **all** answers, customized:
  - **Architect**: "Stronger benefit for introverted workers; placement near focus areas recommended"
  - **Researcher**: Full interaction table
  - **Student**: "Individual differences: introverts may benefit more (debate why)"
  - **Reviewer**: Subgroup analysis available in exported data
  - **Quick lookup**: "Works especially well for introverted workers"

### Rule 7: Competing Explanations Must Be Acknowledged

**Principle**: If multiple theories fit the data, all must be named.

**Implementation**:
- Finding: Plants reduce stress. Three theories fit:
  1. Attention Restoration (Kaplan)
  2. Stress Recovery (Ulrich)
  3. Social signaling / status (evolutionary psychology)
- **All answers must acknowledge** this, at type-appropriate depth:
  - **Architect**: "Mechanism unclear; probably multiple pathways"
  - **Researcher**: "Evidence supports ART (r = 0.35), SRT (r = 0.38), and evolutionary signaling pathway. Cannot currently distinguish empirically."
  - **Student**: "The main theoretical debate: is this ART, SRT, or something else?"
  - **Reviewer**: Cross-reference papers testing each mechanism
  - **Quick lookup**: Omit mechanism debate (depth=minimal) but don't claim false certainty

---

## Part E: Test Criteria

### Test Case 1: "Do plants reduce stress?"

#### Test for Architect

**Query**: "Do plants reduce stress in office environments?"

**Expected Answer Characteristics**:
- ✓ Opens with design parameters (plant visibility, placement, density)
- ✓ Includes EBD level or evidence strength
- ✓ Provides scope: "Works best in offices with natural light; weaker in sealed buildings"
- ✓ Trade-offs explicitly stated
- ✓ Measurement approach given (e.g., "Self-reported stress or cortisol sampling")
- ✓ No mechanism details; instead actionability: "What to do"
- ✓ Length: 300–500 words
- ✓ Credence expressed as "65% confident" (not "supported by research")

**Failure Modes**:
- ✗ Reads like a literature review (mechanism-first)
- ✗ Includes statistical notation (I², p-values)
- ✗ Omits scope conditions
- ✗ Over-claims certainty ("Plants definitely reduce stress")

---

#### Test for Researcher

**Query**: "What does the evidence show on plants and workplace stress?"

**Expected Answer Characteristics**:
- ✓ Leads with effect sizes (d = 0.48, 95% CI: 0.32–0.64)
- ✓ Includes heterogeneity (I² = 52%)
- ✓ Publication bias assessment (Egger p = 0.08)
- ✓ Subgroup breakdown (effect by population, setting, intervention type)
- ✓ Replication rate: "60% of RCTs positive; 40% null or opposite"
- ✓ Contested mechanisms: "ART vs SRT both fit data; cannot distinguish empirically"
- ✓ Research gaps: "Long-term effects unknown; dose-response unclear"
- ✓ Credence interval: "60–70% credence, range reflects publication bias (10–15%)"
- ✓ Length: 800–1200 words
- ✓ Citations: Full APA with DOIs, inline when relevant

**Failure Modes**:
- ✗ Simplified to lay language ("Plants seem to help")
- ✗ Omits effect size or heterogeneity
- ✗ No publication bias discussion
- ✗ Presents single mechanism as settled

---

#### Test for Student

**Query**: "How does the biophilic design work to reduce stress?"

**Expected Answer Characteristics**:
- ✓ Starts with foundational theory explanation (ART and/or SRT)
- ✓ Traces historical development (Ulrich 1984 → Kaplan 1989 → modern work)
- ✓ Key papers named and contextualized ("Marselle 2019 meta-analysis showed...")
- ✓ Mechanism debate: "Some argue ART, others SRT; evidence supports both"
- ✓ Learning path: "Start with Ulrich; then read Kaplan; then see modern critiques"
- ✓ Research opportunities: "Good thesis directions include: testing mechanism with fMRI, longitudinal effects..."
- ✓ Individual differences: "Introverts may benefit more but understudied"
- ✓ Length: 600–900 words
- ✓ Tone: Scaffolding, inviting deeper learning

**Failure Modes**:
- ✗ Too simple (no theoretical depth)
- ✗ No historical context
- ✗ Presents one theory as settled
- ✗ Doesn't point to future research directions

---

#### Test for Reviewer

**Query**: "I need all evidence on plants and stress for a meta-analysis."

**Expected Answer Characteristics**:
- ✓ Structured table: 17 studies, study-level data (author, year, n, design, effect, 95% CI)
- ✓ GRADE certainty ratings (high/moderate/low)
- ✓ Inclusion/exclusion criteria documented
- ✓ Publication bias metrics (funnel plot, Egger p, trim-fill)
- ✓ Heterogeneity: I², Q test, explanation of variance
- ✓ Subgroup analyses: effect by population, setting, intervention type
- ✓ Exportable format: CSV or JSON compatible with RevMan/other software
- ✓ Search strategy reproduced: databases, search terms, date range, selection process (Cohen's κ for inter-rater agreement)
- ✓ Sensitivity analyses: remove low-quality, show effect change
- ✓ Zero narrative opinion; all data-driven

**Failure Modes**:
- ✗ Narrative synthesis instead of tables
- ✗ Cherry-picked studies
- ✗ No GRADE ratings
- ✗ Search strategy not reproducible

---

#### Test for Quick Lookup

**Query**: "Do plants reduce stress?"

**Expected Answer Characteristics**:
- ✓ Headline: "Yes" or "Probably" (not equivocal)
- ✓ Credence label: "Moderate confidence"
- ✓ One-sentence mechanism: "They seem to let your attention system take a break"
- ✓ One-sentence scope: "Works best with living plants visible from your desk"
- ✓ One-sentence caveat: "Only 5 proper studies; most evidence from observations"
- ✓ Total length: <100 words
- ✓ No citations, no effect sizes, no methodology

**Failure Modes**:
- ✗ Too detailed (includes heterogeneity, GRADE)
- ✗ Equivocal language ("May help, but evidence is mixed")
- ✗ Mechanism explanation too deep
- ✗ Too long (>100 words)

---

### Test Case 2: "What are scope conditions for nature-view effects in healthcare?"

#### Test for Architect

**Query**: "When should I use windows with nature views in hospital design? Are there cases where it backfires?"

**Expected Answer Characteristics**:
- ✓ Population scope: "Applies to post-operative patients; limited evidence for chronic patients"
- ✓ Setting scope: "Private or semi-private rooms; no evidence for intensive care (too acute)"
- ✓ View type: "Real nature views (>50% vegetation) > photos > no view"
- ✓ Contraindication: "May increase stress for agoraphobic or anxiety-prone patients; screen for this"
- ✓ Parameters: "Window area: 20+ sq ft visible; distance from bed <10 ft; unobstructed view"
- ✓ Measurement: "Length of stay, pain medication use, patient satisfaction"
- ✓ Trade-off: "Views increase cost; prioritize post-op recovery areas; ICU may not benefit"

---

#### Test for Researcher

**Query**: "What are the scope conditions for Ulrich's window effect? How does this generalize?"

**Expected Answer Characteristics**:
- ✓ Ulrich 1984 effect (gallbladder surgery patients): LOS 8.4 vs 7.0 days, p < 0.05
- ✓ Replication: Only 3 direct replications; 2 positive, 1 null (in intensive care)
- ✓ Moderators studied:
  - Surgery type: Post-op recovery stronger than acute medical
  - Window type: Real views (d = 0.6) > photos (d = 0.2) > no view
  - Patient characteristics: Anxiety level predicts who benefits (r = 0.40); chronicity unclear
- ✓ Confounds not ruled out: Patients in window rooms may have better-located, more expensive rooms; reverse causality possible
- ✓ Mechanisms unclear: Visual attention? Perceived control? Light exposure? Not tested directly
- ✓ Generalization: Primarily US hospital culture; limited non-Western evidence
- ✓ Research gaps: "Long-term outcomes unknown; mechanism untested; non-Western populations; ICU effectiveness"

---

#### Test for Student

**Query**: "Why do hospital window views matter for recovery? Is this just beautiful aesthetics or something deeper?"

**Expected Answer Characteristics**:
- ✓ Context: Ulrich's groundbreaking 1984 study; revolutionized EBD thinking
- ✓ Theory options:
  - SRT: Nature triggers positive affect → parasympathetic activation → faster recovery
  - Cognitive: Nature views reduce cortisol, supporting immune function
  - Evolutionary: Natural scenes signal safety → behavioral approach
- ✓ Current debate: "All three mechanisms probably play a role; hard to separate empirically"
- ✓ Learning question: "What would distinguish these theories? Design a study..."
- ✓ Scope: "Strong for post-op; weaker for chronic pain; unclear for ICU"
- ✓ Field trajectory: "1980s: Ulrich's insight. 2000s: Multiple mechanisms proposed. 2010s+: Neuroimaging starting to test mechanisms"

---

### Measurement of Personalization Effectiveness

**Success Metric 1: Type-Appropriateness Scoring**

For each user type, score the answer 0–1 on adherence to profile criteria:

```python
def score_answer_appropriateness(
    answer: TypedAnswer,
    user_type: UserTypeID
) -> float:
    """
    Score answer on how well it matches user type expectations.
    """
    profile = USER_PROFILES[user_type]
    score = 0.0
    max_points = 0.0

    # Check answer structure
    if user_type == UserTypeID.ARCHITECT:
        # 20% of score: Does answer lead with design parameters?
        if answer.design_parameters:
            score += 0.20
        max_points += 0.20

        # 15% of score: Actionability
        if _is_actionable(answer.actionability_section):
            score += 0.15
        max_points += 0.15

        # 15% of score: Scope conditions
        if len(answer.scope_conditions) >= 3:
            score += 0.15
        max_points += 0.15

        # 10% of score: No unnecessary mechanism detail
        mechanism_words = len(answer.mechanism.split()) if answer.mechanism else 0
        if mechanism_words < 100:  # Should be brief
            score += 0.10
        max_points += 0.10

        # 20% of score: Measurement approach clear
        if "measurement" in answer.actionability_section.lower() or "KPI" in answer.actionability_section:
            score += 0.20
        max_points += 0.20

        # 20% of score: Credence expressed as percentage, not "supported by evidence"
        if "% confident" in answer.uncertainty_expressed or "credence" in answer.uncertainty_expressed:
            score += 0.20
        max_points += 0.20

    elif user_type == UserTypeID.RESEARCHER:
        # Similar but different criteria
        max_points += 1.0
        # Check for effect sizes, heterogeneity, publication bias, etc.
        score += _score_researcher_answer(answer)

    # ... and so on for other types

    return score / max_points if max_points > 0 else 0.0
```

**Success Metric 2: User Satisfaction (A/B Testing)**

- Ask users (after seeing answer): "How well did this answer match your needs?"
- Measure difference between personalized and generic answers
- Target: Personalized answers score 15–25% higher on satisfaction

**Success Metric 3: Differentiation Score**

Measure that answers are genuinely different, not just reformatted:

```python
def differentiation_score(query: str) -> float:
    """
    Generate answers to same query for all 5 user types.
    Measure structural and content differences.
    """
    answers = {}
    for user_type in UserTypeID:
        answers[user_type] = generate_answer(query, user_type)

    # Compute pairwise cosine similarity on answer embeddings
    differences = []
    types_list = list(UserTypeID)
    for i, type_a in enumerate(types_list):
        for type_b in types_list[i+1:]:
            sim = cosine_similarity(
                embed(answers[type_a].to_text()),
                embed(answers[type_b].to_text())
            )
            differences.append(1 - sim)  # Higher = more different

    # Average difference
    avg_diff = sum(differences) / len(differences)

    # Target: average cosine distance > 0.3 (fairly different)
    return avg_diff
```

**Success Metric 4: Epistemic Integrity Audit**

Randomly sample answers and check guardrails:

```python
def audit_epistemic_integrity(
    answer: TypedAnswer,
    user_type: UserTypeID
) -> Dict[str, bool]:
    """
    Audit answer against epistemic guardrails.
    """
    checks = {
        "no_misrepresentation": (
            answer.confidence_reasoning and
            not _overconfident(answer) and
            "caveat" in answer.to_text().lower() or answer.caveat_count > 0
        ),
        "evidence_quality_disclosed": (
            answer.evidence_summary and
            ("RCT" in answer.evidence_summary or "observational" in answer.evidence_summary)
        ),
        "scope_conditions_present": len(answer.scope_conditions) > 0,
        "individual_differences_noted": (
            "individual" in answer.to_text().lower() or
            "population" in answer.to_text().lower()
        ),
        "competing_explanations_named": (
            "mechanism" in answer.to_text().lower() or
            "debate" in answer.to_text().lower() or
            answer.competing_theories > 0
        ),
    }

    return checks
```

---

## Part F: Implementation Roadmap

### Phase 1: Data Structure Definition (Week 1)
- [ ] Define `UserProfile`, `TypedAnswer`, design parameter data structures
- [ ] Create `UserTypeID` enum and profiles for all 5 types
- [ ] Version and commit to codebase

### Phase 2: Handler Architecture (Weeks 2–3)
- [ ] Extend `ArbitraryQAHandler` with type-aware routing
- [ ] Create `TypeSpecificHandlers` class with handlers per question type
- [ ] Implement for 3 primary question types: MECHANISM, EVIDENCE_FOR, SCOPE
- [ ] Add fallback for generic answers (backward compatibility)

### Phase 3: Response Generation (Weeks 4–5)
- [ ] Implement architect handler (design parameters + scope)
- [ ] Implement researcher handler (effect sizes + heterogeneity)
- [ ] Implement student handler (theory + learning path)
- [ ] Implement reviewer handler (exportable study data)
- [ ] Implement quick lookup handler (headline + credence)

### Phase 4: Integration (Week 6)
- [ ] Update `1_query.py` to pass user type through request
- [ ] Update `api_client.py` to handle personalized responses
- [ ] Update frontend to show personalization indicator
- [ ] Test end-to-end query → response

### Phase 5: Testing & Validation (Week 7)
- [ ] Run test cases (Part E: Test Criteria)
- [ ] Score answer appropriateness per type
- [ ] Audit epistemic integrity
- [ ] Measure differentiation (answers actually differ)
- [ ] Fix failures and iterate

### Phase 6: Evaluation (Weeks 8+)
- [ ] A/B test: personalized vs generic (user satisfaction)
- [ ] Gather user feedback per type
- [ ] Refine profiles based on feedback
- [ ] Document learned patterns in DECISIONS_LOG.md

---

## Code Snippets for Implementation

### Snippet 1: User Profile Enumeration

```python
# src/services/user_personalization.py

from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

class UserTypeID(Enum):
    """Canonical user type identifiers."""
    ARCHITECT = "architect"
    RESEARCHER = "researcher"
    STUDENT = "student"
    REVIEWER = "reviewer"
    QUICK_LOOKUP = "quick_lookup"

@dataclass
class DesignParameter:
    """Actionable design specification."""
    parameter_name: str
    recommended_range: Tuple[float, float]
    unit: str
    evidence_level: str  # "High", "Moderate", "Low"
    population_scope: dict  # {"office": 0.38, "hospital": 0.25}
    trade_offs: List[str]
    measurement_approach: str
    contraindications: List[str]

    def to_text(self) -> str:
        """Format as human-readable text."""
        return f"{self.parameter_name}: {self.recommended_range[0]}–{self.recommended_range[1]} {self.unit}"

@dataclass
class TypedAnswer:
    """Answer customized for a user type."""
    user_type_id: UserTypeID
    headline: Optional[str]
    design_parameters: Optional[List[DesignParameter]]
    mechanism: Optional[str]
    theory_explanation: Optional[str]
    effect_sizes: Optional[dict]
    study_data: Optional[List[dict]]
    evidence_summary: str
    scope_conditions: List[str]
    actionability_section: str
    uncertainty_expressed: str
    citations: List[str]
    answer_completeness: float
    sources_used: List[str]
    confidence_reasoning: str

    def to_text(self, **opts) -> str:
        """Render to readable text per type."""
        if self.user_type_id == UserTypeID.QUICK_LOOKUP:
            return self._render_quick_lookup()
        elif self.user_type_id == UserTypeID.ARCHITECT:
            return self._render_architect()
        elif self.user_type_id == UserTypeID.RESEARCHER:
            return self._render_researcher()
        # ... and so on

    def _render_quick_lookup(self) -> str:
        """Render quick lookup answer (<100 words)."""
        lines = []
        if self.headline:
            lines.append(f"**{self.headline}**")
        lines.append(f"*Confidence: {self.uncertainty_expressed}*")
        if self.mechanism:
            lines.append(f"Why: {self.mechanism[:80]}...")
        if self.scope_conditions:
            lines.append(f"Scope: {self.scope_conditions[0]}")
        if self.confidence_reasoning:
            lines.append(f"Caveat: {self.confidence_reasoning[:80]}...")
        return "\n\n".join(lines)

    def _render_architect(self) -> str:
        """Render architect answer (design parameters first)."""
        lines = []
        if self.design_parameters:
            lines.append("## Design Parameters")
            for dp in self.design_parameters:
                lines.append(f"- {dp.to_text()} (Evidence: {dp.evidence_level})")
        lines.append("\n## Scope of Applicability")
        lines.extend([f"- {sc}" for sc in self.scope_conditions[:3]])
        lines.append(f"\n## Evidence Strength")
        lines.append(self.evidence_summary)
        lines.append(f"\n## How to Measure Success")
        lines.append(self.actionability_section)
        lines.append(f"\n## Confidence: {self.uncertainty_expressed}")
        return "\n".join(lines)

    # ... more render methods

    def to_json(self) -> dict:
        """Serialize to JSON for API."""
        return {
            "user_type": self.user_type_id.value,
            "headline": self.headline,
            "evidence_summary": self.evidence_summary,
            "scope_conditions": self.scope_conditions,
            "uncertainty": self.uncertainty_expressed,
            "design_parameters": [asdict(dp) for dp in (self.design_parameters or [])],
            "completeness": self.answer_completeness,
        }
```

### Snippet 2: Type-Specific Handler

```python
# src/services/type_specific_handlers.py

class TypeSpecificHandlers:
    """Generate type-specific answers."""

    def handle_mechanism_question(
        self,
        query: str,
        user_type: UserTypeID,
        evidence_base: dict
    ) -> TypedAnswer:
        """
        Route "How does X cause Y?" questions based on user type.
        """
        base_mechanism = self._extract_mechanism(query, evidence_base)
        effect_data = evidence_base.get("effect_data", {})

        if user_type == UserTypeID.ARCHITECT:
            return self._architect_mechanism(
                query, base_mechanism, effect_data
            )
        elif user_type == UserTypeID.RESEARCHER:
            return self._researcher_mechanism(
                query, base_mechanism, effect_data
            )
        elif user_type == UserTypeID.STUDENT:
            return self._student_mechanism(
                query, base_mechanism, effect_data
            )
        elif user_type == UserTypeID.REVIEWER:
            return self._reviewer_mechanism(
                query, base_mechanism, effect_data
            )
        else:  # QUICK_LOOKUP
            return self._quick_mechanism(
                query, base_mechanism, effect_data
            )

    def _architect_mechanism(
        self,
        query: str,
        mechanism: str,
        effect_data: dict
    ) -> TypedAnswer:
        """Architect: mechanism → design implications."""
        # Extract the key mechanism
        mechanism_text = mechanism  # Keep brief

        # Translate to design parameters
        design_params = self._extract_design_parameters(mechanism, effect_data)

        # Get scope from effect_data
        scope = self._get_scope_conditions(effect_data, "office_workers")

        # Actionability: what should they do?
        actionable = self._make_actionable(design_params, scope)

        return TypedAnswer(
            user_type_id=UserTypeID.ARCHITECT,
            headline=f"Design guidance for: {query}",
            design_parameters=design_params,
            mechanism=mechanism_text[:150],  # Brief only
            theory_explanation=None,
            effect_sizes=None,
            study_data=None,
            evidence_summary=effect_data.get("summary", ""),
            scope_conditions=scope,
            actionability_section=actionable,
            uncertainty_expressed=self._express_credence_architect(effect_data),
            citations=effect_data.get("citations", []),
            answer_completeness=self._compute_completeness(
                UserTypeID.ARCHITECT,
                design_params, scope, actionable
            ),
            sources_used=effect_data.get("sources", []),
            confidence_reasoning=effect_data.get("confidence_reasoning", ""),
        )

    def _researcher_mechanism(
        self,
        query: str,
        mechanism: str,
        effect_data: dict
    ) -> TypedAnswer:
        """Researcher: full mechanism + evidence quality."""
        # Deep mechanism explanation
        mechanism_text = mechanism  # Keep full

        # Effect sizes with CI, heterogeneity, etc.
        effect_sizes = self._extract_effect_sizes(effect_data)

        # Competing mechanisms
        competitors = effect_data.get("competing_mechanisms", [])
        mechanism_discussion = self._discuss_mechanisms(
            mechanism_text, competitors, effect_sizes
        )

        # Research gaps
        gaps = effect_data.get("research_gaps", [])

        return TypedAnswer(
            user_type_id=UserTypeID.RESEARCHER,
            headline=f"Mechanism research: {query}",
            design_parameters=None,
            mechanism=mechanism_discussion,
            theory_explanation=None,
            effect_sizes=effect_sizes,
            study_data=None,
            evidence_summary=self._detailed_evidence_summary(effect_data),
            scope_conditions=self._get_scope_with_heterogeneity(effect_data),
            actionability_section=self._research_recommendations(gaps),
            uncertainty_expressed=self._express_credence_researcher(effect_data),
            citations=effect_data.get("citations_with_dois", []),
            answer_completeness=1.0,  # Researchers expect completeness
            sources_used=effect_data.get("sources", []),
            confidence_reasoning=effect_data.get("confidence_reasoning_detailed", ""),
        )

    def _student_mechanism(
        self,
        query: str,
        mechanism: str,
        effect_data: dict
    ) -> TypedAnswer:
        """Student: foundational theory + learning path."""
        # Theory explanation
        theories = effect_data.get("theories", [])
        theory_text = self._explain_theories(theories)

        # Historical context
        history = effect_data.get("historical_context", "")

        # Learning path
        key_papers = effect_data.get("landmark_papers", [])
        learning_path = self._create_learning_path(key_papers)

        # Learning questions
        learning_qs = effect_data.get("learning_questions", [])

        return TypedAnswer(
            user_type_id=UserTypeID.STUDENT,
            headline=f"Learning: {query}",
            design_parameters=None,
            mechanism=mechanism[:300],  # Explain the mechanism
            theory_explanation=theory_text,
            effect_sizes=None,
            study_data=None,
            evidence_summary=f"{history}\n\n{learning_path}",
            scope_conditions=[f"Applies to: {s}" for s in effect_data.get("populations", [])[:3]],
            actionability_section=self._next_learning_steps(learning_qs),
            uncertainty_expressed=self._express_credence_student(effect_data),
            citations=key_papers,
            answer_completeness=0.8,  # Students want depth but not everything
            sources_used=effect_data.get("sources", []),
            confidence_reasoning=f"Field consensus: {effect_data.get('consensus', '')}",
        )

    def _reviewer_mechanism(
        self,
        query: str,
        mechanism: str,
        effect_data: dict
    ) -> TypedAnswer:
        """Reviewer: structured, exportable data."""
        # Study-by-study data
        studies = effect_data.get("studies", [])
        study_data = self._format_for_export(studies)

        # GRADE assessments
        grade_data = effect_data.get("grade_assessments", {})

        return TypedAnswer(
            user_type_id=UserTypeID.REVIEWER,
            headline=f"Systematic review data: {query}",
            design_parameters=None,
            mechanism=None,
            theory_explanation=None,
            effect_sizes=effect_data.get("meta_effect_sizes", {}),
            study_data=study_data,  # Exportable table
            evidence_summary=f"Studies: {len(studies)}; GRADE: {grade_data}",
            scope_conditions=self._subgroup_analyses(effect_data),
            actionability_section=self._meta_analysis_guidance(effect_data),
            uncertainty_expressed=f"GRADE certainty: {grade_data.get('overall', '')}",
            citations=self._format_for_bibtex(studies),
            answer_completeness=1.0,  # Must be complete for SR
            sources_used=[],
            confidence_reasoning=f"Bias assessment: {effect_data.get('publication_bias', '')}",
        )

    def _quick_mechanism(
        self,
        query: str,
        mechanism: str,
        effect_data: dict
    ) -> TypedAnswer:
        """Quick lookup: headline + one sentence each."""
        return TypedAnswer(
            user_type_id=UserTypeID.QUICK_LOOKUP,
            headline=self._one_sentence_answer(query, effect_data),
            design_parameters=None,
            mechanism=mechanism[:60] + "...",  # One sentence
            theory_explanation=None,
            effect_sizes=None,
            study_data=None,
            evidence_summary=f"{effect_data.get('study_count', '?')} studies",
            scope_conditions=[effect_data.get('scope_one_liner', '')],
            actionability_section=effect_data.get('quick_recommendation', ''),
            uncertainty_expressed=self._express_credence_quick(effect_data),
            citations=[],
            answer_completeness=0.6,  # Quick lookup is intentionally incomplete
            sources_used=[],
            confidence_reasoning=effect_data.get('quick_caveat', ''),
        )

    # Helper methods...
    def _express_credence_architect(self, effect_data: dict) -> str:
        """Express credence as percentage with scope variance."""
        credence = effect_data.get("credence_point", 0.65)
        scope_var = effect_data.get("scope_variance", 0.10)
        return (
            f"{int(credence*100)}% confident. "
            f"Stronger in offices ({int((credence+scope_var)*100)}%), "
            f"weaker in homes ({int((credence-scope_var)*100)}%)"
        )

    def _express_credence_researcher(self, effect_data: dict) -> str:
        """Express credence as interval with bias and heterogeneity."""
        low = effect_data.get("credence_low", 0.55)
        high = effect_data.get("credence_high", 0.75)
        bias = effect_data.get("publication_bias_inflation", 0.10)
        het = effect_data.get("heterogeneity_i2", 0.5)
        return (
            f"{int(low*100)}–{int(high*100)}% credence. "
            f"Publication bias likely inflates by {int(bias*100)}%; "
            f"heterogeneity I² = {int(het*100)}%"
        )

    def _express_credence_student(self, effect_data: dict) -> str:
        """Express credence verbally with reason."""
        credence = effect_data.get("credence_point", 0.65)
        reason = effect_data.get("credence_reason", "")
        if credence > 0.75:
            label = "Well-established"
        elif credence > 0.60:
            label = "Fairly well-supported"
        elif credence > 0.50:
            label = "Moderate evidence"
        else:
            label = "Emerging but not settled"
        return f"{label}. {reason}"

    def _express_credence_quick(self, effect_data: dict) -> str:
        """Express credence as simple label."""
        credence = effect_data.get("credence_point", 0.65)
        if credence >= 0.75:
            return "High confidence"
        elif credence >= 0.60:
            return "Moderate confidence"
        elif credence >= 0.45:
            return "Low confidence"
        else:
            return "Very low confidence"
```

---

## Conclusion

This specification transforms the QA system's user-type personalization from cosmetic to fundamental. Each user type now receives answers genuinely structured, deepened, and focused for their needs—while maintaining epistemic integrity across all variations.

The implementation roadmap spans 8 weeks and integrates with existing infrastructure (`ArbitraryQAHandler`, `integrated_query_service`). The test criteria (Part E) ensure that personalization is measurable and that no simplification compromises the evidence's integrity.

---

**Document History**:
- **2026-03-02**: Initial specification; expert panel deliberation complete; implementation roadmap defined

**Next Steps**:
1. Panel review and feedback
2. Prioritize which question types to personalize first
3. Begin Phase 1 (data structures) immediately
4. Create DECISIONS_LOG.md to track implementation choices

