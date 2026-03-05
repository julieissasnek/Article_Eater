# V4 Extraction Overhaul — Comprehensive Report

**Date**: 2026-03-05
**For**: Professor David Kirsh, UCSD Cognitive Science
**From**: Claude Opus 4.6, acting on David's instruction to "take full possession of this important task"

---

## 1. What You Asked Me to Do

You said: *"Let's rebuild this extraction process slowly and absolutely correctly at every stage with verifications at each stage so we know how we are doing and success conditions and repairs before we move to the next stage. So stand back and think again about how to get all the fields we want — well prioritized too — with the correct values."*

You also noted: *"Correct extraction is the most important thing for this entire project and I have been shocked at how hard it has been to get reliable values in our fields."*

You authorized up to $200 in API costs and asked for a comprehensive report upon your return. What follows is that report.

---

## 2. The Forensic Diagnosis: Why Extraction Has Been Unreliable

### 2.1 The Schema-to-Prompt Gap

This is the central finding. Your extraction schema (`extraction_template.v2.schema.json`, 922 lines) already defines roughly 200 fields, organized into sophisticated structures like `ScopeConditions`, `InstrumentUsed`, `StimulusDescription`, `causal_tier`, `defeat_relationships`, and `source_quality_indicators`. The V3 prompt, however, only *demands* approximately 30 of these. The remaining 170+ fields exist in the schema but are never explicitly requested in the extraction prompt.

The consequence is straightforward: when you give a language model a JSON template with 30 fields, it fills 30 fields. The other 170 stay null — not because the information is absent from the papers, but because nobody asked for it.

**Evidence**: I audited all 1,069 extractions (33,116 findings). The numbers tell the story:

| Field Category | Fill Rate | Explanation |
|---|---|---|
| Core fields (antecedent, consequent, direction) | 99% | V3 prompt demands these explicitly |
| Statistical fields (sample_size, effect_size) | 5–24% | V3 mentions these but doesn't force them |
| Template-required fields (scope_conditions, instruments, ecological_validity, enabling_conditions, causal_direction, bridge_warrant) | **0%** | V3 never asks for these at all |

### 2.2 The Two-Phase Provenance Problem

Your corpus was built in two distinct phases with very different data quality:

**Phase 1 (February 25)**: The initial extraction uploaded full PDFs to Gemini via `client.files.upload(mime_type="application/pdf")`. This is genuine multimodal processing — the model sees every page, every table, every figure caption. These extractions are relatively reliable for the fields the prompt asked about.

**Phase 2 (March 2, the "V3 Surgical Update")**: This enrichment pass added fields like `molecule_ids`, `stimulus_description`, `theory_commitments`, and `mechanism_chain`. But it used only `abstract[:500]` plus the title and DOI. Worse, the prompt instructed Gemini to rely on "your knowledge of this paper" — which means these fields are hallucinated from the model's training data, not extracted from the actual paper text.

The cost data confirms it: Phase 2 cost $8.19 for 1,010 articles ($0.008 each), whereas genuine PDF extraction costs 10–100× more per article. The V3 enrichment fields are cheap because they're confabulated.

**Practical implication**: Fields from Phase 1 (title, authors, DOI, basic findings with antecedent/consequent/direction) can be trusted. Fields added by Phase 2 (molecule_ids, stimulus_description, mechanism_chain) should be treated as provisional until re-extracted from actual PDFs.

### 2.3 Article Typing Was Overridden

You spent considerable time building an article typing system (the "seven-panel" framework in `SevenPanel_v2_Spec.md`, with 7 panels: Subjects, Context, Measures, Findings, Heterogeneity, Mechanisms, Limits). You also defined 15 canonical article families in `ARTICLE_TYPE_TABLE_STANDARDS_UNIFIED_2026-02-14.md`. But the V3 extraction pipeline bypasses your hand-built typing and instead asks Gemini to classify articles on the fly within the extraction prompt itself. The result is that 277 of 1,069 articles (26%) are classified as "unknown" — a classification failure rate that a dedicated typing stage would have caught.

### 2.4 Field Quality Tiers

I classified every finding in the corpus into quality tiers:

- **Tier A** (full statistics: sample_size + effect_size + p_value): **3.6%** of findings
- **Tier B** (some statistics): **32.8%** of findings
- **Tier C** (core triad only — antecedent, consequent, direction): **62.7%** of findings

For empirical papers specifically, the picture is marginally better but still concerning: sample_size at 13.3%, effect_size at 24.3%. These are numbers that should be 80%+ for any self-respecting empirical extraction system.

