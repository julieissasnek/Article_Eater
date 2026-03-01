# Extraction Pipeline Audit & Improved AG Prompt

**Date:** 2026-02-24  
**Author:** Opus (Architecture/Theory)  
**For:** David Kirsh  
**Re:** Code audit of `pdf_extraction_module.py`, `gemini_extraction_queue.py`, PROMPT_MAP, and templates T9/T12/T27 — with substantially improved prompt for AG panel session

---

## Part 1: Code Audit — What's Actually Going Wrong

I've now read all ~2,100 lines of code, the three template files, the 51-entry alias registry, and the extraction instructions. The problems are more specific and more architecturally consequential than AG's panel identified. Here is what I found, organized from most damaging to least.

---

### Problem 1: The Classification Prompt Is Expensive, Naive, and Disconnected from Downstream Extraction

**Where:** `pdf_extraction_module.py`, lines 654–711, method `_classify_paper()`

The classification step uploads the **entire PDF** to Gemini and asks for a single word:

```
Classify this paper. Return ONE word only:
empirical
meta_analysis
systematic_review
...
```

This has three compounding failures:

**Cost waste.** You're paying for a ~50,000-token input (a full PDF in vision mode) to get a 1-token output. At Gemini 2.5 Flash pricing ($0.15/M input), that's roughly $0.0075 per classification — and you're doing this for *every* paper before extraction even begins. For 500 papers, that's ~$3.75 just on classification, plus the API latency of uploading each PDF twice (once to classify, once to extract).

**No reasoning chain.** A one-word answer with `temperature=0.0` gives Gemini no room to reason about ambiguous cases. A paper that's primarily empirical but includes a systematic review section will be classified somewhat arbitrarily. There's no confidence signal, no explanation, no fallback logic.

**The fallback is wrong.** Line 707: `return ArticleType.EMPIRICAL  # Default`. If Gemini returns anything that doesn't match your enum (and with a one-word prompt, unexpected outputs are common — "empirical study", "experimental", "quasi-experimental"), it defaults to EMPIRICAL. This means papers that are theoretical, qualitative, or methods papers get the EMPIRICAL extraction prompt, which demands p-values and effect sizes they don't have, guaranteeing extraction failure.

**What should happen:** The classification should use only the first and last 2–3 pages of the PDF (introduction + conclusion), which carry almost all the classification signal. It should request a JSON response with `article_type`, `confidence`, and `signals` (what led to the classification). This is what your UNKNOWN_PROMPT already does — it extracts `detected_article_type`, `classification_confidence`, and `classification_signals`. You have the right idea in the wrong place.

---

### Problem 2: The Templates Are Invisible to the Extraction Prompts

**Where:** `gemini_extraction_queue.py`, lines 80–395 (PROMPT_MAP)

This is the most consequential architectural gap. Your template system (T1–T51) is a sophisticated ontology with causal links, moderators, scope conditions, maturity ratings, and cross-template interactions. But the extraction prompts know **nothing** about this. The prompts list framework codes (`PP`, `SN`, `DP`, etc.) and CNFA domain codes (`A1_Materials`, `A4_Light`, etc.), and they ask Gemini to populate a `theory_links` array — but they never explain *what matching a template means*.

Consider what happens when Gemini processes a paper about ceiling height effects on creativity. The paper probably discusses:
- "Spaciousness" and "perceived openness" (which maps to A2_Spatial_Scale)
- "Divergent thinking" or "creative ideation" (which maps to A9_Task_Cognition)
- Perhaps Meyers-Levy & Zhu (2007), which connects to the Predictive Processing framework

But the prompt just says `theory_links: ["PP", "SN", "DP", ...]` with no guidance on when PP applies versus SN versus DP. Gemini has to guess. Compare this to template T9 (Dual-Process Implicit Evaluation), which has explicit causal links:

```
environmental_features → subcortical_visual_processing → implicit_affective_tag → explicit_evaluation
```

If the extraction prompt included even a compressed version of this chain ("If the paper discusses rapid or automatic evaluations of spaces — approach/avoid, first impressions, implicit associations — this maps to T9/DP"), Gemini would have dramatically better recall for theory linking.

**What should happen:** The prompt should include a condensed "matching guide" for the templates most likely to be relevant, based on the paper's CNFA domain classification. A paper classified as involving A4_Light doesn't need to see template descriptions for all 51 templates — it needs the 8–12 templates that involve lighting, circadian regulation, visual comfort, and mood.

