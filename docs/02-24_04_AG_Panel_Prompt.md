# AG Expert Panel Prompt — Extraction Pipeline Redesign

**Paste this entire prompt into Antigravity (Gemini 2.5 Pro).**

---

## Context

You are Antigravity, running Gemini 2.5 Pro. You are convening a 7-expert panel to redesign a PDF extraction pipeline that extracts structured findings from environmental psychology / neuroarchitecture papers.

Opus (Claude) has already completed a code audit and produced two deliverables:
1. **`revised_prompts_v2.py`** — Complete rewrite of all extraction prompts with 166-template matching guide, 15 article sub-types in 5 families, graceful degradation rules, negative examples, domain terminology bridge, and provenance depth tagging.
2. **`pipeline_repairs.py`** — Revised classification (intro+conclusion pages only), 4-tier quality routing (accept/repair/requeue/fail), partial extraction repair, findings normalization, image extraction bug fix.

Your job is to **test these revised prompts against the Gemini API** and **run the expert panel to identify anything Opus missed or got wrong**. You have access to the codebase and can run actual extractions.

---

## Pre-Work (BEFORE convening the panel)

Do these four things first and show the results:

### Pre-Work 1: Dump Code Sections
Show the current PROMPT_MAP from `scripts/gemini_extraction_queue.py` (lines 80–395) and the `_classify_paper()` method from `src/extraction/pdf_extraction_module.py` (lines 654–711). These are what we're replacing.

### Pre-Work 2: Run a Failing Paper
Pick one paper from the queue that has previously failed or been requeued. Run it through the CURRENT pipeline. Show the raw Gemini API response. Identify exactly where the extraction breaks (missing findings? wrong article type? vague antecedents? missing statistics?).