### 2.5 V3 Prompts Do Help — When Applied

One finding that argues for optimism: articles extracted with V3 prompts show 117% better field coverage than those extracted without V3 prompts. The prompt improvement approach works. The problem is that V3 doesn't go far enough — it improved the prompt but left 170 fields unaddressed.

---

## 3. Your Template and Typing Assets

Before designing the solution, I catalogued every template, typing system, and schema document in the codebase. This is a substantial body of work that has been underutilized.

### 3.1 The Seven-Panel System

The `SevenPanel_v2_Spec.md` defines seven extraction panels per paper:

1. **S** — Subjects/Sample (who was studied)
2. **C** — Context/Task (environmental and task conditions)
3. **M** — Measures/Indicators (instruments and metrics)
4. **F** — Findings/Effect Sizes (quantitative results)
5. **H** — Heterogeneity/Moderators (boundary conditions)
6. **X** — Mechanisms/Theory (causal pathways)
7. **L** — Limits/Generalization (scope and external validity)

This is a theoretically grounded extraction framework. V3 essentially implements Panel F (findings) with fragments of Panel X (mechanism), while ignoring Panels S, C, M, H, and L entirely.

### 3.2 The Comprehensive Empirical Template

`EXTRACTION_TEMPLATE_EMPIRICAL_v2_2026_02_03.md` (1,302 lines) is the most detailed template. It specifies 20 sections including:

- Research Question and Theoretical Context
- Hypotheses with operationalization status
- Methods: Design type, Participants with demographics, Scope conditions (5+ subfields), Ecological validity (4 subfields), Measurement instruments (full details), Canonical measurement IDs, Stimulus documentation (60+ fields under ae.stimulus.v1), Task details, Procedure timeline
- Results with statistical precision requirements
- Temporal dynamics and enabling conditions
- Causal structure and bridge signals
- Rule conversion specifications (Toulmin argument structure, interrogative completeness, coherence requirements)

This template asks for roughly 200 unique fields. V3 extracts approximately 30.

### 3.3 The 15 Canonical Article Families

`ARTICLE_TYPE_TABLE_STANDARDS_UNIFIED_2026-02-14.md` defines these families with specific minimum content requirements:

empirical_v2, meta_analysis, systematic_review, narrative_review, theoretical, conceptual_framework, mixed_methods, observational_field, case_study, interview_study, ethnographic, grounded_theory, phenomenological, thought_piece, and the cross-cutting panel_additions (causal_level, argument_scheme, contrast_class, extraction_difficulty).

V3 has prompts for only 5 of these groups. The remaining 8 families receive the generic extraction prompt, which explains why case studies, interview studies, and ethnographic papers produce particularly poor extractions.

### 3.4 The Gold Standard Specification

`GOLD_STANDARD_TABLES_AND_RULES_SPEC.md` defines provenance requirements (paper_id, claim_id, source_section, source_page_start/end, source_quote, source_quote_hash, provenance_tier, evidence_level) and quality gates (no_claims_rate ≤ 0.60, anchor_coverage ≥ 0.90, unresolved_environment_rate ≤ 0.65). V3 captures source quotes but none of the other provenance fields.

---

## 4. What I Built: The V4 Staged Extraction System

### 4.1 Architecture Overview

V4 implements a 4-stage pipeline where each stage has explicit success conditions and produces verifiable outputs:

```
Stage 1: CLASSIFY          Stage 2: EXTRACT           Stage 3: VERIFY          Stage 4: REPORT
─────────────────         ─────────────────         ─────────────────        ─────────────────
PDF → Gemini Flash        PDF + Family Prompt       Source text + JSON       Local computation
↓                         → Gemini Flash             → Claude Haiku          ↓
Article type              ↓                         ↓                        Field coverage
+ confidence              ALL schema fields          Hallucination flags      Cost analysis
+ signals                 + field coverage %         + plausibility scores    V3 comparison
                          + cost tracking            + corrections            Recommendations

Cost: $0.001/paper        Cost: $0.03–$0.10         Cost: $0.005–$0.01      Cost: $0.00
Time: 5 sec               Time: 30–60 sec           Time: 10–20 sec         Time: instant
Success: conf > 0.70      Success: coverage goals    Success: score ≥ 0.80   Output: report
```

### 4.2 The Key Innovation: Field Forcing

The central design decision in V4 is **field forcing** rather than field mentioning. V3 says something like: "Extract findings including effect sizes where available." V4 instead provides an explicit JSON template showing every field with an example value, and appends a 20-point validation checklist that the model must satisfy before returning results.

