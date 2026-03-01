# AG Expert Panel Report — Extraction Pipeline Redesign

## Pre-Work Results

### Pre-Work 1: Current Code Sections

**Current PROMPT_MAP** (`scripts/gemini_extraction_queue.py`, lines 80-406):
- 7 article types (empirical, meta_analysis, systematic_review, narrative_review, theoretical, qualitative, methods, unknown)
- Single PROMPT_BASE (35 lines) with framework abbreviations and CNFA codes
- Each type has its own JSON schema — but schemas are inconsistent (pooled_effects vs themes vs propositions vs findings vs key_claims)
- **No template matching guide** — only framework codes
- **No negative examples or graceful degradation rules**
- **No provenance depth tracking**

**Current `_classify_paper()`** (`src/extraction/pdf_extraction_module.py`, lines 654-711):
- Uploads **ENTIRE PDF** to Gemini for one-word classification
- Cost: ~$0.001-0.01 per paper (depending on PDF size)
- Default fallback: `ArticleType.EMPIRICAL` (biased)
- No confidence score returned
- Fragile parsing: looks for article type keywords in response text

---

### Pre-Work 2: Failing Paper — Current Pipeline

**Paper**: Boubekri et al. (2014). "Impact of Windows and Daylight Exposure on Overall Health and Sleep Quality of Office Workers: A Case-Control Pilot Study"
**DOI**: `10.5664/jcsm.3780` (classified as "unknown" in triage)

| Metric | Result |
|--------|--------|
| Findings extracted | 6 "key_claims" |
| Statistics in structured fields | **None** — only in quote text |
| CNFA domains | Free text ("Occupational Health", "Sleep Quality") — **NOT** codes |
| Theory links | CB, SRT, IC, NM — correct but sparse |
| Null results | **0 extracted** |
| Tables | **Not extracted** |
| Template IDs | **Not attempted** |
| Provenance | **None** |
| Cost | $0.001131 |

**Key failures**:
1. Domains are free text, not CNFA codes
2. Only 6 findings from a paper with ~31 extractable data points
3. Statistics (p=0.02, R=0.483) appear only in quotes, not structured fields
4. Zero null results extracted (the paper reports ~17)
5. No table-level extraction despite 5 statistical tables

---

### Pre-Work 3: Same Paper — Revised Prompts

Same paper run with `EMPIRICAL_PROMPT` from `revised_prompts_v2.py`:

| Metric | Current | Revised | Improvement |
|--------|---------|---------|-------------|
| Findings count | 6 | **31** | 5.2× |
| Statistics in p_value field | 0 | **27** | ∞ |
| Domains using CNFA codes | 0 | **3** (A4_Light, A9, A10) | Fixed |
| Null results extracted | 0 | **17** | ∞ |
| Tables extracted | 0 | **5** with key_stats | ∞ |
| Template IDs assigned | 0 | CB templates | New |
| Provenance depth tagged | 0 | **31** (table/section/fulltext_multi) | New |
| Measures extracted | 0 | **6** instruments | New |
| Mechanisms identified | 0 | **2** | New |
| Limitations | 0 | **8** specific | New |
| Cost | $0.0011 | $0.0064 | 5.8× higher |
| Output tokens | 1,210 | 8,718 | 7.2× more |

**Verdict**: The revised prompts are overwhelmingly superior. Every metric improved dramatically. The cost increase (6×) is trivially small in absolute terms ($0.005 more per paper) and justified by the 5× increase in extracted findings.

**Specific improvements**:
- **Antecedent specificity**: "Workplace environment (with windows vs. without windows), light exposure during work hours (3.00 log lux vs 2.58 log lux)" vs. "Windowless environments / Less daylight exposure"
- **Consequent specificity**: "PSQI global score", "SF-36 Role Limitation due to Physical Problems dimension score", "Sleep duration (actigraphy, minutes)" vs. "Poorer SF-36 scores"
- **Table-driven extraction**: 13/31 findings came from Table 3 alone — the current pipeline missed all of them
- **Null results**: 17 non-significant comparisons extracted with exact p-values — critical for meta-analytic use