### Pre-Work 3: Run the Same Paper with the Revised Prompt
Take the same failing paper. Use the appropriate prompt from `revised_prompts_v2.py` (based on the paper's article family). Run it through Gemini. Show the raw API response. Compare side by side.

### Pre-Work 4: Classification Test
Take 5 papers of different types (1 empirical, 1 meta-analysis, 1 theoretical, 1 qualitative, 1 review). For each, extract only pages 1–3 + last 2 pages using PyMuPDF. Send to Gemini with the CLASSIFICATION_PROMPT from `revised_prompts_v2.py`. Report: did it classify correctly? What confidence? What signals?

---

## Expert Panel

After completing pre-work, convene these 7 experts. Each has a distinct methodological commitment that will generate genuine disagreement.

### Panel Members

**Dr. Chen** — Information Extraction Researcher (NLP)
*Commitment:* Pipeline decomposition matters more than prompt engineering. The extraction should be broken into sub-tasks (entity recognition → relation extraction → schema filling) rather than asking one prompt to do everything.
*Will cite:* SciREX (Jain et al., 2020), SciIE (Luan et al., 2018), distant supervision methods (Mintz et al., 2009).
*Will challenge:* Dr. Okonkwo's one-prompt approach and Opus's monolithic prompt design.

**Dr. Okonkwo** — Prompt Engineer
*Commitment:* Few-shot examples + chain-of-thought reasoning beats architectural complexity. The right examples in the prompt will outperform pipeline restructuring.
*Will cite:* Self-consistency (Wang et al., 2022), chain-of-thought prompting (Wei et al., 2022).
*Will challenge:* Dr. Chen's sub-task decomposition as over-engineering, and Opus's template matching guide as too large for the context window.

**Dr. Krishnamurthy** — Bayesian Network / Knowledge Graph Specialist
*Commitment:* Template-driven extraction is the right idea but Opus's matching guide is still too passive. The templates should constrain extraction, not just label it after the fact.
*Will challenge:* Both Chen and Okonkwo — the templates ARE the schema, and extraction should be template-first.

**Dr. Voss** — Methodologist (Research Synthesis)
*Commitment:* Different research traditions report findings differently. A meta-analysis, a qualitative study, and an empirical experiment should NOT be forced through the same finding schema.
*Will challenge:* Opus's decision to normalize everything to `findings` — is this losing important information?
*Will evaluate:* Whether the 5-family field contracts (from `article_type_contract.py`) are actually respected by the revised prompts.

**Dr. Banerjee** — Site Reliability Engineer
*Commitment:* You need baselines before you change anything. Measure current extraction precision/recall, then measure after changes.
*Will push for:* Gold standard papers, A/B testing framework, cost tracking per paper, the partial extraction repair system.
*Will challenge:* Anyone who wants to ship changes without measurement.

**Dr. Espinoza** — Document AI Specialist
*Commitment:* You're underusing Gemini's vision capabilities. Tables should be extracted separately with table-specific prompts. Figures should be analyzed for data.
*Will push for:* Table detection → table-specific extraction, figure analysis, page-level processing.
*Will challenge:* Opus's text-heavy approach that treats PDF as a single blob.

**Dr. Whitfield** — Domain Expert (Environmental Psychology / Neuroarchitecture)
*Commitment:* The terminology bridge is essential but incomplete. The field has specific conventions for reporting that the prompts need to understand.
*Will push for:* Expanded terminology mapping, domain-specific extraction rules (e.g., POE studies report differently than lab experiments), and validation that the 166 templates actually cover the field.
*Will challenge:* Anyone who proposes solutions without domain knowledge.

---

## Panel Protocol — Four Rounds

### Round 1: Individual Diagnosis (250 words minimum per expert)
Each expert examines the pre-work results (original vs. revised extraction) and diagnoses what Opus got right, what Opus missed, and what they would do differently. Each must reference specific lines from the pre-work results.

### Round 2: Cross-Examination (minimum 10 exchanges, 150 words each)
Experts challenge each other. Required conflicts:
- Chen vs. Okonkwo: Is one monolithic prompt the right approach, or should extraction be decomposed?
- Krishnamurthy vs. Opus's design: Should templates constrain extraction (template-first) or label it (extraction-first)?
- Voss vs. the `findings` normalization: Is forcing everything into antecedent→consequent losing information for theoretical and qualitative papers?
- Banerjee vs. everyone: Where are the baselines? How do we know the revised prompts are better?
- Espinoza challenges the pre-work results: What did table-specific extraction miss?
- Whitfield challenges terminology coverage: What domain terms are still missing from the bridge?

### Round 3: Three Concrete Experiments
The panel designs and (where possible) RUNS three experiments:

**Experiment 1: Prompt A/B Test**
Run 5 papers through both the original and revised prompts. Compare: (a) number of findings extracted, (b) template_ids assigned, (c) provenance_depth coverage, (d) specificity of antecedent/consequent. Show results in a table.

**Experiment 2: Table-Specific Extraction**
Take a paper with statistical tables. Run (a) the standard full-PDF prompt and (b) a two-pass approach: first extract tables as images, then send table images with a table-specific prompt. Compare statistics extraction rate.

**Experiment 3: Classification Accuracy**
Run the lightweight classification prompt (intro+conclusion pages only) on 10 papers where the true type is known. Report accuracy, confidence calibration, and failure modes.

### Round 4: Synthesis
Produce these deliverables:

1. **Verdict on Opus's revised prompts:** What to keep as-is, what to modify, what to add. Be specific — quote prompt sections.

2. **Revised prompts** (if modifications needed): Provide the complete revised prompt text. Do not say "add X here" — write the actual text.

3. **Template matching guide assessment:** Is the 166-template guide too large? Should it be dynamically selected based on paper domain? Propose a specific solution.

4. **Gold standard paper list:** Nominate 20 specific papers (with DOIs if possible) to serve as the extraction benchmark — 4 empirical, 2 meta-analysis, 2 systematic review, 2 narrative review, 2 theoretical, 2 qualitative, 2 methods, 2 mixed/unusual.

5. **Dissent section:** Any expert who disagrees with the consensus explains why.

---

## Critical Instructions

- **DO the pre-work first.** Run actual extractions. Show actual API responses. The panel needs real data.
- **DO NOT produce generic advice.** Every recommendation must reference specific code, specific prompt text, or specific domain examples from the pre-work.
- **DO NOT have experts agree politely.** If they agree on a point, they must jointly challenge a third expert.
- **DO NOT stop after Round 1.** Run all four rounds in full.
- **DO NOT compress the cross-examination.** Round 2 must have at minimum 10 substantive exchanges (150+ words each). This is where the real insights emerge.
- **When experts cite methods or research, include real citations** (author, year, brief description).
- **Deliverables must be executable:** revised prompts should be complete text, code should be Python, the template guide assessment should include a concrete proposal (not just "consider dynamic selection").
- **If an experiment can be run immediately** (testing a revised prompt on a paper), RUN IT and report the result. Do not just describe what you would do.

---

## Files You Need

These files should already be in your working directory:
- `src/extraction/revised_prompts_v2.py` — the revised prompts to test
- `src/extraction/pipeline_repairs.py` — the pipeline repair code
- `src/extraction/article_type_contract.py` — the field contracts per article family
- `scripts/gemini_extraction_queue.py` — the current pipeline (what we're replacing)
- `docs/template_id_aliases.json` — the template registry
- `data/templates/*.json` — all 208 template files (166 unique)

If any file is missing, say so before proceeding.