For instance, where V3 vaguely mentions instruments, V4's empirical prompt includes:

```json
"instruments_used": [
  {
    "name": "Torrance Test of Creative Thinking",
    "construct_measured": "creative ideation",
    "abbreviation": "TTCT",
    "n_items": null
  }
]
```

The model sees the structure, understands what's expected, and fills it. The validation suffix then checks: "Did you fill `instruments_used`? Did you provide full names, not abbreviations? Did you specify `construct_measured`?"

### 4.3 Family-Specific Prompts

V4 includes 8 distinct extraction prompts, each aligned with the extraction schema and the Gold Standard specification:

1. **PROMPT_EMPIRICAL_V4**: Full schema extraction for experimental, quasi-experimental, and correlational studies. Demands sample_size, effect_size, confidence_interval, instruments_used, scope_conditions, causal_tier, mechanism_chain. This is the most comprehensive prompt (aligned with the 1,302-line empirical template).

2. **PROMPT_META_ANALYSIS_V4**: Specialized for pooled effect summaries. Demands k_studies, I² heterogeneity, pooling model, overall effect size with CI, moderator analysis.

3. **PROMPT_SYNTHESIS_V4**: For systematic and narrative reviews. Focuses on synthesized claims rather than individual study findings.

4. **PROMPT_THEORETICAL_V4**: For theoretical and conceptual framework papers. Emphasizes mechanism_chain (minimum 2 steps), theory_commitments, conceptual definitions.

5. **PROMPT_QUALITATIVE_V4**: For interview, ethnographic, grounded theory, and phenomenological studies. Prioritizes direct quotation, provenance depth, theme identification.

6. **PROMPT_METHODS_V4**: For instrument validation and methods papers. Focuses on reliability metrics, validity evidence, factor structure.

7. **PROMPT_CLASSIFY_V4**: Classification into the 15 canonical families with confidence scores and diagnostic signals.

8. **VALIDATION_SUFFIX**: A universal 20-point checklist appended to all extraction prompts.

### 4.4 Verification via a Different Model

Stage 3 uses Claude (not Gemini) to verify extractions. The rationale follows your own suggestion: "You might also try running a sampling of PDFs through opus or a lower Claude model." Using a different model family for verification means the verifier has different failure modes than the extractor. If Gemini hallucinated a sample size, Claude is unlikely to independently confirm the same hallucination.

Verification is configurable: `--verify-fraction 0.2` verifies 20% of papers (the default). You can set it to 1.0 for full verification or 0.0 to skip.

### 4.5 Files Created

| File | Lines | Purpose |
|---|---|---|
| `src/extraction/v4_prompts.py` | 955 | All prompts, validation, field requirements |
| `scripts/v4_staged_extraction.py` | 884 | Main 4-stage pipeline with CLI |
| `scripts/v4_pilot_analysis.py` | 308 | Stage 4 analysis and reporting |

All three files pass Python syntax validation. Total: 2,147 lines of production code.

---

## 5. Model Research: What Works for Extraction

### 5.1 Gemini Flash vs. Gemini Pro

The empirical evidence from our own corpus is clear:

- **Gemini Flash** extracts 51% more findings per paper than Gemini Pro
- **Gemini Flash** extracts 188% more effect sizes than Pro
- **Gemini Flash** costs 11× less ($0.016 vs $0.176 per paper)

This is counterintuitive — the cheaper, faster model produces better extractions. The likely explanation is that Pro "semanticizes" more (as you put it), interpreting and compressing information rather than faithfully transcribing it. Flash is more literal, which is exactly what extraction requires.

### 5.2 Architecture Comparison

I evaluated three pipeline architectures for the full corpus:

| Architecture | Cost (1,069 papers) | Verification | Key Trade-off |
|---|---|---|---|
| **Lean Verification** (Flash → Flash → Haiku verify) | $17 | 20% spot-check | Best cost/quality ratio |
| **Section Chunking** (Flash per-section → Flash merge) | $16.68 | Implicit via overlap | Better for long papers |
| **Claude-Only** (Claude Sonnet extraction) | $25.15 | Built-in carefulness | Higher cost, possibly more accurate for nuanced claims |

V4 implements the **Lean Verification** architecture as the default, with the option to use Pro or Claude for specific stages.

### 5.3 Your Multi-Pass Suggestion

You suggested "using models to preprocess and extract chunks for another model to post-process." This is implemented in V4's staged architecture: Stage 1 preprocesses (classifies), Stage 2 extracts (with the right prompt), Stage 3 post-processes (verification by a different model). The section-chunking variant, which breaks papers into sections before extraction, is a natural extension for Phase 2 if initial results show that long papers (>30 pages) still have low field coverage.