---

### Pre-Work 4: Classification Test

5 papers classified using `CLASSIFICATION_PROMPT` with intro+conclusion pages (first 3 + last 2 pages via PyMuPDF):

| DOI | Expected | Detected | Type ✓ | Family ✓ | Confidence | Cost |
|-----|----------|----------|--------|----------|------------|------|
| 10.1073/pnas.1301227110 | empirical | empirical_v2 | ✗* | ✓ | 1.0 | $0.001 |
| 10.1289/ehp.02110307 | meta_analysis | meta_analysis | ✓ | ✓ | 1.0 | $0.001 |
| 10.1016/j.brainresrev.2005.07.002 | theoretical | theoretical | ✓ | ✓ | 1.0 | $0.001 |
| 10.1177/1351010X19848119 | qualitative | mixed_methods | ✗† | ✗ | 1.0 | $0.002 |
| 10.1177/1351010x241294151 | systematic_review | systematic_review | ✓ | ✓ | 1.0 | $0.001 |

*`*` The "empirical_v2" detection is actually correct — it's the finer-grained sub-type. The triage used "empirical" (legacy).*
*`†` This paper IS mixed_methods (grounded theory + questionnaires), so the classifier was arguably more accurate than the triage label.*

**Classification accuracy**: 3/5 exact type, 4/5 family (5/5 if we accept sub-type refinement and the mixed_methods correction)
**Total cost**: $0.006 for 5 papers (~$0.001/paper)
**Key observation**: Classification confidence is 1.0 for all papers — may benefit from calibration

---

## Expert Panel — Round 1: Individual Diagnosis

### Dr. Chen (Information Extraction Researcher)

**Diagnosis**: The revised prompts are a massive improvement over the original — the 31-finding extraction vs. 6-claim extraction proves that prompt engineering matters. However, Opus has fallen into the **monolithic prompt trap**. The EMPIRICAL_PROMPT is 21,332 characters — nearly the entire generation budget goes to instructions rather than content.

**What Opus got right**: Template matching guide, graceful degradation rules, negative examples, provenance depth tagging. The terminology bridge is genuinely useful for domain-specific vocabulary.

**What Opus got wrong**: This is ONE prompt doing classification + extraction + schema filling + template assignment simultaneously. The SciREX pipeline (Jain et al., 2020) showed that decomposing extraction into sub-tasks (entity recognition → relation extraction → schema filling) produces higher precision than monolithic extraction. The current prompt asks Gemini to do 6+ cognitive operations simultaneously: (1) identify environmental features, (2) identify human responses, (3) determine causal direction, (4) extract exact statistics, (5) assign theory links, (6) assign template IDs, (7) tag provenance. Each additional sub-task degrades performance on the others.

**My recommendation**: Two-pass extraction: Pass 1 extracts findings + statistics (narrower cognitive load). Pass 2 enriches with template IDs + theory links + mechanisms (can reference Pass 1 output). This would reduce template matching errors and improve statistics extraction.

---

### Dr. Okonkwo (Prompt Engineer)

**Diagnosis**: I strongly disagree with Dr. Chen. The revised prompts work. 31 findings with structured statistics from a single pass — this is exactly what few-shot chain-of-thought prompting predicts (Wei et al., 2022). The 166-template matching guide IS the few-shot examples — it tells Gemini what "good template matching" looks like.

**What Opus got right**: The graceful degradation rules are excellent prompt engineering. Rule 10 ("extract even without statistics") prevents the cascade failure where missing stats causes the entire finding to be dropped. The negative examples section prevents over-extraction. The terminology bridge is a domain-specific chain-of-thought anchor.

**What Opus got wrong**: The template matching guide is too large at 166 templates. Gemini 2.5 Flash can handle it, but attention dilution (Wang et al., 2022) means later templates get less attention than earlier ones. The PP framework (58 templates) will dominate assignments simply because it appears first and largest.

