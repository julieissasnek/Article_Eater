# ADVERSARIAL EXPERT REVIEW: ARTICLE EATER SYSTEM
## Run this prompt inside the repo. Read everything. Hold nothing sacred.

---

You are a panel of seven world-class experts convened to conduct a brutally honest review of this software system. You have been retained precisely because you have no loyalty to the project, no investment in its success, and no incentive to be polite. Your job is to find what's broken, what's fake, what's confused, and what's good — in that order.

The system claims to be a comprehensive framework for evaluating how architectural design affects human wellbeing, grounded in predictive processing theory and operationalized through mechanistic templates, a web of belief, and dual evaluation pipelines (paper assessment and building assessment). It has been under development for several months by a professor of cognitive science and multiple AI agents.

You have full access to the repository. Read the code, the data, the documentation, the templates, the tests, the databases. Leave no file unexamined that matters.

---

## YOUR PANEL

You will write your review as seven distinct expert voices. Each expert writes their own section. They disagree with each other where warranted. They are specific — they cite files, line numbers, function names, data values. They do not speak in generalities.

### Expert 1: COMPUTATIONAL EPISTEMOLOGIST
*Specialization: formal epistemology, belief revision, coherence theory, Bayesian networks*

Your questions:
- Does the "web of belief" actually implement coherentism, or is it just a graph database with the word "belief" in the column names? Examine src/services/web_of_belief.py, web_persistence.py, epistemic_causal_bridge.py, and the actual beliefs/constraints tables. Is there a real coherence measure or just a formula that produces a number?
- Does the Bayesian updating (if any) follow actual Bayesian principles? Are the priors justified? Are the likelihoods calibrated? Or is this "Bayesian" in the way that marketing departments use the word?
- The system has "entrenchment" scores. Does entrenchment follow anything like Quine's web of belief, Harman's conservative principles, or Levi's epistemic utilities? Or is it a made-up metric?
- The "credence" values on beliefs — are they genuine subjective probabilities that obey the probability axioms, or are they confidence scores wearing a philosophical costume?
- The bridge warrants between domains — do they have any epistemic justification, or are they just "these two things seem related"?

### Expert 2: SOFTWARE ARCHITECT
*Specialization: production systems, API design, data pipelines, technical debt*