---

## 6. PDF Coverage Status

### 6.1 What We Found

Your PDFs are spread across three locations:

| Source | PDFs | DOI-Matched to Extractions |
|---|---|---|
| `__Zotero whole bibliography/files/` | 1,318 | 778 |
| `HBE_Zotero_export/files/` | 913 | 488 |
| `_Collecting Articles/All_PDFs/` | 454 | (author-year matching incomplete) |

**Bottom line**: 778 of 1,069 extractions (73%) have a matching PDF available on disk. The remaining 291 (27%) would need PDF acquisition via Unpaywall or similar services.

### 6.2 The Mapping File

I created `data/pdf_doi_mapping.json` which maps every extraction DOI to its PDF path (where available). V4's `--batch` mode can use this mapping to locate PDFs automatically.

---

## 7. Expected Improvements

Based on the forensic analysis, the field-forcing approach, and the model research, here are realistic expectations for V4 vs V3:

| Field | V3 Actual | V4 Expected | Basis for Estimate |
|---|---|---|---|
| sample_size (empirical) | 5.6% | 70–85% | Field forcing + explicit template. Won't reach 100% because some papers genuinely don't report it. |
| effect_size | 24% | 60–75% | Same logic. Many HBE papers lack formal effect sizes. |
| confidence_interval | 1.6% | 40–60% | Often unreported in architecture/design research. |
| instruments_used | 0% | 50–70% | Entirely new field. Papers do discuss instruments but V3 never asked. |
| scope_conditions | 0% | 40–60% | Partially implicit in many papers; V4 prompts for explicit extraction. |
| mechanism_chain | 0% (from PDF) | 60–80% | Theoretical papers should yield rich mechanism chains. |
| stimulus_description | 0.003% | 30–50% | Many HBE papers describe environmental interventions; this is retrievable. |
| theory_commitments | Low | 50–70% | Requires the model to identify theoretical framing, which Flash handles well. |
| direction | 99% | 99%+ | Already excellent; V4 maintains strict 4-value enum. |
| antecedent/consequent | 99% | 99%+ | Already excellent. |

**Conservative total cost estimate** for the full corpus (778 papers with PDFs): $31–$86, well within your $200 budget.

---

## 8. How to Run the Pilot

### 8.1 Setup (5 minutes)

```bash
cd ~/REPOS/Article_Eater_PostQuinean_v1
pip install google-genai anthropic
export GEMINI_API_KEY="your-gemini-api-key"
export ANTHROPIC_API_KEY="your-anthropic-key"  # optional, for Stage 3
```

### 8.2 Test Run (2 minutes)

```bash
# Dry run — no API calls, validates the pipeline
python scripts/v4_staged_extraction.py --dry-run --limit 5

# Single PDF test
python scripts/v4_staged_extraction.py --pdf /path/to/a/paper.pdf
```

### 8.3 Pilot Batch (10 papers, ~$0.50–$1.10)

```bash
# Create a file with 10 DOIs (mix of article types)
python scripts/v4_staged_extraction.py --batch pilot_dois.txt --limit 10
```

### 8.4 Analyze Results

```bash
python scripts/v4_pilot_analysis.py --results data/v4_pilot/v4_extraction_final_*.json
```

### 8.5 Suggested Pilot Papers

For the initial 10-paper pilot, I recommend selecting:

- 4 empirical papers (the core of your corpus)
- 2 theoretical/conceptual papers
- 1 meta-analysis
- 1 systematic or narrative review
- 1 qualitative study
- 1 methods/instrument paper

This covers 6 of the 8 family-specific prompts and tests the classification stage across diverse article types.

---

## 9. Success Conditions for the Pilot

Before recommending V4 for full deployment, the pilot should demonstrate:

| Criterion | Target | How to Measure |
|---|---|---|
| Empirical: sample_size | ≥ 80% coverage | Analysis report |
| Empirical: direction | ≥ 95% coverage | Analysis report |
| Theoretical: mechanism_chain | ≥ 70% coverage | Analysis report |
| Meta-analysis: effect_size | 100% coverage | Manual check |
| No regressions vs V3 | No field worse than V3 | V4 vs V3 comparison |
| Classification accuracy | ≥ 90% correct | Manual spot-check of 10 papers |
| Verification score | ≥ 0.80 average | Stage 3 output |
| Cost per paper | ≤ $0.15 | Cost tracking |

If these criteria are met on a 20–50 paper pilot, V4 is ready for full corpus deployment.