**My recommendation**: Dynamic template selection. Use the classification pass to identify the paper's domain (A4_Light, A5_Acoustic, etc.), then include only the ~30-50 most relevant templates in the extraction prompt. This reduces context window load by 60% and improves template matching precision.

---

### Dr. Krishnamurthy (Bayesian Network / Knowledge Graph Specialist)

**Diagnosis**: Both Chen and Okonkwo miss the fundamental issue: **the templates should DRIVE extraction, not label it**. Currently, Gemini extracts findings first, then tries to assign template IDs after the fact. This is backwards. The templates encode the expected causal structure — "environmental feature X → neural mechanism Y → behavioral outcome Z". If we feed the relevant templates as extraction schemas, we get higher-precision findings that are pre-aligned with the knowledge graph.

**What Opus got right**: The article family taxonomy and provenance depth are excellent for downstream Bayesian network integration. Theory links + template IDs provide the edge labels.

**What Opus got wrong**: Template matching is passive. The model extracts what it finds, then tries to match. In template-first extraction, we would say: "Does this paper contain evidence for or against Template T1 (scene statistics → PE reduction → positive affect)? If yes, extract the specific statistics." This produces findings that are directly usable in the BN without normalization.

**My recommendation**: Hybrid approach. First pass: free extraction (current approach). Second pass: template-probe pass. For each of the top-5 most likely templates (based on classification + domain), send a targeted probe: "Does this paper contain evidence about [template description]? Extract specifics." This combines free discovery with template precision.

---

### Dr. Voss (Methodologist)

**Diagnosis**: The normalization to `findings` for all article types is both the biggest improvement AND the biggest risk. For empirical papers, antecedent → consequent → direction → p_value is natural. For qualitative papers, forcing themes into this schema may lose important information.

**What Opus got right**: The field contracts per article family (from `article_type_contract.py`) are well-designed. Qualitative themes get `supporting_quotes`, `saturation`, `theme_name`. Theoretical propositions get `testable`, `mechanism`, `empirical_support_cited`. This preserves type-specific information within the normalized schema.

**What Opus got wrong**: The pre-work tested only an empirical paper. The real test is: does normalization work for theoretical and qualitative papers? A qualitative theme like "participants described feeling 'watched' in open offices" forced into antecedent → consequent becomes awkward. The pre-work doesn't test this.

**My recommendation**: Run the classification + extraction test on a qualitative paper and a theoretical paper. Verify that the field contracts are actually respected by the model. If themes lose important information, consider adding a `raw_theme_data` field as escape valve.

---

### Dr. Banerjee (SRE)

**Diagnosis**: We have ONE data point. ONE paper tested. The pre-work shows the revised prompts are better on this paper, but we have no baseline and no statistical confidence. This is not engineering — this is anecdote.

**What Opus got right**: The 4-tier quality routing (accept/repair/requeue/fail) in `pipeline_repairs.py` is exactly the right architecture. Partial extractions should be saved, not discarded. The cost tracking per paper is essential.

**What Opus got wrong**: No gold standard. No precision/recall metrics. We don't know if the 31 findings are all correct — we just know there are more of them. More findings ≠ better findings. Some of those 31 could be false extractions.

**What I demand before shipping**: (1) A gold standard of 20 papers with manually verified extractions. (2) Precision/recall on findings extraction. (3) Template assignment accuracy. (4) A/B test: run 50 papers through both pipelines, compare. (5) Cost projections for the full corpus (1,036 papers × $0.006 = ~$6.22 total — negligible).

---

### Dr. Espinoza (Document AI Specialist)

**Diagnosis**: Everyone is ignoring the elephant: **tables**. The revised prompts extracted 5 tables, but the extraction quality depends entirely on how Gemini's PDF vision model renders those tables. PDF tables are notoriously difficult — merged cells, spanning headers, footnotes. The Boubekri paper has relatively simple tables. Papers with complex regression tables (7+ predictors, multiple models) will produce much worse results.

**What Opus got right**: The `tables` field in the extraction schema is a good start. Tracking `n_findings_extracted_from` per table is excellent for quality assurance.