---

### Problem 3: The Quality Gate Destroys Salvageable Extractions

**Where:** `pdf_extraction_module.py`, lines 804–881, method `_evaluate_quality()`

When a paper produces an extraction that scores below the threshold, the quality evaluator returns `action="requeue"` or `action="fail"`. The `process_one()` method (line 1001) stores the quality report but **does not save the partial extraction to a recoverable location**. It sets `item.status = QueueStatus.REQUEUED` and the paper goes back in the queue for a complete re-extraction from scratch.

The waste here is enormous. If Gemini extracted 5 findings from a paper but 3 of them are missing p-values, you're throwing away the 2 good findings plus all the metadata (title, sample size, study design, domains, stimuli, tables) and spending another $0.01–0.02 to redo everything. Over hundreds of papers, this adds up to both significant cost and significant time.

The SRE on AG's panel identified this correctly: you need a `data/partial_extractions/` folder and a repair pass. But let me be more specific about what repair should look like:

1. Save the raw JSON to `results/partial/{doi}.json` whenever quality score > 0.2 (i.e., *something* was extracted)
2. For findings that have antecedent + consequent but missing statistics, run a **focused follow-up prompt** that sends only the relevant pages (identified by the `source` field in the partial extraction — "Table 3", "p. 12") and asks specifically: "This finding reports [antecedent] → [consequent]. Find the p-value, effect size, and sample size from the referenced location."
3. For findings that have statistics but vague antecedent/consequent descriptions, run a prompt that asks for specificity: "The paper reports a significant effect of 'spatial configuration' on 'performance'. Specify: what exactly was the spatial configuration (e.g., open plan vs. cellular offices, room volume > 50m³ vs < 30m³) and what performance measure (e.g., Stroop task accuracy, SAT scores, self-reported productivity)?"

This targeted repair approach costs a fraction of full re-extraction and should recover 40–60% of currently failing papers.

---

### Problem 4: Two Parallel Systems That Don't Talk

**Where:** Both files

You have two extraction systems that overlap confusingly:

- **`gemini_extraction_queue.py`** has its own `QueueItem`, `ExtractionStatus`, `extract_paper()`, `compare_extractions()`, `merge_extractions()`, and `process_queue_item()`. It does 2-run verification with a 3rd-run tie-breaker using Gemini Pro.

- **`pdf_extraction_module.py`** has its own `QueueItem`, `QueueStatus`, `ExtractionPipeline`, `_extract_paper()`, `_evaluate_quality()`, and `process_one()`. It does single-run extraction with quality-scored routing.

The module imports `PROMPT_MAP` from the queue script (line 721), but everything else is independent. The queue script's 2-run verification is never used by the module's pipeline. The module's quality scoring is never used by the queue script.

This isn't just messy — it creates concrete bugs. The module's `_extract_paper()` (line 776) constructs an `ExtractionResult` dataclass from the JSON, but the JSON schema comes from prompts designed for the queue script's simpler data model. Fields like `pooled_effects` (from META_ANALYSIS_PROMPT) and `themes` (from QUALITATIVE_PROMPT) and `propositions` (from THEORETICAL_PROMPT) don't match the `ExtractionResult` contract, which expects `findings`, `stimuli`, and `tables`. The module's quality evaluator then tries to score `result.findings` — which will be an empty list for meta-analyses that returned `pooled_effects` instead.

**What should happen:** One system. The module (`pdf_extraction_module.py`) should be the canonical pipeline. The queue script's PROMPT_MAP should be absorbed into the module. The 2-run verification logic should become an optional quality mode within the module's `process_one()` method.

---

### Problem 5: The Comparison Logic Is Positionally Naive

**Where:** `gemini_extraction_queue.py`, lines 522–558, function `compare_extractions()`

The comparison zips findings from Run 1 and Run 2 by position (`zip(findings1, findings2)`) and checks if `direction` matches. This assumes Gemini will extract findings in the same order across runs — which it won't for papers with many findings, especially when different runs pick up different findings or extract them from different sections.

The comparison also only checks `direction`, ignoring whether the antecedent and consequent match. Run 1 might extract "ceiling height → creativity (increase)" as finding #3, while Run 2 might extract "ceiling height → creativity (increase)" as finding #5 and "noise level → creativity (decrease)" as finding #3. The positional zip would flag a disagreement on finding #3 when in fact both runs agree on the ceiling height result.