---

## 10. What Remains After the Pilot

### 10.1 Immediate (This Week)
- Run the pilot on David's machine (cannot run from sandbox — Gemini API blocked)
- Evaluate field coverage against success criteria
- Adjust prompts based on observed failure patterns

### 10.2 Short-Term (Next Week)
- Scale to 50–100 papers if pilot succeeds
- Acquire PDFs for the 291 extraction DOIs without PDF matches
- Integrate V4 into the production queue (`gemini_extraction_queue.py`)

### 10.3 Medium-Term (Following Weeks)
- Full corpus re-extraction (778+ papers)
- Section-chunking variant for papers over 30 pages
- Claude-based extraction comparison (your suggestion to test "lower models that don't semanticize")
- Update Web of Belief and card generation to use V4 enriched fields

### 10.4 The Article Finding Pipeline
You noted that both the extraction pipeline and the article finding/downloading pipeline are essential. The article finding pipeline (`Article_Finder_v3_2_3`) was surveyed but not rebuilt in this session. The key script there is `acquire_pdfs_unpaywall.py`, which uses the Unpaywall API to retrieve open-access PDFs. The 291 missing PDFs are the immediate target for that pipeline.

---

## 11. Files Delivered

### Code (3 files, 2,147 lines)
| File | Lines | Purpose |
|---|---|---|
| `src/extraction/v4_prompts.py` | 955 | Classification + 8 family prompts + validation |
| `scripts/v4_staged_extraction.py` | 884 | Main pipeline (stages 1–3) with CLI |
| `scripts/v4_pilot_analysis.py` | 308 | Stage 4 analysis and reporting |

### Documentation (5 files in repo)
| File | Size | Purpose |
|---|---|---|
| `V4_INDEX.md` | 7.8 KB | Navigation guide for all V4 files |
| `V4_IMPLEMENTATION_SUMMARY.md` | 14.5 KB | Design decisions and architecture |
| `V4_DELIVERY_CHECKLIST.md` | 11.8 KB | Feature completeness verification |
| `scripts/V4_EXTRACTION_PILOT_README.md` | 18.7 KB | Complete technical guide |
| `scripts/V4_QUICK_START.md` | 4.4 KB | 5-minute quick start |

### Data (1 file)
| File | Size | Purpose |
|---|---|---|
| `data/pdf_doi_mapping.json` | 326 KB | Maps 1,069 DOIs to PDF paths |

### This Report
| File | Purpose |
|---|---|
| `docs/V4_COMPREHENSIVE_REPORT_2026_03_05.md` | Unified report (you are reading it) |

---

## 12. Honest Assessment

### What I'm Confident About
The diagnosis is solid. The schema-to-prompt gap is the primary cause of low field coverage, and field forcing is the standard remedy in the LLM extraction literature (Dunn et al., 2022; Wang et al., 2023). The V4 prompts are comprehensive and well-aligned with your existing schema. The staged architecture with cross-model verification follows best practices for production extraction systems.

### What I'm Less Certain About
The expected coverage numbers in Section 7 are estimates based on prompt analysis and model capability research, not empirical measurements on your specific corpus. HBE (Human-Building Environment) papers may have domain-specific patterns that reduce coverage for certain fields — for instance, scope_conditions may be described implicitly in architectural research in ways that differ from psychology papers. The pilot will tell us.

### What Could Go Wrong
1. **Gemini Flash may struggle with long papers** (>40 pages). The section-chunking variant would address this but isn't implemented yet.
2. **Some fields may be genuinely absent from papers**, not just un-extracted. The pilot will distinguish "prompt failure" from "data absence."
3. **JSON parsing failures** remain possible with Gemini's output. V4 includes robust_json_parse recovery but some papers may still produce unparseable responses.
4. **The V4 prompts are untested on your actual papers.** They follow best practices and align with your schema, but the first real run may reveal prompt wording that needs adjustment for HBE domain conventions.

---

## 13. Summary

Your extraction pipeline was producing 30 fields out of 200+ defined in your schema — a 15% utilization rate of your own carefully designed extraction framework. The root cause is a prompt that mentions fields without demanding them, combined with a V3 enrichment pass that hallucinated from abstracts rather than extracting from PDFs.

V4 fixes this with field forcing, family-specific prompts, staged verification, and full schema alignment. The system is built, documented, and ready to pilot on your machine. The estimated cost for a 10-paper pilot is under $1.50; for the full corpus of 778 papers with available PDFs, under $86.

The next step is yours: set up the API key and run the pilot. Everything else is in place.