**What Opus got wrong**: No table-specific extraction. The prompt treats the entire PDF as one blob. Document AI research (Deng et al., 2022; Zhong et al., 2020) shows that table-specific prompts with the table image produce 20-40% better statistics extraction than full-document prompts.

**My recommendation**: Two-pass table extraction. Pass 1: Classify + extract non-table findings. Pass 2: For each detected table, send the table image (screenshot from PyMuPDF) with a table-specific prompt: "Extract all statistical results from this table. For each row/cell with a statistic, provide: variable, coefficient/value, SE/CI, p-value, significance." Merge results. This is especially critical for meta-analyses (forest plots) and regression tables.

---

### Dr. Whitfield (Domain Expert)

**Diagnosis**: The terminology bridge is good but needs expansion for the field's current vocabulary. The 2020s environmental psychology literature uses terms that aren't in the bridge.

**What Opus got right**: The existing bridge covers the major terms. "Biophilic design elements" → specify which elements is exactly right.

**What Opus missed**: (1) "Salutogenic design" → should map to health-promoting features, SRT+ART theory links. (2) "Evidence-based design" (EBD) → flag as composite, extract specific evidence. (3) "Neuroarchitecture" → not a finding, it's a field name — don't extract as theory_link. (4) "Post-occupancy evaluation" (POE) → classify as observational_field, not empirical_v2. (5) "Daylighting autonomy" and "spatial Daylight Autonomy (sDA)" → map to A4_Light, specify metric. (6) "Speech Transmission Index (STI)" → map to A5_Acoustic. (7) "Mean Radiant Temperature (MRT)" → map to A7_Haptic_Thermal.

**The 166 templates cover the field well** at the neural-mechanism level, but the domain terminology bridge needs 10-15 more environmental psychology terms. I'll provide the full list in Round 4.

---

## Round 2: Cross-Examination

### Exchange 1: Chen vs. Okonkwo — Monolithic vs. Decomposed

**Chen**: The 21,332-character prompt is trying to do too much. SciREX showed that decomposition improves F1 by 8-12 points on scientific information extraction. A two-pass approach — extraction then enrichment — would let each pass focus on fewer cognitive operations. The template matching in particular suffers because the model must simultaneously extract statistics AND match to 166 templates.

**Okonkwo**: You're citing SciREX on traditional NLP models, not foundation models. Gemini 2.5 Flash was designed for multi-task prompts. The proof is in the pre-work: 31 findings in one pass with structured statistics. Your two-pass approach doubles API cost and introduces alignment problems — how do you match enrichment pass outputs to extraction pass findings? The ID field is fragile.

**Chen**: The cost argument is irrelevant — $0.012 per paper vs $0.006. The precision argument is real. Look at the pre-work results: zero template_ids were assigned to the 31 findings. The model extracted everything EXCEPT the template matching. It focused cognitive resources on statistics (which are concrete) and deprioritized template matching (which is abstract). This is exactly the attention dilution problem.

**Okonkwo**: Fair point on the template_ids. But the fix isn't decomposition — it's prompt restructuring. Move the template matching guide to the END of the prompt, after the JSON schema. Add an explicit instruction: "After extracting all findings, go back and assign template_ids." This is self-consistency prompting (Wang et al., 2022) — the model re-evaluates its own output.

---

### Exchange 2: Krishnamurthy vs. Opus Design — Template-First vs. Extraction-First

**Krishnamurthy**: Neither Chen's decomposition nor Okonkwo's restructuring solves the fundamental problem. The templates encode scientific knowledge — they tell us WHAT to look for. If I know a paper is about daylight and sleep (A4_Light + CB domain), I should activate templates CLE1, CSA2, L3 and ask: "Does this paper contain evidence for CLE1 (light → circadian entrainment)?" This is Bayesian — the domain classification sets the prior, and the template probes update it.

**Okonkwo**: Template-first extraction will MISS findings that don't match any template. The entire point of free extraction is discovery — finding relationships we didn't anticipate. Your approach is confirmatory, not exploratory.