**What should happen:** Semantic matching. Compute similarity between (antecedent, consequent) pairs across runs using string overlap or embedding similarity. Match findings by content, not position. Then check direction agreement on matched pairs.

---

### Problem 6: The Prompts Have No Negative Examples or Graceful Degradation Instructions

**Where:** `gemini_extraction_queue.py`, all prompts

The EMPIRICAL_PROMPT (lines 117–173) has a `CRITICAL RULES` section that says "p_value and effect_size are CRITICAL - search tables, figures, text carefully." But it never says what to do when the paper genuinely doesn't report effect sizes — which is common in older environmental psychology literature, in field studies using chi-square tests, and in EEG/fMRI studies that report activation maps rather than traditional effect sizes.

The result: Gemini either (a) invents statistics to satisfy the prompt's demand, (b) returns null for effect_size which then fails your quality check, or (c) skips the finding entirely because it can't fill the required fields. All three outcomes are bad.

**What should happen:** The prompt needs explicit instructions like:

> "If the paper reports a t-test, F-test, or chi-square with a p-value but no effect size, extract the finding with `effect_size: null` and `effect_size_type: null`. DO NOT skip the finding. If the paper reports only 'p < .05' without an exact value, use `p_value: '<0.05'`. If the paper reports confidence intervals but no p-value, extract the CI and set `p_value: null`. Partial information is far more valuable than no extraction."

You also need **negative examples** — cases where Gemini should *not* extract something as a finding:

> "Do NOT extract: (a) citations of other papers' findings unless the current paper replicates or extends them with new data; (b) hypothesized relationships stated in the introduction that are not tested; (c) demographic descriptive statistics (e.g., 'mean age was 22.3') unless age is an independent variable."

---

### Problem 7: The Image Extraction Has a Scoping Bug

**Where:** `pdf_extraction_module.py`, lines 887–936, method `_extract_images()`

Lines 902–905:

```python
with fitz.open(str(pdf_path)) as doc:
    for page_num in range(len(doc)):
        page = doc[page_num]
image_list = page.get_images(full=True)
```

The `image_list = page.get_images(full=True)` is **outside the for loop** — it only captures images from the last page. The `for page_num in range(len(doc))` loop sets `page` to each page but doesn't do anything with the images until after the loop exits, at which point `page` is the final page. This means you're only extracting images from the last page of every PDF.

**Fix:** The `image_list` call and subsequent processing need to be inside the for loop.

---

## Part 2: The Improved AG Prompt

Below is a substantially rewritten prompt for AG. The key changes from your original:

1. **Pre-work required before the panel** — AG must dump actual code and failure outputs first
2. **Expert personas with specific intellectual commitments** that produce genuine disagreement
3. **A four-round deliberation protocol** with minimum word counts and required cross-examination
4. **Concrete deliverables** (not just conversation)
5. **Explicit grounding** in your actual codebase, templates, and failure modes

---

### PROMPT FOR AG

---

**TASK: Redesign the PDF extraction pipeline through a structured expert panel**

**SYSTEM INSTRUCTION:** You are running a multi-round expert panel to diagnose and fix a failing PDF extraction system. You must complete all preparatory work before convening the panel. You must run all four deliberation rounds without stopping. Experts must disagree with each other where they genuinely have different methodological commitments. The final deliverable is executable code and revised prompts, not recommendations.

---

**CONTEXT:**

We have a pipeline that extracts structured findings from scientific PDFs about environmental psychology and neuroarchitecture. The pipeline:
1. Uploads full PDFs to the Gemini API
2. Classifies article type (empirical, meta-analysis, systematic review, narrative review, theoretical, qualitative, methods)
3. Sends an article-type-specific prompt asking Gemini to return structured JSON
4. Evaluates extraction quality via field coverage scoring
5. Routes papers to ACCEPTED, REQUEUED, or FAILED

The pipeline is failing at an unacceptable rate. Common failure modes include:
- Papers classified incorrectly (the classifier uploads the full PDF and asks for one word)
- Gemini returns empty findings arrays or malformed JSON
- Findings are extracted but lack statistics, so quality checks fail
- Papers are requeued and re-extracted from scratch with no learning from the prior attempt
- The prompts don't explain our template ontology (51 templates across 10 cognitive science frameworks), so theory_links are poorly populated
- Meta-analyses return `pooled_effects` but the pipeline expects `findings`, causing silent failures
- Papers that report confidence intervals, odds ratios, or Bayesian credible intervals instead of p-values fail the statistics check