Your questions:
- Can this system actually run end-to-end on a new paper or building that wasn't in the test suite? Try it. Pick a paper DOI not in the test data. Feed it through. What happens?
- How much of the codebase is real computation vs placeholder/stub/TODO? Search for `pass`, `TODO`, `FIXME`, `placeholder`, `NotImplementedError`, `raise NotImplementedError`, default return values, hardcoded 50.0, hardcoded 0.5. Quantify.
- The template computation functions — do they actually COMPUTE something from inputs, or do they return a default? Trace the call from `evaluate_building()` through template activation to WIS score. Show me where real math happens (or doesn't).
- How many of the 150 templates have actual compute functions vs being data-only JSON files that are never executed?
- Test coverage: what percentage of the codebase has tests? What percentage of the tests are meaningful vs testing that True == True?
- Database integrity: are there orphaned records, broken foreign keys, tables that exist in the schema but are never written to? You saw the DB — many tables have 0 rows. Why do they exist?
- Dependency hell: how many packages are imported but never used? How many are pinned to versions? Could this run on a fresh machine?

### Expert 3: RESEARCH METHODOLOGIST / PSYCHOMETRICIAN
*Specialization: meta-analysis, effect size estimation, measurement validity, statistical inference*

Your questions:
- The WIS (Wellbeing Impact Score) — what IS it? Is it a validated psychometric construct, or did someone make up a 0-100 scale and call it a score? What does WIS = 50 mean? What does WIS = 70 mean? Is there any evidence that the difference between 50 and 70 corresponds to a real difference in human wellbeing?
- The template parameters (priors, effect sizes, confidence intervals) — where did the NUMBERS come from? Are they from meta-analyses? Expert elicitation? Or are they defaults that were never updated? Examine the actual JSON files in data/templates/. How many have `prior_confidence: 0.85` or similar suspiciously round numbers?
- The effect size conversion (Sprint D is building this) — is there awareness that converting between effect size metrics introduces systematic biases? F to d is only valid for one-df contrasts. β to d assumes bivariate normality. r to d assumes equal groups. Are these assumptions documented?
- The domain aggregation (geometric mean across domains) — why geometric mean? Is there any psychometric justification, or is it because geometric mean "sounds sophisticated"? What happens when one domain has WIS=0? The geometric mean goes to zero. Is that intended?
- The lifespan moderation (age_band_modifiers in the templates) — where do these multipliers come from? If `toddler_0_3.vision = 0.7` for template AX1, what study established that toddlers have 70% of adult sensitivity to this mechanism? These look like guesses presented as data.
- The calibration panels (Docs 56-63) — are these real calibrations with empirical data, or are they "expert panels" of AI agents agreeing with each other? If the latter, this is not calibration. It is confabulation with extra steps.

### Expert 4: COGNITIVE SCIENTIST / NEUROSCIENTIST
*Specialization: predictive processing, perception, environmental psychology, embodied cognition*

Your questions:
- Does the system's use of "predictive processing" go beyond using the words "prediction error"? Read the templates. Do they actually model prediction, error signals, precision weighting, and belief updating? Or do they use PP vocabulary to describe ordinary stimulus-response relationships?
- The causal chains in the templates (environmental → neural → affective → behavioral) — are these real multi-level mechanisms, or are they just "X causes Y causes Z" chains with neuroscience words in the middle? For a system claiming to be mechanistic, where are the MECHANISMS? Can any template actually predict the MAGNITUDE of an effect from first principles?
- The "dual pathway" discovery (image-forming vs non-visual for light, discriminative vs affective for touch) — is this genuine theoretical insight, or is it restating textbook neuroscience as if it were novel?
- The theory reductions (ART → templates, SRT → templates, Biophilia → templates) — are these genuine intertheoretic reductions in the philosophy of science sense, or are they just "this concept from Theory X maps loosely onto this template"? A real reduction explains WHY the higher-level theory works in terms of lower-level mechanisms. Does this system do that?
- Examine the specific template for a domain you know well (pick any: light, sound, thermal, nature views). Is the mechanistic story correct? Are the key references real and do they support the claimed mechanism? Are important competing explanations acknowledged?

### Expert 5: PRACTICING ARCHITECT / BUILDING SCIENTIST
*Specialization: evidence-based design, post-occupancy evaluation, building performance*

Your questions:
- Run the building evaluation on three buildings you know: (a) a typical open-plan office, (b) a hospital patient room with a window, (c) a school classroom. Do the results make sense? Do they capture what any competent architect would know about these spaces?
- The input features the system requires (ceiling_height_m, illuminance_lux, ambient_noise_dba, etc.) — are these things an architect would actually HAVE for a building under design? A building that hasn't been built yet doesn't have measured lux values. How does the system handle design-phase evaluation?
- The "practical accessibility" ratings (A through D) on templates — do these correspond to reality? If template X is rated "A" (no equipment needed), can you actually assess it without instruments?
- The system claims to handle 10 architectural domains. Do they cover what matters? What's MISSING? Ventilation/air quality? Thermal mass? Acoustic privacy vs acoustic quality? Wayfinding at the urban scale? Biophilic elements beyond nature views?
- The WIS scoring at the building level — would this score be useful to an architect making actual design decisions? Or is it too abstract? Does the system tell you WHAT TO CHANGE to improve the score?

### Expert 6: DATA ENGINEER / ML OPS
*Specialization: data pipelines, ETL, data quality, production ML systems*

Your questions:
- The PDF extraction pipeline (the 171k-row CSV) — Doc 70 says it's garbage. Verify this independently. Sample 50 random rows. How many contain real scientific claims? Is Doc 70's 7%/93% split accurate, and is the 7% really garbage too?
- The web of belief rebuild (Sprint D, Task D.11) — is the proposed rebuild architecture sound? Will it actually produce a better web, or will it just produce a smaller web with different problems?
- Data lineage: for any given WIS score that the system produces, can you trace backward to the specific evidence (paper, table, finding) that justifies it? If not, the system is not auditable.
- The vocabulary sheet (Sprint D, Task D.1) — is the proposed IV/DV vocabulary comprehensive enough? What important variables in the environmental psychology literature are missing? What variables are included that shouldn't be (too vague, not measurable, not architectural)?
- Database architecture: is SQLite the right choice for a system with 83 MB of data and multiple concurrent agents? Are there locking issues? Should this be PostgreSQL?
- The system has TWO databases (ae.db and web_persistence.db) that should arguably be one. What's the migration path?

### Expert 7: PHILOSOPHY OF SCIENCE / THEORY ASSESSMENT
*Specialization: scientific theories, explanation, reduction, theory change*

Your questions:
- What is the system's THEORY? Not its software architecture — its substantive intellectual claim about how built environments affect human wellbeing. State it precisely. Then evaluate: is it testable? Is it falsifiable? What would COUNT as evidence against it?
- The predictive processing framework — is it doing genuine theoretical work here, or is it a "theory of everything" that predicts everything and therefore nothing? PP theory is famously flexible. Does the system constrain PP's predictions in any way?
- The template system claims to be "mechanistic." But a mechanism, in philosophy of science, is a specific organized arrangement of entities and activities that produces a phenomenon (Machamer, Darden, Craver 2000). Do the templates specify mechanisms at this level of detail, or are they black boxes with inputs and outputs?
- The inter-template interactions — do they model actual mechanistic interactions (competition for shared neural resources, synergistic activation patterns), or are they just additive/multiplicative adjustments with no mechanistic justification?
- The "star rating" system for evidence quality (★ to ★★★★) — what are the criteria? Do they correspond to established evidence grading frameworks (GRADE, Oxford Centre for EBM levels, Campbell Collaboration)? Or is this a bespoke system?
- Most ambitiously: does this system actually ADVANCE KNOWLEDGE? Could it discover something that wasn't already known? Or does it just formalize existing knowledge in a more complicated wrapper?

---

## END-TO-END EFFECTIVENESS TESTS

Before writing your reviews, the panel MUST execute these concrete tests. Document every step, every output, every failure. These are not thought experiments — run the code.

### Test A: New Paper Evaluation (never seen by the system)

Pick a real paper NOT in the corpus. Suggestions:
- Yin et al. (2018) "Effects of biophilic indoor environment on stress and anxiety recovery" (doi:10.1016/j.envint.2018.04.028)
- Kwallek et al. (2007) "Work week productivity, visual complexity, and individual environmental sensitivity in three offices" (doi:10.1016/j.envint.2006.06.017)
- Shibata & Suzuki (2004) "Effects of an indoor plant on creative task performance and mood" (doi:10.1111/j.1467-9450.2004.00444.x)

For the selected paper:
1. Manually create 3-5 structured claims from the paper's findings (iv, dv, direction, effect_size, sample_n)
2. Feed them through `process_paper()` in `src/cmr/process_paper.py`
3. Document: Did it match to correct templates? Did it identify the right direction? Did the VOI score make sense? Did it generate update proposals? How long did it take?
4. Now try feeding the paper's RAW text (not structured claims). What happens?

### Test B: Building Evaluation — Three Real Buildings

Run `evaluate_building()` from `src/cmr/building_eval.py` on these three cases:

**Case 1: A good building — Maggie's Centre, Dundee (Frank Gehry)**
```python
building_context = {"building_type": "healthcare", "climate_zone": "4A", "building_name": "Maggie's Centre Dundee"}
measured_features = {
    "ceiling_height_m": 4.5, "floor_area_m2": 280, "illuminance_lux": 500,
    "ambient_noise_dba": 35, "has_nature_view": True, "view_content": "garden",
    "natural_material_ratio": 0.6, "cct_kelvin": 4000,
    "has_daylight_variation": True, "visual_privacy_score": 0.7
}
occupant_profile = {"age": 55, "cultural_context": "Western"}
```
Expected: HIGH WIS. This is an award-winning therapeutic environment.

**Case 2: A bad building — windowless basement office**
```python
building_context = {"building_type": "office", "climate_zone": "4A", "building_name": "Generic Basement Office"}
measured_features = {
    "ceiling_height_m": 2.4, "floor_area_m2": 200, "illuminance_lux": 200,
    "ambient_noise_dba": 55, "has_nature_view": False, "view_content": "none",
    "natural_material_ratio": 0.0, "cct_kelvin": 6500,
    "has_daylight_variation": False, "visual_privacy_score": 0.2
}
occupant_profile = {"age": 35, "cultural_context": "Western"}
```
Expected: LOW WIS. No daylight, no view, noisy, low ceilings, no natural materials.

**Case 3: A mixed building — typical open-plan tech office**
```python
building_context = {"building_type": "office", "climate_zone": "3C", "building_name": "Typical Tech Office"}
measured_features = {
    "ceiling_height_m": 3.0, "floor_area_m2": 500, "illuminance_lux": 400,
    "ambient_noise_dba": 48, "has_nature_view": True, "view_content": "urban_park",
    "natural_material_ratio": 0.15, "cct_kelvin": 4500,
    "has_daylight_variation": True, "shared_area_ratio": 0.8,
    "phone_booths_per_worker": 0.05, "visual_privacy_score": 0.15
}
occupant_profile = {"age": 30, "cultural_context": "Western"}
```
Expected: MIXED WIS. Good light and views, but terrible privacy and acoustic conditions. The system should show high scores in light/nature domains and low scores in social/acoustic domains. If it returns the same WIS for all three buildings, it is broken.

**For all three cases, document:**
- Does it run without errors?
- Does the overall WIS discriminate between buildings? (If all three return 50.0, the system is not functional.)
- Do the domain-level scores make sense? (Light should be high for Maggie's, low for the basement.)
- Does the report tell you WHAT's wrong and HOW to fix it?
- How long does evaluation take?

### Test C: Sensitivity Check

Take Case 1 (Maggie's Centre) and change ONE input at a time:
- Set `has_nature_view: False` — does WIS drop? By how much?
- Set `ceiling_height_m: 2.4` — does WIS drop?
- Set `ambient_noise_dba: 65` — does WIS drop?
- Set `illuminance_lux: 50` — does WIS drop?

If changing inputs does NOT change the WIS, the template computation is not wired. If it changes by exactly the same amount regardless of which input, the computation is probably a linear placeholder.

### Test D: The Ulrich Test (known-good paper)

The system has been tested on Ulrich (1984). Run it again:
```python
claims = [
    {"iv": "has_nature_view", "dv": "recovery_time", "direction": "decrease", "effect_size": 0.71, "sample_n": 46},
    {"iv": "has_nature_view", "dv": "pain_medication_use", "direction": "decrease", "effect_size": 0.50, "sample_n": 46}
]
```
Verify it matches VIEW1. Check the update proposals. This is the baseline — if THIS doesn't work, nothing does.

---

## USER-CENTERED EVALUATION

The system is useless if nobody can use it. Evaluate against five concrete user types. For each, walk through their actual workflow step by step and identify every point where the system fails them.

### User 1: THE PRACTICING ARCHITECT
*Sarah, 15 years experience, designing a new pediatric hospital wing*

Sarah's questions:
- "I'm at schematic design. I haven't chosen materials or lighting fixtures yet. Can the system tell me what MATTERS MOST for child patients aged 4-12?" → Does the system support design-phase queries when you only know building_type and occupant_profile, not measured_features?
- "My client wants me to justify the cost of floor-to-ceiling windows in patient rooms. Can this system give me evidence I can put in a presentation?" → Does the paper evaluation produce citable evidence summaries? Are the citations real and findable?
- "I want to compare two design options: courtyard layout vs linear corridor. How do I input spatial configuration?" → Are the input variables things an architect actually controls? Or are they post-occupancy measurements?
- "I designed the building. Now it's built. The client wants a post-occupancy evaluation. Can this system structure the POE?" → Does the system bridge from design-phase assessment to post-occupancy measurement?

**Evaluate:** What percentage of Sarah's workflow can the system actually support TODAY? What would need to change?

### User 2: THE RESEARCHER
*Dr. Chen, environmental psychology PhD, conducting a meta-analysis on daylight and cognitive performance*

Dr. Chen's questions:
- "I want to find all papers in the system's database that study daylight → cognitive outcomes." → Can the system query by IV/DV pair and return a list of papers with effect sizes? Or does it only evaluate one paper at a time?
- "I want to see the system's current 'state of knowledge' about daylight effects — the aggregated evidence across all processed papers." → Does the web of belief support queries like "show me all beliefs about illuminance_lux"?
- "I found a new paper that contradicts the existing evidence. I want to see how integrating it changes the system's confidence." → Does the paper eval pipeline show before/after credence? Does it flag the contradiction clearly?
- "The system says daylight has effect size d=0.4 on attention. I want to know: which studies does that come from? What's the heterogeneity? Are there moderators?" → Is there a provenance trail from aggregated parameters back to individual study findings?

**Evaluate:** Can a researcher use this as a living systematic review tool? Or is it a one-way pipeline that ingests papers but can't be queried?

### User 3: THE POLICY MAKER
*James, senior advisor at a municipal planning department, writing new building codes*

James's questions:
- "We're considering mandating minimum daylight requirements in schools. What evidence level supports this?" → Can the system produce a policy brief? Does it distinguish between strong evidence (multiple RCTs) and weak evidence (case studies)?
- "I need to know the cost-benefit: how much does adding nature views to hospital rooms save in reduced recovery time and medication?" → Does the system connect to any cost data, or is it purely about effect sizes?
- "I need results I can present to a city council. They need plain English, not p-values." → Does the architect-facing report (Sprint 12, Task 12.8) actually exist? Is it readable by non-scientists?

**Evaluate:** Could the system's outputs survive scrutiny in a policy hearing? Or are they too hedged, too technical, or too vague?

### User 4: THE BUILDING DEVELOPER
*Maria, VP of Design at a commercial real estate firm, evaluating 3 buildings for acquisition*

Maria's questions:
- "Give me a single number I can compare across buildings." → Does the overall WIS serve this purpose? Is it stable enough across evaluations that you'd make a $50M decision based on it?
- "I don't have detailed measurements for these buildings yet. I have floor plans and photos. What can you tell me?" → How much can the system do with limited input data? Does it gracefully degrade, or does it require complete feature vectors?
- "One building scored 62, another scored 58. Is that difference meaningful?" → Does the system report confidence intervals? Can it say "these two buildings are not significantly different"?

**Evaluate:** Is the WIS actionable for business decisions? Or is it a research prototype that would embarrass itself in a commercial context?

### User 5: THE STUDENT / NEWCOMER
*Alex, graduate student in architecture, learning about evidence-based design*

Alex's questions:
- "I want to understand HOW the system works. Is there a tutorial? An example walkthrough?" → Does documentation exist for someone who wasn't part of the development?
- "I want to evaluate my thesis project — a co-working space. Can I follow a step-by-step process?" → Is there a user-facing workflow, or do you need to write Python?
- "I read a paper in class about prospect-refuge theory. Does the system include this? Where?" → Can a student navigate from a theory name to the relevant templates, evidence, and mechanisms?

**Evaluate:** Is the system learnable? Is there any on-ramp for someone who didn't build it?

---

## REVIEW PROCEDURE

1. **Read the architecture documents first:** Look in `docs/` for anything labeled "Doc" with a number — these are the project's intellectual history. Pay special attention to: Doc 67 (sprint plan), Doc 68 (CMR contract), Doc 69 (methodology), Doc 70 (data diagnosis). Also read any README, ARCHITECTURE, or overview documents.

2. **Read the template system:** Examine `data/templates/*.json` — sample at least 15 templates from different domains. Read the causal_links, key_references, scope_conditions, and moderators. Are these real science or plausible-sounding fabrication?

3. **Read the core code paths:** Trace through:
   - Paper evaluation: `src/cmr/paper_eval.py` → `claim_extraction.py` → `template_matching.py`
   - Building evaluation: `src/cmr/building_eval.py` → `feature_mapping.py` → template computation
   - Web of belief: `src/services/web_of_belief.py` → `web_persistence.py`
   - Theory reduction: wherever ART/SRT/Biophilia reduction logic lives

4. **Run the system:** If possible, execute the test suite. Try to evaluate a building. Try to evaluate a paper. Record what works and what doesn't.

5. **Examine the data:** Look at `data/production/realtime_pdf_confirmed_rows.csv` (sample — it's 154 MB). Look at the SQLite databases. Look at the gold standard files if they exist yet.

6. **Write your review:** Each expert writes 500-1500 words. Be specific. Cite files and line numbers. Distinguish between: (a) things that are WRONG (bugs, logical errors, false claims), (b) things that are MISSING (gaps, incomplete implementations), (c) things that are QUESTIONABLE (design choices that may or may not be defensible), and (d) things that are GOOD (genuinely impressive, well-designed, or scientifically sound).

---

## OUTPUT FORMAT

Produce a single document: `docs/adversarial_review_report.md`

Structure:
1. **Executive Summary** (500 words): The overall verdict. What is this system, really? Is it what it claims to be?
2. **End-to-End Test Results**: Tests A through D, with exact inputs, outputs, timings, and pass/fail.
3. **Expert 1 Review** through **Expert 7 Review**: Each expert's section.
4. **User-Centered Evaluation**: For each of the five user types, a workflow walkthrough showing exactly where the system succeeds and fails. Include a SUPPORT MATRIX:

```
                    Architect  Researcher  Policy  Developer  Student
Design-phase eval      ?          -          -        ?         ?
Paper processing       -          ?          -        -         ?
Evidence query         -          ?          ?        -         ?
Building comparison    ?          -          -        ?         -
Report generation      ?          ?          ?        ?         -
Provenance trail       -          ?          ?        -         ?
Tutorial/onboarding    -          -          -        -         ?

✅ = works today  ⚠️ = partially works  ❌ = broken/missing  - = not relevant
```

5. **Cross-Expert Agreements**: Where do multiple experts converge on the same problem?
6. **The Good**: What genuinely works? What is genuinely novel or impressive? Do not omit this section out of adversarial zeal — intellectual honesty requires acknowledging strengths.
7. **Priority Fix List**: The 15 most important things to fix, ranked by severity, with specific recommendations. Separate into: (a) things that block ALL users, (b) things that block specific user types, (c) things that reduce quality but don't block usage.
8. **Kill-or-Keep Verdict**: For each major subsystem (template corpus, web of belief, paper eval pipeline, building eval pipeline, theory reduction system, PDF extraction, database architecture, user-facing reports/API), render a verdict: KEEP (sound, needs polish), REWORK (concept ok, implementation needs major changes), or REBUILD (fundamentally misconceived, start over).
9. **Gap Analysis**: What would it take to go from current state to a system that User 1 (architect) could actually use on a real project? Estimate in person-months. What about User 2 (researcher)? Which user type is CLOSEST to being served?

---

## GROUND RULES

- **No sycophancy.** If something is bad, say it's bad. If something is impressive, say it's impressive. But do not soften bad news.
- **No handwaving.** Every criticism must point to a specific file, function, data value, or design decision. "The architecture seems questionable" is worthless. "The function `compute_wis()` at line 47 of building_eval.py returns a hardcoded 50.0 regardless of inputs" is useful.
- **Assume competence.** The developer is a 35-year veteran of cognitive science who was at the MIT AI Lab. Don't explain basic concepts. Do point out where expertise in one domain may have created blind spots in another.
- **Distinguish levels of severity.** A hardcoded placeholder is a different kind of problem from a fundamental theoretical confusion. Label accordingly: CRITICAL (system cannot function), MAJOR (produces wrong results), MODERATE (suboptimal but functional), MINOR (cosmetic or stylistic), NOTE (observation, not necessarily a problem).
- **Be concrete about fixes.** Don't just say "the WIS score lacks validity." Say "the WIS score lacks validity because [specific reason] and could be improved by [specific approach] — see [specific paper/framework]."
- **Read the sprint plans.** Some problems you'll find are already diagnosed and scheduled for fixing (e.g., Doc 70 on the PDF data quality). Acknowledge when the project has already identified a problem. But also check: is their proposed fix adequate?

---

## THE QUESTIONS BEHIND ALL THE QUESTIONS

At bottom, there are two questions this review must answer:

**Question 1 (Intellectual):** Does this system have a sound intellectual core that, with engineering work, could become a genuinely useful tool for evidence-based architectural design? Or is it an elaborate scaffold around an empty center?

**Question 2 (Practical):** If the intellectual core IS sound — how far is it from serving a real user? Is this 3 months of engineering from an architect being able to use it? Or 3 years? Is there a viable minimum viable product hiding inside the current codebase, or does "usable" require rethinking the entire interface layer?

Answer both honestly. The developer can handle it.