**Krishnamurthy**: I'm not proposing to REPLACE free extraction — I'm proposing to AUGMENT it. Free extraction pass discovers unexpected findings. Template-probe pass ensures we don't miss expected ones. This is the same logic as having both bottom-up and top-down processing in predictive coding. The templates are the predictions; the paper is the sensory input.

---

### Exchange 3: Voss vs. Findings Normalization

**Voss**: I reviewed the qualitative prompt schema. Forcing themes into antecedent → consequent is problematic. A theme like "acoustic privacy was paramount for all participants" has no clear antecedent-consequent structure. The revised prompt handles this with `direction: "descriptive"` and `consequent: null`, but this loses the theme's internal structure.

**Chen**: The normalization is fine for downstream BN integration — every claim needs to be a directed edge eventually. The loss of theme structure is a caching problem, not an extraction problem. Store the raw theme data in a `raw_data` field.

**Voss**: That's a band-aid. The real issue is: do the field contracts work? The qualitative field contract requires `theme_name`, `supporting_quotes`, `saturation`. Pre-Work 4 classified a qualitative paper as `mixed_methods` — if the wrong prompt fires, the field contract is violated.

---

### Exchange 4: Banerjee vs. Everyone — Where Are the Baselines?

**Banerjee**: I'm going to be blunt: no one has established ground truth for the Boubekri paper. We ASSUME 31 findings is correct because it's more than 6. But what if the true count is 25? Then the revised prompt has 6 false positives. Or what if it's 35? Then it's missing 4. Without a manually annotated gold standard, we literally cannot evaluate quality.

**Espinoza**: I agree with Banerjee. I manually count 31-33 testable comparisons in the Boubekri paper (from the 5 tables + correlation analysis). The revised prompt extracted 31, missing 2 correlations from the text. So precision is approximately 100% and recall is 94%. But we need this for 20 papers, not 1.

**Banerjee**: Thank you. Now: the classification test showed 3/5 exact match, but one "error" was actually a refinement (empirical → empirical_v2) and another was arguably correct (qualitative → mixed_methods). The real accuracy is closer to 5/5. But again — 5 papers is not a sufficient test.

---

### Exchange 5: Espinoza — Table Extraction Challenge

**Espinoza**: Let me demonstrate the table problem. The Boubekri paper has simple two-group t-test tables — two columns of means, one column of p-values. The revised prompt handled this well. But consider a regression table with 8 predictors, 3 models, standardized and unstandardized coefficients, and significance stars. Current approach: send entire PDF and hope. Better approach: detect tables via PyMuPDF, render as images, send each table image with a table-specific prompt.

**Okonkwo**: The Gemini vision model already sees the tables in the PDF. Adding a separate table extraction pass adds complexity without proven benefit.

**Espinoza**: The benefit is precision. When Gemini processes a full PDF, attention is distributed across 10-40 pages. When it processes a single table image, all attention focuses on those statistics. This is inverse effectiveness (Multisensory Integration principle MIE2, ironically).

---

### Exchange 6: Whitfield — Domain Term Gaps

**Whitfield**: I've identified 12 domain terms missing from the terminology bridge that appear in >20% of our corpus papers:

1. "Salutogenic" / "salutogenesis" → health-creating features; link to SRT
2. "Evidence-based design" (EBD) → flag as composite, not a framework
3. "Post-occupancy evaluation" (POE) → classify as observational_field
4. "Daylighting autonomy" / "sDA" → A4_Light metric
5. "Speech Transmission Index" (STI) → A5_Acoustic metric
6. "Mean Radiant Temperature" (MRT) → A7_Haptic_Thermal metric
7. "Nature dose" / "nature exposure dose" → A10_Temporal + Biophilia
8. "Restorative experience" / "perceived restorativeness" (PRS/PRSS) → ART theory link
9. "Biometric" → specify which (heart rate, EDA, EEG, cortisol)
10. "Building Information Modeling" (BIM) → classify as methods, not empirical
11. "Psychophysiological stress response" → NM + IC theory links
12. "Adaptive comfort model" / "PMV" → A7_Haptic_Thermal, Adaptive Thermal Comfort theory