---

**PREPARATORY WORK (do this BEFORE convening the panel):**

1. Display the current `_classify_paper()` method from `pdf_extraction_module.py` (lines 654–711). Identify exactly why it fails for ambiguous papers.

2. Display the EMPIRICAL_PROMPT from `gemini_extraction_queue.py` (lines 117–173). Identify every assumption it makes about how papers report statistics.

3. Display the `_evaluate_quality()` method (lines 804–881). Calculate: if a paper has 4 findings, 3 with antecedent/consequent/direction but only 1 with p_value, what score does it get? Does it pass or fail for an empirical paper? Show your math.

4. Display the `compare_extractions()` function (lines 522–558). Explain specifically why positional zip comparison fails when two runs extract different numbers of findings.

5. Look at templates T9 and T12. Explain how the extraction prompt's `theory_links` field connects (or fails to connect) to the template's `causal_links` structure.

**Present all 5 analyses. I will review before you proceed.**

---

**PANEL COMPOSITION — 7 experts:**

1. **Dr. Mei-Ling Chen, Information Extraction Researcher**
   - Methodological commitment: Pipeline decomposition over monolithic prompts. Slot-filling with schema constraints. Cites SciREX (Jain et al., 2020) for scientific document extraction and SciIE (Luan et al., 2018) for multi-task scientific IE.
   - She believes: Classification, entity extraction, relation extraction, and slot-filling should be separate LLM calls with separate prompts, not one massive prompt.
   - She will challenge: Anyone who thinks prompt engineering alone can fix systemic architectural problems.

2. **Dr. James Okonkwo, Prompt Engineering Specialist**
   - Methodological commitment: Few-shot exemplars + chain-of-thought > architectural changes. Cites work on structured output generation, self-consistency decoding (Wang et al., 2022), and format-following instruction tuning.
   - He believes: 80% of the extraction failures are prompt failures. With proper negative examples, formatting demonstrations, and degradation instructions, a single well-crafted prompt can handle most papers.
   - He will challenge: Dr. Chen's pipeline decomposition as unnecessary complexity that introduces more failure points.

3. **Dr. Anya Krishnamurthy, Bayesian Network / Knowledge Graph Expert**
   - Methodological commitment: The extraction schema should serve the downstream knowledge structure, not the other way around. Familiar with Quinean coherentism and web-of-belief architectures.
   - She believes: The template ontology (T1–T51) should DRIVE the extraction, not be an afterthought. Extraction should ask "which templates does this paper provide evidence for?" not "extract findings and we'll link to templates later."
   - She will challenge: Both Chen and Okonkwo for treating extraction as purely a text-processing problem rather than a knowledge-construction problem.

4. **Dr. Robert Voss, Scientific Methodology Expert**
   - Methodological commitment: Different research traditions report findings in fundamentally different ways. Environmental psychology spans experimental lab studies, field quasi-experiments, post-occupancy evaluations, neuroimaging, qualitative interviews, and design case studies.
   - He believes: The current prompts assume a narrow frequentist reporting convention (p-values, effect sizes, sample sizes) that excludes half the relevant literature. Papers from HERD, Facilities, and Building and Environment often report practical significance without traditional statistics.
   - He will challenge: Quality thresholds that require statistics for empirical papers — many valid empirical studies use different reporting conventions.

5. **Dr. Priya Banerjee, ML Pipeline Engineer (SRE perspective)**
   - Methodological commitment: You can't improve what you can't measure. Wants error budgets, confusion matrices, and evaluation harnesses before any changes.
   - She believes: Before changing anything, we need a gold-standard evaluation set of 20 manually-extracted papers to measure precision/recall/F1. Then we change ONE thing at a time and measure impact.
   - She will challenge: Everyone making changes without baselines. She will also push for partial extraction repair over re-extraction.

6. **Dr. Tomás Espinoza, Document Understanding Specialist**
   - Methodological commitment: PDFs are visual documents, not just text. Tables, figures, supplementary materials, and layout carry critical information that text extraction misses.
   - He believes: Gemini's vision capabilities are being underused. The current pipeline uploads the PDF as a file, but doesn't tell Gemini to specifically examine tables and figures. A targeted prompt that says "Extract findings from Tables 2 and 3" after first identifying what tables exist would dramatically improve statistical extraction.
   - He will challenge: Text-only approaches and will push for table-specific extraction passes.