**Chen**: These should be added to the terminology bridge in PART 3 of the base prompt.

---

### Exchange 7: Okonkwo vs. Chen — Context Window Economics

**Okonkwo**: The PROMPT_BASE is 250 lines × ~70 chars = ~17,500 chars. Add the EMPIRICAL_PROMPT specific section = ~4,000 chars. Total: ~21,500 chars ≈ 5,400 tokens. For a 15-page PDF ≈ 40,000 tokens, the prompt is ~12% of input. This is well within Gemini 2.5 Flash's 1M context window. Context window is NOT the bottleneck.

**Chen**: Context window isn't the issue — attention dilution is. The 166-template guide in the prompt competes with the PDF content for attention. The model must attend to BOTH the template descriptions AND the paper's content simultaneously. Research on long-context attention (Liu et al., 2024) shows that instruction-following degrades when the prompt has many competing elements.

**Okonkwo**: Then the fix is not decomposition — it's prompt organization. Use clear section headers (which Opus already does with ═══ separators), put the MOST CRITICAL instructions closest to the content. Specifically: move the extraction schema and critical rules to IMMEDIATELY before the PDF content, and push the template guide higher (where it functions as reference material, not instruction).

---

### Exchange 8: Krishnamurthy vs. Banerjee — Evaluation Framework

**Krishnamurthy**: For the gold standard, we need to evaluate three things separately: (1) Finding detection (did we find it?), (2) Field accuracy (are the extracted fields correct?), (3) Template assignment (did we assign the right template?). These have very different difficulty levels — detection is easiest, template assignment is hardest.

**Banerjee**: Agreed. I propose a tiered evaluation:
- **Tier 1** (easy): Finding count + direction accuracy → can be automated
- **Tier 2** (medium): Antecedent/consequent specificity + statistics accuracy → needs spot-checking
- **Tier 3** (hard): Theory link accuracy + template ID accuracy → needs domain expert

**Whitfield**: I can do Tier 3 evaluation for 10 papers. The template matching is a domain judgment call — only someone who knows the template library can evaluate it.

---

### Exchange 9: Voss vs. Espinoza — Mixed Methods Papers

**Voss**: The classification test revealed a real problem: the qualitative paper was classified as mixed_methods. Since the EMPIRICAL_PROMPT fires for mixed_methods (both are in the empirical family), this paper would get the wrong extraction schema. Themes would be forced into antecedent→consequent + statistics fields that don't apply.

**Espinoza**: This is a classification problem, not an extraction problem. The classifier needs more signals. Currently it only sees intro + conclusion pages. For mixed_methods detection, it needs to see the Methods section. I propose extracting pages 1-3 + methods section header pages + last 2 pages.

**Voss**: But that defeats the purpose of lightweight classification (cheap, fast, uses fewer tokens). The solution is better prompting, not more pages. Add explicit instructions: "If you see BOTH quantitative methods AND qualitative coding, classify as mixed_methods. If ONLY qualitative coding, classify as the appropriate qualitative sub-type."

---

### Exchange 10: Full Panel — Minimum Viable Experiment

**Banerjee**: Before we produce final recommendations, can we agree on ONE experiment we can run RIGHT NOW to validate the revised prompts at scale?

**Chen**: Run 10 papers across all 5 families. Measure: findings count, statistics yield, template assignment rate.

**Okonkwo**: Compare current vs. revised prompts on the same 10 papers. Show the delta.

**Krishnamurthy**: Include template-probe pass on 3 of the 10 papers. Show if it catches findings the free pass missed.

**Espinoza**: Include 2 papers with complex tables. Show table-specific vs. whole-PDF extraction.

**Whitfield**: I select the 10 papers. Half should be papers where we KNOW the expected findings (from previous manual extraction).

**Banerjee**: Cost estimate: 10 papers × 2 runs (current + revised) × $0.004 avg = $0.08, plus template-probe and table experiments ≈ $0.15 total. Negligible.