7. **Dr. Sarah Whitfield, Domain Expert in Environmental Psychology**
   - Methodological commitment: Deep knowledge of the neuroarchitecture and environmental psychology literature. Knows how findings are reported in Environment and Behavior, Journal of Environmental Psychology, HERD, Architectural Science Review, and Building and Environment.
   - She believes: The terminology matrix is essential. Environmental psychology papers say "biophilic design elements" not "antecedent: nature exposure." They say "perceived restoration" not "consequent: stress recovery." The prompts need a domain-specific translation layer.
   - She will challenge: Generic extraction approaches that don't understand the field's conventions.

---

**DELIBERATION PROTOCOL:**

**Round 1: Individual Diagnosis**
Each expert examines the preparatory analyses and the actual code. Each must:
- Identify the **specific failure modes** their expertise reveals (not generic advice)
- Reference specific line numbers or prompt text
- Propose their single highest-priority fix
- Minimum 250 words per expert

**Round 2: Cross-Examination**
Required exchanges (minimum 150 words each):
- Chen vs. Okonkwo: Is pipeline decomposition necessary, or can prompt engineering solve the problem?
- Krishnamurthy vs. Chen: Should extraction be template-driven (top-down) or finding-driven (bottom-up)?
- Voss vs. Banerjee: Can we relax quality thresholds without a gold standard, or must we measure first?
- Whitfield vs. Okonkwo: Can few-shot examples compensate for missing domain terminology, or do we need a terminology matrix?
- Espinoza vs. everyone: Does table-specific extraction justify the added API cost?
- At least 3 additional exchanges on disagreements that emerge from Round 1

**Round 3: Concrete Experiments**
The panel designs exactly 3 experiments, ordered by effort:

**Experiment 1 (1–2 hours):** Lowest effort, highest expected impact
**Experiment 2 (4–8 hours):** Medium effort, addresses the architectural issue identified as most important in Round 2
**Experiment 3 (1–2 days):** Full redesign of the component the panel agrees is most broken

Each experiment specifies:
- Hypothesis
- Exact code changes (write the actual code or pseudocode)
- Success metric and evaluation method
- Expected improvement (quantified if possible)
- What we learn if it fails

**Round 4: Synthesis**
The panel produces:
1. **Revised classification prompt** (actual text, not a description)
2. **Revised empirical extraction prompt** (actual text, with few-shot examples, negative examples, and degradation instructions)
3. **Template matching guide** (condensed version of the template ontology that can be included in prompts, organized by CNFA domain)
4. **Revised quality evaluation function** (actual code, with partial-credit scoring and repair routing)
5. **Dissent section** — any expert who disagrees with the consensus explains why

---

**CRITICAL INSTRUCTIONS:**

- Do NOT produce generic advice. Every recommendation must reference specific code, specific prompt text, or specific domain examples.
- Do NOT have experts agree politely. If they agree on a point, they must jointly challenge a third expert.
- Do NOT stop after Round 1. Run all four rounds in sequence.
- When experts cite methods or research, include real citations (author, year, brief description).
- The deliverables must be **executable or near-executable**: revised prompts should be complete text, revised code should be Python that could be dropped into the codebase, the template matching guide should be a JSON or structured text that can be prepended to extraction prompts.
- If an experiment can be run immediately (e.g., testing a revised prompt on a single paper), run it and report the result.

---

## Part 3: My Direct Recommendations (Independent of AG)

Given my reading of the code, here are the changes I would prioritize, ordered by impact-per-hour-of-effort:

### Priority 1: Fix the Prompt (2–3 hours, highest impact)

The empirical extraction prompt needs three additions:

**A. Graceful degradation instructions** — explicit rules for what to do when fields are missing. This alone will probably recover 30% of your failures.

**B. Negative examples** — what NOT to extract (hypotheses, cited findings from other papers, demographic descriptives). This will reduce false positives and improve precision.

**C. Domain terminology bridge** — a mapping table like:

```
When the paper says...          → Extract as...
"biophilic design elements"     → antecedent: specific biophilic element (specify: plants, water features, natural materials, etc.)
"perceived restoration"         → consequent: perceived restorativeness (PRS subscale if specified)
"environmental satisfaction"    → consequent: environmental satisfaction (specify measure: BUS, POE subscale, etc.)
"physiological stress markers"  → consequent: specify which marker (cortisol, heart rate variability, skin conductance, etc.)
"spatial configuration"         → antecedent: specify configuration (open plan, cellular, hybrid, specific layout metric if given)
```