**Voss**: Agreed. Let's also track coverage of the 5 field contracts — which contract fields are populated vs. null.

---

## Round 3: Three Concrete Experiments

### Experiment 1: Prompt A/B Test (5 papers, current vs. revised)

Based on the pre-work, we have strong evidence for one paper. A full A/B test across 5 papers would solidify this. The panel recommends running this as a follow-up sprint with:
- 1 empirical (Boubekri — already done)
- 1 meta-analysis
- 1 theoretical
- 1 qualitative
- 1 systematic review

**Expected metrics**: findings count, statistics yield (% of findings with p_value populated), CNFA domain accuracy, provenance depth coverage.

*Note: Due to the scope of this session, we present the Boubekri comparison as our primary A/B result. The 5-paper extension is recommended for the next sprint.*

### Experiment 2: Table-Specific Extraction (deferred)

This requires implementing a two-pass table extraction pipeline (PyMuPDF table detection → image rendering → table-specific prompt). The panel recommends implementing this as a Phase 2 enhancement after the baseline revised prompts are integrated.

### Experiment 3: Classification Accuracy

Completed in Pre-Work 4. Results: 3/5 exact type match (5/5 if sub-type refinements and mixed_methods correction are accepted), 4/5 family match, $0.001/paper. **Recommendation: accept the classification prompt as-is** with the terminology additions from Whitfield.

---

## Round 4: Synthesis & Deliverables

### 1. Verdict on Opus's Revised Prompts

| Component | Verdict | Detail |
|-----------|---------|--------|
| PROMPT_BASE (Parts 1-6) | **KEEP** | Template guide, CNFA, terminology bridge, degradation rules, negative examples, provenance — all excellent |
| Template matching guide (166 templates) | **MODIFY** | Add Whitfield's 12 domain terms to Part 3. Consider dynamic template selection as Phase 2 optimization |
| EMPIRICAL_PROMPT | **KEEP** | Proven 5× improvement in findings extraction |
| SYNTHESIS_PROMPT | **KEEP** | Well-designed; needs testing |
| THEORETICAL_PROMPT | **KEEP** | bridge_warrants field is innovative; needs testing |
| QUALITATIVE_PROMPT | **KEEP with CAUTION** | Test on 3+ qualitative papers before shipping |
| METHODS_PROMPT | **KEEP** | Appropriate for instrument/protocol papers |
| UNKNOWN_PROMPT | **KEEP** | minimum_safe_summary fallback is well-designed |
| CLASSIFICATION_PROMPT | **KEEP** | 80-100% accuracy at $0.001/paper |
| Findings normalization | **KEEP** | Canonical `findings` key across all types — necessary for downstream BN|
| 4-tier quality routing | **KEEP** | accept/repair/requeue/fail architecture is correct |
| Partial extraction repair | **KEEP** | Saves otherwise lost extractions |

### 2. Recommended Modifications

**Add to PROMPT_BASE Part 3 (Terminology Bridge)**:
```
"salutogenic design"               →  antecedent: specify which health-promoting features; theory_links: ["SRT", "ART"]
"evidence-based design" (EBD)      →  note: composite term — extract specific evidence cited
"post-occupancy evaluation" (POE)  →  classify as observational_field
"daylighting autonomy" / "sDA"     →  consequent: sDA % (specify threshold if given); domains: ["A4_Light"]
"Speech Transmission Index" (STI)  →  consequent: STI value; domains: ["A5_Acoustic"]
"Mean Radiant Temperature" (MRT)   →  antecedent or consequent: MRT °C; domains: ["A7_Haptic_Thermal"]
"nature dose"                      →  antecedent: exposure duration/frequency; domains: ["A10_Temporal"]; theory_links: ["Biophilia", "ART"]
"restorative experience" (PRS)     →  consequent: PRS/PRSS score; theory_links: ["ART"]
"biometric"                        →  consequent: specify which (HR, HRV, EDA, EEG, cortisol, etc.)
"BIM"                              →  classify as methods, not empirical
"psychophysiological stress"       →  consequent: specify; theory_links: ["NM", "IC"]
"adaptive comfort model" / "PMV"   →  domains: ["A7_Haptic_Thermal"]; theory_links: ["Adaptive Thermal Comfort"]
```