### Priority 2: Implement Partial Extraction Repair (4–6 hours)

Save every extraction that scores > 0.2 to `results/partial/`. Add a `_repair_extraction()` method that:
1. Identifies which findings are missing which fields
2. For missing statistics: sends a focused prompt with only the relevant pages
3. For vague antecedents/consequents: sends a specificity prompt
4. Re-evaluates quality after repair

### Priority 3: Fix the Classification (2–3 hours)

Replace the full-PDF-one-word classifier with a two-stage approach:
1. Extract pages 1–3 and the last 2 pages using PyMuPDF (you already have fitz imported)
2. Send only those pages with a structured classification prompt that returns JSON with type, confidence, and signals
3. Save ~60% of classification API costs

### Priority 4: Unify the Two Systems (half a day)

Absorb the PROMPT_MAP into `pdf_extraction_module.py`. Add the 2-run verification as an optional mode. Remove the duplicate data structures. Fix the `pooled_effects`/`themes`/`propositions` → `findings` mapping so quality evaluation works across all article types.

### Priority 5: Fix the Image Extraction Bug (10 minutes)

Move `image_list = page.get_images(full=True)` inside the for loop. This is a one-line indentation fix that's currently causing you to miss all images except those on the last page.

---

### Priority 6: Build a 20-Paper Gold Standard (ongoing)

Manually extract findings from 20 papers (4 empirical, 2 meta-analysis, 2 systematic review, 2 narrative review, 2 theoretical, 2 qualitative, 2 methods, 4 mixed/unusual). Use these as:
- Few-shot examples in prompts (2–3 exemplars per article type)
- Evaluation harness for measuring precision/recall/F1 of the extraction
- Regression tests after any pipeline change

---

## Part 4: Decision — Run Panel Here or Send to AG?

You have two options:

**Option A: Send the improved prompt to AG.** AG (Gemini 2.5 Pro Reasoning) is capable of running the panel, especially with the much more structured prompt above. The advantage is that AG can actually test changes against the Gemini API in real time. The disadvantage is that maintaining 7 distinct expert voices across 4 rounds of dialogue is a serious coherence challenge, and AG may still compress the deliberation.

**Option B: Run the panel here with me.** I can maintain the expert voices more distinctly across longer deliberation, and I can directly write the revised prompts and code. The disadvantage is that I can't test against the Gemini API directly.

**My recommendation: A hybrid approach.** Let me write the revised prompts and the repair logic (Priorities 1–3) directly, since those are architectural and prompt-engineering tasks where I can produce near-final code. Send AG the improved prompt above for the parts that require interactive testing against Gemini — specifically Experiment 1 (testing a revised prompt on a real paper) and the table-specific extraction approach (Dr. Espinoza's contribution).

Want me to proceed with writing the revised prompts and repair code now?

---

## References

Bar, M., Kassam, K. S., Ghuman, A. S., Boshyan, J., Schmid, A. M., Dale, A. M., ... & Halgren, E. (2006). Top-down facilitation of visual recognition. *Proceedings of the National Academy of Sciences*, 103(2), 449–454. [Google Scholar: ~1,800 citations]

Evans, J. S. B., & Stanovich, K. E. (2013). Dual-process theories of higher cognition: Advancing the debate. *Perspectives on Psychological Science*, 8(3), 223–241. [~3,400 citations]

Jain, S., van Zuylen, M., Hajishirzi, H., & Beltagy, I. (2020). SciREX: A challenge dataset for document-level information extraction. *Proceedings of ACL*, 7506–7516. [~180 citations]

Luan, Y., He, L., Ostendorf, M., & Hajishirzi, H. (2018). Multi-task identification of entities, relations, and coreference for scientific knowledge graph construction. *EMNLP*, 3219–3232. [~450 citations]

Mintz, M., Bills, S., Snow, R., & Jurafsky, D. (2009). Distant supervision for relation extraction without labeled data. *Proceedings of ACL-IJCNLP*, 1003–1011. [~4,200 citations]

Ratner, A., Bach, S. H., Ehrenberg, H., Fries, J., Wu, S., & Ré, C. (2017). Snorkel: Rapid training data creation with weak supervision. *Proceedings of VLDB*, 11(3), 269–282. [~2,100 citations]

Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., ... & Zhou, D. (2022). Self-consistency improves chain of thought reasoning in language models. *ICLR 2023*. [~1,500 citations]