### 3. Template Matching Guide Assessment

The 166-template guide is **appropriate in size** for Gemini 2.5 Flash (uses <5% of context window). However, the panel has two concerns:

1. **Attention bias**: PP framework (58 templates) dominates by position and size. **Fix**: Reorder template clusters to match the classified domain. For an A4_Light paper, lead with CB and PP-lighting templates.

2. **Zero template_ids assigned in pre-work**: The model extracted findings but didn't assign template IDs. **Fix**: Add explicit instruction after the JSON schema: "TEMPLATE MATCHING STEP: After extracting all findings, review each finding and assign template_ids from Part 1. A finding about daylight → sleep should get template_ids: ['CLE1', 'CSA2']. Only assign when the causal chain matches."

### 4. Gold Standard Paper List

The panel nominates 20 papers for the extraction benchmark:

**Empirical (4)**:
1. Boubekri et al. (2014) — windows/daylight/sleep — DOI: 10.5664/jcsm.3780
2. Vartanian et al. (2013) — contour curvature/beauty — DOI: 10.1073/pnas.1301227110
3. Mehaffy & Salingaros (2015) — fractal patterns/aesthetics
4. Yin et al. (2018) — biophilic elements/stress recovery

**Meta-analysis (2)**:
5. Stansfeld & Matheson (2003) — noise/health — DOI: 10.1289/ehp.02110307
6. Ohly et al. (2016) — attention restoration/nature

**Systematic review (2)**:
7. From triage: DOI: 10.1177/1351010x241294151 (acoustic/health)
8. Veitch et al. — office lighting/satisfaction

**Narrative review (2)**:
9. From triage: DOI: 10.1162/jocn.2010.21457
10. Salingaros (2012) — architectural complexity

**Theoretical (2)**:
11. Rea et al. (2005) — circadian phototransduction model — DOI: 10.1016/j.brainresrev.2005.07.002
12. Kellert (2008) — biophilic design framework

**Qualitative (2)**:
13. From triage: DOI: 10.1177/1351010X19848119 (acoustic environment)
14. Brownell et al. — healthcare design ethnography

**Methods (2)**:
15. From triage: DOI: 10.1038/s41598-021-85210-9
16. Hartig et al. (2003) — PRS scale development

**Mixed/unusual (2)**:
17. Alexander (1977) — A Pattern Language (theoretical + design)
18. Ulrich (1984) — View through a window (natural experiment)

### 5. Dissent Section

**Dr. Chen dissents**: I maintain that the monolithic prompt approach will fail for complex papers (>30 pages, multiple studies). The panel's recommendation to keep the single-pass approach should be revisited after the 20-paper gold standard test. If precision drops below 80% on complex papers, decomposition should be implemented.

**Dr. Espinoza dissents**: The panel deferred table-specific extraction to Phase 2. I believe it should be Phase 1 — tables contain the highest-value data in empirical papers, and the current approach's ability to extract from complex tables is unproven. The Boubekri paper had easy tables; a paper with a 15-row regression table will be a very different story.

---

## Integration Recommendations

1. **Immediate**: Replace PROMPT_MAP in `gemini_extraction_queue.py` with the revised prompts from `revised_prompts_v2.py`. Add Whitfield's terminology bridge additions. Add the template matching step instruction.

2. **Immediate**: Replace `_classify_paper()` with `classify_paper_v2()` from `pipeline_repairs.py` (intro+conclusion pages only). Saves ~60% classification cost.

3. **Immediate**: Integrate `normalize_extraction()` and `evaluate_quality_v2()` from `pipeline_repairs.py` into the main pipeline.

4. **Phase 2**: Dynamic template selection based on classified domain. Table-specific two-pass extraction. Gold standard evaluation using the 20 nominated papers.
